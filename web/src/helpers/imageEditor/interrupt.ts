import { LogSeverity } from '../../types/manager/manager';
import {
  ImageEditorCSS,
  ImageEditorState,
  ImageEditorStatus,
} from '../../types/widgets/imageEditor';
import { getApiRoutes, getLfManager } from '../../utils/common';
import { getPathColumn, getStatusColumn } from './selectors';
import { resetSettings } from './settings';
import { setGridStatus } from './status';

//#region Interrupt
export const handleInterruptForState = async (state: ImageEditorState) => {
  const lfManager = getLfManager();
  const { syntax } = lfManager.getManagers().lfFramework;
  const { actionButtons, grid, imageviewer } = state.elements;
  const dataset = imageviewer.lfDataset;
  const statusColumn = getStatusColumn(dataset);
  const pathColumn = getPathColumn(dataset);
  const parsedPath = pathColumn ? syntax.json.unescape(pathColumn).parsedJSON : undefined;
  const path = typeof parsedPath?.title === 'string' ? parsedPath.title : null;

  if (statusColumn?.title === ImageEditorStatus.Pending) {
    statusColumn.title = ImageEditorStatus.Completed;

    try {
      if (!dataset || !path) {
        throw new Error('The active editing session has no bound dataset path.');
      }
      const update = await getApiRoutes().json.update(path, dataset);
      if (update.status !== LogSeverity.Success) {
        throw new Error(String(update.message || 'The editing-session update was rejected.'));
      }
    } catch (error) {
      statusColumn.title = ImageEditorStatus.Pending;
      if (actionButtons?.interrupt && actionButtons?.resume) {
        setGridStatus(ImageEditorStatus.Pending, grid, actionButtons);
      } else {
        grid?.classList.remove(ImageEditorCSS.GridIsInactive);
      }
      lfManager.log(
        'Failed to resume the workflow; the editing session remains pending.',
        { error, path },
        LogSeverity.Error,
      );
      return;
    }

    if (actionButtons?.interrupt && actionButtons?.resume) {
      setGridStatus(ImageEditorStatus.Completed, grid, actionButtons);
    } else {
      grid?.classList.add(ImageEditorCSS.GridIsInactive);
    }

    try {
      const components = await imageviewer.getComponents();
      const navigation = components?.navigation;
      await imageviewer.reset();
      await navigation?.masonry?.setSelectedShape?.(null);
    } catch (error) {
      lfManager.log(
        'Failed to reset image viewer after workflow interrupt.',
        { error },
        LogSeverity.Warning,
      );
    }
  }

  await resetSettings(imageviewer);
};
//#endregion
