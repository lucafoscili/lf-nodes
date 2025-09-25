import { bq as onFrameworkReady, br as j, bs as S } from "./index-BoZzaTEw.js";
onFrameworkReady.then(((t) => {
  t.register("lf-core", { getAssetPath: S, setAssetPath: j });
}));
const o = async (s) => {
  const a = await onFrameworkReady;
  return s.debugInfo = a.debug.info.create(), a.theme.register(void 0), a;
};
export {
  o
};
