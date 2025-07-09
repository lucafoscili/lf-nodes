import { bp as onFrameworkReady, bq as S, br as g } from "./index-B7yCDN23.js";
onFrameworkReady.then((t) => {
  t.register("lf-core", { getAssetPath: g, setAssetPath: S });
});
const o = async (s) => {
  const a = await onFrameworkReady;
  return s.debugInfo = a.debug.info.create(), a.theme.register(void 0), a;
};
export {
  o
};
