import { LfComponentTag } from '@lf-widgets/foundations/dist';

//#region Manager
export interface WorkflowRunnerManager {
  runWorkflow: () => Promise<void>;
  setStatus: (status: WorkflowStatus, message?: string) => void;
  setWorkflow: (id: string) => Promise<void>;
}
//#endregion

//#region State
export type WorkflowStatus = 'ready' | 'running' | 'error';
export interface WorkflowCurrent {
  status: WorkflowStatus;
  workflow: WorkflowAPIDefinition['id'] | null;
}
export interface WorkflowUI {
  layout: {
    _root: HTMLDivElement | null;
    drawer: { _root: HTMLLfDrawerElement | null };
    header: {
      _root: HTMLLfHeaderElement | null;
      drawerToggle: HTMLLfButtonElement | null;
      themeSwitch: HTMLLfButtonElement | null;
    };
    main: {
      _root: HTMLElement | null;
      title: {
        _root: HTMLElement | null;
      };
      workflow: {
        _root: HTMLElement | null;
        fields: Array<
          HTMLLfButtonElement | HTMLLfTextfieldElement | HTMLLfToggleElement | HTMLLfUploadElement
        >;
        options: HTMLDivElement | null;
        result: HTMLElement | null;
        run: HTMLLfButtonElement | null;
        status: HTMLElement | null;
        title: HTMLElement | null;
      };
    };
  };
}
export interface WorkflowState {
  current: WorkflowCurrent;
  manager: WorkflowRunnerManager;
  ui: WorkflowUI;
  workflows: WorkflowAPIDefinition[];
}
//#endregion

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
//#endregion
