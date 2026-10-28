import { defineConfig } from 'vitest/config';
import type { Reporter, Vitest } from 'vitest/node';

// Vitest 4.0 has no collection timeout; testTimeout only starts after imports.
const collectionTimeout = 60_000;
const collectionTimeoutReporter = (): Reporter => {
  let vitest: Vitest;
  let startupTimer: ReturnType<typeof setTimeout> | undefined;
  const pending = new Set<string>();
  const active = new Set<string>();
  const collecting = new Map<string, ReturnType<typeof setTimeout>>();

  const clearTimers = () => {
    clearTimeout(startupTimer);
    collecting.forEach(clearTimeout);
    collecting.clear();
  };
  const deadline = (phase: string, files: () => string) => setTimeout(() => {
    clearTimers();
    vitest.logger.error(`[vitest] ${phase} timed out after ${collectionTimeout}ms: ${files()}`);
    process.exitCode = 1;
    // exit() also enforces teardownTimeout if a worker cannot shut down.
    void vitest.exit(true);
  }, collectionTimeout).unref();
  const awaitWorker = () => {
    clearTimeout(startupTimer);
    if (!active.size && pending.size) {
      startupTimer = deadline('Worker startup before collection; waiting for files',
        () => [...pending].join(', '));
    }
  };

  return {
    onInit(ctx) {
      vitest = ctx;
      ctx.onClose(clearTimers);
      startupTimer = deadline('Test discovery', () => ctx.config.root);
    },
    onTestRunStart(specifications) {
      clearTimers();
      pending.clear();
      active.clear();
      specifications.forEach(({ moduleId }) => pending.add(moduleId));
      awaitWorker();
    },
    onTestModuleQueued({ moduleId }) {
      clearTimeout(startupTimer);
      pending.delete(moduleId);
      active.add(moduleId);
      collecting.set(moduleId, deadline('Test collection', () => moduleId));
    },
    onTestModuleCollected({ moduleId }) {
      clearTimeout(collecting.get(moduleId));
      collecting.delete(moduleId);
    },
    onTestModuleEnd({ moduleId }) {
      clearTimeout(collecting.get(moduleId));
      collecting.delete(moduleId);
      active.delete(moduleId);
      awaitWorker();
    },
    onTestRunEnd: clearTimers,
    onProcessTimeout() {
      process.exitCode = 1;
    },
  };
};

export default defineConfig({
  test: {
    // Concurrent worker startup can stall before collection on Windows.
    ...(process.platform === 'win32'
      ? { pool: 'threads' as const, maxWorkers: 1, fileParallelism: false }
      : {}),
    environment: 'jsdom',
    globals: true,
    restoreMocks: true,
    clearMocks: true,
    unstubGlobals: true,
    teardownTimeout: 10_000,
    coverage: { provider: 'v8', enabled: false },
    reporters: ['verbose', collectionTimeoutReporter()],
  },
});
