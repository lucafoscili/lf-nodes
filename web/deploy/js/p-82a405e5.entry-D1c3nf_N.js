import { n, V, aW as LF_TOAST_BLOCKS, C as CY_ATTRIBUTES, b as LF_ATTRIBUTES, aX as LF_TOAST_PARTS, d as LF_STYLE_ID, aY as LF_TOAST_CSS_VARIABLES, f as LF_WRAPPER_ID, D as D$1, aZ as LF_TOAST_PROPS, p as pt, W as W$1, z as z$1 } from "./index-BCfB3I5o.js";
import { a } from "./p-Dl9cVpAY-BVBOtcmu.js";
var p, u, b, g, y, w, k, z, x, _ = function(t, a2, o, e) {
  if ("function" == typeof a2 ? t !== a2 || true : !a2.has(t)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return a2.get(t);
};
const W = class {
  constructor(e) {
    n(this, e), this.lfEvent = V(this, "lf-toast-event"), this.lfCloseIcon = "", this.lfCloseCallback = () => {
      this.unmount();
    }, this.lfTimer = null, this.lfMessage = "", this.lfStyle = "", this.lfUiSize = "medium", this.lfUiState = "primary", p.set(this, void 0), u.set(this, LF_TOAST_BLOCKS), b.set(this, CY_ATTRIBUTES), g.set(this, LF_ATTRIBUTES), y.set(this, LF_TOAST_PARTS), w.set(this, LF_STYLE_ID), k.set(this, LF_TOAST_CSS_VARIABLES), z.set(this, LF_WRAPPER_ID), x.set(this, ((t = false) => {
      const { assets: a2, theme: e2 } = _(this, p), { get: s } = a2, { bemClass: r } = e2, { toast: i } = _(this, u), { style: l } = s(`./assets/svg/${t ? this.lfCloseIcon : this.lfIcon}.svg`);
      return D$1("div", { class: r(i._, i.icon, { "has-actions": t }), "data-cy": _(this, b).maskedSvg, onPointerDown: t ? (t2) => this.lfCloseCallback(this, t2) : null, part: _(this, y).icon, style: l, tabIndex: t && 0 });
    }));
  }
  onLfEvent(t, a2) {
    this.lfEvent.emit({ comp: this, eventType: a2, id: this.rootElement.id, originalEvent: t });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const t = LF_TOAST_PROPS.map(((t2) => [t2, this[t2]]));
    return Object.fromEntries(t);
  }
  async refresh() {
    pt(this);
  }
  async unmount(t = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), t);
  }
  connectedCallback() {
    _(this, p) && _(this, p).theme.register(this);
  }
  async componentWillLoad() {
    if ((function(t, a2, o, e, s) {
      if ("function" == typeof a2 ? t !== a2 || true : !a2.has(t)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
      a2.set(t, o);
    })(this, p, await a(this)), "" === this.lfCloseIcon) {
      const { "--lf-icon-delete": t } = _(this, p).theme.get.current().variables;
      this.lfCloseIcon = t;
    }
  }
  componentDidLoad() {
    const { info: t } = _(this, p).debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), t.update(this, "did-load");
  }
  componentWillRender() {
    const { info: t } = _(this, p).debug;
    t.update(this, "will-render");
  }
  componentDidRender() {
    const { info: t } = _(this, p).debug, { lfTimer: a2 } = this;
    a2 && setTimeout((() => {
      this.lfCloseCallback ? this.lfCloseCallback(this, null) : this.unmount();
    }), a2), t.update(this, "did-render");
  }
  render() {
    const { theme: t } = _(this, p), { bemClass: a2, setLfStyle: e } = t, { toast: r } = _(this, u), { lfCloseIcon: i, lfIcon: l, lfMessage: n2, lfStyle: f, lfTimer: c } = this;
    return D$1(W$1, { key: "e569d0786ffcc7e54591ab035295a67e77c5fc9a" }, D$1("style", { key: "3ac2600235b052f34f63b295d572e0b8ed8d3b6a", id: _(this, w) }, `
          :host {
            ${c ? `--${_(this, k).timer}: ${c}ms;` : ""}
          }
        ${f && e(this) || ""}`), D$1("div", { key: "9fe6019e6eb0f9638ba6d1e09fc77ffbf3ce7289", id: _(this, z), "data-lf": _(this, g).fadeIn }, D$1("div", { key: "0124659082f10b8e086e5ded657ce7f49e9b07d3", class: a2(r._), "data-lf": _(this, g)[this.lfUiState] }, D$1("div", { key: "1e3f008e79ed4bc5d2f0908207336f22d102ed2c", class: a2(r._, r.accent, { temporary: !!c }) }), D$1("div", { key: "f851569ec778d762125c7f8074e594efcc58a215", class: a2(r._, r.messageWrapper, { full: Boolean(l) && Boolean(i), "has-actions": Boolean(i), "has-icon": Boolean(l) }) }, l && _(this, x).call(this), n2 && D$1("div", { key: "4646a7e6a58a020315348d20a2780c97cd6e84b2", class: a2(r._, r.message) }, n2), i && _(this, x).call(this, true)))));
  }
  disconnectedCallback() {
    var _a;
    (_a = _(this, p)) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return z$1(this);
  }
};
p = /* @__PURE__ */ new WeakMap(), u = /* @__PURE__ */ new WeakMap(), b = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), W.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=danger]{--lf-toast-color-primary:var(\n    --lf-toast-color-danger,\n    var(--lf-color-danger)\n  );--lf-toast-color-on-primary:var(\n    --lf-toast-color-danger,\n    var(--lf-color-on-danger)\n  )}[data-lf=disabled]{opacity:var(--lf-toast-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-toast-color-primary:var(\n    --lf-toast-color-info,\n    var(--lf-color-info)\n  );--lf-toast-color-on-primary:var(\n    --lf-toast-color-info,\n    var(--lf-color-on-info)\n  )}[data-lf=secondary]{--lf-toast-color-primary:var(\n    --lf-toast-color-secondary,\n    var(--lf-color-secondary)\n  );--lf-toast-color-on-primary:var(\n    --lf-toast-color-secondary,\n    var(--lf-color-on-secondary)\n  )}[data-lf=success]{--lf-toast-color-primary:var(\n    --lf-toast-color-success,\n    var(--lf-color-success)\n  );--lf-toast-color-on-primary:var(\n    --lf-toast-color-success,\n    var(--lf-color-on-success)\n  )}[data-lf=warning]{--lf-toast-color-primary:var(\n    --lf-toast-color-warning,\n    var(--lf-color-warning)\n  );--lf-toast-color-on-primary:var(\n    --lf-toast-color-warning,\n    var(--lf-color-on-warning)\n  )}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-toast-font-family, var(--lf-font-family-primary));font-size:var(--lf-toast-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-toast-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%;animation:slideIn 250ms ease-out;box-sizing:border-box;z-index:var(--lf-ui-zindex-toast, 998)}.toast{border:0;border-style:solid;border-radius:var(--lf-toast-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-toast-color-surface, var(--lf-color-surface)), 0.675);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);width:100%;height:100%;box-shadow:var(--lf-ui-box-shadow-modal);display:grid;grid-template-rows:auto 1fr;overflow:hidden}.toast__accent{background-color:rgba(var(--lf-toast-color-primary, var(--lf-color-primary)), 0.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);height:var(--lf-toast-accent-height, 0.25em);width:100%}.toast__accent--temporary{animation:reduceWidthToZero linear var(--lf_toast_timer, 5000ms) forwards}.toast__message-wrapper{align-content:var(--lf-toast-message-align-content, center);box-sizing:border-box;display:grid;gap:1em;grid-template-columns:1fr;height:100%;overflow:auto;padding:var(--lf-toast-padding, 0.75em)}.toast__message-wrapper--has-icon{grid-template-columns:auto 1fr}.toast__message-wrapper--has-actions{grid-template-columns:1fr auto}.toast__message-wrapper--full{grid-template-columns:auto 1fr auto}.toast__icon{background-color:rgba(var(--lf-comp-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin:var(--lf-toast-icon-margin, auto 0.5em);opacity:var(--lf-toast-icon-opacity, 1)}.toast__icon--has-actions{-webkit-mask:var(--lf-icon-clear);mask:var(--lf-icon-clear);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-toast-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);cursor:pointer;margin:auto 0.5em auto auto;position:relative}.toast__icon--has-actions:hover{opacity:0.75}.toast__message{color:rgb(var(--lf-toast-color-on-bg, var(--lf-color-on-bg)));overflow:auto;padding:var(--lf-toast-message-padding, 0.75em 0.75em 0.75em 0)}@media only screen and (max-width: 600px){:host{animation:slideUp 250ms ease-out}}@keyframes reduceWidthToZero{0%{width:100%}100%{width:0}}@keyframes slideIn{0%{transform:var(--lf-toast-slidein-from, translateX(100%))}100%{transform:var(--lf-toast-slidein-to, translateX(0))}}@keyframes slideUp{0%{transform:var(--lf-toast-slideup-from, translateY(100%))}100%{transform:var(--lf-toast-slideup-to, translateY(0))}}";
export {
  W as lf_toast
};
