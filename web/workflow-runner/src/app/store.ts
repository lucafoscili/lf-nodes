import { DEFAULT_STATUS_MESSAGES } from '../config';
import { WorkflowAPIDataset, WorkflowNodeResults, WorkflowRunStatus } from '../types/api';
import { WorkflowManager } from '../types/manager';
import { WorkflowCellStatus } from '../types/section';
import {
  WorkflowRunEntryUpdate,
  WorkflowRunEntry,
  WorkflowState,
  WorkflowStateListener,
  WorkflowStateNotification,
  WorkflowStateUpdater,
  WorkflowStatus,
  WorkflowStore,
  WorkflowView,
} from '../types/state';

/** Keep history ordering independent of server/map insertion order. */
export const compareWorkflowRuns = (
  a: Pick<WorkflowRunEntry, 'runId' | 'createdAt'>,
  b: Pick<WorkflowRunEntry, 'runId' | 'createdAt'>,
) => {
  if (a.createdAt !== b.createdAt) {
    return b.createdAt - a.createdAt;
  }
  // Avoid locale-dependent ordering in a persisted/history contract.
  return a.runId < b.runId ? -1 : a.runId > b.runId ? 1 : 0;
};

//#region Factory
export const createWorkflowRunnerStore = (initialState: WorkflowState): WorkflowStore => {
  let state = initialState;

  const listeners = new Set<WorkflowStateListener>();
  const pendingMutations: Array<() => void> = [];
  let isApplyingMutation = false;

  const cloneWorkflowsDataset = (dataset: WorkflowAPIDataset): WorkflowAPIDataset => ({
    ...dataset,
    columns: dataset.columns ? dataset.columns.slice() : undefined,
    nodes: Array.isArray(dataset.nodes) ? dataset.nodes.slice() : [],
  });

  const createDraft = (source: WorkflowState): WorkflowState => ({
    ...source,
    current: { ...source.current },
    inputStatuses: { ...source.inputStatuses },
    notifications: source.notifications.slice(),
    runs: source.runs.map((run) => ({ ...run })),
    workflows: cloneWorkflowsDataset(source.workflows),
  });

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
        const draft = createDraft(current);
        mutator(draft);
        return draft;
      }),
    );
  };

  const mutate = {
    cancelInFlightRun: (runId: string | null) =>
      applyMutation((draft) => {
        draft.cancelInFlightRunId = runId;
      }),
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
    inputPrefillRun: (runId: string | null) =>
      applyMutation((draft) => {
        draft.inputPrefillRunId = runId;
      }),
    submissionInFlight: (submissionId: string | null) =>
      applyMutation((draft) => {
        draft.submissionInFlightId = submissionId;
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
    queuedJobs: (count: number) => {
      if (state.queuedJobs === count) {
        return;
      }
      applyMutation((draft) => {
        draft.queuedJobs = count;
      });
    },
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
      removeMany: (runIds: string[]) => {
        if (runIds.length === 0) {
          return;
        }
        const removed = new Set(runIds);
        applyMutation((draft) => {
          draft.runs = draft.runs.filter((run) => !removed.has(run.runId));
          if (draft.currentRunId && removed.has(draft.currentRunId)) {
            draft.currentRunId = null;
          }
          if (draft.cancelInFlightRunId && removed.has(draft.cancelInFlightRunId)) {
            draft.cancelInFlightRunId = null;
          }
          if (draft.selectedRunId && removed.has(draft.selectedRunId)) {
            draft.selectedRunId = null;
          }
          if (draft.inputPrefillRunId && removed.has(draft.inputPrefillRunId)) {
            draft.inputPrefillRunId = null;
          }
        });
      },
      upsert: (entry: WorkflowRunEntryUpdate) =>
        applyMutation((draft) => {
          const now = entry.updatedAt ?? Date.now();
          const existingIndex = draft.runs.findIndex((run) => run.runId === entry.runId);

          if (existingIndex >= 0) {
            const current = draft.runs[existingIndex];
            const createdAt = entry.createdAt ?? current.createdAt;
            const nextRuns = draft.runs.slice();
            nextRuns[existingIndex] = {
              ...current,
              ...entry,
              artifacts: entry.artifacts !== undefined ? entry.artifacts : current.artifacts,
              createdAt,
              updatedAt: now,
              status: entry.status ?? current.status,
              submissionId:
                entry.submissionId !== undefined ? entry.submissionId : current.submissionId,
              cancelRequested:
                entry.cancelRequested !== undefined
                  ? entry.cancelRequested
                  : current.cancelRequested,
              workflowId: entry.workflowId ?? current.workflowId,
              workflowName: entry.workflowName ?? current.workflowName,
              inputs: entry.inputs ?? current.inputs,
              outputs: entry.outputs ?? current.outputs,
              error: entry.error ?? current.error ?? null,
              httpStatus: entry.httpStatus !== undefined ? entry.httpStatus : current.httpStatus,
              resultPayload:
                entry.resultPayload !== undefined ? entry.resultPayload : current.resultPayload,
            };
            draft.runs = nextRuns.sort(compareWorkflowRuns);
          } else {
            const createdAt = entry.createdAt ?? now;
            const nextRuns = draft.runs.filter((run) => run.runId !== entry.runId);
            draft.runs = [
              {
                runId: entry.runId,
                artifacts: entry.artifacts ?? [],
                submissionId: entry.submissionId ?? null,
                cancelRequested: entry.cancelRequested ?? false,
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
              ...nextRuns,
            ].sort(compareWorkflowRuns);
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
        // Workflow navigation must not surrender control of an owned active
        // run; the floating action remains Stop until that run is terminal.
        currentRunId: state.currentRunId,
        results: null,
        selectedRunId: null,
        view: 'workflow',
      } satisfies WorkflowState),
  );
};
//#endregion
