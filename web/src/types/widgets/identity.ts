import { BaseWidgetState, CustomWidgetName, WidgetFactory } from './widgets';

const BASE_CSS_CLASS = 'lf-identity';

export enum IdentityCSS {
  Content = BASE_CSS_CLASS,
  Chip = `${BASE_CSS_CLASS}__chip`,
  Value = `${BASE_CSS_CLASS}__value`,
  Label = `${BASE_CSS_CLASS}__label`,
  Actions = `${BASE_CSS_CLASS}__actions`,
  Regenerate = `${BASE_CSS_CLASS}__regenerate`,
  Copy = `${BASE_CSS_CLASS}__copy`,
  Select = `${BASE_CSS_CLASS}__select`,
  Empty = `${BASE_CSS_CLASS}__empty`,
}

export type IdentityDeserializedValue = string;
export type Id = Widget<CustomWidgetName.id>;
export type Ref = Widget<CustomWidgetName.ref>;
export type IdFactory = WidgetFactory<IdentityDeserializedValue, IdentityState>;
export type RefFactory = WidgetFactory<IdentityDeserializedValue, IdentityState>;

export interface IdentityInputOptions {
  default?: unknown;
  lf_id_kind?: string;
  lf_ref_kind?: string;
  lf_label_widget?: string;
  [key: string]: unknown;
}

export interface IdentityCandidate {
  id: string;
  kind: string;
  label?: string;
  node: NodeType;
  inputName?: string;
  path?: string;
}

export interface IdentityState extends BaseWidgetState {
  chip?: HTMLButtonElement;
  inputName: string;
  kind: string;
  getLabel?: () => string;
  labelWidget?: string;
  refKind?: string;
  select?: HTMLSelectElement;
  selected: string;
  value: string;
  refresh?: () => void;
}
