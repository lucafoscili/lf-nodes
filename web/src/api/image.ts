import {
  APIEndpoints,
  APIUploadDirectory,
  GetFilesystemAPIPayload,
  GetImageAPIPayload,
  ImageAPIs,
  ImageExplorerRequestOptions,
  ProcessImageAPIPayload,
  UploadImageAPIPayload,
} from '../types/api/api';
import { LogSeverity } from '../types/manager/manager';
import { getComfyAPI, getLfManager } from '../utils/common';

export const IMAGE_API: ImageAPIs = {
  //#region get
  get: async (directory) => {
    const lfManager = getLfManager();

    const payload: GetImageAPIPayload = {
      data: {},
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const body = new FormData();
      if (directory) {
        body.append('directory', directory);
      }

      const response = await getComfyAPI().fetchApi(APIEndpoints.GetImage, {
        body,
        method: 'POST',
      });

      const code = response.status;

      switch (code) {
        case 200:
          const p: GetImageAPIPayload = await response.json();
          if (p.status === 'success') {
            payload.data = p.data;
            payload.message = 'Images fetched successfully.';
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => '');
            payload.message = `Unexpected response from the get-image API (${code}): ${
              errorText || response.statusText
            }`;
          }
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

  //#region explore
  explore: async (directory, options = {}) => {
    const lfManager = getLfManager();

    const payload: GetFilesystemAPIPayload = {
      data: {},
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const body = new FormData();
      if (directory) {
        body.append('directory', directory);
      }

      const { scope, nodePath }: ImageExplorerRequestOptions = options;
      if (scope) {
        body.append('scope', scope);
      }
      if (nodePath) {
        body.append('node', nodePath);
      }

      const response = await getComfyAPI().fetchApi(APIEndpoints.ExploreFilesystem, {
        body,
        method: 'POST',
      });

      const code = response.status;

      switch (code) {
        case 200:
          const p: GetFilesystemAPIPayload = await response.json();
          if (p.status === 'success') {
            payload.data = p.data ?? {};
            payload.message = 'Filesystem data fetched successfully.';
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => '');
            payload.message = `Unexpected response from the explore-filesystem API (${code}): ${
              errorText || response.statusText
            }`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error as string;
      payload.status = LogSeverity.Error;
    }

    lfManager.log(payload.message, { payload, options }, payload.status);
    return payload;
  },
  //#endregion

  //#region process
  process: async (url, type, settings) => {
    const lfManager = getLfManager();

    const payload: ProcessImageAPIPayload = {
      data: '',
      mask: undefined,
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const body = new FormData();
      body.append('url', url);
      body.append('type', type);
      body.append('settings', JSON.stringify(settings));

      const response = await getComfyAPI().fetchApi(APIEndpoints.ProcessImage, {
        body,
        method: 'POST',
      });

      const code = response.status;

      switch (code) {
        case 200:
          const p: ProcessImageAPIPayload = await response.json();
          if (p.status === 'success') {
            payload.data = p.data;
            payload.mask = p.mask;
            payload.message = 'Image processed successfully.';
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => '');
            payload.message = `Unexpected response from the process-image API (${code}): ${
              errorText || response.statusText
            }`;
          }
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

  //#region upload
  upload: async (file: File | Blob, directory: APIUploadDirectory = 'temp') => {
    const lfManager = getLfManager();

    const payload: UploadImageAPIPayload = {
      payload: { paths: [] },
      message: '',
      status: LogSeverity.Info,
    };

    try {
      const body = new FormData();
      body.append('file', file);
      if (directory && directory !== 'temp') {
        body.append('directory', directory);
      }

      const response = await getComfyAPI().fetchApi(APIEndpoints.UploadImage, {
        body,
        method: 'POST',
      });

      const code = response.status;

      switch (code) {
        case 200: {
          const p: UploadImageAPIPayload = await response.json();

          if (
            p.status === 'success' &&
            Array.isArray(p.payload?.paths) &&
            p.payload.paths.length > 0
          ) {
            payload.payload.paths = [p.payload.paths[0]];
            payload.message = 'Image uploaded successfully.';
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        }
        default:
          {
            const errorText = await response.text().catch(() => '');
            payload.message = `Unexpected response from the upload-image API (${code}): ${
              errorText || response.statusText
            }`;
          }
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
