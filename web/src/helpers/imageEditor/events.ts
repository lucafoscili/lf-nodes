import {
  LfButtonEventPayload,
  LfCanvasElement,
  LfCanvasEventPayload,
  LfCanvasInterface,
  LfDataColumn,
  LfEvent,
  LfImageviewerEventPayload,
  LfMasonryEventPayload,
  LfMasonryInterface,
  LfSliderEventPayload,
  LfTextfieldEventPayload,
  LfToggleEventPayload,
  LfTreeEventPayload,
} from '@lf-widgets/foundations';
import { SETTINGS } from '../../fixtures/imageEditor';
import { LogSeverity } from '../../types/manager/manager';
import {
  EventHandlerDeps,
  ImageEditorBrushFilter,
  ImageEditorDataset,
  ImageEditorDatasetSelection,
  ImageEditorIcons,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { NodeName } from '../../types/widgets/widgets';
import {
  canvasToBase64,
  debounce,
  getApiRoutes,
  getLfManager,
  isMasonry,
  isTree,
  LFInterruptFlags,
} from '../../utils/common';
import { registerManualApplyChange } from './manualApply';
import { setBrush } from './settings';
import { updateCb } from './update';
/// @ts-ignore
import { api } from '/scripts/api.js';

export const createEventHandlers = ({
  handleInterruptForState,
  prepSettings,
}: EventHandlerDeps) => {
  const resolveComponentTag = (comp: unknown) => {
    const root = (comp as { rootElement?: Element })?.rootElement;
    return typeof root?.tagName === 'string' ? root.tagName.toLowerCase() : '';
  };

  const updateDatasetSelection = (
    dataset: ImageEditorDataset,
    selection: ImageEditorDatasetSelection,
  ): ImageEditorDataset => {
    const nextColumns: LfDataColumn[] = Array.isArray(dataset?.columns) ? [...dataset.columns] : [];

    const selectedColumnIndex = nextColumns.findIndex((column) => column?.id === 'selected');

    const selectionColumn = (
      selectedColumnIndex >= 0 ? nextColumns[selectedColumnIndex] : { id: 'selected' }
    ) as LfDataColumn;

    const coercedSelectionColumn = {
      ...selectionColumn,
      title: selection as unknown as string,
    } as unknown as LfDataColumn;

    if (selectedColumnIndex >= 0) {
      nextColumns[selectedColumnIndex] = coercedSelectionColumn;
    } else {
      nextColumns.push(coercedSelectionColumn);
    }

    return {
      ...dataset,
      columns: nextColumns,
      selection,
    };
  };

  const resolveSelectionName = (selectedShape: LfMasonryEventPayload['selectedShape']) => {
    if (!selectedShape) {
      return undefined;
    }

    const shape = selectedShape.shape as
      | (LfMasonryEventPayload['selectedShape']['shape'] & {
          htmlProps?: Record<string, unknown>;
          lfValue?: unknown;
        })
      | undefined;

    const htmlProps = shape?.htmlProps ?? {};
    const htmlTitle =
      htmlProps && typeof htmlProps['title'] === 'string' ? htmlProps['title'] : undefined;
    const htmlId = htmlProps && typeof htmlProps['id'] === 'string' ? htmlProps['id'] : undefined;
    const shapeValue =
      shape && typeof (shape as { value?: unknown }).value === 'string'
        ? (shape as { value?: string }).value
        : undefined;
    const lfValue = typeof shape?.lfValue === 'string' ? (shape.lfValue as string) : undefined;

    return htmlTitle ?? htmlId ?? shapeValue ?? lfValue ?? undefined;
  };

  const syncSelectionWithDataset = async (
    state: ImageEditorState,
    masonryEvent: CustomEvent<LfMasonryEventPayload>,
  ) => {
    const { elements } = state;
    const dataset = (elements.imageviewer.lfDataset || {}) as ImageEditorDataset;
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
    let selectionIndex = typeof selectedShape?.index === 'number' ? selectedShape.index : undefined;

    if (typeof selectionIndex !== 'number') {
      const shape = selectedShape?.shape as
        | ({
            htmlProps?: Record<string, unknown>;
            lfValue?: unknown;
            value?: unknown;
          } & Record<string, unknown>)
        | undefined;

      const shapeId =
        shape?.htmlProps && typeof shape.htmlProps['id'] === 'string'
          ? (shape.htmlProps['id'] as string)
          : undefined;
      const shapeValue =
        typeof shape?.value === 'string'
          ? (shape.value as string)
          : typeof shape?.lfValue === 'string'
          ? (shape.lfValue as string)
          : undefined;

      const resolvedIndex = nodes.findIndex((node) => {
        const cell = (node?.cells?.lfImage ?? {}) as {
          htmlProps?: Record<string, unknown>;
          value?: unknown;
          lfValue?: unknown;
        };
        const htmlProps = cell?.htmlProps ?? {};
        const cellId =
          typeof htmlProps['id'] === 'string' ? (htmlProps['id'] as string) : undefined;
        const cellValue =
          typeof cell?.value === 'string'
            ? (cell.value as string)
            : typeof cell?.lfValue === 'string'
            ? (cell.lfValue as string)
            : undefined;

        if (shapeId && cellId === shapeId) {
          return true;
        }

        if (shapeValue && cellValue === shapeValue) {
          return true;
        }

        return false;
      });

      selectionIndex = resolvedIndex >= 0 ? resolvedIndex : undefined;
    }

    if (typeof selectionIndex !== 'number') {
      getLfManager().log(
        'Unable to resolve selected masonry index.',
        { selectedShape },
        LogSeverity.Warning,
      );
      return;
    }

    const previousSelection = dataset.selection;

    const resolvedContextId =
      dataset.context_id ?? dataset.selection?.context_id ?? state.contextId;

    const baseSelection: ImageEditorDatasetSelection = {
      index: selectionIndex,
      context_id: resolvedContextId,
    };

    const derivedName = resolveSelectionName(selectedShape);
    if (derivedName) {
      baseSelection.name = derivedName;
    }

    if (resolvedContextId) {
      state.contextId = resolvedContextId;
    }

    const selectedNode = nodes?.[selectionIndex];
    const imageCell = (selectedNode?.cells?.lfImage ?? {}) as {
      htmlProps?: Record<string, unknown>;
      value?: unknown;
      lfValue?: unknown;
    };
    const imageValue =
      typeof imageCell?.value === 'string'
        ? (imageCell.value as string)
        : typeof imageCell?.lfValue === 'string'
        ? (imageCell.lfValue as string)
        : undefined;

    if (selectedNode?.id) {
      baseSelection.node_id = selectedNode.id;
    }

    if (imageValue) {
      baseSelection.url = imageValue;
    }

    const nextDataset = updateDatasetSelection(
      {
        ...dataset,
        context_id: dataset.context_id ?? resolvedContextId,
        selection: dataset.selection ?? undefined,
      },
      baseSelection,
    );

    if (resolvedContextId && nextDataset.selection) {
      nextDataset.selection.context_id = resolvedContextId;
    }

    elements.imageviewer.lfDataset = nextDataset;

    if (!resolvedContextId) {
      return;
    }

    const selectionChanged =
      JSON.stringify(previousSelection ?? null) !== JSON.stringify(nextDataset.selection ?? null);
    const contextChanged = dataset.context_id !== nextDataset.context_id;

    if (!selectionChanged && !contextChanged) {
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
          const ogEv = originalEvent as LfEvent;
          switch (ogEv.detail.eventType) {
            case 'click':
              if (isTree(ogEv.detail.comp)) {
                const { node } = ogEv.detail as LfTreeEventPayload;
                if (node.cells?.lfCode) {
                  prepSettings(state, node);
                }
              }
              break;

            case 'lf-event':
              const masonryEvent = ogEv as CustomEvent<LfMasonryEventPayload>;
              if (isMasonry(ogEv.detail.comp)) {
                const { selectedShape } = masonryEvent.detail;
                if (!selectedShape) {
                  getLfManager().log(
                    'Masonry selection cleared.',
                    { selectedShape },
                    LogSeverity.Info,
                  );
                  return;
                }
                await syncSelectionWithDataset(state, masonryEvent);
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

  return handlers;
};
