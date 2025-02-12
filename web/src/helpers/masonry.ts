import { LfDataCell, LfImageEventPayload, LfMasonryEventPayload } from '@lf-widgets/foundations';
import { MasonryState } from '../types/widgets/masonry';

export const EV_HANDLERS = {
  //#region Masonry handler
  masonry: (state: MasonryState, e: CustomEvent<LfMasonryEventPayload>) => {
    const { eventType, originalEvent, selectedShape } = e.detail;

    switch (eventType) {
      case 'lf-event':
        const { eventType } = (originalEvent as CustomEvent<LfImageEventPayload>).detail;
        switch (eventType) {
          case 'click':
            const v =
              selectedShape.shape?.value || (selectedShape.shape as LfDataCell<'image'>)?.lfValue;
            state.selected.index = selectedShape.index;
            state.selected.name = v ? String(v).valueOf() : '';
            break;
        }
        break;
    }
  },
  //#endregion
};
