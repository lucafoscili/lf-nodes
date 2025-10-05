import {
  LfButtonEventPayload,
  LfCanvasElement,
  LfCanvasEventPayload,
  LfCanvasInterface,
  LfDataDataset,
  LfDataNode,
  LfEvent,
  LfImageEventPayload,
  LfImageviewerEventPayload,
  LfMasonryEventPayload,
  LfMasonryInterface,
  LfSliderEventPayload,
  LfTextfieldEventPayload,
  LfToggleEventPayload,
  LfTreeEventPayload,
} from '@lf-widgets/foundations';
import { IMAGE_API } from '../../api/image';
import { SETTINGS } from '../../fixtures/imageEditor';
import { LogSeverity } from '../../types/manager/manager';
import {
  EventHandlerDeps,
  ImageEditorBrushFilter,
  ImageEditorDataset,
  ImageEditorIcons,
  ImageEditorNavigationTreeState,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { NodeName } from '../../types/widgets/widgets';
import {
  canvasToBase64,
  debounce,
  getApiRoutes,
  getLfManager,
  isImage,
  isMasonry,
  isTree,
  LFInterruptFlags,
  normalizeDirectoryRequest,
} from '../../utils/common';
import {
  applySelectionColumn,
  buildSelectionPayload,
  deriveDirectoryValue,
  ensureDatasetContext,
  hasContextChanged,
  hasSelectionChanged,
  resolveSelectionIndex,
} from './dataset';
import { registerManualApplyChange } from './manualApply';
import { setBrush } from './settings';
import { extractNavigationTreeMetadata, findNodeInNavigationTree } from './tree';
import { updateCb } from './update';
/// @ts-ignore
import { api } from '/scripts/api.js';

export const createEventHandlers = ({
  handleInterruptForState,
  prepSettings,
}: EventHandlerDeps) => {
  const syncSelectionWithDataset = async (
    state: ImageEditorState,
    masonryEvent: CustomEvent<LfMasonryEventPayload>,
  ) => {
    const { elements } = state;
    const dataset = (elements.imageviewer.lfDataset || {}) as ImageEditorDataset;
    const effectiveContextId = ensureDatasetContext(dataset, state);
    const previousSelection = dataset.selection;
    const previousContextId = dataset.context_id ?? effectiveContextId;

    const { comp, selectedShape: rawSelectedShape } = masonryEvent.detail;
    const masonryComp = comp as LfMasonryInterface | undefined;

    let selectedShape = rawSelectedShape;

    if (
      (!selectedShape || typeof selectedShape.index !== 'number') &&
      masonryComp?.getSelectedShape
    ) {
      try {
        selectedShape = await masonryComp.getSelectedShape();
      } catch (error) {
        getLfManager().log('Failed to resolve masonry selection.', { error }, LogSeverity.Warning);
      }
    }

    const nodes = Array.isArray(dataset?.nodes) ? dataset.nodes : [];
    const selectionIndex = resolveSelectionIndex(selectedShape, nodes);

    if (typeof selectionIndex !== 'number') {
      getLfManager().log(
        'Unable to resolve selected masonry index.',
        { selectedShape },
        LogSeverity.Warning,
      );
      return;
    }

    const { selection, contextId } = buildSelectionPayload({
      dataset,
      index: selectionIndex,
      nodes,
      selectedShape,
      fallbackContextId: previousContextId ?? state.contextId,
    });

    const resolvedContextId =
      selection.context_id ?? contextId ?? previousContextId ?? state.contextId;
    if (resolvedContextId) {
      state.contextId = resolvedContextId;
      if (!selection.context_id) {
        selection.context_id = resolvedContextId;
      }
    }

    const nextDataset = applySelectionColumn(
      {
        ...dataset,
        context_id: dataset.context_id ?? resolvedContextId,
      },
      selection,
    );

    if (resolvedContextId && nextDataset.selection) {
      nextDataset.selection.context_id = resolvedContextId;
    }

    elements.imageviewer.lfDataset = nextDataset;

    if (!resolvedContextId) {
      return;
    }

    if (
      !hasSelectionChanged(previousSelection, nextDataset.selection) &&
      !hasContextChanged(previousContextId, nextDataset.context_id)
    ) {
      return;
    }

    getApiRoutes()
      .json.update(resolvedContextId, nextDataset)
      .catch((error) =>
        getLfManager().log(
          'Failed to persist image selection.',
          { error, contextId: resolvedContextId },
          LogSeverity.Warning,
        ),
      );
  };

  const navigationHandlers = {
    expand: async ({
      node,
      treeState,
      persist,
      updateDataset,
    }: {
      node: LfDataNode;
      treeState: ImageEditorNavigationTreeState | undefined;
      persist: () => Promise<void> | void;
      updateDataset: (
        dataset: (LfDataDataset & { parent_id?: string }) | null | undefined,
        options?: { reset?: boolean },
      ) => void;
    }) => {
      if (!treeState || !node) {
        return;
      }

      const metadata = extractNavigationTreeMetadata(node);
      if (!metadata || metadata.isPlaceholder || !metadata.hasChildren) {
        return;
      }

      const nodeId = metadata.id;
      if (!nodeId) {
        return;
      }

      const wasExpanded = treeState.expandedNodes.has(nodeId);
      if (wasExpanded) {
        treeState.expandedNodes.delete(nodeId);
      } else {
        treeState.expandedNodes.add(nodeId);
      }

      if (wasExpanded) {
        await persist();
        return;
      }

      if (treeState.pendingNodes.has(nodeId)) {
        return;
      }

      if (treeState.loadedNodes.has(nodeId)) {
        await persist();
        return;
      }

      const expansionDirectory = normalizeDirectoryRequest(
        metadata.paths?.resolved ?? metadata.paths?.raw ?? metadata.paths?.relative ?? '',
      );
      const nodePath = metadata.paths?.resolved ?? metadata.paths?.raw ?? expansionDirectory;

      if (!expansionDirectory || !nodePath) {
        return;
      }

      treeState.pendingNodes.add(nodeId);

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
          treeState.loadedNodes.add(nodeId);
          return;
        }

        updateDataset(branch, { reset: false });
      } catch (error) {
        getLfManager().log(
          'Failed to expand navigation tree node.',
          { error, nodeId, path: nodePath },
          LogSeverity.Warning,
        );
      } finally {
        treeState.pendingNodes.delete(nodeId);
      }
    },
    select: async ({
      node,
      treeState,
      persist,
      editorState,
    }: {
      node: LfDataNode;
      treeState: ImageEditorNavigationTreeState | undefined;
      persist: () => Promise<void> | void;
      editorState: ImageEditorState | undefined;
    }) => {
      if (!treeState || !node) {
        return;
      }

      const metadata = extractNavigationTreeMetadata(node);
      if (!metadata) {
        return;
      }

      let targetMetadata = metadata;

      if (metadata.isPlaceholder) {
        const datasetToSearch = treeState.dataset ?? treeState.prepared ?? undefined;
        const parentId = metadata.parentId;
        if (parentId && datasetToSearch) {
          const parentNode = findNodeInNavigationTree(
            datasetToSearch,
            (candidate) => extractNavigationTreeMetadata(candidate)?.id === parentId,
          );
          if (parentNode) {
            const parentMetadata = extractNavigationTreeMetadata(parentNode);
            if (parentMetadata) {
              targetMetadata = parentMetadata;
            }
          }
        }
      }

      if (!editorState) {
        return;
      }

      treeState.selectedNodeId = targetMetadata.id ?? metadata.id ?? undefined;
      await persist();

      const targetDirectory = normalizeDirectoryRequest(
        targetMetadata.paths?.resolved ??
          targetMetadata.paths?.raw ??
          targetMetadata.paths?.relative ??
          targetMetadata.name ??
          '',
      );

      const currentDirectory = normalizeDirectoryRequest(
        editorState.directoryValue ??
          deriveDirectoryValue(editorState.directory) ??
          editorState.lastRequestedDirectory ??
          '',
      );

      if (targetDirectory === currentDirectory && !targetMetadata.isRoot) {
        return;
      }

      await editorState.refreshDirectory?.(targetDirectory);
      await persist();
    },
  } as const;

  const handlers = {
    //#region Button
    button: async (state: ImageEditorState, e: CustomEvent<LfButtonEventPayload>) => {
      const { comp, eventType } = e.detail;

      if (eventType === 'click') {
        const isPatched = api?.[LFInterruptFlags.PatchedInterrupt] === true;

        switch (comp.lfIcon) {
          case ImageEditorIcons.Interrupt:
            getApiRoutes().comfy.interrupt();
            if (!isPatched) {
              await handleInterruptForState(state);
            }
            break;
          case ImageEditorIcons.Resume:
            await handleInterruptForState(state);
            break;
          default:
            break;
        }
      }
    },
    //#endregion
    //#region Canvas
    canvas: async (state: ImageEditorState, e: CustomEvent<LfCanvasEventPayload>) => {
      const { comp, eventType, points } = e.detail;
      const { filter, filterType } = state;

      switch (eventType) {
        case 'stroke':
          const originalFilter = filter;
          const originalFilterType = filterType;
          const canvas = await comp.getCanvas();
          const b64Canvas = canvasToBase64(canvas);
          if (filterType !== 'brush' && !filter?.hasCanvasAction) {
            state.filterType = 'brush';
          }

          const brushDefaults = {
            ...SETTINGS.brush.settings,
            ...state.lastBrushSettings,
          };

          const temporaryFilter: ImageEditorBrushFilter = {
            ...JSON.parse(JSON.stringify(SETTINGS.brush)),
            settings: {
              ...brushDefaults,
              b64_canvas: b64Canvas,
              color: comp.lfColor ?? brushDefaults.color,
              opacity: comp.lfOpacity ?? brushDefaults.opacity,
              points,
              size: comp.lfSize ?? brushDefaults.size,
            },
          };
          state.filter = temporaryFilter;

          try {
            await updateCb(state, true, true);
          } finally {
            if (originalFilter?.hasCanvasAction) {
              const existingSettings =
                originalFilter.settings ?? ({} as typeof originalFilter.settings);
              originalFilter.settings = {
                ...existingSettings,
                b64_canvas: b64Canvas,
              };
            }
            state.filter = originalFilter;
            state.filterType = originalFilterType;
            await comp.clearCanvas();
          }
          break;
      }
    },
    //#endregion
    //#region Imageviewer
    imageviewer: async (state: ImageEditorState, e: CustomEvent<LfImageviewerEventPayload>) => {
      const { comp, eventType, originalEvent } = e.detail;
      const { node } = state;

      switch (eventType) {
        case 'lf-event': {
          // Events bubbled up by imageviewer's children
          const ogEv = originalEvent as LfEvent;
          switch (ogEv.detail.eventType) {
            case 'click':
              // Check if it's a tree event
              if (isTree(ogEv.detail.comp)) {
                const treeEvent = ogEv as CustomEvent<LfTreeEventPayload>;
                const { id, node } = treeEvent.detail;

                switch (id) {
                  case 'details-tree':
                    if (node?.cells?.lfCode) {
                      prepSettings(state, node);
                    }
                    break;
                  case 'navigation-tree':
                    const isExpansion = Boolean(treeEvent.detail.expansion);
                    const metadata = extractNavigationTreeMetadata(node);

                    const hasNavigationPaths = Boolean(
                      metadata &&
                        !metadata.isPlaceholder &&
                        (metadata.isRoot ||
                          Object.values(metadata.paths ?? {}).some((value) => Boolean(value))),
                    );

                    if (hasNavigationPaths) {
                      if (isExpansion) {
                        await state.navigationTree?.handlers?.expand?.(node);
                        return;
                      }

                      await state.navigationTree?.handlers?.select?.(node);
                      return;
                    }
                    break;
                }
              }
              break;

            case 'lf-event': // Events bubbled up further
              // Check if it's a masonry event
              const masonryEvent = ogEv as CustomEvent<LfMasonryEventPayload>;
              const isMasonryEvent = isMasonry(ogEv.detail.comp);

              if (isMasonryEvent) {
                const { selectedShape } = masonryEvent.detail;

                switch (masonryEvent.detail.eventType) {
                  case 'lf-event': // Events bubbled up by masonry children
                    // Check if it's an image event
                    const subOgEv = masonryEvent.detail
                      .originalEvent as CustomEvent<LfImageEventPayload>;
                    const isImageEvent = isImage(subOgEv.detail.comp);
                    if (isImageEvent) {
                      switch (subOgEv.detail.eventType) {
                        case 'click':
                          if (!selectedShape) {
                            getLfManager().log(
                              'Masonry selection cleared.',
                              { selectedShape },
                              LogSeverity.Info,
                            );
                            return;
                          }
                          await syncSelectionWithDataset(state, masonryEvent);
                          break;
                      }
                    }
                }
                break;
              }
              break;

            case 'ready':
              const c = ogEv.detail.comp as LfCanvasElement & LfCanvasInterface;
              const isCanvas = c.rootElement.tagName.toLowerCase() === 'lf-canvas';
              if (isCanvas) {
                setBrush(c, SETTINGS.brush.settings);
              }
              break;

            case 'stroke': {
              const canvasEv = ogEv as CustomEvent<LfCanvasEventPayload>;
              await handlers.canvas(state, canvasEv);
              break;
            }
          }
          break;
        }

        case 'ready': {
          const { navigation } = await comp.getComponents();

          switch (node.comfyClass) {
            case NodeName.imagesEditingBreakpoint:
              navigation.load.lfLabel = '';
              navigation.load.lfUiState = 'disabled';
              navigation.textfield.lfLabel = 'Previews are visible in your ComfyUI/temp folder';
              navigation.textfield.lfUiState = 'disabled';
              break;
            default:
              navigation.textfield.lfLabel = 'Directory (relative to ComfyUI/input)';
              break;
          }
          break;
        }
      }
    },
    //#endregion
    //#region Slider
    slider: async (state: ImageEditorState, e: CustomEvent<LfSliderEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { preview, snapshot } = update;

      switch (eventType) {
        case 'change':
          registerManualApplyChange(state);
          snapshot();
          break;
        case 'input':
          registerManualApplyChange(state);
          const debouncedSlider = debounce(preview, 300);
          debouncedSlider();
          break;
      }
    },
    //#endregion
    //#region Textfield
    textfield: async (state: ImageEditorState, e: CustomEvent<LfTextfieldEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { preview, snapshot } = update;

      switch (eventType) {
        case 'change':
          registerManualApplyChange(state);
          snapshot();
          break;
        case 'input':
          registerManualApplyChange(state);
          const debouncedTextfield = debounce(preview, 300);
          debouncedTextfield();
          break;
      }
    },
    //#endregion
    //#region Toggle
    toggle: async (state: ImageEditorState, e: CustomEvent<LfToggleEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { snapshot } = update;

      switch (eventType) {
        case 'change':
          registerManualApplyChange(state);
          snapshot();
          break;
      }
    },
    //#endregion
  } satisfies Record<string, unknown>;

  return Object.assign(handlers, { navigation: navigationHandlers });
};
