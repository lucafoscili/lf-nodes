import { ComfyAPIs } from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getComfyAPI, getComfyAPP, getLfManager } from '../utils/common';

declare global {
  interface Window {
    comfyAPI: ComfyUI;
  }
}

//#region Comfy APIs
export const COMFY_API: ComfyAPIs = {
  comfyUi: () => window.comfyAPI,
  event: (name, callback) => {
    getComfyAPI().addEventListener(name, callback);
  },
  executeCommand: (name) => {
    try {
      getComfyAPP().extensionManager.command.execute(name);
    } catch (error) {
      getLfManager().log(`Command ${name} not executed!`, { error }, LogSeverity.Warning);
    }
  },
  getDragAndScale: () => {
    return getComfyAPP().canvas.ds as ComfyDS;
  },
  getLinkById: (id) => {
    return getComfyAPP().graph.links[String(id).valueOf()];
  },
  getNodeById: (id) => {
    return getComfyAPP().graph.getNodeById(+(id || getComfyAPP().runningNodeId));
  },
  getResourceUrl: (subfolder, filename, type = 'output') => {
    const params = [
      'filename=' + encodeURIComponent(filename),
      'type=' + type,
      'subfolder=' + subfolder,
      getComfyAPP().getRandParam().substring(1),
    ].join('&');
    return `/view?${params}`;
  },
  interrupt: () => {
    return getComfyAPI().interrupt();
  },
  queuePrompt: async () => {
    getComfyAPP().queuePrompt(0);
  },
  redraw: () => {
    getComfyAPP().graph.setDirtyCanvas(true, false);
  },
  redrawFull: () => {
    getComfyAPP().graph.setDirtyCanvas(true, true);
  },
  scheduleRedraw: (() => {
    let scheduled = false;

    return (immediate = false) => {
      if (immediate) {
        scheduled = false;
        try {
          getComfyAPP().graph.setDirtyCanvas(true, true);
        } catch {}
        return;
      }
      if (scheduled) {
        return;
      }
      scheduled = true;
      requestAnimationFrame(() => {
        scheduled = false;
        try {
          const { app } = comfyAPI;

          app.graph.setDirtyCanvas(true, true);
        } catch {}
      });
    };
  })(),
  register: (extension) => {
    getComfyAPP().registerExtension(extension);
  },
  upload: async (body) => {
    return await getComfyAPI().fetchApi('/upload/image', {
      method: 'POST',
      body,
    });
  },
};
//#endregion
