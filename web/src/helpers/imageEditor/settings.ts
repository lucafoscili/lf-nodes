import { LfCanvasElement } from '@lf-widgets/foundations/dist';
import { SETTINGS } from '../../fixtures/imageEditor';
import { LfEventName } from '../../types/events/events';
import {
  ImageEditorBrushSettings,
  ImageEditorControlConfig,
  ImageEditorControlIds,
  ImageEditorControls,
  ImageEditorCSS,
  ImageEditorDataset,
  ImageEditorFilter,
  ImageEditorFilterSettings,
  ImageEditorFilterType,
  ImageEditorIcons,
  ImageEditorMultiinputConfig,
  ImageEditorSliderConfig,
  ImageEditorSliderIds,
  ImageEditorState,
  ImageEditorTextfieldConfig,
  ImageEditorTextfieldIds,
  ImageEditorToggleConfig,
  ImageEditorToggleIds,
  PrepSettingsDeps,
  PrepSettingsFn,
} from '../../types/widgets/imageEditor';
import { TagName } from '../../types/widgets/widgets';
import { getLfManager } from '../../utils/common';
import { IMAGE_EDITOR_CONSTANTS } from './constants';
import { parseLabel } from './selectors';

//#region Helpers
/**
 * Type guard function that validates whether the provided object conforms to the ImageEditorFilter interface.
 * It checks for the presence and correct types of required properties: `controlIds`, `configs`, and `settings`.
 * Additionally, it validates that `configs` contains valid control types from `ImageEditorControls`, each with an array of configurations
 * having `id`, `title`, and `defaultValue`. Optional property `hasCanvasAction` is checked for boolean type if present.
 *
 * @param obj - The unknown object to validate.
 * @returns `true` if the object is a valid `ImageEditorFilter`, otherwise `false`.
 */
function isValidImageEditorFilter(obj: unknown): obj is ImageEditorFilter {
  if (
    typeof obj !== 'object' ||
    obj === null ||
    !('controlIds' in obj) ||
    !('configs' in obj) ||
    !('settings' in obj)
  ) {
    return false;
  }

  const filter = obj as Record<string, unknown>;

  if (typeof filter.controlIds !== 'object' || filter.controlIds === null) {
    return false;
  }

  if (typeof filter.configs !== 'object' || filter.configs === null) {
    return false;
  }

  const configs = filter.configs as Record<string, unknown>;
  const validControlTypes = Object.values(ImageEditorControls);

  for (const [controlType, controlConfigs] of Object.entries(configs)) {
    if (!validControlTypes.includes(controlType as ImageEditorControls)) {
      return false;
    }

    if (!Array.isArray(controlConfigs)) {
      return false;
    }

    for (const config of controlConfigs) {
      if (
        typeof config !== 'object' ||
        config === null ||
        !('id' in config) ||
        !('title' in config) ||
        !('defaultValue' in config)
      ) {
        return false;
      }
    }
  }

  if (typeof filter.settings !== 'object' || filter.settings === null) {
    return false;
  }

  if ('hasCanvasAction' in filter && typeof filter.hasCanvasAction !== 'boolean') {
    return false;
  }

  return true;
}
function assertImageEditorFilter(obj: unknown): ImageEditorFilter {
  if (!isValidImageEditorFilter(obj)) {
    throw new Error('Invalid ImageEditorFilter structure');
  }
  return obj;
}
function assignStoredSetting(
  settings: ImageEditorFilter['settings'],
  controlIds: ImageEditorFilter['controlIds'],
  id: ImageEditorControlIds,
  value: unknown,
): void {
  const controlIdValues = Object.values(controlIds);
  if (!controlIdValues.includes(id as any)) {
    console.warn(`Control ID '${id}' not found in filter controlIds, skipping assignment`);
    return;
  }

  (settings as ImageEditorFilterSettings)[id] =
    value as ImageEditorFilterSettings[ImageEditorControlIds];
}
//#endregion

//#region createPrepSettings
export const createPrepSettings = (deps: PrepSettingsDeps): PrepSettingsFn => {
  const { onSlider, onTextfield, onToggle, onMultiinput } = deps;

  return (state, node) => {
    const { syntax } = getLfManager().getManagers().lfFramework;
    state.elements.controls = {};
    const parsed = syntax.json.unescape(node.cells.lfCode.value).parsedJSON;
    state.filter = assertImageEditorFilter(parsed);
    const idRaw = (node.id as string) || IMAGE_EDITOR_CONSTANTS.FILTERS.BRUSH;
    const alias =
      idRaw === IMAGE_EDITOR_CONSTANTS.FILTERS.INPAINT_DETAIL ||
      idRaw === IMAGE_EDITOR_CONSTANTS.FILTERS.INPAINT_ADV
        ? IMAGE_EDITOR_CONSTANTS.FILTERS.INPAINT
        : idRaw;
    state.filterType = alias as ImageEditorFilterType;
    state.filterNodeId = idRaw;

    const dataset = state.elements.imageviewer.lfDataset as ImageEditorDataset | undefined;
    const defaults = dataset?.defaults?.[state.filterType] as
      | Partial<Record<ImageEditorControlIds, unknown>>
      | undefined;
    if (defaults) {
      applyFilterDefaults(state, defaults);
    }

    state.settingsStore = state.settingsStore ?? {};
    const stored = state.settingsStore[state.filterType] ?? {};
    const mutableSettings = state.filter.settings;
    (Object.keys(stored) as ImageEditorControlIds[]).forEach((id) => {
      const storedValue = stored[id];
      if (typeof storedValue === 'undefined') {
        return;
      }
      assignStoredSetting(mutableSettings, state.filter.controlIds, id, storedValue);
    });

    const { elements, filter } = state;
    const { settings } = elements;

    if (!filter?.configs) {
      return;
    }

    settings.innerHTML = '';

    const controlsContainer = document.createElement(TagName.Div);
    controlsContainer.classList.add(ImageEditorCSS.SettingsControls);
    settings.appendChild(controlsContainer);
    const controlGroups = Object.keys(filter.configs) as ImageEditorControls[];
    controlGroups.forEach((controlType) => {
      const configs = filter.configs[controlType];
      if (!configs) {
        return;
      }

      configs.forEach((config: ImageEditorControlConfig) => {
        switch (controlType) {
          case ImageEditorControls.Slider: {
            const sliderConfig = config as ImageEditorSliderConfig;
            const slider = document.createElement(TagName.LfSlider);

            slider.lfLabel = parseLabel(sliderConfig);
            slider.lfLeadingLabel = true;
            slider.lfMax = Number(sliderConfig.max);
            slider.lfMin = Number(sliderConfig.min);
            slider.lfStep = Number(sliderConfig.step);
            slider.lfStyle = '.form-field { width: 100%; }';
            slider.lfValue = Number(sliderConfig.defaultValue);
            slider.title = sliderConfig.title;
            slider.dataset.id = sliderConfig.id;
            slider.addEventListener(LfEventName.LfSlider, (event) => onSlider(state, event));

            const storedValue = stored[sliderConfig.id as ImageEditorControlIds];
            if (typeof storedValue !== 'undefined') {
              slider.lfValue = Number(storedValue);
            }

            controlsContainer.appendChild(slider);
            state.elements.controls[sliderConfig.id as ImageEditorSliderIds] = slider;
            break;
          }
          case ImageEditorControls.Textfield: {
            const textfieldConfig = config as ImageEditorTextfieldConfig;
            const textfield = document.createElement(TagName.LfTextfield);

            textfield.lfLabel = parseLabel(textfieldConfig);
            textfield.lfHtmlAttributes = { type: textfieldConfig.type };
            textfield.lfValue = String(textfieldConfig.defaultValue).valueOf();
            textfield.title = textfieldConfig.title;
            textfield.dataset.id = textfieldConfig.id;
            textfield.addEventListener(LfEventName.LfTextfield, (event) =>
              onTextfield(state, event),
            );

            const storedValue = stored[textfieldConfig.id as ImageEditorControlIds];
            if (typeof storedValue !== 'undefined') {
              textfield.lfValue = String(storedValue);
            }

            controlsContainer.appendChild(textfield);
            state.elements.controls[textfieldConfig.id as ImageEditorTextfieldIds] = textfield;
            break;
          }
          case ImageEditorControls.Multiinput: {
            const multiConfig = config as ImageEditorMultiinputConfig;
            const multiinput = document.createElement(
              TagName.LfMultiinput,
            ) as HTMLLfMultiinputElement;

            multiinput.lfMode = multiConfig.mode ?? 'tags';
            multiinput.lfAllowFreeInput = multiConfig.allowFreeInput ?? true;
            multiinput.lfValue = String(multiConfig.defaultValue ?? '').valueOf();
            multiinput.title = multiConfig.title;
            multiinput.dataset.id = multiConfig.id;
            multiinput.addEventListener(LfEventName.LfMultiinput, (event) =>
              onMultiinput(state, event),
            );

            const storedValue = stored[multiConfig.id as ImageEditorControlIds];
            if (typeof storedValue !== 'undefined') {
              multiinput.lfValue = String(storedValue);
            }

            const effectiveValue = multiinput.lfValue ?? '';
            if (effectiveValue.trim()) {
              const tags = effectiveValue
                .split(',')
                .map((token) => token.trim())
                .filter((token) => token.length > 0);
              void multiinput.setHistory(tags);
            }

            controlsContainer.appendChild(multiinput);
            state.elements.controls[multiConfig.id as ImageEditorTextfieldIds] = multiinput;
            break;
          }
          case ImageEditorControls.Toggle: {
            const toggleConfig = config as ImageEditorToggleConfig;
            const toggle = document.createElement(TagName.LfToggle);

            toggle.dataset.off = toggleConfig.off;
            toggle.dataset.on = toggleConfig.on;
            toggle.lfLabel = parseLabel(toggleConfig);
            toggle.lfValue = toggleConfig.defaultValue ?? false;
            toggle.title = toggleConfig.title;
            toggle.dataset.id = toggleConfig.id;
            toggle.addEventListener(LfEventName.LfToggle, (event) => onToggle(state, event));

            const storedValue = stored[toggleConfig.id as ImageEditorControlIds];
            if (typeof storedValue !== 'undefined') {
              const boolValue =
                storedValue === true ||
                (typeof storedValue === 'string' && storedValue.toLowerCase() === 'true');
              toggle.lfValue = boolValue;
            }

            controlsContainer.appendChild(toggle);
            state.elements.controls[toggleConfig.id as ImageEditorToggleIds] = toggle;
            break;
          }
          default:
            throw new Error(`Unknown control type: ${controlType}`);
        }
      });
    });

    const buttonsWrapper = document.createElement(TagName.Div);
    buttonsWrapper.classList.add(ImageEditorCSS.SettingsButtons);
    settings.appendChild(buttonsWrapper);

    const resetButton = document.createElement(TagName.LfButton);
    resetButton.lfIcon = ImageEditorIcons.Reset;
    resetButton.lfLabel = 'Reset';
    resetButton.lfStretchX = true;
    resetButton.addEventListener('click', () => {
      void (async () => {
        await resetSettings(settings);
        await state.update.snapshot();
      })();
    });
    buttonsWrapper.appendChild(resetButton);

    if (state.filterType === 'brush') {
      const brushSettings = (state.filter.settings ?? {}) as ImageEditorBrushSettings;
      state.lastBrushSettings = {
        ...state.lastBrushSettings,
        ...JSON.parse(JSON.stringify(brushSettings)),
      };
    }

    if (filter?.hasCanvasAction) {
      requestAnimationFrame(async () => {
        const canvas = (await state.elements.imageviewer.getComponents()).details.canvas;
        const brushSource = {
          ...SETTINGS.brush.settings,
          ...state.lastBrushSettings,
          ...((state.filter.settings ?? {}) as Partial<ImageEditorBrushSettings>),
        };

        if (brushSource.color) {
          canvas.lfColor = brushSource.color;
        }
        if (typeof brushSource.opacity === 'number') {
          canvas.lfOpacity = brushSource.opacity;
        }
        if (typeof brushSource.size === 'number') {
          canvas.lfSize = brushSource.size;
        }
      });
    }
  };
};
//#endregion

//#region resetSettings
export async function resetSettings(settings: HTMLElement) {
  const controls = Array.from(settings.querySelectorAll('[data-id]'));
  for (const control of controls) {
    switch (control.tagName) {
      case 'LF-MULTIINPUT': {
        const multiinput = control as HTMLLfMultiinputElement;
        await multiinput.setValue(multiinput.lfValue);
        break;
      }
      case 'LF-SLIDER': {
        const slider = control as HTMLLfSliderElement;
        await slider.setValue(slider.lfValue);
        await slider.refresh();
        break;
      }
      case 'LF-TEXTFIELD': {
        const textfield = control as HTMLLfTextfieldElement;
        await textfield.setValue(textfield.lfValue);
        break;
      }
      case 'LF-TOGGLE': {
        const toggle = control as HTMLLfToggleElement;
        toggle.setValue(toggle.lfValue ? 'on' : 'off');
        break;
      }
    }
  }
}
//#endregion

//#region setBrush
export const setBrush = async (
  canvas: LfCanvasElement,
  lastBrushSettings: ImageEditorBrushSettings,
) => {
  if (canvas) {
    const { color, opacity, size } = lastBrushSettings;
    canvas.lfColor = color;
    canvas.lfOpacity = opacity;
    canvas.lfSize = size;
  }
};
//#endregion

//#region applyFilterDefaults
export const applyFilterDefaults = (
  state: ImageEditorState,
  defaults: Partial<Record<ImageEditorControlIds, unknown>>,
) => {
  const { filter } = state;
  if (!filter) {
    return;
  }

  const mutableSettings = filter.settings;

  (Object.keys(filter.configs) as ImageEditorControls[]).forEach((controlType) => {
    const configs = filter.configs[controlType];
    configs?.forEach((config) => {
      const defaultValue = defaults[config.id as ImageEditorControlIds];
      if (typeof defaultValue === 'undefined') {
        return;
      }

      switch (controlType) {
        case ImageEditorControls.Multiinput: {
          const multiConfig = config as ImageEditorMultiinputConfig;
          const stringValue =
            defaultValue === null || typeof defaultValue === 'undefined'
              ? ''
              : String(defaultValue);
          multiConfig.defaultValue = stringValue;
          mutableSettings[multiConfig.id] = stringValue;
          break;
        }
        case ImageEditorControls.Slider: {
          const sliderConfig = config as ImageEditorSliderConfig;
          const numericValue =
            typeof defaultValue === 'number' ? defaultValue : Number(defaultValue);
          sliderConfig.defaultValue = numericValue;
          mutableSettings[sliderConfig.id] = numericValue;
          break;
        }
        case ImageEditorControls.Textfield: {
          const textfieldConfig = config as ImageEditorTextfieldConfig;
          const stringValue =
            defaultValue === null || typeof defaultValue === 'undefined'
              ? ''
              : String(defaultValue);
          textfieldConfig.defaultValue = stringValue;
          mutableSettings[textfieldConfig.id] = stringValue;
          break;
        }
        case ImageEditorControls.Toggle: {
          const toggleConfig = config as ImageEditorToggleConfig;
          const boolValue =
            defaultValue === true ||
            (typeof defaultValue === 'string' && defaultValue.toLowerCase() === 'true');
          toggleConfig.defaultValue = boolValue;
          mutableSettings[toggleConfig.id] = boolValue ? toggleConfig.on : toggleConfig.off;
          break;
        }
      }
    });
  });
};
//#endregion
