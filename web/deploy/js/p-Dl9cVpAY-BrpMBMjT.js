import { bq as onFrameworkReady } from "./index-CkCoJ671.js";
const getGlobalScope = () => {
  if (typeof globalThis === "undefined") {
    return void 0;
  }
  return globalThis;
};
const getStencilHelper = (key) => {
  const globalScope = getGlobalScope();
  const candidates = [
    globalScope == null ? void 0 : globalScope.StencilCore,
    globalScope == null ? void 0 : globalScope.app,
    globalScope == null ? void 0 : globalScope.App,
    globalScope == null ? void 0 : globalScope.lfWidgets,
    globalScope
  ];
  for (const candidate of candidates) {
    const helper = candidate == null ? void 0 : candidate[key];
    if (typeof helper === "function") {
      return helper.bind(candidate);
    }
  }
  if (typeof window === "undefined") {
    try {
      const stencil = require("@stencil/core");
      const helper = stencil == null ? void 0 : stencil[key];
      if (typeof helper === "function") {
        return helper;
      }
    } catch {
    }
  }
  return void 0;
};
const getAssetPathProxy = (path) => {
  const helper = getStencilHelper("getAssetPath");
  if (helper) {
    try {
      const result = helper(path);
      if (typeof result === "string" && result.length > 0) {
        return result;
      }
    } catch {
    }
  }
  return path;
};
const setAssetPathProxy = (path) => {
  const helper = getStencilHelper("setAssetPath");
  if (helper) {
    try {
      helper(path);
    } catch {
    }
  }
};
const registerStencilAssetProxies = (module) => {
  onFrameworkReady.then((framework) => {
    framework.register(module, {
      getAssetPath: getAssetPathProxy,
      setAssetPath: setAssetPathProxy
    });
  }).catch(() => {
  });
};
registerStencilAssetProxies("lf-core");
const a = async (o) => {
  const a2 = await onFrameworkReady;
  return o.debugInfo = a2.debug.info.create(), a2.theme.register(o), a2;
};
export {
  a
};
