import {
  WorkflowAPIUploadPayload,
  WorkflowAPIUploadResponse,
} from '../../types/workflow-runner/api';
import { isWorkflowAPIUploadPayload, isWorkflowAPIUploadResponse } from './validators';

//#region Helpers
const _returnErrorResponse = (
  message: string,
  payload: WorkflowAPIUploadPayload,
): WorkflowAPIUploadResponse => ({
  message,
  payload,
  status: 'error',
});

const _returnSuccessResponse = (
  message: string,
  payload: WorkflowAPIUploadPayload,
): WorkflowAPIUploadResponse => ({
  message,
  payload,
  status: 'ready',
});
//#endregion

//#region Public API
export const invokeUploadAPI = async (files: File[]): Promise<WorkflowAPIUploadResponse> => {
  try {
    const formData = new FormData();
    if (!files || files.length === 0) {
      const payload: WorkflowAPIUploadPayload = { detail: 'missing_file' };
      return _returnErrorResponse('Missing file to upload.', payload);
    }
    files.forEach((file) => formData.append('file', file));

    const response = await fetch(`/api/lf-nodes/upload`, {
      method: 'POST',
      body: formData,
    });

    const responseBody: unknown = await response.json();
    console.debug('invokeUploadAPI: response body', responseBody);

    // Validate the response shape strictly at runtime using validators.
    let payload: WorkflowAPIUploadPayload | undefined;
    if (isWorkflowAPIUploadResponse(responseBody)) {
      payload = responseBody.payload;
    } else if (isWorkflowAPIUploadPayload(responseBody)) {
      // Some older deployments might return the payload directly; accept that shape.
      payload = responseBody;
    } else {
      // Response doesn't match expected shapes — log and return an error-shaped payload.
      // eslint-disable-next-line no-console
      console.error('invokeUploadAPI: unexpected response shape from server', responseBody);
      const errPayload: WorkflowAPIUploadPayload = { detail: 'invalid_response_shape' };
      return _returnErrorResponse('Invalid response shape from upload API.', errPayload);
    }

    if (!response.ok) {
      const { detail, error } = payload || { detail: 'unknown', error: undefined };
      const message = `Upload failed: ${detail} (${error?.message || error})`;
      console.error(message, payload);
      return _returnErrorResponse(message, payload || { detail: String(response.status) });
    }

    return _returnSuccessResponse(
      'Upload completed successfully.',
      payload as WorkflowAPIUploadPayload,
    );
  } catch (error) {
    console.error('Error invoking run API:', error);
    const payload: WorkflowAPIUploadPayload = {
      detail: String((error as Error).message || error),
    };
    return _returnErrorResponse('Error invoking run API.', payload);
  }
};
//#endregion
