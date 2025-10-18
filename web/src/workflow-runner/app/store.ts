import { WorkflowState } from '../../types/workflow-runner/state';

type StateMutator = (state: WorkflowState) => void;
type StateListener = (state: WorkflowState) => void;

export interface WorkflowRunnerStore {
  getState: () => WorkflowState;
  setState: (mutator: StateMutator) => void;
  subscribe: (listener: StateListener) => () => void;
}

export const createWorkflowRunnerStore = (initialState: WorkflowState): WorkflowRunnerStore => {
  let state = initialState;
  const listeners = new Set<StateListener>();

  const getState = () => state;

  const setState = (mutator: StateMutator) => {
    mutator(state);

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
