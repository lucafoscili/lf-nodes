import {
  LfCodeInterface,
  LfComponentTag,
  LfMasonryPropsInterface,
} from '@lf-widgets/foundations/dist';
import { WorkflowStatus } from './state';

//#region API
export interface WorkflowAPIResponse {
  message: string;
  payload: WorkflowAPIRunPayload;
  status: WorkflowStatus;
}
export interface WorkflowAPIDefinition {
  id: string;
  label: string;
  description: string;
  fields: WorkflowAPIField[];
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

// typed representation of the node `ui` payload
export interface LFCodeItem {
  _description?: string | string[];
  lfLanguage?: string;
  lfValue?: string;
}

export interface LFMasonryItem {
  _description?: string | string[];
  lfDataset?: {
    nodes?: Array<{
      title?: string;
      filename?: string;
      url?: string;
    }>;
  };
}

export interface WorkflowAPIUI {
  _description?: string | string[];
  lf_code?: LFCodeItem[];
  lf_masonry?: LFMasonryItem[];
}
export interface WorkflowAPIField {
  name: LfComponentTag;
  label: string;
  component: string;
  description?: string;
  required?: boolean;
  default?: unknown;
  extra?: Record<string, any>;
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
