import { POLLING_INTERVALS } from '../config';
import { subscribeRunEvents } from '../services/workflow-service';
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
  queueIntervalMs = POLLING_INTERVALS.queue,
  runLifecycle,
  store,
}: WorkflowCreatePollingControllerOptions): WorkflowPollingController => {
  let queueTimerId: number | null = null;
  let sseSource: EventSource | null = null;

  //#region Stop
  const stopQueuePolling = () => {
    if (queueTimerId !== null) {
      window.clearInterval(queueTimerId);
      queueTimerId = null;
    }
    if (sseSource) {
      sseSource.close();
      sseSource = null;
    }
  };
  //#endregion

  //#region Queue Polling
  const startQueuePolling = () => {
    if (queueTimerId !== null) {
      return;
    }

    const poll = () => {
      void pollQueue();
    };

    poll();
    queueTimerId = window.setInterval(poll, queueIntervalMs);

    // Subscribe to SSE for real-time run status updates
    try {
      const es = subscribeRunEvents((ev) => {
        try {
          runLifecycle.handleStatusResponse(ev as any);
        } catch (err) {
          // Ignore errors in SSE event handling
        }
      });
      if (es) {
        sseSource = es;
        es.onerror = () => {
          try {
            es.close();
          } catch {}
          sseSource = null;
        };
      }
    } catch (err) {
      // Ignore SSE setup errors
    }
  };

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
    startQueuePolling,
    stopQueuePolling,
  };
};
//#endregion
