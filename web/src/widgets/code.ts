import { CodeCSS, CodeFactory, CodeNormalizeCallback, CodeState } from '../types/widgets/code';
import { CustomWidgetName, NodeName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, CodeState>();

export const codeFactory: CodeFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { code } = STATE.get(wrapper);

        switch (code.lfLanguage) {
          case 'json':
            return code.lfValue || '{}';
          default:
            return code.lfValue || '';
        }
      },
      setValue(value) {
        const { code } = STATE.get(wrapper);

        const callback: CodeNormalizeCallback = (v, u) => {
          switch (code.lfLanguage) {
            case 'json':
              code.lfValue = u.unescapedString || '{}';
              break;
            default:
              code.lfValue = typeof v === 'string' ? v : '';
              break;
          }
        };

        normalizeValue(value, callback, CustomWidgetName.code);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const code = document.createElement(TagName.LfCode);

    content.classList.add(CodeCSS.Content);
    code.classList.add(CodeCSS.Widget);

    switch (node.comfyClass) {
      case NodeName.displayJson:
      case NodeName.displayPrimitiveAsJson:
      case NodeName.geminiAPI:
      case NodeName.shuffleJsonKeys:
      case NodeName.sortJsonKeys:
      case NodeName.stringToJson:
        code.lfLanguage = 'json';
        code.lfValue = '{}';
        break;
      default:
        code.lfLanguage = 'markdown';
        code.lfValue = '';
        break;
    }

    content.appendChild(code);
    wrapper.appendChild(content);

    const options = codeFactory.options(wrapper);

    STATE.set(wrapper, { code, node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.code, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
