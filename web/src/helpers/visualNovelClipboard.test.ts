import { describe, expect, it, vi } from 'vitest';
import { installVnClipboardIdentityRemap } from './visualNovelClipboard';
import { VnClipboardItems } from './visualNovel';

describe('VN clipboard identity adapter', () => {
  it('remaps a complete payload before the native paste transaction begins', () => {
    class Canvas {
      received: unknown;
      _deserializeItems(parsed: unknown) {
        this.received = parsed;
        return parsed;
      }
    }
    const canvas = new Canvas();
    const original = {
      nodes: [{
        id: 1,
        type: 'LF_SceneSpec',
        widgets_values: [
          'lf:scene:old',
          'Opening',
          JSON.stringify({
            participants: [],
            entryPredicate: {},
            beats: [{ id: 'lf:beat:old', text: 'Hello' }],
            choices: [],
            artRequests: [],
          }),
        ],
      }],
    };

    expect(installVnClipboardIdentityRemap(canvas)).toBe(true);
    const result = canvas._deserializeItems(original) as typeof original;

    expect(original.nodes[0].widgets_values[0]).toBe('lf:scene:old');
    expect(result.nodes[0].widgets_values[0]).toMatch(/^lf:scene:/);
    expect(result.nodes[0].widgets_values[0] === 'lf:scene:old').toBe(false);
    expect(canvas.received).toBe(result);
  });

  it('is idempotent and reports an incompatible frontend', () => {
    class Canvas {
      calls = 0;
      _deserializeItems(parsed: unknown) {
        this.calls += 1;
        return parsed;
      }
    }
    const canvas = new Canvas();
    expect(installVnClipboardIdentityRemap(canvas)).toBe(true);
    expect(installVnClipboardIdentityRemap(canvas)).toBe(true);
    canvas._deserializeItems({ nodes: [] });
    expect(canvas.calls).toBe(1);

    const logger = vi.fn();
    const error = vi.spyOn(console, 'error').mockImplementation(() => undefined);
    expect(installVnClipboardIdentityRemap({}, logger)).toBe(false);
    expect(logger).toHaveBeenCalledWith(
      expect.stringContaining('no compatible paste transaction'),
      expect.anything(),
    );
    error.mockRestore();
  });

  it('preserves duplicate-key body text instead of collapsing it during paste', () => {
    const rawBody = '{"choices":[{"label":"A","label":"B"}]}';
    const payload = {
      nodes: [{
        type: 'LF_SceneSpec',
        widgets_values: ['lf:scene:old', 'Opening', rawBody],
      }],
    };

    const transformed = installAndTransform(payload);
    expect(transformed.nodes[0].widgets_values[2]).toBe(rawBody);
    expect(transformed.nodes[0].widgets_values[0]).toMatch(/^lf:scene:/);
  });
});

const installAndTransform = <T extends VnClipboardItems>(payload: T): T => {
  // Keep this test on the public clipboard adapter's observable path while
  // allowing the native deserializer to return the transformed payload.
  class Canvas {
    _deserializeItems(parsed: unknown) {
      return parsed;
    }
  }
  const canvas = new Canvas();
  installVnClipboardIdentityRemap(canvas);
  return canvas._deserializeItems(payload) as T;
};
