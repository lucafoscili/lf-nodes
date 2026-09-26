import { createHash } from 'node:crypto';
import { readdirSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import {
  auditSanitizedTitanic,
  sanitizeTitanicWorkflow,
} from '../sanitize_titanic.mts';

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

    expect(sanitized).toEqual(fixture);
    expect(auditSanitizedTitanic(sanitized)).toEqual([]);
    expect(sanitized.nodes).toHaveLength(372);
    expect(sanitized.links).toHaveLength(490);
    const indexedKey = sanitized.nodes.find((node) => node.id === 596);
    expect(indexedKey.type).toBe('LF_GetKeyFromJSONByIndex');
    expect(indexedKey.widgets_values_named.index).toBe(1);
    expect(sanitized.links).toContainEqual([1208, 595, 0, 596, 0, 'JSON']);
    expect(sanitized.links).toContainEqual([1209, 596, 0, 597, 0, 'STRING']);
  });

  it('contains every currently published LF node type', () => {
    const fixtureTypes = [...new Set(
      readFixture().nodes
        .map((node: any) => node.type)
        .filter((type: unknown) => typeof type === 'string' && type.startsWith('LF_')),
    )].sort();
    expect(fixtureTypes).toEqual(publicNodeTypes());
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
