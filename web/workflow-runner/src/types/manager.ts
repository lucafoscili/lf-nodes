import {
  WorkflowAPIItem,
  WorkflowCellInputId,
  WorkflowCellsInputContainer,
  WorkflowCellsOutputContainer,
  WorkflowCellType,
} from './api';
import { WorkflowRunEntry, WorkflowStore, WorkflowView } from './state';

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
  runs: {
    all: () => WorkflowRunEntry[];
    get: (runId: string) => WorkflowRunEntry | null;
    select: (runId: string | null, view?: WorkflowView) => void;
    selected: () => WorkflowRunEntry | null;
  };
  workflow: {
    cells: <T extends WorkflowCellType>(
      type: T,
    ) => T extends WorkflowCellInputId ? WorkflowCellsInputContainer : WorkflowCellsOutputContainer;
    current: () => WorkflowAPIItem;
    description: () => string;
    title: () => string;
  };
}
//#endregion
