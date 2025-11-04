import './setup';
import { makeFetchMock, getClientInternalsWithMethods } from './_utils';
import { describe, expect, it } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient - polling', () => {
  it('polling merges snapshot', async () => {
    const client = new WorkflowRunnerClient(store);
    makeFetchMock(async () => ({
      ok: true,
      json: async () => ({ runs: [{ run_id: 'r4', status: 'pending', seq: 2 }] }),
    }));
    await getClientInternalsWithMethods(client).pollActiveRuns();
    expect(getClientInternalsWithMethods(client).runs.get('r4').status).toBe('pending');
    expect(getClientInternalsWithMethods(client).lastSeq.get('r4')).toBe(2);
  });
});
