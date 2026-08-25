import { describe, expect, it, vi } from 'vitest';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import type { WorkflowUICells } from '../types/section';
import {
  getRetainedUploadPrefill,
  setRetainedUploadPrefill,
} from '../utils/input-prefill';
import {
  applyWorkflowSessionDraft,
  captureWorkflowSessionDraft,
  clearWorkflowSessionDraft,
  getWorkflowSessionDraft,
  replaceWorkflowSessionDraft,
  watchWorkflowSessionDraft,
} from '../utils/session-drafts';

type DraftCell = HTMLElement & {
  getHistory?: () => Promise<unknown>;
  getValue?: () => Promise<unknown>;
  lfDataset?: {
    nodes?: Array<{
      id: string;
      value?: string | number;
      workflowValue?: string | number;
      children?: Array<{ id: string; value?: string | number; workflowValue?: string | number }>;
    }>;
  };
  lfValue?: unknown;
  setHistory?: (value: string) => Promise<void> | void;
  setValue?: (value: unknown) => Promise<void> | void;
};

const cell = (tagName: string, id: string, methods: Partial<DraftCell> = {}) => {
  const element = document.createElement(tagName) as DraftCell;
  element.id = id;
  Object.assign(element, methods);
  return element;
};

const tick = () => new Promise<void>((resolve) => setTimeout(resolve, 0));

describe('Workflow Runner session drafts', () => {
  it('restores an unfinished form after leaving and returning to its workflow', async () => {
    const store = createWorkflowRunnerStore(initState());
    const original = cell('lf-textfield', 'prompt', {
      getValue: async () => 'unfinished scene description',
    });
    const stop = watchWorkflowSessionDraft(
      store,
      'workflow-a',
      [original] as WorkflowUICells,
    );

    original.dispatchEvent(
      new CustomEvent('lf-textfield-event', { detail: { eventType: 'input' } }),
    );
    await tick();
    stop();

    const restore = vi.fn();
    const remounted = cell('lf-textfield', 'prompt', { setValue: restore });
    await applyWorkflowSessionDraft(
      [remounted] as WorkflowUICells,
      getWorkflowSessionDraft(store, 'workflow-a')!,
    );

    expect(restore).toHaveBeenCalledWith('unfinished scene description');
  });

  it('keeps drafts isolated per workflow', () => {
    const store = createWorkflowRunnerStore(initState());
    replaceWorkflowSessionDraft(store, 'workflow-a', { prompt: 'A' });
    replaceWorkflowSessionDraft(store, 'workflow-b', { prompt: 'B' });

    expect(getWorkflowSessionDraft(store, 'workflow-a')).toEqual({ prompt: 'A' });
    expect(getWorkflowSessionDraft(store, 'workflow-b')).toEqual({ prompt: 'B' });
  });

  it('captures semantic selects, toggles, and chat alongside text values', async () => {
    const store = createWorkflowRunnerStore(initState());
    await captureWorkflowSessionDraft(
      store,
      'workflow-a',
      [
        cell('lf-textfield', 'prompt', { getValue: async () => 'plain text' }),
        cell('lf-select', 'sampler', {
          getValue: async () => ({ id: 'euler-option', value: 'Euler', workflowValue: 'euler' }),
        }),
        cell('lf-toggle', 'enabled', { getValue: async () => 'on' }),
        cell('lf-chat', 'conversation', {
          getHistory: async () => '[{"role":"user","content":"hello"}]',
        }),
      ] as WorkflowUICells,
    );

    expect(getWorkflowSessionDraft(store, 'workflow-a')).toEqual({
      prompt: 'plain text',
      sampler: 'euler',
      enabled: true,
      conversation: '[{"role":"user","content":"hello"}]',
    });
  });

  it('Reset clears only the selected workflow so declarations can supply defaults again', () => {
    const store = createWorkflowRunnerStore(initState());
    replaceWorkflowSessionDraft(store, 'workflow-a', { prompt: 'edited' });
    replaceWorkflowSessionDraft(store, 'workflow-b', { prompt: 'keep me' });

    clearWorkflowSessionDraft(store, 'workflow-a');

    expect(getWorkflowSessionDraft(store, 'workflow-a')).toBeUndefined();
    expect(getWorkflowSessionDraft(store, 'workflow-b')).toEqual({ prompt: 'keep me' });
  });

  it('lets an intentional Remix prefill supersede the ordinary draft', async () => {
    const store = createWorkflowRunnerStore(initState());
    replaceWorkflowSessionDraft(store, 'workflow-a', {
      prompt: 'ordinary draft',
      steps: '12',
    });

    replaceWorkflowSessionDraft(store, 'workflow-a', {
      prompt: 'selected run prompt',
      steps: '8',
    });

    const prompt = vi.fn();
    const steps = vi.fn();
    await applyWorkflowSessionDraft(
      [
        cell('lf-textfield', 'prompt', { setValue: prompt }),
        cell('lf-textfield', 'steps', { setValue: steps }),
      ] as WorkflowUICells,
      getWorkflowSessionDraft(store, 'workflow-a')!,
    );

    expect(prompt).toHaveBeenCalledWith('selected run prompt');
    expect(steps).toHaveBeenCalledWith('8');
  });

  it('retains the exact upload File object while the browser session remains mounted', async () => {
    const store = createWorkflowRunnerStore(initState());
    const upload = new File(['pixels'], 'reference.png', { type: 'image/png' });
    const original = cell('lf-upload', 'reference', {
      getValue: async () => [upload],
    });

    await captureWorkflowSessionDraft(
      store,
      'workflow-a',
      [original] as WorkflowUICells,
    );

    const remounted = cell('lf-upload', 'reference');
    await applyWorkflowSessionDraft(
      [remounted] as WorkflowUICells,
      getWorkflowSessionDraft(store, 'workflow-a')!,
    );

    expect(Array.isArray(remounted.lfValue)).toBe(true);
    expect((remounted.lfValue as File[])[0]).toBe(upload);
  });

  it('restores a retained opaque upload reference without converting it to a path', async () => {
    const store = createWorkflowRunnerStore(initState());
    const original = cell('lf-upload', 'reference', { getValue: async () => [] });
    setRetainedUploadPrefill(original, {
      schema: 'lf.workflow-upload-prefill.v1',
      reference: {
        schema: 'lf.workflow-upload-ref.v1',
        sourceRunId: 'source-run',
        inputId: 'reference',
      },
      names: ['reference.png'],
      available: true,
    });
    await captureWorkflowSessionDraft(
      store,
      'workflow-a',
      [original] as WorkflowUICells,
    );

    const remounted = cell('lf-upload', 'reference');
    await applyWorkflowSessionDraft(
      [remounted] as WorkflowUICells,
      getWorkflowSessionDraft(store, 'workflow-a')!,
    );

    expect(getRetainedUploadPrefill(remounted)).toEqual({
      schema: 'lf.workflow-upload-prefill.v1',
      reference: {
        schema: 'lf.workflow-upload-ref.v1',
        sourceRunId: 'source-run',
        inputId: 'reference',
      },
      names: ['reference.png'],
      available: true,
    });
  });

  it('does not let an older async capture resurrect a cleared draft', async () => {
    const store = createWorkflowRunnerStore(initState());
    let release!: (value: unknown) => void;
    const delayed = new Promise((resolve) => {
      release = resolve;
    });
    const original = cell('lf-textfield', 'prompt', {
      getValue: () => delayed,
    });

    const capture = captureWorkflowSessionDraft(
      store,
      'workflow-a',
      [original] as WorkflowUICells,
    );
    clearWorkflowSessionDraft(store, 'workflow-a');
    release('stale value');
    await capture;

    expect(getWorkflowSessionDraft(store, 'workflow-a')).toBeUndefined();
  });

  it('does not let a slower old input read overwrite a newer draft capture', async () => {
    const store = createWorkflowRunnerStore(initState());
    let releaseOld!: (value: unknown) => void;
    const oldValue = new Promise((resolve) => {
      releaseOld = resolve;
    });
    const oldCapture = captureWorkflowSessionDraft(
      store,
      'workflow-a',
      [cell('lf-textfield', 'prompt', { getValue: () => oldValue })] as WorkflowUICells,
    );
    await captureWorkflowSessionDraft(
      store,
      'workflow-a',
      [cell('lf-textfield', 'prompt', { getValue: async () => 'new value' })] as WorkflowUICells,
    );
    releaseOld('old value');
    await oldCapture;

    expect(getWorkflowSessionDraft(store, 'workflow-a')).toEqual({ prompt: 'new value' });
  });
});
