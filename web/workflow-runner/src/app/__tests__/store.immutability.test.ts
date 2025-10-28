import assert from 'node:assert/strict';
import test from 'node:test';

import { createWorkflowRunnerStore } from '../store';
import { initState } from '../state';
import { WorkflowState } from '../../types/state';

test('run upsert mutations notify subscribers with fresh state references', () => {
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

  assert.equal(observed.length, 3, 'expected three subscriber notifications');

  const [pendingState, runningState, succeededState] = observed;

  assert.notStrictEqual(pendingState, runningState);
  assert.notStrictEqual(runningState, succeededState);
  assert.notStrictEqual(pendingState, succeededState);

  assert.notStrictEqual(pendingState.runs, runningState.runs);
  assert.notStrictEqual(runningState.runs, succeededState.runs);

  assert.equal(pendingState.runs[0]?.status, 'pending');
  assert.equal(runningState.runs[0]?.status, 'running');
  assert.equal(succeededState.runs[0]?.status, 'succeeded');
});
