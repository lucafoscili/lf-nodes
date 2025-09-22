import { LfDataDataset } from '@lf-widgets/foundations';
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
  filter: ImageEditorFilter;
  filterType: ImageEditorFilterType;
  lastBrushSettings: ImageEditorBrushSettings;
  update: {
    preview: () => Promise<void>;
    snapshot: () => Promise<void>;
  };
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
  Slider = 'slider',
  Textfield = 'textfield',
  Toggle = 'toggle',
}
export enum ImageEditorCanvasIds {
  B64Canvas = 'b64_canvas',
  Points = 'points',
}
export enum ImageEditorSliderIds {
  Balance = 'balance',
  BlueChannel = 'b_channel',
  BlurKernelSize = 'blur_kernel_size',
  BlurSigma = 'blur_sigma',
  DenoisePercentage = 'denoise_percentage',
  FocusPosition = 'focus_position',
  FocusSize = 'focus_size',
  Gamma = 'gamma',
  GreenChannel = 'g_channel',
  Intensity = 'intensity',
  Midpoint = 'midpoint',
  Opacity = 'opacity',
  Radius = 'radius',
  RedChannel = 'r_channel',
  SharpenAmount = 'sharpen_amount',
  Size = 'size',
  Softness = 'softness',
  Steps = 'steps',
  Strength = 'strength',
  Threshold = 'threshold',
}
export enum ImageEditorTextfieldIds {
  Color = 'color',
  Highlights = 'highlights',
  NegativePrompt = 'negative_prompt',
  PositivePrompt = 'positive_prompt',
  Shadows = 'shadows',
  Tint = 'tint',
}
export enum ImageEditorToggleIds {
  ClipSoft = 'clip_soft',
  Localized = 'localized',
  ProtectSkin = 'protect_skin',
  Shape = 'shape',
  Smooth = 'smoooth',
  SoftBlend = 'soft_blend',
  Vertical = 'vertical',
}
export type ImageEditorControlIds =
  | ImageEditorCanvasIds
  | ImageEditorSliderIds
  | ImageEditorTextfieldIds
  | ImageEditorToggleIds;
export type ImageEditorControlMap<ID extends ImageEditorControlIds> =
  ID extends ImageEditorCanvasIds
    ? HTMLLfCanvasElement
    : ID extends ImageEditorSliderIds
    ? HTMLLfSliderElement
    : ID extends ImageEditorTextfieldIds
    ? HTMLLfTextfieldElement
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
  | ImageEditorSliderConfig
  | ImageEditorTextfieldConfig
  | ImageEditorToggleConfig;
export type ImageEditorSettingsFor = Partial<{
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
  clarity: ImageEditorClaritySettings;
  contrast: ImageEditorContrastSettings;
  desaturate: ImageEditorDesaturateSettings;
  filmGrain: ImageEditorFilmGrainSettings;
  gaussianBlur: ImageEditorGaussianBlurSettings;
  inpaint: ImageEditorInpaintSettings;
  line: ImageEditorLineSettings;
  sepia: ImageEditorSepiaSettings;
  splitTone: ImageEditorSplitToneSettings;
  tiltShift: ImageEditorTiltShiftSettings;
  vibrance: ImageEditorVibranceSettings;
  vignette: ImageEditorVignetteSettings;
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
  strength: number;
  sharpen_amount: number;
  blur_kernel_size: number;
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
  b64_canvas: string;
  denoise_percentage: number;
  negative_prompt: string;
  positive_prompt: string;
  steps: number;
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
  BlurKernelSize = 'blur_kernel_size',
  Strength = 'strength',
  SharpenAmount = 'sharpen_amount',
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
  B64Canvas = 'b64_canvas',
  DenoisePercentage = 'denoise_percentage',
  NegativePrompt = 'negative_prompt',
  PositivePrompt = 'positive_prompt',
  Steps = 'steps',
}
export type ImageEditorFilterType = keyof ImageEditorFilterSettingsMap;
export interface ImageEditorFilterDefinition<
  ImageEditorControlIdsEnum extends { [key: string]: string },
  ImageEditorSettings extends ImageEditorFilterSettings,
  ImageEditorConfigs extends ImageEditorSettingsFor,
> {
  controlIds: ImageEditorControlIdsEnum;
  configs: ImageEditorConfigs;
  hasCanvasAction?: boolean;
  requiresManualApply?: boolean;
  settings: ImageEditorSettings;
}
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
    [ImageEditorControls.Slider]: ImageEditorSliderConfig[];
    [ImageEditorControls.Textfield]: ImageEditorTextfieldConfig[];
  }
>;
export type ImageEditorFilters = {
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
  vibrance: ImageEditorVibranceFilter;
  vignette: ImageEditorVignetteFilter;
};
export type ImageEditorFilter =
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
  | ImageEditorVibranceFilter
  | ImageEditorVignetteFilter;

export type ImageEditorRequestSettings<T extends ImageEditorFilterType> =
  ImageEditorFilterSettingsMap[T] & { context_id?: string };
//#endregion
