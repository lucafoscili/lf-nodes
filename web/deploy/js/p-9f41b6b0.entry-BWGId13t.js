import { n, H, aS as LF_ACCORDION_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, aT as LF_ACCORDION_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, N, aU as LF_ACCORDION_PROPS, f as de, U, F } from "./index-B7yCDN23.js";
import { o } from "./p-BJbvgtBt-BB0MQEt4.js";
import { f } from "./p-B2nA4wTt-DSm22Q3m.js";
var v, m, u, g, y, w, k, x, z, _, E, W, C, M, j, T = function(r, o2, i, a) {
  if ("a" === i && !a) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof o2 ? r !== o2 || !a : !o2.has(r)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === i ? a : "a" === i ? a.call(r) : a ? a.value : o2.get(r);
}, D = function(r, o2, i, a, e) {
  if ("function" == typeof o2 ? r !== o2 || true : !o2.has(r)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return o2.set(r, i), i;
};
const L = class {
  constructor(a) {
    n(this, a), this.lfEvent = H(this, "lf-accordion-event"), v.add(this), this.expandedNodes = /* @__PURE__ */ new Set(), this.selectedNodes = /* @__PURE__ */ new Set(), this.lfDataset = null, this.lfRipple = true, this.lfUiSize = "medium", this.lfUiState = "primary", this.lfStyle = "", m.set(this, void 0), u.set(this, LF_ACCORDION_BLOCKS), g.set(this, CY_ATTRIBUTES), y.set(this, LF_ATTRIBUTES), w.set(this, LF_ACCORDION_PARTS), k.set(this, LF_STYLE_ID), x.set(this, LF_WRAPPER_ID), z.set(this, {}), j.set(this, (r) => {
      const { cells: o2 } = r, a2 = o2 && Object.keys(o2)[0], e = o2 == null ? void 0 : o2[a2];
      return N(f, { cell: e, index: 0, shape: e.shape, eventDispatcher: async (r2) => this.onLfEvent(r2, "lf-event"), framework: T(this, m, "f") });
    });
  }
  onLfEvent(r, o2, i) {
    const { effects: a } = T(this, m, "f"), { lfRipple: e, rootElement: t } = this;
    "pointerdown" === o2 && e && a.ripple(r, T(this, z, "f")[i.id]), this.lfEvent.emit({ comp: this, eventType: o2, id: t.id, originalEvent: r });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const r = LF_ACCORDION_PROPS.map((r2) => [r2, this[r2]]);
    return Object.fromEntries(r);
  }
  async getSelectedNodes() {
    return this.selectedNodes;
  }
  async refresh() {
    de(this);
  }
  async toggleNode(r, o2) {
    const i = this.lfDataset.nodes.find((o3) => o3.id === r);
    i && (T(this, v, "m", E).call(this, i) ? T(this, v, "m", _).call(this, i) ? this.expandedNodes.delete(i) : this.expandedNodes.add(i) : T(this, v, "m", W).call(this, i) ? this.selectedNodes.delete(i) : this.selectedNodes.add(i), T(this, v, "m", E).call(this, i) || this.onLfEvent(o2 || new CustomEvent("click"), "click"), this.refresh());
  }
  async unmount(r = 0) {
    setTimeout(() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, r);
  }
  connectedCallback() {
    T(this, m, "f") && T(this, m, "f").theme.register(this);
  }
  async componentWillLoad() {
    D(this, m, await o(this));
  }
  componentDidLoad() {
    const { info: r } = T(this, m, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), r.update(this, "did-load");
  }
  componentWillRender() {
    const { info: r } = T(this, m, "f").debug;
    r.update(this, "will-render");
  }
  componentDidRender() {
    const { debug: r } = T(this, m, "f");
    r.info.update(this, "did-render");
  }
  render() {
    const { bemClass: r, setLfStyle: o2 } = T(this, m, "f").theme, { lfStyle: a } = this;
    D(this, z, {});
    const { accordion: t } = T(this, u, "f");
    return N(U, { key: "cf05618985fae22815dc9feb7bcb3bcfeb67daf5" }, a && N("style", { key: "2248a586b39ae7758361616bcf82494baf6f43b1", id: T(this, k, "f") }, o2(this)), N("div", { key: "02dacfdfddd9e16e776e0ab666b273e04390c263", id: T(this, x, "f") }, N("div", { key: "b98095b71dcadbfab5de9cdedba3bbd06470d924", class: r(t._), part: T(this, w, "f").accordion }, T(this, v, "m", M).call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = T(this, m, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return F(this);
  }
};
m = /* @__PURE__ */ new WeakMap(), u = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), j = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakSet(), _ = function(r) {
  return this.expandedNodes.has(r);
}, E = function(r) {
  return r.cells && Object.keys(r.cells).length > 0;
}, W = function(r) {
  return this.selectedNodes.has(r);
}, C = function(r) {
  const { assets: o2, theme: a } = T(this, m, "f"), { style: e } = o2.get(`./assets/svg/${r}.svg`), { node: t } = T(this, u, "f");
  return N("div", { class: a.bemClass(t._, t.icon), "data-cy": T(this, g, "f").maskedSvg, part: T(this, w, "f").icon, style: e });
}, M = function() {
  const { bemClass: r } = T(this, m, "f").theme, { lfDataset: o2 } = this, a = [];
  for (let e = 0; e < o2.nodes.length; e++) {
    const t = o2.nodes[e], n2 = T(this, v, "m", _).call(this, t), l = T(this, v, "m", E).call(this, t), s = T(this, v, "m", W).call(this, t);
    a.push(N("div", { class: r(T(this, u, "f").node._), "data-cy": T(this, g, "f").node, "data-lf": T(this, y, "f")[this.lfUiState] }, N("div", { class: r(T(this, u, "f").node._, T(this, u, "f").node.header, { expanded: l && n2, selected: !l && s }), "data-cy": !l && T(this, g, "f").button, onClick: (r2) => this.toggleNode(t.id, r2), onPointerDown: (r2) => {
      this.onLfEvent(r2, "pointerdown", t);
    }, part: T(this, w, "f").header, tabindex: "1", title: t.description }, N("div", { "data-cy": T(this, g, "f").rippleSurface, "data-lf": T(this, y, "f").rippleSurface, part: T(this, w, "f").rippleSurface, ref: (r2) => {
      r2 && this.lfRipple && (T(this, z, "f")[t.id] = r2);
    } }), t.icon ? T(this, v, "m", C).call(this, t.icon) : null, N("span", { class: r(T(this, u, "f").node._, T(this, u, "f").node.text), part: T(this, w, "f").text }, t.value), l && N("div", { class: r(T(this, u, "f").node._, T(this, u, "f").node.expand, { expanded: n2 }), "data-cy": T(this, g, "f").dropdownButton, "data-lf": T(this, y, "f").icon, part: T(this, w, "f").icon })), n2 && N("div", { class: r(T(this, u, "f").node._, T(this, u, "f").node.content, { selected: s }), "data-lf": T(this, y, "f").fadeIn, part: T(this, w, "f").content }, T(this, j, "f").call(this, t))));
  }
  return a;
}, L.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}[data-lf=danger]{--lf-accordion-color-primary:var(\n    --lf-accordion-color-danger,\n    var(--lf-color-danger)\n  );--lf-accordion-color-on-primary:var(\n    --lf-accordion-color-danger,\n    var(--lf-color-on-danger)\n  )}[data-lf=disabled]{opacity:var(--lf-accordion-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-accordion-color-primary:var(\n    --lf-accordion-color-info,\n    var(--lf-color-info)\n  );--lf-accordion-color-on-primary:var(\n    --lf-accordion-color-info,\n    var(--lf-color-on-info)\n  )}[data-lf=secondary]{--lf-accordion-color-primary:var(\n    --lf-accordion-color-secondary,\n    var(--lf-color-secondary)\n  );--lf-accordion-color-on-primary:var(\n    --lf-accordion-color-secondary,\n    var(--lf-color-on-secondary)\n  )}[data-lf=success]{--lf-accordion-color-primary:var(\n    --lf-accordion-color-success,\n    var(--lf-color-success)\n  );--lf-accordion-color-on-primary:var(\n    --lf-accordion-color-success,\n    var(--lf-color-on-success)\n  )}[data-lf=warning]{--lf-accordion-color-primary:var(\n    --lf-accordion-color-warning,\n    var(--lf-color-warning)\n  );--lf-accordion-color-on-primary:var(\n    --lf-accordion-color-warning,\n    var(--lf-color-on-warning)\n  )}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-accordion-font-family, var(--lf-font-family-primary));font-size:var(--lf-accordion-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-accordion-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-accordion-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-accordion-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-accordion-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-accordion-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-accordion-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-accordion-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}.accordion{border:0;border-style:solid;border-color:rgba(var(--lf-accordion-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-accordion-border-radius, var(--lf-ui-border-radius));border-left:0;border-right:0;width:100%;height:100%;box-sizing:border-box;display:flex;flex-direction:var(--lf-accordion-flex-direction, column);flex-wrap:var(--lf-accordion-flex-wrap, nowrap);width:100%}.node{border:0;border-style:solid;border-color:rgba(var(--lf-accordion-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-accordion-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-accordion-color-bg, var(--lf-color-bg)), 0.375);color:rgb(var(--lf-accordion-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:0;border-top:0;box-sizing:border-box;width:100%}.node:not(:first-of-type){border:0;border-style:solid;border-color:rgba(var(--lf-accordion-border-color, var(--lf-color-border)), 1);border-width:1px;margin-bottom:0;margin-left:0;margin-right:0}.node__content,.node__content ::slotted(*){border:0;border-style:solid;border-radius:var(--lf-accordion-border-radius, var(--lf-ui-border-radius));border-top-left-radius:0;border-top-right-radius:0}.node__header{border:0;border-style:solid;border-radius:var(--lf-accordion-border-radius, var(--lf-ui-border-radius));color:rgb(var(--lf-accordion-color-on-bg, var(--lf-color-on-bg)));transition:all 150ms cubic-bezier(0.42, 0, 0.58, 1);align-items:center;border:none;box-sizing:border-box;cursor:var(--lf-accordion-cursor, pointer);display:flex;line-height:var(--lf-accordion-line-height, 1.75em);outline:none;padding:var(--lf-accordion-padding, 1em);position:relative;text-align:var(--lf-accordion-text-align, left);width:100%}.node__header:hover{background-color:rgba(var(--lf-accordion-color-primary, var(--lf-color-primary)), 0.175)}.node__header--expanded{border-bottom-left-radius:0;border-bottom-right-radius:0}.node__header--selected{background-color:rgba(var(--lf-accordion-color-primary, var(--lf-color-primary)), 0.375)}.node__header--selected:hover{background-color:rgba(var(--lf-accordion-color-primary, var(--lf-color-primary)), 0.475)}.node__text{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:1.25em;font-weight:500;line-height:1.4em;letter-spacing:0em;margin:var(--lf-accordion-text-margin, 0 0.5em 0 0)}.node__text--highlighted{background-color:rgba(var(--lf-accordion-color-primary, var(--lf-color-primary)), 1);color:rgb(var(--lf-accordion-color-on-primary, var(--lf-color-on-primary)))}.node__expand,.node__icon{margin:0}.node__icon{background-color:rgba(var(--lf-accordion-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin:var(--lf-accordion-icon-margin, 0 0.5em 0 0)}.node__expand{-webkit-mask:var(--lf-icon-dropdown);mask:var(--lf-icon-dropdown);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-accordion-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;transition:all 150ms cubic-bezier(0.42, 0, 0.58, 1);margin:var(--lf-accordion-expand-margin, 0 0 0 auto)}.node__expand--expanded{transform:rotate(-180deg)}.node__expand--placeholder{visibility:hidden}";
export {
  L as lf_accordion
};
