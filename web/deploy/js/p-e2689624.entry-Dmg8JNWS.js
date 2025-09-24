import { n, I, bm as LF_HEADER_BLOCKS, bn as LF_HEADER_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, bo as LF_HEADER_PROPS, m as mt, W as W$1, bp as LF_HEADER_SLOT, f as L, G } from "./index-D1ZUnp-K.js";
import { o } from "./p-DklcdYZv-CEo6lGn3.js";
var b, u, v, p, m, z = function(e, r, a, i) {
  if ("function" == typeof r ? e !== r || true : !r.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return r.get(e);
};
const w = class {
  constructor(a) {
    n(this, a), this.lfEvent = I(this, "lf-header-event"), this.lfStyle = "", b.set(this, void 0), u.set(this, LF_HEADER_BLOCKS), v.set(this, LF_HEADER_PARTS), p.set(this, LF_STYLE_ID), m.set(this, LF_WRAPPER_ID);
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
    mt(this);
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
    !(function(e, r, a, i, t) {
      if ("function" == typeof r ? e !== r || true : !r.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
      r.set(e, a);
    })(this, b, await o(this));
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
    const { bemClass: e, setLfStyle: r } = z(this, b).theme, { header: a } = z(this, u), { lfStyle: o2 } = this;
    return W$1(L, { key: "d08eda643b8a9c7bc9d1bb117f09ab64660180f8" }, o2 && W$1("style", { key: "daa7eb123c72b285ce1c827f8adfdc0b0900f59c", id: z(this, p) }, r(this)), W$1("div", { key: "b7499d58b9725b78bc9a608d82b051d5e63cefc3", id: z(this, m) }, W$1("header", { key: "027236b510cbaf1326bcd6a1e948f428670fbb40", class: e(a._), part: z(this, v).header }, W$1("section", { key: "11efdf4a877acc8d00e1e2aecb14fdce8963972f", class: e(a._, a.section), part: z(this, v).section }, W$1("slot", { key: "87c980b4af04a6144b0f3000796a249d8a72bc00", name: LF_HEADER_SLOT })))));
  }
  disconnectedCallback() {
    var _a;
    (_a = z(this, b)) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return G(this);
  }
};
b = /* @__PURE__ */ new WeakMap(), u = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakMap(), p = /* @__PURE__ */ new WeakMap(), m = /* @__PURE__ */ new WeakMap(), w.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}:host{display:block;font-family:var(--lf-header-font-family, var(--lf-font-family-primary));font-size:var(--lf-header-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-header-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{border:0;border-style:solid;border-radius:var(--lf-header-border-radius, var(--lf-ui-border-radius));border-top-left-radius:0;border-top-right-radius:0;background-color:rgba(var(--lf-header-color-header, var(--lf-color-header)), 0.375);color:rgb(var(--lf-header-color-on-header, var(--lf-color-on-header)));backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);box-shadow:0 2px 4px -1px rgba(var(--lf-color-on-header), 0.2), 0 4px 5px 0 rgba(var(--lf-color-on-header), 0.14), 0 1px 10px 0 rgba(var(--lf-color-on-header), 0.12);box-sizing:border-box;display:block;height:var(--lf-ui-height-header);left:0;top:0;width:100%;z-index:var(--lf-ui-zindex-header)}.header{width:100%;height:100%;box-sizing:border-box;display:flex;flex-direction:column;justify-content:var(--lf-header-justify, space-between);padding:var(--lf-header-padding, 0.5em 0.75em)}.header__section{width:100%;height:100%;box-sizing:border-box;display:flex;position:relative}";
export {
  w as lf_header
};
