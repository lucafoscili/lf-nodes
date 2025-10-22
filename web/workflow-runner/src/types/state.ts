import { WorkflowAPIDataset, WorkflowNodeResults } from './api';
import { WorkflowManager } from './manager';
import { WorkflowUICells } from './section';

//#region Store
export interface WorkflowStore {
  getState: () => WorkflowState;
  setState: (updater: WorkflowStateUpdater) => void;
  subscribe: (listener: WorkflowStateListener) => () => void;
}
//#endregion

//#region State
export interface WorkflowState {
  current: WorkflowStateCurrent;
  isDebug: boolean;
  manager: WorkflowManager | null;
  mutate: WorkflowStateMutators;
  results: WorkflowNodeResults | null;
  ui: WorkflowStateUI;
  workflows: WorkflowAPIDataset;
}
export interface WorkflowStateCurrent {
  id: string | null;
  message: string | null;
  status: WorkflowStatus;
}
export type WorkflowStateListener = (state: WorkflowState) => void;
export interface WorkflowStateMutators {
  isDebug: (isDebug: boolean) => void;
  manager: (manager: WorkflowManager | null) => void;
  runResult: (status: WorkflowStatus, message: string, results: WorkflowNodeResults | null) => void;
  status: (status: WorkflowStatus, message?: string) => void;
  ui: (updater: (ui: WorkflowStateUI) => void) => void;
  workflow: (id: string) => void;
  workflows: (workflows: WorkflowAPIDataset) => void;
}
export interface WorkflowStateUI {
  layout: {
    _root: HTMLDivElement | null;
    actionButton: { _root: HTMLLfButtonElement | null };
    drawer: { _root: HTMLLfDrawerElement | null; tree: HTMLLfTreeElement | null };
    header: {
      _root: HTMLLfHeaderElement | null;
      drawerToggle: HTMLLfButtonElement | null;
      debugToggle: HTMLLfButtonElement | null;
      themeSwitch: HTMLLfButtonElement | null;
    };
    main: {
      _root: HTMLElement | null;
      title: {
        _root: HTMLElement | null;
      };
      workflow: {
        _root: HTMLElement | null;
        cells: WorkflowUICells | null;
        description: HTMLElement | null;
        options: HTMLDivElement | null;
        result: HTMLElement | null;
        run: HTMLLfButtonElement | null;
        status: HTMLElement | null;
        title: HTMLElement | null;
      };
    };
    dev: {
      _root: HTMLDivElement | null;
      card: HTMLLfCardElement | null;
    };
  };
}
export type WorkflowStateUpdater = (state: WorkflowState) => WorkflowState;
export type WorkflowStatus = 'ready' | 'running' | 'error';
//#endregion
