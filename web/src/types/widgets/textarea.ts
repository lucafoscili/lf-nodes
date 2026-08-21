import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';
import { JsonIdPathPattern } from '../../helpers/visualNovel';

//#region CSS
const BASE_CSS_CLASS = 'lf-textarea';
export enum TextareaCSS {
  Content = BASE_CSS_CLASS,
  References = `${BASE_CSS_CLASS}__references`,
  Reference = `${BASE_CSS_CLASS}__reference`,
  ReferenceLabel = `${BASE_CSS_CLASS}__reference-label`,
  ReferenceSelect = `${BASE_CSS_CLASS}__reference-select`,
  Widget = `${BASE_CSS_CLASS}__widget`,
  WidgetError = `${BASE_CSS_CLASS}__widget--error`,
}
//#endregion

//#region Widget
export type Textarea = Widget<CustomWidgetName.textarea>;
export type TextareaFactory = WidgetFactory<TextareaDeserializedValue, TextareaState>;
export type TextareaNormalizeCallback = NormalizeValueCallback<TextareaDeserializedValue | string>;
//#endregion

//#region Value
/** LF_TEXTAREA serializes the authored JSON document as text. */
export type TextareaDeserializedValue = string;
//#endregion

//#region Authoring metadata
export interface TextareaReferencePathPattern {
  /** RFC 6901 path. `*` matches one array/object segment. */
  path: string;
  kind: string;
}
//#endregion

//#region State
export interface TextareaState extends BaseWidgetState {
  idPaths: JsonIdPathPattern[];
  inputName: string;
  references: HTMLDivElement;
  refPaths: TextareaReferencePathPattern[];
  textarea: HTMLTextAreaElement;
  validationTimer?: ReturnType<typeof setTimeout>;
}
//#endregion
