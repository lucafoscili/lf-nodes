var _a, _b, _c;
import "../../js/lf-widgets-core-C1ol8nV-.js";
import { g as getLfFramework } from "../../js/lf-widgets-framework-B9H_1Mhq.js";
import "../../js/lf-widgets-foundations-BHCEI3uH.js";
const apiBase = "/api";
const apiRoutePrefix = "/lf-nodes";
const runtime = { "comfyUiProtocol": "http:", "comfyUiPort": 8188, "frontendProxyPort": 9188 };
const chat = { "provider": "kobold" };
const staticPaths = { "assets": "/lf-nodes/static/assets/" };
const theme$a = "dark";
const runnerConfig = {
  apiBase,
  apiRoutePrefix,
  runtime,
  chat,
  staticPaths,
  theme: theme$a
};
const API_BASE = runnerConfig.apiBase;
const API_ROUTE_PREFIX = runnerConfig.apiRoutePrefix;
const API_ROOT = `${API_BASE}${API_ROUTE_PREFIX}`;
const DEFAULT_COMFY_UI_PROTOCOL = String((_a = runnerConfig.runtime) == null ? void 0 : _a.comfyUiProtocol);
const DEFAULT_COMFY_UI_PORT = String((_b = runnerConfig.runtime) == null ? void 0 : _b.comfyUiPort);
const DEFAULT_FRONTEND_PROXY_PORT = String((_c = runnerConfig.runtime) == null ? void 0 : _c.frontendProxyPort);
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
  const activeRuns = state.runs.filter((run) => ACTIVE_STATUSES.has(run.status) && Boolean(run.submissionId));
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
  let elapsedTimer = null;
  const stopElapsedTimer = () => {
    if (elapsedTimer !== null) {
      clearTimeout(elapsedTimer);
      elapsedTimer = null;
    }
  };
  const destroy = () => {
    stopElapsedTimer();
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
    _root.lfLabel = "Run";
    _root.lfStyling = "floating";
    _root.title = "Run current workflow";
    _root.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(ACTION_BUTTON_CLASSES._, _root);
    debugLog(ACTION_BUTTON_MOUNTED);
  };
  const render = () => {
    var _a2, _b2, _c2, _d, _e, _f;
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const _root = elements[ACTION_BUTTON_CLASSES._];
    if (!_root) {
      return;
    }
    const activeRun = state.runs.find((run) => run.runId === state.currentRunId && ["pending", "running"].includes(run.status));
    const submissionBusy = Boolean(state.submissionInFlightId && !activeRun);
    const cancellationBusy = Boolean(activeRun && (state.cancelInFlightRunId === activeRun.runId || activeRun.cancelRequested));
    stopElapsedTimer();
    if (activeRun) {
      const elapsedSeconds = Math.max(0, Math.floor((Date.now() - activeRun.createdAt) / 1e3));
      _root.dataset.mode = cancellationBusy ? "stopping" : "stop";
      _root.lfAriaLabel = cancellationBusy ? "Stopping current workflow run" : "Stop current workflow run";
      _root.lfIcon = "x";
      _root.lfLabel = cancellationBusy ? `Stopping · ${elapsedSeconds}s` : `Stop · ${elapsedSeconds}s`;
      _root.lfShowSpinner = true;
      _root.lfUiState = cancellationBusy || !activeRun.submissionId ? "disabled" : "danger";
      _root.title = cancellationBusy ? `Cancellation requested for ${activeRun.runId}` : `Stop ${activeRun.status} run ${activeRun.runId}`;
      if (typeof _root.setAttribute === "function") {
        _root.setAttribute("aria-busy", "true");
      }
      elapsedTimer = setTimeout(render, 1e3);
    } else if (submissionBusy) {
      _root.dataset.mode = "starting";
      _root.lfAriaLabel = "Starting workflow run";
      _root.lfIcon = "send";
      _root.lfLabel = "Starting…";
      _root.lfShowSpinner = true;
      _root.lfUiState = "disabled";
      _root.title = `Submitting ${state.submissionInFlightId}`;
      if (typeof _root.setAttribute === "function") {
        _root.setAttribute("aria-busy", "true");
      }
    } else {
      const workflow = (_b2 = (_a2 = manager.workflow) == null ? void 0 : _a2.current) == null ? void 0 : _b2.call(_a2);
      const setupRequired = ((_c2 = workflow == null ? void 0 : workflow.readiness) == null ? void 0 : _c2.status) === "setup_required";
      const setupMessage = (_f = (_e = (_d = workflow == null ? void 0 : workflow.readiness) == null ? void 0 : _d.issues) == null ? void 0 : _e[0]) == null ? void 0 : _f.message;
      _root.dataset.mode = setupRequired ? "setup-required" : "run";
      _root.lfAriaLabel = setupRequired ? "Workflow setup required" : "Run current workflow";
      _root.lfIcon = setupRequired ? theme$9.get.icon("alertTriangle") : "send";
      _root.lfLabel = setupRequired ? "Setup required" : "Run";
      _root.lfShowSpinner = false;
      _root.lfUiState = state.current.id && !setupRequired ? "primary" : "disabled";
      _root.title = setupRequired ? setupMessage || "Install the required workflow dependencies before running." : "Run current workflow";
      if (typeof _root.removeAttribute === "function") {
        _root.removeAttribute("aria-busy");
      }
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
  var _a2;
  const { article, folderOpen, lfSignature, listTree } = getLfFramework().theme.get.icons();
  const fallback = folderOpen || article || listTree || lfSignature;
  const shippedCategories = [];
  const customCollections = [];
  const home = { icon: article || fallback, id: "home", value: "Home" };
  const shipped = {
    icon: lfSignature || fallback,
    id: "workflows:shipped",
    value: "LF Nodes",
    children: shippedCategories
  };
  const custom = {
    icon: folderOpen || fallback,
    id: "workflows:custom",
    value: "Custom",
    children: customCollections
  };
  const roots = [];
  const wfs = { icon: listTree || fallback, id: "workflows", value: "Workflows", children: roots };
  const clone = JSON.parse(JSON.stringify(workflows));
  (_a2 = clone.nodes) == null ? void 0 : _a2.forEach((node) => {
    var _a3, _b2, _c2, _d, _e;
    node.children = void 0;
    const issue = (_c2 = (_b2 = (_a3 = node.readiness) == null ? void 0 : _a3.issues) == null ? void 0 : _b2[0]) == null ? void 0 : _c2.message;
    if (((_d = node.readiness) == null ? void 0 : _d.status) === "setup_required") {
      node.icon = getLfFramework().theme.get.icon("alertTriangle");
      node.description = `Setup required${issue ? `: ${issue}` : "."}`;
    } else if (((_e = node.readiness) == null ? void 0 : _e.status) === "warning") {
      node.icon = getLfFramework().theme.get.icon("hexagonInfo");
      node.description = `Check setup${issue ? `: ${issue}` : "."}`;
    }
    const isCustom = node.origin !== "shipped";
    const name = isCustom ? node.collection || "Custom" : node.category || "Uncategorized";
    const groups = isCustom ? customCollections : shippedCategories;
    let group = groups.find((item) => item.value === name);
    if (!group) {
      group = {
        icon: isCustom ? _getIcon("Custom") : _getIcon(name),
        id: `${isCustom ? "custom" : "shipped"}:${name}`,
        value: name,
        children: []
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
  const dataset = {
    nodes: [home, wfs]
  };
  return dataset;
};
const _getIcon = (category) => {
  const { ai, codeCircle2, folder, folderOpen, json, music, photo, robot, wand } = getLfFramework().theme.get.icons();
  const fallback = folder || folderOpen || photo;
  const category_icons = {
    Audio: music,
    Custom: folderOpen,
    "Image Processing": wand,
    JSON: json,
    "Krea 2": ai,
    "MiniMax H3": ai,
    "TRELLIS.2": ai,
    TripoSplat: ai,
    LLM: robot,
    "Media Intake": folderOpen,
    SVG: codeCircle2,
    "Text to Image": photo
  };
  return category_icons[category] || fallback;
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
const artifactViewUrl = (artifact) => {
  const params = new URLSearchParams({
    filename: artifact.filename,
    subfolder: (artifact.subfolder || "").replaceAll("\\", "/"),
    type: artifact.type || "output"
  });
  return `/view?${params.toString()}`;
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
  compare: (props) => {
    const comp = document.createElement("lf-compare");
    comp.className = "workflow-output-compare";
    _setProps("LfCompare", comp, props);
    return comp;
  },
  select: (props) => {
    const comp = document.createElement("lf-select");
    _setProps("LfSelect", comp, props);
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
    case "choice":
    case "select": {
      const p = props || {};
      return createComponent.select(sanitizeProps(p, "LfSelect"));
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
const _outputRelativeArtifact = (value) => {
  if (typeof value !== "string" || !value || value.includes("\\")) {
    return null;
  }
  const parts = value.split("/");
  if (parts.some((part) => !part || part === "." || part === "..") || !parts.every((part) => /^[^\\/:\x00-\x1F\x7F]+$/.test(part))) {
    return null;
  }
  const filename = parts.pop();
  if (!filename) {
    return null;
  }
  return {
    filename,
    subfolder: parts.join("/"),
    type: "output"
  };
};
const _fileNameArtifacts = (fileNames) => Array.isArray(fileNames) ? fileNames.map(_outputRelativeArtifact).filter((artifact) => artifact !== null) : [];
const _isBrowserImage = (artifact, mediaType) => /^(?:image\/(?:png|jpe?g|gif|webp|avif|apng|svg\+xml))$/.test(mediaType) || /\.(?:png|jpe?g|gif|webp|avif|apng|svg)$/i.test(artifact.filename);
const _mediaOutput = (artifacts) => {
  var _a2;
  if (!Array.isArray(artifacts) || artifacts.length === 0) {
    return null;
  }
  const media = document.createElement("div");
  media.className = "workflow-output-media";
  for (const artifact of artifacts) {
    if (!(artifact == null ? void 0 : artifact.filename)) {
      continue;
    }
    const item = document.createElement("figure");
    item.className = "workflow-output-media__item";
    const src = artifactViewUrl(artifact);
    const mediaType = ((_a2 = artifact.media_type) == null ? void 0 : _a2.toLowerCase()) || "";
    const isAudio = mediaType.startsWith("audio/") || /\.(?:wav|mp3|m4a|flac|ogg|opus)$/i.test(artifact.filename);
    const isVideo = mediaType.startsWith("video/") || /\.(?:mp4|webm)$/i.test(artifact.filename);
    const isBrowserImage = _isBrowserImage(artifact, mediaType);
    if (isAudio) {
      const audio = document.createElement("audio");
      audio.className = "workflow-output-media__preview";
      audio.controls = true;
      audio.preload = "metadata";
      audio.src = src;
      item.appendChild(audio);
    } else if (isVideo) {
      const video = document.createElement("video");
      video.className = "workflow-output-media__preview";
      video.controls = true;
      video.playsInline = true;
      video.preload = "metadata";
      video.src = src;
      item.appendChild(video);
    } else if (isBrowserImage) {
      const image = document.createElement("img");
      image.alt = artifact.filename;
      image.className = "workflow-output-media__preview";
      image.loading = "lazy";
      image.src = src;
      item.appendChild(image);
    } else {
      const note = document.createElement("span");
      note.className = "workflow-output-media__note";
      note.textContent = "Preview is not available in the browser.";
      item.appendChild(note);
    }
    const link = document.createElement("a");
    link.className = "workflow-output-media__link";
    link.href = src;
    if (!isAudio && !isVideo && !isBrowserImage) {
      link.download = artifact.filename;
    }
    link.rel = "noopener";
    link.target = "_blank";
    link.textContent = !isAudio && !isVideo && !isBrowserImage ? `Download ${artifact.filename}` : artifact.filename;
    item.appendChild(link);
    media.appendChild(item);
  }
  return media.childElementCount > 0 ? media : null;
};
const createOutputComponent = (descriptor) => {
  const { syntax } = getLfFramework();
  const modelArtifacts = descriptor["3d"];
  const { civitai_metadata, dataset, audio, file_names, audios, images, json, metadata, props, shape, slot_map, string, svg } = descriptor;
  const el = document.createElement("div");
  const standardArtifacts = [
    ...images || [],
    ...audio || [],
    ...audios || [],
    ...modelArtifacts || []
  ];
  const media = _mediaOutput(standardArtifacts.length > 0 ? standardArtifacts : _fileNameArtifacts(file_names));
  if (media) {
    el.appendChild(media);
    const hasLegacyPayload = shape === "masonry" ? dataset !== void 0 && dataset !== null : Boolean(string || svg || civitai_metadata || (file_names == null ? void 0 : file_names.length) || json || metadata || dataset);
    if (!hasLegacyPayload) {
      return el;
    }
  }
  switch (shape) {
    case "compare": {
      const p = props || {};
      p.lfDataset = dataset || json || { nodes: [] };
      p.lfShape || (p.lfShape = "image");
      const compare = createComponent.compare(p);
      el.appendChild(compare);
      break;
    }
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
    const { current, manager, queuedJobs, currentRunId, runs } = store.getState();
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
        const run = runs.find((entry) => entry.runId === currentRunId);
        const prefix = currentRunId.slice(0, 8);
        const submission = (run == null ? void 0 : run.submissionId) ? ` · ${run.submissionId.slice(0, 16)}` : "";
        const activity = (run == null ? void 0 : run.cancelRequested) ? "Stopping" : (run == null ? void 0 : run.status) === "pending" ? "Queued" : "Running";
        displayMessage = `${activity} ${prefix}${submission}`;
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
  var _a2, _b2, _c2;
  const prep = [];
  for (const id in defs) {
    const cell = defs[id];
    const { nodeId } = cell;
    const result = ((_b2 = (_a2 = outs == null ? void 0 : outs[nodeId]) == null ? void 0 : _a2.lf_output) == null ? void 0 : _b2[0]) || ((_c2 = outs == null ? void 0 : outs[nodeId]) == null ? void 0 : _c2[0]) || (outs == null ? void 0 : outs[nodeId]);
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
  if (!Number.isFinite(n) || Number.isNaN(n) || n < 0) {
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
  var _a2, _b2, _c2;
  const { artifacts, cancel_requested, created_at, error, inputs, result, run_id, status, submission_id, updated_at, workflow_id } = rec;
  const hasResult = rec.result !== void 0;
  const resultOutputs = ((_c2 = (_b2 = (_a2 = result == null ? void 0 : result.body) == null ? void 0 : _a2.payload) == null ? void 0 : _b2.history) == null ? void 0 : _c2.outputs) || null;
  const outputs = resultOutputs ?? (rec.outputs !== void 0 ? rec.outputs : hasResult ? null : void 0);
  const createdAt = normalizeTimestamp(created_at, 0);
  const updatedAt = normalizeTimestamp(updated_at, createdAt);
  const map = {
    runId: run_id,
    ...artifacts !== void 0 ? { artifacts } : {},
    ...submission_id !== void 0 ? { submissionId: submission_id } : {},
    ...cancel_requested !== void 0 ? { cancelRequested: cancel_requested } : {},
    status,
    createdAt,
    updatedAt,
    workflowId: workflow_id ?? null,
    workflowName: workflow_id && wfs[workflow_id] || "Unknown workflow",
    error: error ?? null,
    httpStatus: hasResult ? (result == null ? void 0 : result.http_status) ?? null : void 0,
    resultPayload: hasResult ? result ?? null : void 0,
    outputs,
    // Summary/SSE records intentionally omit input snapshots. Keep the
    // browser's just-submitted values until an explicit detail response
    // supplies the durable snapshot.
    inputs: inputs === void 0 ? void 0 : inputs ?? {}
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
const pendingHandoffs = /* @__PURE__ */ new WeakMap();
const acceptsArtifact = (cell, artifact) => {
  var _a2;
  const html = (_a2 = cell.props) == null ? void 0 : _a2.lfHtmlAttributes;
  const accept = typeof (html == null ? void 0 : html.accept) === "string" ? html.accept.trim().toLowerCase() : "";
  if (!accept) {
    return true;
  }
  const filename = artifact.filename.toLowerCase();
  const mediaType = (artifact.mediaType || "").toLowerCase();
  return accept.split(",").some((rawRule) => {
    const rule = rawRule.trim();
    if (!rule) {
      return false;
    }
    if (rule.startsWith(".")) {
      return filename.endsWith(rule);
    }
    if (rule.endsWith("/*")) {
      return mediaType.startsWith(rule.slice(0, -1));
    }
    return Boolean(mediaType) && mediaType === rule;
  });
};
const listCompatibleArtifactTargets = (workflows, artifact) => {
  var _a2, _b2;
  if (!artifact.available) {
    return [];
  }
  const targets = [];
  for (const workflow of workflows.nodes || []) {
    if (((_a2 = workflow.readiness) == null ? void 0 : _a2.status) === "setup_required") {
      continue;
    }
    const inputGroup = (_b2 = workflow.children) == null ? void 0 : _b2.find((child) => child == null ? void 0 : child.id.endsWith(":inputs"));
    const cells = (inputGroup == null ? void 0 : inputGroup.cells) || {};
    for (const inputId of Object.keys(cells)) {
      const cell = cells[inputId];
      if (!cell || cell.shape !== "upload" || !acceptsArtifact(cell, artifact)) {
        continue;
      }
      targets.push({
        workflowId: workflow.id,
        workflowName: String(workflow.value || workflow.id),
        inputId,
        inputName: String(cell.value || cell.title || inputId)
      });
    }
  }
  return targets.sort((a, b) => {
    const workflowOrder = a.workflowName.localeCompare(b.workflowName);
    return workflowOrder || a.inputName.localeCompare(b.inputName);
  });
};
const buildArtifactPrefill = (artifact) => ({
  schema: "lf.workflow-upload-prefill.v1",
  reference: { ...artifact.reference },
  names: [artifact.filename],
  available: artifact.available
});
const queueArtifactHandoff = (store, artifact, target) => {
  if (!artifact.available || !target.workflowId || !target.inputId) {
    return;
  }
  pendingHandoffs.set(store, {
    workflowId: target.workflowId,
    inputs: { [target.inputId]: buildArtifactPrefill(artifact) }
  });
  const state = store.getState();
  if (state.current.id !== target.workflowId) {
    state.mutate.workflow(target.workflowId);
  }
  changeView(store, "workflow", { clearResults: true });
};
const consumeArtifactHandoff = (store, workflowId) => {
  const pending = pendingHandoffs.get(store);
  if (!pending || !workflowId || pending.workflowId !== workflowId) {
    return null;
  }
  pendingHandoffs.delete(store);
  return pending.inputs;
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
  handoff: theme$6.bemClass(ROOT_CLASS$6, "handoff"),
  handoffArtifact: theme$6.bemClass(ROOT_CLASS$6, "handoff-artifact"),
  handoffCancel: theme$6.bemClass(ROOT_CLASS$6, "handoff-cancel"),
  handoffDestination: theme$6.bemClass(ROOT_CLASS$6, "handoff-destination"),
  handoffSubmit: theme$6.bemClass(ROOT_CLASS$6, "handoff-submit"),
  remix: theme$6.bemClass(ROOT_CLASS$6, "remix"),
  item: theme$6.bemClass(ROOT_CLASS$6, "item"),
  results: theme$6.bemClass(ROOT_CLASS$6, "results"),
  subtitle: theme$6.bemClass(ROOT_CLASS$6, "subtitle"),
  title: theme$6.bemClass(ROOT_CLASS$6, "title"),
  useOutput: theme$6.bemClass(ROOT_CLASS$6, "use-output")
};
const _formatDescription = (selectedRun, description) => {
  if (!selectedRun) {
    return description;
  }
  const timestamp = selectedRun.updatedAt || selectedRun.createdAt;
  const submission = selectedRun.submissionId ? ` · Submission ${selectedRun.submissionId}` : "";
  return `Run ${selectedRun.runId.slice(0, 8)}${submission} · ${formatStatus(selectedRun.status)} · ${formatTimestamp(timestamp)}`;
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
  const { arrowBack, folder, refresh } = theme$6.get.icons();
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
  const remixButton = document.createElement("lf-button");
  remixButton.className = RESULTS_CLASSES.remix;
  remixButton.lfIcon = refresh;
  remixButton.lfLabel = "Remix";
  remixButton.lfStyling = "flat";
  remixButton.lfUiSize = "small";
  remixButton.lfUiState = "disabled";
  remixButton.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  const useOutputButton = document.createElement("lf-button");
  useOutputButton.className = RESULTS_CLASSES.useOutput;
  useOutputButton.lfIcon = refresh;
  useOutputButton.lfLabel = "Use in…";
  useOutputButton.lfStyling = "flat";
  useOutputButton.lfUiSize = "small";
  useOutputButton.lfUiState = "disabled";
  title.appendChild(h3);
  title.appendChild(actions);
  actions.appendChild(backButton);
  actions.appendChild(remixButton);
  actions.appendChild(useOutputButton);
  actions.appendChild(historyButton);
  return {
    actions,
    backButton,
    h3,
    historyButton,
    remixButton,
    title,
    useOutputButton
  };
};
const _handoff = () => {
  const root = document.createElement("section");
  root.className = RESULTS_CLASSES.handoff;
  root.hidden = true;
  const heading = document.createElement("h4");
  heading.textContent = "Use a saved output as an input";
  const description = document.createElement("p");
  description.textContent = "Choose an output and destination. Runner keeps an opaque link to the saved artifact; no re-upload is needed.";
  const artifactLabel = document.createElement("label");
  artifactLabel.textContent = "Output";
  const artifact = document.createElement("select");
  artifact.className = RESULTS_CLASSES.handoffArtifact;
  artifactLabel.appendChild(artifact);
  const destinationLabel = document.createElement("label");
  destinationLabel.textContent = "Destination";
  const destination = document.createElement("select");
  destination.className = RESULTS_CLASSES.handoffDestination;
  destinationLabel.appendChild(destination);
  const controls = document.createElement("div");
  const submit = document.createElement("lf-button");
  submit.className = RESULTS_CLASSES.handoffSubmit;
  submit.lfLabel = "Continue";
  submit.lfUiState = "primary";
  submit.lfUiSize = "small";
  const cancel = document.createElement("lf-button");
  cancel.className = RESULTS_CLASSES.handoffCancel;
  cancel.lfLabel = "Cancel";
  cancel.lfStyling = "flat";
  cancel.lfUiSize = "small";
  controls.appendChild(submit);
  controls.appendChild(cancel);
  root.appendChild(heading);
  root.appendChild(description);
  root.appendChild(artifactLabel);
  root.appendChild(destinationLabel);
  root.appendChild(controls);
  return { artifact, cancel, destination, root, submit };
};
const createResultsSection = (store) => {
  const { WORKFLOW_RESULTS_DESTROYED, WORKFLOW_RESULTS_MOUNTED, WORKFLOW_RESULTS_UPDATED } = DEBUG_MESSAGES;
  let renderedContent = null;
  let handoffArtifacts = [];
  let handoffTargets = [];
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in RESULTS_CLASSES) {
      const element = RESULTS_CLASSES[cls];
      uiRegistry.remove(element);
    }
    renderedContent = null;
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
    const { actions, backButton, h3, historyButton, remixButton, title, useOutputButton } = _title$3(store);
    const handoff = _handoff();
    const updateDestinations = () => {
      const previousTarget = handoffTargets[Number(handoff.destination.value) || 0];
      const artifact = handoffArtifacts[Number(handoff.artifact.value) || 0];
      handoffTargets = artifact ? listCompatibleArtifactTargets(store.getState().workflows, artifact) : [];
      handoff.destination.replaceChildren(...handoffTargets.map((target, index) => {
        const option = document.createElement("option");
        option.value = String(index);
        option.textContent = `${target.workflowName} — ${target.inputName}`;
        return option;
      }));
      const preservedTarget = previousTarget ? handoffTargets.findIndex((target) => target.workflowId === previousTarget.workflowId && target.inputId === previousTarget.inputId) : -1;
      handoff.destination.value = String(Math.max(0, preservedTarget));
      handoff.submit.lfUiState = handoffTargets.length ? "primary" : "disabled";
    };
    handoff.artifact.addEventListener("change", updateDestinations);
    useOutputButton.addEventListener("lf-button-event", (event) => {
      var _a2;
      if (((_a2 = event.detail) == null ? void 0 : _a2.eventType) !== "click") {
        return;
      }
      handoff.root.hidden = !handoff.root.hidden;
      if (!handoff.root.hidden) {
        updateDestinations();
        handoff.artifact.focus();
      }
    });
    handoff.cancel.addEventListener("lf-button-event", (event) => {
      var _a2;
      if (((_a2 = event.detail) == null ? void 0 : _a2.eventType) === "click") {
        handoff.root.hidden = true;
        useOutputButton.focus();
      }
    });
    handoff.submit.addEventListener("lf-button-event", (event) => {
      var _a2;
      if (((_a2 = event.detail) == null ? void 0 : _a2.eventType) !== "click") {
        return;
      }
      const artifact = handoffArtifacts[Number(handoff.artifact.value) || 0];
      const target = handoffTargets[Number(handoff.destination.value) || 0];
      if (artifact && target) {
        queueArtifactHandoff(store, artifact, target);
      }
    });
    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(handoff.root);
    _root.appendChild(results);
    elements[MAIN_CLASSES._].prepend(_root);
    uiRegistry.set(RESULTS_CLASSES._, _root);
    uiRegistry.set(RESULTS_CLASSES.actions, actions);
    uiRegistry.set(RESULTS_CLASSES.back, backButton);
    uiRegistry.set(RESULTS_CLASSES.description, description);
    uiRegistry.set(RESULTS_CLASSES.h3, h3);
    uiRegistry.set(RESULTS_CLASSES.history, historyButton);
    uiRegistry.set(RESULTS_CLASSES.handoff, handoff.root);
    uiRegistry.set(RESULTS_CLASSES.handoffArtifact, handoff.artifact);
    uiRegistry.set(RESULTS_CLASSES.handoffCancel, handoff.cancel);
    uiRegistry.set(RESULTS_CLASSES.handoffDestination, handoff.destination);
    uiRegistry.set(RESULTS_CLASSES.handoffSubmit, handoff.submit);
    uiRegistry.set(RESULTS_CLASSES.remix, remixButton);
    uiRegistry.set(RESULTS_CLASSES.results, results);
    uiRegistry.set(RESULTS_CLASSES.title, title);
    uiRegistry.set(RESULTS_CLASSES.useOutput, useOutputButton);
    debugLog(WORKFLOW_RESULTS_MOUNTED);
  };
  const render = () => {
    var _a2, _b2, _c2, _d;
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
    const handoff = elements[RESULTS_CLASSES.handoff];
    const handoffArtifact = elements[RESULTS_CLASSES.handoffArtifact];
    const remixButton = elements[RESULTS_CLASSES.remix];
    const useOutputButton = elements[RESULTS_CLASSES.useOutput];
    descr.textContent = _formatDescription(selectedRun, manager.workflow.description());
    h3.textContent = (selectedRun == null ? void 0 : selectedRun.workflowName) || manager.workflow.title();
    backButton.lfUiState = selectedRun ? "primary" : "disabled";
    historyButton.lfUiState = runs.length > 0 ? "primary" : "disabled";
    const workflowAvailable = Boolean((selectedRun == null ? void 0 : selectedRun.workflowId) && ((_b2 = (_a2 = state.workflows) == null ? void 0 : _a2.nodes) == null ? void 0 : _b2.some((node) => node.id === selectedRun.workflowId)));
    if (remixButton) {
      remixButton.lfUiState = selectedRun && workflowAvailable && Object.keys(selectedRun.inputs || {}).length > 0 ? "primary" : "disabled";
    }
    const artifacts = ((selectedRun == null ? void 0 : selectedRun.artifacts) || []).filter((artifact) => {
      var _a3;
      return Boolean(artifact && artifact.schema === "lf.workflow-artifact.v1" && ((_a3 = artifact.reference) == null ? void 0 : _a3.schema) === "lf.workflow-artifact-ref.v1" && artifact.filename);
    }).sort((a, b) => Number(b.available) - Number(a.available));
    const hasUsableArtifact = artifacts.some((artifact) => artifact.available && listCompatibleArtifactTargets(state.workflows, artifact).length > 0);
    if (useOutputButton) {
      useOutputButton.lfUiState = hasUsableArtifact ? "primary" : "disabled";
      useOutputButton.hidden = (selectedRun == null ? void 0 : selectedRun.status) !== "succeeded" || artifacts.length === 0;
      useOutputButton.title = hasUsableArtifact ? "Use a saved output in another workflow" : artifacts.some((artifact) => artifact.available) ? "No ready workflow accepts this output type" : "Saved outputs are no longer available on disk";
    }
    if (handoff && handoffArtifact) {
      if ((renderedContent == null ? void 0 : renderedContent.runId) !== (selectedRun == null ? void 0 : selectedRun.runId) || !hasUsableArtifact) {
        handoff.hidden = true;
      }
      const previousArtifactId = (_c2 = handoffArtifacts[Number(handoffArtifact.value) || 0]) == null ? void 0 : _c2.reference.artifactId;
      handoffArtifacts = artifacts;
      const nameCounts = artifacts.reduce((counts, artifact) => {
        counts.set(artifact.filename, (counts.get(artifact.filename) || 0) + 1);
        return counts;
      }, /* @__PURE__ */ new Map());
      handoffArtifact.replaceChildren(...artifacts.map((artifact, index) => {
        const option = document.createElement("option");
        option.value = String(index);
        option.disabled = !artifact.available || listCompatibleArtifactTargets(state.workflows, artifact).length === 0;
        const source = (nameCounts.get(artifact.filename) || 0) > 1 ? ` · node ${artifact.nodeId || "unknown"}` : "";
        const unavailable = artifact.available ? "" : " · file no longer on disk";
        option.textContent = `${artifact.filename}${source}${unavailable}`;
        return option;
      }));
      const firstUsable = artifacts.findIndex((artifact) => artifact.available && listCompatibleArtifactTargets(state.workflows, artifact).length > 0);
      const preservedArtifact = previousArtifactId ? artifacts.findIndex((artifact) => artifact.reference.artifactId === previousArtifactId && artifact.available && listCompatibleArtifactTargets(state.workflows, artifact).length > 0) : -1;
      handoffArtifact.value = String(Math.max(0, preservedArtifact >= 0 ? preservedArtifact : firstUsable));
      handoffArtifact.dispatchEvent(new Event("change"));
    }
    const outputs = state.results ?? (selectedRun == null ? void 0 : selectedRun.outputs) ?? null;
    const nextContent = {
      element,
      error: (selectedRun == null ? void 0 : selectedRun.error) ?? null,
      outputs,
      resultPayload: (selectedRun == null ? void 0 : selectedRun.resultPayload) ?? null,
      runId: (selectedRun == null ? void 0 : selectedRun.runId) ?? null
    };
    if ((renderedContent == null ? void 0 : renderedContent.element) === nextContent.element && renderedContent.error === nextContent.error && renderedContent.outputs === nextContent.outputs && renderedContent.resultPayload === nextContent.resultPayload && renderedContent.runId === nextContent.runId) {
      return;
    }
    renderedContent = nextContent;
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
      appendCodeBlock("Run payload", stringifyDetail(((_d = selectedRun == null ? void 0 : selectedRun.resultPayload) == null ? void 0 : _d.body) ?? (selectedRun == null ? void 0 : selectedRun.resultPayload) ?? null));
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
  var _a2;
  const { workflows } = store.getState();
  const clone = JSON.parse(JSON.stringify(workflows));
  const root = { cells: {}, id: "root", value: "Workflows" };
  (_a2 = clone.nodes) == null ? void 0 : _a2.forEach((node) => {
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
  var _a2, _b2, _c2, _d, _e, _f, _g;
  const { comp, originalEvent } = e.detail;
  const ogEvent = originalEvent;
  const { manager, mutate } = store.getState();
  if (comp.rootElement.className === OUTPUTS_CLASSES.masonry) {
    switch ((_a2 = ogEvent == null ? void 0 : ogEvent.detail) == null ? void 0 : _a2.eventType) {
      case "click":
        const card = ogEvent.detail.comp;
        const node = (_c2 = (_b2 = card.lfDataset) == null ? void 0 : _b2.nodes) == null ? void 0 : _c2[0];
        const isValidCard = (node == null ? void 0 : node.id) && card.rootElement.tagName.toLowerCase() === "lf-card";
        if (isValidCard) {
          const { id } = node;
          if (manager.runs.get(id) && ((_d = manager.runs.selected()) == null ? void 0 : _d.runId) !== id) {
            manager.runs.select(id, "run");
          }
        }
        break;
      default:
        return;
    }
  }
  if (comp.rootElement.className === HOME_CLASSES.masonry) {
    switch ((_e = ogEvent == null ? void 0 : ogEvent.detail) == null ? void 0 : _e.eventType) {
      case "click":
        const card = ogEvent.detail.comp;
        const node = (_g = (_f = card.lfDataset) == null ? void 0 : _f.nodes) == null ? void 0 : _g[0];
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
const masonryClickFallback = (e, store) => {
  var _a2, _b2, _c2;
  const card = e.composedPath().find((entry) => entry instanceof Element && entry.tagName.toLowerCase() === "lf-card");
  const node = (_b2 = (_a2 = card == null ? void 0 : card.lfDataset) == null ? void 0 : _a2.nodes) == null ? void 0 : _b2[0];
  const runId = typeof (node == null ? void 0 : node.id) === "string" ? node.id : "";
  if (!runId) {
    return;
  }
  const { manager } = store.getState();
  if (manager.runs.get(runId) && ((_c2 = manager.runs.selected()) == null ? void 0 : _c2.runId) !== runId) {
    manager.runs.select(runId, "run");
  }
};
const { theme: theme$3 } = getLfFramework();
const ROOT_CLASS$3 = "outputs-section";
const OUTPUTS_CLASSES = {
  _: theme$3.bemClass(ROOT_CLASS$3),
  cleanup: theme$3.bemClass(ROOT_CLASS$3, "cleanup"),
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
      const value = cell.value || cell.lfValue;
      if (shape === "image" && typeof value === "string" && value) {
        return value;
      }
    }
  }
  return null;
};
const _isBrowserPreviewPath = (value) => /\.(?:png|jpe?g|gif|webp|avif|apng|svg)(?:$|[?#])/i.test(value);
const _isTemporaryMedia = (value, explicitType) => {
  if (explicitType === "temp") {
    return true;
  }
  if (!value.startsWith("/view?")) {
    return false;
  }
  try {
    return new URLSearchParams(value.slice(value.indexOf("?") + 1)).get("type") === "temp";
  } catch {
    return false;
  }
};
const getFirstOutputMediaUrl = (outputs) => {
  if (!outputs) {
    return "";
  }
  const tryPayload = (payload, allowTemporary) => {
    if (!payload || typeof payload !== "object") {
      return { image: null, fallback: null };
    }
    const { code: codeIcon, forms: stringIcon, json: jsonIcon, photoX: fallback } = theme$3.get.icons();
    let foundImage = null;
    let fallbackCandidate = null;
    const artifacts = [
      ...payload.images || [],
      ...payload.audio || [],
      ...payload.audios || [],
      ...payload["3d"] || []
    ];
    if (artifacts.length) {
      const artifact = artifacts.find((item) => {
        if (!item || !item.url && !item.filename) {
          return false;
        }
        const previewPath = typeof item.filename === "string" && item.filename ? item.filename : item.url || "";
        if (!_isBrowserPreviewPath(previewPath)) {
          return false;
        }
        const value = typeof item.url === "string" ? item.url : item.filename || "";
        return allowTemporary || !_isTemporaryMedia(value, item.type);
      });
      if (artifact) {
        if (typeof artifact.filename === "string" && artifact.filename) {
          return {
            image: artifactViewUrl({
              filename: artifact.filename,
              subfolder: artifact.subfolder,
              type: artifact.type,
              url: artifact.url
            }),
            fallback: null
          };
        }
      }
    }
    if (Array.isArray(payload.lf_output)) {
      for (const entry of payload.lf_output) {
        const { dataset: dataset2, file_names, json, metadata, string, svg } = entry;
        const image2 = _extractImageFromDataset(dataset2) ?? _extractImageFromDataset(json) ?? (file_names == null ? void 0 : file_names.find((name) => typeof name === "string" && name && _isBrowserPreviewPath(name))) ?? null;
        if (image2 && (allowTemporary || !_isTemporaryMedia(image2))) {
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
    if (fromDataset && (allowTemporary || !_isTemporaryMedia(fromDataset))) {
      return { image: fromDataset, fallback: null };
    }
    const fileNames = payload.file_names;
    if (Array.isArray(fileNames)) {
      const fileName = fileNames.find((name) => typeof name === "string" && name && _isBrowserPreviewPath(name));
      if (fileName && (allowTemporary || !_isTemporaryMedia(fileName))) {
        return { image: fileName, fallback: null };
      }
    }
    const image = payload.image;
    if (typeof image === "string" && image && (allowTemporary || !_isTemporaryMedia(image))) {
      return { image, fallback: null };
    }
    return { image: null, fallback: fallbackCandidate ?? fallback };
  };
  let fallbackImage = null;
  for (const allowTemporary of [false, true]) {
    for (const nodeId in outputs) {
      if (!Object.prototype.hasOwnProperty.call(outputs, nodeId)) {
        continue;
      }
      const payload = outputs[nodeId];
      const { image, fallback: candidate } = tryPayload(payload, allowTemporary);
      if (image) {
        return image;
      }
      if (!fallbackImage && candidate) {
        fallbackImage = candidate;
      }
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
    case "timeout":
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
    case "timeout":
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
      value: getFirstOutputMediaUrl(run.outputs)
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
  masonry.addEventListener("click", (e) => masonryClickFallback(e, store));
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
  const cleanup = document.createElement("lf-button");
  cleanup.className = OUTPUTS_CLASSES.cleanup;
  cleanup.lfAriaLabel = "Remove stale Runner history entries";
  cleanup.lfLabel = "Remove missing";
  cleanup.lfStyling = "flat";
  cleanup.lfUiSize = "small";
  cleanup.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  title.appendChild(h4);
  title.appendChild(controls);
  controls.appendChild(cleanup);
  controls.appendChild(toggle);
  return { cleanup, h4, title, controls, toggle };
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
    const { cleanup, controls, h4, title, toggle } = _title$1(store);
    const masonry = _masonry(store);
    _root.appendChild(title);
    _root.appendChild(masonry);
    elements[MAIN_CLASSES._].appendChild(_root);
    uiRegistry.set(OUTPUTS_CLASSES._, _root);
    uiRegistry.set(OUTPUTS_CLASSES.cleanup, cleanup);
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
    const cleanup = elements[OUTPUTS_CLASSES.cleanup];
    const masonry = elements[OUTPUTS_CLASSES.masonry];
    const toggle = elements[OUTPUTS_CLASSES.toggle];
    if (!cleanup || !h4 || !masonry || !toggle) {
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
    const cleanupBusy = cleanup.getAttribute("aria-busy") === "true";
    cleanup.hidden = !isHistoryView;
    cleanup.lfUiState = isHistoryView && !cleanupBusy ? "danger" : "disabled";
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
const WORKFLOW_RUNNER_PATH = `${API_ROOT}/workflow-runner`;
const resolveComfyUrl = (href = window.location.href, proxyPort = DEFAULT_FRONTEND_PROXY_PORT, comfyPort = DEFAULT_COMFY_UI_PORT, comfyProtocol = DEFAULT_COMFY_UI_PROTOCOL) => {
  const current = new URL(href);
  if (current.port === proxyPort) {
    current.protocol = comfyProtocol;
    current.port = comfyPort;
  }
  const runnerIndex = current.pathname.indexOf(WORKFLOW_RUNNER_PATH);
  const runnerEnd = runnerIndex + WORKFLOW_RUNNER_PATH.length;
  if (runnerIndex >= 0 && (runnerEnd === current.pathname.length || current.pathname[runnerEnd] === "/")) {
    const deploymentPrefix = current.pathname.slice(0, runnerIndex);
    current.pathname = deploymentPrefix || "/";
  } else {
    current.pathname = "/";
  }
  current.search = "";
  current.hash = "";
  return current.toString();
};
const HISTORY_CLEANUP_IN_FLIGHT = /* @__PURE__ */ new WeakSet();
const _historyCleanupNotification = (store, message, status) => {
  store.getState().mutate.notifications.add({
    id: `${performance.now()}-${Math.random()}`,
    message,
    status
  });
};
const removeMissingHistory = async (button, store) => {
  if (HISTORY_CLEANUP_IN_FLIGHT.has(button) || store.getState().view !== "history") {
    return;
  }
  HISTORY_CLEANUP_IN_FLIGHT.add(button);
  button.lfAriaLabel = "Checking Runner history for missing outputs";
  button.lfLabel = "Checking…";
  button.lfShowSpinner = true;
  button.lfUiState = "disabled";
  button.setAttribute("aria-busy", "true");
  try {
    const { manager } = store.getState();
    const preview = await manager.runs.pruneMissingArtifacts(true);
    if (preview.candidate_count === 0) {
      const preserved2 = preview.skipped_unknown ? ` ${preview.skipped_unknown} ambiguous or fileless successful run${preview.skipped_unknown === 1 ? " was" : "s were"} preserved.` : "";
      _historyCleanupNotification(store, `No missing-output or failed runs to remove.${preserved2}`, "info");
      return;
    }
    const count = preview.candidate_count;
    const confirmed = window.confirm(`Remove ${count} run${count === 1 ? "" : "s"} from Runner history?

This removes Runner history and saved remix inputs for successful runs whose outputs are missing, plus failed, cancelled, and timed-out runs. It never deletes files and preserves ambiguous or fileless successful runs.`);
    if (!confirmed) {
      return;
    }
    button.lfAriaLabel = "Removing stale Runner history";
    button.lfLabel = "Removing…";
    const result = await manager.runs.pruneMissingArtifacts(false, preview.candidate_run_ids);
    const removed = result.removed_count;
    const preserved = result.skipped_unknown ? ` ${result.skipped_unknown} ambiguous or fileless successful run${result.skipped_unknown === 1 ? " was" : "s were"} preserved.` : "";
    const changed = result.skipped_changed ? ` ${result.skipped_changed} run${result.skipped_changed === 1 ? " changed" : "s changed"} during cleanup and ${result.skipped_changed === 1 ? "was" : "were"} left untouched.` : "";
    _historyCleanupNotification(store, `Removed ${removed} stale run${removed === 1 ? "" : "s"} from Runner history. No files were deleted.${preserved}${changed}`, "info");
  } catch (error) {
    const detail = error instanceof Error && error.message ? ` ${error.message}` : "";
    _historyCleanupNotification(store, `Unable to clean Runner history.${detail}`, "danger");
  } finally {
    HISTORY_CLEANUP_IN_FLIGHT.delete(button);
    button.removeAttribute("aria-busy");
    button.lfAriaLabel = "Remove stale Runner history entries";
    button.lfLabel = "Remove missing";
    button.lfShowSpinner = false;
    button.lfUiState = store.getState().view === "history" ? "danger" : "disabled";
  }
};
const buttonHandler = (e, store) => {
  const { comp, eventType } = e.detail;
  const { manager, view } = store.getState();
  switch (eventType) {
    case "click":
      switch (comp.rootElement.className) {
        // Action Button
        case ACTION_BUTTON_CLASSES._: {
          const state = store.getState();
          const activeRun = state.runs.find((run) => run.runId === state.currentRunId && ["pending", "running"].includes(run.status));
          if (activeRun && manager.getDispatchers().cancelWorkflow) {
            void manager.getDispatchers().cancelWorkflow();
          } else if (!state.submissionInFlightId) {
            void manager.getDispatchers().runWorkflow();
          }
          break;
        }
        // Drawer
        case DRAWER_CLASSES.buttonComfyUi:
          window.open(resolveComfyUrl(), "_blank", "noopener,noreferrer");
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
        case RESULTS_CLASSES.remix:
          if (manager.runs.selected() && manager.runs.remix) {
            manager.runs.remix(manager.runs.selected().runId);
          }
          break;
        case OUTPUTS_CLASSES.cleanup:
          void removeMissingHistory(comp.rootElement, store);
          break;
        default:
          return;
      }
      break;
    default:
      return;
  }
};
const RETAINED_UPLOAD_EVENT = "lf-workflow-retained-upload-change";
const retainedUploads = /* @__PURE__ */ new WeakMap();
const findSelectNodeId = (nodes, workflowValue) => {
  let displayFallback;
  const visit = (items) => {
    for (const node of items || []) {
      if (node.workflowValue === workflowValue) {
        return node.id;
      }
      if (displayFallback === void 0 && (node.value === workflowValue || node.id === String(workflowValue))) {
        displayFallback = node.id;
      }
      const childMatch = visit(node.children);
      if (childMatch) {
        return childMatch;
      }
    }
    return void 0;
  };
  return visit(nodes) ?? displayFallback;
};
const normalizeRetainedUpload = (cell, value) => {
  if (!value || typeof value !== "object" || Array.isArray(value) || value.schema !== "lf.workflow-upload-prefill.v1") {
    return void 0;
  }
  const candidate = value;
  const reference = candidate.reference;
  const names = candidate.names;
  if (!reference || typeof reference !== "object" || typeof reference.sourceRunId !== "string" || !reference.sourceRunId || reference.sourceRunId.length > 256 || !Array.isArray(names) || names.length === 0 || names.length > 64 || names.some((name) => typeof name !== "string" || !name.trim() || name.length > 255) || typeof candidate.available !== "boolean") {
    return void 0;
  }
  const normalizedReference = reference.schema === "lf.workflow-upload-ref.v1" && typeof reference.inputId === "string" && reference.inputId === cell.id ? {
    schema: "lf.workflow-upload-ref.v1",
    sourceRunId: reference.sourceRunId,
    inputId: reference.inputId
  } : reference.schema === "lf.workflow-artifact-ref.v1" && typeof reference.artifactId === "string" && /^[0-9a-f]{64}$/.test(reference.artifactId) && typeof reference.filename === "string" && Boolean(reference.filename) && reference.filename.length <= 255 && !/[\\/\0]/.test(reference.filename) ? {
    schema: "lf.workflow-artifact-ref.v1",
    sourceRunId: reference.sourceRunId,
    artifactId: reference.artifactId,
    filename: reference.filename
  } : void 0;
  if (!normalizedReference) {
    return void 0;
  }
  return {
    schema: "lf.workflow-upload-prefill.v1",
    reference: normalizedReference,
    names: names.map((name) => name.trim()),
    available: candidate.available
  };
};
const emitRetainedUploadChange = (cell, detail) => {
  cell.dispatchEvent(new CustomEvent(RETAINED_UPLOAD_EVENT, { detail }));
};
const setRetainedUploadPrefill = (cell, value) => {
  const normalized = normalizeRetainedUpload(cell, value);
  if (normalized === void 0) {
    return false;
  }
  retainedUploads.set(cell, normalized);
  emitRetainedUploadChange(cell, {
    available: normalized.available,
    names: [...normalized.names],
    retained: true
  });
  return true;
};
const clearRetainedUploadPrefill = (cell) => {
  retainedUploads.delete(cell);
  emitRetainedUploadChange(cell, { available: false, names: [], retained: false });
};
const getRetainedUploadPrefill = (cell) => {
  const retained = retainedUploads.get(cell);
  return retained ? {
    ...retained,
    reference: { ...retained.reference },
    names: [...retained.names]
  } : void 0;
};
const applyInputPrefill = async (cells, inputs) => {
  var _a2;
  for (const cell of cells) {
    const id = cell.id;
    if (!id || !Object.prototype.hasOwnProperty.call(inputs, id)) {
      continue;
    }
    const value = inputs[id];
    try {
      switch (cell.tagName.toLowerCase()) {
        case "lf-upload": {
          setRetainedUploadPrefill(cell, value);
          continue;
        }
        case "lf-chat": {
          const history = typeof value === "string" ? value : JSON.stringify(value ?? []);
          if (typeof cell.setHistory === "function") {
            await cell.setHistory(history);
          }
          break;
        }
        case "lf-select": {
          const selectedId = findSelectNodeId((_a2 = cell.lfDataset) == null ? void 0 : _a2.nodes, value) ?? String(value ?? "");
          if (typeof cell.setValue === "function") {
            await cell.setValue(selectedId);
          } else {
            cell.lfValue = selectedId;
          }
          break;
        }
        case "lf-toggle": {
          const enabled = value === true || value === "on" || value === 1;
          if (typeof cell.setValue === "function") {
            await cell.setValue(enabled ? "on" : "off");
          } else {
            cell.lfValue = enabled;
          }
          break;
        }
        default: {
          const text = value === null || value === void 0 ? "" : String(value);
          if (typeof cell.setValue === "function") {
            await cell.setValue(text);
          } else {
            cell.lfValue = text;
          }
        }
      }
    } catch {
    }
  }
};
const stores = /* @__PURE__ */ new WeakMap();
const getStore = (store) => {
  let draftStore = stores.get(store);
  if (!draftStore) {
    draftStore = { captureSequences: /* @__PURE__ */ new Map(), drafts: /* @__PURE__ */ new Map(), revisions: /* @__PURE__ */ new Map() };
    stores.set(store, draftStore);
  }
  return draftStore;
};
const cloneDraft = (draft) => {
  const clone = {};
  for (const [id, value] of Object.entries(draft)) {
    clone[id] = Array.isArray(value) ? value.slice() : value;
  }
  return clone;
};
const revision = (draftStore, workflowId) => draftStore.revisions.get(workflowId) ?? 0;
const isFileArray = (value) => Array.isArray(value) && value.every((item) => typeof File !== "undefined" && item instanceof File);
const readCell = async (cell) => {
  switch (cell.tagName.toLowerCase()) {
    case "lf-chat":
      return typeof cell.getHistory === "function" ? cell.getHistory() : cell.lfValue;
    case "lf-select": {
      const selected = typeof cell.getValue === "function" ? await cell.getValue() : cell.lfValue;
      if (selected && typeof selected === "object" && !Array.isArray(selected)) {
        const node = selected;
        return node.workflowValue ?? node.value ?? node.id ?? null;
      }
      return selected ?? null;
    }
    case "lf-toggle": {
      const value = typeof cell.getValue === "function" ? await cell.getValue() : cell.lfValue;
      return value === true || value === "on" || value === 1;
    }
    case "lf-upload": {
      const value = typeof cell.getValue === "function" ? await cell.getValue() : cell.lfValue;
      const files = isFileArray(value) ? value : [];
      if (files.length > 0) {
        return files.slice();
      }
      return getRetainedUploadPrefill(cell) ?? [];
    }
    default:
      return typeof cell.getValue === "function" ? cell.getValue() : cell.lfValue;
  }
};
const getWorkflowSessionDraft = (store, workflowId) => {
  const draft = getStore(store).drafts.get(workflowId);
  return draft ? cloneDraft(draft) : void 0;
};
const replaceWorkflowSessionDraft = (store, workflowId, draft) => {
  const draftStore = getStore(store);
  draftStore.revisions.set(workflowId, revision(draftStore, workflowId) + 1);
  draftStore.drafts.set(workflowId, cloneDraft(draft));
};
const clearWorkflowSessionDraft = (store, workflowId) => {
  const draftStore = getStore(store);
  draftStore.revisions.set(workflowId, revision(draftStore, workflowId) + 1);
  draftStore.drafts.delete(workflowId);
};
const captureWorkflowSessionDraft = async (store, workflowId, cells) => {
  if (!workflowId) {
    return;
  }
  const draftStore = getStore(store);
  const startedAtRevision = revision(draftStore, workflowId);
  const captureSequence = (draftStore.captureSequences.get(workflowId) ?? 0) + 1;
  draftStore.captureSequences.set(workflowId, captureSequence);
  const captured = {};
  for (const cell of cells || []) {
    if (!(cell == null ? void 0 : cell.id)) {
      continue;
    }
    try {
      captured[cell.id] = await readCell(cell);
    } catch {
    }
  }
  if (revision(draftStore, workflowId) !== startedAtRevision || draftStore.captureSequences.get(workflowId) !== captureSequence) {
    return;
  }
  draftStore.drafts.set(workflowId, {
    ...draftStore.drafts.get(workflowId) || {},
    ...captured
  });
};
const applyWorkflowSessionDraft = async (cells, draft) => {
  const ordinary = { ...draft };
  for (const cell of cells || []) {
    if (cell.tagName.toLowerCase() !== "lf-upload" || !cell.id) {
      continue;
    }
    const value = draft[cell.id];
    if (!isFileArray(value)) {
      continue;
    }
    clearRetainedUploadPrefill(cell);
    cell.lfValue = value.slice();
    delete ordinary[cell.id];
  }
  await applyInputPrefill(cells, ordinary);
};
const EVENTS_BY_TAG = {
  "lf-chat": ["lf-chat-event"],
  "lf-select": ["lf-select-event"],
  "lf-textfield": ["lf-textfield-event"],
  "lf-toggle": ["lf-toggle-event"],
  "lf-upload": ["lf-upload-event", RETAINED_UPLOAD_EVENT]
};
const watchWorkflowSessionDraft = (store, workflowId, cells, shouldCapture = () => true) => {
  let queued = false;
  let disposed = false;
  const requestCapture = () => {
    if (disposed || !shouldCapture() || queued) {
      return;
    }
    queued = true;
    queueMicrotask(() => {
      queued = false;
      if (!disposed && shouldCapture()) {
        void captureWorkflowSessionDraft(store, workflowId, cells);
      }
    });
  };
  const listeners = [];
  for (const cell of cells || []) {
    for (const eventName of EVENTS_BY_TAG[cell.tagName.toLowerCase()] || []) {
      const listener = (event) => {
        var _a2;
        const eventType = (_a2 = event.detail) == null ? void 0 : _a2.eventType;
        if (eventName !== RETAINED_UPLOAD_EVENT && !["change", "delete", "input", "update", "upload"].includes(eventType || "")) {
          return;
        }
        requestCapture();
      };
      cell.addEventListener(eventName, listener);
      listeners.push([cell, eventName, listener]);
    }
  }
  return () => {
    disposed = true;
    for (const [cell, eventName, listener] of listeners) {
      cell.removeEventListener(eventName, listener);
    }
  };
};
const { theme: theme$2 } = getLfFramework();
const ROOT_CLASS$2 = "inputs-section";
const INPUTS_CLASSES = {
  _: theme$2.bemClass(ROOT_CLASS$2),
  cell: theme$2.bemClass(ROOT_CLASS$2, "cell"),
  cells: theme$2.bemClass(ROOT_CLASS$2, "cells"),
  description: theme$2.bemClass(ROOT_CLASS$2, "description"),
  help: theme$2.bemClass(ROOT_CLASS$2, "help"),
  h3: theme$2.bemClass(ROOT_CLASS$2, "title-h3"),
  openButton: theme$2.bemClass(ROOT_CLASS$2, "title-open-button"),
  resetButton: theme$2.bemClass(ROOT_CLASS$2, "title-reset-button"),
  options: theme$2.bemClass(ROOT_CLASS$2, "options"),
  readiness: theme$2.bemClass(ROOT_CLASS$2, "readiness"),
  retainedUpload: theme$2.bemClass(ROOT_CLASS$2, "retained-upload"),
  retainedUploadClear: theme$2.bemClass(ROOT_CLASS$2, "retained-upload-clear"),
  retainedUploadText: theme$2.bemClass(ROOT_CLASS$2, "retained-upload-text"),
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
const _title = (store, onReset) => {
  const download = theme$2.get.icon("download");
  const refresh = theme$2.get.icon("refresh");
  const title = document.createElement("div");
  const h3 = document.createElement("h3");
  const resetButton = document.createElement("lf-button");
  const openButton = document.createElement("lf-button");
  title.className = INPUTS_CLASSES.title;
  h3.className = INPUTS_CLASSES.h3;
  resetButton.className = INPUTS_CLASSES.resetButton;
  resetButton.lfAriaLabel = "Reset this workflow form to its defaults";
  resetButton.lfIcon = refresh;
  resetButton.lfLabel = "Reset";
  resetButton.lfStyling = "flat";
  resetButton.lfUiSize = "xsmall";
  resetButton.addEventListener("lf-button-event", (event) => {
    var _a2;
    if (((_a2 = event.detail) == null ? void 0 : _a2.eventType) === "click") {
      onReset();
    }
  });
  const label = "Download Workflow JSON";
  openButton.className = INPUTS_CLASSES.openButton;
  openButton.lfAriaLabel = label;
  openButton.lfIcon = download;
  openButton.lfStyling = "icon";
  openButton.lfUiSize = "xsmall";
  openButton.title = label;
  openButton.addEventListener("lf-button-event", (e) => buttonHandler(e, store));
  title.appendChild(h3);
  title.appendChild(resetButton);
  title.appendChild(openButton);
  return { h3, openButton, resetButton, title };
};
const _help = (value) => {
  if (!value) {
    return null;
  }
  const p = document.createElement("p");
  p.className = INPUTS_CLASSES.help;
  p.textContent = value;
  return p;
};
const _readiness = () => {
  const notice = document.createElement("aside");
  notice.className = INPUTS_CLASSES.readiness;
  notice.hidden = true;
  notice.setAttribute("role", "status");
  return notice;
};
const _helperHasValue = (helper) => {
  if (typeof helper === "string") {
    return Boolean(helper.trim());
  }
  if (!helper || typeof helper !== "object") {
    return false;
  }
  const value = helper.value;
  return typeof value === "string" && Boolean(value.trim());
};
const _hasNativeHelper = (cell) => {
  const props = cell.props;
  if (!props) {
    return false;
  }
  if (!cell.shape || cell.shape === "textfield") {
    return _helperHasValue(props.lfHelper);
  }
  if (cell.shape === "choice" || cell.shape === "select") {
    const textfieldProps = props.lfTextfieldProps;
    return Boolean(textfieldProps && typeof textfieldProps === "object" && _helperHasValue(textfieldProps.lfHelper));
  }
  return false;
};
const _retainedUpload = (component) => {
  const retained = document.createElement("div");
  const text = document.createElement("span");
  const clear = document.createElement("button");
  retained.className = INPUTS_CLASSES.retainedUpload;
  retained.hidden = true;
  text.className = INPUTS_CLASSES.retainedUploadText;
  clear.className = INPUTS_CLASSES.retainedUploadClear;
  clear.type = "button";
  clear.textContent = "Clear";
  clear.setAttribute("aria-label", "Stop reusing the previous upload");
  component.addEventListener(RETAINED_UPLOAD_EVENT, (event) => {
    const detail = event.detail;
    const names = Array.isArray(detail == null ? void 0 : detail.names) ? detail.names : [];
    retained.hidden = !(detail == null ? void 0 : detail.retained);
    text.textContent = (detail == null ? void 0 : detail.retained) ? detail.available ? `Reusing ${names.length > 1 ? `${names.length} previous uploads` : names[0] || "previous upload"}. Choose a new file to replace it.` : `${names.length > 1 ? `${names.length} previous uploads are` : `${names[0] || "The previous upload"} is`} no longer available. Choose the file${names.length > 1 ? "s" : ""} again.` : "";
  });
  component.addEventListener("lf-upload-event", (event) => {
    var _a2;
    const detail = event.detail;
    if ((detail == null ? void 0 : detail.eventType) === "upload" && ((_a2 = detail.selectedFiles) == null ? void 0 : _a2.length)) {
      clearRetainedUploadPrefill(component);
    }
  });
  clear.addEventListener("click", () => clearRetainedUploadPrefill(component));
  retained.append(text, clear);
  return retained;
};
const createInputsSection = (store) => {
  const { WORKFLOW_INPUTS_DESTROYED, WORKFLOW_INPUTS_MOUNTED, WORKFLOW_INPUTS_UPDATED } = DEBUG_MESSAGES;
  let activeHydration = null;
  let mountGeneration = 0;
  let mountedCells = [];
  let mountedWorkflowId = null;
  let skipDestroyCapture = false;
  let stopWatchingDraft = null;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const wasHydrating = activeHydration !== null;
    mountGeneration += 1;
    activeHydration = null;
    stopWatchingDraft == null ? void 0 : stopWatchingDraft();
    stopWatchingDraft = null;
    if (!skipDestroyCapture && !wasHydrating && mountedWorkflowId && mountedCells.length > 0) {
      void captureWorkflowSessionDraft(store, mountedWorkflowId, mountedCells);
    }
    for (const cls in INPUTS_CLASSES) {
      const element = INPUTS_CLASSES[cls];
      uiRegistry.remove(element);
    }
    mountedCells = [];
    mountedWorkflowId = null;
    debugLog(WORKFLOW_INPUTS_DESTROYED);
  };
  const mount = () => {
    var _a2;
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[INPUTS_CLASSES._]) {
      return;
    }
    const workflow = manager.workflow.current();
    const workflowId = (workflow == null ? void 0 : workflow.id) || ((_a2 = state.current) == null ? void 0 : _a2.id) || null;
    const generation = ++mountGeneration;
    const _root = document.createElement("section");
    _root.className = INPUTS_CLASSES._;
    const description = _description();
    const readiness = _readiness();
    const options = _options();
    const reset = () => {
      if (!mountedWorkflowId) {
        return;
      }
      clearWorkflowSessionDraft(store, mountedWorkflowId);
      store.getState().mutate.inputPrefillRun(null);
      skipDestroyCapture = true;
      try {
        destroy();
      } finally {
        skipDestroyCapture = false;
      }
      mount();
      render();
    };
    const { h3, openButton, resetButton, title } = _title(store, reset);
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
        if (cell.required === false) {
          component.dataset.required = "false";
        }
        cellElements.push(component);
        wrapper.appendChild(component);
        const help = _hasNativeHelper(cell) ? null : _help(cell.title);
        if (help) {
          wrapper.appendChild(help);
        }
        if (cell.shape === "upload") {
          wrapper.appendChild(_retainedUpload(component));
        }
        options.appendChild(wrapper);
      }
    }
    uiRegistry.set(INPUTS_CLASSES.cells, cellElements);
    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(readiness);
    _root.appendChild(options);
    elements[MAIN_CLASSES._].prepend(_root);
    uiRegistry.set(INPUTS_CLASSES._, _root);
    uiRegistry.set(INPUTS_CLASSES.description, description);
    uiRegistry.set(INPUTS_CLASSES.h3, h3);
    uiRegistry.set(INPUTS_CLASSES.openButton, openButton);
    uiRegistry.set(INPUTS_CLASSES.resetButton, resetButton);
    uiRegistry.set(INPUTS_CLASSES.options, options);
    uiRegistry.set(INPUTS_CLASSES.readiness, readiness);
    uiRegistry.set(INPUTS_CLASSES.title, title);
    mountedCells = cellElements;
    mountedWorkflowId = workflowId;
    if (workflowId) {
      const currentState = store.getState();
      const artifactPrefill = consumeArtifactHandoff(store, workflowId);
      let prefill = artifactPrefill;
      let isIntentionalOverride = Boolean(artifactPrefill);
      if (!prefill && currentState.inputPrefillRunId) {
        const pendingRunId = currentState.inputPrefillRunId;
        const run = manager.runs.get(pendingRunId);
        currentState.mutate.inputPrefillRun(null);
        if ((run == null ? void 0 : run.workflowId) === workflowId && run.inputs) {
          prefill = run.inputs;
          isIntentionalOverride = true;
        }
      }
      const values = prefill || getWorkflowSessionDraft(store, workflowId);
      if (values) {
        if (isIntentionalOverride) {
          replaceWorkflowSessionDraft(store, workflowId, values);
        }
        activeHydration = generation;
        void applyWorkflowSessionDraft(cellElements, values).finally(() => {
          if (activeHydration === generation) {
            activeHydration = null;
          }
        });
      }
      stopWatchingDraft = watchWorkflowSessionDraft(store, workflowId, cellElements, () => activeHydration !== generation);
    }
    debugLog(WORKFLOW_INPUTS_MOUNTED);
  };
  const render = () => {
    var _a2, _b2, _c2;
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
    const readiness = elements[INPUTS_CLASSES.readiness];
    const workflow = manager.workflow.current();
    descr.textContent = manager.workflow.description();
    h3.textContent = manager.workflow.title();
    if (readiness) {
      const status = (_a2 = workflow == null ? void 0 : workflow.readiness) == null ? void 0 : _a2.status;
      const issues = ((_b2 = workflow == null ? void 0 : workflow.readiness) == null ? void 0 : _b2.issues) || [];
      readiness.hidden = !status || status === "ready";
      if (status && status !== "ready") {
        readiness.dataset.status = status;
        const prefix = status === "setup_required" ? "Setup required" : "Setup check";
        readiness.textContent = `${prefix}: ${((_c2 = issues[0]) == null ? void 0 : _c2.message) || "Review this workflow before running."}`;
      } else {
        readiness.textContent = "";
        delete readiness.dataset.status;
      }
    }
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
    credentials: "include",
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
  let data;
  try {
    data = await syntax.json.parse(response);
  } catch {
    throw new WorkflowApiError(`${RUN_GENERIC} (invalid response)`, {
      status: response.status
    });
  }
  if (!response.ok || !data) {
    const payloadData = (data == null ? void 0 : data.payload) || { detail: response.statusText };
    const detail = (payloadData == null ? void 0 : payloadData.detail) || response.statusText;
    throw new WorkflowApiError(`${RUN_GENERIC} (${detail})`, {
      payload: payloadData,
      status: response.status
    });
  }
  const raw = data;
  const validStatuses = /* @__PURE__ */ new Set([
    "accepted",
    "cancelled",
    "failed",
    "pending",
    "reconciling",
    "running",
    "succeeded",
    "timeout"
  ]);
  if (typeof raw.run_id !== "string" || !raw.run_id || typeof raw.submission_id !== "string" || !raw.submission_id || payload.submissionId !== void 0 && raw.submission_id !== payload.submissionId || raw.status !== void 0 && !validStatuses.has(raw.status) || raw.idempotent_replay !== void 0 && typeof raw.idempotent_replay !== "boolean") {
    throw new WorkflowApiError(`${RUN_GENERIC} (invalid response)`, {
      status: response.status
    });
  }
  return {
    idempotentReplay: raw.idempotent_replay === true,
    runId: raw.run_id,
    status: raw.status ?? "pending",
    submissionId: raw.submission_id
  };
};
const getWorkflowSubmission = async (submissionId) => {
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl(`/submissions/${encodeURIComponent(submissionId)}`), {
    credentials: "include",
    method: "GET"
  });
  if (response.status === 404) {
    return null;
  }
  if (response.status === 401) {
    try {
      window.location.href = `${window.location.origin}${API_BASE}/workflow-runner`;
    } catch (err) {
    }
    throw new WorkflowApiError("Unauthorized", { status: 401 });
  }
  let data;
  try {
    data = await syntax.json.parse(response);
  } catch {
    throw new WorkflowApiError("Invalid submission response.", { status: response.status });
  }
  if (!response.ok) {
    const detail = data && typeof data === "object" && typeof data.detail === "string" ? data.detail : response.statusText;
    throw new WorkflowApiError(`Unable to reconcile submission (${detail || response.status}).`, {
      payload: data,
      status: response.status
    });
  }
  const snapshot = data;
  const validStatuses = /* @__PURE__ */ new Set([
    "accepted",
    "cancelled",
    "failed",
    "pending",
    "reconciling",
    "running",
    "succeeded",
    "timeout"
  ]);
  if (!snapshot || snapshot.submission_id !== submissionId || snapshot.run_id !== null && typeof snapshot.run_id !== "string" || typeof snapshot.workflow_id !== "string" || !snapshot.status || !validStatuses.has(snapshot.status)) {
    throw new WorkflowApiError("Invalid submission response.", { status: response.status });
  }
  return snapshot;
};
const cancelWorkflowSubmission = async (submissionId) => {
  const response = await fetch(buildApiUrl(`/submissions/${encodeURIComponent(submissionId)}/cancel`), {
    credentials: "include",
    method: "POST"
  });
  const data = await response.json().catch(() => null);
  if (!response.ok || !data || !("submission_id" in data)) {
    const detail = data && "detail" in data ? data.detail || data.error : response.statusText;
    throw new WorkflowApiError(`Unable to stop workflow (${detail || response.status}).`, {
      payload: data ?? void 0,
      status: response.status
    });
  }
  return data;
};
const uploadWorkflowFiles = async (files) => {
  var _a2, _b2;
  const { UPLOAD_GENERIC, UPLOAD_INVALID_RESPONSE, UPLOAD_MISSING_FILE } = ERROR_MESSAGES;
  const { syntax } = getLfFramework();
  if (!files || files.length === 0) {
    throw new WorkflowApiError(UPLOAD_MISSING_FILE, {
      payload: { error: { message: "missing_file" } }
    });
  }
  const formData = new FormData();
  formData.append("directory", "input");
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
      const detail = ((_a2 = payload == null ? void 0 : payload.error) == null ? void 0 : _a2.message) || response.statusText;
      throw new WorkflowApiError(`${UPLOAD_GENERIC} (${detail})`, {
        payload
      });
    }
    return data;
  }
  if (isWorkflowAPIUploadPayload(data)) {
    if (!response.ok) {
      const detail = ((_b2 = data.error) == null ? void 0 : _b2.message) || response.statusText;
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
const SUBMISSIONS_IN_FLIGHT = /* @__PURE__ */ new WeakSet();
const RETRYABLE_SUBMISSIONS = /* @__PURE__ */ new WeakMap();
let fallbackSubmissionCounter = 0;
const createWorkflowSubmissionId = () => {
  const browserCrypto = globalThis.crypto;
  if (typeof (browserCrypto == null ? void 0 : browserCrypto.randomUUID) === "function") {
    return `lf-web:${browserCrypto.randomUUID()}`;
  }
  if (typeof (browserCrypto == null ? void 0 : browserCrypto.getRandomValues) === "function") {
    const bytes = new Uint8Array(16);
    browserCrypto.getRandomValues(bytes);
    const entropy = Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("");
    return `lf-web:${entropy}`;
  }
  fallbackSubmissionCounter += 1;
  return `lf-web:${Date.now().toString(36)}:${fallbackSubmissionCounter.toString(36)}:${Math.random().toString(36).slice(2)}`;
};
const _readInputIntent = async (store) => {
  const state = store.getState();
  const { uiRegistry } = state.manager;
  const elements = uiRegistry.get();
  const cells = (elements == null ? void 0 : elements[INPUTS_CLASSES.cells]) || [];
  const intent = [];
  for (const cell of cells) {
    const id = cell.id || "";
    _setCellStatus(store, id);
    const tagName = cell.tagName.toLowerCase();
    try {
      switch (tagName) {
        case "lf-chat": {
          const value = await cell.getHistory();
          intent.push({ id, kind: "value", tagName, value });
          break;
        }
        case "lf-select": {
          const selected = await cell.getValue();
          intent.push({
            id,
            kind: "value",
            tagName,
            value: (selected == null ? void 0 : selected.workflowValue) ?? (selected == null ? void 0 : selected.value) ?? (selected == null ? void 0 : selected.id) ?? null
          });
          break;
        }
        case "lf-toggle": {
          const value = await cell.getValue();
          intent.push({ id, kind: "value", tagName, value: value !== "off" });
          break;
        }
        case "lf-upload": {
          const value = await cell.getValue();
          intent.push({
            files: Array.isArray(value) ? value : value || [],
            id,
            kind: "upload",
            required: cell.dataset.required !== "false",
            retained: getRetainedUploadPrefill(cell)
          });
          break;
        }
        default: {
          const value = await cell.getValue();
          intent.push({ id, kind: "value", tagName, value });
        }
      }
    } catch (error) {
      if (tagName === "lf-upload") {
        _setCellStatus(store, id, "error");
      }
      throw error;
    }
  }
  return intent;
};
const _canonicalizeIntentValue = (value, ancestors = /* @__PURE__ */ new WeakSet()) => {
  if (value === null || typeof value === "string" || typeof value === "boolean") {
    return value;
  }
  if (typeof value === "number") {
    if (Number.isNaN(value))
      return { $number: "NaN" };
    if (value === Infinity)
      return { $number: "Infinity" };
    if (value === -Infinity)
      return { $number: "-Infinity" };
    if (Object.is(value, -0))
      return { $number: "-0" };
    return value;
  }
  if (typeof value === "undefined")
    return { $type: "undefined" };
  if (typeof value === "bigint")
    return { $bigint: value.toString() };
  if (typeof value === "symbol")
    return { $symbol: value.description ?? "" };
  if (typeof value === "function")
    return { $function: value.name || "" };
  if (typeof value !== "object")
    return { $type: typeof value };
  if (ancestors.has(value)) {
    throw new Error("An input contains a circular value and cannot be submitted.");
  }
  ancestors.add(value);
  try {
    if (Array.isArray(value)) {
      return value.map((item) => _canonicalizeIntentValue(item, ancestors));
    }
    if (value instanceof Date) {
      return { $date: value.toISOString() };
    }
    const normalized = {};
    for (const key of Object.keys(value).sort()) {
      normalized[key] = _canonicalizeIntentValue(value[key], ancestors);
    }
    return normalized;
  } finally {
    ancestors.delete(value);
  }
};
const _intentFingerprint = (workflowId, intent) => JSON.stringify({
  workflowId,
  inputs: intent.map((entry) => {
    if (entry.kind === "value") {
      return {
        id: entry.id,
        kind: entry.kind,
        tagName: entry.tagName,
        value: _canonicalizeIntentValue(entry.value)
      };
    }
    if (entry.files.length > 0) {
      return {
        files: entry.files.map((file) => ({
          lastModified: file.lastModified,
          name: file.name,
          relativePath: file.webkitRelativePath || "",
          size: file.size,
          type: file.type
        })),
        id: entry.id,
        kind: entry.kind,
        required: entry.required
      };
    }
    return {
      id: entry.id,
      kind: entry.kind,
      required: entry.required,
      retainedReference: entry.retained ? _canonicalizeIntentValue(entry.retained.reference) : null
    };
  })
});
const _materializeInputs = async (store, intent) => {
  const inputs = {};
  for (const entry of intent) {
    if (entry.kind === "value") {
      inputs[entry.id] = entry.value;
      continue;
    }
    try {
      const uploaded = await _handleUploadCell(store, entry.files, entry.required, entry.retained);
      if (uploaded !== void 0) {
        inputs[entry.id] = uploaded;
      }
    } catch (error) {
      _setCellStatus(store, entry.id, "error");
      throw error;
    }
  }
  return inputs;
};
const _createEnvelope = (workflowId, inputs, submissionId) => {
  const serialized = JSON.stringify({ workflowId, inputs, submissionId });
  if (!serialized) {
    throw new Error("Workflow inputs could not be serialized.");
  }
  return JSON.parse(serialized);
};
const _handleUploadCell = async (store, rawValue, required, retainedValue) => {
  var _a2;
  const { ERROR_UPLOADING_FILE, RUNNING_UPLOADING_FILE } = STATUS_MESSAGES;
  const files = Array.isArray(rawValue) ? rawValue : rawValue;
  if (!files || files.length === 0) {
    if (retainedValue == null ? void 0 : retainedValue.available) {
      return { ...retainedValue.reference };
    }
    if (retainedValue && !retainedValue.available) {
      throw new Error("The previous upload is no longer available. Choose the file again.");
    }
    if (!required) {
      return void 0;
    }
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
        message: `Upload failed: ${((_a2 = error.payload) == null ? void 0 : _a2.detail) || error.message}`,
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
const _toRunStatus = (status) => status === "accepted" || status === "reconciling" ? "pending" : status;
const _normalizeRunResponse = (response, submissionId) => {
  if (typeof response === "string") {
    return {
      idempotentReplay: false,
      runId: response,
      status: "pending",
      submissionId
    };
  }
  if (!response.runId || response.submissionId !== submissionId) {
    throw new WorkflowApiError("Workflow run failed. (invalid response)", { status: 200 });
  }
  return response;
};
const _recordRun = (store, response, workflowId, workflowName, startedAt) => {
  const timestamp = Date.now();
  upsertRun(store, {
    cancelRequested: false,
    createdAt: startedAt,
    error: null,
    httpStatus: null,
    // Upload responses contain host paths for the immediate local request.
    // Do not copy them into browser state: the run-detail endpoint will
    // hydrate authoritative, opaque remix references after registration.
    inputs: {},
    outputs: null,
    resultPayload: null,
    runId: response.runId,
    submissionId: response.submissionId,
    status: _toRunStatus(response.status),
    updatedAt: timestamp,
    workflowId,
    workflowName
  });
  ensureActiveRun(store, response.runId);
};
const _errorDetail = (error, fallback) => {
  if (error instanceof WorkflowApiError) {
    const payload = error.payload;
    return (payload == null ? void 0 : payload.detail) || error.message;
  }
  return error instanceof Error ? error.message || fallback : fallback;
};
const _isAuthoritativeRejection = (error) => error instanceof WorkflowApiError && typeof error.status === "number" && error.status >= 400 && error.status < 500;
const _reconcileSubmission = async (submissionId) => {
  try {
    const snapshot = await getWorkflowSubmission(submissionId);
    if (!snapshot) {
      return { kind: "unknown" };
    }
    if (snapshot.run_id) {
      return {
        kind: "recovered",
        response: {
          idempotentReplay: true,
          runId: snapshot.run_id,
          status: snapshot.status,
          submissionId: snapshot.submission_id
        }
      };
    }
    if (snapshot.status === "failed" || snapshot.status === "cancelled") {
      return {
        detail: snapshot.error || `Submission ${snapshot.status}.`,
        kind: "rejected"
      };
    }
  } catch {
  }
  return { kind: "unknown" };
};
const workflowDispatcher = async (store) => {
  var _a2, _b2, _c2, _d, _e, _f, _g, _h, _i, _j;
  const { INPUTS_COLLECTED } = DEBUG_MESSAGES;
  const { NO_WORKFLOW_SELECTED } = NOTIFICATION_MESSAGES;
  const { ERROR_RUNNING_WORKFLOW, RUNNING_DISPATCHING_WORKFLOW, RUNNING_SUBMITTING_WORKFLOW } = STATUS_MESSAGES;
  const state = store.getState();
  const { current } = state;
  const id = current.id;
  if (SUBMISSIONS_IN_FLIGHT.has(store) || state.submissionInFlightId) {
    return;
  }
  if (!id) {
    addNotification(store, {
      id: performance.now().toString(),
      message: NO_WORKFLOW_SELECTED,
      status: "warning"
    });
    return;
  }
  const cached = RETRYABLE_SUBMISSIONS.get(store);
  const provisionalSubmissionId = (cached == null ? void 0 : cached.outcome) === "ambiguous" ? String(cached.envelope.submissionId) : createWorkflowSubmissionId();
  SUBMISSIONS_IN_FLIGHT.add(store);
  (_b2 = (_a2 = state.mutate).submissionInFlight) == null ? void 0 : _b2.call(_a2, provisionalSubmissionId);
  try {
    setStatus$1(store, "running", RUNNING_SUBMITTING_WORKFLOW);
    let attempt;
    try {
      const intent = await _readInputIntent(store);
      const intentFingerprint = _intentFingerprint(id, intent);
      if ((cached == null ? void 0 : cached.intentFingerprint) === intentFingerprint) {
        if (cached.outcome === "ambiguous") {
          attempt = cached;
        } else {
          attempt = {
            envelope: _createEnvelope(id, cached.envelope.inputs, provisionalSubmissionId),
            intentFingerprint,
            outcome: "ambiguous",
            startedAt: Date.now()
          };
        }
      } else {
        RETRYABLE_SUBMISSIONS.delete(store);
        const submissionId = (cached == null ? void 0 : cached.outcome) === "ambiguous" ? createWorkflowSubmissionId() : provisionalSubmissionId;
        (_d = (_c2 = state.mutate).submissionInFlight) == null ? void 0 : _d.call(_c2, submissionId);
        const inputs = await _materializeInputs(store, intent);
        attempt = {
          envelope: _createEnvelope(id, inputs, submissionId),
          intentFingerprint,
          outcome: "ambiguous",
          startedAt: Date.now()
        };
      }
      (_f = (_e = state.mutate).submissionInFlight) == null ? void 0 : _f.call(_e, String(attempt.envelope.submissionId));
      debugLog(INPUTS_COLLECTED, "informational", {
        id,
        inputKeys: Object.keys(attempt.envelope.inputs)
      });
    } catch (error) {
      const detail = _errorDetail(error, "Failed to collect inputs.");
      setStatus$1(store, "error", ERROR_RUNNING_WORKFLOW);
      addNotification(store, {
        id: performance.now().toString(),
        message: `Failed to collect inputs: ${detail}`,
        status: "danger"
      });
      return;
    }
    setStatus$1(store, "running", RUNNING_DISPATCHING_WORKFLOW);
    clearResults(store);
    const workflowName = ((_g = state.manager) == null ? void 0 : _g.workflow.title()) ?? id;
    RETRYABLE_SUBMISSIONS.set(store, attempt);
    try {
      const response = _normalizeRunResponse(await runWorkflow(attempt.envelope), String(attempt.envelope.submissionId));
      RETRYABLE_SUBMISSIONS.delete(store);
      _recordRun(store, response, id, workflowName, attempt.startedAt);
    } catch (error) {
      setStatus$1(store, "error", ERROR_RUNNING_WORKFLOW);
      const payload = error instanceof WorkflowApiError ? error.payload : void 0;
      const inputName = (_h = payload == null ? void 0 : payload.error) == null ? void 0 : _h.input;
      if (inputName) {
        _setCellStatus(store, inputName, "error");
      }
      if (_isAuthoritativeRejection(error)) {
        attempt.outcome = "authoritative-rejection";
        RETRYABLE_SUBMISSIONS.set(store, attempt);
        addNotification(store, {
          id: performance.now().toString(),
          message: `Workflow run failed: ${(payload == null ? void 0 : payload.detail) || error.message}`,
          status: "danger"
        });
        return;
      }
      attempt.outcome = "ambiguous";
      RETRYABLE_SUBMISSIONS.set(store, attempt);
      const reconciliation = await _reconcileSubmission(String(attempt.envelope.submissionId));
      if (reconciliation.kind === "recovered") {
        RETRYABLE_SUBMISSIONS.delete(store);
        _recordRun(store, reconciliation.response, id, workflowName, attempt.startedAt);
        addNotification(store, {
          id: performance.now().toString(),
          message: "Workflow submission recovered after the response was interrupted.",
          status: "info"
        });
        return;
      }
      if (reconciliation.kind === "rejected") {
        attempt.outcome = "authoritative-rejection";
        RETRYABLE_SUBMISSIONS.set(store, attempt);
        addNotification(store, {
          id: performance.now().toString(),
          message: `Workflow run failed: ${reconciliation.detail}`,
          status: "danger"
        });
        return;
      }
      addNotification(store, {
        id: performance.now().toString(),
        message: "Workflow outcome is unknown. Retry is safe: unchanged inputs will reuse the same submission and uploaded files.",
        status: "warning"
      });
    }
  } finally {
    SUBMISSIONS_IN_FLIGHT.delete(store);
    (_j = (_i = store.getState().mutate).submissionInFlight) == null ? void 0 : _j.call(_i, null);
  }
};
const workflowCancellationDispatcher = async (store) => {
  const state = store.getState();
  const run = state.runs.find((entry) => entry.runId === state.currentRunId);
  if (!run || !run.submissionId || !["pending", "running"].includes(run.status) || run.cancelRequested || state.cancelInFlightRunId === run.runId) {
    return;
  }
  state.mutate.cancelInFlightRun(run.runId);
  setStatus$1(store, "running", "Stopping workflow...");
  try {
    if (!state.manager.runs.cancel) {
      throw new Error("Workflow cancellation is unavailable.");
    }
    await state.manager.runs.cancel(run.runId);
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unable to stop workflow.";
    addNotification(store, {
      id: performance.now().toString(),
      message: detail,
      status: "danger"
    });
    setStatus$1(store, "error", detail);
  } finally {
    store.getState().mutate.cancelInFlightRun(null);
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
    var _a2, _b2;
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
    const body = ((_b2 = (_a2 = manager.getAppRoot()) == null ? void 0 : _a2.ownerDocument) == null ? void 0 : _b2.body) ?? document.body;
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
var _WorkflowRunnerClient_ES, _WorkflowRunnerClient_STORE, _WorkflowRunnerClient_WORKFLOW_NAMES, _WorkflowRunnerClient_CACHE_KEY, _WorkflowRunnerClient_CACHE_EXPIRY_MS, _WorkflowRunnerClient_INITIAL_BACKOFF_MS, _WorkflowRunnerClient_MAX_BACKOFF_MS, _WorkflowRunnerClient_POLLING_INTERVAL_MS, _WorkflowRunnerClient_RUNS_QUERY_LIMIT, _WorkflowRunnerClient_EVENT_RUN, _WorkflowRunnerClient_EVENT_QUEUE, _WorkflowRunnerClient_LAST_SEQ, _WorkflowRunnerClient_RUNS, _WorkflowRunnerClient_WORKFLOW_CACHE, _WorkflowRunnerClient_STATE, _WorkflowRunnerClient_POLLING, _WorkflowRunnerClient_BACKOFF_MS, _WorkflowRunnerClient_RECONNECT_TIMER, _WorkflowRunnerClient_STOPPED, _WorkflowRunnerClient_INFLIGHT_RECONCILES, _WorkflowRunnerClient_INFLIGHT_DETAILS, _WorkflowRunnerClient_LOADED_DETAILS, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, _WorkflowRunnerClient_REMOVED_RUN_IDS;
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
    _WorkflowRunnerClient_RECONNECT_TIMER.set(this, null);
    _WorkflowRunnerClient_STOPPED.set(this, true);
    _WorkflowRunnerClient_INFLIGHT_RECONCILES.set(this, /* @__PURE__ */ new Map());
    _WorkflowRunnerClient_INFLIGHT_DETAILS.set(this, /* @__PURE__ */ new Map());
    _WorkflowRunnerClient_LOADED_DETAILS.set(this, /* @__PURE__ */ new Set());
    _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID.set(this, null);
    _WorkflowRunnerClient_REMOVED_RUN_IDS.set(this, /* @__PURE__ */ new Set());
    this.onUpdate = (runs) => {
      var _a2;
      if (Object.keys(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_NAMES, "f")).length === 0) {
        const workflows = ((_a2 = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f").getState().workflows) == null ? void 0 : _a2.nodes) || [];
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
    const promise = this._fetchRun(run_id, false).catch(() => {
    }).finally(() => {
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f").delete(run_id);
    });
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f").set(run_id, promise);
  }
  async _fetchRun(run_id, includeDetail) {
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_REMOVED_RUN_IDS, "f").has(run_id)) {
      return;
    }
    try {
      const detailQuery = includeDetail ? "" : "?detail=0";
      const resp = await fetch(`${API_ROOT}/run/${encodeURIComponent(run_id)}/status${detailQuery}`, {
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
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_REMOVED_RUN_IDS, "f").has(run_id)) {
        return;
      }
      if (includeDetail && __classPrivateFieldGet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, "f") !== run_id) {
        return;
      }
      const rec = {
        run_id: data.run_id,
        artifacts: Array.isArray(data.artifacts) ? data.artifacts : void 0,
        submission_id: data.submission_id,
        cancel_requested: data.cancel_requested,
        workflow_id: data.workflow_id,
        status: data.status,
        seq: data.seq || 0,
        owner_id: data.owner_id,
        created_at: data.created_at,
        updated_at: data.updated_at,
        inputs: data.inputs,
        outputs: data.outputs,
        result: data.result,
        error: data.error
      };
      this.upsertRun(rec);
      if (includeDetail) {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LOADED_DETAILS, "f").add(run_id);
      }
    } catch (e) {
      debugLog("reconcileRun error", "warning", e);
      throw e;
    }
  }
  /** Fetch a terminal result only when its output detail is actually opened. */
  async loadRunDetail(run_id) {
    if (!run_id || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_REMOVED_RUN_IDS, "f").has(run_id)) {
      return;
    }
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, "f") && __classPrivateFieldGet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, "f") !== run_id) {
      this.releaseRunDetail(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, "f"));
    }
    __classPrivateFieldSet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, run_id, "f");
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_LOADED_DETAILS, "f").has(run_id)) {
      return;
    }
    const pending = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_DETAILS, "f").get(run_id);
    if (pending) {
      return pending;
    }
    const promise = this._fetchRun(run_id, true).finally(() => {
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_DETAILS, "f").delete(run_id);
    });
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_DETAILS, "f").set(run_id, promise);
    return promise;
  }
  /** Release the heavyweight payload while retaining the run's summary preview. */
  releaseRunDetail(run_id) {
    const target = run_id || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, "f");
    if (!target) {
      return;
    }
    const existing = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").get(target);
    const hadResult = (existing == null ? void 0 : existing.result) !== void 0 && existing.result !== null;
    const hadArtifacts = (existing == null ? void 0 : existing.artifacts) !== void 0;
    if (existing && (hadResult || hadArtifacts)) {
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").set(target, { ...existing, artifacts: [], result: null });
    }
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LOADED_DETAILS, "f").delete(target);
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, "f") === target) {
      __classPrivateFieldSet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, null, "f");
    }
    if (hadResult || hadArtifacts) {
      this.emitUpdate();
    }
  }
  applyEvent(ev) {
    if (!ev || !ev.run_id || typeof ev.status === "undefined" || ev.status === null) {
      debugLog("applyEvent: invalid run record (missing run_id or status)", "warning", ev);
      return;
    }
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_REMOVED_RUN_IDS, "f").has(ev.run_id)) {
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
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_REMOVED_RUN_IDS, "f").has(rec.run_id)) {
      return;
    }
    const last = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").get(rec.run_id) ?? -1;
    if (rec.seq < last)
      return;
    const existing = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").get(rec.run_id);
    if (rec.seq === last && existing) {
      const supplements = {
        ...rec.artifacts !== void 0 ? { artifacts: rec.artifacts } : {},
        ...rec.submission_id !== void 0 ? { submission_id: rec.submission_id } : {},
        ...rec.cancel_requested !== void 0 ? { cancel_requested: rec.cancel_requested } : {},
        ...rec.workflow_id !== void 0 ? { workflow_id: rec.workflow_id } : {},
        ...rec.owner_id !== void 0 ? { owner_id: rec.owner_id } : {},
        ...rec.created_at !== void 0 ? { created_at: rec.created_at } : {},
        ...rec.updated_at !== void 0 ? { updated_at: rec.updated_at } : {},
        ...rec.inputs !== void 0 ? { inputs: rec.inputs } : {},
        ...rec.outputs !== void 0 ? { outputs: rec.outputs } : {},
        ...rec.result !== void 0 ? { result: rec.result } : {},
        ...rec.error !== void 0 ? { error: rec.error } : {}
      };
      const hasNewSupplement = Object.entries(supplements).some(([key, value]) => existing[key] !== value);
      if (!hasNewSupplement) {
        return;
      }
      const merged = {
        ...existing,
        ...supplements
      };
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").set(rec.run_id, merged);
      this.emitUpdate();
      return;
    }
    const refreshOpenTerminalDetail = !!existing && rec.seq > last && __classPrivateFieldGet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, "f") === rec.run_id && ["succeeded", "failed", "cancelled", "timeout"].includes(rec.status);
    if (existing && rec.seq > last) {
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LOADED_DETAILS, "f").delete(rec.run_id);
    }
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").set(rec.run_id, rec.seq);
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").set(rec.run_id, rec);
    if (rec.workflow_id && !__classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f").has(rec.workflow_id)) {
      this.fetchWorkflowNames([rec.workflow_id]);
    }
    this.emitUpdate();
    if (refreshOpenTerminalDetail) {
      void this.loadRunDetail(rec.run_id);
    }
  }
  removeRuns(runIds) {
    const uniqueIds = [...new Set(runIds.filter(Boolean))];
    if (uniqueIds.length === 0) {
      return;
    }
    for (const runId of uniqueIds) {
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_REMOVED_RUN_IDS, "f").add(runId);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").delete(runId);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").delete(runId);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LOADED_DETAILS, "f").delete(runId);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f").delete(runId);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_DETAILS, "f").delete(runId);
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, "f") === runId) {
        __classPrivateFieldSet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, null, "f");
      }
    }
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f").getState().mutate.runs.removeMany(uniqueIds);
    ensureActiveRun(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f"));
    this.saveCache();
  }
  // Remove a run completely from state and cache (used when server returns 404)
  removeRun(runId) {
    this.removeRuns([runId]);
  }
  async pruneMissingArtifacts(dryRun, candidateRunIds) {
    if (!dryRun && !candidateRunIds) {
      throw new Error("History cleanup requires the candidate IDs from a dry-run preview.");
    }
    const requestBody = dryRun ? { dry_run: true } : { candidate_run_ids: candidateRunIds, dry_run: false };
    const resp = await fetch(`${API_ROOT}/workflow-runner/runs/prune-missing-artifacts`, {
      body: JSON.stringify(requestBody),
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    let data = {};
    try {
      data = await resp.json();
    } catch {
    }
    if (!resp.ok) {
      const detail = typeof data.detail === "string" ? ` ${data.detail}` : "";
      throw new Error(`History cleanup failed (${resp.status}).${detail}`);
    }
    const candidateRunIdsResponse = Array.isArray(data.candidate_run_ids) ? data.candidate_run_ids.filter((runId) => typeof runId === "string") : [];
    const candidateCount = Number(data.candidate_count) || 0;
    if (dryRun && (candidateRunIdsResponse.length !== candidateCount || new Set(candidateRunIdsResponse).size !== candidateRunIdsResponse.length)) {
      throw new Error("History cleanup preview did not identify its candidates safely.");
    }
    const response = {
      candidate_count: candidateCount,
      candidate_run_ids: candidateRunIdsResponse,
      dry_run: Boolean(data.dry_run),
      removed_count: Number(data.removed_count) || 0,
      removed_run_ids: Array.isArray(data.removed_run_ids) ? data.removed_run_ids.filter((runId) => typeof runId === "string") : [],
      skipped_changed: Number(data.skipped_changed) || 0,
      skipped_unknown: Number(data.skipped_unknown) || 0
    };
    if (!dryRun && response.removed_run_ids.length > 0) {
      this.removeRuns(response.removed_run_ids);
    }
    return response;
  }
  async cancelSubmission(submissionId, runId) {
    const snapshot = await cancelWorkflowSubmission(submissionId);
    if (snapshot.run_id && snapshot.run_id !== runId) {
      throw new Error("The submission is bound to a different workflow run.");
    }
    const existing = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").get(runId);
    const status = ["pending", "running", "succeeded", "failed", "cancelled", "timeout"].includes(snapshot.status) ? snapshot.status : (existing == null ? void 0 : existing.status) ?? "pending";
    const updated = {
      ...existing ?? { run_id: runId, seq: 0 },
      cancel_requested: snapshot.cancel_requested,
      run_id: runId,
      status,
      submission_id: snapshot.submission_id,
      updated_at: snapshot.updated_at
    };
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").set(runId, updated);
    this.emitUpdate();
    ensureActiveRun(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f"));
    return snapshot;
  }
  processSnapshotArray(arr) {
    const activeSet = /* @__PURE__ */ new Set();
    const missingWorkflowIds = /* @__PURE__ */ new Set();
    const runsMissingWorkflowId = [];
    let changed = false;
    for (const s of arr) {
      if (!s || !s.run_id || typeof s.status === "undefined" || s.status === null) {
        console.warn("processSnapshotArray: ignoring invalid snapshot entry", s);
        continue;
      }
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_REMOVED_RUN_IDS, "f").has(s.run_id)) {
        continue;
      }
      activeSet.add(s.run_id);
      const last = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").get(s.run_id) ?? -1;
      if (s.seq < last)
        continue;
      if (s.seq === last && __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").has(s.run_id)) {
        this.upsertRun(s);
        continue;
      }
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").set(s.run_id, s.seq);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").set(s.run_id, s);
      changed = true;
      if (s.workflow_id && !__classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f").has(s.workflow_id)) {
        missingWorkflowIds.add(s.workflow_id);
      }
      if (!s.workflow_id) {
        runsMissingWorkflowId.push(s.run_id);
      }
    }
    if (changed) {
      this.emitUpdate();
    }
    (async () => {
      try {
        const toReconcile = [];
        for (const [id, rec] of __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").entries()) {
          if (["pending", "running"].includes(rec.status) && !activeSet.has(id)) {
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
      const resp = await fetch(`${API_ROOT}/workflow-runner/runs?status=pending,running,succeeded,failed,cancelled,timeout&owner=me&summary=1&limit=${__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS_QUERY_LIMIT, "f")}`, { credentials: "include" });
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
          __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f").delete(localId);
          __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f").delete(localId);
          __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LOADED_DETAILS, "f").delete(localId);
        }
      }
      this.emitUpdate();
    } catch (e) {
      debugLog("coldLoadRuns error", "warning", e);
    }
  }
  //#region SSE Connection
  async start() {
    __classPrivateFieldSet$1(this, _WorkflowRunnerClient_STOPPED, false, "f");
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f") || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").connecting) {
      return;
    }
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").connecting = true;
    const cachedIds = this.loadCacheIds();
    if (cachedIds.length > 0) {
      this.seedPlaceholders(cachedIds);
    }
    await this.coldLoadRuns();
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STOPPED, "f")) {
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").connecting = false;
      return;
    }
    this.openSse();
  }
  openSse() {
    const url = `${API_ROOT}/workflow-runner/events?summary=1`;
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
              submission_id: payload.submission_id,
              cancel_requested: payload.cancel_requested,
              workflow_id: payload.workflow_id,
              status: payload.status,
              seq: payload.seq ?? 0,
              owner_id: payload.owner_id,
              created_at: payload.created_at,
              updated_at: payload.updated_at,
              inputs: payload.inputs,
              outputs: payload.outputs,
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
      var _a2;
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STOPPED, "f")) {
        (_a2 = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f")) == null ? void 0 : _a2.close();
        __classPrivateFieldSet$1(this, _WorkflowRunnerClient_ES, null, "f");
        return;
      }
      __classPrivateFieldSet$1(this, _WorkflowRunnerClient_BACKOFF_MS, __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INITIAL_BACKOFF_MS, "f"), "f");
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, "f")) {
        clearTimeout(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, "f"));
        __classPrivateFieldSet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, null, "f");
      }
      this.stopPollingFallback();
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
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STOPPED, "f")) {
        return;
      }
      this.startPollingFallback();
      if (!__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, "f")) {
        const delay = this.backoffWithJitter();
        __classPrivateFieldSet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, setTimeout(() => {
          __classPrivateFieldSet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, null, "f");
          if (!__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STOPPED, "f")) {
            void this.start();
          }
        }, delay), "f");
      }
    };
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").addEventListener(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_EVENT_RUN, "f"), (e) => {
      try {
        const payload = JSON.parse(e.data);
        this.applyEvent({
          run_id: payload.run_id,
          submission_id: payload.submission_id,
          cancel_requested: payload.cancel_requested,
          workflow_id: payload.workflow_id,
          status: payload.status,
          seq: payload.seq ?? 0,
          owner_id: payload.owner_id,
          created_at: payload.created_at,
          updated_at: payload.updated_at,
          inputs: payload.inputs,
          outputs: payload.outputs,
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
          submission_id: payload.submission_id,
          cancel_requested: payload.cancel_requested,
          workflow_id: payload.workflow_id,
          status: payload.status,
          seq: payload.seq ?? 0,
          owner_id: payload.owner_id,
          created_at: payload.created_at,
          updated_at: payload.updated_at,
          inputs: payload.inputs,
          outputs: payload.outputs,
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
              submission_id: payload2.submission_id,
              cancel_requested: payload2.cancel_requested,
              workflow_id: payload2.workflow_id,
              status: payload2.status,
              seq: payload2.seq ?? 0,
              owner_id: payload2.owner_id,
              created_at: payload2.created_at,
              updated_at: payload2.updated_at,
              inputs: payload2.inputs,
              outputs: payload2.outputs,
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
    __classPrivateFieldSet$1(this, _WorkflowRunnerClient_STOPPED, true, "f");
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").connecting = false;
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f")) {
      try {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f").close();
      } catch {
      }
      __classPrivateFieldSet$1(this, _WorkflowRunnerClient_ES, null, "f");
    }
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, "f")) {
      clearTimeout(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, "f"));
      __classPrivateFieldSet$1(this, _WorkflowRunnerClient_RECONNECT_TIMER, null, "f");
    }
    this.stopPollingFallback();
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f").clear();
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_DETAILS, "f").clear();
    __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LOADED_DETAILS, "f").clear();
    __classPrivateFieldSet$1(this, _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID, null, "f");
  }
  stopPollingFallback() {
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer) {
      clearTimeout(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer);
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer = null;
    }
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController) {
      try {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController.abort();
      } catch {
      }
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController = null;
    }
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
    self.loadRunDetail = this.loadRunDetail.bind(this);
    self.releaseRunDetail = this.releaseRunDetail.bind(this);
    self.pollActiveRuns = this.pollActiveRuns.bind(this);
    self.coldLoadRuns = this.coldLoadRuns.bind(this);
    self.processSnapshotArray = this.processSnapshotArray.bind(this);
    self.saveCache = this.saveCache.bind(this);
    self.loadCacheIds = this.loadCacheIds.bind(this);
    self.seedPlaceholders = this.seedPlaceholders.bind(this);
    self.start = this.start.bind(this);
    self.stop = this.stop.bind(this);
    self.startPollingFallback = this.startPollingFallback.bind(this);
    self.backoffWithJitter = this.backoffWithJitter.bind(this);
    self.fetchWorkflowNames = this.fetchWorkflowNames.bind(this);
    self.setWorkflowNames = this.setWorkflowNames.bind(this);
    self.lastSeq = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_LAST_SEQ, "f");
    self.runs = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS, "f");
    self.inflightReconciles = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_RECONCILES, "f");
    self.inflightDetails = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_INFLIGHT_DETAILS, "f");
    self.processingSnapshot = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STATE, "f").processingSnapshot;
    self.cacheKey = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_CACHE_KEY, "f");
    self.workflowNames = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_WORKFLOW_CACHE, "f");
    self.store = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_STORE, "f");
    return this;
  }
  startPollingFallback() {
    if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STOPPED, "f") || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f") || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController) {
      return;
    }
    void this.pollActiveRuns().finally(() => {
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_STOPPED, "f") || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_ES, "f") || __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer) {
        return;
      }
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer = setTimeout(() => {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").timer = null;
        this.startPollingFallback();
      }, __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING_INTERVAL_MS, "f"));
    });
  }
  async pollActiveRuns() {
    let ac = null;
    try {
      if (__classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController) {
        return;
      }
      ac = new AbortController();
      __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController = ac;
      const resp = await fetch(`${API_ROOT}/workflow-runner/runs?status=pending,running&owner=me&summary=1&limit=${__classPrivateFieldGet$1(this, _WorkflowRunnerClient_RUNS_QUERY_LIMIT, "f")}`, { signal: ac.signal, credentials: "include" });
      if (!resp.ok) {
        return;
      }
      const data = await resp.json();
      const arr = data.runs || [];
      this.processSnapshotArray(arr);
    } catch (e) {
      if (e && (e.name === "AbortError" || e.code === "ABORT_ERR") || e instanceof DOMException && e.name === "AbortError") ;
      else {
        debugLog("pollActiveRuns error", "warning", e);
      }
    } finally {
      if (ac && __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController === ac) {
        __classPrivateFieldGet$1(this, _WorkflowRunnerClient_POLLING, "f").abortController = null;
      }
    }
  }
  backoffWithJitter() {
    const base = __classPrivateFieldGet$1(this, _WorkflowRunnerClient_BACKOFF_MS, "f");
    const jitterFactor = 0.5 + Math.random() * 0.5;
    __classPrivateFieldSet$1(this, _WorkflowRunnerClient_BACKOFF_MS, Math.min(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_MAX_BACKOFF_MS, "f"), Math.max(__classPrivateFieldGet$1(this, _WorkflowRunnerClient_INITIAL_BACKOFF_MS, "f"), base * 2)), "f");
    return Math.floor(base * jitterFactor);
  }
}
_WorkflowRunnerClient_ES = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_STORE = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_WORKFLOW_NAMES = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_CACHE_KEY = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_CACHE_EXPIRY_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_INITIAL_BACKOFF_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_MAX_BACKOFF_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_POLLING_INTERVAL_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_RUNS_QUERY_LIMIT = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_EVENT_RUN = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_EVENT_QUEUE = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_LAST_SEQ = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_RUNS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_WORKFLOW_CACHE = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_STATE = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_POLLING = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_BACKOFF_MS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_RECONNECT_TIMER = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_STOPPED = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_INFLIGHT_RECONCILES = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_INFLIGHT_DETAILS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_LOADED_DETAILS = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_OPEN_DETAIL_RUN_ID = /* @__PURE__ */ new WeakMap(), _WorkflowRunnerClient_REMOVED_RUN_IDS = /* @__PURE__ */ new WeakMap();
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
    var _a2;
    const { workflows } = store.getState();
    return Boolean((_a2 = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a2.some((node) => node.id === workflowId));
  };
  const updateRouteFromState = (precomputed) => {
    if (isApplyingRoute || pendingRoute) {
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
  cancelInFlightRunId: null,
  current: { status: "idle", message: "", id: null },
  currentRunId: null,
  inputStatuses: {},
  inputPrefillRunId: null,
  submissionInFlightId: null,
  isDebug: false,
  manager: null,
  mutate: {
    cancelInFlightRun: INIT_CB,
    isDebug: INIT_CB,
    manager: INIT_CB,
    inputStatus: INIT_CB,
    inputPrefillRun: INIT_CB,
    submissionInFlight: INIT_CB,
    queuedJobs: INIT_CB,
    notifications: {
      add: INIT_CB,
      removeById: INIT_CB,
      removeByIndex: INIT_CB
    },
    results: INIT_CB,
    runs: {
      clear: INIT_CB,
      removeMany: INIT_CB,
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
const compareWorkflowRuns = (a, b) => {
  if (a.createdAt !== b.createdAt) {
    return b.createdAt - a.createdAt;
  }
  return a.runId < b.runId ? -1 : a.runId > b.runId ? 1 : 0;
};
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
    cancelInFlightRun: (runId) => applyMutation((draft) => {
      draft.cancelInFlightRunId = runId;
    }),
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
    inputPrefillRun: (runId) => applyMutation((draft) => {
      draft.inputPrefillRunId = runId;
    }),
    submissionInFlight: (submissionId) => applyMutation((draft) => {
      draft.submissionInFlightId = submissionId;
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
    queuedJobs: (count) => {
      if (state.queuedJobs === count) {
        return;
      }
      applyMutation((draft) => {
        draft.queuedJobs = count;
      });
    },
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
      removeMany: (runIds) => {
        if (runIds.length === 0) {
          return;
        }
        const removed = new Set(runIds);
        applyMutation((draft) => {
          draft.runs = draft.runs.filter((run) => !removed.has(run.runId));
          if (draft.currentRunId && removed.has(draft.currentRunId)) {
            draft.currentRunId = null;
          }
          if (draft.cancelInFlightRunId && removed.has(draft.cancelInFlightRunId)) {
            draft.cancelInFlightRunId = null;
          }
          if (draft.selectedRunId && removed.has(draft.selectedRunId)) {
            draft.selectedRunId = null;
          }
          if (draft.inputPrefillRunId && removed.has(draft.inputPrefillRunId)) {
            draft.inputPrefillRunId = null;
          }
        });
      },
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
            artifacts: entry.artifacts !== void 0 ? entry.artifacts : current.artifacts,
            createdAt,
            updatedAt: now,
            status: entry.status ?? current.status,
            submissionId: entry.submissionId !== void 0 ? entry.submissionId : current.submissionId,
            cancelRequested: entry.cancelRequested !== void 0 ? entry.cancelRequested : current.cancelRequested,
            workflowId: entry.workflowId ?? current.workflowId,
            workflowName: entry.workflowName ?? current.workflowName,
            inputs: entry.inputs ?? current.inputs,
            outputs: entry.outputs ?? current.outputs,
            error: entry.error ?? current.error ?? null,
            httpStatus: entry.httpStatus !== void 0 ? entry.httpStatus : current.httpStatus,
            resultPayload: entry.resultPayload !== void 0 ? entry.resultPayload : current.resultPayload
          };
          draft.runs = nextRuns.sort(compareWorkflowRuns);
        } else {
          const createdAt = entry.createdAt ?? now;
          const nextRuns = draft.runs.filter((run) => run.runId !== entry.runId);
          draft.runs = [
            {
              runId: entry.runId,
              artifacts: entry.artifacts ?? [],
              submissionId: entry.submissionId ?? null,
              cancelRequested: entry.cancelRequested ?? false,
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
          ].sort(compareWorkflowRuns);
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
    // Workflow navigation must not surrender control of an owned active
    // run; the floating action remains Stop until that run is terminal.
    currentRunId: state.currentRunId,
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
      var _a2;
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
      const firstWorkflow = (_a2 = workflows.nodes) == null ? void 0 : _a2[0];
      const route = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").getPendingRoute();
      const shouldSelectDefault = !route || !route.workflowId && (route.view === "workflow" || route.view === "history") || route.view === "run" && !route.workflowId;
      if (shouldSelectDefault && (firstWorkflow == null ? void 0 : firstWorkflow.id)) {
        state2.mutate.workflow(firstWorkflow.id);
      }
      if ((route == null ? void 0 : route.view) !== "run") {
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").applyPendingRouteIfNeeded();
      }
    });
    this.runs = {
      all: () => {
        return [...__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().runs];
      },
      cancel: async (runId) => {
        const run = this.runs.get(runId);
        if (!(run == null ? void 0 : run.submissionId) || !["pending", "running"].includes(run.status)) {
          return;
        }
        await __classPrivateFieldGet(this, _LfWorkflowRunnerManager_CLIENT, "f").cancelSubmission(run.submissionId, run.runId);
      },
      get: (runId) => {
        const { runs } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
        return runs.find((run) => run.runId === runId) || null;
      },
      pruneMissingArtifacts: (dryRun, candidateRunIds) => __classPrivateFieldGet(this, _LfWorkflowRunnerManager_CLIENT, "f").pruneMissingArtifacts(dryRun, candidateRunIds),
      remix: (runId) => {
        const run = this.runs.get(runId);
        const state2 = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
        if (!(run == null ? void 0 : run.workflowId) || !run.inputs || Object.keys(run.inputs).length === 0) {
          return;
        }
        const workflowExists = state2.workflows.nodes.some((node) => node.id === run.workflowId);
        if (!workflowExists) {
          return;
        }
        clearWorkflowSessionDraft(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), run.workflowId);
        if (state2.current.id !== run.workflowId) {
          state2.mutate.workflow(run.workflowId);
        }
        state2.mutate.inputPrefillRun(run.runId);
        changeView(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), "workflow", { clearResults: true });
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
            clearResults: true
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
        var _a2;
        const workflow = this.workflow.current();
        const section = (_a2 = workflow == null ? void 0 : workflow.children) == null ? void 0 : _a2.find((child) => child.id.endsWith(`:${type}s`));
        return (section == null ? void 0 : section.cells) || {};
      },
      current: () => {
        var _a2;
        const { current, workflows } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
        return ((_a2 = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a2.find((node) => node.id === current.id)) || null;
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
      cancelWorkflow: () => workflowCancellationDispatcher(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f")),
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
    }).then(async () => {
      setStatus$1(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"), "idle", IDLE_WORKFLOWS_LOADED);
      await __classPrivateFieldGet(this, _LfWorkflowRunnerManager_CLIENT, "f").start();
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").applyPendingRouteIfNeeded();
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
  var _a2, _b2, _c2;
  const st = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
  let latestState = st;
  let lastCurrentMessage = st.current.message;
  let lastCurrentStatus = st.current.status;
  let lastDebug = st.isDebug;
  let lastId = st.current.id;
  let lastInputStatuses = st.inputStatuses;
  let lastNotificationsCount = ((_a2 = st.notifications) == null ? void 0 : _a2.length) ?? 0;
  let lastQueued = st.queuedJobs ?? -1;
  let lastResults = st.results;
  let lastRunId = st.currentRunId;
  let lastRunsRef = st.runs;
  let lastCancelInFlightRunId = st.cancelInFlightRunId;
  let lastSubmissionInFlightId = st.submissionInFlightId;
  let lastSelectedRunId = st.selectedRunId;
  let lastView = st.view;
  let lastWorkflowsCount = ((_c2 = (_b2 = st.workflows) == null ? void 0 : _b2.nodes) == null ? void 0 : _c2.length) ?? 0;
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
    var _a3, _b3;
    latestState = state;
    const { current, isDebug, queuedJobs, workflows } = state;
    const { message, status } = current;
    if (state.currentRunId !== lastRunId) {
      needs.actionButton = true;
      needs.header = true;
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
      needs.actionButton = true;
      needs.header = true;
      needs.main = true;
      lastRunsRef = state.runs;
    }
    if (state.cancelInFlightRunId !== lastCancelInFlightRunId || state.submissionInFlightId !== lastSubmissionInFlightId) {
      needs.actionButton = true;
      lastCancelInFlightRunId = state.cancelInFlightRunId;
      lastSubmissionInFlightId = state.submissionInFlightId;
    }
    if (state.selectedRunId !== lastSelectedRunId) {
      needs.main = true;
      const previousRunId = lastSelectedRunId;
      lastSelectedRunId = state.selectedRunId;
      if (previousRunId) {
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_CLIENT, "f").releaseRunDetail(previousRunId);
      }
      if (state.selectedRunId) {
        void __classPrivateFieldGet(this, _LfWorkflowRunnerManager_CLIENT, "f").loadRunDetail(state.selectedRunId);
      }
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
    if (((_a3 = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a3.length) !== lastWorkflowsCount) {
      needs.drawer = true;
      lastWorkflowsCount = ((_b3 = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _b3.length) ?? 0;
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
