import {
  APIEndpoints,
  BaseAPIPayload,
  GetPreviewStatsAPIPayload,
  PreviewAPIs,
} from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getLfManager } from '../utils/common';
/// @ts-ignore
import { api } from '/scripts/api.js';

export const PREVIEW_API: PreviewAPIs = {
  //#region clearCache
  clearCache: async () => {
    const lfManager = getLfManager();

    const payload: BaseAPIPayload = {
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const response: Response = await api.fetchApi(APIEndpoints.ClearPreviewCache, {
        method: 'POST',
      });

      const code = response.status;

      switch (code) {
        case 200:
          const p: BaseAPIPayload = await response.json();
          if (p.status === 'success') {
            payload.message = p.message || 'Preview cache cleared successfully.';
            payload.status = LogSeverity.Success;
          }
          break;
        case 403:
          payload.message = 'Permission denied: Unable to delete preview cache.';
          payload.status = LogSeverity.Error;
          break;
        default:
          {
            const errorText = await response.text().catch(() => '');
            payload.message = `Unexpected response from the clear-preview-cache API (${code}): ${
              errorText || response.statusText
            }`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion

  //#region getStats
  getStats: async () => {
    const lfManager = getLfManager();

    const payload: GetPreviewStatsAPIPayload = {
      data: {
        total_size_bytes: 0,
        file_count: 0,
        path: '',
      },
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const response: Response = await api.fetchApi(APIEndpoints.GetPreviewStats, {
        method: 'POST',
      });

      const code = response.status;

      switch (code) {
        case 200:
          const p: GetPreviewStatsAPIPayload = await response.json();
          if (p.status === 'success') {
            payload.data = p.data;
            payload.message = p.message || 'Preview stats retrieved successfully.';
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => '');
            payload.message = `Unexpected response from the get-preview-stats API (${code}): ${
              errorText || response.statusText
            }`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
};
