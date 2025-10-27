import { WORKFLOW_CLASSES } from '../elements/main.inputs';
import { runWorkflow, uploadWorkflowFiles, WorkflowApiError } from '../services/workflow-service';
import { WorkflowCellStatus, WorkflowUICells } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES, NOTIFICATION_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
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
  const { ERROR_UPLOADING_FILE, RUNNING_UPLOADING_FILE } = STATUS_MESSAGES;

  const files = Array.isArray(rawValue) ? rawValue : (rawValue as File[] | undefined);
  if (!files || files.length === 0) {
    return [];
  }

  const state = store.getState();

  try {
    state.mutate.status('running', RUNNING_UPLOADING_FILE);
    const { payload } = await uploadWorkflowFiles(files);
    const paths = payload?.paths || [];
    return paths.length === 1 ? paths[0] : paths;
  } catch (error) {
    state.mutate.status('error', ERROR_UPLOADING_FILE);

    if (error instanceof WorkflowApiError) {
      state.mutate.notifications.add({
        id: performance.now().toString(),
        message: `Upload failed: ${error.payload?.detail || error.message}`,
        status: 'danger',
      });
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
  const { INPUTS_COLLECTED } = DEBUG_MESSAGES;
  const { NO_WORKFLOW_SELECTED } = NOTIFICATION_MESSAGES;
  const { ERROR_RUNNING_WORKFLOW, RUNNING_DISPATCHING_WORKFLOW, RUNNING_SUBMITTING_WORKFLOW } =
    STATUS_MESSAGES;

  const state = store.getState();
  const { current } = state;
  const id = current.id;

  if (!id) {
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message: NO_WORKFLOW_SELECTED,
      status: 'warning',
    });
    return;
  }

  state.mutate.status('running', RUNNING_SUBMITTING_WORKFLOW);

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

    state.mutate.status('error', ERROR_RUNNING_WORKFLOW);
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message: `Failed to collect inputs: ${detail}`,
      status: 'danger',
    });
    return;
  }

  try {
    state.mutate.status('running', RUNNING_DISPATCHING_WORKFLOW);

    state.mutate.results(null);
    const runId = await runWorkflow({ workflowId: id, inputs });
    state.mutate.runId(runId);
  } catch (error) {
    state.mutate.status('error', ERROR_RUNNING_WORKFLOW);
    if (error instanceof WorkflowApiError) {
      const inputName = error.payload?.error?.input;
      if (inputName) {
        _setCellStatus(store, inputName, 'error');
      }
      state.mutate.notifications.add({
        id: performance.now().toString(),
        message: `Workflow run failed: ${error.payload?.detail || error.message}`,
        status: 'danger',
      });
    }
  }
};
//#endregion
