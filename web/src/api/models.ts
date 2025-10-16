import { APIEndpoints, ModelsAPIs } from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getComfyAPI, getLfManager } from '../utils/common';

export const MODELS_API: ModelsAPIs = {
  free: async () => {
    const lfManager = getLfManager();
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.LFFree, { method: 'POST' });
      if (response.status === 200) {
        return true;
      }
      lfManager.log(
        '"free" endpoint returned non-200',
        { status: response.status },
        LogSeverity.Warning,
      );
      return false;
    } catch (error) {
      lfManager.log('"free" endpoint failed', { error }, LogSeverity.Warning);
      return false;
    }
  },
  refresh: async () => {
    const lfManager = getLfManager();
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.LFRefreshNodeDefs, {
        method: 'POST',
      });
      if (response.status === 200) {
        return true;
      }
      lfManager.log(
        '"refresh-node-defs" endpoint returned non-200',
        { status: response.status },
        LogSeverity.Warning,
      );
      return false;
    } catch (error) {
      lfManager.log('"refresh-node-defs" endpoint failed', { error }, LogSeverity.Warning);
      return false;
    }
  },
};

export const beforeFree = async (options?: any) => {
  const lfManager = getLfManager();
  lfManager.log('Unload triggered — clearing LF caches first…', { options }, LogSeverity.Info);
  try {
    const ok = await MODELS_API.free();
    if (ok) {
      lfManager.log('Caches cleared ✔️', {}, LogSeverity.Success);
    } else {
      lfManager.log('Cache clear call returned non-200', {}, LogSeverity.Warning);
    }
  } catch (error) {
    lfManager.log('Error while clearing caches', { error }, LogSeverity.Warning);
  }
};

export const beforeRefreshNodeDefs = async (trigger?: unknown) => {
  const lfManager = getLfManager();
  lfManager.log('Refresh requested — clearing LF caches first…', { trigger }, LogSeverity.Info);
  try {
    const ok = await MODELS_API.refresh();
    if (ok) {
      lfManager.log('Refresh caches cleared ✔️', {}, LogSeverity.Success);
    } else {
      lfManager.log('Refresh cache clear call returned non-200', {}, LogSeverity.Warning);
    }
  } catch (error) {
    lfManager.log('Error while clearing caches ahead of refresh', { error }, LogSeverity.Warning);
  }
};
