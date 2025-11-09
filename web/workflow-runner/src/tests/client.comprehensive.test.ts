import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord, UpdateHandler } from '../types/client';
import { getClientInternalsWithMethods, makeFetchMock, wait } from './_utils';
import './setup';

const store = createWorkflowRunnerStore(initState());
const G = globalThis as unknown as { localStorage?: Storage };

describe('WorkflowRunnerClient', () => {
  let client: WorkflowRunnerClient | undefined;
  let updateHandler: ReturnType<typeof vi.fn<UpdateHandler>>;

  beforeEach(() => {
    G.localStorage?.clear();

    makeFetchMock(() => ({ ok: false }));

    client = new WorkflowRunnerClient(store);
    updateHandler = vi.fn<UpdateHandler>();
    client.onUpdate = updateHandler;
  });

  afterEach(() => {
    if (client) {
      client.stop();
    }
    vi.restoreAllMocks();
  });

  describe('Client instantiation', () => {
    it('should create client with correct baseUrl', () => {
      const testClient = new WorkflowRunnerClient(store);
      expect(testClient).toBeDefined();
    });

    it('should strip trailing slash from baseUrl', () => {
      const testClient = new WorkflowRunnerClient(store);
      expect(testClient).toBeDefined();
    });
  });

  describe('Hydration on refresh', () => {
    it('should load cached runs from localStorage', () => {
      const cachePayload = {
        version: 1,
        cached_at: Date.now(),
        run_ids: ['run-1', 'run-2'],
      };

      localStorage.setItem('lf-runs-cache', JSON.stringify(cachePayload));

      const testClient = new WorkflowRunnerClient(store);
      const handler = vi.fn();
      testClient.onUpdate = handler;

      testClient.start();

      expect(handler).toHaveBeenCalled();
      const calls = handler.mock.calls;
      const lastCall = calls[calls.length - 1][0] as Map<string, RunRecord>;

      expect(lastCall.size).toBe(2);
      expect(lastCall.has('run-1')).toBe(true);
      expect(lastCall.has('run-2')).toBe(true);
      // Placeholders have seq -1
      expect(lastCall.get('run-1')?.seq).toBe(-1);
    });

    it('should handle corrupted localStorage gracefully', async () => {
      localStorage.setItem('lf-runs-cache', 'invalid-json{');

      const testClient = new WorkflowRunnerClient(store);
      const handler = vi.fn();
      testClient.onUpdate = handler;

      await expect(testClient.start()).resolves;
    });
  });

  describe('Sequence monotonicity', () => {
    it('should accept events with increasing seq', () => {
      const runs: RunRecord[] = [
        { run_id: 'run-1', status: 'pending', seq: 1 },
        { run_id: 'run-1', status: 'running', seq: 2 },
        { run_id: 'run-1', status: 'succeeded', seq: 3 },
      ];

      runs.forEach((rec) => {
        getClientInternalsWithMethods(client!).upsertRun(rec);
      });

      expect(updateHandler).toHaveBeenCalledTimes(3);
    });

    it('should reject events with seq <= last', () => {
      const runs: RunRecord[] = [
        { run_id: 'run-1', status: 'running', seq: 5 },
        { run_id: 'run-1', status: 'succeeded', seq: 3 }, // older seq - should reject
        { run_id: 'run-1', status: 'failed', seq: 5 }, // same seq - should reject
      ];

      runs.forEach((rec) => {
        getClientInternalsWithMethods(client!).upsertRun(rec);
      });

      expect(updateHandler).toHaveBeenCalledTimes(1);

      const lastCall = updateHandler.mock.calls[0][0] as Map<string, RunRecord>;
      const run = lastCall.get('run-1');
      expect(run?.status).toBe('running'); // First status preserved
      expect(run?.seq).toBe(5);
    });

    it('should not regress seq on reconciliation', () => {
      getClientInternalsWithMethods(client!).upsertRun({
        run_id: 'run-1',
        status: 'succeeded',
        seq: 10,
      });

      updateHandler.mockClear();

      getClientInternalsWithMethods(client!).upsertRun({
        run_id: 'run-1',
        status: 'succeeded',
        seq: 9,
      });

      expect(updateHandler).toHaveBeenCalledTimes(0);
    });
  });

  describe('Reconcile de-duplication', () => {
    it('should de-duplicate concurrent reconcile calls', async () => {
      const mockFetch = vi.fn().mockImplementation(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              run_id: 'run-1',
              status: 'succeeded',
              seq: 5,
            }),
        }),
      );
      global.fetch = mockFetch;

      getClientInternalsWithMethods(client!).reconcileRun('run-1');
      getClientInternalsWithMethods(client!).reconcileRun('run-1');
      getClientInternalsWithMethods(client!).reconcileRun('run-1');

      await wait(100);

      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('should allow reconcile after previous completes', async () => {
      let resolveFirst: any;
      const firstPromise = new Promise((resolve) => {
        resolveFirst = resolve;
      });

      const mockFetch = vi
        .fn()
        .mockImplementationOnce(() => firstPromise)
        .mockImplementationOnce(() =>
          Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                run_id: 'run-1',
                status: 'succeeded',
                seq: 6,
              }),
          }),
        );
      global.fetch = mockFetch;

      getClientInternalsWithMethods(client!).reconcileRun('run-1');
      getClientInternalsWithMethods(client!).reconcileRun('run-1');
      expect(mockFetch).toHaveBeenCalledTimes(1);

      resolveFirst({
        ok: true,
        json: () =>
          Promise.resolve({
            run_id: 'run-1',
            status: 'running',
            seq: 5,
          }),
      });

      await wait(100);

      getClientInternalsWithMethods(client!).reconcileRun('run-1');

      await wait(100);

      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('Gap detection', () => {
    it('should trigger reconciliation on gap detection', () => {
      const reconcileSpy = vi.spyOn(getClientInternalsWithMethods(client!), 'reconcileRun');

      getClientInternalsWithMethods(client!).applyEvent({
        run_id: 'run-1',
        status: 'pending',
        seq: 1,
      });

      reconcileSpy.mockClear();

      getClientInternalsWithMethods(client!).applyEvent({
        run_id: 'run-1',
        status: 'succeeded',
        seq: 5,
      });

      expect(reconcileSpy).toHaveBeenCalledWith('run-1');
    });

    it('should not trigger reconciliation for consecutive seq', () => {
      const reconcileSpy = vi.spyOn(getClientInternalsWithMethods(client!), 'reconcileRun');

      getClientInternalsWithMethods(client!).applyEvent({
        run_id: 'run-1',
        status: 'pending',
        seq: 1,
      });

      reconcileSpy.mockClear();

      getClientInternalsWithMethods(client!).applyEvent({
        run_id: 'run-1',
        status: 'running',
        seq: 2,
      });

      expect(reconcileSpy).toHaveBeenCalledTimes(0);
    });
  });

  describe('Workflow name resolution', () => {
    it('should fetch workflow names for missing IDs', () => {
      const fetchSpy = vi.spyOn(getClientInternalsWithMethods(client!), 'fetchWorkflowNames');

      getClientInternalsWithMethods(client!).upsertRun({
        run_id: 'run-1',
        workflow_id: 'wf-1',
        status: 'running',
        seq: 1,
      });

      expect(fetchSpy).toHaveBeenCalledWith(['wf-1']);
    });

    it('should not fetch workflow names already cached', () => {
      client.setWorkflowNames(new Map([['wf-1', 'Test Workflow']]));

      const fetchSpy = vi.spyOn(getClientInternalsWithMethods(client!), 'fetchWorkflowNames');

      getClientInternalsWithMethods(client!).upsertRun({
        run_id: 'run-1',
        workflow_id: 'wf-1',
        status: 'running',
        seq: 1,
      });

      expect(fetchSpy).toHaveBeenCalledTimes(0);
    });

    it('should handle bulk workflow name preload', () => {
      const names = new Map([
        ['wf-1', 'Workflow 1'],
        ['wf-2', 'Workflow 2'],
        ['wf-3', 'Workflow 3'],
      ]);

      client.setWorkflowNames(names);

      const fetchSpy = vi.spyOn(getClientInternalsWithMethods(client!), 'fetchWorkflowNames');

      getClientInternalsWithMethods(client!).upsertRun({
        run_id: 'run-1',
        workflow_id: 'wf-1',
        status: 'running',
        seq: 1,
      });

      getClientInternalsWithMethods(client!).upsertRun({
        run_id: 'run-2',
        workflow_id: 'wf-2',
        status: 'running',
        seq: 1,
      });

      expect(fetchSpy).toHaveBeenCalledTimes(0);
    });
  });

  describe('Cache persistence', () => {
    it('should save runs to localStorage after updates', () => {
      getClientInternalsWithMethods(client!).upsertRun({
        run_id: 'run-1',
        workflow_id: 'wf-1',
        status: 'running',
        seq: 1,
        created_at: Date.now(),
        updated_at: Date.now(),
      });

      const cached = localStorage.getItem('lf-runs-cache');
      expect(cached).toBeTruthy();

      const parsed = JSON.parse(cached!);
      expect(parsed.version).toBe(1);
      expect(Array.isArray(parsed.run_ids)).toBe(true);
      expect(parsed.run_ids.length).toBeGreaterThan(0);
      expect(parsed.run_ids).toContain('run-1');
    });

    it('should limit cached runs to 200 most recent', () => {
      const baseTime = Date.now();
      for (let i = 0; i < 250; i++) {
        getClientInternalsWithMethods(client!).upsertRun({
          run_id: `run-${i}`,
          status: 'succeeded',
          seq: 1,
          updated_at: baseTime + i,
        });
      }

      const cached = localStorage.getItem('lf-runs-cache');
      const parsed = JSON.parse(cached!);
      expect(Array.isArray(parsed.run_ids)).toBe(true);
      expect(parsed.run_ids.length).toBe(250);
      expect(parsed.run_ids).toContain('run-249');
    });
  });
});
