/** Pure helpers for authoring and copying LF visual-novel declarations.
 *
 * These functions deliberately know only the serialized VN contract. They do
 * not depend on LiteGraph, ComfyUI, widgets, or browser state, which makes the
 * copy/paste transformation safe to test before it is connected to a UI hook.
 */

import { parseStrictJson } from './strictJson';

export type JsonRecord = Record<string, unknown>;

export type LfIdGenerator = (kind: string) => string;

export interface JsonIdPathPattern {
  /** RFC 6901 path; `*` matches one array/object segment. */
  path: string;
  kind: string;
  /** Optional property to expose as the identity's author-facing label. */
  label?: string;
}

export interface Identity {
  id: string;
  kind: string;
  path: string;
  label?: string;
}

export interface VnClipboardNode extends JsonRecord {
  type?: string;
  inputs?: unknown[];
  widgets_values?: unknown[];
  widgets_values_named?: JsonRecord;
}

export interface VnClipboardSubgraph extends JsonRecord {
  nodes?: VnClipboardNode[];
  subgraphs?: VnClipboardSubgraph[];
}

export interface VnClipboardItems extends JsonRecord {
  nodes?: VnClipboardNode[];
  subgraphs?: VnClipboardSubgraph[];
}

export interface VnClipboardTransformOptions {
  generateId?: LfIdGenerator;
}

const VN_NODE_FIELDS = {
  LF_VNState: {
    id: ['fixture_id', 0],
    body: ['state_body', 1],
  },
  LF_SceneSpec: {
    id: ['scene_id', 0],
    body: ['scene_body', 2],
  },
  LF_VNSwitch: {
    id: ['switch_id', 0],
    body: ['switch_body', 1],
  },
  LF_VNCompile: {
    id: ['workflow_id', 0],
  },
} as const;

const SCENE_BODY_ID_PATHS: JsonIdPathPattern[] = [
  { path: '/beats/*', kind: 'beat' },
  { path: '/choices/*', kind: 'choice', label: 'label' },
  { path: '/choices/*/effects/*', kind: 'effect' },
  { path: '/artRequests/*', kind: 'art-request' },
];

const SWITCH_BODY_ID_PATHS: JsonIdPathPattern[] = [
  { path: '/cases/*', kind: 'switch-case' },
  { path: '/fallback', kind: 'switch-fallback' },
];

const SCENE_BODY_REF_PATHS = ['/choices/*/nextSceneId'] as const;

const SWITCH_BODY_REF_PATHS = [
  '/cases/*/targetSceneId',
  '/fallback/targetSceneId',
] as const;

const DEFAULT_GENERATOR: LfIdGenerator = (kind) => {
  const uuid =
    typeof globalThis.crypto?.randomUUID === 'function'
      ? globalThis.crypto.randomUUID()
      : `${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}`;
  return `lf:${kind}:${uuid}`;
};

/** Create one LF-owned identity at an explicit authoring-time boundary. */
export const createLfOwnedId = (kind: string): string => DEFAULT_GENERATOR(kind);

const isRecord = (value: unknown): value is JsonRecord =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const clone = <T>(value: T): T => {
  if (typeof structuredClone === 'function') return structuredClone(value);
  return JSON.parse(JSON.stringify(value)) as T;
};

const decodePointerSegment = (segment: string): string =>
  segment.replace(/~1/g, '/').replace(/~0/g, '~');

const encodePointerSegment = (segment: string): string =>
  segment.replace(/~/g, '~0').replace(/\//g, '~1');

const pointerSegments = (path: string): string[] => {
  if (path === '') return [];
  if (!path.startsWith('/')) throw new Error(`JSON pointer must start with '/': ${path}`);
  return path.slice(1).split('/').map(decodePointerSegment);
};

const childEntries = (value: unknown): Array<[string, unknown]> => {
  if (Array.isArray(value)) return value.map((child, index) => [String(index), child]);
  if (isRecord(value)) return Object.entries(value);
  return [];
};

const walkPattern = (
  value: unknown,
  segments: string[],
  visit: (value: JsonRecord, path: string) => void,
  path = '',
): void => {
  if (segments.length === 0) {
    if (isRecord(value)) visit(value, path || '/');
    return;
  }

  const [segment, ...rest] = segments;
  if (segment === '*') {
    for (const [key, child] of childEntries(value)) {
      walkPattern(child, rest, visit, `${path}/${encodePointerSegment(key)}`);
    }
    return;
  }

  if (Array.isArray(value) && /^\d+$/.test(segment)) {
    walkPattern(value[Number(segment)], rest, visit, `${path}/${segment}`);
  } else if (isRecord(value) && Object.prototype.hasOwnProperty.call(value, segment)) {
    walkPattern(value[segment], rest, visit, `${path}/${encodePointerSegment(segment)}`);
  }
};

/** Clone a JSON value and fill missing `id` fields at the supplied pointer patterns. */
export function materializeMissingIds<T>(
  value: T,
  patterns: readonly JsonIdPathPattern[],
  generateId: LfIdGenerator = DEFAULT_GENERATOR,
): T {
  const result = clone(value);
  for (const pattern of patterns) {
    walkPattern(result, pointerSegments(pattern.path), (target) => {
      if (typeof target.id !== 'string' || target.id.length === 0) {
        target.id = generateId(pattern.kind);
      }
    });
  }
  return result;
}

/** Enumerate authored IDs and optional labels at configured body paths. */
export function enumerateIdentities(
  value: unknown,
  patterns: readonly JsonIdPathPattern[],
): Identity[] {
  const identities: Identity[] = [];
  for (const pattern of patterns) {
    walkPattern(value, pointerSegments(pattern.path), (target, path) => {
      if (typeof target.id !== 'string' || target.id.length === 0) return;
      const label = pattern.label ? target[pattern.label] : target.label ?? target.title;
      identities.push({
        id: target.id,
        kind: pattern.kind,
        path,
        ...(typeof label === 'string' && label.length > 0 ? { label } : {}),
      });
    });
  }
  return identities;
}

export const enumerateIdentitiesAndLabels = enumerateIdentities;

const lookup = (idMap: ReadonlyMap<string, string> | JsonRecord, value: unknown): unknown => {
  if (typeof value !== 'string') return value;
  return idMap instanceof Map ? idMap.get(value) ?? value : idMap[value] ?? value;
};

const rewriteAtPointer = (
  value: unknown,
  segments: string[],
  idMap: ReadonlyMap<string, string> | JsonRecord,
): void => {
  if (segments.length === 0) return;
  const [segment, ...rest] = segments;

  if (segment === '*') {
    for (const [, child] of childEntries(value)) rewriteAtPointer(child, rest, idMap);
    return;
  }

  if (rest.length === 0) {
    if (Array.isArray(value) && /^\d+$/.test(segment)) {
      const index = Number(segment);
      if (index < value.length) value[index] = lookup(idMap, value[index]);
    } else if (isRecord(value) && Object.prototype.hasOwnProperty.call(value, segment)) {
      value[segment] = lookup(idMap, value[segment]);
    }
    return;
  }

  if (Array.isArray(value) && /^\d+$/.test(segment)) {
    rewriteAtPointer(value[Number(segment)], rest, idMap);
  } else if (isRecord(value) && Object.prototype.hasOwnProperty.call(value, segment)) {
    rewriteAtPointer(value[segment], rest, idMap);
  }
};

/** Rewrite references only at explicitly configured RFC 6901 paths. */
export function rewriteReferencesAtPaths<T>(
  value: T,
  idMap: ReadonlyMap<string, string> | JsonRecord,
  paths: readonly string[],
): T {
  const result = clone(value);
  for (const path of paths) rewriteAtPointer(result, pointerSegments(path), idMap);
  return result;
}

const parseBody = (value: unknown): unknown => {
  if (typeof value !== 'string') return value;
  try {
    return parseStrictJson(value);
  } catch {
    return value;
  }
};

const writeBody = (original: unknown, body: unknown): unknown =>
  typeof original === 'string' && body !== original ? JSON.stringify(body) : body;

const widgetValue = (node: VnClipboardNode, name: string, index: number): unknown => {
  if (isRecord(node.widgets_values_named) && name in node.widgets_values_named) {
    return node.widgets_values_named[name];
  }
  return Array.isArray(node.widgets_values) ? node.widgets_values[index] : undefined;
};

const setWidgetValue = (
  node: VnClipboardNode,
  name: string,
  index: number,
  value: unknown,
): void => {
  if (isRecord(node.widgets_values_named)) node.widgets_values_named[name] = value;
  if (Array.isArray(node.widgets_values) && index < node.widgets_values.length) {
    node.widgets_values[index] = value;
  }
};

const allNodes = (payload: VnClipboardItems): VnClipboardNode[] => {
  const result: VnClipboardNode[] = [];
  const visitSubgraph = (subgraph: VnClipboardSubgraph): void => {
    result.push(...(subgraph.nodes ?? []));
    subgraph.subgraphs?.forEach(visitSubgraph);
  };
  result.push(...(payload.nodes ?? []));
  payload.subgraphs?.forEach(visitSubgraph);
  return result;
};

interface PendingNode {
  node: VnClipboardNode;
  type: keyof typeof VN_NODE_FIELDS;
  body?: unknown;
  bodyOriginal?: unknown;
  existingBodyIds?: Map<string, string>;
  id?: string;
}

const nodePending = (node: VnClipboardNode): PendingNode | undefined => {
  const type = node.type as keyof typeof VN_NODE_FIELDS;
  const fields = VN_NODE_FIELDS[type];
  if (!fields) return undefined;
  const idName = fields.id[0];
  const idIndex = fields.id[1];
  const bodyField = 'body' in fields ? fields.body : undefined;
  const bodyName = bodyField?.[0];
  const bodyIndex = bodyField?.[1];
  const bodyOriginal = bodyName ? widgetValue(node, bodyName, bodyIndex as number) : undefined;
  const parsedBody = parseBody(bodyOriginal);
  return {
    node,
    type,
    id: typeof widgetValue(node, idName, idIndex) === 'string'
      ? (widgetValue(node, idName, idIndex) as string)
      : undefined,
    ...(bodyName
      ? {
          body: parsedBody,
          bodyOriginal,
          existingBodyIds: new Map(
            enumerateIdentities(parsedBody, type === 'LF_SceneSpec' ? SCENE_BODY_ID_PATHS : SWITCH_BODY_ID_PATHS)
              .map((identity) => [identity.path, identity.id]),
          ),
        }
      : {}),
  };
};

const idKindForNode = (type: PendingNode['type']): string => {
  switch (type) {
    case 'LF_VNState': return 'fixture';
    case 'LF_SceneSpec': return 'scene';
    case 'LF_VNSwitch': return 'switch';
    case 'LF_VNCompile': return 'workflow';
  }
};

const rewriteWithKind = (
  value: unknown,
  maps: ReadonlyMap<string, ReadonlyMap<string, string>>,
  kind: string,
  paths: readonly string[],
): unknown => {
  const map = maps.get(kind);
  return map ? rewriteReferencesAtPaths(value, map, paths) : value;
};

/**
 * Clone and transform Comfy's ClipboardItems-shaped payload.
 *
 * Only LF VN nodes and their known JSON body/reference fields are touched.
 * References whose target is not present in this copied payload are retained.
 */
export function transformVnClipboard<T extends VnClipboardItems>(
  payload: T,
  options: VnClipboardTransformOptions = {},
): T {
  const result = clone(payload);
  const generateId = options.generateId ?? DEFAULT_GENERATOR;
  const pending = allNodes(result)
    .map(nodePending)
    .filter((item): item is PendingNode => item !== undefined);
  const maps = new Map<string, Map<string, string>>();

  const mappedFreshId = (
    kind: string,
    oldId: string | undefined,
    freshId: string,
  ): string => {
    if (!oldId) return freshId;
    let map = maps.get(kind);
    if (!map) {
      map = new Map<string, string>();
      maps.set(kind, map);
    }
    const existing = map.get(oldId);
    if (existing) return existing;
    map.set(oldId, freshId);
    return freshId;
  };

  // Allocate every top-level identity before rewriting any reference, so forward refs work.
  for (const item of pending) {
    const fields = VN_NODE_FIELDS[item.type];
    const [idName, idIndex] = fields.id;
    const freshId = mappedFreshId(
      idKindForNode(item.type),
      item.id,
      generateId(idKindForNode(item.type)),
    );
    setWidgetValue(item.node, idName, idIndex, freshId);
  }

  // Materialize missing body identities after top-level IDs have been allocated.
  for (const item of pending) {
    if (item.body !== undefined && item.bodyOriginal !== undefined) {
      const fields = VN_NODE_FIELDS[item.type];
      const bodyPatterns = item.type === 'LF_SceneSpec' ? SCENE_BODY_ID_PATHS : SWITCH_BODY_ID_PATHS;
      const materialized = materializeMissingIds(item.body, bodyPatterns, generateId);
      item.body = materialized;
      const bodyField = 'body' in fields ? fields.body : undefined;
      if (bodyField) setWidgetValue(item.node, bodyField[0], bodyField[1], writeBody(item.bodyOriginal, materialized));
    }
  }

  // Allocate nested identities in a separate pass. This is important for a
  // forward scene reference from the first copied node to a later node.
  for (const item of pending) {
    if (item.body === undefined || item.bodyOriginal === undefined) continue;
    const patterns = item.type === 'LF_SceneSpec' ? SCENE_BODY_ID_PATHS : SWITCH_BODY_ID_PATHS;
    const identities = enumerateIdentities(item.body, patterns);
    for (const identity of identities) {
      const oldId = item.existingBodyIds?.get(identity.path);
      if (!oldId) continue;
      const freshId = mappedFreshId(identity.kind, oldId, generateId(identity.kind));
      walkPattern(item.body, pointerSegments(identity.path), (target) => { target.id = freshId; });
    }
  }

  // Rewrite only known scene references after every copied identity has a map.
  for (const item of pending) {
    if (item.body === undefined || item.bodyOriginal === undefined) continue;
    const referencePaths = item.type === 'LF_SceneSpec'
      ? SCENE_BODY_REF_PATHS
      : item.type === 'LF_VNSwitch'
        ? SWITCH_BODY_REF_PATHS
        : [];
    const body = rewriteWithKind(item.body, maps, 'scene', referencePaths);
    const itemFields = VN_NODE_FIELDS[item.type];
    const bodyField = 'body' in itemFields ? itemFields.body : undefined;
    if (bodyField) setWidgetValue(item.node, bodyField[0], bodyField[1], writeBody(item.bodyOriginal, body));
  }

  for (const item of pending) {
    const type = item.type;
    if (type === 'LF_VNCompile') {
      const fields = VN_NODE_FIELDS[type];
      const workflow = lookup(maps.get('workflow') ?? new Map(), widgetValue(item.node, 'workflow_id', fields.id[1]));
      setWidgetValue(item.node, 'workflow_id', fields.id[1], workflow);
      setWidgetValue(item.node, 'entry_scene_id', 1, lookup(maps.get('scene') ?? new Map(), widgetValue(item.node, 'entry_scene_id', 1)));
      setWidgetValue(item.node, 'selected_choice_id', 2, lookup(maps.get('choice') ?? new Map(), widgetValue(item.node, 'selected_choice_id', 2)));
    }

    // Newer serialized nodes identify LF_REF widgets directly in `inputs`.
    // Use their declared kind when available, with the VN field names as a
    // compatibility fallback for older snapshots.
    let widgetIndex = 0;
    for (const input of item.node.inputs ?? []) {
      if (!isRecord(input) || !isRecord(input.widget)) continue;
      const name = typeof input.name === 'string' ? input.name : undefined;
      const inputType = input.type;
      const widget = input.widget;
      const kind = typeof widget.lf_ref_kind === 'string'
        ? widget.lf_ref_kind
        : typeof input.lf_ref_kind === 'string'
          ? input.lf_ref_kind
          : name === 'entry_scene_id'
            ? 'scene'
            : name === 'selected_choice_id'
              ? 'choice'
              : undefined;
      if (typeof inputType === 'string' && inputType === 'LF_REF' && kind && name) {
        const value = widgetValue(item.node, name, widgetIndex);
        setWidgetValue(item.node, name, widgetIndex, lookup(maps.get(kind) ?? new Map(), value));
      }
      widgetIndex += 1;
    }
  }

  return result;
}
