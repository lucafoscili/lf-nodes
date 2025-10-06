import { LfDataColumn, LfMasonryEventPayload } from '@lf-widgets/foundations';
import {
  ImageEditorBuildSelectionPayloadParams,
  ImageEditorDataset,
  ImageEditorDatasetNavigationDirectory,
  ImageEditorDatasetSelection,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { asString, getLfManager, isString } from '../../utils/common';

//#region applySelectionColumn
/**
 * Updates dataset with a 'selected' column containing the selection value.
 * Mutates dataset.columns and dataset.selection.
 */
export const applySelectionColumn = (
  dataset: ImageEditorDataset,
  selection: ImageEditorDatasetSelection,
): ImageEditorDataset => {
  const lfData = getLfManager()?.getManagers()?.lfFramework?.data;
  const existingColumns = Array.isArray(dataset?.columns) ? dataset.columns : [];

  const [existingSelectionColumn] = lfData
    ? lfData.column.find(existingColumns, { id: 'selected' })
    : [];

  const updatedSelectionColumn = {
    ...(existingSelectionColumn ?? { id: 'selected' }),
    title: selection as unknown as string,
  } as unknown as LfDataColumn;

  const nextColumns = existingSelectionColumn
    ? existingColumns.map((col) => (col.id === 'selected' ? updatedSelectionColumn : col))
    : [...existingColumns, updatedSelectionColumn];

  return {
    ...dataset,
    columns: nextColumns,
    selection,
  };
};
//#endregion

//#region buildSelectionPayload
/**
 * Builds a selection payload with index, context_id, and optional name/node_id/url
 * derived from the dataset, selectedShape, and nodes.
 */
export const buildSelectionPayload = ({
  dataset,
  index,
  nodes,
  selectedShape,
  fallbackContextId,
}: ImageEditorBuildSelectionPayloadParams): {
  selection: ImageEditorDatasetSelection;
  contextId?: string;
} => {
  const resolvedContextId =
    dataset.context_id ?? dataset.selection?.context_id ?? fallbackContextId;
  const selection: ImageEditorDatasetSelection = {
    index,
    context_id: resolvedContextId,
  };

  const derivedName = deriveSelectionName(selectedShape);
  if (derivedName) {
    selection.name = derivedName;
  }

  const selectedNode =
    Array.isArray(nodes) && index >= 0 && index < nodes.length && nodes[index]
      ? nodes[index]
      : undefined;

  if (selectedNode && typeof selectedNode === 'object') {
    const nodeId = asString((selectedNode as { id?: unknown }).id);
    if (nodeId) {
      selection.node_id = nodeId;
    }

    const imageCell = selectedNode.cells?.lfImage;
    const imageValue = asString(imageCell?.value) ?? asString(imageCell?.lfValue);
    if (imageValue) {
      selection.url = imageValue;
    }
  }

  return { selection, contextId: resolvedContextId };
};
//#endregion

//#region deriveDirectoryValue
/**
 * Extracts directory path from directory object, checking raw → relative → resolved in order.
 */
export const deriveDirectoryValue = (
  directory: ImageEditorDatasetNavigationDirectory | undefined,
): string | undefined => {
  if (!directory) {
    return undefined;
  }

  if (isString(directory.raw)) {
    return directory.raw;
  }

  if (isString(directory.relative)) {
    return directory.relative;
  }

  if (isString(directory.resolved)) {
    return directory.resolved;
  }

  return undefined;
};
//#endregion

//#region deriveSelectionName
/**
 * Derives a human-readable name from selectedShape, checking title → id → value → lfValue in order.
 */
export const deriveSelectionName = (
  selectedShape: LfMasonryEventPayload['selectedShape'],
): string | undefined => {
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
  const htmlTitle = asString(htmlProps['title']);
  const htmlId = asString(htmlProps['id']);
  const shapeValue = asString((shape as { value?: unknown })?.value);
  const lfValue = asString(shape?.lfValue);

  return htmlTitle ?? htmlId ?? shapeValue ?? lfValue ?? undefined;
};
//#endregion

//#region ensureDatasetContext
/**
 * Resolves and syncs context_id between dataset, selection, and state.
 * Mutates all three to align with the resolved context.
 */
export const ensureDatasetContext = (
  dataset: ImageEditorDataset | undefined,
  state: ImageEditorState | undefined,
): string | undefined => {
  if (!dataset) {
    return state?.contextId;
  }

  const setStateContext = (contextId?: string) => {
    if (contextId && state) {
      state.contextId = contextId;
    }
  };

  if (dataset.context_id) {
    setStateContext(dataset.context_id);
  } else if (state?.contextId) {
    dataset.context_id = state.contextId;
  }

  const selection = dataset.selection;
  const resolvedContext = selection?.context_id ?? dataset.context_id ?? state?.contextId;

  if (selection && resolvedContext) {
    selection.context_id = selection.context_id ?? resolvedContext;
    if (!dataset.context_id) {
      dataset.context_id = resolvedContext;
    }
    setStateContext(resolvedContext);
    return resolvedContext;
  }

  if (dataset.context_id) {
    setStateContext(dataset.context_id);
    return dataset.context_id;
  }

  if (state?.contextId) {
    dataset.context_id = state.contextId;
    return state.contextId;
  }

  return undefined;
};
//#endregion

//#region getNavigationDirectory
/**
 * Returns dataset.navigation.directory or undefined.
 */
export const getNavigationDirectory = (
  dataset: ImageEditorDataset | undefined,
): ImageEditorDatasetNavigationDirectory | undefined => {
  return dataset?.navigation?.directory;
};
//#endregion

//#region hasContextChanged
/**
 * Checks if context_id has changed between two states using strict inequality.
 */
export const hasContextChanged = (
  previousContextId: string | undefined,
  nextContextId: string | undefined,
) => {
  return previousContextId !== nextContextId;
};
//#endregion

//#region hasSelectionChanged
/**
 * Checks if selection has changed using JSON serialization comparison.
 * Note: Sensitive to property key order.
 */
export const hasSelectionChanged = (
  previousSelection: ImageEditorDatasetSelection | undefined,
  nextSelection: ImageEditorDatasetSelection | undefined,
) => {
  return JSON.stringify(previousSelection ?? null) !== JSON.stringify(nextSelection ?? null);
};
//#endregion

//#region mergeNavigationDirectory
/**
 * Shallow-merges directory partial into dataset.navigation.directory.
 * Mutates dataset.navigation.
 */
export const mergeNavigationDirectory = (
  dataset: ImageEditorDataset,
  directory: Partial<ImageEditorDatasetNavigationDirectory>,
): ImageEditorDatasetNavigationDirectory => {
  const current = dataset.navigation?.directory ?? {};
  const next = {
    ...current,
    ...directory,
  } satisfies ImageEditorDatasetNavigationDirectory;

  dataset.navigation = dataset.navigation ?? {};
  dataset.navigation.directory = next;

  return next;
};
//#endregion

//#region resolveSelectionIndex
/**
 * Resolves the index of a selected shape by checking explicit index → HTML id → cell value.
 */
export const resolveSelectionIndex = (
  selectedShape: LfMasonryEventPayload['selectedShape'],
  nodes: ImageEditorDataset['nodes'],
): number | undefined => {
  if (typeof selectedShape?.index === 'number') {
    return selectedShape.index;
  }

  if (!Array.isArray(nodes)) {
    return undefined;
  }

  const shape = selectedShape?.shape as
    | ({
        htmlProps?: Record<string, unknown>;
        lfValue?: unknown;
        value?: unknown;
      } & Record<string, unknown>)
    | undefined;

  const shapeId = asString(shape?.htmlProps?.['id']);
  const shapeValue = asString(shape?.value) ?? asString(shape?.lfValue);

  const resolvedIndex = nodes.findIndex((node) => {
    if (!node || typeof node !== 'object') {
      return false;
    }

    const imageCell = node.cells?.lfImage;
    if (!imageCell) {
      return false;
    }

    const cellId = asString(imageCell.htmlProps?.['id']);
    const cellValue = asString(imageCell.value) ?? asString(imageCell.lfValue);

    if (shapeId && cellId === shapeId) {
      return true;
    }

    if (shapeValue && cellValue === shapeValue) {
      return true;
    }

    return false;
  });

  return resolvedIndex >= 0 ? resolvedIndex : undefined;
};
//#endregion
