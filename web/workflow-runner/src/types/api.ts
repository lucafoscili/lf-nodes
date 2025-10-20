import { LfCodeInterface, LfMasonryPropsInterface } from '@lf-widgets/foundations/dist';
import { WorkflowStatus } from './state';

//#region API
export interface RunWorkflowResult extends WorkflowAPIResponse {
  status: Extract<WorkflowStatus, 'ready' | 'error'>;
  payload: WorkflowAPIRunPayload;
}

export interface WorkflowAPIResponse {
  message: string;
  payload: WorkflowAPIRunPayload;
  status: WorkflowStatus;
}
export type WorkflowAPIResultKey = '_description' | 'code' | 'masonry';
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
export interface WorkflowAPIErrorOptions<TPayload> {
  payload?: TPayload;
  status?: number;
}
export interface LFCodeItem extends LfCodeInterface {
  _description?: string | string[];
}

export interface LFMasonryItem extends LfMasonryPropsInterface {
  _description?: string | string[];
  _slotmap?: Record<string, string>;
}

export interface WorkflowAPIUI {
  _description?: string | string[];
  lf_code?: LFCodeItem[];
  lf_masonry?: LFMasonryItem[];
}
export interface WorkflowAPIRunPayload {
  detail: string;
  error?: {
    input?: string;
    message: string;
  };
  history: {
    outputs?: WorkflowAPIUI;
  };
  preferred_output?: string;
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
