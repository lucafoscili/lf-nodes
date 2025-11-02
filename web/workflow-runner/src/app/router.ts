import { WorkflowRoute } from '../types/state';

const RUN_PARAM = 'runId';
const VIEW_PARAM = 'view';
const WORKFLOW_PARAM = 'workflowId';

export const parseRouteFromLocation = (location: Location = window.location): WorkflowRoute => {
  const params = new URLSearchParams(location.search);
  const runId = params.get(RUN_PARAM);
  const workflowId = params.get(WORKFLOW_PARAM);
  const viewParam = params.get(VIEW_PARAM);

  if (runId) {
    return {
      view: 'run',
      runId,
      workflowId,
    };
  }

  if (viewParam === 'history') {
    return {
      view: 'history',
      workflowId,
    };
  }

  if (viewParam === 'home') {
    return {
      view: 'home',
    };
  }

  if (workflowId) {
    return {
      view: 'workflow',
      workflowId,
    };
  }

  return {
    view: 'home',
  };
};

export const routesEqual = (a: WorkflowRoute | null, b: WorkflowRoute | null): boolean => {
  if (a === b) {
    return true;
  }
  if (!a || !b) {
    return false;
  }
  return (
    a.view === b.view &&
    (a.workflowId ?? null) === (b.workflowId ?? null) &&
    (a.runId ?? null) === (b.runId ?? null)
  );
};

export const replaceRouteInHistory = (route: WorkflowRoute) => {
  const params = new URLSearchParams();

  switch (route.view) {
    case 'history':
      params.set(VIEW_PARAM, 'history');
      if (route.workflowId) {
        params.set(WORKFLOW_PARAM, route.workflowId);
      }
      break;
    case 'run':
      if (route.runId) {
        params.set(RUN_PARAM, route.runId);
      }
      if (route.workflowId) {
        params.set(WORKFLOW_PARAM, route.workflowId);
      }
      params.set(VIEW_PARAM, 'run');
      break;
    case 'workflow':
      if (route.workflowId) {
        params.set(WORKFLOW_PARAM, route.workflowId);
      }
      break;
    case 'home':
    default:
      break;
  }

  const query = params.toString();
  const url = query ? `${window.location.pathname}?${query}` : window.location.pathname;
  window.history.replaceState({}, '', url);
};

export const subscribeToRouteChanges = (callback: (route: WorkflowRoute) => void) => {
  const handler = () => callback(parseRouteFromLocation());
  window.addEventListener('popstate', handler);
  return () => window.removeEventListener('popstate', handler);
};
