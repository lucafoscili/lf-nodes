import { WorkflowState } from '../../types/workflow-runner/state';

export interface WorkflowSectionController {
  mount: (state: WorkflowState) => void;
  render: (state: WorkflowState) => void;
  destroy: () => void;
}
