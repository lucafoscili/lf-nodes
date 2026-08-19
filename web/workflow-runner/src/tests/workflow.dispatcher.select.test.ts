import { beforeEach, describe, expect, it, vi } from 'vitest';
import { runWorkflow } from '../services/workflow-service';
import { WorkflowStore } from '../types/state';
import { workflowDispatcher } from '../dispatchers/workflow';
import { INPUTS_CLASSES } from '../elements/main.inputs';

vi.mock('../app/store-actions', () => ({
  addNotification: vi.fn(),
  clearResults: vi.fn(),
  ensureActiveRun: vi.fn(),
  setStatus: vi.fn(),
  upsertRun: vi.fn(),
}));

vi.mock('../services/workflow-service', () => {
  class WorkflowApiError extends Error {
    payload?: unknown;
    status?: number;
  }

  return {
    runWorkflow: vi.fn(async () => 'run-1'),
    uploadWorkflowFiles: vi.fn(),
    WorkflowApiError,
  };
});

vi.mock('../utils/debug', () => ({
  debugLog: vi.fn(),
}));

const createStore = (selected: {
  id: string;
  value?: string | number;
  workflowValue?: string | number;
}) => {
  const select = document.createElement('lf-select') as HTMLLfSelectElement;
  select.id = 'sampler';
  select.getValue = vi.fn(async () => selected);

  const inputStatus = vi.fn();
  const state = {
    current: { id: 'qwen-edit', message: null, status: 'idle' },
    manager: {
      uiRegistry: {
        get: vi.fn(() => ({
          [INPUTS_CLASSES.cells]: [select],
        })),
      },
      workflow: {
        title: vi.fn(() => 'Qwen Edit'),
      },
    },
    mutate: { inputStatus },
  };

  return {
    inputStatus,
    store: { getState: vi.fn(() => state) } as unknown as WorkflowStore,
  };
};

describe('workflowDispatcher select inputs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it.each([
    ['uses an explicit workflow value behind a friendly label', { id: 'cover', value: 'Cover', workflowValue: 'cover' }, 'cover'],
    ['uses the selected semantic value', { id: 'sampler-euler', value: 'euler' }, 'euler'],
    ['preserves a numeric zero value', { id: 'first-option', value: 0 }, 0],
    ['falls back to the selected node id', { id: 'sampler-euler' }, 'sampler-euler'],
  ])('%s', async (_label, selected, expected) => {
    const { inputStatus, store } = createStore(selected);

    await workflowDispatcher(store);

    expect(runWorkflow).toHaveBeenCalledWith({
      workflowId: 'qwen-edit',
      inputs: { sampler: expected },
    });
    expect(inputStatus).toHaveBeenCalledWith('sampler', '');
  });
});
