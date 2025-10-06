import { n, V, aH as LF_HEADER_BLOCKS, aI as LF_HEADER_PARTS, d as LF_STYLE_ID, f as LF_WRAPPER_ID, aJ as LF_HEADER_PROPS, p as pt, D as D$1, aK as LF_HEADER_SLOT, W as W$1, z as z$1 } from "./index-EOkmblAM.js";
import { a } from "./p-Dl9cVpAY-5guf9rt2.js";
var b, u, p, v, m, z = function(e, r, i, t) {
  if ("function" == typeof r ? e !== r || true : !r.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return r.get(e);
};
const w = class {
  constructor(i) {
    n(this, i), this.lfEvent = V(this, "lf-header-event"), this.lfStyle = "", b.set(this, void 0), u.set(this, LF_HEADER_BLOCKS), p.set(this, LF_HEADER_PARTS), v.set(this, LF_STYLE_ID), m.set(this, LF_WRAPPER_ID);
  }
  onLfEvent(e, r) {
    this.lfEvent.emit({ comp: this, id: this.rootElement.id, originalEvent: e, eventType: r });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_HEADER_PROPS.map(((e2) => [e2, this[e2]]));
    return Object.fromEntries(e);
  }
  async refresh() {
    pt(this);
  }
  async unmount(e = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), e);
  }
  connectedCallback() {
    z(this, b) && z(this, b).theme.register(this);
  }
  async componentWillLoad() {
    !(function(e, r, i, t, a2) {
      if ("function" == typeof r ? e !== r || true : !r.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
      r.set(e, i);
    })(this, b, await a(this));
  }
  componentDidLoad() {
    const { info: e } = z(this, b).debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = z(this, b).debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = z(this, b).debug;
    e.update(this, "did-render");
  }
  render() {
    const { bemClass: e, setLfStyle: r } = z(this, b).theme, { header: i } = z(this, u), { lfStyle: o } = this;
    return D$1(W$1, { key: "8b79cfcc84d9c3f941a437797bc323762778518e" }, o && D$1("style", { key: "3828cfff8f58ece70c6e70aafe84e180cd30160d", id: z(this, v) }, r(this)), D$1("div", { key: "46b939b45e13817b4e57c02c13745c3a3939e8b4", id: z(this, m) }, D$1("header", { key: "722c77a14f1f1aeabdd72b6e8966800ea0f818b3", class: e(i._), part: z(this, p).header }, D$1("section", { key: "50f1c709c4b94214697bb37255d3568759e1d89d", class: e(i._, i.section), part: z(this, p).section }, D$1("slot", { key: "8f6b771d309890f35703ab98f078eaf3e2c73a5b", name: LF_HEADER_SLOT })))));
  }
  disconnectedCallback() {
    var _a;
    (_a = z(this, b)) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return z$1(this);
  }
};
b = /* @__PURE__ */ new WeakMap(), u = /* @__PURE__ */ new WeakMap(), p = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakMap(), m = /* @__PURE__ */ new WeakMap(), w.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}:host{display:block;font-family:var(--lf-header-font-family, var(--lf-font-family-primary));font-size:var(--lf-header-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{border:0;border-style:solid;border-radius:var(--lf-header-border-radius, var(--lf-ui-border-radius));border-top-left-radius:0;border-top-right-radius:0;background-color:rgba(var(--lf-header-color-header, var(--lf-color-header)), 0.375);color:rgb(var(--lf-header-color-on-header, var(--lf-color-on-header)));backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);box-shadow:0 2px 4px -1px rgba(var(--lf-color-on-header), 0.2), 0 4px 5px 0 rgba(var(--lf-color-on-header), 0.14), 0 1px 10px 0 rgba(var(--lf-color-on-header), 0.12);box-sizing:border-box;display:block;height:var(--lf-ui-height-header);left:0;top:0;width:100%;z-index:var(--lf-ui-zindex-header)}.header{width:100%;height:100%;box-sizing:border-box;display:flex;flex-direction:column;justify-content:var(--lf-header-justify, space-between);padding:var(--lf-header-padding, 0.5em 0.75em)}.header__section{width:100%;height:100%;box-sizing:border-box;display:flex;position:relative}";
export {
  w as lf_header
};
