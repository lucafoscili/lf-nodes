import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelLabels,
  ControlPanelSection,
} from '../../types/widgets/controlPanel';
import { getLfManager } from '../../utils/common';
import { BUTTON_STYLE } from './styles';

//#region Build analytics section
export const buildAnalyticsSection: ControlPanelFixture['analytics'] = () => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { '--lf-icon-clear': clearIcon } = theme.get.current().variables;

  return {
    icon: ControlPanelIcons.Analytics,
    id: ControlPanelSection.Section,
    value: 'Analytics',
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: 'Usage',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              'Usage analytics can be enabled by saving datasets through the UpdateUsageStatistics node and displayed with the UsageStatistics node.',
          },
          {
            id: ControlPanelSection.Content,
            tagName: 'br',
            value: '',
          },
          {
            id: ControlPanelSection.Content,
            value:
              'Once datasets are created (input folder of ComfyUI), the count for each resource used will increase everytime that particular resource is updated.',
          },
          {
            id: ControlPanelSection.Content,
            tagName: 'br',
            value: '',
          },
          {
            id: ControlPanelSection.Content,
            value: 'This button will clear all usage analytics data from your input folder.',
          },
          {
            id: ControlPanelSection.Content,
            tagName: 'br',
            value: '',
          },
          {
            id: ControlPanelSection.Content,
            value: 'This action is IRREVERSIBLE so use it with caution.',
          },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfButton: {
                lfIcon: clearIcon,
                lfLabel: ControlPanelLabels.DeleteUsage,
                lfStyle: BUTTON_STYLE,
                lfStyling: 'outlined',
                lfUiState: 'danger',
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
