import { LfButtonEventPayload, LfTreeEventPayload } from '@lf-widgets/foundations/dist';
import { ACTION_BUTTON_CLASSES } from '../elements/layout.action-button';
import { DRAWER_CLASSES } from '../elements/layout.drawer';
import { HEADER_CLASSES } from '../elements/layout.header';
import { INPUTS_CLASSES } from '../elements/main.inputs';
import { OUTPUTS_CLASSES } from '../elements/main.outputs';
import { RESULTS_CLASSES } from '../elements/main.results';
import { WorkflowStore } from '../types/state';

//#region Button Handlers
export const buttonHandler = (e: CustomEvent<LfButtonEventPayload>, store: WorkflowStore) => {
  const { comp, eventType } = e.detail;

  const { manager, view } = store.getState();

  switch (eventType) {
    case 'click':
      switch (comp.rootElement.className) {
        // Action Button
        case ACTION_BUTTON_CLASSES._:
          manager.getDispatchers().runWorkflow();
          break;

        // Drawer
        case DRAWER_CLASSES.buttonComfyUi:
          const port = window.location.port || '8188';
          window.open(`http://localhost:${port}`, '_blank');
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
