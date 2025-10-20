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
const ROOT_CLASS$4 = "dev-panel";
const CARD_CLASS = `${ROOT_CLASS$4}__card`;
const createDevPanel = () => {
  const framework = getLfFramework();
  const debugCardDataset = {
    nodes: [
      {
        id: "workflow-runner-debug",
        cells: {
          lfToggle: {
            shape: "toggle",
            lfValue: framework.debug.isEnabled(),
            value: framework.debug.isEnabled()
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
    container.className = ROOT_CLASS$4;
    container.dataset.open = "false";
    container.setAttribute("aria-hidden", "true");
    card = document.createElement("lf-card");
    card.className = CARD_CLASS;
    card.lfLayout = "debug";
    card.lfDataset = debugCardDataset;
    container.appendChild(card);
    (((_b = (_a = state.ui.layout._root) == null ? void 0 : _a.ownerDocument) == null ? void 0 : _b.body) ?? document.body).appendChild(container);
    if (state.dev.panel.open) {
      container.dataset.open = "true";
      container.setAttribute("aria-hidden", "false");
    }
    state.mutate.ui((ui) => {
      ui.layout.dev._root = container;
      ui.layout.dev.card = card;
    });
  };
  const render = (state) => {
    if (!container) {
      return;
    }
    const isOpen = state.dev.panel.open;
    container.dataset.open = String(isOpen);
    container.setAttribute("aria-hidden", String(!isOpen));
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
const ROOT_CLASS$3 = "drawer-section";
const _createDataset = (workflows) => {
  const dataset = {
    nodes: [{ children: workflows.nodes, id: "workflows", value: "Workflows" }]
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
        const isLeaf = !node.children || node.children.length === 0;
        if (!isLeaf) {
          return;
        }
        manager.setWorkflow(node.id);
        break;
    }
  });
  state.mutate.ui((ui) => {
    ui.layout.drawer.tree = tree;
  });
  return tree;
};
const createDrawerSection = () => {
  let element = null;
  let lastState = null;
  const mount = (state) => {
    var _a;
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
  };
  const render = (state) => {
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
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.mutate.ui((ui) => {
        ui.layout.drawer._root = null;
        ui.layout.drawer.tree = null;
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
const createOutputField = (key, result) => {
  const isArrayOfComps = Array.isArray(result) && result.every((item) => typeof item === "object") && result.length > 1;
  if (isArrayOfComps) {
    const wrapper = document.createElement("div");
    wrapper.classList.add(`${key}-output-wrapper`);
    for (const item of result) {
      wrapper.appendChild(_chooseComponentForResult(key, item));
    }
    return wrapper;
  }
  const r = Array.isArray(result) ? result[0] : result;
  return _chooseComponentForResult(key, r);
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
    const { eventType } = e.detail;
    switch (eventType) {
      case "click":
        state.mutate.dev.panel.toggle();
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
    const debugToggle = state.ui.layout.header.debugToggle;
    if (debugToggle) {
      debugToggle.lfUiState = state.dev.panel.open ? "secondary" : "info";
      debugToggle.title = state.dev.panel.open ? "Hide developer console" : "Show developer console";
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
  };
  const render = () => {
  };
  const destroy = () => {
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.mutate.ui((uiState) => {
        uiState.layout.main._root = null;
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
const WORKFLOW_TEXT = "Select a workflow";
const ROOT_CLASS = "workflow-section";
const getCurrentWorkflow = (state) => {
  var _a;
  const { current, workflows } = state;
  return ((_a = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a.find((wf) => wf.id === current.workflow)) || null;
};
const getWorkflowTitle = (state) => {
  const workflow = getCurrentWorkflow(state);
  const str = typeof (workflow == null ? void 0 : workflow.value) === "string" ? workflow.value : String((workflow == null ? void 0 : workflow.value) || "");
  return str || WORKFLOW_TEXT;
};
const getWorkflowDescription = (state) => {
  const workflow = getCurrentWorkflow(state);
  return (workflow == null ? void 0 : workflow.description) || "";
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
  button.onclick = () => {
    var _a;
    return (_a = state.manager) == null ? void 0 : _a.runWorkflow();
  };
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
    if (workflow && workflow.cells) {
      for (const key in workflow.cells) {
        const cell = workflow.cells[key];
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
  };
  const updateResult = (state) => {
    const { ui } = state;
    const element = ui.layout.main.workflow.result;
    if (!element) {
      return;
    }
    const outputs = state.results || {};
    clearChildren(element);
    const nodeIds = Object.keys(outputs || {});
    if (nodeIds.length === 0) {
      return;
    }
    for (const nodeId of nodeIds) {
      const nodeContent = outputs[nodeId];
      const { _description } = nodeContent;
      const title = document.createElement("h4");
      title.className = `${ROOT_CLASS}__result-title`;
      title.textContent = normalize_description(_description) || `Node #${nodeId}`;
      element.appendChild(title);
      const grid = document.createElement("div");
      grid.className = `${ROOT_CLASS}__result-grid`;
      element.appendChild(grid);
      for (const resultKey in nodeContent) {
        const key = resultKey;
        if (key === "_description") {
          continue;
        }
        const resultElement = createOutputField(resultKey, nodeContent[resultKey]);
        resultElement.className = `${ROOT_CLASS}__result-item`;
        if (resultElement) {
          grid.appendChild(resultElement);
        }
      }
    }
    element.scrollIntoView({
      behavior: "smooth",
      block: "start"
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
    if (state.current.workflow !== lastWorkflowId) {
      updateDescription(state);
      updateTitle(state);
      updateOptions(state);
      lastWorkflowId = state.current.workflow;
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
    message: data.message,
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
    const framework = getLfFramework();
    const debug = framework == null ? void 0 : framework.debug;
    const logs = debug == null ? void 0 : debug.logs;
    if (!debug || !logs) {
      return;
    }
    const formattedContext = formatContext(context);
    const payload = formattedContext ? `${message}

${formattedContext}` : message;
    void logs.new(debug, payload, category);
  } catch {
  }
};
const initState = (appContainer) => ({
  current: { status: "ready", message: "Ready.", workflow: null, preferredOutput: null },
  manager: null,
  ui: {
    layout: {
      _root: appContainer,
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
  workflows: {},
  results: null,
  mutate: {
    workflow: () => {
      throw new Error("Mutate not initialized");
    },
    status: () => {
      throw new Error("Mutate not initialized");
    },
    runResult: () => {
      throw new Error("Mutate not initialized");
    },
    manager: () => {
      throw new Error("Mutate not initialized");
    },
    workflows: () => {
      throw new Error("Mutate not initialized");
    },
    ui: () => {
      throw new Error("Mutate not initialized");
    },
    dev: {
      panel: {
        set: () => {
          throw new Error("Mutate not initialized");
        },
        toggle: () => {
          throw new Error("Mutate not initialized");
        }
      }
    }
  },
  dev: {
    panel: {
      open: false
    }
  }
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
    workflow: (workflowId) => setWorkflow(workflowId, setState),
    status: (status, message) => setStatus(status, message, setState),
    runResult: (status, message, preferredOutput, results) => setRunResult(status, message, preferredOutput, results, setState),
    manager: (manager) => applyMutation((draft) => {
      draft.manager = manager;
    }),
    workflows: (workflows) => applyMutation((draft) => {
      draft.workflows = workflows;
    }),
    ui: (updater) => applyMutation((draft) => {
      updater(draft.ui);
    }),
    dev: {
      panel: {
        set: (open) => applyMutation((draft) => {
          draft.dev.panel.open = open;
        }),
        toggle: () => applyMutation((draft) => {
          draft.dev.panel.open = !draft.dev.panel.open;
        })
      }
    }
  };
  state.mutate = mutate;
  return {
    getState,
    setState,
    subscribe
  };
};
const setWorkflow = (workflowId, setState) => {
  setState((state) => ({
    ...state,
    current: {
      ...state.current,
      workflow: workflowId,
      preferredOutput: null
    },
    results: null
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
const setRunResult = (status, message, preferredOutput, results, setState) => {
  setState((state) => ({
    ...state,
    current: {
      ...state.current,
      status,
      message,
      preferredOutput
    },
    results
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
var _LfWorkflowRunnerManager_instances, _LfWorkflowRunnerManager_framework, _LfWorkflowRunnerManager_store, _LfWorkflowRunnerManager_sections, _LfWorkflowRunnerManager_collectInputs, _LfWorkflowRunnerManager_handleUploadField, _LfWorkflowRunnerManager_initializeFramework, _LfWorkflowRunnerManager_initializeLayout, _LfWorkflowRunnerManager_loadWorkflows, _LfWorkflowRunnerManager_subscribeToState;
class LfWorkflowRunnerManager {
  constructor() {
    _LfWorkflowRunnerManager_instances.add(this);
    _LfWorkflowRunnerManager_framework.set(this, getLfFramework());
    _LfWorkflowRunnerManager_store.set(this, void 0);
    _LfWorkflowRunnerManager_sections.set(this, void 0);
    _LfWorkflowRunnerManager_collectInputs.set(this, async () => {
      const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState();
      const { cells } = state.ui.layout.main.workflow;
      const inputs = {};
      for (const cell of cells) {
        const id = cell.id || "";
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.setCellStatus(state, id);
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
      var _a, _b;
      const files = Array.isArray(rawValue) ? rawValue : rawValue;
      if (!files || files.length === 0) {
        return [];
      }
      try {
        this.setStatus("running", "Uploading file...");
        const { payload } = await uploadWorkflowFiles(files);
        const paths = (payload == null ? void 0 : payload.paths) || [];
        this.setStatus("running", "File uploaded, processing...");
        void debugLog("Upload completed.", "success", { fieldName, files: paths.length });
        return paths.length === 1 ? paths[0] : paths;
      } catch (error) {
        if (error instanceof WorkflowApiError) {
          __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.setCellStatus(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState(), fieldName, "error");
          this.setStatus("error", `Upload failed: ${((_a = error.payload) == null ? void 0 : _a.detail) || error.message}`);
          void debugLog("Upload failed.", "error", {
            fieldName,
            detail: ((_b = error.payload) == null ? void 0 : _b.detail) || error.message
          });
        } else {
          void debugLog("Upload failed unexpectedly.", "error", {
            fieldName,
            message: (error == null ? void 0 : error.message) ?? null
          });
        }
        throw error;
      }
    });
    _LfWorkflowRunnerManager_loadWorkflows.set(this, async () => {
      var _a;
      const workflows = await fetchWorkflowDefinitions();
      if (!workflows || !Object.keys(workflows).length) {
        throw new Error("No workflows available from the API.");
      }
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState().mutate.workflows(workflows);
      debugLog("Workflow definitions loaded.", "success", {
        count: ((_a = workflows.nodes) == null ? void 0 : _a.length) ?? 0
      });
      this.setWorkflow(workflows.nodes[0].id);
      this.setStatus("ready", "Workflows loaded.");
    });
    const container = document.querySelector("#app");
    if (!container) {
      throw new Error("Workflow runner container not found.");
    }
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_store, createWorkflowRunnerStore(initState(container)), "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_sections, {
      drawer: createDrawerSection(),
      header: createHeaderSection(),
      main: createMainSection(),
      workflow: createWorkflowSection(),
      dev: createDevPanel()
    }, "f");
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState().mutate.manager(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeFramework).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeLayout).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_subscribeToState).call(this);
    this.setStatus("running", "Loading workflows...");
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_loadWorkflows, "f").call(this).catch((error) => {
      console.error("Failed to load workflows:", error);
      const message = error instanceof Error ? error.message : "Failed to load workflows.";
      void debugLog("Failed to load workflows.", "error", {
        message,
        stack: error instanceof Error ? error.stack : void 0
      });
      this.setStatus("error", message);
    });
  }
  //#endregion
  //#region Workflow execution
  async runWorkflow() {
    var _a, _b, _c, _d, _e, _f, _g, _h, _i;
    const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState();
    const workflowId = state.current.workflow;
    if (!workflowId) {
      this.setStatus("error", "No workflow selected.");
      return;
    }
    this.setStatus("running", "Submitting workflow...");
    let inputs;
    try {
      inputs = await __classPrivateFieldGet(this, _LfWorkflowRunnerManager_collectInputs, "f").call(this);
      void debugLog("Collected workflow inputs.", "informational", {
        workflowId,
        inputKeys: Object.keys(inputs)
      });
    } catch (error) {
      console.error("Failed to collect inputs:", error);
      const detail = error instanceof WorkflowApiError ? ((_a = error.payload) == null ? void 0 : _a.detail) || error.message : (error == null ? void 0 : error.message) || "Failed to collect inputs.";
      this.setStatus("error", `Failed to collect inputs: ${detail}`);
      void debugLog("Failed to collect workflow inputs.", "error", { workflowId, detail });
      return;
    }
    try {
      void debugLog("Dispatching workflow execution.", "informational", {
        workflowId,
        inputKeys: Object.keys(inputs)
      });
      const { status, message, payload } = await runWorkflowRequest(workflowId, inputs);
      const runState = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState();
      runState.mutate.runResult(status, message, payload.preferred_output ?? null, ((_b = payload.history) == null ? void 0 : _b.outputs) ? { ...payload.history.outputs } : null);
      const resultCategory = status === "error" ? "error" : "success";
      void debugLog("Workflow execution completed.", resultCategory, {
        workflowId,
        status,
        preferredOutput: payload.preferred_output ?? null,
        outputs: Object.keys(((_c = payload.history) == null ? void 0 : _c.outputs) ?? {})
      });
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        this.setStatus("error", ((_d = error.payload) == null ? void 0 : _d.detail) || error.message);
        void debugLog("Workflow execution failed.", "error", {
          workflowId,
          detail: ((_e = error.payload) == null ? void 0 : _e.detail) || error.message,
          input: (_g = (_f = error.payload) == null ? void 0 : _f.error) == null ? void 0 : _g.input
        });
        const inputName = (_i = (_h = error.payload) == null ? void 0 : _h.error) == null ? void 0 : _i.input;
        if (inputName) {
          __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.setCellStatus(state, inputName, "error");
        }
      } else {
        console.error("Unexpected error while running workflow:", error);
        this.setStatus("error", "Unexpected error while running the workflow.");
        void debugLog("Workflow execution failed unexpectedly.", "error", {
          workflowId,
          message: (error == null ? void 0 : error.message) ?? null
        });
      }
    }
  }
  //#endregion
  //#region State mutators
  setStatus(status, message) {
    const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState();
    state.mutate.status(status, message);
    const category = status === "error" ? "error" : status === "ready" ? "success" : "informational";
    void debugLog(`Status changed: ${status}`, category, { message: message ?? null });
  }
  setWorkflow(id) {
    const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState();
    if (state.current.workflow === id) {
      return;
    }
    state.mutate.workflow(id);
    void debugLog("Workflow selected.", "informational", { id });
  }
}
_LfWorkflowRunnerManager_framework = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_store = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_sections = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_collectInputs = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_handleUploadField = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_loadWorkflows = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_instances = /* @__PURE__ */ new WeakSet(), _LfWorkflowRunnerManager_initializeFramework = function _LfWorkflowRunnerManager_initializeFramework2() {
  const assetsUrl = buildAssetsUrl();
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_framework, "f").assets.set(assetsUrl);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_framework, "f").theme.set(DEFAULT_THEME);
}, _LfWorkflowRunnerManager_initializeLayout = function _LfWorkflowRunnerManager_initializeLayout2() {
  const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState();
  const root = state.ui.layout._root;
  if (!root) {
    return;
  }
  while (root.firstChild) {
    root.removeChild(root.firstChild);
  }
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").drawer.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").header.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").main.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").dev.mount(state);
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.render(state);
}, _LfWorkflowRunnerManager_subscribeToState = function _LfWorkflowRunnerManager_subscribeToState2() {
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").subscribe((state) => {
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").drawer.render(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").header.render(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").main.render(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.render(state);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").dev.render(state);
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
