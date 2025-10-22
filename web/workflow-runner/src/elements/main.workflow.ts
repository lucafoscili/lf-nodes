import { LfThemeUIState } from '@lf-widgets/core/dist/types/components';
import { LfButtonInterface } from '@lf-widgets/foundations/dist';
import { DEFAULT_STATUS_MESSAGES } from '../config';
import { executeWorkflowButton } from '../handlers/workflow';
import {
  WorkflowAPIItem,
  WorkflowCellOutputItem,
  WorkflowCellsInputContainer,
  WorkflowCellsOutputContainer,
  WorkflowNodeResults,
} from '../types/api';
import { WorkflowCellStatus, WorkflowSectionHandle, WorkflowUICells } from '../types/section';
import { WorkflowState, WorkflowStatus } from '../types/state';
import { clearChildren } from '../utils/common';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { createComponent, createInputCell, createOutputComponent } from './components';

//#region Constants
const ROOT_CLASS = 'workflow-section';
const WORKFLOW_TEXT = 'Select a workflow';
//#endregion

//#region Helpers
const _createDescription = (state: WorkflowState) => {
  const p = document.createElement('p');
  p.className = `${ROOT_CLASS}__description`;
  p.textContent = _getWorkflowDescription(state);
  return p;
};
const _createFieldWrapper = () => {
  const fieldWrapper = document.createElement('div');
  fieldWrapper.className = `${ROOT_CLASS}__field`;
  return fieldWrapper;
};
const _createOptionsWrapper = () => {
  const optionsWrapper = document.createElement('div');
  optionsWrapper.className = `${ROOT_CLASS}__options`;
  return optionsWrapper;
};
const _createResultWrapper = () => {
  const resultWrapper = document.createElement('div');
  resultWrapper.className = `${ROOT_CLASS}__result`;
  return resultWrapper;
};
const _createRunButton = (state: WorkflowState) => {
  const props = {
    lfAriaLabel: 'Run workflow',
    lfLabel: 'Run workflow',
    lfStretchX: true,
  } as Partial<LfButtonInterface>;

  const button = createComponent.button(props);
  button.className = `${ROOT_CLASS}__run`;
  button.addEventListener('lf-button-event', (e) => executeWorkflowButton(e, state));

  return button;
};
const _createStatusWrapper = (tone: LfThemeUIState = 'info') => {
  const statusWrapper = document.createElement('div');
  statusWrapper.className = `${ROOT_CLASS}__status`;
  statusWrapper.dataset.tone = tone;
  return statusWrapper;
};
const _createTitle = (state: WorkflowState) => {
  const h3 = document.createElement('h3');
  h3.className = `${ROOT_CLASS}__title`;
  h3.textContent = _getWorkflowTitle(state);
  return h3;
};
const _deepMerge = (defs: WorkflowCellsOutputContainer, outs: WorkflowNodeResults) => {
  const prep: WorkflowCellOutputItem[] = [];

  for (const id in defs) {
    const cell = defs[id];
    const { nodeId } = cell;
    const result = outs?.[nodeId]?.lf_output[0] || outs?.[nodeId]?.[0] || outs?.[nodeId];

    const item: WorkflowCellOutputItem = {
      ...JSON.parse(JSON.stringify(cell)),
      ...JSON.parse(JSON.stringify(result || {})),
    };
    prep.push(item);
  }

  return prep;
};
const _getCurrentWorkflow = (state: WorkflowState) => {
  const { current, workflows } = state;
  return workflows?.nodes?.find((node) => node.id === current.id) || null;
};
const _getWorkflowInputCells = (workflow: WorkflowAPIItem) => {
  const inputsSection = workflow.children?.find((child) => child.id.endsWith(':inputs'));
  return (inputsSection?.cells || {}) as WorkflowCellsInputContainer;
};
const _getWorkflowOutputCells = (workflow: WorkflowAPIItem) => {
  const outputsSection = workflow.children?.find((child) => child.id.endsWith(':outputs'));
  return (outputsSection?.cells || {}) as WorkflowCellsOutputContainer;
};
const _getWorkflowDescription = (state: WorkflowState) => {
  const workflow = _getCurrentWorkflow(state);
  return workflow?.description || '';
};
const _getWorkflowTitle = (state: WorkflowState) => {
  const workflow = _getCurrentWorkflow(state);
  const str = typeof workflow?.value === 'string' ? workflow.value : String(workflow?.value || '');
  return str || WORKFLOW_TEXT;
};
//#endregion

//#region Factory
export const createWorkflowSection = (): WorkflowSectionHandle => {
  const {
    STATUS_UPDATED,
    WORKFLOW_INPUT_FLAGGED,
    WORKFLOW_INPUTS_CLEARED,
    WORKFLOW_INPUTS_RENDERED,
    WORKFLOW_LAYOUT_DESTROYED,
    WORKFLOW_LAYOUT_MOUNTED,
    WORKFLOW_RESULTS_CLEARED,
    WORKFLOW_RESULTS_RENDERED,
  } = DEBUG_MESSAGES;

  let descriptionElement: HTMLElement | null = null;
  let id: string | null = null;
  let lastMessage: string | null = null;
  let lastResultsRef: WorkflowNodeResults | null = null;
  let lastStatus: WorkflowStatus | null = null;
  let mountedState: WorkflowState | null = null;
  let optionsWrapper: HTMLDivElement | null = null;
  let resultWrapper: HTMLElement | null = null;
  let runButton: HTMLLfButtonElement | null = null;
  let section: HTMLElement | null = null;
  let statusWrapper: HTMLElement | null = null;
  let titleElement: HTMLElement | null = null;

  const mount = (state: WorkflowState) => {
    mountedState = state;
    const { ui } = state;

    section = document.createElement('section');
    section.className = ROOT_CLASS;

    titleElement = _createTitle(state);
    descriptionElement = _createDescription(state);
    optionsWrapper = _createOptionsWrapper();
    runButton = _createRunButton(state);
    statusWrapper = _createStatusWrapper('info');
    resultWrapper = _createResultWrapper();

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

    ui.layout.main._root?.appendChild(section);

    debugLog(WORKFLOW_LAYOUT_MOUNTED, 'informational', {
      workflowId: state.current.id ?? null,
    });
  };

  const updateDescription = (state: WorkflowState) => {
    const { ui } = state;
    const element = ui.layout.main.workflow.description;
    if (!element) {
      return;
    }

    element.textContent = _getWorkflowDescription(state);
  };

  const updateOptions = (state: WorkflowState) => {
    const { ui } = state;
    const element = ui.layout.main.workflow.options;
    if (!element) {
      return;
    }

    clearChildren(element);

    const workflow = _getCurrentWorkflow(state);
    const cellElements: WorkflowUICells = [];

    if (workflow) {
      const inputCells = _getWorkflowInputCells(workflow);
      for (const id in inputCells) {
        if (!Object.prototype.hasOwnProperty.call(inputCells, id)) {
          continue;
        }
        const cell = inputCells[id];
        const wrapper = _createFieldWrapper();
        const component = createInputCell(cell);
        component.id = id;

        cellElements.push(component);
        wrapper.appendChild(component);
        element.appendChild(wrapper);
      }
    }

    state.mutate.ui((uiState) => {
      uiState.layout.main.workflow.cells = cellElements;
    });

    if (workflow && cellElements.length) {
      debugLog(WORKFLOW_INPUTS_RENDERED, 'informational', {
        workflowId: state.current.id,
        cellCount: cellElements.length,
      });
    } else {
      debugLog(WORKFLOW_INPUTS_CLEARED, 'informational', {
        workflowId: state.current.id,
      });
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

    const nodeIds = Object.keys(outputs);
    if (nodeIds.length === 0) {
      debugLog(WORKFLOW_RESULTS_CLEARED, 'informational', {
        workflowId: state.current.id,
      });
      return;
    }

    const workflow = _getCurrentWorkflow(state);
    const outputsDefs = workflow ? _getWorkflowOutputCells(workflow) : {};
    debugLog(WORKFLOW_RESULTS_CLEARED, 'informational', {
      workflowId: state.current.id,
    });

    const prepOutputs = _deepMerge(outputsDefs, outputs);

    for (let i = 0; i < prepOutputs.length; i++) {
      const output = prepOutputs[i];
      const { id, nodeId, title } = output;

      const h4 = document.createElement('h4');
      h4.className = `${ROOT_CLASS}__result-title`;
      h4.textContent = title || `Node #${nodeId}`;
      element.appendChild(h4);

      const grid = document.createElement('div');
      grid.className = `${ROOT_CLASS}__result-grid`;
      element.appendChild(grid);

      const wrapper = document.createElement('div');
      wrapper.className = `${ROOT_CLASS}__result-item`;

      const component = createOutputComponent(output);
      component.id = id;

      wrapper.appendChild(component);
      grid.appendChild(wrapper);
    }

    element.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    });

    debugLog(WORKFLOW_RESULTS_RENDERED, 'informational', {
      workflowId: state.current.id,
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

    const category =
      state.current.status === 'error'
        ? 'error'
        : state.current.status === 'ready'
        ? 'success'
        : 'informational';
    debugLog(STATUS_UPDATED, category, {
      workflowId: state.current.id,
      status: state.current.status,
      message,
    });
  };

  const updateTitle = (state: WorkflowState) => {
    const element = state.ui.layout.main.workflow.title;
    if (!element) {
      return;
    }

    element.textContent = _getWorkflowTitle(state);
  };

  const render = (state: WorkflowState) => {
    if (!section) {
      return;
    }

    if (state.current.id !== id) {
      updateDescription(state);
      updateTitle(state);
      updateOptions(state);
      id = state.current.id;
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

  const setCellStatus = (state: WorkflowState, id: string, status: WorkflowCellStatus = '') => {
    const { ui } = state;

    const field = ui.layout.main.workflow.cells.find((el) => el.id === id);
    const wrapper = field?.parentElement;
    if (wrapper) {
      wrapper.dataset.status = status;
    }
    if (status) {
      debugLog(WORKFLOW_INPUT_FLAGGED, 'informational', {
        workflowId: state.current.id,
        field: id,
        status,
      });
    }
  };

  const destroy = () => {
    section?.remove();
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
      debugLog(WORKFLOW_LAYOUT_DESTROYED, 'informational', {
        workflowId: mountedState.current.id ?? null,
      });
    }

    section = null;
    optionsWrapper = null;
    resultWrapper = null;
    runButton = null;
    statusWrapper = null;
    titleElement = null;
    id = null;
    lastStatus = null;
    lastMessage = null;
    lastResultsRef = null;
    mountedState = null;
  };

  return {
    mount,
    render,
    destroy,
    setCellStatus,
  };
};
//#endregion
