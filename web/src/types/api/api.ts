import { LfDataDataset } from '@lf-widgets/foundations';
import { EventName, GenericEvent } from '../events/events';
import { Extension, LogSeverity } from '../manager/manager';
import { ImageEditorFilterType, ImageEditorRequestSettings } from '../widgets/imageEditor';

//#region API
export interface APIRoutes {
  analytics: AnalyticsAPIs;
  backup: BackupAPIs;
  comfy: ComfyAPIs;
  models: ModelsAPIs;
  github: GitHubAPIs;
  image: ImageAPIs;
  json: JSONAPIs;
  metadata: MetadataAPIs;
  preview: PreviewAPIs;
}
export type AnalyticsType = 'usage';
export interface AnalyticsAPIs {
  clear: (type: AnalyticsType) => Promise<BaseAPIPayload>;
  get: (dir: string, type: AnalyticsType) => Promise<GetAnalyticsAPIPayload>;
}
export type BackupType = 'automatic' | 'manual';
export interface BackupInfo {
  name: string;
  type: string;
  timestamp: string;
  sizeBytes: number;
  fileCount: number;
  path: string;
}
export interface BackupAPIs {
  new: (backupType?: BackupType) => Promise<BaseAPIPayload>;
  getStats: () => Promise<GetBackupStatsAPIPayload>;
  cleanOld: (maxBackups?: number) => Promise<BaseAPIPayload>;
}
export type ComfyURLType = 'input' | 'output' | 'temp';
export interface ComfyAPIs {
  comfyUi: () => ComfyUI;
  event: (name: EventName, callback: (e: GenericEvent) => void) => void;
  executeCommand: (name: ComfyUICommands) => void;
  getDragAndScale: () => ComfyDS;
  getLinkById: (id: string) => LinkInfo;
  getNodeById: (id: string) => NodeType;
  getResourceUrl: (subfolder: string, filename: string, type: ComfyURLType) => void;
  interrupt: () => void;
  queuePrompt: () => Promise<void>;
  redraw: () => void;
  redrawFull: () => void;
  scheduleRedraw: (immediate?: boolean) => void;
  register: (extension: Extension) => void;
  upload: (body: FormData) => Promise<Response>;
}
export interface GitHubAPIs {
  getLatestRelease: () => Promise<GetGitHubLatestReleaseAPIPayload>;
}
export interface ModelsAPIs {
  free: () => Promise<boolean>;
  refresh: () => Promise<boolean>;
}
export interface ImageAPIs {
  get: (dir: string) => Promise<GetImageAPIPayload>;
  process: <T extends ImageEditorFilterType>(
    url: string,
    type: T,
    settings: ImageEditorRequestSettings<T>,
  ) => Promise<ProcessImageAPIPayload>;
  explore: (
    directory: string,
    options?: ImageExplorerRequestOptions,
  ) => Promise<GetFilesystemAPIPayload>;
}
export interface JSONAPIs {
  get: (path: string) => Promise<GetJSONAPIPayload>;
  update: (path: string, dataset: LfDataDataset) => Promise<BaseAPIPayload>;
}
export interface APIMetadataEntry {
  apiFlag: boolean;
  dataset: LfDataDataset;
  hash: string;
  path: string;
}
export interface MetadataAPIs {
  clear: () => Promise<BaseAPIPayload>;
  get: (hash: string) => Promise<GetMetadataAPIPayload>;
  save: (
    modelPath: string,
    dataset: LfDataDataset,
    forcedSave?: boolean,
  ) => Promise<BaseAPIPayload>;
  updateCover: (modelPath: string, b64image: string) => Promise<BaseAPIPayload>;
}
export interface PreviewAPIs {
  clearCache: () => Promise<BaseAPIPayload>;
  getStats: () => Promise<GetPreviewStatsAPIPayload>;
}
//#endregion

//#region Payloads
export interface BaseAPIPayload {
  message: string;
  status: LogSeverity;
}
export interface GetAnalyticsAPIPayload extends BaseAPIPayload {
  data: Record<string, LfDataDataset>;
}
export interface GetGitHubLatestReleaseAPIPayload extends BaseAPIPayload {
  data: GitHubRelease;
}
export interface GetImageAPIPayload extends BaseAPIPayload {
  data: LfDataDataset;
}
export interface GetFilesystemAPIPayload extends BaseAPIPayload {
  data: {
    dataset?: LfDataDataset;
    tree?: (LfDataDataset & { parent_id?: string }) | null;
  };
}
export interface GetJSONAPIPayload extends BaseAPIPayload {
  data: LfDataDataset;
}
export interface GetMetadataAPIPayload extends BaseAPIPayload {
  data: CivitAIModelData;
}
export interface ProcessImageAPIPayload extends BaseAPIPayload {
  data: string;
  mask?: string;
  cutout?: string;
  stats?: Record<string, unknown>;
}
export interface GetPreviewStatsAPIPayload extends BaseAPIPayload {
  data: {
    total_size_bytes: number;
    file_count: number;
    path: string;
  };
}
export interface GetBackupStatsAPIPayload extends BaseAPIPayload {
  data: {
    total_size_bytes: number;
    file_count: number;
    backups: BackupInfo[];
  };
}

export type ImageExplorerScope = 'all' | 'dataset' | 'tree' | 'roots';
export interface ImageExplorerRequestOptions {
  scope?: ImageExplorerScope;
  nodePath?: string;
}
//#endregion

//#region Routes
export enum APIEndpoints {
  ClearAnalytics = `/lf-nodes/clear-analytics`,
  ClearMetadata = `/lf-nodes/clear-metadata`,
  ClearPreviewCache = `/lf-nodes/clear-preview-cache`,
  LFFree = `/lf-nodes/free`,
  LFRefreshNodeDefs = `/lf-nodes/refresh-node-defs`,
  GetAnalytics = `/lf-nodes/get-analytics`,
  GetImage = `/lf-nodes/get-image`,
  ExploreFilesystem = `/lf-nodes/explore-filesystem`,
  GetJson = `/lf-nodes/get-json`,
  GetMetadata = `/lf-nodes/get-metadata`,
  GetPreviewStats = `/lf-nodes/get-preview-stats`,
  GetBackupStats = `/lf-nodes/get-backup-stats`,
  NewBackup = `/lf-nodes/new-backup`,
  CleanOldBackups = `/lf-nodes/clean-old-backups`,
  ProcessImage = `/lf-nodes/process-image`,
  SaveMetadata = '/lf-nodes/save-metadata',
  UpdateJson = `/lf-nodes/update-json`,
  UpdateMetadataCover = '/lf-nodes/update-metadata-cover',
}
//#endregion
