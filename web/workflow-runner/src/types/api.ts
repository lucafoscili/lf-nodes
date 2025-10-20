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
export type WorkflowAPIResult = {
  [K in WorkflowAPIResultKey]?: K extends '_description'
    ? string | string[]
    : K extends 'code'
    ? Partial<LfCodeInterface> & {
        _description?: string | string[];
      }
    : K extends 'masonry'
    ? Partial<LfMasonryPropsInterface> & {
        _description?: string | string[];
        _slotmap?: Record<string, string>;
      }
    : never;
};
export type WorkflowAPIResultKey = '_description' | 'code' | 'masonry';
export interface WorkflowAPIUI {
  _description?: string | string[];
  lf_code?: LFCodeItem[];
  lf_masonry?: LFMasonryItem[];
}
//#endregion

//#region Run
export interface WorkflowAPIRunPayload {
  detail: string;
  error?: {
    input?: string;
    message: string;
  };
  history: {
    outputs?: WorkflowAPIUI;
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
