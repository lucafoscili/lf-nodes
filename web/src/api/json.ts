import { APIEndpoints, BaseAPIPayload, GetJSONAPIPayload, JSONAPIs } from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getComfyAPI, getComfyClientId, getLfManager } from '../utils/common';

const UPDATE_CHAINS = new Map<string, Promise<void>>();

export const serializeJSONUpdate = async <T>(
  key: string,
  operation: () => Promise<T>,
): Promise<T> => {
  const previous = UPDATE_CHAINS.get(key) ?? Promise.resolve();
  const result = previous.catch(() => undefined).then(operation);
  const tail = result.then(
    () => undefined,
    () => undefined,
  );
  UPDATE_CHAINS.set(key, tail);
  try {
    return await result;
  } finally {
    if (UPDATE_CHAINS.get(key) === tail) UPDATE_CHAINS.delete(key);
  }
};

export const JSON_API: JSONAPIs = {
  //#region get
  get: async (filePath) => {
    const lfManager = getLfManager();

    const payload = {
      data: {},
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const body = new FormData();
      body.append('file_path', filePath);
      const callerClientId = getComfyClientId();
      if (callerClientId) {
        body.append('caller_client_id', callerClientId);
      }

      const response = await getComfyAPI().fetchApi(APIEndpoints.GetJson, {
        body,
        method: 'POST',
      });

      const code = response.status;

      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === 'success') {
            payload.data = p.data;
            payload.message = 'JSON data fetched successfully.';
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          payload.message = `Unexpected response from the get-json API: ${await response.text()}`;
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error.toString();
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion

  //#region update
  update: (filePath, dataset) => {
    const serializedDataset = JSON.stringify(dataset);
    return serializeJSONUpdate(filePath, async () => {
      const lfManager = getLfManager();

      const payload: BaseAPIPayload = {
        message: '',
        status: LogSeverity.Info,
      };

      const body = new FormData();
      body.append('file_path', filePath);
      body.append('dataset', serializedDataset);
      const callerClientId = getComfyClientId();
      if (callerClientId) {
        body.append('caller_client_id', callerClientId);
      }

      try {
        const response = await getComfyAPI().fetchApi(APIEndpoints.UpdateJson, {
          body,
          method: 'POST',
        });

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
            payload.message = await response.text().catch(() => 'Unexpected response from the API!');
            payload.status = LogSeverity.Error;
            break;
        }
      } catch (error) {
        payload.message = error;
        payload.status = LogSeverity.Error;
      }

      lfManager.log(payload.message, { payload }, payload.status);
      return payload;
    });
  },
  //#endregion

  //#region recoverEditDataset
  recoverEditDataset: async (nodeId, contextId, callerClientId) => {
    const lfManager = getLfManager();
    const resolvedCallerClientId = callerClientId ?? getComfyClientId();

    const payload: GetJSONAPIPayload = {
      data: {},
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const body = new FormData();
      body.append('node_id', nodeId);
      if (contextId) {
        body.append('context_id', contextId);
      }
      if (resolvedCallerClientId) {
        body.append('caller_client_id', resolvedCallerClientId);
      }

      const response = await getComfyAPI().fetchApi(APIEndpoints.RecoverEditDataset, {
        body,
        method: 'POST',
      });

      const code = response.status;

      switch (code) {
        case 200: {
          const p = await response.json();
          if (p.status === 'success') {
            payload.data = p.data ?? ({} as any);
            payload.message = p.data
              ? 'Recovered pending editing dataset successfully.'
              : 'No pending editing dataset found.';
            payload.status = p.data ? LogSeverity.Success : LogSeverity.Info;
          } else {
            payload.message = p.message ?? 'Failed to recover editing dataset.';
            payload.status = LogSeverity.Error;
          }
          break;
        }
        default:
          payload.message = `Unexpected response from the recover-edit-dataset API: ${await response
            .text()
            .catch(() => '')}`;
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = (error as Error).toString();
      payload.status = LogSeverity.Error;
    }

    lfManager.log(
      payload.message,
      { callerClientId: resolvedCallerClientId, contextId, nodeId, payload },
      payload.status,
    );
    return payload;
  },
  //#endregion
};
