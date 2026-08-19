import { describe, expect, it, vi } from 'vitest';
import { hookDOMWidgetSerialization, sanitizeSerializedValue } from './serialization';

const image = 'data:image/png;base64,AAAA';

describe('sanitizeSerializedValue', () => {
  it('sanitizes nested image data without changing ordinary values', () => {
    const value = {
      nested: [
        {
          preview: image,
          metadataPreview: 'data:image/png;charset=utf-8;base64,BBBB',
          hash: '#abc123',
          path: '/tmp/image.png',
        },
      ],
      text: 'data:text/plain;base64,keep-me',
    };

    const sanitized = sanitizeSerializedValue(value);

    expect(sanitized).toEqual({
      nested: [{ preview: '', metadataPreview: '', hash: '#abc123', path: '/tmp/image.png' }],
      text: 'data:text/plain;base64,keep-me',
    });
    expect(Object.is(sanitized, value)).toBe(false);
    expect(value.nested[0].preview).toBe(image);
  });

  it('preserves cycles in the cloned value', () => {
    const value: { self?: unknown; preview: string } = { preview: image };
    value.self = value;

    const sanitized = sanitizeSerializedValue(value);

    expect(sanitized.preview).toBe('');
    expect(sanitized.self).toBe(sanitized);
    expect(Object.is(sanitized, value)).toBe(false);
  });

  it('fails open when a serialized value cannot be cloned', () => {
    const value = Object.defineProperty({ preview: image }, 'broken', {
      enumerable: true,
      get() {
        throw new Error('host failure');
      },
    });

    expect(sanitizeSerializedValue(value)).toBe(value);
  });

  it('preserves a serialized __proto__ key as data', () => {
    const value = JSON.parse(
      '{"__proto__":{"preview":"data:image/png;base64,AAAA","hash":"#keep"}}',
    ) as Record<string, unknown>;

    const sanitized = sanitizeSerializedValue(value) as Record<string, unknown>;

    expect(Object.prototype.hasOwnProperty.call(sanitized, '__proto__')).toBe(true);
    expect(sanitized.__proto__).toEqual({ preview: '', hash: '#keep' });
    expect(Object.getPrototypeOf(sanitized)).toBe(Object.prototype);
  });
});

describe('hookDOMWidgetSerialization', () => {
  it('sanitizes prompt and exact workflow entries while preserving prior hooks', () => {
    const prior = vi.fn();
    const liveValue = { preview: image, hash: '#preserve' };
    const widget = {
      name: 'ui_widget',
      value: liveValue,
      serializeValue: undefined,
    } as unknown as Widget<any>;
    const node = {
      widgets: [widget],
      onSerialize: prior,
    } as unknown as NodeType;

    hookDOMWidgetSerialization(node, widget);

    expect(widget.serializeValue()).toEqual({ preview: '', hash: '#preserve' });
    expect(liveValue.preview).toBe(image);

    const data = {
      widgets_values: [{ preview: image }],
      widgets_values_named: {
        ui_widget: { preview: image },
        other: { preview: image },
      },
    };
    node.onSerialize(data);

    expect(prior).toHaveBeenCalledOnce();
    expect(data.widgets_values[0]).toEqual({ preview: '' });
    expect(data.widgets_values_named.ui_widget).toEqual({ preview: '' });
    expect(data.widgets_values_named.other).toEqual({ preview: image });
  });

  it('does not double-wrap a node when another LF widget is hooked', () => {
    const widget = (name: string) =>
      ({ name, value: { preview: image } } as unknown as Widget<any>);
    const first = widget('first');
    const second = widget('second');
    const node = { widgets: [first, second] } as unknown as NodeType;

    hookDOMWidgetSerialization(node, first);
    const wrapper = node.onSerialize;
    hookDOMWidgetSerialization(node, second);

    expect(node.onSerialize).toBe(wrapper);
    const data = {
      widgets_values: [{ preview: image }, { preview: image }],
      widgets_values_named: { first: { preview: image }, second: { preview: image } },
    };
    node.onSerialize(data);
    expect(data.widgets_values).toEqual([{ preview: '' }, { preview: '' }]);
    expect(data.widgets_values_named).toEqual({ first: { preview: '' }, second: { preview: '' } });
  });

  it('preserves an intentionally sparse positional widget slot', () => {
    const leading = { name: 'leading', value: 'keep' } as unknown as Widget<any>;
    const widget = { name: 'ui_widget', value: { preview: image } } as unknown as Widget<any>;
    const node = { widgets: [leading, widget] } as unknown as NodeType;
    const widgetsValues = new Array(2);
    widgetsValues[0] = 'keep';

    hookDOMWidgetSerialization(node, widget);
    const data = {
      widgets_values: widgetsValues,
      widgets_values_named: { ui_widget: { preview: image } },
    };
    node.onSerialize(data);

    expect(Object.prototype.hasOwnProperty.call(data.widgets_values, 1)).toBe(false);
    expect(data.widgets_values).toHaveLength(2);
    expect(data.widgets_values_named.ui_widget).toEqual({ preview: '' });
  });

  it('sanitizes async serializeValue results without changing sync results', async () => {
    const asyncWidget = {
      name: 'async_widget',
      value: { preview: image },
      serializeValue: async () => ({ preview: image }),
    } as unknown as Widget<any>;
    const syncWidget = {
      name: 'sync_widget',
      value: { preview: image },
      serializeValue: () => ({ preview: image }),
    } as unknown as Widget<any>;
    const node = { widgets: [asyncWidget, syncWidget] } as unknown as NodeType;

    hookDOMWidgetSerialization(node, asyncWidget);
    hookDOMWidgetSerialization(node, syncWidget);

    const asyncResult = asyncWidget.serializeValue();
    expect(asyncResult).toBeInstanceOf(Promise);
    await expect(asyncResult).resolves.toEqual({ preview: '' });
    expect(syncWidget.serializeValue()).toEqual({ preview: '' });
  });

  it('re-chains a later onSerialize replacement while retaining all LF widgets', () => {
    const first = { name: 'first', value: { preview: image } } as unknown as Widget<any>;
    const second = { name: 'second', value: { preview: image } } as unknown as Widget<any>;
    const node = { widgets: [first, second] } as unknown as NodeType;
    const replacement = vi.fn();

    hookDOMWidgetSerialization(node, first);
    node.onSerialize = replacement;
    hookDOMWidgetSerialization(node, second);

    const data = {
      widgets_values: [{ preview: image }, { preview: image }],
      widgets_values_named: { first: { preview: image }, second: { preview: image } },
    };
    node.onSerialize(data);

    expect(replacement).toHaveBeenCalledOnce();
    expect(data.widgets_values).toEqual([{ preview: '' }, { preview: '' }]);
    expect(data.widgets_values_named).toEqual({ first: { preview: '' }, second: { preview: '' } });
  });

  it('does not recurse when a later onSerialize replacement delegates to the LF wrapper', () => {
    const first = { name: 'first', value: { preview: image } } as unknown as Widget<any>;
    const second = { name: 'second', value: { preview: image } } as unknown as Widget<any>;
    const events: string[] = [];
    const node = { widgets: [first, second] } as unknown as NodeType;

    hookDOMWidgetSerialization(node, first);
    const lfWrapper = node.onSerialize;
    node.onSerialize = function (data) {
      events.push('replacement:start');
      lfWrapper?.call(this, data);
      events.push('replacement:end');
      return data;
    };
    hookDOMWidgetSerialization(node, second);

    const data = {
      widgets_values: [{ preview: image }, { preview: image }],
      widgets_values_named: { first: { preview: image }, second: { preview: image } },
    };
    node.onSerialize(data);

    expect(events).toEqual(['replacement:start', 'replacement:end']);
    expect(data.widgets_values).toEqual([{ preview: '' }, { preview: '' }]);
    expect(data.widgets_values_named).toEqual({ first: { preview: '' }, second: { preview: '' } });
  });
});
