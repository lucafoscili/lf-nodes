import { describe, expect, it, vi } from 'vitest';
import { resolveLfExtensionUrl } from './extensionUrl';

describe('resolveLfExtensionUrl', () => {
  it.each([
    [
      'root',
      'http://127.0.0.1:8188/',
      'http://127.0.0.1:8188/extensions/lf-nodes/assets',
    ],
    [
      'hash tab',
      'http://127.0.0.1:8188/#8cadf405-98db-41d7-aeee-70f4633d770e',
      'http://127.0.0.1:8188/extensions/lf-nodes/assets',
    ],
    [
      'query',
      'http://127.0.0.1:8188/?preview=1#workflow',
      'http://127.0.0.1:8188/extensions/lf-nodes/assets',
    ],
    [
      'subpath',
      'https://example.test/comfy/#workflow',
      'https://example.test/comfy/extensions/lf-nodes/assets',
    ],
  ])('resolves from a %s app URL', (_name, href, expected) => {
    expect(resolveLfExtensionUrl('assets', { href })).toBe(expected);
  });

  it('uses Comfy fileURL so reverse-proxy paths remain authoritative', () => {
    const fileURL = vi.fn((route: string) => `/comfy-proxy${route}`);

    expect(
      resolveLfExtensionUrl('assets/svg/photo-search.svg', {
        api: { fileURL },
        href: 'https://example.test/ignored/#workflow',
      }),
    ).toBe(
      'https://example.test/comfy-proxy/extensions/lf-nodes/assets/svg/photo-search.svg',
    );
    expect(fileURL).toHaveBeenCalledWith(
      '/extensions/lf-nodes/assets/svg/photo-search.svg',
    );
  });
});
