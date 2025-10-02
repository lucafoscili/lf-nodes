import { LogSeverity } from '../../types/manager/manager';

export interface InstallInterruptHookOptions {
  /** Max retry attempts to patch a lazily defined api.interrupt */
  attempts?: number;
  /** Polling interval (ms) between attempts */
  intervalMs?: number;
  /** Optional logger injected by caller (manager) */
  logger?: (message: string, args?: Record<string, unknown>, severity?: LogSeverity) => void;
  /** Override wrapper for tests */
  interruptWrapper?: (original: InterruptFn) => PatchedInterruptFn;
}

export interface InstallInterruptHookResult {
  /** Whether interrupt patch (or interception) was installed immediately */
  interruptHook: boolean;
}

export type InterruptFn = (...args: any[]) => any | Promise<any>;
export type PatchedInterruptFn = (this: any, ...args: any[]) => Promise<any>;

/** Shape we rely on from ComfyUI's frontend api object */
export interface InterruptHookAPI {
  interrupt?: InterruptFn;
  [key: string]: any; // eslint-disable-line @typescript-eslint/no-explicit-any
}
