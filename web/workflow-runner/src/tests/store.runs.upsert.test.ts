import { describe, it, expect } from 'vitest';
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

describe('runs.upsert', () => {
  it('preserves existing fields when updates omit them', () => {
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
    expect(run.runId).toBe('run-1');
    expect(run.status).toBe('running');
    expect(run.createdAt).toBe(createdAt);
    expect(run.workflowId).toBe('wf-1');
    expect(run.workflowName).toBe('Updated workflow');
    expect(run.inputs).toEqual(originalInputs);
    expect(run.resultPayload).toEqual(originalPayload);
  });

  it('inserts new runs at the front and updates existing entries in place', () => {
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
    expect(runs.length).toBe(2);
    expect(runs[0].runId).toBe('run-2');
    expect(runs[1].runId).toBe('run-1');
    expect(runs[1].status).toBe('running');
  });
});
