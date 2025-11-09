import {
  LfDataCell,
  LfDataCellContainer,
  LfDataDataset,
  LfThemeUIState,
} from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/button';
import { masonryHandler } from '../handlers/masonry';
import { WorkflowNodeResultPayload, WorkflowNodeResults, WorkflowRunStatus } from '../types/api';
import { WorkflowSectionController } from '../types/section';
import { WorkflowRunEntry, WorkflowStore } from '../types/state';
import { formatStatus, formatTimestamp, summarizeDetail } from '../utils/common';
import { DEBUG_MESSAGES, UI_CONSTANTS } from '../utils/constants';
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
const _emptyCardCell = () => {
  const lfCard: LfDataCell<'card'> = {
    lfDataset: {
      nodes: [
        {
          cells: {
            '1': {
              value: 'Empty',
            },
            '2': {
              value: 'No outputs to display',
            },
            '3': {
              value: 'Run a workflow to start building your history.',
            },
          },
          description: 'No outputs to display for this workflow.',
          id: 'empty-card',
        },
      ],
    },
    lfStyle: '.lf-card.material-layout__text-section { height: 100%; }',
    shape: 'card',
    value: '',
  };

  return lfCard;
};
const _extractImageFromDataset = (dataset: LfDataDataset | undefined): string | null => {
  if (!dataset?.nodes) {
    return null;
  }

  for (const node of dataset.nodes) {
    const cells = node.cells ?? {};
    for (const key in cells) {
      const cell = cells[key] as LfDataCell<'card'>;
      if (!cell || typeof cell !== 'object') {
        continue;
      }
      const shape = (cell as { shape?: string }).shape;
      const value = (cell as { value?: unknown }).value ?? (cell as { lfValue?: unknown }).lfValue;
      if (shape === 'image' && typeof value === 'string' && value) {
        return value;
      }
    }
  }

  return null;
};
const _getFirstOutputImageUrl = (outputs: WorkflowNodeResults | null) => {
  if (!outputs) {
    return '';
  }

  const tryPayload = (
    payload: WorkflowNodeResultPayload | undefined,
  ): { image: string | null; fallback: string | null } => {
    if (!payload || typeof payload !== 'object') {
      return { image: null, fallback: null };
    }
    const {
      code: codeIcon,
      forms: stringIcon,
      json: jsonIcon,
      photoX: fallback,
    } = theme.get.icons();

    let foundImage: string | null = null;
    let fallbackCandidate: string | null = null;

    if (Array.isArray(payload.lf_output)) {
      for (const entry of payload.lf_output) {
        const { dataset, file_names, json, metadata, string, svg } = entry;
        const image =
          _extractImageFromDataset(dataset) ??
          file_names?.find((name) => typeof name === 'string' && name) ??
          null;
        if (image) {
          foundImage = image;
          break;
        }
        if (!fallbackCandidate) {
          if (typeof svg === 'string' && svg) {
            fallbackCandidate = codeIcon;
          } else if (typeof string === 'string' && string) {
            fallbackCandidate = stringIcon;
          } else if (json || metadata) {
            fallbackCandidate = jsonIcon;
          }
        }
      }
    }

    if (foundImage) {
      return { image: foundImage, fallback: null };
    }

    const dataset = (payload as { dataset?: LfDataDataset }).dataset;
    const fromDataset = _extractImageFromDataset(dataset);
    if (fromDataset) {
      return { image: fromDataset, fallback: null };
    }

    const fileNames = (payload as { file_names?: string[] }).file_names;
    if (Array.isArray(fileNames)) {
      const fileName = fileNames.find((name) => typeof name === 'string' && name);
      if (fileName) {
        return { image: fileName, fallback: null };
      }
    }

    const image = (payload as { image?: string }).image;
    if (typeof image === 'string' && image) {
      return { image, fallback: null };
    }

    return { image: null, fallback: fallbackCandidate ?? fallback };
  };

  let fallbackImage: string | null = null;

  for (const nodeId in outputs) {
    if (!Object.prototype.hasOwnProperty.call(outputs, nodeId)) {
      continue;
    }
    const payload = outputs[nodeId];
    const { image, fallback: candidate } = tryPayload(payload);
    if (image) {
      return image;
    }
    if (!fallbackImage && candidate) {
      fallbackImage = candidate;
    }
  }

  return fallbackImage ?? '';
};
const _getLfIcon = (status: WorkflowRunStatus): string => {
  const { alertTriangle, check, wand, hourglassLow, x } = theme.get.icons();

  switch (status) {
    case 'cancelled':
      return x;
    case 'failed':
      return alertTriangle;
    case 'pending':
      return hourglassLow;
    case 'running':
      return wand;
    case 'succeeded':
      return check;
  }
};
const _getUiState = (status: WorkflowRunStatus): LfThemeUIState => {
  switch (status) {
    case 'cancelled':
      return 'disabled';
    case 'failed':
      return 'danger';
    case 'pending':
      return 'primary';
    case 'running':
      return 'info';
    case 'succeeded':
      return 'success';
  }
};
const _itemCardCell = (run: WorkflowRunEntry) => {
  const { createdAt, error, httpStatus, runId, status, updatedAt, workflowName } = run;
  const errorSummary = summarizeDetail(error);
  const detailLines: string[] = [
    `Created at: ${formatTimestamp(createdAt)}`,
    `Last updated: ${formatTimestamp(updatedAt)}`,
  ];
  if (errorSummary) {
    detailLines.push('', `Error: ${errorSummary}`);
  }
  if (httpStatus !== null && httpStatus !== undefined) {
    detailLines.push(`HTTP Status: ${httpStatus}`);
  }

  const cells: LfDataCellContainer = {
    '1': {
      value: workflowName || 'Workflow run',
    },
    '2': {
      value: `Run ID: ${runId}`,
    },
    '3': {
      value: detailLines.join('\n').trim(),
    },
    lfButton: {
      shape: 'button',
      value: '',
      lfIcon: _getLfIcon(status),
      lfLabel: formatStatus(status),
      lfStyling: 'flat',
      lfUiState: _getUiState(status),
    },
    lfImage: {
      shape: 'image',
      value: _getFirstOutputImageUrl(run.outputs),
    },
  };

  const lfCard: LfDataCell<'card'> = {
    lfDataset: {
      nodes: [
        {
          cells,
          description: `Output results for run ${runId}`,
          id: `${runId}`,
        },
      ],
    },
    lfStyle: '.lf-card.material-layout__text-section { height: 100%; }',
    lfUiState: _getUiState(status),
    shape: 'card',
    value: '',
  };

  return lfCard;
};
const _masonry = (store: WorkflowStore) => {
  const masonry = document.createElement('lf-masonry');
  masonry.className = OUTPUTS_CLASSES.masonry;
  masonry.lfShape = 'card';
  masonry.lfStyle = UI_CONSTANTS.MASONRY_STYLE;
  masonry.addEventListener('lf-masonry-event', (e) => masonryHandler(e, store));

  return masonry;
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
    const masonry = _masonry(store);

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
    const masonry = elements[OUTPUTS_CLASSES.masonry] as HTMLLfMasonryElement;
    const toggle = elements[OUTPUTS_CLASSES.toggle] as HTMLLfButtonElement;

    if (!h4 || !masonry || !toggle) {
      return;
    }

    const activeWorkflowId = state.current.id;
    const allRuns = manager.runs.all();
    const hasAnyRuns = allRuns.length > 0;
    const isHistoryView = state.view === 'history';
    const workflowTitle = manager.workflow.title();
    h4.textContent = workflowTitle ? `${workflowTitle} outputs` : 'Workflow outputs';

    const runs = isHistoryView
      ? allRuns
      : allRuns.filter((run) => (run.workflowId ?? null) === (activeWorkflowId ?? null));

    toggle.lfIcon = isHistoryView ? arrowBack : folder;
    toggle.lfLabel = isHistoryView ? 'Back' : 'History';
    toggle.lfUiState = hasAnyRuns || isHistoryView ? 'primary' : 'disabled';

    const dataset: LfDataDataset = { nodes: [] };

    if (!runs.length) {
      dataset.nodes.push({ cells: { lfCard: _emptyCardCell() }, id: '' });
      masonry.lfCollapseColumns = true;
      masonry.lfSelectable = false;
    } else {
      for (const run of runs) {
        dataset.nodes.push({ cells: { lfCard: _itemCardCell(run) }, id: run.runId });
        masonry.lfCollapseColumns = false;
        masonry.lfSelectable = true;
      }
    }

    masonry.lfDataset = dataset;

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
