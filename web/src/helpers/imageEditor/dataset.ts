import { LfDataColumn, LfMasonryEventPayload } from '@lf-widgets/foundations';
import {
  ImageEditorBuildSelectionPayloadParams,
  ImageEditorDataset,
  ImageEditorDatasetNavigationDirectory,
  ImageEditorDatasetSelection,
  ImageEditorState,
} from '../../types/widgets/imageEditor';
import { asString, isString } from '../../utils/common';

//#region applySelectionColumn
/**
 * Updates (or creates) the column with id 'selected' in the provided dataset and returns a new dataset object.
 *
 * The function:
 * - Ensures there is a column with id === 'selected' in dataset.columns (creates one if absent).
 * - Sets that column's title to the provided selection value (coerced to string).
 * - Produces a new columns array and returns a shallow-copied dataset with the updated columns and selection field.
 *
 * Important notes:
 * - The original dataset and its columns array are not mutated; a new dataset object and a new columns array are returned.
 * - If a 'selected' column already exists, its other properties are preserved and only its title is replaced.
 * - If dataset.columns is null/undefined or not an array, an empty columns array is created and the new 'selected' column is appended.
 *
 * @param dataset - The image editor dataset to update. May have an optional `columns` array.
 * @param selection - The selection value to set; this will be coerced to a string and stored in the selected column's title and in the returned dataset.selection.
 * @returns A new ImageEditorDataset containing the updated columns and selection.
 */
export const applySelectionColumn = (
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
//#endregion

//#region buildSelectionPayload
/**
 * Build a payload describing a dataset selection for the image editor.
 *
 * The function resolves a context identifier, constructs a selection object
 * containing at minimum the supplied index and the resolved context id, and
 * populates optional properties (name, node_id, url) when they can be derived
 * from the supplied inputs.
 *
 * Resolution logic:
 * - The context id is resolved in this order:
 *   1. dataset.context_id
 *   2. dataset.selection?.context_id
 *   3. fallbackContextId
 * - The selection.name is derived from the provided selectedShape using
 *   deriveSelectionName(), if available.
 * - If an image node is found for the given index via getImageNode(nodes, index),
 *   the node's id is read (via asString) and set as selection.node_id when present.
 * - If the image cell for that node contains a value (imageCell.value or
 *   imageCell.lfValue), it is read (via asString) and set as selection.url when present.
 *
 * Notes:
 * - Any of the optional fields (name, node_id, url) will be omitted from the
 *   returned selection if they cannot be derived.
 * - The returned contextId may be undefined if none of the resolution sources
 *   provide a value.
 *
 * @param params.dataset - The dataset object which may contain context/selection info.
 * @param params.index - The index of the image within the dataset to build the selection for.
 * @param params.nodes - The collection of nodes used to locate the image node for the index.
 * @param params.selectedShape - Shape or metadata used to derive a human-readable selection name.
 * @param params.fallbackContextId - A fallback context id to use if the dataset does not provide one.
 *
 * @returns An object containing:
 * - selection: an ImageEditorDatasetSelection with at least { index, context_id } and
 *   optionally { name, node_id, url } when derivable.
 * - contextId?: the resolved context id (same value used in selection.context_id), possibly undefined.
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

  const selectedNode = getImageNode(nodes, index);
  if (selectedNode) {
    const nodeId = asString((selectedNode as { id?: unknown }).id);
    if (nodeId) {
      selection.node_id = nodeId;
    }

    const imageCell = getImageCell(selectedNode);
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
 * Returns a directory path string extracted from an ImageEditorDatasetNavigationDirectory-like object.
 *
 * The function evaluates the provided `directory` in the following order and returns the
 * first value that passes `isString()`:
 * 1. `directory.raw`
 * 2. `directory.relative`
 * 3. `directory.resolved`
 *
 * If `directory` is `undefined` or none of the inspected properties is a string, the function
 * returns `undefined`.
 *
 * @param directory - An object that may contain path properties (`raw`, `relative`, `resolved`) or be `undefined`.
 * @returns The first string value found among `raw`, `relative`, or `resolved`, or `undefined` if no valid string is present.
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
 * Derives a human-readable name for a selected shape.
 *
 * This utility extracts a string identifier from the provided `selectedShape`
 * by checking several possible sources in a defined priority order:
 * 1. `selectedShape.shape.htmlProps.title`
 * 2. `selectedShape.shape.htmlProps.id`
 * 3. `selectedShape.shape.value`
 * 4. `selectedShape.shape.lfValue`
 *
 * Each candidate is coerced to a string (via the internal `asString` helper)
 * before being considered. The first non-null/undefined/non-empty coerced value
 * is returned. If `selectedShape` is falsy or no candidate yields a value,
 * the function returns `undefined`.
 *
 * @param selectedShape - The event payload containing the currently selected shape.
 * @returns A string representing the derived name for the selection, or `undefined`
 *          when no suitable name could be derived.
 *
 * @remarks
 * - `htmlProps` is optional on the shape and is safely handled.
 * - The function intentionally prefers `title` over `id`, then shape-local values.
 * - This is useful for labeling or identifying shapes in UI lists, tooltips, or
 *   dataset entries when multiple potential identifiers exist.
 *
 * @example
 * // Given a shape whose htmlProps.title is "Button A", the result will be "Button A".
 * // If title is absent but id is "btn-1", the result will be "btn-1".
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
 * Ensures a consistent "context id" is established between an optional dataset, its optional selection,
 * and an optional editor state. The function will attempt to resolve a single context id by the
 * following precedence:
 *   1. selection.context_id (if a selection exists)
 *   2. dataset.context_id
 *   3. state.contextId
 *
 * Side effects:
 * - May mutate dataset.selection.context_id, dataset.context_id, and state.contextId to align them
 *   with the resolved context id.
 * - If `dataset` is undefined, the function returns state?.contextId and performs no mutations.
 *
 * Behavior summary:
 * - If dataset is not provided, returns state?.contextId.
 * - If dataset.context_id exists, state.contextId is updated to that value (if state is provided).
 * - If dataset.context_id is missing but state.contextId exists, dataset.context_id is set from state.
 * - If a selection exists and a resolved context can be found, the selection.context_id is ensured,
 *   dataset.context_id is set if missing, and state.contextId is updated.
 * - If no context can be resolved from any source, undefined is returned.
 *
 * @param dataset - The dataset which may contain a context_id and an optional selection. May be undefined.
 * @param state - The editor state which may contain a contextId. May be undefined.
 * @returns The resolved context id string if one could be determined or undefined otherwise.
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
 * Safely retrieves the navigation directory from a given ImageEditorDataset.
 *
 * This function uses optional chaining to return the dataset's navigation.directory
 * when available and yields undefined if the dataset or its navigation property is missing.
 *
 * @param dataset - The ImageEditorDataset that may contain navigation information.
 * @returns The ImageEditorDatasetNavigationDirectory if present; otherwise undefined.
 */
export const getNavigationDirectory = (
  dataset: ImageEditorDataset | undefined,
): ImageEditorDatasetNavigationDirectory | undefined => {
  return dataset?.navigation?.directory;
};
//#endregion

//#region hasContextChanged
/**
 * Determines whether the context identifier has changed between two states.
 *
 * Compares `previousContextId` and `nextContextId` using strict inequality (`!==`).
 * Returns `true` if they differ (including the case where one is `undefined` and the other is a string),
 * and `false` if they are strictly equal (including both being `undefined`).
 *
 * @param previousContextId - The context id from the previous state, or `undefined` if none.
 * @param nextContextId - The context id from the next state, or `undefined` if none.
 * @returns `true` if the context id has changed; otherwise `false`.
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
 * Determines whether two ImageEditorDatasetSelection values differ.
 *
 * Performs a deep equality check by serializing both values to JSON,
 * normalizing undefined to null so that undefined and null are treated consistently.
 *
 * @param previousSelection - The previous selection, or undefined if none.
 * @param nextSelection - The next selection, or undefined if none.
 * @returns true if the serialized representations differ (i.e., the selection changed), false otherwise.
 *
 * @remarks
 * This comparison uses JSON.stringify and therefore is sensitive to:
 * - Property key order (objects with identical contents but different key order may be considered different).
 * - Non-serializable values (functions, symbols, or circular structures will be lost or may throw).
 * If a more robust deep-equality check is required, consider using a dedicated deep-equality utility.
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
 * Merges a partial navigation directory into the dataset's navigation.directory and returns the resulting directory.
 *
 * This function mutates the provided `dataset`: if `dataset.navigation` is undefined it will be created, and
 * `dataset.navigation.directory` will be replaced with a shallow-merged object that combines the existing
 * directory (if any) with the supplied `directory` partial. Properties from `directory` override existing
 * properties with the same keys.
 *
 * Note: the merge is shallow — nested objects are not deeply merged.
 *
 * @param dataset - The ImageEditorDataset to update (mutated in place).
 * @param directory - A partial ImageEditorDatasetNavigationDirectory whose properties will be merged into the existing directory.
 * @returns The updated ImageEditorDatasetNavigationDirectory now stored on `dataset.navigation.directory`.
 *
 * @example
 * // Given dataset.navigation.directory = { page: 1, pageSize: 20 }
 * // and directory = { pageSize: 50 }
 * // After calling mergeNavigationDirectory(dataset, directory):
 * // dataset.navigation.directory === { page: 1, pageSize: 50 }
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
 * Resolve the index of a selected shape within an image editor dataset.
 *
 * This function first returns an explicit numeric index if provided via
 * selectedShape.index. If no explicit index is available it attempts to
 * locate a matching node by comparing either the HTML id (shape.htmlProps.id)
 * or the cell value (shape.value or shape.lfValue) against each node's
 * corresponding image cell. Nodes that do not yield a valid image cell are
 * skipped. If a matching node is found its index is returned; otherwise
 * undefined is returned. If the provided nodes argument is not an array,
 * undefined is returned immediately.
 *
 * Matching precedence:
 * 1. Explicit numeric selectedShape.index (returned immediately).
 * 2. Match by HTML id (shape.htmlProps.id === imageCell.htmlProps.id).
 * 3. Match by value (shape.value or shape.lfValue === imageCell.value or imageCell.lfValue).
 *
 * @param selectedShape - The selected shape payload (may include an explicit index or shape metadata).
 * @param nodes - The dataset nodes to search through (expected to be ImageEditorDataset['nodes']).
 * @returns The index of the matching node within nodes, or undefined if no match or nodes is not an array.
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
    const imageCell = getImageCell(node);
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

//#region Helpers
/**
 * Retrieves the node at the specified index from an ImageEditorDataset nodes array if it exists and is an object.
 *
 * @param nodes - The nodes array from an ImageEditorDataset (may be undefined or non-array).
 * @param index - Zero-based index of the desired node.
 * @returns The node object at the given index when `nodes` is an array, the index is in range, and the element is an object; otherwise `undefined`.
 *
 * @remarks
 * - Defensive: returns `undefined` when `nodes` is not an array or index is out of bounds.
 * - Ensures the returned value is an object (filters out primitives and `null`).
 *
 * @example
 * const node = getImageNode(dataset.nodes, 2);
 * if (node) {
 *   // use node
 * }
 */
const getImageNode = (nodes: ImageEditorDataset['nodes'], index: number) => {
  if (!Array.isArray(nodes) || index < 0 || index >= nodes.length) {
    return undefined;
  }

  const candidate = nodes[index];
  return candidate && typeof candidate === 'object' ? candidate : undefined;
};
/**
 * Retrieves the "lfImage" cell object from a node-like object.
 *
 * This function performs a safe extraction:
 * - If the provided `node` is null, undefined, or not an object, the function returns `undefined`.
 * - If `node` is an object but does not contain a `cells` property or the `cells.lfImage`
 *   entry is missing, the function returns an empty object typed as the expected image cell shape.
 *
 * The returned object (when not `undefined`) may contain these optional properties:
 * - `htmlProps?: Record<string, unknown>` — HTML-related props for rendering the image.
 * - `value?: unknown` — a stored value associated with the cell.
 * - `lfValue?: unknown` — a library/framework-specific value for the cell.
 *
 * Note: The function makes no assumptions about the internal types of those properties beyond
 * `unknown`; callers should perform appropriate type-narrowing before using them. The input
 * object is not mutated.
 *
 * @param node - Any value expected to be a node-like object that may contain a `cells` map.
 * @returns The `lfImage` cell object (possibly empty) when `node` is an object, or `undefined`
 *          when `node` is null/undefined or not an object.
 */
const getImageCell = (node: unknown) => {
  if (!node || typeof node !== 'object') {
    return undefined;
  }

  const cells = (node as { cells?: Record<string, unknown> }).cells ?? {};
  const imageCell = (cells?.lfImage ?? {}) as {
    htmlProps?: Record<string, unknown>;
    value?: unknown;
    lfValue?: unknown;
  };

  return imageCell;
};
//#endregion
