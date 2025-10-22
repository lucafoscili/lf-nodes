import { WorkflowState } from '../types/state';

const INIT_ERROR = 'Mutate not initialized';
const INIT_CB = () => {
  throw new Error(INIT_ERROR);
};

//#region Public API
export const initState = (appContainer: HTMLDivElement): WorkflowState => ({
  current: { status: 'ready', message: 'Ready.', id: null },
  isDebug: false,
  manager: null,
  mutate: {
    isDebug: INIT_CB,
    manager: INIT_CB,
    runResult: INIT_CB,
    status: INIT_CB,
    workflow: INIT_CB,
    workflows: INIT_CB,
    ui: INIT_CB,
  },
  results: null,
  ui: {
    layout: {
      _root: appContainer,
      actionButton: { _root: null },
      drawer: {
        _root: null,
        tree: null,
      },
      header: {
        _root: null,
        drawerToggle: null,
        debugToggle: null,
        themeSwitch: null,
      },
      main: {
        _root: null,
        title: { _root: null },
        workflow: {
          _root: null,
          cells: [],
          description: null,
          options: null,
          result: null,
          run: null,
          status: null,
          title: null,
        },
      },
      dev: {
        _root: null,
        card: null,
      },
    },
  },
  workflows: {
    nodes: [],
  },
});
//#endregion
