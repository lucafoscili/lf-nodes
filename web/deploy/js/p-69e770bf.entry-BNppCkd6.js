import { o, V as V$1, a_ as LF_COMPARE_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, a$ as LF_COMPARE_PARTS, c as LF_STYLE_ID, b0 as LF_COMPARE_CSS_VARS, d as LF_WRAPPER_ID, b1 as LF_COMPARE_DEFAULTS, b2 as LF_COMPARE_PROPS, m as mt, U as U$1, A as A$1, T as T$1, k as kt, b3 as LF_COMPARE_IDS } from "./index-F8Z50_1c.js";
import { o as o$1 } from "./p-c236cf18-BGzPQ9rm.js";
import { f } from "./p-d7fe17a6-BcBLxoIg.js";
const w = (e, t, r) => {
  const i = { nodes: [] };
  for (let a = 0; a < r.length; a++) {
    const s = r[a], o2 = String(a).valueOf();
    i.nodes.push({ icon: e === s && t, id: o2, value: `#${o2}` });
  }
  return i;
}, k = (e) => ({ ...e, defaults: LF_COMPARE_DEFAULTS() }), y = (t) => /* @__PURE__ */ ((t2) => ({ changeView: () => {
  const { controller: r, elements: i, handlers: a } = t2(), { cyAttributes: s, isOverlay: o2, manager: n, parts: c } = r.get, { refs: f2 } = i, { button: h } = a, { assignRef: p, theme: d } = n, { columns2: u, squareToggle: b } = d.get.icons();
  return U$1("lf-button", { "data-cy": s.button, id: LF_COMPARE_IDS.changeView, lfIcon: b, lfIconOff: u, lfStyling: "icon", lfToggable: true, lfValue: !o2(), "onLf-button-event": h, part: c.changeView, ref: p(f2, "changeView"), title: o2() ? "Click for split screen comparison." : "Click for overlay comparison" });
}, leftButton: () => {
  const { controller: r, elements: i, handlers: a } = t2(), { cyAttributes: s, isOverlay: o2, manager: n, parts: c } = r.get, { refs: f2 } = i, { button: h } = a, { assignRef: p, theme: d } = n, u = d.get.icon("imageInPicture"), { "--lf-icon-clear": b } = d.get.current().variables;
  return U$1("lf-button", { "data-cy": s.button, id: LF_COMPARE_IDS.leftButton, lfIcon: b, lfIconOff: u, lfStyling: "icon", lfToggable: true, "onLf-button-event": h, part: c.leftButton, ref: p(f2, "leftButton"), title: o2() ? "Click to open the left panel." : "Click to close the left panel." });
}, leftTree: () => {
  const { controller: r, elements: i, handlers: a } = t2(), { blocks: s, compInstance: o2, lfAttributes: n, manager: c, parts: f2, shapes: h } = r.get, { refs: p } = i, { tree: d } = a, { assignRef: u, theme: b } = c, { bemClass: m, get: g } = b, { "--lf-icon-success": v } = g.current().variables, k2 = o2;
  return U$1("lf-tree", { class: m(s.toolbar._, s.toolbar.panel, { left: true }), "data-lf": n.fadeIn, id: LF_COMPARE_IDS.leftTree, lfDataset: w(k2.leftShape, v, h()), lfFilter: false, "onLf-tree-event": d, part: f2.leftTree, ref: u(p, "leftTree") });
}, rightButton: () => {
  const { controller: r, elements: i, handlers: a } = t2(), { cyAttributes: s, isOverlay: o2, manager: n, parts: c } = r.get, { refs: f2 } = i, { button: h } = a, { assignRef: p, theme: d } = n, u = d.get.icon("imageInPicture"), { "--lf-icon-clear": b } = d.get.current().variables;
  return U$1("lf-button", { "data-cy": s.button, id: LF_COMPARE_IDS.rightButton, lfIcon: b, lfIconOff: u, lfStyling: "icon", lfToggable: true, "onLf-button-event": h, part: c.rightButton, ref: p(f2, "rightButton"), title: o2() ? "Click to open the right panel." : "Click to close the right panel." });
}, rightTree: () => {
  const { controller: r, elements: i, handlers: a } = t2(), { blocks: s, compInstance: o2, lfAttributes: n, manager: c, parts: f2, shapes: h } = r.get, { refs: p } = i, { tree: d } = a, { assignRef: u, theme: b } = c, { bemClass: m, get: g } = b, { "--lf-icon-success": v } = g.current().variables, k2 = o2;
  return U$1("lf-tree", { class: m(s.toolbar._, s.toolbar.panel, { right: true }), "data-lf": n.fadeIn, id: LF_COMPARE_IDS.rightTree, lfDataset: w(k2.rightShape, v, h()), lfFilter: false, "onLf-tree-event": d, part: f2.rightTree, ref: u(p, "rightTree") });
} }))(t), z = (e) => /* @__PURE__ */ ((e2) => ({ button: (t) => {
  const { eventType: r, id: i, valueAsBoolean: a } = t.detail, { set: s } = e2().controller, { leftButton: o2, changeView: n, rightButton: c } = LF_COMPARE_IDS;
  if ("click" === r) switch (i) {
    case o2:
      s.leftPanelOpened(a);
      break;
    case n:
      s.splitView(a);
      break;
    case c:
      s.rightPanelOpened(a);
  }
}, tree: (t) => {
  const { eventType: r, id: i, node: a } = t.detail, { get: s, set: o2 } = e2().controller, { shapes: n } = s, { leftTree: c, rightTree: f2 } = LF_COMPARE_IDS;
  if ("click" === r) {
    const e3 = n()[parseInt(a.id)];
    switch (i) {
      case c:
        o2.leftShape(e3);
        break;
      case f2:
        o2.rightShape(e3);
    }
  }
} }))(e);
var x, T, _, C, I, S, O, W, E, L, M, j, B, P, A, D, R, V, F = function(e, t, r, i) {
  if ("a" === r && !i) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !i : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === r ? i : "a" === r ? i.call(e) : i ? i.value : t.get(e);
}, H = function(e, t, r, i, a) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, r), r;
};
const $ = class {
  constructor(e) {
    o(this, e), this.lfEvent = V$1(this, "lf-compare-event"), x.add(this), this.isLeftPanelOpened = false, this.isRightPanelOpened = false, this.shapes = {}, this.lfDataset = null, this.lfShape = "image", this.lfStyle = "", this.lfView = "main", T.set(this, void 0), _.set(this, LF_COMPARE_BLOCKS), C.set(this, CY_ATTRIBUTES), I.set(this, LF_ATTRIBUTES), S.set(this, LF_COMPARE_PARTS), O.set(this, LF_STYLE_ID), W.set(this, LF_COMPARE_CSS_VARS), E.set(this, LF_WRAPPER_ID), L.set(this, void 0), M.set(this, () => {
      var e2, t, r;
      H(this, L, (e2 = { blocks: F(this, _, "f"), compInstance: this, cyAttributes: F(this, C, "f"), isOverlay: () => F(this, x, "m", P).call(this), lfAttributes: F(this, I, "f"), manager: F(this, T, "f"), parts: F(this, S, "f"), shapes: () => F(this, x, "m", j).call(this) }, t = { leftPanelOpened: (e3) => {
        this.isLeftPanelOpened = void 0 === e3 ? !this.isLeftPanelOpened : e3;
      }, leftShape: (e3) => this.leftShape = e3, rightPanelOpened: (e3) => {
        this.isRightPanelOpened = void 0 === e3 ? !this.isRightPanelOpened : e3;
      }, rightShape: (e3) => this.rightShape = e3, splitView: (e3) => {
        this.lfView = e3 ? "split" : "main";
      } }, r = () => F(this, L, "f"), { controller: { get: k(e2), set: t }, elements: { jsx: y(r), refs: { changeView: null, leftButton: null, leftTree: null, rightButton: null, rightTree: null, slider: null } }, handlers: z(r) }));
    }), V.set(this, (e2) => {
      const { target: t } = e2;
      if (t instanceof HTMLInputElement) {
        const e3 = 100 - parseInt(t.value);
        this.rootElement.style.setProperty(F(this, W, "f").overlayWidth, `${e3}%`);
      }
    });
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e });
  }
  async updateShapes() {
    if (!F(this, T, "f")) return;
    const { data: e, debug: t } = F(this, T, "f");
    try {
      this.shapes = e.cell.shapes.getAll(this.lfDataset);
      const t2 = F(this, x, "m", j).call(this);
      this.leftShape = t2[0], this.rightShape = t2[1];
    } catch (e2) {
      t.logs.new(this, "Error updating shapes: " + e2, "error");
    }
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_COMPARE_PROPS.map((e2) => [e2, this[e2]]);
    return Object.fromEntries(e);
  }
  async refresh() {
    mt(this);
  }
  async unmount(e = 0) {
    setTimeout(() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, e);
  }
  connectedCallback() {
    F(this, T, "f") && F(this, T, "f").theme.register(this);
  }
  async componentWillLoad() {
    H(this, T, await o$1(this)), F(this, M, "f").call(this), this.updateShapes();
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
    return U$1(A$1, { key: "ea73e8d15207f492eb2d3a107a239481c0f40ce0" }, s && U$1("style", { key: "cd91b19576b0e818d31758975cf003d410823728", id: F(this, O, "f") }, r(this)), U$1("div", { key: "c10e9b1c2b198ac3bc82b7cbb80608c224b71bcd", id: F(this, E, "f") }, U$1("div", { key: "d758cb449daaa602ec16c4c03cc03e8143a20c3d", class: t(i._), part: F(this, S, "f").compare }, F(this, x, "m", A).call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = F(this, T, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return T$1(this);
  }
  static get watchers() {
    return { lfDataset: ["updateShapes"], lfShape: ["updateShapes"] };
  }
};
T = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakMap(), S = /* @__PURE__ */ new WeakMap(), O = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), L = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), V = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakSet(), j = function() {
  var _a;
  return ((_a = this.shapes) == null ? void 0 : _a[this.lfShape]) || [];
}, B = function() {
  var _a;
  return !!((_a = this.shapes) == null ? void 0 : _a[this.lfShape]);
}, P = function() {
  return !("main" !== this.lfView);
}, A = function() {
  const { bemClass: t } = F(this, T, "f").theme, { compare: r } = F(this, _, "f");
  if (F(this, x, "m", B).call(this)) {
    const i = this.shapes[this.lfShape];
    if ((i == null ? void 0 : i.length) > 1) return U$1("div", { class: t(r._, r.grid) }, F(this, x, "m", R).call(this), F(this, x, "m", D).call(this));
  }
  return null;
}, D = function() {
  const { bemClass: t } = F(this, T, "f").theme, { toolbar: r } = F(this, _, "f"), { changeView: i, leftButton: a, rightButton: s } = F(this, L, "f").elements.jsx;
  return U$1("div", { class: t(r._) }, a(), i(), s());
}, R = function() {
  var _a, _b;
  const { sanitizeProps: t, theme: r } = F(this, T, "f"), { bemClass: i } = r, { view: a } = F(this, _, "f"), { left: s, right: l } = F(this, L, "f").controller.get.defaults, { leftTree: n, rightTree: c } = F(this, L, "f").elements.jsx, { isLeftPanelOpened: f$1, isRightPanelOpened: h, lfShape: p, lfView: d, leftShape: u, rightShape: b } = this, m = ((_a = s == null ? void 0 : s[p]) == null ? void 0 : _a.call(s)) || [], g = [];
  for (let e = 0; e < m.length; e++) g.push(t(m[e]));
  const w2 = ((_b = l == null ? void 0 : l[p]) == null ? void 0 : _b.call(l)) || [], k2 = [];
  for (let e = 0; e < w2.length; e++) k2.push(t(w2[e]));
  return U$1(kt, null, U$1("div", { class: i(a._, null, { [d]: true }) }, U$1("div", { class: i(a._, a.left) }, U$1(f, { cell: Object.assign(g, u), index: 0, shape: p, eventDispatcher: async (e) => this.onLfEvent(e, "lf-event"), framework: F(this, T, "f") })), f$1 && n(), h && c(), F(this, x, "m", P).call(this) && U$1("div", { class: i(a._, a.slider), onChange: F(this, V, "f"), onInput: F(this, V, "f") }, U$1("input", { class: i(a._, a.input), "data-cy": F(this, C, "f").input, min: "0", max: "100", type: "range", value: "50" })), U$1("div", { class: i(a._, a.right) }, U$1(f, { cell: Object.assign(k2, b), index: 1, shape: p, eventDispatcher: async (e) => this.onLfEvent(e, "lf-event"), framework: F(this, T, "f") }))));
}, $.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-compare-font-family, var(--lf-font-family-primary));font-size:var(--lf-compare-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-compare-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}.compare{width:100%;height:100%}.compare__grid{width:100%;height:100%;display:grid;grid-template-rows:var(--lf-comp-grid-template, 1fr auto);position:relative;user-select:none}.toolbar{border:0;border-style:solid;border-radius:var(--lf-compare-border-radius, var(--lf-ui-border-radius));border-top-left-radius:0;border-top-right-radius:0;background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);box-sizing:border-box;display:flex;justify-content:var(--lf-compare-toolbar-justify, space-between);padding:var(--lf-compare-toolbar-padding, 0.5em);width:var(--lf-compare-toolbar-width, 100%)}.toolbar__panel{border:0;border-style:solid;border-color:rgba(var(--lf-compare-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-compare-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-compare-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);bottom:0;height:var(--lf-compare-panel-height, auto);max-height:var(--lf-compare-panel-max-height, 50%);overflow:auto;position:absolute;width:var(--lf-compare-panel-width, 50%);z-index:var(--lf-compare-panel-z-index, var(--lf-ui-zindex-portal))}.toolbar__panel--left{left:0}.toolbar__panel--right{right:0}.view{width:100%;height:100%;position:relative}.view--main>:first-child{width:100%;height:100%;position:relative}.view--main>:last-child{width:100%;height:100%;clip-path:inset(0 var(--lf_compare_overlay_width, 50%) 0 0);left:0;overflow:hidden;position:absolute;top:0}.view--main>:last-child:after{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.5);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);content:"";height:100%;pointer-events:none;position:absolute;right:var(--lf_compare_overlay_width, 50%);top:0;width:var(--lf-compare-slider-thickness, 3px)}.view--split{display:grid;grid-template-columns:50% 50%;overflow:hidden}.view__slider{width:100%;height:100%;left:0;position:absolute;top:0;touch-action:pan-y;z-index:2}.view__input{width:100%;height:100%;appearance:none;background:transparent;cursor:grab;margin:0;pointer-events:all;z-index:1}.view__input::-webkit-slider-thumb{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);appearance:none;cursor:ew-resize;height:100%;margin:0;width:10px}.view__input::-moz-slider-thumb{background-color:rgba(var(--lf-compare-color-surface, var(--lf-color-surface)), 0.375);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);appearance:none;cursor:ew-resize;height:100%;margin:0;width:10px}';
export {
  $ as lf_compare
};
