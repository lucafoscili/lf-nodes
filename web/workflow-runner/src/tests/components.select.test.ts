import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createInputCell } from '../elements/components';
import { WorkflowCellInput } from '../types/api';

vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    sanitizeProps: vi.fn((props: unknown) => props),
  })),
}));

describe('createInputCell select inputs', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it.each(['select', 'choice'] as const)('creates an LF Select for the %s shape', (shape) => {
    const dataset = {
      nodes: [
        { id: 'euler', value: 'euler' },
        { id: 'dpmpp_2m', value: 'dpmpp_2m' },
      ],
    };
    const textfieldProps = { lfLabel: 'Sampler' };
    const cell: WorkflowCellInput = {
      id: 'sampler',
      nodeId: 'sampler',
      props: {
        lfDataset: dataset,
        lfTextfieldProps: textfieldProps,
        lfValue: 'euler',
      },
      shape,
    };

    const select = createInputCell(cell) as HTMLLfSelectElement;

    expect(select.tagName).toBe('LF-SELECT');
    expect(select.lfDataset).toEqual(dataset);
    expect(select.lfTextfieldProps).toEqual(textfieldProps);
    expect(select.lfValue).toBe('euler');
  });
});
