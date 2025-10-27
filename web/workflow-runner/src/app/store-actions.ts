import { WorkflowNodeResults } from '../types/api';
import {
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

//#region Run Selection
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

export const setView = (store: WorkflowStore, view: WorkflowView) => {
  const state = store.getState();
  if (state.view !== view) {
    state.mutate.view(view);
  }
};

export interface ChangeViewOptions {
  runId?: string | null;
  clearResults?: boolean;
}

export const changeView = (
  store: WorkflowStore,
  view: WorkflowView,
  options: ChangeViewOptions = {},
) => {
  const runId = options.runId ?? null;
  const clearResults = options.clearResults;

  if (view === 'run') {
    if (runId) {
      selectRun(store, runId, { clearResults: clearResults ?? false });
      setView(store, 'run');
      return;
    }
    selectRun(store, null, { clearResults });
    setView(store, 'workflow');
    return;
  }

  selectRun(store, null, { clearResults });
  setView(store, view);
};
//#endregion

//#region Run Management
export const setRunInFlight = (store: WorkflowStore, runId: string | null) => {
  store.getState().mutate.runId(runId);
};

export const setStatus = (store: WorkflowStore, status: WorkflowStatus, message?: string) => {
  store.getState().mutate.status(status, message);
};

export const upsertRun = (store: WorkflowStore, entry: WorkflowRunEntryUpdate) => {
  store.getState().mutate.runs.upsert(entry);
};
//#endregion
