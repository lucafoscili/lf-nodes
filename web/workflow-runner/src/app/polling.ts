import { POLLING_INTERVALS } from '../config';
import { getRunStatus as fetchRunStatus } from '../services/workflow-service';
import { ComfyRawQueueStatus } from '../types/api';
import {
  WorkflowCreatePollingControllerOptions,
  WorkflowPollingController,
} from '../types/manager';
import { parseCount } from '../utils/common';

//#region Helpers
const _defaultQueueFetcher = async (): Promise<ComfyRawQueueStatus> => {
  const resp = await fetch('/queue');
  if (!resp.ok) {
    throw new Error('Failed to fetch queue status');
  }

  return (await resp.json()) as ComfyRawQueueStatus;
};
//#endregion

//#region Polling Controller
export const createPollingController = ({
  fetchQueueStatus = _defaultQueueFetcher,
  getRunStatus = fetchRunStatus,
  queueIntervalMs = POLLING_INTERVALS.queue,
  runIntervalMs = POLLING_INTERVALS.run,
  runLifecycle,
  store,
}: WorkflowCreatePollingControllerOptions): WorkflowPollingController => {
  let queueTimerId: number | null = null;
  let runTimerId: number | null = null;
  let isRunPolling = false;
  let activeRunId: string | null = null;

  //#region Stop
  const stopRunPolling = () => {
    if (typeof runTimerId === 'number') {
      window.clearInterval(runTimerId);
      runTimerId = null;
    }
    const state = store.getState();
    if (state.pollingTimer !== null) {
      state.mutate.pollingTimer(null);
    }
    activeRunId = null;
    isRunPolling = false;
  };
  const stopQueuePolling = () => {
    if (queueTimerId !== null) {
      window.clearInterval(queueTimerId);
      queueTimerId = null;
    }
  };
  //#endregion

  //#region Polling
  const beginRunPolling = (runId: string) => {
    stopRunPolling();
    activeRunId = runId;

    const poll = () => {
      if (activeRunId) {
        void pollRun(activeRunId);
      }
    };

    poll();
    runTimerId = window.setInterval(poll, runIntervalMs);
    store.getState().mutate.pollingTimer(Number(runTimerId));
  };
  const pollRun = async (runId: string) => {
    if (isRunPolling) {
      return;
    }

    const currentState = store.getState();
    if (currentState.currentRunId !== runId) {
      return;
    }

    isRunPolling = true;
    try {
      const response = await getRunStatus(runId);
      const { shouldStopPolling } = runLifecycle.handleStatusResponse(response);
      if (shouldStopPolling) {
        stopRunPolling();
      }
    } catch (error) {
      const { shouldStopPolling } = runLifecycle.handlePollingError(error);
      if (shouldStopPolling) {
        stopRunPolling();
      }
    } finally {
      isRunPolling = false;
    }
  };
  const startQueuePolling = () => {
    if (queueTimerId !== null) {
      return;
    }

    const poll = () => {
      void pollQueue();
    };

    poll();
    queueTimerId = window.setInterval(poll, queueIntervalMs);
  };
  //#endregion

  //#region Queue Polling
  const pollQueue = async () => {
    try {
      const { queue_pending, queue_running } = await fetchQueueStatus();
      const state = store.getState();

      const qPending = parseCount(queue_pending);
      const qRunning = parseCount(queue_running);
      const busy = qPending + qRunning;

      const prev = state.queuedJobs ?? -1;
      if (busy !== prev) {
        state.mutate.queuedJobs(busy);
      }
    } catch (error) {
      const state = store.getState();
      const prev = state.queuedJobs ?? -1;
      if (prev !== -1) {
        state.mutate.queuedJobs(-1);
      }
    }
  };
  //#endregion

  return {
    beginRunPolling,
    startQueuePolling,
    stopQueuePolling,
    stopRunPolling,
  };
};
//#endregion
