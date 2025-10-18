import '@lf-widgets/core/dist/lf-core/lf-core.esm.js';
import { LfWorkflowRunnerManager } from './app/manager';

export const bootstrapWorkflowRunner = (): LfWorkflowRunnerManager | null => {
  const hasComfyApp = typeof comfyAPI !== 'undefined' && comfyAPI?.api && comfyAPI?.app;
  if (hasComfyApp) {
    return null;
  }

  return new LfWorkflowRunnerManager();
};
