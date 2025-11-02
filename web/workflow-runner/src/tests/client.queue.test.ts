import { describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';

describe('WorkflowRunnerClient queue handling', () => {
  it('calls queueHandler with pending/running and does not call applyEvent', () => {
    const client = new WorkflowRunnerClient();
    const spyQueue = vi.fn();
    (client as any).setQueueHandler(spyQueue);

    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    // Simulate a queue_status payload from SSE
    const payload = { type: 'queue_status', pending: 3, running: 1 };
    (client as any).handleQueuePayload(payload);

    expect(spyQueue).toHaveBeenCalledWith(3, 1);
    // ensure no invalid-run warnings
    expect(consoleWarn).toHaveBeenCalledTimes(0);

    consoleWarn.mockRestore();
  });

  it('falls back to applyEvent for run-like payloads', () => {
    const client = new WorkflowRunnerClient();

    const ev = { run_id: 'r-q', status: 'pending', seq: 1 };
    (client as any).handleQueuePayload(ev);

    expect((client as any).runs.get('r-q').status).toBe('pending');
    expect((client as any).lastSeq.get('r-q')).toBe(1);
  });
});
