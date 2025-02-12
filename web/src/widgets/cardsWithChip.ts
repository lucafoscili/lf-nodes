import { getCardProps, prepCards } from '../helpers/card';
import {
  CardsWithChipCSS,
  CardsWithChipDeserializedValue,
  CardsWithChipFactory,
  CardsWithChipNormalizeCallback,
  CardsWithChipState,
} from '../types/widgets/cardsWithChip';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, CardsWithChipState>();

//#region Cards with chip
export const cardsWithChipFactory: CardsWithChipFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { chip, grid } = STATE.get(wrapper);

        return {
          chip: chip?.lfDataset || {},
          props: getCardProps(grid) || [],
        };
      },
      setValue(value) {
        const { chip, grid } = STATE.get(wrapper);

        const callback: CardsWithChipNormalizeCallback = (v, u) => {
          const dataset = u.parsedJson as CardsWithChipDeserializedValue;
          const cardsCount = prepCards(grid, dataset.props);
          if (!cardsCount || !v) {
            return;
          }
          const columns = cardsCount > 1 ? 2 : 1;
          grid.style.setProperty('--card-grid', String(columns).valueOf());
          if (chip) {
            chip.lfDataset = dataset.chip;
          }
        };

        normalizeValue(value, callback, CustomWidgetName.cardsWithChip);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const outerGrid = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const chip = document.createElement(TagName.LfChip);

    content.classList.add(CardsWithChipCSS.Content);
    outerGrid.classList.add(CardsWithChipCSS.Grid);
    grid.classList.add(CardsWithChipCSS.Cards);
    chip.classList.add(CardsWithChipCSS.Chip);

    outerGrid.appendChild(chip);
    outerGrid.appendChild(grid);

    content.appendChild(outerGrid);
    wrapper.appendChild(content);

    const options = cardsWithChipFactory.options(wrapper);

    STATE.set(wrapper, { chip, grid, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.cardsWithChip, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
