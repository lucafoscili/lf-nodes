import { LfDataDataset, LfDataNode, LfTreeInterface } from '@lf-widgets/foundations';
import { IMAGE_API } from '../api/image';
import { SETTINGS, TREE_DATA } from '../fixtures/imageEditor';
import { EV_HANDLERS, getStatusColumn, setGridStatus, updateCb } from '../helpers/imageEditor';
import {
  deriveDirectoryValue,
  ensureDatasetContext,
  getNavigationDirectory,
  mergeNavigationDirectory,
} from '../helpers/imageEditor/dataset';
import {
  extractNavigationTreeMetadata,
  findNodeInNavigationTree,
  mergeNavigationTreeChildren,
  prepareNavigationTreeDataset,
} from '../helpers/imageEditor/tree';
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
  ImageEditorNavigationTreeState,
  ImageEditorNormalizeCallback,
  ImageEditorState,
  ImageEditorStatus,
} from '../types/widgets/imageEditor';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, getLfManager, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, ImageEditorState>();
export const IMAGE_EDITOR_INSTANCES = new Set<ImageEditorState>();

const NAVIGATION_TREE_PROPS_BASE: Partial<LfTreeInterface> = {
  lfAccordionLayout: true,
  lfFilter: true,
  lfInitialExpansionDepth: 0,
  lfGrid: true,
  lfSelectable: false,
} as const;

const shouldEnableNavigationTree = (node: { comfyClass?: string }) =>
  node?.comfyClass === NodeName.loadAndEditImages;

const normalizeDirectoryRequest = (value: unknown): string =>
  typeof value === 'string' ? value : '';

const syncNavigationDirectoryControl = async (
  state: ImageEditorState,
  directoryValue: string | undefined,
): Promise<void> => {
  const { imageviewer } = state.elements;
  if (!imageviewer?.getComponents) {
    return;
  }

  const targetValue = normalizeDirectoryRequest(directoryValue);

  try {
    const components = await imageviewer.getComponents();
    const textfield = components?.navigation?.textfield;
    if (!textfield || typeof textfield.setValue !== 'function') {
      return;
    }

    const currentValue =
      typeof textfield.getValue === 'function' ? await textfield.getValue() : undefined;

    if ((currentValue ?? '') === targetValue) {
      return;
    }

    state.isSyncingDirectory = true;
    await textfield.setValue(targetValue);
  } catch (error) {
    getLfManager().log('Failed to synchronize directory input.', { error }, LogSeverity.Warning);
  } finally {
    state.isSyncingDirectory = false;
  }
};

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

    const navigationTreeEnabled = shouldEnableNavigationTree(node);
    const navigationTreeState: ImageEditorNavigationTreeState | undefined = navigationTreeEnabled
      ? {
          dataset: undefined as (LfDataDataset & { parent_id?: string }) | undefined,
          prepared: undefined as (LfDataDataset & { parent_id?: string }) | undefined,
          loadedNodes: new Set<string>(),
          pendingNodes: new Set<string>(),
          expandedNodes: new Set<string>(),
          handlers: undefined,
          rootsLoaded: false,
          selectedNodeId: undefined,
        }
      : undefined;

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

    const updateNavigationTreeDataset = (
      treeDataset: (LfDataDataset & { parent_id?: string }) | null | undefined,
      { reset }: { reset?: boolean } = {},
    ) => {
      if (!navigationTreeState) {
        return;
      }

      if (reset) {
        navigationTreeState.loadedNodes.clear();
        navigationTreeState.pendingNodes.clear();
        navigationTreeState.rootsLoaded = false;
        navigationTreeState.expandedNodes.clear();
        navigationTreeState.selectedNodeId = undefined;
      }

      if (!treeDataset) {
        const fallbackColumns =
          navigationTreeState.prepared?.columns ??
          navigationTreeState.dataset?.columns ??
          (imageviewer.lfTreeProps?.lfDataset as LfDataDataset | undefined)?.columns ??
          [];

        navigationTreeState.dataset = undefined;
        navigationTreeState.prepared = undefined;

        const previousProps = imageviewer.lfTreeProps ?? {};
        imageviewer.lfTreeProps = {
          ...NAVIGATION_TREE_PROPS_BASE,
          ...previousProps,
          lfDataset: {
            columns: fallbackColumns,
            nodes: [],
          },
        };
        return;
      }

      const shouldMerge = Boolean(navigationTreeState.dataset) && !reset;
      const mergedDataset =
        shouldMerge && navigationTreeState.dataset
          ? mergeNavigationTreeChildren(navigationTreeState.dataset, treeDataset) ??
            navigationTreeState.dataset
          : treeDataset;

      navigationTreeState.dataset = mergedDataset ?? undefined;

      const parentId = treeDataset.parent_id;
      if (parentId) {
        navigationTreeState.loadedNodes.add(parentId);
        navigationTreeState.pendingNodes.delete(parentId);
      }

      if (treeDataset.parent_id === 'root') {
        navigationTreeState.rootsLoaded = true;
        navigationTreeState.loadedNodes.add('root');
        navigationTreeState.pendingNodes.delete('root');
      }

      const prepared = mergedDataset ? prepareNavigationTreeDataset(mergedDataset) : undefined;
      navigationTreeState.prepared = prepared ?? undefined;

      const datasetForTree =
        prepared ??
        (mergedDataset
          ? {
              ...mergedDataset,
              nodes: Array.isArray(mergedDataset.nodes) ? mergedDataset.nodes : [],
            }
          : {
              columns: treeDataset.columns ?? [],
              nodes: [],
              parent_id: treeDataset.parent_id,
            });

      const previousProps = imageviewer.lfTreeProps ?? {};
      imageviewer.lfTreeProps = {
        ...NAVIGATION_TREE_PROPS_BASE,
        ...previousProps,
        lfDataset: datasetForTree,
      };

      void applyNavigationTreePersistence();
    };

    const applyNavigationTreePersistence = async (): Promise<void> => {
      if (
        !navigationTreeState ||
        !navigationTreeState.expandedNodes ||
        !imageviewer?.getComponents
      ) {
        return;
      }

      const shouldPersistSelection = Boolean(navigationTreeState.selectedNodeId);
      const shouldPersistExpansion = navigationTreeState.expandedNodes.size > 0;

      if (!shouldPersistSelection && !shouldPersistExpansion) {
        return;
      }

      try {
        const components = await imageviewer.getComponents();
        const tree = components?.navigation?.tree;
        if (!tree) {
          return;
        }

        const dataset =
          (imageviewer.lfTreeProps?.lfDataset as
            | (LfDataDataset & { parent_id?: string })
            | undefined) ??
          navigationTreeState.prepared ??
          navigationTreeState.dataset;

        if (!dataset) {
          return;
        }

        type TreeWithState = typeof tree & {
          expandedNodes?: Set<LfDataNode>;
          selectedNode?: LfDataNode | null;
          refresh?: () => Promise<void>;
        };

        const treeWithState = tree as TreeWithState;

        if (shouldPersistExpansion) {
          const desiredNodes = new Set<LfDataNode>();
          navigationTreeState.expandedNodes.forEach((nodeId) => {
            const match = findNodeInNavigationTree(dataset, (node) => node.id === nodeId);
            if (match) {
              desiredNodes.add(match);
            }
          });

          if (desiredNodes.size > 0) {
            const nextExpanded = new Set<LfDataNode>(desiredNodes);
            treeWithState.expandedNodes = nextExpanded;
          }
        }

        if (shouldPersistSelection && navigationTreeState.selectedNodeId) {
          const selectedNode = findNodeInNavigationTree(
            dataset,
            (node) => node.id === navigationTreeState.selectedNodeId,
          );

          if (selectedNode) {
            treeWithState.selectedNode = selectedNode;
          }
        }

        if (typeof treeWithState.refresh === 'function') {
          await treeWithState.refresh();
        }
      } catch (error) {
        getLfManager().log(
          'Failed to persist navigation tree state.',
          { error },
          LogSeverity.Warning,
        );
      }
    };

    const loadNavigationTreeRoots = async () => {
      if (!navigationTreeState || navigationTreeState.rootsLoaded) {
        return;
      }

      navigationTreeState.pendingNodes.add('root');

      try {
        const response = await IMAGE_API.explore('', { scope: 'roots' });
        if (response.status !== LogSeverity.Success) {
          return;
        }

        const roots = response.data?.tree;
        if (!roots) {
          return;
        }

        updateNavigationTreeDataset(roots, { reset: true });
      } catch (error) {
        getLfManager().log('Failed to load navigation tree roots.', { error }, LogSeverity.Warning);
      } finally {
        navigationTreeState.pendingNodes.delete('root');
      }
    };

    const handleNavigationTreeExpansion = async (nodeToExpand?: LfDataNode) => {
      if (!navigationTreeEnabled || !navigationTreeState || !nodeToExpand) {
        return;
      }

      const metadata = extractNavigationTreeMetadata(nodeToExpand);
      if (!metadata || metadata.isPlaceholder || !metadata.hasChildren) {
        return;
      }

      const nodeId = metadata.id;
      if (!nodeId) {
        return;
      }

      const wasExpanded = navigationTreeState.expandedNodes.has(nodeId);
      if (wasExpanded) {
        navigationTreeState.expandedNodes.delete(nodeId);
      } else {
        navigationTreeState.expandedNodes.add(nodeId);
      }

      if (wasExpanded) {
        void applyNavigationTreePersistence();
        return;
      }

      if (navigationTreeState.pendingNodes.has(nodeId)) {
        return;
      }

      if (navigationTreeState.loadedNodes.has(nodeId)) {
        void applyNavigationTreePersistence();
        return;
      }

      const expansionDirectory = normalizeDirectoryRequest(
        metadata.paths?.resolved ?? metadata.paths?.raw ?? metadata.paths?.relative ?? '',
      );

      const nodePath = metadata.paths?.resolved ?? metadata.paths?.raw ?? expansionDirectory;

      if (!expansionDirectory || !nodePath) {
        return;
      }

      navigationTreeState.pendingNodes.add(nodeId);

      try {
        const response = await IMAGE_API.explore(expansionDirectory, {
          scope: 'tree',
          nodePath,
        });

        if (response.status !== LogSeverity.Success) {
          return;
        }

        const branch = response.data?.tree;
        if (!branch) {
          navigationTreeState.loadedNodes.add(nodeId);
          return;
        }

        updateNavigationTreeDataset(branch, { reset: false });
      } catch (error) {
        getLfManager().log(
          'Failed to expand navigation tree node.',
          { error, nodeId, path: nodePath },
          LogSeverity.Warning,
        );
      } finally {
        navigationTreeState.pendingNodes.delete(nodeId);
      }
    };

    const handleNavigationTreeSelection = async (nodeToSelect?: LfDataNode) => {
      if (!navigationTreeEnabled || !navigationTreeState || !nodeToSelect) {
        return;
      }

      const metadata = extractNavigationTreeMetadata(nodeToSelect);
      if (!metadata || metadata.isPlaceholder) {
        return;
      }

      const currentState = STATE.get(wrapper);
      if (!currentState) {
        return;
      }

      navigationTreeState.selectedNodeId = metadata.id ?? undefined;
      void applyNavigationTreePersistence();

      const targetDirectory = normalizeDirectoryRequest(
        metadata.paths?.resolved ??
          metadata.paths?.raw ??
          metadata.paths?.relative ??
          metadata.name ??
          '',
      );

      const currentDirectory = normalizeDirectoryRequest(
        currentState.directoryValue ??
          deriveDirectoryValue(currentState.directory) ??
          currentState.lastRequestedDirectory ??
          '',
      );

      if (targetDirectory === currentDirectory && !metadata.isRoot) {
        return;
      }

      await currentState.refreshDirectory?.(targetDirectory);
      void applyNavigationTreePersistence();
    };

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

    const state: ImageEditorState = {
      elements: { actionButtons, controls: {}, grid, imageviewer, settings },
      contextId: undefined,
      directory: undefined,
      directoryValue: undefined,
      filter: null,
      filterType: null,
      lastBrushSettings: JSON.parse(JSON.stringify(SETTINGS.brush.settings)),
      hasAutoDirectoryLoad: false,
      isSyncingDirectory: false,
      lastRequestedDirectory: undefined,
      node,
      navigationTree: navigationTreeState,
      refreshDirectory: refresh,
      update: {
        preview: () => updateCb(STATE.get(wrapper)).then(() => {}),
        snapshot: () => updateCb(STATE.get(wrapper), true).then(() => {}),
      },
      wrapper,
    };

    if (navigationTreeState) {
      navigationTreeState.handlers = {
        expand: handleNavigationTreeExpansion,
        select: handleNavigationTreeSelection,
      };
    }

    STATE.set(wrapper, state);
    IMAGE_EDITOR_INSTANCES.add(state);

    void Promise.resolve().then(async () => {
      const currentState = STATE.get(wrapper);
      if (!currentState) {
        return;
      }

      if (navigationTreeEnabled) {
        await loadNavigationTreeRoots();
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
