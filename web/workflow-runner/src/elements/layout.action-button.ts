import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/button';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'action-button-section';
export const ACTION_BUTTON_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
} as const;
//#endregion

export const createActionButtonSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { ACTION_BUTTON_DESTROYED, ACTION_BUTTON_MOUNTED, ACTION_BUTTON_UPDATED } = DEBUG_MESSAGES;
  let elapsedTimer: ReturnType<typeof setTimeout> | null = null;

  const stopElapsedTimer = () => {
    if (elapsedTimer !== null) {
      clearTimeout(elapsedTimer);
      elapsedTimer = null;
    }
  };
  //#endregion

  //#region Destroy
  const destroy = () => {
    stopElapsedTimer();
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in ACTION_BUTTON_CLASSES) {
      const element = ACTION_BUTTON_CLASSES[cls];
      uiRegistry.remove(element);
    }

    debugLog(ACTION_BUTTON_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[ACTION_BUTTON_CLASSES._]) {
      return;
    }

    const _root = document.createElement('lf-button');
    _root.className = theme.bemClass(ACTION_BUTTON_CLASSES._);
    _root.lfIcon = 'send';
    _root.lfLabel = 'Run';
    _root.lfStyling = 'floating';
    _root.title = 'Run current workflow';
    _root.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(ACTION_BUTTON_CLASSES._, _root);

    debugLog(ACTION_BUTTON_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const _root = elements[ACTION_BUTTON_CLASSES._] as HTMLLfButtonElement;
    if (!_root) {
      return;
    }

    const activeRun = state.runs.find(
      (run) =>
        run.runId === state.currentRunId && ['pending', 'running'].includes(run.status),
    );
    const submissionBusy = Boolean(state.submissionInFlightId && !activeRun);
    const cancellationBusy = Boolean(
      activeRun &&
        (state.cancelInFlightRunId === activeRun.runId || activeRun.cancelRequested),
    );

    stopElapsedTimer();
    if (activeRun) {
      const elapsedSeconds = Math.max(0, Math.floor((Date.now() - activeRun.createdAt) / 1000));
      _root.dataset.mode = cancellationBusy ? 'stopping' : 'stop';
      _root.lfAriaLabel = cancellationBusy
        ? 'Stopping current workflow run'
        : 'Stop current workflow run';
      _root.lfIcon = 'x';
      _root.lfLabel = cancellationBusy ? `Stopping · ${elapsedSeconds}s` : `Stop · ${elapsedSeconds}s`;
      _root.lfShowSpinner = true;
      _root.lfUiState = cancellationBusy || !activeRun.submissionId ? 'disabled' : 'danger';
      _root.title = cancellationBusy
        ? `Cancellation requested for ${activeRun.runId}`
        : `Stop ${activeRun.status} run ${activeRun.runId}`;
      if (typeof _root.setAttribute === 'function') {
        _root.setAttribute('aria-busy', 'true');
      }
      elapsedTimer = setTimeout(render, 1000);
    } else if (submissionBusy) {
      _root.dataset.mode = 'starting';
      _root.lfAriaLabel = 'Starting workflow run';
      _root.lfIcon = 'send';
      _root.lfLabel = 'Starting…';
      _root.lfShowSpinner = true;
      _root.lfUiState = 'disabled';
      _root.title = `Submitting ${state.submissionInFlightId}`;
      if (typeof _root.setAttribute === 'function') {
        _root.setAttribute('aria-busy', 'true');
      }
    } else {
      const workflow = manager.workflow?.current?.();
      const setupRequired = workflow?.readiness?.status === 'setup_required';
      const setupMessage = workflow?.readiness?.issues?.[0]?.message;
      _root.dataset.mode = setupRequired ? 'setup-required' : 'run';
      _root.lfAriaLabel = setupRequired ? 'Workflow setup required' : 'Run current workflow';
      _root.lfIcon = setupRequired ? theme.get.icon('alertTriangle') : 'send';
      _root.lfLabel = setupRequired ? 'Setup required' : 'Run';
      _root.lfShowSpinner = false;
      _root.lfUiState = state.current.id && !setupRequired ? 'primary' : 'disabled';
      _root.title = setupRequired
        ? setupMessage || 'Install the required workflow dependencies before running.'
        : 'Run current workflow';
      if (typeof _root.removeAttribute === 'function') {
        _root.removeAttribute('aria-busy');
      }
    }

    debugLog(ACTION_BUTTON_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
