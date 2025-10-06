import { n, V as V$1, aS as LF_IMAGEVIEWER_BLOCKS, C as CY_ATTRIBUTES, b as LF_ATTRIBUTES, aT as LF_IMAGEVIEWER_PARTS, d as LF_STYLE_ID, f as LF_WRAPPER_ID, aU as LF_IMAGEVIEWER_PROPS, p as pt, D as D$1, W as W$1, z as z$1, aV as IDS } from "./index-EOkmblAM.js";
import { a } from "./p-Dl9cVpAY-5guf9rt2.js";
const g = async (e, t = null) => {
  const { history: i } = e.controller.set;
  null === t ? (i.pop(), b(e)) : i.pop(t);
}, b = async (e) => {
  const { controller: t, elements: i } = e, { masonry: s } = i.refs.navigation, { set: n2 } = t;
  n2.currentShape({}), n2.history.index(null), s.setSelectedShape(null);
}, v = (e) => {
  const { compInstance: t, currentShape: i, manager: s } = e.controller.get, { lfDataset: n2 } = t, { getAll: a2 } = s.data.cell.shapes, r = i();
  return a2(n2, false).image.find(((e2) => e2.value === r.value || e2.lfValue === r.value));
}, p = async (e, t) => {
  requestAnimationFrame((() => e.lfShowSpinner = true)), await t(), requestAnimationFrame((() => e.lfShowSpinner = false));
}, y = (e, t) => {
  const i = e;
  e.value = t, i.lfValue && (i.lfValue = t);
}, w = (t) => ({ canvas: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, history: o, lfAttribute: l, manager: c } = i.get, { details: f } = s.refs, { canvas: d } = n2.details, { currentSnapshot: h } = o, { assignRef: u, theme: m } = c, { bemClass: g2 } = m, b2 = h();
  if (b2) return D$1("lf-canvas", { class: g2(a2.detailsGrid._, a2.detailsGrid.canvas), "data-lf": l.fadeIn, id: IDS.details.canvas, lfImageProps: { lfValue: b2.value }, "onLf-canvas-event": d, ref: u(f, "canvas") });
}, clearHistory: () => {
  var _a;
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, cyAttributes: o, history: l, manager: c } = i.get, { details: f } = s.refs, { button: d } = n2.details, { current: h } = l, { assignRef: u, theme: m } = c, { bemClass: g2, get: b2 } = m, v2 = b2.icon("stackPop"), p2 = !(((_a = h()) == null ? void 0 : _a.length) > 1);
  return D$1("lf-button", { class: g2(a2.detailsGrid._, a2.detailsGrid.clearHistory), "data-cy": o.button, id: IDS.details.clearHistory, lfIcon: v2, lfLabel: "Clear history", lfStretchX: true, lfStyling: "flat", lfUiState: p2 ? "disabled" : "danger", "onLf-button-event": d, ref: u(f, "clearHistory") });
}, deleteShape: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, cyAttributes: o, manager: l } = i.get, { details: c } = s.refs, { button: f } = n2.details, { assignRef: d, theme: h } = l, { bemClass: u, get: m } = h, { "--lf-icon-clear": g2 } = m.current().variables;
  return D$1("lf-button", { class: u(a2.detailsGrid._, a2.detailsGrid.delete), "data-cy": o.button, id: IDS.details.deleteShape, lfIcon: g2, lfLabel: "Delete image", lfStretchX: true, lfUiState: "danger", "onLf-button-event": f, ref: d(c, "deleteShape") });
}, redo: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, cyAttributes: o, history: l, manager: c } = i.get, { current: f, index: d } = l, { details: h } = s.refs, { button: u } = n2.details, { assignRef: m, theme: g2 } = c, { bemClass: b2, get: v2 } = g2, { "--lf-icon-next": p2 } = v2.current().variables, y2 = f(), w2 = !((y2 == null ? void 0 : y2.length) && d() < y2.length - 1);
  return D$1("lf-button", { class: b2(a2.detailsGrid._, a2.detailsGrid.redo), "data-cy": o.button, id: IDS.details.redo, lfIcon: p2, lfLabel: "Redo", lfStretchX: true, lfStyling: "flat", lfUiState: w2 ? "disabled" : "primary", "onLf-button-event": u, ref: m(h, "redo") });
}, save: () => {
  var _a;
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, cyAttributes: o, history: l, manager: c } = i.get, { current: f } = l, { details: d } = s.refs, { button: h } = n2.details, { assignRef: u, theme: m } = c, { bemClass: g2, get: b2 } = m, { "--lf-icon-success": v2 } = b2.current().variables, p2 = !(((_a = f()) == null ? void 0 : _a.length) > 1);
  return D$1("lf-button", { class: g2(a2.detailsGrid._, a2.detailsGrid.commitChanges), "data-cy": o.button, id: IDS.details.save, lfIcon: v2, lfLabel: "Save snapshot", lfStretchX: true, lfUiState: p2 ? "disabled" : "success", "onLf-button-event": h, ref: u(d, "save") });
}, spinner: () => {
  const { controller: i, elements: s } = t(), { blocks: n2, manager: a2, spinnerStatus: o } = i.get, { details: l } = s.refs, { assignRef: c, theme: f } = a2, { bemClass: d } = f;
  return D$1("lf-spinner", { class: d(n2.detailsGrid._, n2.detailsGrid.spinner), id: IDS.details.spinner, lfActive: o(), lfDimensions: "16px", lfFader: true, lfFaderTimeout: 125, lfLayout: 14, ref: c(l, "save") });
}, tree: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, compInstance: o, cyAttributes: l, manager: c } = i.get, { details: f } = s.refs, { tree: d } = n2.details, { assignRef: h, theme: u } = c, { bemClass: m } = u;
  return D$1("lf-tree", { class: m(a2.detailsGrid._, a2.detailsGrid.tree), "data-cy": l.input, id: IDS.details.tree, lfAccordionLayout: true, lfDataset: o.lfValue, lfFilter: false, lfSelectable: true, lfUiSize: "small", "onLf-tree-event": d, ref: h(f, "tree") });
}, undo: () => {
  var _a;
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, cyAttributes: o, history: l, manager: c } = i.get, { current: f, index: d } = l, { details: h } = s.refs, { button: u } = n2.details, { assignRef: m, theme: g2 } = c, { bemClass: b2, get: v2 } = g2, { "--lf-icon-previous": p2 } = v2.current().variables, y2 = !(((_a = f()) == null ? void 0 : _a.length) && d() > 0);
  return D$1("lf-button", { class: b2(a2.detailsGrid._, a2.detailsGrid.undo), "data-cy": o.button, id: IDS.details.undo, lfIcon: p2, lfLabel: "Undo", lfStretchX: true, lfStyling: "flat", lfUiState: y2 ? "disabled" : "primary", "onLf-button-event": u, ref: m(h, "undo") });
} }), x = (t) => ({ load: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, cyAttributes: o, manager: l } = i.get, { navigation: c } = s.refs, { button: f } = n2.navigation, { assignRef: d, theme: h } = l, { bemClass: u } = h;
  return D$1("lf-button", { class: u(a2.navigationGrid._, a2.navigationGrid.button), "data-cy": o.button, id: IDS.navigation.load, lfLabel: "Load", lfStretchX: true, "onLf-button-event": f, ref: d(c, "load") }, D$1("lf-spinner", { lfActive: true, lfDimensions: "2px", lfLayout: 1, slot: "spinner" }));
}, masonry: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, compInstance: o, manager: l } = i.get, { navigation: c } = s.refs, { masonry: f } = n2.navigation, { lfDataset: d } = o, { assignRef: h, theme: u } = l, { bemClass: m } = u;
  return D$1("lf-masonry", { class: m(a2.navigationGrid._, a2.navigationGrid.masonry), id: IDS.navigation.masonry, lfActions: true, lfDataset: d, lfSelectable: true, "onLf-masonry-event": f, ref: h(c, "masonry") });
}, textfield: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, cyAttributes: o, manager: l } = i.get, { navigation: c } = s.refs, { textfield: f } = n2.navigation, { assignRef: d, theme: h } = l, { bemClass: u } = h;
  return D$1("lf-textfield", { class: u(a2.navigationGrid._, a2.navigationGrid.textfield), "data-cy": o.input, id: IDS.navigation.textfield, lfIcon: "folder", lfLabel: "Directory", lfStretchX: true, lfStyling: "flat", "onLf-textfield-event": f, ref: d(c, "textfield") });
}, tree: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, manager: o, navigationTree: l, treeProps: c } = i.get, { navigation: f } = s.refs, { tree: d } = n2.navigation, { assignRef: h, sanitizeProps: u, theme: m } = o, { bemClass: g2 } = m;
  if (!l().enabled) return;
  const b2 = c();
  return D$1("lf-tree", { class: g2(a2.navigationGrid._, a2.navigationGrid.tree), id: IDS.navigation.tree, "onLf-tree-event": d, ref: h(f, "tree"), ...u(b2, "LfTree") });
}, treeToggle: () => {
  const { controller: i, elements: s, handlers: n2 } = t(), { blocks: a2, cyAttributes: o, manager: l, navigationTree: c } = i.get, { navigation: f } = s.refs, { treeToggle: d } = n2.navigation, { assignRef: h, theme: u } = l, { bemClass: m } = u, { "--lf-icon-next": g2, "--lf-icon-previous": b2 } = u.get.current().variables, v2 = c();
  if (!v2.enabled) return;
  const p2 = "start" === v2.position, y2 = v2.open ? p2 ? b2 : g2 : (p2 ? g2 : b2) || "folder";
  return D$1("lf-button", { class: m(a2.navigationGrid._, a2.navigationGrid.treeToggle), "data-cy": o.button, id: IDS.navigation.treeToggle, lfAriaLabel: v2.open ? "Collapse navigation tree" : "Expand navigation tree", lfIcon: y2, lfStretchY: true, "onLf-button-event": d, ref: h(f, "treeToggle") });
} }), k = (e) => ({ button: async (t) => {
  const { comp: i, eventType: s, id: n2 } = t.detail, a2 = e(), { compInstance: o, currentShape: l } = a2.controller.get;
  if (o.onLfEvent(t, "lf-event"), "click" === s) switch (n2) {
    case IDS.details.clearHistory:
      const e2 = l().shape.index;
      p(i, (async () => g(a2, e2)));
      break;
    case IDS.details.deleteShape:
      p(i, (() => (async (e3) => {
        const { compInstance: t2, currentShape: i2, manager: s2 } = e3.controller.get, { lfDataset: n3 } = t2, { findNodeByCell: a3, pop: r } = s2.data.node;
        await g(e3, i2().shape.index);
        const o2 = a3(n3, v(e3));
        r(n3.nodes, o2), t2.lfDataset = { ...n3 }, await b(e3);
      })(a2)));
      break;
    case IDS.details.redo:
      p(i, (() => (async (e3) => {
        const { controller: t2 } = e3, { get: i2, set: s2 } = t2, { current: n3, index: a3 } = i2.history, r = n3(), o2 = a3();
        r && o2 < r.length - 1 && s2.history.index(o2 + 1);
      })(a2)));
      break;
    case IDS.details.save:
      p(i, (() => (async (e3) => {
        const { compInstance: t2, currentShape: i2, history: s2 } = e3.controller.get, { lfDataset: n3 } = t2, a3 = i2();
        if (!a3) return;
        const r = a3.shape.index, o2 = a3.shape.shape, l2 = s2.currentSnapshot().value, c = v(e3);
        c.value = l2, c.lfValue = l2, y(o2, l2), await g(e3, r), t2.lfDataset = { ...n3 };
      })(a2)));
      break;
    case IDS.details.undo:
      p(i, (() => (async (e3) => {
        const { controller: t2 } = e3, { get: i2, set: s2 } = t2, { history: n3 } = i2, { index: a3 } = n3, r = a3();
        r > 0 && s2.history.index(r - 1);
      })(a2)));
  }
}, canvas: (t) => {
  const i = e(), { compInstance: s } = i.controller.get;
  s.onLfEvent(t, "lf-event");
}, tree: (t) => {
  const i = e(), { compInstance: s } = i.controller.get;
  s.onLfEvent(t, "lf-event");
} }), S = (e) => ({ button: async (t) => {
  const { comp: i, eventType: s } = t.detail, n2 = e(), { compInstance: a2 } = n2.controller.get;
  a2.onLfEvent(t, "lf-event"), "click" === s && p(i, (() => (async (e2) => {
    const { controller: t2, elements: i2 } = e2, { textfield: s2 } = i2.refs.navigation, { compInstance: n3 } = t2.get, { lfLoadCallback: a3 } = n3;
    try {
      await a3(n3, await s2.getValue()), g(e2);
    } catch (e3) {
      console.error("Load operation failed:", e3);
    }
  })(n2)));
}, masonry: (t) => {
  var _a;
  const { eventType: i, originalEvent: s, selectedShape: n2 } = t.detail, a2 = e(), { controller: r } = a2, { get: o, set: l } = r, { compInstance: c, history: f } = o, { current: d } = f;
  if (c.onLfEvent(t, "lf-event"), "lf-event" === i && "click" === s.detail.eventType) {
    const e2 = o.currentShape();
    if (((_a = e2 == null ? void 0 : e2.shape) == null ? void 0 : _a.index) === n2.index) b(a2);
    else {
      l.currentShape(n2);
      const e3 = d();
      l.history.index(e3 ? e3.length - 1 : 0), l.history.new(n2);
    }
  }
}, textfield: (t) => {
  const i = e(), { compInstance: s } = i.controller.get;
  s.onLfEvent(t, "lf-event");
}, tree: (t) => {
  const i = e(), { compInstance: s } = i.controller.get;
  s.onLfEvent(t, "lf-event");
}, treeToggle: (t) => {
  const { eventType: i } = t.detail, s = e(), { controller: n2 } = s, { get: a2, set: r } = n2, { compInstance: o, navigationTree: l } = a2;
  if (o.onLfEvent(t, "lf-event"), "click" === i) {
    const e2 = l();
    r.navigationTreeOpen(!e2.open);
  }
} }), z = (e, t) => ({ ...e, spinnerStatus: (e2) => t().elements.refs.details.spinner.lfActive = e2 }), L = (e) => ({ details: w(e), navigation: x(e) }), C = (e) => ({ details: k(e), navigation: S(e) });
var _, W, T, I, A, M, R, D, E, N, O, P, U, j, H, X, F, $, q, B, J, V, Y, G, K = function(e, t, i, s) {
  if ("a" === i && !s) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !s : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === i ? s : "a" === i ? s.call(e) : s ? s.value : t.get(e);
}, Q = function(e, t, i, s, n2) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, i), i;
};
const Z = { collapsedWidth: 48, defaultOpen: true, enabled: false, layout: { columns: 1, mode: "accordion" }, maxWidth: 420, minWidth: 240, position: "start", width: 320 }, ee = class {
  constructor(e) {
    n(this, e), this.lfEvent = V$1(this, "lf-imageviewer-event"), _.add(this), this.currentShape = {}, this.history = {}, this.historyIndex = null, this.isSpinnerActive = false, this.isNavigationTreeOpen = false, this.lfDataset = {}, this.lfLoadCallback = null, this.lfNavigationTree = false, this.lfStyle = "", this.lfTreeProps = {}, this.lfValue = {}, W.set(this, void 0), T.set(this, LF_IMAGEVIEWER_BLOCKS), I.set(this, CY_ATTRIBUTES), A.set(this, LF_ATTRIBUTES), M.set(this, LF_IMAGEVIEWER_PARTS), R.set(this, LF_STYLE_ID), D.set(this, LF_WRAPPER_ID), E.set(this, void 0), N.set(this, K(this, _, "m", O).call(this)), B.set(this, (() => {
      var e2;
      Q(this, E, { controller: { get: { blocks: K(this, T, "f"), compInstance: this, currentShape: () => K(this, _, "m", J).call(this, this.currentShape), cyAttributes: K(this, I, "f"), history: { current: () => this.history[this.currentShape.index], currentSnapshot: () => {
        if (null === this.historyIndex) return null;
        const e3 = this.history[this.currentShape.index][this.historyIndex];
        return K(this, _, "m", J).call(this, e3);
      }, full: () => this.history, index: () => this.historyIndex }, lfAttribute: K(this, A, "f"), manager: K(this, W, "f"), navigationTree: () => K(this, _, "m", X).call(this), parts: K(this, M, "f"), spinnerStatus: () => this.isSpinnerActive, treeProps: () => K(this, _, "m", F).call(this) }, set: z({ currentShape: (e3) => this.currentShape = e3, history: { index: (e3) => this.historyIndex = e3, new: (e3, t = false) => {
        var _a;
        const i = ((_a = this.history) == null ? void 0 : _a[e3.index]) || [];
        this.historyIndex < i.length - 1 && i.splice(this.historyIndex + 1), !(i == null ? void 0 : i.length) || t ? (i.push(e3), this.history[e3.index] = i, this.historyIndex = i.length - 1) : i[0] = e3;
      }, pop: (e3 = null) => {
        null !== e3 ? (this.history[e3] = [this.history[e3][0]], 0 === this.historyIndex ? this.refresh() : this.historyIndex = 0) : (this.history = {}, this.historyIndex = null);
      } }, navigationTreeOpen: (e3) => this.isNavigationTreeOpen = e3 }, e2 = () => K(this, E, "f")) }, elements: { jsx: L(e2), refs: { details: { canvas: null, clearHistory: null, deleteShape: null, redo: null, save: null, spinner: null, undo: null, tree: null }, navigation: { load: null, masonry: null, tree: null, treeToggle: null, textfield: null } } }, handlers: C(e2) });
    }));
  }
  onLfNavigationTreeChange(e) {
    K(this, _, "m", H).call(this, e, true);
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e });
  }
  async addSnapshot(e) {
    var _a;
    const { currentShape: t } = this;
    if (!t || !((_a = Object.keys(t)) == null ? void 0 : _a.length)) return;
    const { history: i } = K(this, E, "f").controller.set, s = JSON.parse(JSON.stringify(t));
    y(s.shape, e), i.new(s, true);
  }
  async clearHistory(e = null) {
    await g(K(this, E, "f"), e);
  }
  async clearSelection() {
    await b(K(this, E, "f"));
  }
  async getComponents() {
    return K(this, E, "f").elements.refs;
  }
  async getCurrentSnapshot() {
    return K(this, E, "f").controller.get.history.currentSnapshot();
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
    await g(K(this, E, "f")), await b(K(this, E, "f"));
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
    K(this, W, "f") && K(this, W, "f").theme.register(this);
  }
  async componentWillLoad() {
    Q(this, W, await a(this)), K(this, _, "m", H).call(this, this.lfNavigationTree), K(this, B, "f").call(this);
  }
  componentDidLoad() {
    const { info: e } = K(this, W, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = K(this, W, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = K(this, W, "f").debug;
    e.update(this, "did-render");
  }
  render() {
    const { bemClass: t, setLfStyle: i } = K(this, W, "f").theme, { lfStyle: s } = this;
    return D$1(W$1, { key: "8c3174e6700175250b0838e4678e1517bb25ac7c" }, s && D$1("style", { key: "3448eaad8799b42e5a9fb204fd71a95a4a0ee6a8", id: K(this, R, "f") }, i(this)), D$1("div", { key: "e7d50e184fd00c8f49821c6c41266609f1212123", id: K(this, D, "f") }, D$1("div", { key: "4a3c2ab1c1424e79e40af9db6eff3e5091656f3b", class: t(K(this, T, "f").imageviewer._), part: K(this, M, "f").imageviewer }, K(this, _, "m", Y).call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = K(this, W, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return z$1(this);
  }
  static get watchers() {
    return { lfNavigationTree: ["onLfNavigationTreeChange"] };
  }
};
W = /* @__PURE__ */ new WeakMap(), T = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakMap(), A = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), R = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), N = /* @__PURE__ */ new WeakMap(), B = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakSet(), O = function() {
  const { collapsedWidth: e, defaultOpen: t, enabled: i, layout: s, maxWidth: n2, minWidth: a2, position: r, width: o } = Z;
  return { collapsedWidth: e, defaultOpen: t, enabled: i, layout: { ...s }, maxWidth: n2, minWidth: a2, position: r, width: o };
}, P = function(e) {
  const t = K(this, _, "m", O).call(this);
  if (true === e) return t.enabled = true, t;
  if (!e) return t.enabled = false, t;
  if (t.enabled = e.enabled ?? true, "boolean" == typeof e.defaultOpen && (t.defaultOpen = e.defaultOpen), "end" === e.position && (t.position = "end"), t.minWidth = K(this, _, "m", U).call(this, e.minWidth, t.minWidth), t.maxWidth = K(this, _, "m", U).call(this, e.maxWidth, t.maxWidth), t.minWidth > t.maxWidth) {
    const e2 = t.minWidth;
    t.minWidth = t.maxWidth, t.maxWidth = e2;
  }
  if (t.width = K(this, _, "m", U).call(this, e.width, t.width), t.width = K(this, _, "m", j).call(this, t.width, t.minWidth, t.maxWidth), e.layout) {
    const { mode: i, columns: s } = e.layout;
    "grid" !== i && "accordion" !== i || (t.layout.mode = i), "number" == typeof s && Number.isFinite(s) && s > 0 && (t.layout.columns = Math.max(1, Math.floor(s)));
  }
  return t;
}, U = function(e, t) {
  if ("number" == typeof e && Number.isFinite(e)) return Math.max(0, e);
  if ("string" == typeof e) {
    const t2 = Number.parseFloat(e);
    if (Number.isFinite(t2)) return Math.max(0, t2);
  }
  return t;
}, j = function(e, t, i) {
  return Math.min(Math.max(e, t), i);
}, H = function(e, t = false) {
  const i = K(this, N, "f"), s = K(this, _, "m", P).call(this, e);
  Q(this, N, s), s.enabled ? t && i.enabled || (this.isNavigationTreeOpen = s.defaultOpen) : this.isNavigationTreeOpen = false;
}, X = function() {
  const { collapsedWidth: e, defaultOpen: t, enabled: i, layout: s, maxWidth: n2, minWidth: a2, position: r, width: o } = K(this, N, "f");
  return { collapsedWidth: e, defaultOpen: t, enabled: i, layout: { ...s }, maxWidth: n2, minWidth: a2, open: i && this.isNavigationTreeOpen, position: r, width: o };
}, F = function() {
  const { layout: e } = K(this, N, "f"), t = { lfAccordionLayout: "accordion" === e.mode, lfFilter: false, lfSelectable: true, lfUiSize: "small" };
  "grid" === e.mode && (t.lfAccordionLayout = false, t.lfGrid = true);
  const i = this.lfTreeProps ?? {}, s = { ...t, ...i };
  return s.lfDataset || (s.lfDataset = this.lfDataset), s;
}, $ = function(e) {
  const t = K(this, _, "m", q).call(this, e), i = e.collapsedWidth;
  return { maxWidth: `${e.open ? e.maxWidth : i}px`, minWidth: `${e.open ? e.minWidth : i}px`, width: `${t}px` };
}, q = function(e) {
  return e.open ? K(this, _, "m", j).call(this, e.width, e.minWidth, e.maxWidth) : e.collapsedWidth;
}, J = function(e) {
  const { data: t } = K(this, W, "f"), { cell: i } = t, { stringify: s } = i;
  return void 0 !== e.index ? { shape: e, value: s(e.shape.value || e.shape.lfValue) } : null;
}, V = function() {
  const { bemClass: t } = K(this, W, "f").theme, { detailsGrid: i } = K(this, T, "f"), { canvas: s, clearHistory: n2, deleteShape: a2, redo: r, save: o, spinner: l, tree: c, undo: f } = K(this, E, "f").elements.jsx.details;
  return D$1("div", { class: t(i._), part: K(this, M, "f").details }, D$1("div", { class: t(i._, i.preview) }, s(), l()), D$1("div", { class: t(i._, i.actions) }, a2(), n2(), f(), r(), o()), c(), D$1("div", { class: t(i._, i.settings) }, D$1("slot", { name: "settings" })));
}, Y = function() {
  const { bemClass: t } = K(this, W, "f").theme, { currentShape: i } = K(this, E, "f").controller.get;
  return D$1("div", { class: t(K(this, T, "f").mainGrid._, null, { selected: !!i() }) }, K(this, _, "m", G).call(this), K(this, _, "m", V).call(this));
}, G = function() {
  const { bemClass: t } = K(this, W, "f").theme, { load: i, masonry: s, textfield: n2, tree: a2, treeToggle: r } = K(this, E, "f").elements.jsx.navigation, o = K(this, E, "f").controller.get.navigationTree(), l = K(this, T, "f").navigationGrid, c = t(l._, void 0, { "with-tree": o.enabled, "tree-closed": o.enabled && !o.open, "tree-end": o.enabled && "end" === o.position }), f = D$1("div", { class: t(l._, l.content) }, n2(), i(), s());
  if (!o.enabled) return D$1("div", { class: c, part: K(this, M, "f").navigation }, f);
  const d = "end" === o.position ? { "tree-end": true } : void 0, h = () => D$1("div", { class: t(l._, l.treeShell, d), style: K(this, _, "m", $).call(this, o) }, D$1("div", { "aria-hidden": o.open ? "false" : "true", class: t(l._, l.treeContent), style: { display: o.open ? "block" : "none" } }, a2()), D$1("div", { class: t(l._, l.treeHeader) }, r()));
  return D$1("div", { class: c, part: K(this, M, "f").navigation }, "start" === o.position && h(), f, "end" === o.position && h());
}, ee.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-imageviewer-font-family, var(--lf-font-family-primary));font-size:var(--lf-imageviewer-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-imageviewer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{background-color:rgba(var(--lf-imageviewer-color-bg, var(--lf-color-bg)), 0.125);color:rgb(var(--lf-imageviewer-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);width:100%;height:100%}.imageviewer{width:100%;height:100%}.main-grid{border:0;border-style:solid;border-color:rgba(var(--lf-imageviewer-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-imageviewer-border-radius, var(--lf-ui-border-radius));width:100%;height:100%;box-sizing:border-box;display:grid;grid-template-columns:100% 0;overflow:auto}.main-grid--selected{grid-template-columns:30% 70%}.main-grid--selected .details-grid{display:grid}.navigation-grid{width:100%;height:100%;box-sizing:border-box;display:grid;grid-template-columns:1fr;overflow:hidden}.navigation-grid--with-tree{grid-template-columns:auto 1fr}.navigation-grid--with-tree.navigation-grid--tree-end{grid-template-columns:1fr auto}.navigation-grid__content{display:grid;grid-template-rows:auto auto 1fr;overflow:hidden}.navigation-grid__textfield{padding:0}.navigation-grid__button{padding-bottom:0.75em}.navigation-grid__masonry{overflow:auto;position:relative}.navigation-grid__tree-shell{display:grid;grid-template-columns:1fr auto;overflow:hidden}.navigation-grid__tree-shell--tree-end{border-left:1px solid rgba(var(--lf-color-border));border-right:none}.navigation-grid__tree-header{border-right:1px solid rgba(var(--lf-color-border))}.navigation-grid__tree-content{overflow:auto}.details-grid{width:100%;height:100%;border-left:1px solid rgba(var(--lf-color-border));box-sizing:border-box;display:none;grid-template-areas:"image image" "actions actions" "tree settings";grid-template-columns:40% 1fr;grid-template-rows:60% auto 1fr;overflow:auto}.details-grid__actions{border-left:1px solid rgba(var(--lf-color-border));box-sizing:border-box;display:flex;grid-area:actions}.details-grid__canvas{border-bottom:1px solid rgba(var(--lf-color-border));box-sizing:border-box}.details-grid__preview{align-content:center;grid-area:image;position:relative}.details-grid__spinner{width:100%;height:100%;left:0;pointer-events:none;position:absolute;top:0}.details-grid__tree{border-right:1px solid rgba(var(--lf-color-border));box-sizing:border-box;grid-area:tree;overflow:auto}.details-grid__settings{grid-area:settings;overflow:auto}';
export {
  ee as lf_imageviewer
};
