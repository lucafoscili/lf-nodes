import { LfButtonEventPayload } from '@lf-widgets/foundations/dist';
import { fetchWorkflowJSON, WorkflowApiError } from '../services/workflow-service';
import { WorkflowStore } from '../types/state';
import { NOTIFICATION_MESSAGES, STATUS_MESSAGES } from '../utils/constants';

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
export const openWorkflowInComfyUI = async (
  e: CustomEvent<LfButtonEventPayload>,
  store: WorkflowStore,
) => {
  const { NO_WORKFLOW_SELECTED } = NOTIFICATION_MESSAGES;
  const { ERROR_FETCHING_WORKFLOWS } = STATUS_MESSAGES;

  const { eventType } = e.detail;

  const state = store.getState();
  const { current } = state;
  const { id } = current;

  switch (eventType) {
    case 'click':
      if (!id) {
        state.mutate.notifications.add({
          id: performance.now().toString(),
          message: NO_WORKFLOW_SELECTED,
          status: 'warning',
        });
        return;
      }

      try {
        const workflowJSON = await fetchWorkflowJSON(id);

        const workflowString = JSON.stringify(workflowJSON, null, 2);
        const blob = new Blob([workflowString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${id}.json`;
        document.body.appendChild(a);
        a.click();

        setTimeout(() => {
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }, 1000);
      } catch (error) {
        state.mutate.status('error', ERROR_FETCHING_WORKFLOWS);
        if (error instanceof WorkflowApiError) {
          state.mutate.notifications.add({
            id: performance.now().toString(),
            message: `Failed to fetch workflow: ${error.message}`,
            status: 'danger',
          });
        }
      }

      break;
    default:
      return;
  }
};
//#endregion
