"""Lifecycle registry for Workflow Runner submissions.

The ComfyUI ``prompt_id`` remains LF's canonical run id for backwards
compatibility.  This registry adds a caller-stable submission id around it so
automation can safely retry a request, inspect its event trail, discover
outputs, and target cancellation without learning ComfyUI internals.

The rich event trail remains process-local.  Once ComfyUI accepts a prompt,
the stable id, request fingerprint, owner, prompt id, and Core URL are also
stored with the canonical job record.  That small durable authority lets a
restarted Runner recover idempotent retries and exact cancellation without
pretending to be a distributed scheduler.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import re
import time
import uuid

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from ..utils.media import media_type_for_filename


SCHEMA_VERSION = "lf.workflow-submission.v1"
EVENT_SCHEMA_VERSION = "lf.workflow-event.v1"
MANIFEST_SCHEMA_VERSION = "lf.workflow-output-manifest.v1"

_SUBMISSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_TERMINAL_STATES = {"succeeded", "failed", "cancelled", "timeout"}
_OUTPUTS_JSON_BUDGET_BYTES = 256 * 1024
_ARTIFACTS_JSON_BUDGET_BYTES = 128 * 1024
_OUTPUT_NODES_JSON_BUDGET_BYTES = 32 * 1024
_MAX_ARTIFACTS = 256
_MAX_OUTPUT_NODES = 512
_MAX_OUTPUT_NODE_ID_BYTES = 512
_MAX_PREFERRED_OUTPUT_BYTES = 512
_MAX_ARTIFACT_PATH_CHARS = 4096
_MAX_MANIFEST_TRAVERSAL_ITEMS = 4096
_MAX_MANIFEST_TRAVERSAL_DEPTH = 32


class SubmissionLifecycleError(ValueError):
    """Base error carrying a stable API detail code."""

    def __init__(self, detail: str, message: str) -> None:
        super().__init__(message)
        self.detail = detail


class SubmissionConflictError(SubmissionLifecycleError):
    """Raised when a stable id is reused for a different request."""


@dataclass
class SubmissionRecord:
    submission_id: str
    workflow_id: str
    request_fingerprint: str
    owner_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: str = "accepted"
    prompt_id: Optional[str] = None
    comfy_url: Optional[str] = None
    cancel_requested: bool = False
    error: Optional[str] = None
    output_manifest: Optional[Dict[str, Any]] = None
    events: list[Dict[str, Any]] = field(default_factory=list)


_records: Dict[str, SubmissionRecord] = {}
_prompt_index: Dict[str, str] = {}
_lock = asyncio.Lock()


def _fingerprint_payload(payload: Mapping[str, Any]) -> str:
    canonical_payload = {
        key: value
        for key, value in payload.items()
        if key not in {"submissionId", "submission_id"}
    }
    try:
        encoded = json.dumps(
            canonical_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise SubmissionLifecycleError(
            "invalid_submission_payload",
            "workflow payload must be JSON serializable",
        ) from exc
    return hashlib.sha256(encoded).hexdigest()


def _requested_submission_id(payload: Mapping[str, Any]) -> Optional[str]:
    camel = payload.get("submissionId")
    snake = payload.get("submission_id")
    if camel is not None and snake is not None and camel != snake:
        raise SubmissionLifecycleError(
            "conflicting_submission_id",
            "submissionId and submission_id must match when both are supplied",
        )
    value = camel if camel is not None else snake
    if value is None:
        return None
    if not isinstance(value, str) or not _SUBMISSION_ID_RE.fullmatch(value):
        raise SubmissionLifecycleError(
            "invalid_submission_id",
            "submission id must be 1-128 portable characters",
        )
    return value


def _append_event(
    record: SubmissionRecord,
    event_type: str,
    status: str,
    **details: Any,
) -> None:
    now = time.time()
    event: Dict[str, Any] = {
        "schema": EVENT_SCHEMA_VERSION,
        "submission_id": record.submission_id,
        "seq": len(record.events) + 1,
        "type": event_type,
        "status": status,
        "created_at": now,
    }
    if record.prompt_id is not None:
        event["run_id"] = record.prompt_id
    if details:
        event["details"] = deepcopy(details)
    record.events.append(event)
    record.status = status
    record.updated_at = now


def _links(submission_id: str) -> Dict[str, str]:
    base = f"/api/lf-nodes/submissions/{submission_id}"
    return {
        "status": base,
        "events": f"{base}/events",
        "cancel": f"{base}/cancel",
    }


def _snapshot(record: SubmissionRecord, *, include_events: bool = True) -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "submission_id": record.submission_id,
        "run_id": record.prompt_id,
        "workflow_id": record.workflow_id,
        "owner_id": record.owner_id,
        "status": record.status,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "cancel_requested": record.cancel_requested,
        "error": record.error,
        "output_manifest": deepcopy(record.output_manifest),
        "links": _links(record.submission_id),
    }
    if include_events:
        snapshot["events"] = deepcopy(record.events)
    else:
        snapshot["event_count"] = len(record.events)
        snapshot["latest_event"] = deepcopy(record.events[-1]) if record.events else None
    return snapshot


def _job_value(job: Any, name: str, default: Any = None) -> Any:
    if isinstance(job, Mapping):
        return job.get(name, default)
    return getattr(job, name, default)


def _job_status(job: Any) -> str:
    value = _job_value(job, "status", "pending")
    return str(getattr(value, "value", value) or "pending")


async def _hydrate_durable_job(job: Any) -> Optional[SubmissionRecord]:
    """Restore the control-plane identity carried by one canonical job row."""

    submission_id = _job_value(job, "submission_id")
    prompt_id = _job_value(job, "id") or _job_value(job, "run_id")
    fingerprint = _job_value(job, "request_fingerprint")
    comfy_url = _job_value(job, "comfy_url")
    if not isinstance(submission_id, str) or not submission_id:
        return None
    if (
        not isinstance(prompt_id, str)
        or not prompt_id
        or not isinstance(fingerprint, str)
        or not fingerprint
        or not isinstance(comfy_url, str)
        or not comfy_url
    ):
        # A partial identity cannot safely authorize a replay or cancellation.
        raise SubmissionLifecycleError(
            "submission_identity_unavailable",
            "stored submission identity is incomplete",
        )

    created_at = _job_value(job, "created_at", time.time())
    updated_at = _job_value(job, "updated_at", created_at)
    try:
        created_at = float(created_at)
    except (TypeError, ValueError):
        created_at = time.time()
    try:
        updated_at = float(updated_at)
    except (TypeError, ValueError):
        updated_at = created_at
    status = _job_status(job)
    result = _job_value(job, "result")
    output_manifest = None
    if result is not None and status == "succeeded":
        output_manifest = build_output_manifest(submission_id, prompt_id, result)

    hydrated = SubmissionRecord(
        submission_id=submission_id,
        workflow_id=str(_job_value(job, "workflow_id", "") or ""),
        request_fingerprint=fingerprint,
        owner_id=_job_value(job, "owner_id"),
        created_at=created_at,
        updated_at=updated_at,
        status=status,
        prompt_id=prompt_id,
        comfy_url=comfy_url,
        error=_job_value(job, "error"),
        output_manifest=output_manifest,
    )

    async with _lock:
        existing = _records.get(submission_id)
        if existing is not None:
            if (
                existing.prompt_id != prompt_id
                or existing.request_fingerprint != fingerprint
                or existing.owner_id != hydrated.owner_id
            ):
                raise SubmissionConflictError(
                    "submission_identity_conflict",
                    "stored submission identity conflicts with process state",
                )
            return existing
        indexed_submission = _prompt_index.get(prompt_id)
        if indexed_submission is not None and indexed_submission != submission_id:
            raise SubmissionConflictError(
                "prompt_submission_conflict",
                "ComfyUI prompt is already bound to another submission",
            )
        _records[submission_id] = hydrated
        _prompt_index[prompt_id] = submission_id
        return hydrated


async def _load_durable_submission(submission_id: str) -> Optional[SubmissionRecord]:
    # Runtime import avoids a lifecycle -> store -> serializer -> lifecycle
    # import cycle during service startup.
    from .job_store import get_job_by_submission_id

    job = await get_job_by_submission_id(submission_id)
    return await _hydrate_durable_job(job) if job is not None else None


async def reserve_submission(
    payload: Mapping[str, Any],
    workflow_id: str,
    owner_id: Optional[str] = None,
) -> tuple[Dict[str, Any], bool]:
    """Reserve a stable id before queue submission.

    Returns ``(snapshot, created)``.  Reusing the same explicit id with the
    exact same request is an idempotent replay; a different request is rejected.
    """

    requested = _requested_submission_id(payload)
    submission_id = requested or f"lf-{uuid.uuid4().hex}"
    fingerprint = _fingerprint_payload(payload)

    if requested is not None:
        async with _lock:
            existing = _records.get(submission_id)
            if existing is not None:
                if (
                    existing.request_fingerprint != fingerprint
                    or existing.owner_id != owner_id
                ):
                    raise SubmissionConflictError(
                        "submission_id_conflict",
                        f"submission id '{submission_id}' already belongs to another request",
                    )
                return _snapshot(existing, include_events=False), False

        # A verified storage miss is the only safe basis for accepting an
        # explicit id after process restart. Storage errors deliberately
        # propagate so a retry cannot duplicate an already accepted prompt.
        durable = await _load_durable_submission(submission_id)
        if durable is not None:
            if (
                durable.request_fingerprint != fingerprint
                or durable.owner_id != owner_id
            ):
                raise SubmissionConflictError(
                    "submission_id_conflict",
                    f"submission id '{submission_id}' already belongs to another request",
                )
            return _snapshot(durable, include_events=False), False

    async with _lock:
        # Recheck after the storage read so concurrent in-process reservations
        # for the same explicit id remain single-writer.
        existing = _records.get(submission_id)
        if existing is not None:
            if (
                existing.request_fingerprint != fingerprint
                or existing.owner_id != owner_id
            ):
                raise SubmissionConflictError(
                    "submission_id_conflict",
                    f"submission id '{submission_id}' already belongs to another request",
                )
            return _snapshot(existing, include_events=False), False

        record = SubmissionRecord(
            submission_id=submission_id,
            workflow_id=workflow_id,
            request_fingerprint=fingerprint,
            owner_id=owner_id,
        )
        _append_event(record, "accepted", "accepted")
        _records[submission_id] = record
        return _snapshot(record, include_events=False), True


async def bind_prompt(
    submission_id: str,
    prompt_id: str,
    comfy_url: str,
) -> Dict[str, Any]:
    async with _lock:
        record = _records.get(submission_id)
        if record is None:
            raise SubmissionLifecycleError("submission_not_found", "unknown submission")
        if record.prompt_id is not None and record.prompt_id != prompt_id:
            raise SubmissionConflictError(
                "submission_prompt_conflict",
                "submission is already bound to another ComfyUI prompt",
            )
        other = _prompt_index.get(prompt_id)
        if other is not None and other != submission_id:
            raise SubmissionConflictError(
                "prompt_submission_conflict",
                "ComfyUI prompt is already bound to another submission",
            )
        record.prompt_id = prompt_id
        record.comfy_url = comfy_url
        _prompt_index[prompt_id] = submission_id
        _append_event(record, "submitted", "pending", run_id=prompt_id)
        return _snapshot(record, include_events=False)


async def record_running(prompt_id: str) -> Optional[Dict[str, Any]]:
    async with _lock:
        submission_id = _prompt_index.get(prompt_id)
        record = _records.get(submission_id) if submission_id else None
        if record is None or record.status in _TERMINAL_STATES:
            return None
        if record.status != "running":
            _append_event(record, "running", "running")
        return _snapshot(record, include_events=False)


class _JsonBudgetExceeded(Exception):
    pass


def _bounded_json_safe(
    value: Any,
    max_bytes: int = _OUTPUTS_JSON_BUDGET_BYTES,
) -> tuple[Any, bool]:
    """Normalize JSON data while aborting before oversized values are copied."""

    remaining = max_bytes

    def consume(size: int) -> None:
        nonlocal remaining
        remaining -= size
        if remaining < 0:
            raise _JsonBudgetExceeded

    def scalar(item: Any) -> Any:
        if isinstance(item, float) and not math.isfinite(item):
            item = str(item)
        if isinstance(item, str) and len(item) > remaining:
            raise _JsonBudgetExceeded
        encoded = json.dumps(
            item,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
        consume(len(encoded))
        return item

    def normalize(item: Any) -> Any:
        if item is None or isinstance(item, (bool, int, float, str)):
            return scalar(item)
        if isinstance(item, Mapping):
            consume(2)  # Braces.
            normalized: Dict[str, Any] = {}
            for index, (key, child) in enumerate(item.items()):
                if index:
                    consume(1)  # Comma.
                normalized_key = str(key)
                scalar(normalized_key)
                consume(1)  # Colon.
                normalized[normalized_key] = normalize(child)
            return normalized
        if isinstance(item, (list, tuple)):
            consume(2)  # Brackets.
            normalized_items = []
            for index, child in enumerate(item):
                if index:
                    consume(1)  # Comma.
                normalized_items.append(normalize(child))
            return normalized_items
        return scalar(str(item))

    try:
        return normalize(value), False
    except (_JsonBudgetExceeded, RecursionError):
        return {
            "_truncated": True,
            "reason": (
                f"output payload exceeded {max_bytes}-byte "
                "manifest budget"
            ),
        }, True


def build_output_manifest(
    submission_id: str,
    prompt_id: str,
    result: Any,
) -> Dict[str, Any]:
    body = result.get("body", {}) if isinstance(result, Mapping) else {}
    payload = body.get("payload", {}) if isinstance(body, Mapping) else {}
    history = payload.get("history", {}) if isinstance(payload, Mapping) else {}
    outputs = history.get("outputs", {}) if isinstance(history, Mapping) else {}
    outputs = outputs if isinstance(outputs, Mapping) else {}

    artifacts: list[Dict[str, Any]] = []
    artifact_keys: set[tuple[str, str, str, str]] = set()
    artifact_bytes = 2  # JSON list brackets.
    artifacts_truncated = False
    traversal_items = 0
    traversal_truncated = False

    def bounded_identifier(value: Any, max_bytes: int) -> tuple[Optional[str], bool]:
        if value is None:
            return None, False
        normalized = str(value)
        if len(normalized.encode("utf-8")) > max_bytes:
            return None, True
        return normalized, False

    def child_path(path: str, component: str) -> str:
        return component[:_MAX_ARTIFACT_PATH_CHARS] if not path else (
            f"{path}.{component}"[:_MAX_ARTIFACT_PATH_CHARS]
        )

    def indexed_path(path: str, index: int) -> str:
        return f"{path}[{index}]"[:_MAX_ARTIFACT_PATH_CHARS]

    def append_artifact(
        node_id: str,
        path: str,
        filename: str,
        subfolder: str,
        storage_type: str,
    ) -> None:
        nonlocal artifact_bytes, artifacts_truncated
        if artifacts_truncated:
            return
        # Standard Comfy history descriptors use OS-native separators. Keep
        # legacy LF ``file_names`` strict, but normalize this structured
        # subfolder field before validating and publishing the manifest.
        subfolder = subfolder.replace("\\", "/")
        subfolder_parts = subfolder.split("/") if subfolder else []
        if (
            not filename
            or len(filename) > 1024
            or any(ord(character) < 32 for character in filename)
            or ":" in filename
            or "/" in filename
            or "\\" in filename
            or filename in {".", ".."}
            or len(subfolder) > 1024
            or any(ord(character) < 32 for character in subfolder)
            or subfolder.startswith("/")
            or any(
                part in {"", ".", ".."} or ":" in part
                for part in subfolder_parts
            )
            or storage_type not in {"input", "output", "temp"}
        ):
            return
        key = (node_id, filename, subfolder, storage_type)
        if key in artifact_keys:
            return
        artifact: Dict[str, Any] = {
            "node_id": node_id[:128],
            "path": path[:_MAX_ARTIFACT_PATH_CHARS],
            "filename": filename,
            "subfolder": subfolder,
            "storage_type": storage_type,
        }
        media_type = media_type_for_filename(filename)
        if media_type:
            artifact["media_type"] = media_type
        encoded_size = len(
            json.dumps(
                artifact,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        separator_size = 1 if artifacts else 0
        if (
            len(artifacts) >= _MAX_ARTIFACTS
            or artifact_bytes + separator_size + encoded_size > _ARTIFACTS_JSON_BUDGET_BYTES
        ):
            artifacts_truncated = True
            return
        artifact_keys.add(key)
        artifacts.append(artifact)
        artifact_bytes += separator_size + encoded_size

    def append_lf_file_names(node_id: str, value: Mapping[str, Any], path: str) -> None:
        nonlocal traversal_items, traversal_truncated
        lf_output = value.get("lf_output")
        if not isinstance(lf_output, (list, tuple)):
            return
        for output_index, output in enumerate(lf_output):
            if artifacts_truncated:
                return
            traversal_items += 1
            if traversal_items > _MAX_MANIFEST_TRAVERSAL_ITEMS:
                traversal_truncated = True
                return
            if not isinstance(output, Mapping):
                continue
            file_names = output.get("file_names")
            if not isinstance(file_names, (list, tuple)):
                continue
            for file_index, raw_file_name in enumerate(file_names):
                if artifacts_truncated:
                    return
                traversal_items += 1
                if traversal_items > _MAX_MANIFEST_TRAVERSAL_ITEMS:
                    traversal_truncated = True
                    return
                if not isinstance(raw_file_name, str) or not raw_file_name:
                    continue
                if (
                    "\x00" in raw_file_name
                    or "\\" in raw_file_name
                    or raw_file_name.startswith("/")
                    or len(raw_file_name) > 1024
                ):
                    continue
                parts = raw_file_name.split("/")
                if any(part in {"", ".", ".."} or ":" in part for part in parts):
                    continue
                filename = parts[-1]
                subfolder = "/".join(parts[:-1])
                artifact_path = (
                    f"{path}.lf_output[{output_index}].file_names[{file_index}]"
                    if path
                    else f"lf_output[{output_index}].file_names[{file_index}]"
                )
                append_artifact(
                    node_id,
                    artifact_path,
                    filename,
                    subfolder,
                    "output",
                )

    def walk(node_id: str, value: Any, path: str, depth: int = 0) -> None:
        nonlocal traversal_items, traversal_truncated
        if traversal_truncated or artifacts_truncated:
            return
        traversal_items += 1
        if (
            traversal_items > _MAX_MANIFEST_TRAVERSAL_ITEMS
            or depth > _MAX_MANIFEST_TRAVERSAL_DEPTH
        ):
            traversal_truncated = True
            return
        if isinstance(value, Mapping):
            filename = value.get("filename")
            if isinstance(filename, str) and filename:
                append_artifact(
                    node_id,
                    path,
                    filename,
                    str(value.get("subfolder") or ""),
                    str(value.get("type") or "output"),
                )
            for key, item in value.items():
                walk(
                    node_id,
                    item,
                    child_path(path, str(key)),
                    depth + 1,
                )
            append_lf_file_names(node_id, value, path)
        elif isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                walk(node_id, item, indexed_path(path, index), depth + 1)

    for raw_node_id, node_output in outputs.items():
        if traversal_truncated or artifacts_truncated:
            break
        node_id, node_id_truncated = bounded_identifier(
            raw_node_id,
            _MAX_OUTPUT_NODE_ID_BYTES,
        )
        if node_id_truncated or node_id is None:
            traversal_truncated = True
            continue
        walk(node_id, node_output, "")

    output_nodes: list[str] = []
    output_nodes_bytes = 2  # JSON list brackets.
    output_nodes_truncated = False
    for raw_node_id in outputs.keys():
        node_id, node_id_truncated = bounded_identifier(
            raw_node_id,
            _MAX_OUTPUT_NODE_ID_BYTES,
        )
        if node_id_truncated or node_id is None:
            output_nodes_truncated = True
            continue
        encoded_size = len(
            json.dumps(node_id, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        )
        separator_size = 1 if output_nodes else 0
        if (
            len(output_nodes) >= _MAX_OUTPUT_NODES
            or output_nodes_bytes + separator_size + encoded_size
            > _OUTPUT_NODES_JSON_BUDGET_BYTES
        ):
            output_nodes_truncated = True
            break
        output_nodes.append(node_id)
        output_nodes_bytes += separator_size + encoded_size

    preferred_output, preferred_output_truncated = bounded_identifier(
        payload.get("preferred_output"),
        _MAX_PREFERRED_OUTPUT_BYTES,
    )

    safe_outputs, outputs_truncated = _bounded_json_safe(outputs)
    manifest_truncated = any(
        (
            outputs_truncated,
            artifacts_truncated,
            output_nodes_truncated,
            traversal_truncated,
            preferred_output_truncated,
        )
    )
    return {
        "schema": MANIFEST_SCHEMA_VERSION,
        "submission_id": submission_id,
        "run_id": prompt_id,
        "preferred_output": preferred_output,
        "output_nodes": output_nodes,
        "artifacts": artifacts,
        "outputs": safe_outputs,
        "outputs_truncated": outputs_truncated,
        "artifacts_truncated": artifacts_truncated,
        "output_nodes_truncated": output_nodes_truncated,
        "traversal_truncated": traversal_truncated,
        "preferred_output_truncated": preferred_output_truncated,
        "manifest_truncated": manifest_truncated,
    }


async def record_terminal(
    prompt_id: str,
    status: str,
    *,
    result: Any = None,
    error: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if status not in _TERMINAL_STATES:
        raise SubmissionLifecycleError("invalid_terminal_status", "invalid terminal status")
    async with _lock:
        submission_id = _prompt_index.get(prompt_id)
        record = _records.get(submission_id) if submission_id else None
        if record is None:
            return None
        if record.status in _TERMINAL_STATES:
            return _snapshot(record, include_events=False)
        record.error = error
        if result is not None:
            record.output_manifest = build_output_manifest(
                record.submission_id,
                prompt_id,
                result,
            )
        _append_event(record, status, status, error=error)
        return _snapshot(record, include_events=False)


async def record_prequeue_failure(
    submission_id: str,
    error: str,
    *,
    ambiguous: bool = False,
) -> Optional[Dict[str, Any]]:
    async with _lock:
        record = _records.get(submission_id)
        if record is None:
            return None
        record.error = error
        if ambiguous:
            _append_event(record, "reconciliation_required", "reconciling", error=error)
        else:
            _append_event(record, "submission_failed", "failed", error=error)
        return _snapshot(record, include_events=False)


async def record_cancel_requested(submission_id: str) -> Dict[str, Any]:
    async with _lock:
        record = _records.get(submission_id)
        if record is None:
            raise SubmissionLifecycleError("submission_not_found", "unknown submission")
        if record.status in _TERMINAL_STATES:
            raise SubmissionConflictError(
                "submission_already_terminal",
                "terminal submissions cannot be cancelled",
            )
        if not record.cancel_requested:
            record.cancel_requested = True
            _append_event(record, "cancel_requested", record.status)
        return _snapshot(record, include_events=False)


async def record_proven_pending_cancellation(
    prompt_id: str,
    *,
    result: Any = None,
) -> Optional[Dict[str, Any]]:
    """Publish cancellation backed by an exact Core pending dequeue.

    The background reconciler can infer ``execution_state_lost`` in the small
    interval between Core dequeuing a prompt and this process publishing the
    cancellation.  Exact dequeue proof is stronger than that synthetic
    negative-state inference, so this transition may correct only that one
    failure.  Real execution failures and all other terminal outcomes remain
    immutable.
    """

    async with _lock:
        submission_id = _prompt_index.get(prompt_id)
        record = _records.get(submission_id) if submission_id else None
        if record is None:
            return None

        if record.status == "cancelled":
            record.cancel_requested = True
            return _snapshot(record, include_events=False)
        if record.status in {"succeeded", "timeout"}:
            return _snapshot(record, include_events=False)
        if record.status == "failed" and record.error != "execution_state_lost":
            return _snapshot(record, include_events=False)

        corrected_state_loss = (
            record.status == "failed" and record.error == "execution_state_lost"
        )
        previous_error = record.error
        record.cancel_requested = True
        record.error = None
        record.output_manifest = None
        _append_event(
            record,
            "execution_state_lost_corrected"
            if corrected_state_loss
            else "cancelled",
            "cancelled",
            reason="exact_pending_dequeue",
            **(
                {"previous_error": previous_error}
                if corrected_state_loss
                else {}
            ),
        )
        return _snapshot(record, include_events=False)


async def get_submission(
    submission_id: str,
    *,
    include_events: bool = True,
) -> Optional[Dict[str, Any]]:
    async with _lock:
        record = _records.get(submission_id)
        if record is not None:
            return _snapshot(record, include_events=include_events)
    record = await _load_durable_submission(submission_id)
    return _snapshot(record, include_events=include_events) if record else None


async def get_submission_by_prompt(
    prompt_id: str,
    *,
    include_events: bool = True,
) -> Optional[Dict[str, Any]]:
    async with _lock:
        submission_id = _prompt_index.get(prompt_id)
        record = _records.get(submission_id) if submission_id else None
        if record is not None:
            return _snapshot(record, include_events=include_events)

    from .job_store import get_job

    job = await get_job(prompt_id)
    record = await _hydrate_durable_job(job) if job is not None else None
    return _snapshot(record, include_events=include_events) if record else None


async def get_submissions_by_prompts(
    prompt_ids: list[str],
) -> Dict[str, Dict[str, Any]]:
    """Snapshot stable lifecycle handles for a bounded run-list response."""

    requested = {prompt_id for prompt_id in prompt_ids if prompt_id}
    async with _lock:
        snapshots: Dict[str, Dict[str, Any]] = {}
        for prompt_id in requested:
            submission_id = _prompt_index.get(prompt_id)
            record = _records.get(submission_id) if submission_id else None
            if record is not None:
                snapshots[prompt_id] = _snapshot(record, include_events=False)
        return snapshots


async def get_cancel_target(submission_id: str) -> Optional[Dict[str, Any]]:
    await get_submission(submission_id, include_events=False)
    async with _lock:
        record = _records.get(submission_id)
        if record is None:
            return None
        return {
            "submission_id": record.submission_id,
            "run_id": record.prompt_id,
            "comfy_url": record.comfy_url,
            "status": record.status,
            "cancel_requested": record.cancel_requested,
        }


async def get_submission_persistence_fields(
    submission_id: str,
) -> Optional[Dict[str, str]]:
    """Return private identity fields for the canonical post-queue job row."""

    async with _lock:
        record = _records.get(submission_id)
        if (
            record is None
            or not record.prompt_id
            or not record.comfy_url
            or not record.request_fingerprint
        ):
            return None
        return {
            "submission_id": record.submission_id,
            "request_fingerprint": record.request_fingerprint,
            "comfy_url": record.comfy_url,
        }


async def reset_for_tests() -> None:
    """Clear process state.  Deliberately public only for focused unit tests."""

    async with _lock:
        _records.clear()
        _prompt_index.clear()


__all__ = [
    "EVENT_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "SCHEMA_VERSION",
    "SubmissionConflictError",
    "SubmissionLifecycleError",
    "bind_prompt",
    "build_output_manifest",
    "get_cancel_target",
    "get_submission",
    "get_submission_by_prompt",
    "get_submission_persistence_fields",
    "get_submissions_by_prompts",
    "record_cancel_requested",
    "record_proven_pending_cancellation",
    "record_prequeue_failure",
    "record_running",
    "record_terminal",
    "reserve_submission",
]
