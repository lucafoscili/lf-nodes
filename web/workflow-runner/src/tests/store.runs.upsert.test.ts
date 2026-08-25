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

  it('keeps history newest-first after mixed-date cold-load/live merges', () => {
    const store = createWorkflowRunnerStore(initState());

    store.getState().mutate.runs.upsert({
      runId: 'legacy-run',
      status: 'failed',
      createdAt: Date.parse('2025-11-15T00:53:35Z'),
      updatedAt: Date.parse('2026-08-16T01:04:33Z'),
    });
    store.getState().mutate.runs.upsert({
      runId: 'newer-run',
      status: 'succeeded',
      createdAt: Date.parse('2026-08-16T01:10:57Z'),
      updatedAt: Date.parse('2026-08-16T01:10:59Z'),
    });
    store.getState().mutate.runs.upsert({
      runId: 'live-run',
      status: 'running',
      createdAt: Date.parse('2026-08-25T00:01:00Z'),
      updatedAt: Date.parse('2026-08-25T00:01:01Z'),
    });

    expect(store.getState().runs.map((run) => run.runId)).toEqual([
      'live-run',
      'newer-run',
      'legacy-run',
    ]);
  });

  it('uses run id as a deterministic tie-break for equal creation times', () => {
    const store = createWorkflowRunnerStore(initState());
    const createdAt = 1_000;

    store.getState().mutate.runs.upsert({
      runId: 'run-z',
      status: 'succeeded',
      createdAt,
      updatedAt: 3_000,
    });
    store.getState().mutate.runs.upsert({
      runId: 'run-a',
      status: 'succeeded',
      createdAt,
      updatedAt: 1_000,
    });

    expect(store.getState().runs.map((run) => run.runId)).toEqual(['run-a', 'run-z']);
  });

  it('removes several runs and clears references to removed entries', () => {
    const store = createWorkflowRunnerStore(initState());
    for (const runId of ['keep', 'remove-a', 'remove-b']) {
      store.getState().mutate.runs.upsert({
        runId,
        status: 'succeeded',
        createdAt: 1,
        updatedAt: 1,
      });
    }
    store.getState().mutate.runId('remove-a');
    store.getState().mutate.selectRun('remove-b');
    store.getState().mutate.inputPrefillRun('remove-a');

    store.getState().mutate.runs.removeMany(['remove-a', 'remove-b', 'remove-a']);

    expect(store.getState().runs.map((run) => run.runId)).toEqual(['keep']);
    expect(store.getState().currentRunId).toBeNull();
    expect(store.getState().selectedRunId).toBeNull();
    expect(store.getState().inputPrefillRunId).toBeNull();
  });
});
