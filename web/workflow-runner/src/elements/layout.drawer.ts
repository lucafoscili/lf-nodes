import { LfDataDataset } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/button';
import { treeHandler } from '../handlers/tree';
import { WorkflowAPIDataset, WorkflowLFNode } from '../types/api';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'drawer-section';
export const DRAWER_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  buttonComfyUi: theme.bemClass(ROOT_CLASS, 'button-comfyui'),
  buttonDebug: theme.bemClass(ROOT_CLASS, 'button-debug'),
  buttonGithub: theme.bemClass(ROOT_CLASS, 'button-github'),
  container: theme.bemClass(ROOT_CLASS, 'container'),
  footer: theme.bemClass(ROOT_CLASS, 'footer'),
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

  categories.sort((a, b) => String(a.value).localeCompare(String(b.value)));

  return dataset;
};
const _getIcon = (category: string) => {
  const { alertTriangle, codeCircle2, photo, json, robot, wand } =
    getLfFramework().theme.get.icons();
  const category_icons = {
    'Image Processing': wand,
    JSON: json,
    LLM: robot,
    SVG: codeCircle2,
    'Text to Image': photo,
  };

  return category_icons[category] || alertTriangle;
};
const _button = (store: WorkflowStore, icon: string, label: string, className: string) => {
  const button = document.createElement('lf-button');
  button.className = className;
  button.lfAriaLabel = label;
  button.lfIcon = icon;
  button.lfStyling = 'icon';
  button.lfUiSize = 'small';
  button.title = label;
  button.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  return button;
};
const _container = (store: WorkflowStore) => {
  const container = document.createElement('div');
  container.className = DRAWER_CLASSES.container;
  container.slot = 'content';

  const { comfyUi, debug, footer, github } = _footer(store);
  const tree = _tree(store);
  container.appendChild(tree);
  container.appendChild(footer);

  return { comfyUi, container, debug, footer, github, tree };
};
const _footer = (store: WorkflowStore) => {
  const footer = document.createElement('div');
  footer.className = DRAWER_CLASSES.footer;

  let icon = getLfFramework().theme.get.icon('imageInPicture');
  let label = 'Open ComfyUI';
  const comfyUi = _button(store, icon, label, DRAWER_CLASSES.buttonComfyUi);

  icon = getLfFramework().theme.get.icon('bug');
  label = 'Toggle developer console';
  const debug = _button(store, icon, label, DRAWER_CLASSES.buttonDebug);

  icon = getLfFramework().theme.get.icon('brandGithub');
  label = 'Open GitHub repository';
  const github = _button(store, icon, label, DRAWER_CLASSES.buttonGithub);

  footer.appendChild(github);
  footer.appendChild(comfyUi);
  footer.appendChild(debug);

  return { comfyUi, debug, footer, github };
};
const _tree = (store: WorkflowStore) => {
  const tree = document.createElement('lf-tree');
  tree.className = DRAWER_CLASSES.tree;
  tree.lfAccordionLayout = true;
  tree.addEventListener('lf-tree-event', (e) => treeHandler(e, store));

  return tree;
};
//#endregion

export const createDrawerSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { DRAWER_DESTROYED, DRAWER_MOUNTED, DRAWER_UPDATED } = DEBUG_MESSAGES;
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in DRAWER_CLASSES) {
      const element = DRAWER_CLASSES[cls];
      uiRegistry.remove(element);
    }

    debugLog(DRAWER_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[DRAWER_CLASSES._]) {
      return;
    }

    const _root = document.createElement('lf-drawer');
    _root.className = ROOT_CLASS;
    _root.lfDisplay = 'slide';

    const { comfyUi, debug, footer, github, container, tree } = _container(store);
    _root.appendChild(container);
    manager.getAppRoot().appendChild(_root);

    uiRegistry.set(DRAWER_CLASSES._, _root);
    uiRegistry.set(DRAWER_CLASSES.buttonComfyUi, comfyUi);
    uiRegistry.set(DRAWER_CLASSES.buttonDebug, debug);
    uiRegistry.set(DRAWER_CLASSES.footer, footer);
    uiRegistry.set(DRAWER_CLASSES.buttonGithub, github);
    uiRegistry.set(DRAWER_CLASSES.container, container);
    uiRegistry.set(DRAWER_CLASSES.tree, tree);

    debugLog(DRAWER_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const state = store.getState();
    const { isDebug, manager, workflows } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const debug = elements[DRAWER_CLASSES.buttonDebug] as HTMLLfButtonElement;
    const tree = elements[DRAWER_CLASSES.tree] as HTMLLfTreeElement;

    debug.lfUiState = isDebug ? 'warning' : 'primary';
    debug.title = isDebug ? 'Hide developer console' : 'Show developer console';
    tree.lfDataset = _createDataset(workflows);

    debugLog(DRAWER_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
