import { LfUploadEventPayload } from '@lf-widgets/foundations';
import { LogSeverity } from '../types/manager/manager';
import { UploadState } from '../types/widgets/upload';
import { getApiRoutes, getLfManager } from '../utils/common';

export const EV_HANDLERS = {
  //#region Upload handler
  upload: async (state: UploadState, e: CustomEvent<LfUploadEventPayload>) => {
    const { eventType, selectedFiles } = e.detail;

    const { upload } = state;

    switch (eventType) {
      case 'delete':
        state.files = Array.from(selectedFiles, (file) => file.name).join(';') || '';
        return;
      case 'upload':
        const fileNames: Set<string> = new Set();

        for (let index = 0; index < selectedFiles.length; index++) {
          const file = selectedFiles[index];
          try {
            const body = new FormData();
            const i = file.webkitRelativePath.lastIndexOf('/');
            const subfolder = file.webkitRelativePath.slice(0, i + 1);
            const new_file = new File([file], file.name, {
              type: file.type,
              lastModified: file.lastModified,
            });
            body.append('image', new_file);
            if (i > 0) {
              body.append('subfolder', subfolder);
            }
            const resp = await getApiRoutes().comfy.upload(body);

            if (resp.status === 200 || resp.status === 201) {
              getLfManager().log('POST result', { json: resp.json }, LogSeverity.Success);
              fileNames.add(file.name);
              upload.dataset.files = upload.dataset.files + ';' + file.name;
            } else {
              getLfManager().log('POST failed', { statusText: resp.statusText }, LogSeverity.Error);
            }
          } catch (error) {
            alert(`Upload failed: ${error}`);
          }
        }

        state.files = Array.from(fileNames)?.join(';') || '';
        break;
    }
  },
  //#endregion
};
