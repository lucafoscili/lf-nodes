import {
  WorkflowAPIResponse,
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
} from '../types/api';

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
export const parseJson = async (response: Response) => {
  try {
    return (await response.json()) as WorkflowAPIResponse | Record<string, unknown>;
  } catch {
    return null;
  }
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
