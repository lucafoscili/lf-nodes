import {
  LfSliderEventPayload,
  LfTextfieldEventPayload,
  LfToggleEventPayload,
} from '@lf-widgets/foundations';
import { ImageEditorState, PrepSettingsFn } from '../types/widgets/imageEditor';
import { apiCall } from './imageEditor/api';
import { createEventHandlers } from './imageEditor/events';
import { handleInterruptForState } from './imageEditor/interrupt';
import { getPathColumn, getStatusColumn, parseLabel } from './imageEditor/selectors';
import { applyFilterDefaults, createPrepSettings, resetSettings } from './imageEditor/settings';
import { setGridStatus } from './imageEditor/status';
import { refreshValues, updateCb } from './imageEditor/update';

//#region Event Handlers
const handlerRefs: {
  slider: (state: ImageEditorState, e: CustomEvent<LfSliderEventPayload>) => void | Promise<void>;
  textfield: (
    state: ImageEditorState,
    e: CustomEvent<LfTextfieldEventPayload>,
  ) => void | Promise<void>;
  toggle: (state: ImageEditorState, e: CustomEvent<LfToggleEventPayload>) => void | Promise<void>;
} = {
  slider: async () => {
    throw new Error('Image editor slider handler not initialized.');
  },
  textfield: async () => {
    throw new Error('Image editor textfield handler not initialized.');
  },
  toggle: async () => {
    throw new Error('Image editor toggle handler not initialized.');
  },
};

export const prepSettings: PrepSettingsFn = createPrepSettings({
  onSlider: (state: ImageEditorState, event: CustomEvent<LfSliderEventPayload>) =>
    handlerRefs.slider(state, event),
  onTextfield: (state: ImageEditorState, event: CustomEvent<LfTextfieldEventPayload>) =>
    handlerRefs.textfield(state, event),
  onToggle: (state: ImageEditorState, event: CustomEvent<LfToggleEventPayload>) =>
    handlerRefs.toggle(state, event),
});

export const EV_HANDLERS = createEventHandlers({
  handleInterruptForState,
  prepSettings,
});

handlerRefs.slider = EV_HANDLERS.slider;
handlerRefs.textfield = EV_HANDLERS.textfield;
handlerRefs.toggle = EV_HANDLERS.toggle;
//#endregion

export {
  apiCall,
  applyFilterDefaults,
  getPathColumn,
  getStatusColumn,
  handleInterruptForState,
  parseLabel,
  refreshValues,
  resetSettings,
  setGridStatus,
  updateCb,
};
