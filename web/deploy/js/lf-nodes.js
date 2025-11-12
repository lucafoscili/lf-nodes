import { g as getLfFramework } from "./lf-widgets-framework-DcaHVr-f.js";
import "./lf-widgets-core-DIEht-jK.js";
import "./lf-widgets-foundations-Bbv1isuU.js";
var APIEndpoints;
(function(APIEndpoints2) {
  APIEndpoints2["CleanOldBackups"] = "/lf-nodes/clean-old-backups";
  APIEndpoints2["ClearAnalytics"] = "/lf-nodes/clear-analytics";
  APIEndpoints2["ClearMetadata"] = "/lf-nodes/clear-metadata";
  APIEndpoints2["ClearPreviewCache"] = "/lf-nodes/clear-preview-cache";
  APIEndpoints2["Free"] = "/lf-nodes/free";
  APIEndpoints2["ExploreFilesystem"] = "/lf-nodes/explore-filesystem";
  APIEndpoints2["GetAnalytics"] = "/lf-nodes/get-analytics";
  APIEndpoints2["GetCpuStats"] = "/lf-nodes/get-cpu-stats";
  APIEndpoints2["GetDiskStats"] = "/lf-nodes/get-disk-stats";
  APIEndpoints2["GetGpuStats"] = "/lf-nodes/get-gpu-stats";
  APIEndpoints2["GetImage"] = "/lf-nodes/get-image";
  APIEndpoints2["GetJson"] = "/lf-nodes/get-json";
  APIEndpoints2["GetRamStats"] = "/lf-nodes/get-ram-stats";
  APIEndpoints2["GetMetadata"] = "/lf-nodes/get-metadata";
  APIEndpoints2["GetPreviewStats"] = "/lf-nodes/get-preview-stats";
  APIEndpoints2["GetBackupStats"] = "/lf-nodes/get-backup-stats";
  APIEndpoints2["NewBackup"] = "/lf-nodes/new-backup";
  APIEndpoints2["ProcessImage"] = "/lf-nodes/process-image";
  APIEndpoints2["UploadImage"] = "/lf-nodes/upload";
  APIEndpoints2["RefreshNodeDefs"] = "/lf-nodes/refresh-node-defs";
  APIEndpoints2["SaveMetadata"] = "/lf-nodes/save-metadata";
  APIEndpoints2["UpdateJson"] = "/lf-nodes/update-json";
  APIEndpoints2["UpdateMetadataCover"] = "/lf-nodes/update-metadata-cover";
  APIEndpoints2["Workflows"] = "/lf-nodes/workflows";
})(APIEndpoints || (APIEndpoints = {}));
var LogSeverity;
(function(LogSeverity2) {
  LogSeverity2["Info"] = "info";
  LogSeverity2["Success"] = "success";
  LogSeverity2["Warning"] = "warning";
  LogSeverity2["Error"] = "error";
})(LogSeverity || (LogSeverity = {}));
const ANALYTICS_API = {
  //#region clear
  clear: async (type) => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("type", type);
      const response = await getComfyAPI().fetchApi(APIEndpoints.ClearAnalytics, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
            lfManager.getCachedDatasets().usage = {};
          }
          break;
        case 404:
          payload.message = `Analytics not found: ${type}. Skipping deletion.`;
          payload.status = LogSeverity.Info;
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the clear-analytics ${type} API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region get
  get: async (directory, type) => {
    const lfManager = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    if (!directory || !type) {
      payload.message = `Missing directory (received ${directory}) or  (received ${type}).`;
      payload.status = LogSeverity.Error;
      lfManager.log(payload.message, { payload }, LogSeverity.Error);
      return payload;
    }
    try {
      const body = new FormData();
      body.append("directory", directory);
      body.append("type", type);
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetAnalytics, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.data = p.data;
            payload.message = "Analytics data fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
            lfManager.getCachedDatasets().usage = payload.data;
          }
          break;
        case 404:
          payload.status = LogSeverity.Info;
          lfManager.log(`${type} analytics file not found.`, { payload }, payload.status);
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the get-analytics ${type} API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const BACKUP_API = {
  //#region new
  new: async (backupType = "automatic") => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("backup_type", backupType);
      const response = await getComfyAPI().fetchApi(APIEndpoints.NewBackup, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getStats
  getStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: {
        total_size_bytes: 0,
        file_count: 0,
        backups: []
      },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetBackupStats, { method: "GET" });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.data = p.data;
            payload.message = "Backup statistics retrieved successfully.";
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region cleanOld
  cleanOld: async (maxBackups) => {
    const lfManager = getLfManager();
    const _maxBackups = maxBackups || lfManager.getBackupRetention();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    if (_maxBackups <= 0) {
      const message = "Backup retention is set to 0, skipping cleanup.";
      lfManager.log(payload.message, { payload }, payload.status);
      payload.message = message;
      payload.status = LogSeverity.Info;
      return payload;
    }
    try {
      const body = new FormData();
      body.append("max_backups", String(_maxBackups));
      const response = await getComfyAPI().fetchApi(APIEndpoints.CleanOldBackups, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const COMFY_API = {
  comfyUi: () => window.comfyAPI,
  event: (name, callback) => {
    getComfyAPI().addEventListener(name, callback);
  },
  executeCommand: (name) => {
    try {
      getComfyAPP().extensionManager.command.execute(name);
    } catch (error) {
      getLfManager().log(`Command ${name} not executed!`, { error }, LogSeverity.Warning);
    }
  },
  getDragAndScale: () => {
    return getComfyAPP().canvas.ds;
  },
  getLinkById: (id) => {
    return getComfyAPP().graph.links[String(id).valueOf()];
  },
  getNodeById: (id) => {
    return getComfyAPP().graph.getNodeById(+(id || getComfyAPP().runningNodeId));
  },
  getResourceUrl: (subfolder, filename, type = "output") => {
    const params = [
      "filename=" + encodeURIComponent(filename),
      "type=" + type,
      "subfolder=" + subfolder,
      getComfyAPP().getRandParam().substring(1)
    ].join("&");
    return `/view?${params}`;
  },
  interrupt: () => {
    return getComfyAPI().interrupt();
  },
  queuePrompt: async () => {
    getComfyAPP().queuePrompt(0);
  },
  redraw: () => {
    getComfyAPP().graph.setDirtyCanvas(true, false);
  },
  redrawFull: () => {
    getComfyAPP().graph.setDirtyCanvas(true, true);
  },
  scheduleRedraw: /* @__PURE__ */ (() => {
    let scheduled = false;
    return (immediate = false) => {
      if (immediate) {
        scheduled = false;
        try {
          getComfyAPP().graph.setDirtyCanvas(true, true);
        } catch {
        }
        return;
      }
      if (scheduled) {
        return;
      }
      scheduled = true;
      requestAnimationFrame(() => {
        scheduled = false;
        try {
          const { app } = comfyAPI;
          app.graph.setDirtyCanvas(true, true);
        } catch {
        }
      });
    };
  })(),
  register: (extension) => {
    getComfyAPP().registerExtension(extension);
  },
  upload: async (body) => {
    return await getComfyAPI().fetchApi("/upload/image", {
      method: "POST",
      body
    });
  }
};
const GITHUB_API = {
  //#region getLatestRelease
  getLatestRelease: async () => {
    const lfManager = getLfManager();
    const REPO = "lf-nodes";
    const USER = "lucafoscili";
    const payload = {
      data: null,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await fetch(`https://api.github.com/repos/${USER}/${REPO}/releases/latest`);
      const code = response.status;
      switch (code) {
        case 200:
          const releaseData = await response.json();
          payload.data = releaseData;
          payload.message = "Latest release successfully fetched from GitHub.";
          payload.status = LogSeverity.Success;
          break;
        case 404:
          payload.message = "No releases found for the repository!";
          payload.status = LogSeverity.Info;
          break;
        default:
          payload.message = "Unexpected response from the GitHub API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = `Error fetching release info: ${error}`;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const IMAGE_API = {
  //#region get
  get: async (directory) => {
    const lfManager = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      if (directory) {
        body.append("directory", directory);
      }
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetImage, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.data = p.data;
            payload.message = "Images fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the get-image API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region explore
  explore: async (directory, options = {}) => {
    const lfManager = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      if (directory) {
        body.append("directory", directory);
      }
      const { scope, nodePath } = options;
      if (scope) {
        body.append("scope", scope);
      }
      if (nodePath) {
        body.append("node", nodePath);
      }
      const response = await getComfyAPI().fetchApi(APIEndpoints.ExploreFilesystem, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.data = p.data ?? {};
            payload.message = "Filesystem data fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the explore-filesystem API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload, options }, payload.status);
    return payload;
  },
  //#endregion
  //#region process
  process: async (url, type, settings) => {
    const lfManager = getLfManager();
    const payload = {
      data: "",
      mask: void 0,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("url", url);
      body.append("type", type);
      body.append("settings", JSON.stringify(settings));
      const response = await getComfyAPI().fetchApi(APIEndpoints.ProcessImage, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.data = p.data;
            payload.mask = p.mask;
            payload.message = "Image processed successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the process-image API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region upload
  upload: async (file, directory = "temp") => {
    var _a;
    const lfManager = getLfManager();
    const payload = {
      payload: { paths: [] },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("file", file);
      if (directory && directory !== "temp") {
        body.append("directory", directory);
      }
      const response = await getComfyAPI().fetchApi(APIEndpoints.UploadImage, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200: {
          const p = await response.json();
          if (p.status === "success" && Array.isArray((_a = p.payload) == null ? void 0 : _a.paths) && p.payload.paths.length > 0) {
            payload.payload.paths = [p.payload.paths[0]];
            payload.message = "Image uploaded successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        }
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the upload-image API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const JSON_API = {
  //#region get
  get: async (filePath) => {
    const lfManager = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("file_path", filePath);
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetJson, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.data = p.data;
            payload.message = "JSON data fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          payload.message = `Unexpected response from the get-json API: ${await response.text()}`;
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error.toString();
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region update
  update: async (filePath, dataset) => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    const body = new FormData();
    body.append("file_path", filePath);
    body.append("dataset", JSON.stringify(dataset));
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.UpdateJson, {
        body,
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const METADATA_API = {
  //#region clear
  clear: async () => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.ClearMetadata, {
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region get
  get: async (hash) => {
    const lfManager = getLfManager();
    const payload = {
      data: null,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await fetch(`https://civitai.com/api/v1/model-versions/by-hash/${hash}`);
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          payload.data = p;
          payload.message = "Metadata succesfully fetched from CivitAI.";
          payload.status = LogSeverity.Success;
          break;
        case 404:
          payload.message = "Model not found on CivitAI!";
          payload.status = LogSeverity.Info;
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region save
  save: async (modelPath, dataset, forcedSave = false) => {
    const lfManager = getLfManager();
    const payload = {
      data: null,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("model_path", modelPath);
      body.append("metadata", JSON.stringify(dataset));
      body.append("forced_save", String(forcedSave).valueOf());
      const response = await getComfyAPI().fetchApi(APIEndpoints.SaveMetadata, {
        method: "POST",
        body
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region updateCover
  updateCover: async (modelPath, b64image) => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("model_path", modelPath);
      body.append("base64_image", b64image);
      const response = await getComfyAPI().fetchApi(APIEndpoints.UpdateMetadataCover, {
        method: "POST",
        body
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.message = p.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const MODELS_API = {
  //#region free
  free: async () => {
    const lfManager = getLfManager();
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.Free, { method: "POST" });
      if (response.status === 200) {
        return true;
      }
      lfManager.log('"free" endpoint returned non-200', { status: response.status }, LogSeverity.Warning);
      return false;
    } catch (error) {
      lfManager.log('"free" endpoint failed', { error }, LogSeverity.Warning);
      return false;
    }
  },
  //#endregion
  //#region refresh
  refresh: async () => {
    const lfManager = getLfManager();
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.RefreshNodeDefs, {
        method: "POST"
      });
      if (response.status === 200) {
        return true;
      }
      lfManager.log('"refresh-node-defs" endpoint returned non-200', { status: response.status }, LogSeverity.Warning);
      return false;
    } catch (error) {
      lfManager.log('"refresh-node-defs" endpoint failed', { error }, LogSeverity.Warning);
      return false;
    }
  }
  //#endregion
};
const beforeFree = async (options) => {
  const lfManager = getLfManager();
  lfManager.log("Unload triggered — clearing LF caches first…", { options }, LogSeverity.Info);
  try {
    const ok = await MODELS_API.free();
    if (ok) {
      lfManager.log("Caches cleared ✔️", {}, LogSeverity.Success);
    } else {
      lfManager.log("Cache clear call returned non-200", {}, LogSeverity.Warning);
    }
  } catch (error) {
    lfManager.log("Error while clearing caches", { error }, LogSeverity.Warning);
  }
};
const beforeRefreshNodeDefs = async (trigger) => {
  const lfManager = getLfManager();
  lfManager.log("Refresh requested — clearing LF caches first…", { trigger }, LogSeverity.Info);
  try {
    const ok = await MODELS_API.refresh();
    if (ok) {
      lfManager.log("Refresh caches cleared ✔️", {}, LogSeverity.Success);
    } else {
      lfManager.log("Refresh cache clear call returned non-200", {}, LogSeverity.Warning);
    }
  } catch (error) {
    lfManager.log("Error while clearing caches ahead of refresh", { error }, LogSeverity.Warning);
  }
};
const PREVIEW_API = {
  //#region clearCache
  clearCache: async () => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.ClearPreviewCache, {
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.message = p.message || "Preview cache cleared successfully.";
            payload.status = LogSeverity.Success;
          }
          break;
        case 403:
          payload.message = "Permission denied: Unable to delete preview cache.";
          payload.status = LogSeverity.Error;
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the clear-preview-cache API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getStats
  getStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: {
        total_size_bytes: 0,
        file_count: 0,
        path: ""
      },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetPreviewStats, {
        method: "POST"
      });
      const code = response.status;
      switch (code) {
        case 200:
          const p = await response.json();
          if (p.status === "success") {
            payload.data = p.data;
            payload.message = p.message || "Preview stats retrieved successfully.";
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the get-preview-stats API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const unexpectedMessage = (endpoint, code, response, text) => {
  const body = text || response.statusText || "No message provided.";
  return `Unexpected response from ${endpoint} (${code}): ${body}`;
};
const normalizeMessage = (message, fallback = "Statistics retrieved successfully.") => {
  return message && message.trim().length > 0 ? message : fallback;
};
const SYSTEM_API = {
  //#region getGpuStats
  getGpuStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: [],
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetGpuStats, {
        method: "GET"
      });
      const code = response.status;
      switch (code) {
        case 200: {
          const p = await response.json();
          payload.data = p.data || [];
          payload.message = normalizeMessage(p.message, "GPU statistics retrieved successfully.");
          payload.status = p.status === "success" ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text = await response.text().catch(() => "");
          payload.message = unexpectedMessage("get-gpu-stats", code, response, text);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getDiskStats
  getDiskStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: [],
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetDiskStats, {
        method: "GET"
      });
      const code = response.status;
      switch (code) {
        case 200: {
          const p = await response.json();
          payload.data = p.data || [];
          payload.message = normalizeMessage(p.message, "Disk statistics retrieved successfully.");
          payload.status = p.status === "success" ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text = await response.text().catch(() => "");
          payload.message = unexpectedMessage("get-disk-stats", code, response, text);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getCpuStats
  getCpuStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: {
        average: 0,
        cores: [],
        count: 0,
        physical_count: 0
      },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetCpuStats, {
        method: "GET"
      });
      const code = response.status;
      switch (code) {
        case 200: {
          const p = await response.json();
          payload.data = p.data || payload.data;
          payload.message = normalizeMessage(p.message, "CPU statistics retrieved successfully.");
          payload.status = p.status === "success" ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text = await response.text().catch(() => "");
          payload.message = unexpectedMessage("get-cpu-stats", code, response, text);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getRamStats
  getRamStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: {
        available: 0,
        percent: 0,
        swap_total: 0,
        swap_used: 0,
        total: 0,
        used: 0
      },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await getComfyAPI().fetchApi(APIEndpoints.GetRamStats, {
        method: "GET"
      });
      const code = response.status;
      switch (code) {
        case 200: {
          const p = await response.json();
          payload.data = p.data || payload.data;
          payload.message = normalizeMessage(p.message, "RAM statistics retrieved successfully.");
          payload.status = p.status === "success" ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text = await response.text().catch(() => "");
          payload.message = unexpectedMessage("get-ram-stats", code, response, text);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error) {
      payload.message = String(error);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
var MessengerCSS;
(function(MessengerCSS2) {
  MessengerCSS2["Content"] = "lf-messenger";
  MessengerCSS2["Widget"] = "lf-messenger__widget";
  MessengerCSS2["Placeholder"] = "lf-messenger__placeholder";
  MessengerCSS2["PlaceholderHidden"] = "lf-messenger__placeholder--hidden";
})(MessengerCSS || (MessengerCSS = {}));
var ComfyWidgetName;
(function(ComfyWidgetName2) {
  ComfyWidgetName2["boolean"] = "BOOLEAN";
  ComfyWidgetName2["combo"] = "COMBO";
  ComfyWidgetName2["customtext"] = "CUSTOMTEXT";
  ComfyWidgetName2["float"] = "FLOAT";
  ComfyWidgetName2["integer"] = "INTEGER";
  ComfyWidgetName2["json"] = "JSON";
  ComfyWidgetName2["number"] = "NUMBER";
  ComfyWidgetName2["seed"] = "SEED";
  ComfyWidgetName2["string"] = "STRING";
  ComfyWidgetName2["text"] = "TEXT";
  ComfyWidgetName2["toggle"] = "TOGGLE";
})(ComfyWidgetName || (ComfyWidgetName = {}));
var CustomWidgetName;
(function(CustomWidgetName2) {
  CustomWidgetName2["card"] = "LF_CARD";
  CustomWidgetName2["cardsWithChip"] = "LF_CARDS_WITH_CHIP";
  CustomWidgetName2["carousel"] = "LF_CAROUSEL";
  CustomWidgetName2["chat"] = "LF_CHAT";
  CustomWidgetName2["chip"] = "LF_CHIP";
  CustomWidgetName2["code"] = "LF_CODE";
  CustomWidgetName2["compare"] = "LF_COMPARE";
  CustomWidgetName2["controlPanel"] = "LF_CONTROL_PANEL";
  CustomWidgetName2["countBarChart"] = "LF_COUNT_BAR_CHART";
  CustomWidgetName2["history"] = "LF_HISTORY";
  CustomWidgetName2["imageEditor"] = "LF_IMAGE_EDITOR";
  CustomWidgetName2["masonry"] = "LF_MASONRY";
  CustomWidgetName2["messenger"] = "LF_MESSENGER";
  CustomWidgetName2["progressbar"] = "LF_PROGRESSBAR";
  CustomWidgetName2["tabBarChart"] = "LF_TAB_BAR_CHART";
  CustomWidgetName2["textarea"] = "LF_TEXTAREA";
  CustomWidgetName2["tree"] = "LF_TREE";
  CustomWidgetName2["upload"] = "LF_UPLOAD";
})(CustomWidgetName || (CustomWidgetName = {}));
var NodeName;
(function(NodeName2) {
  NodeName2["backgroundRemover"] = "LF_BackgroundRemover";
  NodeName2["blend"] = "LF_Blend";
  NodeName2["blobToImage"] = "LF_BlobToImage";
  NodeName2["bloom"] = "LF_Bloom";
  NodeName2["blurImages"] = "LF_BlurImages";
  NodeName2["boolean"] = "LF_Boolean";
  NodeName2["brightness"] = "LF_Brightness";
  NodeName2["brush"] = "LF_Brush";
  NodeName2["captionImageWD14"] = "LF_CaptionImageWD14";
  NodeName2["characterImpersonator"] = "LF_CharacterImpersonator";
  NodeName2["checkpointSelector"] = "LF_CheckpointSelector";
  NodeName2["civitaiMetadataSetup"] = "LF_CivitAIMetadataSetup";
  NodeName2["clarity"] = "LF_Clarity";
  NodeName2["colorAnalysis"] = "LF_ColorAnalysis";
  NodeName2["compareImages"] = "LF_CompareImages";
  NodeName2["contrast"] = "LF_Contrast";
  NodeName2["controlPanel"] = "LF_ControlPanel";
  NodeName2["createMask"] = "LF_CreateMask";
  NodeName2["detectRegions"] = "LF_DetectRegions";
  NodeName2["desaturation"] = "LF_Desaturation";
  NodeName2["diffusionModelSelector"] = "LF_DiffusionModelSelector";
  NodeName2["displayBoolean"] = "LF_DisplayBoolean";
  NodeName2["displayFloat"] = "LF_DisplayFloat";
  NodeName2["displayInteger"] = "LF_DisplayInteger";
  NodeName2["displayJson"] = "LF_DisplayJSON";
  NodeName2["displayPrimitiveAsJson"] = "LF_DisplayPrimitiveAsJSON";
  NodeName2["displayString"] = "LF_DisplayString";
  NodeName2["markdownDocGenerator"] = "LF_MarkdownDocGenerator";
  NodeName2["filmGrain"] = "LF_FilmGrain";
  NodeName2["float"] = "LF_Float";
  NodeName2["embeddingSelector"] = "LF_EmbeddingSelector";
  NodeName2["emptyImage"] = "LF_EmptyImage";
  NodeName2["extractFaceEmbedding"] = "LF_ExtractFaceEmbedding";
  NodeName2["extractPromptFromLoraTag"] = "LF_ExtractPromptFromLoraTag";
  NodeName2["extractString"] = "LF_ExtractString";
  NodeName2["gaussianBlur"] = "LF_GaussianBlur";
  NodeName2["geminiAPI"] = "LF_GeminiAPI";
  NodeName2["getValueFromJson"] = "LF_GetValueFromJSON";
  NodeName2["getRandomKeyFromJson"] = "LF_GetRandomKeyFromJSON";
  NodeName2["imageClassifier"] = "LF_ImageClassifier";
  NodeName2["imageListFromJSON"] = "LF_ImageListFromJSON";
  NodeName2["imageHistogram"] = "LF_ImageHistogram";
  NodeName2["imagesEditingBreakpoint"] = "LF_ImagesEditingBreakpoint";
  NodeName2["imagesSlideshow"] = "LF_ImagesSlideshow";
  NodeName2["imageToSvg"] = "LF_ImageToSVG";
  NodeName2["inpaint"] = "LF_Inpaint";
  NodeName2["inpaintAdvanced"] = "LF_InpaintAdvanced";
  NodeName2["integer"] = "LF_Integer";
  NodeName2["isLandscape"] = "LF_IsLandscape";
  NodeName2["jsonPromptCombinator"] = "LF_JSONPromptCombinator";
  NodeName2["keywordCounter"] = "LF_KeywordCounter";
  NodeName2["keywordToggleFromJson"] = "LF_KeywordToggleFromJSON";
  NodeName2["line"] = "LF_Line";
  NodeName2["llmChat"] = "LF_LLMChat";
  NodeName2["llmMessenger"] = "LF_LLMMessenger";
  NodeName2["loadAndEditImages"] = "LF_LoadAndEditImages";
  NodeName2["loadClipSegModel"] = "LF_LoadCLIPSegModel";
  NodeName2["loadWd14Model"] = "LF_LoadWD14Model";
  NodeName2["loadFileOnce"] = "LF_LoadFileOnce";
  NodeName2["loadImages"] = "LF_LoadImages";
  NodeName2["loadLoraTags"] = "LF_LoadLoraTags";
  NodeName2["loadMetadata"] = "LF_LoadMetadata";
  NodeName2["loraAndEmbeddingSelector"] = "LF_LoraAndEmbeddingSelector";
  NodeName2["loraSelector"] = "LF_LoraSelector";
  NodeName2["lutApplication"] = "LF_LUTApplication";
  NodeName2["lutGeneration"] = "LF_LUTGeneration";
  NodeName2["mathOperation"] = "LF_MathOperation";
  NodeName2["multipleImageResizeForWeb"] = "LF_MultipleImageResizeForWeb";
  NodeName2["notify"] = "LF_Notify";
  NodeName2["onnxSelector"] = "LF_ONNXSelector";
  NodeName2["openAIAPI"] = "LF_OpenAIAPI";
  NodeName2["parsePromptWithLoraTags"] = "LF_ParsePromptWithLoraTags";
  NodeName2["randomBoolean"] = "LF_RandomBoolean";
  NodeName2["regexReplace"] = "LF_RegexReplace";
  NodeName2["regionExtractor"] = "LF_RegionExtractor";
  NodeName2["regionMask"] = "LF_RegionMask";
  NodeName2["resizeImageByEdge"] = "LF_ResizeImageByEdge";
  NodeName2["resizeImageToDimension"] = "LF_ResizeImageToDimension";
  NodeName2["resizeImageToSquare"] = "LF_ResizeImageToSquare";
  NodeName2["resolutionSwitcher"] = "LF_ResolutionSwitcher";
  NodeName2["samplerSelector"] = "LF_SamplerSelector";
  NodeName2["saturation"] = "LF_Saturation";
  NodeName2["saveImageForCivitai"] = "LF_SaveImageForCivitAI";
  NodeName2["saveJson"] = "LF_SaveJSON";
  NodeName2["saveMarkdown"] = "LF_SaveMarkdown";
  NodeName2["saveSvg"] = "LF_SaveSVG";
  NodeName2["saveText"] = "LF_SaveText";
  NodeName2["schedulerSelector"] = "LF_SchedulerSelector";
  NodeName2["sepia"] = "LF_Sepia";
  NodeName2["sequentialSeedsGenerator"] = "LF_SequentialSeedsGenerator";
  NodeName2["setValueInJson"] = "LF_SetValueInJSON";
  NodeName2["shuffleJsonKeys"] = "LF_ShuffleJSONKeys";
  NodeName2["something2Number"] = "LF_Something2Number";
  NodeName2["something2String"] = "LF_Something2String";
  NodeName2["sortJsonKeys"] = "LF_SortJSONKeys";
  NodeName2["sortTags"] = "LF_SortTags";
  NodeName2["splitTone"] = "LF_SplitTone";
  NodeName2["stabilityAPI"] = "LF_StabilityAPI";
  NodeName2["string"] = "LF_String";
  NodeName2["stringReplace"] = "LF_StringReplace";
  NodeName2["stringTemplate"] = "LF_StringTemplate";
  NodeName2["stringToJson"] = "LF_StringToJSON";
  NodeName2["switchFloat"] = "LF_SwitchFloat";
  NodeName2["switchImage"] = "LF_SwitchImage";
  NodeName2["switchInteger"] = "LF_SwitchInteger";
  NodeName2["switchJson"] = "LF_SwitchJSON";
  NodeName2["switchMask"] = "LF_SwitchMask";
  NodeName2["switchString"] = "LF_SwitchString";
  NodeName2["tiledSuperRes"] = "LF_TiledSuperRes";
  NodeName2["tiltShift"] = "LF_TiltShift";
  NodeName2["updateUsageStatistics"] = "LF_UpdateUsageStatistics";
  NodeName2["uploadImages"] = "LF_UploadImages";
  NodeName2["upscaleModelSelector"] = "LF_UpscaleModelSelector";
  NodeName2["urandomSeedGenerator"] = "LF_UrandomSeedGenerator";
  NodeName2["usageStatistics"] = "LF_UsageStatistics";
  NodeName2["vaeDecode"] = "LF_VAEDecode";
  NodeName2["vaeEncode"] = "LF_VAEEncode";
  NodeName2["vaeSelector"] = "LF_VAESelector";
  NodeName2["viewImages"] = "LF_ViewImages";
  NodeName2["viewSVGs"] = "LF_ViewSVGs";
  NodeName2["vibrance"] = "LF_Vibrance";
  NodeName2["vignette"] = "LF_Vignette";
  NodeName2["wallOfText"] = "LF_WallOfText";
  NodeName2["writeJson"] = "LF_WriteJSON";
})(NodeName || (NodeName = {}));
var TagName;
(function(TagName2) {
  TagName2["Div"] = "div";
  TagName2["LfAccordion"] = "lf-accordion";
  TagName2["LfArticle"] = "lf-article";
  TagName2["LfButton"] = "lf-button";
  TagName2["LfCard"] = "lf-card";
  TagName2["LfCarousel"] = "lf-carousel";
  TagName2["LfChat"] = "lf-chat";
  TagName2["LfChart"] = "lf-chart";
  TagName2["LfChip"] = "lf-chip";
  TagName2["LfCode"] = "lf-code";
  TagName2["LfCompare"] = "lf-compare";
  TagName2["LfImageviewer"] = "lf-imageviewer";
  TagName2["LfList"] = "lf-list";
  TagName2["LfMasonry"] = "lf-masonry";
  TagName2["LfMessenger"] = "lf-messenger";
  TagName2["LfProgressbar"] = "lf-progressbar";
  TagName2["LfSlider"] = "lf-slider";
  TagName2["LfSpinner"] = "lf-spinner";
  TagName2["LfTabbar"] = "lf-tabbar";
  TagName2["LfTextfield"] = "lf-textfield";
  TagName2["LfToggle"] = "lf-toggle";
  TagName2["LfTree"] = "lf-tree";
  TagName2["LfUpload"] = "lf-upload";
  TagName2["Textarea"] = "textarea";
})(TagName || (TagName = {}));
const NODE_WIDGET_MAP = {
  LF_BackgroundRemover: [CustomWidgetName.compare],
  LF_Blend: [CustomWidgetName.compare],
  LF_BlobToImage: [CustomWidgetName.code],
  LF_Bloom: [CustomWidgetName.compare],
  LF_BlurImages: [CustomWidgetName.masonry],
  LF_Boolean: [CustomWidgetName.history],
  LF_Brightness: [CustomWidgetName.compare],
  LF_Brush: [CustomWidgetName.compare],
  LF_CaptionImageWD14: [CustomWidgetName.countBarChart],
  LF_CharacterImpersonator: [CustomWidgetName.code],
  LF_CheckpointSelector: [CustomWidgetName.card],
  LF_CivitAIMetadataSetup: [CustomWidgetName.code],
  LF_Clarity: [CustomWidgetName.compare],
  LF_ColorAnalysis: [CustomWidgetName.tabBarChart],
  LF_CompareImages: [CustomWidgetName.compare],
  LF_Contrast: [CustomWidgetName.compare],
  LF_ControlPanel: [CustomWidgetName.controlPanel],
  LF_CreateMask: [CustomWidgetName.compare],
  LF_DetectRegions: [CustomWidgetName.compare],
  LF_Desaturation: [CustomWidgetName.compare],
  LF_DiffusionModelSelector: [CustomWidgetName.card],
  LF_DisplayBoolean: [CustomWidgetName.code],
  LF_DisplayFloat: [CustomWidgetName.code],
  LF_DisplayInteger: [CustomWidgetName.code],
  LF_DisplayJSON: [CustomWidgetName.code],
  LF_DisplayPrimitiveAsJSON: [CustomWidgetName.code],
  LF_DisplayString: [CustomWidgetName.code],
  LF_EmbeddingSelector: [CustomWidgetName.card],
  LF_EmptyImage: [CustomWidgetName.masonry],
  LF_ExtractFaceEmbedding: [CustomWidgetName.code],
  LF_ExtractPromptFromLoraTag: [CustomWidgetName.code],
  LF_ExtractString: [CustomWidgetName.code],
  LF_FilmGrain: [CustomWidgetName.compare],
  LF_Float: [CustomWidgetName.history],
  LF_GaussianBlur: [CustomWidgetName.compare],
  LF_GeminiAPI: [CustomWidgetName.code],
  LF_GetRandomKeyFromJSON: [CustomWidgetName.code],
  LF_GetValueFromJSON: [CustomWidgetName.code],
  LF_ImageClassifier: [CustomWidgetName.code],
  LF_ImageHistogram: [CustomWidgetName.tabBarChart],
  LF_ImageListFromJSON: [CustomWidgetName.masonry],
  LF_ImagesEditingBreakpoint: [CustomWidgetName.imageEditor],
  LF_ImagesSlideshow: [CustomWidgetName.carousel],
  LF_ImageToSVG: [CustomWidgetName.compare],
  LF_Inpaint: [CustomWidgetName.compare],
  LF_InpaintAdvanced: [CustomWidgetName.compare],
  LF_Integer: [CustomWidgetName.history],
  LF_IsLandscape: [CustomWidgetName.tree],
  LF_JSONPromptCombinator: [CustomWidgetName.code],
  LF_KeywordCounter: [CustomWidgetName.countBarChart],
  LF_KeywordToggleFromJSON: [CustomWidgetName.chip],
  LF_Line: [CustomWidgetName.compare],
  LF_LLMChat: [CustomWidgetName.chat],
  LF_LLMMessenger: [CustomWidgetName.messenger],
  LF_LoadAndEditImages: [CustomWidgetName.imageEditor],
  LF_LoadFileOnce: [CustomWidgetName.history],
  LF_LoadCLIPSegModel: [CustomWidgetName.code],
  LF_LoadWD14Model: [CustomWidgetName.code],
  LF_LoadImages: [CustomWidgetName.masonry],
  LF_LoadLoraTags: [CustomWidgetName.cardsWithChip],
  LF_LoadMetadata: [CustomWidgetName.upload],
  LF_LoraAndEmbeddingSelector: [CustomWidgetName.card],
  LF_LoraSelector: [CustomWidgetName.card],
  LF_LUTApplication: [CustomWidgetName.compare],
  LF_LUTGeneration: [CustomWidgetName.tabBarChart],
  LF_MarkdownDocGenerator: [CustomWidgetName.code],
  LF_MathOperation: [CustomWidgetName.code],
  LF_MultipleImageResizeForWeb: [CustomWidgetName.tree],
  LF_Notify: [],
  LF_ONNXSelector: [CustomWidgetName.history],
  LF_OpenAIAPI: [CustomWidgetName.code],
  LF_ParsePromptWithLoraTags: [CustomWidgetName.code],
  LF_RandomBoolean: [CustomWidgetName.progressbar],
  LF_RegexReplace: [CustomWidgetName.code],
  LF_RegionExtractor: [CustomWidgetName.code],
  LF_RegionMask: [CustomWidgetName.compare],
  LF_ResizeImageByEdge: [CustomWidgetName.tree],
  LF_ResizeImageToDimension: [CustomWidgetName.tree],
  LF_ResizeImageToSquare: [CustomWidgetName.tree],
  LF_ResolutionSwitcher: [CustomWidgetName.progressbar],
  LF_SamplerSelector: [CustomWidgetName.history],
  LF_Saturation: [CustomWidgetName.compare],
  LF_SaveImageForCivitAI: [CustomWidgetName.masonry],
  LF_SaveJSON: [CustomWidgetName.tree],
  LF_SaveMarkdown: [CustomWidgetName.tree],
  LF_SaveSVG: [CustomWidgetName.masonry],
  LF_SaveText: [CustomWidgetName.tree],
  LF_SchedulerSelector: [CustomWidgetName.history],
  LF_Sepia: [CustomWidgetName.compare],
  LF_SequentialSeedsGenerator: [CustomWidgetName.history],
  LF_SetValueInJSON: [CustomWidgetName.code],
  LF_ShuffleJSONKeys: [CustomWidgetName.code],
  LF_Something2Number: [CustomWidgetName.code],
  LF_Something2String: [CustomWidgetName.code],
  LF_SortJSONKeys: [CustomWidgetName.code],
  LF_SortTags: [CustomWidgetName.code],
  LF_SplitTone: [CustomWidgetName.compare],
  LF_StabilityAPI: [CustomWidgetName.code],
  LF_String: [CustomWidgetName.history],
  LF_StringReplace: [CustomWidgetName.code],
  LF_StringTemplate: [CustomWidgetName.code],
  LF_StringToJSON: [CustomWidgetName.code],
  LF_SwitchFloat: [CustomWidgetName.progressbar],
  LF_SwitchImage: [CustomWidgetName.progressbar],
  LF_SwitchInteger: [CustomWidgetName.progressbar],
  LF_SwitchJSON: [CustomWidgetName.progressbar],
  LF_SwitchMask: [CustomWidgetName.progressbar],
  LF_SwitchString: [CustomWidgetName.progressbar],
  LF_TiledSuperRes: [CustomWidgetName.compare],
  LF_TiltShift: [CustomWidgetName.compare],
  LF_UpdateUsageStatistics: [CustomWidgetName.code],
  LF_UploadImages: [CustomWidgetName.upload],
  LF_UpscaleModelSelector: [CustomWidgetName.history],
  LF_UsageStatistics: [CustomWidgetName.tabBarChart],
  LF_UrandomSeedGenerator: [CustomWidgetName.tree],
  LF_VAEDecode: [CustomWidgetName.code],
  LF_VAEEncode: [CustomWidgetName.code],
  LF_VAESelector: [CustomWidgetName.history],
  LF_Vibrance: [CustomWidgetName.compare],
  LF_ViewImages: [CustomWidgetName.masonry],
  LF_ViewSVGs: [CustomWidgetName.masonry],
  LF_Vignette: [CustomWidgetName.compare],
  LF_WallOfText: [CustomWidgetName.code],
  LF_WriteJSON: [CustomWidgetName.textarea]
};
const onAfterGraphConfigured = async (ctor, cb) => {
  const proto = ctor.prototype;
  const original = proto.onAfterGraphConfigured;
  proto.onAfterGraphConfigured = function() {
    var _a, _b;
    const r = original == null ? void 0 : original.apply(this, arguments);
    try {
      cb(this);
    } catch (err) {
      (_b = (_a = getLfManager()) == null ? void 0 : _a.log) == null ? void 0 : _b.call(_a, "onAfterGraphConfigured hook error", { err }, LogSeverity.Warning);
    }
    return r;
  };
};
const onConnectionsChange = async (nodeType) => {
  const onConnectionsChange2 = nodeType.prototype.onConnectionsChange;
  nodeType.prototype.onConnectionsChange = function() {
    const r = onConnectionsChange2 == null ? void 0 : onConnectionsChange2.apply(this, arguments);
    const node = this;
    switch (node.comfyClass) {
      case NodeName.keywordToggleFromJson:
        chipCb(node);
        break;
      case NodeName.llmMessenger:
        messengerCb(node);
        break;
    }
    return r;
  };
};
const onDrawBackground = async (nodeType) => {
  const onDrawBackground2 = nodeType.prototype.onDrawBackground;
  nodeType.prototype.onDrawBackground = function() {
    const r = onDrawBackground2 == null ? void 0 : onDrawBackground2.apply(this, arguments);
    const node = this;
    refreshChart(node);
    return r;
  };
};
const onNodeCreated = async (nodeType) => {
  const onNodeCreated2 = nodeType.prototype.onNodeCreated;
  nodeType.prototype.onNodeCreated = function() {
    var _a;
    const r = onNodeCreated2 ? onNodeCreated2.apply(this, arguments) : void 0;
    const node = this;
    for (let index = 0; index < ((_a = node.widgets) == null ? void 0 : _a.length); index++) {
      const w = node.widgets[index];
      switch (w.type.toUpperCase()) {
        case CustomWidgetName.imageEditor:
          const ds = getApiRoutes().comfy.getDragAndScale();
          if (ds) {
            const onredraw = ds.onredraw;
            ds.onredraw = function() {
              const r2 = onredraw ? onredraw.apply(this, arguments) : void 0;
              const state = w.options.getState();
              setCanvasSizeCb(state.elements.imageviewer);
              return r2;
            };
          }
          break;
        case ComfyWidgetName.customtext:
        case ComfyWidgetName.string:
        case ComfyWidgetName.text:
          w.serializeValue = () => {
            const comfy = getApiRoutes().comfy.comfyUi();
            return comfy.utils.applyTextReplacements(comfy.app.app, w.value);
          };
          break;
      }
    }
    return r;
  };
};
const chipCb = (node) => {
  var _a, _b, _c, _d, _e;
  const lfManager = getLfManager();
  const { syntax } = lfManager.getManagers().lfFramework;
  const routes = getApiRoutes().comfy;
  const textarea = getInput(node, ComfyWidgetName.json);
  const linkInput = routes.getLinkById((_a = textarea == null ? void 0 : textarea.link) == null ? void 0 : _a.toString());
  const nodeInput = routes.getNodeById((_b = linkInput == null ? void 0 : linkInput.origin_id) == null ? void 0 : _b.toString());
  if (!textarea || !linkInput || !nodeInput) {
    return;
  }
  const chipW = getCustomWidget(node, CustomWidgetName.chip);
  const datasetW = (_c = nodeInput == null ? void 0 : nodeInput.widgets) == null ? void 0 : _c[linkInput.origin_slot];
  if (!((_d = chipW.options) == null ? void 0 : _d.getState) || !((_e = datasetW.options) == null ? void 0 : _e.getValue)) {
    lfManager.log("Missing options", { chipW, datasetW }, LogSeverity.Warning);
    return;
  }
  const dataset = datasetW.options.getValue();
  const chip = chipW.options.getState().chip;
  try {
    const newData = syntax.json.unescape(dataset).parsedJSON;
    if (syntax.json.isValid(newData) && syntax.json.isValid(chip.lfDataset)) {
      if (!syntax.json.areEqual(newData, chip.lfDataset)) {
        chip.lfDataset = newData;
        lfManager.log("Updated chip data", { dataset }, LogSeverity.Info);
      }
    } else {
      if (syntax.json.isValid(newData)) {
        chip.lfDataset = newData;
        lfManager.log("Set chip data", { dataset }, LogSeverity.Info);
      } else {
        lfManager.log("Invalid JSON data", { dataset, error: "Invalid JSON" }, LogSeverity.Warning);
      }
    }
  } catch (error) {
    lfManager.log("Error processing chip data", { dataset, error }, LogSeverity.Error);
  }
};
const messengerCb = (node) => {
  var _a, _b, _c, _d, _e, _f, _g;
  const textarea = getInput(node, ComfyWidgetName.json);
  const linkInput = getApiRoutes().comfy.getLinkById((_a = textarea == null ? void 0 : textarea.link) == null ? void 0 : _a.toString());
  const nodeInput = getApiRoutes().comfy.getNodeById((_b = linkInput == null ? void 0 : linkInput.origin_id) == null ? void 0 : _b.toString());
  if (!textarea || !linkInput || !nodeInput) {
    return;
  }
  const messengerW = getCustomWidget(node, CustomWidgetName.messenger);
  const datasetW = (_c = nodeInput == null ? void 0 : nodeInput.widgets) == null ? void 0 : _c[linkInput.origin_slot];
  if (!((_d = datasetW == null ? void 0 : datasetW.options) == null ? void 0 : _d.getValue)) {
    return;
  }
  const dataset = datasetW.options.getValue();
  const messenger = ((_e = messengerW == null ? void 0 : messengerW.options) == null ? void 0 : _e.getState()).elements.messenger;
  try {
    const { syntax } = getLfManager().getManagers().lfFramework;
    const newData = syntax.json.unescape(dataset).parsedJSON;
    if (syntax.json.isValid(newData) && syntax.json.isValid(messenger.lfDataset)) {
      if (!syntax.json.areEqual(newData, messenger.lfDataset)) {
        messenger.lfDataset = newData;
        messenger.reset();
        getLfManager().log("Updated messenger data", { dataset }, LogSeverity.Info);
      }
    } else {
      if (syntax.json.isValid(newData)) {
        messenger.lfDataset = newData;
        messenger.reset();
        getLfManager().log("Set messenger data", { dataset }, LogSeverity.Info);
      } else {
        getLfManager().log("Invalid JSON data", { dataset, error: "Invalid JSON" }, LogSeverity.Warning);
      }
    }
    const placeholder = messenger.nextSibling || messenger.previousSibling;
    if ((_g = (_f = messenger.lfDataset) == null ? void 0 : _f.nodes) == null ? void 0 : _g[0]) {
      placeholder.classList.add(MessengerCSS.PlaceholderHidden);
    } else {
      placeholder.classList.remove(MessengerCSS.PlaceholderHidden);
    }
  } catch (error) {
    getLfManager().log("Error processing messenger data", { dataset, error }, LogSeverity.Error);
  }
};
const setCanvasSizeCb = (imageviewer) => {
  requestAnimationFrame(async () => {
    try {
      const { canvas } = (await imageviewer.getComponents()).details;
      canvas == null ? void 0 : canvas.resizeCanvas();
    } catch (error) {
    }
  });
};
const getLogStyle = () => {
  return {
    fontFamily: "var(--lf-font-family-monospace)",
    margin: "0",
    maxWidth: "100%",
    overflow: "hidden",
    padding: "4px 8px",
    textOverflow: "ellipsis"
  };
};
function installLFBeforeFreeHooks(api, opts = {}) {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {
  });
  if (!isFreeHookAPI(api)) {
    logger('"api" object not available; cannot install free hooks yet', {}, LogSeverity.Warning);
    return { freeMemoryHook: false, fetchFallbackHook: false };
  }
  const wrap = opts.freeWrapper ?? ((fn) => async function(options) {
    await beforeFree(options);
    return fn.apply(this ?? api, [options]);
  });
  const installFreeMemory = () => {
    try {
      if (api[LFFreeFlags.PatchedFree] === true)
        return true;
      const current = api.freeMemory;
      if (typeof current === "function") {
        api[LFFreeFlags.OriginalFreeRef] = current;
        api.freeMemory = wrap(current);
        api[LFFreeFlags.PatchedFree] = true;
        return true;
      }
      const desc = Object.getOwnPropertyDescriptor(api, "freeMemory");
      if (!desc || desc.configurable) {
        let original;
        Object.defineProperty(api, "freeMemory", {
          configurable: true,
          enumerable: true,
          get() {
            return original;
          },
          set(fn) {
            if (api[LFFreeFlags.PatchedFree] === true) {
              original = fn;
              return;
            }
            if (typeof fn === "function") {
              api[LFFreeFlags.OriginalFreeRef] = fn;
              original = wrap(fn);
              api[LFFreeFlags.PatchedFree] = true;
            } else {
              original = fn;
            }
          }
        });
      }
      return false;
    } catch (e) {
      logger("Failed to patch freeMemory; proceeding without LF cache clear hook", { e }, LogSeverity.Warning);
      return false;
    }
  };
  let freePatched = installFreeMemory();
  if (!freePatched) {
    let count = 0;
    const iv = setInterval(() => {
      count += 1;
      if (installFreeMemory() || api[LFFreeFlags.PatchedFree] === true || count > attempts) {
        clearInterval(iv);
      }
    }, intervalMs);
  }
  const installFetchFallback = () => {
    try {
      if (api[LFFreeFlags.PatchedFetch] === true) {
        return true;
      }
      const originalFetchApi = api.fetchApi;
      if (typeof originalFetchApi !== "function") {
        return false;
      }
      api[LFFreeFlags.PatchedFetch] = true;
      api.fetchApi = async function(path, init) {
        try {
          const url = typeof path === "string" ? path : String(path ?? "");
          const isFree = url.endsWith("/free") || url.endsWith("/api/free");
          const isOur = url.includes("/lf-nodes/free");
          const method = ((init == null ? void 0 : init.method) ?? "GET").toUpperCase();
          if (isFree && !isOur && method === "POST" && api[LFFreeFlags.InBeforeFree] !== true) {
            api[LFFreeFlags.InBeforeFree] = true;
            try {
              await beforeFree(init);
            } finally {
              api[LFFreeFlags.InBeforeFree] = false;
            }
          }
        } catch {
        }
        return originalFetchApi.apply(this ?? api, [path, init]);
      };
      return true;
    } catch (e) {
      logger("Failed to patch api.fetchApi; proceeding without LF cache clear fallback", { e }, LogSeverity.Warning);
      return false;
    }
  };
  const fetchPatched = installFetchFallback();
  return { freeMemoryHook: freePatched, fetchFallbackHook: fetchPatched };
}
const applySelectionColumn = (dataset, selection) => {
  var _a, _b, _c;
  const lfData = (_c = (_b = (_a = getLfManager()) == null ? void 0 : _a.getManagers()) == null ? void 0 : _b.lfFramework) == null ? void 0 : _c.data;
  const existingColumns = Array.isArray(dataset == null ? void 0 : dataset.columns) ? dataset.columns : [];
  const [existingSelectionColumn] = lfData ? lfData.column.find(existingColumns, { id: "selected" }) : [];
  const updatedSelectionColumn = {
    ...existingSelectionColumn ?? { id: "selected" },
    title: selection
  };
  const nextColumns = existingSelectionColumn ? existingColumns.map((col) => col.id === "selected" ? updatedSelectionColumn : col) : [...existingColumns, updatedSelectionColumn];
  return {
    ...dataset,
    columns: nextColumns,
    selection
  };
};
const buildSelectionPayload = ({ dataset, index, nodes, selectedShape, fallbackContextId }) => {
  var _a, _b;
  const resolvedContextId = dataset.context_id ?? ((_a = dataset.selection) == null ? void 0 : _a.context_id) ?? fallbackContextId;
  const selection = {
    index,
    context_id: resolvedContextId
  };
  const derivedName = deriveSelectionName(selectedShape);
  if (derivedName) {
    selection.name = derivedName;
  }
  const selectedNode = Array.isArray(nodes) && index >= 0 && index < nodes.length && nodes[index] ? nodes[index] : void 0;
  if (selectedNode && typeof selectedNode === "object") {
    const nodeId = asString(selectedNode.id);
    if (nodeId) {
      selection.node_id = nodeId;
    }
    const imageCell = (_b = selectedNode.cells) == null ? void 0 : _b.lfImage;
    const imageValue = asString(imageCell == null ? void 0 : imageCell.value) ?? asString(imageCell == null ? void 0 : imageCell.lfValue);
    if (imageValue) {
      selection.url = imageValue;
    }
  }
  return { selection, contextId: resolvedContextId };
};
const deriveDirectoryValue = (directory) => {
  if (!directory) {
    return void 0;
  }
  if (isString(directory.raw)) {
    return directory.raw;
  }
  if (isString(directory.relative)) {
    return directory.relative;
  }
  if (isString(directory.resolved)) {
    return directory.resolved;
  }
  return void 0;
};
const deriveSelectionName = (selectedShape) => {
  if (!selectedShape) {
    return void 0;
  }
  const shape = selectedShape.shape;
  const htmlProps = (shape == null ? void 0 : shape.htmlProps) ?? {};
  const htmlTitle = asString(htmlProps["title"]);
  const htmlId = asString(htmlProps["id"]);
  const shapeValue = asString(shape == null ? void 0 : shape.value);
  const lfValue = asString(shape == null ? void 0 : shape.lfValue);
  return htmlTitle ?? htmlId ?? shapeValue ?? lfValue ?? void 0;
};
const ensureDatasetContext = (dataset, state) => {
  if (!dataset) {
    return state == null ? void 0 : state.contextId;
  }
  const setStateContext = (contextId) => {
    if (contextId && state) {
      state.contextId = contextId;
    }
  };
  if (dataset.context_id) {
    setStateContext(dataset.context_id);
  } else if (state == null ? void 0 : state.contextId) {
    dataset.context_id = state.contextId;
  }
  const selection = dataset.selection;
  const resolvedContext = (selection == null ? void 0 : selection.context_id) ?? dataset.context_id ?? (state == null ? void 0 : state.contextId);
  if (selection && resolvedContext) {
    selection.context_id = selection.context_id ?? resolvedContext;
    if (!dataset.context_id) {
      dataset.context_id = resolvedContext;
    }
    setStateContext(resolvedContext);
    return resolvedContext;
  }
  if (dataset.context_id) {
    setStateContext(dataset.context_id);
    return dataset.context_id;
  }
  if (state == null ? void 0 : state.contextId) {
    dataset.context_id = state.contextId;
    return state.contextId;
  }
  return void 0;
};
const getNavigationDirectory = (dataset) => {
  var _a;
  return (_a = dataset == null ? void 0 : dataset.navigation) == null ? void 0 : _a.directory;
};
const hasContextChanged = (previousContextId, nextContextId) => {
  return previousContextId !== nextContextId;
};
const hasSelectionChanged = (previousSelection, nextSelection) => {
  return JSON.stringify(previousSelection ?? null) !== JSON.stringify(nextSelection ?? null);
};
const mergeNavigationDirectory = (dataset, directory) => {
  var _a;
  const current = ((_a = dataset.navigation) == null ? void 0 : _a.directory) ?? {};
  const next = {
    ...current,
    ...directory
  };
  dataset.navigation = dataset.navigation ?? {};
  dataset.navigation.directory = next;
  return next;
};
const resolveSelectionIndex = (selectedShape, nodes) => {
  var _a;
  if (typeof (selectedShape == null ? void 0 : selectedShape.index) === "number") {
    return selectedShape.index;
  }
  if (!Array.isArray(nodes)) {
    return void 0;
  }
  const shape = selectedShape == null ? void 0 : selectedShape.shape;
  const shapeId = asString((_a = shape == null ? void 0 : shape.htmlProps) == null ? void 0 : _a["id"]);
  const shapeValue = asString(shape == null ? void 0 : shape.value) ?? asString(shape == null ? void 0 : shape.lfValue);
  const resolvedIndex = nodes.findIndex((node) => {
    var _a2, _b;
    if (!node || typeof node !== "object") {
      return false;
    }
    const imageCell = (_a2 = node.cells) == null ? void 0 : _a2.lfImage;
    if (!imageCell) {
      return false;
    }
    const cellId = asString((_b = imageCell.htmlProps) == null ? void 0 : _b["id"]);
    const cellValue = asString(imageCell.value) ?? asString(imageCell.lfValue);
    if (shapeId && cellId === shapeId) {
      return true;
    }
    if (shapeValue && cellValue === shapeValue) {
      return true;
    }
    return false;
  });
  return resolvedIndex >= 0 ? resolvedIndex : void 0;
};
const MANUAL_APPLY_PROCESSING_LABEL = "Applying…";
const hasManualApplyPendingChanges = (state) => {
  const manual = state.manualApply;
  if (!manual) {
    return false;
  }
  return manual.latestChangeId > manual.latestAppliedChangeId;
};
const updateManualApplyButton = (state) => {
  const manual = state.manualApply;
  if (!manual) {
    return;
  }
  manual.dirty = hasManualApplyPendingChanges(state);
  if (manual.isProcessing) {
    manual.button.lfUiState = "disabled";
    manual.button.lfLabel = MANUAL_APPLY_PROCESSING_LABEL;
    return;
  }
  manual.button.lfLabel = manual.defaultLabel;
  if (manual.dirty) {
    manual.button.lfUiState = "success";
  } else {
    manual.button.lfUiState = "disabled";
  }
};
const initManualApplyState = (state, button) => {
  state.manualApply = {
    button,
    defaultLabel: button.lfLabel ?? "Apply",
    dirty: false,
    isProcessing: false,
    changeCounter: 0,
    latestChangeId: 0,
    latestAppliedChangeId: 0,
    activeRequestChangeId: 0
  };
  updateManualApplyButton(state);
};
const registerManualApplyChange = (state) => {
  var _a;
  if (!((_a = state.filter) == null ? void 0 : _a.requiresManualApply) || !state.manualApply) {
    return;
  }
  const manual = state.manualApply;
  manual.latestChangeId = ++manual.changeCounter;
  if (!manual.isProcessing) {
    updateManualApplyButton(state);
  }
};
const beginManualApplyRequest = (state) => {
  if (!state.manualApply) {
    return;
  }
  const manual = state.manualApply;
  manual.isProcessing = true;
  manual.activeRequestChangeId = manual.latestChangeId;
  updateManualApplyButton(state);
};
const resolveManualApplyRequest = (state, wasSuccessful) => {
  if (!state.manualApply) {
    return;
  }
  const manual = state.manualApply;
  if (wasSuccessful) {
    manual.latestAppliedChangeId = Math.max(manual.latestAppliedChangeId, manual.activeRequestChangeId);
  }
  manual.activeRequestChangeId = 0;
  manual.isProcessing = false;
  updateManualApplyButton(state);
};
const apiCall$2 = async (state, addSnapshot) => {
  var _a, _b;
  const { elements, filter, filterType } = state;
  const { imageviewer } = elements;
  const lfManager = getLfManager();
  const snapshot = await imageviewer.getCurrentSnapshot();
  if (!snapshot) {
    lfManager.log("No snapshot available for processing!", {}, LogSeverity.Warning);
    return false;
  }
  const snapshotValue = snapshot.value;
  const baseSettings = filter.settings;
  const payload = {
    ...baseSettings
  };
  const contextDataset = imageviewer.lfDataset;
  const contextId = ensureDatasetContext(contextDataset, state);
  if (!contextId && filterType === "inpaint") {
    lfManager.log("Missing editing context. Run the workflow to register an editing session before using inpaint.", { dataset: contextDataset }, LogSeverity.Warning);
    if ((_a = state.manualApply) == null ? void 0 : _a.isProcessing) {
      resolveManualApplyRequest(state, false);
    }
    return false;
  }
  payload.context_id = contextId;
  requestAnimationFrame(() => imageviewer.setSpinnerStatus(true));
  let isSuccess = false;
  try {
    const response = await getApiRoutes().image.process(snapshotValue, filterType, payload);
    if (response.mask) {
      lfManager.log("Saved inpaint mask preview to temp", { mask: response.mask }, LogSeverity.Info);
    }
    if (response.cutout) {
      lfManager.log("Saved cutout preview to temp", { cutout: response.cutout }, LogSeverity.Info);
    }
    if (response.stats) {
      lfManager.log("Filter statistics", { stats: response.stats }, LogSeverity.Info);
    }
    if (addSnapshot) {
      await imageviewer.addSnapshot(response.data);
    } else {
      const { canvas } = (await imageviewer.getComponents()).details;
      const image = await canvas.getImage();
      requestAnimationFrame(() => image.lfValue = response.data);
    }
    isSuccess = true;
  } catch (error) {
    lfManager.log("Error processing image!", { error }, LogSeverity.Error);
  }
  requestAnimationFrame(() => imageviewer.setSpinnerStatus(false));
  if ((_b = state.manualApply) == null ? void 0 : _b.isProcessing) {
    resolveManualApplyRequest(state, isSuccess);
  }
  return isSuccess;
};
var ImageEditorCSS;
(function(ImageEditorCSS2) {
  ImageEditorCSS2["Content"] = "lf-imageeditor";
  ImageEditorCSS2["Widget"] = "lf-imageeditor__widget";
  ImageEditorCSS2["Actions"] = "lf-imageeditor__actions";
  ImageEditorCSS2["Grid"] = "lf-imageeditor__grid";
  ImageEditorCSS2["GridHasActions"] = "lf-imageeditor__grid--has-actions";
  ImageEditorCSS2["GridIsInactive"] = "lf-imageeditor__grid--is-inactive";
  ImageEditorCSS2["Settings"] = "lf-imageeditor__settings";
  ImageEditorCSS2["SettingsControls"] = "lf-imageeditor__settings__controls";
  ImageEditorCSS2["SettingsButtons"] = "lf-imageeditor__settings__buttons";
})(ImageEditorCSS || (ImageEditorCSS = {}));
var ImageEditorStatus;
(function(ImageEditorStatus2) {
  ImageEditorStatus2["Completed"] = "completed";
  ImageEditorStatus2["Pending"] = "pending";
})(ImageEditorStatus || (ImageEditorStatus = {}));
var ImageEditorColumnId;
(function(ImageEditorColumnId2) {
  ImageEditorColumnId2["Path"] = "path";
  ImageEditorColumnId2["Status"] = "status";
})(ImageEditorColumnId || (ImageEditorColumnId = {}));
var ImageEditorIcons;
(function(ImageEditorIcons2) {
  ImageEditorIcons2["Interrupt"] = "x";
  ImageEditorIcons2["Reset"] = "refresh";
  ImageEditorIcons2["Resume"] = "check";
})(ImageEditorIcons || (ImageEditorIcons = {}));
var ImageEditorControls;
(function(ImageEditorControls2) {
  ImageEditorControls2["Canvas"] = "canvas";
  ImageEditorControls2["Slider"] = "slider";
  ImageEditorControls2["Textfield"] = "textfield";
  ImageEditorControls2["Toggle"] = "toggle";
})(ImageEditorControls || (ImageEditorControls = {}));
var ImageEditorCanvasIds;
(function(ImageEditorCanvasIds2) {
  ImageEditorCanvasIds2["B64Canvas"] = "b64_canvas";
  ImageEditorCanvasIds2["Points"] = "points";
})(ImageEditorCanvasIds || (ImageEditorCanvasIds = {}));
var ImageEditorSliderIds;
(function(ImageEditorSliderIds2) {
  ImageEditorSliderIds2["Amount"] = "amount";
  ImageEditorSliderIds2["Balance"] = "balance";
  ImageEditorSliderIds2["BlueChannel"] = "b_channel";
  ImageEditorSliderIds2["BlurKernelSize"] = "blur_kernel_size";
  ImageEditorSliderIds2["BlurSigma"] = "blur_sigma";
  ImageEditorSliderIds2["ClarityAmount"] = "clarity_amount";
  ImageEditorSliderIds2["DenoisePercentage"] = "denoise_percentage";
  ImageEditorSliderIds2["Cfg"] = "cfg";
  ImageEditorSliderIds2["ConditioningMix"] = "conditioning_mix";
  ImageEditorSliderIds2["Dilate"] = "dilate";
  ImageEditorSliderIds2["FocusPosition"] = "focus_position";
  ImageEditorSliderIds2["FocusSize"] = "focus_size";
  ImageEditorSliderIds2["Gamma"] = "gamma";
  ImageEditorSliderIds2["GreenChannel"] = "g_channel";
  ImageEditorSliderIds2["Intensity"] = "intensity";
  ImageEditorSliderIds2["Midpoint"] = "midpoint";
  ImageEditorSliderIds2["Opacity"] = "opacity";
  ImageEditorSliderIds2["RoiAlign"] = "roi_align";
  ImageEditorSliderIds2["RoiMinSize"] = "roi_min_size";
  ImageEditorSliderIds2["RoiPadding"] = "roi_padding";
  ImageEditorSliderIds2["Radius"] = "radius";
  ImageEditorSliderIds2["RedChannel"] = "r_channel";
  ImageEditorSliderIds2["SharpenAmount"] = "sharpen_amount";
  ImageEditorSliderIds2["Size"] = "size";
  ImageEditorSliderIds2["Sigma"] = "sigma";
  ImageEditorSliderIds2["Softness"] = "softness";
  ImageEditorSliderIds2["Steps"] = "steps";
  ImageEditorSliderIds2["Strength"] = "strength";
  ImageEditorSliderIds2["Threshold"] = "threshold";
  ImageEditorSliderIds2["UpsampleTarget"] = "upsample_target";
  ImageEditorSliderIds2["Feather"] = "feather";
})(ImageEditorSliderIds || (ImageEditorSliderIds = {}));
var ImageEditorTextfieldIds;
(function(ImageEditorTextfieldIds2) {
  ImageEditorTextfieldIds2["Color"] = "color";
  ImageEditorTextfieldIds2["Highlights"] = "highlights";
  ImageEditorTextfieldIds2["NegativePrompt"] = "negative_prompt";
  ImageEditorTextfieldIds2["PositivePrompt"] = "positive_prompt";
  ImageEditorTextfieldIds2["Seed"] = "seed";
  ImageEditorTextfieldIds2["Shadows"] = "shadows";
  ImageEditorTextfieldIds2["Tint"] = "tint";
})(ImageEditorTextfieldIds || (ImageEditorTextfieldIds = {}));
var ImageEditorToggleIds;
(function(ImageEditorToggleIds2) {
  ImageEditorToggleIds2["ClipSoft"] = "clip_soft";
  ImageEditorToggleIds2["Localized"] = "localized";
  ImageEditorToggleIds2["ProtectSkin"] = "protect_skin";
  ImageEditorToggleIds2["Shape"] = "shape";
  ImageEditorToggleIds2["Smooth"] = "smoooth";
  ImageEditorToggleIds2["SoftBlend"] = "soft_blend";
  ImageEditorToggleIds2["TransparentBackground"] = "transparent_background";
  ImageEditorToggleIds2["Vertical"] = "vertical";
  ImageEditorToggleIds2["UseConditioning"] = "use_conditioning";
  ImageEditorToggleIds2["RoiAuto"] = "roi_auto";
  ImageEditorToggleIds2["RoiAlignAuto"] = "roi_align_auto";
  ImageEditorToggleIds2["ApplyUnsharpMask"] = "apply_unsharp_mask";
})(ImageEditorToggleIds || (ImageEditorToggleIds = {}));
var ImageEditorBackgroundRemoverIds;
(function(ImageEditorBackgroundRemoverIds2) {
  ImageEditorBackgroundRemoverIds2["Color"] = "color";
  ImageEditorBackgroundRemoverIds2["TransparentBackground"] = "transparent_background";
})(ImageEditorBackgroundRemoverIds || (ImageEditorBackgroundRemoverIds = {}));
var ImageEditorBlendIds;
(function(ImageEditorBlendIds2) {
  ImageEditorBlendIds2["Opacity"] = "opacity";
})(ImageEditorBlendIds || (ImageEditorBlendIds = {}));
var ImageEditorBloomIds;
(function(ImageEditorBloomIds2) {
  ImageEditorBloomIds2["Threshold"] = "threshold";
  ImageEditorBloomIds2["Radius"] = "radius";
  ImageEditorBloomIds2["Intensity"] = "intensity";
  ImageEditorBloomIds2["Tint"] = "tint";
})(ImageEditorBloomIds || (ImageEditorBloomIds = {}));
var ImageEditorBrightnessIds;
(function(ImageEditorBrightnessIds2) {
  ImageEditorBrightnessIds2["Strength"] = "strength";
  ImageEditorBrightnessIds2["Gamma"] = "gamma";
  ImageEditorBrightnessIds2["Midpoint"] = "midpoint";
  ImageEditorBrightnessIds2["Localized"] = "localized";
})(ImageEditorBrightnessIds || (ImageEditorBrightnessIds = {}));
var ImageEditorBrushIds;
(function(ImageEditorBrushIds2) {
  ImageEditorBrushIds2["B64Canvas"] = "b64_canvas";
  ImageEditorBrushIds2["Color"] = "color";
  ImageEditorBrushIds2["Opacity"] = "opacity";
  ImageEditorBrushIds2["Size"] = "size";
})(ImageEditorBrushIds || (ImageEditorBrushIds = {}));
var ImageEditorClarityIds;
(function(ImageEditorClarityIds2) {
  ImageEditorClarityIds2["Amount"] = "clarity_amount";
})(ImageEditorClarityIds || (ImageEditorClarityIds = {}));
var ImageEditorContrastIds;
(function(ImageEditorContrastIds2) {
  ImageEditorContrastIds2["Strength"] = "strength";
  ImageEditorContrastIds2["Localized"] = "contrast";
  ImageEditorContrastIds2["Midpoint"] = "midpoint";
})(ImageEditorContrastIds || (ImageEditorContrastIds = {}));
var ImageEditorDesaturateIds;
(function(ImageEditorDesaturateIds2) {
  ImageEditorDesaturateIds2["RedChannel"] = "r_channel";
  ImageEditorDesaturateIds2["GreenChannel"] = "g_channel";
  ImageEditorDesaturateIds2["BlueChannel"] = "b_channel";
  ImageEditorDesaturateIds2["Strength"] = "strength";
})(ImageEditorDesaturateIds || (ImageEditorDesaturateIds = {}));
var ImageEditorFilmGrainIds;
(function(ImageEditorFilmGrainIds2) {
  ImageEditorFilmGrainIds2["Intensity"] = "intensity";
  ImageEditorFilmGrainIds2["Size"] = "size";
  ImageEditorFilmGrainIds2["Tint"] = "tint";
  ImageEditorFilmGrainIds2["SoftBlend"] = "soft_blend";
})(ImageEditorFilmGrainIds || (ImageEditorFilmGrainIds = {}));
var ImageEditorGaussianBlurIds;
(function(ImageEditorGaussianBlurIds2) {
  ImageEditorGaussianBlurIds2["BlurKernelSize"] = "blur_kernel_size";
  ImageEditorGaussianBlurIds2["BlurSigma"] = "blur_sigma";
})(ImageEditorGaussianBlurIds || (ImageEditorGaussianBlurIds = {}));
var ImageEditorLineIds;
(function(ImageEditorLineIds2) {
  ImageEditorLineIds2["Color"] = "color";
  ImageEditorLineIds2["Opacity"] = "opacity";
  ImageEditorLineIds2["Points"] = "points";
  ImageEditorLineIds2["Size"] = "size";
  ImageEditorLineIds2["Smooth"] = "smooth";
})(ImageEditorLineIds || (ImageEditorLineIds = {}));
var ImageEditorSaturationIds;
(function(ImageEditorSaturationIds2) {
  ImageEditorSaturationIds2["Intensity"] = "intensity";
})(ImageEditorSaturationIds || (ImageEditorSaturationIds = {}));
var ImageEditorSepiaIds;
(function(ImageEditorSepiaIds2) {
  ImageEditorSepiaIds2["Intensity"] = "intensity";
})(ImageEditorSepiaIds || (ImageEditorSepiaIds = {}));
var ImageEditorSplitToneIds;
(function(ImageEditorSplitToneIds2) {
  ImageEditorSplitToneIds2["Balance"] = "balance";
  ImageEditorSplitToneIds2["Highlights"] = "highlights";
  ImageEditorSplitToneIds2["Intensity"] = "intensity";
  ImageEditorSplitToneIds2["Shadows"] = "shadows";
  ImageEditorSplitToneIds2["Softness"] = "softness";
})(ImageEditorSplitToneIds || (ImageEditorSplitToneIds = {}));
var ImageEditorTiltShiftIds;
(function(ImageEditorTiltShiftIds2) {
  ImageEditorTiltShiftIds2["FocusPosition"] = "focus_position";
  ImageEditorTiltShiftIds2["FocusSize"] = "focus_size";
  ImageEditorTiltShiftIds2["Radius"] = "radius";
  ImageEditorTiltShiftIds2["Smooth"] = "smooth";
  ImageEditorTiltShiftIds2["Vertical"] = "vertical";
})(ImageEditorTiltShiftIds || (ImageEditorTiltShiftIds = {}));
var ImageEditorUnsharpMaskIds;
(function(ImageEditorUnsharpMaskIds2) {
  ImageEditorUnsharpMaskIds2["Amount"] = "amount";
  ImageEditorUnsharpMaskIds2["Radius"] = "radius";
  ImageEditorUnsharpMaskIds2["Sigma"] = "sigma";
  ImageEditorUnsharpMaskIds2["Threshold"] = "threshold";
})(ImageEditorUnsharpMaskIds || (ImageEditorUnsharpMaskIds = {}));
var ImageEditorVibranceIds;
(function(ImageEditorVibranceIds2) {
  ImageEditorVibranceIds2["Intensity"] = "intensity";
  ImageEditorVibranceIds2["ClipSoft"] = "clip_soft";
  ImageEditorVibranceIds2["ProtectSkin"] = "protect_skin";
})(ImageEditorVibranceIds || (ImageEditorVibranceIds = {}));
var ImageEditorVignetteIds;
(function(ImageEditorVignetteIds2) {
  ImageEditorVignetteIds2["Color"] = "color";
  ImageEditorVignetteIds2["Intensity"] = "intensity";
  ImageEditorVignetteIds2["Radius"] = "radius";
  ImageEditorVignetteIds2["Shape"] = "shape";
})(ImageEditorVignetteIds || (ImageEditorVignetteIds = {}));
var ImageEditorInpaintIds;
(function(ImageEditorInpaintIds2) {
  ImageEditorInpaintIds2["B64Canvas"] = "b64_canvas";
  ImageEditorInpaintIds2["ApplyUnsharpMask"] = "apply_unsharp_mask";
  ImageEditorInpaintIds2["Cfg"] = "cfg";
  ImageEditorInpaintIds2["ConditioningMix"] = "conditioning_mix";
  ImageEditorInpaintIds2["DenoisePercentage"] = "denoise_percentage";
  ImageEditorInpaintIds2["NegativePrompt"] = "negative_prompt";
  ImageEditorInpaintIds2["PositivePrompt"] = "positive_prompt";
  ImageEditorInpaintIds2["Seed"] = "seed";
  ImageEditorInpaintIds2["Steps"] = "steps";
  ImageEditorInpaintIds2["UseConditioning"] = "use_conditioning";
  ImageEditorInpaintIds2["RoiAuto"] = "roi_auto";
  ImageEditorInpaintIds2["RoiPadding"] = "roi_padding";
  ImageEditorInpaintIds2["RoiAlign"] = "roi_align";
  ImageEditorInpaintIds2["RoiAlignAuto"] = "roi_align_auto";
  ImageEditorInpaintIds2["RoiMinSize"] = "roi_min_size";
  ImageEditorInpaintIds2["Dilate"] = "dilate";
  ImageEditorInpaintIds2["Feather"] = "feather";
  ImageEditorInpaintIds2["UpsampleTarget"] = "upsample_target";
})(ImageEditorInpaintIds || (ImageEditorInpaintIds = {}));
const BACKGROUND_SETTINGS = {
  backgroundRemover: {
    controlIds: ImageEditorBackgroundRemoverIds,
    settings: {
      color: "#000000",
      transparent_background: true
    },
    configs: {
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Background color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#000000",
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: "Used to fill the removed background when transparency is disabled.",
          type: "color"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Transparent background",
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.TransparentBackground,
          off: "false",
          on: "true",
          title: "Keep an alpha channel instead of filling the background with the selected color."
        }
      ]
    }
  }
};
const BASIC_ADJUSTMENT_SETTINGS = {
  //#region Brightness
  brightness: {
    controlIds: ImageEditorBrightnessIds,
    settings: {
      strength: 0,
      gamma: 0,
      localized: false,
      midpoint: 0.5
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Brightness Strength",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: "1",
          min: "-1",
          step: "0.05",
          title: "Adjust the brightness of the image. Negative values darken, positive values brighten."
        },
        {
          ariaLabel: "Gamma",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Gamma,
          max: "3",
          min: "0.1",
          step: "0.1",
          title: "Adjust the gamma correction. Values < 1 brighten shadows, > 1 darken highlights."
        },
        {
          ariaLabel: "Midpoint",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Midpoint,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Defines the tonal midpoint for brightness scaling."
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Localized Brightness",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Localized,
          off: "false",
          on: "true",
          title: "Enhance brightness locally in darker regions."
        }
      ]
    }
  },
  //#endregion
  //#region Clarity
  clarity: {
    controlIds: ImageEditorClarityIds,
    settings: {
      clarity_amount: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Clarity Amount",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.ClarityAmount,
          isMandatory: true,
          max: "1",
          min: "-1",
          step: "0.05",
          title: "Lightroom-style clarity. Negative values soften details, positive values boost local contrast."
        }
      ]
    }
  },
  //#endregion
  //#region Contrast
  contrast: {
    controlIds: ImageEditorContrastIds,
    settings: {
      strength: 0,
      localized: false,
      midpoint: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Contrast Strength",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: "1",
          min: "-1",
          step: "0.05",
          title: "Controls the intensity of the contrast adjustment. 1.0 is no change, below 1 reduces contrast, above 1 increases contrast."
        },
        {
          ariaLabel: "Midpoint",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Midpoint,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Defines the tonal midpoint for contrast scaling."
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Localized Contrast",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Localized,
          off: "false",
          on: "true",
          title: "Apply contrast enhancement locally to edges and textures."
        }
      ]
    }
  },
  //#endregion
  //#region Desaturate
  desaturate: {
    controlIds: ImageEditorDesaturateIds,
    settings: {
      r_channel: 1,
      g_channel: 1,
      b_channel: 1,
      strength: 0
    },
    configs: {
      slider: [
        {
          ariaLabel: "Desaturation strength",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the intensity of the desaturation. 0 is no effect, 1 is fully desaturated."
        },
        {
          ariaLabel: "Red channel level",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.RedChannel,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the intensity of the red channel desaturation relative to the total strength of the filter."
        },
        {
          ariaLabel: "Green channel level",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.GreenChannel,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the intensity of the green channel desaturation relative to the total strength of the filter."
        },
        {
          ariaLabel: "Blue channel level",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.BlueChannel,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the intensity of the blue channel desaturation relative to the total strength of the filter."
        }
      ]
    }
  },
  //#endregion
  //#region Saturation
  saturation: {
    controlIds: ImageEditorSaturationIds,
    settings: {
      intensity: 1
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Saturation Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "5",
          min: "0",
          step: "0.1",
          title: "Controls the intensity of the saturation adjustment. 1.0 is no change, below 1 reduces saturation, above 1 increases saturation."
        }
      ]
    }
  },
  //#endregion
  //#region Unsharp Mask
  unsharpMask: {
    controlIds: ImageEditorUnsharpMaskIds,
    settings: {
      amount: 0.5,
      radius: 5,
      sigma: 1,
      threshold: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Sharpen Amount",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Amount,
          isMandatory: true,
          max: "5",
          min: "0",
          step: "0.05",
          title: "Overall strength applied to the high-frequency detail mask."
        },
        {
          ariaLabel: "Radius",
          controlType: ImageEditorControls.Slider,
          defaultValue: 5,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: "31",
          min: "1",
          step: "2",
          title: "Gaussian blur kernel size (odd numbers give the best results)."
        },
        {
          ariaLabel: "Sigma",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Sigma,
          isMandatory: true,
          max: "5",
          min: "0.1",
          step: "0.1",
          title: "Gaussian blur sigma controlling feather softness around edges."
        },
        {
          ariaLabel: "Threshold",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Threshold,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Skip sharpening for pixels below this normalized contrast level."
        }
      ]
    }
    //#endregion
  }
};
const CREATIVE_EFFECT_SETTINGS = {
  //#region Blend
  blend: {
    controlIds: ImageEditorBlendIds,
    settings: {
      color: "#FF0000",
      opacity: 0.5
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Opacity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Adjust the opacity of the blended layer."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FF0000",
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: "Sets the solid color that will be blended onto the image.",
          type: "color"
        }
      ]
    }
  },
  //#endregion
  //#region Bloom
  bloom: {
    controlIds: ImageEditorBloomIds,
    settings: {
      intensity: 0.6,
      radius: 15,
      threshold: 0.8,
      tint: "#FFFFFF"
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Bloom Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.6,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "2",
          min: "0",
          step: "0.05",
          title: "How strong the bloom reads after compositing. 1.0 = add the blurred highlights at full strength."
        },
        {
          ariaLabel: "Bloom Radius",
          controlType: ImageEditorControls.Slider,
          defaultValue: 15,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: "127",
          min: "3",
          step: "2",
          title: "Blur radius in pixels (odd numbers only). Bigger radius → softer, more cinematic glow."
        },
        {
          ariaLabel: "Threshold",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.8,
          id: ImageEditorSliderIds.Threshold,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Bright-pass cutoff. 0 = everything glows, 1 = nothing glows. For dim scenes start around 0.15-0.35."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Tint Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FFFFFF",
          id: ImageEditorTextfieldIds.Color,
          title: "Hex color for the glow (e.g., FFCCAA). Pure white FFFFFF keeps original hue.",
          type: "color"
        }
      ]
    }
  },
  //#endregion
  //#region Film Grain
  filmGrain: {
    controlIds: ImageEditorFilmGrainIds,
    settings: { intensity: 0, size: 1, soft_blend: false, tint: "#FFFFFF" },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Sets the strength of the filter."
        },
        {
          ariaLabel: "Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: "5",
          min: "0.5",
          step: "0.1",
          title: "Sets the size of the noise's granularity."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Tint",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FFFFFF",
          id: ImageEditorTextfieldIds.Tint,
          isMandatory: true,
          title: "Hexadecimal color (default is FFFFFF for no tint).",
          type: "color"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Soft blend",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.SoftBlend,
          title: "If True, uses a soft blending mode for the grain.",
          off: "false",
          on: "true"
        }
      ]
    }
  },
  //#endregion
  //#region Gaussian Blur
  gaussianBlur: {
    controlIds: ImageEditorGaussianBlurIds,
    settings: {
      blur_kernel_size: 1,
      blur_sigma: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Blur Sigma",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.BlurSigma,
          max: "10",
          min: "0.1",
          step: "0.1",
          title: "Standard deviation for the Gaussian kernel. Controls blur intensity."
        },
        {
          ariaLabel: "Blur Kernel Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 7,
          id: ImageEditorSliderIds.BlurKernelSize,
          max: "51",
          min: "1",
          step: "2",
          title: "Controls the size of the Gaussian blur kernel. Higher values mean more smoothing."
        }
      ]
    }
  },
  //#endregion
  //#region Sepia
  sepia: {
    controlIds: ImageEditorSepiaIds,
    settings: {
      intensity: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Sepia Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Controls the intensity of the sepia effect."
        }
      ]
    }
  },
  //#endregion
  //#region Split Tone
  splitTone: {
    controlIds: ImageEditorSplitToneIds,
    settings: {
      balance: 0.5,
      highlights: "#FFAA55",
      intensity: 0.6,
      shadows: "#0066FF",
      softness: 0.25
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.6,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "2",
          min: "0",
          step: "0.05",
          title: "Strength of the tint applied."
        },
        {
          ariaLabel: "Balance",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Balance,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Luminance pivot. 0 = lift even deep blacks; 1 = tint only the brightest pixels."
        },
        {
          ariaLabel: "Softness",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.25,
          id: ImageEditorSliderIds.Softness,
          isMandatory: true,
          max: "0.5",
          min: "0.01",
          step: "0.01",
          title: "Width of the transition band around the balance value."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Highlights",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FFAA55",
          id: ImageEditorTextfieldIds.Highlights,
          title: "Hex colour applied to highlights (e.g. FFAA55).",
          type: "color"
        },
        {
          ariaLabel: "Shadows",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#0066FF",
          id: ImageEditorTextfieldIds.Shadows,
          title: "Hex colour applied to shadows (e.g. 0066FF).",
          type: "color"
        }
      ]
    }
  },
  //#endregion
  //#region Tilt Shift
  tiltShift: {
    controlIds: ImageEditorTiltShiftIds,
    settings: {
      focus_position: 0.5,
      focus_size: 0.25,
      radius: 25,
      smooth: false,
      vertical: false
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Focus Position",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.FocusPosition,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Vertical center of the sharp band (0 = top, 1 = bottom)."
        },
        {
          ariaLabel: "Focus Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.25,
          id: ImageEditorSliderIds.FocusSize,
          isMandatory: true,
          max: "0.9",
          min: "0.05",
          step: "0.01",
          title: "Height of the sharp zone as a fraction of the image."
        },
        {
          ariaLabel: "Blur Radius",
          controlType: ImageEditorControls.Slider,
          defaultValue: 25,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: "151",
          min: "3",
          step: "2",
          title: "Gaussian radius for out-of-focus areas. Higher values mean more blur and less detail."
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Smooth Fall-off Curve",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Smooth,
          off: "linear",
          on: "smooth",
          title: "Fall-off curve of blur vs distance. Linear means a constant fall-off, smooth means a gradual transition."
        },
        {
          ariaLabel: "Vertical Orientation",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Vertical,
          off: "horizontal",
          on: "vertical",
          title: "Direction of the focus band. Horizontal means the focus band is horizontal, vertical means it is vertical."
        }
      ]
    }
  },
  //#endregion
  //#region Vibrance
  vibrance: {
    controlIds: ImageEditorVibranceIds,
    settings: {
      intensity: 0,
      protect_skin: true,
      clip_soft: true
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Vibrance Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "2",
          min: "-1",
          step: "0.05",
          title: "Controls the intensity of the vibrance adjustment. Negative values reduce vibrance, positive values increase it."
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Protect Skin Tones",
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.ProtectSkin,
          off: "false",
          on: "true",
          title: "If true, skin tones are less affected by the vibrance adjustment."
        },
        {
          ariaLabel: "Clip Softly",
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.ClipSoft,
          off: "false",
          on: "true",
          title: "If true, saturation is rolled off near maximum to avoid clipping."
        }
      ]
    }
  },
  //#endregion
  //#region Vignette
  vignette: {
    controlIds: ImageEditorVignetteIds,
    settings: {
      intensity: 0,
      radius: 0,
      shape: false,
      color: "000000"
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Vignette Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the darkness of the vignette effect. Higher values mean darker edges."
        },
        {
          ariaLabel: "Vignette Radius",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the size of the vignette effect. Lower values mean a smaller vignette."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#000000",
          id: ImageEditorTextfieldIds.Color,
          title: "Sets the color of the vignette.",
          type: "color"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Circular",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Shape,
          off: "elliptical",
          on: "circular",
          title: "Selects the shape of the vignette effect, defaults to elliptical."
        }
      ]
    }
  }
  //#endregion
};
const DIFFUSION_SETTINGS = {
  //#region Inpaint
  inpaint: {
    controlIds: ImageEditorInpaintIds,
    hasCanvasAction: true,
    requiresManualApply: true,
    settings: {
      b64_canvas: "",
      cfg: 7,
      denoise_percentage: 40,
      steps: 16,
      positive_prompt: "",
      negative_prompt: "",
      upsample_target: 2048,
      use_conditioning: true,
      conditioning_mix: -1,
      apply_unsharp_mask: true
    },
    configs: {
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Positive prompt",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "",
          id: ImageEditorTextfieldIds.PositivePrompt,
          isMandatory: false,
          title: "Prompt applied to masked pixels.",
          type: "text"
        },
        {
          ariaLabel: "Negative prompt",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "",
          id: ImageEditorTextfieldIds.NegativePrompt,
          isMandatory: false,
          title: "Negative prompt applied to masked pixels.",
          type: "text"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Use conditioning prompts",
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.UseConditioning,
          isMandatory: false,
          off: "false",
          on: "true",
          title: "If enabled, prepend the connected conditioning inputs to the prompts before sampling."
        }
      ],
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Conditioning mix",
          controlType: ImageEditorControls.Slider,
          defaultValue: -1,
          id: ImageEditorSliderIds.ConditioningMix,
          isMandatory: false,
          max: "1",
          min: "-1",
          step: "0.1",
          title: "Blend input conditioning (-1) with inpaint prompts (1). 0 keeps both contributions balanced."
        },
        {
          ariaLabel: "Denoise percentage",
          controlType: ImageEditorControls.Slider,
          defaultValue: 40,
          id: ImageEditorSliderIds.DenoisePercentage,
          isMandatory: true,
          max: "100",
          min: "0",
          step: "1",
          title: "Noise applied during inpaint. 0 keeps original pixels, 100 fully regenerates."
        },
        {
          ariaLabel: "CFG scale",
          controlType: ImageEditorControls.Slider,
          defaultValue: 7,
          id: ImageEditorSliderIds.Cfg,
          isMandatory: true,
          max: "30",
          min: "1",
          step: "0.5",
          title: "Classifier-free guidance applied during the inpaint pass."
        },
        {
          ariaLabel: "Steps",
          controlType: ImageEditorControls.Slider,
          defaultValue: 16,
          id: ImageEditorSliderIds.Steps,
          isMandatory: true,
          max: "30",
          min: "1",
          step: "1",
          title: "Diffusion steps used for the inpaint sampler."
        },
        {
          ariaLabel: "Upsample target (px)",
          controlType: ImageEditorControls.Slider,
          defaultValue: 2048,
          id: ImageEditorSliderIds.UpsampleTarget,
          isMandatory: false,
          max: "2048",
          min: "0",
          step: "16",
          title: "Detailer path: upscale ROI longer side to this size before inpaint (0 disables)."
        }
      ]
    }
  }
  //#endregion
};
const INPAINT_ADV = {
  //#region Inpaint (adv.)
  controlIds: ImageEditorInpaintIds,
  hasCanvasAction: true,
  requiresManualApply: true,
  settings: {
    ...DIFFUSION_SETTINGS.inpaint.settings,
    use_conditioning: false,
    conditioning_mix: 0,
    apply_unsharp_mask: true,
    roi_auto: true,
    roi_padding: 32,
    roi_align: 8,
    roi_align_auto: false,
    roi_min_size: 64,
    dilate: 0,
    feather: 0,
    seed: 42
  },
  configs: {
    [ImageEditorControls.Textfield]: [
      {
        ariaLabel: "Positive prompt",
        controlType: ImageEditorControls.Textfield,
        defaultValue: "",
        id: ImageEditorTextfieldIds.PositivePrompt,
        isMandatory: false,
        title: "Prompt applied to masked pixels.",
        type: "text"
      },
      {
        ariaLabel: "Negative prompt",
        controlType: ImageEditorControls.Textfield,
        defaultValue: "",
        id: ImageEditorTextfieldIds.NegativePrompt,
        isMandatory: false,
        title: "Negative prompt applied to masked pixels.",
        type: "text"
      },
      {
        ariaLabel: "Seed",
        controlType: ImageEditorControls.Textfield,
        defaultValue: "",
        id: ImageEditorTextfieldIds.Seed,
        isMandatory: false,
        title: "Optional seed override. Leave blank for a random seed.",
        type: "number"
      }
    ],
    [ImageEditorControls.Slider]: [
      {
        ariaLabel: "Conditioning mix",
        controlType: ImageEditorControls.Slider,
        defaultValue: -1,
        id: ImageEditorSliderIds.ConditioningMix,
        isMandatory: false,
        max: "1",
        min: "-1",
        step: "0.1",
        title: "Blend input conditioning (-1) with inpaint prompts (1). 0 keeps both contributions balanced."
      },
      {
        ariaLabel: "Denoise percentage",
        controlType: ImageEditorControls.Slider,
        defaultValue: 40,
        id: ImageEditorSliderIds.DenoisePercentage,
        isMandatory: true,
        max: "100",
        min: "0",
        step: "1",
        title: "Noise applied during inpaint. 0 keeps original pixels, 100 fully regenerates."
      },
      {
        ariaLabel: "CFG scale",
        controlType: ImageEditorControls.Slider,
        defaultValue: 7,
        id: ImageEditorSliderIds.Cfg,
        isMandatory: true,
        max: "30",
        min: "1",
        step: "0.5",
        title: "Classifier-free guidance applied during the inpaint pass."
      },
      {
        ariaLabel: "Steps",
        controlType: ImageEditorControls.Slider,
        defaultValue: 16,
        id: ImageEditorSliderIds.Steps,
        isMandatory: true,
        max: "30",
        min: "1",
        step: "1",
        title: "Diffusion steps used for the inpaint sampler."
      },
      {
        ariaLabel: "Upsample target (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 2048,
        id: ImageEditorSliderIds.UpsampleTarget,
        isMandatory: false,
        max: "2048",
        min: "0",
        step: "16",
        title: "Detailer path: upscale ROI longer side to this size before inpaint (0 disables)."
      },
      {
        ariaLabel: "ROI padding (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 32,
        id: ImageEditorSliderIds.RoiPadding,
        isMandatory: false,
        max: "256",
        min: "0",
        step: "1",
        title: "Pixels of padding around the mask bounding box when cropping the ROI."
      },
      {
        ariaLabel: "ROI align multiple",
        controlType: ImageEditorControls.Slider,
        defaultValue: 8,
        id: ImageEditorSliderIds.RoiAlign,
        isMandatory: false,
        max: "64",
        min: "1",
        step: "1",
        title: "Align ROI size/position to this multiple. Keeps latent-friendly dims. Disable auto-align to use."
      },
      {
        ariaLabel: "ROI minimum size (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 64,
        id: ImageEditorSliderIds.RoiMinSize,
        isMandatory: false,
        max: "1024",
        min: "1",
        step: "1",
        title: "Enforce a minimum width/height for the cropped ROI."
      },
      {
        ariaLabel: "Dilate mask (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 0,
        id: ImageEditorSliderIds.Dilate,
        isMandatory: false,
        max: "64",
        min: "0",
        step: "1",
        title: "Expand mask edges before inpaint to avoid seams."
      },
      {
        ariaLabel: "Feather mask (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 0,
        id: ImageEditorSliderIds.Feather,
        isMandatory: false,
        max: "64",
        min: "0",
        step: "1",
        title: "Soften mask edges to blend the inpainted region."
      }
    ],
    [ImageEditorControls.Toggle]: [
      {
        ariaLabel: "Use conditioning prompts",
        controlType: ImageEditorControls.Toggle,
        defaultValue: false,
        id: ImageEditorToggleIds.UseConditioning,
        isMandatory: false,
        off: "false",
        on: "true",
        title: "If enabled, prepend the connected conditioning inputs to the prompts before sampling."
      },
      {
        ariaLabel: "Auto ROI crop",
        controlType: ImageEditorControls.Toggle,
        defaultValue: true,
        id: ImageEditorToggleIds.RoiAuto,
        isMandatory: false,
        off: "false",
        on: "true",
        title: "Automatically crop to mask bounding box to speed up inpainting."
      },
      {
        ariaLabel: "Auto-align ROI",
        controlType: ImageEditorControls.Toggle,
        defaultValue: false,
        id: ImageEditorToggleIds.RoiAlignAuto,
        isMandatory: false,
        off: "false",
        on: "true",
        title: "Infer alignment multiple from VAE/model. Disable to set a manual multiple (see slider)."
      },
      {
        ariaLabel: "Apply unsharp mask",
        controlType: ImageEditorControls.Toggle,
        defaultValue: true,
        id: ImageEditorToggleIds.ApplyUnsharpMask,
        isMandatory: false,
        off: "false",
        on: "true",
        title: "Apply a gentle unsharp mask after downscaling the inpainted region."
      }
    ]
  }
  //#endregion
};
const DRAWING_SETTINGS = {
  //#region Brush
  brush: {
    controlIds: ImageEditorBrushIds,
    hasCanvasAction: true,
    settings: { b64_canvas: "", color: "#FF0000", opacity: 0.2, size: 150 },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 150,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: "500",
          min: "1",
          step: "1",
          title: "Sets the size of the brush."
        },
        {
          ariaLabel: "Opacity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.2,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: "1",
          min: "0.05",
          step: "0.05",
          title: "Sets the opacity of the brush."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FF0000",
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: "Sets the color of the brush stroke.",
          type: "color"
        }
      ]
    }
  },
  //#endregion
  //#region Line
  line: {
    controlIds: ImageEditorLineIds,
    hasCanvasAction: true,
    settings: { color: "#FF0000", opacity: 1, points: [], size: 10, smooth: false },
    configs: {
      [ImageEditorControls.Canvas]: [],
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 10,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: "500",
          min: "1",
          step: "1",
          title: "Sets the size of the brush."
        },
        {
          ariaLabel: "Opacity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: "1",
          min: "0.05",
          step: "0.05",
          title: "Sets the opacity of the brush."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FF0000",
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: "Sets the color of the brush stroke.",
          type: "color"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Smooth",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Smooth,
          title: "Draws a smooth line.",
          off: "false",
          on: "true"
        }
      ]
    }
  }
  //#endregion
};
const SETTINGS = {
  ...BASIC_ADJUSTMENT_SETTINGS,
  ...BACKGROUND_SETTINGS,
  ...CREATIVE_EFFECT_SETTINGS,
  ...DRAWING_SETTINGS,
  ...DIFFUSION_SETTINGS
};
const TREE_DATA = {
  nodes: [
    //#region Settings
    {
      description: "Tool configuration.",
      id: "settings",
      icon: "brush",
      value: "Settings",
      children: [
        {
          description: "Brush configuration.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.brush)
            }
          },
          id: "brush",
          value: "Brush"
        }
      ]
    },
    //#endregion
    //#region Diffusion Tools
    {
      description: "Diffusion-based retouching tools.",
      id: "diffusion_tools",
      value: "Diffusion Tools",
      icon: "wand",
      children: [
        {
          description: "Inpaint masked areas using the connected diffusion model.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.inpaint)
            }
          },
          id: "inpaint",
          value: "Inpaint"
        },
        {
          description: "Inpaint with advanced ROI controls.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(INPAINT_ADV)
            }
          },
          id: "inpaint_adv",
          value: "Inpaint (adv.)"
        }
      ]
    },
    //#endregion
    //#region Cutouts
    {
      description: "Background removal and matting tools.",
      id: "cutouts",
      value: "Cutouts",
      icon: "replace",
      children: [
        {
          description: "Remove the background using rembg with optional solid fill.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.backgroundRemover)
            }
          },
          id: "background_remover",
          value: "Background remover"
        }
      ]
    },
    //#endregion
    //#region Basic Adjustments
    {
      description: "Basic adjustments such as sharpening and color tuning.",
      id: "basic_adjustments",
      value: "Basic Adjustments",
      icon: "settings",
      children: [
        {
          description: "Adjusts the brightness.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.brightness)
            }
          },
          id: "brightness",
          value: "Brightness"
        },
        {
          description: "Simulates the Lightroom clarity effect.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.clarity)
            }
          },
          id: "clarity",
          value: "Clarity"
        },
        {
          description: "Sharpens edges using a classic unsharp mask pipeline.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.unsharpMask)
            }
          },
          id: "unsharp_mask",
          value: "Unsharp Mask"
        },
        {
          description: "Adjusts the contrast.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.contrast)
            }
          },
          id: "contrast",
          value: "Contrast"
        },
        {
          description: "Reduces the saturation.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.desaturate)
            }
          },
          id: "desaturate",
          value: "Desaturate"
        },
        {
          description: "Adjusts the saturation.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.saturation)
            }
          },
          id: "saturation",
          value: "Saturation"
        }
      ]
    },
    //#endregion
    //#region Creative Effects
    {
      description: "Artistic filters, such as vignette effect and gaussian blur.",
      id: "creative_effects",
      icon: "palette",
      value: "Creative Effects",
      children: [
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.blend)
            }
          },
          description: "Blends a color layer onto the image.",
          id: "blend",
          value: "Blend"
        },
        {
          description: "Applies a bloom effect.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.bloom)
            }
          },
          id: "bloom",
          value: "Bloom"
        },
        {
          description: "Applies a film grain effect.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.filmGrain)
            }
          },
          id: "film_grain",
          value: "Film grain"
        },
        {
          description: "Blurs the image.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.gaussianBlur)
            }
          },
          id: "gaussian_blur",
          value: "Gaussian blur"
        },
        {
          description: "Draws a line.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.line)
            }
          },
          id: "line",
          value: "Line"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.sepia)
            }
          },
          description: "Applies a sepia effect to the image.",
          id: "sepia",
          value: "Sepia"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.splitTone)
            }
          },
          description: "Applies a split tone effect to the image.",
          id: "split_tone",
          value: "Split tone"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.tiltShift)
            }
          },
          description: "Applies a tilt-shift effect to the image.",
          id: "tilt_shift",
          value: "Tilt-shift"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.vibrance)
            }
          },
          description: "Applies a vibrance effect to the image.",
          id: "vibrance",
          value: "Vibrance"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.vignette)
            }
          },
          description: "Applies a vignetting effect to the image.",
          id: "vignette",
          value: "Vignette"
        }
      ]
    }
    //#endregion
  ]
};
var LfEventName;
(function(LfEventName2) {
  LfEventName2["LfAccordion"] = "lf-accordion-event";
  LfEventName2["LfArticle"] = "lf-article-event";
  LfEventName2["LfButton"] = "lf-button-event";
  LfEventName2["LfCanvas"] = "lf-canvas-event";
  LfEventName2["LfCard"] = "lf-card-event";
  LfEventName2["LfCarousel"] = "lf-carousel-event";
  LfEventName2["LfChat"] = "lf-chat-event";
  LfEventName2["LfChart"] = "lf-chart-event";
  LfEventName2["LfChip"] = "lf-chip-event";
  LfEventName2["LfCode"] = "lf-code-event";
  LfEventName2["LfCompare"] = "lf-compare-event";
  LfEventName2["LfImageviewer"] = "lf-imageviewer-event";
  LfEventName2["LfList"] = "lf-list-event";
  LfEventName2["LfManager"] = "lf-manager-ready";
  LfEventName2["LfMasonry"] = "lf-masonry-event";
  LfEventName2["LfMessenger"] = "lf-messenger-event";
  LfEventName2["LfProgressbar"] = "lf-progressbar-event";
  LfEventName2["LfSlider"] = "lf-slider-event";
  LfEventName2["LfSpinner"] = "lf-spinner-event";
  LfEventName2["LfTabbar"] = "lf-tabbar-event";
  LfEventName2["LfTextfield"] = "lf-textfield-event";
  LfEventName2["LfToggle"] = "lf-toggle-event";
  LfEventName2["LfTree"] = "lf-tree-event";
  LfEventName2["LfUpload"] = "lf-upload-event";
  LfEventName2["Textarea"] = "textarea-event";
})(LfEventName || (LfEventName = {}));
function getPathColumn(dataset) {
  var _a;
  return ((_a = dataset == null ? void 0 : dataset.columns) == null ? void 0 : _a.find((c) => c.id === ImageEditorColumnId.Path)) || null;
}
function getStatusColumn(dataset) {
  var _a;
  return ((_a = dataset == null ? void 0 : dataset.columns) == null ? void 0 : _a.find((c) => c.id === ImageEditorColumnId.Status)) || null;
}
function parseLabel(data) {
  return data.isMandatory ? `${data.ariaLabel}*` : data.ariaLabel;
}
const refreshValues = async (state, addSnapshot = false) => {
  const { elements, filter } = state;
  const { controls } = elements;
  const lfManager = getLfManager();
  state.settingsStore = state.settingsStore ?? {};
  const storeForFilter = state.settingsStore[state.filterType] = state.settingsStore[state.filterType] ?? {};
  for (const key in controls) {
    if (Object.prototype.hasOwnProperty.call(controls, key)) {
      const id = key;
      const control = controls[id];
      switch (control.tagName) {
        case "LF-SLIDER": {
          const slider = control;
          const sliderValue = await slider.getValue();
          const value = addSnapshot ? sliderValue.real : sliderValue.display;
          filter.settings[id] = value;
          storeForFilter[id] = value;
          break;
        }
        case "LF-TEXTFIELD": {
          const textfield = control;
          const textfieldValue = await textfield.getValue();
          filter.settings[id] = textfieldValue;
          storeForFilter[id] = textfieldValue;
          break;
        }
        case "LF-TOGGLE": {
          const toggle = control;
          const toggleValue = await toggle.getValue();
          const value = toggleValue === "on" ? toggle.dataset.on : toggle.dataset.off;
          filter.settings[id] = value;
          storeForFilter[id] = value;
          break;
        }
        default:
          lfManager.log(`Unhandled control type: ${control.tagName}`, { control }, LogSeverity.Warning);
          continue;
      }
    }
  }
};
const updateCb = async (state, addSnapshot = false, force = false) => {
  await refreshValues(state, addSnapshot);
  const { elements, filter } = state;
  const { imageviewer } = elements;
  if (!filter) {
    return false;
  }
  const { settings } = filter;
  const validValues = isValidObject(settings);
  const isCanvasAction = settings.points || settings.b64_canvas;
  const hasCanvasAction = filter.hasCanvasAction;
  if (validValues && hasCanvasAction) {
    const canvas = (await imageviewer.getComponents()).details.canvas;
    const brushDefaults = {
      ...SETTINGS.brush.settings,
      ...state.lastBrushSettings
    };
    const candidateSettings = settings ?? {};
    const brushSettings = {
      color: candidateSettings.color ?? brushDefaults.color,
      opacity: candidateSettings.opacity ?? brushDefaults.opacity,
      size: candidateSettings.size ?? brushDefaults.size
    };
    canvas.lfColor = brushSettings.color;
    canvas.lfOpacity = brushSettings.opacity;
    canvas.lfSize = brushSettings.size;
    state.lastBrushSettings = {
      ...state.lastBrushSettings,
      color: brushSettings.color,
      opacity: brushSettings.opacity,
      size: brushSettings.size
    };
  }
  const shouldUpdate = validValues && (!hasCanvasAction || isCanvasAction);
  const requiresManualApply = !!(filter == null ? void 0 : filter.requiresManualApply);
  let success = false;
  if (shouldUpdate && (force || !requiresManualApply)) {
    success = await apiCall$2(state, addSnapshot);
  }
  return success;
};
const createPrepSettings = (deps) => {
  const { onSlider, onTextfield, onToggle } = deps;
  return (state, node) => {
    var _a;
    const { syntax } = getLfManager().getManagers().lfFramework;
    state.elements.controls = {};
    state.filter = syntax.json.unescape(node.cells.lfCode.value).parsedJSON;
    const idRaw = node.id || "brush";
    const alias = idRaw === "inpaint_detail" || idRaw === "inpaint_adv" ? "inpaint" : idRaw;
    state.filterType = alias;
    state.manualApply = void 0;
    const dataset = state.elements.imageviewer.lfDataset;
    const defaults = (_a = dataset == null ? void 0 : dataset.defaults) == null ? void 0 : _a[state.filterType];
    if (defaults) {
      applyFilterDefaults(state, defaults);
    }
    state.settingsStore = state.settingsStore ?? {};
    const stored = state.settingsStore[state.filterType] ?? {};
    const mutableSettings = state.filter.settings;
    Object.keys(stored).forEach((id) => {
      const storedValue = stored[id];
      if (typeof storedValue === "undefined") {
        return;
      }
      mutableSettings[id] = storedValue;
    });
    const { elements, filter } = state;
    const { settings } = elements;
    if (!(filter == null ? void 0 : filter.configs)) {
      return;
    }
    settings.innerHTML = "";
    const controlsContainer = document.createElement(TagName.Div);
    controlsContainer.classList.add(ImageEditorCSS.SettingsControls);
    settings.appendChild(controlsContainer);
    const controlGroups = Object.keys(filter.configs);
    controlGroups.forEach((controlType) => {
      const configs = filter.configs[controlType];
      if (!configs) {
        return;
      }
      configs.forEach((config) => {
        switch (controlType) {
          case ImageEditorControls.Slider: {
            const sliderConfig = config;
            const slider = document.createElement(TagName.LfSlider);
            slider.lfLabel = parseLabel(sliderConfig);
            slider.lfLeadingLabel = true;
            slider.lfMax = Number(sliderConfig.max);
            slider.lfMin = Number(sliderConfig.min);
            slider.lfStep = Number(sliderConfig.step);
            slider.lfStyle = ".form-field { width: 100%; }";
            slider.lfValue = Number(sliderConfig.defaultValue);
            slider.title = sliderConfig.title;
            slider.dataset.id = sliderConfig.id;
            slider.addEventListener(LfEventName.LfSlider, (event) => onSlider(state, event));
            const storedValue = stored[sliderConfig.id];
            if (typeof storedValue !== "undefined") {
              slider.lfValue = Number(storedValue);
            }
            controlsContainer.appendChild(slider);
            state.elements.controls[sliderConfig.id] = slider;
            break;
          }
          case ImageEditorControls.Textfield: {
            const textfieldConfig = config;
            const textfield = document.createElement(TagName.LfTextfield);
            textfield.lfLabel = parseLabel(textfieldConfig);
            textfield.lfHtmlAttributes = { type: textfieldConfig.type };
            textfield.lfValue = String(textfieldConfig.defaultValue).valueOf();
            textfield.title = textfieldConfig.title;
            textfield.dataset.id = textfieldConfig.id;
            textfield.addEventListener(LfEventName.LfTextfield, (event) => onTextfield(state, event));
            const storedValue = stored[textfieldConfig.id];
            if (typeof storedValue !== "undefined") {
              textfield.lfValue = String(storedValue);
            }
            controlsContainer.appendChild(textfield);
            state.elements.controls[textfieldConfig.id] = textfield;
            break;
          }
          case ImageEditorControls.Toggle: {
            const toggleConfig = config;
            const toggle = document.createElement(TagName.LfToggle);
            toggle.dataset.off = toggleConfig.off;
            toggle.dataset.on = toggleConfig.on;
            toggle.lfLabel = parseLabel(toggleConfig);
            toggle.lfValue = toggleConfig.defaultValue ?? false;
            toggle.title = toggleConfig.title;
            toggle.dataset.id = toggleConfig.id;
            toggle.addEventListener(LfEventName.LfToggle, (event) => onToggle(state, event));
            const storedValue = stored[toggleConfig.id];
            if (typeof storedValue !== "undefined") {
              const boolValue = storedValue === true || typeof storedValue === "string" && storedValue.toLowerCase() === "true";
              toggle.lfValue = boolValue;
            }
            controlsContainer.appendChild(toggle);
            state.elements.controls[toggleConfig.id] = toggle;
            break;
          }
          default:
            throw new Error(`Unknown control type: ${controlType}`);
        }
      });
    });
    const buttonsWrapper = document.createElement(TagName.Div);
    buttonsWrapper.classList.add(ImageEditorCSS.SettingsButtons);
    settings.appendChild(buttonsWrapper);
    const resetButton = document.createElement(TagName.LfButton);
    resetButton.lfIcon = ImageEditorIcons.Reset;
    resetButton.lfLabel = "Reset";
    resetButton.lfStretchX = true;
    resetButton.addEventListener("click", () => {
      void (async () => {
        await resetSettings(settings);
        registerManualApplyChange(state);
      })();
    });
    buttonsWrapper.appendChild(resetButton);
    if (state.filterType === "brush") {
      const brushSettings = state.filter.settings ?? {};
      state.lastBrushSettings = {
        ...state.lastBrushSettings,
        ...JSON.parse(JSON.stringify(brushSettings))
      };
    }
    if (filter == null ? void 0 : filter.hasCanvasAction) {
      requestAnimationFrame(async () => {
        const canvas = (await state.elements.imageviewer.getComponents()).details.canvas;
        const brushSource = {
          ...SETTINGS.brush.settings,
          ...state.lastBrushSettings,
          ...state.filter.settings ?? {}
        };
        if (brushSource.color) {
          canvas.lfColor = brushSource.color;
        }
        if (typeof brushSource.opacity === "number") {
          canvas.lfOpacity = brushSource.opacity;
        }
        if (typeof brushSource.size === "number") {
          canvas.lfSize = brushSource.size;
        }
      });
    }
    if (filter == null ? void 0 : filter.requiresManualApply) {
      const applyButton = document.createElement(TagName.LfButton);
      applyButton.lfIcon = ImageEditorIcons.Resume;
      applyButton.lfLabel = "Apply";
      applyButton.lfStretchX = true;
      initManualApplyState(state, applyButton);
      applyButton.addEventListener("click", () => {
        if (!state.manualApply || state.manualApply.isProcessing) {
          return;
        }
        const hasPending = hasManualApplyPendingChanges(state);
        if (!hasPending) {
          return;
        }
        beginManualApplyRequest(state);
        void updateCb(state, true, true);
      });
      buttonsWrapper.appendChild(applyButton);
    }
  };
};
async function resetSettings(settings) {
  const controls = Array.from(settings.querySelectorAll("[data-id]"));
  for (const control of controls) {
    switch (control.tagName) {
      case "LF-SLIDER": {
        const slider = control;
        await slider.setValue(slider.lfValue);
        await slider.refresh();
        break;
      }
      case "LF-TEXTFIELD": {
        const textfield = control;
        await textfield.setValue(textfield.lfValue);
        break;
      }
      case "LF-TOGGLE": {
        const toggle = control;
        toggle.setValue(toggle.lfValue ? "on" : "off");
        break;
      }
    }
  }
}
const setBrush = async (canvas, lastBrushSettings) => {
  if (canvas) {
    const { color, opacity, size } = lastBrushSettings;
    canvas.lfColor = color;
    canvas.lfOpacity = opacity;
    canvas.lfSize = size;
  }
};
const applyFilterDefaults = (state, defaults) => {
  const { filter } = state;
  if (!filter) {
    return;
  }
  const mutableSettings = filter.settings;
  Object.keys(filter.configs).forEach((controlType) => {
    const configs = filter.configs[controlType];
    configs == null ? void 0 : configs.forEach((config) => {
      const defaultValue = defaults[config.id];
      if (typeof defaultValue === "undefined") {
        return;
      }
      switch (controlType) {
        case ImageEditorControls.Slider: {
          const sliderConfig = config;
          const numericValue = typeof defaultValue === "number" ? defaultValue : Number(defaultValue);
          sliderConfig.defaultValue = numericValue;
          mutableSettings[sliderConfig.id] = numericValue;
          break;
        }
        case ImageEditorControls.Textfield: {
          const textfieldConfig = config;
          const stringValue = defaultValue === null || typeof defaultValue === "undefined" ? "" : String(defaultValue);
          textfieldConfig.defaultValue = stringValue;
          mutableSettings[textfieldConfig.id] = stringValue;
          break;
        }
        case ImageEditorControls.Toggle: {
          const toggleConfig = config;
          const boolValue = defaultValue === true || typeof defaultValue === "string" && defaultValue.toLowerCase() === "true";
          toggleConfig.defaultValue = boolValue;
          mutableSettings[toggleConfig.id] = boolValue ? toggleConfig.on : toggleConfig.off;
          break;
        }
      }
    });
  });
};
const createEventHandlers = ({ handleInterruptForState: handleInterruptForState2, prepSettings: prepSettings2 }) => {
  const syncSelectionWithDataset = async (state, masonryEvent) => {
    const { elements } = state;
    const dataset = elements.imageviewer.lfDataset || {};
    const effectiveContextId = ensureDatasetContext(dataset, state);
    const previousSelection = dataset.selection;
    const previousContextId = dataset.context_id ?? effectiveContextId;
    const { comp, selectedShape: rawSelectedShape } = masonryEvent.detail;
    const masonryComp = comp;
    let selectedShape = rawSelectedShape;
    if ((!selectedShape || typeof selectedShape.index !== "number") && (masonryComp == null ? void 0 : masonryComp.getSelectedShape)) {
      try {
        selectedShape = await masonryComp.getSelectedShape();
      } catch (error) {
        getLfManager().log("Failed to resolve masonry selection.", { error }, LogSeverity.Warning);
      }
    }
    const nodes = Array.isArray(dataset == null ? void 0 : dataset.nodes) ? dataset.nodes : [];
    const selectionIndex = resolveSelectionIndex(selectedShape, nodes);
    if (typeof selectionIndex !== "number") {
      getLfManager().log("Unable to resolve selected masonry index.", { selectedShape }, LogSeverity.Warning);
      return;
    }
    const { selection, contextId } = buildSelectionPayload({
      dataset,
      index: selectionIndex,
      nodes,
      selectedShape,
      fallbackContextId: previousContextId ?? state.contextId
    });
    const resolvedContextId = selection.context_id ?? contextId ?? previousContextId ?? state.contextId;
    if (resolvedContextId) {
      state.contextId = resolvedContextId;
      if (!selection.context_id) {
        selection.context_id = resolvedContextId;
      }
    }
    const nextDataset = applySelectionColumn({
      ...dataset,
      context_id: dataset.context_id ?? resolvedContextId
    }, selection);
    if (resolvedContextId && nextDataset.selection) {
      nextDataset.selection.context_id = resolvedContextId;
    }
    elements.imageviewer.lfDataset = nextDataset;
    if (!resolvedContextId) {
      return;
    }
    if (!hasSelectionChanged(previousSelection, nextDataset.selection) && !hasContextChanged(previousContextId, nextDataset.context_id)) {
      return;
    }
    getApiRoutes().json.update(resolvedContextId, nextDataset).catch((error) => getLfManager().log("Failed to persist image selection.", { error, contextId: resolvedContextId }, LogSeverity.Warning));
  };
  const handlers = {
    //#region Button
    button: async (state, e) => {
      const { comp, eventType } = e.detail;
      if (eventType === "click") {
        const isPatched = getComfyAPI()[LFInterruptFlags.PatchedInterrupt] === true;
        switch (comp.lfIcon) {
          case ImageEditorIcons.Interrupt:
            getApiRoutes().comfy.interrupt();
            if (!isPatched) {
              await handleInterruptForState2(state);
            }
            break;
          case ImageEditorIcons.Resume:
            await handleInterruptForState2(state);
            break;
        }
      }
    },
    //#endregion
    //#region Canvas
    canvas: async (state, e) => {
      const { comp, eventType, points } = e.detail;
      const { filter, filterType } = state;
      switch (eventType) {
        case "stroke":
          const originalFilter = filter;
          const originalFilterType = filterType;
          const canvas = await comp.getCanvas();
          const b64Canvas = canvasToBase64(canvas);
          if (filterType !== "brush" && !(filter == null ? void 0 : filter.hasCanvasAction)) {
            state.filterType = "brush";
          }
          const brushDefaults = {
            ...SETTINGS.brush.settings,
            ...state.lastBrushSettings
          };
          const temporaryFilter = {
            ...JSON.parse(JSON.stringify(SETTINGS.brush)),
            settings: {
              ...brushDefaults,
              b64_canvas: b64Canvas,
              color: comp.lfColor ?? brushDefaults.color,
              opacity: comp.lfOpacity ?? brushDefaults.opacity,
              points,
              size: comp.lfSize ?? brushDefaults.size
            }
          };
          state.filter = temporaryFilter;
          try {
            await updateCb(state, true, true);
          } finally {
            if (originalFilter == null ? void 0 : originalFilter.hasCanvasAction) {
              const existingSettings = originalFilter.settings ?? {};
              originalFilter.settings = {
                ...existingSettings,
                b64_canvas: b64Canvas
              };
            }
            state.filter = originalFilter;
            state.filterType = originalFilterType;
            await comp.clearCanvas();
          }
          break;
      }
    },
    //#endregion
    //#region Imageviewer
    imageviewer: async (state, e) => {
      var _a;
      const { comp, eventType, originalEvent } = e.detail;
      const { node } = state;
      switch (eventType) {
        case "lf-event": {
          const ogEv = originalEvent;
          if (isTree(ogEv.detail.comp)) {
            const treeEvent = ogEv;
            const { id, node: treeNode, eventType: eventType2 } = treeEvent.detail;
            switch (id) {
              case "details-tree":
                if (((_a = treeNode == null ? void 0 : treeNode.cells) == null ? void 0 : _a.lfCode) && eventType2 === "click") {
                  prepSettings2(state, treeNode);
                }
                break;
              case "navigation-tree":
                if (!state.navigationManager || !treeNode || eventType2 !== "click") {
                  break;
                }
                await state.navigationManager.handleTreeClick(treeNode);
                const needsLazyLoad = !treeNode.children || treeNode.children.length === 0;
                if (needsLazyLoad) {
                  await state.navigationManager.expandNode(treeNode);
                }
                break;
            }
          }
          switch (ogEv.detail.eventType) {
            case "lf-event":
              const masonryEvent = ogEv;
              const isMasonryEvent = isMasonry(ogEv.detail.comp);
              if (isMasonryEvent) {
                const { selectedShape } = masonryEvent.detail;
                switch (masonryEvent.detail.eventType) {
                  case "lf-event":
                    const subOgEv = masonryEvent.detail.originalEvent;
                    const isImageEvent = isImage(subOgEv.detail.comp);
                    if (isImageEvent) {
                      switch (subOgEv.detail.eventType) {
                        case "click":
                          if (!selectedShape) {
                            getLfManager().log("Masonry selection cleared.", { selectedShape }, LogSeverity.Info);
                            return;
                          }
                          await syncSelectionWithDataset(state, masonryEvent);
                          break;
                      }
                    }
                }
                break;
              }
              break;
            case "ready":
              const c = ogEv.detail.comp;
              const isCanvas = c.rootElement.tagName.toLowerCase() === "lf-canvas";
              if (isCanvas) {
                const brushSettings = (state == null ? void 0 : state.lastBrushSettings) ?? SETTINGS.brush.settings;
                setBrush(c, brushSettings);
              }
              break;
            case "stroke": {
              const canvasEv = ogEv;
              await handlers.canvas(state, canvasEv);
              break;
            }
          }
          break;
        }
        case "ready": {
          const { navigation } = await comp.getComponents();
          switch (node.comfyClass) {
            case NodeName.imagesEditingBreakpoint:
              navigation.load.lfLabel = "";
              navigation.load.lfUiState = "disabled";
              navigation.textfield.lfLabel = "Previews are visible in your ComfyUI/temp folder";
              navigation.textfield.lfUiState = "disabled";
              break;
            default:
              navigation.textfield.lfLabel = "Directory (relative to ComfyUI/input)";
              break;
          }
          break;
        }
      }
    },
    //#endregion
    //#region Slider
    slider: async (state, e) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { preview, snapshot } = update;
      switch (eventType) {
        case "change":
          registerManualApplyChange(state);
          snapshot();
          break;
        case "input":
          registerManualApplyChange(state);
          const debouncedSlider = debounce(preview, 300);
          debouncedSlider();
          break;
      }
    },
    //#endregion
    //#region Textfield
    textfield: async (state, e) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { preview, snapshot } = update;
      switch (eventType) {
        case "change":
          registerManualApplyChange(state);
          snapshot();
          break;
        case "input":
          registerManualApplyChange(state);
          const debouncedTextfield = debounce(preview, 300);
          debouncedTextfield();
          break;
      }
    },
    //#endregion
    //#region Toggle
    toggle: async (state, e) => {
      const { eventType } = e.detail;
      const { update } = state;
      const { snapshot } = update;
      switch (eventType) {
        case "change":
          registerManualApplyChange(state);
          snapshot();
          break;
      }
    }
    //#endregion
  };
  return handlers;
};
function setGridStatus(status, grid, actionButtons) {
  const { interrupt, resume } = actionButtons;
  switch (status) {
    case ImageEditorStatus.Completed:
      requestAnimationFrame(() => {
        if (interrupt) {
          interrupt.lfUiState = "disabled";
        }
        if (resume) {
          resume.lfUiState = "disabled";
        }
      });
      grid == null ? void 0 : grid.classList.add(ImageEditorCSS.GridIsInactive);
      break;
    case ImageEditorStatus.Pending:
      requestAnimationFrame(() => {
        if (interrupt) {
          interrupt.lfUiState = "danger";
        }
        if (resume) {
          resume.lfUiState = "success";
        }
      });
      grid == null ? void 0 : grid.classList.remove(ImageEditorCSS.GridIsInactive);
      break;
  }
}
const handleInterruptForState = async (state) => {
  var _a, _b;
  const lfManager = getLfManager();
  const { syntax } = lfManager.getManagers().lfFramework;
  const { actionButtons, grid, imageviewer } = state.elements;
  const dataset = imageviewer.lfDataset;
  const statusColumn = getStatusColumn(dataset);
  const pathColumn = getPathColumn(dataset);
  const parsedPath = pathColumn ? syntax.json.unescape(pathColumn).parsedJSON : void 0;
  const path = typeof (parsedPath == null ? void 0 : parsedPath.title) === "string" ? parsedPath.title : null;
  if ((statusColumn == null ? void 0 : statusColumn.title) === ImageEditorStatus.Pending) {
    statusColumn.title = ImageEditorStatus.Completed;
    if (dataset && path) {
      try {
        await getApiRoutes().json.update(path, dataset);
      } catch (error) {
        lfManager.log("Failed to update JSON after workflow interrupt.", { error, path }, LogSeverity.Warning);
      }
    }
    if ((actionButtons == null ? void 0 : actionButtons.interrupt) && (actionButtons == null ? void 0 : actionButtons.resume)) {
      setGridStatus(ImageEditorStatus.Completed, grid, actionButtons);
    } else {
      grid == null ? void 0 : grid.classList.add(ImageEditorCSS.GridIsInactive);
    }
    try {
      const components = await imageviewer.getComponents();
      const navigation = components == null ? void 0 : components.navigation;
      await imageviewer.reset();
      await ((_b = (_a = navigation == null ? void 0 : navigation.masonry) == null ? void 0 : _a.setSelectedShape) == null ? void 0 : _b.call(_a, null));
    } catch (error) {
      lfManager.log("Failed to reset image viewer after workflow interrupt.", { error }, LogSeverity.Warning);
    }
  }
  await resetSettings(imageviewer);
};
const handlerRefs = {
  slider: async () => {
    throw new Error("Image editor slider handler not initialized.");
  },
  textfield: async () => {
    throw new Error("Image editor textfield handler not initialized.");
  },
  toggle: async () => {
    throw new Error("Image editor toggle handler not initialized.");
  }
};
const prepSettings = createPrepSettings({
  onSlider: (state, event) => handlerRefs.slider(state, event),
  onTextfield: (state, event) => handlerRefs.textfield(state, event),
  onToggle: (state, event) => handlerRefs.toggle(state, event)
});
const EV_HANDLERS$a = createEventHandlers({
  handleInterruptForState,
  prepSettings
});
handlerRefs.slider = EV_HANDLERS$a.slider;
handlerRefs.textfield = EV_HANDLERS$a.textfield;
handlerRefs.toggle = EV_HANDLERS$a.toggle;
const syncNavigationDirectoryControl = async (state, directoryValue) => {
  const { imageviewer } = state.elements;
  const { navigation } = await imageviewer.getComponents();
  const { textfield } = navigation;
  const current = await textfield.getValue();
  const target = normalizeDirectoryRequest(directoryValue);
  if ((current ?? "") === target) {
    return;
  }
  try {
    state.isSyncingDirectory = true;
    await textfield.setValue(target);
  } catch (error) {
    getLfManager().log("Failed to synchronize directory input.", { error }, LogSeverity.Warning);
  } finally {
    state.isSyncingDirectory = false;
  }
};
const extractMetadata = (node) => {
  const lfData = getLfData();
  const metadata = lfData.node.extractCellMetadata(node, "lfCode", {
    validate: (val) => {
      if (typeof val === "string") {
        try {
          val = JSON.parse(val);
        } catch {
          return false;
        }
      }
      if (typeof val !== "object" || val === null) {
        return false;
      }
      return "id" in val || "name" in val || "paths" in val;
    },
    transform: (val) => {
      let parsed = val;
      if (typeof val === "string") {
        try {
          parsed = JSON.parse(val);
        } catch {
          parsed = val;
        }
      }
      return {
        id: parsed.id ?? String(node.id ?? ""),
        name: parsed.name ?? String(node.value ?? ""),
        hasChildren: Boolean(parsed.hasChildren),
        paths: parsed.paths ?? {},
        isRoot: parsed.isRoot
      };
    }
  });
  return metadata ?? null;
};
const createNavigationTreeManager = (imageviewer, editorState) => {
  const _getDirectoryPath = (metadata) => {
    return metadata.paths.resolved ?? metadata.paths.raw ?? metadata.paths.relative ?? metadata.name ?? "";
  };
  const loadRoots = async () => {
    var _a;
    try {
      const response = await IMAGE_API.explore("", { scope: "roots" });
      if (response.status === LogSeverity.Success && ((_a = response.data) == null ? void 0 : _a.tree)) {
        imageviewer.lfNavigation = {
          isTreeOpen: false,
          treeProps: {
            lfAccordionLayout: true,
            lfDataset: response.data.tree ?? { columns: [], nodes: [] },
            lfFilter: true,
            lfGrid: true,
            lfSelectable: true
          }
        };
      }
    } catch (error) {
      getLfManager().log("Failed to load navigation roots.", { error }, LogSeverity.Warning);
    }
  };
  const expandNode = async (node) => {
    var _a, _b, _c;
    const metadata = extractMetadata(node);
    if (!(metadata == null ? void 0 : metadata.hasChildren)) {
      return;
    }
    const nodeId = metadata.id;
    const path = normalizeDirectoryRequest(_getDirectoryPath(metadata));
    if (!path) {
      return;
    }
    try {
      const response = await IMAGE_API.explore(path, { scope: "tree", nodePath: path });
      if (response.status === LogSeverity.Success && ((_a = response.data) == null ? void 0 : _a.tree)) {
        const { navigation } = await imageviewer.getComponents();
        const branch = response.data.tree;
        if (!Array.isArray(branch.nodes)) {
          return;
        }
        const currentDataset = (_c = (_b = imageviewer.lfNavigation) == null ? void 0 : _b.treeProps) == null ? void 0 : _c.lfDataset;
        if (!currentDataset) {
          return;
        }
        const lfData = getLfData();
        if (!lfData) {
          return;
        }
        const parentNode = lfData.node.find(currentDataset, (n) => n.id === nodeId);
        if (!parentNode) {
          return;
        }
        parentNode.children = branch.nodes;
        const parentId = parentNode.id;
        navigation.tree.lfExpandedNodeIds = Array.isArray(navigation.tree.lfExpandedNodeIds) && !navigation.tree.lfExpandedNodeIds.includes(parentId) ? [...navigation.tree.lfExpandedNodeIds, parentId] : [parentId];
      }
    } catch (error) {
      getLfManager().log("Failed to expand node.", { error, nodeId, path }, LogSeverity.Warning);
    }
  };
  const handleTreeClick = async (node) => {
    var _a;
    const metadata = extractMetadata(node);
    if (!metadata) {
      return;
    }
    const targetPath = normalizeDirectoryRequest(_getDirectoryPath(metadata));
    const currentPath = normalizeDirectoryRequest(editorState.directoryValue ?? deriveDirectoryValue(editorState.directory) ?? "");
    if (targetPath === currentPath && !metadata.isRoot) {
      return;
    }
    await ((_a = editorState.refreshDirectory) == null ? void 0 : _a.call(editorState, targetPath));
  };
  return {
    loadRoots,
    expandNode,
    handleTreeClick
  };
};
const IMAGE_EDITOR_INSTANCES = /* @__PURE__ */ new Set();
const STATE$h = /* @__PURE__ */ new WeakMap();
const imageEditorFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$h.get(wrapper),
      getValue: () => {
        const { imageviewer } = STATE$h.get(wrapper).elements;
        return imageviewer.lfDataset || {};
      },
      setValue: (value) => {
        const state = STATE$h.get(wrapper);
        const { actionButtons, grid, imageviewer } = state.elements;
        const callback = (_, u) => {
          var _a, _b;
          const parsedValue = u.parsedJSON;
          const isPending = ((_a = getStatusColumn(parsedValue)) == null ? void 0 : _a.title) === ImageEditorStatus.Pending;
          if (isPending) {
            setGridStatus(ImageEditorStatus.Pending, grid, actionButtons);
          }
          const dataset = parsedValue || {};
          ensureDatasetContext(dataset, state);
          const navigationDirectory = getNavigationDirectory(dataset);
          if (navigationDirectory) {
            state.directory = { ...navigationDirectory };
          }
          const derivedDirectoryValue = deriveDirectoryValue(navigationDirectory);
          if (derivedDirectoryValue !== void 0) {
            state.directoryValue = derivedDirectoryValue;
          }
          imageviewer.lfDataset = dataset;
          imageviewer.getComponents().then(({ details }) => {
            const { canvas } = details;
            if (canvas) {
              setBrush(canvas, STATE$h.get(wrapper).lastBrushSettings);
            }
          }).catch((error) => getLfManager().log("Failed to prepare image editor canvas.", { error }, LogSeverity.Warning));
          void syncNavigationDirectoryControl(state, state.directoryValue);
          const shouldAutoLoad = !state.hasAutoDirectoryLoad && (!Array.isArray(dataset == null ? void 0 : dataset.nodes) || dataset.nodes.length === 0);
          if (shouldAutoLoad) {
            state.hasAutoDirectoryLoad = true;
            (_b = state.refreshDirectory) == null ? void 0 : _b.call(state, normalizeDirectoryRequest(state.directoryValue));
          }
        };
        normalizeValue(value, callback, CustomWidgetName.imageEditor);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const settings = document.createElement(TagName.Div);
    const imageviewer = document.createElement(TagName.LfImageviewer);
    const navigationTreeEnabled = node.comfyClass === NodeName.loadAndEditImages;
    let navigationManager = null;
    const refresh = async (directory) => {
      const state2 = STATE$h.get(wrapper);
      const normalizedDirectory = normalizeDirectoryRequest(directory);
      if (!state2) {
        return;
      }
      state2.hasAutoDirectoryLoad = true;
      state2.lastRequestedDirectory = normalizedDirectory;
      try {
        const response = navigationTreeEnabled ? await IMAGE_API.explore(normalizedDirectory, { scope: "dataset" }) : await IMAGE_API.get(normalizedDirectory);
        if (response.status !== LogSeverity.Success) {
          getLfManager().log("Images not found.", { response }, LogSeverity.Info);
          return;
        }
        const rawData = response.data;
        const dataset = (navigationTreeEnabled ? rawData == null ? void 0 : rawData.dataset : rawData) ?? { nodes: [] };
        const mergedDirectory = mergeNavigationDirectory(dataset, { raw: normalizedDirectory });
        state2.directory = { ...mergedDirectory };
        const derivedDirectoryValue = deriveDirectoryValue(mergedDirectory);
        state2.directoryValue = derivedDirectoryValue ?? normalizedDirectory;
        state2.lastRequestedDirectory = state2.directoryValue;
        ensureDatasetContext(dataset, state2);
        imageviewer.lfDataset = dataset;
        await syncNavigationDirectoryControl(state2, state2.directoryValue);
      } catch (error) {
        getLfManager().log("Failed to refresh image directory.", { error, directory: normalizedDirectory }, LogSeverity.Warning);
      }
    };
    settings.classList.add(ImageEditorCSS.Settings);
    settings.slot = "settings";
    imageviewer.classList.add(ImageEditorCSS.Widget);
    imageviewer.lfLoadCallback = async (_, value) => {
      const state2 = STATE$h.get(wrapper);
      if (!state2 || state2.isSyncingDirectory) {
        return;
      }
      const directoryValue = normalizeDirectoryRequest(value);
      if (state2.lastRequestedDirectory === directoryValue && state2.directoryValue === directoryValue) {
        getLfManager().log("lfLoadCallback: directory unchanged, skipping", {}, LogSeverity.Info);
        return;
      }
      await refresh(directoryValue);
    };
    imageviewer.lfValue = TREE_DATA;
    imageviewer.addEventListener(LfEventName.LfImageviewer, (e) => EV_HANDLERS$a.imageviewer(STATE$h.get(wrapper), e));
    imageviewer.appendChild(settings);
    const actionButtons = {};
    const state = {
      contextId: void 0,
      elements: { actionButtons, controls: {}, grid, imageviewer, settings },
      directory: void 0,
      directoryValue: void 0,
      filter: null,
      filterType: null,
      hasAutoDirectoryLoad: false,
      isSyncingDirectory: false,
      lastBrushSettings: JSON.parse(JSON.stringify(SETTINGS.brush.settings)),
      lastRequestedDirectory: void 0,
      node,
      refreshDirectory: refresh,
      update: {
        preview: () => updateCb(STATE$h.get(wrapper)).then(() => {
        }),
        snapshot: () => updateCb(STATE$h.get(wrapper), true).then(() => {
        })
      },
      wrapper
    };
    switch (node.comfyClass) {
      case NodeName.imagesEditingBreakpoint:
        const actions = document.createElement(TagName.Div);
        const interrupt = document.createElement(TagName.LfButton);
        const resume = document.createElement(TagName.LfButton);
        interrupt.lfIcon = ImageEditorIcons.Interrupt;
        interrupt.lfLabel = "Interrupt workflow";
        interrupt.lfStretchX = true;
        interrupt.lfUiState = "danger";
        interrupt.title = "Click to interrupt the workflow.";
        interrupt.addEventListener(LfEventName.LfButton, (e) => EV_HANDLERS$a.button(STATE$h.get(wrapper), e));
        resume.lfIcon = ImageEditorIcons.Resume;
        resume.lfLabel = "Resume workflow";
        resume.lfStretchX = true;
        resume.lfStyling = "flat";
        resume.lfUiState = "success";
        resume.title = "Click to resume the workflow. Remember to save your snapshots after editing the images!";
        resume.addEventListener(LfEventName.LfButton, (e) => EV_HANDLERS$a.button(STATE$h.get(wrapper), e));
        actions.classList.add(ImageEditorCSS.Actions);
        actions.appendChild(interrupt);
        actions.appendChild(resume);
        grid.classList.add(ImageEditorCSS.GridIsInactive);
        grid.classList.add(ImageEditorCSS.GridHasActions);
        grid.appendChild(actions);
        actionButtons.interrupt = interrupt;
        actionButtons.resume = resume;
        setGridStatus(ImageEditorStatus.Completed, grid, actionButtons);
    }
    grid.classList.add(ImageEditorCSS.Grid);
    grid.appendChild(imageviewer);
    content.classList.add(ImageEditorCSS.Content);
    content.appendChild(grid);
    wrapper.appendChild(content);
    const options = imageEditorFactory.options(wrapper);
    STATE$h.set(wrapper, state);
    IMAGE_EDITOR_INSTANCES.add(state);
    if (navigationTreeEnabled) {
      navigationManager = createNavigationTreeManager(imageviewer, state);
      state.navigationManager = navigationManager;
    }
    void Promise.resolve().then(async () => {
      var _a, _b;
      const currentState = STATE$h.get(wrapper);
      if (!currentState) {
        return;
      }
      if (navigationTreeEnabled && navigationManager) {
        await navigationManager.loadRoots();
      }
      if (currentState.hasAutoDirectoryLoad) {
        return;
      }
      const currentDataset = (_a = currentState.elements.imageviewer) == null ? void 0 : _a.lfDataset;
      const hasNodes = Array.isArray(currentDataset == null ? void 0 : currentDataset.nodes) && currentDataset.nodes.length > 0;
      const hasDirectoryValue = Boolean(currentState.directoryValue);
      if (hasNodes || hasDirectoryValue) {
        return;
      }
      (_b = currentState.refreshDirectory) == null ? void 0 : _b.call(currentState, "");
    });
    return { widget: createDOMWidget(CustomWidgetName.imageEditor, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$h
  //#endregion
};
function installLFInterruptHook(apiObj, opts = {}) {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {
  });
  if (!isInterruptHookAPI(apiObj)) {
    logger('"api" object not available; cannot install interrupt hook yet', {}, LogSeverity.Warning);
    return { interruptHook: false };
  }
  const scopedApi = apiObj;
  const wrap = opts.interruptWrapper;
  const makePatched = (fn) => {
    const factory = wrap ?? ((original) => async function patched2(...args) {
      if (scopedApi[LFInterruptFlags.InBeforeInterrupt] === true) {
        return original.apply(this ?? scopedApi, args);
      }
      scopedApi[LFInterruptFlags.InBeforeInterrupt] = true;
      try {
        const result = await original.apply(this ?? scopedApi, args);
        for (const state of IMAGE_EDITOR_INSTANCES) {
          try {
            await handleInterruptForState(state);
          } catch (error) {
            logger("LF interrupt hook failed while applying image editor cleanup.", { error }, LogSeverity.Warning);
          }
        }
        return result;
      } finally {
        scopedApi[LFInterruptFlags.InBeforeInterrupt] = false;
      }
    });
    return factory(fn);
  };
  const installInterrupt = () => {
    try {
      if (scopedApi[LFInterruptFlags.PatchedInterrupt] === true) {
        return true;
      }
      const current = scopedApi.interrupt;
      if (typeof current === "function") {
        scopedApi[LFInterruptFlags.OriginalInterruptRef] = current;
        scopedApi.interrupt = makePatched(current);
        scopedApi[LFInterruptFlags.PatchedInterrupt] = true;
        return true;
      }
      const descriptor = Object.getOwnPropertyDescriptor(scopedApi, "interrupt");
      if (!descriptor || descriptor.configurable) {
        let original;
        Object.defineProperty(scopedApi, "interrupt", {
          configurable: true,
          enumerable: true,
          get() {
            return scopedApi[LFInterruptFlags.PatchedInterrupt] ? original : scopedApi[LFInterruptFlags.OriginalInterruptRef] ?? original;
          },
          set(fn) {
            if (typeof fn !== "function") {
              original = fn;
              return;
            }
            scopedApi[LFInterruptFlags.OriginalInterruptRef] = fn;
            original = makePatched(fn);
            scopedApi[LFInterruptFlags.PatchedInterrupt] = true;
          }
        });
      }
      return false;
    } catch (error) {
      logger("Failed to patch api.interrupt; proceeding without LF interrupt hook", { error }, LogSeverity.Warning);
      return false;
    }
  };
  let patched = installInterrupt();
  if (!patched) {
    let count = 0;
    const timer2 = setInterval(() => {
      count += 1;
      patched = installInterrupt();
      if (patched || count > attempts) {
        clearInterval(timer2);
      }
    }, intervalMs);
  }
  return { interruptHook: patched };
}
function installLFRefreshNodeHook(appObj, opts = {}) {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {
  });
  if (!isRefreshHookApp(appObj)) {
    logger('"app" object not available; cannot install refresh hook yet', {}, LogSeverity.Warning);
    return { refreshHook: false };
  }
  const scopedApp = appObj;
  const wrap = opts.refreshWrapper;
  const makePatched = (fn) => {
    const factory = wrap ?? ((original) => async function patched2(...args) {
      if (scopedApp[LFRefreshFlags.InBeforeRefresh] === true) {
        return original.apply(this ?? scopedApp, args);
      }
      scopedApp[LFRefreshFlags.InBeforeRefresh] = true;
      try {
        await beforeRefreshNodeDefs(args == null ? void 0 : args[0]);
      } catch (error) {
        logger("LF refresh hook failed before calling original function", { error }, LogSeverity.Warning);
      } finally {
        scopedApp[LFRefreshFlags.InBeforeRefresh] = false;
      }
      return original.apply(this ?? scopedApp, args);
    });
    return factory(fn);
  };
  const installRefresh = () => {
    try {
      if (scopedApp[LFRefreshFlags.PatchedRefresh] === true) {
        return true;
      }
      const current = scopedApp.refreshComboInNodes;
      if (typeof current === "function") {
        scopedApp[LFRefreshFlags.OriginalRefreshRef] = current;
        scopedApp.refreshComboInNodes = makePatched(current);
        scopedApp[LFRefreshFlags.PatchedRefresh] = true;
        return true;
      }
      const descriptor = Object.getOwnPropertyDescriptor(scopedApp, "refreshComboInNodes");
      if (!descriptor || descriptor.configurable) {
        let original;
        Object.defineProperty(scopedApp, "refreshComboInNodes", {
          configurable: true,
          enumerable: true,
          get() {
            return scopedApp[LFRefreshFlags.PatchedRefresh] ? original : scopedApp[LFRefreshFlags.OriginalRefreshRef] ?? original;
          },
          set(fn) {
            if (typeof fn !== "function") {
              original = fn;
              return;
            }
            scopedApp[LFRefreshFlags.OriginalRefreshRef] = fn;
            original = makePatched(fn);
            scopedApp[LFRefreshFlags.PatchedRefresh] = true;
          }
        });
      }
      return false;
    } catch (error) {
      logger("Failed to patch refreshComboInNodes; proceeding without LF refresh hook", { error }, LogSeverity.Warning);
      return false;
    }
  };
  let patched = installRefresh();
  if (!patched) {
    let count = 0;
    const timer2 = setInterval(() => {
      count += 1;
      patched = installRefresh();
      if (patched || count > attempts) {
        clearInterval(timer2);
      }
    }, intervalMs);
  }
  return { refreshHook: patched };
}
const CATEGORY = "✨ LF Nodes";
const DESCRIPTION = "Virtual reroute node that propagates upstream type and optional label.";
const DISPLAY_NAME = "Reroute";
const EXTENSION_NAME = `lf.virtual.${DISPLAY_NAME}`;
const NODE_PATH = "✨ LF Nodes/Reroute";
const SERIALIZED_KEYS = ["label", "showIcon", "showType", "mode", "horizontal"];
function deriveInnerColor(base) {
  const hex = base.trim();
  const expand = (h) => h.length === 4 ? `#${h[1]}${h[1]}${h[2]}${h[2]}${h[3]}${h[3]}` : h;
  if (!/^#([0-9a-fA-F]{3}){1,2}$/.test(hex)) {
    return "#ececec";
  }
  const full = expand(hex).substring(1);
  const r = parseInt(full.substring(0, 2), 16);
  const g = parseInt(full.substring(2, 4), 16);
  const b = parseInt(full.substring(4, 6), 16);
  const lighten = (c) => Math.min(255, Math.round(c + (255 - c) * 0.55));
  const rL = lighten(r);
  const gL = lighten(g);
  const bL = lighten(b);
  return `#${rL.toString(16).padStart(2, "0")}${gL.toString(16).padStart(2, "0")}${bL.toString(16).padStart(2, "0")}`;
}
const lfReroute = {
  name: EXTENSION_NAME,
  registerCustomNodes(appInstance) {
    var _a, _b;
    class LFReroute extends LGraphNode {
      constructor() {
        var _a2, _b2, _c, _d, _e, _f;
        super();
        this.isVirtualNode = true;
        this.properties = {
          horizontal: false,
          label: "",
          mode: "label+type",
          showType: true,
          showIcon: true
        };
        this.title = this.properties.label || "Label";
        (_a2 = this.addProperty) == null ? void 0 : _a2.call(this, "label", this.properties.label, "string");
        (_b2 = this.addProperty) == null ? void 0 : _b2.call(this, "mode", this.properties.mode, "string");
        (_c = this.addProperty) == null ? void 0 : _c.call(this, "showType", this.properties.showType, "boolean");
        (_d = this.addProperty) == null ? void 0 : _d.call(this, "showIcon", this.properties.showIcon, "boolean");
        (_e = this.addProperty) == null ? void 0 : _e.call(this, "horizontal", this.properties.horizontal, "boolean");
        this.addInput("", "*");
        this.addOutput(this.makeOutputName("*"), "*");
        this.__labelWidget = (_f = this.addWidget) == null ? void 0 : _f.call(this, "text", "Label", this.properties.label, (v) => {
          this.properties.label = v;
          this.refreshLabel();
        }, { multiline: false });
        if (this.__labelWidget) {
          this.__labelWidget.serializeValue = () => this.properties.label;
        }
        this.onConnectionsChange = () => {
          var _a3, _b3;
          try {
            reroutePropagationLogic.call(this, appInstance);
          } catch (error) {
            (_b3 = (_a3 = getLfManager()) == null ? void 0 : _a3.log) == null ? void 0 : _b3.call(_a3, "[LFReroute] onConnectionsChange error", { error }, LogSeverity.Warning);
          }
        };
      }
      snapToGrid(size) {
        const proto = LGraphNode.prototype;
        if (proto == null ? void 0 : proto.snapToGrid) {
          return proto.snapToGrid.call(this, size);
        }
        const grid = size || LiteGraph.CANVAS_GRID_SIZE || 10;
        if (this.pos) {
          this.pos[0] = grid * Math.round(this.pos[0] / grid);
          this.pos[1] = grid * Math.round(this.pos[1] / grid);
        }
      }
      getExtraMenuOptions(_ignored, options) {
        options.unshift({
          content: "Cycle Label/Type Mode",
          callback: () => {
            const order = ["label+type", "label", "type"];
            const i = order.indexOf(this.properties.mode);
            this.properties.mode = order[(i + 1) % order.length];
            this.refreshLabel();
          }
        }, {
          content: (this.properties.showType ? "Hide" : "Show") + " Type Part",
          callback: () => {
            this.properties.showType = !this.properties.showType;
            this.refreshLabel();
          }
        }, {
          content: (this.properties.showIcon ? "Hide" : "Show") + " Icon",
          callback: () => {
            this.properties.showIcon = !this.properties.showIcon;
            COMFY_API.scheduleRedraw();
          }
        }, {
          content: "Edit Label",
          callback: () => {
            const v = prompt("Set label", this.properties.label || "");
            if (v !== null) {
              this.properties.label = v;
              this.refreshLabel();
            }
          }
        }, {
          content: "Set " + (this.properties.horizontal ? "Horizontal" : "Vertical"),
          callback: () => {
            this.properties.horizontal = !this.properties.horizontal;
            this.applyOrientation();
          }
        });
      }
      makeOutputName(displayType, labelOverride) {
        const label = (labelOverride !== void 0 ? labelOverride : this.properties.label || "").trim();
        const typePart = this.properties.showType ? displayType : "";
        switch (this.properties.mode) {
          case "label":
            return label || (this.properties.showType ? displayType : "");
          case "type":
            return typePart;
          case "label+type":
          default:
            if (label && typePart)
              return `${label}:${typePart}`;
            return label || typePart;
        }
      }
      refreshLabel() {
        var _a2;
        if (!((_a2 = this.outputs) == null ? void 0 : _a2.length))
          return;
        const effectiveLabel = (this.properties.label || "").trim() || this.__autoLabel || "";
        const displayType = this.__outputType || this.outputs[0].type || "*";
        this.outputs[0].name = this.makeOutputName(displayType, effectiveLabel);
        this.title = effectiveLabel || "Label";
        this.size = this.computeSize();
        this.applyOrientation();
        COMFY_API.scheduleRedraw();
        const w = this.__labelWidget;
        if (w && "value" in w && w.value !== this.properties.label) {
          w.value = this.properties.label;
        }
      }
      onSerialize(raw) {
        const o = raw;
        if (o == null ? void 0 : o.properties) {
          const target = o.properties;
          for (const key of SERIALIZED_KEYS) {
            target[key] = this.properties[key];
          }
        }
        if (Array.isArray(o == null ? void 0 : o.widgets_values) && this.__labelWidget && this.widgets) {
          const idx = this.widgets.indexOf(this.__labelWidget);
          if (idx >= 0) {
            o.widgets_values[idx] = this.properties.label;
          }
        }
      }
      onConfigure(raw) {
        const o = raw;
        const props = (o == null ? void 0 : o.properties) || {};
        for (const key of SERIALIZED_KEYS) {
          const incoming = props[key];
          if (incoming === void 0)
            continue;
          if (key === "mode") {
            if (typeof incoming === "string" && ["label", "type", "label+type"].includes(incoming)) {
              this.properties.mode = incoming;
            }
            continue;
          }
          if (key === "label") {
            if (typeof incoming === "string") {
              this.properties.label = incoming;
            } else if (Array.isArray(o == null ? void 0 : o.widgets_values) && this.__labelWidget && this.widgets) {
              const idx = this.widgets.indexOf(this.__labelWidget);
              const wv = o.widgets_values[idx];
              if (idx >= 0 && typeof wv === "string") {
                this.properties.label = wv;
              }
            }
            continue;
          }
          if (key === "horizontal" || key === "showIcon" || key === "showType") {
            if (typeof incoming === "boolean") {
              this.properties[key] = incoming;
            }
            continue;
          }
        }
        if (this.__labelWidget && this.widgets) {
          const idx = this.widgets.indexOf(this.__labelWidget);
          if (idx >= 0 && "value" in this.__labelWidget) {
            this.__labelWidget.value = this.properties.label;
          }
        }
        this.refreshLabel();
      }
      applyOrientation() {
        var _a2, _b2, _c, _d;
        if (this.properties.horizontal) {
          if ((_a2 = this.inputs) == null ? void 0 : _a2[0]) {
            this.inputs[0].pos = [this.size[0] / 2, 0];
          }
          if ((_b2 = this.outputs) == null ? void 0 : _b2[0]) {
            this.outputs[0].pos = [this.size[0] / 2, this.size[1]];
          }
        } else {
          if ((_c = this.inputs) == null ? void 0 : _c[0]) {
            delete this.inputs[0].pos;
          }
          if ((_d = this.outputs) == null ? void 0 : _d[0]) {
            delete this.outputs[0].pos;
          }
        }
        COMFY_API.scheduleRedraw();
      }
      computeSize() {
        var _a2, _b2, _c;
        const base = this.title || "";
        const slotName = ((_b2 = (_a2 = this.outputs) == null ? void 0 : _a2[0]) == null ? void 0 : _b2.name) || "";
        const longest = base.length > slotName.length ? base : slotName;
        const textSize = LiteGraph.NODE_TEXT_SIZE || 14;
        const w = Math.max(120, textSize * longest.length * 0.6 + 50);
        const collapsed = (_c = this.flags) == null ? void 0 : _c.collapsed;
        const h = collapsed ? 28 : 50;
        return [w, h];
      }
      onDrawForeground(ctx) {
        var _a2, _b2, _c, _d;
        try {
          if (!this.properties.showIcon || !ctx) {
            return;
          }
          const headerH = LiteGraph && LiteGraph.NODE_TITLE_HEIGHT || 24;
          const radius = 6;
          const cx = 10 + radius;
          const cy = -headerH / 2;
          ctx.save();
          const displayType = this.__outputType || ((_b2 = (_a2 = this.outputs) == null ? void 0 : _a2[0]) == null ? void 0 : _b2.type);
          let baseColor;
          if (displayType && (LGraphCanvas == null ? void 0 : LGraphCanvas.link_type_colors)) {
            const c = LGraphCanvas.link_type_colors[displayType];
            if (typeof c === "string") {
              baseColor = c;
            }
          }
          const outer = baseColor || "#3a3a3a";
          const inner = deriveInnerColor(baseColor || "#3a3a3a");
          ctx.fillStyle = outer;
          ctx.beginPath();
          ctx.arc(cx, cy, radius, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = inner;
          ctx.beginPath();
          ctx.arc(cx, cy, radius * 0.4, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        } catch (err) {
          (_d = (_c = getLfManager()) == null ? void 0 : _c.log) == null ? void 0 : _d.call(_c, "[LFReroute] onDrawForeground error", { err }, LogSeverity.Info);
        }
      }
    }
    function reroutePropagationLogic(appInstance2) {
      var _a2, _b2, _c, _d, _e, _f, _g, _h, _i, _j, _k, _l, _m, _n, _o, _p;
      const isLabeled = (n) => {
        var _a3;
        return ((_a3 = n == null ? void 0 : n.constructor) == null ? void 0 : _a3.type) === NODE_PATH;
      };
      let inputType = null;
      let upstream = this;
      let originNode = null;
      while (((_b2 = (_a2 = upstream == null ? void 0 : upstream.inputs) == null ? void 0 : _a2[0]) == null ? void 0 : _b2.link) != null) {
        const linkId = upstream.inputs[0].link;
        const link = appInstance2.graph.links[linkId];
        if (!link)
          break;
        const origin = appInstance2.graph.getNodeById(link.origin_id);
        if (!origin)
          break;
        if (isLabeled(origin)) {
          if (origin === this) {
            (_c = upstream.disconnectInput) == null ? void 0 : _c.call(upstream, link.target_slot);
            break;
          }
          upstream = origin;
          continue;
        }
        inputType = ((_e = (_d = origin.outputs) == null ? void 0 : _d[link.origin_slot]) == null ? void 0 : _e.type) || null;
        originNode = origin;
        break;
      }
      let downstreamType = null;
      const firstLinks = ((_g = (_f = this.outputs) == null ? void 0 : _f[0]) == null ? void 0 : _g.links) || [];
      for (const l of firstLinks) {
        const link = appInstance2.graph.links[l];
        if (!link) {
          continue;
        }
        const target = appInstance2.graph.getNodeById(link.target_id);
        if (!target || isLabeled(target)) {
          continue;
        }
        downstreamType = ((_i = (_h = target.inputs) == null ? void 0 : _h[link.target_slot]) == null ? void 0 : _i.type) || null;
        if (downstreamType) {
          break;
        }
      }
      const finalType = inputType || downstreamType || "*";
      if (!(this.properties.label || "").trim()) {
        if (originNode) {
          const candidateTitle = (originNode.title || "").trim();
          const candidateSlotName = (() => {
            var _a3, _b3, _c2, _d2;
            if (!originNode.outputs)
              return "";
            const slotIdx = (() => {
              var _a4, _b4;
              if (((_b4 = (_a4 = upstream == null ? void 0 : upstream.inputs) == null ? void 0 : _a4[0]) == null ? void 0 : _b4.link) != null) {
                const linkId = upstream.inputs[0].link;
                const link = appInstance2.graph.links[linkId];
                if (link)
                  return link.origin_slot ?? 0;
              }
              return 0;
            })();
            return (((_b3 = (_a3 = originNode.outputs) == null ? void 0 : _a3[slotIdx]) == null ? void 0 : _b3.label) || ((_d2 = (_c2 = originNode.outputs) == null ? void 0 : _c2[slotIdx]) == null ? void 0 : _d2.name) || "").trim();
          })();
          const effectiveSlotName = candidateSlotName && candidateSlotName !== "*" ? candidateSlotName : "";
          const chosen = effectiveSlotName || candidateTitle;
          if (chosen) {
            this.__autoLabel = chosen;
          }
        } else {
          this.__autoLabel = void 0;
        }
      } else {
        this.__autoLabel = void 0;
      }
      this.__outputType = finalType;
      if ((_j = this.inputs) == null ? void 0 : _j[0]) {
        this.inputs[0].type = finalType;
      }
      if ((_k = this.outputs) == null ? void 0 : _k[0]) {
        this.outputs[0].type = finalType;
        this.outputs[0].name = this.makeOutputName(finalType);
      }
      this.size = this.computeSize();
      this.applyOrientation();
      this.refreshLabel();
      const color = (_l = LGraphCanvas.link_type_colors) == null ? void 0 : _l[finalType];
      if (color) {
        if ((_n = (_m = this.outputs) == null ? void 0 : _m[0]) == null ? void 0 : _n.links) {
          for (const l of this.outputs[0].links) {
            const link = appInstance2.graph.links[l];
            if (link) {
              link.color = color;
            }
          }
        }
        const inLinkId = (_p = (_o = this.inputs) == null ? void 0 : _o[0]) == null ? void 0 : _p.link;
        if (inLinkId != null) {
          const inLink = appInstance2.graph.links[inLinkId];
          if (inLink) {
            inLink.color = color;
          }
        }
      }
      COMFY_API.scheduleRedraw();
    }
    LiteGraph.registerNodeType(NODE_PATH, Object.assign(LFReroute, {
      title_mode: LiteGraph.NORMAL_TITLE,
      title: "Reroute",
      collapsable: true,
      category: "LF Nodes",
      description: "Label + type aware reroute (frontend virtual)"
    }));
    onAfterGraphConfigured(LFReroute, (node) => {
      requestAnimationFrame(() => {
        var _a2, _b2, _c;
        try {
          (_a2 = node.onConnectionsChange) == null ? void 0 : _a2.call(node);
        } catch (err) {
          (_c = (_b2 = getLfManager()) == null ? void 0 : _b2.log) == null ? void 0 : _c.call(_b2, "[LFReroute] onAfterGraphConfigured", { err }, LogSeverity.Warning);
        }
      });
    });
    (_b = (_a = getLfManager()) == null ? void 0 : _a.log) == null ? void 0 : _b.call(_a, `Virtual node registered (UI compliant): ${NODE_PATH}`, {}, LogSeverity.Success);
  },
  beforeRegisterVueAppNodeDefs(defs) {
    const def = defs.find((d) => d.name === NODE_PATH);
    if (def) {
      def.display_name = DISPLAY_NAME;
      def.category = CATEGORY;
      def.description = DESCRIPTION;
      if (def.python_module === "custom_nodes.frontend_only") {
        def.python_module = "lf_nodes.virtual";
      }
    }
  }
};
var __classPrivateFieldGet$3 = function(receiver, state, kind, f) {
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var _LFNodes_REGISTRY;
class LFNodes {
  constructor() {
    _LFNodes_REGISTRY.set(this, /* @__PURE__ */ new Map());
    this.add = (extension) => {
      var _a, _b;
      const lfManager = getLfManager();
      if (!(extension == null ? void 0 : extension.name)) {
        (_a = lfManager == null ? void 0 : lfManager.log) == null ? void 0 : _a.call(lfManager, `Attempted to add virtual node with invalid name`, { extension }, LogSeverity.Warning);
        return;
      }
      if (__classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").has(extension.name)) {
        (_b = lfManager == null ? void 0 : lfManager.log) == null ? void 0 : _b.call(lfManager, `Duplicate virtual node ignored: '${extension.name}'`, {}, LogSeverity.Warning);
        return;
      }
      __classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").set(extension.name, { extension, registered: false });
    };
    this.addMany = (extensions) => {
      extensions.forEach((e) => this.add(e));
    };
    this.list = () => Array.from(__classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").values());
    this.registerAll = () => {
      const lfManager = getLfManager();
      __classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").forEach((entry, key) => {
        var _a, _b;
        if (entry.registered) {
          return;
        }
        try {
          COMFY_API.register(entry.extension);
          entry.registered = true;
          (_a = lfManager == null ? void 0 : lfManager.log) == null ? void 0 : _a.call(lfManager, `Registered virtual node '${key}'`, {}, LogSeverity.Success);
        } catch (error) {
          entry.error = error;
          (_b = lfManager == null ? void 0 : lfManager.log) == null ? void 0 : _b.call(lfManager, `Failed to register virtual node '${key}'`, { error }, LogSeverity.Error);
        }
      });
    };
    this.add(lfReroute);
  }
}
_LFNodes_REGISTRY = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldGet$2 = function(receiver, state, kind, f) {
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var __classPrivateFieldSet$1 = function(receiver, state, value, kind, f) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value), value;
};
var _LFTooltip_instances, _LFTooltip_CB, _LFTooltip_CSS_CLASSES, _LFTooltip_LAYOUT, _LFTooltip_TOOLTIP_ELEMENT, _LFTooltip_initialize, _LFTooltip_uploadLayout, _LFTooltip_buttonEventHandler;
class LFTooltip {
  constructor() {
    _LFTooltip_instances.add(this);
    _LFTooltip_CB.set(this, {});
    _LFTooltip_CSS_CLASSES.set(this, {
      wrapper: "lf-tooltip",
      content: `lf-tooltip__content`
    });
    _LFTooltip_LAYOUT.set(this, void 0);
    _LFTooltip_TOOLTIP_ELEMENT.set(this, void 0);
    _LFTooltip_buttonEventHandler.set(this, async (upload, e) => {
      const { eventType } = e.detail;
      switch (eventType) {
        case "click":
          const lfManager = getLfManager();
          switch (__classPrivateFieldGet$2(this, _LFTooltip_LAYOUT, "f")) {
            case "upload":
              const files = await upload.getValue();
              const reader = new FileReader();
              reader.onload = (e2) => {
                var _a;
                const result = (_a = e2.target) == null ? void 0 : _a.result;
                let base64String = "";
                if (typeof result === "string") {
                  base64String = result.replace(/^data:.*,/, "");
                } else if (result instanceof ArrayBuffer) {
                  const arrayBufferView = new Uint8Array(result);
                  base64String = btoa(String.fromCharCode.apply(null, arrayBufferView));
                }
                if (__classPrivateFieldGet$2(this, _LFTooltip_CB, "f")) {
                  lfManager.log("Invoking upload callback.", { base64String }, LogSeverity.Info);
                  __classPrivateFieldGet$2(this, _LFTooltip_CB, "f")[__classPrivateFieldGet$2(this, _LFTooltip_LAYOUT, "f")](base64String);
                }
              };
              reader.readAsDataURL(files[0]);
              break;
          }
      }
    });
  }
  //#endregion
  //#region Create
  create(anchor, layout, cb) {
    const lfFramework = getLfManager().getManagers().lfFramework;
    if (__classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f")) {
      __classPrivateFieldGet$2(this, _LFTooltip_instances, "m", _LFTooltip_initialize).call(this);
    }
    const parent = document.body;
    __classPrivateFieldSet$1(this, _LFTooltip_CB, cb ? { [layout]: cb } : {}, "f");
    __classPrivateFieldSet$1(this, _LFTooltip_LAYOUT, layout ?? "upload", "f");
    __classPrivateFieldSet$1(this, _LFTooltip_TOOLTIP_ELEMENT, document.createElement("div"), "f");
    __classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f").classList.add(__classPrivateFieldGet$2(this, _LFTooltip_CSS_CLASSES, "f").wrapper);
    let layoutElement;
    switch (__classPrivateFieldGet$2(this, _LFTooltip_LAYOUT, "f")) {
      case "upload":
        layoutElement = __classPrivateFieldGet$2(this, _LFTooltip_instances, "m", _LFTooltip_uploadLayout).call(this);
        __classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f").appendChild(layoutElement);
        break;
    }
    lfFramework.portal.open(layoutElement, __classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f"), anchor, 0, "auto");
    lfFramework.addClickCallback({ cb: () => this.destroy(), element: layoutElement });
    requestAnimationFrame(() => parent.appendChild(__classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f")));
  }
  //#endregion
  //#region Destroy
  destroy() {
    __classPrivateFieldGet$2(this, _LFTooltip_instances, "m", _LFTooltip_initialize).call(this);
  }
}
_LFTooltip_CB = /* @__PURE__ */ new WeakMap(), _LFTooltip_CSS_CLASSES = /* @__PURE__ */ new WeakMap(), _LFTooltip_LAYOUT = /* @__PURE__ */ new WeakMap(), _LFTooltip_TOOLTIP_ELEMENT = /* @__PURE__ */ new WeakMap(), _LFTooltip_buttonEventHandler = /* @__PURE__ */ new WeakMap(), _LFTooltip_instances = /* @__PURE__ */ new WeakSet(), _LFTooltip_initialize = function _LFTooltip_initialize2() {
  var _a;
  (_a = __classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f")) == null ? void 0 : _a.remove();
  __classPrivateFieldSet$1(this, _LFTooltip_TOOLTIP_ELEMENT, null, "f");
  __classPrivateFieldSet$1(this, _LFTooltip_CB, {}, "f");
  __classPrivateFieldSet$1(this, _LFTooltip_LAYOUT, null, "f");
}, _LFTooltip_uploadLayout = function _LFTooltip_uploadLayout2() {
  const content = document.createElement(TagName.Div);
  const upload = document.createElement(TagName.LfUpload);
  const button = document.createElement(TagName.LfButton);
  content.classList.add(__classPrivateFieldGet$2(this, _LFTooltip_CSS_CLASSES, "f").content);
  button.lfIcon = "upload";
  button.lfLabel = "Update cover";
  button.lfStretchX = true;
  content.dataset.lf = "portal";
  content.appendChild(upload);
  content.appendChild(button);
  button.addEventListener(LfEventName.LfButton, __classPrivateFieldGet$2(this, _LFTooltip_buttonEventHandler, "f").bind(__classPrivateFieldGet$2(this, _LFTooltip_buttonEventHandler, "f"), upload));
  return content;
};
const DOWNLOAD_PLACEHOLDERS = {
  lfDataset: {
    nodes: [
      {
        cells: {
          lfImage: { shape: "image", value: "download" },
          lfText: { shape: "text", value: "Fetching metadata from CivitAI..." }
        },
        id: "0"
      }
    ]
  }
};
const CARD_PROPS_TO_SERIALIZE = ["lfDataset"];
const EV_HANDLERS$9 = {
  //#region Button handler
  button: (state, e) => {
    const { comp, eventType } = e.detail;
    const { grid, node } = state;
    switch (eventType) {
      case "click":
        const cards = Array.from(grid.querySelectorAll(TagName.LfCard));
        if (cards == null ? void 0 : cards.length) {
          const models = [];
          const widget = getCustomWidget(node, CustomWidgetName.card);
          cards.forEach((card) => {
            var _a, _b, _c, _d;
            const hashCell = (_d = (_c = (_b = (_a = card.lfDataset) == null ? void 0 : _a.nodes) == null ? void 0 : _b[0]) == null ? void 0 : _c.cells) == null ? void 0 : _d.lfCode;
            if (hashCell) {
              const { hash, path } = JSON.parse(JSON.stringify(hashCell.value));
              const dataset = card.lfDataset;
              comp.lfShowSpinner = true;
              models.push({ apiFlag: true, dataset, hash, path });
            }
          });
          if (models.length) {
            const value = {
              props: []
            };
            cardPlaceholders(widget, cards.length);
            apiCall$1(models, true).then((r) => {
              for (let index = 0; index < r.length; index++) {
                const cardProps = r[index];
                if (cardProps.lfDataset) {
                  value.props.push(cardProps);
                } else {
                  value.props.push({
                    ...cardProps,
                    lfDataset: models[index].dataset
                  });
                }
              }
              widget.options.setValue(JSON.stringify(value));
              requestAnimationFrame(() => comp.lfShowSpinner = false);
            });
          }
        }
        break;
    }
  },
  //#endregion
  //#region Card handler
  card: (e) => {
    var _a, _b;
    const { comp, eventType, originalEvent } = e.detail;
    const node = (_b = (_a = comp.lfDataset) == null ? void 0 : _a.nodes) == null ? void 0 : _b[0];
    switch (eventType) {
      case "click":
        if (node == null ? void 0 : node.value) {
          window.open(String(node.value).valueOf(), "_blank");
        }
        break;
      case "contextmenu":
        const ogEv = originalEvent;
        const lfManager = getLfManager();
        ogEv.preventDefault();
        ogEv.stopPropagation();
        const tip = lfManager.getManagers().tooltip;
        const cb = async (b64image) => {
          var _a2, _b2, _c, _d;
          const node2 = (_b2 = (_a2 = comp.lfDataset) == null ? void 0 : _a2.nodes) == null ? void 0 : _b2[0];
          if (node2) {
            const code = (_c = node2 == null ? void 0 : node2.cells) == null ? void 0 : _c.lfCode;
            if (code) {
              try {
                const path = JSON.parse(JSON.stringify(code.value)).path;
                lfManager.log(`Updating cover for model with path: ${path}`, { b64image }, LogSeverity.Info);
                getApiRoutes().metadata.updateCover(path, b64image);
                const image = (_d = node2 == null ? void 0 : node2.cells) == null ? void 0 : _d.lfImage;
                if (image) {
                  image.value = `data:image/png;charset=utf-8;base64,${b64image}`;
                  comp.refresh();
                  tip.destroy();
                }
              } catch (error) {
                lfManager.log("Failed to fetch the model's path from .info file", { b64image }, LogSeverity.Error);
              }
            }
          }
        };
        tip.create({ x: ogEv.x, y: ogEv.y }, "upload", cb);
        break;
    }
  }
  //#endregion
};
const cardPlaceholders = (widget, count) => {
  const dummyValue = {
    props: []
  };
  for (let index = 0; index < count; index++) {
    dummyValue.props.push(DOWNLOAD_PLACEHOLDERS);
  }
  widget.options.setValue(JSON.stringify(dummyValue));
};
const apiCall$1 = async (models, forcedSave = false) => {
  const promises = models.map(async ({ dataset, hash, path, apiFlag }) => {
    if (apiFlag) {
      const payload = await getApiRoutes().metadata.get(hash);
      return onResponse(dataset, path, forcedSave, payload);
    } else {
      return onResponse(dataset, path, forcedSave, null);
    }
  });
  return Promise.all(promises);
};
const onResponse = async (dataset, path, forcedSave, payload) => {
  var _a, _b, _c;
  const r = payload == null ? void 0 : payload.data;
  const id = r == null ? void 0 : r.id;
  const props = {
    lfStyle: ".sub-2.description { white-space: pre-wrap; }"
  };
  switch (typeof id) {
    case "number":
      const code = (_c = (_b = (_a = dataset == null ? void 0 : dataset.nodes) == null ? void 0 : _a[0]) == null ? void 0 : _b.cells) == null ? void 0 : _c.lfCode;
      const civitaiDataset = prepareValidDataset(r, code);
      props.lfDataset = civitaiDataset;
      getApiRoutes().metadata.save(path, civitaiDataset, forcedSave);
      break;
    case "string":
      const node = dataset.nodes[0];
      node.description = "";
      node.value = "";
      node.cells.lfButton = {
        lfIcon: "warning",
        lfLabel: "Not found on CivitAI!",
        lfStyling: "flat",
        lfUiState: "disabled",
        shape: "button",
        value: ""
      };
      node.cells.text3 = {
        value: "Whoops! It seems like something's off. Falling back to local data."
      };
      props.lfDataset = dataset;
      break;
  }
  return props;
};
const prepCards = (container, propsArray) => {
  var _a;
  const { syntax } = getLfManager().getManagers().lfFramework;
  let count = 0;
  const cards = container.querySelectorAll("lf-card");
  cards.forEach((c) => c.remove());
  for (let index = 0; propsArray && index < propsArray.length; index++) {
    const card = container.appendChild(createCard());
    count += 1;
    const props = propsArray[index];
    if (props.lfDataset) {
      for (const key in props) {
        if (Object.prototype.hasOwnProperty.call(props, key)) {
          const prop = props[key];
          if (key === "lfDataset") {
            try {
              if (typeof prop === "string") {
                card.lfDataset = syntax.json.unescape(prop).parsedJSON;
              } else {
                card.lfDataset = prop;
              }
              const node = (_a = card.lfDataset.nodes) == null ? void 0 : _a[0];
              if (node) {
                card.dataset.link = node.description;
                if (node.value) {
                  card.title = String(node.value).valueOf();
                }
              }
            } catch (error) {
              getLfManager().log("Error when setting lfData prop on card!", { error }, LogSeverity.Error);
            }
          } else {
            card[key] = prop;
          }
        }
      }
    }
  }
  return count;
};
const getCardProps = (container) => {
  const propsArray = [];
  const cards = container.querySelectorAll("lf-card");
  for (let index = 0; index < cards.length; index++) {
    const card = cards[index];
    const props = CARD_PROPS_TO_SERIALIZE.reduce((acc, p) => {
      if (card[p]) {
        acc[p] = card[p];
      }
      return acc;
    }, {});
    propsArray.push(props);
  }
  return propsArray;
};
const createCard = () => {
  const card = document.createElement(TagName.LfCard);
  card.addEventListener(LfEventName.LfCard, EV_HANDLERS$9.card);
  return card;
};
const prepareValidDataset = (r, code) => {
  var _a, _b, _c, _d, _e;
  const dataset = {
    nodes: [
      {
        cells: { lfCode: code ?? null, lfImage: null, text1: null, text2: null, text3: null },
        id: r.id.toString(),
        description: "Click to open the model's page on CivitAI",
        value: `https://civitai.com/models/${r.modelId}`
      }
    ]
  };
  const cells = dataset.nodes[0].cells;
  cells.lfImage = {
    shape: "image",
    value: r.images[0].url
  };
  cells.text1 = { value: r.model.name };
  cells.text2 = { value: r.name };
  cells.text3 = {
    value: `- Info:
Type: ${((_a = r.model) == null ? void 0 : _a.type) ? r.model.type : "N/A"}
Status: ${r.status ? r.status : "N/A"}
Base model: ${r.baseModel ? r.baseModel : "N/A"}
Description: ${r.description ? r.description : "N/A"}

- Trained words:
${((_b = r.trainedWords) == null ? void 0 : _b.length) ? r.trainedWords.join(", ") : "N/A"}

- Stats:
Updated at: ${r.updatedAt ? r.updatedAt : "N/A"}
Downloads: ${((_c = r.stats) == null ? void 0 : _c.downloadCount) ? r.stats.downloadCount : "N/A"}
Rating: ${((_d = r.stats) == null ? void 0 : _d.rating) ? r.stats.rating : "N/A"}
Thumbs up: ${((_e = r.stats) == null ? void 0 : _e.thumbsUpCount) ? r.stats.thumbsUpCount : "N/A"}

(data pulled from CivitAI at: ${(/* @__PURE__ */ new Date()).toLocaleDateString()})
`
  };
  return dataset;
};
var CardCSS;
(function(CardCSS2) {
  CardCSS2["Content"] = "lf-card";
  CardCSS2["ContentHasButton"] = "lf-card--has-button";
  CardCSS2["Grid"] = "lf-card__grid";
})(CardCSS || (CardCSS = {}));
const STATE$g = /* @__PURE__ */ new WeakMap();
const cardFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$g.get(wrapper),
      getValue() {
        const { grid } = STATE$g.get(wrapper);
        return {
          props: getCardProps(grid) || []
        };
      },
      setValue(value) {
        const { grid } = STATE$g.get(wrapper);
        const callback = (_, u) => {
          const { props } = u.parsedJSON;
          const len = (props == null ? void 0 : props.length) > 1 ? 2 : 1;
          grid.style.setProperty("--card-grid", `repeat(1, 1fr) / repeat(${len}, 1fr)`);
          prepCards(grid, props);
        };
        normalizeValue(value, callback, CustomWidgetName.card);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    grid.classList.add(CardCSS.Grid);
    content.classList.add(CardCSS.Content);
    content.appendChild(grid);
    switch (node.comfyClass) {
      case NodeName.checkpointSelector:
      case NodeName.diffusionModelSelector:
      case NodeName.embeddingSelector:
      case NodeName.loraAndEmbeddingSelector:
      case NodeName.loraSelector:
        content.classList.add(CardCSS.ContentHasButton);
        const button = document.createElement(TagName.LfButton);
        button.lfIcon = "download";
        button.lfLabel = "Refresh";
        button.lfStretchX = true;
        button.title = "Attempts to manually ownload fresh metadata from CivitAI";
        button.addEventListener(LfEventName.LfButton, (e) => EV_HANDLERS$9.button(STATE$g.get(wrapper), e));
        content.appendChild(button);
        break;
    }
    wrapper.appendChild(content);
    const options = cardFactory.options(wrapper);
    STATE$g.set(wrapper, { grid, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.card, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$g
  //#endregion
};
var CardsWithChipCSS;
(function(CardsWithChipCSS2) {
  CardsWithChipCSS2["Content"] = "lf-cardswithchip";
  CardsWithChipCSS2["Cards"] = "lf-cardswithchip__cards";
  CardsWithChipCSS2["Chip"] = "lf-cardswithchip__chip";
  CardsWithChipCSS2["Grid"] = "lf-cardswithchip__grid";
})(CardsWithChipCSS || (CardsWithChipCSS = {}));
const STATE$f = /* @__PURE__ */ new WeakMap();
const cardsWithChipFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$f.get(wrapper),
      getValue() {
        const { chip, grid } = STATE$f.get(wrapper);
        return {
          chip: (chip == null ? void 0 : chip.lfDataset) || {},
          props: getCardProps(grid) || []
        };
      },
      setValue(value) {
        const { chip, grid } = STATE$f.get(wrapper);
        const callback = (v, u) => {
          const dataset = u.parsedJSON;
          const cardsCount = prepCards(grid, dataset.props);
          if (!cardsCount || !v) {
            return;
          }
          const columns = cardsCount > 1 ? 2 : 1;
          grid.style.setProperty("--card-grid", String(columns).valueOf());
          if (chip) {
            chip.lfDataset = dataset.chip;
          }
        };
        normalizeValue(value, callback, CustomWidgetName.cardsWithChip);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const outerGrid = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const chip = document.createElement(TagName.LfChip);
    content.classList.add(CardsWithChipCSS.Content);
    outerGrid.classList.add(CardsWithChipCSS.Grid);
    grid.classList.add(CardsWithChipCSS.Cards);
    chip.classList.add(CardsWithChipCSS.Chip);
    outerGrid.appendChild(chip);
    outerGrid.appendChild(grid);
    content.appendChild(outerGrid);
    wrapper.appendChild(content);
    const options = cardsWithChipFactory.options(wrapper);
    STATE$f.set(wrapper, { chip, grid, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.cardsWithChip, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$f
  //#endregion
};
var CarouselCSS;
(function(CarouselCSS2) {
  CarouselCSS2["Content"] = "lf-carousel";
  CarouselCSS2["Widget"] = "lf-carousel__widget";
})(CarouselCSS || (CarouselCSS = {}));
const STATE$e = /* @__PURE__ */ new WeakMap();
const carouselFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE$e.get(wrapper),
      getValue() {
        const { carousel } = STATE$e.get(wrapper);
        return (carousel == null ? void 0 : carousel.lfDataset) || {};
      },
      setValue(value) {
        const { carousel } = STATE$e.get(wrapper);
        const callback = (_, u) => {
          const dataset = u.parsedJSON;
          carousel.lfDataset = dataset || {};
        };
        normalizeValue(value, callback, CustomWidgetName.carousel);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const carousel = document.createElement(TagName.LfCarousel);
    carousel.lfAutoPlay = true;
    content.classList.add(CarouselCSS.Content);
    carousel.classList.add(CarouselCSS.Widget);
    content.appendChild(carousel);
    wrapper.appendChild(content);
    const options = carouselFactory.options(wrapper);
    STATE$e.set(wrapper, { carousel, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.carousel, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$e
  //#endregion
};
const EV_HANDLERS$8 = {
  //#region Chat handler
  chat: (state, e) => {
    const { eventType, history, status } = e.detail;
    switch (eventType) {
      case "polling":
        const severity = status === "ready" ? LogSeverity.Info : status === "offline" ? LogSeverity.Error : LogSeverity.Warning;
        getLfManager().log("Chat widget, polling status: " + status, { chat: e.detail }, severity);
        break;
      case "update":
        state.history = history;
        break;
    }
  }
  //#endregion
};
var ChatCSS;
(function(ChatCSS2) {
  ChatCSS2["Content"] = "lf-chat";
  ChatCSS2["Widget"] = "lf-chat__widget";
})(ChatCSS || (ChatCSS = {}));
const STATE$d = /* @__PURE__ */ new WeakMap();
const chatFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$d.get(wrapper),
      getValue() {
        const { history } = STATE$d.get(wrapper);
        return history || "";
      },
      setValue(value) {
        const state = STATE$d.get(wrapper);
        const callback = (v) => {
          state.history = v || "";
          if (v && state.chat.lfValue) {
            state.chat.lfValue = JSON.parse(v);
          }
          state.chat.setHistory(v);
        };
        normalizeValue(value, callback, CustomWidgetName.chat);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const chat = document.createElement(TagName.LfChat);
    content.classList.add(ChatCSS.Content);
    chat.classList.add(ChatCSS.Widget);
    chat.addEventListener(LfEventName.LfChat, (e) => EV_HANDLERS$8.chat(STATE$d.get(wrapper), e));
    content.appendChild(chat);
    wrapper.appendChild(content);
    const options = chatFactory.options(wrapper);
    STATE$d.set(wrapper, { chat, history: "", node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.chat, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$d
  //#endregion
};
const EV_HANDLERS$7 = {
  //#region Chip handler
  chip: async (state, e) => {
    const { comp, eventType } = e.detail;
    switch (eventType) {
      case "click":
        const selectedValues = [];
        (await comp.getSelectedNodes()).forEach((node) => {
          selectedValues.push(String(node.value).valueOf());
        });
        state.selected = selectedValues.join(", ");
        break;
    }
  }
};
var ChipCSS;
(function(ChipCSS2) {
  ChipCSS2["Content"] = "lf-chip";
  ChipCSS2["Widget"] = "lf-chip__widget";
})(ChipCSS || (ChipCSS = {}));
const STATE$c = /* @__PURE__ */ new WeakMap();
const chipFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE$c.get(wrapper),
      getValue() {
        const { selected } = STATE$c.get(wrapper);
        return selected || "";
      },
      setValue(value) {
        const state = STATE$c.get(wrapper);
        const callback = (v) => {
          const value2 = v ? v.split(", ") : [];
          state.selected = v;
          state.chip.setSelectedNodes(value2);
        };
        normalizeValue(value, callback, CustomWidgetName.chip);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const chip = document.createElement(TagName.LfChip);
    content.classList.add(ChipCSS.Content);
    chip.classList.add(ChipCSS.Widget);
    chip.addEventListener(LfEventName.LfChip, (e) => EV_HANDLERS$7.chip(STATE$c.get(wrapper), e));
    switch (node.comfyClass) {
      case NodeName.keywordToggleFromJson:
        chip.lfStyling = "filter";
        break;
    }
    content.appendChild(chip);
    wrapper.appendChild(content);
    const options = chipFactory.options(wrapper);
    STATE$c.set(wrapper, { chip, node, selected: "", wrapper });
    return { widget: createDOMWidget(CustomWidgetName.chip, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$c
  //#endregion
};
var CodeCSS;
(function(CodeCSS2) {
  CodeCSS2["Content"] = "lf-code";
  CodeCSS2["Widget"] = "lf-code__widget";
})(CodeCSS || (CodeCSS = {}));
const STATE$b = /* @__PURE__ */ new WeakMap();
const codeFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$b.get(wrapper),
      getValue() {
        const { code } = STATE$b.get(wrapper);
        switch (code.lfLanguage) {
          case "json":
            return code.lfValue || "{}";
          default:
            return code.lfValue || "";
        }
      },
      setValue(value) {
        const { code } = STATE$b.get(wrapper);
        const callback = (v, u) => {
          switch (code.lfLanguage) {
            case "json":
              code.lfValue = u.unescapedString || "{}";
              break;
            default:
              code.lfValue = typeof v === "string" ? v : "";
              break;
          }
        };
        normalizeValue(value, callback, CustomWidgetName.code);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const code = document.createElement(TagName.LfCode);
    content.classList.add(CodeCSS.Content);
    code.classList.add(CodeCSS.Widget);
    switch (node.comfyClass) {
      case NodeName.displayJson:
      case NodeName.displayPrimitiveAsJson:
      case NodeName.shuffleJsonKeys:
      case NodeName.sortJsonKeys:
      case NodeName.stringToJson:
        code.lfLanguage = "json";
        code.lfValue = "{}";
        break;
      default:
        code.lfLanguage = "markdown";
        code.lfValue = "";
        break;
    }
    content.appendChild(code);
    wrapper.appendChild(content);
    const options = codeFactory.options(wrapper);
    STATE$b.set(wrapper, { code, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.code, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$b
  //#endregion
};
var CompareCSS;
(function(CompareCSS2) {
  CompareCSS2["Content"] = "lf-compare";
  CompareCSS2["Widget"] = "lf-compare__widget";
})(CompareCSS || (CompareCSS = {}));
const STATE$a = /* @__PURE__ */ new WeakMap();
const compareFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$a.get(wrapper),
      getValue() {
        const { compare } = STATE$a.get(wrapper);
        return compare.lfDataset || {};
      },
      setValue(value) {
        const { compare } = STATE$a.get(wrapper);
        const callback = (_, u) => {
          compare.lfDataset = u.parsedJSON || {};
        };
        normalizeValue(value, callback, CustomWidgetName.compare);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const compare = document.createElement(TagName.LfCompare);
    content.classList.add(CompareCSS.Content);
    compare.classList.add(CompareCSS.Widget);
    switch (node.comfyClass) {
      default:
        compare.lfShape = "image";
        break;
    }
    content.appendChild(compare);
    wrapper.appendChild(content);
    const options = compareFactory.options(wrapper);
    STATE$a.set(wrapper, { compare, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.compare, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$a
  //#endregion
};
var ControlPanelCSS;
(function(ControlPanelCSS2) {
  ControlPanelCSS2["Content"] = "lf-controlpanel";
  ControlPanelCSS2["Grid"] = "lf-controlpanel__grid";
  ControlPanelCSS2["Spinner"] = "lf-controlpanel__spinner";
})(ControlPanelCSS || (ControlPanelCSS = {}));
var ControlPanelIcons;
(function(ControlPanelIcons2) {
  ControlPanelIcons2["Analytics"] = "chart-histogram";
  ControlPanelIcons2["Backup"] = "download";
  ControlPanelIcons2["Debug"] = "bug";
  ControlPanelIcons2["ExternalPreviews"] = "photo-search";
  ControlPanelIcons2["GitHub"] = "brand-github";
  ControlPanelIcons2["Metadata"] = "hexagon-info";
  ControlPanelIcons2["SystemDashboard"] = "percentage-60";
  ControlPanelIcons2["Theme"] = "color-swatch";
})(ControlPanelIcons || (ControlPanelIcons = {}));
var ControlPanelIds;
(function(ControlPanelIds2) {
  ControlPanelIds2["Analytics"] = "analytics";
  ControlPanelIds2["Backup"] = "backup";
  ControlPanelIds2["Debug"] = "debug";
  ControlPanelIds2["ExternalPreviews"] = "external-previews";
  ControlPanelIds2["GitHub"] = "github";
  ControlPanelIds2["Metadata"] = "metadata";
  ControlPanelIds2["SystemDashboard"] = "system-dashboard";
  ControlPanelIds2["Theme"] = "theme";
})(ControlPanelIds || (ControlPanelIds = {}));
var ControlPanelLabels;
(function(ControlPanelLabels2) {
  ControlPanelLabels2["AutoBackup"] = "Automatic Backup";
  ControlPanelLabels2["Backup"] = "Backup now";
  ControlPanelLabels2["BackupRetention"] = "Maximum backups to keep";
  ControlPanelLabels2["ClearLogs"] = "Clear logs";
  ControlPanelLabels2["ClearPreviews"] = "Clear preview cache";
  ControlPanelLabels2["Debug"] = "Debug";
  ControlPanelLabels2["DeleteUsage"] = "Delete usage analytics info";
  ControlPanelLabels2["DeleteMetadata"] = "Delete models info";
  ControlPanelLabels2["Done"] = "Done!";
  ControlPanelLabels2["OpenIssue"] = "Open an issue";
  ControlPanelLabels2["RefreshBackupStats"] = "Refresh backup stats";
  ControlPanelLabels2["RefreshPreviewStats"] = "Refresh preview stats";
  ControlPanelLabels2["SystemAutoRefresh"] = "Auto refresh (seconds)";
  ControlPanelLabels2["RefreshSystemStats"] = "Refresh system stats";
  ControlPanelLabels2["Theme"] = "Random theme";
})(ControlPanelLabels || (ControlPanelLabels = {}));
var ControlPanelSection;
(function(ControlPanelSection2) {
  ControlPanelSection2["Content"] = "content";
  ControlPanelSection2["ContentSeparator"] = "content_spearator";
  ControlPanelSection2["Paragraph"] = "paragraph";
  ControlPanelSection2["Root"] = "root";
  ControlPanelSection2["Section"] = "section";
})(ControlPanelSection || (ControlPanelSection = {}));
const BUTTON_STYLE = ":host { margin: auto; padding: 1em 0; width: max-content; }";
const STYLES = {
  customization: () => ({
    margin: "0"
  }),
  debugGrid: () => ({
    display: "grid",
    gridTemplateRows: "repeat(5, max-content) 1fr",
    height: "100%",
    margin: "0"
  }),
  debugLogs: () => ({
    display: "grid",
    gridGap: "0.75em",
    gridTemplateRows: "320px 480px"
  }),
  logsArea: () => ({
    backgroundColor: "rgba(var(--lf-color-on-bg), 0.075)",
    borderRadius: "0.5em",
    display: "block",
    height: "100%",
    marginBottom: "1em",
    overflow: "auto"
  }),
  separator: () => ({
    border: "1px solid rgb(var(--lf-color-border))",
    display: "block",
    margin: "0.75em auto 1.25em",
    opacity: "0.25",
    width: "50%"
  })
};
const buildAnalyticsSection = () => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-clear": clearIcon } = theme.get.current().variables;
  return {
    icon: ControlPanelIcons.Analytics,
    id: ControlPanelSection.Section,
    value: "Analytics",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Usage",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Usage analytics can be enabled by saving datasets through the UpdateUsageStatistics node and displayed with the UsageStatistics node."
          },
          {
            id: ControlPanelSection.Content,
            tagName: "br",
            value: ""
          },
          {
            id: ControlPanelSection.Content,
            value: "Once datasets are created (input folder of ComfyUI), the count for each resource used will increase everytime that particular resource is updated."
          },
          {
            id: ControlPanelSection.Content,
            tagName: "br",
            value: ""
          },
          {
            id: ControlPanelSection.Content,
            value: "This button will clear all usage analytics data from your input folder."
          },
          {
            id: ControlPanelSection.Content,
            tagName: "br",
            value: ""
          },
          {
            id: ControlPanelSection.Content,
            value: "This action is IRREVERSIBLE so use it with caution."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: clearIcon,
                lfLabel: ControlPanelLabels.DeleteUsage,
                lfStyle: BUTTON_STYLE,
                lfStyling: "outlined",
                lfUiState: "danger",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildBackupSection = (stats) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-download": downloadIcon, "--lf-icon-refresh": refreshIcon } = theme.get.current().variables;
  const { progress } = theme.get.icons();
  const totalBytes = (stats == null ? void 0 : stats.totalSizeBytes) ?? 0;
  const fileCount = (stats == null ? void 0 : stats.fileCount) ?? 0;
  const maxBytes = 1024 * 1024 * 1024;
  const percentage = Math.min(totalBytes / maxBytes * 100, 100);
  return {
    icon: ControlPanelIcons.Backup,
    id: ControlPanelSection.Section,
    value: "Backup",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Toggle on/off",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Toggle this toggle to automatically back up the folder <path/to/your/comfyui/user/LF_Nodes> once a day (the first time you open this workflow)."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfToggle: {
                lfLabel: ControlPanelLabels.AutoBackup,
                lfLeadingLabel: true,
                lfStyle: ":host { text-align: center; padding: 1em 0; }",
                shape: "toggle",
                value: !!getLfManager().isBackupEnabled()
              }
            }
          }
        ]
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Backup statistics",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Backup files are stored in the user/LF_Nodes folder. Monitor your backup folder size to ensure you have enough disk space."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "",
            children: [
              {
                id: "backup-info",
                value: `Current backup: ${formatBytes(totalBytes)} (${fileCount} files)`,
                cssStyle: { display: "block", marginBottom: "0.75em" }
              },
              {
                id: "backup-progress",
                value: "",
                cells: {
                  lfProgressbar: {
                    lfIcon: progress,
                    lfLabel: `${formatBytes(totalBytes)} (${percentage.toFixed(1)}%)`,
                    shape: "progressbar",
                    value: percentage
                  }
                }
              }
            ]
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: refreshIcon,
                lfLabel: ControlPanelLabels.RefreshBackupStats,
                lfStyle: BUTTON_STYLE,
                lfStyling: "flat",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Rolling backup retention",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Set the maximum number of backups to keep. When this limit is exceeded, the oldest backups will be automatically deleted. Set to 0 to disable this feature."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfTextfield: {
                lfHtmlAttributes: { type: "number" },
                lfLabel: ControlPanelLabels.BackupRetention,
                lfStyle: ":host { text-align: center; padding: 1em 0; }",
                lfValue: getLfManager().getBackupRetention().toString() || "14",
                shape: "textfield",
                value: ""
              }
            }
          }
        ]
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Backup files",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "This button will create a manual backup of the content in <path/to/your/comfyui/user/LF_Nodes>."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: downloadIcon,
                lfLabel: ControlPanelLabels.Backup,
                lfStyle: BUTTON_STYLE,
                lfStyling: "raised",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildDebugSection = (logsData) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-clear": clearIcon } = theme.get.current().variables;
  return {
    icon: ControlPanelIcons.Debug,
    id: ControlPanelSection.Section,
    cssStyle: STYLES.debugGrid(),
    value: "Debug",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Toggle on/off",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Activating the debug will enable the display of verbose logging."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfToggle: {
                lfLabel: ControlPanelLabels.Debug,
                lfLeadingLabel: true,
                lfStyle: ":host { text-align: center; padding: 1em 0; }",
                shape: "toggle",
                value: !!getLfManager().isDebug()
              }
            }
          }
        ]
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Logs",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Every time the node manager receives a message it will be printed below."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "In the browser console there should be more informations."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "Further below another card will display additional LF Widgets information."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                shape: "button",
                lfIcon: clearIcon,
                lfLabel: ControlPanelLabels.ClearLogs,
                lfStretchX: true,
                lfStyle: BUTTON_STYLE,
                lfUiState: "danger",
                value: ""
              }
            }
          }
        ]
      },
      {
        id: ControlPanelSection.Paragraph,
        cssStyle: STYLES.debugLogs(),
        value: "",
        children: [
          {
            id: "content-wrapper",
            cssStyle: STYLES.logsArea(),
            value: "",
            children: logsData
          },
          {
            id: "content-wrapper",
            value: "",
            cells: {
              lfCard: {
                lfDataset: {
                  nodes: [
                    {
                      cells: {
                        lfCode: { shape: "code", value: "" },
                        lfButton: { shape: "button", value: "" },
                        lfButton_2: { shape: "button", value: "" },
                        lfToggle: {
                          shape: "toggle",
                          value: !!getLfManager().getManagers().lfFramework.debug.isEnabled()
                        }
                      },
                      id: "debug"
                    }
                  ]
                },
                lfLayout: "debug",
                shape: "card",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildExternalPreviewsSection = (stats) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-delete": deleteIcon, "--lf-icon-refresh": refreshIcon } = theme.get.current().variables;
  const { progress } = theme.get.icons();
  const totalBytes = (stats == null ? void 0 : stats.totalSizeBytes) ?? 0;
  const fileCount = (stats == null ? void 0 : stats.fileCount) ?? 0;
  const maxBytes = 1024 * 1024 * 1024;
  const percentage = Math.min(totalBytes / maxBytes * 100, 100);
  return {
    icon: ControlPanelIcons.ExternalPreviews,
    id: ControlPanelSection.Section,
    value: "External Previews",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Cache statistics",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "External image previews are cached in the _lf_external_previews folder under ComfyUI/input to speed up loading."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "",
            children: [
              {
                id: "cache-info",
                value: `Current cache: ${formatBytes(totalBytes)} (${fileCount} files)`,
                cssStyle: { display: "block", marginBottom: "0.75em" }
              },
              {
                id: "cache-progress",
                value: "",
                cells: {
                  lfProgressbar: {
                    lfIcon: progress,
                    lfLabel: `${formatBytes(totalBytes)} (${percentage.toFixed(1)}%)`,
                    shape: "progressbar",
                    value: percentage
                  }
                }
              }
            ]
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: refreshIcon,
                lfLabel: ControlPanelLabels.RefreshPreviewStats,
                lfStyle: BUTTON_STYLE,
                lfStyling: "flat",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Clear cache",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "This button will permanently delete the entire preview cache folder and all its contents."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "This action is IRREVERSIBLE so use it with caution."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: deleteIcon,
                lfLabel: ControlPanelLabels.ClearPreviews,
                lfStyle: BUTTON_STYLE,
                lfStyling: "outlined",
                lfUiState: "danger",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildGitHubSection = () => {
  var _a, _b;
  const lfManager = getLfManager();
  const releaseData = lfManager.getLatestRelease();
  const { theme } = lfManager.getManagers().lfFramework;
  const { brandGithub } = theme.get.icons();
  return {
    icon: ControlPanelIcons.GitHub,
    id: ControlPanelSection.Section,
    value: "",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: `Version: ${(releaseData == null ? void 0 : releaseData.tag_name) || "N/A"}`,
        children: [
          {
            cells: {
              lfCode: {
                lfLanguage: "markdown",
                shape: "code",
                value: (releaseData == null ? void 0 : releaseData.body) || "No changelog available"
              }
            },
            id: "release-description"
          },
          {
            id: "release-author",
            children: [
              {
                id: "author-avatar",
                value: "",
                cssStyle: {
                  backgroundImage: `url(${((_a = releaseData == null ? void 0 : releaseData.author) == null ? void 0 : _a.avatar_url) || ""})`,
                  backgroundSize: "cover",
                  borderRadius: "50%",
                  display: "inline-block",
                  height: "2em",
                  marginRight: "0.5em",
                  verticalAlign: "middle",
                  width: "2em"
                }
              },
              {
                id: "author-name",
                value: `Author: ${((_b = releaseData == null ? void 0 : releaseData.author) == null ? void 0 : _b.login) || "Unknown"}`,
                cssStyle: {
                  fontSize: "0.9em",
                  color: "rgb(var(--lf-color-secondary))",
                  verticalAlign: "middle"
                }
              }
            ],
            cssStyle: {
              alignItems: "center",
              display: "flex",
              justifyContent: "center",
              marginBottom: ".25em"
            }
          },
          {
            cssStyle: {
              color: "rgb(var(--lf-color-secondary))",
              display: "block",
              fontSize: "0.9em",
              fontStyle: "italic",
              marginBottom: "2em",
              textAlign: "center",
              width: "100%"
            },
            id: "release-date",
            value: `Published on: ${(releaseData == null ? void 0 : releaseData.published_at) ? new Date(releaseData.published_at).toLocaleDateString() : "Unknown"}`
          },
          {
            cssStyle: STYLES.separator(),
            id: ControlPanelSection.ContentSeparator,
            value: ""
          },
          {
            id: ControlPanelSection.Paragraph,
            value: "Bug report",
            children: [
              {
                id: ControlPanelSection.Content,
                value: "If you find bugs or odd behaviors feel free to open an issue on GitHub, just follow the link below!"
              },
              { id: ControlPanelSection.Content, tagName: "br", value: "" },
              {
                id: ControlPanelSection.Content,
                value: "Be sure to include as much information as you can, without sufficient data it's difficult to troubleshoot problems."
              },
              {
                id: ControlPanelSection.Content,
                value: "",
                cells: {
                  lfButton: {
                    lfIcon: brandGithub,
                    lfLabel: ControlPanelLabels.OpenIssue,
                    lfStyle: BUTTON_STYLE,
                    lfStyling: "raised",
                    shape: "button",
                    value: ""
                  }
                }
              }
            ]
          }
        ]
      }
    ]
  };
};
const buildMetadataSection = () => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-delete": deleteIcon } = theme.get.current().variables;
  return {
    icon: ControlPanelIcons.Metadata,
    id: ControlPanelSection.Section,
    value: "Metadata",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Purge metadata files",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Metadata pulled from CivitAI are stored in .info files saved in the same folders of the models to avoid unnecessary fetches from the API."
          },
          { id: ControlPanelSection.Content, tagName: "div", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "By pressing this button it's possible to delete every .info file created by fetching the metadata."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "This action is IRREVERSIBLE so use it with caution."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: deleteIcon,
                lfLabel: ControlPanelLabels.DeleteMetadata,
                lfStyle: BUTTON_STYLE,
                lfStyling: "outlined",
                lfUiState: "danger",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildSystemDashboardSection = (stats) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-refresh": refreshIcon } = theme.get.current().variables;
  const { progress } = theme.get.icons();
  const refreshTimeout = getLfManager().getSystemTimeout() || 0;
  const gpus = (stats == null ? void 0 : stats.gpus) ?? [];
  const disks = (stats == null ? void 0 : stats.disks) ?? [];
  const cpu = stats == null ? void 0 : stats.cpu;
  const ram = stats == null ? void 0 : stats.ram;
  const errors = (stats == null ? void 0 : stats.errors) ?? [];
  const timestamp = (stats == null ? void 0 : stats.timestamp) ? new Date(stats.timestamp) : null;
  const lastUpdated = timestamp ? timestamp.toLocaleString() : "Waiting for data";
  const gpuNodes = gpus.length ? gpus.map((gpu) => {
    const vramPercent = gpu.vram_total ? clampPercent(gpu.vram_used / gpu.vram_total * 100) : 0;
    const utilPercent = clampPercent(gpu.utilization);
    return {
      id: `gpu-${gpu.index}`,
      value: "",
      cssStyle: { marginBottom: "1em" },
      children: [
        {
          id: `gpu-${gpu.index}-title`,
          value: `${gpu.name} (GPU ${gpu.index})`,
          tagName: "strong"
        },
        buildProgressNode(progress, `gpu-${gpu.index}-vram`, `VRAM ${formatBytes(gpu.vram_used)} / ${formatBytes(gpu.vram_total)} (${percentLabel(vramPercent)})`, vramPercent),
        buildProgressNode(progress, `gpu-${gpu.index}-util`, `Utilization ${percentLabel(utilPercent)}`, utilPercent)
      ]
    };
  }) : [
    {
      id: "gpu-none",
      value: "No GPUs detected.",
      cssStyle: { opacity: "0.7" }
    }
  ];
  const cpuNodes = cpu ? [
    buildProgressNode(progress, "cpu-average", `Average usage ${percentLabel(cpu.average)}`, clampPercent(cpu.average)),
    {
      id: "cpu-meta",
      value: `Logical cores: ${cpu.count} • Physical cores: ${cpu.physical_count}`,
      cssStyle: { fontSize: "0.9em", opacity: "0.8" }
    },
    {
      id: "cpu-cores",
      value: "",
      cssStyle: {
        display: "grid",
        gap: "0.75em",
        gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))"
      },
      children: cpu.cores.map((core) => buildProgressNode(progress, `cpu-core-${core.index}`, `Core ${core.index} ${percentLabel(core.usage)}`, clampPercent(core.usage)))
    }
  ] : [
    {
      id: "cpu-none",
      value: "CPU statistics unavailable.",
      cssStyle: { opacity: "0.7" }
    }
  ];
  const ramNodes = ram ? [
    buildProgressNode(progress, "ram-usage", `RAM ${formatBytes(ram.used)} / ${formatBytes(ram.total)} (${percentLabel(ram.percent)})`, clampPercent(ram.percent)),
    {
      id: "ram-available",
      value: `Available: ${formatBytes(ram.available)}`,
      cssStyle: { fontSize: "0.9em", opacity: "0.8" }
    },
    ...ram.swap_total ? [
      buildProgressNode(progress, "swap-usage", `Swap ${formatBytes(ram.swap_used)} / ${formatBytes(ram.swap_total)} (${percentLabel(ram.swap_used / ram.swap_total * 100)})`, clampPercent(ram.swap_used / ram.swap_total * 100))
    ] : []
  ] : [
    {
      id: "ram-none",
      value: "RAM statistics unavailable.",
      cssStyle: { opacity: "0.7" }
    }
  ];
  const diskNodes = disks.length ? disks.map((disk, index) => {
    const used = toNumber(disk.used);
    const total = toNumber(disk.total);
    const percent = total ? clampPercent(used / total * 100) : clampPercent(disk.percent);
    const descriptor = [disk.device || disk.mountpoint, disk.label].filter(Boolean).join(" ");
    return {
      id: `disk-${index}`,
      value: "",
      cssStyle: { marginBottom: "1em" },
      children: [
        {
          id: `disk-${index}-title`,
          value: descriptor || disk.mountpoint,
          tagName: "strong"
        },
        {
          id: `disk-${index}-mount`,
          value: `Mount: ${disk.mountpoint}`,
          cssStyle: { fontSize: "0.9em", opacity: "0.8", marginBottom: "0.25em" }
        },
        buildProgressNode(progress, `disk-${index}-usage`, `${formatBytes(disk.used)} / ${formatBytes(disk.total)} (${percentLabel(percent)})`, percent)
      ]
    };
  }) : [
    {
      id: "disk-none",
      value: "No disks detected.",
      cssStyle: { opacity: "0.7" }
    }
  ];
  const overviewChildren = [
    {
      id: ControlPanelSection.Content,
      value: "Monitor real-time hardware usage for GPUs, CPU, memory, and storage."
    },
    {
      id: ControlPanelSection.Content,
      value: `Last updated: ${lastUpdated}`,
      cssStyle: { fontSize: "0.85em", opacity: "0.75" }
    },
    {
      id: ControlPanelSection.Content,
      value: refreshTimeout > 0 ? `Auto refresh every ${refreshTimeout}s` : "Auto refresh disabled.",
      cssStyle: { fontSize: "0.85em", opacity: "0.75", marginTop: "0.3em" }
    },
    {
      id: ControlPanelSection.Content,
      value: "",
      cells: {
        lfTextfield: {
          lfHelper: { showWhenFocused: false, value: "Set to 0 to disable auto refresh" },
          lfHtmlAttributes: { type: "number", min: "0", step: "any" },
          lfLabel: ControlPanelLabels.SystemAutoRefresh,
          lfStyle: ":host { display: block; margin: 0.75em auto; max-width: 240px; }",
          lfValue: refreshTimeout > 0 ? refreshTimeout.toString() : "",
          shape: "textfield",
          value: ""
        }
      }
    }
  ];
  if (errors.length) {
    overviewChildren.push({
      id: "system-errors",
      value: "",
      children: errors.map((message, index) => ({
        id: `system-error-${index}`,
        value: message,
        cssStyle: {
          color: "rgb(var(--lf-color-danger))",
          fontSize: "0.85em"
        }
      }))
    });
  }
  overviewChildren.push({
    id: ControlPanelSection.Content,
    value: "",
    cells: {
      lfButton: {
        lfIcon: refreshIcon,
        lfLabel: ControlPanelLabels.RefreshSystemStats,
        lfStyle: BUTTON_STYLE,
        lfStyling: "flat",
        shape: "button",
        value: ""
      }
    }
  });
  return {
    icon: ControlPanelIcons.SystemDashboard,
    id: ControlPanelSection.Section,
    value: "System monitor",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Overview",
        children: overviewChildren
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "GPU usage",
        children: gpuNodes
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "CPU usage",
        children: cpuNodes
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Memory",
        children: ramNodes
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Disk usage",
        children: diskNodes
      }
    ]
  };
};
const getUsageState = (percent) => {
  const value = clampPercent(percent);
  if (value >= 90)
    return "danger";
  if (value >= 70)
    return "warning";
  if (value === 0)
    return "primary";
  return "success";
};
const buildProgressNode = (icon, id, label, percent) => ({
  id,
  value: "",
  cells: {
    lfProgressbar: {
      lfIcon: icon,
      lfLabel: label,
      lfUiState: getUsageState(percent),
      shape: "progressbar",
      value: clampPercent(percent)
    }
  }
});
const buildThemeSection = () => {
  return {
    icon: ControlPanelIcons.Theme,
    id: ControlPanelSection.Section,
    value: "Customization",
    cssStyle: STYLES.customization(),
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Theme selector",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Through the button below it's possible to set a random theme for the LF Widgets components, or select one from the dropdown menu."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfDataset: getLfThemes(),
                lfLabel: ControlPanelLabels.Theme,
                lfStyle: BUTTON_STYLE,
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const SECTIONS = {
  [ControlPanelIds.Analytics]: buildAnalyticsSection,
  [ControlPanelIds.Backup]: buildBackupSection,
  [ControlPanelIds.Debug]: buildDebugSection,
  [ControlPanelIds.ExternalPreviews]: buildExternalPreviewsSection,
  [ControlPanelIds.GitHub]: buildGitHubSection,
  [ControlPanelIds.Metadata]: buildMetadataSection,
  [ControlPanelIds.SystemDashboard]: buildSystemDashboardSection,
  [ControlPanelIds.Theme]: buildThemeSection
};
const setArticleDataset = (article, node) => {
  article.lfDataset = {
    nodes: [{ children: [node], id: ControlPanelSection.Root }]
  };
};
let SYSTEM_REFRESH_TIMER = null;
let SYSTEM_ARTICLE = null;
let SYSTEM_LAST_STATS;
const clearSystemAutoRefresh = () => {
  if (SYSTEM_REFRESH_TIMER) {
    clearTimeout(SYSTEM_REFRESH_TIMER);
    SYSTEM_REFRESH_TIMER = null;
  }
};
const getSystemAutoRefreshSeconds = () => {
  var _a, _b;
  try {
    const stored = ((_b = (_a = getLfManager()) == null ? void 0 : _a.getSystemTimeout) == null ? void 0 : _b.call(_a)) ?? 0;
    return typeof stored === "number" && stored > 0 ? Math.floor(stored) : 0;
  } catch {
    return 0;
  }
};
const hasConnectedArticle = () => {
  return SYSTEM_ARTICLE && SYSTEM_ARTICLE.isConnected && document.body.contains(SYSTEM_ARTICLE);
};
const scheduleSystemAutoRefresh = () => {
  clearSystemAutoRefresh();
  const seconds = getSystemAutoRefreshSeconds();
  if (seconds <= 0 || !hasConnectedArticle()) {
    return;
  }
  const delay = Math.max(seconds * 1e3, 1e3);
  SYSTEM_REFRESH_TIMER = setTimeout(() => {
    if (!hasConnectedArticle()) {
      clearSystemAutoRefresh();
      return;
    }
    refreshSystemDashboard(SYSTEM_ARTICLE, { reschedule: false }).finally(() => {
      scheduleSystemAutoRefresh();
    });
  }, delay);
};
const setSystemAutoRefreshSeconds = (seconds, article) => {
  const sanitized = typeof seconds === "number" && Number.isFinite(seconds) && seconds > 0 ? Math.floor(seconds) : 0;
  getLfManager().setSystemTimeout(sanitized);
  if (article) {
    SYSTEM_ARTICLE = article;
  }
  if (sanitized > 0) {
    scheduleSystemAutoRefresh();
  } else {
    clearSystemAutoRefresh();
  }
  const targetArticle = article ?? SYSTEM_ARTICLE;
  if (targetArticle) {
    applySystemStats(targetArticle, SYSTEM_LAST_STATS);
  }
  return sanitized;
};
const applySystemStats = (article, stats) => {
  const nextStats = stats ? { ...stats } : SYSTEM_LAST_STATS ? { ...SYSTEM_LAST_STATS } : void 0;
  SYSTEM_LAST_STATS = nextStats;
  setArticleDataset(article, SECTIONS[ControlPanelIds.SystemDashboard](nextStats));
  requestAnimationFrame(() => {
    const textfield = article.querySelector(`lf-textfield[lf-label="${ControlPanelLabels.SystemAutoRefresh}"]`);
    if (textfield) {
      const timeout = getSystemAutoRefreshSeconds();
      const value = timeout > 0 ? timeout.toString() : "";
      if (textfield.lfValue !== value) {
        textfield.lfValue = value;
      }
    }
  });
};
const gatherSystemStats = async () => {
  const routes = getApiRoutes().system;
  const [gpu, cpu, ram, disks] = await Promise.all([
    routes.getGpuStats(),
    routes.getCpuStats(),
    routes.getRamStats(),
    routes.getDiskStats()
  ]);
  const stats = { timestamp: Date.now() };
  const errors = [];
  if (gpu.status === LogSeverity.Success) {
    stats.gpus = gpu.data || [];
  } else {
    errors.push(`GPU: ${gpu.message || "Statistics unavailable."}`);
  }
  if (cpu.status === LogSeverity.Success) {
    stats.cpu = cpu.data;
  } else {
    errors.push(`CPU: ${cpu.message || "Statistics unavailable."}`);
  }
  if (ram.status === LogSeverity.Success) {
    stats.ram = ram.data;
  } else {
    errors.push(`RAM: ${ram.message || "Statistics unavailable."}`);
  }
  if (disks.status === LogSeverity.Success) {
    stats.disks = disks.data || [];
  } else {
    errors.push(`Disks: ${disks.message || "Statistics unavailable."}`);
  }
  if (errors.length) {
    stats.errors = errors;
  }
  return stats;
};
const refreshSystemDashboard = async (article, options = {}) => {
  var _a;
  const { reschedule = true } = options;
  const payload = {
    message: "",
    status: LogSeverity.Info
  };
  SYSTEM_ARTICLE = article;
  try {
    const stats = await gatherSystemStats();
    applySystemStats(article, stats);
    if ((_a = stats.errors) == null ? void 0 : _a.length) {
      payload.message = `System statistics updated with warnings: ${stats.errors.join(" | ")}`;
      payload.status = LogSeverity.Warning;
    } else {
      payload.message = "System statistics updated.";
      payload.status = LogSeverity.Success;
    }
  } catch (error) {
    payload.message = String(error);
    payload.status = LogSeverity.Error;
  }
  if (reschedule) {
    scheduleSystemAutoRefresh();
  }
  return payload;
};
const getSystemLastStats = () => SYSTEM_LAST_STATS;
let BUTTON_TIMEOUT;
const INTRO_SECTION = ControlPanelIds.GitHub;
const withButtonSpinner = (comp, promise, label) => {
  const onResponse2 = () => {
    comp.lfIcon = "check";
    comp.lfLabel = ControlPanelLabels.Done;
    comp.lfShowSpinner = false;
    comp.lfUiState = "disabled";
  };
  const restore = () => {
    comp.lfLabel = label;
    comp.lfIcon = "x";
    comp.lfUiState = "primary";
    BUTTON_TIMEOUT = null;
  };
  requestAnimationFrame(() => comp.lfShowSpinner = true);
  promise.then(() => {
    requestAnimationFrame(onResponse2);
    if (BUTTON_TIMEOUT) {
      clearTimeout(BUTTON_TIMEOUT);
    }
    BUTTON_TIMEOUT = setTimeout(() => requestAnimationFrame(restore), 1e3);
  });
};
const updateArticleSection = (article, id, data) => {
  const buildNode = SECTIONS[id];
  if (!buildNode)
    return;
  setArticleDataset(article, buildNode(data));
};
const handleButtonClick = (comp, slot) => {
  switch (comp.lfLabel) {
    case ControlPanelLabels.Backup:
      withButtonSpinner(comp, getApiRoutes().backup.new("manual"), ControlPanelLabels.Backup);
      getApiRoutes().backup.cleanOld();
      break;
    case ControlPanelLabels.ClearLogs: {
      const { article, dataset } = getLfManager().getDebugDataset();
      if ((dataset == null ? void 0 : dataset.length) > 0) {
        dataset.splice(0, dataset.length);
        article.refresh();
      }
      break;
    }
    case ControlPanelLabels.ClearPreviews:
      withButtonSpinner(comp, getApiRoutes().preview.clearCache(), ControlPanelLabels.ClearPreviews);
      break;
    case ControlPanelLabels.DeleteMetadata:
      withButtonSpinner(comp, getApiRoutes().metadata.clear(), ControlPanelLabels.DeleteMetadata);
      break;
    case ControlPanelLabels.DeleteUsage:
      withButtonSpinner(comp, getApiRoutes().analytics.clear("usage"), ControlPanelLabels.DeleteUsage);
      break;
    case ControlPanelLabels.OpenIssue:
      window.open("https://github.com/lucafoscili/comfyui-lf/issues/new", "_blank");
      break;
    case ControlPanelLabels.RefreshPreviewStats:
      getApiRoutes().preview.getStats().then((response) => {
        if (response.status === "success") {
          updateArticleSection(slot, ControlPanelIds.ExternalPreviews, {
            totalSizeBytes: response.data.total_size_bytes,
            fileCount: response.data.file_count
          });
        }
      });
      break;
    case ControlPanelLabels.RefreshBackupStats:
      getApiRoutes().backup.getStats().then((response) => {
        if (response.status === "success") {
          updateArticleSection(slot, ControlPanelIds.Backup, {
            totalSizeBytes: response.data.total_size_bytes,
            fileCount: response.data.file_count
          });
        }
      });
      break;
    case ControlPanelLabels.RefreshSystemStats:
      withButtonSpinner(comp, refreshSystemDashboard(slot), ControlPanelLabels.RefreshSystemStats);
      break;
    case ControlPanelLabels.Theme:
      getLfManager().getManagers().lfFramework.theme.randomize();
      break;
  }
};
const EV_HANDLERS$6 = {
  article: (e) => {
    const { comp, eventType, originalEvent } = e.detail;
    if (eventType === "lf-event") {
      handleLfEvent(originalEvent, comp.rootElement);
    }
  },
  button: (e, slot) => {
    const { comp, eventType, originalEvent } = e.detail;
    switch (eventType) {
      case "click":
        handleButtonClick(comp, slot);
        break;
      case "lf-event": {
        const ogEv = originalEvent;
        EV_HANDLERS$6.list(ogEv);
        break;
      }
    }
  },
  list: (e) => {
    const { comp, eventType, node } = e.detail;
    const { lfFramework } = getLfManager().getManagers();
    const element = comp.rootElement;
    const value = node.id;
    switch (eventType) {
      case "click":
        lfFramework.theme.set(value);
        break;
      case "ready":
        element.title = "Change the LF Nodes suite theme";
        lfFramework.theme.set(value);
        break;
    }
  },
  textfield: (e) => {
    const { comp, eventType, value } = e.detail;
    const element = comp.rootElement;
    const article = element.closest("lf-article");
    switch (eventType) {
      case "change":
        if (comp.lfLabel === ControlPanelLabels.SystemAutoRefresh) {
          const trimmed = (value || "").trim();
          const parsed = trimmed ? Number(trimmed) : 0;
          const normalized = setSystemAutoRefreshSeconds(parsed, article);
          comp.lfValue = normalized > 0 ? normalized.toString() : "";
        } else if (comp.lfLabel === ControlPanelLabels.BackupRetention) {
          const retentionValue = parseInt(value, 10);
          if (!isNaN(retentionValue) && retentionValue >= 0) {
            getLfManager().setBackupRetention(retentionValue);
          }
        }
        break;
      case "ready":
        if (comp.lfLabel === ControlPanelLabels.SystemAutoRefresh) {
          element.title = "Auto refresh interval in seconds (0 or empty disables auto refresh)";
          const currentTimeout = getSystemAutoRefreshSeconds();
          comp.lfValue = currentTimeout > 0 ? currentTimeout.toString() : comp.lfValue || "";
        } else if (comp.lfLabel === ControlPanelLabels.BackupRetention) {
          element.title = "Maximum number of backups to keep (0 = unlimited)";
        }
        break;
    }
  },
  toggle: (e) => {
    const { comp, eventType, value } = e.detail;
    const element = comp.rootElement;
    switch (eventType) {
      case "change":
        getLfManager().toggleDebug(value === "on" ? true : false);
        break;
      case "ready":
        element.title = "Activate verbose console logging";
        break;
    }
  }
};
const handleLfEvent = (e, slot) => {
  const { comp } = e.detail;
  if (isButton(comp)) {
    const ogEv = e;
    EV_HANDLERS$6.button(ogEv, slot);
  }
  if (isTextfield(comp)) {
    const ogEv = e;
    EV_HANDLERS$6.textfield(ogEv);
  }
  if (isToggle(comp)) {
    const ogEv = e;
    EV_HANDLERS$6.toggle(ogEv);
  }
};
const INTRO_SECTION_ID = INTRO_SECTION;
const prepArticle = (key, node) => {
  const article = document.createElement(TagName.LfArticle);
  setArticleDataset(article, node);
  article.slot = key;
  article.addEventListener(LfEventName.LfArticle, EV_HANDLERS$6.article);
  return article;
};
const buildSection = (id) => {
  switch (id) {
    //#region Analytics
    case ControlPanelIds.Analytics: {
      const node = SECTIONS[ControlPanelIds.Analytics]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion
    //#region Backup
    case ControlPanelIds.Backup: {
      const node = SECTIONS[ControlPanelIds.Backup]();
      const article = prepArticle(id, node);
      getApiRoutes().backup.getStats().then((response) => {
        if (response.status === "success") {
          const updatedNode = SECTIONS[ControlPanelIds.Backup]({
            totalSizeBytes: response.data.total_size_bytes,
            fileCount: response.data.file_count
          });
          setArticleDataset(article, updatedNode);
        }
      });
      return { article, node };
    }
    //#endregion
    //#region Debug
    case ControlPanelIds.Debug: {
      const logsData = [];
      const node = SECTIONS[ControlPanelIds.Debug](logsData);
      const article = prepArticle(id, node);
      getLfManager().setDebugDataset(article, logsData);
      return { article, node };
    }
    //#endregion
    //#region ExternalPreviews
    case ControlPanelIds.ExternalPreviews: {
      const node = SECTIONS[ControlPanelIds.ExternalPreviews]();
      const article = prepArticle(id, node);
      getApiRoutes().preview.getStats().then((response) => {
        if (response.status === "success") {
          const updatedNode = SECTIONS[ControlPanelIds.ExternalPreviews]({
            totalSizeBytes: response.data.total_size_bytes,
            fileCount: response.data.file_count
          });
          setArticleDataset(article, updatedNode);
        }
      });
      return { article, node };
    }
    //#endregion
    //#region Metadata
    case ControlPanelIds.Metadata: {
      const node = SECTIONS[ControlPanelIds.Metadata]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion
    //#region System Dashboard
    case ControlPanelIds.SystemDashboard: {
      const initialStats = getSystemLastStats();
      const node = SECTIONS[ControlPanelIds.SystemDashboard](initialStats);
      const article = prepArticle(id, node);
      applySystemStats(article, initialStats);
      refreshSystemDashboard(article);
      return { article, node };
    }
    //#endregion
    //#region Theme
    case ControlPanelIds.Theme: {
      const node = SECTIONS[ControlPanelIds.Theme]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion
    default:
      return null;
  }
};
const createContent = () => {
  const grid = document.createElement(TagName.Div);
  const accordion = document.createElement(TagName.LfAccordion);
  const nodes = [];
  accordion.lfDataset = { nodes };
  for (const id in SECTIONS) {
    if (id !== INTRO_SECTION_ID && Object.prototype.hasOwnProperty.call(SECTIONS, id)) {
      const section = buildSection(id);
      if (!section) {
        continue;
      }
      const { article, node } = section;
      const { icon, value } = node;
      nodes.push({
        cells: {
          lfSlot: {
            shape: "slot",
            value: id
          }
        },
        icon,
        id,
        value
      });
      accordion.appendChild(article);
    }
  }
  const intro = prepArticle(INTRO_SECTION_ID, SECTIONS[INTRO_SECTION_ID]());
  grid.classList.add(ControlPanelCSS.Grid);
  grid.appendChild(intro);
  grid.appendChild(accordion);
  return grid;
};
const STATE$9 = /* @__PURE__ */ new WeakMap();
const controlPanelFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$9.get(wrapper),
      getValue() {
        return {
          backup: getLfManager().isBackupEnabled() || false,
          backupRetention: getLfManager().getBackupRetention() || 14,
          debug: getLfManager().isDebug() || false,
          systemTimeout: getLfManager().getSystemTimeout() || 0,
          themes: getLfManager().getManagers().lfFramework.theme.get.current().name || ""
        };
      },
      setValue(value) {
        const callback = (_, u) => {
          const { backup, backupRetention, debug, systemTimeout, themes } = u.parsedJSON;
          if (backup === true || backup === false) {
            getLfManager().toggleBackup(backup);
          }
          if (typeof backupRetention === "number") {
            getLfManager().setBackupRetention(backupRetention);
          }
          if (debug === true || debug === false) {
            getLfManager().toggleDebug(debug);
          }
          if (typeof systemTimeout === "number") {
            setSystemAutoRefreshSeconds(systemTimeout);
          }
          if (themes) {
            getLfManager().getManagers().lfFramework.theme.set(themes);
          }
          return value;
        };
        normalizeValue(value, callback, CustomWidgetName.controlPanel);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const contentCb = (domWidget, isReady) => {
      const readyCb = (domWidget2) => {
        setTimeout(() => {
          getApiRoutes().backup.new();
          contentCb(domWidget2, true);
          getApiRoutes().backup.cleanOld();
        }, 750);
      };
      const createSpinner = () => {
        const spinner = document.createElement(TagName.LfSpinner);
        spinner.classList.add(ControlPanelCSS.Spinner);
        spinner.lfActive = true;
        spinner.lfLayout = 11;
        return spinner;
      };
      const content = document.createElement(TagName.Div);
      if (isReady) {
        content.appendChild(createContent());
        domWidget.replaceChild(content, domWidget.firstChild);
      } else {
        const spinner = createSpinner();
        spinner.addEventListener(LfEventName.LfSpinner, readyCb.bind(null, domWidget));
        content.appendChild(spinner);
        domWidget.appendChild(content);
      }
      content.classList.add(ControlPanelCSS.Content);
    };
    const wrapper = document.createElement(TagName.Div);
    contentCb(wrapper, false);
    const options = controlPanelFactory.options(wrapper);
    STATE$9.set(wrapper, { node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.controlPanel, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$9
  //#endregion
};
var CountBarChartCSS;
(function(CountBarChartCSS2) {
  CountBarChartCSS2["Content"] = "lf-countbarchart";
  CountBarChartCSS2["Widget"] = "lf-countbarchart__widget";
})(CountBarChartCSS || (CountBarChartCSS = {}));
const STATE$8 = /* @__PURE__ */ new WeakMap();
const countBarChartFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE$8.get(wrapper),
      getValue() {
        const { datasets } = STATE$8.get(wrapper);
        return {
          chart: (datasets == null ? void 0 : datasets.chart) || {},
          chip: (datasets == null ? void 0 : datasets.chip) || {}
        };
      },
      setValue(value) {
        const { card, datasets } = STATE$8.get(wrapper);
        const callback = (_, u) => {
          const json = u.parsedJSON;
          datasets.chart = json.chart || {};
          datasets.chip = json.chip || {};
          card.lfDataset = {
            nodes: [
              {
                id: "countBarChart",
                cells: {
                  lfButton: { shape: "button", value: "" },
                  lfChart: {
                    lfAxis: ["Axis_0"],
                    lfDataset: datasets.chart,
                    lfSeries: ["Series_0"],
                    shape: "chart",
                    value: ""
                  },
                  lfChip: { lfDataset: datasets.chip, shape: "chip", value: "" }
                }
              }
            ]
          };
        };
        normalizeValue(value, callback, CustomWidgetName.countBarChart);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const card = document.createElement(TagName.LfCard);
    const chart = {};
    const chip = {};
    card.classList.add(CountBarChartCSS.Widget);
    card.lfLayout = "keywords";
    content.classList.add(CountBarChartCSS.Content);
    content.appendChild(card);
    wrapper.appendChild(content);
    const options = countBarChartFactory.options(wrapper);
    STATE$8.set(wrapper, { card, datasets: { chart, chip }, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.countBarChart, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$8
  //#endregion
};
const EV_HANDLERS$5 = {
  //#region List handler
  list: (state, e) => {
    const { eventType, node } = e.detail;
    const comfyNode = state.node;
    const strValue = node ? String(node.value).valueOf() : "";
    if (eventType === "click" && strValue) {
      const boolW = getWidget(comfyNode, ComfyWidgetName.boolean);
      const comboW = getWidget(comfyNode, ComfyWidgetName.combo);
      const customtextW = getWidget(comfyNode, ComfyWidgetName.customtext);
      const floatW = getWidget(comfyNode, ComfyWidgetName.float);
      const intW = getWidget(comfyNode, ComfyWidgetName.integer);
      const numberW = getWidget(comfyNode, ComfyWidgetName.number);
      const seedW = getWidget(comfyNode, ComfyWidgetName.seed);
      const stringW = getWidget(comfyNode, ComfyWidgetName.string);
      const textW = getWidget(comfyNode, ComfyWidgetName.text);
      const toggleW = getWidget(comfyNode, ComfyWidgetName.toggle);
      switch (comfyNode.comfyClass) {
        case NodeName.boolean:
          if (boolW) {
            boolW.value = String(node.value).toLowerCase() === "true" ? true : false;
          } else if (toggleW) {
            toggleW.value = String(node.value).toLowerCase() === "true" ? true : false;
          }
          break;
        case NodeName.float:
          if (numberW) {
            numberW.value = Number(node.value).valueOf();
          } else if (intW) {
            floatW.value = Number(node.value).valueOf();
          }
          break;
        case NodeName.integer:
        case NodeName.sequentialSeedsGenerator:
          if (numberW) {
            numberW.value = Number(node.value).valueOf();
          } else if (intW) {
            intW.value = Number(node.value).valueOf();
          } else if (seedW) {
            seedW.value = Number(node.value).valueOf();
          }
          break;
        case NodeName.samplerSelector:
        case NodeName.schedulerSelector:
        case NodeName.upscaleModelSelector:
        case NodeName.vaeSelector:
          comboW.value = node.value;
          break;
        case NodeName.string:
          if (stringW) {
            stringW.options.setValue(node.value);
          } else if (customtextW) {
            customtextW.options.setValue(node.value);
          } else if (textW) {
            textW.value = node.value;
          }
          break;
      }
    }
  }
  //#endregion
};
var HistoryCSS;
(function(HistoryCSS2) {
  HistoryCSS2["Content"] = "lf-history";
  HistoryCSS2["Widget"] = "lf-history__widget";
})(HistoryCSS || (HistoryCSS = {}));
const STATE$7 = /* @__PURE__ */ new WeakMap();
const historyFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$7.get(wrapper),
      getValue() {
        const { list } = STATE$7.get(wrapper);
        return (list == null ? void 0 : list.lfDataset) || {};
      },
      setValue(value) {
        const { list } = STATE$7.get(wrapper);
        const callback = (_, u) => {
          list.lfDataset = u.parsedJSON || {};
        };
        normalizeValue(value, callback, CustomWidgetName.history);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const list = document.createElement(TagName.LfList);
    list.classList.add(HistoryCSS.Widget);
    list.lfEmpty = "History is empty!";
    list.lfEnableDeletions = true;
    switch (node.comfyClass) {
      case NodeName.loadFileOnce:
        break;
      default:
        list.lfSelectable = true;
        break;
    }
    list.addEventListener(LfEventName.LfList, (e) => EV_HANDLERS$5.list(STATE$7.get(wrapper), e));
    content.classList.add(HistoryCSS.Content);
    content.appendChild(list);
    wrapper.appendChild(content);
    const options = historyFactory.options(wrapper);
    STATE$7.set(wrapper, { list, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.history, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$7
  //#endregion
};
const EV_HANDLERS$4 = {
  //#region Masonry handler
  masonry: (state, e) => {
    var _a, _b;
    const { comp, eventType, originalEvent, selectedShape } = e.detail;
    if (!comp.lfSelectable) {
      return;
    }
    switch (eventType) {
      case "lf-event":
        const { eventType: eventType2 } = originalEvent.detail;
        switch (eventType2) {
          case "click":
            const v = ((_a = selectedShape.shape) == null ? void 0 : _a.value) || ((_b = selectedShape.shape) == null ? void 0 : _b.lfValue);
            state.selected.index = selectedShape.index;
            state.selected.name = v ? String(v).valueOf() : "";
            break;
        }
        break;
    }
  }
  //#endregion
};
var MasonryCSS;
(function(MasonryCSS2) {
  MasonryCSS2["Content"] = "lf-masonry";
  MasonryCSS2["Slot"] = "lf-masonry__slot";
  MasonryCSS2["Widget"] = "lf-masonry__widget";
})(MasonryCSS || (MasonryCSS = {}));
const STATE$6 = /* @__PURE__ */ new WeakMap();
const masonryFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$6.get(wrapper),
      getValue() {
        const { masonry, selected } = STATE$6.get(wrapper);
        const { index, name } = selected;
        return {
          columns: (masonry == null ? void 0 : masonry.lfColumns) || 3,
          dataset: (masonry == null ? void 0 : masonry.lfDataset) || {},
          index: isValidNumber(index) ? index : NaN,
          name: name || "",
          view: (masonry == null ? void 0 : masonry.lfView) || "main"
        };
      },
      setValue(value) {
        const callback = (_, u) => {
          const { masonry, selected } = STATE$6.get(wrapper);
          const { columns, dataset, index, name, view, slot_map } = u.parsedJSON;
          if (columns) {
            masonry.lfColumns = columns;
          }
          if (dataset) {
            masonry.lfDataset = dataset || {};
          }
          if (view) {
            masonry.lfView = view;
          }
          if (isValidNumber(index)) {
            selected.index = index;
            selected.name = name || "";
            masonry.setSelectedShape(index);
          }
          if (slot_map && typeof slot_map === "object" && Object.keys(slot_map).length > 0) {
            while (masonry.firstChild) {
              masonry.removeChild(masonry.firstChild);
            }
            for (const key in slot_map) {
              if (!Object.hasOwn(slot_map, key))
                continue;
              const element = slot_map[key];
              const div = document.createElement("div");
              div.innerHTML = element;
              div.setAttribute("slot", key);
              div.classList.add(MasonryCSS.Slot);
              masonry.appendChild(div);
            }
            masonry.lfShape = "slot";
          }
        };
        normalizeValue(value, callback, CustomWidgetName.masonry);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const masonry = document.createElement(TagName.LfMasonry);
    masonry.classList.add(MasonryCSS.Widget);
    masonry.addEventListener(LfEventName.LfMasonry, (e) => EV_HANDLERS$4.masonry(STATE$6.get(wrapper), e));
    masonry.lfActions = true;
    masonry.lfColumns = 3;
    switch (node.comfyClass) {
      case NodeName.loadImages:
        masonry.lfSelectable = true;
        break;
    }
    content.classList.add(MasonryCSS.Content);
    content.appendChild(masonry);
    wrapper.appendChild(content);
    const options = masonryFactory.options(wrapper);
    STATE$6.set(wrapper, { masonry, node, selected: { index: NaN, name: "" }, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.masonry, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$6
  //#endregion
};
const PLACEHOLDER_MESSAGE = `The setup of this node must be done client-side. Use either <strong>LF_WriteJSON</strong> or <strong>LF_DisplayJSON</strong>
to connect as input a valid JSON dataset. Check the repository's workflows to see a 
<a target="_blank" href="https://github.com/lucafoscili/lucafoscili/blob/7cd0e072cb790ff2e921d6db0b16027d1dea0545/lf-nodes/workflows/Flux%20%2B%20LLM%20Character%20manager.json">working example here.</a>.`;
const EV_HANDLERS$3 = {
  //#region Messenger handler
  messenger: (state, e) => {
    const { eventType, config } = e.detail;
    switch (eventType) {
      case "save":
        if (config && typeof config === "object") {
          state.config = config;
        }
        break;
    }
  }
  //#endregion
};
const STATE$5 = /* @__PURE__ */ new WeakMap();
const messengerFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$5.get(wrapper),
      getValue() {
        const { config, elements } = STATE$5.get(wrapper);
        const { messenger } = elements;
        return {
          dataset: messenger.lfDataset || {},
          config
        };
      },
      setValue(value) {
        const state = STATE$5.get(wrapper);
        const { elements } = state;
        const { messenger, placeholder } = elements;
        const callback = (_, u) => {
          const { config, dataset } = u.parsedJSON;
          messenger.lfDataset = dataset;
          if (isValidObject(config)) {
            messenger.lfValue = config;
            state.config = config;
          }
          placeholder.classList.add(MessengerCSS.PlaceholderHidden);
        };
        const onException = () => {
          placeholder.classList.remove(MessengerCSS.PlaceholderHidden);
        };
        normalizeValue(value, callback, CustomWidgetName.messenger, onException);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const placeholder = document.createElement(TagName.Div);
    const messenger = document.createElement(TagName.LfMessenger);
    content.classList.add(MessengerCSS.Content);
    messenger.classList.add(MessengerCSS.Widget);
    placeholder.classList.add(MessengerCSS.Placeholder);
    placeholder.innerHTML = PLACEHOLDER_MESSAGE;
    messenger.addEventListener(LfEventName.LfMessenger, (e) => EV_HANDLERS$3.messenger(STATE$5.get(wrapper), e));
    content.appendChild(placeholder);
    content.appendChild(messenger);
    wrapper.appendChild(content);
    const options = messengerFactory.options(wrapper);
    STATE$5.set(wrapper, { config: null, elements: { messenger, placeholder }, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.messenger, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$5
  //#endregion
};
var ProgressbarCSS;
(function(ProgressbarCSS2) {
  ProgressbarCSS2["Content"] = "lf-progressbar";
})(ProgressbarCSS || (ProgressbarCSS = {}));
var ProgressbarLabels;
(function(ProgressbarLabels2) {
  ProgressbarLabels2["ArrowRight"] = "→";
  ProgressbarLabels2["ArrowUp"] = "↑";
  ProgressbarLabels2["Fallback"] = "N/A";
  ProgressbarLabels2["False"] = "false";
  ProgressbarLabels2["True"] = "true";
})(ProgressbarLabels || (ProgressbarLabels = {}));
const STATE$4 = /* @__PURE__ */ new WeakMap();
const progressbarFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$4.get(wrapper),
      getValue() {
        const { progressbar } = STATE$4.get(wrapper);
        return {
          bool: progressbar.lfLabel === "true" ? true : false,
          roll: progressbar.lfValue || 0
        };
      },
      setValue(value) {
        const { node, progressbar } = STATE$4.get(wrapper);
        const callback = (_, u) => {
          const { bool, roll } = u.parsedJSON;
          const isFalse = !!(bool === false);
          const isTrue = !!(bool === true);
          switch (node.comfyClass) {
            case NodeName.resolutionSwitcher:
              if (isTrue) {
                progressbar.lfLabel = ProgressbarLabels.ArrowRight;
                progressbar.lfUiState = "primary";
              } else if (isFalse) {
                progressbar.lfLabel = ProgressbarLabels.ArrowUp;
                progressbar.lfUiState = "secondary";
              } else {
                progressbar.lfLabel = ProgressbarLabels.Fallback;
                progressbar.lfUiState = "disabled";
              }
              break;
            default:
              if (isTrue) {
                progressbar.lfLabel = ProgressbarLabels.True;
                progressbar.lfUiState = "success";
              } else if (isFalse) {
                progressbar.lfLabel = ProgressbarLabels.False;
                progressbar.lfUiState = "danger";
              } else {
                progressbar.lfLabel = ProgressbarLabels.Fallback;
                progressbar.lfUiState = "disabled";
              }
              break;
          }
          progressbar.title = roll ? "Actual roll: " + roll.toString() : "";
          progressbar.lfValue = roll || 100;
        };
        normalizeValue(value, callback, CustomWidgetName.progressbar);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const progressbar = document.createElement(TagName.LfProgressbar);
    progressbar.lfIsRadial = true;
    progressbar.lfLabel = ProgressbarLabels.Fallback;
    content.classList.add(ProgressbarCSS.Content);
    content.appendChild(progressbar);
    wrapper.appendChild(content);
    const options = progressbarFactory.options(wrapper);
    STATE$4.set(wrapper, { node, progressbar, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.progressbar, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$4
  //#endregion
};
const EV_HANDLERS$2 = {
  //#region Tabbar handler
  tabbar: (state, e) => {
    const { eventType, node } = e.detail;
    const { elements } = state;
    const { chart } = elements;
    switch (eventType) {
      case "click":
        switch (state.node.comfyClass) {
          case NodeName.usageStatistics:
            chart.lfDataset = getLfManager().getCachedDatasets().usage[node.id];
            break;
          default:
            chart.lfDataset = node.cells.lfChart.lfDataset;
            break;
        }
        break;
    }
  },
  //#endregion
  //#region Textfield handler
  textfield: (state, e) => {
    const { eventType, value } = e.detail;
    switch (eventType) {
      case "change":
        state.directory = value;
        apiCall(state);
        break;
    }
  }
  //#endregion
};
const apiCall = async (state) => {
  const { directory, elements, selected, type } = state;
  const { chart, tabbar, textfield } = elements;
  getApiRoutes().analytics.get(directory, type).then((r) => {
    if (r.status === "success") {
      if ((r == null ? void 0 : r.data) && Object.entries(r.data).length > 0) {
        const firstKey = selected || Object.keys(r.data)[0];
        chart.lfDataset = r.data[firstKey];
        tabbar.lfDataset = prepareTabbarDataset(r.data);
        requestAnimationFrame(async () => {
          if (directory !== await textfield.getValue()) {
            textfield.setValue(directory);
          }
          tabbar.setValue(0);
        });
      } else {
        getLfManager().log("Analytics not found.", { r }, LogSeverity.Info);
      }
    }
  });
};
const prepareTabbarDataset = (data) => {
  var _a;
  const dataset = { nodes: [] };
  for (const filename in data) {
    if (Object.prototype.hasOwnProperty.call(data, filename)) {
      const node = {
        cells: { lfChart: { lfDataset: data[filename], shape: "chart", value: "" } },
        id: filename,
        value: ((_a = filename.split("_")) == null ? void 0 : _a[0]) || filename
      };
      dataset.nodes.push(node);
    }
  }
  return dataset;
};
var TabBarChartCSS;
(function(TabBarChartCSS2) {
  TabBarChartCSS2["Content"] = "lf-tabbarchart";
  TabBarChartCSS2["Directory"] = "lf-tabbarchart__directory";
  TabBarChartCSS2["DirectoryHidden"] = "lf-tabbarchart__directory--hidden";
  TabBarChartCSS2["Grid"] = "lf-tabbarchart__grid";
  TabBarChartCSS2["GridNoDirectory"] = "lf-tabbarchart__grid--no-directory";
  TabBarChartCSS2["Spinner"] = "lf-tabbarchart__spinner";
  TabBarChartCSS2["Tabbar"] = "lf-tabbarchart__tabbar";
})(TabBarChartCSS || (TabBarChartCSS = {}));
var TabBarChartColors;
(function(TabBarChartColors2) {
  TabBarChartColors2["Blue"] = "blue";
  TabBarChartColors2["Green"] = "green";
  TabBarChartColors2["Red"] = "red";
})(TabBarChartColors || (TabBarChartColors = {}));
var TabBarChartIds;
(function(TabBarChartIds2) {
  TabBarChartIds2["Blue"] = "blue";
  TabBarChartIds2["Counter"] = "counter";
  TabBarChartIds2["Green"] = "green";
  TabBarChartIds2["Intensity"] = "intensity";
  TabBarChartIds2["Name"] = "name";
  TabBarChartIds2["Red"] = "red";
})(TabBarChartIds || (TabBarChartIds = {}));
const STATE$3 = /* @__PURE__ */ new WeakMap();
const tabBarChartFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$3.get(wrapper),
      getValue: () => {
        const { directory, node } = STATE$3.get(wrapper);
        switch (node.comfyClass) {
          case NodeName.usageStatistics:
            return { directory: directory || "" };
          default:
            return {};
        }
      },
      setValue: (value) => {
        const state = STATE$3.get(wrapper);
        const { chart, tabbar } = state.elements;
        const callback = (_, u) => {
          const parsedValue = u.parsedJSON;
          switch (state.node.comfyClass) {
            case NodeName.usageStatistics:
              state.directory = parsedValue.directory;
              apiCall(state);
              break;
            default:
              for (const key in parsedValue) {
                const dataset = parsedValue[key];
                chart.lfDataset = dataset || {};
                tabbar.lfDataset = prepareTabbarDataset(parsedValue) || {};
                requestAnimationFrame(async () => tabbar.setValue(0));
              }
              break;
          }
        };
        normalizeValue(value, callback, CustomWidgetName.tabBarChart);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const textfield = document.createElement(TagName.LfTextfield);
    const chart = document.createElement(TagName.LfChart);
    const tabbar = document.createElement(TagName.LfTabbar);
    let type;
    switch (node.comfyClass) {
      case NodeName.colorAnalysis:
        chart.lfAxis = [TabBarChartIds.Intensity];
        chart.lfColors = [TabBarChartColors.Red, TabBarChartColors.Green, TabBarChartColors.Blue];
        chart.lfSeries = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfTypes = ["scatter"];
        grid.classList.add(TabBarChartCSS.GridNoDirectory);
        textfield.classList.add(TabBarChartCSS.DirectoryHidden);
        break;
      case NodeName.imageHistogram:
      case NodeName.lutGeneration:
        chart.lfAxis = [TabBarChartIds.Intensity];
        chart.lfColors = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfSeries = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfTypes = ["area"];
        grid.classList.add(TabBarChartCSS.GridNoDirectory);
        textfield.classList.add(TabBarChartCSS.DirectoryHidden);
        break;
      case NodeName.usageStatistics:
        type = "usage";
        chart.lfAxis = [TabBarChartIds.Name];
        chart.lfSeries = [TabBarChartIds.Counter, TabBarChartIds.Counter];
        chart.lfTypes = ["area"];
        break;
    }
    tabbar.classList.add(TabBarChartCSS.Tabbar);
    tabbar.lfValue = null;
    tabbar.addEventListener(LfEventName.LfTabbar, (e) => EV_HANDLERS$2.tabbar(STATE$3.get(wrapper), e));
    textfield.classList.add(TabBarChartCSS.Directory);
    textfield.lfIcon = "folder";
    textfield.lfLabel = "Directory";
    textfield.lfStyling = "flat";
    textfield.addEventListener(LfEventName.LfTextfield, (e) => EV_HANDLERS$2.textfield(STATE$3.get(wrapper), e));
    grid.classList.add(TabBarChartCSS.Grid);
    grid.appendChild(textfield);
    grid.appendChild(tabbar);
    grid.appendChild(chart);
    content.classList.add(TabBarChartCSS.Content);
    content.appendChild(grid);
    wrapper.appendChild(content);
    const options = tabBarChartFactory.options(wrapper);
    STATE$3.set(wrapper, {
      directory: "",
      elements: { chart, tabbar, textfield },
      node,
      selected: "",
      type,
      wrapper
    });
    return { widget: createDOMWidget(CustomWidgetName.tabBarChart, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$3
  //#endregion
};
var TextareaCSS;
(function(TextareaCSS2) {
  TextareaCSS2["Content"] = "lf-textarea";
  TextareaCSS2["Widget"] = "lf-textarea__widget";
  TextareaCSS2["WidgetError"] = "lf-textarea__widget--error";
})(TextareaCSS || (TextareaCSS = {}));
let VALIDATION_TIMEOUT;
const EV_HANDLERS$1 = {
  //#region Input handler
  input: (e) => {
    const textarea = e.currentTarget;
    const startValidationTimer = () => {
      const validateAndFormatJSON = async () => {
        try {
          const jsonObject = JSON.parse(textarea.value);
          const formattedJson = JSON.stringify(jsonObject, null, 2);
          if (formattedJson !== "{}") {
            textarea.title = "";
            textarea.value = formattedJson;
            textarea.classList.remove(TextareaCSS.WidgetError);
          }
        } catch (error) {
          getLfManager().log("Error parsing JSON", { error }, LogSeverity.Warning);
          textarea.classList.add(TextareaCSS.WidgetError);
          textarea.title = error;
        }
      };
      VALIDATION_TIMEOUT = setTimeout(validateAndFormatJSON, 2500);
    };
    clearTimeout(VALIDATION_TIMEOUT);
    startValidationTimer();
  }
  //#endregion
};
const STATE$2 = /* @__PURE__ */ new WeakMap();
const textareaFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$2.get(wrapper),
      getValue() {
        const { textarea } = STATE$2.get(wrapper);
        try {
          return (textarea == null ? void 0 : textarea.value) || "{}";
        } catch (error) {
          return error;
        }
      },
      setValue(value) {
        const { textarea } = STATE$2.get(wrapper);
        const callback = (_, u) => {
          const parsedJson = u.parsedJSON;
          textarea.value = JSON.stringify(parsedJson, null, 2) || "{}";
        };
        normalizeValue(value, callback, CustomWidgetName.textarea);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const textarea = document.createElement(TagName.Textarea);
    content.classList.add(TextareaCSS.Content);
    content.appendChild(textarea);
    textarea.classList.add(TextareaCSS.Widget);
    textarea.addEventListener("input", EV_HANDLERS$1.input);
    wrapper.appendChild(content);
    const options = textareaFactory.options(wrapper);
    STATE$2.set(wrapper, { node, textarea, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.textarea, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$2
  //#endregion
};
var TreeCSS;
(function(TreeCSS2) {
  TreeCSS2["Content"] = "lf-tree";
  TreeCSS2["Widget"] = "lf-tree__widget";
})(TreeCSS || (TreeCSS = {}));
const STATE$1 = /* @__PURE__ */ new WeakMap();
const treeFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE$1.get(wrapper),
      getValue() {
        const { tree } = STATE$1.get(wrapper);
        return tree.lfDataset || {};
      },
      setValue(value) {
        const { tree } = STATE$1.get(wrapper);
        const callback = (_, u) => {
          tree.lfDataset = u.parsedJSON || {};
        };
        normalizeValue(value, callback, CustomWidgetName.tree);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const tree = document.createElement(TagName.LfTree);
    switch (node.comfyClass) {
      case NodeName.isLandscape:
        tree.lfAccordionLayout = false;
        tree.lfSelectable = false;
        break;
      default:
        tree.lfAccordionLayout = true;
        tree.lfSelectable = false;
        break;
    }
    tree.classList.add(TreeCSS.Widget);
    content.classList.add(TreeCSS.Content);
    content.appendChild(tree);
    wrapper.appendChild(content);
    const options = treeFactory.options(wrapper);
    STATE$1.set(wrapper, { node, tree, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.tree, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$1
  //#endregion
};
const EV_HANDLERS = {
  //#region Upload handler
  upload: async (state, e) => {
    var _a;
    const { eventType, selectedFiles } = e.detail;
    const { upload } = state;
    switch (eventType) {
      case "delete":
        state.files = Array.from(selectedFiles, (file) => file.name).join(";") || "";
        return;
      case "upload":
        const socket = getWidget(state.node, ComfyWidgetName.combo);
        const dir = ((_a = socket.value) == null ? void 0 : _a.toString()) || "temp";
        const { filesStr } = await uploadFiles(selectedFiles, upload, dir);
        state.files = filesStr || "";
        break;
    }
  }
  //#endregion
};
var UploadCSS;
(function(UploadCSS2) {
  UploadCSS2["Content"] = "lf-upload";
  UploadCSS2["Widget"] = "lf-upload__widget";
})(UploadCSS || (UploadCSS = {}));
const STATE = /* @__PURE__ */ new WeakMap();
const uploadFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { files } = STATE.get(wrapper);
        return files || "";
      },
      setValue(value) {
        const state = STATE.get(wrapper);
        const callback = (v) => {
          state.files = v;
        };
        normalizeValue(value, callback, CustomWidgetName.upload);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const upload = document.createElement(TagName.LfUpload);
    upload.classList.add(UploadCSS.Widget);
    upload.addEventListener(LfEventName.LfUpload, (e) => EV_HANDLERS.upload(STATE.get(wrapper), e));
    content.classList.add(UploadCSS.Content);
    content.appendChild(upload);
    wrapper.appendChild(content);
    const options = uploadFactory.options(wrapper);
    STATE.set(wrapper, { files: "", node, upload, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.upload, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE
  //#endregion
};
var __classPrivateFieldGet$1 = function(receiver, state, kind, f) {
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var _LFWidgets_FACTORIES, _LFWidgets_notifications;
class LFWidgets {
  constructor() {
    _LFWidgets_FACTORIES.set(this, {
      [CustomWidgetName.card]: cardFactory,
      [CustomWidgetName.carousel]: carouselFactory,
      [CustomWidgetName.cardsWithChip]: cardsWithChipFactory,
      [CustomWidgetName.chat]: chatFactory,
      [CustomWidgetName.chip]: chipFactory,
      [CustomWidgetName.code]: codeFactory,
      [CustomWidgetName.compare]: compareFactory,
      [CustomWidgetName.controlPanel]: controlPanelFactory,
      [CustomWidgetName.countBarChart]: countBarChartFactory,
      [CustomWidgetName.history]: historyFactory,
      [CustomWidgetName.imageEditor]: imageEditorFactory,
      [CustomWidgetName.masonry]: masonryFactory,
      [CustomWidgetName.messenger]: messengerFactory,
      [CustomWidgetName.progressbar]: progressbarFactory,
      [CustomWidgetName.tabBarChart]: tabBarChartFactory,
      [CustomWidgetName.textarea]: textareaFactory,
      [CustomWidgetName.tree]: treeFactory,
      [CustomWidgetName.upload]: uploadFactory
    });
    this.render = (name) => __classPrivateFieldGet$1(this, _LFWidgets_FACTORIES, "f")[name].render;
    this.decorators = {
      card: (payload, widget) => {
        const { apiFlags, datasets, hashes, paths, chip } = payload;
        cardPlaceholders(widget, 1);
        const value = {
          props: [],
          chip
        };
        const models = [];
        for (let index = 0; index < (datasets == null ? void 0 : datasets.length); index++) {
          const apiFlag = apiFlags[index];
          const dataset = datasets[index];
          const hash = hashes[index];
          const path = paths[index];
          models.push({ dataset, hash, path, apiFlag });
        }
        apiCall$1(models).then((r) => {
          for (let index = 0; index < r.length; index++) {
            const cardProps = r[index];
            if (cardProps.lfDataset) {
              value.props.push(cardProps);
            } else {
              value.props.push({
                ...cardProps,
                lfDataset: models[index].dataset
              });
            }
          }
          widget.options.setValue(JSON.stringify(value));
          getApiRoutes().comfy.redraw();
        });
      }
    };
    this.onEvent = (name, event, widgets) => {
      const lfManager = getLfManager();
      const payload = event.detail;
      const id = resolveNodeId(payload);
      if (!id) {
        lfManager.log(`Event '${name}' missing node identifier; present keys: ${Object.keys(payload).join(", ")}`, { payload, name }, LogSeverity.Warning);
        return;
      }
      const node = lfManager.getApiRoutes().comfy.getNodeById(id);
      if (node) {
        lfManager.log(`${node.comfyClass} (#${node.id}): event '${name}' fired`, { payload, node }, LogSeverity.Info);
        switch (name) {
          case NodeName.notify:
            if ("action" in payload) {
              __classPrivateFieldGet$1(this, _LFWidgets_notifications, "f").show(payload);
            }
            break;
        }
        for (let index = 0; index < widgets.length; index++) {
          const widgetName = widgets[index];
          const widget = getCustomWidget(node, widgetName);
          switch (widgetName) {
            case CustomWidgetName.imageEditor:
              switch (name) {
                case NodeName.imagesEditingBreakpoint:
                  if (widget && "value" in payload) {
                    const { value } = payload;
                    lfManager.log(`Initiating JSON data fetch for editing breakpoint from path: ${value}`, { widget, value });
                    getApiRoutes().json.get(value).then((r) => {
                      if (r.status === LogSeverity.Success) {
                        lfManager.log("JSON data fetched successfully for image editing breakpoint.", { data: r.data }, LogSeverity.Success);
                        widget.options.setValue(JSON.stringify(r.data));
                      } else {
                        lfManager.log(`Failed to fetch JSON data: ${r.message}`, { response: r }, LogSeverity.Error);
                      }
                    }).catch((error) => {
                      lfManager.log(`Error during JSON fetch for editing breakpoint: ${error.toString()}`, { error }, LogSeverity.Error);
                    });
                  } else {
                    lfManager.log(`Image editor widget handling failed: missing 'widget' or 'value' in payload.`, { widget, payload }, LogSeverity.Warning);
                  }
                  break;
                default:
                  if (widget && "dataset" in payload) {
                    const { dataset } = payload;
                    widget.options.setValue(JSON.stringify(dataset));
                  }
                  break;
              }
              break;
            case CustomWidgetName.card:
            case CustomWidgetName.cardsWithChip:
              if (widget && "apiFlags" in payload) {
                this.decorators.card(payload, widget);
              }
              break;
            case CustomWidgetName.code:
            case CustomWidgetName.upload:
              if (widget && "value" in payload) {
                const { value } = payload;
                widget.options.setValue(value);
              }
              break;
            case CustomWidgetName.masonry:
            case CustomWidgetName.progressbar:
              if (widget) {
                widget.options.setValue(JSON.stringify(payload));
              }
              break;
            case CustomWidgetName.countBarChart:
            case CustomWidgetName.tabBarChart:
              if (widget && "datasets" in payload) {
                const { datasets } = payload;
                widget.options.setValue(JSON.stringify(datasets));
              }
              break;
            default:
              if (widget && "dataset" in payload) {
                const { dataset } = payload;
                widget.options.setValue(JSON.stringify(dataset));
              }
              break;
          }
        }
        lfManager.getApiRoutes().comfy.redraw();
      } else {
        lfManager.log(`Event '${name}' was fired but its related node (#${id}) wasn't found in the graph! Skipping handling the event.`, { payload, name }, LogSeverity.Warning);
      }
    };
    _LFWidgets_notifications.set(this, {
      decorate: (payload) => {
        const { action, image, message, silent, tag, title } = payload;
        const icon = action === "focus tab" ? "photo-search" : action === "interrupt" ? "x" : action === "interrupt and queue" ? "refresh" : action === "queue prompt" ? "stack-push" : "";
        const options = {
          body: message,
          icon: icon ? window.location.href + `extensions/lf-nodes/assets/svg/${icon}.svg` : void 0,
          requireInteraction: action === "none" ? false : true,
          silent,
          tag
        };
        if ("image" in Notification.prototype && image) {
          options.image = image;
        }
        if (Notification.permission === "granted") {
          const notification = new Notification(title, options);
          notification.addEventListener("click", () => {
            const lfManager = getLfManager();
            const routes = getApiRoutes().comfy;
            switch (action) {
              case "focus tab":
                window.focus();
                break;
              case "interrupt":
                routes.interrupt();
                break;
              case "interrupt and queue":
                routes.interrupt();
                routes.queuePrompt();
                lfManager.log("New prompt queued from notification after interrupting.", {}, LogSeverity.Success);
                break;
              case "queue prompt":
                routes.queuePrompt();
                lfManager.log("New prompt queued from notification.", {}, LogSeverity.Success);
                break;
            }
          });
        }
      },
      show: (payload) => {
        const lfManager = getLfManager();
        if (Notification.permission !== "granted") {
          Notification.requestPermission().then((permission) => {
            if (permission === "granted") {
              __classPrivateFieldGet$1(this, _LFWidgets_notifications, "f").decorate(payload);
            } else {
              lfManager.log("Notification permission denied.", {}, LogSeverity.Warning);
            }
          });
        } else {
          __classPrivateFieldGet$1(this, _LFWidgets_notifications, "f").decorate(payload);
        }
      }
    });
  }
}
_LFWidgets_FACTORIES = /* @__PURE__ */ new WeakMap(), _LFWidgets_notifications = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldGet = function(receiver, state, kind, f) {
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f : kind === "a" ? f.call(receiver) : f ? f.value : state.get(receiver);
};
var __classPrivateFieldSet = function(receiver, state, value, kind, f) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f.call(receiver, value) : f ? f.value = value : state.set(receiver, value), value;
};
var _LFManager_APIS, _LFManager_AUTOMATIC_BACKUP, _LFManager_BACKUP_RETENTION, _LFManager_CACHED_DATASETS, _LFManager_DEBUG, _LFManager_DEBUG_ARTICLE, _LFManager_DEBUG_DATASET, _LFManager_INITIALIZED, _LFManager_LATEST_RELEASE, _LFManager_MANAGERS, _LFManager_SYSTEM_TIMEOUT;
class LFManager {
  constructor() {
    _LFManager_APIS.set(this, {
      analytics: ANALYTICS_API,
      backup: BACKUP_API,
      comfy: COMFY_API,
      models: MODELS_API,
      github: GITHUB_API,
      image: IMAGE_API,
      json: JSON_API,
      metadata: METADATA_API,
      preview: PREVIEW_API,
      system: SYSTEM_API
    });
    _LFManager_AUTOMATIC_BACKUP.set(this, true);
    _LFManager_BACKUP_RETENTION.set(this, 14);
    _LFManager_CACHED_DATASETS.set(this, {
      usage: null
    });
    _LFManager_DEBUG.set(this, false);
    _LFManager_DEBUG_ARTICLE.set(this, void 0);
    _LFManager_DEBUG_DATASET.set(this, void 0);
    _LFManager_INITIALIZED.set(this, false);
    _LFManager_LATEST_RELEASE.set(this, void 0);
    _LFManager_MANAGERS.set(this, {});
    _LFManager_SYSTEM_TIMEOUT.set(this, 0);
    const assetsUrl = window.location.href + "extensions/lf-nodes/assets";
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework = getLfFramework();
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework.assets.set(assetsUrl);
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework.theme.set("dark");
    this.log("LfFramework ready!", { lfFramework: __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework }, LogSeverity.Success);
    const link = document.createElement("link");
    link.dataset.filename = "_index";
    link.rel = "stylesheet";
    link.type = "text/css";
    link.href = `extensions/lf-nodes/css/_index.css`;
    document.head.appendChild(link);
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").tooltip = new LFTooltip();
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").widgets = new LFWidgets();
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").nodes = new LFNodes();
  }
  //#region Initialize
  initialize() {
    const api = getComfyAPI();
    const app = getComfyAPP();
    installLFBeforeFreeHooks(api, {
      logger: (m, a, s) => this.log(m, a, s)
    });
    installLFRefreshNodeHook(app, {
      logger: (m, a, s) => this.log(m, a, s)
    });
    installLFInterruptHook(api, {
      logger: (m, a, s) => this.log(m, a, s)
    });
    __classPrivateFieldGet(this, _LFManager_APIS, "f").github.getLatestRelease().then((r) => __classPrivateFieldSet(this, _LFManager_LATEST_RELEASE, (r == null ? void 0 : r.data) || null, "f"));
    if (__classPrivateFieldGet(this, _LFManager_INITIALIZED, "f")) {
      this.log("Attempt to initialize LFManager when already ready!", { LFManager: this }, LogSeverity.Warning);
      return;
    }
    for (const key in NodeName) {
      if (Object.prototype.hasOwnProperty.call(NodeName, key)) {
        const name = NodeName[key];
        const eventName = this.getEventName(name);
        const widgets = NODE_WIDGET_MAP[name];
        const customWidgets = {};
        const callbacks = [];
        if (widgets.includes(CustomWidgetName.countBarChart) || widgets.includes(CustomWidgetName.tabBarChart)) {
          callbacks.push(onDrawBackground);
        }
        if (widgets.includes(CustomWidgetName.chip) || widgets.includes(CustomWidgetName.messenger)) {
          callbacks.push(onConnectionsChange);
        }
        callbacks.push(onNodeCreated);
        const extension = {
          name: "LFExt_" + name,
          async beforeRegisterNodeDef(node) {
            if (node.comfyClass === name) {
              callbacks.forEach((c) => c(node));
            }
          },
          getCustomWidgets: () => widgets.reduce((acc, widget) => {
            return {
              ...acc,
              [widget]: __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").widgets.render(widget)
            };
          }, customWidgets)
        };
        __classPrivateFieldGet(this, _LFManager_APIS, "f").comfy.register(extension);
        __classPrivateFieldGet(this, _LFManager_APIS, "f").comfy.event(eventName, (e) => {
          __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").widgets.onEvent(name, e, widgets);
        });
      }
    }
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").nodes.registerAll();
    __classPrivateFieldSet(this, _LFManager_INITIALIZED, true, "f");
  }
  //#endregion
  //#region Getters
  getApiRoutes() {
    return __classPrivateFieldGet(this, _LFManager_APIS, "f");
  }
  getCachedDatasets() {
    return __classPrivateFieldGet(this, _LFManager_CACHED_DATASETS, "f");
  }
  getDebugDataset() {
    return { article: __classPrivateFieldGet(this, _LFManager_DEBUG_ARTICLE, "f"), dataset: __classPrivateFieldGet(this, _LFManager_DEBUG_DATASET, "f") };
  }
  getEventName(node) {
    return node.toLowerCase().replace("_", "-");
  }
  getLatestRelease() {
    return __classPrivateFieldGet(this, _LFManager_LATEST_RELEASE, "f");
  }
  getManagers() {
    return __classPrivateFieldGet(this, _LFManager_MANAGERS, "f");
  }
  getPrefixedNode(nodeName) {
    return `✨ LF Nodes/${nodeName}`;
  }
  getBackupRetention() {
    return __classPrivateFieldGet(this, _LFManager_BACKUP_RETENTION, "f");
  }
  getSystemTimeout() {
    return __classPrivateFieldGet(this, _LFManager_SYSTEM_TIMEOUT, "f");
  }
  isBackupEnabled() {
    return __classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f");
  }
  isDebug() {
    return __classPrivateFieldGet(this, _LFManager_DEBUG, "f");
  }
  //#endregion
  //#region Log
  log(message, args, severity = LogSeverity.Info) {
    var _a;
    if (!__classPrivateFieldGet(this, _LFManager_DEBUG, "f")) {
      return;
    }
    let colorCode = "";
    switch (severity) {
      case "success":
        colorCode = "\x1B[32m";
        break;
      case "warning":
        colorCode = "\x1B[33m";
        break;
      case "error":
        colorCode = "\x1B[31m";
        break;
      default:
        colorCode = "\x1B[0m";
        break;
    }
    const italicCode = "\x1B[3m";
    const boldCode = "\x1B[1m";
    const resetColorCode = "\x1B[0m";
    const dot = "• LF Nodes •";
    if (__classPrivateFieldGet(this, _LFManager_DEBUG_DATASET, "f") && ((_a = __classPrivateFieldGet(this, _LFManager_DEBUG_ARTICLE, "f")) == null ? void 0 : _a.isConnected) && severity !== LogSeverity.Info) {
      const id = String(performance.now()).valueOf();
      const icon = severity === LogSeverity.Error ? "🔴 " : severity === LogSeverity.Success ? "🟢 " : severity === LogSeverity.Warning ? "🟠 " : "🔵 ";
      __classPrivateFieldGet(this, _LFManager_DEBUG_DATASET, "f").unshift({
        cssStyle: getLogStyle(),
        id,
        tagName: "pre",
        value: icon + message
      });
      __classPrivateFieldGet(this, _LFManager_DEBUG_ARTICLE, "f").refresh();
    }
    console.log(`${colorCode}${boldCode}${dot}${resetColorCode}${italicCode} ${message} ${resetColorCode}`, args);
  }
  //#endregion
  //#region Setters
  setBackupRetention(value) {
    if (typeof value === "number" && value >= 0) {
      __classPrivateFieldSet(this, _LFManager_BACKUP_RETENTION, Math.floor(value), "f");
      this.log(`Backup retention set to: ${__classPrivateFieldGet(this, _LFManager_BACKUP_RETENTION, "f")}`, { value }, LogSeverity.Info);
    }
    return __classPrivateFieldGet(this, _LFManager_BACKUP_RETENTION, "f");
  }
  setDebugDataset(article, dataset) {
    __classPrivateFieldSet(this, _LFManager_DEBUG_ARTICLE, article, "f");
    __classPrivateFieldSet(this, _LFManager_DEBUG_DATASET, dataset, "f");
    this.log("Debug dataset set!", { article, dataset }, LogSeverity.Info);
  }
  setSystemTimeout(value = 0) {
    if (typeof value === "number" && value >= 0) {
      __classPrivateFieldSet(this, _LFManager_SYSTEM_TIMEOUT, Math.floor(value), "f");
      this.log(`System timeout set to: ${value}`, { value }, LogSeverity.Info);
    }
  }
  toggleBackup(value) {
    if (value === false || value === true) {
      __classPrivateFieldSet(this, _LFManager_AUTOMATIC_BACKUP, value, "f");
    } else {
      __classPrivateFieldSet(this, _LFManager_AUTOMATIC_BACKUP, !__classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f"), "f");
    }
    this.log(`Automatic backup active: '${__classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f")}'`, { value }, LogSeverity.Warning);
    return __classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f");
  }
  toggleDebug(value) {
    if (value === false || value === true) {
      __classPrivateFieldSet(this, _LFManager_DEBUG, value, "f");
    } else {
      __classPrivateFieldSet(this, _LFManager_DEBUG, !__classPrivateFieldGet(this, _LFManager_DEBUG, "f"), "f");
    }
    this.log(`Debug active: '${__classPrivateFieldGet(this, _LFManager_DEBUG, "f")}'`, { value }, LogSeverity.Warning);
    return __classPrivateFieldGet(this, _LFManager_DEBUG, "f");
  }
}
_LFManager_APIS = /* @__PURE__ */ new WeakMap(), _LFManager_AUTOMATIC_BACKUP = /* @__PURE__ */ new WeakMap(), _LFManager_BACKUP_RETENTION = /* @__PURE__ */ new WeakMap(), _LFManager_CACHED_DATASETS = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG_ARTICLE = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG_DATASET = /* @__PURE__ */ new WeakMap(), _LFManager_INITIALIZED = /* @__PURE__ */ new WeakMap(), _LFManager_LATEST_RELEASE = /* @__PURE__ */ new WeakMap(), _LFManager_MANAGERS = /* @__PURE__ */ new WeakMap(), _LFManager_SYSTEM_TIMEOUT = /* @__PURE__ */ new WeakMap();
var LFFreeFlags;
(function(LFFreeFlags2) {
  LFFreeFlags2["PatchedFree"] = "_lf_patched_freeMemory";
  LFFreeFlags2["OriginalFreeRef"] = "_lf_original_freeMemory";
  LFFreeFlags2["PatchedFetch"] = "_lf_patched_fetchApi_free";
  LFFreeFlags2["InBeforeFree"] = "_lf_in_beforeFree";
})(LFFreeFlags || (LFFreeFlags = {}));
var LFInterruptFlags;
(function(LFInterruptFlags2) {
  LFInterruptFlags2["PatchedInterrupt"] = "_lf_patched_interrupt";
  LFInterruptFlags2["OriginalInterruptRef"] = "_lf_original_interrupt";
  LFInterruptFlags2["InBeforeInterrupt"] = "_lf_in_beforeInterrupt";
})(LFInterruptFlags || (LFInterruptFlags = {}));
var LFRefreshFlags;
(function(LFRefreshFlags2) {
  LFRefreshFlags2["PatchedRefresh"] = "_lf_patched_refreshComboInNodes";
  LFRefreshFlags2["OriginalRefreshRef"] = "_lf_original_refreshComboInNodes";
  LFRefreshFlags2["InBeforeRefresh"] = "_lf_in_beforeRefreshComboInNodes";
})(LFRefreshFlags || (LFRefreshFlags = {}));
const LF_MANAGER_SYMBOL_ID = "__LfManager__";
const LF_MANAGER_SYMBOL = Symbol.for(LF_MANAGER_SYMBOL_ID);
const DEFAULT_WIDGET_NAME = "ui_widget";
let timer;
const isButton = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-button";
};
const isImage = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-image";
};
const isMasonry = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-masonry";
};
const isTextfield = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-textfield";
};
const isTree = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-tree";
};
const isToggle = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-toggle";
};
const getApiRoutes = () => {
  return getLfManager().getApiRoutes();
};
const getComfyAPI = () => {
  return comfyAPI["api"].api;
};
const getComfyAPP = () => {
  return comfyAPI["app"].app;
};
const getLfData = () => {
  var _a;
  return (_a = getLfManager().getManagers().lfFramework) == null ? void 0 : _a.data;
};
const getLfManager = () => {
  return window[LF_MANAGER_SYMBOL];
};
const getLfThemes = () => {
  return getLfManager().getManagers().lfFramework.theme.get.themes().asDataset;
};
const initLfManager = () => {
  if (!window[LF_MANAGER_SYMBOL]) {
    window[LF_MANAGER_SYMBOL] = new LFManager();
  }
};
function isFreeHookAPI(obj) {
  if (!obj || typeof obj !== "object")
    return false;
  const o = obj;
  return typeof o["freeMemory"] === "function" || typeof o["fetchApi"] === "function" || LFFreeFlags.PatchedFree in o || LFFreeFlags.PatchedFetch in o;
}
function isRefreshHookApp(obj) {
  if (!obj || typeof obj !== "object")
    return false;
  const o = obj;
  return typeof o["refreshComboInNodes"] === "function" || "refreshComboInNodes" in o || LFRefreshFlags.PatchedRefresh in o;
}
function isInterruptHookAPI(obj) {
  if (!obj || typeof obj !== "object")
    return false;
  const o = obj;
  return typeof o["interrupt"] === "function" || "interrupt" in o || LFInterruptFlags.PatchedInterrupt in o;
}
const getInput = (node, type) => {
  var _a;
  return (_a = node == null ? void 0 : node.inputs) == null ? void 0 : _a.find((w) => w.type.toLowerCase() === type.toLowerCase());
};
const resolveNodeId = (p) => {
  if (!p) {
    return null;
  }
  return p.node ?? p.id ?? p.node_id ?? null;
};
const clampPercent = (value) => {
  if (typeof value !== "number" || Number.isNaN(value) || !Number.isFinite(value)) {
    return 0;
  }
  return Math.min(100, Math.max(0, value));
};
const isValidNumber = (n) => {
  return !isNaN(n) && typeof n === "number";
};
const toNumber = (value) => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  return 0;
};
const asString = (value) => typeof value === "string" ? value : void 0;
const formatBytes = (bytes) => {
  if (!bytes) {
    return "0 B";
  }
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / Math.pow(1024, index);
  return `${value.toFixed(2)} ${units[index]}`;
};
const isString = (value) => typeof value === "string";
const normalizeDirectoryRequest = (value) => typeof value === "string" ? value : "";
const percentLabel = (value) => `${clampPercent(value).toFixed(1)}%`;
const canvasToBase64 = (canvas) => {
  return canvas.toDataURL("image/png");
};
const createDOMWidget = (type, element, node, options) => {
  getLfManager().log(`Creating '${type}'`, { element });
  try {
    const { nodeData } = Object.getPrototypeOf(node).constructor;
    let name = DEFAULT_WIDGET_NAME;
    for (const key in nodeData.input) {
      if (Object.prototype.hasOwnProperty.call(nodeData.input, key)) {
        const input = nodeData.input[key];
        for (const key2 in input) {
          if (Object.prototype.hasOwnProperty.call(input, key2)) {
            const element2 = Array.from(input[key2]);
            if (element2[0] === type) {
              name = key2;
              break;
            }
          }
        }
        if (name) {
          break;
        }
      }
    }
    return node.addDOMWidget(name, type, element, options);
  } catch (error) {
    getLfManager().log(`Couldn't find a widget of type ${type}`, { error, node }, LogSeverity.Warning);
    return node.addDOMWidget(DEFAULT_WIDGET_NAME, type, element, options);
  }
};
const debounce = (func, delay) => {
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => func(...args), delay);
  };
};
const findWidget = (node, type) => {
  var _a;
  return (_a = node == null ? void 0 : node.widgets) == null ? void 0 : _a.find((w) => w.type === type);
};
const getCustomWidget = (node, type) => {
  var _a;
  return (_a = node == null ? void 0 : node.widgets) == null ? void 0 : _a.find((w) => w.type.toLowerCase() === type.toLowerCase());
};
const getWidget = (node, type) => {
  var _a;
  return (_a = node == null ? void 0 : node.widgets) == null ? void 0 : _a.find((w) => w.type.toLowerCase() === type.toLowerCase());
};
const isValidObject = (obj) => {
  return obj && typeof obj === "object" && Object.keys(obj).length > 0;
};
const normalizeValue = (value, callback, widget, onException) => {
  const { syntax } = getLfManager().getManagers().lfFramework;
  try {
    callback(value, syntax.json.unescape(value));
  } catch (error) {
    if (onException) {
      onException();
    }
    getLfManager().log(`Normalization error!`, { error, widget }, LogSeverity.Error);
  }
};
const refreshChart = (node) => {
  var _a, _b;
  try {
    const domWidget = ((_a = findWidget(node, CustomWidgetName.countBarChart)) == null ? void 0 : _a.element) || ((_b = findWidget(node, CustomWidgetName.tabBarChart)) == null ? void 0 : _b.element);
    if (domWidget) {
      const chart = domWidget.querySelector("lf-chart");
      if (chart) {
        const canvas = chart.shadowRoot.querySelector("canvas");
        const isSmaller = (canvas == null ? void 0 : canvas.clientWidth) < chart.clientWidth || (canvas == null ? void 0 : canvas.clientHeight) < chart.clientHeight;
        const isBigger = (canvas == null ? void 0 : canvas.clientWidth) > chart.clientWidth || (canvas == null ? void 0 : canvas.clientHeight) > chart.clientHeight;
        if (isSmaller || isBigger) {
          chart.refresh();
        }
      }
    }
  } catch (error) {
    getLfManager().log("Whoops! It seems there is no chart. :V", { error }, LogSeverity.Error);
  }
};
const uploadFiles = async (files, uploadEl, dir = "temp") => {
  var _a;
  const fileNames = /* @__PURE__ */ new Set();
  for (let index = 0; index < files.length; index++) {
    const file = files[index];
    try {
      const new_file = new File([file], file.name, {
        type: file.type,
        lastModified: file.lastModified
      });
      const resp = await getApiRoutes().image.upload(new_file, dir);
      if (resp && resp.status === "success" && Array.isArray((_a = resp.payload) == null ? void 0 : _a.paths) && resp.payload.paths.length > 0) {
        getLfManager().log("Upload result", { paths: resp.payload.paths }, LogSeverity.Success);
        fileNames.add(file.name);
        uploadEl.dataset.files = uploadEl.dataset.files + ";" + file.name;
      } else {
        const detail = resp.message || "upload_failed";
        getLfManager().log("POST failed", { detail }, LogSeverity.Error);
      }
    } catch (error) {
      alert(`Upload failed: ${error}`);
    }
  }
  return { files: Array.from(fileNames), filesStr: Array.from(fileNames).join(";") };
};
{
  console.log("LF modules loaded!");
}
getLfFramework();
{
  console.log("LF Framework initialized!");
}
const hasComfyApp = (comfyAPI == null ? void 0 : comfyAPI.api) && (comfyAPI == null ? void 0 : comfyAPI.app);
if (hasComfyApp) {
  initLfManager();
  const lfManager = getLfManager();
  lfManager.initialize();
  {
    console.log("LF Manager initialized!", lfManager);
  }
} else {
  {
    console.log("No Comfy app detected.");
  }
}
//# sourceMappingURL=lf-nodes.js.map
