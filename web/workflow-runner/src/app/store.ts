import { DEFAULT_STATUS_MESSAGES } from '../config';
import { WorkflowNodeOutputs } from '../types/api';
import { WorkflowStatus } from '../types/section';
import {
  WorkflowState,
  WorkflowStateListener,
  WorkflowStateUpdater,
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
    manager: (manager: WorkflowState['manager']) =>
      applyMutation((draft) => {
        draft.manager = manager;
      }),
    status: (status: WorkflowStatus, message?: string) => setStatus(status, message, setState),
    runResult: (status: WorkflowStatus, message: string, results: WorkflowNodeOutputs | null) =>
      setRunResult(status, message, results, setState),
    ui: (updater: (ui: WorkflowState['ui']) => void) =>
      applyMutation((draft) => {
        updater(draft.ui);
      }),
    workflow: (workflowId: string) => setWorkflow(workflowId, setState),
    workflows: (workflows: WorkflowState['workflows']) =>
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
  results: WorkflowNodeOutputs | null,
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
