import { LfCodeInterface, LfMasonryPropsInterface } from '@lf-widgets/foundations/dist';
import { WorkflowStatus } from './section';

//#region API
export interface LFCodeItem extends LfCodeInterface {
  _description?: string | string[];
}
export interface LFMasonryItem extends LfMasonryPropsInterface {
  _description?: string | string[];
  _slotmap?: Record<string, string>;
}
export interface WorkflowAPIErrorOptions<TPayload> {
  payload?: TPayload;
  status?: number;
}
export interface WorkflowAPIResponse {
  message: string;
  payload: WorkflowAPIRunPayload;
  status: WorkflowStatus;
}
//#endregion

//#region Run
export interface WorkflowNodeOutputProps {
  _slotmap?: Record<string, string>;
  [key: string]: unknown;
}
export interface WorkflowNodeOutputItem {
  id?: string;
  nodeId?: string;
  shape: string;
  title?: string;
  props?: WorkflowNodeOutputProps;
}
export interface WorkflowNodeOutputPayload {
  lf_output?: WorkflowNodeOutputItem[] | WorkflowNodeOutputItem;
  [key: string]: unknown;
}
export type WorkflowNodeOutputs = Record<string, WorkflowNodeOutputPayload>;

export interface WorkflowAPIRunPayload {
  detail: string;
  error?: {
    input?: string;
    message: string;
  };
  history: {
    outputs?: WorkflowNodeOutputs;
  };
}
export interface WorkflowAPIRunResult extends WorkflowAPIResponse {
  status: Extract<WorkflowStatus, 'ready' | 'error'>;
  payload: WorkflowAPIRunPayload;
}
//#endregion

//#region Upload
export interface WorkflowAPIUploadPayload {
  detail: string;
  error?: {
    message: string;
  };
  paths?: string[];
}
export interface WorkflowAPIUploadResponse {
  message: string;
  payload: WorkflowAPIUploadPayload;
  status: WorkflowStatus;
}
//#endregion
