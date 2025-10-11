import { ControlPanelFixture, ControlPanelIds } from '../../types/widgets/controlPanel';
import { buildAnalyticsSection } from './analytics';
import { buildBackupSection } from './backup';
import { buildDebugSection } from './debug';
import { buildExternalPreviewsSection } from './externalPreviews';
import { buildGitHubSection } from './github';
import { buildMetadataSection } from './metadata';
import { buildSystemDashboardSection } from './systemDashboard';
import { buildThemeSection } from './theme';

export const SECTIONS: ControlPanelFixture = {
  [ControlPanelIds.Analytics]: buildAnalyticsSection,
  [ControlPanelIds.Backup]: buildBackupSection,
  [ControlPanelIds.Debug]: buildDebugSection,
  [ControlPanelIds.ExternalPreviews]: buildExternalPreviewsSection,
  [ControlPanelIds.GitHub]: buildGitHubSection,
  [ControlPanelIds.Metadata]: buildMetadataSection,
  [ControlPanelIds.SystemDashboard]: buildSystemDashboardSection,
  [ControlPanelIds.Theme]: buildThemeSection,
};

export { BUTTON_STYLE, STYLES } from './styles';
