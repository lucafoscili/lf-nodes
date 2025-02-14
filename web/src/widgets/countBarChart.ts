import { LfDataDataset } from '@lf-widgets/foundations';
import {
  CountBarChartCSS,
  CountBarChartDeserializedValue,
  CountBarChartFactory,
  CountBarChartNormalizeCallback,
  CountBarChartState,
} from '../types/widgets/countBarChart';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, CountBarChartState>();

export const countBarChartFactory: CountBarChartFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { datasets } = STATE.get(wrapper);

        return {
          chart: datasets?.chart || {},
          chip: datasets?.chip || {},
        };
      },
      setValue(value) {
        const { card, datasets } = STATE.get(wrapper);

        const callback: CountBarChartNormalizeCallback = (_, u) => {
          const json = u.parsedJson as CountBarChartDeserializedValue;
          datasets.chart = json.chart || {};
          datasets.chip = json.chip || {};
          card.lfDataset = {
            nodes: [
              {
                id: 'countBarChart',
                cells: {
                  lfButton: { shape: 'button', value: '' },
                  lfChart: {
                    lfAxis: ['Axis_0'],
                    lfDataset: datasets.chart,
                    lfSeries: ['Series_0'],
                    shape: 'chart',
                    value: '',
                  },
                  lfChip: { lfDataset: datasets.chip, shape: 'chip', value: '' },
                },
              },
            ],
          };
        };

        normalizeValue(value, callback, CustomWidgetName.countBarChart);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const card = document.createElement(TagName.LfCard);

    const chart: LfDataDataset = {};
    const chip: LfDataDataset = {};

    card.classList.add(CountBarChartCSS.Widget);
    card.lfLayout = 'keywords';

    content.classList.add(CountBarChartCSS.Content);
    content.appendChild(card);

    wrapper.appendChild(content);

    const options = countBarChartFactory.options(wrapper);

    STATE.set(wrapper, { card, datasets: { chart, chip }, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.countBarChart, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
