import { n, I as I$1, V as LF_TREE_BLOCKS, X as LF_TREE_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, Y as LF_TREE_PROPS, m as mt, a as LF_ATTRIBUTES, C as CY_ATTRIBUTES, W as W$1, f as L$1, G, Z as LF_TREE_CSS_VARIABLES } from "./index-BqTPLB6U.js";
import { o } from "./p-DklcdYZv-CGe0ClQS.js";
import { f } from "./p-HvQH5Jh2-b3mQPQ0e.js";
const g = (e) => ({ blocks: e.blocks, compInstance: e.compInstance, manager: e.manager, cyAttributes: e.cyAttributes, dataset: e.dataset, columns: e.columns, isGrid: e.isGrid, lfAttributes: e.lfAttributes, parts: e.parts, isExpanded: e.isExpanded, isHidden: e.isHidden, isSelected: e.isSelected, filterValue: e.filterValue }), u = (e) => ({ expansion: e.expansion, selection: e.selection, filter: e.filter }), v = ({ depth: t, expanded: r = false, manager: o2, node: i, onClickExpand: a, type: d }) => {
  const { get: c } = o2.assets, { bemClass: f2 } = o2.theme;
  switch (d) {
    case "dropdown":
      return W$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.dropdown, { expanded: r }), "data-cy": CY_ATTRIBUTES.maskedSvg });
    case "expand":
      return W$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.expand, { expanded: r }), "data-cy": CY_ATTRIBUTES.maskedSvg, onClick: a });
    case "icon":
      const { style: o3 } = c(`./assets/svg/${i.icon}.svg`);
      return W$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.icon), "data-cy": CY_ATTRIBUTES.maskedSvg, style: o3 });
    case "padding":
      return W$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.padding), style: { [LF_TREE_CSS_VARIABLES.multiplier]: t.toString() } });
    default:
      return W$1("div", { class: f2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.expand, { hidden: true }) });
  }
}, w = (t) => {
  var _a, _b;
  const { manager: r } = t, { bemClass: o2 } = r.theme, { accordionLayout: i, depth: a, elements: s, events: c, expanded: f2, node: p, selected: h } = t || {}, m = W$1(v, p.icon ? { manager: r, node: p, type: "icon" } : { manager: r, type: "placeholder" });
  return i ? W$1("div", { class: o2(LF_TREE_BLOCKS.node._, null, { expanded: f2, selected: h }), "data-cy": CY_ATTRIBUTES.node, "data-depth": a.toString(), key: p.id, onClick: c.onClickExpand, onPointerDown: c.onPointerDown, part: LF_TREE_PARTS.node, title: p.description }, W$1("div", { class: o2(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.content) }, s.ripple, m, s.value, W$1(v, ((_a = p.children) == null ? void 0 : _a.length) ? { expanded: f2, manager: r, node: p, type: "dropdown" } : { manager: r, type: "placeholder" }))) : W$1("div", { class: o2(LF_TREE_BLOCKS.node._, null, { expanded: f2, selected: h }), "data-cy": CY_ATTRIBUTES.node, "data-depth": a.toString(), key: p.id, onClick: c.onClick, onPointerDown: c.onPointerDown, title: p.description }, W$1("div", { class: "node__content" }, s.ripple, W$1(v, { depth: a, manager: r, type: "padding" }), W$1(v, ((_b = p.children) == null ? void 0 : _b.length) ? { expanded: f2, manager: r, node: p, onClickExpand: c.onClickExpand, type: "expand" } : { manager: r, type: "placeholder" }), m, s.value));
}, k = (t) => ({ filter: () => {
  const { controller: r, handlers: o2 } = t(), { compInstance: i, manager: a } = r.get, { theme: n2 } = a, { bemClass: s, get: l } = n2, d = r.get.blocks.tree;
  return i.lfFilter ? W$1("lf-textfield", { class: s(d._, d.filter), lfStretchX: true, lfIcon: l.current().variables["--lf-icon-search"], lfLabel: "Search...", lfStyling: "flat", "onLf-textfield-event": (e) => o2.filter.input(e), ref: (e) => t().elements.refs.filterField = e }) : null;
}, header: () => {
  const { controller: r } = t(), o2 = r.get.columns(), { blocks: i, isGrid: a, manager: n2, parts: s } = r.get;
  if (!(a() && o2.length > 0)) return null;
  const { bemClass: l } = n2.theme, d = i.header;
  return W$1("div", { class: l(d._), part: s.header }, W$1("div", { class: l(d._, d.row) }, o2.map(((t2, r2) => W$1("div", { class: l(d._, d.cell), part: 0 === r2 ? s.headerRow : void 0, "data-column": t2.id, "data-index": r2.toString(), key: t2.id }, t2.title)))));
}, nodes: () => {
  const r = t(), { controller: o2, elements: i, handlers: a } = r, { get: n2 } = o2, { blocks: s, manager: l, parts: d } = n2, { bemClass: c } = l.theme, { tree: f$1 } = s, p = l.data.cell.stringify, h = n2.filterValue() || "", m = n2.columns(), g2 = n2.isGrid(), u2 = n2.dataset(), v2 = n2.manager.data.node.traverseVisible(u2 == null ? void 0 : u2.nodes, { isExpanded: n2.isExpanded, isHidden: n2.isHidden, isSelected: n2.isSelected, forceExpand: !!h }), k2 = v2.length > 0, x2 = v2.map((({ node: t2, depth: r2, expanded: o3, selected: f$12 }) => {
    const h2 = s.node, u3 = ((t3) => {
      if (!g2 || !m.length) return null;
      const r3 = s.node;
      return W$1("div", { class: c(r3._, r3.grid), part: d.node + "-grid" }, m.map(((r4, o4) => ((t4, r5, o5) => {
        var _a;
        const i2 = s.node, a2 = (_a = t4.cells) == null ? void 0 : _a[r5.id];
        if (!a2) {
          const a3 = c(i2._, i2.gridCell);
          return W$1("div", { class: o5 ? a3 + " value" : a3, "data-column": r5.id }, o5 ? p(t4.value) : "");
        }
        const d2 = a2.shape || "text", f$13 = "text" === d2 || "number" === d2 || "slot" === d2, h3 = l.data.cell.shapes.get(a2);
        if (!Object.prototype.hasOwnProperty.call(h3, "lfValue")) return h3.lfValue = a2.value, W$1("div", { class: c(i2._, i2.gridCell), "data-column": r5.id }, f$13 ? p(a2.value) : W$1(f, { framework: l, shape: d2, index: 0, cell: h3, eventDispatcher: async (e) => n2.compInstance.onLfEvent(e, "lf-event", { node: t4 }) }));
      })(t3, r4, 0 === o4))));
    })(t2), v3 = n2.compInstance.lfGrid && u3 ? W$1("div", { class: c(h2._, h2.value, { grid: true }) }, u3) : W$1("div", { class: c(h2._, h2.value) }, p(t2.value));
    return W$1(w, { accordionLayout: n2.compInstance.lfAccordionLayout && 0 === r2, depth: r2, elements: { ripple: W$1("div", { "data-cy": n2.cyAttributes.rippleSurface, "data-lf": n2.lfAttributes.rippleSurface, ref: (e) => {
      e && n2.compInstance.lfRipple && (i.refs.rippleSurfaces[t2.id] = e);
    } }), value: v3 }, events: { onClick: (e) => a.node.click(e, t2), onClickExpand: (e) => a.node.expand(e, t2), onPointerDown: (e) => a.node.pointerDown(e, t2) }, expanded: o3, manager: l, node: t2, selected: f$12 });
  }));
  if (k2) return W$1("div", { class: c(f$1._, f$1.nodesWrapper) }, x2);
  if (h) {
    const { noMatches: t2 } = s;
    return W$1("div", { class: c(t2._) }, W$1("div", { class: c(t2._, t2.icon) }), W$1("div", { class: c(t2._, t2.text) }, 'No matches found for "', W$1("strong", { class: c(t2._, t2.filter) }, h), '".'));
  }
  return W$1("div", { class: c(f$1._, f$1.nodesWrapper) });
}, empty: () => {
  const { controller: r } = t(), { compInstance: o2, manager: i } = r.get, { theme: a } = i, { bemClass: n2 } = a, s = r.get.blocks, { emptyData: l } = s, d = r.get.parts;
  return W$1("div", { class: n2(l._), part: d.emptyData }, W$1("div", { class: n2(l._, l.text) }, o2.lfEmpty));
} }), x = (e) => ({ filter: { input: (t) => {
  var _a, _b;
  const r = e(), { controller: o2 } = r, i = o2.get.compInstance, a = ((_a = t.detail.inputValue) == null ? void 0 : _a.toLowerCase()) || "";
  clearTimeout(i._filterTimeout), i._filterTimeout = setTimeout((() => {
    o2.set.filter.setValue(a), o2.set.filter.apply(a);
  }), 300), (_b = i.onLfEvent) == null ? void 0 : _b.call(i, t, "lf-event");
} }, node: { click: (t, r) => {
  var _a;
  const o2 = e(), { controller: i } = o2, a = i.get.compInstance;
  i.set.selection.set(r);
  const n2 = i.get.isSelected(r);
  (_a = a.onLfEvent) == null ? void 0 : _a.call(a, t, "click", { node: r, selected: n2 });
}, expand: (t, r) => {
  var _a;
  const o2 = e(), { controller: i } = o2, a = i.get.compInstance;
  i.set.expansion.toggle(r), (_a = a.onLfEvent) == null ? void 0 : _a.call(a, t, "click", { node: r, expansion: true });
}, pointerDown: (t, r) => {
  var _a;
  const o2 = e(), { controller: i } = o2, a = i.get.compInstance;
  (_a = a.onLfEvent) == null ? void 0 : _a.call(a, t, "pointerdown", { node: r });
} } });
var y, _, z, C, E, S, D, j, I = function(e, t, r, o2) {
  if ("a" === r && !o2) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !o2 : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === r ? o2 : "a" === r ? o2.call(e) : o2 ? o2.value : t.get(e);
}, L = function(e, t, r, o2, i) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, r), r;
};
const T = class {
  constructor(e) {
    n(this, e), this.lfEvent = I$1(this, "lf-tree-event"), y.add(this), this.expandedNodes = /* @__PURE__ */ new Set(), this.hiddenNodes = /* @__PURE__ */ new Set(), this.selectedNode = null, this.lfAccordionLayout = true, this.lfDataset = null, this.lfEmpty = "Empty data.", this.lfFilter = true, this.lfGrid = false, this.lfRipple = true, this.lfSelectable = true, this.lfStyle = "", this.lfUiSize = "medium", _.set(this, void 0), z.set(this, LF_TREE_BLOCKS), C.set(this, LF_TREE_PARTS), E.set(this, LF_STYLE_ID), S.set(this, LF_WRAPPER_ID), this._filterValue = "", D.set(this, void 0);
  }
  handleDatasetChange() {
    this.expandedNodes = /* @__PURE__ */ new Set(), this.hiddenNodes = /* @__PURE__ */ new Set(), this.selectedNode = null, this._filterValue = "", I(this, y, "m", j).call(this);
  }
  handleInitialDepthChange() {
    this.expandedNodes = /* @__PURE__ */ new Set(), I(this, y, "m", j).call(this);
  }
  onLfEvent(e, t, r) {
    var _a;
    const { effects: o2 } = I(this, _, "f"), { node: i, selected: a } = r || {};
    if ("pointerdown" === t && i && this.lfRipple) {
      const t2 = (_a = I(this, D, "f")) == null ? void 0 : _a.elements.refs.rippleSurfaces[i.id];
      t2 && o2.ripple(e, t2);
    }
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e, node: i, ...(r == null ? void 0 : r.expansion) ? { expansion: true } : {}, ...null != a ? { selected: a } : {} });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_TREE_PROPS.map(((e2) => [e2, this[e2]]));
    return Object.fromEntries(e);
  }
  async refresh() {
    mt(this);
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
    L(this, _, await o(this)), L(this, D, (e = { blocks: I(this, z, "f"), compInstance: this, cyAttributes: CY_ATTRIBUTES, dataset: () => this.lfDataset, columns: () => {
      var _a;
      return ((_a = this.lfDataset) == null ? void 0 : _a.columns) || [];
    }, isGrid: () => {
      var _a, _b;
      return !(!this.lfGrid || !((_b = (_a = this.lfDataset) == null ? void 0 : _a.columns) == null ? void 0 : _b.length));
    }, lfAttributes: LF_ATTRIBUTES, manager: I(this, _, "f"), parts: I(this, C, "f"), isExpanded: (e2) => this.expandedNodes.has(e2), isHidden: (e2) => this.hiddenNodes.has(e2), isSelected: (e2) => this.selectedNode === e2, filterValue: () => this._filterValue }, t = { expansion: { toggle: (e2) => {
      this.expandedNodes.has(e2) ? this.expandedNodes.delete(e2) : this.expandedNodes.add(e2), this.expandedNodes = new Set(this.expandedNodes);
    } }, selection: { set: (e2) => {
      this.lfSelectable && (this.selectedNode = e2);
    } }, filter: { setValue: (e2) => {
      this._filterValue = e2;
    }, apply: (e2) => {
      const { filter: t2 } = I(this, _, "f").data.node;
      if (!e2) return void (this.hiddenNodes = /* @__PURE__ */ new Set());
      const { ancestorNodes: r2, remainingNodes: o2 } = t2(this.lfDataset, { value: e2 }, true), i = new Set(o2);
      r2 && r2.forEach(((e3) => i.delete(e3))), this.hiddenNodes = i;
    } } }, r = () => I(this, D, "f"), { controller: { get: g(e), set: u(t) }, elements: { jsx: k(r), refs: { rippleSurfaces: {}, filterField: null } }, handlers: x(r) })), I(this, y, "m", j).call(this);
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
    const { bemClass: t, setLfStyle: r } = I(this, _, "f").theme, { tree: o2 } = I(this, z, "f"), { lfDataset: a, lfStyle: n2, lfGrid: s } = this, l = (_a = I(this, D, "f")) == null ? void 0 : _a.elements.jsx, d = !((_b = a == null ? void 0 : a.nodes) == null ? void 0 : _b.length);
    return W$1(L$1, { key: "b7b5f145306b1d87cc1fec34efd6ecfdecb6428e" }, n2 && W$1("style", { key: "831b2a9aba3505202b4b15e88e8c2efaaa6a1c82", id: I(this, E, "f") }, r(this)), W$1("div", { key: "eb3037beff1fed2b61a78fd62733ceef9b91847b", id: I(this, S, "f") }, W$1("div", { key: "7a6b3136591ae2c4bdbcb90de95c65c98b4062bd", class: t(o2._) + (s ? " tree--grid" : ""), part: I(this, C, "f").tree }, l == null ? void 0 : l.filter(), l == null ? void 0 : l.header(), d ? l == null ? void 0 : l.empty() : l == null ? void 0 : l.nodes())));
  }
  disconnectedCallback() {
    var _a;
    (_a = I(this, _, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return G(this);
  }
  static get watchers() {
    return { lfDataset: ["handleDatasetChange"], lfInitialExpansionDepth: ["handleInitialDepthChange"] };
  }
};
_ = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), S = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakSet(), j = function() {
  var _a;
  const e = this.lfInitialExpansionDepth, t = (r, o2) => {
    var _a2;
    for (const i of r) (null == e || o2 < e) && this.expandedNodes.add(i), ((_a2 = i.children) == null ? void 0 : _a2.length) && t(i.children, o2 + 1);
  };
  t(((_a = this.lfDataset) == null ? void 0 : _a.nodes) || [], 0), this.expandedNodes = new Set(this.expandedNodes);
}, T.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}:host{display:block;font-family:var(--lf-tree-font-family, var(--lf-font-family-primary));font-size:var(--lf-tree-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}:host([lf-accordion-layout]) .node[data-depth="0"]{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);font-size:1em;height:var(--lf-tree-accordion-node-height, 4em)}:host([lf-accordion-layout]) .node[data-depth="0"] .node__value{font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;font-size:1em}:host([lf-selectable]) .node:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.075);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.175);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.225);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.tree{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-bg, var(--lf-color-bg)), 0.275);color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);padding:var(--lf-tree-padding, 0)}.tree__filter{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));border-bottom-left-radius:0;border-bottom-right-radius:0;background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.875);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px);position:sticky;top:0;z-index:1}.tree--grid{display:flex;flex-direction:column;overflow:hidden}.tree--grid .header{position:sticky;top:0;z-index:2;background:var(--lf-tree-color-bg, rgba(0, 0, 0, 0.3));backdrop-filter:blur(10px);font-size:0.85em;line-height:1.2}.tree--grid .header__row{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(120px, auto);column-gap:0.5em;padding:0.5em 1em 0.25em 3.25em;box-sizing:border-box}.tree--grid .header__cell{font-size:0.875em;font-weight:400;line-height:1.25em;letter-spacing:0.2em;font-weight:600;text-transform:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.node{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);box-sizing:border-box;height:var(--lf-tree-node-height, 2em);padding:var(--lftree-node-padding, 0 1em);position:relative}.node__content{width:100%;height:100%;align-items:center;display:flex}.node__dropdown,.node__expand,.node__icon{cursor:pointer;margin:0}.node__dropdown,.node__expand{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);overflow:hidden}.node__dropdown:hover,.node__expand:hover{opacity:0.75}.node__dropdown{-webkit-mask:var(--lf-icon-dropdown);mask:var(--lf-icon-dropdown);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__dropdown--expanded{transform:rotate(180deg)}.node__dropdown--expanded:hover{opacity:0.75}.node__dropdown--hidden{visibility:hidden}.node__expand{-webkit-mask:var(--lf-icon-collapsed);mask:var(--lf-icon-collapsed);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--expanded{-webkit-mask:var(--lf-icon-expanded);mask:var(--lf-icon-expanded);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--hidden{visibility:hidden}.node__icon{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__padding{height:100%;width:calc(1.75em * var(--lf_tree_padding_multiplier))}.node__value{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;margin:0 0 0 0.5em;width:100%}.node__value--grid .node__grid{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(120px, auto);column-gap:0.5em;align-items:center;padding:0 1em 0 0;box-sizing:border-box;min-height:100%}.node__value--grid .node__grid-cell{font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;display:flex;align-items:center;min-height:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.node__value--grid .node__grid-cell--value{font-weight:500}.no-matches{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));align-items:center;box-sizing:border-box;display:flex;justify-content:center;margin:auto;padding:1em;width:100%}.no-matches__icon{-webkit-mask:var(--lf-icon-warning);mask:var(--lf-icon-warning);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin-right:0.375em}.no-matches__text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:400;line-height:1.25em;letter-spacing:0.2em}.no-matches__filter{color:var(--lf-primary-color)}.empty-data{width:100%;height:100%;font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:1em;align-items:center;display:flex;justify-content:center;margin:1em 0}';
export {
  T as lf_tree
};
