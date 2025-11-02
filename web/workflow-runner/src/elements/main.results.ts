import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/button';
import { WorkflowSectionController } from '../types/section';
import { WorkflowRunEntry, WorkflowStore } from '../types/state';
import {
  clearChildren,
  deepMerge,
  formatStatus,
  formatTimestamp,
  stringifyDetail,
  summarizeDetail,
} from '../utils/common';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { createComponent, createOutputComponent } from './components';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'results-section';
export const RESULTS_CLASSES = {
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
  subtitle: theme.bemClass(ROOT_CLASS, 'subtitle'),
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
  p.className = RESULTS_CLASSES.description;

  return p;
};
const _results = () => {
  const cellWrapper = document.createElement('div');
  cellWrapper.className = RESULTS_CLASSES.results;

  return cellWrapper;
};
const _title = (store: WorkflowStore) => {
  const { arrowBack, folder } = theme.get.icons();
  const { manager } = store.getState();

  const title = document.createElement('div');
  title.className = RESULTS_CLASSES.title;

  const h3 = document.createElement('h3');
  h3.className = RESULTS_CLASSES.h3;

  const actions = document.createElement('div');
  actions.className = RESULTS_CLASSES.actions;

  const backButton = document.createElement('lf-button');
  backButton.className = RESULTS_CLASSES.back;
  backButton.lfIcon = arrowBack;
  backButton.lfLabel = 'Back';
  backButton.lfStyling = 'flat';
  backButton.lfUiSize = 'small';
  backButton.lfUiState = 'disabled';
  backButton.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  const historyButton = document.createElement('lf-button');
  historyButton.className = RESULTS_CLASSES.history;
  historyButton.lfIcon = folder;
  historyButton.lfLabel = 'History';
  historyButton.lfStyling = 'flat';
  historyButton.lfUiSize = 'small';
  historyButton.lfUiState = manager.runs.all().length === 0 ? 'disabled' : 'primary';
  historyButton.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

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

    for (const cls in RESULTS_CLASSES) {
      const element = RESULTS_CLASSES[cls];
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
    if (elements && elements[RESULTS_CLASSES._]) {
      return;
    }

    const _root = document.createElement('section');
    _root.className = RESULTS_CLASSES._;

    const results = _results();
    const description = _description();
    const { actions, backButton, h3, historyButton, title } = _title(store);

    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(results);

    elements[MAIN_CLASSES._].prepend(_root);

    uiRegistry.set(RESULTS_CLASSES._, _root);
    uiRegistry.set(RESULTS_CLASSES.actions, actions);
    uiRegistry.set(RESULTS_CLASSES.back, backButton);
    uiRegistry.set(RESULTS_CLASSES.description, description);
    uiRegistry.set(RESULTS_CLASSES.h3, h3);
    uiRegistry.set(RESULTS_CLASSES.history, historyButton);
    uiRegistry.set(RESULTS_CLASSES.results, results);
    uiRegistry.set(RESULTS_CLASSES.title, title);

    debugLog(WORKFLOW_RESULTS_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const { syntax } = getLfFramework();
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const selectedRun = manager.runs.selected();
    const runs = manager.runs.all();

    const descr = elements[RESULTS_CLASSES.description] as HTMLElement;
    const element = elements[RESULTS_CLASSES.results] as HTMLElement;
    const h3 = elements[RESULTS_CLASSES.h3] as HTMLElement;
    const backButton = elements[RESULTS_CLASSES.back] as HTMLLfButtonElement | undefined;
    const historyButton = elements[RESULTS_CLASSES.history] as HTMLLfButtonElement | undefined;

    descr.textContent = _formatDescription(selectedRun, manager.workflow.description());
    h3.textContent = selectedRun?.workflowName || manager.workflow.title();
    backButton.lfUiState = selectedRun ? 'primary' : 'disabled';
    historyButton.lfUiState = runs.length > 0 ? 'primary' : 'disabled';

    const outputs = state.results ?? selectedRun?.outputs ?? null;
    clearChildren(element);

    const nodeIds = outputs ? Object.keys(outputs) : [];
    if (nodeIds.length === 0) {
      const empty = document.createElement('p');
      empty.className = RESULTS_CLASSES.empty;
      const summary = summarizeDetail(selectedRun?.error ?? null);
      if (selectedRun) {
        empty.textContent = summary
          ? `This run has not produced any outputs yet. ${summary}`
          : 'This run has not produced any outputs yet.';
      } else {
        empty.textContent = 'Select a run to inspect its outputs.';
      }
      element.appendChild(empty);

      const appendCodeBlock = (label: string, content: string | null) => {
        if (!content) {
          return;
        }

        const wrapper = document.createElement('div');
        wrapper.className = RESULTS_CLASSES.item;

        const heading = document.createElement('h4');
        heading.className = RESULTS_CLASSES.subtitle;
        heading.textContent = label;

        const code = createComponent.code({
          lfLanguage: syntax.json.isLikeString(content) ? 'json' : 'markdown',
          lfStickyHeader: false,
          lfUiState: 'danger',
          lfValue: content,
        });

        wrapper.appendChild(heading);
        wrapper.appendChild(code);

        element.appendChild(wrapper);
      };

      appendCodeBlock('Error detail', stringifyDetail(selectedRun?.error ?? null));
      appendCodeBlock(
        'Run payload',
        stringifyDetail(selectedRun?.resultPayload?.body ?? selectedRun?.resultPayload ?? null),
      );

      return;
    }

    const workflow = manager.workflow.current();
    const outputsDefs = workflow ? manager.workflow.cells('output') : {};

    const prepOutputs = deepMerge(outputsDefs, outputs || {});

    for (let i = 0; i < prepOutputs.length; i++) {
      const output = prepOutputs[i];
      const { id, nodeId, title } = output;

      const h4 = document.createElement('h4');
      h4.className = RESULTS_CLASSES.subtitle;
      h4.textContent = title || `Node #${nodeId}`;
      element.appendChild(h4);

      const grid = document.createElement('div');
      grid.className = RESULTS_CLASSES.grid;
      element.appendChild(grid);

      const wrapper = document.createElement('div');
      wrapper.className = RESULTS_CLASSES.item;

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
