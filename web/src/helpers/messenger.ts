import { LfMessengerEventPayload } from '@lf-widgets/foundations';
import { MessengerState } from '../types/widgets/messenger';

export const EV_HANDLERS = {
  //#region Messenger handler
  messenger: (state: MessengerState, e: CustomEvent<LfMessengerEventPayload>) => {
    const { eventType, config } = e.detail;

    switch (eventType) {
      case 'save':
        if (config && typeof config === 'object') {
          state.config = config;
        }
        break;
    }
  },
  //#endregion
};
