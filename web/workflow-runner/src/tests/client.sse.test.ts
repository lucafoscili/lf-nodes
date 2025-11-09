import './setup';
import { TestEventSource, makeFetchMock, wait, getClientInternalsWithMethods } from './_utils';
import { describe, expect, it } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient - SSE and snapshot processing', () => {
  it('start() merges initial SSE snapshot (message/run) into state', async () => {
    const client = new WorkflowRunnerClient(store);

    // Mock coldLoadRuns to be empty (server snapshot via SSE will provide data)
    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs')) {
        return { ok: true, json: async () => ({ runs: [] }) };
      }
      return { ok: false };
    });

    // Start client (will call coldLoadRuns and then create EventSource)
    await getClientInternalsWithMethods(client).start();

    // There should be one TestEventSource instance created by the global mock
    const es = TestEventSource.instances[TestEventSource.instances.length - 1];
    expect(es).toBeDefined();

    // Simulate server sending an initial snapshot as generic messages
    const msg1 = { run_id: 'sse1', status: 'succeeded', seq: 1, updated_at: 1111 };
    const msg2 = { run_id: 'sse2', status: 'pending', seq: 2, updated_at: 2222 };

    es.sendMessage(msg1);
    es.sendMessage(msg2);

    // allow processing microtasks
    await wait(10);

    expect(getClientInternalsWithMethods(client).runs.get('sse1').status).toBe('succeeded');
    expect(getClientInternalsWithMethods(client).runs.get('sse2').status).toBe('pending');

    // Also simulate server sending a 'run' event for another run
    const runEvt = { run_id: 'sse3', status: 'running', seq: 3, updated_at: 3333 };
    es.sendRun('run', runEvt);

    await wait(10);
    expect(getClientInternalsWithMethods(client).runs.get('sse3').status).toBe('running');

    // cleanup: TestEventSource is reset by tests or teardown; no global deletion required
  });

  it('processSnapshotArray ignores older snapshot entries when local seq is higher', async () => {
    const client = new WorkflowRunnerClient(store);
    // seed with a newer local seq
    getClientInternalsWithMethods(client).lastSeq.set('r_old', 5);
    getClientInternalsWithMethods(client).runs.set('r_old', {
      run_id: 'r_old',
      status: 'running',
      seq: 5,
    });

    // snapshot contains older seq (3) — should be ignored
    getClientInternalsWithMethods(client).processSnapshotArray([
      { run_id: 'r_old', status: 'succeeded', seq: 3 },
    ]);
    expect(getClientInternalsWithMethods(client).lastSeq.get('r_old')).toBe(5);
    expect(getClientInternalsWithMethods(client).runs.get('r_old').status).toBe('running');
  });

  it('processSnapshotArray accepts snapshot entries with higher seq', async () => {
    const client = new WorkflowRunnerClient(store);
    getClientInternalsWithMethods(client).lastSeq.set('r_up', 2);
    getClientInternalsWithMethods(client).runs.set('r_up', {
      run_id: 'r_up',
      status: 'pending',
      seq: 2,
    });

    getClientInternalsWithMethods(client).processSnapshotArray([
      { run_id: 'r_up', status: 'succeeded', seq: 3 },
    ]);

    expect(getClientInternalsWithMethods(client).lastSeq.get('r_up')).toBe(3);
    expect(getClientInternalsWithMethods(client).runs.get('r_up').status).toBe('succeeded');
  });

  it('start() clears processingSnapshot after receiving initial messages', async () => {
    const client = new WorkflowRunnerClient(store);

    makeFetchMock(async (url: string) => {
      if (url.includes('/workflow-runner/runs'))
        return { ok: true, json: async () => ({ runs: [] }) };
      return { ok: false };
    });

    // start() sets processingSnapshot = true initially
    await getClientInternalsWithMethods(client).start();
    expect(getClientInternalsWithMethods(client).processingSnapshot).toBe(true);

    // Find the created TestEventSource instance
    const esInst = TestEventSource.instances[TestEventSource.instances.length - 1];
    expect(esInst).toBeDefined();

    // call sendMessage to simulate message
    esInst.sendMessage({ run_id: 'm1', status: 'succeeded', seq: 1 });

    await wait(10);
    expect(getClientInternalsWithMethods(client).processingSnapshot).toBe(false);
  });
});
