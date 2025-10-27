import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { clearChildren, deepMerge } from '../utils/common';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { createOutputComponent } from './components';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'results-section';
export const WORKFLOW_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  empty: theme.bemClass(ROOT_CLASS, 'empty'),
  grid: theme.bemClass(ROOT_CLASS, 'grid'),
  h3: theme.bemClass(ROOT_CLASS, 'title-h3'),
  item: theme.bemClass(ROOT_CLASS, 'item'),
  results: theme.bemClass(ROOT_CLASS, 'results'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
const _results = () => {
  const cellWrapper = document.createElement('div');
  cellWrapper.className = WORKFLOW_CLASSES.results;

  return cellWrapper;
};
const _description = () => {
  const p = document.createElement('p');
  p.className = WORKFLOW_CLASSES.description;

  return p;
};
const _title = () => {
  const title = document.createElement('div');
  const h3 = document.createElement('h3');

  title.className = WORKFLOW_CLASSES.title;

  h3.className = WORKFLOW_CLASSES.h3;

  title.appendChild(h3);

  return { h3, title };
};
const _formatStatus = (status: string) =>
  status.charAt(0).toUpperCase() + status.slice(1);
const _formatTimestamp = (timestamp: number) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return 'Unknown time';
  }
  return date.toLocaleString();
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
    const description = _description(); // TODO: description should include the id of the prompt
    const { h3, title } = _title();

    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(results);

    elements[MAIN_CLASSES._].appendChild(_root);

    uiRegistry.set(WORKFLOW_CLASSES._, _root);
    uiRegistry.set(WORKFLOW_CLASSES.description, description);
    uiRegistry.set(WORKFLOW_CLASSES.h3, h3);
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
    const titleText = selectedRun?.workflowName || manager.workflow.title();
    const descriptionText = selectedRun
      ? `Run ${selectedRun.runId.slice(0, 8)} • ${_formatStatus(selectedRun.status)} • ${_formatTimestamp(
          selectedRun.updatedAt || selectedRun.createdAt,
        )}`
      : manager.workflow.description();

    descr.textContent = descriptionText;
    h3.textContent = titleText;

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
