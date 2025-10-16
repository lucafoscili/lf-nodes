import { build } from 'esbuild';
import { readFile as fsReadFile, writeFile as fsWriteFile, mkdir } from 'fs/promises';
import * as sass from 'sass';
import path from 'path';
const outDir = path.resolve('web/deploy_workflow_app/js');
const srcEntry = path.resolve('web/src/workflow/index.ts');
const outFile = path.join(outDir, 'submit-prompt.js');
const htmlSrc = path.resolve('web/src/workflow/index.html');
const htmlOut = path.resolve('web/deploy_workflow_app/submit-prompt.html');

const logColor = '\x1b[36m%s\x1b[0m'; // cyan

async function ensureDir(dir) {
  try {
    await mkdir(dir, { recursive: true });
  } catch (_) {}
}

async function run() {
  console.log(logColor, '*-------------------------------------------*');
  console.log(logColor, '*   B u i l d   W o r k f l o w   A p p     *');
  console.log(logColor, '*-------------------------------------------*');
  console.log(logColor, '*---*');
  await ensureDir(outDir);
  try {
    await build({
      entryPoints: [srcEntry],
      bundle: true,
      sourcemap: false,
      format: 'esm',
      target: ['es2020'],
      outfile: outFile,
      minify: false,
    });
    console.log(logColor, '✓ Built' + outFile);
  } catch (err) {
    console.error(logColor, 'Build failed', err);
    process.exit(1);
  }

  try {
    const html = await fsReadFile(htmlSrc, 'utf8');
    const rewritten = html.replace(
      /<script[^>]*type=["']module["'][^>]*><\/script>|<script[^>]*src=["'][^"']+["'][^>]*><\/script>/i,
      '',
    );
    try {
      const cssOutDir = path.resolve('web/deploy_workflow_app/css');
      try {
        await mkdir(cssOutDir, { recursive: true });
      } catch (_) {}
      const scssPath = path.resolve('web/src/workflow/styles/global.scss');
      const cssOutFile = path.join(cssOutDir, 'submit-prompt.css');
      // Use the modern Dart Sass JS API to avoid the legacy-js-api deprecation
      // warning. `sass.compile` returns an object with a `.css` property.
      const cssResult = sass.compile(scssPath, { style: 'compressed' });
      await fsWriteFile(cssOutFile, cssResult.css);
      console.log(logColor, ' ✓ Built CSS' + cssOutFile);
    } catch (cssErr) {
      console.warn(
        logColor,
        '⚠️  Failed to compile workflow SCSS, continuing without dedicated CSS:',
        cssErr && cssErr.message ? cssErr.message : cssErr,
      );
    }

    const cssLink = `<link rel="stylesheet" href="/api/lf-nodes/static-workflow/css/submit-prompt.css">`;
    const scriptTag = `<script type="module" src="/api/lf-nodes/static-workflow/js/submit-prompt.js"></script>`;
    let finalHtml = rewritten.replace('</head>', `  ${cssLink}\n</head>`);
    finalHtml = finalHtml.replace('</body>', `  ${scriptTag}\n</body>`);
    await fsWriteFile(htmlOut, finalHtml, 'utf8');
    console.log(logColor, '✓ Wrote production HTML to' + htmlOut);
  } catch (err) {
    console.error(logColor, 'Failed to copy HTML', err);
  }

  console.log(logColor, '*---*');
}

run();
