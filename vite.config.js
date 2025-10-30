import { resolve } from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { defineConfig } from 'vite';

const tempRoot = resolve(__dirname, 'web/temp');

export default defineConfig({
  base: './',
  root: tempRoot,
  build: {
    emptyOutDir: false,
    outDir: resolve(__dirname, 'web/deploy'),
    sourcemap: true,
    minify: false,
    rollupOptions: {
      input: {
        'js/lf-nodes': resolve(tempRoot, 'index.js'),
        'workflow-runner/js/workflow-runner': resolve(tempRoot, 'workflow-runner/index.js'),
        'workflow-runner/js/bootstrap-login': resolve(
          tempRoot,
          'workflow-runner/bootstrap-login.js',
        ),
        'workflow-runner/js/bootstrap-not-found': resolve(
          tempRoot,
          'workflow-runner/bootstrap-not-found.js',
        ),
      },
      external: ['/scripts/api.js', '/scripts/app.js'],
      output: {
        entryFileNames: (chunk) => `${chunk.name}.js`,
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
        manualChunks(id) {
          if (id.includes('@lf-widgets')) {
            const match = id.match(/@lf-widgets\/([^/]+)/);
            if (match && match[1]) {
              return `lf-widgets-${match[1]}`;
            }
            return 'lf-widgets-core';
          }
        },
      },
      plugins: [visualizer({ open: false, filename: 'web/temp/bundle-stats.html' })],
    },
  },
});
