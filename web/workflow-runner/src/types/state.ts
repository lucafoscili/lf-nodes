import { LfDataDataset } from '@lf-widgets/foundations/dist';
import { WorkflowAPIUI } from './api';
import { WorkflowRunnerManager } from './manager';

//#region State
export type WorkflowStateUpdater = (state: WorkflowState) => WorkflowState;
export type WorkflowStateListener = (state: WorkflowState) => void;
export interface WorkflowRunnerStore {
  getState: () => WorkflowState;
  setState: (updater: WorkflowStateUpdater) => void;
  subscribe: (listener: WorkflowStateListener) => () => void;
}
export type WorkflowStatus = 'ready' | 'running' | 'error';
export interface WorkflowCurrent {
  status: WorkflowStatus;
  message: string | null;
  workflow: string;
  preferredOutput?: string | null;
}
export interface WorkflowUI {
  layout: {
    _root: HTMLDivElement | null;
    drawer: { _root: HTMLLfDrawerElement | null; tree: HTMLLfTreeElement | null };
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
        cells: Array<
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
  manager: WorkflowRunnerManager | null;
  mutate: {
    workflow: (id: string) => void;
    status: (status: WorkflowStatus, message?: string) => void;
    runResult: (
      status: WorkflowStatus,
      message: string,
      preferredOutput: string | null,
      results: any,
    ) => void;
  };
  results: WorkflowAPIUI | null;
  ui: WorkflowUI;
  workflows: LfDataDataset;
}
//#endregion
