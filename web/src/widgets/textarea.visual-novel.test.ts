import { beforeEach, describe, expect, it, vi } from 'vitest';
import { TextareaCSS } from '../types/widgets/textarea';
import { CustomWidgetName } from '../types/widgets/widgets';
import { textareaFactory } from './textarea';

const MANAGER_SYMBOL = Symbol.for('__LfManager__');

const makeNode = () => {
  const node = {
    comfyClass: 'LF_SceneSpec',
    graph: { _nodes: [] as NodeType[], setDirtyCanvas: vi.fn() },
    widgets: [] as Widget<any>[],
  } as unknown as NodeType;
  (node.graph._nodes as NodeType[]).push(node);
  node.addDOMWidget = vi.fn((name, type, element, options) => {
    const widget = {
      element,
      name,
      options,
      serializeValue: () => options?.getValue(),
      type,
    } as Widget<any>;
    node.widgets?.push(widget);
    return widget;
  });
  return node;
};

describe('LF_TEXTAREA VN authoring boundary', () => {
  beforeEach(() => {
    (window as unknown as Record<PropertyKey, unknown>)[MANAGER_SYMBOL] = {
      log: vi.fn(),
    };
  });

  it('materializes missing child IDs only after valid JSON hydration', () => {
    const node = makeNode();
    const { widget } = textareaFactory.render(node, 'scene_body', [
      CustomWidgetName.textarea,
      { lf_id_paths: [{ path: '/beats/*', kind: 'beat' }] },
    ]);

    widget.options?.setValue(JSON.stringify({ beats: [{ text: 'Hello' }] }));

    const value = JSON.parse(widget.options?.getValue() as string);
    expect(value.beats[0].id).toMatch(/^lf:beat:/);
    expect(value.beats[0].text).toBe('Hello');
  });

  it('preserves authored IDs and visibly retains invalid raw JSON', () => {
    const node = makeNode();
    const { widget } = textareaFactory.render(node, 'scene_body', [
      CustomWidgetName.textarea,
      { lf_id_paths: [{ path: '/beats/*', kind: 'beat' }] },
    ]);
    const state = widget.options?.getState();

    widget.options?.setValue('{"beats":[{"id":"lf:beat:kept","text":"Hello"}]}');
    expect(JSON.parse(widget.options?.getValue() as string).beats[0].id).toBe('lf:beat:kept');

    widget.options?.setValue('{broken');
    expect(widget.options?.getValue()).toBe('{broken');
    expect(state?.textarea.classList.contains(TextareaCSS.WidgetError)).toBe(true);
  });

  it('rejects duplicate keys and preserves their exact raw text', () => {
    const node = makeNode();
    const { widget } = textareaFactory.render(node, 'scene_body', [
      CustomWidgetName.textarea,
      { lf_id_paths: [{ path: '/beats/*', kind: 'beat' }] },
    ]);
    const raw = '{"beats":[{"text":"first","text":"second"}]}';
    const state = widget.options?.getState();

    widget.options?.setValue(raw);

    expect(widget.options?.getValue()).toBe(raw);
    expect(state?.textarea.classList.contains(TextareaCSS.WidgetError)).toBe(true);
  });

  it('writes picker selections as immutable IDs inside the JSON document', () => {
    const node = makeNode();
    const sceneIdentity = {
      comfyClass: 'LF_SceneSpec',
      graph: node.graph,
      widgets: [{
        type: 'LF_ID',
        options: {
          getState: () => ({ kind: 'scene', getLabel: () => 'Second scene' }),
          getValue: () => 'lf:scene:second',
        },
      }],
    } as unknown as NodeType;
    node.graph._nodes.push(sceneIdentity);

    const { widget } = textareaFactory.render(node, 'scene_body', [
      CustomWidgetName.textarea,
      { lf_ref_paths: [{ path: '/choices/*/nextSceneId', kind: 'scene' }] },
    ]);
    widget.options?.setValue(JSON.stringify({
      choices: [{ label: 'Continue', nextSceneId: '' }],
    }));

    const state = widget.options?.getState();
    const select = state?.references.querySelector('select') as HTMLSelectElement;
    expect(select).toBeTruthy();
    expect(Array.from(select.options).map((option) => option.textContent)).toContain(
      'Second scene · second',
    );

    select.value = 'lf:scene:second';
    select.dispatchEvent(new Event('change'));
    const value = JSON.parse(widget.options?.getValue() as string);
    expect(value.choices[0].nextSceneId).toBe('lf:scene:second');
  });

  it('never lets a stale picker collapse duplicate-key raw text', () => {
    const node = makeNode();
    node.graph._nodes.push({
      comfyClass: 'LF_SceneSpec',
      graph: node.graph,
      widgets: [{
        type: 'LF_ID',
        options: {
          getState: () => ({ kind: 'scene', getLabel: () => 'Second scene' }),
          getValue: () => 'lf:scene:second',
        },
      }],
    } as unknown as NodeType);

    const { widget } = textareaFactory.render(node, 'scene_body', [
      CustomWidgetName.textarea,
      { lf_ref_paths: [{ path: '/choices/*/nextSceneId', kind: 'scene' }] },
    ]);
    widget.options?.setValue('{"choices":[{"label":"Continue","nextSceneId":""}]}');
    const state = widget.options?.getState();
    const select = state?.references.querySelector('select') as HTMLSelectElement;
    const raw = '{"choices":[{"nextSceneId":"lf:scene:first","nextSceneId":"lf:scene:second"}]}';

    widget.options?.setValue(raw);
    select.value = 'lf:scene:second';
    select.dispatchEvent(new Event('change'));

    expect(widget.options?.getValue()).toBe(raw);
    expect(state?.textarea.classList.contains(TextareaCSS.WidgetError)).toBe(true);
  });

  it('resolves a valid target that hydrates later in the configure pass', () => {
    vi.useFakeTimers();
    const node = makeNode();
    const { widget } = textareaFactory.render(node, 'scene_body', [
      CustomWidgetName.textarea,
      { lf_ref_paths: [{ path: '/choices/*/nextSceneId', kind: 'scene' }] },
    ]);
    widget.options?.setValue(JSON.stringify({
      choices: [{ label: 'Continue', nextSceneId: 'lf:scene:later' }],
    }));
    const state = widget.options?.getState();
    expect(state?.references.querySelector('select')?.selectedOptions[0]?.textContent)
      .toContain('Unresolved');

    node.graph._nodes.push({
      comfyClass: 'LF_SceneSpec',
      graph: node.graph,
      widgets: [{
        type: 'LF_ID',
        options: {
          getState: () => ({ kind: 'scene', getLabel: () => 'Later scene' }),
          getValue: () => 'lf:scene:later',
        },
      }],
    } as unknown as NodeType);
    vi.runAllTimers();

    expect(state?.references.querySelector('select')?.selectedOptions[0]?.textContent)
      .toBe('Later scene · later');
    vi.useRealTimers();
  });
});
