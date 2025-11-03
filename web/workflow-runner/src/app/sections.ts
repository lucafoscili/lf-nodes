import {
  ChangeViewOptions,
  RouteBuilder,
  SectionsResolver,
  ViewDefinition,
  WorkflowMainSections,
} from '../types/section';
import { WorkflowRoute, WorkflowState, WorkflowStore, WorkflowView } from '../types/state';
import { selectRun, setView } from './store-actions';

const DEFAULT_VIEW: WorkflowView = 'workflow';
const SECTION_PRESETS: Record<'home' | 'history' | 'run' | 'workflow', WorkflowMainSections[]> = {
  home: ['home'],
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
  //#region Home
  home: {
    sections: () => cloneSections(SECTION_PRESETS.home),
    toRoute: () => ({ view: 'home' }),
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return 'home';
    },
  },
  //#endregion
  //#region History
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
  //#endregion
  //#region Run
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
      const runId = requestedRunId ?? state.selectedRunId ?? null;
      const hasRun = Boolean(runId && state.runs.some((run) => run.runId === runId));

      if (!hasRun) {
        selectRunWithDefaults(store, null, options.clearResults);
        return 'workflow';
      }

      selectRunWithDefaults(store, runId, options.clearResults);
      return 'run';
    },
  },
  //#endregion
  //#region Workflow
  workflow: {
    sections: () => cloneSections(SECTION_PRESETS.workflow),
    toRoute: buildWorkflowRoute,
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return 'workflow';
    },
  },
  //#endregion
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
