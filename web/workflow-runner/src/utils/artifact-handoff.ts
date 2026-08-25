import { changeView } from '../app/sections';
import {
  WorkflowAPIDataset,
  WorkflowCellInput,
  WorkflowOutputArtifact,
} from '../types/api';
import { WorkflowStore } from '../types/state';
import { WorkflowUploadPrefill } from './input-prefill';

export type { WorkflowOutputArtifact } from '../types/api';

export type WorkflowArtifactTarget = {
  workflowId: string;
  workflowName: string;
  inputId: string;
  inputName: string;
};

type PendingArtifactHandoff = {
  workflowId: string;
  inputs: Record<string, WorkflowUploadPrefill>;
};

const pendingHandoffs = new WeakMap<WorkflowStore, PendingArtifactHandoff>();

const acceptsArtifact = (cell: WorkflowCellInput, artifact: WorkflowOutputArtifact): boolean => {
  const html = (cell.props as { lfHtmlAttributes?: { accept?: unknown } } | undefined)
    ?.lfHtmlAttributes;
  const accept = typeof html?.accept === 'string' ? html.accept.trim().toLowerCase() : '';
  if (!accept) {
    return true;
  }
  const filename = artifact.filename.toLowerCase();
  const mediaType = (artifact.mediaType || '').toLowerCase();
  return accept.split(',').some((rawRule) => {
    const rule = rawRule.trim();
    if (!rule) {
      return false;
    }
    if (rule.startsWith('.')) {
      return filename.endsWith(rule);
    }
    if (rule.endsWith('/*')) {
      return mediaType.startsWith(rule.slice(0, -1));
    }
    return Boolean(mediaType) && mediaType === rule;
  });
};

export const listCompatibleArtifactTargets = (
  workflows: WorkflowAPIDataset,
  artifact: WorkflowOutputArtifact,
): WorkflowArtifactTarget[] => {
  if (!artifact.available) {
    return [];
  }
  const targets: WorkflowArtifactTarget[] = [];
  for (const workflow of workflows.nodes || []) {
    if (workflow.readiness?.status === 'setup_required') {
      continue;
    }
    const inputGroup = workflow.children?.find((child) => child?.id.endsWith(':inputs'));
    const cells = inputGroup?.cells || {};
    for (const inputId of Object.keys(cells)) {
      const cell = cells[inputId];
      if (!cell || cell.shape !== 'upload' || !acceptsArtifact(cell, artifact)) {
        continue;
      }
      targets.push({
        workflowId: workflow.id,
        workflowName: String(workflow.value || workflow.id),
        inputId,
        inputName: String(cell.value || cell.title || inputId),
      });
    }
  }
  return targets.sort((a, b) => {
    const workflowOrder = a.workflowName.localeCompare(b.workflowName);
    return workflowOrder || a.inputName.localeCompare(b.inputName);
  });
};

export const buildArtifactPrefill = (
  artifact: WorkflowOutputArtifact,
): WorkflowUploadPrefill => ({
  schema: 'lf.workflow-upload-prefill.v1',
  reference: { ...artifact.reference },
  names: [artifact.filename],
  available: artifact.available,
});

export const queueArtifactHandoff = (
  store: WorkflowStore,
  artifact: WorkflowOutputArtifact,
  target: WorkflowArtifactTarget,
): void => {
  if (!artifact.available || !target.workflowId || !target.inputId) {
    return;
  }
  pendingHandoffs.set(store, {
    workflowId: target.workflowId,
    inputs: { [target.inputId]: buildArtifactPrefill(artifact) },
  });

  const state = store.getState();
  if (state.current.id !== target.workflowId) {
    state.mutate.workflow(target.workflowId);
  }
  changeView(store, 'workflow', { clearResults: true });
};

export const consumeArtifactHandoff = (
  store: WorkflowStore,
  workflowId: string | null,
): Record<string, WorkflowUploadPrefill> | null => {
  const pending = pendingHandoffs.get(store);
  if (!pending || !workflowId || pending.workflowId !== workflowId) {
    return null;
  }
  pendingHandoffs.delete(store);
  return pending.inputs;
};
