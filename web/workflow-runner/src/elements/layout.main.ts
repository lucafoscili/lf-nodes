import { WorkflowState } from '../types/state';
import { WorkflowSectionController } from './section';

//#region Constants
const ROOT_CLASS = 'main-section';
//#endregion

//#region Factory
export const createMainSection = (): WorkflowSectionController => {
  let element: HTMLElement | null = null;
  let lastState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    lastState = state;
    const { ui } = state;

    element = document.createElement('main');
    element.className = ROOT_CLASS;

    ui.layout.main._root = element;
    ui.layout._root?.appendChild(element);
  };

  const render = () => {};

  const destroy = () => {
    element?.remove();
    if (lastState) {
      lastState.ui.layout.main._root = null;
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
