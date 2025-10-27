import { getLfFramework } from '@lf-widgets/framework';
import { buildAssetsUrl, DEFAULT_THEME } from '../config';
import { workflowDispatcher } from '../dispatchers/workflow';
import { createActionButtonSection } from '../elements/layout.action-button';
import { createDevSection } from '../elements/layout.dev';
import { createDrawerSection } from '../elements/layout.drawer';
import { createHeaderSection } from '../elements/layout.header';
import { createMainSection } from '../elements/layout.main';
import { createNotificationsSection } from '../elements/layout.notifications';
import { WORKFLOW_CLASSES } from '../elements/main.inputs';
import { fetchWorkflowDefinitions, getRunStatus } from '../services/workflow-service';
import {
  WorkflowCellInputId,
  WorkflowCellsInputContainer,
  WorkflowCellsOutputContainer,
  WorkflowCellType,
  WorkflowRunStatusResponse,
} from '../types/api';
import { WorkflowDispatchers, WorkflowManager, WorkflowUIItem } from '../types/manager';
import { WorkflowCellStatus, WorkflowSectionController, WorkflowUICells } from '../types/section';
import { WorkflowStore } from '../types/state';
import { parseCount } from '../utils/common';
import { NOTIFICATION_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import { initState } from './state';
import { createWorkflowRunnerStore } from './store';

export class LfWorkflowRunnerManager implements WorkflowManager {
  //#region Initialization
  #APP_ROOT: HTMLDivElement;
  #DISPATCHERS: WorkflowDispatchers;
  #FRAMEWORK = getLfFramework();
  #SECTIONS: {
    actionButton: WorkflowSectionController;
    dev: WorkflowSectionController;
    drawer: WorkflowSectionController;
    header: WorkflowSectionController;
    main: WorkflowSectionController;
    notifications: WorkflowSectionController;
  };
  #STORE: WorkflowStore;
  #UI_REGISTRY = new WeakMap();

  constructor() {
    const {
      ERROR_FETCHING_WORKFLOWS,
      IDLE_WORKFLOWS_LOADED,
      RUNNING_INITIALIZING,
      RUNNING_LOADING_WORKFLOWS,
    } = STATUS_MESSAGES;
    const { WORKFLOWS_LOAD_FAILED } = NOTIFICATION_MESSAGES;

    this.#APP_ROOT = document.querySelector<HTMLDivElement>('#app');
    this.#STORE = createWorkflowRunnerStore(initState());
    this.#DISPATCHERS = {
      runWorkflow: () => workflowDispatcher(this.#STORE),
    };
    this.#SECTIONS = {
      actionButton: createActionButtonSection(this.#STORE),
      dev: createDevSection(this.#STORE),
      drawer: createDrawerSection(this.#STORE),
      header: createHeaderSection(this.#STORE),
      main: createMainSection(this.#STORE),
      notifications: createNotificationsSection(this.#STORE),
    };

    const state = this.#STORE.getState();

    state.mutate.manager(this);

    this.#initializeFramework();
    this.#initializeLayout();

    state.mutate.status('running', RUNNING_INITIALIZING);
    this.#subscribeToState();

    state.mutate.status('running', RUNNING_LOADING_WORKFLOWS);
    this.#loadWorkflows()
      .catch((error) => {
        state.mutate.notifications.add({
          id: performance.now().toString(),
          message: error instanceof Error ? error.message : WORKFLOWS_LOAD_FAILED,
          status: 'danger',
        });
        state.mutate.status('error', ERROR_FETCHING_WORKFLOWS);
      })
      .then(() => {
        state.mutate.status('idle', IDLE_WORKFLOWS_LOADED);
      });

    this.#startQueuePolling();
  }
  //#endregion

  //#region Internal helpers
  #initializeFramework() {
    const assetsUrl = buildAssetsUrl();

    this.#FRAMEWORK.assets.set(assetsUrl);
    this.#FRAMEWORK.theme.set(DEFAULT_THEME);
  }
  #initializeLayout() {
    const state = this.#STORE.getState();

    while (this.#APP_ROOT.firstChild) {
      this.#APP_ROOT.removeChild(this.#APP_ROOT.firstChild);
    }

    this.#SECTIONS.actionButton.mount();
    this.#SECTIONS.drawer.mount();
    this.#SECTIONS.header.mount();
    this.#SECTIONS.main.mount();
    this.#SECTIONS.notifications.mount();

    if (state.isDebug) {
      this.#SECTIONS.dev.mount();
      this.#SECTIONS.dev.render();
    }
  }
  #loadWorkflows = async () => {
    const { NO_WORKFLOWS_AVAILABLE } = NOTIFICATION_MESSAGES;

    const state = this.#STORE.getState();

    const workflows = await fetchWorkflowDefinitions();
    if (!workflows || !Object.keys(workflows).length) {
      state.mutate.notifications.add({
        id: performance.now().toString(),
        message: NO_WORKFLOWS_AVAILABLE,
        status: 'danger',
      });
    }

    state.mutate.workflows(workflows);

    const firstWorkflow = workflows.nodes?.[0];
    if (firstWorkflow?.id) {
      state.mutate.workflow(firstWorkflow.id);
    }
  };
  #startQueuePolling() {
    setInterval(async () => {
      try {
        const resp = await fetch('/queue');
        if (!resp.ok) {
          throw new Error('Failed to fetch queue status');
        }

        const state = this.#STORE.getState();

        const { queue_running, queue_pending } = (await resp.json()) as {
          queue_pending: unknown;
          queue_running: unknown;
        };

        const qPending = parseCount(queue_pending);
        const qRunning = parseCount(queue_running);
        const busy = qPending + qRunning;

        const prev = state.queuedJobs ?? -1;
        if (busy !== prev) {
          state.mutate.queuedJobs(busy);
        }
      } catch (e) {
        const state = this.#STORE.getState();

        try {
          const prev = state.queuedJobs ?? -1;
          if (prev !== -1) {
            state.mutate.queuedJobs(-1);
          }
        } catch (err) {}
      }
    }, 750);
  }
  #beginRunPolling(runId: string) {
    const state = this.#STORE.getState();
    this.#stopRunPolling();

    let isPolling = false;
    const poll = async () => {
      if (isPolling) {
        return;
      }

      const currentState = this.#STORE.getState();
      if (currentState.currentRunId !== runId) {
        return;
      }

      isPolling = true;
      try {
        const response = await getRunStatus(runId);
        this.#handleRunStatusResponse(response);
      } catch (error) {
        this.#handleRunPollingError(error);
      } finally {
        isPolling = false;
      }
    };

    poll();
    const timerId = window.setInterval(poll, 3000);
    state.mutate.pollingTimer(Number(timerId));
  }
  #stopRunPolling() {
    const state = this.#STORE.getState();
    const timerId = state.pollingTimer;
    if (typeof timerId === 'number') {
      window.clearInterval(timerId);
      state.mutate.pollingTimer(null);
    }
  }
  #handleRunPollingError(error: unknown) {
    const state = this.#STORE.getState();
    const detail = error instanceof Error ? error.message : STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW;

    state.mutate.status('error', STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW);
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message: `${NOTIFICATION_MESSAGES.WORKFLOW_STATUS_FAILED}: ${detail}`,
      status: 'danger',
    });
    state.mutate.runId(null);
    this.#stopRunPolling();
  }
  #handleRunStatusResponse(response: WorkflowRunStatusResponse) {
    const state = this.#STORE.getState();
    const { status } = response;

    switch (status) {
      case 'pending':
      case 'running':
        if (
          state.current.status !== 'running' ||
          state.current.message !== STATUS_MESSAGES.RUNNING_POLLING_WORKFLOW
        ) {
          state.mutate.status('running', STATUS_MESSAGES.RUNNING_POLLING_WORKFLOW);
        }
        break;
      case 'succeeded':
        this.#handleRunSuccess(response);
        break;
      case 'failed':
        this.#handleRunFailure(response);
        break;
      case 'cancelled':
        this.#handleRunCancellation(response);
        break;
      default:
        break;
    }

    if (status === 'succeeded' || status === 'failed' || status === 'cancelled') {
      this.#stopRunPolling();
      state.mutate.runId(null);
    }
  }
  #handleRunSuccess(response: WorkflowRunStatusResponse) {
    const state = this.#STORE.getState();
    const outputs = this.#extractRunOutputs(response);

    state.mutate.results(outputs);
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message: NOTIFICATION_MESSAGES.WORKFLOW_COMPLETED,
      status: 'success',
    });
    state.mutate.status('idle', STATUS_MESSAGES.IDLE);
  }
  #handleRunFailure(response: WorkflowRunStatusResponse) {
    const state = this.#STORE.getState();
    const payload = response.result?.body?.payload;
    const detail =
      payload?.detail ||
      payload?.error?.message ||
      response.error ||
      STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW;
    const outputs = this.#extractRunOutputs(response);

    state.mutate.results(outputs);
    if (payload?.error?.input) {
      this.#setInputStatus(payload.error.input, 'error');
    }
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message: `Workflow run failed: ${detail}`,
      status: 'danger',
    });
    state.mutate.status('error', STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW);
  }
  #handleRunCancellation(response: WorkflowRunStatusResponse) {
    const state = this.#STORE.getState();
    const outputs = this.#extractRunOutputs(response);
    const message = response.error || NOTIFICATION_MESSAGES.WORKFLOW_CANCELLED;

    state.mutate.results(outputs);
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message,
      status: 'warning',
    });
    state.mutate.status('idle', STATUS_MESSAGES.IDLE);
  }
  #extractRunOutputs(response: WorkflowRunStatusResponse) {
    const outputs = response.result?.body?.payload?.history?.outputs;
    if (!outputs) {
      return null;
    }
    return { ...outputs };
  }
  #setInputStatus(inputId: string, status: WorkflowCellStatus) {
    const elements = this.uiRegistry.get();
    const cells = (elements?.[WORKFLOW_CLASSES.cells] as WorkflowUICells) || [];

    const cell = cells.find((el) => el.id === inputId);
    const wrapper = cell?.parentElement;
    if (wrapper) {
      wrapper.dataset.status = status;
    }
  }
  #subscribeToState() {
    const st = this.#STORE.getState();
    let lastCurrentMessage = st.current.message;
    let lastCurrentStatus = st.current.status;
    let lastDebug = st.isDebug;
    let lastId = st.current.id;
    let lastNotificationsCount = st.notifications?.length ?? 0;
    let lastQueued = st.queuedJobs ?? -1;
    let lastResults = st.results;
    let lastRunId = st.currentRunId;
    let lastWorkflowsCount = st.workflows?.nodes?.length ?? 0;

    let scheduled = false;
    const needs = {
      header: false,
      dev: false,
      drawer: false,
      main: false,
      actionButton: false,
      notifications: false,
    };

    this.#STORE.subscribe((state) => {
      const { current, isDebug, queuedJobs, workflows } = state;
      const { message, status } = current;

      if (state.currentRunId !== lastRunId) {
        if (state.currentRunId) {
          this.#beginRunPolling(state.currentRunId);
        } else {
          this.#stopRunPolling();
        }
        lastRunId = state.currentRunId;
      }

      if (current.id !== lastId || state.results !== lastResults) {
        needs.main = true;
        lastId = current.id;
        lastResults = state.results;
      }

      if (message !== lastCurrentMessage || status !== lastCurrentStatus) {
        needs.actionButton = true;
        needs.header = true;
        lastCurrentMessage = message;
        lastCurrentStatus = status;
      }

      if (state.notifications.length !== lastNotificationsCount) {
        needs.notifications = true;
        lastNotificationsCount = state.notifications.length;
      }

      if (queuedJobs !== lastQueued) {
        needs.header = true;
        lastQueued = queuedJobs;
      }

      if (workflows?.nodes?.length !== lastWorkflowsCount) {
        needs.drawer = true;
        lastWorkflowsCount = workflows?.nodes?.length ?? 0;
      }

      if (isDebug !== lastDebug) {
        needs.dev = true;
        needs.drawer = true;
        lastDebug = isDebug;
      }

      if (!scheduled) {
        scheduled = true;
        requestAnimationFrame(() => {
          scheduled = false;

          const sections = this.#SECTIONS;
          for (const sectionKey in needs) {
            const need = needs[sectionKey as keyof typeof needs];
            const section = sections[sectionKey as keyof typeof sections];
            if (need) {
              switch (sectionKey) {
                case 'dev':
                  if (isDebug) {
                    section.mount();
                    section.render();
                  } else {
                    section.destroy();
                  }
                  break;
                default:
                  section.render();
                  break;
              }
            }
          }

          Object.keys(needs).forEach((k) => (needs[k] = false));
        });
      }
    });
  }
  //#endregion

  //#region Getters
  getAppRoot() {
    return this.#APP_ROOT;
  }
  getDispatchers() {
    return this.#DISPATCHERS;
  }
  getStore() {
    return this.#STORE;
  }
  //#endregion

  //#region UI registry
  uiRegistry = {
    delete: () => {
      const elements = this.#UI_REGISTRY.get(this);
      if (elements) {
        for (const elementId in elements) {
          const element = elements[elementId];
          if (element && typeof element === 'object' && 'remove' in element) {
            (element as HTMLElement).remove();
          }
        }
      }
      this.#UI_REGISTRY.delete(this);
    },
    get: () => {
      return this.#UI_REGISTRY.get(this);
    },
    remove: (elementId: string) => {
      const elements = this.#UI_REGISTRY.get(this);
      if (elements && elements[elementId]) {
        const element = elements[elementId];
        if (element && typeof element === 'object' && 'remove' in element) {
          (element as HTMLElement).remove();
        }
        delete elements[elementId];
        this.#UI_REGISTRY.set(this, elements);
      }
    },
    set: (elementId: string, element: WorkflowUIItem) => {
      const elements = this.#UI_REGISTRY.get(this) || {};
      elements[elementId] = element;
      this.#UI_REGISTRY.set(this, elements);
    },
  };
  //#endregion

  //#region Workflow
  workflow = {
    cells: <T extends WorkflowCellType>(type: T) => {
      const workflow = this.workflow.current();
      const section = workflow?.children?.find((child) => child.id.endsWith(`:${type}s`));
      return (section?.cells || {}) as T extends WorkflowCellInputId
        ? WorkflowCellsInputContainer
        : WorkflowCellsOutputContainer;
    },
    current: () => {
      const { current, workflows } = this.#STORE.getState();
      return workflows?.nodes?.find((node) => node.id === current.id) || null;
    },
    description: () => {
      const workflow = this.workflow.current();
      return workflow?.description || '';
    },
    title: () => {
      const workflow = this.workflow.current();
      const str =
        typeof workflow?.value === 'string' ? workflow.value : String(workflow?.value || '');
      return str || 'No workflow selected';
    },
  };
  //#endregion
}
