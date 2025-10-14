import { D, C as CY_ATTRIBUTES } from "./index-KdsGGJBN.js";
const r = ({ framework: e, shape: r2, index: a, cell: n, eventDispatcher: o, defaultCb: s, refCallback: c }) => {
  const { data: L, sanitizeProps: l } = e, { stringify: d } = L.cell, i = (e2) => {
    s && s(e2), o(e2);
  };
  switch (r2) {
    case "badge":
      return D("lf-badge", { ...l(f("LfBadge", r2, n, a), "LfBadge"), "onLf-badge-event": i, ref: c });
    case "button":
      return D("lf-button", { ...l(f("LfButton", r2, n, a), "LfButton"), "onLf-button-event": i, ref: c });
    case "canvas":
      return D("lf-canvas", { ...l(f("LfCanvas", r2, n, a), "LfCanvas"), "onLf-canvas-event": i, ref: c });
    case "card":
      return D("lf-card", { ...l(f("LfCard", r2, n, a), "LfCard"), "onLf-card-event": i, ref: c });
    case "chart":
      return D("lf-chart", { ...l(f("LfChart", r2, n, a), "LfChart"), "onLf-chart-event": i, ref: c });
    case "chat":
      return D("lf-chat", { ...l(f("LfChat", r2, n, a), "LfChat"), "onLf-chat-event": i, ref: c });
    case "chip":
      return D("lf-chip", { ...l(f("LfChip", r2, n, a), "LfChip"), "onLf-chip-event": i, ref: c });
    case "code":
      return D("lf-code", { ...l(f("LfCode", r2, n, a), "LfCode"), "onLf-code-event": i, ref: c });
    case "image":
      return D("lf-image", { ...l(f("LfImage", r2, n, a), "LfImage"), "onLf-image-event": i, ref: c });
    case "photoframe":
      return D("lf-photoframe", { ...l(f("LfPhotoframe", r2, n, a), "LfPhotoframe"), "onLf-photoframe-event": i, ref: c });
    case "progressbar":
      return D("lf-progressbar", { ...l(f("LfProgressbar", r2, n, a), "LfProgressbar"), "onLf-progressbar-event": i, ref: c });
    case "textfield":
      return D("lf-textfield", { ...l(f("LfTextfield", r2, n, a), "LfTextfield"), "onLf-textfield-event": i, ref: c });
    case "toggle":
      return D("lf-toggle", { ...l(f("LfToggle", r2, n, a), "LfToggle"), "onLf-toggle-event": i, ref: c });
    case "typewriter":
      return D("lf-typewriter", { ...l(f("LfTypewriter", r2, n, a), "LfTypewriter"), "onLf-typewriter-event": i, ref: c });
    case "upload":
      return D("lf-upload", { ...l(f("LfUpload", r2, n, a), "LfUpload"), "onLf-upload-event": i, ref: c });
  }
  return "slot" === r2 ? D("slot", { key: `${r2}${a}`, name: d(n.value), ...l(f(null, r2, n, a)) }) : D("div", { id: `${r2}${a}`, key: `${r2}${a}`, ...l(f(null, r2, n, a)) }, n.value);
}, f = (t, r2, f2, a) => {
  var _a;
  const n = {};
  if (f2.htmlProps) for (const e in f2.htmlProps) {
    const t2 = f2.htmlProps[e];
    if ("dataset" === e) for (const e2 in t2) n[`data-${e2}`] = t2[e2];
  }
  for (const e in f2) n[e] = f2[e];
  const o = ((_a = n == null ? void 0 : n.htmlProps) == null ? void 0 : _a.id) || `${r2}${a}`;
  return n.value && !n.lfValue && (n.lfValue = n.value), delete n.htmlProps, delete n.shape, delete n.value, { "data-component": t || r2, "data-cy": CY_ATTRIBUTES.shape, "data-index": a, id: o, key: `${r2}${a}`, ...n };
};
export {
  r
};
