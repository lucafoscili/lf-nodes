import { LfMessengerConfig, LfMessengerDataset } from '@lf-widgets/foundations';
import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';

//#region CSS
const BASE_CSS_CLASS = 'lf-messenger';
export enum MessengerCSS {
  Content = BASE_CSS_CLASS,
  Widget = `${BASE_CSS_CLASS}__widget`,
  Placeholder = `${BASE_CSS_CLASS}__placeholder`,
  PlaceholderHidden = `${BASE_CSS_CLASS}__placeholder--hidden`,
}
//#endregion

//#region Widget
export type Messenger = Widget<CustomWidgetName.messenger>;
export type MessengerFactory = WidgetFactory<MessengerDeserializedValue, MessengerState>;
export type MessengerNormalizeCallback = NormalizeValueCallback<
  MessengerDeserializedValue | string
>;
//#endregion

//#region Value
export type MessengerDeserializedValue = {
  dataset: LfMessengerDataset;
  config: LfMessengerConfig;
};
//#endregion

//#region State
export interface MessengerState extends BaseWidgetState {
  config: LfMessengerConfig;
  elements: {
    messenger: HTMLLfMessengerElement;
    placeholder: HTMLDivElement;
  };
}
//#endregion
