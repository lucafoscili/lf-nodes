import { LfDataDataset } from '@lf-widgets/foundations';
import {
  CompareCSS,
  CompareFactory,
  CompareNormalizeCallback,
  CompareState,
} from '../types/widgets/compare';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, CompareState>();

export const compareFactory: CompareFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { compare } = STATE.get(wrapper);

        return compare.lfDataset || {};
      },
      setValue(value) {
        const { compare } = STATE.get(wrapper);

        const callback: CompareNormalizeCallback = (_, u) => {
          compare.lfDataset = (u.parsedJSON as LfDataDataset) || {};
        };

        normalizeValue(value, callback, CustomWidgetName.compare);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const compare = document.createElement(TagName.LfCompare);

    content.classList.add(CompareCSS.Content);
    compare.classList.add(CompareCSS.Widget);

    switch (node.comfyClass) {
      default:
        compare.lfShape = 'image';
        break;
    }

    content.appendChild(compare);
    wrapper.appendChild(content);

    const options = compareFactory.options(wrapper);

    STATE.set(wrapper, { compare, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.compare, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
