import asyncio
import execution
import folder_paths
import logging
import os
import time
import uuid

from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from aiohttp import web
from server import PromptServer

from .config import CONFIG as RUNNER_CONFIG
from .registry import InputValidationError, get_workflow, list_workflows
from .registry import _json_safe as workflow_json_safe
from ..utils.constants import API_ROUTE_PREFIX, NOT_FND_HTML
from ..utils.helpers.logic.sanitize_filename import sanitize_filename

DEPLOY_ROOT = RUNNER_CONFIG.deploy_root
WORKFLOW_RUNNER_ROOT = RUNNER_CONFIG.runner_root
SHARED_JS_ROOT = RUNNER_CONFIG.shared_js_root

ASSET_SEARCH_ROOTS = (
    RUNNER_CONFIG.deploy_root,
    RUNNER_CONFIG.runner_root,
)

WORKFLOW_STATIC_ROOTS = (RUNNER_CONFIG.runner_root,)
WORKFLOW_HTML = RUNNER_CONFIG.workflow_html


def _sanitize_rel_path(raw_path: str) -> Optional[Path]:
    normalized = raw_path.replace("\\", "/")
    if ".." in normalized or normalized.startswith("/"):
        return None
    parts = [part for part in normalized.split("/") if part]
    return Path(*parts)


def _serve_first_existing(paths: Iterable[Path]) -> Optional[web.FileResponse]:
    for candidate in paths:
        if candidate.exists() and candidate.is_file():
            return web.FileResponse(str(candidate))
    return None

# region Workflow runner page
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflow-runner")
async def lf_nodes_workflow_runner_page(_: web.Request) -> web.Response:
    try:
        response = _serve_first_existing((WORKFLOW_HTML,))

        if response is not None:
            return response

    except Exception:
        pass

    return web.Response(text=NOT_FND_HTML, content_type="text/html", status=404)
# endregion

# region Static assets
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static/{{path:.*}}")
async def lf_nodes_static_asset(request: web.Request) -> web.Response:
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

# region Shared JS
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/js/{{path:.*}}")
async def lf_nodes_static_js(request: web.Request) -> web.Response:
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
async def lf_nodes_static_workflow(request: web.Request) -> web.Response:
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

# region Workflow
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows")
async def lf_nodes_list_workflows(_: web.Request) -> web.Response:
    return web.json_response({"workflows": list_workflows()})
# endregion

# region Run
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/run")
async def lf_nodes_run_workflow(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except Exception as exc:  # pragma: no cover - defensive, logged to UI
        logging.warning("Failed to parse workflow request payload: %s", exc)
        return web.json_response(_make_run_payload(detail=str(exc), error_message="invalid_json"), status=400)

    workflow_id = payload.get("workflowId")
    inputs = payload.get("inputs", {})
    if not isinstance(inputs, dict):
        return web.json_response(
            _make_run_payload(detail="inputs must be an object", error_message="invalid_inputs"),
            status=400,
        )

    definition = get_workflow(workflow_id or "")
    if definition is None:
        return web.json_response(
            _make_run_payload(detail=f"No workflow found for id '{workflow_id}'.", error_message="unknown_workflow"),
            status=404,
        )

    try:
        prompt = definition.load_prompt()
        definition.configure_prompt(prompt, inputs)
    except FileNotFoundError as exc:
        return web.json_response(_make_run_payload(detail=str(exc), error_message="missing_source"), status=400)
    except InputValidationError as exc:
        # Provide the offending input name so the UI can highlight the field
        return web.json_response(_make_run_payload(detail=str(exc), error_message="invalid_input", error_input=getattr(exc, 'input_name', None)), status=400)
    except ValueError as exc:
        return web.json_response(_make_run_payload(detail=str(exc), error_message="invalid_input"), status=400)
    except Exception as exc:  # pragma: no cover - unexpected issues are surfaced to the UI
        logging.exception("Failed to prepare workflow '%s': %s", workflow_id, exc)
        return web.json_response(_make_run_payload(detail=str(exc), error_message="configuration_failed"), status=500)

    prompt_id = payload.get("promptId") or uuid.uuid4().hex
    validation = await execution.validate_prompt(prompt_id, prompt, None)
    if not validation[0]:
        return web.json_response(
            _make_run_payload(
                detail=validation[1],
                error_message="validation_failed",
                history={"outputs": {}, "node_errors": _json_safe(validation[3])},
            ),
            status=400,
        )

    server = PromptServer.instance
    queue_number = server.number
    server.number += 1

    extra_data = {"lf_nodes": {"workflow_id": workflow_id}}
    extra_data.update(payload.get("extraData", {}))

    server.prompt_queue.put((queue_number, prompt_id, prompt, extra_data, validation[2]))

    try:
        history_entry = await _wait_for_completion(prompt_id)
    except TimeoutError as exc:
        return web.json_response(_make_run_payload(detail=str(exc), error_message="timeout"), status=504)

    status = history_entry.get("status") or {}
    status_str = status.get("status_str", "unknown")
    http_status = 200 if status_str == "success" else 500
    
    preferred_output = None
    try:
        outputs_in_history = set((history_entry.get('outputs') or {}).keys())
        validated_outputs = validation[2] if isinstance(validation, (list, tuple)) and len(validation) > 2 else []
        for o in validated_outputs:
            if o in outputs_in_history:
                preferred_output = o
                break
        if preferred_output is None:
            for o, v in (history_entry.get('outputs') or {}).items():
                try:
                    if isinstance(v, dict) and (v.get('images') or v.get('lf_images')):
                        preferred_output = o
                        break
                except Exception:
                    continue
    except Exception:
        preferred_output = None

    # Build payload matching WorkflowAPIRunPayload:
    sanitized = _sanitize_history(history_entry)
    history_outputs = sanitized.get("outputs", {}) if isinstance(sanitized, dict) else {}
    if status_str == "success":
        return web.json_response(
            _make_run_payload(detail="success", history={"outputs": history_outputs}, preferred_output=preferred_output),
            status=200,
        )
    else:
        # Non-success execution -> surface an error object and return non-200 status
        return web.json_response(
            _make_run_payload(detail=status_str or "error", error_message="execution_failed", history={"outputs": history_outputs}, preferred_output=preferred_output),
            status=http_status,
        )
# endregion


# region Upload handler
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/upload")
async def lf_nodes_upload(request: web.Request) -> web.Response:
    """Accept a multipart file upload and save to Comfy temp directory.

    Returns a run-style WorkflowAPIResponse wrapped by _make_run_payload.
    The returned path is the absolute file path which can be passed to nodes
    that expect an image path. Files are written with their original filename
    into the temp directory.
    """
    # Expect a multipart form with one or more fields named 'file'
    try:
        reader = await request.multipart()
    except Exception as exc:
        logging.warning('Failed to parse multipart upload: %s', exc)
        return web.json_response({
            "message": str(exc),
            "payload": {"detail": str(exc), "error": {"message": 'invalid_multipart'}},
            "status": "error",
        }, status=400)

    paths = []
    temp_dir = folder_paths.get_temp_directory()
    os.makedirs(temp_dir, exist_ok=True)

    # Iterate through all parts and save those with name 'file' (support multiple files)
    try:
        while True:
            part = await reader.next()
            if part is None:
                break

            # Only process file fields named 'file' (also accept 'files' for compatibility)
            if part.name not in ('file', 'files'):
                # skip other form fields
                continue

            raw_filename = part.filename or ""
            sanitized = sanitize_filename(raw_filename)
            if sanitized is None:
                # add a timestamp suffix to create a filename
                sanitized = f"upload_{int(time.time())}.png"

            # Avoid clobbering: add a numeric suffix if file exists
            dest_path = os.path.join(temp_dir, sanitized)
            base, ext = os.path.splitext(dest_path)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = f"{base}_{counter}{ext}"
                counter += 1

            # Write file to disk
            with open(dest_path, 'wb') as f:
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)

            paths.append(dest_path)
    except Exception as exc:
        logging.exception('Failed while saving uploaded files: %s', exc)
        return web.json_response({
            "message": str(exc),
            "payload": {"detail": str(exc), "error": {"message": 'save_failed'}},
            "status": "error",
        }, status=500)

    if not paths:
        return web.json_response({
            "message": "missing_file",
            "payload": {"detail": "missing_file", "error": {"message": 'missing_file'}},
            "status": "error",
        }, status=400)

    # Build a dedicated upload-style payload with saved paths
    return web.json_response({
        "message": "success",
        "payload": {"detail": "success", "paths": paths},
        "status": "ready",
    }, status=200)
# endregion

# region Helpers
def _json_safe(value: Any) -> Any:
    """
    Thin wrapper that reuses the workflow serializer while keeping the intent
    clear within this module.
    """
    return workflow_json_safe(value)


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

def _sanitize_history(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize a single history entry for safe JSON serialization.
    This function processes a history entry dictionary and returns a sanitized
    representation containing only the "status", "outputs", and "prompt" keys,
    each run through a helper (_json_safe) to ensure JSON-serializability.
    Behavior:
    - The function reads entry.get("outputs", {}) and treats None as an empty dict.
    - For each node_id -> node_out pair in outputs:
        - If node_out is a dict:
            - Make a shallow copy and rename any keys that start with "lf_" by removing
                that prefix (e.g., "lf_key" -> "key"), but only if the resulting name is
                non-empty and does not already exist in the dict. Other keys are preserved.
        - If node_out is a list:
            - Iterate elements; for any element that is a dict, apply the same
                "lf_"-prefix renaming logic on a shallow copy of that element. Non-dict
                elements are preserved as-is.
        - Any other types for node_out are preserved unchanged.
        - If processing a node_out raises an exception, the original node_out is
            kept unchanged as a fallback.
    - After processing all outputs, the function returns a dict with:
            {"status": _json_safe(status_value),
             "prompt": _json_safe(prompt_value)}
    Parameters
    ----------
    entry : Dict[str, Any]
            The history entry to sanitize. Expected to possibly contain the keys
            "status", "outputs", and "prompt", where "outputs" is typically a mapping
            of node identifiers to values (dict, list, or other).
    Returns
    -------
    Dict[str, Any]
            A sanitized dictionary with keys "status", "outputs", and "prompt",
            suitable for JSON serialization via the helper _json_safe.
    Notes
    -----
    - The function only removes the "lf_" prefix from keys when doing so will not
        cause a key collision in the same mapping.
    - _json_safe is an external helper assumed to convert arbitrary objects into
        JSON-safe representations; consult its implementation for specific behavior.
    """
    outputs = entry.get("outputs", {}) or {}
    safe_outputs = {}
    for node_id, node_out in outputs.items():
        try:
            if isinstance(node_out, dict):
                node_copy = dict(node_out)
                for key in list(node_copy.keys()):
                    if key.startswith('lf_'):
                        new_key = key[3:]
                        if new_key and new_key not in node_copy:
                            node_copy[new_key] = node_copy.pop(key)
                safe_outputs[node_id] = node_copy
            elif isinstance(node_out, list):
                new_list = []
                for elem in node_out:
                    if isinstance(elem, dict):
                        elem_copy = dict(elem)
                        for key in list(elem_copy.keys()):
                            if key.startswith('lf_'):
                                new_key = key[3:]
                                if new_key and new_key not in elem_copy:
                                    elem_copy[new_key] = elem_copy.pop(key)
                        new_list.append(elem_copy)
                    else:
                        new_list.append(elem)
                safe_outputs[node_id] = new_list
            else:
                safe_outputs[node_id] = node_out
        except Exception:
            safe_outputs[node_id] = node_out

    return {
        "status": _json_safe(entry.get("status")),
        "outputs": _json_safe(safe_outputs),
        "prompt": _json_safe(entry.get("prompt")),
    }
# endregion
