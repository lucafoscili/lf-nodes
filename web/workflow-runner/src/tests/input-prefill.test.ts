import { describe, expect, it, vi } from 'vitest';
import { applyInputPrefill, InputPrefillCell } from '../utils/input-prefill';

const cell = (tagName: string, id: string, methods: Partial<InputPrefillCell> = {}) =>
  ({ tagName, id, ...methods }) as InputPrefillCell;

describe('applyInputPrefill', () => {
  it('restores text, select, toggle and chat values while skipping uploads', async () => {
    const text = vi.fn();
    const select = vi.fn();
    const toggle = vi.fn();
    const chat = vi.fn();
    const upload = vi.fn();

    await applyInputPrefill(
      [
        cell('LF-TEXTFIELD', 'prompt', { setValue: text }),
        cell('LF-SELECT', 'mode', {
          setValue: select,
          lfDataset: {
            nodes: [{ id: 'cover-option', value: 'Cover', workflowValue: 'cover' }],
          },
        }),
        cell('LF-TOGGLE', 'instrumental', { setValue: toggle }),
        cell('LF-CHAT', 'assistant', { setHistory: chat }),
        cell('LF-UPLOAD', 'source', { setValue: upload }),
      ],
      {
        prompt: 'somber',
        mode: 'cover',
        instrumental: false,
        assistant: [{ role: 'user', content: 'keep the singer' }],
        source: 'temporary/path.wav',
      },
    );

    expect(text).toHaveBeenCalledWith('somber');
    expect(select).toHaveBeenCalledWith('cover-option');
    expect(toggle).toHaveBeenCalledWith('off');
    expect(chat).toHaveBeenCalledWith('[{"role":"user","content":"keep the singer"}]');
    expect(upload.mock.calls.length).toBe(0);
  });

  it('degrades safely when a control is retired or its setter throws', async () => {
    const broken = vi.fn(() => {
      throw new Error('retired widget');
    });
    const fallback = cell('LF-TEXTFIELD', 'title');

    await expect(
      applyInputPrefill(
        [cell('LF-TEXTFIELD', 'broken', { setValue: broken }), fallback],
        { broken: 'ignored', title: 'restored' },
      ),
    ).resolves.toBeUndefined();
    expect(fallback.lfValue).toBe('restored');
  });
});
