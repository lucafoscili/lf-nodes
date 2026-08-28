import { beforeEach, describe, expect, it, vi } from 'vitest';

import { LogSeverity } from '../../types/manager/manager';
import {
  ImageEditorColumnId,
  ImageEditorCSS,
  ImageEditorState,
  ImageEditorStatus,
} from '../../types/widgets/imageEditor';
import { handleInterruptForState } from './interrupt';

const mocks = vi.hoisted(() => ({
  log: vi.fn(),
  unescape: vi.fn(),
  update: vi.fn(),
}));

vi.mock('../../utils/common', () => ({
  getApiRoutes: () => ({ json: { update: mocks.update } }),
  getComfyAPI: vi.fn(),
  getLfManager: () => ({
    getManagers: () => ({
      lfFramework: {
        syntax: { json: { unescape: mocks.unescape } },
      },
    }),
    log: mocks.log,
  }),
}));

type EditorHarness = ReturnType<typeof createEditorHarness>;

function createEditorHarness() {
  const statusColumn = {
    id: ImageEditorColumnId.Status,
    title: ImageEditorStatus.Pending,
  };
  const pathColumn = {
    id: ImageEditorColumnId.Path,
    title: 'serialized-session-path',
  };
  const dataset = {
    columns: [statusColumn, pathColumn],
    nodes: [],
  };

  const setSelectedShape = vi.fn(async () => undefined);
  const reset = vi.fn(async () => undefined);
  const getComponents = vi.fn(async () => ({
    navigation: { masonry: { setSelectedShape } },
  }));
  const imageviewer = document.createElement('div') as unknown as HTMLLfImageviewerElement;
  imageviewer.lfDataset = dataset;
  imageviewer.getComponents = getComponents as unknown as HTMLLfImageviewerElement['getComponents'];
  imageviewer.reset = reset as HTMLLfImageviewerElement['reset'];

  const grid = document.createElement('div');
  grid.classList.add(ImageEditorCSS.GridIsInactive);
  const interrupt = document.createElement('button') as unknown as HTMLLfButtonElement;
  const resume = document.createElement('button') as unknown as HTMLLfButtonElement;
  interrupt.lfUiState = 'disabled';
  resume.lfUiState = 'disabled';

  const state = {
    elements: {
      actionButtons: { interrupt, resume },
      controls: {},
      grid,
      imageviewer,
      settings: document.createElement('div'),
    },
  } as unknown as ImageEditorState;

  return {
    dataset,
    getComponents,
    grid,
    imageviewer,
    interrupt,
    pathColumn,
    reset,
    resume,
    setSelectedShape,
    state,
    statusColumn,
  };
}

function expectPendingAndInteractive(harness: EditorHarness) {
  expect(harness.statusColumn.title).toBe(ImageEditorStatus.Pending);
  expect(harness.grid.classList.contains(ImageEditorCSS.GridIsInactive)).toBe(false);
  expect(harness.interrupt.lfUiState).toBe('danger');
  expect(harness.resume.lfUiState).toBe('success');
  expect(harness.getComponents).toHaveBeenCalledTimes(0);
  expect(harness.reset).toHaveBeenCalledTimes(0);
  expect(harness.setSelectedShape).toHaveBeenCalledTimes(0);
}

describe('image editor workflow resume', () => {
  beforeEach(() => {
    vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
      callback(0);
      return 1;
    });
    mocks.unescape.mockReturnValue({
      parsedJSON: { title: 'C:/ComfyUI/temp/context_edit_dataset.json' },
    });
  });

  it('restores pending state and leaves the editor active when the update rejects', async () => {
    const harness = createEditorHarness();
    mocks.update.mockRejectedValueOnce(new Error('write failed'));

    await handleInterruptForState(harness.state);

    expectPendingAndInteractive(harness);
    expect(mocks.log).toHaveBeenCalledWith(
      'Failed to resume the workflow; the editing session remains pending.',
      expect.objectContaining({ path: 'C:/ComfyUI/temp/context_edit_dataset.json' }),
      LogSeverity.Error,
    );
  });

  it('restores pending state and leaves the editor active for a non-success update', async () => {
    const harness = createEditorHarness();
    mocks.update.mockResolvedValueOnce({
      message: 'update rejected',
      status: LogSeverity.Error,
    });

    await handleInterruptForState(harness.state);

    expectPendingAndInteractive(harness);
  });

  it('completes and resets the editor only after a successful update', async () => {
    const harness = createEditorHarness();
    mocks.update.mockResolvedValueOnce({
      message: 'updated',
      status: LogSeverity.Success,
    });

    await handleInterruptForState(harness.state);

    expect(mocks.update).toHaveBeenCalledWith(
      'C:/ComfyUI/temp/context_edit_dataset.json',
      harness.dataset,
    );
    expect(harness.statusColumn.title).toBe(ImageEditorStatus.Completed);
    expect(harness.grid.classList.contains(ImageEditorCSS.GridIsInactive)).toBe(true);
    expect(harness.interrupt.lfUiState).toBe('disabled');
    expect(harness.resume.lfUiState).toBe('disabled');
    expect(harness.getComponents).toHaveBeenCalledOnce();
    expect(harness.reset).toHaveBeenCalledOnce();
    expect(harness.setSelectedShape).toHaveBeenCalledWith(null);
  });
});
