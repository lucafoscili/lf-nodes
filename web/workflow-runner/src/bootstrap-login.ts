import { getLfFramework } from '@lf-widgets/framework';

//#region Bootstrap
(function initLoginBootstrap() {
  const hasComfyApp = typeof comfyAPI !== 'undefined' && comfyAPI?.api && comfyAPI?.app;
  if (hasComfyApp) {
    return null;
  }

  const framework = getLfFramework();
  framework.theme.set('dark');

  return;
})();
//#endregion
