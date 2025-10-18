import { beforeRefreshNodeDefs } from '../api/models';
import {
  InstallRefreshHookOptions,
  InstallRefreshHookResult,
  PatchedRefreshComboFn,
  RefreshComboFn,
  RefreshHookApp,
} from '../types/hooks/refresh';
import { LogSeverity } from '../types/manager/manager';
import { isRefreshHookApp, LFRefreshFlags } from '../utils/common';

export function installLFRefreshNodeHook(
  appObj: unknown,
  opts: InstallRefreshHookOptions = {},
): InstallRefreshHookResult {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {});

  if (!isRefreshHookApp(appObj)) {
    logger('"app" object not available; cannot install refresh hook yet', {}, LogSeverity.Warning);
    return { refreshHook: false };
  }

  const scopedApp = appObj as RefreshHookApp & Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any

  const wrap: ((original: RefreshComboFn) => PatchedRefreshComboFn) | undefined =
    opts.refreshWrapper;

  const makePatched = (fn: RefreshComboFn): PatchedRefreshComboFn => {
    const factory =
      wrap ??
      ((original: RefreshComboFn): PatchedRefreshComboFn =>
        async function patched(this: unknown, ...args: any[]) {
          if (scopedApp[LFRefreshFlags.InBeforeRefresh] === true) {
            return original.apply(this ?? scopedApp, args);
          }

          scopedApp[LFRefreshFlags.InBeforeRefresh] = true;
          try {
            await beforeRefreshNodeDefs(args?.[0]);
          } catch (error) {
            logger(
              'LF refresh hook failed before calling original function',
              { error },
              LogSeverity.Warning,
            );
          } finally {
            scopedApp[LFRefreshFlags.InBeforeRefresh] = false;
          }

          return original.apply(this ?? scopedApp, args);
        });

    return factory(fn);
  };

  const installRefresh = (): boolean => {
    try {
      if (scopedApp[LFRefreshFlags.PatchedRefresh] === true) {
        return true;
      }

      const current = scopedApp.refreshComboInNodes;
      if (typeof current === 'function') {
        scopedApp[LFRefreshFlags.OriginalRefreshRef] = current;
        scopedApp.refreshComboInNodes = makePatched(current) as RefreshComboFn;
        scopedApp[LFRefreshFlags.PatchedRefresh] = true;
        return true;
      }

      const descriptor = Object.getOwnPropertyDescriptor(scopedApp, 'refreshComboInNodes');
      if (!descriptor || descriptor.configurable) {
        let original: RefreshComboFn | undefined;
        Object.defineProperty(scopedApp, 'refreshComboInNodes', {
          configurable: true,
          enumerable: true,
          get() {
            return scopedApp[LFRefreshFlags.PatchedRefresh]
              ? original
              : scopedApp[LFRefreshFlags.OriginalRefreshRef] ?? original;
          },
          set(fn: RefreshComboFn) {
            if (typeof fn !== 'function') {
              original = fn;
              return;
            }

            scopedApp[LFRefreshFlags.OriginalRefreshRef] = fn;
            original = makePatched(fn);
            scopedApp[LFRefreshFlags.PatchedRefresh] = true;
          },
        });
      }

      return false;
    } catch (error) {
      logger(
        'Failed to patch refreshComboInNodes; proceeding without LF refresh hook',
        { error },
        LogSeverity.Warning,
      );
      return false;
    }
  };

  let patched = installRefresh();
  if (!patched) {
    let count = 0;
    const timer = setInterval(() => {
      count += 1;
      patched = installRefresh();
      if (patched || count > attempts) {
        clearInterval(timer);
      }
    }, intervalMs);
  }

  return { refreshHook: patched };
}
