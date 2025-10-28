import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/button';
import { WorkflowNodeResults } from '../types/api';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { formatStatus, formatTimestamp } from '../utils/common';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'outputs-section';
export const OUTPUTS_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  empty: theme.bemClass(ROOT_CLASS, 'empty'),
  h4: theme.bemClass(ROOT_CLASS, 'title-h4'),
  controls: theme.bemClass(ROOT_CLASS, 'controls'),
  item: theme.bemClass(ROOT_CLASS, 'item'),
  itemHeader: theme.bemClass(ROOT_CLASS, 'item-header'),
  itemMeta: theme.bemClass(ROOT_CLASS, 'item-meta'),
  itemTitle: theme.bemClass(ROOT_CLASS, 'item-title'),
  masonry: theme.bemClass(ROOT_CLASS, 'masonry'),
  status: theme.bemClass(ROOT_CLASS, 'status'),
  timestamp: theme.bemClass(ROOT_CLASS, 'timestamp'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
  toggle: theme.bemClass(ROOT_CLASS, 'toggle'),
} as const;
//#endregion

//#region Helpers
const _cloneOutputs = (outputs: WorkflowNodeResults | null) => {
  if (!outputs) {
    return null;
  }
  try {
    return JSON.parse(JSON.stringify(outputs));
  } catch (error) {
    return outputs;
  }
};
const _masonry = () => {
  const masonryWrapper = document.createElement('div');
  masonryWrapper.className = OUTPUTS_CLASSES.masonry;

  return masonryWrapper;
};
const _title = (store: WorkflowStore) => {
  const title = document.createElement('div');
  title.className = OUTPUTS_CLASSES.title;

  const h4 = document.createElement('h4');
  h4.className = OUTPUTS_CLASSES.h4;

  const controls = document.createElement('div');
  controls.className = OUTPUTS_CLASSES.controls;

  const toggle = document.createElement('lf-button');
  toggle.className = OUTPUTS_CLASSES.toggle;
  toggle.lfStyling = 'flat';
  toggle.lfUiSize = 'small';
  toggle.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  title.appendChild(h4);
  title.appendChild(controls);
  controls.appendChild(toggle);

  return { h4, title, controls, toggle };
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

    for (const cls in OUTPUTS_CLASSES) {
      const element = OUTPUTS_CLASSES[cls];
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
    if (elements && elements[OUTPUTS_CLASSES._]) {
      return;
    }

    const _root = document.createElement('section');
    _root.className = OUTPUTS_CLASSES._;

    const { controls, h4, title, toggle } = _title(store);
    const masonry = _masonry();

    _root.appendChild(title);
    _root.appendChild(masonry);

    elements[MAIN_CLASSES._].appendChild(_root);

    uiRegistry.set(OUTPUTS_CLASSES._, _root);
    uiRegistry.set(OUTPUTS_CLASSES.controls, controls);
    uiRegistry.set(OUTPUTS_CLASSES.h4, h4);
    uiRegistry.set(OUTPUTS_CLASSES.masonry, masonry);
    uiRegistry.set(OUTPUTS_CLASSES.title, title);
    uiRegistry.set(OUTPUTS_CLASSES.toggle, toggle);

    debugLog(WORKFLOW_OUTPUTS_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const { arrowBack, folder } = theme.get.icons();

    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const h4 = elements[OUTPUTS_CLASSES.h4] as HTMLElement;
    const masonry = elements[OUTPUTS_CLASSES.masonry] as HTMLDivElement;
    const toggle = elements[OUTPUTS_CLASSES.toggle] as HTMLLfButtonElement;

    if (!h4 || !masonry || !toggle) {
      return;
    }

    const activeWorkflowId = state.current.id;
    const allRuns = manager.runs.all();
    const hasAnyRuns = allRuns.length > 0;
    const isHistoryView = state.view === 'history';
    const selectedRunId = state.selectedRunId;
    const workflowTitle = manager.workflow.title();
    h4.textContent = workflowTitle ? `${workflowTitle} outputs` : 'Workflow outputs';

    masonry.replaceChildren();

    const runs = isHistoryView
      ? allRuns
      : allRuns.filter((run) => (run.workflowId ?? null) === (activeWorkflowId ?? null));

    toggle.lfIcon = isHistoryView ? arrowBack : folder;
    toggle.lfLabel = isHistoryView ? 'Back to workflow view' : 'Open full history';
    toggle.lfUiState = hasAnyRuns || isHistoryView ? 'primary' : 'disabled';

    if (!runs.length) {
      const empty = document.createElement('p');
      empty.className = OUTPUTS_CLASSES.empty;
      empty.textContent = isHistoryView
        ? 'Run a workflow to start building your history.'
        : 'No runs for this workflow yet. Open full history to browse previous runs.';
      masonry.appendChild(empty);

      debugLog(WORKFLOW_OUTPUTS_UPDATED);

      return;
    }

    for (const run of runs) {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = OUTPUTS_CLASSES.item;
      item.dataset.runId = run.runId;
      item.dataset.status = run.status;
      item.dataset.selected = String(run.runId === selectedRunId);
      item.setAttribute('aria-pressed', String(run.runId === selectedRunId));

      const header = document.createElement('div');
      header.className = OUTPUTS_CLASSES.itemHeader;

      const title = document.createElement('span');
      title.className = OUTPUTS_CLASSES.itemTitle;
      title.textContent = run.workflowName || workflowTitle || 'Workflow run';

      const status = document.createElement('span');
      status.className = OUTPUTS_CLASSES.status;
      status.textContent = formatStatus(run.status);
      status.dataset.state = run.status;

      header.appendChild(title);
      header.appendChild(status);

      const meta = document.createElement('div');
      meta.className = OUTPUTS_CLASSES.itemMeta;

      const timestamp = document.createElement('span');
      timestamp.className = OUTPUTS_CLASSES.timestamp;
      timestamp.textContent = formatTimestamp(run.updatedAt || run.createdAt);
      meta.appendChild(timestamp);

      if (run.error) {
        const error = document.createElement('span');
        error.className = OUTPUTS_CLASSES.status;
        error.dataset.state = 'error';
        error.textContent = run.error;
        meta.appendChild(error);
      }

      item.appendChild(header);
      item.appendChild(meta);

      item.addEventListener('click', () => {
        manager.runs.select(run.runId, 'run');
        const selected = manager.runs.get(run.runId);
        const selectedOutputs = _cloneOutputs(selected?.outputs ?? null);
        store.getState().mutate.results(selectedOutputs);
      });

      masonry.appendChild(item);
    }

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
