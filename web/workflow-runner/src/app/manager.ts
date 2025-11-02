import { getLfFramework } from '@lf-widgets/framework';
import { buildAssetsUrl, DEFAULT_THEME } from '../config';
import { workflowDispatcher } from '../dispatchers/workflow';
import { createActionButtonSection } from '../elements/layout.action-button';
import { createDevSection } from '../elements/layout.dev';
import { createDrawerSection } from '../elements/layout.drawer';
import { createHeaderSection } from '../elements/layout.header';
import { createMainSection } from '../elements/layout.main';
import { createNotificationsSection } from '../elements/layout.notifications';
import { INPUTS_CLASSES } from '../elements/main.inputs';
import {
  fetchWorkflowDefinitions,
  fetchWorkflowJSON,
  WorkflowApiError,
} from '../services/workflow-service';
import {
  WorkflowCellInputId,
  WorkflowCellsInputContainer,
  WorkflowCellsOutputContainer,
  WorkflowCellType,
} from '../types/api';
import { RunRecord } from '../types/client';
import {
  RoutingController,
  WorkflowDispatchers,
  WorkflowManager,
  WorkflowUIItem,
} from '../types/manager';
import { WorkflowCellStatus, WorkflowSectionController, WorkflowUICells } from '../types/section';
import { WorkflowRunEntry, WorkflowStore, WorkflowView } from '../types/state';
import { recordToUI } from '../utils/common';
import { NOTIFICATION_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import { WorkflowRunnerClient } from './client';
import { createRoutingController } from './routing';
import { changeView, resolveMainSections } from './sections';
import { initState } from './state';
import { createWorkflowRunnerStore } from './store';
import { addNotification, ensureActiveRun, selectRun, upsertRun } from './store-actions';

export class LfWorkflowRunnerManager implements WorkflowManager {
  //#region Initialization
  #APP_ROOT: HTMLDivElement;
  #CLIENT: WorkflowRunnerClient;
  #DISPATCHERS: WorkflowDispatchers;
  #FRAMEWORK = getLfFramework();
  #ROUTING: RoutingController;
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
  #WORKFLOW_NAMES = new Map<string, string>();

  constructor() {
    const {
      ERROR_FETCHING_WORKFLOWS,
      IDLE_WORKFLOWS_LOADED,
      RUNNING_INITIALIZING,
      RUNNING_LOADING_WORKFLOWS,
    } = STATUS_MESSAGES;
    const { WORKFLOWS_LOAD_FAILED } = NOTIFICATION_MESSAGES;

    this.#APP_ROOT = document.querySelector<HTMLDivElement>('#app');
    if (!this.#APP_ROOT) {
      const fallback = document.createElement('div');
      fallback.id = 'app';
      if (document.body) {
        document.body.appendChild(fallback);
      }
      this.#APP_ROOT = fallback as HTMLDivElement;
    }

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
    this.#ROUTING = createRoutingController({ store: this.#STORE });

    this.#CLIENT = new WorkflowRunnerClient();
    this.#CLIENT.setUpdateHandler((runs: Map<string, RunRecord>) => {
      // DRY: map all runs through single transformation point
      for (const rec of runs.values()) {
        const uiEntry = recordToUI(rec, this.#WORKFLOW_NAMES);
        upsertRun(this.#STORE, uiEntry);
      }
      // Maintain selection invariant (select active run if current is terminal)
      ensureActiveRun(this.#STORE);
    });

    // Register queue handler so SSE queue_status updates drive the UI indicator
    this.#CLIENT.setQueueHandler((pending: number, _running: number) => {
      try {
        const state = this.#STORE.getState();
        state.mutate.queuedJobs(pending ?? 0);
      } catch (e) {
        // tolerate store errors silently
      }
    });

    const state = this.#STORE.getState();

    state.mutate.manager(this);

    // Expose internal private fields under string keys to make them reachable
    // from tests that access them via bracket notation (e.g. manager['#CLIENT']).
    // This is a small, test-friendly shim and does not affect production usage.
    try {
      (this as any)['#CLIENT'] = this.#CLIENT;
      (this as any)['#STORE'] = this.#STORE;
      (this as any)['#WORKFLOW_NAMES'] = this.#WORKFLOW_NAMES;
    } catch (e) {
      // ignore if environment forbids defining these keys
    }

    this.#ROUTING.initialize();
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
        this.#ROUTING.updateRouteFromState();
        // Start client after workflows loaded to populate workflow names
        this.#preloadWorkflowNames();
        this.#CLIENT.start();
      });
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
    const route = this.#ROUTING.getPendingRoute();
    const shouldSelectDefault =
      !route ||
      (!route.workflowId && (route.view === 'workflow' || route.view === 'history')) ||
      (route.view === 'run' && !route.workflowId);

    if (shouldSelectDefault && firstWorkflow?.id) {
      state.mutate.workflow(firstWorkflow.id);
    }

    this.#ROUTING.applyPendingRouteIfNeeded();
  };
  #preloadWorkflowNames() {
    // Preload workflow names into client to avoid individual fetches
    const state = this.#STORE.getState();
    const workflows = state.workflows?.nodes || [];

    for (const node of workflows) {
      if (node.id && (node as any).name) {
        this.#WORKFLOW_NAMES.set(node.id, (node as any).name);
      }
    }

    this.#CLIENT.setWorkflowNames(this.#WORKFLOW_NAMES);
  }
  #setInputStatus(inputId: string, status: WorkflowCellStatus) {
    const elements = this.uiRegistry.get();
    const cells = (elements?.[INPUTS_CLASSES.cells] as WorkflowUICells) || [];

    const cell = cells.find((el) => el.id === inputId);
    const wrapper = cell?.parentElement;
    if (wrapper) {
      wrapper.dataset.status = status;
    }
  }
  #subscribeToState() {
    const st = this.#STORE.getState();
    let latestState = st;
    let lastCurrentMessage = st.current.message;
    let lastCurrentStatus = st.current.status;
    let lastDebug = st.isDebug;
    let lastId = st.current.id;
    let lastInputStatuses = st.inputStatuses;
    let lastNotificationsCount = st.notifications?.length ?? 0;
    let lastQueued = st.queuedJobs ?? -1;
    let lastResults = st.results;
    let lastRunId = st.currentRunId;
    let lastRunsRef = st.runs;
    let lastSelectedRunId = st.selectedRunId;
    let lastView = st.view;
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
      latestState = state;
      const { current, isDebug, queuedJobs, workflows } = state;
      const { message, status } = current;

      if (state.currentRunId !== lastRunId) {
        // Run polling removed - SSE handles status updates
        lastRunId = state.currentRunId;
      }

      if (current.id !== lastId) {
        needs.main = true;
        lastId = current.id;
      }
      if (state.results !== lastResults) {
        needs.main = true;
        lastResults = state.results;
      }
      if (state.runs !== lastRunsRef) {
        needs.main = true;
        lastRunsRef = state.runs;
      }
      if (state.selectedRunId !== lastSelectedRunId) {
        needs.main = true;
        lastSelectedRunId = state.selectedRunId;
      }
      if (state.view !== lastView) {
        needs.main = true;
        lastView = state.view;
      }
      if (state.inputStatuses !== lastInputStatuses) {
        needs.main = true;
        lastInputStatuses = state.inputStatuses;
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

          const stateSnapshot = latestState;
          const snapshotDebug = stateSnapshot.isDebug;

          const sections = this.#SECTIONS;
          for (const sectionKey in needs) {
            const need = needs[sectionKey as keyof typeof needs];
            const section = sections[sectionKey as keyof typeof sections];
            if (need) {
              switch (sectionKey) {
                case 'dev':
                  if (snapshotDebug) {
                    section.mount();
                    section.render();
                  } else {
                    section.destroy();
                  }
                  break;
                case 'main':
                  const mainSections = resolveMainSections(stateSnapshot);
                  section.render(mainSections);
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
      this.#ROUTING.updateRouteFromState();
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

  //#region Runs
  runs = {
    all: (): WorkflowRunEntry[] => {
      return [...this.#STORE.getState().runs];
    },
    get: (runId: string): WorkflowRunEntry | null => {
      const { runs } = this.#STORE.getState();
      return runs.find((run) => run.runId === runId) || null;
    },
    select: (runId: string | null, nextView?: WorkflowView) => {
      if (!nextView) {
        selectRun(this.#STORE, runId);
        return;
      }

      if (nextView === 'run' && runId) {
        const run = this.runs.get(runId);
        const state = this.#STORE.getState();
        if (run?.workflowId && run.workflowId !== state.current.id) {
          state.mutate.workflow(run.workflowId);
        }
        changeView(this.#STORE, 'run', {
          runId,
          clearResults: false,
        });
        return;
      }

      changeView(this.#STORE, nextView, {
        runId: nextView === 'run' ? runId : null,
      });
    },
    selected: (): WorkflowRunEntry | null => {
      const { runs, selectedRunId } = this.#STORE.getState();
      if (!selectedRunId) {
        return null;
      }
      return runs.find((run) => run.runId === selectedRunId) || null;
    },
  };
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
      this.#ROUTING.destroy();
      // Stop the client on cleanup
      this.#CLIENT.stop();
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
    download: async (id?: string) => {
      const { ERROR_FETCHING_WORKFLOWS } = STATUS_MESSAGES;

      const state = this.#STORE.getState();
      id = id || state.current.id;

      try {
        const workflowJSON = await fetchWorkflowJSON(id);

        const workflowString = JSON.stringify(workflowJSON, null, 2);
        const blob = new Blob([workflowString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${id}.json`;
        document.body.appendChild(a);
        a.click();

        setTimeout(() => {
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }, 1000);
      } catch (error) {
        state.mutate.status('error', ERROR_FETCHING_WORKFLOWS);
        if (error instanceof WorkflowApiError) {
          addNotification(this.#STORE, {
            id: performance.now().toString(),
            message: `Failed to fetch workflow: ${error.message}`,
            status: 'danger',
          });
        }
      }
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
