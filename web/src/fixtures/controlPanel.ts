import { LfArticleNode } from '@lf-widgets/foundations';
import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelIds,
  ControlPanelLabels,
  ControlPanelSection,
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
  [ControlPanelIds.Backup]: (): LfArticleNode => {
    const { theme } = getLfManager().getManagers().lfFramework;
    const { '--lf-icon-download': downloadIcon } = theme.get.current().variables;

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
                } as any,
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
                'This button will create a manual backup of the content in <path/to/your/comfyui/user/LF_Nodes>',
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
                marginBottom: '1em',
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
                "Through the button below it's possible to set a random theme for the Ketchup Lite components, or select one from the dropdown menu.",
            },
            {
              id: ControlPanelSection.Content,
              value: '',
              cells: {
                lfButton: {
                  lfDataset: getLfThemes(),
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
