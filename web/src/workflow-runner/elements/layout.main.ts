import { WorkflowState } from '../../types/workflow-runner/state';

//#region Constants
const ROOT_CLASS = 'main-section';
//#endregion

//#region Section
const _createSection = (state: WorkflowState) => {
  const { ui } = state;

  const section = document.createElement('main');
  section.className = ROOT_CLASS;

  ui.layout.main._root = section;
  ui.layout._root.appendChild(section);
};
//#endregion

//#region Public API
export const mainSection = {
  create: _createSection,
};
//#endregion
