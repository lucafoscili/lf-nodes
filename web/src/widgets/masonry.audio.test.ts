import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NODE_WIDGET_MAP } from '../helpers/manager';
import { LFWidgets } from '../managers/widgets';
import { MasonryAudioFile, MasonryDeserializedValue, MasonryState } from '../types/widgets/masonry';
import { CustomWidgetName, NodeName } from '../types/widgets/widgets';
import { masonryFactory } from './masonry';

const MANAGER_SYMBOL = Symbol.for('__LfManager__');
const files: MasonryAudioFile[] = [
  { filename: 'clip & "lead".wav', subfolder: 'sound refs/scene + 2', type: 'output' },
  { filename: 'second.wav', subfolder: '', type: 'output' },
];
const redraw = vi.fn();
const getNodeById = vi.fn();
type PreviewNode = NodeType & { onExecuted?: (...args: unknown[]) => unknown };

const render = (
  comfyClass: NodeName = NodeName.saveAudio,
  previous = vi.fn(),
  previousRemoval?: () => void,
): {
  node: PreviewNode;
  widget: ReturnType<typeof masonryFactory.render>['widget'];
  state: MasonryState;
  previous: ReturnType<typeof vi.fn>;
} => {
  const node = {
    id: '77',
    comfyClass,
    graph: { _nodes: [] },
    widgets: [],
    onExecuted: previous,
    onRemoved: previousRemoval,
    addDOMWidget(name, type, element, options) {
      const widget = { name, type, element, options, serializeValue: () => options.getValue() };
      this.widgets.push(widget);
      return widget;
    },
  } as PreviewNode;
  const { widget } = masonryFactory.render(node);
  return { node, widget, state: widget.options.getState() as MasonryState, previous };
};

beforeEach(() => {
  vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => undefined);
  vi.spyOn(HTMLMediaElement.prototype, 'load').mockImplementation(() => undefined);
  getNodeById.mockReset();
  (window as unknown as Record<PropertyKey, unknown>)[MANAGER_SYMBOL] = {
    log: vi.fn(),
    getApiRoutes: () => ({ comfy: { getNodeById, redraw } }),
    getManagers: () => ({
      lfFramework: {
        syntax: {
          json: {
            unescape: (value: unknown) => ({
              parsedJSON: typeof value === 'string' ? JSON.parse(value) : value,
            }),
          },
        },
      },
    }),
  };
});

describe('LF_SaveAudio preview', () => {
  it('registers a one-column LF masonry preview with native controls and readable labels', () => {
    expect(NODE_WIDGET_MAP[NodeName.saveAudio]).toEqual([CustomWidgetName.masonry]);
    const { widget, state } = render();
    widget.options.setValue(JSON.stringify({ audio: files }));

    expect(state.masonry.lfColumns).toBe(1);
    expect(state.masonry.lfActions).toBe(false);
    expect(state.masonry.lfShape).toBe('slot');
    expect(state.masonry.lfDataset.nodes).toHaveLength(2);
    const controls = state.masonry.querySelectorAll('audio');
    expect(controls).toHaveLength(2);
    controls.forEach((audio, index) => {
      const reference = [files[index].subfolder, files[index].filename].filter(Boolean).join('/');
      expect(audio.controls).toBe(true);
      expect(audio.autoplay).toBe(false);
      expect(audio.preload).toBe('metadata');
      expect(audio.style.width).toBe('100%');
      expect(audio.getAttribute('aria-label')).toBe(reference);
      expect(audio.previousElementSibling?.textContent).toBe(reference);
      expect(audio.parentElement?.slot).toBe(`lf-audio-${index}`);
    });
  });

  it('uses restart-stable /view output URLs with every filename and subfolder encoded', () => {
    const { widget, state } = render();
    widget.options.setValue(JSON.stringify({ audio: files }));
    const audio = state.masonry.querySelector('audio');
    const url = new URL(audio.src, window.location.href);
    expect(url.pathname).toBe('/view');
    expect([...url.searchParams.keys()]).toEqual(['filename', 'subfolder', 'type']);
    expect(url.searchParams.get('filename')).toBe(files[0].filename);
    expect(url.searchParams.get('subfolder')).toBe(files[0].subfolder);
    expect(url.searchParams.get('type')).toBe('output');
    expect(state.masonry.querySelector('a')?.getAttribute('href')).toBe(audio.getAttribute('src'));
    expect(state.masonry.querySelector('a')?.download).toBe(files[0].filename);
  });

  it('hydrates controls from the registered live event without requiring a backend dataset', () => {
    const { node, state } = render();
    getNodeById.mockReturnValue(node);
    new LFWidgets().onEvent(
      NodeName.saveAudio,
      new CustomEvent('lf-saveaudio', { detail: { node: node.id, audio: files } }),
      [CustomWidgetName.masonry],
    );
    expect(state.audio).toEqual(files);
    expect(state.masonry.querySelectorAll('audio')).toHaveLength(2);
    expect(redraw).toHaveBeenCalled();
  });

  it('retains output descriptors across widget serialization and reload', () => {
    const { widget } = render();
    widget.options.setValue(JSON.stringify({ audio: files }));
    const serialized = JSON.stringify(widget.serializeValue());
    const restored = render();
    restored.widget.options.setValue(serialized);
    expect(restored.state.audio).toEqual(files);
    expect(restored.state.masonry.querySelectorAll('audio')).toHaveLength(2);
    expect(serialized.includes('data:audio')).toBe(false);
    expect(serialized.includes('<audio')).toBe(false);
    expect(serialized.includes('type=temp')).toBe(false);
    expect(restored.widget.options.getValue()).toEqual(widget.options.getValue());
  });

  it('does not expose live descriptor objects through serialized widget state', () => {
    const { widget, state } = render();
    widget.options.setValue(JSON.stringify({ audio: files }));
    const serialized = widget.options.getValue() as MasonryDeserializedValue;
    serialized.audio[0].filename = 'mutated.wav';
    expect(state.audio[0].filename).toBe(files[0].filename);
  });

  it('hydrates all mapped history entries in order and preserves the previous callback', () => {
    const previous = vi.fn().mockReturnValue('existing result');
    const { node, state } = render(NodeName.saveAudio, previous);
    const output = {
      lf_output: [{ audio: [files[0]] }, { audio: [files[1]] }],
      audio: files,
    };
    expect(node.onExecuted(output, 'history')).toBe('existing result');
    expect(previous).toHaveBeenCalledWith(output, 'history');
    expect(previous.mock.contexts[0]).toBe(node);
    expect(state.audio).toEqual(files);
    expect(state.masonry.querySelectorAll('audio')).toHaveLength(2);
  });

  it('supports native-only audio history without depending on Comfy SaveAudio class hooks', () => {
    const { node, state } = render();
    node.onExecuted({ audio: files });
    expect(state.audio).toEqual(files);
  });

  it('does not reset playing controls when live and history payloads match', () => {
    const { node, widget, state } = render();
    widget.options.setValue(JSON.stringify({ audio: files }));
    const audio = state.masonry.querySelector('audio');
    node.onExecuted({ lf_output: [{ audio: files }] });
    expect(state.masonry.querySelector('audio')).toBe(audio);
    expect(audio.pause).toHaveBeenCalledTimes(0);
  });

  it('clears old controls when a new explicit audio result is empty', () => {
    const { node, widget, state } = render();
    widget.options.setValue(JSON.stringify({ audio: files }));
    node.onExecuted({ lf_output: [{ audio: [] }], audio: files });
    expect(state.audio).toEqual([]);
    expect(state.masonry.querySelectorAll('audio')).toHaveLength(0);
    expect(state.masonry.lfDataset.nodes).toHaveLength(0);
    expect(HTMLMediaElement.prototype.pause).toHaveBeenCalledTimes(2);
  });

  it('ignores unrelated history messages and non-output descriptors', () => {
    const { node, widget, state } = render();
    widget.options.setValue(JSON.stringify({
      audio: [null, { ...files[0], type: 'temp' }, { filename: 'missing-type.wav' }, files[1]],
    }));
    node.onExecuted({ lf_output: [null, { receipt: {} }] });
    node.onExecuted(null);
    expect(state.audio).toEqual([files[1]]);
  });

  it('stops and releases controls on node removal while preserving the existing handler', () => {
    const onRemoved = vi.fn();
    const { node, widget, state } = render(NodeName.saveAudio, vi.fn(), onRemoved);
    widget.options.setValue(JSON.stringify({ audio: files }));
    node.onRemoved();
    expect(HTMLMediaElement.prototype.pause).toHaveBeenCalledTimes(2);
    expect(HTMLMediaElement.prototype.load).toHaveBeenCalledTimes(2);
    expect(state.masonry.querySelector('audio')?.hasAttribute('src')).toBe(false);
    expect(onRemoved).toHaveBeenCalledTimes(1);
    expect(onRemoved.mock.contexts[0]).toBe(node);
  });

  it('does not install audio history hooks or change the layout of image masonry widgets', () => {
    const { node, state, previous } = render(NodeName.viewImages);
    expect(node.onExecuted).toBe(previous);
    expect(node.onRemoved).toBeUndefined();
    expect(state.masonry.lfActions).toBe(true);
    expect(state.masonry.lfColumns).toBe(3);
  });

  it('recreates released sources if the same widget is restored after node removal', () => {
    const { node, widget, state } = render();
    widget.options.setValue(JSON.stringify({ audio: files }));
    const serialized = JSON.stringify(widget.options.getValue());
    node.onRemoved();
    widget.options.setValue(serialized);
    expect(state.masonry.querySelectorAll('audio[src]')).toHaveLength(2);
    expect(state.audio).toEqual(files);
  });
});
