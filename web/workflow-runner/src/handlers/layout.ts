import { LfButtonEventPayload, LfTreeEventPayload } from '@lf-widgets/foundations/dist';
import { DRAWER_CLASSES } from '../elements/layout.drawer';
import { WorkflowState } from '../types/state';

//#region Button Handlers
export const openGithubRepo = (e: CustomEvent<LfButtonEventPayload>) => {
  const { eventType } = e.detail;

  switch (eventType) {
    case 'click':
      window.open('https://github.com/lucafoscili/lf-nodes', '_blank');
      break;
    default:
      return;
  }
};
export const toggleDebug = (e: CustomEvent<LfButtonEventPayload>, state: WorkflowState) => {
  const { eventType } = e.detail;

  const { manager } = state;

  switch (eventType) {
    case 'click':
      manager.toggleDebug();
      break;
    default:
      return;
  }
};
export const toggleDrawer = (e: CustomEvent<LfButtonEventPayload>, state: WorkflowState) => {
  const { eventType } = e.detail;

  const { manager } = state;
  const elements = manager.uiRegistry.get();
  const drawer = elements[DRAWER_CLASSES._] as HTMLLfDrawerElement;

  switch (eventType) {
    case 'click':
      drawer.toggle();
      break;
    default:
      return;
  }
};
//#endregion

//#region Tree handlers
export const drawerNavigation = (e: CustomEvent<LfTreeEventPayload>, state: WorkflowState) => {
  const { eventType, node } = e.detail;

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
        manager.setWorkflow(node.id);
        drawer.close();
      }
      break;
  }
};
//#endregion
