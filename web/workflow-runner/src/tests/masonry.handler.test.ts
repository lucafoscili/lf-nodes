import { describe, expect, it, vi } from 'vitest';
import { masonryClickFallback } from '../handlers/masonry';
import { WorkflowStore } from '../types/state';

const createStore = (selectedRunId: string | null = null) => {
  const select = vi.fn();
  const knownRunIds = new Set(['run-1']);
  const state = {
    manager: {
      runs: {
        get: vi.fn((runId: string) => (knownRunIds.has(runId) ? { runId } : null)),
        select,
        selected: vi.fn(() => (selectedRunId ? { runId: selectedRunId } : null)),
      },
    },
  };
  return {
    select,
    store: { getState: vi.fn(() => state) } as unknown as WorkflowStore,
  };
};

const cardClick = (runId?: string) => {
  const child = document.createElement('span');
  const card = document.createElement('lf-card') as HTMLLfCardElement;
  card.lfDataset = {
    nodes: [
      {
        cells: {},
        id: runId ?? '',
      },
    ],
  };
  return {
    composedPath: () => [child, card],
  } as unknown as MouseEvent;
};

describe('masonryClickFallback', () => {
  it('opens a result from the composed native card click', () => {
    const { select, store } = createStore();

    masonryClickFallback(cardClick('run-1'), store);

    expect(select).toHaveBeenCalledWith('run-1', 'run');
  });

  it('does not duplicate a selection already handled by the LFW custom event', () => {
    const { select, store } = createStore('run-1');

    masonryClickFallback(cardClick('run-1'), store);

    expect(select).toHaveBeenCalledTimes(0);
  });

  it.each(['', 'empty-card', 'stale-run'])(
    'ignores native clicks that do not resolve to a current run (%s)',
    (runId) => {
      const { select, store } = createStore();

      masonryClickFallback(cardClick(runId), store);

      expect(select).toHaveBeenCalledTimes(0);
    },
  );
});
