import { resolve } from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  root: resolve(__dirname, 'web/temp'),
  build: {
    assetsDir: '.',
    outDir: resolve(__dirname, 'web/deploy/js'),
    emptyOutDir: true,
    rollupOptions: {
      external: ['/scripts/api.js', '/scripts/app.js'],
      input: {
        'lf-core': resolve(__dirname, 'web/temp/@lf-widgets/core/dist/lf-core/lf-core.esm.js'),
        'lf-nodes': resolve(__dirname, 'web/temp/index.js'),
      },
      plugins: [visualizer({ open: false, filename: 'web/temp/bundle-stats.html' })],
      treeshake: {
        moduleSideEffects: (id) => {
          const shouldKeep =
            id.includes('@lf-widgets/foundations') ||
            id.includes('@lf-widgets/framework') ||
            id.includes('@lf-widgets/core');
          return shouldKeep;
        },
      },
    },
  },
});
