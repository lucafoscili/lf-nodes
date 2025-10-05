import { LfTreeEventPayload, LfTreeInterface } from '@lf-widgets/foundations';
import { IMAGE_API } from '../api/image';
import { SETTINGS, TREE_DATA } from '../fixtures/imageEditor';
import { EV_HANDLERS, getStatusColumn, setGridStatus, updateCb } from '../helpers/imageEditor';
import {
  deriveDirectoryValue,
  ensureDatasetContext,
  getNavigationDirectory,
  mergeNavigationDirectory,
} from '../helpers/imageEditor/dataset';
import { syncNavigationDirectoryControl } from '../helpers/imageEditor/navigation';
import { createNavigationTreeManager } from '../helpers/imageEditor/navigationTree';
import { setBrush } from '../helpers/imageEditor/settings';
import { LfEventName } from '../types/events/events';
import { LogSeverity } from '../types/manager/manager';
import {
  ImageEditorActionButtons,
  ImageEditorCSS,
  ImageEditorDataset,
  ImageEditorDeserializedValue,
  ImageEditorFactory,
  ImageEditorIcons,
  ImageEditorNormalizeCallback,
  ImageEditorState,
  ImageEditorStatus,
} from '../types/widgets/imageEditor';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import {
  createDOMWidget,
  getLfManager,
  normalizeDirectoryRequest,
  normalizeValue,
} from '../utils/common';

export const IMAGE_EDITOR_INSTANCES = new Set<ImageEditorState>();
const STATE = new WeakMap<HTMLDivElement, ImageEditorState>();

const NAVIGATION_TREE_PROPS_BASE: Partial<LfTreeInterface> = {
  lfAccordionLayout: true,
  lfFilter: true,
  lfInitialExpansionDepth: 0,
  lfGrid: true,
  lfSelectable: true,
} as const;

export const imageEditorFactory: ImageEditorFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue: () => {
        const { imageviewer } = STATE.get(wrapper).elements;

        return imageviewer.lfDataset || {};
      },
      setValue: (value) => {
        const state = STATE.get(wrapper);
        const { actionButtons, grid, imageviewer } = state.elements;

        const callback: ImageEditorNormalizeCallback = (_, u) => {
          const parsedValue = u.parsedJson as ImageEditorDeserializedValue;
          const isPending = getStatusColumn(parsedValue)?.title === ImageEditorStatus.Pending;
          if (isPending) {
            setGridStatus(ImageEditorStatus.Pending, grid, actionButtons);
          }

          const dataset = (parsedValue || {}) as ImageEditorDataset;
          ensureDatasetContext(dataset, state);

          const navigationDirectory = getNavigationDirectory(dataset);
          if (navigationDirectory) {
            state.directory = { ...navigationDirectory };
          }

          const derivedDirectoryValue = deriveDirectoryValue(navigationDirectory);
          if (derivedDirectoryValue !== undefined) {
            state.directoryValue = derivedDirectoryValue;
          }

          imageviewer.lfDataset = dataset;
          imageviewer
            .getComponents()
            .then(({ details }) => {
              const { canvas } = details;
              if (canvas) {
                setBrush(canvas, STATE.get(wrapper).lastBrushSettings);
              }
            })
            .catch((error) =>
              getLfManager().log(
                'Failed to prepare image editor canvas.',
                { error },
                LogSeverity.Warning,
              ),
            );

          void syncNavigationDirectoryControl(state, state.directoryValue);

          const shouldAutoLoad =
            !state.hasAutoDirectoryLoad &&
            (!Array.isArray(dataset?.nodes) || dataset.nodes.length === 0);

          if (shouldAutoLoad) {
            state.hasAutoDirectoryLoad = true;
            state.refreshDirectory?.(normalizeDirectoryRequest(state.directoryValue));
          }
        };

        normalizeValue(value, callback, CustomWidgetName.imageEditor);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const settings = document.createElement(TagName.Div);
    const imageviewer = document.createElement(TagName.LfImageviewer);

    const navigationTreeEnabled = node.comfyClass === NodeName.loadAndEditImages;
    let navigationManager: ReturnType<typeof createNavigationTreeManager> | null = null;
    let expandedNodes = new Set<string>();

    if (navigationTreeEnabled) {
      imageviewer.lfNavigationTree = {
        defaultOpen: true,
        enabled: true,
        minWidth: 240,
        width: 320,
        position: 'start',
      };
      imageviewer.lfTreeProps = {
        ...NAVIGATION_TREE_PROPS_BASE,
        lfDataset: { columns: [], nodes: [] },
      };
    }

    const refresh = async (directory: string) => {
      const state = STATE.get(wrapper);
      const normalizedDirectory = normalizeDirectoryRequest(directory);

      if (!state) {
        return;
      }

      state.hasAutoDirectoryLoad = true;
      state.lastRequestedDirectory = normalizedDirectory;

      try {
        if (navigationTreeEnabled) {
          const response = await IMAGE_API.explore(normalizedDirectory, { scope: 'dataset' });
          if (response.status !== LogSeverity.Success) {
            getLfManager().log('Images not found.', { response }, LogSeverity.Info);
            return;
          }

          const dataset = (response.data?.dataset ?? { nodes: [] }) as ImageEditorDataset;
          const mergedDirectory = mergeNavigationDirectory(dataset, { raw: normalizedDirectory });

          state.directory = { ...mergedDirectory };
          const derivedDirectoryValue = deriveDirectoryValue(mergedDirectory);
          state.directoryValue = derivedDirectoryValue ?? normalizedDirectory;
          state.lastRequestedDirectory = state.directoryValue;

          ensureDatasetContext(dataset, state);

          imageviewer.lfDataset = dataset;

          await syncNavigationDirectoryControl(state, state.directoryValue);

          // Sync tree selection to highlight the current directory
          if (state.navigationManager && state.directoryValue) {
            await state.navigationManager.syncSelectionByPath(state.directoryValue);
          }

          return;
        }

        const response = await IMAGE_API.get(normalizedDirectory);
        if (response.status !== LogSeverity.Success) {
          getLfManager().log('Images not found.', { response }, LogSeverity.Info);
          return;
        }

        const dataset = (response.data ?? { nodes: [] }) as ImageEditorDataset;
        const mergedDirectory = mergeNavigationDirectory(dataset, { raw: normalizedDirectory });

        state.directory = { ...mergedDirectory };
        const derivedDirectoryValue = deriveDirectoryValue(mergedDirectory);
        state.directoryValue = derivedDirectoryValue ?? normalizedDirectory;
        state.lastRequestedDirectory = state.directoryValue;

        ensureDatasetContext(dataset, state);

        imageviewer.lfDataset = dataset;
        await syncNavigationDirectoryControl(state, state.directoryValue);

        // Sync tree selection to highlight the current directory
        if (state.navigationManager && state.directoryValue) {
          await state.navigationManager.syncSelectionByPath(state.directoryValue);
        }
      } catch (error) {
        getLfManager().log(
          'Failed to refresh image directory.',
          { error, directory: normalizedDirectory },
          LogSeverity.Warning,
        );
      }
    };

    settings.classList.add(ImageEditorCSS.Settings);
    settings.slot = 'settings';

    imageviewer.classList.add(ImageEditorCSS.Widget);
    imageviewer.lfLoadCallback = async (_, value) => {
      const state = STATE.get(wrapper);
      if (!state || state.isSyncingDirectory) {
        return;
      }

      let directoryValue = normalizeDirectoryRequest(value);
      if (!directoryValue) {
        const fallbackDirectory =
          state.directoryValue ?? deriveDirectoryValue(state.directory) ?? undefined;
        directoryValue = normalizeDirectoryRequest(fallbackDirectory);
      }

      if (
        state.lastRequestedDirectory === directoryValue &&
        state.directoryValue === directoryValue
      ) {
        return;
      }

      await refresh(directoryValue);
    };
    imageviewer.lfValue = TREE_DATA;
    imageviewer.addEventListener(LfEventName.LfImageviewer, (e) =>
      EV_HANDLERS.imageviewer(STATE.get(wrapper), e),
    );
    imageviewer.appendChild(settings);

    const actionButtons: ImageEditorActionButtons = {};

    const state: ImageEditorState = {
      contextId: undefined,
      elements: { actionButtons, controls: {}, grid, imageviewer, settings },
      directory: undefined,
      directoryValue: undefined,
      filter: null,
      filterType: null,
      hasAutoDirectoryLoad: false,
      isSyncingDirectory: false,
      lastBrushSettings: JSON.parse(JSON.stringify(SETTINGS.brush.settings)),
      lastRequestedDirectory: undefined,
      node,
      refreshDirectory: refresh,
      update: {
        preview: () => updateCb(STATE.get(wrapper)).then(() => {}),
        snapshot: () => updateCb(STATE.get(wrapper), true).then(() => {}),
      },
      wrapper,
    };

    switch (node.comfyClass) {
      case NodeName.imagesEditingBreakpoint:
        const actions = document.createElement(TagName.Div);
        const interrupt = document.createElement(TagName.LfButton);
        const resume = document.createElement(TagName.LfButton);

        interrupt.lfIcon = ImageEditorIcons.Interrupt;
        interrupt.lfLabel = 'Interrupt workflow';
        interrupt.lfStretchX = true;
        interrupt.lfUiState = 'danger';
        interrupt.title = 'Click to interrupt the workflow.';
        interrupt.addEventListener(LfEventName.LfButton, (e) =>
          EV_HANDLERS.button(STATE.get(wrapper), e),
        );

        resume.lfIcon = ImageEditorIcons.Resume;
        resume.lfLabel = 'Resume workflow';
        resume.lfStretchX = true;
        resume.lfStyling = 'flat';
        resume.lfUiState = 'success';
        resume.title =
          'Click to resume the workflow. Remember to save your snapshots after editing the images!';
        resume.addEventListener(LfEventName.LfButton, (e) =>
          EV_HANDLERS.button(STATE.get(wrapper), e),
        );

        actions.classList.add(ImageEditorCSS.Actions);
        actions.appendChild(interrupt);
        actions.appendChild(resume);

        grid.classList.add(ImageEditorCSS.GridIsInactive);
        grid.classList.add(ImageEditorCSS.GridHasActions);
        grid.appendChild(actions);

        actionButtons.interrupt = interrupt;
        actionButtons.resume = resume;

        setGridStatus(ImageEditorStatus.Completed, grid, actionButtons);
    }

    grid.classList.add(ImageEditorCSS.Grid);
    grid.appendChild(imageviewer);

    content.classList.add(ImageEditorCSS.Content);
    content.appendChild(grid);

    wrapper.appendChild(content);

    const options = imageEditorFactory.options(wrapper);

    STATE.set(wrapper, state);
    IMAGE_EDITOR_INSTANCES.add(state);

    // Initialize navigation tree manager after state is set
    if (navigationTreeEnabled) {
      navigationManager = createNavigationTreeManager(imageviewer, state);
      state.navigationManager = navigationManager;

      // Handle tree events
      imageviewer.addEventListener('lf-tree-event', async (e) => {
        if (!navigationManager) return;

        const treeEvent = e as CustomEvent<LfTreeEventPayload>;
        const { node, expansion } = treeEvent.detail;
        if (!node) return;

        if (expansion) {
          // User clicked expand icon - load subdirectories
          await navigationManager.expandNode(node);
        } else {
          // User clicked node itself - select and load images
          await navigationManager.selectNode(node);
        }
      });
    }

    void Promise.resolve().then(async () => {
      const currentState = STATE.get(wrapper);
      if (!currentState) {
        return;
      }

      if (navigationTreeEnabled && navigationManager) {
        await navigationManager.loadRoots();
      }

      if (currentState.hasAutoDirectoryLoad) {
        return;
      }

      const currentDataset = currentState.elements.imageviewer?.lfDataset as
        | ImageEditorDataset
        | undefined;
      const hasNodes = Array.isArray(currentDataset?.nodes) && currentDataset.nodes.length > 0;
      const hasDirectoryValue = Boolean(currentState.directoryValue);

      if (hasNodes || hasDirectoryValue) {
        return;
      }

      currentState.refreshDirectory?.('');
    });

    return { widget: createDOMWidget(CustomWidgetName.imageEditor, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
