import { getLfFramework } from '@lf-widgets/framework';
import { buttonHandler } from '../handlers/button';
import { WorkflowSectionController } from '../types/section';
import { WorkflowRunEntry, WorkflowStore } from '../types/state';
import {
  clearChildren,
  deepMerge,
  formatStatus,
  formatTimestamp,
  stringifyDetail,
  summarizeDetail,
} from '../utils/common';
import { DEBUG_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import {
  listCompatibleArtifactTargets,
  queueArtifactHandoff,
  WorkflowArtifactTarget,
  WorkflowOutputArtifact,
} from '../utils/artifact-handoff';
import { createComponent, createOutputComponent } from './components';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'results-section';
export const RESULTS_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  actions: theme.bemClass(ROOT_CLASS, 'actions'),
  back: theme.bemClass(ROOT_CLASS, 'back'),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  empty: theme.bemClass(ROOT_CLASS, 'empty'),
  grid: theme.bemClass(ROOT_CLASS, 'grid'),
  h3: theme.bemClass(ROOT_CLASS, 'title-h3'),
  history: theme.bemClass(ROOT_CLASS, 'history'),
  handoff: theme.bemClass(ROOT_CLASS, 'handoff'),
  handoffArtifact: theme.bemClass(ROOT_CLASS, 'handoff-artifact'),
  handoffCancel: theme.bemClass(ROOT_CLASS, 'handoff-cancel'),
  handoffDestination: theme.bemClass(ROOT_CLASS, 'handoff-destination'),
  handoffSubmit: theme.bemClass(ROOT_CLASS, 'handoff-submit'),
  remix: theme.bemClass(ROOT_CLASS, 'remix'),
  item: theme.bemClass(ROOT_CLASS, 'item'),
  results: theme.bemClass(ROOT_CLASS, 'results'),
  subtitle: theme.bemClass(ROOT_CLASS, 'subtitle'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
  useOutput: theme.bemClass(ROOT_CLASS, 'use-output'),
} as const;
//#endregion

//#region Helpers
const _formatDescription = (selectedRun: WorkflowRunEntry | null, description: string) => {
  if (!selectedRun) {
    return description;
  }

  const timestamp = selectedRun.updatedAt || selectedRun.createdAt;
  const submission = selectedRun.submissionId
    ? ` · Submission ${selectedRun.submissionId}`
    : '';
  return `Run ${selectedRun.runId.slice(0, 8)}${submission} · ${formatStatus(
    selectedRun.status,
  )} · ${formatTimestamp(timestamp)}`;
};
const _description = () => {
  const p = document.createElement('p');
  p.className = RESULTS_CLASSES.description;

  return p;
};
const _results = () => {
  const cellWrapper = document.createElement('div');
  cellWrapper.className = RESULTS_CLASSES.results;

  return cellWrapper;
};
const _title = (store: WorkflowStore) => {
  const { arrowBack, folder, refresh } = theme.get.icons();
  const { manager } = store.getState();

  const title = document.createElement('div');
  title.className = RESULTS_CLASSES.title;

  const h3 = document.createElement('h3');
  h3.className = RESULTS_CLASSES.h3;

  const actions = document.createElement('div');
  actions.className = RESULTS_CLASSES.actions;

  const backButton = document.createElement('lf-button');
  backButton.className = RESULTS_CLASSES.back;
  backButton.lfIcon = arrowBack;
  backButton.lfLabel = 'Back';
  backButton.lfStyling = 'flat';
  backButton.lfUiSize = 'small';
  backButton.lfUiState = 'disabled';
  backButton.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  const historyButton = document.createElement('lf-button');
  historyButton.className = RESULTS_CLASSES.history;
  historyButton.lfIcon = folder;
  historyButton.lfLabel = 'History';
  historyButton.lfStyling = 'flat';
  historyButton.lfUiSize = 'small';
  historyButton.lfUiState = manager.runs.all().length === 0 ? 'disabled' : 'primary';
  historyButton.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  const remixButton = document.createElement('lf-button');
  remixButton.className = RESULTS_CLASSES.remix;
  remixButton.lfIcon = refresh;
  remixButton.lfLabel = 'Remix';
  remixButton.lfStyling = 'flat';
  remixButton.lfUiSize = 'small';
  remixButton.lfUiState = 'disabled';
  remixButton.addEventListener('lf-button-event', (e) => buttonHandler(e, store));

  const useOutputButton = document.createElement('lf-button');
  useOutputButton.className = RESULTS_CLASSES.useOutput;
  useOutputButton.lfIcon = refresh;
  useOutputButton.lfLabel = 'Use in…';
  useOutputButton.lfStyling = 'flat';
  useOutputButton.lfUiSize = 'small';
  useOutputButton.lfUiState = 'disabled';

  title.appendChild(h3);
  title.appendChild(actions);
  actions.appendChild(backButton);
  actions.appendChild(remixButton);
  actions.appendChild(useOutputButton);
  actions.appendChild(historyButton);

  return {
    actions,
    backButton,
    h3,
    historyButton,
    remixButton,
    title,
    useOutputButton,
  };
};

const _handoff = () => {
  const root = document.createElement('section');
  root.className = RESULTS_CLASSES.handoff;
  root.hidden = true;

  const heading = document.createElement('h4');
  heading.textContent = 'Use a saved output as an input';
  const description = document.createElement('p');
  description.textContent =
    'Choose an output and destination. Runner keeps an opaque link to the saved artifact; no re-upload is needed.';

  const artifactLabel = document.createElement('label');
  artifactLabel.textContent = 'Output';
  const artifact = document.createElement('select');
  artifact.className = RESULTS_CLASSES.handoffArtifact;
  artifactLabel.appendChild(artifact);

  const destinationLabel = document.createElement('label');
  destinationLabel.textContent = 'Destination';
  const destination = document.createElement('select');
  destination.className = RESULTS_CLASSES.handoffDestination;
  destinationLabel.appendChild(destination);

  const controls = document.createElement('div');
  const submit = document.createElement('lf-button');
  submit.className = RESULTS_CLASSES.handoffSubmit;
  submit.lfLabel = 'Continue';
  submit.lfUiState = 'primary';
  submit.lfUiSize = 'small';
  const cancel = document.createElement('lf-button');
  cancel.className = RESULTS_CLASSES.handoffCancel;
  cancel.lfLabel = 'Cancel';
  cancel.lfStyling = 'flat';
  cancel.lfUiSize = 'small';
  controls.appendChild(submit);
  controls.appendChild(cancel);

  root.appendChild(heading);
  root.appendChild(description);
  root.appendChild(artifactLabel);
  root.appendChild(destinationLabel);
  root.appendChild(controls);

  return { artifact, cancel, destination, root, submit };
};
//#endregion

export const createResultsSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { WORKFLOW_RESULTS_DESTROYED, WORKFLOW_RESULTS_MOUNTED, WORKFLOW_RESULTS_UPDATED } =
    DEBUG_MESSAGES;
  let renderedContent: {
    element: HTMLElement;
    error: unknown;
    outputs: unknown;
    resultPayload: unknown;
    runId: string | null;
  } | null = null;
  let handoffArtifacts: WorkflowOutputArtifact[] = [];
  let handoffTargets: WorkflowArtifactTarget[] = [];
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in RESULTS_CLASSES) {
      const element = RESULTS_CLASSES[cls];
      uiRegistry.remove(element);
    }
    renderedContent = null;

    debugLog(WORKFLOW_RESULTS_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[RESULTS_CLASSES._]) {
      return;
    }

    const _root = document.createElement('section');
    _root.className = RESULTS_CLASSES._;

    const results = _results();
    const description = _description();
    const {
      actions,
      backButton,
      h3,
      historyButton,
      remixButton,
      title,
      useOutputButton,
    } = _title(store);
    const handoff = _handoff();

    const updateDestinations = () => {
      const previousTarget = handoffTargets[Number(handoff.destination.value) || 0];
      const artifact = handoffArtifacts[Number(handoff.artifact.value) || 0];
      handoffTargets = artifact
        ? listCompatibleArtifactTargets(store.getState().workflows, artifact)
        : [];
      handoff.destination.replaceChildren(
        ...handoffTargets.map((target, index) => {
          const option = document.createElement('option');
          option.value = String(index);
          option.textContent = `${target.workflowName} — ${target.inputName}`;
          return option;
        }),
      );
      const preservedTarget = previousTarget
        ? handoffTargets.findIndex(
            (target) =>
              target.workflowId === previousTarget.workflowId &&
              target.inputId === previousTarget.inputId,
          )
        : -1;
      handoff.destination.value = String(Math.max(0, preservedTarget));
      handoff.submit.lfUiState = handoffTargets.length ? 'primary' : 'disabled';
    };

    handoff.artifact.addEventListener('change', updateDestinations);
    useOutputButton.addEventListener('lf-button-event', (event) => {
      if ((event as CustomEvent<{ eventType?: string }>).detail?.eventType !== 'click') {
        return;
      }
      handoff.root.hidden = !handoff.root.hidden;
      if (!handoff.root.hidden) {
        updateDestinations();
        handoff.artifact.focus();
      }
    });
    handoff.cancel.addEventListener('lf-button-event', (event) => {
      if ((event as CustomEvent<{ eventType?: string }>).detail?.eventType === 'click') {
        handoff.root.hidden = true;
        useOutputButton.focus();
      }
    });
    handoff.submit.addEventListener('lf-button-event', (event) => {
      if ((event as CustomEvent<{ eventType?: string }>).detail?.eventType !== 'click') {
        return;
      }
      const artifact = handoffArtifacts[Number(handoff.artifact.value) || 0];
      const target = handoffTargets[Number(handoff.destination.value) || 0];
      if (artifact && target) {
        queueArtifactHandoff(store, artifact, target);
      }
    });

    _root.appendChild(title);
    _root.appendChild(description);
    _root.appendChild(handoff.root);
    _root.appendChild(results);

    elements[MAIN_CLASSES._].prepend(_root);

    uiRegistry.set(RESULTS_CLASSES._, _root);
    uiRegistry.set(RESULTS_CLASSES.actions, actions);
    uiRegistry.set(RESULTS_CLASSES.back, backButton);
    uiRegistry.set(RESULTS_CLASSES.description, description);
    uiRegistry.set(RESULTS_CLASSES.h3, h3);
    uiRegistry.set(RESULTS_CLASSES.history, historyButton);
    uiRegistry.set(RESULTS_CLASSES.handoff, handoff.root);
    uiRegistry.set(RESULTS_CLASSES.handoffArtifact, handoff.artifact);
    uiRegistry.set(RESULTS_CLASSES.handoffCancel, handoff.cancel);
    uiRegistry.set(RESULTS_CLASSES.handoffDestination, handoff.destination);
    uiRegistry.set(RESULTS_CLASSES.handoffSubmit, handoff.submit);
    uiRegistry.set(RESULTS_CLASSES.remix, remixButton);
    uiRegistry.set(RESULTS_CLASSES.results, results);
    uiRegistry.set(RESULTS_CLASSES.title, title);
    uiRegistry.set(RESULTS_CLASSES.useOutput, useOutputButton);

    debugLog(WORKFLOW_RESULTS_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const { syntax } = getLfFramework();
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const selectedRun = manager.runs.selected();
    const runs = manager.runs.all();

    const descr = elements[RESULTS_CLASSES.description] as HTMLElement;
    const element = elements[RESULTS_CLASSES.results] as HTMLElement;
    const h3 = elements[RESULTS_CLASSES.h3] as HTMLElement;
    const backButton = elements[RESULTS_CLASSES.back] as HTMLLfButtonElement | undefined;
    const historyButton = elements[RESULTS_CLASSES.history] as HTMLLfButtonElement | undefined;
    const handoff = elements[RESULTS_CLASSES.handoff] as HTMLElement | undefined;
    const handoffArtifact = elements[
      RESULTS_CLASSES.handoffArtifact
    ] as HTMLSelectElement | undefined;
    const remixButton = elements[RESULTS_CLASSES.remix] as HTMLLfButtonElement | undefined;
    const useOutputButton = elements[
      RESULTS_CLASSES.useOutput
    ] as HTMLLfButtonElement | undefined;

    descr.textContent = _formatDescription(selectedRun, manager.workflow.description());
    h3.textContent = selectedRun?.workflowName || manager.workflow.title();
    backButton.lfUiState = selectedRun ? 'primary' : 'disabled';
    historyButton.lfUiState = runs.length > 0 ? 'primary' : 'disabled';
    const workflowAvailable = Boolean(
      selectedRun?.workflowId &&
        state.workflows?.nodes?.some((node) => node.id === selectedRun.workflowId),
    );
    if (remixButton) {
      remixButton.lfUiState =
        selectedRun && workflowAvailable && Object.keys(selectedRun.inputs || {}).length > 0
          ? 'primary'
          : 'disabled';
    }

    const artifacts = (selectedRun?.artifacts || [])
      .filter(
        (artifact): artifact is WorkflowOutputArtifact =>
          Boolean(
            artifact &&
              artifact.schema === 'lf.workflow-artifact.v1' &&
              artifact.reference?.schema === 'lf.workflow-artifact-ref.v1' &&
              artifact.filename,
          ),
      )
      .sort((a, b) => Number(b.available) - Number(a.available));
    const hasUsableArtifact = artifacts.some(
      (artifact) =>
        artifact.available &&
        listCompatibleArtifactTargets(state.workflows, artifact).length > 0,
    );
    if (useOutputButton) {
      useOutputButton.lfUiState = hasUsableArtifact ? 'primary' : 'disabled';
      useOutputButton.hidden = selectedRun?.status !== 'succeeded' || artifacts.length === 0;
      useOutputButton.title = hasUsableArtifact
        ? 'Use a saved output in another workflow'
        : artifacts.some((artifact) => artifact.available)
          ? 'No ready workflow accepts this output type'
          : 'Saved outputs are no longer available on disk';
    }
    if (handoff && handoffArtifact) {
      if (renderedContent?.runId !== selectedRun?.runId || !hasUsableArtifact) {
        handoff.hidden = true;
      }
      const previousArtifactId = handoffArtifacts[Number(handoffArtifact.value) || 0]?.reference
        .artifactId;
      handoffArtifacts = artifacts;
      const nameCounts = artifacts.reduce((counts, artifact) => {
        counts.set(artifact.filename, (counts.get(artifact.filename) || 0) + 1);
        return counts;
      }, new Map<string, number>());
      handoffArtifact.replaceChildren(
        ...artifacts.map((artifact, index) => {
          const option = document.createElement('option');
          option.value = String(index);
          option.disabled =
            !artifact.available ||
            listCompatibleArtifactTargets(state.workflows, artifact).length === 0;
          const source = (nameCounts.get(artifact.filename) || 0) > 1
            ? ` · node ${artifact.nodeId || 'unknown'}`
            : '';
          const unavailable = artifact.available ? '' : ' · file no longer on disk';
          option.textContent = `${artifact.filename}${source}${unavailable}`;
          return option;
        }),
      );
      const firstUsable = artifacts.findIndex(
        (artifact) =>
          artifact.available &&
          listCompatibleArtifactTargets(state.workflows, artifact).length > 0,
      );
      const preservedArtifact = previousArtifactId
        ? artifacts.findIndex(
            (artifact) =>
              artifact.reference.artifactId === previousArtifactId &&
              artifact.available &&
              listCompatibleArtifactTargets(state.workflows, artifact).length > 0,
          )
        : -1;
      handoffArtifact.value = String(
        Math.max(0, preservedArtifact >= 0 ? preservedArtifact : firstUsable),
      );
      handoffArtifact.dispatchEvent(new Event('change'));
    }

    const outputs = state.results ?? selectedRun?.outputs ?? null;
    const nextContent = {
      element,
      error: selectedRun?.error ?? null,
      outputs,
      resultPayload: selectedRun?.resultPayload ?? null,
      runId: selectedRun?.runId ?? null,
    };
    if (
      renderedContent?.element === nextContent.element &&
      renderedContent.error === nextContent.error &&
      renderedContent.outputs === nextContent.outputs &&
      renderedContent.resultPayload === nextContent.resultPayload &&
      renderedContent.runId === nextContent.runId
    ) {
      // Queue/SSE/header state can change while a terminal result is open.
      // Keep its media DOM intact so native audio/video playback is not reset.
      return;
    }
    renderedContent = nextContent;
    clearChildren(element);

    const nodeIds = outputs ? Object.keys(outputs) : [];
    if (nodeIds.length === 0) {
      const empty = document.createElement('p');
      empty.className = RESULTS_CLASSES.empty;
      const summary = summarizeDetail(selectedRun?.error ?? null);
      if (selectedRun) {
        empty.textContent = summary
          ? `This run has not produced any outputs yet. ${summary}`
          : 'This run has not produced any outputs yet.';
      } else {
        empty.textContent = 'Select a run to inspect its outputs.';
      }
      element.appendChild(empty);

      const appendCodeBlock = (label: string, content: string | null) => {
        if (!content) {
          return;
        }

        const wrapper = document.createElement('div');
        wrapper.className = RESULTS_CLASSES.item;

        const heading = document.createElement('h4');
        heading.className = RESULTS_CLASSES.subtitle;
        heading.textContent = label;

        const code = createComponent.code({
          lfLanguage: syntax.json.isLikeString(content) ? 'json' : 'markdown',
          lfStickyHeader: false,
          lfUiState: 'danger',
          lfValue: content,
        });

        wrapper.appendChild(heading);
        wrapper.appendChild(code);

        element.appendChild(wrapper);
      };

      appendCodeBlock('Error detail', stringifyDetail(selectedRun?.error ?? null));
      appendCodeBlock(
        'Run payload',
        stringifyDetail(selectedRun?.resultPayload?.body ?? selectedRun?.resultPayload ?? null),
      );

      return;
    }

    const workflow = manager.workflow.current();
    const outputsDefs = workflow ? manager.workflow.cells('output') : {};

    const prepOutputs = deepMerge(outputsDefs, outputs || {});

    for (let i = 0; i < prepOutputs.length; i++) {
      const output = prepOutputs[i];
      const { id, nodeId, title } = output;

      const h4 = document.createElement('h4');
      h4.className = RESULTS_CLASSES.subtitle;
      h4.textContent = title || `Node #${nodeId}`;
      element.appendChild(h4);

      const grid = document.createElement('div');
      grid.className = RESULTS_CLASSES.grid;
      element.appendChild(grid);

      const wrapper = document.createElement('div');
      wrapper.className = RESULTS_CLASSES.item;

      const component = createOutputComponent(output);
      component.id = id;

      wrapper.appendChild(component);
      grid.appendChild(wrapper);
    }

    debugLog(WORKFLOW_RESULTS_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
//#endregion
