import aiohttp
import asyncio
import contextlib
import execution
import json
import logging
import time
import uuid
import os
import sys

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
    # Fast-mode gating: drastically reduce sleeps & cap iterations when LF_RUNNER_TEST_FAST=1
    fast_mode = os.getenv("LF_RUNNER_TEST_FAST") == "1"
    poll_sleep = 0.01 if fast_mode else 0.35
    max_fast_iterations = 50 if fast_mode else None

    effective_timeout = timeout_seconds
    if (timeout_seconds is None or timeout_seconds == 0):
        if fast_mode:
            # In fast-mode convert infinite waits to a short bounded timeout
            effective_timeout = 1.0
        elif "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
            effective_timeout = 5.0  # short cap for non fast-mode test scenarios
    deadline = start + effective_timeout if effective_timeout and effective_timeout > 0 else None

    session_to_use = session
    should_close_session = session_to_use is None
    if session_to_use is None:
        session_to_use = aiohttp.ClientSession()

    try:
        iteration = 0
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

                if deadline is None and ("PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules):
                    if time.perf_counter() - start > 10.0:
                        raise TimeoutError(f"Prompt {prompt_id} exceeded max test poll duration.")

                iteration += 1
                if max_fast_iterations is not None and iteration >= max_fast_iterations:
                    raise TimeoutError(f"Prompt {prompt_id} exceeded fast-mode max poll iterations ({max_fast_iterations}).")
                await asyncio.sleep(poll_sleep)

            except aiohttp.ClientError as exc:
                logging.warning("Failed to poll history for prompt %s: %s", prompt_id, exc)
                if deadline is not None and time.perf_counter() >= deadline:
                    raise TimeoutError(f"Prompt {prompt_id} did not finish within {timeout_seconds} seconds.")
                # Safety: abort if stuck polling too long in test even without explicit timeout
                if deadline is None and ("PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules):
                    if time.perf_counter() - start > 10.0:
                        raise TimeoutError(f"Prompt {prompt_id} exceeded max test poll duration.")
                iteration += 1
                if max_fast_iterations is not None and iteration >= max_fast_iterations:
                    raise TimeoutError(f"Prompt {prompt_id} exceeded fast-mode max poll iterations ({max_fast_iterations}).")
                await asyncio.sleep(poll_sleep)
    finally:
        if should_close_session and session_to_use:
            await session_to_use.close()

async def _monitor_until_running(
    prompt_id: str,
    stop_event: asyncio.Event,
    *,
    comfy_url: str = "http://127.0.0.1:8188",
    session: aiohttp.ClientSession | None = None,
) -> None:
    """Continuously poll the /queue to mark RUNNING as soon as it starts.

    Intended to run concurrently with waiting for completion; exits when either
    RUNNING is set or stop_event is signaled (completion/cancellation).
    """
    try:
        session_to_use = session
        should_close = session_to_use is None
        if session_to_use is None:
            session_to_use = aiohttp.ClientSession()
        try:
            fast_mode = os.getenv("LF_RUNNER_TEST_FAST") == "1"
            poll_sleep = 0.01 if fast_mode else 0.5
            max_fast_iterations = 50 if fast_mode else None
            iteration = 0
            while not stop_event.is_set():
                try:
                    async with session_to_use.get(f"{comfy_url}/queue") as resp:
                        if resp.status == 200:
                            q = await resp.json()
                            running = q.get("queue_running", [])
                            pending = q.get("queue_pending", [])
                            for item in running:
                                if isinstance(item, list) and len(item) >= 2 and item[1] == prompt_id:
                                    with contextlib.suppress(Exception):
                                        await set_job_status(prompt_id, JobStatus.RUNNING)
                                    return
                            if not any(isinstance(it, list) and len(it) >= 2 and it[1] == prompt_id for it in pending):
                                # not found anywhere; stop monitoring
                                return
                except aiohttp.ClientError:
                    # transient issue; retry
                    pass
                iteration += 1
                if max_fast_iterations is not None and iteration >= max_fast_iterations:
                    # In fast mode, avoid leaking background tasks that spin forever
                    return
                await asyncio.sleep(poll_sleep)
        finally:
            if should_close and session_to_use:
                await session_to_use.close()
    except asyncio.CancelledError:
        raise
    except Exception:
        logging.exception("monitor_until_running error for %s", prompt_id)
# endregion

# region Execution
async def submit_workflow(
    payload: Dict[str, Any], prepared: Tuple[WorkflowNode, Dict[str, Any]] | None = None
) -> Tuple[str, str, str, Dict[str, Any], Tuple[Any, ...], str]:
    """Prepare, validate and submit a workflow returning lightweight context.

    Returns:
        (prompt_id, client_id, comfy_url, prompt_dict, validation_tuple, workflow_id)

    Raises:
        WorkflowPreparationError for preparation failures.
    """
    settings = get_settings()
    comfy_url = settings.COMFY_BACKEND_URL

    definition, prompt = prepared or _prepare_workflow_execution(payload)
    workflow_id = payload.get("workflowId")
    client_id = payload.get("clientId") or uuid.uuid4().hex

    # Local validation (non-fatal if it crashes)
    try:
        validation = await execution.validate_prompt(uuid.uuid4().hex, prompt, None)
    except Exception as exc:
        logging.warning("Local validate_prompt failed: %s (continuing)", exc)
        validation = (True, "", [], [])
    if not validation[0]:
        response = _make_run_payload(detail=validation[1], error_message="validation_failed", history={"outputs": {}, "node_errors": json_safe(validation[3])})
        raise WorkflowPreparationError(response, 400)

    extra_data = {"lf_nodes": {"workflow_id": workflow_id}}
    extra_data.update(payload.get("extraData", {}))
    body = {"prompt": prompt, "client_id": client_id, "extra_data": extra_data}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{comfy_url}/prompt",
                headers={"Content-Type": "application/json"},
                data=json.dumps(body)
            ) as resp:
                resp.raise_for_status()
                prompt_data = await resp.json()
                prompt_id = prompt_data["prompt_id"]
        except Exception as exc:
            logging.exception("Failed to submit prompt to ComfyUI API: %s", exc)
            response = _make_run_payload(detail=f"Failed to queue prompt: {exc}", error_message="queue_failed")
            raise WorkflowPreparationError(response, 500)
    return prompt_id, client_id, comfy_url, prompt, validation, workflow_id

async def finalize_workflow(
    prompt_id: str,
    client_id: str,
    comfy_url: str,
    validation: Tuple[Any, ...],
) -> Tuple[JobStatus, Dict[str, Any], int]:
    """
    Asynchronously finalizes a workflow execution by monitoring its state, waiting for completion,
    and processing the results. Handles timeouts by attempting to interrupt the execution.

    Args:
        prompt_id (str): The unique identifier for the prompt being executed.
        client_id (str): The client identifier associated with the execution.
        comfy_url (str): The base URL of the ComfyUI server.
        validation (Tuple[Any, ...]): A tuple containing validation data, potentially including
            validated output names.

    Returns:
        Tuple[JobStatus, Dict[str, Any], int]: A tuple containing:
            - JobStatus: The status of the job (SUCCEEDED or FAILED).
            - Dict[str, Any]: A response payload with details, history, and preferred output.
            - int: The HTTP status code (200 for success, 500 for error, 504 for timeout).
    """
    async with aiohttp.ClientSession() as session:
        # Start continuous running monitor while we wait for completion
        stop_event = asyncio.Event()
        monitor_task = asyncio.create_task(
            _monitor_until_running(prompt_id, stop_event, comfy_url=comfy_url, session=session)
        )

        try:
            history_entry = await _wait_for_completion(
                prompt_id, RUNNER_CONFIG.prompt_timeout_seconds, comfy_url, session
            )
        except TimeoutError as exc:
            # Try to interrupt the run cleanly
            try:
                async with session.post(
                    f"{comfy_url}/interrupt",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"client_id": client_id})
                ) as interrupt_resp:
                    if interrupt_resp.status < 400:
                        logging.info("Successfully interrupted prompt %s", prompt_id)
            except Exception as interrupt_exc:
                logging.warning("Failed to interrupt prompt %s: %s", prompt_id, interrupt_exc)
            response = _make_run_payload(detail=str(exc), error_message="timeout")
            # stop monitor
            stop_event.set()
            with contextlib.suppress(Exception):
                monitor_task.cancel()
                await monitor_task
            return JobStatus.FAILED, response, 504
        finally:
            stop_event.set()
            with contextlib.suppress(Exception):
                monitor_task.cancel()
                await monitor_task

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

async def execute_workflow(
    payload: Dict[str, Any], prepared: Tuple[WorkflowNode, Dict[str, Any]] | None = None
) -> Tuple[str, JobStatus, Dict[str, Any], int]:
    """
    Execute a workflow by submitting it and finalizing the execution.
    This is a blocking convenience wrapper that preserves the old interface. It first submits the workflow using `submit_workflow`, and if successful, finalizes it using `finalize_workflow`. The function returns a 4-tuple containing the prompt ID, job status, response data, and HTTP status code.

    Args:
        payload (Dict[str, Any]): The payload data required to execute the workflow.
        prepared (Tuple[WorkflowNode, Dict[str, Any]] | None, optional): Pre-prepared workflow node and associated data. Defaults to None.

    Returns:
        Tuple[str, JobStatus, Dict[str, Any], int]: A tuple containing:
            - prompt_id (str): The unique identifier for the submitted prompt.
            - status (JobStatus): The final status of the job (e.g., SUCCESS, FAILED).
            - response (Dict[str, Any]): The response data from the workflow execution.
            - http_status (int): The HTTP status code from the finalization step.

    Raises:
        WorkflowPreparationError: If the workflow submission fails, this exception is caught and the function returns a failure tuple instead of propagating the error.
    """
    try:
        prompt_id, client_id, comfy_url, prompt, validation, _ = await submit_workflow(payload, prepared)
    except WorkflowPreparationError as exc:
        return "", JobStatus.FAILED, exc.response_body, exc.status
    
    status, response, http_status = await finalize_workflow(prompt_id, client_id, comfy_url, validation)

    return prompt_id, status, response, http_status
# endregion

__all__ = [
    "execute_workflow",
    "submit_workflow",
    "finalize_workflow",
    "_make_run_payload",
    "_prepare_workflow_execution",
    "_sanitize_history",
    "_wait_for_completion",
    "_monitor_until_running",
    "WorkflowPreparationError",
]
