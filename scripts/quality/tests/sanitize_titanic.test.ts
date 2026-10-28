import { createHash } from 'node:crypto';
import { readdirSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import {
  assertTitanicNodePreservation,
  auditSanitizedTitanic,
  sanitizeTitanicWorkflow,
} from '../sanitize_titanic.mts';
import { validateLfNodeCoverage } from '../titanic_e2e_core';

const fixturePath = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'fixtures', 'E2E.json');
const imageFixturePath = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  'fixtures',
  'titanic-image',
  'titanic-fixture.png',
);
const manifestPath = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  'titanic_cases.json',
);
const nodesRoot = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  '..',
  '..',
  'modules',
  'nodes',
);

const readFixture = () => JSON.parse(readFileSync(fixturePath, 'utf8'));
const readManifest = () => JSON.parse(readFileSync(manifestPath, 'utf8'));

const publicNodeTypes = (): string[] => {
  const files = readdirSync(nodesRoot, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.py'))
    .map((entry) => resolve(entry.parentPath, entry.name));
  const names = new Set<string>();
  for (const path of files) {
    const source = readFileSync(path, 'utf8');
    for (const mapping of source.matchAll(/NODE_CLASS_MAPPINGS\s*=\s*\{([\s\S]*?)\}/g)) {
      for (const key of mapping[1].matchAll(/["'](LF_[A-Za-z0-9_]+)["']\s*:/g)) {
        names.add(key[1]);
      }
    }
  }
  return [...names].sort();
};

const coverageWorkflow = (): any => ({
  nodes: [
    { id: 1, type: 'LF_Source' },
    { id: 2, type: 'LF_Transform' },
    { id: 3, type: 'LF_Output' },
  ],
  links: [[1, 1, 0, 2, 0, 'STRING'], [2, 2, 0, 3, 0, 'STRING']],
});

const checkCoverage = (workflow: any, overrides: any = {}) => validateLfNodeCoverage(
  workflow,
  {
    coverageCases: [{ id: 'test.chain', title: 'Test chain', resourceClass: 'cpu', targets: [3], timeoutSeconds: 1 }],
    coverageExemptions: [],
    disabledNodes: [],
    ...overrides,
  },
  ['LF_Source', 'LF_Transform', 'LF_Output'],
);

describe('Titanic published type reachability', () => {
  it('rejects detached type presence', () => {
    const workflow = coverageWorkflow();
    workflow.links.shift();
    expect(checkCoverage(workflow)).toEqual([
      'LF node type LF_Source is not reachable from coverage targets and has no exemption',
    ]);
  });

  it('walks ordinary and use-everywhere ancestor chains', () => {
    const workflow = coverageWorkflow();
    expect(checkCoverage(workflow)).toEqual([]);
    workflow.links.shift();
    workflow.extra = { ue_links: [{ upstream: '1', downstream: 2 }] };
    expect(checkCoverage(workflow)).toEqual([]);
    workflow.links.push([3, 3, 0, 1, 0, 'STRING']);
    expect(checkCoverage(workflow)).toEqual([]);
  });

  it('stops at disabled nodes and reuses their policy reasons as exemptions', () => {
    const workflow = coverageWorkflow();
    workflow.nodes[1].mode = 2;
    expect(checkCoverage(workflow)).toHaveLength(2);
    expect(checkCoverage(workflow, {
      disabledNodes: [{ id: 2, type: 'LF_Transform', reason: 'external intake disabled by policy' }],
      coverageExemptions: [{ type: 'LF_Source', nodeIds: [1], reason: 'dormant upstream branch' }],
    })).toEqual([]);
    workflow.nodes[2].mode = 2;
    expect(checkCoverage(workflow)).toContain(
      'LF node type LF_Output is not reachable from coverage targets and has no exemption',
    );
  });

  it('requires exemption reasons and exact fixture instances', () => {
    const workflow = coverageWorkflow();
    workflow.links.shift();
    const exemption = { type: 'LF_Source', nodeIds: [1], reason: 'dormant source pending fixture work' };
    expect(checkCoverage(workflow, { coverageExemptions: [exemption] })).toEqual([]);
    expect(checkCoverage(workflow, { coverageExemptions: [{ ...exemption, reason: ' ' }] })).toEqual([
      'Coverage exemption for LF_Source requires a reason',
    ]);
    expect(checkCoverage(workflow, { coverageExemptions: [{ ...exemption, nodeIds: [] }] })).toEqual([
      'Coverage exemption node IDs do not match LF_Source',
    ]);
  });
});

describe('Titanic publication sanitizer', () => {
  it('pins a metadata-free generic raster fixture', () => {
    const png = readFileSync(imageFixturePath);
    expect(createHash('sha256').update(png).digest('hex')).toBe(
      '6e2f2c6536fe6c9161ac9947830b50697182834dd61a050978f89d544d4fbeb0',
    );

    const chunks: string[] = [];
    for (let offset = 8; offset < png.length; ) {
      const length = png.readUInt32BE(offset);
      chunks.push(png.toString('ascii', offset + 4, offset + 8));
      offset += 12 + length;
    }
    expect(chunks).toEqual(['IHDR', 'IDAT', 'IEND']);
  });

  it('keeps the checked-in canonical fixture clean and idempotent', () => {
    const fixture = readFixture();
    const sanitized = sanitizeTitanicWorkflow(fixture).workflow;
    const manifest = readManifest();

    expect(sanitized).toEqual(fixture);
    expect(createHash('sha256').update(readFileSync(fixturePath)).digest('hex')).toBe(manifest.workflow.expectedSha256);
    expect(auditSanitizedTitanic(sanitized)).toEqual([]);
    expect(sanitized.nodes).toHaveLength(manifest.workflow.expectedNodeCount);
    expect(sanitized.links).toHaveLength(manifest.workflow.expectedLinkCount);
    const indexedKey = sanitized.nodes.find((node) => node.id === 596);
    expect(indexedKey.type).toBe('LF_GetKeyFromJSONByIndex');
    expect(indexedKey.widgets_values_named.index).toBe(1);
    expect(sanitized.links).toContainEqual([1208, 595, 0, 596, 0, 'JSON']);
    expect(sanitized.links).toContainEqual([1209, 596, 0, 597, 0, 'STRING']);
  });

  it('reaches or explicitly exempts every currently published LF node type', () => {
    expect(validateLfNodeCoverage(readFixture(), readManifest(), publicNodeTypes())).toEqual([]);
  });

  it('allows added nodes while preserving every canonical node identity', () => {
    const canonical = { nodes: [{ id: 1, type: 'LF_Source' }] };
    expect(() => assertTitanicNodePreservation({
      nodes: [...canonical.nodes, { id: 2, type: 'LF_Output' }],
    }, canonical)).not.toThrow();
  });

  it('names deleted canonical nodes even when replacements preserve or increase the count', () => {
    const canonical = { nodes: [{ id: 1, type: 'LF_Source' }, { id: 2, type: 'LF_Output' }] };
    for (const replacements of [[], [{ id: 3, type: 'LF_Source' }], [
      { id: 3, type: 'LF_Source' }, { id: 4, type: 'LF_Transform' },
    ]]) {
      expect(() => assertTitanicNodePreservation({
        nodes: [canonical.nodes[1], ...replacements],
      }, canonical)).toThrow('node 1: LF_Source');
    }
  });

  it('rejects retyping an existing canonical node ID', () => {
    expect(() => assertTitanicNodePreservation({
      nodes: [{ id: 1, type: 'LF_Transform' }],
    }, { nodes: [{ id: 1, type: 'LF_Source' }] })).toThrow('node 1: LF_Source');
  });

  it('pins synthetic CPU inputs and connected coverage for all six additions', () => {
    const fixture = readFixture();
    const manifest = readManifest();
    const byId = (id: number) => fixture.nodes.find((node: any) => node.id === id);
    expect([612, 614, 618, 620, 623, 625].map((id) => byId(id).type)).toEqual([
      'LF_ApplyTextureToGLB', 'LF_ScaleGLBNodes', 'LF_ExtractImageRegions',
      'LF_ComposeImageRegions', 'LF_LoadImageLayers', 'LF_ComposeImageLayers',
    ]);
    const repoRoot = resolve(nodesRoot, '..', '..');
    for (const asset of manifest.fixtures) {
      const bytes = readFileSync(resolve(repoRoot, asset.path));
      expect(createHash('sha256').update(bytes).digest('hex')).toBe(asset.expectedSha256);
    }
    expect(manifest.fixtures.map((asset: any) => asset.path.split('/').at(-1))).toEqual([
      'lower.png', 'upper.png', 'synthetic.glb',
    ]);
    expect(byId(612).widgets_values_named.source_glb).toBe('titanic-cpu/synthetic.glb');
    expect(byId(614).widgets_values_named.percent).toBe(75);
    expect(byId(615).size).toEqual([500, 600]);
    expect(byId(623).widgets_values_named.include_masks).toBe(true);
    expect(byId(625).inputs.map((input: any) => input.link)).not.toContain(null);
    expect(byId(623).outputs.map((output: any) => output.shape ?? null)).toEqual([null, 6, null, null, 6]);
    expect(byId(625).outputs.map((output: any) => output.shape ?? null)).toEqual([null, 6, 6]);
    expect(JSON.parse(byId(622).widgets_values_named.ui_widget).layers.map((layer: any) => layer.rect)).toEqual([
      [8, 8, 32, 16], [24, 8, 16, 16],
    ]);
    expect(manifest.coverageCases.find((item: any) => item.id === 'cpu.glb-texture-scale')).toMatchObject({
      resourceClass: 'cpu', targets: [613, 615], bindings: { fixtureGlbSourceNodeIds: [612] },
    });
    expect(manifest.coverageCases.find((item: any) => item.id === 'cpu.image-regions-layers')).toMatchObject({
      resourceClass: 'cpu', targets: [616, 621, 622, 626, 627, 628], bindings: { fixtureLayerManifestNodeIds: [622] },
    });
    const newOutputIds = fixture.nodes.filter((node: any) => node.id >= 612 && node.id <= 629 &&
      ['LF_WriteJSON', 'LF_ViewImages', 'Preview3DAdvanced'].includes(node.type)).map((node: any) => node.id).sort();
    const newTargets = manifest.coverageCases.flatMap((item: any) => item.targets)
      .filter((id: number) => id >= 612 && id <= 629).sort();
    expect(newTargets).toEqual(newOutputIds);
    // Every serialized socket points back to the same exact graph edge.
    const nodes = new Map(fixture.nodes.map((node: any) => [node.id, node]));
    for (const link of fixture.links.filter((edge: any) => edge[0] >= 1230)) {
      const [id, source, sourceSlot, destination, destinationSlot, type] = link;
      expect((nodes.get(source) as any).outputs[sourceSlot].links).toContain(id);
      expect((nodes.get(destination) as any).inputs[destinationSlot].link).toBe(id);
      expect((nodes.get(source) as any).outputs[sourceSlot].type).toBe(type);
    }
  });

  it('connects synthetic regional diagnostics and independent core SAM3/DINOv3 cases', () => {
    const fixture = readFixture();
    const manifest = readManifest();
    const byId = (id: number) => fixture.nodes.find((node: any) => node.id === id);
    const coverageCase = (id: string) => manifest.coverageCases.find((item: any) => item.id === id);
    const upstream = (id: number, name: string) => {
      const slot = byId(id).inputs.findIndex((input: any) => input.name === name);
      const link = fixture.links.find((edge: any) => edge[3] === id && edge[4] === slot);
      return link?.slice(1, 3);
    };

    expect([641, 642, 647, 648, 650, 651, 652].map((id) => byId(id).type)).toEqual([
      'LF_TextRegionMasks', 'LF_RegionColorStats', 'LF_TextRegionMasks', 'LF_RegionColorStats',
      'LF_VisionPatchEncode', 'LF_VisionPatchEncode', 'LF_RegionFeatureSimilarity',
    ]);
    expect(JSON.parse(byId(640).widgets_values_named.ui_widget)).toEqual([
      { id: 'surface', prompt: 'outer surface', priority: 0 },
      { id: 'detail', prompt: 'central detail', priority: 10 },
    ]);
    expect(upstream(638, 'image_1')).toEqual([636, 0]);
    expect(upstream(638, 'image_2')).toEqual([637, 0]);
    expect(upstream(639, 'image')).toEqual([638, 0]);
    expect(upstream(641, 'masks')).toEqual([639, 0]);
    expect(byId(635).widgets_values_named).toEqual({ x: 16, y: 12, operation: 'add' });
    expect(upstream(642, 'masks')).toEqual([641, 0]);
    expect(upstream(642, 'metadata')).toEqual([641, 1]);
    for (const id of [641, 642, 647, 648, 650, 651]) {
      expect(byId(id).inputs.find((input: any) => input.name === 'ui_widget').type).toBe('LF_COMPARE');
      expect(byId(id).widgets_values_named.ui_widget).toEqual({});
    }
    expect(byId(652).inputs.find((input: any) => input.name === 'ui_widget').type).toBe('LF_COUNT_BAR_CHART');
    expect(coverageCase('cpu.region-comparison')).toMatchObject({
      resourceClass: 'cpu', targets: [638, 640, 642],
      execution: { requiredNodeIds: [641, 642], forbiddenCachedNodeIds: [641, 642] },
      expect: { '641': { requiredNamedValues: { schema: 'lf.text-region-masks.v1', ordering: 'image-major', area: 2304, raw_area: 3072 } },
        '642': { minimumPreviewCount: 3, requiredNamedValues: { schema: 'lf.region-color-stats.v1', matched_count: 768, intersection_count: 768 } } },
    });

    expect(byId(643).type).toBe('CheckpointLoaderSimple');
    expect(byId(643).widgets_values_named.ckpt_name).toBe('sam3.1_multiplex_fp16.safetensors');
    expect(upstream(644, 'clip')).toEqual([643, 1]);
    expect(byId(645).type).toBe('SAM3_Detect');
    expect(byId(645).widgets_values_named.individual_masks).toBe(false);
    expect(upstream(645, 'model')).toEqual([643, 0]);
    expect(upstream(645, 'conditioning')).toEqual([644, 0]);
    expect(upstream(647, 'masks')).toEqual([645, 0]);
    expect(JSON.parse(byId(646).widgets_values_named.ui_widget)[0].prompt)
      .toBe(byId(644).widgets_values_named.text);
    expect(coverageCase('model.sam3-region-masks')).toMatchObject({
      resourceClass: 'gpu', targets: [646, 648],
      execution: { requiredNodeIds: [643, 644, 645, 647, 648], forbiddenCachedNodeIds: [643, 644, 645, 647, 648] },
    });

    expect(byId(649).type).toBe('CLIPVisionLoader');
    expect(byId(649).widgets_values_named.clip_name).toBe('dino_v3_vit_h.safetensors');
    for (const id of [650, 651]) {
      expect(upstream(id, 'clip_vision')).toEqual([649, 0]);
      expect(byId(id).widgets_values_named.crop).toBe('none');
    }
    expect(upstream(652, 'features_a')).toEqual([650, 0]);
    expect(upstream(652, 'features_b')).toEqual([651, 0]);
    expect(upstream(652, 'masks')).toEqual([641, 0]);
    expect(upstream(652, 'metadata')).toEqual([641, 1]);
    expect(upstream(653, 'json_input')).toEqual([652, 0]);
    expect(byId(652).widgets_values_named).toMatchObject({ model_file: 'dino_v3_vit_h.safetensors', crop: 'none' });
    const dino = coverageCase('model.dinov3-region-features');
    expect(dino).toMatchObject({ resourceClass: 'gpu', targets: [653],
      execution: { requiredNodeIds: [641, 649, 650, 651, 652], forbiddenCachedNodeIds: [641, 649, 650, 651, 652] } });
    for (const id of [650, 651, 652]) {
      expect(dino.expect[String(id)].requiredNamedValues).toMatchObject({ crop: 'none', prefix_tokens: 5 });
    }
    for (const type of ['LF_TextRegionMasks', 'LF_RegionColorStats', 'LF_RegionFeatureSimilarity', 'LF_VisionPatchEncode']) {
      expect(manifest.coverageExemptions.some((item: any) => item.type === type)).toBe(false);
    }
    const outputTypes = ['LF_ImageList', 'LF_WriteJSON', 'LF_RegionColorStats', 'LF_DisplayJSON'];
    const outputIds = fixture.nodes.filter((node: any) => node.id >= 630 && outputTypes.includes(node.type))
      .map((node: any) => node.id).sort();
    const targets = manifest.coverageCases.flatMap((item: any) => item.targets)
      .filter((id: number) => id >= 630).sort();
    expect(targets).toEqual(outputIds);
  });

  it('pins the new media, audio, and exact-instance local-LLM coverage slice', () => {
    const fixture = readFixture();
    const manifest = readManifest();
    const byId = (id: number) => fixture.nodes.find((node: any) => node.id === id);
    expect(
      Array.from({ length: 14 }, (_, index) => byId(598 + index).type),
    ).toEqual([
      'LF_SeamlessTile',
      'LF_IsoDiamondTiles',
      'LF_SelectLoopSegment',
      'EmptyAudio',
      'LF_SaveAudio',
      'LF_LMSLoadModel',
      'LF_LocalChatCompletions',
      'LF_H3PromptMaker',
      'LF_WallOfText',
      'LF_LMSUnloadModel',
      'LF_H3PromptMaker',
      'LF_DisplayString',
      'LF_ViewImages',
      'LF_ViewImages',
    ]);
    expect(byId(605).widgets_values_named).toMatchObject({
      intent: 'A yellow diagonal line glides slowly across a dark blue background.',
      mode: 'auto',
      review: true,
    });
    expect(byId(608).widgets_values_named).toMatchObject({
      intent: 'A yellow diagonal line glides slowly across a dark blue background.',
      review: false,
    });
    expect(byId(599).widgets_values).toEqual([
      64, 32, 4, 42, 'fixed', 0.5, {},
    ]);
    expect(byId(599).widgets_values_named).toMatchObject({
      seed: 42,
      control_after_generate: 'fixed',
      texture_scale: 0.5,
      ui_widget: {},
    });
    expect(byId(606).widgets_values).toEqual([
      '\n\n---\n\n', '', '', false, 42, 'fixed', '',
    ]);
    expect(byId(606).widgets_values_named).toMatchObject({
      seed: 42,
      control_after_generate: 'fixed',
      ui_widget: '',
    });
    expect(byId(555).widgets_values_named).toMatchObject({ width: 512, height: 320 });
    expect(byId(553).widgets_values_named).toMatchObject({ width: 448, height: 150 });
    expect(fixture.links).toContainEqual([1221, 556, 0, 605, 4, 'IMAGE']);
    expect(fixture.links).toContainEqual([1222, 553, 0, 605, 10, 'IMAGE']);
    expect(byId(589).widgets_values_named.batch_size).toBe(6);
    expect(byId(589).outputs[0].links).toContain(1213);
    expect(byId(563).outputs[0].links).not.toContain(1213);
    expect(fixture.links).toContainEqual([1213, 589, 0, 600, 0, 'IMAGE']);
    expect(fixture.links).toContainEqual([1219, 603, 0, 607, 1, 'STRING']);
    expect(fixture.links).toContainEqual([1228, 606, 0, 607, 0, 'STRING']);

    const lifecycle = manifest.coverageCases.find(
      (candidate: any) => candidate.id === 'llm.local-lifecycle',
    );
    expect(lifecycle).toMatchObject({
      resourceClass: 'local-llm-lifecycle-gpu-write',
      targets: [609],
      bindings: {
        localModelIdNodeIds: [603],
        localNativeChatNodeIds: [603, 604, 605, 607, 608],
      },
    });
    expect(
      manifest.coverageCases.find((candidate: any) => candidate.id === 'fs.audio-write'),
    ).toMatchObject({
      resourceClass: 'durable-write',
      targets: [602],
      expect: { '602': { receiptSchema: 'lf.audio_file.receipt.v1' } },
    });
  });

  it('tracks the current periodic and normalized batch output schemas', () => {
    const fixture = readFixture();
    const byId = (id: number) => fixture.nodes.find((node: any) => node.id === id);
    const outputContract = (id: number) => byId(id).outputs.map((output: any) => ({
      name: output.name,
      type: output.type,
      shape: output.shape ?? null,
    }));

    expect(byId(590).widgets_values_named.sampling_basis).toBe('timeline');
    expect(byId(590).inputs.at(-1)).toMatchObject({
      name: 'sampling_basis',
      type: 'COMBO',
      widget: { name: 'sampling_basis' },
    });
    expect(outputContract(590)).toEqual([
      { name: 'image', type: 'IMAGE', shape: null },
      { name: 'receipt', type: 'JSON', shape: null },
      { name: 'image_list', type: 'IMAGE', shape: 6 },
    ]);
    expect(outputContract(592)).toEqual([
      { name: 'image', type: 'IMAGE', shape: null },
      { name: 'receipt', type: 'JSON', shape: null },
      { name: 'image_list', type: 'IMAGE', shape: 6 },
    ]);
  });

  it('removes private selectors, stale sessions, preview caches, and old history', () => {
    const fixture = readFixture();
    const byId = (id: number) => fixture.nodes.find((node: any) => node.id === id);

    byId(49).widgets_values_named.filter = '*\\morana.*';
    byId(50).widgets_values_named.lora = 'PONY\\character\\5h4rt.safetensors';
    byId(93).widgets_values_named.dir = 'D:\\private';
    byId(93).widgets_values_named.cache_images = {
      dataset: { nodes: [{ value: '/view?filename=private.png&type=input' }] },
    };
    byId(135).widgets_values_named.randomize = {
      nodes: [{ icon: 'history', description: 'Execution date: yesterday' }],
    };
    byId(463).widgets_values_named.ui_widget = {
      context_id: 'C:\\Users\\Luca\\temp\\463_deadbeef_edit_dataset.json',
    };
    byId(142).widgets_values_named.ui_widget = {
      config: {},
      history: [
        { role: 'user', content: 'private old prompt' },
        { role: 'assistant', content: 'private old response' },
      ],
    };
    byId(357).widgets_values_named.ui_widget = JSON.stringify({
      nodes: [
        {
          icon: 'history',
          id: 'Execution time: yesterday',
          value: 'Execution time: yesterday',
        },
      ],
    });
    for (const node of [byId(49), byId(50), byId(93), byId(135), byId(142), byId(357), byId(463)]) {
      const names = Object.keys(node.widgets_values_named);
      node.widgets_values = names.map((name) => node.widgets_values_named[name]);
    }

    const sanitized = sanitizeTitanicWorkflow(fixture).workflow;
    const cleanById = (id: number) => sanitized.nodes.find((node: any) => node.id === id);

    expect(cleanById(49).widgets_values_named.filter).toBe('');
    expect(cleanById(49).widgets_values_named.weight).toBe(1);
    expect(cleanById(49).widgets_values_named.randomize).toBe(false);
    expect(cleanById(50).widgets_values_named.lora).toBe(
      'PONY\\style\\d0f_v2.safetensors',
    );
    for (const id of [93, 100, 103]) {
      expect(cleanById(id).widgets_values_named).toMatchObject({
        dir: 'custom_nodes/lf-nodes/scripts/quality/fixtures/titanic-image',
        load_cap: 1,
        cache_images: true,
        copy_into_input_dir: false,
      });
    }
    expect(cleanById(481).widgets_values_named).toMatchObject({
      dir: 'custom_nodes/lf-nodes/scripts/quality/fixtures/titanic-image',
      filter: 'titanic-fixture.png',
    });
    expect(cleanById(135).widgets_values_named.randomize).toBe(false);
    expect(cleanById(463).widgets_values_named.ui_widget).toEqual({});
    expect(cleanById(142).widgets_values_named.ui_widget).toEqual({
      config: {},
      history: [
        { role: 'user', content: 'Return one short, generic test response.' },
      ],
    });
    expect(cleanById(145).widgets_values_named.ui_widget.config).toEqual({
      currentCharacter: 'character_guide',
    });
    const messengerCharacter =
      cleanById(145).widgets_values_named.ui_widget.dataset.nodes[0];
    expect(messengerCharacter.children.map((child: any) => child.id)).toEqual([
      'chat',
      'avatars',
      'styles',
      'locations',
      'outfits',
      'timeframes',
    ]);
    expect(cleanById(357).widgets_values_named.ui_widget).not.toContain('Execution time:');
    expect(cleanById(117).widgets_values_named.mutate_source).toBe(false);
    for (const id of [51, 52, 250, 251]) {
      expect(cleanById(id).widgets_values_named.randomize).toBe(false);
    }
    for (const id of [48, 55, 56]) {
      expect(cleanById(id).widgets_values_named.filter).toBe('');
    }
    expect(cleanById(453).widgets_values_named.use_regex_placeholders).toBe(false);
    expect(cleanById(575).widgets_values_named).toMatchObject({
      control_after_generate: 'fixed',
      inference_steps: 8,
      guidance_scale: 7,
      infer_method: 'ode',
      shift: 3,
      output_format: 'flac',
    });
    expect(auditSanitizedTitanic(sanitized)).toEqual([]);
  });

  it('fails the publication audit on credentials, private data, or adult markers', () => {
    expect(
      auditSanitizedTitanic({
        api_key: 'not-empty',
        client_secret: 'also-not-empty',
        path: 'C:\\Users\\Someone\\private.png',
        networkPath: '\\\\server\\share\\fixture.png',
        homePath: '/home/someone/private.png',
        contact: 'maintainer@example.com',
        project: 'Velora',
        prompt: 'explicit ＮＳＦＷ fixture',
      }),
    ).toEqual([
      '$.api_key: non-empty credential field',
      '$.client_secret: non-empty credential field',
      '$.contact: email address',
      '$.homePath: POSIX home path',
      '$.networkPath: UNC path',
      '$.path: absolute Windows path',
      '$.project: private project or personal vocabulary',
      '$.prompt: explicit adult-content vocabulary',
    ]);
  });

  it('rejects private character aliases even when obfuscated', () => {
    expect(
      auditSanitizedTitanic({ filter: '*\\m0r4n4.*' }),
    ).toEqual(['$.filter: private character vocabulary']);
  });

  it('detects execution and chat history nested inside semantic JSON strings', () => {
    const findings = auditSanitizedTitanic({
      textarea: JSON.stringify({
        nodes: [
          {
            icon: 'history',
            value: 'Execution time: 2024-01-01 00:00:00',
          },
        ],
      }),
      chat: {
        history: [
          { role: 'user', content: 'old prompt' },
          { role: 'assistant', content: 'old result' },
        ],
      },
    });
    expect(findings).toContain('$.textarea: execution-history timestamp');
    expect(findings).toContain('$.textarea#json.nodes[0].icon: execution-history node');
    expect(findings).toContain('$.chat.history: non-canonical chat history');
  });
});
