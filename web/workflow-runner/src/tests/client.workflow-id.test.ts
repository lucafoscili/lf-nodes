import './setup';
import { makeFetchMock, getClientInternalsWithMethods } from './_utils';
import { describe, expect, it } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord } from '../types/client';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient - workflow_id handling', () => {
  it('stores and retrieves workflow_id correctly', () => {
    const client = new WorkflowRunnerClient(store);
    const ev: RunRecord = {
      run_id: 'wf-test-1',
      workflow_id: 't2i_15_lcm',
      status: 'pending',
      seq: 1,
    };
    getClientInternalsWithMethods(client).applyEvent(ev);

    const stored = getClientInternalsWithMethods(client).runs.get('wf-test-1');
    expect(stored).toBeDefined();
    expect(stored.workflow_id).toBe('t2i_15_lcm');
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

  it('multiple runs with same workflow_id are handled correctly', () => {
    const client = new WorkflowRunnerClient(store);
    const workflow_id = 'shared_workflow';

    const runs = [
      { run_id: 'shared-1', workflow_id, status: 'pending', seq: 1 },
      { run_id: 'shared-2', workflow_id, status: 'running', seq: 1 },
      { run_id: 'shared-3', workflow_id, status: 'succeeded', seq: 1 },
    ];

    runs.forEach((run) =>
      getClientInternalsWithMethods(client).applyEvent(run as unknown as RunRecord),
    );

    expect(getClientInternalsWithMethods(client).runs.size).toBe(3);
    runs.forEach((run) => {
      const stored = getClientInternalsWithMethods(client).runs.get(run.run_id);
      expect(stored.workflow_id).toBe(workflow_id);
    });
  });
});
