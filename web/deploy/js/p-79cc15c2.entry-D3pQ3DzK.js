import { n, I as I$1, s as LF_MASONRY_DEFAULT_COLUMNS, t as LF_MASONRY_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, u as LF_MASONRY_PARTS, c as LF_STYLE_ID, v as LF_MASONRY_CSS_VARS, d as LF_WRAPPER_ID, W as W$1, k as kt, w as LF_MASONRY_PROPS, m as mt, f as L$1, G, x as LF_MASONRY_IDS } from "./index-CV1UCVp-.js";
import { o } from "./p-DklcdYZv-BOyMa_rz.js";
import { f } from "./p-HvQH5Jh2-gnu4dCv7.js";
const b = (t) => Number(t.rootElement.style.getPropertyValue(LF_MASONRY_CSS_VARS.columns)), w = (t, e) => Number(t.rootElement.style.setProperty(LF_MASONRY_CSS_VARS.columns, String(e))), k = (e) => /* @__PURE__ */ ((e2) => ({ addColumn: () => {
  const { controller: s, elements: i, handlers: a } = e2(), { refs: r } = i, { button: n2 } = a, { blocks: l, cyAttributes: f2, lfAttributes: h, manager: c, parts: d } = s.get, { assignRef: m, theme: u } = c, { bemClass: p, get: g } = u, { "--lf-icon-plus": y } = g.current().variables;
  return W$1("lf-button", { class: p(l.grid._, l.grid.addColumn), "data-cy": f2.button, "data-lf": h.fadeIn, id: LF_MASONRY_IDS.addColumn, key: LF_MASONRY_IDS.addColumn, lfIcon: y, lfStyling: "floating", lfUiSize: "xxsmall", "onLf-button-event": n2, part: d.addColumn, ref: m(r, "addColumn"), title: "Click to add a column to the masonry." });
}, removeColumn: () => {
  const { controller: s, elements: i, handlers: a } = e2(), { refs: r } = i, { button: n2 } = a, { blocks: l, cyAttributes: f2, lfAttributes: h, manager: c, parts: d } = s.get, { assignRef: m, theme: u } = c, { bemClass: p, get: g } = u, { "--lf-icon-minus": y } = g.current().variables;
  return W$1("lf-button", { class: p(l.grid._, l.grid.removeColumn), "data-cy": f2.button, "data-lf": h.fadeIn, id: LF_MASONRY_IDS.removeColumn, key: LF_MASONRY_IDS.removeColumn, lfIcon: y, lfStyling: "floating", lfUiSize: "xxsmall", "onLf-button-event": n2, part: d.removeColumn, ref: m(r, "removeColumn"), title: "Click to remove a column from the masonry." });
}, changeView: () => {
  const { controller: s, elements: i, handlers: a } = e2(), { refs: r } = i, { blocks: n2, cyAttributes: l, isMasonry: f2, isVertical: h, manager: c, parts: d } = s.get, { button: m } = a, { assignRef: u, theme: p } = c, { bemClass: g, get: y } = p, { layoutBoardSplit: v, viewportTall: b2, viewportWide: w2 } = y.icons();
  return W$1("lf-button", { class: g(n2.grid._, n2.grid.changeViewe), "data-cy": l.button, id: LF_MASONRY_IDS.masonry, key: LF_MASONRY_IDS.masonry, lfIcon: f2() ? b2 : h() ? w2 : v, lfStyling: "floating", lfUiSize: "xsmall", "onLf-button-event": m, part: d.changeView, ref: u(r, "changeView"), title: f2() ? "Click to view the images arranged vertically." : h() ? "Click to view the images arranged horizontally." : "Click to view the images arranged in a masonry." });
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
        const { compInstance: e2, currentColumns: s2 } = t3.controller.get, i2 = e2, a = b(i2) || s2();
        a > 1 && w(i2, a - 1);
      })(t2());
      break;
    case LF_MASONRY_IDS.addColumn:
      (async (t3) => {
        const { compInstance: e2, currentColumns: s2 } = t3.controller.get, i2 = e2, a = b(i2) || s2();
        w(i2, a + 1);
      })(t2());
  }
} }))(t);
var x, C, S, M, W, _, A, T, E, I, j, L, V, D, P, R, H, U, B, N, O, F, J, K, Q = function(t, e, s, i) {
  if ("a" === s && !i) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof e ? t !== e || !i : !e.has(t)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === s ? i : "a" === s ? i.call(t) : i ? i.value : e.get(t);
}, Y = function(t, e, s, i, a) {
  if ("function" == typeof e ? t !== e || true : !e.has(t)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return e.set(t, s), s;
};
const Z = class {
  constructor(a) {
    n(this, a), this.lfEvent = I$1(this, "lf-masonry-event"), x.add(this), this.selectedShape = {}, this.shapes = {}, this.lfActions = false, this.lfColumns = Array.from(LF_MASONRY_DEFAULT_COLUMNS), this.lfDataset = null, this.lfSelectable = false, this.lfShape = "image", this.lfStyle = "", this.lfView = "main", C.set(this, void 0), S.set(this, LF_MASONRY_BLOCKS), M.set(this, CY_ATTRIBUTES), W.set(this, LF_ATTRIBUTES), _.set(this, LF_MASONRY_PARTS), A.set(this, LF_STYLE_ID), T.set(this, LF_MASONRY_CSS_VARS), E.set(this, LF_WRAPPER_ID), I.set(this, void 0), j.set(this, void 0), L.set(this, void 0), V.set(this, (() => {
      var t;
      Y(this, L, { controller: { get: { blocks: Q(this, S, "f"), compInstance: this, currentColumns: () => Q(this, I, "f"), cyAttributes: Q(this, M, "f"), isMasonry: () => Q(this, P, "f").call(this), isVertical: () => Q(this, R, "f").call(this), lfAttributes: Q(this, W, "f"), manager: Q(this, C, "f"), parts: Q(this, _, "f"), shapes: () => this.shapes } }, elements: { jsx: k(t = () => Q(this, L, "f")), refs: { addColumn: null, removeColumn: null, changeView: null } }, handlers: z(t) });
    })), D.set(this, (() => {
      var _a;
      return !!((_a = this.shapes) == null ? void 0 : _a[this.lfShape]);
    })), P.set(this, (() => "main" === this.lfView)), R.set(this, (() => "vertical" === this.lfView)), H.set(this, ((t, e) => () => {
      clearTimeout(Q(this, j, "f")), Y(this, j, setTimeout(t, e));
    })), U.set(this, ((t) => t.every(((t2, e, s) => 0 === e || s[e - 1] < t2)))), N.set(this, (() => {
      const { lfShape: e, selectedShape: s, shapes: i } = this, a2 = i[this.lfShape].map((() => ({ htmlProps: { dataset: { lf: Q(this, W, "f").fadeIn, selected: "" } } })));
      void 0 !== s.index && (a2[s.index] = { htmlProps: { dataset: { lf: Q(this, W, "f").fadeIn, selected: "true" } } });
      const r = Array.from({ length: Q(this, I, "f") }, (() => []), []);
      for (let s2 = 0; s2 < i[e].length; s2++) {
        const n2 = i[e][s2], o2 = a2[s2];
        r[s2 % Q(this, I, "f")].push(W$1(f, { cell: Object.assign(o2, n2), index: s2, shape: e, eventDispatcher: async (t) => this.onLfEvent(t, "lf-event"), framework: Q(this, C, "f") }));
      }
      return r;
    })), O.set(this, Q(this, H, "f").call(this, (() => {
      this.viewportWidth = window.innerWidth;
    }), 200)), F.set(this, (() => {
      const { bemClass: e } = Q(this, C, "f").theme, { grid: s } = Q(this, S, "f"), { addColumn: i, changeView: a2, removeColumn: r } = Q(this, L, "f").elements.jsx;
      return W$1("div", { class: e(s._, s.actions), "data-lf": Q(this, W, "f").fadeIn }, Q(this, P, "f").call(this) && W$1("div", { class: e(s._, s.sub) }, i(), r()), a2());
    })), J.set(this, (() => {
      const { bemClass: e } = Q(this, C, "f").theme, { grid: s } = Q(this, S, "f");
      return Q(this, N, "f").call(this).map(((a2, r) => W$1("div", { key: r, class: e(s._, s.column) }, a2.map(((e2) => W$1(kt, null, e2))))));
    })), K.set(this, (() => {
      var _a;
      const { bemClass: e } = Q(this, C, "f").theme, { grid: s } = Q(this, S, "f"), { lfActions: a2, lfShape: r, lfView: n2, shapes: o2 } = this;
      return Q(this, D, "f").call(this) && ((_a = o2[r]) == null ? void 0 : _a.length) ? W$1(kt, null, W$1("div", { class: e(s._, null, { [n2]: true }) }, Q(this, J, "f").call(this)), a2 && Q(this, F, "f").call(this)) : null;
    }));
  }
  onLfEvent(t, e) {
    const { lfSelectable: s, lfShape: i, selectedShape: a, shapes: r } = this;
    let n2 = false;
    const o2 = {};
    if ("lf-event" === e) {
      const { comp: e2, eventType: l } = t.detail;
      if ("click" === l && s) {
        const t2 = parseInt(e2.rootElement.dataset.index);
        a.index !== t2 && (o2.index = t2, o2.shape = r[i][t2]), n2 = true;
      }
    }
    n2 && (this.selectedShape = o2), this.lfEvent.emit({ comp: this, eventType: e, id: this.rootElement.id, originalEvent: t, selectedShape: this.selectedShape });
  }
  validateColumns() {
    if (!Q(this, C, "f")) return;
    const { debug: t } = Q(this, C, "f");
    Array.isArray(this.lfColumns) && !Q(this, U, "f").call(this, this.lfColumns) && (t.logs.new(this, "Invalid breakpoints in lfColumns: must be sorted in ascending order.", "warning"), this.lfColumns = [...LF_MASONRY_DEFAULT_COLUMNS]);
  }
  async updateShapes() {
    if (!Q(this, C, "f")) return;
    const { data: t, debug: e } = Q(this, C, "f");
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
    const t = LF_MASONRY_PROPS.map(((t2) => [t2, this[t2]]));
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
    const { debug: e } = Q(this, C, "f"), s = (_b = (_a = this.shapes) == null ? void 0 : _a[this.lfShape]) == null ? void 0 : _b[t];
    s ? this.selectedShape = { index: t, shape: s } : (this.selectedShape = {}, e.logs.new(this, `Couldn't set shape with index: ${t}`)), this.updateShapes();
  }
  async unmount(t = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), t);
  }
  connectedCallback() {
    Q(this, C, "f") && Q(this, C, "f").theme.register(this);
  }
  async componentWillLoad() {
    Y(this, C, await o(this)), Q(this, V, "f").call(this), this.updateShapes();
  }
  componentDidLoad() {
    window.addEventListener("resize", Q(this, O, "f")), this.viewportWidth = window.innerWidth;
    const { info: t } = Q(this, C, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), t.update(this, "did-load");
  }
  componentWillRender() {
    const { info: t } = Q(this, C, "f").debug;
    Y(this, I, Q(this, P, "f").call(this) ? Q(this, x, "m", B).call(this) : 1), t.update(this, "will-render");
  }
  componentDidRender() {
    const { info: t } = Q(this, C, "f").debug;
    t.update(this, "did-render");
  }
  render() {
    const { bemClass: e, setLfStyle: s } = Q(this, C, "f").theme, { masonry: i } = Q(this, S, "f"), { lfStyle: a } = this, n2 = { [Q(this, T, "f").columns]: String(Q(this, I, "f")) };
    return W$1(L$1, { key: "f15dfb28cb25832011b4c77c80c19d2df9dfbec4", style: n2 }, a && W$1("style", { key: "dc3c0a746b80d1383e446c7a232d9cc49b38ffc7", id: Q(this, A, "f") }, s(this)), W$1("div", { key: "2ffcf048d6643efa080b5ab21709060b0ae1196c", id: Q(this, E, "f") }, W$1("div", { key: "20ffcd6cbbe7c235d1a26be2aa54106149a922da", class: e(i._) }, Q(this, K, "f").call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = Q(this, C, "f")) == null ? void 0 : _a.theme.unregister(this), window.removeEventListener("resize", Q(this, O, "f"));
  }
  get rootElement() {
    return G(this);
  }
  static get watchers() {
    return { lfColumns: ["validateColumns"], lfDataset: ["updateShapes"], lfShape: ["updateShapes"] };
  }
};
C = /* @__PURE__ */ new WeakMap(), S = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), A = /* @__PURE__ */ new WeakMap(), T = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakMap(), j = /* @__PURE__ */ new WeakMap(), L = /* @__PURE__ */ new WeakMap(), V = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), P = /* @__PURE__ */ new WeakMap(), R = /* @__PURE__ */ new WeakMap(), H = /* @__PURE__ */ new WeakMap(), U = /* @__PURE__ */ new WeakMap(), N = /* @__PURE__ */ new WeakMap(), O = /* @__PURE__ */ new WeakMap(), F = /* @__PURE__ */ new WeakMap(), J = /* @__PURE__ */ new WeakMap(), K = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakSet(), B = function() {
  var _a, _b;
  const { lfColumns: t, viewportWidth: e, shapes: s, lfShape: i } = this;
  if ("number" == typeof t) return Math.min(t, ((_a = s[i]) == null ? void 0 : _a.length) || 0);
  if (Array.isArray(t)) {
    const a = t;
    let r = 1;
    for (let t2 = 0; t2 < a.length && e >= a[t2]; t2++) r = t2 + 1;
    return Math.min(r, ((_b = s == null ? void 0 : s[i]) == null ? void 0 : _b.length) || 0);
  }
  return 1;
}, Z.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-masonry-font-family, var(--lf-font-family-primary));font-size:var(--lf-masonry-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}:host([lf-selectable]) lf-image{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);box-sizing:border-box;cursor:pointer;overflow:hidden}:host([lf-selectable]) lf-image:hover,:host([lf-selectable]) lf-image[data-selected=true]{filter:var(--lf-comp-selected-filter, brightness(110%) drop-shadow(0 0 0.5em rgb(var(--lf-color-secondary))))}:host([lf-selectable]) lf-image[data-selected=true]{border:var(--lf-masonry-selected-border, 1px solid rgba(var(--lf-color-secondary, 0.875)))}.masonry{width:100%;height:100%;box-sizing:border-box;display:flex;gap:var(--lf-masonry-grid-gap, 0.5em);overflow:auto;padding:var(--lf-masonry-padding, 0.75em);position:relative}.masonry:not(:hover) .grid__actions{display:none}.grid{width:100%;height:100%;align-items:var(--lf-masonry-grid-items-alignment, start);column-gap:var(--lf-masonry-grid-gap, 0.5em);display:grid;overflow-y:auto;overflow-x:hidden}.grid--horizontal{grid-template-rows:1fr;overflow-x:auto;overflow-y:hidden}.grid--horizontal .grid__column{flex-direction:row;height:100%;min-height:max-content;width:auto}.grid--main{grid-template-columns:repeat(var(--lf_masonry_columns), var(--lf-masonry-column-size, minmax(0px, 1fr)))}.grid--main .grid__column{flex-direction:column}.grid--vertical{grid-template-columns:1fr}.grid--vertical .grid__column{flex-direction:column}.grid__column{display:flex;flex:1;gap:var(--lf-masonry-grid-gap, 0.5em);width:100%}.grid__actions{bottom:var(--lf-masonry-button-bottom, 1em);display:grid;grid-auto-flow:row;grid-gap:var(--lf-masonry-grid-gap-actions, 0.5em);justify-items:center;position:absolute;right:var(--lf-masonry-button-right, 1em);z-index:var(--lf-masonry-actions-z-index, 2)}.grid__sub{display:grid;grid-gap:var(--lf-masonry-grid-gap-actions-sub, 0.25em)}";
export {
  Z as lf_masonry
};
