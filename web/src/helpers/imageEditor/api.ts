import { LogSeverity } from '../../types/manager/manager';
import {
  ImageEditorDataset,
  ImageEditorRequestSettings,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { getApiRoutes, getLfManager } from '../../utils/common';
import { ensureDatasetContext } from './dataset';
import { showError } from './status';

//#region API Call
export const apiCall = async (state: ImageEditorState, addSnapshot: boolean) => {
  if (state.isApiProcessing) {
    return false;
  }

  const { elements, filter, filterType } = state;
  const { imageviewer } = elements;

  const lfManager = getLfManager();

  const snapshot = await imageviewer.getCurrentSnapshot();
  if (!snapshot) {
    lfManager.log('No snapshot available for processing!', {}, LogSeverity.Warning);
    showError(state, 'No snapshot available for processing!');
    return false;
  }

  const snapshotValue = snapshot.value;
  const baseSettings = filter.settings as ImageEditorRequestSettings<typeof filterType>;
  const payload: ImageEditorRequestSettings<typeof filterType> = {
    ...baseSettings,
  };

  const contextDataset = imageviewer.lfDataset as ImageEditorDataset | undefined;
  const contextId = ensureDatasetContext(contextDataset, state);

  if (!contextId && filterType === 'inpaint') {
    lfManager.log(
      'Missing editing context. Run the workflow to register an editing session before using inpaint.',
      { dataset: contextDataset },
      LogSeverity.Warning,
    );
    showError(state, 'Missing editing context. Run the workflow to register an editing session.');
    return false;
  }

  payload.context_id = contextId;

  state.isApiProcessing = true;
  requestAnimationFrame(() => imageviewer.setSpinnerStatus(true));

  let isSuccess = false;

  try {
    const response = await getApiRoutes().image.process(snapshotValue, filterType, payload);

    if (response.status !== LogSeverity.Success) {
      lfManager.log('API Error', { response }, LogSeverity.Error);
      showError(state, response.message || 'Unknown API error');
      requestAnimationFrame(() => imageviewer.setSpinnerStatus(false));
      state.isApiProcessing = false;
      return false;
    }

    if (response.mask) {
      lfManager.log(
        'Saved inpaint mask preview to temp',
        { mask: response.mask },
        LogSeverity.Info,
      );
    }
    if (response.cutout) {
      lfManager.log('Saved cutout preview to temp', { cutout: response.cutout }, LogSeverity.Info);
    }
    if (response.stats) {
      lfManager.log('Filter statistics', { stats: response.stats }, LogSeverity.Info);
    }
    if (addSnapshot) {
      await imageviewer.addSnapshot(response.data);
    } else {
      const { canvas } = (await imageviewer.getComponents()).details;
      const image = await canvas.getImage();
      requestAnimationFrame(() => (image.lfValue = response.data));
    }
    isSuccess = true;
  } catch (error) {
    lfManager.log('Error processing image!', { error }, LogSeverity.Error);
    showError(state, 'Error processing image! Check console for details.');
  }

  requestAnimationFrame(() => imageviewer.setSpinnerStatus(false));
  state.isApiProcessing = false;

  return isSuccess;
};
//#endregion
