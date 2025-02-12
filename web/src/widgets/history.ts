import { LfDataDataset } from '@lf-widgets/foundations';
import { EV_HANDLERS } from '../helpers/history';
import { LfEventName } from '../types/events/events';
import {
  HistoryCSS,
  HistoryFactory,
  HistoryNormalizeCallback,
  HistoryState,
} from '../types/widgets/history';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, HistoryState>();

export const historyFactory: HistoryFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { list } = STATE.get(wrapper);

        return list?.lfDataset || {};
      },
      setValue(value) {
        const { list } = STATE.get(wrapper);

        const callback: HistoryNormalizeCallback = (_, u) => {
          list.lfDataset = (u.parsedJson as LfDataDataset) || {};
        };

        normalizeValue(value, callback, CustomWidgetName.history);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const list = document.createElement(TagName.LfList);

    list.classList.add(HistoryCSS.Widget);
    list.lfEmpty = 'History is empty!';
    list.lfEnableDeletions = true;

    switch (node.comfyClass) {
      case NodeName.loadFileOnce:
        break;
      default:
        list.lfSelectable = true;
        break;
    }

    list.addEventListener(LfEventName.LfList, (e) => EV_HANDLERS.list(STATE.get(wrapper), e));

    content.classList.add(HistoryCSS.Content);
    content.appendChild(list);

    wrapper.appendChild(content);

    const options = historyFactory.options(wrapper);

    STATE.set(wrapper, { list, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.history, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
