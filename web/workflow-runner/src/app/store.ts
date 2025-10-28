import { DEFAULT_STATUS_MESSAGES } from '../config';
import { WorkflowAPIDataset, WorkflowNodeResults, WorkflowRunStatus } from '../types/api';
import { WorkflowManager } from '../types/manager';
import { WorkflowCellStatus } from '../types/section';
import {
  WorkflowRunEntryUpdate,
  WorkflowState,
  WorkflowStateListener,
  WorkflowStateNotification,
  WorkflowStateUpdater,
  WorkflowStatus,
  WorkflowStore,
  WorkflowView,
} from '../types/state';

//#region Factory
export const createWorkflowRunnerStore = (initialState: WorkflowState): WorkflowStore => {
  let state = initialState;
  const listeners = new Set<WorkflowStateListener>();
  const pendingMutations: Array<() => void> = [];
  let isApplyingMutation = false;

  const getState = () => state;

  const setState = (updater: WorkflowStateUpdater) => {
    const nextState = updater(state);
    if (nextState === state) {
      return;
    }

    state = nextState;
    for (const listener of listeners) {
      listener(state);
    }
  };

  const subscribe = (listener: WorkflowStateListener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  };

  const enqueueMutation = (mutation: () => void) => {
    pendingMutations.push(mutation);
    if (isApplyingMutation) {
      return;
    }

    isApplyingMutation = true;
    try {
      while (pendingMutations.length > 0) {
        const nextMutation = pendingMutations.shift();
        if (nextMutation) {
          nextMutation();
        }
      }
    } finally {
      isApplyingMutation = false;
    }
  };

  const applyMutation = (mutator: (draft: WorkflowState) => void) => {
    enqueueMutation(() =>
      setState((current) => {
        mutator(current);
        return { ...current };
      }),
    );
  };

  const mutate = {
    isDebug: (isDebug: boolean) =>
      applyMutation((draft) => {
        draft.isDebug = isDebug;
      }),
    manager: (manager: WorkflowManager) =>
      applyMutation((draft) => {
        draft.manager = manager;
      }),
    inputStatus: (cellId: string, status: WorkflowCellStatus) =>
      applyMutation((draft) => {
        if (status) {
          draft.inputStatuses = {
            ...draft.inputStatuses,
            [cellId]: status,
          };
        } else if (cellId in draft.inputStatuses) {
          const { [cellId]: _removed, ...rest } = draft.inputStatuses;
          draft.inputStatuses = rest;
        }
      }),
    notifications: {
      add: (notification: WorkflowStateNotification) =>
        applyMutation((draft) => {
          draft.notifications.push(notification);
        }),
      removeById: (id: string) =>
        applyMutation((draft) => {
          draft.notifications = draft.notifications.filter((n) => n.id !== id);
        }),
      removeByIndex: (index: number) =>
        applyMutation((draft) => {
          draft.notifications.splice(index, 1);
        }),
    },
    pollingTimer: (timerId: number | null) =>
      applyMutation((draft) => {
        draft.pollingTimer = timerId;
      }),
    queuedJobs: (count: number) =>
      applyMutation((draft) => {
        draft.queuedJobs = count;
      }),
    results: (results: WorkflowNodeResults | null) =>
      applyMutation((draft) => {
        draft.results = results;
      }),
    runId: (runId: string | null) =>
      applyMutation((draft) => {
        draft.currentRunId = runId;
      }),
    runs: {
      clear: () =>
        applyMutation((draft) => {
          draft.runs = [];
        }),
      upsert: (entry: WorkflowRunEntryUpdate) =>
        applyMutation((draft) => {
          const now = entry.updatedAt ?? Date.now();
          const existingIndex = draft.runs.findIndex((run) => run.runId === entry.runId);

          if (existingIndex >= 0) {
            const current = draft.runs[existingIndex];
            const createdAt = entry.createdAt ?? current.createdAt;
            draft.runs[existingIndex] = {
              ...current,
              ...entry,
              createdAt,
              updatedAt: now,
              status: entry.status ?? current.status,
              workflowId: entry.workflowId ?? current.workflowId,
              workflowName: entry.workflowName ?? current.workflowName,
              inputs: entry.inputs ?? current.inputs,
              outputs: entry.outputs ?? current.outputs,
              error: entry.error ?? current.error ?? null,
              httpStatus: entry.httpStatus !== undefined ? entry.httpStatus : current.httpStatus,
              resultPayload:
                entry.resultPayload !== undefined ? entry.resultPayload : current.resultPayload,
            };
          } else {
            const createdAt = entry.createdAt ?? now;
            draft.runs = [
              {
                runId: entry.runId,
                createdAt,
                updatedAt: now,
                status: (entry.status ?? 'pending') as WorkflowRunStatus,
                workflowId: entry.workflowId ?? null,
                workflowName: entry.workflowName ?? 'Unnamed workflow',
                inputs: entry.inputs ?? {},
                outputs: entry.outputs ?? null,
                error: entry.error ?? null,
                httpStatus: entry.httpStatus ?? null,
                resultPayload:
                  entry.resultPayload === undefined ? null : entry.resultPayload ?? null,
              },
              ...draft.runs.filter((run) => run.runId !== entry.runId),
            ];
          }
        }),
    },
    selectRun: (runId: string | null) =>
      applyMutation((draft) => {
        draft.selectedRunId = runId;
      }),
    view: (view: WorkflowView) =>
      applyMutation((draft) => {
        draft.view = view;
      }),
    status: (status: WorkflowStatus, message?: string) => setStatus(status, message, setState),
    workflow: (workflowId: string) => setWorkflow(workflowId, setState),
    workflows: (workflows: WorkflowAPIDataset) =>
      applyMutation((draft) => {
        draft.workflows = workflows;
      }),
  };

  state.mutate = mutate;

  return {
    getState,
    setState,
    subscribe,
  };
};
//#endregion

//#region Mutators
const setStatus = (
  status: WorkflowStatus,
  message: string | undefined,
  setState: (updater: WorkflowStateUpdater) => void,
) => {
  setState(
    (state) =>
      ({
        ...state,
        current: {
          ...state.current,
          status,
          message: message ?? DEFAULT_STATUS_MESSAGES[status],
        },
      } satisfies WorkflowState),
  );
};
const setWorkflow = (id: string, setState: (updater: WorkflowStateUpdater) => void) => {
  setState(
    (state) =>
      ({
        ...state,
        inputStatuses: {},
        current: {
          ...state.current,
          id,
        },
        currentRunId: null,
        results: null,
        selectedRunId: null,
        view: 'workflow',
      } satisfies WorkflowState),
  );
};
//#endregion
