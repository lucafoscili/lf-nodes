import { WorkflowMainSections } from '../types/section';
import {
  WorkflowRoute,
  WorkflowState,
  WorkflowStore,
  WorkflowView,
} from '../types/state';
import { selectRun, setView } from './store-actions';

export const HOME_PLACEHOLDER = 'Select a workflow to get started.';

type SectionsResolver = (state: WorkflowState) => WorkflowMainSections[];
type RouteBuilder = (state: WorkflowState) => WorkflowRoute;

export interface ChangeViewOptions {
  runId?: string | null;
  clearResults?: boolean;
}

interface ViewDefinition {
  sections: SectionsResolver;
  toRoute: RouteBuilder;
  enter: (store: WorkflowStore, options: ChangeViewOptions) => WorkflowView;
}

const DEFAULT_VIEW: WorkflowView = 'workflow';
const SECTION_PRESETS: Record<'home' | 'history' | 'run' | 'workflow', WorkflowMainSections[]> = {
  home: [],
  history: ['outputs'],
  run: ['results'],
  workflow: ['inputs', 'outputs'],
};

const cloneSections = (sections: WorkflowMainSections[]) => sections.slice();
const selectRunWithDefaults = (
  store: WorkflowStore,
  runId: string | null,
  clearResults: boolean | undefined,
) => {
  if (clearResults === undefined) {
    selectRun(store, runId);
  } else {
    selectRun(store, runId, { clearResults });
  }
};

const resolveRunSections: SectionsResolver = (state) => {
  const { runs, selectedRunId } = state;
  if (selectedRunId && runs.some((run) => run.runId === selectedRunId)) {
    return cloneSections(SECTION_PRESETS.run);
  }
  return [];
};

const buildWorkflowRoute: RouteBuilder = (state) => {
  const workflowId = state.current.id ?? undefined;
  return workflowId ? { view: 'workflow', workflowId } : { view: 'workflow' };
};

const VIEW_DEFINITIONS: Record<WorkflowView, ViewDefinition> = {
  home: {
    sections: () => cloneSections(SECTION_PRESETS.home),
    toRoute: () => ({ view: 'home' }),
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return 'home';
    },
  },
  history: {
    sections: () => cloneSections(SECTION_PRESETS.history),
    toRoute: (state) => {
      const workflowId = state.current.id ?? undefined;
      return workflowId ? { view: 'history', workflowId } : { view: 'history' };
    },
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return 'history';
    },
  },
  run: {
    sections: resolveRunSections,
    toRoute: (state) => {
      const workflowId = state.current.id ?? undefined;
      const runId = state.selectedRunId ?? undefined;
      if (runId) {
        return { view: 'run', runId, workflowId };
      }
      return VIEW_DEFINITIONS.workflow.toRoute(state);
    },
    enter: (store, options) => {
      const requestedRunId = options.runId ?? null;
      const state = store.getState();
      const runId =
        requestedRunId ?? state.selectedRunId ?? null;
      const hasRun =
        Boolean(runId && state.runs.some((run) => run.runId === runId));

      if (!hasRun) {
        selectRunWithDefaults(store, null, options.clearResults);
        return 'workflow';
      }

      selectRunWithDefaults(store, runId, options.clearResults);
      return 'run';
    },
  },
  workflow: {
    sections: () => cloneSections(SECTION_PRESETS.workflow),
    toRoute: buildWorkflowRoute,
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return 'workflow';
    },
  },
};

const getViewDefinition = (view: WorkflowView): ViewDefinition =>
  VIEW_DEFINITIONS[view] ?? VIEW_DEFINITIONS[DEFAULT_VIEW];

export const changeView = (
  store: WorkflowStore,
  view: WorkflowView,
  options: ChangeViewOptions = {},
): WorkflowView => {
  const definition = getViewDefinition(view);
  const resolvedView = definition.enter(store, options);
  setView(store, resolvedView);
  return resolvedView;
};

export const resolveMainSections = (state: WorkflowState): WorkflowMainSections[] => {
  const definition = getViewDefinition(state.view);
  return definition.sections(state);
};

export const computeRouteFromState = (state: WorkflowState): WorkflowRoute => {
  const definition = getViewDefinition(state.view);
  return definition.toRoute(state);
};

export const getDefaultView = (): WorkflowView => DEFAULT_VIEW;
