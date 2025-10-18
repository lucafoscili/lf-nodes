import { WorkflowState } from '../types/state';

type StateUpdater = (state: WorkflowState) => WorkflowState;
type StateListener = (state: WorkflowState) => void;

export interface WorkflowRunnerStore {
  getState: () => WorkflowState;
  setState: (updater: StateUpdater) => void;
  subscribe: (listener: StateListener) => () => void;
}

export const createWorkflowRunnerStore = (initialState: WorkflowState): WorkflowRunnerStore => {
  let state = initialState;
  const listeners = new Set<StateListener>();

  const getState = () => state;

  const setState = (updater: StateUpdater) => {
    const nextState = updater(state);
    if (nextState === state) {
      return;
    }

    state = nextState;
    for (const listener of listeners) {
      listener(state);
    }
  };

  const subscribe = (listener: StateListener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  };

  return {
    getState,
    setState,
    subscribe,
  };
};
