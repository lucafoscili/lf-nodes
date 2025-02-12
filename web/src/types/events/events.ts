import { LfDataDataset } from '@lf-widgets/foundations';
import { CustomWidgetName, NodeName } from '../widgets/widgets';

// #region Common declarations
export type GenericPayload = WidgetPayloadFor<CustomWidgetName>;
export type GenericEvent = CustomEvent<GenericPayload>;
export interface BaseEventPayload {
  id: string;
}
export type EventCallback<T extends EventPayload<CustomWidgetName>> = (e: CustomEvent<T>) => void;
type ToKebabCase<S extends string> = S extends `${infer First}${infer Rest}`
  ? `${Lowercase<First>}${Rest extends Capitalize<Rest> ? '-' : ''}${ToKebabCase<Rest>}`
  : S;
export type KebabCaseNodeName<N extends NodeName> = N extends `LF_${infer Name}`
  ? `lf-${ToKebabCase<Name>}`
  : never;
export type EventName = {
  [N in NodeName]: KebabCaseNodeName<N>;
}[NodeName];
export type EventPayload<W extends CustomWidgetName> = WidgetPayloadMap[W];
export type WidgetPayloadFor<T extends CustomWidgetName> = WidgetPayloadMap[T];
export type WidgetPayloadMap = {
  [W in CustomWidgetName]: W extends CustomWidgetName.card
    ? CardPayload
    : W extends CustomWidgetName.cardsWithChip
    ? CardPayload
    : W extends CustomWidgetName.code
    ? StringPayload
    : W extends CustomWidgetName.compare
    ? SingleDatasetPayload
    : W extends CustomWidgetName.countBarChart
    ? MultiDatasetPayload
    : W extends CustomWidgetName.history
    ? SingleDatasetPayload
    : W extends CustomWidgetName.masonry
    ? MasonryPayload
    : W extends CustomWidgetName.progressbar
    ? ProgressbarPayload
    : W extends CustomWidgetName.tabBarChart
    ? MultiDatasetPayload
    : W extends CustomWidgetName.tree
    ? SingleDatasetPayload
    : W extends CustomWidgetName.upload
    ? StringPayload
    : BaseEventPayload;
};
export enum LfEventName {
  LfAccordion = 'lf-accordion-event',
  LfArticle = 'lf-article-event',
  LfButton = 'lf-button-event',
  LfCanvas = 'lf-canvas-event',
  LfCard = 'lf-card-event',
  LfCarousel = 'lf-carousel-event',
  LfChat = 'lf-chat-event',
  LfChart = 'lf-chart-event',
  LfChip = 'lf-chip-event',
  LfCode = 'lf-code-event',
  LfCompare = 'lf-compare-event',
  LfImageviewer = 'lf-imageviewer-event',
  LfList = 'lf-list-event',
  LfManager = 'lf-manager-ready',
  LfMasonry = 'lf-masonry-event',
  LfMessenger = 'lf-messenger-event',
  LfProgressbar = 'lf-progressbar-event',
  LfSlider = 'lf-slider-event',
  LfSpinner = 'lf-spinner-event',
  LfTabbar = 'lf-tabbar-event',
  LfTextfield = 'lf-textfield-event',
  LfToggle = 'lf-toggle-event',
  LfTree = 'lf-tree-event',
  LfUpload = 'lf-upload-event',
  Textarea = 'textarea-event',
}
// #endregion

// #region Card payload
export interface CardPayload extends BaseEventPayload {
  datasets: LfDataDataset[];
  apiFlags: boolean[];
  hashes: string[];
  paths: string[];
  chip?: LfDataDataset;
}
// #endregion

// #region Masonry payload
export interface MasonryPayload extends SingleDatasetPayload {
  index: number;
  name: string;
}
// #endregion

// #region Multi dataset payload
export interface MultiDatasetPayload extends BaseEventPayload {
  datasets: { [index: string]: LfDataDataset };
}
// #endregion

// #region Notify payload
export interface NotifyPayload extends BaseEventPayload {
  action: 'none' | 'focus tab' | 'interrupt' | 'interrupt and queue' | 'queue prompt';
  image: string;
  message: string;
  silent: boolean;
  tag: string;
  title: string;
}
// #endregion

// #region Progressbar payload
export interface ProgressbarPayload extends BaseEventPayload {
  bool: boolean;
  roll?: number;
}
// #endregion

// #region Dataset payload
export interface SingleDatasetPayload extends BaseEventPayload {
  dataset: LfDataDataset;
}
// #endregion

// #region String payload
export interface StringPayload extends BaseEventPayload {
  value: string;
}
// #endregion
