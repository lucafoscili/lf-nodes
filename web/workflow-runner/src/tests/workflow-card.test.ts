import { describe, expect, it, vi } from 'vitest';
import { buildAssetsUrl } from '../config';
import { resolveWorkflowHeroUrl, workflowCardPresentation } from '../utils/workflow-card';

vi.mock('../config', () => ({
  buildAssetsUrl: vi.fn(() => `${window.location.origin}/api/lf-nodes/static/assets/`),
}));

describe('workflow card presentation boundary', () => {
  it.each(['portrait.webp', 'before-after.PNG', 'v1/output.jpg', 'result.jpeg', 'result.avif'])(
    'resolves a local catalogue raster (%s)',
    (asset) => {
      expect(resolveWorkflowHeroUrl(asset)).toBe(
        `${window.location.origin}/api/lf-nodes/static/assets/workflow-runner/heroes/${asset}`,
      );
    },
  );

  it.each([
    undefined, null, {}, 7, '', ' ', '/portrait.png', '//external.test/a.png',
    'https://external.test/a.png', 'http://localhost/a.png', '../a.png', 'a/../b.png',
    './a.png', 'a//b.png', 'a\\b.png', '%2e%2e/a.png', 'a.png?token=secret',
    'a.png#x', 'data:image/png;base64,aaa', 'blob:https://external.test/a.png',
    'file:///a.png', 'C:/a.png', 'a.svg', 'a.gif', 'a.html', 'a.png\n',
    'a./b.png', 'a..b.png', `${'a'.repeat(240)}.png`,
  ])('rejects a malformed or non-local hero (%s)', (asset) => {
    expect(resolveWorkflowHeroUrl(asset)).toBeUndefined();
  });

  it('fails closed if asset configuration resolves off-origin', () => {
    vi.mocked(buildAssetsUrl).mockReturnValueOnce('https://external.test/assets/');
    expect(resolveWorkflowHeroUrl('portrait.png')).toBeUndefined();
  });

  it.each([undefined, null, [], 'summary', {}, { summary: '' }, { summary: 'a\nb' },
    { summary: 'a\u0085b' }, { summary: 'a\u2028b' }, { summary: 'a\u2029b' },
    { summary: 'x'.repeat(181) }])('keeps the legacy card for malformed metadata (%s)', (value) => {
    expect(workflowCardPresentation(value)).toBeUndefined();
  });

  it('normalizes visible copy and preserves the accessible comparison description', () => {
    expect(workflowCardPresentation({
      summary: '  Restore  detail. ',
      hero: { asset: 'restore-before-after.webp', alt: 'Before: noisy face. After: restored face.' },
    })).toEqual({
      summary: 'Restore detail.',
      hero: {
        url: `${window.location.origin}/api/lf-nodes/static/assets/workflow-runner/heroes/restore-before-after.webp`,
        alt: 'Before: noisy face. After: restored face.',
      },
    });
  });

  it.each([undefined, null, [], {}, { asset: 'x.png', alt: '' },
    { asset: 'x.png', alt: 'x'.repeat(501) }, { asset: 'https://elsewhere/x.png', alt: 'Output' }])(
    'retains the summary without an absent or invalid hero (%s)',
    (hero) => expect(workflowCardPresentation({ summary: 'Output preview.', hero })).toEqual({
      summary: 'Output preview.',
    }),
  );
});
