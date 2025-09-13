import { LfDataDataset } from '@lf-widgets/foundations';
import { EventName, GenericEvent } from '../events/events';
import { Extension, LogSeverity } from '../manager/manager';
import { ImageEditorFilterSettingsMap, ImageEditorFilterType } from '../widgets/imageEditor';

//#region API
export interface APIRoutes {
  analytics: AnalyticsAPIs;
  backup: BackupAPIs;
  comfy: ComfyAPIs;
  github: GitHubAPIs;
  image: ImageAPIs;
  json: JSONAPIs;
  metadata: MetadataAPIs;
}
export type AnalyticsType = 'usage';
export interface AnalyticsAPIs {
  clear: (type: AnalyticsType) => Promise<BaseAPIPayload>;
  get: (dir: string, type: AnalyticsType) => Promise<GetAnalyticsAPIPayload>;
}
export type BackupType = 'automatic' | 'manual';
export interface BackupAPIs {
  new: (backupType?: BackupType) => Promise<BaseAPIPayload>;
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
export interface ImageAPIs {
  get: (dir: string) => Promise<GetImageAPIPayload>;
  process: <T extends ImageEditorFilterType>(
    url: string,
    type: T,
    settings: ImageEditorFilterSettingsMap[T],
  ) => Promise<ProcessImageAPIPayload>;
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
export interface GetJSONAPIPayload extends BaseAPIPayload {
  data: LfDataDataset;
}
export interface GetMetadataAPIPayload extends BaseAPIPayload {
  data: CivitAIModelData;
}
export interface ProcessImageAPIPayload extends BaseAPIPayload {
  data: string;
}
//#endregion

//#region Routes
export enum APIEndpoints {
  ClearAnalytics = `/lf-nodes/clear-analytics`,
  ClearMetadata = `/lf-nodes/clear-metadata`,
  GetAnalytics = `/lf-nodes/get-analytics`,
  GetImage = `/lf-nodes/get-image`,
  GetJson = `/lf-nodes/get-json`,
  GetMetadata = `/lf-nodes/get-metadata`,
  NewBackup = `/lf-nodes/new-backup`,
  ProcessImage = `/lf-nodes/process-image`,
  SaveMetadata = '/lf-nodes/save-metadata',
  UpdateJson = `/lf-nodes/update-json`,
  UpdateMetadataCover = '/lf-nodes/update-metadata-cover',
}
//#endregion
