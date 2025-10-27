import asyncio
import execution
import json
import logging
import os
import time
import uuid

from aiohttp import web
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple
from server import PromptServer

from .config import CONFIG as RUNNER_CONFIG
from .registry import InputValidationError, get_workflow, list_workflows
from ..utils.constants import API_ROUTE_PREFIX, NOT_FND_HTML
from ..utils.helpers.conversion import json_safe
from .job_manager import JobStatus, create_job, get_job, set_job_status

# Dev dotenv loader: load `.env` for local dev. The loader will run if either:
#  - DEV_ENV=1 is already set in the environment, OR
#  - a .env file exists next to this module (convenience for local dev).
try:
    env_path = Path(__file__).parent / ".env"
    should_load = os.environ.get("DEV_ENV") == "1" or env_path.exists()
    if should_load and env_path.exists():
        # lightweight loader to avoid adding a runtime dependency
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and not os.environ.get(k):
                os.environ[k] = v
except Exception:
    logging.exception('Failed to load local .env')

DEPLOY_ROOT = RUNNER_CONFIG.deploy_root
WORKFLOW_RUNNER_ROOT = RUNNER_CONFIG.runner_root
SHARED_JS_ROOT = RUNNER_CONFIG.shared_js_root

ASSET_SEARCH_ROOTS = (
    RUNNER_CONFIG.deploy_root,
    RUNNER_CONFIG.runner_root,
)

WORKFLOW_STATIC_ROOTS = (RUNNER_CONFIG.runner_root,)
WORKFLOW_HTML = RUNNER_CONFIG.workflow_html

# region Helpers

def _make_run_payload(
    *,
    detail: str = "",
    error_message: str | None = None,
    error_input: str | None = None,
    history: Dict[str, Any] | None = None,
    preferred_output: str | None = None,
) -> Dict[str, Any]:
    """
    Build a response payload compatible with the frontend's WorkflowAPIRunPayload:

    {
      "detail": string,
      "error": { "message": string, "input": string | undefined },
      "history": { outputs?: {...} },
      "preferred_output": string | undefined
    }
    """
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
    """
    Sanitize a single history entry for safe JSON serialization.
    The function returns a dictionary containing only the "status", "outputs",
    and "prompt" keys, each passed through `_json_safe` so nested values remain
    JSON-serializable while preserving the original key names.
    """
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
def _sanitize_rel_path(raw_path: str) -> Optional[Path]:
    """Sanitizes a relative path to prevent directory traversal and ensure safety.

    This function normalizes the input path by converting backslashes to forward slashes,
    checks for potentially unsafe elements like ".." or paths starting with "/", and
    constructs a Path object from valid parts if the path is deemed safe.

    Args:
        raw_path (str): The raw path string to be sanitized.

    Returns:
        Optional[Path]: A Path object representing the sanitized relative path if valid,
        or None if the path contains unsafe elements (e.g., ".." or absolute path indicators).
    """
    normalized = raw_path.replace("\\", "/")
    if ".." in normalized or normalized.startswith("/"):
        return None
    parts = [part for part in normalized.split("/") if part]
    return Path(*parts)

def _serve_first_existing(paths: Iterable[Path]) -> Optional[web.FileResponse]:
    """
    Serves the first existing file from a list of candidate paths.

    This function iterates through the provided paths and returns a web.FileResponse
    for the first path that exists and is a file. If no such path is found, it returns None.

    Args:
        paths (Iterable[Path]): An iterable of Path objects to check for existence and file status.

    Returns:
        Optional[web.FileResponse]: A FileResponse for the first existing file, or None if no file is found.
    """
    for candidate in paths:
        if candidate.exists() and candidate.is_file():
            return web.FileResponse(str(candidate))
    return None

async def _wait_for_completion(prompt_id: str, timeout_seconds: float = 180.0) -> Dict[str, Any]:
    """
    Poll the prompt queue history until the prompt either completes, fails,
    or the timeout is reached.
    """
    queue = PromptServer.instance.prompt_queue
    start = time.perf_counter()

    while True:
        history = queue.get_history(prompt_id=prompt_id)
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status") or {}
            if status.get("completed") is True or status.get("status_str") == "error":
                return entry
            if entry.get("outputs"):
                # Some nodes don't populate status but still produce outputs.
                return entry

        if (time.perf_counter() - start) >= timeout_seconds:
            raise TimeoutError(f"Prompt {prompt_id} did not finish within {timeout_seconds} seconds.")

        await asyncio.sleep(0.35)
# endregion

def _emit_run_progress(run_id: str, message: str, **extra: Any) -> None:
    payload = {"run_id": run_id, "message": message}
    if extra:
        payload.update(extra)
    try:
        PromptServer.instance.send_sync("lf-runner:progress", payload)
    except Exception:
        logging.exception("Failed to send progress event for run %s", run_id)

# region Workflow execution
async def execute_workflow(payload: Dict[str, Any], run_id: str) -> Tuple[JobStatus, Dict[str, Any], int]:
    workflow_id = payload.get("workflowId")
    inputs = payload.get("inputs", {})
    if not isinstance(inputs, dict):
        response = _make_run_payload(
            detail="inputs must be an object",
            error_message="invalid_inputs",
        )
        return JobStatus.FAILED, response, 400

    definition = get_workflow(workflow_id or "")
    if definition is None:
        response = _make_run_payload(
            detail=f"No workflow found for id '{workflow_id}'.",
            error_message="unknown_workflow",
        )
        return JobStatus.FAILED, response, 404

    try:
        prompt = definition.load_prompt()
        definition.configure_prompt(prompt, inputs)
    except FileNotFoundError as exc:
        response = _make_run_payload(detail=str(exc), error_message="missing_source")
        return JobStatus.FAILED, response, 400
    except InputValidationError as exc:
        response = _make_run_payload(
            detail=str(exc),
            error_message="invalid_input",
            error_input=getattr(exc, "input_name", None),
        )
        return JobStatus.FAILED, response, 400
    except ValueError as exc:
        response = _make_run_payload(detail=str(exc), error_message="invalid_input")
        return JobStatus.FAILED, response, 400
    except Exception as exc:
        logging.exception("Failed to prepare workflow '%s': %s", workflow_id, exc)
        response = _make_run_payload(detail=str(exc), error_message="configuration_failed")
        return JobStatus.FAILED, response, 500

    prompt_id = payload.get("promptId") or uuid.uuid4().hex
    validation = await execution.validate_prompt(prompt_id, prompt, None)
    if not validation[0]:
        response = _make_run_payload(
            detail=validation[1],
            error_message="validation_failed",
            history={"outputs": {}, "node_errors": json_safe(validation[3])},
        )
        return JobStatus.FAILED, response, 400

    server = PromptServer.instance
    queue_number = server.number
    server.number += 1

    extra_data = {"lf_nodes": {"workflow_id": workflow_id, "run_id": run_id}}
    extra_data.update(payload.get("extraData", {}))

    server.prompt_queue.put((queue_number, prompt_id, prompt, extra_data, validation[2]))
    _emit_run_progress(run_id, "workflow_queued", prompt_id=prompt_id)

    try:
        history_entry = await _wait_for_completion(prompt_id)
    except TimeoutError as exc:
        response = _make_run_payload(detail=str(exc), error_message="timeout")
        return JobStatus.FAILED, response, 504

    status = history_entry.get("status") or {}
    status_str = status.get("status_str", "unknown")
    http_status = 200 if status_str == "success" else 500

    preferred_output = None
    try:
        outputs_in_history = set((history_entry.get("outputs") or {}).keys())
        validated_outputs = (
            validation[2] if isinstance(validation, (list, tuple)) and len(validation) > 2 else []
        )
        for output_name in validated_outputs:
            if output_name in outputs_in_history:
                preferred_output = output_name
                break
        if preferred_output is None:
            for output_name, output_value in (history_entry.get("outputs") or {}).items():
                try:
                    if isinstance(output_value, dict) and (
                        output_value.get("images") or output_value.get("lf_images")
                    ):
                        preferred_output = output_name
                        break
                except Exception:
                    continue
    except Exception:
        preferred_output = None

    sanitized = _sanitize_history(history_entry)
    history_outputs = sanitized.get("outputs", {}) if isinstance(sanitized, dict) else {}
    if status_str == "success":
        response = _make_run_payload(
            detail="success",
            history={"outputs": history_outputs},
            preferred_output=preferred_output,
        )
        return JobStatus.SUCCEEDED, response, http_status

    response = _make_run_payload(
        detail=status_str or "error",
        error_message="execution_failed",
        history={"outputs": history_outputs},
        preferred_output=preferred_output,
    )
    return JobStatus.FAILED, response, http_status
# endregion

# region Workflow runner page
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflow-runner")
async def route_workflow_runner_page(_: web.Request) -> web.Response:
    try:
        response = _serve_first_existing((WORKFLOW_HTML,))

        if response is not None:
            return response

    except Exception:
        pass

    return web.Response(text=NOT_FND_HTML, content_type="text/html", status=404)
# endregion

# region Run
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/run")
async def route_run_workflow(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except Exception as exc:
        logging.warning("Failed to parse workflow request payload: %s", exc)
        return web.json_response(
            _make_run_payload(detail=str(exc), error_message="invalid_json"),
            status=400,
        )

    if not isinstance(payload, dict):
        return web.json_response(
            _make_run_payload(detail="Payload must be a JSON object.", error_message="invalid_payload"),
            status=400,
        )

    run_id = str(uuid.uuid4())
    await create_job(run_id)
    _emit_run_progress(run_id, "workflow_received")

    async def worker() -> None:
        try:
            await set_job_status(run_id, JobStatus.RUNNING)
            _emit_run_progress(run_id, "workflow_started")

            job_status, response_body, http_status = await execute_workflow(payload, run_id)
            job_result = {"http_status": http_status, "body": response_body}

            await set_job_status(run_id, job_status, result=job_result)
            _emit_run_progress(run_id, "workflow_completed", status=job_status.value)
        except asyncio.CancelledError:
            await set_job_status(run_id, JobStatus.CANCELLED, error="cancelled")
            _emit_run_progress(run_id, "workflow_cancelled")
            raise
        except Exception as exc:
            logging.exception("Workflow run %s failed unexpectedly: %s", run_id, exc)
            error_payload = _make_run_payload(detail=str(exc), error_message="unhandled_exception")
            job_result = {"http_status": 500, "body": error_payload}
            await set_job_status(run_id, JobStatus.FAILED, error=str(exc), result=job_result)
            _emit_run_progress(run_id, "workflow_failed", error=str(exc))

    PromptServer.instance.loop.create_task(worker())

    return web.json_response({"run_id": run_id}, status=202)


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/run/{{run_id}}/status")
async def route_run_status(request: web.Request) -> web.Response:
    run_id = request.match_info.get("run_id")
    if not run_id:
        raise web.HTTPNotFound(text="Unknown run id")

    job = await get_job(run_id)
    if job is None:
        raise web.HTTPNotFound(text="Unknown run id")

    is_terminal = job.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}
    payload = {
        "run_id": job.id,
        "status": job.status.value,
        "created_at": job.created_at,
        "error": job.error,
        "result": job.result if is_terminal else None,
    }
    return web.json_response(payload)
# endregion

# region Static assets
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static/{{path:.*}}")
async def route_static_asset(request: web.Request) -> web.Response:
    try:
        raw_path = request.match_info.get('path', '')
        if not raw_path.startswith('assets/'):
            return web.Response(status=404, text='Not found')

        rel_path = _sanitize_rel_path(raw_path)
        if rel_path is None:
            return web.Response(status=400, text='Invalid path')

        response = _serve_first_existing(root / rel_path for root in ASSET_SEARCH_ROOTS)
        if response is not None:
            return response
    except Exception:
        logging.exception('Error while attempting to serve static asset: %s', request.path)

    return web.Response(status=404, text='Not found')
# endregion

# region Static JS
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/js/{{path:.*}}")
async def route_static_js(request: web.Request) -> web.Response:
    try:
        raw_path = request.match_info.get('path', '')
        rel_path = _sanitize_rel_path(raw_path)
        if rel_path is None:
            return web.Response(status=400, text='Invalid path')

        response = _serve_first_existing((SHARED_JS_ROOT / rel_path,))
        if response is not None:
            return response
    except Exception:
        logging.exception('Error while attempting to serve shared JS asset: %s', request.path)

    return web.Response(status=404, text='Not found')
# endregion

# region Workflow static
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static-workflow-runner/{'{path:.*}'}")
async def route_static_workflow(request: web.Request) -> web.Response:
    try:
        raw_path = request.match_info.get('path', '')
        rel_path = _sanitize_rel_path(raw_path)
        if rel_path is None:
            return web.Response(status=400, text='Invalid path')

        response = _serve_first_existing(root / rel_path for root in WORKFLOW_STATIC_ROOTS)
        if response is not None:
            return response
    except Exception:
        pass

    return web.Response(status=404, text='Not found')
# endregion

# region List workflows
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows")
async def route_list_workflows(_: web.Request) -> web.Response:
    return web.json_response({"workflows": list_workflows()})
# endregion

# region Get workflow
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows/{{workflow_id}}")
async def route_get_workflow(request: web.Request) -> web.Response:
    workflow_id = request.match_info.get('workflow_id')
    if not workflow_id:
        return web.Response(status=400, text='Missing workflow_id')
    
    workflow = get_workflow(workflow_id)
    if not workflow:
        return web.Response(status=404, text='Workflow not found')
    
    try:
        with workflow.workflow_path.open("r", encoding="utf-8") as workflow_file:
            workflow_json = json.load(workflow_file)
        return web.json_response(workflow_json)
    except Exception as e:
        logging.exception(f"Error loading workflow {workflow_id}")
        return web.Response(status=500, text=f'Error loading workflow: {str(e)}')
# endregion
