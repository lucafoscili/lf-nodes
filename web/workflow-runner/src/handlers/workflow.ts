import { LfButtonEventPayload } from '@lf-widgets/foundations/dist';
import { WorkflowStore } from '../types/state';

//#region Button Handlers
export const executeWorkflow = (e: CustomEvent<LfButtonEventPayload>, store: WorkflowStore) => {
  const { eventType } = e.detail;

  const { manager } = store.getState();

  switch (eventType) {
    case 'click':
      manager.getDispatchers().runWorkflow();
      break;
    default:
      return;
  }
};
//#endregion
