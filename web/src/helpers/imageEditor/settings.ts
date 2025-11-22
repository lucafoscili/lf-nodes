import { LfCanvasElement, LfDataDataset } from '@lf-widgets/foundations/dist';
import { MODELS_API } from '../../api/models';
import { SETTINGS } from '../../fixtures/imageEditor';
import { LfEventName } from '../../types/events/events';
import { LogSeverity } from '../../types/manager/manager';
import {
  ImageEditorBrushSettings,
  ImageEditorControlConfig,
  ImageEditorControlIds,
  ImageEditorControls,
  ImageEditorCSS,
  ImageEditorDataset,
  ImageEditorFilter,
  ImageEditorFilterType,
  ImageEditorIcons,
  ImageEditorMultiinputConfig,
  ImageEditorSelectConfig,
  ImageEditorSelectIds,
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
//#endregion

//#region createPrepSettings
export const createPrepSettings = (deps: PrepSettingsDeps): PrepSettingsFn => {
  const { onMultiinput, onSelect, onSlider, onTextfield, onToggle } = deps;

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

            controlsContainer.appendChild(textfield);
            state.elements.controls[textfieldConfig.id as ImageEditorTextfieldIds] = textfield;
            break;
          }
          case ImageEditorControls.Multiinput: {
            const multiConfig = config as ImageEditorMultiinputConfig;
            const multiinput = document.createElement(
              TagName.LfMultiinput,
            ) as HTMLLfMultiinputElement;

            multiinput.lfAllowFreeInput = multiConfig.allowFreeInput ?? true;
            multiinput.lfMaxHistory = 100;
            multiinput.lfMode = multiConfig.mode ?? 'tags';
            multiinput.lfTextfieldProps = { lfLabel: parseLabel(multiConfig) };
            multiinput.lfValue = String(multiConfig.defaultValue ?? '').valueOf();
            multiinput.title = multiConfig.title;
            multiinput.dataset.id = multiConfig.id;
            multiinput.addEventListener(LfEventName.LfMultiinput, (event) =>
              onMultiinput(state, event),
            );

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
          case ImageEditorControls.Select: {
            const selectConfig = config as ImageEditorSelectConfig;
            const select = document.createElement(TagName.LfSelect) as HTMLLfSelectElement;

            select.lfTextfieldProps = { lfLabel: parseLabel(selectConfig) };
            select.title = selectConfig.title;
            select.dataset.id = selectConfig.id;
            select.addEventListener(LfEventName.LfSelect, (event) => onSelect(state, event));

            const fallbackDataset: LfDataDataset = {
              nodes: selectConfig.values.map(({ id, value }) => ({
                id,
                value,
              })),
            };

            select.lfDataset = fallbackDataset;
            select.lfValue = String(selectConfig.defaultValue ?? '');

            if (
              selectConfig.id === ImageEditorSelectIds.Sampler ||
              selectConfig.id === ImageEditorSelectIds.Scheduler
            ) {
              (async () => {
                try {
                  const dataset =
                    selectConfig.id === ImageEditorSelectIds.Sampler
                      ? await MODELS_API.getSamplers()
                      : await MODELS_API.getSchedulers();

                  if (dataset && Array.isArray(dataset.nodes) && dataset.nodes.length > 0) {
                    select.lfDataset = dataset as LfDataDataset;

                    const targetValue = String(selectConfig.defaultValue ?? '');
                    if (targetValue) {
                      await select.setValue(targetValue);
                    }
                  }
                } catch (error) {
                  getLfManager().log(
                    'Failed to load sampling options for select control.',
                    { error, id: selectConfig.id },
                    LogSeverity.Warning,
                  );
                }
              })();
            }

            controlsContainer.appendChild(select);
            state.elements.controls[selectConfig.id as ImageEditorSelectIds] = select;
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
      case 'LF-SELECT': {
        const select = control as HTMLLfSelectElement;
        await select.setValue(String(select.lfValue ?? ''));
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
        case ImageEditorControls.Select: {
          const selectConfig = config as ImageEditorSelectConfig;
          const stringValue =
            defaultValue === null || typeof defaultValue === 'undefined'
              ? ''
              : String(defaultValue);
          selectConfig.defaultValue = stringValue;
          mutableSettings[selectConfig.id] = stringValue;
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
