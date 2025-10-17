import { LfComponentTag } from '@lf-widgets/foundations/dist';
import { WorkflowStatus } from './state';

//#region API
export interface WorkflowAPIDefinition {
  id: string;
  label: string;
  description: string;
  fields: WorkflowAPIField[];
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
    outputs?: Record<string, unknown>;
  };
  preferred_output?: string;
}
export interface WorkflowAPIResponse {
  message: string;
  payload: WorkflowAPIRunPayload;
  status: WorkflowStatus;
}
// Dedicated upload API types (decoupled from run API)
export interface WorkflowAPIUploadPayload {
  detail: string;
  error?: {
    message: string;
  };
  // List of absolute paths for saved files
  paths?: string[];
}

export interface WorkflowAPIUploadResponse {
  message: string;
  payload: WorkflowAPIUploadPayload;
  status: WorkflowStatus;
}
//#endregion
