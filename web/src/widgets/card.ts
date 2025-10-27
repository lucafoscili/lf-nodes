import { EV_HANDLERS, getCardProps, prepCards } from '../helpers/card';
import { LfEventName } from '../types/events/events';
import {
  CardCSS,
  CardDeserializedValue,
  CardFactory,
  CardNormalizeCallback,
  CardState,
} from '../types/widgets/card';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, CardState>();

export const cardFactory: CardFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { grid } = STATE.get(wrapper);

        return {
          props: getCardProps(grid) || [],
        };
      },
      setValue(value) {
        const { grid } = STATE.get(wrapper);

        const callback: CardNormalizeCallback = (_, u) => {
          const { props } = u.parsedJSON as unknown as CardDeserializedValue;
          const len = props?.length > 1 ? 2 : 1;
          grid.style.setProperty('--card-grid', `repeat(1, 1fr) / repeat(${len}, 1fr)`);
          prepCards(grid, props);
        };

        normalizeValue(value, callback, CustomWidgetName.card);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);

    grid.classList.add(CardCSS.Grid);

    content.classList.add(CardCSS.Content);
    content.appendChild(grid);

    switch (node.comfyClass as NodeName) {
      case NodeName.checkpointSelector:
      case NodeName.diffusionModelSelector:
      case NodeName.embeddingSelector:
      case NodeName.loraAndEmbeddingSelector:
      case NodeName.loraSelector:
        content.classList.add(CardCSS.ContentHasButton);

        const button = document.createElement(TagName.LfButton);
        button.lfIcon = 'download';
        button.lfLabel = 'Refresh';
        button.lfStretchX = true;
        button.title = 'Attempts to manually ownload fresh metadata from CivitAI';
        button.addEventListener(LfEventName.LfButton, (e) =>
          EV_HANDLERS.button(STATE.get(wrapper), e),
        );

        content.appendChild(button);
        break;
    }

    wrapper.appendChild(content);

    const options = cardFactory.options(wrapper);

    STATE.set(wrapper, { grid, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.card, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
