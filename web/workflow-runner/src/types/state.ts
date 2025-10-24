import { WorkflowAPIDataset, WorkflowNodeResults } from './api';
import { WorkflowManager } from './manager';

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
  queuedJobs: number;
  mutate: WorkflowStateMutators;
  results: WorkflowNodeResults | null;
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
  manager: (manager: WorkflowManager) => void;
  queuedJobs: (count: number) => void;
  runResult: (status: WorkflowStatus, message: string, results: WorkflowNodeResults | null) => void;
  status: (status: WorkflowStatus, message?: string) => void;
  workflow: (id: string) => void;
  workflows: (workflows: WorkflowAPIDataset) => void;
}
export type WorkflowStateUpdater = (state: WorkflowState) => WorkflowState;
export type WorkflowStatus = 'running' | 'idle' | 'error';
//#endregion
