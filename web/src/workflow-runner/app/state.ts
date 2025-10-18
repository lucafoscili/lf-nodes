import { WorkflowState } from '../../types/workflow-runner/state';

//#region Public API
export const initState = (appContainer: HTMLDivElement): WorkflowState => ({
  current: { status: 'ready', message: 'Ready.', workflow: null, preferredOutput: null },
  manager: null,
  ui: {
    layout: {
      _root: appContainer,
      drawer: {
        _root: null,
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
          fields: [],
          options: null,
          result: null,
          run: null,
          status: null,
          title: null,
        },
      },
    },
  },
  workflows: [],
  results: null,
});
//#endregion
