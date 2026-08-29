import { readFileSync, readdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import {
  GENERIC_CHAT_HISTORY,
  auditSanitizedExample,
  exampleTopologyProjection,
  sanitizeExampleWorkflow,
} from '../sanitize_example_workflows.mts';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const exampleDir = resolve(repoRoot, 'example_workflows');
const exampleFiles = readdirSync(exampleDir)
  .filter((file) => file.toLowerCase().endsWith('.json'))
  .sort((left, right) => left.localeCompare(right));

const readExample = (file: string) =>
  JSON.parse(readFileSync(resolve(exampleDir, file), 'utf8'));

describe('shipped example workflow sanitizer', () => {
  it('keeps all 17 tracked JSON examples parseable, clean, and idempotent', () => {
    expect(exampleFiles).toHaveLength(17);

    for (const file of exampleFiles) {
      const workflow = readExample(file);
      const first = sanitizeExampleWorkflow(workflow).workflow;
      const second = sanitizeExampleWorkflow(first).workflow;

      expect(first, file).toEqual(workflow);
      expect(second, file).toEqual(first);
      expect(auditSanitizedExample(first), file).toEqual([]);
    }
  });

  it('removes private and transient state without changing topology or sockets', () => {
    const workflow = {
      last_node_id: 4,
      last_link_id: 2,
      nodes: [
        {
          id: 1,
          type: 'LF_LoadAndEditImages',
          mode: 0,
          order: 0,
          inputs: [{ name: 'config', type: 'JSON', link: null }],
          outputs: [{ name: 'image', type: 'IMAGE', links: [1] }],
          widgets_values: [
            {
              nodes: [{ value: '/view?filename=private.png&nonce=abc' }],
              context_id:
                'C:\\Users\\Luca\\Documents\\GitHub\\ComfyUI\\temp\\1_edit_dataset.json',
              selection: { index: 0 },
              defaults: { inpaint: { steps: 8 } },
            },
          ],
        },
        {
          id: 2,
          type: 'LF_LLMChat',
          mode: 0,
          order: 1,
          inputs: [{ name: 'ui_widget', type: 'LF_CHAT', link: null }],
          outputs: [{ name: 'chat_history_json', type: 'JSON', links: [2] }],
          widgets_values: [
            {
              history: [
                { role: 'user', content: 'A private previous request.' },
                { role: 'assistant', content: 'A private previous answer.' },
              ],
            },
          ],
        },
        {
          id: 3,
          type: 'LF_CheckpointSelector',
          mode: 0,
          order: 2,
          inputs: [{ name: 'filter', type: 'STRING', link: null }],
          outputs: [{ name: 'checkpoint', type: 'STRING', links: [] }],
          widgets_values: [
            'model.safetensors',
            {
              props: [
                {
                  lfDataset: {
                    nodes: [
                      {
                        value:
                          'data:image/png;charset=utf-8;base64,private-preview',
                      },
                    ],
                  },
                },
              ],
            },
          ],
        },
        {
          id: 4,
          type: 'LF_UrandomSeedGenerator',
          mode: 0,
          order: 3,
          inputs: [],
          outputs: [],
          widgets_values: [
            true,
            {
              nodes: [
                {
                  icon: 'history',
                  id: 'Execution time: 2025-01-01 00:00:00',
                  value: 'Execution time: 2025-01-01 00:00:00',
                  children: [
                    { id: 'seed1', value: '42' },
                    { id: 'seed2', value: '84' },
                  ],
                },
              ],
            },
          ],
        },
      ],
      links: [
        [1, 1, 0, 2, 0, 'IMAGE'],
        [2, 2, 0, 3, 0, 'JSON'],
      ],
      groups: [{ id: 1, title: 'Example', bounding: [0, 0, 100, 100] }],
      config: {},
      extra: {},
      version: 0.4,
    };

    const beforeTopology = exampleTopologyProjection(workflow);
    const sanitized = sanitizeExampleWorkflow(workflow).workflow;

    expect(exampleTopologyProjection(sanitized)).toEqual(beforeTopology);
    expect(sanitized.nodes[0].widgets_values[0]).toEqual({
      defaults: { inpaint: { steps: 8 } },
    });
    expect(sanitized.nodes[1].widgets_values[0]).toEqual({
      history: GENERIC_CHAT_HISTORY,
    });
    expect(sanitized.nodes[2].widgets_values[1]).toEqual({});
    expect(sanitized.nodes[3].widgets_values[1]).toEqual({
      nodes: [
        {
          id: 'fixture-seeds',
          value: 'Fixture seeds',
          children: [
            { id: 'seed1', value: '42' },
            { id: 'seed2', value: '84' },
          ],
        },
      ],
    });
    expect(auditSanitizedExample(sanitized)).toEqual([]);
  });

  it('projects absolute Comfy paths to portable relative inputs', () => {
    const workflow = {
      last_node_id: 1,
      last_link_id: 0,
      nodes: [
        {
          id: 1,
          type: 'LF_LoadFileOnce',
          mode: 0,
          order: 0,
          inputs: [],
          outputs: [],
          widgets_values: [
            'C:\\Users\\Luca\\Documents\\GitHub\\ComfyUI\\output\\example.txt',
          ],
        },
      ],
      links: [],
      groups: [],
      config: {},
      extra: {},
      version: 0.4,
    };

    const sanitized = sanitizeExampleWorkflow(workflow).workflow;
    expect(sanitized.nodes[0].widgets_values[0]).toBe('output/example.txt');
    expect(auditSanitizedExample(sanitized)).toEqual([]);
  });
});
