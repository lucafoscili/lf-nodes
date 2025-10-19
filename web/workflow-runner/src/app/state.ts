import { WorkflowState } from '../types/state';

//#region Public API
export const initState = (appContainer: HTMLDivElement): WorkflowState => ({
  current: { status: 'ready', message: 'Ready.', workflow: null, preferredOutput: null },
  manager: null,
  ui: {
    layout: {
      _root: appContainer,
      drawer: {
        _root: null,
        tree: null,
      },
      header: {
        _root: null,
        drawerToggle: null,
        themeSwitch: null,
      },
      main: {
        _root: null,
        title: { _root: null },
        workflow: {
          _root: null,
          cells: [],
          options: null,
          result: null,
          run: null,
          status: null,
          title: null,
        },
      },
    },
  },
  workflows: {},
  results: null,
  mutate: {
    workflow: () => {
      throw new Error('Mutate not initialized');
    },
    status: () => {
      throw new Error('Mutate not initialized');
    },
    runResult: () => {
      throw new Error('Mutate not initialized');
    },
  },
});
//#endregion
