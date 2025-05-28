import { n, H, L as LF_PLACEHOLDER_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, b as LF_PLACEHOLDER_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, e as LF_PLACEHOLDER_PROPS, f as de, N, U, F } from "./index-Be7z5Nuo.js";
import { o } from "./p-BJbvgtBt-BdWeNtWf.js";
var v, m, b, u, w, y, g, z, k, x, W, E, C = function(e, t, i, s) {
  if ("a" === i && !s) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !s : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === i ? s : "a" === i ? s.call(e) : s ? s.value : t.get(e);
}, M = function(e, t, i, s, a) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, i), i;
};
const T = class {
  constructor(i) {
    n(this, i), this.lfEvent = H(this, "lf-placeholder-event"), v.add(this), this.isInViewport = false, this.lfIcon = "template", this.lfProps = {}, this.lfStyle = "", this.lfThreshold = 0.25, this.lfTrigger = "both", this.lfValue = "LfCard", m.set(this, void 0), b.set(this, LF_PLACEHOLDER_BLOCKS), u.set(this, CY_ATTRIBUTES), w.set(this, LF_ATTRIBUTES), y.set(this, LF_PLACEHOLDER_PARTS), g.set(this, LF_STYLE_ID), z.set(this, LF_WRAPPER_ID), k.set(this, null), x.set(this, null), W.set(this, false);
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, id: this.rootElement.id, originalEvent: e, eventType: t });
  }
  async getComponent() {
    return C(this, x, "f");
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_PLACEHOLDER_PROPS.map((e2) => [e2, this[e2]]);
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
    C(this, m, "f") && (C(this, m, "f").theme.register(this), C(this, v, "m", E).call(this));
  }
  async componentWillLoad() {
    M(this, m, await o(this));
  }
  componentDidLoad() {
    const { info: e } = C(this, m, "f").debug;
    C(this, v, "m", E).call(this), C(this, k, "f").observe(this.rootElement), this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = C(this, m, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = C(this, m, "f").debug;
    C(this, x, "f") && !C(this, W, "f") && (M(this, W, true), this.onLfEvent(new CustomEvent("load"), "load")), e.update(this, "did-render");
  }
  render() {
    const { assets: e, sanitizeProps: t, theme: i } = C(this, m, "f"), { bemClass: o2, setLfStyle: l } = i, { placeholder: n2 } = C(this, b, "f"), { isInViewport: f, lfValue: h, lfProps: c, lfTrigger: d, lfIcon: p, lfStyle: v2 } = this;
    let k2;
    if (Boolean("viewport" === d && f || "props" === d && c || "both" === d && c && f)) {
      const e2 = h.toLowerCase().replace("lf", ""), i2 = { [`onLf-${e2}-event`]: (e3) => {
        this.onLfEvent(e3, "lf-event");
      } };
      k2 = N("lf-" + e2, { key: "700c750eb756e656a765c934e42a3ff7d35c835b", ...t(c, h), ...i2, "data-lf": LF_ATTRIBUTES.fadeIn, ref: (e3) => M(this, x, e3) });
    } else if (p) {
      const { style: t2 } = e.get(`./assets/svg/${p}.svg`);
      k2 = N("div", { key: "7543c4b6740b3340dc2453651c7290117946ec53", class: o2(n2._, n2.icon), "data-cy": C(this, u, "f").maskedSvg, "data-lf": C(this, w, "f").fadeIn, part: C(this, y, "f").icon, style: t2 });
    }
    return N(U, { key: "3d35b3f8ad468158880f4eea0ddff3c3d991d952" }, v2 && N("style", { key: "8316bc849fcb1be22017184f6deaa81605b35b7b", id: C(this, g, "f") }, l(this)), N("div", { key: "2553ca5c4547f006d02e52f052ea7966bff2bbe6", id: C(this, z, "f") }, N("div", { key: "89e0e7cb0ccc22f9bba82d6d2bd3f6a64fe8f24a", class: o2(n2._), part: C(this, y, "f").placeholder }, k2)));
  }
  disconnectedCallback() {
    var _a, _b;
    (_a = C(this, m, "f")) == null ? void 0 : _a.theme.unregister(this), (_b = C(this, k, "f")) == null ? void 0 : _b.unobserve(this.rootElement);
  }
  get rootElement() {
    return F(this);
  }
};
m = /* @__PURE__ */ new WeakMap(), b = /* @__PURE__ */ new WeakMap(), u = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakSet(), E = function() {
  const { debug: e } = C(this, m, "f");
  M(this, k, new IntersectionObserver((t) => {
    t.forEach((t2) => {
      const i = this.rootElement.hasAttribute("lf-hydrated");
      t2.isIntersecting && i && (e.logs.new(this, "lf-placeholder entering the viewport, rendering " + this.lfValue + "."), this.isInViewport = true, C(this, k, "f").unobserve(this.rootElement));
    });
  }, { threshold: this.lfThreshold }));
}, T.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-placeholder-font-family, var(--lf-font-family-primary));font-size:var(--lf-placeholder-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%;position:relative}.placeholder{align-items:var(--lf-placeholder-ver-alignment, center);display:flex;height:var(--lf-placeholder-height, 100%);justify-content:var(--lf-placeholder-hor-alignment, center);width:var(--lf-placeholder-width, 100%)}.placeholder__icon{background-color:rgba(var(--lf-placeholder-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;width:100%;height:100%;animation:shine ease 2s infinite}@keyframes shine{0%{opacity:0.4}50%{opacity:0.8}100%{opacity:0.4}}";
export {
  T as lf_placeholder
};
