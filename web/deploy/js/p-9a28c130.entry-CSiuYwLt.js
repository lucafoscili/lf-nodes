import { n, V as V$1, b8 as LF_COMPARE_BLOCKS, C as CY_ATTRIBUTES, b as LF_ATTRIBUTES, b9 as LF_COMPARE_PARTS, d as LF_STYLE_ID, ba as LF_COMPARE_CSS_VARS, f as LF_WRAPPER_ID, bb as LF_COMPARE_DEFAULTS, bc as LF_COMPARE_PROPS, p as pt, D as D$1, W as W$1, z as z$1, j as jt, bd as LF_COMPARE_IDS } from "./index-BCfB3I5o.js";
import { a } from "./p-Dl9cVpAY-BVBOtcmu.js";
import { f } from "./p-Cn5YKT90-DluM1Jlc.js";
const w = (e, t, r) => {
  const i = { nodes: [] };
  for (let a2 = 0; a2 < r.length; a2++) {
    const s = r[a2], o = String(a2).valueOf(), l = "string" == typeof s.value && s.value.trim().length > 0;
    i.nodes.push({ icon: e === s && t, id: o, value: l ? s.value : `#${o}` });
  }
  return i;
}, k = (e) => ({ ...e, defaults: LF_COMPARE_DEFAULTS() }), y = (t) => /* @__PURE__ */ ((t2) => ({ changeView: () => {
  const { controller: r, elements: i, handlers: a2 } = t2(), { cyAttributes: s, isOverlay: o, manager: n2, parts: f2 } = r.get, { refs: c } = i, { button: h } = a2, { assignRef: p, theme: d } = n2, { columns2: u, squareToggle: m } = d.get.icons();
  return D$1("lf-button", { "data-cy": s.button, id: LF_COMPARE_IDS.changeView, lfIcon: m, lfIconOff: u, lfStyling: "icon", lfToggable: true, lfValue: !o(), "onLf-button-event": h, part: f2.changeView, ref: p(c, "changeView"), title: o() ? "Click for split screen comparison." : "Click for overlay comparison" });
}, leftButton: () => {
  const { controller: r, elements: i, handlers: a2 } = t2(), { cyAttributes: s, isOverlay: o, manager: n2, parts: f2 } = r.get, { refs: c } = i, { button: h } = a2, { assignRef: p, theme: d } = n2, u = d.get.icon("imageInPicture"), { "--lf-icon-clear": m } = d.get.current().variables;
  return D$1("lf-button", { "data-cy": s.button, id: LF_COMPARE_IDS.leftButton, lfIcon: m, lfIconOff: u, lfStyling: "icon", lfToggable: true, "onLf-button-event": h, part: f2.leftButton, ref: p(c, "leftButton"), title: o() ? "Click to open the left panel." : "Click to close the left panel." });
}, leftTree: () => {
  const { controller: r, elements: i, handlers: a2 } = t2(), { blocks: s, compInstance: o, lfAttributes: n2, manager: f2, parts: c, shapes: h } = r.get, { refs: p } = i, { tree: d } = a2, { assignRef: u, theme: m } = f2, { bemClass: b, get: g } = m, { "--lf-icon-success": v } = g.current().variables, k2 = o;
  return D$1("lf-tree", { class: b(s.toolbar._, s.toolbar.panel, { left: true }), "data-lf": n2.fadeIn, id: LF_COMPARE_IDS.leftTree, lfDataset: w(k2.leftShape, v, h()), lfFilter: false, "onLf-tree-event": d, part: c.leftTree, ref: u(p, "leftTree") });
}, rightButton: () => {
  const { controller: r, elements: i, handlers: a2 } = t2(), { cyAttributes: s, isOverlay: o, manager: n2, parts: f2 } = r.get, { refs: c } = i, { button: h } = a2, { assignRef: p, theme: d } = n2, u = d.get.icon("imageInPicture"), { "--lf-icon-clear": m } = d.get.current().variables;
  return D$1("lf-button", { "data-cy": s.button, id: LF_COMPARE_IDS.rightButton, lfIcon: m, lfIconOff: u, lfStyling: "icon", lfToggable: true, "onLf-button-event": h, part: f2.rightButton, ref: p(c, "rightButton"), title: o() ? "Click to open the right panel." : "Click to close the right panel." });
}, rightTree: () => {
  const { controller: r, elements: i, handlers: a2 } = t2(), { blocks: s, compInstance: o, lfAttributes: n2, manager: f2, parts: c, shapes: h } = r.get, { refs: p } = i, { tree: d } = a2, { assignRef: u, theme: m } = f2, { bemClass: b, get: g } = m, { "--lf-icon-success": v } = g.current().variables, k2 = o;
  return D$1("lf-tree", { class: b(s.toolbar._, s.toolbar.panel, { right: true }), "data-lf": n2.fadeIn, id: LF_COMPARE_IDS.rightTree, lfDataset: w(k2.rightShape, v, h()), lfFilter: false, "onLf-tree-event": d, part: c.rightTree, ref: u(p, "rightTree") });
} }))(t), z = (e) => /* @__PURE__ */ ((e2) => ({ button: (t) => {
  const { eventType: r, id: i, valueAsBoolean: a2 } = t.detail, { set: s } = e2().controller, { leftButton: o, changeView: n2, rightButton: f2 } = LF_COMPARE_IDS;
  if ("click" === r) switch (i) {
    case o:
      s.leftPanelOpened(a2);
      break;
    case n2:
      s.splitView(a2);
      break;
    case f2:
      s.rightPanelOpened(a2);
  }
}, tree: (t) => {
  const { eventType: r, id: i, node: a2 } = t.detail, { get: s, set: o } = e2().controller, { shapes: n2 } = s, { leftTree: f2, rightTree: c } = LF_COMPARE_IDS;
  if ("click" === r) {
    const e3 = n2()[parseInt(a2.id)];
    switch (i) {
      case f2:
        o.leftShape(e3);
        break;
      case c:
        o.rightShape(e3);
    }
  }
} }))(e);
var x, T, _, C, I, S, O, W, B, E, L, M, j, P, A, D, V, R, F = function(e, t, r, i) {
  if ("a" === r && !i) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !i : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === r ? i : "a" === r ? i.call(e) : i ? i.value : t.get(e);
}, H = function(e, t, r, i, a2) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, r), r;
};
const Y = class {
  constructor(e) {
    n(this, e), this.lfEvent = V$1(this, "lf-compare-event"), x.add(this), this.isLeftPanelOpened = false, this.isRightPanelOpened = false, this.shapes = {}, this.lfDataset = null, this.lfShape = "image", this.lfStyle = "", this.lfView = "main", T.set(this, void 0), _.set(this, LF_COMPARE_BLOCKS), C.set(this, CY_ATTRIBUTES), I.set(this, LF_ATTRIBUTES), S.set(this, LF_COMPARE_PARTS), O.set(this, LF_STYLE_ID), W.set(this, LF_COMPARE_CSS_VARS), B.set(this, LF_WRAPPER_ID), E.set(this, void 0), L.set(this, (() => {
      var e2, t, r;
      H(this, E, (e2 = { blocks: F(this, _, "f"), compInstance: this, cyAttributes: F(this, C, "f"), isOverlay: () => F(this, x, "m", P).call(this), lfAttributes: F(this, I, "f"), manager: F(this, T, "f"), parts: F(this, S, "f"), shapes: () => F(this, x, "m", M).call(this) }, t = { leftPanelOpened: (e3) => {
        this.isLeftPanelOpened = void 0 === e3 ? !this.isLeftPanelOpened : e3;
      }, leftShape: (e3) => this.leftShape = e3, rightPanelOpened: (e3) => {
        this.isRightPanelOpened = void 0 === e3 ? !this.isRightPanelOpened : e3;
      }, rightShape: (e3) => this.rightShape = e3, splitView: (e3) => {
        this.lfView = e3 ? "split" : "main";
      } }, r = () => F(this, E, "f"), { controller: { get: k(e2), set: t }, elements: { jsx: y(r), refs: { changeView: null, leftButton: null, leftTree: null, rightButton: null, rightTree: null, slider: null } }, handlers: z(r) }));
    })), R.set(this, ((e2) => {
      const { target: t } = e2;
      if (t instanceof HTMLInputElement) {
        const e3 = 100 - parseInt(t.value);
        this.rootElement.style.setProperty(F(this, W, "f").overlayWidth, `${e3}%`);
      }
    }));
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e });
  }
  async updateShapes() {
    if (!F(this, T, "f")) return;
    const { data: e, debug: t } = F(this, T, "f");
    try {
      this.shapes = e.cell.shapes.getAll(this.lfDataset);
      const t2 = F(this, x, "m", M).call(this);
      this.leftShape = t2[0], this.rightShape = t2[1];
    } catch (e2) {
      t.logs.new(this, "Error updating shapes: " + e2, "error");
    }
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_COMPARE_PROPS.map(((e2) => [e2, this[e2]]));
    return Object.fromEntries(e);
  }
  async refresh() {
    pt(this);
  }
  async unmount(e = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), e);
  }
  connectedCallback() {
    F(this, T, "f") && F(this, T, "f").theme.register(this);
  }
  async componentWillLoad() {
    H(this, T, await a(this)), F(this, L, "f").call(this), this.updateShapes();
  }
  componentDidLoad() {
    const { info: e } = F(this, T, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = F(this, T, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = F(this, T, "f").debug;
    e.update(this, "did-render");
  }
  render() {
    const { bemClass: t, setLfStyle: r } = F(this, T, "f").theme, { compare: i } = F(this, _, "f"), { lfStyle: s } = this;
    return D$1(W$1, { key: "b380add562e68e1fd55ef7941e73975245ede58b" }, s && D$1("style", { key: "5e22ff430f5b625411e951c399071bf8c689d709", id: F(this, O, "f") }, r(this)), D$1("div", { key: "5c3143d8cd79c62a85a915a8944752df19c6f63b", id: F(this, B, "f") }, D$1("div", { key: "06951a5445c8869c068e24c8fc889b7691ef7a3b", class: t(i._), part: F(this, S, "f").compare }, F(this, x, "m", A).call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = F(this, T, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return z$1(this);
  }
  static get watchers() {
    return { lfDataset: ["updateShapes"], lfShape: ["updateShapes"] };
  }
};
T = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakMap(), S = /* @__PURE__ */ new WeakMap(), O = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), B = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), L = /* @__PURE__ */ new WeakMap(), R = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakSet(), M = function() {
  var _a;
  return ((_a = this.shapes) == null ? void 0 : _a[this.lfShape]) || [];
}, j = function() {
  var _a;
  return !!((_a = this.shapes) == null ? void 0 : _a[this.lfShape]);
}, P = function() {
  return !("main" !== this.lfView);
}, A = function() {
  const { bemClass: t } = F(this, T, "f").theme, { compare: r } = F(this, _, "f");
  if (F(this, x, "m", j).call(this)) {
    const i = this.shapes[this.lfShape];
    if ((i == null ? void 0 : i.length) > 1) return D$1("div", { class: t(r._, r.grid) }, F(this, x, "m", V).call(this), F(this, x, "m", D).call(this));
  }
  return null;
}, D = function() {
  const { bemClass: t } = F(this, T, "f").theme, { toolbar: r } = F(this, _, "f"), { changeView: i, leftButton: a2, rightButton: s } = F(this, E, "f").elements.jsx;
  return D$1("div", { class: t(r._) }, a2(), i(), s());
}, V = function() {
  var _a, _b;
  const { sanitizeProps: t, theme: r } = F(this, T, "f"), { bemClass: i } = r, { view: a2 } = F(this, _, "f"), { left: s, right: l } = F(this, E, "f").controller.get.defaults, { leftTree: n2, rightTree: f$1 } = F(this, E, "f").elements.jsx, { isLeftPanelOpened: c, isRightPanelOpened: h, lfShape: p, lfView: d, leftShape: u, rightShape: m } = this, b = ((_a = s == null ? void 0 : s[p]) == null ? void 0 : _a.call(s)) || [], g = [];
  for (let e = 0; e < b.length; e++) g.push(t(b[e]));
  const w2 = ((_b = l == null ? void 0 : l[p]) == null ? void 0 : _b.call(l)) || [], k2 = [];
  for (let e = 0; e < w2.length; e++) k2.push(t(w2[e]));
  return D$1(jt, null, D$1("div", { class: i(a2._, null, { [d]: true }) }, D$1("div", { class: i(a2._, a2.left) }, D$1(f, { cell: Object.assign(g, u), index: 0, shape: p, eventDispatcher: async (e) => this.onLfEvent(e, "lf-event"), framework: F(this, T, "f") })), c && n2(), h && f$1(), F(this, x, "m", P).call(this) && D$1("div", { class: i(a2._, a2.slider), onChange: F(this, R, "f"), onInput: F(this, R, "f") }, D$1("input", { class: i(a2._, a2.input), "data-cy": F(this, C, "f").input, min: "0", max: "100", type: "range", value: "50" })), D$1("div", { class: i(a2._, a2.right) }, D$1(f, { cell: Object.assign(k2, m), index: 1, shape: p, eventDispatcher: async (e) => this.onLfEvent(e, "lf-event"), framework: F(this, T, "f") }))));
}, Y.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-compare-font-family, var(--lf-font-family-primary));font-size:var(--lf-compare-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}.compare{width:100%;height:100%}.compare__grid{width:100%;height:100%;display:grid;grid-template-rows:var(--lf-comp-grid-template, 1fr auto);position:relative;user-select:none}.toolbar{border:0;border-style:solid;border-radius:var(--lf-compare-border-radius, var(--lf-ui-border-radius));border-top-left-radius:0;border-top-right-radius:0;background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);box-sizing:border-box;display:flex;justify-content:var(--lf-compare-toolbar-justify, space-between);padding:var(--lf-compare-toolbar-padding, 0.5em);width:var(--lf-compare-toolbar-width, 100%)}.toolbar__panel{border:0;border-style:solid;border-color:rgba(var(--lf-compare-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-compare-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-compare-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);bottom:0;height:var(--lf-compare-panel-height, auto);max-height:var(--lf-compare-panel-max-height, 50%);overflow:auto;position:absolute;width:var(--lf-compare-panel-width, 50%);z-index:var(--lf-compare-panel-z-index, var(--lf-ui-zindex-portal))}.toolbar__panel--left{left:0}.toolbar__panel--right{right:0}.view{width:100%;height:100%;position:relative}.view--main>:first-child{width:100%;height:100%;position:relative}.view--main>:last-child{width:100%;height:100%;clip-path:inset(0 var(--lf_compare_overlay_width, 50%) 0 0);left:0;overflow:hidden;position:absolute;top:0}.view--main>:last-child:after{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.5);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);content:"";height:100%;pointer-events:none;position:absolute;right:var(--lf_compare_overlay_width, 50%);top:0;width:var(--lf-compare-slider-thickness, 3px)}.view--split{display:grid;grid-template-columns:50% 50%;overflow:hidden}.view__slider{width:100%;height:100%;left:0;position:absolute;top:0;touch-action:pan-y;z-index:2}.view__input{width:100%;height:100%;appearance:none;background:transparent;cursor:grab;margin:0;pointer-events:all;z-index:1}.view__input::-webkit-slider-thumb{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);appearance:none;cursor:ew-resize;height:100%;margin:0;width:10px}.view__input::-moz-slider-thumb{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);appearance:none;cursor:ew-resize;height:100%;margin:0;width:10px}';
export {
  Y as lf_compare
};
