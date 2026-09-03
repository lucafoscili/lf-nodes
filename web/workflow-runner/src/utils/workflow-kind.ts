import {
  WorkflowAPIDataset,
  WorkflowAPIItem,
  WorkflowAPIKind,
  WorkflowAPIWireKind,
} from '../types/api';

type WorkflowKindSource = Pick<WorkflowAPIItem, 'kind'> | null | undefined;

/**
 * Translate every supported catalogue spelling into the Runner's canonical
 * block/orchestra vocabulary. Unknown and missing values remain backward
 * compatible blocks.
 */
export const normalizeWorkflowKind = (
  kind: WorkflowAPIWireKind | string | null | undefined,
): WorkflowAPIKind => (kind === 'orchestra' || kind === 'sequence' ? 'orchestra' : 'block');

export const isWorkflowOrchestra = (workflow: WorkflowKindSource): boolean =>
  normalizeWorkflowKind(workflow?.kind) === 'orchestra';

export const normalizeWorkflowDatasetKinds = (
  dataset: WorkflowAPIDataset,
): WorkflowAPIDataset => ({
  ...dataset,
  nodes: dataset.nodes.map((node) => ({
    ...node,
    kind: normalizeWorkflowKind(node.kind),
  })),
});
