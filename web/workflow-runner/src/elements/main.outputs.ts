import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowSectionController } from '../types/section';
import { WorkflowNodeResults } from '../types/api';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'outputs-section';
export const WORKFLOW_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  empty: theme.bemClass(ROOT_CLASS, 'empty'),
  h4: theme.bemClass(ROOT_CLASS, 'title-h4'),
  item: theme.bemClass(ROOT_CLASS, 'item'),
  itemHeader: theme.bemClass(ROOT_CLASS, 'item-header'),
  itemMeta: theme.bemClass(ROOT_CLASS, 'item-meta'),
  itemTitle: theme.bemClass(ROOT_CLASS, 'item-title'),
  masonry: theme.bemClass(ROOT_CLASS, 'masonry'),
  status: theme.bemClass(ROOT_CLASS, 'status'),
  timestamp: theme.bemClass(ROOT_CLASS, 'timestamp'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
const _masonry = () => {
  const masonryWrapper = document.createElement('div');
  masonryWrapper.className = WORKFLOW_CLASSES.masonry;

  return masonryWrapper;
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
    const masonry = elements[WORKFLOW_CLASSES.masonry] as HTMLDivElement;
    if (!h4 || !masonry) {
      return;
    }

    const workflowTitle = manager.workflow.title();
    h4.textContent = workflowTitle ? `${workflowTitle} outputs` : 'Workflow outputs';

    masonry.replaceChildren();

    const runs = manager.runs.all();
    const selectedRunId = state.selectedRunId;

    if (!runs.length) {
      const empty = document.createElement('p');
      empty.className = WORKFLOW_CLASSES.empty;
      empty.textContent = 'Run a workflow to start building your history.';
      masonry.appendChild(empty);
      debugLog(WORKFLOW_OUTPUTS_UPDATED);
      return;
    }

    for (const run of runs) {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = WORKFLOW_CLASSES.item;
      item.dataset.runId = run.runId;
      item.dataset.status = run.status;
      item.dataset.selected = String(run.runId === selectedRunId);
      item.setAttribute('aria-pressed', String(run.runId === selectedRunId));

      const header = document.createElement('div');
      header.className = WORKFLOW_CLASSES.itemHeader;

      const title = document.createElement('span');
      title.className = WORKFLOW_CLASSES.itemTitle;
      title.textContent = run.workflowName || workflowTitle || 'Workflow run';

      const status = document.createElement('span');
      status.className = WORKFLOW_CLASSES.status;
      status.textContent = _formatStatus(run.status);
      status.dataset.state = run.status;

      header.appendChild(title);
      header.appendChild(status);

      const meta = document.createElement('div');
      meta.className = WORKFLOW_CLASSES.itemMeta;

      const timestamp = document.createElement('span');
      timestamp.className = WORKFLOW_CLASSES.timestamp;
      timestamp.textContent = _formatTimestamp(run.updatedAt || run.createdAt);
      meta.appendChild(timestamp);

      if (run.error) {
        const error = document.createElement('span');
        error.className = WORKFLOW_CLASSES.status;
        error.dataset.state = 'error';
        error.textContent = run.error;
        meta.appendChild(error);
      }

      item.appendChild(header);
      item.appendChild(meta);

      item.addEventListener('click', () => {
        manager.runs.select(run.runId);
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
