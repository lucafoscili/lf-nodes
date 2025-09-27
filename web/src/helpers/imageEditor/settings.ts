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
  ImageEditorFilterType,
  ImageEditorIcons,
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
import { unescapeJson } from '../../utils/common';
import {
  beginManualApplyRequest,
  hasManualApplyPendingChanges,
  initManualApplyState,
  registerManualApplyChange,
} from './manualApply';
import { parseLabel } from './selectors';
import { updateCb } from './update';

//#region createPrepSettings
export const createPrepSettings = (deps: PrepSettingsDeps): PrepSettingsFn => {
  const { onSlider, onTextfield, onToggle } = deps;

  return (state, node) => {
    state.elements.controls = {};
    state.filter = unescapeJson(node.cells.lfCode.value).parsedJson as ImageEditorFilter;
    const idRaw = (node.id as string) || 'brush';
    const alias = idRaw === 'inpaint_detail' || idRaw === 'inpaint_adv' ? 'inpaint' : idRaw;
    state.filterType = alias as ImageEditorFilterType;
    state.manualApply = undefined;

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
      mutableSettings[id] = storedValue as never;
    });

    const { elements, filter } = state;
    const { settings } = elements;

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
        registerManualApplyChange(state);
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

    if (filter?.requiresManualApply) {
      const applyButton = document.createElement(TagName.LfButton);
      applyButton.lfIcon = ImageEditorIcons.Resume;
      applyButton.lfLabel = 'Apply';
      applyButton.lfStretchX = true;
      initManualApplyState(state, applyButton);
      applyButton.addEventListener('click', () => {
        if (!state.manualApply || state.manualApply.isProcessing) {
          return;
        }

        const hasPending = hasManualApplyPendingChanges(state);
        if (!hasPending) {
          return;
        }

        beginManualApplyRequest(state);
        void updateCb(state, true, true);
      });
      buttonsWrapper.appendChild(applyButton);
    }
  };
};
//#endregion

//#region resetSettings
export async function resetSettings(settings: HTMLElement) {
  const controls = Array.from(settings.querySelectorAll('[data-id]'));
  for (const control of controls) {
    switch (control.tagName) {
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
