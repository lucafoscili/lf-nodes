import { ImageEditorState } from '../../types/widgets/imageEditor';

//#region Constants
export const MANUAL_APPLY_PROCESSING_LABEL = 'Applying…';
//#endregion

//#region hasManualApplyPendingChanges
export const hasManualApplyPendingChanges = (state: ImageEditorState): boolean => {
  const manual = state.manualApply;
  if (!manual) {
    return false;
  }
  return manual.latestChangeId > manual.latestAppliedChangeId;
};

export const updateManualApplyButton = (state: ImageEditorState) => {
  const manual = state.manualApply;
  if (!manual) {
    return;
  }

  manual.dirty = hasManualApplyPendingChanges(state);

  if (manual.isProcessing) {
    manual.button.lfUiState = 'disabled';
    manual.button.lfLabel = MANUAL_APPLY_PROCESSING_LABEL;
    return;
  }

  manual.button.lfLabel = manual.defaultLabel;

  if (manual.dirty) {
    manual.button.lfUiState = 'success';
  } else {
    manual.button.lfUiState = 'disabled';
  }
};
//#endregion

//#region initManualApplyState
export const initManualApplyState = (state: ImageEditorState, button: HTMLLfButtonElement) => {
  state.manualApply = {
    button,
    defaultLabel: button.lfLabel ?? 'Apply',
    dirty: false,
    isProcessing: false,
    changeCounter: 0,
    latestChangeId: 0,
    latestAppliedChangeId: 0,
    activeRequestChangeId: 0,
  };

  updateManualApplyButton(state);
};
//#endregion

//#region registerManualApplyChange
export const registerManualApplyChange = (state: ImageEditorState) => {
  if (!state.filter?.requiresManualApply || !state.manualApply) {
    return;
  }

  const manual = state.manualApply;
  manual.latestChangeId = ++manual.changeCounter;

  if (!manual.isProcessing) {
    updateManualApplyButton(state);
  }
};
//#endregion

//#region beginManualApplyRequest
export const beginManualApplyRequest = (state: ImageEditorState) => {
  if (!state.manualApply) {
    return;
  }

  const manual = state.manualApply;
  manual.isProcessing = true;
  manual.activeRequestChangeId = manual.latestChangeId;
  updateManualApplyButton(state);
};
//#endregion

//#region resolveManualApplyRequest
export const resolveManualApplyRequest = (state: ImageEditorState, wasSuccessful: boolean) => {
  if (!state.manualApply) {
    return;
  }

  const manual = state.manualApply;

  if (wasSuccessful) {
    manual.latestAppliedChangeId = Math.max(
      manual.latestAppliedChangeId,
      manual.activeRequestChangeId,
    );
  }

  manual.activeRequestChangeId = 0;
  manual.isProcessing = false;
  updateManualApplyButton(state);
};
//#endregion
