import {
  WorkflowNodeResults,
  WorkflowOutputArtifact,
  WorkflowRunResultPayload,
  WorkflowRunStatus,
} from './api';

//#region Run record
export type RunRecord = {
  run_id: string;
  submission_id?: string | null;
  cancel_requested?: boolean;
  workflow_id?: string | null;
  status: WorkflowRunStatus;
  seq: number;
  owner_id?: string | null;
  created_at?: number | null;
  updated_at?: number | null;
  inputs?: Record<string, unknown> | null;
  outputs?: WorkflowNodeResults | null;
  artifacts?: WorkflowOutputArtifact[];
  result?: WorkflowRunResultPayload | null;
  error?: string | null;
};
//#endregion

//#region Events
export type EventPayload = RunRecord & { type?: string };

export type QueuePayload = {
  type?: 'queue_status';
  pending?: number;
  running?: number;
  run_id?: string;
  submission_id?: string | null;
  cancel_requested?: boolean;
  workflow_id?: string;
  status?: WorkflowRunStatus;
  seq?: number;
  owner_id?: string;
  created_at?: number;
  updated_at?: number;
  inputs?: Record<string, unknown> | null;
  outputs?: WorkflowNodeResults;
  result?: WorkflowRunResultPayload;
  error?: string;
};

export type UpdateHandler = (runs: Map<string, RunRecord>) => void;
//#endregion

//#region Workflow API
export type WorkflowNameItem = {
  workflow_id?: string;
  id?: string;
  workflowId?: string;
  key?: string;
  name?: string;
  title?: string;
  workflow_name?: string;
  value?: string;
};

export type WorkflowApiResponse =
  | WorkflowNameItem[]
  | {
      workflows?: WorkflowNameItem[] | { nodes?: WorkflowNameItem[] } | Record<string, string>;
      items?: WorkflowNameItem[];
    };
//#endregion
