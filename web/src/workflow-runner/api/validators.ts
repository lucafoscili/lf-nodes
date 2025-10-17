// Lightweight runtime type guards for Workflow-runner API shapes.
import type {
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
} from '../../types/workflow-runner/api';

export const isObject = (v: unknown): v is Record<string, unknown> =>
  v !== null && typeof v === 'object';

export const isString = (v: unknown): v is string => typeof v === 'string';

export const isStringArray = (v: unknown): v is string[] =>
  Array.isArray(v) && v.every((e) => typeof e === 'string');

export const isWorkflowAPIUploadPayload = (v: unknown): v is WorkflowAPIUploadPayload => {
  if (!isObject(v)) return false;
  if (!('detail' in v) || !isString((v as any).detail)) return false;

  if ('paths' in v && !(isStringArray((v as any).paths) || (v as any).paths === undefined))
    return false;

  if ('error' in v) {
    const err = (v as any).error;
    if (!isObject(err) || !('message' in err) || !isString(err.message)) return false;
  }

  return true;
};

export const isWorkflowAPIUploadResponse = (v: unknown): v is WorkflowAPIUploadResponse => {
  if (!isObject(v)) return false;
  if (!('message' in v) || !isString((v as any).message)) return false;
  if (!('status' in v) || !isString((v as any).status)) return false;
  if (!('payload' in v) || !isWorkflowAPIUploadPayload((v as any).payload)) return false;
  return true;
};

export default {
  isWorkflowAPIUploadPayload,
  isWorkflowAPIUploadResponse,
};
