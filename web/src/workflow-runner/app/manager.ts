import { getLfFramework } from '@lf-widgets/framework';
import { APIEndpoints } from '../../types/api/api';
import { WorkflowAPIRunPayload } from '../../types/workflow-runner/api';
import { WorkflowRunnerManager } from '../../types/workflow-runner/manager';
import { WorkflowState, WorkflowStatus } from '../../types/workflow-runner/state';
import { invokeRunAPI } from '../api/run';
import { drawerSection } from '../elements/layout.drawer';
import { headerSection } from '../elements/layout.header';
import { mainSection } from '../elements/layout.main';
import { workflowSection } from '../elements/main.workflow';
import { handleUploadField } from '../utils/common';
import { initState } from './state';

export class LfWorkflowRunnerManager implements WorkflowRunnerManager {
  //#region Private fields
  #API_BASE = '/api';
  #ASSETS_BASE = this.#API_BASE + '/lf-nodes/static/assets/';
  #ASSETS_URL = window.location.origin + this.#ASSETS_BASE;
  #MANAGERS: { lfFramework: ReturnType<typeof getLfFramework> | null } = {
    lfFramework: null,
  };
  #STATE: WorkflowState = initState(document.querySelector('#app'), this);
  //#endregion

  //#region Constructor
  constructor() {
    const assetsUrl = this.#ASSETS_URL;

    this.#MANAGERS.lfFramework = getLfFramework();
    this.#MANAGERS.lfFramework.assets.set(assetsUrl);
    this.#MANAGERS.lfFramework.theme.set('dark');

    this.#initializeElements();
    this.#loadWorkflows()
      .then(() => this.setStatus('ready'))
      .catch((err) => {
        console.error(err);
        this.setStatus('error');
      });
  }
  //#endregion

  //#region Initialize
  #buildLayout() {
    const { ui } = this.#STATE;

    ui.layout._root.appendChild(ui.layout.drawer._root);
    ui.layout._root.appendChild(ui.layout.main._root);
  }
  #initializeElements() {
    const { ui } = this.#STATE;

    // Remove children using a snapshot-safe loop to avoid skipping when removing
    // from a live NodeList. Using firstChild removal is widest-compatible.
    while (ui.layout._root.firstChild) {
      ui.layout._root.removeChild(ui.layout._root.firstChild);
    }

    drawerSection.create(this.#STATE);
    headerSection.create(this.#STATE);
    mainSection.create(this.#STATE);

    workflowSection.create(this.#STATE);

    this.#buildLayout();
  }
  //#endregion

  //#region loadWorkflows
  #loadWorkflows = async () => {
    const response = await fetch(`${this.#API_BASE}${APIEndpoints.Workflows}`);
    if (!response.ok) {
      throw new Error(`Failed to load workflows (${response.status})`);
    }

    const data = await response.json();
    this.#STATE.workflows = Array.isArray(data.workflows) ? data.workflows : [];
    const firstWorkflow = this.#STATE.workflows[0];
    if (!firstWorkflow) {
      throw new Error('No workflows available from the API.');
    }

    this.setWorkflow(firstWorkflow.id);
  };
  //#endregion

  //#region Run Workflow
  collectInputs = async () => {
    const { fields } = this.#STATE.ui.layout.main.workflow;

    const inputs: Record<string, unknown> = {};
    for (const el of fields) {
      const value: unknown = await el.getValue();
      workflowSection.update.fieldWrapper(this.#STATE, el.dataset.name);

      switch (el.tagName.toLowerCase()) {
        case 'lf-toggle':
          inputs[el.dataset.name] = value === 'off' ? false : true;
          break;

        case 'lf-upload':
          try {
            const files = value as File[];
            const paths = await handleUploadField(this.#STATE, el.dataset.name, files);

            inputs[el.dataset.name] = paths.length === 1 ? paths[0] : paths;
          } catch (err) {
            throw err;
          }
          break;

        default:
        case 'lf-textfield':
          inputs[el.dataset.name] = value;
          break;
      }
    }

    return inputs;
  };
  runWorkflow = async () => {
    const { current } = this.#STATE;

    if (!current.workflow) {
      this.setStatus('error', 'No workflow selected.');
      return;
    }

    this.setStatus('running', 'Submitting workflow…');
    let inputs: Record<string, unknown>;
    try {
      inputs = await this.collectInputs();
    } catch (err) {
      console.error('Failed to collect inputs:', err);
      const short =
        err && (err as Error).message ? (err as Error).message : 'Failed to collect inputs';
      const userMessage = `Failed to collect inputs: ${short}`;
      this.setStatus('error', userMessage);
      return;
    }
    const { message, payload, status } = await invokeRunAPI(current.workflow, inputs);
    if (payload.error?.input) {
      workflowSection.update.fieldWrapper(this.#STATE, payload.error.input, 'error');
    }
    this.setStatus(status, message);

    if (status === 'ready') {
      this.setResult(payload);
      this.#STATE.ui.layout.main.workflow.result.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    }
  };
  //#endregion

  //#region Setters
  setResult = (payload: WorkflowAPIRunPayload) => {
    const outputs = payload.history && payload.history.outputs ? payload.history.outputs : {};

    workflowSection.update.result(this.#STATE, outputs);
  };
  setStatus = (status: WorkflowStatus, message?: string) => {
    const { current } = this.#STATE;

    current.status = status;
    workflowSection.update.run(this.#STATE);
    workflowSection.update.status(this.#STATE, message);
  };
  setWorkflow = async (id: string) => {
    const { current } = this.#STATE;

    if (current.workflow === id) {
      return;
    }

    current.workflow = id;
    workflowSection.update.title(this.#STATE);
    workflowSection.update.options(this.#STATE);
  };
  //#endregion
}
