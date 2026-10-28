import { describe, expect, it, vi } from 'vitest';
import { NodeName } from '../types/widgets/widgets';
import { compareFactory } from './compare';

vi.mock('../utils/common', () => ({
  createDOMWidget: (_name: string, element: HTMLDivElement, _node: unknown, options: unknown) =>
    ({ element, options }),
  normalizeValue: (value: string, callback: (value: string, parsed: unknown) => void) =>
    callback(value, { parsedJSON: JSON.parse(value) }),
}));

describe('regional compare summaries', () => {
  it.each([NodeName.textRegionMasks, NodeName.regionColorStats, NodeName.visionPatchEncode])(
    '%s keeps labels visible without opening image selectors and restores them from saved state',
    (comfyClass) => {
      const { widget } = compareFactory.render({ comfyClass } as never);
      const dataset = { nodes: [{ id: 'surface', value: 'surface | DE00 2.000', cells: {
        lfImage: { shape: 'image', lfValue: '/view?type=input&filename=preview.png', value: 'surface A' },
      } }] };
      widget.options.setValue(JSON.stringify(dataset));
      const summary = widget.element.querySelector('lf-tree') as HTMLLfTreeElement;
      expect(summary.lfDataset).toEqual({ nodes: [{ id: 'surface', value: 'surface | DE00 2.000' }] });
      expect(summary.lfStyle).toContain('white-space: normal');
      expect(widget.options.getValue()).toEqual(dataset);
    },
  );

  it('keeps the existing generic Compare widget layout', () => {
    const { widget } = compareFactory.render({ comfyClass: NodeName.compareImages } as never);
    expect(widget.element.querySelector('lf-tree')).toBeNull();
  });
});
