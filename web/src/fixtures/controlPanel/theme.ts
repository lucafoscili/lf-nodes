import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelLabels,
  ControlPanelSection,
} from '../../types/widgets/controlPanel';
import { getLfThemes } from '../../utils/common';
import { BUTTON_STYLE, STYLES } from './styles';

//#region Build theme section
export const buildThemeSection: ControlPanelFixture['theme'] = () => {
  return {
    icon: ControlPanelIcons.Theme,
    id: ControlPanelSection.Section,
    value: 'Customization',
    cssStyle: STYLES.customization(),
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: 'Theme selector',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              "Through the button below it's possible to set a random theme for the LF Widgets components, or select one from the dropdown menu.",
          },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfButton: {
                lfDataset: getLfThemes(),
                lfLabel: ControlPanelLabels.Theme,
                lfStyle: BUTTON_STYLE,
                shape: 'button',
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
