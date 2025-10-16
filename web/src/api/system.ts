import {
  APIEndpoints,
  DiskInfo,
  GetCpuStatsAPIPayload,
  GetDiskStatsAPIPayload,
  GetGpuStatsAPIPayload,
  GetRamStatsAPIPayload,
  GPUInfo,
  RamStats,
  SystemAPIs,
} from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getComfyAPI, getLfManager } from '../utils/common';

const unexpectedMessage = (endpoint: string, code: number, response: Response, text?: string) => {
  const body = text || response.statusText || 'No message provided.';
  return `Unexpected response from ${endpoint} (${code}): ${body}`;
};

const normalizeMessage = (message?: string, fallback = 'Statistics retrieved successfully.') => {
  return message && message.trim().length > 0 ? message : fallback;
};

export const SYSTEM_API: SystemAPIs = {
  //#region getGpuStats
  getGpuStats: async () => {
    const lfManager = getLfManager();
    const payload: GetGpuStatsAPIPayload = {
      data: [] as GPUInfo[],
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const response: Response = await getComfyAPI().fetchApi(APIEndpoints.GetGpuStats, {
        method: 'GET',
      });
      const code = response.status;

      switch (code) {
        case 200: {
          const p: GetGpuStatsAPIPayload = await response.json();
          payload.data = p.data || [];
          payload.message = normalizeMessage(p.message, 'GPU statistics retrieved successfully.');
          payload.status = p.status === 'success' ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text = await response.text().catch(() => '');
          payload.message = unexpectedMessage('get-gpu-stats', code, response, text);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion

  //#region getDiskStats
  getDiskStats: async () => {
    const lfManager = getLfManager();
    const payload: GetDiskStatsAPIPayload = {
      data: [] as DiskInfo[],
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const response: Response = await getComfyAPI().fetchApi(APIEndpoints.GetDiskStats, {
        method: 'GET',
      });
      const code = response.status;

      switch (code) {
        case 200: {
          const p: GetDiskStatsAPIPayload = await response.json();
          payload.data = p.data || [];
          payload.message = normalizeMessage(p.message, 'Disk statistics retrieved successfully.');
          payload.status = p.status === 'success' ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text = await response.text().catch(() => '');
          payload.message = unexpectedMessage('get-disk-stats', code, response, text);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion

  //#region getCpuStats
  getCpuStats: async () => {
    const lfManager = getLfManager();
    const payload: GetCpuStatsAPIPayload = {
      data: {
        average: 0,
        cores: [],
        count: 0,
        physical_count: 0,
      },
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const response: Response = await getComfyAPI().fetchApi(APIEndpoints.GetCpuStats, {
        method: 'GET',
      });
      const code = response.status;

      switch (code) {
        case 200: {
          const p: GetCpuStatsAPIPayload = await response.json();
          payload.data = p.data || payload.data;
          payload.message = normalizeMessage(p.message, 'CPU statistics retrieved successfully.');
          payload.status = p.status === 'success' ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text = await response.text().catch(() => '');
          payload.message = unexpectedMessage('get-cpu-stats', code, response, text);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion

  //#region getRamStats
  getRamStats: async () => {
    const lfManager = getLfManager();
    const payload: GetRamStatsAPIPayload = {
      data: {
        available: 0,
        percent: 0,
        swap_total: 0,
        swap_used: 0,
        total: 0,
        used: 0,
      } as RamStats,
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const response: Response = await getComfyAPI().fetchApi(APIEndpoints.GetRamStats, {
        method: 'GET',
      });
      const code = response.status;

      switch (code) {
        case 200: {
          const p: GetRamStatsAPIPayload = await response.json();
          payload.data = p.data || payload.data;
          payload.message = normalizeMessage(p.message, 'RAM statistics retrieved successfully.');
          payload.status = p.status === 'success' ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text = await response.text().catch(() => '');
          payload.message = unexpectedMessage('get-ram-stats', code, response, text);
          payload.status = LogSeverity.Error;
          break;
        }
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
