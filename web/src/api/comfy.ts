import { ComfyAPIs } from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getLfManager } from '../utils/common';
/// @ts-ignore
import { api } from '/scripts/api.js';
/// @ts-ignore
import { app } from '/scripts/app.js';

declare global {
  interface Window {
    comfyAPI: ComfyUI;
  }
}

//#region Comfy APIs
export const COMFY_API: ComfyAPIs = {
  comfyUi: () => window.comfyAPI,
  event: (name, callback) => {
    api.addEventListener(name, callback);
  },
  executeCommand: (name) => {
    try {
      app.extensionManager.command.execute(name);
    } catch (error) {
      getLfManager().log(`Command ${name} not executed!`, { error }, LogSeverity.Warning);
    }
  },
  getDragAndScale: () => {
    return app.canvas.ds as ComfyDS;
  },
  getLinkById: (id) => {
    return app.graph.links[String(id).valueOf()];
  },
  getNodeById: (id) => {
    return app.graph.getNodeById(+(id || app.runningNodeId));
  },
  getResourceUrl: (subfolder, filename, type = 'output') => {
    const params = [
      'filename=' + encodeURIComponent(filename),
      'type=' + type,
      'subfolder=' + subfolder,
      app.getRandParam().substring(1),
    ].join('&');
    return `/view?${params}`;
  },
  interrupt: () => {
    return api.interrupt();
  },
  queuePrompt: async () => {
    app.queuePrompt(0);
  },
  redraw: () => {
    app.graph.setDirtyCanvas(true, false);
  },
  redrawFull: () => {
    app.graph.setDirtyCanvas(true, true);
  },
  register: (extension) => {
    app.registerExtension(extension);
  },
  upload: async (body) => {
    return await api.fetchApi('/upload/image', {
      method: 'POST',
      body,
    });
  },
};
//#endregion
