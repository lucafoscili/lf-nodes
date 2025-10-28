import assert from 'node:assert/strict';
import test from 'node:test';

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
  status,
  updatedAt: createdAt,
  workflowId: 'wf',
  workflowName: 'Workflow',
});

test('ensureActiveRun maintains a queue of pending runs', () => {
  const store = createWorkflowRunnerStore(initState());

  const runA = createRun('run-a', 'pending', 1000);
  upsertRun(store, runA);
  ensureActiveRun(store, runA.runId);

  assert.equal(store.getState().currentRunId, 'run-a');

  const runB = createRun('run-b', 'pending', 2000);
  upsertRun(store, runB);
  ensureActiveRun(store, runB.runId);

  assert.equal(
    store.getState().currentRunId,
    'run-a',
    'an existing active run should not be replaced by a newer pending run',
  );

  upsertRun(store, { runId: 'run-a', status: 'succeeded', updatedAt: 3000 });
  setRunInFlight(store, null);
  ensureActiveRun(store);

  assert.equal(
    store.getState().currentRunId,
    'run-b',
    'the next pending run should become active after the current run completes',
  );

  upsertRun(store, { runId: 'run-b', status: 'succeeded', updatedAt: 4000 });
  setRunInFlight(store, null);
  ensureActiveRun(store);

  assert.equal(store.getState().currentRunId, null);
});
