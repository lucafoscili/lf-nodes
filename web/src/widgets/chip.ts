import { EV_HANDLERS } from '../helpers/chip';
import { LfEventName } from '../types/events/events';
import { ChipCSS, ChipFactory, ChipNormalizeCallback, ChipState } from '../types/widgets/chip';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, ChipState>();

export const chipFactory: ChipFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { selected } = STATE.get(wrapper);

        return selected || '';
      },
      setValue(value) {
        const state = STATE.get(wrapper);

        const callback: ChipNormalizeCallback = (v) => {
          const value = v ? v.split(', ') : [];
          state.selected = v;
          state.chip.setSelectedNodes(value);
        };

        normalizeValue(value, callback, CustomWidgetName.chip);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const chip = document.createElement(TagName.LfChip);

    content.classList.add(ChipCSS.Content);
    chip.classList.add(ChipCSS.Widget);
    chip.addEventListener(LfEventName.LfChip, (e) => EV_HANDLERS.chip(STATE.get(wrapper), e));

    switch (node.comfyClass) {
      case NodeName.keywordToggleFromJson:
        chip.lfStyling = 'filter';
        break;
    }

    content.appendChild(chip);
    wrapper.appendChild(content);

    const options = chipFactory.options(wrapper);

    STATE.set(wrapper, { chip, node, selected: '', wrapper });

    return { widget: createDOMWidget(CustomWidgetName.chip, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
