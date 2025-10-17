import {
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
} from '../../types/workflow-runner/api';
import { WorkflowState } from '../../types/workflow-runner/state';
import { invokeUploadAPI } from '../api/upload';
import { workflowSection } from '../elements/main.workflow';

//#region API
export const isObject = (v: unknown): v is Record<string, unknown> =>
  v !== null && typeof v === 'object';
export const isString = (v: unknown): v is string => typeof v === 'string';
export const isStringArray = (v: unknown): v is string[] =>
  Array.isArray(v) && v.every((e) => typeof e === 'string');
export const isWorkflowAPIUploadPayload = (v: unknown): v is WorkflowAPIUploadPayload => {
  if (!isObject(v)) {
    return false;
  }
  if (!('detail' in v) || !isString(v.detail)) {
    return false;
  }
  if ('paths' in v && !(isStringArray(v.paths) || v.paths === undefined)) {
    return false;
  }
  if ('error' in v) {
    const err = v.error;
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
//#endregion

//#region Upload
export const handleUploadField = async (
  state: WorkflowState,
  fieldName: string,
  files: File[],
): Promise<string[]> => {
  const { manager } = state;

  manager.setStatus('running', 'Uploading file…');

  const response = await invokeUploadAPI(files);

  if (!response || response.status !== 'ready') {
    workflowSection.update.fieldWrapper(state, fieldName, 'error');
    manager.setStatus('error', `Upload failed: ${response?.payload?.detail ?? 'unknown error'}`);
    throw new Error(response?.payload?.detail || 'Upload failed');
  }

  const paths = response.payload?.paths || [];

  manager.setStatus('running', 'File uploaded, processing...');

  return paths;
};
//#endregion
