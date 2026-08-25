import { describe, it, expect } from 'vitest';
import { ensureActiveRun, setRunInFlight, upsertRun } from '../app/store-actions';
import { createWorkflowRunnerStore } from '../app/store';
import { initState } from '../app/state';
import { WorkflowRunStatus } from '../types/api';

const createRun = (runId: string, status: WorkflowRunStatus, createdAt = Date.now()) => ({
  createdAt,
  error: null,
  httpStatus: null,
  inputs: {},
  outputs: null,
  resultPayload: null,
  runId,
  submissionId: `lf-web:${runId}`,
  status,
  updatedAt: createdAt,
  workflowId: 'wf',
  workflowName: 'Workflow',
});

describe('runs.queue', () => {
  it('ensureActiveRun maintains a queue of pending runs', () => {
    const store = createWorkflowRunnerStore(initState());

    const runA = createRun('run-a', 'pending', 1000);
    upsertRun(store, runA);
    ensureActiveRun(store, runA.runId);

    expect(store.getState().currentRunId).toBe('run-a');

    const runB = createRun('run-b', 'pending', 2000);
    upsertRun(store, runB);
    ensureActiveRun(store, runB.runId);

    expect(store.getState().currentRunId).toBe('run-a');

    upsertRun(store, { runId: 'run-a', status: 'succeeded', updatedAt: 3000 });
    setRunInFlight(store, null);
    ensureActiveRun(store);

    expect(store.getState().currentRunId).toBe('run-b');

    upsertRun(store, { runId: 'run-b', status: 'succeeded', updatedAt: 4000 });
    setRunInFlight(store, null);
    ensureActiveRun(store);

    expect(store.getState().currentRunId).toBeNull();
  });

  it('ensureActiveRun honors preferred run when it is still pending', () => {
    const store = createWorkflowRunnerStore(initState());

    const runA = createRun('run-a', 'pending', 1000);
    const runB = createRun('run-b', 'pending', 1000);
    const runC = createRun('run-c', 'pending', 1000);

    upsertRun(store, runA);
    upsertRun(store, runB);
    upsertRun(store, runC);

    ensureActiveRun(store, runB.runId);
    expect(store.getState().currentRunId).toBe('run-b');

    upsertRun(store, { runId: 'run-b', status: 'succeeded', updatedAt: 2_000 });
    setRunInFlight(store, null);
    ensureActiveRun(store, runB.runId);

    const fallbackRunId = store.getState().currentRunId;
    expect(fallbackRunId === 'run-a' || fallbackRunId === 'run-c').toBe(true);
    expect(store.getState().runs.find((run) => run.runId === fallbackRunId)?.status).toBe(
      'pending',
    );
  });

  it('does not let an unbound legacy active row monopolize Run control', () => {
    const store = createWorkflowRunnerStore(initState());
    upsertRun(store, {
      createdAt: 1,
      runId: 'legacy-running',
      status: 'running',
      submissionId: null,
      updatedAt: 1,
    });

    ensureActiveRun(store);

    expect(store.getState().currentRunId).toBeNull();
    expect(store.getState().runs.some((run) => run.runId === 'legacy-running')).toBe(true);
  });

  it('prefers a controlled active run while retaining an unbound legacy row', () => {
    const store = createWorkflowRunnerStore(initState());
    upsertRun(store, {
      createdAt: 1,
      runId: 'legacy-running',
      status: 'running',
      submissionId: null,
      updatedAt: 1,
    });
    upsertRun(store, {
      createdAt: 2,
      runId: 'controlled-pending',
      status: 'pending',
      submissionId: 'lf-web:controlled',
      updatedAt: 2,
    });

    ensureActiveRun(store);

    expect(store.getState().currentRunId).toBe('controlled-pending');
    expect(store.getState().runs).toHaveLength(2);
  });
});
