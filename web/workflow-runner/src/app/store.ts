import { DEFAULT_STATUS_MESSAGES } from '../config';
import { WorkflowAPIDataset, WorkflowNodeResults } from '../types/api';
import { WorkflowManager } from '../types/manager';
import {
  WorkflowState,
  WorkflowStateListener,
  WorkflowStateUpdater,
  WorkflowStatus,
  WorkflowStore,
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
    queuedJobs: (count: number) =>
      applyMutation((draft) => {
        draft.queuedJobs = count;
      }),
    status: (status: WorkflowStatus, message?: string) => setStatus(status, message, setState),
    runResult: (status: WorkflowStatus, message: string, results: WorkflowNodeResults | null) =>
      setRunResult(status, message, results, setState),
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
const setRunResult = (
  status: WorkflowStatus,
  message: string,
  results: WorkflowNodeResults | null,
  setState: (updater: WorkflowStateUpdater) => void,
) => {
  setState(
    (state) =>
      ({
        ...state,
        current: {
          ...state.current,
          status,
          message,
        },
        results,
      } satisfies WorkflowState),
  );
};
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
        current: {
          ...state.current,
          id,
        },
        results: null,
      } satisfies WorkflowState),
  );
};
//#endregion
