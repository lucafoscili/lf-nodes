import { LfThemeUIState } from '@lf-widgets/foundations/dist';
import {
  WorkflowAPIDataset,
  WorkflowNodeResults,
  WorkflowRunResultPayload,
  WorkflowRunStatus,
} from './api';
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
  currentRunId: string | null;
  isDebug: boolean;
  manager: WorkflowManager | null;
  mutate: WorkflowStateMutators;
  notifications: WorkflowStateNotification[];
  pollingTimer: number | null;
  queuedJobs: number;
  runs: WorkflowRunEntry[];
  results: WorkflowNodeResults | null;
  selectedRunId: string | null;
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
  notifications: {
    add: (notification: WorkflowStateNotification) => void;
    removeById: (id: string) => void;
    removeByIndex: (index: number) => void;
  };
  pollingTimer: (timerId: number | null) => void;
  queuedJobs: (count: number) => void;
  results: (results: WorkflowNodeResults | null) => void;
  runId: (runId: string | null) => void;
  runs: WorkflowStateRunMutators;
  selectRun: (runId: string | null) => void;
  status: (status: WorkflowStatus, message?: string) => void;
  workflow: (id: string) => void;
  workflows: (workflows: WorkflowAPIDataset) => void;
}
export interface WorkflowStateNotification {
  id: string;
  message: string;
  status: LfThemeUIState;
}
export interface WorkflowRunEntry {
  runId: string;
  createdAt: number;
  updatedAt: number;
  status: WorkflowRunStatus;
  workflowId: string | null;
  workflowName: string;
  inputs: Record<string, unknown>;
  outputs: WorkflowNodeResults | null;
  error: string | null;
  httpStatus: number | null;
  resultPayload?: WorkflowRunResultPayload | null;
}
export type WorkflowRunEntryUpdate = Partial<Omit<WorkflowRunEntry, 'runId'>> & {
  runId: string;
};
export interface WorkflowStateRunMutators {
  clear: () => void;
  upsert: (entry: WorkflowRunEntryUpdate) => void;
}
export type WorkflowStateUpdater = (state: WorkflowState) => WorkflowState;
export type WorkflowStatus = 'running' | 'idle' | 'error';
//#endregion
