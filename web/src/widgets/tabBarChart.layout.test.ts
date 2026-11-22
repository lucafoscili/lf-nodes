import { beforeEach, describe, expect, it, vi } from 'vitest';
import { NODE_WIDGET_MAP } from '../helpers/manager';
import { EV_HANDLERS } from '../helpers/tabBarChart';
import { LFWidgets } from '../managers/widgets';
import { TabBarChartDeserializedValue, TabBarChartState } from '../types/widgets/tabBarChart';
import { CHART_RESULT_NODES, CustomWidgetName, NodeName } from '../types/widgets/widgets';
import { tabBarChartFactory } from './tabBarChart';

const MANAGER_SYMBOL = Symbol.for('__LfManager__');
const redraw = vi.fn();
const getNodeById = vi.fn();
type ChartNode = NodeType & { onExecuted?: (...args: unknown[]) => unknown };

const dataset = (axisTitle: string, series: string[], type: 'bar' | 'line') => ({
  columns: [
    { id: 'x', title: axisTitle },
    ...series.map((title, index) => ({ id: `s${index}`, shape: 'number', title })),
  ],
  nodes: [{ id: '0', cells: { x: { value: 'a' }, ...Object.fromEntries(series.map((_, index) => [`s${index}`, { value: index }])) } }],
  chart: { axis: 'x', series: series.map((_, index) => `s${index}`), types: series.map(() => type) },
});
const charts: TabBarChartDeserializedValue = {
  'Luma mean': dataset('Frame', ['face', 'hair'], 'bar'),
  'face_ratio, hair': dataset('Index', ['face_ratio'], 'line'),
};

const node = (comfyClass: NodeName, previous = vi.fn()): ChartNode =>
  ({
    id: '41',
    comfyClass,
    graph: { _nodes: [] },
    widgets: [],
    onExecuted: previous,
    addDOMWidget(name, type, element, options) {
      const widget = { name, type, element, options, serializeValue: () => options.getValue() };
      this.widgets.push(widget);
      return widget;
    },
  }) as ChartNode;

const stateOf = (chartNode: ChartNode) =>
  chartNode.widgets[0].options.getState() as TabBarChartState;

beforeEach(() => {
  vi.stubGlobal('requestAnimationFrame', () => 0);
  getNodeById.mockReset();
  (window as unknown as Record<PropertyKey, unknown>)[MANAGER_SYMBOL] = {
    log: vi.fn(),
    getApiRoutes: () => ({ comfy: { getNodeById, redraw } }),
    getManagers: () => ({
      lfFramework: {
        syntax: {
          json: {
            unescape: (value: unknown) => ({
              parsedJSON: typeof value === 'string' ? JSON.parse(value) : value,
            }),
          },
        },
      },
    }),
  };
});

describe('chart results drawn from their numbers', () => {
  it.each(CHART_RESULT_NODES)('%s registers the tab bar chart', (comfyClass) => {
    expect(NODE_WIDGET_MAP[comfyClass]).toEqual([CustomWidgetName.tabBarChart]);
  });

  it('draws the first tab with its own layout and names tabs as given', () => {
    const chartNode = node(NodeName.regionMeasure);
    const { widget } = tabBarChartFactory.render(chartNode);
    widget.options.setValue(JSON.stringify(charts));
    const { chart, tabbar } = stateOf(chartNode).elements;
    expect(chart.lfAxis).toEqual(['x']);
    expect(chart.lfSeries).toEqual(['s0', 's1']);
    expect(chart.lfTypes).toEqual(['bar', 'bar']);
    expect(chart.lfDataset).toEqual(charts['Luma mean']);
    expect(tabbar.lfDataset.nodes.map((tab) => tab.value)).toEqual(['Luma mean', 'face_ratio, hair']);
  });

  it('switches layout with the tab it shows', () => {
    const chartNode = node(NodeName.plotChart);
    const { widget } = tabBarChartFactory.render(chartNode);
    widget.options.setValue(JSON.stringify(charts));
    const state = stateOf(chartNode);
    const second = state.elements.tabbar.lfDataset.nodes[1];
    EV_HANDLERS.tabbar(state, new CustomEvent('lf-tabbar', { detail: { eventType: 'click', node: second } }) as never);
    expect(state.elements.chart.lfSeries).toEqual(['s0']);
    expect(state.elements.chart.lfTypes).toEqual(['line']);
    expect(state.elements.chart.lfDataset).toEqual(charts['face_ratio, hair']);
  });

  it.each(CHART_RESULT_NODES)('%s restores its charts from history', (comfyClass) => {
    const previous = vi.fn().mockReturnValue('previous result');
    const chartNode = node(comfyClass, previous);
    new LFWidgets().render(CustomWidgetName.tabBarChart)(chartNode);
    getNodeById.mockReturnValue(chartNode);
    expect(chartNode.onExecuted({ lf_output: [{ datasets: charts }] })).toBe('previous result');
    expect(stateOf(chartNode).elements.chart.lfDataset).toEqual(charts['Luma mean']);
  });
});
