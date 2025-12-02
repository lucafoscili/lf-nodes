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
    snackbar.classList.add(ImageEditorCSS.Snackbar);
    snackbar.lfPosition = 'inline';

    settings.prepend(snackbar);

    state.infoSnackbar = snackbar;
  }

  snackbar.lfMessage = message;
  snackbar.lfUiState = uiState;
};
//#endregion

//#region progress bar
export const setProgress = (state: ImageEditorState, value: number | null) => {
  const { settings } = state.elements;
  let bar = state.progressbar;

  if (!bar || !settings.contains(bar)) {
    bar = document.createElement('lf-progressbar');
    bar.classList.add(ImageEditorCSS.ProgressBar);
    bar.classList.add(ImageEditorCSS.ProgressBarHidden);
    bar.lfAnimated = true;
    bar.lfUiSize = 'xsmall';
    bar.lfUiState = 'info';

    settings.prepend(bar);

    state.progressbar = bar;
  }

  const numeric = typeof value === 'number' ? value : 0;
  const clamped = Math.max(0, Math.min(100, numeric));

  if (clamped <= 0 || clamped >= 100) {
    bar.lfValue = clamped;
    bar.classList.add(ImageEditorCSS.ProgressBarHidden);
  } else {
    bar.lfValue = clamped;
    bar.classList.remove(ImageEditorCSS.ProgressBarHidden);
  }
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
