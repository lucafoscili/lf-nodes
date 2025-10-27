import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowMainSections, WorkflowSectionController } from '../types/section';
import { WorkflowStore, WorkflowView } from '../types/state';
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

//#region Helpers
const _sectionsForView = (view: WorkflowView): WorkflowMainSections[] => {
  switch (view) {
    case 'history':
      return ['outputs'];
    case 'home':
      return [];
    case 'run':
      return ['results'];
    case 'workflow':
    default:
      return ['inputs', 'outputs'];
  }
};
//#endregion

export const createMainSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { MAIN_DESTROYED, MAIN_MOUNTED, MAIN_UPDATED } = DEBUG_MESSAGES;
  const INPUTS = createInputsSection(store);
  const OUTPUTS = createOutputsSection(store);
  const RESULTS = createResultsSection(store);
  let LAST_SCOPE: WorkflowMainSections[] = [];
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in MAIN_CLASSES) {
      const element = MAIN_CLASSES[cls];
      uiRegistry.remove(element);
    }

    INPUTS.destroy();
    OUTPUTS.destroy();
    RESULTS.destroy();
    uiRegistry.remove(MAIN_CLASSES.home);

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

    INPUTS.mount();
    OUTPUTS.mount();
    RESULTS.mount();

    debugLog(MAIN_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = (scope?: WorkflowMainSections[]) => {
    const state = store.getState();

    const { manager } = state;
    const { uiRegistry } = manager;

    const resolvedSections = scope ?? _sectionsForView(state.view);
    const scopeSet = new Set<WorkflowMainSections>(resolvedSections);

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    LAST_SCOPE.forEach((section) => {
      if (!scopeSet.has(section)) {
        switch (section) {
          case 'inputs':
            INPUTS.destroy();
            break;
          case 'outputs':
            OUTPUTS.destroy();
            break;
          case 'results':
            RESULTS.destroy();
            break;
        }
      }
    });

    scopeSet.forEach((section) => {
      switch (section) {
        case 'inputs':
          if (!LAST_SCOPE.find((s) => s === 'inputs')) {
            INPUTS.mount();
          }
          INPUTS.render();
          break;
        case 'outputs':
          if (!LAST_SCOPE.find((s) => s === 'outputs')) {
            OUTPUTS.mount();
          }
          OUTPUTS.render();
          break;
        case 'results':
          if (!LAST_SCOPE.find((s) => s === 'results')) {
            RESULTS.mount();
          }
          RESULTS.render();
          break;
      }
    });

    if (resolvedSections.length === 0) {
      if (!elements[MAIN_CLASSES.home]) {
        const placeholder = document.createElement('div');
        placeholder.className = MAIN_CLASSES.home;
        placeholder.textContent = 'Select a workflow to get started.';
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

    debugLog(MAIN_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
