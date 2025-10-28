import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/layout';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { createComponent } from './components';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'header-section';
export const HEADER_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  appMessage: theme.bemClass(ROOT_CLASS, 'app-message'),
  container: theme.bemClass(ROOT_CLASS, 'container'),
  drawerToggle: theme.bemClass(ROOT_CLASS, 'drawer-toggle'),
  serverIndicator: theme.bemClass(ROOT_CLASS, 'server-indicator'),
  serverIndicatorCounter: theme.bemClass(ROOT_CLASS, 'server-indicator-counter'),
  serverIndicatorLight: theme.bemClass(ROOT_CLASS, 'server-indicator-light'),
} as const;
//#endregion

//#region Helpers
const _appMessage = () => {
  const appMessage = document.createElement('div');
  appMessage.className = HEADER_CLASSES.appMessage;
  appMessage.ariaAtomic = 'true';
  appMessage.ariaLive = 'polite';

  return appMessage;
};
const _container = () => {
  const container = document.createElement('div');
  container.className = HEADER_CLASSES.container;
  container.slot = 'content';

  return container;
};
const _drawerToggle = (store: WorkflowStore) => {
  const lfIcon = theme.get.icon('menu2');

  const props = {
    lfAriaLabel: 'Toggle drawer',
    lfIcon,
    lfStyling: 'icon',
  } as Partial<LfButtonInterface>;

  const drawerToggle = createComponent.button(props);
  drawerToggle.className = HEADER_CLASSES.drawerToggle;
  drawerToggle.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  return drawerToggle;
};

const _serverIndicator = (store: WorkflowStore) => {
  const serverIndicator = document.createElement('div');
  serverIndicator.className = HEADER_CLASSES.serverIndicator;

  const light = document.createElement('lf-button');
  light.className = HEADER_CLASSES.serverIndicatorLight;
  light.lfUiSize = 'large';
  light.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  const counter = document.createElement('span');
  counter.className = HEADER_CLASSES.serverIndicatorCounter;

  serverIndicator.appendChild(counter);
  serverIndicator.appendChild(light);

  return { counter, light, serverIndicator };
};
//#endregion

export const createHeaderSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { HEADER_DESTROYED, HEADER_MOUNTED, HEADER_UPDATED } = DEBUG_MESSAGES;
  const HIDE_KEY = '__lf_hide_timer__';
  const HIDE_DELAY = 900;
  const FADE_CLEAR_DELAY = 380;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in HEADER_CLASSES) {
      const element = HEADER_CLASSES[cls];
      uiRegistry.remove(element);
    }

    const elements = uiRegistry.get();
    if (elements && elements[HEADER_CLASSES.appMessage]) {
      const appMessage = elements[HEADER_CLASSES.appMessage] as HTMLElement;
      const timer = appMessage[HIDE_KEY] as ReturnType<typeof setTimeout> | undefined;
      if (timer) {
        clearTimeout(timer);
        appMessage[HIDE_KEY] = undefined;
      }
    }

    debugLog(HEADER_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[HEADER_CLASSES._]) {
      return;
    }

    const _root = document.createElement('lf-header');
    _root.className = HEADER_CLASSES._;

    const appMessage = _appMessage();
    const container = _container();
    const drawerToggle = _drawerToggle(store);
    const { counter, light, serverIndicator } = _serverIndicator(store);

    _root.appendChild(container);
    container.appendChild(drawerToggle);
    container.appendChild(appMessage);
    container.appendChild(serverIndicator);

    manager.getAppRoot().appendChild(_root);

    uiRegistry.set(HEADER_CLASSES._, _root);
    uiRegistry.set(HEADER_CLASSES.appMessage, appMessage);
    uiRegistry.set(HEADER_CLASSES.container, container);
    uiRegistry.set(HEADER_CLASSES.drawerToggle, drawerToggle);
    uiRegistry.set(HEADER_CLASSES.serverIndicator, serverIndicator);
    uiRegistry.set(HEADER_CLASSES.serverIndicatorCounter, counter);
    uiRegistry.set(HEADER_CLASSES.serverIndicatorLight, light);

    debugLog(HEADER_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const { alertTriangle, check, hourglassLow } = theme.get.icons();
    const { current, manager, queuedJobs } = store.getState();
    const { message, status } = current;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const appMessage = elements[HEADER_CLASSES.appMessage] as HTMLElement;
    const counter = elements[HEADER_CLASSES.serverIndicatorCounter] as HTMLElement;
    const light = elements[HEADER_CLASSES.serverIndicatorLight] as HTMLLfButtonElement;

    const isIdle = status === 'idle';

    if (isIdle) {
      appMessage.dataset.status = current.status || '';
      appMessage.dataset.visible = 'true';

      if (typeof message === 'string' && message.length > 0) {
        appMessage.innerText = message;
      }

      const prev = appMessage[HIDE_KEY] as ReturnType<typeof setTimeout> | undefined;
      if (prev) {
        clearTimeout(prev);
      }

      appMessage[HIDE_KEY] = setTimeout(() => {
        appMessage.dataset.visible = 'false';

        const clearTimer = setTimeout(() => {
          appMessage.innerText = '';
          appMessage[HIDE_KEY] = undefined;
        }, FADE_CLEAR_DELAY);

        appMessage[HIDE_KEY] = clearTimer as unknown as ReturnType<typeof setTimeout>;
      }, HIDE_DELAY);
    } else {
      const prev = appMessage[HIDE_KEY] as ReturnType<typeof setTimeout> | undefined;
      if (prev) {
        clearTimeout(prev);
        appMessage[HIDE_KEY] = undefined;
      }

      appMessage.innerText = message || '';
      appMessage.dataset.status = status || '';
      appMessage.dataset.visible = 'true';
    }

    if (queuedJobs < 0) {
      counter.innerText = '';
      light.lfIcon = alertTriangle;
      light.lfUiState = 'danger';
      light.title = 'Server disconnected';
    } else if (queuedJobs === 0) {
      counter.innerText = '';
      light.lfIcon = check;
      light.lfUiState = 'success';
      light.title = 'Server idle';
    } else {
      counter.innerText = queuedJobs.toString();
      light.lfIcon = hourglassLow;
      light.lfUiState = 'warning';
      light.title = `Jobs in queue: ${queuedJobs}`;
    }

    debugLog(HEADER_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
