import { n, I, aX as LF_PLACEHOLDER_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, aY as LF_PLACEHOLDER_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, aZ as LF_PLACEHOLDER_PROPS, m as mt, W as W$1, f as L, G } from "./index-D_nXp8pz.js";
import { o } from "./p-DklcdYZv-DT7BY8Do.js";
var v, m, b, u, w, y, z, g, k, x, W, C, E = function(e, t, i, s) {
  if ("a" === i && !s) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? e !== t || !s : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === i ? s : "a" === i ? s.call(e) : s ? s.value : t.get(e);
}, M = function(e, t, i, s, a) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, i), i;
};
const T = class {
  constructor(i) {
    n(this, i), this.lfEvent = I(this, "lf-placeholder-event"), v.add(this), this.isInViewport = false, this.lfIcon = "template", this.lfProps = {}, this.lfStyle = "", this.lfThreshold = 0.25, this.lfTrigger = "both", this.lfValue = "LfCard", m.set(this, void 0), b.set(this, LF_PLACEHOLDER_BLOCKS), u.set(this, CY_ATTRIBUTES), w.set(this, LF_ATTRIBUTES), y.set(this, LF_PLACEHOLDER_PARTS), z.set(this, LF_STYLE_ID), g.set(this, LF_WRAPPER_ID), k.set(this, null), x.set(this, null), W.set(this, false);
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, id: this.rootElement.id, originalEvent: e, eventType: t });
  }
  async getComponent() {
    return E(this, x, "f");
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_PLACEHOLDER_PROPS.map(((e2) => [e2, this[e2]]));
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
    E(this, m, "f") && (E(this, m, "f").theme.register(this), E(this, v, "m", C).call(this));
  }
  async componentWillLoad() {
    M(this, m, await o(this));
  }
  componentDidLoad() {
    const { info: e } = E(this, m, "f").debug;
    E(this, v, "m", C).call(this), E(this, k, "f").observe(this.rootElement), this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = E(this, m, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = E(this, m, "f").debug;
    E(this, x, "f") && !E(this, W, "f") && (M(this, W, true), this.onLfEvent(new CustomEvent("load"), "load")), e.update(this, "did-render");
  }
  render() {
    const { assets: e, sanitizeProps: t, theme: i } = E(this, m, "f"), { bemClass: o2, setLfStyle: l } = i, { placeholder: r } = E(this, b, "f"), { isInViewport: f, lfValue: h, lfProps: c, lfTrigger: d, lfIcon: p, lfStyle: v2 } = this;
    let k2;
    if (Boolean("viewport" === d && f || "props" === d && c || "both" === d && c && f)) {
      const e2 = h.toLowerCase().replace("lf", ""), i2 = { [`onLf-${e2}-event`]: (e3) => {
        this.onLfEvent(e3, "lf-event");
      } };
      k2 = W$1("lf-" + e2, { key: "70059493fdccb2a95269d9f9ac36f9e45e2bee96", ...t(c, h), ...i2, "data-lf": LF_ATTRIBUTES.fadeIn, ref: (e3) => M(this, x, e3) });
    } else if (p) {
      const { style: t2 } = e.get(`./assets/svg/${p}.svg`);
      k2 = W$1("div", { key: "8c229eb0faf998bb18e493136ef1c926cf8c0367", class: o2(r._, r.icon), "data-cy": E(this, u, "f").maskedSvg, "data-lf": E(this, w, "f").fadeIn, part: E(this, y, "f").icon, style: t2 });
    }
    return W$1(L, { key: "181cee7151ead42ebbb4c9bdea49020254e8ee77" }, v2 && W$1("style", { key: "67b201b596c66625d0c033b5715199c6181688a8", id: E(this, z, "f") }, l(this)), W$1("div", { key: "8db285c023bd3380a282c6c00b72b62d5a34ddaf", id: E(this, g, "f") }, W$1("div", { key: "160905b3bcda5345ff27624d04f79b2276de16db", class: o2(r._), part: E(this, y, "f").placeholder }, k2)));
  }
  disconnectedCallback() {
    var _a, _b;
    (_a = E(this, m, "f")) == null ? void 0 : _a.theme.unregister(this), (_b = E(this, k, "f")) == null ? void 0 : _b.unobserve(this.rootElement);
  }
  get rootElement() {
    return G(this);
  }
};
m = /* @__PURE__ */ new WeakMap(), b = /* @__PURE__ */ new WeakMap(), u = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakSet(), C = function() {
  const { debug: e } = E(this, m, "f");
  M(this, k, new IntersectionObserver(((t) => {
    t.forEach(((t2) => {
      const i = this.rootElement.hasAttribute("lf-hydrated");
      t2.isIntersecting && i && (e.logs.new(this, "lf-placeholder entering the viewport, rendering " + this.lfValue + "."), this.isInViewport = true, E(this, k, "f").unobserve(this.rootElement));
    }));
  }), { threshold: this.lfThreshold }));
}, T.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-placeholder-font-family, var(--lf-font-family-primary));font-size:var(--lf-placeholder-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-placeholder-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%;position:relative}.placeholder{align-items:var(--lf-placeholder-ver-alignment, center);display:flex;height:var(--lf-placeholder-height, 100%);justify-content:var(--lf-placeholder-hor-alignment, center);width:var(--lf-placeholder-width, 100%)}.placeholder__icon{background-color:rgba(var(--lf-placeholder-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;width:100%;height:100%;animation:shine ease 2s infinite}@keyframes shine{0%{opacity:0.4}50%{opacity:0.8}100%{opacity:0.4}}";
export {
  T as lf_placeholder
};
