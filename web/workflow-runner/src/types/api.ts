import {
  LfComponentPropsFor,
  LfDataColumn,
  LfDataDataset,
  LfDataNode,
} from '@lf-widgets/foundations/dist';
import { WorkflowStatus } from './state';

//#region API
export interface WorkflowAPIErrorOptions<T> {
  payload?: T;
  status?: number;
}
export interface WorkflowAPIResponse {
  message: string;
  payload: WorkflowAPIRunPayload;
  status: WorkflowStatus;
}
//#endregion

//#region Dataset
export type WorkflowLFNode = Omit<LfDataNode, 'children' | 'cells'>;
export interface WorkflowAPIItem extends WorkflowLFNode {
  children: [WorkflowAPIInputs?, WorkflowAPIOutputs?];
  category: string;
}
export interface WorkflowAPIInputs extends WorkflowLFNode {
  cells: WorkflowCellsInputContainer;
  id: `${string}:inputs`;
}
export interface WorkflowAPIOutputs extends WorkflowLFNode {
  cells: WorkflowCellsOutputContainer;
  id: `${string}:outputs`;
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
  title?: string;
  value?: string;
}

// Inputs
export interface WorkflowCellInput extends WorkflowCellBase {
  props?: Partial<
    LfComponentPropsFor<
      'LfButton' | 'LfCode' | 'LfMasonry' | 'LfTextfield' | 'LfToggle' | 'LfUpload'
    >
  >;
  shape?: 'textfield' | 'toggle' | 'upload';
}
export interface WorkflowCellsInputContainer {
  [index: string]: WorkflowCellInput;
}

// Outputs
export interface WorkflowCellOutput extends WorkflowNodeOutputs, WorkflowCellBase {
  props?: Partial<LfComponentPropsFor<'LfCode' | 'LfMasonry'>>;
  shape?: 'code' | 'masonry';
}
export type ShapeToComponentNameMap = {
  button: 'LfButton';
  code: 'LfCode';
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
    LoadMetadataNodeOutputs,
    SaveSVGNodeOutputs,
    SaveImageForCivitAINodeOutputs {}
export interface DisplayJSONNodeOutputs {
  json: Record<string, unknown>;
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
  lf_output?: [
    {
      civitai_metadata?: string;
      file_names?: string[];
      dataset?: LfDataDataset;
      slot_map?: Record<string, string>;
      svg?: string;
    },
  ];
  [key: string]: unknown;
}
export type WorkflowNodeResults = Record<string, WorkflowNodeResultPayload>;
//#endregion

//#region Run
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
  promptId?: string;
  extraData?: Record<string, unknown>;
}
export interface WorkflowRunResultPayload {
  body: WorkflowAPIResponse;
  http_status: number;
}
export type WorkflowRunStatus = 'pending' | 'running' | 'succeeded' | 'failed' | 'cancelled';
export interface WorkflowRunStatusResponse {
  created_at: number;
  error?: string | null;
  result: WorkflowRunResultPayload | null;
  run_id: string;
  status: WorkflowRunStatus;
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
