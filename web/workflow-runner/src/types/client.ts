import { WorkflowRunResultPayload } from './api';

//#region Run record
export type RunRecord = {
  run_id: string;
  workflow_id?: string | null;
  status: string;
  seq: number;
  owner_id?: string | null;
  created_at?: number | null;
  updated_at?: number | null;
  result?: WorkflowRunResultPayload | null;
  error?: string | null;
};
//#endregion

//#region Events
export type EventPayload = RunRecord & { type?: string };
export type UpdateHandler = (runs: Map<string, RunRecord>) => void;
//#endregion
