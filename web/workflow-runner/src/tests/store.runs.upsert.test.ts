import assert from 'node:assert/strict';
import test from 'node:test';

import { createWorkflowRunnerStore } from '../app/store';
import { initState } from '../app/state';
import { WorkflowRunResultPayload } from '../types/api';

const createResultPayload = (): WorkflowRunResultPayload => ({
  http_status: 202,
  body: {
    message: 'pending',
    payload: {
      detail: 'original',
      history: {},
    },
    status: 'pending',
  },
});

test('runs.upsert preserves existing fields when updates omit them', () => {
  const store = createWorkflowRunnerStore(initState());
  const createdAt = 1_000;
  const originalPayload = createResultPayload();
  const originalInputs = { foo: 'bar' };

  store.getState().mutate.runs.upsert({
    runId: 'run-1',
    status: 'pending',
    createdAt,
    updatedAt: createdAt,
    workflowId: 'wf-1',
    workflowName: 'Original workflow',
    inputs: originalInputs,
    outputs: null,
    resultPayload: originalPayload,
  });

  store.getState().mutate.runs.upsert({
    runId: 'run-1',
    status: 'running',
    updatedAt: createdAt + 1,
    workflowName: 'Updated workflow',
    resultPayload: undefined,
  });

  const [run] = store.getState().runs;
  assert.equal(run.runId, 'run-1');
  assert.equal(run.status, 'running');
  assert.equal(run.createdAt, createdAt, 'createdAt should remain untouched');
  assert.equal(run.workflowId, 'wf-1');
  assert.equal(run.workflowName, 'Updated workflow');
  assert.deepEqual(run.inputs, originalInputs);
  assert.deepEqual(run.resultPayload, originalPayload, 'undefined update should preserve existing payload');
});

test('runs.upsert inserts new runs at the front and updates existing entries in place', () => {
  const store = createWorkflowRunnerStore(initState());
  store.getState().mutate.runs.upsert({
    runId: 'run-1',
    status: 'pending',
    createdAt: 1,
    updatedAt: 1,
  });

  store.getState().mutate.runs.upsert({
    runId: 'run-2',
    status: 'pending',
    createdAt: 2,
    updatedAt: 2,
  });

  store.getState().mutate.runs.upsert({
    runId: 'run-1',
    status: 'running',
    updatedAt: 3,
  });

  const { runs } = store.getState();
  assert.equal(runs.length, 2);
  assert.equal(runs[0].runId, 'run-2', 'most recent insertion should remain at the front');
  assert.equal(runs[1].runId, 'run-1', 'the original run should remain in place');
  assert.equal(runs[1].status, 'running', 'existing entry should be updated in place');
});
