import { n, V as V$1, b8 as LF_TREE_BLOCKS, b9 as LF_TREE_PARTS, C as CY_ATTRIBUTES, f as LF_ATTRIBUTES, b as LF_STYLE_ID, c as LF_WRAPPER_ID, ba as LF_TREE_PROPS, p as pt, D as D$1, W as W$1, z as z$1, bb as LF_TREE_CSS_VARIABLES } from "./index-CeSp9ZDS.js";
import { a } from "./p-Dl9cVpAY-UT28Wpzm.js";
import { r } from "./p-CKijk88y-j_wd_eAs.js";
const m = ({ depth: t, expanded: r2 = false, manager: i, node: o, onClickExpand: n2, type: d }) => {
  const { get: c } = i.assets, { bemClass: f } = i.theme;
  switch (d) {
    case "dropdown":
      return D$1("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.dropdown, { expanded: r2 }), "data-cy": CY_ATTRIBUTES.maskedSvg });
    case "expand":
      return D$1("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.expand, { expanded: r2 }), "data-cy": CY_ATTRIBUTES.maskedSvg, onClick: n2 });
    case "icon":
      const { style: i2 } = c(`./assets/svg/${o.icon}.svg`);
      return D$1("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.icon), "data-cy": CY_ATTRIBUTES.maskedSvg, style: i2 });
    case "padding":
      return D$1("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.padding), style: { [LF_TREE_CSS_VARIABLES.multiplier]: t.toString() } });
    default:
      return D$1("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.expand, { hidden: true }) });
  }
}, b = (t) => {
  var _a, _b;
  const { manager: r2 } = t, { bemClass: i } = r2.theme, { accordionLayout: o, depth: n2, elements: s, events: c, expanded: f, node: h, selected: p } = t || {}, u = D$1(m, h.icon ? { manager: r2, node: h, type: "icon" } : { manager: r2, type: "placeholder" });
  return o ? D$1("div", { class: i(LF_TREE_BLOCKS.node._, null, { expanded: f, selected: p }), "data-cy": CY_ATTRIBUTES.node, "data-depth": n2.toString(), key: h.id, onClick: c.onClickExpand, onPointerDown: c.onPointerDown, part: LF_TREE_PARTS.node, title: h.description }, D$1("div", { class: i(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.content) }, s.ripple, u, s.value, D$1(m, ((_a = h.children) == null ? void 0 : _a.length) ? { expanded: f, manager: r2, node: h, type: "dropdown" } : { manager: r2, type: "placeholder" }))) : D$1("div", { class: i(LF_TREE_BLOCKS.node._, null, { expanded: f, selected: p }), "data-cy": CY_ATTRIBUTES.node, "data-depth": n2.toString(), key: h.id, onClick: c.onClick, onPointerDown: c.onPointerDown, title: h.description }, D$1("div", { class: "node__content" }, s.ripple, D$1(m, { depth: n2, manager: r2, type: "padding" }), D$1(m, ((_b = h.children) == null ? void 0 : _b.length) ? { expanded: f, manager: r2, node: h, onClickExpand: c.onClickExpand, type: "expand" } : { manager: r2, type: "placeholder" }), u, s.value));
}, v = (t) => ({ filter: () => {
  const { controller: r2, handlers: i } = t(), { compInstance: o, manager: n2 } = r2.get, { theme: a2 } = n2, { bemClass: s, get: l } = a2, d = r2.get.blocks.tree;
  return o.lfFilter ? D$1("lf-textfield", { class: s(d._, d.filter), lfStretchX: true, lfIcon: l.current().variables["--lf-icon-search"], lfLabel: "Search...", lfStyling: "flat", "onLf-textfield-event": (e) => i.filter.input(e), ref: (e) => t().elements.refs.filterField = e }) : null;
}, header: () => {
  const { controller: r2 } = t(), i = r2.get.columns(), { blocks: o, isGrid: n2, manager: a2, parts: s } = r2.get;
  if (!(n2() && i.length > 0)) return null;
  const { bemClass: l } = a2.theme, d = o.header;
  return D$1("div", { class: l(d._), part: s.header }, D$1("div", { class: l(d._, d.row) }, i.map(((t2, r3) => D$1("div", { class: l(d._, d.cell), part: 0 === r3 ? s.headerRow : void 0, "data-column": t2.id, "data-index": r3.toString(), key: t2.id }, t2.title)))));
}, nodes: () => {
  const r$1 = t(), { controller: i, elements: o, handlers: n2 } = r$1, { get: a2 } = i, { blocks: s, manager: l, parts: d } = a2, { bemClass: c } = l.theme, { tree: f } = s, h = l.data.cell.stringify, p = a2.filterValue() || "", u = a2.columns(), m2 = a2.isGrid(), v2 = a2.dataset(), w2 = a2.manager.data.node.traverseVisible(v2 == null ? void 0 : v2.nodes, { isExpanded: a2.isExpanded, isHidden: a2.isHidden, isSelected: a2.isSelected, forceExpand: !!p }), k2 = w2.length > 0, y2 = w2.map((({ node: t2, depth: r$12, expanded: i2, selected: f2 }) => {
    const p2 = s.node, v3 = ((t3) => {
      if (!m2 || !u.length) return null;
      const r$13 = s.node;
      return D$1("div", { class: c(r$13._, r$13.grid), part: d.node + "-grid" }, u.map(((r$14, i3) => ((t4, r$15, i4) => {
        var _a;
        const o2 = s.node, n3 = (_a = t4.cells) == null ? void 0 : _a[r$15.id];
        if (!n3) {
          const n4 = c(o2._, o2.gridCell);
          return D$1("div", { class: i4 ? n4 + " value" : n4, "data-column": r$15.id }, i4 ? h(t4.value) : "");
        }
        const d2 = n3.shape || "text", f3 = "text" === d2 || "number" === d2 || "slot" === d2, p3 = l.data.cell.shapes.get(n3);
        Object.prototype.hasOwnProperty.call(p3, "lfValue") || (p3.lfValue = n3.value);
        const u2 = p3.lfValue ?? n3.value;
        return D$1("div", { class: c(o2._, o2.gridCell), "data-column": r$15.id }, f3 ? h(u2) : D$1(r, { framework: l, shape: d2, index: 0, cell: p3, eventDispatcher: async (e) => a2.compInstance.onLfEvent(e, "lf-event", { node: t4 }) }));
      })(t3, r$14, 0 === i3))));
    })(t2), w3 = a2.compInstance.lfGrid && v3 ? D$1("div", { class: c(p2._, p2.value, { grid: true }) }, v3) : D$1("div", { class: c(p2._, p2.value) }, h(t2.value));
    return D$1(b, { accordionLayout: a2.compInstance.lfAccordionLayout && 0 === r$12, depth: r$12, elements: { ripple: D$1("div", { "data-cy": a2.cyAttributes.rippleSurface, "data-lf": a2.lfAttributes.rippleSurface, ref: (e) => {
      e && a2.compInstance.lfRipple && (o.refs.rippleSurfaces[t2.id] = e);
    } }), value: w3 }, events: { onClick: (e) => n2.node.click(e, t2), onClickExpand: (e) => n2.node.expand(e, t2), onPointerDown: (e) => n2.node.pointerDown(e, t2) }, expanded: i2, manager: l, node: t2, selected: f2 });
  }));
  if (k2) return D$1("div", { class: c(f._, f.nodesWrapper) }, y2);
  if (p) {
    const { noMatches: t2 } = s;
    return D$1("div", { class: c(t2._) }, D$1("div", { class: c(t2._, t2.icon) }), D$1("div", { class: c(t2._, t2.text) }, 'No matches found for "', D$1("strong", { class: c(t2._, t2.filter) }, p), '".'));
  }
  return D$1("div", { class: c(f._, f.nodesWrapper) });
}, empty: () => {
  const { controller: r2 } = t(), { compInstance: i, manager: o } = r2.get, { theme: n2 } = o, { bemClass: a2 } = n2, s = r2.get.blocks, { emptyData: l } = s, d = r2.get.parts;
  return D$1("div", { class: a2(l._), part: d.emptyData }, D$1("div", { class: a2(l._, l.text) }, i.lfEmpty));
} }), w = (e) => ({ filter: { input: (t) => {
  var _a, _b;
  const r2 = e(), { controller: i } = r2, o = i.get.compInstance, n2 = ((_a = t.detail.inputValue) == null ? void 0 : _a.toLowerCase()) || "";
  clearTimeout(o._filterTimeout), o._filterTimeout = setTimeout((() => {
    i.set.filter.setValue(n2), i.set.filter.apply(n2);
  }), 300), (_b = o.onLfEvent) == null ? void 0 : _b.call(o, t, "lf-event");
} }, node: { click: (t, r2) => {
  var _a;
  const i = e(), { controller: o } = i, n2 = o.get.compInstance;
  o.set.state.selection.set(r2), (_a = n2.onLfEvent) == null ? void 0 : _a.call(n2, t, "click", { node: r2 });
}, expand: (t, r2) => {
  var _a;
  const i = e(), { controller: o } = i, n2 = o.get.compInstance;
  o.set.state.expansion.toggle(r2), (_a = n2.onLfEvent) == null ? void 0 : _a.call(n2, t, "click", { node: r2 });
}, pointerDown: (t, r2) => {
  var _a;
  const i = e(), { controller: o } = i, n2 = o.get.compInstance;
  (_a = n2.onLfEvent) == null ? void 0 : _a.call(n2, t, "pointerdown", { node: r2 });
} } }), k = /* @__PURE__ */ new WeakMap();
let y = 0;
const x = (e) => {
  if (null == e) return [];
  if (Array.isArray(e)) return e.map(((e2) => "string" == typeof e2 || "number" == typeof e2 ? String(e2) : null)).filter(((e2) => !!e2));
  if (e instanceof Set) return Array.from(e).map(((e2) => "string" == typeof e2 || "number" == typeof e2 ? String(e2) : null)).filter(((e2) => !!e2));
  if ("string" == typeof e) {
    try {
      const t = JSON.parse(e);
      if (Array.isArray(t)) return x(t);
    } catch (t) {
      const r2 = e.split(/[\,\s]+/).map(((e2) => e2.trim())).filter(Boolean);
      if (r2.length) return r2;
    }
    return e ? [e] : [];
  }
  return [];
}, _ = (e) => null == e ? [] : Array.isArray(e) ? e : [e], z = (e) => {
  if (!e) return null;
  const t = e.id;
  if (null != t) {
    const r3 = String(t).trim();
    if (r3) return k.delete(e), r3;
  }
  const r2 = k.get(e);
  if (r2) return e.id = r2, r2;
  var i;
  const o = `${("string" == typeof (i = e.value) && i.trim() ? i.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 32) || null : "number" != typeof i || Number.isNaN(i) ? null : String(i)) ?? "node"}-${(++y).toString(36)}`;
  return k.set(e, o), e.id = o, o;
}, S = (e) => {
  const t = [];
  for (const r2 of e) if ("string" == typeof r2 || "number" == typeof r2) {
    const e2 = String(r2);
    e2 && t.push(e2);
  } else {
    const e2 = z(r2);
    e2 && t.push(e2);
  }
  return t;
}, P = (e, t) => {
  let r2, i = false;
  const o = (e2) => {
    var r3, o2;
    (r3 = x(t.getProp())).length === (o2 = e2).length && r3.every(((e3, t2) => e3 === o2[t2])) || (i = true, t.setProp([...e2]), i = false);
  };
  return { syncProp: o, applyIdsWithSanitization: (e2, i2, o2) => {
    const n2 = x(e2), a2 = t.getManager();
    if (!a2) return r2 = [...n2], o2(n2, i2), n2;
    const { ids: s } = a2.data.node.sanitizeIds(t.getDataset(), n2);
    return r2 = void 0, o2(s, i2), s;
  }, handlePropChange: (e2, t2) => {
    if (i) return;
    const r3 = t2(x(e2), { emit: false, updateProp: false });
    o(r3);
  }, initialisePersistentState: (e2, t2, i2) => {
    const o2 = x(e2);
    return o2.length ? (t2(o2, { emit: false, updateProp: true }), void (r2 = void 0)) : r2 && r2.length ? (t2(r2, { emit: false, updateProp: true }), void (r2 = void 0)) : void (i2 && i2());
  }, reconcileAfterDatasetChange: (e2, r3, i2) => {
    const n2 = x(t.getProp());
    if (n2.length) {
      const e3 = r3(n2, { emit: false, updateProp: false });
      o(e3);
    } else {
      if (e2 && e2.length) {
        const t2 = r3(e2, { emit: false, updateProp: false });
        if (o(t2), t2.length) return;
      }
      i2 && i2();
    }
  }, getPendingIds: () => r2, clearPendingIds: () => {
    r2 = void 0;
  } };
};
var C, E, D, I, A, N, M, W, T, j, L, F, H, V = function(e, t, r2, i) {
  if ("a" === r2 && !i) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !i : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === r2 ? i : "a" === r2 ? i.call(e) : i ? i.value : t.get(e);
}, $ = function(e, t, r2, i, o) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, r2), r2;
};
const B = class {
  constructor(e) {
    n(this, e), this.lfEvent = V$1(this, "lf-tree-event"), C.add(this), this.expandedNodes = /* @__PURE__ */ new Set(), this.hiddenNodes = /* @__PURE__ */ new Set(), this.selectedNode = null, this.lfAccordionLayout = true, this.lfDataset = null, this.lfEmpty = "Empty data.", this.lfFilter = true, this.lfGrid = false, this.lfRipple = true, this.lfSelectable = true, this.lfStyle = "", this.lfUiSize = "medium", E.set(this, void 0), D.set(this, LF_TREE_BLOCKS), I.set(this, LF_TREE_PARTS), A.set(this, CY_ATTRIBUTES), N.set(this, LF_ATTRIBUTES), M.set(this, LF_STYLE_ID), W.set(this, LF_WRAPPER_ID), this._filterValue = "", T.set(this, void 0), j.set(this, void 0), L.set(this, void 0);
  }
  handleDatasetChange() {
    if (!V(this, E, "f") || !V(this, j, "f") || !V(this, L, "f")) return;
    const e = new Set(this.expandedNodes), t = z(this.selectedNode);
    V(this, j, "f").reconcileAfterDatasetChange(e), V(this, L, "f").reconcileAfterDatasetChange(t), this.hiddenNodes = /* @__PURE__ */ new Set();
  }
  handleExpandedPropChange(e) {
    V(this, j, "f") && V(this, j, "f").handlePropChange(e);
  }
  handleSelectedPropChange(e) {
    V(this, L, "f") && V(this, L, "f").handlePropChange(e);
  }
  handleInitialDepthChange() {
    V(this, j, "f") && V(this, j, "f").handleInitialDepthChange(new Set(this.expandedNodes));
  }
  handleSelectableChange(e) {
    V(this, L, "f") && V(this, L, "f").handleSelectableChange(!!e);
  }
  handleFilterToggle(e) {
    e || (this._filterValue = "", this.hiddenNodes = /* @__PURE__ */ new Set());
  }
  onLfEvent(e, t, r2 = {}) {
    var _a, _b;
    const i = V(this, E, "f"), o = r2.node ?? null;
    if (i && "pointerdown" === t && this.lfRipple) {
      const t2 = z(o), r3 = t2 ? (_a = V(this, T, "f")) == null ? void 0 : _a.elements.refs.rippleSurfaces[t2] : void 0;
      r3 && i.effects.ripple(e, r3);
    }
    const n2 = { comp: this, eventType: t, id: (_b = this.rootElement) == null ? void 0 : _b.id, originalEvent: e, node: o ?? void 0, expandedNodeIds: r2.expandedNodeIds ?? (V(this, j, "f") ? V(this, j, "f").getIds() : []), selectedNodeIds: r2.selectedNodeIds ?? (V(this, L, "f") ? V(this, L, "f").getIds() : []) };
    this.lfEvent.emit(n2);
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
  async getExpandedNodeIds() {
    return V(this, j, "f") ? V(this, j, "f").getIds() : [];
  }
  async getSelectedNodeIds() {
    return V(this, L, "f") ? V(this, L, "f").getIds() : [];
  }
  async setExpandedNodes(e) {
    if (!V(this, j, "f")) return;
    if (null == e) return void V(this, j, "f").applyIds([], { emit: true, updateProp: true });
    const t = _(e), r2 = S(t);
    V(this, j, "f").applyIds(r2, { emit: true, updateProp: true });
  }
  async setSelectedNodes(e) {
    V(this, L, "f") && (null != e ? V(this, L, "f").applyTargets(e, { emit: true, updateProp: true }) : V(this, L, "f").applyIds([], { emit: true, updateProp: true }));
  }
  async selectByPredicate(e) {
    if (!V(this, E, "f") || !this.lfDataset) return;
    const t = V(this, E, "f").data.node.find(this.lfDataset, e);
    if (t) return await this.setSelectedNodes(t), t;
    await this.setSelectedNodes(null);
  }
  async unmount(e = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), e);
  }
  connectedCallback() {
    V(this, E, "f") && V(this, E, "f").theme.register(this);
  }
  async componentWillLoad() {
    var e;
    $(this, E, await a(this)), $(this, T, { controller: { get: { blocks: V(this, D, "f"), columns: () => {
      var _a;
      return ((_a = this.lfDataset) == null ? void 0 : _a.columns) || [];
    }, compInstance: this, cyAttributes: V(this, A, "f"), dataset: () => this.lfDataset, filterValue: () => this._filterValue, isExpanded: (e2) => {
      const t = z(e2);
      return !!t && this.expandedNodes.has(t);
    }, isGrid: () => {
      var _a, _b;
      return !(!this.lfGrid || !((_b = (_a = this.lfDataset) == null ? void 0 : _a.columns) == null ? void 0 : _b.length));
    }, isHidden: (e2) => this.hiddenNodes.has(e2), isSelected: (e2) => this.selectedNode === e2, lfAttributes: V(this, N, "f"), manager: V(this, E, "f"), parts: V(this, I, "f"), state: { expansion: { ids: () => {
      var _a;
      return ((_a = V(this, j, "f")) == null ? void 0 : _a.getIds()) ?? Array.from(this.expandedNodes);
    }, nodes: () => this.expandedNodes }, selection: { ids: () => {
      if (V(this, L, "f")) return V(this, L, "f").getIds();
      const e2 = z(this.selectedNode);
      return e2 ? [e2] : [];
    }, node: () => this.selectedNode } }, expandedProp: () => this.lfExpandedNodeIds, selectedProp: () => this.lfSelectedNodeIds, initialExpansionDepth: () => this.lfInitialExpansionDepth, selectable: () => this.lfSelectable, allowsMultiSelect: () => V(this, C, "m", F).call(this), canSelectNode: (e2) => V(this, C, "m", H).call(this, e2) }, set: { filter: { apply: (e2) => {
      if (!V(this, E, "f") || !this.lfDataset) return void (this.hiddenNodes = /* @__PURE__ */ new Set());
      if (!e2) return void (this.hiddenNodes = /* @__PURE__ */ new Set());
      const { filter: t } = V(this, E, "f").data.node, { ancestorNodes: r2, remainingNodes: i } = t(this.lfDataset, { value: e2 }, true), o = new Set(i);
      r2 && r2.forEach(((e3) => o.delete(e3))), this.hiddenNodes = o;
    }, setValue: (e2) => {
      this._filterValue = e2;
    } }, state: { expansion: { apply: () => {
      var _a, _b;
      const e2 = (_a = V(this, j, "f")) == null ? void 0 : _a.getIds();
      void 0 !== e2 && ((_b = V(this, j, "f")) == null ? void 0 : _b.applyIds(e2, { emit: false, updateProp: true }));
    }, toggle: (e2) => {
      var _a;
      return (_a = V(this, j, "f")) == null ? void 0 : _a.toggle(e2);
    }, setNodes: (e2) => {
      this.expandedNodes = new Set(e2);
    }, setProp: (e2) => {
      this.lfExpandedNodeIds = e2;
    } }, selection: { apply: () => {
      var _a, _b;
      const e2 = (_a = V(this, L, "f")) == null ? void 0 : _a.getIds();
      void 0 !== e2 && ((_b = V(this, L, "f")) == null ? void 0 : _b.applyIds(e2, { emit: false, updateProp: true }));
    }, set: (e2) => {
      var _a;
      return (_a = V(this, L, "f")) == null ? void 0 : _a.applyTargets(e2, { emit: true, updateProp: true, node: e2 });
    }, clear: () => {
      var _a;
      (_a = V(this, L, "f")) == null ? void 0 : _a.clearSelection({ emit: true, updateProp: true });
    }, setNode: (e2) => {
      this.selectedNode = e2 ?? null;
    }, setProp: (e2) => {
      this.lfSelectedNodeIds = e2;
    } } } } }, elements: { jsx: v(e = () => V(this, T, "f")), refs: { rippleSurfaces: {}, filterField: null } }, handlers: w(e) }), $(this, j, ((e2) => {
      const { controller: t } = e2(), r2 = P(0, { getProp: () => t.get.expandedProp(), setProp: (e3) => t.set.state.expansion.setProp(e3), getDataset: () => t.get.dataset(), getManager: () => t.get.manager }), i = () => {
        const e3 = t.get.state.expansion.nodes();
        return Array.from(e3 ?? /* @__PURE__ */ new Set());
      }, o = (e3, i2 = {}) => {
        t.set.state.expansion.setNodes(e3), false !== i2.updateProp && r2.syncProp(e3);
      }, n2 = (e3, t2 = {}) => r2.applyIdsWithSanitization(e3, t2, ((e4, t3) => {
        o(e4, t3);
      })), a2 = (e3) => {
        const r3 = t.get.initialExpansionDepth(), i2 = t.get.dataset(), n3 = (i2 == null ? void 0 : i2.nodes) ?? [], a3 = e3 ? new Set(e3) : /* @__PURE__ */ new Set(), s = /* @__PURE__ */ new Set(), l = (e4, t2) => {
          for (const i3 of e4) {
            const e5 = z(i3);
            e5 && (null == r3 || t2 < r3 || a3.has(e5)) && s.add(e5), Array.isArray(i3.children) && i3.children.length > 0 && l(i3.children, t2 + 1);
          }
        };
        l(n3, 0), o(Array.from(s), {});
      };
      return { applyIds: n2, handlePropChange: (e3) => {
        r2.handlePropChange(e3, n2);
      }, applyInitialExpansion: a2, reconcileAfterDatasetChange: (e3) => {
        const t2 = e3 ? Array.from(e3) : null;
        r2.reconcileAfterDatasetChange(t2, n2, (() => {
          a2(e3);
        }));
      }, handleInitialDepthChange(e3) {
        a2(e3);
      }, toggle: (e3) => {
        const t2 = z(e3);
        if (!t2) return;
        const r3 = new Set(i());
        r3.has(t2) ? r3.delete(t2) : r3.add(t2), n2(Array.from(r3), { emit: true, updateProp: true, node: e3 });
      }, getIds: () => i(), initialisePersistentState: (e3) => {
        r2.initialisePersistentState(e3, n2, (() => {
          a2(new Set(i()));
        }));
      } };
    })((() => V(this, T, "f")))), $(this, L, ((e2) => {
      const { controller: t } = e2(), r2 = P(0, { getProp: () => t.get.selectedProp(), setProp: (e3) => t.set.state.selection.setProp(e3), getDataset: () => t.get.dataset(), getManager: () => t.get.manager });
      let i = [];
      const o = (e3, o2, n3 = {}) => {
        const a3 = t.get.allowsMultiSelect() ? e3 : e3.slice(0, 1);
        return i = [...a3], t.set.state.selection.setNode(i.length ? o2[0] ?? null : null), false !== n3.updateProp && r2.syncProp(i), i;
      }, n2 = (e3 = {}) => (r2.clearPendingIds(), i = [], t.set.state.selection.setNode(null), false !== e3.updateProp && r2.syncProp([]), i), a2 = (e3, i2 = {}) => {
        if (!t.get.selectable()) return n2(i2);
        let a3 = [];
        return r2.applyIdsWithSanitization(e3, i2, ((e4, r3) => {
          const i3 = t.get.manager, n3 = t.get.dataset();
          if (i3 && n3) {
            const s = i3.data.node.sanitizeIds(n3, e4, { predicate: (e5) => t.get.canSelectNode(e5), limit: t.get.allowsMultiSelect() ? void 0 : 1 });
            a3 = o(s.ids, s.nodes, r3);
          } else {
            const i4 = t.get.allowsMultiSelect() ? e4 : e4.slice(0, 1);
            a3 = o(i4, [], r3);
          }
        })), a3;
      };
      return { applyIds: a2, applyTargets: (e3, t2 = {}) => {
        if (null == e3) return a2([], t2);
        const r3 = _(e3), i2 = S(r3);
        return a2(i2, t2);
      }, handlePropChange: (e3) => {
        r2.handlePropChange(e3, a2);
      }, reconcileAfterDatasetChange: (e3) => {
        r2.reconcileAfterDatasetChange(e3 ? [e3] : null, a2, (() => {
          n2({ updateProp: true });
        }));
      }, initialisePersistentState: (e3) => {
        r2.initialisePersistentState(e3, a2, (() => {
          n2({ updateProp: true });
        }));
      }, handleSelectableChange: (e3) => {
        e3 || n2({ updateProp: true });
      }, getIds: () => [...i], clearSelection: n2 };
    })((() => V(this, T, "f")))), V(this, j, "f").initialisePersistentState(this.lfExpandedNodeIds), V(this, L, "f").initialisePersistentState(this.lfSelectedNodeIds), V(this, L, "f").handleSelectableChange(this.lfSelectable), this.handleDatasetChange();
  }
  componentDidLoad() {
    const { info: e } = V(this, E, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = V(this, E, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { debug: e } = V(this, E, "f");
    e.info.update(this, "did-render");
  }
  render() {
    var _a, _b;
    const { bemClass: t, setLfStyle: r2 } = V(this, E, "f").theme, { tree: i } = V(this, D, "f"), { lfDataset: n2, lfStyle: a2, lfGrid: s } = this, l = (_a = V(this, T, "f")) == null ? void 0 : _a.elements.jsx, d = !((_b = n2 == null ? void 0 : n2.nodes) == null ? void 0 : _b.length);
    return D$1(W$1, { key: "bb981ab53aaaa3837054ca638c97601e46a58cfe" }, a2 && D$1("style", { key: "87d22f0df77b8522e5a1f8465a7f7b49f30a6142", id: V(this, M, "f") }, r2(this)), D$1("div", { key: "e9aaa9ae39004cbc097228bf92cfd17efa336506", id: V(this, W, "f") }, D$1("div", { key: "4f1c47a323a598ad7d22ce45b7ebd49d6ed5fa4e", class: t(i._) + (s ? " tree--grid" : ""), part: V(this, I, "f").tree }, l == null ? void 0 : l.filter(), l == null ? void 0 : l.header(), d ? l == null ? void 0 : l.empty() : l == null ? void 0 : l.nodes())));
  }
  disconnectedCallback() {
    var _a;
    (_a = V(this, E, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return z$1(this);
  }
  static get watchers() {
    return { lfDataset: ["handleDatasetChange"], lfExpandedNodeIds: ["handleExpandedPropChange"], lfSelectedNodeIds: ["handleSelectedPropChange"], lfInitialExpansionDepth: ["handleInitialDepthChange"], lfSelectable: ["handleSelectableChange"], lfFilter: ["handleFilterToggle"] };
  }
};
E = /* @__PURE__ */ new WeakMap(), D = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakMap(), A = /* @__PURE__ */ new WeakMap(), N = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), T = /* @__PURE__ */ new WeakMap(), j = /* @__PURE__ */ new WeakMap(), L = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakSet(), F = function() {
  return false;
}, H = function(e) {
  return !!e && !!this.lfSelectable && true !== e.isDisabled;
}, B.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}:host{display:block;font-family:var(--lf-tree-font-family, var(--lf-font-family-primary));font-size:var(--lf-tree-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}:host([lf-accordion-layout]) .node[data-depth="0"]{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);font-size:1em;height:var(--lf-tree-accordion-node-height, 4em)}:host([lf-accordion-layout]) .node[data-depth="0"] .node__value{font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;font-size:1em}:host([lf-selectable]) .node:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.075);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.175);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.225);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.tree{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-bg, var(--lf-color-bg)), 0.275);color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);padding:var(--lf-tree-padding, 0)}.tree__filter{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));border-bottom-left-radius:0;border-bottom-right-radius:0;background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.875);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px);position:sticky;top:0;z-index:1}.tree--grid{align-content:start;display:grid;height:100%;overflow:auto;width:100%}.tree--grid .header{position:sticky;top:0;z-index:2;background:var(--lf-tree-color-bg, rgba(0, 0, 0, 0.3));backdrop-filter:blur(10px);font-size:0.85em;line-height:1.2}.tree--grid .header__row{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(120px, auto);column-gap:0.5em;padding:0.5em 1em 0.25em 3.25em;box-sizing:border-box}.tree--grid .header__cell{font-size:0.875em;font-weight:400;line-height:1.25em;letter-spacing:0.2em;font-weight:600;text-transform:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.node{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);box-sizing:border-box;height:var(--lf-tree-node-height, 2em);padding:var(--lftree-node-padding, 0 1em);position:relative}.node__content{width:100%;height:100%;align-items:center;display:flex}.node__dropdown,.node__expand,.node__icon{cursor:pointer;margin:0}.node__dropdown,.node__expand{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);overflow:hidden}.node__dropdown:hover,.node__expand:hover{opacity:0.75}.node__dropdown{-webkit-mask:var(--lf-icon-dropdown);mask:var(--lf-icon-dropdown);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__dropdown--expanded{transform:rotate(180deg)}.node__dropdown--expanded:hover{opacity:0.75}.node__dropdown--hidden{visibility:hidden}.node__expand{-webkit-mask:var(--lf-icon-collapsed);mask:var(--lf-icon-collapsed);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--expanded{-webkit-mask:var(--lf-icon-expanded);mask:var(--lf-icon-expanded);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--hidden{visibility:hidden}.node__icon{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__padding{height:100%;width:calc(1.75em * var(--lf_tree_padding_multiplier))}.node__value{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;margin:0 0 0 0.5em;width:100%}.node__value--grid .node__grid{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(120px, auto);column-gap:0.5em;align-items:center;padding:0 1em 0 0;box-sizing:border-box;min-height:100%}.node__value--grid .node__grid-cell{font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;display:flex;align-items:center;min-height:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.node__value--grid .node__grid-cell--value{font-weight:500}.no-matches{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));align-items:center;box-sizing:border-box;display:flex;justify-content:center;margin:auto;padding:1em;width:100%}.no-matches__icon{-webkit-mask:var(--lf-icon-warning);mask:var(--lf-icon-warning);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin-right:0.375em}.no-matches__text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:400;line-height:1.25em;letter-spacing:0.2em}.no-matches__filter{color:var(--lf-primary-color)}.empty-data{width:100%;height:100%;font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:1em;align-items:center;display:flex;justify-content:center;margin:1em 0}';
export {
  B as lf_tree
};
