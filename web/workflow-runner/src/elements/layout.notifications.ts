import { LfThemeUIState } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStatus, WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'notifications-section';
export const NOTIFICATIONS_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  _visible: theme.bemClass(ROOT_CLASS, undefined, { active: true }),
  item: theme.bemClass(ROOT_CLASS, 'item'),
} as const;
//#endregion

//#region Helpers
const _checkForVisible = (_root: HTMLDivElement) => {
  if (_root.hasChildNodes()) {
    _root.className = NOTIFICATIONS_CLASSES._visible;
  } else {
    _root.className = NOTIFICATIONS_CLASSES._;
  }
};
const _getStateCategory = (status: WorkflowStatus | LfThemeUIState) => {
  let category: LfThemeUIState;

  switch (status) {
    case 'danger':
    case 'error':
      category = 'danger';
      break;
    default:
      category = 'info';
      break;
  }

  return category;
};
//#endregion

//#region Factory
export const createNotificationsSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { NOTIFICATIONS_DESTROYED, NOTIFICATIONS_MOUNTED, NOTIFICATIONS_UPDATED, STATUS_UPDATED } =
    DEBUG_MESSAGES;
  let lastMessage: string | null = null;
  let lastStatus: string | null = null;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const state = store.getState();
    if (!state.manager) {
      return;
    }

    const { manager } = state;
    const { uiRegistry } = manager;

    for (const cls in NOTIFICATIONS_CLASSES) {
      const element = NOTIFICATIONS_CLASSES[cls];
      uiRegistry.remove(element);
    }

    lastMessage = null;
    lastStatus = null;

    debugLog(NOTIFICATIONS_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[NOTIFICATIONS_CLASSES._]) {
      return;
    }

    const _root = document.createElement('div');
    _root.className = NOTIFICATIONS_CLASSES._;

    manager.getAppRoot().appendChild(_root);

    uiRegistry.set(NOTIFICATIONS_CLASSES._, _root);

    debugLog(NOTIFICATIONS_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const state = store.getState();
    const { current, manager } = state;
    const { id, message, status } = current;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const _root = elements[NOTIFICATIONS_CLASSES._] as HTMLDivElement;

    if (status !== lastStatus || message !== lastMessage) {
      const timestamp = new Date().getTime();

      const element = document.createElement('lf-toast');
      element.className = NOTIFICATIONS_CLASSES.item;
      element.lfCloseCallback = () => {
        uiRegistry.remove(NOTIFICATIONS_CLASSES.item + timestamp);
        _checkForVisible(_root);
      };
      element.lfIcon =
        status === 'error' ? theme.get.icon('alertTriangle') : theme.get.icon('infoHexagon');
      element.lfMessage = message;
      element.lfTimer = status === 'error' ? 5000 : 5000; //TODO: Update when the CSS variable is fixed LFW-side
      element.lfUiState = _getStateCategory(status);

      _root.appendChild(element);
      _checkForVisible(_root);

      uiRegistry.set(NOTIFICATIONS_CLASSES.item + timestamp, element);

      lastStatus = status;
      lastMessage = message;
      debugLog(STATUS_UPDATED, status, {
        id,
        status,
        message,
      });
    }

    debugLog(NOTIFICATIONS_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
