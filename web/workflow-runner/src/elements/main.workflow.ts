import { LfThemeUIState } from '@lf-widgets/core/dist/types/components';
import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import {
  WorkflowAPIField,
  WorkflowAPIResult,
  WorkflowAPIResultKey,
  WorkflowAPIUI,
} from '../types/api';
import { WorkflowState, WorkflowStatus } from '../types/state';
import { DEFAULT_STATUS_MESSAGES } from '../config';
import { clearChildren, normalize_description } from '../utils/common';
import { createComponent, createInputField, createOutputField } from './components';
import { WorkflowSectionController } from './section';

//#region Constants & helpers
const WORKFLOW_TEXT = 'Select a workflow';
const ROOT_CLASS = 'workflow-section';
type FieldStatus = 'error' | '';

const getCurrentWorkflow = (state: WorkflowState) => {
  const { current, workflows } = state;
  return workflows.find((wf) => wf.id === current.workflow) || null;
};

const getWorkflowLabel = (state: WorkflowState) => {
  const workflow = getCurrentWorkflow(state);
  return workflow?.label || WORKFLOW_TEXT;
};

const createFieldWrapper = () => {
  const fieldWrapper = document.createElement('div');
  fieldWrapper.className = `${ROOT_CLASS}__field`;
  return fieldWrapper;
};

const createOptionsWrapper = () => {
  const optionsWrapper = document.createElement('div');
  optionsWrapper.className = `${ROOT_CLASS}__options`;
  return optionsWrapper;
};

const createResultWrapper = () => {
  const resultWrapper = document.createElement('div');
  resultWrapper.className = `${ROOT_CLASS}__result`;
  return resultWrapper;
};

const createRunButton = (state: WorkflowState) => {
  const props = {
    lfAriaLabel: 'Run workflow',
    lfLabel: 'Run workflow',
    lfStretchX: true,
  } as Partial<LfButtonInterface>;

  const button = createComponent.button(props);
  button.className = `${ROOT_CLASS}__run`;
  button.onclick = () => state.manager?.runWorkflow();
  return button;
};

const createStatusWrapper = (tone: LfThemeUIState = 'info') => {
  const statusWrapper = document.createElement('div');
  statusWrapper.className = `${ROOT_CLASS}__status`;
  statusWrapper.dataset.tone = tone;
  return statusWrapper;
};

const createTitle = (state: WorkflowState) => {
  const h3 = document.createElement('h3');
  h3.className = `${ROOT_CLASS}__title`;
  h3.textContent = getWorkflowLabel(state);
  return h3;
};
//#endregion

export interface WorkflowSectionHandle extends WorkflowSectionController {
  setFieldStatus: (state: WorkflowState, name: string, status?: FieldStatus) => void;
}

//#region Factory
export const createWorkflowSection = (): WorkflowSectionHandle => {
  let section: HTMLElement | null = null;
  let optionsWrapper: HTMLDivElement | null = null;
  let resultWrapper: HTMLElement | null = null;
  let runButton: HTMLLfButtonElement | null = null;
  let statusWrapper: HTMLElement | null = null;
  let titleElement: HTMLElement | null = null;
  let lastWorkflowId: string | null = null;
  let lastStatus: WorkflowStatus | null = null;
  let lastMessage: string | null = null;
  let lastResultsRef: WorkflowAPIUI | null = null;
  let mountedState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    mountedState = state;
    const { ui } = state;

    section = document.createElement('section');
    section.className = ROOT_CLASS;

    titleElement = createTitle(state);
    optionsWrapper = createOptionsWrapper();
    runButton = createRunButton(state);
    statusWrapper = createStatusWrapper('info');
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

    ui.layout.main._root?.appendChild(section);
  };

  const updateOptions = (state: WorkflowState) => {
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
      const fieldElement = createInputField(field as WorkflowAPIField);
      fieldElement.dataset.name = field.name;

      ui.layout.main.workflow.fields.push(fieldElement);
      wrapper.appendChild(fieldElement);
      element.appendChild(wrapper);
    }
  };

  const updateResult = (state: WorkflowState) => {
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
        const key = resultKey as WorkflowAPIResultKey;
        if (key === '_description') {
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
      behavior: 'smooth',
      block: 'start',
    });
  };

  const updateRunButton = (state: WorkflowState) => {
    const button = state.ui.layout.main.workflow.run;
    if (!button) {
      return;
    }
    button.lfShowSpinner = state.current.status === 'running';
  };

  const updateStatus = (state: WorkflowState) => {
    const element = state.ui.layout.main.workflow.status;
    if (!element) {
      return;
    }

    const message = state.current.message ?? DEFAULT_STATUS_MESSAGES[state.current.status];
    element.textContent = message;
    element.dataset.tone = state.current.status;
  };

  const updateTitle = (state: WorkflowState) => {
    const element = state.ui.layout.main.workflow.title;
    if (!element) {
      return;
    }

    element.textContent = getWorkflowLabel(state);
  };

  const render = (state: WorkflowState) => {
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

  const setFieldStatus = (state: WorkflowState, name: string, status: FieldStatus = '') => {
    const { ui } = state;
    const field = ui.layout.main.workflow.fields.find((el) => el.dataset.name === name);
    const wrapper = field?.parentElement;
    if (wrapper) {
      wrapper.dataset.status = status;
    }
  };

  const destroy = () => {
    section?.remove();
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
    setFieldStatus,
  };
};
//#endregion
