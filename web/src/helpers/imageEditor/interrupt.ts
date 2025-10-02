import { LfDataColumn } from '@lf-widgets/foundations';
import { LogSeverity } from '../../types/manager/manager';
import {
  ImageEditorCSS,
  ImageEditorState,
  ImageEditorStatus,
} from '../../types/widgets/imageEditor';
import { getApiRoutes, getLfManager, unescapeJson } from '../../utils/common';
import { getPathColumn, getStatusColumn } from './selectors';
import { resetSettings } from './settings';
import { setGridStatus } from './status';

//#region Interrupt
export const handleInterruptForState = async (state: ImageEditorState) => {
  const lfManager = getLfManager();
  const { actionButtons, grid, imageviewer } = state.elements;
  const dataset = imageviewer.lfDataset;
  const statusColumn = getStatusColumn(dataset);
  const pathColumn = getPathColumn(dataset);
  const parsedPath = pathColumn
    ? (unescapeJson(pathColumn).parsedJson as LfDataColumn | undefined)
    : undefined;
  const path = typeof parsedPath?.title === 'string' ? parsedPath.title : null;

  if (statusColumn?.title === ImageEditorStatus.Pending) {
    statusColumn.title = ImageEditorStatus.Completed;

    if (dataset && path) {
      try {
        await getApiRoutes().json.update(path, dataset);
      } catch (error) {
        lfManager.log(
          'Failed to update JSON after workflow interrupt.',
          { error, path },
          LogSeverity.Warning,
        );
      }
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
