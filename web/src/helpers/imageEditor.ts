import {
  LfButtonEventPayload,
  LfCanvasEventPayload,
  LfDataColumn,
  LfDataDataset,
  LfDataNode,
  LfEvent,
  LfImageviewerEventPayload,
  LfSliderEventPayload,
  LfTextfieldEventPayload,
  LfToggleEventPayload,
  LfTreeEventPayload,
} from '@lf-widgets/foundations';
import { SETTINGS } from '../fixtures/imageEditor';
import { LfEventName } from '../types/events/events';
import { LogSeverity } from '../types/manager/manager';
import {
  ImageEditorActionButtons,
  ImageEditorBrushFilter,
  ImageEditorBrushSettings,
  ImageEditorColumnId,
  ImageEditorControlConfig,
  ImageEditorControlIds,
  ImageEditorControls,
  ImageEditorCSS,
  ImageEditorFilter,
  ImageEditorFilterType,
  ImageEditorIcons,
  ImageEditorRequestSettings,
  ImageEditorSliderConfig,
  ImageEditorSliderIds,
  ImageEditorState,
  ImageEditorStatus,
  ImageEditorTextfieldConfig,
  ImageEditorTextfieldIds,
  ImageEditorToggleConfig,
  ImageEditorToggleIds,
} from '../types/widgets/imageEditor';
import { NodeName, TagName } from '../types/widgets/widgets';
import {
  canvasToBase64,
  debounce,
  getApiRoutes,
  getLfManager,
  isTree,
  isValidObject,
  unescapeJson,
} from '../utils/common';

export const EV_HANDLERS = {
  //#region Button handler
  button: async (state: ImageEditorState, e: CustomEvent<LfButtonEventPayload>) => {
    const { comp, eventType } = e.detail;

    const { elements } = state;
    const { actionButtons, grid, imageviewer } = elements;

    if (eventType === 'click') {
      const update = async () => {
        const dataset = imageviewer.lfDataset;
        const pathColumn = getPathColumn(dataset);
        const statusColumn = getStatusColumn(dataset);

        if (statusColumn?.title === ImageEditorStatus.Pending) {
          statusColumn.title = ImageEditorStatus.Completed;
          const path = (unescapeJson(pathColumn).parsedJson as LfDataColumn).title;

          await getApiRoutes().json.update(path, dataset);
          setGridStatus(ImageEditorStatus.Completed, grid, actionButtons);

          const { masonry } = (await imageviewer.getComponents()).navigation;
          await imageviewer.reset();
          await masonry.setSelectedShape(null);
        }
      };

      switch (comp.lfIcon) {
        case ImageEditorIcons.Interrupt:
          getApiRoutes().comfy.interrupt();
          break;
      }

      await update();
      resetSettings(imageviewer);
    }
  },
  //#endregion

  //#region Canvas handler
  canvas: async (state: ImageEditorState, e: CustomEvent<LfCanvasEventPayload>) => {
    const { comp, eventType, points } = e.detail;

    const { filter, filterType } = state;

    switch (eventType) {
      case 'stroke':
        const originalFilter = filter;
        const originalFilterType = filterType;
        const canvas = await comp.getCanvas();
        const b64_canvas = canvasToBase64(canvas);
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
            b64_canvas,
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
              b64_canvas,
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

  //#region Imageviewer handler
  imageviewer: async (state: ImageEditorState, e: CustomEvent<LfImageviewerEventPayload>) => {
    const { comp, eventType, originalEvent } = e.detail;

    const { node } = state;

    switch (eventType) {
      case 'lf-event':
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
          case 'stroke':
            const canvasEv = ogEv as CustomEvent<LfCanvasEventPayload>;
            EV_HANDLERS.canvas(state, canvasEv);
            break;
        }
        break;

      case 'ready':
        const { details, navigation } = await comp.getComponents();
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
  },
  //#endregion

  //#region Slider handler
  slider: async (state: ImageEditorState, e: CustomEvent<LfSliderEventPayload>) => {
    const { eventType } = e.detail;

    const { update } = state;
    const { preview, snapshot } = update;

    switch (eventType) {
      case 'change':
        snapshot();
        break;
      case 'input':
        const debouncedCallback = debounce(preview, 300);
        debouncedCallback();
        break;
    }
  },
  //#endregion

  //#region Textfield handler
  textfield: async (state: ImageEditorState, e: CustomEvent<LfTextfieldEventPayload>) => {
    const { eventType } = e.detail;

    const { update } = state;
    const { preview, snapshot } = update;

    switch (eventType) {
      case 'change':
        snapshot();
        break;
      case 'input':
        const debouncedCallback = debounce(preview, 300);
        debouncedCallback();
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
        snapshot();
        break;
    }
  },
  //#endregion
};

//#region apiCall
export const apiCall = async (state: ImageEditorState, addSnapshot: boolean) => {
  const { elements, filter, filterType } = state;
  const { imageviewer } = elements;

  const lfManager = getLfManager();

  const snapshotValue = (await imageviewer.getCurrentSnapshot()).value;
  const baseSettings = filter.settings as ImageEditorRequestSettings<typeof filterType>;
  const payload: ImageEditorRequestSettings<typeof filterType> = {
    ...baseSettings,
  };

  const contextId = (
    imageviewer.lfDataset as ImageEditorRequestSettings<typeof filterType> | undefined
  )?.context_id;

  if (contextId) {
    payload.context_id = contextId;
  }

  requestAnimationFrame(() => imageviewer.setSpinnerStatus(true));

  try {
    const response = await getApiRoutes().image.process(snapshotValue, filterType, payload);
    if (response.mask) {
      lfManager.log(
        'Saved inpaint mask preview to temp',
        { mask: response.mask },
        LogSeverity.Info,
      );
    }
    if (addSnapshot) {
      await imageviewer.addSnapshot(response.data);
    } else {
      const { canvas } = (await imageviewer.getComponents()).details;
      const image = await canvas.getImage();
      requestAnimationFrame(() => (image.lfValue = response.data));
    }
  } catch (error) {
    lfManager.log('Error processing image!', { error }, LogSeverity.Error);
  }

  requestAnimationFrame(() => imageviewer.setSpinnerStatus(false));
};
//#endregion

//#region refreshValues
export const refreshValues = async (state: ImageEditorState, addSnapshot = false) => {
  const { elements, filter } = state;
  const { controls } = elements;

  const lfManager = getLfManager();

  for (const key in controls) {
    if (Object.prototype.hasOwnProperty.call(controls, key)) {
      const id = key as ImageEditorControlIds;
      const control = controls[id];

      switch (control.tagName) {
        case 'LF-SLIDER': {
          const slider = control as HTMLLfSliderElement;
          const sliderValue = await slider.getValue();
          filter.settings[id] = addSnapshot ? sliderValue.real : sliderValue.display;
          break;
        }
        case 'LF-TEXTFIELD': {
          const textfield = control as HTMLLfTextfieldElement;
          const textfieldValue = await textfield.getValue();
          filter.settings[id] = textfieldValue;
          break;
        }
        case 'LF-TOGGLE': {
          const toggle = control as HTMLLfToggleElement;
          const toggleValue = await toggle.getValue();
          filter.settings[id] = toggleValue === 'on' ? toggle.dataset.on : toggle.dataset.off;
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

//#region prepSettings
export const prepSettings = (state: ImageEditorState, node: LfDataNode) => {
  state.elements.controls = {};
  state.filter = unescapeJson(node.cells.lfCode.value).parsedJson as ImageEditorFilter;
  state.filterType = node.id as ImageEditorFilterType;

  const { elements, filter } = state;
  const { settings } = elements;

  settings.innerHTML = '';

  const controlsContainer = document.createElement(TagName.Div);
  controlsContainer.classList.add(ImageEditorCSS.SettingsControls);
  settings.appendChild(controlsContainer);

  const controlNames = Object.keys(filter.configs) as ImageEditorControls[];
  controlNames.forEach((controlName) => {
    const controls: ImageEditorControlConfig[] = filter.configs[controlName];
    if (controls) {
      controls.forEach((control) => {
        switch (controlName) {
          case ImageEditorControls.Slider:
            const slider = createSlider(state, control as ImageEditorSliderConfig);
            controlsContainer.appendChild(slider);
            state.elements.controls[control.id as ImageEditorSliderIds] = slider;
            break;
          case ImageEditorControls.Textfield:
            const textfield = createTextfield(state, control as ImageEditorTextfieldConfig);
            controlsContainer.appendChild(textfield);
            state.elements.controls[control.id as ImageEditorTextfieldIds] = textfield;
            break;
          case ImageEditorControls.Toggle:
            const toggle = createToggle(state, control as ImageEditorToggleConfig);
            controlsContainer.appendChild(toggle);
            state.elements.controls[control.id as ImageEditorToggleIds] = toggle;
            break;
          default:
            throw new Error(`Unknown control type: ${controlName}`);
        }
      });
    }
  });

  const resetButton = document.createElement(TagName.LfButton);
  resetButton.lfIcon = ImageEditorIcons.Reset;
  resetButton.lfLabel = 'Reset';
  resetButton.lfStretchX = true;
  resetButton.addEventListener('click', () => resetSettings(settings));
  settings.appendChild(resetButton);

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
    applyButton.addEventListener('click', () => {
      void updateCb(state, true, true);
    });
    settings.appendChild(applyButton);
  }
};
//#endregion

//#region createSlider
export const createSlider = (state: ImageEditorState, data: ImageEditorSliderConfig) => {
  const comp = document.createElement(TagName.LfSlider);

  comp.lfLabel = parseLabel(data);
  comp.lfLeadingLabel = true;
  comp.lfMax = Number(data.max);
  comp.lfMin = Number(data.min);
  comp.lfStep = Number(data.step);
  comp.lfStyle = '.form-field { width: 100%; }';
  comp.lfValue = Number(data.defaultValue);
  comp.title = data.title;
  comp.addEventListener(LfEventName.LfSlider, (e) => EV_HANDLERS.slider(state, e));

  return comp;
};
//#endregion

//#region createTextfield
export const createTextfield = (state: ImageEditorState, data: ImageEditorTextfieldConfig) => {
  const comp = document.createElement(TagName.LfTextfield);

  comp.lfLabel = parseLabel(data);
  comp.lfHtmlAttributes = { type: data.type };
  comp.lfValue = String(data.defaultValue).valueOf();
  comp.title = data.title;
  comp.addEventListener(LfEventName.LfTextfield, (e) => EV_HANDLERS.textfield(state, e));

  return comp;
};
//#endregion

//#region createToggle
export const createToggle = (state: ImageEditorState, data: ImageEditorToggleConfig) => {
  const comp = document.createElement(TagName.LfToggle);

  comp.dataset.off = data.off;
  comp.dataset.on = data.on;
  comp.lfLabel = parseLabel(data);
  comp.lfValue = false;
  comp.title = data.title;
  comp.addEventListener(LfEventName.LfToggle, (e) => EV_HANDLERS.toggle(state, e));

  return comp;
};
//#endregion

//#region Utils
export const getPathColumn = (dataset: LfDataDataset): LfDataColumn | null => {
  return dataset?.columns?.find((c) => c.id === ImageEditorColumnId.Path) || null;
};
export const getStatusColumn = (dataset: LfDataDataset): LfDataColumn | null => {
  return dataset?.columns?.find((c) => c.id === ImageEditorColumnId.Status) || null;
};
export const parseLabel = (data: ImageEditorControlConfig) => {
  return data.isMandatory ? `${data.ariaLabel}*` : data.ariaLabel;
};
export const resetSettings = async (settings: HTMLElement) => {
  const controls = Array.from(settings.querySelectorAll('[data-id]'));
  for (const control of controls) {
    switch (control.tagName) {
      case 'LF-SLIDER':
        const slider = control as HTMLLfSliderElement;
        await slider.setValue(slider.lfValue);
        await slider.refresh();
        break;
      case 'LF-TEXTFIELD':
        const textfield = control as HTMLLfTextfieldElement;
        await textfield.setValue(textfield.lfValue);
        break;
      case 'LF-TOGGLE':
        const toggle = control as HTMLLfToggleElement;
        toggle.setValue(toggle.lfValue ? 'on' : 'off');
        break;
    }
  }
};
export const setGridStatus = (
  status: ImageEditorStatus,
  grid: HTMLDivElement,
  actionButtons: ImageEditorActionButtons,
) => {
  switch (status) {
    case ImageEditorStatus.Completed:
      requestAnimationFrame(() => {
        actionButtons.interrupt.lfUiState = 'disabled';
        actionButtons.resume.lfUiState = 'disabled';
      });
      grid.classList.add(ImageEditorCSS.GridIsInactive);
      break;

    case ImageEditorStatus.Pending:
      requestAnimationFrame(() => {
        actionButtons.interrupt.lfUiState = 'danger';
        actionButtons.resume.lfUiState = 'success';
      });
      grid.classList.remove(ImageEditorCSS.GridIsInactive);
      break;
  }
};
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

  if (shouldUpdate && (force || !requiresManualApply)) {
    apiCall(state, addSnapshot);
  }
};
//#endregion
