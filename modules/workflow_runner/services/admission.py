"""Generic full-lifecycle admission for Workflow Runner submissions.

The acquired lease owns the queue boundary.  LF's default provider delegates
its single submission to the normal HTTP transport; an installed provider may
instead submit through a cooperative transport of its own.  The same lease is
held until the exact prompt has terminal history and is absent from ComfyUI's
running and pending queues.
"""

from __future__ import annotations

import asyncio
import importlib.metadata
import json
import os
import re
import threading
import time

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Awaitable, Callable, Mapping, Protocol, runtime_checkable


_PROVIDER_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_PROVIDER_ENVIRONMENT_VARIABLE = "WORKFLOW_RUNNER_SUBMISSION_PROVIDER"
_PROVIDER_ENTRY_POINT_GROUP = "lf_nodes.workflow_admission_providers"


def _freeze(value: Any) -> Any:
    """Recursively freeze request data without changing scalar values."""

    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze(item) for item in value)
    return value


def _canonical_json_object(value: Mapping[str, Any]) -> tuple[Mapping[str, Any], str]:
    """Return one JSON-normalized immutable object and its canonical bytes."""

    # The round trip both rejects non-JSON queue data and normalizes tuples and
    # mapping keys exactly as the HTTP JSON decoder would see them.
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    normalized = json.loads(encoded)
    if not isinstance(normalized, dict):
        raise TypeError("workflow queue body must be a JSON object")
    return _freeze(normalized), encoded


class WorkflowSubmissionRejectedBeforeQueue(Exception):
    """Explicit proof that no prompt was accepted by the queue transport.

    A provider may raise this only before starting its own queue transport or
    invoking LF's delegate.  Only this marker makes it safe for orchestration
    to release a guarded lease after ``submit`` raises.  Every unmarked failure
    is ambiguous and retains the handle for provider-side reconciliation.
    """


class WorkflowSubmissionOutcomeUnknown(RuntimeError):
    """Submission crossed a queue boundary but did not yield trusted context."""


@dataclass(frozen=True, slots=True)
class WorkflowSubmissionRequest:
    """Exact, immutable ComfyUI queue envelope presented for admission."""

    workflow_id: str | None
    owner_id: str | None
    client_id: str
    comfy_url: str
    prompt: Mapping[str, Any]
    validation: tuple[Any, ...]
    queue_body: Mapping[str, Any]
    queue_body_json: str
    required_provider_id: str | None = None
    admission_metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        body, body_json = _canonical_json_object(self.queue_body)
        prompt = body.get("prompt")
        if not isinstance(prompt, Mapping):
            raise TypeError("workflow queue body must contain an object prompt")
        if body.get("client_id") != self.client_id:
            raise ValueError("workflow queue body client_id does not match request")
        if not isinstance(self.client_id, str) or not self.client_id:
            raise ValueError("workflow submission client_id must be non-empty")
        if not isinstance(self.comfy_url, str) or not self.comfy_url:
            raise ValueError("workflow submission comfy_url must be non-empty")
        if self.required_provider_id is not None:
            _validate_provider_id(self.required_provider_id)

        object.__setattr__(self, "queue_body", body)
        object.__setattr__(self, "queue_body_json", body_json)
        # Prompt identity is deliberately anchored to the exact admitted body.
        object.__setattr__(self, "prompt", prompt)
        object.__setattr__(self, "validation", _freeze(tuple(self.validation)))
        object.__setattr__(self, "admission_metadata", _freeze(self.admission_metadata))


@dataclass(frozen=True, slots=True)
class WorkflowPromptContext:
    """Canonical context returned by the lease that submitted the prompt.

    Providers must anchor ``prompt`` to the exact admitted ``request.prompt``
    object.  They must not clone or mutate it: this context proves which frozen
    queue envelope crossed the submission boundary.
    """

    prompt_id: str
    client_id: str
    comfy_url: str
    prompt: Mapping[str, Any]
    validation: tuple[Any, ...]
    workflow_id: str | None

    def as_legacy_tuple(
        self,
    ) -> tuple[str, str, str, Mapping[str, Any], tuple[Any, ...], str | None]:
        return (
            self.prompt_id,
            self.client_id,
            self.comfy_url,
            self.prompt,
            self.validation,
            self.workflow_id,
        )


@dataclass(frozen=True, slots=True)
class WorkflowAdmissionOutcome:
    """Terminal information supplied when an acquired lease is released."""

    prompt_id: str | None
    status: str
    error: str | None = None


WorkflowSubmissionDelegate = Callable[
    [WorkflowSubmissionRequest],
    Awaitable[WorkflowPromptContext],
]


@runtime_checkable
class WorkflowAdmissionLease(Protocol):
    """Authority held from pre-queue admission through terminal completion."""

    async def submit(
        self,
        request: WorkflowSubmissionRequest,
        default_submit: WorkflowSubmissionDelegate,
    ) -> WorkflowPromptContext:
        """Own or explicitly delegate the single exact queue submission."""

    async def release(self, outcome: WorkflowAdmissionOutcome) -> None:
        """Release authority after exact terminal proof."""


@runtime_checkable
class WorkflowAdmissionProvider(Protocol):
    """Provider installed by an optional scheduler/resource integration."""

    provider_id: str

    async def acquire(
        self,
        request: WorkflowSubmissionRequest,
    ) -> WorkflowAdmissionLease:
        """Acquire authority for one exact queue envelope before submission."""


class _DefaultAdmissionLease:
    async def submit(
        self,
        request: WorkflowSubmissionRequest,
        default_submit: WorkflowSubmissionDelegate,
    ) -> WorkflowPromptContext:
        return await default_submit(request)

    async def release(self, outcome: WorkflowAdmissionOutcome) -> None:
        return None


class _DefaultAdmissionProvider:
    provider_id = "lf-default"

    async def acquire(self, request: WorkflowSubmissionRequest) -> WorkflowAdmissionLease:
        return _DefaultAdmissionLease()


class AcquiredWorkflowAdmission:
    """One-shot submission and retryable release around a provider lease."""

    __slots__ = (
        "_lease",
        "_request",
        "_state_lock",
        "_submitted",
        "_released",
    )

    def __init__(
        self,
        lease: WorkflowAdmissionLease,
        request: WorkflowSubmissionRequest,
    ) -> None:
        self._lease = lease
        self._request = request
        self._state_lock = asyncio.Lock()
        self._submitted = False
        self._released = False

    @property
    def request(self) -> WorkflowSubmissionRequest:
        return self._request

    @property
    def released(self) -> bool:
        return self._released

    async def submit(
        self,
        default_submit: WorkflowSubmissionDelegate,
    ) -> WorkflowPromptContext:
        async with self._state_lock:
            if self._released:
                raise RuntimeError("workflow admission was released before submission")
            if self._submitted:
                raise RuntimeError("workflow admission permits exactly one submission")
            self._submitted = True

        delegated = False
        delegate_open = True
        delegated_result: WorkflowPromptContext | None = None

        async def one_shot_default(
            request: WorkflowSubmissionRequest,
        ) -> WorkflowPromptContext:
            nonlocal delegated, delegated_result
            if not delegate_open:
                raise RuntimeError("default workflow submission delegate has expired")
            if request is not self._request:
                raise PermissionError("default submission must use the admitted exact request")
            if delegated:
                raise RuntimeError("default workflow submission delegate is single-use")
            delegated = True
            delegated_result = await default_submit(request)
            return delegated_result

        try:
            result = await self._lease.submit(self._request, one_shot_default)
        except WorkflowSubmissionRejectedBeforeQueue as exc:
            if delegated:
                raise WorkflowSubmissionOutcomeUnknown(
                    "provider claimed pre-queue rejection after delegating submission"
                ) from exc
            raise
        finally:
            delegate_open = False

        if type(result) is not WorkflowPromptContext:
            raise TypeError("workflow admission lease returned an invalid prompt context")
        if delegated and result is not delegated_result:
            raise PermissionError(
                "workflow admission lease replaced the delegated prompt context"
            )
        if not result.prompt_id:
            raise ValueError("workflow admission lease returned an empty prompt id")
        if (
            result.client_id != self._request.client_id
            or result.comfy_url != self._request.comfy_url
            or result.prompt is not self._request.prompt
            or result.validation != self._request.validation
            or result.workflow_id != self._request.workflow_id
        ):
            raise PermissionError(
                "workflow admission lease returned context for a different submission"
            )
        return result

    async def release(self, outcome: WorkflowAdmissionOutcome) -> None:
        # Keep the lock across release so concurrent callers cannot double-free.
        # State changes only after the provider confirms success, allowing retry
        # and preserving the authority if provider release itself fails.
        async with self._state_lock:
            if self._released:
                return
            try:
                await self._lease.release(outcome)
            except BaseException as exc:
                retain_workflow_admission(self, exc)
                raise
            self._released = True
            _RETAINED_ADMISSIONS.pop(self._request.client_id, None)


@dataclass(frozen=True, slots=True)
class RetainedWorkflowAdmission:
    """Strong reference to authority whose queue outcome needs reconciliation."""

    admission: AcquiredWorkflowAdmission
    error: str
    retained_at: float


_DEFAULT_PROVIDER: WorkflowAdmissionProvider = _DefaultAdmissionProvider()
_provider: WorkflowAdmissionProvider = _DEFAULT_PROVIDER
_RETAINED_ADMISSIONS: dict[str, RetainedWorkflowAdmission] = {}
_environment_provider_initialized = False
_environment_provider_lock = threading.Lock()


def _validate_provider_id(provider_id: Any) -> str:
    if not isinstance(provider_id, str) or not _PROVIDER_ID_PATTERN.fullmatch(provider_id):
        raise ValueError(
            "workflow admission provider_id must be a non-empty identifier of at "
            "most 128 ASCII letters, digits, dots, underscores, or hyphens"
        )
    return provider_id


def retain_workflow_admission(
    admission: AcquiredWorkflowAdmission,
    error: BaseException | str,
) -> RetainedWorkflowAdmission:
    """Retain ambiguous authority until its provider explicitly reconciles it."""

    record = RetainedWorkflowAdmission(
        admission=admission,
        error=str(error) or type(error).__name__,
        retained_at=time.time(),
    )
    _RETAINED_ADMISSIONS[admission.request.client_id] = record
    return record


def get_retained_workflow_admission(
    client_id: str,
) -> RetainedWorkflowAdmission | None:
    return _RETAINED_ADMISSIONS.get(client_id)


def list_retained_workflow_admissions() -> tuple[RetainedWorkflowAdmission, ...]:
    return tuple(_RETAINED_ADMISSIONS.values())


async def reconcile_retained_workflow_admission(
    client_id: str,
    outcome: WorkflowAdmissionOutcome,
) -> bool:
    """Retry release of one process-local admission retained after ambiguity."""

    retained = _RETAINED_ADMISSIONS.get(client_id)
    if retained is None:
        return False
    await retained.admission.release(outcome)
    return True


def set_workflow_admission_provider(
    provider: WorkflowAdmissionProvider | None,
) -> WorkflowAdmissionProvider:
    """Install a process-wide provider and return the previous provider.

    An explicit programmatic installation is authoritative for this process;
    the lazy environment loader must not replace it on first acquisition.
    """

    global _provider, _environment_provider_initialized
    replacement = _DEFAULT_PROVIDER if provider is None else provider
    _validate_provider_id(getattr(replacement, "provider_id", None))
    if not callable(getattr(replacement, "acquire", None)):
        raise TypeError("workflow admission provider must define async acquire(request)")
    previous = _provider
    _provider = replacement
    _environment_provider_initialized = True
    return previous


def get_workflow_admission_provider() -> WorkflowAdmissionProvider:
    return _provider


def _matching_provider_entry_points(selector: str) -> tuple[Any, ...]:
    entry_points = importlib.metadata.entry_points()
    select = getattr(entry_points, "select", None)
    if callable(select):
        return tuple(select(group=_PROVIDER_ENTRY_POINT_GROUP, name=selector))

    if isinstance(entry_points, Mapping):
        candidates = entry_points.get(_PROVIDER_ENTRY_POINT_GROUP, ())
    else:
        candidates = entry_points
    return tuple(
        entry_point
        for entry_point in candidates
        if getattr(entry_point, "group", _PROVIDER_ENTRY_POINT_GROUP)
        == _PROVIDER_ENTRY_POINT_GROUP
        and getattr(entry_point, "name", None) == selector
    )


def configure_workflow_admission_from_environment(
    selection: str | None = None,
) -> WorkflowAdmissionProvider:
    """Install one named provider entry point from trusted process config.

    Providers register factories in the
    ``lf_nodes.workflow_admission_providers`` entry-point group.  The setting
    selects an entry-point name, never an importable module path.  LF passes
    its exact active ABI types into the factory so ComfyUI's dual
    plugin/package import names cannot create lookalike context types after a
    prompt has already crossed the queue boundary.
    """

    global _environment_provider_initialized

    with _environment_provider_lock:
        if selection is None and _environment_provider_initialized:
            return get_workflow_admission_provider()

        selected = (
            os.environ.get(_PROVIDER_ENVIRONMENT_VARIABLE, "")
            if selection is None
            else selection
        )
        if not isinstance(selected, str):
            raise TypeError("workflow admission provider selection must be a string")
        selected = selected.strip()

        if selected in ("", _DEFAULT_PROVIDER.provider_id):
            if selected:
                set_workflow_admission_provider(None)
            _environment_provider_initialized = True
            return get_workflow_admission_provider()

        selected = _validate_provider_id(selected)
        matches = _matching_provider_entry_points(selected)
        if not matches:
            raise RuntimeError(
                f"no installed workflow admission provider entry point named {selected!r}"
            )
        if len(matches) != 1:
            raise RuntimeError(
                f"multiple workflow admission provider entry points named {selected!r}"
            )

        entry_point = matches[0]
        try:
            factory = entry_point.load()
        except Exception as exc:
            raise RuntimeError(
                f"failed to load workflow admission provider {selected!r}"
            ) from exc
        if not callable(factory):
            raise RuntimeError(
                f"workflow admission provider entry point {selected!r} "
                "did not load a callable factory"
            )
        provider = factory(
            prompt_context_type=WorkflowPromptContext,
            submission_rejected_type=WorkflowSubmissionRejectedBeforeQueue,
        )
        if getattr(provider, "provider_id", None) != selected:
            raise RuntimeError("workflow admission provider factory returned wrong id")

        set_workflow_admission_provider(provider)
        _environment_provider_initialized = True
        return provider


async def acquire_workflow_admission(
    request: WorkflowSubmissionRequest,
) -> AcquiredWorkflowAdmission:
    """Acquire the installed provider for one exact prepared submission."""

    configure_workflow_admission_from_environment()
    provider = get_workflow_admission_provider()
    provider_id = _validate_provider_id(getattr(provider, "provider_id", None))
    if (
        request.required_provider_id is not None
        and provider_id != request.required_provider_id
    ):
        raise PermissionError(
            f"workflow requires admission provider '{request.required_provider_id}', "
            f"but installed provider is '{provider_id}'"
        )

    lease = await provider.acquire(request)
    if not callable(getattr(lease, "submit", None)) or not callable(
        getattr(lease, "release", None)
    ):
        raise TypeError("workflow admission provider returned an invalid lease")
    return AcquiredWorkflowAdmission(lease, request)


async def acquire_default_workflow_admission(
    request: WorkflowSubmissionRequest,
) -> AcquiredWorkflowAdmission:
    """Acquire LF's no-op/default delegating lease for legacy callers."""

    if request.required_provider_id is not None:
        raise PermissionError(
            f"workflow requires admission provider '{request.required_provider_id}'; "
            "direct default submission is forbidden"
        )
    lease = await _DEFAULT_PROVIDER.acquire(request)
    return AcquiredWorkflowAdmission(lease, request)


__all__ = [
    "AcquiredWorkflowAdmission",
    "RetainedWorkflowAdmission",
    "WorkflowAdmissionLease",
    "WorkflowAdmissionOutcome",
    "WorkflowAdmissionProvider",
    "WorkflowPromptContext",
    "WorkflowSubmissionDelegate",
    "WorkflowSubmissionOutcomeUnknown",
    "WorkflowSubmissionRejectedBeforeQueue",
    "WorkflowSubmissionRequest",
    "acquire_default_workflow_admission",
    "acquire_workflow_admission",
    "configure_workflow_admission_from_environment",
    "get_retained_workflow_admission",
    "get_workflow_admission_provider",
    "list_retained_workflow_admissions",
    "reconcile_retained_workflow_admission",
    "retain_workflow_admission",
    "set_workflow_admission_provider",
]
