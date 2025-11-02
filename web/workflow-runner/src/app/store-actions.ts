import { WorkflowNodeResults } from '../types/api';
import {
  WorkflowRunEntry,
  WorkflowRunEntryUpdate,
  WorkflowStateNotification,
  WorkflowStatus,
  WorkflowStore,
  WorkflowView,
} from '../types/state';

//#region Notifications
export const addNotification = (store: WorkflowStore, notification: WorkflowStateNotification) => {
  store.getState().mutate.notifications.add(notification);
};
//#endregion

//#region Results
export const clearResults = (store: WorkflowStore) => {
  store.getState().mutate.results(null);
};
export const setResults = (store: WorkflowStore, results: WorkflowNodeResults | null) => {
  store.getState().mutate.results(results);
};
//#endregion

//#region Status
export const setStatus = (store: WorkflowStore, status: WorkflowStatus, message?: string) => {
  store.getState().mutate.status(status, message);
};
//#endregion

//#region View
export const setView = (store: WorkflowStore, view: WorkflowView) => {
  const state = store.getState();
  if (state.view !== view) {
    state.mutate.view(view);
  }
};
//#endregion

//#region Run
export const setRunInFlight = (store: WorkflowStore, runId: string | null) => {
  const state = store.getState();
  if (state.currentRunId === runId) {
    return;
  }
  state.mutate.runId(runId);
};
export const selectRun = (
  store: WorkflowStore,
  runId: string | null,
  options?: { clearResults?: boolean },
) => {
  const state = store.getState();
  state.mutate.selectRun(runId);

  const shouldClearResults = options?.clearResults ?? !runId;
  if (shouldClearResults) {
    state.mutate.results(null);
  }
};
export const upsertRun = (store: WorkflowStore, entry: WorkflowRunEntryUpdate) => {
  store.getState().mutate.runs.upsert(entry);
};

const ACTIVE_STATUSES = new Set<WorkflowRunEntry['status']>(['pending', 'running']);

export const ensureActiveRun = (store: WorkflowStore, preferredRunId?: string) => {
  const state = store.getState();
  const activeRuns = state.runs.filter((run) => ACTIVE_STATUSES.has(run.status));
  const currentRunId = state.currentRunId;

  if (currentRunId && activeRuns.some((run) => run.runId === currentRunId)) {
    return;
  }

  const preferred =
    preferredRunId !== undefined
      ? activeRuns.find((run) => run.runId === preferredRunId) ?? null
      : null;

  const nextRun =
    preferred ??
    activeRuns
      .slice()
      .sort((a, b) => {
        if (a.createdAt !== b.createdAt) {
          return a.createdAt - b.createdAt;
        }
        return a.updatedAt - b.updatedAt;
      })
      .shift() ??
    null;

  if (!nextRun) {
    if (currentRunId !== null) {
      setRunInFlight(store, null);
      setStatus(store, 'idle');
    }
    return;
  }

  if (nextRun.runId !== currentRunId) {
    setRunInFlight(store, nextRun.runId);
  }
};
//#endregion
