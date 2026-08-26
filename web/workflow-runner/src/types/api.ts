import {
  LfComponentPropsFor,
  LfDataColumn,
  LfDataDataset,
  LfDataNode,
} from '@lf-widgets/foundations/dist';

//#region API
export interface WorkflowQueueStatus {
  pending: number;
  running: number;
}
export interface WorkflowAPIErrorOptions<T> {
  payload?: T;
  status?: number;
}
export interface WorkflowAPIResponse {
  message: string;
  payload: WorkflowAPIRunPayload;
  status: WorkflowRunStatus;
}
//#endregion

//#region Dataset
export type WorkflowLFNode = Omit<LfDataNode, 'children' | 'cells'>;
export type WorkflowReadinessStatus = 'ready' | 'warning' | 'setup_required';
export interface WorkflowReadinessIssue {
  code: string;
  message: string;
}
export interface WorkflowReadiness {
  status: WorkflowReadinessStatus;
  issues: WorkflowReadinessIssue[];
}
export interface WorkflowAPIItem extends WorkflowLFNode {
  children: [WorkflowAPIInputs?, WorkflowAPIOutputs?];
  category: string;
  collection?: string;
  origin?: 'shipped' | 'custom';
  readiness?: WorkflowReadiness;
}
export interface WorkflowAPIInputs extends WorkflowLFNode {
  cells: WorkflowCellsInputContainer;
  id: `${string}:${WorkflowCellInputId}s`;
}
export interface WorkflowAPIOutputs extends WorkflowLFNode {
  cells: WorkflowCellsOutputContainer;
  id: `${string}:${WorkflowCellOutputId}s`;
}
export interface WorkflowAPIDataset {
  columns?: Array<LfDataColumn>;
  nodes: Array<WorkflowAPIItem>;
}
//#endregion

//#region Cells
// Common
export interface WorkflowCellBase {
  id: string;
  nodeId: string;
  required?: boolean;
  title?: string;
  value?: string;
}
export type WorkflowCellInputId = 'input';
export type WorkflowCellOutputId = 'output';
export type WorkflowCellType = WorkflowCellInputId | WorkflowCellOutputId;

// Inputs
export interface WorkflowCellInput extends WorkflowCellBase {
  props?: Partial<
    LfComponentPropsFor<
      | 'LfButton'
      | 'LfChat'
      | 'LfCode'
      | 'LfMasonry'
      | 'LfSelect'
      | 'LfTextfield'
      | 'LfToggle'
      | 'LfUpload'
    >
  >;
  shape?: 'chat' | 'choice' | 'select' | 'textfield' | 'toggle' | 'upload';
}
export interface WorkflowCellsInputContainer {
  [index: string]: WorkflowCellInput;
}

// Outputs
export interface WorkflowCellOutput extends WorkflowNodeOutputs, WorkflowCellBase {
  props?: Partial<LfComponentPropsFor<'LfCode' | 'LfCompare' | 'LfMasonry'>>;
  shape?: 'code' | 'compare' | 'masonry';
}
export type ShapeToComponentNameMap = {
  button: 'LfButton';
  code: 'LfCode';
  compare: 'LfCompare';
  masonry: 'LfMasonry';
  textfield: 'LfTextfield';
  toggle: 'LfToggle';
  upload: 'LfUpload';
};
export type Shape = keyof ShapeToComponentNameMap;
export type WorkflowCellOutputItemFor<S extends Shape> = WorkflowCellOutput & {
  props?: Partial<LfComponentPropsFor<ShapeToComponentNameMap[S]>>;
  shape: S;
};
export type WorkflowCellOutputItem = WorkflowCellOutputItemFor<Shape>;
export interface WorkflowCellsOutputContainer {
  [index: string]: WorkflowCellOutputItemFor<Shape>;
}
//#endregion

//#region Nodes outputs
export interface WorkflowNodeOutputs
  extends DisplayJSONNodeOutputs,
    DisplayStringNodeOutputs,
    LoadMetadataNodeOutputs,
    SaveSVGNodeOutputs,
    SaveImageForCivitAINodeOutputs,
    StandardComfyNodeOutputs {}
export interface ComfyFileArtifact {
  filename: string;
  subfolder?: string;
  type?: string;
  url?: string;
  media_type?: string;
}
export interface StandardComfyNodeOutputs {
  '3d'?: ComfyFileArtifact[];
  animated?: boolean[];
  images?: ComfyFileArtifact[];
  audio?: ComfyFileArtifact[];
  audios?: ComfyFileArtifact[];
}
export interface DisplayJSONNodeOutputs {
  json: Record<string, unknown>;
}
export interface DisplayStringNodeOutputs {
  string: string;
}
export interface LoadMetadataNodeOutputs {
  metadata: Record<string, unknown>;
}
export interface SaveImageForCivitAINodeOutputs {
  civitai_metadata: string;
  dataset: LfDataDataset;
  file_names: string[];
}
export interface SaveSVGNodeOutputs {
  dataset: LfDataDataset;
  slot_map: Record<string, string>;
  svg: string;
}
//#endregion

//#region Results
export interface WorkflowNodeResultPayload {
  lf_output?: Array<WorkflowNodeOutputs>;
  [key: string]: unknown;
}
export type WorkflowNodeResults = Record<string, WorkflowNodeResultPayload>;
//#endregion

//#region Run
export interface WorkflowArtifactReference {
  schema: 'lf.workflow-artifact-ref.v1';
  sourceRunId: string;
  artifactId: string;
  filename: string;
}
export interface WorkflowOutputArtifact {
  schema: 'lf.workflow-artifact.v1';
  reference: WorkflowArtifactReference;
  filename: string;
  nodeId: string;
  mediaType?: string;
  available: boolean;
}
export interface WorkflowAPIRunPayload {
  detail: string;
  error?: {
    input?: string;
    message: string;
  };
  history: {
    outputs?: WorkflowNodeResults;
  };
  preferred_output?: string;
}
export interface WorkflowRunRequestPayload {
  workflowId: string;
  inputs: Record<string, unknown>;
  submissionId?: string;
  promptId?: string;
  extraData?: Record<string, unknown>;
}
export interface WorkflowRunResponse {
  idempotentReplay: boolean;
  runId: string;
  status: WorkflowSubmissionStatus;
  submissionId: string;
}
export interface WorkflowRunResultPayload {
  body: WorkflowAPIResponse;
  http_status: number;
}
export type WorkflowRunStatus =
  | 'pending'
  | 'running'
  | 'succeeded'
  | 'failed'
  | 'cancelled'
  | 'timeout';
export type WorkflowSubmissionStatus =
  | WorkflowRunStatus
  | 'accepted'
  | 'reconciling';
export interface WorkflowSubmissionSnapshot {
  cancel_requested: boolean;
  created_at: number;
  error?: string | null;
  owner_id?: string | null;
  run_id: string | null;
  status: WorkflowSubmissionStatus;
  submission_id: string;
  updated_at: number;
  workflow_id: string;
}
export interface WorkflowRunStatusResponse {
  created_at: number;
  error?: string | null;
  result: WorkflowRunResultPayload | null;
  run_id: string;
  status: WorkflowRunStatus;
  submission_id?: string | null;
  cancel_requested?: boolean;
}
export interface WorkflowRunPruneResponse {
  candidate_count: number;
  candidate_run_ids: string[];
  dry_run: boolean;
  removed_count: number;
  removed_run_ids: string[];
  skipped_changed: number;
  skipped_unknown: number;
}
//#endregion

//#region Upload
export interface WorkflowAPIUploadPayload {
  paths?: string[];
  error?: {
    message: string;
  };
}
export interface WorkflowAPIUploadResponse {
  payload: WorkflowAPIUploadPayload;
}
//#endregion
