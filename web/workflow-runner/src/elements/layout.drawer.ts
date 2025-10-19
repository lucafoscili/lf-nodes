import { LfDataDataset } from '@lf-widgets/foundations/dist';
import { WorkflowSectionController } from '../types/section';
import { WorkflowState } from '../types/state';

//#region Constants
const ROOT_CLASS = 'drawer-section';
//#endregion

//#region Helpers
const _createDataset = (workflows: LfDataDataset) => {
  const dataset: LfDataDataset = {
    nodes: [{ children: workflows.nodes, id: 'workflows', value: 'Workflows' }],
  };
  return dataset;
};
const _container = (state: WorkflowState): HTMLDivElement => {
  const container = document.createElement('div');
  container.className = `${ROOT_CLASS}__container`;
  container.slot = 'content';

  container.appendChild(_tree(state));

  return container;
};
const _tree = (state: WorkflowState): HTMLLfTreeElement => {
  const { manager } = state;

  const tree = document.createElement('lf-tree');
  tree.className = `${ROOT_CLASS}__tree`;
  tree.lfAccordionLayout = true;
  tree.addEventListener('lf-tree-event', (e) => {
    const { eventType, node } = e.detail;

    switch (eventType) {
      case 'click':
        const isLeaf = !node.children || node.children.length === 0;
        if (!isLeaf) {
          return;
        }

        manager.setWorkflow(node.id);
        break;
    }
  });

  state.ui.layout.drawer.tree = tree;

  return tree;
};
//#endregion

//#region Factory
export const createDrawerSection = (): WorkflowSectionController => {
  let element: HTMLLfDrawerElement | null = null;
  let lastState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    lastState = state;
    const { ui } = state;

    element = document.createElement('lf-drawer');
    element.className = ROOT_CLASS;
    element.lfDisplay = 'slide';

    ui.layout.drawer._root = element;

    element.appendChild(_container(state));
    ui.layout._root?.appendChild(element);
  };

  const render = (state: WorkflowState) => {
    if (!element) {
      return;
    }

    lastState = state ?? lastState;
    const { ui } = state;
    const tree = ui.layout.drawer.tree;
    if (!tree || !lastState.workflows) {
      return;
    }

    tree.lfDataset = _createDataset(state.workflows);
  };

  const destroy = () => {
    element?.remove();
    if (lastState) {
      lastState.ui.layout.drawer._root = null;
      lastState.ui.layout.drawer.tree = null;
    }
    element = null;
    lastState = null;
  };

  return {
    mount,
    render,
    destroy,
  };
};
