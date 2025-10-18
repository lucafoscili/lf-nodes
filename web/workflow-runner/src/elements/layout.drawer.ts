import { WorkflowState } from '../types/state';
import { WorkflowSectionController } from './section';

//#region Constants
const ROOT_CLASS = 'drawer-section';
//#endregion

//#region Factory
export const createDrawerSection = (): WorkflowSectionController => {
  let element: HTMLLfDrawerElement | null = null;
  let lastState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    lastState = state;
    const { ui } = state;

    element = document.createElement('lf-drawer');
    element.className = ROOT_CLASS;
    element.lfDisplay = 'slide';

    ui.layout.drawer._root = element;
    ui.layout._root?.appendChild(element);
  };

  const render = () => {};

  const destroy = () => {
    element?.remove();
    if (lastState) {
      lastState.ui.layout.drawer._root = null;
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
