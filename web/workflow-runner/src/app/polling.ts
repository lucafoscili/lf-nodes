import { POLLING_INTERVALS } from '../config';
import { getRunStatus as fetchRunStatus, subscribeRunEvents } from '../services/workflow-service';
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
  const perRunPolling = new Map<string, boolean>();
  let sseEnabled = false;
  let sseSource: EventSource | null = null;
  const MAX_CONCURRENT_RUN_REQUESTS = 3;
  let concurrentRunRequests = 0;

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

    if (activeRunId !== runId) {
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

  const pollSingleRun = async (runId: string) => {
    if (perRunPolling.get(runId)) {
      return;
    }

    if (concurrentRunRequests >= MAX_CONCURRENT_RUN_REQUESTS) {
      return;
    }

    perRunPolling.set(runId, true);
    concurrentRunRequests += 1;
    try {
      const response = await getRunStatus(runId);
      const { shouldStopPolling } = runLifecycle.handleStatusResponse(response);
      if (shouldStopPolling) {
        // nothing extra to do here; lifecycle already handled removal of
        // current run if needed.
      }
    } catch (error) {
      runLifecycle.handlePollingError(error);
    } finally {
      perRunPolling.delete(runId);
      concurrentRunRequests = Math.max(0, concurrentRunRequests - 1);
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
    try {
      if (!sseEnabled) {
        const es = subscribeRunEvents((ev) => {
          try {
            const { shouldStopPolling } = runLifecycle.handleStatusResponse(ev as any);
            // lifecycle will handle run in-flight changes; we don't explicitly
            // stop per-run polling here because SSE is authoritative.
          } catch (err) {}
        });
        if (es) {
          sseEnabled = true;
          sseSource = es;
          es.onerror = () => {
            try {
              es.close();
            } catch {}
            sseEnabled = false;
            sseSource = null;
          };
        }
      }
    } catch (err) {
      // ignore
    }
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
      if (!sseEnabled) {
        const activeRuns = state.runs.filter((r) => ['pending', 'running'].includes(r.status));
        for (const run of activeRuns) {
          if (run.runId) {
            void pollSingleRun(run.runId);
          }
        }
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
