import { n, V, aS as LF_TREE_BLOCKS, aT as LF_TREE_PARTS, d as LF_STYLE_ID, f as LF_WRAPPER_ID, aU as LF_TREE_PROPS, p as pt, b as LF_ATTRIBUTES, C as CY_ATTRIBUTES, D as D$1, W as W$1, z as z$1, aV as LF_TREE_CSS_VARIABLES } from "./index-BFq_6STv.js";
import { a } from "./p-Dl9cVpAY-9zAXgbCa.js";
import { f } from "./p-Cn5YKT90-BudbUsl0.js";
const g = (e) => ({ blocks: e.blocks, compInstance: e.compInstance, manager: e.manager, cyAttributes: e.cyAttributes, dataset: e.dataset, columns: e.columns, isGrid: e.isGrid, lfAttributes: e.lfAttributes, parts: e.parts, isExpanded: e.isExpanded, isHidden: e.isHidden, isSelected: e.isSelected, filterValue: e.filterValue }), b = (e) => ({ expansion: e.expansion, selection: e.selection, filter: e.filter }), v = ({ depth: t, expanded: r = false, manager: o, node: i, onClickExpand: n2, type: d }) => {
  const { get: c } = o.assets, { bemClass: f2 } = o.theme;
  switch (d) {
    case "dropdown":
      return D$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.dropdown, { expanded: r }), "data-cy": CY_ATTRIBUTES.maskedSvg });
    case "expand":
      return D$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.expand, { expanded: r }), "data-cy": CY_ATTRIBUTES.maskedSvg, onClick: n2 });
    case "icon":
      const { style: o2 } = c(`./assets/svg/${i.icon}.svg`);
      return D$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.icon), "data-cy": CY_ATTRIBUTES.maskedSvg, style: o2 });
    case "padding":
      return D$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.padding), style: { [LF_TREE_CSS_VARIABLES.multiplier]: t.toString() } });
    default:
      return D$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.expand, { hidden: true }) });
  }
}, w = (t) => {
  var _a, _b;
  const { manager: r } = t, { bemClass: o } = r.theme, { accordionLayout: i, depth: n2, elements: s, events: c, expanded: f2, node: h, selected: p } = t || {}, m = D$1(v, h.icon ? { manager: r, node: h, type: "icon" } : { manager: r, type: "placeholder" });
  return i ? D$1("div", { class: o(LF_TREE_BLOCKS.node._, null, { expanded: f2, selected: p }), "data-cy": CY_ATTRIBUTES.node, "data-depth": n2.toString(), key: h.id, onClick: c.onClickExpand, onPointerDown: c.onPointerDown, part: LF_TREE_PARTS.node, title: h.description }, D$1("div", { class: o(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.content) }, s.ripple, m, s.value, D$1(v, ((_a = h.children) == null ? void 0 : _a.length) ? { expanded: f2, manager: r, node: h, type: "dropdown" } : { manager: r, type: "placeholder" }))) : D$1("div", { class: o(LF_TREE_BLOCKS.node._, null, { expanded: f2, selected: p }), "data-cy": CY_ATTRIBUTES.node, "data-depth": n2.toString(), key: h.id, onClick: c.onClick, onPointerDown: c.onPointerDown, title: h.description }, D$1("div", { class: "node__content" }, s.ripple, D$1(v, { depth: n2, manager: r, type: "padding" }), D$1(v, ((_b = h.children) == null ? void 0 : _b.length) ? { expanded: f2, manager: r, node: h, onClickExpand: c.onClickExpand, type: "expand" } : { manager: r, type: "placeholder" }), m, s.value));
}, k = (t) => ({ filter: () => {
  const { controller: r, handlers: o } = t(), { compInstance: i, manager: n2 } = r.get, { theme: a2 } = n2, { bemClass: s, get: l } = a2, d = r.get.blocks.tree;
  return i.lfFilter ? D$1("lf-textfield", { class: s(d._, d.filter), lfStretchX: true, lfIcon: l.current().variables["--lf-icon-search"], lfLabel: "Search...", lfStyling: "flat", "onLf-textfield-event": (e) => o.filter.input(e), ref: (e) => t().elements.refs.filterField = e }) : null;
}, header: () => {
  const { controller: r } = t(), o = r.get.columns(), { blocks: i, isGrid: n2, manager: a2, parts: s } = r.get;
  if (!(n2() && o.length > 0)) return null;
  const { bemClass: l } = a2.theme, d = i.header;
  return D$1("div", { class: l(d._), part: s.header }, D$1("div", { class: l(d._, d.row) }, o.map(((t2, r2) => D$1("div", { class: l(d._, d.cell), part: 0 === r2 ? s.headerRow : void 0, "data-column": t2.id, "data-index": r2.toString(), key: t2.id }, t2.title)))));
}, nodes: () => {
  const r = t(), { controller: o, elements: i, handlers: n2 } = r, { get: a2 } = o, { blocks: s, manager: l, parts: d } = a2, { bemClass: c } = l.theme, { tree: f$1 } = s, h = l.data.cell.stringify, p = a2.filterValue() || "", m = a2.columns(), g2 = a2.isGrid(), b2 = a2.dataset(), v2 = a2.manager.data.node.traverseVisible(b2 == null ? void 0 : b2.nodes, { isExpanded: a2.isExpanded, isHidden: a2.isHidden, isSelected: a2.isSelected, forceExpand: !!p }), k2 = v2.length > 0, x2 = v2.map((({ node: t2, depth: r2, expanded: o2, selected: f$12 }) => {
    const p2 = s.node, b3 = ((t3) => {
      if (!g2 || !m.length) return null;
      const r3 = s.node;
      return D$1("div", { class: c(r3._, r3.grid), part: d.node + "-grid" }, m.map(((r4, o3) => ((t4, r5, o4) => {
        var _a;
        const i2 = s.node, n3 = (_a = t4.cells) == null ? void 0 : _a[r5.id];
        if (!n3) {
          const n4 = c(i2._, i2.gridCell);
          return D$1("div", { class: o4 ? n4 + " value" : n4, "data-column": r5.id }, o4 ? h(t4.value) : "");
        }
        const d2 = n3.shape || "text", f$13 = "text" === d2 || "number" === d2 || "slot" === d2, p3 = l.data.cell.shapes.get(n3);
        Object.prototype.hasOwnProperty.call(p3, "lfValue") || (p3.lfValue = n3.value);
        const m2 = p3.lfValue ?? n3.value;
        return D$1("div", { class: c(i2._, i2.gridCell), "data-column": r5.id }, f$13 ? h(m2) : D$1(f, { framework: l, shape: d2, index: 0, cell: p3, eventDispatcher: async (e) => a2.compInstance.onLfEvent(e, "lf-event", { node: t4 }) }));
      })(t3, r4, 0 === o3))));
    })(t2), v3 = a2.compInstance.lfGrid && b3 ? D$1("div", { class: c(p2._, p2.value, { grid: true }) }, b3) : D$1("div", { class: c(p2._, p2.value) }, h(t2.value));
    return D$1(w, { accordionLayout: a2.compInstance.lfAccordionLayout && 0 === r2, depth: r2, elements: { ripple: D$1("div", { "data-cy": a2.cyAttributes.rippleSurface, "data-lf": a2.lfAttributes.rippleSurface, ref: (e) => {
      e && a2.compInstance.lfRipple && (i.refs.rippleSurfaces[t2.id] = e);
    } }), value: v3 }, events: { onClick: (e) => n2.node.click(e, t2), onClickExpand: (e) => n2.node.expand(e, t2), onPointerDown: (e) => n2.node.pointerDown(e, t2) }, expanded: o2, manager: l, node: t2, selected: f$12 });
  }));
  if (k2) return D$1("div", { class: c(f$1._, f$1.nodesWrapper) }, x2);
  if (p) {
    const { noMatches: t2 } = s;
    return D$1("div", { class: c(t2._) }, D$1("div", { class: c(t2._, t2.icon) }), D$1("div", { class: c(t2._, t2.text) }, 'No matches found for "', D$1("strong", { class: c(t2._, t2.filter) }, p), '".'));
  }
  return D$1("div", { class: c(f$1._, f$1.nodesWrapper) });
}, empty: () => {
  const { controller: r } = t(), { compInstance: o, manager: i } = r.get, { theme: n2 } = i, { bemClass: a2 } = n2, s = r.get.blocks, { emptyData: l } = s, d = r.get.parts;
  return D$1("div", { class: a2(l._), part: d.emptyData }, D$1("div", { class: a2(l._, l.text) }, o.lfEmpty));
} }), x = (e) => ({ filter: { input: (t) => {
  var _a, _b;
  const r = e(), { controller: o } = r, i = o.get.compInstance, n2 = ((_a = t.detail.inputValue) == null ? void 0 : _a.toLowerCase()) || "";
  clearTimeout(i._filterTimeout), i._filterTimeout = setTimeout((() => {
    o.set.filter.setValue(n2), o.set.filter.apply(n2);
  }), 300), (_b = i.onLfEvent) == null ? void 0 : _b.call(i, t, "lf-event");
} }, node: { click: (t, r) => {
  var _a;
  const o = e(), { controller: i } = o, n2 = i.get.compInstance;
  i.set.selection.set(r);
  const a2 = i.get.isSelected(r);
  (_a = n2.onLfEvent) == null ? void 0 : _a.call(n2, t, "click", { node: r, selected: a2 });
}, expand: (t, r) => {
  var _a;
  const o = e(), { controller: i } = o, n2 = i.get.compInstance;
  i.set.expansion.toggle(r), (_a = n2.onLfEvent) == null ? void 0 : _a.call(n2, t, "click", { node: r, expansion: true });
}, pointerDown: (t, r) => {
  var _a;
  const o = e(), { controller: i } = o, n2 = i.get.compInstance;
  (_a = n2.onLfEvent) == null ? void 0 : _a.call(n2, t, "pointerdown", { node: r });
} } });
var y, _, z, C, S, E, D, j, T, I = function(e, t, r, o) {
  if ("a" === r && !o) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !o : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === r ? o : "a" === r ? o.call(e) : o ? o.value : t.get(e);
}, L = function(e, t, r, o, i) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, r), r;
};
const W = class {
  constructor(e) {
    n(this, e), this.lfEvent = V(this, "lf-tree-event"), y.add(this), this.expandedNodes = /* @__PURE__ */ new Set(), this.hiddenNodes = /* @__PURE__ */ new Set(), this.selectedNode = null, this.lfAccordionLayout = true, this.lfDataset = null, this.lfEmpty = "Empty data.", this.lfFilter = true, this.lfGrid = false, this.lfRipple = true, this.lfSelectable = true, this.lfStyle = "", this.lfUiSize = "medium", _.set(this, void 0), z.set(this, LF_TREE_BLOCKS), C.set(this, LF_TREE_PARTS), S.set(this, LF_STYLE_ID), E.set(this, LF_WRAPPER_ID), this._filterValue = "", D.set(this, void 0);
  }
  handleDatasetChange() {
    const e = new Set(this.expandedNodes);
    this.hiddenNodes = /* @__PURE__ */ new Set(), this.selectedNode = null, this._filterValue = "", I(this, y, "m", j).call(this, e);
  }
  handleInitialDepthChange() {
    const e = new Set(this.expandedNodes);
    I(this, y, "m", j).call(this, e);
  }
  onLfEvent(e, t, r) {
    var _a;
    const { effects: o } = I(this, _, "f"), { node: i, selected: n2 } = r || {};
    if ("pointerdown" === t && i && this.lfRipple) {
      const t2 = (_a = I(this, D, "f")) == null ? void 0 : _a.elements.refs.rippleSurfaces[i.id];
      t2 && o.ripple(e, t2);
    }
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e, node: i, ...(r == null ? void 0 : r.expansion) ? { expansion: true } : {}, ...null != n2 ? { selected: n2 } : {} });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_TREE_PROPS.map(((e2) => [e2, this[e2]]));
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
    I(this, _, "f") && I(this, _, "f").theme.register(this);
  }
  async componentWillLoad() {
    var e, t, r;
    L(this, _, await a(this)), L(this, D, (e = { blocks: I(this, z, "f"), compInstance: this, cyAttributes: CY_ATTRIBUTES, dataset: () => this.lfDataset, columns: () => {
      var _a;
      return ((_a = this.lfDataset) == null ? void 0 : _a.columns) || [];
    }, isGrid: () => {
      var _a, _b;
      return !(!this.lfGrid || !((_b = (_a = this.lfDataset) == null ? void 0 : _a.columns) == null ? void 0 : _b.length));
    }, lfAttributes: LF_ATTRIBUTES, manager: I(this, _, "f"), parts: I(this, C, "f"), isExpanded: (e2) => {
      const t2 = I(this, y, "m", T).call(this, e2);
      return !!t2 && this.expandedNodes.has(t2);
    }, isHidden: (e2) => this.hiddenNodes.has(e2), isSelected: (e2) => this.selectedNode === e2, filterValue: () => this._filterValue }, t = { expansion: { toggle: (e2) => {
      const t2 = I(this, y, "m", T).call(this, e2);
      t2 && (this.expandedNodes.has(t2) ? this.expandedNodes.delete(t2) : this.expandedNodes.add(t2), this.expandedNodes = new Set(this.expandedNodes));
    } }, selection: { set: (e2) => {
      this.lfSelectable && (this.selectedNode = e2);
    } }, filter: { setValue: (e2) => {
      this._filterValue = e2;
    }, apply: (e2) => {
      const { filter: t2 } = I(this, _, "f").data.node;
      if (!e2) return void (this.hiddenNodes = /* @__PURE__ */ new Set());
      const { ancestorNodes: r2, remainingNodes: o } = t2(this.lfDataset, { value: e2 }, true), i = new Set(o);
      r2 && r2.forEach(((e3) => i.delete(e3))), this.hiddenNodes = i;
    } } }, r = () => I(this, D, "f"), { controller: { get: g(e), set: b(t) }, elements: { jsx: k(r), refs: { rippleSurfaces: {}, filterField: null } }, handlers: x(r) })), I(this, y, "m", j).call(this);
  }
  componentDidLoad() {
    const { info: e } = I(this, _, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = I(this, _, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { debug: e } = I(this, _, "f");
    e.info.update(this, "did-render");
  }
  render() {
    var _a, _b;
    const { bemClass: t, setLfStyle: r } = I(this, _, "f").theme, { tree: o } = I(this, z, "f"), { lfDataset: n2, lfStyle: a2, lfGrid: s } = this, l = (_a = I(this, D, "f")) == null ? void 0 : _a.elements.jsx, d = !((_b = n2 == null ? void 0 : n2.nodes) == null ? void 0 : _b.length);
    return D$1(W$1, { key: "4933548e58c7ff222fec653efb038d4854f6b6cd" }, a2 && D$1("style", { key: "ad92155880b9e12cf96b9f1c201fad650f37bfed", id: I(this, S, "f") }, r(this)), D$1("div", { key: "d4edda4f125ee2f3d9a4a33a213d9999588a37fa", id: I(this, E, "f") }, D$1("div", { key: "90ef037862c67f5a3dbc8302a2acee37ee147f09", class: t(o._) + (s ? " tree--grid" : ""), part: I(this, C, "f").tree }, l == null ? void 0 : l.filter(), l == null ? void 0 : l.header(), d ? l == null ? void 0 : l.empty() : l == null ? void 0 : l.nodes())));
  }
  disconnectedCallback() {
    var _a;
    (_a = I(this, _, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return z$1(this);
  }
  static get watchers() {
    return { lfDataset: ["handleDatasetChange"], lfInitialExpansionDepth: ["handleInitialDepthChange"] };
  }
};
_ = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakMap(), S = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakSet(), j = function(e) {
  var _a;
  const t = this.lfInitialExpansionDepth, r = ((_a = this.lfDataset) == null ? void 0 : _a.nodes) ?? [], o = e ?? this.expandedNodes ?? /* @__PURE__ */ new Set(), i = /* @__PURE__ */ new Set(), n2 = (e2, r2) => {
    for (const a2 of e2) {
      const e3 = I(this, y, "m", T).call(this, a2);
      e3 && (null == t || r2 < t || o.has(e3)) && i.add(e3), Array.isArray(a2.children) && a2.children.length > 0 && n2(a2.children, r2 + 1);
    }
  };
  n2(r, 0), this.expandedNodes = i;
}, T = function(e) {
  if (!e) return null;
  const t = e.id;
  return null == t ? null : String(t);
}, W.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}:host{display:block;font-family:var(--lf-tree-font-family, var(--lf-font-family-primary));font-size:var(--lf-tree-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}:host([lf-accordion-layout]) .node[data-depth="0"]{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);font-size:1em;height:var(--lf-tree-accordion-node-height, 4em)}:host([lf-accordion-layout]) .node[data-depth="0"] .node__value{font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;font-size:1em}:host([lf-selectable]) .node:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.075);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.175);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.225);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.tree{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-bg, var(--lf-color-bg)), 0.275);color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);padding:var(--lf-tree-padding, 0)}.tree__filter{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));border-bottom-left-radius:0;border-bottom-right-radius:0;background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.875);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px);position:sticky;top:0;z-index:1}.tree--grid{display:flex;flex-direction:column;overflow:hidden}.tree--grid .header{position:sticky;top:0;z-index:2;background:var(--lf-tree-color-bg, rgba(0, 0, 0, 0.3));backdrop-filter:blur(10px);font-size:0.85em;line-height:1.2}.tree--grid .header__row{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(120px, auto);column-gap:0.5em;padding:0.5em 1em 0.25em 3.25em;box-sizing:border-box}.tree--grid .header__cell{font-size:0.875em;font-weight:400;line-height:1.25em;letter-spacing:0.2em;font-weight:600;text-transform:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.node{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);box-sizing:border-box;height:var(--lf-tree-node-height, 2em);padding:var(--lftree-node-padding, 0 1em);position:relative}.node__content{width:100%;height:100%;align-items:center;display:flex}.node__dropdown,.node__expand,.node__icon{cursor:pointer;margin:0}.node__dropdown,.node__expand{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);overflow:hidden}.node__dropdown:hover,.node__expand:hover{opacity:0.75}.node__dropdown{-webkit-mask:var(--lf-icon-dropdown);mask:var(--lf-icon-dropdown);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__dropdown--expanded{transform:rotate(180deg)}.node__dropdown--expanded:hover{opacity:0.75}.node__dropdown--hidden{visibility:hidden}.node__expand{-webkit-mask:var(--lf-icon-collapsed);mask:var(--lf-icon-collapsed);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--expanded{-webkit-mask:var(--lf-icon-expanded);mask:var(--lf-icon-expanded);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--hidden{visibility:hidden}.node__icon{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__padding{height:100%;width:calc(1.75em * var(--lf_tree_padding_multiplier))}.node__value{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;margin:0 0 0 0.5em;width:100%}.node__value--grid .node__grid{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(120px, auto);column-gap:0.5em;align-items:center;padding:0 1em 0 0;box-sizing:border-box;min-height:100%}.node__value--grid .node__grid-cell{font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;display:flex;align-items:center;min-height:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.node__value--grid .node__grid-cell--value{font-weight:500}.no-matches{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));align-items:center;box-sizing:border-box;display:flex;justify-content:center;margin:auto;padding:1em;width:100%}.no-matches__icon{-webkit-mask:var(--lf-icon-warning);mask:var(--lf-icon-warning);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin-right:0.375em}.no-matches__text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:400;line-height:1.25em;letter-spacing:0.2em}.no-matches__filter{color:var(--lf-primary-color)}.empty-data{width:100%;height:100%;font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:1em;align-items:center;display:flex;justify-content:center;margin:1em 0}';
export {
  W as lf_tree
};
