import { enumerateIdentities, JsonIdPathPattern } from './visualNovel';
import { parseStrictJson } from './strictJson';

export interface IdentityCandidate {
  id: string;
  kind: string;
  label: string;
}

interface IdentityWidgetState {
  getLabel?: () => string;
  kind?: string;
}

interface TextareaIdentityState {
  idPaths?: JsonIdPathPattern[];
}

const widgetValue = (widget: Widget<any>): unknown =>
  widget.options?.getValue ? widget.options.getValue() : widget.value;

const candidateLabel = (
  state: IdentityWidgetState | undefined,
  node: NodeType,
  id: string,
): string => {
  const explicit = state?.getLabel?.().trim();
  if (explicit) return explicit;
  const title = (node as NodeType & { title?: string }).title?.trim();
  return title || node.comfyClass || id;
};

/**
 * Discover identities already authored in the current graph.
 *
 * The picker shows labels, but every option value remains the immutable ID.
 * This helper intentionally reads only LF_ID and configured LF_TEXTAREA
 * widgets; consumer catalogues can still feed LF_REF through typed links.
 */
export const collectIdentityCandidates = (
  origin: NodeType,
  kind: string,
): IdentityCandidate[] => {
  const nodes = origin.graph?._nodes ?? [origin];
  const candidates = new Map<string, IdentityCandidate>();

  for (const node of nodes) {
    for (const widget of node.widgets ?? []) {
      const type = String(widget.type ?? '').toUpperCase();
      if (type === 'LF_ID') {
        const state = widget.options?.getState?.() as IdentityWidgetState | undefined;
        const id = widgetValue(widget);
        if (state?.kind === kind && typeof id === 'string' && id) {
          candidates.set(id, {
            id,
            kind,
            label: candidateLabel(state, node, id),
          });
        }
        continue;
      }

      if (type !== 'LF_TEXTAREA') continue;
      const state = widget.options?.getState?.() as TextareaIdentityState | undefined;
      if (!state?.idPaths?.length) continue;
      const value = widgetValue(widget);
      try {
        const parsed = typeof value === 'string' ? parseStrictJson(value) : value;
        for (const identity of enumerateIdentities(parsed, state.idPaths)) {
          if (identity.kind !== kind) continue;
          candidates.set(identity.id, {
            id: identity.id,
            kind,
            label: identity.label || identity.id,
          });
        }
      } catch {
        // Invalid raw JSON remains visibly marked by LF_TEXTAREA and cannot
        // contribute a misleading reference candidate.
      }
    }
  }

  return [...candidates.values()].sort((left, right) =>
    left.label.localeCompare(right.label) || left.id.localeCompare(right.id),
  );
};
