import { LfDataDataset } from '@lf-widgets/foundations';
import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';

//#region CSS
const BASE_CSS_CLASS = 'lf-compare';
export enum CompareCSS {
  Content = BASE_CSS_CLASS,
  Widget = `${BASE_CSS_CLASS}__widget`,
  WithSummary = `${BASE_CSS_CLASS}--summary`,
  Summary = `${BASE_CSS_CLASS}__summary`,
}
//#endregion

//#region Widget
export type Compare = Widget<CustomWidgetName.compare>;
export type CompareFactory = WidgetFactory<CompareDeserializedValue, CompareState>;
export type CompareNormalizeCallback = NormalizeValueCallback<CompareDeserializedValue | string>;
//#endregion

//#region Value
export type CompareDeserializedValue = LfDataDataset;
//#endregion

//#region State
export interface CompareState extends BaseWidgetState {
  compare: HTMLLfCompareElement;
  summary?: HTMLLfTreeElement;
}
//#endregion
