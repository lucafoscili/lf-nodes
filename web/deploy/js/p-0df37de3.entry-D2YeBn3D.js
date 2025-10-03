import { n, V, f as LF_SPLASH_BLOCKS, g as LF_SPLASH_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, h as LF_SPLASH_PROPS, p as pt, D as D$1, W as W$1, z } from "./index-CAhA1yg9.js";
import { a } from "./p-Dl9cVpAY-bPm7KoFq.js";
var d, p, v, m, b, u = function(e, t, s, a2) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return t.get(e);
};
const g = class {
  constructor(s) {
    n(this, s), this.lfEvent = V(this, "lf-splash-event"), this.state = "initializing", this.lfLabel = "Loading...", this.lfStyle = "", d.set(this, void 0), p.set(this, LF_SPLASH_BLOCKS), v.set(this, LF_SPLASH_PARTS), m.set(this, LF_STYLE_ID), b.set(this, LF_WRAPPER_ID);
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_SPLASH_PROPS.map(((e2) => [e2, this[e2]]));
    return Object.fromEntries(e);
  }
  async refresh() {
    pt(this);
  }
  async unmount(e = 575) {
    setTimeout((() => {
      this.state = "unmounting", setTimeout((() => {
        this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
      }), 300);
    }), e);
  }
  connectedCallback() {
    u(this, d) && u(this, d).theme.register(this);
  }
  async componentWillLoad() {
    !(function(e, t, s, a2, i) {
      if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
      t.set(e, s);
    })(this, d, await a(this));
  }
  componentDidLoad() {
    const { info: e } = u(this, d).debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = u(this, d).debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = u(this, d).debug;
    e.update(this, "did-render");
  }
  render() {
    const { bemClass: e, setLfStyle: t } = u(this, d).theme, { lfLabel: s, lfStyle: l, state: o } = this, r = "unmounting" === o, { splash: f } = u(this, p);
    return D$1(W$1, { key: "b2f8e4fa5ca16c1ec0835688eaf8c8db79e004de" }, l && D$1("style", { key: "01e56d34ff2df739886396381e1d9c3ee75c44c7", id: u(this, m) }, t(this)), D$1("div", { key: "a63455f43781ab1dd0a7de874516107aeda037e4", id: u(this, b) }, D$1("div", { key: "28b288678d2c163dab061b917c84ea4b8dd8f1c1", class: e(f._, null, { active: r }), part: u(this, v).splash }, D$1("div", { key: "6939e6eff13d37bbfbf3f7c59f496c70699cd9c8", class: e(f._, f.content), part: u(this, v).content }, D$1("div", { key: "ad9c8d8d3d00c153bf1d6bbee56fae140c5c462e", class: e(f._, f.widget), part: u(this, v).widget }, D$1("slot", { key: "3b97f4a962a2a10527a568a2b935b79b43be6ca8" })), D$1("div", { key: "1e98521df8a0244361a51d011aba684d3b1fbfe1", class: e(f._, f.label), part: u(this, v).label }, r ? "Ready!" : s)))));
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
