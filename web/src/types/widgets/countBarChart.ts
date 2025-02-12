import { LfDataDataset } from '@lf-widgets/foundations';
import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';

//#region CSS
const BASE_CSS_CLASS = 'lf-countbarchart';
export enum CountBarChartCSS {
  Content = BASE_CSS_CLASS,
  Widget = `${BASE_CSS_CLASS}__widget`,
}
//#endregion

//#region Count bar chart
export type CountBarChart = Widget<CustomWidgetName.countBarChart>;
export type CountBarChartFactory = WidgetFactory<
  CountBarChartDeserializedValue,
  CountBarChartState
>;
export type CountBarChartNormalizeCallback = NormalizeValueCallback<
  CountBarChartDeserializedValue | string
>;
//#endregion

//#region Value
export type CountBarChartDeserializedValue = {
  chart: LfDataDataset;
  chip: LfDataDataset;
};
//#endregion

//#region State
export interface CountBarChartState extends BaseWidgetState {
  card: HTMLLfCardElement;
  datasets: {
    chart: LfDataDataset;
    chip: LfDataDataset;
  };
}
//#endregion
