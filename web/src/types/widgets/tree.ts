import { LfDataDataset } from '@lf-widgets/foundations';
import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';

//#region CSS
const BASE_CSS_CLASS = 'lf-tree';
export enum TreeCSS {
  Content = BASE_CSS_CLASS,
  Widget = `${BASE_CSS_CLASS}__widget`,
}
//#endregion

//#region Widget
export type Tree = Widget<CustomWidgetName.tree>;
export type TreeFactory = WidgetFactory<TreeDeserializedValue, TreeState>;
export type TreeNormalizeCallback = NormalizeValueCallback<TreeDeserializedValue | string>;
//#endregion

//#region Value
export type TreeDeserializedValue = LfDataDataset;
//#endregion

//#region State
export interface TreeState extends BaseWidgetState {
  tree: HTMLLfTreeElement;
}
//#endregion
