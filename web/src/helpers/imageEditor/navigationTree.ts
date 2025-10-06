import { LfDataDataset, LfDataNode } from '@lf-widgets/foundations';
import { IMAGE_API } from '../../api/image';
import { LogSeverity } from '../../types/manager/manager';
import { ImageEditorState } from '../../types/widgets/imageEditor';
import { getLfManager, normalizeDirectoryRequest } from '../../utils/common';
import { deriveDirectoryValue } from './dataset';

interface NavigationMetadata {
  id: string;
  name: string;
  hasChildren: boolean;
  paths: {
    raw?: string;
    relative?: string;
    resolved?: string;
  };
  isRoot?: boolean;
}

const getLfData = () => getLfManager()?.getManagers()?.lfFramework?.data;

const extractMetadata = (node: LfDataNode): NavigationMetadata | null => {
  const lfData = getLfData();
  if (!lfData) return null;

  const metadata = lfData.node.extractCellMetadata<NavigationMetadata>(node, 'lfCode', {
    validate: (val): val is NavigationMetadata => {
      if (typeof val === 'string') {
        try {
          val = JSON.parse(val);
        } catch {
          return false;
        }
      }
      if (typeof val !== 'object' || val === null) return false;
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

const getDirectoryPath = (metadata: NavigationMetadata): string => {
  return (
    metadata.paths.resolved ?? metadata.paths.raw ?? metadata.paths.relative ?? metadata.name ?? ''
  );
};

export const createNavigationTreeManager = (
  imageviewer: HTMLLfImageviewerElement,
  editorState: ImageEditorState,
) => {
  const loadRoots = async () => {
    try {
      const response = await IMAGE_API.explore('', { scope: 'roots' });
      if (response.status === LogSeverity.Success && response.data?.tree) {
        // Update tree props directly
        if (imageviewer.lfNavigation?.treeProps) {
          imageviewer.lfNavigation.treeProps.lfDataset = response.data.tree ?? {
            columns: response.data.tree?.columns ?? [],
            nodes: [],
          };
        }
      }
    } catch (error) {
      getLfManager().log('Failed to load navigation roots.', { error }, LogSeverity.Warning);
    }
  };

  const expandNode = async (node: LfDataNode) => {
    const metadata = extractMetadata(node);
    if (!metadata?.hasChildren) return;

    const nodeId = metadata.id;
    const path = normalizeDirectoryRequest(getDirectoryPath(metadata));
    if (!path) return;

    try {
      const response = await IMAGE_API.explore(path, { scope: 'tree', nodePath: path });
      if (response.status === LogSeverity.Success && response.data?.tree) {
        const branch = response.data.tree;
        if (!Array.isArray(branch.nodes)) return;

        const currentDataset = imageviewer.lfNavigation?.treeProps?.lfDataset;
        if (!currentDataset) return;

        const lfData = getLfData();
        if (!lfData) return;

        const parentNode = lfData.node.find(currentDataset, (n) => n.id === nodeId);
        if (!parentNode) return;

        // Update parent's children and trigger reactivity
        parentNode.children = branch.nodes;
        imageviewer.lfNavigation.treeProps.lfDataset = {
          ...currentDataset,
          columns: branch.columns ?? currentDataset.columns,
          nodes: [...currentDataset.nodes],
        };
      }
    } catch (error) {
      getLfManager().log('Failed to expand node.', { error, nodeId, path }, LogSeverity.Warning);
    }
  };

  const handleTreeClick = async (node: LfDataNode) => {
    const metadata = extractMetadata(node);
    if (!metadata) return;

    const targetPath = normalizeDirectoryRequest(getDirectoryPath(metadata));
    const currentPath = normalizeDirectoryRequest(
      editorState.directoryValue ?? deriveDirectoryValue(editorState.directory) ?? '',
    );

    // Skip if clicking the same directory (unless it's a root)
    if (targetPath === currentPath && !metadata.isRoot) return;

    await editorState.refreshDirectory?.(targetPath);
  };

  return {
    loadRoots,
    expandNode,
    handleTreeClick,
  };
};
