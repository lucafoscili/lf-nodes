import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelLabels,
  ControlPanelSection,
} from '../../types/widgets/controlPanel';
import { formatBytes, getLfManager } from '../../utils/common';
import { BUTTON_STYLE, STYLES } from './styles';

//#region Build external previews section
export const buildExternalPreviewsSection: ControlPanelFixture['external-previews'] = (stats?) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { '--lf-icon-delete': deleteIcon, '--lf-icon-refresh': refreshIcon } =
    theme.get.current().variables;
  const { progress } = theme.get.icons();

  const totalBytes = stats?.totalSizeBytes ?? 0;
  const fileCount = stats?.fileCount ?? 0;
  const maxBytes = 1024 * 1024 * 1024; // 1GB reference
  const percentage = Math.min((totalBytes / maxBytes) * 100, 100);

  return {
    icon: ControlPanelIcons.ExternalPreviews,
    id: ControlPanelSection.Section,
    value: 'External Previews',
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: 'Cache statistics',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              'External image previews are cached in the _lf_external_previews folder under ComfyUI/input to speed up loading.',
          },
          { id: ControlPanelSection.Content, tagName: 'br', value: '' },
          {
            id: ControlPanelSection.Content,
            value: '',
            children: [
              {
                id: 'cache-info',
                value: `Current cache: ${formatBytes(totalBytes)} (${fileCount} files)`,
                cssStyle: { display: 'block', marginBottom: '0.75em' },
              },
              {
                id: 'cache-progress',
                value: '',
                cells: {
                  lfProgressbar: {
                    lfIcon: progress,
                    lfLabel: `${formatBytes(totalBytes)} (${percentage.toFixed(1)}%)`,
                    shape: 'progressbar',
                    value: percentage,
                  },
                },
              },
            ],
          },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfButton: {
                lfIcon: refreshIcon,
                lfLabel: ControlPanelLabels.RefreshPreviewStats,
                lfStyle: BUTTON_STYLE,
                lfStyling: 'flat',
                shape: 'button',
                value: '',
              },
            },
          },
        ],
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: '',
      },
      {
        id: ControlPanelSection.Paragraph,
        value: 'Clear cache',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              'This button will permanently delete the entire preview cache folder and all its contents.',
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
                lfLabel: ControlPanelLabels.ClearPreviews,
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
