import { LfThemeUIState } from '@lf-widgets/core/dist/types/components';
import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowAPIField, WorkflowState } from '../../types/workflow-runner/state';
import { createComponent } from './components';

//#region Constants
const WORKFLOW_TEXT = 'Select a workflow';
const ROOT_CLASS = 'workflow-section';
//#endregion

//#region Helpers
const _getCurrentWorkflow = (state: WorkflowState) => {
  const { current, workflows } = state;
  return workflows.find((wf) => wf.id === current.workflow) || null;
};
const _getWorkflowLabel = (state: WorkflowState) => {
  const workflow = _getCurrentWorkflow(state);
  return workflow?.label || WORKFLOW_TEXT;
};
//#endregion

//#region Elements
const _field = (field: WorkflowAPIField) => {
  const {
    component,
    default: lfValue,
    description,
    extra: lfHtmlAttributes,
    label: lfLabel,
  } = field;
  const { sanitizeProps } = getLfFramework();
  const safeHtmlAttributes = sanitizeProps(lfHtmlAttributes);

  switch (component) {
    case 'lf-toggle': {
      return createComponent.toggle({
        lfAriaLabel: lfLabel,
        lfLabel,
        lfValue: Boolean(lfValue ?? false),
      });
    }
    case 'lf-upload': {
      return createComponent.upload({
        lfLabel,
      });
    }
    default:
    case 'lf-textfield': {
      return createComponent.textfield({
        lfHelper: { value: description ?? '', showWhenFocused: false },
        lfHtmlAttributes: safeHtmlAttributes,
        lfLabel,
        lfValue: String(lfValue ?? ''),
      });
    }
  }
};
const _fieldWrapper = () => {
  const fieldWrapper = document.createElement('div');
  fieldWrapper.className = `${ROOT_CLASS}__field`;
  return fieldWrapper;
};
const _optionsWrapper = () => {
  const optionsWrapper = document.createElement('div');
  optionsWrapper.className = `${ROOT_CLASS}__options`;
  return optionsWrapper;
};
const _result = (output: { lf_images?: any; lf_masonry?: any }) => {
  console.log(output);
};
const _resultWrapper = () => {
  const resultWrapper = document.createElement('div');
  resultWrapper.className = `${ROOT_CLASS}__result`;
  return resultWrapper;
};
const _runButton = (state: WorkflowState) => {
  const { runWorkflow } = state.manager;

  const props = {
    lfAriaLabel: 'Run workflow',
    lfLabel: 'Run workflow',
    lfStretchX: true,
  } as Partial<LfButtonInterface>;
  const run = createComponent.button(props);
  run.className = `${ROOT_CLASS}__run`;
  run.onclick = () => runWorkflow();
  return run;
};
const _statusWrapper = (tone: LfThemeUIState = 'info') => {
  const statusWrapper = document.createElement('div');
  statusWrapper.className = `${ROOT_CLASS}__status`;
  statusWrapper.dataset.tone = tone;
  return statusWrapper;
};
const _title = (state: WorkflowState) => {
  const h3 = document.createElement('h3');
  h3.className = `${ROOT_CLASS}__title`;
  h3.textContent = _getWorkflowLabel(state);
  return h3;
};
//#endregion

//#region Section
const _createSection = (state: WorkflowState) => {
  const { ui } = state;

  const section = document.createElement('section');
  section.className = ROOT_CLASS;

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
  fieldWrapper: (state: WorkflowState, name: string, status: 'error' | '' = '') => {
    const { ui } = state;

    const field = ui.layout.main.workflow.fields.find((el) => el.dataset.name === name);
    const wrapper = field.parentElement;

    if (field && wrapper) {
      wrapper.dataset.status = status;
    }
  },
  options: (state: WorkflowState) => {
    const { current, ui } = state;

    const element = ui.layout.main.workflow.options;
    if (!element) {
      return;
    }

    element.childNodes.forEach((n) => n.remove());
    if (!current.workflow) {
      return;
    }

    ui.layout.main.workflow.fields = [];
    const workflow = _getCurrentWorkflow(state);
    for (const field of workflow.fields ?? []) {
      const wrapper = _fieldWrapper();
      const fieldElement = _field(field);
      fieldElement.dataset.name = field.name;

      ui.layout.main.workflow.fields.push(fieldElement);

      wrapper.appendChild(fieldElement);
      element.appendChild(wrapper);
    }
  },
  result: (state: WorkflowState, outputs: Record<string, unknown>) => {
    const { ui } = state;

    const element = ui.layout.main.workflow.result;
    element.childNodes.forEach((n) => n.remove());

    for (const key in outputs) {
      _result(outputs[key]);
      //const resultElement = _result(outputs[key]);
      // element.appendChild(resultElement);
    }
  },
  run: (state: WorkflowState) => {
    const { current, ui } = state;

    const element = ui.layout.main.workflow.run;
    element.lfShowSpinner = current.status === 'running';
  },
  status: (state: WorkflowState, message?: string) => {
    const { current, ui } = state;

    const element = ui.layout.main.workflow.status;
    switch (current.status) {
      case 'ready':
        element.textContent = message || 'Ready.';
        break;
      case 'running':
        element.textContent = message || 'Running...';
        break;
      case 'error':
        element.textContent = message || 'An error occurred while running the workflow.';
        break;
    }

    element.dataset.tone = current.status;
  },
  title: (state: WorkflowState) => {
    const { ui } = state;

    const element = ui.layout.main.workflow.title;
    element.textContent = _getWorkflowLabel(state);
  },
};
//#endregion

//#region Public API
export const workflowSection = {
  create: _createSection,
  update: _updateSection,
};
//#endregion
