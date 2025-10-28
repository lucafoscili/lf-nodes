import { CreateRoutingControllerOptions, RoutingController } from '../types/manager';
import { WorkflowRoute } from '../types/state';
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

  //#region Update Route
  const updateRouteFromState = (precomputed?: WorkflowRoute) => {
    if (isApplyingRoute) {
      return;
    }
    const nextRoute = precomputed ?? computeRouteFromState(store.getState());
    if (!routesEqual(nextRoute, currentRoute)) {
      currentRoute = nextRoute;
      replaceRouteInHistory(nextRoute);
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
      let workflowId = route.workflowId ?? null;
      if (workflowId && workflowExists(workflowId) && state.current.id !== workflowId) {
        state.mutate.workflow(workflowId);
      } else if (workflowId && !workflowExists(workflowId)) {
        workflowId = state.current.id ?? null;
      }

      const normalizedRoute: WorkflowRoute = {
        view: route.view,
        workflowId: workflowId ?? undefined,
        runId: route.runId ?? undefined,
      };

      changeView(store, normalizedRoute.view, {
        runId: normalizedRoute.runId ?? null,
        clearResults: normalizedRoute.view === 'run' ? false : undefined,
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
    currentRoute = parseRouteFromLocation();
    pendingRoute = currentRoute;
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



