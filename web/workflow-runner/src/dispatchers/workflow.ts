import { WORKFLOW_CLASSES } from '../elements/main.workflow';
import {
  runWorkflowRequest,
  uploadWorkflowFiles,
  WorkflowApiError,
} from '../services/workflow-service';
import { WorkflowManager } from '../types/manager';
import { WorkflowCellStatus, WorkflowUICells } from '../types/section';
import { WorkflowState, WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region Helpers
const _collectInputs = async (state: WorkflowState): Promise<Record<string, unknown>> => {
  const { manager } = state;
  const { uiRegistry } = manager;

  const elements = uiRegistry.get();
  const cells = (elements?.[WORKFLOW_CLASSES.cells] as WorkflowUICells) || [];

  const inputs: Record<string, unknown> = {};

  for (const cell of cells) {
    const id = cell.id || '';
    _setCellStatus(state, id);
    const value: unknown = await cell.getValue();

    switch (cell.tagName.toLowerCase()) {
      case 'lf-toggle':
        inputs[id] = value === 'off' ? false : true;
        break;
      case 'lf-upload':
        try {
          inputs[id] = await _handleUploadField(manager, value);
        } catch (error) {
          _setCellStatus(state, id, 'error');
          manager.setStatus('error', `Upload failed: ${error.payload?.detail || error.message}`);
          throw error;
        }
        break;
      default:
        inputs[id] = value;
    }
  }

  return inputs;
};
const _handleUploadField = async (manager: WorkflowManager, rawValue: unknown) => {
  const { UPLOADING_FILE, FILE_PROCESSING } = STATUS_MESSAGES;

  const files = Array.isArray(rawValue) ? rawValue : (rawValue as File[] | undefined);
  if (!files || files.length === 0) {
    return [];
  }

  try {
    manager.setStatus('running', UPLOADING_FILE);
    const { payload } = await uploadWorkflowFiles(files);
    const paths = payload?.paths || [];
    manager.setStatus('running', FILE_PROCESSING);
    return paths.length === 1 ? paths[0] : paths;
  } catch (error) {
    if (error instanceof WorkflowApiError) {
      manager.setStatus('error', `Upload failed: ${error.payload?.detail || error.message}`);
    } else {
      manager.setStatus('error', 'Upload failed unexpectedly.');
    }
    throw error;
  }
};
const _setCellStatus = (state: WorkflowState, id: string, status: WorkflowCellStatus = '') => {
  const { WORKFLOW_INPUT_FLAGGED } = DEBUG_MESSAGES;
  const { current, manager } = state;
  const { uiRegistry } = manager;

  const elements = uiRegistry.get();
  const cells = (elements?.[WORKFLOW_CLASSES.cells] as WorkflowUICells) || [];

  const field = cells.find((el) => el.id === id);
  const wrapper = field?.parentElement;
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
    manager.setStatus('error', WORKFLOW_NOT_SELECTED);
    return;
  }

  manager.setStatus('running', SUBMITTING_WORKFLOW);

  let inputs: Record<string, unknown>;
  try {
    inputs = await _collectInputs(state);
    debugLog(INPUTS_COLLECTED, 'informational', {
      id,
      inputKeys: Object.keys(inputs),
    });
  } catch (error) {
    const detail =
      error instanceof WorkflowApiError
        ? error.payload?.detail || error.message
        : (error as Error)?.message || 'Failed to collect inputs.';
    manager.setStatus('error', `Failed to collect inputs: ${detail}`);
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
        _setCellStatus(state, inputName, 'error');
      }
      manager.setStatus('error', error.payload?.detail || error.message);
    } else {
      manager.setStatus('error', 'Unexpected error while running the workflow.');
    }
  }
};
//#endregion
