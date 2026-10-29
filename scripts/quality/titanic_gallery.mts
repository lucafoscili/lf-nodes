import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, extname, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import playwright from 'playwright';

import type { TitanicPayloads } from './titanic_e2e_core.ts';

type JsonRecord = Record<string, any>;
export interface GalleryRender {
  evidenceIndex: number;
  caseId: string;
  nodeId: string;
  nodeType: string;
  payloadIndex: number;
  widget: string;
  role: 'default' | 'alternative';
  file: string;
  outcome?: 'PASS' | 'FAIL';
  error?: string;
}

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const usage = `LF Titanic widget gallery
Usage: corepack yarn titanic:gallery --run DIR [--run DIR] --out DIR
  --alternative NODE=WIDGET  Add a view (repeatable; e.g. LF_RegionColorStats=countBarChart).
  --node NODE                Render only this node type (repeatable).
  --bundle-dir DIR           Built LF web/deploy folder (default: repository web/deploy).
  --comfy-url URL            Preview origin (default: http://127.0.0.1:8188).
  --browser-channel NAME     Installed browser channel, e.g. msedge.
No workflow is opened or submitted. Only saved UI outputs and preview assets are read.`;

export function parseGalleryArgs(args: string[]) {
  const options = {
    runs: [] as string[], out: '', bundleDir: resolve(repoRoot, 'web/deploy'),
    comfyUrl: 'http://127.0.0.1:8188', browserChannel: undefined as string | undefined,
    alternatives: {} as Record<string, string[]>, nodes: [] as string[],
  };
  for (let index = 0; index < args.length; index++) {
    const flag = args[index];
    if (flag === '--') continue;
    const value = args[++index];
    if (!value || value.startsWith('--')) throw new Error(`${flag}: missing value`);
    switch (flag) {
      case '--run': options.runs.push(resolve(value)); break;
      case '--out': options.out = resolve(value); break;
      case '--bundle-dir': options.bundleDir = resolve(value); break;
      case '--comfy-url': options.comfyUrl = value; break;
      case '--browser-channel': options.browserChannel = value; break;
      case '--node': options.nodes.push(value); break;
      case '--alternative': {
        const [node, widget, extra] = value.split('=');
        if (!node || !widget || extra) throw new Error('--alternative expects NODE=WIDGET');
        (options.alternatives[node] ??= []).push(widget);
        break;
      }
      default: throw new Error(`Unknown option: ${flag}`);
    }
  }
  if (!options.runs.length || !options.out) throw new Error('--run and --out are required');
  return options;
}

// The built bundle supplies both registries; do not copy node defaults here.
export function planGallery(
  evidence: TitanicPayloads[], defaults: Record<string, string[]>,
  widgetNames: Record<string, string>, alternatives: Record<string, string[]> = {},
  selectedNodes: string[] = [],
): GalleryRender[] {
  const names = new Set(Object.values(widgetNames));
  const normalize = (name: string) => {
    const widget = widgetNames[name] ?? name;
    if (!names.has(widget)) throw new Error(`Unknown widget: ${name}`);
    return widget;
  };
  const renders: GalleryRender[] = [];
  for (const [evidenceIndex, run] of evidence.entries()) {
    if (run.schema !== 'lf.titanic-payloads.v1') throw new Error('Unsupported payload evidence schema');
    for (const node of run.nodes) {
      if (selectedNodes.length && !selectedNodes.includes(node.nodeType)) continue;
      const defaultWidgets = (defaults[node.nodeType] ?? []).map(normalize);
      const views = [...new Set([...defaultWidgets, ...(alternatives[node.nodeType] ?? []).map(normalize)])];
      if (!views.length) throw new Error(`${node.nodeType}: NODE_WIDGET_MAP has no widget; name an alternative`);
      const payloads = (node.ui as JsonRecord).lf_output ?? [node.ui];
      if (!Array.isArray(payloads) || !payloads.length) throw new Error(`${node.nodeType}: no UI payloads`);
      for (let payloadIndex = 0; payloadIndex < payloads.length; payloadIndex++) {
        for (const widget of views) {
          renders.push({
            evidenceIndex, caseId: run.caseId, nodeId: node.nodeId, nodeType: node.nodeType, payloadIndex,
            widget: normalize(widget), role: defaultWidgets.includes(widget) ? 'default' : 'alternative',
            file: `${String(renders.length + 1).padStart(3, '0')}-${node.nodeType.replace(/[^a-zA-Z0-9_-]/g, '_')}-${widget}.png`,
          });
        }
      }
    }
  }
  for (const node of [...selectedNodes, ...Object.keys(alternatives)]) {
    if (!renders.some((render) => render.nodeType === node)) throw new Error(`${node}: no saved payload`);
  }
  if (!renders.length) throw new Error('No saved payloads to render');
  return renders;
}

export const galleryManifest = (renders: GalleryRender[]) => ({
  schema: 'lf.titanic-gallery.v1', renders: renders.map((render) => ({ ...render })),
});

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#191a20;color:#e8e9ee;font:16px system-ui}
main{box-sizing:border-box;width:960px;padding:24px}h1{font-size:22px;margin:0 0 6px}
p{color:#b9bdca;margin:0 0 20px}#widget{width:912px;height:680px}
#widget>div{width:100%;height:100%;position:relative}*{box-sizing:border-box}
</style></head><body><main><h1 id="title"></h1><p id="label"></p><div id="widget"></div></main>
<script>var comfyAPI = {}; globalThis.__name = (value) => value;</script><script type="module">
import { NODE_WIDGET_MAP, CustomWidgetName, initLfManager, getLfManager } from '/extensions/lf-nodes/js/lf-nodes.js';
const graph = { getNodeById: () => window.galleryNode, setDirtyCanvas() {} };
comfyAPI = { api: { api: { fileURL: path => path } }, app: { app: { graph } } };
initLfManager();
const manager = getLfManager();
manager.log = (message, details, severity) => { if (severity === 'error' || severity === 'warning') console.error(message); };
window.gallery = { defaults: structuredClone(NODE_WIDGET_MAP), widgetNames: CustomWidgetName,
  render(spec, payload) {
    if (!payload || !Object.keys(payload).length) throw new Error('Saved UI output is empty');
    document.querySelector('#title').textContent = spec.nodeType;
    document.querySelector('#label').textContent = spec.widget + ' · ' + spec.role + ' · ' + spec.caseId + ' · node ' + spec.nodeId;
    const host = document.querySelector('#widget'); host.replaceChildren(); host.style.height = '680px';
    const node = window.galleryNode = { id: spec.nodeId, comfyClass: spec.nodeType, widgets: [], size: [912,680],
      addDOMWidget(name, type, element, options) {
        const widget = { name, type, element, options, value: '' };
        this.widgets.push(widget); host.append(element); return widget;
      }, setSize() {}, setDirtyCanvas() {} };
    // Isolated gallery page only: production registration and defaults stay untouched.
    NODE_WIDGET_MAP[spec.nodeType] = [spec.widget];
    const widgets = manager.getManagers().widgets;
    widgets.render(spec.widget)(node);
    this.before = JSON.stringify(node.widgets[0].options.getValue());
    widgets.onEvent(spec.nodeType, new CustomEvent('lf-result', { detail: { ...payload, node: spec.nodeId } }), [spec.widget]);
  }
};
</script></body></html>`;

export async function renderGallery(options: ReturnType<typeof parseGalleryArgs>) {
  const evidence: TitanicPayloads[] = [];
  for (const run of options.runs) {
    const directory = resolve(run, 'payloads');
    for (const file of (await readdir(directory)).filter((name) => name.endsWith('.json')).sort()) {
      evidence.push(JSON.parse(await readFile(resolve(directory, file), 'utf8')));
    }
  }
  const bundle = await readFile(resolve(options.bundleDir, 'js/lf-nodes.js'), 'utf8');
  await mkdir(options.out, { recursive: true });
  const browser = await playwright.chromium.launch({ headless: true, channel: options.browserChannel });
  const renders: GalleryRender[] = [];
  try {
    const context = await browser.newContext({ viewport: { width: 960, height: 800 }, deviceScaleFactor: 1 });
    let errors: string[] = [];
    await context.route('**/*', async (route) => {
      const url = new URL(route.request().url());
      try {
        if (url.pathname === '/') return await route.fulfill({ contentType: 'text/html', body: html });
        if (url.pathname.startsWith('/extensions/lf-nodes/')) {
          const relative = decodeURIComponent(url.pathname.slice('/extensions/lf-nodes/'.length));
          const path = resolve(options.bundleDir, relative);
          if (!path.startsWith(resolve(options.bundleDir) + sep)) throw new Error(`Invalid asset: ${relative}`);
          const types: Record<string, string> = { '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };
          const body = relative === 'js/lf-nodes.js'
            ? Buffer.from(bundle + '\nexport { NODE_WIDGET_MAP, CustomWidgetName, initLfManager, getLfManager };\n', 'utf8')
            : await readFile(path);
          return await route.fulfill({ contentType: types[extname(path)] ?? 'application/octet-stream', body });
        }
        // Payload previews use Comfy's generated-preview endpoint. Never submit work.
        const target = new URL(url.pathname + url.search, options.comfyUrl);
        if (url.pathname !== '/view' || route.request().method() !== 'GET') throw new Error(`Unsupported gallery request: ${url.pathname}`);
        const response = await context.request.get(target.href, { timeout: 30_000 });
        if (!response.ok()) throw new Error(`Preview HTTP ${response.status()}: ${url.pathname}`);
        await route.fulfill({ response });
      } catch (error) {
        errors.push(String(error));
        await route.abort();
      }
    });
    const page = await context.newPage();
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
    await page.goto('http://lf-gallery.local/');
    await page.waitForFunction(() => Boolean((window as any).gallery), null, { timeout: 30_000 });
    if (errors.length) throw new Error(errors.join('; '));
    const registry = await page.evaluate(() => ({ defaults: (window as any).gallery.defaults, widgets: (window as any).gallery.widgetNames }));
    renders.push(...planGallery(evidence, registry.defaults, registry.widgets, options.alternatives, options.nodes));
    for (const render of renders) {
      errors = [];
      try {
        const node = evidence[render.evidenceIndex].nodes.find((node) => node.nodeId === render.nodeId);
        const payload = (node!.ui as JsonRecord).lf_output?.[render.payloadIndex] ?? node!.ui;
        await page.evaluate(({ render, payload }) => (window as any).gallery.render(render, payload), { render, payload });
        await page.waitForFunction(() => {
          const value = (window as any).galleryNode.widgets[0].options.getValue();
          return value && JSON.stringify(value) !== (window as any).gallery.before;
        }, null, { timeout: 10_000 }).catch(() => { throw new Error('Payload did not populate this widget'); });
        // Walk nested web-component shadows: outer readiness alone misses images/charts.
        await page.evaluate(async (widget) => {
          const images: HTMLImageElement[] = [];
          const ready = async (root: Document | ShadowRoot | Element) => {
            for (const element of Array.from(root.querySelectorAll('*')) as any[]) {
              if (element.componentOnReady) await element.componentOnReady();
              if (element.shadowRoot) await ready(element.shadowRoot);
              if (element instanceof HTMLImageElement && element.src) {
                await element.decode();
                images.push(element);
              }
            }
          };
          await Promise.race([
            ready(document.querySelector('#widget')!),
            new Promise((_, reject) => setTimeout(() => reject(new Error('Widget readiness timed out')), 30_000)),
          ]);
          await document.fonts.ready;
          // Compare displays full-width images; a fixed landscape frame clips
          // square/portrait evidence. Give the gallery the image's full height.
          if (widget === (window as any).gallery.widgetNames.compare && images.length) {
            const height = Math.max(680, ...images.map((image) => Math.ceil(912 * image.naturalHeight / image.naturalWidth)));
            document.querySelector<HTMLElement>('#widget')!.style.height = `${height}px`;
            (window as any).galleryNode.size[1] = height;
          }
        }, render.widget);
        // LF charts animate their canvas after component readiness (not a CSS animation).
        await page.waitForTimeout(2_000);
        if (errors.length) throw new Error([...new Set(errors)].join('; '));
        await page.locator('main').screenshot({ path: resolve(options.out, render.file), animations: 'disabled' });
        render.outcome = 'PASS';
      } catch (error) {
        render.outcome = 'FAIL'; render.error = String(error).split(/\r?\n/, 1)[0];
        console.error(`${render.nodeType} ${render.widget}: ${render.error}`);
      }
    }
  } finally {
    await browser.close();
    await writeFile(resolve(options.out, 'manifest.json'), JSON.stringify(galleryManifest(renders), null, 2) + '\n', 'utf8');
  }
  console.log(`${renders.filter((render) => render.outcome === 'PASS').length}/${renders.length} renders: ${options.out}`);
  if (renders.some((render) => render.outcome === 'FAIL')) throw new Error('Gallery has failed renders; see manifest.json');
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  if (process.argv.includes('--help')) console.log(usage);
  else await renderGallery(parseGalleryArgs(process.argv.slice(2))).catch((error) => {
    console.error(`Titanic gallery: ${String(error).split(/\r?\n/, 1)[0]}`); process.exitCode = 1;
  });
}
