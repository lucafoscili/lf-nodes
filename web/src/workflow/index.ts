import '@lf-widgets/core/dist/lf-core/lf-core.esm.js';
import { LfWorkflowApp } from './app/manager';

//#region Bootstrap
const hasComfyApp = comfyAPI?.api && comfyAPI?.app;
if (!hasComfyApp) {
  new LfWorkflowApp();
}
//#endregion
