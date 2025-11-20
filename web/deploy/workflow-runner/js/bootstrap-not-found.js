import { g as getLfFramework } from "../../js/lf-widgets-framework-qjsxfoUK.js";
import "../../js/lf-widgets-foundations-8UtpQZAe.js";
(function initNotFoundBootstrap() {
  const hasComfyApp = typeof comfyAPI !== "undefined" && (comfyAPI == null ? void 0 : comfyAPI.api) && (comfyAPI == null ? void 0 : comfyAPI.app);
  if (hasComfyApp) {
    return null;
  }
  const framework = getLfFramework();
  framework.theme.set("dark");
  return;
})();
//# sourceMappingURL=bootstrap-not-found.js.map
