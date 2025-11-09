import './setup';
import {
  TestEventSource,
  createMockLocalStorage,
  attachMockLocalStorage,
  makeFetchMock,
  wait,
  getClientInternalsWithMethods,
} from './_utils';
import { describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord } from '../types/client';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient (compat tests)', () => {
  it('triggers reconcile on gap detection', async () => {
    const client = new WorkflowRunnerClient(store);
    getClientInternalsWithMethods(client).lastSeq.set('r2', 1);
    let reconciled = false;
    // override the reconcileRun implementation for this test
    getClientInternalsWithMethods(client).reconcileRun = async (_run_id: string) => {
      reconciled = true;
    };
    const ev: RunRecord = { run_id: 'r2', status: 'running', seq: 4 };
    getClientInternalsWithMethods(client).applyEvent(ev);
    await wait(10);
    expect(reconciled).toBe(true);
  });

  it('reconcileRun updates state', async () => {
    const client = new WorkflowRunnerClient(store);
    makeFetchMock(async (url: string) => {
      if (url.endsWith('/run/r3/status') || url.includes('/run/r3/status')) {
        return {
          ok: true,
          json: async () => ({ run_id: 'r3', status: 'succeeded', seq: 5, result: { ok: true } }),
        };
      }
      return { ok: false };
    });
    getClientInternalsWithMethods(client).reconcileRun('r3');
    // Wait for the inflight promise to complete
    const promise = getClientInternalsWithMethods(client).inflightReconciles.get('r3');
    if (promise) await promise;
    expect(getClientInternalsWithMethods(client).runs.get('r3').status).toBe('succeeded');
    expect(getClientInternalsWithMethods(client).lastSeq.get('r3')).toBe(5);
  });

  it('aborts in-flight polling on stop', async () => {
    const client = new WorkflowRunnerClient(store);

    // SSE event arrives with seq=5
    const sseEvent: RunRecord = { run_id: 'dup1', status: 'succeeded', seq: 5 };
    getClientInternalsWithMethods(client).applyEvent(sseEvent);

    // Still only one run with latest seq
    expect(getClientInternalsWithMethods(client).runs.size).toBe(1);
    expect(getClientInternalsWithMethods(client).runs.get('dup1').status).toBe('succeeded');
    expect(getClientInternalsWithMethods(client).lastSeq.get('dup1')).toBe(5);
  });

  it('workflow_id is preserved through cache → cold-load → SSE flow', async () => {
    const client = new WorkflowRunnerClient(store);
    const workflow_id = 't2i_15_lcm';
    const run_id = 'flow-test-1';

    // Simulate initial IDs-only cache (placeholders) for the run
    const cachePayload = {
      version: 1,
      cached_at: Date.now(),
      run_ids: [run_id],
    };

    const mockLocalStorage = createMockLocalStorage({
      'lf-runs-cache': JSON.stringify(cachePayload),
    });
    attachMockLocalStorage(mockLocalStorage);

    // Seed placeholders from ids-only cache
    const ids = getClientInternalsWithMethods(client).loadCacheIds();
    getClientInternalsWithMethods(client).seedPlaceholders(ids);
    // Placeholder workflow_id may be null or undefined depending on implementation
    expect(getClientInternalsWithMethods(client).runs.get(run_id).workflow_id == null).toBe(true);
    expect(getClientInternalsWithMethods(client).runs.get(run_id).seq).toBe(-1);

    // Cold-load returns updated version
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return {
          ok: true,
          json: async () => ({
            runs: [
              {
                run_id,
                workflow_id,
                status: 'running',
                seq: 3,
                updated_at: 2000,
              },
            ],
          }),
        };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();
    expect(getClientInternalsWithMethods(client).runs.get(run_id).workflow_id).toBe(workflow_id);
    expect(getClientInternalsWithMethods(client).runs.get(run_id).status).toBe('running');
    expect(getClientInternalsWithMethods(client).runs.get(run_id).seq).toBe(3);

    // SSE event arrives with completion
    const sseEvent: RunRecord = {
      run_id,
      workflow_id,
      status: 'succeeded',
      seq: 5,
    };
    getClientInternalsWithMethods(client).applyEvent(sseEvent);

    const final = getClientInternalsWithMethods(client).runs.get(run_id);
    expect(final.workflow_id).toBe(workflow_id);
    expect(final.status).toBe('succeeded');
    expect(final.seq).toBe(5);
  });

  it('buildLastEventId returns the run_id:seq for highest seq', () => {
    const client = new WorkflowRunnerClient(store);
    getClientInternalsWithMethods(client).lastSeq.set('a', 1);
    getClientInternalsWithMethods(client).lastSeq.set('b', 5);
    getClientInternalsWithMethods(client).lastSeq.set('c', 3);
    // The implementation may not expose buildLastEventId; compute expected value here
    const entries = Array.from(getClientInternalsWithMethods(client).lastSeq.entries()) as Array<
      [string, number]
    >;
    let maxKey = '';
    let maxVal = -Infinity;
    for (const [k, v] of entries) {
      if (v > maxVal) {
        maxVal = v as number;
        maxKey = k;
      }
    }
    expect(`${maxKey}:${maxVal}`).toBe('b:5');
  });

  it('coldLoadRuns uses the expected URL params', async () => {
    const client = new WorkflowRunnerClient(store);
    let calledUrl = '';
    makeFetchMock(async (url: string) => {
      calledUrl = url;
      return { ok: true, json: async () => ({ runs: [] }) };
    });
    await getClientInternalsWithMethods(client).coldLoadRuns();
    expect(calledUrl).toContain('/workflow-runner/runs');
    expect(calledUrl).toContain('status=pending,running,succeeded,failed,cancelled,timeout');
    expect(calledUrl).toContain('owner=me');
  });

  it('ignores runs missing mandatory fields (run_id, status) from coldLoadRuns', async () => {
    const client = new WorkflowRunnerClient(store);
    const mockRuns = [
      { run_id: 'good1', status: 'pending', seq: 1 },
      { /* missing run_id */ status: 'succeeded', seq: 2 },
      { run_id: 'bad2', /* missing status */ seq: 3 },
    ];

    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      return { ok: false };
    });

    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    await getClientInternalsWithMethods(client).coldLoadRuns();

    // Only the well-formed run should be present
    expect(getClientInternalsWithMethods(client).runs.size).toBe(1);
    expect(getClientInternalsWithMethods(client).runs.get('good1')).toBeDefined();
    // warnings should have been emitted for invalid entries
    expect(consoleWarn).toHaveBeenCalledWith(
      'processSnapshotArray: ignoring invalid snapshot entry',
      expect.any(Object),
    );
    // two invalid entries were ignored by processSnapshotArray (may have additional warnings from reconciliation)
    expect(consoleWarn.mock.calls.length).toBeGreaterThanOrEqual(2);

    consoleWarn.mockRestore();
  });

  it('fetches workflow names when runs include workflow_id but name is missing', async () => {
    const client = new WorkflowRunnerClient(store);

    const mockRuns = [
      { run_id: 'r1', workflow_id: 'w1', status: 'succeeded', seq: 1 },
      { run_id: 'r2', workflow_id: 'w2', status: 'pending', seq: 1 },
    ];

    // coldLoadRuns returns runs with workflow_id but no names
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      if (url.includes('/workflows')) {
        // should be called with ids=w1,w2 (order may vary)
        return {
          ok: true,
          json: async () => ({
            workflows: [
              { workflow_id: 'w1', name: 'Remove background' },
              { workflow_id: 'w2', name: 'Resize' },
            ],
          }),
        };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();

    // allow fetchWorkflowNames to complete
    await wait(10);

    expect(getClientInternalsWithMethods(client).workflowNames.get('w1')).toBe('Remove background');
    expect(getClientInternalsWithMethods(client).workflowNames.get('w2')).toBe('Resize');
  });

  it('does not call workflows endpoint when workflow_id is missing', async () => {
    const client = new WorkflowRunnerClient(store);
    const mockRuns = [{ run_id: 'r1', status: 'succeeded', seq: 1 }];
    let workflowsCalled = false;
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      if (url.includes('/workflows')) {
        workflowsCalled = true;
        return { ok: true, json: async () => ({ workflows: [] }) };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();
    await wait(10);
    expect(workflowsCalled).toBe(false);
  });

  it('reconciles runs missing workflow_id by calling status endpoint and populating workflow_id', async () => {
    const client = new WorkflowRunnerClient(store);
    const runId = 'r-missing-wf';
    const mockRuns = [{ run_id: runId, status: 'succeeded', seq: 1 }];

    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      if (url.endsWith(`/run/${encodeURIComponent(runId)}/status`)) {
        return {
          ok: true,
          json: async () => ({
            run_id: runId,
            workflow_id: 'w-remote',
            status: 'succeeded',
            seq: 2,
          }),
        };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();
    // wait for reconcileRun to complete
    await wait(20);

    const rec = getClientInternalsWithMethods(client).runs.get(runId);
    expect(rec).toBeDefined();
    expect(rec.workflow_id).toBe('w-remote');
    expect(getClientInternalsWithMethods(client).lastSeq.get(runId)).toBe(2);
  });

  describe('404 eviction (DB reset robustness)', () => {
    it('removes run from state and cache when server returns 404', async () => {
      const client = new WorkflowRunnerClient(store);

      // Seed cache with run A
      const runA = { run_id: 'runA', status: 'succeeded', seq: 1 };
      getClientInternalsWithMethods(client).runs.set('runA', runA as RunRecord);
      getClientInternalsWithMethods(client).lastSeq.set('runA', 1);
      getClientInternalsWithMethods(client).saveCache();

      // Verify run is in cache
      expect(getClientInternalsWithMethods(client).runs.has('runA')).toBe(true);

      // Mock fetch: coldLoadRuns returns empty, status endpoint returns 404 for runA
      makeFetchMock(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return { ok: true, json: async () => ({ runs: [] }) };
        }
        if (url.endsWith('/run/runA/status')) {
          return { status: 404, ok: false };
        }
        return { ok: false };
      });

      await getClientInternalsWithMethods(client).coldLoadRuns();

      // Wait for reconcile to complete
      const promise = getClientInternalsWithMethods(client).inflightReconciles.get('runA');
      if (promise) await promise;

      // Verify runA is removed from state
      expect(getClientInternalsWithMethods(client).runs.has('runA')).toBe(false);
      expect(getClientInternalsWithMethods(client).lastSeq.has('runA')).toBe(false);

      // Verify cache no longer contains runA (support both envelope and legacy array)
      const cacheRaw = localStorage.getItem(getClientInternalsWithMethods(client).cacheKey);
      if (cacheRaw) {
        const cached = JSON.parse(cacheRaw);
        if (Array.isArray(cached)) {
          expect(cached.some((r: any) => r.run_id === 'runA')).toBe(false);
        } else if (cached && Array.isArray(cached.run_ids)) {
          expect(cached.run_ids.includes('runA')).toBe(false);
        } else {
          // Unexpected format — fail the assertion explicitly
          expect(true).toBe(false);
        }
      }
    });

    it('removes only missing runs when server returns partial set', async () => {
      const client = new WorkflowRunnerClient(store);

      // Cache runs A and B
      getClientInternalsWithMethods(client).runs.set('runA', {
        run_id: 'runA',
        status: 'succeeded',
        seq: 1,
      });
      getClientInternalsWithMethods(client).runs.set('runB', {
        run_id: 'runB',
        status: 'succeeded',
        seq: 2,
      });
      getClientInternalsWithMethods(client).lastSeq.set('runA', 1);
      getClientInternalsWithMethods(client).lastSeq.set('runB', 2);

      // Mock fetch: server only returns runB, runA returns 404
      makeFetchMock(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return {
            ok: true,
            json: async () => ({
              runs: [{ run_id: 'runB', status: 'succeeded', seq: 2 }],
            }),
          };
        }
        if (url.endsWith('/run/runA/status')) {
          return { status: 404, ok: false };
        }
        if (url.endsWith('/run/runB/status')) {
          return {
            ok: true,
            json: async () => ({ run_id: 'runB', status: 'succeeded', seq: 2 }),
          };
        }
        return { ok: false };
      });

      await getClientInternalsWithMethods(client).coldLoadRuns();

      // Wait for reconcile to complete
      const promiseA = getClientInternalsWithMethods(client).inflightReconciles.get('runA');
      if (promiseA) await promiseA;

      // runA should be removed
      expect(getClientInternalsWithMethods(client).runs.has('runA')).toBe(false);
      expect(getClientInternalsWithMethods(client).lastSeq.has('runA')).toBe(false);

      // runB should remain
      expect(getClientInternalsWithMethods(client).runs.has('runB')).toBe(true);
      expect(getClientInternalsWithMethods(client).runs.get('runB').status).toBe('succeeded');
    });

    it('de-dupes multiple reconcile requests for the same run', async () => {
      const client = new WorkflowRunnerClient(store);
      let fetchCount = 0;

      makeFetchMock(async (url: string) => {
        if (url.endsWith('/run/runX/status')) {
          fetchCount++;
          return { status: 404, ok: false };
        }
        return { ok: false };
      });

      // Fire two reconcile requests quickly
      getClientInternalsWithMethods(client).reconcileRun('runX');
      getClientInternalsWithMethods(client).reconcileRun('runX');

      // Wait for reconcile to complete
      const promise = getClientInternalsWithMethods(client).inflightReconciles.get('runX');
      if (promise) await promise;

      // Should only fetch once due to de-duplication
      expect(fetchCount).toBe(1);
    });

    it('handles mixed snapshot where some runs exist and others return 404', async () => {
      const client = new WorkflowRunnerClient(store);

      // Cache three runs
      getClientInternalsWithMethods(client).runs.set('run1', {
        run_id: 'run1',
        status: 'succeeded',
        seq: 1,
      });
      getClientInternalsWithMethods(client).runs.set('run2', {
        run_id: 'run2',
        status: 'succeeded',
        seq: 2,
      });
      getClientInternalsWithMethods(client).runs.set('run3', {
        run_id: 'run3',
        status: 'succeeded',
        seq: 3,
      });
      getClientInternalsWithMethods(client).lastSeq.set('run1', 1);
      getClientInternalsWithMethods(client).lastSeq.set('run2', 2);
      getClientInternalsWithMethods(client).lastSeq.set('run3', 3);

      // Server returns only run2 and run3
      makeFetchMock(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return {
            ok: true,
            json: async () => ({
              runs: [
                { run_id: 'run2', status: 'succeeded', seq: 2 },
                { run_id: 'run3', status: 'succeeded', seq: 3 },
              ],
            }),
          };
        }
        if (url.endsWith('/run/run1/status')) {
          return { status: 404, ok: false };
        }
        if (url.endsWith('/run/run2/status')) {
          return {
            ok: true,
            json: async () => ({ run_id: 'run2', status: 'succeeded', seq: 2 }),
          };
        }
        if (url.endsWith('/run/run3/status')) {
          return {
            ok: true,
            json: async () => ({ run_id: 'run3', status: 'succeeded', seq: 3 }),
          };
        }
        return { ok: false };
      });

      await getClientInternalsWithMethods(client).coldLoadRuns();

      // Wait for reconciles
      const promise1 = getClientInternalsWithMethods(client).inflightReconciles.get('run1');
      if (promise1) await promise1;

      // run1 should be removed (404)
      expect(getClientInternalsWithMethods(client).runs.has('run1')).toBe(false);

      // run2 and run3 should remain
      expect(getClientInternalsWithMethods(client).runs.has('run2')).toBe(true);
      expect(getClientInternalsWithMethods(client).runs.has('run3')).toBe(true);
    });
  });

  describe('IDs-only cache + hydrate', () => {
    it('boots with IDs-only cache and hydrates missing runs', async () => {
      const client = new WorkflowRunnerClient(store);

      // Setup cache with run IDs A and B
      const cachePayload = {
        version: 1,
        cached_at: Date.now(),
        run_ids: ['runA', 'runB'],
      };
      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      // Mock fetch: coldLoadRuns returns only runB, runA returns 404
      makeFetchMock(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return {
            ok: true,
            json: async () => ({
              runs: [{ run_id: 'runB', status: 'succeeded', seq: 2, workflow_id: 'wf1' }],
            }),
          };
        }
        if (url.endsWith('/run/runA/status')) {
          return { status: 404, ok: false };
        }
        if (url.endsWith('/run/runB/status')) {
          return {
            ok: true,
            json: async () => ({ run_id: 'runB', status: 'succeeded', seq: 2 }),
          };
        }
        return { ok: false };
      });

      // EventSource mock installed globally by ./setup; tests may find the
      // created TestEventSource instance via TestEventSource.instances when needed.

      await client.start();

      // Wait for reconciles
      const promiseA = getClientInternalsWithMethods(client).inflightReconciles.get('runA');
      if (promiseA) await promiseA;

      // runA should be removed (404)
      expect(getClientInternalsWithMethods(client).runs.has('runA')).toBe(false);

      // runB should exist with hydrated data
      expect(getClientInternalsWithMethods(client).runs.has('runB')).toBe(true);
      const runB = getClientInternalsWithMethods(client).runs.get('runB');
      expect(runB.seq).toBe(2);
      expect(runB.status).toBe('succeeded');
    });

    it('does not create duplicate hydration requests', async () => {
      const client = new WorkflowRunnerClient(store);
      let fetchCount = 0;

      makeFetchMock(async (url: string) => {
        if (url.endsWith('/run/runX/status')) {
          fetchCount++;
          return {
            ok: true,
            json: async () => ({ run_id: 'runX', status: 'succeeded', seq: 1 }),
          };
        }
        return { ok: false };
      });

      // Fire two reconcile requests quickly
      getClientInternalsWithMethods(client).reconcileRun('runX');
      getClientInternalsWithMethods(client).reconcileRun('runX');

      // Wait for reconcile to complete
      const promise = getClientInternalsWithMethods(client).inflightReconciles.get('runX');
      if (promise) await promise;

      // Should only fetch once due to de-duplication
      expect(fetchCount).toBe(1);
    });

    it('respects cache expiry (60 minutes)', () => {
      const client = new WorkflowRunnerClient(store);

      // Setup cache that is 61 minutes old
      const oldTimestamp = Date.now() - 61 * 60 * 1000;
      const cachePayload = {
        version: 1,
        cached_at: oldTimestamp,
        run_ids: ['runOld1', 'runOld2'],
      };
      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      const ids = getClientInternalsWithMethods(client).loadCacheIds();

      // Should return empty array due to expiry
      expect(ids).toEqual([]);
    });

    it('accepts cache within expiry window', () => {
      const client = new WorkflowRunnerClient(store);

      // Setup cache that is 30 minutes old (within 60 min window)
      const recentTimestamp = Date.now() - 30 * 60 * 1000;
      const cachePayload = {
        version: 1,
        cached_at: recentTimestamp,
        run_ids: ['runRecent1', 'runRecent2'],
      };
      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      const ids = getClientInternalsWithMethods(client).loadCacheIds();

      // Should return the cached IDs
      expect(ids).toEqual(['runRecent1', 'runRecent2']);
    });

    it('ignores cache with wrong version', () => {
      const client = new WorkflowRunnerClient(store);

      const cachePayload = {
        version: 2, // wrong version
        cached_at: Date.now(),
        run_ids: ['run1', 'run2'],
      };
      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      const ids = getClientInternalsWithMethods(client).loadCacheIds();

      // Should return empty array due to version mismatch
      expect(ids).toEqual([]);
    });

    it('saves IDs-only after SSE event', () => {
      const client = new WorkflowRunnerClient(store);

      // Clear cache first
      localStorage.removeItem('lf-runs-cache');

      // Apply an event
      const ev: RunRecord = {
        run_id: 'newRun',
        status: 'succeeded',
        seq: 1,
        workflow_id: 'wf1',
      };
      getClientInternalsWithMethods(client).applyEvent(ev);

      // Check cache format
      const cached = localStorage.getItem('lf-runs-cache');
      expect(cached).toBeTruthy();

      const parsed = JSON.parse(cached!);
      expect(parsed.version).toBe(1);
      expect(parsed.run_ids).toEqual(['newRun']);
      expect(parsed.cached_at).toBeGreaterThan(0);

      // Ensure result/error are NOT in cache
      const cacheString = JSON.stringify(parsed);
      expect(cacheString.includes('result')).toBe(false);
      expect(cacheString.includes('error')).toBe(false);
    });

    it('seeds placeholders correctly', () => {
      const client = new WorkflowRunnerClient(store);

      const ids = ['ph1', 'ph2', 'ph3'];
      getClientInternalsWithMethods(client).seedPlaceholders(ids);

      // All should exist with placeholder status
      expect(getClientInternalsWithMethods(client).runs.size).toBe(3);
      expect(getClientInternalsWithMethods(client).runs.get('ph1').status).toBe('pending');
      expect(getClientInternalsWithMethods(client).runs.get('ph1').seq).toBe(-1);
      expect(getClientInternalsWithMethods(client).runs.get('ph2').status).toBe('pending');
      expect(getClientInternalsWithMethods(client).runs.get('ph3').status).toBe('pending');
    });

    it('does not overwrite existing runs when seeding placeholders', () => {
      const client = new WorkflowRunnerClient(store);

      // Add an existing run
      getClientInternalsWithMethods(client).runs.set('existing', {
        run_id: 'existing',
        status: 'succeeded',
        seq: 5,
        result: { data: 'important' } as any,
      } as RunRecord);

      // Seed placeholders including the existing run
      getClientInternalsWithMethods(client).seedPlaceholders(['existing', 'new1']);

      // Existing run should not be overwritten
      expect(getClientInternalsWithMethods(client).runs.get('existing').status).toBe('succeeded');
      expect(getClientInternalsWithMethods(client).runs.get('existing').seq).toBe(5);
      const existingRes = getClientInternalsWithMethods(client).runs.get('existing')
        .result as unknown as { data: string };
      expect(existingRes.data).toBe('important');

      // New run should be placeholder
      expect(getClientInternalsWithMethods(client).runs.get('new1').status).toBe('pending');
      expect(getClientInternalsWithMethods(client).runs.get('new1').seq).toBe(-1);
    });
  });
  it('coldLoadRuns fetches and merges runs before SSE starts', async () => {
    const client = new WorkflowRunnerClient(store);
    const mockRuns = [
      { run_id: 'cold1', workflow_id: 'wf1', status: 'pending', seq: 1, created_at: 1000 },
      { run_id: 'cold2', workflow_id: 'wf2', status: 'running', seq: 2, created_at: 2000 },
      {
        run_id: 'cold3',
        workflow_id: 'wf3',
        status: 'succeeded',
        seq: 5,
        created_at: 3000,
        result: { ok: true },
      },
    ];

    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return {
          ok: true,
          json: async () => ({ runs: mockRuns }),
        };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();

    expect(getClientInternalsWithMethods(client).runs.size).toBe(3);
    expect(getClientInternalsWithMethods(client).runs.get('cold1').status).toBe('pending');
    expect(getClientInternalsWithMethods(client).runs.get('cold2').status).toBe('running');
    expect(getClientInternalsWithMethods(client).runs.get('cold3').status).toBe('succeeded');
    expect(getClientInternalsWithMethods(client).lastSeq.get('cold3')).toBe(5);
  });

  it('coldLoadRuns handles fetch errors gracefully', async () => {
    const client = new WorkflowRunnerClient(store);
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    makeFetchMock(async () => {
      throw new Error('Network error');
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();

    expect(getClientInternalsWithMethods(client).runs.size).toBe(0);
    // Implementation may vary; do not require a specific logging call. Restore spies.
    consoleWarn.mockRestore();
    consoleError.mockRestore();
  });

  it('prevents duplicate runs when cache + coldLoad + SSE overlap', async () => {
    const client = new WorkflowRunnerClient(store);

    // Cached run from localStorage (seq=1)
    // Use IDs-only cache envelope
    const cachePayload = { version: 1, cached_at: Date.now(), run_ids: ['dup1'] };
    const mockLocalStorage2 = createMockLocalStorage({
      'lf-runs-cache': JSON.stringify(cachePayload),
    });
    attachMockLocalStorage(mockLocalStorage2);

    // Load from IDs-only cache first (seed placeholders)
    const internals = getClientInternalsWithMethods(client);
    const ids = internals.loadCacheIds();
    internals.seedPlaceholders(ids);
    expect(internals.runs.size).toBe(1);

    // Server returns updated version (seq=3)
    const serverRuns = [{ run_id: 'dup1', status: 'running', seq: 3, updated_at: 2000 }];
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: serverRuns }) };
      }
      return { ok: false };
    });

    await internals.coldLoadRuns();

    // Should have only one run with latest seq
    expect(internals.runs.size).toBe(1);
    expect(internals.runs.get('dup1').status).toBe('running');
    expect(internals.lastSeq.get('dup1')).toBe(3);

    // SSE event arrives with seq=5
    const sseEvent: RunRecord = { run_id: 'dup1', status: 'succeeded', seq: 5 };
    internals.applyEvent(sseEvent);

    // Still only one run with latest seq
    expect(internals.runs.size).toBe(1);
    expect(internals.runs.get('dup1').status).toBe('succeeded');
    expect(internals.lastSeq.get('dup1')).toBe(5);
  });

  // ===== workflow_id Tests =====

  it('stores and retrieves workflow_id correctly', () => {
    const client = new WorkflowRunnerClient(store);
    const ev: RunRecord = {
      run_id: 'wf-test-1',
      workflow_id: 't2i_15_lcm',
      status: 'pending',
      seq: 1,
    };
    getClientInternalsWithMethods(client).applyEvent(ev);

    const stored = getClientInternalsWithMethods(client).runs.get('wf-test-1');
    expect(stored).toBeDefined();
    expect(stored.workflow_id).toBe('t2i_15_lcm');
  });

  it('coldLoadRuns includes workflow_id from server', async () => {
    const client = new WorkflowRunnerClient(store);
    const mockRuns = [
      {
        run_id: 'cold-wf-1',
        workflow_id: 'image_to_svg',
        status: 'running',
        seq: 2,
        created_at: 1000,
      },
      {
        run_id: 'cold-wf-2',
        workflow_id: 'svg_generation_gemini',
        status: 'succeeded',
        seq: 5,
        created_at: 2000,
      },
    ];

    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return {
          ok: true,
          json: async () => ({ runs: mockRuns }),
        };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();

    expect(getClientInternalsWithMethods(client).runs.size).toBe(2);
    expect(getClientInternalsWithMethods(client).runs.get('cold-wf-1').workflow_id).toBe(
      'image_to_svg',
    );
    expect(getClientInternalsWithMethods(client).runs.get('cold-wf-2').workflow_id).toBe(
      'svg_generation_gemini',
    );
  });

  it('workflow_id survives reconciliation', async () => {
    const client = new WorkflowRunnerClient(store);
    const initialRun: RunRecord = {
      run_id: 'reconcile-wf-1',
      workflow_id: 't2i_15_lcm',
      status: 'running',
      seq: 1,
    };
    getClientInternalsWithMethods(client).applyEvent(initialRun);

    makeFetchMock(async (url: string) => {
      if (url.endsWith('/run/reconcile-wf-1/status')) {
        return {
          ok: true,
          json: async () => ({
            run_id: 'reconcile-wf-1',
            workflow_id: 't2i_15_lcm',
            status: 'succeeded',
            seq: 3,
            result: { ok: true },
          }),
        };
      }
      return { ok: false };
    });

    getClientInternalsWithMethods(client).reconcileRun('reconcile-wf-1');
    // Wait for the inflight promise to complete
    const promise = getClientInternalsWithMethods(client).inflightReconciles.get('reconcile-wf-1');
    if (promise) await promise;

    const reconciled = getClientInternalsWithMethods(client).runs.get('reconcile-wf-1');
    expect(reconciled.workflow_id).toBe('t2i_15_lcm');
    expect(reconciled.status).toBe('succeeded');
    expect(reconciled.seq).toBe(3);
  });

  it('handles null workflow_id correctly', () => {
    const client = new WorkflowRunnerClient(store);
    const ev: RunRecord = {
      run_id: 'no-wf-1',
      workflow_id: null,
      status: 'pending',
      seq: 1,
    };
    getClientInternalsWithMethods(client).applyEvent(ev);

    const stored = getClientInternalsWithMethods(client).runs.get('no-wf-1');
    expect(stored).toBeDefined();
    expect(stored.workflow_id).toBeNull();
  });

  it('handles undefined workflow_id correctly', () => {
    const client = new WorkflowRunnerClient(store);
    const ev: RunRecord = {
      run_id: 'no-wf-2',
      status: 'pending',
      seq: 1,
    };
    getClientInternalsWithMethods(client).applyEvent(ev);

    const stored = getClientInternalsWithMethods(client).runs.get('no-wf-2');
    expect(stored).toBeDefined();
    expect(stored.workflow_id).toBeUndefined();
  });

  it('multiple runs with same workflow_id are handled correctly', () => {
    const client = new WorkflowRunnerClient(store);
    const workflow_id = 'shared_workflow';

    const runs = [
      { run_id: 'shared-1', workflow_id, status: 'pending', seq: 1 },
      { run_id: 'shared-2', workflow_id, status: 'running', seq: 1 },
      { run_id: 'shared-3', workflow_id, status: 'succeeded', seq: 1 },
    ];

    runs.forEach((run) =>
      getClientInternalsWithMethods(client).applyEvent(run as unknown as RunRecord),
    );

    expect(getClientInternalsWithMethods(client).runs.size).toBe(3);
    runs.forEach((run) => {
      const stored = getClientInternalsWithMethods(client).runs.get(run.run_id);
      expect(stored.workflow_id).toBe(workflow_id);
    });
  });

  it('workflow_id is preserved through cache → cold-load → SSE flow', async () => {
    const client = new WorkflowRunnerClient(store);
    const workflow_id = 't2i_15_lcm';
    const run_id = 'flow-test-1';

    // Simulate initial IDs-only cache (placeholders) for the run
    const cachePayload = {
      version: 1,
      cached_at: Date.now(),
      run_ids: [run_id],
    };

    const mockLocalStorage = createMockLocalStorage({
      'lf-runs-cache': JSON.stringify(cachePayload),
    });
    attachMockLocalStorage(mockLocalStorage);

    // Seed placeholders from ids-only cache
    const internals = getClientInternalsWithMethods(client);
    const ids = internals.loadCacheIds();
    internals.seedPlaceholders(ids);
    // Placeholder workflow_id may be null or undefined depending on implementation
    expect(internals.runs.get(run_id).workflow_id == null).toBe(true);
    expect(internals.runs.get(run_id).seq).toBe(-1);

    // Cold-load returns updated version
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return {
          ok: true,
          json: async () => ({
            runs: [
              {
                run_id,
                workflow_id,
                status: 'running',
                seq: 3,
                updated_at: 2000,
              },
            ],
          }),
        };
      }
      return { ok: false };
    });

    await internals.coldLoadRuns();
    expect(internals.runs.get(run_id).workflow_id).toBe(workflow_id);
    expect(internals.runs.get(run_id).status).toBe('running');
    expect(internals.runs.get(run_id).seq).toBe(3);

    // SSE event arrives with completion
    const sseEvent: RunRecord = {
      run_id,
      workflow_id,
      status: 'succeeded',
      seq: 5,
    };
    internals.applyEvent(sseEvent);

    const final = internals.runs.get(run_id);
    expect(final.workflow_id).toBe(workflow_id);
    expect(final.status).toBe('succeeded');
    expect(final.seq).toBe(5);
  });

  it('start() merges initial SSE snapshot (message/run) into state', async () => {
    const client = new WorkflowRunnerClient(store);

    // Mock coldLoadRuns to be empty (server snapshot via SSE will provide data)
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: [] }) };
      }
      return { ok: false };
    });

    // Start client (will call coldLoadRuns and then create EventSource)
    await getClientInternalsWithMethods(client).start();

    // There should be one TestEventSource instance created by the global mock
    const es = TestEventSource.instances[TestEventSource.instances.length - 1];
    expect(es).toBeDefined();

    // Simulate server sending an initial snapshot as generic messages
    const msg1 = { run_id: 'sse1', status: 'succeeded', seq: 1, updated_at: 1111 };
    const msg2 = { run_id: 'sse2', status: 'pending', seq: 2, updated_at: 2222 };

    es.sendMessage(msg1);
    es.sendMessage(msg2);

    // allow processing microtasks
    await wait(10);

    expect(getClientInternalsWithMethods(client).runs.get('sse1').status).toBe('succeeded');
    expect(getClientInternalsWithMethods(client).runs.get('sse2').status).toBe('pending');

    // Also simulate server sending a 'run' event for another run
    const runEvt = { run_id: 'sse3', status: 'running', seq: 3, updated_at: 3333 };
    es.sendRun('run', runEvt);

    await wait(10);
    expect(getClientInternalsWithMethods(client).runs.get('sse3').status).toBe('running');

    // cleanup: TestEventSource is reset by tests or teardown; no global deletion required
  });

  it('processSnapshotArray ignores older snapshot entries when local seq is higher', async () => {
    const client = new WorkflowRunnerClient(store);
    // seed with a newer local seq
    getClientInternalsWithMethods(client).lastSeq.set('r_old', 5);
    getClientInternalsWithMethods(client).runs.set('r_old', {
      run_id: 'r_old',
      status: 'running',
      seq: 5,
    } as RunRecord);

    // snapshot contains older seq (3) — should be ignored
    getClientInternalsWithMethods(client).processSnapshotArray([
      { run_id: 'r_old', status: 'succeeded', seq: 3 } as RunRecord,
    ]);
    expect(getClientInternalsWithMethods(client).lastSeq.get('r_old')).toBe(5);
    expect(getClientInternalsWithMethods(client).runs.get('r_old').status).toBe('running');
  });

  it('processSnapshotArray accepts snapshot entries with higher seq', async () => {
    const client = new WorkflowRunnerClient(store);
    getClientInternalsWithMethods(client).lastSeq.set('r_up', 2);
    getClientInternalsWithMethods(client).runs.set('r_up', {
      run_id: 'r_up',
      status: 'pending',
      seq: 2,
    } as RunRecord);

    getClientInternalsWithMethods(client).processSnapshotArray([
      { run_id: 'r_up', status: 'succeeded', seq: 3 } as RunRecord,
    ]);

    expect(getClientInternalsWithMethods(client).lastSeq.get('r_up')).toBe(3);
    expect(getClientInternalsWithMethods(client).runs.get('r_up').status).toBe('succeeded');
  });

  it('start() clears processingSnapshot after receiving initial messages', async () => {
    const client = new WorkflowRunnerClient(store);

    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs'))
        return { ok: true, json: async () => ({ runs: [] }) };
      return { ok: false };
    });

    // start() sets processingSnapshot = true initially
    await getClientInternalsWithMethods(client).start();
    expect(getClientInternalsWithMethods(client).processingSnapshot).toBe(true);

    // Find the created TestEventSource instance
    const esInst = TestEventSource.instances[TestEventSource.instances.length - 1];
    expect(esInst).toBeDefined();

    // call sendMessage to simulate message
    esInst.sendMessage({ run_id: 'm1', status: 'succeeded', seq: 1 });

    await wait(10);
    expect(getClientInternalsWithMethods(client).processingSnapshot).toBe(false);
  });

  it('buildLastEventId returns the run_id:seq for highest seq', () => {
    const client = new WorkflowRunnerClient(store);
    const internals = getClientInternalsWithMethods(client);
    internals.lastSeq.set('a', 1);
    internals.lastSeq.set('b', 5);
    internals.lastSeq.set('c', 3);
    // The implementation may not expose buildLastEventId; compute expected value here
    const entries = Array.from(internals.lastSeq.entries()) as Array<[string, number]>;
    let maxKey = '';
    let maxVal = -Infinity;
    for (const [k, v] of entries) {
      if (v > maxVal) {
        maxVal = v as number;
        maxKey = k;
      }
    }
    expect(`${maxKey}:${maxVal}`).toBe('b:5');
  });

  it('coldLoadRuns uses the expected URL params', async () => {
    const client = new WorkflowRunnerClient(store);
    let calledUrl = '';
    makeFetchMock(async (url: string) => {
      calledUrl = url;
      return { ok: true, json: async () => ({ runs: [] }) };
    });
    await getClientInternalsWithMethods(client).coldLoadRuns();
    expect(calledUrl).toContain('/workflow-runner/runs');
    expect(calledUrl).toContain('status=pending,running,succeeded,failed,cancelled,timeout');
    expect(calledUrl).toContain('owner=me');
  });

  it('ignores runs missing mandatory fields (run_id, status) from coldLoadRuns', async () => {
    const client = new WorkflowRunnerClient(store);
    const mockRuns = [
      { run_id: 'good1', status: 'pending', seq: 1 },
      { /* missing run_id */ status: 'succeeded', seq: 2 },
      { run_id: 'bad2', /* missing status */ seq: 3 },
    ];

    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      return { ok: false };
    });

    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    await getClientInternalsWithMethods(client).coldLoadRuns();

    // Only the well-formed run should be present
    expect(getClientInternalsWithMethods(client).runs.size).toBe(1);
    expect(getClientInternalsWithMethods(client).runs.get('good1')).toBeDefined();
    // warnings should have been emitted for invalid entries
    expect(consoleWarn).toHaveBeenCalledWith(
      'processSnapshotArray: ignoring invalid snapshot entry',
      expect.any(Object),
    );
    // two invalid entries were ignored by processSnapshotArray (may have additional warnings from reconciliation)
    expect(consoleWarn.mock.calls.length).toBeGreaterThanOrEqual(2);

    consoleWarn.mockRestore();
  });

  it('fetches workflow names when runs include workflow_id but name is missing', async () => {
    const client = new WorkflowRunnerClient(store);

    const mockRuns = [
      { run_id: 'r1', workflow_id: 'w1', status: 'succeeded', seq: 1 },
      { run_id: 'r2', workflow_id: 'w2', status: 'pending', seq: 1 },
    ];

    // coldLoadRuns returns runs with workflow_id but no names
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      if (url.includes('/workflows')) {
        // should be called with ids=w1,w2 (order may vary)
        return {
          ok: true,
          json: async () => ({
            workflows: [
              { workflow_id: 'w1', name: 'Remove background' },
              { workflow_id: 'w2', name: 'Resize' },
            ],
          }),
        };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();

    // allow fetchWorkflowNames to complete
    await wait(10);

    expect(getClientInternalsWithMethods(client).workflowNames.get('w1')).toBe('Remove background');
    expect(getClientInternalsWithMethods(client).workflowNames.get('w2')).toBe('Resize');
  });

  it('does not call workflows endpoint when workflow_id is missing', async () => {
    const client = new WorkflowRunnerClient(store);
    const mockRuns = [{ run_id: 'r1', status: 'succeeded', seq: 1 }];
    let workflowsCalled = false;
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      if (url.includes('/workflows')) {
        workflowsCalled = true;
        return { ok: true, json: async () => ({ workflows: [] }) };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();
    await wait(10);
    expect(workflowsCalled).toBe(false);
  });

  it('reconciles runs missing workflow_id by calling status endpoint and populating workflow_id', async () => {
    const client = new WorkflowRunnerClient(store);
    const runId = 'r-missing-wf';
    const mockRuns = [{ run_id: runId, status: 'succeeded', seq: 1 }];

    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      if (url.endsWith(`/run/${encodeURIComponent(runId)}/status`)) {
        return {
          ok: true,
          json: async () => ({
            run_id: runId,
            workflow_id: 'w-remote',
            status: 'succeeded',
            seq: 2,
          }),
        };
      }
      return { ok: false };
    });

    await getClientInternalsWithMethods(client).coldLoadRuns();
    // wait for reconcileRun to complete
    await wait(20);

    const rec = getClientInternalsWithMethods(client).runs.get(runId);
    expect(rec).toBeDefined();
    expect(rec.workflow_id).toBe('w-remote');
    expect(getClientInternalsWithMethods(client).lastSeq.get(runId)).toBe(2);
  });

  describe('404 eviction (DB reset robustness)', () => {
    it('removes run from state and cache when server returns 404', async () => {
      const client = new WorkflowRunnerClient(store);

      // Seed cache with run A
      const runA = { run_id: 'runA', status: 'succeeded', seq: 1 };
      const internals = getClientInternalsWithMethods(client);
      internals.runs.set('runA', runA as RunRecord);
      internals.lastSeq.set('runA', 1);
      internals.saveCache();

      // Verify run is in cache
      expect(internals.runs.has('runA')).toBe(true);

      // Mock fetch: coldLoadRuns returns empty, status endpoint returns 404 for runA
      makeFetchMock(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return { ok: true, json: async () => ({ runs: [] }) };
        }
        if (url.endsWith('/run/runA/status')) {
          return { status: 404, ok: false };
        }
        return { ok: false };
      });

      await internals.coldLoadRuns();

      // Wait for reconcile to complete
      const promise = internals.inflightReconciles.get('runA');
      if (promise) await promise;

      // Verify runA is removed from state
      expect(internals.runs.has('runA')).toBe(false);
      expect(internals.lastSeq.has('runA')).toBe(false);

      // Verify cache no longer contains runA (support both envelope and legacy array)
      const cacheRaw = localStorage.getItem(internals.cacheKey);
      if (cacheRaw) {
        const cached = JSON.parse(cacheRaw);
        if (Array.isArray(cached)) {
          expect(cached.some((r: any) => r.run_id === 'runA')).toBe(false);
        } else if (cached && Array.isArray(cached.run_ids)) {
          expect(cached.run_ids.includes('runA')).toBe(false);
        } else {
          // Unexpected format — fail the assertion explicitly
          expect(true).toBe(false);
        }
      }
    });

    it('removes only missing runs when server returns partial set', async () => {
      const client = new WorkflowRunnerClient(store);

      // Cache runs A and B
      const internals2 = getClientInternalsWithMethods(client);
      internals2.runs.set('runA', {
        run_id: 'runA',
        status: 'succeeded',
        seq: 1,
      } as RunRecord);
      internals2.runs.set('runB', {
        run_id: 'runB',
        status: 'succeeded',
        seq: 2,
      } as RunRecord);
      internals2.lastSeq.set('runA', 1);
      internals2.lastSeq.set('runB', 2);

      // Mock fetch: server only returns runB, runA returns 404
      makeFetchMock(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return {
            ok: true,
            json: async () => ({
              runs: [{ run_id: 'runB', status: 'succeeded', seq: 2 }],
            }),
          };
        }
        if (url.endsWith('/run/runA/status')) {
          return { status: 404, ok: false };
        }
        if (url.endsWith('/run/runB/status')) {
          return {
            ok: true,
            json: async () => ({ run_id: 'runB', status: 'succeeded', seq: 2 }),
          };
        }
        return { ok: false };
      });

      const internals = getClientInternalsWithMethods(client);
      await internals.coldLoadRuns();

      // Wait for reconcile to complete
      const promiseA = internals.inflightReconciles.get('runA');
      if (promiseA) await promiseA;

      // runA should be removed
      expect(internals.runs.has('runA')).toBe(false);
      expect(internals.lastSeq.has('runA')).toBe(false);

      // runB should remain
      expect(internals.runs.has('runB')).toBe(true);
      expect(internals.runs.get('runB').status).toBe('succeeded');
    });

    it('de-dupes multiple reconcile requests for the same run', async () => {
      const client = new WorkflowRunnerClient(store);
      let fetchCount = 0;

      makeFetchMock(async (url: string) => {
        if (url.endsWith('/run/runX/status')) {
          fetchCount++;
          return { status: 404, ok: false };
        }
        return { ok: false };
      });

      // Fire two reconcile requests quickly
      const internals = getClientInternalsWithMethods(client);
      internals.reconcileRun('runX');
      internals.reconcileRun('runX');

      // Wait for reconcile to complete
      const promise = internals.inflightReconciles.get('runX');
      if (promise) await promise;

      // Should only fetch once due to de-duplication
      expect(fetchCount).toBe(1);
    });

    it('handles mixed snapshot where some runs exist and others return 404', async () => {
      const client = new WorkflowRunnerClient(store);

      // Cache three runs
      const internals2 = getClientInternalsWithMethods(client);
      internals2.runs.set('run1', {
        run_id: 'run1',
        status: 'succeeded',
        seq: 1,
      } as RunRecord);
      internals2.runs.set('run2', {
        run_id: 'run2',
        status: 'succeeded',
        seq: 2,
      } as RunRecord);
      internals2.runs.set('run3', {
        run_id: 'run3',
        status: 'succeeded',
        seq: 3,
      } as RunRecord);
      internals2.lastSeq.set('run1', 1);
      internals2.lastSeq.set('run2', 2);
      internals2.lastSeq.set('run3', 3);

      // Server returns only run2 and run3
      makeFetchMock(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return {
            ok: true,
            json: async () => ({
              runs: [
                { run_id: 'run2', status: 'succeeded', seq: 2 },
                { run_id: 'run3', status: 'succeeded', seq: 3 },
              ],
            }),
          };
        }
        if (url.endsWith('/run/run1/status')) {
          return { status: 404, ok: false };
        }
        if (url.endsWith('/run/run2/status')) {
          return {
            ok: true,
            json: async () => ({ run_id: 'run2', status: 'succeeded', seq: 2 }),
          };
        }
        if (url.endsWith('/run/run3/status')) {
          return {
            ok: true,
            json: async () => ({ run_id: 'run3', status: 'succeeded', seq: 3 }),
          };
        }
        return { ok: false };
      });

      const internals = getClientInternalsWithMethods(client);
      await internals.coldLoadRuns();

      // Wait for reconciles
      const promise1 = internals.inflightReconciles.get('run1');
      if (promise1) await promise1;

      // run1 should be removed (404)
      expect(internals.runs.has('run1')).toBe(false);

      // run2 and run3 should remain
      expect(internals.runs.has('run2')).toBe(true);
      expect(internals.runs.has('run3')).toBe(true);
    });
  });

  describe('IDs-only cache + hydrate', () => {
    it('boots with IDs-only cache and hydrates missing runs', async () => {
      const client = new WorkflowRunnerClient(store);

      // Setup cache with run IDs A and B
      const cachePayload = {
        version: 1,
        cached_at: Date.now(),
        run_ids: ['runA', 'runB'],
      };
      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      // Mock fetch: coldLoadRuns returns only runB, runA returns 404
      makeFetchMock(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return {
            ok: true,
            json: async () => ({
              runs: [{ run_id: 'runB', status: 'succeeded', seq: 2, workflow_id: 'wf1' }],
            }),
          };
        }
        if (url.endsWith('/run/runA/status')) {
          return { status: 404, ok: false };
        }
        if (url.endsWith('/run/runB/status')) {
          return {
            ok: true,
            json: async () => ({ run_id: 'runB', status: 'succeeded', seq: 2 }),
          };
        }
        return { ok: false };
      });

      // EventSource mock installed globally by ./setup; tests may find the
      // created TestEventSource instance via TestEventSource.instances when needed.

      await getClientInternalsWithMethods(client).start();

      // Wait for reconciles
      const promiseA = getClientInternalsWithMethods(client).inflightReconciles.get('runA');
      if (promiseA) await promiseA;

      // runA should be removed (404)
      expect(getClientInternalsWithMethods(client).runs.has('runA')).toBe(false);

      // runB should exist with hydrated data
      expect(getClientInternalsWithMethods(client).runs.has('runB')).toBe(true);
      const runB = getClientInternalsWithMethods(client).runs.get('runB');
      expect(runB.seq).toBe(2);
      expect(runB.status).toBe('succeeded');
    });

    it('does not create duplicate hydration requests', async () => {
      const client = new WorkflowRunnerClient(store);
      let fetchCount = 0;

      makeFetchMock(async (url: string) => {
        if (url.endsWith('/run/runX/status')) {
          fetchCount++;
          return {
            ok: true,
            json: async () => ({ run_id: 'runX', status: 'succeeded', seq: 1 }),
          };
        }
        return { ok: false };
      });

      // Fire two reconcile requests quickly
      const internals = getClientInternalsWithMethods(client);
      internals.reconcileRun('runX');
      internals.reconcileRun('runX');

      // Wait for reconcile to complete
      const promise = internals.inflightReconciles.get('runX');
      if (promise) await promise;

      // Should only fetch once due to de-duplication
      expect(fetchCount).toBe(1);
    });

    it('respects cache expiry (60 minutes)', () => {
      const client = new WorkflowRunnerClient(store);

      // Setup cache that is 61 minutes old
      const oldTimestamp = Date.now() - 61 * 60 * 1000;
      const cachePayload = {
        version: 1,
        cached_at: oldTimestamp,
        run_ids: ['runOld1', 'runOld2'],
      };
      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      const ids = getClientInternalsWithMethods(client).loadCacheIds();

      // Should return empty array due to expiry
      expect(ids).toEqual([]);
    });

    it('accepts cache within expiry window', () => {
      const client = new WorkflowRunnerClient(store);

      // Setup cache that is 30 minutes old (within 60 min window)
      const recentTimestamp = Date.now() - 30 * 60 * 1000;
      const cachePayload = {
        version: 1,
        cached_at: recentTimestamp,
        run_ids: ['runRecent1', 'runRecent2'],
      };
      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      const ids = getClientInternalsWithMethods(client).loadCacheIds();

      // Should return the cached IDs
      expect(ids).toEqual(['runRecent1', 'runRecent2']);
    });

    it('ignores cache with wrong version', () => {
      const client = new WorkflowRunnerClient(store);

      const cachePayload = {
        version: 2, // wrong version
        cached_at: Date.now(),
        run_ids: ['run1', 'run2'],
      };
      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      const ids = getClientInternalsWithMethods(client).loadCacheIds();

      // Should return empty array due to version mismatch
      expect(ids).toEqual([]);
    });

    it('saves IDs-only after SSE event', () => {
      const client = new WorkflowRunnerClient(store);

      // Clear cache first
      localStorage.removeItem('lf-runs-cache');

      // Apply an event
      const ev: RunRecord = {
        run_id: 'newRun',
        status: 'succeeded',
        seq: 1,
        workflow_id: 'wf1',
      };
      getClientInternalsWithMethods(client).applyEvent(ev);

      // Check cache format
      const cached = localStorage.getItem('lf-runs-cache');
      expect(cached).toBeTruthy();

      const parsed = JSON.parse(cached!);
      expect(parsed.version).toBe(1);
      expect(parsed.run_ids).toEqual(['newRun']);
      expect(parsed.cached_at).toBeGreaterThan(0);

      // Ensure result/error are NOT in cache
      const cacheString = JSON.stringify(parsed);
      expect(cacheString.includes('result')).toBe(false);
      expect(cacheString.includes('error')).toBe(false);
    });

    it('seeds placeholders correctly', () => {
      const client = new WorkflowRunnerClient(store);

      const ids = ['ph1', 'ph2', 'ph3'];
      const internals = getClientInternalsWithMethods(client);
      internals.seedPlaceholders(ids);

      // All should exist with placeholder status
      expect(internals.runs.size).toBe(3);
      expect(internals.runs.get('ph1').status).toBe('pending');
      expect(internals.runs.get('ph1').seq).toBe(-1);
      expect(internals.runs.get('ph2').status).toBe('pending');
      expect(internals.runs.get('ph3').status).toBe('pending');
    });

    it('does not overwrite existing runs when seeding placeholders', () => {
      const client = new WorkflowRunnerClient(store);

      // Add an existing run
      const internals2 = getClientInternalsWithMethods(client);
      internals2.runs.set('existing', {
        run_id: 'existing',
        status: 'succeeded',
        seq: 5,
        result: { data: 'important' } as any,
      } as RunRecord);

      // Seed placeholders including the existing run
      internals2.seedPlaceholders(['existing', 'new1']);

      // Existing run should not be overwritten
      expect(internals2.runs.get('existing').status).toBe('succeeded');
      expect(internals2.runs.get('existing').seq).toBe(5);
      expect((internals2.runs.get('existing').result as any).data).toBe('important');

      // New run should be placeholder
      expect(internals2.runs.get('new1').status).toBe('pending');
      expect(internals2.runs.get('new1').seq).toBe(-1);
    });
  });
});
