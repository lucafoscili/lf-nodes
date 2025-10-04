import { LfDataDataset, LfDataNode, LfDataNodePlaceholderOptions } from '@lf-widgets/foundations';
import {
  ImageEditorNavigationTreeMetadata,
  ImageEditorNavigationTreeMetadataPaths,
} from '../../types/widgets/imageEditor';
import { getLfManager } from '../../utils/common';

export const NAVIGATION_TREE_PLACEHOLDER_SUFFIX = '__lf_placeholder';
const getLfData = () => {
  const lfData = getLfManager()?.getManagers()?.lfFramework?.data;
  if (!lfData) {
    throw new Error('LF Framework data module is unavailable.');
  }
  return lfData;
};

const createPlaceholderNode = (parent: LfDataNode): LfDataNode => {
  const parentMetadata = extractNavigationTreeMetadata(parent);
  const parentId = parentMetadata?.id ?? String(parent.id ?? '');
  const placeholderId = `${parentId}${NAVIGATION_TREE_PLACEHOLDER_SUFFIX}`;
  const metadata: ImageEditorNavigationTreeMetadata = {
    id: placeholderId,
    name: 'Loading…',
    hasChildren: false,
    parentId,
    paths: parentMetadata?.paths ?? {},
    isPlaceholder: true,
    imageCount: undefined,
    isRoot: false,
  };

  return {
    id: placeholderId,
    value: 'Loading…',
    cells: {
      name: {
        shape: 'text',
        value: 'Loading…',
      },
      items: {
        shape: 'text',
        value: '',
      },
      type: {
        shape: 'text',
        value: '',
      },
      lfCode: {
        shape: 'code',
        value: JSON.stringify({ ...metadata, isPlaceholder: true }),
      },
    },
    children: [],
  };
};

const isPlaceholderNode = (node: LfDataNode | undefined): boolean => {
  if (!node) {
    return false;
  }

  if (typeof node.id === 'string' && node.id.endsWith(NAVIGATION_TREE_PLACEHOLDER_SUFFIX)) {
    return true;
  }

  const metadata = extractNavigationTreeMetadata(node);
  if (!metadata) {
    return false;
  }

  if (metadata.isPlaceholder) {
    return true;
  }

  if (metadata.name !== 'Loading…') {
    return false;
  }

  const pathValues = Object.values(metadata.paths ?? {}).filter(Boolean);
  return pathValues.length === 0;
};

export const NAVIGATION_TREE_PLACEHOLDER_CONFIG: LfDataNodePlaceholderOptions = {
  create: ({ parent }) => createPlaceholderNode(parent),
  isPlaceholder: (node) => isPlaceholderNode(node),
  shouldDecorate: (node) => {
    const metadata = extractNavigationTreeMetadata(node);
    if (metadata?.isPlaceholder) {
      return false;
    }
    if (metadata && metadata.hasChildren !== undefined) {
      return metadata.hasChildren;
    }
    return node.hasChildren === true;
  },
};

export const extractNavigationTreeMetadata = (
  node: LfDataNode | undefined,
): ImageEditorNavigationTreeMetadata | undefined => {
  if (!node) {
    return undefined;
  }

  const rawValue = (node.cells?.lfCode as { value?: unknown } | undefined)?.value;
  if (typeof rawValue !== 'string') {
    return undefined;
  }

  try {
    const parsed = JSON.parse(rawValue) as Partial<
      ImageEditorNavigationTreeMetadata & {
        paths?: ImageEditorNavigationTreeMetadataPaths;
        isPlaceholder?: boolean;
      }
    >;

    if (!parsed || typeof parsed !== 'object') {
      return undefined;
    }

    return {
      id: parsed.id ?? String(node.id ?? ''),
      name: parsed.name ?? String(node.value ?? ''),
      hasChildren: Boolean(parsed.hasChildren),
      imageCount: parsed.imageCount,
      parentId: parsed.parentId ?? null,
      isRoot: Boolean(parsed.isRoot),
      paths: parsed.paths ?? {},
      isPlaceholder: Boolean(parsed.isPlaceholder),
    };
  } catch (error) {
    return undefined;
  }
};

export const prepareNavigationTreeDataset = <
  T extends (LfDataDataset & { parent_id?: string }) | undefined,
>(
  dataset: T,
): T => {
  if (!dataset) {
    return dataset;
  }

  return getLfData().node.decoratePlaceholders(dataset, NAVIGATION_TREE_PLACEHOLDER_CONFIG);
};

export const mergeNavigationTreeChildren = (
  dataset: (LfDataDataset & { parent_id?: string }) | undefined,
  branch: (LfDataDataset & { parent_id?: string }) | undefined,
): (LfDataDataset & { parent_id?: string }) | undefined => {
  if (!dataset || !branch) {
    return dataset;
  }

  const parentId = branch.parent_id;
  if (!parentId) {
    return dataset;
  }

  const merged = getLfData().node.mergeChildren(dataset, {
    parentId,
    children: (Array.isArray(branch.nodes) ? branch.nodes : undefined) as LfDataNode[] | undefined,
    columns: branch.columns,
    placeholder: {
      removeExisting: true,
      reapply: true,
      config: NAVIGATION_TREE_PLACEHOLDER_CONFIG,
    },
  });
  return merged as typeof dataset;
};

export const findNodeInNavigationTree = (
  dataset: (LfDataDataset & { parent_id?: string }) | undefined,
  predicate: (node: LfDataNode) => boolean,
): LfDataNode | undefined => {
  if (!dataset || !Array.isArray(dataset.nodes) || typeof predicate !== 'function') {
    return undefined;
  }

  return getLfData().node.find(dataset, predicate);
};
