import { createContent } from '../helpers/controlPanel';
import { LfEventName } from '../types/events/events';
import {
  ControlPanelCSS,
  ControlPanelDeserializedValue,
  ControlPanelFactory,
  ControlPanelNormalizeCallback,
  ControlPanelState,
} from '../types/widgets/controlPanel';
import { CustomWidgetName, TagName } from '../types/widgets/widgets';
import { createDOMWidget, getApiRoutes, getLfManager, normalizeValue } from '../utils/common';

const STATE = new WeakMap<HTMLDivElement, ControlPanelState>();

export const controlPanelFactory: ControlPanelFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE.get(wrapper),
      getValue() {
        return {
          backup: getLfManager().isBackupEnabled() || false,
          backupRetention: getLfManager().getBackupRetention() || 14,
          debug: getLfManager().isDebug() || false,
          themes: getLfManager().getManagers().lfFramework.theme.get.current().name || '',
        };
      },
      setValue(value) {
        const callback: ControlPanelNormalizeCallback = (_, u) => {
          const { backup, backupRetention, debug, themes } =
            u.parsedJson as ControlPanelDeserializedValue;

          if (backup === true || backup === false) {
            getLfManager().toggleBackup(backup);
          }
          if (typeof backupRetention === 'number') {
            getLfManager().setBackupRetention(backupRetention);
          }
          if (debug === true || debug === false) {
            getLfManager().toggleDebug(debug);
          }
          if (themes) {
            getLfManager().getManagers().lfFramework.theme.set(themes);
          }
          return value;
        };

        normalizeValue(value, callback, CustomWidgetName.controlPanel);
      },
    };
  },
  //#endregion

  //#region Render
  render: (node) => {
    const contentCb = (domWidget: HTMLDivElement, isReady: boolean) => {
      const readyCb = (domWidget: HTMLDivElement) => {
        setTimeout(() => {
          getApiRoutes().backup.new();
          contentCb(domWidget, true);
          getApiRoutes().backup.cleanOld();
        }, 750);
      };

      const createSpinner = () => {
        const spinner = document.createElement(TagName.LfSpinner);
        spinner.classList.add(ControlPanelCSS.Spinner);
        spinner.lfActive = true;
        spinner.lfLayout = 11;

        return spinner;
      };

      const content = document.createElement(TagName.Div);

      if (isReady) {
        content.appendChild(createContent());
        domWidget.replaceChild(content, domWidget.firstChild);
      } else {
        const spinner = createSpinner();
        spinner.addEventListener(LfEventName.LfSpinner, readyCb.bind(null, domWidget));
        content.appendChild(spinner);
        domWidget.appendChild(content);
      }

      content.classList.add(ControlPanelCSS.Content);
    };

    const wrapper = document.createElement(TagName.Div);
    contentCb(wrapper, false);

    const options = controlPanelFactory.options(wrapper);

    STATE.set(wrapper, { node, wrapper });

    return { widget: createDOMWidget(CustomWidgetName.controlPanel, wrapper, node, options) };
  },
  //#endregion

  //#region State
  state: STATE,
  //#endregion
};
