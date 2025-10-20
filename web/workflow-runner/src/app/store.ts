import { DEFAULT_STATUS_MESSAGES } from '../config';
import {
  WorkflowRunnerStore,
  WorkflowState,
  WorkflowStateListener,
  WorkflowStateUpdater,
  WorkflowStatus,
} from '../types/state';

//#region Factory
export const createWorkflowRunnerStore = (initialState: WorkflowState): WorkflowRunnerStore => {
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
    workflow: (workflowId: string) => setWorkflow(workflowId, setState),
    status: (status: WorkflowStatus, message: string) => setStatus(status, message, setState),
    runResult: (status: WorkflowStatus, message: string, results: any) =>
      setRunResult(status, message, results, setState),
    manager: (manager: WorkflowState['manager']) =>
      applyMutation((draft) => {
        draft.manager = manager;
      }),
    workflows: (workflows: WorkflowState['workflows']) =>
      applyMutation((draft) => {
        draft.workflows = workflows;
      }),
    ui: (updater: (ui: WorkflowState['ui']) => void) =>
      applyMutation((draft) => {
        updater(draft.ui);
      }),
    dev: {
      panel: {
        set: (open: boolean) =>
          applyMutation((draft) => {
            draft.dev.panel.open = open;
          }),
        toggle: () =>
          applyMutation((draft) => {
            draft.dev.panel.open = !draft.dev.panel.open;
          }),
      },
    },
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
const setRunResult = (
  status: WorkflowStatus,
  message: string,
  results: any,
  setState: (updater: WorkflowStateUpdater) => void,
) => {
  setState((state) => ({
    ...state,
    current: {
      ...state.current,
      status,
      message,
    },
    results,
  }));
};
const setStatus = (
  status: WorkflowStatus,
  message: string,
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
//#endregion
