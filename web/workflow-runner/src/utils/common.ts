import {
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
  WorkflowCellOutputItem,
  WorkflowCellsOutputContainer,
  WorkflowNodeResults,
  WorkflowRunStatus,
} from '../types/api';
import { RunRecord } from '../types/client';
import type { WorkflowRunEntryUpdate } from '../types/state';

//#region API
export const deepMerge = (defs: WorkflowCellsOutputContainer, outs: WorkflowNodeResults) => {
  const prep: WorkflowCellOutputItem[] = [];

  for (const id in defs) {
    const cell = defs[id];
    const { nodeId } = cell;
    const result = outs?.[nodeId]?.lf_output[0] || outs?.[nodeId]?.[0] || outs?.[nodeId];

    const item: WorkflowCellOutputItem = {
      ...JSON.parse(JSON.stringify(cell)),
      ...JSON.parse(JSON.stringify(result || {})),
    };
    prep.push(item);
  }

  return prep;
};
export const isObject = (v: unknown): v is Record<string, unknown> =>
  v !== null && typeof v === 'object';
export const isString = (v: unknown): v is string => typeof v === 'string';
export const isStringArray = (v: unknown): v is string[] =>
  Array.isArray(v) && v.every((e) => typeof e === 'string');
export const isWorkflowAPIUploadPayload = (v: unknown): v is WorkflowAPIUploadPayload => {
  if (!isObject(v)) {
    return false;
  }
  const hasPaths = 'paths' in v && isStringArray(v.paths);
  const hasError =
    'error' in v && isObject(v.error) && 'message' in v.error && isString(v.error.message);

  if (!hasPaths && !hasError) {
    return false;
  }
  if ('error' in v) {
    const err = (v as any).error;
    if (!isObject(err) || !('message' in err) || !isString(err.message)) {
      return false;
    }
  }

  return true;
};
export const isWorkflowAPIUploadResponse = (v: unknown): v is WorkflowAPIUploadResponse => {
  if (!isObject(v)) {
    return false;
  }
  if (!('message' in v) || !isString(v.message)) {
    return false;
  }
  if (!('status' in v) || !isString(v.status)) {
    return false;
  }
  if (!('payload' in v) || !isWorkflowAPIUploadPayload(v.payload)) {
    return false;
  }

  return true;
};
export const normalize_description = (description: string | string[] | undefined): string => {
  if (!description) {
    return '';
  } else if (Array.isArray(description) && description.length > 1) {
    return description.join('\n');
  } else if (Array.isArray(description) && description.length === 1) {
    return description[0];
  } else if (typeof description === 'string') {
    return description;
  } else {
    return '';
  }
};
export const parseCount = (v: unknown) => {
  if (Array.isArray(v)) {
    return v.length;
  }
  if (v === null || v === undefined) {
    return 0;
  }
  if (typeof v === 'boolean') {
    return v ? 1 : 0;
  }
  const n = Number(v as any);
  return Number.isFinite(n) ? n : 0;
};
//#endregion

//#region Client
export const recordToUI = (rec: RunRecord, workflowNames?: Map<string, string>) => {
  const { created_at, error, result, run_id, status, updated_at, workflow_id } = rec;

  const now = Date.now();
  const map: WorkflowRunEntryUpdate = {
    runId: run_id,
    status: status as WorkflowRunStatus,
    createdAt: created_at ?? now,
    updatedAt: updated_at ?? now,
    workflowId: workflow_id ?? null,
    workflowName: (workflow_id && workflowNames?.get(workflow_id)) || 'Unnamed Workflow',
    error: error ?? null,
    httpStatus: result?.http_status ?? null,
    resultPayload: result ?? null,
    outputs: result?.body?.payload?.history?.outputs || null,
    inputs: {}, // TODO: populate if available in rec
  };

  return map;
};
//#endregion

//#region Helpers
export const formatStatus = (status: string) => status.charAt(0).toUpperCase() + status.slice(1);
export const formatTimestamp = (timestamp: number) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return 'Unknown time';
  }
  return date.toLocaleString();
};
const _tryParseJson = (value: string) => {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
};
export const stringifyDetail = (value: unknown): string | null => {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) {
      return null;
    }
    const parsed = _tryParseJson(trimmed);
    if (parsed !== null) {
      try {
        return JSON.stringify(parsed, null, 2);
      } catch {
        return trimmed;
      }
    }
    return trimmed;
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
};
export const summarizeDetail = (value: unknown): string | null => {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) {
      return null;
    }
    const parsed = _tryParseJson(trimmed);
    if (parsed && typeof parsed === 'object') {
      const message = (parsed as { message?: unknown }).message;
      if (typeof message === 'string' && message.trim()) {
        return message.trim();
      }
      const detail = (parsed as { detail?: unknown }).detail;
      if (typeof detail === 'string' && detail.trim()) {
        return detail.trim();
      }
      return JSON.stringify(parsed);
    }
    return trimmed;
  }
  if (typeof value === 'object') {
    const message = (value as { message?: unknown }).message;
    if (typeof message === 'string' && message.trim()) {
      return message.trim();
    }
    const detail = (value as { detail?: unknown }).detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail.trim();
    }
    try {
      const str = JSON.stringify(value);
      return str.length > 200 ? `${str.slice(0, 197)}...` : str;
    } catch {
      return '[object Object]';
    }
  }
  return String(value);
};
//#endregion

//#region Upload
export const clearChildren = (element: Element | null) => {
  if (!element) {
    return;
  }

  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
};
//#endregion
