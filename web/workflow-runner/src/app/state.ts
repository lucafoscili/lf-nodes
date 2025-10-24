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
  isDebug: false,
  manager: null,
  mutate: {
    isDebug: INIT_CB,
    manager: INIT_CB,
    runResult: INIT_CB,
    status: INIT_CB,
    workflow: INIT_CB,
    workflows: INIT_CB,
  },
  results: null,
  workflows: {
    nodes: [],
  },
});
//#endregion
