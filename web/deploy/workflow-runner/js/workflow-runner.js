import { g as getLfFramework } from "../../js/lf-widgets-6WpDY9VV.js";
const apiBase = "/api";
const apiRoutePrefix = "/lf-nodes";
const staticPaths = { "assets": "/lf-nodes/static/assets/" };
const theme = "dark";
const runnerConfig = {
  apiBase,
  apiRoutePrefix,
  staticPaths,
  theme
};
const API_BASE = runnerConfig.apiBase;
const API_ROUTE_PREFIX = runnerConfig.apiRoutePrefix;
const API_ROOT = `${API_BASE}${API_ROUTE_PREFIX}`;
const DEFAULT_STATUS_MESSAGES = {
  ready: "Ready.",
  running: "Running...",
  error: "An error occurred while running the workflow."
};
const DEFAULT_THEME = runnerConfig.theme;
const STATIC_ASSETS_PATH = runnerConfig.staticPaths.assets;
const buildApiUrl = (path) => `${API_ROOT}${path.startsWith("/") ? path : `/${path}`}`;
const buildAssetsUrl = (origin = window.location.origin) => `${origin}${API_BASE}${STATIC_ASSETS_PATH.startsWith("/") ? STATIC_ASSETS_PATH : `/${STATIC_ASSETS_PATH}`}`;
const ROOT_CLASS$5 = "dev-panel";
const CARD_CLASS = `${ROOT_CLASS$5}__card`;
const buildDebugDataset = () => {
  const framework = getLfFramework();
  const enabled = framework.debug.isEnabled();
  return {
    nodes: [
      {
        id: "workflow-runner-debug",
        cells: {
          lfToggle: {
            shape: "toggle",
            lfValue: enabled,
            value: enabled
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
const createDevPanel = () => {
  let container = null;
  let card = null;
  let mountedState = null;
  const mount = (state) => {
    var _a, _b;
    if (container) {
      return;
    }
    mountedState = state;
    container = document.createElement("div");
    container.className = ROOT_CLASS$5;
    container.dataset.open = "false";
    container.setAttribute("aria-hidden", "true");
    card = document.createElement("lf-card");
    card.className = CARD_CLASS;
    card.lfLayout = "debug";
    card.lfDataset = buildDebugDataset();
    const body = ((_b = (_a = state.ui.layout._root) == null ? void 0 : _a.ownerDocument) == null ? void 0 : _b.body) ?? document.body;
    container.appendChild(card);
    body.appendChild(container);
    state.mutate.ui((ui) => {
      ui.layout.dev._root = container;
      ui.layout.dev.card = card;
    });
  };
  const render = (state) => {
    if (!container) {
      return;
    }
    container.setAttribute("aria-hidden", String(!state.isDebug));
  };
  const destroy = () => {
    if (container == null ? void 0 : container.isConnected) {
      container.remove();
    }
    if (mountedState) {
      mountedState.mutate.ui((ui) => {
        ui.layout.dev._root = null;
        ui.layout.dev.card = null;
      });
    }
    container = null;
    card = null;
    mountedState = null;
  };
  return {
    mount,
    render,
    destroy
  };
};
const executeWorkflowButton = (e, state) => {
  var _a;
  const { eventType } = e.detail;
  switch (eventType) {
    case "click":
      (_a = state.manager) == null ? void 0 : _a.runWorkflow();
      break;
    default:
      return;
  }
};
const ROOT_CLASS$4 = "action-button-section";
const createActionButtonSection = () => {
  let element = null;
  let lastState = null;
  const mount = (state) => {
    var _a;
    lastState = state;
    const { ui } = state;
    element = document.createElement("lf-button");
    element.className = ROOT_CLASS$4;
    element.lfIcon = "send";
    element.lfStyling = "floating";
    element.title = "Run current workflow";
    element.addEventListener("lf-button-event", (e) => executeWorkflowButton(e, state));
    state.mutate.ui((uiState) => {
      uiState.layout.actionButton._root = element;
    });
    (_a = ui.layout._root) == null ? void 0 : _a.appendChild(element);
  };
  const render = () => {
  };
  const destroy = () => {
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.mutate.ui((uiState) => {
        uiState.layout.actionButton._root = null;
      });
    }
    element = null;
    lastState = null;
  };
  return {
    mount,
    render,
    destroy
  };
};
const DEBUG_MESSAGES = {
  DRAWER_DESTROYED: "Drawer section destroyed.",
  DRAWER_MOUNTED: "Drawer section mounted.",
  DRAWER_UPDATED: "Drawer dataset refreshed.",
  INPUTS_COLLECTED: "Collected workflow inputs.",
  MAIN_DESTROYED: "Main content destroyed.",
  MAIN_MOUNTED: "Main content mounted.",
  STATUS_UPDATED: "Workflow status updated.",
  WORKFLOW_COMPLETED: "Workflow execution completed.",
  WORKFLOW_DISPATCHING: "Dispatching workflow execution.",
  WORKFLOW_LAYOUT_DESTROYED: "Workflow layout destroyed.",
  WORKFLOW_LAYOUT_MOUNTED: "Workflow layout mounted.",
  WORKFLOW_INPUT_FLAGGED: "Workflow input flagged.",
  WORKFLOW_INPUTS_CLEARED: "Workflow inputs cleared.",
  WORKFLOW_INPUTS_RENDERED: "Workflow inputs rendered.",
  WORKFLOW_NOT_SELECTED: "No workflow selected.",
  WORKFLOW_RESULTS_CLEARED: "Workflow results cleared.",
  WORKFLOW_RESULTS_RENDERED: "Workflow results rendered.",
  WORKFLOWS_LOAD_FAILED: "Failed to load workflows.",
  WORKFLOWS_LOADED: "Workflow definitions loaded."
};
const STATUS_MESSAGES = {
  FILE_PROCESSING: "File uploaded, processing...",
  LOADING_WORKFLOWS: "Loading workflows...",
  SUBMITTING_WORKFLOW: "Submitting workflow...",
  UPLOADING_FILE: "Uploading file..."
};
const formatContext = (context) => {
  if (context === void 0 || context === null) {
    return null;
  }
  if (typeof context === "string") {
    return context;
  }
  try {
    const serialized = JSON.stringify(context, null, 2);
    return serialized ? serialized : null;
  } catch {
    return String(context);
  }
};
const debugLog = (message, category = "informational", context) => {
  try {
    const { debug } = getLfFramework();
    const { logs } = debug;
    const formattedContext = formatContext(context);
    const payload = formattedContext ? `${message}

${formattedContext}` : message;
    logs.new(debug, payload, category);
  } catch {
  }
};
const ROOT_CLASS$3 = "drawer-section";
const _createDataset = (workflows) => {
  var _a;
  const clone = JSON.parse(JSON.stringify(workflows));
  (_a = clone.nodes) == null ? void 0 : _a.forEach((child) => {
    child.children = void 0;
  });
  const dataset = {
    nodes: [{ children: clone.nodes, id: "workflows", value: "Workflows" }]
  };
  return dataset;
};
const _container$1 = (state) => {
  const container = document.createElement("div");
  container.className = `${ROOT_CLASS$3}__container`;
  container.slot = "content";
  container.appendChild(_tree(state));
  return container;
};
const _tree = (state) => {
  const { manager } = state;
  const tree = document.createElement("lf-tree");
  tree.className = `${ROOT_CLASS$3}__tree`;
  tree.lfAccordionLayout = true;
  tree.addEventListener("lf-tree-event", (e) => {
    const { eventType, node } = e.detail;
    switch (eventType) {
      case "click":
        if (!manager) {
          return;
        }
        const isLeaf = !node.children || node.children.length === 0;
        if (!isLeaf) {
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
const createDrawerSection = () => {
  const { DRAWER_DESTROYED, DRAWER_MOUNTED, DRAWER_UPDATED } = DEBUG_MESSAGES;
  let element = null;
  let lastState = null;
  const mount = (state) => {
    var _a, _b, _c;
    lastState = state;
    const { ui } = state;
    element = document.createElement("lf-drawer");
    element.className = ROOT_CLASS$3;
    element.lfDisplay = "slide";
    state.mutate.ui((ui2) => {
      ui2.layout.drawer._root = element;
    });
    element.appendChild(_container$1(state));
    (_a = ui.layout._root) == null ? void 0 : _a.appendChild(element);
    debugLog(DRAWER_MOUNTED, "informational", {
      workflowCount: ((_c = (_b = state.workflows) == null ? void 0 : _b.nodes) == null ? void 0 : _c.length) ?? 0
    });
  };
  const render = (state) => {
    var _a, _b;
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
    if ((previousState == null ? void 0 : previousState.workflows) !== state.workflows) {
      debugLog(DRAWER_UPDATED, "informational", {
        workflowCount: ((_b = (_a = state.workflows) == null ? void 0 : _a.nodes) == null ? void 0 : _b.length) ?? 0
      });
    }
    tree.lfDataset = _createDataset(state.workflows);
  };
  const destroy = () => {
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.mutate.ui((ui) => {
        ui.layout.drawer._root = null;
        ui.layout.drawer.tree = null;
      });
      debugLog(DRAWER_DESTROYED, "informational", {});
    }
    element = null;
    lastState = null;
  };
  return {
    mount,
    render,
    destroy
  };
};
const isObject = (v) => v !== null && typeof v === "object";
const isString = (v) => typeof v === "string";
const isStringArray = (v) => Array.isArray(v) && v.every((e) => typeof e === "string");
const isWorkflowAPIUploadPayload = (v) => {
  if (!isObject(v)) {
    return false;
  }
  if (!("detail" in v) || !isString(v.detail)) {
    return false;
  }
  if ("paths" in v && !(isStringArray(v.paths) || v.paths === void 0)) {
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
const normalize_description = (description) => {
  if (!description) {
    return "";
  } else if (Array.isArray(description) && description.length > 1) {
    return description.join("\n");
  } else if (Array.isArray(description) && description.length === 1) {
    return description[0];
  } else if (typeof description === "string") {
    return description;
  } else {
    return "";
  }
};
const clearChildren = (element) => {
  if (!element) {
    return;
  }
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
};
const _chooseComponentForResult = (key, props) => {
  const el = document.createElement("div");
  const { _description } = props;
  if (_description) {
    const desc = document.createElement("div");
    desc.innerHTML = normalize_description(_description);
    el.appendChild(desc);
  }
  switch (key) {
    case "masonry":
      const masonry = createComponent.masonry(props);
      el.appendChild(masonry);
      break;
    default:
    case "code":
      const code = createComponent.code(props);
      el.appendChild(code);
      break;
  }
  return el;
};
const _setProps = (comp, element, props) => {
  if (!props) {
    return;
  }
  const { sanitizeProps } = getLfFramework();
  const hasSlots = props._slotmap && Object.keys(props._slotmap).length > 0;
  if (hasSlots) {
    _setSlots(comp, element, props);
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
const _setSlots = (_comp, element, props) => {
  for (const slotName in props._slotmap) {
    const slotHtml = props._slotmap[slotName];
    const wrapper = document.createElement("div");
    wrapper.innerHTML = slotHtml;
    wrapper.setAttribute("slot", slotName);
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
  code: (props) => {
    const comp = document.createElement("lf-code");
    _setProps("LfCode", comp, props);
    return comp;
  },
  masonry: (props) => {
    const comp = document.createElement("lf-masonry");
    _setProps("LfMasonry", comp, props);
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
  switch (cell.shape) {
    case "toggle": {
      return createComponent.toggle(sanitizeProps(cell, "LfToggle"));
    }
    case "upload": {
      return createComponent.upload(sanitizeProps(cell, "LfUpload"));
    }
    default:
    case "textfield": {
      return createComponent.textfield(sanitizeProps(cell, "LfTextfield"));
    }
  }
};
const createOutputComponent = (descriptor) => {
  if (!descriptor) {
    const fallback = document.createElement("pre");
    fallback.textContent = "No output available.";
    return fallback;
  }
  const key = descriptor.shape === "masonry" ? "masonry" : "code";
  const props = descriptor.props || {};
  return _chooseComponentForResult(key, props);
};
const ROOT_CLASS$2 = "header-section";
const _container = () => {
  const container = document.createElement("div");
  container.className = `${ROOT_CLASS$2}__container`;
  container.slot = "content";
  return container;
};
const _drawerToggle = (state) => {
  const { theme: theme2 } = getLfFramework();
  const { get } = theme2;
  const lfIcon = get.icon("menu2");
  const props = {
    lfAriaLabel: "Toggle drawer",
    lfIcon,
    lfStyling: "icon"
  };
  const drawerToggle = createComponent.button(props);
  drawerToggle.className = `${ROOT_CLASS$2}__drawer-toggle`;
  drawerToggle.addEventListener("lf-button-event", (e) => {
    const { eventType } = e.detail;
    switch (eventType) {
      case "click":
        state.ui.layout.drawer._root.toggle();
        break;
    }
  });
  return drawerToggle;
};
const _debugToggle = (state) => {
  const { theme: theme2 } = getLfFramework();
  const { get } = theme2;
  const lfIcon = get.icon("code");
  const props = {
    lfAriaLabel: "Toggle developer console",
    lfIcon,
    lfStyling: "icon"
  };
  const debugToggle = createComponent.button(props);
  debugToggle.lfUiState = "info";
  debugToggle.className = `${ROOT_CLASS$2}__debug-toggle`;
  debugToggle.addEventListener("lf-button-event", (e) => {
    var _a;
    const { eventType } = e.detail;
    switch (eventType) {
      case "click":
        (_a = state.manager) == null ? void 0 : _a.toggleDebug();
        break;
    }
  });
  return debugToggle;
};
const createHeaderSection = () => {
  let element = null;
  let lastState = null;
  const mount = (state) => {
    var _a;
    lastState = state;
    const { ui } = state;
    element = document.createElement("lf-header");
    element.className = ROOT_CLASS$2;
    const container = _container();
    const drawerToggle = _drawerToggle(state);
    const debugToggle = _debugToggle(state);
    state.mutate.ui((uiState) => {
      uiState.layout.header.drawerToggle = drawerToggle;
      uiState.layout.header.debugToggle = debugToggle;
    });
    element.appendChild(container);
    container.appendChild(drawerToggle);
    container.appendChild(debugToggle);
    state.mutate.ui((uiState) => {
      uiState.layout.header._root = element;
    });
    (_a = ui.layout._root) == null ? void 0 : _a.appendChild(element);
  };
  const render = (state) => {
    const { isDebug } = state;
    const debugToggle = state.ui.layout.header.debugToggle;
    if (debugToggle) {
      debugToggle.lfUiState = isDebug ? "secondary" : "info";
      debugToggle.title = isDebug ? "Hide developer console" : "Show developer console";
    }
  };
  const destroy = () => {
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.mutate.ui((uiState) => {
        uiState.layout.header._root = null;
        uiState.layout.header.drawerToggle = null;
        uiState.layout.header.debugToggle = null;
        uiState.layout.header.themeSwitch = null;
      });
    }
    element = null;
    lastState = null;
  };
  return {
    mount,
    render,
    destroy
  };
};
const ROOT_CLASS$1 = "main-section";
const createMainSection = () => {
  const { MAIN_DESTROYED, MAIN_MOUNTED } = DEBUG_MESSAGES;
  let element = null;
  let lastState = null;
  const mount = (state) => {
    var _a;
    lastState = state;
    const { ui } = state;
    element = document.createElement("main");
    element.className = ROOT_CLASS$1;
    state.mutate.ui((uiState) => {
      uiState.layout.main._root = element;
    });
    (_a = ui.layout._root) == null ? void 0 : _a.appendChild(element);
    debugLog(MAIN_MOUNTED, "informational", {});
  };
  const render = () => {
  };
  const destroy = () => {
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.mutate.ui((uiState) => {
        uiState.layout.main._root = null;
      });
      debugLog(MAIN_DESTROYED, "informational", {});
    }
    element = null;
    lastState = null;
  };
  return {
    mount,
    render,
    destroy
  };
};
const WORKFLOW_TEXT = "Select a workflow";
const ROOT_CLASS = "workflow-section";
const getCurrentWorkflow = (state) => {
  var _a;
  const { current, workflows } = state;
  return ((_a = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a.find((node) => node.id === current.id)) || null;
};
const getWorkflowSection = (workflow, section) => {
  var _a;
  return ((_a = workflow == null ? void 0 : workflow.children) == null ? void 0 : _a.find((child) => {
    var _a2;
    return ((_a2 = child == null ? void 0 : child.props) == null ? void 0 : _a2.lfSection) === section;
  })) || null;
};
const getWorkflowInputCells = (workflow) => {
  const inputsSection = getWorkflowSection(workflow, "inputs");
  return (inputsSection == null ? void 0 : inputsSection.cells) || {};
};
const getWorkflowOutputCells = (workflow) => {
  const outputsSection = getWorkflowSection(workflow, "outputs");
  return (outputsSection == null ? void 0 : outputsSection.cells) || {};
};
const groupOutputDefinitionsByNode = (workflow) => {
  const outputCells = getWorkflowOutputCells(workflow);
  const grouped = {};
  for (const key in outputCells) {
    if (!Object.prototype.hasOwnProperty.call(outputCells, key)) {
      continue;
    }
    const cell = outputCells[key];
    const nodeId = (cell == null ? void 0 : cell.lfNodeId) || (cell == null ? void 0 : cell.nodeId) || (cell == null ? void 0 : cell.node_id);
    if (!nodeId) {
      continue;
    }
    if (!grouped[nodeId]) {
      grouped[nodeId] = [];
    }
    grouped[nodeId].push(cell);
  }
  return grouped;
};
const extractDefinitionProps = (definition) => {
  if (!definition) {
    return {};
  }
  const reservedKeys = /* @__PURE__ */ new Set(["id", "value", "shape", "title", "lfNodeId"]);
  const props = {};
  for (const key in definition) {
    if (!Object.prototype.hasOwnProperty.call(definition, key)) {
      continue;
    }
    if (!reservedKeys.has(key)) {
      props[key] = definition[key];
    }
  }
  return props;
};
const normalizeNodeOutputs = (payload) => {
  if (!payload) {
    return [];
  }
  const raw = payload.lf_output;
  if (!raw) {
    return [];
  }
  return Array.isArray(raw) ? raw : [raw];
};
const getWorkflowDescription = (state) => {
  const workflow = getCurrentWorkflow(state);
  return (workflow == null ? void 0 : workflow.description) || "";
};
const getWorkflowTitle = (state) => {
  const workflow = getCurrentWorkflow(state);
  const str = typeof (workflow == null ? void 0 : workflow.value) === "string" ? workflow.value : String((workflow == null ? void 0 : workflow.value) || "");
  return str || WORKFLOW_TEXT;
};
const createFieldWrapper = () => {
  const fieldWrapper = document.createElement("div");
  fieldWrapper.className = `${ROOT_CLASS}__field`;
  return fieldWrapper;
};
const createOptionsWrapper = () => {
  const optionsWrapper = document.createElement("div");
  optionsWrapper.className = `${ROOT_CLASS}__options`;
  return optionsWrapper;
};
const createResultWrapper = () => {
  const resultWrapper = document.createElement("div");
  resultWrapper.className = `${ROOT_CLASS}__result`;
  return resultWrapper;
};
const createRunButton = (state) => {
  const props = {
    lfAriaLabel: "Run workflow",
    lfLabel: "Run workflow",
    lfStretchX: true
  };
  const button = createComponent.button(props);
  button.className = `${ROOT_CLASS}__run`;
  button.addEventListener("lf-button-event", (e) => executeWorkflowButton(e, state));
  return button;
};
const createStatusWrapper = (tone = "info") => {
  const statusWrapper = document.createElement("div");
  statusWrapper.className = `${ROOT_CLASS}__status`;
  statusWrapper.dataset.tone = tone;
  return statusWrapper;
};
const createTitle = (state) => {
  const h3 = document.createElement("h3");
  h3.className = `${ROOT_CLASS}__title`;
  h3.textContent = getWorkflowTitle(state);
  return h3;
};
const createDescription = (state) => {
  const p = document.createElement("p");
  p.className = `${ROOT_CLASS}__description`;
  p.textContent = getWorkflowDescription(state);
  return p;
};
const createWorkflowSection = () => {
  const { STATUS_UPDATED, WORKFLOW_INPUT_FLAGGED, WORKFLOW_INPUTS_CLEARED, WORKFLOW_INPUTS_RENDERED, WORKFLOW_LAYOUT_DESTROYED, WORKFLOW_LAYOUT_MOUNTED, WORKFLOW_RESULTS_CLEARED, WORKFLOW_RESULTS_RENDERED } = DEBUG_MESSAGES;
  let descriptionElement = null;
  let lastMessage = null;
  let lastResultsRef = null;
  let lastStatus = null;
  let lastWorkflowId = null;
  let mountedState = null;
  let optionsWrapper = null;
  let resultWrapper = null;
  let runButton = null;
  let section = null;
  let statusWrapper = null;
  let titleElement = null;
  const mount = (state) => {
    var _a;
    mountedState = state;
    const { ui } = state;
    section = document.createElement("section");
    section.className = ROOT_CLASS;
    titleElement = createTitle(state);
    descriptionElement = createDescription(state);
    optionsWrapper = createOptionsWrapper();
    runButton = createRunButton(state);
    statusWrapper = createStatusWrapper("info");
    resultWrapper = createResultWrapper();
    state.mutate.ui((uiState) => {
      uiState.layout.main.workflow._root = section;
      uiState.layout.main.workflow.description = descriptionElement;
      uiState.layout.main.workflow.options = optionsWrapper;
      uiState.layout.main.workflow.result = resultWrapper;
      uiState.layout.main.workflow.run = runButton;
      uiState.layout.main.workflow.status = statusWrapper;
      uiState.layout.main.workflow.title = titleElement;
    });
    section.appendChild(titleElement);
    section.appendChild(descriptionElement);
    section.appendChild(optionsWrapper);
    section.appendChild(runButton);
    section.appendChild(statusWrapper);
    section.appendChild(resultWrapper);
    (_a = ui.layout.main._root) == null ? void 0 : _a.appendChild(section);
    debugLog(WORKFLOW_LAYOUT_MOUNTED, "informational", {
      workflowId: state.current.id ?? null
    });
  };
  const updateDescription = (state) => {
    const { ui } = state;
    const element = ui.layout.main.workflow.description;
    if (!element) {
      return;
    }
    element.textContent = getWorkflowDescription(state);
  };
  const updateOptions = (state) => {
    const { ui } = state;
    const element = ui.layout.main.workflow.options;
    if (!element) {
      return;
    }
    clearChildren(element);
    const workflow = getCurrentWorkflow(state);
    const cellElements = [];
    if (workflow) {
      const inputCells = getWorkflowInputCells(workflow);
      for (const key in inputCells) {
        if (!Object.prototype.hasOwnProperty.call(inputCells, key)) {
          continue;
        }
        const cell = inputCells[key];
        const wrapper = createFieldWrapper();
        const cellElement = createInputCell(cell);
        cellElements.push(cellElement);
        wrapper.appendChild(cellElement);
        element.appendChild(wrapper);
      }
    }
    state.mutate.ui((uiState) => {
      uiState.layout.main.workflow.cells = cellElements;
    });
    if (workflow && cellElements.length) {
      debugLog(WORKFLOW_INPUTS_RENDERED, "informational", {
        workflowId: state.current.id,
        cellCount: cellElements.length
      });
    } else {
      debugLog(WORKFLOW_INPUTS_CLEARED, "informational", {
        workflowId: state.current.id
      });
    }
  };
  const updateResult = (state) => {
    var _a, _b;
    const { ui } = state;
    const element = ui.layout.main.workflow.result;
    if (!element) {
      return;
    }
    const outputs = state.results || {};
    clearChildren(element);
    const nodeIds = Object.keys(outputs);
    if (nodeIds.length === 0) {
      debugLog(WORKFLOW_RESULTS_CLEARED, "informational", {
        workflowId: state.current.id
      });
      return;
    }
    const workflow = getCurrentWorkflow(state);
    const definitionsByNode = workflow ? groupOutputDefinitionsByNode(workflow) : {};
    let hasRendered = false;
    for (const nodeId of nodeIds) {
      const nodePayload = outputs[nodeId];
      const items = normalizeNodeOutputs(nodePayload);
      if (!items.length) {
        continue;
      }
      const title = document.createElement("h4");
      title.className = `${ROOT_CLASS}__result-title`;
      const definitionGroup = definitionsByNode[nodeId] || [];
      const nodeLabel = definitionGroup.length ? normalize_description(((_a = definitionGroup[0]) == null ? void 0 : _a.title) || ((_b = definitionGroup[0]) == null ? void 0 : _b.value)) : null;
      title.textContent = nodeLabel || `Node #${nodeId}`;
      element.appendChild(title);
      const grid = document.createElement("div");
      grid.className = `${ROOT_CLASS}__result-grid`;
      element.appendChild(grid);
      items.forEach((item, index) => {
        const definition = definitionGroup.find((candidate) => (candidate == null ? void 0 : candidate.id) === (item == null ? void 0 : item.id)) || definitionGroup[index];
        const mergedProps = {
          ...extractDefinitionProps(definition),
          ...(item == null ? void 0 : item.props) || {}
        };
        const descriptor = {
          ...item,
          id: (item == null ? void 0 : item.id) ?? (definition == null ? void 0 : definition.id),
          shape: (item == null ? void 0 : item.shape) || (definition == null ? void 0 : definition.shape) || "code",
          title: (item == null ? void 0 : item.title) || (definition == null ? void 0 : definition.title) || (definition == null ? void 0 : definition.value) || ((item == null ? void 0 : item.id) ? normalize_description(item.id) : `Output ${index + 1}`),
          props: mergedProps
        };
        const wrapper = document.createElement("div");
        wrapper.className = `${ROOT_CLASS}__result-item`;
        if (descriptor.title) {
          const label = document.createElement("h5");
          label.className = `${ROOT_CLASS}__result-subtitle`;
          label.textContent = String(descriptor.title);
          wrapper.appendChild(label);
        }
        const component = createOutputComponent(descriptor);
        wrapper.appendChild(component);
        grid.appendChild(wrapper);
      });
      hasRendered = true;
    }
    if (!hasRendered) {
      debugLog(WORKFLOW_RESULTS_CLEARED, "informational", {
        workflowId: state.current.id
      });
      return;
    }
    element.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
    debugLog(WORKFLOW_RESULTS_RENDERED, "informational", {
      workflowId: state.current.id,
      nodes: nodeIds
    });
  };
  const updateRunButton = (state) => {
    const button = state.ui.layout.main.workflow.run;
    if (!button) {
      return;
    }
    button.lfShowSpinner = state.current.status === "running";
  };
  const updateStatus = (state) => {
    const element = state.ui.layout.main.workflow.status;
    if (!element) {
      return;
    }
    const message = state.current.message ?? DEFAULT_STATUS_MESSAGES[state.current.status];
    element.textContent = message;
    element.dataset.tone = state.current.status;
    const category = state.current.status === "error" ? "error" : state.current.status === "ready" ? "success" : "informational";
    debugLog(STATUS_UPDATED, category, {
      workflowId: state.current.id,
      status: state.current.status,
      message
    });
  };
  const updateTitle = (state) => {
    const element = state.ui.layout.main.workflow.title;
    if (!element) {
      return;
    }
    element.textContent = getWorkflowTitle(state);
  };
  const render = (state) => {
    if (!section) {
      return;
    }
    if (state.current.id !== lastWorkflowId) {
      updateDescription(state);
      updateTitle(state);
      updateOptions(state);
      lastWorkflowId = state.current.id;
    }
    if (state.current.status !== lastStatus || state.current.message !== lastMessage) {
      updateRunButton(state);
      updateStatus(state);
      lastStatus = state.current.status;
      lastMessage = state.current.message ?? null;
    }
    if (state.results !== lastResultsRef) {
      updateResult(state);
      lastResultsRef = state.results;
    }
  };
  const setCellStatus = (state, id, status = "") => {
    const { ui } = state;
    const field = ui.layout.main.workflow.cells.find((el) => el.id === id);
    const wrapper = field == null ? void 0 : field.parentElement;
    if (wrapper) {
      wrapper.dataset.status = status;
    }
    if (status) {
      debugLog(WORKFLOW_INPUT_FLAGGED, "informational", {
        workflowId: state.current.id,
        field: id,
        status
      });
    }
  };
  const destroy = () => {
    section == null ? void 0 : section.remove();
    if (mountedState) {
      mountedState.mutate.ui((uiState) => {
        const wf = uiState.layout.main.workflow;
        wf._root = null;
        wf.cells = [];
        wf.options = null;
        wf.result = null;
        wf.run = null;
        wf.status = null;
        wf.title = null;
      });
      debugLog(WORKFLOW_LAYOUT_DESTROYED, "informational", {
        workflowId: mountedState.current.id ?? null
      });
    }
    section = null;
    optionsWrapper = null;
    resultWrapper = null;
    runButton = null;
    statusWrapper = null;
    titleElement = null;
    lastWorkflowId = null;
    lastStatus = null;
    lastMessage = null;
    lastResultsRef = null;
    mountedState = null;
  };
  return {
    mount,
    render,
    destroy,
    setCellStatus
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
async function parseJson(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}
const fetchWorkflowDefinitions = async () => {
  const response = await fetch(buildApiUrl("/workflows"), { method: "GET" });
  const data = await parseJson(response);
  if (!response.ok) {
    const message = `Failed to load workflows (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }
  if (!(data == null ? void 0 : data.workflows) || !Array.isArray(data.workflows.nodes)) {
    throw new WorkflowApiError("Invalid workflows response shape.", { payload: data });
  }
  return data.workflows;
};
const runWorkflowRequest = async (workflowId, inputs) => {
  const response = await fetch(buildApiUrl("/run"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workflowId, inputs })
  });
  const data = await parseJson(response);
  const payload = data && data.payload || {
    detail: response.statusText || "unknown",
    history: {}
  };
  if (!response.ok || !data) {
    const detail = (payload == null ? void 0 : payload.detail) || response.statusText || "unknown";
    throw new WorkflowApiError(`Workflow execution failed: ${detail}`, {
      status: response.status,
      payload
    });
  }
  return {
    message: "Workflow execution completed.",
    payload,
    status: data.status
  };
};
const uploadWorkflowFiles = async (files) => {
  if (!files || files.length === 0) {
    throw new WorkflowApiError("Missing file to upload.", {
      payload: { detail: "missing_file" }
    });
  }
  const formData = new FormData();
  files.forEach((file) => formData.append("file", file));
  const response = await fetch(buildApiUrl("/upload"), {
    method: "POST",
    body: formData
  });
  const data = await parseJson(response);
  if (isWorkflowAPIUploadResponse(data)) {
    if (!response.ok) {
      const { payload } = data;
      const detail = (payload == null ? void 0 : payload.detail) || response.statusText || "unknown";
      throw new WorkflowApiError(`Upload failed: ${detail}`, {
        status: response.status,
        payload
      });
    }
    return data;
  }
  if (isWorkflowAPIUploadPayload(data)) {
    if (!response.ok) {
      const detail = data.detail || response.statusText || "unknown";
      throw new WorkflowApiError(`Upload failed: ${detail}`, {
        status: response.status,
        payload: data
      });
    }
    return {
      message: "Upload completed successfully.",
      payload: data,
      status: "ready"
    };
  }
  throw new WorkflowApiError("Invalid response shape from upload API.", {
    status: response.status
  });
};
const INIT_ERROR = "Mutate not initialized";
const INIT_CB = () => {
  throw new Error(INIT_ERROR);
};
const initState = (appContainer) => ({
  current: { status: "ready", message: "Ready.", id: null },
  isDebug: false,
  manager: null,
  mutate: {
    isDebug: INIT_CB,
    manager: INIT_CB,
    runResult: INIT_CB,
    status: INIT_CB,
    workflow: INIT_CB,
    workflows: INIT_CB,
    ui: INIT_CB
  },
  results: null,
  ui: {
    layout: {
      _root: appContainer,
      actionButton: { _root: null },
      drawer: {
        _root: null,
        tree: null
      },
      header: {
        _root: null,
        drawerToggle: null,
        debugToggle: null,
        themeSwitch: null
      },
      main: {
        _root: null,
        title: { _root: null },
        workflow: {
          _root: null,
          cells: [],
          description: null,
          options: null,
          result: null,
          run: null,
          status: null,
          title: null
        }
      },
      dev: {
        _root: null,
        card: null
      }
    }
  },
  workflows: {}
});
const createWorkflowRunnerStore = (initialState) => {
  let state = initialState;
  const listeners = /* @__PURE__ */ new Set();
  const pendingMutations = [];
  let isApplyingMutation = false;
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
      mutator(current);
      return { ...current };
    }));
  };
  const mutate = {
    isDebug: (isDebug) => applyMutation((draft) => {
      draft.isDebug = isDebug;
    }),
    manager: (manager) => applyMutation((draft) => {
      draft.manager = manager;
    }),
    status: (status, message) => setStatus(status, message, setState),
    runResult: (status, message, results) => setRunResult(status, message, results, setState),
    ui: (updater) => applyMutation((draft) => {
      updater(draft.ui);
    }),
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
const setRunResult = (status, message, results, setState) => {
  setState((state) => ({
    ...state,
    current: {
      ...state.current,
      status,
      message
    },
    results
  }));
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
    current: {
      ...state.current,
      id
    },
    results: null
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
var _LfWorkflowRunnerManager_instances, _LfWorkflowRunnerManager_FRAMEWORK, _LfWorkflowRunnerManager_IS_DEBUG, _LfWorkflowRunnerManager_SECTIONS, _LfWorkflowRunnerManager_STORE, _LfWorkflowRunnerManager_collectInputs, _LfWorkflowRunnerManager_handleUploadField, _LfWorkflowRunnerManager_initializeFramework, _LfWorkflowRunnerManager_initializeLayout, _LfWorkflowRunnerManager_loadWorkflows, _LfWorkflowRunnerManager_subscribeToState;
class LfWorkflowRunnerManager {
  constructor() {
    _LfWorkflowRunnerManager_instances.add(this);
    _LfWorkflowRunnerManager_FRAMEWORK.set(this, getLfFramework());
    _LfWorkflowRunnerManager_IS_DEBUG.set(this, false);
    _LfWorkflowRunnerManager_SECTIONS.set(this, void 0);
    _LfWorkflowRunnerManager_STORE.set(this, void 0);
    _LfWorkflowRunnerManager_collectInputs.set(this, async () => {
      const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
      const { cells } = state.ui.layout.main.workflow;
      const inputs = {};
      for (const cell of cells) {
        const id = cell.id || "";
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").workflow.setCellStatus(state, id);
        const value = await cell.getValue();
        switch (cell.tagName.toLowerCase()) {
          case "lf-toggle":
            inputs[id] = value === "off" ? false : true;
            break;
          case "lf-upload":
            inputs[id] = await __classPrivateFieldGet(this, _LfWorkflowRunnerManager_handleUploadField, "f").call(this, id, value);
            break;
          default:
            inputs[id] = value;
        }
      }
      return inputs;
    });
    _LfWorkflowRunnerManager_handleUploadField.set(this, async (fieldName, rawValue) => {
      var _a;
      const { UPLOADING_FILE, FILE_PROCESSING } = STATUS_MESSAGES;
      const files = Array.isArray(rawValue) ? rawValue : rawValue;
      if (!files || files.length === 0) {
        return [];
      }
      try {
        this.setStatus("running", UPLOADING_FILE);
        const { payload } = await uploadWorkflowFiles(files);
        const paths = (payload == null ? void 0 : payload.paths) || [];
        this.setStatus("running", FILE_PROCESSING);
        return paths.length === 1 ? paths[0] : paths;
      } catch (error) {
        if (error instanceof WorkflowApiError) {
          __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").workflow.setCellStatus(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState(), fieldName, "error");
          this.setStatus("error", `Upload failed: ${((_a = error.payload) == null ? void 0 : _a.detail) || error.message}`);
        } else {
          this.setStatus("error", "Upload failed unexpectedly.");
        }
        throw error;
      }
    });
    _LfWorkflowRunnerManager_loadWorkflows.set(this, async () => {
      var _a;
      const { WORKFLOWS_LOADED } = DEBUG_MESSAGES;
      const workflows = await fetchWorkflowDefinitions();
      if (!workflows || !Object.keys(workflows).length) {
        throw new Error("No workflows available from the API.");
      }
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().mutate.workflows(workflows);
      const firstWorkflow = (_a = workflows.nodes) == null ? void 0 : _a[0];
      if (firstWorkflow == null ? void 0 : firstWorkflow.id) {
        this.setWorkflow(firstWorkflow.id);
      }
      this.setStatus("ready", WORKFLOWS_LOADED);
    });
    const { WORKFLOWS_LOAD_FAILED } = DEBUG_MESSAGES;
    const { LOADING_WORKFLOWS } = STATUS_MESSAGES;
    const container = document.querySelector("#app");
    if (!container) {
      throw new Error("Workflow runner container not found.");
    }
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_STORE, createWorkflowRunnerStore(initState(container)), "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_IS_DEBUG, __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().isDebug, "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_SECTIONS, {
      actionButton: createActionButtonSection(),
      drawer: createDrawerSection(),
      header: createHeaderSection(),
      main: createMainSection(),
      workflow: createWorkflowSection(),
      dev: createDevPanel()
    }, "f");
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().mutate.manager(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeFramework).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeLayout).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_subscribeToState).call(this);
    this.setStatus("running", LOADING_WORKFLOWS);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_loadWorkflows, "f").call(this).catch((error) => {
      const message = error instanceof Error ? error.message : WORKFLOWS_LOAD_FAILED;
      debugLog(WORKFLOWS_LOAD_FAILED, "error", {
        message,
        stack: error instanceof Error ? error.stack : void 0
      });
      this.setStatus("error", message);
    });
  }
  //#endregion
  //#region Workflow execution
  async runWorkflow() {
    var _a, _b, _c, _d, _e, _f;
    const { INPUTS_COLLECTED, WORKFLOW_COMPLETED, WORKFLOW_DISPATCHING, WORKFLOW_NOT_SELECTED } = DEBUG_MESSAGES;
    const { SUBMITTING_WORKFLOW } = STATUS_MESSAGES;
    const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
    const id = state.current.id;
    if (!id) {
      this.setStatus("error", WORKFLOW_NOT_SELECTED);
      return;
    }
    this.setStatus("running", SUBMITTING_WORKFLOW);
    let inputs;
    try {
      inputs = await __classPrivateFieldGet(this, _LfWorkflowRunnerManager_collectInputs, "f").call(this);
      debugLog(INPUTS_COLLECTED, "informational", {
        id,
        inputKeys: Object.keys(inputs)
      });
    } catch (error) {
      const detail = error instanceof WorkflowApiError ? ((_a = error.payload) == null ? void 0 : _a.detail) || error.message : (error == null ? void 0 : error.message) || "Failed to collect inputs.";
      this.setStatus("error", `Failed to collect inputs: ${detail}`);
      return;
    }
    try {
      debugLog(WORKFLOW_DISPATCHING, "informational", {
        id,
        inputKeys: Object.keys(inputs)
      });
      const { status, message, payload } = await runWorkflowRequest(id, inputs);
      const runState = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
      runState.mutate.runResult(status, message, ((_b = payload.history) == null ? void 0 : _b.outputs) ? { ...payload.history.outputs } : null);
      const resultCategory = status === "error" ? "error" : "success";
      debugLog(WORKFLOW_COMPLETED, resultCategory, {
        id,
        wfStatus: status,
        outputs: Object.keys(((_c = payload.history) == null ? void 0 : _c.outputs) ?? {})
      });
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        const inputName = (_e = (_d = error.payload) == null ? void 0 : _d.error) == null ? void 0 : _e.input;
        if (inputName) {
          __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").workflow.setCellStatus(state, inputName, "error");
        }
        this.setStatus("error", ((_f = error.payload) == null ? void 0 : _f.detail) || error.message);
      } else {
        this.setStatus("error", "Unexpected error while running the workflow.");
      }
    }
  }
  //#endregion
  //#region Getters
  isDebugEnabled() {
    return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().isDebug;
  }
  //#endregion
  //#region State mutators
  setStatus(status, message) {
    const { mutate } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
    const resolved = message ?? DEFAULT_STATUS_MESSAGES[status];
    mutate.status(status, resolved);
  }
  setWorkflow(id) {
    const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
    if (state.current.id === id) {
      return;
    }
    state.mutate.workflow(id);
  }
  toggleDebug() {
    const current = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().isDebug;
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().mutate.isDebug(!current);
  }
}
_LfWorkflowRunnerManager_FRAMEWORK = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_IS_DEBUG = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_SECTIONS = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_STORE = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_collectInputs = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_handleUploadField = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_loadWorkflows = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_instances = /* @__PURE__ */ new WeakSet(), _LfWorkflowRunnerManager_initializeFramework = function _LfWorkflowRunnerManager_initializeFramework2() {
  const assetsUrl = buildAssetsUrl();
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_FRAMEWORK, "f").assets.set(assetsUrl);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_FRAMEWORK, "f").theme.set(DEFAULT_THEME);
}, _LfWorkflowRunnerManager_initializeLayout = function _LfWorkflowRunnerManager_initializeLayout2() {
  const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
  const root = state.ui.layout._root;
  if (!root) {
    return;
  }
  while (root.firstChild) {
    root.removeChild(root.firstChild);
  }
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").actionButton.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").drawer.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").header.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").main.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").workflow.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").workflow.render(state);
  if (state.isDebug) {
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").dev.mount(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").dev.render(state);
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_IS_DEBUG, true, "f");
  }
}, _LfWorkflowRunnerManager_subscribeToState = function _LfWorkflowRunnerManager_subscribeToState2() {
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").subscribe((state) => {
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").actionButton.render(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").drawer.render(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").header.render(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").main.render(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").workflow.render(state);
    const shouldShowDevPanel = state.isDebug;
    if (shouldShowDevPanel && !__classPrivateFieldGet(this, _LfWorkflowRunnerManager_IS_DEBUG, "f")) {
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").dev.mount(state);
      __classPrivateFieldSet(this, _LfWorkflowRunnerManager_IS_DEBUG, true, "f");
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").dev.render(state);
    } else if (!shouldShowDevPanel && __classPrivateFieldGet(this, _LfWorkflowRunnerManager_IS_DEBUG, "f")) {
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").dev.destroy();
      __classPrivateFieldSet(this, _LfWorkflowRunnerManager_IS_DEBUG, false, "f");
    } else if (shouldShowDevPanel && __classPrivateFieldGet(this, _LfWorkflowRunnerManager_IS_DEBUG, "f")) {
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f").dev.render(state);
    }
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
