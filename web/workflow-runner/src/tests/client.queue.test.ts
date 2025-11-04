import { describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';

const store = createWorkflowRunnerStore(initState());

describe('WorkflowRunnerClient queue handling', () => {
  //#region queueHandler tests
  it('calls queueHandler with pending/running and does not call applyEvent', () => {
    const client = new WorkflowRunnerClient(store);
    const spyQueue = vi.fn();
    // use public API: assign to the public `queueHandler` field
    client.queueHandler = spyQueue;

    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    const payload = { type: 'queue_status', pending: 3, running: 1 };
    client.handleQueuePayload(payload);

    expect(spyQueue).toHaveBeenCalledWith(3, 1);
    expect(consoleWarn).toHaveBeenCalledTimes(0);

    consoleWarn.mockRestore();
  });
  //#endregion

  //#region applyEvent
  it('falls back to applyEvent for run-like payloads', () => {
    const client = new WorkflowRunnerClient(store);

    const ev = { run_id: 'r-q', status: 'pending', seq: 1 };
    client.handleQueuePayload(ev);

    // Use the explicit test getters on the client rather than poking internals
    expect(client.getRuns().get('r-q')?.status).toBe('pending');
    expect(client.getLastSeq().get('r-q')).toBe(1);
  });
  //#endregion
});
