import { n, V as V$1, H as LF_MASONRY_DEFAULT_COLUMNS, J as LF_MASONRY_BLOCKS, C as CY_ATTRIBUTES, f as LF_ATTRIBUTES, K as LF_MASONRY_PARTS, b as LF_STYLE_ID, M as LF_MASONRY_CSS_VARS, c as LF_WRAPPER_ID, D as D$1, k as jt, N as LF_MASONRY_PROPS, p as pt, W as W$1, z as z$1, P as LF_MASONRY_IDS } from "./index-KdsGGJBN.js";
import { a } from "./p-Dl9cVpAY-C31OpVB5.js";
import { r } from "./p-CKijk88y-BB5Rc032.js";
const v = (e) => /* @__PURE__ */ ((e2) => ({ addColumn: () => {
  const { controller: s, elements: i, handlers: a2 } = e2(), { refs: r2 } = i, { button: n2 } = a2, { blocks: l, cyAttributes: f, lfAttributes: h, manager: c, parts: d } = s.get, { assignRef: m, theme: u } = c, { bemClass: p, get: g } = u, { "--lf-icon-plus": y } = g.current().variables;
  return D$1("lf-button", { class: p(l.grid._, l.grid.addColumn), "data-cy": f.button, "data-lf": h.fadeIn, id: LF_MASONRY_IDS.addColumn, key: LF_MASONRY_IDS.addColumn, lfIcon: y, lfStyling: "floating", lfUiSize: "xxsmall", "onLf-button-event": n2, part: d.addColumn, ref: m(r2, "addColumn"), title: "Click to add a column to the masonry." });
}, removeColumn: () => {
  const { controller: s, elements: i, handlers: a2 } = e2(), { refs: r2 } = i, { button: n2 } = a2, { blocks: l, cyAttributes: f, lfAttributes: h, manager: c, parts: d } = s.get, { assignRef: m, theme: u } = c, { bemClass: p, get: g } = u, { "--lf-icon-minus": y } = g.current().variables;
  return D$1("lf-button", { class: p(l.grid._, l.grid.removeColumn), "data-cy": f.button, "data-lf": h.fadeIn, id: LF_MASONRY_IDS.removeColumn, key: LF_MASONRY_IDS.removeColumn, lfIcon: y, lfStyling: "floating", lfUiSize: "xxsmall", "onLf-button-event": n2, part: d.removeColumn, ref: m(r2, "removeColumn"), title: "Click to remove a column from the masonry." });
}, changeView: () => {
  const { controller: s, elements: i, handlers: a2 } = e2(), { refs: r2 } = i, { blocks: n2, cyAttributes: l, isMasonry: f, isVertical: h, manager: c, parts: d } = s.get, { button: m } = a2, { assignRef: u, theme: p } = c, { bemClass: g, get: y } = p, { layoutBoardSplit: b, viewportTall: v2, viewportWide: w2 } = y.icons();
  return D$1("lf-button", { class: g(n2.grid._, n2.grid.changeViewe), "data-cy": l.button, id: LF_MASONRY_IDS.masonry, key: LF_MASONRY_IDS.masonry, lfIcon: f() ? v2 : h() ? w2 : b, lfStyling: "floating", lfUiSize: "xsmall", "onLf-button-event": m, part: d.changeView, ref: u(r2, "changeView"), title: f() ? "Click to view the images arranged vertically." : h() ? "Click to view the images arranged horizontally." : "Click to view the images arranged in a masonry." });
} }))(e), w = (t) => /* @__PURE__ */ ((t2) => ({ button: (e) => {
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
        const { get: e2 } = t3.controller, { compInstance: s2, currentColumns: i2 } = e2, a2 = s2, r2 = i2();
        r2 > 1 && (a2.lfColumns = r2 - 1);
      })(t2());
      break;
    case LF_MASONRY_IDS.addColumn:
      (async (t3) => {
        const { get: e2 } = t3.controller, { compInstance: s2, currentColumns: i2 } = e2, a2 = i2();
        s2.lfColumns = a2 + 1;
      })(t2());
  }
} }))(t);
var k, z, x, C, S, M, W, _, A, T, E, j, I, V, L, D, P, R, U, B, H, O, F, K, Y = function(t, e, s, i) {
  if ("a" === s && !i) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof e ? t !== e || !i : !e.has(t)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === s ? i : "a" === s ? i.call(t) : i ? i.value : e.get(t);
}, $ = function(t, e, s, i, a2) {
  if ("function" == typeof e ? t !== e || true : !e.has(t)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return e.set(t, s), s;
};
const q = class {
  constructor(a2) {
    n(this, a2), this.lfEvent = V$1(this, "lf-masonry-event"), k.add(this), this.selectedShape = {}, this.shapes = {}, this.lfActions = false, this.lfColumns = Array.from(LF_MASONRY_DEFAULT_COLUMNS), this.lfDataset = null, this.lfSelectable = false, this.lfShape = "image", this.lfStyle = "", this.lfView = "main", z.set(this, void 0), x.set(this, LF_MASONRY_BLOCKS), C.set(this, CY_ATTRIBUTES), S.set(this, LF_ATTRIBUTES), M.set(this, LF_MASONRY_PARTS), W.set(this, LF_STYLE_ID), _.set(this, LF_MASONRY_CSS_VARS), A.set(this, LF_WRAPPER_ID), T.set(this, void 0), E.set(this, void 0), j.set(this, void 0), I.set(this, (() => {
      var t;
      $(this, j, { controller: { get: { blocks: Y(this, x, "f"), compInstance: this, currentColumns: () => Y(this, T, "f"), cyAttributes: Y(this, C, "f"), isMasonry: () => Y(this, L, "f").call(this), isVertical: () => Y(this, D, "f").call(this), lfAttributes: Y(this, S, "f"), manager: Y(this, z, "f"), parts: Y(this, M, "f"), shapes: () => this.shapes } }, elements: { jsx: v(t = () => Y(this, j, "f")), refs: { addColumn: null, removeColumn: null, changeView: null } }, handlers: w(t) });
    })), V.set(this, (() => {
      var _a;
      return !!((_a = this.shapes) == null ? void 0 : _a[this.lfShape]);
    })), L.set(this, (() => "main" === this.lfView)), D.set(this, (() => "vertical" === this.lfView)), P.set(this, ((t, e) => () => {
      clearTimeout(Y(this, E, "f")), $(this, E, setTimeout(t, e));
    })), R.set(this, ((t) => t.every(((t2, e, s) => 0 === e || s[e - 1] < t2)))), B.set(this, (() => {
      const { lfShape: e, selectedShape: s, shapes: i } = this, a3 = i[this.lfShape].map((() => ({ htmlProps: { dataset: { lf: Y(this, S, "f").fadeIn, selected: "" } } })));
      void 0 !== s.index && (a3[s.index] = { htmlProps: { dataset: { lf: Y(this, S, "f").fadeIn, selected: "true" } } });
      const r$1 = Array.from({ length: Y(this, T, "f") }, (() => []), []);
      for (let s2 = 0; s2 < i[e].length; s2++) {
        const n2 = i[e][s2], o = a3[s2];
        r$1[s2 % Y(this, T, "f")].push(D$1(r, { cell: Object.assign(o, n2), index: s2, shape: e, eventDispatcher: async (t) => this.onLfEvent(t, "lf-event"), framework: Y(this, z, "f") }));
      }
      return r$1;
    })), H.set(this, Y(this, P, "f").call(this, (() => {
      this.viewportWidth = window.innerWidth;
    }), 200)), O.set(this, (() => {
      const { bemClass: e } = Y(this, z, "f").theme, { grid: s } = Y(this, x, "f"), { addColumn: i, changeView: a3, removeColumn: r2 } = Y(this, j, "f").elements.jsx;
      return D$1("div", { class: e(s._, s.actions), "data-lf": Y(this, S, "f").fadeIn }, Y(this, L, "f").call(this) && D$1("div", { class: e(s._, s.sub) }, i(), r2()), a3());
    })), F.set(this, (() => {
      const { bemClass: e } = Y(this, z, "f").theme, { grid: s } = Y(this, x, "f");
      return Y(this, B, "f").call(this).map(((a3, r2) => D$1("div", { key: r2, class: e(s._, s.column) }, a3.map(((e2) => D$1(jt, null, e2))))));
    })), K.set(this, (() => {
      var _a;
      const { bemClass: e } = Y(this, z, "f").theme, { grid: s } = Y(this, x, "f"), { lfActions: a3, lfShape: r2, lfView: n2, shapes: o } = this;
      return Y(this, V, "f").call(this) && ((_a = o[r2]) == null ? void 0 : _a.length) ? D$1(jt, null, D$1("div", { class: e(s._, null, { [n2]: true }) }, Y(this, F, "f").call(this)), a3 && Y(this, O, "f").call(this)) : null;
    }));
  }
  onLfEvent(t, e) {
    const { lfSelectable: s, lfShape: i, selectedShape: a2, shapes: r2 } = this;
    let n2 = false;
    const o = {};
    if ("lf-event" === e) {
      const { comp: e2, eventType: l } = t.detail;
      if ("click" === l && s) {
        const t2 = parseInt(e2.rootElement.dataset.index);
        a2.index !== t2 && (o.index = t2, o.shape = r2[i][t2]), n2 = true;
      }
    }
    n2 && (this.selectedShape = o), this.lfEvent.emit({ comp: this, eventType: e, id: this.rootElement.id, originalEvent: t, selectedShape: this.selectedShape });
  }
  validateColumns() {
    if (!Y(this, z, "f")) return;
    const { debug: t } = Y(this, z, "f");
    Array.isArray(this.lfColumns) && !Y(this, R, "f").call(this, this.lfColumns) && (t.logs.new(this, "Invalid breakpoints in lfColumns: must be sorted in ascending order.", "warning"), this.lfColumns = [...LF_MASONRY_DEFAULT_COLUMNS]);
  }
  async updateShapes() {
    if (!Y(this, z, "f")) return;
    const { data: t, debug: e } = Y(this, z, "f");
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
    pt(this);
  }
  async setSelectedShape(t) {
    var _a, _b;
    const { debug: e } = Y(this, z, "f"), s = (_b = (_a = this.shapes) == null ? void 0 : _a[this.lfShape]) == null ? void 0 : _b[t];
    s ? this.selectedShape = { index: t, shape: s } : (this.selectedShape = {}, e.logs.new(this, `Couldn't set shape with index: ${t}`)), this.updateShapes();
  }
  async unmount(t = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), t);
  }
  connectedCallback() {
    Y(this, z, "f") && Y(this, z, "f").theme.register(this);
  }
  async componentWillLoad() {
    $(this, z, await a(this)), Y(this, I, "f").call(this), this.updateShapes();
  }
  componentDidLoad() {
    window.addEventListener("resize", Y(this, H, "f")), this.viewportWidth = window.innerWidth;
    const { info: t } = Y(this, z, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), t.update(this, "did-load");
  }
  componentWillRender() {
    const { info: t } = Y(this, z, "f").debug;
    $(this, T, Y(this, L, "f").call(this) ? Y(this, k, "m", U).call(this) : 1), t.update(this, "will-render");
  }
  componentDidRender() {
    const { info: t } = Y(this, z, "f").debug;
    t.update(this, "did-render");
  }
  render() {
    const { bemClass: e, setLfStyle: s } = Y(this, z, "f").theme, { masonry: i } = Y(this, x, "f"), { lfStyle: a2 } = this, n2 = { [Y(this, _, "f").columns]: String(Y(this, T, "f")) };
    return D$1(W$1, { key: "badbb6aa631769c02b287aeb7244293e15f1b81f", style: n2 }, a2 && D$1("style", { key: "f7d6a9aee293e23aff45c85c5c48927de3416edb", id: Y(this, W, "f") }, s(this)), D$1("div", { key: "3d0ec51656b8fb1726406a24ed184207609ea2f1", id: Y(this, A, "f") }, D$1("div", { key: "d3f7292aaee793b705fba479363c8668bc57c79a", class: e(i._) }, Y(this, K, "f").call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = Y(this, z, "f")) == null ? void 0 : _a.theme.unregister(this), window.removeEventListener("resize", Y(this, H, "f"));
  }
  get rootElement() {
    return z$1(this);
  }
  static get watchers() {
    return { lfColumns: ["validateColumns"], lfDataset: ["updateShapes"], lfShape: ["updateShapes"] };
  }
};
z = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakMap(), S = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), A = /* @__PURE__ */ new WeakMap(), T = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), j = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakMap(), V = /* @__PURE__ */ new WeakMap(), L = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), P = /* @__PURE__ */ new WeakMap(), R = /* @__PURE__ */ new WeakMap(), B = /* @__PURE__ */ new WeakMap(), H = /* @__PURE__ */ new WeakMap(), O = /* @__PURE__ */ new WeakMap(), F = /* @__PURE__ */ new WeakMap(), K = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakSet(), U = function() {
  var _a, _b;
  const { lfColumns: t, viewportWidth: e, shapes: s, lfShape: i } = this;
  if (!Y(this, V, "f").call(this)) return 1;
  if ("number" == typeof t) return Math.min(t, ((_a = s[i]) == null ? void 0 : _a.length) || 0);
  if (Array.isArray(t)) {
    const a2 = t;
    let r2 = 1;
    for (let t2 = 0; t2 < a2.length && e >= a2[t2]; t2++) r2 = t2 + 1;
    return Math.min(r2, ((_b = s == null ? void 0 : s[i]) == null ? void 0 : _b.length) || 0);
  }
  return 1;
}, q.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-masonry-font-family, var(--lf-font-family-primary));font-size:var(--lf-masonry-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-masonry-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}:host([lf-selectable]) lf-image{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);box-sizing:border-box;cursor:pointer;overflow:hidden}:host([lf-selectable]) lf-image:hover,:host([lf-selectable]) lf-image[data-selected=true]{filter:var(--lf-comp-selected-filter, brightness(110%) drop-shadow(0 0 0.5em rgb(var(--lf-color-secondary))))}:host([lf-selectable]) lf-image[data-selected=true]{border:var(--lf-masonry-selected-border, 1px solid rgba(var(--lf-color-secondary, 0.875)))}.masonry{width:100%;height:100%;box-sizing:border-box;display:flex;gap:var(--lf-masonry-grid-gap, 0.5em);overflow:auto;padding:var(--lf-masonry-padding, 0.75em);position:relative}.masonry:not(:hover) .grid__actions{display:none}.grid{width:100%;height:100%;align-items:var(--lf-masonry-grid-items-alignment, start);column-gap:var(--lf-masonry-grid-gap, 0.5em);display:grid;overflow-y:auto;overflow-x:hidden}.grid--horizontal{grid-template-rows:1fr;overflow-x:auto;overflow-y:hidden}.grid--horizontal .grid__column{flex-direction:row;height:100%;min-height:max-content;width:auto}.grid--main{grid-template-columns:repeat(var(--lf_masonry_columns), var(--lf-masonry-column-size, minmax(0px, 1fr)))}.grid--main .grid__column{flex-direction:column}.grid--vertical{grid-template-columns:1fr}.grid--vertical .grid__column{flex-direction:column}.grid__column{display:flex;flex:1;gap:var(--lf-masonry-grid-gap, 0.5em);width:100%}.grid__actions{backdrop-filter:var(--lf-masonry-actions-backdrop, blur(10px));background-color:var(--lf-masonry-actions-background, rgba(var(--lf-color-surface), 0.75));border-radius:var(--lf-masonry-actions-border-radius, 50px);bottom:var(--lf-masonry-button-bottom, 1em);display:grid;grid-auto-flow:row;grid-gap:var(--lf-masonry-grid-gap-actions, 0.5em);justify-items:center;margin:var(--lf-masonry-actions-margin, 0 0.5em 0.5em 0);padding:var(--lf-masonry-actions-padding, 0.75em);position:absolute;right:var(--lf-masonry-button-right, 1em);z-index:var(--lf-masonry-actions-z-index, 2)}.grid__sub{display:grid;grid-gap:var(--lf-masonry-grid-gap-actions-sub, 0.25em)}";
export {
  q as lf_masonry
};
