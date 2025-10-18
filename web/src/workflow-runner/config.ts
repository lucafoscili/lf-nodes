import { WorkflowStatus } from '../types/workflow-runner/state';

export const API_BASE = '/api';
export const API_ROUTE_PREFIX = '/lf-nodes';
export const API_ROOT = `${API_BASE}${API_ROUTE_PREFIX}`;
export const STATIC_ASSETS_PATH = `${API_ROUTE_PREFIX}/static/assets/`;
export const DEFAULT_THEME = 'dark';

export const DEFAULT_STATUS_MESSAGES: Record<WorkflowStatus, string> = {
  ready: 'Ready.',
  running: 'Running...',
  error: 'An error occurred while running the workflow.',
};

export const buildApiUrl = (path: string): string =>
  `${API_ROOT}${path.startsWith('/') ? path : `/${path}`}`;

export const buildAssetsUrl = (origin: string = window.location.origin): string =>
  `${origin}${API_BASE}${STATIC_ASSETS_PATH}`;
