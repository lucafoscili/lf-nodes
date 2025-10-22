import { LfMessengerDataset } from '@lf-widgets/foundations';
import { LogSeverity } from '../types/manager/manager';
import { ChipState } from '../types/widgets/chip';
import { ImageEditorState } from '../types/widgets/imageEditor';
import { MessengerCSS, MessengerState } from '../types/widgets/messenger';
import {
  ComfyWidgetName,
  CustomWidgetName,
  GenericWidget,
  NodeName,
  NodeWidgetMap,
} from '../types/widgets/widgets';
import {
  areJSONEqual,
  getApiRoutes,
  getCustomWidget,
  getInput,
  getLfManager,
  isValidJSON,
  refreshChart,
  unescapeJson,
} from '../utils/common';

//#region Node-Widget map
export const NODE_WIDGET_MAP: NodeWidgetMap = {
  LF_BackgroundRemover: [CustomWidgetName.compare],
  LF_Blend: [CustomWidgetName.compare],
  LF_BlobToImage: [CustomWidgetName.code],
  LF_Bloom: [CustomWidgetName.compare],
  LF_BlurImages: [CustomWidgetName.masonry],
  LF_Boolean: [CustomWidgetName.history],
  LF_Brightness: [CustomWidgetName.compare],
  LF_Brush: [CustomWidgetName.compare],
  LF_CaptionImageWD14: [CustomWidgetName.countBarChart],
  LF_CharacterImpersonator: [CustomWidgetName.code],
  LF_CheckpointSelector: [CustomWidgetName.card],
  LF_CivitAIMetadataSetup: [CustomWidgetName.code],
  LF_Clarity: [CustomWidgetName.compare],
  LF_ColorAnalysis: [CustomWidgetName.tabBarChart],
  LF_CompareImages: [CustomWidgetName.compare],
  LF_Contrast: [CustomWidgetName.compare],
  LF_ControlPanel: [CustomWidgetName.controlPanel],
  LF_CreateMask: [CustomWidgetName.compare],
  LF_DetectRegions: [CustomWidgetName.compare],
  LF_Desaturation: [CustomWidgetName.compare],
  LF_DiffusionModelSelector: [CustomWidgetName.card],
  LF_DisplayBoolean: [CustomWidgetName.code],
  LF_DisplayFloat: [CustomWidgetName.code],
  LF_DisplayInteger: [CustomWidgetName.code],
  LF_DisplayJSON: [CustomWidgetName.code],
  LF_DisplayPrimitiveAsJSON: [CustomWidgetName.code],
  LF_DisplayString: [CustomWidgetName.code],
  LF_EmbeddingSelector: [CustomWidgetName.card],
  LF_EmptyImage: [CustomWidgetName.masonry],
  LF_ExtractFaceEmbedding: [CustomWidgetName.code],
  LF_ExtractPromptFromLoraTag: [CustomWidgetName.code],
  LF_ExtractString: [CustomWidgetName.code],
  LF_FilmGrain: [CustomWidgetName.compare],
  LF_Float: [CustomWidgetName.history],
  LF_GaussianBlur: [CustomWidgetName.compare],
  LF_GeminiAPI: [CustomWidgetName.code],
  LF_GetRandomKeyFromJSON: [CustomWidgetName.code],
  LF_GetValueFromJSON: [CustomWidgetName.code],
  LF_ImageClassifier: [CustomWidgetName.code],
  LF_ImageHistogram: [CustomWidgetName.tabBarChart],
  LF_ImageListFromJSON: [CustomWidgetName.masonry],
  LF_ImagesEditingBreakpoint: [CustomWidgetName.imageEditor],
  LF_ImagesSlideshow: [CustomWidgetName.carousel],
  LF_ImageToSVG: [CustomWidgetName.compare],
  LF_Inpaint: [CustomWidgetName.compare],
  LF_InpaintAdvanced: [CustomWidgetName.compare],
  LF_Integer: [CustomWidgetName.history],
  LF_IsLandscape: [CustomWidgetName.tree],
  LF_JSONPromptCombinator: [CustomWidgetName.code],
  LF_KeywordCounter: [CustomWidgetName.countBarChart],
  LF_KeywordToggleFromJSON: [CustomWidgetName.chip],
  LF_Line: [CustomWidgetName.compare],
  LF_LLMChat: [CustomWidgetName.chat],
  LF_LLMMessenger: [CustomWidgetName.messenger],
  LF_LoadAndEditImages: [CustomWidgetName.imageEditor],
  LF_LoadFileOnce: [CustomWidgetName.history],
  LF_LoadCLIPSegModel: [CustomWidgetName.code],
  LF_LoadWD14Model: [CustomWidgetName.code],
  LF_LoadImages: [CustomWidgetName.masonry],
  LF_LoadLoraTags: [CustomWidgetName.cardsWithChip],
  LF_LoadMetadata: [CustomWidgetName.code, CustomWidgetName.upload],
  LF_LoraAndEmbeddingSelector: [CustomWidgetName.card],
  LF_LoraSelector: [CustomWidgetName.card],
  LF_LUTApplication: [CustomWidgetName.compare],
  LF_LUTGeneration: [CustomWidgetName.tabBarChart],
  LF_MarkdownDocGenerator: [CustomWidgetName.code],
  LF_MathOperation: [CustomWidgetName.code],
  LF_MultipleImageResizeForWeb: [CustomWidgetName.tree],
  LF_Notify: [],
  LF_ParsePromptWithLoraTags: [CustomWidgetName.code],
  LF_RandomBoolean: [CustomWidgetName.progressbar],
  LF_RegexReplace: [CustomWidgetName.code],
  LF_RegionExtractor: [CustomWidgetName.code],
  LF_RegionMask: [CustomWidgetName.compare],
  LF_ResizeImageByEdge: [CustomWidgetName.tree],
  LF_ResizeImageToDimension: [CustomWidgetName.tree],
  LF_ResizeImageToSquare: [CustomWidgetName.tree],
  LF_ResolutionSwitcher: [CustomWidgetName.progressbar],
  LF_SamplerSelector: [CustomWidgetName.history],
  LF_Saturation: [CustomWidgetName.compare],
  LF_SaveImageForCivitAI: [CustomWidgetName.masonry],
  LF_SaveJSON: [CustomWidgetName.tree],
  LF_SaveMarkdown: [CustomWidgetName.tree],
  LF_SaveSVG: [CustomWidgetName.masonry],
  LF_SaveText: [CustomWidgetName.tree],
  LF_SchedulerSelector: [CustomWidgetName.history],
  LF_Sepia: [CustomWidgetName.compare],
  LF_SequentialSeedsGenerator: [CustomWidgetName.history],
  LF_SetValueInJSON: [CustomWidgetName.code],
  LF_ShuffleJSONKeys: [CustomWidgetName.code],
  LF_Something2Number: [CustomWidgetName.code],
  LF_Something2String: [CustomWidgetName.code],
  LF_SortJSONKeys: [CustomWidgetName.code],
  LF_SortTags: [CustomWidgetName.code],
  LF_SplitTone: [CustomWidgetName.compare],
  LF_String: [CustomWidgetName.history],
  LF_StringReplace: [CustomWidgetName.code],
  LF_StringTemplate: [CustomWidgetName.code],
  LF_StringToJSON: [CustomWidgetName.code],
  LF_SwitchFloat: [CustomWidgetName.progressbar],
  LF_SwitchImage: [CustomWidgetName.progressbar],
  LF_SwitchInteger: [CustomWidgetName.progressbar],
  LF_SwitchJSON: [CustomWidgetName.progressbar],
  LF_SwitchMask: [CustomWidgetName.progressbar],
  LF_SwitchString: [CustomWidgetName.progressbar],
  LF_TiledSuperRes: [CustomWidgetName.compare],
  LF_TiltShift: [CustomWidgetName.compare],
  LF_UpdateUsageStatistics: [CustomWidgetName.code],
  LF_UpscaleModelSelector: [CustomWidgetName.history],
  LF_UsageStatistics: [CustomWidgetName.tabBarChart],
  LF_UrandomSeedGenerator: [CustomWidgetName.tree],
  LF_VAEDecode: [CustomWidgetName.code],
  LF_VAESelector: [CustomWidgetName.history],
  LF_ONNXSelector: [CustomWidgetName.history],
  LF_Vibrance: [CustomWidgetName.compare],
  LF_ViewImages: [CustomWidgetName.masonry],
  LF_ViewSVGs: [CustomWidgetName.masonry],
  LF_Vignette: [CustomWidgetName.compare],
  LF_WallOfText: [CustomWidgetName.code],
  LF_WriteJSON: [CustomWidgetName.textarea],
};
//#endregion

//#region onAfterGraphConfigured
/**
 * Accepts any class (not strictly requiring NodeType) to minimize casting at call sites.
 */
export const onAfterGraphConfigured = async <T extends abstract new (...args: any) => any>(
  ctor: T,
  cb: (instance: InstanceType<T>) => void,
) => {
  const proto = ctor.prototype;
  const original: (() => void) | undefined = proto.onAfterGraphConfigured;
  proto.onAfterGraphConfigured = function () {
    const r = original?.apply(this, arguments as any);
    try {
      cb(this as InstanceType<T>);
    } catch (err) {
      getLfManager()?.log?.('onAfterGraphConfigured hook error', { err }, LogSeverity.Warning);
    }
    return r as any;
  };
};
//#endregion

//#region onConnectionsChange
export const onConnectionsChange = async (nodeType: NodeType) => {
  const onConnectionsChange = nodeType.prototype.onConnectionsChange;
  nodeType.prototype.onConnectionsChange = function () {
    const r = onConnectionsChange?.apply(this, arguments);
    const node = this;

    switch (node.comfyClass) {
      case NodeName.keywordToggleFromJson:
        chipCb(node);
        break;

      case NodeName.llmMessenger:
        messengerCb(node);
        break;
    }

    return r;
  };
};
//#endregion

//#region onDrawBackground
export const onDrawBackground = async (nodeType: NodeType) => {
  const onDrawBackground = nodeType.prototype.onDrawBackground;
  nodeType.prototype.onDrawBackground = function () {
    const r = onDrawBackground?.apply(this, arguments);
    const node = this;

    refreshChart(node);

    return r;
  };
};
//#endregion

//#region onNodeCreated
export const onNodeCreated = async (nodeType: NodeType) => {
  const onNodeCreated = nodeType.prototype.onNodeCreated;

  nodeType.prototype.onNodeCreated = function () {
    const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : void 0;
    const node = this;

    for (let index = 0; index < node.widgets?.length; index++) {
      const w: GenericWidget = node.widgets[index];

      switch (w.type.toUpperCase()) {
        case CustomWidgetName.imageEditor:
          const ds = getApiRoutes().comfy.getDragAndScale();
          if (ds) {
            const onredraw = ds.onredraw;

            ds.onredraw = function () {
              const r = onredraw ? onredraw.apply(this, arguments) : void 0;
              const state = w.options.getState() as ImageEditorState;
              setCanvasSizeCb(state.elements.imageviewer);
              return r;
            };
          }
          break;
        case ComfyWidgetName.customtext:
        case ComfyWidgetName.string:
        case ComfyWidgetName.text:
          w.serializeValue = () => {
            const comfy = getApiRoutes().comfy.comfyUi();
            return comfy.utils.applyTextReplacements(comfy.app.app, w.value);
          };
          break;
      }
    }
    return r;
  };
};
//#endregion

//#region chipCb
const chipCb = (node: NodeType) => {
  const lfManager = getLfManager();
  const routes = getApiRoutes().comfy;
  const textarea = getInput(node, ComfyWidgetName.json);
  const linkInput = routes.getLinkById(textarea?.link?.toString());
  const nodeInput = routes.getNodeById(linkInput?.origin_id?.toString());
  if (!textarea || !linkInput || !nodeInput) {
    return;
  }
  const chipW = getCustomWidget(node, CustomWidgetName.chip);
  const datasetW = nodeInput?.widgets?.[linkInput.origin_slot];
  if (!chipW.options?.getState || !datasetW.options?.getValue) {
    lfManager.log('Missing options', { chipW, datasetW }, LogSeverity.Warning);
    return;
  }

  const dataset = datasetW.options.getValue();
  const chip = (chipW.options.getState() as ChipState).chip;
  try {
    const newData = unescapeJson(dataset).parsedJson;

    if (isValidJSON(newData) && isValidJSON(chip.lfDataset)) {
      if (!areJSONEqual(newData, chip.lfDataset)) {
        chip.lfDataset = newData;
        lfManager.log('Updated chip data', { dataset }, LogSeverity.Info);
      }
    } else {
      if (isValidJSON(newData)) {
        chip.lfDataset = newData;
        lfManager.log('Set chip data', { dataset }, LogSeverity.Info);
      } else {
        lfManager.log('Invalid JSON data', { dataset, error: 'Invalid JSON' }, LogSeverity.Warning);
      }
    }
  } catch (error) {
    lfManager.log('Error processing chip data', { dataset, error }, LogSeverity.Error);
  }
};
//#endregion

//#region messengerCb
const messengerCb = (node: NodeType) => {
  const textarea = getInput(node, ComfyWidgetName.json);
  const linkInput = getApiRoutes().comfy.getLinkById(textarea?.link?.toString());
  const nodeInput = getApiRoutes().comfy.getNodeById(linkInput?.origin_id?.toString());
  if (!textarea || !linkInput || !nodeInput) {
    return;
  }

  const messengerW = getCustomWidget(node, CustomWidgetName.messenger);
  const datasetW = nodeInput?.widgets?.[linkInput.origin_slot];
  if (!datasetW?.options?.getValue) {
    return;
  }

  const dataset = datasetW.options.getValue();
  const messenger = (messengerW?.options?.getState() as MessengerState).elements.messenger;
  try {
    const newData = unescapeJson(dataset).parsedJson;

    if (isValidJSON(newData) && isValidJSON(messenger.lfDataset)) {
      if (!areJSONEqual(newData, messenger.lfDataset)) {
        messenger.lfDataset = newData as unknown as LfMessengerDataset;
        messenger.reset();
        getLfManager().log('Updated messenger data', { dataset }, LogSeverity.Info);
      }
    } else {
      if (isValidJSON(newData)) {
        messenger.lfDataset = newData as unknown as LfMessengerDataset;
        messenger.reset();
        getLfManager().log('Set messenger data', { dataset }, LogSeverity.Info);
      } else {
        getLfManager().log(
          'Invalid JSON data',
          { dataset, error: 'Invalid JSON' },
          LogSeverity.Warning,
        );
      }
    }
    const placeholder = messenger.nextSibling || messenger.previousSibling;
    if (messenger.lfDataset?.nodes?.[0]) {
      (placeholder as HTMLDivElement).classList.add(MessengerCSS.PlaceholderHidden);
    } else {
      (placeholder as HTMLDivElement).classList.remove(MessengerCSS.PlaceholderHidden);
    }
  } catch (error) {
    getLfManager().log('Error processing messenger data', { dataset, error }, LogSeverity.Error);
  }
};
//#endregion

//#region setCanvasSizeCb
const setCanvasSizeCb = (imageviewer: HTMLLfImageviewerElement) => {
  requestAnimationFrame(async () => {
    try {
      const { canvas } = (await imageviewer.getComponents()).details;
      canvas?.resizeCanvas();
    } catch (error) {}
  });
};
//#endregion

//#region getLogStyle
export const getLogStyle = () => {
  return {
    fontFamily: 'var(--lf-font-family-monospace)',
    margin: '0',
    maxWidth: '100%',
    overflow: 'hidden',
    padding: '4px 8px',
    textOverflow: 'ellipsis',
  };
};
//#endregion
