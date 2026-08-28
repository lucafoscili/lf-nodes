import { LfDataNode } from '@lf-widgets/foundations/dist';
import { IMAGE_API } from '../api/image';
import { JSON_API } from '../api/json';
import { SETTINGS } from '../fixtures/imageEditor/settings';
import { TREE_DATA } from '../fixtures/imageEditor/treeData';
import {
  EV_HANDLERS,
  getStatusColumn,
  prepSettings,
  setGridStatus,
  updateCb,
} from '../helpers/imageEditor';
import {
  deriveDirectoryValue,
  ensureDatasetContext,
  getNavigationDirectory,
  mergeNavigationDirectory,
} from '../helpers/imageEditor/dataset';
import { syncNavigationDirectoryControl } from '../helpers/imageEditor/navigation';
import { createNavigationTreeManager } from '../helpers/imageEditor/navigationTree';
import { setBrush } from '../helpers/imageEditor/settings';
import type { GetFilesystemAPIPayload, GetImageAPIPayload } from '../types/api/api';
import { LfEventName } from '../types/events/events';
import { LogSeverity } from '../types/manager/manager';
import {
  ImageEditorActionButtons,
  ImageEditorColumnId,
  ImageEditorCSS,
  ImageEditorDataset,
  ImageEditorDeserializedValue,
  ImageEditorFactory,
  ImageEditorIcons,
  ImageEditorNormalizeCallback,
  ImageEditorState,
  ImageEditorStatus,
} from '../types/widgets/imageEditor';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import {
  createDOMWidget,
  getComfyClientId,
  getLfManager,
  normalizeDirectoryRequest,
  normalizeValue,
} from '../utils/common';

export const IMAGE_EDITOR_INSTANCES = new Set<ImageEditorState>();
const STATE = new WeakMap<HTMLDivElement, ImageEditorState>();

export interface ImageEditorRecoveryRequest {
  contextId?: string;
  callerClientId?: string;
}

export const queueImageEditorHydration = (state: ImageEditorState, value: unknown): void => {
  state.pendingHydrationValue = value;
};

export const consumeImageEditorHydration = (
  state: ImageEditorState,
  fallback: unknown,
): unknown => {
  const value = state.pendingHydrationValue ?? fallback;
  delete state.pendingHydrationValue;
  return value;
};

const isPendingImageEditorDataset = (dataset: unknown): dataset is ImageEditorDataset =>
  Boolean(
    dataset &&
      typeof dataset === 'object' &&
      getStatusColumn(dataset as ImageEditorDataset)?.title === ImageEditorStatus.Pending,
  );

/**
 * Keeps the observational dataset visible while removing every capability that
 * could resume or mutate a serialized session whose server-side ownership
 * could not be re-established. The immutable owner is preserved verbatim; it
 * is evidence, not a credential the frontend may rewrite.
 */
export const makeImageEditorDatasetInert = (dataset: ImageEditorDataset): ImageEditorDataset => {
  const inert: ImageEditorDataset & { recovery_client_id?: string } = {
    ...dataset,
    columns: Array.isArray(dataset.columns)
      ? dataset.columns.filter(
          (column) =>
            column.id !== ImageEditorColumnId.Path && column.id !== ImageEditorColumnId.Status,
        )
      : dataset.columns,
    selection: dataset.selection ? { ...dataset.selection } : dataset.selection,
  };

  delete inert.context_id;
  delete inert.recovery_client_id;
  if (inert.selection) {
    delete inert.selection.context_id;
  }
  return inert;
};

export const resolveImageEditorHydrationDataset = (
  serializedDataset: unknown,
  recoveredDataset: ImageEditorDataset | null,
): { dataset: unknown; readOnly: boolean } => {
  if (recoveredDataset) {
    return { dataset: recoveredDataset, readOnly: false };
  }
  if (isPendingImageEditorDataset(serializedDataset)) {
    return {
      dataset: makeImageEditorDatasetInert(serializedDataset),
      readOnly: true,
    };
  }
  return { dataset: serializedDataset, readOnly: false };
};

/**
 * Resolves the recovery authority carried by the widget's serialized value.
 *
 * Load-and-edit node ids are graph-local, so they are not sufficient to select
 * a completed loader session. Its root context_id is the exact capability for
 * that dataset; without it, hydration must use the serialized value instead of
 * falling back to a node-wide scan. A breakpoint is an active transaction and
 * intentionally retains its node-scoped pending-session recovery.
 */
export const resolveImageEditorRecoveryRequest = (
  nodeName: string | undefined,
  serializedDataset: unknown,
  callerClientId?: string,
): ImageEditorRecoveryRequest | null => {
  if (nodeName === NodeName.loadAndEditImages) {
    if (!serializedDataset || typeof serializedDataset !== 'object') {
      return null;
    }

    const contextId = (serializedDataset as { context_id?: unknown }).context_id;
    return typeof contextId === 'string' && contextId.trim()
      ? {
          contextId: contextId.trim(),
          ...(callerClientId ? { callerClientId } : {}),
        }
      : null;
  }

  if (nodeName === NodeName.imagesEditingBreakpoint) {
    const contextId = isPendingImageEditorDataset(serializedDataset)
      ? (serializedDataset as { context_id?: unknown }).context_id
      : undefined;
    const exactContextId =
      typeof contextId === 'string' && contextId.trim() ? contextId.trim() : undefined;
    if (!exactContextId && !callerClientId) {
      return null;
    }
    return {
      ...(exactContextId ? { contextId: exactContextId } : {}),
      ...(callerClientId ? { callerClientId } : {}),
    };
  }

  return null;
};

export const imageEditorFactory: ImageEditorFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue: () => {
        const { imageviewer } = STATE.get(wrapper).elements;
        return imageviewer.lfDataset || {};
      },
      setValue: (value) => {
        const state = STATE.get(wrapper);
        const { actionButtons, grid, imageviewer } = state.elements;
        const { status } = state;

        const isInitializing = status === 'initializing';

        let serializedDataset: unknown;
        try {
          serializedDataset = getLfManager()
            .getManagers()
            .lfFramework.syntax.json.unescape(value).parsedJSON;
        } catch {
          serializedDataset = undefined;
        }

        const callerClientId = getComfyClientId();
        const recoveryRequest = resolveImageEditorRecoveryRequest(
          state.node.comfyClass,
          serializedDataset,
          callerClientId,
        );

        const reconcileSession = async () => {
          if (!isInitializing) {
            return Promise.reject('Already initialized');
          }

          state.status = 'reconciling';

          if (!recoveryRequest) {
            return null;
          }

          try {
            const nodeId = String(state.node.id ?? '');
            const resp = await JSON_API.recoverEditDataset(
              nodeId,
              recoveryRequest.contextId,
              recoveryRequest.callerClientId,
            );
            if (resp.status !== LogSeverity.Success || !resp.data) {
              return null;
            }

            const dataset = resp.data as ImageEditorDataset;
            return dataset;
          } catch (error) {
            getLfManager().log(
              'Failed to recover pending editing dataset for image editor.',
              { error, nodeId: state.node.id },
              LogSeverity.Warning,
            );
          }

          return null;
        };

        const callback: ImageEditorNormalizeCallback = (_, u) => {
          const parsedValue = u.parsedJSON as ImageEditorDeserializedValue;
          const isPending = getStatusColumn(parsedValue)?.title === ImageEditorStatus.Pending;
          if (state.node.comfyClass === NodeName.imagesEditingBreakpoint) {
            setGridStatus(
              isPending && !state.recoveryReadOnly
                ? ImageEditorStatus.Pending
                : ImageEditorStatus.Completed,
              grid,
              actionButtons,
            );
          }

          const dataset = (parsedValue || {}) as ImageEditorDataset;
          if (state.recoveryReadOnly) {
            state.contextId = undefined;
          } else {
            ensureDatasetContext(dataset, state);
          }

          const navigationDirectory = getNavigationDirectory(dataset);
          if (navigationDirectory) {
            state.directory = { ...navigationDirectory };
          }

          const derivedDirectoryValue = deriveDirectoryValue(navigationDirectory);
          if (derivedDirectoryValue !== undefined) {
            state.directoryValue = derivedDirectoryValue;
          }

          imageviewer.lfDataset = dataset;
          imageviewer
            .getComponents()
            .then(({ details }) => {
              const { canvas } = details;
              if (canvas) {
                setBrush(canvas, STATE.get(wrapper).lastBrushSettings);
              }
            })
            .catch((error) =>
              getLfManager().log(
                'Failed to prepare image editor canvas.',
                { error },
                LogSeverity.Warning,
              ),
            );

          syncNavigationDirectoryControl(state, state.directoryValue);

          const shouldAutoLoad =
            !state.hasAutoDirectoryLoad &&
            (!Array.isArray(dataset?.nodes) || dataset.nodes.length === 0);

          if (shouldAutoLoad) {
            state.hasAutoDirectoryLoad = true;
            state.refreshDirectory?.(normalizeDirectoryRequest(state.directoryValue));
          }

          if (state.filterNodeId) {
            const findNodeById = (id: string) => {
              const search = (nodes: LfDataNode[]): LfDataNode | undefined => {
                for (const n of nodes) {
                  if (n && typeof n === 'object') {
                    if ((n.id as string) === id) {
                      return n;
                    }
                    if (Array.isArray(n.children)) {
                      const found = search(n.children);
                      if (found) {
                        return found;
                      }
                    }
                  }
                }
                return undefined;
              };
              return search(TREE_DATA.nodes || []);
            };

            const detailsNode = findNodeById(state.filterNodeId);
            if (detailsNode) {
              prepSettings(state, detailsNode);
            }
          }
        };

        switch (status) {
          case 'initializing':
            reconcileSession().then((reconciled) => {
              const hydration = resolveImageEditorHydrationDataset(
                consumeImageEditorHydration(state, serializedDataset ?? value),
                reconciled,
              );
              state.recoveryReadOnly = hydration.readOnly;
              const dataset = hydration.dataset;
              normalizeValue(dataset, callback, CustomWidgetName.imageEditor);
              state.status = 'ready';
            });
            break;
          case 'reconciling':
            // A breakpoint can emit its live context while initial recovery is
            // still in flight. Keep the newest authorized dataset so the
            // initialization result cannot overwrite or discard that event.
            queueImageEditorHydration(state, serializedDataset ?? value);
            break;
          case 'ready':
            state.recoveryReadOnly = false;
            normalizeValue(value, callback, CustomWidgetName.imageEditor);
            break;
        }
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const settings = document.createElement(TagName.Div);
    const imageviewer = document.createElement(TagName.LfImageviewer);

    const navigationTreeEnabled = node.comfyClass === NodeName.loadAndEditImages;
    let navigationManager: ReturnType<typeof createNavigationTreeManager> | null = null;

    const refresh = async (directory: string) => {
      const state = STATE.get(wrapper);
      const normalizedDirectory = normalizeDirectoryRequest(directory);

      if (!state) {
        return;
      }

      state.hasAutoDirectoryLoad = true;
      state.lastRequestedDirectory = normalizedDirectory;

      try {
        if (navigationTreeEnabled) {
          const response = await IMAGE_API.explore(normalizedDirectory, { scope: 'dataset' });

          if (response.status !== LogSeverity.Success) {
            getLfManager().log('Images not found.', { response }, LogSeverity.Info);
            return;
          }

          const fsData = response.data as GetFilesystemAPIPayload['data'];
          const dataset: ImageEditorDataset =
            (fsData?.dataset as ImageEditorDataset) ?? ({ nodes: [] } as ImageEditorDataset);

          const mergedDirectory = mergeNavigationDirectory(dataset, { raw: normalizedDirectory });

          state.directory = { ...mergedDirectory };
          const derivedDirectoryValue = deriveDirectoryValue(mergedDirectory);
          state.directoryValue = derivedDirectoryValue ?? normalizedDirectory;
          state.lastRequestedDirectory = state.directoryValue;

          ensureDatasetContext(dataset, state);
          imageviewer.lfDataset = dataset;
        } else {
          const response = await IMAGE_API.get(normalizedDirectory);

          if (response.status !== LogSeverity.Success) {
            getLfManager().log('Images not found.', { response }, LogSeverity.Info);
            return;
          }

          const imageData = response.data as GetImageAPIPayload['data'];
          const dataset: ImageEditorDataset =
            (imageData as ImageEditorDataset) ?? ({ nodes: [] } as ImageEditorDataset);

          const mergedDirectory = mergeNavigationDirectory(dataset, { raw: normalizedDirectory });

          state.directory = { ...mergedDirectory };
          const derivedDirectoryValue = deriveDirectoryValue(mergedDirectory);
          state.directoryValue = derivedDirectoryValue ?? normalizedDirectory;
          state.lastRequestedDirectory = state.directoryValue;

          ensureDatasetContext(dataset, state);
          imageviewer.lfDataset = dataset;
        }

        await syncNavigationDirectoryControl(state, state.directoryValue);
      } catch (error) {
        getLfManager().log(
          'Failed to refresh image directory.',
          { error, directory: normalizedDirectory },
          LogSeverity.Warning,
        );
      }
    };

    settings.classList.add(ImageEditorCSS.Settings);
    settings.slot = 'settings';

    imageviewer.classList.add(ImageEditorCSS.Widget);
    imageviewer.lfLoadCallback = async (_, value) => {
      const state = STATE.get(wrapper);
      if (!state || state.isSyncingDirectory) {
        return;
      }

      if (!navigationTreeEnabled) {
        return;
      }

      const directoryValue = normalizeDirectoryRequest(value);

      if (
        state.lastRequestedDirectory === directoryValue &&
        state.directoryValue === directoryValue
      ) {
        getLfManager().log('lfLoadCallback: directory unchanged, skipping', {}, LogSeverity.Info);
        return;
      }

      await refresh(directoryValue);
    };
    imageviewer.lfValue = TREE_DATA;
    imageviewer.addEventListener(LfEventName.LfImageviewer, (e) =>
      EV_HANDLERS.imageviewer(STATE.get(wrapper), e),
    );
    imageviewer.appendChild(settings);

    const actionButtons: ImageEditorActionButtons = {};

    const state: ImageEditorState = {
      contextId: undefined,
      elements: { actionButtons, controls: {}, grid, imageviewer, settings },
      directory: undefined,
      directoryValue: undefined,
      filter: null,
      filterType: null,
      hasAutoDirectoryLoad: false,
      isSyncingDirectory: false,
      lastBrushSettings: JSON.parse(JSON.stringify(SETTINGS.brush.settings)),
      lastRequestedDirectory: undefined,
      node,
      refreshDirectory: refresh,
      status: 'initializing',
      update: {
        apply: () => updateCb(STATE.get(wrapper), true, false, true).then(() => {}),
        preview: () => updateCb(STATE.get(wrapper)).then(() => {}),
        snapshot: () => updateCb(STATE.get(wrapper), true).then(() => {}),
      },
      wrapper,
    };

    switch (node.comfyClass) {
      case NodeName.imagesEditingBreakpoint:
        const actions = document.createElement(TagName.Div);
        const interrupt = document.createElement(TagName.LfButton);
        const resume = document.createElement(TagName.LfButton);

        interrupt.lfIcon = ImageEditorIcons.Interrupt;
        interrupt.lfLabel = 'Interrupt workflow';
        interrupt.lfStretchX = true;
        interrupt.lfUiState = 'danger';
        interrupt.title = 'Click to interrupt the workflow.';
        interrupt.addEventListener(LfEventName.LfButton, (e) =>
          EV_HANDLERS.button(STATE.get(wrapper), e),
        );

        resume.lfIcon = ImageEditorIcons.Resume;
        resume.lfLabel = 'Resume workflow';
        resume.lfStretchX = true;
        resume.lfStyling = 'flat';
        resume.lfUiState = 'success';
        resume.title =
          'Click to resume the workflow. Remember to save your snapshots after editing the images!';
        resume.addEventListener(LfEventName.LfButton, (e) =>
          EV_HANDLERS.button(STATE.get(wrapper), e),
        );

        actions.classList.add(ImageEditorCSS.Actions);
        actions.appendChild(interrupt);
        actions.appendChild(resume);

        grid.classList.add(ImageEditorCSS.GridIsInactive);
        grid.classList.add(ImageEditorCSS.GridHasActions);
        grid.appendChild(actions);

        actionButtons.interrupt = interrupt;
        actionButtons.resume = resume;

        setGridStatus(ImageEditorStatus.Completed, grid, actionButtons);
    }

    grid.classList.add(ImageEditorCSS.Grid);
    grid.appendChild(imageviewer);

    content.classList.add(ImageEditorCSS.Content);
    content.appendChild(grid);

    wrapper.appendChild(content);

    const options = imageEditorFactory.options(wrapper);

    STATE.set(wrapper, state);
    IMAGE_EDITOR_INSTANCES.add(state);

    if (navigationTreeEnabled) {
      navigationManager = createNavigationTreeManager(imageviewer, state);
      state.navigationManager = navigationManager;
    }

    void Promise.resolve().then(async () => {
      if (!navigationTreeEnabled) {
        return;
      }

      const currentState = STATE.get(wrapper);
      if (!currentState) {
        return;
      }

      if (navigationTreeEnabled && navigationManager) {
        await navigationManager.loadRoots();
      }

      if (currentState.hasAutoDirectoryLoad) {
        return;
      }

      const currentDataset = currentState.elements.imageviewer?.lfDataset as
        | ImageEditorDataset
        | undefined;
      const hasNodes = Array.isArray(currentDataset?.nodes) && currentDataset.nodes.length > 0;
      const hasDirectoryValue = Boolean(currentState.directoryValue);

      if (hasNodes || hasDirectoryValue) {
        return;
      }

      currentState.refreshDirectory?.('');
    });

    return { widget: createDOMWidget(CustomWidgetName.imageEditor, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
