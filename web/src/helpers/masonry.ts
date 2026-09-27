import { LfDataCell, LfImageEventPayload, LfMasonryEventPayload } from '@lf-widgets/foundations';
import { MasonryFileIdentity, MasonryState } from '../types/widgets/masonry';

export const EV_HANDLERS = {
  //#region Masonry handler
  masonry: (state: MasonryState, e: CustomEvent<LfMasonryEventPayload>) => {
    const { comp, eventType, originalEvent, selectedShape } = e.detail;

    if (!comp.lfSelectable) {
      return;
    }

    switch (eventType) {
      case 'lf-event':
        const { eventType } = (originalEvent as CustomEvent<LfImageEventPayload>).detail;
        switch (eventType) {
          case 'click':
            const v =
              selectedShape.shape?.value || (selectedShape.shape as LfDataCell<'image'>)?.lfValue;
            state.selected.index = selectedShape.index;
            state.selected.name = v ? String(v).valueOf() : '';
            const selectedCell = state.masonry.lfDataset?.nodes?.[selectedShape.index]?.cells?.lfImage;
            const identity = (selectedCell as unknown as { file_identity?: MasonryFileIdentity })?.file_identity ??
              (selectedShape.shape as unknown as { file_identity?: MasonryFileIdentity })?.file_identity;
            if (identity && typeof identity.directory === 'string' && typeof identity.relative_path === 'string') {
              state.selected.file_identity = { ...identity };
            } else {
              delete state.selected.file_identity;
            }
            break;
        }
        break;
    }
  },
  //#endregion
};
