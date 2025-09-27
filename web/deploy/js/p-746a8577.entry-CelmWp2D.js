import { n, I as I$1, j as LF_IMAGEVIEWER_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, l as LF_IMAGEVIEWER_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, o as LF_IMAGEVIEWER_PROPS, m as mt, W as W$1, f as L$1, G, p as IDS } from "./index-BemNYdu-.js";
import { o } from "./p-DklcdYZv-CETWN9aP.js";
const b = async (e, t = null) => {
  const { history: s } = e.controller.set;
  null === t ? (s.pop(), g(e)) : s.pop(t);
}, g = async (e) => {
  const { controller: t, elements: s } = e, { masonry: i } = s.refs.navigation, { set: a } = t;
  a.currentShape({}), a.history.index(null), i.setSelectedShape(null);
}, v = (e) => {
  const { compInstance: t, currentShape: s, manager: i } = e.controller.get, { lfDataset: a } = t, { getAll: n2 } = i.data.cell.shapes, r = s();
  return n2(a, false).image.find(((e2) => e2.value === r.value || e2.lfValue === r.value));
}, p = async (e, t) => {
  requestAnimationFrame((() => e.lfShowSpinner = true)), await t(), requestAnimationFrame((() => e.lfShowSpinner = false));
}, y = (e, t) => {
  const s = e;
  e.value = t, s.lfValue && (s.lfValue = t);
}, w = (t) => ({ canvas: () => {
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, history: l, lfAttribute: o2, manager: c } = s.get, { details: f } = i.refs, { canvas: d } = a.details, { currentSnapshot: h } = l, { assignRef: u, theme: m } = c, { bemClass: b2 } = m, g2 = h();
  if (g2) return W$1("lf-canvas", { class: b2(n2.detailsGrid._, n2.detailsGrid.canvas), "data-lf": o2.fadeIn, id: IDS.details.canvas, lfImageProps: { lfValue: g2.value }, "onLf-canvas-event": d, ref: u(f, "canvas") });
}, clearHistory: () => {
  var _a;
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, cyAttributes: l, history: o2, manager: c } = s.get, { details: f } = i.refs, { button: d } = a.details, { current: h } = o2, { assignRef: u, theme: m } = c, { bemClass: b2, get: g2 } = m, v2 = g2.icon("stackPop"), p2 = !(((_a = h()) == null ? void 0 : _a.length) > 1);
  return W$1("lf-button", { class: b2(n2.detailsGrid._, n2.detailsGrid.clearHistory), "data-cy": l.button, id: IDS.details.clearHistory, lfIcon: v2, lfLabel: "Clear history", lfStretchX: true, lfStyling: "flat", lfUiState: p2 ? "disabled" : "danger", "onLf-button-event": d, ref: u(f, "clearHistory") });
}, deleteShape: () => {
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, cyAttributes: l, manager: o2 } = s.get, { details: c } = i.refs, { button: f } = a.details, { assignRef: d, theme: h } = o2, { bemClass: u, get: m } = h, { "--lf-icon-clear": b2 } = m.current().variables;
  return W$1("lf-button", { class: u(n2.detailsGrid._, n2.detailsGrid.delete), "data-cy": l.button, id: IDS.details.deleteShape, lfIcon: b2, lfLabel: "Delete image", lfStretchX: true, lfUiState: "danger", "onLf-button-event": f, ref: d(c, "deleteShape") });
}, redo: () => {
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, cyAttributes: l, history: o2, manager: c } = s.get, { current: f, index: d } = o2, { details: h } = i.refs, { button: u } = a.details, { assignRef: m, theme: b2 } = c, { bemClass: g2, get: v2 } = b2, { "--lf-icon-next": p2 } = v2.current().variables, y2 = f(), w2 = !((y2 == null ? void 0 : y2.length) && d() < y2.length - 1);
  return W$1("lf-button", { class: g2(n2.detailsGrid._, n2.detailsGrid.redo), "data-cy": l.button, id: IDS.details.redo, lfIcon: p2, lfLabel: "Redo", lfStretchX: true, lfStyling: "flat", lfUiState: w2 ? "disabled" : "primary", "onLf-button-event": u, ref: m(h, "redo") });
}, save: () => {
  var _a;
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, cyAttributes: l, history: o2, manager: c } = s.get, { current: f } = o2, { details: d } = i.refs, { button: h } = a.details, { assignRef: u, theme: m } = c, { bemClass: b2, get: g2 } = m, { "--lf-icon-success": v2 } = g2.current().variables, p2 = !(((_a = f()) == null ? void 0 : _a.length) > 1);
  return W$1("lf-button", { class: b2(n2.detailsGrid._, n2.detailsGrid.commitChanges), "data-cy": l.button, id: IDS.details.save, lfIcon: v2, lfLabel: "Save snapshot", lfStretchX: true, lfUiState: p2 ? "disabled" : "success", "onLf-button-event": h, ref: u(d, "save") });
}, spinner: () => {
  const { controller: s, elements: i } = t(), { blocks: a, manager: n2, spinnerStatus: l } = s.get, { details: o2 } = i.refs, { assignRef: c, theme: f } = n2, { bemClass: d } = f;
  return W$1("lf-spinner", { class: d(a.detailsGrid._, a.detailsGrid.spinner), id: IDS.details.spinner, lfActive: l(), lfDimensions: "16px", lfFader: true, lfFaderTimeout: 125, lfLayout: 14, ref: c(o2, "save") });
}, tree: () => {
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, compInstance: l, cyAttributes: o2, manager: c } = s.get, { details: f } = i.refs, { tree: d } = a.details, { assignRef: h, theme: u } = c, { bemClass: m } = u;
  return W$1("lf-tree", { class: m(n2.detailsGrid._, n2.detailsGrid.tree), "data-cy": o2.input, id: IDS.details.tree, lfAccordionLayout: true, lfDataset: l.lfValue, lfFilter: false, lfSelectable: true, lfUiSize: "small", "onLf-tree-event": d, ref: h(f, "tree") });
}, undo: () => {
  var _a;
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, cyAttributes: l, history: o2, manager: c } = s.get, { current: f, index: d } = o2, { details: h } = i.refs, { button: u } = a.details, { assignRef: m, theme: b2 } = c, { bemClass: g2, get: v2 } = b2, { "--lf-icon-previous": p2 } = v2.current().variables, y2 = !(((_a = f()) == null ? void 0 : _a.length) && d() > 0);
  return W$1("lf-button", { class: g2(n2.detailsGrid._, n2.detailsGrid.undo), "data-cy": l.button, id: IDS.details.undo, lfIcon: p2, lfLabel: "Undo", lfStretchX: true, lfStyling: "flat", lfUiState: y2 ? "disabled" : "primary", "onLf-button-event": u, ref: m(h, "undo") });
} }), k = (t) => ({ load: () => {
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, cyAttributes: l, manager: o2 } = s.get, { navigation: c } = i.refs, { button: f } = a.navigation, { assignRef: d, theme: h } = o2, { bemClass: u } = h;
  return W$1("lf-button", { class: u(n2.navigationGrid._, n2.navigationGrid.button), "data-cy": l.button, id: IDS.navigation.load, lfLabel: "Load", lfStretchX: true, "onLf-button-event": f, ref: d(c, "load") }, W$1("lf-spinner", { lfActive: true, lfDimensions: "2px", lfLayout: 1, slot: "spinner" }));
}, masonry: () => {
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, compInstance: l, manager: o2 } = s.get, { navigation: c } = i.refs, { masonry: f } = a.navigation, { lfDataset: d } = l, { assignRef: h, theme: u } = o2, { bemClass: m } = u;
  return W$1("lf-masonry", { class: m(n2.navigationGrid._, n2.navigationGrid.masonry), id: IDS.navigation.masonry, lfActions: true, lfDataset: d, lfSelectable: true, "onLf-masonry-event": f, ref: h(c, "masonry") });
}, textfield: () => {
  const { controller: s, elements: i, handlers: a } = t(), { blocks: n2, cyAttributes: l, manager: o2 } = s.get, { navigation: c } = i.refs, { textfield: f } = a.navigation, { assignRef: d, theme: h } = o2, { bemClass: u } = h;
  return W$1("lf-textfield", { class: u(n2.navigationGrid._, n2.navigationGrid.textfield), "data-cy": l.input, id: IDS.navigation.textfield, lfIcon: "folder", lfLabel: "Directory", lfStretchX: true, lfStyling: "flat", "onLf-textfield-event": f, ref: d(c, "textfield") });
} }), x = (e) => ({ button: async (t) => {
  const { comp: s, eventType: i, id: a } = t.detail, n2 = e(), { compInstance: l, currentShape: o2 } = n2.controller.get;
  if (l.onLfEvent(t, "lf-event"), "click" === i) switch (a) {
    case IDS.details.clearHistory:
      const e2 = o2().shape.index;
      p(s, (async () => b(n2, e2)));
      break;
    case IDS.details.deleteShape:
      p(s, (() => (async (e3) => {
        const { compInstance: t2, currentShape: s2, manager: i2 } = e3.controller.get, { lfDataset: a2 } = t2, { findNodeByCell: n3, pop: r } = i2.data.node;
        await b(e3, s2().shape.index);
        const l2 = n3(a2, v(e3));
        r(a2.nodes, l2), t2.lfDataset = { ...a2 }, await g(e3);
      })(n2)));
      break;
    case IDS.details.redo:
      p(s, (() => (async (e3) => {
        const { controller: t2 } = e3, { get: s2, set: i2 } = t2, { current: a2, index: n3 } = s2.history, r = a2(), l2 = n3();
        r && l2 < r.length - 1 && i2.history.index(l2 + 1);
      })(n2)));
      break;
    case IDS.details.save:
      p(s, (() => (async (e3) => {
        const { compInstance: t2, currentShape: s2, history: i2 } = e3.controller.get, { lfDataset: a2 } = t2, n3 = s2();
        if (!n3) return;
        const r = n3.shape.index, l2 = n3.shape.shape, o3 = i2.currentSnapshot().value, c = v(e3);
        c.value = o3, c.lfValue = o3, y(l2, o3), await b(e3, r), t2.lfDataset = { ...a2 };
      })(n2)));
      break;
    case IDS.details.undo:
      p(s, (() => (async (e3) => {
        const { controller: t2 } = e3, { get: s2, set: i2 } = t2, { history: a2 } = s2, { index: n3 } = a2, r = n3();
        r > 0 && i2.history.index(r - 1);
      })(n2)));
  }
}, canvas: (t) => {
  const s = e(), { compInstance: i } = s.controller.get;
  i.onLfEvent(t, "lf-event");
}, tree: (t) => {
  const s = e(), { compInstance: i } = s.controller.get;
  i.onLfEvent(t, "lf-event");
} }), S = (e) => ({ button: async (t) => {
  const { comp: s, eventType: i } = t.detail, a = e(), { compInstance: n2 } = a.controller.get;
  n2.onLfEvent(t, "lf-event"), "click" === i && p(s, (() => (async (e2) => {
    const { controller: t2, elements: s2 } = e2, { textfield: i2 } = s2.refs.navigation, { compInstance: a2 } = t2.get, { lfLoadCallback: n3 } = a2;
    try {
      await n3(a2, await i2.getValue()), b(e2);
    } catch (e3) {
      console.error("Load operation failed:", e3);
    }
  })(a)));
}, masonry: (t) => {
  var _a;
  const { eventType: s, originalEvent: i, selectedShape: a } = t.detail, n2 = e(), { controller: r } = n2, { get: l, set: o2 } = r, { compInstance: c, history: f } = l, { current: d } = f;
  if (c.onLfEvent(t, "lf-event"), "lf-event" === s && "click" === i.detail.eventType) {
    const e2 = l.currentShape();
    if (((_a = e2 == null ? void 0 : e2.shape) == null ? void 0 : _a.index) === a.index) g(n2);
    else {
      o2.currentShape(a);
      const e3 = d();
      o2.history.index(e3 ? e3.length - 1 : 0), o2.history.new(a);
    }
  }
}, textfield: (t) => {
  const s = e(), { compInstance: i } = s.controller.get;
  i.onLfEvent(t, "lf-event");
} }), z = (e, t) => ({ ...e, spinnerStatus: (e2) => t().elements.refs.details.spinner.lfActive = e2 }), C = (e) => ({ details: w(e), navigation: k(e) }), L = (e) => ({ details: x(e), navigation: S(e) });
var I, A, _, D, R, W, E, T, M, j, H, U, X, P, F = function(e, t, s, i) {
  if ("a" === s && !i) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !i : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === s ? i : "a" === s ? i.call(e) : i ? i.value : t.get(e);
}, O = function(e, t, s, i, a) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, s), s;
};
const N = class {
  constructor(e) {
    n(this, e), this.lfEvent = I$1(this, "lf-imageviewer-event"), I.add(this), this.currentShape = {}, this.history = {}, this.historyIndex = null, this.isSpinnerActive = false, this.lfDataset = {}, this.lfLoadCallback = null, this.lfStyle = "", this.lfValue = {}, A.set(this, void 0), _.set(this, LF_IMAGEVIEWER_BLOCKS), D.set(this, CY_ATTRIBUTES), R.set(this, LF_ATTRIBUTES), W.set(this, LF_IMAGEVIEWER_PARTS), E.set(this, LF_STYLE_ID), T.set(this, LF_WRAPPER_ID), M.set(this, void 0), j.set(this, (() => {
      var e2;
      O(this, M, { controller: { get: { blocks: F(this, _, "f"), compInstance: this, currentShape: () => F(this, I, "m", H).call(this, this.currentShape), cyAttributes: F(this, D, "f"), history: { current: () => this.history[this.currentShape.index], currentSnapshot: () => {
        if (null === this.historyIndex) return null;
        const e3 = this.history[this.currentShape.index][this.historyIndex];
        return F(this, I, "m", H).call(this, e3);
      }, full: () => this.history, index: () => this.historyIndex }, lfAttribute: F(this, R, "f"), manager: F(this, A, "f"), parts: F(this, W, "f"), spinnerStatus: () => this.isSpinnerActive }, set: z({ currentShape: (e3) => this.currentShape = e3, history: { index: (e3) => this.historyIndex = e3, new: (e3, t = false) => {
        var _a;
        const s = ((_a = this.history) == null ? void 0 : _a[e3.index]) || [];
        this.historyIndex < s.length - 1 && s.splice(this.historyIndex + 1), !(s == null ? void 0 : s.length) || t ? (s.push(e3), this.history[e3.index] = s, this.historyIndex = s.length - 1) : s[0] = e3;
      }, pop: (e3 = null) => {
        null !== e3 ? (this.history[e3] = [this.history[e3][0]], 0 === this.historyIndex ? this.refresh() : this.historyIndex = 0) : (this.history = {}, this.historyIndex = null);
      } } }, e2 = () => F(this, M, "f")) }, elements: { jsx: C(e2), refs: { details: { canvas: null, clearHistory: null, deleteShape: null, redo: null, save: null, spinner: null, undo: null, tree: null }, navigation: { load: null, masonry: null, textfield: null } } }, handlers: L(e2) });
    }));
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e });
  }
  async addSnapshot(e) {
    var _a;
    const { currentShape: t } = this;
    if (!t || !((_a = Object.keys(t)) == null ? void 0 : _a.length)) return;
    const { history: s } = F(this, M, "f").controller.set, i = JSON.parse(JSON.stringify(t));
    y(i.shape, e), s.new(i, true);
  }
  async clearHistory(e = null) {
    await b(F(this, M, "f"), e);
  }
  async clearSelection() {
    await g(F(this, M, "f"));
  }
  async getComponents() {
    return F(this, M, "f").elements.refs;
  }
  async getCurrentSnapshot() {
    return F(this, M, "f").controller.get.history.currentSnapshot();
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_IMAGEVIEWER_PROPS.map(((e2) => [e2, this[e2]]));
    return Object.fromEntries(e);
  }
  async refresh() {
    mt(this);
  }
  async reset() {
    await b(F(this, M, "f")), await g(F(this, M, "f"));
  }
  async setSpinnerStatus(e) {
    this.isSpinnerActive = e;
  }
  async unmount(e = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), e);
  }
  connectedCallback() {
    F(this, A, "f") && F(this, A, "f").theme.register(this);
  }
  async componentWillLoad() {
    O(this, A, await o(this)), F(this, j, "f").call(this);
  }
  componentDidLoad() {
    const { info: e } = F(this, A, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = F(this, A, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = F(this, A, "f").debug;
    e.update(this, "did-render");
  }
  render() {
    const { bemClass: t, setLfStyle: s } = F(this, A, "f").theme, { lfStyle: i } = this;
    return W$1(L$1, { key: "8d61db92ca05782d25f678f92d84a62b47e003c8" }, i && W$1("style", { key: "6449523eeaffb30648b18bd7e1f2b26c8a9b3237", id: F(this, E, "f") }, s(this)), W$1("div", { key: "fe954b609a79b439a3c8da67cfa8eaaf630cc209", id: F(this, T, "f") }, W$1("div", { key: "9a36612905e1d9049db6363350c70155f8a27023", class: t(F(this, _, "f").imageviewer._), part: F(this, W, "f").imageviewer }, F(this, I, "m", X).call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = F(this, A, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return G(this);
  }
};
A = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), R = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), T = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), j = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakSet(), H = function(e) {
  const { data: t } = F(this, A, "f"), { cell: s } = t, { stringify: i } = s;
  return void 0 !== e.index ? { shape: e, value: i(e.shape.value || e.shape.lfValue) } : null;
}, U = function() {
  const { bemClass: t } = F(this, A, "f").theme, { detailsGrid: s } = F(this, _, "f"), { canvas: i, clearHistory: a, deleteShape: n2, redo: r, save: l, spinner: o2, tree: c, undo: f } = F(this, M, "f").elements.jsx.details;
  return W$1("div", { class: t(s._), part: F(this, W, "f").details }, W$1("div", { class: t(s._, s.preview) }, i(), o2()), W$1("div", { class: t(s._, s.actions) }, n2(), a(), f(), r(), l()), c(), W$1("div", { class: t(s._, s.settings) }, W$1("slot", { name: "settings" })));
}, X = function() {
  const { bemClass: t } = F(this, A, "f").theme, { currentShape: s } = F(this, M, "f").controller.get;
  return W$1("div", { class: t(F(this, _, "f").mainGrid._, null, { selected: !!s() }) }, F(this, I, "m", P).call(this), F(this, I, "m", U).call(this));
}, P = function() {
  const { bemClass: t } = F(this, A, "f").theme, { load: s, masonry: i, textfield: a } = F(this, M, "f").elements.jsx.navigation;
  return W$1("div", { class: t(F(this, _, "f").navigationGrid._), part: F(this, W, "f").navigation }, a(), s(), i());
}, N.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-imageviewer-font-family, var(--lf-font-family-primary));font-size:var(--lf-imageviewer-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{background-color:rgba(var(--lf-imageviewer-color-bg, var(--lf-color-bg)), 0.125);color:rgb(var(--lf-imageviewer-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);width:100%;height:100%}.imageviewer{width:100%;height:100%}.main-grid{border:0;border-style:solid;border-color:rgba(var(--lf-imageviewer-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-imageviewer-border-radius, var(--lf-ui-border-radius));width:100%;height:100%;box-sizing:border-box;display:grid;grid-template-columns:100% 0;overflow:auto}.main-grid--selected{grid-template-columns:30% 70%}.main-grid--selected .details-grid{display:grid}.navigation-grid{width:100%;height:100%;display:grid;grid-template-rows:auto auto 1fr;overflow:auto}.navigation-grid__textfield{padding:0}.navigation-grid__button{padding-bottom:0.75em}.navigation-grid__masonry{overflow:auto;position:relative}.details-grid{width:100%;height:100%;border-left:1px solid var(--lf-color-border);box-sizing:border-box;display:none;grid-template-areas:"image image" "actions actions" "tree settings";grid-template-columns:40% 1fr;grid-template-rows:60% auto 1fr;overflow:auto}.details-grid__actions{border-left:1px solid var(--lf-color-border);box-sizing:border-box;display:flex;grid-area:actions}.details-grid__canvas{border-bottom:1px solid var(--lf-color-border);box-sizing:border-box}.details-grid__preview{grid-area:image;position:relative}.details-grid__spinner{width:100%;height:100%;left:0;pointer-events:none;position:absolute;top:0}.details-grid__tree{border-right:1px solid var(--lf-color-border);box-sizing:border-box;grid-area:tree;overflow:auto}.details-grid__settings{grid-area:settings;overflow:auto}';
export {
  N as lf_imageviewer
};
