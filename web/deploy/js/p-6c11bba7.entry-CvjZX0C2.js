import { n, H, X as LF_SPLASH_BLOCKS, Y as LF_SPLASH_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, Z as LF_SPLASH_PROPS, f as de, N, U, F } from "./index-CLXmI-OO.js";
import { o } from "./p-BJbvgtBt-BDBzyvY0.js";
var d, p, v, b, m, u = function(e, t, s, i) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return t.get(e);
};
const g = class {
  constructor(s) {
    n(this, s), this.lfEvent = H(this, "lf-splash-event"), this.state = "initializing", this.lfLabel = "Loading...", this.lfStyle = "", d.set(this, void 0), p.set(this, LF_SPLASH_BLOCKS), v.set(this, LF_SPLASH_PARTS), b.set(this, LF_STYLE_ID), m.set(this, LF_WRAPPER_ID);
  }
  onLfEvent(e, t) {
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: e });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_SPLASH_PROPS.map((e2) => [e2, this[e2]]);
    return Object.fromEntries(e);
  }
  async refresh() {
    de(this);
  }
  async unmount(e = 575) {
    setTimeout(() => {
      this.state = "unmounting", setTimeout(() => {
        this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
      }, 300);
    }, e);
  }
  connectedCallback() {
    u(this, d) && u(this, d).theme.register(this);
  }
  async componentWillLoad() {
    !function(e, t, s, i, a) {
      if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
      t.set(e, s);
    }(this, d, await o(this));
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
    const { bemClass: e, setLfStyle: t } = u(this, d).theme, { lfLabel: s, lfStyle: l, state: o2 } = this, n2 = "unmounting" === o2, { splash: r } = u(this, p);
    return N(U, { key: "e619f4a2c71887611835bab6e1f29ab1b40f95dc" }, l && N("style", { key: "817187da88c539d3c04c06c32ecebacf6fb19985", id: u(this, b) }, t(this)), N("div", { key: "a56de9a50ff252b4fdeb268c7e2b1f14df17bfbd", id: u(this, m) }, N("div", { key: "5e08e82f209309804f7eeccd106c74858446ab66", class: e(r._, null, { active: n2 }), part: u(this, v).splash }, N("div", { key: "43ea78e1ccf20bd60c948a9eb146c09ae02eb323", class: e(r._, r.content), part: u(this, v).content }, N("div", { key: "81545c9d4a837a4651548b27fba534e6eca877e0", class: e(r._, r.widget), part: u(this, v).widget }, N("slot", { key: "9a0ed96228ec9763565d4efa85b93137b458b275" })), N("div", { key: "fe84f2cb00402811dff4d89ee1bd88748512f0e3", class: e(r._, r.label), part: u(this, v).label }, n2 ? "Ready!" : s)))));
  }
  disconnectedCallback() {
    var _a;
    (_a = u(this, d)) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return F(this);
  }
};
d = /* @__PURE__ */ new WeakMap(), p = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakMap(), b = /* @__PURE__ */ new WeakMap(), m = /* @__PURE__ */ new WeakMap(), g.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}:host{display:block;font-family:var(--lf-splash-font-family, var(--lf-font-family-primary));font-size:var(--lf-splash-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-splash-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{margin:0}.splash{background-color:rgba(var(--lf-splash-color-bg, var(--lf-color-bg)), 1);color:rgb(var(--lf-splash-color-on-bg, var(--lf-color-on-bg)));display:flex;height:var(--lf-splash-height, 100dvh);left:var(--lf-splash-left, 0);opacity:1;position:var(--lf-splash-position, fixed);top:var(--lf-splash-top, 0);width:var(--lf-splash-width, 100dvw);z-index:var(--lf-ui-zindex-splash, 999)}.splash--active{transition:opacity 200ms cubic-bezier(0.4, 0, 0.6, 1);opacity:0}.splash__content{margin:auto}.splash__widget{height:var(--lf-splash-widget-height, 10em);margin:var(--lf-splash-widget-margin, auto);width:var(--lf-splash-widget-width, 10em)}.splash__label{font-size:0.875em;font-weight:500;line-height:1.375em;letter-spacing:0.01em;text-align:center}";
export {
  g as lf_splash
};
