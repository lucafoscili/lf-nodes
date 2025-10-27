import { WorkflowState } from '../types/state';

//#region Constants
const INIT_ERROR = 'Mutate not initialized';
const INIT_CB = () => {
  throw new Error(INIT_ERROR);
};
//#endregion

//#region Public API
export const initState = (): WorkflowState => ({
  current: { status: 'idle', message: '', id: null },
  currentRunId: null,
  isDebug: false,
  manager: null,
  pollingTimer: null,
  queuedJobs: -1,
  runs: [],
  mutate: {
    isDebug: INIT_CB,
    manager: INIT_CB,
    queuedJobs: INIT_CB,
    notifications: {
      add: INIT_CB,
      removeById: INIT_CB,
      removeByIndex: INIT_CB,
    },
    pollingTimer: INIT_CB,
    results: INIT_CB,
    runs: {
      clear: INIT_CB,
      upsert: INIT_CB,
    },
    runId: INIT_CB,
    selectRun: INIT_CB,
    status: INIT_CB,
    view: INIT_CB,
    workflow: INIT_CB,
    workflows: INIT_CB,
  },
  notifications: [],
  results: null,
  selectedRunId: null,
  view: 'workflow',
  workflows: {
    nodes: [],
  },
});
//#endregion
