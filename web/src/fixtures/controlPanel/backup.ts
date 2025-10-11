import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelLabels,
  ControlPanelSection,
} from '../../types/widgets/controlPanel';
import { formatBytes, getLfManager } from '../../utils/common';
import { BUTTON_STYLE, STYLES } from './styles';

//#region Build backup section
export const buildBackupSection: ControlPanelFixture['backup'] = (stats?) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { '--lf-icon-download': downloadIcon, '--lf-icon-refresh': refreshIcon } =
    theme.get.current().variables;
  const { progress } = theme.get.icons();

  const totalBytes = stats?.totalSizeBytes ?? 0;
  const fileCount = stats?.fileCount ?? 0;
  const maxBytes = 1024 * 1024 * 1024; // 1GB reference
  const percentage = Math.min((totalBytes / maxBytes) * 100, 100);

  return {
    icon: ControlPanelIcons.Backup,
    id: ControlPanelSection.Section,
    value: 'Backup',
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: 'Toggle on/off',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              'Toggle this toggle to automatically back up the folder <path/to/your/comfyui/user/LF_Nodes> once a day (the first time you open this workflow).',
          },
          { id: ControlPanelSection.Content, tagName: 'br', value: '' },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfToggle: {
                lfLabel: ControlPanelLabels.AutoBackup,
                lfLeadingLabel: true,
                lfStyle: ':host { text-align: center; padding: 1em 0; }',
                shape: 'toggle',
                value: !!getLfManager().isBackupEnabled(),
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
        value: 'Backup statistics',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              'Backup files are stored in the user/LF_Nodes folder. Monitor your backup folder size to ensure you have enough disk space.',
          },
          { id: ControlPanelSection.Content, tagName: 'br', value: '' },
          {
            id: ControlPanelSection.Content,
            value: '',
            children: [
              {
                id: 'backup-info',
                value: `Current backup: ${formatBytes(totalBytes)} (${fileCount} files)`,
                cssStyle: { display: 'block', marginBottom: '0.75em' },
              },
              {
                id: 'backup-progress',
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
                lfLabel: ControlPanelLabels.RefreshBackupStats,
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
        value: 'Rolling backup retention',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              'Set the maximum number of backups to keep. When this limit is exceeded, the oldest backups will be automatically deleted. Set to 0 to disable this feature.',
          },
          { id: ControlPanelSection.Content, tagName: 'br', value: '' },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfTextfield: {
                lfHtmlAttributes: { type: 'number' },
                lfLabel: ControlPanelLabels.BackupRetention,
                lfStyle: ':host { text-align: center; padding: 1em 0; }',
                lfValue: getLfManager().getBackupRetention().toString() || '14',
                shape: 'textfield',
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
        value: 'Backup files',
        children: [
          {
            id: ControlPanelSection.Content,
            value:
              'This button will create a manual backup of the content in <path/to/your/comfyui/user/LF_Nodes>.',
          },
          {
            id: ControlPanelSection.Content,
            value: '',
            cells: {
              lfButton: {
                lfIcon: downloadIcon,
                lfLabel: ControlPanelLabels.Backup,
                lfStyle: BUTTON_STYLE,
                lfStyling: 'raised',
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
