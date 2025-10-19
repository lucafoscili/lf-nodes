import { WorkflowState } from './state';

export interface WorkflowSectionController {
  mount: (state: WorkflowState) => void;
  render: (state: WorkflowState) => void;
  destroy: () => void;
}
export type WorkflowCellStatus = 'error' | '';
export interface WorkflowSectionHandle extends WorkflowSectionController {
  setCellStatus: (state: WorkflowState, id: string, status?: WorkflowCellStatus) => void;
}
