import {
  ImageEditorActionButtons,
  ImageEditorCSS,
  ImageEditorState,
  ImageEditorStatus,
} from '../../types/widgets/imageEditor';

//#region showError
export const showError = (state: ImageEditorState, message: string) => {
  const { settings } = state.elements;
  const errorDiv = document.createElement('div');
  errorDiv.style.color = 'var(--error-color)';
  errorDiv.style.padding = '8px';
  errorDiv.style.marginBottom = '8px';
  errorDiv.style.border = '1px solid var(--error-color)';
  errorDiv.style.borderRadius = '4px';
  errorDiv.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
  errorDiv.innerText = message;

  settings.prepend(errorDiv);

  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
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
