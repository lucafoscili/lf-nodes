import { getLfFramework } from '@lf-widgets/framework';
import { executeWorkflow } from '../handlers/workflow';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'action-button-section';
export const ACTION_BUTTON_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
} as const;
//#endregion

export const createActionButtonSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { ACTION_BUTTON_DESTROYED, ACTION_BUTTON_MOUNTED, ACTION_BUTTON_UPDATED } = DEBUG_MESSAGES;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in ACTION_BUTTON_CLASSES) {
      const element = ACTION_BUTTON_CLASSES[cls];
      uiRegistry.remove(element);
    }

    debugLog(ACTION_BUTTON_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[ACTION_BUTTON_CLASSES._]) {
      return;
    }

    const _root = document.createElement('lf-button') as HTMLLfButtonElement;
    _root.className = theme.bemClass(ACTION_BUTTON_CLASSES._);
    _root.lfIcon = 'send';
    _root.lfStyling = 'floating';
    _root.title = 'Run current workflow';
    _root.addEventListener('lf-button-event', (e) => executeWorkflow(e, store));

    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(ACTION_BUTTON_CLASSES._, _root);

    debugLog(ACTION_BUTTON_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const { current, manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const _root = elements[ACTION_BUTTON_CLASSES._] as HTMLLfButtonElement;
    if (!_root) {
      return;
    }

    _root.lfShowSpinner = current.status === 'running';

    debugLog(ACTION_BUTTON_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
