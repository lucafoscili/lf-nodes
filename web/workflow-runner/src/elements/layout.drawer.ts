import { LfDataDataset, LfIconType } from '@lf-widgets/foundations/dist';
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
  const { article, folderOpen, lfSignature, listTree } = getLfFramework().theme.get.icons();
  const fallback = folderOpen || article || listTree || lfSignature;

  const shippedCategories: Array<WorkflowLFNode & { children: WorkflowLFNode[] }> = [];
  const customCollections: Array<WorkflowLFNode & { children: WorkflowLFNode[] }> = [];
  const home = { icon: article || fallback, id: 'home', value: 'Home' };
  const shipped = {
    icon: lfSignature || fallback,
    id: 'workflows:shipped',
    value: 'LF Nodes',
    children: shippedCategories,
  };
  const custom = {
    icon: folderOpen || fallback,
    id: 'workflows:custom',
    value: 'Custom',
    children: customCollections,
  };
  const roots: Array<WorkflowLFNode & { children: WorkflowLFNode[] }> = [];
  const wfs = { icon: listTree || fallback, id: 'workflows', value: 'Workflows', children: roots };

  const clone: WorkflowAPIDataset = JSON.parse(JSON.stringify(workflows));

  clone.nodes?.forEach((node) => {
    node.children = undefined;
    const issue = node.readiness?.issues?.[0]?.message;
    if (node.readiness?.status === 'setup_required') {
      node.icon = getLfFramework().theme.get.icon('alertTriangle');
      node.description = `Setup required${issue ? `: ${issue}` : '.'}`;
    } else if (node.readiness?.status === 'warning') {
      node.icon = getLfFramework().theme.get.icon('hexagonInfo');
      node.description = `Check setup${issue ? `: ${issue}` : '.'}`;
    }
    // Only explicitly packaged records enter LF Nodes. Missing or malformed
    // provenance fails closed into Custom instead of borrowing LF's identity.
    const isCustom = node.origin !== 'shipped';
    const name = isCustom ? node.collection || 'Custom' : node.category || 'Uncategorized';
    const groups = isCustom ? customCollections : shippedCategories;
    let group = groups.find((item) => item.value === name);
    if (!group) {
      group = {
        icon: isCustom ? _getIcon('Custom') : _getIcon(name),
        id: `${isCustom ? 'custom' : 'shipped'}:${name}`,
        value: name,
        children: [],
      };
      groups.push(group);
    }
    group.children.push(node);
  });

  shippedCategories.sort((a, b) => String(a.value).localeCompare(String(b.value)));
  customCollections.sort((a, b) => String(a.value).localeCompare(String(b.value)));
  if (shippedCategories.length) {
    roots.push(shipped);
  }
  if (customCollections.length) {
    roots.push(custom);
  }

  const dataset: LfDataDataset = {
    nodes: [home, wfs],
  };

  return dataset;
};
const _getIcon = (category: string) => {
  const { ai, codeCircle2, folder, folderOpen, json, music, photo, robot, wand } =
    getLfFramework().theme.get.icons();
  const fallback = folder || folderOpen || photo;
  const category_icons = {
    Audio: music,
    Custom: folderOpen,
    'Image Processing': wand,
    JSON: json,
    'Krea 2': ai,
    'MiniMax H3': ai,
    'TRELLIS.2': ai,
    TripoSplat: ai,
    LLM: robot,
    'Media Intake': folderOpen,
    SVG: codeCircle2,
    'Text to Image': photo,
  };

  return category_icons[category] || fallback;
};
const _button = (store: WorkflowStore, icon: LfIconType, label: string, className: string) => {
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
