import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { toggleDrawer } from '../handlers/layout';
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
  container: theme.bemClass(ROOT_CLASS, 'container'),
  drawerToggle: theme.bemClass(ROOT_CLASS, 'drawer-toggle'),
} as const;
//#endregion

//#region Helpers
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
  drawerToggle.addEventListener('lf-button-event', (e) => toggleDrawer(e, store));

  return drawerToggle;
};
//#endregion

export const createHeaderSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { HEADER_DESTROYED, HEADER_MOUNTED, HEADER_UPDATED } = DEBUG_MESSAGES;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in HEADER_CLASSES) {
      const element = HEADER_CLASSES[cls];
      uiRegistry.remove(element);
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

    const container = _container();
    const drawerToggle = _drawerToggle(store);

    _root.appendChild(container);
    container.appendChild(drawerToggle);

    manager.getAppRoot().appendChild(_root);

    uiRegistry.set(HEADER_CLASSES._, _root);
    uiRegistry.set(HEADER_CLASSES.container, container);
    uiRegistry.set(HEADER_CLASSES.drawerToggle, drawerToggle);

    debugLog(HEADER_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
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
