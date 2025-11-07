import aiohttp
import asyncio
import execution
import json
import logging
import time
import uuid

from typing import Any, Dict, Tuple

from .job_store import JobStatus, set_job_status
from .registry import InputValidationError, WorkflowNode, get_workflow
from ..config import CONFIG as RUNNER_CONFIG, get_settings
from ...utils.helpers.conversion import json_safe

# region Exceptions
class WorkflowPreparationError(Exception):
    """
    Raised when a workflow request fails basic preparation/validation before queueing.
    Carries the response body and HTTP status code to bubble the failure upstream.
    """
    def __init__(self, response_body: Dict[str, Any], status: int) -> None:
        super().__init__(response_body.get("detail") or "Workflow preparation failed.")
        self.response_body = response_body
        self.status = status
# endregion

# region Helpers
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

async def _wait_for_completion(prompt_id: str, timeout_seconds: float | None = None, comfy_url: str = "http://127.0.0.1:8188", session: aiohttp.ClientSession | None = None) -> Dict[str, Any]:
    """
    Asynchronously waits for the completion of a prompt execution identified by the given prompt_id.
    This function polls ComfyUI's history API at regular intervals until the prompt is either
    completed successfully, encounters an error, or produces outputs. If a timeout is specified,
    it will raise a TimeoutError if the prompt does not finish within the allotted time.

    Args:
        prompt_id (str): The unique identifier of the prompt to wait for.
        timeout_seconds (float | None, optional): The maximum time in seconds to wait for completion.
            If None or 0, waits indefinitely. Defaults to None.

    Returns:
        Dict[str, Any]: The history entry for the prompt, containing status and outputs.

    Raises:
        TimeoutError: If the prompt does not complete within the specified timeout_seconds.
    """
    start = time.perf_counter()
    deadline = start + timeout_seconds if timeout_seconds and timeout_seconds > 0 else None

    # Use provided session or create a new one
    session_to_use = session
    should_close_session = session_to_use is None
    if session_to_use is None:
        session_to_use = aiohttp.ClientSession()

    try:
        while True:
            try:
                async with session_to_use.get(f"{comfy_url}/history/{prompt_id}") as resp:
                    resp.raise_for_status()
                    history = await resp.json()

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

            except aiohttp.ClientError as exc:
                logging.warning("Failed to poll history for prompt %s: %s", prompt_id, exc)
                if deadline is not None and time.perf_counter() >= deadline:
                    raise TimeoutError(f"Prompt {prompt_id} did not finish within {timeout_seconds} seconds.")
                await asyncio.sleep(0.35)
    finally:
        if should_close_session and session_to_use:
            await session_to_use.close()

async def _monitor_execution_state(prompt_id: str, run_id: str, comfy_url: str = "http://127.0.0.1:8188", session: aiohttp.ClientSession | None = None) -> None:
    """
    Monitor execution state and update job status appropriately.

    Since we're using the HTTP API, we can't directly check queue state.
    Instead, we poll the history API to see if the prompt has started executing.

    Args:
        prompt_id (str): The unique identifier of the prompt to monitor.
        run_id (str): The unique identifier of the run associated with the prompt.
    """
    try:
        # Give ComfyUI a moment to start processing the prompt
        await asyncio.sleep(0.5)

        # Use provided session or create a new one
        session_to_use = session
        should_close_session = session_to_use is None
        if session_to_use is None:
            session_to_use = aiohttp.ClientSession()

        try:
            # Check if the prompt appears in history (meaning it started)
            async with session_to_use.get(f"{comfy_url}/history/{prompt_id}") as resp:
                if resp.status == 200:
                    history = await resp.json()
                    if prompt_id in history:
                        # Prompt has started (it's in history)
                        try:
                            await set_job_status(run_id, JobStatus.RUNNING)
                            logging.info("Run %s: marked RUNNING (found in history)", run_id)
                        except Exception:
                            logging.exception("Failed to set job RUNNING for %s", run_id)
                    else:
                        # Prompt not in history yet, assume it's queued
                        logging.debug("Run %s: prompt not yet in history, assuming queued", run_id)
                else:
                    logging.warning("Failed to check history for prompt %s: HTTP %d", prompt_id, resp.status)
        finally:
            if should_close_session and session_to_use:
                await session_to_use.close()

    except Exception:
        logging.exception("Error monitoring execution state for run %s", run_id)
# endregion

# region Execution
async def execute_workflow(
    payload: Dict[str, Any], run_id: str, prepared: Tuple[WorkflowNode, Dict[str, Any]] | None = None
) -> Tuple[JobStatus, Dict[str, Any], int]:
    settings = get_settings()
    comfy_url = settings.COMFY_BACKEND_URL
    try:
        _, prompt = prepared or _prepare_workflow_execution(payload)
    except WorkflowPreparationError as exc:
        return JobStatus.FAILED, exc.response_body, exc.status

    workflow_id = payload.get("workflowId")
    client_id = payload.get("clientId") or uuid.uuid4().hex
    # Don't generate prompt_id here - ComfyUI will provide it
    try:
        validation = await execution.validate_prompt(uuid.uuid4().hex, prompt, None)
    except Exception as exc:
        logging.warning("Local validate_prompt failed: %s (continuing)", exc)
        validation = (True, "", [], [])  # Use temp ID for validation
    if not validation[0]:
        response = _make_run_payload(detail=validation[1], error_message="validation_failed", history={"outputs": {}, "node_errors": json_safe(validation[3])})
        return JobStatus.FAILED, response, 400

    # Use ComfyUI's public HTTP API instead of manipulating internal queue
    extra_data = {"lf_nodes": {"workflow_id": workflow_id, "run_id": run_id}}
    extra_data.update(payload.get("extraData", {}))

    body = {
        "prompt": prompt,
        "client_id": client_id,
        "extra_data": extra_data
    }

    # Use single session for all HTTP operations
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{comfy_url}/prompt",
                headers={"Content-Type": "application/json"},
                data=json.dumps(body)
            ) as resp:
                resp.raise_for_status()
                prompt_data = await resp.json()
                prompt_id = prompt_data["prompt_id"]  # Use the prompt_id returned by ComfyUI
        except Exception as exc:
            logging.exception("Failed to submit prompt to ComfyUI API: %s", exc)
            response = _make_run_payload(detail=f"Failed to queue prompt: {exc}", error_message="queue_failed")
            return JobStatus.FAILED, response, 500

        # Mark as PENDING immediately after successful submission
        await set_job_status(run_id, JobStatus.PENDING)

        # Monitor execution state and update job status accordingly
        await _monitor_execution_state(prompt_id, run_id, comfy_url, session)

        try:
            history_entry = await _wait_for_completion(prompt_id, RUNNER_CONFIG.prompt_timeout_seconds, comfy_url, session)
        except TimeoutError as exc:
            # Try to interrupt the run cleanly
            try:
                async with session.post(
                    f"{comfy_url}/interrupt",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"client_id": client_id})
                ) as interrupt_resp:
                    if interrupt_resp.status < 400:
                        logging.info("Successfully interrupted run %s", run_id)
            except Exception as interrupt_exc:
                logging.warning("Failed to interrupt run %s: %s", run_id, interrupt_exc)

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
# endregion

__all__ = [
    "execute_workflow",
    "_make_run_payload",
    "_prepare_workflow_execution",
    "_sanitize_history",
    "_wait_for_completion",
    "WorkflowPreparationError",
]
