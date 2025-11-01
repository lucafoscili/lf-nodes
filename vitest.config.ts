import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
    restoreMocks: true,
    clearMocks: true,
    unstubGlobals: true,
    coverage: { provider: 'v8', enabled: false },
  },
});
