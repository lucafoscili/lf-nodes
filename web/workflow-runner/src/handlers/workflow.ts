import { LfButtonEventPayload } from '@lf-widgets/foundations/dist';
import { fetchWorkflowJSON, WorkflowApiError } from '../services/workflow-service';
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
export const openWorkflowInComfyUI = async (
  e: CustomEvent<LfButtonEventPayload>,
  store: WorkflowStore,
) => {
  const { eventType } = e.detail;

  const { current, manager } = store.getState();
  const { id } = current;

  switch (eventType) {
    case 'click':
      if (!id) {
        manager.setStatus('error', 'No workflow selected');
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
          manager.setStatus('error', `Failed to fetch workflow: ${error.message}`);
        } else {
          manager.setStatus('error', 'Unexpected error while fetching workflow');
        }
      }

      break;
    default:
      return;
  }
};
//#endregion
