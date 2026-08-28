import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

type JsonRecord = Record<string, any>;

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..', '..');
const defaultInput = resolve(
  repoRoot,
  '..',
  '..',
  'user',
  'default',
  'workflows',
  'E2E.json',
);
const defaultOutput = resolve(scriptDir, 'fixtures', 'E2E.json');

const SEMANTIC_UI_WIDGET_CLASSES = new Set([
  'LF_KeywordToggleFromJSON',
  'LF_WriteJSON',
  'LF_LLMChat',
  'LF_LLMMessenger',
]);

const HISTORY_PRIMITIVES = new Set([
  'LF_Boolean',
  'LF_Float',
  'LF_Integer',
  'LF_String',
]);

const GENERIC_JSON_DATASET = {
  nodes: [
    { id: 'alpha', value: 'Alpha' },
    { id: 'beta', value: 'Beta' },
  ],
};

const GENERIC_CHAT_HISTORY = [
  {
    role: 'user',
    content: 'Return one short, generic test response.',
  },
];

const GENERIC_MESSENGER_CHAT = [
  { role: 'user', content: 'Hello.' },
  {
    role: 'assistant',
    content: 'Welcome to this generic test scene.',
  },
];

const GENERIC_MESSENGER_DATASET = {
  dataset: {
    nodes: [
      {
        id: 'character_guide',
        value: 'Guide',
        children: [
          {
            id: 'chat',
            value: '',
            cells: {
              lfChat: {
                shape: 'chat',
                value: GENERIC_MESSENGER_CHAT,
              },
            },
          },
          {
            id: 'styles',
            value: 0,
            children: [
              {
                id: 'style_0',
                value: 'Illustration',
                description: 'Clean generic illustration.',
              },
            ],
          },
          {
            id: 'locations',
            value: 0,
            children: [
              {
                id: 'location_0',
                value: 'Studio',
                description: 'Neutral studio backdrop.',
              },
            ],
          },
          {
            id: 'outfits',
            value: 0,
            children: [
              {
                id: 'outfit_0',
                value: 'Everyday clothes',
                description: 'Simple generic clothing.',
              },
            ],
          },
          {
            id: 'timeframes',
            value: 0,
            children: [
              {
                id: 'timeframe_0',
                value: 'Present day',
                description: 'Contemporary setting.',
              },
            ],
          },
        ],
      },
    ],
  },
  config: { currentCharacter: 'character_guide' },
};

const GENERIC_SEED_DATASET = {
  nodes: [
    {
      id: 'fixture-seeds',
      value: 'Fixture seeds',
      children: Array.from({ length: 20 }, (_, index) => ({
        id: `seed${index + 1}`,
        value: String(index),
      })),
    },
  ],
};

const sha256 = (value: string | Buffer): string =>
  createHash('sha256').update(value).digest('hex');

const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

const topologyProjection = (workflow: JsonRecord): JsonRecord => ({
  ...workflow,
  nodes: (workflow.nodes ?? []).map((node: JsonRecord) => {
    const { widgets_values: _values, widgets_values_named: _named, ...structural } = node;
    return structural;
  }),
});

const emptyWidgetValue = (value: unknown): unknown => {
  if (typeof value === 'string') return '';
  if (Array.isArray(value)) return [];
  if (value && typeof value === 'object') return {};
  return value ?? {};
};

const clearHistoryDatasets = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(clearHistoryDatasets);
  if (!value || typeof value !== 'object') return value;

  const record = value as JsonRecord;
  const nodes = record.nodes;
  if (
    Array.isArray(nodes) &&
    nodes.some(
      (node) =>
        node?.icon === 'history' ||
        (typeof node?.description === 'string' && node.description.startsWith('Execution date:')),
    )
  ) {
    return { ...record, nodes: [] };
  }

  return Object.fromEntries(
    Object.entries(record).map(([key, child]) => [key, clearHistoryDatasets(child)]),
  );
};

const isMessageArray = (value: unknown): value is JsonRecord[] =>
  Array.isArray(value) &&
  value.length > 0 &&
  value.every(
    (entry) =>
      entry &&
      typeof entry === 'object' &&
      typeof entry.role === 'string' &&
      typeof entry.content === 'string',
  );

const isCanonicalMessageFixture = (value: JsonRecord[]): boolean => {
  const serialized = JSON.stringify(value);
  return (
    serialized === JSON.stringify(GENERIC_CHAT_HISTORY) ||
    serialized === JSON.stringify(GENERIC_MESSENGER_CHAT)
  );
};

const widgetNames = (node: JsonRecord): string[] =>
  Object.keys(node.widgets_values_named ?? {});

const setWidget = (
  node: JsonRecord,
  name: string,
  value: unknown,
  changes: string[],
): void => {
  const names = widgetNames(node);
  const index = names.indexOf(name);
  if (index < 0 || !Array.isArray(node.widgets_values)) {
    throw new Error(`node ${node.id} ${node.type} has no serialized widget ${JSON.stringify(name)}`);
  }
  if (names.length !== node.widgets_values.length) {
    throw new Error(
      `node ${node.id} ${node.type} widget-name/value cardinality drifted ` +
        `(${names.length} names, ${node.widgets_values.length} values)`,
    );
  }
  node.widgets_values[index] = clone(value);
  node.widgets_values_named[name] = clone(value);
  changes.push(`${node.id}:${node.type}.${name}`);
};

const requireNode = (workflow: JsonRecord, id: number, type: string): JsonRecord => {
  const node = (workflow.nodes ?? []).find((candidate: JsonRecord) => Number(candidate.id) === id);
  if (!node || node.type !== type) {
    throw new Error(`expected node ${id} to be ${type}`);
  }
  return node;
};

export const auditSanitizedTitanic = (workflow: JsonRecord): string[] => {
  const findings: string[] = [];
  const blockedStrings: Array<[string, RegExp]> = [
    ['absolute Windows path', /(?:^|[^A-Za-z0-9_])[A-Za-z]:[\\/]/],
    ['UNC path', /(?:^|[\s"'(])\\\\[^\\/:*?"<>|\r\n]+\\[^\\/:*?"<>|\r\n]+/],
    ['POSIX home path', /\/(?:home|Users)\/[^/\s]+(?:\/|$)/i],
    ['file URI', /file:\/\//i],
    ['volatile Comfy preview URL', /\/view\?/i],
    ['volatile external-preview cache', /_lf_external_previews/i],
    ['editing-session residue', /_edit_dataset\.json/i],
    [
      'private character vocabulary',
      /\b(?:morana|redxiii|shadowheart)\b|m0r4n4|5h4rt/i,
    ],
    [
      'private project or personal vocabulary',
      /\b(?:luca|foscili|velora|eden|azeroth|sentinel|stellaris|garage)\b/i,
    ],
    [
      'email address',
      /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i,
    ],
    ['embedded data URI', /data:[^;,]+[;,]/i],
    [
      'explicit adult-content vocabulary',
      /\b(?:nsfw|n5fw|porn(?:ography|ographic)?|pr0n|nudity|nude|nud3|erotic|3r0tic|hentai|h3ntai|genitals?|lustify|pornmaster)\b/i,
    ],
    ['execution-history timestamp', /Execution (?:date|time):/i],
  ];
  const credentialKey = /^(?:api[_-]?key|x[_-]?api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|private[_-]?key|password|secret|authorization|bearer)$/i;

  const visit = (value: unknown, path: string): void => {
    if (Array.isArray(value)) {
      if (isMessageArray(value) && !isCanonicalMessageFixture(value)) {
        findings.push(`${path}: non-canonical chat history`);
      }
      value.forEach((child, index) => visit(child, `${path}[${index}]`));
      return;
    }
    if (!value || typeof value !== 'object') {
      if (typeof value === 'string') {
        const normalized = value.normalize('NFKC');
        for (const [label, pattern] of blockedStrings) {
          if (pattern.test(normalized)) findings.push(`${path}: ${label}`);
        }
        const trimmed = value.trim();
        if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
          try {
            visit(JSON.parse(trimmed), `${path}#json`);
          } catch {
            // Authoring widgets may intentionally contain invalid JSON while
            // being edited. Other publication checks still inspect the raw
            // string for blocked paths, credentials, and vocabulary.
          }
        }
      }
      return;
    }
    for (const [key, child] of Object.entries(value as JsonRecord)) {
      const childPath = `${path}.${key}`;
      if (key === 'icon' && child === 'history') {
        findings.push(`${childPath}: execution-history node`);
      }
      if (
        key === 'history' &&
        Array.isArray(child) &&
        child.length > 0 &&
        !isCanonicalMessageFixture(child)
      ) {
        findings.push(`${childPath}: non-canonical chat history`);
      }
      if (
        credentialKey.test(key) &&
        ((typeof child === 'string' && child.trim().length > 0) ||
          (child !== null && child !== undefined && typeof child !== 'string'))
      ) {
        findings.push(`${childPath}: non-empty credential field`);
      }
      visit(child, childPath);
    }
  };

  visit(workflow, '$');
  return [...new Set(findings)].sort();
};

export const sanitizeTitanicWorkflow = (
  source: JsonRecord,
): { workflow: JsonRecord; changes: string[] } => {
  const workflow = clone(source);
  const beforeTopology = JSON.stringify(topologyProjection(source));
  const changes: string[] = [];

  if (!Array.isArray(workflow.nodes) || !Array.isArray(workflow.links)) {
    throw new Error('Titanic workflow has no nodes/links arrays');
  }

  for (const node of workflow.nodes) {
    if (node.widgets_values_named && Array.isArray(node.widgets_values)) {
      const names = widgetNames(node);
      if (names.length !== node.widgets_values.length) {
        throw new Error(
          `node ${node.id} ${node.type} widget-name/value cardinality drifted ` +
            `(${names.length} names, ${node.widgets_values.length} values)`,
        );
      }

      for (let index = 0; index < node.widgets_values.length; index += 1) {
        const cleared = clearHistoryDatasets(node.widgets_values[index]);
        node.widgets_values[index] = cleared;
        node.widgets_values_named[names[index]] = clone(cleared);
      }

      if (
        names.includes('ui_widget') &&
        !SEMANTIC_UI_WIDGET_CLASSES.has(String(node.type))
      ) {
        const current = node.widgets_values_named.ui_widget;
        setWidget(node, 'ui_widget', emptyWidgetValue(current), changes);
      }

      if (
        HISTORY_PRIMITIVES.has(String(node.type)) &&
        names.includes('randomize') &&
        typeof node.widgets_values_named.randomize !== 'boolean'
      ) {
        setWidget(node, 'randomize', false, changes);
      }
    }
  }

  const genericCombinedSelector = requireNode(
    workflow,
    49,
    'LF_LoraAndEmbeddingSelector',
  );
  // This old workflow predates the selector's weight/randomize split. Repair
  // the serialized values as part of publication so a private filter cannot
  // survive in the newly inserted boolean slot.
  setWidget(genericCombinedSelector, 'weight', 1, changes);
  setWidget(genericCombinedSelector, 'randomize', false, changes);
  setWidget(genericCombinedSelector, 'filter', '', changes);
  const genericLora = 'PONY\\style\\d0f_v2.safetensors';
  setWidget(requireNode(workflow, 50, 'LF_LoraSelector'), 'lora', genericLora, changes);
  setWidget(requireNode(workflow, 50, 'LF_LoraSelector'), 'filter', '', changes);

  const genericJson = JSON.stringify(GENERIC_JSON_DATASET, null, 2);
  setWidget(requireNode(workflow, 117, 'LF_SortJSONKeys'), 'mutate_source', false, changes);
  setWidget(requireNode(workflow, 119, 'LF_WriteJSON'), 'ui_widget', genericJson, changes);
  setWidget(requireNode(workflow, 333, 'LF_KeywordToggleFromJSON'), 'ui_widget', 'Alpha', changes);
  setWidget(
    requireNode(workflow, 357, 'LF_WriteJSON'),
    'ui_widget',
    JSON.stringify(GENERIC_SEED_DATASET, null, 2),
    changes,
  );
  for (const id of [142, 252]) {
    setWidget(
      requireNode(workflow, id, 'LF_LLMChat'),
      'ui_widget',
      { config: {}, history: clone(GENERIC_CHAT_HISTORY) },
      changes,
    );
  }
  setWidget(
    requireNode(workflow, 145, 'LF_LLMMessenger'),
    'ui_widget',
    clone(GENERIC_MESSENGER_DATASET),
    changes,
  );

  // Repair values that older workflow saves shifted when their public node
  // schemas gained boolean/filter controls. These are typed fixture inputs,
  // not observational state, so publication must leave them executable.
  for (const [id, type] of [
    [51, 'LF_SamplerSelector'],
    [52, 'LF_SchedulerSelector'],
    [250, 'LF_VAESelector'],
    [251, 'LF_UpscaleModelSelector'],
  ] as const) {
    setWidget(requireNode(workflow, id, type), 'randomize', false, changes);
  }
  for (const id of [48, 55, 56]) {
    setWidget(requireNode(workflow, id, 'LF_EmbeddingSelector'), 'filter', '', changes);
  }
  setWidget(
    requireNode(workflow, 453, 'LF_StringTemplate'),
    'use_regex_placeholders',
    false,
    changes,
  );
  const aceStep = requireNode(workflow, 575, 'LF_ACEStepRemix');
  setWidget(aceStep, 'control_after_generate', 'fixed', changes);
  setWidget(aceStep, 'inference_steps', 8, changes);
  setWidget(aceStep, 'guidance_scale', 7, changes);
  setWidget(aceStep, 'infer_method', 'ode', changes);
  setWidget(aceStep, 'shift', 3, changes);
  setWidget(aceStep, 'output_format', 'flac', changes);

  for (const id of [93, 100, 103]) {
    const node = requireNode(workflow, id, 'LF_LoadImages');
    setWidget(node, 'dir', '', changes);
    // `cache_images` was inserted before the observational widget after this
    // graph was first authored; old saved datasets otherwise occupy the new
    // boolean slot and carry their preview URLs into the canonical fixture.
    setWidget(node, 'cache_images', true, changes);
  }
  for (const id of [240, 241]) {
    setWidget(
      requireNode(workflow, id, 'LF_LoadFileOnce'),
      'dir',
      'custom_nodes/lf-nodes/web/deploy/assets/svg',
      changes,
    );
  }
  setWidget(
    requireNode(workflow, 244, 'LF_LoadLocalJSON'),
    'url',
    'custom_nodes/lf-nodes/package.json',
    changes,
  );
  setWidget(
    requireNode(workflow, 363, 'LF_RegionExtractor'),
    'dir',
    'custom_nodes/lf-nodes/modules/nodes/seeds/sequential_seeds_generator.py',
    changes,
  );
  setWidget(
    requireNode(workflow, 481, 'LF_LoadFileOnce'),
    'dir',
    'custom_nodes/lf-nodes/web/deploy/assets/svg',
    changes,
  );

  const afterTopology = JSON.stringify(topologyProjection(workflow));
  if (afterTopology !== beforeTopology) {
    throw new Error('sanitization changed Titanic topology or non-widget metadata');
  }

  const findings = auditSanitizedTitanic(workflow);
  if (findings.length) {
    throw new Error(`sanitized Titanic still contains blocked content:\n${findings.join('\n')}`);
  }

  return { workflow, changes };
};

const parseArgs = (argv: string[]): { input: string; output: string } => {
  let input = defaultInput;
  let output = defaultOutput;
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--input' || arg === '--output') {
      const value = argv[index + 1];
      if (!value || value.startsWith('--')) throw new Error(`${arg} requires a value`);
      if (arg === '--input') input = resolve(value);
      else output = resolve(value);
      index += 1;
      continue;
    }
    throw new Error(`unknown argument: ${arg}`);
  }
  return { input, output };
};

const main = async (): Promise<void> => {
  const options = parseArgs(process.argv.slice(2));
  const sourceBytes = await readFile(options.input);
  const source = JSON.parse(sourceBytes.toString('utf8')) as JsonRecord;
  const { workflow, changes } = sanitizeTitanicWorkflow(source);
  const outputBytes = `${JSON.stringify(workflow)}\n`;
  await mkdir(dirname(options.output), { recursive: true });
  await writeFile(options.output, outputBytes, 'utf8');
  console.log(
    JSON.stringify(
      {
        input: options.input,
        inputSha256: sha256(sourceBytes),
        output: options.output,
        outputSha256: sha256(outputBytes),
        nodes: workflow.nodes.length,
        links: workflow.links.length,
        sanitizedWidgetFields: changes.length,
      },
      null,
      2,
    ),
  );
};

if (resolve(process.argv[1] ?? '') === fileURLToPath(import.meta.url)) {
  await main();
}
