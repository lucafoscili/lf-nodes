import { getLfFramework } from '@lf-widgets/framework';
import { buildAssetsUrl, DEFAULT_THEME } from '../config';
import { workflowDispatcher } from '../dispatchers/workflow';
import { createActionButtonSection } from '../elements/layout.action-button';
import { createDevSection } from '../elements/layout.dev';
import { createDrawerSection } from '../elements/layout.drawer';
import { createHeaderSection } from '../elements/layout.header';
import { createMainSection } from '../elements/layout.main';
import { createNotificationsSection } from '../elements/layout.notifications';
import { fetchWorkflowDefinitions } from '../services/workflow-service';
import { WorkflowDispatchers, WorkflowManager, WorkflowUIItem } from '../types/manager';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { parseCount } from '../utils/common';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
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
    const { LOADING_WORKFLOWS, WORKFLOWS_LOAD_FAILED } = DEBUG_MESSAGES;

    this.#APP_ROOT = document.querySelector<HTMLDivElement>('#app');
    if (!this.#APP_ROOT) {
      throw new Error('Workflow runner container not found.');
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

    const state = this.#STORE.getState();

    state.mutate.manager(this);

    this.#initializeFramework();
    this.#initializeLayout();
    this.#subscribeToState();
    debugLog(LOADING_WORKFLOWS);

    this.#loadWorkflows().catch((error) => {
      const message = error instanceof Error ? error.message : WORKFLOWS_LOAD_FAILED;
      debugLog(WORKFLOWS_LOAD_FAILED, 'error', {
        message,
        stack: error instanceof Error ? error.stack : undefined,
      });
      state.mutate.status('error', message);
    });

    this.#startPolling();
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
    const { WORKFLOWS_LOADED } = DEBUG_MESSAGES;

    const state = this.#STORE.getState();

    const workflows = await fetchWorkflowDefinitions();
    if (!workflows || !Object.keys(workflows).length) {
      throw new Error('No workflows available from the API.');
    }

    state.mutate.workflows(workflows);

    const firstWorkflow = workflows.nodes?.[0];
    if (firstWorkflow?.id) {
      state.mutate.workflow(firstWorkflow.id);
    }

    state.mutate.status('idle', WORKFLOWS_LOADED);
  };
  #startPolling() {
    setInterval(async () => {
      try {
        const resp = await fetch('/queue');
        if (!resp.ok) {
          throw new Error('Failed to fetch queue status');
        }

        const { queue_running, queue_pending } = (await resp.json()) as {
          queue_pending: unknown;
          queue_running: unknown;
        };

        const qPending = parseCount(queue_pending);
        const qRunning = parseCount(queue_running);
        const busy = qPending + qRunning;

        const prev = this.#STORE.getState().queuedJobs ?? -1;
        if (busy !== prev) {
          this.#STORE.getState().mutate.queuedJobs(busy);
        }
      } catch (e) {
        try {
          const prev = this.#STORE.getState().queuedJobs ?? -1;
          if (prev !== -1) {
            this.#STORE.getState().mutate.queuedJobs(-1);
          }
        } catch (err) {}
      }
    }, 750);
  }
  #subscribeToState() {
    const st = this.#STORE.getState();
    let lastCurrentMessage = st.current.message;
    let lastCurrentStatus = st.current.status;
    let lastDebug = st.isDebug;
    let lastId = st.current.id;
    let lastQueued = st.queuedJobs ?? -1;
    let lastResults = st.results;
    let lastWorkflows = st.workflows;

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

      if (current.id !== lastId || state.results !== lastResults) {
        needs.main = true;
        lastId = current.id;
        lastResults = state.results;
      }

      if (message !== lastCurrentMessage || status !== lastCurrentStatus) {
        needs.actionButton = true;
        needs.notifications = true;
        lastCurrentMessage = message;
        lastCurrentStatus = status;
      }

      if (queuedJobs !== lastQueued) {
        needs.header = true;
        lastQueued = queuedJobs;
      }

      if (workflows !== lastWorkflows) {
        needs.drawer = true;
        lastWorkflows = workflows;
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
}
