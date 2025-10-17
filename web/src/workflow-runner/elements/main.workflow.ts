import { LfThemeUIState } from '@lf-widgets/core/dist/types/components';
import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import {
  WorkflowAPIResult,
  WorkflowAPIResultKey,
  WorkflowAPIUI,
} from '../../types/workflow-runner/api';
import { WorkflowState } from '../../types/workflow-runner/state';
import { normalize_description } from '../utils/common';
import { createComponent, createInputField, createOutputField } from './components';

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
  result: (state: WorkflowState, outputs: WorkflowAPIUI) => {
    const { ui } = state;

    const element = ui.layout.main.workflow.result;
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }

    for (const nodeId in outputs) {
      const nodeContent = outputs[nodeId] as WorkflowAPIResult;
      const { _description } = nodeContent;

      const title = document.createElement('h4');
      title.className = `${ROOT_CLASS}__result-title`;
      title.textContent = normalize_description(_description) || `Node #${nodeId}`;
      element.appendChild(title);

      const grid = document.createElement('div');
      grid.className = `${ROOT_CLASS}__result-grid`;
      element.appendChild(grid);

      for (const resultKey in nodeContent) {
        const rK = resultKey as WorkflowAPIResultKey;
        switch (rK) {
          case '_description':
            break;
          default:
            const resultElement = createOutputField(resultKey, nodeContent[resultKey]);
            resultElement.className = `${ROOT_CLASS}__result-item`;
            if (resultElement) {
              grid.appendChild(resultElement);
            }
            break;
        }
      }
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
