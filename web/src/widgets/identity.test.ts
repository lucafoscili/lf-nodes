import { beforeEach, describe, expect, it, vi } from 'vitest';
import { CustomWidgetName } from '../types/widgets/widgets';
import { idFactory, refFactory } from './identity';

const managerSymbol = Symbol.for('__LfManager__');

describe('LF identity widgets', () => {
  beforeEach(() => {
    (window as unknown as Record<PropertyKey, unknown>)[managerSymbol] = { log: vi.fn() };
  });

  it('creates an author-time LF ID and keeps regeneration guarded', () => {
    const addDOMWidget = vi.fn((name?: string, type?: string, element?: HTMLDivElement, options?: any) => ({
      name,
      type,
      element,
      options,
      serializeValue: () => options?.getValue?.(),
    }));
    const node = { widgets: [], graph: { _nodes: [] }, addDOMWidget } as unknown as NodeType;
    node.graph._nodes.push(node);

    const { widget } = idFactory.render(node, 'scene_id', {
      default: '',
      lf_id_kind: 'scene',
    });
    const state = widget.options.getState();
    expect(state.value).toMatch(/^lf:scene:[^:]+/);
    expect(addDOMWidget).toHaveBeenCalledWith(
      'scene_id',
      CustomWidgetName.id,
      expect.any(HTMLDivElement),
      expect.anything(),
    );

    const original = state.value;
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false);
    state.chip?.parentElement?.querySelector('button:last-child')?.dispatchEvent(new MouseEvent('click'));
    expect(state.value).toBe(original);
    confirm.mockReturnValue(true);
    state.chip?.parentElement?.querySelector('button:last-child')?.dispatchEvent(new MouseEvent('click'));
    expect(state.value).toMatch(/^lf:scene:/);
    expect(state.value === original).toBe(false);
  });

  it('uses immutable IDs as LF_REF values while rendering friendly labels', () => {
    const widgets: Array<Widget<any>> = [];
    const addDOMWidget = vi.fn((name?: string, type?: string, element?: HTMLDivElement, options?: any) => {
      const widget = {
        name,
        type,
        element,
        options,
        serializeValue: () => options?.getValue?.(),
      } as Widget<any>;
      widgets.push(widget);
      return widget;
    });
    const node = { widgets, graph: { _nodes: [] }, addDOMWidget } as unknown as NodeType;
    node.graph._nodes.push(node);
    const id = idFactory.render(node, 'scene_id', { lf_id_kind: 'scene' }).widget;
    node.widgets.push(id);
    const { widget } = refFactory.render(node, 'entry_scene_id', { lf_ref_kind: 'scene' });
    const select = widget.element?.querySelector('select') as HTMLSelectElement;
    expect(select.options).toHaveLength(2);
    expect(select.options[1].value).toBe(id.options.getValue());
    select.value = id.options.getValue();
    select.dispatchEvent(new Event('change'));
    expect(widget.options.getValue()).toBe(id.options.getValue());
    expect(addDOMWidget.mock.calls.at(-1)?.[0]).toBe('entry_scene_id');
  });

  it('refreshes an ID chip after its friendly title hydrates', () => {
    vi.useFakeTimers();
    const widgets: Array<Widget<any>> = [];
    const addDOMWidget = vi.fn((name?: string, type?: string, element?: HTMLDivElement, options?: any) => {
      const widget = { name, type, element, options } as Widget<any>;
      widgets.push(widget);
      return widget;
    });
    const title = { name: 'title', value: 'Opening' } as Widget<any>;
    const node = { widgets, graph: { _nodes: [] }, addDOMWidget } as unknown as NodeType;
    node.graph._nodes.push(node);
    widgets.push(title);
    const id = idFactory.render(node, 'scene_id', {
      lf_id_kind: 'scene',
      lf_label_widget: 'title',
    }).widget;
    widgets.push(id);

    id.options.setValue('lf:scene:kept');
    title.value = 'Signal at Dusk';
    vi.runAllTimers();

    expect(id.options.getState().chip?.textContent).toBe('Signal at Dusk · lf:scene:kept');
    vi.useRealTimers();
  });

  it('remaps matching live references when an author regenerates an ID', () => {
    const widgets: Array<Widget<any>> = [];
    const addDOMWidget = vi.fn((name?: string, type?: string, element?: HTMLDivElement, options?: any) => {
      const widget = {
        name,
        type,
        element,
        options,
        serializeValue: () => options?.getValue?.(),
      } as Widget<any>;
      widgets.push(widget);
      return widget;
    });
    const node = { widgets, graph: { _nodes: [] }, addDOMWidget } as unknown as NodeType;
    node.graph._nodes.push(node);
    const idWidget = idFactory.render(node, 'scene_id', { lf_id_kind: 'scene' }).widget;
    const oldId = idWidget.options.getValue();
    const refWidget = refFactory.render(node, 'entry_scene_id', {
      default: oldId,
      lf_ref_kind: 'scene',
    }).widget;
    const textarea = document.createElement('textarea');
    textarea.value = JSON.stringify({
      choices: [{ nextSceneId: oldId, effects: [{ payload: { nextSceneId: oldId } }] }],
      metadata: { targetSceneId: oldId },
    });
    widgets.push({
      type: CustomWidgetName.textarea,
      options: {
        getState: () => ({
          textarea,
          refPaths: [{ path: '/choices/*/nextSceneId', kind: 'scene' }],
        }),
      },
    } as Widget<any>);
    const duplicateKeyRaw = `{"choices":[{"nextSceneId":"${oldId}","nextSceneId":"scene.external"}]}`;
    const duplicateKeyTextarea = document.createElement('textarea');
    duplicateKeyTextarea.value = duplicateKeyRaw;
    widgets.push({
      type: CustomWidgetName.textarea,
      options: {
        getState: () => ({
          textarea: duplicateKeyTextarea,
          refPaths: [{ path: '/choices/*/nextSceneId', kind: 'scene' }],
        }),
      },
    } as Widget<any>);

    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true);
    const idState = idWidget.options.getState();
    idState.chip?.parentElement?.querySelector('button:last-child')?.dispatchEvent(new MouseEvent('click'));
    const nextId = idWidget.options.getValue();
    expect(nextId === oldId).toBe(false);
    expect(refWidget.options.getValue()).toBe(nextId);
    const body = JSON.parse(textarea.value);
    expect(body.choices[0].nextSceneId).toBe(nextId);
    expect(body.choices[0].effects[0].payload.nextSceneId).toBe(oldId);
    expect(body.metadata.targetSceneId).toBe(oldId);
    expect(duplicateKeyTextarea.value).toBe(duplicateKeyRaw);
    confirm.mockRestore();
  });
});
