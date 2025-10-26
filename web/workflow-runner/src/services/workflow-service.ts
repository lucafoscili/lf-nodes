import { buildApiUrl } from '../config';
import {
  WorkflowAPIDataset,
  WorkflowAPIErrorOptions,
  WorkflowAPIResponse,
  WorkflowAPIRunPayload,
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
} from '../types/api';
import {
  isWorkflowAPIUploadPayload,
  isWorkflowAPIUploadResponse,
  parseJson,
} from '../utils/common';
import { ERROR_MESSAGES } from '../utils/constants';

//#region Errors
export class WorkflowApiError<TPayload = unknown> extends Error {
  readonly payload?: TPayload;
  readonly status?: number;

  constructor(message: string, options: WorkflowAPIErrorOptions<TPayload> = {}) {
    super(message);
    this.name = 'WorkflowApiError';
    this.payload = options.payload;
    this.status = options.status;
  }
}
//#endregion

//#region Fetchers
export const fetchWorkflowDefinitions = async () => {
  const response = await fetch(buildApiUrl('/workflows'), { method: 'GET' });
  const data = (await parseJson(response)) as { workflows?: WorkflowAPIDataset } | null;

  if (!response.ok) {
    const message = `Failed to load workflows (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }

  if (!data?.workflows || !Array.isArray(data.workflows.nodes)) {
    throw new WorkflowApiError('Invalid workflows response shape.', { payload: data });
  }

  return data.workflows;
};

export const fetchWorkflowJSON = async (workflowId: string) => {
  const response = await fetch(buildApiUrl(`/workflows/${workflowId}`), { method: 'GET' });
  const data = (await parseJson(response)) as Record<string, unknown> | null;

  if (!response.ok) {
    const message = `Failed to load workflow JSON (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }

  return data;
};
//#endregion

//#region Run Workflow
export const runWorkflowRequest = async (
  workflowId: string,
  inputs: Record<string, unknown>,
): Promise<WorkflowAPIRunPayload> => {
  const { RUN_GENERIC } = ERROR_MESSAGES;

  const response = await fetch(buildApiUrl('/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workflowId, inputs }),
  });

  const data = (await parseJson(response)) as WorkflowAPIResponse | null;
  const payload: WorkflowAPIRunPayload = (data && data.payload) || {
    detail: response.statusText,
    history: {},
  };

  if (!response.ok || !data) {
    const detail = payload?.detail || response.statusText;
    throw new WorkflowApiError(`${RUN_GENERIC} (${detail})`, {
      payload,
    });
  }

  return payload;
};
//#endregion

//#region Upload image
export const uploadWorkflowFiles = async (files: File[]): Promise<WorkflowAPIUploadResponse> => {
  const { UPLOAD_GENERIC, UPLOAD_INVALID_RESPONSE, UPLOAD_MISSING_FILE } = ERROR_MESSAGES;

  if (!files || files.length === 0) {
    throw new WorkflowApiError<WorkflowAPIUploadPayload>(UPLOAD_MISSING_FILE, {
      payload: { error: { message: 'missing_file' } },
    });
  }

  const formData = new FormData();
  files.forEach((file) => formData.append('file', file));

  const response = await fetch(buildApiUrl('/upload'), {
    method: 'POST',
    body: formData,
  });

  const data = (await parseJson(response)) as unknown;
  if (isWorkflowAPIUploadResponse(data)) {
    if (!response.ok) {
      const { payload } = data;
      const detail = payload?.error?.message || response.statusText;
      throw new WorkflowApiError<WorkflowAPIUploadPayload>(`${UPLOAD_GENERIC} (${detail})`, {
        payload,
      });
    }

    return data;
  }

  if (isWorkflowAPIUploadPayload(data)) {
    if (!response.ok) {
      const detail = data.error?.message || response.statusText;
      throw new WorkflowApiError<WorkflowAPIUploadPayload>(`${UPLOAD_GENERIC} (${detail})`, {
        payload: data,
      });
    }

    return {
      payload: data,
    };
  }

  throw new WorkflowApiError<WorkflowAPIUploadPayload>(UPLOAD_INVALID_RESPONSE, {
    status: response.status,
  });
};
//#endregion
