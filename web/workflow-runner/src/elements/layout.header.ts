import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowState } from '../types/state';
import { createComponent } from './components';
import { WorkflowSectionController } from '../types/section';

//#region Constants
const ROOT_CLASS = 'header-section';
//#endregion

//#region Elements
const _container = () => {
  const container = document.createElement('div');
  container.className = `${ROOT_CLASS}__container`;
  container.slot = 'content';
  return container;
};

const _drawerToggle = (state: WorkflowState) => {
  const { theme } = getLfFramework();
  const { get } = theme;
  const lfIcon = get.icon('menu2');

  const props = {
    lfAriaLabel: 'Toggle drawer',
    lfIcon,
    lfStyling: 'icon',
  } as Partial<LfButtonInterface>;
  const drawerToggle = createComponent.button(props);
  drawerToggle.className = `${ROOT_CLASS}__drawer-toggle`;
  drawerToggle.addEventListener('lf-button-event', (e) => {
    const { eventType } = e.detail;

    switch (eventType) {
      case 'click':
        state.ui.layout.drawer._root.toggle();
        break;
    }
  });

  return drawerToggle;
};
//#endregion

//#region Factory
export const createHeaderSection = (): WorkflowSectionController => {
  let element: HTMLLfHeaderElement | null = null;
  let lastState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    lastState = state;
    const { ui } = state;

    element = document.createElement('lf-header');
    element.className = ROOT_CLASS;

    const container = _container();
    const drawerToggle = _drawerToggle(state);

    ui.layout.header.drawerToggle = drawerToggle;

    element.appendChild(container);
    container.appendChild(drawerToggle);

    ui.layout.header._root = element;
    ui.layout._root?.appendChild(element);
  };

  const render = () => {};

  const destroy = () => {
    element?.remove();
    if (lastState) {
      lastState.ui.layout.header._root = null;
      lastState.ui.layout.header.drawerToggle = null;
      lastState.ui.layout.header.themeSwitch = null;
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
