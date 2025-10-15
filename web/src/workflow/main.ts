// Entry for the Workflow Runner UI (TypeScript)
// This file contains the same logic that was previously embedded in the
// Python file's LFN_WORKFLOW_RUNNER_HTML. It's intentionally small and
// framework-free so it can be maintained easily and built with Vite.

const API_BASE = '/api/lf-nodes';

const workflowSelect = document.getElementById('workflow-select') as HTMLSelectElement;
const fieldsContainer = document.getElementById('fields') as HTMLElement;
const runButton = document.getElementById('run-button') as HTMLButtonElement;
const statusElement = document.getElementById('status') as HTMLElement;
const resultElement = document.getElementById('result') as HTMLElement;

let workflows: any[] = [];
const fieldRenderers = new Map<string, any>();

const stringify = (value: any) => JSON.stringify(value, null, 2);

function setStatus(message: string | null, tone: string = 'info') {
  if (!statusElement) return;
  statusElement.textContent = message ?? '';
  statusElement.dataset.tone = tone;
}

function resetResult() {
  if (!resultElement) return;
  resultElement.textContent = '';
}

function createFieldRenderer(field: any) {
  const wrapper = document.createElement('div');
  wrapper.className = 'field';

  const label = document.createElement('label');
  label.textContent = field.label;
  wrapper.appendChild(label);

  let input: HTMLInputElement;
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
    if (field.placeholder) input.placeholder = field.placeholder;
  }

  if (field.extra && field.extra.htmlAttributes) {
    Object.entries(field.extra.htmlAttributes).forEach(([key, value]) => {
      try {
        input.setAttribute(key, String(value));
      } catch (_) {
        /* noop */
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
      if (input.type === 'file') {
        // @ts-ignore
        return input.files && input.files.length > 0 ? input.files[0] : null;
      }
      return input.value;
    },
  };
}

async function renderFields(workflowId: string) {
  fieldRenderers.clear();
  if (fieldsContainer) fieldsContainer.textContent = '';
  const workflow = workflows.find((wf) => wf.id === workflowId);
  if (!workflow) return;
  for (const field of workflow.fields ?? []) {
    const renderer = createFieldRenderer(field);
    fieldsContainer.appendChild(renderer.element);
    fieldRenderers.set(field.name, renderer);
  }
}

async function loadWorkflows() {
  const response = await fetch(`${API_BASE}/workflows`);
  if (!response.ok) throw new Error(`Failed to load workflows (${response.status})`);
  const data = await response.json();
  workflows = Array.isArray(data.workflows) ? data.workflows : [];
  if (workflowSelect) workflowSelect.innerHTML = '';
  workflows.forEach((wf, index) => {
    const option = document.createElement('option');
    option.value = wf.id;
    option.textContent = wf.label ?? wf.id;
    if (index === 0) option.selected = true;
    workflowSelect.appendChild(option);
  });
  if (workflows.length > 0) await renderFields(workflows[0].id);
}

if (workflowSelect) {
  workflowSelect.addEventListener('change', (event) => {
    // @ts-ignore
    renderFields(event.target.value);
  });
}

if (runButton) {
  runButton.addEventListener('click', async () => {
    const workflowId = workflowSelect?.value;
    if (!workflowId) {
      setStatus('Select a workflow to continue.', 'warn');
      return;
    }

    runButton.disabled = true;
    setStatus('Submitting workflow…', 'info');
    resetResult();

    const inputs: Record<string, any> = {};

    for (const [name, renderer] of fieldRenderers.entries()) {
      const val = await renderer.getValue();
      if (val instanceof File) {
        setStatus('Uploading file…', 'info');
        const form = new FormData();
        form.append('file', val, val.name);
        try {
          const uploadResp = await fetch(`${API_BASE}/upload`, { method: 'POST', body: form });
          if (!uploadResp.ok) throw new Error(await uploadResp.text());
          const uploadJson = await uploadResp.json();
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

      const outputs = payload.history && payload.history.outputs ? payload.history.outputs : {};
      const outputKeys = Object.keys(outputs || {});
      const preferred = payload.preferred_output;
      let selectedKey: string | null = null;
      if (preferred && outputs[preferred]) selectedKey = preferred;
      else if (outputKeys.length > 0) selectedKey = outputKeys[0];

      function renderOutputForKey(key: string | null) {
        if (!resultElement) return;
        resultElement.innerHTML = '';
        if (!key || !outputs[key]) {
          resultElement.textContent = stringify(outputs);
          return;
        }
        const val = outputs[key];
        try {
          if (val && val.images && Array.isArray(val.images) && val.images.length > 0) {
            const imgInfo = val.images[0];
            const filename = imgInfo.filename || imgInfo.name;
            const type = imgInfo.type || 'temp';
            const subfolder = imgInfo.subfolder || '';
            if (filename) {
              const url = `/view?filename=${encodeURIComponent(filename)}&type=${encodeURIComponent(
                type,
              )}&subfolder=${encodeURIComponent(subfolder)}`;
              const img = document.createElement('img');
              img.src = url;
              img.style.maxWidth = '100%';
              img.style.borderRadius = '8px';
              img.alt = filename;
              resultElement.appendChild(img);
              return;
            }
          }
          if (val && val.svg) {
            const svgText = Array.isArray(val.svg) ? val.svg[0] : val.svg;
            try {
              const wrapper = document.createElement('div');
              wrapper.style.borderRadius = '8px';
              wrapper.style.overflow = 'auto';
              wrapper.style.padding = '0.6rem';
              wrapper.style.background = '#061018';
              const blob = new Blob([svgText], { type: 'image/svg+xml' });
              const url = URL.createObjectURL(blob);
              const obj = document.createElement('object');
              obj.type = 'image/svg+xml';
              obj.data = url;
              obj.style.width = '100%';
              obj.style.border = 'none';
              wrapper.appendChild(obj);
              const dl = document.createElement('a');
              dl.href = url;
              dl.download = key + '.svg' || 'result.svg';
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
              /* fallback to textual */
            }
          }
        } catch (e) {
          /* fallback */
        }

        if (outputs[key]) resultElement.textContent = stringify(outputs[key]);
        else resultElement.textContent = stringify(outputs);
      }

      let outputSelect = document.getElementById('output-select') as HTMLSelectElement | null;
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
          resultElement.parentNode?.insertBefore(outputSelect, resultElement);
        }
        outputSelect.innerHTML = '';
        for (const key of outputKeys) {
          const opt = document.createElement('option');
          opt.value = key;
          opt.textContent = `${key}` + (key === preferred ? ' (preferred)' : '');
          outputSelect.appendChild(opt);
        }
        outputSelect.value = selectedKey || '';
        outputSelect.onchange = (e) => {
          renderOutputForKey((e.target as HTMLSelectElement).value);
        };
      } else {
        if (outputSelect && outputSelect.parentNode)
          outputSelect.parentNode.removeChild(outputSelect);
      }

      renderOutputForKey(selectedKey);
    } catch (error) {
      console.error(error);
      setStatus('Failed to execute workflow.', 'error');
      if (resultElement) resultElement.textContent = String(error);
    } finally {
      runButton.disabled = false;
    }
  });
}

// bootstrap
loadWorkflows()
  .then(() => setStatus('Ready.', 'info'))
  .catch((err) => {
    console.error(err);
    setStatus('Unable to load workflows.', 'error');
  });
