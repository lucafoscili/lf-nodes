import runnerConfig from './runner.config.json';
import { WorkflowStatus } from './types/state';

//#region Constants
export const API_BASE = runnerConfig.apiBase;
export const API_ROUTE_PREFIX = runnerConfig.apiRoutePrefix;
export const API_ROOT = `${API_BASE}${API_ROUTE_PREFIX}`;

type ChatConfig = {
  useProxy?: boolean;
  provider?: 'openai' | 'gemini' | 'kobold' | string;
  path?: string; // optional custom path relative to API_ROOT
};

const CHAT_CFG: ChatConfig | undefined = runnerConfig.chat;

const ensureLeadingSlash = (p?: string) => (p ? (p.startsWith('/') ? p : `/${p}`) : undefined);

export const CHAT_ENDPOINT = CHAT_CFG?.useProxy
  ? `${API_ROOT}${ensureLeadingSlash(CHAT_CFG.path ?? `/proxy/${CHAT_CFG.provider ?? 'openai'}`)}`
  : '';
export const DEFAULT_STATUS_MESSAGES: Record<WorkflowStatus, string> = {
  idle: 'Ready.',
  running: 'Running...',
  error: 'An error occurred while running the workflow.',
};
export const DEFAULT_THEME = runnerConfig.theme ?? 'dark';
export const STATIC_ASSETS_PATH = runnerConfig.staticPaths.assets;
export const STATIC_WORKFLOW_RUNNER_PATH = runnerConfig.staticPaths.workflowRunner;
const DEFAULT_QUEUE_POLL_INTERVAL = 750;
export const POLLING_INTERVALS = {
  queue: runnerConfig.polling?.queueIntervalMs ?? DEFAULT_QUEUE_POLL_INTERVAL,
} as const;
//#endregion

//#region Helpers
export const buildApiUrl = (path: string): string =>
  `${API_ROOT}${path.startsWith('/') ? path : `/${path}`}`;

export const buildAssetsUrl = (origin: string = window.location.origin): string =>
  `${origin}${API_BASE}${
    STATIC_ASSETS_PATH.startsWith('/') ? STATIC_ASSETS_PATH : `/${STATIC_ASSETS_PATH}`
  }`;
//#endregion
