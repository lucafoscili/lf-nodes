import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import { PRIVATE_VOCABULARY } from '../sanitize_titanic.mts';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');

// Every tracked text file is public. Exempt: the generated bundle, the
// license and package manifest (they carry the author's name), and the
// sanitizers and their tests, which name the words they scrub or reject.
const EXEMPT_PREFIXES = ['web/deploy/'];
const EXEMPT_FILES = new Set([
  'LICENSE',
  'package.json',
  'scripts/quality/sanitize_example_workflows.mts',
  'scripts/quality/sanitize_titanic.mts',
  'scripts/quality/tests/sanitize_example_workflows.test.ts',
  'scripts/quality/tests/sanitize_titanic.test.ts',
]);

const trackedPublicFiles = (): string[] =>
  execFileSync('git', ['ls-files', '-z'], {
    cwd: repoRoot,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  })
    .split('\0')
    .filter(
      (path) =>
        path &&
        !EXEMPT_FILES.has(path) &&
        !EXEMPT_PREFIXES.some((prefix) => path.startsWith(prefix)),
    );

describe('public vocabulary', () => {
  it('keeps private project and personal words out of public files', () => {
    const files = trackedPublicFiles();
    expect(files.length).toBeGreaterThan(0);

    const findings: string[] = [];
    for (const path of files) {
      const bytes = readFileSync(resolve(repoRoot, path));
      if (bytes.includes(0)) continue;
      bytes
        .toString('utf8')
        .normalize('NFKC')
        .split('\n')
        .forEach((line, index) => {
          if (PRIVATE_VOCABULARY.test(line)) findings.push(`${path}:${index + 1}`);
        });
    }

    expect(findings).toEqual([]);
  });
});
