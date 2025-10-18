import { WorkflowState } from '../types/state';

export interface WorkflowSectionController {
  mount: (state: WorkflowState) => void;
  render: (state: WorkflowState) => void;
  destroy: () => void;
}
