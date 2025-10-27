import { getLfFramework } from '@lf-widgets/framework';
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
} as const;
//#endregion

export const createMainSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { MAIN_DESTROYED, MAIN_MOUNTED, MAIN_UPDATED } = DEBUG_MESSAGES;
  const DEFAULT_SCOPE: WorkflowMainSections[] = ['inputs', 'outputs'];
  const INPUTS = createInputsSection(store);
  const OUTPUTS = createOutputsSection(store);
  const RESULTS = createResultsSection(store);
  let LAST_SCOPE = [...DEFAULT_SCOPE];
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
  const render = (scope = [...DEFAULT_SCOPE]) => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const scopeSet = new Set<WorkflowMainSections>(scope as WorkflowMainSections[]);

    const elements = uiRegistry.get();
    if (!elements || !scopeSet.size) {
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

    scope.forEach((section) => {
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

    LAST_SCOPE = [Array.from(scopeSet)].flat();
    debugLog(MAIN_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
