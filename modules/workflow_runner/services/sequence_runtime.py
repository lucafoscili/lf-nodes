"""Durable linear orchestration for declaration-driven Runner sequences.

The runtime intentionally composes ordinary workflow submissions.  It does not
own Comfy graphs, infer domain compatibility, or create a second execution
path.  A sequence is a bounded list of narrow workflows whose public inputs,
literal defaults, and durable media or text from declared earlier stages are wired
declaratively. Stages still execute one at a time in declaration order.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import uuid

from copy import deepcopy
from inspect import isawaitable
from typing import Any, Awaitable, Callable, Mapping

from . import job_store, sequence_store
from .job_store import JobStatus
from .remix_inputs import project_public_output_artifacts


SEQUENCE_PARENT_RUN_PREFIX = "lf-sequence:"
_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CHILD_SUBMISSION_PATTERN = re.compile(r"^lfseq:[0-9a-f]{32}:0[0-7]$")
_MIN_STAGES = 2
_MAX_STAGES = 8
_MAX_BINDINGS_PER_STAGE = 128
_TERMINAL_STATUSES = frozenset({"succeeded", "failed", "cancelled", "timeout"})
_ACTIVE_CHILD_STATUSES = frozenset({"pending", "running"})

ChildRunner = Callable[..., Awaitable[Mapping[str, Any]]]
ChildCanceller = Callable[[str], Awaitable[Mapping[str, Any]]]
OutputNodeResolver = Callable[[str, str], str]
WorkflowResolver = Callable[[str], Any]

_locks: dict[str, asyncio.Lock] = {}
_supervisors: dict[str, asyncio.Task[dict[str, Any]]] = {}
LOG = logging.getLogger(__name__)


class SequenceExecutionError(RuntimeError):
    """One bounded, user-presentable orchestration failure."""

    def __init__(self, detail: str, message: str) -> None:
        super().__init__(message)
        self.detail = detail


def is_sequence_parent_run_id(run_id: Any) -> bool:
    """Allow Core's prompt reconciler to skip synthetic sequence parents."""

    return isinstance(run_id, str) and run_id.startswith(SEQUENCE_PARENT_RUN_PREFIX)


def is_sequence_parent_job(job: Any) -> bool:
    if isinstance(job, Mapping):
        run_id = job.get("id") or job.get("run_id")
    else:
        run_id = getattr(job, "id", getattr(job, "run_id", job))
    return is_sequence_parent_run_id(run_id)


def is_sequence_child_submission_id(submission_id: Any) -> bool:
    """Identify private child runs so list/SSE projections can hide plumbing."""

    return (
        isinstance(submission_id, str)
        and _CHILD_SUBMISSION_PATTERN.fullmatch(submission_id) is not None
    )


def is_sequence_child_job(job: Any) -> bool:
    submission_id = (
        job.get("submission_id")
        if isinstance(job, Mapping)
        else getattr(job, "submission_id", None)
    )
    return is_sequence_child_submission_id(submission_id)


def make_sequence_parent_run_id() -> str:
    return f"{SEQUENCE_PARENT_RUN_PREFIX}{uuid.uuid4().hex}"


def child_submission_id(parent_run_id: str, stage_index: int, stage_id: str) -> str:
    """Return one portable stable id derived solely from parent and stage."""

    authority = f"{parent_run_id}\0{stage_index}\0{stage_id}".encode("utf-8")
    digest = hashlib.sha256(authority).hexdigest()
    return f"lfseq:{digest[:32]}:{stage_index:02d}"


def _read(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _bounded_id(value: Any, label: str) -> str:
    normalized = value.strip() if isinstance(value, str) else ""
    if not _ID_PATTERN.fullmatch(normalized):
        raise ValueError(f"{label} must be a portable identifier of at most 128 characters")
    return normalized


def _json_copy(value: Any, label: str) -> Any:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be JSON serializable") from exc


def _default_output_node_resolver(workflow_id: str, output_id: str) -> str:
    from .registry import get_workflow

    definition = get_workflow(workflow_id)
    if definition is None:
        raise ValueError(f"unknown stage workflow '{workflow_id}'")
    if getattr(definition, "stages", None) is not None:
        raise ValueError("sequence stages cannot reference another sequence")
    matches = [
        str(getattr(cell, "node_id", ""))
        for cell in definition.outputs
        if getattr(cell, "id", None) == output_id
    ]
    if len(matches) != 1 or not matches[0]:
        raise ValueError(
            f"workflow '{workflow_id}' has no unique public output '{output_id}'"
        )
    return matches[0]


def _default_workflow_resolver(workflow_id: str) -> Any:
    from .registry import WorkflowNode, get_workflow

    definition = get_workflow(workflow_id)
    if definition is None:
        raise ValueError(f"unknown stage workflow '{workflow_id}'")
    if not isinstance(definition, WorkflowNode):
        raise ValueError("sequence stages cannot reference another sequence")
    return definition


def _select_default(cell: Any, props: Mapping[str, Any]) -> Any:
    dataset = props.get("lfDataset")
    nodes = dataset.get("nodes") if isinstance(dataset, Mapping) else None
    if not isinstance(nodes, (list, tuple)) or not nodes:
        raise ValueError(f"select input '{_read(cell, 'id')}' has no options")
    raw_default = props.get("lfValue")
    selected: Any = None
    if type(raw_default) is int:
        if 0 <= raw_default < len(nodes):
            selected = nodes[raw_default]
    else:
        selected = next(
            (
                option
                for option in nodes
                if isinstance(option, Mapping)
                and str(option.get("id", "")) == str(raw_default)
            ),
            None,
        )
    if not isinstance(selected, Mapping):
        raise ValueError(
            f"select input '{_read(cell, 'id')}' has an invalid declared default"
        )
    value = selected.get("workflowValue")
    if value is None:
        value = selected.get("value")
    if value is None:
        value = selected.get("id")
    return _json_copy(value, f"default for input '{_read(cell, 'id')}'")


def _semantic_block_defaults(block: Any) -> dict[str, Any]:
    """Mirror the browser dispatcher for one block's untouched controls."""

    defaults: dict[str, Any] = {}
    for cell in _read(block, "inputs", ()):
        input_id = _bounded_id(_read(cell, "id"), "block input id")
        shape = str(_read(cell, "shape", "") or "").lower()
        # Uploads carry user/local custody and never have a portable technical
        # default. Required uploads are checked against declaration bindings.
        if shape == "upload":
            continue
        props = _read(cell, "props", {})
        if not isinstance(props, Mapping) or "lfValue" not in props:
            continue
        defaults[input_id] = (
            _select_default(cell, props)
            if shape == "select"
            else _json_copy(props["lfValue"], f"default for input '{input_id}'")
        )
    return defaults


def _binding_kind(binding: Any) -> str:
    # Bind to the declaration contract when available. The structural fallback
    # keeps focused embedders/tests lightweight without inventing a second
    # public binding shape.
    from .registry import (
        WorkflowSequenceArtifactBinding,
        WorkflowSequenceLiteralBinding,
        WorkflowSequencePublicInputBinding,
        WorkflowSequenceTextBinding,
    )

    if isinstance(binding, WorkflowSequencePublicInputBinding):
        return "public_input"
    if isinstance(binding, WorkflowSequenceLiteralBinding):
        return "literal"
    if isinstance(binding, WorkflowSequenceArtifactBinding):
        return "artifact"
    if isinstance(binding, WorkflowSequenceTextBinding):
        return "text"
    explicit = _read(binding, "kind")
    if isinstance(explicit, str):
        normalized = explicit.strip().lower().replace("-", "_")
        aliases = {
            "public": "public_input",
            "input": "public_input",
            "public_input": "public_input",
            "literal": "literal",
            "artifact": "artifact",
            "text": "text",
        }
        if normalized in aliases:
            return aliases[normalized]
    if _read(binding, "public_input_id") is not None:
        return "public_input"
    if _read(binding, "output_id") is not None:
        return "artifact"
    if isinstance(binding, Mapping) and "value" in binding:
        return "literal"
    if hasattr(binding, "value"):
        return "literal"
    raise ValueError("sequence binding has no recognized source")


def normalize_sequence_definition(
    definition: Any,
    inputs: Mapping[str, Any],
    *,
    output_node_resolver: OutputNodeResolver | None = None,
    workflow_resolver: WorkflowResolver | None = None,
) -> dict[str, Any]:
    """Compile declaration objects into one restart-safe private plan."""

    sequence_id = _bounded_id(_read(definition, "id"), "sequence id")
    if not isinstance(inputs, Mapping):
        raise TypeError("sequence inputs must be a mapping")
    raw_inputs = _json_copy(dict(inputs), "sequence inputs")
    declared_public_cells = _read(definition, "inputs", None)
    public_cells_by_id: dict[str, Any] = {}
    if declared_public_cells is None:
        # Structural test/embedding declarations predate WorkflowSequenceNode.
        # Production declarations always publish their public input cells.
        normalized_inputs = raw_inputs
    else:
        public_cells = tuple(declared_public_cells)
        public_cells_by_id = {_read(cell, "id"): cell for cell in public_cells}
        public_ids = {
            _bounded_id(_read(cell, "id"), "sequence public input id")
            for cell in public_cells
        }
        unknown = sorted(set(raw_inputs) - public_ids)
        if unknown:
            raise ValueError(
                "sequence inputs contain unknown port(s): " + ", ".join(unknown)
            )
        normalized_inputs = _semantic_block_defaults(
            type("_SequenceInputs", (), {"inputs": public_cells})()
        )
        normalized_inputs.update(raw_inputs)
        missing_required = [
            str(_read(cell, "id"))
            for cell in public_cells
            if bool(_read(cell, "required", True))
            and _read(cell, "id") not in normalized_inputs
        ]
        if missing_required:
            raise ValueError(
                "sequence is missing required public input(s): "
                + ", ".join(missing_required)
            )
    raw_stages = _read(definition, "stages")
    if isinstance(raw_stages, (str, bytes)):
        raise TypeError("sequence stages must be a sequence")
    try:
        stages = tuple(raw_stages)
    except TypeError as exc:
        raise TypeError("sequence stages must be a sequence") from exc
    if not _MIN_STAGES <= len(stages) <= _MAX_STAGES:
        raise ValueError(
            f"sequence must contain {_MIN_STAGES} to {_MAX_STAGES} stages"
        )

    declared_stage_ids = tuple(
        _bounded_id(_read(stage, "id"), "stage id") for stage in stages
    )
    if len(set(declared_stage_ids)) != len(declared_stage_ids):
        raise ValueError("sequence stage ids must be unique")

    resolve_output = output_node_resolver or _default_output_node_resolver
    resolve_workflow = workflow_resolver or _default_workflow_resolver
    normalized_stages: list[dict[str, Any]] = []
    for stage_index, stage in enumerate(stages):
        stage_id = declared_stage_ids[stage_index]
        workflow_id = _bounded_id(_read(stage, "workflow_id"), "stage workflow id")
        if workflow_id == sequence_id:
            raise ValueError("sequence stages cannot reference their parent sequence")
        block = resolve_workflow(workflow_id)
        defaults = _semantic_block_defaults(block)

        raw_bindings = _read(stage, "bindings", ())
        if isinstance(raw_bindings, (str, bytes)):
            raise TypeError("stage bindings must be a sequence")
        try:
            bindings = tuple(raw_bindings)
        except TypeError as exc:
            raise TypeError("stage bindings must be a sequence") from exc
        if len(bindings) > _MAX_BINDINGS_PER_STAGE:
            raise ValueError("stage has too many bindings")

        normalized_bindings: list[dict[str, Any]] = []
        target_ids: set[str] = set()
        for binding in bindings:
            target_input_id = _bounded_id(
                _read(binding, "target_input_id"), "target input id"
            )
            if target_input_id in target_ids:
                raise ValueError(
                    f"stage '{stage_id}' binds input '{target_input_id}' more than once"
                )
            target_ids.add(target_input_id)
            kind = _binding_kind(binding)
            normalized: dict[str, Any] = {
                "kind": kind,
                "target_input_id": target_input_id,
            }
            if kind == "public_input":
                public_input_id = _bounded_id(
                    _read(binding, "public_input_id"), "public input id"
                )
                if public_input_id not in normalized_inputs:
                    public_cell = public_cells_by_id.get(public_input_id)
                    target_cell = next((
                        cell for cell in _read(block, "inputs", ())
                        if _read(cell, "id") == target_input_id
                    ), None)
                    if all(
                        cell is not None
                        and _read(cell, "shape") == "upload"
                        and not _read(cell, "required", True)
                        for cell in (public_cell, target_cell)
                    ):
                        target_ids.remove(target_input_id)
                        continue
                    raise ValueError(
                        f"sequence input '{public_input_id}' required by stage "
                        f"'{stage_id}' is missing"
                    )
                normalized["public_input_id"] = public_input_id
            elif kind == "literal":
                normalized["value"] = _json_copy(
                    _read(binding, "value"), "literal binding value"
                )
            else:
                if stage_index == 0:
                    raise ValueError(f"the first sequence stage cannot consume an {kind} output")
                output_id = _bounded_id(_read(binding, "output_id"), "output id")
                raw_source_stage_id = _read(binding, "source_stage_id")
                if raw_source_stage_id is None:
                    # Preserve the original normalized wire byte-for-byte for
                    # every legacy immediate-predecessor binding.  Besides
                    # compatibility, this keeps its definition fingerprint
                    # stable across the additive named-source upgrade.
                    source_stage_index = stage_index - 1
                else:
                    source_stage_id = _bounded_id(
                        raw_source_stage_id,
                        f"{kind} source stage id",
                    )
                    try:
                        source_stage_index = declared_stage_ids.index(
                            source_stage_id
                        )
                    except ValueError as exc:
                        raise ValueError(
                            f"stage '{stage_id}' references unknown {kind} source "
                            f"stage '{source_stage_id}'"
                        ) from exc
                    if source_stage_index == stage_index:
                        raise ValueError(
                            f"stage '{stage_id}' cannot consume an {kind} from itself"
                        )
                    if source_stage_index > stage_index:
                        raise ValueError(
                            f"stage '{stage_id}' references future {kind} source "
                            f"stage '{source_stage_id}'"
                        )
                    normalized["source_stage_id"] = source_stage_id
                    normalized["source_stage_index"] = source_stage_index

                source_workflow_id = str(
                    normalized_stages[source_stage_index]["workflow_id"]
                )
                output_node_id = resolve_output(source_workflow_id, output_id)
                if not isinstance(output_node_id, str) or not output_node_id:
                    raise ValueError(f"{kind} output resolver returned an invalid node id")
                normalized["output_id"] = output_id
                normalized["output_node_id"] = output_node_id
            normalized_bindings.append(normalized)

        required_unbound_uploads = [
            _read(cell, "id")
            for cell in _read(block, "inputs", ())
            if str(_read(cell, "shape", "") or "").lower() == "upload"
            and bool(_read(cell, "required", True))
            and _read(cell, "id") not in target_ids
        ]
        if required_unbound_uploads:
            raise ValueError(
                f"stage '{stage_id}' must bind required upload input(s): "
                + ", ".join(str(value) for value in required_unbound_uploads)
            )

        normalized_stages.append(
            {
                "id": stage_id,
                "workflow_id": workflow_id,
                "defaults": defaults,
                "bindings": normalized_bindings,
                "status": "pending",
                "child_submission_id": None,
                "child_request_fingerprint": None,
                "child_run_id": None,
                "error": None,
            }
        )

    raw_final_output_ids = _read(definition, "final_output_ids", None)
    if raw_final_output_ids is None:
        # Structural embedders predating WorkflowSequenceNode remain useful in
        # focused tests. Registered public declarations always provide this
        # field and therefore always receive strict output projection.
        final_outputs = None
    else:
        if isinstance(raw_final_output_ids, (str, bytes)):
            raise TypeError("sequence final output ids must be a sequence")
        final_outputs = []
        for raw_output_id in raw_final_output_ids:
            output_id = _bounded_id(raw_output_id, "sequence final output id")
            output_node_id = resolve_output(
                normalized_stages[-1]["workflow_id"], output_id
            )
            if not isinstance(output_node_id, str) or not output_node_id:
                raise ValueError("final output resolver returned an invalid node id")
            final_outputs.append(
                {"output_id": output_id, "output_node_id": output_node_id}
            )
    plan_authority = {
        "sequence_id": sequence_id,
        "inputs": normalized_inputs,
        "final_outputs": final_outputs,
        "stages": [
            {
                "id": stage["id"],
                "workflow_id": stage["workflow_id"],
                "defaults": stage["defaults"],
                "bindings": stage["bindings"],
            }
            for stage in normalized_stages
        ],
    }
    fingerprint = hashlib.sha256(
        json.dumps(
            plan_authority,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return {
        "schema": sequence_store.SEQUENCE_STATE_SCHEMA,
        "sequence_id": sequence_id,
        "definition_fingerprint": fingerprint,
        "status": "pending",
        "current_stage": 0,
        "cancel_requested": False,
        "cancel_dispatched": False,
        "terminal_child_run_id": None,
        "error": None,
        "error_detail": None,
        "inputs": normalized_inputs,
        "final_outputs": final_outputs,
        "stages": normalized_stages,
    }


def _state_snapshot(record: sequence_store.SequenceStateRecord) -> dict[str, Any]:
    snapshot = deepcopy(record.state)
    snapshot.update(
        {
            "parent_run_id": record.parent_run_id,
            "owner_id": record.owner_id,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "seq": record.seq,
        }
    )
    return snapshot


async def get_sequence_execution(parent_run_id: str) -> dict[str, Any] | None:
    record = await sequence_store.get_state(parent_run_id)
    return _state_snapshot(record) if record is not None else None


async def _ensure_parent_job(
    record: sequence_store.SequenceStateRecord,
) -> sequence_store.SequenceStateRecord:
    if record.status == "pending":
        state = record.state
        state["status"] = "running"
        record = await sequence_store.save_state(record.parent_run_id, state)
    parent = await job_store.get_job(record.parent_run_id)
    if parent is None:
        parent = await job_store.create_job(
            record.parent_run_id,
            record.sequence_id,
            owner_id=record.owner_id,
            inputs=record.state.get("inputs", {}),
        )
    if parent.workflow_id != record.sequence_id or parent.owner_id != record.owner_id:
        raise ValueError("parent run id is already bound to another job")
    if record.status in sequence_store.ACTIVE_SEQUENCE_STATUSES:
        parent_status = _job_status(parent)
        if parent_status in _TERMINAL_STATUSES:
            # Public terminal publication intentionally happens before the
            # private state commit. A hard stop in that small interval must
            # adopt the already-published truth, never resume more stages.
            state = record.state
            state["status"] = parent_status
            state["error"] = getattr(parent, "error", None)
            state["error_detail"] = "sequence_parent_terminal_recovery"
            if parent_status == "succeeded":
                state["current_stage"] = len(state.get("stages", ()))
            return await sequence_store.save_state(record.parent_run_id, state)
        if parent.status == JobStatus.PENDING:
            await job_store.set_job_status(record.parent_run_id, JobStatus.RUNNING)
        from .lifecycle import record_running

        await record_running(record.parent_run_id)
    return record


def _job_status(job: Any) -> str:
    value = getattr(job, "status", "")
    return str(getattr(value, "value", value) or "")


def _validate_child_job(
    job: Any,
    stage: Mapping[str, Any],
    owner_id: str | None,
) -> None:
    if (
        getattr(job, "workflow_id", None) != stage.get("workflow_id")
        or getattr(job, "owner_id", None) != owner_id
        or getattr(job, "submission_id", None)
        != stage.get("child_submission_id")
        or getattr(job, "request_fingerprint", None)
        != stage.get("child_request_fingerprint")
    ):
        raise SequenceExecutionError(
            "sequence_child_authority_mismatch",
            f"stage '{stage.get('id')}' child authority does not match its durable plan",
        )


def _stage_for_child_run_id(
    state: Mapping[str, Any], child_run_id: str
) -> Mapping[str, Any] | None:
    matches = [
        stage
        for stage in state.get("stages", ())
        if isinstance(stage, Mapping) and stage.get("child_run_id") == child_run_id
    ]
    return matches[0] if len(matches) == 1 else None


def _child_request_fingerprint(
    workflow_id: str,
    inputs: Mapping[str, Any],
) -> str:
    # Keep this byte-for-byte aligned with lifecycle._fingerprint_payload for
    # the exact child payload emitted below. The stable submission id itself
    # is intentionally excluded from lifecycle request identity.
    canonical_payload = {"inputs": inputs, "workflowId": workflow_id}
    encoded = json.dumps(
        canonical_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _project_final_child_result(state: Mapping[str, Any], result: Any) -> Any:
    """Keep the ordinary result envelope while exposing declared outputs only."""

    final_outputs = state.get("final_outputs")
    if final_outputs is None:
        return deepcopy(result)
    if not isinstance(final_outputs, list) or not final_outputs:
        raise SequenceExecutionError(
            "sequence_output_missing",
            "the sequence declares no final outputs",
        )
    node_ids = list(
        dict.fromkeys(str(item.get("output_node_id") or "") for item in final_outputs)
    )
    if not all(node_ids):
        raise SequenceExecutionError(
            "sequence_output_missing",
            "the sequence final-output plan is malformed",
        )
    projected = deepcopy(result)
    body = projected.get("body") if isinstance(projected, Mapping) else None
    payload = body.get("payload") if isinstance(body, Mapping) else None
    history = payload.get("history") if isinstance(payload, Mapping) else None
    outputs = history.get("outputs") if isinstance(history, Mapping) else None
    if not isinstance(outputs, Mapping):
        raise SequenceExecutionError(
            "sequence_output_missing",
            "the final stage returned no output map",
        )
    missing = [node_id for node_id in node_ids if node_id not in outputs]
    if missing:
        raise SequenceExecutionError(
            "sequence_output_missing",
            "the final stage did not produce declared output node(s): "
            + ", ".join(missing),
        )
    history["outputs"] = {node_id: deepcopy(outputs[node_id]) for node_id in node_ids}
    preferred_output = payload.get("preferred_output")
    if preferred_output is not None and str(preferred_output) not in node_ids:
        payload["preferred_output"] = node_ids[0]
    return projected


def _project_unsuccessful_child_result(
    state: Mapping[str, Any],
    result: Any,
    source_stage: Mapping[str, Any],
) -> Any:
    """Preserve failure diagnostics without publishing private stage outputs."""

    final_outputs = state.get("final_outputs")
    if final_outputs is None:
        # Structural embedders without a declared public-output contract retain
        # their legacy projection. Registered sequences always declare it.
        return deepcopy(result)

    projected = deepcopy(result)
    body = projected.get("body") if isinstance(projected, Mapping) else None
    payload = body.get("payload") if isinstance(body, Mapping) else None
    history = payload.get("history") if isinstance(payload, Mapping) else None
    outputs = history.get("outputs") if isinstance(history, Mapping) else None
    if not isinstance(outputs, Mapping):
        return projected

    stages = state.get("stages")
    source_is_final_stage = (
        isinstance(stages, (list, tuple))
        and bool(stages)
        and source_stage is stages[-1]
    )
    allowed_node_ids: list[str] = []
    if source_is_final_stage and isinstance(final_outputs, list):
        allowed_node_ids = list(
            dict.fromkeys(
                str(item.get("output_node_id") or "")
                for item in final_outputs
                if isinstance(item, Mapping)
                and isinstance(item.get("output_node_id"), str)
                and item.get("output_node_id")
            )
        )

    projected_outputs = {
        node_id: deepcopy(outputs[node_id])
        for node_id in allowed_node_ids
        if node_id in outputs
    }
    history["outputs"] = projected_outputs
    preferred_output = payload.get("preferred_output")
    if preferred_output is not None and str(preferred_output) not in projected_outputs:
        if projected_outputs:
            payload["preferred_output"] = next(iter(projected_outputs))
        else:
            payload.pop("preferred_output", None)
    return projected


async def _project_parent_terminal(
    record: sequence_store.SequenceStateRecord,
    *,
    status_override: str | None = None,
    child_run_id_override: str | None = None,
    error_override: str | None = None,
) -> None:
    state = record.state
    status = status_override or str(state["status"])
    if status not in _TERMINAL_STATUSES:
        return
    run_id = child_run_id_override or state.get("terminal_child_run_id")
    child = await job_store.get_job(run_id) if isinstance(run_id, str) else None
    parent = await job_store.get_job(record.parent_run_id)
    if child is not None:
        source_stage = _stage_for_child_run_id(state, str(run_id))
        if source_stage is None:
            raise SequenceExecutionError(
                "sequence_child_authority_mismatch",
                "the terminal child is not owned by a unique sequence stage",
            )
        _validate_child_job(child, source_stage, record.owner_id)
        child_result = getattr(child, "result", None)
        result = (
            _project_final_child_result(state, child_result)
            if status == "succeeded"
            else _project_unsuccessful_child_result(
                state,
                child_result,
                source_stage,
            )
        )
    elif run_id is None and status in {"failed", "cancelled", "timeout"}:
        result = None
    elif parent is not None and _job_status(parent) == status:
        # History cleanup may remove private child plumbing after the public
        # parent became authoritative. Never erase that durable projection.
        result = getattr(parent, "result", None)
    else:
        raise SequenceExecutionError(
            "sequence_terminal_projection_unavailable",
            "the terminal child result is no longer available for projection",
        )
    error = error_override if error_override is not None else state.get("error")
    normalized_error = error if isinstance(error, str) else None
    if (
        parent is None
        or _job_status(parent) != status
        or getattr(parent, "result", None) != result
        or getattr(parent, "error", None) != normalized_error
    ):
        await job_store.set_job_status(
            record.parent_run_id,
            JobStatus(status),
            result=result,
            error=normalized_error,
        )
    # A controller may bind the synthetic run to the ordinary stable
    # submission lifecycle before invoking this runtime. Publishing through
    # that same seam is a no-op for unbound/embedded callers and makes HTTP
    # replay, status, artifacts, and cancellation truthful when it is bound.
    from .lifecycle import record_terminal

    await record_terminal(
        record.parent_run_id,
        status,
        result=result,
        error=normalized_error,
    )


async def _save_and_project_terminal(
    record: sequence_store.SequenceStateRecord,
    state: dict[str, Any],
    status: str,
    *,
    child_run_id: str | None,
    error: str | None,
    error_detail: str | None = None,
) -> sequence_store.SequenceStateRecord:
    state["status"] = status
    state["terminal_child_run_id"] = child_run_id
    state["error"] = error[:2048] if isinstance(error, str) else None
    state["error_detail"] = (
        error_detail[:128] if isinstance(error_detail, str) else None
    )
    # Publish the durable public result first. If private state persistence is
    # interrupted, replay sees the still-active state and safely repeats this
    # idempotent projection from the canonical child row. The opposite order
    # could strand a terminal sequence whose result existed only in a pruned
    # hidden child.
    await _project_parent_terminal(
        record,
        status_override=status,
        child_run_id_override=child_run_id,
        error_override=state["error"],
    )
    return await sequence_store.save_state(record.parent_run_id, state)


async def _save_success_or_missing_output_failure(
    record: sequence_store.SequenceStateRecord,
    state: dict[str, Any],
    child_run_id: str | None,
) -> sequence_store.SequenceStateRecord:
    try:
        return await _save_and_project_terminal(
            record,
            state,
            "succeeded",
            child_run_id=child_run_id,
            error=None,
        )
    except SequenceExecutionError as exc:
        if exc.detail != "sequence_output_missing":
            raise
        return await _save_and_project_terminal(
            record,
            state,
            "failed",
            child_run_id=None,
            error=str(exc),
            error_detail=exc.detail,
        )


async def fail_sequence_execution(
    parent_run_id: str,
    *,
    error: str,
    error_detail: str = "sequence_supervisor_failed",
    child_canceller: ChildCanceller | None = None,
) -> dict[str, Any]:
    """Terminalize private and public authority after an unexpected failure."""

    lock = _locks.setdefault(parent_run_id, asyncio.Lock())
    async with lock:
        record = await sequence_store.get_state(parent_run_id)
        if record is None:
            raise KeyError(parent_run_id)
        if record.status in _TERMINAL_STATUSES:
            if await job_store.get_job(parent_run_id) is not None:
                await _project_parent_terminal(record)
            return _state_snapshot(record)
        record = await _ensure_parent_job(record)
        if record.status in _TERMINAL_STATUSES:
            return _state_snapshot(record)
        state = record.state
        stages = state.get("stages", ())
        stage_index = int(state.get("current_stage", 0) or 0)
        cleanup_stage: Mapping[str, Any] | None = None
        if isinstance(stages, list) and 0 <= stage_index < len(stages):
            stages[stage_index]["status"] = "failed"
            stages[stage_index]["error"] = str(error)[:2048]
            cleanup_stage = deepcopy(stages[stage_index])
        # An unexpected supervisor failure is not child terminal proof. Keep
        # any exact child authority in private state, but publish no guessed
        # child result through the failed public parent.
        record = await _save_and_project_terminal(
            record,
            state,
            "failed",
            child_run_id=None,
            error=str(error),
            error_detail=error_detail,
        )
        # Terminal truth must not depend on cancellation transport, but an
        # already-running exact child should not become invisible GPU work
        # merely because its supervisor crashed.  Cancel only after the
        # failed parent/private state is durable, validate the stored child
        # authority again, and keep any transport failure as diagnostic-only.
        submission_id = (
            cleanup_stage.get("child_submission_id")
            if cleanup_stage is not None
            else None
        )
        child_run_id = (
            cleanup_stage.get("child_run_id")
            if cleanup_stage is not None
            else None
        )
        if isinstance(submission_id, str) and isinstance(child_run_id, str):
            try:
                child = await job_store.get_job(child_run_id)
                if child is not None:
                    _validate_child_job(child, cleanup_stage, record.owner_id)
                    if _job_status(child) in _ACTIVE_CHILD_STATUSES:
                        canceller = child_canceller or _default_child_canceller
                        cancellation = await canceller(submission_id)
                        if not isinstance(cancellation, Mapping):
                            raise RuntimeError(
                                "child canceller returned an invalid response"
                            )
            except Exception:
                LOG.exception(
                    "Could not cancel exact child %s after sequence supervisor "
                    "failure for %s",
                    child_run_id,
                    parent_run_id,
                )
        return _state_snapshot(record)


def _artifact_reference(
    previous_run_id: str,
    previous_result: Any,
    output_node_id: str,
    output_id: str,
) -> dict[str, Any]:
    descriptors = project_public_output_artifacts(previous_run_id, previous_result)
    matches = [
        item
        for item in descriptors
        if item.get("nodeId") == output_node_id and item.get("available") is True
    ]
    if len(matches) != 1:
        reason = "missing" if not matches else "ambiguous"
        raise SequenceExecutionError(
            "sequence_artifact_unavailable",
            f"prior output '{output_id}' is {reason}; expected exactly one available artifact",
        )
    reference = matches[0].get("reference")
    if not isinstance(reference, Mapping):
        raise SequenceExecutionError(
            "sequence_artifact_unavailable",
            f"prior output '{output_id}' has no opaque artifact reference",
        )
    return deepcopy(dict(reference))


def _text_output(previous_result: Any, output_node_id: str, output_id: str) -> str:
    body = previous_result.get("body") if isinstance(previous_result, Mapping) else None
    payload = body.get("payload") if isinstance(body, Mapping) else None
    history = payload.get("history") if isinstance(payload, Mapping) else None
    outputs = history.get("outputs") if isinstance(history, Mapping) else None
    node_output = outputs.get(output_node_id) if isinstance(outputs, Mapping) else None
    items = node_output.get("lf_output") if isinstance(node_output, Mapping) else None
    if not isinstance(items, list) or not items:
        raise SequenceExecutionError(
            "sequence_text_unavailable",
            f"prior output '{output_id}' is missing; expected one durable text payload",
        )
    if len(items) != 1:
        raise SequenceExecutionError(
            "sequence_text_unavailable",
            f"prior output '{output_id}' is ambiguous; expected one durable text payload",
        )
    item = items[0]
    # DisplayString history uses `string`; authoring nodes use `value`.
    keys = [key for key in ("string", "value") if isinstance(item, Mapping) and key in item]
    if len(keys) != 1 or not isinstance(item[keys[0]], str):
        raise SequenceExecutionError(
            "sequence_text_unavailable",
            f"prior output '{output_id}' must contain exactly one string or value text field",
        )
    return item[keys[0]]


def sequence_stage_declared_inputs(
    state: Mapping[str, Any],
    stage_index: int,
) -> dict[str, Any]:
    """Return stage values known before any prior output is materialized."""

    stage = state["stages"][stage_index]
    inputs: dict[str, Any] = deepcopy(stage.get("defaults", {}))
    for binding in stage["bindings"]:
        target = binding["target_input_id"]
        if binding["kind"] == "public_input":
            inputs[target] = deepcopy(state["inputs"][binding["public_input_id"]])
        elif binding["kind"] == "literal":
            inputs[target] = deepcopy(binding["value"])
    return inputs


def sequence_stage_preflight_inputs(
    state: Mapping[str, Any], stage_index: int,
) -> dict[str, Any]:
    """Exercise portable graph configuration without submitting a placeholder."""

    inputs = sequence_stage_declared_inputs(state, stage_index)
    for binding in state["stages"][stage_index]["bindings"]:
        if binding["kind"] == "text":
            inputs[binding["target_input_id"]] = "Pending text from an earlier orchestra stage."
    return inputs


async def _stage_inputs(
    state: Mapping[str, Any],
    stage_index: int,
    owner_id: str | None,
) -> dict[str, Any]:
    stage = state["stages"][stage_index]
    inputs = sequence_stage_declared_inputs(state, stage_index)
    for binding in stage["bindings"]:
        kind = binding["kind"]
        if kind not in {"artifact", "text"}:
            continue
        target = binding["target_input_id"]
        source_stage_index = binding.get("source_stage_index")
        source_stage_id = binding.get("source_stage_id")
        if source_stage_index is None and source_stage_id is None:
            # Legacy v1 private plans contain neither field and retain the
            # original immediately-previous semantics.
            if stage_index <= 0:
                raise SequenceExecutionError(
                    f"sequence_{kind}_source_invalid",
                    f"stage '{stage.get('id')}' has no earlier {kind} source",
                )
            source_stage_index = stage_index - 1
        elif (
            type(source_stage_index) is not int
            or not isinstance(source_stage_id, str)
            or not source_stage_id
            or source_stage_index < 0
            or source_stage_index >= stage_index
        ):
            raise SequenceExecutionError(
                f"sequence_{kind}_source_invalid",
                f"stage '{stage.get('id')}' has malformed {kind} source authority",
            )

        source = state["stages"][source_stage_index]
        if source_stage_id is not None and source.get("id") != source_stage_id:
            raise SequenceExecutionError(
                f"sequence_{kind}_source_invalid",
                f"stage '{stage.get('id')}' {kind} source no longer matches "
                f"stage '{source_stage_id}'",
            )
        source_run_id = source.get("child_run_id")
        if not isinstance(source_run_id, str) or not source_run_id:
            raise SequenceExecutionError(
                f"sequence_{kind}_unavailable",
                f"source stage '{source.get('id')}' has no durable child run",
            )
        source_job = await job_store.get_job(source_run_id)
        if source_job is None or _job_status(source_job) != "succeeded":
            raise SequenceExecutionError(
                f"sequence_{kind}_unavailable",
                f"source stage '{source.get('id')}' result is no longer available",
            )
        _validate_child_job(source_job, source, owner_id)
        if kind == "text":
            inputs[target] = _text_output(
                source_job.result, binding["output_node_id"], binding["output_id"],
            )
        else:
            inputs[target] = _artifact_reference(
                source_run_id,
                source_job.result,
                binding["output_node_id"],
                binding["output_id"],
            )
    return inputs


async def create_sequence_execution(
    definition: Any,
    inputs: Mapping[str, Any],
    *,
    owner_id: str | None = None,
    parent_run_id: str | None = None,
    output_node_resolver: OutputNodeResolver | None = None,
    workflow_resolver: WorkflowResolver | None = None,
) -> dict[str, Any]:
    """Persist a sequence and create its one synthetic public parent job."""

    run_id = parent_run_id or make_sequence_parent_run_id()
    if not is_sequence_parent_run_id(run_id) or len(run_id) > 128:
        raise ValueError("sequence parent run id must use the lf-sequence: prefix")
    plan = normalize_sequence_definition(
        definition,
        inputs,
        output_node_resolver=output_node_resolver,
        workflow_resolver=workflow_resolver,
    )
    existing = await sequence_store.get_state(run_id)
    if existing is not None:
        if (
            existing.sequence_id != plan["sequence_id"]
            or existing.owner_id != owner_id
            or existing.state.get("definition_fingerprint")
            != plan["definition_fingerprint"]
        ):
            raise ValueError("parent run id is already bound to another sequence")
        if existing.status in _TERMINAL_STATUSES:
            if await job_store.get_job(run_id) is not None:
                await _project_parent_terminal(existing)
            return _state_snapshot(existing)
        existing = await _ensure_parent_job(existing)
        return _state_snapshot(existing)

    record = await sequence_store.create_state(
        run_id,
        plan["sequence_id"],
        owner_id=owner_id,
        state=plan,
    )
    record = await _ensure_parent_job(record)
    return _state_snapshot(record)


async def _default_child_runner(
    payload: Mapping[str, Any], *, owner_id: str | None
) -> Mapping[str, Any]:
    from .run_service import run_workflow

    return await run_workflow(
        dict(payload),
        owner_id=owner_id,
        _sequence_child=True,
    )


async def _default_child_canceller(submission_id: str) -> Mapping[str, Any]:
    from .run_service import cancel_workflow_submission

    return await cancel_workflow_submission(submission_id)


async def _invoke_runner(
    runner: ChildRunner,
    payload: Mapping[str, Any],
    owner_id: str | None,
) -> Mapping[str, Any]:
    result = runner(dict(payload), owner_id=owner_id)
    if isawaitable(result):
        result = await result
    if not isinstance(result, Mapping):
        raise RuntimeError("child runner returned an invalid response")
    return result


async def advance_sequence_execution(
    parent_run_id: str,
    *,
    child_runner: ChildRunner | None = None,
    child_canceller: ChildCanceller | None = None,
) -> dict[str, Any]:
    """Advance one sequence by at most one child lifecycle transition."""

    lock = _locks.setdefault(parent_run_id, asyncio.Lock())
    async with lock:
        record = await sequence_store.get_state(parent_run_id)
        if record is None:
            raise KeyError(parent_run_id)
        if record.status in _TERMINAL_STATUSES:
            if await job_store.get_job(parent_run_id) is not None:
                await _project_parent_terminal(record)
            return _state_snapshot(record)
        record = await _ensure_parent_job(record)
        state = record.state

        runner = child_runner or _default_child_runner
        canceller = child_canceller or _default_child_canceller
        stage_index = int(state["current_stage"])
        if stage_index >= len(state["stages"]):
            record = await _save_success_or_missing_output_failure(
                record, state, state["stages"][-1].get("child_run_id")
            )
            return _state_snapshot(record)
        stage = state["stages"][stage_index]

        if state.get("cancel_requested") and not stage.get("child_run_id"):
            stage["status"] = "cancelled"
            record = await _save_and_project_terminal(
                record,
                state,
                "cancelled",
                child_run_id=None,
                error="cancelled",
            )
            return _state_snapshot(record)

        stage_inputs: dict[str, Any] | None = None
        if not stage.get("child_run_id"):
            try:
                stage_inputs = await _stage_inputs(state, stage_index, record.owner_id)
            except Exception as exc:
                stage["status"] = "failed"
                stage["error"] = str(exc)[:2048]
                record = await _save_and_project_terminal(
                    record,
                    state,
                    "failed",
                    child_run_id=None,
                    error=f"stage '{stage['id']}' could not resolve its inputs: {exc}",
                    error_detail=(
                        exc.detail if isinstance(exc, SequenceExecutionError) else None
                    ),
                )
                return _state_snapshot(record)

        if stage["status"] == "pending":
            stage["child_submission_id"] = child_submission_id(
                parent_run_id, stage_index, stage["id"]
            )
            assert stage_inputs is not None
            stage["child_request_fingerprint"] = _child_request_fingerprint(
                stage["workflow_id"], stage_inputs
            )
            stage["status"] = "submitting"
            record = await sequence_store.save_state(parent_run_id, state)
            state = record.state
            stage = state["stages"][stage_index]

        if not stage.get("child_run_id"):
            assert stage_inputs is not None
            expected_fingerprint = _child_request_fingerprint(
                stage["workflow_id"], stage_inputs
            )
            stored_fingerprint = stage.get("child_request_fingerprint")
            if stored_fingerprint is None:
                stage["child_request_fingerprint"] = expected_fingerprint
                record = await sequence_store.save_state(parent_run_id, state)
                state = record.state
                stage = state["stages"][stage_index]
            elif stored_fingerprint != expected_fingerprint:
                stage["status"] = "failed"
                stage["error"] = "child request authority changed after persistence"
                record = await _save_and_project_terminal(
                    record,
                    state,
                    "failed",
                    child_run_id=None,
                    error=f"stage '{stage['id']}' child request authority changed",
                    error_detail="sequence_child_authority_mismatch",
                )
                return _state_snapshot(record)
            child_payload = {
                "workflowId": stage["workflow_id"],
                "inputs": stage_inputs,
                "submissionId": stage["child_submission_id"],
            }
            try:
                response = await _invoke_runner(runner, child_payload, record.owner_id)
            except Exception as exc:
                stage["status"] = "failed"
                stage["error"] = str(exc)[:2048]
                record = await _save_and_project_terminal(
                    record,
                    state,
                    "failed",
                    child_run_id=None,
                    error=f"stage '{stage['id']}' submission failed: {exc}",
                )
                return _state_snapshot(record)
            child_run_id = response.get("run_id")
            if not isinstance(child_run_id, str) or not child_run_id:
                stage["status"] = "failed"
                stage["error"] = "child submission did not bind a run id"
                record = await _save_and_project_terminal(
                    record,
                    state,
                    "failed",
                    child_run_id=None,
                    error=f"stage '{stage['id']}' did not bind a child run",
                )
                return _state_snapshot(record)
            stage["child_run_id"] = child_run_id
            stage["status"] = "running"
            record = await sequence_store.save_state(parent_run_id, state)
            state = record.state
            stage = state["stages"][stage_index]

        child_run_id = stage["child_run_id"]
        child = await job_store.get_job(child_run_id)
        if child is None:
            recovered = await job_store.get_job_by_submission_id(
                stage["child_submission_id"]
            )
            if recovered is not None and recovered.id == child_run_id:
                child = recovered
            else:
                parent = await job_store.get_job(parent_run_id)
                if (
                    stage_index + 1 >= len(state["stages"])
                    and parent is not None
                    and _job_status(parent) == "succeeded"
                ):
                    # Public-first terminal publication can survive both a
                    # private-state commit failure and later child pruning.
                    # That public result is already authoritative.
                    stage["status"] = "succeeded"
                    state["current_stage"] = len(state["stages"])
                    record = await _save_success_or_missing_output_failure(
                        record, state, child_run_id
                    )
                    return _state_snapshot(record)
                stage["status"] = "failed"
                stage["error"] = "durable child job disappeared"
                record = await _save_and_project_terminal(
                    record,
                    state,
                    "failed",
                    child_run_id=None,
                    error=f"stage '{stage['id']}' durable child job disappeared",
                    error_detail="sequence_child_missing",
                )
                return _state_snapshot(record)

        try:
            _validate_child_job(child, stage, record.owner_id)
        except SequenceExecutionError as exc:
            stage["status"] = "failed"
            stage["error"] = str(exc)
            record = await _save_and_project_terminal(
                record,
                state,
                "failed",
                child_run_id=None,
                error=str(exc),
                error_detail=exc.detail,
            )
            return _state_snapshot(record)

        child_status = _job_status(child)
        if state.get("cancel_requested") and child_status in _ACTIVE_CHILD_STATUSES:
            if not state.get("cancel_dispatched"):
                try:
                    cancel_snapshot = await canceller(stage["child_submission_id"])
                    if not isinstance(cancel_snapshot, Mapping):
                        raise RuntimeError("child canceller returned an invalid response")
                except Exception as exc:
                    # Cancellation transport is not terminal truth. Preserve
                    # the exact intent and active child authority so the
                    # supervisor retries while still observing a child that
                    # may independently finish.
                    stage["error"] = f"cancellation dispatch failed: {exc}"[:2048]
                    record = await sequence_store.save_state(parent_run_id, state)
                    return _state_snapshot(record)
                stage["error"] = None
                state["cancel_dispatched"] = True
                record = await sequence_store.save_state(parent_run_id, state)
            return _state_snapshot(record)
        if child_status in _ACTIVE_CHILD_STATUSES:
            if stage["status"] != child_status:
                stage["status"] = child_status
                record = await sequence_store.save_state(parent_run_id, state)
            return _state_snapshot(record)
        if child_status not in _TERMINAL_STATUSES:
            return _state_snapshot(record)

        stage["status"] = child_status
        stage["error"] = getattr(child, "error", None)
        if state.get("cancel_requested") and child_status == "cancelled":
            record = await _save_and_project_terminal(
                record,
                state,
                "cancelled",
                child_run_id=child_run_id,
                error="cancelled",
            )
            return _state_snapshot(record)
        if state.get("cancel_requested") and child_status == "succeeded":
            # Exact cancellation lost the race to a successful final stage.
            # Preserve that success; when stages remain, honour the sequence
            # cancellation by stopping cleanly before the next submission.
            if stage_index + 1 < len(state["stages"]):
                record = await _save_and_project_terminal(
                    record,
                    state,
                    "cancelled",
                    child_run_id=child_run_id,
                    error="cancelled",
                )
                return _state_snapshot(record)
            state["cancel_requested"] = False
            state["cancel_dispatched"] = False
        if child_status != "succeeded":
            error = getattr(child, "error", None) or (
                f"stage '{stage['id']}' ended with {child_status}"
            )
            record = await _save_and_project_terminal(
                record,
                state,
                child_status,
                child_run_id=child_run_id,
                error=str(error),
            )
            return _state_snapshot(record)

        state["current_stage"] = stage_index + 1
        if state["current_stage"] >= len(state["stages"]):
            record = await _save_success_or_missing_output_failure(
                record, state, child_run_id
            )
        else:
            record = await sequence_store.save_state(parent_run_id, state)
        return _state_snapshot(record)


async def drive_sequence_execution(
    parent_run_id: str,
    *,
    child_runner: ChildRunner | None = None,
    child_canceller: ChildCanceller | None = None,
    poll_interval: float = 0.25,
) -> dict[str, Any]:
    """Supervise one sequence until its public parent is terminal."""

    while True:
        snapshot = await advance_sequence_execution(
            parent_run_id,
            child_runner=child_runner,
            child_canceller=child_canceller,
        )
        if snapshot["status"] in _TERMINAL_STATUSES:
            return snapshot
        await asyncio.sleep(max(0.0, poll_interval))


async def _supervise_sequence_execution(
    parent_run_id: str,
    *,
    child_runner: ChildRunner | None,
    child_canceller: ChildCanceller | None,
    poll_interval: float,
) -> dict[str, Any]:
    """Contain an unexpected supervisor crash as an explicit failed run."""

    try:
        return await drive_sequence_execution(
            parent_run_id,
            child_runner=child_runner,
            child_canceller=child_canceller,
            poll_interval=poll_interval,
        )
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        LOG.exception("Workflow sequence supervisor failed for %s", parent_run_id)
        try:
            return await fail_sequence_execution(
                parent_run_id,
                error=str(exc) or type(exc).__name__,
                child_canceller=child_canceller,
            )
        except Exception:
            LOG.exception(
                "Could not terminalize failed workflow sequence %s",
                parent_run_id,
            )
            raise


def schedule_sequence_execution(
    parent_run_id: str,
    *,
    child_runner: ChildRunner | None = None,
    child_canceller: ChildCanceller | None = None,
    poll_interval: float = 0.25,
) -> asyncio.Task[dict[str, Any]]:
    existing = _supervisors.get(parent_run_id)
    if existing is not None and not existing.done():
        return existing
    task = asyncio.create_task(
        _supervise_sequence_execution(
            parent_run_id,
            child_runner=child_runner,
            child_canceller=child_canceller,
            poll_interval=poll_interval,
        )
    )
    _supervisors[parent_run_id] = task

    def forget(completed: asyncio.Task[dict[str, Any]]) -> None:
        if not completed.cancelled():
            # Retrieve a terminalization failure so asyncio does not reduce it
            # to an unowned "Task exception was never retrieved" warning. The
            # guarded supervisor has already logged the exact parent id.
            completed.exception()
        if _supervisors.get(parent_run_id) is completed:
            _supervisors.pop(parent_run_id, None)

    task.add_done_callback(forget)
    return task


async def start_sequence_execution(
    definition: Any,
    inputs: Mapping[str, Any],
    *,
    owner_id: str | None = None,
    parent_run_id: str | None = None,
    output_node_resolver: OutputNodeResolver | None = None,
    workflow_resolver: WorkflowResolver | None = None,
    child_runner: ChildRunner | None = None,
    child_canceller: ChildCanceller | None = None,
    poll_interval: float = 0.25,
) -> dict[str, Any]:
    snapshot = await create_sequence_execution(
        definition,
        inputs,
        owner_id=owner_id,
        parent_run_id=parent_run_id,
        output_node_resolver=output_node_resolver,
        workflow_resolver=workflow_resolver,
    )
    if snapshot["status"] not in _TERMINAL_STATUSES:
        schedule_sequence_execution(
            snapshot["parent_run_id"],
            child_runner=child_runner,
            child_canceller=child_canceller,
            poll_interval=poll_interval,
        )
    return snapshot


async def cancel_sequence_execution(
    parent_run_id: str,
    *,
    child_canceller: ChildCanceller | None = None,
) -> dict[str, Any]:
    """Target only the exact active child of one sequence parent."""

    lock = _locks.setdefault(parent_run_id, asyncio.Lock())
    async with lock:
        record = await sequence_store.get_state(parent_run_id)
        if record is None:
            raise KeyError(parent_run_id)
        state = record.state
        if state["status"] in _TERMINAL_STATUSES:
            if await job_store.get_job(parent_run_id) is not None:
                await _project_parent_terminal(record)
            return _state_snapshot(record)
        stage_index = int(state["current_stage"])
        stage = state["stages"][stage_index]
        submission_id = stage.get("child_submission_id")
        child_run_id = stage.get("child_run_id")
        if isinstance(submission_id, str) and not isinstance(child_run_id, str):
            # A restart can land after the deterministic child was durably
            # registered but before its prompt id reached private sequence
            # state. Recover that exact authority instead of manufacturing an
            # idle-parent cancellation around a possibly running prompt.
            recovered = await job_store.get_job_by_submission_id(submission_id)
            if recovered is None:
                raise SequenceExecutionError(
                    "sequence_child_not_bound",
                    "the active child has not reached a durably cancellable run",
                )
            _validate_child_job(recovered, stage, record.owner_id)
            child_run_id = recovered.id
            stage["child_run_id"] = child_run_id
            stage["status"] = _job_status(recovered) or "running"
            record = await sequence_store.save_state(parent_run_id, state)
            state = record.state
            stage = state["stages"][stage_index]

        if not isinstance(submission_id, str) or not isinstance(child_run_id, str):
            state["cancel_requested"] = True
            stage["status"] = "cancelled"
            record = await _save_and_project_terminal(
                record,
                state,
                "cancelled",
                child_run_id=None,
                error="cancelled",
            )
            return _state_snapshot(record)

        child = await job_store.get_job(child_run_id)
        if child is None:
            raise SequenceExecutionError(
                "sequence_child_missing",
                "the active child job is no longer available for exact cancellation",
            )
        _validate_child_job(child, stage, record.owner_id)

        canceller = child_canceller or _default_child_canceller
        state["cancel_requested"] = True
        record = await sequence_store.save_state(parent_run_id, state)
        try:
            cancel_snapshot = await canceller(submission_id)
            if not isinstance(cancel_snapshot, Mapping):
                raise RuntimeError("child canceller returned an invalid response")
        except Exception:
            state = record.state
            state["cancel_requested"] = False
            state["cancel_dispatched"] = False
            await sequence_store.save_state(parent_run_id, state)
            raise
        state = record.state
        cancellation_status = str(cancel_snapshot.get("status") or "")
        if cancellation_status in {"failed", "timeout"}:
            # Exact terminal truth beats a late cancellation request.
            state["cancel_requested"] = False
            state["cancel_dispatched"] = False
        elif cancellation_status == "succeeded" and stage_index + 1 >= len(
            state["stages"]
        ):
            # Nothing remains to stop: final-stage success won the race.
            state["cancel_requested"] = False
            state["cancel_dispatched"] = False
        else:
            state["cancel_dispatched"] = True
        record = await sequence_store.save_state(parent_run_id, state)
        return _state_snapshot(record)


async def resume_sequence_executions(
    *,
    child_runner: ChildRunner | None = None,
    child_canceller: ChildCanceller | None = None,
    poll_interval: float = 0.25,
) -> list[str]:
    """Repair public parents and resume every durable nonterminal sequence."""

    resumed: list[str] = []
    records = await sequence_store.list_states(active_only=False)
    records_by_parent = {record.parent_run_id: record for record in records}

    # A hard stop can land after the public parent was durably created but
    # before private sequence authority was committed. Such a parent cannot
    # be resumed safely; terminalize it explicitly instead of leaving an
    # immortal synthetic run that Core's reconciler correctly ignores.
    for parent_run_id, parent in (
        await job_store.list_jobs(owner_id=None, status=None)
    ).items():
        if (
            not is_sequence_parent_job(parent)
            or _job_status(parent) not in sequence_store.ACTIVE_SEQUENCE_STATUSES
            or parent_run_id in records_by_parent
        ):
            continue
        try:
            error = "Workflow sequence recovery state is unavailable."
            result = {
                "http_status": 500,
                "body": {
                    "message": error,
                    "payload": {
                        "detail": error,
                        "error": {"message": "sequence_state_missing"},
                        "history": {"outputs": {}},
                    },
                    "status": "error",
                },
            }
            await job_store.set_job_status(
                parent_run_id,
                JobStatus.FAILED,
                result=result,
                error="sequence_state_missing",
            )
            from .lifecycle import record_terminal

            await record_terminal(
                parent_run_id,
                "failed",
                result=result,
                error="sequence_state_missing",
            )
        except Exception:
            LOG.exception(
                "Could not terminalize orphaned workflow sequence %s",
                parent_run_id,
            )

    for record in records:
        try:
            if record.status in _TERMINAL_STATUSES:
                # A missing terminal parent was intentionally pruned from
                # public history. Private recovery state must never resurrect
                # it.
                if await job_store.get_job(record.parent_run_id) is None:
                    continue
                await _project_parent_terminal(record)
                continue
            record = await _ensure_parent_job(record)
            if record.status in _TERMINAL_STATUSES:
                continue
            schedule_sequence_execution(
                record.parent_run_id,
                child_runner=child_runner,
                child_canceller=child_canceller,
                poll_interval=poll_interval,
            )
            resumed.append(record.parent_run_id)
        except Exception:
            # One stale/corrupt private row must not prevent independent
            # sequences from recovering after process restart.
            LOG.exception(
                "Could not resume workflow sequence %s", record.parent_run_id
            )
    return resumed


async def delete_sequence_execution_state(parent_run_id: str) -> bool:
    """Remove terminal private authority and its exact hidden child rows."""

    if not is_sequence_parent_run_id(parent_run_id):
        return False
    lock = _locks.setdefault(parent_run_id, asyncio.Lock())
    async with lock:
        record = await sequence_store.get_state(parent_run_id)
        if (
            record is None
            or record.status not in _TERMINAL_STATUSES
            or await job_store.get_job(parent_run_id) is not None
        ):
            return False
        if not await _delete_terminal_sequence_children(record):
            return False
        deleted = await sequence_store.delete_state(parent_run_id)
    if deleted and _locks.get(parent_run_id) is lock:
        _locks.pop(parent_run_id, None)
    return deleted


async def _delete_terminal_sequence_children(record: Any) -> bool:
    """Delete only child rows whose full durable authority still matches."""

    seen_child_run_ids: set[str] = set()
    child_snapshots: list[tuple[str, Any, str]] = []
    stages = record.state.get("stages", ())
    if not isinstance(stages, list):
        return False
    for stage in stages:
        if not isinstance(stage, Mapping):
            return False
        child_run_id = stage.get("child_run_id")
        if not isinstance(child_run_id, str) or not child_run_id:
            continue
        if child_run_id in seen_child_run_ids:
            return False
        seen_child_run_ids.add(child_run_id)
        child = await job_store.get_job(child_run_id)
        if child is None:
            continue
        try:
            _validate_child_job(child, stage, record.owner_id)
        except SequenceExecutionError:
            LOG.exception(
                "Refusing to delete mismatched sequence child %s",
                child_run_id,
            )
            return False
        child_status = _job_status(child)
        if child_status not in _TERMINAL_STATUSES:
            return False
        child_snapshots.append((child_run_id, child, child_status))

    # Do not mutate any child row until the entire durable plan has proved
    # terminal and exact. A later active or mismatched stage must preserve all
    # earlier child history as well as the public parent.
    #
    # The store exposes per-row CAS rather than an atomic batch. If a later CAS
    # loses after an earlier row was removed, return False: the caller retains
    # the public parent and private plan, and a retry treats missing rows as an
    # already-completed portion of the same bounded cascade.
    for child_run_id, child, child_status in child_snapshots:
        removed = await job_store.hard_delete_job_if_unchanged(
            child_run_id,
            owner_id=getattr(child, "owner_id", None),
            status=child_status,
            seq=int(getattr(child, "seq", 0) or 0),
            updated_at=getattr(child, "updated_at", None),
        )
        if not removed and await job_store.get_job(child_run_id) is not None:
            return False
    return True


async def hard_delete_sequence_parent_if_unchanged(
    parent_run_id: str,
    *,
    owner_id: str | None,
    status: str,
    seq: int,
    updated_at: float | None,
) -> bool:
    """CAS-delete one terminal parent only after its private cascade succeeds.

    Private state is removed before the public history row so an active or
    mismatched child, a failed child CAS, or a failed state delete always leaves
    the user-visible parent available for diagnosis and retry. If the final
    parent CAS loses a race, restore the terminal state snapshot when possible;
    a missing state is also accepted on a later retry because it is the durable
    residue of a cascade that already completed.
    """

    if not is_sequence_parent_run_id(parent_run_id) or status not in _TERMINAL_STATUSES:
        return False
    lock = _locks.setdefault(parent_run_id, asyncio.Lock())
    removed = False
    async with lock:
        parent = await job_store.get_job(parent_run_id)
        if parent is None:
            return False
        if (
            getattr(parent, "owner_id", None) != owner_id
            or _job_status(parent) != status
            or int(getattr(parent, "seq", 0) or 0) != int(seq)
            or getattr(parent, "updated_at", None) != updated_at
        ):
            return False

        record = await sequence_store.get_state(parent_run_id)
        private_state_deleted = False
        if record is not None:
            if (
                record.status not in _TERMINAL_STATUSES
                or record.sequence_id != getattr(parent, "workflow_id", None)
                or record.owner_id != owner_id
            ):
                return False
            if not await _delete_terminal_sequence_children(record):
                return False
            private_state_deleted = await sequence_store.delete_state(parent_run_id)
            if not private_state_deleted:
                return False

        try:
            removed = await job_store.hard_delete_job_if_unchanged(
                parent_run_id,
                owner_id=owner_id,
                status=status,
                seq=seq,
                updated_at=updated_at,
            )
        except Exception:
            if private_state_deleted:
                await _restore_sequence_state_after_parent_cas(record)
            raise
        if not removed and await job_store.get_job(parent_run_id) is None:
            removed = True
        elif not removed and private_state_deleted:
            await _restore_sequence_state_after_parent_cas(record)

    if removed and _locks.get(parent_run_id) is lock:
        _locks.pop(parent_run_id, None)
    return removed


async def _restore_sequence_state_after_parent_cas(record: Any) -> None:
    """Best-effort rollback for a terminal parent that survived its CAS."""

    try:
        await sequence_store.create_state(
            record.parent_run_id,
            record.sequence_id,
            owner_id=record.owner_id,
            state=record.state,
        )
    except Exception:
        LOG.exception(
            "Could not restore private sequence state after parent cleanup race for %s",
            record.parent_run_id,
        )


async def stop_sequence_supervisors() -> None:
    tasks = list(_supervisors.values())
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    _supervisors.clear()
    _locks.clear()


__all__ = [
    "SEQUENCE_PARENT_RUN_PREFIX",
    "SequenceExecutionError",
    "advance_sequence_execution",
    "cancel_sequence_execution",
    "child_submission_id",
    "create_sequence_execution",
    "delete_sequence_execution_state",
    "drive_sequence_execution",
    "fail_sequence_execution",
    "get_sequence_execution",
    "hard_delete_sequence_parent_if_unchanged",
    "is_sequence_child_job",
    "is_sequence_child_submission_id",
    "is_sequence_parent_job",
    "is_sequence_parent_run_id",
    "make_sequence_parent_run_id",
    "normalize_sequence_definition",
    "resume_sequence_executions",
    "schedule_sequence_execution",
    "sequence_stage_declared_inputs",
    "start_sequence_execution",
    "stop_sequence_supervisors",
]
