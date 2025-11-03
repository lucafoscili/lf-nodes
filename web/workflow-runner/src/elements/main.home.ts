import { LfDataDataset, LfDataNode } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { masonryHandler } from '../handlers/masonry';
import { WorkflowAPIDataset } from '../types/api';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'home-section';
export const HOME_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  h1: theme.bemClass(ROOT_CLASS, 'title-h1'),
  masonry: theme.bemClass(ROOT_CLASS, 'masonry'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
const _createDataset = (store: WorkflowStore) => {
  const { workflows } = store.getState();

  const clone: WorkflowAPIDataset = JSON.parse(JSON.stringify(workflows));

  const root: LfDataNode = { cells: {}, id: 'root', value: 'Workflows' };

  clone.nodes?.forEach((node) => {
    const id = node.id;
    root.cells[id] = {
      lfDataset: {
        nodes: [
          {
            cells: {
              '1': {
                value: String(node.value),
              },
              '2': {
                value: node.category,
              },
              '3': {
                value: node.description,
              },
            },
            id,
          },
        ],
      },
      shape: 'card',
      value: '',
    };
  });

  const dataset: LfDataDataset = {
    nodes: [root],
  };

  return dataset;
};
const _masonry = (store: WorkflowStore) => {
  const masonry = document.createElement('lf-masonry');
  masonry.className = HOME_CLASSES.masonry;
  masonry.lfShape = 'card';
  masonry.lfStyle = '.masonry .grid { overflow-x: unset; overflow-y: unset; }'; // FIXME: Experimental
  masonry.addEventListener('lf-masonry-event', (e) => masonryHandler(e, store));

  return masonry;
};
const _description = () => {
  const p = document.createElement('p');
  p.className = HOME_CLASSES.description;
  p.textContent = 'Below a list of the available workflows.';

  return p;
};
const _title = () => {
  const title = document.createElement('div');
  const h1 = document.createElement('h1');

  title.className = HOME_CLASSES.title;

  h1.className = HOME_CLASSES.h1;
  h1.textContent = 'Workflow Runner';

  title.appendChild(h1);

  return { h1, title };
};
//#endregion

export const createHomeSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { HOME_DESTROYED, HOME_MOUNTED, HOME_UPDATED } = DEBUG_MESSAGES;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in HOME_CLASSES) {
      const element = HOME_CLASSES[cls];
      uiRegistry.remove(element);
    }

    debugLog(HOME_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[HOME_CLASSES._]) {
      return;
    }

    const _root = document.createElement('section');
    _root.className = HOME_CLASSES._;

    const description = _description();
    const masonry = _masonry(store);
    const { h1, title } = _title();

    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(masonry);

    elements[MAIN_CLASSES._].prepend(_root);

    uiRegistry.set(HOME_CLASSES._, _root);
    uiRegistry.set(HOME_CLASSES.description, description);
    uiRegistry.set(HOME_CLASSES.h1, h1);
    uiRegistry.set(HOME_CLASSES.masonry, masonry);
    uiRegistry.set(HOME_CLASSES.title, title);

    debugLog(HOME_MOUNTED);
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

    const masonry = elements[HOME_CLASSES.masonry] as HTMLLfMasonryElement;

    masonry.lfDataset = _createDataset(store);

    debugLog(HOME_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
//#endregion
