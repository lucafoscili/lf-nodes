import {
  ComfyRawQueueStatus,
  WorkflowAPIItem,
  WorkflowCellInputId,
  WorkflowCellsInputContainer,
  WorkflowCellsOutputContainer,
  WorkflowCellType,
  WorkflowRunStatusResponse,
} from './api';
import { WorkflowCellStatus } from './section';
import { WorkflowRoute, WorkflowRunEntry, WorkflowStore, WorkflowView } from './state';

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

//#region Polling
export interface WorkflowPollingController {
  beginRunPolling: (runId: string) => void;
  startQueuePolling: () => void;
  stopQueuePolling: () => void;
  stopRunPolling: () => void;
}
export interface WorkflowCreatePollingControllerOptions {
  fetchQueueStatus?: () => Promise<ComfyRawQueueStatus>;
  getRunStatus?: (runId: string) => Promise<WorkflowRunStatusResponse>;
  queueIntervalMs?: number;
  runIntervalMs?: number;
  runLifecycle: RunLifecycleController;
  store: WorkflowStore;
}
//#endregion

//#region Routing
export interface RoutingController {
  applyPendingRouteIfNeeded: () => void;
  destroy: () => void;
  getPendingRoute: () => WorkflowRoute | null;
  initialize: () => void;
  updateRouteFromState: (precomputed?: WorkflowRoute) => void;
}
export interface CreateRoutingControllerOptions {
  store: WorkflowStore;
}
//#endregion

//#region Run Lifecycle
export interface RunLifecycleController {
  handlePollingError: (error: unknown) => { shouldStopPolling: boolean };
  handleStatusResponse: (response: WorkflowRunStatusResponse) => { shouldStopPolling: boolean };
  updateProgress: (response: WorkflowRunStatusResponse) => void;
}
export interface CreateRunLifecycleOptions {
  setInputStatus?: (inputId: string, status: WorkflowCellStatus) => void;
  store: WorkflowStore;
}
//#endregion
