import {
  ImageEditorActionButtons,
  ImageEditorCSS,
  ImageEditorStatus,
} from '../../types/widgets/imageEditor';

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
