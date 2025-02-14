import { bp as onFrameworkReady, bq as k, br as j } from "./index-DlhbnacL.js";
onFrameworkReady.then((t) => {
  t.register("lf-core", { getAssetPath: j, setAssetPath: k });
});
const o = async (s) => {
  const a = await onFrameworkReady;
  return s.debugInfo = a.debug.info.create(), a.theme.register(void 0), a;
};
export {
  o
};
