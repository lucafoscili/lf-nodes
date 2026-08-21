import {
  cancelTextareaValidation,
  parseStrictJson,
  scheduleTextareaValidation,
  validateAndFormatTextarea,
} from '../helpers/textarea';
import {
  JsonIdPathPattern,
  JsonRecord,
  materializeMissingIds,
} from '../helpers/visualNovel';
import { collectIdentityCandidates } from '../helpers/visualNovelGraph';
import {
  TextareaCSS,
  TextareaDeserializedValue,
  TextareaFactory,
  TextareaReferencePathPattern,
  TextareaState,
} from '../types/widgets/textarea';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, TextareaState>();

const isRecord = (value: unknown): value is JsonRecord =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const readInputOptions = (inputData: unknown): JsonRecord => {
  const candidate = Array.isArray(inputData) ? inputData[1] : inputData;
  return isRecord(candidate) ? candidate : {};
};

const readIdPaths = (options: JsonRecord): JsonIdPathPattern[] => {
  if (!Array.isArray(options.lf_id_paths)) return [];
  return options.lf_id_paths.flatMap((value) => {
    if (!isRecord(value) || typeof value.path !== 'string' || typeof value.kind !== 'string') {
      return [];
    }
    return [{
      path: value.path,
      kind: value.kind,
      ...(typeof value.label === 'string' ? { label: value.label } : {}),
    }];
  });
};

const readRefPaths = (options: JsonRecord): TextareaReferencePathPattern[] => {
  if (!Array.isArray(options.lf_ref_paths)) return [];
  return options.lf_ref_paths.flatMap((value) => {
    if (!isRecord(value) || typeof value.path !== 'string' || typeof value.kind !== 'string') {
      return [];
    }
    return [{ path: value.path, kind: value.kind }];
  });
};

const decodePointerSegment = (segment: string): string =>
  segment.replace(/~1/g, '/').replace(/~0/g, '~');

const encodePointerSegment = (segment: string): string =>
  segment.replace(/~/g, '~0').replace(/\//g, '~1');

interface ReferenceLocation {
  current: string;
  key: string;
  label: string;
  parent: JsonRecord;
  path: string;
}

const referenceLocations = (
  value: unknown,
  pointer: string,
): ReferenceLocation[] => {
  if (!pointer.startsWith('/')) return [];
  const segments = pointer.slice(1).split('/').map(decodePointerSegment);
  const result: ReferenceLocation[] = [];

  const visit = (current: unknown, index: number, path: string) => {
    if (index >= segments.length) return;
    const segment = segments[index];
    const isLast = index === segments.length - 1;

    if (segment === '*') {
      const entries = Array.isArray(current)
        ? current.map((child, childIndex) => [String(childIndex), child] as const)
        : isRecord(current)
          ? Object.entries(current)
          : [];
      for (const [key, child] of entries) {
        visit(child, index + 1, `${path}/${encodePointerSegment(key)}`);
      }
      return;
    }

    if (isLast) {
      if (!isRecord(current) || !Object.prototype.hasOwnProperty.call(current, segment)) return;
      const authored = current[segment];
      const context = [current.label, current.title, current.text, current.id]
        .find((item) => typeof item === 'string' && item.trim()) as string | undefined;
      result.push({
        current: typeof authored === 'string' ? authored : '',
        key: segment,
        label: context || `${path || '/'}${path ? '/' : ''}${segment}`,
        parent: current,
        path: `${path}/${encodePointerSegment(segment)}`,
      });
      return;
    }

    if (Array.isArray(current) && /^\d+$/.test(segment)) {
      visit(current[Number(segment)], index + 1, `${path}/${segment}`);
    } else if (isRecord(current) && Object.prototype.hasOwnProperty.call(current, segment)) {
      visit(current[segment], index + 1, `${path}/${encodePointerSegment(segment)}`);
    }
  };

  visit(value, 0, '');
  return result;
};

const compactId = (id: string) => {
  const parts = id.split(':');
  const tail = parts.at(-1) || id;
  return tail.length > 10 ? `${tail.slice(0, 8)}…` : tail;
};

const populateReferenceSelect = (
  state: TextareaState,
  select: HTMLSelectElement,
  kind: string,
  current: string,
) => {
  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = `Choose ${kind.replaceAll('-', ' ')}…`;
  select.replaceChildren(placeholder);

  let resolved = false;
  for (const candidate of collectIdentityCandidates(state.node, kind)) {
    const option = document.createElement('option');
    option.value = candidate.id;
    option.textContent = `${candidate.label} · ${compactId(candidate.id)}`;
    option.title = candidate.id;
    select.appendChild(option);
    if (candidate.id === current) resolved = true;
  }

  if (current && !resolved) {
    const unresolved = document.createElement('option');
    unresolved.value = current;
    unresolved.textContent = `Unresolved · ${compactId(current)}`;
    unresolved.title = current;
    select.appendChild(unresolved);
  }
  select.value = current;
};

const normalizeDocument = (state: TextareaState, value: unknown) =>
  state.idPaths.length ? materializeMissingIds(value, state.idPaths) : value;

const renderReferenceControls = (state: TextareaState, value: unknown) => {
  state.references.replaceChildren();
  state.references.hidden = state.refPaths.length === 0;
  if (!state.refPaths.length) return;

  for (const pattern of state.refPaths) {
    for (const location of referenceLocations(value, pattern.path)) {
      const row = document.createElement('label');
      const label = document.createElement('span');
      const select = document.createElement('select');

      row.classList.add(TextareaCSS.Reference);
      label.classList.add(TextareaCSS.ReferenceLabel);
      select.classList.add(TextareaCSS.ReferenceSelect);
      label.textContent = location.label;
      label.title = location.path;

      const refresh = () => {
        let current = location.current;
        try {
          const latest = parseStrictJson(state.textarea.value);
          const match = referenceLocations(latest, pattern.path)
            .find((item) => item.path === location.path);
          if (match) current = match.current;
        } catch {}
        populateReferenceSelect(state, select, pattern.kind, current);
      };
      refresh();
      select.addEventListener('pointerdown', refresh);
      select.addEventListener('focus', refresh);
      select.addEventListener('change', () => {
        try {
          const parsed = parseStrictJson(state.textarea.value);
          const target = referenceLocations(parsed, pattern.path)
            .find((item) => item.path === location.path);
          if (!target) return;
          target.parent[target.key] = select.value;
          state.textarea.value = JSON.stringify(parsed);
          validateAndFormatTextarea(
            state.textarea,
            (next) => normalizeDocument(state, next),
            (next) => renderReferenceControls(state, next),
          );
          (state.node.graph as unknown as { setDirtyCanvas?: (fg: boolean, bg: boolean) => void })
            ?.setDirtyCanvas?.(true, true);
        } catch {}
      });

      row.append(label, select);
      state.references.appendChild(row);
    }
  }
};

const refreshReferencesAfterHydration = (state: TextareaState): void => {
  if (!state.refPaths.length) return;
  globalThis.setTimeout(() => {
    try {
      renderReferenceControls(state, parseStrictJson(state.textarea.value));
    } catch {
      // Invalid authored text stays visible and retains its error styling.
    }
  }, 0);
};

const validateState = (state: TextareaState) =>
  validateAndFormatTextarea(
    state.textarea,
    (value) => normalizeDocument(state, value),
    (value) => renderReferenceControls(state, value),
  );

export const textareaFactory: TextareaFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { textarea } = STATE.get(wrapper);

        return textarea?.value ?? '{}';
      },
      setValue(value) {
        const state = STATE.get(wrapper);
        const hydrated: unknown = value;
        state.textarea.value = typeof hydrated === 'string'
          ? hydrated
          : JSON.stringify(hydrated as TextareaDeserializedValue);
        validateState(state);
        // During workflow configure, a valid target node can hydrate after the
        // textarea that references it. Rebuild the picker once that pass ends.
        refreshReferencesAfterHydration(state);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node, inputName = 'ui_widget', inputData) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const textarea = document.createElement(TagName.Textarea);
    const references = document.createElement(TagName.Div);
    const inputOptions = readInputOptions(inputData);

    content.classList.add(TextareaCSS.Content);
    references.classList.add(TextareaCSS.References);
    references.hidden = true;
    content.append(textarea, references);

    textarea.classList.add(TextareaCSS.Widget);

    wrapper.appendChild(content);

    const options = textareaFactory.options(wrapper);

    const state: TextareaState = {
      idPaths: readIdPaths(inputOptions),
      inputName,
      node,
      references,
      refPaths: readRefPaths(inputOptions),
      textarea,
      wrapper,
    };
    STATE.set(wrapper, state);

    textarea.addEventListener('input', () => {
      scheduleTextareaValidation(
        textarea,
        (value) => normalizeDocument(state, value),
        (value) => renderReferenceControls(state, value),
      );
    });
    textarea.addEventListener('blur', () => {
      cancelTextareaValidation(textarea);
      validateState(state);
    });

    return {
      widget: createDOMWidget(CustomWidgetName.textarea, wrapper, node, options, inputName),
    };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
