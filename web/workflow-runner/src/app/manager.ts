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
import { fetchWorkflowDefinitions } from '../services/workflow-service';
import {
  WorkflowCellInputId,
  WorkflowCellsInputContainer,
  WorkflowCellsOutputContainer,
  WorkflowCellType,
} from '../types/api';
import {
  RunLifecycleController,
  WorkflowDispatchers,
  WorkflowManager,
  WorkflowPollingController,
  WorkflowUIItem,
} from '../types/manager';
import { WorkflowCellStatus, WorkflowSectionController, WorkflowUICells } from '../types/section';
import { WorkflowRoute, WorkflowRunEntry, WorkflowStore, WorkflowView } from '../types/state';
import { NOTIFICATION_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import { createPollingController } from './polling';
import {
  parseRouteFromLocation,
  replaceRouteInHistory,
  routesEqual,
  subscribeToRouteChanges,
} from './router';
import { createRunLifecycle } from './runs';
import { sectionsForView } from './sections';
import { initState } from './state';
import { createWorkflowRunnerStore } from './store';

export class LfWorkflowRunnerManager implements WorkflowManager {
  //#region Initialization
  #APP_ROOT: HTMLDivElement;
  #CURRENT_ROUTE: WorkflowRoute | null;
  #DISPATCHERS: WorkflowDispatchers;
  #FRAMEWORK = getLfFramework();
  #IS_APPLYING_ROUTE = false;
  #PENDING_ROUTE: WorkflowRoute | null;
  #POLLING: WorkflowPollingController;
  #ROUTE_UNSUBSCRIBE?: () => void;
  #RUN_LIFECYCLE: RunLifecycleController;
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
    this.#RUN_LIFECYCLE = createRunLifecycle({
      store: this.#STORE,
      setInputStatus: (inputId, status) => {
        this.#setInputStatus(inputId, status);
      },
    });
    this.#POLLING = createPollingController({
      runLifecycle: this.#RUN_LIFECYCLE,
      store: this.#STORE,
    });

    const state = this.#STORE.getState();

    state.mutate.manager(this);

    this.#initializeRouter();
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
        this.#updateRouteFromState();
      });

    this.#POLLING.startQueuePolling();
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
  #initializeRouter() {
    this.#CURRENT_ROUTE = parseRouteFromLocation();
    this.#PENDING_ROUTE = this.#CURRENT_ROUTE;
    this.#ROUTE_UNSUBSCRIBE = subscribeToRouteChanges((route) => {
      this.#handleRouteChange(route);
    });
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
    const route = this.#PENDING_ROUTE;
    const shouldSelectDefault =
      !route ||
      (!route.workflowId && (route.view === 'workflow' || route.view === 'history')) ||
      (route.view === 'run' && !route.workflowId);

    if (shouldSelectDefault && firstWorkflow?.id) {
      state.mutate.workflow(firstWorkflow.id);
    }

    this.#applyPendingRouteIfNeeded();
  };
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
    let lastRunsRef = st.runs;
    let lastSelectedRunId = st.selectedRunId;
    let lastWorkflowsCount = st.workflows?.nodes?.length ?? 0;
    let lastView = st.view;

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
          this.#POLLING.beginRunPolling(state.currentRunId);
        } else {
          this.#POLLING.stopRunPolling();
        }
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
                case 'main':
                  const views = sectionsForView(state.view);
                  section.render(views);
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
      this.#updateRouteFromState();
    });
  }
  //#endregion

  //#region Routing
  #applyPendingRouteIfNeeded() {
    if (this.#PENDING_ROUTE) {
      const route = this.#PENDING_ROUTE;
      this.#PENDING_ROUTE = null;
      this.#applyRoute(route, false);
    } else {
      this.#updateRouteFromState();
    }
  }
  #applyRoute(route: WorkflowRoute, allowDefer = true) {
    if (allowDefer && !this.#hasWorkflowsLoaded()) {
      this.#PENDING_ROUTE = route;
      return;
    }

    this.#IS_APPLYING_ROUTE = true;
    this.#PENDING_ROUTE = null;
    try {
      const state = this.#STORE.getState();
      let workflowId = route.workflowId ?? null;
      if (workflowId && this.#workflowExists(workflowId) && state.current.id !== workflowId) {
        state.mutate.workflow(workflowId);
      } else if (workflowId && !this.#workflowExists(workflowId)) {
        workflowId = state.current.id ?? null;
      }

      switch (route.view) {
        case 'home':
          state.mutate.selectRun(null);
          state.mutate.results(null);
          state.mutate.view('home');
          break;
        case 'history':
          state.mutate.selectRun(null);
          state.mutate.results(null);
          state.mutate.view('history');
          break;
        case 'run':
          if (route.runId) {
            state.mutate.selectRun(route.runId);
            state.mutate.view('run');
          } else {
            state.mutate.selectRun(null);
            state.mutate.results(null);
            state.mutate.view('workflow');
          }
          break;
        case 'workflow':
        default:
          state.mutate.selectRun(null);
          state.mutate.results(null);
          state.mutate.view('workflow');
          break;
      }
    } finally {
      this.#IS_APPLYING_ROUTE = false;
      this.#updateRouteFromState();
    }
  }
  #computeRouteFromState(): WorkflowRoute {
    const state = this.#STORE.getState();
    const workflowId = state.current.id ?? undefined;

    switch (state.view) {
      case 'home':
        return { view: 'home' };
      case 'history':
        return { view: 'history', workflowId };
      case 'run':
        if (state.selectedRunId) {
          return { view: 'run', runId: state.selectedRunId, workflowId };
        }
        return workflowId ? { view: 'workflow', workflowId } : { view: 'workflow' };
      case 'workflow':
      default:
        return workflowId ? { view: 'workflow', workflowId } : { view: 'workflow' };
    }
  }
  #handleRouteChange(route: WorkflowRoute) {
    this.#PENDING_ROUTE = route;
    this.#applyRoute(route);
  }
  #hasWorkflowsLoaded() {
    const { workflows } = this.#STORE.getState();
    return Array.isArray(workflows?.nodes) && workflows.nodes.length > 0;
  }
  #updateRouteFromState(precomputed?: WorkflowRoute) {
    if (this.#IS_APPLYING_ROUTE) {
      return;
    }
    const nextRoute = precomputed ?? this.#computeRouteFromState();
    if (!routesEqual(nextRoute, this.#CURRENT_ROUTE)) {
      this.#CURRENT_ROUTE = nextRoute;
      replaceRouteInHistory(nextRoute);
    }
  }
  #workflowExists(workflowId: string) {
    const { workflows } = this.#STORE.getState();
    return Boolean(workflows?.nodes?.some((node) => node.id === workflowId));
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
      if (this.#ROUTE_UNSUBSCRIBE) {
        this.#ROUTE_UNSUBSCRIBE();
        this.#ROUTE_UNSUBSCRIBE = undefined;
      }
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
      const state = this.#STORE.getState();
      state.mutate.selectRun(runId);
      if (nextView) {
        state.mutate.view(nextView);
      } else {
        state.mutate.view(runId ? 'run' : 'workflow');
      }
      if (!runId) {
        state.mutate.results(null);
      }
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
