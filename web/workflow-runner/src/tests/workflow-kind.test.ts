import { describe, expect, it } from 'vitest';
import {
  isWorkflowOrchestra,
  normalizeWorkflowDatasetKinds,
  normalizeWorkflowKind,
} from '../utils/workflow-kind';

describe('workflow kind taxonomy', () => {
  it.each([
    ['block', 'block'],
    ['workflow', 'block'],
    [undefined, 'block'],
    ['unexpected', 'block'],
    ['orchestra', 'orchestra'],
    ['sequence', 'orchestra'],
  ] as const)('normalizes %s to %s', (input, expected) => {
    expect(normalizeWorkflowKind(input)).toBe(expected);
  });

  it('uses the shared predicate for canonical and legacy orchestras', () => {
    expect(isWorkflowOrchestra({ kind: 'orchestra' })).toBe(true);
    expect(isWorkflowOrchestra({ kind: 'sequence' })).toBe(true);
    expect(isWorkflowOrchestra({ kind: 'workflow' })).toBe(false);
    expect(isWorkflowOrchestra({})).toBe(false);
  });

  it('returns a canonically typed dataset without mutating the wire payload', () => {
    const source = {
      nodes: [
        { id: 'missing' },
        { id: 'legacy-block', kind: 'workflow' },
        { id: 'legacy-orchestra', kind: 'sequence' },
        { id: 'block', kind: 'block' },
        { id: 'orchestra', kind: 'orchestra' },
      ],
    } as any;

    const normalized = normalizeWorkflowDatasetKinds(source);

    expect(normalized.nodes.map((node) => node.kind)).toEqual([
      'block',
      'block',
      'orchestra',
      'block',
      'orchestra',
    ]);
    expect(source.nodes[0].kind).toBeUndefined();
    expect(source.nodes[2].kind).toBe('sequence');
  });
});
