import { describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { WorkflowRunStatus } from '../types/api';
import { QueuePayload } from '../types/client';

const store = createWorkflowRunnerStore(initState());

describe('WorkflowRunnerClient queue handling', () => {
  it('calls queueHandler with pending/running and does not call applyEvent', () => {
    const client = new WorkflowRunnerClient(store);
    const spyQueue = vi.fn();
    client.queueHandler = spyQueue;

    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    const payload: QueuePayload = { type: 'queue_status', pending: 3, running: 1 };
    client.handleQueuePayload(payload);

    expect(spyQueue).toHaveBeenCalledWith(3, 1);
    expect(consoleWarn).toHaveBeenCalledTimes(0);

    consoleWarn.mockRestore();
  });
  //#endregion

  //#region applyEvent
  it('falls back to applyEvent for run-like payloads', () => {
    const client = new WorkflowRunnerClient(store);

    const ev: QueuePayload = { run_id: 'r-q', status: 'pending' as WorkflowRunStatus, seq: 1 };
    client.handleQueuePayload(ev);

    expect(client.getRuns().get('r-q')?.status).toBe('pending');
    expect(client.getLastSeq().get('r-q')).toBe(1);
  });
  //#endregion
});
