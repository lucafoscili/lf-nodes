// @vitest-environment node

import { resolve } from 'node:path';

import { describe, expect, it } from 'vitest';

import type { TitanicPayloads } from '../titanic_e2e_core.ts';
import { parseArgs as parseTitanicArgs } from '../titanic_e2e.mts';
import { galleryManifest, parseGalleryArgs, planGallery } from '../titanic_gallery.mts';

// Deliberately synthetic: the built bundle owns the real NODE_WIDGET_MAP defaults.
const widgetNames = { code: 'LfCode', tree: 'LfTree', countBarChart: 'LfCountBarChart' };
const defaults = { LF_Example: [widgetNames.tree] };
const evidence = (ui: Record<string, unknown> = { lf_output: [{ value: 'final UI' }] }): TitanicPayloads[] => [{
  schema: 'lf.titanic-payloads.v1', caseId: 'cpu.example',
  nodes: [{ nodeId: '10', nodeType: 'LF_Example', ui }],
}];

describe('Titanic gallery offline contracts', () => {
  it('keeps payload persistence opt-in for the execution harness', () => {
    expect(parseTitanicArgs([]).savePayloads).toBe(false);
    expect(parseTitanicArgs(['--full', '--case', 'cpu.example', '--save-payloads']))
      .toMatchObject({ mode: 'full', caseIds: ['cpu.example'], savePayloads: true });
  });
  it('parses repeatable input runs, views and node selection without conflating them', () => {
    const options = parseGalleryArgs([
      '--', '--run', 'run-one', '--run', 'run-two', '--out', 'gallery',
      '--bundle-dir', 'bundle', '--comfy-url', 'http://127.0.0.1:9191',
      '--browser-channel', 'msedge', '--node', 'LF_Example', '--node', 'LF_Other',
      '--alternative', 'LF_Example=countBarChart', '--alternative', 'LF_Example=LfCode',
      '--alternative', 'LF_Other=tree',
    ]);
    expect(options).toEqual({
      runs: [resolve('run-one'), resolve('run-two')], out: resolve('gallery'),
      bundleDir: resolve('bundle'), comfyUrl: 'http://127.0.0.1:9191', browserChannel: 'msedge',
      alternatives: { LF_Example: ['countBarChart', 'LfCode'], LF_Other: ['tree'] },
      nodes: ['LF_Example', 'LF_Other'],
    });
  });

  it('supplies local preview defaults while requiring explicit evidence and output locations', () => {
    expect(parseGalleryArgs(['--run', 'run', '--out', 'gallery'])).toMatchObject({
      runs: [resolve('run')], out: resolve('gallery'), comfyUrl: 'http://127.0.0.1:8188',
      browserChannel: undefined, alternatives: {}, nodes: [],
    });
    expect(parseGalleryArgs(['--run', 'run', '--out', 'gallery']).bundleDir).toMatch(/[\\/]web[\\/]deploy$/);
    expect(() => parseGalleryArgs(['--out', 'gallery'])).toThrow('--run and --out are required');
    expect(() => parseGalleryArgs(['--run', 'run'])).toThrow('--run and --out are required');
  });

  it.each<[string[], string]>([
    [['--run'], '--run: missing value'],
    [['--run', '--out', 'gallery'], '--run: missing value'],
    [['--unknown', 'value'], 'Unknown option: --unknown'],
    [['--alternative', '=tree'], '--alternative expects NODE=WIDGET'],
    [['--alternative', 'LF_Example='], '--alternative expects NODE=WIDGET'],
    [['--alternative', 'LF_Example=tree=code'], '--alternative expects NODE=WIDGET'],
  ])('rejects invalid CLI arguments %j', (args, message) => {
    expect(() => parseGalleryArgs(args)).toThrow(message);
  });

  it('uses whichever NODE_WIDGET_MAP defaults the supplied bundle registry declares', () => {
    for (const widgets of [[widgetNames.tree], [widgetNames.code, widgetNames.countBarChart]]) {
      const renders = planGallery(evidence(), { LF_Example: widgets }, widgetNames);
      expect(renders.map(({ widget, role }) => ({ widget, role })))
        .toEqual(widgets.map((widget) => ({ widget, role: 'default' })));
    }
  });

  it('normalizes alternative enum keys and values, deduplicating repeated and default views', () => {
    const input = evidence();
    const alternatives = { LF_Example: ['tree', 'LfTree', 'countBarChart', 'LfCountBarChart', 'code', 'LfCode'] };
    const before = structuredClone({ input, defaults, widgetNames, alternatives });
    expect(planGallery(input, defaults, widgetNames, alternatives).map(({ widget, role }) => ({ widget, role })))
      .toEqual([
        { widget: 'LfTree', role: 'default' },
        { widget: 'LfCountBarChart', role: 'alternative' },
        { widget: 'LfCode', role: 'alternative' },
      ]);
    expect({ input, defaults, widgetNames, alternatives }).toEqual(before);
  });

  it('preserves case, node, payload and view identity with a unique screenshot for every render', () => {
    const input: TitanicPayloads[] = [
      { schema: 'lf.titanic-payloads.v1', caseId: 'cpu.first', nodes: [
        { nodeId: '10', nodeType: 'LF_Example', ui: { lf_output: [{ value: 'one' }, { value: 'two' }] } },
        { nodeId: '11', nodeType: 'LF_Example', ui: { lf_output: [{ value: 'three' }] } },
      ] },
      { schema: 'lf.titanic-payloads.v1', caseId: 'cpu.second', nodes: [
        { nodeId: '10', nodeType: 'LF_Example', ui: { lf_output: [{ value: 'four' }] } },
      ] },
    ];
    const renders = planGallery(input, defaults, widgetNames, { LF_Example: ['code'] });
    expect(renders.map(({ caseId, nodeId, payloadIndex, widget }) => [caseId, nodeId, payloadIndex, widget]))
      .toEqual([
        ['cpu.first', '10', 0, 'LfTree'], ['cpu.first', '10', 0, 'LfCode'],
        ['cpu.first', '10', 1, 'LfTree'], ['cpu.first', '10', 1, 'LfCode'],
        ['cpu.first', '11', 0, 'LfTree'], ['cpu.first', '11', 0, 'LfCode'],
        ['cpu.second', '10', 0, 'LfTree'], ['cpu.second', '10', 0, 'LfCode'],
      ]);
    expect(new Set(renders.map(({ file }) => file)).size).toBe(renders.length);
    expect(renders.every(({ file }) => /^[a-zA-Z0-9_.-]+\.png$/.test(file))).toBe(true);
    expect(galleryManifest(renders)).toEqual({ schema: 'lf.titanic-gallery.v1', renders });
  });

  it('supports native UI payloads and filters unselected node types before requiring their registry entry', () => {
    const input = evidence({ text: ['native final UI'] });
    input[0].nodes.push({ nodeId: '20', nodeType: 'NativeOnly', ui: { result: ['other UI'] } });
    expect(planGallery(input, defaults, widgetNames, {}, ['LF_Example'])).toEqual([
      expect.objectContaining({ nodeId: '10', nodeType: 'LF_Example', payloadIndex: 0, widget: 'LfTree' }),
    ]);
  });

  it('distinguishes the same case and node captured in multiple input runs', () => {
    const input = [
      ...evidence({ lf_output: [{ value: 'first run' }] }),
      ...evidence({ lf_output: [{ value: 'second run, first payload' }, { value: 'second run, second payload' }] }),
    ];
    const renders = planGallery(input, defaults, widgetNames);
    expect(galleryManifest(renders).renders.map(({ evidenceIndex, caseId, nodeId, payloadIndex }) => ({
      evidenceIndex, caseId, nodeId, payloadIndex,
    }))).toEqual([
      { evidenceIndex: 0, caseId: 'cpu.example', nodeId: '10', payloadIndex: 0 },
      { evidenceIndex: 1, caseId: 'cpu.example', nodeId: '10', payloadIndex: 0 },
      { evidenceIndex: 1, caseId: 'cpu.example', nodeId: '10', payloadIndex: 1 },
    ]);
    expect(new Set(renders.map(({ file }) => file)).size).toBe(3);
  });

  it('keeps the manifest to render identity and outcomes, without copying saved UI or prompt/workflow data', () => {
    const input = evidence({ lf_output: [{ value: 'UI_ONLY_SENTINEL', prompt: 'nested prompt' }] });
    Object.assign(input[0], { prompt: { secret: 'PROMPT_ONLY_SENTINEL' }, workflow: { nodes: ['WORKFLOW_ONLY_SENTINEL'] } });
    const renders = planGallery(input, defaults, widgetNames);
    Object.assign(renders[0], { outcome: 'PASS' });
    const manifest = galleryManifest(renders);
    expect(manifest.renders[0]).toEqual({
      evidenceIndex: 0, caseId: 'cpu.example', nodeId: '10', nodeType: 'LF_Example', payloadIndex: 0,
      widget: 'LfTree', role: 'default', file: renders[0].file, outcome: 'PASS',
    });
    expect(JSON.stringify(manifest)).not.toMatch(/SENTINEL|"(?:prompt|workflow|ui)":/);
    expect(manifest.renders[0]).not.toBe(renders[0]);
  });

  it('retains failed render outcomes and errors for review', () => {
    const renders = planGallery(evidence(), defaults, widgetNames);
    Object.assign(renders[0], { outcome: 'FAIL', error: 'Preview asset could not decode' });
    expect(galleryManifest(renders).renders[0]).toMatchObject({
      outcome: 'FAIL', error: 'Preview asset could not decode',
    });
  });

  it('rejects missing payload selections, empty payload lists and incompatible evidence', () => {
    expect(() => planGallery([], defaults, widgetNames)).toThrow('No saved payloads to render');
    expect(() => planGallery(evidence(), defaults, widgetNames, {}, ['LF_Missing']))
      .toThrow('LF_Missing: no saved payload');
    expect(() => planGallery(evidence(), defaults, widgetNames, { LF_Missing: ['code'] }))
      .toThrow('LF_Missing: no saved payload');
    for (const lf_output of [[], 'not a payload list']) {
      expect(() => planGallery(evidence({ lf_output }), defaults, widgetNames)).toThrow('LF_Example: no UI payloads');
    }
    const unsupported = evidence();
    Object.assign(unsupported[0], { schema: 'unsupported' });
    expect(() => planGallery(unsupported, defaults, widgetNames)).toThrow('Unsupported payload evidence schema');
  });

  it('rejects absent NODE_WIDGET_MAP defaults and unknown default or alternative widgets', () => {
    for (const registry of [{}, { LF_Example: [] }]) {
      expect(() => planGallery(evidence(), registry, widgetNames)).toThrow('LF_Example: NODE_WIDGET_MAP has no widget');
    }
    expect(() => planGallery(evidence(), { LF_Example: ['missing'] }, widgetNames))
      .toThrow('Unknown widget: missing');
    expect(() => planGallery(evidence(), defaults, widgetNames, { LF_Example: ['missing'] }))
      .toThrow('Unknown widget: missing');
  });

  it('renders an explicitly requested widget even when the node has no registered default', () => {
    expect(planGallery(evidence(), { LF_Example: [] }, widgetNames, { LF_Example: ['tree'] }))
      .toEqual([expect.objectContaining({ widget: 'LfTree', role: 'alternative' })]);
  });
});
