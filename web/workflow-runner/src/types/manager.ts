import { WorkflowStore } from './state';

//#region Dispatchers
export type WorkflowDispatcher = () => Promise<void>;
export interface WorkflowDispatchers {
  runWorkflow: WorkflowDispatcher;
}
//#endregion

//#region Manager
export type WorkflowUIItem = HTMLElement | HTMLElement[];
export interface WorkflowManager {
  getAppRoot: () => HTMLDivElement;
  getDispatchers: () => WorkflowDispatchers;
  getStore: () => WorkflowStore;
  uiRegistry: {
    delete: () => void;
    get: () => WeakMap<WeakKey, WorkflowUIItem>;
    remove: (elementId: string) => void;
    set: (elementId: string, element: WorkflowUIItem) => void;
  };
}
//#endregion
