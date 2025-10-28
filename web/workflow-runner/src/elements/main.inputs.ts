import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/button';
import { WorkflowSectionController, WorkflowUICells } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { createInputCell } from './components';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'inputs-section';
export const INPUTS_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  cell: theme.bemClass(ROOT_CLASS, 'cell'),
  cells: theme.bemClass(ROOT_CLASS, 'cells'),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  h3: theme.bemClass(ROOT_CLASS, 'title-h3'),
  openButton: theme.bemClass(ROOT_CLASS, 'title-open-button'),
  options: theme.bemClass(ROOT_CLASS, 'options'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
const _cells = () => {
  const cellWrapper = document.createElement('div');
  cellWrapper.className = INPUTS_CLASSES.cell;

  return cellWrapper;
};
const _description = () => {
  const p = document.createElement('p');
  p.className = INPUTS_CLASSES.description;

  return p;
};
const _options = () => {
  const optionsWrapper = document.createElement('div');
  optionsWrapper.className = INPUTS_CLASSES.options;

  return optionsWrapper;
};
const _title = (store: WorkflowStore) => {
  const lfIcon = theme.get.icon('download');

  const title = document.createElement('div');
  const h3 = document.createElement('h3');
  const openButton = document.createElement('lf-button');

  title.className = INPUTS_CLASSES.title;

  h3.className = INPUTS_CLASSES.h3;

  const label = 'Download Workflow JSON';
  openButton.className = INPUTS_CLASSES.openButton;
  openButton.lfAriaLabel = label;
  openButton.lfIcon = lfIcon;
  openButton.lfStyling = 'icon';
  openButton.lfUiSize = 'xsmall';
  openButton.title = label;
  openButton.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  title.appendChild(h3);
  title.appendChild(openButton);

  return { h3, openButton, title };
};
//#endregion

export const createInputsSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { WORKFLOW_INPUTS_DESTROYED, WORKFLOW_INPUTS_MOUNTED, WORKFLOW_INPUTS_UPDATED } =
    DEBUG_MESSAGES;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in INPUTS_CLASSES) {
      const element = INPUTS_CLASSES[cls];
      uiRegistry.remove(element);
    }

    debugLog(WORKFLOW_INPUTS_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[INPUTS_CLASSES._]) {
      return;
    }

    const workflow = manager.workflow.current();

    const _root = document.createElement('section');
    _root.className = INPUTS_CLASSES._;

    const description = _description();
    const options = _options();
    const { h3, openButton, title } = _title(store);

    const cellElements: WorkflowUICells = [];
    if (workflow) {
      const inputCells = manager.workflow.cells('input');
      for (const id in inputCells) {
        if (!Object.prototype.hasOwnProperty.call(inputCells, id)) {
          continue;
        }

        const cell = inputCells[id];

        const wrapper = _cells();
        wrapper.dataset.shape = cell.shape || '';

        const component = createInputCell(cell);
        component.id = id;

        cellElements.push(component);
        wrapper.appendChild(component);
        options.appendChild(wrapper);
      }
    }

    uiRegistry.set(INPUTS_CLASSES.cells, cellElements);

    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(options);

    elements[MAIN_CLASSES._].appendChild(_root);

    uiRegistry.set(INPUTS_CLASSES._, _root);
    uiRegistry.set(INPUTS_CLASSES.description, description);
    uiRegistry.set(INPUTS_CLASSES.h3, h3);
    uiRegistry.set(INPUTS_CLASSES.openButton, openButton);
    uiRegistry.set(INPUTS_CLASSES.options, options);
    uiRegistry.set(INPUTS_CLASSES.title, title);

    debugLog(WORKFLOW_INPUTS_MOUNTED);
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

    const cells = elements[INPUTS_CLASSES.cells] as WorkflowUICells;
    const descr = elements[INPUTS_CLASSES.description] as HTMLElement;
    const h3 = elements[INPUTS_CLASSES.h3] as HTMLElement;
    descr.textContent = manager.workflow.description();
    h3.textContent = manager.workflow.title();

    const statuses = state.inputStatuses || {};

    cells?.forEach((cell) => {
      const id = cell.id;
      const parent = cell?.parentElement;
      const status = statuses[id] || '';
      if (cell && parent) {
        if (status) {
          parent.dataset.status = status;
        } else {
          delete parent.dataset.status;
        }
      }
    });

    debugLog(WORKFLOW_INPUTS_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
//#endregion
