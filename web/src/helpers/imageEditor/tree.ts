import { LfDataDataset, LfDataNode } from '@lf-widgets/foundations';
import {
  ImageEditorNavigationTreeMetadata,
  ImageEditorNavigationTreeMetadataPaths,
} from '../../types/widgets/imageEditor';
import { getLfManager } from '../../utils/common';

const getLfData = () => {
  const lfData = getLfManager()?.getManagers()?.lfFramework?.data;
  if (!lfData) {
    throw new Error('LF Framework data module is unavailable.');
  }
  return lfData;
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
    };
  } catch (error) {
    return undefined;
  }
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

  const parentNode = getLfData().node.find(dataset, (node) => node.id === parentId);
  parentNode.children = [...((Array.isArray(branch.nodes) ? branch.nodes : undefined) ?? [])];
  return dataset;
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
