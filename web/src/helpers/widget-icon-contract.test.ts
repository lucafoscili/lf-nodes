import { LF_ICONS_REGISTRY } from '@lf-widgets/foundations';
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

const ICON_PATTERN = /["']icon["']\s*:\s*["']([^"']+)["']/g;
const ICON_PRODUCERS = [
  '../../../modules/nodes/io/save_dds.py',
  '../../../modules/nodes/image/resize_image_by_edge.py',
  '../../../modules/nodes/image/resize_image_to_dimension.py',
  '../../../modules/nodes/image/resize_image_to_square.py',
];

describe('Python widget icon contracts', () => {
  it('uses names from the installed LF Widgets icon registry', () => {
    const installedIcons = new Set<string>(Object.values(LF_ICONS_REGISTRY));

    for (const relativePath of ICON_PRODUCERS) {
      const source = readFileSync(new URL(relativePath, import.meta.url), 'utf8');
      const usedIcons = Array.from(source.matchAll(ICON_PATTERN), (match) => match[1]);

      expect(usedIcons.length, `${relativePath} should declare widget icons`).toBeGreaterThan(0);
      for (const icon of usedIcons) {
        expect(installedIcons.has(icon), `${relativePath} uses unknown icon ${icon}`).toBe(true);
      }
    }
  });
});
