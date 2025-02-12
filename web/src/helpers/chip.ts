import { LfChipEventPayload } from '@lf-widgets/foundations';
import { ChipState } from '../types/widgets/chip';

export const EV_HANDLERS = {
  //#region Chip handler
  chip: async (state: ChipState, e: CustomEvent<LfChipEventPayload>) => {
    const { comp, eventType } = e.detail;
    switch (eventType) {
      case 'click':
        const selectedValues: string[] = [];
        (await comp.getSelectedNodes()).forEach((node) => {
          selectedValues.push(String(node.value).valueOf());
        });
        state.selected = selectedValues.join(', ');
        break;
    }
    //#endregion
  },
};
