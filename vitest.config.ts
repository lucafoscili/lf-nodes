import { defineConfig } from 'vitest/config';

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
    coverage: { provider: 'v8', enabled: false },
    reporters: ['verbose'],
  },
});
