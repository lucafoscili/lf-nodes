import { WorkflowMainSections } from '../types/section';
import { WorkflowView } from '../types/state';

export const HOME_PLACEHOLDER = 'Select a workflow to get started.';

export const sectionsForView = (view: WorkflowView): WorkflowMainSections[] => {
  switch (view) {
    case 'home':
      return [];
    case 'history':
      return ['outputs'];
    case 'run':
      return ['results'];
    case 'workflow':
    default:
      return ['inputs', 'outputs'];
  }
};
