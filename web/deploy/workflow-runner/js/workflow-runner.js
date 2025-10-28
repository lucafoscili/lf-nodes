var _a, _b;
import { g as getLfFramework } from "../../js/lf-widgets-CAA2GbO2.js";
const apiBase = "/api";
const apiRoutePrefix = "/lf-nodes";
const staticPaths = { "assets": "/lf-nodes/static/assets/" };
const polling = { "queueIntervalMs": 750, "runIntervalMs": 3e3 };
const theme$9 = "dark";
const runnerConfig = {
  apiBase,
  apiRoutePrefix,
  staticPaths,
  polling,
  theme: theme$9
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
const POLLING_INTERVALS = {
  queue: (_a = runnerConfig.polling) == null ? void 0 : _a.queueIntervalMs,
  run: (_b = runnerConfig.polling) == null ? void 0 : _b.runIntervalMs
};
const buildApiUrl = (path) => `${API_ROOT}${path.startsWith("/") ? path : `/${path}`}`;
const buildAssetsUrl = (origin = window.location.origin) => `${origin}${API_BASE}${STATIC_ASSETS_PATH.startsWith("/") ? STATIC_ASSETS_PATH : `/${STATIC_ASSETS_PATH}`}`;
const addNotification = (store, notification) => {
  store.getState().mutate.notifications.add(notification);
};
const clearResults = (store) => {
  store.getState().mutate.results(null);
};
const setResults = (store, results) => {
  store.getState().mutate.results(results);
};
const selectRun = (store, runId, options) => {
  const state = store.getState();
  state.mutate.selectRun(runId);
  const shouldClearResults = (options == null ? void 0 : options.clearResults) ?? !runId;
  if (shouldClearResults) {
    state.mutate.results(null);
  }
};
const setView = (store, view) => {
  const state = store.getState();
  if (state.view !== view) {
    state.mutate.view(view);
  }
};
const setRunInFlight = (store, runId) => {
  store.getState().mutate.runId(runId);
};
const setStatus$1 = (store, status, message) => {
  store.getState().mutate.status(status, message);
};
const upsertRun = (store, entry) => {
  store.getState().mutate.runs.upsert(entry);
};
const deepMerge = (defs, outs) => {
  var _a2, _b2;
  const prep = [];
  for (const id in defs) {
    const cell = defs[id];
    const { nodeId } = cell;
    const result = ((_a2 = outs == null ? void 0 : outs[nodeId]) == null ? void 0 : _a2.lf_output[0]) || ((_b2 = outs == null ? void 0 : outs[nodeId]) == null ? void 0 : _b2[0]) || (outs == null ? void 0 : outs[nodeId]);
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
const formatStatus = (status) => status.charAt(0).toUpperCase() + status.slice(1);
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "Unknown time";
  }
  return date.toLocaleString();
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
  WORKFLOW_CANCELLED: "Workflow run cancelled.",
  WORKFLOW_COMPLETED: "Workflow execution completed successfully.",
  WORKFLOW_STATUS_FAILED: "Failed to fetch workflow status.",
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
  RUNNING_POLLING_WORKFLOW: "Processing workflow...",
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
const runWorkflow = async (payload) => {
  const { RUN_GENERIC } = ERROR_MESSAGES;
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl("/run"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
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
const getRunStatus = async (runId) => {
  const { RUN_GENERIC } = ERROR_MESSAGES;
  const { syntax } = getLfFramework();
  const response = await fetch(buildApiUrl(`/run/${runId}/status`), { method: "GET" });
  const data = await syntax.json.parse(response);
  if (!response.ok || !data) {
    const detail = (data == null ? void 0 : data.error) || response.statusText || runId;
    throw new WorkflowApiError(`${RUN_GENERIC} (${detail})`, {
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
  files.forEach((file) => formData.append("file", file));
  const response = await fetch(buildApiUrl("/upload"), {
    method: "POST",
    body: formData
  });
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
const HOME_PLACEHOLDER = "Select a workflow to get started.";
const DEFAULT_VIEW = "workflow";
const SECTION_PRESETS = {
  home: [],
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
  home: {
    sections: () => cloneSections(SECTION_PRESETS.home),
    toRoute: () => ({ view: "home" }),
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return "home";
    }
  },
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
  workflow: {
    sections: () => cloneSections(SECTION_PRESETS.workflow),
    toRoute: buildWorkflowRoute,
    enter: (store, options) => {
      selectRunWithDefaults(store, null, options.clearResults);
      return "workflow";
    }
  }
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
const { theme: theme$8 } = getLfFramework();
const ROOT_CLASS$8 = "outputs-section";
const WORKFLOW_CLASSES$2 = {
  _: theme$8.bemClass(ROOT_CLASS$8),
  empty: theme$8.bemClass(ROOT_CLASS$8, "empty"),
  h4: theme$8.bemClass(ROOT_CLASS$8, "title-h4"),
  controls: theme$8.bemClass(ROOT_CLASS$8, "controls"),
  item: theme$8.bemClass(ROOT_CLASS$8, "item"),
  itemHeader: theme$8.bemClass(ROOT_CLASS$8, "item-header"),
  itemMeta: theme$8.bemClass(ROOT_CLASS$8, "item-meta"),
  itemTitle: theme$8.bemClass(ROOT_CLASS$8, "item-title"),
  masonry: theme$8.bemClass(ROOT_CLASS$8, "masonry"),
  status: theme$8.bemClass(ROOT_CLASS$8, "status"),
  timestamp: theme$8.bemClass(ROOT_CLASS$8, "timestamp"),
  title: theme$8.bemClass(ROOT_CLASS$8, "title")
};
const _masonry = () => {
  const masonryWrapper = document.createElement("div");
  masonryWrapper.className = WORKFLOW_CLASSES$2.masonry;
  return masonryWrapper;
};
const _formatStatus = (status) => status.charAt(0).toUpperCase() + status.slice(1);
const _formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "Unknown time";
  }
  return date.toLocaleString();
};
const _cloneOutputs = (outputs) => {
  if (!outputs) {
    return null;
  }
  try {
    return JSON.parse(JSON.stringify(outputs));
  } catch (error) {
    return outputs;
  }
};
const _title$2 = () => {
  const title = document.createElement("div");
  const h4 = document.createElement("h4");
  const controls = document.createElement("div");
  const toggle = document.createElement("lf-button");
  title.className = WORKFLOW_CLASSES$2.title;
  controls.className = WORKFLOW_CLASSES$2.controls;
  h4.className = WORKFLOW_CLASSES$2.h4;
  title.appendChild(h4);
  title.appendChild(controls);
  controls.appendChild(toggle);
  toggle.lfStyling = "flat";
  toggle.lfUiSize = "small";
  return { h4, title, controls, toggle };
};
const createOutputsSection = (store) => {
  const { WORKFLOW_OUTPUTS_DESTROYED, WORKFLOW_OUTPUTS_MOUNTED, WORKFLOW_OUTPUTS_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in WORKFLOW_CLASSES$2) {
      const element = WORKFLOW_CLASSES$2[cls];
      uiRegistry.remove(element);
    }
    debugLog(WORKFLOW_OUTPUTS_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[WORKFLOW_CLASSES$2._]) {
      return;
    }
    const _root = document.createElement("section");
    _root.className = WORKFLOW_CLASSES$2._;
    const { h4, title, toggle } = _title$2();
    const masonry = _masonry();
    _root.appendChild(title);
    _root.appendChild(masonry);
    elements[MAIN_CLASSES._].appendChild(_root);
    uiRegistry.set(WORKFLOW_CLASSES$2._, _root);
    uiRegistry.set(WORKFLOW_CLASSES$2.h4, h4);
    uiRegistry.set(WORKFLOW_CLASSES$2.masonry, masonry);
    uiRegistry.set(WORKFLOW_CLASSES$2.title, title);
    uiRegistry.set(WORKFLOW_CLASSES$2.controls, toggle);
    debugLog(WORKFLOW_OUTPUTS_MOUNTED);
  };
  const render = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const h4 = elements[WORKFLOW_CLASSES$2.h4];
    const masonry = elements[WORKFLOW_CLASSES$2.masonry];
    const toggle = elements[WORKFLOW_CLASSES$2.controls];
    if (!h4 || !masonry || !toggle) {
      return;
    }
    const workflowTitle = manager.workflow.title();
    h4.textContent = workflowTitle ? `${workflowTitle} outputs` : "Workflow outputs";
    masonry.replaceChildren();
    const runs = manager.runs.all();
    const selectedRunId = state.selectedRunId;
    const isHistoryView = state.view === "history";
    toggle.lfLabel = isHistoryView ? "Back to workflow view" : "Open full history";
    toggle.toggleAttribute("disabled", !runs.length && !isHistoryView);
    toggle.onclick = () => {
      if (isHistoryView) {
        manager.runs.select(null, "workflow");
      } else {
        manager.runs.select(null, "history");
      }
    };
    if (!runs.length) {
      const empty = document.createElement("p");
      empty.className = WORKFLOW_CLASSES$2.empty;
      empty.textContent = "Run a workflow to start building your history.";
      masonry.appendChild(empty);
      debugLog(WORKFLOW_OUTPUTS_UPDATED);
      return;
    }
    for (const run of runs) {
      const item = document.createElement("button");
      item.type = "button";
      item.className = WORKFLOW_CLASSES$2.item;
      item.dataset.runId = run.runId;
      item.dataset.status = run.status;
      item.dataset.selected = String(run.runId === selectedRunId);
      item.setAttribute("aria-pressed", String(run.runId === selectedRunId));
      const header = document.createElement("div");
      header.className = WORKFLOW_CLASSES$2.itemHeader;
      const title = document.createElement("span");
      title.className = WORKFLOW_CLASSES$2.itemTitle;
      title.textContent = run.workflowName || workflowTitle || "Workflow run";
      const status = document.createElement("span");
      status.className = WORKFLOW_CLASSES$2.status;
      status.textContent = _formatStatus(run.status);
      status.dataset.state = run.status;
      header.appendChild(title);
      header.appendChild(status);
      const meta = document.createElement("div");
      meta.className = WORKFLOW_CLASSES$2.itemMeta;
      const timestamp = document.createElement("span");
      timestamp.className = WORKFLOW_CLASSES$2.timestamp;
      timestamp.textContent = _formatTimestamp(run.updatedAt || run.createdAt);
      meta.appendChild(timestamp);
      if (run.error) {
        const error = document.createElement("span");
        error.className = WORKFLOW_CLASSES$2.status;
        error.dataset.state = "error";
        error.textContent = run.error;
        meta.appendChild(error);
      }
      item.appendChild(header);
      item.appendChild(meta);
      item.addEventListener("click", () => {
        manager.runs.select(run.runId, "run");
        const selected = manager.runs.get(run.runId);
        const selectedOutputs = _cloneOutputs((selected == null ? void 0 : selected.outputs) ?? null);
        store.getState().mutate.results(selectedOutputs);
      });
      masonry.appendChild(item);
    }
    debugLog(WORKFLOW_OUTPUTS_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const { theme: theme$7 } = getLfFramework();
const ROOT_CLASS$7 = "results-section";
const WORKFLOW_CLASSES$1 = {
  _: theme$7.bemClass(ROOT_CLASS$7),
  actions: theme$7.bemClass(ROOT_CLASS$7, "actions"),
  back: theme$7.bemClass(ROOT_CLASS$7, "back"),
  description: theme$7.bemClass(ROOT_CLASS$7, "description"),
  empty: theme$7.bemClass(ROOT_CLASS$7, "empty"),
  grid: theme$7.bemClass(ROOT_CLASS$7, "grid"),
  h3: theme$7.bemClass(ROOT_CLASS$7, "title-h3"),
  history: theme$7.bemClass(ROOT_CLASS$7, "history"),
  item: theme$7.bemClass(ROOT_CLASS$7, "item"),
  results: theme$7.bemClass(ROOT_CLASS$7, "results"),
  title: theme$7.bemClass(ROOT_CLASS$7, "title")
};
const _formatDescription = (selectedRun, description) => {
  return selectedRun ? `Run ${selectedRun.runId.slice(0, 8)} • ${formatStatus(selectedRun.status)} • ${formatTimestamp(selectedRun.updatedAt || selectedRun.createdAt)}` : description;
};
const _description$1 = () => {
  const p = document.createElement("p");
  p.className = WORKFLOW_CLASSES$1.description;
  return p;
};
const _results = () => {
  const cellWrapper = document.createElement("div");
  cellWrapper.className = WORKFLOW_CLASSES$1.results;
  return cellWrapper;
};
const _title$1 = (store) => {
  const { manager } = store.getState();
  const title = document.createElement("div");
  const h3 = document.createElement("h3");
  const actions = document.createElement("div");
  const backButton = document.createElement("lf-button");
  const historyButton = document.createElement("lf-button");
  title.className = WORKFLOW_CLASSES$1.title;
  actions.className = WORKFLOW_CLASSES$1.actions;
  h3.className = WORKFLOW_CLASSES$1.h3;
  backButton.className = WORKFLOW_CLASSES$1.back;
  historyButton.className = WORKFLOW_CLASSES$1.history;
  backButton.lfLabel = "Back to workflow";
  backButton.lfStyling = "flat";
  backButton.lfUiSize = "small";
  backButton.onclick = () => manager.runs.select(null, "workflow");
  backButton.toggleAttribute("disabled", true);
  historyButton.lfLabel = "View all runs";
  historyButton.lfStyling = "flat";
  historyButton.lfUiSize = "small";
  historyButton.onclick = () => manager.runs.select(null, "history");
  historyButton.toggleAttribute("disabled", manager.runs.all().length === 0);
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
    for (const cls in WORKFLOW_CLASSES$1) {
      const element = WORKFLOW_CLASSES$1[cls];
      uiRegistry.remove(element);
    }
    debugLog(WORKFLOW_RESULTS_DESTROYED);
  };
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (elements && elements[WORKFLOW_CLASSES$1._]) {
      return;
    }
    const _root = document.createElement("section");
    _root.className = WORKFLOW_CLASSES$1._;
    const results = _results();
    const description = _description$1();
    const { actions, backButton, h3, historyButton, title } = _title$1(store);
    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(results);
    elements[MAIN_CLASSES._].appendChild(_root);
    uiRegistry.set(WORKFLOW_CLASSES$1._, _root);
    uiRegistry.set(WORKFLOW_CLASSES$1.actions, actions);
    uiRegistry.set(WORKFLOW_CLASSES$1.back, backButton);
    uiRegistry.set(WORKFLOW_CLASSES$1.description, description);
    uiRegistry.set(WORKFLOW_CLASSES$1.h3, h3);
    uiRegistry.set(WORKFLOW_CLASSES$1.history, historyButton);
    uiRegistry.set(WORKFLOW_CLASSES$1.results, results);
    uiRegistry.set(WORKFLOW_CLASSES$1.title, title);
    debugLog(WORKFLOW_RESULTS_MOUNTED);
  };
  const render = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    const descr = elements[WORKFLOW_CLASSES$1.description];
    const element = elements[WORKFLOW_CLASSES$1.results];
    const h3 = elements[WORKFLOW_CLASSES$1.h3];
    const selectedRun = manager.runs.selected();
    const runs = manager.runs.all();
    const backButton = elements[WORKFLOW_CLASSES$1.back];
    const historyButton = elements[WORKFLOW_CLASSES$1.history];
    backButton == null ? void 0 : backButton.toggleAttribute("disabled", !selectedRun);
    historyButton == null ? void 0 : historyButton.toggleAttribute("disabled", runs.length === 0);
    descr.textContent = _formatDescription(selectedRun, manager.workflow.description());
    h3.textContent = (selectedRun == null ? void 0 : selectedRun.workflowName) || manager.workflow.title();
    const outputs = state.results ?? (selectedRun == null ? void 0 : selectedRun.outputs) ?? null;
    clearChildren(element);
    const nodeIds = outputs ? Object.keys(outputs) : [];
    if (nodeIds.length === 0) {
      const empty = document.createElement("p");
      empty.className = WORKFLOW_CLASSES$1.empty;
      empty.textContent = selectedRun ? "This run has not produced any outputs yet." : "Select a run to inspect its outputs.";
      element.appendChild(empty);
      return;
    }
    const workflow = manager.workflow.current();
    const outputsDefs = workflow ? manager.workflow.cells("output") : {};
    const prepOutputs = deepMerge(outputsDefs, outputs || {});
    for (let i = 0; i < prepOutputs.length; i++) {
      const output = prepOutputs[i];
      const { id, nodeId, title } = output;
      const h4 = document.createElement("h4");
      h4.className = WORKFLOW_CLASSES$1.title;
      h4.textContent = title || `Node #${nodeId}`;
      element.appendChild(h4);
      const grid = document.createElement("div");
      grid.className = WORKFLOW_CLASSES$1.grid;
      element.appendChild(grid);
      const wrapper = document.createElement("div");
      wrapper.className = WORKFLOW_CLASSES$1.item;
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
const { theme: theme$6 } = getLfFramework();
const ROOT_CLASS$6 = "main-section";
const MAIN_CLASSES = {
  _: theme$6.bemClass(ROOT_CLASS$6),
  home: theme$6.bemClass(ROOT_CLASS$6, "home")
};
const createMainSection = (store) => {
  const { MAIN_DESTROYED, MAIN_MOUNTED, MAIN_UPDATED } = DEBUG_MESSAGES;
  const INPUTS = createInputsSection(store);
  const OUTPUTS = createOutputsSection(store);
  const RESULTS = createResultsSection(store);
  let LAST_SCOPE = [];
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in MAIN_CLASSES) {
      const element = MAIN_CLASSES[cls];
      uiRegistry.remove(element);
    }
    INPUTS.destroy();
    OUTPUTS.destroy();
    RESULTS.destroy();
    uiRegistry.remove(MAIN_CLASSES.home);
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
    debugLog(MAIN_MOUNTED);
  };
  const render = (scope) => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;
    const resolvedSections = scope ?? resolveMainSections(state);
    const scopeSet = new Set(resolvedSections);
    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }
    LAST_SCOPE.forEach((section) => {
      if (!scopeSet.has(section)) {
        switch (section) {
          case "inputs":
            INPUTS.destroy();
            break;
          case "outputs":
            OUTPUTS.destroy();
            break;
          case "results":
            RESULTS.destroy();
            break;
        }
      }
    });
    scopeSet.forEach((section) => {
      switch (section) {
        case "inputs":
          if (!LAST_SCOPE.find((s) => s === "inputs")) {
            INPUTS.mount();
          }
          INPUTS.render();
          break;
        case "outputs":
          if (!LAST_SCOPE.find((s) => s === "outputs")) {
            OUTPUTS.mount();
          }
          OUTPUTS.render();
          break;
        case "results":
          if (!LAST_SCOPE.find((s) => s === "results")) {
            RESULTS.mount();
          }
          RESULTS.render();
          break;
      }
    });
    if (resolvedSections.length === 0) {
      if (!elements[MAIN_CLASSES.home]) {
        const placeholder = document.createElement("div");
        placeholder.className = MAIN_CLASSES.home;
        placeholder.textContent = HOME_PLACEHOLDER;
        const root = elements[MAIN_CLASSES._];
        if (root) {
          root.appendChild(placeholder);
          uiRegistry.set(MAIN_CLASSES.home, placeholder);
        }
      }
    } else {
      uiRegistry.remove(MAIN_CLASSES.home);
    }
    LAST_SCOPE = Array.from(scopeSet);
    debugLog(MAIN_UPDATED);
  };
  return {
    destroy,
    mount,
    render
  };
};
const { theme: theme$5 } = getLfFramework();
const ROOT_CLASS$5 = "inputs-section";
const WORKFLOW_CLASSES = {
  _: theme$5.bemClass(ROOT_CLASS$5),
  cell: theme$5.bemClass(ROOT_CLASS$5, "cell"),
  cells: theme$5.bemClass(ROOT_CLASS$5, "cells"),
  description: theme$5.bemClass(ROOT_CLASS$5, "description"),
  h3: theme$5.bemClass(ROOT_CLASS$5, "title-h3"),
  openButton: theme$5.bemClass(ROOT_CLASS$5, "title-open-button"),
  options: theme$5.bemClass(ROOT_CLASS$5, "options"),
  title: theme$5.bemClass(ROOT_CLASS$5, "title")
};
const _cells = () => {
  const cellWrapper = document.createElement("div");
  cellWrapper.className = WORKFLOW_CLASSES.cell;
  return cellWrapper;
};
const _description = () => {
  const p = document.createElement("p");
  p.className = WORKFLOW_CLASSES.description;
  return p;
};
const _options = () => {
  const optionsWrapper = document.createElement("div");
  optionsWrapper.className = WORKFLOW_CLASSES.options;
  return optionsWrapper;
};
const _title = (store) => {
  const lfIcon = theme$5.get.icon("download");
  const title = document.createElement("div");
  const h3 = document.createElement("h3");
  const openButton = document.createElement("lf-button");
  title.className = WORKFLOW_CLASSES.title;
  h3.className = WORKFLOW_CLASSES.h3;
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
const createInputsSection = (store) => {
  const { WORKFLOW_INPUTS_DESTROYED, WORKFLOW_INPUTS_MOUNTED, WORKFLOW_INPUTS_UPDATED } = DEBUG_MESSAGES;
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;
    for (const cls in WORKFLOW_CLASSES) {
      const element = WORKFLOW_CLASSES[cls];
      uiRegistry.remove(element);
    }
    debugLog(WORKFLOW_INPUTS_DESTROYED);
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
    const description = _description();
    const options = _options();
    const { h3, openButton, title } = _title(store);
    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(options);
    elements[MAIN_CLASSES._].appendChild(_root);
    uiRegistry.set(WORKFLOW_CLASSES._, _root);
    uiRegistry.set(WORKFLOW_CLASSES.description, description);
    uiRegistry.set(WORKFLOW_CLASSES.h3, h3);
    uiRegistry.set(WORKFLOW_CLASSES.openButton, openButton);
    uiRegistry.set(WORKFLOW_CLASSES.options, options);
    uiRegistry.set(WORKFLOW_CLASSES.title, title);
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
    const descr = elements[WORKFLOW_CLASSES.description];
    const h3 = elements[WORKFLOW_CLASSES.h3];
    const options = elements[WORKFLOW_CLASSES.options];
    descr.textContent = manager.workflow.description();
    h3.textContent = manager.workflow.title();
    clearChildren(options);
    const workflow = manager.workflow.current();
    const statuses = state.inputStatuses || {};
    const cellElements = [];
    if (workflow) {
      const inputCells = manager.workflow.cells("input");
      for (const id in inputCells) {
        if (!Object.prototype.hasOwnProperty.call(inputCells, id)) {
          continue;
        }
        const cell = inputCells[id];
        const wrapper = _cells();
        const component = createInputCell(cell);
        component.id = id;
        const status = statuses[id] || "";
        if (status) {
          wrapper.dataset.status = status;
        } else {
          delete wrapper.dataset.status;
        }
        cellElements.push(component);
        wrapper.appendChild(component);
        options.appendChild(wrapper);
      }
    }
    uiRegistry.set(WORKFLOW_CLASSES.cells, cellElements);
    debugLog(WORKFLOW_INPUTS_UPDATED);
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
  var _a2;
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
  const cells = (elements == null ? void 0 : elements[WORKFLOW_CLASSES.cells]) || [];
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
  var _a2, _b2, _c, _d, _e;
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
    const detail = error instanceof WorkflowApiError ? ((_a2 = error.payload) == null ? void 0 : _a2.detail) || error.message : (error == null ? void 0 : error.message) || "Failed to collect inputs.";
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
    const workflowName = ((_b2 = state.manager) == null ? void 0 : _b2.workflow.title()) ?? id;
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
    setRunInFlight(store, runId);
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
    card.lfDataset = _createDataset$1();
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
  var _a2, _b2;
  const categories = [];
  const root = { id: "workflows", value: "Workflows", children: categories };
  const clone = JSON.parse(JSON.stringify(workflows));
  (_a2 = clone.nodes) == null ? void 0 : _a2.forEach((child) => {
    child.children = void 0;
  });
  (_b2 = clone.nodes) == null ? void 0 : _b2.forEach((node) => {
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
const _defaultQueueFetcher = async () => {
  const resp = await fetch("/queue");
  if (!resp.ok) {
    throw new Error("Failed to fetch queue status");
  }
  return await resp.json();
};
const createPollingController = ({ fetchQueueStatus = _defaultQueueFetcher, getRunStatus: getRunStatus$1 = getRunStatus, queueIntervalMs = POLLING_INTERVALS.queue, runIntervalMs = POLLING_INTERVALS.run, runLifecycle, store }) => {
  let queueTimerId = null;
  let runTimerId = null;
  let isRunPolling = false;
  let activeRunId = null;
  const stopRunPolling = () => {
    if (typeof runTimerId === "number") {
      window.clearInterval(runTimerId);
      runTimerId = null;
    }
    const state = store.getState();
    if (state.pollingTimer !== null) {
      state.mutate.pollingTimer(null);
    }
    activeRunId = null;
    isRunPolling = false;
  };
  const stopQueuePolling = () => {
    if (queueTimerId !== null) {
      window.clearInterval(queueTimerId);
      queueTimerId = null;
    }
  };
  const beginRunPolling = (runId) => {
    stopRunPolling();
    activeRunId = runId;
    const poll = () => {
      if (activeRunId) {
        void pollRun(activeRunId);
      }
    };
    poll();
    runTimerId = window.setInterval(poll, runIntervalMs);
    store.getState().mutate.pollingTimer(Number(runTimerId));
  };
  const pollRun = async (runId) => {
    if (isRunPolling) {
      return;
    }
    const currentState = store.getState();
    if (currentState.currentRunId !== runId) {
      return;
    }
    isRunPolling = true;
    try {
      const response = await getRunStatus$1(runId);
      const { shouldStopPolling } = runLifecycle.handleStatusResponse(response);
      if (shouldStopPolling) {
        stopRunPolling();
      }
    } catch (error) {
      const { shouldStopPolling } = runLifecycle.handlePollingError(error);
      if (shouldStopPolling) {
        stopRunPolling();
      }
    } finally {
      isRunPolling = false;
    }
  };
  const startQueuePolling = () => {
    if (queueTimerId !== null) {
      return;
    }
    const poll = () => {
      void pollQueue();
    };
    poll();
    queueTimerId = window.setInterval(poll, queueIntervalMs);
  };
  const pollQueue = async () => {
    try {
      const { queue_pending, queue_running } = await fetchQueueStatus();
      const state = store.getState();
      const qPending = parseCount(queue_pending);
      const qRunning = parseCount(queue_running);
      const busy = qPending + qRunning;
      const prev = state.queuedJobs ?? -1;
      if (busy !== prev) {
        state.mutate.queuedJobs(busy);
      }
    } catch (error) {
      const state = store.getState();
      const prev = state.queuedJobs ?? -1;
      if (prev !== -1) {
        state.mutate.queuedJobs(-1);
      }
    }
  };
  return {
    beginRunPolling,
    startQueuePolling,
    stopQueuePolling,
    stopRunPolling
  };
};
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
    if (isApplyingRoute) {
      return;
    }
    const nextRoute = precomputed ?? computeRouteFromState(store.getState());
    if (!routesEqual(nextRoute, currentRoute)) {
      currentRoute = nextRoute;
      replaceRouteInHistory(nextRoute);
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
      let workflowId = route.workflowId ?? null;
      if (workflowId && workflowExists(workflowId) && state.current.id !== workflowId) {
        state.mutate.workflow(workflowId);
      } else if (workflowId && !workflowExists(workflowId)) {
        workflowId = state.current.id ?? null;
      }
      const normalizedRoute = {
        view: route.view,
        workflowId: workflowId ?? void 0,
        runId: route.runId ?? void 0
      };
      changeView(store, normalizedRoute.view, {
        runId: normalizedRoute.runId ?? null,
        clearResults: normalizedRoute.view === "run" ? false : void 0
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
    currentRoute = parseRouteFromLocation();
    pendingRoute = currentRoute;
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
const _coerceTimestamp = (value, fallback) => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value > 1e12 ? Math.round(value) : Math.round(value * 1e3);
  }
  return fallback;
};
const _extractRunOutputs = (response) => {
  var _a2, _b2, _c, _d;
  const outputs = (_d = (_c = (_b2 = (_a2 = response.result) == null ? void 0 : _a2.body) == null ? void 0 : _b2.payload) == null ? void 0 : _c.history) == null ? void 0 : _d.outputs;
  if (!outputs) {
    return null;
  }
  return { ...outputs };
};
const createRunLifecycle = ({ setInputStatus, store }) => {
  const { WORKFLOW_COMPLETED, WORKFLOW_STATUS_FAILED, WORKFLOW_CANCELLED } = NOTIFICATION_MESSAGES;
  const updateProgress = (response) => {
    var _a2;
    const now = Date.now();
    upsertRun(store, {
      runId: response.run_id,
      createdAt: _coerceTimestamp(response.created_at, now),
      updatedAt: now,
      status: response.status,
      error: response.error ?? null,
      httpStatus: ((_a2 = response.result) == null ? void 0 : _a2.http_status) ?? null,
      resultPayload: response.result ?? null
    });
  };
  const handleRunSuccess = (response) => {
    var _a2;
    const runId = response.run_id;
    const outputs = _extractRunOutputs(response);
    const now = Date.now();
    upsertRun(store, {
      runId,
      createdAt: _coerceTimestamp(response.created_at, now),
      updatedAt: now,
      status: "succeeded",
      error: null,
      outputs,
      httpStatus: ((_a2 = response.result) == null ? void 0 : _a2.http_status) ?? null,
      resultPayload: response.result ?? null
    });
    setResults(store, outputs);
    addNotification(store, {
      id: performance.now().toString(),
      message: WORKFLOW_COMPLETED,
      status: "success"
    });
    setStatus$1(store, "idle", STATUS_MESSAGES.IDLE);
  };
  const handleRunFailure = (response) => {
    var _a2, _b2, _c, _d, _e, _f;
    const payload = (_b2 = (_a2 = response.result) == null ? void 0 : _a2.body) == null ? void 0 : _b2.payload;
    const runId = response.run_id;
    const detail = (payload == null ? void 0 : payload.detail) || ((_c = payload == null ? void 0 : payload.error) == null ? void 0 : _c.message) || response.error || STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW;
    const outputs = _extractRunOutputs(response);
    const now = Date.now();
    const hasInputError = Boolean((_d = payload == null ? void 0 : payload.error) == null ? void 0 : _d.input);
    upsertRun(store, {
      runId,
      createdAt: _coerceTimestamp(response.created_at, now),
      updatedAt: now,
      status: "failed",
      error: detail,
      outputs,
      httpStatus: ((_e = response.result) == null ? void 0 : _e.http_status) ?? null,
      resultPayload: response.result ?? null
    });
    if (hasInputError) {
      if ((_f = payload == null ? void 0 : payload.error) == null ? void 0 : _f.input) {
        setInputStatus == null ? void 0 : setInputStatus(payload.error.input, "error");
      }
    } else {
      setResults(store, outputs);
    }
    addNotification(store, {
      id: performance.now().toString(),
      message: `Workflow run failed: ${detail}`,
      status: "danger"
    });
    setStatus$1(store, "error", STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW);
  };
  const handleRunCancellation = (response) => {
    var _a2;
    const runId = response.run_id;
    const outputs = _extractRunOutputs(response);
    const message = response.error || WORKFLOW_CANCELLED;
    const now = Date.now();
    upsertRun(store, {
      runId,
      createdAt: _coerceTimestamp(response.created_at, now),
      updatedAt: now,
      status: "cancelled",
      error: message,
      outputs,
      httpStatus: ((_a2 = response.result) == null ? void 0 : _a2.http_status) ?? null,
      resultPayload: response.result ?? null
    });
    setResults(store, outputs);
    addNotification(store, {
      id: performance.now().toString(),
      message,
      status: "warning"
    });
    setStatus$1(store, "idle", STATUS_MESSAGES.IDLE);
  };
  const handleStatusResponse = (response) => {
    const state = store.getState();
    updateProgress(response);
    const { status } = response;
    switch (status) {
      case "cancelled":
        handleRunCancellation(response);
        break;
      case "failed":
        handleRunFailure(response);
        break;
      case "pending":
      case "running":
        if (state.current.status !== "running" || state.current.message !== STATUS_MESSAGES.RUNNING_POLLING_WORKFLOW) {
          setStatus$1(store, "running", STATUS_MESSAGES.RUNNING_POLLING_WORKFLOW);
        }
        break;
      case "succeeded":
        handleRunSuccess(response);
        break;
    }
    if (status === "succeeded" || status === "failed" || status === "cancelled") {
      setRunInFlight(store, null);
      return { shouldStopPolling: true };
    }
    return { shouldStopPolling: false };
  };
  const handlePollingError = (error) => {
    const state = store.getState();
    const detail = error instanceof Error ? error.message : STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW;
    setStatus$1(store, "error", STATUS_MESSAGES.ERROR_RUNNING_WORKFLOW);
    addNotification(store, {
      id: performance.now().toString(),
      message: `${WORKFLOW_STATUS_FAILED}: ${detail}`,
      status: "danger"
    });
    const runId = state.currentRunId;
    if (runId) {
      const now = Date.now();
      upsertRun(store, {
        runId,
        updatedAt: now,
        status: "failed",
        error: detail
      });
      if (state.selectedRunId === runId) {
        setResults(store, null);
      }
    }
    setRunInFlight(store, null);
    return { shouldStopPolling: true };
  };
  return {
    handlePollingError,
    handleStatusResponse,
    updateProgress
  };
};
const INIT_ERROR = "Mutate not initialized";
const INIT_CB = () => {
  throw new Error(INIT_ERROR);
};
const initState = () => ({
  current: { status: "idle", message: "", id: null },
  currentRunId: null,
  isDebug: false,
  manager: null,
  inputStatuses: {},
  pollingTimer: null,
  queuedJobs: -1,
  runs: [],
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
    pollingTimer: INIT_CB,
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
  results: null,
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
    pollingTimer: (timerId) => applyMutation((draft) => {
      draft.pollingTimer = timerId;
    }),
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
          draft.runs[existingIndex] = {
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
        } else {
          const createdAt = entry.createdAt ?? now;
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
            ...draft.runs.filter((run) => run.runId !== entry.runId)
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
var _LfWorkflowRunnerManager_instances, _LfWorkflowRunnerManager_APP_ROOT, _LfWorkflowRunnerManager_DISPATCHERS, _LfWorkflowRunnerManager_FRAMEWORK, _LfWorkflowRunnerManager_POLLING, _LfWorkflowRunnerManager_ROUTING, _LfWorkflowRunnerManager_RUN_LIFECYCLE, _LfWorkflowRunnerManager_SECTIONS, _LfWorkflowRunnerManager_STORE, _LfWorkflowRunnerManager_UI_REGISTRY, _LfWorkflowRunnerManager_initializeFramework, _LfWorkflowRunnerManager_initializeLayout, _LfWorkflowRunnerManager_loadWorkflows, _LfWorkflowRunnerManager_setInputStatus, _LfWorkflowRunnerManager_subscribeToState;
class LfWorkflowRunnerManager {
  constructor() {
    _LfWorkflowRunnerManager_instances.add(this);
    _LfWorkflowRunnerManager_APP_ROOT.set(this, void 0);
    _LfWorkflowRunnerManager_DISPATCHERS.set(this, void 0);
    _LfWorkflowRunnerManager_FRAMEWORK.set(this, getLfFramework());
    _LfWorkflowRunnerManager_POLLING.set(this, void 0);
    _LfWorkflowRunnerManager_ROUTING.set(this, void 0);
    _LfWorkflowRunnerManager_RUN_LIFECYCLE.set(this, void 0);
    _LfWorkflowRunnerManager_SECTIONS.set(this, void 0);
    _LfWorkflowRunnerManager_STORE.set(this, void 0);
    _LfWorkflowRunnerManager_UI_REGISTRY.set(this, /* @__PURE__ */ new WeakMap());
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
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_RUN_LIFECYCLE, createRunLifecycle({
      store: __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f"),
      setInputStatus: (inputId, status) => {
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_setInputStatus).call(this, inputId, status);
      }
    }), "f");
    __classPrivateFieldSet(this, _LfWorkflowRunnerManager_POLLING, createPollingController({
      runLifecycle: __classPrivateFieldGet(this, _LfWorkflowRunnerManager_RUN_LIFECYCLE, "f"),
      store: __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STORE, "f")
    }), "f");
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
      state.mutate.notifications.add({
        id: performance.now().toString(),
        message: error instanceof Error ? error.message : WORKFLOWS_LOAD_FAILED,
        status: "danger"
      });
      state.mutate.status("error", ERROR_FETCHING_WORKFLOWS);
    }).then(() => {
      state.mutate.status("idle", IDLE_WORKFLOWS_LOADED);
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ROUTING, "f").updateRouteFromState();
    });
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_POLLING, "f").startQueuePolling();
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
_LfWorkflowRunnerManager_APP_ROOT = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_DISPATCHERS = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_FRAMEWORK = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_POLLING = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_ROUTING = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_RUN_LIFECYCLE = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_SECTIONS = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_STORE = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_UI_REGISTRY = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_loadWorkflows = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_instances = /* @__PURE__ */ new WeakSet(), _LfWorkflowRunnerManager_initializeFramework = function _LfWorkflowRunnerManager_initializeFramework2() {
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
}, _LfWorkflowRunnerManager_setInputStatus = function _LfWorkflowRunnerManager_setInputStatus2(inputId, status) {
  const elements = this.uiRegistry.get();
  const cells = (elements == null ? void 0 : elements[WORKFLOW_CLASSES.cells]) || [];
  const cell = cells.find((el) => el.id === inputId);
  const wrapper = cell == null ? void 0 : cell.parentElement;
  if (wrapper) {
    wrapper.dataset.status = status;
  }
}, _LfWorkflowRunnerManager_subscribeToState = function _LfWorkflowRunnerManager_subscribeToState2() {
  var _a2, _b2, _c;
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
  let lastSelectedRunId = st.selectedRunId;
  let lastView = st.view;
  let lastWorkflowsCount = ((_c = (_b2 = st.workflows) == null ? void 0 : _b2.nodes) == null ? void 0 : _c.length) ?? 0;
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
      if (state.currentRunId) {
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_POLLING, "f").beginRunPolling(state.currentRunId);
      } else {
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_POLLING, "f").stopRunPolling();
      }
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
