import { beforeEach, describe, expect, it, vi } from 'vitest';
import { addNotification, upsertRun } from '../app/store-actions';
import { workflowDispatcher } from '../dispatchers/workflow';
import { INPUTS_CLASSES } from '../elements/main.inputs';
import {
  getWorkflowSubmission,
  runWorkflow,
  uploadWorkflowFiles,
  WorkflowApiError,
} from '../services/workflow-service';
import { WorkflowRunRequestPayload, WorkflowRunResponse } from '../types/api';
import { WorkflowStore } from '../types/state';
import { setRetainedUploadPrefill } from '../utils/input-prefill';

vi.mock('../app/store-actions', () => ({
  addNotification: vi.fn(),
  clearResults: vi.fn(),
  ensureActiveRun: vi.fn(),
  setStatus: vi.fn(),
  upsertRun: vi.fn(),
}));

vi.mock('../services/workflow-service', () => {
  class WorkflowApiError extends Error {
    payload?: unknown;
    status?: number;

    constructor(
      message: string,
      options: { payload?: unknown; status?: number } = {},
    ) {
      super(message);
      this.name = 'WorkflowApiError';
      this.payload = options.payload;
      this.status = options.status;
    }
  }

  return {
    getWorkflowSubmission: vi.fn(async () => null),
    runWorkflow: vi.fn(),
    uploadWorkflowFiles: vi.fn(),
    WorkflowApiError,
  };
});

vi.mock('../utils/debug', () => ({ debugLog: vi.fn() }));

const successfulResponse = (request: WorkflowRunRequestPayload): WorkflowRunResponse => ({
  idempotentReplay: false,
  runId: `run-${request.submissionId}`,
  status: 'pending',
  submissionId: String(request.submissionId),
});

const createStore = () => {
  let prompt = 'original prompt';
  let files = [
    new File(['original bytes'], 'identity.png', {
      lastModified: 1_700_000_000_000,
      type: 'image/png',
    }),
  ];

  const text = document.createElement('lf-textfield') as HTMLLfTextfieldElement;
  text.id = 'prompt';
  text.getValue = vi.fn(async () => prompt);

  const upload = document.createElement('lf-upload') as HTMLLfUploadElement;
  upload.id = 'identity_image';
  upload.getValue = vi.fn(async () => files);

  const state: any = {
    current: { id: 'identity-edit', message: null, status: 'idle' },
    manager: {
      uiRegistry: {
        get: vi.fn(() => ({ [INPUTS_CLASSES.cells]: [text, upload] })),
      },
      workflow: { title: vi.fn(() => 'Identity Edit') },
    },
    mutate: {
      inputStatus: vi.fn(),
      submissionInFlight: vi.fn((submissionId: string | null) => {
        state.submissionInFlightId = submissionId;
      }),
    },
    submissionInFlightId: null,
  };

  return {
    setFile: (nextFile: File) => {
      files = [nextFile];
    },
    setPrompt: (value: string) => {
      prompt = value;
    },
    setRetainedArtifact: (sourceRunId: string, artifactId: string) => {
      files = [];
      setRetainedUploadPrefill(upload, {
        available: true,
        names: ['identity.png'],
        reference: {
          artifactId,
          filename: 'identity.png',
          schema: 'lf.workflow-artifact-ref.v1',
          sourceRunId,
        },
        schema: 'lf.workflow-upload-prefill.v1',
      });
    },
    store: { getState: vi.fn(() => state) } as unknown as WorkflowStore,
  };
};

describe('workflowDispatcher ambiguous retry identity', () => {
  beforeEach(() => {
    vi.mocked(getWorkflowSubmission).mockReset().mockResolvedValue(null);
    vi.mocked(runWorkflow).mockReset().mockImplementation(async (request) =>
      successfulResponse(request),
    );
    vi.mocked(uploadWorkflowFiles).mockReset().mockImplementation(async (files) => ({
      payload: { paths: [`uploaded/${files[0].name}`] },
    }) as any);
  });

  it('reuses the exact accepted-but-lost envelope and does not upload twice', async () => {
    const { store } = createStore();
    vi.mocked(runWorkflow).mockRejectedValueOnce(new TypeError('connection reset'));

    await workflowDispatcher(store);
    const firstEnvelope = vi.mocked(runWorkflow).mock.calls[0][0];

    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(1);
    expect(getWorkflowSubmission).toHaveBeenCalledWith(firstEnvelope.submissionId);
    expect(addNotification).toHaveBeenCalledWith(
      store,
      expect.objectContaining({
        message: expect.stringContaining('Retry is safe'),
        status: 'warning',
      }),
    );

    await workflowDispatcher(store);

    expect(runWorkflow).toHaveBeenCalledTimes(2);
    expect(vi.mocked(runWorkflow).mock.calls[1][0]).toBe(firstEnvelope);
    expect(vi.mocked(runWorkflow).mock.calls[1][0].submissionId).toBe(
      firstEnvelope.submissionId,
    );
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(1);
  });

  it('uses a fresh identity and rematerializes after a text intent change', async () => {
    const { setPrompt, store } = createStore();
    vi.mocked(runWorkflow).mockRejectedValueOnce(new TypeError('connection reset'));

    await workflowDispatcher(store);
    const firstEnvelope = vi.mocked(runWorkflow).mock.calls[0][0];
    setPrompt('changed prompt');
    await workflowDispatcher(store);
    const secondEnvelope = vi.mocked(runWorkflow).mock.calls[1][0];

    expect(secondEnvelope.submissionId === firstEnvelope.submissionId).toBe(false);
    expect(secondEnvelope.inputs.prompt).toBe('changed prompt');
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(2);
  });

  it('includes file metadata in intent identity', async () => {
    const { setFile, store } = createStore();
    vi.mocked(runWorkflow).mockRejectedValueOnce(new TypeError('connection reset'));

    await workflowDispatcher(store);
    const firstEnvelope = vi.mocked(runWorkflow).mock.calls[0][0];
    setFile(
      new File(['replacement'], 'replacement.png', {
        lastModified: 1_700_000_000_001,
        type: 'image/png',
      }),
    );
    await workflowDispatcher(store);

    expect(
      vi.mocked(runWorkflow).mock.calls[1][0].submissionId === firstEnvelope.submissionId,
    ).toBe(false);
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(2);
  });

  it('includes the retained artifact identity in intent identity', async () => {
    const { setRetainedArtifact, store } = createStore();
    setRetainedArtifact('source-run-1', 'a'.repeat(64));
    vi.mocked(runWorkflow).mockRejectedValueOnce(new TypeError('connection reset'));

    await workflowDispatcher(store);
    const firstEnvelope = vi.mocked(runWorkflow).mock.calls[0][0];
    setRetainedArtifact('source-run-2', 'b'.repeat(64));
    await workflowDispatcher(store);
    const secondEnvelope = vi.mocked(runWorkflow).mock.calls[1][0];

    expect(secondEnvelope.submissionId === firstEnvelope.submissionId).toBe(false);
    expect(secondEnvelope.inputs.identity_image).toEqual({
      artifactId: 'b'.repeat(64),
      filename: 'identity.png',
      schema: 'lf.workflow-artifact-ref.v1',
      sourceRunId: 'source-run-2',
    });
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(0);
  });

  it('uses a fresh id after an authoritative 4xx without reuploading unchanged files', async () => {
    const { store } = createStore();
    vi.mocked(runWorkflow).mockRejectedValueOnce(
      new WorkflowApiError('invalid input', {
        payload: { detail: 'invalid input' },
        status: 422,
      }),
    );

    await workflowDispatcher(store);
    const firstEnvelope = vi.mocked(runWorkflow).mock.calls[0][0];
    await workflowDispatcher(store);
    const secondEnvelope = vi.mocked(runWorkflow).mock.calls[1][0];

    expect(secondEnvelope === firstEnvelope).toBe(false);
    expect(secondEnvelope.submissionId === firstEnvelope.submissionId).toBe(false);
    expect(secondEnvelope.inputs).toEqual(firstEnvelope.inputs);
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(1);
    expect(getWorkflowSubmission).toHaveBeenCalledTimes(0);
  });

  it.each([
    [
      '5xx',
      () => new WorkflowApiError('server unavailable', { status: 503 }),
    ],
    ['network failure', () => new TypeError('connection reset')],
    ['timeout', () => new DOMException('timed out', 'AbortError')],
    [
      'invalid success response',
      () =>
        ({
          idempotentReplay: false,
          runId: '',
          status: 'pending',
          submissionId: 'wrong-submission',
        }) as WorkflowRunResponse,
    ],
  ])('retains the exact envelope after %s', async (_label, failure) => {
    const { store } = createStore();
    const outcome = failure();
    if (outcome instanceof Error) {
      vi.mocked(runWorkflow).mockRejectedValueOnce(outcome);
    } else {
      vi.mocked(runWorkflow).mockResolvedValueOnce(outcome);
    }

    await workflowDispatcher(store);
    const firstEnvelope = vi.mocked(runWorkflow).mock.calls[0][0];
    await workflowDispatcher(store);

    expect(vi.mocked(runWorkflow).mock.calls[1][0]).toBe(firstEnvelope);
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(1);
  });

  it('clears retry identity after a valid success', async () => {
    const { store } = createStore();

    await workflowDispatcher(store);
    const firstEnvelope = vi.mocked(runWorkflow).mock.calls[0][0];
    await workflowDispatcher(store);
    const secondEnvelope = vi.mocked(runWorkflow).mock.calls[1][0];

    expect(secondEnvelope.submissionId === firstEnvelope.submissionId).toBe(false);
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(2);
  });

  it('clears retry identity when GET reconciliation recovers the accepted run', async () => {
    const { store } = createStore();
    vi.mocked(runWorkflow).mockRejectedValueOnce(new TypeError('connection reset'));
    vi.mocked(getWorkflowSubmission).mockImplementationOnce(async (submissionId) => ({
      cancel_requested: false,
      created_at: 1,
      error: null,
      run_id: 'run-recovered',
      status: 'pending',
      submission_id: submissionId,
      updated_at: 2,
      workflow_id: 'identity-edit',
    }));

    await workflowDispatcher(store);
    const recoveredSubmissionId = vi.mocked(runWorkflow).mock.calls[0][0].submissionId;

    expect(upsertRun).toHaveBeenCalledWith(
      store,
      expect.objectContaining({
        runId: 'run-recovered',
        submissionId: recoveredSubmissionId,
      }),
    );
    await workflowDispatcher(store);
    expect(
      vi.mocked(runWorkflow).mock.calls[1][0].submissionId === recoveredSubmissionId,
    ).toBe(false);
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(2);
  });

  it('keeps the double-click lock to one upload and one POST', async () => {
    const { store } = createStore();
    let resolveRun: ((response: WorkflowRunResponse) => void) | undefined;
    vi.mocked(runWorkflow).mockImplementationOnce(
      () =>
        new Promise<WorkflowRunResponse>((resolve) => {
          resolveRun = resolve;
        }),
    );

    const firstClick = workflowDispatcher(store);
    await vi.waitFor(() => expect(runWorkflow).toHaveBeenCalledTimes(1));
    await workflowDispatcher(store);

    expect(runWorkflow).toHaveBeenCalledTimes(1);
    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(1);
    resolveRun?.(successfulResponse(vi.mocked(runWorkflow).mock.calls[0][0]));
    await firstClick;
  });
});
