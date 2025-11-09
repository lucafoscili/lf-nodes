import './setup';
import { getClientInternalsWithMethods } from './_utils';
import { describe, expect, it } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord } from '../types/client';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient - event handling', () => {
  it('ignores duplicate events', () => {
    const client = new WorkflowRunnerClient(store);
    const ev: RunRecord = { run_id: 'r1', status: 'pending', seq: 1 };
    getClientInternalsWithMethods(client).applyEvent(ev);
    getClientInternalsWithMethods(client).applyEvent(ev);
    expect(getClientInternalsWithMethods(client).runs.size).toBe(1);
    expect(getClientInternalsWithMethods(client).lastSeq.get('r1')).toBe(1);
  });
});
