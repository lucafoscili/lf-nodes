import { createHash } from 'node:crypto';
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

type JsonRecord = Record<string, any>;

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..', '..');
const defaultExampleDir = resolve(repoRoot, 'example_workflows');

const EDITOR_NODE_TYPES = new Set([
  'LF_ImagesEditingBreakpoint',
  'LF_LoadAndEditImages',
]);

const SEMANTIC_WIDGET_TYPES = new Set([
  'LF_KeywordToggleFromJSON',
  'LF_LLMChat',
  'LF_LLMMessenger',
  'LF_UrandomSeedGenerator',
  'LF_WriteJSON',
]);

export const GENERIC_CHAT_HISTORY = [
  {
    role: 'user',
    content: 'Return one short, generic test response.',
  },
];

export const GENERIC_MESSENGER_CHAT = [
  { role: 'user', content: 'Hello.' },
  {
    role: 'assistant',
    content: 'Welcome to this generic example.',
  },
];

const WINDOWS_ABSOLUTE_PATH = /^[A-Za-z]:[\\/]/;
const UNC_PATH = /^\\\\/;
const POSIX_HOME_PATH = /^\/(?:home|Users)\//i;
const CREDENTIAL_KEY = /^(?:api[_-]?key|x[_-]?api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|private[_-]?key|password|secret|authorization|bearer)$/i;

const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

const isRecord = (value: unknown): value is JsonRecord =>
  Boolean(value) && typeof value === 'object' && !Array.isArray(value);

const hasContent = (value: unknown): boolean => {
  if (Array.isArray(value)) return value.length > 0;
  if (isRecord(value)) return Object.keys(value).length > 0;
  if (typeof value === 'string') return value.trim().length > 0;
  return value !== null && value !== undefined && value !== false;
};

const isMessageArray = (value: unknown): value is JsonRecord[] =>
  Array.isArray(value) &&
  value.length > 0 &&
  value.every(
    (entry) =>
      isRecord(entry) &&
      typeof entry.role === 'string' &&
      typeof entry.content === 'string',
  );

const canonicalMessages = (nodeType: string): JsonRecord[] =>
  clone(
    nodeType === 'LF_LLMMessenger'
      ? GENERIC_MESSENGER_CHAT
      : GENERIC_CHAT_HISTORY,
  );

const isAbsoluteLocalPath = (value: string): boolean =>
  WINDOWS_ABSOLUTE_PATH.test(value) ||
  UNC_PATH.test(value) ||
  POSIX_HOME_PATH.test(value) ||
  /^file:\/\//i.test(value);

const sanitizeAbsolutePath = (value: string): string => {
  const normalized = value.replace(/^file:\/\//i, '').replace(/\\/g, '/');
  const lower = normalized.toLowerCase();
  const comfyMarker = '/comfyui/';
  const comfyIndex = lower.lastIndexOf(comfyMarker);

  if (comfyIndex >= 0) {
    const relative = normalized.slice(comfyIndex + comfyMarker.length);
    if (/^temp(?:\/|$)/i.test(relative) || /_edit_dataset\.json$/i.test(relative)) {
      return '';
    }
    if (/^models(?:\/|$)/i.test(relative)) {
      return relative.split('/').filter(Boolean).at(-1) ?? '';
    }
    return relative;
  }

  const leaf = normalized.split('/').filter(Boolean).at(-1) ?? '';
  return extname(leaf) ? leaf : '';
};

const sanitizeString = (
  value: string,
  nodeType: string,
  changes: string[],
  path: string,
): string => {
  const trimmed = value.trim();
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      const parsed = JSON.parse(trimmed) as unknown;
      const sanitized = sanitizeWidgetValue(parsed, nodeType, changes, `${path}#json`);
      const indentation = value.includes('\n') ? 2 : undefined;
      const result = JSON.stringify(sanitized, null, indentation);
      if (result !== value) changes.push(path);
      return result;
    } catch {
      // Plain text and intentionally incomplete JSON remain strings. The
      // publication audit still inspects them for local or transient content.
    }
  }

  if (
    /^data:image\//i.test(trimmed) ||
    /\/view\?/i.test(value) ||
    /Execution (?:date|time):/i.test(value)
  ) {
    changes.push(path);
    return '';
  }

  if (isAbsoluteLocalPath(trimmed)) {
    const result = sanitizeAbsolutePath(trimmed);
    if (result !== value) changes.push(path);
    return result;
  }

  let result = value
    .replace(/\bLuca\s+Foscili\b/gi, 'Example User')
    .replace(/\bLuca\b/gi, 'User')
    .replace(/\bFoscili\b/gi, 'User');

  if (/^[a-z][a-z\d+.-]*:\/\//i.test(result)) {
    try {
      const url = new URL(result);
      if (url.searchParams.has('nonce')) {
        url.searchParams.delete('nonce');
        result = url.toString();
      }
    } catch {
      // Leave non-standard URLs for the audit below.
    }
  }

  if (result !== value) changes.push(path);
  return result;
};

const containsTransientState = (value: unknown): boolean => {
  if (typeof value === 'string') {
    return (
      /\/view\?|^data:image\//i.test(value) ||
      /_edit_dataset\.json/i.test(value) ||
      /Execution (?:date|time):/i.test(value) ||
      isAbsoluteLocalPath(value.trim())
    );
  }
  if (Array.isArray(value)) {
    return (
      isMessageArray(value) || value.some((child) => containsTransientState(child))
    );
  }
  if (!isRecord(value)) return false;

  return Object.entries(value).some(([key, child]) => {
    if (
      key === 'context_id' ||
      key === 'dataset' ||
      key === 'history' ||
      key === 'lfDataset' ||
      key === 'navigation' ||
      key === 'nonce' ||
      key === 'selection'
    ) {
      return true;
    }
    if (key === 'icon' && child === 'history') return true;
    return containsTransientState(child);
  });
};

const sanitizeValue = (
  value: unknown,
  nodeType: string,
  changes: string[],
  path: string,
): unknown => {
  if (typeof value === 'string') {
    return sanitizeString(value, nodeType, changes, path);
  }
  if (isMessageArray(value)) {
    const result = canonicalMessages(nodeType);
    if (JSON.stringify(result) !== JSON.stringify(value)) changes.push(path);
    return result;
  }
  if (Array.isArray(value)) {
    return value.map((child, index) =>
      sanitizeValue(child, nodeType, changes, `${path}[${index}]`),
    );
  }
  if (!isRecord(value)) return value;

  if (
    nodeType === 'LF_UrandomSeedGenerator' &&
    value.icon === 'history' &&
    Array.isArray(value.children)
  ) {
    changes.push(path);
    return {
      id: 'fixture-seeds',
      value: 'Fixture seeds',
      children: sanitizeValue(
        value.children,
        nodeType,
        changes,
        `${path}.children`,
      ),
    };
  }

  const output: JsonRecord = {};
  for (const [key, child] of Object.entries(value)) {
    const childPath = `${path}.${key}`;
    if (CREDENTIAL_KEY.test(key)) {
      output[key] = '';
      if (hasContent(child)) changes.push(childPath);
      continue;
    }
    if (key === 'nonce') {
      changes.push(childPath);
      continue;
    }
    if (key === 'context_id' || key === 'navigation' || key === 'selection') {
      changes.push(childPath);
      continue;
    }
    if (key === 'lfDataset') {
      output[key] = {};
      if (hasContent(child)) changes.push(childPath);
      continue;
    }
    if (key === 'dataset' && nodeType !== 'LF_LLMMessenger') {
      output[key] = {};
      if (hasContent(child)) changes.push(childPath);
      continue;
    }
    if (key === 'history') {
      output[key] = Array.isArray(child) ? canonicalMessages(nodeType) : {};
      if (JSON.stringify(output[key]) !== JSON.stringify(child)) {
        changes.push(childPath);
      }
      continue;
    }
    if (key === 'icon' && child === 'history') {
      changes.push(childPath);
      continue;
    }
    if (
      typeof child === 'string' &&
      /^Execution (?:date|time):/i.test(child)
    ) {
      changes.push(childPath);
      continue;
    }
    output[key] = sanitizeValue(child, nodeType, changes, childPath);
  }
  return output;
};

const sanitizeEditorWidget = (
  value: unknown,
  nodeType: string,
  changes: string[],
  path: string,
): unknown => {
  if (!isRecord(value)) return sanitizeValue(value, nodeType, changes, path);
  const output: JsonRecord = {};
  if (isRecord(value.defaults)) {
    output.defaults = sanitizeValue(
      value.defaults,
      nodeType,
      changes,
      `${path}.defaults`,
    );
  }
  if (JSON.stringify(output) !== JSON.stringify(value)) changes.push(path);
  return output;
};

const sanitizeWidgetValue = (
  value: unknown,
  nodeType: string,
  changes: string[],
  path: string,
): unknown => {
  if (EDITOR_NODE_TYPES.has(nodeType)) {
    if (typeof value === 'string') {
      const trimmed = value.trim();
      if (trimmed.startsWith('{')) {
        try {
          const result = sanitizeEditorWidget(
            JSON.parse(trimmed),
            nodeType,
            changes,
            `${path}#json`,
          );
          const serialized = JSON.stringify(result, null, value.includes('\n') ? 2 : undefined);
          if (serialized !== value) changes.push(path);
          return serialized;
        } catch {
          // Fall through to ordinary string sanitation.
        }
      }
    } else if (isRecord(value)) {
      return sanitizeEditorWidget(value, nodeType, changes, path);
    }
  }

  if (
    !SEMANTIC_WIDGET_TYPES.has(nodeType) &&
    (isRecord(value) || Array.isArray(value)) &&
    containsTransientState(value)
  ) {
    changes.push(path);
    return Array.isArray(value) ? [] : {};
  }

  return sanitizeValue(value, nodeType, changes, path);
};

export const exampleTopologyProjection = (workflow: JsonRecord): JsonRecord => ({
  last_node_id: workflow.last_node_id,
  last_link_id: workflow.last_link_id,
  links: clone(workflow.links ?? []),
  groups: clone(workflow.groups ?? []),
  nodes: (workflow.nodes ?? []).map((node: JsonRecord) => ({
    id: node.id,
    type: node.type,
    mode: node.mode,
    order: node.order,
    inputs: clone(node.inputs ?? []),
    outputs: clone(node.outputs ?? []),
  })),
});

export const auditSanitizedExample = (workflow: JsonRecord): string[] => {
  const findings: string[] = [];
  const blockedStrings: Array<[string, RegExp]> = [
    ['absolute Windows path', /(?:^|[^A-Za-z0-9_])[A-Za-z]:[\\/]/],
    ['UNC path', /(?:^|[\s"'(])\\\\[^\\/:*?"<>|\r\n]+\\[^\\/:*?"<>|\r\n]+/],
    ['POSIX home path', /\/(?:home|Users)\/[^/\s]+(?:\/|$)/i],
    ['file URI', /file:\/\//i],
    ['volatile Comfy preview URL', /\/view\?/i],
    ['volatile external-preview cache', /_lf_external_previews/i],
    ['editing-session residue', /_edit_dataset\.json/i],
    ['embedded image data URI', /data:image\//i],
    ['cache-busting nonce', /(?:[?&]|\b)nonce=/i],
    ['private username', /\b(?:luca|foscili)\b/i],
    ['execution-history timestamp', /Execution (?:date|time):/i],
  ];

  const visit = (value: unknown, path: string, nodeType = ''): void => {
    if (Array.isArray(value)) {
      value.forEach((child, index) => visit(child, `${path}[${index}]`, nodeType));
      return;
    }
    if (!isRecord(value)) {
      if (typeof value === 'string') {
        const normalized = value.normalize('NFKC');
        for (const [label, pattern] of blockedStrings) {
          if (pattern.test(normalized)) findings.push(`${path}: ${label}`);
        }
        const trimmed = value.trim();
        if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
          try {
            visit(JSON.parse(trimmed), `${path}#json`, nodeType);
          } catch {
            // Invalid authoring JSON is still inspected as a raw string.
          }
        }
      }
      return;
    }

    for (const [key, child] of Object.entries(value)) {
      const childPath = `${path}.${key}`;
      if (key === 'nonce') findings.push(`${childPath}: nonce state`);
      if (
        (key === 'context_id' || key === 'navigation' || key === 'selection') &&
        hasContent(child)
      ) {
        findings.push(`${childPath}: transient editor state`);
      }
      if (key === 'lfDataset' && hasContent(child)) {
        findings.push(`${childPath}: transient selector dataset`);
      }
      if (
        key === 'dataset' &&
        nodeType !== 'LF_LLMMessenger' &&
        hasContent(child)
      ) {
        findings.push(`${childPath}: transient observational dataset`);
      }
      if (key === 'icon' && child === 'history') {
        findings.push(`${childPath}: execution-history node`);
      }
      if (CREDENTIAL_KEY.test(key) && hasContent(child)) {
        findings.push(`${childPath}: non-empty credential field`);
      }
      visit(child, childPath, nodeType);
    }
  };

  for (const [index, node] of (workflow.nodes ?? []).entries()) {
    const nodeType = String(node.type ?? '');
    visit(node.widgets_values ?? [], `$.nodes[${index}].widgets_values`, nodeType);
    visit(
      node.widgets_values_named ?? {},
      `$.nodes[${index}].widgets_values_named`,
      nodeType,
    );
    visit(node.properties ?? {}, `$.nodes[${index}].properties`, nodeType);
  }
  visit(workflow.extra ?? {}, '$.extra');
  visit(workflow.config ?? {}, '$.config');

  return [...new Set(findings)].sort();
};

export const sanitizeExampleWorkflow = (
  source: JsonRecord,
): { workflow: JsonRecord; changes: string[] } => {
  if (!Array.isArray(source.nodes) || !Array.isArray(source.links)) {
    throw new Error('example workflow has no nodes/links arrays');
  }

  const workflow = clone(source);
  const beforeTopology = JSON.stringify(exampleTopologyProjection(workflow));
  const changes: string[] = [];

  for (const [index, node] of workflow.nodes.entries()) {
    const nodeType = String(node.type ?? '');
    if (Array.isArray(node.widgets_values)) {
      node.widgets_values = node.widgets_values.map((value: unknown, widgetIndex: number) =>
        sanitizeWidgetValue(
          value,
          nodeType,
          changes,
          `$.nodes[${index}].widgets_values[${widgetIndex}]`,
        ),
      );
    }
    if (isRecord(node.widgets_values_named)) {
      node.widgets_values_named = Object.fromEntries(
        Object.entries(node.widgets_values_named).map(([name, value]) => [
          name,
          sanitizeWidgetValue(
            value,
            nodeType,
            changes,
            `$.nodes[${index}].widgets_values_named.${name}`,
          ),
        ]),
      );
    }
    if (isRecord(node.properties)) {
      node.properties = sanitizeValue(
        node.properties,
        nodeType,
        changes,
        `$.nodes[${index}].properties`,
      );
    }
  }

  workflow.extra = sanitizeValue(workflow.extra ?? {}, '', changes, '$.extra');
  workflow.config = sanitizeValue(workflow.config ?? {}, '', changes, '$.config');

  const afterTopology = JSON.stringify(exampleTopologyProjection(workflow));
  if (afterTopology !== beforeTopology) {
    throw new Error('example sanitization changed graph topology or socket schemas');
  }

  const findings = auditSanitizedExample(workflow);
  if (findings.length) {
    throw new Error(
      `sanitized example still contains blocked content:\n${findings.join('\n')}`,
    );
  }

  return { workflow, changes: [...new Set(changes)].sort() };
};

const sha256 = (value: string | Buffer): string =>
  createHash('sha256').update(value).digest('hex');

const parseArgs = (argv: string[]): { directory: string; check: boolean } => {
  let directory = defaultExampleDir;
  let check = false;
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--check') {
      check = true;
      continue;
    }
    if (arg === '--dir') {
      const value = argv[index + 1];
      if (!value || value.startsWith('--')) throw new Error('--dir requires a value');
      directory = resolve(value);
      index += 1;
      continue;
    }
    throw new Error(`unknown argument: ${arg}`);
  }
  return { directory, check };
};

const main = async (): Promise<void> => {
  const options = parseArgs(process.argv.slice(2));
  const files = (await readdir(options.directory))
    .filter((file) => file.toLowerCase().endsWith('.json'))
    .sort((left, right) => left.localeCompare(right));

  const results: JsonRecord[] = [];
  for (const file of files) {
    const path = resolve(options.directory, file);
    const sourceBytes = await readFile(path);
    const source = JSON.parse(sourceBytes.toString('utf8')) as JsonRecord;
    const { workflow, changes } = sanitizeExampleWorkflow(source);
    const outputBytes = `${JSON.stringify(workflow)}\n`;
    const changed = !sourceBytes.equals(Buffer.from(outputBytes));
    if (options.check && changed) {
      throw new Error(`${file} is not in deterministic sanitized form`);
    }
    if (!options.check && changed) await writeFile(path, outputBytes, 'utf8');
    results.push({
      file,
      changed,
      sha256: sha256(outputBytes),
      nodes: workflow.nodes.length,
      links: workflow.links.length,
      sanitizedFields: changes.length,
    });
  }

  console.log(
    JSON.stringify(
      {
        directory: options.directory,
        mode: options.check ? 'check' : 'write',
        files: results.length,
        results,
      },
      null,
      2,
    ),
  );
};

if (resolve(process.argv[1] ?? '') === fileURLToPath(import.meta.url)) {
  await main();
}
