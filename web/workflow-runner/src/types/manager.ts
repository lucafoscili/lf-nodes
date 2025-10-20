import { WorkflowStatus } from './section';

//#region Manager
export interface WorkflowManager {
  runWorkflow: () => Promise<void>;
  setStatus: (status: WorkflowStatus, message?: string) => void;
  setWorkflow: (id: string) => void;
}
//#endregion
