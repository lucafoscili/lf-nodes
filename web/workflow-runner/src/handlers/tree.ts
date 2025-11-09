import { LfTreeEventPayload } from '@lf-widgets/foundations/dist';
import { DRAWER_CLASSES } from '../elements/layout.drawer';
import { WorkflowStore } from '../types/state';

//#region Tree handlers
export const treeHandler = (e: CustomEvent<LfTreeEventPayload>, store: WorkflowStore) => {
  const { comp, eventType, node } = e.detail;

  const state = store.getState();
  const { manager } = state;
  const elements = manager.uiRegistry.get();
  const drawer = elements[DRAWER_CLASSES._] as HTMLLfDrawerElement;

  switch (eventType) {
    case 'click':
      switch (comp.rootElement.className) {
        case DRAWER_CLASSES.tree:
          if (!manager) {
            return;
          }

          const isLeaf = !node.children || node.children.length === 0;
          const isHome = node.id === 'home';

          if (isHome) {
            state.mutate.view('home');
          } else if (isLeaf) {
            state.mutate.workflow(node.id);
          }

          drawer.close();
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
