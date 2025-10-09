import { EV_HANDLERS } from '../helpers/masonry';
import { LfEventName } from '../types/events/events';
import {
  MasonryCSS,
  MasonryDeserializedValue,
  MasonryFactory,
  MasonryNormalizeCallback,
  MasonryState,
} from '../types/widgets/masonry';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, isValidNumber, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, MasonryState>();

export const masonryFactory: MasonryFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { masonry, selected } = STATE.get(wrapper);
        const { index, name } = selected;

        return {
          columns: masonry?.lfColumns || 3,
          dataset: masonry?.lfDataset || {},
          index: isValidNumber(index) ? index : NaN,
          name: name || '',
          view: masonry?.lfView || 'main',
        };
      },
      setValue(value) {
        const callback: MasonryNormalizeCallback = (_, u) => {
          const { masonry, selected } = STATE.get(wrapper);

          const { columns, dataset, index, name, view, slot_map } =
            u.parsedJson as MasonryDeserializedValue;

          if (columns) {
            masonry.lfColumns = columns;
          }
          if (dataset) {
            masonry.lfDataset = dataset || {};
          }
          if (view) {
            masonry.lfView = view;
          }
          if (isValidNumber(index)) {
            selected.index = index;
            selected.name = name || '';
            masonry.setSelectedShape(index);
          }

          if (slot_map && typeof slot_map === 'object' && Object.keys(slot_map).length > 0) {
            while (masonry.firstChild) {
              masonry.removeChild(masonry.firstChild);
            }

            for (const key in slot_map) {
              if (!Object.hasOwn(slot_map, key)) continue;

              const element = slot_map[key];
              const div = document.createElement('div');
              div.innerHTML = element;
              div.setAttribute('slot', key);
              div.classList.add(MasonryCSS.Slot);
              masonry.appendChild(div);
            }

            masonry.lfShape = 'slot';
          }
        };

        normalizeValue(value, callback, CustomWidgetName.masonry);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const masonry = document.createElement(TagName.LfMasonry);

    masonry.classList.add(MasonryCSS.Widget);
    masonry.addEventListener(LfEventName.LfMasonry, (e) =>
      EV_HANDLERS.masonry(STATE.get(wrapper), e),
    );
    masonry.lfActions = true;
    masonry.lfColumns = 3;

    switch (node.comfyClass) {
      case NodeName.loadImages:
        masonry.lfSelectable = true;
        break;
    }

    content.classList.add(MasonryCSS.Content);
    content.appendChild(masonry);

    wrapper.appendChild(content);

    const options = masonryFactory.options(wrapper);

    STATE.set(wrapper, { masonry, node, selected: { index: NaN, name: '' }, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.masonry, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
