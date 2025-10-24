import { LfDataDataset } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { drawerNavigation, openGithubRepo, toggleDebug } from '../handlers/layout';
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
  button: theme.bemClass(ROOT_CLASS, 'button'),
  buttonDebug: theme.bemClass(ROOT_CLASS, 'button', { toggable: true }),
  container: theme.bemClass(ROOT_CLASS, 'container'),
  footer: theme.bemClass(ROOT_CLASS, 'footer'),
  tree: theme.bemClass(ROOT_CLASS, 'tree'),
} as const;
//#endregion

//#region Helpers
const _footer = (state: WorkflowState) => {
  const footer = document.createElement('div');
  footer.className = DRAWER_CLASSES.footer;

  const github = document.createElement('lf-button');
  github.className = DRAWER_CLASSES.button;
  github.lfIcon = getLfFramework().theme.get.icon('brandGithub');
  github.lfStyling = 'icon';
  github.lfUiSize = 'small';
  github.addEventListener('lf-button-event', (e) => openGithubRepo(e));

  const debug = document.createElement('lf-button');
  debug.className = DRAWER_CLASSES.buttonDebug;
  debug.lfIcon = getLfFramework().theme.get.icon('bug');
  debug.lfStyling = 'icon';
  debug.lfUiSize = 'small';
  debug.addEventListener('lf-button-event', (e) => toggleDebug(e, state));

  footer.appendChild(github);
  footer.appendChild(debug);

  return { footer, debug, github };
};
const _container = (state: WorkflowState) => {
  const container = document.createElement('div');
  container.className = DRAWER_CLASSES.container;
  container.slot = 'content';

  const { footer, debug, github } = _footer(state);
  const tree = _tree(state);
  container.appendChild(tree);
  container.appendChild(footer);

  return { footer, container, debug, github, tree };
};
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
  const lastDebug: boolean | null = null;
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

    const { footer, debug, github, container, tree } = _container(state);
    _root.appendChild(container);
    manager.getAppRoot().appendChild(_root);

    uiRegistry.set(DRAWER_CLASSES._, _root);
    uiRegistry.set(DRAWER_CLASSES.button, footer);
    uiRegistry.set(DRAWER_CLASSES.container, container);
    uiRegistry.set(DRAWER_CLASSES.buttonDebug, debug);
    uiRegistry.set(DRAWER_CLASSES.button, github);
    uiRegistry.set(DRAWER_CLASSES.tree, tree);

    debugLog(DRAWER_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const state = store.getState();
    const { manager, workflows } = state;
    const { uiRegistry } = manager;
    const isDebug = manager.isDebugEnabled();

    if (!manager) {
      return;
    }

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const debug = elements[DRAWER_CLASSES.buttonDebug] as HTMLLfButtonElement;
    const tree = elements[DRAWER_CLASSES.tree] as HTMLLfTreeElement;

    if (debug) {
      debug.lfUiState = isDebug ? 'warning' : 'primary';
      debug.title = isDebug ? 'Hide developer console' : 'Show developer console';
    }

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
