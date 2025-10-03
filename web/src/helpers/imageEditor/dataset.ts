import { LfDataColumn, LfMasonryEventPayload } from '@lf-widgets/foundations';
import {
  ImageEditorDataset,
  ImageEditorDatasetSelection,
  ImageEditorState,
} from '../../types/widgets/imageEditor';

const asString = (value: unknown): string | undefined =>
  typeof value === 'string' ? value : undefined;

const getImageNode = (nodes: ImageEditorDataset['nodes'], index: number) => {
  if (!Array.isArray(nodes) || index < 0 || index >= nodes.length) {
    return undefined;
  }

  const candidate = nodes[index];
  return candidate && typeof candidate === 'object' ? candidate : undefined;
};

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

interface BuildSelectionPayloadParams {
  dataset: ImageEditorDataset;
  index: number;
  nodes: ImageEditorDataset['nodes'];
  selectedShape?: LfMasonryEventPayload['selectedShape'];
  fallbackContextId?: string;
}

export const buildSelectionPayload = ({
  dataset,
  index,
  nodes,
  selectedShape,
  fallbackContextId,
}: BuildSelectionPayloadParams): {
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

export const hasSelectionChanged = (
  previousSelection: ImageEditorDatasetSelection | undefined,
  nextSelection: ImageEditorDatasetSelection | undefined,
) => {
  return JSON.stringify(previousSelection ?? null) !== JSON.stringify(nextSelection ?? null);
};

export const hasContextChanged = (
  previousContextId: string | undefined,
  nextContextId: string | undefined,
) => {
  return previousContextId !== nextContextId;
};

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
