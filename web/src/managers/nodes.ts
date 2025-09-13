import { COMFY_API } from '../api/comfy';
import { lfReroute } from '../nodes/reroute';
import {
  LFNodesInterface,
  LogSeverity,
  RegisteredVirtualNode,
  VirtualNodeExtension,
} from '../types/manager/manager';
import { getLfManager } from '../utils/common';

export class LFNodes implements LFNodesInterface {
  #REGISTRY: Map<string, RegisteredVirtualNode> = new Map();

  constructor() {
    this.add(lfReroute);
  }

  add = (extension: VirtualNodeExtension) => {
    const lfManager = getLfManager();
    if (!extension?.name) {
      lfManager?.log?.(
        `Attempted to add virtual node with invalid name`,
        { extension },
        LogSeverity.Warning,
      );
      return;
    }
    if (this.#REGISTRY.has(extension.name)) {
      lfManager?.log?.(
        `Duplicate virtual node ignored: '${extension.name}'`,
        {},
        LogSeverity.Warning,
      );
      return;
    }
    this.#REGISTRY.set(extension.name, { extension, registered: false });
  };

  addMany = (extensions: VirtualNodeExtension[]) => {
    extensions.forEach((e) => this.add(e));
  };

  list = () => Array.from(this.#REGISTRY.values());

  registerAll = () => {
    const lfManager = getLfManager();

    this.#REGISTRY.forEach((entry, key) => {
      if (entry.registered) {
        return;
      }
      try {
        COMFY_API.register(entry.extension);
        entry.registered = true;
        lfManager?.log?.(`Registered virtual node '${key}'`, {}, LogSeverity.Success);
      } catch (error) {
        entry.error = error;
        lfManager?.log?.(`Failed to register virtual node '${key}'`, { error }, LogSeverity.Error);
      }
    });
  };
}
