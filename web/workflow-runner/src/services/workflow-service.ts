import { getLfFramework } from '@lf-widgets/framework';
import { API_BASE, buildApiUrl } from '../config';
import {
  WorkflowAPIDataset,
  WorkflowAPIErrorOptions,
  WorkflowAPIResponse,
  WorkflowAPIRunPayload,
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
  WorkflowRunRequestPayload,
  WorkflowRunResponse,
  WorkflowRunStatusResponse,
  WorkflowSubmissionSnapshot,
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
  if (response.status === 401) {
    // session expired or unauthorized -> redirect to hosted login page
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {
      // ignore in non-browser contexts
    }
    throw new WorkflowApiError('Unauthorized', { status: 401 });
  }
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
  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {}
    throw new WorkflowApiError('Unauthorized', { status: 401 });
  }
  const data = (await syntax.json.parse(response)) as Record<string, unknown> | null;

  if (!response.ok) {
    const message = `Failed to load workflow JSON (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }

  return data;
};
//#endregion

//#region Run Workflow
export const runWorkflow = async (payload: WorkflowRunRequestPayload): Promise<WorkflowRunResponse> => {
  const { RUN_GENERIC } = ERROR_MESSAGES;

  const { syntax } = getLfFramework();

  const response = await fetch(buildApiUrl('/run'), {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {}
    throw new WorkflowApiError('Unauthorized', { status: 401 });
  }

  let data:
    | WorkflowAPIResponse
    | {
        idempotent_replay?: boolean;
        run_id?: string;
        status?: WorkflowSubmissionSnapshot['status'];
        submission_id?: string;
      }
    | null;
  try {
    data = (await syntax.json.parse(response)) as typeof data;
  } catch {
    // The POST may already have crossed the queue boundary. Preserve the HTTP
    // status so callers can distinguish an explicit 4xx rejection from an
    // unreadable success/5xx response whose outcome is ambiguous.
    throw new WorkflowApiError(`${RUN_GENERIC} (invalid response)`, {
      status: response.status,
    });
  }

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

  const raw = data as {
    idempotent_replay?: boolean;
    run_id?: string;
    status?: WorkflowSubmissionSnapshot['status'];
    submission_id?: string;
  };
  const validStatuses = new Set<WorkflowSubmissionSnapshot['status']>([
    'accepted',
    'cancelled',
    'failed',
    'pending',
    'reconciling',
    'running',
    'succeeded',
    'timeout',
  ]);
  if (
    typeof raw.run_id !== 'string' ||
    !raw.run_id ||
    typeof raw.submission_id !== 'string' ||
    !raw.submission_id ||
    (payload.submissionId !== undefined && raw.submission_id !== payload.submissionId) ||
    (raw.status !== undefined && !validStatuses.has(raw.status)) ||
    (raw.idempotent_replay !== undefined && typeof raw.idempotent_replay !== 'boolean')
  ) {
    throw new WorkflowApiError(`${RUN_GENERIC} (invalid response)`, {
      status: response.status,
    });
  }

  return {
    idempotentReplay: raw.idempotent_replay === true,
    runId: raw.run_id,
    status: raw.status ?? 'pending',
    submissionId: raw.submission_id,
  };
};

export const getWorkflowSubmission = async (
  submissionId: string,
): Promise<WorkflowSubmissionSnapshot | null> => {
  const { syntax } = getLfFramework();
  const response = await fetch(
    buildApiUrl(`/submissions/${encodeURIComponent(submissionId)}`),
    {
      credentials: 'include',
      method: 'GET',
    },
  );
  if (response.status === 404) {
    return null;
  }
  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {}
    throw new WorkflowApiError('Unauthorized', { status: 401 });
  }

  let data: unknown;
  try {
    data = await syntax.json.parse(response);
  } catch {
    throw new WorkflowApiError('Invalid submission response.', { status: response.status });
  }
  if (!response.ok) {
    const detail =
      data && typeof data === 'object' && typeof (data as { detail?: unknown }).detail === 'string'
        ? (data as { detail: string }).detail
        : response.statusText;
    throw new WorkflowApiError(`Unable to reconcile submission (${detail || response.status}).`, {
      payload: data,
      status: response.status,
    });
  }

  const snapshot = data as Partial<WorkflowSubmissionSnapshot> | null;
  const validStatuses = new Set<WorkflowSubmissionSnapshot['status']>([
    'accepted',
    'cancelled',
    'failed',
    'pending',
    'reconciling',
    'running',
    'succeeded',
    'timeout',
  ]);
  if (
    !snapshot ||
    snapshot.submission_id !== submissionId ||
    (snapshot.run_id !== null && typeof snapshot.run_id !== 'string') ||
    typeof snapshot.workflow_id !== 'string' ||
    !snapshot.status ||
    !validStatuses.has(snapshot.status)
  ) {
    throw new WorkflowApiError('Invalid submission response.', { status: response.status });
  }
  return snapshot as WorkflowSubmissionSnapshot;
};

export const cancelWorkflowSubmission = async (
  submissionId: string,
): Promise<WorkflowSubmissionSnapshot> => {
  const response = await fetch(
    buildApiUrl(`/submissions/${encodeURIComponent(submissionId)}/cancel`),
    {
      credentials: 'include',
      method: 'POST',
    },
  );
  const data = (await response.json().catch(() => null)) as
    | WorkflowSubmissionSnapshot
    | { detail?: string; error?: string }
    | null;

  if (!response.ok || !data || !('submission_id' in data)) {
    const detail = data && 'detail' in data ? data.detail || data.error : response.statusText;
    throw new WorkflowApiError(`Unable to stop workflow (${detail || response.status}).`, {
      payload: data ?? undefined,
      status: response.status,
    });
  }

  return data;
};

export const getRunStatus = async (runId: string): Promise<WorkflowRunStatusResponse> => {
  const { RUN_GENERIC } = ERROR_MESSAGES;
  const { syntax } = getLfFramework();

  const response = await fetch(buildApiUrl(`/run/${runId}/status`), { method: 'GET' });
  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {}
    throw new WorkflowApiError('Unauthorized', { status: 401 });
  }
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
  // Runner uploads are reusable workflow inputs, not disposable previews.
  // Select Comfy's durable input storage explicitly and put the selector
  // before the streamed file parts so the upload endpoint applies it to every
  // file in this request.
  formData.append('directory', 'input');
  files.forEach((file) => formData.append('file', file));

  const response = await fetch(buildApiUrl('/upload'), {
    method: 'POST',
    body: formData,
  });

  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {}
    throw new WorkflowApiError('Unauthorized', { status: 401 });
  }

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
