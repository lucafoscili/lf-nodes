import {
  LfDataDataset,
  LfDataNode,
  LfMasonryEventPayload,
  LfMultiInputEventPayload,
  LfSelectEventPayload,
  LfSliderEventPayload,
  LfTextfieldEventPayload,
  LfToggleEventPayload,
} from '@lf-widgets/foundations';
import type { createEventHandlers } from '../../helpers/imageEditor/events';
import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';

//#region CSS
const BASE_CSS_CLASS = 'lf-imageeditor';
export enum ImageEditorCSS {
  Content = BASE_CSS_CLASS,
  Widget = `${BASE_CSS_CLASS}__widget`,
  Actions = `${BASE_CSS_CLASS}__actions`,
  Grid = `${BASE_CSS_CLASS}__grid`,
  GridHasActions = `${BASE_CSS_CLASS}__grid--has-actions`,
  GridIsInactive = `${BASE_CSS_CLASS}__grid--is-inactive`,
  Settings = `${BASE_CSS_CLASS}__settings`,
  SettingsControls = `${BASE_CSS_CLASS}__settings__controls`,
  SettingsButtons = `${BASE_CSS_CLASS}__settings__buttons`,
}
//#endregion

//#region Widget
export type ImageEditor = Widget<CustomWidgetName.imageEditor>;
export type ImageEditorFactory = WidgetFactory<ImageEditorDeserializedValue, ImageEditorState>;
export type ImageEditorNormalizeCallback = NormalizeValueCallback<
  ImageEditorDeserializedValue | string
>;
//#endregion

//#region Value
export interface ImageEditorDatasetNavigationDirectory {
  raw?: string;
  relative?: string;
  resolved?: string;
  is_external?: boolean;
}

export type ImageEditorDeserializedValue = LfDataDataset;
//#endregion

//#region State
export interface ImageEditorState extends BaseWidgetState {
  elements: {
    actionButtons: ImageEditorActionButtons;
    controls: Partial<{
      [K in ImageEditorControlIds]: ImageEditorControlMap<K>;
    }>;
    grid: HTMLDivElement;
    imageviewer: HTMLLfImageviewerElement;
    settings: HTMLDivElement;
  };
  contextId?: string;
  filter: ImageEditorFilter;
  filterNodeId?: string;
  filterType: ImageEditorFilterType;
  lastBrushSettings: ImageEditorBrushSettings;
  directory?: ImageEditorDatasetNavigationDirectory;
  directoryValue?: string;
  hasAutoDirectoryLoad?: boolean;
  isSyncingDirectory?: boolean;
  isApiProcessing?: boolean;
  lastRequestedDirectory?: string;
  navigationManager?: NavigationManager;
  settingsStore?: Partial<
    Record<ImageEditorFilterType, Partial<Record<ImageEditorControlIds, ImageEditorControlValue>>>
  >;
  update: {
    preview: () => Promise<void>;
    snapshot: () => Promise<void>;
  };
  refreshDirectory?: (directory: string) => Promise<void>;
}
export interface PrepSettingsDeps {
  onMultiinput: (
    state: ImageEditorState,
    e: CustomEvent<LfMultiInputEventPayload>,
  ) => void | Promise<void>;
  onSelect: (state: ImageEditorState, e: CustomEvent<LfSelectEventPayload>) => void | Promise<void>;
  onSlider: (state: ImageEditorState, e: CustomEvent<LfSliderEventPayload>) => void | Promise<void>;
  onTextfield: (
    state: ImageEditorState,
    e: CustomEvent<LfTextfieldEventPayload>,
  ) => void | Promise<void>;
  onToggle: (state: ImageEditorState, e: CustomEvent<LfToggleEventPayload>) => void | Promise<void>;
}
export type PrepSettingsFn = (state: ImageEditorState, node: LfDataNode) => void;
export interface EventHandlerDeps {
  handleInterruptForState: (state: ImageEditorState) => Promise<void>;
  prepSettings: PrepSettingsFn;
}
export type EventHandlers = ReturnType<typeof createEventHandlers>;
export interface NavigationManager {
  loadRoots: () => Promise<void>;
  expandNode: (node: LfDataNode) => Promise<void>;
  handleTreeClick: (node: LfDataNode) => Promise<void>;
}
export interface NavigationMetadata {
  id: string;
  name: string;
  hasChildren: boolean;
  paths: {
    raw?: string;
    relative?: string;
    resolved?: string;
  };
  isRoot?: boolean;
}
//#endregion

//#region Dataset
export enum ImageEditorStatus {
  Completed = 'completed',
  Pending = 'pending',
}
export enum ImageEditorColumnId {
  Path = 'path',
  Status = 'status',
}
export interface ImageEditorDatasetNavigation {
  directory?: ImageEditorDatasetNavigationDirectory;
}
export interface ImageEditorBuildSelectionPayloadParams {
  dataset: ImageEditorDataset;
  index: number;
  nodes: ImageEditorDataset['nodes'];
  selectedShape?: LfMasonryEventPayload['selectedShape'];
  fallbackContextId?: string;
}
//#endregion

//#region U.I.
export interface ImageEditorActionButtons {
  interrupt?: HTMLLfButtonElement;
  resume?: HTMLLfButtonElement;
}
export enum ImageEditorIcons {
  Interrupt = 'x',
  Reset = 'refresh',
  Resume = 'check',
}
//#endregion

//#region Controls
export type ImageEditorUpdateCallback = (addSnapshot?: boolean, force?: boolean) => Promise<void>;
export enum ImageEditorControls {
  Canvas = 'canvas',
  Multiinput = 'multiinput',
  Select = 'select',
  Slider = 'slider',
  Textfield = 'textfield',
  Toggle = 'toggle',
}
export enum ImageEditorCanvasIds {
  B64Canvas = 'b64_canvas',
  Points = 'points',
}
export enum ImageEditorSliderIds {
  Amount = 'amount',
  Balance = 'balance',
  BlueChannel = 'b_channel',
  BlurKernelSize = 'blur_kernel_size',
  BlurSigma = 'blur_sigma',
  ClarityAmount = 'clarity_amount',
  DenoisePercentage = 'denoise_percentage',
  Cfg = 'cfg',
  ConditioningMix = 'conditioning_mix',
  Dilate = 'dilate',
  FocusPosition = 'focus_position',
  FocusSize = 'focus_size',
  Gamma = 'gamma',
  GreenChannel = 'g_channel',
  Intensity = 'intensity',
  Midpoint = 'midpoint',
  Opacity = 'opacity',
  RoiAlign = 'roi_align',
  RoiMinSize = 'roi_min_size',
  RoiPadding = 'roi_padding',
  Radius = 'radius',
  RedChannel = 'r_channel',
  SharpenAmount = 'sharpen_amount',
  Size = 'size',
  Sigma = 'sigma',
  Softness = 'softness',
  Steps = 'steps',
  Strength = 'strength',
  Threshold = 'threshold',
  UpsampleTarget = 'upsample_target',
  Feather = 'feather',
}
export enum ImageEditorTextfieldIds {
  Color = 'color',
  Highlights = 'highlights',
  NegativePrompt = 'negative_prompt',
  PositivePrompt = 'positive_prompt',
  Seed = 'seed',
  Shadows = 'shadows',
  Tint = 'tint',
}
export enum ImageEditorToggleIds {
  ApplyUnsharpMask = 'apply_unsharp_mask',
  ClipSoft = 'clip_soft',
  Localized = 'localized',
  ProtectSkin = 'protect_skin',
  RoiAuto = 'roi_auto',
  RoiAlignAuto = 'roi_align_auto',
  Shape = 'shape',
  Smooth = 'smoooth',
  SoftBlend = 'soft_blend',
  TransparentBackground = 'transparent_background',
  Vertical = 'vertical',
}
export enum ImageEditorSelectIds {
  Sampler = 'sampler',
  Scheduler = 'scheduler',
}
export type ImageEditorControlIds =
  | ImageEditorCanvasIds
  | ImageEditorSelectIds
  | ImageEditorSliderIds
  | ImageEditorTextfieldIds
  | ImageEditorToggleIds;
export type ImageEditorControlMap<ID extends ImageEditorControlIds> =
  ID extends ImageEditorCanvasIds
    ? HTMLLfCanvasElement
    : ID extends ImageEditorSelectIds
    ? HTMLLfSelectElement
    : ID extends ImageEditorSliderIds
    ? HTMLLfSliderElement
    : ID extends ImageEditorTextfieldIds
    ? HTMLLfMultiinputElement | HTMLLfTextfieldElement
    : ID extends ImageEditorToggleIds
    ? HTMLLfToggleElement
    : never;
export type ImageEditorControlValue = string | number | boolean;
export type ImageEditorFilterSettings = Partial<{
  [K in ImageEditorControlIds]: number | boolean | string | Array<{ x: number; y: number }>;
}>;
export interface ImageEditorBaseConfig<
  ID extends ImageEditorControlIds,
  V extends ImageEditorControlValue,
> {
  ariaLabel: string;
  defaultValue: V;
  id: ID;
  isMandatory?: boolean;
  title: string;
}
export interface ImageEditorCanvasConfig
  extends ImageEditorBaseConfig<ImageEditorSliderIds, number> {
  points: Array<{ x: number; y: number }>;
}
export interface ImageEditorMultiinputConfig
  extends ImageEditorBaseConfig<ImageEditorTextfieldIds, string> {
  allowFreeInput?: boolean;
  controlType: ImageEditorControls.Multiinput;
  maxHistory?: number;
  mode?: 'history' | 'tags';
}
export interface ImageEditorSelectConfig
  extends ImageEditorBaseConfig<ImageEditorSelectIds, string> {
  controlType: ImageEditorControls.Select;
  values: LfDataNode[];
}
export interface ImageEditorSliderConfig
  extends ImageEditorBaseConfig<ImageEditorSliderIds, number> {
  controlType: ImageEditorControls.Slider;
  max: string;
  min: string;
  step: string;
}
export interface ImageEditorTextfieldConfig
  extends ImageEditorBaseConfig<ImageEditorTextfieldIds, string> {
  controlType: ImageEditorControls.Textfield;
  type: 'color' | 'number' | 'text';
}
export interface ImageEditorToggleConfig
  extends ImageEditorBaseConfig<ImageEditorToggleIds, boolean> {
  controlType: ImageEditorControls.Toggle;
  off: string;
  on: string;
}
export type ImageEditorControlConfig =
  | ImageEditorCanvasConfig
  | ImageEditorMultiinputConfig
  | ImageEditorSelectConfig
  | ImageEditorSliderConfig
  | ImageEditorTextfieldConfig
  | ImageEditorToggleConfig;
export type ImageEditorSettingsFor = Partial<{
  [ImageEditorControls.Multiinput]: ImageEditorMultiinputConfig[];
  [ImageEditorControls.Select]: ImageEditorSelectConfig[];
  [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
  [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
  [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
}>;
//#endregion

//#region Filters
export interface ImageEditorFilterSettingsMap {
  blend: ImageEditorBlendSettings;
  bloom: ImageEditorBloomSettings;
  brightness: ImageEditorBrightnessSettings;
  brush: ImageEditorBrushSettings;
  backgroundRemover: ImageEditorBackgroundRemoverSettings;
  clarity: ImageEditorClaritySettings;
  contrast: ImageEditorContrastSettings;
  desaturate: ImageEditorDesaturateSettings;
  filmGrain: ImageEditorFilmGrainSettings;
  gaussianBlur: ImageEditorGaussianBlurSettings;
  inpaint: ImageEditorInpaintSettings;
  line: ImageEditorLineSettings;
  saturation: ImageEditorSaturationSettings;
  sepia: ImageEditorSepiaSettings;
  splitTone: ImageEditorSplitToneSettings;
  tiltShift: ImageEditorTiltShiftSettings;
  unsharpMask: ImageEditorUnsharpMaskSettings;
  vibrance: ImageEditorVibranceSettings;
  vignette: ImageEditorVignetteSettings;
}
export interface ImageEditorBackgroundRemoverSettings extends ImageEditorFilterSettings {
  color: string;
  transparent_background: boolean;
}
export interface ImageEditorBlendSettings extends ImageEditorFilterSettings {
  color: string;
  opacity: number;
}
export interface ImageEditorBloomSettings extends ImageEditorFilterSettings {
  threshold: number;
  radius: number;
  intensity: number;
  tint: string;
}
export interface ImageEditorBrightnessSettings extends ImageEditorFilterSettings {
  strength: number;
  gamma: number;
  localized: boolean;
  midpoint: number;
}
export interface ImageEditorBrushSettings extends ImageEditorFilterSettings {
  b64_canvas: string;
  color: string;
  opacity: number;
  size: number;
}
export interface ImageEditorClaritySettings extends ImageEditorFilterSettings {
  clarity_amount: number;
}
export interface ImageEditorContrastSettings extends ImageEditorFilterSettings {
  strength: number;
  localized: boolean;
  midpoint: number;
}
export interface ImageEditorDesaturateSettings extends ImageEditorFilterSettings {
  r_channel: number;
  g_channel: number;
  b_channel: number;
  strength: number;
}
export interface ImageEditorFilmGrainSettings extends ImageEditorFilterSettings {
  intensity: number;
  size: number;
  tint: string;
  soft_blend: boolean;
}
export interface ImageEditorGaussianBlurSettings extends ImageEditorFilterSettings {
  blur_kernel_size: number;
  blur_sigma: number;
}
export interface ImageEditorLineSettings extends ImageEditorFilterSettings {
  color: string;
  opacity: number;
  points: Array<{ x: number; y: number }>;
  size: number;
  smooth: boolean;
}
export interface ImageEditorSaturationSettings extends ImageEditorFilterSettings {
  intensity: number;
}
export interface ImageEditorSepiaSettings extends ImageEditorFilterSettings {
  intensity: number;
}
export interface ImageEditorSplitToneSettings extends ImageEditorFilterSettings {
  balance: number;
  highlights: string;
  intensity: number;
  shadows: string;
  softness: number;
}
export interface ImageEditorTiltShiftSettings extends ImageEditorFilterSettings {
  focus_position: number;
  focus_size: number;
  radius: number;
  smooth: boolean;
  vertical: boolean;
}
export interface ImageEditorUnsharpMaskSettings extends ImageEditorFilterSettings {
  amount: number;
  radius: number;
  sigma: number;
  threshold: number;
}
export interface ImageEditorVibranceSettings extends ImageEditorFilterSettings {
  intensity: number;
  clip_soft: boolean;
  protect_skin: boolean;
}
export interface ImageEditorVignetteSettings extends ImageEditorFilterSettings {
  intensity: number;
  radius: number;
  shape: boolean;
}
export interface ImageEditorInpaintSettings extends ImageEditorFilterSettings {
  apply_unsharp_mask?: boolean;
  b64_canvas: string;
  cfg: number;
  conditioning_mix?: number;
  denoise_percentage: number;
  dilate?: number;
  feather?: number;
  negative_prompt: string;
  positive_prompt: string;
  roi_align?: number;
  roi_align_auto?: boolean;
  roi_auto?: boolean;
  roi_min_size?: number;
  roi_padding?: number;
  sampler?: string;
  scheduler?: string;
  seed?: number;
  steps: number;
  upsample_target: number;
}
export enum ImageEditorBackgroundRemoverIds {
  Color = 'color',
  TransparentBackground = 'transparent_background',
}
export enum ImageEditorBlendIds {
  Opacity = 'opacity',
}
export enum ImageEditorBloomIds {
  Threshold = 'threshold',
  Radius = 'radius',
  Intensity = 'intensity',
  Tint = 'tint',
}
export enum ImageEditorBrightnessIds {
  Strength = 'strength',
  Gamma = 'gamma',
  Midpoint = 'midpoint',
  Localized = 'localized',
}
export enum ImageEditorBrushIds {
  B64Canvas = 'b64_canvas',
  Color = 'color',
  Opacity = 'opacity',
  Size = 'size',
}
export enum ImageEditorClarityIds {
  Amount = 'clarity_amount',
}
export enum ImageEditorContrastIds {
  Strength = 'strength',
  Localized = 'contrast',
  Midpoint = 'midpoint',
}
export enum ImageEditorDesaturateIds {
  RedChannel = 'r_channel',
  GreenChannel = 'g_channel',
  BlueChannel = 'b_channel',
  Strength = 'strength',
}
export enum ImageEditorFilmGrainIds {
  Intensity = 'intensity',
  Size = 'size',
  Tint = 'tint',
  SoftBlend = 'soft_blend',
}
export enum ImageEditorGaussianBlurIds {
  BlurKernelSize = 'blur_kernel_size',
  BlurSigma = 'blur_sigma',
}
export enum ImageEditorLineIds {
  Color = 'color',
  Opacity = 'opacity',
  Points = 'points',
  Size = 'size',
  Smooth = 'smooth',
}
export enum ImageEditorSaturationIds {
  Intensity = 'intensity',
}
export enum ImageEditorSepiaIds {
  Intensity = 'intensity',
}
export enum ImageEditorSplitToneIds {
  Balance = 'balance',
  Highlights = 'highlights',
  Intensity = 'intensity',
  Shadows = 'shadows',
  Softness = 'softness',
}
export enum ImageEditorTiltShiftIds {
  FocusPosition = 'focus_position',
  FocusSize = 'focus_size',
  Radius = 'radius',
  Smooth = 'smooth',
  Vertical = 'vertical',
}
export enum ImageEditorUnsharpMaskIds {
  Amount = 'amount',
  Radius = 'radius',
  Sigma = 'sigma',
  Threshold = 'threshold',
}
export enum ImageEditorVibranceIds {
  Intensity = 'intensity',
  ClipSoft = 'clip_soft',
  ProtectSkin = 'protect_skin',
}
export enum ImageEditorVignetteIds {
  Color = 'color',
  Intensity = 'intensity',
  Radius = 'radius',
  Shape = 'shape',
}
export enum ImageEditorInpaintIds {
  ApplyUnsharpMask = 'apply_unsharp_mask',
  B64Canvas = 'b64_canvas',
  Cfg = 'cfg',
  ConditioningMix = 'conditioning_mix',
  DenoisePercentage = 'denoise_percentage',
  Dilate = 'dilate',
  Feather = 'feather',
  NegativePrompt = 'negative_prompt',
  PositivePrompt = 'positive_prompt',
  RoiAuto = 'roi_auto',
  RoiPadding = 'roi_padding',
  RoiAlign = 'roi_align',
  RoiAlignAuto = 'roi_align_auto',
  RoiMinSize = 'roi_min_size',
  Sampler = 'sampler',
  Scheduler = 'scheduler',
  Seed = 'seed',
  Steps = 'steps',
  UpsampleTarget = 'upsample_target',
}
export type ImageEditorFilterType = keyof ImageEditorFilterSettingsMap;
export type ImageEditorDatasetDefaults = Partial<
  Record<ImageEditorFilterType, Partial<ImageEditorFilterSettingsMap[ImageEditorFilterType]>>
>;
export interface ImageEditorDatasetSelection {
  context_id?: string;
  index?: number;
  name?: string;
  node_id?: string;
  url?: string;
}
export type ImageEditorDataset = ImageEditorDeserializedValue & {
  context_id?: string;
  defaults?: ImageEditorDatasetDefaults;
  selection?: ImageEditorDatasetSelection;
  navigation?: ImageEditorDatasetNavigation;
};
export interface ImageEditorFilterDefinition<
  ImageEditorControlIdsEnum extends { [key: string]: string },
  ImageEditorSettings extends ImageEditorFilterSettings,
  ImageEditorConfigs extends ImageEditorSettingsFor,
> {
  controlIds: ImageEditorControlIdsEnum;
  configs: ImageEditorConfigs;
  hasCanvasAction?: boolean;
  settings: ImageEditorSettings;
}
export type ImageEditorBackgroundRemoverFilter = ImageEditorFilterDefinition<
  typeof ImageEditorBackgroundRemoverIds,
  ImageEditorBackgroundRemoverSettings,
  {
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
    [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorBlendFilter = ImageEditorFilterDefinition<
  typeof ImageEditorBlendIds,
  ImageEditorBlendSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
  }
>;
export type ImageEditorBloomFilter = ImageEditorFilterDefinition<
  typeof ImageEditorBloomIds,
  ImageEditorBloomSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
  }
>;
export type ImageEditorBrightnessFilter = ImageEditorFilterDefinition<
  typeof ImageEditorBrightnessIds,
  ImageEditorBrightnessSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorBrushFilter = ImageEditorFilterDefinition<
  typeof ImageEditorBrushIds,
  ImageEditorBrushSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
  }
>;
export type ImageEditorClarityFilter = ImageEditorFilterDefinition<
  typeof ImageEditorClarityIds,
  ImageEditorClaritySettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
  }
>;
export type ImageEditorContrastFilter = ImageEditorFilterDefinition<
  typeof ImageEditorContrastIds,
  ImageEditorContrastSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorDesaturateFilter = ImageEditorFilterDefinition<
  typeof ImageEditorDesaturateIds,
  ImageEditorDesaturateSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
  }
>;
export type ImageEditorFilmGrainFilter = ImageEditorFilterDefinition<
  typeof ImageEditorFilmGrainIds,
  ImageEditorFilmGrainSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
    [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorGaussianBlurFilter = ImageEditorFilterDefinition<
  typeof ImageEditorGaussianBlurIds,
  ImageEditorGaussianBlurSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
  }
>;
export type ImageEditorLineFilter = ImageEditorFilterDefinition<
  typeof ImageEditorLineIds,
  ImageEditorLineSettings,
  {
    [ImageEditorControls.Canvas]: ImageEditorCanvasConfig[];
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
    [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorSaturationFilter = ImageEditorFilterDefinition<
  typeof ImageEditorSaturationIds,
  ImageEditorSaturationSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
  }
>;
export type ImageEditorSepiaFilter = ImageEditorFilterDefinition<
  typeof ImageEditorSepiaIds,
  ImageEditorSepiaSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
  }
>;
export type ImageEditorSplitToneFilter = ImageEditorFilterDefinition<
  typeof ImageEditorSplitToneIds,
  ImageEditorSplitToneSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
  }
>;
export type ImageEditorTiltShiftFilter = ImageEditorFilterDefinition<
  typeof ImageEditorTiltShiftIds,
  ImageEditorTiltShiftSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorUnsharpMaskFilter = ImageEditorFilterDefinition<
  typeof ImageEditorUnsharpMaskIds,
  ImageEditorUnsharpMaskSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
  }
>;
export type ImageEditorVibranceFilter = ImageEditorFilterDefinition<
  typeof ImageEditorVibranceIds,
  ImageEditorVibranceSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorVignetteFilter = ImageEditorFilterDefinition<
  typeof ImageEditorVignetteIds,
  ImageEditorVignetteSettings,
  {
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
    [ImageEditorControls.Toggle]: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorInpaintFilter = ImageEditorFilterDefinition<
  typeof ImageEditorInpaintIds,
  ImageEditorInpaintSettings,
  {
    [ImageEditorControls.Multiinput]?: ImageEditorMultiinputConfig[];
    [ImageEditorControls.Select]?: ImageEditorSelectConfig[];
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]?: ImageEditorTextfieldConfig[];
    [ImageEditorControls.Toggle]?: ImageEditorToggleConfig[];
  }
>;
export type ImageEditorFilters = {
  backgroundRemover: ImageEditorBackgroundRemoverFilter;
  blend: ImageEditorBlendFilter;
  bloom: ImageEditorBloomFilter;
  brightness: ImageEditorBrightnessFilter;
  brush: ImageEditorBrushFilter;
  clarity: ImageEditorClarityFilter;
  contrast: ImageEditorContrastFilter;
  desaturate: ImageEditorDesaturateFilter;
  filmGrain: ImageEditorFilmGrainFilter;
  gaussianBlur: ImageEditorGaussianBlurFilter;
  inpaint: ImageEditorInpaintFilter;
  line: ImageEditorLineFilter;
  saturation: ImageEditorSaturationFilter;
  sepia: ImageEditorSepiaFilter;
  splitTone: ImageEditorSplitToneFilter;
  tiltShift: ImageEditorTiltShiftFilter;
  unsharpMask: ImageEditorUnsharpMaskFilter;
  vibrance: ImageEditorVibranceFilter;
  vignette: ImageEditorVignetteFilter;
};
export type ImageEditorFilter =
  | ImageEditorBackgroundRemoverFilter
  | ImageEditorBlendFilter
  | ImageEditorBloomFilter
  | ImageEditorBrightnessFilter
  | ImageEditorBrushFilter
  | ImageEditorClarityFilter
  | ImageEditorContrastFilter
  | ImageEditorDesaturateFilter
  | ImageEditorFilmGrainFilter
  | ImageEditorGaussianBlurFilter
  | ImageEditorInpaintFilter
  | ImageEditorLineFilter
  | ImageEditorSaturationFilter
  | ImageEditorSepiaFilter
  | ImageEditorSplitToneFilter
  | ImageEditorTiltShiftFilter
  | ImageEditorUnsharpMaskFilter
  | ImageEditorVibranceFilter
  | ImageEditorVignetteFilter;
export type ImageEditorRequestSettings<T extends ImageEditorFilterType> =
  ImageEditorFilterSettingsMap[T] & { context_id?: string };
export type ImageEditorSetting =
  | ImageEditorBackgroundRemoverSettings
  | ImageEditorBlendSettings
  | ImageEditorBloomSettings
  | ImageEditorBrightnessSettings
  | ImageEditorBrushSettings
  | ImageEditorClaritySettings
  | ImageEditorContrastSettings
  | ImageEditorDesaturateSettings
  | ImageEditorFilmGrainSettings
  | ImageEditorGaussianBlurSettings
  | ImageEditorInpaintSettings
  | ImageEditorLineSettings
  | ImageEditorSaturationSettings
  | ImageEditorSepiaSettings
  | ImageEditorSplitToneSettings
  | ImageEditorTiltShiftSettings
  | ImageEditorUnsharpMaskSettings
  | ImageEditorVibranceSettings
  | ImageEditorVignetteSettings;
//#endregion
