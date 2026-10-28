import { beforeEach, describe, expect, it, vi } from 'vitest';

import { CustomWidgetName, NodeName } from '../types/widgets/widgets';
import { LFWidgets } from './widgets';
import { NODE_WIDGET_MAP } from '../helpers/manager';
import { compareFactory } from '../widgets/compare';
import { countBarChartFactory } from '../widgets/countBarChart';
import { masonryFactory } from '../widgets/masonry';
import { treeFactory } from '../widgets/tree';

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

describe('region comparison result views', () => {
  const dataset = { nodes: [{ id: 'surface', value: 'surface: 0.75' }] };
  const datasets = { chart: dataset, chip: dataset };
  const payload = { dataset, datasets };
  const factories = {
    [CustomWidgetName.compare]: compareFactory,
    [CustomWidgetName.countBarChart]: countBarChartFactory,
    [CustomWidgetName.masonry]: masonryFactory,
    [CustomWidgetName.tree]: treeFactory,
  };

  it.each([
    [NodeName.textRegionMasks, CustomWidgetName.compare, CustomWidgetName.masonry],
    [NodeName.regionColorStats, CustomWidgetName.compare, CustomWidgetName.countBarChart],
    [NodeName.regionFeatureSimilarity, CustomWidgetName.countBarChart, CustomWidgetName.tree],
    [NodeName.visionPatchEncode, CustomWidgetName.compare, CustomWidgetName.masonry],
  ])('hydrates %s live and cached, including a map-only alternative', (name, inputType, alternative) => {
    const mapping = NODE_WIDGET_MAP[name];
    try {
      for (const selected of [inputType, alternative]) {
        NODE_WIDGET_MAP[name] = [selected];
        const previous = vi.fn((_output: unknown) => 'previous result');
        const node = { comfyClass: name, id: 641, onExecuted: previous };
        mocks.getNodeById.mockReturnValue(node);
        const factory = vi.spyOn(factories[selected], 'render').mockReturnValue({ widget: {} } as never);
        const widgets = new LFWidgets();
        widgets.render(inputType)(node as never);
        expect(factory).toHaveBeenCalledWith(node);

        const expected = selected === CustomWidgetName.masonry
          ? { ...payload, node: '641' }
          : selected === CustomWidgetName.countBarChart ? datasets : dataset;
        widgets.onEvent(name, new CustomEvent('lf-result', {
          detail: { ...payload, node: '641' },
        }), [selected]);
        expect(mocks.setValue).toHaveBeenLastCalledWith(JSON.stringify(expected));
        mocks.setValue.mockClear();

        expect(node.onExecuted({ lf_output: [payload] } as never)).toBe('previous result');
        expect(mocks.setValue).toHaveBeenLastCalledWith(JSON.stringify(expected));
        expect(previous).toHaveBeenCalledWith({ lf_output: [payload] });
        factory.mockRestore();
      }
    } finally {
      NODE_WIDGET_MAP[name] = mapping;
    }
  });

  it('retains grids from every mapped encoder execution and names missing history', () => {
    const node = { comfyClass: NodeName.visionPatchEncode, id: 650, onExecuted: vi.fn() };
    mocks.getNodeById.mockReturnValue(node);
    vi.spyOn(compareFactory, 'render').mockReturnValue({ widget: {} } as never);
    new LFWidgets().render(CustomWidgetName.compare)(node as never);
    node.onExecuted({ lf_output: [payload, payload] });
    const value = JSON.parse(mocks.setValue.mock.lastCall[0]);
    expect(value.nodes.map((item: { id: string }) => item.id)).toEqual(['0:surface', '1:surface']);
    expect(value.nodes[1].value).toContain('Image 2');
    node.onExecuted({});
    expect(mocks.log.mock.lastCall[0]).toContain('missing lf_output widget result');
  });
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
