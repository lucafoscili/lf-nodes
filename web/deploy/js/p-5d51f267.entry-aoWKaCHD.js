import { n, V, Q as LF_CAROUSEL_BLOCKS, C as CY_ATTRIBUTES, f as LF_ATTRIBUTES, R as LF_CAROUSEL_PARTS, b as LF_STYLE_ID, c as LF_WRAPPER_ID, U as LF_CAROUSEL_PROPS, p as pt, D as D$1, W as W$1, z as z$1, k as jt, X as LF_CAROUSEL_IDS } from "./index-slE0ws_4.js";
import { a } from "./p-Dl9cVpAY-C1XL_Hwc.js";
import { r } from "./p-CKijk88y-DUiS1pYX.js";
const m = { start: (t) => {
  const { controller: e } = t, { get: s, set: i } = e, { compInstance: r2 } = s, { lfAutoPlay: a2, lfInterval: o } = r2;
  a2 && o > 0 && i.interval(setInterval((() => {
    i.index.next();
  }), o));
}, stop: (t) => {
  const { controller: e } = t, { get: s, set: i } = e, { interval: r2 } = s;
  r2() && (clearInterval(r2()), i.interval(null));
} }, g = (t, e) => {
  const { start: s, stop: i } = m;
  return { ...t, autoplay: { start: () => s(e()), stop: () => i(e()) } };
}, y = (e) => /* @__PURE__ */ ((e2) => ({ back: () => {
  const { controller: s, elements: i, handlers: r2 } = e2(), { blocks: a2, cyAttributes: o, manager: n2, parts: c } = s.get, { assignRef: f, theme: h } = n2, { refs: u } = i, { button: d } = r2, { "--lf-icon-previous": b } = h.get.current().variables;
  return D$1("lf-button", { class: h.bemClass(a2.carousel._, a2.carousel.back), "data-cy": o.button, id: LF_CAROUSEL_IDS.back, lfIcon: b, lfStyling: "icon", lfUiSize: "large", "onLf-button-event": d, part: c.back, ref: f(u, "back"), title: "Previous slide." });
}, forward: () => {
  const { controller: s, elements: i, handlers: r2 } = e2(), { blocks: a2, cyAttributes: o, manager: n2, parts: c } = s.get, { assignRef: f, theme: h } = n2, { refs: u } = i, { button: d } = r2, { "--lf-icon-next": b } = h.get.current().variables;
  return D$1("lf-button", { class: h.bemClass(a2.carousel._, a2.carousel.forward), "data-cy": o.button, id: LF_CAROUSEL_IDS.forward, lfIcon: b, lfStyling: "icon", lfUiSize: "large", "onLf-button-event": d, part: c.forward, ref: f(u, "forward"), title: "Next slide." });
} }))(e), w = (t) => /* @__PURE__ */ ((t2) => ({ button: (e) => {
  const { eventType: s, id: i } = e.detail, { next: r2, previous: a2 } = t2().controller.set.index;
  if ("click" === s) switch (i) {
    case LF_CAROUSEL_IDS.back:
      a2();
      break;
    case LF_CAROUSEL_IDS.forward:
      r2();
  }
} }))(t);
var k, z, x, _, S, E, W, j, C, M, T, I, L, P, D, A, R, H = function(t, e, s, i) {
  if ("a" === s && !i) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof e ? t !== e || !i : !e.has(t)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === s ? i : "a" === s ? i.call(t) : i ? i.value : e.get(t);
}, B = function(t, e, s, i, r2) {
  if ("function" == typeof e ? t !== e || true : !e.has(t)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return e.set(t, s), s;
};
const O = class {
  constructor(t) {
    n(this, t), this.lfEvent = V(this, "lf-carousel-event"), k.add(this), this.currentIndex = 0, this.shapes = {}, this.lfDataset = null, this.lfAutoPlay = false, this.lfInterval = 3e3, this.lfLightbox = false, this.lfNavigation = false, this.lfShape = "image", this.lfStyle = "", z.set(this, void 0), x.set(this, LF_CAROUSEL_BLOCKS), _.set(this, CY_ATTRIBUTES), S.set(this, LF_ATTRIBUTES), E.set(this, LF_CAROUSEL_PARTS), W.set(this, LF_STYLE_ID), j.set(this, LF_WRAPPER_ID), C.set(this, void 0), M.set(this, void 0), T.set(this, void 0), I.set(this, (() => {
      var t2;
      B(this, T, { controller: { get: { blocks: H(this, x, "f"), compInstance: this, cyAttributes: CY_ATTRIBUTES, index: { current: () => this.currentIndex }, interval: () => H(this, M, "f"), manager: H(this, z, "f"), parts: LF_CAROUSEL_PARTS, totalSlides: () => H(this, k, "m", L).call(this) }, set: g({ index: { current: (t3) => this.currentIndex = t3, next: () => {
        var t3, e;
        this.currentIndex = (t3 = this.currentIndex, e = H(this, k, "m", L).call(this), (t3 + 1) % e);
      }, previous: () => {
        var t3, e;
        this.currentIndex = (t3 = this.currentIndex, e = H(this, k, "m", L).call(this), (t3 - 1 + e) % e);
      } }, interval: (t3) => B(this, M, t3, "f") }, t2 = () => H(this, T, "f")) }, elements: { jsx: y(t2), refs: { back: null, forward: null } }, handlers: w(t2) });
    }));
  }
  onLfEvent(t, e) {
    const { lightbox: s } = H(this, z, "f").effects;
    if ("lf-event" === e && this.lfLightbox) {
      const { comp: e2, eventType: i } = t.detail;
      if ("click" === i) {
        const { rootElement: t2 } = e2;
        t2 instanceof HTMLElement && s.show(t2);
      }
    }
    this.lfEvent.emit({ comp: this, eventType: e, id: this.rootElement.id, originalEvent: t });
  }
  async updateShapes() {
    if (!H(this, z, "f")) return;
    const { data: t, debug: e } = H(this, z, "f");
    try {
      this.shapes = t.cell.shapes.getAll(this.lfDataset);
    } catch (t2) {
      e.logs.new(this, "Error updating shapes: " + t2, "error");
    }
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const t = LF_CAROUSEL_PROPS.map(((t2) => [t2, this[t2]]));
    return Object.fromEntries(t);
  }
  async goToSlide(t) {
    const { current: e } = H(this, T, "f").controller.set.index;
    e(t);
  }
  async nextSlide() {
    const { next: t } = H(this, T, "f").controller.set.index;
    t();
  }
  async prevSlide() {
    const { previous: t } = H(this, T, "f").controller.set.index;
    t();
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
    H(this, z, "f") && H(this, z, "f").theme.register(this);
  }
  async componentWillLoad() {
    B(this, z, await a(this)), H(this, I, "f").call(this), this.updateShapes(), this.lfAutoPlay && m.start(H(this, T, "f"));
  }
  componentDidLoad() {
    const { info: t } = H(this, z, "f").debug, { register: e } = H(this, z, "f").drag, { next: s, previous: i } = H(this, T, "f").controller.set.index;
    e.swipe(H(this, C, "f"), { onEnd: (t2, e2) => {
      var _a;
      if ((_a = e2.swipeData) == null ? void 0 : _a.direction) {
        const { direction: t3 } = e2.swipeData;
        "left" === t3 ? s() : "right" === t3 && i();
      }
    } }), this.onLfEvent(new CustomEvent("ready"), "ready"), t.update(this, "did-load");
  }
  componentWillRender() {
    const { info: t } = H(this, z, "f").debug;
    t.update(this, "will-render");
  }
  componentDidRender() {
    const { info: t } = H(this, z, "f").debug;
    t.update(this, "did-render");
  }
  render() {
    const { bemClass: e, setLfStyle: s } = H(this, z, "f").theme, { lfStyle: i } = this, { carousel: a2 } = H(this, x, "f");
    return D$1(W$1, { key: "80540b7fb5566ef47c904a27811e0f15de3b4f3e" }, i && D$1("style", { key: "07913ca7e055a83fde61905b79e923092bdb3f9e", id: H(this, W, "f") }, s(this)), D$1("div", { key: "901aef70c78f967fe0e8925f21146e3ff7453a69", id: H(this, j, "f") }, D$1("div", { key: "2ab6f3383322d90fcd4b4fb0cfe68999d24f3c87", class: e(a2._), part: H(this, E, "f").carousel, ref: (t) => {
      t && B(this, C, t);
    }, role: "region" }, H(this, k, "m", D).call(this))));
  }
  disconnectedCallback() {
    var _a, _b;
    (_a = H(this, z, "f")) == null ? void 0 : _a.drag.unregister.swipe(H(this, C, "f")), (_b = H(this, z, "f")) == null ? void 0 : _b.theme.unregister(this), m.stop(H(this, T, "f"));
  }
  get rootElement() {
    return z$1(this);
  }
  static get watchers() {
    return { lfDataset: ["updateShapes"], lfShape: ["updateShapes"] };
  }
};
z = /* @__PURE__ */ new WeakMap(), x = /* @__PURE__ */ new WeakMap(), _ = /* @__PURE__ */ new WeakMap(), S = /* @__PURE__ */ new WeakMap(), E = /* @__PURE__ */ new WeakMap(), W = /* @__PURE__ */ new WeakMap(), j = /* @__PURE__ */ new WeakMap(), C = /* @__PURE__ */ new WeakMap(), M = /* @__PURE__ */ new WeakMap(), T = /* @__PURE__ */ new WeakMap(), I = /* @__PURE__ */ new WeakMap(), k = /* @__PURE__ */ new WeakSet(), L = function() {
  var _a, _b;
  return ((_b = (_a = this.shapes) == null ? void 0 : _a[this.lfShape]) == null ? void 0 : _b.length) || 0;
}, P = function() {
  var _a;
  return !!((_a = this.shapes) == null ? void 0 : _a[this.lfShape]);
}, D = function() {
  const { bemClass: e } = H(this, z, "f").theme, { carousel: s } = H(this, x, "f"), { elements: i } = H(this, T, "f"), { jsx: r2 } = i, { back: a2, forward: l } = r2;
  if (H(this, k, "m", P).call(this)) {
    const i2 = this.shapes[this.lfShape];
    if (i2 == null ? void 0 : i2.length) return D$1(jt, null, D$1("div", { "aria-live": "polite", class: e(s._, s.track), part: H(this, E, "f").track, role: "region" }, H(this, k, "m", R).call(this), this.lfNavigation && a2(), this.lfNavigation && l()), H(this, k, "m", A).call(this));
  }
  return null;
}, A = function() {
  const { bemClass: e } = H(this, z, "f").theme, { slideBar: s } = H(this, x, "f"), i = H(this, k, "m", L).call(this), r2 = [];
  for (let a2 = 0; a2 < i; a2++) {
    const i2 = `Jump to slide ${a2 + 1}`;
    r2.push(D$1("div", { "aria-label": i2, class: e(s._, s.segment, { active: a2 === this.currentIndex }), "data-cy": H(this, _, "f").button, "data-index": a2, onClick: async () => this.goToSlide(a2), part: H(this, E, "f").segment, role: "button", tabIndex: 0, title: i2 }));
  }
  return D$1("div", { class: e(s._), part: H(this, E, "f").slideBar }, r2);
}, R = function() {
  const { bemClass: e } = H(this, z, "f").theme, { currentIndex: s, lfShape: i } = this, { carousel: r$1 } = H(this, x, "f"), a2 = this.shapes[i].map((() => ({ htmlProps: { dataset: { lf: H(this, S, "f").fadeIn } } }))), o = this.shapes[i][s], l = a2[s];
  return D$1("div", { class: e(r$1._, r$1.slide), "data-index": s }, D$1(r, { cell: Object.assign(l, o), index: s, shape: i, eventDispatcher: async (t) => this.onLfEvent(t, "lf-event"), framework: H(this, z, "f") }));
}, O.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-carousel-font-family, var(--lf-font-family-primary));font-size:var(--lf-carousel-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-carousel-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-carousel-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-carousel-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-carousel-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-carousel-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-carousel-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-carousel-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%;margin:auto;overflow:hidden;position:relative}:host([lf-lightbox]) [data-lf=fade-in]{cursor:pointer}.carousel{border:0;border-style:solid;border-radius:var(--lf-carousel-border-radius, var(--lf-ui-border-radius));width:100%;height:100%;display:flex;justify-content:center;overflow:hidden;position:relative}.carousel:hover .slide-bar{opacity:1}.carousel:hover .carousel__back,.carousel:hover .carousel__forward{opacity:1}.carousel:hover .carousel__back{left:0.5em}.carousel:hover .carousel__forward{right:0.5em}.carousel__back,.carousel__forward{transition:all 250ms cubic-bezier(0.34, 1.56, 0.64, 1);opacity:0;position:absolute;top:50%;transform:translateY(-50%)}.carousel__back{left:0}.carousel__forward{right:0}.carousel__track{width:100%;height:100%;transition:all 250ms cubic-bezier(0.34, 1.56, 0.64, 1);display:flex;will-change:transform}.carousel__slide{width:100%;height:100%;align-items:center;flex-shrink:0;justify-content:center}.slide-bar{background-color:rgba(var(--lf-carousel-color-surface, var(--lf-color-surface)), 0.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);align-items:center;bottom:0;box-sizing:border-box;display:flex;flex-wrap:nowrap;height:var(--lf-carousel-slide-bar-height, 0.75em);left:0;opacity:var(--lf-carousel-slide-bar-opacity, 0.75);position:absolute;width:100%}.slide-bar:hover{opacity:var(--lf-carousel-slide-bar-opacity-hover, 1)}.slide-bar__segment{background-color:rgba(var(--lf-carousel-color-surface, var(--lf-color-surface)), 1);width:100%;height:100%;transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);cursor:pointer}.slide-bar__segment:not(.slide-bar__segment--active):hover{background-color:rgba(var(--lf-carousel-color-on-surface, var(--lf-color-on-surface)), 0.5)}.slide-bar__segment--active{background-color:rgba(var(--lf-carousel-color-on-surface, var(--lf-color-on-surface)), 1)}";
export {
  O as lf_carousel
};
