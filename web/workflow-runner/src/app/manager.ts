import { getLfFramework } from '@lf-widgets/framework';
import { buildAssetsUrl, DEFAULT_THEME } from '../config';
import { createDrawerSection } from '../elements/layout.drawer';
import { createHeaderSection } from '../elements/layout.header';
import { createMainSection } from '../elements/layout.main';
import { createWorkflowSection } from '../elements/main.workflow';
import {
  fetchWorkflowDefinitions,
  runWorkflowRequest,
  uploadWorkflowFiles,
  WorkflowApiError,
} from '../services/workflow-service';
import { WorkflowRunnerManager } from '../types/manager';
import { WorkflowSectionHandle } from '../types/section';
import { WorkflowRunnerStore, WorkflowStatus } from '../types/state';
import { initState } from './state';
import { createWorkflowRunnerStore } from './store';

export class LfWorkflowRunnerManager implements WorkflowRunnerManager {
  //#region Initialization
  #framework = getLfFramework();
  #store: WorkflowRunnerStore;
  #sections: {
    drawer: ReturnType<typeof createDrawerSection>;
    header: ReturnType<typeof createHeaderSection>;
    main: ReturnType<typeof createMainSection>;
    workflow: WorkflowSectionHandle;
  };

  constructor() {
    const container = document.querySelector<HTMLDivElement>('#app');
    if (!container) {
      throw new Error('Workflow runner container not found.');
    }

    this.#store = createWorkflowRunnerStore(initState(container));
    this.#sections = {
      drawer: createDrawerSection(),
      header: createHeaderSection(),
      main: createMainSection(),
      workflow: createWorkflowSection(),
    };

    this.#store.setState((state) => ({
      ...state,
      manager: this,
    }));

    this.#initializeFramework();
    this.#initializeLayout();
    this.#subscribeToState();
    this.setStatus('running', 'Loading workflows...');
    this.#loadWorkflows().catch((error) => {
      console.error('Failed to load workflows:', error);
      const message = error instanceof Error ? error.message : 'Failed to load workflows.';
      this.setStatus('error', message);
    });
  }
  //#endregion

  //#region Internal helpers
  #collectInputs = async (): Promise<Record<string, unknown>> => {
    const state = this.#store.getState();
    const { cells } = state.ui.layout.main.workflow;
    const inputs: Record<string, unknown> = {};

    for (const cell of cells) {
      const id = cell.id || '';
      this.#sections.workflow.setCellStatus(state, id);
      const value: unknown = await cell.getValue();

      switch (cell.tagName.toLowerCase()) {
        case 'lf-toggle':
          inputs[id] = value === 'off' ? false : true;
          break;
        case 'lf-upload':
          inputs[id] = await this.#handleUploadField(id, value);
          break;
        default:
          inputs[id] = value;
      }
    }

    return inputs;
  };
  #handleUploadField = async (fieldName: string, rawValue: unknown) => {
    const files = Array.isArray(rawValue) ? rawValue : (rawValue as File[] | undefined);
    if (!files || files.length === 0) {
      return [];
    }

    try {
      this.setStatus('running', 'Uploading file...');
      const { payload } = await uploadWorkflowFiles(files);
      const paths = payload?.paths || [];
      this.setStatus('running', 'File uploaded, processing...');
      return paths.length === 1 ? paths[0] : paths;
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        this.#sections.workflow.setCellStatus(this.#store.getState(), fieldName, 'error');
        this.setStatus('error', `Upload failed: ${error.payload?.detail || error.message}`);
      }
      throw error;
    }
  };
  #initializeFramework() {
    const assetsUrl = buildAssetsUrl();
    this.#framework.assets.set(assetsUrl);
    this.#framework.theme.set(DEFAULT_THEME);
  }
  #initializeLayout() {
    const state = this.#store.getState();
    const root = state.ui.layout._root;
    if (!root) {
      return;
    }

    while (root.firstChild) {
      root.removeChild(root.firstChild);
    }

    this.#sections.drawer.mount(state);
    this.#sections.header.mount(state);
    this.#sections.main.mount(state);
    this.#sections.workflow.mount(state);
    this.#sections.workflow.render(state);
  }
  #loadWorkflows = async () => {
    const workflows = await fetchWorkflowDefinitions();
    if (!workflows || !Object.keys(workflows).length) {
      throw new Error('No workflows available from the API.');
    }

    this.#store.setState((state) => ({
      ...state,
      workflows,
    }));

    this.setWorkflow(workflows.nodes[0].id);
    this.setStatus('ready', 'Workflows loaded.');
  };
  #subscribeToState() {
    this.#store.subscribe((state) => {
      this.#sections.drawer.render(state);
      this.#sections.header.render(state);
      this.#sections.main.render(state);
      this.#sections.workflow.render(state);
    });
  }
  //#endregion

  //#region Workflow execution
  async runWorkflow(): Promise<void> {
    const state = this.#store.getState();
    const workflowId = state.current.workflow;
    if (!workflowId) {
      this.setStatus('error', 'No workflow selected.');
      return;
    }

    this.setStatus('running', 'Submitting workflow...');

    let inputs: Record<string, unknown>;
    try {
      inputs = await this.#collectInputs();
    } catch (error) {
      console.error('Failed to collect inputs:', error);
      const detail =
        error instanceof WorkflowApiError
          ? error.payload?.detail || error.message
          : (error as Error)?.message || 'Failed to collect inputs.';
      this.setStatus('error', `Failed to collect inputs: ${detail}`);
      return;
    }

    try {
      const { status, message, payload } = await runWorkflowRequest(workflowId, inputs);

      const state = this.#store.getState();
      state.mutate.runResult(
        status,
        message,
        payload.preferred_output ?? null,
        payload.history?.outputs ? { ...payload.history.outputs } : null,
      );
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        const state = this.#store.getState();
        state.mutate.status('error', error.message);
        const inputName = error.payload?.error?.input;
        if (inputName) {
          this.#sections.workflow.setCellStatus(state, inputName, 'error');
        }
      } else {
        console.error('Unexpected error while running workflow:', error);
        this.setStatus('error', 'Unexpected error while running the workflow.');
      }
    }
  }
  //#endregion

  //#region State mutators
  setStatus(status: WorkflowStatus, message?: string): void {
    const state = this.#store.getState();
    state.mutate.status(status, message);
  }

  setWorkflow(id: string): void {
    const state = this.#store.getState();
    if (state.current.workflow === id) {
      return;
    }

    state.mutate.workflow(id);
  }
  //#endregion
}
