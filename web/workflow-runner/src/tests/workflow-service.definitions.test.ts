import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: () => ({
    syntax: {
      json: {
        parse: (response: { json: () => Promise<unknown> }) => response.json(),
      },
    },
  }),
}));

import { fetchWorkflowDefinitions } from '../services/workflow-service';

describe('workflow definition taxonomy boundary', () => {
  const realFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = realFetch;
    vi.restoreAllMocks();
  });

  it('publishes only canonical block/orchestra kinds to the frontend store', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        workflows: {
          nodes: [
            { id: 'missing' },
            { id: 'legacy-block', kind: 'workflow' },
            { id: 'legacy-orchestra', kind: 'sequence' },
            { id: 'block', kind: 'block' },
            { id: 'orchestra', kind: 'orchestra' },
          ],
        },
      }),
    }) as typeof fetch;

    const result = await fetchWorkflowDefinitions();

    expect(result.nodes.map((node) => node.kind)).toEqual([
      'block',
      'block',
      'orchestra',
      'block',
      'orchestra',
    ]);
  });

  it('preserves optional card metadata while normalizing the workflow kind', async () => {
    const card = {
      summary: 'Restore fine details.',
      hero: { asset: 'restore-before-after.webp', alt: 'Before: soft details. After: restored details.' },
    };
    const wire = { id: 'restore', kind: 'workflow', card };
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ workflows: { nodes: [wire] } }),
    }) as typeof fetch;

    const result = await fetchWorkflowDefinitions();

    expect(result.nodes[0]).toMatchObject({ id: 'restore', kind: 'block', card });
    expect(wire.kind).toBe('workflow');
    expect(wire.card).toEqual(card);
  });
});
