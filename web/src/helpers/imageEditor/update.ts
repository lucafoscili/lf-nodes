import { SETTINGS } from '../../fixtures/imageEditor';
import { LogSeverity } from '../../types/manager/manager';
import {
  ImageEditorBrushSettings,
  ImageEditorControlIds,
  ImageEditorDataset,
  ImageEditorSetting,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { getLfManager, isValidObject } from '../../utils/common';
import { apiCall } from './api';
import { IMAGE_EDITOR_CONSTANTS } from './constants';

//#region refreshValues
export const refreshValues = async (state: ImageEditorState, addSnapshot = false) => {
  const { elements, filter } = state;
  const { controls, imageviewer } = elements;

  const lfManager = getLfManager();

  state.settingsStore = state.settingsStore ?? {};
  const storeForFilter = (state.settingsStore[state.filterType] =
    state.settingsStore[state.filterType] ?? {});

  for (const key in controls) {
    if (Object.prototype.hasOwnProperty.call(controls, key)) {
      const id = key as ImageEditorControlIds;
      const control = controls[id];

      switch (control.tagName) {
        case IMAGE_EDITOR_CONSTANTS.TAGS.SLIDER: {
          const slider = control as HTMLLfSliderElement;
          const sliderValue = await slider.getValue();
          const value = addSnapshot ? sliderValue.real : sliderValue.display;
          filter.settings[id] = value;
          storeForFilter[id] = value;
          break;
        }
        case IMAGE_EDITOR_CONSTANTS.TAGS.TEXTFIELD: {
          const textfield = control as HTMLLfTextfieldElement;
          const textfieldValue = await textfield.getValue();
          filter.settings[id] = textfieldValue;
          storeForFilter[id] = textfieldValue;
          break;
        }
        case IMAGE_EDITOR_CONSTANTS.TAGS.TOGGLE: {
          const toggle = control as HTMLLfToggleElement;
          const toggleValue = await toggle.getValue();
          const value =
            toggleValue === IMAGE_EDITOR_CONSTANTS.UI.ON ? toggle.dataset.on : toggle.dataset.off;
          filter.settings[id] = value;
          storeForFilter[id] = value;
          break;
        }
        default:
          lfManager.log(
            `Unhandled control type: ${control.tagName}`,
            { control },
            LogSeverity.Warning,
          );
          continue;
      }
    }
  }

  const dataset = imageviewer.lfDataset as ImageEditorDataset | undefined;
  if (dataset && state.filterType) {
    const defaults = (dataset.defaults = dataset.defaults ?? {});
    const existing = defaults[state.filterType] ?? {};
    defaults[state.filterType] = {
      ...existing,
      ...storeForFilter,
    } as ImageEditorSetting;
  }
};
//#endregion

//#region updateCb
export const updateCb = async (
  state: ImageEditorState,
  addSnapshot = false,
  fromCanvas = false,
) => {
  await refreshValues(state, addSnapshot);

  const { elements, filter } = state;
  const { imageviewer } = elements;

  if (!filter) {
    return false;
  }

  const { settings } = filter;
  const validValues = isValidObject(settings);

  const isCanvasAction = settings.points || settings.b64_canvas;
  const hasCanvasAction = filter.hasCanvasAction;

  if (validValues && hasCanvasAction) {
    const canvas = (await imageviewer.getComponents()).details.canvas;
    const brushDefaults = {
      ...SETTINGS.brush.settings,
      ...state.lastBrushSettings,
    };
    const candidateSettings = (settings ?? {}) as Partial<ImageEditorBrushSettings>;
    const brushSettings: ImageEditorBrushSettings = {
      ...brushDefaults,
      color: candidateSettings.color ?? brushDefaults.color,
      opacity: candidateSettings.opacity ?? brushDefaults.opacity,
      size: candidateSettings.size ?? brushDefaults.size,
    };

    canvas.lfColor = brushSettings.color;
    canvas.lfOpacity = brushSettings.opacity;
    canvas.lfSize = brushSettings.size;

    state.lastBrushSettings = {
      ...state.lastBrushSettings,
      color: brushSettings.color,
      opacity: brushSettings.opacity,
      size: brushSettings.size,
    };
  }

  // Only call API if:
  // 1. Settings are valid
  // 2. For canvas-based filters: must have actual canvas data (points or b64_canvas)
  // 3. For regular filters: just need valid settings
  const shouldUpdate = validValues && (!hasCanvasAction || isCanvasAction);
  let success = false;
  if (shouldUpdate && (!hasCanvasAction || fromCanvas)) {
    success = await apiCall(state, addSnapshot);
  }

  return success;
};
//#endregion
