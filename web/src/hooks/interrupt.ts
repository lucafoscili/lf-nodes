import { handleInterruptForState } from '../helpers/imageEditor';
import {
  InstallInterruptHookOptions,
  InstallInterruptHookResult,
  InterruptFn,
  InterruptHookAPI,
  PatchedInterruptFn,
} from '../types/hooks/interrupt';
import { LogSeverity } from '../types/manager/manager';
import { isInterruptHookAPI, LFInterruptFlags } from '../utils/common';
import { IMAGE_EDITOR_INSTANCES } from '../widgets/imageEditor';

export function installLFInterruptHook(
  apiObj: unknown,
  opts: InstallInterruptHookOptions = {},
): InstallInterruptHookResult {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {});

  if (!isInterruptHookAPI(apiObj)) {
    logger(
      '"api" object not available; cannot install interrupt hook yet',
      {},
      LogSeverity.Warning,
    );
    return { interruptHook: false };
  }

  const scopedApi = apiObj as InterruptHookAPI & Record<string, unknown>;

  const wrap: ((fn: InterruptFn) => PatchedInterruptFn) | undefined = opts.interruptWrapper;

  const makePatched = (fn: InterruptFn): PatchedInterruptFn => {
    const factory =
      wrap ??
      ((original: InterruptFn): PatchedInterruptFn =>
        async function patched(this: unknown, ...args: any[]) {
          if (scopedApi[LFInterruptFlags.InBeforeInterrupt] === true) {
            return original.apply(this ?? scopedApi, args);
          }

          scopedApi[LFInterruptFlags.InBeforeInterrupt] = true;
          try {
            const result = await original.apply(this ?? scopedApi, args);

            for (const state of IMAGE_EDITOR_INSTANCES) {
              try {
                await handleInterruptForState(state);
              } catch (error) {
                logger(
                  'LF interrupt hook failed while applying image editor cleanup.',
                  { error },
                  LogSeverity.Warning,
                );
              }
            }

            return result;
          } finally {
            scopedApi[LFInterruptFlags.InBeforeInterrupt] = false;
          }
        });

    return factory(fn);
  };

  const installInterrupt = (): boolean => {
    try {
      if (scopedApi[LFInterruptFlags.PatchedInterrupt] === true) {
        return true;
      }

      const current = scopedApi.interrupt;
      if (typeof current === 'function') {
        scopedApi[LFInterruptFlags.OriginalInterruptRef] = current;
        scopedApi.interrupt = makePatched(current) as InterruptFn;
        scopedApi[LFInterruptFlags.PatchedInterrupt] = true;
        return true;
      }

      const descriptor = Object.getOwnPropertyDescriptor(scopedApi, 'interrupt');
      if (!descriptor || descriptor.configurable) {
        let original: InterruptFn | undefined;
        Object.defineProperty(scopedApi, 'interrupt', {
          configurable: true,
          enumerable: true,
          get() {
            return scopedApi[LFInterruptFlags.PatchedInterrupt]
              ? original
              : (scopedApi[LFInterruptFlags.OriginalInterruptRef] as InterruptFn) ?? original;
          },
          set(fn: InterruptFn) {
            if (typeof fn !== 'function') {
              original = fn;
              return;
            }

            scopedApi[LFInterruptFlags.OriginalInterruptRef] = fn;
            original = makePatched(fn);
            scopedApi[LFInterruptFlags.PatchedInterrupt] = true;
          },
        });
      }

      return false;
    } catch (error) {
      logger(
        'Failed to patch api.interrupt; proceeding without LF interrupt hook',
        { error },
        LogSeverity.Warning,
      );
      return false;
    }
  };

  let patched = installInterrupt();
  if (!patched) {
    let count = 0;
    const timer = setInterval(() => {
      count += 1;
      patched = installInterrupt();
      if (patched || count > attempts) {
        clearInterval(timer);
      }
    }, intervalMs);
  }

  return { interruptHook: patched };
}
