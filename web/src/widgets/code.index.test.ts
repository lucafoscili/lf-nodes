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

it('restores the retarget GLB filename and report from durable history', () => {
  (window as unknown as Record<PropertyKey, unknown>)[Symbol.for('__LfManager__')] = { log: vi.fn() };
  const previous = vi.fn();
  const node = {
    id: '43', comfyClass: NodeName.retargetMotion, widgets: [], onExecuted: previous,
    addDOMWidget(name, type, element, options) { return { name, type, element, options }; },
  } as unknown as NodeType & { onExecuted: (...args: unknown[]) => unknown };
  const { widget } = codeFactory.render(node);
  const report = { glb_file: 'LF_Nodes/Motion/retarget_1.glb', report_file: 'LF_Nodes/Motion/retarget_1.json', frames: 3 };
  const value = JSON.stringify(report);
  node.onExecuted({ lf_output: [{ value, json: report, file_names: [report.glb_file, report.report_file] }] });
  expect(previous).toHaveBeenCalledOnce();
  expect(widget.options.getValue()).toBe(value);
  expect(codeFactory.state.get(widget.element as HTMLDivElement).code.lfLanguage).toBe('json');
});
