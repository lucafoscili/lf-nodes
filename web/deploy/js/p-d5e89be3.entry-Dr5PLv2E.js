import { n, H, bd as LF_TREE_BLOCKS, be as LF_TREE_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, bf as LF_TREE_PROPS, f as de, N, U, F, a as LF_ATTRIBUTES, C as CY_ATTRIBUTES, bg as LF_TREE_CSS_VARIABLES } from "./index-SKIQxmfa.js";
import { o } from "./p-BJbvgtBt-D5c3bMa4.js";
const m = ({ depth: t2, expanded: o2 = false, manager: r, node: i, onClickExpand: a, type: d }) => {
  const { get: c } = r.assets, { bemClass: f } = r.theme;
  switch (d) {
    case "dropdown":
      return N("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.dropdown, { expanded: o2 }), "data-cy": CY_ATTRIBUTES.maskedSvg });
    case "expand":
      return N("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.expand, { expanded: o2 }), "data-cy": CY_ATTRIBUTES.maskedSvg, onClick: a });
    case "icon":
      const { style: r2 } = c(`./assets/svg/${i.icon}.svg`);
      return N("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.icon), "data-cy": CY_ATTRIBUTES.maskedSvg, style: r2 });
    case "padding":
      return N("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.padding), style: { [LF_TREE_CSS_VARIABLES.multiplier]: t2.toString() } });
    default:
      return N("div", { class: f(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.expand, { hidden: true }) });
  }
}, v = (t2) => {
  var _a, _b;
  const { manager: o2 } = t2, { bemClass: r } = o2.theme, { accordionLayout: i, depth: a, elements: s, events: c, expanded: f, node: h, selected: p } = t2 || {}, b = N(m, h.icon ? { manager: o2, node: h, type: "icon" } : { manager: o2, type: "placeholder" });
  return i ? N("div", { class: r(LF_TREE_BLOCKS.node._, null, { expanded: f, selected: p }), "data-cy": CY_ATTRIBUTES.node, "data-depth": a.toString(), key: h.id, onClick: c.onClickExpand, onPointerDown: c.onPointerDown, part: LF_TREE_PARTS.node, title: h.description }, N("div", { class: r(LF_TREE_BLOCKS.node._, LF_TREE_BLOCKS.node.content) }, s.ripple, b, s.value, N(m, ((_a = h.children) == null ? void 0 : _a.length) ? { expanded: f, manager: o2, node: h, type: "dropdown" } : { manager: o2, type: "placeholder" }))) : N("div", { class: r(LF_TREE_BLOCKS.node._, null, { expanded: f, selected: p }), "data-cy": CY_ATTRIBUTES.node, "data-depth": a.toString(), key: h.id, onClick: c.onClick, onPointerDown: c.onPointerDown, title: h.description }, N("div", { class: "node__content" }, s.ripple, N(m, { depth: a, manager: o2, type: "padding" }), N(m, ((_b = h.children) == null ? void 0 : _b.length) ? { expanded: f, manager: o2, node: h, onClickExpand: c.onClickExpand, type: "expand" } : { manager: o2, type: "placeholder" }), b, s.value));
};
var u, g, k, w, y, x, z, _, C, E, S, W, D = function(e, t2, o2, r) {
  if ("a" === o2 && !r) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t2 ? e !== t2 || !r : !t2.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === o2 ? r : "a" === o2 ? r.call(e) : r ? r.value : t2.get(e);
}, L = function(e, t2, o2, r, i) {
  if ("function" == typeof t2 ? e !== t2 || true : !t2.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t2.set(e, o2), o2;
};
const M = class {
  constructor(e) {
    n(this, e), this.lfEvent = H(this, "lf-tree-event"), u.add(this), this.expandedNodes = /* @__PURE__ */ new Set(), this.hiddenNodes = /* @__PURE__ */ new Set(), this.selectedNode = null, this.lfAccordionLayout = true, this.lfDataset = null, this.lfFilter = true, this.lfEmpty = "Empty data.", this.lfRipple = true, this.lfSelectable = true, this.lfStyle = "", this.lfUiSize = "medium", g.set(this, void 0), k.set(this, LF_TREE_BLOCKS), w.set(this, LF_TREE_PARTS), y.set(this, LF_STYLE_ID), x.set(this, LF_WRAPPER_ID), z.set(this, {}), _.set(this, void 0), C.set(this, "");
  }
  onLfEvent(e, t2, o2) {
    var _a;
    const { effects: r } = D(this, g, "f"), { expansion: i, node: a } = o2 || {};
    switch (t2) {
      case "click":
        i && ((_a = a.children) == null ? void 0 : _a.length) ? (this.expandedNodes.has(a) ? this.expandedNodes.delete(a) : this.expandedNodes.add(a), this.expandedNodes = new Set(this.expandedNodes)) : a && (this.selectedNode = a);
        break;
      case "pointerdown":
        this.lfRipple && r.ripple(e, D(this, z, "f")[a.id]);
    }
    this.lfEvent.emit({ comp: this, eventType: t2, id: this.rootElement.id, originalEvent: e, node: a });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_TREE_PROPS.map((e2) => [e2, this[e2]]);
    return Object.fromEntries(e);
  }
  async refresh() {
    de(this);
  }
  async unmount(e = 0) {
    setTimeout(() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, e);
  }
  connectedCallback() {
    D(this, g, "f") && D(this, g, "f").theme.register(this);
  }
  async componentWillLoad() {
    L(this, g, await o(this));
  }
  componentDidLoad() {
    const { info: e } = D(this, g, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = D(this, g, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { debug: e } = D(this, g, "f");
    e.info.update(this, "did-render");
  }
  render() {
    var _a;
    const { bemClass: t2, get: o2, setLfStyle: r } = D(this, g, "f").theme, { emptyData: a, tree: n2 } = D(this, k, "f"), { lfDataset: s, lfEmpty: l, lfFilter: d, lfStyle: c } = this, f = !((_a = s == null ? void 0 : s.nodes) == null ? void 0 : _a.length);
    return L(this, z, {}), N(U, { key: "5bb40a2e5b1581d155ac1eb971faa123f2b962d5" }, c && N("style", { key: "d077098b7aa8b831fbb764bf7b28cc03e2113fcd", id: D(this, y, "f") }, r(this)), N("div", { key: "ee7999fbda1372b236647574777921f106186cde", id: D(this, x, "f") }, N("div", { key: "5befccaddf6785110381d505c33376f1e7fdc23f", class: t2(n2._), part: D(this, w, "f").tree }, d && N("lf-textfield", { key: "fd03282db386ca45f1991a14814af5438ca98d5d", class: t2(n2._, n2.filter), lfStretchX: true, lfIcon: o2.current().variables["--lf-icon-search"], lfLabel: "Search...", lfStyling: "flat", "onLf-textfield-event": (e) => {
      this.onLfEvent(e, "lf-event"), "input" === e.detail.eventType && D(this, u, "m", E).call(this, e);
    } }), f ? N("div", { class: t2(a._), part: D(this, w, "f").emptyData }, N("div", { class: t2(a._, a.text) }, l)) : D(this, u, "m", S).call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = D(this, g, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return F(this);
  }
};
g = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakMap(), u = /* @__PURE__ */ new WeakSet(), E = function(e) {
  const { filter: t2 } = D(this, g, "f").data.node;
  clearTimeout(D(this, _, "f")), L(this, _, setTimeout(() => {
    var _a;
    if (L(this, C, (_a = e.detail.inputValue) == null ? void 0 : _a.toLowerCase(), "f"), D(this, C, "f")) {
      const { ancestorNodes: e2, remainingNodes: o2 } = t2(this.lfDataset, { value: D(this, C, "f") }, true);
      this.hiddenNodes = new Set(o2), e2 && e2.forEach((e3) => {
        this.hiddenNodes.delete(e3);
      });
    } else this.hiddenNodes = /* @__PURE__ */ new Set();
  }, 300));
}, S = function() {
  const { bemClass: t2 } = D(this, g, "f").theme, { noMatches: o2 } = D(this, k, "f"), r = [], i = this.lfDataset.nodes;
  for (let e = 0; e < i.length; e++) {
    const t3 = i[e];
    D(this, u, "m", W).call(this, r, t3, 0);
  }
  return r.length ? r : D(this, C, "f") && N("div", { class: t2(o2._) }, N("div", { class: t2(o2._, o2.icon) }), N("div", { class: t2(o2._, o2.text) }, 'No matches found for "', N("strong", { class: t2(o2._, o2.filter) }, D(this, C, "f")), '".'));
}, W = function t(o2, r, i) {
  var _a;
  const { stringify: a } = D(this, g, "f").data.cell;
  this.debugInfo.endTime || (null == this.lfInitialExpansionDepth || this.lfInitialExpansionDepth > i) && this.expandedNodes.add(r);
  const n2 = !!D(this, C, "f") || this.expandedNodes.has(r), s = this.hiddenNodes.has(r), d = this.selectedNode === r, c = { accordionLayout: this.lfAccordionLayout && 0 === i, depth: i, elements: { ripple: N("div", { "data-cy": CY_ATTRIBUTES.rippleSurface, "data-lf": LF_ATTRIBUTES.rippleSurface, ref: (e) => {
    e && this.lfRipple && (D(this, z, "f")[r.id] = e);
  } }), value: N("div", { class: "node__value" }, a(r.value)) }, events: { onClick: (e) => {
    this.onLfEvent(e, "click", { node: r });
  }, onClickExpand: (e) => {
    this.onLfEvent(e, "click", { expansion: true, node: r });
  }, onPointerDown: (e) => {
    this.onLfEvent(e, "pointerdown", { node: r });
  } }, expanded: n2, manager: D(this, g, "f"), node: r, selected: d };
  s || (o2.push(N(v, { ...c })), n2 && ((_a = r.children) == null ? void 0 : _a.map((e) => D(this, u, "m", t).call(this, o2, e, i + 1))));
}, M.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}:host{display:block;font-family:var(--lf-tree-font-family, var(--lf-font-family-primary));font-size:var(--lf-tree-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-tree-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}:host([lf-accordion-layout]) .node[data-depth="0"]{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);font-size:1em;height:var(--lf-tree-accordion-node-height, 4em)}:host([lf-accordion-layout]) .node[data-depth="0"] .node__value{font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;font-size:1em}:host([lf-selectable]) .node:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.075);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.175);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}:host([lf-selectable]) .node--selected:hover{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 0.225);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.tree{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-tree-color-bg, var(--lf-color-bg)), 0.275);color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);padding:var(--lf-tree-padding, 0)}.tree__filter{border:0;border-style:solid;border-radius:var(--lf-tree-border-radius, var(--lf-ui-border-radius));border-bottom-left-radius:0;border-bottom-right-radius:0;background-color:rgba(var(--lf-tree-color-surface, var(--lf-color-surface)), 0.875);color:rgb(var(--lf-tree-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px);position:sticky;top:0;z-index:1}.node{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);box-sizing:border-box;height:var(--lf-tree-node-height, 2em);padding:var(--lftree-node-padding, 0 1em);position:relative}.node__content{width:100%;height:100%;align-items:center;display:flex}.node__dropdown,.node__expand,.node__icon{cursor:pointer;margin:0}.node__dropdown,.node__expand{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);overflow:hidden}.node__dropdown:hover,.node__expand:hover{opacity:0.75}.node__dropdown{-webkit-mask:var(--lf-icon-dropdown);mask:var(--lf-icon-dropdown);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__dropdown--expanded{transform:rotate(180deg)}.node__dropdown--expanded:hover{opacity:0.75}.node__dropdown--hidden{visibility:hidden}.node__expand{-webkit-mask:var(--lf-icon-collapsed);mask:var(--lf-icon-collapsed);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--expanded{-webkit-mask:var(--lf-icon-expanded);mask:var(--lf-icon-expanded);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__expand--hidden{visibility:hidden}.node__icon{background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden}.node__padding{height:100%;width:calc(1.75em * var(--lf_tree_padding_multiplier))}.node__value{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;margin:0 0 0 0.5em;width:100%}.no-matches{color:rgb(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)));align-items:center;box-sizing:border-box;display:flex;justify-content:center;margin:auto;padding:1em;width:100%}.no-matches__icon{-webkit-mask:var(--lf-icon-warning);mask:var(--lf-icon-warning);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-tree-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin-right:0.375em}.no-matches__text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:400;line-height:1.25em;letter-spacing:0.2em}.no-matches__filter{color:var(--lf-primary-color)}.empty-data{width:100%;height:100%;font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:1em;align-items:center;display:flex;justify-content:center;margin:1em 0}';
export {
  M as lf_tree
};
