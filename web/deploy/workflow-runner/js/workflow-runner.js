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
const STATIC_ASSETS_PATH = runnerConfig.staticPaths.assets;
const DEFAULT_THEME = runnerConfig.theme;
const DEFAULT_STATUS_MESSAGES = {
  ready: "Ready.",
  running: "Running...",
  error: "An error occurred while running the workflow."
};
const buildApiUrl = (path) => `${API_ROOT}${path.startsWith("/") ? path : `/${path}`}`;
const buildAssetsUrl = (origin = window.location.origin) => `${origin}${API_BASE}${STATIC_ASSETS_PATH.startsWith("/") ? STATIC_ASSETS_PATH : `/${STATIC_ASSETS_PATH}`}`;
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
  if (!data || !Array.isArray(data.workflows)) {
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
const ROOT_CLASS$3 = "drawer-section";
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
    ui.layout.drawer._root = element;
    (_a = ui.layout._root) == null ? void 0 : _a.appendChild(element);
  };
  const render = () => {
  };
  const destroy = () => {
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.ui.layout.drawer._root = null;
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
        lfStretchX: true
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
const createInputField = (field) => {
  const { component, default: lfValue, description, extra: lfHtmlAttributes, label: lfLabel } = field;
  const { sanitizeProps } = getLfFramework();
  const safeHtmlAttributes = sanitizeProps(lfHtmlAttributes);
  switch (component) {
    case "lf-toggle": {
      return createComponent.toggle({
        lfAriaLabel: lfLabel,
        lfLabel,
        lfValue: Boolean(lfValue ?? false)
      });
    }
    case "lf-upload": {
      return createComponent.upload({
        lfLabel
      });
    }
    default:
    case "lf-textfield": {
      return createComponent.textfield({
        lfHelper: { value: description ?? "", showWhenFocused: false },
        lfHtmlAttributes: safeHtmlAttributes,
        lfLabel,
        lfValue: String(lfValue ?? "")
      });
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
const _drawerToggle = () => {
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
  return drawerToggle;
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
    const drawerToggle = _drawerToggle();
    ui.layout.header.drawerToggle = drawerToggle;
    element.appendChild(container);
    container.appendChild(drawerToggle);
    ui.layout.header._root = element;
    (_a = ui.layout._root) == null ? void 0 : _a.appendChild(element);
  };
  const render = () => {
  };
  const destroy = () => {
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.ui.layout.header._root = null;
      lastState.ui.layout.header.drawerToggle = null;
      lastState.ui.layout.header.themeSwitch = null;
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
    ui.layout.main._root = element;
    (_a = ui.layout._root) == null ? void 0 : _a.appendChild(element);
  };
  const render = () => {
  };
  const destroy = () => {
    element == null ? void 0 : element.remove();
    if (lastState) {
      lastState.ui.layout.main._root = null;
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
  const { current, workflows } = state;
  return workflows.find((wf) => wf.id === current.workflow) || null;
};
const getWorkflowLabel = (state) => {
  const workflow = getCurrentWorkflow(state);
  return (workflow == null ? void 0 : workflow.label) || WORKFLOW_TEXT;
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
  h3.textContent = getWorkflowLabel(state);
  return h3;
};
const createWorkflowSection = () => {
  let section = null;
  let optionsWrapper = null;
  let resultWrapper = null;
  let runButton = null;
  let statusWrapper = null;
  let titleElement = null;
  let lastWorkflowId = null;
  let lastStatus = null;
  let lastMessage = null;
  let lastResultsRef = null;
  let mountedState = null;
  const mount = (state) => {
    var _a;
    mountedState = state;
    const { ui } = state;
    section = document.createElement("section");
    section.className = ROOT_CLASS;
    titleElement = createTitle(state);
    optionsWrapper = createOptionsWrapper();
    runButton = createRunButton(state);
    statusWrapper = createStatusWrapper("info");
    resultWrapper = createResultWrapper();
    ui.layout.main.workflow._root = section;
    ui.layout.main.workflow.options = optionsWrapper;
    ui.layout.main.workflow.result = resultWrapper;
    ui.layout.main.workflow.run = runButton;
    ui.layout.main.workflow.status = statusWrapper;
    ui.layout.main.workflow.title = titleElement;
    section.appendChild(titleElement);
    section.appendChild(optionsWrapper);
    section.appendChild(runButton);
    section.appendChild(statusWrapper);
    section.appendChild(resultWrapper);
    (_a = ui.layout.main._root) == null ? void 0 : _a.appendChild(section);
  };
  const updateOptions = (state) => {
    const { ui } = state;
    const element = ui.layout.main.workflow.options;
    if (!element) {
      return;
    }
    clearChildren(element);
    ui.layout.main.workflow.fields = [];
    const workflow = getCurrentWorkflow(state);
    if (!workflow || !workflow.fields) {
      return;
    }
    for (const field of workflow.fields) {
      const wrapper = createFieldWrapper();
      const fieldElement = createInputField(field);
      fieldElement.dataset.name = field.name;
      ui.layout.main.workflow.fields.push(fieldElement);
      wrapper.appendChild(fieldElement);
      element.appendChild(wrapper);
    }
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
    element.textContent = getWorkflowLabel(state);
  };
  const render = (state) => {
    if (!section) {
      return;
    }
    if (state.current.workflow !== lastWorkflowId) {
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
  const setFieldStatus = (state, name, status = "") => {
    const { ui } = state;
    const field = ui.layout.main.workflow.fields.find((el) => el.dataset.name === name);
    const wrapper = field == null ? void 0 : field.parentElement;
    if (wrapper) {
      wrapper.dataset.status = status;
    }
  };
  const destroy = () => {
    section == null ? void 0 : section.remove();
    if (mountedState) {
      const wf = mountedState.ui.layout.main.workflow;
      wf._root = null;
      wf.fields = [];
      wf.options = null;
      wf.result = null;
      wf.run = null;
      wf.status = null;
      wf.title = null;
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
    setFieldStatus
  };
};
const createWorkflowRunnerStore = (initialState) => {
  let state = initialState;
  const listeners = /* @__PURE__ */ new Set();
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
  return {
    getState,
    setState,
    subscribe
  };
};
const initState = (appContainer) => ({
  current: { status: "ready", message: "Ready.", workflow: null, preferredOutput: null },
  manager: null,
  ui: {
    layout: {
      _root: appContainer,
      drawer: {
        _root: null
      },
      header: {
        _root: null,
        drawerToggle: null,
        themeSwitch: null
      },
      main: {
        _root: null,
        title: { _root: null },
        workflow: {
          _root: null,
          fields: [],
          options: null,
          result: null,
          run: null,
          status: null,
          title: null
        }
      }
    }
  },
  workflows: [],
  results: null
});
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
var _LfWorkflowRunnerManager_instances, _LfWorkflowRunnerManager_framework, _LfWorkflowRunnerManager_store, _LfWorkflowRunnerManager_sections, _LfWorkflowRunnerManager_collectInputs, _LfWorkflowRunnerManager_handleUploadField, _LfWorkflowRunnerManager_initializeFramework, _LfWorkflowRunnerManager_initializeLayout, _LfWorkflowRunnerManager_subscribeToState, _LfWorkflowRunnerManager_loadWorkflows;
class LfWorkflowRunnerManager {
  constructor() {
    _LfWorkflowRunnerManager_instances.add(this);
    _LfWorkflowRunnerManager_framework.set(this, getLfFramework());
    _LfWorkflowRunnerManager_store.set(this, void 0);
    _LfWorkflowRunnerManager_sections.set(this, void 0);
    _LfWorkflowRunnerManager_collectInputs.set(this, async () => {
      const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState();
      const { fields } = state.ui.layout.main.workflow;
      const inputs = {};
      for (const element of fields) {
        const fieldName = element.dataset.name || "";
        if (!fieldName) {
          continue;
        }
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.setFieldStatus(state, fieldName);
        const value = await element.getValue();
        switch (element.tagName.toLowerCase()) {
          case "lf-toggle":
            inputs[fieldName] = value === "off" ? false : true;
            break;
          case "lf-upload":
            inputs[fieldName] = await __classPrivateFieldGet(this, _LfWorkflowRunnerManager_handleUploadField, "f").call(this, fieldName, value);
            break;
          default:
            inputs[fieldName] = value;
        }
      }
      return inputs;
    });
    _LfWorkflowRunnerManager_handleUploadField.set(this, async (fieldName, rawValue) => {
      var _a;
      const files = Array.isArray(rawValue) ? rawValue : rawValue;
      if (!files || files.length === 0) {
        return [];
      }
      try {
        this.setStatus("running", "Uploading file...");
        const { payload } = await uploadWorkflowFiles(files);
        const paths = (payload == null ? void 0 : payload.paths) || [];
        this.setStatus("running", "File uploaded, processing...");
        return paths.length === 1 ? paths[0] : paths;
      } catch (error) {
        if (error instanceof WorkflowApiError) {
          __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.setFieldStatus(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState(), fieldName, "error");
          this.setStatus("error", `Upload failed: ${((_a = error.payload) == null ? void 0 : _a.detail) || error.message}`);
        }
        throw error;
      }
    });
    _LfWorkflowRunnerManager_loadWorkflows.set(this, async () => {
      const workflows = await fetchWorkflowDefinitions();
      if (!workflows.length) {
        throw new Error("No workflows available from the API.");
      }
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").setState((state) => ({
        ...state,
        workflows
      }));
      await this.setWorkflow(workflows[0].id);
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
      workflow: createWorkflowSection()
    }, "f");
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").setState((state) => ({
      ...state,
      manager: this
    }));
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeFramework).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeLayout).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_subscribeToState).call(this);
    this.setStatus("running", "Loading workflows...");
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_loadWorkflows, "f").call(this).catch((error) => {
      console.error("Failed to load workflows:", error);
      const message = error instanceof Error ? error.message : "Failed to load workflows.";
      this.setStatus("error", message);
    });
  }
  async runWorkflow() {
    var _a, _b, _c;
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
    } catch (error) {
      console.error("Failed to collect inputs:", error);
      const detail = error instanceof WorkflowApiError ? ((_a = error.payload) == null ? void 0 : _a.detail) || error.message : (error == null ? void 0 : error.message) || "Failed to collect inputs.";
      this.setStatus("error", `Failed to collect inputs: ${detail}`);
      return;
    }
    try {
      const response = await runWorkflowRequest(workflowId, inputs);
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").setState((state2) => {
        var _a2;
        return {
          ...state2,
          current: {
            ...state2.current,
            status: response.status,
            message: response.message,
            preferredOutput: response.payload.preferred_output ?? null
          },
          results: ((_a2 = response.payload.history) == null ? void 0 : _a2.outputs) ? { ...response.payload.history.outputs } : null
        };
      });
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").setState((state2) => ({
          ...state2,
          current: {
            ...state2.current,
            status: "error",
            message: error.message
          }
        }));
        const inputName = (_c = (_b = error.payload) == null ? void 0 : _b.error) == null ? void 0 : _c.input;
        if (inputName) {
          __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.setFieldStatus(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState(), inputName, "error");
        }
      } else {
        console.error("Unexpected error while running workflow:", error);
        this.setStatus("error", "Unexpected error while running the workflow.");
      }
    }
  }
  setStatus(status, message) {
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").setState((state) => ({
      ...state,
      current: {
        ...state.current,
        status,
        message: message ?? DEFAULT_STATUS_MESSAGES[status]
      }
    }));
  }
  async setWorkflow(id) {
    const state = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").getState();
    if (state.current.workflow === id) {
      return;
    }
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").setState((state2) => ({
      ...state2,
      current: {
        ...state2.current,
        workflow: id,
        preferredOutput: null
      },
      results: null
    }));
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
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.render(state);
}, _LfWorkflowRunnerManager_subscribeToState = function _LfWorkflowRunnerManager_subscribeToState2() {
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_store, "f").subscribe((state) => {
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_sections, "f").workflow.render(state);
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
