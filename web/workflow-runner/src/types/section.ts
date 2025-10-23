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
  mount: () => void;
  render: () => void;
}
export interface WorkflowSectionHandle extends WorkflowSectionController {
  setCellStatus: (id: string, status?: WorkflowCellStatus) => void;
}
//#endregion
