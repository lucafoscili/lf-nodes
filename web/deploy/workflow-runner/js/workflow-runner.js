import { g as getLfFramework } from "../../js/lf-widgets-CAA2GbO2.js";
const apiBase = "/api";
const apiRoutePrefix = "/lf-nodes";
const staticPaths = { "assets": "/lf-nodes/static/assets/" };
const theme$7 = "dark";
const runnerConfig = {
  apiBase,
  apiRoutePrefix,
  staticPaths,
  theme: theme$7
};
const API_BASE = runnerConfig.apiBase;
const API_ROUTE_PREFIX = runnerConfig.apiRoutePrefix;
const API_ROOT = `${API_BASE}${API_ROUTE_PREFIX}`;
const DEFAULT_STATUS_MESSAGES = {
  idle: "Ready.",
  running: "Running...",
  error: "An error occurred while running the workflow."
};
const DEFAULT_THEME = runnerConfig.theme;
const STATIC_ASSETS_PATH = runnerConfig.staticPaths.assets;
const buildApiUrl = (path) => `${API_ROOT}${path.startsWith("/") ? path : `/${path}`}`;
const buildAssetsUrl = (origin = window.location.origin) => `${origin}${API_BASE}${STATIC_ASSETS_PATH.startsWith("/") ? STATIC_ASSETS_PATH : `/${STATIC_ASSETS_PATH}`}`;
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
const parseCount = (v) => {
  if (Array.isArray(v)) {
    return v.length;
  }
  if (v === null || v === void 0) {
    return 0;
  }
  if (typeof v === "boolean") {
    return v ? 1 : 0;
  }
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};
const clearChildren = (element) => {
  if (!element) {
    return;
  }
  while (element.firstChild) {
    element.removeChild(element.firstChild);
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
  INPUTS_COLLECTED: "Collected workflow inputs.",
  MAIN_DESTROYED: "Main section destroyed.",
  MAIN_MOUNTED: "Main section mounted.",
  MAIN_UPDATED: "Main section updated.",
  NOTIFICATIONS_DESTROYED: "Notifications section destroyed.",
  NOTIFICATIONS_MOUNTED: "Notifications section mounted.",
  NOTIFICATIONS_UPDATED: "Notifications section refreshed.",
  WORKFLOW_LAYOUT_DESTROYED: "Workflow layout destroyed.",
  WORKFLOW_LAYOUT_MOUNTED: "Workflow layout mounted.",
  WORKFLOW_LAYOUT_UPDATED: "Workflow layout updated.",
  WORKFLOW_INPUT_FLAGGED: "Workflow input flagged.",
  WORKFLOW_INPUTS_CLEARED: "Workflow inputs cleared.",
  WORKFLOW_INPUTS_RENDERED: "Workflow inputs rendered.",
  WORKFLOW_RESULTS_CLEARED: "Workflow results cleared.",
  WORKFLOW_RESULTS_RENDERED: "Workflow results rendered."
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
  WORKFLOW_COMPLETED: "Workflow execution completed successfully.",
  WORKFLOWS_LOAD_FAILED: "Failed to load workflows."
};
const STATUS_MESSAGES = {
  ERROR_FETCHING_WORKFLOWS: "Error fetching workflows!",
  ERROR_RUNNING_WORKFLOW: "Error running workflow!",
  ERROR_UPLOADING_FILE: "Error uploading file!",
  IDLE: "Idle",
  IDLE_WORKFLOWS_LOADED: "Workflows loaded",
  RUNNING_DISPATCHING_WORKFLOW: "Dispatching workflow...",
  RUNNING_INITIALIZING: "Initializing...",
  RUNNING_LOADING_WORKFLOWS: "Loading workflows...",
  RUNNING_SUBMITTING_WORKFLOW: "Submitting workflow...",
  RUNNING_UPLOADING_FILE: "Uploading file..."
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
  const data = await syntax.json.parse(response);
  if (!response.ok) {
    const message = `Failed to load workflow JSON (${response.status})`;
    throw new WorkflowApiError(message, { status: response.status, payload: data });
  }
  return data;
};
const runWorkflowRequest = async (workflowId, inputs) => {
  const { RUN_GENERIC } = ERROR_MESSAGES;
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl("/run"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workflowId, inputs })
  });
  const data = await syntax.json.parse(response);
  const payload = data && data.payload || {
    detail: response.statusText,
    history: {}
  };
  if (!response.ok || !data) {
    const detail = (payload == null ? void 0 : payload.detail) || response.statusText;
    throw new WorkflowApiError(`${RUN_GENERIC} (${detail})`, {
      payload
    });
  }
  return payload;
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
const executeWorkflow = (e, store) => {
  const { eventType } = e.detail;
  const { manager } = store.getState();
  switch (eventType) {
    case "click":
      manager.getDispatchers().runWorkflow();
      break;
    default:
      return;
  }
};
const openWorkflowInComfyUI = async (e, store) => {
  const { NO_WORKFLOW_SELECTED } = NOTIFICATION_MESSAGES;
  const { ERROR_FETCHING_WORKFLOWS } = STATUS_MESSAGES;
  const { eventType } = e.detail;
  const state = store.getState();
  const { current } = state;
  const { id } = current;
  switch (eventType) {
    case "click":
      if (!id) {
        state.mutate.notifications.add({
          id: performance.now().toString(),
          message: NO_WORKFLOW_SELECTED,
          status: "warning"
        });
        return;
      }
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
        }, 1e3);
      } catch (error) {
        state.mutate.status("error", ERROR_FETCHING_WORKFLOWS);
        if (error instanceof WorkflowApiError) {
          state.mutate.notifications.add({
            id: performance.now().toString(),
            message: `Failed to fetch workflow: ${error.message}`,
            status: "danger"
          });
        }
      }
      break;
    default:
      return;
  }
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
  const { dataset, json, metadata, props, shape, slot_map, svg } = descriptor;
  const el = document.createElement("div");
  switch (shape) {
    case "code": {
      const p = props || {};
      p.lfValue = svg || syntax.json.unescape(json || metadata || dataset || { message: "No output available." }).unescapedString;
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
const { theme: theme$6 } = getLfFramework();
const ROOT_CLASS$6 = "main-section";
const MAIN_CLASSES = {
  _: theme$6.bemClass(ROOT_CLASS$6)
};
const createMainSection = (store) => {
  const { MAIN_DESTROYED, MAIN_MOUNTED, MAIN_UPDATED } = DEBUG_MESSAGES;
  const WORKFLOW_SECTION = createWorkflowSection(store);
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in MAIN_CLASSES) {
      const element = MAIN_CLASSES[cls];
      uiRegistry.remove(element);
    }
    WORKFLOW_SECTION.destroy();
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
    _root.className = ROOT_CLASS$6;
    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(MAIN_CLASSES._, _root);
    WORKFLOW_SECTION.mount();
    debugLog(MAIN_MOUNTED);
  };
  const render = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    WORKFLOW_SECTION.render();
    debugLog(MAIN_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const WORKFLOW_TEXT = "Select a workflow";
const { theme: theme$5 } = getLfFramework();
const ROOT_CLASS$5 = "workflow-section";
const WORKFLOW_CLASSES = {
  _: theme$5.bemClass(ROOT_CLASS$5),
  cell: theme$5.bemClass(ROOT_CLASS$5, "cell"),
  cells: theme$5.bemClass(ROOT_CLASS$5, "cells"),
  description: theme$5.bemClass(ROOT_CLASS$5, "description"),
  h3: theme$5.bemClass(ROOT_CLASS$5, "title-h3"),
  openButton: theme$5.bemClass(ROOT_CLASS$5, "title-open-button"),
  options: theme$5.bemClass(ROOT_CLASS$5, "options"),
  result: theme$5.bemClass(ROOT_CLASS$5, "result"),
  resultGrid: theme$5.bemClass(ROOT_CLASS$5, "result-grid"),
  resultItem: theme$5.bemClass(ROOT_CLASS$5, "result-item"),
  resultTitle: theme$5.bemClass(ROOT_CLASS$5, "result-title"),
  title: theme$5.bemClass(ROOT_CLASS$5, "title")
};
const _createCellWrapper = () => {
  const cellWrapper = document.createElement("div");
  cellWrapper.className = WORKFLOW_CLASSES.cell;
  return cellWrapper;
};
const _createDescription = (store) => {
  const p = document.createElement("p");
  p.className = WORKFLOW_CLASSES.description;
  p.textContent = _getWorkflowDescription(store);
  return p;
};
const _createOptionsWrapper = () => {
  const optionsWrapper = document.createElement("div");
  optionsWrapper.className = WORKFLOW_CLASSES.options;
  return optionsWrapper;
};
const _createResultWrapper = () => {
  const resultWrapper = document.createElement("div");
  resultWrapper.className = WORKFLOW_CLASSES.result;
  return resultWrapper;
};
const _deepMerge = (defs, outs) => {
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
const _getCurrentWorkflow = (store) => {
  var _a;
  const { current, workflows } = store.getState();
  return ((_a = workflows == null ? void 0 : workflows.nodes) == null ? void 0 : _a.find((node) => node.id === current.id)) || null;
};
const _getWorkflowDescription = (store) => {
  const workflow = _getCurrentWorkflow(store);
  return (workflow == null ? void 0 : workflow.description) || "";
};
const _getWorkflowInputCells = (workflow) => {
  var _a;
  const inputsSection = (_a = workflow.children) == null ? void 0 : _a.find((child) => child.id.endsWith(":inputs"));
  return (inputsSection == null ? void 0 : inputsSection.cells) || {};
};
const _getWorkflowOutputCells = (workflow) => {
  var _a;
  const outputsSection = (_a = workflow.children) == null ? void 0 : _a.find((child) => child.id.endsWith(":outputs"));
  return (outputsSection == null ? void 0 : outputsSection.cells) || {};
};
const _getWorkflowTitle = (store) => {
  const workflow = _getCurrentWorkflow(store);
  const str = typeof (workflow == null ? void 0 : workflow.value) === "string" ? workflow.value : String((workflow == null ? void 0 : workflow.value) || "");
  return str || WORKFLOW_TEXT;
};
const _title = (store) => {
  const lfIcon = theme$5.get.icon("download");
  const title = document.createElement("div");
  const h3 = document.createElement("h3");
  const openButton = document.createElement("lf-button");
  title.className = WORKFLOW_CLASSES.title;
  h3.className = WORKFLOW_CLASSES.h3;
  h3.textContent = _getWorkflowTitle(store);
  const label = "Download Workflow JSON";
  openButton.className = WORKFLOW_CLASSES.openButton;
  openButton.lfAriaLabel = label;
  openButton.lfIcon = lfIcon;
  openButton.lfStyling = "icon";
  openButton.lfUiSize = "xsmall";
  openButton.title = label;
  openButton.addEventListener("lf-button-event", (e) => openWorkflowInComfyUI(e, store));
  title.appendChild(h3);
  title.appendChild(openButton);
  return { h3, openButton, title };
};
const createWorkflowSection = (store) => {
  const { WORKFLOW_INPUTS_CLEARED, WORKFLOW_INPUTS_RENDERED, WORKFLOW_LAYOUT_DESTROYED, WORKFLOW_LAYOUT_MOUNTED, WORKFLOW_LAYOUT_UPDATED, WORKFLOW_RESULTS_CLEARED, WORKFLOW_RESULTS_RENDERED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in WORKFLOW_CLASSES) {
      const element = WORKFLOW_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(WORKFLOW_LAYOUT_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[WORKFLOW_CLASSES._]) {
      return;
    }
    const _root = document.createElement("section");
    _root.className = WORKFLOW_CLASSES._;
    const description = _createDescription(store);
    const options = _createOptionsWrapper();
    const result = _createResultWrapper();
    const { h3, openButton, title } = _title(store);
    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(options);
    _root.appendChild(result);
    elements[MAIN_CLASSES._].appendChild(_root);
    uiRegistry.set(WORKFLOW_CLASSES._, _root);
    uiRegistry.set(WORKFLOW_CLASSES.description, description);
    uiRegistry.set(WORKFLOW_CLASSES.h3, h3);
    uiRegistry.set(WORKFLOW_CLASSES.openButton, openButton);
    uiRegistry.set(WORKFLOW_CLASSES.options, options);
    uiRegistry.set(WORKFLOW_CLASSES.result, result);
    uiRegistry.set(WORKFLOW_CLASSES.title, title);
    debugLog(WORKFLOW_LAYOUT_MOUNTED);
  };
  const render = () => {
    const state = store.getState();
    const { current, manager } = state;
    const { id } = current;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const descr = elements[WORKFLOW_CLASSES.description];
    const h3 = elements[WORKFLOW_CLASSES.h3];
    descr.textContent = _getWorkflowDescription(store);
    h3.textContent = _getWorkflowTitle(store);
    updateOptions();
    updateResults();
    debugLog(WORKFLOW_LAYOUT_UPDATED);
  };
  const updateOptions = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    const element = elements[WORKFLOW_CLASSES.options];
    if (!element) {
      return;
    }
    clearChildren(element);
    const workflow = _getCurrentWorkflow(store);
    const cellElements = [];
    if (workflow) {
      const inputCells = _getWorkflowInputCells(workflow);
      for (const id in inputCells) {
        if (!Object.prototype.hasOwnProperty.call(inputCells, id)) {
          continue;
        }
        const cell = inputCells[id];
        const wrapper = _createCellWrapper();
        const component = createInputCell(cell);
        component.id = id;
        cellElements.push(component);
        wrapper.appendChild(component);
        element.appendChild(wrapper);
      }
    }
    uiRegistry.set(WORKFLOW_CLASSES.cells, cellElements);
    if (workflow && cellElements.length) {
      debugLog(WORKFLOW_INPUTS_RENDERED);
    } else {
      debugLog(WORKFLOW_INPUTS_CLEARED);
    }
  };
  const updateResults = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    const element = elements[WORKFLOW_CLASSES.result];
    if (!element) {
      return;
    }
    const outputs = state.results || {};
    clearChildren(element);
    const nodeIds = Object.keys(outputs);
    if (nodeIds.length === 0) {
      debugLog(WORKFLOW_RESULTS_CLEARED);
      return;
    }
    const workflow = _getCurrentWorkflow(store);
    const outputsDefs = workflow ? _getWorkflowOutputCells(workflow) : {};
    debugLog(WORKFLOW_RESULTS_CLEARED);
    const prepOutputs = _deepMerge(outputsDefs, outputs);
    for (let i = 0; i < prepOutputs.length; i++) {
      const output = prepOutputs[i];
      const { id, nodeId, title } = output;
      const h4 = document.createElement("h4");
      h4.className = WORKFLOW_CLASSES.resultTitle;
      h4.textContent = title || `Node #${nodeId}`;
      element.appendChild(h4);
      const grid = document.createElement("div");
      grid.className = WORKFLOW_CLASSES.resultGrid;
      element.appendChild(grid);
      const wrapper = document.createElement("div");
      wrapper.className = WORKFLOW_CLASSES.resultItem;
      const component = createOutputComponent(output);
      component.id = id;
      wrapper.appendChild(component);
      grid.appendChild(wrapper);
    }
    element.scrollIntoView({ behavior: "smooth", block: "center" });
    debugLog(WORKFLOW_RESULTS_RENDERED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const _collectInputs = async (store) => {
  const state = store.getState();
  const { uiRegistry } = state.manager;
  const elements = uiRegistry.get();
  const cells = (elements == null ? void 0 : elements[WORKFLOW_CLASSES.cells]) || [];
  const inputs = {};
  for (const cell of cells) {
    const id = cell.id || "";
    _setCellStatus(store, id);
    const value = await cell.getValue();
    switch (cell.tagName.toLowerCase()) {
      case "lf-toggle":
        inputs[id] = value === "off" ? false : true;
        break;
      case "lf-upload":
        try {
          inputs[id] = await _handleUploadCell(store, value);
        } catch (error) {
          _setCellStatus(store, id, "error");
          throw error;
        }
        break;
      default:
        inputs[id] = value;
    }
  }
  return inputs;
};
const _handleUploadCell = async (store, rawValue) => {
  var _a;
  const { ERROR_UPLOADING_FILE, RUNNING_UPLOADING_FILE } = STATUS_MESSAGES;
  const files = Array.isArray(rawValue) ? rawValue : rawValue;
  if (!files || files.length === 0) {
    return [];
  }
  const state = store.getState();
  try {
    state.mutate.status("running", RUNNING_UPLOADING_FILE);
    const { payload } = await uploadWorkflowFiles(files);
    const paths = (payload == null ? void 0 : payload.paths) || [];
    return paths.length === 1 ? paths[0] : paths;
  } catch (error) {
    state.mutate.status("error", ERROR_UPLOADING_FILE);
    if (error instanceof WorkflowApiError) {
      state.mutate.notifications.add({
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
  const { current, manager } = store.getState();
  const { uiRegistry } = manager;
  const elements = uiRegistry.get();
  const cells = (elements == null ? void 0 : elements[WORKFLOW_CLASSES.cells]) || [];
  const cell = cells.find((el) => el.id === id);
  const wrapper = cell == null ? void 0 : cell.parentElement;
  if (wrapper) {
    wrapper.dataset.status = status;
  }
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
  const { NO_WORKFLOW_SELECTED, WORKFLOW_COMPLETED } = NOTIFICATION_MESSAGES;
  const { ERROR_RUNNING_WORKFLOW, IDLE, RUNNING_DISPATCHING_WORKFLOW, RUNNING_SUBMITTING_WORKFLOW } = STATUS_MESSAGES;
  const state = store.getState();
  const { current } = state;
  const id = current.id;
  if (!id) {
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message: NO_WORKFLOW_SELECTED,
      status: "warning"
    });
    return;
  }
  state.mutate.status("running", RUNNING_SUBMITTING_WORKFLOW);
  let inputs;
  try {
    inputs = await _collectInputs(store);
    debugLog(INPUTS_COLLECTED, "informational", {
      id,
      inputKeys: Object.keys(inputs)
    });
  } catch (error) {
    const detail = error instanceof WorkflowApiError ? ((_a = error.payload) == null ? void 0 : _a.detail) || error.message : (error == null ? void 0 : error.message) || "Failed to collect inputs.";
    state.mutate.status("error", ERROR_RUNNING_WORKFLOW);
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message: `Failed to collect inputs: ${detail}`,
      status: "danger"
    });
    return;
  }
  try {
    state.mutate.status("running", RUNNING_DISPATCHING_WORKFLOW);
    const payload = await runWorkflowRequest(id, inputs);
    state.mutate.results(((_b = payload.history) == null ? void 0 : _b.outputs) ? { ...payload.history.outputs } : null);
    state.mutate.notifications.add({
      id: performance.now().toString(),
      message: WORKFLOW_COMPLETED,
      status: "success"
    });
    state.mutate.status("idle", IDLE);
  } catch (error) {
    state.mutate.status("error", ERROR_RUNNING_WORKFLOW);
    if (error instanceof WorkflowApiError) {
      const inputName = (_d = (_c = error.payload) == null ? void 0 : _c.error) == null ? void 0 : _d.input;
      if (inputName) {
        _setCellStatus(store, inputName, "error");
      }
      state.mutate.notifications.add({
        id: performance.now().toString(),
        message: `Workflow run failed: ${((_e = error.payload) == null ? void 0 : _e.detail) || error.message}`,
        status: "danger"
      });
    }
  }
};
const { theme: theme$4 } = getLfFramework();
const ROOT_CLASS$4 = "action-button-section";
const ACTION_BUTTON_CLASSES = {
  _: theme$4.bemClass(ROOT_CLASS$4)
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
    _root.className = theme$4.bemClass(ACTION_BUTTON_CLASSES._);
    _root.lfIcon = "send";
    _root.lfStyling = "floating";
    _root.title = "Run current workflow";
    _root.addEventListener("lf-button-event", (e) => executeWorkflow(e, store));
    manager.getAppRoot().appendChild(_root);
    uiRegistry.set(ACTION_BUTTON_CLASSES._, _root);
    debugLog(ACTION_BUTTON_MOUNTED);
  };
  const render = () => {
    const { current, manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const _root = elements[ACTION_BUTTON_CLASSES._];
    if (!_root) {
      return;
    }
    _root.lfShowSpinner = current.status === "running";
    debugLog(ACTION_BUTTON_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const { theme: theme$3 } = getLfFramework();
const ROOT_CLASS$3 = "dev-section";
const DEV_CLASSES = {
  _: theme$3.bemClass(ROOT_CLASS$3),
  card: theme$3.bemClass(ROOT_CLASS$3, "card")
};
const _createDataset$1 = () => {
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
    card.lfDataset = _createDataset$1();
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
const openComfyUI = (e) => {
  const { eventType } = e.detail;
  switch (eventType) {
    case "click":
      const port = window.location.port || "3000";
      window.open(`http://localhost:${port}`, "_blank");
  }
};
const openGithubRepo = (e) => {
  const { eventType } = e.detail;
  switch (eventType) {
    case "click":
      window.open("https://github.com/lucafoscili/lf-nodes", "_blank");
      break;
    default:
      return;
  }
};
const toggleDebug = (e, store) => {
  const { eventType } = e.detail;
  const state = store.getState();
  switch (eventType) {
    case "click":
      state.mutate.isDebug(!state.isDebug);
      break;
    default:
      return;
  }
};
const toggleDrawer = (e, store) => {
  const { eventType } = e.detail;
  const { manager } = store.getState();
  const elements = manager.uiRegistry.get();
  const drawer = elements[DRAWER_CLASSES._];
  switch (eventType) {
    case "click":
      drawer.toggle();
      break;
    default:
      return;
  }
};
const drawerNavigation = (e, store) => {
  const { eventType, node } = e.detail;
  const state = store.getState();
  const { manager } = state;
  const elements = manager.uiRegistry.get();
  const drawer = elements[DRAWER_CLASSES._];
  switch (eventType) {
    case "click":
      if (!manager) {
        return;
      }
      const isLeaf = !node.children || node.children.length === 0;
      if (isLeaf) {
        state.mutate.workflow(node.id);
        drawer.close();
      }
      break;
  }
};
const { theme: theme$2 } = getLfFramework();
const ROOT_CLASS$2 = "drawer-section";
const DRAWER_CLASSES = {
  _: theme$2.bemClass(ROOT_CLASS$2),
  buttonComfyUi: theme$2.bemClass(ROOT_CLASS$2, "button-comfyui"),
  buttonDebug: theme$2.bemClass(ROOT_CLASS$2, "button-debug"),
  buttonGithub: theme$2.bemClass(ROOT_CLASS$2, "button-github"),
  container: theme$2.bemClass(ROOT_CLASS$2, "container"),
  footer: theme$2.bemClass(ROOT_CLASS$2, "footer"),
  tree: theme$2.bemClass(ROOT_CLASS$2, "tree")
};
const _button = (icon, label, evCb, className) => {
  const button = document.createElement("lf-button");
  button.className = className;
  button.lfAriaLabel = label;
  button.lfIcon = icon;
  button.lfStyling = "icon";
  button.lfUiSize = "small";
  button.title = label;
  button.addEventListener("lf-button-event", evCb);
  return button;
};
const _footer = (store) => {
  const footer = document.createElement("div");
  footer.className = DRAWER_CLASSES.footer;
  let icon = getLfFramework().theme.get.icon("imageInPicture");
  let label = "Open ComfyUI";
  const comfyUi = _button(icon, label, (e) => openComfyUI(e), DRAWER_CLASSES.buttonComfyUi);
  icon = getLfFramework().theme.get.icon("bug");
  label = "Toggle developer console";
  const debug = _button(icon, label, (e) => toggleDebug(e, store), DRAWER_CLASSES.buttonDebug);
  icon = getLfFramework().theme.get.icon("brandGithub");
  label = "Open GitHub repository";
  const github = _button(icon, label, (e) => openGithubRepo(e), DRAWER_CLASSES.buttonGithub);
  footer.appendChild(github);
  footer.appendChild(comfyUi);
  footer.appendChild(debug);
  return { comfyUi, debug, footer, github };
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
const _createDataset = (workflows) => {
  var _a, _b;
  const categories = [];
  const root = { id: "workflows", value: "Workflows", children: categories };
  const clone = JSON.parse(JSON.stringify(workflows));
  (_a = clone.nodes) == null ? void 0 : _a.forEach((child) => {
    child.children = void 0;
  });
  (_b = clone.nodes) == null ? void 0 : _b.forEach((node) => {
    const name = (node == null ? void 0 : node.category) || "Uncategorized";
    let category = categories.find((cat) => cat.value === name);
    if (!category) {
      category = { icon: _getIcon(name), id: name, value: name, children: [] };
      categories.push(category);
    }
    category.children.push(node);
  });
  const dataset = {
    nodes: [root]
  };
  return dataset;
};
const _getIcon = (category) => {
  const { alertTriangle, codeCircle2, json } = getLfFramework().theme.get.icons();
  const category_icons = {
    SVG: codeCircle2,
    JSON: json
  };
  return category_icons[category] || alertTriangle;
};
const _tree = (store) => {
  const tree = document.createElement("lf-tree");
  tree.className = DRAWER_CLASSES.tree;
  tree.lfAccordionLayout = true;
  tree.addEventListener("lf-tree-event", (e) => drawerNavigation(e, store));
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
    _root.className = ROOT_CLASS$2;
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
    tree.lfDataset = _createDataset(workflows);
    debugLog(DRAWER_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const { theme: theme$1 } = getLfFramework();
const ROOT_CLASS$1 = "header-section";
const HEADER_CLASSES = {
  _: theme$1.bemClass(ROOT_CLASS$1),
  appMessage: theme$1.bemClass(ROOT_CLASS$1, "app-message"),
  container: theme$1.bemClass(ROOT_CLASS$1, "container"),
  drawerToggle: theme$1.bemClass(ROOT_CLASS$1, "drawer-toggle"),
  serverIndicator: theme$1.bemClass(ROOT_CLASS$1, "server-indicator"),
  serverIndicatorCounter: theme$1.bemClass(ROOT_CLASS$1, "server-indicator-counter"),
  serverIndicatorLight: theme$1.bemClass(ROOT_CLASS$1, "server-indicator-light")
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
  const lfIcon = theme$1.get.icon("menu2");
  const props = {
    lfAriaLabel: "Toggle drawer",
    lfIcon,
    lfStyling: "icon"
  };
  const drawerToggle = createComponent.button(props);
  drawerToggle.className = HEADER_CLASSES.drawerToggle;
  drawerToggle.addEventListener("lf-button-event", (e) => toggleDrawer(e, store));
  return drawerToggle;
};
const _serverIndicator = () => {
  const serverIndicator = document.createElement("div");
  serverIndicator.className = HEADER_CLASSES.serverIndicator;
  const light = document.createElement("lf-button");
  light.className = HEADER_CLASSES.serverIndicatorLight;
  light.lfUiSize = "large";
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
    const { counter, light, serverIndicator } = _serverIndicator();
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
    const { alertTriangle, check, hourglassLow } = theme$1.get.icons();
    const { current, manager, queuedJobs } = store.getState();
    const { message, status } = current;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const appMessage = elements[HEADER_CLASSES.appMessage];
    const counter = elements[HEADER_CLASSES.serverIndicatorCounter];
    const light = elements[HEADER_CLASSES.serverIndicatorLight];
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
      appMessage.innerText = message || "";
      appMessage.dataset.status = status || "";
      appMessage.dataset.visible = "true";
    }
    if (queuedJobs < 0) {
      light.lfIcon = alertTriangle;
      light.lfUiState = "danger";
      light.title = "Server disconnected";
    } else if (queuedJobs === 0) {
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
      element.lfIcon = status === "danger" ? theme.get.icon("alertTriangle") : theme.get.icon("infoHexagon");
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
const INIT_ERROR = "Mutate not initialized";
const INIT_CB = () => {
  throw new Error(INIT_ERROR);
};
const initState = () => ({
  current: { status: "idle", message: "", id: null },
  isDebug: false,
  manager: null,
  queuedJobs: -1,
  mutate: {
    isDebug: INIT_CB,
    manager: INIT_CB,
    queuedJobs: INIT_CB,
    notifications: {
      add: INIT_CB,
      removeById: INIT_CB,
      removeByIndex: INIT_CB
    },
    results: INIT_CB,
    status: INIT_CB,
    workflow: INIT_CB,
    workflows: INIT_CB
  },
  notifications: [],
  results: null,
  workflows: {
    nodes: []
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
    isDebug: (isDebug) => applyMutation((draft) => {
      draft.isDebug = isDebug;
    }),
    manager: (manager) => applyMutation((draft) => {
      draft.manager = manager;
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
    status: (status, message) => setStatus(status, message, setState),
    results: (results) => applyMutation((draft) => {
      draft.results = results;
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
var _LfWorkflowRunnerManager_instances, _LfWorkflowRunnerManager_APP_ROOT, _LfWorkflowRunnerManager_DISPATCHERS, _LfWorkflowRunnerManager_FRAMEWORK, _LfWorkflowRunnerManager_SECTIONS, _LfWorkflowRunnerManager_STORE, _LfWorkflowRunnerManager_UI_REGISTRY, _LfWorkflowRunnerManager_initializeFramework, _LfWorkflowRunnerManager_initializeLayout, _LfWorkflowRunnerManager_loadWorkflows, _LfWorkflowRunnerManager_startPolling, _LfWorkflowRunnerManager_subscribeToState;
class LfWorkflowRunnerManager {
  constructor() {
    _LfWorkflowRunnerManager_instances.add(this);
    _LfWorkflowRunnerManager_APP_ROOT.set(this, void 0);
    _LfWorkflowRunnerManager_DISPATCHERS.set(this, void 0);
    _LfWorkflowRunnerManager_FRAMEWORK.set(this, getLfFramework());
    _LfWorkflowRunnerManager_SECTIONS.set(this, void 0);
    _LfWorkflowRunnerManager_STORE.set(this, void 0);
    _LfWorkflowRunnerManager_UI_REGISTRY.set(this, /* @__PURE__ */ new WeakMap());
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
      if (firstWorkflow == null ? void 0 : firstWorkflow.id) {
        state2.mutate.workflow(firstWorkflow.id);
      }
    });
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
    const { ERROR_FETCHING_WORKFLOWS, IDLE_WORKFLOWS_LOADED, RUNNING_INITIALIZING, RUNNING_LOADING_WORKFLOWS } = STATUS_MESSAGES;
    const { WORKFLOWS_LOAD_FAILED } = NOTIFICATION_MESSAGES;
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_APP_ROOT, document.querySelector("#app"), "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_STORE, createWorkflowRunnerStore(initState()), "f");
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
    const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
    state.mutate.manager(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeFramework).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeLayout).call(this);
    state.mutate.status("running", RUNNING_INITIALIZING);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_subscribeToState).call(this);
    state.mutate.status("running", RUNNING_LOADING_WORKFLOWS);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_loadWorkflows, "f").call(this).catch((error) => {
      state.mutate.notifications.add({
        id: performance.now().toString(),
        message: error instanceof Error ? error.message : WORKFLOWS_LOAD_FAILED,
        status: "danger"
      });
      state.mutate.status("error", ERROR_FETCHING_WORKFLOWS);
    }).then(() => {
      state.mutate.status("idle", IDLE_WORKFLOWS_LOADED);
    });
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_startPolling).call(this);
  }
  //#endregion
  //#region Getters
  getAppRoot() {
    return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_APP_ROOT, "f");
  }
  getDispatchers() {
    return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_DISPATCHERS, "f");
  }
  getStore() {
    return __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f");
  }
}
_LfWorkflowRunnerManager_APP_ROOT = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_DISPATCHERS = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_FRAMEWORK = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_SECTIONS = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_STORE = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_UI_REGISTRY = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_loadWorkflows = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_instances = /* @__PURE__ */ new WeakSet(), _LfWorkflowRunnerManager_initializeFramework = function _LfWorkflowRunnerManager_initializeFramework2() {
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
}, _LfWorkflowRunnerManager_startPolling = function _LfWorkflowRunnerManager_startPolling2() {
  setInterval(async () => {
    try {
      const resp = await fetch("/queue");
      if (!resp.ok) {
        throw new Error("Failed to fetch queue status");
      }
      const { queue_running, queue_pending } = await resp.json();
      const qPending = parseCount(queue_pending);
      const qRunning = parseCount(queue_running);
      const busy = qPending + qRunning;
      const prev = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().queuedJobs ?? -1;
      if (busy !== prev) {
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().mutate.queuedJobs(busy);
      }
    } catch (e) {
      try {
        const prev = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().queuedJobs ?? -1;
        if (prev !== -1) {
          __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState().mutate.queuedJobs(-1);
        }
      } catch (err) {
      }
    }
  }, 750);
}, _LfWorkflowRunnerManager_subscribeToState = function _LfWorkflowRunnerManager_subscribeToState2() {
  var _a, _b, _c;
  const st = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f").getState();
  let lastCurrentMessage = st.current.message;
  let lastCurrentStatus = st.current.status;
  let lastDebug = st.isDebug;
  let lastId = st.current.id;
  let lastNotificationsCount = ((_a = st.notifications) == null ? void 0 : _a.length) ?? 0;
  let lastQueued = st.queuedJobs ?? -1;
  let lastResults = st.results;
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
    const { current, isDebug, queuedJobs, workflows } = state;
    const { message, status } = current;
    if (current.id !== lastId || state.results !== lastResults) {
      needs.main = true;
      lastId = current.id;
      lastResults = state.results;
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
        const sections = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_SECTIONS, "f");
        for (const sectionKey in needs) {
          const need = needs[sectionKey];
          const section = sections[sectionKey];
          if (need) {
            switch (sectionKey) {
              case "dev":
                if (isDebug) {
                  section.mount();
                  section.render();
                } else {
                  section.destroy();
                }
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
