import { PLACEHOLDER_MESSAGE } from '../fixtures/messenger';
import { EV_HANDLERS } from '../helpers/messenger';
import { LfEventName } from '../types/events/events';
import {
  MessengerCSS,
  MessengerDeserializedValue,
  MessengerFactory,
  MessengerNormalizeCallback,
  MessengerState,
} from '../types/widgets/messenger';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, isValidObject, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, MessengerState>();

export const messengerFactory: MessengerFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { config, elements } = STATE.get(wrapper);
        const { messenger } = elements;

        return {
          dataset: messenger.lfDataset || {},
          config,
        };
      },
      setValue(value) {
        const state = STATE.get(wrapper);
        const { elements } = state;
        const { messenger, placeholder } = elements;

        const callback: MessengerNormalizeCallback = (_, u) => {
          const { config, dataset } = u.parsedJson as MessengerDeserializedValue;
          messenger.lfDataset = dataset;

          if (isValidObject(config)) {
            messenger.lfValue = config;
            state.config = config;
          }

          placeholder.classList.add(MessengerCSS.PlaceholderHidden);
        };
        const onException = () => {
          placeholder.classList.remove(MessengerCSS.PlaceholderHidden);
        };

        normalizeValue(value, callback, CustomWidgetName.messenger, onException);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const placeholder = document.createElement(TagName.Div);
    const messenger = document.createElement(TagName.LfMessenger);

    content.classList.add(MessengerCSS.Content);
    messenger.classList.add(MessengerCSS.Widget);
    placeholder.classList.add(MessengerCSS.Placeholder);

    placeholder.innerHTML = PLACEHOLDER_MESSAGE;

    messenger.addEventListener(LfEventName.LfMessenger, (e) =>
      EV_HANDLERS.messenger(STATE.get(wrapper), e),
    );

    content.appendChild(placeholder);
    content.appendChild(messenger);

    wrapper.appendChild(content);

    const options = messengerFactory.options(wrapper);

    STATE.set(wrapper, { config: null, elements: { messenger, placeholder }, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.messenger, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
