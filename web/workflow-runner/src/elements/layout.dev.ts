import type { LfDataDataset } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'dev-section';
export const DEV_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  card: theme.bemClass(ROOT_CLASS, 'card'),
} as const;
//#endregion

//#region Helpers
const _createDataset = (): LfDataDataset => {
  return {
    nodes: [
      {
        id: 'workflow-runner-debug',
        cells: {
          lfToggle: {
            shape: 'toggle',
            value: false,
          },
          lfCode: {
            shape: 'code',
            value: '',
          },
          lfButton: {
            shape: 'button',
            value: '',
          },
          lfButton_2: {
            shape: 'button',
            value: '',
          },
        },
      },
    ],
  };
};
//#endregion

//#region Factory
export const createDevSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { DEV_SECTION_DESTROYED, DEV_SECTION_MOUNTED, DEV_SECTION_UPDATED } = DEBUG_MESSAGES;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in DEV_CLASSES) {
      const element = DEV_CLASSES[cls];
      uiRegistry.remove(element);
    }

    debugLog(DEV_SECTION_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[DEV_CLASSES._]) {
      return;
    }

    const _root = document.createElement('div');
    _root.className = DEV_CLASSES._;

    const card = document.createElement('lf-card') as HTMLLfCardElement;
    card.className = DEV_CLASSES.card;
    card.lfLayout = 'debug';
    card.lfDataset = _createDataset();

    const body = manager.getAppRoot()?.ownerDocument?.body ?? document.body;
    _root.appendChild(card);
    body.appendChild(_root);

    uiRegistry.set(DEV_CLASSES._, _root);
    uiRegistry.set(DEV_CLASSES.card, card);

    debugLog(DEV_SECTION_MOUNTED);
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

    debugLog(DEV_SECTION_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
