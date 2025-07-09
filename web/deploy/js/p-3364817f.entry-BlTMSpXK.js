import { n, H, w as LF_ARTICLE_BLOCKS, C as CY_ATTRIBUTES, x as LF_ARTICLE_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, y as LF_ARTICLE_PROPS, f as de, N, U, F, j as ge } from "./index-B7yCDN23.js";
import { o } from "./p-BJbvgtBt-BB0MQEt4.js";
import { f } from "./p-B2nA4wTt-DSm22Q3m.js";
var g, u, b, p, y, z, w, k, x, C, E, W, j, S, T = function(t, e, i, a) {
  if ("a" === i && !a) throw new TypeError("Private accessor was defined without a getter");
  if ("function" == typeof e ? t !== e || !a : !e.has(t)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === i ? a : "a" === i ? a.call(t) : a ? a.value : e.get(t);
};
const D = class {
  constructor(i) {
    n(this, i), this.lfEvent = H(this, "lf-article-event"), g.add(this), this.lfDataset = null, this.lfEmpty = "Empty data.", this.lfStyle = "", this.lfUiSize = "medium", u.set(this, void 0), b.set(this, LF_ARTICLE_BLOCKS), p.set(this, CY_ATTRIBUTES), y.set(this, LF_ARTICLE_PARTS), z.set(this, LF_STYLE_ID), w.set(this, LF_WRAPPER_ID);
  }
  onLfEvent(t, e) {
    this.lfEvent.emit({ comp: this, eventType: e, id: this.rootElement.id, originalEvent: t });
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const t = LF_ARTICLE_PROPS.map((t2) => [t2, this[t2]]);
    return Object.fromEntries(t);
  }
  async refresh() {
    de(this);
  }
  async unmount(t = 0) {
    setTimeout(() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }, t);
  }
  connectedCallback() {
    T(this, u, "f") && T(this, u, "f").theme.register(this);
  }
  async componentWillLoad() {
    !function(t, e, i, a, r) {
      if ("function" == typeof e ? t !== e || true : !e.has(t)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
      e.set(t, i);
    }(this, u, await o(this));
  }
  componentDidLoad() {
    const { info: t } = T(this, u, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), t.update(this, "did-load");
  }
  componentWillRender() {
    const { info: t } = T(this, u, "f").debug;
    t.update(this, "will-render");
  }
  componentDidRender() {
    const { info: t } = T(this, u, "f").debug;
    t.update(this, "did-render");
  }
  render() {
    var _a;
    const { theme: t } = T(this, u, "f"), { bemClass: e, setLfStyle: i } = t, { lfDataset: l, lfEmpty: o2, lfStyle: n2 } = this, { emptyData: s } = T(this, b, "f");
    return N(U, { key: "facc45a56c7f608d4ea63431396e1a044bf952cc" }, n2 && N("style", { key: "32ff6a90169431aa5dba003da5e168715cbeb1f5", id: T(this, z, "f") }, i(this)), N("div", { key: "c5549c09dd1786060182280c0586fee4d7c45985", id: T(this, w, "f") }, ((_a = l == null ? void 0 : l.nodes) == null ? void 0 : _a.length) ? T(this, g, "m", x).call(this) : N("div", { class: e(s._), part: T(this, y, "f").emptyData }, N("div", { class: e(s._, s.text) }, o2))));
  }
  disconnectedCallback() {
    var _a;
    (_a = T(this, u, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return F(this);
  }
};
u = /* @__PURE__ */ new WeakMap(), b = /* @__PURE__ */ new WeakMap(), p = /* @__PURE__ */ new WeakMap(), y = /* @__PURE__ */ new WeakMap(), z = /* @__PURE__ */ new WeakMap(), w = /* @__PURE__ */ new WeakMap(), g = /* @__PURE__ */ new WeakSet(), k = function(t, e) {
  var _a;
  switch (e) {
    case 0:
      return T(this, g, "m", C).call(this, t, e);
    case 1:
      return T(this, g, "m", E).call(this, t, e);
    case 2:
      return T(this, g, "m", j).call(this, t, e);
    default:
      return ((_a = t.children) == null ? void 0 : _a.length) ? T(this, g, "m", W).call(this, t, e) : T(this, g, "m", S).call(this, t, e);
  }
}, x = function() {
  const t = [], { nodes: e } = this.lfDataset;
  for (let i = 0; i < e.length; i++) {
    const a = e[i];
    t.push(T(this, g, "m", k).call(this, a, 0));
  }
  return N(ge, null, t);
}, C = function(t, e) {
  const { bemClass: i } = T(this, u, "f").theme, { children: r, cssStyle: l, value: n2 } = t;
  return N(ge, null, N("article", { class: i(T(this, b, "f").article._), "data-cy": T(this, p, "f").node, "data-depth": e.toString(), part: T(this, y, "f").article, style: l }, n2 && N("h1", null, n2), r && t.children.map((t2) => T(this, g, "m", k).call(this, t2, e + 1))));
}, E = function(t, e) {
  const { bemClass: i } = T(this, u, "f").theme, { children: r, cssStyle: l, value: n2 } = t;
  return N(ge, null, N("section", { class: i(T(this, b, "f").section._), "data-cy": T(this, p, "f").node, "data-depth": e.toString(), part: T(this, y, "f").section, style: l }, n2 && N("h2", null, n2), r && r.map((t2) => T(this, g, "m", k).call(this, t2, e + 1))));
}, W = function(t, e) {
  const { bemClass: i } = T(this, u, "f").theme, { children: r, cssStyle: l, tagName: n2, value: s } = t, f2 = (r == null ? void 0 : r.some((t2) => "li" === t2.tagName)) ? "ul" : n2 || "div";
  return N(ge, null, s && N("div", null, s), N(f2, { class: i(T(this, b, "f").content._), "data-cy": T(this, p, "f").node, "data-depth": e.toString(), part: T(this, y, "f").content, style: l }, r && r.map((t2) => T(this, g, "m", k).call(this, t2, e + 1))));
}, j = function(t, e) {
  const { bemClass: i } = T(this, u, "f").theme, { children: r, cssStyle: l, value: n2 } = t;
  return N(ge, null, N("p", { class: i(T(this, b, "f").paragraph._), "data-cy": T(this, p, "f").node, "data-depth": e.toString(), part: T(this, y, "f").paragraph, style: l }, n2 && N("h3", null, n2), r && r.map((t2) => T(this, g, "m", k).call(this, t2, e + 1))));
}, S = function(t, e) {
  const { theme: i } = T(this, u, "f"), { cells: r, cssStyle: l, tagName: o2, value: n2 } = t, s = r && Object.keys(r)[0], f$1 = r == null ? void 0 : r[s], { content: c } = T(this, b, "f");
  if (f$1) return N(f, { cell: f$1, index: 0, shape: f$1.shape, eventDispatcher: async (t2) => this.onLfEvent(t2, "lf-event"), framework: T(this, u, "f") });
  {
    const t2 = o2 || "span";
    return N(t2, { class: i.bemClass(c._, c.body, { [t2]: Boolean(t2) }), "data-depth": e.toString(), part: T(this, y, "f").content, style: l }, n2);
  }
}, D.style = "::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}:host{display:block;font-family:var(--lf-article-font-family, var(--lf-font-family-primary));font-size:var(--lf-article-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(\n        var(--lf-article-font-size, var(--lf-font-size)) * var(--lf-ui-size-large)\n      )}:host([lf-ui-size=medium]){font-size:calc(\n        var(--lf-article-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium)\n      )}:host([lf-ui-size=small]){font-size:calc(\n        var(--lf-article-font-size, var(--lf-font-size)) * var(--lf-ui-size-small)\n      )}:host([lf-ui-size=xlarge]){font-size:calc(\n        var(--lf-article-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge)\n      )}:host([lf-ui-size=xsmall]){font-size:calc(\n        var(--lf-article-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall)\n      )}:host([lf-ui-size=xxlarge]){font-size:calc(\n        var(--lf-article-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge)\n      )}:host([lf-ui-size=xxsmall]){font-size:calc(\n        var(--lf-article-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall)\n      )}#lf-component{width:100%;height:100%}:host{border:0;border-style:solid;border-radius:var(--lf-article-border-radius, var(--lf-ui-border-radius));color:rgb(var(--lf-article-color-on-bg, var(--lf-color-on-bg)))}.article{background-color:rgba(var(--lf-article-color-bg, var(--lf-color-bg)), 0.375);color:rgb(var(--lf-article-color-on-bg, var(--lf-color-on-bg)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);margin:var(--lf-article-margin, auto);max-width:var(--lf-article-max-width, 1200px);padding:var(--lf-article-padding, 2.5em)}.content__body{font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:1em;font-family:var(--lf-article-font-family-body, var(--lf-font-family-primary));font-size:var(--lf-article-font-size-body, var(--lf-font-size))}.empty-data{width:100%;height:100%;align-items:center;display:flex;justify-content:center}[data-component=LfCode]{max-width:max-content;margin:auto;padding:1.75em 0}h1{font-size:2em;font-weight:600;line-height:1.2em;letter-spacing:0em;margin-bottom:0.5em;color:rgb(var(--lf-article-color-h1, var(--lf-color-on-bg)));font-family:var(--lf-article-font-family-h1, var(--lf-font-family-primary));font-size:var(--lf-article-font-size-h1, 2em);margin-top:0;margin-bottom:1em;word-break:break-word}h2{font-size:1.75em;font-weight:500;line-height:1.3em;letter-spacing:0em;margin-bottom:0.5em;color:rgb(var(--lf-article-color-h2, var(--lf-color-on-bg)));font-family:var(--lf-article-font-family-h2, var(--lf-font-family-primary));font-size:var(--lf-article-font-size-h2, 1.75em);margin:1.5em 0 0.5em}h3{font-size:1.5em;font-weight:500;line-height:1.4em;letter-spacing:0em;margin-bottom:0.5em;color:rgb(var(--lf-article-color-h3, var(--lf-color-on-bg)));font-family:var(--lf-article-font-family-h3, var(--lf-font-family-primary));font-size:var(--lf-article-font-size-h3, 1.5em);margin:1em 0 0.5em}h4{font-size:1.25em;font-weight:500;line-height:1.5em;letter-spacing:0em;margin-bottom:0.5em;color:rgb(var(--lf-article-color-h4, var(--lf-color-on-bg)));font-family:var(--lf-article-font-family-h4, var(--lf-font-family-primary));font-size:var(--lf-article-font-size-h4, 1.25em);margin:1em 0 0.5em}h5{font-size:1.125em;font-weight:500;line-height:1.6em;letter-spacing:0em;margin-bottom:0.5em;color:rgb(var(--lf-article-color-h5, var(--lf-color-on-bg)));font-family:var(--lf-article-font-family-h5, var(--lf-font-family-primary));font-size:var(--lf-article-font-size-h5, 1.125em);margin:1em 0 0.5em}h6{font-size:1em;font-weight:500;line-height:1.5em;letter-spacing:0em;margin-bottom:0.5em;color:rgb(var(--lf-article-color-h6, var(--lf-color-on-bg)));font-family:var(--lf-article-font-family-h6, var(--lf-font-family-primary));font-size:var(--lf-article-font-size-h6, 1em);margin:1em 0 0.5em}ul,ol{font-size:1em;font-weight:400;line-height:1.6em;letter-spacing:0em;margin-bottom:0.5em;margin-left:1.5em;margin:1em 0;padding-inline-start:var(--lf-article-padding-ul, 1.25em)}";
export {
  D as lf_article
};
