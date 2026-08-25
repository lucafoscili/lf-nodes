import { beforeEach, describe, expect, it, vi } from 'vitest';
import { addNotification, upsertRun } from '../app/store-actions';
import { workflowDispatcher } from '../dispatchers/workflow';
import { INPUTS_CLASSES } from '../elements/main.inputs';
import { runWorkflow, uploadWorkflowFiles } from '../services/workflow-service';
import { WorkflowStore } from '../types/state';
import { setRetainedUploadPrefill } from '../utils/input-prefill';

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
      submissionId: expect.stringMatching(/^lf-web:/),
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

  it('reuses a retained upload on remix without uploading its bytes again', async () => {
    const { store } = createStore(true);
    const registry = store.getState().manager.uiRegistry.get() as unknown as Record<
      string,
      HTMLElement[]
    >;
    const cells = registry[INPUTS_CLASSES.cells];
    setRetainedUploadPrefill(cells[0], {
      schema: 'lf.workflow-upload-prefill.v1',
      reference: {
        schema: 'lf.workflow-upload-ref.v1',
        sourceRunId: 'run-source',
        inputId: 'scene_image',
      },
      names: ['scene.png'],
      available: true,
    });

    await workflowDispatcher(store);

    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(1);
    expect(runWorkflow).toHaveBeenCalledWith({
      workflowId: 'image_identity_edit',
      inputs: {
        scene_image: {
          schema: 'lf.workflow-upload-ref.v1',
          sourceRunId: 'run-source',
          inputId: 'scene_image',
        },
        identity_image: 'identity.png',
      },
      submissionId: expect.stringMatching(/^lf-web:/),
    });
    expect(upsertRun).toHaveBeenCalledWith(
      store,
      expect.objectContaining({ runId: 'run-1', inputs: {} }),
    );
  });

  it('requires reselection when a retained required upload has expired', async () => {
    const { store } = createStore(true);
    const registry = store.getState().manager.uiRegistry.get() as unknown as Record<
      string,
      HTMLElement[]
    >;
    setRetainedUploadPrefill(registry[INPUTS_CLASSES.cells][0], {
      schema: 'lf.workflow-upload-prefill.v1',
      reference: {
        schema: 'lf.workflow-upload-ref.v1',
        sourceRunId: 'run-source',
        inputId: 'scene_image',
      },
      names: ['expired.png'],
      available: false,
    });

    await workflowDispatcher(store);

    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(0);
    expect(runWorkflow).toHaveBeenCalledTimes(0);
    expect(addNotification).toHaveBeenCalledWith(
      store,
      expect.objectContaining({
        message:
          'Failed to collect inputs: The previous upload is no longer available. Choose the file again.',
      }),
    );
  });

  it('requires reselection when a retained optional upload has expired', async () => {
    const { store } = createStore(false);
    const registry = store.getState().manager.uiRegistry.get() as unknown as Record<
      string,
      HTMLElement[]
    >;
    setRetainedUploadPrefill(registry[INPUTS_CLASSES.cells][0], {
      schema: 'lf.workflow-upload-prefill.v1',
      reference: {
        schema: 'lf.workflow-upload-ref.v1',
        sourceRunId: 'run-source',
        inputId: 'scene_image',
      },
      names: ['expired-optional.png'],
      available: false,
    });

    await workflowDispatcher(store);

    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(0);
    expect(runWorkflow).toHaveBeenCalledTimes(0);
    expect(addNotification).toHaveBeenCalledWith(
      store,
      expect.objectContaining({
        message:
          'Failed to collect inputs: The previous upload is no longer available. Choose the file again.',
      }),
    );
  });

  it('lets a fresh selection replace the retained reference', async () => {
    const { store } = createStore(true);
    const registry = store.getState().manager.uiRegistry.get() as unknown as Record<
      string,
      HTMLLfUploadElement[]
    >;
    const cells = registry[INPUTS_CLASSES.cells];
    setRetainedUploadPrefill(cells[0], {
      schema: 'lf.workflow-upload-prefill.v1',
      reference: {
        schema: 'lf.workflow-upload-ref.v1',
        sourceRunId: 'run-source',
        inputId: 'scene_image',
      },
      names: ['old-scene.png'],
      available: true,
    });
    cells[0].getValue = vi.fn(async () => [new File(['fresh'], 'fresh-scene.png')]);
    vi.mocked(uploadWorkflowFiles).mockImplementation(async (files: File[]) => ({
      payload: { paths: [files[0].name] },
    }) as any);

    await workflowDispatcher(store);

    expect(uploadWorkflowFiles).toHaveBeenCalledTimes(2);
    expect(runWorkflow).toHaveBeenCalledWith({
      workflowId: 'image_identity_edit',
      inputs: {
        scene_image: 'fresh-scene.png',
        identity_image: 'identity.png',
      },
      submissionId: expect.stringMatching(/^lf-web:/),
    });
  });

  it('uses one stable submission id and ignores accidental re-entry', async () => {
    const { store } = createStore(false);
    let resolveRun: ((runId: string) => void) | undefined;
    vi.mocked(runWorkflow).mockReturnValueOnce(
      new Promise<string>((resolve) => {
        resolveRun = resolve;
      }) as any,
    );

    const firstClick = workflowDispatcher(store);
    await vi.waitFor(() => expect(runWorkflow).toHaveBeenCalledTimes(1));
    await workflowDispatcher(store);

    expect(runWorkflow).toHaveBeenCalledTimes(1);
    const request = vi.mocked(runWorkflow).mock.calls[0][0];
    expect(request.submissionId).toMatch(/^lf-web:/);

    resolveRun?.('run-stable');
    await firstClick;
    expect(upsertRun).toHaveBeenCalledWith(
      store,
      expect.objectContaining({
        runId: 'run-stable',
        submissionId: request.submissionId,
      }),
    );
  });
});
