import { describe, expect, it } from 'vitest';
import { protectDOMWidgetWidth } from './domWidget';

describe('protectDOMWidgetWidth', () => {
  it('ignores sidebar width writes so the canvas can fall back to node width', () => {
    const widget: { width?: number } = {};

    protectDOMWidgetWidth(widget);
    widget.width = 228;

    expect(widget.width).toBeUndefined();
  });

  it('preserves unrelated widget state', () => {
    const widget = {
      name: 'ui_widget',
      value: { nodes: [] as unknown[] },
      width: undefined as number | undefined,
    };

    expect(protectDOMWidgetWidth(widget)).toBe(widget);
    expect(widget).toMatchObject({ name: 'ui_widget', value: { nodes: [] } });
  });

  it('does not add an enumerable key to legacy widgets without width', () => {
    const widget: { width?: number } = {};

    protectDOMWidgetWidth(widget);

    expect(Object.keys(widget).includes('width')).toBe(false);
  });

  it('fails open for a non-configurable width descriptor', () => {
    const widget: { width?: number } = {};
    Object.defineProperty(widget, 'width', {
      configurable: false,
      value: 320,
      writable: true,
    });

    protectDOMWidgetWidth(widget);
    widget.width = 228;

    expect(widget.width).toBe(228);
  });

  it('fails open for non-extensible host widget objects', () => {
    const widget = Object.preventExtensions({}) as { width?: number };

    protectDOMWidgetWidth(widget);
    expect(widget.width).toBeUndefined();
  });
});
