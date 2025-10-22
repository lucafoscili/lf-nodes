import { WorkflowState } from './state';

//#region Workflow
export type WorkflowUICell =
  | HTMLLfButtonElement
  | HTMLLfTextfieldElement
  | HTMLLfToggleElement
  | HTMLLfUploadElement;
export type WorkflowUICells = Array<WorkflowUICell>;
export type WorkflowCellStatus = 'error' | '';
export interface WorkflowSectionController {
  destroy: () => void;
  mount: (state: WorkflowState) => void;
  render: (state: WorkflowState) => void;
}
export interface WorkflowSectionHandle extends WorkflowSectionController {
  setCellStatus: (state: WorkflowState, id: string, status?: WorkflowCellStatus) => void;
}
//#endregion
