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
import os
import folder_paths

# region Submit prompt
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/submit-prompt")
async def lf_nodes_workflow_runner_page(_: web.Request) -> web.Response:
    return web.Response(text=LFN_WORKFLOW_RUNNER_HTML, content_type="text/html")
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

  filename = field.filename or f"upload_{int(time.time())}"
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

# region HTML content
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

          // Special-case the common 'source_path' field: render a file input
          // so users can upload an image directly. The uploaded file will be
          // sent to the server and stored in Comfy's temp directory.
          let input;
          if (field.name === 'source_path') {
            input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.className = 'fallback-input';
          } else {
            input = document.createElement('input');
            input.type = 'text';
            input.value = field.default ?? '';
            input.className = 'fallback-input';
            if (field.placeholder) {
              input.placeholder = field.placeholder;
            }
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
              // If this is a file input, return the File object (or null)
              if (input.type === 'file') {
                return input.files && input.files.length > 0 ? input.files[0] : null;
              }
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
          // Upload any selected files first and replace value with the
          // saved path returned by the server.
          for (const [name, renderer] of fieldRenderers.entries()) {
            const val = await renderer.getValue();
            // If val is a File object, upload it to the server
            if (val instanceof File) {
              setStatus('Uploading file…', 'info');
              const form = new FormData();
              form.append('file', val, val.name);
              try {
                const uploadResp = await fetch(`${API_BASE}/upload`, { method: 'POST', body: form });
                if (!uploadResp.ok) {
                  const err = await uploadResp.text();
                  throw new Error(`Upload failed: ${err}`);
                }
                const uploadJson = await uploadResp.json();
                // Server returns the absolute path to use as the workflow input
                inputs[name] = uploadJson.path;
              } catch (err) {
                setStatus('File upload failed.', 'error');
                resultElement.textContent = String(err);
                runButton.disabled = false;
                return;
              }
            } else {
              inputs[name] = val;
            }
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

            // If outputs contain image info (or any outputs), render them and
            // provide a small selector when multiple outputs exist. Default to
            // the server-provided preferred_output when available.
            const outputs = payload.history && payload.history.outputs ? payload.history.outputs : {};
            const outputKeys = Object.keys(outputs || {});

            // Determine which key to show by default
            const preferred = payload.preferred_output;
            let selectedKey = null;
            if (preferred && outputs[preferred]) selectedKey = preferred;
            else if (outputKeys.length > 0) selectedKey = outputKeys[0];

            // Helper: render a single output key (images if present, otherwise JSON)
            function renderOutputForKey(key) {
              resultElement.innerHTML = '';
              if (!key || !outputs[key]) {
                resultElement.textContent = stringify(outputs);
                return;
              }
              const val = outputs[key];
              // If images[] exists, render the first image
              try {
                if (val && val.images && Array.isArray(val.images) && val.images.length > 0) {
                  const imgInfo = val.images[0];
                  const filename = imgInfo.filename || imgInfo.name;
                  const type = imgInfo.type || 'temp';
                  const subfolder = imgInfo.subfolder || '';
                  if (filename) {
                    const url = `/view?filename=${encodeURIComponent(filename)}&type=${encodeURIComponent(type)}&subfolder=${encodeURIComponent(subfolder)}`;
                    const img = document.createElement('img');
                    img.src = url;
                    img.style.maxWidth = '100%';
                    img.style.borderRadius = '8px';
                    img.alt = filename;
                    resultElement.appendChild(img);
                    return;
                  }
                }
                // If there's an SVG UI payload, render it inline and add download
                if (val && val.svg) {
                  const svgText = Array.isArray(val.svg) ? val.svg[0] : val.svg;
                  try {
                    // Create a container and inject the SVG string. We trust this SVG
                    // because it was produced locally by the workflow, but to be safe
                    // render inside a sandboxed <object> when possible.
                    const wrapper = document.createElement('div');
                    wrapper.style.borderRadius = '8px';
                    wrapper.style.overflow = 'auto';
                    wrapper.style.padding = '0.6rem';
                    wrapper.style.background = '#061018';

                    // Use an <object> with data: URI so the SVG is rendered as vector
                    const blob = new Blob([svgText], { type: 'image/svg+xml' });
                    const url = URL.createObjectURL(blob);
                    const obj = document.createElement('object');
                    obj.type = 'image/svg+xml';
                    obj.data = url;
                    obj.style.width = '100%';
                    obj.style.height = '480px';
                    obj.style.border = 'none';
                    wrapper.appendChild(obj);

                    // Add download button
                    const dl = document.createElement('a');
                    dl.href = url;
                    dl.download = (key + '.svg') || 'result.svg';
                    dl.textContent = 'Download SVG';
                    dl.style.display = 'inline-block';
                    dl.style.marginTop = '0.6rem';
                    dl.style.padding = '0.45rem 0.65rem';
                    dl.style.background = '#1f2533';
                    dl.style.border = '1px solid #39435a';
                    dl.style.borderRadius = '8px';
                    dl.style.color = 'white';
                    wrapper.appendChild(dl);

                    resultElement.appendChild(wrapper);
                    return;
                  } catch (e) {
                    // Continue to textual fallback
                  }
                }
              } catch (e) {
                // fall through to textual representation
              }

              // Fallback: pretty-print the specific output node (or all outputs)
              if (outputs[key]) {
                resultElement.textContent = stringify(outputs[key]);
              } else {
                resultElement.textContent = stringify(outputs);
              }
            }

            // If multiple outputs, create a small dropdown for choosing which
            // node's output to display. Insert it above the result element.
            let outputSelect = document.getElementById('output-select');
            if (outputKeys.length > 1) {
              if (!outputSelect) {
                outputSelect = document.createElement('select');
                outputSelect.id = 'output-select';
                outputSelect.style.marginTop = '0.6rem';
                outputSelect.style.padding = '0.4rem 0.6rem';
                outputSelect.style.borderRadius = '8px';
                outputSelect.style.background = '#111520';
                outputSelect.style.border = '1px solid #3a4154';
                outputSelect.style.color = 'inherit';
                // Insert before resultElement
                resultElement.parentNode.insertBefore(outputSelect, resultElement);
              }
              // Populate options
              outputSelect.innerHTML = '';
              for (const key of outputKeys) {
                const opt = document.createElement('option');
                opt.value = key;
                opt.textContent = `${key}`;
                if (key === preferred) opt.textContent += ' (preferred)';
                outputSelect.appendChild(opt);
              }
              outputSelect.value = selectedKey;
              outputSelect.onchange = (e) => {
                renderOutputForKey(e.target.value);
              };
            } else {
              // Remove select if present and not needed
              if (outputSelect && outputSelect.parentNode) outputSelect.parentNode.removeChild(outputSelect);
            }

            // Finally render the selected output (or a fallback)
            renderOutputForKey(selectedKey);
          } catch (error) {
            console.error(error);
            setStatus('Failed to execute workflow.', 'error');
            resultElement.textContent = String(error);
          } finally {
            runButton.disabled = false;
          }
        });

        // Upload endpoint helper (server-side implemented below)

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
