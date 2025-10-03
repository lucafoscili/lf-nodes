import { n, V, b9 as LF_TABBAR_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, ba as LF_TABBAR_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, D as D$1, bb as LF_TABBAR_PROPS, p as pt, W as W$1, z as z$1 } from "./index-CcDeec9x.js";
import { a } from "./p-Dl9cVpAY-Bg0qOWea.js";
const p = (t, r) => {
  if (t) {
    const a2 = t.scrollLeft;
    t.scrollTo({ left: "left" === r ? a2 - 200 : a2 + 200, behavior: "smooth" });
  }
};
var u, v, m, g, y, w, z, k, x, _, W, M = function(t, r, a2, i) {
  if ("function" == typeof r ? t !== r || !i : !r.has(t)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === a2 ? i : "a" === a2 ? i.call(t) : i ? i.value : r.get(t);
}, C = function(t, r, a2, i, o) {
  if ("function" == typeof r ? t !== r || true : !r.has(t)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return r.set(t, a2), a2;
};
const E = class {
  constructor(i) {
    n(this, i), this.lfEvent = V(this, "lf-tabbar-event"), this.value = null, this.lfAriaLabel = "", this.lfDataset = null, this.lfNavigation = false, this.lfRipple = true, this.lfStyle = "", this.lfUiSize = "medium", this.lfUiState = "primary", this.lfValue = null, u.set(this, void 0), v.set(this, LF_TABBAR_BLOCKS), m.set(this, CY_ATTRIBUTES), g.set(this, LF_ATTRIBUTES), y.set(this, LF_TABBAR_PARTS), w.set(this, LF_STYLE_ID), z.set(this, LF_WRAPPER_ID), k.set(this, void 0), x.set(this, void 0), _.set(this, ((t) => {
      const { get: r } = M(this, u, "f").assets, { bemClass: i2 } = M(this, u, "f").theme, { tab: o } = M(this, v, "f"), { style: e } = r(`./assets/svg/${t.icon}.svg`);
      return D$1("div", { class: i2(o._, o.icon), "data-cy": M(this, m, "f").maskedSvg, style: e });
    })), W.set(this, ((t, r) => {
      const { theme: i2 } = M(this, u, "f"), { bemClass: o } = i2, { tab: e } = M(this, v, "f"), { lfRipple: l, value: n2 } = this, s = t === (n2 == null ? void 0 : n2.node);
      return D$1("button", { "aria-selected": s, "aria-label": (this.lfAriaLabel && t.value ? `${this.lfAriaLabel} ${t.value}` : t.value || this.lfAriaLabel || t.icon || this.rootElement.id || "tab").toString().trim(), class: o(e._, null, { active: s }), "data-cy": M(this, m, "f").button, "data-lf": M(this, g, "f")[this.lfUiState], onClick: (a2) => {
        this.onLfEvent(a2, "click", r, t);
      }, onPointerDown: (a2) => {
        this.onLfEvent(a2, "pointerdown", r, t);
      }, part: M(this, y, "f").tab, role: "tab", tabIndex: r, title: (t == null ? void 0 : t.description) || "" }, D$1("div", { "data-cy": M(this, m, "f").rippleSurface, "data-lf": M(this, g, "f").rippleSurface, ref: (t2) => {
        t2 && l && M(this, k, "f").push(t2);
      } }), D$1("span", { class: o(e._, e.content), "data-cy": M(this, m, "f").node }, t.icon && M(this, _, "f").call(this, t), t.value && D$1("span", { class: o(e._, e.label) }, t.value)), D$1("span", { class: o(e._, e.indicator, { active: s }) }, D$1("span", { class: o(e._, e.indicatorContent, { active: true }) })));
    }));
  }
  onLfEvent(t, r, a2 = 0, i) {
    const { effects: o } = M(this, u, "f");
    switch (r) {
      case "click":
        this.value = { index: a2, node: i };
        break;
      case "pointerdown":
        this.lfRipple && o.ripple(t, M(this, k, "f")[a2]);
    }
    this.lfEvent.emit({ comp: this, eventType: r, id: this.rootElement.id, originalEvent: t, node: i });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const t = LF_TABBAR_PROPS.map(((t2) => [t2, this[t2]]));
    return Object.fromEntries(t);
  }
  async getValue() {
    return this.value;
  }
  async refresh() {
    pt(this);
  }
  async setValue(t) {
    let r, a2;
    return "number" == typeof t ? (r = t, a2 = this.lfDataset.nodes[r]) : "string" == typeof t && (r = this.lfDataset.nodes.findIndex(((r2) => r2.id === t)), a2 = this.lfDataset.nodes[r]), this.value = { index: r, node: a2 }, this.value;
  }
  async unmount(t = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), t);
  }
  connectedCallback() {
    M(this, u, "f") && M(this, u, "f").theme.register(this);
  }
  async componentWillLoad() {
    C(this, u, await a(this));
    const { debug: t } = M(this, u, "f"), { lfDataset: r, lfValue: a$1 } = this;
    try {
      if (null !== a$1 && ("number" == typeof a$1 && (this.value = { index: a$1, node: r.nodes[a$1] }), "string" == typeof a$1)) {
        const t2 = r.nodes.find(((t3) => t3.id === a$1));
        this.value = { index: r.nodes.indexOf(t2), node: t2 };
      }
    } catch (r2) {
      t.logs.new(this, "Something went wrong while setting the initial selected value.", "warning");
    }
  }
  componentDidLoad() {
    const { debug: t, drag: r } = M(this, u, "f");
    M(this, x, "f") && r.register.dragToScroll(M(this, x, "f")), this.onLfEvent(new CustomEvent("ready"), "ready"), t.info.update(this, "did-load");
  }
  componentWillRender() {
    const { debug: t } = M(this, u, "f");
    t.info.update(this, "will-render");
  }
  componentDidRender() {
    const { info: t } = M(this, u, "f").debug;
    t.update(this, "did-render");
  }
  render() {
    const { data: t, theme: r } = M(this, u, "f"), { bemClass: i, get: e, setLfStyle: l } = r, { "--lf-icon-next": n2, "--lf-icon-previous": s } = e.current().variables, { tabbar: f } = M(this, v, "f"), { lfDataset: c, lfStyle: b } = this;
    if (!t.node.exists(c)) return;
    C(this, k, []);
    const d = c.nodes;
    return D$1(W$1, null, b && D$1("style", { id: M(this, w, "f") }, l(this)), D$1("div", { id: M(this, z, "f") }, D$1("div", { class: i(f._), part: M(this, y, "f").tabbbar, role: "tablist" }, this.lfNavigation && D$1("lf-button", { lfIcon: s, lfStretchY: true, lfStyling: "flat", lfUiSize: this.lfUiSize, "onLf-button-event": () => p(M(this, x, "f"), "left") }), D$1("div", { class: i(f._, f.scroll), ref: (t2) => {
      t2 && C(this, x, t2);
    } }, d.map(((t2, r2) => M(this, W, "f").call(this, t2, r2)))), this.lfNavigation && D$1("lf-button", { lfIcon: n2, lfStretchY: true, lfStyling: "flat", lfUiSize: this.lfUiSize, "onLf-button-event": () => p(M(this, x, "f"), "right") }))));
  }
  disconnectedCallback() {
    var _a, _b, _c;
    ((_a = M(this, u, "f")) == null ? void 0 : _a.drag.getActiveSession(M(this, x, "f"))) && ((_b = M(this, u, "f")) == null ? void 0 : _b.drag.unregister.dragToScroll(M(this, x, "f"))), (_c = M(this, u, "f")) == null ? void 0 : _c.theme.unregister(this);
  }
  get rootElement() {
    return z$1(this);
  }
};
u = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakMap(), m = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), E.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}[data-lf=danger]{--lf-tabbar-color-primary:var(\n    --lf-tabbar-color-danger,\n    var(--lf-color-danger)\n  );--lf-tabbar-color-on-primary:var(\n    --lf-tabbar-color-danger,\n    var(--lf-color-on-danger)\n  )}[data-lf=disabled]{opacity:var(--lf-tabbar-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-tabbar-color-primary:var(\n    --lf-tabbar-color-info,\n    var(--lf-color-info)\n  );--lf-tabbar-color-on-primary:var(\n    --lf-tabbar-color-info,\n    var(--lf-color-on-info)\n  )}[data-lf=secondary]{--lf-tabbar-color-primary:var(\n    --lf-tabbar-color-secondary,\n    var(--lf-color-secondary)\n  );--lf-tabbar-color-on-primary:var(\n    --lf-tabbar-color-secondary,\n    var(--lf-color-on-secondary)\n  )}[data-lf=success]{--lf-tabbar-color-primary:var(\n    --lf-tabbar-color-success,\n    var(--lf-color-success)\n  );--lf-tabbar-color-on-primary:var(\n    --lf-tabbar-color-success,\n    var(--lf-color-on-success)\n  )}[data-lf=warning]{--lf-tabbar-color-primary:var(\n    --lf-tabbar-color-warning,\n    var(--lf-color-warning)\n  );--lf-tabbar-color-on-primary:var(\n    --lf-tabbar-color-warning,\n    var(--lf-color-on-warning)\n  )}:host{display:block;font-family:var(--lf-tabbar-font-family, var(--lf-font-family-primary));font-size:var(--lf-tabbar-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-tabbar-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-tabbar-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-tabbar-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-tabbar-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-tabbar-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-tabbar-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-tabbar-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%}.tabbar{display:flex;height:var(--lf-tabbar-height, 2.25em);width:100%}.tabbar__scroll{display:flex;overflow:hidden;width:100%}.tab{font-family:var(--lf-tabbar-font-family, var(--lf-font-family-primary));background-color:rgba(var(--lf-tabbar-color-bg, var(--lf-color-bg)), 0.375);color:rgb(var(--lf-tabbar-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);appearance:none;border:none;box-sizing:border-box;cursor:pointer;display:flex;flex:1 0 auto;height:100%;justify-content:center;margin:0;min-width:var(--lf-tabbar-min-width, 5em);outline:none;padding:var(--lf-tabbar-tab-padding, 0 1.25em);position:relative;text-align:center}.tab:first-child{border:0;border-style:solid;border-radius:var(--lf-tabbar-border-radius, var(--lf-ui-border-radius));border-bottom-left-radius:0;border-bottom-right-radius:0;border-top-right-radius:0}.tab:last-child{border:0;border-style:solid;border-radius:var(--lf-tabbar-border-radius, var(--lf-ui-border-radius));border-bottom-left-radius:0;border-bottom-right-radius:0;border-top-left-radius:0}.tab:hover{background-color:rgba(var(--lf-tabbar-color-primary, var(--lf-color-primary)), 0.125);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.tab--active{background-color:rgba(var(--lf-tabbar-color-primary, var(--lf-color-primary)), 0.225);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.tab--active:hover{background-color:rgba(var(--lf-tabbar-color-primary, var(--lf-color-primary)), 0.325);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.tab--active .tab__icon{background-color:rgba(var(--lf-tabbar-color-primary, var(--lf-color-primary)), 1)}.tab--active .tab__label{color:rgb(var(--lf-tabbar-color-primary, var(--lf-color-primary)));font-weight:600;opacity:1}.tab__icon{background-color:rgba(var(--lf-tabbar-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1)}.tab__content{align-items:center;display:flex;height:inherit;justify-content:center;pointer-events:none;position:relative}.tab__label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;opacity:0.75}.tab__icon+.tab__label{padding-left:0.5em;padding-right:0}.tab__indicator{width:100%;height:100%;transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);display:flex;justify-content:center;left:0;pointer-events:none;position:absolute;top:0}.tab__indicator--active .tab__indicator-content{opacity:1}.tab__indicator-content{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);opacity:0;transform-origin:left center}.tab__indicator-content--active{align-self:flex-end;border-color:rgb(var(--lf-tabbar-color-indicator, var(--lf-tabbar-color-primary)));border-top-style:solid;border-top-width:2px;box-sizing:border-box;width:100%}";
export {
  E as lf_tabbar
};
