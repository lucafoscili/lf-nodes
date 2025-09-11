import { n, I, y as LF_DRAWER_BLOCKS, a as LF_ATTRIBUTES, z as LF_DRAWER_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, A as LF_DRAWER_PROPS, m as mt, W as W$1, B as LF_DRAWER_SLOT, f as L$1, G, D as LF_EFFECTS_FOCUSABLES } from "./index-DBkjGVaZ.js";
import { o } from "./p-DklcdYZv-C8MvA4fT.js";
var b, p, v, m, y, g, z, x, k, C, E, W, M, T, L, D = function(i, t, e, r) {
  if ("a" === e && !r) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof t ? i !== t || !r : !t.has(i)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === e ? r : "a" === e ? r.call(i) : r ? r.value : t.get(i);
}, A = function(i, t, e, r, s) {
  if ("function" == typeof t ? i !== t || true : !t.has(i)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(i, e), e;
};
const j = class {
  constructor(e) {
    n(this, e), this.lfEvent = I(this, "lf-drawer-event"), b.add(this), this.lfDisplay = "slide", this.lfPosition = "left", this.lfResponsive = 0, this.lfStyle = "", this.lfValue = false, p.set(this, void 0), v.set(this, LF_DRAWER_BLOCKS), m.set(this, LF_ATTRIBUTES), y.set(this, LF_DRAWER_PARTS), g.set(this, LF_STYLE_ID), z.set(this, LF_WRAPPER_ID), x.set(this, void 0), k.set(this, null), C.set(this, void 0), E.set(this, void 0);
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
    D(this, p, "f") && (this.lfResponsive > 0 ? (D(this, b, "m", W).call(this), D(this, C, "f") || (A(this, C, (async () => {
      D(this, E, "f") && clearTimeout(D(this, E, "f")), A(this, E, window.setTimeout((() => {
        D(this, b, "m", W).call(this), A(this, E, null, "f");
      }), 200), "f");
    })), window.addEventListener("resize", D(this, C, "f")))) : D(this, C, "f") && (window.removeEventListener("resize", D(this, C, "f")), A(this, C, null)));
  }
  async close() {
    this.lfValue && requestAnimationFrame((() => {
      this.lfValue = false, this.onLfEvent(new CustomEvent("close"), "close"), D(this, p, "f").effects.backdrop.hide(), D(this, k, "f") && (D(this, k, "f").focus(), A(this, k, null));
    }));
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const i = LF_DRAWER_PROPS.map(((i2) => [i2, this[i2]]));
    return Object.fromEntries(i);
  }
  async isOpened() {
    return this.lfValue;
  }
  async open() {
    this.lfValue || (A(this, k, document.activeElement), requestAnimationFrame((() => {
      this.lfValue = true, this.onLfEvent(new CustomEvent("open"), "open"), "slide" === this.lfDisplay && D(this, p, "f").effects.backdrop.show((() => this.close())), requestAnimationFrame((() => {
        D(this, b, "m", T).call(this);
      }));
    })));
  }
  async refresh() {
    mt(this);
  }
  async toggle() {
    this.lfValue ? this.close() : this.open();
  }
  async unmount(i = 0) {
    setTimeout((() => {
      D(this, p, "f").effects.backdrop.hide(), this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), i);
  }
  connectedCallback() {
    D(this, p, "f") && D(this, p, "f").theme.register(this);
  }
  async componentWillLoad() {
    A(this, p, await o(this)), this.lfResponsive > 0 && (D(this, b, "m", W).call(this), A(this, C, (async () => {
      D(this, E, "f") && clearTimeout(D(this, E, "f")), A(this, E, window.setTimeout((() => {
        D(this, b, "m", W).call(this), A(this, E, null, "f");
      }), 200), "f");
    })), window.addEventListener("resize", D(this, C, "f")));
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
    return W$1(L$1, { key: "f4bd7c5cb658a7c2743f363caeefd92c20f0d9e4" }, a && W$1("style", { key: "388b3ce0fcfaa65fa066189ca34f768a1d9a0170", id: D(this, g, "f") }, t(this)), W$1("div", { key: "be76c4d9fe59c1fb2905e304f1e7d6cc46a05d49", "aria-modal": o2, id: D(this, z, "f"), ref: (i2) => {
      i2 && A(this, x, i2);
    }, role: "dialog" }, W$1("div", { key: "3710b99c4db058f755a9f5a5a25b41969b4d59f0", class: i(e._), part: D(this, y, "f").drawer }, W$1("div", { key: "161a88e84b887d17f0e5675b923f15bc35aae12d", class: i(e._, e.content), "lf-data": D(this, m, "f").fadeIn, part: D(this, y, "f").content }, W$1("slot", { key: "a31ab9b41206e945077320ffa5e94fec39eb5786", name: LF_DRAWER_SLOT })))));
  }
  disconnectedCallback() {
    var _a, _b;
    D(this, C, "f") && window.removeEventListener("resize", D(this, C, "f")), (_a = D(this, p, "f")) == null ? void 0 : _a.effects.backdrop.hide(), (_b = D(this, p, "f")) == null ? void 0 : _b.theme.unregister(this);
  }
  get rootElement() {
    return G(this);
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
  this.lfValue && ("slide" === i && "dock" === t ? D(this, p, "f").effects.backdrop.hide() : "dock" === i && "slide" === t && D(this, p, "f").effects.backdrop.show((() => this.close())));
}, T = function() {
  if (!this.lfValue) return;
  if (!D(this, x, "f")) return;
  const i = D(this, x, "f").querySelector(LF_EFFECTS_FOCUSABLES.join(","));
  i ? i.focus() : D(this, x, "f").focus();
}, L = function(i) {
  if (!this.lfValue || !D(this, x, "f")) return;
  const t = Array.from(D(this, x, "f").querySelectorAll(LF_EFFECTS_FOCUSABLES.join(","))).filter(((i2) => i2.offsetWidth > 0 || i2.offsetHeight > 0 || i2 === document.activeElement));
  if (0 === t.length) return void i.preventDefault();
  const e = t[0], r = t[t.length - 1];
  i.shiftKey && document.activeElement === e ? (i.preventDefault(), r.focus()) : i.shiftKey || document.activeElement !== r || (i.preventDefault(), e.focus());
}, j.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-drawer-font-family, var(--lf-font-family-primary));font-size:var(--lf-drawer-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-drawer-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{border:0;border-style:solid;border-radius:var(--lf-drawer-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-drawer-color-drawer, var(--lf-color-drawer)), 0.375);color:rgb(var(--lf-drawer-color-on-drawer, var(--lf-color-on-drawer)));backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);box-sizing:border-box;display:block;height:100dvh;left:calc(var(--lf-ui-width-drawer) * -1);position:absolute;top:0;width:var(--lf-ui-width-drawer);z-index:var(--lf-ui-zindex-drawer)}:host([lf-position=left]){transition:left 300ms cubic-bezier(0.4, 0, 0.2, 1);border-bottom-left-radius:0;border-top-left-radius:0;border-right:var(--lf-drawer-border, 1px solid rgba(var(--lf-color-border), 0.75));left:calc(var(--lf-ui-width-drawer) * -1);right:auto}:host([lf-position=right]){transition:right 300ms cubic-bezier(0.4, 0, 0.2, 1);border-bottom-right-radius:0;border-top-right-radius:0;border-left:var(--lf-drawer-border, 1px solid rgba(var(--lf-color-border), 0.75));left:auto;right:calc(var(--lf-ui-width-drawer) * -1)}:host([lf-display=dock]){box-shadow:none}:host([lf-display=dock])[lf-position=left]{left:0}:host([lf-display=dock])[lf-position=right]{right:0}:host([lf-value]){left:0}:host([lf-value][lf-position=left][lf-display=slide]){box-shadow:var(--lf-drawer-left-box-shadow, 4px 0 10px -2px rgba(var(--lf-color-on-drawer), 0.2), 8px 0 16px 2px rgba(var(--lf-color-on-drawer), 0.14), 2px 0 20px 5px rgba(var(--lf-color-on-drawer), 0.14))}:host([lf-value][lf-position=right][lf-display=slide]){box-shadow:var(--lf-drawer-right-box-shadow, -4px 0 10px -2px rgba(var(--lf-color-on-drawer), 0.2), -8px 0 16px 2px rgba(var(--lf-color-on-drawer), 0.14), -2px 0 20px 5px rgba(var(--lf-color-on-drawer), 0.14))}.drawer,.drawer__content{width:100%;height:100%}";
export {
  j as lf_drawer
};
