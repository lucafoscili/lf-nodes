import { beforeEach, describe, expect, it, vi } from 'vitest';

import { CustomWidgetName, NodeName } from '../types/widgets/widgets';
import { LFWidgets } from './widgets';

const mocks = vi.hoisted(() => ({
  getJson: vi.fn(),
  getNodeById: vi.fn(),
  log: vi.fn(),
  redraw: vi.fn(),
  setValue: vi.fn(),
}));

vi.mock('../utils/common', () => ({
  getApiRoutes: () => ({ json: { get: mocks.getJson } }),
  getCustomWidget: () => ({
    options: {
      getState: () => undefined,
      setValue: mocks.setValue,
    },
  }),
  getLfManager: () => ({
    getApiRoutes: () => ({
      comfy: { getNodeById: mocks.getNodeById, redraw: mocks.redraw },
    }),
    log: mocks.log,
  }),
  resolveNodeId: (payload: { node?: string }) => payload.node ?? null,
}));

beforeEach(() => {
  mocks.getJson.mockReset();
  mocks.getNodeById.mockReset();
  mocks.log.mockReset();
  mocks.redraw.mockReset();
  mocks.setValue.mockReset();
});

describe('image editor live-event hydration', () => {
  it('hydrates LF_LoadAndEditImages from the emitted value context path', async () => {
    const node = { comfyClass: NodeName.loadAndEditImages, id: 73 };
    const dataset = {
      columns: [],
      context_id: 'C:/ComfyUI/temp/loader-context.json',
      nodes: [],
      owner_client_id: 'server-owner',
    };
    mocks.getNodeById.mockReturnValue(node);
    mocks.getJson.mockResolvedValue({ data: dataset, status: 'success' });

    new LFWidgets().onEvent(
      NodeName.loadAndEditImages,
      new CustomEvent('lf-loadandeditimages', {
        detail: { node: '73', value: dataset.context_id },
      }) as never,
      [CustomWidgetName.imageEditor],
    );

    await vi.waitFor(() => {
      expect(mocks.getJson).toHaveBeenCalledWith(dataset.context_id);
      expect(mocks.setValue).toHaveBeenCalledWith(JSON.stringify(dataset));
    });
  });

  it('hydrates LF_ImagesEditingBreakpoint from its targeted context event', async () => {
    const node = { comfyClass: NodeName.imagesEditingBreakpoint, id: 463 };
    const dataset = {
      columns: [{ id: 'status', title: 'pending' }],
      context_id: 'C:/ComfyUI/temp/breakpoint-context.json',
      nodes: [],
      owner_client_id: 'server-owner',
    };
    mocks.getNodeById.mockReturnValue(node);
    mocks.getJson.mockResolvedValue({ data: dataset, status: 'success' });

    new LFWidgets().onEvent(
      NodeName.imagesEditingBreakpoint,
      new CustomEvent('lf-imageseditingbreakpoint', {
        detail: { node: '463', value: dataset.context_id },
      }) as never,
      [CustomWidgetName.imageEditor],
    );

    await vi.waitFor(() => {
      expect(mocks.getJson).toHaveBeenCalledWith(dataset.context_id);
      expect(mocks.setValue).toHaveBeenCalledWith(JSON.stringify(dataset));
    });
  });
});
