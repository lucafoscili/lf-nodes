import '@lf-widgets/core/dist/lf-core/lf-core.esm.js';
import { getLfFramework } from '@lf-widgets/framework';
import { LfFramework } from '@lf-widgets/framework/dist/types/lf-framework/lf-framework';

export class LfWorkflowApp {
  #API_BASE = '/api/lf-nodes';
  #ASSETS_BASE = this.#API_BASE + '/static/assets/';
  #ASSETS_URL = window.location.origin + this.#ASSETS_BASE;
  #APP = document.querySelector('#app') as HTMLDivElement;
  #FIELD_RENDERERS: Map<string, { element: HTMLElement; getValue: () => Promise<any> }> = new Map();
  #MANAGERS: { lfFramework: LfFramework | null } = {
    lfFramework: null,
  };
  #STATE = {
    ui: {
      buttons: {
        run: null as HTMLLfButtonElement | null,
      },
      fields: {
        workflow: null as HTMLSelectElement | null,
      },
      labels: {
        workflow: null as HTMLLabelElement | null,
      },
      sections: {
        fields: null as HTMLElement | null,
        result: null as HTMLElement | null,
        status: null as HTMLElement | null,
        workflow: null as HTMLElement | null,
      },
      title: null as HTMLHeadingElement | null,
    },
    workflows: [] as any[],
  };
  #STRINGIFY = (value: any) => JSON.stringify(value, null, 2);

  constructor() {
    const assetsUrl = this.#ASSETS_URL;
    this.#MANAGERS.lfFramework = getLfFramework();
    this.#MANAGERS.lfFramework.assets.set(assetsUrl);
    this.#MANAGERS.lfFramework.theme.set('dark');

    this.#initializeElements();
    this.#loadWorkflows()
      .then(() => this.set.status('Ready.', 'info'))
      .catch((err) => {
        console.error(err);
        this.set.status('Unable to load workflows.', 'error');
      });
  }

  #initializeElements() {
    const { ui } = this.#STATE;
    const { buttons, fields, labels, sections } = ui;

    ui.title = document.createElement('h1');
    ui.title.textContent = 'LF Nodes — Workflow Runner';

    sections.workflow = document.createElement('section');
    labels.workflow = document.createElement('label');
    fields.workflow = document.createElement('select');
    sections.workflow.className = 'field-container';
    labels.workflow.htmlFor = 'workflow-select';
    labels.workflow.textContent = 'Workflow';
    fields.workflow.id = 'workflow-select';
    fields.workflow.addEventListener('change', (event) => {
      // @ts-ignore
      renderFields(event.target.value);
    });
    sections.fields = document.createElement('section');
    sections.fields.id = 'fields';
    sections.fields.className = 'field-container';

    buttons.run = document.createElement('lf-button');
    buttons.run.id = 'run-button';
    buttons.run.lfAriaLabel = 'Run workflow';
    buttons.run.lfLabel = 'Run workflow';
    buttons.run.addEventListener('click', async () => {
      const { ui, workflows } = this.#STATE;
      const { buttons, fields, sections } = ui;

      const workflowId = fields.workflow.value;
      if (!workflowId) {
        this.set.status('Select a workflow to continue.', 'warn');
        return;
      }

      buttons.run.lfUiState = 'disabled';
      this.set.status('Submitting workflow…', 'info');
      this.set.result('');

      const inputs: Record<string, any> = {};

      for (const [name, renderer] of this.#FIELD_RENDERERS.entries()) {
        const val = await renderer.getValue();
        if (val instanceof File) {
          this.set.status('Uploading file…', 'info');
          const form = new FormData();
          form.append('file', val, val.name);
          try {
            const uploadResp = await fetch(`${this.#API_BASE}/upload`, {
              method: 'POST',
              body: form,
            });
            if (!uploadResp.ok) throw new Error(await uploadResp.text());
            const uploadJson = await uploadResp.json();
            inputs[name] = uploadJson.path;
          } catch (err) {
            this.set.status('File upload failed.', 'error');
            sections.result.textContent = String(err);
            buttons.run.lfUiState = 'primary';
            return;
          }
        } else {
          inputs[name] = val;
        }
      }

      try {
        const response = await fetch(`${this.#API_BASE}/run`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ workflowId, inputs }),
        });

        const payload = await response.json();
        if (!response.ok) {
          this.set.status(payload.detail ?? 'Workflow execution failed.', 'error');
          sections.result.textContent = this.#STRINGIFY(payload);
          return;
        }

        this.set.status(`Workflow completed with status: ${payload.status}`, 'info');

        const outputs = payload.history && payload.history.outputs ? payload.history.outputs : {};
        const outputKeys = Object.keys(outputs || {});
        const preferred = payload.preferred_output;
        let selectedKey: string | null = null;
        if (preferred && outputs[preferred]) {
          selectedKey = preferred;
        } else if (outputKeys.length > 0) {
          selectedKey = outputKeys[0];
        }

        const renderOutputForKey = (key: string | null) => {
          this.set.result('');
          if (!key || !outputs[key]) {
            sections.result.textContent = this.#STRINGIFY(outputs);
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
                const nonce = Date.now();
                const url = `/view?filename=${encodeURIComponent(
                  filename,
                )}&type=${encodeURIComponent(type)}&subfolder=${encodeURIComponent(
                  subfolder,
                )}&nonce=${nonce}`;
                const img = document.createElement('img');
                img.src = url;
                img.style.maxWidth = '100%';
                img.style.borderRadius = '8px';
                img.alt = filename;
                img.title = filename;
                sections.result.appendChild(img);
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
                const providedName =
                  (val && typeof val.filename === 'string' && val.filename) ||
                  (val && typeof val.name === 'string' && val.name) ||
                  (Array.isArray(val.svg) && val.svgFilename) ||
                  null;
                const imageFilename =
                  (val &&
                    val.images &&
                    Array.isArray(val.images) &&
                    val.images[0] &&
                    (val.images[0].filename || val.images[0].name)) ||
                  null;
                let downloadName =
                  providedName || imageFilename || (key ? `${key}.svg` : 'result.svg');
                if (!downloadName.toLowerCase().endsWith('.svg')) downloadName += '.svg';
                dl.download = downloadName;
                dl.textContent = 'Download SVG';
                dl.style.display = 'inline-block';
                dl.style.marginTop = '0.6rem';
                dl.style.padding = '0.45rem 0.65rem';
                dl.style.background = '#1f2533';
                dl.style.border = '1px solid #39435a';
                dl.style.borderRadius = '8px';
                dl.style.color = 'white';
                wrapper.appendChild(dl);
                sections.result.appendChild(wrapper);
                return;
              } catch (e) {
                /* fallback to textual */
              }
            }
          } catch (e) {
            /* fallback */
          }

          if (outputs[key]) {
            sections.result.textContent = this.#STRINGIFY(outputs[key]);
          } else {
            sections.result.textContent = this.#STRINGIFY(outputs);
          }
        };

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
            sections.result.parentNode?.insertBefore(outputSelect, sections.result);
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
        this.set.status('Failed to execute workflow.', 'error');
        if (sections.result) {
          sections.result.textContent = String(error);
        }
      } finally {
        buttons.run.lfUiState = 'primary';
      }
    });

    sections.status = document.createElement('div');
    sections.status.id = 'status';
    sections.status.dataset.tone = 'info';

    sections.result = document.createElement('pre');
    sections.result.id = 'result';

    this.#APP.childNodes.forEach((n) => n.remove());
    this.#APP.appendChild(ui.title);
    sections.workflow.appendChild(labels.workflow);
    sections.workflow.appendChild(fields.workflow);
    this.#APP.appendChild(sections.workflow);
    this.#APP.appendChild(sections.fields);
    this.#APP.appendChild(buttons.run);
    this.#APP.appendChild(sections.status);
    this.#APP.appendChild(sections.result);
  }

  //#region loadWorkflows
  #loadWorkflows = async () => {
    const { ui } = this.#STATE;
    const { fields } = ui;

    const createFieldRenderer = (field: any) => {
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
    };

    const renderFields = async (workflowId: string) => {
      const { ui } = this.#STATE;
      const { sections } = ui;

      this.#FIELD_RENDERERS.clear();
      sections.fields.textContent = '';

      const workflow = this.#STATE.workflows.find((wf) => wf.id === workflowId);
      if (!workflow) {
        return;
      }
      for (const field of workflow.fields ?? []) {
        const renderer = createFieldRenderer(field);
        sections.fields.appendChild(renderer.element);
        this.#FIELD_RENDERERS.set(field.name, renderer);
      }
    };

    const response = await fetch(`${this.#API_BASE}/workflows`);
    if (!response.ok) {
      throw new Error(`Failed to load workflows (${response.status})`);
    }

    const data = await response.json();
    this.#STATE.workflows = Array.isArray(data.workflows) ? data.workflows : [];

    fields.workflow.innerHTML = '';

    this.#STATE.workflows.forEach((wf, index) => {
      const option = document.createElement('option');
      option.value = wf.id;
      option.textContent = wf.label ?? wf.id;

      if (index === 0) {
        option.selected = true;
      }

      fields.workflow.appendChild(option);
    });

    if (this.#STATE.workflows.length > 0) {
      await renderFields(this.#STATE.workflows[0].id);
    }
  };
  //#endregion

  //#region Setters
  set = {
    result: (message: string | null, tone: string = 'info') => {
      const { ui } = this.#STATE;
      const { sections } = ui;

      sections.result.textContent = message ?? '';
      sections.result.dataset.tone = tone;
    },
    status: (message: string | null, tone: string = 'info') => {
      const { ui } = this.#STATE;
      const { sections } = ui;

      sections.status.textContent = message ?? '';
      sections.status.dataset.tone = tone;
    },
  };
  //#endregion
}

//#region Bootstrap
const hasComfyApp = typeof window !== 'undefined' && typeof (window as any).LGraph !== 'undefined';
if (!hasComfyApp) {
  new LfWorkflowApp();
}
//#endregion
