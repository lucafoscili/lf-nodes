import { Card, CardDeserializedValue } from './card';
import { CardsWithChip, CardsWithChipDeserializedValue } from './cardsWithChip';
import { Carousel, CarouselDeserializedValue } from './carousel';
import { Chat, ChatDeserializedValue } from './chat';
import { Chip, ChipDeserializedValue } from './chip';
import { Code, CodeDeserializedValue } from './code';
import { Compare, CompareDeserializedValue } from './compare';
import { ControlPanel, ControlPanelDeserializedValue } from './controlPanel';
import { CountBarChart, CountBarChartDeserializedValue } from './countBarChart';
import { History, HistoryDeserializedValue } from './history';
import { ImageEditor, ImageEditorDeserializedValue } from './imageEditor';
import { Masonry, MasonryDeserializedValue } from './masonry';
import { Messenger, MessengerDeserializedValue } from './messenger';
import { Progressbar, ProgressbarDeserializedValue } from './progressbar';
import { TabBarChart, TabBarChartDeserializedValue } from './tabBarChart';
import { Textarea, TextareaDeserializedValue } from './textarea';
import { Tree, TreeDeserializedValue } from './tree';
import { Upload, UploadDeserializedValue } from './upload';

//#region Enums
export enum ComfyWidgetName {
  boolean = 'BOOLEAN',
  combo = 'COMBO',
  customtext = 'CUSTOMTEXT',
  float = 'FLOAT',
  integer = 'INTEGER',
  json = 'JSON',
  number = 'NUMBER',
  seed = 'SEED',
  string = 'STRING',
  text = 'TEXT',
  toggle = 'TOGGLE',
}
export enum CustomWidgetName {
  card = 'LF_CARD',
  cardsWithChip = 'LF_CARDS_WITH_CHIP',
  carousel = 'LF_CAROUSEL',
  chat = 'LF_CHAT',
  chip = 'LF_CHIP',
  code = 'LF_CODE',
  compare = 'LF_COMPARE',
  controlPanel = 'LF_CONTROL_PANEL',
  countBarChart = 'LF_COUNT_BAR_CHART',
  history = 'LF_HISTORY',
  imageEditor = 'LF_IMAGE_EDITOR',
  masonry = 'LF_MASONRY',
  messenger = 'LF_MESSENGER',
  progressbar = 'LF_PROGRESSBAR',
  tabBarChart = 'LF_TAB_BAR_CHART',
  textarea = 'LF_TEXTAREA',
  tree = 'LF_TREE',
  upload = 'LF_UPLOAD',
}
export enum NodeName {
  backgroundRemover = 'LF_BackgroundRemover',
  blend = 'LF_Blend',
  blobToImage = 'LF_BlobToImage',
  bloom = 'LF_Bloom',
  blurImages = 'LF_BlurImages',
  boolean = 'LF_Boolean',
  brightness = 'LF_Brightness',
  brush = 'LF_Brush',
  captionImageWD14 = 'LF_CaptionImageWD14',
  characterImpersonator = 'LF_CharacterImpersonator',
  checkpointSelector = 'LF_CheckpointSelector',
  civitaiMetadataSetup = 'LF_CivitAIMetadataSetup',
  clarity = 'LF_Clarity',
  colorAnalysis = 'LF_ColorAnalysis',
  compareImages = 'LF_CompareImages',
  contrast = 'LF_Contrast',
  controlPanel = 'LF_ControlPanel',
  createMask = 'LF_CreateMask',
  detectRegions = 'LF_DetectRegions',
  desaturation = 'LF_Desaturation',
  diffusionModelSelector = 'LF_DiffusionModelSelector',
  displayBoolean = 'LF_DisplayBoolean',
  displayFloat = 'LF_DisplayFloat',
  displayInteger = 'LF_DisplayInteger',
  displayJson = 'LF_DisplayJSON',
  displayPrimitiveAsJson = 'LF_DisplayPrimitiveAsJSON',
  displayString = 'LF_DisplayString',
  markdownDocGenerator = 'LF_MarkdownDocGenerator',
  filmGrain = 'LF_FilmGrain',
  float = 'LF_Float',
  embeddingSelector = 'LF_EmbeddingSelector',
  emptyImage = 'LF_EmptyImage',
  extractFaceEmbedding = 'LF_ExtractFaceEmbedding',
  extractPromptFromLoraTag = 'LF_ExtractPromptFromLoraTag',
  extractString = 'LF_ExtractString',
  gaussianBlur = 'LF_GaussianBlur',
  getValueFromJson = 'LF_GetValueFromJSON',
  getRandomKeyFromJson = 'LF_GetRandomKeyFromJSON',
  imageClassifier = 'LF_ImageClassifier',
  imageListFromJSON = 'LF_ImageListFromJSON',
  imageHistogram = 'LF_ImageHistogram',
  imagesEditingBreakpoint = 'LF_ImagesEditingBreakpoint',
  imagesSlideshow = 'LF_ImagesSlideshow',
  imageToSvg = 'LF_ImageToSVG',
  inpaint = 'LF_Inpaint',
  inpaintAdvanced = 'LF_InpaintAdvanced',
  integer = 'LF_Integer',
  isLandscape = 'LF_IsLandscape',
  jsonPromptCombinator = 'LF_JSONPromptCombinator',
  keywordCounter = 'LF_KeywordCounter',
  keywordToggleFromJson = 'LF_KeywordToggleFromJSON',
  line = 'LF_Line',
  llmChat = 'LF_LLMChat',
  llmMessenger = 'LF_LLMMessenger',
  loadAndEditImages = 'LF_LoadAndEditImages',
  loadClipSegModel = 'LF_LoadCLIPSegModel',
  loadWd14Model = 'LF_LoadWD14Model',
  loadFileOnce = 'LF_LoadFileOnce',
  loadImages = 'LF_LoadImages',
  loadLoraTags = 'LF_LoadLoraTags',
  loadMetadata = 'LF_LoadMetadata',
  loraAndEmbeddingSelector = 'LF_LoraAndEmbeddingSelector',
  loraSelector = 'LF_LoraSelector',
  lutApplication = 'LF_LUTApplication',
  lutGeneration = 'LF_LUTGeneration',
  mathOperation = 'LF_MathOperation',
  multipleImageResizeForWeb = 'LF_MultipleImageResizeForWeb',
  notify = 'LF_Notify',
  parsePromptWithLoraTags = 'LF_ParsePromptWithLoraTags',
  randomBoolean = 'LF_RandomBoolean',
  regexReplace = 'LF_RegexReplace',
  regionExtractor = 'LF_RegionExtractor',
  regionMask = 'LF_RegionMask',
  resizeImageByEdge = 'LF_ResizeImageByEdge',
  resizeImageToDimension = 'LF_ResizeImageToDimension',
  resizeImageToSquare = 'LF_ResizeImageToSquare',
  resolutionSwitcher = 'LF_ResolutionSwitcher',
  samplerSelector = 'LF_SamplerSelector',
  saturation = 'LF_Saturation',
  saveImageForCivitai = 'LF_SaveImageForCivitAI',
  saveJson = 'LF_SaveJSON',
  saveMarkdown = 'LF_SaveMarkdown',
  saveText = 'LF_SaveText',
  schedulerSelector = 'LF_SchedulerSelector',
  sepia = 'LF_Sepia',
  sequentialSeedsGenerator = 'LF_SequentialSeedsGenerator',
  setValueInJson = 'LF_SetValueInJSON',
  shuffleJsonKeys = 'LF_ShuffleJSONKeys',
  something2Number = 'LF_Something2Number',
  something2String = 'LF_Something2String',
  sortJsonKeys = 'LF_SortJSONKeys',
  sortTags = 'LF_SortTags',
  splitTone = 'LF_SplitTone',
  string = 'LF_String',
  stringReplace = 'LF_StringReplace',
  stringTemplate = 'LF_StringTemplate',
  stringToJson = 'LF_StringToJSON',
  switchFloat = 'LF_SwitchFloat',
  switchImage = 'LF_SwitchImage',
  switchInteger = 'LF_SwitchInteger',
  switchJson = 'LF_SwitchJSON',
  switchString = 'LF_SwitchString',
  tiledSuperRes = 'LF_TiledSuperRes',
  tiltShift = 'LF_TiltShift',
  updateUsageStatistics = 'LF_UpdateUsageStatistics',
  upscaleModelSelector = 'LF_UpscaleModelSelector',
  urandomSeedGenerator = 'LF_UrandomSeedGenerator',
  usageStatistics = 'LF_UsageStatistics',
  vaeDecode = 'LF_VAEDecode',
  vaeSelector = 'LF_VAESelector',
  onnxSelector = 'LF_ONNXSelector',
  viewImages = 'LF_ViewImages',
  vibrance = 'LF_Vibrance',
  vignette = 'LF_Vignette',
  wallOfText = 'LF_WallOfText',
  writeJson = 'LF_WriteJSON',
}
export enum TagName {
  Div = 'div',
  LfAccordion = 'lf-accordion',
  LfArticle = 'lf-article',
  LfButton = 'lf-button',
  LfCard = 'lf-card',
  LfCarousel = 'lf-carousel',
  LfChat = 'lf-chat',
  LfChart = 'lf-chart',
  LfChip = 'lf-chip',
  LfCode = 'lf-code',
  LfCompare = 'lf-compare',
  LfImageviewer = 'lf-imageviewer',
  LfList = 'lf-list',
  LfMasonry = 'lf-masonry',
  LfMessenger = 'lf-messenger',
  LfProgressbar = 'lf-progressbar',
  LfSlider = 'lf-slider',
  LfSpinner = 'lf-spinner',
  LfTabbar = 'lf-tabbar',
  LfTextfield = 'lf-textfield',
  LfToggle = 'lf-toggle',
  LfTree = 'lf-tree',
  LfUpload = 'lf-upload',
  Textarea = 'textarea',
}
//#endregion

//#region Maps
export type ComfyWidgetMap = {
  [ComfyWidgetName.boolean]: ComfyWidget;
  [ComfyWidgetName.combo]: ComfyWidget;
  [ComfyWidgetName.customtext]: ComfyWidget;
  [ComfyWidgetName.float]: ComfyWidget;
  [ComfyWidgetName.integer]: ComfyWidget;
  [ComfyWidgetName.json]: ComfyWidget;
  [ComfyWidgetName.number]: ComfyWidget;
  [ComfyWidgetName.seed]: ComfyWidget;
  [ComfyWidgetName.string]: ComfyWidget;
  [ComfyWidgetName.text]: ComfyWidget;
  [ComfyWidgetName.toggle]: ComfyWidget;
};
export type CustomWidgetMap = {
  [CustomWidgetName.card]: Card;
  [CustomWidgetName.carousel]: Carousel;
  [CustomWidgetName.cardsWithChip]: CardsWithChip;
  [CustomWidgetName.chat]: Chat;
  [CustomWidgetName.chip]: Chip;
  [CustomWidgetName.code]: Code;
  [CustomWidgetName.compare]: Compare;
  [CustomWidgetName.controlPanel]: ControlPanel;
  [CustomWidgetName.countBarChart]: CountBarChart;
  [CustomWidgetName.history]: History;
  [CustomWidgetName.imageEditor]: ImageEditor;
  [CustomWidgetName.masonry]: Masonry;
  [CustomWidgetName.messenger]: Messenger;
  [CustomWidgetName.progressbar]: Progressbar;
  [CustomWidgetName.tabBarChart]: TabBarChart;
  [CustomWidgetName.textarea]: Textarea;
  [CustomWidgetName.tree]: Tree;
  [CustomWidgetName.upload]: Upload;
};
export type CustomWidgetDeserializedValuesMap<Name extends CustomWidgetName> = {
  [CustomWidgetName.card]: CardDeserializedValue;
  [CustomWidgetName.cardsWithChip]: CardsWithChipDeserializedValue;
  [CustomWidgetName.carousel]: CarouselDeserializedValue;
  [CustomWidgetName.chat]: ChatDeserializedValue;
  [CustomWidgetName.chip]: ChipDeserializedValue;
  [CustomWidgetName.code]: CodeDeserializedValue;
  [CustomWidgetName.compare]: CompareDeserializedValue;
  [CustomWidgetName.controlPanel]: ControlPanelDeserializedValue;
  [CustomWidgetName.countBarChart]: CountBarChartDeserializedValue;
  [CustomWidgetName.history]: HistoryDeserializedValue;
  [CustomWidgetName.imageEditor]: ImageEditorDeserializedValue;
  [CustomWidgetName.masonry]: MasonryDeserializedValue;
  [CustomWidgetName.messenger]: MessengerDeserializedValue;
  [CustomWidgetName.progressbar]: ProgressbarDeserializedValue;
  [CustomWidgetName.tabBarChart]: TabBarChartDeserializedValue;
  [CustomWidgetName.textarea]: TextareaDeserializedValue;
  [CustomWidgetName.tree]: TreeDeserializedValue;
  [CustomWidgetName.upload]: UploadDeserializedValue;
}[Name];
export type NodeWidgetMap = {
  [N in NodeName]: CustomWidgetName[];
};
//#endregion

//#region Helpers
export type ComfyWidget = Widget<ComfyWidgetName>;
export type CustomWidget = Card;
export type GenericWidget = ComfyWidget | CustomWidget;
export type UnescapeJSONPayload = {
  validJson: boolean;
  parsedJson?: {};
  unescapedStr: string;
};
export type NormalizeValueCallback<
  V extends CustomWidgetDeserializedValuesMap<CustomWidgetName>,
  S extends BaseWidgetState = BaseWidgetState,
> = (origValue: V, unescaped: UnescapeJSONPayload, state?: S) => void;
export type GenericWidgetCallback = ComfyWidgetCallback | CustomWidgetCallback;
export type CustomWidgetCallback = <T extends CustomWidgetName>(
  node: NodeType,
  name: T,
) => { widget: CustomWidget };
export type ComfyWidgetCallback = <T extends ComfyWidgetName>(
  node: NodeType,
  name: T,
) => { widget: ComfyWidget };
export interface WidgetFactory<
  V extends CustomWidgetDeserializedValuesMap<CustomWidgetName> = CustomWidgetDeserializedValuesMap<CustomWidgetName>,
  S extends BaseWidgetState = BaseWidgetState,
> {
  options: (wrapper: HTMLDivElement) => WidgetOptions<V, S>;
  render: (node: NodeType) => { widget: GenericWidget };
  state: WeakMap<HTMLDivElement, S>;
}
export interface WidgetOptions<
  V extends CustomWidgetDeserializedValuesMap<CustomWidgetName> = CustomWidgetDeserializedValuesMap<CustomWidgetName>,
  S extends BaseWidgetState = BaseWidgetState,
> {
  hideOnZoom: boolean;
  getState: () => S;
  getValue: () => V;
  setValue(value: string | V): void;
}
export interface BaseWidgetState {
  node: NodeType;
  wrapper: HTMLDivElement;
}
export type WidgetSetter = {
  [W in CustomWidgetName]: CustomWidgetCallback;
};
//#endregion
