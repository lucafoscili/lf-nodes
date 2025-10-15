import { build } from 'esbuild';
import { readFile as fsReadFile, writeFile as fsWriteFile, mkdir } from 'fs/promises';
import sass from 'sass';
import path from 'path';

const outDir = path.resolve('web/deploy/js');
const srcEntry = path.resolve('web/src/workflow/main.ts');
const outFile = path.join(outDir, 'submit-prompt.js');
const htmlSrc = path.resolve('web/src/workflow/index.html');
const htmlOut = path.resolve('web/deploy/submit-prompt.html');

async function ensureDir(dir) {
  try {
    await mkdir(dir, { recursive: true });
  } catch (_) {}
}

async function run() {
  console.log('* Building submit-prompt bundle...');
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
    console.log('✓ Built', outFile);
  } catch (err) {
    console.error('Build failed', err);
    process.exit(1);
  }

  try {
    // Read source HTML and rewrite the module import to point to the
    // production-built bundle (relative path into deploy/js). This makes
    // the copied HTML load the minimal submit-prompt.js bundle in prod.
    const html = await fsReadFile(htmlSrc, 'utf8');
    // Replace any <script type="module" src="..."> with the production bundle
    const rewritten = html.replace(
      /<script[^>]*type=["']module["'][^>]*><\/script>|<script[^>]*src=["'][^"']+["'][^>]*><\/script>/i,
      '',
    );
    // Build a small dedicated CSS file for the workflow UI so we don't pull
    // in the large global _index.css intended for the full Comfy UI.
    try {
      const cssOutDir = path.resolve('web/deploy/css');
      try {
        await mkdir(cssOutDir, { recursive: true });
      } catch (_) {}
      const scssPath = path.resolve('web/src/workflow/styles.scss');
      const cssOutFile = path.join(cssOutDir, 'submit-prompt.css');
      const cssResult = sass.renderSync({ file: scssPath, outputStyle: 'compressed' });
      await fsWriteFile(cssOutFile, cssResult.css);
      console.log('✓ Built CSS', cssOutFile);
    } catch (cssErr) {
      console.warn(
        '⚠️  Failed to compile workflow SCSS, continuing without dedicated CSS:',
        cssErr && cssErr.message ? cssErr.message : cssErr,
      );
    }

    const cssLink = `<link rel="stylesheet" href="/api/lf-nodes/static/css/submit-prompt.css">`;
    const scriptTag = `<script type="module" src="/api/lf-nodes/static/js/submit-prompt.js"></script>`;
    let finalHtml = rewritten.replace('</head>', `  ${cssLink}\n</head>`);
    finalHtml = finalHtml.replace('</body>', `  ${scriptTag}\n</body>`);
    await fsWriteFile(htmlOut, finalHtml, 'utf8');
    console.log('✓ Wrote production HTML to', htmlOut);
  } catch (err) {
    console.error('Failed to copy HTML', err);
  }
}

run();
