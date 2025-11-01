import { describe, it, expect, vi } from 'vitest';
import { WorkflowRunnerClient, RunRecord } from '../app/client';

describe('workflowRunnerClient (compat tests)', () => {
  it('ignores duplicate events', () => {
    const client = new WorkflowRunnerClient('/api/lf-nodes');
    const ev: RunRecord = { run_id: 'r1', status: 'pending', seq: 1 };
    (client as any).applyEvent(ev);
    (client as any).applyEvent(ev);
    expect((client as any).runs.size).toBe(1);
    expect((client as any).lastSeq.get('r1')).toBe(1);
  });

  it('triggers reconcile on gap detection', async () => {
    const client = new WorkflowRunnerClient('/api/lf-nodes');
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
    const client = new WorkflowRunnerClient('/api/lf-nodes');
    (global as any).fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({ run_id: 'r3', status: 'succeeded', seq: 5, result: { ok: true } }),
    }));
    await (client as any).reconcileRun('r3');
    expect((client as any).runs.get('r3').status).toBe('succeeded');
    expect((client as any).lastSeq.get('r3')).toBe(5);
  });

  it('polling merges snapshot', async () => {
    const client = new WorkflowRunnerClient('/api/lf-nodes');
    (global as any).fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({ runs: [{ run_id: 'r4', status: 'pending', seq: 2 }] }),
    }));
    await (client as any).pollActiveRuns();
    expect((client as any).runs.get('r4').status).toBe('pending');
    expect((client as any).lastSeq.get('r4')).toBe(2);
  });

  it('aborts in-flight polling on stop', async () => {
    const client = new WorkflowRunnerClient('/api/lf-nodes');
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
    const client = new WorkflowRunnerClient('/api/lf-nodes');
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
});
