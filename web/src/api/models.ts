import { APIEndpoints, ModelsAPIs } from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getLfManager } from '../utils/common';
/// @ts-ignore
import { api } from '/scripts/api.js';

export const MODELS_API: ModelsAPIs = {
  free: async () => {
    const lfManager = getLfManager();
    try {
      const response = await api.fetchApi(APIEndpoints.LFFree, { method: 'POST' });
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
