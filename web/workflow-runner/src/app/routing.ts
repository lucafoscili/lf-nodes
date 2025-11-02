import {
  CreateRoutingControllerOptions,
  NormalizedRouteResult,
  RoutingController,
} from '../types/manager';
import { WorkflowRoute, WorkflowState } from '../types/state';
import {
  parseRouteFromLocation,
  replaceRouteInHistory,
  routesEqual,
  subscribeToRouteChanges,
} from './router';
import { changeView, computeRouteFromState } from './sections';

//#region Routing Controller
export const createRoutingController = ({
  store,
}: CreateRoutingControllerOptions): RoutingController => {
  let currentRoute: WorkflowRoute | null = null;
  let pendingRoute: WorkflowRoute | null = null;
  let isApplyingRoute = false;
  let unsubscribe: (() => void) | undefined;

  //#region Helpers
  const hasWorkflowsLoaded = () => {
    const { workflows } = store.getState();
    return Array.isArray(workflows?.nodes) && workflows.nodes.length > 0;
  };

  const workflowExists = (workflowId: string) => {
    const { workflows } = store.getState();
    return Boolean(workflows?.nodes?.some((node) => node.id === workflowId));
  };
  //#endregion

  //#region Update Route
  const updateRouteFromState = (precomputed?: WorkflowRoute) => {
    if (isApplyingRoute) {
      return;
    }
    const state = store.getState();
    const nextRoute = precomputed ?? computeRouteFromState(state);
    const normalized = normalizeRoute(nextRoute, state).route;
    if (!routesEqual(normalized, currentRoute)) {
      currentRoute = normalized;
      replaceRouteInHistory(normalized);
    }
  };
  //#endregion

  //#region Apply Route
  const applyRoute = (route: WorkflowRoute, allowDefer = true) => {
    if (allowDefer && !hasWorkflowsLoaded()) {
      pendingRoute = route;
      return;
    }

    isApplyingRoute = true;
    pendingRoute = null;
    try {
      const state = store.getState();
      const { route: normalizedRoute, clearResults } = normalizeRoute(route, state);

      const workflowId = normalizedRoute.workflowId ?? null;
      if (workflowId && state.current.id !== workflowId && workflowExists(workflowId)) {
        state.mutate.workflow(workflowId);
      }

      changeView(store, normalizedRoute.view, {
        runId: normalizedRoute.runId ?? null,
        clearResults,
      });
    } finally {
      isApplyingRoute = false;
      updateRouteFromState();
    }
  };
  //#endregion

  //#region Apply Pending Route
  const applyPendingRouteIfNeeded = () => {
    if (pendingRoute) {
      const route = pendingRoute;
      pendingRoute = null;
      applyRoute(route, false);
    } else {
      updateRouteFromState();
    }
  };
  //#endregion

  //#region Handle Route Change
  const handleRouteChange = (route: WorkflowRoute) => {
    pendingRoute = route;
    applyRoute(route);
  };
  //#endregion

  //#region Initialize / Destroy
  const initialize = () => {
    currentRoute = null;
    pendingRoute = parseRouteFromLocation();
    unsubscribe = subscribeToRouteChanges((route) => {
      handleRouteChange(route);
    });
  };

  const destroy = () => {
    if (unsubscribe) {
      unsubscribe();
      unsubscribe = undefined;
    }
  };
  //#endregion

  return {
    applyPendingRouteIfNeeded,
    destroy,
    getPendingRoute: () => pendingRoute,
    initialize,
    updateRouteFromState,
  };
};
//#endregion

//#region Normalize Route
export const normalizeRoute = (
  route: WorkflowRoute,
  state: WorkflowState,
): NormalizedRouteResult => {
  const { runs, current, workflows } = state;
  const availableNodes = workflows?.nodes ?? [];
  const workflowExists = (id?: string | null) =>
    Boolean(id && availableNodes.some((node) => node.id === id));

  const findRun = (runId?: string | null) =>
    runId ? runs.find((run) => run.runId === runId) ?? null : null;

  const run = findRun(route.runId ?? null);

  let workflowId = route.workflowId ?? undefined;
  if (workflowId && !workflowExists(workflowId)) {
    workflowId = undefined;
  }

  const runWorkflowId = run?.workflowId ?? null;
  if (workflowId === undefined && workflowExists(runWorkflowId)) {
    workflowId = runWorkflowId ?? undefined;
  } else if (workflowId === undefined && workflowExists(current.id)) {
    workflowId = current.id ?? undefined;
  }

  let runId = run?.runId ?? undefined;
  let view = route.view;

  if (view === 'run') {
    if (!runId) {
      view = 'workflow';
    }
  } else if (view === 'history' || view === 'workflow') {
    runId = undefined;
  } else if (view === 'home') {
    workflowId = undefined;
    runId = undefined;
  } else {
    view = 'workflow';
    runId = undefined;
  }

  if (view !== 'run') {
    runId = undefined;
  }

  const normalizedRoute: WorkflowRoute = { view };
  if (workflowId) {
    normalizedRoute.workflowId = workflowId;
  }
  if (view === 'run' && runId) {
    normalizedRoute.runId = runId;
    if (runWorkflowId && workflowExists(runWorkflowId)) {
      normalizedRoute.workflowId = runWorkflowId;
    }
  }

  const clearResults = normalizedRoute.view === 'run' && normalizedRoute.runId ? false : undefined;

  return {
    route: normalizedRoute,
    clearResults,
  };
};
//#endregion
