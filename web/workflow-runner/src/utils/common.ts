import {
  WorkflowAPIResponse,
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
} from '../types/api';
import { UnescapeJSONPayload } from '../types/section';

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

//#region JSON
export const areJSONEqual = (a: unknown, b: unknown) => {
  return JSON.stringify(a) === JSON.stringify(b);
};
export const isJSONLikeString = (value: unknown): value is string => {
  if (typeof value !== 'string') return false;
  const trimmed = value.trim();
  if (
    !(
      (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
      (trimmed.startsWith('[') && trimmed.endsWith(']'))
    )
  ) {
    return false;
  }

  if (trimmed.startsWith('{')) {
    if (trimmed === '{}') return true;
    if (/".*"\s*:\s*.+/.test(trimmed)) return true;
    return false;
  }

  if (trimmed.indexOf('"') !== -1) return true;

  const simpleArrayScalar =
    /^\[\s*(?:-?\d+(\.\d+)?|true|false|null)(\s*,\s*(?:-?\d+(\.\d+)?|true|false|null))*\s*\]$/i;
  if (trimmed.startsWith('[') && simpleArrayScalar.test(trimmed)) return true;

  return false;
};
export const isValidJSON = (value: unknown) => {
  try {
    JSON.stringify(value);
    return true;
  } catch (error) {
    return false;
  }
};
export const parseJson = async (response: Response) => {
  try {
    return (await response.json()) as WorkflowAPIResponse | Record<string, unknown>;
  } catch {
    return null;
  }
};
export const unescapeJson = (input: any): UnescapeJSONPayload => {
  let validJson = false;
  let parsedJson: Record<string, unknown> | undefined = undefined;
  let unescapedStr = input;

  const recursiveUnescape = (inputStr: string): string => {
    let newStr = inputStr.replace(/\\(.)/g, '$1');
    while (newStr !== inputStr) {
      inputStr = newStr;
      newStr = inputStr.replace(/\\(.)/g, '$1');
    }
    return newStr;
  };

  const deepParse = (data: unknown) => {
    if (isJSONLikeString(data)) {
      try {
        const innerJson = JSON.parse(data);
        if (typeof innerJson === 'object' && innerJson !== null) {
          return deepParse(innerJson);
        }
      } catch (e) {
        return data;
      }
    } else if (typeof data === 'object' && data !== null) {
      Object.keys(data).forEach((key) => {
        data[key] = deepParse(data[key]);
      });
    }
    return data;
  };

  try {
    parsedJson = isJSONLikeString(input) ? JSON.parse(input) : input;
    validJson = true;
    parsedJson = deepParse(parsedJson) as Record<string, unknown>;
    unescapedStr = JSON.stringify(parsedJson, null, 2);
  } catch (error) {
    if (typeof input === 'object' && input !== null) {
      try {
        unescapedStr = JSON.stringify(input, null, 2);
        validJson = true;
        parsedJson = input;
      } catch (stringifyError) {
        unescapedStr = recursiveUnescape(input.toString());
      }
    } else {
      unescapedStr = recursiveUnescape(input.toString());
    }
  }

  return { validJson, parsedJson, unescapedStr };
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
