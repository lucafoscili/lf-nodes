import {
  WorkflowAPIDefinition,
  WorkflowAPIResponse,
  WorkflowAPIRunPayload,
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
} from '../types/api';
import { WorkflowStatus } from '../types/state';
import { buildApiUrl } from '../config';
import { isWorkflowAPIUploadPayload, isWorkflowAPIUploadResponse } from '../utils/common';

export interface WorkflowApiErrorOptions<TPayload> {
  payload?: TPayload;
  status?: number;
}

export class WorkflowApiError<TPayload = unknown> extends Error {
  readonly payload?: TPayload;
  readonly status?: number;

  constructor(message: string, options: WorkflowApiErrorOptions<TPayload> = {}) {
    super(message);
    this.name = 'WorkflowApiError';
    this.payload = options.payload;
    this.status = options.status;
  }
}

type JsonValue = Record<string, unknown> | WorkflowAPIResponse | WorkflowAPIUploadResponse | null;

async function parseJson(response: Response): Promise<JsonValue> {
  try {
    return (await response.json()) as JsonValue;
  } catch {
    return null;
  }
}

export const fetchWorkflowDefinitions = async (): Promise<WorkflowAPIDefinition[]> => {
  const response = await fetch(buildApiUrl('/workflows'), { method: 'GET' });
  const data = (await parseJson(response)) as { workflows?: WorkflowAPIDefinition[] } | null;

  if (!response.ok) {
    const message = `Failed to load workflows (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }

  if (!data || !Array.isArray(data.workflows)) {
    throw new WorkflowApiError('Invalid workflows response shape.', { payload: data });
  }

  return data.workflows;
};

export interface RunWorkflowResult extends WorkflowAPIResponse {
  status: Extract<WorkflowStatus, 'ready' | 'error'>;
  payload: WorkflowAPIRunPayload;
}

export const runWorkflowRequest = async (
  workflowId: string,
  inputs: Record<string, unknown>,
): Promise<RunWorkflowResult> => {
  const response = await fetch(buildApiUrl('/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workflowId, inputs }),
  });

  const data = (await parseJson(response)) as WorkflowAPIResponse | null;
  const payload: WorkflowAPIRunPayload =
    (data && data.payload) ||
    ({
      detail: response.statusText || 'unknown',
      history: {},
    } as WorkflowAPIRunPayload);

  if (!response.ok || !data) {
    const detail = payload?.detail || response.statusText || 'unknown';
    throw new WorkflowApiError(`Workflow execution failed: ${detail}`, {
      status: response.status,
      payload,
    });
  }

  return {
    message: data.message,
    payload,
    status: data.status as RunWorkflowResult['status'],
  };
};

export interface UploadWorkflowResult extends WorkflowAPIUploadResponse {
  payload: WorkflowAPIUploadPayload;
}

export const uploadWorkflowFiles = async (files: File[]): Promise<UploadWorkflowResult> => {
  if (!files || files.length === 0) {
    throw new WorkflowApiError<WorkflowAPIUploadPayload>('Missing file to upload.', {
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
      const detail = payload?.detail || response.statusText || 'unknown';
      throw new WorkflowApiError<WorkflowAPIUploadPayload>(`Upload failed: ${detail}`, {
        status: response.status,
        payload,
      });
    }

    return data;
  }

  if (isWorkflowAPIUploadPayload(data)) {
    if (!response.ok) {
      const detail = data.detail || response.statusText || 'unknown';
      throw new WorkflowApiError<WorkflowAPIUploadPayload>(`Upload failed: ${detail}`, {
        status: response.status,
        payload: data,
      });
    }

    return {
      message: 'Upload completed successfully.',
      payload: data,
      status: 'ready',
    };
  }

  throw new WorkflowApiError<WorkflowAPIUploadPayload>('Invalid response shape from upload API.', {
    status: response.status,
  });
};
