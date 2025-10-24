import { LfButtonEventPayload, LfTreeEventPayload } from '@lf-widgets/foundations/dist';
import { DRAWER_CLASSES } from '../elements/layout.drawer';
import { WorkflowStore } from '../types/state';

//#region Button Handlers
export const openComfyUI = (e: CustomEvent<LfButtonEventPayload>) => {
  const { eventType } = e.detail;

  switch (eventType) {
    case 'click':
      const port = window.location.port || '3000';
      window.open(`http://localhost:${port}`, '_blank');
  }
};
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
export const toggleDebug = (e: CustomEvent<LfButtonEventPayload>, store: WorkflowStore) => {
  const { eventType } = e.detail;

  const { manager } = store.getState();

  switch (eventType) {
    case 'click':
      manager.toggleDebug();
      break;
    default:
      return;
  }
};
export const toggleDrawer = (e: CustomEvent<LfButtonEventPayload>, store: WorkflowStore) => {
  const { eventType } = e.detail;

  const { manager } = store.getState();
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
export const drawerNavigation = (e: CustomEvent<LfTreeEventPayload>, store: WorkflowStore) => {
  const { eventType, node } = e.detail;

  const { manager } = store.getState();
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
