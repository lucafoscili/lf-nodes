import { LfDataDataset, LfDataNode } from '@lf-widgets/foundations';
import { IMAGE_API } from '../../api/image';
import { LogSeverity } from '../../types/manager/manager';
import { ImageEditorState } from '../../types/widgets/imageEditor';
import { getLfManager, normalizeDirectoryRequest } from '../../utils/common';
import { deriveDirectoryValue } from './dataset';

interface NavigationTreeState {
  dataset: LfDataDataset | null;
  loadedNodes: Set<string>;
  pendingNodes: Set<string>;
}

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
  const state: NavigationTreeState = {
    dataset: null,
    loadedNodes: new Set(),
    pendingNodes: new Set(),
  };

  const updateTreeDataset = async (dataset: LfDataDataset | null) => {
    state.dataset = dataset;

    if (imageviewer.lfNavigation?.treeProps) {
      imageviewer.lfNavigation.treeProps.lfDataset = dataset ?? {
        columns: dataset?.columns ?? [],
        nodes: [],
      };
    }
  };

  const mergeChildren = async (
    parentId: string,
    children: LfDataNode[],
    columns?: LfDataDataset['columns'],
  ) => {
    if (!state.dataset) return;

    const lfData = getLfData();
    if (!lfData) return;

    const parentNode = lfData.node.find(state.dataset, (node) => node.id === parentId);
    if (!parentNode) return;

    const merged: LfDataDataset = {
      ...state.dataset,
      columns: columns || state.dataset.columns,
      nodes: [...state.dataset.nodes], // Clone to trigger reactivity
    };

    parentNode.children = [...children]; // Replace parent's children

    await updateTreeDataset(merged);
    state.loadedNodes.add(parentId);
    state.pendingNodes.delete(parentId);
  };

  const loadRoots = async () => {
    if (state.loadedNodes.has('root')) return;

    state.pendingNodes.add('root');
    try {
      const response = await IMAGE_API.explore('', { scope: 'roots' });
      if (response.status === LogSeverity.Success && response.data?.tree) {
        await updateTreeDataset(response.data.tree);
        state.loadedNodes.add('root');
      }
    } catch (error) {
      getLfManager().log('Failed to load navigation roots.', { error }, LogSeverity.Warning);
    } finally {
      state.pendingNodes.delete('root');
    }
  };

  const expandNode = async (node: LfDataNode) => {
    const metadata = extractMetadata(node);
    if (!metadata?.hasChildren) return;

    const nodeId = metadata.id;
    if (state.loadedNodes.has(nodeId) || state.pendingNodes.has(nodeId)) return;

    const path = normalizeDirectoryRequest(getDirectoryPath(metadata));
    if (!path) return;

    state.pendingNodes.add(nodeId);
    try {
      const response = await IMAGE_API.explore(path, { scope: 'tree', nodePath: path });
      if (response.status === LogSeverity.Success && response.data?.tree) {
        const branch = response.data.tree;
        if (Array.isArray(branch.nodes)) {
          await mergeChildren(nodeId, branch.nodes, branch.columns);
        }
      }
    } catch (error) {
      getLfManager().log('Failed to expand node.', { error, nodeId, path }, LogSeverity.Warning);
    } finally {
      state.pendingNodes.delete(nodeId);
    }
  };

  const syncSelection = async (nodeId: string) => {
    try {
      const { navigation } = await imageviewer.getComponents();
      if (navigation?.tree) {
        await navigation.tree.setSelectedNodes(nodeId);
      }
    } catch (error) {
      getLfManager().log('Failed to sync tree selection.', { error, nodeId }, LogSeverity.Warning);
    }
  };

  const selectNode = async (node: LfDataNode) => {
    const metadata = extractMetadata(node);
    if (!metadata) return;

    const targetPath = normalizeDirectoryRequest(getDirectoryPath(metadata));
    const currentPath = normalizeDirectoryRequest(
      editorState.directoryValue ?? deriveDirectoryValue(editorState.directory) ?? '',
    );

    await syncSelection(metadata.id);

    if (targetPath === currentPath && !metadata.isRoot) return;

    await editorState.refreshDirectory?.(targetPath);
  };

  const syncSelectionByPath = async (directoryPath: string) => {
    const normalizedPath = normalizeDirectoryRequest(directoryPath);

    try {
      const { navigation } = await imageviewer.getComponents();
      if (!navigation?.tree) return;

      await navigation.tree.selectByPredicate((node) => {
        const metadata = extractMetadata(node);
        if (!metadata) return false;
        const nodePath = normalizeDirectoryRequest(getDirectoryPath(metadata));
        return nodePath === normalizedPath;
      });
    } catch (error) {
      getLfManager().log(
        'Failed to sync selection by path.',
        { error, path: directoryPath },
        LogSeverity.Warning,
      );
    }
  };

  return {
    loadRoots,
    expandNode,
    selectNode,
    syncSelectionByPath,
    getState: () => ({ ...state }),
  };
};
