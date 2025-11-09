import { g as getLfFramework } from "../../js/lf-widgets-framework-DcaHVr-f.js";
import "../../js/lf-widgets-foundations-Bbv1isuU.js";
(function initLoginBootstrap() {
  const hasComfyApp = typeof comfyAPI !== "undefined" && (comfyAPI == null ? void 0 : comfyAPI.api) && (comfyAPI == null ? void 0 : comfyAPI.app);
  if (hasComfyApp) {
    return null;
  }
  const framework = getLfFramework();
  framework.theme.set("dark");
  return;
})();
//# sourceMappingURL=bootstrap-login.js.map
