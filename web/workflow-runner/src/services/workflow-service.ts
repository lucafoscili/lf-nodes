import { buildApiUrl } from '../config';
import {
  WorkflowAPIDataset,
  WorkflowAPIErrorOptions,
  WorkflowAPIResponse,
  WorkflowAPIRunPayload,
  WorkflowAPIRunResult,
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
} from '../types/api';
import { WorkflowStatus } from '../types/state';
import {
  isWorkflowAPIUploadPayload,
  isWorkflowAPIUploadResponse,
  parseJson,
} from '../utils/common';
import { ERROR_MESSAGES, STATUS_MESSAGES } from '../utils/constants';

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
//#endregion

//#region Run Workflow
export const runWorkflowRequest = async (
  workflowId: string,
  inputs: Record<string, unknown>,
): Promise<WorkflowAPIRunResult> => {
  const { RUN_GENERIC } = ERROR_MESSAGES;
  const { WORKFLOW_COMPLETED } = STATUS_MESSAGES;

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
      status: response.status,
      payload,
    });
  }

  return {
    message: WORKFLOW_COMPLETED,
    payload,
    status: data.status as Extract<WorkflowStatus, 'ready' | 'error'>,
  };
};
//#endregion

//#region Upload image
export const uploadWorkflowFiles = async (files: File[]): Promise<WorkflowAPIUploadResponse> => {
  const { UPLOAD_GENERIC, UPLOAD_INVALID_RESPONSE, UPLOAD_MISSING_FILE } = ERROR_MESSAGES;
  const { UPLOAD_COMPLETED } = STATUS_MESSAGES;

  if (!files || files.length === 0) {
    throw new WorkflowApiError<WorkflowAPIUploadPayload>(UPLOAD_MISSING_FILE, {
      payload: { detail: 'missing_file' },
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
      const detail = payload?.detail || response.statusText;
      throw new WorkflowApiError<WorkflowAPIUploadPayload>(`${UPLOAD_GENERIC} (${detail})`, {
        status: response.status,
        payload,
      });
    }

    return data;
  }

  if (isWorkflowAPIUploadPayload(data)) {
    if (!response.ok) {
      const detail = data.detail || response.statusText;
      throw new WorkflowApiError<WorkflowAPIUploadPayload>(`${UPLOAD_GENERIC} (${detail})`, {
        status: response.status,
        payload: data,
      });
    }

    return {
      message: UPLOAD_COMPLETED,
      payload: data,
      status: 'idle',
    };
  }

  throw new WorkflowApiError<WorkflowAPIUploadPayload>(UPLOAD_INVALID_RESPONSE, {
    status: response.status,
  });
};
//#endregion
