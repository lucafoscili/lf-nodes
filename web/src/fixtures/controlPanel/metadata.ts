import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelLabels,
  ControlPanelSection,
} from '../../types/widgets/controlPanel';
import { getLfManager } from '../../utils/common';
import { BUTTON_STYLE } from './styles';

//#region Build metadata section
export const buildMetadataSection: ControlPanelFixture['metadata'] = () => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { '--lf-icon-delete': deleteIcon } = theme.get.current().variables;

  return {
    icon: ControlPanelIcons.Metadata,
    id: ControlPanelSection.Section,
    value: 'Metadata',
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: 'Purge metadata files',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              'Metadata pulled from CivitAI are stored in .info files saved in the same folders of the models to avoid unnecessary fetches from the API.',
          },
          { id: ControlPanelSection.Content, tagName: 'div', value: '' },
          {
            id: ControlPanelSection.Content,
            value:
              "By pressing this button it's possible to delete every .info file created by fetching the metadata.",
          },
          { id: ControlPanelSection.Content, tagName: 'br', value: '' },
          {
            id: ControlPanelSection.Content,
            value: 'This action is IRREVERSIBLE so use it with caution.',
          },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfButton: {
                lfIcon: deleteIcon,
                lfLabel: ControlPanelLabels.DeleteMetadata,
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
