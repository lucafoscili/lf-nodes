import type { WorkflowArtifactReference } from '../types/api';

export type InputPrefillCell = HTMLElement & {
  getHistory?: () => Promise<unknown>;
  setHistory?: (...args: any[]) => Promise<void> | void;
  setValue?: (...args: any[]) => Promise<void> | void;
  lfDataset?: {
    nodes?: InputPrefillNode[];
  };
  lfValue?: unknown;
};

export const RETAINED_UPLOAD_EVENT = 'lf-workflow-retained-upload-change';

type RetainedUploadEventDetail = {
  available: boolean;
  names: string[];
  retained: boolean;
};

export type WorkflowUploadReference = {
  schema: 'lf.workflow-upload-ref.v1';
  sourceRunId: string;
  inputId: string;
};

export type WorkflowUploadPrefill = {
  schema: 'lf.workflow-upload-prefill.v1';
  reference: WorkflowUploadReference | WorkflowArtifactReference;
  names: string[];
  available: boolean;
};

const retainedUploads = new WeakMap<InputPrefillCell, WorkflowUploadPrefill>();

type InputPrefillNode = {
  id: string;
  value?: string | number;
  workflowValue?: string | number;
  children?: InputPrefillNode[];
};

const findSelectNodeId = (
  nodes: InputPrefillNode[] | undefined,
  workflowValue: unknown,
): string | undefined => {
  let displayFallback: string | undefined;
  const visit = (items: InputPrefillNode[] | undefined): string | undefined => {
    for (const node of items || []) {
      if (node.workflowValue === workflowValue) {
        return node.id;
      }
      if (
        displayFallback === undefined &&
        (node.value === workflowValue || node.id === String(workflowValue))
      ) {
        displayFallback = node.id;
      }
      const childMatch = visit(node.children);
      if (childMatch) {
        return childMatch;
      }
    }
    return undefined;
  };

  return visit(nodes) ?? displayFallback;
};

const normalizeRetainedUpload = (
  cell: InputPrefillCell,
  value: unknown,
): WorkflowUploadPrefill | undefined => {
  if (
    !value ||
    typeof value !== 'object' ||
    Array.isArray(value) ||
    (value as { schema?: unknown }).schema !== 'lf.workflow-upload-prefill.v1'
  ) {
    return undefined;
  }
  const candidate = value as Partial<WorkflowUploadPrefill>;
  const reference = candidate.reference;
  const names = candidate.names;
  if (
    !reference ||
    typeof reference !== 'object' ||
    typeof reference.sourceRunId !== 'string' ||
    !reference.sourceRunId ||
    reference.sourceRunId.length > 256 ||
    !Array.isArray(names) ||
    names.length === 0 ||
    names.length > 64 ||
    names.some((name) => typeof name !== 'string' || !name.trim() || name.length > 255) ||
    typeof candidate.available !== 'boolean'
  ) {
    return undefined;
  }
  const normalizedReference: WorkflowUploadReference | WorkflowArtifactReference | undefined =
    reference.schema === 'lf.workflow-upload-ref.v1' &&
    typeof (reference as Partial<WorkflowUploadReference>).inputId === 'string' &&
    (reference as WorkflowUploadReference).inputId === cell.id
      ? {
          schema: 'lf.workflow-upload-ref.v1',
          sourceRunId: reference.sourceRunId,
          inputId: (reference as WorkflowUploadReference).inputId,
        }
      : reference.schema === 'lf.workflow-artifact-ref.v1' &&
          typeof (reference as Partial<WorkflowArtifactReference>).artifactId === 'string' &&
          /^[0-9a-f]{64}$/.test((reference as WorkflowArtifactReference).artifactId) &&
          typeof (reference as Partial<WorkflowArtifactReference>).filename === 'string' &&
          Boolean((reference as WorkflowArtifactReference).filename) &&
          (reference as WorkflowArtifactReference).filename.length <= 255 &&
          !/[\\/\0]/.test((reference as WorkflowArtifactReference).filename)
        ? {
            schema: 'lf.workflow-artifact-ref.v1',
            sourceRunId: reference.sourceRunId,
            artifactId: (reference as WorkflowArtifactReference).artifactId,
            filename: (reference as WorkflowArtifactReference).filename,
          }
        : undefined;
  if (!normalizedReference) {
    return undefined;
  }
  return {
    schema: 'lf.workflow-upload-prefill.v1',
    reference: normalizedReference,
    names: names.map((name) => name.trim()),
    available: candidate.available,
  };
};

const emitRetainedUploadChange = (
  cell: InputPrefillCell,
  detail: RetainedUploadEventDetail,
) => {
  cell.dispatchEvent(new CustomEvent<RetainedUploadEventDetail>(RETAINED_UPLOAD_EVENT, { detail }));
};

export const setRetainedUploadPrefill = (cell: InputPrefillCell, value: unknown): boolean => {
  const normalized = normalizeRetainedUpload(cell, value);
  if (normalized === undefined) {
    return false;
  }
  retainedUploads.set(cell, normalized);
  emitRetainedUploadChange(cell, {
    available: normalized.available,
    names: [...normalized.names],
    retained: true,
  });
  return true;
};

export const clearRetainedUploadPrefill = (cell: InputPrefillCell): void => {
  retainedUploads.delete(cell);
  emitRetainedUploadChange(cell, { available: false, names: [], retained: false });
};

export const getRetainedUploadPrefill = (
  cell: InputPrefillCell,
): WorkflowUploadPrefill | undefined => {
  const retained = retainedUploads.get(cell);
  return retained
    ? {
        ...retained,
        reference: { ...retained.reference },
        names: [...retained.names],
      }
    : undefined;
};

/** Restore replayable controls and retain server-backed uploads from a prior run. */
export const applyInputPrefill = async (
  cells: InputPrefillCell[],
  inputs: Record<string, unknown>,
): Promise<void> => {
  for (const cell of cells) {
    const id = cell.id;
    if (!id || !Object.prototype.hasOwnProperty.call(inputs, id)) {
      continue;
    }

    const value = inputs[id];
    try {
      switch (cell.tagName.toLowerCase()) {
        case 'lf-upload': {
          setRetainedUploadPrefill(cell, value);
          continue;
        }
        case 'lf-chat': {
          const history = typeof value === 'string' ? value : JSON.stringify(value ?? []);
          if (typeof cell.setHistory === 'function') {
            await cell.setHistory(history);
          }
          break;
        }
        case 'lf-select': {
          // Runs store the semantic workflowValue, while lf-select restores by
          // its UI node id. Resolve the current definition so friendly option
          // ids may evolve independently from the submitted value.
          const selectedId = findSelectNodeId(cell.lfDataset?.nodes, value) ?? String(value ?? '');
          if (typeof cell.setValue === 'function') {
            await cell.setValue(selectedId);
          } else {
            cell.lfValue = selectedId;
          }
          break;
        }
        case 'lf-toggle': {
          const enabled = value === true || value === 'on' || value === 1;
          if (typeof cell.setValue === 'function') {
            await cell.setValue(enabled ? 'on' : 'off');
          } else {
            cell.lfValue = enabled;
          }
          break;
        }
        default: {
          const text = value === null || value === undefined ? '' : String(value);
          if (typeof cell.setValue === 'function') {
            await cell.setValue(text);
          } else {
            cell.lfValue = text;
          }
        }
      }
    } catch {
      // A retired/malformed input must not prevent the rest of the form from
      // being restored. The normal form defaults remain available to the user.
    }
  }
};
