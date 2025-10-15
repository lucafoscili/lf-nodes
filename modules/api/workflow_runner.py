import asyncio
import execution
import folder_paths
import logging
import os
import time
import uuid

from pathlib import Path
from typing import Any, Dict
from aiohttp import web
from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX, NOT_FND_HTML
from ..utils.helpers.logic.sanitize_filename import sanitize_filename
from ..workflows import get_workflow, list_workflows
from ..workflows.registry import _json_safe as workflow_json_safe

# region Static assets
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/static/{{path:.*}}")
async def lf_nodes_static_asset(request: web.Request) -> web.Response:
    try:
        module_root = Path(__file__).resolve().parents[2]
        rel_path = request.match_info.get('path', '')
        if '..' in rel_path or rel_path.startswith('/') or rel_path.startswith('\\'):
            return web.Response(status=400, text='Invalid path')

        asset_path = module_root / 'web' / 'deploy' / Path(rel_path)
        if asset_path.exists() and asset_path.is_file():
            return web.FileResponse(str(asset_path))
    except Exception:
        pass

    return web.Response(status=404, text='Not found')
# endregion

# region Submit prompt
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/submit-prompt")
async def lf_nodes_workflow_runner_page(_: web.Request) -> web.Response:
  try:
    module_root = Path(__file__).resolve().parents[2]
    deploy_html = module_root / "web" / "deploy" / "submit-prompt.html"
    if deploy_html.exists():
      return web.FileResponse(str(deploy_html))
    
  except Exception:
    pass

  return web.Response(text=NOT_FND_HTML, content_type="text/html", status=404)
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
        return web.json_response({"error": "invalid_json", "detail": str(exc)}, status=400)

    workflow_id = payload.get("workflowId")
    inputs = payload.get("inputs", {})
    if not isinstance(inputs, dict):
        return web.json_response(
            {"error": "invalid_inputs", "detail": "inputs must be an object"},
            status=400,
        )

    definition = get_workflow(workflow_id or "")
    if definition is None:
        return web.json_response(
            {"error": "unknown_workflow", "detail": f"No workflow found for id '{workflow_id}'."},
            status=404,
        )

    try:
        prompt = definition.load_prompt()
        definition.configure_prompt(prompt, inputs)
    except FileNotFoundError as exc:
        return web.json_response({"error": "missing_source", "detail": str(exc)}, status=400)
    except ValueError as exc:
        return web.json_response({"error": "invalid_input", "detail": str(exc)}, status=400)
    except Exception as exc:  # pragma: no cover - unexpected issues are surfaced to the UI
        logging.exception("Failed to prepare workflow '%s': %s", workflow_id, exc)
        return web.json_response({"error": "configuration_failed", "detail": str(exc)}, status=500)

    prompt_id = payload.get("promptId") or uuid.uuid4().hex
    validation = await execution.validate_prompt(prompt_id, prompt, None)
    if not validation[0]:
        return web.json_response(
            {
                "error": "validation_failed",
                "detail": validation[1],
                "node_errors": _json_safe(validation[3]),
            },
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
        return web.json_response({"error": "timeout", "detail": str(exc), "prompt_id": prompt_id}, status=504)

    status = history_entry.get("status") or {}
    status_str = status.get("status_str", "unknown")
    http_status = 200 if status_str == "success" else 500
    
    # Choose a preferred output to surface in the UI.
    # Prefer the first validated output (from validate_prompt) that produced outputs.
    preferred_output = None
    try:
        outputs_in_history = set((history_entry.get('outputs') or {}).keys())
        validated_outputs = validation[2] if isinstance(validation, (list, tuple)) and len(validation) > 2 else []
        for o in validated_outputs:
            if o in outputs_in_history:
                preferred_output = o
                break
        # Fallback: pick an output node that contains an images array if present
        if preferred_output is None:
            for o, v in (history_entry.get('outputs') or {}).items():
                try:
                    if isinstance(v, dict) and v.get('images'):
                        preferred_output = o
                        break
                except Exception:
                    continue
    except Exception:
        preferred_output = None

    return web.json_response(
        {
            "prompt_id": prompt_id,
            "status": status_str,
            "history": _sanitize_history(history_entry),
            "workflow_id": workflow_id,
            "preferred_output": preferred_output,
        },
        status=http_status,
    )
# endregion


# region Upload handler
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/upload")
async def lf_nodes_upload(request: web.Request) -> web.Response:
  """Accept a multipart file upload and save to Comfy temp directory.

  Returns JSON: { "path": <path_to_use_in_workflow> }
  The returned path is the absolute file path which can be passed to nodes that
  expect an image path. Files are written with their original filename into
  the temp directory.
  """
  reader = await request.multipart()
  field = await reader.next()
  if field is None or field.name != 'file':
    return web.json_response({'error': 'missing_file'}, status=400)

  raw_filename = field.filename or ""
  sanitized = sanitize_filename(raw_filename)
  if sanitized is None:
    filename = f"upload_{int(time.time())}.png"
  else:
    filename = sanitized
  # Ensure directory exists
  temp_dir = folder_paths.get_temp_directory()
  os.makedirs(temp_dir, exist_ok=True)
  # Avoid clobbering: add a numeric suffix if file exists
  dest_path = os.path.join(temp_dir, filename)
  base, ext = os.path.splitext(dest_path)
  counter = 1
  while os.path.exists(dest_path):
    dest_path = f"{base}_{counter}{ext}"
    counter += 1

  try:
    with open(dest_path, 'wb') as f:
      while True:
        chunk = await field.read_chunk()
        if not chunk:
          break
        f.write(chunk)
  except Exception as exc:
    logging.exception('Failed to save uploaded file: %s', exc)
    return web.json_response({'error': 'save_failed', 'detail': str(exc)}, status=500)

  # Return the absolute path which workflows expect for file inputs
  return web.json_response({'path': dest_path})
# endregion

# region Helpers
def _json_safe(value: Any) -> Any:
    """
    Thin wrapper that reuses the workflow serializer while keeping the intent
    clear within this module.
    """
    return workflow_json_safe(value)

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
    return {
        "status": _json_safe(entry.get("status")),
        "outputs": _json_safe(entry.get("outputs", {})),
        "prompt": _json_safe(entry.get("prompt")),
    }
# endregion
