import { LfDataDataset } from '@lf-widgets/foundations';
import {
  CompareCSS,
  CompareFactory,
  CompareNormalizeCallback,
  CompareState,
} from '../types/widgets/compare';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
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
        const { compare, summary } = STATE.get(wrapper);

        const callback: CompareNormalizeCallback = (_, u) => {
          const dataset = (u.parsedJSON as LfDataDataset) || {};
          compare.lfDataset = dataset;
          if (summary) {
            summary.lfDataset = { nodes: (dataset.nodes || []).map(({ id, value }) => ({ id, value })) };
          }
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
    let summary: HTMLLfTreeElement;
    if ([NodeName.textRegionMasks, NodeName.regionColorStats, NodeName.visionPatchEncode]
      .includes(node.comfyClass as NodeName)) {
      // Compare's image selectors are closed by default. Keep result labels visible.
      summary = document.createElement(TagName.LfTree);
      summary.classList.add(CompareCSS.Summary);
      summary.lfAccordionLayout = false;
      summary.lfSelectable = false;
      summary.lfFilter = false;
      summary.lfStyle = '.node__value { white-space: normal; overflow-wrap: anywhere; }';
      content.classList.add(CompareCSS.WithSummary);
      content.appendChild(summary);
    }
    wrapper.appendChild(content);

    const options = compareFactory.options(wrapper);

    STATE.set(wrapper, { compare, summary, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.compare, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
