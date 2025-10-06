import { LfArticleNode } from '@lf-widgets/foundations';
import {
  BaseWidgetState,
  CustomWidgetName,
  NormalizeValueCallback,
  WidgetFactory,
} from './widgets';

//#region CSS
const BASE_CSS_CLASS = 'lf-controlpanel';
export enum ControlPanelCSS {
  Content = BASE_CSS_CLASS,
  Grid = `${BASE_CSS_CLASS}__grid`,
  Spinner = `${BASE_CSS_CLASS}__spinner`,
}
//#endregion

//#region Control panel
export type ControlPanel = Widget<CustomWidgetName.controlPanel>;
export type ControlPanelFactory = WidgetFactory<ControlPanelDeserializedValue, ControlPanelState>;
export type ControlPanelNormalizeCallback = NormalizeValueCallback<
  ControlPanelDeserializedValue | string
>;
//#endregion

//#region Value
export type ControlPanelDeserializedValue = {
  backup: boolean;
  backupRetention: number;
  debug: boolean;
  themes: string;
};
//#endregion

//#region State
export interface ControlPanelState extends BaseWidgetState {}
//#endregion

//#region Dataset
export interface ControlPanelFixture {
  [ControlPanelIds.Analytics]: () => LfArticleNode;
  [ControlPanelIds.Backup]: (stats?: {
    totalSizeBytes: number;
    fileCount: number;
  }) => LfArticleNode;
  [ControlPanelIds.Debug]: (logsData: LfArticleNode[]) => LfArticleNode;
  [ControlPanelIds.ExternalPreviews]: (stats?: {
    totalSizeBytes: number;
    fileCount: number;
  }) => LfArticleNode;
  [ControlPanelIds.GitHub]: () => LfArticleNode;
  [ControlPanelIds.Metadata]: () => LfArticleNode;
  [ControlPanelIds.Theme]: () => LfArticleNode;
}
export enum ControlPanelIcons {
  Analytics = 'chart-histogram',
  Backup = 'download',
  Debug = 'bug',
  ExternalPreviews = 'photo-search',
  GitHub = 'brand-github',
  Metadata = 'info-hexagon',
  Theme = 'color-swatch',
}
export enum ControlPanelIds {
  Analytics = 'analytics',
  Backup = 'backup',
  Debug = 'debug',
  ExternalPreviews = 'external-previews',
  GitHub = 'github',
  Metadata = 'metadata',
  Theme = 'theme',
}
export enum ControlPanelLabels {
  AutoBackup = 'Automatic Backup',
  Backup = 'Backup now',
  BackupRetention = 'Maximum backups to keep',
  ClearLogs = 'Clear logs',
  ClearPreviews = 'Clear preview cache',
  Debug = 'Debug',
  DeleteUsage = 'Delete usage analytics info',
  DeleteMetadata = 'Delete models info',
  Done = 'Done!',
  OpenIssue = 'Open an issue',
  RefreshBackupStats = 'Refresh backup stats',
  RefreshPreviewStats = 'Refresh preview stats',
  Theme = 'Random theme',
}
export enum ControlPanelSection {
  Content = 'content',
  ContentSeparator = 'content_spearator',
  Paragraph = 'paragraph',
  Root = 'root',
  Section = 'section',
}
//#endregion
