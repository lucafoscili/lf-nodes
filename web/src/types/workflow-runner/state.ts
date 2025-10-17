import { WorkflowAPIDefinition } from './api';
import { WorkflowRunnerManager } from './manager';

//#region State
export type WorkflowStatus = 'ready' | 'running' | 'error';
export interface WorkflowCurrent {
  status: WorkflowStatus;
  workflow: WorkflowAPIDefinition['id'] | null;
}
export interface WorkflowUI {
  layout: {
    _root: HTMLDivElement | null;
    drawer: { _root: HTMLLfDrawerElement | null };
    header: {
      _root: HTMLLfHeaderElement | null;
      drawerToggle: HTMLLfButtonElement | null;
      themeSwitch: HTMLLfButtonElement | null;
    };
    main: {
      _root: HTMLElement | null;
      title: {
        _root: HTMLElement | null;
      };
      workflow: {
        _root: HTMLElement | null;
        fields: Array<
          HTMLLfButtonElement | HTMLLfTextfieldElement | HTMLLfToggleElement | HTMLLfUploadElement
        >;
        options: HTMLDivElement | null;
        result: HTMLElement | null;
        run: HTMLLfButtonElement | null;
        status: HTMLElement | null;
        title: HTMLElement | null;
      };
    };
  };
}
export interface WorkflowState {
  current: WorkflowCurrent;
  manager: WorkflowRunnerManager;
  ui: WorkflowUI;
  workflows: WorkflowAPIDefinition[];
}
//#endregion
