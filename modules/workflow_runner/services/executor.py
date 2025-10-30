import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, Tuple, Optional

from aiohttp import web
from server import PromptServer

from ..config import CONFIG as RUNNER_CONFIG
from .job_store import JobStatus
from ..registry import InputValidationError, WorkflowNode, get_workflow, list_workflows
from ...utils.helpers.conversion import json_safe
import execution

class WorkflowPreparationError(Exception):
    """
    Raised when a workflow request fails basic preparation/validation before queueing.
    Carries the response body and HTTP status code to bubble the failure upstream.
    """

    def __init__(self, response_body: Dict[str, Any], status: int) -> None:
        super().__init__(response_body.get("detail") or "Workflow preparation failed.")
        self.response_body = response_body
        self.status = status

def _make_run_payload(
    *,
    detail: str = "",
    error_message: str | None = None,
    error_input: str | None = None,
    history: Dict[str, Any] | None = None,
    preferred_output: str | None = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"detail": detail or ""}
    if error_message is not None:
        payload["error"] = {"message": str(error_message)}
        if error_input:
            payload["error"]["input"] = str(error_input)

    payload["history"] = history or {"outputs": {}}
    if preferred_output is not None:
        payload["preferred_output"] = preferred_output

    return {"message": detail or "", "payload": payload, "status": "error" if error_message else "ready"}

def _sanitize_history(entry: Dict[str, Any]) -> Dict[str, Any]:
    outputs = entry.get("outputs", {}) or {}
    safe_outputs = {}
    for node_id, node_out in outputs.items():
        try:
            safe_outputs[str(node_id)] = json_safe(node_out)
        except Exception:
            safe_outputs[str(node_id)] = node_out

    return {
        "status": json_safe(entry.get("status")),
        "outputs": json_safe(safe_outputs),
        "prompt": json_safe(entry.get("prompt")),
    }

async def _wait_for_completion(prompt_id: str, timeout_seconds: float | None = None) -> Dict[str, Any]:
    queue = PromptServer.instance.prompt_queue
    start = time.perf_counter()
    deadline = start + timeout_seconds if timeout_seconds and timeout_seconds > 0 else None

    while True:
        history = queue.get_history(prompt_id=prompt_id)
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status") or {}
            if status.get("completed") is True or status.get("status_str") == "error":
                return entry
            if entry.get("outputs"):
                return entry

        if deadline is not None and time.perf_counter() >= deadline:
            raise TimeoutError(f"Prompt {prompt_id} did not finish within {timeout_seconds} seconds.")

        await asyncio.sleep(0.35)

def _prepare_workflow_execution(payload: Dict[str, Any]) -> Tuple[WorkflowNode, Dict[str, Any]]:
    inputs = payload.get("inputs", {})
    if not isinstance(inputs, dict):
        response = _make_run_payload(detail="inputs must be an object", error_message="invalid_inputs")
        raise WorkflowPreparationError(response, 400)

    workflow_id = payload.get("workflowId")
    definition = get_workflow(workflow_id or "")
    if definition is None:
        response = _make_run_payload(detail=f"No workflow found for id '{workflow_id}'.", error_message="unknown_workflow")
        raise WorkflowPreparationError(response, 404)

    try:
        prompt = definition.load_prompt()
        definition.configure_prompt(prompt, inputs)
    except FileNotFoundError as exc:
        response = _make_run_payload(detail=str(exc), error_message="missing_source")
        raise WorkflowPreparationError(response, 400) from exc
    except InputValidationError as exc:
        response = _make_run_payload(detail=str(exc), error_message="invalid_input", error_input=getattr(exc, "input_name", None))
        raise WorkflowPreparationError(response, 400) from exc
    except ValueError as exc:
        response = _make_run_payload(detail=str(exc), error_message="invalid_input")
        raise WorkflowPreparationError(response, 400) from exc
    except Exception as exc:
        logging.exception("Failed to prepare workflow '%s': %s", workflow_id, exc)
        response = _make_run_payload(detail=str(exc), error_message="configuration_failed")
        raise WorkflowPreparationError(response, 500) from exc

    return definition, prompt

async def execute_workflow(
    payload: Dict[str, Any], run_id: str, prepared: Tuple[WorkflowNode, Dict[str, Any]] | None = None
) -> Tuple[JobStatus, Dict[str, Any], int]:
    try:
        _, prompt = prepared or _prepare_workflow_execution(payload)
    except WorkflowPreparationError as exc:
        return JobStatus.FAILED, exc.response_body, exc.status

    workflow_id = payload.get("workflowId")

    prompt_id = payload.get("promptId") or uuid.uuid4().hex
    validation = await execution.validate_prompt(prompt_id, prompt, None)
    if not validation[0]:
        response = _make_run_payload(detail=validation[1], error_message="validation_failed", history={"outputs": {}, "node_errors": json_safe(validation[3])})
        return JobStatus.FAILED, response, 400

    server = PromptServer.instance
    queue_number = server.number
    server.number += 1

    extra_data = {"lf_nodes": {"workflow_id": workflow_id, "run_id": run_id}}
    extra_data.update(payload.get("extraData", {}))

    server.prompt_queue.put((queue_number, prompt_id, prompt, extra_data, validation[2]))

    try:
        history_entry = await _wait_for_completion(prompt_id, RUNNER_CONFIG.prompt_timeout_seconds)
    except TimeoutError as exc:
        response = _make_run_payload(detail=str(exc), error_message="timeout")
        return JobStatus.FAILED, response, 504

    status = history_entry.get("status") or {}
    status_str = status.get("status_str", "unknown")
    http_status = 200 if status_str == "success" else 500

    preferred_output = None
    try:
        outputs_in_history = set((history_entry.get("outputs") or {}).keys())
        validated_outputs = (validation[2] if isinstance(validation, (list, tuple)) and len(validation) > 2 else [])
        for output_name in validated_outputs:
            if output_name in outputs_in_history:
                preferred_output = output_name
                break
        if preferred_output is None:
            for output_name, output_value in (history_entry.get("outputs") or {}).items():
                try:
                    if isinstance(output_value, dict) and (output_value.get("images") or output_value.get("lf_images")):
                        preferred_output = output_name
                        break
                except Exception:
                    continue
    except Exception:
        preferred_output = None

    sanitized = _sanitize_history(history_entry)
    history_outputs = sanitized.get("outputs", {}) if isinstance(sanitized, dict) else {}
    if status_str == "success":
        response = _make_run_payload(detail="success", history={"outputs": history_outputs}, preferred_output=preferred_output)
        return JobStatus.SUCCEEDED, response, http_status

    response = _make_run_payload(detail=status_str or "error", error_message="execution_failed", history={"outputs": history_outputs}, preferred_output=preferred_output)
    return JobStatus.FAILED, response, http_status

__all__ = [
    "execute_workflow",
    "_make_run_payload",
    "_prepare_workflow_execution",
    "_sanitize_history",
    "_wait_for_completion",
    "WorkflowPreparationError",
]
