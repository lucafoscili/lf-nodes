import { WorkflowState } from '../types/state';

//#region Public API
export const initState = (appContainer: HTMLDivElement): WorkflowState => ({
  current: { status: 'ready', message: 'Ready.', workflow: null, preferredOutput: null },
  manager: null,
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
    manager: () => {
      throw new Error('Mutate not initialized');
    },
    workflows: () => {
      throw new Error('Mutate not initialized');
    },
    ui: () => {
      throw new Error('Mutate not initialized');
    },
    dev: {
      panel: {
        set: () => {
          throw new Error('Mutate not initialized');
        },
        toggle: () => {
          throw new Error('Mutate not initialized');
        },
      },
    },
  },
  dev: {
    panel: {
      open: false,
    },
  },
});
//#endregion
