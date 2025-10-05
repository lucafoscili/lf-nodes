import { LfDataDataset, LfDataNode, LfTreeElement } from '@lf-widgets/foundations';
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
  try {
    const raw = (node.cells?.lfCode as { value?: unknown })?.value;
    if (typeof raw !== 'string') return null;

    const parsed = JSON.parse(raw) as Partial<NavigationMetadata>;
    return {
      id: parsed.id ?? String(node.id ?? ''),
      name: parsed.name ?? String(node.value ?? ''),
      hasChildren: Boolean(parsed.hasChildren),
      paths: parsed.paths ?? {},
      isRoot: parsed.isRoot,
    };
  } catch {
    return null;
  }
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

  const updateTreeDataset = (dataset: LfDataDataset | null) => {
    state.dataset = dataset;
    imageviewer.lfTreeProps = {
      ...imageviewer.lfTreeProps,
      lfDataset: dataset ?? { columns: dataset?.columns ?? [], nodes: [] },
    };
  };

  const mergeChildren = (
    parentId: string,
    children: LfDataNode[],
    columns?: LfDataDataset['columns'],
  ) => {
    if (!state.dataset) return;

    const lfData = getLfData();
    if (!lfData) return;

    const merged = lfData.node.mergeChildren(state.dataset, {
      parentId,
      children,
      columns: columns as any,
    }) as LfDataDataset;

    updateTreeDataset(merged);
    state.loadedNodes.add(parentId);
    state.pendingNodes.delete(parentId);
  };

  const loadRoots = async () => {
    if (state.loadedNodes.has('root')) return;

    state.pendingNodes.add('root');
    try {
      const response = await IMAGE_API.explore('', { scope: 'roots' });
      if (response.status === LogSeverity.Success && response.data?.tree) {
        updateTreeDataset(response.data.tree);
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
          mergeChildren(nodeId, branch.nodes, branch.columns);
        }
      }
    } catch (error) {
      getLfManager().log('Failed to expand node.', { error, nodeId, path }, LogSeverity.Warning);
    } finally {
      state.pendingNodes.delete(nodeId);
    }
  };

  const selectNode = async (node: LfDataNode) => {
    const metadata = extractMetadata(node);
    if (!metadata) return;

    const targetPath = normalizeDirectoryRequest(getDirectoryPath(metadata));
    const currentPath = normalizeDirectoryRequest(
      editorState.directoryValue ?? deriveDirectoryValue(editorState.directory) ?? '',
    );

    if (targetPath === currentPath && !metadata.isRoot) return;

    await editorState.refreshDirectory?.(targetPath);
  };

  const persistExpansion = async (
    tree: LfTreeElement,
    expandedIds: string[],
  ): Promise<Set<string>> => {
    if (!tree.setExpandedNodes) {
      return new Set(expandedIds);
    }

    try {
      await tree.setExpandedNodes(expandedIds);
      if (tree.getExpandedNodeIds) {
        const normalized = await tree.getExpandedNodeIds();
        return new Set(normalized);
      }
    } catch (error) {
      getLfManager().log('Failed to persist tree expansion.', { error }, LogSeverity.Warning);
    }
    return new Set(expandedIds);
  };

  return {
    loadRoots,
    expandNode,
    selectNode,
    persistExpansion,
    getState: () => ({ ...state }),
  };
};
