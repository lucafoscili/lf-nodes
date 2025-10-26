//#region Workflow
export type UnescapeJSONPayload = {
  validJson: boolean;
  parsedJson?: {};
  unescapedStr: string;
};
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
//#endregion
