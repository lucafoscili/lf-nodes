import { describe, expect, it, vi } from 'vitest';

import { hydrateSamplingSelectDataset } from './sampling';

describe('image editor sampling option hydration', () => {
  const dataset = {
    nodes: [
      { id: 'dpmpp_2m', value: 'dpmpp_2m' },
      { id: 'euler', value: 'euler' },
    ],
  };

  it('preserves a newer user selection when the sampler catalogue arrives late', async () => {
    const select = {
      getValue: vi.fn().mockResolvedValue({ id: 'euler' }),
      setValue: vi.fn().mockResolvedValue(undefined),
      lfDataset: { nodes: [] },
    } as unknown as HTMLLfSelectElement;

    await hydrateSamplingSelectDataset(select, dataset, 'dpmpp_2m');

    expect(select.lfDataset).toBe(dataset);
    expect(select.setValue).toHaveBeenCalledWith('euler');
  });

  it('uses the declared default when the previous selection is unavailable', async () => {
    const select = {
      getValue: vi.fn().mockResolvedValue({ id: 'removed_sampler' }),
      setValue: vi.fn().mockResolvedValue(undefined),
      lfDataset: { nodes: [] },
    } as unknown as HTMLLfSelectElement;

    await hydrateSamplingSelectDataset(select, dataset, 'dpmpp_2m');

    expect(select.setValue).toHaveBeenCalledWith('dpmpp_2m');
  });
});
