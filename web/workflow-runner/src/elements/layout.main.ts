import { getLfFramework } from '@lf-widgets/framework';
import { HOME_PLACEHOLDER, resolveMainSections } from '../app/sections';
import { WorkflowMainSections, WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { createInputsSection } from './main.inputs';
import { createOutputsSection } from './main.outputs';
import { createResultsSection } from './main.results';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'main-section';
export const MAIN_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  home: theme.bemClass(ROOT_CLASS, 'home'),
} as const;
//#endregion

export const createMainSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { MAIN_DESTROYED, MAIN_MOUNTED, MAIN_UPDATED } = DEBUG_MESSAGES;
  const INPUTS = createInputsSection(store);
  const OUTPUTS = createOutputsSection(store);
  const RESULTS = createResultsSection(store);
  const SECTION_CONTROLLERS: Record<WorkflowMainSections, WorkflowSectionController> = {
    inputs: INPUTS,
    outputs: OUTPUTS,
    results: RESULTS,
  };
  let LAST_SCOPE: WorkflowMainSections[] = [];
  let LAST_WORKFLOW_ID: string | null = store.getState().current.id;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    Object.values(MAIN_CLASSES).forEach((className) => uiRegistry.remove(className));
    Object.values(SECTION_CONTROLLERS).forEach((controller) => controller.destroy());

    debugLog(MAIN_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[MAIN_CLASSES._]) {
      return;
    }

    const _root = document.createElement('main');
    _root.className = ROOT_CLASS;

    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(MAIN_CLASSES._, _root);

    debugLog(MAIN_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = (scope?: WorkflowMainSections[]) => {
    const state = store.getState();

    const { manager } = state;
    const { uiRegistry } = manager;
    const workflowId = state.current.id ?? null;
    const workflowChanged = workflowId !== LAST_WORKFLOW_ID;

    const resolvedSections = scope ?? resolveMainSections(state);
    const scopeSet = new Set<WorkflowMainSections>(resolvedSections);

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const previousSections = new Set<WorkflowMainSections>(LAST_SCOPE);

    if (workflowChanged && previousSections.size > 0) {
      previousSections.forEach((section) => {
        SECTION_CONTROLLERS[section].destroy();
      });
      previousSections.clear();
      LAST_SCOPE = [];
    } else {
      LAST_SCOPE.forEach((section) => {
        if (!scopeSet.has(section)) {
          SECTION_CONTROLLERS[section].destroy();
          previousSections.delete(section);
        }
      });
    }

    scopeSet.forEach((section) => {
      const controller = SECTION_CONTROLLERS[section];
      if (!previousSections.has(section)) {
        controller.mount();
      }
      controller.render();
    });

    if (resolvedSections.length === 0) {
      if (!elements[MAIN_CLASSES.home]) {
        const placeholder = document.createElement('div');
        placeholder.className = MAIN_CLASSES.home;
        placeholder.textContent = HOME_PLACEHOLDER;
        const root = elements[MAIN_CLASSES._] as HTMLElement | undefined;
        if (root) {
          root.appendChild(placeholder);
          uiRegistry.set(MAIN_CLASSES.home, placeholder);
        }
      }
    } else {
      uiRegistry.remove(MAIN_CLASSES.home);
    }

    LAST_SCOPE = Array.from(scopeSet);
    LAST_WORKFLOW_ID = workflowId;

    debugLog(MAIN_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
