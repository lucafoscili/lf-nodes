import './setup';
import { makeFetchMock, getClientInternalsWithMethods } from './_utils';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord } from '../types/client';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient - polling', () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('polling merges snapshot', async () => {
    const client = new WorkflowRunnerClient(store);
    makeFetchMock(async () => ({
      ok: true,
      json: async () => ({ runs: [{ run_id: 'r4', status: 'pending', seq: 2 }] }),
    }));
    await getClientInternalsWithMethods(client).pollActiveRuns();
    expect(getClientInternalsWithMethods(client).runs.get('r4').status).toBe('pending');
    expect(getClientInternalsWithMethods(client).lastSeq.get('r4')).toBe(2);
  });

  it('does not publish an unchanged same-sequence polling snapshot', () => {
    const localStore = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(localStore);
    const internals = getClientInternalsWithMethods(client);
    const snapshot: RunRecord[] = [{ run_id: 'stable', status: 'succeeded', seq: 4 }];

    internals.processSnapshotArray(snapshot);
    const subscriber = vi.fn();
    localStore.subscribe(subscriber);

    internals.processSnapshotArray(snapshot);

    expect(subscriber).toHaveBeenCalledTimes(0);
  });

  it('reconciles a pending run omitted from the authoritative active snapshot', () => {
    const localStore = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(localStore);
    const internals = getClientInternalsWithMethods(client);
    internals.processSnapshotArray([{ run_id: 'pending-finished', status: 'pending', seq: 1 }]);
    const reconcile = vi.spyOn(internals, 'reconcileRun').mockImplementation(() => undefined);

    internals.processSnapshotArray([]);

    expect(reconcile).toHaveBeenCalledWith('pending-finished');
  });

  it('merges lifecycle control metadata from an equal-sequence snapshot', () => {
    const localStore = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(localStore);
    const internals = getClientInternalsWithMethods(client);
    internals.processSnapshotArray([{ run_id: 'same-seq', status: 'running', seq: 4 }]);

    internals.processSnapshotArray([
      {
        run_id: 'same-seq',
        status: 'running',
        seq: 4,
        submission_id: 'lf-web:same-seq',
        cancel_requested: true,
      },
    ]);

    expect(internals.runs.get('same-seq')).toMatchObject({
      submission_id: 'lf-web:same-seq',
      cancel_requested: true,
      status: 'running',
      seq: 4,
    });
  });

  it('backs off exponentially up to the configured ceiling', () => {
    const client = new WorkflowRunnerClient(createWorkflowRunnerStore(initState()));
    const internals = getClientInternalsWithMethods(client);
    vi.spyOn(Math, 'random').mockReturnValue(1);

    const delays = Array.from({ length: 8 }, () => internals.backoffWithJitter());

    expect(delays).toEqual([1000, 2000, 4000, 8000, 16000, 30000, 30000, 30000]);
  });

  it('never overlaps a slow poll', async () => {
    const client = new WorkflowRunnerClient(createWorkflowRunnerStore(initState()));
    const internals = getClientInternalsWithMethods(client);
    let release: (() => void) | undefined;
    const fetchMock = vi.fn(
      () =>
        new Promise<any>((resolve) => {
          release = () => resolve({ ok: true, json: async () => ({ runs: [] }) });
        }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const first = internals.pollActiveRuns();
    const overlapping = internals.pollActiveRuns();
    expect(fetchMock).toHaveBeenCalledTimes(1);

    release?.();
    await Promise.all([first, overlapping]);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('stop cancels reconnect and polling so the client cannot resurrect', async () => {
    vi.useFakeTimers();
    const client = new WorkflowRunnerClient(createWorkflowRunnerStore(initState()));
    makeFetchMock(async () => ({ ok: true, json: async () => ({ runs: [] }) }));
    await client.start();
    const instances = (globalThis as any).TestEventSource.instances;
    const countBeforeError = instances.length;
    instances.at(-1).onerror?.();

    client.stop();
    await vi.advanceTimersByTimeAsync(60_000);

    expect(instances).toHaveLength(countBeforeError);
  });
});
