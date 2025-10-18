import '@lf-widgets/core/dist/lf-core/lf-core.esm.js';
import { LfWorkflowRunnerManager } from './app/manager';

//#region Bootstrap
const hasComfyApp = comfyAPI?.api && comfyAPI?.app;
if (!hasComfyApp) {
  new LfWorkflowRunnerManager();
}
//#endregion
