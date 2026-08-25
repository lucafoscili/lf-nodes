import type { WorkflowRunPruneResponse } from '../types/api';
import type { WorkflowStore } from '../types/state';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { removeMissingHistory } from '../handlers/button';

const result = (
  overrides: Partial<WorkflowRunPruneResponse> = {},
): WorkflowRunPruneResponse => ({
  candidate_count: 0,
  candidate_run_ids: [],
  dry_run: true,
  removed_count: 0,
  removed_run_ids: [],
  skipped_changed: 0,
  skipped_unknown: 0,
  ...overrides,
});

const setup = (pruneMissingArtifacts: ReturnType<typeof vi.fn>) => {
  const notifications: Array<{ message: string; status: string }> = [];
  const state = {
    manager: {
      runs: { pruneMissingArtifacts },
    },
    mutate: {
      notifications: {
        add: vi.fn((notification) => notifications.push(notification)),
      },
    },
    view: 'history',
  };
  const store = {
    getState: vi.fn(() => state),
  } as unknown as WorkflowStore;
  const button = document.createElement('lf-button');
  return { button, notifications, store };
};

describe('Remove missing history control', () => {
  let confirmMock: ReturnType<typeof vi.fn<(message?: string) => boolean>>;

  beforeEach(() => {
    confirmMock = vi.fn<(message?: string) => boolean>(() => true);
    vi.stubGlobal('confirm', confirmMock);
  });

  it('reports a zero-result scan without asking for confirmation', async () => {
    const prune = vi.fn().mockResolvedValue(result({ skipped_unknown: 2 }));
    const { button, notifications, store } = setup(prune);

    await removeMissingHistory(button, store);

    expect(confirmMock.mock.calls.length).toBe(0);
    expect(prune).toHaveBeenCalledOnce();
    expect(prune).toHaveBeenCalledWith(true);
    expect(notifications[0].message).toContain('No missing-output or failed runs');
    expect(notifications[0].message).toContain('2 ambiguous or fileless successful runs were preserved');
  });

  it('stops after preview when confirmation is cancelled', async () => {
    confirmMock.mockReturnValue(false);
    const prune = vi.fn().mockResolvedValue(
      result({ candidate_count: 4, candidate_run_ids: ['a', 'b', 'c', 'd'] }),
    );
    const { button, notifications, store } = setup(prune);

    await removeMissingHistory(button, store);

    expect(prune).toHaveBeenCalledTimes(1);
    expect(notifications).toHaveLength(0);
    expect(button.lfShowSpinner).toBe(false);
    expect(button.getAttribute('aria-busy')).toBeNull();
  });

  it('confirms and executes cleanup, then reports preserved records', async () => {
    const prune = vi
      .fn()
      .mockResolvedValueOnce(
        result({ candidate_count: 3, candidate_run_ids: ['a', 'b', 'c'] }),
      )
      .mockResolvedValueOnce(
        result({
          candidate_count: 3,
          candidate_run_ids: ['a', 'b', 'c'],
          dry_run: false,
          removed_count: 2,
          removed_run_ids: ['a', 'b'],
          skipped_changed: 1,
          skipped_unknown: 5,
        }),
      );
    const { button, notifications, store } = setup(prune);

    await removeMissingHistory(button, store);

    expect(confirmMock.mock.calls[0]?.[0]).toContain('never deletes files');
    expect(prune.mock.calls).toEqual([[true], [false, ['a', 'b', 'c']]]);
    expect(notifications[0].message).toContain('Removed 2 stale runs');
    expect(notifications[0].message).toContain('5 ambiguous or fileless successful runs were preserved');
    expect(notifications[0].message).toContain('1 run changed during cleanup');
    expect(button.lfLabel).toBe('Remove missing');
    expect(button.lfUiState).toBe('danger');
  });

  it('shows an error and restores the control', async () => {
    const prune = vi.fn().mockRejectedValue(new Error('Server unavailable'));
    const { button, notifications, store } = setup(prune);

    await removeMissingHistory(button, store);

    expect(notifications[0]).toEqual(
      expect.objectContaining({ message: expect.stringContaining('Server unavailable'), status: 'danger' }),
    );
    expect(button.lfShowSpinner).toBe(false);
    expect(button.lfUiState).toBe('danger');
  });

  it('blocks repeated clicks while the scan is pending', async () => {
    let resolvePreview: ((value: WorkflowRunPruneResponse) => void) | undefined;
    const preview = new Promise<WorkflowRunPruneResponse>((resolve) => {
      resolvePreview = resolve;
    });
    const prune = vi.fn(() => preview);
    const { button, store } = setup(prune);

    const first = removeMissingHistory(button, store);
    const second = removeMissingHistory(button, store);

    expect(prune).toHaveBeenCalledOnce();
    expect(button.lfShowSpinner).toBe(true);
    expect(button.lfUiState).toBe('disabled');
    expect(button.getAttribute('aria-busy')).toBe('true');

    resolvePreview?.(result());
    await Promise.all([first, second]);
  });
});
