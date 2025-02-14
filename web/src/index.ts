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

initLfManager();
const lfManager = getLfManager();
lfManager.initialize();
if (isDev) {
  console.log('LF Manager initialized!', lfManager);
}
