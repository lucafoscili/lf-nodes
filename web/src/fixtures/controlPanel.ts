import { LfArticleNode } from '@lf-widgets/foundations';
import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelIds,
  ControlPanelLabels,
  ControlPanelSection,
  ControlPanelSystemStats,
} from '../types/widgets/controlPanel';
import { getLfManager, getLfThemes } from '../utils/common';

//#region Styles
const BUTTON_STYLE = ':host { margin: auto; padding: 1em 0; width: max-content; }';
const STYLES = {
  customization: () => {
    return {
      margin: '0',
    };
  },
  debugGrid: () => {
    return {
      display: 'grid',
      gridTemplateRows: 'repeat(5, max-content) 1fr',
      height: '100%',
      margin: '0',
    };
  },
  debugLogs: () => {
    return {
      display: 'grid',
      gridGap: '0.75em',
      gridTemplateRows: '320px 480px',
    };
  },
  logsArea: () => {
    return {
      backgroundColor: 'rgba(var(--lf-color-on-bg), 0.075)',
      borderRadius: '0.5em',
      display: 'block',
      height: '100%',
      marginBottom: '1em',
      overflow: 'auto',
    };
  },
  separator: () => {
    return {
      border: '1px solid rgb(var(--lf-color-border))',
      display: 'block',
      margin: '0.75em auto 1.25em',
      opacity: '0.25',
      width: '50%',
    };
  },
};
//#endregion

export const SECTIONS: ControlPanelFixture = {
  //#region Analytics
  [ControlPanelIds.Analytics]: (): LfArticleNode => {
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
  },
  //#endregion

  //#region Backup
  [ControlPanelIds.Backup]: (stats?: {
    totalSizeBytes: number;
    fileCount: number;
  }): LfArticleNode => {
    const { theme } = getLfManager().getManagers().lfFramework;
    const { '--lf-icon-download': downloadIcon, '--lf-icon-refresh': refreshIcon } =
      theme.get.current().variables;
    const { progress } = theme.get.icons();

    const totalBytes = stats?.totalSizeBytes ?? 0;
    const fileCount = stats?.fileCount ?? 0;

    // Convert bytes to human-readable format
    const formatBytes = (bytes: number): string => {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
    };

    // Calculate percentage (assuming 1GB max for visualization)
    const maxBytes = 1024 * 1024 * 1024; // 1GB
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
            {
              id: ControlPanelSection.Content,
              tagName: 'br',
              value: '',
            },
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
            {
              id: ControlPanelSection.Content,
              tagName: 'br',
              value: '',
            },
            {
              id: ControlPanelSection.Content,
              value: '',
              children: [
                {
                  id: 'backup-info',
                  value: `Current backup: ${formatBytes(totalBytes)} (${fileCount} files)`,
                  cssStyle: {
                    display: 'block',
                    marginBottom: '0.75em',
                  },
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
            {
              id: ControlPanelSection.Content,
              tagName: 'br',
              value: '',
            },
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
  },
  //#endregion

  //#region Debug
  [ControlPanelIds.Debug]: (logsData: LfArticleNode[]): LfArticleNode => {
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
            {
              id: ControlPanelSection.Content,
              tagName: 'br',
              value: '',
            },
            {
              id: ControlPanelSection.Content,
              value: 'In the browser console there should be more informations.',
            },
            {
              id: ControlPanelSection.Content,
              tagName: 'br',
              value: '',
            },
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
              cells: {
                lfCard: {
                  lfDataset: {
                    nodes: [
                      {
                        cells: {
                          lfCode: { shape: 'code', value: '' },
                          lfButton: {
                            shape: 'button',
                            value: '',
                          },
                          lfButton_2: {
                            shape: 'button',
                            value: '',
                          },
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
              id: 'content-wrapper',
            },
          ],
        },
      ],
    };
  },
  //#endregion

  //#region ExternalPreviews
  [ControlPanelIds.ExternalPreviews]: (stats?: {
    totalSizeBytes: number;
    fileCount: number;
  }): LfArticleNode => {
    const { theme } = getLfManager().getManagers().lfFramework;
    const { '--lf-icon-delete': deleteIcon, '--lf-icon-refresh': refreshIcon } =
      theme.get.current().variables;
    const { progress } = theme.get.icons();

    const totalBytes = stats?.totalSizeBytes ?? 0;
    const fileCount = stats?.fileCount ?? 0;

    // Convert bytes to human-readable format
    const formatBytes = (bytes: number): string => {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
    };

    // Calculate percentage (assuming 1GB max for visualization)
    const maxBytes = 1024 * 1024 * 1024; // 1GB
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
            {
              id: ControlPanelSection.Content,
              tagName: 'br',
              value: '',
            },
            {
              id: ControlPanelSection.Content,
              value: '',
              children: [
                {
                  id: 'cache-info',
                  value: `Current cache: ${formatBytes(totalBytes)} (${fileCount} files)`,
                  cssStyle: {
                    display: 'block',
                    marginBottom: '0.75em',
                  },
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
  },
  //#endregion

  //#region GitHub
  [ControlPanelIds.GitHub]: (): LfArticleNode => {
    const lfManager = getLfManager();
    const releaseData = lfManager.getLatestRelease();
    const { theme } = lfManager.getManagers().lfFramework;
    const { brandGithub } = theme.get.icons();

    return {
      icon: ControlPanelIcons.GitHub,
      id: ControlPanelSection.Section,
      value: '',
      children: [
        {
          id: ControlPanelSection.Paragraph,
          value: `Version: ${releaseData?.tag_name || 'N/A'}`,
          children: [
            {
              cells: {
                lfCode: {
                  lfLanguage: 'markdown',
                  shape: 'code',
                  value: releaseData?.body || 'No changelog available',
                },
              },
              id: 'release-description',
            },
            {
              id: 'release-author',
              children: [
                {
                  id: 'author-avatar',
                  value: '',
                  cssStyle: {
                    backgroundImage: `url(${releaseData?.author?.avatar_url || ''})`,
                    backgroundSize: 'cover',
                    borderRadius: '50%',
                    display: 'inline-block',
                    height: '2em',
                    marginRight: '0.5em',
                    verticalAlign: 'middle',
                    width: '2em',
                  },
                },
                {
                  id: 'author-name',
                  value: `Author: ${releaseData?.author?.login || 'Unknown'}`,
                  cssStyle: {
                    fontSize: '0.9em',
                    color: 'rgb(var(--lf-color-secondary))',
                    verticalAlign: 'middle',
                  },
                },
              ],
              cssStyle: {
                alignItems: 'center',
                display: 'flex',
                justifyContent: 'center',
                marginBottom: '.25em',
              },
            },
            {
              cssStyle: {
                color: 'rgb(var(--lf-color-secondary))',
                display: 'block',
                fontSize: '0.9em',
                fontStyle: 'italic',
                marginBottom: '2em',
                textAlign: 'center',
                width: '100%',
              },
              id: 'release-date',
              value: `Published on: ${
                releaseData?.published_at
                  ? new Date(releaseData.published_at).toLocaleDateString()
                  : 'Unknown'
              }`,
            },
            {
              cssStyle: STYLES.separator(),
              id: ControlPanelSection.ContentSeparator,
              value: '',
            },
            {
              id: ControlPanelSection.Paragraph,
              value: 'Bug report',
              children: [
                {
                  id: ControlPanelSection.Content,
                  value:
                    'If you find bugs or odd behaviors feel free to open an issue on GitHub, just follow the link below!',
                },
                {
                  id: ControlPanelSection.Content,
                  tagName: 'br',
                  value: '',
                },
                {
                  id: ControlPanelSection.Content,
                  value:
                    "Be sure to include as much information as you can, without sufficient data it's difficult to troubleshoot problems.",
                },
                {
                  id: ControlPanelSection.Content,
                  value: '',
                  cells: {
                    lfButton: {
                      lfIcon: brandGithub,
                      lfLabel: ControlPanelLabels.OpenIssue,
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
        },
      ],
    };
  },
  //#endregion

  //#region Metadata
  [ControlPanelIds.Metadata]: (): LfArticleNode => {
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
  },
  //#endregion

  //#region SystemDashboard
  [ControlPanelIds.SystemDashboard]: (stats?: ControlPanelSystemStats): LfArticleNode => {
    const { theme } = getLfManager().getManagers().lfFramework;
    const { '--lf-icon-refresh': refreshIcon } = theme.get.current().variables;
    const { progress } = theme.get.icons();

    const clampPercent = (value: number = 0) => {
      if (Number.isNaN(value)) {
        return 0;
      }

      return Math.min(100, Math.max(0, value || 0));
    };
    const getUsageState = (percent: number) => {
      const value = clampPercent(percent);

      if (value >= 90) {
        return 'danger';
      }
      if (value >= 70) {
        return 'warning';
      }
      if (value == 0) {
        return 'primary';
      }
      return 'success';
    };
    const percentLabel = (value: number) => `${clampPercent(value).toFixed(1)}%`;
    const formatBytes = (bytes: number): string => {
      if (!bytes) {
        return '0 B';
      }

      const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
      let value = bytes;
      let index = 0;
      while (value >= 1024 && index < units.length - 1) {
        value /= 1024;
        index += 1;
      }
      const decimals = value >= 10 || index === 0 ? 1 : 2;

      return `${value.toFixed(decimals)} ${units[index]}`;
    };
    const createProgressNode = (id: string, label: string, percent: number): LfArticleNode => ({
      id,
      value: '',
      cells: {
        lfProgressbar: {
          lfIcon: progress,
          lfLabel: label,
          lfUiState: getUsageState(percent),
          shape: 'progressbar',
          value: clampPercent(percent) || 0,
        },
      },
    });

    const gpus = stats?.gpus ?? [];
    const disks = stats?.disks ?? [];
    const cpu = stats?.cpu;
    const ram = stats?.ram;
    const errors = stats?.errors ?? [];
    const timestamp = stats?.timestamp ? new Date(stats.timestamp) : null;
    const lastUpdated = timestamp ? timestamp.toLocaleString() : 'Waiting for data';

    const gpuNodes: LfArticleNode[] = gpus.length
      ? gpus.map((gpu) => {
          const vramPercent = gpu.vram_total ? (gpu.vram_used / gpu.vram_total) * 100 : 0;
          const utilPercent = gpu.utilization ?? 0;
          return {
            id: `gpu-${gpu.index}`,
            value: '',
            cssStyle: {
              marginBottom: '1em',
            },
            children: [
              {
                id: `gpu-${gpu.index}-title`,
                value: `${gpu.name} (GPU ${gpu.index})`,
                tagName: 'strong',
              },
              createProgressNode(
                `gpu-${gpu.index}-vram`,
                `VRAM ${formatBytes(gpu.vram_used)} / ${formatBytes(
                  gpu.vram_total,
                )} (${percentLabel(vramPercent)})`,
                vramPercent,
              ),
              createProgressNode(
                `gpu-${gpu.index}-util`,
                `Utilization ${percentLabel(utilPercent)}`,
                utilPercent,
              ),
            ],
          };
        })
      : [
          {
            id: 'gpu-none',
            value: 'No GPUs detected.',
            cssStyle: {
              opacity: '0.7',
            },
          },
        ];

    const cpuNodes: LfArticleNode[] = cpu
      ? [
          createProgressNode(
            'cpu-average',
            `Average usage ${percentLabel(cpu.average)}`,
            cpu.average,
          ),
          {
            id: 'cpu-meta',
            value: `Logical cores: ${cpu.count} • Physical cores: ${cpu.physical_count}`,
            cssStyle: {
              fontSize: '0.9em',
              opacity: '0.8',
            },
          },
          {
            id: 'cpu-cores',
            value: '',
            cssStyle: {
              display: 'grid',
              gap: '0.75em',
              gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            },
            children: cpu.cores.map((core) =>
              createProgressNode(
                `cpu-core-${core.index}`,
                `Core ${core.index} ${percentLabel(core.usage)}`,
                core.usage,
              ),
            ),
          },
        ]
      : [
          {
            id: 'cpu-none',
            value: 'CPU statistics unavailable.',
            cssStyle: {
              opacity: '0.7',
            },
          },
        ];

    const ramNodes: LfArticleNode[] = ram
      ? [
          createProgressNode(
            'ram-usage',
            `RAM ${formatBytes(ram.used)} / ${formatBytes(ram.total)} (${percentLabel(
              ram.percent,
            )})`,
            ram.percent,
          ),
          {
            id: 'ram-available',
            value: `Available: ${formatBytes(ram.available)}`,
            cssStyle: {
              fontSize: '0.9em',
              opacity: '0.8',
            },
          },
          ...(ram.swap_total
            ? [
                createProgressNode(
                  'swap-usage',
                  `Swap ${formatBytes(ram.swap_used)} / ${formatBytes(
                    ram.swap_total,
                  )} (${percentLabel(
                    ram.swap_total ? (ram.swap_used / ram.swap_total) * 100 : 0,
                  )})`,
                  ram.swap_total ? (ram.swap_used / ram.swap_total) * 100 : 0,
                ),
              ]
            : []),
        ]
      : [
          {
            id: 'ram-none',
            value: 'RAM statistics unavailable.',
            cssStyle: {
              opacity: '0.7',
            },
          },
        ];

    const diskNodes: LfArticleNode[] = disks.length
      ? disks.map((disk, index) => {
          const percent = disk.total ? (disk.used / disk.total) * 100 : disk.percent;

          return {
            id: `disk-${index}`,
            value: '',
            cssStyle: {
              marginBottom: '1em',
            },
            children: [
              {
                cells: {
                  lfChip: {
                    lfAriaLabel: `Disk ${disk.device || disk.mountpoint} ${disk.label}`,
                    lfDataset: {
                      nodes: [
                        { id: `disk-${index}-device`, value: `${disk.device || disk.mountpoint}` },
                        { id: `disk-${index}-label`, value: `${disk.label}` },
                      ],
                    },
                    lfStyle: ':host { width: max-content; }',
                    lfUiSize: 'small',
                    shape: 'chip',
                    value: '',
                  },
                },
                id: `disk-${index}-mount`,
                value: ``,
                cssStyle: {
                  fontSize: '0.9em',
                  opacity: '0.8',
                  marginBottom: '0.25em',
                },
              },
              createProgressNode(
                `disk-${index}-usage`,
                `${formatBytes(disk.used)} / ${formatBytes(disk.total)} (${percentLabel(percent)})`,
                percent,
              ),
            ],
          };
        })
      : [
          {
            id: 'disk-none',
            value: 'No disks detected.',
            cssStyle: {
              opacity: '0.7',
            },
          },
        ];

    const errorNodes: LfArticleNode[] = errors.map((error, index) => ({
      id: `system-error-${index}`,
      value: error,
      cssStyle: {
        color: 'rgb(var(--lf-color-danger))',
        fontSize: '0.85em',
      },
    }));

    const overviewChildren: LfArticleNode[] = [
      {
        id: ControlPanelSection.Content,
        value: 'Monitor real-time hardware usage for GPUs, CPU, memory, and storage.',
      },
      {
        id: ControlPanelSection.Content,
        value: `Last updated: ${lastUpdated}`,
        cssStyle: {
          fontSize: '0.85em',
          opacity: '0.75',
        },
      },
      {
        id: ControlPanelSection.Content,
        value:
          stats?.autoRefreshSeconds && stats.autoRefreshSeconds > 0
            ? `Auto refresh every ${stats.autoRefreshSeconds}s`
            : 'Auto refresh disabled.',
        cssStyle: {
          fontSize: '0.85em',
          opacity: '0.75',
          marginTop: '0.3em',
        },
      },
      {
        id: ControlPanelSection.Content,
        value: '',
        cells: {
          lfTextfield: {
            lfHelper: { showWhenFocused: false, value: 'Set to 0 to disable auto refresh' },
            lfHtmlAttributes: { type: 'number', min: '0', step: 'any' },
            lfLabel: ControlPanelLabels.SystemAutoRefresh,
            lfStyle: ':host { display: block; margin: 0.75em auto; max-width: 240px; }',
            lfValue:
              stats?.autoRefreshSeconds !== undefined && stats.autoRefreshSeconds > 0
                ? String(stats.autoRefreshSeconds)
                : '',
            shape: 'textfield',
            value: '',
          },
        },
      },
    ];

    if (errorNodes.length) {
      overviewChildren.push({
        id: 'system-errors',
        value: '',
        children: errorNodes,
      });
    }

    overviewChildren.push({
      id: ControlPanelSection.Content,
      value: '',
      cells: {
        lfButton: {
          lfIcon: refreshIcon,
          lfLabel: ControlPanelLabels.RefreshSystemStats,
          lfStyle: BUTTON_STYLE,
          lfStyling: 'flat',
          shape: 'button',
          value: '',
        },
      },
    });

    return {
      icon: ControlPanelIcons.SystemDashboard,
      id: ControlPanelSection.Section,
      value: 'System monitor',
      children: [
        {
          id: ControlPanelSection.Paragraph,
          value: 'Overview',
          children: overviewChildren,
        },
        {
          cssStyle: STYLES.separator(),
          id: ControlPanelSection.ContentSeparator,
          value: '',
        },
        {
          id: ControlPanelSection.Paragraph,
          value: 'GPU usage',
          children: gpuNodes,
        },
        {
          cssStyle: STYLES.separator(),
          id: ControlPanelSection.ContentSeparator,
          value: '',
        },
        {
          id: ControlPanelSection.Paragraph,
          value: 'CPU usage',
          children: cpuNodes,
        },
        {
          cssStyle: STYLES.separator(),
          id: ControlPanelSection.ContentSeparator,
          value: '',
        },
        {
          id: ControlPanelSection.Paragraph,
          value: 'Memory',
          children: ramNodes,
        },
        {
          cssStyle: STYLES.separator(),
          id: ControlPanelSection.ContentSeparator,
          value: '',
        },
        {
          id: ControlPanelSection.Paragraph,
          value: 'Disk usage',
          children: diskNodes,
        },
      ],
    };
  },
  //#endregion

  //#region Theme
  [ControlPanelIds.Theme]: (): LfArticleNode => {
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
  },
  //#endregion
};
