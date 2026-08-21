import { beforeEach, describe, expect, it, vi } from 'vitest';
import { CustomWidgetName } from '../types/widgets/widgets';
import { createDOMWidget } from './common';
import { textareaFactory } from '../widgets/textarea';

const MANAGER_SYMBOL = Symbol.for('__LfManager__');

describe('createDOMWidget naming', () => {
  beforeEach(() => {
    (window as unknown as Record<PropertyKey, unknown>)[MANAGER_SYMBOL] = {
      log: vi.fn(),
    };
  });

  it('uses the explicit input name for repeated widgets of one type', () => {
    const addDOMWidget = vi.fn((name?: string) => ({ name })) as unknown as NodeType['addDOMWidget'];
    const node = { addDOMWidget } as unknown as NodeType;
    const options = {} as WidgetOptions;

    createDOMWidget(CustomWidgetName.textarea, document.createElement('div'), node, options, 'body');
    createDOMWidget(
      CustomWidgetName.textarea,
      document.createElement('div'),
      node,
      options,
      'fallback_body',
    );

    expect(addDOMWidget).toHaveBeenNthCalledWith(
      1,
      'body',
      CustomWidgetName.textarea,
      expect.any(HTMLDivElement),
      options,
    );
    expect(addDOMWidget).toHaveBeenNthCalledWith(
      2,
      'fallback_body',
      CustomWidgetName.textarea,
      expect.any(HTMLDivElement),
      options,
    );
  });

  it('passes each Comfy input name through the textarea factory', () => {
    const addDOMWidgetMock = vi.fn((name?: string) => ({ name }));
    const addDOMWidget = addDOMWidgetMock as unknown as NodeType['addDOMWidget'];
    const node = { addDOMWidget } as unknown as NodeType;

    textareaFactory.render(node, 'opaque_body');
    textareaFactory.render(node, 'scene_body');

    expect(addDOMWidgetMock.mock.calls.map(([name]) => name)).toEqual([
      'opaque_body',
      'scene_body',
    ]);
  });

  it('retains the node-data scan for node-only callers', () => {
    class LegacyNode {}
    Object.defineProperty(LegacyNode, 'nodeData', {
      value: {
        input: {
          required: { body: [CustomWidgetName.textarea] },
        },
      },
    });

    const addDOMWidget = vi.fn((name?: string) => ({ name })) as unknown as NodeType['addDOMWidget'];
    const node = Object.assign(new LegacyNode(), { addDOMWidget }) as unknown as NodeType;

    createDOMWidget(
      CustomWidgetName.textarea,
      document.createElement('div'),
      node,
      {} as WidgetOptions,
    );

    expect(addDOMWidget).toHaveBeenCalledWith(
      'body',
      CustomWidgetName.textarea,
      expect.any(HTMLDivElement),
      expect.anything(),
    );
  });
});
