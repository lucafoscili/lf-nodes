import { collectIdentityCandidates } from '../helpers/visualNovelGraph';
import { createLfOwnedId, rewriteReferencesAtPaths } from '../helpers/visualNovel';
import { parseStrictJson } from '../helpers/textarea';
import {
  IdentityCSS,
  IdentityInputOptions,
  IdentityState,
  IdFactory,
  RefFactory,
} from '../types/widgets/identity';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget } from '../utils/common';

const ID_STATE = new WeakMap<HTMLDivElement, IdentityState>();
const REF_STATE = new WeakMap<HTMLDivElement, IdentityState>();

const optionsOf = (inputData: unknown): IdentityInputOptions => {
  if (Array.isArray(inputData)) return (inputData[1] ?? {}) as IdentityInputOptions;
  return (inputData ?? {}) as IdentityInputOptions;
};

export const generateLfId = (kind: string): string => createLfOwnedId(kind || 'id');

const labelFor = (state: IdentityState): string | undefined => {
  if (!state.labelWidget) return undefined;
  const widget = state.node.widgets?.find((candidate) => candidate.name === state.labelWidget);
  const value = widget?.options?.getValue?.() ?? widget?.value;
  return typeof value === 'string' && value.trim() ? value.trim() : undefined;
};

const updateChip = (state: IdentityState): void => {
  if (!state.chip) return;
  const label = labelFor(state);
  state.chip.textContent = label ? `${label} · ${state.value}` : state.value || 'Unassigned';
  state.chip.title = state.value ? `Copy ${state.value}` : 'No identity assigned';
  state.chip.disabled = !state.value;
};

const refreshAfterHydration = (refresh: () => void): void => {
  globalThis.setTimeout(refresh, 0);
};

const copyValue = async (value: string): Promise<void> => {
  if (!value) return;
  try {
    await globalThis.navigator?.clipboard?.writeText(value);
  } catch {
    // Clipboard permissions are optional; the ID remains visible and can be
    // copied through normal browser text selection.
  }
};

const readValue = (value: unknown): string => (typeof value === 'string' ? value : '');

const idOptions = (wrapper: HTMLDivElement): ReturnType<IdFactory['options']> => ({
  hideOnZoom: true,
  getState: () => ID_STATE.get(wrapper),
  getValue: () => ID_STATE.get(wrapper)?.value || '',
  setValue(value) {
    const state = ID_STATE.get(wrapper);
    if (!state) return;
    const next = readValue(value);
    if (next) state.value = next;
    updateChip(state);
    // Comfy hydrates widgets in serialized order. A semantic ID can therefore
    // arrive before its friendly title widget; refresh once the configure pass
    // has finished so a reopened workflow never keeps the default label.
    refreshAfterHydration(() => updateChip(state));
  },
});

const refOptions = (wrapper: HTMLDivElement): ReturnType<RefFactory['options']> => ({
  hideOnZoom: true,
  getState: () => REF_STATE.get(wrapper),
  getValue: () => {
    const state = REF_STATE.get(wrapper);
    return state?.selected || '';
  },
  setValue(value) {
    const state = REF_STATE.get(wrapper);
    if (!state) return;
    state.selected = readValue(value);
    state.refresh?.();
    // Candidate nodes later in the workflow may not have hydrated yet.
    refreshAfterHydration(() => state.refresh?.());
  },
});

const identityContent = (className: string): [HTMLDivElement, HTMLDivElement] => {
  const wrapper = document.createElement(TagName.Div);
  const content = document.createElement(TagName.Div);
  wrapper.classList.add(IdentityCSS.Content, className);
  content.classList.add(IdentityCSS.Chip);
  wrapper.appendChild(content);
  return [wrapper, content];
};

const graphNodes = (node: NodeType): NodeType[] => {
  const nodes = node.graph?._nodes ?? [];
  return nodes.includes(node) ? nodes : [node, ...nodes];
};

const markGraphChanged = (node: NodeType) => {
  (node.graph as unknown as { setDirtyCanvas?: (fg: boolean, bg: boolean) => void })
    ?.setDirtyCanvas?.(true, true);
};

const remapLiveReferences = (
  node: NodeType,
  kind: string,
  previous: string,
  next: string,
): void => {
  for (const graphNode of graphNodes(node)) {
    for (const widget of graphNode.widgets ?? []) {
      if (String(widget.type ?? '').toUpperCase() === CustomWidgetName.ref) {
        const state = widget.options?.getState?.() as IdentityState | undefined;
        if (
          state?.refKind === kind &&
          (state.selected === previous || state.value === previous)
        ) {
          state.selected = next;
          state.value = next;
          state.refresh?.();
        }
        continue;
      }
      if (String(widget.type ?? '').toUpperCase() !== CustomWidgetName.textarea) continue;
      const textareaState = widget.options?.getState?.() as
        | {
            refPaths?: Array<{ kind: string; path: string }>;
            textarea?: HTMLTextAreaElement;
          }
        | undefined;
      if (!textareaState?.textarea) continue;
      const referencePaths = (textareaState.refPaths ?? [])
        .filter((pattern) => pattern.kind === kind)
        .map((pattern) => pattern.path);
      if (!referencePaths.length) continue;
      try {
        const parsed = parseStrictJson(textareaState.textarea.value || '{}');
        const rewritten = rewriteReferencesAtPaths(
          parsed,
          new Map([[previous, next]]),
          referencePaths,
        );
        if (JSON.stringify(rewritten) !== JSON.stringify(parsed)) {
          const serialized = JSON.stringify(rewritten, null, 2);
          if (widget.options?.setValue) widget.options.setValue(serialized);
          else textareaState.textarea.value = serialized;
        }
      } catch {
        // Invalid text remains untouched; LF_TEXTAREA will continue to show it.
      }
    }
  }
};

export const idFactory: IdFactory = {
  options: idOptions,
  render(node, inputName, inputData) {
    const metadata = optionsOf(inputData);
    const [wrapper, content] = identityContent('lf-id');
    const chip = document.createElement('button');
    const copy = document.createElement('button');
    const regenerate = document.createElement('button');
    const kind = metadata.lf_id_kind || 'id';
    const initial = readValue(metadata.default) || generateLfId(kind);

    chip.type = 'button';
    chip.classList.add(IdentityCSS.Value, IdentityCSS.Copy);
    copy.type = 'button';
    copy.classList.add(IdentityCSS.Copy);
    copy.textContent = 'Copy';
    regenerate.type = 'button';
    regenerate.classList.add(IdentityCSS.Regenerate);
    regenerate.textContent = 'Regenerate';

    const state: IdentityState = {
      node,
      wrapper,
      chip,
      inputName: inputName || '',
      kind,
      labelWidget: metadata.lf_label_widget,
      getLabel: () => labelFor(state) || '',
      selected: initial,
      value: initial,
    };
    const regenerateValue = () => {
      let allowed = false;
      try {
        allowed = globalThis.confirm?.(
          'Regenerate this identity and remap matching references in the current graph?',
        ) ?? false;
      } catch {
        allowed = false;
      }
      if (allowed) {
        const previous = state.value;
        state.value = generateLfId(state.kind);
        remapLiveReferences(state.node, state.kind, previous, state.value);
        updateChip(state);
        markGraphChanged(state.node);
      }
    };
    chip.addEventListener('click', () => {
      updateChip(state);
      copyValue(state.value);
    });
    chip.addEventListener('focus', () => updateChip(state));
    chip.addEventListener('pointerenter', () => updateChip(state));
    copy.addEventListener('click', () => copyValue(state.value));
    regenerate.addEventListener('click', regenerateValue);
    updateChip(state);
    content.append(chip, copy, regenerate);
    ID_STATE.set(wrapper, state);
    return { widget: createDOMWidget(CustomWidgetName.id, wrapper, node, idOptions(wrapper), inputName) };
  },
  state: ID_STATE,
};

export const refFactory: RefFactory = {
  options: refOptions,
  render(node, inputName, inputData) {
    const metadata = optionsOf(inputData);
    const [wrapper, content] = identityContent('lf-ref');
    const select = document.createElement('select');
    const kind = metadata.lf_ref_kind || 'id';
    const state: IdentityState = {
      node,
      wrapper,
      select,
      inputName: inputName || '',
      kind,
      refKind: kind,
      labelWidget: metadata.lf_label_widget,
      selected: readValue(metadata.default),
      value: readValue(metadata.default),
    };

    select.classList.add(IdentityCSS.Select);
    select.addEventListener('focus', () => state.refresh?.());
    select.addEventListener('click', () => state.refresh?.());
    select.addEventListener('change', () => {
      state.selected = select.value;
      state.value = select.value;
      markGraphChanged(state.node);
    });
    state.refresh = () => {
      const selected = state.selected;
      const candidates = collectIdentityCandidates(node, kind);
      select.replaceChildren();
      const empty = document.createElement('option');
      empty.value = '';
      empty.textContent = `Select ${kind}`;
      select.appendChild(empty);
      for (const candidate of candidates) {
        const option = document.createElement('option');
        option.value = candidate.id;
        option.textContent = candidate.label ? `${candidate.label} · ${candidate.id}` : candidate.id;
        select.appendChild(option);
      }
      if (selected && !candidates.some((candidate) => candidate.id === selected)) {
        const unavailable = document.createElement('option');
        unavailable.value = selected;
        unavailable.textContent = `Unavailable · ${selected}`;
        select.appendChild(unavailable);
      }
      select.value = selected;
      state.value = select.value;
    };
    content.appendChild(select);
    REF_STATE.set(wrapper, state);
    state.refresh();
    return { widget: createDOMWidget(CustomWidgetName.ref, wrapper, node, refOptions(wrapper), inputName) };
  },
  state: REF_STATE,
};

export { ID_STATE, REF_STATE };
