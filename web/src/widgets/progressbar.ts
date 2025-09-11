import {
  ProgressbarCSS,
  ProgressbarDeserializedValue,
  ProgressbarFactory,
  ProgressbarLabels,
  ProgressbarNormalizeCallback,
  ProgressbarState,
} from '../types/widgets/progressbar';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, ProgressbarState>();

export const progressbarFactory: ProgressbarFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { progressbar } = STATE.get(wrapper);

        return {
          bool: progressbar.lfLabel === 'true' ? true : false,
          roll: progressbar.lfValue || 0,
        };
      },
      setValue(value) {
        const { node, progressbar } = STATE.get(wrapper);

        const callback: ProgressbarNormalizeCallback = (_, u) => {
          const { bool, roll } = u.parsedJson as ProgressbarDeserializedValue;

          const isFalse = !!(bool === false);
          const isTrue = !!(bool === true);

          switch (node.comfyClass) {
            case NodeName.resolutionSwitcher:
              if (isTrue) {
                progressbar.lfLabel = ProgressbarLabels.ArrowRight;
                progressbar.lfUiState = 'primary';
              } else if (isFalse) {
                progressbar.lfLabel = ProgressbarLabels.ArrowUp;
                progressbar.lfUiState = 'secondary';
              } else {
                progressbar.lfLabel = ProgressbarLabels.Fallback;
                progressbar.lfUiState = 'disabled';
              }
              break;
            default:
              if (isTrue) {
                progressbar.lfLabel = ProgressbarLabels.True;
                progressbar.lfUiState = 'success';
              } else if (isFalse) {
                progressbar.lfLabel = ProgressbarLabels.False;
                progressbar.lfUiState = 'danger';
              } else {
                progressbar.lfLabel = ProgressbarLabels.Fallback;
                progressbar.lfUiState = 'disabled';
              }
              break;
          }

          progressbar.title = roll ? 'Actual roll: ' + roll.toString() : '';
          progressbar.lfValue = roll || 100;
        };

        normalizeValue(value, callback, CustomWidgetName.progressbar);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const progressbar = document.createElement(TagName.LfProgressbar);

    progressbar.lfIsRadial = true;
    progressbar.lfLabel = ProgressbarLabels.Fallback;

    content.classList.add(ProgressbarCSS.Content);
    content.appendChild(progressbar);

    wrapper.appendChild(content);

    const options = progressbarFactory.options(wrapper);

    STATE.set(wrapper, { node, progressbar, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.progressbar, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
