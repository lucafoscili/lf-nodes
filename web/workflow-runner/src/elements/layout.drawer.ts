import { LfDataDataset } from '@lf-widgets/foundations/dist';
import { WorkflowAPIDataset, WorkflowLFNode } from '../types/api';
import { WorkflowSectionController } from '../types/section';
import { WorkflowState } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region Constants
const ROOT_CLASS = 'drawer-section';
//#endregion

//#region Helpers
const _createDataset = (workflows: WorkflowAPIDataset) => {
  const categories: Array<WorkflowLFNode & { children: WorkflowLFNode[] }> = [];
  const root = { id: 'workflows', value: 'Workflows', children: categories };

  const clone: WorkflowAPIDataset = JSON.parse(JSON.stringify(workflows));
  clone.nodes?.forEach((child) => {
    child.children = undefined;
  });

  clone.nodes?.forEach((node) => {
    const name = node?.category || 'Uncategorized';
    let category = categories.find((cat) => cat.value === name);
    if (!category) {
      category = { id: name, value: name, children: [] };
      categories.push(category);
    }
    category.children.push(node);
  });

  const dataset: LfDataDataset = {
    nodes: [root],
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
        if (!manager) {
          return;
        }

        const isLeaf = !node.children || node.children.length === 0;
        if (isLeaf) {
          manager.setWorkflow(node.id);
        }
        break;
    }
  });

  state.mutate.ui((ui) => {
    ui.layout.drawer.tree = tree;
  });

  return tree;
};
//#endregion

//#region Factory
export const createDrawerSection = (): WorkflowSectionController => {
  const { DRAWER_DESTROYED, DRAWER_MOUNTED, DRAWER_UPDATED } = DEBUG_MESSAGES;

  let element: HTMLLfDrawerElement | null = null;
  let lastState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    lastState = state;
    const { ui } = state;

    element = document.createElement('lf-drawer');
    element.className = ROOT_CLASS;
    element.lfDisplay = 'slide';

    state.mutate.ui((ui) => {
      ui.layout.drawer._root = element;
    });

    element.appendChild(_container(state));
    ui.layout._root?.appendChild(element);

    debugLog(DRAWER_MOUNTED, 'informational', {
      workflowCount: state.workflows?.nodes?.length ?? 0,
    });
  };

  const render = (state: WorkflowState) => {
    if (!element) {
      return;
    }

    const previousState = lastState;
    lastState = state;

    const { ui } = state;
    const tree = ui.layout.drawer.tree;
    if (!tree) {
      return;
    }

    if (previousState?.workflows !== state.workflows) {
      debugLog(DRAWER_UPDATED, 'informational', {
        workflowCount: state.workflows?.nodes?.length ?? 0,
      });
    }

    tree.lfDataset = _createDataset(state.workflows);
  };

  const destroy = () => {
    element?.remove();
    if (lastState) {
      lastState.mutate.ui((ui) => {
        ui.layout.drawer._root = null;
        ui.layout.drawer.tree = null;
      });
      debugLog(DRAWER_DESTROYED, 'informational', {});
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
