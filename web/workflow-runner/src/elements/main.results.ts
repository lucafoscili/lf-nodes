import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowSectionController } from '../types/section';
import { WorkflowRunEntry, WorkflowStore } from '../types/state';
import { clearChildren, deepMerge, formatStatus, formatTimestamp } from '../utils/common';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { createOutputComponent } from './components';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'results-section';
export const WORKFLOW_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  actions: theme.bemClass(ROOT_CLASS, 'actions'),
  back: theme.bemClass(ROOT_CLASS, 'back'),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  empty: theme.bemClass(ROOT_CLASS, 'empty'),
  grid: theme.bemClass(ROOT_CLASS, 'grid'),
  h3: theme.bemClass(ROOT_CLASS, 'title-h3'),
  history: theme.bemClass(ROOT_CLASS, 'history'),
  item: theme.bemClass(ROOT_CLASS, 'item'),
  results: theme.bemClass(ROOT_CLASS, 'results'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
const _formatDescription = (selectedRun: WorkflowRunEntry | null, description: string) => {
  if (!selectedRun) {
    return description;
  }

  const timestamp = selectedRun.updatedAt || selectedRun.createdAt;
  return `Run ${selectedRun.runId.slice(0, 8)} - ${formatStatus(
    selectedRun.status,
  )} - ${formatTimestamp(timestamp)}`;
};
const _description = () => {
  const p = document.createElement('p');
  p.className = WORKFLOW_CLASSES.description;

  return p;
};
const _results = () => {
  const cellWrapper = document.createElement('div');
  cellWrapper.className = WORKFLOW_CLASSES.results;

  return cellWrapper;
};
const _title = (store: WorkflowStore) => {
  const { manager } = store.getState();

  const title = document.createElement('div');
  const h3 = document.createElement('h3');
  const actions = document.createElement('div');
  const backButton = document.createElement('lf-button');
  const historyButton = document.createElement('lf-button');

  title.className = WORKFLOW_CLASSES.title;
  actions.className = WORKFLOW_CLASSES.actions;

  h3.className = WORKFLOW_CLASSES.h3;
  backButton.className = WORKFLOW_CLASSES.back;
  historyButton.className = WORKFLOW_CLASSES.history;

  backButton.lfLabel = 'Back to workflow';
  backButton.lfStyling = 'flat';
  backButton.lfUiSize = 'small';
  backButton.onclick = () => manager.runs.select(null, 'workflow');
  backButton.toggleAttribute('disabled', true);

  historyButton.lfLabel = 'View all runs';
  historyButton.lfStyling = 'flat';
  historyButton.lfUiSize = 'small';
  historyButton.onclick = () => manager.runs.select(null, 'history');
  historyButton.toggleAttribute('disabled', manager.runs.all().length === 0);

  title.appendChild(h3);
  title.appendChild(actions);
  actions.appendChild(backButton);
  actions.appendChild(historyButton);

  return { actions, backButton, h3, historyButton, title };
};
//#endregion

export const createResultsSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { WORKFLOW_RESULTS_DESTROYED, WORKFLOW_RESULTS_MOUNTED, WORKFLOW_RESULTS_UPDATED } =
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

    debugLog(WORKFLOW_RESULTS_DESTROYED);
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

    const results = _results();
    const description = _description();
    const { actions, backButton, h3, historyButton, title } = _title(store);

    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(results);

    elements[MAIN_CLASSES._].appendChild(_root);

    uiRegistry.set(WORKFLOW_CLASSES._, _root);
    uiRegistry.set(WORKFLOW_CLASSES.actions, actions);
    uiRegistry.set(WORKFLOW_CLASSES.back, backButton);
    uiRegistry.set(WORKFLOW_CLASSES.description, description);
    uiRegistry.set(WORKFLOW_CLASSES.h3, h3);
    uiRegistry.set(WORKFLOW_CLASSES.history, historyButton);
    uiRegistry.set(WORKFLOW_CLASSES.results, results);
    uiRegistry.set(WORKFLOW_CLASSES.title, title);

    debugLog(WORKFLOW_RESULTS_MOUNTED);
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

    const descr = elements[WORKFLOW_CLASSES.description] as HTMLElement;
    const element = elements[WORKFLOW_CLASSES.results] as HTMLElement;
    const h3 = elements[WORKFLOW_CLASSES.h3] as HTMLElement;
    const selectedRun = manager.runs.selected();
    const runs = manager.runs.all();
    const backButton = elements[WORKFLOW_CLASSES.back] as HTMLLfButtonElement | undefined;
    const historyButton = elements[WORKFLOW_CLASSES.history] as HTMLLfButtonElement | undefined;

    backButton?.toggleAttribute('disabled', !selectedRun);
    historyButton?.toggleAttribute('disabled', runs.length === 0);

    descr.textContent = _formatDescription(selectedRun, manager.workflow.description());
    h3.textContent = selectedRun?.workflowName || manager.workflow.title();

    const outputs = state.results ?? selectedRun?.outputs ?? null;
    clearChildren(element);

    const nodeIds = outputs ? Object.keys(outputs) : [];
    if (nodeIds.length === 0) {
      const empty = document.createElement('p');
      empty.className = WORKFLOW_CLASSES.empty;
      empty.textContent = selectedRun
        ? 'This run has not produced any outputs yet.'
        : 'Select a run to inspect its outputs.';
      element.appendChild(empty);
      return;
    }

    const workflow = manager.workflow.current();
    const outputsDefs = workflow ? manager.workflow.cells('output') : {};

    const prepOutputs = deepMerge(outputsDefs, outputs || {});

    for (let i = 0; i < prepOutputs.length; i++) {
      const output = prepOutputs[i];
      const { id, nodeId, title } = output;

      const h4 = document.createElement('h4');
      h4.className = WORKFLOW_CLASSES.title;
      h4.textContent = title || `Node #${nodeId}`;
      element.appendChild(h4);

      const grid = document.createElement('div');
      grid.className = WORKFLOW_CLASSES.grid;
      element.appendChild(grid);

      const wrapper = document.createElement('div');
      wrapper.className = WORKFLOW_CLASSES.item;

      const component = createOutputComponent(output);
      component.id = id;

      wrapper.appendChild(component);
      grid.appendChild(wrapper);
    }

    debugLog(WORKFLOW_RESULTS_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
//#endregion
