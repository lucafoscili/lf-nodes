import { LfDataDataset } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { drawerNavigation } from '../handlers/layout';
import { WorkflowAPIDataset, WorkflowLFNode } from '../types/api';
import { WorkflowSectionController } from '../types/section';
import { WorkflowState, WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'drawer-section';
export const DRAWER_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  container: theme.bemClass(ROOT_CLASS, 'container'),
  tree: theme.bemClass(ROOT_CLASS, 'tree'),
} as const;
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
      category = { icon: _getIcon(name), id: name, value: name, children: [] };
      categories.push(category);
    }
    category.children.push(node);
  });

  const dataset: LfDataDataset = {
    nodes: [root],
  };

  return dataset;
};
const _getIcon = (category: string) => {
  const { alertTriangle, codeCircle2, json } = getLfFramework().theme.get.icons();
  const category_icons = {
    SVG: codeCircle2,
    JSON: json,
  };

  return category_icons[category] || alertTriangle;
};
const _container = (state: WorkflowState) => {
  const container = document.createElement('div');
  container.className = DRAWER_CLASSES.container;
  container.slot = 'content';

  const tree = _tree(state);
  container.appendChild(tree);

  return { container, tree };
};
const _tree = (state: WorkflowState) => {
  const tree = document.createElement('lf-tree');
  tree.className = DRAWER_CLASSES.tree;
  tree.lfAccordionLayout = true;
  tree.addEventListener('lf-tree-event', (e) => drawerNavigation(e, state));

  return tree;
};
//#endregion

export const createDrawerSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { DRAWER_DESTROYED, DRAWER_MOUNTED, DRAWER_UPDATED } = DEBUG_MESSAGES;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const state = store.getState();
    if (!state.manager) {
      return;
    }

    const { uiRegistry } = state.manager;

    for (const cls in DRAWER_CLASSES) {
      const element = DRAWER_CLASSES[cls];
      uiRegistry.remove(element);
    }

    debugLog(DRAWER_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[DRAWER_CLASSES._]) {
      return;
    }

    const _root = document.createElement('lf-drawer');
    _root.className = ROOT_CLASS;
    _root.lfDisplay = 'slide';

    const { container, tree } = _container(state);
    _root.appendChild(container);
    manager.getAppRoot().appendChild(_root);

    uiRegistry.set(DRAWER_CLASSES._, _root);
    uiRegistry.set(DRAWER_CLASSES.container, container);
    uiRegistry.set(DRAWER_CLASSES.tree, tree);

    debugLog(DRAWER_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const state = store.getState();
    const { manager, workflows } = state;
    const { uiRegistry } = manager;

    if (!manager) {
      return;
    }

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const tree = elements[DRAWER_CLASSES.tree] as HTMLLfTreeElement;
    if (tree) {
      tree.lfDataset = _createDataset(workflows);
    }

    debugLog(DRAWER_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
