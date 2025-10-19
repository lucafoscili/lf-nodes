import {
  WorkflowRunnerStore,
  WorkflowState,
  WorkflowStateListener,
  WorkflowStateUpdater,
  WorkflowStatus,
} from '../types/state';
import { DEFAULT_STATUS_MESSAGES } from '../config';

//#region Factory
export const createWorkflowRunnerStore = (initialState: WorkflowState): WorkflowRunnerStore => {
  let state = initialState;
  const listeners = new Set<WorkflowStateListener>();

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

  const mutate = {
    workflow: (workflowId: string) => setWorkflow(workflowId, setState),
    status: (status: WorkflowStatus, message?: string) => setStatus(status, message, setState),
    runResult: (
      status: WorkflowStatus,
      message: string,
      preferredOutput: string | null,
      results: any,
    ) => setRunResult(status, message, preferredOutput, results, setState),
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
const setWorkflow = (workflowId: string, setState: (updater: WorkflowStateUpdater) => void) => {
  setState((state) => ({
    ...state,
    current: {
      ...state.current,
      workflow: workflowId,
      preferredOutput: null,
    },
    results: null,
  }));
};

const setStatus = (
  status: WorkflowStatus,
  message: string | undefined,
  setState: (updater: WorkflowStateUpdater) => void,
) => {
  setState((state) => ({
    ...state,
    current: {
      ...state.current,
      status,
      message: message ?? DEFAULT_STATUS_MESSAGES[status],
    },
  }));
};

const setRunResult = (
  status: WorkflowStatus,
  message: string,
  preferredOutput: string | null,
  results: any,
  setState: (updater: WorkflowStateUpdater) => void,
) => {
  setState((state) => ({
    ...state,
    current: {
      ...state.current,
      status,
      message,
      preferredOutput,
    },
    results,
  }));
};
//#endregion
