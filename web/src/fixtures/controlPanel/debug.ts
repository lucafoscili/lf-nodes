import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelLabels,
  ControlPanelSection,
} from '../../types/widgets/controlPanel';
import { getLfManager } from '../../utils/common';
import { BUTTON_STYLE, STYLES } from './styles';

//#region Build debug section
export const buildDebugSection: ControlPanelFixture['debug'] = (logsData) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { '--lf-icon-clear': clearIcon } = theme.get.current().variables;

  return {
    icon: ControlPanelIcons.Debug,
    id: ControlPanelSection.Section,
    cssStyle: STYLES.debugGrid(),
    value: 'Debug',
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: 'Toggle on/off',
        children: [
          {
            id: ControlPanelSection.Content,
            value: 'Activating the debug will enable the display of verbose logging.',
          },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfToggle: {
                lfLabel: ControlPanelLabels.Debug,
                lfLeadingLabel: true,
                lfStyle: ':host { text-align: center; padding: 1em 0; }',
                shape: 'toggle',
                value: !!getLfManager().isDebug(),
              },
            },
          },
        ],
      },
      {
        id: ControlPanelSection.Paragraph,
        value: 'Logs',
        children: [
          {
            id: ControlPanelSection.Content,
            value: 'Every time the node manager receives a message it will be printed below.',
          },
          { id: ControlPanelSection.Content, tagName: 'br', value: '' },
          {
            id: ControlPanelSection.Content,
            value: 'In the browser console there should be more informations.',
          },
          { id: ControlPanelSection.Content, tagName: 'br', value: '' },
          {
            id: ControlPanelSection.Content,
            value: 'Further below another card will display additional LF Widgets information.',
          },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfButton: {
                shape: 'button',
                lfIcon: clearIcon,
                lfLabel: ControlPanelLabels.ClearLogs,
                lfStretchX: true,
                lfStyle: BUTTON_STYLE,
                lfUiState: 'danger',
                value: '',
              },
            },
          },
        ],
      },
      {
        id: ControlPanelSection.Paragraph,
        cssStyle: STYLES.debugLogs(),
        value: '',
        children: [
          {
            id: 'content-wrapper',
            cssStyle: STYLES.logsArea(),
            value: '',
            children: logsData,
          },
          {
            id: 'content-wrapper',
            value: '',
            cells: {
              lfCard: {
                lfDataset: {
                  nodes: [
                    {
                      cells: {
                        lfCode: { shape: 'code', value: '' },
                        lfButton: { shape: 'button', value: '' },
                        lfButton_2: { shape: 'button', value: '' },
                        lfToggle: {
                          shape: 'toggle',
                          value: !!getLfManager().getManagers().lfFramework.debug.isEnabled(),
                        },
                      },
                      id: 'debug',
                    },
                  ],
                },
                lfLayout: 'debug',
                shape: 'card',
                value: '',
              },
            },
          },
        ],
      },
    ],
  };
};
//#endregion
