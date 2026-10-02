// @vitest-environment node
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, it } from 'vitest';

it('copies SVGs with canonical LF bytes without changing fonts or source assets', () => {
  const root = mkdtempSync(path.join(tmpdir(), 'lf-widget-copy-'));
  try {
    const assets = path.join(root, 'node_modules', '@lf-widgets', 'assets', 'assets');
    const svg = path.join(assets, 'svg');
    const fonts = path.join(assets, 'fonts');
    mkdirSync(svg, { recursive: true });
    mkdirSync(fonts, { recursive: true });
    const crlfSvg = '<svg>\r\n  <path d="M0 0"/>\r\n</svg>\r\n';
    const lfSvg = '<svg>\n</svg>\n';
    const font = Buffer.from([0, 13, 10, 255]);
    writeFileSync(path.join(svg, 'crlf.svg'), crlfSvg);
    writeFileSync(path.join(svg, 'lf.svg'), lfSvg);
    writeFileSync(path.join(fonts, 'fixture.woff2'), font);

    execFileSync(process.execPath, [fileURLToPath(new URL('./copy-widgets.js', import.meta.url))], {
      cwd: root,
      timeout: 30_000,
    });

    const output = path.join(root, 'web', 'deploy', 'assets');
    expect(readFileSync(path.join(output, 'svg', 'crlf.svg'), 'utf8')).toBe(crlfSvg.replace(/\r\n/g, '\n'));
    expect(readFileSync(path.join(output, 'svg', 'lf.svg'), 'utf8')).toBe(lfSvg);
    expect(readFileSync(path.join(output, 'fonts', 'fixture.woff2'))).toEqual(font);
    expect(readFileSync(path.join(svg, 'crlf.svg'), 'utf8')).toBe(crlfSvg);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
