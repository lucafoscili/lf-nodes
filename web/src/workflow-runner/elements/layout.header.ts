import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowState } from '../../types/workflow-runner/state';
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
const _drawerToggle = () => {
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
  return drawerToggle;
};
//#endregion

//#region Section
const _createSection = (state: WorkflowState) => {
  const { ui } = state;

  const section = document.createElement('lf-header');
  section.className = ROOT_CLASS;

  const container = _container();
  const drawerToggle = _drawerToggle();

  ui.layout.header.drawerToggle = drawerToggle;

  section.appendChild(container);

  container.appendChild(drawerToggle);

  ui.layout.header._root = section;
  ui.layout._root.appendChild(section);
};
//#endregion

//#region Public API
export const headerSection = {
  create: _createSection,
};
//#endregion
