import { SETTINGS, TREE_DATA } from '../fixtures/imageEditor';
import { EV_HANDLERS, getStatusColumn, setGridStatus, updateCb } from '../helpers/imageEditor';
import { ensureDatasetContext } from '../helpers/imageEditor/dataset';
import { setBrush } from '../helpers/imageEditor/settings';
import { LfEventName } from '../types/events/events';
import { LogSeverity } from '../types/manager/manager';
import {
  ImageEditorActionButtons,
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
import { createDOMWidget, getLfManager, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, ImageEditorState>();
export const IMAGE_EDITOR_INSTANCES = new Set<ImageEditorState>();

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

        const callback: ImageEditorNormalizeCallback = (_, u) => {
          const parsedValue = u.parsedJson as ImageEditorDeserializedValue;
          const isPending = getStatusColumn(parsedValue)?.title === ImageEditorStatus.Pending;
          if (isPending) {
            setGridStatus(ImageEditorStatus.Pending, grid, actionButtons);
          }

          const dataset = (parsedValue || {}) as ImageEditorDataset;
          ensureDatasetContext(dataset, state);

          imageviewer.lfDataset = dataset;
          imageviewer.getComponents().then(({ details }) => {
            const { canvas } = details;
            if (canvas) {
              setBrush(canvas, STATE.get(wrapper).lastBrushSettings);
            }
          });
        };

        normalizeValue(value, callback, CustomWidgetName.imageEditor);
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

    const refresh = async (directory: string) => {
      const state = STATE.get(wrapper);
      getLfManager()
        .getApiRoutes()
        .image.get(directory)
        .then((r) => {
          if (r.status === 'success') {
            if (r?.data && Object.entries(r.data).length > 0) {
              const dataset = r.data as ImageEditorDataset;
              ensureDatasetContext(dataset, state);

              imageviewer.lfDataset = dataset;
            } else {
              getLfManager().log('Images not found.', { r }, LogSeverity.Info);
            }
          }
        });
    };

    settings.classList.add(ImageEditorCSS.Settings);
    settings.slot = 'settings';

    imageviewer.classList.add(ImageEditorCSS.Widget);
    imageviewer.lfLoadCallback = async (_, value) => await refresh(value);
    imageviewer.lfValue = TREE_DATA;
    imageviewer.addEventListener(LfEventName.LfImageviewer, (e) =>
      EV_HANDLERS.imageviewer(STATE.get(wrapper), e),
    );
    imageviewer.appendChild(settings);

    const actionButtons: ImageEditorActionButtons = {};

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

    const state: ImageEditorState = {
      elements: { actionButtons, controls: {}, grid, imageviewer, settings },
      contextId: undefined,
      filter: null,
      filterType: null,
      lastBrushSettings: JSON.parse(JSON.stringify(SETTINGS.brush.settings)),
      node,
      update: {
        preview: () => updateCb(STATE.get(wrapper)).then(() => {}),
        snapshot: () => updateCb(STATE.get(wrapper), true).then(() => {}),
      },
      wrapper,
    };

    STATE.set(wrapper, state);
    IMAGE_EDITOR_INSTANCES.add(state);

    return { widget: createDOMWidget(CustomWidgetName.imageEditor, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
