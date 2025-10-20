import { LfDataDataset } from '@lf-widgets/foundations/dist';
import { WorkflowAPIUI } from './api';
import { WorkflowManager } from './manager';
import { WorkflowCells, WorkflowStatus } from './section';

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
  results: WorkflowAPIUI | null;
  ui: WorkflowStateUI;
  workflows: LfDataDataset;
}
export interface WorkflowStateCurrent {
  id: string;
  message: string | null;
  status: WorkflowStatus;
}
export type WorkflowStateListener = (state: WorkflowState) => void;
export interface WorkflowStateMutators {
  isDebug: (isDebug: boolean) => void;
  manager: (manager: WorkflowManager | null) => void;
  runResult: (status: WorkflowStatus, message: string, results: any) => void;
  status: (status: WorkflowStatus, message?: string) => void;
  ui: (updater: (ui: WorkflowStateUI) => void) => void;
  workflow: (id: string) => void;
  workflows: (workflows: LfDataDataset) => void;
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
        cells: WorkflowCells;
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
//#endregion
