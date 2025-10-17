import { resolve } from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  build: {
    assetsDir: '.',
    emptyOutDir: true,
    lib: {
      formats: ['es'],
      name: 'lf-nodes',
      entry: resolve(__dirname, 'web/temp/index.js'),
    },
    outDir: resolve(__dirname, 'web/deploy/js'),
    minify: false,
    rollupOptions: {
      external: ['/scripts/api.js', '/scripts/app.js'],
      plugins: [visualizer({ open: false, filename: 'web/temp/bundle-stats.html' })],
    },
    sourcemap: true,
  },
  root: resolve(__dirname, 'web/temp'),
});
