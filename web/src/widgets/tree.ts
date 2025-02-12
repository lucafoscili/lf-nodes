import {
  TreeCSS,
  TreeDeserializedValue,
  TreeFactory,
  TreeNormalizeCallback,
  TreeState,
} from '../types/widgets/tree';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, TreeState>();

export const treeFactory: TreeFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { tree } = STATE.get(wrapper);

        return tree.lfDataset || {};
      },
      setValue(value) {
        const { tree } = STATE.get(wrapper);

        const callback: TreeNormalizeCallback = (_, u) => {
          tree.lfDataset = (u.parsedJson as TreeDeserializedValue) || {};
        };

        normalizeValue(value, callback, CustomWidgetName.tree);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const tree = document.createElement(TagName.LfTree);

    switch (node.comfyClass as NodeName) {
      case NodeName.isLandscape:
        tree.lfAccordionLayout = false;
        tree.lfSelectable = false;
        break;
      default:
        tree.lfAccordionLayout = true;
        tree.lfSelectable = false;
        break;
    }

    tree.classList.add(TreeCSS.Widget);

    content.classList.add(TreeCSS.Content);
    content.appendChild(tree);

    wrapper.appendChild(content);

    const options = treeFactory.options(wrapper);

    STATE.set(wrapper, { node, tree, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.tree, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
