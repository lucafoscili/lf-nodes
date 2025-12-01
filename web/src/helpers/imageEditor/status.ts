import { LfThemeUIState } from '@lf-widgets/foundations/dist';
import {
  ImageEditorActionButtons,
  ImageEditorCSS,
  ImageEditorState,
  ImageEditorStatus,
} from '../../types/widgets/imageEditor';

//#region snackbar
export const showBanner = (state: ImageEditorState, message: string, uiState: LfThemeUIState) => {
  const { settings } = state.elements;
  let snackbar = state.infoSnackbar;

  if (!snackbar || !settings.contains(snackbar)) {
    snackbar = document.createElement('lf-snackbar');
    snackbar.lfPosition = 'inline';

    settings.prepend(snackbar);

    state.infoSnackbar = snackbar;
  }

  snackbar.lfMessage = message;
  snackbar.lfUiState = uiState;
};
//#endregion

//#region setGridStatus
export function setGridStatus(
  status: ImageEditorStatus,
  grid: HTMLDivElement,
  actionButtons: ImageEditorActionButtons,
) {
  const { interrupt, resume } = actionButtons;
  switch (status) {
    case ImageEditorStatus.Completed:
      requestAnimationFrame(() => {
        if (interrupt) {
          interrupt.lfUiState = 'disabled';
        }
        if (resume) {
          resume.lfUiState = 'disabled';
        }
      });
      grid?.classList.add(ImageEditorCSS.GridIsInactive);
      break;

    case ImageEditorStatus.Pending:
      requestAnimationFrame(() => {
        if (interrupt) {
          interrupt.lfUiState = 'danger';
        }
        if (resume) {
          resume.lfUiState = 'success';
        }
      });
      grid?.classList.remove(ImageEditorCSS.GridIsInactive);
      break;
  }
}
//#endregion
