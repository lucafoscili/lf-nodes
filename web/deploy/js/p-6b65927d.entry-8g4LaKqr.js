import { o, V as V$1, b4 as LF_MASONRY_DEFAULT_COLUMNS, b5 as LF_MASONRY_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, b6 as LF_MASONRY_PARTS, c as LF_STYLE_ID, b7 as LF_MASONRY_CSS_VARS, d as LF_WRAPPER_ID, U as U$1, k as kt, b8 as LF_MASONRY_PROPS, m as mt, A as A$1, T as T$1, b9 as LF_MASONRY_IDS } from "./index-BPYlQam6.js";
import { o as o$1 } from "./p-c236cf18-C0p0BmJn.js";
import { f } from "./p-d7fe17a6-BY4mw-ed.js";
const v = (t) => Number(t.rootElement.style.getPropertyValue(LF_MASONRY_CSS_VARS.columns)), w = (t, e) => Number(t.rootElement.style.setProperty(LF_MASONRY_CSS_VARS.columns, String(e))), k = (e) => /* @__PURE__ */ ((e2) => ({ addColumn: () => {
  const { controller: s, elements: i, handlers: a } = e2(), { refs: n } = i, { button: r } = a, { blocks: l, cyAttributes: f2, lfAttributes: h, manager: c, parts: d } = s.get, { assignRef: m, theme: u } = c, { bemClass: p, get: g } = u, { "--lf-icon-plus": y } = g.current().variables;
  return U$1("lf-button", { class: p(l.grid._, l.grid.addColumn), "data-cy": f2.button, "data-lf": h.fadeIn, id: LF_MASONRY_IDS.addColumn, key: LF_MASONRY_IDS.addColumn, lfIcon: y, lfStyling: "floating", lfUiSize: "xxsmall", "onLf-button-event": r, part: d.addColumn, ref: m(n, "addColumn"), title: "Click to add a column to the masonry." });
}, removeColumn: () => {
  const { controller: s, elements: i, handlers: a } = e2(), { refs: n } = i, { button: r } = a, { blocks: l, cyAttributes: f2, lfAttributes: h, manager: c, parts: d } = s.get, { assignRef: m, theme: u } = c, { bemClass: p, get: g } = u, { "--lf-icon-minus": y } = g.current().variables;
  return U$1("lf-button", { class: p(l.grid._, l.grid.removeColumn), "data-cy": f2.button, "data-lf": h.fadeIn, id: LF_MASONRY_IDS.removeColumn, key: LF_MASONRY_IDS.removeColumn, lfIcon: y, lfStyling: "floating", lfUiSize: "xxsmall", "onLf-button-event": r, part: d.removeColumn, ref: m(n, "removeColumn"), title: "Click to remove a column from the masonry." });
}, changeView: () => {
  const { controller: s, elements: i, handlers: a } = e2(), { refs: n } = i, { blocks: r, cyAttributes: l, isMasonry: f2, isVertical: h, manager: c, parts: d } = s.get, { button: m } = a, { assignRef: u, theme: p } = c, { bemClass: g, get: y } = p, { layoutBoardSplit: b, viewportTall: v2, viewportWide: w2 } = y.icons();
  return U$1("lf-button", { class: g(r.grid._, r.grid.changeViewe), "data-cy": l.button, id: LF_MASONRY_IDS.masonry, key: LF_MASONRY_IDS.masonry, lfIcon: f2() ? v2 : h() ? w2 : b, lfStyling: "floating", lfUiSize: "xsmall", "onLf-button-event": m, part: d.changeView, ref: u(n, "changeView"), title: f2() ? "Click to view the images arranged vertically." : h() ? "Click to view the images arranged horizontally." : "Click to view the images arranged in a masonry." });
} }))(e), z = (t) => /* @__PURE__ */ ((t2) => ({ button: (e) => {
  const { eventType: s, id: i } = e.detail;
  if ("click" === s) switch (i) {
    case LF_MASONRY_IDS.masonry:
      (async (t3) => {
        const { compInstance: e2, isMasonry: s2, isVertical: i2 } = t3.controller.get;
        e2.lfView = s2() ? "vertical" : i2() ? "horizontal" : "main";
      })(t2());
      break;
    case LF_MASONRY_IDS.removeColumn:
      (async (t3) => {
        const { compInstance: e2, currentColumns: s2 } = t3.controller.get, i2 = e2, a = v(i2) || s2();
        a > 1 && w(i2, a - 1);
      })(t2());
      break;
    case LF_MASONRY_IDS.addColumn:
      (async (t3) => {
        const { compInstance: e2, currentColumns: s2 } = t3.controller.get, i2 = e2, a = v(i2) || s2();
        w(i2, a + 1);
      })(t2());
  }
} }))(t);
var x, C, S, M, W, _, A, T, E, I, j, L, V, P, D, R, U, N, O, B, F, H, $, q, G = function(t, e, s, i) {
  if ("a" === s && !i) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof e ? t !== e || !i : !e.has(t)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === s ? i : "a" === s ? i.call(t) : i ? i.value : e.get(t);
}, J = function(t, e, s, i, a) {
  if ("function" == typeof e ? t !== e || true : !e.has(t)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return e.set(t, s), s;
};
const K = class {
  constructor(a) {
    o(this, a), this.lfEvent = V$1(this, "lf-masonry-event"), x.add(this), this.selectedShape = {}, this.shapes = {}, this.lfActions = false, this.lfColumns = Array.from(LF_MASONRY_DEFAULT_COLUMNS), this.lfDataset = null, this.lfSelectable = false, this.lfShape = "image", this.lfStyle = "", this.lfView = "main", C.set(this, void 0), S.set(this, LF_MASONRY_BLOCKS), M.set(this, CY_ATTRIBUTES), W.set(this, LF_ATTRIBUTES), _.set(this, LF_MASONRY_PARTS), A.set(this, LF_STYLE_ID), T.set(this, LF_MASONRY_CSS_VARS), E.set(this, LF_WRAPPER_ID), I.set(this, void 0), j.set(this, void 0), L.set(this, void 0), V.set(this, () => {
      var t;
      J(this, L, { controller: { get: { blocks: G(this, S, "f"), compInstance: this, currentColumns: () => G(this, I, "f"), cyAttributes: G(this, M, "f"), isMasonry: () => G(this, D, "f").call(this), isVertical: () => G(this, R, "f").call(this), lfAttributes: G(this, W, "f"), manager: G(this, C, "f"), parts: G(this, _, "f"), shapes: () => this.shapes } }, elements: { jsx: k(t = () => G(this, L, "f")), refs: { addColumn: null, removeColumn: null, changeView: null } }, handlers: z(t) });
    }), P.set(this, () => {
      var _a;
      return !!((_a = this.shapes) == null ? void 0 : _a[this.lfShape]);
    }), D.set(this, () => "main" === this.lfView), R.set(this, () => "vertical" === this.lfView), U.set(this, (t, e) => () => {
      clearTimeout(G(this, j, "f")), J(this, j, setTimeout(t, e));
    }), N.set(this, (t) => t.every((t2, e, s) => 0 === e || s[e - 1] < t2)), B.set(this, () => {
      const { lfShape: e, selectedShape: s, shapes: i } = this, a2 = i[this.lfShape].map(() => ({ htmlProps: { dataset: { lf: G(this, W, "f").fadeIn, selected: "" } } }));
      void 0 !== s.index && (a2[s.index] = { htmlProps: { dataset: { lf: G(this, W, "f").fadeIn, selected: "true" } } });
      const n = Array.from({ length: G(this, I, "f") }, () => [], []);
      for (let s2 = 0; s2 < i[e].length; s2++) {
        const r = i[e][s2], o2 = a2[s2];
        n[s2 % G(this, I, "f")].push(U$1(f, { cell: Object.assign(o2, r), index: s2, shape: e, eventDispatcher: async (t) => this.onLfEvent(t, "lf-event"), framework: G(this, C, "f") }));
      }
      return n;
    }), F.set(this, G(this, U, "f").call(this, () => {
      this.viewportWidth = window.innerWidth;
    }, 200)), H.set(this, () => {
      const { bemClass: e } = G(this, C, "f").theme, { grid: s } = G(this, S, "f"), { addColumn: i, changeView: a2, removeColumn: n } = G(this, L, "f").elements.jsx;
      return U$1("div", { class: e(s._, s.actions), "data-lf": G(this, W, "f").fadeIn }, G(this, D, "f").call(this) && U$1("div", { class: e(s._, s.sub) }, i(), n()), a2());
    }), $.set(this, () => {
      const { bemClass: e } = G(this, C, "f").theme, { grid: s } = G(this, S, "f");
      return G(this, B, "f").call(this).map((a2, n) => U$1("div", { key: n, class: e(s._, s.column) }, a2.map((e2) => U$1(kt, null, e2))));
    }), q.set(this, () => {
      var _a;
      const { bemClass: e } = G(this, C, "f").theme, { grid: s } = G(this, S, "f"), { lfActions: a2, lfShape: n, lfView: r, shapes: o2 } = this;
      return G(this, P, "f").call(this) && ((_a = o2[n]) == null ? void 0 : _a.length) ? U$1(kt, null, U$1("div", { class: e(s._, null, { [r]: true }) }, G(this, $, "f").call(this)), a2 && G(this, H, "f").call(this)) : null;
    });
  }
  onLfEvent(t, e) {
    const { lfSelectable: s, lfShape: i, selectedShape: a, shapes: n } = this;
    let r = false;
    const o2 = {};
    if ("lf-event" === e) {
      const { comp: e2, eventType: l } = t.detail;
      if ("click" === l && s) {
        const t2 = parseInt(e2.rootElement.dataset.index);
        a.index !== t2 && (o2.index = t2, o2.shape = n[i][t2]), r = true;
      }
    }
    r && (this.selectedShape = o2), this.lfEvent.emit({ comp: this, eventType: e, id: this.rootElement.id, originalEvent: t, selectedShape: this.selectedShape });
  }
  validateColumns() {
    if (!G(this, C, "f")) return;
    const { debug: t } = G(this, C, "f");
    Array.isArray(this.lfColumns) && !G(this, N, "f").call(this, this.lfColumns) && (t.logs.new(this, "Invalid breakpoints in lfColumns: must be sorted in ascending order.", "warning"), this.lfColumns = [...LF_MASONRY_DEFAULT_COLUMNS]);
  }
  async updateShapes() {
    if (!G(this, C, "f")) return;
    const { data: t, debug: e } = G(this, C, "f");
    try {
      this.shapes = t.cell.shapes.getAll(this.lfDataset);
    } catch (t2) {
      e.logs.new(this, "Error updating shapes: " + t2, "error");
    }
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const t = LF_MASONRY_PROPS.map((t2) => [t2, this[t2]]);
    return Object.fromEntries(t);
  }
  async getSelectedShape() {
    return this.selectedShape;
  }
  async redecorateShapes() {
    this.updateShapes();
  }
  async refresh() {
    mt(this);
  }
  async setSelectedShape(t) {
    var _a, _b;
    const { debug: e } = G(this, C, "f"), s = (_b = (_a = this.shapes) == null ? void 0 : _a[this.lfShape]) == null ? void 0 : _b[t];
    s ? this.selectedShape = { index: t, shape: s } : (this.selectedShape = {}, e.logs.new(this, `Couldn't set shape with index: ${t}`)), this.updateShapes();
  }
  async unmount(t = 0) {
    setTimeout(() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, t);
  }
  connectedCallback() {
    G(this, C, "f") && G(this, C, "f").theme.register(this);
  }
  async componentWillLoad() {
    J(this, C, await o$1(this)), G(this, V, "f").call(this), this.updateShapes();
  }
  componentDidLoad() {
    window.addEventListener("resize", G(this, F, "f")), this.viewportWidth = window.innerWidth;
    const { info: t } = G(this, C, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), t.update(this, "did-load");
  }
  componentWillRender() {
    const { info: t } = G(this, C, "f").debug;
    J(this, I, G(this, D, "f").call(this) ? G(this, x, "m", O).call(this) : 1), t.update(this, "will-render");
  }
  componentDidRender() {
    const { info: t } = G(this, C, "f").debug;
    t.update(this, "did-render");
  }
  render() {
    const { bemClass: e, setLfStyle: s } = G(this, C, "f").theme, { masonry: i } = G(this, S, "f"), { lfStyle: a } = this, r = { [G(this, T, "f").columns]: String(G(this, I, "f")) };
    return U$1(A$1, { key: "d0051cc4d9a9ed96378fc6bac872f4cb43c7ebc7", style: r }, a && U$1("style", { key: "ef79b9b9ff06bb679df1d735302481885dd83c2b", id: G(this, A, "f") }, s(this)), U$1("div", { key: "4152ce202069ef7db4d5fe2a98bbc9c9543e11b7", id: G(this, E, "f") }, U$1("div", { key: "355f308a51be89300cc0e223a9e81f607e0a89b4", class: e(i._) }, G(this, q, "f").call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = G(this, C, "f")) == null ? void 0 : _a.theme.unregister(this), window.removeEventListener("resize", G(this, F, "f"));
  }
  get rootElement() {
    return T$1(this);
  }
  static get watchers() {
    return { lfColumns: ["validateColumns"], lfDataset: ["updateShapes"], lfShape: ["updateShapes"] };
  }
};
C = /* @__PURE__ */ new WeakMap(), S = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), A = /* @__PURE__ */ new WeakMap(), T = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakMap(), j = /* @__PURE__ */ new WeakMap(), L = /* @__PURE__ */ new WeakMap(), V = /* @__PURE__ */ new WeakMap(), P = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), R = /* @__PURE__ */ new WeakMap(), U = /* @__PURE__ */ new WeakMap(), N = /* @__PURE__ */ new WeakMap(), B = /* @__PURE__ */ new WeakMap(), F = /* @__PURE__ */ new WeakMap(), H = /* @__PURE__ */ new WeakMap(), $ = /* @__PURE__ */ new WeakMap(), q = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakSet(), O = function() {
  var _a, _b;
  const { lfColumns: t, viewportWidth: e, shapes: s, lfShape: i } = this;
  if ("number" == typeof t) return Math.min(t, ((_a = s[i]) == null ? void 0 : _a.length) || 0);
  if (Array.isArray(t)) {
    const a = t;
    let n = 1;
    for (let t2 = 0; t2 < a.length && e >= a[t2]; t2++) n = t2 + 1;
    return Math.min(n, ((_b = s == null ? void 0 : s[i]) == null ? void 0 : _b.length) || 0);
  }
  return 1;
}, K.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-masonry-font-family, var(--lf-font-family-primary));font-size:var(--lf-masonry-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}:host([lf-selectable]) lf-image{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);box-sizing:border-box;cursor:pointer;overflow:hidden}:host([lf-selectable]) lf-image:hover,:host([lf-selectable]) lf-image[data-selected=true]{filter:var(--lf-comp-selected-filter, brightness(110%) drop-shadow(0 0 0.5em rgb(var(--lf-color-secondary))))}:host([lf-selectable]) lf-image[data-selected=true]{border:var(--lf-masonry-selected-border, 1px solid rgba(var(--lf-color-secondary, 0.875)))}.masonry{width:100%;height:100%;box-sizing:border-box;display:flex;gap:var(--lf-masonry-grid-gap, 0.5em);overflow:auto;padding:var(--lf-masonry-padding, 0.75em);position:relative}.masonry:not(:hover) .grid__actions{display:none}.grid{width:100%;height:100%;align-items:var(--lf-masonry-grid-items-alignment, start);column-gap:var(--lf-masonry-grid-gap, 0.5em);display:grid;overflow-y:auto;overflow-x:hidden}.grid--horizontal{grid-template-rows:1fr;overflow-x:auto;overflow-y:hidden}.grid--horizontal .grid__column{flex-direction:row;height:100%;min-height:max-content;width:auto}.grid--main{grid-template-columns:repeat(var(--lf_masonry_columns), var(--lf-masonry-column-size, minmax(0px, 1fr)))}.grid--main .grid__column{flex-direction:column}.grid--vertical{grid-template-columns:1fr}.grid--vertical .grid__column{flex-direction:column}.grid__column{display:flex;flex:1;gap:var(--lf-masonry-grid-gap, 0.5em);width:100%}.grid__actions{bottom:var(--lf-masonry-button-bottom, 1em);display:grid;grid-auto-flow:row;grid-gap:var(--lf-masonry-grid-gap-actions, 0.5em);justify-items:center;position:absolute;right:var(--lf-masonry-button-right, 1em);z-index:var(--lf-masonry-actions-z-index, 2)}.grid__sub{display:grid;grid-gap:var(--lf-masonry-grid-gap-actions-sub, 0.25em)}";
export {
  K as lf_masonry
};
