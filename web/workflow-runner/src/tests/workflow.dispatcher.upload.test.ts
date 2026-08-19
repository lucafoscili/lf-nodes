import { beforeEach, describe, expect, it, vi } from 'vitest';
import { addNotification } from '../app/store-actions';
import { workflowDispatcher } from '../dispatchers/workflow';
import { INPUTS_CLASSES } from '../elements/main.inputs';
import { runWorkflow, uploadWorkflowFiles } from '../services/workflow-service';
import { WorkflowStore } from '../types/state';

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
    uploadWorkflowFiles: vi.fn(async () => ({ payload: { paths: ['identity.png'] } })),
    WorkflowApiError,
  };
});

vi.mock('../utils/debug', () => ({ debugLog: vi.fn() }));

const createStore = (sceneRequired: boolean) => {
  const scene = document.createElement('lf-upload') as HTMLLfUploadElement;
  scene.id = 'scene_image';
  scene.getValue = vi.fn(async () => []);
  if (!sceneRequired) scene.dataset.required = 'false';

  const identity = document.createElement('lf-upload') as HTMLLfUploadElement;
  identity.id = 'identity_image';
  identity.getValue = vi.fn(async () => [new File(['identity'], 'identity.png')]);

  const state = {
    current: { id: 'image_identity_edit', message: null, status: 'idle' },
    manager: {
      uiRegistry: {
        get: vi.fn(() => ({ [INPUTS_CLASSES.cells]: [scene, identity] })),
      },
      workflow: { title: vi.fn(() => 'Image Identity Edit') },
    },
    mutate: { inputStatus: vi.fn() },
  };

  return { store: { getState: vi.fn(() => state) } as unknown as WorkflowStore };
};

describe('workflowDispatcher upload requiredness', () => {
  beforeEach(() => vi.clearAllMocks());

  it('omits an empty optional upload while submitting the required identity', async () => {
    const { store } = createStore(false);

    await workflowDispatcher(store);

    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(1);
    expect(runWorkflow).toHaveBeenCalledWith({
      workflowId: 'image_identity_edit',
      inputs: { identity_image: 'identity.png' },
    });
    expect(addNotification).toHaveBeenCalledTimes(0);
  });

  it('retains fail-closed behavior for an empty required upload', async () => {
    const { store } = createStore(true);

    await workflowDispatcher(store);

    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(0);
    expect(runWorkflow).toHaveBeenCalledTimes(0);
    expect(addNotification).toHaveBeenCalledWith(
      store,
      expect.objectContaining({ message: 'Failed to collect inputs: No files selected for upload.' }),
    );
  });
});
