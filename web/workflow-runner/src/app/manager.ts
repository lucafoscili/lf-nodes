import { getLfFramework } from '@lf-widgets/framework';
import { buildAssetsUrl, DEFAULT_THEME } from '../config';
import { createDevPanel } from '../elements/dev.panel';
import { createActionButtonSection } from '../elements/layout.action-button';
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
import { WorkflowManager } from '../types/manager';
import { WorkflowSectionHandle, WorkflowStatus } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { initState } from './state';
import { createWorkflowRunnerStore } from './store';

export class LfWorkflowRunnerManager implements WorkflowManager {
  //#region Initialization
  #FRAMEWORK = getLfFramework();
  #IS_DEBUG = false;
  #SECTIONS: {
    actionButton: ReturnType<typeof createActionButtonSection>;
    dev: ReturnType<typeof createDevPanel>;
    drawer: ReturnType<typeof createDrawerSection>;
    header: ReturnType<typeof createHeaderSection>;
    main: ReturnType<typeof createMainSection>;
    workflow: WorkflowSectionHandle;
  };
  #STORE: WorkflowStore;

  constructor() {
    const { WORKFLOWS_LOAD_FAILED } = DEBUG_MESSAGES;
    const { LOADING_WORKFLOWS } = STATUS_MESSAGES;

    const container = document.querySelector<HTMLDivElement>('#app');
    if (!container) {
      throw new Error('Workflow runner container not found.');
    }

    this.#STORE = createWorkflowRunnerStore(initState(container));
    this.#SECTIONS = {
      actionButton: createActionButtonSection(),
      drawer: createDrawerSection(),
      header: createHeaderSection(),
      main: createMainSection(),
      workflow: createWorkflowSection(),
      dev: createDevPanel(),
    };

    this.#STORE.getState().mutate.manager(this);

    this.#initializeFramework();
    this.#initializeLayout();
    this.#subscribeToState();
    this.setStatus('running', LOADING_WORKFLOWS);
    this.#loadWorkflows().catch((error) => {
      const message = error instanceof Error ? error.message : WORKFLOWS_LOAD_FAILED;
      debugLog(WORKFLOWS_LOAD_FAILED, 'error', {
        message,
        stack: error instanceof Error ? error.stack : undefined,
      });
      this.setStatus('error', message);
    });
  }
  //#endregion

  //#region Internal helpers
  #collectInputs = async (): Promise<Record<string, unknown>> => {
    const state = this.#STORE.getState();
    const { cells } = state.ui.layout.main.workflow;
    const inputs: Record<string, unknown> = {};

    for (const cell of cells) {
      const id = cell.id || '';
      this.#SECTIONS.workflow.setCellStatus(state, id);
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
    const { UPLOAD_COMPLETED, UPLOAD_FAILED, UPLOAD_FAILED_UNEXPECTED } = DEBUG_MESSAGES;
    const { UPLOADING_FILE, FILE_PROCESSING } = STATUS_MESSAGES;

    const files = Array.isArray(rawValue) ? rawValue : (rawValue as File[] | undefined);
    if (!files || files.length === 0) {
      return [];
    }

    try {
      this.setStatus('running', UPLOADING_FILE);
      const { payload } = await uploadWorkflowFiles(files);
      const paths = payload?.paths || [];
      this.setStatus('running', FILE_PROCESSING);
      debugLog(UPLOAD_COMPLETED, 'success', { fieldName, files: paths.length });
      return paths.length === 1 ? paths[0] : paths;
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        this.#SECTIONS.workflow.setCellStatus(this.#STORE.getState(), fieldName, 'error');
        this.setStatus('error', `Upload failed: ${error.payload?.detail || error.message}`);
        debugLog(UPLOAD_FAILED, 'error', {
          fieldName,
          detail: error.payload?.detail || error.message,
        });
      } else {
        debugLog(UPLOAD_FAILED_UNEXPECTED, 'error', {
          fieldName,
          message: (error as Error)?.message ?? null,
        });
      }
      throw error;
    }
  };
  #initializeFramework() {
    const assetsUrl = buildAssetsUrl();

    this.#FRAMEWORK.assets.set(assetsUrl);
    this.#FRAMEWORK.theme.set(DEFAULT_THEME);
  }
  #initializeLayout() {
    const state = this.#STORE.getState();
    const root = state.ui.layout._root;
    if (!root) {
      return;
    }

    while (root.firstChild) {
      root.removeChild(root.firstChild);
    }

    this.#SECTIONS.actionButton.mount(state);
    this.#SECTIONS.drawer.mount(state);
    this.#SECTIONS.header.mount(state);
    this.#SECTIONS.main.mount(state);
    this.#SECTIONS.workflow.mount(state);
    this.#SECTIONS.workflow.render(state);
  }
  #loadWorkflows = async () => {
    const { WORKFLOWS_LOADED } = DEBUG_MESSAGES;

    const workflows = await fetchWorkflowDefinitions();
    if (!workflows || !Object.keys(workflows).length) {
      throw new Error('No workflows available from the API.');
    }

    this.#STORE.getState().mutate.workflows(workflows);
    debugLog(WORKFLOWS_LOADED, 'success', {
      count: workflows.nodes?.length ?? 0,
    });

    this.setWorkflow(workflows.nodes[0].id);
    this.setStatus('ready', WORKFLOWS_LOADED);
  };
  #subscribeToState() {
    this.#STORE.subscribe((state) => {
      this.#SECTIONS.actionButton.render(state);
      this.#SECTIONS.drawer.render(state);
      this.#SECTIONS.header.render(state);
      this.#SECTIONS.main.render(state);
      this.#SECTIONS.workflow.render(state);

      switch (this.#IS_DEBUG) {
        case false:
          this.#SECTIONS.dev.mount(state);
          this.#IS_DEBUG = true;
          this.#SECTIONS.dev.render(state);
          break;
        case true:
          this.#SECTIONS.dev.destroy();
          this.#IS_DEBUG = false;
          break;
      }
    });
  }
  //#endregion

  //#region Workflow execution
  async runWorkflow(): Promise<void> {
    const {
      INPUTS_COLLECTED,
      INPUTS_FAILED,
      WORKFLOW_COMPLETED,
      WORKFLOW_DISPATCHING,
      WORKFLOW_FAILED,
      WORKFLOW_FAILED_UNEXPECTED,
    } = DEBUG_MESSAGES;
    const { SUBMITTING_WORKFLOW } = STATUS_MESSAGES;

    const state = this.#STORE.getState();
    const workflowId = state.current.id;
    if (!workflowId) {
      this.setStatus('error', 'No workflow selected.');
      return;
    }

    this.setStatus('running', SUBMITTING_WORKFLOW);

    let inputs: Record<string, unknown>;
    try {
      inputs = await this.#collectInputs();
      debugLog(INPUTS_COLLECTED, 'informational', {
        workflowId,
        inputKeys: Object.keys(inputs),
      });
    } catch (error) {
      const detail =
        error instanceof WorkflowApiError
          ? error.payload?.detail || error.message
          : (error as Error)?.message || 'Failed to collect inputs.';
      this.setStatus('error', `Failed to collect inputs: ${detail}`);
      debugLog(INPUTS_FAILED, 'error', { workflowId, detail });
      return;
    }

    try {
      debugLog(WORKFLOW_DISPATCHING, 'informational', {
        workflowId,
        inputKeys: Object.keys(inputs),
      });
      const { status, message, payload } = await runWorkflowRequest(workflowId, inputs);

      const runState = this.#STORE.getState();
      runState.mutate.runResult(
        status,
        message,
        payload.history?.outputs ? { ...payload.history.outputs } : null,
      );

      const resultCategory = status === 'error' ? 'error' : 'success';
      debugLog(WORKFLOW_COMPLETED, resultCategory, {
        workflowId,
        wfStatus: status,
        outputs: Object.keys(payload.history?.outputs ?? {}),
      });
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        this.setStatus('error', error.payload?.detail || error.message);
        debugLog(WORKFLOW_FAILED, 'error', {
          workflowId,
          detail: error.payload?.detail || error.message,
          input: error.payload?.error?.input,
        });
        const inputName = error.payload?.error?.input;
        if (inputName) {
          this.#SECTIONS.workflow.setCellStatus(state, inputName, 'error');
        }
      } else {
        this.setStatus('error', 'Unexpected error while running the workflow.');
        debugLog(WORKFLOW_FAILED_UNEXPECTED, 'error', {
          workflowId,
          message: (error as Error)?.message ?? null,
        });
      }
    }
  }
  //#endregion

  //#region State mutators
  setStatus(status: WorkflowStatus, message?: string): void {
    const { STATUS_UPDATED } = DEBUG_MESSAGES;

    const state = this.#STORE.getState();
    state.mutate.status(status, message);
    const category =
      status === 'error' ? 'error' : status === 'ready' ? 'success' : 'informational';
    debugLog(STATUS_UPDATED, category, {
      status,
      message: message ?? null,
    });
  }
  setWorkflow(id: string): void {
    const { WORKFLOW_SELECTED } = DEBUG_MESSAGES;

    const state = this.#STORE.getState();
    if (state.current.id === id) {
      return;
    }

    state.mutate.workflow(id);
    debugLog(WORKFLOW_SELECTED, 'informational', { id });
  }
  //#endregion
}
