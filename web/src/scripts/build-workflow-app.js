import { build } from 'esbuild';
import { readFile as fsReadFile, writeFile as fsWriteFile, mkdir } from 'fs/promises';
import path from 'path';
import * as sass from 'sass';
const outDir = path.resolve('web/deploy_workflow_runner/js');
const srcEntry = path.resolve('web/src/workflow-runner/index.ts');
const outFile = path.join(outDir, 'workflow-runner.js');
const htmlSrc = path.resolve('web/src/workflow-runner/index.html');
const htmlOut = path.resolve('web/deploy_workflow_runner/workflow-runner.html');

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
      sourcemap: true,
      format: 'esm',
      target: ['es2020'],
      outfile: outFile,
      minify: false,
    });
    console.log(logColor, '✅ Built ' + outFile);
  } catch (err) {
    console.error(logColor, '❌ Build failed', err);
    process.exit(1);
  }

  try {
    const html = await fsReadFile(htmlSrc, 'utf8');
    const rewritten = html.replace(
      /<script[^>]*type=["']module["'][^>]*><\/script>|<script[^>]*src=["'][^"']+["'][^>]*><\/script>/i,
      '',
    );
    try {
      const cssOutDir = path.resolve('web/deploy_workflow_runner/css');
      try {
        await mkdir(cssOutDir, { recursive: true });
      } catch (_) {}
      const scssPath = path.resolve('web/src/workflow-runner/styles/global.scss');
      const cssOutFile = path.join(cssOutDir, 'workflow-runner.css');
      const cssResult = sass.compile(scssPath, { style: 'compressed' });
      await fsWriteFile(cssOutFile, cssResult.css);
      console.log(logColor, '✅ Built CSS' + cssOutFile);
    } catch (cssErr) {
      console.warn(
        logColor,
        '⚠️ Failed to compile workflow SCSS, continuing without dedicated CSS:',
        cssErr && cssErr.message ? cssErr.message : cssErr,
      );
    }

    const cssLink = `<link rel="stylesheet" href="/api/lf-nodes/static-workflow-runner/css/workflow-runner.css">`;
    const scriptTag = `<script type="module" src="/api/lf-nodes/static-workflow-runner/js/workflow-runner.js"></script>`;
    let finalHtml = rewritten.replace('</head>', `  ${cssLink}\n</head>`);
    finalHtml = finalHtml.replace('</body>', `  ${scriptTag}\n</body>`);
    await fsWriteFile(htmlOut, finalHtml, 'utf8');
    console.log(logColor, '✅ Wrote production HTML to ' + htmlOut);
  } catch (err) {
    console.error(logColor, '❌ Failed to copy HTML', err);
  }

  console.log(logColor, '*---*');
}

run();
