import { getLfFramework } from '@lf-widgets/framework';
import { buildAssetsUrl, DEFAULT_STATUS_MESSAGES, DEFAULT_THEME } from '../config';
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
import { WorkflowStatus, WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { initState } from './state';
import { createWorkflowRunnerStore } from './store';

export class LfWorkflowRunnerManager implements WorkflowManager {
  //#region Initialization
  #DISPATCHERS: WorkflowDispatchers;
  #FRAMEWORK = getLfFramework();
  #IS_DEBUG = false;
  #APP_ROOT: HTMLDivElement;
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
    const { WORKFLOWS_LOAD_FAILED } = DEBUG_MESSAGES;
    const { LOADING_WORKFLOWS } = STATUS_MESSAGES;

    this.#APP_ROOT = document.querySelector<HTMLDivElement>('#app');
    if (!this.#APP_ROOT) {
      throw new Error('Workflow runner container not found.');
    }

    this.#STORE = createWorkflowRunnerStore(initState());
    this.#IS_DEBUG = this.#STORE.getState().isDebug;

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
      this.#IS_DEBUG = true;
    }
  }
  #loadWorkflows = async () => {
    const { WORKFLOWS_LOADED } = DEBUG_MESSAGES;

    const workflows = await fetchWorkflowDefinitions();
    if (!workflows || !Object.keys(workflows).length) {
      throw new Error('No workflows available from the API.');
    }

    this.#STORE.getState().mutate.workflows(workflows);

    const firstWorkflow = workflows.nodes?.[0];
    if (firstWorkflow?.id) {
      this.setWorkflow(firstWorkflow.id);
    }
    this.setStatus('idle', WORKFLOWS_LOADED);
  };
  #subscribeToState() {
    this.#STORE.subscribe((state) => {
      this.#SECTIONS.actionButton.render();
      this.#SECTIONS.drawer.render();
      this.#SECTIONS.header.render();
      this.#SECTIONS.main.render();
      this.#SECTIONS.notifications.render();

      const shouldShowDevPanel = state.isDebug;
      if (shouldShowDevPanel && !this.#IS_DEBUG) {
        this.#SECTIONS.dev.mount();
        this.#IS_DEBUG = true;
        this.#SECTIONS.dev.render();
      } else if (!shouldShowDevPanel && this.#IS_DEBUG) {
        this.#SECTIONS.dev.destroy();
        this.#IS_DEBUG = false;
      } else if (shouldShowDevPanel && this.#IS_DEBUG) {
        this.#SECTIONS.dev.render();
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
  isDebugEnabled() {
    return this.#STORE.getState().isDebug;
  }
  //#endregion

  //#region State mutators
  setStatus(status: WorkflowStatus, message?: string): void {
    const { mutate } = this.#STORE.getState();

    const resolved = message ?? DEFAULT_STATUS_MESSAGES[status];
    mutate.status(status, resolved);
  }
  setWorkflow(id: string): void {
    const state = this.#STORE.getState();

    if (state.current.id === id) {
      return;
    }

    state.mutate.workflow(id);
  }
  toggleDebug(): void {
    const current = this.#STORE.getState().isDebug;
    this.#STORE.getState().mutate.isDebug(!current);
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
