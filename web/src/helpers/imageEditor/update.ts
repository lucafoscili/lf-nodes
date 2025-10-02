import { SETTINGS } from '../../fixtures/imageEditor';
import { LogSeverity } from '../../types/manager/manager';
import {
  ImageEditorBrushSettings,
  ImageEditorControlIds,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { getLfManager, isValidObject } from '../../utils/common';
import { apiCall } from './api';

//#region refreshValues
export const refreshValues = async (state: ImageEditorState, addSnapshot = false) => {
  const { elements, filter } = state;
  const { controls } = elements;

  const lfManager = getLfManager();

  state.settingsStore = state.settingsStore ?? {};
  const storeForFilter = (state.settingsStore[state.filterType] =
    state.settingsStore[state.filterType] ?? {});

  for (const key in controls) {
    if (Object.prototype.hasOwnProperty.call(controls, key)) {
      const id = key as ImageEditorControlIds;
      const control = controls[id];

      switch (control.tagName) {
        case 'LF-SLIDER': {
          const slider = control as HTMLLfSliderElement;
          const sliderValue = await slider.getValue();
          const value = addSnapshot ? sliderValue.real : sliderValue.display;
          filter.settings[id] = value;
          storeForFilter[id] = value;
          break;
        }
        case 'LF-TEXTFIELD': {
          const textfield = control as HTMLLfTextfieldElement;
          const textfieldValue = await textfield.getValue();
          filter.settings[id] = textfieldValue;
          storeForFilter[id] = textfieldValue;
          break;
        }
        case 'LF-TOGGLE': {
          const toggle = control as HTMLLfToggleElement;
          const toggleValue = await toggle.getValue();
          const value = toggleValue === 'on' ? toggle.dataset.on : toggle.dataset.off;
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
};
//#endregion

//#region updateCb
export const updateCb = async (state: ImageEditorState, addSnapshot = false, force = false) => {
  await refreshValues(state, addSnapshot);

  const { elements, filter } = state;
  const { imageviewer } = elements;
  const { settings } = filter;

  const validValues = isValidObject(settings);

  const isCanvasAction = settings.points || settings.b64_canvas;
  const isStroke = !filter || filter.hasCanvasAction;

  if (validValues && isStroke) {
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

  const shouldUpdate = !!(validValues && (!isStroke || (isStroke && isCanvasAction)));
  const requiresManualApply = !!filter?.requiresManualApply;

  let success = false;
  if (shouldUpdate && (force || !requiresManualApply)) {
    success = await apiCall(state, addSnapshot);
  }

  return success;
};
//#endregion
