import { describe, expect, it, vi } from 'vitest';
import {
  applyInputPrefill,
  clearRetainedUploadPrefill,
  getRetainedUploadPrefill,
  InputPrefillCell,
} from '../utils/input-prefill';

const cell = (tagName: string, id: string, methods: Partial<InputPrefillCell> = {}) => {
  const element = document.createElement(tagName) as InputPrefillCell;
  element.id = id;
  Object.assign(element, methods);
  return element;
};

describe('applyInputPrefill', () => {
  it('restores controls and retains a prior server-backed upload without calling its setter', async () => {
    const text = vi.fn();
    const select = vi.fn();
    const toggle = vi.fn();
    const chat = vi.fn();
    const upload = vi.fn();
    const uploadCell = cell('LF-UPLOAD', 'source', { setValue: upload });

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
        uploadCell,
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
    expect(getRetainedUploadPrefill(uploadCell)).toBeUndefined();
  });

  it('retains and clears only an opaque prior-upload reference', async () => {
    const upload = cell('LF-UPLOAD', 'source');
    const prefill = {
      schema: 'lf.workflow-upload-prefill.v1',
      reference: {
        schema: 'lf.workflow-upload-ref.v1',
        sourceRunId: 'run-source',
        inputId: 'source',
      },
      names: ['reference.png'],
      available: true,
    };

    await applyInputPrefill([upload], { source: prefill });
    expect(getRetainedUploadPrefill(upload)).toEqual(prefill);

    clearRetainedUploadPrefill(upload);
    expect(getRetainedUploadPrefill(upload)).toBeUndefined();

    await applyInputPrefill([upload], { source: ['C:\\temp\\reference.png'] });
    expect(getRetainedUploadPrefill(upload)).toBeUndefined();

    await applyInputPrefill([upload], {
      source: {
        ...prefill,
        reference: { ...prefill.reference, inputId: 'different-cell' },
      },
    });
    expect(getRetainedUploadPrefill(upload)).toBeUndefined();
  });

  it('retains an opaque prior-output artifact for a different upload input', async () => {
    const upload = cell('LF-UPLOAD', 'image_b');
    const prefill = {
      schema: 'lf.workflow-upload-prefill.v1',
      reference: {
        schema: 'lf.workflow-artifact-ref.v1',
        sourceRunId: 'source-run',
        artifactId: 'a'.repeat(64),
        filename: 'candidate.png',
      },
      names: ['candidate.png'],
      available: true,
    };

    await applyInputPrefill([upload], { image_b: prefill });

    expect(getRetainedUploadPrefill(upload)).toEqual(prefill);
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
