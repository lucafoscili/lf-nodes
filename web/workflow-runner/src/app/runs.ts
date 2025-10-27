import { WorkflowNodeResults, WorkflowRunStatus, WorkflowRunStatusResponse } from '../types/api';
import { CreateRunLifecycleOptions, RunLifecycleController } from '../types/manager';
import { NOTIFICATION_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import {
  addNotification,
  setResults,
  setRunInFlight,
  setStatus,
  upsertRun,
} from './store-actions';

//#region Helpers
const _coerceTimestamp = (value: number | null | undefined, fallback: number) => {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value > 1e12 ? Math.round(value) : Math.round(value * 1000);
  }

  return fallback;
};
const _extractRunOutputs = (response: WorkflowRunStatusResponse): WorkflowNodeResults | null => {
  const outputs = response.result?.body?.payload?.history?.outputs;
  if (!outputs) {
    return null;
  }

  return { ...outputs };
};
//#endregion

//#region Run Lifecycle
export const createRunLifecycle = ({
  setInputStatus,
  store,
}: CreateRunLifecycleOptions): RunLifecycleController => {
  const { WORKFLOW_COMPLETED, WORKFLOW_STATUS_FAILED, WORKFLOW_CANCELLED } = NOTIFICATION_MESSAGES;

  //#region Progress update
  const updateProgress = (response: WorkflowRunStatusResponse) => {
    const now = Date.now();
    upsertRun(store, {
      runId: response.run_id,
      createdAt: _coerceTimestamp(response.created_at, now),
      updatedAt: now,
      status: response.status,
      error: response.error ?? null,
      httpStatus: response.result?.http_status ?? null,
      resultPayload: response.result ?? null,
    });
  };
  //#endregion

  //#region Success
  const handleRunSuccess = (response: WorkflowRunStatusResponse) => {
    const state = store.getState();
    const runId = response.run_id;
    const outputs = _extractRunOutputs(response);
    const now = Date.now();

    upsertRun(store, {
      runId,
      createdAt: _coerceTimestamp(response.created_at, now),
      updatedAt: now,
      status: 'succeeded' as WorkflowRunStatus,
      error: null,
      outputs,
      httpStatus: response.result?.http_status ?? null,
      resultPayload: response.result ?? null,
    });

    if (state.selectedRunId === runId) {
      setResults(store, outputs);
    }

    addNotification(store, {
      id: performance.now().toString(),
      message: WORKFLOW_COMPLETED,
      status: 'success',
    });

    setStatus(store, 'idle', STATUS_MESSAGES.IDLE);
  };
  //#endregion

  //#region Cancellation
  const handleRunFailure = (response: WorkflowRunStatusResponse) => {
    const state = store.getState();
    const payload = response.result?.body?.payload;
    const runId = response.run_id;
    const detail =
      payload?.detail ||
      payload?.error?.message ||
      response.error ||
      STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW;
    const outputs = _extractRunOutputs(response);
    const now = Date.now();

    upsertRun(store, {
      runId,
      createdAt: _coerceTimestamp(response.created_at, now),
      updatedAt: now,
      status: 'failed' as WorkflowRunStatus,
      error: detail,
      outputs,
      httpStatus: response.result?.http_status ?? null,
      resultPayload: response.result ?? null,
    });

    if (state.selectedRunId === runId) {
      setResults(store, outputs);
    }

    if (payload?.error?.input) {
      setInputStatus?.(payload.error.input, 'error');
    }

    addNotification(store, {
      id: performance.now().toString(),
      message: `Workflow run failed: ${detail}`,
      status: 'danger',
    });

    setStatus(store, 'error', STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW);
  };
  //#endregion

  //#region Cancellation
  const handleRunCancellation = (response: WorkflowRunStatusResponse) => {
    const state = store.getState();
    const runId = response.run_id;
    const outputs = _extractRunOutputs(response);
    const message = response.error || WORKFLOW_CANCELLED;
    const now = Date.now();

    upsertRun(store, {
      runId,
      createdAt: _coerceTimestamp(response.created_at, now),
      updatedAt: now,
      status: 'cancelled' as WorkflowRunStatus,
      error: message,
      outputs,
      httpStatus: response.result?.http_status ?? null,
      resultPayload: response.result ?? null,
    });

    if (state.selectedRunId === runId) {
      setResults(store, outputs);
    }

    addNotification(store, {
      id: performance.now().toString(),
      message,
      status: 'warning',
    });

    setStatus(store, 'idle', STATUS_MESSAGES.IDLE);
  };
  //#endregion

  //#region Status
  const handleStatusResponse = (response: WorkflowRunStatusResponse) => {
    const state = store.getState();

    updateProgress(response);
    const { status } = response;

    switch (status) {
      case 'cancelled':
        handleRunCancellation(response);
        break;
      case 'failed':
        handleRunFailure(response);
        break;
      case 'pending':
      case 'running':
        if (
          state.current.status !== 'running' ||
          state.current.message !== STATUS_MESSAGES.RUNNING_POLLING_WORKFLOW
        ) {
          setStatus(store, 'running', STATUS_MESSAGES.RUNNING_POLLING_WORKFLOW);
        }
        break;
      case 'succeeded':
        handleRunSuccess(response);
        break;
      default:
        break;
    }

    if (status === 'succeeded' || status === 'failed' || status === 'cancelled') {
      setRunInFlight(store, null);
      return { shouldStopPolling: true };
    }

    return { shouldStopPolling: false };
  };
  //#endregion

  //#region Error
  const handlePollingError = (error: unknown) => {
    const state = store.getState();
    const detail = error instanceof Error ? error.message : STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW;

    setStatus(store, 'error', STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW);

    addNotification(store, {
      id: performance.now().toString(),
      message: `${WORKFLOW_STATUS_FAILED}: ${detail}`,
      status: 'danger',
    });

    const runId = state.currentRunId;
    if (runId) {
      const now = Date.now();
      upsertRun(store, {
        runId,
        updatedAt: now,
        status: 'failed' as WorkflowRunStatus,
        error: detail,
      });
      if (state.selectedRunId === runId) {
        setResults(store, null);
      }
    }

    setRunInFlight(store, null);

    return { shouldStopPolling: true };
  };
  //#endregion

  return {
    handlePollingError,
    handleStatusResponse,
    updateProgress,
  };
};
//#endregion
