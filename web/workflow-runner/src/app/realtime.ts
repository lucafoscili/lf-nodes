import { subscribeQueueEvents, subscribeRunEvents } from '../services/workflow-service';
import {
  WorkflowCreateRealtimeControllerOptions,
  WorkflowRealtimeController,
} from '../types/manager';
import { debugLog } from '../utils/debug';

//#region Realtime Controller (SSE-based)
export const createRealtimeController = ({
  runLifecycle,
  store,
}: WorkflowCreateRealtimeControllerOptions): WorkflowRealtimeController => {
  let runSseSource: EventSource | null = null;
  let queueSseSource: EventSource | null = null;

  //#region Stop
  const stopRealtimeUpdates = () => {
    if (runSseSource) {
      runSseSource.close();
      runSseSource = null;
    }
    if (queueSseSource) {
      queueSseSource.close();
      queueSseSource = null;
    }
  };
  //#endregion

  //#region Start Realtime
  const startRealtimeUpdates = () => {
    try {
      const runEs = subscribeRunEvents((ev) => {
        try {
          runLifecycle.handleStatusResponse(ev);
        } catch (err) {
          debugLog('Error handling run SSE event:', 'warning');
        }
      });
      if (runEs) {
        runSseSource = runEs;
        runEs.onerror = () => {
          try {
            runEs.close();
          } catch {}
          runSseSource = null;
        };
      }
    } catch (err) {
      debugLog('Failed to start run SSE subscription:', 'error');
    }

    try {
      const queueEs = subscribeQueueEvents((ev) => {
        try {
          const busy = (ev.pending || 0) + (ev.running || 0);
          const state = store.getState();
          if (state.queuedJobs !== busy) {
            state.mutate.queuedJobs(busy);
          }
        } catch (err) {
          debugLog('Error handling queue SSE event:', 'warning');
        }
      });
      if (queueEs) {
        queueSseSource = queueEs;
        queueEs.onerror = () => {
          try {
            queueEs.close();
          } catch {}
        };
      }
    } catch (err) {
      debugLog('Failed to start queue SSE subscription:', 'error');
    }
  };
  //#endregion

  return {
    startRealtimeUpdates,
    stopRealtimeUpdates,
  };
};
//#endregion
