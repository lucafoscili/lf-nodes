import { WorkflowSectionController } from '../types/section';
import { WorkflowState } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region Constants
const ROOT_CLASS = 'main-section';
//#endregion

//#region Factory
export const createMainSection = (): WorkflowSectionController => {
  const { MAIN_DESTROYED, MAIN_MOUNTED } = DEBUG_MESSAGES;

  let element: HTMLElement | null = null;
  let lastState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    lastState = state;
    const { ui } = state;

    element = document.createElement('main');
    element.className = ROOT_CLASS;

    state.mutate.ui((uiState) => {
      uiState.layout.main._root = element;
    });
    ui.layout._root?.appendChild(element);

    debugLog(MAIN_MOUNTED, 'informational', {});
  };

  const render = () => {};

  const destroy = () => {
    element?.remove();
    if (lastState) {
      lastState.mutate.ui((uiState) => {
        uiState.layout.main._root = null;
      });
      debugLog(MAIN_DESTROYED, 'informational', {});
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
