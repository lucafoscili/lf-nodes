import { expect, it, vi } from 'vitest';
import { NodeName } from '../types/widgets/widgets';
import { codeFactory } from './code';

it('restores indexed-key history without changing random-key callbacks', () => {
  (window as unknown as Record<PropertyKey, unknown>)[Symbol.for('__LfManager__')] = {
    log: vi.fn(),
  };
  const render = (comfyClass: NodeName) => {
    const previous = vi.fn().mockReturnValue('preserved');
    const node = {
      id: '42', comfyClass, widgets: [], onExecuted: previous,
      addDOMWidget(name, type, element, options) {
        const widget = { name, type, element, options };
        return widget;
      },
    } as unknown as NodeType & { onExecuted: (...args: unknown[]) => unknown };
    const { widget } = codeFactory.render(node);
    return { node, widget, previous };
  };
  const { node, widget, previous } = render(NodeName.getKeyFromJsonByIndex);
  const output = { lf_output: [{ value: 'first' }, null, { value: 'second' }] };
  expect(node.onExecuted(output, 'history')).toBe('preserved');
  expect(previous).toHaveBeenCalledWith(output, 'history');
  expect(previous.mock.contexts[0]).toBe(node);
  expect(widget.options.getValue()).toBe('first\n\nsecond');
  node.onExecuted(null);
  expect(widget.options.getValue()).toBe('first\n\nsecond');
  const random = render(NodeName.getRandomKeyFromJson);
  expect(random.node.onExecuted).toBe(random.previous);
});
