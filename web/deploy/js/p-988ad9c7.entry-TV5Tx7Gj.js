import { n, V, b0 as LF_IMAGEVIEWER_BLOCKS, C as CY_ATTRIBUTES, f as LF_ATTRIBUTES, b1 as LF_IMAGEVIEWER_PARTS, b as LF_STYLE_ID, c as LF_WRAPPER_ID, b2 as LF_IMAGEVIEWER_PROPS, p as pt, D as D$1, W as W$1, z as z$1, b3 as IDS } from "./index-KdsGGJBN.js";
import { a } from "./p-Dl9cVpAY-C31OpVB5.js";
const u = async (e, t = null) => {
  const { history: a2 } = e.controller.set;
  null === t ? (a2.pop(), b(e)) : a2.pop(t);
}, b = async (e) => {
  const { controller: t, elements: a2 } = e, { masonry: s } = a2.refs.navigation, { set: i } = t;
  i.currentShape({}), i.history.index(null), s.setSelectedShape(null);
}, v = (e) => {
  const { compInstance: t, currentShape: a2, manager: s } = e.controller.get, { lfDataset: i } = t, { getAll: n2 } = s.data.cell.shapes, r = a2();
  return n2(i, false).image.find(((e2) => e2.value === r.value || e2.lfValue === r.value));
}, p = async (e, t) => {
  requestAnimationFrame((() => e.lfShowSpinner = true)), await t(), requestAnimationFrame((() => e.lfShowSpinner = false));
}, y = (e, t) => {
  const a2 = e;
  e.value = t, a2.lfValue && (a2.lfValue = t);
}, w = (t) => ({ canvas: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, history: l, lfAttribute: o, manager: c } = a2.get, { details: f } = s.refs, { canvas: d } = i.details, { currentSnapshot: h } = l, { assignRef: g, theme: m } = c, { bemClass: u2 } = m, b2 = h();
  if (b2) return D$1("lf-canvas", { class: u2(n2.detailsGrid._, n2.detailsGrid.canvas), "data-lf": o.fadeIn, id: IDS.details.canvas, lfImageProps: { lfValue: b2.value }, "onLf-canvas-event": d, ref: g(f, "canvas") });
}, clearHistory: () => {
  var _a;
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, cyAttributes: l, history: o, manager: c } = a2.get, { details: f } = s.refs, { button: d } = i.details, { current: h } = o, { assignRef: g, theme: m } = c, { bemClass: u2, get: b2 } = m, v2 = b2.icon("stackPop"), p2 = !(((_a = h()) == null ? void 0 : _a.length) > 1);
  return D$1("lf-button", { class: u2(n2.detailsGrid._, n2.detailsGrid.clearHistory), "data-cy": l.button, id: IDS.details.clearHistory, lfIcon: v2, lfLabel: "Clear history", lfStretchX: true, lfStyling: "flat", lfUiState: p2 ? "disabled" : "danger", "onLf-button-event": d, ref: g(f, "clearHistory") });
}, deleteShape: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, cyAttributes: l, manager: o } = a2.get, { details: c } = s.refs, { button: f } = i.details, { assignRef: d, theme: h } = o, { bemClass: g, get: m } = h, { "--lf-icon-clear": u2 } = m.current().variables;
  return D$1("lf-button", { class: g(n2.detailsGrid._, n2.detailsGrid.delete), "data-cy": l.button, id: IDS.details.deleteShape, lfIcon: u2, lfLabel: "Delete image", lfStretchX: true, lfUiState: "danger", "onLf-button-event": f, ref: d(c, "deleteShape") });
}, redo: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, cyAttributes: l, history: o, manager: c } = a2.get, { current: f, index: d } = o, { details: h } = s.refs, { button: g } = i.details, { assignRef: m, theme: u2 } = c, { bemClass: b2, get: v2 } = u2, { "--lf-icon-next": p2 } = v2.current().variables, y2 = f(), w2 = !((y2 == null ? void 0 : y2.length) && d() < y2.length - 1);
  return D$1("lf-button", { class: b2(n2.detailsGrid._, n2.detailsGrid.redo), "data-cy": l.button, id: IDS.details.redo, lfIcon: p2, lfLabel: "Redo", lfStretchX: true, lfStyling: "flat", lfUiState: w2 ? "disabled" : "primary", "onLf-button-event": g, ref: m(h, "redo") });
}, save: () => {
  var _a;
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, cyAttributes: l, history: o, manager: c } = a2.get, { current: f } = o, { details: d } = s.refs, { button: h } = i.details, { assignRef: g, theme: m } = c, { bemClass: u2, get: b2 } = m, { "--lf-icon-success": v2 } = b2.current().variables, p2 = !(((_a = f()) == null ? void 0 : _a.length) > 1);
  return D$1("lf-button", { class: u2(n2.detailsGrid._, n2.detailsGrid.commitChanges), "data-cy": l.button, id: IDS.details.save, lfIcon: v2, lfLabel: "Save snapshot", lfStretchX: true, lfUiState: p2 ? "disabled" : "success", "onLf-button-event": h, ref: g(d, "save") });
}, spinner: () => {
  const { controller: a2, elements: s } = t(), { blocks: i, manager: n2, spinnerStatus: l } = a2.get, { details: o } = s.refs, { assignRef: c, theme: f } = n2, { bemClass: d } = f;
  return D$1("lf-spinner", { class: d(i.detailsGrid._, i.detailsGrid.spinner), id: IDS.details.spinner, lfActive: l(), lfDimensions: "16px", lfFader: true, lfFaderTimeout: 125, lfLayout: 14, ref: c(o, "save") });
}, tree: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, compInstance: l, cyAttributes: o, manager: c } = a2.get, { details: f } = s.refs, { tree: d } = i.details, { assignRef: h, theme: g } = c, { bemClass: m } = g;
  return D$1("lf-tree", { class: m(n2.detailsGrid._, n2.detailsGrid.tree), "data-cy": o.input, id: IDS.details.tree, lfAccordionLayout: true, lfDataset: l.lfValue, lfFilter: false, lfSelectable: true, lfUiSize: "small", "onLf-tree-event": d, ref: h(f, "tree") });
}, undo: () => {
  var _a;
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, cyAttributes: l, history: o, manager: c } = a2.get, { current: f, index: d } = o, { details: h } = s.refs, { button: g } = i.details, { assignRef: m, theme: u2 } = c, { bemClass: b2, get: v2 } = u2, { "--lf-icon-previous": p2 } = v2.current().variables, y2 = !(((_a = f()) == null ? void 0 : _a.length) && d() > 0);
  return D$1("lf-button", { class: b2(n2.detailsGrid._, n2.detailsGrid.undo), "data-cy": l.button, id: IDS.details.undo, lfIcon: p2, lfLabel: "Undo", lfStretchX: true, lfStyling: "flat", lfUiState: y2 ? "disabled" : "primary", "onLf-button-event": g, ref: m(h, "undo") });
} }), x = (t) => ({ load: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, cyAttributes: l, manager: o } = a2.get, { navigation: c } = s.refs, { button: f } = i.navigation, { assignRef: d, theme: h } = o, { bemClass: g } = h;
  return D$1("lf-button", { class: g(n2.navigationGrid._, n2.navigationGrid.button), "data-cy": l.button, id: IDS.navigation.load, lfLabel: "Load", lfStretchX: true, "onLf-button-event": f, ref: d(c, "load") }, D$1("lf-spinner", { lfActive: true, lfDimensions: "2px", lfLayout: 1, slot: "spinner" }));
}, masonry: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, compInstance: l, manager: o } = a2.get, { navigation: c } = s.refs, { masonry: f } = i.navigation, { lfDataset: d } = l, { assignRef: h, theme: g } = o, { bemClass: m } = g;
  return D$1("lf-masonry", { class: m(n2.navigationGrid._, n2.navigationGrid.masonry), id: IDS.navigation.masonry, lfActions: true, lfDataset: d, lfSelectable: true, "onLf-masonry-event": f, ref: h(c, "masonry") });
}, navToggle: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, cyAttributes: l, manager: o } = a2.get, { navigation: c } = s.refs, { navToggle: f } = i.navigation, { assignRef: d, theme: h } = o, { bemClass: g } = h, { "--lf-icon-next": m, "--lf-icon-previous": u2 } = h.get.current().variables, b2 = a2.get.navigation.isTreeOpen();
  return D$1("lf-button", { class: g(n2.navigationGrid._, n2.navigationGrid.navToggle), "data-cy": l.button, id: IDS.navigation.navToggle, lfAriaLabel: b2 ? "Collapse navigation tree" : "Expand navigation tree", lfIcon: b2 ? u2 : m, lfStretchY: true, "onLf-button-event": f, ref: d(c, "navToggle"), title: b2 ? "Collapse" : "Expand" });
}, textfield: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, cyAttributes: l, manager: o } = a2.get, { navigation: c } = s.refs, { textfield: f } = i.navigation, { assignRef: d, theme: h } = o, { bemClass: g } = h;
  return D$1("lf-textfield", { class: g(n2.navigationGrid._, n2.navigationGrid.textfield), "data-cy": l.input, id: IDS.navigation.textfield, lfIcon: "folder", lfLabel: "Directory", lfStretchX: true, lfStyling: "flat", "onLf-textfield-event": f, ref: d(c, "textfield") });
}, tree: () => {
  const { controller: a2, elements: s, handlers: i } = t(), { blocks: n2, compInstance: l, manager: o } = a2.get, { navigation: c } = s.refs, { tree: f } = i.navigation, { assignRef: d, sanitizeProps: h, theme: g } = o, { bemClass: m } = g, u2 = l.lfNavigation || {};
  return D$1("lf-tree", { class: m(n2.navigationGrid._, n2.navigationGrid.tree), id: IDS.navigation.tree, "onLf-tree-event": f, ref: d(c, "tree"), ...h(u2.treeProps, "LfTree") });
} }), k = (e) => ({ button: async (t) => {
  const { comp: a2, eventType: s, id: i } = t.detail, n2 = e(), { compInstance: l, currentShape: o } = n2.controller.get;
  if (l.onLfEvent(t, "lf-event"), "click" === s) switch (i) {
    case IDS.details.clearHistory:
      const e2 = o().shape.index;
      p(a2, (async () => u(n2, e2)));
      break;
    case IDS.details.deleteShape:
      p(a2, (() => (async (e3) => {
        const { compInstance: t2, currentShape: a3, manager: s2 } = e3.controller.get, { lfDataset: i2 } = t2, { findNodeByCell: n3, pop: r } = s2.data.node;
        await u(e3, a3().shape.index);
        const l2 = n3(i2, v(e3));
        r(i2.nodes, l2), t2.lfDataset = { ...i2 }, await b(e3);
      })(n2)));
      break;
    case IDS.details.redo:
      p(a2, (() => (async (e3) => {
        const { controller: t2 } = e3, { get: a3, set: s2 } = t2, { current: i2, index: n3 } = a3.history, r = i2(), l2 = n3();
        r && l2 < r.length - 1 && s2.history.index(l2 + 1);
      })(n2)));
      break;
    case IDS.details.save:
      p(a2, (() => (async (e3) => {
        const { compInstance: t2, currentShape: a3, history: s2 } = e3.controller.get, { lfDataset: i2 } = t2, n3 = a3();
        if (!n3) return;
        const r = n3.shape.index, l2 = n3.shape.shape, o2 = s2.currentSnapshot().value, c = v(e3);
        c.value = o2, c.lfValue = o2, y(l2, o2), await u(e3, r), t2.lfDataset = { ...i2 };
      })(n2)));
      break;
    case IDS.details.undo:
      p(a2, (() => (async (e3) => {
        const { controller: t2 } = e3, { get: a3, set: s2 } = t2, { history: i2 } = a3, { index: n3 } = i2, r = n3();
        r > 0 && s2.history.index(r - 1);
      })(n2)));
  }
}, canvas: (t) => {
  const a2 = e(), { compInstance: s } = a2.controller.get;
  s.onLfEvent(t, "lf-event");
}, tree: (t) => {
  const a2 = e(), { compInstance: s } = a2.controller.get;
  s.onLfEvent(t, "lf-event");
} }), z = (e) => ({ button: async (t) => {
  const { comp: a2, eventType: s } = t.detail, i = e(), { compInstance: n2 } = i.controller.get;
  n2.onLfEvent(t, "lf-event"), "click" === s && p(a2, (() => (async (e2) => {
    const { controller: t2, elements: a3 } = e2, { textfield: s2 } = a3.refs.navigation, { compInstance: i2 } = t2.get, { lfLoadCallback: n3 } = i2;
    try {
      await n3(i2, await s2.getValue()), u(e2);
    } catch (e3) {
      console.error("Load operation failed:", e3);
    }
  })(i)));
}, masonry: (t) => {
  var _a;
  const { eventType: a2, originalEvent: s, selectedShape: i } = t.detail, n2 = e(), { controller: r } = n2, { get: l, set: o } = r, { compInstance: c, history: f } = l, { current: d } = f;
  if (c.onLfEvent(t, "lf-event"), "lf-event" === a2 && "click" === s.detail.eventType) {
    const e2 = l.currentShape();
    if (((_a = e2 == null ? void 0 : e2.shape) == null ? void 0 : _a.index) === i.index) b(n2);
    else {
      o.currentShape(i);
      const e3 = d();
      o.history.index(e3 ? e3.length - 1 : 0), o.history.new(i);
    }
  }
}, navToggle: (t) => {
  const { eventType: a2 } = t.detail, s = e(), { controller: i } = s, { get: n2, set: r } = i, { compInstance: l } = n2;
  l.onLfEvent(t, "lf-event"), "click" === a2 && r.navigation.toggleTree();
}, textfield: (t) => {
  const a2 = e(), { compInstance: s } = a2.controller.get;
  s.onLfEvent(t, "lf-event");
}, tree: (t) => {
  const a2 = e(), { compInstance: s } = a2.controller.get;
  s.onLfEvent(t, "lf-event");
} }), S = (e, t) => ({ ...e, spinnerStatus: (e2) => t().elements.refs.details.spinner.lfActive = e2 }), L = (e) => ({ details: w(e), navigation: x(e) }), C = (e) => ({ details: k(e), navigation: z(e) });
var _, I, T, A, R, D, E, W, M, j, H, P, U, X, O = function(e, t, a2, s) {
  if ("a" === a2 && !s) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !s : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === a2 ? s : "a" === a2 ? s.call(e) : s ? s.value : t.get(e);
}, B = function(e, t, a2, s, i) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, a2), a2;
};
const F = class {
  constructor(e) {
    n(this, e), this.lfEvent = V(this, "lf-imageviewer-event"), _.add(this), this.currentShape = {}, this.history = {}, this.historyIndex = null, this.isNavigationTreeOpen = false, this.isSpinnerActive = false, this.lfDataset = {}, this.lfLoadCallback = null, this.lfStyle = "", this.lfValue = {}, I.set(this, void 0), T.set(this, LF_IMAGEVIEWER_BLOCKS), A.set(this, CY_ATTRIBUTES), R.set(this, LF_ATTRIBUTES), D.set(this, LF_IMAGEVIEWER_PARTS), E.set(this, LF_STYLE_ID), W.set(this, LF_WRAPPER_ID), M.set(this, void 0), j.set(this, (() => {
      var e2;
      B(this, M, { controller: { get: { blocks: O(this, T, "f"), compInstance: this, currentShape: () => O(this, _, "m", H).call(this, this.currentShape), cyAttributes: O(this, A, "f"), history: { current: () => this.history[this.currentShape.index], currentSnapshot: () => {
        if (null === this.historyIndex) return null;
        const e3 = this.history[this.currentShape.index][this.historyIndex];
        return O(this, _, "m", H).call(this, e3);
      }, full: () => this.history, index: () => this.historyIndex }, lfAttribute: O(this, R, "f"), manager: O(this, I, "f"), navigation: { hasNav: () => {
        var _a, _b;
        return Boolean((_b = (_a = this.lfNavigation) == null ? void 0 : _a.treeProps) == null ? void 0 : _b.lfDataset);
      }, isTreeOpen: () => this.isNavigationTreeOpen }, parts: O(this, D, "f"), spinnerStatus: () => this.isSpinnerActive }, set: S({ currentShape: (e3) => this.currentShape = e3, history: { index: (e3) => this.historyIndex = e3, new: (e3, t = false) => {
        var _a;
        const a2 = ((_a = this.history) == null ? void 0 : _a[e3.index]) || [];
        this.historyIndex < a2.length - 1 && a2.splice(this.historyIndex + 1), !(a2 == null ? void 0 : a2.length) || t ? (a2.push(e3), this.history[e3.index] = a2, this.historyIndex = a2.length - 1) : a2[0] = e3;
      }, pop: (e3 = null) => {
        null !== e3 ? (this.history[e3] = [this.history[e3][0]], 0 === this.historyIndex ? this.refresh() : this.historyIndex = 0) : (this.history = {}, this.historyIndex = null);
      } }, navigation: { isTreeOpen: (e3) => {
        this.isNavigationTreeOpen = e3;
      }, toggleTree: () => {
        this.isNavigationTreeOpen = !this.isNavigationTreeOpen;
      } } }, e2 = () => O(this, M, "f")) }, elements: { jsx: L(e2), refs: { details: { canvas: null, clearHistory: null, deleteShape: null, redo: null, save: null, spinner: null, undo: null, tree: null }, navigation: { load: null, masonry: null, navToggle: null, tree: null, textfield: null } } }, handlers: C(e2) });
    }));
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e });
  }
  async addSnapshot(e) {
    var _a;
    const { currentShape: t } = this;
    if (!t || !((_a = Object.keys(t)) == null ? void 0 : _a.length)) return;
    const { history: a2 } = O(this, M, "f").controller.set, s = JSON.parse(JSON.stringify(t));
    y(s.shape, e), a2.new(s, true);
  }
  async clearHistory(e = null) {
    await u(O(this, M, "f"), e);
  }
  async clearSelection() {
    await b(O(this, M, "f"));
  }
  async getComponents() {
    return O(this, M, "f").elements.refs;
  }
  async getCurrentSnapshot() {
    return O(this, M, "f").controller.get.history.currentSnapshot();
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_IMAGEVIEWER_PROPS.map(((e2) => [e2, this[e2]]));
    return Object.fromEntries(e);
  }
  async refresh() {
    pt(this);
  }
  async reset() {
    await u(O(this, M, "f")), await b(O(this, M, "f"));
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
    O(this, I, "f") && O(this, I, "f").theme.register(this);
  }
  async componentWillLoad() {
    B(this, I, await a(this)), O(this, j, "f").call(this), O(this, M, "f").controller.get.navigation.hasNav() && (this.isNavigationTreeOpen = true);
  }
  componentDidLoad() {
    const { info: e } = O(this, I, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = O(this, I, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = O(this, I, "f").debug;
    e.update(this, "did-render");
  }
  render() {
    const { bemClass: t, setLfStyle: a2 } = O(this, I, "f").theme, { lfStyle: s } = this;
    return D$1(W$1, { key: "fbd19d0e1e615d75bbc7158fc9f9733dee8f350e" }, s && D$1("style", { key: "d1bb9217fe9805fbe843e672e56a2cf7d606b6f5", id: O(this, E, "f") }, a2(this)), D$1("div", { key: "d40bd5f1c362aa925e808d0cc889d0ce021b5d3d", id: O(this, W, "f") }, D$1("div", { key: "18f1b3febb27f6919d4a62590f87e3515212dd6c", class: t(O(this, T, "f").imageviewer._), part: O(this, D, "f").imageviewer }, O(this, _, "m", U).call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = O(this, I, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return z$1(this);
  }
};
I = /* @__PURE__ */ new WeakMap(), T = /* @__PURE__ */ new WeakMap(), A = /* @__PURE__ */ new WeakMap(), R = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), j = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakSet(), H = function(e) {
  const { data: t } = O(this, I, "f"), { cell: a2 } = t, { stringify: s } = a2;
  return void 0 !== e.index ? { shape: e, value: s(e.shape.value || e.shape.lfValue) } : null;
}, P = function() {
  const { bemClass: t } = O(this, I, "f").theme, { detailsGrid: a2 } = O(this, T, "f"), { canvas: s, clearHistory: i, deleteShape: n2, redo: r, save: l, spinner: o, tree: c, undo: f } = O(this, M, "f").elements.jsx.details;
  return D$1("div", { class: t(a2._), part: O(this, D, "f").details }, D$1("div", { class: t(a2._, a2.preview) }, s(), o()), D$1("div", { class: t(a2._, a2.actions) }, n2(), i(), f(), r(), l()), c(), D$1("div", { class: t(a2._, a2.settings) }, D$1("slot", { name: "settings" })));
}, U = function() {
  const { bemClass: t } = O(this, I, "f").theme, { currentShape: a2 } = O(this, M, "f").controller.get;
  return D$1("div", { class: t(O(this, T, "f").mainGrid._, null, { selected: !!a2() }) }, O(this, _, "m", X).call(this), O(this, _, "m", P).call(this));
}, X = function() {
  var _a, _b, _c, _d;
  const { bemClass: t } = O(this, I, "f").theme, { load: a2, masonry: s, navToggle: i, textfield: n2, tree: r } = O(this, M, "f").elements.jsx.navigation, l = O(this, T, "f").navigationGrid, o = Boolean((_b = (_a = this.lfNavigation) == null ? void 0 : _a.treeProps) == null ? void 0 : _b.lfDataset) && Boolean((_d = (_c = this.lfNavigation) == null ? void 0 : _c.treeProps) == null ? void 0 : _d.lfDataset), c = t(l._, void 0, { "has-drawer": o && this.isNavigationTreeOpen, "has-nav": o });
  return D$1("div", { class: c, part: O(this, D, "f").navigation }, r(), i(), n2(), a2(), s());
}, F.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-imageviewer-font-family, var(--lf-font-family-primary));font-size:var(--lf-imageviewer-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{background-color:rgba(var(--lf-imageviewer-color-bg, var(--lf-color-bg)), 0.125);color:rgb(var(--lf-imageviewer-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);width:100%;height:100%}.imageviewer{width:100%;height:100%}.main-grid{border:0;border-style:solid;border-color:rgba(var(--lf-imageviewer-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-imageviewer-border-radius, var(--lf-ui-border-radius));width:100%;height:100%;box-sizing:border-box;display:grid;grid-template-columns:100% 0;overflow:auto}.main-grid--selected{grid-template-columns:30% 70%}.main-grid--selected .details-grid{display:grid}.navigation-grid{width:100%;height:100%;box-sizing:border-box;display:grid;grid-template-areas:"textfield" "button" "masonry";grid-template-columns:1fr;grid-template-rows:repeat(2, auto) 1fr;overflow:hidden}.navigation-grid--has-nav{grid-template-areas:"nav-toggle textfield" "nav-toggle button" "nav-toggle masonry";grid-template-columns:auto 1fr}.navigation-grid--has-nav .navigation-grid__nav-toggle{display:block}.navigation-grid--has-drawer{grid-template-areas:"tree nav-toggle textfield" "tree nav-toggle button" "tree nav-toggle masonry";grid-template-columns:var(--lf-imageviewer-nav-width, auto) auto 1fr}.navigation-grid--has-drawer .navigation-grid__tree{display:grid}.navigation-grid__button{grid-area:button;padding-bottom:0.75em}.navigation-grid__masonry{grid-area:masonry;overflow:auto;position:relative}.navigation-grid__nav-toggle{border-right:1px solid rgba(var(--lf-color-border));box-sizing:border-box;display:none;grid-area:nav-toggle}.navigation-grid__textfield{grid-area:textfield;padding:0}.navigation-grid__tree{display:none;grid-area:tree;overflow:auto}.details-grid{width:100%;height:100%;border-left:1px solid rgba(var(--lf-color-border));box-sizing:border-box;display:none;grid-template-areas:"image image" "actions actions" "tree settings";grid-template-columns:40% 1fr;grid-template-rows:60% auto 1fr;overflow:auto}.details-grid__actions{border-left:1px solid rgba(var(--lf-color-border));box-sizing:border-box;display:flex;grid-area:actions}.details-grid__canvas{border-bottom:1px solid rgba(var(--lf-color-border));box-sizing:border-box}.details-grid__preview{align-content:center;grid-area:image;position:relative}.details-grid__spinner{width:100%;height:100%;left:0;pointer-events:none;position:absolute;top:0}.details-grid__tree{border-right:1px solid rgba(var(--lf-color-border));box-sizing:border-box;grid-area:tree;overflow:auto}.details-grid__settings{grid-area:settings;overflow:auto}';
export {
  F as lf_imageviewer
};
