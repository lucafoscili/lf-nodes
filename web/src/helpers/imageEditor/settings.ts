import { LfCanvasElement, LfDataDataset, LfDataNode } from '@lf-widgets/foundations/dist';
import { MODELS_API } from '../../api/models';
import { SETTINGS } from '../../fixtures/imageEditor/settings';
import { LfEventName } from '../../types/events/events';
import { LogSeverity } from '../../types/manager/manager';
import {
  ImageEditorBrushSettings,
  ImageEditorCheckboxConfig,
  ImageEditorCheckboxIds,
  ImageEditorControlConfig,
  ImageEditorControlIds,
  ImageEditorControls,
  ImageEditorCSS,
  ImageEditorDataset,
  ImageEditorFilter,
  ImageEditorFilterType,
  ImageEditorIcons,
  ImageEditorLayout,
  ImageEditorLayoutGroup,
  ImageEditorMultiinputConfig,
  ImageEditorSelectConfig,
  ImageEditorSelectIds,
  ImageEditorSettingsFor,
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

const layoutWarningFilters = new Set<string>();

//#region Helpers
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

export const updateResizeHelperText = async (state: ImageEditorState) => {
  try {
    const { canvas } = (await state.elements.imageviewer.getComponents()).details;
    const lfImage = await canvas.getImage();
    const domImg = (await lfImage.getImage()) as HTMLImageElement | null;
    const width = domImg?.naturalWidth || domImg?.width || 0;
    const height = domImg?.naturalHeight || domImg?.height || 0;

    const helperText = width && height ? `Current: ${width}x${height}px` : 'Current: unknown';

    if (state.filterType === 'resizeEdge') {
      const control = state.elements.controls[
        ImageEditorTextfieldIds.ResizeSizePx
      ] as HTMLLfTextfieldElement;

      if (control && control.tagName === 'LF-TEXTFIELD') {
        control.lfHelper = {
          value: helperText,
          showWhenFocused: false,
        };
      }
      return;
    }

    const assignHelper = (
      controlId: ImageEditorTextfieldIds.ResizeHeight | ImageEditorTextfieldIds.ResizeWidth,
    ) => {
      const control = state.elements.controls[controlId] as
        | HTMLLfTextfieldElement
        | HTMLLfMultiinputElement
        | undefined;

      if (control && control.tagName === 'LF-TEXTFIELD') {
        (control as HTMLLfTextfieldElement).lfHelper = {
          value: helperText,
          showWhenFocused: false,
        };
      }
    };

    assignHelper(ImageEditorTextfieldIds.ResizeHeight);
    assignHelper(ImageEditorTextfieldIds.ResizeWidth);
  } catch (error) {
    getLfManager().log('Failed to update resize helper text.', { error }, LogSeverity.Warning);
  }
};
//#endregion

//#region createPrepSettings
export const createPrepSettings = (deps: PrepSettingsDeps): PrepSettingsFn => {
  const { onMultiinput, onSelect, onSlider, onTextfield, onToggle, onCheckbox } = deps;

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

    const controlIndex = new Map<
      ImageEditorControlIds,
      { controlType: ImageEditorControls; config: ImageEditorControlConfig }
    >();

    (Object.keys(state.filter.configs ?? {}) as ImageEditorControls[]).forEach((controlType) => {
      const configs = state.filter.configs?.[controlType] as ImageEditorControlConfig[] | undefined;
      configs?.forEach((config) => {
        controlIndex.set(config.id as ImageEditorControlIds, { controlType, config });
      });
    });

    const defaultLayout = (): ImageEditorLayout => {
      const layout: ImageEditorLayout = [];
      (Object.keys(state.filter.configs ?? {}) as ImageEditorControls[]).forEach((controlType) => {
        const configs = state.filter.configs?.[controlType] as
          | ImageEditorControlConfig[]
          | undefined;
        configs?.forEach((config) => layout.push(config.id as ImageEditorControlIds));
      });
      return layout;
    };

    const layout = (state.filter as ImageEditorFilter & { layout?: ImageEditorLayout }).layout;
    const layoutToRender = layout ?? defaultLayout();
    if (!layout && !layoutWarningFilters.has(state.filterType)) {
      layoutWarningFilters.add(state.filterType);
      getLfManager().log(
        'Filter missing layout definition; falling back to config order.',
        { filterType: state.filterType },
        LogSeverity.Warning,
      );
    }

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
    const renderedControls = new Set<ImageEditorControlIds>();

    const renderControl = (controlId: ImageEditorControlIds, target: HTMLElement) => {
      if (renderedControls.has(controlId)) {
        return;
      }

      const entry = controlIndex.get(controlId);
      if (!entry) {
        getLfManager().log(
          'Layout references unknown control id.',
          { controlId, filterType: state.filterType },
          LogSeverity.Warning,
        );
        return;
      }

      const { controlType, config } = entry;
      const settingsRecord = state.filter.settings as unknown as Record<string, unknown>;
      if (typeof settingsRecord[controlId] === 'undefined') {
        settingsRecord[controlId] = (config as { defaultValue?: unknown }).defaultValue;
      }

      switch (controlType) {
        case ImageEditorControls.Checkbox: {
          const checkboxConfig = config as ImageEditorCheckboxConfig;
          const checkbox = document.createElement(TagName.LfCheckbox);

          checkbox.lfLabel = parseLabel(checkboxConfig);
          checkbox.lfValue = checkboxConfig.defaultValue ?? false;
          checkbox.title = checkboxConfig.title;
          checkbox.addEventListener(LfEventName.LfCheckbox, (event) => onCheckbox(state, event));

          target.appendChild(checkbox);
          state.elements.controls[checkboxConfig.id as ImageEditorCheckboxIds] = checkbox;
          renderedControls.add(controlId);
          break;
        }
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

          target.appendChild(slider);
          state.elements.controls[sliderConfig.id as ImageEditorSliderIds] = slider;
          renderedControls.add(controlId);
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
          textfield.addEventListener(LfEventName.LfTextfield, (event) => onTextfield(state, event));

          target.appendChild(textfield);
          state.elements.controls[textfieldConfig.id as ImageEditorTextfieldIds] = textfield;
          renderedControls.add(controlId);
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

          target.appendChild(multiinput);
          state.elements.controls[multiConfig.id as ImageEditorTextfieldIds] = multiinput;
          renderedControls.add(controlId);
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

          target.appendChild(select);
          state.elements.controls[selectConfig.id as ImageEditorSelectIds] = select;
          renderedControls.add(controlId);
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

          target.appendChild(toggle);
          state.elements.controls[toggleConfig.id as ImageEditorToggleIds] = toggle;
          renderedControls.add(controlId);
          break;
        }
        default:
          throw new Error(`Unknown control type: ${controlType}`);
      }
    };

    const renderLayout = (items: ImageEditorLayout, target: HTMLElement) => {
      items.forEach((item) => {
        if (typeof item === 'object' && 'children' in item) {
          const group = item as ImageEditorLayoutGroup;
          if (!group.children || group.children.length === 0) {
            return;
          }

          const slotId = group.id;
          const accordion = document.createElement(TagName.LfAccordion);
          const slotCell = { shape: 'slot', value: slotId } as const;

          const baseNode =
            group.node ??
            ({
              id: slotId,
              value: group.id,
            } as LfDataNode);

          const withSlot: LfDataNode = {
            ...baseNode,
            cells: {
              ...(baseNode.cells ?? {}),
              lfSlot: slotCell,
            },
          };

          accordion.lfDataset = { nodes: [withSlot] };

          const groupContainer = document.createElement(TagName.Div);
          groupContainer.classList.add(ImageEditorCSS.SettingsControls);
          (groupContainer as HTMLElement & { slot?: string }).slot = slotId;

          renderLayout(group.children, groupContainer);
          accordion.appendChild(groupContainer);
          target.appendChild(accordion);
          return;
        }

        renderControl(item as ImageEditorControlIds, target);
      });
    };

    renderLayout(layoutToRender, controlsContainer);

    if (state.filterType === 'resizeEdge' || state.filterType === 'resizeFree') {
      updateResizeHelperText(state);
    }

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

    const requiresApply = filter?.manualApply === true;
    if (requiresApply) {
      const applyButton = document.createElement(TagName.LfButton);
      applyButton.lfIcon = '--lf-icon-success';
      applyButton.lfLabel = 'Apply';
      applyButton.lfStretchX = true;
      applyButton.addEventListener('click', () => {
        if (state.update.apply) {
          void state.update.apply();
        } else {
          void state.update.snapshot();
        }
      });
      buttonsWrapper.appendChild(applyButton);
    }

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
      case 'LF-CHECKBOX': {
        const checkbox = control as HTMLLfCheckboxElement;
        void checkbox.setValue(checkbox.lfValue ?? false);
        break;
      }
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
  const configsByType = filter.configs ?? ({} as ImageEditorSettingsFor);

  (Object.keys(configsByType) as ImageEditorControls[]).forEach((controlType) => {
    const configs = configsByType[controlType] as ImageEditorControlConfig[] | undefined;
    configs?.forEach((config) => {
      const defaultValue = defaults[config.id as ImageEditorControlIds];
      if (typeof defaultValue === 'undefined') {
        return;
      }

      switch (controlType) {
        case ImageEditorControls.Checkbox: {
          const checkboxConfig = config as ImageEditorCheckboxConfig;
          const boolValue =
            defaultValue === true ||
            (typeof defaultValue === 'string' && defaultValue.toLowerCase() === 'true');
          checkboxConfig.defaultValue = boolValue;
          mutableSettings[checkboxConfig.id] = boolValue;
          break;
        }
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
          if (textfieldConfig.id === ImageEditorTextfieldIds.Seed) {
            const numericValue =
              defaultValue === null || defaultValue === ''
                ? -1
                : typeof defaultValue === 'number'
                ? defaultValue
                : Number(defaultValue);
            textfieldConfig.defaultValue = numericValue.toString();
            mutableSettings[textfieldConfig.id] = numericValue;
            break;
          }

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
