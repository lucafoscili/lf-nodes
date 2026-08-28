import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import {
  auditSanitizedTitanic,
  sanitizeTitanicWorkflow,
} from '../sanitize_titanic.mts';

const fixturePath = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'fixtures', 'E2E.json');

const readFixture = () => JSON.parse(readFileSync(fixturePath, 'utf8'));

describe('Titanic publication sanitizer', () => {
  it('keeps the checked-in canonical fixture clean and idempotent', () => {
    const fixture = readFixture();
    const sanitized = sanitizeTitanicWorkflow(fixture).workflow;

    expect(sanitized).toEqual(fixture);
    expect(auditSanitizedTitanic(sanitized)).toEqual([]);
    expect(sanitized.nodes).toHaveLength(354);
    expect(sanitized.links).toHaveLength(467);
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
    expect(cleanById(93).widgets_values_named.dir).toBe('');
    expect(cleanById(93).widgets_values_named.cache_images).toBe(true);
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
