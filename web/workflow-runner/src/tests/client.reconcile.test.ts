import './setup';
import { makeFetchMock, wait, getClientInternalsWithMethods } from './_utils';
import { describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { RunRecord } from '../types/client';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient - reconcile', () => {
  it('triggers reconcile on gap detection', async () => {
    const client = new WorkflowRunnerClient(store);
    getClientInternalsWithMethods(client).lastSeq.set('r2', 1);
    let reconciled = false;
    // override the reconcileRun implementation for this test
    getClientInternalsWithMethods(client).reconcileRun = async (_run_id: string) => {
      reconciled = true;
    };
    const ev: RunRecord = { run_id: 'r2', status: 'running', seq: 4 };
    getClientInternalsWithMethods(client).applyEvent(ev);
    await wait(10);
    expect(reconciled).toBe(true);
  });

  it('reconcileRun updates state', async () => {
    const client = new WorkflowRunnerClient(store);
    makeFetchMock(async (url: string) => {
      if (url.endsWith('/run/r3/status') || url.includes('/run/r3/status')) {
        return {
          ok: true,
          json: async () => ({ run_id: 'r3', status: 'succeeded', seq: 5, result: { ok: true } }),
        };
      }
      return { ok: false };
    });

    getClientInternalsWithMethods(client).reconcileRun('r3');
    // Wait for the inflight promise to complete
    const promise = getClientInternalsWithMethods(client).inflightReconciles.get('r3');
    if (promise) await promise;

    const reconciled = getClientInternalsWithMethods(client).runs.get('r3');
    expect(reconciled.status).toBe('succeeded');
    expect(reconciled.seq).toBe(5);
  });

  it('workflow_id survives reconciliation', async () => {
    const client = new WorkflowRunnerClient(store);
    const initialRun: RunRecord = {
      run_id: 'reconcile-wf-1',
      workflow_id: 't2i_15_lcm',
      status: 'running',
      seq: 1,
    };
    getClientInternalsWithMethods(client).applyEvent(initialRun);

    makeFetchMock(async (url: string) => {
      if (url.endsWith('/run/reconcile-wf-1/status')) {
        return {
          ok: true,
          json: async () => ({
            run_id: 'reconcile-wf-1',
            workflow_id: 't2i_15_lcm',
            status: 'succeeded',
            seq: 3,
            result: { ok: true },
          }),
        };
      }
      return { ok: false };
    });

    getClientInternalsWithMethods(client).reconcileRun('reconcile-wf-1');
    // Wait for the inflight promise to complete
    const promise = getClientInternalsWithMethods(client).inflightReconciles.get('reconcile-wf-1');
    if (promise) await promise;

    const reconciled = getClientInternalsWithMethods(client).runs.get('reconcile-wf-1');
    expect(reconciled.workflow_id).toBe('t2i_15_lcm');
    expect(reconciled.status).toBe('succeeded');
    expect(reconciled.seq).toBe(3);
  });
});
