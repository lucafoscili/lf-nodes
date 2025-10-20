import { executeWorkflowButton } from '../handlers/workflow';
import { WorkflowSectionController } from '../types/section';
import { WorkflowState } from '../types/state';

//#region Constants
const ROOT_CLASS = 'action-button-section';
//#endregion

//#region Factory
export const createActionButtonSection = (): WorkflowSectionController => {
  let element: HTMLLfButtonElement | null = null;
  let lastState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    lastState = state;
    const { ui } = state;

    element = document.createElement('lf-button');
    element.className = ROOT_CLASS;
    element.lfIcon = 'send';
    element.lfStyling = 'floating';
    element.title = 'Run current workflow';
    element.addEventListener('lf-button-event', (e) => executeWorkflowButton(e, state));

    state.mutate.ui((uiState) => {
      uiState.layout.actionButton._root = element;
    });
    ui.layout._root?.appendChild(element);
  };

  const render = () => {};

  const destroy = () => {
    element?.remove();
    if (lastState) {
      lastState.mutate.ui((uiState) => {
        uiState.layout.actionButton._root = null;
      });
    }
    element = null;
    lastState = null;
  };

  return {
    mount,
    render,
    destroy,
  };
};
//#endregion
