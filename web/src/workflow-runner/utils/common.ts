import { WorkflowState } from '../../types/workflow-runner/state';
import { invokeUploadAPI } from '../api/upload';
import { workflowSection } from '../elements/main.workflow';

//#region Upload
export const handleUploadField = async (
  state: WorkflowState,
  fieldName: string,
  files: File[],
): Promise<string[]> => {
  const { manager } = state;

  manager.setStatus('running', 'Uploading file…');

  const response = await invokeUploadAPI(files);

  if (!response || response.status !== 'ready') {
    workflowSection.update.fieldWrapper(state, fieldName, 'error');
    manager.setStatus('error', `Upload failed: ${response?.payload?.detail ?? 'unknown error'}`);
    throw new Error(response?.payload?.detail || 'Upload failed');
  }

  const paths = response.payload?.paths || [];

  manager.setStatus('running', 'File uploaded, processing...');

  return paths;
};
//#endregion
