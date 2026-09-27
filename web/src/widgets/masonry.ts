import {
  installAudioPreviewHistory,
  releaseAudioPreview,
  setMasonryAudio,
} from '../helpers/audioPreview';
import { EV_HANDLERS } from '../helpers/masonry';
import { LfEventName } from '../types/events/events';
import {
  MasonryCSS,
  MasonryDeserializedValue,
  MasonryFactory,
  MasonryNormalizeCallback,
  MasonryState,
} from '../types/widgets/masonry';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, isValidNumber, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, MasonryState>();

export const masonryFactory: MasonryFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { audio, masonry, selected } = STATE.get(wrapper);
        const { index, name } = selected;

        return {
          ...(selected.file_identity ? { file_identity: { ...selected.file_identity } } : {}),
          ...(audio ? { audio: audio.map((file) => ({ ...file })) } : {}),
          columns: masonry?.lfColumns || 3,
          dataset: masonry?.lfDataset || {},
          index: isValidNumber(index) ? index : NaN,
          name: name || '',
          view: masonry?.lfView || 'main',
        };
      },
      setValue(value) {
        const callback: MasonryNormalizeCallback = (_, u) => {
          const state = STATE.get(wrapper);
          const { masonry, selected } = state;

          const { audio, columns, dataset, index, name, view, slot_map, file_identity } =
            u.parsedJSON as unknown as MasonryDeserializedValue;

          if (columns) {
            masonry.lfColumns = columns;
          }
          if (dataset) {
            masonry.lfDataset = dataset || {};
          }
          if (view) {
            masonry.lfView = view;
          }
          if (file_identity && typeof file_identity.directory === 'string' && typeof file_identity.relative_path === 'string') {
            selected.file_identity = { ...file_identity };
          } else if (isValidNumber(index) || typeof name === 'string') {
            delete selected.file_identity;
          }
          if (isValidNumber(index)) {
            selected.index = index;
            selected.name = name || '';
            masonry.setSelectedShape(index);
          } else if (typeof name === 'string') {
            selected.index = NaN;
            selected.name = name;
          }

          if (Array.isArray(audio)) {
            setMasonryAudio(state, audio);
          } else if (slot_map && typeof slot_map === 'object' && Object.keys(slot_map).length > 0) {
            while (masonry.firstChild) {
              masonry.removeChild(masonry.firstChild);
            }

            for (const key in slot_map) {
              if (!Object.hasOwn(slot_map, key)) continue;

              const element = slot_map[key];
              const div = document.createElement('div');
              div.innerHTML = element;
              div.setAttribute('slot', key);
              div.classList.add(MasonryCSS.Slot);
              masonry.appendChild(div);
            }

            masonry.lfShape = 'slot';
          }
        };

        normalizeValue(value, callback, CustomWidgetName.masonry);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const masonry = document.createElement(TagName.LfMasonry);

    masonry.classList.add(MasonryCSS.Widget);
    masonry.addEventListener(LfEventName.LfMasonry, (e) =>
      EV_HANDLERS.masonry(STATE.get(wrapper), e),
    );
    masonry.lfActions = true;
    masonry.lfColumns = 3;

    switch (node.comfyClass) {
      case NodeName.saveAudio:
        masonry.lfActions = false;
        masonry.lfColumns = 1;
        break;
      case NodeName.loadImages:
        masonry.lfSelectable = true;
        break;
    }

    content.classList.add(MasonryCSS.Content);
    content.appendChild(masonry);

    wrapper.appendChild(content);

    const options = masonryFactory.options(wrapper);

    STATE.set(wrapper, { masonry, node, selected: { index: NaN, name: '' }, wrapper });

    if (node.comfyClass === NodeName.saveAudio) {
      installAudioPreviewHistory(node, (audio) => options.setValue(JSON.stringify({ audio })));
      const onRemoved = node.onRemoved;
      node.onRemoved = function () {
        releaseAudioPreview(masonry);
        return onRemoved?.apply(this, arguments);
      };
    }

    return { widget: createDOMWidget(CustomWidgetName.masonry, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
