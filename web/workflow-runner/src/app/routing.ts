import { CreateRoutingControllerOptions, RoutingController } from '../types/manager';
import { WorkflowRoute, WorkflowState, WorkflowView } from '../types/state';
import {
  parseRouteFromLocation,
  replaceRouteInHistory,
  routesEqual,
  subscribeToRouteChanges,
} from './router';
import { changeView } from './store-actions';

type RouteBuilder = (state: WorkflowState) => WorkflowRoute;

const ROUTE_BUILDERS: Record<WorkflowView, RouteBuilder> = {
  home: () => ({ view: 'home' }),
  history: (state) => {
    const workflowId = state.current.id ?? undefined;
    return workflowId ? { view: 'history', workflowId } : { view: 'history' };
  },
  run: (state) => {
    const workflowId = state.current.id ?? undefined;
    const runId = state.selectedRunId ?? undefined;
    if (runId) {
      return { view: 'run', runId, workflowId };
    }
    return workflowId ? { view: 'workflow', workflowId } : { view: 'workflow' };
  },
  workflow: (state) => {
    const workflowId = state.current.id ?? undefined;
    return workflowId ? { view: 'workflow', workflowId } : { view: 'workflow' };
  },
};

const DEFAULT_ROUTE_BUILDER = ROUTE_BUILDERS.workflow;

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

  const computeRouteFromState = (): WorkflowRoute => {
    const state = store.getState();
    const builder = ROUTE_BUILDERS[state.view] ?? DEFAULT_ROUTE_BUILDER;
    return builder(state);
  };
  //#endregion

  //#region Update Route
  const updateRouteFromState = (precomputed?: WorkflowRoute) => {
    if (isApplyingRoute) {
      return;
    }
    const nextRoute = precomputed ?? computeRouteFromState();
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

      if (normalizedRoute.view === 'run') {
        changeView(store, 'run', {
          runId: normalizedRoute.runId ?? null,
          clearResults: false,
        });
      } else {
        changeView(store, normalizedRoute.view);
      }
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



