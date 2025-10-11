import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelLabels,
  ControlPanelSection,
} from '../../types/widgets/controlPanel';
import { getLfManager } from '../../utils/common';
import { BUTTON_STYLE, STYLES } from './styles';

//#region Build GitHub section
export const buildGitHubSection: ControlPanelFixture['github'] = () => {
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
              { id: ControlPanelSection.Content, tagName: 'br', value: '' },
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
};
//#endregion
