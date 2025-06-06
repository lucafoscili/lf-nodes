import {
  CarouselCSS,
  CarouselDeserializedValue,
  CarouselFactory,
  CarouselNormalizeCallback,
  CarouselState,
} from '../types/widgets/carousel';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, CarouselState>();

export const carouselFactory: CarouselFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { carousel } = STATE.get(wrapper);

        return carousel?.lfDataset || {};
      },
      setValue(value) {
        const { carousel } = STATE.get(wrapper);

        const callback: CarouselNormalizeCallback = (_, u) => {
          const dataset = u.parsedJson as CarouselDeserializedValue;
          carousel.lfDataset = dataset || {};
        };

        normalizeValue(value, callback, CustomWidgetName.carousel);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const carousel = document.createElement(TagName.LfCarousel);

    carousel.lfAutoPlay = true;

    content.classList.add(CarouselCSS.Content);
    carousel.classList.add(CarouselCSS.Widget);

    content.appendChild(carousel);
    wrapper.appendChild(content);

    const options = carouselFactory.options(wrapper);

    STATE.set(wrapper, { carousel, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.carousel, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
