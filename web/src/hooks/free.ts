import { beforeFree } from '../api/models';
import {
  FreeMemoryFn,
  InstallFreeHookOptions,
  InstallFreeHookResult,
  PatchedFreeMemoryFn,
} from '../types/hooks/free';
import { LogSeverity } from '../types/manager/manager';
import { isFreeHookAPI, LFFreeFlags } from '../utils/common';

export function installLFBeforeFreeHooks(
  api: unknown,
  opts: InstallFreeHookOptions = {},
): InstallFreeHookResult {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {});

  if (!isFreeHookAPI(api)) {
    logger('"api" object not available; cannot install free hooks yet', {}, LogSeverity.Warning);
    return { freeMemoryHook: false, fetchFallbackHook: false };
  }

  const wrap: (fn: FreeMemoryFn) => PatchedFreeMemoryFn =
    opts.freeWrapper ??
    ((fn: FreeMemoryFn): PatchedFreeMemoryFn =>
      async function (this: unknown, options: unknown) {
        await beforeFree(options);
        return fn.apply(this ?? api, [options]);
      });

  const installFreeMemory = (): boolean => {
    try {
      if (api[LFFreeFlags.PatchedFree] === true) return true;

      const current = api.freeMemory;
      if (typeof current === 'function') {
        api[LFFreeFlags.OriginalFreeRef] = current;
        api.freeMemory = wrap(current);
        api[LFFreeFlags.PatchedFree] = true;
        return true;
      }

      const desc = Object.getOwnPropertyDescriptor(api, 'freeMemory');
      if (!desc || desc.configurable) {
        let original: FreeMemoryFn | undefined;
        Object.defineProperty(api, 'freeMemory', {
          configurable: true,
          enumerable: true,
          get() {
            return original;
          },
          set(fn: FreeMemoryFn) {
            if (api[LFFreeFlags.PatchedFree] === true) {
              original = fn;
              return;
            }
            if (typeof fn === 'function') {
              api[LFFreeFlags.OriginalFreeRef] = fn;
              original = wrap(fn);
              api[LFFreeFlags.PatchedFree] = true;
            } else {
              original = fn;
            }
          },
        });
      }
      return false;
    } catch (e) {
      logger(
        'Failed to patch freeMemory; proceeding without LF cache clear hook',
        { e },
        LogSeverity.Warning,
      );
      return false;
    }
  };

  let freePatched = installFreeMemory();
  if (!freePatched) {
    let count = 0;
    const iv = setInterval(() => {
      count += 1;
      if (installFreeMemory() || api[LFFreeFlags.PatchedFree] === true || count > attempts) {
        clearInterval(iv);
      }
    }, intervalMs);
  }

  const installFetchFallback = (): boolean => {
    try {
      if (api[LFFreeFlags.PatchedFetch] === true) {
        return true;
      }

      const originalFetchApi = api.fetchApi;
      if (typeof originalFetchApi !== 'function') {
        return false;
      }

      api[LFFreeFlags.PatchedFetch] = true;
      api.fetchApi = async function (path: string, init?: RequestInit) {
        try {
          const url = typeof path === 'string' ? path : String(path ?? '');
          const isFree = url.endsWith('/free') || url.endsWith('/api/free');
          const isOur = url.includes('/lf-nodes/free');
          const method = (init?.method ?? 'GET').toUpperCase();
          if (isFree && !isOur && method === 'POST' && api[LFFreeFlags.InBeforeFree] !== true) {
            api[LFFreeFlags.InBeforeFree] = true;
            try {
              await beforeFree(init);
            } finally {
              api[LFFreeFlags.InBeforeFree] = false;
            }
          }
        } catch {}
        return originalFetchApi.apply(this ?? api, [path, init]);
      };
      return true;
    } catch (e) {
      logger(
        'Failed to patch api.fetchApi; proceeding without LF cache clear fallback',
        { e },
        LogSeverity.Warning,
      );
      return false;
    }
  };

  const fetchPatched = installFetchFallback();

  return { freeMemoryHook: freePatched, fetchFallbackHook: fetchPatched };
}
