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
        'LF free endpoint returned non-200',
        { status: response.status },
        LogSeverity.Warning,
      );
      return false;
    } catch (error) {
      lfManager.log('LF free endpoint failed', { error }, LogSeverity.Warning);
      return false;
    }
  },
};

// Execute this before calling ComfyUI's native free API. Adds visible logs and clears LF caches.
export const beforeFree = async (options?: any) => {
  const lfManager = getLfManager();
  console.info('[LF Nodes] Unload triggered — clearing LF caches first…', options);
  lfManager.log('LF: Unload triggered — clearing LF caches first…', { options }, LogSeverity.Info);
  try {
    const ok = await MODELS_API.free();
    if (ok) {
      console.info('[LF Nodes] Caches cleared ✔️');
      lfManager.log('LF: Caches cleared ✔️', {}, LogSeverity.Success);
    } else {
      console.warn('[LF Nodes] Cache clear call returned non-200');
      lfManager.log('LF: Cache clear call returned non-200', {}, LogSeverity.Warning);
    }
  } catch (error) {
    console.warn('[LF Nodes] Error while clearing caches', error);
    lfManager.log('LF: Error while clearing caches', { error }, LogSeverity.Warning);
  }
};
