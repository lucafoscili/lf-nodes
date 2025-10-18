import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowRunnerManager } from '../../types/workflow-runner/manager';
import { WorkflowStatus } from '../../types/workflow-runner/state';
import {
  fetchWorkflowDefinitions,
  runWorkflowRequest,
  uploadWorkflowFiles,
  WorkflowApiError,
} from '../services/workflow-service';
import { DEFAULT_STATUS_MESSAGES, DEFAULT_THEME, buildAssetsUrl } from '../config';
import { createDrawerSection } from '../elements/layout.drawer';
import { createHeaderSection } from '../elements/layout.header';
import { createMainSection } from '../elements/layout.main';
import { createWorkflowSection, WorkflowSectionHandle } from '../elements/main.workflow';
import { createWorkflowRunnerStore, WorkflowRunnerStore } from './store';
import { initState } from './state';

export class LfWorkflowRunnerManager implements WorkflowRunnerManager {
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

    this.#store.setState((state) => {
      state.manager = this;
    });

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
      const response = await runWorkflowRequest(workflowId, inputs);
      this.#store.setState((draft) => {
        draft.current.status = response.status;
        draft.current.message = response.message;
        draft.current.preferredOutput = response.payload.preferred_output ?? null;
        draft.results = response.payload.history?.outputs
          ? { ...response.payload.history.outputs }
          : null;
      });
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        this.#store.setState((draft) => {
          draft.current.status = 'error';
          draft.current.message = error.message;
        });
        const inputName = error.payload?.error?.input;
        if (inputName) {
          this.#sections.workflow.setFieldStatus(this.#store.getState(), inputName, 'error');
        }
      } else {
        console.error('Unexpected error while running workflow:', error);
        this.setStatus('error', 'Unexpected error while running the workflow.');
      }
    }
  }

  setStatus(status: WorkflowStatus, message?: string): void {
    this.#store.setState((draft) => {
      draft.current.status = status;
      draft.current.message = message ?? DEFAULT_STATUS_MESSAGES[status];
    });
  }

  async setWorkflow(id: string): Promise<void> {
    const state = this.#store.getState();
    if (state.current.workflow === id) {
      return;
    }

    this.#store.setState((draft) => {
      draft.current.workflow = id;
      draft.current.preferredOutput = null;
      draft.results = null;
    });
  }

  //#region Internal helpers
  #collectInputs = async (): Promise<Record<string, unknown>> => {
    const state = this.#store.getState();
    const { fields } = state.ui.layout.main.workflow;
    const inputs: Record<string, unknown> = {};

    for (const element of fields) {
      const fieldName = element.dataset.name || '';
      if (!fieldName) {
        continue;
      }

      this.#sections.workflow.setFieldStatus(state, fieldName);
      const value: unknown = await element.getValue();
      switch (element.tagName.toLowerCase()) {
        case 'lf-toggle':
          inputs[fieldName] = value === 'off' ? false : true;
          break;
        case 'lf-upload':
          inputs[fieldName] = await this.#handleUploadField(fieldName, value);
          break;
        default:
          inputs[fieldName] = value;
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
        this.#sections.workflow.setFieldStatus(this.#store.getState(), fieldName, 'error');
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

  #subscribeToState() {
    this.#store.subscribe((state) => {
      this.#sections.workflow.render(state);
    });
  }

  #loadWorkflows = async () => {
    const workflows = await fetchWorkflowDefinitions();
    if (!workflows.length) {
      throw new Error('No workflows available from the API.');
    }

    this.#store.setState((draft) => {
      draft.workflows = workflows;
    });

    await this.setWorkflow(workflows[0].id);
    this.setStatus('ready', 'Workflows loaded.');
  };
  //#endregion
}
