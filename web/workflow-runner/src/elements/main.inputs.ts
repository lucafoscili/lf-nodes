import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/button';
import { WorkflowCellInput } from '../types/api';
import { WorkflowSectionController, WorkflowUICells } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { consumeArtifactHandoff } from '../utils/artifact-handoff';
import { createInputCell } from './components';
import { MAIN_CLASSES } from './layout.main';
import {
  clearRetainedUploadPrefill,
  RETAINED_UPLOAD_EVENT,
} from '../utils/input-prefill';
import {
  applyWorkflowSessionDraft,
  captureWorkflowSessionDraft,
  clearWorkflowSessionDraft,
  getWorkflowSessionDraft,
  replaceWorkflowSessionDraft,
  watchWorkflowSessionDraft,
} from '../utils/session-drafts';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'inputs-section';
export const INPUTS_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  cell: theme.bemClass(ROOT_CLASS, 'cell'),
  cells: theme.bemClass(ROOT_CLASS, 'cells'),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  help: theme.bemClass(ROOT_CLASS, 'help'),
  h3: theme.bemClass(ROOT_CLASS, 'title-h3'),
  openButton: theme.bemClass(ROOT_CLASS, 'title-open-button'),
  resetButton: theme.bemClass(ROOT_CLASS, 'title-reset-button'),
  options: theme.bemClass(ROOT_CLASS, 'options'),
  readiness: theme.bemClass(ROOT_CLASS, 'readiness'),
  retainedUpload: theme.bemClass(ROOT_CLASS, 'retained-upload'),
  retainedUploadClear: theme.bemClass(ROOT_CLASS, 'retained-upload-clear'),
  retainedUploadText: theme.bemClass(ROOT_CLASS, 'retained-upload-text'),
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
const _title = (store: WorkflowStore, onReset: () => void) => {
  const download = theme.get.icon('download');
  const refresh = theme.get.icon('refresh');

  const title = document.createElement('div');
  const h3 = document.createElement('h3');
  const resetButton = document.createElement('lf-button');
  const openButton = document.createElement('lf-button');

  title.className = INPUTS_CLASSES.title;

  h3.className = INPUTS_CLASSES.h3;

  resetButton.className = INPUTS_CLASSES.resetButton;
  resetButton.lfAriaLabel = 'Reset this workflow form to its defaults';
  resetButton.lfIcon = refresh;
  resetButton.lfLabel = 'Reset';
  resetButton.lfStyling = 'flat';
  resetButton.lfUiSize = 'xsmall';
  resetButton.addEventListener('lf-button-event', (event) => {
    if ((event as CustomEvent<{ eventType?: string }>).detail?.eventType === 'click') {
      onReset();
    }
  });

  const label = 'Download Workflow JSON';
  openButton.className = INPUTS_CLASSES.openButton;
  openButton.lfAriaLabel = label;
  openButton.lfIcon = download;
  openButton.lfStyling = 'icon';
  openButton.lfUiSize = 'xsmall';
  openButton.title = label;
  openButton.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  title.appendChild(h3);
  title.appendChild(resetButton);
  title.appendChild(openButton);

  return { h3, openButton, resetButton, title };
};
const _help = (value?: string) => {
  if (!value) {
    return null;
  }

  const p = document.createElement('p');
  p.className = INPUTS_CLASSES.help;
  p.textContent = value;
  return p;
};
const _readiness = () => {
  const notice = document.createElement('aside');
  notice.className = INPUTS_CLASSES.readiness;
  notice.hidden = true;
  notice.setAttribute('role', 'status');
  return notice;
};
const _helperHasValue = (helper: unknown) => {
  if (typeof helper === 'string') {
    return Boolean(helper.trim());
  }
  if (!helper || typeof helper !== 'object') {
    return false;
  }
  const value = (helper as Record<string, unknown>).value;
  return typeof value === 'string' && Boolean(value.trim());
};
const _hasNativeHelper = (cell: WorkflowCellInput) => {
  const props = cell.props as Record<string, unknown> | undefined;
  if (!props) {
    return false;
  }

  if (!cell.shape || cell.shape === 'textfield') {
    return _helperHasValue(props.lfHelper);
  }

  if (cell.shape === 'choice' || cell.shape === 'select') {
    const textfieldProps = props.lfTextfieldProps;
    return Boolean(
      textfieldProps &&
        typeof textfieldProps === 'object' &&
        _helperHasValue((textfieldProps as Record<string, unknown>).lfHelper),
    );
  }

  return false;
};
const _retainedUpload = (component: HTMLElement) => {
  const retained = document.createElement('div');
  const text = document.createElement('span');
  const clear = document.createElement('button');

  retained.className = INPUTS_CLASSES.retainedUpload;
  retained.hidden = true;
  text.className = INPUTS_CLASSES.retainedUploadText;
  clear.className = INPUTS_CLASSES.retainedUploadClear;
  clear.type = 'button';
  clear.textContent = 'Clear';
  clear.setAttribute('aria-label', 'Stop reusing the previous upload');

  component.addEventListener(RETAINED_UPLOAD_EVENT, (event) => {
    const detail = (
      event as CustomEvent<{ available?: boolean; names?: string[]; retained?: boolean }>
    ).detail;
    const names = Array.isArray(detail?.names) ? detail.names : [];
    retained.hidden = !detail?.retained;
    text.textContent = detail?.retained
      ? detail.available
        ? `Reusing ${names.length > 1 ? `${names.length} previous uploads` : names[0] || 'previous upload'}. Choose a new file to replace it.`
        : `${names.length > 1 ? `${names.length} previous uploads are` : `${names[0] || 'The previous upload'} is`} no longer available. Choose the file${names.length > 1 ? 's' : ''} again.`
      : '';
  });
  component.addEventListener('lf-upload-event', (event) => {
    const detail = (event as CustomEvent<{ eventType?: string; selectedFiles?: File[] }>).detail;
    if (detail?.eventType === 'upload' && detail.selectedFiles?.length) {
      clearRetainedUploadPrefill(component);
    }
  });
  clear.addEventListener('click', () => clearRetainedUploadPrefill(component));

  retained.append(text, clear);
  return retained;
};
//#endregion

export const createInputsSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { WORKFLOW_INPUTS_DESTROYED, WORKFLOW_INPUTS_MOUNTED, WORKFLOW_INPUTS_UPDATED } =
    DEBUG_MESSAGES;
  let activeHydration: number | null = null;
  let mountGeneration = 0;
  let mountedCells: WorkflowUICells = [];
  let mountedWorkflowId: string | null = null;
  let skipDestroyCapture = false;
  let stopWatchingDraft: (() => void) | null = null;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const wasHydrating = activeHydration !== null;
    mountGeneration += 1;
    activeHydration = null;
    stopWatchingDraft?.();
    stopWatchingDraft = null;
    if (!skipDestroyCapture && !wasHydrating && mountedWorkflowId && mountedCells.length > 0) {
      void captureWorkflowSessionDraft(store, mountedWorkflowId, mountedCells);
    }

    for (const cls in INPUTS_CLASSES) {
      const element = INPUTS_CLASSES[cls];
      uiRegistry.remove(element);
    }
    mountedCells = [];
    mountedWorkflowId = null;

    debugLog(WORKFLOW_INPUTS_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[INPUTS_CLASSES._]) {
      return;
    }

    const workflow = manager.workflow.current();
    const workflowId = workflow?.id || state.current?.id || null;
    const generation = ++mountGeneration;

    const _root = document.createElement('section');
    _root.className = INPUTS_CLASSES._;

    const description = _description();
    const readiness = _readiness();
    const options = _options();
    const reset = () => {
      if (!mountedWorkflowId) {
        return;
      }
      clearWorkflowSessionDraft(store, mountedWorkflowId);
      store.getState().mutate.inputPrefillRun(null);
      skipDestroyCapture = true;
      try {
        destroy();
      } finally {
        skipDestroyCapture = false;
      }
      mount();
      render();
    };
    const { h3, openButton, resetButton, title } = _title(store, reset);

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
        if (cell.required === false) {
          component.dataset.required = 'false';
        }

        cellElements.push(component);
        wrapper.appendChild(component);
        const help = _hasNativeHelper(cell) ? null : _help(cell.title);
        if (help) {
          wrapper.appendChild(help);
        }
        if (cell.shape === 'upload') {
          wrapper.appendChild(_retainedUpload(component));
        }
        options.appendChild(wrapper);
      }
    }

    uiRegistry.set(INPUTS_CLASSES.cells, cellElements);

    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(readiness);
    _root.appendChild(options);

    elements[MAIN_CLASSES._].prepend(_root);

    uiRegistry.set(INPUTS_CLASSES._, _root);
    uiRegistry.set(INPUTS_CLASSES.description, description);
    uiRegistry.set(INPUTS_CLASSES.h3, h3);
    uiRegistry.set(INPUTS_CLASSES.openButton, openButton);
    uiRegistry.set(INPUTS_CLASSES.resetButton, resetButton);
    uiRegistry.set(INPUTS_CLASSES.options, options);
    uiRegistry.set(INPUTS_CLASSES.readiness, readiness);
    uiRegistry.set(INPUTS_CLASSES.title, title);

    mountedCells = cellElements;
    mountedWorkflowId = workflowId;

    if (workflowId) {
      const currentState = store.getState();
      const artifactPrefill = consumeArtifactHandoff(store, workflowId);
      let prefill: Record<string, unknown> | undefined = artifactPrefill;
      let isIntentionalOverride = Boolean(artifactPrefill);

      if (!prefill && currentState.inputPrefillRunId) {
        const pendingRunId = currentState.inputPrefillRunId;
        const run = manager.runs.get(pendingRunId);
        // Remix is a one-shot, intentional replacement of an ordinary draft.
        currentState.mutate.inputPrefillRun(null);
        if (run?.workflowId === workflowId && run.inputs) {
          prefill = run.inputs;
          isIntentionalOverride = true;
        }
      }

      const values = prefill || getWorkflowSessionDraft(store, workflowId);
      if (values) {
        if (isIntentionalOverride) {
          replaceWorkflowSessionDraft(store, workflowId, values);
        }
        activeHydration = generation;
        void applyWorkflowSessionDraft(cellElements, values).finally(() => {
          if (activeHydration === generation) {
            activeHydration = null;
          }
        });
      }

      stopWatchingDraft = watchWorkflowSessionDraft(
        store,
        workflowId,
        cellElements,
        () => activeHydration !== generation,
      );
    }

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
    const readiness = elements[INPUTS_CLASSES.readiness] as HTMLElement | undefined;
    const workflow = manager.workflow.current();
    descr.textContent = manager.workflow.description();
    h3.textContent = manager.workflow.title();
    if (readiness) {
      const status = workflow?.readiness?.status;
      const issues = workflow?.readiness?.issues || [];
      readiness.hidden = !status || status === 'ready';
      if (status && status !== 'ready') {
        readiness.dataset.status = status;
        const prefix = status === 'setup_required' ? 'Setup required' : 'Setup check';
        readiness.textContent = `${prefix}: ${issues[0]?.message || 'Review this workflow before running.'}`;
      } else {
        readiness.textContent = '';
        delete readiness.dataset.status;
      }
    }

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
