import { WorkflowStatus } from './state';

//#region Manager
export interface WorkflowRunnerManager {
  runWorkflow: () => Promise<void>;
  setStatus: (status: WorkflowStatus, message?: string) => void;
  setWorkflow: (id: string) => void;
}
//#endregion
