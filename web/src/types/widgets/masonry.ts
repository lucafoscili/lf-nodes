import { LfDataDataset, LfMasonryColumns, LfMasonryView } from '@lf-widgets/foundations';
import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';

//#region CSS
const BASE_CSS_CLASS = 'lf-masonry';
export enum MasonryCSS {
  Content = BASE_CSS_CLASS,
  Slot = `${BASE_CSS_CLASS}__slot`,
  Widget = `${BASE_CSS_CLASS}__widget`,
}
//#endregion

//#region Widget
export type Masonry = Widget<CustomWidgetName.masonry>;
export type MasonryFactory = WidgetFactory<MasonryDeserializedValue, MasonryState>;
export type MasonryNormalizeCallback = NormalizeValueCallback<MasonryDeserializedValue | string>;
//#endregion

//#region Value
export interface MasonryAudioFile {
  filename: string;
  subfolder: string;
  type: 'output';
}
export interface MasonryFileIdentity {
  directory: string;
  relative_path: string;
}
export interface MasonryDeserializedValue {
  file_identity?: MasonryFileIdentity;
  audio?: MasonryAudioFile[];
  columns?: LfMasonryColumns;
  dataset: LfDataDataset;
  index?: number;
  name?: string;
  view?: LfMasonryView;
  slot_map?: { [slotName: string]: string };
}
//#endregion

//#region State
export interface MasonryState extends BaseWidgetState {
  audio?: MasonryAudioFile[];
  masonry: HTMLLfMasonryElement;
  selected: {
    file_identity?: MasonryFileIdentity;
    index?: number;
    name?: string;
  };
}
//#endregion
