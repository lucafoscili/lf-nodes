import {
  LfButtonEventPayload,
  LfCanvasElement,
  LfCanvasEventPayload,
  LfCanvasInterface,
  LfCheckboxEventPayload,
  LfEvent,
  LfImageEventPayload,
  LfImageviewerEventPayload,
  LfMasonryEventPayload,
  LfMasonryInterface,
  LfMultiInputEventPayload,
  LfSelectEventPayload,
  LfSliderEventPayload,
  LfTextfieldEventPayload,
  LfToggleEventPayload,
  LfTreeEventPayload,
} from '@lf-widgets/foundations';
import { SETTINGS } from '../../fixtures/imageEditor/settings';
import { LogSeverity } from '../../types/manager/manager';
import {
  EventHandlerDeps,
  ImageEditorBrushFilter,
  ImageEditorDataset,
  ImageEditorIcons,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { NodeName } from '../../types/widgets/widgets';
import {
  canvasToBase64,
  debounce,
  getApiRoutes,
  getComfyAPI,
  getLfManager,
  isImage,
  isMasonry,
  isTree,
  LFInterruptFlags,
} from '../../utils/common';
import { IMAGE_EDITOR_CONSTANTS } from './constants';
import {
  applySelectionColumn,
  buildSelectionPayload,
  ensureDatasetContext,
  hasContextChanged,
  hasSelectionChanged,
  resolveSelectionIndex,
} from './dataset';
import { setBrush, updateResizeHelperText } from './settings';
import { updateCb } from './update';

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

  const handlers = {
    //#region Button
    button: async (state: ImageEditorState, e: CustomEvent<LfButtonEventPayload>) => {
      const { comp, eventType } = e.detail;

      if (eventType === IMAGE_EDITOR_CONSTANTS.EVENTS.CLICK) {
        const isPatched = getComfyAPI()[LFInterruptFlags.PatchedInterrupt] === true;

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
        case IMAGE_EDITOR_CONSTANTS.EVENTS.STROKE:
          const originalFilter = filter;
          const originalFilterType = filterType;
          const canvas = await comp.getCanvas();
          const b64Canvas = canvasToBase64(canvas);
          if (filterType !== IMAGE_EDITOR_CONSTANTS.FILTERS.BRUSH && !filter?.hasCanvasAction) {
            state.filterType = IMAGE_EDITOR_CONSTANTS.FILTERS.BRUSH;
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
    //#region Checkbox
    checkbox: async (state: ImageEditorState, e: CustomEvent<LfCheckboxEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { snapshot } = update;

      switch (eventType) {
        case 'change':
          snapshot();
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
          // Events bubbled up
          const ogEv = originalEvent as LfEvent;

          if (isTree(ogEv.detail.comp)) {
            // Check if it's a tree event
            const treeEvent = ogEv as CustomEvent<LfTreeEventPayload>;
            const { id, node: treeNode, eventType } = treeEvent.detail;

            switch (id) {
              case 'details-tree':
                if (treeNode?.cells?.lfCode && eventType === 'click') {
                  prepSettings(state, treeNode);
                }
                break;

              case 'navigation-tree':
                if (!state.navigationManager || !treeNode || eventType !== 'click') {
                  break;
                }

                await state.navigationManager.handleTreeClick(treeNode);

                const needsLazyLoad = !treeNode.children || treeNode.children.length === 0;
                if (needsLazyLoad) {
                  await state.navigationManager.expandNode(treeNode);
                }

                break;
            }
          }

          switch (ogEv.detail.eventType) {
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
                        case 'load':
                          if (
                            state.filterType === 'resizeEdge' ||
                            state.filterType === 'resizeFree'
                          ) {
                            updateResizeHelperText(state);
                          }
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
                const brushSettings = state?.lastBrushSettings ?? SETTINGS.brush.settings;
                setBrush(c, brushSettings);
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
    //#region Multiinput
    multiinput: async (state: ImageEditorState, e: CustomEvent<LfMultiInputEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { preview, snapshot } = update;

      switch (eventType) {
        case 'change':
          snapshot();
          break;
        case 'input':
          const debouncedMultiinput = debounce(preview, 300);
          debouncedMultiinput();
          break;
      }
    },
    //#endregion
    //#region Select
    select: async (state: ImageEditorState, e: CustomEvent<LfSelectEventPayload>) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { snapshot } = update;

      switch (eventType) {
        case 'change':
          snapshot();
          break;
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
          snapshot();
          break;
        case 'input':
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
          snapshot();
          break;
        case 'input':
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
          snapshot();
          break;
      }
    },
    //#endregion
  } satisfies Record<string, unknown>;

  return handlers;
};
