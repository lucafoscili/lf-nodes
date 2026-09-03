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

  it('renders profile tiers with a consistent icon and tone', () => {
    const nodes = [
      {
        id: 'fast',
        profileTier: 'fast',
        value: 'Fast',
        workflowValue: 'quick_recipe',
      },
      {
        id: 'baseline',
        profileTier: 'baseline',
        value: 'Baseline',
        workflowValue: 'stable_recipe',
      },
      {
        id: 'quality',
        profileTier: 'quality',
        value: 'Quality',
        workflowValue: 'hero_recipe',
      },
    ] as const;
    const helper = { showWhenFocused: false, value: 'What this knob changes.' };
    const cell: WorkflowCellInput = {
      id: 'profile',
      nodeId: 'sampler',
      props: {
        lfDataset: { nodes: [...nodes] },
        lfTextfieldProps: { lfHelper: helper, lfLabel: 'Profile' },
        lfValue: 'baseline',
      },
      shape: 'select',
    };

    const select = createInputCell(cell) as HTMLLfSelectElement;

    expect(select.lfUiState).toBe('primary');
    expect(select.lfTextfieldProps).toMatchObject({
      lfHelper: helper,
      lfIcon: 'contrast-2',
      lfLabel: 'Profile',
    });
    expect(select.lfDataset.nodes.map((node) => node.icon)).toEqual([
      'stopwatch',
      'contrast-2',
      'wand',
    ]);

    select.dispatchEvent(
      new CustomEvent('lf-select-event', {
        detail: { eventType: 'change', node: nodes[0] },
      }),
    );
    expect(select.lfUiState).toBe('info');
    expect(select.lfTextfieldProps?.lfIcon).toBe('stopwatch');

    select.dispatchEvent(
      new CustomEvent('lf-select-event', {
        detail: { eventType: 'change', node: nodes[2] },
      }),
    );
    expect(select.lfUiState).toBe('secondary');
    expect(select.lfTextfieldProps?.lfIcon).toBe('wand');
  });

  it('replaces LF Select’s implicit primary default with the selected tier tone', () => {
    const createElement = document.createElement.bind(document);
    const createElementSpy = vi
      .spyOn(document, 'createElement')
      .mockImplementation((tagName, options) => {
        const element = createElement(tagName, options);
        if (tagName.toLowerCase() === 'lf-select') {
          (element as HTMLLfSelectElement).lfUiState = 'primary';
        }
        return element;
      });

    try {
      const select = createInputCell({
        id: 'profile',
        nodeId: 'sampler',
        props: {
          lfDataset: {
            nodes: [
              {
                id: 'fast',
                profileTier: 'fast',
                value: 'Fast',
                workflowValue: 'quick_recipe',
              },
            ],
          },
          lfValue: 'fast',
        },
        shape: 'select',
      }) as HTMLLfSelectElement;

      expect(select.lfUiState).toBe('info');
      expect(select.lfTextfieldProps?.lfIcon).toBe('stopwatch');
    } finally {
      createElementSpy.mockRestore();
    }
  });

  it('resolves numeric defaults without replacing a functional UI state', () => {
    const nodes = [
      {
        id: 'fast',
        profileTier: 'fast' as const,
        value: 'Fast',
        workflowValue: 'quick_recipe',
      },
      {
        id: 'quality',
        profileTier: 'quality' as const,
        value: 'Quality',
        workflowValue: 'hero_recipe',
      },
    ];
    const cell: WorkflowCellInput = {
      id: 'profile',
      nodeId: 'sampler',
      props: {
        lfDataset: { nodes },
        lfUiState: 'disabled',
        lfValue: 0,
      },
      shape: 'select',
    };

    const select = createInputCell(cell) as HTMLLfSelectElement;

    expect(select.lfUiState).toBe('disabled');
    expect(select.lfTextfieldProps?.lfIcon).toBe('stopwatch');

    select.dispatchEvent(
      new CustomEvent('lf-select-event', {
        detail: {
          eventType: 'change',
          node: nodes[1],
        },
      }),
    );
    expect(select.lfUiState).toBe('disabled');
    expect(select.lfTextfieldProps?.lfIcon).toBe('wand');
  });

  it.each(['constructor', 'toString'])('ignores inherited profile tier key %s', (profileTier) => {
    const node = {
      id: profileTier,
      profileTier,
      value: 'Unknown tier',
      workflowValue: 'unchanged_recipe',
    };
    const select = createInputCell({
      id: 'profile',
      nodeId: 'sampler',
      props: {
        lfDataset: { nodes: [node as any] },
        lfValue: profileTier,
      },
      shape: 'select',
    }) as HTMLLfSelectElement;

    expect(select.lfDataset.nodes).toEqual([node]);
    expect(select.lfUiState).toBeUndefined();
    expect(select.lfTextfieldProps).toBeUndefined();
  });
});
