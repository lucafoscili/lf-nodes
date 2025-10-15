import { getLfFramework } from '@lf-widgets/framework';
import './@lf-widgets/core/dist/lf-core/lf-core.esm.js';
import { getLfManager, initLfManager } from './utils/common';

const isDev = true;
if (isDev) {
  console.log('LF modules loaded!');
}

getLfFramework();
if (isDev) {
  console.log('LF Framework initialized!');
}

const hasComfyApp = typeof window !== 'undefined' && typeof (window as any).LGraph !== 'undefined';
if (hasComfyApp) {
  initLfManager();
  const lfManager = getLfManager();
  lfManager.initialize();
  if (isDev) {
    console.log('LF Manager initialized!', lfManager);
  }
} else {
  if (isDev) {
    console.log('No Comfy app detected.');
  }
}
