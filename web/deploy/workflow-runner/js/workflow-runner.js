import { g as getLfFramework } from "../../js/lf-widgets-6WpDY9VV.js";
import { A as APIEndpoints } from "../../js/api-CvAQcIfO.js";
const _returnErrorResponse$1 = (message, payload) => ({
  message,
  payload,
  status: "error"
});
const _returnSuccessResponse$1 = (message, payload) => ({
  message,
  payload,
  status: "ready"
});
const invokeRunAPI = async (id, inputs) => {
  try {
    const response = await fetch(`/api/lf-nodes/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workflowId: id, inputs })
    });
    const responseBody = await response.json();
    const payload = responseBody.payload;
    if (!response.ok) {
      const { detail, error } = payload;
      const message = `Workflow execution failed: ${detail} (${(error == null ? void 0 : error.message) || error})`;
      console.error(message, payload);
      return _returnErrorResponse$1(message, payload);
    }
    return _returnSuccessResponse$1("Workflow executed successfully.", payload);
  } catch (error) {
    console.error("Error invoking run API:", error);
    const payload = {
      detail: String(error.message || error),
      history: {}
    };
    return _returnErrorResponse$1("Error invoking run API.", payload);
  }
};
const ROOT_CLASS$3 = "drawer-section";
const _createSection$3 = (state) => {
  const { ui } = state;
  const section = document.createElement("lf-drawer");
  section.className = ROOT_CLASS$3;
  section.lfDisplay = "slide";
  ui.layout.drawer._root = section;
  ui.layout._root.appendChild(section);
};
const drawerSection = {
  create: _createSection$3
};
const _returnErrorResponse = (message, payload) => ({
  message,
  payload,
  status: "error"
});
const _returnSuccessResponse = (message, payload) => ({
  message,
  payload,
  status: "ready"
});
const invokeUploadAPI = async (files) => {
  try {
    const formData = new FormData();
    if (!files || files.length === 0) {
      const payload2 = { detail: "missing_file" };
      return _returnErrorResponse("Missing file to upload.", payload2);
    }
    files.forEach((file) => formData.append("file", file));
    const response = await fetch(`/api/lf-nodes/upload`, {
      method: "POST",
      body: formData
    });
    const responseBody = await response.json();
    let payload;
    if (isWorkflowAPIUploadResponse(responseBody)) {
      payload = responseBody.payload;
    } else if (isWorkflowAPIUploadPayload(responseBody)) {
      payload = responseBody;
    } else {
      const errPayload = { detail: "invalid_response_shape" };
      return _returnErrorResponse("Invalid response shape from upload API.", errPayload);
    }
    if (!response.ok) {
      const { detail, error } = payload || { detail: "unknown", error: void 0 };
      const message = `Upload failed: ${detail} (${(error == null ? void 0 : error.message) || error})`;
      console.error(message, payload);
      return _returnErrorResponse(message, payload || { detail: String(response.status) });
    }
    return _returnSuccessResponse("Upload completed successfully.", payload);
  } catch (error) {
    console.error("Error invoking run API:", error);
    const payload = {
      detail: String(error.message || error)
    };
    return _returnErrorResponse("Error invoking run API.", payload);
  }
};
const WORKFLOW_TEXT = "Select a workflow";
const ROOT_CLASS$2 = "workflow-section";
const _getCurrentWorkflow = (state) => {
  const { current, workflows } = state;
  return workflows.find((wf) => wf.id === current.workflow) || null;
};
const _getWorkflowLabel = (state) => {
  const workflow = _getCurrentWorkflow(state);
  return (workflow == null ? void 0 : workflow.label) || WORKFLOW_TEXT;
};
const _fieldWrapper = () => {
  const fieldWrapper = document.createElement("div");
  fieldWrapper.className = `${ROOT_CLASS$2}__field`;
  return fieldWrapper;
};
const _optionsWrapper = () => {
  const optionsWrapper = document.createElement("div");
  optionsWrapper.className = `${ROOT_CLASS$2}__options`;
  return optionsWrapper;
};
const _resultWrapper = () => {
  const resultWrapper = document.createElement("div");
  resultWrapper.className = `${ROOT_CLASS$2}__result`;
  return resultWrapper;
};
const _runButton = (state) => {
  const { runWorkflow } = state.manager;
  const props = {
    lfAriaLabel: "Run workflow",
    lfLabel: "Run workflow",
    lfStretchX: true
  };
  const run = createComponent.button(props);
  run.className = `${ROOT_CLASS$2}__run`;
  run.onclick = () => runWorkflow();
  return run;
};
const _statusWrapper = (tone = "info") => {
  const statusWrapper = document.createElement("div");
  statusWrapper.className = `${ROOT_CLASS$2}__status`;
  statusWrapper.dataset.tone = tone;
  return statusWrapper;
};
const _title = (state) => {
  const h3 = document.createElement("h3");
  h3.className = `${ROOT_CLASS$2}__title`;
  h3.textContent = _getWorkflowLabel(state);
  return h3;
};
const _createSection$2 = (state) => {
  const { ui } = state;
  const section = document.createElement("section");
  section.className = ROOT_CLASS$2;
  const optionsWrapper = _optionsWrapper();
  const runButton = _runButton(state);
  const resultWrapper = _resultWrapper();
  const statusWrapper = _statusWrapper();
  const title = _title(state);
  ui.layout.main.workflow._root = section;
  ui.layout.main.workflow.options = optionsWrapper;
  ui.layout.main.workflow.result = resultWrapper;
  ui.layout.main.workflow.run = runButton;
  ui.layout.main.workflow.status = statusWrapper;
  ui.layout.main.workflow.title = title;
  section.appendChild(title);
  section.appendChild(optionsWrapper);
  section.appendChild(runButton);
  section.appendChild(statusWrapper);
  section.appendChild(resultWrapper);
  ui.layout.main._root.appendChild(section);
};
const _updateSection = {
  fieldWrapper: (state, name, status = "") => {
    const { ui } = state;
    const field = ui.layout.main.workflow.fields.find((el) => el.dataset.name === name);
    const wrapper = field.parentElement;
    if (field && wrapper) {
      wrapper.dataset.status = status;
    }
  },
  options: (state) => {
    const { current, ui } = state;
    const element = ui.layout.main.workflow.options;
    if (!element) {
      return;
    }
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }
    if (!current.workflow) {
      return;
    }
    ui.layout.main.workflow.fields = [];
    const workflow = _getCurrentWorkflow(state);
    for (const field of workflow.fields ?? []) {
      const wrapper = _fieldWrapper();
      const fieldElement = createInputField(field);
      fieldElement.dataset.name = field.name;
      ui.layout.main.workflow.fields.push(fieldElement);
      wrapper.appendChild(fieldElement);
      element.appendChild(wrapper);
    }
  },
  result: (state, outputs) => {
    const { ui } = state;
    const element = ui.layout.main.workflow.result;
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }
    for (const nodeId in outputs) {
      const nodeContent = outputs[nodeId];
      const { _description } = nodeContent;
      const title = document.createElement("h4");
      title.className = `${ROOT_CLASS$2}__result-title`;
      title.textContent = normalize_description(_description) || `Node #${nodeId}`;
      element.appendChild(title);
      const grid = document.createElement("div");
      grid.className = `${ROOT_CLASS$2}__result-grid`;
      element.appendChild(grid);
      for (const resultKey in nodeContent) {
        const rK = resultKey;
        switch (rK) {
          case "_description":
            break;
          default:
            const resultElement = createOutputField(resultKey, nodeContent[resultKey]);
            resultElement.className = `${ROOT_CLASS$2}__result-item`;
            if (resultElement) {
              grid.appendChild(resultElement);
            }
            break;
        }
      }
    }
  },
  run: (state) => {
    const { current, ui } = state;
    const element = ui.layout.main.workflow.run;
    element.lfShowSpinner = current.status === "running";
  },
  status: (state, message) => {
    const { current, ui } = state;
    const element = ui.layout.main.workflow.status;
    switch (current.status) {
      case "ready":
        element.textContent = message || "Ready.";
        break;
      case "running":
        element.textContent = message || "Running...";
        break;
      case "error":
        element.textContent = message || "An error occurred while running the workflow.";
        break;
    }
    element.dataset.tone = current.status;
  },
  title: (state) => {
    const { ui } = state;
    const element = ui.layout.main.workflow.title;
    element.textContent = _getWorkflowLabel(state);
  }
};
const workflowSection = {
  create: _createSection$2,
  update: _updateSection
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
const handleUploadField = async (state, fieldName, files) => {
  var _a, _b, _c;
  const { manager } = state;
  manager.setStatus("running", "Uploading file…");
  const response = await invokeUploadAPI(files);
  if (!response || response.status !== "ready") {
    workflowSection.update.fieldWrapper(state, fieldName, "error");
    manager.setStatus("error", `Upload failed: ${((_a = response == null ? void 0 : response.payload) == null ? void 0 : _a.detail) ?? "unknown error"}`);
    throw new Error(((_b = response == null ? void 0 : response.payload) == null ? void 0 : _b.detail) || "Upload failed");
  }
  const paths = ((_c = response.payload) == null ? void 0 : _c.paths) || [];
  manager.setStatus("running", "File uploaded, processing...");
  return paths;
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
const ROOT_CLASS$1 = "header-section";
const _container = () => {
  const container = document.createElement("div");
  container.className = `${ROOT_CLASS$1}__container`;
  container.slot = "content";
  return container;
};
const _drawerToggle = () => {
  const { theme } = getLfFramework();
  const { get } = theme;
  const lfIcon = get.icon("menu2");
  const props = {
    lfAriaLabel: "Toggle drawer",
    lfIcon,
    lfStyling: "icon"
  };
  const drawerToggle = createComponent.button(props);
  drawerToggle.className = `${ROOT_CLASS$1}__drawer-toggle`;
  return drawerToggle;
};
const _createSection$1 = (state) => {
  const { ui } = state;
  const section = document.createElement("lf-header");
  section.className = ROOT_CLASS$1;
  const container = _container();
  const drawerToggle = _drawerToggle();
  ui.layout.header.drawerToggle = drawerToggle;
  section.appendChild(container);
  container.appendChild(drawerToggle);
  ui.layout.header._root = section;
  ui.layout._root.appendChild(section);
};
const headerSection = {
  create: _createSection$1
};
const ROOT_CLASS = "main-section";
const _createSection = (state) => {
  const { ui } = state;
  const section = document.createElement("main");
  section.className = ROOT_CLASS;
  ui.layout.main._root = section;
  ui.layout._root.appendChild(section);
};
const mainSection = {
  create: _createSection
};
const initState = (appContainer, manager) => ({
  current: { status: "ready", workflow: null },
  manager,
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
  workflows: []
});
var __classPrivateFieldGet = function(receiver, state, kind, f) {
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var _LfWorkflowRunnerManager_instances, _LfWorkflowRunnerManager_API_BASE, _LfWorkflowRunnerManager_ASSETS_BASE, _LfWorkflowRunnerManager_ASSETS_URL, _LfWorkflowRunnerManager_MANAGERS, _LfWorkflowRunnerManager_STATE, _LfWorkflowRunnerManager_buildLayout, _LfWorkflowRunnerManager_initializeElements, _LfWorkflowRunnerManager_loadWorkflows;
class LfWorkflowRunnerManager {
  //#endregion
  //#region Constructor
  constructor() {
    _LfWorkflowRunnerManager_instances.add(this);
    _LfWorkflowRunnerManager_API_BASE.set(this, "/api");
    _LfWorkflowRunnerManager_ASSETS_BASE.set(this, __classPrivateFieldGet(this, _LfWorkflowRunnerManager_API_BASE, "f") + "/lf-nodes/static/assets/");
    _LfWorkflowRunnerManager_ASSETS_URL.set(this, window.location.origin + __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ASSETS_BASE, "f"));
    _LfWorkflowRunnerManager_MANAGERS.set(this, {
      lfFramework: null
    });
    _LfWorkflowRunnerManager_STATE.set(this, initState(document.querySelector("#app"), this));
    _LfWorkflowRunnerManager_loadWorkflows.set(this, async () => {
      const response = await fetch(`${__classPrivateFieldGet(this, _LfWorkflowRunnerManager_API_BASE, "f")}${APIEndpoints.Workflows}`);
      if (!response.ok) {
        throw new Error(`Failed to load workflows (${response.status})`);
      }
      const data = await response.json();
      __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f").workflows = Array.isArray(data.workflows) ? data.workflows : [];
      const firstWorkflow = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f").workflows[0];
      if (!firstWorkflow) {
        throw new Error("No workflows available from the API.");
      }
      this.setWorkflow(firstWorkflow.id);
    });
    this.collectInputs = async () => {
      const { fields } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f").ui.layout.main.workflow;
      const inputs = {};
      for (const el of fields) {
        const value = await el.getValue();
        workflowSection.update.fieldWrapper(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"), el.dataset.name);
        switch (el.tagName.toLowerCase()) {
          case "lf-toggle":
            inputs[el.dataset.name] = value === "off" ? false : true;
            break;
          case "lf-upload":
            try {
              const files = value;
              const paths = await handleUploadField(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"), el.dataset.name, files);
              inputs[el.dataset.name] = paths.length === 1 ? paths[0] : paths;
            } catch (err) {
              throw err;
            }
            break;
          default:
          case "lf-textfield":
            inputs[el.dataset.name] = value;
            break;
        }
      }
      return inputs;
    };
    this.runWorkflow = async () => {
      var _a;
      const { current } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f");
      if (!current.workflow) {
        this.setStatus("error", "No workflow selected.");
        return;
      }
      this.setStatus("running", "Submitting workflow…");
      let inputs;
      try {
        inputs = await this.collectInputs();
      } catch (err) {
        console.error("Failed to collect inputs:", err);
        const short = err && err.message ? err.message : "Failed to collect inputs";
        const userMessage = `Failed to collect inputs: ${short}`;
        this.setStatus("error", userMessage);
        return;
      }
      const { message, payload, status } = await invokeRunAPI(current.workflow, inputs);
      if ((_a = payload.error) == null ? void 0 : _a.input) {
        workflowSection.update.fieldWrapper(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"), payload.error.input, "error");
      }
      this.setStatus(status, message);
      if (status === "ready") {
        this.setResult(payload);
        __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f").ui.layout.main.workflow.result.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }
    };
    this.setResult = (payload) => {
      const outputs = payload.history && payload.history.outputs ? payload.history.outputs : {};
      workflowSection.update.result(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"), outputs);
    };
    this.setStatus = (status, message) => {
      const { current } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f");
      current.status = status;
      workflowSection.update.run(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"));
      workflowSection.update.status(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"), message);
    };
    this.setWorkflow = async (id) => {
      const { current } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f");
      if (current.workflow === id) {
        return;
      }
      current.workflow = id;
      workflowSection.update.title(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"));
      workflowSection.update.options(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"));
    };
    const assetsUrl = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_ASSETS_URL, "f");
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_MANAGERS, "f").lfFramework = getLfFramework();
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_MANAGERS, "f").lfFramework.assets.set(assetsUrl);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_MANAGERS, "f").lfFramework.theme.set("dark");
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_initializeElements).call(this);
    __classPrivateFieldGet(this, _LfWorkflowRunnerManager_loadWorkflows, "f").call(this).then(() => this.setStatus("ready")).catch((err) => {
      console.error(err);
      this.setStatus("error");
    });
  }
}
_LfWorkflowRunnerManager_API_BASE = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_ASSETS_BASE = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_ASSETS_URL = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_MANAGERS = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_STATE = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_loadWorkflows = /* @__PURE__ */ new WeakMap(), _LfWorkflowRunnerManager_instances = /* @__PURE__ */ new WeakSet(), _LfWorkflowRunnerManager_buildLayout = function _LfWorkflowRunnerManager_buildLayout2() {
  const { ui } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f");
  ui.layout._root.appendChild(ui.layout.drawer._root);
  ui.layout._root.appendChild(ui.layout.main._root);
}, _LfWorkflowRunnerManager_initializeElements = function _LfWorkflowRunnerManager_initializeElements2() {
  const { ui } = __classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f");
  while (ui.layout._root.firstChild) {
    ui.layout._root.removeChild(ui.layout._root.firstChild);
  }
  drawerSection.create(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"));
  headerSection.create(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"));
  mainSection.create(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"));
  workflowSection.create(__classPrivateFieldGet(this, _LfWorkflowRunnerManager_STATE, "f"));
  __classPrivateFieldGet(this, _LfWorkflowRunnerManager_instances, "m", _LfWorkflowRunnerManager_buildLayout).call(this);
};
const hasComfyApp = (comfyAPI == null ? void 0 : comfyAPI.api) && (comfyAPI == null ? void 0 : comfyAPI.app);
if (!hasComfyApp) {
  new LfWorkflowRunnerManager();
}
//# sourceMappingURL=workflow-runner.js.map
