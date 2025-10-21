import runnerConfig from './runner.config.json';
import { WorkflowStatus } from './types/state';

//#region Constants
export const API_BASE = runnerConfig.apiBase;
export const API_ROUTE_PREFIX = runnerConfig.apiRoutePrefix;
export const API_ROOT = `${API_BASE}${API_ROUTE_PREFIX}`;
export const DEFAULT_STATUS_MESSAGES: Record<WorkflowStatus, string> = {
  ready: 'Ready.',
  running: 'Running...',
  error: 'An error occurred while running the workflow.',
};
export const DEFAULT_THEME = runnerConfig.theme ?? 'dark';
export const STATIC_ASSETS_PATH = runnerConfig.staticPaths.assets;
export const STATIC_WORKFLOW_RUNNER_PATH = runnerConfig.staticPaths.workflowRunner;
//#endregion

//#region Helpers
export const buildApiUrl = (path: string): string =>
  `${API_ROOT}${path.startsWith('/') ? path : `/${path}`}`;

export const buildAssetsUrl = (origin: string = window.location.origin): string =>
  `${origin}${API_BASE}${
    STATIC_ASSETS_PATH.startsWith('/') ? STATIC_ASSETS_PATH : `/${STATIC_ASSETS_PATH}`
  }`;
//#endregion
