import { n, H, bh as LF_SLIDER_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, bi as LF_SLIDER_PARTS, c as LF_STYLE_ID, bj as LF_SLIDER_CSS_VARIABLES, d as LF_WRAPPER_ID, bk as LF_SLIDER_PROPS, f as de, N, U, F } from "./index-B7yCDN23.js";
import { o } from "./p-BJbvgtBt-BB0MQEt4.js";
var u, m, v, g, y, w, k, z, x, _, M, W = function(r, e, i, l) {
  if ("function" == typeof e ? r !== e || true : !e.has(r)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return e.get(r);
}, E = function(r, e, i, l, a) {
  if ("function" == typeof e ? r !== e || true : !e.has(r)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return e.set(r, i), i;
};
const C = class {
  constructor(i) {
    n(this, i), this.lfEvent = H(this, "lf-slider-event"), this.value = { display: 0, real: 0 }, this.lfLabel = "", this.lfLeadingLabel = false, this.lfMax = 100, this.lfMin = 0, this.lfStep = 1, this.lfRipple = true, this.lfStyle = "", this.lfUiSize = "medium", this.lfUiState = "primary", this.lfValue = 50, u.set(this, void 0), m.set(this, LF_SLIDER_BLOCKS), v.set(this, CY_ATTRIBUTES), g.set(this, LF_ATTRIBUTES), y.set(this, LF_SLIDER_PARTS), w.set(this, LF_STYLE_ID), k.set(this, LF_SLIDER_CSS_VARIABLES), z.set(this, LF_WRAPPER_ID), x.set(this, void 0), _.set(this, void 0), M.set(this, () => "disabled" === this.lfUiState);
  }
  onLfEvent(r, e) {
    const { effects: i } = W(this, u);
    switch (e) {
      case "change":
        this.setValue(+W(this, x).value), this.refresh();
        break;
      case "input":
        this.value.display = +W(this, x).value, this.refresh();
        break;
      case "pointerdown":
        this.lfRipple && i.ripple(r, W(this, _));
    }
    this.lfEvent.emit({ comp: this, eventType: e, id: this.rootElement.id, originalEvent: r, value: this.value });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const r = LF_SLIDER_PROPS.map((r2) => [r2, this[r2]]);
    return Object.fromEntries(r);
  }
  async getValue() {
    return this.value;
  }
  async refresh() {
    de(this);
  }
  async setValue(r) {
    this.value = { display: r, real: r };
  }
  async unmount(r = 0) {
    setTimeout(() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, r);
  }
  connectedCallback() {
    W(this, u) && W(this, u).theme.register(this);
  }
  async componentWillLoad() {
    E(this, u, await o(this));
    const { lfValue: r } = this;
    r && this.setValue(r);
  }
  componentDidLoad() {
    const { debug: r } = W(this, u);
    this.onLfEvent(new CustomEvent("ready"), "ready"), r.info.update(this, "did-load");
  }
  componentWillRender() {
    const { info: r } = W(this, u).debug;
    r.update(this, "will-render");
  }
  componentDidRender() {
    const { info: r } = W(this, u).debug;
    r.update(this, "did-render");
  }
  render() {
    const { bemClass: r, setLfStyle: e } = W(this, u).theme, { formField: i, slider: t } = W(this, m), { lfLabel: o2, lfLeadingLabel: s, lfMax: n2, lfMin: f, lfRipple: d, lfStep: c, lfStyle: h, value: p } = this;
    return N(U, { key: "69128664c0532f37c163673a3b42ae9e8af535d3" }, N("style", { key: "fb7510630ef43ceb178de61f1e91abe8129f4f9c", id: W(this, w) }, `
            :host {
              ${W(this, k).value}: ${(p.display - f) / (n2 - f) * 100}%;
            }
          ${h && e(this) || ""}`), N("div", { key: "97eb886f237d4b93845d306a5fd34da0e9a415bf", id: W(this, z) }, N("div", { key: "a448369c92e62f196980370cc24ef2917e09e198", class: r(i._, null, { leading: s }), part: W(this, y).formField }, N("div", { key: "7bd48df7f38a22faa63642518c28c4efdee2835a", class: r(t._, null, { "has-value": p.display > f, disabled: W(this, M).call(this) }), "data-lf": W(this, g)[this.lfUiState], part: W(this, y).slider }, N("input", { key: "830f9a146ba4595e33c938e294956ca4a4d5d723", type: "range", class: r(t._, t.nativeControl), "data-cy": W(this, v).input, disabled: W(this, M).call(this), max: n2, min: f, onBlur: (r2) => {
      this.onLfEvent(r2, "blur");
    }, onChange: (r2) => {
      this.onLfEvent(r2, "change");
    }, onFocus: (r2) => {
      this.onLfEvent(r2, "focus");
    }, onInput: (r2) => {
      this.onLfEvent(r2, "input");
    }, onPointerDown: (r2) => {
      this.onLfEvent(r2, "pointerdown");
    }, part: W(this, y).nativeControl, ref: (r2) => {
      r2 && E(this, x, r2);
    }, step: c, value: p.real }), N("div", { key: "dd5bdcc53525a30b084cdb614b41d31727de2863", class: r(t._, t.track) }, N("div", { key: "24219f112409f7e005fafa706d2079671772e97e", class: r(t._, t.thumbUnderlay) }, N("div", { key: "c10fe89510425e42af1137151d1a3af95d4a3be8", class: r(t._, t.thumb), "data-cy": W(this, v).rippleSurface, "data-lf": W(this, g).rippleSurface, part: W(this, y).thumb, ref: (r2) => {
      d && E(this, _, r2);
    } }))), N("span", { key: "b4ae6071370af64ea2d77e2131d80ed9dff336ef", class: r(t._, t.value), part: W(this, y).value }, p.display)), N("label", { key: "a1330dc860c441533ea2b231121896bcf4d4a5b2", class: r(i._, i.label), part: W(this, y).label }, o2))));
  }
  disconnectedCallback() {
    var _a;
    (_a = W(this, u)) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return F(this);
  }
};
u = /* @__PURE__ */ new WeakMap(), m = /* @__PURE__ */ new WeakMap(), v = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), C.style = '::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=ripple]{animation-duration:var(--lf-ui-duration-ripple, 675ms);animation-fill-mode:forwards;animation-name:lf-ripple;animation-timing-function:var(--lf-ui-timing-ripple, ease-out);background:var(--lf-ui-ripple-background, var(--lf-color-primary));border-radius:var(--lf-ui-radius-ripple, 50%);height:var(--lf-ui-ripple-height, 100%);left:var(--lf-ui-ripple-x, 50%);opacity:var(--lf-ui-opacity-ripple, 0.5);pointer-events:none;position:absolute;top:var(--lf-ui-ripple-y, 50%);transform:scale(0);width:var(--lf-ui-ripple-width, 100%)}@keyframes lf-ripple{from{transform:scale(0)}to{opacity:0;transform:scale(4)}}[data-lf=ripple-surface]{cursor:pointer;height:100%;left:0;overflow:hidden;position:absolute;top:0;width:100%}[data-lf=danger]{--lf-slider-color-primary:var(\n    --lf-slider-color-danger,\n    var(--lf-color-danger)\n  );--lf-slider-color-on-primary:var(\n    --lf-slider-color-danger,\n    var(--lf-color-on-danger)\n  )}[data-lf=disabled]{opacity:var(--lf-slider-ui-opacity-disabled, var(--lf-ui-opacity-disabled));pointer-events:none}[data-lf=info]{--lf-slider-color-primary:var(\n    --lf-slider-color-info,\n    var(--lf-color-info)\n  );--lf-slider-color-on-primary:var(\n    --lf-slider-color-info,\n    var(--lf-color-on-info)\n  )}[data-lf=secondary]{--lf-slider-color-primary:var(\n    --lf-slider-color-secondary,\n    var(--lf-color-secondary)\n  );--lf-slider-color-on-primary:var(\n    --lf-slider-color-secondary,\n    var(--lf-color-on-secondary)\n  )}[data-lf=success]{--lf-slider-color-primary:var(\n    --lf-slider-color-success,\n    var(--lf-color-success)\n  );--lf-slider-color-on-primary:var(\n    --lf-slider-color-success,\n    var(--lf-color-on-success)\n  )}[data-lf=warning]{--lf-slider-color-primary:var(\n    --lf-slider-color-warning,\n    var(--lf-color-warning)\n  );--lf-slider-color-on-primary:var(\n    --lf-slider-color-warning,\n    var(--lf-color-on-warning)\n  )}:host{display:block;font-family:var(--lf-slider-font-family, var(--lf-font-family-primary));font-size:var(--lf-slider-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-slider-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-slider-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-slider-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-slider-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-slider-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-slider-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-slider-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{width:100%;height:100%}.form-field{color:rgb(var(--lf-slider-color-on-bg, var(--lf-color-on-bg)));width:100%;height:100%;font-size:0.875em;font-weight:500;line-height:1.5em;letter-spacing:0.01em;align-items:center;box-sizing:border-box;display:inline-flex;padding:var(--lf-slider-padding, 2em 0.5em);vertical-align:middle}.form-field__label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:var(--lf-slider-label-min-width, max-content);padding-left:var(--lf-slider-label-padding-left, 1.5em)}.form-field--leading .form-field__label{margin-left:auto;margin-right:0;order:-1;padding-left:0;padding-right:var(--lf-slider-label-padding-right, 1.5em)}.slider{display:block;position:relative;outline:none;margin:var(--lf-slider-margin, 0 0.75em);min-width:var(--lf-slider-min-width, 7em);user-select:none;width:100%}.slider--has-value .slider__track:after{border:0;border-style:solid;border-radius:var(--lf-slider-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-slider-color-primary, var(--lf-color-primary)), 0.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);transition:all 300ms cubic-bezier(0.5, 1.7, 0.2, 1);position:absolute;content:"";height:100%;left:0;top:0;width:var(--lf_slider_value)}.slider__label{cursor:pointer;margin-left:0;margin-right:auto;padding-left:var(--lf-slider-label-padding-left, 0.5em);padding-right:0;user-select:none}.slider__value{color:rgb(var(--lf-slider-color-on-bg, var(--lf-color-on-bg)));font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;bottom:var(--lf-slider-value-bottom-position, -3em);left:50%;position:absolute;transform:translateX(-50%);white-space:nowrap}.slider__track{border:0;border-style:solid;border-radius:var(--lf-slider-border-radius, var(--lf-ui-border-radius));background-color:rgba(var(--lf-slider-color-primary, var(--lf-color-primary)), 0.25);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);transition:all 300ms cubic-bezier(0.5, 1.7, 0.2, 1);box-shadow:var(--lf-slider-box-shadow, 0 0.25em 0.5em rgba(var(--lf-comp-color-on-bg, var(--lf-color-on-bg)), 0.2));box-sizing:border-box;height:var(--lf-slider-track-height, 0.5em);width:100%}.slider__thumb-underlay{transition:all 300ms cubic-bezier(0.5, 1.7, 0.2, 1);align-items:center;border-radius:50%;display:flex;height:var(--lf-slider-thumb-height, 1.25em);justify-content:center;left:var(--lf_slider_value);pointer-events:none;position:absolute;top:var(--lf-slider-thumb-underlay-top, -0.6em);transform:translateX(-50%);width:var(--lf-slider-thumb-width, 1.25em)}.slider__thumb{background-color:rgba(var(--lf-slider-color-primary, var(--lf-color-primary)), 0.6);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);transition:all 300ms cubic-bezier(0.5, 1.7, 0.2, 1);border-radius:50%;box-shadow:var(--lf-slider-thumb-box-shadow, 0 0.25em 0.5em rgba(var(--lf-comp-color-on-bg, var(--lf-color-on-bg)), 0.2));cursor:pointer;height:var(--lf-slider-thumb-height, 1.5em);width:var(--lf-slider-thumb-width, 1.5em)}.slider__thumb:hover{background-color:rgba(var(--lf-slider-color-primary, var(--lf-color-primary)), 0.8);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);transform:scale(var(--lf-slider-thumb-hover-scale, 1.1))}.slider__native-control{cursor:pointer;height:var(--lf-slider-input-height, 3em);left:0;opacity:0;position:absolute;top:calc(var(--lf-slider-input-height, 3em) / -2);width:100%;z-index:2}';
export {
  C as lf_slider
};
