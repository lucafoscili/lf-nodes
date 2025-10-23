import { LfButtonEventPayload } from '@lf-widgets/foundations/dist';
import { WorkflowState } from '../types/state';

//#region Button Handlers
export const executeWorkflow = (e: CustomEvent<LfButtonEventPayload>, state: WorkflowState) => {
  const { eventType } = e.detail;

  const { manager } = state;

  switch (eventType) {
    case 'click':
      manager.getDispatchers().runWorkflow();
      break;
    default:
      return;
  }
};
//#endregion
