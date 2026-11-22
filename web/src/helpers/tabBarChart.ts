import {
  LfDataDataset,
  LfDataNode,
  LfTabbarEventPayload,
  LfTextfieldEventPayload,
} from '@lf-widgets/foundations';
import { LogSeverity } from '../types/manager/manager';
import { TabBarChartDataset, TabBarChartState } from '../types/widgets/tabBarChart';
import { NodeName } from '../types/widgets/widgets';
import { getApiRoutes, getLfManager } from '../utils/common';

export const EV_HANDLERS = {
  //#region Tabbar handler
  tabbar: (state: TabBarChartState, e: CustomEvent<LfTabbarEventPayload>) => {
    const { eventType, node } = e.detail;

    const { elements } = state;
    const { chart } = elements;

    switch (eventType) {
      case 'click':
        switch (state.node.comfyClass) {
          case NodeName.usageStatistics:
            chart.lfDataset = getLfManager().getCachedDatasets().usage[node.id];
            break;
          default:
            applyChartDataset(chart, node.cells.lfChart.lfDataset);
            break;
        }
        break;
    }
  },
  //#endregion
  //#region Textfield handler
  textfield: (state: TabBarChartState, e: CustomEvent<LfTextfieldEventPayload>) => {
    const { eventType, value } = e.detail;

    switch (eventType) {
      case 'change':
        state.directory = value;
        apiCall(state);
        break;
    }
  },
  //#endregion
};

//#region apiCall
export const apiCall = async (state: TabBarChartState) => {
  const { directory, elements, selected, type } = state;
  const { chart, tabbar, textfield } = elements;

  getApiRoutes()
    .analytics.get(directory, type)
    .then((r) => {
      if (r.status === 'success') {
        if (r?.data && Object.entries(r.data).length > 0) {
          const firstKey = selected || Object.keys(r.data)[0];
          chart.lfDataset = r.data[firstKey];
          tabbar.lfDataset = prepareTabbarDataset(r.data, (filename) => filename.split('_')?.[0] || filename);

          requestAnimationFrame(async () => {
            if (directory !== (await textfield.getValue())) {
              textfield.setValue(directory);
            }
            tabbar.setValue(0);
          });
        } else {
          getLfManager().log('Analytics not found.', { r }, LogSeverity.Info);
        }
      }
    });
};
//#endregion

//#region applyChartDataset
/** Draw a dataset with its own layout when it carries one (lf-chart keeps the layout it loaded with otherwise). */
export const applyChartDataset = (chart: HTMLLfChartElement, dataset: TabBarChartDataset) => {
  const layout = dataset?.chart;
  if (layout) {
    chart.lfAxis = [layout.axis];
    chart.lfSeries = layout.series;
    chart.lfTypes = layout.types;
  }
  chart.lfDataset = dataset || {};
};
//#endregion

//#region prepareTabbarDataset
export const prepareTabbarDataset = (
  data: Record<string, LfDataDataset>,
  label: (key: string) => string = (key) => key,
) => {
  const dataset: LfDataDataset = { nodes: [] };
  for (const key in data) {
    if (Object.prototype.hasOwnProperty.call(data, key)) {
      const node: LfDataNode = {
        cells: { lfChart: { lfDataset: data[key], shape: 'chart', value: '' } },
        id: key,
        value: label(key),
      };
      dataset.nodes.push(node);
    }
  }
  return dataset;
};
//#endregion
