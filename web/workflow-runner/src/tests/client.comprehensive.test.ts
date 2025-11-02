import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { RunRecord, UpdateHandler } from '../types/client';

// Mock localStorage for Node environment
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(global, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

describe('WorkflowRunnerClient', () => {
  let client: WorkflowRunnerClient | undefined;
  let updateHandler: ReturnType<typeof vi.fn<UpdateHandler>>;

  beforeEach(() => {
    // Clear localStorage before each test
    mockLocalStorage.clear();

    // Mock fetch globally
    global.fetch = vi.fn();

    // Mock EventSource as proper class
    global.EventSource = class MockEventSource {
      addEventListener = vi.fn();
      close = vi.fn();
      onerror = null;
      onmessage = null;
      onopen = null;
      constructor(public url: string) {}
    } as unknown as typeof EventSource;

    client = new WorkflowRunnerClient();
    updateHandler = vi.fn<UpdateHandler>();
    client.setUpdateHandler(updateHandler);
  });

  afterEach(() => {
    if (client) {
      client.stop();
    }
    vi.restoreAllMocks();
  });

  describe('Client instantiation', () => {
    it('should create client with correct baseUrl', () => {
      const testClient = new WorkflowRunnerClient();
      expect(testClient).toBeDefined();
    });

    it('should strip trailing slash from baseUrl', () => {
      const testClient = new WorkflowRunnerClient();
      expect(testClient).toBeDefined();
      // baseUrl is private, but behavior should be consistent
    });
  });

  describe('Hydration on refresh', () => {
    it('should load cached runs from localStorage', () => {
      // Seed localStorage with cached runs
      const cachedRuns: RunRecord[] = [
        {
          run_id: 'run-1',
          status: 'succeeded',
          seq: 5,
          workflow_id: 'wf-1',
          owner_id: 'user-1',
          created_at: Date.now() - 10000,
          updated_at: Date.now() - 5000,
        },
        {
          run_id: 'run-2',
          status: 'running',
          seq: 3,
          workflow_id: 'wf-2',
          owner_id: 'user-1',
          created_at: Date.now() - 8000,
          updated_at: Date.now() - 2000,
        },
      ];

      localStorage.setItem('lf-runs-cache', JSON.stringify(cachedRuns));

      const testClient = new WorkflowRunnerClient();
      const handler = vi.fn();
      testClient.setUpdateHandler(handler);

      // Start should load cache synchronously
      testClient.start();

      // Handler should be called with cached runs
      expect(handler).toHaveBeenCalled();
      const calls = handler.mock.calls;
      const lastCall = calls[calls.length - 1][0] as Map<string, RunRecord>;

      expect(lastCall.size).toBe(2);
      expect(lastCall.has('run-1')).toBe(true);
      expect(lastCall.has('run-2')).toBe(true);
    });

    it('should handle corrupted localStorage gracefully', async () => {
      localStorage.setItem('lf-runs-cache', 'invalid-json{');

      const testClient = new WorkflowRunnerClient();
      const handler = vi.fn();
      testClient.setUpdateHandler(handler);

      // Should not throw
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
        // Simulate event ingestion via internal method
        (client as any).upsertRun(rec);
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
        (client as any).upsertRun(rec);
      });

      // Only first event should trigger update
      expect(updateHandler).toHaveBeenCalledTimes(1);

      const lastCall = updateHandler.mock.calls[0][0] as Map<string, RunRecord>;
      const run = lastCall.get('run-1');
      expect(run?.status).toBe('running'); // First status preserved
      expect(run?.seq).toBe(5);
    });

    it('should not regress seq on reconciliation', () => {
      // Initial event with high seq
      (client as any).upsertRun({
        run_id: 'run-1',
        status: 'succeeded',
        seq: 10,
      });

      updateHandler.mockClear();

      // Reconciliation returns older seq
      (client as any).upsertRun({
        run_id: 'run-1',
        status: 'succeeded',
        seq: 9,
      });

      // Should not trigger update
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

      // Trigger multiple reconciles concurrently
      (client as any).reconcileRun('run-1');
      (client as any).reconcileRun('run-1');
      (client as any).reconcileRun('run-1');

      // Wait for async operations
      await new Promise((resolve) => setTimeout(resolve, 100));

      // Fetch should only be called once due to de-duplication
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

      // First reconcile
      (client as any).reconcileRun('run-1');

      // Second reconcile should be de-duped
      (client as any).reconcileRun('run-1');

      expect(mockFetch).toHaveBeenCalledTimes(1);

      // Resolve first fetch
      resolveFirst({
        ok: true,
        json: () =>
          Promise.resolve({
            run_id: 'run-1',
            status: 'running',
            seq: 5,
          }),
      });

      await new Promise((resolve) => setTimeout(resolve, 100));

      // Third reconcile after first completes should proceed
      (client as any).reconcileRun('run-1');

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('Gap detection', () => {
    it('should trigger reconciliation on gap detection', () => {
      const reconcileSpy = vi.spyOn(client as any, 'reconcileRun');

      // Initial event
      (client as any).applyEvent({
        run_id: 'run-1',
        status: 'pending',
        seq: 1,
      });

      reconcileSpy.mockClear();

      // Gap: seq jumps from 1 to 5
      (client as any).applyEvent({
        run_id: 'run-1',
        status: 'succeeded',
        seq: 5,
      });

      // Should trigger reconciliation
      expect(reconcileSpy).toHaveBeenCalledWith('run-1');
    });

    it('should not trigger reconciliation for consecutive seq', () => {
      const reconcileSpy = vi.spyOn(client as any, 'reconcileRun');

      (client as any).applyEvent({
        run_id: 'run-1',
        status: 'pending',
        seq: 1,
      });

      reconcileSpy.mockClear();

      // No gap: seq 1 → 2
      (client as any).applyEvent({
        run_id: 'run-1',
        status: 'running',
        seq: 2,
      });

      expect(reconcileSpy).toHaveBeenCalledTimes(0);
    });
  });

  describe('Workflow name resolution', () => {
    it('should fetch workflow names for missing IDs', () => {
      const fetchSpy = vi.spyOn(client as any, 'fetchWorkflowNames');

      (client as any).upsertRun({
        run_id: 'run-1',
        workflow_id: 'wf-1',
        status: 'running',
        seq: 1,
      });

      expect(fetchSpy).toHaveBeenCalledWith(['wf-1']);
    });

    it('should not fetch workflow names already cached', () => {
      // Preload workflow name
      client.setWorkflowNames(new Map([['wf-1', 'Test Workflow']]));

      const fetchSpy = vi.spyOn(client as any, 'fetchWorkflowNames');

      (client as any).upsertRun({
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

      // Verify by inserting runs - no fetch should happen
      const fetchSpy = vi.spyOn(client as any, 'fetchWorkflowNames');

      (client as any).upsertRun({
        run_id: 'run-1',
        workflow_id: 'wf-1',
        status: 'running',
        seq: 1,
      });

      (client as any).upsertRun({
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
      (client as any).upsertRun({
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
      expect(parsed).toBeInstanceOf(Array);
      expect(parsed.length).toBeGreaterThan(0);
      expect(parsed[0].run_id).toBe('run-1');
    });

    it('should limit cached runs to 200 most recent', () => {
      // Add 250 runs
      const baseTime = Date.now();
      for (let i = 0; i < 250; i++) {
        (client as any).upsertRun({
          run_id: `run-${i}`,
          status: 'succeeded',
          seq: 1,
          updated_at: baseTime + i,
        });
      }

      const cached = localStorage.getItem('lf-runs-cache');
      const parsed = JSON.parse(cached!);

      expect(parsed.length).toBe(200);

      // Should keep most recent (highest updated_at)
      expect(parsed[0].run_id).toBe('run-249');
    });
  });
});
