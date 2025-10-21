import { WorkflowState } from './state';

//#region Workflow
export type WorkflowCell =
  | HTMLLfButtonElement
  | HTMLLfTextfieldElement
  | HTMLLfToggleElement
  | HTMLLfUploadElement;
export type WorkflowCells = Array<WorkflowCell>;
export type WorkflowCellStatus = 'error' | '';
export interface WorkflowSectionController {
  mount: (state: WorkflowState) => void;
  render: (state: WorkflowState) => void;
  destroy: () => void;
}
export interface WorkflowSectionHandle extends WorkflowSectionController {
  setCellStatus: (state: WorkflowState, id: string, status?: WorkflowCellStatus) => void;
}
//#endregion
