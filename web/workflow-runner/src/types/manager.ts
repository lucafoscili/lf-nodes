import { WorkflowStatus } from './state';

//#region Manager
export interface WorkflowManager {
  runWorkflow: () => Promise<void>;
  setStatus: (status: WorkflowStatus, message?: string) => void;
  setWorkflow: (id: string) => void;
  toggleDebug: () => void;
  isDebugEnabled: () => boolean;
}
//#endregion
