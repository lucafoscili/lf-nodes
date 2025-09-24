import { LogSeverity } from '../../types/manager/manager';

export interface InstallFreeHookOptions {
  /** Max retry attempts to patch a lazily defined api.freeMemory */
  attempts?: number;
  /** Polling interval (ms) between attempts */
  intervalMs?: number;
  /** Optional logger injected by caller (manager) */
  logger?: (message: string, args?: Record<string, unknown>, severity?: LogSeverity) => void;
  /** Override wrapper for tests */
  freeWrapper?: (original: FreeMemoryFn) => PatchedFreeMemoryFn;
}

export interface InstallFreeHookResult {
  /** Whether freeMemory patch (or interception) was installed immediately */
  freeMemoryHook: boolean;
  /** Whether fetchApi fallback interception was installed */
  fetchFallbackHook: boolean;
}

export type FreeMemoryFn = (options?: any) => any | Promise<any>;
export type PatchedFreeMemoryFn = (this: any, options: any) => Promise<any>;
export type FetchApiFn = (path: string, init?: RequestInit) => Promise<Response> | Response;

/** Shape we rely on from ComfyUI's frontend api object */
export interface FreeHookAPI {
  freeMemory?: FreeMemoryFn;
  fetchApi?: FetchApiFn;
  // Dynamic flags & any additional members we don't explicitly enumerate
  [key: string]: any; // eslint-disable-line @typescript-eslint/no-explicit-any
}
