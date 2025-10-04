import { n, V, w as LF_SPLASH_BLOCKS, x as LF_SPLASH_PARTS, d as LF_STYLE_ID, f as LF_WRAPPER_ID, y as LF_SPLASH_PROPS, p as pt, D as D$1, W as W$1, z } from "./index-BFq_6STv.js";
import { a } from "./p-Dl9cVpAY-9zAXgbCa.js";
var d, p, v, m, b, u = function(t, s, e, a2) {
  if ("function" == typeof s ? t !== s || true : !s.has(t)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return s.get(t);
};
const g = class {
  constructor(e) {
    n(this, e), this.lfEvent = V(this, "lf-splash-event"), this.state = "initializing", this.lfLabel = "Loading...", this.lfStyle = "", d.set(this, void 0), p.set(this, LF_SPLASH_BLOCKS), v.set(this, LF_SPLASH_PARTS), m.set(this, LF_STYLE_ID), b.set(this, LF_WRAPPER_ID);
  }
  onLfEvent(t, s) {
    this.lfEvent.emit({ comp: this, eventType: s, id: this.rootElement.id, originalEvent: t });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const t = LF_SPLASH_PROPS.map(((t2) => [t2, this[t2]]));
    return Object.fromEntries(t);
  }
  async refresh() {
    pt(this);
  }
  async unmount(t = 575) {
    setTimeout((() => {
      this.state = "unmounting", setTimeout((() => {
        this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
      }), 300);
    }), t);
  }
  connectedCallback() {
    u(this, d) && u(this, d).theme.register(this);
  }
  async componentWillLoad() {
    !(function(t, s, e, a2, i) {
      if ("function" == typeof s ? t !== s || true : !s.has(t)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
      s.set(t, e);
    })(this, d, await a(this));
  }
  componentDidLoad() {
    const { info: t } = u(this, d).debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), t.update(this, "did-load");
  }
  componentWillRender() {
    const { info: t } = u(this, d).debug;
    t.update(this, "will-render");
  }
  componentDidRender() {
    const { info: t } = u(this, d).debug;
    t.update(this, "did-render");
  }
  render() {
    const { bemClass: t, setLfStyle: s } = u(this, d).theme, { lfLabel: e, lfStyle: l, state: o } = this, r = "unmounting" === o, { splash: f } = u(this, p);
    return D$1(W$1, { key: "1f05bd939b021ddfa85a39c4e12f7985f1707030" }, l && D$1("style", { key: "027913f95b6817f5926188ae16ac7774936e7b6b", id: u(this, m) }, s(this)), D$1("div", { key: "0f16cdd9bb4397aff286bb90fece2034d85c7f83", id: u(this, b) }, D$1("div", { key: "75863d9a46178491dd15404929bb24db7168ef5f", class: t(f._, null, { active: r }), part: u(this, v).splash }, D$1("div", { key: "cba0cc1e7103a7c1a516f033d9a4fd5abfb2683a", class: t(f._, f.content), part: u(this, v).content }, D$1("div", { key: "44c08f651fbd3c38334f05c4701ad21cfb25decb", class: t(f._, f.widget), part: u(this, v).widget }, D$1("slot", { key: "a6763485801abb4c955dba3c7dee0eaa3e898fdf" })), D$1("div", { key: "ac99a9d2a6cd942fea72f085f40f845692f7e698", class: t(f._, f.label), part: u(this, v).label }, r ? "Ready!" : e)))));
  }
  disconnectedCallback() {
    var _a;
    (_a = u(this, d)) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return z(this);
  }
};
d = /* @__PURE__ */ new WeakMap(), p = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakMap(), m = /* @__PURE__ */ new WeakMap(), b = /* @__PURE__ */ new WeakMap(), g.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}:host{display:block;font-family:var(--lf-splash-font-family, var(--lf-font-family-primary));font-size:var(--lf-splash-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{margin:0}.splash{background-color:rgba(var(--lf-splash-color-bg, var(--lf-color-bg)), 1);color:rgb(var(--lf-splash-color-on-bg, var(--lf-color-on-bg)));display:flex;height:var(--lf-splash-height, 100dvh);left:var(--lf-splash-left, 0);opacity:1;position:var(--lf-splash-position, fixed);top:var(--lf-splash-top, 0);width:var(--lf-splash-width, 100dvw);z-index:var(--lf-ui-zindex-splash, 999)}.splash--active{transition:opacity 200ms cubic-bezier(0.4, 0, 0.6, 1);opacity:0}.splash__content{margin:auto}.splash__widget{height:var(--lf-splash-widget-height, 10em);margin:var(--lf-splash-widget-margin, auto);width:var(--lf-splash-widget-width, 10em)}.splash__label{font-size:0.875em;font-weight:500;line-height:1.375em;letter-spacing:0.01em;text-align:center}";
export {
  g as lf_splash
};
