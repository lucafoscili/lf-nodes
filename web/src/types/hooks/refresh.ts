import { LogSeverity } from '../../types/manager/manager';

export interface InstallRefreshHookOptions {
  /** Max retry attempts to patch a lazily defined app.refreshComboInNodes */
  attempts?: number;
  /** Polling interval (ms) between attempts */
  intervalMs?: number;
  /** Optional logger injected by caller (manager) */
  logger?: (message: string, args?: Record<string, unknown>, severity?: LogSeverity) => void;
  /** Override wrapper for tests */
  refreshWrapper?: (original: RefreshComboFn) => PatchedRefreshComboFn;
}

export interface InstallRefreshHookResult {
  /** Whether refreshComboInNodes patch was installed immediately */
  refreshHook: boolean;
}

export type RefreshComboFn = (...args: any[]) => any | Promise<any>;
export type PatchedRefreshComboFn = (this: any, ...args: any[]) => Promise<any>;

/** Shape we rely on from ComfyUI's frontend app object */
export interface RefreshHookApp {
  refreshComboInNodes?: RefreshComboFn;
  [key: string]: any; // eslint-disable-line @typescript-eslint/no-explicit-any
}
