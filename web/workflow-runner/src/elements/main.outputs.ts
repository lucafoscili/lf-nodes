import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'outputs-section';
export const WORKFLOW_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  h4: theme.bemClass(ROOT_CLASS, 'title-h4'),
  masonry: theme.bemClass(ROOT_CLASS, 'masonry'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
const _masonry = () => {
  const masonryWrapper = document.createElement('lf-masonry');
  masonryWrapper.className = WORKFLOW_CLASSES.masonry;

  return masonryWrapper;
};
const _title = () => {
  const title = document.createElement('div');
  const h4 = document.createElement('h4');

  title.className = WORKFLOW_CLASSES.title;

  h4.className = WORKFLOW_CLASSES.h4;

  title.appendChild(h4);

  return { h4, title };
};
//#endregion

export const createOutputsSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { WORKFLOW_OUTPUTS_DESTROYED, WORKFLOW_OUTPUTS_MOUNTED, WORKFLOW_OUTPUTS_UPDATED } =
    DEBUG_MESSAGES;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in WORKFLOW_CLASSES) {
      const element = WORKFLOW_CLASSES[cls];
      uiRegistry.remove(element);
    }

    debugLog(WORKFLOW_OUTPUTS_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[WORKFLOW_CLASSES._]) {
      return;
    }

    const _root = document.createElement('section');
    _root.className = WORKFLOW_CLASSES._;

    const { h4, title } = _title();
    const masonry = _masonry();

    _root.appendChild(title);
    _root.appendChild(masonry);

    elements[MAIN_CLASSES._].appendChild(_root);

    uiRegistry.set(WORKFLOW_CLASSES._, _root);
    uiRegistry.set(WORKFLOW_CLASSES.h4, h4);
    uiRegistry.set(WORKFLOW_CLASSES.masonry, masonry);
    uiRegistry.set(WORKFLOW_CLASSES.title, title);

    debugLog(WORKFLOW_OUTPUTS_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const h4 = elements[WORKFLOW_CLASSES.h4] as HTMLElement;
    h4.textContent = manager.workflow.title() + ' outputs' || 'Unknown workflow outputs';

    // TODO: render outputs inside masonry based on their status

    debugLog(WORKFLOW_OUTPUTS_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
//#endregion
