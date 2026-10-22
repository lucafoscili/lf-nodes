import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import { PRIVATE_VOCABULARY } from '../sanitize_titanic.mts';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');

// Public text: documentation, scripts, node sources and the Runner catalogue.
const SCANNED_ROOTS = ['docs', 'scripts', 'modules/nodes', 'modules/workflow_runner/workflows'];

// The sanitizers and their tests name the words they scrub or reject.
const EXEMPT = [
  'scripts/quality/sanitize_example_workflows.mts',
  'scripts/quality/sanitize_titanic.mts',
  'scripts/quality/tests/',
];

const trackedPublicFiles = (): string[] =>
  execFileSync('git', ['ls-files', '-z', '--', ...SCANNED_ROOTS], {
    cwd: repoRoot,
    encoding: 'utf8',
  })
    .split('\0')
    .filter((path) => path && !EXEMPT.some((exempt) => path.startsWith(exempt)));

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
