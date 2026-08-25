import './setup';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord } from '../types/client';
import { attachMockLocalStorage, createMockLocalStorage, getClientInternalsWithMethods } from './_utils';

const response = (body: Record<string, unknown>, ok = true, status = 200) => ({
  json: async () => body,
  ok,
  status,
});

describe('WorkflowRunnerClient history cleanup', () => {
  beforeEach(() => {
    attachMockLocalStorage(createMockLocalStorage());
  });

  it('posts a dry-run scan without mutating client history', async () => {
    const store = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(store);
    getClientInternalsWithMethods(client).applyEvent({
      run_id: 'keep-for-preview',
      status: 'succeeded',
      seq: 1,
    });
    const fetchMock = vi.fn(async () =>
      response({
        candidate_count: 3,
        candidate_run_ids: ['candidate-a', 'candidate-b', 'candidate-c'],
        dry_run: true,
        removed_count: 0,
        removed_run_ids: [],
        skipped_changed: 0,
        skipped_unknown: 2,
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const result = await client.pruneMissingArtifacts(true);

    expect(result.candidate_count).toBe(3);
    expect(client.getRuns().has('keep-for-preview')).toBe(true);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/workflow-runner\/runs\/prune-missing-artifacts$/),
      expect.objectContaining({
        body: JSON.stringify({ dry_run: true }),
        credentials: 'include',
        method: 'POST',
      }),
    );
  });

  it('evicts removed IDs from maps, store, and cache immediately', async () => {
    const store = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(store);
    const internals = getClientInternalsWithMethods(client);
    for (const runId of ['remove-a', 'remove-b', 'keep']) {
      internals.applyEvent({ run_id: runId, status: 'succeeded', seq: 1 });
    }
    const fetchMock = vi.fn(async () =>
      response({
        candidate_count: 2,
        candidate_run_ids: ['remove-a', 'remove-b'],
        dry_run: false,
        removed_count: 2,
        removed_run_ids: ['remove-a', 'remove-b'],
        skipped_changed: 0,
        skipped_unknown: 1,
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    await client.pruneMissingArtifacts(false, ['remove-a', 'remove-b']);

    expect([...client.getRuns().keys()]).toEqual(['keep']);
    expect(store.getState().runs.map((run) => run.runId)).toEqual(['keep']);
    expect([...client.getLastSeq().keys()]).toEqual(['keep']);
    expect(JSON.parse(localStorage.getItem('lf-runs-cache') || '{}').run_ids).toEqual(['keep']);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/workflow-runner\/runs\/prune-missing-artifacts$/),
      expect.objectContaining({
        body: JSON.stringify({
          candidate_run_ids: ['remove-a', 'remove-b'],
          dry_run: false,
        }),
      }),
    );
  });

  it('does not let late detail or SSE payloads resurrect removed cards', async () => {
    const store = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(store);
    const internals = getClientInternalsWithMethods(client);
    internals.applyEvent({ run_id: 'stale', status: 'succeeded', seq: 1 });

    let resolveDetail: ((value: Record<string, unknown>) => void) | undefined;
    const detailBody = new Promise<Record<string, unknown>>((resolve) => {
      resolveDetail = resolve;
    });
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string, options?: RequestInit) => {
        if (url.includes('/run/stale/status')) {
          return { json: () => detailBody, ok: true, status: 200 };
        }
        const body = JSON.parse(String(options?.body || '{}')) as {
          candidate_run_ids?: string[];
          dry_run?: boolean;
        };
        return response({
          candidate_count: 1,
          candidate_run_ids: ['stale'],
          dry_run: Boolean(body.dry_run),
          removed_count: body.dry_run ? 0 : 1,
          removed_run_ids: body.dry_run ? [] : ['stale'],
          skipped_changed: 0,
          skipped_unknown: 0,
        });
      }),
    );

    const detailRequest = client.loadRunDetail('stale');
    await client.pruneMissingArtifacts(false, ['stale']);
    resolveDetail?.({ run_id: 'stale', status: 'succeeded', seq: 2 });
    await detailRequest;
    internals.applyEvent({ run_id: 'stale', status: 'succeeded', seq: 3 } as RunRecord);

    expect(client.getRuns().has('stale')).toBe(false);
    expect(store.getState().runs.some((run) => run.runId === 'stale')).toBe(false);
  });

  it('surfaces a useful API error', async () => {
    const client = new WorkflowRunnerClient(createWorkflowRunnerStore(initState()));
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => response({ detail: 'Cleanup unavailable' }, false, 503)),
    );

    await expect(client.pruneMissingArtifacts(true)).rejects.toThrow(
      'History cleanup failed (503). Cleanup unavailable',
    );
  });

  it('fails closed instead of executing without preview candidate IDs', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    const client = new WorkflowRunnerClient(createWorkflowRunnerStore(initState()));

    await expect(client.pruneMissingArtifacts(false)).rejects.toThrow(
      'requires the candidate IDs from a dry-run preview',
    );
    expect(fetchMock).toHaveBeenCalledTimes(0);
  });

  it('rejects a dry-run response whose count is not bound to exact IDs', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        response({
          candidate_count: 2,
          candidate_run_ids: ['only-one'],
          dry_run: true,
          removed_count: 0,
          removed_run_ids: [],
          skipped_changed: 0,
          skipped_unknown: 0,
        }),
      ),
    );
    const client = new WorkflowRunnerClient(createWorkflowRunnerStore(initState()));

    await expect(client.pruneMissingArtifacts(true)).rejects.toThrow(
      'preview did not identify its candidates safely',
    );
  });
});
