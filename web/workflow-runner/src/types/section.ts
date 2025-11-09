import { WorkflowRoute, WorkflowState, WorkflowStore, WorkflowView } from './state';

//#region View types
export type WorkflowMainSections = 'home' | 'inputs' | 'outputs' | 'results';
export type WorkflowUICell =
  | HTMLLfButtonElement
  | HTMLLfChatElement
  | HTMLLfTextfieldElement
  | HTMLLfToggleElement
  | HTMLLfUploadElement;
export type WorkflowUICells = Array<WorkflowUICell>;
export type WorkflowCellStatus = 'error' | '';
export interface WorkflowSectionController {
  destroy: () => void;
  mount: () => void;
  render: (scope?: WorkflowMainSections[]) => void;
}
export type SectionsResolver = (state: WorkflowState) => WorkflowMainSections[];
export type RouteBuilder = (state: WorkflowState) => WorkflowRoute;
export interface ChangeViewOptions {
  runId?: string | null;
  clearResults?: boolean;
}
export interface ViewDefinition {
  sections: SectionsResolver;
  toRoute: RouteBuilder;
  enter: (store: WorkflowStore, options: ChangeViewOptions) => WorkflowView;
}
//#endregion
