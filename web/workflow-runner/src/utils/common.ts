import {
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
  WorkflowCellOutputItem,
  WorkflowCellsOutputContainer,
  WorkflowNodeResults,
} from '../types/api';

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
  // New API: either a 'paths' string array (success) or an 'error' object (failure) is acceptable
  const hasPaths = 'paths' in (v as any) && isStringArray((v as any).paths);
  const hasError =
    'error' in (v as any) &&
    isObject((v as any).error) &&
    'message' in (v as any).error &&
    isString((v as any).error.message);

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
