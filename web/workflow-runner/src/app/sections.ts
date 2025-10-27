import { WorkflowMainSections } from '../types/section';
import { WorkflowState, WorkflowView } from '../types/state';

export const HOME_PLACEHOLDER = 'Select a workflow to get started.';

const DEFAULT_VIEW: WorkflowView = 'workflow';
export const VIEW_MAIN_SECTIONS: Record<WorkflowView, WorkflowMainSections[]> = {
  home: [],
  history: ['outputs'],
  run: ['results'],
  workflow: ['inputs', 'outputs'],
};

export const resolveMainSections = (state: WorkflowState): WorkflowMainSections[] => {
  const { runs, selectedRunId } = state;
  const view = VIEW_MAIN_SECTIONS[state.view] ? state.view : DEFAULT_VIEW;

  if (view === 'run') {
    const selectedRunExists = Boolean(
      selectedRunId && runs.some((run) => run.runId === selectedRunId),
    );
    return selectedRunExists ? VIEW_MAIN_SECTIONS.run : [];
  }

  return VIEW_MAIN_SECTIONS[view] ?? VIEW_MAIN_SECTIONS[DEFAULT_VIEW];
};
