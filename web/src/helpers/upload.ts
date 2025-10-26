import { LfUploadEventPayload } from '@lf-widgets/foundations';
import { UploadState } from '../types/widgets/upload';
import { ComfyWidgetName } from '../types/widgets/widgets';
import { getWidget, uploadFiles } from '../utils/common';

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
        const socket = getWidget(state.node, ComfyWidgetName.combo);
        const dir = socket.value?.toString() || 'temp';
        const { filesStr } = await uploadFiles(selectedFiles, upload, dir);

        state.files = filesStr || '';
        break;
    }
  },
  //#endregion
};
