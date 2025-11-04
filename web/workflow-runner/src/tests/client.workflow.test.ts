import './setup';
import {
  TestEventSource,
  createMockLocalStorage,
  attachMockLocalStorage,
  makeFetchMock,
  wait,
  getClientInternalsWithMethods,
} from './_utils';
import { describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord } from '../types/client';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient - workflow handling', () => {
  it('applies workflow_id to runs without it', () => {
    const client = new WorkflowRunnerClient(store);
    const workflow_id = 'test_wf';

    client.onUpdate = (runs) => {
      for (const run of runs.values()) {
        if (!run.workflow_id) {
          run.workflow_id = workflow_id;
        }
      }
    };

    const runs = [
      { run_id: 'shared-1', status: 'pending', seq: 1 },
      { run_id: 'shared-2', status: 'running', seq: 1 },
      { run_id: 'shared-3', status: 'succeeded', seq: 1 },
    ];

    runs.forEach((run) => getClientInternalsWithMethods(client).applyEvent(run as RunRecord));

    expect(getClientInternalsWithMethods(client).runs.size).toBe(3);
    runs.forEach((run) => {
      const stored = getClientInternalsWithMethods(client).runs.get(run.run_id);
      expect(stored.workflow_id).toBe(workflow_id);
    });
  });

  it('multiple runs with same workflow_id are handled correctly', () => {
    const client = new WorkflowRunnerClient(store);
    const workflow_id = 'shared_workflow';

    const runs = [
      { run_id: 'shared-1', workflow_id, status: 'pending', seq: 1 },
      { run_id: 'shared-2', workflow_id, status: 'running', seq: 1 },
      { run_id: 'shared-3', workflow_id, status: 'succeeded', seq: 1 },
    ];

    runs.forEach((run) => getClientInternalsWithMethods(client).applyEvent(run as RunRecord));

    expect(getClientInternalsWithMethods(client).runs.size).toBe(3);
    runs.forEach((run) => {
      const stored = getClientInternalsWithMethods(client).runs.get(run.run_id);
      expect(stored.workflow_id).toBe(workflow_id);
    });
  });

  it('handles null workflow_id correctly', () => {
    const client = new WorkflowRunnerClient(store);
    const ev: RunRecord = {
      run_id: 'no-wf-1',
      workflow_id: null,
      status: 'pending',
      seq: 1,
    };
    getClientInternalsWithMethods(client).applyEvent(ev);

    const stored = getClientInternalsWithMethods(client).runs.get('no-wf-1');
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
    getClientInternalsWithMethods(client).applyEvent(ev);

    const stored = getClientInternalsWithMethods(client).runs.get('no-wf-2');
    expect(stored).toBeDefined();
    expect(stored.workflow_id).toBeUndefined();
  });

  it('workflow_id is preserved through cache → cold-load → SSE flow', async () => {
    const client = new WorkflowRunnerClient(store);
    const workflow_id = 't2i_15_lcm';
    const run_id = 'flow-test-1';

    // Simulate initial IDs-only cache (placeholders) for the run
    const cachePayload = {
      version: 1,
      cached_at: Date.now(),
      run_ids: [run_id],
    };

    const mockLocalStorage = createMockLocalStorage({
      'lf-runs-cache': JSON.stringify(cachePayload),
    });

    attachMockLocalStorage(mockLocalStorage);

    // Start client to load cache
    await client.start();

    // Verify placeholder was created
    expect(client.getRuns().has(run_id)).toBe(true);
    expect(client.getRuns().get(run_id).status).toBe('pending');

    // Simulate SSE event with full run data
    const sseData = {
      run_id,
      workflow_id,
      status: 'running' as const,
      seq: 1,
    };

    getClientInternalsWithMethods(client).applyEvent(sseData);

    // Verify workflow_id was preserved
    expect(client.getRuns().get(run_id).workflow_id).toBe(workflow_id);

    // Simulate reconcile by applying authoritative state
    const reconciledData = {
      run_id,
      workflow_id,
      status: 'succeeded' as const,
      seq: 3,
    };

    getClientInternalsWithMethods(client).applyEvent(reconciledData);

    const reconciled = client.getRuns().get(run_id);
    expect(reconciled.workflow_id).toBe('t2i_15_lcm');
    expect(reconciled.status).toBe('succeeded');
    expect(reconciled.seq).toBe(3);
  });
});
