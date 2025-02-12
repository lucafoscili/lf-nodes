import { LfChatEventPayload } from '@lf-widgets/foundations';
import { LogSeverity } from '../types/manager/manager';
import { ChatState } from '../types/widgets/chat';
import { getLfManager } from '../utils/common';

export const EV_HANDLERS = {
  //#region Chat handler
  chat: (state: ChatState, e: CustomEvent<LfChatEventPayload>) => {
    const { eventType, history, status } = e.detail;

    switch (eventType) {
      case 'polling':
        const severity =
          status === 'ready'
            ? LogSeverity.Info
            : status === 'offline'
            ? LogSeverity.Error
            : LogSeverity.Warning;
        getLfManager().log('Chat widget, polling status: ' + status, { chat: e.detail }, severity);
        break;
      case 'update':
        state.history = history;
        break;
    }
  },
  //#endregion
};
