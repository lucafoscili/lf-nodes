import "../../js/lf-widgets-core-DIEht-jK.js";
import { g as getLfFramework } from "../../js/lf-widgets-framework-DcaHVr-f.js";
import "../../js/lf-widgets-foundations-Bbv1isuU.js";
const apiBase = "/api";
const apiRoutePrefix = "/lf-nodes";
const chat = { "provider": "kobold" };
const staticPaths = { "assets": "/lf-nodes/static/assets/" };
const theme$a = "dark";
const runnerConfig = {
  apiBase,
  apiRoutePrefix,
  chat,
  staticPaths,
  theme: theme$a
};
const API_BASE = runnerConfig.apiBase;
const API_ROUTE_PREFIX = runnerConfig.apiRoutePrefix;
const API_ROOT = `${API_BASE}${API_ROUTE_PREFIX}`;
const CHAT_CFG = runnerConfig.chat;
const ensureLeadingSlash = (p) => p ? p.startsWith("/") ? p : `/${p}` : void 0;
const CHAT_ENDPOINT = `${API_ROOT}${ensureLeadingSlash(CHAT_CFG.path ?? `/proxy/${CHAT_CFG.provider}`)}`;
const DEFAULT_STATUS_MESSAGES = {
  idle: "Ready.",
  running: "Running...",
  error: "An error occurred while running the workflow."
};
const DEFAULT_THEME = runnerConfig.theme;
const STATIC_ASSETS_PATH = runnerConfig.staticPaths.assets;
const buildApiUrl = (path) => `${API_ROOT}${path.startsWith("/") ? path : `/${path}`}`;
const buildAssetsUrl = (origin = window.location.origin) => `${origin}${API_BASE}${STATIC_ASSETS_PATH.startsWith("/") ? STATIC_ASSETS_PATH : `/${STATIC_ASSETS_PATH}`}`;
const addNotification = (store, notification) => {
  store.getState().mutate.notifications.add(notification);
};
const clearResults = (store) => {
  store.getState().mutate.results(null);
};
const setStatus$1 = (store, status, message) => {
  store.getState().mutate.status(status, message);
};
const setView = (store, view) => {
  const state = store.getState();
  if (state.view !== view) {
    state.mutate.view(view);
  }
};
const setRunInFlight = (store, runId) => {
  const state = store.getState();
  if (state.currentRunId === runId) {
    return;
  }
  state.mutate.runId(runId);
};
const selectRun = (store, runId, options) => {
  const state = store.getState();
  state.mutate.selectRun(runId);
  const shouldClearResults = (options == null ? void 0 : options.clearResults) ?? !runId;
  if (shouldClearResults) {
    state.mutate.results(null);
  }
};
const upsertRun = (store, entry) => {
  store.getState().mutate.runs.upsert(entry);
};
const ACTIVE_STATUSES = /* @__PURE__ */ new Set(["pending", "running"]);
const ensureActiveRun = (store, preferredRunId) => {
  const state = store.getState();
  const activeRuns = state.runs.filter((run) => ACTIVE_STATUSES.has(run.status));
  const currentRunId = state.currentRunId;
  if (currentRunId && activeRuns.some((run) => run.runId === currentRunId)) {
    return;
  }
  const preferred = preferredRunId !== void 0 ? activeRuns.find((run) => run.runId === preferredRunId) ?? null : null;
  const nextRun = preferred ?? activeRuns.slice().sort((a, b) => {
    if (a.createdAt !== b.createdAt) {
      return a.createdAt - b.createdAt;
    }
    return a.updatedAt - b.updatedAt;
  }).shift() ?? null;
  if (!nextRun) {
    if (currentRunId !== null) {
      setRunInFlight(store, null);
      setStatus$1(store, "idle");
    }
    return;
  }
  if (nextRun.runId !== currentRunId) {
    setRunInFlight(store, nextRun.runId);
  }
};
const DEBUG_MESSAGES = {
  ACTION_BUTTON_DESTROYED: "Action button section destroyed.",
  ACTION_BUTTON_MOUNTED: "Action button section mounted.",
  ACTION_BUTTON_UPDATED: "Action button section refreshed.",
  DEV_SECTION_DESTROYED: "Dev section destroyed.",
  DEV_SECTION_MOUNTED: "Dev section mounted.",
  DEV_SECTION_UPDATED: "Dev section refreshed.",
  DRAWER_DESTROYED: "Drawer section destroyed.",
  DRAWER_MOUNTED: "Drawer section mounted.",
  DRAWER_UPDATED: "Drawer section refreshed.",
  HEADER_DESTROYED: "Header section destroyed.",
  HEADER_MOUNTED: "Header section mounted.",
  HEADER_UPDATED: "Header section refreshed.",
  HOME_DESTROYED: "Home section destroyed.",
  HOME_MOUNTED: "Home section mounted.",
  HOME_UPDATED: "Home section refreshed.",
  INPUTS_COLLECTED: "Collected workflow inputs.",
  MAIN_DESTROYED: "Main section destroyed.",
  MAIN_MOUNTED: "Main section mounted.",
  MAIN_UPDATED: "Main section refreshed.",
  NOTIFICATIONS_DESTROYED: "Notifications section destroyed.",
  NOTIFICATIONS_MOUNTED: "Notifications section mounted.",
  NOTIFICATIONS_UPDATED: "Notifications section refreshed.",
  WORKFLOW_INPUT_FLAGGED: "Workflow input flagged.",
  WORKFLOW_INPUTS_DESTROYED: "Workflow inputs destroyed.",
  WORKFLOW_INPUTS_MOUNTED: "Workflow inputs mounted.",
  WORKFLOW_INPUTS_UPDATED: "Workflow inputs refreshed.",
  WORKFLOW_OUTPUTS_DESTROYED: "Workflow outputs destroyed.",
  WORKFLOW_OUTPUTS_MOUNTED: "Workflow outputs mounted.",
  WORKFLOW_OUTPUTS_UPDATED: "Workflow outputs refreshed.",
  WORKFLOW_RESULTS_DESTROYED: "Workflow results destroyed.",
  WORKFLOW_RESULTS_MOUNTED: "Workflow results mounted.",
  WORKFLOW_RESULTS_UPDATED: "Workflow results refreshed."
};
const ERROR_MESSAGES = {
  RUN_GENERIC: "Workflow execution failed.",
  UPLOAD_GENERIC: "Upload failed.",
  UPLOAD_INVALID_RESPONSE: "Invalid response shape from upload API.",
  UPLOAD_MISSING_FILE: "Missing file to upload."
};
const NOTIFICATION_MESSAGES = {
  NO_WORKFLOWS_AVAILABLE: "No workflows available from the API.",
  NO_WORKFLOW_SELECTED: "No workflow selected.",
  WORKFLOWS_LOAD_FAILED: "Failed to load workflows."
};
const STATUS_MESSAGES = {
  ERROR_FETCHING_WORKFLOWS: "Error fetching workflows!",
  ERROR_RUNNING_WORKFLOW: "Error running workflow!",
  ERROR_UPLOADING_FILE: "Error uploading file!",
  IDLE_WORKFLOWS_LOADED: "Workflows loaded",
  RUNNING_DISPATCHING_WORKFLOW: "Dispatching workflow...",
  RUNNING_INITIALIZING: "Initializing...",
  RUNNING_LOADING_WORKFLOWS: "Loading workflows...",
  RUNNING_SUBMITTING_WORKFLOW: "Submitting workflow...",
  RUNNING_UPLOADING_FILE: "Uploading file..."
};
const UI_CONSTANTS = {
  MASONRY_STYLE: ".masonry .grid { overflow-x: unset; overflow-y: unset; }",
  DOWNLOAD_CLEANUP_DELAY_MS: 1e3
};
const _formatContext = (context) => {
  if (context === void 0 || context === null) {
    return null;
  }
  if (typeof context === "string") {
    return context;
  }
  try {
    const serialized = JSON.stringify(context);
    return serialized ? serialized : null;
  } catch {
    return String(context);
  }
};
const _getLogLevel = (category) => {
  let level;
  switch (category) {
    case "error":
      level = "error";
      break;
    default:
      level = "informational";
  }
  return level;
};
const debugLog = (message, category = "idle", context) => {
  try {
    const { debug } = getLfFramework();
    const { logs } = debug;
    const formattedContext = _formatContext(context);
    const payload = formattedContext ? `${message}

${formattedContext}` : message;
    logs.new(debug, payload, _getLogLevel(category));
  } catch {
  }
};
const { theme: theme$9 } = getLfFramework();
const ROOT_CLASS$9 = "action-button-section";
const ACTION_BUTTON_CLASSES = {
  _: theme$9.bemClass(ROOT_CLASS$9)
};
const createActionButtonSection = (store) => {
  const { ACTION_BUTTON_DESTROYED, ACTION_BUTTON_MOUNTED, ACTION_BUTTON_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in ACTION_BUTTON_CLASSES) {
      const element = ACTION_BUTTON_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(ACTION_BUTTON_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[ACTION_BUTTON_CLASSES._]) {
      return;
    }
    const _root = document.createElement("lf-button");
    _root.className = theme$9.bemClass(ACTION_BUTTON_CLASSES._);
    _root.lfIcon = "send";
    _root.lfStyling = "floating";
    _root.title = "Run current workflow";
    _root.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(ACTION_BUTTON_CLASSES._, _root);
    debugLog(ACTION_BUTTON_MOUNTED);
  };
  const render = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const _root = elements[ACTION_BUTTON_CLASSES._];
    if (!_root) {
      return;
    }
    debugLog(ACTION_BUTTON_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const treeHandler = (e, store) => {
  const { comp, eventType, node } = e.detail;
  const state = store.getState();
  const { manager } = state;
  const elements = manager.uiRegistry.get();
  const drawer = elements[DRAWER_CLASSES._];
  switch (eventType) {
    case "click":
      switch (comp.rootElement.className) {
        case DRAWER_CLASSES.tree:
          if (!manager) {
            return;
          }
          const isLeaf = !node.children || node.children.length === 0;
          const isHome = node.id === "home";
          if (isHome) {
            state.mutate.view("home");
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
const { theme: theme$8 } = getLfFramework();
const ROOT_CLASS$8 = "drawer-section";
const DRAWER_CLASSES = {
  _: theme$8.bemClass(ROOT_CLASS$8),
  buttonComfyUi: theme$8.bemClass(ROOT_CLASS$8, "button-comfyui"),
  buttonDebug: theme$8.bemClass(ROOT_CLASS$8, "button-debug"),
  buttonGithub: theme$8.bemClass(ROOT_CLASS$8, "button-github"),
  container: theme$8.bemClass(ROOT_CLASS$8, "container"),
  footer: theme$8.bemClass(ROOT_CLASS$8, "footer"),
  tree: theme$8.bemClass(ROOT_CLASS$8, "tree")
};
const _createDataset$2 = (workflows) => {
  var _a;
  const { article, listTree } = getLfFramework().theme.get.icons();
  const categories = [];
  const home = { icon: article, id: "home", value: "Home" };
  const wfs = { icon: listTree, id: "workflows", value: "Workflows", children: categories };
  const clone = JSON.parse(JSON.stringify(workflows));
  (_a = clone.nodes) == null ? void 0 : _a.forEach((node) => {
    node.children = void 0;
    const name = (node == null ? void 0 : node.category) || "Uncategorized";
    let category = categories.find((cat) => cat.value === name);
    if (!category) {
      category = { icon: _getIcon(name), id: name, value: name, children: [] };
      categories.push(category);
    }
    category.children.push(node);
  });
  const dataset = {
    nodes: [home, wfs]
  };
  categories.sort((a, b) => String(a.value).localeCompare(String(b.value)));
  return dataset;
};
const _getIcon = (category) => {
  const { alertTriangle, codeCircle2, photo, json, robot, wand } = getLfFramework().theme.get.icons();
  const category_icons = {
    "Image Processing": wand,
    JSON: json,
    LLM: robot,
    SVG: codeCircle2,
    "Text to Image": photo
  };
  return category_icons[category] || alertTriangle;
};
const _button = (store, icon, label, className) => {
  const button = document.createElement("lf-button");
  button.className = className;
  button.lfAriaLabel = label;
  button.lfIcon = icon;
  button.lfStyling = "icon";
  button.lfUiSize = "small";
  button.title = label;
  button.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  return button;
};
const _container$1 = (store) => {
  const container = document.createElement("div");
  container.className = DRAWER_CLASSES.container;
  container.slot = "content";
  const { comfyUi, debug, footer, github } = _footer(store);
  const tree = _tree(store);
  container.appendChild(tree);
  container.appendChild(footer);
  return { comfyUi, container, debug, footer, github, tree };
};
const _footer = (store) => {
  const footer = document.createElement("div");
  footer.className = DRAWER_CLASSES.footer;
  let icon = getLfFramework().theme.get.icon("imageInPicture");
  let label = "Open ComfyUI";
  const comfyUi = _button(store, icon, label, DRAWER_CLASSES.buttonComfyUi);
  icon = getLfFramework().theme.get.icon("bug");
  label = "Toggle developer console";
  const debug = _button(store, icon, label, DRAWER_CLASSES.buttonDebug);
  icon = getLfFramework().theme.get.icon("brandGithub");
  label = "Open GitHub repository";
  const github = _button(store, icon, label, DRAWER_CLASSES.buttonGithub);
  footer.appendChild(github);
  footer.appendChild(comfyUi);
  footer.appendChild(debug);
  return { comfyUi, debug, footer, github };
};
const _tree = (store) => {
  const tree = document.createElement("lf-tree");
  tree.className = DRAWER_CLASSES.tree;
  tree.lfAccordionLayout = true;
  tree.addEventListener("lf-tree-event", (e) => treeHandler(e, store));
  return tree;
};
const createDrawerSection = (store) => {
  const { DRAWER_DESTROYED, DRAWER_MOUNTED, DRAWER_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in DRAWER_CLASSES) {
      const element = DRAWER_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(DRAWER_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[DRAWER_CLASSES._]) {
      return;
    }
    const _root = document.createElement("lf-drawer");
    _root.className = ROOT_CLASS$8;
    _root.lfDisplay = "slide";
    const { comfyUi, debug, footer, github, container, tree } = _container$1(store);
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
  const render = () => {
    const state = store.getState();
    const { isDebug, manager, workflows } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const debug = elements[DRAWER_CLASSES.buttonDebug];
    const tree = elements[DRAWER_CLASSES.tree];
    debug.lfUiState = isDebug ? "warning" : "primary";
    debug.title = isDebug ? "Hide developer console" : "Show developer console";
    tree.lfDataset = _createDataset$2(workflows);
    debugLog(DRAWER_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const _setProps = (comp, element, props, slotMap = {}) => {
  if (!props) {
    return;
  }
  const { sanitizeProps } = getLfFramework();
  const hasSlots = Object.keys(slotMap).length > 0;
  if (hasSlots) {
    _setSlots(comp, element, slotMap);
  }
  const el = element;
  const safeProps = sanitizeProps(props, comp);
  for (const key in safeProps) {
    if (Object.hasOwn(safeProps, key)) {
      const prop = safeProps[key];
      el[key] = prop;
    }
  }
};
const _setSlots = (_comp, element, slotMap) => {
  for (const slotName in slotMap) {
    const slotHtml = slotMap[slotName];
    const wrapper = document.createElement("div");
    wrapper.innerHTML = slotHtml;
    wrapper.setAttribute("slot", slotName);
    wrapper.style.fill = "rgba(var(--lf-color-secondary, 1))";
    wrapper.style.stroke = "rgba(var(--lf-color-primary, 1))";
    element.appendChild(wrapper);
    if (slotName.toLowerCase().endsWith(".svg")) {
      const dlButton = createComponent.button({
        lfAriaLabel: "Download SVG",
        lfIcon: "download",
        lfLabel: "Download SVG",
        lfStretchX: true,
        lfUiState: "success"
      });
      dlButton.onclick = () => {
        const blob = new Blob([slotHtml], { type: "image/svg+xml" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = slotName.toLowerCase().endsWith(".svg") ? slotName : `${slotName}.svg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      };
      dlButton.style.position = "absolute";
      dlButton.style.bottom = "0";
      wrapper.style.display = "grid";
      wrapper.style.gridTemplateRows = "1fr auto";
      wrapper.style.margin = "0 auto";
      wrapper.style.maxWidth = "360px";
      wrapper.style.position = "relative";
      wrapper.appendChild(dlButton);
    }
  }
};
const createComponent = {
  button: (props) => {
    const comp = document.createElement("lf-button");
    _setProps("LfButton", comp, props);
    return comp;
  },
  chat: (props) => {
    const comp = document.createElement("lf-chat");
    if (CHAT_ENDPOINT) {
      comp.lfEndpointUrl = CHAT_ENDPOINT;
    }
    _setProps("LfChat", comp, props);
    return comp;
  },
  code: (props) => {
    const comp = document.createElement("lf-code");
    _setProps("LfCode", comp, props);
    return comp;
  },
  masonry: (props, slot_map) => {
    const comp = document.createElement("lf-masonry");
    _setProps("LfMasonry", comp, props, slot_map);
    return comp;
  },
  textfield: (props) => {
    const comp = document.createElement("lf-textfield");
    _setProps("LfTextfield", comp, props);
    return comp;
  },
  toggle: (props) => {
    const comp = document.createElement("lf-toggle");
    _setProps("LfToggle", comp, props);
    return comp;
  },
  upload: (props) => {
    const comp = document.createElement("lf-upload");
    _setProps("LfUpload", comp, props);
    return comp;
  }
};
const createInputCell = (cell) => {
  const { sanitizeProps } = getLfFramework();
  const { props, shape } = cell;
  switch (shape) {
    case "chat": {
      const p = props || {};
      return createComponent.chat(sanitizeProps(p, "LfChat"));
    }
    case "toggle": {
      const p = props || {};
      return createComponent.toggle(sanitizeProps(p, "LfToggle"));
    }
    case "upload": {
      const p = props || {};
      return createComponent.upload(sanitizeProps(p, "LfUpload"));
    }
    default:
    case "textfield": {
      const p = props || {};
      return createComponent.textfield(sanitizeProps(p, "LfTextfield"));
    }
  }
};
const createOutputComponent = (descriptor) => {
  const { syntax } = getLfFramework();
  const { civitai_metadata, dataset, file_names, json, metadata, props, shape, slot_map, string, svg } = descriptor;
  const el = document.createElement("div");
  switch (shape) {
    case "code": {
      const p = props || {};
      p.lfValue = string || svg || civitai_metadata || (file_names == null ? void 0 : file_names.join("\n")) || syntax.json.unescape(json || metadata || dataset || { message: "No output available." }).unescapedString;
      const code = createComponent.code(p);
      el.appendChild(code);
      break;
    }
    case "masonry": {
      const p = props || {};
      p.lfDataset = dataset;
      const masonry = createComponent.masonry(p, slot_map);
      el.appendChild(masonry);
      break;
    }
    default: {
      const fallback = document.createElement("pre");
      fallback.textContent = "No output available.";
      el.appendChild(fallback);
      break;
    }
  }
  return el;
};
const { theme: theme$7 } = getLfFramework();
const ROOT_CLASS$7 = "header-section";
const HEADER_CLASSES = {
  _: theme$7.bemClass(ROOT_CLASS$7),
  appMessage: theme$7.bemClass(ROOT_CLASS$7, "app-message"),
  container: theme$7.bemClass(ROOT_CLASS$7, "container"),
  drawerToggle: theme$7.bemClass(ROOT_CLASS$7, "drawer-toggle"),
  serverIndicator: theme$7.bemClass(ROOT_CLASS$7, "server-indicator"),
  serverIndicatorCounter: theme$7.bemClass(ROOT_CLASS$7, "server-indicator-counter"),
  serverIndicatorLight: theme$7.bemClass(ROOT_CLASS$7, "server-indicator-light")
};
const _appMessage = () => {
  const appMessage = document.createElement("div");
  appMessage.className = HEADER_CLASSES.appMessage;
  appMessage.ariaAtomic = "true";
  appMessage.ariaLive = "polite";
  return appMessage;
};
const _container = () => {
  const container = document.createElement("div");
  container.className = HEADER_CLASSES.container;
  container.slot = "content";
  return container;
};
const _drawerToggle = (store) => {
  const lfIcon = theme$7.get.icon("menu2");
  const props = {
    lfAriaLabel: "Toggle drawer",
    lfIcon,
    lfStyling: "icon"
  };
  const drawerToggle = createComponent.button(props);
  drawerToggle.className = HEADER_CLASSES.drawerToggle;
  drawerToggle.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  return drawerToggle;
};
const _serverIndicator = (store) => {
  const serverIndicator = document.createElement("div");
  serverIndicator.className = HEADER_CLASSES.serverIndicator;
  const light = document.createElement("lf-button");
  light.className = HEADER_CLASSES.serverIndicatorLight;
  light.lfUiSize = "large";
  light.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  const counter = document.createElement("span");
  counter.className = HEADER_CLASSES.serverIndicatorCounter;
  serverIndicator.appendChild(counter);
  serverIndicator.appendChild(light);
  return { counter, light, serverIndicator };
};
const createHeaderSection = (store) => {
  const { HEADER_DESTROYED, HEADER_MOUNTED, HEADER_UPDATED } = DEBUG_MESSAGES;
  const HIDE_KEY = "__lf_hide_timer__";
  const HIDE_DELAY = 900;
  const FADE_CLEAR_DELAY = 380;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in HEADER_CLASSES) {
      const element = HEADER_CLASSES[cls];
      uiRegistry.remove(element);
    }
    const elements = uiRegistry.get();
    if (elements && elements[HEADER_CLASSES.appMessage]) {
      const appMessage = elements[HEADER_CLASSES.appMessage];
      const timer = appMessage[HIDE_KEY];
      if (timer) {
        clearTimeout(timer);
        appMessage[HIDE_KEY] = void 0;
      }
    }
    debugLog(HEADER_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[HEADER_CLASSES._]) {
      return;
    }
    const _root = document.createElement("lf-header");
    _root.className = HEADER_CLASSES._;
    const appMessage = _appMessage();
    const container = _container();
    const drawerToggle = _drawerToggle(store);
    const { counter, light, serverIndicator } = _serverIndicator(store);
    _root.appendChild(container);
    container.appendChild(drawerToggle);
    container.appendChild(appMessage);
    container.appendChild(serverIndicator);
    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(HEADER_CLASSES._, _root);
    uiRegistry.set(HEADER_CLASSES.appMessage, appMessage);
    uiRegistry.set(HEADER_CLASSES.container, container);
    uiRegistry.set(HEADER_CLASSES.drawerToggle, drawerToggle);
    uiRegistry.set(HEADER_CLASSES.serverIndicator, serverIndicator);
    uiRegistry.set(HEADER_CLASSES.serverIndicatorCounter, counter);
    uiRegistry.set(HEADER_CLASSES.serverIndicatorLight, light);
    debugLog(HEADER_MOUNTED);
  };
  const render = () => {
    const { alertTriangle, check, hourglassLow } = theme$7.get.icons();
    const { current, manager, queuedJobs, currentRunId } = store.getState();
    const { message, status } = current;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const appMessage = elements[HEADER_CLASSES.appMessage];
    const counter = elements[HEADER_CLASSES.serverIndicatorCounter];
    const light = elements[HEADER_CLASSES.serverIndicatorLight];
    if (!appMessage || !counter || !light) {
      return;
    }
    const isIdle = status === "idle";
    if (isIdle) {
      appMessage.dataset.status = current.status || "";
      appMessage.dataset.visible = "true";
      if (typeof message === "string" && message.length > 0) {
        appMessage.innerText = message;
      }
      const prev = appMessage[HIDE_KEY];
      if (prev) {
        clearTimeout(prev);
      }
      appMessage[HIDE_KEY] = setTimeout(() => {
        appMessage.dataset.visible = "false";
        const clearTimer = setTimeout(() => {
          appMessage.innerText = "";
          appMessage[HIDE_KEY] = void 0;
        }, FADE_CLEAR_DELAY);
        appMessage[HIDE_KEY] = clearTimer;
      }, HIDE_DELAY);
    } else {
      const prev = appMessage[HIDE_KEY];
      if (prev) {
        clearTimeout(prev);
        appMessage[HIDE_KEY] = void 0;
      }
      let displayMessage = message || "";
      if (currentRunId) {
        const parts = currentRunId.split("-");
        const prefix = parts[0] || currentRunId.slice(0, 8);
        displayMessage = `Processing ${prefix}`;
      }
      appMessage.innerText = displayMessage;
      appMessage.dataset.status = status || "";
      appMessage.dataset.visible = "true";
    }
    if (queuedJobs < 0) {
      counter.innerText = "";
      light.lfIcon = alertTriangle;
      light.lfUiState = "danger";
      light.title = "Server disconnected";
    } else if (queuedJobs === 0) {
      counter.innerText = "";
      light.lfIcon = check;
      light.lfUiState = "success";
      light.title = "Server idle";
    } else {
      counter.innerText = queuedJobs.toString();
      light.lfIcon = hourglassLow;
      light.lfUiState = "warning";
      light.title = `Jobs in queue: ${queuedJobs}`;
    }
    debugLog(HEADER_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const DEFAULT_VIEW = "workflow";
const SECTION_PRESETS = {
  home: ["home"],
  history: ["outputs"],
  run: ["results"],
  workflow: ["inputs", "outputs"]
};
const cloneSections = (sections) => sections.slice();
const selectRunWithDefaults = (store, runId, clearResults2) => {
  if (clearResults2 === void 0) {
    selectRun(store, runId);
  } else {
    selectRun(store, runId, { clearResults: clearResults2 });
  }
};
const resolveRunSections = (state) => {
  const { runs, selectedRunId } = state;
  if (selectedRunId && runs.some((run) => run.runId === selectedRunId)) {
    return cloneSections(SECTION_PRESETS.run);
  }
  return [];
};
const buildWorkflowRoute = (state) => {
  const workflowId = state.current.id ?? void 0;
  return workflowId ? { view: "workflow", workflowId } : { view: "workflow" };
};
const VIEW_DEFINITIONS = {
  //#region Home
  home: {
    sections: () => cloneSections(SECTION_PRESETS.home),
    toRoute: () => ({ view: "home" }),
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return "home";
    }
  },
  //#endregion
  //#region History
  history: {
    sections: () => cloneSections(SECTION_PRESETS.history),
    toRoute: (state) => {
      const workflowId = state.current.id ?? void 0;
      return workflowId ? { view: "history", workflowId } : { view: "history" };
    },
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return "history";
    }
  },
  //#endregion
  //#region Run
  run: {
    sections: resolveRunSections,
    toRoute: (state) => {
      const workflowId = state.current.id ?? void 0;
      const runId = state.selectedRunId ?? void 0;
      if (runId) {
        return { view: "run", runId, workflowId };
      }
      return VIEW_DEFINITIONS.workflow.toRoute(state);
    },
    enter: (store, options) => {
      const requestedRunId = options.runId ?? null;
      const state = store.getState();
      const runId = requestedRunId ?? state.selectedRunId ?? null;
      const hasRun = Boolean(runId && state.runs.some((run) => run.runId === runId));
      if (!hasRun) {
        selectRunWithDefaults(store, null, options.clearResults);
        return "workflow";
      }
      selectRunWithDefaults(store, runId, options.clearResults);
      return "run";
    }
  },
  //#endregion
  //#region Workflow
  workflow: {
    sections: () => cloneSections(SECTION_PRESETS.workflow),
    toRoute: buildWorkflowRoute,
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return "workflow";
    }
  }
  //#endregion
};
const getViewDefinition = (view) => VIEW_DEFINITIONS[view] ?? VIEW_DEFINITIONS[DEFAULT_VIEW];
const changeView = (store, view, options = {}) => {
  const definition = getViewDefinition(view);
  const resolvedView = definition.enter(store, options);
  setView(store, resolvedView);
  return resolvedView;
};
const resolveMainSections = (state) => {
  const definition = getViewDefinition(state.view);
  return definition.sections(state);
};
const computeRouteFromState = (state) => {
  const definition = getViewDefinition(state.view);
  return definition.toRoute(state);
};
const _tryParseJson = (value) => {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
};
const deepMerge = (defs, outs) => {
  var _a, _b;
  const prep = [];
  for (const id in defs) {
    const cell = defs[id];
    const { nodeId } = cell;
    const result = ((_a = outs == null ? void 0 : outs[nodeId]) == null ? void 0 : _a.lf_output[0]) || ((_b = outs == null ? void 0 : outs[nodeId]) == null ? void 0 : _b[0]) || (outs == null ? void 0 : outs[nodeId]);
    const item = {
      ...JSON.parse(JSON.stringify(cell)),
      ...JSON.parse(JSON.stringify(result || {}))
    };
    prep.push(item);
  }
  return prep;
};
const isObject = (v) => v !== null && typeof v === "object";
const isString = (v) => typeof v === "string";
const isStringArray = (v) => Array.isArray(v) && v.every((e) => typeof e === "string");
const isWorkflowAPIUploadPayload = (v) => {
  if (!isObject(v)) {
    return false;
  }
  const hasPaths = "paths" in v && isStringArray(v.paths);
  const hasError = "error" in v && isObject(v.error) && "message" in v.error && isString(v.error.message);
  if (!hasPaths && !hasError) {
    return false;
  }
  if ("error" in v) {
    const err = v.error;
    if (!isObject(err) || !("message" in err) || !isString(err.message)) {
      return false;
    }
  }
  return true;
};
const isWorkflowAPIUploadResponse = (v) => {
  if (!isObject(v)) {
    return false;
  }
  if (!("message" in v) || !isString(v.message)) {
    return false;
  }
  if (!("status" in v) || !isString(v.status)) {
    return false;
  }
  if (!("payload" in v) || !isWorkflowAPIUploadPayload(v.payload)) {
    return false;
  }
  return true;
};
const normalizeTimestamp = (v, fallback) => {
  if (v === null || v === void 0) {
    return fallback;
  }
  const n = typeof v === "string" ? Number(v) : v;
  if (!Number.isFinite(n) || Number.isNaN(n)) {
    return fallback;
  }
  return n < 1e12 ? Math.floor(n * 1e3) : Math.floor(n);
};
const formatStatus = (status) => status.charAt(0).toUpperCase() + status.slice(1);
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "Unknown time";
  }
  return date.toLocaleString();
};
const recordToUI = (rec, wfs = {}) => {
  var _a, _b, _c;
  const { created_at, error, result, run_id, status, updated_at, workflow_id } = rec;
  const now = Date.now();
  const map = {
    runId: run_id,
    status,
    createdAt: normalizeTimestamp(created_at, now),
    updatedAt: normalizeTimestamp(updated_at, now),
    workflowId: workflow_id ?? null,
    workflowName: workflow_id && wfs[workflow_id] || "Unknown workflow",
    error: error ?? null,
    httpStatus: (result == null ? void 0 : result.http_status) ?? null,
    resultPayload: result ?? null,
    outputs: ((_c = (_b = (_a = result == null ? void 0 : result.body) == null ? void 0 : _a.payload) == null ? void 0 : _b.history) == null ? void 0 : _c.outputs) || null,
    inputs: {}
    // TODO: populate if available in rec
  };
  return map;
};
const stringifyDetail = (value) => {
  if (value === null || value === void 0) {
    return null;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) {
      return null;
    }
    const parsed = _tryParseJson(trimmed);
    if (parsed !== null) {
      try {
        return JSON.stringify(parsed, null, 2);
      } catch {
        return trimmed;
      }
    }
    return trimmed;
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
};
const summarizeDetail = (value) => {
  if (value === null || value === void 0) {
    return null;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) {
      return null;
    }
    const parsed = _tryParseJson(trimmed);
    if (parsed && typeof parsed === "object") {
      const message = parsed.message;
      if (typeof message === "string" && message.trim()) {
        return message.trim();
      }
      const detail = parsed.detail;
      if (typeof detail === "string" && detail.trim()) {
        return detail.trim();
      }
      return JSON.stringify(parsed);
    }
    return trimmed;
  }
  if (typeof value === "object") {
    const message = value.message;
    if (typeof message === "string" && message.trim()) {
      return message.trim();
    }
    const detail = value.detail;
    if (typeof detail === "string" && detail.trim()) {
      return detail.trim();
    }
    try {
      const str = JSON.stringify(value);
      return str.length > 200 ? `${str.slice(0, 197)}...` : str;
    } catch {
      return "[object Object]";
    }
  }
  return String(value);
};
const clearChildren = (element) => {
  if (!element) {
    return;
  }
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
};
const { theme: theme$6 } = getLfFramework();
const ROOT_CLASS$6 = "results-section";
const RESULTS_CLASSES = {
  _: theme$6.bemClass(ROOT_CLASS$6),
  actions: theme$6.bemClass(ROOT_CLASS$6, "actions"),
  back: theme$6.bemClass(ROOT_CLASS$6, "back"),
  description: theme$6.bemClass(ROOT_CLASS$6, "description"),
  empty: theme$6.bemClass(ROOT_CLASS$6, "empty"),
  grid: theme$6.bemClass(ROOT_CLASS$6, "grid"),
  h3: theme$6.bemClass(ROOT_CLASS$6, "title-h3"),
  history: theme$6.bemClass(ROOT_CLASS$6, "history"),
  item: theme$6.bemClass(ROOT_CLASS$6, "item"),
  results: theme$6.bemClass(ROOT_CLASS$6, "results"),
  subtitle: theme$6.bemClass(ROOT_CLASS$6, "subtitle"),
  title: theme$6.bemClass(ROOT_CLASS$6, "title")
};
const _formatDescription = (selectedRun, description) => {
  if (!selectedRun) {
    return description;
  }
  const timestamp = selectedRun.updatedAt || selectedRun.createdAt;
  return `Run ${selectedRun.runId.slice(0, 8)} - ${formatStatus(selectedRun.status)} - ${formatTimestamp(timestamp)}`;
};
const _description$2 = () => {
  const p = document.createElement("p");
  p.className = RESULTS_CLASSES.description;
  return p;
};
const _results = () => {
  const cellWrapper = document.createElement("div");
  cellWrapper.className = RESULTS_CLASSES.results;
  return cellWrapper;
};
const _title$3 = (store) => {
  const { arrowBack, folder } = theme$6.get.icons();
  const { manager } = store.getState();
  const title = document.createElement("div");
  title.className = RESULTS_CLASSES.title;
  const h3 = document.createElement("h3");
  h3.className = RESULTS_CLASSES.h3;
  const actions = document.createElement("div");
  actions.className = RESULTS_CLASSES.actions;
  const backButton = document.createElement("lf-button");
  backButton.className = RESULTS_CLASSES.back;
  backButton.lfIcon = arrowBack;
  backButton.lfLabel = "Back";
  backButton.lfStyling = "flat";
  backButton.lfUiSize = "small";
  backButton.lfUiState = "disabled";
  backButton.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  const historyButton = document.createElement("lf-button");
  historyButton.className = RESULTS_CLASSES.history;
  historyButton.lfIcon = folder;
  historyButton.lfLabel = "History";
  historyButton.lfStyling = "flat";
  historyButton.lfUiSize = "small";
  historyButton.lfUiState = manager.runs.all().length === 0 ? "disabled" : "primary";
  historyButton.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  title.appendChild(h3);
  title.appendChild(actions);
  actions.appendChild(backButton);
  actions.appendChild(historyButton);
  return { actions, backButton, h3, historyButton, title };
};
const createResultsSection = (store) => {
  const { WORKFLOW_RESULTS_DESTROYED, WORKFLOW_RESULTS_MOUNTED, WORKFLOW_RESULTS_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in RESULTS_CLASSES) {
      const element = RESULTS_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(WORKFLOW_RESULTS_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[RESULTS_CLASSES._]) {
      return;
    }
    const _root = document.createElement("section");
    _root.className = RESULTS_CLASSES._;
    const results = _results();
    const description = _description$2();
    const { actions, backButton, h3, historyButton, title } = _title$3(store);
    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(results);
    elements[MAIN_CLASSES._].prepend(_root);
    uiRegistry.set(RESULTS_CLASSES._, _root);
    uiRegistry.set(RESULTS_CLASSES.actions, actions);
    uiRegistry.set(RESULTS_CLASSES.back, backButton);
    uiRegistry.set(RESULTS_CLASSES.description, description);
    uiRegistry.set(RESULTS_CLASSES.h3, h3);
    uiRegistry.set(RESULTS_CLASSES.history, historyButton);
    uiRegistry.set(RESULTS_CLASSES.results, results);
    uiRegistry.set(RESULTS_CLASSES.title, title);
    debugLog(WORKFLOW_RESULTS_MOUNTED);
  };
  const render = () => {
    var _a;
    const { syntax } = getLfFramework();
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const selectedRun = manager.runs.selected();
    const runs = manager.runs.all();
    const descr = elements[RESULTS_CLASSES.description];
    const element = elements[RESULTS_CLASSES.results];
    const h3 = elements[RESULTS_CLASSES.h3];
    const backButton = elements[RESULTS_CLASSES.back];
    const historyButton = elements[RESULTS_CLASSES.history];
    descr.textContent = _formatDescription(selectedRun, manager.workflow.description());
    h3.textContent = (selectedRun == null ? void 0 : selectedRun.workflowName) || manager.workflow.title();
    backButton.lfUiState = selectedRun ? "primary" : "disabled";
    historyButton.lfUiState = runs.length > 0 ? "primary" : "disabled";
    const outputs = state.results ?? (selectedRun == null ? void 0 : selectedRun.outputs) ?? null;
    clearChildren(element);
    const nodeIds = outputs ? Object.keys(outputs) : [];
    if (nodeIds.length === 0) {
      const empty = document.createElement("p");
      empty.className = RESULTS_CLASSES.empty;
      const summary = summarizeDetail((selectedRun == null ? void 0 : selectedRun.error) ?? null);
      if (selectedRun) {
        empty.textContent = summary ? `This run has not produced any outputs yet. ${summary}` : "This run has not produced any outputs yet.";
      } else {
        empty.textContent = "Select a run to inspect its outputs.";
      }
      element.appendChild(empty);
      const appendCodeBlock = (label, content) => {
        if (!content) {
          return;
        }
        const wrapper = document.createElement("div");
        wrapper.className = RESULTS_CLASSES.item;
        const heading = document.createElement("h4");
        heading.className = RESULTS_CLASSES.subtitle;
        heading.textContent = label;
        const code = createComponent.code({
          lfLanguage: syntax.json.isLikeString(content) ? "json" : "markdown",
          lfStickyHeader: false,
          lfUiState: "danger",
          lfValue: content
        });
        wrapper.appendChild(heading);
        wrapper.appendChild(code);
        element.appendChild(wrapper);
      };
      appendCodeBlock("Error detail", stringifyDetail((selectedRun == null ? void 0 : selectedRun.error) ?? null));
      appendCodeBlock("Run payload", stringifyDetail(((_a = selectedRun == null ? void 0 : selectedRun.resultPayload) == null ? void 0 : _a.body) ?? (selectedRun == null ? void 0 : selectedRun.resultPayload) ?? null));
      return;
    }
    const workflow = manager.workflow.current();
    const outputsDefs = workflow ? manager.workflow.cells("output") : {};
    const prepOutputs = deepMerge(outputsDefs, outputs || {});
    for (let i = 0; i < prepOutputs.length; i++) {
      const output = prepOutputs[i];
      const { id, nodeId, title } = output;
      const h4 = document.createElement("h4");
      h4.className = RESULTS_CLASSES.subtitle;
      h4.textContent = title || `Node #${nodeId}`;
      element.appendChild(h4);
      const grid = document.createElement("div");
      grid.className = RESULTS_CLASSES.grid;
      element.appendChild(grid);
      const wrapper = document.createElement("div");
      wrapper.className = RESULTS_CLASSES.item;
      const component = createOutputComponent(output);
      component.id = id;
      wrapper.appendChild(component);
      grid.appendChild(wrapper);
    }
    debugLog(WORKFLOW_RESULTS_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const { theme: theme$5 } = getLfFramework();
const ROOT_CLASS$5 = "main-section";
const MAIN_CLASSES = {
  _: theme$5.bemClass(ROOT_CLASS$5),
  home: theme$5.bemClass(ROOT_CLASS$5, "home")
};
const createMainSection = (store) => {
  const { MAIN_DESTROYED, MAIN_MOUNTED, MAIN_UPDATED } = DEBUG_MESSAGES;
  const HOME = createHomeSection(store);
  const INPUTS = createInputsSection(store);
  const OUTPUTS = createOutputsSection(store);
  const RESULTS = createResultsSection(store);
  const SECTION_CONTROLLERS = {
    home: HOME,
    inputs: INPUTS,
    outputs: OUTPUTS,
    results: RESULTS
  };
  let LAST_SCOPE = [];
  let LAST_WORKFLOW_ID = store.getState().current.id;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    Object.values(MAIN_CLASSES).forEach((className) => uiRegistry.remove(className));
    Object.values(SECTION_CONTROLLERS).forEach((controller) => controller.destroy());
    debugLog(MAIN_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[MAIN_CLASSES._]) {
      return;
    }
    const _root = document.createElement("main");
    _root.className = ROOT_CLASS$5;
    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(MAIN_CLASSES._, _root);
    debugLog(MAIN_MOUNTED);
  };
  const render = (scope) => {
    const state = store.getState();
    const { manager, view } = state;
    const { uiRegistry } = manager;
    const workflowId = state.current.id ?? null;
    const workflowChanged = workflowId !== LAST_WORKFLOW_ID;
    const resolvedSections = scope ?? resolveMainSections(state);
    const scopeSet = new Set(resolvedSections);
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const root = elements[MAIN_CLASSES._];
    root.dataset.view = view;
    const previousSections = new Set(LAST_SCOPE);
    if (workflowChanged && previousSections.size > 0) {
      previousSections.forEach((section) => {
        SECTION_CONTROLLERS[section].destroy();
      });
      previousSections.clear();
      LAST_SCOPE = [];
    } else {
      LAST_SCOPE.forEach((section) => {
        if (!scopeSet.has(section)) {
          SECTION_CONTROLLERS[section].destroy();
          previousSections.delete(section);
        }
      });
    }
    scopeSet.forEach((section) => {
      const controller = SECTION_CONTROLLERS[section];
      if (!previousSections.has(section)) {
        controller.mount();
      }
      controller.render();
    });
    LAST_SCOPE = Array.from(scopeSet);
    LAST_WORKFLOW_ID = workflowId;
    debugLog(MAIN_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const { theme: theme$4 } = getLfFramework();
const ROOT_CLASS$4 = "home-section";
const HOME_CLASSES = {
  _: theme$4.bemClass(ROOT_CLASS$4),
  description: theme$4.bemClass(ROOT_CLASS$4, "description"),
  h1: theme$4.bemClass(ROOT_CLASS$4, "title-h1"),
  masonry: theme$4.bemClass(ROOT_CLASS$4, "masonry"),
  title: theme$4.bemClass(ROOT_CLASS$4, "title")
};
const _createDataset$1 = (store) => {
  var _a;
  const { workflows } = store.getState();
  const clone = JSON.parse(JSON.stringify(workflows));
  const root = { cells: {}, id: "root", value: "Workflows" };
  (_a = clone.nodes) == null ? void 0 : _a.forEach((node) => {
    const id = node.id;
    root.cells[id] = {
      lfDataset: {
        nodes: [
          {
            cells: {
              "1": {
                value: String(node.value)
              },
              "2": {
                value: node.category
              },
              "3": {
                value: node.description
              }
            },
            id
          }
        ]
      },
      shape: "card",
      value: ""
    };
  });
  const dataset = {
    nodes: [root]
  };
  return dataset;
};
const _masonry$1 = (store) => {
  const masonry = document.createElement("lf-masonry");
  masonry.className = HOME_CLASSES.masonry;
  masonry.lfShape = "card";
  masonry.lfStyle = UI_CONSTANTS.MASONRY_STYLE;
  masonry.addEventListener("lf-masonry-event", (e) => masonryHandler(e, store));
  return masonry;
};
const _description$1 = () => {
  const p = document.createElement("p");
  p.className = HOME_CLASSES.description;
  p.textContent = "Below a list of the available workflows.";
  return p;
};
const _title$2 = () => {
  const title = document.createElement("div");
  const h1 = document.createElement("h1");
  title.className = HOME_CLASSES.title;
  h1.className = HOME_CLASSES.h1;
  h1.textContent = "Workflow Runner";
  title.appendChild(h1);
  return { h1, title };
};
const createHomeSection = (store) => {
  const { HOME_DESTROYED, HOME_MOUNTED, HOME_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in HOME_CLASSES) {
      const element = HOME_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(HOME_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[HOME_CLASSES._]) {
      return;
    }
    const _root = document.createElement("section");
    _root.className = HOME_CLASSES._;
    const description = _description$1();
    const masonry = _masonry$1(store);
    const { h1, title } = _title$2();
    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(masonry);
    elements[MAIN_CLASSES._].prepend(_root);
    uiRegistry.set(HOME_CLASSES._, _root);
    uiRegistry.set(HOME_CLASSES.description, description);
    uiRegistry.set(HOME_CLASSES.h1, h1);
    uiRegistry.set(HOME_CLASSES.masonry, masonry);
    uiRegistry.set(HOME_CLASSES.title, title);
    debugLog(HOME_MOUNTED);
  };
  const render = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const masonry = elements[HOME_CLASSES.masonry];
    masonry.lfDataset = _createDataset$1(store);
    debugLog(HOME_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const masonryHandler = (e, store) => {
  var _a, _b, _c, _d, _e, _f;
  const { comp, originalEvent } = e.detail;
  const ogEvent = originalEvent;
  const { manager, mutate } = store.getState();
  if (comp.rootElement.className === OUTPUTS_CLASSES.masonry) {
    switch ((_a = ogEvent == null ? void 0 : ogEvent.detail) == null ? void 0 : _a.eventType) {
      case "click":
        const card = ogEvent.detail.comp;
        const node = (_c = (_b = card.lfDataset) == null ? void 0 : _b.nodes) == null ? void 0 : _c[0];
        const isValidCard = (node == null ? void 0 : node.id) && card.rootElement.tagName.toLowerCase() === "lf-card";
        if (isValidCard) {
          const { id } = node;
          manager.runs.select(id, "run");
          const selected = manager.runs.get(id);
          const selectedOutputs = JSON.parse(JSON.stringify(selected.outputs)) || null;
          store.getState().mutate.results(selectedOutputs);
        }
        break;
      default:
        return;
    }
  }
  if (comp.rootElement.className === HOME_CLASSES.masonry) {
    switch ((_d = ogEvent == null ? void 0 : ogEvent.detail) == null ? void 0 : _d.eventType) {
      case "click":
        const card = ogEvent.detail.comp;
        const node = (_f = (_e = card.lfDataset) == null ? void 0 : _e.nodes) == null ? void 0 : _f[0];
        const isValidCard = (node == null ? void 0 : node.id) && card.rootElement.tagName.toLowerCase() === "lf-card";
        if (isValidCard) {
          const { id } = node;
          mutate.workflow(id);
          setView(store, "workflow");
        }
        break;
      default:
        return;
    }
  }
};
const { theme: theme$3 } = getLfFramework();
const ROOT_CLASS$3 = "outputs-section";
const OUTPUTS_CLASSES = {
  _: theme$3.bemClass(ROOT_CLASS$3),
  empty: theme$3.bemClass(ROOT_CLASS$3, "empty"),
  h4: theme$3.bemClass(ROOT_CLASS$3, "title-h4"),
  controls: theme$3.bemClass(ROOT_CLASS$3, "controls"),
  item: theme$3.bemClass(ROOT_CLASS$3, "item"),
  itemHeader: theme$3.bemClass(ROOT_CLASS$3, "item-header"),
  itemMeta: theme$3.bemClass(ROOT_CLASS$3, "item-meta"),
  itemTitle: theme$3.bemClass(ROOT_CLASS$3, "item-title"),
  masonry: theme$3.bemClass(ROOT_CLASS$3, "masonry"),
  status: theme$3.bemClass(ROOT_CLASS$3, "status"),
  timestamp: theme$3.bemClass(ROOT_CLASS$3, "timestamp"),
  title: theme$3.bemClass(ROOT_CLASS$3, "title"),
  toggle: theme$3.bemClass(ROOT_CLASS$3, "toggle")
};
const _emptyCardCell = () => {
  const lfCard = {
    lfDataset: {
      nodes: [
        {
          cells: {
            "1": {
              value: "Empty"
            },
            "2": {
              value: "No outputs to display"
            },
            "3": {
              value: "Run a workflow to start building your history."
            }
          },
          description: "No outputs to display for this workflow.",
          id: "empty-card"
        }
      ]
    },
    lfStyle: ".lf-card.material-layout__text-section { height: 100%; }",
    shape: "card",
    value: ""
  };
  return lfCard;
};
const _extractImageFromDataset = (dataset) => {
  if (!(dataset == null ? void 0 : dataset.nodes)) {
    return null;
  }
  for (const node of dataset.nodes) {
    const cells = node.cells ?? {};
    for (const key in cells) {
      const cell = cells[key];
      if (!cell || typeof cell !== "object") {
        continue;
      }
      const shape = cell.shape;
      const value = cell.value ?? cell.lfValue;
      if (shape === "image" && typeof value === "string" && value) {
        return value;
      }
    }
  }
  return null;
};
const _getFirstOutputImageUrl = (outputs) => {
  if (!outputs) {
    return "";
  }
  const tryPayload = (payload) => {
    if (!payload || typeof payload !== "object") {
      return { image: null, fallback: null };
    }
    const { code: codeIcon, forms: stringIcon, json: jsonIcon, photoX: fallback } = theme$3.get.icons();
    let foundImage = null;
    let fallbackCandidate = null;
    if (Array.isArray(payload.lf_output)) {
      for (const entry of payload.lf_output) {
        const { dataset: dataset2, file_names, json, metadata, string, svg } = entry;
        const image2 = _extractImageFromDataset(dataset2) ?? (file_names == null ? void 0 : file_names.find((name) => typeof name === "string" && name)) ?? null;
        if (image2) {
          foundImage = image2;
          break;
        }
        if (!fallbackCandidate) {
          if (typeof svg === "string" && svg) {
            fallbackCandidate = codeIcon;
          } else if (typeof string === "string" && string) {
            fallbackCandidate = stringIcon;
          } else if (json || metadata) {
            fallbackCandidate = jsonIcon;
          }
        }
      }
    }
    if (foundImage) {
      return { image: foundImage, fallback: null };
    }
    const dataset = payload.dataset;
    const fromDataset = _extractImageFromDataset(dataset);
    if (fromDataset) {
      return { image: fromDataset, fallback: null };
    }
    const fileNames = payload.file_names;
    if (Array.isArray(fileNames)) {
      const fileName = fileNames.find((name) => typeof name === "string" && name);
      if (fileName) {
        return { image: fileName, fallback: null };
      }
    }
    const image = payload.image;
    if (typeof image === "string" && image) {
      return { image, fallback: null };
    }
    return { image: null, fallback: fallbackCandidate ?? fallback };
  };
  let fallbackImage = null;
  for (const nodeId in outputs) {
    if (!Object.prototype.hasOwnProperty.call(outputs, nodeId)) {
      continue;
    }
    const payload = outputs[nodeId];
    const { image, fallback: candidate } = tryPayload(payload);
    if (image) {
      return image;
    }
    if (!fallbackImage && candidate) {
      fallbackImage = candidate;
    }
  }
  return fallbackImage ?? "";
};
const _getLfIcon = (status) => {
  const { alertTriangle, check, wand, hourglassLow, x } = theme$3.get.icons();
  switch (status) {
    case "cancelled":
      return x;
    case "failed":
      return alertTriangle;
    case "pending":
      return hourglassLow;
    case "running":
      return wand;
    case "succeeded":
      return check;
  }
};
const _getUiState = (status) => {
  switch (status) {
    case "cancelled":
      return "disabled";
    case "failed":
      return "danger";
    case "pending":
      return "primary";
    case "running":
      return "info";
    case "succeeded":
      return "success";
  }
};
const _itemCardCell = (run) => {
  const { createdAt, error, httpStatus, runId, status, updatedAt, workflowName } = run;
  const errorSummary = summarizeDetail(error);
  const detailLines = [
    `Created at: ${formatTimestamp(createdAt)}`,
    `Last updated: ${formatTimestamp(updatedAt)}`
  ];
  if (errorSummary) {
    detailLines.push("", `Error: ${errorSummary}`);
  }
  if (httpStatus !== null && httpStatus !== void 0) {
    detailLines.push(`HTTP Status: ${httpStatus}`);
  }
  const cells = {
    "1": {
      value: workflowName || "Workflow run"
    },
    "2": {
      value: `Run ID: ${runId}`
    },
    "3": {
      value: detailLines.join("\n").trim()
    },
    lfButton: {
      shape: "button",
      value: "",
      lfIcon: _getLfIcon(status),
      lfLabel: formatStatus(status),
      lfStyling: "flat",
      lfUiState: _getUiState(status)
    },
    lfImage: {
      shape: "image",
      value: _getFirstOutputImageUrl(run.outputs)
    }
  };
  const lfCard = {
    lfDataset: {
      nodes: [
        {
          cells,
          description: `Output results for run ${runId}`,
          id: `${runId}`
        }
      ]
    },
    lfStyle: ".lf-card.material-layout__text-section { height: 100%; }",
    lfUiState: _getUiState(status),
    shape: "card",
    value: ""
  };
  return lfCard;
};
const _masonry = (store) => {
  const masonry = document.createElement("lf-masonry");
  masonry.className = OUTPUTS_CLASSES.masonry;
  masonry.lfShape = "card";
  masonry.lfStyle = UI_CONSTANTS.MASONRY_STYLE;
  masonry.addEventListener("lf-masonry-event", (e) => masonryHandler(e, store));
  return masonry;
};
const _title$1 = (store) => {
  const title = document.createElement("div");
  title.className = OUTPUTS_CLASSES.title;
  const h4 = document.createElement("h4");
  h4.className = OUTPUTS_CLASSES.h4;
  const controls = document.createElement("div");
  controls.className = OUTPUTS_CLASSES.controls;
  const toggle = document.createElement("lf-button");
  toggle.className = OUTPUTS_CLASSES.toggle;
  toggle.lfStyling = "flat";
  toggle.lfUiSize = "small";
  toggle.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  title.appendChild(h4);
  title.appendChild(controls);
  controls.appendChild(toggle);
  return { h4, title, controls, toggle };
};
const createOutputsSection = (store) => {
  const { WORKFLOW_OUTPUTS_DESTROYED, WORKFLOW_OUTPUTS_MOUNTED, WORKFLOW_OUTPUTS_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in OUTPUTS_CLASSES) {
      const element = OUTPUTS_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(WORKFLOW_OUTPUTS_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[OUTPUTS_CLASSES._]) {
      return;
    }
    const _root = document.createElement("section");
    _root.className = OUTPUTS_CLASSES._;
    const { controls, h4, title, toggle } = _title$1(store);
    const masonry = _masonry(store);
    _root.appendChild(title);
    _root.appendChild(masonry);
    elements[MAIN_CLASSES._].appendChild(_root);
    uiRegistry.set(OUTPUTS_CLASSES._, _root);
    uiRegistry.set(OUTPUTS_CLASSES.controls, controls);
    uiRegistry.set(OUTPUTS_CLASSES.h4, h4);
    uiRegistry.set(OUTPUTS_CLASSES.masonry, masonry);
    uiRegistry.set(OUTPUTS_CLASSES.title, title);
    uiRegistry.set(OUTPUTS_CLASSES.toggle, toggle);
    debugLog(WORKFLOW_OUTPUTS_MOUNTED);
  };
  const render = () => {
    const { arrowBack, folder } = theme$3.get.icons();
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const h4 = elements[OUTPUTS_CLASSES.h4];
    const masonry = elements[OUTPUTS_CLASSES.masonry];
    const toggle = elements[OUTPUTS_CLASSES.toggle];
    if (!h4 || !masonry || !toggle) {
      return;
    }
    const activeWorkflowId = state.current.id;
    const allRuns = manager.runs.all();
    const hasAnyRuns = allRuns.length > 0;
    const isHistoryView = state.view === "history";
    const workflowTitle = manager.workflow.title();
    h4.textContent = workflowTitle ? `${workflowTitle} outputs` : "Workflow outputs";
    const runs = isHistoryView ? allRuns : allRuns.filter((run) => (run.workflowId ?? null) === (activeWorkflowId ?? null));
    toggle.lfIcon = isHistoryView ? arrowBack : folder;
    toggle.lfLabel = isHistoryView ? "Back" : "History";
    toggle.lfUiState = hasAnyRuns || isHistoryView ? "primary" : "disabled";
    const dataset = { nodes: [] };
    if (!runs.length) {
      dataset.nodes.push({ cells: { lfCard: _emptyCardCell() }, id: "" });
      masonry.lfCollapseColumns = true;
      masonry.lfSelectable = false;
    } else {
      for (const run of runs) {
        dataset.nodes.push({ cells: { lfCard: _itemCardCell(run) }, id: run.runId });
        masonry.lfCollapseColumns = false;
        masonry.lfSelectable = true;
      }
    }
    masonry.lfDataset = dataset;
    debugLog(WORKFLOW_OUTPUTS_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const buttonHandler = (e, store) => {
  const { comp, eventType } = e.detail;
  const { manager, view } = store.getState();
  switch (eventType) {
    case "click":
      switch (comp.rootElement.className) {
        // Action Button
        case ACTION_BUTTON_CLASSES._:
          manager.getDispatchers().runWorkflow();
          break;
        // Drawer
        case DRAWER_CLASSES.buttonComfyUi:
          const port = window.location.port || "8188";
          window.open(`http://localhost:${port}`, "_blank");
          break;
        case DRAWER_CLASSES.buttonDebug:
          store.getState().mutate.isDebug(!store.getState().isDebug);
          break;
        case DRAWER_CLASSES.buttonGithub:
          window.open("https://github.com/lucafoscili/lf-nodes", "_blank");
          break;
        // Header
        case HEADER_CLASSES.drawerToggle:
          const elements = manager.uiRegistry.get();
          const drawer = elements[DRAWER_CLASSES._];
          drawer.toggle();
          break;
        // Workflow
        case HEADER_CLASSES.serverIndicatorLight:
        case RESULTS_CLASSES.history:
          manager.runs.select(null, "history");
          break;
        case INPUTS_CLASSES.openButton:
          manager.workflow.download();
          break;
        case OUTPUTS_CLASSES.toggle:
          const isHistoryView = view === "history";
          if (isHistoryView) {
            manager.runs.select(null, "workflow");
          } else {
            manager.runs.select(null, "history");
          }
          break;
        case RESULTS_CLASSES.back:
          manager.runs.select(null, "workflow");
          break;
        default:
          return;
      }
      break;
    default:
      return;
  }
};
const { theme: theme$2 } = getLfFramework();
const ROOT_CLASS$2 = "inputs-section";
const INPUTS_CLASSES = {
  _: theme$2.bemClass(ROOT_CLASS$2),
  cell: theme$2.bemClass(ROOT_CLASS$2, "cell"),
  cells: theme$2.bemClass(ROOT_CLASS$2, "cells"),
  description: theme$2.bemClass(ROOT_CLASS$2, "description"),
  h3: theme$2.bemClass(ROOT_CLASS$2, "title-h3"),
  openButton: theme$2.bemClass(ROOT_CLASS$2, "title-open-button"),
  options: theme$2.bemClass(ROOT_CLASS$2, "options"),
  title: theme$2.bemClass(ROOT_CLASS$2, "title")
};
const _cells = () => {
  const cellWrapper = document.createElement("div");
  cellWrapper.className = INPUTS_CLASSES.cell;
  return cellWrapper;
};
const _description = () => {
  const p = document.createElement("p");
  p.className = INPUTS_CLASSES.description;
  return p;
};
const _options = () => {
  const optionsWrapper = document.createElement("div");
  optionsWrapper.className = INPUTS_CLASSES.options;
  return optionsWrapper;
};
const _title = (store) => {
  const lfIcon = theme$2.get.icon("download");
  const title = document.createElement("div");
  const h3 = document.createElement("h3");
  const openButton = document.createElement("lf-button");
  title.className = INPUTS_CLASSES.title;
  h3.className = INPUTS_CLASSES.h3;
  const label = "Download Workflow JSON";
  openButton.className = INPUTS_CLASSES.openButton;
  openButton.lfAriaLabel = label;
  openButton.lfIcon = lfIcon;
  openButton.lfStyling = "icon";
  openButton.lfUiSize = "xsmall";
  openButton.title = label;
  openButton.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  title.appendChild(h3);
  title.appendChild(openButton);
  return { h3, openButton, title };
};
const createInputsSection = (store) => {
  const { WORKFLOW_INPUTS_DESTROYED, WORKFLOW_INPUTS_MOUNTED, WORKFLOW_INPUTS_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in INPUTS_CLASSES) {
      const element = INPUTS_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(WORKFLOW_INPUTS_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[INPUTS_CLASSES._]) {
      return;
    }
    const workflow = manager.workflow.current();
    const _root = document.createElement("section");
    _root.className = INPUTS_CLASSES._;
    const description = _description();
    const options = _options();
    const { h3, openButton, title } = _title(store);
    const cellElements = [];
    if (workflow) {
      const inputCells = manager.workflow.cells("input");
      for (const id in inputCells) {
        if (!Object.prototype.hasOwnProperty.call(inputCells, id)) {
          continue;
        }
        const cell = inputCells[id];
        const wrapper = _cells();
        wrapper.dataset.shape = cell.shape || "";
        const component = createInputCell(cell);
        component.id = id;
        cellElements.push(component);
        wrapper.appendChild(component);
        options.appendChild(wrapper);
      }
    }
    uiRegistry.set(INPUTS_CLASSES.cells, cellElements);
    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(options);
    elements[MAIN_CLASSES._].prepend(_root);
    uiRegistry.set(INPUTS_CLASSES._, _root);
    uiRegistry.set(INPUTS_CLASSES.description, description);
    uiRegistry.set(INPUTS_CLASSES.h3, h3);
    uiRegistry.set(INPUTS_CLASSES.openButton, openButton);
    uiRegistry.set(INPUTS_CLASSES.options, options);
    uiRegistry.set(INPUTS_CLASSES.title, title);
    debugLog(WORKFLOW_INPUTS_MOUNTED);
  };
  const render = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const cells = elements[INPUTS_CLASSES.cells];
    const descr = elements[INPUTS_CLASSES.description];
    const h3 = elements[INPUTS_CLASSES.h3];
    descr.textContent = manager.workflow.description();
    h3.textContent = manager.workflow.title();
    const statuses = state.inputStatuses || {};
    cells == null ? void 0 : cells.forEach((cell) => {
      const id = cell.id;
      const parent = cell == null ? void 0 : cell.parentElement;
      const status = statuses[id] || "";
      if (cell && parent) {
        if (status) {
          parent.dataset.status = status;
        } else {
          delete parent.dataset.status;
        }
      }
    });
    debugLog(WORKFLOW_INPUTS_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
class WorkflowApiError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = "WorkflowApiError";
    this.payload = options.payload;
    this.status = options.status;
  }
}
const fetchWorkflowDefinitions = async () => {
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl("/workflows"), { method: "GET" });
  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {
    }
    throw new WorkflowApiError("Unauthorized", { status: 401 });
  }
  const data = await syntax.json.parse(response);
  if (!response.ok) {
    const message = `Failed to load workflows (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }
  if (!(data == null ? void 0 : data.workflows) || !Array.isArray(data.workflows.nodes)) {
    throw new WorkflowApiError("Invalid workflows response shape.", { payload: data });
  }
  return data.workflows;
};
const fetchWorkflowJSON = async (workflowId) => {
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl(`/workflows/${workflowId}`), { method: "GET" });
  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {
    }
    throw new WorkflowApiError("Unauthorized", { status: 401 });
  }
  const data = await syntax.json.parse(response);
  if (!response.ok) {
    const message = `Failed to load workflow JSON (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }
  return data;
};
const runWorkflow = async (payload) => {
  const { RUN_GENERIC } = ERROR_MESSAGES;
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl("/run"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {
    }
    throw new WorkflowApiError("Unauthorized", { status: 401 });
  }
  const data = await syntax.json.parse(response);
  if (!response.ok || !data) {
    const payloadData = (data == null ? void 0 : data.payload) || { detail: response.statusText };
    const detail = (payloadData == null ? void 0 : payloadData.detail) || response.statusText;
    throw new WorkflowApiError(`${RUN_GENERIC} (${detail})`, {
      payload: payloadData,
      status: response.status
    });
  }
  const runId = data.run_id;
  if (!runId) {
    throw new WorkflowApiError(`${RUN_GENERIC} (invalid response)`, {
      status: response.status
    });
  }
  return runId;
};
const uploadWorkflowFiles = async (files) => {
  var _a, _b;
  const { UPLOAD_GENERIC, UPLOAD_INVALID_RESPONSE, UPLOAD_MISSING_FILE } = ERROR_MESSAGES;
  const { syntax } = getLfFramework();
  if (!files || files.length === 0) {
    throw new WorkflowApiError(UPLOAD_MISSING_FILE, {
      payload: { error: { message: "missing_file" } }
    });
  }
  const formData = new FormData();
  files.forEach((file) => formData.append("file", file));
  const response = await fetch(buildApiUrl("/upload"), {
    method: "POST",
    body: formData
  });
  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {
    }
    throw new WorkflowApiError("Unauthorized", { status: 401 });
  }
  const data = await syntax.json.parse(response);
  if (isWorkflowAPIUploadResponse(data)) {
    if (!response.ok) {
      const { payload } = data;
      const detail = ((_a = payload == null ? void 0 : payload.error) == null ? void 0 : _a.message) || response.statusText;
      throw new WorkflowApiError(`${UPLOAD_GENERIC} (${detail})`, {
        payload
      });
    }
    return data;
  }
  if (isWorkflowAPIUploadPayload(data)) {
    if (!response.ok) {
      const detail = ((_b = data.error) == null ? void 0 : _b.message) || response.statusText;
      throw new WorkflowApiError(`${UPLOAD_GENERIC} (${detail})`, {
        payload: data
      });
    }
    return {
      payload: data
    };
  }
  throw new WorkflowApiError(UPLOAD_INVALID_RESPONSE, {
    status: response.status
  });
};
const _collectInputs = async (store) => {
  const state = store.getState();
  const { uiRegistry } = state.manager;
  const elements = uiRegistry.get();
  const cells = (elements == null ? void 0 : elements[INPUTS_CLASSES.cells]) || [];
  const inputs = {};
  for (const cell of cells) {
    const id = cell.id || "";
    _setCellStatus(store, id);
    switch (cell.tagName.toLowerCase()) {
      case "lf-chat": {
        const value = await cell.getHistory();
        inputs[id] = value;
        break;
      }
      case "lf-toggle": {
        const value = await cell.getValue();
        inputs[id] = value === "off" ? false : true;
        break;
      }
      case "lf-upload": {
        try {
          const value = await cell.getValue();
          inputs[id] = await _handleUploadCell(store, value);
        } catch (error) {
          _setCellStatus(store, id, "error");
          throw error;
        }
        break;
      }
      default: {
        const value = await cell.getValue();
        inputs[id] = value;
      }
    }
  }
  return inputs;
};
const _handleUploadCell = async (store, rawValue) => {
  var _a;
  const { ERROR_UPLOADING_FILE, RUNNING_UPLOADING_FILE } = STATUS_MESSAGES;
  const files = Array.isArray(rawValue) ? rawValue : rawValue;
  if (!files || files.length === 0) {
    throw new Error("No files selected for upload.");
  }
  try {
    setStatus$1(store, "running", RUNNING_UPLOADING_FILE);
    const { payload } = await uploadWorkflowFiles(files);
    const paths = (payload == null ? void 0 : payload.paths) || [];
    return paths.length === 1 ? paths[0] : paths;
  } catch (error) {
    setStatus$1(store, "error", ERROR_UPLOADING_FILE);
    if (error instanceof WorkflowApiError) {
      addNotification(store, {
        id: performance.now().toString(),
        message: `Upload failed: ${((_a = error.payload) == null ? void 0 : _a.detail) || error.message}`,
        status: "danger"
      });
    }
    throw error;
  }
};
const _setCellStatus = (store, id, status = "") => {
  const { WORKFLOW_INPUT_FLAGGED } = DEBUG_MESSAGES;
  const state = store.getState();
  const { current, manager, mutate } = state;
  const { uiRegistry } = manager;
  const elements = uiRegistry.get();
  const cells = (elements == null ? void 0 : elements[INPUTS_CLASSES.cells]) || [];
  const cell = cells.find((el) => el.id === id);
  const wrapper = cell == null ? void 0 : cell.parentElement;
  if (wrapper) {
    if (status) {
      wrapper.dataset.status = status;
    } else {
      delete wrapper.dataset.status;
    }
  }
  mutate.inputStatus(id, status);
  if (status) {
    debugLog(WORKFLOW_INPUT_FLAGGED, "informational", {
      cell: id,
      id: current.id,
      status
    });
  }
};
const workflowDispatcher = async (store) => {
  var _a, _b, _c, _d, _e;
  const { INPUTS_COLLECTED } = DEBUG_MESSAGES;
  const { NO_WORKFLOW_SELECTED } = NOTIFICATION_MESSAGES;
  const { ERROR_RUNNING_WORKFLOW, RUNNING_DISPATCHING_WORKFLOW, RUNNING_SUBMITTING_WORKFLOW } = STATUS_MESSAGES;
  const state = store.getState();
  const { current } = state;
  const id = current.id;
  if (!id) {
    addNotification(store, {
      id: performance.now().toString(),
      message: NO_WORKFLOW_SELECTED,
      status: "warning"
    });
    return;
  }
  setStatus$1(store, "running", RUNNING_SUBMITTING_WORKFLOW);
  let inputs;
  try {
    inputs = await _collectInputs(store);
    debugLog(INPUTS_COLLECTED, "informational", {
      id,
      inputKeys: Object.keys(inputs)
    });
  } catch (error) {
    const detail = error instanceof WorkflowApiError ? ((_a = error.payload) == null ? void 0 : _a.detail) || error.message : (error == null ? void 0 : error.message) || "Failed to collect inputs.";
    setStatus$1(store, "error", ERROR_RUNNING_WORKFLOW);
    addNotification(store, {
      id: performance.now().toString(),
      message: `Failed to collect inputs: ${detail}`,
      status: "danger"
    });
    return;
  }
  try {
    setStatus$1(store, "running", RUNNING_DISPATCHING_WORKFLOW);
    clearResults(store);
    const runId = await runWorkflow({ workflowId: id, inputs });
    const workflowName = ((_b = state.manager) == null ? void 0 : _b.workflow.title()) ?? id;
    const timestamp = Date.now();
    const clonedInputs = JSON.parse(JSON.stringify(inputs));
    upsertRun(store, {
      createdAt: timestamp,
      error: null,
      httpStatus: null,
      inputs: clonedInputs,
      outputs: null,
      resultPayload: null,
      runId,
      status: "pending",
      updatedAt: timestamp,
      workflowId: id,
      workflowName
    });
    ensureActiveRun(store, runId);
  } catch (error) {
    setStatus$1(store, "error", ERROR_RUNNING_WORKFLOW);
    if (error instanceof WorkflowApiError) {
      const inputName = (_d = (_c = error.payload) == null ? void 0 : _c.error) == null ? void 0 : _d.input;
      if (inputName) {
        _setCellStatus(store, inputName, "error");
      }
      addNotification(store, {
        id: performance.now().toString(),
        message: `Workflow run failed: ${((_e = error.payload) == null ? void 0 : _e.detail) || error.message}`,
        status: "danger"
      });
    }
  }
};
const { theme: theme$1 } = getLfFramework();
const ROOT_CLASS$1 = "dev-section";
const DEV_CLASSES = {
  _: theme$1.bemClass(ROOT_CLASS$1),
  card: theme$1.bemClass(ROOT_CLASS$1, "card")
};
const _createDataset = () => {
  return {
    nodes: [
      {
        id: "workflow-runner-debug",
        cells: {
          lfToggle: {
            shape: "toggle",
            value: false
          },
          lfCode: {
            shape: "code",
            value: ""
          },
          lfButton: {
            shape: "button",
            value: ""
          },
          lfButton_2: {
            shape: "button",
            value: ""
          }
        }
      }
    ]
  };
};
const createDevSection = (store) => {
  const { DEV_SECTION_DESTROYED, DEV_SECTION_MOUNTED, DEV_SECTION_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in DEV_CLASSES) {
      const element = DEV_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(DEV_SECTION_DESTROYED);
  };
  const mount = () => {
    var _a, _b;
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[DEV_CLASSES._]) {
      return;
    }
    const _root = document.createElement("div");
    _root.className = DEV_CLASSES._;
    const card = document.createElement("lf-card");
    card.className = DEV_CLASSES.card;
    card.lfLayout = "debug";
    card.lfDataset = _createDataset();
    const body = ((_b = (_a = manager.getAppRoot()) == null ? void 0 : _a.ownerDocument) == null ? void 0 : _b.body) ?? document.body;
    _root.appendChild(card);
    body.appendChild(_root);
    uiRegistry.set(DEV_CLASSES._, _root);
    uiRegistry.set(DEV_CLASSES.card, card);
    debugLog(DEV_SECTION_MOUNTED);
  };
  const render = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    debugLog(DEV_SECTION_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const { theme } = getLfFramework();
const ROOT_CLASS = "notifications-section";
const NOTIFICATIONS_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  _visible: theme.bemClass(ROOT_CLASS, void 0, { active: true }),
  item: theme.bemClass(ROOT_CLASS, "item")
};
const _checkForVisible = (_root) => {
  if (_root.hasChildNodes()) {
    _root.className = NOTIFICATIONS_CLASSES._visible;
  } else {
    _root.className = NOTIFICATIONS_CLASSES._;
  }
};
const _getStateCategory = (status) => {
  let category;
  switch (status) {
    case "danger":
    case "error":
      category = "danger";
      break;
    default:
      category = "info";
      break;
  }
  return category;
};
const createNotificationsSection = (store) => {
  const { NOTIFICATIONS_DESTROYED, NOTIFICATIONS_MOUNTED, NOTIFICATIONS_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in NOTIFICATIONS_CLASSES) {
      const element = NOTIFICATIONS_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(NOTIFICATIONS_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[NOTIFICATIONS_CLASSES._]) {
      return;
    }
    const _root = document.createElement("div");
    _root.className = NOTIFICATIONS_CLASSES._;
    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(NOTIFICATIONS_CLASSES._, _root);
    debugLog(NOTIFICATIONS_MOUNTED);
  };
  const render = () => {
    const state = store.getState();
    const { manager, notifications } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const _root = elements[NOTIFICATIONS_CLASSES._];
    for (const notif of notifications) {
      const { id, message, status } = notif;
      const uid = `${NOTIFICATIONS_CLASSES.item}-${id}`;
      const element = document.createElement("lf-toast");
      element.className = NOTIFICATIONS_CLASSES.item;
      element.lfCloseCallback = () => {
        uiRegistry.remove(uid);
        _checkForVisible(_root);
      };
      element.lfIcon = status === "danger" ? theme.get.icon("alertTriangle") : theme.get.icon("hexagonInfo");
      element.lfMessage = message;
      element.lfUiState = _getStateCategory(status);
      element.lfTimer = status === "danger" ? 5e3 : 2500;
      _root.appendChild(element);
      requestAnimationFrame(() => {
        _root.scrollTop = _root.scrollHeight;
      });
      _checkForVisible(_root);
      uiRegistry.set(uid, element);
      state.mutate.notifications.removeById(id);
    }
    debugLog(NOTIFICATIONS_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
var __classPrivateFieldSet$1 = function(receiver, state, value, kind, f) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$1 = function(receiver, state, kind, f) {
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var _WorkflowRunnerClient_ES, _WorkflowRunnerClient_STORE, _WorkflowRunnerClient_WORKFLOW_NAMES, _WorkflowRunnerClient_CACHE_KEY, _WorkflowRunnerClient_CACHE_EXPIRY_MS, _WorkflowRunnerClient_INITIAL_BACKOFF_MS, _WorkflowRunnerClient_MAX_BACKOFF_MS, _WorkflowRunnerClient_POLLING_INTERVAL_MS, _WorkflowRunnerClient_RUNS_QUERY_LIMIT, _WorkflowRunnerClient_EVENT_RUN, _WorkflowRunnerClient_EVENT_QUEUE, _WorkflowRunnerClient_LAST_SEQ, _WorkflowRunnerClient_RUNS, _WorkflowRunnerClient_WORKFLOW_CACHE, _WorkflowRunnerClient_STATE, _WorkflowRunnerClient_POLLING, _WorkflowRunnerClient_BACKOFF_MS, _WorkflowRunnerClient_INFLIGHT_RECONCILES;
class WorkflowRunnerClient {
  constructor(store) {
    _WorkflowRunnerClient_ES.set(this, null);
    _WorkflowRunnerClient_STORE.set(this, void 0);
    _WorkflowRunnerClient_WORKFLOW_NAMES.set(this, {});
    _WorkflowRunnerClient_CACHE_KEY.set(this, "lf-runs-cache");
    _WorkflowRunnerClient_CACHE_EXPIRY_MS.set(this, 60 * 60 * 1e3);
    _WorkflowRunnerClient_INITIAL_BACKOFF_MS.set(this, 1e3);
    _WorkflowRunnerClient_MAX_BACKOFF_MS.set(this, 3e4);
    _WorkflowRunnerClient_POLLING_INTERVAL_MS.set(this, 3e3);
    _WorkflowRunnerClient_RUNS_QUERY_LIMIT.set(this, 200);
    _WorkflowRunnerClient_EVENT_RUN.set(this, "run");
    _WorkflowRunnerClient_EVENT_QUEUE.set(this, "queue");
    _WorkflowRunnerClient_LAST_SEQ.set(this, /* @__PURE__ */ new Map());
    _WorkflowRunnerClient_RUNS.set(this, /* @__PURE__ */ new Map());
    _WorkflowRunnerClient_WORKFLOW_CACHE.set(this, /* @__PURE__ */ new Map());
    _WorkflowRunnerClient_STATE.set(this, {
      connecting: false,
      processingSnapshot: false
    });
    _WorkflowRunnerClient_POLLING.set(this, {
      timer: null,
      abortController: null
    });
    _WorkflowRunnerClient_BACKOFF_MS.set(this, 1e3);
    _WorkflowRunnerClient_INFLIGHT_RECONCILES.set(this, /* @__PURE__ */ new Map());
    this.onUpdate = (runs) => {
      var _a;
      if (Object.keys(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_NAMES, "f")).length === 0) {
        const workflows = ((_a = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f").getState().workflows) == null ? void 0 : _a.nodes) || [];
        for (let i = 0; i < workflows.length; i++) {
          const w = workflows[i];
          __classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_NAMES, "f")[w.id] = String(w.value);
        }
      }
      for (const rec of runs.values()) {
        const uiEntry = recordToUI(rec, __classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_NAMES, "f"));
        upsertRun(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f"), uiEntry);
      }
      ensureActiveRun(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f"));
    };
    this.queueHandler = (pending, running) => {
      try {
        const state = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f").getState();
        const nr = pending + running;
        state.mutate.queuedJobs(nr);
      } catch (e) {
        debugLog("queueHandler error", "informational", e);
      }
    };
    __classPrivateFieldSet$1(this, _WorkflowRunnerClient_STORE, store, "f");
  }
  // Preload workflow names to avoid fetching them individually
  setWorkflowNames(names) {
    for (const [id, name] of names) {
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f").set(id, name);
    }
    this.emitUpdate();
  }
  emitUpdate() {
    if (this.onUpdate)
      this.onUpdate(new Map(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f")));
    this.saveCache();
  }
  // Reconcile server record for a run via REST (de-duplicated)
  reconcileRun(run_id) {
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f").has(run_id)) {
      return;
    }
    const promise = this._reconcileRunOnce(run_id).catch(() => {
    }).finally(() => {
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f").delete(run_id);
    });
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f").set(run_id, promise);
  }
  async _reconcileRunOnce(run_id) {
    try {
      const resp = await fetch(`${API_ROOT}/run/${encodeURIComponent(run_id)}/status`, {
        credentials: "include"
      });
      if (resp.status === 404) {
        this.removeRun(run_id);
        return;
      }
      if (!resp || !resp.ok) {
        debugLog("reconcileRun: fetch failed", "informational", resp == null ? void 0 : resp.status);
        return;
      }
      const data = await resp.json();
      const rec = {
        run_id: data.run_id,
        workflow_id: data.workflow_id,
        status: data.status,
        seq: data.seq || 0,
        owner_id: data.owner_id,
        created_at: data.created_at,
        updated_at: data.updated_at,
        result: data.result,
        error: data.error
      };
      this.upsertRun(rec);
    } catch (e) {
      debugLog("reconcileRun error", "warning", e);
      throw e;
    }
  }
  applyEvent(ev) {
    if (!ev || !ev.run_id || typeof ev.status === "undefined" || ev.status === null) {
      debugLog("applyEvent: invalid run record (missing run_id or status)", "warning", ev);
      return;
    }
    const last = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").get(ev.run_id) ?? -1;
    if (last >= 0 && ev.seq > last + 1) {
      this.reconcileRun(ev.run_id);
    }
    this.upsertRun(ev);
  }
  // Upsert with seq monotonicity guard and workflow name fetch
  upsertRun(rec) {
    const last = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").get(rec.run_id) ?? -1;
    if (rec.seq <= last)
      return;
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").set(rec.run_id, rec.seq);
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").set(rec.run_id, rec);
    if (rec.workflow_id && !__classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f").has(rec.workflow_id)) {
      this.fetchWorkflowNames([rec.workflow_id]);
    }
    this.emitUpdate();
  }
  // Remove a run completely from state and cache (used when server returns 404)
  removeRun(runId) {
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").delete(runId);
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").delete(runId);
    this.emitUpdate();
  }
  processSnapshotArray(arr) {
    const activeSet = /* @__PURE__ */ new Set();
    const missingWorkflowIds = /* @__PURE__ */ new Set();
    const runsMissingWorkflowId = [];
    for (const s of arr) {
      if (!s || !s.run_id || typeof s.status === "undefined" || s.status === null) {
        console.warn("processSnapshotArray: ignoring invalid snapshot entry", s);
        continue;
      }
      activeSet.add(s.run_id);
      const last = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").get(s.run_id) ?? -1;
      if (s.seq <= last)
        continue;
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").set(s.run_id, s.seq);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").set(s.run_id, s);
      if (s.workflow_id && !__classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f").has(s.workflow_id)) {
        missingWorkflowIds.add(s.workflow_id);
      }
      if (!s.workflow_id) {
        runsMissingWorkflowId.push(s.run_id);
      }
    }
    this.emitUpdate();
    (async () => {
      try {
        const toReconcile = [];
        for (const [id, rec] of __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").entries()) {
          if (rec.status === "running" && !activeSet.has(id)) {
            toReconcile.push(id);
          }
        }
        for (const id of toReconcile) {
          this.reconcileRun(id);
        }
      } catch (e) {
      }
      if (missingWorkflowIds.size > 0) {
        try {
          this.fetchWorkflowNames(Array.from(missingWorkflowIds));
        } catch (e) {
        }
      }
      for (const runId of runsMissingWorkflowId) {
        try {
          this.reconcileRun(runId);
        } catch (e) {
        }
      }
    })();
  }
  // Fetch human-friendly workflow names for given ids and cache them
  async fetchWorkflowNames(ids) {
    const needs = ids.filter((id) => !!id && !__classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f").has(id));
    if (needs.length === 0)
      return;
    try {
      const resp = await fetch(`${API_ROOT}/workflows?ids=${encodeURIComponent(needs.join(","))}`, {
        credentials: "include"
      });
      if (!resp || !resp.ok)
        return;
      const data = await resp.json();
      let items = [];
      try {
        if (Array.isArray(data)) {
          items = data;
        } else if (data) {
          if (Array.isArray(data.workflows)) {
            items = data.workflows;
          } else if (data.items && Array.isArray(data.items)) {
            items = data.items;
          } else if (data.workflows && Array.isArray(data.workflows.nodes)) {
            items = data.workflows.nodes.map((n) => ({
              workflow_id: n.id ?? n.key ?? n.value,
              name: n.value ?? n.title ?? n.name
            }));
          } else if (data.workflows && typeof data.workflows === "object") {
            for (const k of Object.keys(data.workflows)) {
              const v = data.workflows[k];
              if (typeof v === "string") {
                items.push({ workflow_id: k, name: v });
              } else if (v && typeof v === "object") {
                items.push({
                  workflow_id: v.id ?? k,
                  name: v.name ?? v.value ?? v.title ?? JSON.stringify(v)
                });
              }
            }
          }
        }
      } catch (e) {
        debugLog("fetchWorkflowNames: failed to normalize response", "warning", e);
        items = [];
      }
      if (!items || typeof items[Symbol.iterator] !== "function") {
        items = [];
      }
      for (const it of items) {
        try {
          const id = it.workflow_id ?? it.id ?? it.workflowId ?? it.key;
          const name = it.name ?? it.title ?? it.workflow_name ?? it.value ?? null;
          if (id && name)
            __classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f").set(id, name);
        } catch (e) {
          debugLog("fetchWorkflowNames: skipping malformed item", "warning", e);
        }
      }
      this.emitUpdate();
    } catch (e) {
      debugLog("fetchWorkflowNames error", "warning", e);
    }
  }
  // Save active runs to localStorage (IDs-only for schema stability)
  saveCache() {
    try {
      if (typeof localStorage === "undefined")
        return;
      const ids = Array.from(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").keys());
      const payload = {
        version: 1,
        cached_at: Date.now(),
        run_ids: ids.slice(-300)
        // cap to recent 300 runs
      };
      localStorage.setItem(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_CACHE_KEY, "f"), JSON.stringify(payload));
    } catch (e) {
      debugLog("LocalStorage write skipped", "warning", e);
    }
  }
  // Load cached run IDs (optimistic placeholders until hydrated)
  loadCacheIds() {
    try {
      if (typeof localStorage === "undefined")
        return [];
      const raw = localStorage.getItem(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_CACHE_KEY, "f"));
      if (!raw)
        return [];
      const parsed = JSON.parse(raw);
      if (parsed.version !== 1)
        return [];
      const cacheAge = Date.now() - (parsed.cached_at ?? 0);
      if (cacheAge > __classPrivateFieldGet$1(this, _WorkflowRunnerClient_CACHE_EXPIRY_MS, "f"))
        return [];
      return Array.isArray(parsed.run_ids) ? parsed.run_ids : [];
    } catch (e) {
      debugLog("loadCacheIds error", "warning", e);
      return [];
    }
  }
  // Seed placeholder entries for optimistic UI (hydrated later)
  seedPlaceholders(ids) {
    for (const id of ids) {
      if (!__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").has(id)) {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").set(id, {
          run_id: id,
          status: "pending",
          // placeholder status; harmless until hydrated
          seq: -1,
          created_at: 0,
          updated_at: 0,
          owner_id: null,
          workflow_id: null
          // no result/error
        });
      }
    }
    this.emitUpdate();
  }
  // Cold-load runs from server before SSE connection (restores state after refresh)
  async coldLoadRuns() {
    try {
      const resp = await fetch(`${API_ROOT}/workflow-runner/runs?status=pending,running,succeeded,failed,cancelled,timeout&owner=me&limit=${__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS_QUERY_LIMIT, "f")}`, { credentials: "include" });
      if (!resp || !resp.ok) {
        debugLog("coldLoadRuns: fetch failed", "informational", resp == null ? void 0 : resp.status);
        return;
      }
      const data = await resp.json();
      const arr = data.runs || [];
      const serverIds = new Set(arr.map((r) => r.run_id));
      this.processSnapshotArray(arr);
      for (const localId of Array.from(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").keys())) {
        if (!serverIds.has(localId)) {
          this.reconcileRun(localId);
        }
      }
    } catch (e) {
      debugLog("coldLoadRuns error", "warning", e);
    }
  }
  //#region SSE Connection
  async start() {
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f") || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").connecting) {
      return;
    }
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").connecting = true;
    const cachedIds = this.loadCacheIds();
    if (cachedIds.length > 0) {
      this.seedPlaceholders(cachedIds);
    }
    await this.coldLoadRuns();
    const serverIds = new Set(Array.from(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").keys()).filter((id) => {
      const run = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").get(id);
      return run && run.seq >= 0;
    }));
    for (const id of cachedIds) {
      if (!serverIds.has(id)) {
        this.reconcileRun(id);
      }
    }
    this.openSse();
  }
  openSse() {
    const url = `${API_ROOT}/workflow-runner/events`;
    try {
      __classPrivateFieldSet$1(this, _WorkflowRunnerClient_ES, new EventSource(url), "f");
    } catch (err) {
      __classPrivateFieldSet$1(this, _WorkflowRunnerClient_ES, EventSource(url), "f");
    }
    try {
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f") && typeof __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f") === "object") {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").onmessage = (e) => {
          try {
            const payload = JSON.parse(e.data);
            this.applyEvent({
              run_id: payload.run_id,
              workflow_id: payload.workflow_id,
              status: payload.status,
              seq: payload.seq ?? 0,
              owner_id: payload.owner_id,
              created_at: payload.created_at,
              updated_at: payload.updated_at,
              result: payload.result,
              error: payload.error
            });
          } catch (err) {
            debugLog("invalid generic event message", "informational", err);
          }
          if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").processingSnapshot) {
            __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").processingSnapshot = false;
          }
        };
      }
    } catch (e) {
      debugLog("EventSource onmessage assignment failed", "informational", e);
    }
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").processingSnapshot = true;
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").onopen = () => {
      __classPrivateFieldSet$1(this, _WorkflowRunnerClient_BACKOFF_MS, __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INITIAL_BACKOFF_MS, "f"), "f");
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer) {
        clearInterval(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer);
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer = null;
        if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController) {
          try {
            __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController.abort();
          } catch {
          }
          __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController = null;
        }
      }
    };
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").onerror = () => {
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f")) {
        try {
          __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").close();
        } catch {
          debugLog("EventSource close failed", "informational");
        }
        __classPrivateFieldSet$1(this, _WorkflowRunnerClient_ES, null, "f");
      }
      this.startPollingFallback();
      const delay = this.backoffWithJitter();
      setTimeout(() => this.start(), delay);
    };
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").addEventListener(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_EVENT_RUN, "f"), (e) => {
      try {
        const payload = JSON.parse(e.data);
        this.applyEvent({
          run_id: payload.run_id,
          workflow_id: payload.workflow_id,
          status: payload.status,
          seq: payload.seq ?? 0,
          owner_id: payload.owner_id,
          created_at: payload.created_at,
          updated_at: payload.updated_at,
          result: payload.result,
          error: payload.error
        });
      } catch (err) {
        debugLog("Invalid run event", "warning", err);
      }
    });
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").addEventListener(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_EVENT_QUEUE, "f"), (e) => {
      try {
        const payload = JSON.parse(e.data);
        this.handleQueuePayload(payload);
      } catch (err) {
        debugLog("Invalid queue event", "warning", err);
      }
    });
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").connecting = false;
  }
  handleQueuePayload(payload) {
    if (!payload) {
      return;
    }
    try {
      if (payload && (payload.type === "queue_status" || typeof payload.pending === "number")) {
        const pending = Number(payload.pending || 0) || 0;
        const running = Number(payload.running || 0) || 0;
        if (this.queueHandler) {
          this.queueHandler(pending, running);
        }
        return;
      }
      if (payload && (payload.run_id || payload.status || payload.seq !== void 0)) {
        this.applyEvent({
          run_id: payload.run_id,
          workflow_id: payload.workflow_id,
          status: payload.status,
          seq: payload.seq ?? 0,
          owner_id: payload.owner_id,
          created_at: payload.created_at,
          updated_at: payload.updated_at,
          result: payload.result,
          error: payload.error
        });
      }
    } catch (e) {
      debugLog("handleQueuePayload error", "warning", e);
    }
    try {
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f") && typeof __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f") === "object") {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").onmessage = (e) => {
          try {
            const payload2 = JSON.parse(e.data);
            this.applyEvent({
              run_id: payload2.run_id,
              workflow_id: payload2.workflow_id,
              status: payload2.status,
              seq: payload2.seq ?? 0,
              owner_id: payload2.owner_id,
              created_at: payload2.created_at,
              updated_at: payload2.updated_at,
              result: payload2.result,
              error: payload2.error
            });
          } catch (err) {
          }
          if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").processingSnapshot) {
            __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").processingSnapshot = false;
          }
        };
      }
    } catch (e) {
      debugLog("EventSource onmessage reassignment failed", "informational", e);
    }
  }
  stop() {
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f")) {
      try {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").close();
      } catch {
      }
      __classPrivateFieldSet$1(this, _WorkflowRunnerClient_ES, null, "f");
    }
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer) {
      clearInterval(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer = null;
    }
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController) {
      try {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController.abort();
      } catch {
      }
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController = null;
    }
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f").clear();
  }
  getRuns() {
    return __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f");
  }
  getLastSeq() {
    return __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f");
  }
  /**
   * Test API: returns a minimal test-only facade exposing internal maps
   * and operations used by unit tests. Prefer public behavior where
   * possible; this API exists solely to avoid fragile `as any` casts in
   * tests and is intentionally small.
   */
  getTestApi() {
    const self = this;
    self.applyEvent = this.applyEvent.bind(this);
    self.upsertRun = this.upsertRun.bind(this);
    self.reconcileRun = this.reconcileRun.bind(this);
    self.pollActiveRuns = this.pollActiveRuns.bind(this);
    self.coldLoadRuns = this.coldLoadRuns.bind(this);
    self.processSnapshotArray = this.processSnapshotArray.bind(this);
    self.saveCache = this.saveCache.bind(this);
    self.loadCacheIds = this.loadCacheIds.bind(this);
    self.seedPlaceholders = this.seedPlaceholders.bind(this);
    self.start = this.start.bind(this);
    self.stop = this.stop.bind(this);
    self.fetchWorkflowNames = this.fetchWorkflowNames.bind(this);
    self.setWorkflowNames = this.setWorkflowNames.bind(this);
    self.lastSeq = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f");
    self.runs = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f");
    self.inflightReconciles = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f");
    self.processingSnapshot = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").processingSnapshot;
    self.cacheKey = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_CACHE_KEY, "f");
    self.workflowNames = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f");
    self.store = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f");
    return this;
  }
  startPollingFallback() {
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer) {
      return;
    }
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer = setInterval(() => this.pollActiveRuns(), __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING_INTERVAL_MS, "f"));
    this.pollActiveRuns();
  }
  async pollActiveRuns() {
    try {
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController) {
        try {
          __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController.abort();
        } catch {
        }
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController = null;
      }
      const ac = new AbortController();
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController = ac;
      const resp = await fetch(`${API_ROOT}/workflow-runner/runs?status=pending,running&owner=me&limit=${__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS_QUERY_LIMIT, "f")}`, { signal: ac.signal, credentials: "include" });
      if (!resp.ok) {
        return;
      }
      const data = await resp.json();
      const arr = data.runs || [];
      this.processSnapshotArray(arr);
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController === ac) {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController = null;
      }
    } catch (e) {
      if (e && (e.name === "AbortError" || e.code === "ABORT_ERR") || e instanceof DOMException && e.name === "AbortError") ;
      else {
        debugLog("pollActiveRuns error", "warning", e);
      }
    }
  }
  backoffWithJitter() {
    const base = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_BACKOFF_MS, "f");
    const jitterFactor = 0.5 + Math.random() * 0.5;
    return Math.floor(base * jitterFactor);
  }
}
_WorkflowRunnerClient_ES = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_STORE = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_WORKFLOW_NAMES = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_CACHE_KEY = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_CACHE_EXPIRY_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_INITIAL_BACKOFF_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_MAX_BACKOFF_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_POLLING_INTERVAL_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_RUNS_QUERY_LIMIT = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_EVENT_RUN = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_EVENT_QUEUE = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_LAST_SEQ = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_RUNS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_WORKFLOW_CACHE = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_STATE = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_POLLING = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_BACKOFF_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_INFLIGHT_RECONCILES = /* @__PURE__ */ new WeakMap();
const RUN_PARAM = "runId";
const VIEW_PARAM = "view";
const WORKFLOW_PARAM = "workflowId";
const parseRouteFromLocation = (location = window.location) => {
  const params = new URLSearchParams(location.search);
  const runId = params.get(RUN_PARAM);
  const workflowId = params.get(WORKFLOW_PARAM);
  const viewParam = params.get(VIEW_PARAM);
  if (runId) {
    return {
      view: "run",
      runId,
      workflowId
    };
  }
  if (viewParam === "history") {
    return {
      view: "history",
      workflowId
    };
  }
  if (viewParam === "home") {
    return {
      view: "home"
    };
  }
  if (workflowId) {
    return {
      view: "workflow",
      workflowId
    };
  }
  return {
    view: "home"
  };
};
const routesEqual = (a, b) => {
  if (a === b) {
    return true;
  }
  if (!a || !b) {
    return false;
  }
  return a.view === b.view && (a.workflowId ?? null) === (b.workflowId ?? null) && (a.runId ?? null) === (b.runId ?? null);
};
const replaceRouteInHistory = (route) => {
  const params = new URLSearchParams();
  switch (route.view) {
    case "history":
      params.set(VIEW_PARAM, "history");
      if (route.workflowId) {
        params.set(WORKFLOW_PARAM, route.workflowId);
      }
      break;
    case "run":
      if (route.runId) {
        params.set(RUN_PARAM, route.runId);
      }
      if (route.workflowId) {
        params.set(WORKFLOW_PARAM, route.workflowId);
      }
      params.set(VIEW_PARAM, "run");
      break;
    case "workflow":
      if (route.workflowId) {
        params.set(WORKFLOW_PARAM, route.workflowId);
      }
      break;
  }
  const query = params.toString();
  const url = query ? `${window.location.pathname}?${query}` : window.location.pathname;
  window.history.replaceState({}, "", url);
};
const subscribeToRouteChanges = (callback) => {
  const handler = () => callback(parseRouteFromLocation());
  window.addEventListener("popstate", handler);
  return () => window.removeEventListener("popstate", handler);
};
const createRoutingController = ({ store }) => {
  let currentRoute = null;
  let pendingRoute = null;
  let isApplyingRoute = false;
  let unsubscribe;
  const hasWorkflowsLoaded = () => {
    const { workflows } = store.getState();
    return Array.isArray(workflows == null ? void 0 : workflows.nodes) && workflows.nodes.length > 0;
  };
  const workflowExists = (workflowId) => {
    var _a;
    const { workflows } = store.getState();
    return Boolean((_a = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a.some((node) => node.id === workflowId));
  };
  const updateRouteFromState = (precomputed) => {
    if (isApplyingRoute) {
      return;
    }
    const state = store.getState();
    const nextRoute = precomputed ?? computeRouteFromState(state);
    const normalized = normalizeRoute(nextRoute, state).route;
    if (!routesEqual(normalized, currentRoute)) {
      currentRoute = normalized;
      replaceRouteInHistory(normalized);
    }
  };
  const applyRoute = (route, allowDefer = true) => {
    if (allowDefer && !hasWorkflowsLoaded()) {
      pendingRoute = route;
      return;
    }
    isApplyingRoute = true;
    pendingRoute = null;
    try {
      const state = store.getState();
      const { route: normalizedRoute, clearResults: clearResults2 } = normalizeRoute(route, state);
      const workflowId = normalizedRoute.workflowId ?? null;
      if (workflowId && state.current.id !== workflowId && workflowExists(workflowId)) {
        state.mutate.workflow(workflowId);
      }
      changeView(store, normalizedRoute.view, {
        runId: normalizedRoute.runId ?? null,
        clearResults: clearResults2
      });
    } finally {
      isApplyingRoute = false;
      updateRouteFromState();
    }
  };
  const applyPendingRouteIfNeeded = () => {
    if (pendingRoute) {
      const route = pendingRoute;
      pendingRoute = null;
      applyRoute(route, false);
    } else {
      updateRouteFromState();
    }
  };
  const handleRouteChange = (route) => {
    pendingRoute = route;
    applyRoute(route);
  };
  const initialize = () => {
    currentRoute = null;
    pendingRoute = parseRouteFromLocation();
    unsubscribe = subscribeToRouteChanges((route) => {
      handleRouteChange(route);
    });
  };
  const destroy = () => {
    if (unsubscribe) {
      unsubscribe();
      unsubscribe = void 0;
    }
  };
  return {
    applyPendingRouteIfNeeded,
    destroy,
    getPendingRoute: () => pendingRoute,
    initialize,
    updateRouteFromState
  };
};
const normalizeRoute = (route, state) => {
  const { runs, current, workflows } = state;
  const availableNodes = (workflows == null ? void 0 : workflows.nodes) ?? [];
  const workflowExists = (id) => Boolean(id && availableNodes.some((node) => node.id === id));
  const findRun = (runId2) => runId2 ? runs.find((run2) => run2.runId === runId2) ?? null : null;
  const run = findRun(route.runId ?? null);
  let workflowId = route.workflowId ?? void 0;
  if (workflowId && !workflowExists(workflowId)) {
    workflowId = void 0;
  }
  const runWorkflowId = (run == null ? void 0 : run.workflowId) ?? null;
  if (workflowId === void 0 && workflowExists(runWorkflowId)) {
    workflowId = runWorkflowId ?? void 0;
  } else if (workflowId === void 0 && workflowExists(current.id)) {
    workflowId = current.id ?? void 0;
  }
  let runId = (run == null ? void 0 : run.runId) ?? void 0;
  let view = route.view;
  if (view === "run") {
    if (!runId) {
      view = "workflow";
    }
  } else if (view === "history" || view === "workflow") {
    runId = void 0;
  } else if (view === "home") {
    workflowId = void 0;
    runId = void 0;
  } else {
    view = "workflow";
    runId = void 0;
  }
  if (view !== "run") {
    runId = void 0;
  }
  const normalizedRoute = { view };
  if (workflowId) {
    normalizedRoute.workflowId = workflowId;
  }
  if (view === "run" && runId) {
    normalizedRoute.runId = runId;
    if (runWorkflowId && workflowExists(runWorkflowId)) {
      normalizedRoute.workflowId = runWorkflowId;
    }
  }
  const clearResults2 = normalizedRoute.view === "run" && normalizedRoute.runId ? false : void 0;
  return {
    route: normalizedRoute,
    clearResults: clearResults2
  };
};
const INIT_ERROR = "Mutate not initialized";
const INIT_CB = () => {
  throw new Error(INIT_ERROR);
};
const initState = () => ({
  current: { status: "idle", message: "", id: null },
  currentRunId: null,
  inputStatuses: {},
  isDebug: false,
  manager: null,
  mutate: {
    isDebug: INIT_CB,
    manager: INIT_CB,
    inputStatus: INIT_CB,
    queuedJobs: INIT_CB,
    notifications: {
      add: INIT_CB,
      removeById: INIT_CB,
      removeByIndex: INIT_CB
    },
    results: INIT_CB,
    runs: {
      clear: INIT_CB,
      upsert: INIT_CB
    },
    runId: INIT_CB,
    selectRun: INIT_CB,
    status: INIT_CB,
    view: INIT_CB,
    workflow: INIT_CB,
    workflows: INIT_CB
  },
  notifications: [],
  queuedJobs: -1,
  results: null,
  runs: [],
  selectedRunId: null,
  view: "workflow",
  workflows: {
    nodes: []
  }
});
const createWorkflowRunnerStore = (initialState) => {
  let state = initialState;
  const listeners = /* @__PURE__ */ new Set();
  const pendingMutations = [];
  let isApplyingMutation = false;
  const cloneWorkflowsDataset = (dataset) => ({
    ...dataset,
    columns: dataset.columns ? dataset.columns.slice() : void 0,
    nodes: Array.isArray(dataset.nodes) ? dataset.nodes.slice() : []
  });
  const createDraft = (source) => ({
    ...source,
    current: { ...source.current },
    inputStatuses: { ...source.inputStatuses },
    notifications: source.notifications.slice(),
    runs: source.runs.map((run) => ({ ...run })),
    workflows: cloneWorkflowsDataset(source.workflows)
  });
  const getState = () => state;
  const setState = (updater) => {
    const nextState = updater(state);
    if (nextState === state) {
      return;
    }
    state = nextState;
    for (const listener of listeners) {
      listener(state);
    }
  };
  const subscribe = (listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  };
  const enqueueMutation = (mutation) => {
    pendingMutations.push(mutation);
    if (isApplyingMutation) {
      return;
    }
    isApplyingMutation = true;
    try {
      while (pendingMutations.length > 0) {
        const nextMutation = pendingMutations.shift();
        if (nextMutation) {
          nextMutation();
        }
      }
    } finally {
      isApplyingMutation = false;
    }
  };
  const applyMutation = (mutator) => {
    enqueueMutation(() => setState((current) => {
      const draft = createDraft(current);
      mutator(draft);
      return draft;
    }));
  };
  const mutate = {
    isDebug: (isDebug) => applyMutation((draft) => {
      draft.isDebug = isDebug;
    }),
    manager: (manager) => applyMutation((draft) => {
      draft.manager = manager;
    }),
    inputStatus: (cellId, status) => applyMutation((draft) => {
      if (status) {
        draft.inputStatuses = {
          ...draft.inputStatuses,
          [cellId]: status
        };
      } else if (cellId in draft.inputStatuses) {
        const { [cellId]: _removed, ...rest } = draft.inputStatuses;
        draft.inputStatuses = rest;
      }
    }),
    notifications: {
      add: (notification) => applyMutation((draft) => {
        draft.notifications.push(notification);
      }),
      removeById: (id) => applyMutation((draft) => {
        draft.notifications = draft.notifications.filter((n) => n.id !== id);
      }),
      removeByIndex: (index) => applyMutation((draft) => {
        draft.notifications.splice(index, 1);
      })
    },
    queuedJobs: (count) => applyMutation((draft) => {
      draft.queuedJobs = count;
    }),
    results: (results) => applyMutation((draft) => {
      draft.results = results;
    }),
    runId: (runId) => applyMutation((draft) => {
      draft.currentRunId = runId;
    }),
    runs: {
      clear: () => applyMutation((draft) => {
        draft.runs = [];
      }),
      upsert: (entry) => applyMutation((draft) => {
        const now = entry.updatedAt ?? Date.now();
        const existingIndex = draft.runs.findIndex((run) => run.runId === entry.runId);
        if (existingIndex >= 0) {
          const current = draft.runs[existingIndex];
          const createdAt = entry.createdAt ?? current.createdAt;
          const nextRuns = draft.runs.slice();
          nextRuns[existingIndex] = {
            ...current,
            ...entry,
            createdAt,
            updatedAt: now,
            status: entry.status ?? current.status,
            workflowId: entry.workflowId ?? current.workflowId,
            workflowName: entry.workflowName ?? current.workflowName,
            inputs: entry.inputs ?? current.inputs,
            outputs: entry.outputs ?? current.outputs,
            error: entry.error ?? current.error ?? null,
            httpStatus: entry.httpStatus !== void 0 ? entry.httpStatus : current.httpStatus,
            resultPayload: entry.resultPayload !== void 0 ? entry.resultPayload : current.resultPayload
          };
          draft.runs = nextRuns;
        } else {
          const createdAt = entry.createdAt ?? now;
          const nextRuns = draft.runs.filter((run) => run.runId !== entry.runId);
          draft.runs = [
            {
              runId: entry.runId,
              createdAt,
              updatedAt: now,
              status: entry.status ?? "pending",
              workflowId: entry.workflowId ?? null,
              workflowName: entry.workflowName ?? "Unnamed workflow",
              inputs: entry.inputs ?? {},
              outputs: entry.outputs ?? null,
              error: entry.error ?? null,
              httpStatus: entry.httpStatus ?? null,
              resultPayload: entry.resultPayload === void 0 ? null : entry.resultPayload ?? null
            },
            ...nextRuns
          ];
        }
      })
    },
    selectRun: (runId) => applyMutation((draft) => {
      draft.selectedRunId = runId;
    }),
    view: (view) => applyMutation((draft) => {
      draft.view = view;
    }),
    status: (status, message) => setStatus(status, message, setState),
    workflow: (workflowId) => setWorkflow(workflowId, setState),
    workflows: (workflows) => applyMutation((draft) => {
      draft.workflows = workflows;
    })
  };
  state.mutate = mutate;
  return {
    getState,
    setState,
    subscribe
  };
};
const setStatus = (status, message, setState) => {
  setState((state) => ({
    ...state,
    current: {
      ...state.current,
      status,
      message: message ?? DEFAULT_STATUS_MESSAGES[status]
    }
  }));
};
const setWorkflow = (id, setState) => {
  setState((state) => ({
    ...state,
    inputStatuses: {},
    current: {
      ...state.current,
      id
    },
    currentRunId: null,
    results: null,
    selectedRunId: null,
    view: "workflow"
  }));
};
var __classPrivateFieldSet = function(receiver, state, value, kind, f) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet = function(receiver, state, kind, f) {
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var _LfWorkflowRunnerManager_instances, _LfWorkflowRunnerManager_FRAMEWORK, _LfWorkflowRunnerManager_STORE, _LfWorkflowRunnerManager_CLIENT, _LfWorkflowRunnerManager_APP_ROOT, _LfWorkflowRunnerManager_SECTIONS, _LfWorkflowRunnerManager_UI_REGISTRY, _LfWorkflowRunnerManager_DISPATCHERS, _LfWorkflowRunnerManager_ROUTING, _LfWorkflowRunnerManager_initializeFramework, _LfWorkflowRunnerManager_initializeLayout, _LfWorkflowRunnerManager_loadWorkflows, _LfWorkflowRunnerManager_subscribeToState;
class LfWorkflowRunnerManager {
  constructor() {
    _LfWorkflowRunnerManager_instances.add(this);
    _LfWorkflowRunnerManager_FRAMEWORK.set(this, getLfFramework());
    _LfWorkflowRunnerManager_STORE.set(this, void 0);
    _LfWorkflowRunnerManager_CLIENT.set(this, void 0);
    _LfWorkflowRunnerManager_APP_ROOT.set(this, void 0);
    _LfWorkflowRunnerManager_SECTIONS.set(this, void 0);
    _LfWorkflowRunnerManager_UI_REGISTRY.set(this, /* @__PURE__ */ new WeakMap());
    _LfWorkflowRunnerManager_DISPATCHERS.set(this, void 0);
    _LfWorkflowRunnerManager_ROUTING.set(this, void 0);
    _LfWorkflowRunnerManager_loadWorkflows.set(this, async () => {
      var _a;
      const { NO_WORKFLOWS_AVAILABLE } = NOTIFICATION_MESSAGES;
      const state2 = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
      const workflows = await fetchWorkflowDefinitions();
      if (!workflows || !Object.keys(workflows).length) {
        state2.mutate.notifications.add({
          id: performance.now().toString(),
          message: NO_WORKFLOWS_AVAILABLE,
          status: "danger"
        });
      }
      state2.mutate.workflows(workflows);
      const firstWorkflow = (_a = workflows.nodes) == null ? void 0 : _a[0];
      const route = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").getPendingRoute();
      const shouldSelectDefault = !route || !route.workflowId && (route.view === "workflow" || route.view === "history") || route.view === "run" && !route.workflowId;
      if (shouldSelectDefault && (firstWorkflow == null ? void 0 : firstWorkflow.id)) {
        state2.mutate.workflow(firstWorkflow.id);
      }
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").applyPendingRouteIfNeeded();
    });
    this.runs = {
      all: () => {
        return [...__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().runs];
      },
      get: (runId) => {
        const { runs } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
        return runs.find((run) => run.runId === runId) || null;
      },
      select: (runId, nextView) => {
        if (!nextView) {
          selectRun(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), runId);
          return;
        }
        if (nextView === "run" && runId) {
          const run = this.runs.get(runId);
          const state2 = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
          if ((run == null ? void 0 : run.workflowId) && run.workflowId !== state2.current.id) {
            state2.mutate.workflow(run.workflowId);
          }
          changeView(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), "run", {
            runId,
            clearResults: false
          });
          return;
        }
        changeView(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), nextView, {
          runId: nextView === "run" ? runId : null
        });
      },
      selected: () => {
        const { runs, selectedRunId } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
        if (!selectedRunId) {
          return null;
        }
        return runs.find((run) => run.runId === selectedRunId) || null;
      }
    };
    this.uiRegistry = {
      delete: () => {
        const elements = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_UI_REGISTRY, "f").get(this);
        if (elements) {
          for (const elementId in elements) {
            const element = elements[elementId];
            if (element && typeof element === "object" && "remove" in element) {
              element.remove();
            }
          }
        }
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_UI_REGISTRY, "f").delete(this);
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").destroy();
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_CLIENT, "f").stop();
      },
      get: () => {
        return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_UI_REGISTRY, "f").get(this);
      },
      remove: (elementId) => {
        const elements = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_UI_REGISTRY, "f").get(this);
        if (elements && elements[elementId]) {
          const element = elements[elementId];
          if (element && typeof element === "object" && "remove" in element) {
            element.remove();
          }
          delete elements[elementId];
          __classPrivateFieldGet(this, _LfWorkflowRunnerManager_UI_REGISTRY, "f").set(this, elements);
        }
      },
      set: (elementId, element) => {
        const elements = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_UI_REGISTRY, "f").get(this) || {};
        elements[elementId] = element;
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_UI_REGISTRY, "f").set(this, elements);
      }
    };
    this.workflow = {
      cells: (type) => {
        var _a;
        const workflow = this.workflow.current();
        const section = (_a = workflow == null ? void 0 : workflow.children) == null ? void 0 : _a.find((child) => child.id.endsWith(`:${type}s`));
        return (section == null ? void 0 : section.cells) || {};
      },
      current: () => {
        var _a;
        const { current, workflows } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
        return ((_a = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a.find((node) => node.id === current.id)) || null;
      },
      download: async (id) => {
        const { ERROR_FETCHING_WORKFLOWS: ERROR_FETCHING_WORKFLOWS2 } = STATUS_MESSAGES;
        const state2 = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
        id = id || state2.current.id;
        try {
          const workflowJSON = await fetchWorkflowJSON(id);
          const workflowString = JSON.stringify(workflowJSON, null, 2);
          const blob = new Blob([workflowString], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `${id}.json`;
          document.body.appendChild(a);
          a.click();
          setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          }, UI_CONSTANTS.DOWNLOAD_CLEANUP_DELAY_MS);
        } catch (error) {
          state2.mutate.status("error", ERROR_FETCHING_WORKFLOWS2);
          if (error instanceof WorkflowApiError) {
            addNotification(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), {
              id: performance.now().toString(),
              message: `Failed to fetch workflow: ${error.message}`,
              status: "danger"
            });
          }
        }
      },
      description: () => {
        const workflow = this.workflow.current();
        return (workflow == null ? void 0 : workflow.description) || "";
      },
      title: () => {
        const workflow = this.workflow.current();
        const str = typeof (workflow == null ? void 0 : workflow.value) === "string" ? workflow.value : String((workflow == null ? void 0 : workflow.value) || "");
        return str || "No workflow selected";
      }
    };
    const { ERROR_FETCHING_WORKFLOWS, IDLE_WORKFLOWS_LOADED, RUNNING_INITIALIZING, RUNNING_LOADING_WORKFLOWS } = STATUS_MESSAGES;
    const { WORKFLOWS_LOAD_FAILED } = NOTIFICATION_MESSAGES;
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_APP_ROOT, document.querySelector("#app"), "f");
    if (!__classPrivateFieldGet(this, _LfWorkflowRunnerManager_APP_ROOT, "f")) {
      const fallback = document.createElement("div");
      fallback.id = "app";
      if (document.body) {
        document.body.appendChild(fallback);
      }
      __classPrivateFieldSet(this, _LfWorkflowRunnerManager_APP_ROOT, fallback, "f");
    }
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_STORE, createWorkflowRunnerStore(initState()), "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_CLIENT, new WorkflowRunnerClient(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f")), "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_DISPATCHERS, {
      runWorkflow: () => workflowDispatcher(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"))
    }, "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_SECTIONS, {
      actionButton: createActionButtonSection(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f")),
      dev: createDevSection(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f")),
      drawer: createDrawerSection(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f")),
      header: createHeaderSection(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f")),
      main: createMainSection(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f")),
      notifications: createNotificationsSection(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"))
    }, "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_ROUTING, createRoutingController({ store: __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f") }), "f");
    const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
    state.mutate.manager(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").initialize();
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeFramework).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeLayout).call(this);
    state.mutate.status("running", RUNNING_INITIALIZING);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_subscribeToState).call(this);
    state.mutate.status("running", RUNNING_LOADING_WORKFLOWS);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_loadWorkflows, "f").call(this).catch((error) => {
      addNotification(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), {
        id: performance.now().toString(),
        message: error instanceof Error ? error.message : WORKFLOWS_LOAD_FAILED,
        status: "danger"
      });
      setStatus$1(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), "error", ERROR_FETCHING_WORKFLOWS);
    }).then(() => {
      setStatus$1(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), "idle", IDLE_WORKFLOWS_LOADED);
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").updateRouteFromState();
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_CLIENT, "f").start();
    });
  }
  //#endregion
  //#region Getters
  getAppRoot() {
    return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_APP_ROOT, "f");
  }
  getClient() {
    return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_CLIENT, "f");
  }
  getDispatchers() {
    return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_DISPATCHERS, "f");
  }
  getStore() {
    return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f");
  }
}
_LfWorkflowRunnerManager_FRAMEWORK = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_STORE = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_CLIENT = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_APP_ROOT = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_SECTIONS = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_UI_REGISTRY = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_DISPATCHERS = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_ROUTING = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_loadWorkflows = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_instances = /* @__PURE__ */ new WeakSet(), _LfWorkflowRunnerManager_initializeFramework = function _LfWorkflowRunnerManager_initializeFramework2() {
  const assetsUrl = buildAssetsUrl();
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_FRAMEWORK, "f").assets.set(assetsUrl);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_FRAMEWORK, "f").theme.set(DEFAULT_THEME);
}, _LfWorkflowRunnerManager_initializeLayout = function _LfWorkflowRunnerManager_initializeLayout2() {
  const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
  while (__classPrivateFieldGet(this, _LfWorkflowRunnerManager_APP_ROOT, "f").firstChild) {
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_APP_ROOT, "f").removeChild(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_APP_ROOT, "f").firstChild);
  }
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").actionButton.mount();
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").drawer.mount();
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").header.mount();
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").main.mount();
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").notifications.mount();
  if (state.isDebug) {
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").dev.mount();
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").dev.render();
  }
}, _LfWorkflowRunnerManager_subscribeToState = function _LfWorkflowRunnerManager_subscribeToState2() {
  var _a, _b, _c;
  const st = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
  let latestState = st;
  let lastCurrentMessage = st.current.message;
  let lastCurrentStatus = st.current.status;
  let lastDebug = st.isDebug;
  let lastId = st.current.id;
  let lastInputStatuses = st.inputStatuses;
  let lastNotificationsCount = ((_a = st.notifications) == null ? void 0 : _a.length) ?? 0;
  let lastQueued = st.queuedJobs ?? -1;
  let lastResults = st.results;
  let lastRunId = st.currentRunId;
  let lastRunsRef = st.runs;
  let lastSelectedRunId = st.selectedRunId;
  let lastView = st.view;
  let lastWorkflowsCount = ((_c = (_b = st.workflows) == null ? void 0 : _b.nodes) == null ? void 0 : _c.length) ?? 0;
  let scheduled = false;
  const needs = {
    header: false,
    dev: false,
    drawer: false,
    main: false,
    actionButton: false,
    notifications: false
  };
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").subscribe((state) => {
    var _a2, _b2;
    latestState = state;
    const { current, isDebug, queuedJobs, workflows } = state;
    const { message, status } = current;
    if (state.currentRunId !== lastRunId) {
      lastRunId = state.currentRunId;
    }
    if (current.id !== lastId) {
      needs.main = true;
      lastId = current.id;
    }
    if (state.results !== lastResults) {
      needs.main = true;
      lastResults = state.results;
    }
    if (state.runs !== lastRunsRef) {
      needs.main = true;
      lastRunsRef = state.runs;
    }
    if (state.selectedRunId !== lastSelectedRunId) {
      needs.main = true;
      lastSelectedRunId = state.selectedRunId;
    }
    if (state.view !== lastView) {
      needs.main = true;
      lastView = state.view;
    }
    if (state.inputStatuses !== lastInputStatuses) {
      needs.main = true;
      lastInputStatuses = state.inputStatuses;
    }
    if (message !== lastCurrentMessage || status !== lastCurrentStatus) {
      needs.actionButton = true;
      needs.header = true;
      lastCurrentMessage = message;
      lastCurrentStatus = status;
    }
    if (state.notifications.length !== lastNotificationsCount) {
      needs.notifications = true;
      lastNotificationsCount = state.notifications.length;
    }
    if (queuedJobs !== lastQueued) {
      needs.header = true;
      lastQueued = queuedJobs;
    }
    if (((_a2 = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a2.length) !== lastWorkflowsCount) {
      needs.drawer = true;
      lastWorkflowsCount = ((_b2 = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _b2.length) ?? 0;
    }
    if (isDebug !== lastDebug) {
      needs.dev = true;
      needs.drawer = true;
      lastDebug = isDebug;
    }
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(() => {
        scheduled = false;
        const stateSnapshot = latestState;
        const snapshotDebug = stateSnapshot.isDebug;
        const sections = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f");
        for (const sectionKey in needs) {
          const need = needs[sectionKey];
          const section = sections[sectionKey];
          if (need) {
            switch (sectionKey) {
              case "dev":
                if (snapshotDebug) {
                  section.mount();
                  section.render();
                } else {
                  section.destroy();
                }
                break;
              case "main":
                const mainSections = resolveMainSections(stateSnapshot);
                section.render(mainSections);
                break;
              default:
                section.render();
                break;
            }
          }
        }
        Object.keys(needs).forEach((k) => needs[k] = false);
      });
    }
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").updateRouteFromState();
  });
};
const bootstrapWorkflowRunner = () => {
  const hasComfyApp = typeof comfyAPI !== "undefined" && (comfyAPI == null ? void 0 : comfyAPI.api) && (comfyAPI == null ? void 0 : comfyAPI.app);
  if (hasComfyApp) {
    return null;
  }
  return new LfWorkflowRunnerManager();
};
bootstrapWorkflowRunner();
//# sourceMappingURL=workflow-runner.js.map
