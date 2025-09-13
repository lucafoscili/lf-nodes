import { CustomWidgetName } from '../widgets/widgets';

//#region Comfy extension
type AtLeastOne<T, U = { [K in keyof T]: Pick<T, K> }> = Partial<T> & U[keyof U];
export type CustomWidgetGetter = Record<CustomWidgetName, Function>;
export interface Extension {
  beforeRegisterNodeDef?: (node: NodeType, data: NodeData, name: string) => void;
  getCustomWidgets?: () => AtLeastOne<Partial<CustomWidgetGetter>>;
  name: string;
  nodeCreated?: (node: NodeType) => void;
}
export type ExtensionCallback = (node: NodeType) => void;
//#endregion

//#region Log
export enum LogSeverity {
  Info = 'info',
  Success = 'success',
  Warning = 'warning',
  Error = 'error',
}
//#endregion

//#region Nodes
export interface VirtualNodeExtension extends Extension {
  name: string;
  registerCustomNodes?: (appInstance: GraphAppLike) => void;
}

export interface RegisteredVirtualNode {
  extension: VirtualNodeExtension;
  registered: boolean;
  error?: unknown;
}

export interface LFNodesInterface {
  add: (ext: VirtualNodeExtension) => void;
  addMany: (ext: VirtualNodeExtension[]) => void;
  list: () => RegisteredVirtualNode[];
  registerAll: () => void;
}
//#endregion

//#region Tooltip
export type TooltipUploadCallback = (b64image: string) => void;
export type TooltipCallbacks = TooltipUploadCallback;
export type TooltipLayouts = 'upload';
//#endregion
