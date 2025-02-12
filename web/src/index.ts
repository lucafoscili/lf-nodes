import * as Foundations from '@lf-widgets/foundations';
import * as Framework from '@lf-widgets/framework';
import * as Core from '@lf-widgets/core/dist/loader';

import { getLfManager, initLfManager } from './utils/common';

const isDev = process.env.NODE_ENV === 'development';

if (isDev) {
  console.log('LF modules loaded!', Core, Foundations, Framework);
}

Framework.getLfFramework();
if (isDev) {
  console.log('LF Framework initialized!', Framework);
}

initLfManager();
const lfManager = getLfManager();
lfManager.initialize();
if (isDev) {
  console.log('LF Manager initialized!', lfManager);
}

Core.defineCustomElements(window);
if (isDev) {
  console.log('LF Core custom elements defined!', Core);
}
