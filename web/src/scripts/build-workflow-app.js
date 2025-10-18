import { access, readFile as fsReadFile, writeFile as fsWriteFile, mkdir } from 'fs/promises';
import path from 'path';
import * as sass from 'sass';

const deployRoot = path.resolve('web/deploy');
const workflowRunnerRoot = path.join(deployRoot, 'workflow-runner');
const outDir = path.join(workflowRunnerRoot, 'js');
const cssOutDir = path.join(workflowRunnerRoot, 'css');
const outFile = path.join(outDir, 'workflow-runner.js');
const htmlSrc = path.resolve('web/workflow-runner/src/index.html');
const htmlOut = path.join(workflowRunnerRoot, 'workflow-runner.html');

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
    await access(outFile);
  } catch {
    console.error(
      logColor,
      `Missing workflow runner bundle at ${outFile}. Did Vite finish building the multi-entry bundle?`,
    );
    process.exit(1);
  }

  try {
    const html = await fsReadFile(htmlSrc, 'utf8');
    const rewritten = html.replace(
      /<script[^>]*type=["']module["'][^>]*><\/script>|<script[^>]*src=["'][^"']+["'][^>]*><\/script>/i,
      '',
    );

    try {
      await ensureDir(cssOutDir);
      const scssPath = path.resolve('web/workflow-runner/src/styles/global.scss');
      const cssOutFile = path.join(cssOutDir, 'workflow-runner.css');
      const cssResult = sass.compile(scssPath, { style: 'compressed' });
      await fsWriteFile(cssOutFile, cssResult.css);
      console.log(logColor, 'Built CSS: ' + cssOutFile);
    } catch (cssErr) {
      console.warn(
        logColor,
        'Failed to compile workflow SCSS, continuing without dedicated CSS:',
        cssErr && cssErr.message ? cssErr.message : cssErr,
      );
    }

    const cssLink = `<link rel="stylesheet" href="/api/lf-nodes/static-workflow-runner/css/workflow-runner.css">`;
    const scriptTag = `<script type="module" src="/api/lf-nodes/static-workflow-runner/js/workflow-runner.js"></script>`;
    let finalHtml = rewritten.replace('</head>', `  ${cssLink}\n</head>`);
    finalHtml = finalHtml.replace('</body>', `  ${scriptTag}\n</body>`);
    await fsWriteFile(htmlOut, finalHtml, 'utf8');
    console.log(logColor, 'Wrote production HTML: ' + htmlOut);
  } catch (err) {
    console.error(logColor, 'Failed to copy HTML', err);
  }

  console.log(logColor, '*---*');
}

run();
