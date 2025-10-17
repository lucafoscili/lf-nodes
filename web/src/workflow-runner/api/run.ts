import { WorkflowAPIResponse, WorkflowAPIRunPayload } from '../../types/workflow-runner/state';

//#region Helpers
const _returnErrorResponse = (
  message: string,
  payload: WorkflowAPIRunPayload,
): WorkflowAPIResponse => ({
  message,
  payload,
  status: 'error',
});

const _returnSuccessResponse = (
  message: string,
  payload: WorkflowAPIRunPayload,
): WorkflowAPIResponse => ({
  message,
  payload,
  status: 'ready',
});
//#endregion

//#region Public API
export const invokeRunAPI = async (
  id: string,
  inputs: Record<string, unknown>,
): Promise<WorkflowAPIResponse> => {
  try {
    const response = await fetch(`/api/lf-nodes/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workflowId: id, inputs }),
    });

    const responseBody: WorkflowAPIResponse = await response.json();
    const payload: WorkflowAPIRunPayload = responseBody.payload;

    if (!response.ok) {
      const { detail, error } = payload;
      const message = `Workflow execution failed: ${detail} (${error?.message || error})`;
      console.error(message, payload);
      return _returnErrorResponse(message, payload);
    }

    return _returnSuccessResponse('Workflow executed successfully.', payload);
  } catch (error) {
    console.error('Error invoking run API:', error);
    const payload: WorkflowAPIRunPayload = {
      detail: String((error as Error).message || error),
      history: {},
    };
    return _returnErrorResponse('Error invoking run API.', payload);
  }
};
//#endregion
