import asyncio
import logging
import time
import uuid
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict

from aiohttp import web

import execution
from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX
from ..workflows import get_workflow, list_workflows
from ..workflows.registry import _json_safe as workflow_json_safe

LFN_WORKFLOW_RUNNER_HTML = dedent(
    """\
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>LF Nodes — Workflow Runner</title>
      <style>
        :root { color-scheme: dark; font-family: "Segoe UI", system-ui, sans-serif; }
        body { margin: 0; background: #0f1115; color: #e8ebf0; }
        main {
          max-width: 720px;
          margin: 3rem auto;
          padding: 2rem 2.5rem;
          background: rgba(20, 24, 32, 0.92);
          border-radius: 18px;
          box-shadow: 0 22px 60px rgba(7, 12, 22, 0.45);
        }
        h1 { margin: 0 0 1.5rem; font-size: 1.85rem; letter-spacing: 0.02em; }
        .field { margin: 1.5rem 0; display: flex; flex-direction: column; gap: 0.6rem; }
        .field label { font-weight: 600; }
        select, button {
          background: #161b24;
          color: inherit;
          border: 1px solid #252b38;
          border-radius: 10px;
          padding: 0.7rem 0.85rem;
          font-size: 1rem;
          transition: border 0.15s ease, transform 0.15s ease, background 0.15s ease;
        }
        select:focus-visible, button:focus-visible { outline: 2px solid #3f7fff; outline-offset: 3px; }
        button { cursor: pointer; font-weight: 600; margin-top: 1rem; }
        button[disabled] { opacity: 0.55; cursor: not-allowed; }
        button:not([disabled]):hover { transform: translateY(-1px); background: #1f2533; border-color: #39435a; }
        .field__description { font-size: 0.9rem; opacity: 0.75; margin: 0; }
        #status { margin-top: 1.25rem; min-height: 1.5rem; font-size: 0.95rem; transition: color 0.2s ease; }
        #status[data-tone="info"] { color: #8ab4ff; }
        #status[data-tone="warn"] { color: #ffd166; }
        #status[data-tone="error"] { color: #ff6f6f; }
        #result {
          background: #0b0d12;
          border-radius: 14px;
          padding: 1rem 1.2rem;
          margin-top: 1rem;
          white-space: pre-wrap;
          max-height: 360px;
          overflow: auto;
          border: 1px solid #1d2230;
          font-size: 0.95rem;
        }
        .fallback-input {
          padding: 0.6rem 0.75rem;
          border-radius: 8px;
          border: 1px solid #3a4154;
          background: #111520;
          color: inherit;
        }
      </style>
    </head>
    <body>
      <main>
        <h1>LF Nodes — Workflow Runner</h1>
        <section class="field">
          <label for="workflow-select">Workflow</label>
          <select id="workflow-select"></select>
        </section>
        <section id="fields"></section>
        <button id="run-button" type="button">Run workflow</button>
        <div id="status" data-tone="info"></div>
        <pre id="result"></pre>
      </main>
      <script type="module">
        const API_BASE = '/api/lf-nodes';
        const workflowSelect = document.getElementById('workflow-select');
        const fieldsContainer = document.getElementById('fields');
        const runButton = document.getElementById('run-button');
        const statusElement = document.getElementById('status');
        const resultElement = document.getElementById('result');

        let workflows = [];
        const fieldRenderers = new Map();

        const stringify = (value) => JSON.stringify(value, null, 2);

        function setStatus(message, tone = 'info') {
          statusElement.textContent = message ?? '';
          statusElement.dataset.tone = tone;
        }

        function resetResult() {
          resultElement.textContent = '';
        }

        function createFieldRenderer(field) {
          const wrapper = document.createElement('div');
          wrapper.className = 'field';

          const label = document.createElement('label');
          label.textContent = field.label;
          wrapper.appendChild(label);

          const input = document.createElement('input');
          input.type = 'text';
          input.value = field.default ?? '';
          input.className = 'fallback-input';
          if (field.placeholder) {
            input.placeholder = field.placeholder;
          }
          if (field.extra && field.extra.htmlAttributes) {
            Object.entries(field.extra.htmlAttributes).forEach(([key, value]) => {
              try {
                input.setAttribute(key, value);
              } catch (_) {
                /* skip invalid attributes */
              }
            });
          }
          wrapper.appendChild(input);

          if (field.description) {
            const desc = document.createElement('p');
            desc.className = 'field__description';
            desc.textContent = field.description;
            wrapper.appendChild(desc);
          }

          return {
            element: wrapper,
            async getValue() {
              return input.value;
            }
          };
        }

        async function renderFields(workflowId) {
          fieldRenderers.clear();
          fieldsContainer.textContent = '';
          const workflow = workflows.find((wf) => wf.id === workflowId);
          if (!workflow) {
            return;
          }
          for (const field of workflow.fields ?? []) {
            const renderer = createFieldRenderer(field);
            fieldsContainer.appendChild(renderer.element);
            fieldRenderers.set(field.name, renderer);
          }
        }

        async function loadWorkflows() {
          const response = await fetch(`${API_BASE}/workflows`);
          if (!response.ok) {
            throw new Error(`Failed to load workflows (${response.status})`);
          }
          const data = await response.json();
          workflows = Array.isArray(data.workflows) ? data.workflows : [];
          workflowSelect.innerHTML = '';
          workflows.forEach((wf, index) => {
            const option = document.createElement('option');
            option.value = wf.id;
            option.textContent = wf.label ?? wf.id;
            if (index === 0) option.selected = true;
            workflowSelect.appendChild(option);
          });
          if (workflows.length > 0) {
            await renderFields(workflows[0].id);
          }
        }

        workflowSelect.addEventListener('change', (event) => {
          renderFields(event.target.value);
        });

        runButton.addEventListener('click', async () => {
          const workflowId = workflowSelect.value;
          if (!workflowId) {
            setStatus('Select a workflow to continue.', 'warn');
            return;
          }
          runButton.disabled = true;
          setStatus('Submitting workflow…', 'info');
          resetResult();

          const inputs = {};
          for (const [name, renderer] of fieldRenderers.entries()) {
            inputs[name] = await renderer.getValue();
          }

          try {
            const response = await fetch(`${API_BASE}/run`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ workflowId, inputs }),
            });
            const payload = await response.json();
            if (!response.ok) {
              setStatus(payload.detail ?? 'Workflow execution failed.', 'error');
              resultElement.textContent = stringify(payload);
              return;
            }
            setStatus(`Workflow completed with status: ${payload.status}`, 'info');
            resultElement.textContent = stringify(payload.history.outputs);
          } catch (error) {
            console.error(error);
            setStatus('Failed to execute workflow.', 'error');
            resultElement.textContent = String(error);
          } finally {
            runButton.disabled = false;
          }
        });

        loadWorkflows()
          .then(() => setStatus('Ready.', 'info'))
          .catch((error) => {
            console.error(error);
            setStatus('Unable to load workflows.', 'error');
          });
      </script>
    </body>
    </html>
    """
)

_LFW_PACKAGE_ROOTS = {
    "core": Path(__file__).resolve().parents[5] / "lf-widgets" / "packages" / "core" / "dist",
    "foundations": Path(__file__).resolve().parents[5] / "lf-widgets" / "packages" / "foundations" / "dist",
    "framework": Path(__file__).resolve().parents[5] / "lf-widgets" / "packages" / "framework" / "dist",
}


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


def _resolve_lfw_asset(relative_path: str) -> Path | None:
    if not relative_path:
        return None

    normalized = relative_path.strip("/")
    if not normalized:
        return None

    parts = Path(normalized).parts
    package_key = parts[0] if parts and parts[0] in _LFW_PACKAGE_ROOTS else "core"
    root = _LFW_PACKAGE_ROOTS.get(package_key)
    if root is None or not root.exists():
        logging.warning("LF Widgets package '%s' dist folder not found at %s", package_key, root)
        return None

    remaining_parts = parts[1:] if parts and parts[0] == package_key else parts
    base_path = root.joinpath(*remaining_parts) if remaining_parts else root

    candidate_strings = [str(base_path)]

    if not base_path.suffix:
        candidate_strings.append(f"{base_path}.js")
        candidate_strings.append(str(base_path / "index.js"))
        candidate_strings.append(f"{base_path}.mjs")

    for candidate_str in candidate_strings:
        candidate = Path(candidate_str).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            continue

        if candidate.is_file():
            return candidate

    return None


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows")
async def lf_nodes_list_workflows(_: web.Request) -> web.Response:
    return web.json_response({"workflows": list_workflows()})


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

    return web.json_response(
        {
            "prompt_id": prompt_id,
            "status": status_str,
            "history": _sanitize_history(history_entry),
            "workflow_id": workflow_id,
        },
        status=http_status,
    )


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/submit-prompt")
async def lf_nodes_workflow_runner_page(_: web.Request) -> web.Response:
    return web.Response(text=LFN_WORKFLOW_RUNNER_HTML, content_type="text/html")


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/assets/lfw/{{asset_path:.*}}")
async def lf_nodes_lfw_assets(request: web.Request) -> web.Response:
    asset_path = request.match_info.get("asset_path", "")
    asset = _resolve_lfw_asset(asset_path)
    if asset is None:
        return web.Response(status=404, text="Asset not found")
    return web.FileResponse(asset)
