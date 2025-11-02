import { describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord } from '../types/client';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient (compat tests)', () => {
  it('ignores duplicate events', () => {
    const client = new WorkflowRunnerClient(store);
    const ev: RunRecord = { run_id: 'r1', status: 'pending', seq: 1 };
    (client as any).applyEvent(ev);
    (client as any).applyEvent(ev);
    expect((client as any).runs.size).toBe(1);
    expect((client as any).lastSeq.get('r1')).toBe(1);
  });

  it('triggers reconcile on gap detection', async () => {
    const client = new WorkflowRunnerClient(store);
    (client as any).lastSeq.set('r2', 1);
    let reconciled = false;
    (client as any).reconcileRun = async (_run_id: string) => {
      reconciled = true;
    };
    const ev: RunRecord = { run_id: 'r2', status: 'running', seq: 4 };
    (client as any).applyEvent(ev);
    await new Promise((r) => setTimeout(r, 10));
    expect(reconciled).toBe(true);
  });

  it('reconcileRun updates state', async () => {
    const client = new WorkflowRunnerClient(store);
    (global as any).fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({ run_id: 'r3', status: 'succeeded', seq: 5, result: { ok: true } }),
    }));
    (client as any).reconcileRun('r3');
    // Wait for the inflight promise to complete
    const promise = (client as any).inflightReconciles.get('r3');
    if (promise) await promise;
    expect((client as any).runs.get('r3').status).toBe('succeeded');
    expect((client as any).lastSeq.get('r3')).toBe(5);
  });

  it('polling merges snapshot', async () => {
    const client = new WorkflowRunnerClient(store);
    (global as any).fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({ runs: [{ run_id: 'r4', status: 'pending', seq: 2 }] }),
    }));
    await (client as any).pollActiveRuns();
    expect((client as any).runs.get('r4').status).toBe('pending');
    expect((client as any).lastSeq.get('r4')).toBe(2);
  });

  it('aborts in-flight polling on stop', async () => {
    const client = new WorkflowRunnerClient(store);
    let fetchCalled = false;
    (global as any).fetch = vi.fn((_url: string, opts?: any) => {
      fetchCalled = true;
      const signal: AbortSignal | undefined = opts && opts.signal;
      return new Promise((_resolve, reject) => {
        if (signal && signal.aborted) return reject(new DOMException('Aborted', 'AbortError'));
        const onAbort = () => reject(new DOMException('Aborted', 'AbortError'));
        signal && signal.addEventListener('abort', onAbort);
      });
    });
    const p = (client as any).pollActiveRuns();
    await new Promise((r) => setTimeout(r, 5));
    client.stop();
    try {
      await p;
    } catch {}
    expect(fetchCalled).toBe(true);
  });

  it('reconciles runs missing from snapshot on reconnect', async () => {
    const client = new WorkflowRunnerClient(store);
    // seed client with a run that was previously running
    (client as any).runs.set('rx', { run_id: 'rx', status: 'running', seq: 2 });
    (client as any).lastSeq.set('rx', 2);

    // mock fetch so that reconcileRun returns a terminal state
    (global as any).fetch = vi.fn(async (url: string) => {
      if (url.endsWith('/run/rx/status')) {
        return {
          ok: true,
          json: async () => ({ run_id: 'rx', status: 'succeeded', seq: 3, result: { ok: true } }),
        };
      }
      // default snapshot (empty) for pollActiveRuns
      return { ok: true, json: async () => ({ runs: [] }) };
    });

    // process an empty snapshot (simulating reconnect snapshot that omits 'rx')
    await (client as any).processSnapshotArray([]);

    // allow reconcileRun to complete
    await new Promise((r) => setTimeout(r, 10));

    expect((client as any).runs.get('rx').status).toBe('succeeded');
    expect((client as any).lastSeq.get('rx')).toBe(3);
  });

  it('coldLoadRuns fetches and merges runs before SSE starts', async () => {
    const client = new WorkflowRunnerClient(store);
    const mockRuns = [
      { run_id: 'cold1', status: 'pending', seq: 1, created_at: 1000 },
      { run_id: 'cold2', status: 'running', seq: 2, created_at: 2000 },
      { run_id: 'cold3', status: 'succeeded', seq: 5, created_at: 3000, result: { ok: true } },
    ];

    (global as any).fetch = vi.fn(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return {
          ok: true,
          json: async () => ({ runs: mockRuns }),
        };
      }
      return { ok: false };
    });

    await (client as any).coldLoadRuns();

    expect((client as any).runs.size).toBe(3);
    expect((client as any).runs.get('cold1').status).toBe('pending');
    expect((client as any).runs.get('cold2').status).toBe('running');
    expect((client as any).runs.get('cold3').status).toBe('succeeded');
    expect((client as any).lastSeq.get('cold3')).toBe(5);
  });

  it('coldLoadRuns handles fetch errors gracefully', async () => {
    const client = new WorkflowRunnerClient(store);
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    (global as any).fetch = vi.fn(async () => {
      throw new Error('Network error');
    });

    await (client as any).coldLoadRuns();

    expect((client as any).runs.size).toBe(0);
    expect(consoleWarn).toHaveBeenCalledWith('coldLoadRuns error', expect.any(Error));
    consoleWarn.mockRestore();
  });

  it('saveCache stores runs to localStorage', () => {
    const client = new WorkflowRunnerClient(store);
    (client as any).runs.set('cache1', {
      run_id: 'cache1',
      status: 'running',
      seq: 10,
      updated_at: 5000,
    });
    (client as any).runs.set('cache2', {
      run_id: 'cache2',
      status: 'succeeded',
      seq: 20,
      updated_at: 6000,
    });

    const mockLocalStorage: any = {};
    (global as any).localStorage = {
      setItem: vi.fn((key: string, value: string) => {
        mockLocalStorage[key] = value;
      }),
      getItem: vi.fn((key: string) => mockLocalStorage[key] || null),
      removeItem: vi.fn((key: string) => {
        delete mockLocalStorage[key];
      }),
    };

    (client as any).saveCache();

    expect(localStorage.setItem).toHaveBeenCalledWith('lf-runs-cache', expect.any(String));
    const cached = JSON.parse(mockLocalStorage['lf-runs-cache']);
    expect(cached).toBeInstanceOf(Array);
    expect(cached.length).toBe(2);
    expect(cached.find((r: any) => r.run_id === 'cache1')).toBeDefined();
    expect(cached.find((r: any) => r.run_id === 'cache2')).toBeDefined();
  });

  it('loadCache restores runs from localStorage', () => {
    const client = new WorkflowRunnerClient(store);
    const cachedRuns = [
      { run_id: 'restore1', status: 'pending', seq: 3, updated_at: 7000 },
      { run_id: 'restore2', status: 'running', seq: 4, updated_at: 8000 },
    ];

    const mockLocalStorage: any = {
      'lf-runs-cache': JSON.stringify(cachedRuns),
    };

    (global as any).localStorage = {
      setItem: vi.fn((key: string, value: string) => {
        mockLocalStorage[key] = value;
      }),
      getItem: vi.fn((key: string) => mockLocalStorage[key] || null),
      removeItem: vi.fn((key: string) => {
        delete mockLocalStorage[key];
      }),
    };

    (client as any).loadCache();

    expect((client as any).runs.size).toBe(2);
    expect((client as any).runs.get('restore1').status).toBe('pending');
    expect((client as any).runs.get('restore2').status).toBe('running');
    expect((client as any).lastSeq.get('restore1')).toBe(3);
    expect((client as any).lastSeq.get('restore2')).toBe(4);
  });

  it('loadCache handles missing or invalid cache gracefully', () => {
    const client = new WorkflowRunnerClient(store);
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    (global as any).localStorage = {
      setItem: vi.fn(),
      getItem: vi.fn(() => null),
      removeItem: vi.fn(),
    };

    (client as any).loadCache();
    expect((client as any).runs.size).toBe(0);

    // test invalid JSON
    (global as any).localStorage.getItem = vi.fn(() => '{invalid json}');
    (client as any).loadCache();
    expect(consoleWarn).toHaveBeenCalled();

    consoleWarn.mockRestore();
  });

  it('prevents duplicate runs when cache + coldLoad + SSE overlap', async () => {
    const client = new WorkflowRunnerClient(store);

    // Cached run from localStorage (seq=1)
    const cachedRuns = [{ run_id: 'dup1', status: 'pending', seq: 1, updated_at: 1000 }];
    (global as any).localStorage = {
      setItem: vi.fn(),
      getItem: vi.fn(() => JSON.stringify(cachedRuns)),
      removeItem: vi.fn(),
    };

    // Load from cache first
    (client as any).loadCache();
    expect((client as any).runs.size).toBe(1);
    expect((client as any).lastSeq.get('dup1')).toBe(1);

    // Server returns updated version (seq=3)
    const serverRuns = [{ run_id: 'dup1', status: 'running', seq: 3, updated_at: 2000 }];
    (global as any).fetch = vi.fn(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: serverRuns }) };
      }
      return { ok: false };
    });

    await (client as any).coldLoadRuns();

    // Should have only one run with latest seq
    expect((client as any).runs.size).toBe(1);
    expect((client as any).runs.get('dup1').status).toBe('running');
    expect((client as any).lastSeq.get('dup1')).toBe(3);

    // SSE event arrives with seq=5
    const sseEvent: RunRecord = { run_id: 'dup1', status: 'succeeded', seq: 5 };
    (client as any).applyEvent(sseEvent);

    // Still only one run with latest seq
    expect((client as any).runs.size).toBe(1);
    expect((client as any).runs.get('dup1').status).toBe('succeeded');
    expect((client as any).lastSeq.get('dup1')).toBe(5);
  });

  it('limits cache to 200 most recent runs', () => {
    const client = new WorkflowRunnerClient(store);

    // Add 250 runs with different updated_at timestamps
    for (let i = 0; i < 250; i++) {
      (client as any).runs.set(`run${i}`, {
        run_id: `run${i}`,
        status: i % 2 === 0 ? 'succeeded' : 'running',
        seq: i,
        updated_at: 1000 + i,
      });
    }

    const mockLocalStorage: any = {};
    (global as any).localStorage = {
      setItem: vi.fn((key: string, value: string) => {
        mockLocalStorage[key] = value;
      }),
      getItem: vi.fn((key: string) => mockLocalStorage[key] || null),
      removeItem: vi.fn(),
    };

    (client as any).saveCache();

    const cached = JSON.parse(mockLocalStorage['lf-runs-cache']);
    expect(cached.length).toBe(200);
    // Should contain the most recent runs (highest updated_at)
    expect(cached[0].run_id).toBe('run249');
    expect(cached[199].run_id).toBe('run50');
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
    (client as any).applyEvent(ev);

    const stored = (client as any).runs.get('wf-test-1');
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

    (global as any).fetch = vi.fn(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return {
          ok: true,
          json: async () => ({ runs: mockRuns }),
        };
      }
      return { ok: false };
    });

    await (client as any).coldLoadRuns();

    expect((client as any).runs.size).toBe(2);
    expect((client as any).runs.get('cold-wf-1').workflow_id).toBe('image_to_svg');
    expect((client as any).runs.get('cold-wf-2').workflow_id).toBe('svg_generation_gemini');
  });

  it('caches workflow_id in localStorage', () => {
    const client = new WorkflowRunnerClient(store);
    (client as any).runs.set('cache-wf-1', {
      run_id: 'cache-wf-1',
      workflow_id: 't2i_15_lcm',
      status: 'running',
      seq: 10,
      updated_at: 5000,
    });

    const mockLocalStorage: any = {};
    (global as any).localStorage = {
      setItem: vi.fn((key: string, value: string) => {
        mockLocalStorage[key] = value;
      }),
      getItem: vi.fn((key: string) => mockLocalStorage[key] || null),
      removeItem: vi.fn(),
    };

    (client as any).saveCache();

    const cached = JSON.parse(mockLocalStorage['lf-runs-cache']);
    expect(cached).toBeInstanceOf(Array);
    expect(cached.length).toBe(1);
    expect(cached[0].workflow_id).toBe('t2i_15_lcm');
    expect(cached[0].run_id).toBe('cache-wf-1');
  });

  it('restores workflow_id from localStorage', () => {
    const client = new WorkflowRunnerClient(store);
    const cachedRuns = [
      {
        run_id: 'restore-wf-1',
        workflow_id: 'image_to_svg',
        status: 'pending',
        seq: 3,
        updated_at: 7000,
      },
    ];

    const mockLocalStorage: any = {
      'lf-runs-cache': JSON.stringify(cachedRuns),
    };

    (global as any).localStorage = {
      setItem: vi.fn((key: string, value: string) => {
        mockLocalStorage[key] = value;
      }),
      getItem: vi.fn((key: string) => mockLocalStorage[key] || null),
      removeItem: vi.fn(),
    };

    (client as any).loadCache();

    expect((client as any).runs.size).toBe(1);
    const restored = (client as any).runs.get('restore-wf-1');
    expect(restored.workflow_id).toBe('image_to_svg');
    expect(restored.status).toBe('pending');
  });

  it('workflow_id survives reconciliation', async () => {
    const client = new WorkflowRunnerClient(store);
    const initialRun: RunRecord = {
      run_id: 'reconcile-wf-1',
      workflow_id: 't2i_15_lcm',
      status: 'running',
      seq: 1,
    };
    (client as any).applyEvent(initialRun);

    (global as any).fetch = vi.fn(async (url: string) => {
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

    (client as any).reconcileRun('reconcile-wf-1');
    // Wait for the inflight promise to complete
    const promise = (client as any).inflightReconciles.get('reconcile-wf-1');
    if (promise) await promise;

    const reconciled = (client as any).runs.get('reconcile-wf-1');
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
    (client as any).applyEvent(ev);

    const stored = (client as any).runs.get('no-wf-1');
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
    (client as any).applyEvent(ev);

    const stored = (client as any).runs.get('no-wf-2');
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

    runs.forEach((run) => (client as any).applyEvent(run));

    expect((client as any).runs.size).toBe(3);
    runs.forEach((run) => {
      const stored = (client as any).runs.get(run.run_id);
      expect(stored.workflow_id).toBe(workflow_id);
    });
  });

  it('workflow_id is preserved through cache → cold-load → SSE flow', async () => {
    const client = new WorkflowRunnerClient(store);
    const workflow_id = 't2i_15_lcm';
    const run_id = 'flow-test-1';

    // Simulate initial run in cache
    const cachedRuns = [
      {
        run_id,
        workflow_id,
        status: 'pending',
        seq: 1,
        updated_at: 1000,
      },
    ];

    const mockLocalStorage: any = {
      'lf-runs-cache': JSON.stringify(cachedRuns),
    };

    (global as any).localStorage = {
      setItem: vi.fn((key: string, value: string) => {
        mockLocalStorage[key] = value;
      }),
      getItem: vi.fn((key: string) => mockLocalStorage[key] || null),
      removeItem: vi.fn(),
    };

    // Load from cache
    (client as any).loadCache();
    expect((client as any).runs.get(run_id).workflow_id).toBe(workflow_id);
    expect((client as any).runs.get(run_id).seq).toBe(1);

    // Cold-load returns updated version
    (global as any).fetch = vi.fn(async (url: string) => {
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

    await (client as any).coldLoadRuns();
    expect((client as any).runs.get(run_id).workflow_id).toBe(workflow_id);
    expect((client as any).runs.get(run_id).status).toBe('running');
    expect((client as any).runs.get(run_id).seq).toBe(3);

    // SSE event arrives with completion
    const sseEvent: RunRecord = {
      run_id,
      workflow_id,
      status: 'succeeded',
      seq: 5,
    };
    (client as any).applyEvent(sseEvent);

    const final = (client as any).runs.get(run_id);
    expect(final.workflow_id).toBe(workflow_id);
    expect(final.status).toBe('succeeded');
    expect(final.seq).toBe(5);
  });

  it('start() merges initial SSE snapshot (message/run) into state', async () => {
    const client = new WorkflowRunnerClient(store);

    // Mock coldLoadRuns to be empty (server snapshot via SSE will provide data)
    (global as any).fetch = vi.fn(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: [] }) };
      }
      return { ok: false };
    });

    // Fake EventSource implementation to simulate server-sent events
    class FakeEventSource {
      static instances: FakeEventSource[] = [];
      onopen: ((e?: any) => void) | null = null;
      onmessage: ((e: any) => void) | null = null;
      onerror: ((e?: any) => void) | null = null;
      listeners: Record<string, (e: any) => void> = {} as any;
      constructor(_url: string) {
        (FakeEventSource.instances as any).push(this);
      }
      addEventListener(type: string, cb: (e: any) => void) {
        this.listeners[type] = cb;
      }
      close() {}
      // helpers
      send(type: string, data: any) {
        const evt = { data: JSON.stringify(data) } as any;
        const handler = this.listeners[type] || this.onmessage;
        if (handler) handler(evt);
      }
    }

    (global as any).EventSource = FakeEventSource as any;

    // Start client (will call coldLoadRuns and then create EventSource)
    await (client as any).start();

    // There should be one EventSource instance
    const es = (FakeEventSource as any).instances[0] as FakeEventSource;
    expect(es).toBeDefined();

    // Simulate server sending an initial snapshot as generic messages
    const msg1 = { run_id: 'sse1', status: 'succeeded', seq: 1, updated_at: 1111 };
    const msg2 = { run_id: 'sse2', status: 'pending', seq: 2, updated_at: 2222 };

    es.send('message', msg1);
    es.send('message', msg2);

    // allow processing microtasks
    await new Promise((r) => setTimeout(r, 10));

    expect((client as any).runs.get('sse1').status).toBe('succeeded');
    expect((client as any).runs.get('sse2').status).toBe('pending');

    // Also simulate server sending a 'run' event for another run
    const runEvt = { run_id: 'sse3', status: 'running', seq: 3, updated_at: 3333 };
    es.send('run', runEvt);

    await new Promise((r) => setTimeout(r, 10));
    expect((client as any).runs.get('sse3').status).toBe('running');

    // cleanup
    delete (global as any).EventSource;
  });

  it('processSnapshotArray ignores older snapshot entries when local seq is higher', async () => {
    const client = new WorkflowRunnerClient(store);
    // seed with a newer local seq
    (client as any).lastSeq.set('r_old', 5);
    (client as any).runs.set('r_old', { run_id: 'r_old', status: 'running', seq: 5 });

    // snapshot contains older seq (3) — should be ignored
    (client as any).processSnapshotArray([{ run_id: 'r_old', status: 'succeeded', seq: 3 }]);
    expect((client as any).lastSeq.get('r_old')).toBe(5);
    expect((client as any).runs.get('r_old').status).toBe('running');
  });

  it('processSnapshotArray accepts snapshot entries with higher seq', async () => {
    const client = new WorkflowRunnerClient(store);
    (client as any).lastSeq.set('r_up', 2);
    (client as any).runs.set('r_up', { run_id: 'r_up', status: 'pending', seq: 2 });

    (client as any).processSnapshotArray([{ run_id: 'r_up', status: 'succeeded', seq: 3 }]);

    expect((client as any).lastSeq.get('r_up')).toBe(3);
    expect((client as any).runs.get('r_up').status).toBe('succeeded');
  });

  it('start() clears processingSnapshot after receiving initial messages', async () => {
    const client = new WorkflowRunnerClient(store);

    (global as any).fetch = vi.fn(async (url: string) => {
      if (url.includes('/workflow-runner/runs'))
        return { ok: true, json: async () => ({ runs: [] }) };
      return { ok: false };
    });

    class FakeEventSource2 {
      onopen: ((e?: any) => void) | null = null;
      onmessage: ((e: any) => void) | null = null;
      listeners: Record<string, (e: any) => void> = {} as any;
      constructor(_url: string) {}
      addEventListener(type: string, cb: (e: any) => void) {
        this.listeners[type] = cb;
      }
      sendMessage(data: any) {
        const evt = { data: JSON.stringify(data) } as any;
        if (this.onmessage) this.onmessage(evt);
      }
      sendRun(type: string, data: any) {
        const evt = { data: JSON.stringify(data) } as any;
        const handler = this.listeners[type];
        if (handler) handler(evt);
      }
      close() {}
    }

    (global as any).EventSource = FakeEventSource2 as any;

    // start() sets processingSnapshot = true initially
    await (client as any).start();
    expect((client as any).processingSnapshot).toBe(true);

    // Simulate messages arriving and ensure processingSnapshot flips to false
    const es = (global as any).EventSource as any;
    // Find instance: our FakeEventSource2 doesn't record instances, so we'll call onmessage handler directly
    // access the instance created inside start() via client's es
    const inst = (client as any).es as any;
    // call onmessage to simulate message
    inst.onmessage({ data: JSON.stringify({ run_id: 'm1', status: 'succeeded', seq: 1 }) });

    await new Promise((r) => setTimeout(r, 10));
    expect((client as any).processingSnapshot).toBe(false);

    delete (global as any).EventSource;
  });

  it('buildLastEventId returns the run_id:seq for highest seq', () => {
    const client = new WorkflowRunnerClient(store);
    (client as any).lastSeq.set('a', 1);
    (client as any).lastSeq.set('b', 5);
    (client as any).lastSeq.set('c', 3);
    const lid = (client as any).buildLastEventId();
    expect(lid).toBe('b:5');
  });

  it('coldLoadRuns uses the expected URL params', async () => {
    const client = new WorkflowRunnerClient(store);
    let calledUrl = '';
    (global as any).fetch = vi.fn(async (url: string) => {
      calledUrl = url;
      return { ok: true, json: async () => ({ runs: [] }) };
    });
    await (client as any).coldLoadRuns();
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

    (global as any).fetch = vi.fn(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      return { ok: false };
    });

    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    await (client as any).coldLoadRuns();

    // Only the well-formed run should be present
    expect((client as any).runs.size).toBe(1);
    expect((client as any).runs.get('good1')).toBeDefined();
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
    (global as any).fetch = vi.fn(async (url: string) => {
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

    await (client as any).coldLoadRuns();

    // allow fetchWorkflowNames to complete
    await new Promise((r) => setTimeout(r, 10));

    expect((client as any).workflowNames.get('w1')).toBe('Remove background');
    expect((client as any).workflowNames.get('w2')).toBe('Resize');
  });

  it('does not call workflows endpoint when workflow_id is missing', async () => {
    const client = new WorkflowRunnerClient(store);
    const mockRuns = [{ run_id: 'r1', status: 'succeeded', seq: 1 }];
    let workflowsCalled = false;
    (global as any).fetch = vi.fn(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: mockRuns }) };
      }
      if (url.includes('/workflows')) {
        workflowsCalled = true;
        return { ok: true, json: async () => ({ workflows: [] }) };
      }
      return { ok: false };
    });

    await (client as any).coldLoadRuns();
    await new Promise((r) => setTimeout(r, 10));
    expect(workflowsCalled).toBe(false);
  });

  it('reconciles runs missing workflow_id by calling status endpoint and populating workflow_id', async () => {
    const client = new WorkflowRunnerClient(store);
    const runId = 'r-missing-wf';
    const mockRuns = [{ run_id: runId, status: 'succeeded', seq: 1 }];

    (global as any).fetch = vi.fn(async (url: string) => {
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

    await (client as any).coldLoadRuns();
    // wait for reconcileRun to complete
    await new Promise((r) => setTimeout(r, 20));

    const rec = (client as any).runs.get(runId);
    expect(rec).toBeDefined();
    expect(rec.workflow_id).toBe('w-remote');
    expect((client as any).lastSeq.get(runId)).toBe(2);
  });

  describe('404 eviction (DB reset robustness)', () => {
    it('removes run from state and cache when server returns 404', async () => {
      const client = new WorkflowRunnerClient(store);

      // Seed cache with run A
      const runA = { run_id: 'runA', status: 'succeeded', seq: 1 };
      (client as any).runs.set('runA', runA);
      (client as any).lastSeq.set('runA', 1);
      (client as any).saveCache();

      // Verify run is in cache
      expect((client as any).runs.has('runA')).toBe(true);

      // Mock fetch: coldLoadRuns returns empty, status endpoint returns 404 for runA
      (global as any).fetch = vi.fn(async (url: string) => {
        if (url.includes('/workflow-runner/runs')) {
          return { ok: true, json: async () => ({ runs: [] }) };
        }
        if (url.endsWith('/run/runA/status')) {
          return { status: 404, ok: false };
        }
        return { ok: false };
      });

      await (client as any).coldLoadRuns();

      // Wait for reconcile to complete
      const promise = (client as any).inflightReconciles.get('runA');
      if (promise) await promise;

      // Verify runA is removed from state
      expect((client as any).runs.has('runA')).toBe(false);
      expect((client as any).lastSeq.has('runA')).toBe(false);

      // Verify cache no longer contains runA
      const cacheRaw = localStorage.getItem((client as any).cacheKey);
      if (cacheRaw) {
        const cached = JSON.parse(cacheRaw);
        expect(cached.some((r: any) => r.run_id === 'runA')).toBe(false);
      }
    });

    it('removes only missing runs when server returns partial set', async () => {
      const client = new WorkflowRunnerClient(store);

      // Cache runs A and B
      (client as any).runs.set('runA', { run_id: 'runA', status: 'succeeded', seq: 1 });
      (client as any).runs.set('runB', { run_id: 'runB', status: 'succeeded', seq: 2 });
      (client as any).lastSeq.set('runA', 1);
      (client as any).lastSeq.set('runB', 2);

      // Mock fetch: server only returns runB, runA returns 404
      (global as any).fetch = vi.fn(async (url: string) => {
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

      await (client as any).coldLoadRuns();

      // Wait for reconcile to complete
      const promiseA = (client as any).inflightReconciles.get('runA');
      if (promiseA) await promiseA;

      // runA should be removed
      expect((client as any).runs.has('runA')).toBe(false);
      expect((client as any).lastSeq.has('runA')).toBe(false);

      // runB should remain
      expect((client as any).runs.has('runB')).toBe(true);
      expect((client as any).runs.get('runB').status).toBe('succeeded');
    });

    it('de-dupes multiple reconcile requests for the same run', async () => {
      const client = new WorkflowRunnerClient(store);
      let fetchCount = 0;

      (global as any).fetch = vi.fn(async (url: string) => {
        if (url.endsWith('/run/runX/status')) {
          fetchCount++;
          return { status: 404, ok: false };
        }
        return { ok: false };
      });

      // Fire two reconcile requests quickly
      (client as any).reconcileRun('runX');
      (client as any).reconcileRun('runX');

      // Wait for reconcile to complete
      const promise = (client as any).inflightReconciles.get('runX');
      if (promise) await promise;

      // Should only fetch once due to de-duplication
      expect(fetchCount).toBe(1);
    });

    it('handles mixed snapshot where some runs exist and others return 404', async () => {
      const client = new WorkflowRunnerClient(store);

      // Cache three runs
      (client as any).runs.set('run1', { run_id: 'run1', status: 'succeeded', seq: 1 });
      (client as any).runs.set('run2', { run_id: 'run2', status: 'succeeded', seq: 2 });
      (client as any).runs.set('run3', { run_id: 'run3', status: 'succeeded', seq: 3 });
      (client as any).lastSeq.set('run1', 1);
      (client as any).lastSeq.set('run2', 2);
      (client as any).lastSeq.set('run3', 3);

      // Server returns only run2 and run3
      (global as any).fetch = vi.fn(async (url: string) => {
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

      await (client as any).coldLoadRuns();

      // Wait for reconciles
      const promise1 = (client as any).inflightReconciles.get('run1');
      if (promise1) await promise1;

      // run1 should be removed (404)
      expect((client as any).runs.has('run1')).toBe(false);

      // run2 and run3 should remain
      expect((client as any).runs.has('run2')).toBe(true);
      expect((client as any).runs.has('run3')).toBe(true);
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
      (global as any).fetch = vi.fn(async (url: string) => {
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

      // Mock EventSource to prevent actual SSE connection
      const mockES = {
        onopen: null,
        onerror: null,
        onmessage: null,
        addEventListener: vi.fn(),
        close: vi.fn(),
      };
      (global as any).EventSource = vi.fn(() => mockES);

      await client.start();

      // Wait for reconciles
      const promiseA = (client as any).inflightReconciles.get('runA');
      if (promiseA) await promiseA;

      // runA should be removed (404)
      expect((client as any).runs.has('runA')).toBe(false);

      // runB should exist with hydrated data
      expect((client as any).runs.has('runB')).toBe(true);
      const runB = (client as any).runs.get('runB');
      expect(runB.seq).toBe(2);
      expect(runB.status).toBe('succeeded');
    });

    it('does not create duplicate hydration requests', async () => {
      const client = new WorkflowRunnerClient(store);
      let fetchCount = 0;

      (global as any).fetch = vi.fn(async (url: string) => {
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
      (client as any).reconcileRun('runX');
      (client as any).reconcileRun('runX');

      // Wait for reconcile to complete
      const promise = (client as any).inflightReconciles.get('runX');
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

      const ids = (client as any).loadCacheIds();

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

      const ids = (client as any).loadCacheIds();

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

      const ids = (client as any).loadCacheIds();

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
      (client as any).applyEvent(ev);

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
      (client as any).seedPlaceholders(ids);

      // All should exist with placeholder status
      expect((client as any).runs.size).toBe(3);
      expect((client as any).runs.get('ph1').status).toBe('pending');
      expect((client as any).runs.get('ph1').seq).toBe(-1);
      expect((client as any).runs.get('ph2').status).toBe('pending');
      expect((client as any).runs.get('ph3').status).toBe('pending');
    });

    it('does not overwrite existing runs when seeding placeholders', () => {
      const client = new WorkflowRunnerClient(store);

      // Add an existing run
      (client as any).runs.set('existing', {
        run_id: 'existing',
        status: 'succeeded',
        seq: 5,
        result: { data: 'important' },
      });

      // Seed placeholders including the existing run
      (client as any).seedPlaceholders(['existing', 'new1']);

      // Existing run should not be overwritten
      expect((client as any).runs.get('existing').status).toBe('succeeded');
      expect((client as any).runs.get('existing').seq).toBe(5);
      expect((client as any).runs.get('existing').result.data).toBe('important');

      // New run should be placeholder
      expect((client as any).runs.get('new1').status).toBe('pending');
      expect((client as any).runs.get('new1').seq).toBe(-1);
    });
  });
});
