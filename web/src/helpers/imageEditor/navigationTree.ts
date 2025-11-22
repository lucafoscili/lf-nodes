import { LfDataNode } from '@lf-widgets/foundations';
import { IMAGE_API } from '../../api/image';
import { LogSeverity } from '../../types/manager/manager';
import { ImageEditorState, NavigationMetadata } from '../../types/widgets/imageEditor';
import { getLfData, getLfManager, normalizeDirectoryRequest } from '../../utils/common';
import { deriveDirectoryValue } from './dataset';

//#region extractMetadata
const extractMetadata = (node: LfDataNode): NavigationMetadata | null => {
  const lfData = getLfData();

  const metadata = lfData.node.extractCellMetadata<NavigationMetadata>(node, 'lfCode', {
    validate: (val): val is NavigationMetadata => {
      if (typeof val === 'string') {
        try {
          val = JSON.parse(val);
        } catch {
          return false;
        }
      }
      if (typeof val !== 'object' || val === null) {
        return false;
      }
      return 'id' in val || 'name' in val || 'paths' in val;
    },
    transform: (val) => {
      let parsed = val;
      if (typeof val === 'string') {
        try {
          parsed = JSON.parse(val);
        } catch {
          parsed = val;
        }
      }

      return {
        id: parsed.id ?? String(node.id ?? ''),
        name: parsed.name ?? String(node.value ?? ''),
        hasChildren: Boolean(parsed.hasChildren),
        paths: parsed.paths ?? {},
        isRoot: parsed.isRoot,
      };
    },
  });

  return metadata ?? null;
};
//#endregion

//#region createNavigationTreeManager
export const createNavigationTreeManager = (
  imageviewer: HTMLLfImageviewerElement,
  editorState: ImageEditorState,
) => {
  const _getDirectoryPath = (metadata: NavigationMetadata): string => {
    return (
      metadata.paths.resolved ??
      metadata.paths.raw ??
      metadata.paths.relative ??
      metadata.name ??
      ''
    );
  };

  const loadRoots = async () => {
    try {
      const response = await IMAGE_API.explore('', { scope: 'roots' });
      if (response.status === LogSeverity.Success && response.data?.tree) {
        imageviewer.lfNavigation = {
          isTreeOpen: false,
          treeProps: {
            lfAccordionLayout: true,
            lfDataset: response.data.tree ?? { columns: [], nodes: [] },
            lfFilter: true,
            lfGrid: true,
            lfSelectable: true,
          },
        };
      }
    } catch (error) {
      getLfManager().log('Failed to load navigation roots.', { error }, LogSeverity.Warning);
    }
  };

  const expandNode = async (node: LfDataNode) => {
    const metadata = extractMetadata(node);
    if (!metadata?.hasChildren) {
      return;
    }

    const nodeId = metadata.id;

    const path = normalizeDirectoryRequest(_getDirectoryPath(metadata));
    if (!path) {
      return;
    }

    try {
      const response = await IMAGE_API.explore(path, { scope: 'tree', nodePath: path });
      if (response.status === LogSeverity.Success && response.data?.tree) {
        const { navigation } = await imageviewer.getComponents();
        const branch = response.data.tree;
        if (!Array.isArray(branch.nodes)) {
          return;
        }

        const currentDataset = imageviewer.lfNavigation?.treeProps?.lfDataset;
        if (!currentDataset) {
          return;
        }

        const lfData = getLfData();
        if (!lfData) {
          return;
        }

        const parentNode = lfData.node.find(currentDataset, (n) => n.id === nodeId);
        if (!parentNode) {
          return;
        }

        parentNode.children = branch.nodes;
        const parentId = parentNode.id;

        navigation.tree.lfExpandedNodeIds =
          Array.isArray(navigation.tree.lfExpandedNodeIds) &&
          !navigation.tree.lfExpandedNodeIds.includes(parentId)
            ? [...navigation.tree.lfExpandedNodeIds, parentId]
            : [parentId];
      }
    } catch (error) {
      getLfManager().log('Failed to expand node.', { error, nodeId, path }, LogSeverity.Warning);
    }
  };
  //#endregion

  //#region handleTreeClick
  const handleTreeClick = async (node: LfDataNode) => {
    const metadata = extractMetadata(node);
    if (!metadata) {
      return;
    }

    const targetPath = normalizeDirectoryRequest(_getDirectoryPath(metadata));
    const currentPath = normalizeDirectoryRequest(
      editorState.directoryValue ?? deriveDirectoryValue(editorState.directory) ?? '',
    );

    if (targetPath === currentPath && !metadata.isRoot) {
      return;
    }

    await editorState.refreshDirectory?.(targetPath);
  };
  //#endregion

  return {
    loadRoots,
    expandNode,
    handleTreeClick,
  };
};
