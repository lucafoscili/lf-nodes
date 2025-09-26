import { n, I, a1 as IMAGE_TYPE_IDS, a2 as LF_MESSENGER_CLEAN_UI, a3 as LF_MESSENGER_BLOCKS, C as CY_ATTRIBUTES, a as LF_ATTRIBUTES, a4 as LF_MESSENGER_PARTS, c as LF_STYLE_ID, d as LF_WRAPPER_ID, W as W$1, k as kt, a5 as OPTION_TYPE_IDS, a6 as LF_MESSENGER_PROPS, m as mt, f as L$1, G as G$1, a7 as LF_MESSENGER_IDS, a8 as LF_MESSENGER_FILTER, a9 as LF_MESSENGER_NAV, aa as LF_MESSENGER_MENU, ab as TIMEFRAME_COVER, ac as STYLE_COVER, ad as OUTFIT_COVER, ae as LOCATION_COVER, af as AVATAR_COVER, ag as CHILD_ROOT_MAP } from "./index-DGym7ebr.js";
import { o } from "./p-DklcdYZv-D0qRoWIr.js";
const T = (e, t) => {
  const { currentCharacter: r } = e.controller.get.compInstance;
  return t ?? r;
}, L = (e, t) => {
  const { lfEndpointUrl: r, lfMaxTokens: s, lfPollingInterval: a, lfSystem: o2, lfTemperature: n2 } = t;
  e.lfEndpointUrl = r, e.lfMaxTokens = s, e.lfPollingInterval = a, e.lfSystem = o2, e.lfTemperature = n2;
}, E = (e) => {
  const { lfDataset: t } = e.controller.get.compInstance;
  return !!((t == null ? void 0 : t.nodes) || []).length;
}, M = (e) => {
  var _a;
  const { lfDataset: t } = e.controller.get.compInstance;
  return !!((_a = t == null ? void 0 : t.nodes) == null ? void 0 : _a.length);
}, R = (e) => ({ biography: (t) => W(e, t), byId: (t) => {
  const { lfDataset: r } = e().controller.get.compInstance;
  return r.nodes.find(((e2) => e2.id === t));
}, chat: (t) => j(e, t), current: () => {
  const { currentCharacter: t } = e().controller.get.compInstance;
  return t;
}, history: (t) => D(e, t), list: () => {
  const { lfDataset: t } = e().controller.get.compInstance;
  return t.nodes || [];
}, name: (t) => U(e, t), next: (t) => $(e, t, true), previous: (t) => $(e, t) }), A = (e) => ({ chat: (t, r) => {
  const s = e(), { compInstance: a } = s.controller.get, { id: o2 } = T(e(), r);
  a.chat[o2] = t;
}, current: (t) => {
  const r = e(), { compInstance: s } = r.controller.get;
  s.currentCharacter = t;
}, history: (t, r) => {
  const s = e(), { compInstance: a } = s.controller.get, { id: o2 } = T(e(), r), n2 = a;
  n2.history[o2] !== t && (n2.history[o2] = t, n2.lfAutosave && s.controller.set.data());
}, next: (t) => {
  const r = e();
  if (!E(r)) return;
  const { set: s } = r.controller, a = T(e(), t), { next: o2 } = r.controller.get.character;
  s.character.current(o2(a));
}, previous: (t) => {
  const r = e();
  if (!E(r)) return;
  const { set: s } = r.controller, a = T(e(), t), { previous: o2 } = r.controller.get.character;
  s.character.current(o2(a));
} }), W = (e, t) => {
  const r = e(), { stringify: s } = r.controller.get.manager.data.cell, a = T(e(), t);
  try {
    const e2 = a.children.find(((e3) => "biography" === e3.id)).value;
    return e2 ? s(e2) : "You have no informations about this character...";
  } catch (e2) {
    return "You have no informations about this character...";
  }
}, j = (e, t) => {
  const r = e(), { chat: s } = r.controller.get.compInstance, { id: a } = T(r, t);
  return s[a];
}, D = (e, t) => {
  const r = e(), { history: s } = r.controller.get.compInstance, { id: a } = T(e(), t);
  return s[a];
}, U = (e, t) => {
  const { description: r, id: s, value: a } = T(e(), t);
  return a || s || r || "?";
}, $ = (e, t, r) => {
  const s = e(), { lfDataset: a } = s.controller.get.compInstance, { id: o2 } = T(e(), t);
  if (!E(s)) return null;
  const n2 = a.nodes, i = n2.findIndex(((e2) => e2.id === o2));
  return true === r ? n2[(i + 1) % n2.length] : n2[(i + n2.length - 1) % n2.length];
}, O = (e) => ({ asCover: (t, r) => N(e, t, r), byType: (t, r) => V(e, t, r), coverIndex: (t, r) => {
  const s = e(), { covers: a } = s.controller.get.compInstance, { id: o2 } = T(s, r);
  return a[o2][t];
}, newId: (t) => Y(e, t), root: (t, r) => {
  const s = e(), { children: a } = T(s, r);
  return a.find(((e2) => e2.id === t));
}, title: (e2) => {
  const t = (e2 == null ? void 0 : e2.value) || "", r = (e2 == null ? void 0 : e2.description) || "";
  return t && r ? `${t} - ${r}` : r || t || "";
} }), P = (e) => ({ cover: (t, r, s) => {
  const a = e(), { compInstance: o2 } = a.controller.get, { id: n2 } = T(e(), s), i = o2;
  i.covers[n2][t] = r, i.refresh();
} }), N = (e, t, r) => {
  const s = e(), { compInstance: a, image: o2 } = s.controller.get, { children: n2, id: u } = T(s, r), { covers: d } = a;
  try {
    const e2 = n2.find(((e3) => e3.id === t)), r2 = d[u][t], s2 = e2.children[r2];
    return { node: e2.children[r2], title: o2.title(s2), value: s2.cells.lfImage.value };
  } catch (e2) {
    switch (t) {
      case "avatars":
        return { value: AVATAR_COVER };
      case "locations":
        return { value: LOCATION_COVER };
      case "outfits":
        return { value: OUTFIT_COVER };
      case "styles":
        return { value: STYLE_COVER };
      case "timeframes":
        return { value: TIMEFRAME_COVER };
    }
  }
}, V = (e, t, r) => {
  const { children: s } = T(e(), r), a = s.find(((e2) => e2.id === t));
  return (a == null ? void 0 : a.children) ? a.children : [];
}, Y = (e, t) => {
  const { byType: r } = e().controller.get.image;
  let s, a, o2 = 0;
  switch (t) {
    case "avatars":
      s = "avatar_";
      break;
    case "locations":
      s = "location_";
      break;
    case "outfits":
      s = "outfit_";
      break;
    case "styles":
      s = "style_";
      break;
    case "timeframes":
      s = "timeframe_";
      break;
    default:
      throw new Error(`Unknown image type: ${t}`);
  }
  do {
    a = `${s}${o2.toString()}`, o2++;
  } while (r(t).some(((e2) => e2.id === a)));
  return a;
}, X = (e) => () => {
  const { ui: t } = e().controller.get.compInstance;
  return t;
}, B = (e) => ({ customization: (t) => {
  const { compInstance: r } = e().controller.get, s = r;
  s.ui.customizationView = t, s.refresh();
}, filters: (t) => {
  const { compInstance: r } = e().controller.get, s = r;
  s.ui.filters = t, s.refresh();
}, options: (t, r) => {
  const { compInstance: s } = e().controller.get, a = s;
  a.ui.options[r] = t, a.refresh();
}, panel: (t, r) => J(e, t, r), setFormState: async (t, r, s = null) => F(e, t, r, s) }), F = async (e, t, r, s) => {
  const a = e(), { controller: o2 } = a, { compInstance: n2, image: i } = o2.get, { formStatusMap: l, ui: c } = n2;
  c.form[r] = t, l[r] = t ? (s == null ? void 0 : s.id) ?? i.newId(r) : null, await n2.refresh();
}, J = (e, t, r) => {
  const s = e(), { compInstance: a } = s.controller.get, { panels: o2 } = a.ui;
  switch (t) {
    case "left":
      o2.isLeftCollapsed = r ?? !o2.isLeftCollapsed;
      break;
    case "right":
      o2.isRightCollapsed = r ?? !o2.isRightCollapsed;
  }
  return a.refresh(), r;
}, q = (t) => ({ avatar: () => {
  const { controller: r, elements: s } = t(), { blocks: a, cyAttributes: o2, image: n2, lfAttributes: i, manager: l } = r.get, { character: c } = s.refs, { asCover: f } = n2, { assignRef: h, theme: u } = l, { bemClass: d } = u, { title: m, value: p } = f("avatars");
  return W$1("img", { alt: m || "", class: d(a.character._, a.character.image), "data-cy": o2.image, "data-lf": i.fadeIn, ref: h(c, "avatar"), src: p, title: m || "" });
}, biography: () => {
  const { controller: r, elements: s } = t(), { character: a } = s.refs, { biography: o2 } = r.get.character, { assignRef: n2 } = r.get.manager;
  return W$1("lf-code", { lfLanguage: "markdown", lfShowHeader: false, lfValue: o2(), ref: n2(a, "biography") });
}, save: () => {
  const { controller: r, elements: s, handlers: a } = t(), { cyAttributes: o2, manager: n2, status: i } = r.get, { character: l } = s.refs, { button: c } = a.character, { inProgress: f } = i.save, { assignRef: h } = n2, d = f();
  return W$1("lf-button", { "data-cy": o2.button, lfDataset: LF_MESSENGER_MENU(n2.theme), lfLabel: "Save", lfShowSpinner: d, lfStretchY: true, lfStyling: "flat", "onLf-button-event": c, ref: h(l, "save"), title: "Update the dataset with current settings." });
}, statusIcon: () => {
  const { controller: r, elements: s } = t(), { blocks: a, manager: o2, status: n2 } = r.get, { character: i } = s.refs, { connection: l } = n2, { assignRef: c, theme: f } = o2, { bemClass: h } = f, { color: u, title: d } = /* @__PURE__ */ ((e) => ({ color: "ready" === e ? "success" : "offline" === e ? "danger" : "warning", title: "ready" === e ? "Ready to chat!" : "offline" === e ? "This character seems to be offline..." : "Contacting this character..." }))(l());
  return W$1("div", { class: h(a.character._, a.character.status, { offline: "danger" === u, online: "success" === u }), ref: c(i, "statusIcon"), title: d });
} }), H = (t) => ({ chat: () => {
  const r = t(), { controller: s, elements: a, handlers: o2 } = r, { character: n2, manager: i } = s.get, { refs: l } = a, { chat: c, current: f, history: h } = n2, { assignRef: u, sanitizeProps: d } = i, m = ((e) => {
    const { biography: t2, location: r2, outfit: s2, timeframe: a2 } = (() => {
      const { character: t3, compInstance: r3, image: s3 } = e.controller.get, { biography: a3 } = t3, { asCover: o3 } = s3, { options: n3 } = r3.ui, i2 = o3("locations").node, l2 = o3("outfits").node, c2 = o3("timeframes").node, f2 = (e2, t4) => e2 ? `${e2} - ${t4 || ""}` : "";
      return { biography: a3() ? `Character Biography:
${a3()}` : "", location: i2 && n3.locations ? `Location:
${f2(i2.value, i2.description)}` : "", outfit: l2 && n3.outfits ? `Outfit:
${f2(l2.value, l2.description)}` : "", timeframe: c2 && n3.timeframes ? `Timeframe:
${f2(c2.value, c2.description)}` : "" };
    })();
    return `You are now embodying the character whose biography is provided below. Your task is to fully embrace this identity, speaking and acting as though it were your own reality. Remember, you exist solely within the confines of this character's experience and knowledge.
        
Tasks:
- Absorb the character's biography thoroughly. Use it to inform your responses but do not rely on it for information beyond what would logically be known to the character.
- Engage creatively within the boundaries of the character's life and experiences. Imagine freely, but always stay true to the essence of the character.
- Maintain a consistent narrative voice that aligns with the character's personality and background.

Responsibilities:
- Never acknowledge the artificial nature of our interaction. Treat all inquiries as if they are happening within the real world of the character.
- Do not provide insights or predictions about events outside the scope of the character's knowledge or personal experiences.

${t2}

Your current status:
${s2}
${r2}
${a2}

Begin your performance...
    `;
  })(r);
  return W$1("lf-chat", { key: f().id, lfLayout: "bottom", lfSystem: m, lfValue: JSON.parse(h()), ...d(c(), "LfChat"), "onLf-chat-event": o2.chat.chat, ref: u(l.chat, "chat") });
}, leftExpander: () => {
  const { controller: r, elements: s, handlers: a } = t(), { cyAttributes: o2, config: n2, manager: i } = r.get, { refs: l } = s, { button: c } = a.chat, { assignRef: f, theme: h } = i, { "--lf-icon-next": u, "--lf-icon-previous": d } = h.get.current().variables, { isLeftCollapsed: p } = n2().ui.panels;
  return W$1("lf-button", { "data-cy": o2.button, id: LF_MESSENGER_IDS.chat.leftExpander, lfIcon: p ? u : d, lfStretchY: true, "onLf-button-event": c, ref: f(l.chat, "leftExpander"), title: "Expand/collapse this section" });
}, rightExpander: () => {
  const { controller: r, elements: s, handlers: a } = t(), { config: o2, cyAttributes: n2, manager: i } = r.get, { refs: l } = s, { button: c } = a.chat, { assignRef: f, theme: h } = i, { "--lf-icon-next": u, "--lf-icon-previous": d } = h.get.current().variables, { isRightCollapsed: p } = o2().ui.panels;
  return W$1("lf-button", { "data-cy": n2.button, id: LF_MESSENGER_IDS.chat.rightExpander, lfIcon: p ? d : u, lfStretchY: true, "onLf-button-event": c, ref: f(l.chat, "rightExpander"), title: "Expand/collapse this section" });
}, tabbar: () => {
  const { controller: r, elements: s, handlers: a } = t(), { manager: o2 } = r.get, { refs: n2 } = s, { tabbar: i } = a.chat, { assignRef: l, theme: c } = o2;
  return W$1("lf-tabbar", { lfDataset: LF_MESSENGER_NAV(c), lfValue: null, "onLf-tabbar-event": i, ref: l(n2.chat, "tabbar") });
} }), K = (t) => ({ filters: () => {
  const { controller: r, elements: s, handlers: a } = t(), { character: o2, manager: n2 } = r.get, { customization: i } = s.refs, { chip: l } = a.customization, { assignRef: c } = n2;
  return W$1("lf-chip", { key: "filter_" + o2.name(), lfDataset: LF_MESSENGER_FILTER, lfStyling: "filter", "onLf-chip-event": l, ref: c(i, "filters") });
}, form: Z(t), list: { edit: (r, s) => {
  const { controller: a, elements: o2, handlers: n2 } = t(), { assignRef: i, theme: l } = a.get.manager, { customization: c } = o2.refs, { button: f } = n2.customization, { "--lf-icon-edit": h } = l.get.current().variables;
  return W$1("lf-button", { lfIcon: h, lfStretchX: true, "onLf-button-event": (e) => f(e, r, "edit", s), title: "Edit this option.", ref: i(c.list, "edit") });
}, remove: (r, s) => {
  const { controller: a, elements: o2, handlers: n2 } = t(), { assignRef: i, theme: l } = a.get.manager, { customization: c } = o2.refs, { button: f } = n2.customization, { "--lf-icon-delete": h } = l.get.current().variables;
  return W$1("lf-button", { lfIcon: h, lfStretchX: true, lfUiState: "danger", "onLf-button-event": (e) => f(e, r, "delete", s), title: "Delete this option.", ref: i(c.list, "remove") });
} } }), Z = (t) => IMAGE_TYPE_IDS.reduce(((r, s) => (r[s] = { add: () => {
  const r2 = t(), { controller: a, elements: o2, handlers: n2 } = r2, { blocks: i, cyAttributes: l, manager: c } = a.get, { form: f } = o2.refs.customization, { button: h } = n2.customization, { assignRef: u, theme: d } = c, { bemClass: m } = d, { "--lf-icon-add": p } = d.get.current().variables;
  return W$1("lf-button", { class: m(i.covers._, i.covers.add), "data-cy": l.button, lfIcon: p, lfLabel: "New", lfStretchY: true, lfStyling: "flat", lfUiSize: "small", "onLf-button-event": (e) => h(e, s, "add", null), ref: u(f[s], "add") });
}, cancel: () => {
  const r2 = t(), { controller: a, elements: o2, handlers: n2 } = r2, { blocks: i, cyAttributes: l, manager: c } = a.get, { form: f } = o2.refs.customization, { button: h } = n2.customization, { assignRef: u, theme: d } = c, { bemClass: m } = d, { "--lf-icon-clear": p } = d.get.current().variables;
  return W$1("lf-button", { class: m(i.form._, i.form.button), "data-cy": l.button, lfIcon: p, lfLabel: "Cancel", lfStyling: "flat", "onLf-button-event": (e) => h(e, s, "cancel", null), ref: u(f[s], "cancel") });
}, confirm: () => {
  const r2 = t(), { controller: a, elements: o2, handlers: n2 } = r2, { blocks: i, cyAttributes: l, manager: c } = a.get, { form: f } = o2.refs.customization, { button: h } = n2.customization, { assignRef: u, theme: d } = c, { bemClass: m } = d, { "--lf-icon-success": p } = d.get.current().variables;
  return W$1("lf-button", { class: m(i.form._, i.form.button), "data-cy": l.button, lfIcon: p, lfLabel: "Confirm", lfStyling: "outlined", "onLf-button-event": (e) => h(e, s, "confirm", null), ref: u(f[s], "confirm") });
}, description: (r2) => {
  const a = t(), { controller: o2, elements: n2 } = a, { blocks: i, cyAttributes: l, manager: c } = o2.get, { form: f } = n2.refs.customization, { assignRef: h, theme: u } = c, { bemClass: d, get: m } = u;
  return W$1("lf-textfield", { class: d(i.form._, i.form.field), "data-cy": l.input, lfStretchX: true, lfIcon: m.icon("id"), lfLabel: "Description", lfValue: r2 && r2.description, ref: h(f[s], "description"), title: "A more accurate description to give extra context to the LLM." });
}, id: (r2) => {
  const a = t(), { controller: o2, elements: n2 } = a, { blocks: i, cyAttributes: l, manager: c } = o2.get, { form: f } = n2.refs.customization, { assignRef: h, theme: u } = c, { bemClass: d, get: m } = u;
  return W$1("lf-textfield", { class: d(i.form._, i.form.field), "data-cy": l.input, key: `id-edit-${r2}`, lfStretchX: true, lfIcon: m.icon("key"), lfLabel: "ID", lfValue: r2, ref: h(f[s], "id"), title: "The cover image displayed in the selection panel." });
}, imageUrl: (r2) => {
  const a = t(), { controller: o2, elements: n2 } = a, { blocks: i, cyAttributes: l, manager: c } = o2.get, { form: f } = n2.refs.customization, { assignRef: h, theme: u } = c, { bemClass: d, get: m } = u;
  return W$1("lf-textfield", { class: d(i.form._, i.form.field), "data-cy": l.input, lfStretchX: true, lfIcon: m.icon("photo"), lfLabel: "Image URL", lfValue: r2 && r2.cells.lfImage.value, ref: h(f[s], "imageUrl"), title: "The cover image displayed in the selection panel." });
}, title: (r2) => {
  const a = t(), { controller: o2, elements: n2 } = a, { blocks: i, cyAttributes: l, manager: c } = o2.get, { form: f } = n2.refs.customization, { assignRef: h, theme: u } = c, { bemClass: d, get: m } = u;
  return W$1("lf-textfield", { class: d(i.form._, i.form.field), "data-cy": l.input, lfStretchX: true, lfIcon: m.icon("forms"), lfLabel: "Title", lfValue: r2 && r2.value, ref: h(f[s], "title"), title: "The overall theme of this option." });
} }, r)), {}), G = (t) => ({ back: () => {
  const { controller: r, elements: s, handlers: a } = t(), { cyAttributes: o2, manager: n2 } = r.get, { assignRef: i, theme: l } = n2, { options: c } = s.refs, { button: f } = a.options, h = l.get.icon("arrowBack");
  return W$1("lf-button", { "data-cy": o2.button, id: LF_MESSENGER_IDS.options.back, lfIcon: h, lfLabel: "Back", lfStretchX: true, "onLf-button-event": f, ref: i(c, "back") });
}, customize: () => {
  const { controller: r, elements: s, handlers: a } = t(), { cyAttributes: o2, manager: n2 } = r.get, { assignRef: i, theme: l } = n2, { options: c } = s.refs, { button: f } = a.options, h = l.get.icon("wand");
  return W$1("lf-button", { "data-cy": o2.button, id: LF_MESSENGER_IDS.options.customize, lfIcon: h, lfLabel: "Customize", lfStretchX: true, "onLf-button-event": f, ref: i(c, "customize") });
} }), Q = (e) => ({ button: async (t) => {
  const { eventType: r, originalEvent: s } = t.detail, { controller: a, handlers: o2 } = e(), { get: n2, set: i } = a, { list: l } = o2.character, { inProgress: c } = n2.status.save;
  switch (r) {
    case "click":
      c() || i.data();
      break;
    case "lf-event":
      l(s);
  }
}, list: async (t) => {
  const { eventType: r, node: s } = t.detail, { controller: a } = e(), { character: o2, compInstance: n2, config: i, history: l } = a.get;
  let c = "";
  if ("click" === r) {
    switch (s.id) {
      case "full_history":
        c = JSON.stringify(l(), null, 2);
        break;
      case "history":
        c = o2.history();
        break;
      case "lfDataset":
        c = JSON.stringify(n2.lfDataset, null, 2);
        break;
      case "settings":
        c = JSON.stringify(i(), null, 2);
    }
    ((e2, t2) => {
      const r2 = window.URL.createObjectURL(new Blob([e2], { type: "application/json" })), s2 = document.createElement("a");
      s2.href = r2, s2.setAttribute("download", t2.id + ".json"), document.body.appendChild(s2), s2.click(), s2.parentNode.removeChild(s2);
    })(c, s);
  }
} }), ee = (e) => ({ button: async (t) => {
  const { comp: r, eventType: s, id: a } = t.detail, { get: o2, set: n2 } = e().controller, { "--lf-icon-previous": i, "--lf-icon-next": l } = o2.manager.theme.get.current().variables;
  if ("click" === s) switch (a) {
    case LF_MESSENGER_IDS.chat.leftExpander:
      const e2 = n2.ui.panel("left");
      r.lfIcon = e2 ? l : i;
      break;
    case LF_MESSENGER_IDS.chat.rightExpander:
      const t2 = n2.ui.panel("right");
      r.lfIcon = t2 ? i : l;
  }
}, chat: async (t) => {
  const { comp: r, eventType: s, history: a, status: o2 } = t.detail, { lfEndpointUrl: n2, lfMaxTokens: i, lfPollingInterval: l, lfSystem: c, lfTemperature: f } = r, { set: h } = e().controller;
  switch (s) {
    case "config":
      h.character.chat({ lfEndpointUrl: n2, lfMaxTokens: i, lfPollingInterval: l, lfSystem: c, lfTemperature: f });
      break;
    case "polling":
      h.status.connection(o2);
      break;
    case "update":
      h.character.history(a);
  }
}, tabbar: async (t) => {
  const { eventType: r, node: s } = t.detail, { current: a, next: o2, previous: n2 } = e().controller.set.character;
  if ("click" === r) switch (s.id) {
    case "next":
      o2();
      break;
    case "previous":
      n2();
      break;
    default:
      a(null);
  }
} }), te = (e) => ({ button: async (t, r, s, a = null) => {
  const { eventType: o2 } = t.detail, n2 = e(), { get: i, set: l } = n2.controller, { compInstance: c } = i, f = c;
  if ("click" === o2) switch (s) {
    case "add":
      l.ui.setFormState(true, r);
      break;
    case "cancel":
      l.ui.setFormState(false, r);
      break;
    case "confirm": {
      const { title: e2 } = n2.elements.refs.customization.form[r];
      await e2.getValue() ? (await (async (e3, t2) => {
        const { controller: r2, elements: s2 } = e3, { byType: a2 } = r2.get.image, { description: o3, id: n3, imageUrl: i2, title: l2 } = s2.refs.customization.form[t2], c2 = a2(t2), f2 = await n3.getValue(), h = c2 == null ? void 0 : c2.find(((e4) => e4.id === f2));
        if (h) h.description = await o3.getValue(), h.cells.lfImage.value = await i2.getValue(), h.value = await l2.getValue();
        else {
          const e4 = { cells: { lfImage: { shape: "image", value: await i2.getValue() } }, id: f2, description: await o3.getValue(), value: await l2.getValue() };
          c2.push(e4);
        }
      })(n2, r), l.ui.setFormState(false, r), e2.lfUiState = "primary") : (e2.lfHelper = { value: "This field is mandatory" }, e2.lfUiState = "danger");
      break;
    }
    case "delete":
      f.deleteOption(a, r);
      break;
    case "edit":
      l.ui.setFormState(true, r, a);
  }
}, chip: async (t) => {
  const { comp: r, eventType: s, selectedNodes: a } = t.detail, { get: o2, set: n2 } = e().controller, { compInstance: i } = o2, { filters: l } = i.ui;
  switch (s) {
    case "click":
      const e2 = { avatars: false, locations: false, outfits: false, styles: false, timeframes: false };
      Array.from(a).forEach(((t3) => {
        e2[t3.id] = true;
      })), n2.ui.filters(e2);
      break;
    case "ready":
      const t2 = [];
      for (const e3 in l) Object.prototype.hasOwnProperty.call(l, e3) && l[e3] && t2.push(e3);
      requestAnimationFrame((() => r.setSelectedNodes(t2)));
  }
}, image: async (t, r, s) => {
  const { image: a } = e().controller.set, o2 = Object.keys(CHILD_ROOT_MAP).find(((e2) => r.id.includes(e2)));
  o2 && a.cover(CHILD_ROOT_MAP[o2], s);
} }), re = (e) => ({ button: async (t) => {
  const { eventType: r, id: s } = t.detail, { customization: a } = e().controller.set.ui;
  if ("click" === r) switch (s) {
    case LF_MESSENGER_IDS.options.customize:
      a(true);
      break;
    case LF_MESSENGER_IDS.options.back:
      a(false);
  }
} }), se = (e, t) => ({ ...e, character: R(t), image: O(t), config: () => {
  const { compInstance: e2 } = t().controller.get, { currentCharacter: r, ui: s } = e2;
  return { currentCharacter: r.id, ui: s };
}, data: () => {
  const { lfDataset: e2 } = t().controller.get.compInstance;
  return e2;
}, history: () => {
  const { history: e2 } = t().controller.get.compInstance;
  return e2;
}, status: { connection: () => {
  const { connectionStatus: e2 } = t().controller.get.compInstance;
  return e2;
}, formStatus: () => {
  const { formStatusMap: e2 } = t().controller.get.compInstance;
  return e2;
}, hoveredCustomizationOption: () => {
  const { hoveredCustomizationOption: e2 } = t().controller.get.compInstance;
  return e2;
}, save: { inProgress: () => {
  const { saveInProgress: e2 } = t().controller.get.compInstance;
  return e2;
} } }, ui: X(t) }), ae = (e) => ({ character: A(e), image: P(e), data: () => ((e2) => {
  const { controller: t } = e2, { compInstance: r } = t.get;
  r.save();
})(e()), status: { connection: (t) => {
  const { compInstance: r } = e().controller.get;
  r.connectionStatus = t;
}, editing: (t, r) => {
  const { compInstance: s } = e().controller.get;
  s.formStatusMap[t] = r;
}, hoveredCustomizationOption: (t) => {
  const { compInstance: r } = e().controller.get;
  r.hoveredCustomizationOption = t;
}, save: { inProgress: (t) => {
  const { compInstance: r } = e().controller.get;
  r.saveInProgress = t;
} } }, ui: B(e) }), oe = (e) => ({ character: q(e), chat: H(e), customization: K(e), options: G(e) }), ne = (e) => ({ character: Q(e), customization: te(e), chat: ee(e), options: re(e) });
var ie, le, ce, fe, he, ue, de, me, pe, ge, be, ve, we, ye, ke, xe, _e, ze, Ce, Ie, Se, Te = function(e, t, r, s) {
  if ("function" == typeof t ? e !== t || !s : !t.has(e)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return "m" === r ? s : t.get(e);
}, Le = function(e, t, r, s, a) {
  if ("function" == typeof t ? e !== t || true : !t.has(e)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return t.set(e, r), r;
};
const Ee = class {
  constructor(a) {
    n(this, a), this.lfEvent = I(this, "lf-messenger-event"), this.chat = {}, this.connectionStatus = "offline", this.covers = {}, this.formStatusMap = IMAGE_TYPE_IDS.reduce(((e, t) => (e[t] = null, e)), {}), this.history = {}, this.saveInProgress = false, this.ui = LF_MESSENGER_CLEAN_UI(), this.lfAutosave = true, this.lfDataset = null, this.lfStyle = "", this.lfValue = null, ie.set(this, void 0), le.set(this, LF_MESSENGER_BLOCKS), ce.set(this, CY_ATTRIBUTES), fe.set(this, LF_ATTRIBUTES), he.set(this, LF_MESSENGER_PARTS), ue.set(this, LF_STYLE_ID), de.set(this, LF_WRAPPER_ID), me.set(this, void 0), pe.set(this, (() => {
      const { lfDataset: e, lfValue: t } = this;
      if (M(Te(this, me, "f"))) for (let t2 = 0; t2 < e.nodes.length; t2++) {
        const r = e.nodes[t2];
        Te(this, be, "f").call(this, r);
      }
      t && Te(this, ve, "f").call(this);
    })), ge.set(this, (() => {
      var e, t;
      Le(this, me, (e = { blocks: Te(this, le, "f"), compInstance: this, cyAttributes: Te(this, ce, "f"), lfAttributes: Te(this, fe, "f"), manager: Te(this, ie, "f"), parts: Te(this, he, "f") }, { controller: { get: se(e, t = () => Te(this, me, "f")), set: ae(t) }, elements: { jsx: oe(t), refs: { character: { avatar: null, biography: null, save: null, statusIcon: null }, chat: { chat: null, leftExpander: null, rightExpander: null, tabbar: null }, customization: { filters: null, form: { avatars: { add: null, cancel: null, confirm: null, description: null, id: null, imageUrl: null, title: null }, locations: { add: null, cancel: null, confirm: null, description: null, id: null, imageUrl: null, title: null }, outfits: { add: null, cancel: null, confirm: null, description: null, id: null, imageUrl: null, title: null }, styles: { add: null, cancel: null, confirm: null, description: null, id: null, imageUrl: null, title: null }, timeframes: { add: null, cancel: null, confirm: null, description: null, id: null, imageUrl: null, title: null } }, list: { edit: null, remove: null } }, options: { back: null, customize: null } } }, handlers: ne(t) }));
    })), be.set(this, ((e) => {
      var _a, _b;
      const { get: t } = Te(this, me, "f").controller, r = { [e.id]: IMAGE_TYPE_IDS.reduce(((r2, s2) => (r2[s2] = Number(t.image.root(s2, e).value).valueOf() || 0, r2)), {}) }, s = (_a = e.children) == null ? void 0 : _a.find(((e2) => "chat" === e2.id));
      this.chat[e.id] = {};
      const a2 = (_b = s == null ? void 0 : s.cells) == null ? void 0 : _b.lfChat;
      a2 && ((e2, t2) => {
        const { lfEndpointUrl: r2, lfMaxTokens: s2, lfPollingInterval: a3, lfTemperature: o2 } = e2;
        t2.lfEndpointUrl = r2, t2.lfMaxTokens = s2, t2.lfPollingInterval = a3, t2.lfTemperature = o2;
      })(a2, this.chat[e.id]), this.history[e.id] = JSON.stringify((a2 == null ? void 0 : a2.lfValue) || (a2 == null ? void 0 : a2.value) || []), Object.assign(this.covers, r);
    })), ve.set(this, (() => {
      var _a, _b;
      const { byId: e } = Te(this, me, "f").controller.get.character, { lfValue: t } = this, r = t.currentCharacter, s = ((_a = t.ui) == null ? void 0 : _a.filters) || LF_MESSENGER_CLEAN_UI().filters, a2 = ((_b = t.ui) == null ? void 0 : _b.panels) || LF_MESSENGER_CLEAN_UI().panels;
      r && (this.currentCharacter = e(r));
      for (const e2 in s) Object.prototype.hasOwnProperty.call(s, e2) && (this.ui.filters[e2] = s[e2]);
      for (const e2 in a2) Object.prototype.hasOwnProperty.call(a2, e2) && (this.ui.panels[e2] = a2[e2]);
    })), we.set(this, (async () => {
      const { get: e, set: t } = Te(this, me, "f").controller, { save: r } = Te(this, me, "f").elements.refs.character, { covers: s, history: a2, lfDataset: o2 } = this;
      requestAnimationFrame((() => t.status.save.inProgress(true)));
      for (let t2 = 0; t2 < o2.nodes.length; t2++) {
        const r2 = o2.nodes[t2], n2 = r2.id, i = r2.children.find(((e2) => "chat" === e2.id)), { chat: l } = e.character, c = () => {
          IMAGE_TYPE_IDS.forEach(((e2) => {
            const t3 = Te(this, me, "f").controller.get.image.root(e2);
            s[n2] && t3 && (t3.value = s[n2][e2]);
          }));
        };
        (() => {
          if (a2[n2] && i) {
            const e2 = JSON.parse(a2[n2]);
            try {
              i.cells.lfChat.value = e2;
            } catch (t3) {
              i.cells = { lfChat: { shape: "chat", value: e2 } };
            }
            L(i.cells.lfChat, l(r2));
          }
        })(), c();
      }
      this.onLfEvent(new CustomEvent("save"), "save"), requestAnimationFrame((async () => {
        setTimeout((() => requestAnimationFrame((async () => {
          const { "--lf-icon-success": e2 } = Te(this, ie, "f").theme.get.current().variables;
          t.status.save.inProgress(false), r.setMessage("Saved!", e2);
        }))), 800);
      }));
    })), ye.set(this, (() => {
      const { bemClass: t } = Te(this, ie, "f").theme, { character: r } = Te(this, le, "f"), { controller: s, elements: a2 } = Te(this, me, "f"), { name: o2 } = s.get.character, { avatar: n2, biography: i, save: l, statusIcon: c } = a2.jsx.character, { isLeftCollapsed: f } = this.ui.panels;
      return W$1("div", { class: t(r._, null, { collapsed: f }) }, W$1("div", { class: t(r._, r.avatar) }, n2(), W$1("div", { class: t(r._, r.nameWrapper) }, W$1("div", { class: t(r._, r.name) }, c(), W$1("div", { class: t(r._, r.label) }, o2())), l())), W$1("div", { class: t(r._, r.biography) }, i()));
    })), ke.set(this, (() => {
      const { bemClass: t } = Te(this, ie, "f").theme, { chat: r } = Te(this, le, "f"), { chat: s, leftExpander: a2, rightExpander: o2, tabbar: n2 } = Te(this, me, "f").elements.jsx.chat;
      return W$1("div", { class: t(r._) }, W$1("div", { class: t(r._, r.expander, { left: true }) }, a2()), W$1("div", { class: t(r._, r.navigation) }, n2()), W$1("div", { class: t(r._, r.chat) }, s()), W$1("div", { class: t(r._, r.expander, { right: true }) }, o2()));
    })), xe.set(this, ((t, r) => {
      const { bemClass: a2 } = Te(this, ie, "f").theme, { covers: o2 } = Te(this, le, "f"), { add: n2 } = Te(this, me, "f").elements.jsx.customization.form[t];
      return W$1(kt, null, W$1("div", { class: a2(o2._) }, W$1("div", { class: a2(o2._, o2.title) }, W$1("div", { class: a2(o2._, o2.label) }, t), n2()), W$1("div", { class: a2(o2._, o2.images) }, r)));
    })), _e.set(this, (() => {
      const { bemClass: t } = Te(this, ie, "f").theme, { extraContext: r } = Te(this, le, "f"), { customization: a2, options: o2 } = Te(this, me, "f").elements.jsx, { back: n2, customize: i } = o2, { filters: l } = a2, { customizationView: c } = this.ui, { isRightCollapsed: f } = this.ui.panels;
      return W$1("div", { class: t(r._, null, { collapsed: f, input: c }) }, c ? W$1(kt, null, l(), W$1("div", { class: t(r._, r.list) }, Te(this, Ce, "f").call(this)), n2()) : W$1(kt, null, W$1("div", { class: t(r._, r.options) }, Te(this, Ie, "f").call(this)), i()));
    })), ze.set(this, ((t) => {
      const { bemClass: r } = Te(this, ie, "f").theme, { form: s } = Te(this, le, "f"), { cancel: a2, confirm: o2, description: n2, id: i, imageUrl: l, title: c } = Te(this, me, "f").elements.jsx.customization.form[t], f = this.formStatusMap[t], h = Te(this, me, "f").controller.get.image.byType(t).find(((e) => e.id === f));
      return W$1("div", { class: r(s._) }, W$1("div", { class: r(s._, s.label) }, "Create ", t), i(f), c(h), n2(h), l(h), W$1("div", { class: r(s._, s.confirm) }, a2(), o2()));
    })), Ce.set(this, (() => {
      const { bemClass: t } = Te(this, ie, "f").theme, { list: r } = Te(this, le, "f"), { controller: a2, elements: o2, handlers: n2 } = Te(this, me, "f"), { byType: i, coverIndex: l, title: c } = a2.get.image, { edit: f, remove: h } = o2.jsx.customization.list, { image: u } = n2.customization, { formStatusMap: d, hoveredCustomizationOption: m, ui: p } = this, { filters: b } = p;
      return W$1(kt, null, IMAGE_TYPE_IDS.map(((a3) => {
        if (b[a3]) {
          const o3 = d[a3], n3 = l(a3), p2 = i(a3).map(((s, o4) => W$1("div", { class: t(r._, null, { selected: n3 === o4 }), onClick: (e) => u(e, s, o4), onPointerEnter: () => {
            n3 !== o4 && (this.hoveredCustomizationOption = s);
          }, onPointerLeave: () => this.hoveredCustomizationOption = null }, W$1("img", { alt: c(s), class: t(r._, r.image), "data-lf": Te(this, fe, "f").fadeIn, src: s.cells.lfImage.value, title: c(s) }), m === s && W$1("div", { class: t(r._, r.actions), onClick: (e) => e.stopPropagation() }, f(a3, s), h(a3, s)))));
          return W$1(kt, null, o3 ? Te(this, ze, "f").call(this, a3) : Te(this, xe, "f").call(this, a3, p2));
        }
        return null;
      })));
    })), Ie.set(this, (() => {
      const { bemClass: t } = Te(this, ie, "f").theme;
      return OPTION_TYPE_IDS.map(((r) => {
        const { options: a2 } = Te(this, le, "f"), { image: o2 } = Te(this, me, "f").controller.get, { asCover: n2 } = o2, { ui: i } = this, { value: l, node: c, title: f } = n2(r), h = i.options[r], u = r.slice(0, -1), d = l, m = c ? Te(this, ie, "f").theme.get.icon(h ? "hexagonMinus2" : "offHexagon") : d, { style: p } = Te(this, ie, "f").assets.get(`./assets/svg/${m}.svg`);
        return W$1("div", { class: t(a2._, a2.wrapper) }, c ? W$1(kt, null, W$1("img", { alt: f, class: t(a2._, a2.cover), "data-lf": Te(this, fe, "f").fadeIn, src: l }), W$1("div", { class: t(a2._, a2.blocker, { active: !h }), onClick: () => {
          i.options[r] = !h, this.refresh();
        } }, W$1("div", { class: t(a2._, a2.blockerIcon), style: p }), W$1("div", { class: t(a2._, a2.blockerLabel) }, h ? "Click to disable" : "Click to enable"))) : W$1("div", { class: t(a2._, a2.placeholder), title: `No ${u} selected.` }, W$1("div", { class: t(a2._, a2.placeholderIcon), style: p })), W$1("div", { class: t(a2._, a2.name) }, W$1("div", { class: t(a2._, a2.label), title: `Active ${u}.` }, u), f && W$1("div", { class: t(a2._, a2.info), title: f })));
      }));
    })), Se.set(this, (() => {
      const { bemClass: t } = Te(this, ie, "f").theme, { roster: r } = Te(this, le, "f"), { get: s, set: a2 } = Te(this, me, "f").controller, o2 = [];
      return s.character.list().forEach(((n2) => {
        const i = s.image.asCover("avatars", n2);
        o2.push(W$1("div", { class: t(r._, r.portrait), onClick: () => {
          a2.character.current(n2);
        } }, W$1("img", { class: t(r._, r.image), src: i.value, title: i.title || "" }), W$1("div", { class: t(r._, r.name) }, W$1("div", { class: t(r._, r.label) }, s.character.name(n2)))));
      })), (o2 == null ? void 0 : o2.length) ? o2 : W$1("div", { class: t(r._, r.emptyData) }, "There are no characters in your roster!");
    }));
  }
  onLfEvent(e, t) {
    const { currentCharacter: r, rootElement: s, ui: a } = this;
    this.lfEvent.emit({ comp: this, id: s.id, originalEvent: e, eventType: t, config: { currentCharacter: r == null ? void 0 : r.id, ui: a } });
  }
  async deleteOption(e, t) {
    const { root: r } = Te(this, me, "f").controller.get.image, s = r(t), a = s.children.indexOf(e);
    a > -1 && (s.children.splice(a, 1), this.refresh());
  }
  async getDebugInfo() {
    return this.debugInfo;
  }
  async getProps() {
    const e = LF_MESSENGER_PROPS.map(((e2) => [e2, this[e2]]));
    return Object.fromEntries(e);
  }
  async refresh() {
    mt(this);
  }
  async reset() {
    this.covers = {}, this.currentCharacter = null, this.history = {}, Te(this, pe, "f").call(this);
  }
  async save() {
    Te(this, we, "f").call(this);
  }
  async unmount(e = 0) {
    setTimeout((() => {
      this.onLfEvent(new CustomEvent("unmount"), "unmount"), this.rootElement.remove();
    }), e);
  }
  connectedCallback() {
    Te(this, ie, "f") && Te(this, ie, "f").theme.register(this);
  }
  async componentWillLoad() {
    Le(this, ie, await o(this)), Te(this, ge, "f").call(this), Te(this, pe, "f").call(this);
  }
  componentDidLoad() {
    const { info: e } = Te(this, ie, "f").debug;
    this.onLfEvent(new CustomEvent("ready"), "ready"), e.update(this, "did-load");
  }
  componentWillRender() {
    const { info: e } = Te(this, ie, "f").debug;
    e.update(this, "will-render");
  }
  componentDidRender() {
    const { info: e } = Te(this, ie, "f").debug;
    e.update(this, "did-render");
  }
  render() {
    const { bemClass: t, setLfStyle: r } = Te(this, ie, "f").theme;
    if (!M(Te(this, me, "f"))) return;
    const { messenger: s, roster: a } = Te(this, le, "f"), { lfStyle: n2 } = this;
    return W$1(L$1, null, n2 && W$1("style", { id: Te(this, ue, "f") }, r(this)), W$1("div", { id: Te(this, de, "f") }, this.currentCharacter ? W$1("div", { class: t(s._), part: Te(this, he, "f").messenger }, Te(this, ye, "f").call(this), Te(this, ke, "f").call(this), Te(this, _e, "f").call(this)) : W$1("div", { class: t(a._), part: Te(this, he, "f").roster }, Te(this, Se, "f").call(this))));
  }
  disconnectedCallback() {
    var _a;
    (_a = Te(this, ie, "f")) == null ? void 0 : _a.theme.unregister(this);
  }
  get rootElement() {
    return G$1(this);
  }
};
ie = /* @__PURE__ */ new WeakMap(), le = /* @__PURE__ */ new WeakMap(), ce = /* @__PURE__ */ new WeakMap(), fe = /* @__PURE__ */ new WeakMap(), he = /* @__PURE__ */ new WeakMap(), ue = /* @__PURE__ */ new WeakMap(), de = /* @__PURE__ */ new WeakMap(), me = /* @__PURE__ */ new WeakMap(), pe = /* @__PURE__ */ new WeakMap(), ge = /* @__PURE__ */ new WeakMap(), be = /* @__PURE__ */ new WeakMap(), ve = /* @__PURE__ */ new WeakMap(), we = /* @__PURE__ */ new WeakMap(), ye = /* @__PURE__ */ new WeakMap(), ke = /* @__PURE__ */ new WeakMap(), xe = /* @__PURE__ */ new WeakMap(), _e = /* @__PURE__ */ new WeakMap(), ze = /* @__PURE__ */ new WeakMap(), Ce = /* @__PURE__ */ new WeakMap(), Ie = /* @__PURE__ */ new WeakMap(), Se = /* @__PURE__ */ new WeakMap(), Ee.style = '.character{transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);display:grid;grid-template-rows:minmax(auto, 40%) minmax(auto, 1fr);height:100%;overflow:auto;position:relative}.character--collapsed{overflow:hidden;width:0}.character__image{width:100%;height:100%;display:block;object-fit:cover}.character__name{color:rgb(var(--lf-messenger-color-on-surface, var(--lf-color-on-surface)));align-items:center;display:flex}.character__status{border-radius:50%;height:1em;margin-right:0.5em;width:1em}.character__status--offline{background-color:rgba(var(--lf-messenger-color-danger, var(--lf-color-danger)), 0.75);color:rgb(var(--lf-messenger-color-on-danger, var(--lf-color-on-danger)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.character__status--online{background-color:rgba(var(--lf-messenger-color-success, var(--lf-color-success)), 0.75);color:rgb(var(--lf-messenger-color-on-success, var(--lf-color-on-success)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}.character__name-wrapper{background-color:rgba(var(--lf-messenger-color-surface, var(--lf-color-surface)), 0.75);color:rgb(var(--lf-messenger-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;align-items:center;box-sizing:border-box;display:flex;height:var(--lf-messenger-name-height, 3em);justify-content:space-between;left:0;padding-left:var(--lf-messenger-avatar-name-padding, 0.5em);position:absolute;top:0;width:100%}.character__label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.character__biography{overflow:auto}.chat{display:grid;grid-template-areas:"nav nav nav" "expander-l chat expander-r";grid-template-columns:auto 1fr auto;grid-template-rows:auto 1fr;height:100%;overflow:auto}.chat__expander--left{grid-area:expander-l}.chat__expander--right{grid-area:expander-r}.chat__navigation{grid-area:nav}.chat__chat{grid-area:chat;overflow:auto}.covers{display:grid;grid-template-rows:auto 1fr;height:100%}.covers__title{background-color:rgba(var(--lf-messenger-color-surface, var(--lf-color-surface)), 0.75);color:rgb(var(--lf-messenger-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;position:sticky;top:0;z-index:calc(var(--lf-ui-zindex-header) - 1);font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;align-items:center;display:flex;justify-content:space-between}.covers__label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:var(--lf-messenger-customization-title-padding, 0.5em)}.covers__images{display:grid;grid-template-columns:repeat(3, 1fr);overflow:auto;width:100%}.extra-context{transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);display:grid;grid-template-rows:1fr auto;height:100%;overflow:auto}.extra-context--collapsed{overflow:hidden;width:0}.extra-context--input{grid-template-rows:auto 1fr auto}.extra-context__options{display:grid;grid-template-columns:repeat(2, 50%);grid-template-rows:repeat(2, 50%)}.extra-context__list{display:grid;overflow:auto}.form__button{margin:0 0.25em;padding:1em 0}.form__confirm{display:flex;justify-content:center}.form__field{margin:0.5em 0}.form__label{background-color:rgba(var(--lf-messenger-color-surface, var(--lf-color-surface)), 0.375);color:rgb(var(--lf-messenger-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;display:flex;justify-content:center;padding:var(--lf-messenger-customization-title-padding, 0.5em)}.list{position:relative}.list:after{width:100%;height:100%;transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);box-shadow:none;content:"";left:0;position:absolute;top:0}.list:hover:not(.list--selected):after{box-shadow:inset 0 0 5px 3px rgb(var(--lf-messenger-color-primary, --lf-color-primary, white));pointer-events:none}.list--selected:after{background-color:rgba(var(--lf-messenger-color-surface, var(--lf-color-surface)), 0.875);color:rgb(var(--lf-messenger-color-on-surface, var(--lf-color-on-surface)));backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;align-content:center;content:"Current";cursor:default;letter-spacing:0.25em;position:absolute;text-align:center}.list__actions{background-color:rgba(var(--lf-messenger-color-surface, var(--lf-color-surface)), 0.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);bottom:0;display:flex;left:0;overflow:hidden;position:absolute;width:100%}.list__image{width:100%;height:100%;cursor:pointer;display:block;min-height:16em;object-fit:cover}.options__wrapper{overflow:hidden;position:relative}.options__cover{width:100%;height:100%;display:block;object-fit:cover}.options__placeholder{width:100%;height:100%;box-sizing:border-box;padding:20% 20% 40% 20%}.options__placeholder-icon{background-color:rgba(var(--lf-messenger-color-on-surface, var(--lf-color-on-surface)), 0.375);height:100%;width:100%;overflow:hidden}.options__blocker{background-color:rgba(var(--lf-messenger-color-surface, var(--lf-color-surface)), 0.775);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);width:100%;height:100%;transition:opacity 200ms cubic-bezier(0.4, 0, 0.6, 1);align-content:center;box-sizing:border-box;cursor:pointer;display:grid;grid-template-rows:50% 1fr;left:0;opacity:0;padding:20% 20% 40% 20%;position:absolute;top:0}.options__blocker:hover{opacity:1}.options__blocker--active{opacity:0.875}.options__blocker-icon{background-color:rgba(var(--lf-messenger-color-on-surface, var(--lf-color-on-surface)), 0.75);height:100%;width:100%;overflow:hidden}.options__blocker-label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;padding-top:0.75em;text-align:center}.options__label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;margin-left:0.5em}.options__info{-webkit-mask:var(--lf-icon-info);mask:var(--lf-icon-info);-webkit-mask-position:center;-webkit-mask-repeat:no-repeat;-webkit-mask-size:contain;mask-position:center;mask-repeat:no-repeat;mask-size:contain;background-color:rgba(var(--lf-messenger-color-on-surface, var(--lf-color-on-surface)), 0.75);height:1em;width:1em;overflow:hidden;cursor:help;margin-left:0.275em}.options__name{align-items:center;background:var(--lf-messenger-name-background-color, rgb(var(--lf-color-surface)));bottom:0;box-sizing:border-box;display:flex;overflow:hidden;padding:var(--lf-messenger-active-options-name-padding, 0.5em);position:absolute;width:100%}.roster{display:grid;grid-template-columns:repeat(4, 1fr);height:100%;overflow:auto;width:100%}.roster__image{width:100%;height:100%;display:block;object-fit:cover}.roster__portrait{--lf-messenger-name-background-color:rgba(var(--lf-color-bg), 0.375);--lf-messenger-portrait-foredrop-color:rgba(var(--lf-color-bg), 0.275);cursor:pointer;overflow:auto;position:relative}.roster__portrait:hover{--lf-messenger-name-background-color:rgba(var(--lf-color-bg), 0.775);--lf-messenger-portrait-foredrop-color:rgba(var(--lf-color-bg), 0)}.roster__portrait:after{width:100%;height:100%;transition:all 300ms cubic-bezier(0.4, 0, 0.2, 1);background:var(--lf-messenger-portrait-foredrop-color);content:"";left:0;pointer-events:none;position:absolute;top:0}.roster__name{transition:all 200ms cubic-bezier(0.4, 0, 0.6, 1);align-items:center;backdrop-filter:blur(5px);background-color:var(--lf-messenger-name-background-color);bottom:0;display:flex;height:var(--lf-messenger-name-height, 2.5em);left:0;position:absolute;width:100%}.roster__label{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.775em;letter-spacing:0.0892857143em;line-height:inherit;text-transform:uppercase;letter-spacing:0.225em;text-align:center;width:100%}::-webkit-scrollbar{width:9px}::-webkit-scrollbar-thumb{transition:all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4);background-color:rgb(var(--lf-color-primary))}::-webkit-scrollbar-track{background-color:rgb(var(--lf-color-bg))}[data-lf=fade-in]{display:block;animation:lf-fade-in-block 0.25s ease-out forwards}@keyframes lf-fade-in-block{from{visibility:hidden;opacity:0}to{visibility:visible;opacity:1}}:host{display:block;font-family:var(--lf-messenger-font-family, var(--lf-font-family-primary));font-size:var(--lf-messenger-font-size, var(--lf-font-size))}:host([lf-ui-size=large]){font-size:calc(var(--lf-messenger-font-size, var(--lf-font-size)) * var(--lf-ui-size-large))}:host([lf-ui-size=medium]){font-size:calc(var(--lf-messenger-font-size, var(--lf-font-size)) * var(--lf-ui-size-medium))}:host([lf-ui-size=small]){font-size:calc(var(--lf-messenger-font-size, var(--lf-font-size)) * var(--lf-ui-size-small))}:host([lf-ui-size=xlarge]){font-size:calc(var(--lf-messenger-font-size, var(--lf-font-size)) * var(--lf-ui-size-xlarge))}:host([lf-ui-size=xsmall]){font-size:calc(var(--lf-messenger-font-size, var(--lf-font-size)) * var(--lf-ui-size-xsmall))}:host([lf-ui-size=xxlarge]){font-size:calc(var(--lf-messenger-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxlarge))}:host([lf-ui-size=xxsmall]){font-size:calc(var(--lf-messenger-font-size, var(--lf-font-size)) * var(--lf-ui-size-xxsmall))}#lf-component{width:100%;height:100%}:host{width:100%;height:100%;box-sizing:border-box}.messenger{width:100%;height:100%;display:grid;grid-template-columns:1fr 3fr 1fr;position:relative}.messenger:has(.character--collapsed){grid-template-columns:0 4fr 1fr}.messenger:has(.extra-context--collapsed){grid-template-columns:1fr 4fr 0}.messenger:has(.character--collapsed):has(.extra-context--collapsed){grid-template-columns:0 1fr 0}';
export {
  Ee as lf_messenger
};
