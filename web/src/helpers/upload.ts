import { LfUploadEventPayload } from '@lf-widgets/foundations';
import { UploadState } from '../types/widgets/upload';
import { uploadFiles } from '../utils/common';

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
        const { filesStr } = await uploadFiles(selectedFiles, upload);

        state.files = filesStr || '';
        break;
    }
  },
  //#endregion
};
