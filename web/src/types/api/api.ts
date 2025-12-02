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
  system: SystemAPIs;
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
  getSamplers: () => Promise<LfDataDataset>;
  getSchedulers: () => Promise<LfDataDataset>;
  refresh: () => Promise<boolean>;
}
export interface ImageAPIs {
  get: (dir: string) => Promise<GetImageAPIPayload>;
  explore: (
    directory: string,
    options?: ImageExplorerRequestOptions,
  ) => Promise<GetFilesystemAPIPayload>;
  process: <T extends ImageEditorFilterType>(
    url: string,
    type: T,
    settings: ImageEditorRequestSettings<T>,
  ) => Promise<ProcessImageAPIPayload>;
  upload: (file: File | Blob, directory?: ComfyURLType) => Promise<UploadImageAPIPayload>;
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
export interface SystemAPIs {
  getGpuStats: () => Promise<GetGpuStatsAPIPayload>;
  getDiskStats: () => Promise<GetDiskStatsAPIPayload>;
  getCpuStats: () => Promise<GetCpuStatsAPIPayload>;
  getRamStats: () => Promise<GetRamStatsAPIPayload>;
}
export type APIUploadDirectory = 'input' | 'output' | 'temp';
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
export interface GPUInfo {
  name: string;
  index: number;
  vram_used: number;
  vram_total: number;
  utilization: number;
}
export interface DiskInfo {
  device: string;
  mountpoint: string;
  label: string;
  used: number;
  total: number;
  percent: number;
}
export interface CpuCoreInfo {
  index: number;
  usage: number;
}
export interface CpuStats {
  cores: CpuCoreInfo[];
  average: number;
  count: number;
  physical_count: number;
}
export interface RamStats {
  used: number;
  total: number;
  available: number;
  percent: number;
  swap_used: number;
  swap_total: number;
}
export interface GetGpuStatsAPIPayload extends BaseAPIPayload {
  data: GPUInfo[];
}
export interface GetDiskStatsAPIPayload extends BaseAPIPayload {
  data: DiskInfo[];
}
export interface GetCpuStatsAPIPayload extends BaseAPIPayload {
  data: CpuStats;
}
export interface GetRamStatsAPIPayload extends BaseAPIPayload {
  data: RamStats;
}

export type ImageExplorerScope = 'all' | 'dataset' | 'tree' | 'roots';
export interface ImageExplorerRequestOptions {
  scope?: ImageExplorerScope;
  nodePath?: string;
}
export interface ProcessImageAPIPayload extends BaseAPIPayload {
  data: string;
  mask?: string;
  cutout?: string;
  stats?: Record<string, unknown>;
  wd14_backend?: string;
  wd14_tags?: string[];
}
export interface UploadImageAPIPayload extends BaseAPIPayload {
  payload: {
    paths: string[];
    [key: string]: unknown;
  };
}
//#endregion

//#region Routes
export enum APIEndpoints {
  CleanOldBackups = `/lf-nodes/clean-old-backups`,
  ClearAnalytics = `/lf-nodes/clear-analytics`,
  ClearMetadata = `/lf-nodes/clear-metadata`,
  ClearPreviewCache = `/lf-nodes/clear-preview-cache`,
  Free = `/lf-nodes/free`,
  ExploreFilesystem = `/lf-nodes/explore-filesystem`,
  GetAnalytics = `/lf-nodes/get-analytics`,
  GetBackupStats = `/lf-nodes/get-backup-stats`,
  GetCpuStats = '/lf-nodes/get-cpu-stats',
  GetDiskStats = '/lf-nodes/get-disk-stats',
  GetGpuStats = '/lf-nodes/get-gpu-stats',
  GetImage = `/lf-nodes/get-image`,
  GetJson = `/lf-nodes/get-json`,
  GetMetadata = `/lf-nodes/get-metadata`,
  GetRamStats = '/lf-nodes/get-ram-stats',
  GetPreviewStats = `/lf-nodes/get-preview-stats`,
  GetSamplers = `/lf-nodes/get-samplers`,
  GetSchedulers = `/lf-nodes/get-schedulers`,
  NewBackup = `/lf-nodes/new-backup`,
  ProcessImage = `/lf-nodes/process-image`,
  RefreshNodeDefs = `/lf-nodes/refresh-node-defs`,
  SaveMetadata = '/lf-nodes/save-metadata',
  UpdateJson = `/lf-nodes/update-json`,
  UpdateMetadataCover = '/lf-nodes/update-metadata-cover',
  UploadImage = `/lf-nodes/upload`,
  Workflows = `/lf-nodes/workflows`,
}
//#endregion
