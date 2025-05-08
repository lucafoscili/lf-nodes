import { N, C as CY_ATTRIBUTES } from "./index-CLXmI-OO.js";
const f = ({ framework: e, shape: f2, index: a, cell: n, eventDispatcher: o, defaultCb: c, refCallback: L }) => {
  const { data: s, sanitizeProps: l } = e, { stringify: d } = s.cell, i = (e2) => {
    c && c(e2), o(e2);
  };
  switch (f2) {
    case "badge":
      return N("lf-badge", { ...l(r("LfBadge", f2, n, a), "LfBadge"), "onLf-badge-event": i, ref: L });
    case "button":
      return N("lf-button", { ...l(r("LfButton", f2, n, a), "LfButton"), "onLf-button-event": i, ref: L });
    case "canvas":
      return N("lf-canvas", { ...l(r("LfCanvas", f2, n, a), "LfCanvas"), "onLf-canvas-event": i, ref: L });
    case "card":
      return N("lf-card", { ...l(r("LfCard", f2, n, a), "LfCard"), "onLf-card-event": i, ref: L });
    case "chart":
      return N("lf-chart", { ...l(r("LfChart", f2, n, a), "LfChart"), "onLf-chart-event": i, ref: L });
    case "chat":
      return N("lf-chat", { ...l(r("LfChat", f2, n, a), "LfChat"), "onLf-chat-event": i, ref: L });
    case "chip":
      return N("lf-chip", { ...l(r("LfChip", f2, n, a), "LfChip"), "onLf-chip-event": i, ref: L });
    case "code":
      return N("lf-code", { ...l(r("LfCode", f2, n, a), "LfCode"), "onLf-code-event": i, ref: L });
    case "image":
      return N("lf-image", { ...l(r("LfImage", f2, n, a), "LfImage"), "onLf-image-event": i, ref: L });
    case "photoframe":
      return N("lf-photoframe", { ...l(r("LfPhotoframe", f2, n, a), "LfPhotoframe"), "onLf-photoframe-event": i, ref: L });
    case "toggle":
      return N("lf-toggle", { ...l(r("LfToggle", f2, n, a), "LfToggle"), "onLf-toggle-event": i, ref: L });
    case "typewriter":
      return N("lf-typewriter", { ...l(r("LfTypewriter", f2, n, a), "LfTypewriter"), "onLf-typewriter-event": i, ref: L });
    case "upload":
      return N("lf-upload", { ...l(r("LfUpload", f2, n, a), "LfUpload"), "onLf-upload-event": i, ref: L });
  }
  return "slot" === f2 ? N("slot", { key: `${f2}${a}`, name: d(n.value), ...l(r(null, f2, n, a)) }) : N("div", { id: `${f2}${a}`, key: `${f2}${a}`, ...l(r(null, f2, n, a)) }, n.value);
}, r = (t, f2, r2, a) => {
  var _a;
  const n = {};
  if (r2.htmlProps) for (const e in r2.htmlProps) {
    const t2 = r2.htmlProps[e];
    if ("dataset" === e) for (const e2 in t2) n[`data-${e2}`] = t2[e2];
  }
  for (const e in r2) n[e] = r2[e];
  const o = ((_a = n == null ? void 0 : n.htmlProps) == null ? void 0 : _a.id) || `${f2}${a}`;
  return n.value && !n.lfValue && (n.lfValue = n.value), delete n.htmlProps, delete n.shape, delete n.value, { "data-component": t || f2, "data-cy": CY_ATTRIBUTES.shape, "data-index": a, id: o, key: `${f2}${a}`, ...n };
};
export {
  f
};
