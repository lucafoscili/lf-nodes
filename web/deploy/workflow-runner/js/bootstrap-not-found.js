import { g as getLfFramework } from "../../js/lf-widgets-framework-C98FQqUU.js";
import "../../js/lf-widgets-foundations-LHw4zrea.js";
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
