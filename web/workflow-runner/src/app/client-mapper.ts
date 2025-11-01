import type { RunRecord } from './client';
import type { WorkflowRunEntryUpdate } from '../types/state';

/**
 * Maps a RunRecord from WorkflowRunnerClient to the UI state format.
 * This is the single source of truth for transforming network-level run data
 * into application state.
 */
export function mapRunRecordToUi(
  rec: RunRecord,
  workflowNames?: Map<string, string>,
): WorkflowRunEntryUpdate {
  const now = Date.now();

  return {
    runId: rec.run_id,
    status: rec.status as any, // WorkflowRunStatus is compatible
    createdAt: rec.created_at ?? now,
    updatedAt: rec.updated_at ?? now,
    workflowId: rec.workflow_id ?? null,
    workflowName: (rec.workflow_id && workflowNames?.get(rec.workflow_id)) || 'Unnamed Workflow',
    error: rec.error ?? null,
    httpStatus: rec.result?.http_status ?? null,
    resultPayload: rec.result ?? null,
    outputs: extractRunOutputs(rec),
    inputs: {}, // TODO: populate if available in rec
  };
}

/**
 * Extract outputs from run result payload.
 */
function extractRunOutputs(rec: RunRecord): any | null {
  const outputs = rec.result?.body?.payload?.history?.outputs;
  if (!outputs) return null;
  return { ...outputs };
}
