import { EV_HANDLERS } from '../helpers/chat';
import { LfEventName } from '../types/events/events';
import { ChatCSS, ChatFactory, ChatNormalizeCallback, ChatState } from '../types/widgets/chat';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, ChatState>();

export const chatFactory: ChatFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { history } = STATE.get(wrapper);

        return history || '';
      },
      setValue(value) {
        const state = STATE.get(wrapper);

        const callback: ChatNormalizeCallback = (v) => {
          state.history = v || '';
          state.chat.setHistory(v);
        };

        normalizeValue(value, callback, CustomWidgetName.chat);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const chat = document.createElement(TagName.LfChat);

    content.classList.add(ChatCSS.Content);
    chat.classList.add(ChatCSS.Widget);

    chat.addEventListener(LfEventName.LfChat, (e) => EV_HANDLERS.chat(STATE.get(wrapper), e));

    content.appendChild(chat);
    wrapper.appendChild(content);

    const options = chatFactory.options(wrapper);

    STATE.set(wrapper, { chat, history: '', node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.chat, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
