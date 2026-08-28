import { describe, expect, it } from 'vitest';

import { NodeName } from '../types/widgets/widgets';
import {
  consumeImageEditorHydration,
  makeImageEditorDatasetInert,
  queueImageEditorHydration,
  resolveImageEditorHydrationDataset,
  resolveImageEditorRecoveryRequest,
} from './imageEditor';

const pendingColumns = [
  { id: 'status', title: 'pending' },
  { id: 'path', title: 'C:/ComfyUI/temp/session.json' },
];

describe('image editor recovery authority', () => {
  it('binds load-and-edit recovery to the serialized root context_id', () => {
    expect(
      resolveImageEditorRecoveryRequest(
        NodeName.loadAndEditImages,
        { context_id: 'C:/ComfyUI/temp/workflow-a-context.json' },
        'client-loader',
      ),
    ).toEqual({
      callerClientId: 'client-loader',
      contextId: 'C:/ComfyUI/temp/workflow-a-context.json',
    });
  });

  it('never falls back to node-only loader recovery without that capability', () => {
    expect(resolveImageEditorRecoveryRequest(NodeName.loadAndEditImages, {})).toBeNull();
    expect(
      resolveImageEditorRecoveryRequest(NodeName.loadAndEditImages, {
        selection: { context_id: 'not-root-authority' },
      }),
    ).toBeNull();
  });

  it('binds breakpoint recovery to the current client and exact context when present', () => {
    expect(
      resolveImageEditorRecoveryRequest(
        NodeName.imagesEditingBreakpoint,
        {
          columns: pendingColumns,
          context_id: 'C:/ComfyUI/temp/breakpoint-context.json',
        },
        'client-a',
      ),
    ).toEqual({
      callerClientId: 'client-a',
      contextId: 'C:/ComfyUI/temp/breakpoint-context.json',
    });
  });

  it('allows an owner-bound node scan before the breakpoint event hydrates the widget', () => {
    expect(
      resolveImageEditorRecoveryRequest(NodeName.imagesEditingBreakpoint, {}, 'client-a'),
    ).toEqual({ callerClientId: 'client-a' });
  });

  it('keeps the newest live hydration that arrives while recovery is in flight', () => {
    const state = {} as Parameters<typeof queueImageEditorHydration>[0];
    const first = { context_id: 'first' };
    const latest = { context_id: 'latest' };

    queueImageEditorHydration(state, first);
    queueImageEditorHydration(state, latest);

    expect(consumeImageEditorHydration(state, { context_id: 'serialized' })).toBe(latest);
    expect(state.pendingHydrationValue).toBeUndefined();
  });

  it('allows only exact-context ownerless recovery without a current client id', () => {
    expect(
      resolveImageEditorRecoveryRequest(
        NodeName.imagesEditingBreakpoint,
        {
          columns: pendingColumns,
          context_id: 'C:/ComfyUI/temp/breakpoint-context.json',
        },
      ),
    ).toEqual({ contextId: 'C:/ComfyUI/temp/breakpoint-context.json' });
    expect(
      resolveImageEditorRecoveryRequest(NodeName.imagesEditingBreakpoint, {
        columns: pendingColumns,
      }),
    ).toBeNull();
  });

  it('makes failed pending recovery inert without rewriting immutable ownership', () => {
    const dataset = {
      columns: pendingColumns,
      context_id: 'C:/ComfyUI/temp/breakpoint-context.json',
      nodes: [],
      owner_client_id: 'original-owner',
      selection: { context_id: 'C:/ComfyUI/temp/breakpoint-context.json', index: 0 },
    };

    const hydration = resolveImageEditorHydrationDataset(dataset, null);
    const inert = hydration.dataset as typeof dataset;

    expect(hydration.readOnly).toBe(true);
    expect(dataset.owner_client_id).toBe('original-owner');
    expect(inert.owner_client_id).toBe('original-owner');
    expect(inert === dataset).toBe(false);
    expect(inert.columns).toEqual([]);
    expect('context_id' in inert).toBe(false);
    expect('context_id' in inert.selection).toBe(false);
    expect(
      resolveImageEditorRecoveryRequest(NodeName.imagesEditingBreakpoint, inert, 'other-tab'),
    ).toEqual({ callerClientId: 'other-tab' });
  });

  it('preserves recovered ownership and pending capability unchanged', () => {
    const recovered = {
      columns: pendingColumns,
      context_id: 'C:/ComfyUI/temp/active.json',
      nodes: [],
      owner_client_id: 'server-owner',
    };

    expect(resolveImageEditorHydrationDataset({}, recovered)).toEqual({
      dataset: recovered,
      readOnly: false,
    });
    expect(recovered.owner_client_id).toBe('server-owner');
  });

  it('removes legacy mutable recovery ownership from an inert copy only', () => {
    const dataset = {
      columns: pendingColumns,
      nodes: [],
      owner_client_id: 'server-owner',
      recovery_client_id: 'legacy-owner',
    };
    const inert = makeImageEditorDatasetInert(dataset as never) as Record<string, unknown>;

    expect(inert.owner_client_id).toBe('server-owner');
    expect('recovery_client_id' in inert).toBe(false);
    expect(dataset.recovery_client_id).toBe('legacy-owner');
  });
});
