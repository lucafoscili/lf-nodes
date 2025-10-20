import { LfButtonEventPayload } from '@lf-widgets/foundations/dist';
import { WorkflowState } from '../types/state';

export const executeWorkflowButton = (
  e: CustomEvent<LfButtonEventPayload>,
  state: WorkflowState,
) => {
  const { eventType } = e.detail;

  switch (eventType) {
    case 'click':
      state.manager?.runWorkflow();
      break;
    default:
      return;
  }
};
