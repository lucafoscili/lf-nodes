import {
  LfButtonEventPayload,
  LfCanvasEventPayload,
  LfEvent,
  LfImageviewerEventPayload,
  LfSliderEventPayload,
  LfTextfieldEventPayload,
  LfToggleEventPayload,
  LfTreeEventPayload,
} from '@lf-widgets/foundations';
import { SETTINGS } from '../../fixtures/imageEditor';
import {
  EventHandlerDeps,
  ImageEditorBrushFilter,
  ImageEditorIcons,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { NodeName } from '../../types/widgets/widgets';
import {
  canvasToBase64,
  debounce,
  getApiRoutes,
  isTree,
  LFInterruptFlags,
} from '../../utils/common';
import { registerManualApplyChange } from './manualApply';
import { updateCb } from './update';
/// @ts-ignore
import { api } from '/scripts/api.js';

export const createEventHandlers = ({
  handleInterruptForState,
  prepSettings,
}: EventHandlerDeps) => {
  const handlers = {
    //#region Button
    button: async (state: ImageEditorState, e: CustomEvent<LfButtonEventPayload>) => {
      const { comp, eventType } = e.detail;

      if (eventType === 'click') {
        const isPatched = api?.[LFInterruptFlags.PatchedInterrupt] === true;

        switch (comp.lfIcon) {
          case ImageEditorIcons.Interrupt:
            getApiRoutes().comfy.interrupt();
            if (!isPatched) {
              await handleInterruptForState(state);
            }
            break;
          case ImageEditorIcons.Resume:
            await handleInterruptForState(state);
            break;
          default:
            break;
        }
      }
    },
    //#endregion
    //#region Canvas
    canvas: async (state: ImageEditorState, e: CustomEvent<LfCanvasEventPayload>) => {
      const { comp, eventType, points } = e.detail;
      const { filter, filterType } = state;

      switch (eventType) {
        case 'stroke':
          const originalFilter = filter;
          const originalFilterType = filterType;
          const canvas = await comp.getCanvas();
          const b64Canvas = canvasToBase64(canvas);
          if (filterType !== 'brush' && !filter?.hasCanvasAction) {
            state.filterType = 'brush';
          }

          const brushDefaults = {
            ...SETTINGS.brush.settings,
            ...state.lastBrushSettings,
          };

          const temporaryFilter: ImageEditorBrushFilter = {
            ...JSON.parse(JSON.stringify(SETTINGS.brush)),
            settings: {
              ...brushDefaults,
              b64_canvas: b64Canvas,
              color: comp.lfColor ?? brushDefaults.color,
              opacity: comp.lfOpacity ?? brushDefaults.opacity,
              points,
              size: comp.lfSize ?? brushDefaults.size,
            },
          };
          state.filter = temporaryFilter;

          try {
            await updateCb(state, true, true);
          } finally {
            if (originalFilter?.hasCanvasAction) {
              const existingSettings =
                originalFilter.settings ?? ({} as typeof originalFilter.settings);
              originalFilter.settings = {
                ...existingSettings,
                b64_canvas: b64Canvas,
              };
            }
            state.filter = originalFilter;
            state.filterType = originalFilterType;
            await comp.clearCanvas();
          }
          break;
      }
    },
    //#endregion
    //#region Imageviewer
    imageviewer: async (state: ImageEditorState, e: CustomEvent<LfImageviewerEventPayload>) => {
      const { comp, eventType, originalEvent } = e.detail;
      const { node } = state;

      switch (eventType) {
        case 'lf-event': {
          const ogEv = originalEvent as LfEvent;
          switch (ogEv.detail.eventType) {
            case 'click':
              if (isTree(ogEv.detail.comp)) {
                const { node } = ogEv.detail as LfTreeEventPayload;
                if (node.cells?.lfCode) {
                  prepSettings(state, node);
                }
              }
              break;
            case 'stroke': {
              const canvasEv = ogEv as CustomEvent<LfCanvasEventPayload>;
              await handlers.canvas(state, canvasEv);
              break;
            }
          }
          break;
        }

        case 'ready': {
          const { navigation } = await comp.getComponents();
          switch (node.comfyClass) {
            case NodeName.imagesEditingBreakpoint:
              navigation.load.lfLabel = '';
              navigation.load.lfUiState = 'disabled';
              navigation.textfield.lfLabel = 'Previews are visible in your ComfyUI/temp folder';
              navigation.textfield.lfUiState = 'disabled';
              break;
            default:
              navigation.textfield.lfLabel = 'Directory (relative to ComfyUI/input)';
              break;
          }
          break;
        }
      }
    },
    //#endregion
    //#region Slider
    slider: async (state: ImageEditorState, e: CustomEvent<LfSliderEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { preview, snapshot } = update;

      switch (eventType) {
        case 'change':
          registerManualApplyChange(state);
          snapshot();
          break;
        case 'input':
          registerManualApplyChange(state);
          const debouncedSlider = debounce(preview, 300);
          debouncedSlider();
          break;
      }
    },
    //#endregion
    //#region Textfield
    textfield: async (state: ImageEditorState, e: CustomEvent<LfTextfieldEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { preview, snapshot } = update;

      switch (eventType) {
        case 'change':
          registerManualApplyChange(state);
          snapshot();
          break;
        case 'input':
          registerManualApplyChange(state);
          const debouncedTextfield = debounce(preview, 300);
          debouncedTextfield();
          break;
      }
    },
    //#endregion
    //#region Toggle
    toggle: async (state: ImageEditorState, e: CustomEvent<LfToggleEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { snapshot } = update;

      switch (eventType) {
        case 'change':
          registerManualApplyChange(state);
          snapshot();
          break;
      }
    },
    //#endregion
  } satisfies Record<string, unknown>;

  return handlers;
};
