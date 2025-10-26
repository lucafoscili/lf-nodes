import { LfButtonEventPayload } from '@lf-widgets/foundations/dist';
import { fetchWorkflowJSON, WorkflowApiError } from '../services/workflow-service';
import { WorkflowStore } from '../types/state';
import { STATUS_MESSAGES } from '../utils/constants';

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
  const { NO_WORKFLOW_SELECTED } = STATUS_MESSAGES;

  const { eventType } = e.detail;

  const state = store.getState();
  const { current, manager } = state;
  const { id } = current;

  switch (eventType) {
    case 'click':
      if (!id) {
        state.mutate.status('error', NO_WORKFLOW_SELECTED);
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
        if (error instanceof WorkflowApiError) {
          state.mutate.status('error', `Failed to fetch workflow: ${error.message}`);
        } else {
          state.mutate.status('error', 'Unexpected error while fetching workflow');
        }
      }

      break;
    default:
      return;
  }
};
//#endregion
