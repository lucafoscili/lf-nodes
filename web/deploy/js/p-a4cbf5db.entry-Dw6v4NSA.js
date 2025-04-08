import { o, V as V$1, bd as LF_LIST_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, be as LF_LIST_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, bf as LF_LIST_PROPS, m as mt, U as U$1, A as A$1, T as T$1, bg as LF_SPINNER_PROPS } from "./index-C1C0sYsA.js";
import { o as o$1 } from "./p-c236cf18-izR9TZep.js";
var v, b, u, g, k, y, w, x, z, _, C, E, W, T, D, N, M = function(e, i, r, n) {
  if ("a" === r && !n) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof i ? e !== i || !n : !i.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === r ? n : "a" === r ? n.call(e) : n ? n.value : i.get(e);
}, S = function(e, i, r, n, s) {
  if ("function" == typeof i ? e !== i || true : !i.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return i.set(e, r), r;
};
const j = class {
  constructor(r) {
    o(this, r), this.lfEvent = V$1(this, "lf-list-event"), v.add(this), this.lfDataset = null, this.lfEmpty = "Empty data.", this.lfEnableDeletions = false, this.lfNavigation = true, this.lfRipple = true, this.lfSelectable = true, this.lfStyle = "", this.lfUiSize = "medium", this.lfUiState = "primary", this.lfValue = null, b.set(this, void 0), u.set(this, LF_LIST_BLOCKS), g.set(this, CY_ATTRIBUTES), k.set(this, LF_ATTRIBUTES), y.set(this, LF_LIST_PARTS), w.set(this, []), x.set(this, LF_STYLE_ID), z.set(this, LF_WRAPPER_ID), _.set(this, []);
  }
  onLfEvent(e, i, r, n = 0) {
    const { effects: s } = M(this, b, "f");
    switch (i) {
      case "blur":
        this.focused = null;
        break;
      case "click":
        this.focused = n, M(this, v, "m", C).call(this, n);
        break;
      case "delete":
        n > -1 && (this.lfDataset.nodes.splice(n, 1), this.refresh());
        break;
      case "focus":
        this.focused = n;
        break;
      case "pointerdown":
        this.lfRipple && s.ripple(e, M(this, w, "f")[n]);
    }
    this.lfEvent.emit({ comp: this, eventType: i, id: this.rootElement.id, originalEvent: e, node: r });
  }
  listenKeydown(e) {
    const { focused: i, lfNavigation: r } = this;
    if (r) switch (e.key) {
      case "ArrowDown":
        e.preventDefault(), e.stopPropagation(), this.focusNext();
        break;
      case "ArrowUp":
        e.preventDefault(), e.stopPropagation(), this.focusPrevious();
        break;
      case "Enter":
        e.preventDefault(), e.stopPropagation(), M(this, v, "m", C).call(this, i);
    }
  }
  async focusNext() {
    const { focused: e, selected: i } = this;
    isNaN(e) || null == e ? this.focused = i : this.focused++, this.focused > M(this, _, "f").length - 1 && (this.focused = 0), M(this, _, "f")[this.focused].focus();
  }
  async focusPrevious() {
    const { focused: e, selected: i } = this;
    isNaN(e) || null == e ? this.focused = i : this.focused--, this.focused < 0 && (this.focused = M(this, _, "f").length - 1), M(this, _, "f")[this.focused].focus();
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_LIST_PROPS.map((e2) => [e2, this[e2]]);
    return Object.fromEntries(e);
  }
  async getSelected() {
    return this.lfDataset.nodes[this.selected];
  }
  async refresh() {
    mt(this);
  }
  async selectNode(e) {
    void 0 === e && (e = this.focused), M(this, v, "m", C).call(this, e);
  }
  async unmount(e = 0) {
    setTimeout(() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, e);
  }
  connectedCallback() {
    M(this, b, "f") && M(this, b, "f").theme.register(this);
  }
  async componentWillLoad() {
    S(this, b, await o$1(this)), this.lfValue && "number" == typeof this.lfValue && (this.selected = this.lfValue);
  }
  componentDidLoad() {
    const { debug: e } = M(this, b, "f");
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.info.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = M(this, b, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = M(this, b, "f").debug;
    e.update(this, "did-render");
  }
  render() {
    var _a;
    const { bemClass: e, setLfStyle: i } = M(this, b, "f").theme, { emptyData: r, list: t } = M(this, u, "f"), { lfDataset: a, lfEmpty: o2, lfSelectable: l, lfStyle: c } = this, f = !((_a = a == null ? void 0 : a.nodes) == null ? void 0 : _a.length);
    return S(this, _, []), U$1(A$1, { key: "3ccb26e779601b260cf06b045836d1962dcc5166" }, c && U$1("style", { key: "9ce623e9fda10dafd0a43638f86488aaf3c32bed", id: M(this, x, "f") }, i(this)), U$1("div", { key: "13de27c7463e9d83ae14facef78421a9ea1f5390", id: M(this, z, "f") }, f ? U$1("div", { class: e(r._), part: M(this, y, "f").emptyData }, U$1("div", { class: e(r._, r.text) }, o2)) : U$1("ul", { "aria-multiselectable": "false", class: e(t._, null, { empty: f, selectable: l }), part: M(this, y, "f").list, role: "listbox" }, a.nodes.map((e2, i2) => M(this, v, "m", T).call(this, e2, i2)))));
  }
  disconnectedCallback() {
    var _a;
    (_a = M(this, b, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return T$1(this);
  }
};
b = /* @__PURE__ */ new WeakMap(), u = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakSet(), C = function(e) {
  this.lfSelectable && null != e && !isNaN(e) && (this.selected = e);
}, E = function(e) {
  const { bemClass: i } = M(this, b, "f").theme;
  return U$1("div", { class: i(M(this, u, "f").delete._), "data-cy": M(this, g, "f").button, "data-lf": M(this, k, "f").icon, onClick: (i2) => {
    var _a, _b;
    const r = (_b = (_a = this.lfDataset) == null ? void 0 : _a.nodes) == null ? void 0 : _b.indexOf(e);
    this.onLfEvent(i2, "delete", e, r);
  }, part: M(this, y, "f").delete }, U$1("div", { class: i(M(this, u, "f").delete._, M(this, u, "f").delete.icon), key: e.id + "_delete" }));
}, W = function(e) {
  const { get: i } = M(this, b, "f").assets, { bemClass: r } = M(this, b, "f").theme, { style: s } = i(`./assets/svg/${e.icon}.svg`);
  return U$1("div", { class: r(M(this, u, "f").node._, M(this, u, "f").node.icon), "data-cy": M(this, g, "f").maskedSvg, style: s });
}, T = function(e, i) {
  const { stringify: r } = M(this, b, "f").data.cell, { bemClass: s } = M(this, b, "f").theme, { list: t } = M(this, u, "f"), { focused: a, lfDataset: o2, lfRipple: l, selected: c } = this, f = a === o2.nodes.findIndex((i2) => i2.id === e.id), m = c === o2.nodes.findIndex((i2) => i2.id === e.id);
  return U$1("li", { class: s(t._, t.item, { focused: f, "has-description": !!e.description, selected: m }), "data-lf": M(this, k, "f")[this.lfUiState], key: e.id }, this.lfEnableDeletions ? M(this, v, "m", E).call(this, e) : null, U$1("div", { "aria-checked": m, "aria-selected": m, class: s(M(this, u, "f").node._), "data-cy": M(this, g, "f").node, "data-index": i.toString(), onBlur: (r2) => this.onLfEvent(r2, "blur", e, i), onClick: (r2) => this.onLfEvent(r2, "click", e, i), onFocus: (r2) => this.onLfEvent(r2, "focus", e, i), onPointerDown: (r2) => this.onLfEvent(r2, "pointerdown", e, i), part: M(this, y, "f").node, ref: (e2) => {
    e2 && M(this, _, "f").push(e2);
  }, role: "option", tabindex: m ? "0" : "-1", title: r(e.value) || r(e.description) }, U$1("div", { "data-cy": M(this, g, "f").rippleSurface, "data-lf": M(this, k, "f").rippleSurface, ref: (e2) => {
    l && e2 && M(this, w, "f").push(e2);
  } }), e.icon && M(this, v, "m", W).call(this, e), U$1("span", { class: s(M(this, u, "f").node._, M(this, u, "f").node.text) }, M(this, v, "m", N).call(this, e), M(this, v, "m", D).call(this, e))));
}, D = function(e) {
  const { bemClass: i } = M(this, b, "f").theme;
  return e.description && U$1("div", { class: i(M(this, u, "f").node._, M(this, u, "f").node.subtitle) }, e.description);
}, N = function(e) {
  const { bemClass: i } = M(this, b, "f").theme;
  return String(e.value).valueOf() && U$1("div", { class: i(M(this, u, "f").node._, M(this, u, "f").node.title) }, String(e.value).valueOf());
}, j.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}[data-lf=danger]{--lf-list-color-primary:var(\n    --lf-list-color-danger,\n    var(--lf-color-danger)\n  );--lf-list-color-on-primary:var(\n    --lf-list-color-danger,\n    var(--lf-color-on-danger)\n  )}[data-lf=disabled]{opacity:var(--lf-list-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-list-color-primary:var(\n    --lf-list-color-info,\n    var(--lf-color-info)\n  );--lf-list-color-on-primary:var(\n    --lf-list-color-info,\n    var(--lf-color-on-info)\n  )}[data-lf=secondary]{--lf-list-color-primary:var(\n    --lf-list-color-secondary,\n    var(--lf-color-secondary)\n  );--lf-list-color-on-primary:var(\n    --lf-list-color-secondary,\n    var(--lf-color-on-secondary)\n  )}[data-lf=success]{--lf-list-color-primary:var(\n    --lf-list-color-success,\n    var(--lf-color-success)\n  );--lf-list-color-on-primary:var(\n    --lf-list-color-success,\n    var(--lf-color-on-success)\n  )}[data-lf=warning]{--lf-list-color-primary:var(\n    --lf-list-color-warning,\n    var(--lf-color-warning)\n  );--lf-list-color-on-primary:var(\n    --lf-list-color-warning,\n    var(--lf-color-on-warning)\n  )}:host{display:block;font-family:var(--lf-list-font-family, var(--lf-font-family-primary));font-size:var(--lf-list-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-list-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-list-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-list-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-list-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-list-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-list-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-list-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%;outline:none}.list{border:0;border-style:solid;border-color:rgba(var(--lf-list-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-list-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-list-color-bg, var(--lf-color-bg)), 0.275);color:rgb(var(--lf-list-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);width:100%;height:100%;box-sizing:border-box;list-style-type:none;margin:0;overflow:auto;padding:0.5em 0}.list--empty{padding:0}.list--selectable .list__item{cursor:pointer;user-select:none}.list:not(.list.list--selectable) .list__item{cursor:default;pointer-events:none}.list__item{transition:all 150ms cubic-bezier(0.42, 0, 0.58, 1);display:flex;height:var(--lf-list-item-height, 2.5em);width:100%}.list__item:hover{background-color:rgba(var(--lf-list-color-on-bg, var(--lf-color-on-bg)), 0.125);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.list__item:hover .delete{width:1.5em}.list__item--has-description{height:var(--lf-list-item-with-description-height, 3.6em)}.list__item--focused{background-color:rgba(var(--lf-list-color-primary, var(--lf-color-primary)), 0.225);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.list__item--selected{background-color:rgba(var(--lf-list-color-primary, var(--lf-color-primary)), 0.325);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.list__item--selected:hover{background-color:rgba(var(--lf-list-color-primary, var(--lf-color-primary)), 0.475);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.delete{background-color:rgba(var(--lf-list-color-danger, var(--lf-color-danger)), 0.575);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);transition:all 150ms cubic-bezier(0.42, 0, 0.58, 1);align-content:center;box-sizing:border-box;opacity:0.75;overflow:hidden;width:0}.delete:hover{opacity:1}.delete__icon{-webkit-mask:var(--lf-icon-clear);mask:var(--lf-icon-clear);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-list-color-on-danger, var(--lf-color-on-danger)), 1);height:1.5em;width:1.5em;overflow:hidden;margin:0}.node{transition:all 150ms cubic-bezier(0.42, 0, 0.58, 1);align-items:center;box-sizing:border-box;display:flex;justify-content:flex-start;padding:var(--lf-list-item-padding, 0 0.75em);position:relative;outline:none;overflow:hidden;width:100%}.node__title{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:0.5em;margin-left:1.5em;display:block;margin-bottom:-1.5em;margin-left:0;margin-top:0}.node__title:before{content:"";display:inline-block;height:1.5em;vertical-align:0;width:0}.node__title:after{content:"";display:inline-block;width:0;height:2em;vertical-align:-2em}.node__subtitle{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.875em;font-weight:500;line-height:1.375em;letter-spacing:0.01em;display:block;margin-top:0;opacity:0.75;padding-bottom:0.5em}.node__icon{background-color:rgba(var(--lf-list-color-on-bg, var(--lf-color-on-bg)), 1);height:1.5em;width:1.5em;overflow:hidden;margin:0 0.75em 0 0}.node__text{overflow:hidden;width:100%}.empty-data{border:0;border-style:solid;border-color:rgba(var(--lf-list-border-color, var(--lf-color-border)), 1);border-width:1px;border-radius:var(--lf-list-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-list-color-bg, var(--lf-color-bg)), 0.275);color:rgb(var(--lf-list-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);width:100%;height:100%;font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:1em;align-items:center;box-sizing:border-box;display:flex;justify-content:center}';
const A = { 1: { className: "spinner-bar-v1", elements: () => [] }, 2: { className: "spinner-bar-v2", elements: () => [] }, 3: { className: "spinner-bar-v3", elements: (e) => [U$1("div", { class: "progress-bar", style: { width: `${e}%` } })] } }, P = { 7: { className: "spinner-v7", elements: () => Array(6).fill(0).map(() => U$1("div", { class: "sk-spinner-v7-dot" })) }, 9: { className: "spinner-v9", elements: () => [U$1("div", { class: "sk-spinner-v9-bounce1" }), U$1("div", { class: "sk-spinner-v9-bounce2" })] }, 10: { className: "spinner-v10", elements: () => [U$1("div", { class: "sk-spinner-v10-cube1" }), U$1("div", { class: "sk-spinner-v10-cube2" })] }, 12: { className: "spinner-v12", elements: () => [U$1("div", { class: "sk-spinner-v12-dot1" }), U$1("div", { class: "sk-spinner-v12-dot2" })] }, 13: { className: "spinner-v13", elements: () => Array(9).fill(0).map((e, i) => U$1("div", { class: `sk-spinner-v13-cube sk-spinner-v13-cube${i + 1}` })) }, 14: { className: "spinner-v14", elements: () => Array(12).fill(0).map((e, i) => U$1("div", { class: `sk-spinner-v14-circle${i + 1} sk-spinner-v14-circle` })) } };
var Z, F, L, X, Y, B, $ = function(e, i, r, n) {
  if ("a" === r && !n) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof i ? e !== i || !n : !i.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === r ? n : "a" === r ? n.call(e) : n ? n.value : i.get(e);
}, R = function(e, i, r, n, s) {
  if ("function" == typeof i ? e !== i || true : !i.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return i.set(e, r), r;
};
const V = class {
  constructor(r) {
    o(this, r), this.lfEvent = V$1(this, "lf-spinner-event"), Z.add(this), this.bigWait = false, this.progress = 0, this.lfActive = false, this.lfBarVariant = false, this.lfDimensions = "", this.lfFader = false, this.lfFaderTimeout = 3500, this.lfFullScreen = false, this.lfLayout = 1, this.lfStyle = "", this.lfTimeout = 0, F.set(this, void 0), L.set(this, LF_STYLE_ID), X.set(this, LF_WRAPPER_ID), Y.set(this, void 0);
  }
  lfBarVariantChanged(e) {
    $(this, F, "f") && (e && this.lfTimeout ? $(this, Z, "m", B).call(this) : (this.progress = 0, cancelAnimationFrame($(this, Y, "f"))));
  }
  lfTimeoutChanged(e, i) {
    $(this, F, "f") && e !== i && this.lfBarVariant && $(this, Z, "m", B).call(this);
  }
  onLfEvent(e, i) {
    this.lfEvent.emit({ comp: this, id: this.rootElement.id, originalEvent: e, eventType: i });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_SPINNER_PROPS.map((e2) => [e2, this[e2]]);
    return Object.fromEntries(e);
  }
  async refresh() {
    mt(this);
  }
  async unmount(e = 0) {
    setTimeout(() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, e);
  }
  connectedCallback() {
    $(this, F, "f") && $(this, F, "f").theme.register(this);
  }
  async componentWillLoad() {
    R(this, F, await o$1(this));
  }
  componentDidLoad() {
    const { info: e } = $(this, F, "f").debug, { lfBarVariant: i, lfTimeout: r } = this;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load"), i && r && $(this, Z, "m", B).call(this);
  }
  componentWillRender() {
    const { info: e } = $(this, F, "f").debug;
    e.update(this, "will-render");
  }
  componentWillUpdate() {
    this.lfFader && (this.bigWait = false);
  }
  componentDidRender() {
    const { info: e } = $(this, F, "f").debug;
    this.rootElement.shadowRoot && this.lfFader && this.lfActive && setTimeout(() => {
      this.bigWait = true;
    }, this.lfFaderTimeout), e.update(this, "did-render");
  }
  render() {
    const { setLfStyle: e } = $(this, F, "f").theme, { bigWait: i, lfBarVariant: r, lfDimensions: t, lfFullScreen: a, lfLayout: o2, lfStyle: l, progress: c } = this, f = { height: a ? void 0 : "100%", width: a ? void 0 : "100%", fontSize: t || (r ? "0.25em" : ".875em") }, m = r ? A[o2] : P[o2], p = r ? "loading-wrapper-master-bar" : "loading-wrapper-master-spinner", d = { "spinner-version": !r, "big-wait": i }, h = (m == null ? void 0 : m.className) || `spinner-${r ? "bar-v" : "v"}${o2}`, v2 = (m == null ? void 0 : m.elements(c)) || [];
    return U$1(A$1, { key: "aadaa863383ee09ec9144e7a7271a1ef6f8128da", style: f }, l && U$1("style", { key: "6668e69726737ec2d3e8c433e04d9281616804dd", id: $(this, L, "f") }, e(this)), U$1("div", { key: "30f34d19846f5d13f0e8d662539a8246c756873b", id: $(this, X, "f"), style: f }, U$1("div", { key: "bb01af4c72dbffd01a4015c4825f0590a41a4f48", id: "loading-wrapper-master", class: { ...d }, style: f }, U$1("div", { key: "3a0f37632281d446a9d8e4df075f7622da374990", id: p, style: f }, U$1("div", { key: "bfa6468839aecba00e6b956a7e12385eca7e333b", class: h }, v2)))));
  }
  disconnectedCallback() {
    var _a;
    (_a = $(this, F, "f")) == null ? void 0 : _a.theme.unregister(this), cancelAnimationFrame($(this, Y, "f"));
  }
  get rootElement() {
    return T$1(this);
  }
  static get watchers() {
    return { lfBarVariant: ["lfBarVariantChanged"], lfTimeout: ["lfTimeoutChanged"] };
  }
};
F = /* @__PURE__ */ new WeakMap(), L = /* @__PURE__ */ new WeakMap(), X = /* @__PURE__ */ new WeakMap(), Y = /* @__PURE__ */ new WeakMap(), Z = /* @__PURE__ */ new WeakSet(), B = function() {
  this.progress = 0;
  const e = Date.now(), i = this.lfTimeout, r = () => {
    const n = Date.now() - e;
    this.progress = Math.min(n / i * 100, 100), this.progress < 100 ? R(this, Y, requestAnimationFrame(r)) : cancelAnimationFrame($(this, Y, "f"));
  };
  R(this, Y, requestAnimationFrame(r));
}, V.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}[data-lf=danger]{--lf-spinner-color-primary:var(\n    --lf-spinner-color-danger,\n    var(--lf-color-danger)\n  );--lf-spinner-color-on-primary:var(\n    --lf-spinner-color-danger,\n    var(--lf-color-on-danger)\n  )}[data-lf=disabled]{opacity:var(--lf-spinner-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-spinner-color-primary:var(\n    --lf-spinner-color-info,\n    var(--lf-color-info)\n  );--lf-spinner-color-on-primary:var(\n    --lf-spinner-color-info,\n    var(--lf-color-on-info)\n  )}[data-lf=secondary]{--lf-spinner-color-primary:var(\n    --lf-spinner-color-secondary,\n    var(--lf-color-secondary)\n  );--lf-spinner-color-on-primary:var(\n    --lf-spinner-color-secondary,\n    var(--lf-color-on-secondary)\n  )}[data-lf=success]{--lf-spinner-color-primary:var(\n    --lf-spinner-color-success,\n    var(--lf-color-success)\n  );--lf-spinner-color-on-primary:var(\n    --lf-spinner-color-success,\n    var(--lf-color-on-success)\n  )}[data-lf=warning]{--lf-spinner-color-primary:var(\n    --lf-spinner-color-warning,\n    var(--lf-color-warning)\n  );--lf-spinner-color-on-primary:var(\n    --lf-spinner-color-warning,\n    var(--lf-color-on-warning)\n  )}:host{display:block;font-family:var(--lf-spinner-font-family, var(--lf-font-family-primary));font-size:var(--lf-spinner-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-spinner-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-spinner-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-spinner-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-spinner-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-spinner-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-spinner-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-spinner-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}#loading-wrapper-master{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);background:transparent;opacity:0;overflow:hidden;transform:translateZ(0)}#loading-wrapper-master.spinner-version>#loading-wrapper-master-spinner{width:100%;height:100%;position:relative}#loading-wrapper-master.spinner-version>#loading-wrapper-master-spinner div{position:absolute;top:0;right:0;bottom:0;left:0;margin:auto}:host([lf-active]) #loading-wrapper-master{opacity:1}:host([lf-active]) #loading-wrapper-master.spinner-version>#loading-wrapper-master-spinner{opacity:1;overflow:hidden}:host([lf-active]) #loading-wrapper-master[lf-bar-variant]>#loading-wrapper-master-bar{opacity:1}:host([lf-active]) #loading-wrapper-master[lf-bar-variant]>#loading-wrapper-master-bar div.spinner-bar-v2{animation:sk-spinner-bar-v2 20s;background-color:rgb(var(--lf-color-on-spinner));left:-1%}:host([lf-active]) #loading-wrapper-master.loading-wrapper-big-wait{background:rgba(var(--lf-comp-color-bg, var(--lf-color-bg)), 0.25)}:host([lf-active]) #loading-wrapper-master.loading-wrapper-big-wait>#loading-wrapper-master-spinner{font-size:10px}:host([lf-full-screen]) #loading-wrapper-master{position:fixed;top:0;left:0;right:0;bottom:0;pointer-events:none;width:100%;z-index:9999}:host([lf-full-screen]) #loading-wrapper-master div,:host([lf-full-screen]) #loading-wrapper-master.spinner-version #loading-wrapper-master-spinner{position:fixed;transition:opacity 1.25s ease-in, background-color 1s ease-in, top 0.5s ease-in}.spinner-bar-v1{position:absolute;overflow:hidden;transform:translateZ(0);width:100%;height:1em}.spinner-bar-v1:before{content:"";position:absolute;width:25%;height:1em;animation:sk-spinner-bar-v1 5s linear infinite;transform:translateZ(0)}.spinner-bar-v2{position:absolute;overflow:hidden;transform:translateZ(0);box-shadow:-1px 0px 2px 2px rgb(var(--lf-color-on-spinner));height:calc(1em - 2px);width:100%;animation:sk-spinner-bar-v2 5s forwards;animation-timing-function:cubic-bezier(0.19, 0.78, 0.19, 0.78)}.spinner-bar-v3{background-color:rgb(var(--lf-color-spinner));height:calc(1.5em - 2px);position:absolute;overflow:hidden;width:100%}.spinner-bar-v3 .progress-bar{animation:sk-spinner-bar-v3 1s infinite ease-in-out;background-color:rgb(var(--lf-color-on-spinner));height:100%;transition:width 0.1s linear}@keyframes sk-spinner-bar-v1{from{left:-25%;background:linear-gradient(to left, rgb(var(--lf-color-on-spinner)) 0, transparent 100%)}50%{left:100%}to{left:-25%;background:linear-gradient(to right, rgb(var(--lf-color-on-spinner)) 0, transparent 100%)}}@keyframes sk-spinner-bar-v2{from{left:-100%}to{left:-1%}}@keyframes sk-spinner-bar-v3{0%{opacity:1}50%{opacity:0.6}100%{opacity:1}}.spinner-v1{width:7em;height:7em;border-radius:50%;border-top:1em solid rgb(var(--lf-color-spinner));border-right:1em solid rgb(var(--lf-color-spinner));border-bottom:1em solid rgb(var(--lf-color-spinner));border-left:1em solid rgb(var(--lf-color-on-spinner));transform:translateZ(0);animation:sk-spinner-v1 1.1s infinite linear}.spinner-v2,.spinner-v2:before,.spinner-v2:after{border-radius:50%;width:2em;height:2em;animation-fill-mode:both;animation:sk-spinner-v2 1.4s infinite ease-in-out;transform:translateZ(0)}.spinner-v2{backface-visibility:hidden;color:rgb(var(--lf-color-on-spinner));font-size:1em;transform:translateY(-2.5em);animation-delay:-0.16s}.spinner-v2:before,.spinner-v2:after{content:"";position:absolute;top:0}.spinner-v2:before{left:-4em;animation-delay:-0.32s}.spinner-v2:after{left:4em}.spinner-v3{color:rgb(var(--lf-color-on-spinner));font-size:6em;width:1em;height:1em;border-radius:50%;transform:translateZ(0);animation:sk-spinner-v3 1.7s infinite ease, sk-spinner-v3-1 1.7s infinite ease}.spinner-v4{color:rgb(var(--lf-color-on-spinner));width:1em;height:1em;border-radius:50%;transform:translateZ(0);animation:sk-spinner-v4 1.3s infinite linear}.spinner-v5{width:9em;height:9em;margin-top:-0.8em;border-radius:50%;background:linear-gradient(to right, rgb(var(--lf-color-on-spinner)) 10%, rgba(255, 255, 255, 0) 42%);transform:translateZ(0);animation:sk-spinner-v5 1.4s infinite linear}.spinner-v5::before{content:"";width:50%;height:50%;background:rgb(var(--lf-color-on-spinner));border-radius:100% 0 0 0;position:absolute;top:0;left:0}.spinner-v5::after{content:"";width:75%;height:75%;background:rgb(var(--lf-color-spinner));border-radius:50%;position:absolute;margin:auto;top:0;right:0;bottom:0;left:0}.spinner-v6,.spinner-v6:before,.spinner-v6:after{background:rgb(var(--lf-color-on-spinner));animation:sk-spinner-v6 1s infinite ease-in-out;width:1em;height:4em}.spinner-v6{color:rgb(var(--lf-color-on-spinner));margin-top:2em;transform:translateZ(0);animation-delay:-0.16s}.spinner-v6:before,.spinner-v6:after{content:"";position:absolute;top:0}.spinner-v6:before{left:-1.5em;animation-delay:-0.32s}.spinner-v6:after{left:1.5em}.spinner-v7{width:6em;height:6em;position:relative;animation:sk-spinner-v7 2.5s infinite linear both}.sk-spinner-v7-dot{width:100%;height:100%;position:absolute;left:0;top:0;animation:sk-spinner-v7-dot 2s infinite ease-in-out both}.sk-spinner-v7-dot:before{content:"";display:block;width:25%;height:25%;background-color:rgb(var(--lf-color-on-spinner));border-radius:100%;animation:sk-spinner-v7-dot-before 2s infinite ease-in-out both}.sk-spinner-v7-dot:nth-child(1){animation-delay:-1.1s}.sk-spinner-v7-dot:nth-child(1):before{animation-delay:-1.1s}.sk-spinner-v7-dot:nth-child(2){animation-delay:-1s}.sk-spinner-v7-dot:nth-child(2):before{animation-delay:-1s}.sk-spinner-v7-dot:nth-child(3){animation-delay:-0.9s}.sk-spinner-v7-dot:nth-child(3):before{animation-delay:-0.9s}.sk-spinner-v7-dot:nth-child(4){animation-delay:-0.8s}.sk-spinner-v7-dot:nth-child(4):before{animation-delay:-0.8s}.sk-spinner-v7-dot:nth-child(5){animation-delay:-0.7s}.sk-spinner-v7-dot:nth-child(5):before{animation-delay:-0.7s}.sk-spinner-v7-dot:nth-child(6){animation-delay:-0.6s}.sk-spinner-v7-dot:nth-child(6):before{animation-delay:-0.6s}.spinner-v8{width:8em;height:8em;background-color:rgb(var(--lf-color-on-spinner));animation:sk-spinner-v8 1.2s infinite ease-in-out;transform:perspective(120px) rotateX(0deg) rotateY(0deg)}.spinner-v9{width:8em;height:8em;position:relative}.sk-spinner-v9-bounce1,.sk-spinner-v9-bounce2{width:100%;height:100%;background-color:rgb(var(--lf-color-on-spinner));border-radius:50%;opacity:0.6;position:absolute;top:0;left:0;animation:sk-spinner-v9 2s infinite ease-in-out}.sk-spinner-v9-bounce2{animation-delay:-1s}.spinner-v10{width:8em;height:8em;position:relative}.sk-spinner-v10-cube1,.sk-spinner-v10-cube2{backface-visibility:hidden;background-color:rgb(var(--lf-color-on-spinner));width:2em;height:2em;position:absolute;top:0;left:0;animation:sk-spinner-v10 1.8s infinite ease-in-out}.sk-spinner-v10-cube2{animation-delay:-0.9s}.spinner-v11{width:8em;height:8em;background-color:rgb(var(--lf-color-on-spinner));border-radius:100%;animation:sk-spinner-v11 1s infinite ease-in-out}.spinner-v12{width:8em;height:8em;position:relative;text-align:center;animation:sk-spinner-v12 2s infinite linear}.sk-spinner-v12-dot1,.sk-spinner-v12-dot2{width:60%;height:60%;display:inline-block;position:absolute;background-color:rgb(var(--lf-color-on-spinner));border-radius:100%;animation:sk-spinner-v12-1 2s infinite ease-in-out}.sk-spinner-v12-dot2{bottom:0 !important;animation-delay:-1s}.spinner-v13{width:7em;height:7em}.spinner-v13 .sk-spinner-v13-cube{backface-visibility:hidden;background-color:rgb(var(--lf-color-on-spinner));float:left;width:33%;height:33%;position:relative !important;animation:sk-spinner-v13 1.3s infinite ease-in-out;outline:1px solid transparent}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube1{animation-delay:0.2s}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube2{animation-delay:0.3s}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube3{animation-delay:0.4s}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube4{animation-delay:0.1s}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube5{animation-delay:0.2s}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube6{animation-delay:0.3s}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube7{animation-delay:0s}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube8{animation-delay:0.1s}.spinner-v13 .sk-spinner-v13-cube.sk-spinner-v13-cube9{animation-delay:0.2s}.spinner-v14{width:8em;height:8em;position:relative}.spinner-v14 .sk-spinner-v14-circle{width:100%;height:100%;position:absolute;left:0;top:0}.spinner-v14 .sk-spinner-v14-circle:before{content:"";display:block;margin:0 auto;width:15%;height:15%;background-color:rgb(var(--lf-color-on-spinner));border-radius:100%;animation:sk-spinner-v14-circleFadeDelay 1.2s infinite ease-in-out both}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle2{transform:rotate(30deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle2:before{animation-delay:-1.1s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle3{transform:rotate(60deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle3:before{animation-delay:-1s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle4{transform:rotate(90deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle4:before{animation-delay:-0.9s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle5{transform:rotate(120deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle5:before{animation-delay:-0.8s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle6{transform:rotate(150deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle6:before{animation-delay:-0.7s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle7{transform:rotate(180deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle7:before{animation-delay:-0.6s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle8{transform:rotate(210deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle8:before{animation-delay:-0.5s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle9{transform:rotate(240deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle9:before{animation-delay:-0.4s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle10{transform:rotate(270deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle10:before{animation-delay:-0.3s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle11{transform:rotate(300deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle11:before{animation-delay:-0.2s}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle12{transform:rotate(330deg)}.spinner-v14 .sk-spinner-v14-circle.sk-spinner-v14-circle12:before{animation-delay:-0.1s}@keyframes sk-spinner-v1{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}@keyframes sk-spinner-v2{0%,80%,100%{box-shadow:0 2.5em 0 -1.3em}40%{box-shadow:0 2.5em 0 0}}@keyframes sk-spinner-v3{0%{box-shadow:0 -0.83em 0 -0.4em, 0 -0.83em 0 -0.42em, 0 -0.83em 0 -0.44em, 0 -0.83em 0 -0.46em, 0 -0.83em 0 -0.477em}5%,95%{box-shadow:0 -0.83em 0 -0.4em, 0 -0.83em 0 -0.42em, 0 -0.83em 0 -0.44em, 0 -0.83em 0 -0.46em, 0 -0.83em 0 -0.477em}10%,59%{box-shadow:0 -0.83em 0 -0.4em, -0.087em -0.825em 0 -0.42em, -0.173em -0.812em 0 -0.44em, -0.256em -0.789em 0 -0.46em, -0.297em -0.775em 0 -0.477em}20%{box-shadow:0 -0.83em 0 -0.4em, -0.338em -0.758em 0 -0.42em, -0.555em -0.617em 0 -0.44em, -0.671em -0.488em 0 -0.46em, -0.749em -0.34em 0 -0.477em}38%{box-shadow:0 -0.83em 0 -0.4em, -0.377em -0.74em 0 -0.42em, -0.645em -0.522em 0 -0.44em, -0.775em -0.297em 0 -0.46em, -0.82em -0.09em 0 -0.477em}100%{box-shadow:0 -0.83em 0 -0.4em, 0 -0.83em 0 -0.42em, 0 -0.83em 0 -0.44em, 0 -0.83em 0 -0.46em, 0 -0.83em 0 -0.477em}}@keyframes sk-spinner-v3-1{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}@keyframes sk-spinner-v4{0%,100%{box-shadow:0 -3em 0 0.2em, 2em -2em 0 0em, 3em 0 0 -1em, 2em 2em 0 -1em, 0 3em 0 -1em, -2em 2em 0 -1em, -3em 0 0 -1em, -2em -2em 0 0}12.5%{box-shadow:0 -3em 0 0, 2em -2em 0 0.2em, 3em 0 0 0, 2em 2em 0 -1em, 0 3em 0 -1em, -2em 2em 0 -1em, -3em 0 0 -1em, -2em -2em 0 -1em}25%{box-shadow:0 -3em 0 -0.5em, 2em -2em 0 0, 3em 0 0 0.2em, 2em 2em 0 0, 0 3em 0 -1em, -2em 2em 0 -1em, -3em 0 0 -1em, -2em -2em 0 -1em}37.5%{box-shadow:0 -3em 0 -1em, 2em -2em 0 -1em, 3em 0em 0 0, 2em 2em 0 0.2em, 0 3em 0 0em, -2em 2em 0 -1em, -3em 0em 0 -1em, -2em -2em 0 -1em}50%{box-shadow:0 -3em 0 -1em, 2em -2em 0 -1em, 3em 0 0 -1em, 2em 2em 0 0em, 0 3em 0 0.2em, -2em 2em 0 0, -3em 0em 0 -1em, -2em -2em 0 -1em}62.5%{box-shadow:0 -3em 0 -1em, 2em -2em 0 -1em, 3em 0 0 -1em, 2em 2em 0 -1em, 0 3em 0 0, -2em 2em 0 0.2em, -3em 0 0 0, -2em -2em 0 -1em}75%{box-shadow:0em -3em 0 -1em, 2em -2em 0 -1em, 3em 0em 0 -1em, 2em 2em 0 -1em, 0 3em 0 -1em, -2em 2em 0 0, -3em 0em 0 0.2em, -2em -2em 0 0}87.5%{box-shadow:0em -3em 0 0, 2em -2em 0 -1em, 3em 0 0 -1em, 2em 2em 0 -1em, 0 3em 0 -1em, -2em 2em 0 0, -3em 0em 0 0, -2em -2em 0 0.2em}}@keyframes sk-spinner-v5{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}@keyframes sk-spinner-v6{0%,80%,100%{box-shadow:0 0;height:4em}40%{box-shadow:0 -2em;height:5em}}@keyframes sk-spinner-v7{100%{transform:rotate(360deg)}}@keyframes sk-spinner-v7-dot{80%,100%{transform:rotate(360deg)}}@keyframes sk-spinner-v7-dot-before{0%,100%{transform:scale(1)}50%{transform:scale(0.4)}}@keyframes sk-spinner-v8{0%{transform:perspective(120px) rotateX(0deg) rotateY(0deg)}50%{transform:perspective(120px) rotateX(-180.1deg) rotateY(0deg)}100%{transform:perspective(120px) rotateX(-180deg) rotateY(-179.9deg)}}@keyframes sk-spinner-v9{0%,100%{transform:scale(0)}50%{transform:scale(1)}}@keyframes sk-spinner-v10{25%{transform:translateX(5em) rotate(-90deg) scale(0.5)}50%{transform:translateX(5em) translateY(5em) rotate(-179deg)}50.1%{transform:translateX(5em) translateY(5em) rotate(-180deg)}75%{transform:translateX(0) translateY(5em) rotate(-270deg) scale(0.5)}100%{transform:rotate(-360deg)}}@keyframes sk-spinner-v11{0%{transform:scale(0)}100%{transform:scale(1);opacity:0}}@keyframes sk-spinner-v12{100%{transform:rotate(360deg)}}@keyframes sk-spinner-v12-1{0%,100%{transform:scale(0)}50%{transform:scale(1)}}@keyframes sk-spinner-v13{0%,70%,100%{transform:scale3D(1, 1, 1)}35%{transform:scale3D(0, 0, 1)}}@keyframes sk-spinner-v14-circleFadeDelay{0%,39%,100%{opacity:0}40%{opacity:1}}';
export {
  j as lf_list,
  V as lf_spinner
};
