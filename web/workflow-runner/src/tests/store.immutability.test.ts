import { describe, it, expect, vi } from 'vitest';
import { createWorkflowRunnerStore } from '../app/store';
import { initState } from '../app/state';
import { WorkflowState } from '../types/state';

describe('store.immutability', () => {
  it('run upsert mutations notify subscribers with fresh state references', () => {
    const store = createWorkflowRunnerStore(initState());
    const observed: WorkflowState[] = [];
    store.subscribe((snapshot) => {
      observed.push(snapshot);
    });

    const { mutate } = store.getState();
    const runId = 'test-run';
    const createdAt = Date.now();

    mutate.runs.upsert({ runId, status: 'pending', createdAt, updatedAt: createdAt });
    mutate.runs.upsert({ runId, status: 'running', updatedAt: createdAt + 1 });
    mutate.runs.upsert({ runId, status: 'succeeded', updatedAt: createdAt + 2 });

    expect(observed.length).toBe(3);

    const [pendingState, runningState, succeededState] = observed;

    expect(pendingState !== runningState).toBe(true);
    expect(runningState !== succeededState).toBe(true);
    expect(pendingState !== succeededState).toBe(true);

    expect(pendingState.runs !== runningState.runs).toBe(true);
    expect(runningState.runs !== succeededState.runs).toBe(true);

    expect(pendingState.runs[0]?.status).toBe('pending');
    expect(runningState.runs[0]?.status).toBe('running');
    expect(succeededState.runs[0]?.status).toBe('succeeded');
  });

  it('does not notify subscribers when the queue count is unchanged', () => {
    const store = createWorkflowRunnerStore(initState());
    const subscriber = vi.fn();
    store.subscribe(subscriber);

    store.getState().mutate.queuedJobs(0);
    store.getState().mutate.queuedJobs(0);

    expect(subscriber).toHaveBeenCalledTimes(1);
  });
});
