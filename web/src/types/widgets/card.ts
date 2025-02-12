import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';

//#region CSS
const BASE_CSS_CLASS = 'lf-card';
export enum CardCSS {
  Content = BASE_CSS_CLASS,
  ContentHasButton = `${BASE_CSS_CLASS}--has-button`,
  Grid = `${BASE_CSS_CLASS}__grid`,
}
//#endregion

//#region Widget
export type Card = Widget<CustomWidgetName.card>;
export type CardFactory = WidgetFactory<CardDeserializedValue, CardState>;
export type CardNormalizeCallback = NormalizeValueCallback<CardDeserializedValue | string>;
//#endregion

//#region Value
export interface CardDeserializedValue {
  props: Partial<HTMLLfCardElement>[];
}
//#endregion

//#region State
export interface CardState extends BaseWidgetState {
  grid: HTMLDivElement;
}
//#endregion
