import { LfButtonEventPayload, LfTreeEventPayload } from '@lf-widgets/foundations/dist';
import { ACTION_BUTTON_CLASSES } from '../elements/layout.action-button';
import { DRAWER_CLASSES } from '../elements/layout.drawer';
import { HEADER_CLASSES } from '../elements/layout.header';
import { INPUTS_CLASSES } from '../elements/main.inputs';
import { OUTPUTS_CLASSES } from '../elements/main.outputs';
import { RESULTS_CLASSES } from '../elements/main.results';
import { WorkflowStore } from '../types/state';
import { resolveComfyUrl } from '../utils/comfy-url';

const HISTORY_CLEANUP_IN_FLIGHT = new WeakSet<HTMLElement>();

const _historyCleanupNotification = (
  store: WorkflowStore,
  message: string,
  status: 'danger' | 'info',
) => {
  store.getState().mutate.notifications.add({
    id: `${performance.now()}-${Math.random()}`,
    message,
    status,
  });
};

export const removeMissingHistory = async (
  button: HTMLLfButtonElement,
  store: WorkflowStore,
) => {
  if (HISTORY_CLEANUP_IN_FLIGHT.has(button) || store.getState().view !== 'history') {
    return;
  }

  HISTORY_CLEANUP_IN_FLIGHT.add(button);
  button.lfAriaLabel = 'Checking Runner history for missing outputs';
  button.lfLabel = 'Checking…';
  button.lfShowSpinner = true;
  button.lfUiState = 'disabled';
  button.setAttribute('aria-busy', 'true');

  try {
    const { manager } = store.getState();
    const preview = await manager.runs.pruneMissingArtifacts(true);
    if (preview.candidate_count === 0) {
      const preserved = preview.skipped_unknown
        ? ` ${preview.skipped_unknown} ambiguous or fileless successful run${preview.skipped_unknown === 1 ? ' was' : 's were'} preserved.`
        : '';
      _historyCleanupNotification(
        store,
        `No missing-output or failed runs to remove.${preserved}`,
        'info',
      );
      return;
    }

    const count = preview.candidate_count;
    const confirmed = window.confirm(
      `Remove ${count} run${count === 1 ? '' : 's'} from Runner history?\n\n` +
        'This removes Runner history and saved remix inputs for successful runs whose outputs are missing, plus failed, cancelled, and timed-out runs. It never deletes files and preserves ambiguous or fileless successful runs.',
    );
    if (!confirmed) {
      return;
    }

    button.lfAriaLabel = 'Removing stale Runner history';
    button.lfLabel = 'Removing…';
    const result = await manager.runs.pruneMissingArtifacts(false, preview.candidate_run_ids);
    const removed = result.removed_count;
    const preserved = result.skipped_unknown
      ? ` ${result.skipped_unknown} ambiguous or fileless successful run${result.skipped_unknown === 1 ? ' was' : 's were'} preserved.`
      : '';
    const changed = result.skipped_changed
      ? ` ${result.skipped_changed} run${result.skipped_changed === 1 ? ' changed' : 's changed'} during cleanup and ${result.skipped_changed === 1 ? 'was' : 'were'} left untouched.`
      : '';
    _historyCleanupNotification(
      store,
      `Removed ${removed} stale run${removed === 1 ? '' : 's'} from Runner history. No files were deleted.${preserved}${changed}`,
      'info',
    );
  } catch (error) {
    const detail = error instanceof Error && error.message ? ` ${error.message}` : '';
    _historyCleanupNotification(store, `Unable to clean Runner history.${detail}`, 'danger');
  } finally {
    HISTORY_CLEANUP_IN_FLIGHT.delete(button);
    button.removeAttribute('aria-busy');
    button.lfAriaLabel = 'Remove stale Runner history entries';
    button.lfLabel = 'Remove missing';
    button.lfShowSpinner = false;
    button.lfUiState = store.getState().view === 'history' ? 'danger' : 'disabled';
  }
};

//#region Button Handlers
export const buttonHandler = (e: CustomEvent<LfButtonEventPayload>, store: WorkflowStore) => {
  const { comp, eventType } = e.detail;

  const { manager, view } = store.getState();

  switch (eventType) {
    case 'click':
      switch (comp.rootElement.className) {
        // Action Button
        case ACTION_BUTTON_CLASSES._: {
          const state = store.getState();
          const activeRun = state.runs.find(
            (run) =>
              run.runId === state.currentRunId && ['pending', 'running'].includes(run.status),
          );
          if (activeRun && manager.getDispatchers().cancelWorkflow) {
            void manager.getDispatchers().cancelWorkflow();
          } else if (!state.submissionInFlightId) {
            void manager.getDispatchers().runWorkflow();
          }
          break;
        }

        // Drawer
        case DRAWER_CLASSES.buttonComfyUi:
          window.open(resolveComfyUrl(), '_blank', 'noopener,noreferrer');
          break;
        case DRAWER_CLASSES.buttonDebug:
          store.getState().mutate.isDebug(!store.getState().isDebug);
          break;
        case DRAWER_CLASSES.buttonGithub:
          window.open('https://github.com/lucafoscili/lf-nodes', '_blank');
          break;

        // Header
        case HEADER_CLASSES.drawerToggle:
          const elements = manager.uiRegistry.get();
          const drawer = elements[DRAWER_CLASSES._] as HTMLLfDrawerElement;
          drawer.toggle();
          break;

        // Workflow
        case HEADER_CLASSES.serverIndicatorLight:
        case RESULTS_CLASSES.history:
          manager.runs.select(null, 'history');
          break;
        case INPUTS_CLASSES.openButton:
          manager.workflow.download();
          break;
        case OUTPUTS_CLASSES.toggle:
          const isHistoryView = view === 'history';
          if (isHistoryView) {
            manager.runs.select(null, 'workflow');
          } else {
            manager.runs.select(null, 'history');
          }
          break;
        case RESULTS_CLASSES.back:
          manager.runs.select(null, 'workflow');
          break;
        case RESULTS_CLASSES.remix:
          if (manager.runs.selected() && manager.runs.remix) {
            manager.runs.remix(manager.runs.selected().runId);
          }
          break;
        case OUTPUTS_CLASSES.cleanup:
          void removeMissingHistory(comp.rootElement as HTMLLfButtonElement, store);
          break;
        default:
          return;
      }
      break;
    default:
      return;
  }
};
//#endregion

//#region Tree handlers
export const drawerNavigation = (e: CustomEvent<LfTreeEventPayload>, store: WorkflowStore) => {
  const { eventType, node } = e.detail;

  const state = store.getState();
  const { manager } = state;
  const elements = manager.uiRegistry.get();
  const drawer = elements[DRAWER_CLASSES._] as HTMLLfDrawerElement;

  switch (eventType) {
    case 'click':
      if (!manager) {
        return;
      }

      const isLeaf = !node.children || node.children.length === 0;
      if (isLeaf) {
        state.mutate.workflow(node.id);
        drawer.close();
      }
      break;
  }
};
//#endregion
