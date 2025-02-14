import { o, V as V$1, B as LF_DRAWER_BLOCKS, a as LF_ATTRIBUTES, D as LF_DRAWER_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, E as LF_DRAWER_PROPS, m as mt, U as U$1, F as LF_DRAWER_SLOT, A, T as T$1, G as LF_EFFECTS_FOCUSABLES } from "./index-DlhbnacL.js";
import { o as o$1 } from "./p-c236cf18-D2j4DmvD.js";
var b, p, v, m, y, g, z, x, k, C, E, W, M, T, L, D = function(i, t, e, r) {
  if ("a" === e && !r) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? i !== t || !r : !t.has(i)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === e ? r : "a" === e ? r.call(i) : r ? r.value : t.get(i);
}, j = function(i, t, e, r, s) {
  if ("function" == typeof t ? i !== t || true : !t.has(i)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(i, e), e;
};
const R = class {
  constructor(e) {
    o(this, e), this.lfEvent = V$1(this, "lf-drawer-event"), b.add(this), this.lfDisplay = "slide", this.lfPosition = "left", this.lfResponsive = 0, this.lfStyle = "", this.lfValue = false, p.set(this, void 0), v.set(this, LF_DRAWER_BLOCKS), m.set(this, LF_ATTRIBUTES), y.set(this, LF_DRAWER_PARTS), g.set(this, LF_STYLE_ID), z.set(this, LF_WRAPPER_ID), x.set(this, void 0), k.set(this, null), C.set(this, void 0), E.set(this, void 0);
  }
  onLfEvent(i, t) {
    this.lfEvent.emit({ comp: this, eventType: t, id: this.rootElement.id, originalEvent: i });
  }
  listenKeydown(i) {
    if (this.lfValue) switch (i.key) {
      case "Escape":
        i.preventDefault(), this.close();
        break;
      case "Tab":
        D(this, b, "m", L).call(this, i);
    }
  }
  onLfDisplayChange(i, t) {
    D(this, p, "f") && D(this, b, "m", M).call(this, t, i);
  }
  onLfResponsiveChange() {
    D(this, p, "f") && (this.lfResponsive > 0 ? (D(this, b, "m", W).call(this), D(this, C, "f") || (j(this, C, async () => {
      D(this, E, "f") && clearTimeout(D(this, E, "f")), j(this, E, window.setTimeout(() => {
        D(this, b, "m", W).call(this), j(this, E, null, "f");
      }, 200), "f");
    }), window.addEventListener("resize", D(this, C, "f")))) : D(this, C, "f") && (window.removeEventListener("resize", D(this, C, "f")), j(this, C, null)));
  }
  async close() {
    this.lfValue && requestAnimationFrame(() => {
      this.lfValue = false, this.onLfEvent(new CustomEvent("close"), "close"), D(this, p, "f").effects.backdrop.hide(), D(this, k, "f") && (D(this, k, "f").focus(), j(this, k, null));
    });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const i = LF_DRAWER_PROPS.map((i2) => [i2, this[i2]]);
    return Object.fromEntries(i);
  }
  async isOpened() {
    return this.lfValue;
  }
  async open() {
    this.lfValue || (j(this, k, document.activeElement), requestAnimationFrame(() => {
      this.lfValue = true, this.onLfEvent(new CustomEvent("open"), "open"), "slide" === this.lfDisplay && D(this, p, "f").effects.backdrop.show(() => this.close()), requestAnimationFrame(() => {
        D(this, b, "m", T).call(this);
      });
    }));
  }
  async refresh() {
    mt(this);
  }
  async toggle() {
    this.lfValue ? this.close() : this.open();
  }
  async unmount(i = 0) {
    setTimeout(() => {
      D(this, p, "f").effects.backdrop.hide(), this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, i);
  }
  connectedCallback() {
    D(this, p, "f") && D(this, p, "f").theme.register(this);
  }
  async componentWillLoad() {
    j(this, p, await o$1(this)), this.lfResponsive > 0 && (D(this, b, "m", W).call(this), j(this, C, async () => {
      D(this, E, "f") && clearTimeout(D(this, E, "f")), j(this, E, window.setTimeout(() => {
        D(this, b, "m", W).call(this), j(this, E, null, "f");
      }, 200), "f");
    }), window.addEventListener("resize", D(this, C, "f")));
  }
  componentDidLoad() {
    const { info: i } = D(this, p, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), i.update(this, "did-load");
  }
  componentWillRender() {
    const { info: i } = D(this, p, "f").debug;
    i.update(this, "will-render");
  }
  componentDidRender() {
    const { info: i } = D(this, p, "f").debug;
    i.update(this, "did-render");
  }
  render() {
    const { bemClass: i, setLfStyle: t } = D(this, p, "f").theme, { drawer: e } = D(this, v, "f"), { lfStyle: a } = this, o2 = "slide" === this.lfDisplay && this.lfValue;
    return U$1(A, { key: "2511a3037760165e35a255d068c175254bf3e6c8" }, a && U$1("style", { key: "bb9dc701ae8515ecfbd92984f52f8d3784c34414", id: D(this, g, "f") }, t(this)), U$1("div", { key: "957fdd4724e2cf6376d749a9eb75e5a561d5231f", "aria-modal": o2, id: D(this, z, "f"), ref: (i2) => {
      i2 && j(this, x, i2);
    }, role: "dialog" }, U$1("div", { key: "73aa8f99247d09ae76d357b514cb74ce00eb5ac6", class: i(e._), part: D(this, y, "f").drawer }, U$1("div", { key: "1534d70fa56d84fce76428ab4ab0508606feb01a", class: i(e._, e.content), "lf-data": D(this, m, "f").fadeIn, part: D(this, y, "f").content }, U$1("slot", { key: "fdb3680827b78663e5bd417a8cf9e6ae19aa6f4d", name: LF_DRAWER_SLOT })))));
  }
  disconnectedCallback() {
    var _a, _b;
    D(this, C, "f") && window.removeEventListener("resize", D(this, C, "f")), (_a = D(this, p, "f")) == null ? void 0 : _a.effects.backdrop.hide(), (_b = D(this, p, "f")) == null ? void 0 : _b.theme.unregister(this);
  }
  get rootElement() {
    return T$1(this);
  }
  static get watchers() {
    return { lfDisplay: ["onLfDisplayChange"], lfResponsive: ["onLfResponsiveChange"] };
  }
};
p = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakMap(), m = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), b = /* @__PURE__ */ new WeakSet(), W = function() {
  if (this.lfResponsive <= 0) return;
  const i = this.lfDisplay, t = window.innerWidth >= this.lfResponsive ? "dock" : "slide";
  t !== i && (this.lfDisplay = t, D(this, b, "m", M).call(this, i, t));
}, M = function(i, t) {
  this.lfValue && ("slide" === i && "dock" === t ? D(this, p, "f").effects.backdrop.hide() : "dock" === i && "slide" === t && D(this, p, "f").effects.backdrop.show(() => this.close()));
}, T = function() {
  if (!this.lfValue) return;
  if (!D(this, x, "f")) return;
  const i = D(this, x, "f").querySelector(LF_EFFECTS_FOCUSABLES.join(","));
  i ? i.focus() : D(this, x, "f").focus();
}, L = function(i) {
  if (!this.lfValue || !D(this, x, "f")) return;
  const t = Array.from(D(this, x, "f").querySelectorAll(LF_EFFECTS_FOCUSABLES.join(","))).filter((i2) => i2.offsetWidth > 0 || i2.offsetHeight > 0 || i2 === document.activeElement);
  if (0 === t.length) return void i.preventDefault();
  const e = t[0], r = t[t.length - 1];
  i.shiftKey && document.activeElement === e ? (i.preventDefault(), r.focus()) : i.shiftKey || document.activeElement !== r || (i.preventDefault(), e.focus());
}, R.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-drawer-font-family, var(--lf-font-family-primary));font-size:var(--lf-drawer-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{border:0;border-style:solid;border-radius:var(--lf-drawer-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-drawer-color-drawer, var(--lf-color-drawer)), 0.375);color:rgb(var(--lf-drawer-color-on-drawer, var(--lf-color-on-drawer)));backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);box-sizing:border-box;display:block;height:100dvh;left:calc(var(--lf-ui-width-drawer) * -1);position:absolute;top:0;width:var(--lf-ui-width-drawer);z-index:var(--lf-ui-zindex-drawer)}:host([lf-position=left]){transition:left 300ms cubic-bezier(0.4, 0, 0.2, 1);border-bottom-left-radius:0;border-top-left-radius:0;border-right:var(--lf-drawer-border, 1px solid rgba(var(--lf-color-border), 0.75));left:calc(var(--lf-ui-width-drawer) * -1);right:auto}:host([lf-position=right]){transition:right 300ms cubic-bezier(0.4, 0, 0.2, 1);border-bottom-right-radius:0;border-top-right-radius:0;border-left:var(--lf-drawer-border, 1px solid rgba(var(--lf-color-border), 0.75));left:auto;right:calc(var(--lf-ui-width-drawer) * -1)}:host([lf-display=dock]){box-shadow:none}:host([lf-display=dock])[lf-position=left]{left:0}:host([lf-display=dock])[lf-position=right]{right:0}:host([lf-value]){left:0}:host([lf-value][lf-position=left][lf-display=slide]){box-shadow:var(--lf-drawer-left-box-shadow, 4px 0 10px -2px rgba(var(--lf-color-on-drawer), 0.2), 8px 0 16px 2px rgba(var(--lf-color-on-drawer), 0.14), 2px 0 20px 5px rgba(var(--lf-color-on-drawer), 0.14))}:host([lf-value][lf-position=right][lf-display=slide]){box-shadow:var(--lf-drawer-right-box-shadow, -4px 0 10px -2px rgba(var(--lf-color-on-drawer), 0.2), -8px 0 16px 2px rgba(var(--lf-color-on-drawer), 0.14), -2px 0 20px 5px rgba(var(--lf-color-on-drawer), 0.14))}.drawer,.drawer__content{width:100%;height:100%}";
export {
  R as lf_drawer
};
