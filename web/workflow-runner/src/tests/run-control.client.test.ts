import { afterEach, describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { getClientInternalsWithMethods } from './_utils';

describe('stable run control', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('restores the submission handle from a cold-load record and preserves it through SSE', () => {
    const store = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(store);
    const internals = getClientInternalsWithMethods(client);

    internals.processSnapshotArray([
      {
        run_id: 'run-restored',
        submission_id: 'lf-web:restored',
        cancel_requested: false,
        status: 'pending',
        seq: 1,
        created_at: 1_000,
      },
    ]);
    internals.applyEvent({
      run_id: 'run-restored',
      status: 'running',
      seq: 2,
    });

    const restored = store.getState().runs.find((run) => run.runId === 'run-restored');
    expect(restored?.submissionId).toBe('lf-web:restored');
    expect(restored?.status).toBe('running');
    expect(store.getState().currentRunId).toBe('run-restored');
  });

  it('posts the stable handle and applies terminal cancelled state', async () => {
    const store = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(store);
    getClientInternalsWithMethods(client).processSnapshotArray([
      {
        run_id: 'run-cancel',
        submission_id: 'lf-web:cancel-me',
        cancel_requested: false,
        status: 'pending',
        seq: 1,
        created_at: 1_000,
      },
    ]);
    const fetchMock = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) => ({
      ok: true,
      status: 202,
      statusText: 'Accepted',
      json: async () => ({
        cancel_requested: true,
        created_at: 1,
        run_id: 'run-cancel',
        status: 'cancelled',
        submission_id: 'lf-web:cancel-me',
        updated_at: 2,
        workflow_id: 'workflow-1',
      }),
    }));
    vi.stubGlobal('fetch', fetchMock);

    await client.cancelSubmission('lf-web:cancel-me', 'run-cancel');

    expect(fetchMock).toHaveBeenCalledOnce();
    expect(String(fetchMock.mock.calls[0][0])).toContain(
      '/submissions/lf-web%3Acancel-me/cancel',
    );
    const cancelled = store.getState().runs.find((run) => run.runId === 'run-cancel');
    expect(cancelled?.status).toBe('cancelled');
    expect(cancelled?.cancelRequested).toBe(true);
    expect(store.getState().currentRunId).toBeNull();
  });
});
