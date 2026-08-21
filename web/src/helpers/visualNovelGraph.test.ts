import { describe, expect, it } from 'vitest';
import { collectIdentityCandidates } from './visualNovelGraph';

describe('collectIdentityCandidates', () => {
  it('does not expose identities from strict-invalid duplicate-key bodies', () => {
    const origin = {
      comfyClass: 'LF_VNCompile',
      graph: { _nodes: [] as NodeType[] },
      widgets: [],
    } as unknown as NodeType;
    const invalidSource = {
      comfyClass: 'LF_SceneSpec',
      graph: origin.graph,
      widgets: [{
        type: 'LF_TEXTAREA',
        options: {
          getState: () => ({ idPaths: [{ path: '/choices/*', kind: 'choice' }] }),
          getValue: () => '{"choices":[{"id":"lf:choice:first","id":"lf:choice:second"}]}',
        },
      }],
    } as unknown as NodeType;
    origin.graph._nodes.push(origin, invalidSource);

    expect(collectIdentityCandidates(origin, 'choice')).toEqual([]);
  });
});
