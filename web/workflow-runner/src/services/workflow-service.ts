import { getLfFramework } from '@lf-widgets/framework';
import { buildApiUrl } from '../config';
import {
  WorkflowAPIDataset,
  WorkflowAPIErrorOptions,
  WorkflowAPIResponse,
  WorkflowAPIRunPayload,
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
  WorkflowRunRequestPayload,
  WorkflowRunStatusResponse,
} from '../types/api';
import { isWorkflowAPIUploadPayload, isWorkflowAPIUploadResponse } from '../utils/common';
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
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl('/workflows'), { method: 'GET' });
  const data = (await syntax.json.parse(response)) as { workflows?: WorkflowAPIDataset } | null;

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
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl(`/workflows/${workflowId}`), { method: 'GET' });
  const data = (await syntax.json.parse(response)) as Record<string, unknown> | null;

  if (!response.ok) {
    const message = `Failed to load workflow JSON (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }

  return data;
};
//#endregion

//#region Run Workflow
export const runWorkflow = async (payload: WorkflowRunRequestPayload): Promise<string> => {
  const { RUN_GENERIC } = ERROR_MESSAGES;

  const { syntax } = getLfFramework();

  const response = await fetch(buildApiUrl('/run'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = (await syntax.json.parse(response)) as
    | WorkflowAPIResponse
    | { run_id?: string }
    | null;

  if (!response.ok || !data) {
    const payloadData =
      (data as WorkflowAPIResponse | null)?.payload ||
      ({ detail: response.statusText } as WorkflowAPIRunPayload);
    const detail = payloadData?.detail || response.statusText;
    throw new WorkflowApiError(`${RUN_GENERIC} (${detail})`, {
      payload: payloadData,
      status: response.status,
    });
  }

  const runId = (data as { run_id?: string }).run_id;
  if (!runId) {
    throw new WorkflowApiError(`${RUN_GENERIC} (invalid response)`, {
      status: response.status,
    });
  }

  return runId;
};

export const getRunStatus = async (runId: string): Promise<WorkflowRunStatusResponse> => {
  const { RUN_GENERIC } = ERROR_MESSAGES;
  const { syntax } = getLfFramework();

  const response = await fetch(buildApiUrl(`/run/${runId}/status`), { method: 'GET' });
  const data = (await syntax.json.parse(response)) as WorkflowRunStatusResponse | null;

  if (!response.ok || !data) {
    const detail =
      (typeof data?.error === 'string' && data.error) ||
      (typeof data?.result?.body?.payload?.detail === 'string' &&
        data.result.body.payload.detail) ||
      (data?.result?.body?.payload
        ? JSON.stringify(data.result.body.payload)
        : response.statusText) ||
      runId;
    throw new WorkflowApiError(`${RUN_GENERIC} (${detail})`, {
      payload: data ?? undefined,
      status: response.status,
    });
  }

  return data;
};
//#endregion

//#region Server-Sent Events (Run updates)
export const subscribeRunEvents = (
  onEvent: (ev: WorkflowRunStatusResponse) => void,
): EventSource | null => {
  try {
    const url = buildApiUrl('/run/events');
    const es = new EventSource(url);

    es.addEventListener('run', (ev: MessageEvent) => {
      try {
        const data = JSON.parse(ev.data) as WorkflowRunStatusResponse;
        onEvent(data);
      } catch (err) {
        // ignore malformed messages
      }
    });

    es.addEventListener('message', (ev: MessageEvent) => {
      try {
        const data = JSON.parse(ev.data) as WorkflowRunStatusResponse;
        onEvent(data);
      } catch (err) {
        // ignore
      }
    });

    return es;
  } catch (err) {
    return null;
  }
};
//#endregion

//#region Upload image
export const uploadWorkflowFiles = async (files: File[]): Promise<WorkflowAPIUploadResponse> => {
  const { UPLOAD_GENERIC, UPLOAD_INVALID_RESPONSE, UPLOAD_MISSING_FILE } = ERROR_MESSAGES;

  const { syntax } = getLfFramework();

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

  const data = await syntax.json.parse(response);
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
