import { WORKFLOW_CLASSES } from '../elements/main.workflow';
import {
  runWorkflowRequest,
  uploadWorkflowFiles,
  WorkflowApiError,
} from '../services/workflow-service';
import { WorkflowCellStatus, WorkflowUICells } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region Helpers
const _collectInputs = async (store: WorkflowStore): Promise<Record<string, unknown>> => {
  const state = store.getState();
  const { uiRegistry } = state.manager;

  const elements = uiRegistry.get();
  const cells = (elements?.[WORKFLOW_CLASSES.cells] as WorkflowUICells) || [];

  const inputs: Record<string, unknown> = {};

  for (const cell of cells) {
    const id = cell.id || '';
    _setCellStatus(store, id);
    const value: unknown = await cell.getValue();

    switch (cell.tagName.toLowerCase()) {
      case 'lf-toggle':
        inputs[id] = value === 'off' ? false : true;
        break;
      case 'lf-upload':
        try {
          inputs[id] = await _handleUploadCell(store, value);
        } catch (error) {
          _setCellStatus(store, id, 'error');
          state.mutate.status('error', `Upload failed: ${error.payload?.detail || error.message}`);
          throw error;
        }
        break;
      default:
        inputs[id] = value;
    }
  }

  return inputs;
};
const _handleUploadCell = async (store: WorkflowStore, rawValue: unknown) => {
  const { UPLOADING_FILE, FILE_PROCESSING } = STATUS_MESSAGES;

  const files = Array.isArray(rawValue) ? rawValue : (rawValue as File[] | undefined);
  if (!files || files.length === 0) {
    return [];
  }

  const state = store.getState();

  try {
    state.mutate.status('running', UPLOADING_FILE);
    const { payload } = await uploadWorkflowFiles(files);
    const paths = payload?.paths || [];
    state.mutate.status('running', FILE_PROCESSING);
    return paths.length === 1 ? paths[0] : paths;
  } catch (error) {
    if (error instanceof WorkflowApiError) {
      state.mutate.status('error', `Upload failed: ${error.payload?.detail || error.message}`);
    } else {
      state.mutate.status('error', 'Upload failed unexpectedly.');
    }
    throw error;
  }
};
const _setCellStatus = (store: WorkflowStore, id: string, status: WorkflowCellStatus = '') => {
  const { WORKFLOW_INPUT_FLAGGED } = DEBUG_MESSAGES;
  const { current, manager } = store.getState();
  const { uiRegistry } = manager;

  const elements = uiRegistry.get();
  const cells = (elements?.[WORKFLOW_CLASSES.cells] as WorkflowUICells) || [];

  const cell = cells.find((el) => el.id === id);
  const wrapper = cell?.parentElement;
  if (wrapper) {
    wrapper.dataset.status = status;
  }
  if (status) {
    debugLog(WORKFLOW_INPUT_FLAGGED, 'informational', {
      cell: id,
      id: current.id,
      status,
    });
  }
};
//#endregion

//#region Dispatcher
export const workflowDispatcher = async (store: WorkflowStore) => {
  const { INPUTS_COLLECTED, WORKFLOW_COMPLETED, WORKFLOW_DISPATCHING, WORKFLOW_NOT_SELECTED } =
    DEBUG_MESSAGES;
  const { SUBMITTING_WORKFLOW } = STATUS_MESSAGES;

  const state = store.getState();
  const { current, manager } = state;
  const id = current.id;

  if (!id) {
    state.mutate.status('error', WORKFLOW_NOT_SELECTED);
    return;
  }

  state.mutate.status('running', SUBMITTING_WORKFLOW);

  let inputs: Record<string, unknown>;
  try {
    inputs = await _collectInputs(store);
    debugLog(INPUTS_COLLECTED, 'informational', {
      id,
      inputKeys: Object.keys(inputs),
    });
  } catch (error) {
    const detail =
      error instanceof WorkflowApiError
        ? error.payload?.detail || error.message
        : (error as Error)?.message || 'Failed to collect inputs.';

    state.mutate.status('error', `Failed to collect inputs: ${detail}`);
    return;
  }

  try {
    debugLog(WORKFLOW_DISPATCHING, 'informational', {
      id,
      inputKeys: Object.keys(inputs),
    });
    const { status, message, payload } = await runWorkflowRequest(id, inputs);

    const runState = store.getState();
    runState.mutate.runResult(
      status,
      message,
      payload.history?.outputs ? { ...payload.history.outputs } : null,
    );

    const resultCategory = status === 'error' ? 'error' : 'success';
    debugLog(WORKFLOW_COMPLETED, resultCategory, {
      id,
      wfStatus: status,
      outputs: Object.keys(payload.history?.outputs ?? {}),
    });
  } catch (error) {
    if (error instanceof WorkflowApiError) {
      const inputName = error.payload?.error?.input;
      if (inputName) {
        _setCellStatus(store, inputName, 'error');
      }
      state.mutate.status('error', error.payload?.detail || error.message);
    } else {
      state.mutate.status('error', 'Unexpected error while running the workflow.');
    }
  }
};
//#endregion
