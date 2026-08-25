import type { WorkflowUICells } from '../types/section';
import type { WorkflowStore } from '../types/state';
import {
  applyInputPrefill,
  clearRetainedUploadPrefill,
  getRetainedUploadPrefill,
  RETAINED_UPLOAD_EVENT,
  type InputPrefillCell,
} from './input-prefill';

/**
 * A deliberately browser-session-only form snapshot.
 *
 * File objects stay as File objects; nothing in this structure is serialized,
 * uploaded, or written to localStorage until the user explicitly runs a
 * workflow.
 */
export type WorkflowSessionDraft = Record<string, unknown>;

type DraftStore = {
  captureSequences: Map<string, number>;
  drafts: Map<string, WorkflowSessionDraft>;
  revisions: Map<string, number>;
};

const stores = new WeakMap<WorkflowStore, DraftStore>();

const getStore = (store: WorkflowStore): DraftStore => {
  let draftStore = stores.get(store);
  if (!draftStore) {
    draftStore = { captureSequences: new Map(), drafts: new Map(), revisions: new Map() };
    stores.set(store, draftStore);
  }
  return draftStore;
};

const cloneDraft = (draft: WorkflowSessionDraft): WorkflowSessionDraft => {
  const clone: WorkflowSessionDraft = {};
  for (const [id, value] of Object.entries(draft)) {
    clone[id] = Array.isArray(value) ? value.slice() : value;
  }
  return clone;
};

const revision = (draftStore: DraftStore, workflowId: string) =>
  draftStore.revisions.get(workflowId) ?? 0;

const isFileArray = (value: unknown): value is File[] =>
  Array.isArray(value) &&
  value.every((item) => typeof File !== 'undefined' && item instanceof File);

const readCell = async (cell: InputPrefillCell): Promise<unknown> => {
  switch (cell.tagName.toLowerCase()) {
    case 'lf-chat':
      return typeof cell.getHistory === 'function' ? cell.getHistory() : cell.lfValue;
    case 'lf-select': {
      const selected =
        typeof (cell as InputPrefillCell & { getValue?: () => Promise<unknown> }).getValue ===
        'function'
          ? await (cell as InputPrefillCell & { getValue: () => Promise<unknown> }).getValue()
          : cell.lfValue;
      if (selected && typeof selected === 'object' && !Array.isArray(selected)) {
        const node = selected as {
          id?: string;
          value?: string | number;
          workflowValue?: string | number;
        };
        return node.workflowValue ?? node.value ?? node.id ?? null;
      }
      return selected ?? null;
    }
    case 'lf-toggle': {
      const value =
        typeof (cell as InputPrefillCell & { getValue?: () => Promise<unknown> }).getValue ===
        'function'
          ? await (cell as InputPrefillCell & { getValue: () => Promise<unknown> }).getValue()
          : cell.lfValue;
      return value === true || value === 'on' || value === 1;
    }
    case 'lf-upload': {
      const value =
        typeof (cell as InputPrefillCell & { getValue?: () => Promise<unknown> }).getValue ===
        'function'
          ? await (cell as InputPrefillCell & { getValue: () => Promise<unknown> }).getValue()
          : cell.lfValue;
      const files = isFileArray(value) ? value : [];
      if (files.length > 0) {
        return files.slice();
      }
      return getRetainedUploadPrefill(cell) ?? [];
    }
    default:
      return typeof (cell as InputPrefillCell & { getValue?: () => Promise<unknown> }).getValue ===
        'function'
        ? (cell as InputPrefillCell & { getValue: () => Promise<unknown> }).getValue()
        : cell.lfValue;
  }
};

export const getWorkflowSessionDraft = (
  store: WorkflowStore,
  workflowId: string,
): WorkflowSessionDraft | undefined => {
  const draft = getStore(store).drafts.get(workflowId);
  return draft ? cloneDraft(draft) : undefined;
};

/** Replace a workflow draft, used by intentional prefill sources such as Remix. */
export const replaceWorkflowSessionDraft = (
  store: WorkflowStore,
  workflowId: string,
  draft: WorkflowSessionDraft,
): void => {
  const draftStore = getStore(store);
  draftStore.revisions.set(workflowId, revision(draftStore, workflowId) + 1);
  draftStore.drafts.set(workflowId, cloneDraft(draft));
};

/** Clear one workflow only; other workflow drafts in this mounted session remain intact. */
export const clearWorkflowSessionDraft = (
  store: WorkflowStore,
  workflowId: string,
): void => {
  const draftStore = getStore(store);
  draftStore.revisions.set(workflowId, revision(draftStore, workflowId) + 1);
  draftStore.drafts.delete(workflowId);
};

/**
 * Read the mounted LF controls and merge them into this workflow's draft.
 * The revision guard prevents an older asynchronous read from resurrecting a
 * draft after Reset or Remix deliberately superseded it.
 */
export const captureWorkflowSessionDraft = async (
  store: WorkflowStore,
  workflowId: string,
  cells: WorkflowUICells,
): Promise<void> => {
  if (!workflowId) {
    return;
  }
  const draftStore = getStore(store);
  const startedAtRevision = revision(draftStore, workflowId);
  const captureSequence = (draftStore.captureSequences.get(workflowId) ?? 0) + 1;
  draftStore.captureSequences.set(workflowId, captureSequence);
  const captured: WorkflowSessionDraft = {};

  for (const cell of cells || []) {
    if (!cell?.id) {
      continue;
    }
    try {
      captured[cell.id] = await readCell(cell as InputPrefillCell);
    } catch {
      // A custom element may be mid-unmount. Keep its prior draft value and
      // continue preserving the rest of the form.
    }
  }

  if (
    revision(draftStore, workflowId) !== startedAtRevision ||
    draftStore.captureSequences.get(workflowId) !== captureSequence
  ) {
    return;
  }
  draftStore.drafts.set(workflowId, {
    ...(draftStore.drafts.get(workflowId) || {}),
    ...captured,
  });
};

/** Restore normal controls plus still-live File objects selected in this tab. */
export const applyWorkflowSessionDraft = async (
  cells: WorkflowUICells,
  draft: WorkflowSessionDraft,
): Promise<void> => {
  const ordinary: WorkflowSessionDraft = { ...draft };
  for (const cell of cells || []) {
    if (cell.tagName.toLowerCase() !== 'lf-upload' || !cell.id) {
      continue;
    }
    const value = draft[cell.id];
    if (!isFileArray(value)) {
      continue;
    }

    clearRetainedUploadPrefill(cell as InputPrefillCell);
    // LfUpload exposes lfValue as its supported value prop. Keep the same File
    // objects while cloning only the mutable array container.
    (cell as InputPrefillCell).lfValue = value.slice();
    delete ordinary[cell.id];
  }
  await applyInputPrefill(cells as InputPrefillCell[], ordinary);
};

const EVENTS_BY_TAG: Record<string, string[]> = {
  'lf-chat': ['lf-chat-event'],
  'lf-select': ['lf-select-event'],
  'lf-textfield': ['lf-textfield-event'],
  'lf-toggle': ['lf-toggle-event'],
  'lf-upload': ['lf-upload-event', RETAINED_UPLOAD_EVENT],
};

/** Watch supported LF inputs and snapshot after their value-changing events. */
export const watchWorkflowSessionDraft = (
  store: WorkflowStore,
  workflowId: string,
  cells: WorkflowUICells,
  shouldCapture: () => boolean = () => true,
): (() => void) => {
  let queued = false;
  let disposed = false;

  const requestCapture = () => {
    if (disposed || !shouldCapture() || queued) {
      return;
    }
    queued = true;
    queueMicrotask(() => {
      queued = false;
      if (!disposed && shouldCapture()) {
        void captureWorkflowSessionDraft(store, workflowId, cells);
      }
    });
  };

  const listeners: Array<[HTMLElement, string, EventListener]> = [];
  for (const cell of cells || []) {
    for (const eventName of EVENTS_BY_TAG[cell.tagName.toLowerCase()] || []) {
      const listener: EventListener = (event) => {
        const eventType = (event as CustomEvent<{ eventType?: string }>).detail?.eventType;
        // Ignore lifecycle/noise events. Value events across LF controls use
        // this compact set; the retained-upload event intentionally has none.
        if (
          eventName !== RETAINED_UPLOAD_EVENT &&
          !['change', 'delete', 'input', 'update', 'upload'].includes(eventType || '')
        ) {
          return;
        }
        requestCapture();
      };
      cell.addEventListener(eventName, listener);
      listeners.push([cell, eventName, listener]);
    }
  }

  return () => {
    disposed = true;
    for (const [cell, eventName, listener] of listeners) {
      cell.removeEventListener(eventName, listener);
    }
  };
};
