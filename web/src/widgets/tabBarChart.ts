import { apiCall, EV_HANDLERS, prepareTabbarDataset } from '../helpers/tabBarChart';
import { AnalyticsType } from '../types/api/api';
import { LfEventName } from '../types/events/events';
import {
  TabBarChartColors,
  TabBarChartCSS,
  TabBarChartDeserializedValue,
  TabBarChartFactory,
  TabBarChartIds,
  TabBarChartNormalizeCallback,
  TabBarChartState,
} from '../types/widgets/tabBarChart';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, TabBarChartState>();

export const tabBarChartFactory: TabBarChartFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue: () => {
        const { directory, node } = STATE.get(wrapper);

        switch (node.comfyClass) {
          case NodeName.usageStatistics:
            return { directory: directory || '' };
          default:
            return {};
        }
      },
      setValue: (value) => {
        const state = STATE.get(wrapper);
        const { chart, tabbar } = state.elements;

        const callback: TabBarChartNormalizeCallback = (_, u) => {
          const parsedValue = u.parsedJson as TabBarChartDeserializedValue;

          switch (state.node.comfyClass) {
            case NodeName.usageStatistics:
              state.directory = parsedValue.directory;

              apiCall(state);
              break;
            default:
              for (const key in parsedValue) {
                const dataset = parsedValue[key];
                chart.lfDataset = dataset || {};
                tabbar.lfDataset = prepareTabbarDataset(parsedValue) || {};
                requestAnimationFrame(async () => tabbar.setValue(0));
              }
              break;
          }
        };

        normalizeValue(value, callback, CustomWidgetName.tabBarChart);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const textfield = document.createElement(TagName.LfTextfield);
    const chart = document.createElement(TagName.LfChart);
    const tabbar = document.createElement(TagName.LfTabbar);

    let type: AnalyticsType;

    switch (node.comfyClass as NodeName) {
      case NodeName.colorAnalysis:
        chart.lfAxis = [TabBarChartIds.Intensity];
        chart.lfColors = [TabBarChartColors.Red, TabBarChartColors.Green, TabBarChartColors.Blue];
        chart.lfSeries = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfTypes = ['scatter'];
        grid.classList.add(TabBarChartCSS.GridNoDirectory);
        textfield.classList.add(TabBarChartCSS.DirectoryHidden);
        break;
      case NodeName.imageHistogram:
      case NodeName.lutGeneration:
        chart.lfAxis = [TabBarChartIds.Intensity];
        chart.lfColors = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfSeries = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfTypes = ['area'];
        grid.classList.add(TabBarChartCSS.GridNoDirectory);
        textfield.classList.add(TabBarChartCSS.DirectoryHidden);
        break;
      case NodeName.usageStatistics:
        type = 'usage';
        chart.lfAxis = [TabBarChartIds.Name];
        chart.lfSeries = [TabBarChartIds.Counter, TabBarChartIds.Counter];
        chart.lfTypes = ['area'];
        break;
    }

    tabbar.classList.add(TabBarChartCSS.Tabbar);
    tabbar.lfValue = null;
    tabbar.addEventListener(LfEventName.LfTabbar, (e) => EV_HANDLERS.tabbar(STATE.get(wrapper), e));

    textfield.classList.add(TabBarChartCSS.Directory);
    textfield.lfIcon = 'folder';
    textfield.lfLabel = 'Directory';
    textfield.lfStyling = 'flat';
    textfield.addEventListener(LfEventName.LfTextfield, (e) =>
      EV_HANDLERS.textfield(STATE.get(wrapper), e),
    );

    grid.classList.add(TabBarChartCSS.Grid);
    grid.appendChild(textfield);
    grid.appendChild(tabbar);
    grid.appendChild(chart);

    content.classList.add(TabBarChartCSS.Content);
    content.appendChild(grid);

    wrapper.appendChild(content);

    const options = tabBarChartFactory.options(wrapper);

    STATE.set(wrapper, {
      directory: '',
      elements: { chart, tabbar, textfield },
      node,
      selected: '',
      type,
      wrapper,
    });

    return { widget: createDOMWidget(CustomWidgetName.tabBarChart, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
