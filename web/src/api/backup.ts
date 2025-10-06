import {
  APIEndpoints,
  BackupAPIs,
  BaseAPIPayload,
  GetBackupStatsAPIPayload,
} from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getLfManager } from '../utils/common';
/// @ts-ignore
import { api } from '/scripts/api.js';

export const BACKUP_API: BackupAPIs = {
  //#region new
  new: async (backupType = 'automatic') => {
    const lfManager = getLfManager();

    const payload: BaseAPIPayload = {
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const body = new FormData();
      body.append('backup_type', backupType);
      const response = await api.fetchApi(APIEndpoints.NewBackup, { body, method: 'POST' });

      const code = response.status;

      switch (code) {
        case 200:
          const p: BaseAPIPayload = await response.json();
          if (p.status === 'success') {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = 'Unexpected response from the API!';
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion

  //#region getStats
  getStats: async () => {
    const lfManager = getLfManager();

    const payload: GetBackupStatsAPIPayload = {
      data: {
        total_size_bytes: 0,
        file_count: 0,
        backups: [],
      },
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const response = await api.fetchApi(APIEndpoints.GetBackupStats, { method: 'GET' });

      const code = response.status;

      switch (code) {
        case 200:
          const p = (await response.json()) as GetBackupStatsAPIPayload;
          if (p.status === 'success') {
            payload.data = p.data;
            payload.message = 'Backup statistics retrieved successfully.';
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = 'Unexpected response from the API!';
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion

  //#region cleanOld
  cleanOld: async (maxBackups?: number) => {
    const lfManager = getLfManager();
    const _maxBackups = maxBackups || lfManager.getBackupRetention();
    const payload: BaseAPIPayload = {
      message: '',
      status: LogSeverity.Info,
    };

    if (_maxBackups <= 0) {
      const message = 'Backup retention is set to 0, skipping cleanup.';
      lfManager.log(payload.message, { payload }, payload.status);
      payload.message = message;
      payload.status = LogSeverity.Info;
      return payload;
    }

    try {
      const body = new FormData();
      body.append('max_backups', String(_maxBackups));
      const response = await api.fetchApi(APIEndpoints.CleanOldBackups, { body, method: 'POST' });

      const code = response.status;

      switch (code) {
        case 200:
          const p: BaseAPIPayload = await response.json();
          if (p.status === 'success') {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = 'Unexpected response from the API!';
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
};
