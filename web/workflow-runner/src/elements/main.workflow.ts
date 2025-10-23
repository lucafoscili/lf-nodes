import { getLfFramework } from '@lf-widgets/framework';
import {
  WorkflowAPIItem,
  WorkflowCellOutputItem,
  WorkflowCellsInputContainer,
  WorkflowCellsOutputContainer,
  WorkflowNodeResults,
} from '../types/api';
import { WorkflowSectionController, WorkflowUICells } from '../types/section';
import { WorkflowState, WorkflowStore } from '../types/state';
import { clearChildren } from '../utils/common';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { createInputCell, createOutputComponent } from './components';
import { MAIN_CLASSES } from './layout.main';

//#region Constants
const WORKFLOW_TEXT = 'Select a workflow';
//#endregion

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'workflow-section';
export const WORKFLOW_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  cell: theme.bemClass(ROOT_CLASS, 'cell'),
  cells: theme.bemClass(ROOT_CLASS, 'cells'),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  options: theme.bemClass(ROOT_CLASS, 'options'),
  result: theme.bemClass(ROOT_CLASS, 'result'),
  resultGrid: theme.bemClass(ROOT_CLASS, 'result-grid'),
  resultItem: theme.bemClass(ROOT_CLASS, 'result-item'),
  resultTitle: theme.bemClass(ROOT_CLASS, 'result-title'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
const _createCellWrapper = () => {
  const cellWrapper = document.createElement('div');
  cellWrapper.className = WORKFLOW_CLASSES.cell;

  return cellWrapper;
};
const _createDescription = (state: WorkflowState) => {
  const p = document.createElement('p');
  p.className = WORKFLOW_CLASSES.description;
  p.textContent = _getWorkflowDescription(state);

  return p;
};
const _createOptionsWrapper = () => {
  const optionsWrapper = document.createElement('div');
  optionsWrapper.className = WORKFLOW_CLASSES.options;

  return optionsWrapper;
};
const _createResultWrapper = () => {
  const resultWrapper = document.createElement('div');
  resultWrapper.className = WORKFLOW_CLASSES.result;

  return resultWrapper;
};
const _createTitle = (state: WorkflowState) => {
  const h3 = document.createElement('h3');
  h3.className = WORKFLOW_CLASSES.title;
  h3.textContent = _getWorkflowTitle(state);

  return h3;
};
const _deepMerge = (defs: WorkflowCellsOutputContainer, outs: WorkflowNodeResults) => {
  const prep: WorkflowCellOutputItem[] = [];

  for (const id in defs) {
    const cell = defs[id];
    const { nodeId } = cell;
    const result = outs?.[nodeId]?.lf_output[0] || outs?.[nodeId]?.[0] || outs?.[nodeId];

    const item: WorkflowCellOutputItem = {
      ...JSON.parse(JSON.stringify(cell)),
      ...JSON.parse(JSON.stringify(result || {})),
    };
    prep.push(item);
  }

  return prep;
};
const _getCurrentWorkflow = (state: WorkflowState) => {
  const { current, workflows } = state;
  return workflows?.nodes?.find((node) => node.id === current.id) || null;
};
const _getWorkflowDescription = (state: WorkflowState) => {
  const workflow = _getCurrentWorkflow(state);
  return workflow?.description || '';
};
const _getWorkflowInputCells = (workflow: WorkflowAPIItem) => {
  const inputsSection = workflow.children?.find((child) => child.id.endsWith(':inputs'));
  return (inputsSection?.cells || {}) as WorkflowCellsInputContainer;
};
const _getWorkflowOutputCells = (workflow: WorkflowAPIItem) => {
  const outputsSection = workflow.children?.find((child) => child.id.endsWith(':outputs'));
  return (outputsSection?.cells || {}) as WorkflowCellsOutputContainer;
};
const _getWorkflowTitle = (state: WorkflowState) => {
  const workflow = _getCurrentWorkflow(state);
  const str = typeof workflow?.value === 'string' ? workflow.value : String(workflow?.value || '');
  return str || WORKFLOW_TEXT;
};
//#endregion

export const createWorkflowSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const {
    WORKFLOW_INPUTS_CLEARED,
    WORKFLOW_INPUTS_RENDERED,
    WORKFLOW_LAYOUT_DESTROYED,
    WORKFLOW_LAYOUT_MOUNTED,
    WORKFLOW_LAYOUT_UPDATED,
    WORKFLOW_RESULTS_CLEARED,
    WORKFLOW_RESULTS_RENDERED,
  } = DEBUG_MESSAGES;
  let lastId: string | null = null;
  let lastResultsRef: WorkflowNodeResults | null = null;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const state = store.getState();
    if (!state.manager) {
      return;
    }

    const { manager } = state;
    const { uiRegistry } = manager;

    for (const cls in WORKFLOW_CLASSES) {
      const element = WORKFLOW_CLASSES[cls];
      uiRegistry.remove(element);
    }

    lastId = null;
    lastResultsRef = null;

    debugLog(WORKFLOW_LAYOUT_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    if (!manager) {
      return;
    }

    const elements = uiRegistry.get();
    if (elements && elements[WORKFLOW_CLASSES._]) {
      return;
    }

    const _root = document.createElement('section');
    _root.className = WORKFLOW_CLASSES._;

    const description = _createDescription(state);
    const options = _createOptionsWrapper();
    const result = _createResultWrapper();
    const title = _createTitle(state);

    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(options);
    _root.appendChild(result);

    elements[MAIN_CLASSES._].appendChild(_root);

    uiRegistry.set(WORKFLOW_CLASSES._, _root);
    uiRegistry.set(WORKFLOW_CLASSES.description, description);
    uiRegistry.set(WORKFLOW_CLASSES.options, options);
    uiRegistry.set(WORKFLOW_CLASSES.result, result);
    uiRegistry.set(WORKFLOW_CLASSES.title, title);

    debugLog(WORKFLOW_LAYOUT_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const state = store.getState();
    const { current, manager } = state;
    const { id } = current;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    if (id !== lastId) {
      const descr = elements[WORKFLOW_CLASSES.description] as HTMLElement;
      const title = elements[WORKFLOW_CLASSES.title] as HTMLElement;
      descr.textContent = _getWorkflowDescription(state);
      title.textContent = _getWorkflowTitle(state);
      updateOptions();
      lastId = id;
    }

    if (state.results !== lastResultsRef) {
      updateResults();
      lastResultsRef = state.results;
    }

    debugLog(WORKFLOW_LAYOUT_UPDATED);
  };
  //#endregion

  //#region Update options
  const updateOptions = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    const element = elements[WORKFLOW_CLASSES.options] as HTMLElement;
    if (!element) {
      return;
    }

    clearChildren(element);

    const workflow = _getCurrentWorkflow(state);
    const cellElements: WorkflowUICells = [];

    if (workflow) {
      const inputCells = _getWorkflowInputCells(workflow);
      for (const id in inputCells) {
        if (!Object.prototype.hasOwnProperty.call(inputCells, id)) {
          continue;
        }
        const cell = inputCells[id];
        const wrapper = _createCellWrapper();
        const component = createInputCell(cell);
        component.id = id;

        cellElements.push(component);
        wrapper.appendChild(component);
        element.appendChild(wrapper);
      }
    }

    uiRegistry.set(WORKFLOW_CLASSES.cells, cellElements);

    if (workflow && cellElements.length) {
      debugLog(WORKFLOW_INPUTS_RENDERED);
    } else {
      debugLog(WORKFLOW_INPUTS_CLEARED);
    }
  };
  //#endregion

  //#region Update results
  const updateResults = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    const element = elements[WORKFLOW_CLASSES.result] as HTMLElement;
    if (!element) {
      return;
    }

    const outputs = state.results || {};
    clearChildren(element);

    const nodeIds = Object.keys(outputs);
    if (nodeIds.length === 0) {
      debugLog(WORKFLOW_RESULTS_CLEARED);
      return;
    }

    const workflow = _getCurrentWorkflow(state);
    const outputsDefs = workflow ? _getWorkflowOutputCells(workflow) : {};
    debugLog(WORKFLOW_RESULTS_CLEARED);

    const prepOutputs = _deepMerge(outputsDefs, outputs);

    for (let i = 0; i < prepOutputs.length; i++) {
      const output = prepOutputs[i];
      const { id, nodeId, title } = output;

      const h4 = document.createElement('h4');
      h4.className = WORKFLOW_CLASSES.resultTitle;
      h4.textContent = title || `Node #${nodeId}`;
      element.appendChild(h4);

      const grid = document.createElement('div');
      grid.className = WORKFLOW_CLASSES.resultGrid;
      element.appendChild(grid);

      const wrapper = document.createElement('div');
      wrapper.className = WORKFLOW_CLASSES.resultItem;

      const component = createOutputComponent(output);
      component.id = id;

      wrapper.appendChild(component);
      grid.appendChild(wrapper);
    }

    debugLog(WORKFLOW_RESULTS_RENDERED);
  };

  return {
    destroy,
    mount,
    render,
  };
};
//#endregion
