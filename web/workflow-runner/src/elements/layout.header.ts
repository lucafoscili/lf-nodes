import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowSectionController } from '../types/section';
import { WorkflowState } from '../types/state';
import { createComponent } from './components';

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

const _debugToggle = (state: WorkflowState) => {
  const { theme } = getLfFramework();
  const { get } = theme;
  const lfIcon = get.icon('code');

  const props = {
    lfAriaLabel: 'Toggle developer console',
    lfIcon,
    lfStyling: 'icon',
  } as Partial<LfButtonInterface>;
  const debugToggle = createComponent.button(props);
  debugToggle.lfUiState = 'info';
  debugToggle.className = `${ROOT_CLASS}__debug-toggle`;
  debugToggle.addEventListener('lf-button-event', (e) => {
    const { eventType } = e.detail;

    switch (eventType) {
      case 'click':
        state.manager?.toggleDebug();
        break;
    }
  });

  return debugToggle;
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
    const debugToggle = _debugToggle(state);

    state.mutate.ui((uiState) => {
      uiState.layout.header.drawerToggle = drawerToggle;
      uiState.layout.header.debugToggle = debugToggle;
    });

    element.appendChild(container);
    container.appendChild(drawerToggle);
    container.appendChild(debugToggle);

    state.mutate.ui((uiState) => {
      uiState.layout.header._root = element;
    });
    ui.layout._root?.appendChild(element);
  };

  const render = (state: WorkflowState) => {
    const { isDebug } = state;

    const debugToggle = state.ui.layout.header.debugToggle;
    if (debugToggle) {
      debugToggle.lfUiState = isDebug ? 'secondary' : 'info';
      debugToggle.title = isDebug ? 'Hide developer console' : 'Show developer console';
    }
  };

  const destroy = () => {
    element?.remove();
    if (lastState) {
      lastState.mutate.ui((uiState) => {
        uiState.layout.header._root = null;
        uiState.layout.header.drawerToggle = null;
        uiState.layout.header.debugToggle = null;
        uiState.layout.header.themeSwitch = null;
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
