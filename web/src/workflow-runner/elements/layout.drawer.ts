import { WorkflowState } from '../../types/workflow-runner/state';

//#region Constants
const ROOT_CLASS = 'drawer-section';
//#endregion

//#region Section
const _createSection = (state: WorkflowState) => {
  const { ui } = state;

  const section = document.createElement('lf-drawer');
  section.className = ROOT_CLASS;

  section.lfDisplay = 'slide';

  ui.layout.drawer._root = section;
  ui.layout._root.appendChild(section);
};
//#endregion

//#region Public API
export const drawerSection = {
  create: _createSection,
};
//#endregion
