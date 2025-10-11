import { api } from "/scripts/api.js";
import { app } from "/scripts/app.js";
const LF_ACCORDION_BLOCKS = {
  accordion: { _: "accordion" },
  node: {
    _: "node",
    content: "content",
    expand: "expand",
    header: "header",
    icon: "icon",
    text: "text"
  }
};
const LF_ACCORDION_PARTS = {
  accordion: "accordion",
  content: "content",
  expand: "expand",
  header: "header",
  icon: "icon",
  rippleSurface: "ripple-surface",
  text: "text"
};
const LF_ACCORDION_PROPS = [
  "lfDataset",
  "lfRipple",
  "lfStyle",
  "lfUiSize",
  "lfUiState"
];
const LF_ARTICLE_BLOCKS = {
  article: { _: "article" },
  content: { _: "content", body: "body" },
  emptyData: { _: "empty-data", text: "text" },
  paragraph: { _: "paragraph" },
  section: { _: "section" }
};
const LF_ARTICLE_PARTS = {
  article: "article",
  content: "content",
  emptyData: "empty-data",
  paragraph: "paragraph",
  section: "section"
};
const LF_ARTICLE_PROPS = [
  "lfDataset",
  "lfEmpty",
  "lfStyle"
];
const LF_BADGE_CSS_VARS = {
  transform: "--lf_badge_transform"
};
const LF_BADGE_BLOCKS = {
  badge: { _: "badge", image: "image", label: "label" }
};
const LF_BADGE_PARTS = {
  badge: "badge",
  image: "image",
  label: "label"
};
const LF_BADGE_PROPS = [
  "lfImageProps",
  "lfLabel",
  "lfPosition",
  "lfStyle",
  "lfUiState"
];
const LF_BUTTON_BLOCKS = {
  button: {
    _: "button",
    dropdown: "dropdown",
    dropdownRipple: "dropdown-ripple",
    icon: "icon",
    label: "label",
    list: "list",
    spinner: "spinner"
  }
};
const LF_BUTTON_PARTS = {
  button: "button",
  dropdown: "dropdown",
  dropdownRipple: "dropdown-ripple",
  icon: "icon",
  label: "label",
  list: "list",
  rippleSurface: "ripple-surface",
  spinner: "spinner"
};
const LF_BUTTON_PROPS = [
  "lfAriaLabel",
  "lfDataset",
  "lfIcon",
  "lfIconOff",
  "lfLabel",
  "lfRipple",
  "lfShowSpinner",
  "lfStretchX",
  "lfStretchY",
  "lfStyle",
  "lfStyling",
  "lfToggable",
  "lfTrailingIcon",
  "lfType",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_CANVAS_BLOCKS = {
  canvas: {
    _: "canvas",
    board: "board",
    image: "image",
    preview: "preview"
  }
};
const LF_CANVAS_PARTS = {
  board: "board",
  canvas: "canvas",
  image: "image",
  preview: "preview"
};
const LF_CANVAS_PROPS = [
  "lfBrush",
  "lfColor",
  "lfCursor",
  "lfImageProps",
  "lfOpacity",
  "lfPreview",
  "lfSize",
  "lfStrokeTolerance",
  "lfStyle"
];
const LF_CAROUSEL_BLOCKS = {
  carousel: {
    _: "carousel",
    back: "back",
    forward: "forward",
    slide: "slide",
    track: "track"
  },
  slideBar: {
    _: "slide-bar",
    segment: "segment"
  }
};
const LF_CAROUSEL_IDS = {
  back: "back-button",
  forward: "forward-button"
};
const LF_CAROUSEL_PARTS = {
  back: "back",
  carousel: "carousel",
  forward: "forward",
  segment: "segment",
  slideBar: "slide-bar",
  track: "track"
};
const LF_CAROUSEL_PROPS = [
  "lfAutoPlay",
  "lfDataset",
  "lfInterval",
  "lfLightbox",
  "lfNavigation",
  "lfShape",
  "lfStyle"
];
const LF_CHART_CSS_VARS = {
  height: "--lf_chart_height",
  width: "--lf_chart_width"
};
const LF_CHART_BLOCKS = {
  chart: { _: "chart" }
};
const LF_CHART_PARTS = {
  chart: "chart"
};
const LF_CHART_PROPS = [
  "lfAxis",
  "lfColors",
  "lfDataset",
  "lfLegend",
  "lfSeries",
  "lfSizeX",
  "lfSizeY",
  "lfStyle",
  "lfTypes",
  "lfXAxis",
  "lfYAxis"
];
const LF_CHAT_BLOCKS = {
  chat: {
    _: "chat",
    clear: "clear",
    configuration: "configuration",
    error: "error",
    icon: "icon",
    prompt: "prompt",
    send: "send",
    settings: "settings",
    spinner: "spinner",
    spinnerBar: "spinner-bar",
    text: "text",
    title: "title"
  },
  commands: {
    _: "commands",
    stt: "stt"
  },
  input: {
    _: "input",
    button: "button",
    progressbar: "progressbar",
    textarea: "textarea"
  },
  messages: {
    _: "messages",
    blockquote: "blockquote",
    bold: "bold",
    bulletList: "bullet-list",
    code: "code",
    container: "container",
    content: "content",
    empty: "empty",
    heading: "heading",
    hr: "hr",
    inlineCode: "inline-code",
    inlineContainer: "inline-container",
    italic: "italic",
    lineBreak: "line-break",
    link: "link",
    list: "list",
    listItem: "list-item",
    paragraph: "paragraph"
  },
  request: { _: "request" },
  settings: {
    _: "settings",
    back: "back",
    configuration: "configuration",
    textarea: "textarea",
    textfield: "textfield"
  },
  toolbar: {
    _: "toolbar",
    button: "button"
  }
};
const LF_CHAT_IDS = {
  chat: {
    clear: "chat-clear",
    configuration: "chat-configuration",
    prompt: "chat-prompt",
    send: "chat-send",
    settings: "chat-settings",
    stt: "chat-stt"
  },
  options: {
    back: "option-back",
    contextWindow: "option-context",
    endpointUrl: "option-endpoint",
    maxTokens: "option-maxtokens",
    polling: "option-polling",
    system: "option-system",
    temperature: "option-temperature"
  },
  toolbar: {
    copyContent: "toolbar-copy-content",
    deleteMessage: "toolbar-delete-message",
    regenerate: "toolbar-regenerate"
  }
};
const LF_CHAT_PARTS = {
  back: "back",
  chat: "chat",
  clear: "clear",
  configuration: "configuration",
  contextWindow: "context-window",
  copyContent: "copy-content",
  deleteMessage: "delete-message",
  endpointUrl: "endpoint-url",
  maxTokens: "max-tokens",
  polling: "polling",
  regenerate: "regenerate",
  prompt: "prompt",
  send: "send",
  settings: "settings",
  stt: "stt",
  system: "system",
  temperature: "temperature",
  toolbar: "toolbar"
};
const LF_CHAT_PROPS = [
  "lfContextWindow",
  "lfEmpty",
  "lfEndpointUrl",
  "lfLayout",
  "lfMaxTokens",
  "lfPollingInterval",
  "lfSeed",
  "lfStyle",
  "lfSystem",
  "lfTemperature",
  "lfTypewriterProps",
  "lfUiSize",
  "lfValue"
];
const LF_CHIP_CSS_VARS = {
  indentOffset: "--lf_chip_indent_offset"
};
const LF_CHIP_BLOCKS = {
  chip: { _: "chip", node: "node" },
  item: {
    _: "item",
    checkmark: "checkmark",
    checkmarkPath: "checkmark-path",
    checkmarkSvg: "checkmark-svg",
    icon: "icon",
    indent: "indent",
    primaryAction: "primary-action",
    text: "text"
  },
  wrapper: {
    _: "wrapper",
    indent: "indent",
    node: "node"
  }
};
const LF_CHIP_PARTS = {
  chip: "chip",
  indent: "indent",
  item: "item"
};
const LF_CHIP_PROPS = [
  "lfAriaLabel",
  "lfDataset",
  "lfRipple",
  "lfStyle",
  "lfStyling",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_CODE_BLOCKS = {
  code: { _: "code", header: "header", title: "title" }
};
const LF_CODE_PARTS = {
  code: "code",
  copy: "copy",
  header: "header",
  prism: "prism",
  title: "title"
};
const LF_CODE_PROPS = [
  "lfFadeIn",
  "lfFormat",
  "lfLanguage",
  "lfPreserveSpaces",
  "lfShowCopy",
  "lfShowHeader",
  "lfStickyHeader",
  "lfStyle",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_COMPARE_CSS_VARS = {
  overlayWidth: "--lf_compare_overlay_width"
};
const LF_COMPARE_BLOCKS = {
  compare: { _: "compare", grid: "grid" },
  toolbar: {
    _: "toolbar",
    panel: "panel"
  },
  view: {
    _: "view",
    input: "input",
    left: "left",
    right: "right",
    slider: "slider"
  }
};
const LF_COMPARE_DEFAULTS = () => {
  return {
    left: {
      image: () => [
        {
          htmlProps: {
            dataset: {
              lf: LF_ATTRIBUTES.fadeIn
            }
          },
          lfSizeX: "100%",
          lfSizeY: "100%",
          shape: "image",
          value: ""
        }
      ]
    },
    right: {
      image: () => [
        {
          htmlProps: {
            dataset: {
              lf: LF_ATTRIBUTES.fadeIn
            }
          },
          lfSizeX: "100%",
          lfSizeY: "100%",
          shape: "image",
          value: ""
        }
      ]
    }
  };
};
const LF_COMPARE_IDS = {
  leftButton: "toggle-left-button",
  leftTree: "toggle-left-tree",
  rightButton: "toggle-right-button",
  rightTree: "toggle-right-tree",
  changeView: "change-view"
};
const LF_COMPARE_PARTS = {
  changeView: "changeView",
  compare: "compare",
  leftButton: "leftButton",
  leftTree: "leftTree",
  rightButton: "rightButton",
  rightTree: "rightTree"
};
const LF_COMPARE_PROPS = [
  "lfDataset",
  "lfShape",
  "lfStyle",
  "lfView"
];
const LF_DRAWER_BLOCKS = {
  drawer: { _: "drawer", content: "content" }
};
const LF_DRAWER_PARTS = {
  content: "content",
  drawer: "drawer"
};
const LF_DRAWER_PROPS = [
  "lfDisplay",
  "lfPosition",
  "lfResponsive",
  "lfStyle",
  "lfValue"
];
const LF_DRAWER_SLOT = "content";
const LF_HEADER_BLOCKS = {
  header: { _: "header", section: "section" }
};
const LF_HEADER_PARTS = {
  header: "header",
  section: "section"
};
const LF_HEADER_PROPS = [
  "lfStyle"
];
const LF_HEADER_SLOT = "content";
const LF_IMAGE_CSS_VARS = {
  brokenImage: "--lf_broken_image",
  height: "--lf_image_height",
  mask: "--lf_image_mask",
  width: "--lf_image_width"
};
const LF_IMAGE_BLOCKS = {
  image: { _: "image", icon: "icon", img: "img" }
};
const LF_IMAGE_PARTS = {
  icon: "icon",
  image: "image",
  img: "img"
};
const LF_IMAGE_PROPS = [
  "lfHtmlAttributes",
  "lfSizeX",
  "lfSizeY",
  "lfStyle",
  "lfUiState",
  "lfValue",
  "lfMode"
];
const LF_IMAGEVIEWER_BLOCKS = {
  detailsGrid: {
    _: "details-grid",
    actions: "actions",
    canvas: "canvas",
    clearHistory: "clear-history",
    delete: "delete",
    redo: "details-redo",
    commitChanges: "commit-changes",
    preview: "preview",
    settings: "settings",
    spinner: "spinner",
    tree: "tree",
    undo: "undo"
  },
  imageviewer: { _: "imageviewer" },
  mainGrid: { _: "main-grid" },
  navigationGrid: {
    _: "navigation-grid",
    button: "button",
    masonry: "masonry",
    navToggle: "nav-toggle",
    tree: "tree",
    textfield: "textfield"
  }
};
const IDS = {
  details: {
    canvas: "details-canvas",
    clearHistory: "details-clear-history",
    deleteShape: "details-delete-shape",
    redo: "details-redo",
    save: "details-save",
    spinner: "details-spinner",
    tree: "details-tree",
    undo: "details-undo"
  },
  navigation: {
    load: "navigation-load",
    masonry: "navigation-masonry",
    navToggle: "navigation-nav-toggle",
    tree: "navigation-tree",
    textfield: "navigation-textfield"
  }
};
const LF_IMAGEVIEWER_PARTS = {
  details: "details",
  imageviewer: "imageviewer",
  navigation: "navigation"
};
const LF_IMAGEVIEWER_PROPS = [
  "lfDataset",
  "lfLoadCallback",
  "lfNavigation",
  "lfStyle",
  "lfValue"
];
const LF_LIST_BLOCKS = {
  delete: { _: "delete", icon: "icon" },
  emptyData: { _: "empty-data", text: "text" },
  list: { _: "list", item: "item" },
  node: {
    _: "node",
    icon: "icon",
    subtitle: "subtitle",
    text: "text",
    title: "title"
  }
};
const LF_LIST_PARTS = {
  delete: "delete",
  emptyData: "empty-data",
  list: "list",
  node: "node"
};
const LF_LIST_PROPS = [
  "lfDataset",
  "lfEmpty",
  "lfEnableDeletions",
  "lfNavigation",
  "lfRipple",
  "lfSelectable",
  "lfStyle",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_MASONRY_CSS_VARS = { columns: "--lf_masonry_columns" };
const LF_MASONRY_BLOCKS = {
  grid: {
    _: "grid",
    actions: "actions",
    addColumn: "add-column",
    changeViewe: "change-view",
    column: "column",
    removeColumn: "remove-column",
    sub: "sub"
  },
  masonry: { _: "masonry" }
};
const LF_MASONRY_DEFAULT_COLUMNS = [640, 768, 1024, 1920, 2560];
const LF_MASONRY_IDS = {
  addColumn: "add-column",
  masonry: "masonry",
  removeColumn: "remove-column"
};
const LF_MASONRY_PARTS = {
  addColumn: "add-column",
  changeView: "change-view",
  masonry: "masonry",
  removeColumn: "remove-column"
};
const LF_MASONRY_PROPS = [
  "lfActions",
  "lfColumns",
  "lfDataset",
  "lfSelectable",
  "lfShape",
  "lfStyle",
  "lfView"
];
const LF_MESSENGER_BLOCKS = {
  character: {
    _: "character",
    avatar: "avatar",
    biography: "biography",
    image: "image",
    label: "label",
    name: "name",
    nameWrapper: "name-wrapper",
    status: "status"
  },
  chat: {
    _: "chat",
    chat: "chat",
    expander: "expander",
    navigation: "navigation"
  },
  covers: {
    _: "covers",
    add: "add",
    images: "images",
    label: "label",
    title: "title"
  },
  extraContext: {
    _: "extra-context",
    list: "list",
    options: "options"
  },
  form: {
    _: "form",
    button: "button",
    confirm: "confirm",
    field: "field",
    label: "label"
  },
  list: {
    _: "list",
    actions: "actions",
    image: "image"
  },
  messenger: { _: "messenger" },
  options: {
    _: "options",
    blocker: "blocker",
    blockerIcon: "blocker-icon",
    blockerLabel: "blocker-label",
    cover: "cover",
    info: "info",
    label: "label",
    name: "name",
    placeholder: "placeholder",
    placeholderIcon: "placeholder-icon",
    wrapper: "wrapper"
  },
  roster: {
    _: "roster",
    emptyData: "empty-data",
    image: "image",
    label: "label",
    name: "name",
    portrait: "portrait"
  }
};
const LF_MESSENGER_CLEAN_UI = () => {
  return {
    customizationView: false,
    filters: {
      avatars: false,
      locations: false,
      outfits: false,
      styles: false,
      timeframes: false
    },
    form: {
      avatars: false,
      locations: false,
      outfits: false,
      styles: false,
      timeframes: false
    },
    options: {
      locations: true,
      outfits: true,
      styles: true,
      timeframes: true
    },
    panels: {
      isLeftCollapsed: false,
      isRightCollapsed: false
    }
  };
};
const LF_MESSENGER_PARTS = {
  emptyData: "empty-data",
  messenger: "messenger",
  roster: "roster"
};
const LF_MESSENGER_PROPS = [
  "lfAutosave",
  "lfDataset",
  "lfStyle",
  "lfValue"
];
const LF_MESSENGER_IDS = {
  chat: {
    leftExpander: "left-expander",
    rightExpander: "right-expaner"
  },
  options: {
    back: "back-button",
    customize: "customize-button"
  }
};
const AVATAR_COVER = "id";
const LOCATION_COVER = "sunset-2";
const OUTFIT_COVER = "shirt";
const STYLE_COVER = "color-swatch";
const TIMEFRAME_COVER = "calendar-clock";
const LF_MESSENGER_FILTER = {
  nodes: [
    {
      description: "View avatars",
      icon: AVATAR_COVER,
      id: "avatars",
      value: "Avatars"
    },
    {
      description: "View outfits",
      icon: OUTFIT_COVER,
      id: "outfits",
      value: "Outfits"
    },
    {
      description: "View locations",
      icon: LOCATION_COVER,
      id: "locations",
      value: "Locations"
    },
    {
      description: "View styles",
      icon: STYLE_COVER,
      id: "styles",
      value: "Styles"
    },
    {
      description: "View timeframes",
      icon: TIMEFRAME_COVER,
      id: "timeframes",
      value: "Timeframes"
    }
  ]
};
const LF_MESSENGER_MENU = (theme) => {
  const { "--lf-icon-download": download, "--lf-icon-settings": settings } = theme.get.current().variables;
  return {
    nodes: [
      {
        children: [
          {
            description: "Download the LF Widgets JSON, used as a dataset.",
            icon: download,
            id: "lfDataset",
            value: "Download dataset"
          },
          {
            description: "Download the current configuration settings.",
            icon: settings,
            id: "settings",
            value: "Download configuration"
          }
        ],
        id: "root",
        value: ""
      }
    ]
  };
};
const CHILD_ROOT_MAP = {
  avatar: "avatars",
  location: "locations",
  outfit: "outfits",
  style: "styles",
  timeframe: "timeframes"
};
const OPTION_TYPE_IDS = [
  "locations",
  "outfits",
  "styles",
  "timeframes"
];
const IMAGE_TYPE_IDS = ["avatars", ...OPTION_TYPE_IDS];
const LF_MESSENGER_NAV = (theme) => {
  const { "--lf-icon-next": next, "--lf-icon-previous": previous } = theme.get.current().variables;
  return {
    nodes: [
      {
        description: "Previous character",
        icon: previous,
        id: "previous",
        value: ""
      },
      {
        description: "Character selection",
        id: "character_list",
        value: "Character list"
      },
      {
        description: "Next character",
        icon: next,
        id: "next",
        value: ""
      }
    ]
  };
};
const LF_PHOTOFRAME_BLOCKS = {
  overlay: {
    _: "overlay",
    content: "content",
    description: "description",
    icon: "icon",
    title: "title"
  },
  photoframe: {
    _: "photoframe",
    image: "image",
    placeholder: "placeholder"
  }
};
const LF_PHOTOFRAME_PARTS = {
  description: "description",
  icon: "icon",
  image: "image",
  overlay: "overlay",
  photoframe: "photoframe",
  placeholder: "placeholder",
  title: "title"
};
const LF_PHOTOFRAME_PROPS = [
  "lfOverlay",
  "lfPlaceholder",
  "lfStyle",
  "lfThreshold",
  "lfValue"
];
const LF_PLACEHOLDER_BLOCKS = {
  placeholder: { _: "placeholder", icon: "icon" }
};
const LF_PLACEHOLDER_PARTS = {
  icon: "icon",
  placeholder: "placeholder"
};
const LF_PLACEHOLDER_PROPS = [
  "lfValue",
  "lfProps",
  "lfTrigger",
  "lfIcon",
  "lfStyle",
  "lfThreshold"
];
const LF_PROGRESSBAR_CSS_VARIABLES = {
  transform: "--lf_progressbar_transform",
  width: "--lf_progressbar_percentage_width"
};
const LF_PROGRESSBAR_BLOCKS = {
  pie: { _: "pie", halfCircle: "half-circle", track: "track" },
  progressbar: {
    _: "progressbar",
    icon: "icon",
    label: "label",
    mu: "mu",
    percentage: "percentage",
    text: "text"
  }
};
const LF_PROGRESSBAR_PARTS = {
  icon: "icon",
  label: "label",
  mu: "mu",
  percentage: "percentage",
  progressbar: "progressbar",
  text: "text",
  track: "track"
};
const LF_PROGRESSBAR_PROPS = [
  "lfAnimated",
  "lfCenteredLabel",
  "lfIcon",
  "lfIsRadial",
  "lfLabel",
  "lfStyle",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_SLIDER_CSS_VARIABLES = {
  value: "--lf_slider_value"
};
const LF_SLIDER_BLOCKS = {
  formField: {
    _: "form-field",
    label: "label"
  },
  slider: {
    _: "slider",
    nativeControl: "native-control",
    thumb: "thumb",
    thumbUnderlay: "thumb-underlay",
    track: "track",
    value: "value"
  }
};
const LF_SLIDER_PARTS = {
  formField: "form-field",
  label: "label",
  nativeControl: "native-control",
  slider: "slider",
  thumb: "thumb",
  thumbUnderlay: "thumb-underlay",
  track: "track",
  value: "value"
};
const LF_SLIDER_PROPS = [
  "lfLabel",
  "lfLeadingLabel",
  "lfMax",
  "lfMin",
  "lfRipple",
  "lfStep",
  "lfStyle",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_SPINNER_PROPS = [
  "lfActive",
  "lfBarVariant",
  "lfDimensions",
  "lfFader",
  "lfFaderTimeout",
  "lfFullScreen",
  "lfLayout",
  "lfStyle",
  "lfTimeout"
];
const LF_SPLASH_BLOCKS = {
  splash: {
    _: "splash",
    content: "content",
    label: "label",
    widget: "widget"
  }
};
const LF_SPLASH_PARTS = {
  content: "content",
  label: "label",
  splash: "splash",
  widget: "widget"
};
const LF_SPLASH_PROPS = [
  "lfLabel",
  "lfStyle"
];
const LF_TABBAR_BLOCKS = {
  tab: {
    _: "tab",
    content: "content",
    icon: "icon",
    indicator: "indicator",
    indicatorContent: "indicator-content",
    label: "label"
  },
  tabbar: {
    _: "tabbar",
    scroll: "scroll"
  }
};
const LF_TABBAR_PARTS = {
  tab: "tab",
  tabbbar: "tabbar"
};
const LF_TABBAR_PROPS = [
  "lfAriaLabel",
  "lfDataset",
  "lfNavigation",
  "lfRipple",
  "lfStyle",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_TEXTFIELD_BLOCKS = {
  notchedOutline: {
    _: "notched-outline",
    leading: "leading",
    notch: "notch",
    trailing: "trailing"
  },
  textfield: {
    _: "textfield",
    counter: "counter",
    helperLine: "helper-line",
    helperText: "helper-text",
    icon: "icon",
    input: "input",
    label: "label",
    resizer: "resizer",
    rippleSurface: "ripple-surface"
  }
};
const LF_TEXTFIELD_PARTS = {
  counter: "counter",
  icon: "icon",
  input: "input",
  label: "label",
  textfield: "textfield"
};
const LF_TEXTFIELD_PROPS = [
  "lfHelper",
  "lfHtmlAttributes",
  "lfIcon",
  "lfLabel",
  "lfStretchY",
  "lfStyle",
  "lfStyling",
  "lfTrailingIcon",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_TOAST_CSS_VARIABLES = {
  timer: "--lf_toast_timer"
};
const LF_TOAST_BLOCKS = {
  toast: {
    _: "toast",
    accent: "accent",
    icon: "icon",
    message: "message",
    messageWrapper: "message-wrapper"
  }
};
const LF_TOAST_PARTS = {
  icon: "icon",
  message: "message"
};
const LF_TOAST_PROPS = [
  "lfCloseCallback",
  "lfCloseIcon",
  "lfIcon",
  "lfMessage",
  "lfStyle",
  "lfTimer",
  "lfUiSize",
  "lfUiState"
];
const LF_TOGGLE_BLOCKS = {
  formField: {
    _: "form-field",
    label: "label"
  },
  toggle: {
    _: "toggle",
    label: "label",
    nativeControl: "native-control",
    thumb: "thumb",
    thumbUnderlay: "thumb-underlay",
    track: "track"
  }
};
const LF_TOGGLE_PARTS = {
  label: "label",
  nativeControl: "native-control",
  toggle: "toggle",
  thumb: "thumb",
  track: "track"
};
const LF_TOGGLE_PROPS = [
  "lfAriaLabel",
  "lfLabel",
  "lfLeadingLabel",
  "lfRipple",
  "lfStyle",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_TREE_CSS_VARIABLES = {
  multiplier: "--lf_tree_padding_multiplier"
};
const LF_TREE_BLOCKS = {
  emptyData: { _: "empty-data", text: "text" },
  node: {
    _: "node",
    content: "content",
    dropdown: "dropdown",
    expand: "expand",
    icon: "icon",
    padding: "padding",
    value: "value",
    grid: "grid",
    gridCell: "grid-cell"
  },
  noMatches: { _: "no-matches", filter: "filter", icon: "icon", text: "text" },
  tree: {
    _: "tree",
    filter: "filter",
    nodesWrapper: "nodes-wrapper",
    header: "header"
  },
  header: { _: "header", row: "row", cell: "cell" }
};
const LF_TREE_PARTS = {
  emptyData: "empty-data",
  node: "node",
  header: "header",
  headerRow: "header-row",
  tree: "tree"
};
const LF_TREE_PROPS = [
  "lfAccordionLayout",
  "lfDataset",
  "lfEmpty",
  "lfExpandedNodeIds",
  "lfFilter",
  "lfGrid",
  "lfInitialExpansionDepth",
  "lfRipple",
  "lfSelectable",
  "lfSelectedNodeIds",
  "lfStyle",
  "lfUiSize"
];
const LF_TYPEWRITER_BLOCKS = {
  typewriter: {
    _: "typewriter",
    cursor: "cursor",
    text: "text"
  }
};
const LF_TYPEWRITER_PARTS = {
  cursor: "cursor",
  text: "text",
  typewriter: "typewriter"
};
const LF_TYPEWRITER_PROPS = [
  "lfCursor",
  "lfDeleteSpeed",
  "lfLoop",
  "lfPause",
  "lfSpeed",
  "lfStyle",
  "lfTag",
  "lfUpdatable",
  "lfValue"
];
const LF_UPLOAD_BLOCKS = {
  fileInfo: {
    _: "file-info",
    clear: "clear",
    icon: "icon",
    item: "item",
    name: "name",
    size: "size"
  },
  fileUpload: {
    _: "file-upload",
    input: "input",
    label: "label",
    text: "text"
  },
  upload: { _: "upload" }
};
const LF_UPLOAD_PARTS = {
  fileInfo: "file-info",
  icon: "icon",
  upload: "upload"
};
const LF_UPLOAD_PROPS = [
  "lfLabel",
  "lfRipple",
  "lfStyle",
  "lfValue"
];
const CSS_VAR_PREFIX = "--lf-";
const CY_ATTRIBUTES = {
  button: "button",
  canvas: "canvas",
  check: "check",
  dropdownButton: "dropdown-button",
  dropdownMenu: "dropdown-menu",
  effects: "effects",
  icon: "icon",
  image: "image",
  input: "input",
  maskedSvg: "masked-svg",
  node: "node",
  portal: "portal",
  rippleSurface: "ripple-surface",
  shape: "shape",
  showcaseExample: "showcase-example",
  showcaseGridWrapper: "showcase-grid-wrapper"
};
const LF_ATTRIBUTES = {
  backdrop: "backdrop",
  danger: "danger",
  disabled: "disabled",
  fadeIn: "fade-in",
  icon: "icon",
  info: "info",
  lightbox: "lightbox",
  lightboxContent: "lightbox-content",
  portal: "portal",
  primary: "primary",
  ripple: "ripple",
  rippleSurface: "ripple-surface",
  secondary: "secondary",
  success: "success",
  tilt: "tilt",
  warning: "warning"
};
const LF_STYLE_ID = "lf-style";
const LF_WRAPPER_ID = "lf-component";
const getComponentProps = () => {
  return {
    LfAccordion: LF_ACCORDION_PROPS,
    LfArticle: LF_ARTICLE_PROPS,
    LfBadge: LF_BADGE_PROPS,
    LfButton: LF_BUTTON_PROPS,
    LfCanvas: LF_CANVAS_PROPS,
    LfCard: LF_CARD_PROPS,
    LfCarousel: LF_CAROUSEL_PROPS,
    LfChart: LF_CHART_PROPS,
    LfChat: LF_CHAT_PROPS,
    LfChip: LF_CHIP_PROPS,
    LfCode: LF_CODE_PROPS,
    LfCompare: LF_COMPARE_PROPS,
    LfDrawer: LF_DRAWER_PROPS,
    LfHeader: LF_HEADER_PROPS,
    LfImage: LF_IMAGE_PROPS,
    LfImageviewer: LF_IMAGEVIEWER_PROPS,
    LfList: LF_LIST_PROPS,
    LfMasonry: LF_MASONRY_PROPS,
    LfMessenger: LF_MESSENGER_PROPS,
    LfPhotoframe: LF_PHOTOFRAME_PROPS,
    LfPlaceholder: LF_PLACEHOLDER_PROPS,
    LfProgressbar: LF_PROGRESSBAR_PROPS,
    LfSlider: LF_SLIDER_PROPS,
    LfSpinner: LF_SPINNER_PROPS,
    LfSplash: LF_SPLASH_PROPS,
    LfTabbar: LF_TABBAR_PROPS,
    LfTextfield: LF_TEXTFIELD_PROPS,
    LfToast: LF_TOAST_PROPS,
    LfToggle: LF_TOGGLE_PROPS,
    LfTree: LF_TREE_PROPS,
    LfTypewriter: LF_TYPEWRITER_PROPS,
    LfUpload: LF_UPLOAD_PROPS
  };
};
const LF_CARD_CSS_VARS = {
  height: "--lf_card_height",
  width: "--lf_card_width"
};
const LF_CARD_BLOCKS = {
  card: "card",
  debugLayout: {
    _: "debug-layout",
    section1: "section-1",
    section2: "section-2",
    section3: "section-3",
    section4: "section-4"
  },
  keywordsLayout: {
    _: "keywords-layout",
    section1: "section-1",
    section2: "section-2",
    section3: "section-3"
  },
  materialLayout: {
    _: "material-layout",
    actionsSection: "actions-section",
    coverSection: "cover-section",
    textSection: "text-section"
  },
  textContent: {
    _: "text-content",
    title: "title",
    subtitle: "subtitle",
    description: "description"
  },
  uploadLayout: {
    _: "upload-layout",
    section1: "section-1",
    section2: "section-2"
  }
};
const LF_CARD_DEFAULTS = (getAdapter) => {
  return {
    debug: {
      button: () => {
        const { current, themes } = getAdapter().controller.get.manager.theme.get;
        const { "--lf-icon-clear": clear } = current().variables;
        return [
          {
            htmlProps: {
              id: LF_CARD_IDS.clear
            },
            lfIcon: clear,
            lfLabel: "Clear logs",
            lfStretchX: true,
            lfUiState: "danger",
            shape: "button",
            value: ""
          },
          {
            htmlProps: {
              id: LF_CARD_IDS.theme
            },
            lfDataset: themes().asDataset,
            lfStretchX: true,
            shape: "button",
            value: ""
          }
        ];
      },
      code: () => [
        { lfLanguage: "markdown", shape: "code", value: "" }
      ],
      toggle: () => {
        const { debug } = getAdapter().controller.get.manager;
        return [
          {
            lfLeadingLabel: true,
            lfLabel: "Toggle debug",
            lfValue: debug.isEnabled(),
            shape: "toggle",
            value: false
          }
        ];
      }
    },
    keywords: {
      button: () => {
        const { "--lf-icon-copy": copy } = getAdapter().controller.get.manager.theme.get.current().variables;
        return [
          {
            lfIcon: copy,
            lfLabel: "Copy selected",
            lfStretchX: true,
            lfStyling: "flat",
            shape: "button",
            value: ""
          }
        ];
      },
      chart: () => [
        {
          lfLegend: "hidden",
          lfTypes: ["bar"],
          shape: "chart",
          value: ""
        }
      ],
      chip: () => [
        {
          lfStyle: "#lf-component .chip-set { height: auto; }",
          lfStyling: "filter",
          shape: "chip",
          value: ""
        }
      ]
    },
    material: {
      image: () => [
        {
          htmlProps: {
            dataset: { lf: LF_ATTRIBUTES.fadeIn }
          },
          lfSizeX: "100%",
          lfSizeY: "100%",
          shape: "image",
          value: ""
        }
      ]
    },
    upload: {
      button: () => [
        {
          lfIcon: "upload",
          lfLabel: "Upload",
          lfStretchX: true,
          shape: "button",
          value: ""
        }
      ]
    }
  };
};
const LF_CARD_IDS = {
  clear: "clear",
  theme: "theme"
};
const LF_CARD_PARTS = {
  card: "card",
  debugLayout: "debug-layout",
  keywordsLayout: "keywords-layout",
  materialLayout: "material-layout",
  uploadLayout: "upload-layout"
};
const LF_CARD_PROPS = [
  "lfDataset",
  "lfLayout",
  "lfSizeX",
  "lfSizeY",
  "lfStyle"
];
var LfMessengerProps;
(function(LfMessengerProps2) {
  LfMessengerProps2["lfAutosave"] = "Automatically saves the dataset when a chat updates.";
  LfMessengerProps2["lfDataset"] = "The actual data of the component.";
  LfMessengerProps2["lfStyle"] = "Custom style of the component.";
  LfMessengerProps2["lfValue"] = "Sets the initial configuration, including active character and filters.";
})(LfMessengerProps || (LfMessengerProps = {}));
const LF_COLOR_CODES = {
  aliceblue: "#f0f8ff",
  antiquewhite: "#faebd7",
  aqua: "#00ffff",
  aquamarine: "#7fffd4",
  azure: "#f0ffff",
  beige: "#f5f5dc",
  bisque: "#ffe4c4",
  black: "#000000",
  blanchedalmond: "#ffebcd",
  blue: "#0000ff",
  blueviolet: "#8a2be2",
  brown: "#a52a2a",
  burlywood: "#deb887",
  cadetblue: "#5f9ea0",
  chartreuse: "#7fff00",
  chocolate: "#d2691e",
  coral: "#ff7f50",
  cornflowerblue: "#6495ed",
  cornsilk: "#fff8dc",
  crimson: "#dc143c",
  cyan: "#00ffff",
  darkblue: "#00008b",
  darkcyan: "#008b8b",
  darkgoldenrod: "#b8860b",
  darkgray: "#a9a9a9",
  darkgreen: "#006400",
  darkgrey: "#a9a9a9",
  darkkhaki: "#bdb76b",
  darkmagenta: "#8b008b",
  darkolivegreen: "#556b2f",
  darkorange: "#ff8c00",
  darkorchid: "#9932cc",
  darkred: "#8b0000",
  darksalmon: "#e9967a",
  darkseagreen: "#8fbc8f",
  darkslateblue: "#483d8b",
  darkslategray: "#2f4f4f",
  darkslategrey: "#2f4f4f",
  darkturquoise: "#00ced1",
  darkviolet: "#9400d3",
  deeppink: "#ff1493",
  deepskyblue: "#00bfff",
  dimgray: "#696969",
  dimgrey: "#696969",
  dodgerblue: "#1e90ff",
  firebrick: "#b22222",
  floralwhite: "#fffaf0",
  forestgreen: "#228b22",
  fuchsia: "#ff00ff",
  gainsboro: "#dcdcdc",
  ghostwhite: "#f8f8ff",
  goldenrod: "#daa520",
  gold: "#ffd700",
  gray: "#808080",
  green: "#008000",
  greenyellow: "#adff2f",
  grey: "#808080",
  honeydew: "#f0fff0",
  hotpink: "#ff69b4",
  indianred: "#cd5c5c",
  indigo: "#4b0082",
  ivory: "#fffff0",
  khaki: "#f0e68c",
  lavenderblush: "#fff0f5",
  lavender: "#e6e6fa",
  lawngreen: "#7cfc00",
  lemonchiffon: "#fffacd",
  lightblue: "#add8e6",
  lightcoral: "#f08080",
  lightcyan: "#e0ffff",
  lightgoldenrodyellow: "#fafad2",
  lightgray: "#d3d3d3",
  lightgreen: "#90ee90",
  lightgrey: "#d3d3d3",
  lightpink: "#ffb6c1",
  lightsalmon: "#ffa07a",
  lightseagreen: "#20b2aa",
  lightskyblue: "#87cefa",
  lightslategray: "#778899",
  lightslategrey: "#778899",
  lightsteelblue: "#b0c4de",
  lightyellow: "#ffffe0",
  lime: "#00ff00",
  limegreen: "#32cd32",
  linen: "#faf0e6",
  magenta: "#ff00ff",
  maroon: "#800000",
  mediumaquamarine: "#66cdaa",
  mediumblue: "#0000cd",
  mediumorchid: "#ba55d3",
  mediumpurple: "#9370db",
  mediumseagreen: "#3cb371",
  mediumslateblue: "#7b68ee",
  mediumspringgreen: "#00fa9a",
  mediumturquoise: "#48d1cc",
  mediumvioletred: "#c71585",
  midnightblue: "#191970",
  mintcream: "#f5fffa",
  mistyrose: "#ffe4e1",
  moccasin: "#ffe4b5",
  navajowhite: "#ffdead",
  navy: "#000080",
  oldlace: "#fdf5e6",
  olive: "#808000",
  olivedrab: "#6b8e23",
  orange: "#ffa500",
  orangered: "#ff4500",
  orchid: "#da70d6",
  palegoldenrod: "#eee8aa",
  palegreen: "#98fb98",
  paleturquoise: "#afeeee",
  palevioletred: "#db7093",
  papayawhip: "#ffefd5",
  peachpuff: "#ffdab9",
  peru: "#cd853f",
  pink: "#ffc0cb",
  plum: "#dda0dd",
  powderblue: "#b0e0e6",
  purple: "#800080",
  rebeccapurple: "#663399",
  red: "#ff0000",
  rosybrown: "#bc8f8f",
  royalblue: "#4169e1",
  saddlebrown: "#8b4513",
  salmon: "#fa8072",
  sandybrown: "#f4a460",
  seagreen: "#2e8b57",
  seashell: "#fff5ee",
  sienna: "#a0522d",
  silver: "#c0c0c0",
  skyblue: "#87ceeb",
  slateblue: "#6a5acd",
  slategray: "#708090",
  slategrey: "#708090",
  snow: "#fffafa",
  springgreen: "#00ff7f",
  steelblue: "#4682b4",
  tan: "#d2b48c",
  teal: "#008080",
  thistle: "#d8bfd8",
  tomato: "#ff6347",
  turquoise: "#40e0d0",
  violet: "#ee82ee",
  wheat: "#f5deb3",
  white: "#ffffff",
  whitesmoke: "#f5f5f5",
  yellow: "#ffff00",
  yellowgreen: "#9acd32"
};
const LF_EFFECTS_FOCUSABLES = [
  "a[href]",
  "area[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "iframe",
  "[tabindex]:not([tabindex='-1'])",
  "[contenteditable]"
];
const LF_EFFECTS_VARS = {
  ripple: {
    background: "--lf-ui-ripple-background",
    height: "--lf-ui-ripple-height",
    width: "--lf-ui-ripple-width",
    x: "--lf-ui-ripple-x",
    y: "--lf-ui-ripple-y"
  },
  tilt: {
    x: "--lf-ui-tilt-x",
    y: "--lf-ui-tilt-y",
    lightX: "--lf-ui-tilt-light-x",
    lightY: "--lf-ui-tilt-light-y"
  }
};
const LF_FRAMEWORK_ALLOWED_ATTRS = [
  "alt",
  "autocomplete",
  "autofocus",
  "checked",
  "class",
  "dataset",
  "disabled",
  "href",
  "htmlProps",
  "id",
  "max",
  "maxLength",
  "min",
  "minLength",
  "multiple",
  "name",
  "placeholder",
  "readonly",
  "role",
  "src",
  "srcset",
  "step",
  "title",
  "type",
  "value"
];
const LF_FRAMEWORK_ALLOWED_PREFIXES = ["aria", "data"];
const LF_FRAMEWORK_EVENT_NAME = "lf-core-event";
const LF_FRAMEWORK_SYMBOL_KEY = "__LfFramework__";
const LF_FRAMEWORK_SYMBOL = Symbol.for(LF_FRAMEWORK_SYMBOL_KEY);
let _resolveFrameworkReady = null;
const onFrameworkReady = new Promise((resolve) => {
  _resolveFrameworkReady = resolve;
});
function markFrameworkReady(framework) {
  if (_resolveFrameworkReady) {
    _resolveFrameworkReady(framework);
    _resolveFrameworkReady = null;
  }
}
const LF_THEME_COLORS_PREFIX = "--lf-color-";
const LF_THEME_COLORS_DATA_PREFIX = `${LF_THEME_COLORS_PREFIX}data-`;
const LF_THEME_FONTS_FONTFACE = {
  bebasNeue: "BebasNeue",
  cinzel: "Cinzel",
  IMFellEnglishSC: "IMFellEnglishSC",
  lato: "Lato",
  merriweather: "Merriweather",
  montserrat: "Montserrat",
  orbitron: "Orbitron",
  oswald: "Oswald",
  raleway: "Raleway",
  sawarabiMincho: "SawarabiMincho",
  shareTechMono: "ShareTechMono",
  sourceCodePro: "SourceCodePro",
  staatliches: "Staatliches",
  uncialAntiqua: "UncialAntiqua",
  vt323: "VT323",
  xanhMono: "XanhMono"
};
const LF_THEME_UI_PREFIX = "--lf-ui-";
const LF_THEME_UI_SIZES = [
  "large",
  "medium",
  "small",
  "xlarge",
  "xsmall",
  "xxlarge",
  "xxsmall"
];
({
  ...LF_THEME_UI_SIZES.reduce((acc, size) => {
    acc[size] = `${LF_THEME_UI_PREFIX}size-${size}`;
    return acc;
  }, {})
});
const LF_THEME_ICONS_PREFIX = "--lf-icon-";
const LF_THEME_ICONS = {
  dropdown: `${LF_THEME_ICONS_PREFIX}dropdown`
};
const LF_THEME_ATTRIBUTE = {
  dark: "lf-dark-theme",
  light: "lf-light-theme",
  theme: "lf-theme"
};
const LF_THEME_BASE_VARS = {
  "--lf-color-danger": "#d91e18",
  "--lf-color-info": "#2592df",
  "--lf-color-on-danger": "#fefefe",
  "--lf-color-on-info": "#4a4a4a",
  "--lf-color-on-success": "#fefefe",
  "--lf-color-on-warning": "#151515",
  "--lf-color-success": "#4d9f02",
  "--lf-color-warning": "#ffc107",
  "--lf-font-family-monospace": "Xanh Mono, monospace",
  "--lf-font-family-primary": "Oswald, sans-serif",
  "--lf-font-family-secondary": "Oswald, sans-serif",
  "--lf-font-size": "16px",
  "--lf-icon-add": `hexagon-plus`,
  "--lf-icon-broken-image": `photo-x`,
  "--lf-icon-clear": `x`,
  "--lf-icon-collapsed": `chevron-right`,
  "--lf-icon-copy": `copy`,
  "--lf-icon-copy-ok": `copy-check`,
  "--lf-icon-danger": `square-x`,
  "--lf-icon-delete": `square-x`,
  "--lf-icon-disabled": `lock`,
  "--lf-icon-download": `download`,
  "--lf-icon-dropdown": `chevron-down`,
  "--lf-icon-edit": `edit`,
  "--lf-icon-expanded": `chevron-down`,
  "--lf-icon-info": `info-hexagon`,
  "--lf-icon-minus": `hexagon-minus`,
  "--lf-icon-next": `chevron-right`,
  "--lf-icon-plus": `hexagon-plus`,
  "--lf-icon-previous": `chevron-left`,
  "--lf-icon-primary": `lf-website`,
  "--lf-icon-refresh": `refresh`,
  "--lf-icon-search": `search`,
  "--lf-icon-secondary": `lf-signature`,
  "--lf-icon-settings": `settings`,
  "--lf-icon-success": `check`,
  "--lf-icon-upload": `upload`,
  "--lf-icon-warning": `alert-triangle`,
  "--lf-ui-border-radius": "0",
  "--lf-ui-box-shadow-modal": "0px 0px 7.5px 0px rgba(128, 128, 128, 0.5)",
  "--lf-ui-duration-ripple": "750ms",
  "--lf-ui-height-header": "80px",
  "--lf-ui-opacity-disabled": 0.6,
  "--lf-ui-opacity-ripple": 0.275,
  "--lf-ui-radius-ripple": "0",
  "--lf-ui-size-large": 1.15,
  "--lf-ui-size-medium": 1,
  "--lf-ui-size-small": 0.85,
  "--lf-ui-size-xlarge": 1.25,
  "--lf-ui-size-xsmall": 0.75,
  "--lf-ui-size-xxlarge": 1.35,
  "--lf-ui-size-xxsmall": 0.65,
  "--lf-ui-timing-ripple": "cubic-bezier(0.4, 0, 0.2, 1)",
  "--lf-ui-width-drawer": "320px",
  "--lf-ui-zindex-backdrop": 899,
  "--lf-ui-zindex-drawer": 900,
  "--lf-ui-zindex-header": 898,
  "--lf-ui-zindex-lightbox": 901,
  "--lf-ui-zindex-portal": 997,
  "--lf-ui-zindex-splash": 999,
  "--lf-ui-zindex-toast": 998
};
const DARK = {
  font: [LF_THEME_FONTS_FONTFACE.oswald, LF_THEME_FONTS_FONTFACE.xanhMono],
  isDark: true,
  variables: {
    ...LF_THEME_BASE_VARS,
    "--lf-color-bg": "#000000",
    "--lf-color-border": "#323232",
    "--lf-color-data-1": "#67d6e2",
    //rgb(103, 214, 226)
    "--lf-color-data-2": "#ff88a8",
    //rgb(255, 136, 168)
    "--lf-color-data-3": "#c4fa79",
    //rgb(196, 250, 121)
    "--lf-color-data-4": "#ffad5b",
    //rgb(255, 173, 91)
    "--lf-color-data-5": "#ffd16d",
    //rgb(255, 209, 109)
    "--lf-color-data-6": "#ff7aed",
    //rgb(255, 122, 237)
    "--lf-color-data-7": "#7d99ff",
    //rgb(125, 153, 255)
    "--lf-color-drawer": "#151515",
    "--lf-color-header": "#151515",
    "--lf-color-link": "#2592df",
    "--lf-color-on-bg": "#fefefe",
    "--lf-color-on-border": "#fefefe",
    "--lf-color-on-drawer": "#fefefe",
    "--lf-color-on-header": "#fefefe",
    "--lf-color-on-info": "#fefefe",
    "--lf-color-on-link": "#4a4a4a",
    "--lf-color-on-primary": "#4a4a4a",
    "--lf-color-on-success": "#fefefe",
    "--lf-color-on-secondary": "#151515",
    "--lf-color-on-spinner": "#74cfc8",
    "--lf-color-on-surface": "#d9d9d9",
    "--lf-color-primary": "#c0c0c0",
    "--lf-color-secondary": "#60c1b8",
    "--lf-color-spinner": "#494949",
    "--lf-color-surface": "#151515"
  }
};
const LIGHT = {
  font: [LF_THEME_FONTS_FONTFACE.oswald, LF_THEME_FONTS_FONTFACE.xanhMono],
  isDark: false,
  variables: {
    ...LF_THEME_BASE_VARS,
    "--lf-color-bg": "#ffffff",
    "--lf-color-border": "#dcdcdc",
    "--lf-color-data-1": "#00c1d6",
    //rgb(0, 193, 214)
    "--lf-color-data-2": "#af002f",
    //rgb(175, 0, 47)
    "--lf-color-data-3": "#71c200",
    //rgb(113, 194, 0)
    "--lf-color-data-4": "#ce6700",
    //rgb(216, 143, 70)
    "--lf-color-data-5": "#d18f00",
    //rgb(209, 143, 0)
    "--lf-color-data-6": "#ca00af",
    //rgb(202, 0, 175)
    "--lf-color-data-7": "#0028b9",
    //rgb(0, 40, 185)
    "--lf-color-drawer": "#f8f8f8",
    "--lf-color-header": "#f8f8f8",
    "--lf-color-link": "#1d77b5",
    "--lf-color-on-bg": "#151515",
    "--lf-color-on-border": "#151515",
    "--lf-color-on-drawer": "#151515",
    "--lf-color-on-header": "#151515",
    "--lf-color-on-link": "#ffffff",
    "--lf-color-on-primary": "#fefefe",
    "--lf-color-on-secondary": "#fefefe",
    "--lf-color-on-spinner": "#4d8f89",
    "--lf-color-on-surface": "#151515",
    "--lf-color-primary": "#424242",
    "--lf-color-secondary": "#499499",
    "--lf-color-spinner": "#b3b3b3",
    "--lf-color-surface": "#fefefe"
  }
};
const ABYSS = {
  font: [
    LF_THEME_FONTS_FONTFACE.staatliches,
    LF_THEME_FONTS_FONTFACE.montserrat
  ],
  isDark: true,
  variables: {
    ...DARK.variables,
    "--lf-color-bg": "#081620",
    "--lf-color-border": "#103040",
    "--lf-color-surface": "#12212e",
    "--lf-color-on-surface": "#e5f4ff",
    "--lf-color-primary": "#00aecc",
    "--lf-color-on-primary": "#041013",
    "--lf-color-secondary": "#ff5370",
    "--lf-color-on-secondary": "#1a050c",
    "--lf-color-data-1": "#149cad",
    "--lf-color-data-2": "#ff7f9d",
    "--lf-color-data-3": "#1fdfc3",
    "--lf-color-data-4": "#1f99df",
    "--lf-color-data-5": "#75fdd3",
    "--lf-color-data-6": "#ffad9e",
    "--lf-color-data-7": "#3eddff",
    "--lf-color-on-bg": "#f0faff",
    "--lf-color-on-border": "#dff2ff",
    "--lf-color-link": "#00c5d4",
    "--lf-color-on-link": "#020809",
    "--lf-color-spinner": "#2a5060",
    "--lf-color-on-spinner": "#b3ecff",
    "--lf-ui-border-radius": "0.25em",
    "--lf-ui-radius-ripple": "50%",
    "--lf-font-size": "15px",
    "--lf-font-family-primary": "Staatliches, sans-serif",
    "--lf-font-family-monospace": "Montserrat, sans-serif"
  }
};
const ERIS = {
  font: [LF_THEME_FONTS_FONTFACE.oswald, LF_THEME_FONTS_FONTFACE.xanhMono],
  isDark: true,
  variables: {
    ...DARK.variables,
    "--lf-color-bg": "#0d0b1b",
    "--lf-color-border": "#2c2140",
    "--lf-color-surface": "#181427",
    "--lf-color-data-1": "#6d5dfc",
    "--lf-color-data-2": "#ff4499",
    "--lf-color-data-3": "#00d1ff",
    "--lf-color-data-4": "#ffcc66",
    "--lf-color-danger": "#ff3344",
    "--lf-color-success": "#00ff99",
    "--lf-color-info": "#3399ff",
    "--lf-color-link": "#836aff",
    "--lf-color-on-link": "#ffffff",
    "--lf-color-on-bg": "#f5f5f5",
    "--lf-color-on-surface": "#e2e2e2",
    "--lf-ui-box-shadow-modal": "0px 0px 15px rgba(109, 93, 252, 0.4)",
    "--lf-ui-opacity-ripple": 0.6,
    "--lf-ui-radius-ripple": "60%",
    "--lf-color-header": "#181427",
    "--lf-color-drawer": "#151024",
    "--lf-color-on-header": "#f0f0f0",
    "--lf-color-on-drawer": "#fefefe"
  }
};
const NEON = {
  font: [LF_THEME_FONTS_FONTFACE.orbitron, LF_THEME_FONTS_FONTFACE.vt323],
  isDark: true,
  variables: {
    ...DARK.variables,
    "--lf-color-bg": "#101010",
    "--lf-color-border": "#454545",
    "--lf-color-surface": "#1a1a1a",
    "--lf-color-on-surface": "#f0f0f0",
    "--lf-color-primary": "#00ffcc",
    "--lf-color-on-primary": "#050505",
    "--lf-color-secondary": "#ff2299",
    "--lf-color-on-secondary": "#0a0a0a",
    "--lf-color-data-1": "#00fdff",
    "--lf-color-data-2": "#ff0090",
    "--lf-color-data-3": "#00ff3e",
    "--lf-color-data-4": "#4f7eff",
    "--lf-color-data-5": "#d4ff00",
    "--lf-color-data-6": "#ff7a00",
    "--lf-color-data-7": "#bf00ff",
    "--lf-color-on-bg": "#fcfcfc",
    "--lf-color-on-border": "#fefefe",
    "--lf-color-link": "#00eaff",
    "--lf-color-on-link": "#000000",
    "--lf-color-spinner": "#333333",
    "--lf-color-on-spinner": "#00ff9e",
    "--lf-font-family-monospace": "VT323, monospace",
    "--lf-font-family-primary": "Orbitron, sans-serif",
    "--lf-font-size": "14px",
    "--lf-ui-border-radius": "0.5em",
    "--lf-ui-radius-ripple": "50%"
  }
};
const NIGHT = {
  font: [
    LF_THEME_FONTS_FONTFACE.bebasNeue,
    LF_THEME_FONTS_FONTFACE.shareTechMono
  ],
  isDark: true,
  variables: {
    ...DARK.variables,
    "--lf-color-bg": "#0a0a0a",
    "--lf-color-border": "#3f3f3f",
    "--lf-color-surface": "#141414",
    "--lf-color-on-surface": "#fafafa",
    "--lf-color-primary": "#00ffcc",
    "--lf-color-on-primary": "#111111",
    "--lf-color-secondary": "#ff00d4",
    "--lf-color-on-secondary": "#080808",
    "--lf-color-data-1": "#ff4300",
    "--lf-color-data-2": "#ff0080",
    "--lf-color-data-3": "#00ff5e",
    "--lf-color-data-4": "#0080ff",
    "--lf-color-data-5": "#aaff00",
    "--lf-color-data-6": "#ff8800",
    "--lf-color-data-7": "#da00ff",
    "--lf-color-on-bg": "#fefefe",
    "--lf-color-on-border": "#f1f1f1",
    "--lf-color-link": "#00aacc",
    "--lf-color-on-link": "#000000",
    "--lf-color-spinner": "#222222",
    "--lf-color-on-spinner": "#00ffa2",
    "--lf-font-family-monospace": "Share Tech Mono, monospace",
    "--lf-font-family-primary": "Bebas Neue, sans-serif",
    "--lf-ui-border-radius": "0.25em",
    "--lf-ui-radius-ripple": "50%"
  }
};
const PASTEL = {
  font: [
    LF_THEME_FONTS_FONTFACE.raleway,
    LF_THEME_FONTS_FONTFACE.sourceCodePro
  ],
  isDark: false,
  variables: {
    ...LIGHT.variables,
    "--lf-color-bg": "#fcfcfc",
    "--lf-color-border": "#cccccc",
    "--lf-color-surface": "#ffffff",
    "--lf-color-on-surface": "#151515",
    "--lf-color-primary": "#8a4881",
    "--lf-color-on-primary": "#1b1b1b",
    "--lf-color-secondary": "#ffcce7",
    "--lf-color-on-secondary": "#242424",
    "--lf-color-data-1": "#53969f",
    "--lf-color-data-2": "#af6161",
    "--lf-color-data-3": "#c99b58",
    "--lf-color-data-4": "#7eaa4c",
    "--lf-color-data-5": "#af8817",
    "--lf-color-data-6": "#a14f91",
    "--lf-color-data-7": "#5f6eb9",
    "--lf-color-on-bg": "#222222",
    "--lf-color-on-border": "#151515",
    "--lf-color-link": "#6f86c9",
    "--lf-color-on-link": "#ffffff",
    "--lf-color-spinner": "#aaaaaa",
    "--lf-color-on-spinner": "#333333",
    "--lf-font-family-monospace": "Source Code Pro, monospace",
    "--lf-font-family-primary": "Raleway, sans-serif",
    "--lf-ui-border-radius": "0.25em",
    "--lf-ui-radius-ripple": "50%"
  }
};
const SAKURA = {
  font: [
    LF_THEME_FONTS_FONTFACE.sawarabiMincho,
    LF_THEME_FONTS_FONTFACE.raleway
  ],
  isDark: false,
  variables: {
    ...LIGHT.variables,
    "--lf-color-bg": "#fef5f7",
    "--lf-color-border": "#f9d8db",
    "--lf-color-surface": "#fffafa",
    "--lf-color-on-surface": "#432d33",
    "--lf-color-primary": "#ff7394",
    "--lf-color-on-primary": "#3d1214",
    "--lf-color-secondary": "#ffd59c",
    "--lf-color-on-secondary": "#4e2e1b",
    "--lf-color-data-1": "#53969f",
    "--lf-color-data-2": "#af6161",
    "--lf-color-data-3": "#c99b58",
    "--lf-color-data-4": "#7eaa4c",
    "--lf-color-data-5": "#af8817",
    "--lf-color-data-6": "#a14f91",
    "--lf-color-data-7": "#5f6eb9",
    "--lf-color-on-bg": "#502f32",
    "--lf-color-on-border": "#4d2b2d",
    "--lf-color-link": "#fd9faf",
    "--lf-color-on-link": "#3d1214",
    "--lf-color-spinner": "#dfb5ba",
    "--lf-color-on-spinner": "#511f22",
    "--lf-ui-border-radius": "0.75em",
    "--lf-ui-radius-ripple": "50%",
    "--lf-font-size": "17px",
    "--lf-font-family-primary": "Sawarabi Mincho, serif",
    "--lf-font-family-monospace": "Raleway, sans-serif"
  }
};
const STEAMPUNK = {
  font: [
    LF_THEME_FONTS_FONTFACE.IMFellEnglishSC,
    LF_THEME_FONTS_FONTFACE.shareTechMono
  ],
  isDark: true,
  variables: {
    ...DARK.variables,
    "--lf-color-bg": "#1c1a15",
    "--lf-color-border": "#3c3324",
    "--lf-color-surface": "#2c251b",
    "--lf-color-on-surface": "#f2eee8",
    "--lf-color-primary": "#c68642",
    "--lf-color-on-primary": "#1d1207",
    "--lf-color-secondary": "#8f5937",
    "--lf-color-on-secondary": "#f9f4ed",
    "--lf-color-data-1": "#c29f3a",
    "--lf-color-data-2": "#91654a",
    "--lf-color-data-3": "#e2a676",
    "--lf-color-data-4": "#c17f56",
    "--lf-color-data-5": "#8b6c3a",
    "--lf-color-data-6": "#e4c590",
    "--lf-color-data-7": "#b5974a",
    "--lf-color-on-bg": "#f8f5ed",
    "--lf-color-on-border": "#e2dccb",
    "--lf-color-link": "#b08850",
    "--lf-color-on-link": "#241708",
    "--lf-color-spinner": "#3b2f23",
    "--lf-color-on-spinner": "#f7f3eb",
    "--lf-ui-border-radius": "0.25em",
    "--lf-ui-radius-ripple": "30%",
    "--lf-font-size": "16px",
    "--lf-font-family-primary": "IM Fell English SC, serif",
    "--lf-font-family-monospace": "Share Tech Mono, monospace"
  }
};
const URBAN = {
  font: [LF_THEME_FONTS_FONTFACE.lato, LF_THEME_FONTS_FONTFACE.merriweather],
  isDark: false,
  variables: {
    ...LIGHT.variables,
    "--lf-color-bg": "#f1f3f5",
    "--lf-color-border": "#c9ced3",
    "--lf-color-surface": "#ffffff",
    "--lf-color-on-surface": "#1f1f1f",
    "--lf-color-primary": "#003366",
    "--lf-color-on-primary": "#ffffff",
    "--lf-color-secondary": "#006699",
    "--lf-color-on-secondary": "#ffffff",
    "--lf-color-data-1": "#006699",
    "--lf-color-data-2": "#d9480f",
    "--lf-color-data-3": "#6f42c1",
    "--lf-color-data-4": "#22863a",
    "--lf-color-data-5": "#b08800",
    "--lf-color-data-6": "#d6336c",
    "--lf-color-data-7": "#005cc5",
    "--lf-color-on-bg": "#2d2d2d",
    "--lf-color-on-border": "#3c3c3c",
    "--lf-color-link": "#0044cc",
    "--lf-color-on-link": "#ffffff",
    "--lf-color-spinner": "#9a9a9a",
    "--lf-color-on-spinner": "#333333",
    "--lf-font-family-monospace": "Merriweather, monospace",
    "--lf-font-family-primary": "Lato, sans-serif",
    "--lf-ui-radius-ripple": "50%"
  }
};
const WIZARDRY = {
  font: [LF_THEME_FONTS_FONTFACE.uncialAntiqua, LF_THEME_FONTS_FONTFACE.cinzel],
  isDark: true,
  variables: {
    ...DARK.variables,
    "--lf-color-bg": "#1e0f1b",
    "--lf-color-border": "#462752",
    "--lf-color-surface": "#301b2e",
    "--lf-color-on-surface": "#f9f7f4",
    "--lf-color-primary": "#e5c40f",
    "--lf-color-on-primary": "#2f1c00",
    "--lf-color-secondary": "#8c3d8c",
    "--lf-color-on-secondary": "#f2eaf2",
    "--lf-color-data-1": "#ccac00",
    "--lf-color-data-2": "#d764d7",
    "--lf-color-data-3": "#a352a3",
    "--lf-color-data-4": "#b38a00",
    "--lf-color-data-5": "#d728d7",
    "--lf-color-data-6": "#c47cff",
    "--lf-color-data-7": "#ac66ff",
    "--lf-color-on-bg": "#f8f2ea",
    "--lf-color-on-border": "#e4d6c7",
    "--lf-color-link": "#cda000",
    "--lf-color-on-link": "#120900",
    "--lf-color-spinner": "#4e3b4e",
    "--lf-color-on-spinner": "#e3d8c6",
    "--lf-ui-border-radius": "1.5em",
    "--lf-ui-radius-ripple": "50%",
    "--lf-font-size": "15px",
    "--lf-font-family-primary": "Uncial Antiqua, serif",
    "--lf-font-family-monospace": "Cinzel, serif"
  }
};
const THEME_LIST = {
  abyss: ABYSS,
  dark: DARK,
  eris: ERIS,
  light: LIGHT,
  neon: NEON,
  night: NIGHT,
  pastel: PASTEL,
  sakura: SAKURA,
  steampunk: STEAMPUNK,
  urban: URBAN,
  wizardry: WIZARDRY
};
const LF_ICONS_REGISTRY = {
  adjustmentsHorizontal: "adjustments-horizontal",
  alertTriangle: "alert-triangle",
  arrowAutofitContent: "arrow-autofit-content",
  arrowBack: "arrow-back",
  article: "article",
  bellRinging: "bell-ringing",
  brandFacebook: "brand-facebook",
  brandGithub: "brand-github",
  brandInstagram: "brand-instagram",
  brandLinkedin: "brand-linkedin",
  brandNpm: "brand-npm",
  brandReddit: "brand-reddit",
  brandX: "brand-x",
  brush: "brush",
  bug: "bug",
  calendarClock: "calendar-clock",
  caretDown: "caret-down",
  caretLeft: "caret-left",
  caretRight: "caret-right",
  caretUp: "caret-up",
  chartColumn: "chart-column",
  chartHistogram: "chart-histogram",
  check: "check",
  chevronCompactDown: "chevron-compact-down",
  chevronCompactLeft: "chevron-compact-left",
  chevronCompactRight: "chevron-compact-right",
  chevronCompactUp: "chevron-compact-up",
  chevronDown: "chevron-down",
  chevronLeft: "chevron-left",
  chevronRight: "chevron-right",
  chevronsDown: "chevrons-down",
  chevronsLeft: "chevrons-left",
  chevronsRight: "chevrons-right",
  chevronsUp: "chevrons-up",
  chevronUp: "chevron-up",
  circleArrowDown: "circle-arrow-down",
  circleArrowLeft: "circle-arrow-left",
  circleArrowRight: "circle-arrow-right",
  circleArrowUp: "circle-arrow-up",
  circleCaretDown: "circle-caret-down",
  circleCaretLeft: "circle-caret-left",
  circleCaretRight: "circle-caret-right",
  circleCaretUp: "circle-caret-up",
  circleChevronDown: "circle-chevron-down",
  circleChevronLeft: "circle-chevron-left",
  circleChevronRight: "circle-chevron-right",
  circleChevronUp: "circle-chevron-up",
  circleX: "circle-x",
  code: "code",
  codeCircle2: "code-circle-2",
  colorSwatch: "color-swatch",
  columns2: "columns-2",
  contrast2: "contrast-2",
  copy: "copy",
  copyCheck: "copy-check",
  door: "door",
  download: "download",
  dragDrop: "drag-drop",
  droplet: "droplet",
  edit: "edit",
  file: "file",
  folder: "folder",
  forms: "forms",
  help: "help",
  hexagonMinus: "hexagon-minus",
  hexagonMinus2: "hexagon-minus-2",
  hexagonPlus: "hexagon-plus",
  hexagonPlus2: "hexagon-plus-2",
  highlight: "highlight",
  hourglassLow: "hourglass-low",
  id: "id",
  ikosaedr: "ikosaedr",
  imageInPicture: "image-in-picture",
  infoHexagon: "info-hexagon",
  innerShadowBottom: "inner-shadow-bottom",
  json: "json",
  key: "key",
  layoutBoardSplit: "layout-board-split",
  layoutList: "layout-list",
  layoutNavbar: "layout-navbar",
  layoutNavbarInactive: "layout-navbar-inactive",
  layoutSidebar: "layout-sidebar",
  lfSignature: "lf-signature",
  lfWebsite: "lf-website",
  list: "list",
  listTree: "list-tree",
  loader: "loader",
  loader2: "loader-2",
  loader3: "loader-3",
  lock: "lock",
  menu2: "menu-2",
  messageCircleUser: "message-circle-user",
  messages: "messages",
  microphone: "microphone",
  moon: "moon",
  movie: "movie",
  music: "music",
  network: "network",
  notification: "notification",
  numbers: "numbers",
  offBrush: "off-brush",
  offHexagon: "off-hexagon",
  offHighlight: "off-highlight",
  offId: "off-id",
  offMicrophone: "off-microphone",
  offMoon: "off-moon",
  offNotification: "off-notification",
  offPalette: "off-palette",
  offReplace: "off-replace",
  offSearch: "off-search",
  offSend: "off-send",
  offTemplate: "off-template",
  palette: "palette",
  pdf: "pdf",
  percentage60: "percentage-60",
  photo: "photo",
  photoSearch: "photo-search",
  photoX: "photo-x",
  progress: "progress",
  refresh: "refresh",
  replace: "replace",
  robot: "robot",
  schema: "schema",
  search: "search",
  send: "send",
  settings: "settings",
  shirt: "shirt",
  slideshow: "slideshow",
  squareToggle: "square-toggle",
  squareX: "square-x",
  stackPop: "stack-pop",
  stackPush: "stack-push",
  sunset2: "sunset-2",
  temperature: "temperature",
  template: "template",
  toggleRight: "toggle-right",
  upload: "upload",
  viewportTall: "viewport-tall",
  viewportWide: "viewport-wide",
  wand: "wand",
  writing: "writing",
  x: "x",
  zip: "zip"
};
const GLOBAL_STYLES = {
  "::-webkit-scrollbar": {
    width: "9px"
  },
  "::-webkit-scrollbar-thumb": {
    transition: "all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4)",
    "background-color": "rgb(var(--lf-color-primary))"
  },
  "::-webkit-scrollbar-track": {
    "background-color": "rgb(var(--lf-color-bg))"
  },
  '.lf-effects [data-lf="backdrop"]': {
    transition: "all 200ms cubic-bezier(0.4, 0, 0.6, 1)",
    background: "rgba(0, 0, 0, 0.375)",
    height: "100vh",
    left: "0",
    opacity: "0",
    position: "fixed",
    top: "0",
    width: "100vw",
    "z-index": "var(--lf-ui-zindex-backdrop, 899)"
  },
  "@keyframes lf-fade-in": [
    {
      from: {
        visibility: "hidden",
        opacity: "0"
      }
    },
    {
      to: {
        visibility: "visible",
        opacity: "1"
      }
    }
  ],
  '.lf-effects [data-lf="lightbox"]': {
    transition: "all 200ms cubic-bezier(0.4, 0, 0.6, 1)",
    height: "90dvh",
    left: "5dvw",
    position: "fixed",
    top: "5dvh",
    width: "90dvw",
    "z-index": "var(--lf-ui-zindex-lightbox, 900)"
  },
  '.lf-effects [data-lf="lightbox-content"]': {
    width: "100%",
    height: "100%",
    border: "1px solid rgba(var(--lf-color-border), 0.375)",
    "border-radius": "var(--lf-ui-border-radius)",
    "box-sizing": "border-box",
    outline: "none",
    "z-index": "calc(var(--lf-ui-zindex-lightbox, 900) + 1)"
  },
  "@keyframes lf-pop": [
    {
      from: {
        opacity: "0",
        transform: "translate(-50%, -50%) scale(0.8)"
      }
    },
    {
      to: {
        opacity: "1",
        transform: "translate(-50%, -50%) scale(1)"
      }
    }
  ],
  '.lf-portal [data-lf="portal"]': {
    display: "block",
    height: "auto",
    "max-height": "45dvh",
    "max-width": "45dvw",
    "min-height": "max-content",
    "min-width": "max-content",
    position: "fixed",
    width: "auto",
    "z-index": "var(--lf-ui-zindex-portal)"
  }
};
function _mergeNamespaces(n2, m2) {
  m2.forEach(function(e2) {
    e2 && typeof e2 !== "string" && !Array.isArray(e2) && Object.keys(e2).forEach(function(k2) {
      if (k2 !== "default" && !(k2 in n2)) {
        var d2 = Object.getOwnPropertyDescriptor(e2, k2);
        Object.defineProperty(n2, k2, d2.get ? d2 : {
          enumerable: true,
          get: function() {
            return e2[k2];
          }
        });
      }
    });
  });
  return Object.freeze(n2);
}
var __classPrivateFieldSet$8 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$8 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfColor_LF_MANAGER, _LfColor_handleEdgeCases;
class LfColor {
  constructor(lfFramework2) {
    _LfColor_LF_MANAGER.set(this, void 0);
    _LfColor_handleEdgeCases.set(this, (color) => {
      const { logs } = __classPrivateFieldGet$8(this, _LfColor_LF_MANAGER, "f").debug;
      const { variables } = __classPrivateFieldGet$8(this, _LfColor_LF_MANAGER, "f").theme.get.current();
      if (color === "transparent") {
        color = variables["--lf-color-bg"];
        logs.new(this, "Received TRANSPARENT color, converted to " + color + " (theme background).");
      }
      const altRgbRe = /R(\d{1,3})G(\d{1,3})B(\d{1,3})/;
      const altRgb = altRgbRe.test(color);
      if (altRgb) {
        const parts = color.match(altRgbRe);
        color = "rgb(" + parts[1] + "," + parts[2] + "," + parts[3] + ")";
      }
      return color;
    });
    this.autoContrast = (color) => {
      const rgb = this.compute(color).rgbColor;
      const colorValues = rgb.replace(/[^\d,.]/g, "").split(",");
      const brightness = Math.round((Number(colorValues[0]) * 299 + Number(colorValues[1]) * 587 + Number(colorValues[2]) * 114) / 1e3);
      return brightness > 125 ? "#000000" : "#ffffff";
    };
    this.compute = (color) => {
      const { logs } = __classPrivateFieldGet$8(this, _LfColor_LF_MANAGER, "f").debug;
      color = __classPrivateFieldGet$8(this, _LfColor_handleEdgeCases, "f").call(this, color);
      const lowerColor = color.toLowerCase();
      let isHex = lowerColor.startsWith("#");
      const isHslOrHsla = lowerColor.startsWith("hsl(") || lowerColor.startsWith("hsla(");
      const isRgbOrRgba = lowerColor.startsWith("rgb(") || lowerColor.startsWith("rgba(");
      if (!isHex && !isHslOrHsla && !isRgbOrRgba) {
        const maybeHex = this.convert.codeToHex(color);
        if (maybeHex.startsWith("#")) {
          color = maybeHex;
          isHex = true;
        }
      }
      let colorValues = {
        hexColor: "#000000",
        hslColor: "hsl(0,0%,0%)",
        hslValues: "0,0%,0%",
        hue: "0",
        saturation: "0%",
        lightness: "0%",
        rgbColor: "rgb(0,0,0)",
        rgbValues: "0,0,0"
      };
      if (isHex || isHslOrHsla) {
        const originalInput = color;
        let rgbObj = null;
        if (isHex) {
          colorValues.hexColor = color;
          rgbObj = this.convert.hexToRgb(color);
        } else {
          colorValues.hslColor = color;
          const hslRegex = /hsla?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?%)\s*,\s*(\d+(?:\.\d+)?%)/i;
          const hslMatch = color.match(hslRegex);
          if (hslMatch) {
            const [_2, hRaw, sRaw, lRaw] = hslMatch;
            colorValues.hslValues = `${hRaw},${sRaw},${lRaw}`;
            colorValues.hue = hRaw;
            colorValues.saturation = sRaw;
            colorValues.lightness = lRaw;
            const hNum = parseFloat(hRaw.replace("deg", ""));
            const sNum = parseFloat(sRaw.replace("%", "")) / 100;
            const lNum = parseFloat(lRaw.replace("%", "")) / 100;
            rgbObj = this.convert.hslToRgb(hNum, sNum, lNum);
          } else {
            logs.new(this, `Invalid HSL(A) color: ${color}. Using defaults.`);
          }
        }
        if (rgbObj) {
          const { r: r2, g: g2, b: b2 } = rgbObj;
          const rgbString = `rgb(${r2},${g2},${b2})`;
          colorValues.rgbColor = rgbString;
          colorValues.rgbValues = `${r2},${g2},${b2}`;
          if (isHex) {
            const { h: h2, s: s2, l: l2 } = this.convert.rgbToHsl(r2, g2, b2);
            const hslStr = `${h2},${s2}%,${l2}%`;
            colorValues.hue = `${h2}`;
            colorValues.saturation = `${s2}%`;
            colorValues.lightness = `${l2}%`;
            colorValues.hslValues = hslStr;
            colorValues.hslColor = `hsl(${hslStr})`;
          } else {
            colorValues.hexColor = this.convert.rgbToHex(r2, g2, b2);
          }
          logs.new(this, `Received color "${originalInput}" → Final RGB: ${colorValues.rgbColor}.`);
        }
      }
      const rgbaMatch = color.match(/rgba?\((\d{1,3}),\s?(\d{1,3}),\s?(\d{1,3})(?:,\s?[\d.]+)?\)/i);
      if (rgbaMatch) {
        const [_2, rStr, gStr, bStr] = rgbaMatch;
        colorValues.rgbValues = `${rStr},${gStr},${bStr}`;
        colorValues.rgbColor = `rgb(${rStr},${gStr},${bStr})`;
        if (!colorValues.hexColor || colorValues.hexColor === "#000000") {
          try {
            const r2 = parseInt(rStr, 10);
            const g2 = parseInt(gStr, 10);
            const b2 = parseInt(bStr, 10);
            colorValues.hexColor = this.convert.rgbToHex(r2, g2, b2);
          } catch {
            logs.new(this, `Color not converted to hex value: ${color}.`);
          }
        }
        if (!colorValues.hslColor || colorValues.hslColor === "hsl(0,0%,0%)") {
          try {
            const r2 = parseInt(rStr, 10);
            const g2 = parseInt(gStr, 10);
            const b2 = parseInt(bStr, 10);
            const { h: h2, s: s2, l: l2 } = this.convert.rgbToHsl(r2, g2, b2);
            const hslStr = `${h2},${s2}%,${l2}%`;
            colorValues.hue = `${h2}`;
            colorValues.saturation = `${s2}%`;
            colorValues.lightness = `${l2}%`;
            colorValues.hslValues = hslStr;
            colorValues.hslColor = `hsl(${hslStr})`;
          } catch {
            logs.new(this, `Color not converted to HSL value: ${color}.`);
          }
        }
      } else {
        logs.new(this, `Color not converted to RGB values: ${color}.`);
      }
      return colorValues;
    };
    this.convert = {
      //#region hexToRgb
      hexToRgb: (hex) => {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16)
        } : null;
      },
      //#endregion
      //#region hslToRgb
      hslToRgb: (h2, s2, l2) => {
        if (h2 == void 0) {
          return { r: 0, g: 0, b: 0 };
        }
        let huePrime = h2 / 60;
        const chroma = (1 - Math.abs(2 * l2 - 1)) * s2;
        const secondComponent = chroma * (1 - Math.abs(huePrime % 2 - 1));
        huePrime = Math.floor(huePrime);
        let red, green, blue;
        if (huePrime === 0) {
          red = chroma;
          green = secondComponent;
          blue = 0;
        } else if (huePrime === 1) {
          red = secondComponent;
          green = chroma;
          blue = 0;
        } else if (huePrime === 2) {
          red = 0;
          green = chroma;
          blue = secondComponent;
        } else if (huePrime === 3) {
          red = 0;
          green = secondComponent;
          blue = chroma;
        } else if (huePrime === 4) {
          red = secondComponent;
          green = 0;
          blue = chroma;
        } else if (huePrime === 5) {
          red = chroma;
          green = 0;
          blue = secondComponent;
        }
        const lightnessAdjustment = l2 - chroma / 2;
        red += lightnessAdjustment;
        green += lightnessAdjustment;
        blue += lightnessAdjustment;
        return {
          r: Math.round(red * 255),
          g: Math.round(green * 255),
          b: Math.round(blue * 255)
        };
      },
      //#endregion
      //#region rgbToHex
      rgbToHex: (r2, g2, b2) => {
        const { valueToHex } = this.convert;
        return `#${valueToHex(r2)}${valueToHex(g2)}${valueToHex(b2)}`;
      },
      //#endregion
      //#region rgbToHsl
      rgbToHsl: (r2, g2, b2) => {
        r2 /= 255;
        g2 /= 255;
        b2 /= 255;
        const cmin = Math.min(r2, g2, b2), cmax = Math.max(r2, g2, b2), delta = cmax - cmin;
        let h2 = 0, s2 = 0, l2 = 0;
        if (delta == 0)
          h2 = 0;
        else if (cmax == r2)
          h2 = (g2 - b2) / delta % 6;
        else if (cmax == g2)
          h2 = (b2 - r2) / delta + 2;
        else
          h2 = (r2 - g2) / delta + 4;
        h2 = Math.round(h2 * 60);
        if (h2 < 0)
          h2 += 360;
        l2 = (cmax + cmin) / 2;
        s2 = delta == 0 ? 0 : delta / (1 - Math.abs(2 * l2 - 1));
        s2 = +(s2 * 100).toFixed(1);
        l2 = +(l2 * 100).toFixed(1);
        return { h: h2, s: s2, l: l2 };
      },
      //#endregion
      //#region valueToHex
      valueToHex: (c2) => {
        const hex = c2.toString(16);
        return hex.length == 1 ? "0" + hex : hex;
      },
      //#endregion
      //#region codeToHex
      codeToHex: (color) => {
        const { logs } = __classPrivateFieldGet$8(this, _LfColor_LF_MANAGER, "f").debug;
        const code2 = color.toLowerCase();
        if (LF_COLOR_CODES[code2]) {
          return LF_COLOR_CODES[code2];
        } else {
          logs.new(this, "Could not decode color " + color + "!");
          return color;
        }
      }
      //#endregion
    };
    this.random = (brightness) => {
      function randomChannel(brightness2) {
        var r2 = 255 - brightness2;
        var n2 = 0 | Math.random() * r2 + brightness2;
        var s2 = n2.toString(16);
        return s2.length == 1 ? "0" + s2 : s2;
      }
      return `#${randomChannel(brightness) + randomChannel(brightness) + randomChannel(brightness)}`;
    };
    __classPrivateFieldSet$8(this, _LfColor_LF_MANAGER, lfFramework2, "f");
  }
}
_LfColor_LF_MANAGER = /* @__PURE__ */ new WeakMap(), _LfColor_handleEdgeCases = /* @__PURE__ */ new WeakMap();
const buildNodeLookup = (dataset) => {
  var _a;
  const lookup = /* @__PURE__ */ new Map();
  if (!((_a = dataset == null ? void 0 : dataset.nodes) == null ? void 0 : _a.length)) {
    return lookup;
  }
  const queue = [...dataset.nodes];
  while (queue.length > 0) {
    const current = queue.shift();
    if (!current) {
      continue;
    }
    if (current.id != null) {
      lookup.set(String(current.id), current);
    }
    if (Array.isArray(current.children) && current.children.length) {
      queue.unshift(...current.children);
    }
  }
  return lookup;
};
const normaliseTargetInput = (target) => {
  if (target == null) {
    return [];
  }
  return Array.isArray(target) ? target : [target];
};
const extractCellMetadata = (node, cellId, schema) => {
  if (!node || typeof node !== "object" || !node.cells) {
    return (schema == null ? void 0 : schema.nullable) ? null : void 0;
  }
  const cell = node.cells[cellId];
  if (!cell || typeof cell !== "object") {
    return (schema == null ? void 0 : schema.nullable) ? null : void 0;
  }
  const rawValue = cell.value;
  if (rawValue === void 0 || rawValue === null) {
    return (schema == null ? void 0 : schema.nullable) ? null : void 0;
  }
  if (!schema) {
    return rawValue;
  }
  if (schema.validate && !schema.validate(rawValue)) {
    return schema.nullable ? null : void 0;
  }
  const validated = rawValue;
  if (schema.transform) {
    try {
      return schema.transform(validated);
    } catch {
      return schema.nullable ? null : void 0;
    }
  }
  return validated;
};
const nodeFind = (dataset, predicate) => {
  if (!dataset || !Array.isArray(dataset.nodes) || !predicate) {
    return void 0;
  }
  const queue = [...dataset.nodes];
  while (queue.length > 0) {
    const current = queue.shift();
    if (!current) {
      continue;
    }
    if (predicate(current)) {
      return current;
    }
    if (Array.isArray(current.children) && current.children.length) {
      queue.unshift(...current.children);
    }
  }
  return void 0;
};
const nodeResolveTargets = (dataset, target) => {
  const lookup = buildNodeLookup(dataset);
  const inputs = normaliseTargetInput(target);
  if (!inputs.length) {
    return { ids: [], nodes: [] };
  }
  const ids = [];
  const seenIds = /* @__PURE__ */ new Set();
  const nodesById = /* @__PURE__ */ new Map();
  for (const entry of inputs) {
    if (entry == null) {
      continue;
    }
    let id = null;
    let resolvedNode;
    if (typeof entry === "string") {
      if (!entry) {
        continue;
      }
      id = entry;
      resolvedNode = lookup.get(entry);
    } else {
      const candidateId = entry.id;
      if (candidateId == null) {
        continue;
      }
      id = String(candidateId);
      resolvedNode = lookup.get(id) ?? entry;
    }
    if (!id) {
      continue;
    }
    if (!nodesById.has(id) && resolvedNode) {
      nodesById.set(id, resolvedNode);
    } else if (!nodesById.has(id)) {
      const datasetNode = lookup.get(id);
      if (datasetNode) {
        nodesById.set(id, datasetNode);
      }
    } else if (lookup.has(id)) {
      nodesById.set(id, lookup.get(id));
    }
    if (!seenIds.has(id)) {
      seenIds.add(id);
      ids.push(id);
    }
  }
  const nodes = [];
  for (const id of ids) {
    const resolved = nodesById.get(id) ?? lookup.get(id);
    if (resolved) {
      nodes.push(resolved);
    }
  }
  return { ids, nodes };
};
const nodeSanitizeIds = (dataset, candidates, options = {}) => {
  var _a;
  const empty = { ids: [], nodes: [] };
  if (!((_a = dataset == null ? void 0 : dataset.nodes) == null ? void 0 : _a.length) || !candidates) {
    return empty;
  }
  const lookup = buildNodeLookup(dataset);
  const { predicate, limit } = options;
  const ids = [];
  const nodes = [];
  const seen = /* @__PURE__ */ new Set();
  for (const entry of candidates) {
    if (entry == null) {
      continue;
    }
    let id = null;
    let resolvedNode;
    if (typeof entry === "string" || typeof entry === "number") {
      id = String(entry);
      resolvedNode = lookup.get(id);
    } else {
      const candidateId = entry.id;
      if (candidateId == null) {
        continue;
      }
      id = String(candidateId);
      resolvedNode = lookup.get(id);
    }
    if (!id || seen.has(id) || !resolvedNode) {
      continue;
    }
    if (predicate && !predicate(resolvedNode)) {
      continue;
    }
    ids.push(id);
    nodes.push(resolvedNode);
    seen.add(id);
    if (limit && ids.length >= limit) {
      break;
    }
  }
  return { ids, nodes };
};
const findNodeByCell = (dataset, targetCell) => {
  function recursive(nodes) {
    for (const node of nodes) {
      if (node.cells) {
        for (const cellKey in node.cells) {
          if (node.cells[cellKey] === targetCell) {
            return node;
          }
        }
      }
      if (node.children) {
        const foundNode = recursive(node.children);
        if (foundNode)
          return foundNode;
      }
    }
    return null;
  }
  return recursive(dataset.nodes);
};
const nodeExists = (dataset) => {
  var _a;
  return !!(dataset && ((_a = dataset.nodes) == null ? void 0 : _a.length));
};
const nodeFilter = (dataset, filters, partialMatch = false) => {
  const matchingNodes = /* @__PURE__ */ new Set();
  const remainingNodes = /* @__PURE__ */ new Set();
  const ancestorNodes = /* @__PURE__ */ new Set();
  const recursive = (node, ancestor, ancestorSet) => {
    var _a;
    const hasChildren = (_a = node.children) == null ? void 0 : _a.length;
    let matches = false;
    for (const key in filters) {
      const k2 = key;
      const nodeValue = node[k2];
      const filterValue = filters[k2];
      const nodeValueStr = cellStringify(nodeValue).toLowerCase();
      const filterValueStr = cellStringify(filterValue).toLowerCase();
      if (partialMatch) {
        if (!nodeValueStr.includes(filterValueStr)) {
          continue;
        }
      } else {
        if (nodeValue !== filterValue) {
          continue;
        }
      }
      matches = true;
      break;
    }
    if (ancestor) {
      ancestorSet.add(ancestor);
    }
    if (matches) {
      matchingNodes.add(node);
    } else {
      remainingNodes.add(node);
    }
    if (hasChildren) {
      node.children.forEach((child) => {
        recursive(child, node, ancestorSet);
      });
    } else {
      if (matches) {
        ancestorSet.forEach((node2) => {
          ancestorNodes.add(node2);
        });
      }
    }
  };
  dataset.nodes.forEach((node) => {
    const ancestorSet = /* @__PURE__ */ new Set();
    recursive(node, null, ancestorSet);
  });
  return {
    matchingNodes,
    remainingNodes,
    ancestorNodes
  };
};
const nodeFixIds = (nodes) => {
  function updateNodeIds(node, depth = "0") {
    node.id = depth;
    if (node.children) {
      node.children.forEach((child, index) => {
        const newDepth = `${depth}.${index}`;
        updateNodeIds(child, newDepth);
      });
    }
  }
  nodes.forEach((node) => {
    updateNodeIds(node, "0");
  });
  return nodes;
};
const nodeGetParent = (nodes, child) => {
  let parent = null;
  for (let index = 0; index < nodes.length; index++) {
    let recursive = function(node2) {
      const hasChildren = !!node2.children;
      if (hasChildren && node2.children.includes(child)) {
        parent = node2;
        return;
      }
      for (let index2 = 0; !parent && hasChildren && index2 < node2.children.length; index2++) {
        recursive(node2.children[index2]);
      }
    };
    const node = nodes[index];
    recursive(node);
  }
  return parent;
};
const nodePop = (nodes, node2remove) => {
  let removed = null;
  for (let index = 0; index < nodes.length; index++) {
    let recursive = function(node, array) {
      const i2 = array.indexOf(node2remove);
      if (i2 > -1) {
        removed = { ...node2remove };
        array.splice(i2, 1);
        return;
      }
      for (let index2 = 0; node.children && index2 < node.children.length; index2++) {
        if (node.children[index2]) {
          recursive(node.children[index2], node.children);
        }
      }
    };
    recursive(nodes[index], nodes);
  }
  return removed;
};
const nodeToStream = (nodes) => {
  function recursive(node) {
    streamlined.push(node);
    for (let index = 0; node.children && index < node.children.length; index++) {
      recursive(node.children[index]);
    }
  }
  const streamlined = [];
  for (let index = 0; index < nodes.length; index++) {
    const node = nodes[index];
    recursive(node);
  }
  return streamlined;
};
const nodeTraverseVisible = (nodes, options) => {
  const out = [];
  if (!(nodes == null ? void 0 : nodes.length))
    return out;
  const { isExpanded = () => true, isHidden = () => false, isSelected = () => false, forceExpand } = options || {};
  const walk = (node, depth) => {
    const expanded = forceExpand ? true : isExpanded(node);
    const hidden = isHidden(node);
    const selected = isSelected(node);
    if (!hidden)
      out.push({ node, depth, expanded, hidden, selected });
    if (expanded && node.children) {
      for (const child of node.children)
        walk(child, depth + 1);
    }
  };
  for (const n2 of nodes)
    walk(n2, 0);
  return out;
};
const cellExists = (node) => {
  return !!(node && node.cells && Object.keys(node.cells).length);
};
const cellGetShape = (cell, deepCopy) => {
  if (!deepCopy) {
    return cell;
  }
  const prefix = "lf";
  const shapeProps = {};
  for (const prop in cell) {
    switch (prop) {
      case "htmlProps":
        Object.assign(shapeProps, cell[prop]);
        break;
      case "shape":
        break;
      default:
        if (prop.indexOf(prefix) === 0) {
          shapeProps[prop] = cell[prop];
        } else {
          const prefixedProp = prefix + prop.charAt(0).toUpperCase() + prop.slice(1);
          const k2 = prefixedProp;
          if (!shapeProps[k2]) {
            shapeProps[k2] = cell[prop];
          }
        }
        break;
    }
  }
  return shapeProps;
};
const cellGetAllShapes = (dataset, deepCopy = true) => {
  if (!nodeExists(dataset)) {
    return null;
  }
  const shapes = {
    badge: [],
    button: [],
    canvas: [],
    card: [],
    chart: [],
    chat: [],
    chip: [],
    code: [],
    image: [],
    number: [],
    photoframe: [],
    progressbar: [],
    slot: [],
    text: [],
    textfield: [],
    toggle: [],
    typewriter: [],
    upload: []
  };
  const nodes = dataset.nodes;
  const browseCells = (node) => {
    if (!cellExists(node)) {
      return;
    }
    const cells = node.cells;
    for (const key in cells) {
      if (Object.prototype.hasOwnProperty.call(cells, key)) {
        const cell = cells[key];
        const extracted = cellGetShape(cell, deepCopy);
        switch (cell.shape) {
          case "badge":
            shapes.badge.push(extracted);
            break;
          case "button":
            shapes.button.push(extracted);
            break;
          case "canvas":
            shapes.canvas.push(extracted);
            break;
          case "card":
            shapes.card.push(extracted);
            break;
          case "chart":
            shapes.chart.push(extracted);
            break;
          case "chat":
            shapes.chat.push(extracted);
            break;
          case "chip":
            shapes.chip.push(extracted);
            break;
          case "code":
            shapes.code.push(extracted);
            break;
          case "image":
            shapes.image.push(extracted);
            break;
          case "photoframe":
            shapes.photoframe.push(extracted);
            break;
          case "progressbar":
            shapes.progressbar.push(extracted);
            break;
          case "textfield":
            shapes.textfield.push(extracted);
            break;
          case "toggle":
            shapes.toggle.push(extracted);
            break;
          case "typewriter":
            shapes.typewriter.push(extracted);
            break;
          case "number":
            shapes.number.push(cell);
            break;
          case "upload":
            shapes.upload.push(extracted);
            break;
          case "slot":
            shapes.slot.push(cell);
            break;
          case "text":
          default:
            shapes.text.push(cell);
            break;
        }
      }
    }
  };
  for (let index = 0; index < nodes.length; index++) {
    const node = nodes[index];
    browseCells(node);
  }
  return shapes;
};
const cellStringify = (value) => {
  if (value === null || value === void 0) {
    return String(value).valueOf();
  } else if (value instanceof Date) {
    return value.toISOString();
  } else if (typeof value === "object") {
    try {
      return JSON.stringify(value, null, 2);
    } catch (error2) {
      console.error("Failed to stringify object:", error2);
      return "[object Object]";
    }
  } else {
    return String(value).valueOf();
  }
};
const columnFind = (dataset, filters) => {
  const result = [];
  if (!dataset) {
    return result;
  }
  const columns = dataset.columns ? dataset.columns : dataset;
  for (let index = 0; index < columns.length; index++) {
    const column = columns[index];
    for (const key in filters) {
      const k2 = key;
      const filter = filters[k2];
      if (column[k2] === filter) {
        result.push(column);
      }
    }
  }
  return result;
};
class LfData {
  constructor(_lfFramework) {
    this.cell = {
      exists: (node) => cellExists(node),
      shapes: {
        get: (cell, deepCopy = true) => cellGetShape(cell, deepCopy),
        getAll: (dataset, deepCopy = true) => cellGetAllShapes(dataset, deepCopy)
      },
      stringify: (value) => cellStringify(value)
    };
    this.column = {
      find: (dataset, filters) => columnFind(dataset, filters)
    };
    this.node = {
      exists: (dataset) => nodeExists(dataset),
      filter: (dataset, filters, partialMatch = false) => nodeFilter(dataset, filters, partialMatch),
      findNodeByCell: (dataset, cell) => findNodeByCell(dataset, cell),
      fixIds: (nodes) => nodeFixIds(nodes),
      getParent: (nodes, child) => nodeGetParent(nodes, child),
      pop: (nodes, node2remove) => nodePop(nodes, node2remove),
      toStream: (nodes) => nodeToStream(nodes),
      traverseVisible: (nodes, predicates) => nodeTraverseVisible(nodes, predicates),
      find: (dataset, predicate) => nodeFind(dataset, predicate),
      resolveTargets: (dataset, target) => nodeResolveTargets(dataset, target),
      sanitizeIds: (dataset, candidates, options) => nodeSanitizeIds(dataset, candidates, options),
      extractCellMetadata: (node, cellId, schema) => extractCellMetadata(node, cellId, schema)
    };
  }
}
var __classPrivateFieldSet$7 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$7 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfDebug_COMPONENTS, _LfDebug_IS_ENABLED, _LfDebug_IS_PROD, _LfDebug_LOG_LIMIT, _LfDebug_LOGS, _LfDebug_codeDispatcher, _LfDebug_toggleDispatcher;
class LfDebug {
  constructor(_lfFramework) {
    var _a;
    _LfDebug_COMPONENTS.set(this, {
      codes: /* @__PURE__ */ new Set(),
      toggles: /* @__PURE__ */ new Set()
    });
    _LfDebug_IS_ENABLED.set(this, false);
    _LfDebug_IS_PROD.set(this, false);
    _LfDebug_LOG_LIMIT.set(this, 250);
    _LfDebug_LOGS.set(this, []);
    _LfDebug_codeDispatcher.set(this, (log) => {
      Array.from(__classPrivateFieldGet$7(this, _LfDebug_COMPONENTS, "f").codes).forEach((comp) => {
        if (log) {
          comp.lfValue = `# ${log.id}:
${log.message}

${comp.lfValue}`;
        } else {
          comp.lfValue = "";
        }
      });
    });
    _LfDebug_toggleDispatcher.set(this, () => {
      Array.from(__classPrivateFieldGet$7(this, _LfDebug_COMPONENTS, "f").toggles).forEach((comp) => {
        comp.setValue(__classPrivateFieldGet$7(this, _LfDebug_IS_ENABLED, "f") ? "on" : "off");
      });
    });
    this.info = {
      //#region Create info
      create: () => {
        return {
          endTime: 0,
          renderCount: 0,
          renderEnd: 0,
          renderStart: 0,
          startTime: performance.now()
        };
      },
      //#endregion
      //#region Update info
      update: async (comp, lifecycle) => {
        switch (lifecycle) {
          case "custom":
            if (this.isEnabled()) {
              this.logs.new(comp, "Custom breakpoint  took " + (window.performance.now() - comp.debugInfo.renderStart) + "ms.");
            }
            break;
          case "did-render":
            comp.debugInfo.renderEnd = window.performance.now();
            if (this.isEnabled()) {
              this.logs.new(comp, "Render #" + comp.debugInfo.renderCount + " took " + (comp.debugInfo.renderEnd - comp.debugInfo.renderStart) + "ms.");
            }
            break;
          case "did-load":
            comp.debugInfo.endTime = window.performance.now();
            this.logs.new(comp, "Component ready after " + (comp.debugInfo.endTime - comp.debugInfo.startTime) + "ms.");
            break;
          case "will-render":
            comp.debugInfo.renderCount++;
            comp.debugInfo.renderStart = window.performance.now();
            break;
        }
      }
      //#endregion
    };
    this.logs = {
      //#region Dump logs
      dump: () => {
        __classPrivateFieldSet$7(this, _LfDebug_LOGS, [], "f");
        __classPrivateFieldGet$7(this, _LfDebug_codeDispatcher, "f").call(this);
      },
      //#endregion
      //#region Logs from comp
      fromComponent(comp) {
        return comp.rootElement !== void 0;
      },
      //#endregion
      //#region New log
      new: async (comp, message, category = "informational") => {
        if (__classPrivateFieldGet$7(this, _LfDebug_IS_PROD, "f") && category === "informational") {
          return;
        }
        if (__classPrivateFieldGet$7(this, _LfDebug_COMPONENTS, "f").codes.has(comp)) {
          return;
        }
        const isFromComponent = this.logs.fromComponent(comp);
        const log = {
          category,
          class: null,
          date: /* @__PURE__ */ new Date(),
          id: isFromComponent ? `${comp.rootElement.tagName} ${comp.rootElement.id ? "( #" + comp.rootElement.id + " )" : ""}` : "LfFramework",
          message,
          type: message.indexOf("Render #") > -1 ? "render" : message.indexOf("Component ready") > -1 ? "load" : message.indexOf("Size changed") > -1 ? "resize" : "misc"
        };
        if (__classPrivateFieldGet$7(this, _LfDebug_LOGS, "f").length > __classPrivateFieldGet$7(this, _LfDebug_LOG_LIMIT, "f")) {
          if (__classPrivateFieldGet$7(this, _LfDebug_IS_ENABLED, "f")) {
            console.warn(log.date.toLocaleDateString() + " lf-debug => Too many logs (> " + __classPrivateFieldGet$7(this, _LfDebug_LOG_LIMIT, "f") + ")! Dumping (increase debug.logLimit to store more logs)... .");
          }
          this.logs.dump();
        }
        __classPrivateFieldGet$7(this, _LfDebug_LOGS, "f").push(log);
        switch (category) {
          case "error":
            console.error(`${log.date.toLocaleDateString()} ${log.id} ${log.message}`, log.class);
            break;
          case "warning":
            console.warn(`${log.date.toLocaleDateString()} ${log.id} ${log.message}`, log.class);
            break;
        }
        if (this.isEnabled()) {
          __classPrivateFieldGet$7(this, _LfDebug_codeDispatcher, "f").call(this, log);
        }
      },
      //#endregion
      //#region Print logs
      print: () => {
        const logsToPrint = {
          load: [],
          misc: [],
          render: [],
          resize: []
        };
        for (let index = 0; index < __classPrivateFieldGet$7(this, _LfDebug_LOGS, "f").length; index++) {
          const log = __classPrivateFieldGet$7(this, _LfDebug_LOGS, "f")[index];
          const printEntry = {
            class: log.class,
            date: log.date.toLocaleDateString(),
            message: log.id + log.message
          };
          logsToPrint[log.type].push(printEntry);
        }
        for (const key in logsToPrint) {
          if (Object.prototype.hasOwnProperty.call(logsToPrint, key)) {
            const k2 = key;
            const logs = logsToPrint[k2];
            console.groupCollapsed("%c  %c" + key + " logs (" + logsToPrint[k2].length + ")", "background-color: green; margin-right: 10px; border-radius: 50%", "background-color: transparent");
            for (let index = 0; index < logs.length; index++) {
              const log = logs[index];
              console.log(log.date, log.message, log.class);
            }
            console.groupEnd();
          }
        }
        if (__classPrivateFieldGet$7(this, _LfDebug_LOGS, "f").length > 0) {
          console.groupCollapsed("%c  %cAll logs (" + __classPrivateFieldGet$7(this, _LfDebug_LOGS, "f").length + ")", "background-color: blue; margin-right: 10px; border-radius: 50%", "background-color: transparent");
          console.table(__classPrivateFieldGet$7(this, _LfDebug_LOGS, "f"));
          console.groupEnd();
        }
      }
      //#endregion
    };
    this.isEnabled = () => {
      return __classPrivateFieldGet$7(this, _LfDebug_IS_ENABLED, "f");
    };
    this.register = (comp) => {
      if (comp.rootElement.tagName.toLowerCase() === "lf-code") {
        __classPrivateFieldGet$7(this, _LfDebug_COMPONENTS, "f").codes.add(comp);
      } else {
        __classPrivateFieldGet$7(this, _LfDebug_COMPONENTS, "f").toggles.add(comp);
      }
    };
    this.toggle = (value, dispatch = true) => {
      if (value === false || value === true) {
        __classPrivateFieldSet$7(this, _LfDebug_IS_ENABLED, value, "f");
      } else {
        __classPrivateFieldSet$7(this, _LfDebug_IS_ENABLED, !__classPrivateFieldGet$7(this, _LfDebug_IS_ENABLED, "f"), "f");
      }
      if (dispatch) {
        __classPrivateFieldGet$7(this, _LfDebug_toggleDispatcher, "f").call(this);
      }
      return __classPrivateFieldGet$7(this, _LfDebug_IS_ENABLED, "f");
    };
    this.unregister = (comp) => {
      if (comp.rootElement.tagName.toLowerCase() === "lf-code") {
        __classPrivateFieldGet$7(this, _LfDebug_COMPONENTS, "f").codes.delete(comp);
      } else {
        __classPrivateFieldGet$7(this, _LfDebug_COMPONENTS, "f").toggles.delete(comp);
      }
    };
    __classPrivateFieldSet$7(this, _LfDebug_IS_PROD, typeof process !== "undefined" && ((_a = process.env) == null ? void 0 : _a.NODE_ENV) === "production", "f");
  }
}
_LfDebug_COMPONENTS = /* @__PURE__ */ new WeakMap(), _LfDebug_IS_ENABLED = /* @__PURE__ */ new WeakMap(), _LfDebug_IS_PROD = /* @__PURE__ */ new WeakMap(), _LfDebug_LOG_LIMIT = /* @__PURE__ */ new WeakMap(), _LfDebug_LOGS = /* @__PURE__ */ new WeakMap(), _LfDebug_codeDispatcher = /* @__PURE__ */ new WeakMap(), _LfDebug_toggleDispatcher = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldSet$6 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$6 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfDrag_instances, _LfDrag_IS_DRAGGING, _LfDrag_DRAG_THRESHOLD, _LfDrag_MANAGER, _LfDrag_POINTER_ID, _LfDrag_REDUCED_MOTION, _LfDrag_SESSIONS, _LfDrag_initializeSession, _LfDrag_defaultPointerMoveAndUp, _LfDrag_setupThresholdAwarePointerDown, _LfDrag_dragToDropHandler, _LfDrag_dragToResizeHandler, _LfDrag_dragToScrollHandler, _LfDrag_swipeHandler;
class LfDrag {
  constructor(lfFramework2) {
    _LfDrag_instances.add(this);
    _LfDrag_IS_DRAGGING.set(this, false);
    _LfDrag_DRAG_THRESHOLD.set(this, 5);
    _LfDrag_MANAGER.set(this, void 0);
    _LfDrag_POINTER_ID.set(this, null);
    _LfDrag_REDUCED_MOTION.set(this, window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    _LfDrag_SESSIONS.set(this, /* @__PURE__ */ new WeakMap());
    _LfDrag_defaultPointerMoveAndUp.set(this, (element, session) => {
      const onPointerMove = (moveEvent) => {
        var _a, _b;
        (_b = (_a = session.callbacks) == null ? void 0 : _a.onMove) == null ? void 0 : _b.call(_a, moveEvent, session);
      };
      const onPointerUp = (endEvent) => {
        var _a, _b;
        element.removeEventListener("pointermove", onPointerMove);
        element.removeEventListener("pointerup", onPointerUp);
        element.removeEventListener("pointercancel", onPointerUp);
        (_b = (_a = session.callbacks) == null ? void 0 : _a.onEnd) == null ? void 0 : _b.call(_a, endEvent, session);
      };
      element.addEventListener("pointermove", onPointerMove);
      element.addEventListener("pointerup", onPointerUp);
      element.addEventListener("pointercancel", onPointerUp);
    });
    _LfDrag_dragToDropHandler.set(this, (element, e2) => {
      var _a, _b;
      const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
      if (!session) {
        __classPrivateFieldGet$6(this, _LfDrag_MANAGER, "f").debug.logs.new(this, "Attempted to interact with an unregistered element.", "warning");
        return;
      }
      const startX = e2.clientX;
      const startY = e2.clientY;
      const rect = element.getBoundingClientRect();
      const offsetLeft = rect.left;
      const offsetTop = rect.top;
      (_b = (_a = session.callbacks) == null ? void 0 : _a.onStart) == null ? void 0 : _b.call(_a, e2, session);
      element.style.position = "absolute";
      element.style.cursor = "grabbing";
      const onPointerMove = (moveEvent) => {
        var _a2, _b2;
        session.dragData = {
          ...session.dragData,
          startX,
          startY,
          deltaX: moveEvent.clientX - startX,
          deltaY: moveEvent.clientY - startY,
          lastX: moveEvent.clientX,
          lastY: moveEvent.clientY,
          lastScrollLeft: 0,
          lastScrollTop: 0,
          startScrollLeft: 0,
          startScrollTop: 0
        };
        const newLeft = offsetLeft + session.dragData.deltaX;
        const newTop = offsetTop + session.dragData.deltaY;
        element.style.left = `${newLeft}px`;
        element.style.top = `${newTop}px`;
        (_b2 = (_a2 = session.callbacks) == null ? void 0 : _a2.onMove) == null ? void 0 : _b2.call(_a2, moveEvent, session);
      };
      const onPointerUp = (endEvent) => {
        var _a2, _b2;
        element.removeEventListener("pointermove", onPointerMove);
        element.removeEventListener("pointerup", onPointerUp);
        element.removeEventListener("pointercancel", onPointerUp);
        element.style.cursor = "auto";
        (_b2 = (_a2 = session.callbacks) == null ? void 0 : _a2.onEnd) == null ? void 0 : _b2.call(_a2, endEvent, session);
      };
      element.addEventListener("pointermove", onPointerMove);
      element.addEventListener("pointerup", onPointerUp);
      element.addEventListener("pointercancel", onPointerUp);
    });
    _LfDrag_dragToResizeHandler.set(this, (element, e2) => {
      var _a, _b;
      const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
      if (!session) {
        __classPrivateFieldGet$6(this, _LfDrag_MANAGER, "f").debug.logs.new(this, "Attempted to interact with an unregistered element.", "warning");
        return;
      }
      const startWidth = element.offsetWidth;
      const startHeight = element.offsetHeight;
      const startX = e2.clientX;
      const startY = e2.clientY;
      (_b = (_a = session.callbacks) == null ? void 0 : _a.onStart) == null ? void 0 : _b.call(_a, e2, session);
      element.style.cursor = "nwse-resize";
      const onPointerMove = (moveEvent) => {
        var _a2, _b2;
        const deltaX = moveEvent.clientX - startX;
        const deltaY = moveEvent.clientY - startY;
        session.dragData = {
          ...session.dragData,
          startX,
          startY,
          deltaX,
          deltaY,
          lastX: moveEvent.clientX,
          lastY: moveEvent.clientY,
          startScrollLeft: 0,
          startScrollTop: 0,
          lastScrollLeft: 0,
          lastScrollTop: 0
        };
        element.style.width = `${startWidth + deltaX}px`;
        element.style.height = `${startHeight + deltaY}px`;
        (_b2 = (_a2 = session.callbacks) == null ? void 0 : _a2.onMove) == null ? void 0 : _b2.call(_a2, moveEvent, session);
      };
      const onPointerUp = (endEvent) => {
        var _a2, _b2;
        element.removeEventListener("pointermove", onPointerMove);
        element.removeEventListener("pointerup", onPointerUp);
        element.removeEventListener("pointercancel", onPointerUp);
        element.style.cursor = "auto";
        (_b2 = (_a2 = session.callbacks) == null ? void 0 : _a2.onEnd) == null ? void 0 : _b2.call(_a2, endEvent, session);
      };
      element.addEventListener("pointermove", onPointerMove);
      element.addEventListener("pointerup", onPointerUp);
      element.addEventListener("pointercancel", onPointerUp);
    });
    _LfDrag_dragToScrollHandler.set(this, (element, e2, direction = "x", distX, distY) => {
      var _a, _b;
      const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
      if (!session) {
        __classPrivateFieldGet$6(this, _LfDrag_MANAGER, "f").debug.logs.new(this, "Attempted to interact with an unregistered element.", "warning");
        return;
      }
      element.setPointerCapture(e2.pointerId);
      const startX = e2.clientX - distX;
      const startY = e2.clientY - distY;
      const startScrollLeft = element.scrollLeft;
      const startScrollTop = element.scrollTop;
      const startTime = performance.now();
      (_b = (_a = session.callbacks) == null ? void 0 : _a.onStart) == null ? void 0 : _b.call(_a, e2, session);
      element.style.cursor = "grabbing";
      element.style.userSelect = "none";
      const onPointerMove = (moveEvent) => {
        var _a2, _b2, _c;
        const currentTime = performance.now();
        const timeDelta = currentTime - (((_a2 = session.dragData) == null ? void 0 : _a2.lastMoveTime) || startTime);
        const deltaX = moveEvent.clientX - startX;
        const deltaY = moveEvent.clientY - startY;
        switch (direction) {
          case "x":
            element.scrollLeft = startScrollLeft - deltaX;
            break;
          case "y":
            element.scrollTop = startScrollTop - deltaY;
            break;
        }
        const newVelocityX = -(deltaX / timeDelta);
        const newVelocityY = -(deltaY / timeDelta);
        session.dragData = {
          startX,
          startY,
          startScrollLeft,
          startScrollTop,
          velocityX: newVelocityX,
          velocityY: newVelocityY,
          lastMoveTime: currentTime,
          deltaX: moveEvent.clientX - startX,
          deltaY: moveEvent.clientY - startY,
          lastX: moveEvent.clientX,
          lastY: moveEvent.clientY,
          lastScrollLeft: element.scrollLeft,
          lastScrollTop: element.scrollTop
        };
        (_c = (_b2 = session.callbacks) == null ? void 0 : _b2.onMove) == null ? void 0 : _c.call(_b2, moveEvent, session);
      };
      const onPointerUp = (endEvent) => {
        var _a2, _b2, _c, _d;
        element.releasePointerCapture(endEvent.pointerId);
        element.removeEventListener("pointermove", onPointerMove);
        element.removeEventListener("pointerup", onPointerUp);
        element.removeEventListener("pointercancel", onPointerUp);
        if (!__classPrivateFieldGet$6(this, _LfDrag_REDUCED_MOTION, "f")) {
          let vx = ((_a2 = session.dragData) == null ? void 0 : _a2.velocityX) ?? 0;
          let vy = ((_b2 = session.dragData) == null ? void 0 : _b2.velocityY) ?? 0;
          const momentumFactor = 1;
          const momentumScroll = () => {
            if (Math.abs(vx) > 0.1) {
              switch (direction) {
                case "x":
                  element.scrollLeft += vx * momentumFactor;
                  break;
                case "y":
                  element.scrollTop += vy * momentumFactor;
                  break;
              }
              vx *= 0.95;
              vy *= 0.95;
              requestAnimationFrame(momentumScroll);
            }
          };
          momentumScroll();
        }
        element.setAttribute("aria-grabbed", "false");
        (_d = (_c = session.callbacks) == null ? void 0 : _c.onEnd) == null ? void 0 : _d.call(_c, endEvent, session);
      };
      element.addEventListener("pointermove", onPointerMove);
      element.addEventListener("pointerup", onPointerUp);
      element.addEventListener("pointercancel", onPointerUp);
    });
    _LfDrag_swipeHandler.set(this, (element, e2, direction = "x") => {
      var _a, _b;
      const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
      if (!session) {
        __classPrivateFieldGet$6(this, _LfDrag_MANAGER, "f").debug.logs.new(this, "Attempted to interact with an unregistered element.", "warning");
        return;
      }
      const swipeThreshold = 50;
      const startX = e2.clientX;
      const startY = e2.clientY;
      if (!session.swipeData) {
        session.swipeData = { direction: null };
        (_b = (_a = session.callbacks) == null ? void 0 : _a.onStart) == null ? void 0 : _b.call(_a, e2, session);
      }
      let hasPreventedDefault = false;
      const onPointerMove = (moveEvent) => {
        var _a2, _b2;
        const currentDistX = moveEvent.clientX - startX;
        const currentDistY = moveEvent.clientY - startY;
        const deltaX = Math.abs(currentDistX);
        const deltaY = Math.abs(currentDistY);
        if (deltaX > deltaY && deltaX > swipeThreshold) {
          if (!hasPreventedDefault && moveEvent.cancelable) {
            moveEvent.preventDefault();
            hasPreventedDefault = true;
          }
        }
        if (direction === "x" && deltaX > swipeThreshold) {
          session.swipeData.direction = currentDistX > 0 ? "right" : "left";
        } else if (direction === "y" && deltaY > swipeThreshold) {
          session.swipeData.direction = currentDistY > 0 ? "down" : "up";
        }
        (_b2 = (_a2 = session.callbacks) == null ? void 0 : _a2.onMove) == null ? void 0 : _b2.call(_a2, moveEvent, session);
      };
      const onPointerUp = (endEvent) => {
        var _a2, _b2, _c;
        element.removeEventListener("pointermove", onPointerMove);
        element.removeEventListener("pointerup", onPointerUp);
        element.removeEventListener("pointercancel", onPointerUp);
        if ((_a2 = session.swipeData) == null ? void 0 : _a2.direction) {
          (_c = (_b2 = session.callbacks) == null ? void 0 : _b2.onEnd) == null ? void 0 : _c.call(_b2, endEvent, session);
        }
        session.swipeData = null;
        hasPreventedDefault = false;
      };
      element.addEventListener("pointermove", onPointerMove);
      element.addEventListener("pointerup", onPointerUp);
      element.addEventListener("pointercancel", onPointerUp);
    });
    this.register = {
      /**
       * Registers a custom drag behavior. The user must provide their own onPointerDown handler.
       * The user can also provide optional callbacks (onMove, onEnd).
       * If the user does NOT provide their own onMove/onEnd, the default behavior is to call the defaultPointerMoveAndUp handler.
       *
       * @param element The element to register custom drag behavior on.
       * @param onPointerDown The user-provided handler for pointerdown events.
       * @param callbacks Optional callbacks for onMove, onEnd.
       *
       * @example
       * lfDrag.register.customDrag(element, (e, session) => {
       *  console.log("Custom drag started!");
       * }, {
       * onMove: (e, session) => {
       *  console.log("Custom dragging...");
       * },
       * onEnd: (e, session) => {
       *  console.log("Custom drag ended!");
       * },
       * });
       */
      customDrag: (element, onPointerDown, callbacks = {}) => {
        __classPrivateFieldGet$6(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2) => {
          const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
          if (!session) {
            console.warn("Attempted to interact with an unregistered element.");
            return;
          }
          onPointerDown(e2, session);
          if (!callbacks.onMove && !callbacks.onEnd) {
            __classPrivateFieldGet$6(this, _LfDrag_defaultPointerMoveAndUp, "f").call(this, element, session);
          }
        });
      },
      /**
       * Registers a skeleton for drag-to-drop.
       */
      dragToDrop: (element, callbacks) => {
        __classPrivateFieldGet$6(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2) => {
          __classPrivateFieldGet$6(this, _LfDrag_dragToDropHandler, "f").call(this, element, e2);
        });
      },
      /**
       * Registers a skeleton for drag-to-resize.
       */
      dragToResize: (element, callbacks) => {
        __classPrivateFieldGet$6(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2) => {
          __classPrivateFieldGet$6(this, _LfDrag_dragToResizeHandler, "f").call(this, element, e2);
        });
      },
      /**
       * Registers drag-to-scroll behavior for the element. The user can supply
       * optional callbacks (onStart, onMove, onEnd). This includes velocity + momentum.
       *
       * @param element The element to register drag-to-scroll behavior on.
       * @param callbacks Optional callbacks for onStart, onMove, onEnd.
       * @param direction Optional direction to scroll in (x, y, or both).
       *
       * @example
       * lfDrag.register.dragToScroll(element, {
       *  onStart: (e, session) => {
       *   console.log("Drag started!");
       * },
       *  onMove: (e, session) => {
       *   console.log("Dragging...");
       * },
       *  onEnd: (e, session) => {
       *   console.log("Drag ended!");
       * },
       * });
       */
      dragToScroll: (element, callbacks, direction = "x") => {
        __classPrivateFieldGet$6(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2, distX, distY) => {
          __classPrivateFieldGet$6(this, _LfDrag_dragToScrollHandler, "f").call(this, element, e2, direction, distX, distY);
        });
      },
      /**
       * Registers a swipe handler for the element. The user can supply optional callbacks (onStart, onMove, onEnd).
       *
       * @param element The element to register swipe behavior on.
       * @param callbacks Optional callbacks for onStart, onMove, onEnd.
       * @param direction Optional direction to swipe in (x, y).
       *
       * @example
       * lfDrag.register.swipe(element, {
       *  onStart: (e, session) => {
       *   console.log("Swipe started!");
       * },
       *  onMove: (e, session) => {
       *   console.log("Swiping...");
       * },
       *  onEnd: (e, session) => {
       *   console.log("Swipe ended!");
       * },
       * });
       */
      swipe: (element, callbacks, direction = "x") => {
        __classPrivateFieldGet$6(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2) => {
          __classPrivateFieldGet$6(this, _LfDrag_swipeHandler, "f").call(this, element, e2, direction);
        });
      }
    };
    this.unregister = {
      /**
       * Unregisters any of the standard behaviors (scroll, drop, resize, etc.)
       * by simply calling the session's cleanupCb, then removing the session from the map.
       *
       * @param element The element to unregister drag behavior from.
       *
       * @example
       * lfDrag.unregister.all(element);
       */
      all: (element) => {
        const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
        if (!session)
          return;
        session.cleanupCb();
        __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").delete(element);
      },
      /**
       * Unregisters custom drag behavior from an element.
       *
       * @param element The element to unregister custom drag behavior from.
       *
       * @example
       * lfDrag.unregister.customDrag(element);
       */
      customDrag: (element) => {
        const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").delete(element);
      },
      /**
       * Unregisters drag-to-drop behavior from an element.
       *
       * @param element The element to unregister drag-to-drop behavior from.
       *
       * @example
       * lfDrag.unregister.dragToDrop(element);
       */
      dragToDrop: (element) => {
        const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").delete(element);
      },
      /**
       * Unregisters drag-to-resize behavior from an element.
       *
       * @param element The element to unregister drag-to-resize behavior from.
       *
       * @example
       * lfDrag.unregister.dragToResize(element);
       */
      dragToResize: (element) => {
        const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").delete(element);
      },
      /**
       * Unregisters drag-to-scroll behavior from an element.
       *
       * @param element The element to unregister drag-to-scroll behavior from.
       *
       * @example
       * lfDrag.unregister.dragToScroll(element);
       */
      dragToScroll: (element) => {
        const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").delete(element);
      },
      /**
       * Unregisters swipe behavior from an element.
       *
       * @param element The element to unregister swipe behavior from.
       *
       * @example
       * lfDrag.unregister.swipe(element);
       */
      swipe: (element) => {
        const session = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").delete(element);
      }
    };
    __classPrivateFieldSet$6(this, _LfDrag_MANAGER, lfFramework2, "f");
  }
  //#endregion
  //#region getActiveSession
  /**
   * Public API to get the active session for an element, if any.
   *
   * @param element The element to get the active session for.
   *
   * @example
   * const session = lfDrag.getActiveSession(element);
   * if (session) {
   * console.log("Session is active!");
   * }
   */
  getActiveSession(element) {
    return __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element);
  }
}
_LfDrag_IS_DRAGGING = /* @__PURE__ */ new WeakMap(), _LfDrag_DRAG_THRESHOLD = /* @__PURE__ */ new WeakMap(), _LfDrag_MANAGER = /* @__PURE__ */ new WeakMap(), _LfDrag_POINTER_ID = /* @__PURE__ */ new WeakMap(), _LfDrag_REDUCED_MOTION = /* @__PURE__ */ new WeakMap(), _LfDrag_SESSIONS = /* @__PURE__ */ new WeakMap(), _LfDrag_defaultPointerMoveAndUp = /* @__PURE__ */ new WeakMap(), _LfDrag_dragToDropHandler = /* @__PURE__ */ new WeakMap(), _LfDrag_dragToResizeHandler = /* @__PURE__ */ new WeakMap(), _LfDrag_dragToScrollHandler = /* @__PURE__ */ new WeakMap(), _LfDrag_swipeHandler = /* @__PURE__ */ new WeakMap(), _LfDrag_instances = /* @__PURE__ */ new WeakSet(), _LfDrag_initializeSession = function _LfDrag_initializeSession2(element, callbacks = {}, dragLogicHandler) {
  var _a;
  (_a = __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").get(element)) == null ? void 0 : _a.cleanupCb();
  __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").delete(element);
  const removeThresholdListeners = __classPrivateFieldGet$6(this, _LfDrag_instances, "m", _LfDrag_setupThresholdAwarePointerDown).call(this, element, __classPrivateFieldGet$6(this, _LfDrag_DRAG_THRESHOLD, "f"), (moveEvent, distX, distY) => {
    dragLogicHandler(moveEvent, distX, distY);
  });
  const session = {
    cleanupCb: () => {
      removeThresholdListeners();
      element.style.cursor = "auto";
      element.style.userSelect = "auto";
      element.removeAttribute("aria-grabbed");
      delete element.dataset.lf;
    },
    element,
    callbacks,
    dragData: void 0
  };
  __classPrivateFieldGet$6(this, _LfDrag_SESSIONS, "f").set(element, session);
}, _LfDrag_setupThresholdAwarePointerDown = function _LfDrag_setupThresholdAwarePointerDown2(element, threshold, startDragHandler) {
  let pointerDownX = 0;
  let pointerDownY = 0;
  __classPrivateFieldSet$6(this, _LfDrag_IS_DRAGGING, false, "f");
  __classPrivateFieldSet$6(this, _LfDrag_POINTER_ID, null, "f");
  const onPointerDown = (e2) => {
    pointerDownX = e2.clientX;
    pointerDownY = e2.clientY;
    __classPrivateFieldSet$6(this, _LfDrag_IS_DRAGGING, false, "f");
    __classPrivateFieldSet$6(this, _LfDrag_POINTER_ID, e2.pointerId, "f");
  };
  const onPointerMove = (moveEvent) => {
    if (__classPrivateFieldGet$6(this, _LfDrag_POINTER_ID, "f") === null) {
      return;
    }
    const distX = moveEvent.clientX - pointerDownX;
    const distY = moveEvent.clientY - pointerDownY;
    const distance = Math.sqrt(distX ** 2 + distY ** 2);
    if (!__classPrivateFieldGet$6(this, _LfDrag_IS_DRAGGING, "f") && distance > threshold) {
      __classPrivateFieldSet$6(this, _LfDrag_IS_DRAGGING, true, "f");
      moveEvent.preventDefault();
      element.setPointerCapture(moveEvent.pointerId);
      startDragHandler(moveEvent, distX, distY);
    }
  };
  const onPointerUp = (_upEvent) => {
    __classPrivateFieldSet$6(this, _LfDrag_POINTER_ID, null, "f");
  };
  element.addEventListener("pointerdown", onPointerDown);
  element.addEventListener("pointermove", onPointerMove);
  element.addEventListener("pointerup", onPointerUp);
  element.addEventListener("pointercancel", onPointerUp);
  return () => {
    element.removeEventListener("pointerdown", onPointerDown);
    element.removeEventListener("pointermove", onPointerMove);
    element.removeEventListener("pointerup", onPointerUp);
    element.removeEventListener("pointercancel", onPointerUp);
  };
};
var __classPrivateFieldSet$5 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$5 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfEffects_BACKDROP, _LfEffects_COMPONENTS, _LfEffects_EFFECTS, _LfEffects_INTENSITY, _LfEffects_LIGHTBOX, _LfEffects_MANAGER, _LfEffects_TIMEOUT, _LfEffects_appendToWrapper, _LfEffects_getParentStyle;
class LfEffects {
  constructor(lfFramework2) {
    _LfEffects_BACKDROP.set(this, null);
    _LfEffects_COMPONENTS.set(this, /* @__PURE__ */ new Set());
    _LfEffects_EFFECTS.set(this, void 0);
    _LfEffects_INTENSITY.set(this, {
      tilt: 10
    });
    _LfEffects_LIGHTBOX.set(this, null);
    _LfEffects_MANAGER.set(this, void 0);
    _LfEffects_TIMEOUT.set(this, {
      lightbox: 300,
      ripple: 500
    });
    _LfEffects_appendToWrapper.set(this, (element) => {
      if (typeof document === "undefined") {
        return;
      }
      if (!__classPrivateFieldGet$5(this, _LfEffects_EFFECTS, "f")) {
        __classPrivateFieldSet$5(this, _LfEffects_EFFECTS, document.createElement("div"), "f");
        __classPrivateFieldGet$5(this, _LfEffects_EFFECTS, "f").classList.add("lf-effects");
        __classPrivateFieldGet$5(this, _LfEffects_EFFECTS, "f").dataset.cy = CY_ATTRIBUTES.effects;
        document.body.appendChild(__classPrivateFieldGet$5(this, _LfEffects_EFFECTS, "f"));
      }
      __classPrivateFieldGet$5(this, _LfEffects_EFFECTS, "f").appendChild(element);
    });
    _LfEffects_getParentStyle.set(this, (element) => {
      const { parentElement } = element;
      const { backgroundColor, borderRadius, color } = getComputedStyle(parentElement);
      return {
        backgroundColor,
        borderRadius,
        color
      };
    });
    this.set = {
      intensity: (key, value) => __classPrivateFieldGet$5(this, _LfEffects_INTENSITY, "f")[key] = value,
      timeout: (key, value) => __classPrivateFieldGet$5(this, _LfEffects_TIMEOUT, "f")[key] = value
    };
    this.backdrop = {
      hide: () => {
        if (!__classPrivateFieldGet$5(this, _LfEffects_BACKDROP, "f")) {
          return;
        }
        const backdrop = __classPrivateFieldGet$5(this, _LfEffects_BACKDROP, "f");
        backdrop.style.opacity = "0";
        backdrop.addEventListener("transitionend", () => {
          backdrop.remove();
          __classPrivateFieldSet$5(this, _LfEffects_BACKDROP, null, "f");
        });
      },
      isVisible: () => !!__classPrivateFieldGet$5(this, _LfEffects_BACKDROP, "f"),
      show: (onClose) => {
        const { logs } = __classPrivateFieldGet$5(this, _LfEffects_MANAGER, "f").debug;
        if (__classPrivateFieldGet$5(this, _LfEffects_BACKDROP, "f")) {
          logs.new(this, "A modal is already open.", "warning");
          return;
        }
        const backdrop = document.createElement("div");
        backdrop.setAttribute("data-lf", LF_ATTRIBUTES.backdrop);
        backdrop.addEventListener("click", (e2) => {
          e2.preventDefault();
          e2.stopPropagation();
        });
        backdrop.addEventListener("pointerdown", (e2) => {
          e2.preventDefault();
          e2.stopPropagation();
          if (onClose) {
            onClose();
          }
        });
        backdrop.addEventListener("touchstart", (e2) => {
          e2.preventDefault();
          e2.stopPropagation();
        }, { passive: false });
        __classPrivateFieldGet$5(this, _LfEffects_appendToWrapper, "f").call(this, backdrop);
        requestAnimationFrame(() => {
          backdrop.style.opacity = "1";
        });
        __classPrivateFieldSet$5(this, _LfEffects_BACKDROP, backdrop, "f");
      }
    };
    this.lightbox = {
      show: async (element, closeCb) => {
        const { debug } = __classPrivateFieldGet$5(this, _LfEffects_MANAGER, "f");
        if (__classPrivateFieldGet$5(this, _LfEffects_LIGHTBOX, "f")) {
          debug.logs.new(this, "Lightbox is already open.", "warning");
          return;
        }
        const clone = element.cloneNode(true);
        if (element.tagName.startsWith("LF-") && "getProps" in element) {
          const props = await element.getProps();
          Object.assign(clone, props);
        }
        clone.setAttribute("data-lf", LF_ATTRIBUTES.lightboxContent);
        clone.setAttribute("role", "dialog");
        clone.setAttribute("aria-modal", "true");
        clone.setAttribute("tabindex", "-1");
        const escKeyHandler = (e2) => {
          if (e2.key === "Escape") {
            this.lightbox.hide();
          }
        };
        clone.addEventListener("keydown", escKeyHandler);
        const originalHide = this.lightbox.hide;
        this.lightbox.hide = () => {
          if (closeCb) {
            closeCb();
          }
          originalHide.call(this.lightbox);
          document.removeEventListener("keydown", escKeyHandler);
          this.lightbox.hide = originalHide;
        };
        const portal = document.createElement("div");
        portal.setAttribute("data-lf", LF_ATTRIBUTES.lightbox);
        portal.appendChild(clone);
        __classPrivateFieldGet$5(this, _LfEffects_appendToWrapper, "f").call(this, portal);
        __classPrivateFieldSet$5(this, _LfEffects_LIGHTBOX, portal, "f");
        this.backdrop.show(() => this.lightbox.hide());
        requestAnimationFrame(async () => {
          clone.focus();
        });
      },
      hide: () => {
        if (!__classPrivateFieldGet$5(this, _LfEffects_LIGHTBOX, "f")) {
          return;
        }
        __classPrivateFieldGet$5(this, _LfEffects_LIGHTBOX, "f").remove();
        __classPrivateFieldSet$5(this, _LfEffects_LIGHTBOX, null, "f");
        this.backdrop.hide();
      },
      isVisible: () => !!__classPrivateFieldGet$5(this, _LfEffects_LIGHTBOX, "f")
    };
    this.ripple = (e2, element, autoSurfaceRadius = true) => {
      if (!element) {
        return;
      }
      const ripple = document.createElement("span");
      const { left, height: h2, top, width: w2 } = element.getBoundingClientRect();
      const { backgroundColor, borderRadius, color } = __classPrivateFieldGet$5(this, _LfEffects_getParentStyle, "f").call(this, element);
      const rippleX = e2.clientX - left - w2 / 2;
      const rippleY = e2.clientY - top - h2 / 2;
      if (autoSurfaceRadius) {
        element.style.borderRadius = borderRadius;
      }
      const { background, height, width, x: x2, y: y2 } = LF_EFFECTS_VARS.ripple;
      ripple.dataset.lf = LF_ATTRIBUTES.ripple;
      ripple.style.setProperty(background, color || backgroundColor);
      ripple.style.setProperty(height, `${h2}px`);
      ripple.style.setProperty(width, `${w2}px`);
      ripple.style.setProperty(x2, `${rippleX}px`);
      ripple.style.setProperty(y2, `${rippleY}px`);
      element.appendChild(ripple);
      setTimeout(() => requestAnimationFrame(async () => {
        ripple.remove();
      }), __classPrivateFieldGet$5(this, _LfEffects_TIMEOUT, "f").ripple);
    };
    this.isRegistered = (element) => __classPrivateFieldGet$5(this, _LfEffects_COMPONENTS, "f").has(element);
    this.register = {
      tilt: (element, intensity = 10) => {
        const { tilt } = LF_EFFECTS_VARS;
        element.addEventListener("pointermove", (e2) => {
          const { clientX, clientY } = e2;
          const { height, left, top, width } = element.getBoundingClientRect();
          const x2 = (clientX - left) / width * 100;
          const y2 = (clientY - top) / height * 100;
          element.style.setProperty(tilt.x, `${((clientX - left) / width - 0.5) * intensity}deg`);
          element.style.setProperty(tilt.y, `${-((clientY - top) / height - 0.5) * intensity}deg`);
          element.style.setProperty(tilt.lightX, `${x2}%`);
          element.style.setProperty(tilt.lightY, `${y2}%`);
        });
        element.addEventListener("pointerleave", () => {
          element.style.setProperty(tilt.x, "0deg");
          element.style.setProperty(tilt.y, "0deg");
          element.style.setProperty(tilt.lightX, "50%");
          element.style.setProperty(tilt.lightY, "50%");
        });
        element.dataset.lf = LF_ATTRIBUTES.tilt;
        __classPrivateFieldGet$5(this, _LfEffects_COMPONENTS, "f").add(element);
      }
    };
    this.unregister = {
      tilt: (element) => {
        element.removeEventListener("pointermove", () => {
        });
        element.removeEventListener("pointerleave", () => {
        });
        __classPrivateFieldGet$5(this, _LfEffects_COMPONENTS, "f").delete(element);
      }
    };
    __classPrivateFieldSet$5(this, _LfEffects_MANAGER, lfFramework2, "f");
  }
}
_LfEffects_BACKDROP = /* @__PURE__ */ new WeakMap(), _LfEffects_COMPONENTS = /* @__PURE__ */ new WeakMap(), _LfEffects_EFFECTS = /* @__PURE__ */ new WeakMap(), _LfEffects_INTENSITY = /* @__PURE__ */ new WeakMap(), _LfEffects_LIGHTBOX = /* @__PURE__ */ new WeakMap(), _LfEffects_MANAGER = /* @__PURE__ */ new WeakMap(), _LfEffects_TIMEOUT = /* @__PURE__ */ new WeakMap(), _LfEffects_appendToWrapper = /* @__PURE__ */ new WeakMap(), _LfEffects_getParentStyle = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldSet$4 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$4 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfLLM_DONE_RESPONSE, _LfLLM_IS_ABORT_ERROR, _LfLLM_LF_MANAGER;
class LfLLM {
  constructor(lfFramework2) {
    _LfLLM_DONE_RESPONSE.set(this, "data: [DONE]");
    _LfLLM_IS_ABORT_ERROR.set(this, (e2) => e2 instanceof DOMException && e2.name === "AbortError");
    _LfLLM_LF_MANAGER.set(this, void 0);
    this.utils = {
      hash: (request) => {
        const prune = (obj) => {
          if (obj === null || typeof obj !== "object")
            return obj;
          if (Array.isArray(obj))
            return obj.map(prune);
          const original = obj;
          const out = {};
          Object.keys(original).sort().forEach((k2) => {
            const v2 = original[k2];
            if (v2 === void 0)
              return;
            out[k2] = prune(v2);
          });
          return out;
        };
        const base2 = prune({
          model: request.model,
          messages: request.messages,
          prompt: request.prompt,
          max_tokens: request.max_tokens,
          temperature: request.temperature,
          top_p: request.top_p,
          stop: request.stop,
          presence_penalty: request.presence_penalty,
          frequency_penalty: request.frequency_penalty,
          seed: request.seed
        });
        const str = JSON.stringify(base2);
        let h2 = 2166136261;
        for (let i2 = 0; i2 < str.length; i2++) {
          h2 ^= str.charCodeAt(i2);
          h2 = h2 + (h2 << 1) + (h2 << 4) + (h2 << 7) + (h2 << 8) + (h2 << 24) >>> 0;
        }
        return h2.toString(16);
      },
      estimateTokens: (messages) => {
        let chars = 0;
        messages.forEach((m2) => {
          chars += m2.content.length + m2.role.length + 4;
        });
        return Math.ceil(chars / 4);
      }
    };
    this.fetch = async (request, url) => {
      try {
        const response = await fetch(`${url}/v1/chat/completions`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(request)
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
      } catch (error2) {
        console.error("Error calling LLM:", error2);
        throw error2;
      }
    };
    this.poll = async (url) => {
      return fetch(url);
    };
    this.createAbort = () => new AbortController();
    this.stream = async function* (request, url, opts) {
      var _a, _b, _c, _d, _e, _f, _g, _h, _i, _j, _k, _l, _m, _n, _o, _p;
      const payload = { ...request, stream: request.stream ?? true };
      let response = null;
      try {
        response = await fetch(`${url}/v1/chat/completions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal: opts == null ? void 0 : opts.signal
        });
      } catch (e2) {
        if (__classPrivateFieldGet$4(this, _LfLLM_IS_ABORT_ERROR, "f").call(this, e2)) {
          return;
        }
        throw e2;
      }
      if (!response || !response.ok) {
        throw new Error(`HTTP error! status: ${response == null ? void 0 : response.status}`);
      }
      const reader = (_a = response.body) == null ? void 0 : _a.getReader();
      if (!reader) {
        const full = await response.json();
        const text2 = ((_d = (_c = (_b = full.choices) == null ? void 0 : _b[0]) == null ? void 0 : _c.message) == null ? void 0 : _d.content) || "";
        yield { contentDelta: text2, done: true, raw: full };
        return;
      }
      const decoder = new TextDecoder();
      let buffered = "";
      while (true) {
        let result;
        try {
          result = await reader.read();
        } catch (e2) {
          if (__classPrivateFieldGet$4(this, _LfLLM_IS_ABORT_ERROR, "f").call(this, e2)) {
            return;
          }
          throw e2;
        }
        if (result.done) {
          break;
        }
        buffered += decoder.decode(result.value, { stream: true });
        const lines = buffered.split(/\r?\n/);
        buffered = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed)
            continue;
          if (trimmed === __classPrivateFieldGet$4(this, _LfLLM_DONE_RESPONSE, "f")) {
            yield { done: true };
            return;
          }
          if (trimmed.startsWith("data:")) {
            const jsonPart = trimmed.slice(5).trim();
            try {
              const obj = JSON.parse(jsonPart);
              const delta = ((_g = (_f = (_e = obj.choices) == null ? void 0 : _e[0]) == null ? void 0 : _f.delta) == null ? void 0 : _g.content) || ((_j = (_i = (_h = obj.choices) == null ? void 0 : _h[0]) == null ? void 0 : _i.message) == null ? void 0 : _j.content);
              if (delta) {
                yield { contentDelta: delta, raw: obj };
              }
            } catch (_err) {
            }
          }
        }
      }
      if (buffered.trim()) {
        try {
          if (buffered.trim() === __classPrivateFieldGet$4(this, _LfLLM_DONE_RESPONSE, "f")) {
            yield { done: true };
            return;
          }
          const obj = JSON.parse(buffered.trim());
          const delta = ((_m = (_l = (_k = obj.choices) == null ? void 0 : _k[0]) == null ? void 0 : _l.delta) == null ? void 0 : _m.content) || ((_p = (_o = (_n = obj.choices) == null ? void 0 : _n[0]) == null ? void 0 : _o.message) == null ? void 0 : _p.content);
          if (delta) {
            yield { contentDelta: delta, raw: obj };
          }
        } catch {
        }
      }
      yield { done: true };
    };
    this.speechToText = async (textarea, button) => {
      const { debug } = __classPrivateFieldGet$4(this, _LfLLM_LF_MANAGER, "f");
      const speechConstructor = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!speechConstructor) {
        alert("Speech recognition is not supported in this browser.");
        return;
      }
      const recognition = new speechConstructor();
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.addEventListener("result", (event) => {
        const transcript = Array.from(event.results).map((result) => result[0]).map((result) => result.transcript).join("");
        debug.logs.new(this, "STT response: " + transcript);
        textarea.setValue(transcript);
        const isFinal = event.results[event.results.length - 1].isFinal;
        if (isFinal) {
          recognition.stop();
        }
      });
      recognition.addEventListener("end", () => {
        recognition.stop();
        button.lfShowSpinner = false;
      });
      recognition.addEventListener("start", () => {
        textarea.setFocus();
        button.lfShowSpinner = true;
      });
      try {
        recognition.start();
      } catch (err) {
        debug.logs.new(this, "Error: " + err, "error");
      }
    };
    this.withRetry = async (fn, policy) => {
      var _a, _b;
      const p2 = {
        maxAttempts: (policy == null ? void 0 : policy.maxAttempts) ?? 3,
        baseDelayMs: (policy == null ? void 0 : policy.baseDelayMs) ?? 300,
        jitter: (policy == null ? void 0 : policy.jitter) ?? true,
        retriableStatus: (policy == null ? void 0 : policy.retriableStatus) ?? [
          408,
          429,
          500,
          502,
          503,
          504
        ],
        retriableErrorNames: (policy == null ? void 0 : policy.retriableErrorNames) ?? [
          "TypeError",
          "NetworkError"
        ]
      };
      let attempt = 0;
      let lastError;
      while (attempt < p2.maxAttempts) {
        try {
          return await fn();
        } catch (e2) {
          lastError = e2;
          attempt++;
          if (__classPrivateFieldGet$4(this, _LfLLM_IS_ABORT_ERROR, "f").call(this, e2)) {
            break;
          }
          const name = e2 == null ? void 0 : e2.name;
          const message = e2 == null ? void 0 : e2.message;
          let status;
          if (message) {
            const m2 = message.match(/status:\s*(\d{3})/i);
            if (m2)
              status = parseInt(m2[1], 10);
          }
          if (status === void 0 && typeof e2 === "object" && e2 && "status" in e2) {
            const maybe = e2.status;
            if (typeof maybe === "number")
              status = maybe;
          }
          const nameOk = !name || ((_a = p2.retriableErrorNames) == null ? void 0 : _a.includes(name));
          const statusOk = status === void 0 || ((_b = p2.retriableStatus) == null ? void 0 : _b.includes(status));
          const shouldRetry = nameOk && statusOk;
          if (!shouldRetry) {
            break;
          }
          if (attempt >= p2.maxAttempts) {
            break;
          }
          const delayBase = p2.baseDelayMs * Math.pow(2, attempt - 1);
          const delay = p2.jitter ? Math.floor(Math.random() * delayBase) : delayBase;
          await new Promise((r2) => setTimeout(r2, delay));
        }
      }
      throw lastError;
    };
    __classPrivateFieldSet$4(this, _LfLLM_LF_MANAGER, lfFramework2, "f");
  }
}
_LfLLM_DONE_RESPONSE = /* @__PURE__ */ new WeakMap(), _LfLLM_IS_ABORT_ERROR = /* @__PURE__ */ new WeakMap(), _LfLLM_LF_MANAGER = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldSet$3 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$3$1 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfPortal_RAF, _LfPortal_MANAGER, _LfPortal_PORTAL, _LfPortal_STATE, _LfPortal_appendToWrapper, _LfPortal_clean, _LfPortal_schedulePositionUpdate, _LfPortal_executeRun, _LfPortal_isAnchorHTMLElement, _LfPortal_resetStyle;
class LfPortal {
  constructor(lfFramework2) {
    _LfPortal_RAF.set(this, {
      frameId: 0,
      queue: /* @__PURE__ */ new Set()
    });
    _LfPortal_MANAGER.set(this, void 0);
    _LfPortal_PORTAL.set(this, void 0);
    _LfPortal_STATE.set(this, /* @__PURE__ */ new WeakMap());
    _LfPortal_appendToWrapper.set(this, (element) => {
      if (typeof document === "undefined") {
        return;
      }
      if (!__classPrivateFieldGet$3$1(this, _LfPortal_PORTAL, "f")) {
        __classPrivateFieldSet$3(this, _LfPortal_PORTAL, document.createElement("div"), "f");
        __classPrivateFieldGet$3$1(this, _LfPortal_PORTAL, "f").classList.add("lf-portal");
        __classPrivateFieldGet$3$1(this, _LfPortal_PORTAL, "f").dataset.cy = CY_ATTRIBUTES.portal;
        document.body.appendChild(__classPrivateFieldGet$3$1(this, _LfPortal_PORTAL, "f"));
      }
      __classPrivateFieldGet$3$1(this, _LfPortal_PORTAL, "f").appendChild(element);
    });
    _LfPortal_clean.set(this, (element) => {
      if (!this.isInPortal(element)) {
        return;
      }
      const { dismissCb, parent } = __classPrivateFieldGet$3$1(this, _LfPortal_STATE, "f").get(element);
      __classPrivateFieldGet$3$1(this, _LfPortal_MANAGER, "f").removeClickCallback(dismissCb);
      if (parent) {
        parent.appendChild(element);
      }
      __classPrivateFieldGet$3$1(this, _LfPortal_STATE, "f").delete(element);
    });
    _LfPortal_schedulePositionUpdate.set(this, (element) => {
      __classPrivateFieldGet$3$1(this, _LfPortal_RAF, "f").queue.add(element);
      if (!__classPrivateFieldGet$3$1(this, _LfPortal_RAF, "f").frameId) {
        __classPrivateFieldGet$3$1(this, _LfPortal_RAF, "f").frameId = requestAnimationFrame(() => {
          __classPrivateFieldGet$3$1(this, _LfPortal_RAF, "f").frameId = 0;
          __classPrivateFieldGet$3$1(this, _LfPortal_RAF, "f").queue.forEach((el) => __classPrivateFieldGet$3$1(this, _LfPortal_executeRun, "f").call(this, el));
          __classPrivateFieldGet$3$1(this, _LfPortal_RAF, "f").queue.clear();
        });
      }
    });
    _LfPortal_executeRun.set(this, (element) => {
      if (!this.isInPortal(element) || !element.isConnected) {
        __classPrivateFieldGet$3$1(this, _LfPortal_clean, "f").call(this, element);
        return;
      }
      __classPrivateFieldGet$3$1(this, _LfPortal_resetStyle, "f").call(this, element);
      const state = __classPrivateFieldGet$3$1(this, _LfPortal_STATE, "f").get(element);
      if (!state) {
        __classPrivateFieldGet$3$1(this, _LfPortal_MANAGER, "f").debug.logs.new(this, `State for element not found.`, "warning");
        return;
      }
      const { anchor, margin, placement } = state;
      const { offsetHeight, offsetWidth, style } = element;
      style.display = "block";
      if (!__classPrivateFieldGet$3$1(this, _LfPortal_isAnchorHTMLElement, "f").call(this, anchor)) {
        const { x: x2, y: y2 } = anchor;
        const spaceBelow2 = window.innerHeight - y2;
        const spaceRight = window.innerWidth - x2;
        if (spaceBelow2 < offsetHeight && y2 > offsetHeight) {
          style.top = `${y2 - offsetHeight - margin}px`;
        } else {
          style.top = `${y2 + margin}px`;
        }
        if (spaceRight < offsetWidth && x2 > offsetWidth) {
          style.left = `${x2 - offsetWidth - margin}px`;
        } else {
          style.left = `${x2 + margin}px`;
        }
        return;
      }
      const { top, bottom, left, right } = anchor.getBoundingClientRect();
      const spaceBelow = window.innerHeight - bottom;
      const spaceAbove = top;
      const spaceOnLeft = left;
      const spaceOnRight = window.innerWidth - right;
      let verticalPart = "auto";
      let horizontalPart = "auto";
      if (placement === "auto") {
        verticalPart = "auto";
        horizontalPart = "auto";
      } else {
        const lower = placement.toLowerCase();
        if (lower.startsWith("t")) {
          verticalPart = "t";
        } else if (lower.startsWith("b")) {
          verticalPart = "b";
        } else if (lower.startsWith("l") || lower.startsWith("r")) ;
        if (lower.endsWith("l")) {
          horizontalPart = "l";
        } else if (lower.endsWith("r")) {
          horizontalPart = "r";
        }
      }
      let finalVertical = verticalPart;
      if (verticalPart === "auto") {
        if (spaceBelow >= offsetHeight || spaceBelow >= spaceAbove) {
          finalVertical = "b";
        } else {
          finalVertical = "t";
        }
      } else if (verticalPart === "b") {
        if (spaceBelow < offsetHeight && spaceAbove > offsetHeight) {
          finalVertical = "t";
        }
      } else if (verticalPart === "t") {
        if (spaceAbove < offsetHeight && spaceBelow > offsetHeight) {
          finalVertical = "b";
        }
      }
      let finalHorizontal = horizontalPart;
      if (horizontalPart === "auto") {
        if (spaceOnRight >= offsetWidth || spaceOnRight >= spaceOnLeft) {
          finalHorizontal = "r";
        } else {
          finalHorizontal = "l";
        }
      } else if (horizontalPart === "r") {
        if (spaceOnRight < offsetWidth && spaceOnLeft > offsetWidth) {
          finalHorizontal = "l";
        }
      } else if (horizontalPart === "l") {
        if (spaceOnLeft < offsetWidth && spaceOnRight > offsetWidth) {
          finalHorizontal = "r";
        }
      }
      switch (finalVertical) {
        case "t":
          style.bottom = `${window.innerHeight - top + margin}px`;
          break;
        case "b":
          style.top = `${bottom + margin}px`;
          break;
        default:
          style.top = offsetHeight < top && window.innerHeight - bottom < offsetHeight ? `${window.innerHeight - top + margin}px` : `${bottom + margin}px`;
          break;
      }
      let scrollbarWidth = window.innerWidth - document.documentElement.offsetWidth;
      if (scrollbarWidth > 30) {
        scrollbarWidth = 0;
      }
      switch (finalHorizontal) {
        case "l":
          style.left = `${left}px`;
          break;
        case "r":
          style.right = `${window.innerWidth - scrollbarWidth - right}px`;
          break;
        default:
          style.left = offsetWidth < right && window.innerWidth - left < offsetWidth ? `${window.innerWidth - scrollbarWidth - right}px` : `${left}px`;
          break;
      }
      requestAnimationFrame(() => __classPrivateFieldGet$3$1(this, _LfPortal_schedulePositionUpdate, "f").call(this, element));
    });
    _LfPortal_isAnchorHTMLElement.set(this, (anchor) => {
      return anchor.tagName !== void 0;
    });
    _LfPortal_resetStyle.set(this, (element) => {
      const { style } = element;
      style.bottom = "";
      style.display = "";
      style.left = "";
      style.right = "";
      style.top = "";
    });
    this.close = (element) => {
      __classPrivateFieldGet$3$1(this, _LfPortal_clean, "f").call(this, element);
      __classPrivateFieldGet$3$1(this, _LfPortal_resetStyle, "f").call(this, element);
    };
    this.getState = (element) => {
      return __classPrivateFieldGet$3$1(this, _LfPortal_STATE, "f").get(element);
    };
    this.isInPortal = (element) => {
      return __classPrivateFieldGet$3$1(this, _LfPortal_STATE, "f").has(element);
    };
    this.open = (element, parent, anchor = parent, margin = 0, placement = "auto") => {
      let state = __classPrivateFieldGet$3$1(this, _LfPortal_STATE, "f").get(element);
      if (state) {
        if (anchor) {
          state.anchor = anchor;
        }
        if (margin !== void 0) {
          state.margin = margin;
        }
        if (parent) {
          state.parent = parent;
        }
        if (placement) {
          state.placement = placement;
        }
      } else {
        const dismissCb = {
          cb: () => {
            this.close(element);
          },
          element
        };
        __classPrivateFieldGet$3$1(this, _LfPortal_STATE, "f").set(element, {
          anchor,
          dismissCb,
          margin,
          parent,
          placement
        });
        __classPrivateFieldGet$3$1(this, _LfPortal_MANAGER, "f").addClickCallback(dismissCb, true);
        __classPrivateFieldGet$3$1(this, _LfPortal_appendToWrapper, "f").call(this, element);
      }
      __classPrivateFieldGet$3$1(this, _LfPortal_schedulePositionUpdate, "f").call(this, element);
    };
    __classPrivateFieldSet$3(this, _LfPortal_MANAGER, lfFramework2, "f");
  }
}
_LfPortal_RAF = /* @__PURE__ */ new WeakMap(), _LfPortal_MANAGER = /* @__PURE__ */ new WeakMap(), _LfPortal_PORTAL = /* @__PURE__ */ new WeakMap(), _LfPortal_STATE = /* @__PURE__ */ new WeakMap(), _LfPortal_appendToWrapper = /* @__PURE__ */ new WeakMap(), _LfPortal_clean = /* @__PURE__ */ new WeakMap(), _LfPortal_schedulePositionUpdate = /* @__PURE__ */ new WeakMap(), _LfPortal_executeRun = /* @__PURE__ */ new WeakMap(), _LfPortal_isAnchorHTMLElement = /* @__PURE__ */ new WeakMap(), _LfPortal_resetStyle = /* @__PURE__ */ new WeakMap();
var commonjsGlobal = typeof globalThis !== "undefined" ? globalThis : typeof window !== "undefined" ? window : typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : {};
function getDefaultExportFromCjs(x2) {
  return x2 && x2.__esModule && Object.prototype.hasOwnProperty.call(x2, "default") ? x2["default"] : x2;
}
var index_cjs$4 = {};
var hasRequiredIndex_cjs$2;
function requireIndex_cjs$2() {
  if (hasRequiredIndex_cjs$2) return index_cjs$4;
  hasRequiredIndex_cjs$2 = 1;
  const decodeCache = {};
  function getDecodeCache(exclude) {
    let cache = decodeCache[exclude];
    if (cache) {
      return cache;
    }
    cache = decodeCache[exclude] = [];
    for (let i2 = 0; i2 < 128; i2++) {
      const ch = String.fromCharCode(i2);
      cache.push(ch);
    }
    for (let i2 = 0; i2 < exclude.length; i2++) {
      const ch = exclude.charCodeAt(i2);
      cache[ch] = "%" + ("0" + ch.toString(16).toUpperCase()).slice(-2);
    }
    return cache;
  }
  function decode2(string, exclude) {
    if (typeof exclude !== "string") {
      exclude = decode2.defaultChars;
    }
    const cache = getDecodeCache(exclude);
    return string.replace(/(%[a-f0-9]{2})+/gi, function(seq) {
      let result = "";
      for (let i2 = 0, l2 = seq.length; i2 < l2; i2 += 3) {
        const b1 = parseInt(seq.slice(i2 + 1, i2 + 3), 16);
        if (b1 < 128) {
          result += cache[b1];
          continue;
        }
        if ((b1 & 224) === 192 && i2 + 3 < l2) {
          const b2 = parseInt(seq.slice(i2 + 4, i2 + 6), 16);
          if ((b2 & 192) === 128) {
            const chr = b1 << 6 & 1984 | b2 & 63;
            if (chr < 128) {
              result += "��";
            } else {
              result += String.fromCharCode(chr);
            }
            i2 += 3;
            continue;
          }
        }
        if ((b1 & 240) === 224 && i2 + 6 < l2) {
          const b2 = parseInt(seq.slice(i2 + 4, i2 + 6), 16);
          const b3 = parseInt(seq.slice(i2 + 7, i2 + 9), 16);
          if ((b2 & 192) === 128 && (b3 & 192) === 128) {
            const chr = b1 << 12 & 61440 | b2 << 6 & 4032 | b3 & 63;
            if (chr < 2048 || chr >= 55296 && chr <= 57343) {
              result += "���";
            } else {
              result += String.fromCharCode(chr);
            }
            i2 += 6;
            continue;
          }
        }
        if ((b1 & 248) === 240 && i2 + 9 < l2) {
          const b2 = parseInt(seq.slice(i2 + 4, i2 + 6), 16);
          const b3 = parseInt(seq.slice(i2 + 7, i2 + 9), 16);
          const b4 = parseInt(seq.slice(i2 + 10, i2 + 12), 16);
          if ((b2 & 192) === 128 && (b3 & 192) === 128 && (b4 & 192) === 128) {
            let chr = b1 << 18 & 1835008 | b2 << 12 & 258048 | b3 << 6 & 4032 | b4 & 63;
            if (chr < 65536 || chr > 1114111) {
              result += "����";
            } else {
              chr -= 65536;
              result += String.fromCharCode(55296 + (chr >> 10), 56320 + (chr & 1023));
            }
            i2 += 9;
            continue;
          }
        }
        result += "�";
      }
      return result;
    });
  }
  decode2.defaultChars = ";/?:@&=+$,#";
  decode2.componentChars = "";
  const encodeCache = {};
  function getEncodeCache(exclude) {
    let cache = encodeCache[exclude];
    if (cache) {
      return cache;
    }
    cache = encodeCache[exclude] = [];
    for (let i2 = 0; i2 < 128; i2++) {
      const ch = String.fromCharCode(i2);
      if (/^[0-9a-z]$/i.test(ch)) {
        cache.push(ch);
      } else {
        cache.push("%" + ("0" + i2.toString(16).toUpperCase()).slice(-2));
      }
    }
    for (let i2 = 0; i2 < exclude.length; i2++) {
      cache[exclude.charCodeAt(i2)] = exclude[i2];
    }
    return cache;
  }
  function encode2(string, exclude, keepEscaped) {
    if (typeof exclude !== "string") {
      keepEscaped = exclude;
      exclude = encode2.defaultChars;
    }
    if (typeof keepEscaped === "undefined") {
      keepEscaped = true;
    }
    const cache = getEncodeCache(exclude);
    let result = "";
    for (let i2 = 0, l2 = string.length; i2 < l2; i2++) {
      const code2 = string.charCodeAt(i2);
      if (keepEscaped && code2 === 37 && i2 + 2 < l2) {
        if (/^[0-9a-f]{2}$/i.test(string.slice(i2 + 1, i2 + 3))) {
          result += string.slice(i2, i2 + 3);
          i2 += 2;
          continue;
        }
      }
      if (code2 < 128) {
        result += cache[code2];
        continue;
      }
      if (code2 >= 55296 && code2 <= 57343) {
        if (code2 >= 55296 && code2 <= 56319 && i2 + 1 < l2) {
          const nextCode = string.charCodeAt(i2 + 1);
          if (nextCode >= 56320 && nextCode <= 57343) {
            result += encodeURIComponent(string[i2] + string[i2 + 1]);
            i2++;
            continue;
          }
        }
        result += "%EF%BF%BD";
        continue;
      }
      result += encodeURIComponent(string[i2]);
    }
    return result;
  }
  encode2.defaultChars = ";/?:@&=+$,-_.!~*'()#";
  encode2.componentChars = "-_.!~*'()";
  function format(url) {
    let result = "";
    result += url.protocol || "";
    result += url.slashes ? "//" : "";
    result += url.auth ? url.auth + "@" : "";
    if (url.hostname && url.hostname.indexOf(":") !== -1) {
      result += "[" + url.hostname + "]";
    } else {
      result += url.hostname || "";
    }
    result += url.port ? ":" + url.port : "";
    result += url.pathname || "";
    result += url.search || "";
    result += url.hash || "";
    return result;
  }
  function Url() {
    this.protocol = null;
    this.slashes = null;
    this.auth = null;
    this.port = null;
    this.hostname = null;
    this.hash = null;
    this.search = null;
    this.pathname = null;
  }
  const protocolPattern = /^([a-z0-9.+-]+:)/i;
  const portPattern = /:[0-9]*$/;
  const simplePathPattern = /^(\/\/?(?!\/)[^\?\s]*)(\?[^\s]*)?$/;
  const delims = ["<", ">", '"', "`", " ", "\r", "\n", "	"];
  const unwise = ["{", "}", "|", "\\", "^", "`"].concat(delims);
  const autoEscape = ["'"].concat(unwise);
  const nonHostChars = ["%", "/", "?", ";", "#"].concat(autoEscape);
  const hostEndingChars = ["/", "?", "#"];
  const hostnameMaxLen = 255;
  const hostnamePartPattern = /^[+a-z0-9A-Z_-]{0,63}$/;
  const hostnamePartStart = /^([+a-z0-9A-Z_-]{0,63})(.*)$/;
  const hostlessProtocol = {
    javascript: true,
    "javascript:": true
  };
  const slashedProtocol = {
    http: true,
    https: true,
    ftp: true,
    gopher: true,
    file: true,
    "http:": true,
    "https:": true,
    "ftp:": true,
    "gopher:": true,
    "file:": true
  };
  function urlParse(url, slashesDenoteHost) {
    if (url && url instanceof Url) return url;
    const u2 = new Url();
    u2.parse(url, slashesDenoteHost);
    return u2;
  }
  Url.prototype.parse = function(url, slashesDenoteHost) {
    let lowerProto, hec, slashes;
    let rest = url;
    rest = rest.trim();
    if (!slashesDenoteHost && url.split("#").length === 1) {
      const simplePath = simplePathPattern.exec(rest);
      if (simplePath) {
        this.pathname = simplePath[1];
        if (simplePath[2]) {
          this.search = simplePath[2];
        }
        return this;
      }
    }
    let proto = protocolPattern.exec(rest);
    if (proto) {
      proto = proto[0];
      lowerProto = proto.toLowerCase();
      this.protocol = proto;
      rest = rest.substr(proto.length);
    }
    if (slashesDenoteHost || proto || rest.match(/^\/\/[^@\/]+@[^@\/]+/)) {
      slashes = rest.substr(0, 2) === "//";
      if (slashes && !(proto && hostlessProtocol[proto])) {
        rest = rest.substr(2);
        this.slashes = true;
      }
    }
    if (!hostlessProtocol[proto] && (slashes || proto && !slashedProtocol[proto])) {
      let hostEnd = -1;
      for (let i2 = 0; i2 < hostEndingChars.length; i2++) {
        hec = rest.indexOf(hostEndingChars[i2]);
        if (hec !== -1 && (hostEnd === -1 || hec < hostEnd)) {
          hostEnd = hec;
        }
      }
      let auth, atSign;
      if (hostEnd === -1) {
        atSign = rest.lastIndexOf("@");
      } else {
        atSign = rest.lastIndexOf("@", hostEnd);
      }
      if (atSign !== -1) {
        auth = rest.slice(0, atSign);
        rest = rest.slice(atSign + 1);
        this.auth = auth;
      }
      hostEnd = -1;
      for (let i2 = 0; i2 < nonHostChars.length; i2++) {
        hec = rest.indexOf(nonHostChars[i2]);
        if (hec !== -1 && (hostEnd === -1 || hec < hostEnd)) {
          hostEnd = hec;
        }
      }
      if (hostEnd === -1) {
        hostEnd = rest.length;
      }
      if (rest[hostEnd - 1] === ":") {
        hostEnd--;
      }
      const host = rest.slice(0, hostEnd);
      rest = rest.slice(hostEnd);
      this.parseHost(host);
      this.hostname = this.hostname || "";
      const ipv6Hostname = this.hostname[0] === "[" && this.hostname[this.hostname.length - 1] === "]";
      if (!ipv6Hostname) {
        const hostparts = this.hostname.split(/\./);
        for (let i2 = 0, l2 = hostparts.length; i2 < l2; i2++) {
          const part = hostparts[i2];
          if (!part) {
            continue;
          }
          if (!part.match(hostnamePartPattern)) {
            let newpart = "";
            for (let j2 = 0, k2 = part.length; j2 < k2; j2++) {
              if (part.charCodeAt(j2) > 127) {
                newpart += "x";
              } else {
                newpart += part[j2];
              }
            }
            if (!newpart.match(hostnamePartPattern)) {
              const validParts = hostparts.slice(0, i2);
              const notHost = hostparts.slice(i2 + 1);
              const bit = part.match(hostnamePartStart);
              if (bit) {
                validParts.push(bit[1]);
                notHost.unshift(bit[2]);
              }
              if (notHost.length) {
                rest = notHost.join(".") + rest;
              }
              this.hostname = validParts.join(".");
              break;
            }
          }
        }
      }
      if (this.hostname.length > hostnameMaxLen) {
        this.hostname = "";
      }
      if (ipv6Hostname) {
        this.hostname = this.hostname.substr(1, this.hostname.length - 2);
      }
    }
    const hash = rest.indexOf("#");
    if (hash !== -1) {
      this.hash = rest.substr(hash);
      rest = rest.slice(0, hash);
    }
    const qm = rest.indexOf("?");
    if (qm !== -1) {
      this.search = rest.substr(qm);
      rest = rest.slice(0, qm);
    }
    if (rest) {
      this.pathname = rest;
    }
    if (slashedProtocol[lowerProto] && this.hostname && !this.pathname) {
      this.pathname = "";
    }
    return this;
  };
  Url.prototype.parseHost = function(host) {
    let port = portPattern.exec(host);
    if (port) {
      port = port[0];
      if (port !== ":") {
        this.port = port.substr(1);
      }
      host = host.substr(0, host.length - port.length);
    }
    if (host) {
      this.hostname = host;
    }
  };
  index_cjs$4.decode = decode2;
  index_cjs$4.encode = encode2;
  index_cjs$4.format = format;
  index_cjs$4.parse = urlParse;
  return index_cjs$4;
}
var index_cjsExports$2 = requireIndex_cjs$2();
var index_cjs$3 = /* @__PURE__ */ getDefaultExportFromCjs(index_cjsExports$2);
var mdurl = /* @__PURE__ */ _mergeNamespaces({
  __proto__: null,
  default: index_cjs$3
}, [index_cjsExports$2]);
var index_cjs$2 = {};
var hasRequiredIndex_cjs$1;
function requireIndex_cjs$1() {
  if (hasRequiredIndex_cjs$1) return index_cjs$2;
  hasRequiredIndex_cjs$1 = 1;
  var regex$5 = /[\0-\uD7FF\uE000-\uFFFF]|[\uD800-\uDBFF][\uDC00-\uDFFF]|[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?:[^\uD800-\uDBFF]|^)[\uDC00-\uDFFF]/;
  var regex$4 = /[\0-\x1F\x7F-\x9F]/;
  var regex$3 = /[\xAD\u0600-\u0605\u061C\u06DD\u070F\u0890\u0891\u08E2\u180E\u200B-\u200F\u202A-\u202E\u2060-\u2064\u2066-\u206F\uFEFF\uFFF9-\uFFFB]|\uD804[\uDCBD\uDCCD]|\uD80D[\uDC30-\uDC3F]|\uD82F[\uDCA0-\uDCA3]|\uD834[\uDD73-\uDD7A]|\uDB40[\uDC01\uDC20-\uDC7F]/;
  var regex$2 = /[!-#%-\*,-\/:;\?@\[-\]_\{\}\xA1\xA7\xAB\xB6\xB7\xBB\xBF\u037E\u0387\u055A-\u055F\u0589\u058A\u05BE\u05C0\u05C3\u05C6\u05F3\u05F4\u0609\u060A\u060C\u060D\u061B\u061D-\u061F\u066A-\u066D\u06D4\u0700-\u070D\u07F7-\u07F9\u0830-\u083E\u085E\u0964\u0965\u0970\u09FD\u0A76\u0AF0\u0C77\u0C84\u0DF4\u0E4F\u0E5A\u0E5B\u0F04-\u0F12\u0F14\u0F3A-\u0F3D\u0F85\u0FD0-\u0FD4\u0FD9\u0FDA\u104A-\u104F\u10FB\u1360-\u1368\u1400\u166E\u169B\u169C\u16EB-\u16ED\u1735\u1736\u17D4-\u17D6\u17D8-\u17DA\u1800-\u180A\u1944\u1945\u1A1E\u1A1F\u1AA0-\u1AA6\u1AA8-\u1AAD\u1B5A-\u1B60\u1B7D\u1B7E\u1BFC-\u1BFF\u1C3B-\u1C3F\u1C7E\u1C7F\u1CC0-\u1CC7\u1CD3\u2010-\u2027\u2030-\u2043\u2045-\u2051\u2053-\u205E\u207D\u207E\u208D\u208E\u2308-\u230B\u2329\u232A\u2768-\u2775\u27C5\u27C6\u27E6-\u27EF\u2983-\u2998\u29D8-\u29DB\u29FC\u29FD\u2CF9-\u2CFC\u2CFE\u2CFF\u2D70\u2E00-\u2E2E\u2E30-\u2E4F\u2E52-\u2E5D\u3001-\u3003\u3008-\u3011\u3014-\u301F\u3030\u303D\u30A0\u30FB\uA4FE\uA4FF\uA60D-\uA60F\uA673\uA67E\uA6F2-\uA6F7\uA874-\uA877\uA8CE\uA8CF\uA8F8-\uA8FA\uA8FC\uA92E\uA92F\uA95F\uA9C1-\uA9CD\uA9DE\uA9DF\uAA5C-\uAA5F\uAADE\uAADF\uAAF0\uAAF1\uABEB\uFD3E\uFD3F\uFE10-\uFE19\uFE30-\uFE52\uFE54-\uFE61\uFE63\uFE68\uFE6A\uFE6B\uFF01-\uFF03\uFF05-\uFF0A\uFF0C-\uFF0F\uFF1A\uFF1B\uFF1F\uFF20\uFF3B-\uFF3D\uFF3F\uFF5B\uFF5D\uFF5F-\uFF65]|\uD800[\uDD00-\uDD02\uDF9F\uDFD0]|\uD801\uDD6F|\uD802[\uDC57\uDD1F\uDD3F\uDE50-\uDE58\uDE7F\uDEF0-\uDEF6\uDF39-\uDF3F\uDF99-\uDF9C]|\uD803[\uDEAD\uDF55-\uDF59\uDF86-\uDF89]|\uD804[\uDC47-\uDC4D\uDCBB\uDCBC\uDCBE-\uDCC1\uDD40-\uDD43\uDD74\uDD75\uDDC5-\uDDC8\uDDCD\uDDDB\uDDDD-\uDDDF\uDE38-\uDE3D\uDEA9]|\uD805[\uDC4B-\uDC4F\uDC5A\uDC5B\uDC5D\uDCC6\uDDC1-\uDDD7\uDE41-\uDE43\uDE60-\uDE6C\uDEB9\uDF3C-\uDF3E]|\uD806[\uDC3B\uDD44-\uDD46\uDDE2\uDE3F-\uDE46\uDE9A-\uDE9C\uDE9E-\uDEA2\uDF00-\uDF09]|\uD807[\uDC41-\uDC45\uDC70\uDC71\uDEF7\uDEF8\uDF43-\uDF4F\uDFFF]|\uD809[\uDC70-\uDC74]|\uD80B[\uDFF1\uDFF2]|\uD81A[\uDE6E\uDE6F\uDEF5\uDF37-\uDF3B\uDF44]|\uD81B[\uDE97-\uDE9A\uDFE2]|\uD82F\uDC9F|\uD836[\uDE87-\uDE8B]|\uD83A[\uDD5E\uDD5F]/;
  var regex$1 = /[\$\+<->\^`\|~\xA2-\xA6\xA8\xA9\xAC\xAE-\xB1\xB4\xB8\xD7\xF7\u02C2-\u02C5\u02D2-\u02DF\u02E5-\u02EB\u02ED\u02EF-\u02FF\u0375\u0384\u0385\u03F6\u0482\u058D-\u058F\u0606-\u0608\u060B\u060E\u060F\u06DE\u06E9\u06FD\u06FE\u07F6\u07FE\u07FF\u0888\u09F2\u09F3\u09FA\u09FB\u0AF1\u0B70\u0BF3-\u0BFA\u0C7F\u0D4F\u0D79\u0E3F\u0F01-\u0F03\u0F13\u0F15-\u0F17\u0F1A-\u0F1F\u0F34\u0F36\u0F38\u0FBE-\u0FC5\u0FC7-\u0FCC\u0FCE\u0FCF\u0FD5-\u0FD8\u109E\u109F\u1390-\u1399\u166D\u17DB\u1940\u19DE-\u19FF\u1B61-\u1B6A\u1B74-\u1B7C\u1FBD\u1FBF-\u1FC1\u1FCD-\u1FCF\u1FDD-\u1FDF\u1FED-\u1FEF\u1FFD\u1FFE\u2044\u2052\u207A-\u207C\u208A-\u208C\u20A0-\u20C0\u2100\u2101\u2103-\u2106\u2108\u2109\u2114\u2116-\u2118\u211E-\u2123\u2125\u2127\u2129\u212E\u213A\u213B\u2140-\u2144\u214A-\u214D\u214F\u218A\u218B\u2190-\u2307\u230C-\u2328\u232B-\u2426\u2440-\u244A\u249C-\u24E9\u2500-\u2767\u2794-\u27C4\u27C7-\u27E5\u27F0-\u2982\u2999-\u29D7\u29DC-\u29FB\u29FE-\u2B73\u2B76-\u2B95\u2B97-\u2BFF\u2CE5-\u2CEA\u2E50\u2E51\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u2FF0-\u2FFF\u3004\u3012\u3013\u3020\u3036\u3037\u303E\u303F\u309B\u309C\u3190\u3191\u3196-\u319F\u31C0-\u31E3\u31EF\u3200-\u321E\u322A-\u3247\u3250\u3260-\u327F\u328A-\u32B0\u32C0-\u33FF\u4DC0-\u4DFF\uA490-\uA4C6\uA700-\uA716\uA720\uA721\uA789\uA78A\uA828-\uA82B\uA836-\uA839\uAA77-\uAA79\uAB5B\uAB6A\uAB6B\uFB29\uFBB2-\uFBC2\uFD40-\uFD4F\uFDCF\uFDFC-\uFDFF\uFE62\uFE64-\uFE66\uFE69\uFF04\uFF0B\uFF1C-\uFF1E\uFF3E\uFF40\uFF5C\uFF5E\uFFE0-\uFFE6\uFFE8-\uFFEE\uFFFC\uFFFD]|\uD800[\uDD37-\uDD3F\uDD79-\uDD89\uDD8C-\uDD8E\uDD90-\uDD9C\uDDA0\uDDD0-\uDDFC]|\uD802[\uDC77\uDC78\uDEC8]|\uD805\uDF3F|\uD807[\uDFD5-\uDFF1]|\uD81A[\uDF3C-\uDF3F\uDF45]|\uD82F\uDC9C|\uD833[\uDF50-\uDFC3]|\uD834[\uDC00-\uDCF5\uDD00-\uDD26\uDD29-\uDD64\uDD6A-\uDD6C\uDD83\uDD84\uDD8C-\uDDA9\uDDAE-\uDDEA\uDE00-\uDE41\uDE45\uDF00-\uDF56]|\uD835[\uDEC1\uDEDB\uDEFB\uDF15\uDF35\uDF4F\uDF6F\uDF89\uDFA9\uDFC3]|\uD836[\uDC00-\uDDFF\uDE37-\uDE3A\uDE6D-\uDE74\uDE76-\uDE83\uDE85\uDE86]|\uD838[\uDD4F\uDEFF]|\uD83B[\uDCAC\uDCB0\uDD2E\uDEF0\uDEF1]|\uD83C[\uDC00-\uDC2B\uDC30-\uDC93\uDCA0-\uDCAE\uDCB1-\uDCBF\uDCC1-\uDCCF\uDCD1-\uDCF5\uDD0D-\uDDAD\uDDE6-\uDE02\uDE10-\uDE3B\uDE40-\uDE48\uDE50\uDE51\uDE60-\uDE65\uDF00-\uDFFF]|\uD83D[\uDC00-\uDED7\uDEDC-\uDEEC\uDEF0-\uDEFC\uDF00-\uDF76\uDF7B-\uDFD9\uDFE0-\uDFEB\uDFF0]|\uD83E[\uDC00-\uDC0B\uDC10-\uDC47\uDC50-\uDC59\uDC60-\uDC87\uDC90-\uDCAD\uDCB0\uDCB1\uDD00-\uDE53\uDE60-\uDE6D\uDE70-\uDE7C\uDE80-\uDE88\uDE90-\uDEBD\uDEBF-\uDEC5\uDECE-\uDEDB\uDEE0-\uDEE8\uDEF0-\uDEF8\uDF00-\uDF92\uDF94-\uDFCA]/;
  var regex = /[ \xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000]/;
  index_cjs$2.Any = regex$5;
  index_cjs$2.Cc = regex$4;
  index_cjs$2.Cf = regex$3;
  index_cjs$2.P = regex$2;
  index_cjs$2.S = regex$1;
  index_cjs$2.Z = regex;
  return index_cjs$2;
}
var index_cjsExports$1 = requireIndex_cjs$1();
var index_cjs$1 = /* @__PURE__ */ getDefaultExportFromCjs(index_cjsExports$1);
var ucmicro = /* @__PURE__ */ _mergeNamespaces({
  __proto__: null,
  default: index_cjs$1
}, [index_cjsExports$1]);
var lib$1 = {};
var decode$1 = {};
var decodeDataHtml = {};
var hasRequiredDecodeDataHtml;
function requireDecodeDataHtml() {
  if (hasRequiredDecodeDataHtml) return decodeDataHtml;
  hasRequiredDecodeDataHtml = 1;
  Object.defineProperty(decodeDataHtml, "__esModule", { value: true });
  decodeDataHtml.default = new Uint16Array(
    // prettier-ignore
    'ᵁ<Õıʊҝջאٵ۞ޢߖࠏ੊ઑඡ๭༉༦჊ረዡᐕᒝᓃᓟᔥ\0\0\0\0\0\0ᕫᛍᦍᰒᷝ὾⁠↰⊍⏀⏻⑂⠤⤒ⴈ⹈⿎〖㊺㘹㞬㣾㨨㩱㫠㬮ࠀEMabcfglmnoprstu\\bfms¦³¹ÈÏlig耻Æ䃆P耻&䀦cute耻Á䃁reve;䄂Āiyx}rc耻Â䃂;䐐r;쀀𝔄rave耻À䃀pha;䎑acr;䄀d;橓Āgp¡on;䄄f;쀀𝔸plyFunction;恡ing耻Å䃅Ācs¾Ãr;쀀𝒜ign;扔ilde耻Ã䃃ml耻Ä䃄ЀaceforsuåûþėĜĢħĪĀcrêòkslash;或Ŷöø;櫧ed;挆y;䐑ƀcrtąċĔause;戵noullis;愬a;䎒r;쀀𝔅pf;쀀𝔹eve;䋘còēmpeq;扎܀HOacdefhilorsuōőŖƀƞƢƵƷƺǜȕɳɸɾcy;䐧PY耻©䂩ƀcpyŝŢźute;䄆Ā;iŧŨ拒talDifferentialD;慅leys;愭ȀaeioƉƎƔƘron;䄌dil耻Ç䃇rc;䄈nint;戰ot;䄊ĀdnƧƭilla;䂸terDot;䂷òſi;䎧rcleȀDMPTǇǋǑǖot;抙inus;抖lus;投imes;抗oĀcsǢǸkwiseContourIntegral;戲eCurlyĀDQȃȏoubleQuote;思uote;怙ȀlnpuȞȨɇɕonĀ;eȥȦ户;橴ƀgitȯȶȺruent;扡nt;戯ourIntegral;戮ĀfrɌɎ;愂oduct;成nterClockwiseContourIntegral;戳oss;樯cr;쀀𝒞pĀ;Cʄʅ拓ap;才րDJSZacefiosʠʬʰʴʸˋ˗ˡ˦̳ҍĀ;oŹʥtrahd;椑cy;䐂cy;䐅cy;䐏ƀgrsʿ˄ˇger;怡r;憡hv;櫤Āayː˕ron;䄎;䐔lĀ;t˝˞戇a;䎔r;쀀𝔇Āaf˫̧Ācm˰̢riticalȀADGT̖̜̀̆cute;䂴oŴ̋̍;䋙bleAcute;䋝rave;䁠ilde;䋜ond;拄ferentialD;慆Ѱ̽\0\0\0͔͂\0Ѕf;쀀𝔻ƀ;DE͈͉͍䂨ot;惜qual;扐blèCDLRUVͣͲ΂ϏϢϸontourIntegraìȹoɴ͹\0\0ͻ»͉nArrow;懓Āeo·ΤftƀARTΐΖΡrrow;懐ightArrow;懔eåˊngĀLRΫτeftĀARγιrrow;柸ightArrow;柺ightArrow;柹ightĀATϘϞrrow;懒ee;抨pɁϩ\0\0ϯrrow;懑ownArrow;懕erticalBar;戥ǹABLRTaВЪаўѿͼrrowƀ;BUНОТ憓ar;椓pArrow;懵reve;䌑eft˒к\0ц\0ѐightVector;楐eeVector;楞ectorĀ;Bљњ憽ar;楖ightǔѧ\0ѱeeVector;楟ectorĀ;BѺѻ懁ar;楗eeĀ;A҆҇护rrow;憧ĀctҒҗr;쀀𝒟rok;䄐ࠀNTacdfglmopqstuxҽӀӄӋӞӢӧӮӵԡԯԶՒ՝ՠեG;䅊H耻Ð䃐cute耻É䃉ƀaiyӒӗӜron;䄚rc耻Ê䃊;䐭ot;䄖r;쀀𝔈rave耻È䃈ement;戈ĀapӺӾcr;䄒tyɓԆ\0\0ԒmallSquare;旻erySmallSquare;斫ĀgpԦԪon;䄘f;쀀𝔼silon;䎕uĀaiԼՉlĀ;TՂՃ橵ilde;扂librium;懌Āci՗՚r;愰m;橳a;䎗ml耻Ë䃋Āipժկsts;戃onentialE;慇ʀcfiosօֈ֍ֲ׌y;䐤r;쀀𝔉lledɓ֗\0\0֣mallSquare;旼erySmallSquare;斪Ͱֺ\0ֿ\0\0ׄf;쀀𝔽All;戀riertrf;愱cò׋؀JTabcdfgorstר׬ׯ׺؀ؒؖ؛؝أ٬ٲcy;䐃耻>䀾mmaĀ;d׷׸䎓;䏜reve;䄞ƀeiy؇،ؐdil;䄢rc;䄜;䐓ot;䄠r;쀀𝔊;拙pf;쀀𝔾eater̀EFGLSTصلَٖٛ٦qualĀ;Lؾؿ扥ess;招ullEqual;执reater;檢ess;扷lantEqual;橾ilde;扳cr;쀀𝒢;扫ЀAacfiosuڅڋږڛڞڪھۊRDcy;䐪Āctڐڔek;䋇;䁞irc;䄤r;愌lbertSpace;愋ǰگ\0ڲf;愍izontalLine;攀Āctۃۅòکrok;䄦mpńېۘownHumðįqual;扏܀EJOacdfgmnostuۺ۾܃܇܎ܚܞܡܨ݄ݸދޏޕcy;䐕lig;䄲cy;䐁cute耻Í䃍Āiyܓܘrc耻Î䃎;䐘ot;䄰r;愑rave耻Ì䃌ƀ;apܠܯܿĀcgܴܷr;䄪inaryI;慈lieóϝǴ݉\0ݢĀ;eݍݎ戬Āgrݓݘral;戫section;拂isibleĀCTݬݲomma;恣imes;恢ƀgptݿރވon;䄮f;쀀𝕀a;䎙cr;愐ilde;䄨ǫޚ\0ޞcy;䐆l耻Ï䃏ʀcfosuެ޷޼߂ߐĀiyޱ޵rc;䄴;䐙r;쀀𝔍pf;쀀𝕁ǣ߇\0ߌr;쀀𝒥rcy;䐈kcy;䐄΀HJacfosߤߨ߽߬߱ࠂࠈcy;䐥cy;䐌ppa;䎚Āey߶߻dil;䄶;䐚r;쀀𝔎pf;쀀𝕂cr;쀀𝒦րJTaceflmostࠥࠩࠬࡐࡣ঳সে্਷ੇcy;䐉耻<䀼ʀcmnpr࠷࠼ࡁࡄࡍute;䄹bda;䎛g;柪lacetrf;愒r;憞ƀaeyࡗ࡜ࡡron;䄽dil;䄻;䐛Āfsࡨ॰tԀACDFRTUVarࡾࢩࢱࣦ࣠ࣼयज़ΐ४Ānrࢃ࢏gleBracket;柨rowƀ;BR࢙࢚࢞憐ar;懤ightArrow;懆eiling;挈oǵࢷ\0ࣃbleBracket;柦nǔࣈ\0࣒eeVector;楡ectorĀ;Bࣛࣜ懃ar;楙loor;挊ightĀAV࣯ࣵrrow;憔ector;楎Āerँगeƀ;AVउऊऐ抣rrow;憤ector;楚iangleƀ;BEतथऩ抲ar;槏qual;抴pƀDTVषूौownVector;楑eeVector;楠ectorĀ;Bॖॗ憿ar;楘ectorĀ;B॥०憼ar;楒ightáΜs̀EFGLSTॾঋকঝঢভqualGreater;拚ullEqual;扦reater;扶ess;檡lantEqual;橽ilde;扲r;쀀𝔏Ā;eঽা拘ftarrow;懚idot;䄿ƀnpw৔ਖਛgȀLRlr৞৷ਂਐeftĀAR০৬rrow;柵ightArrow;柷ightArrow;柶eftĀarγਊightáοightáϊf;쀀𝕃erĀLRਢਬeftArrow;憙ightArrow;憘ƀchtਾੀੂòࡌ;憰rok;䅁;扪Ѐacefiosuਗ਼੝੠੷੼અઋ઎p;椅y;䐜Ādl੥੯iumSpace;恟lintrf;愳r;쀀𝔐nusPlus;戓pf;쀀𝕄cò੶;䎜ҀJacefostuણધભીଔଙඑ඗ඞcy;䐊cute;䅃ƀaey઴હાron;䅇dil;䅅;䐝ƀgswે૰଎ativeƀMTV૓૟૨ediumSpace;怋hiĀcn૦૘ë૙eryThiî૙tedĀGL૸ଆreaterGreateòٳessLesóੈLine;䀊r;쀀𝔑ȀBnptଢନଷ଺reak;恠BreakingSpace;䂠f;愕ڀ;CDEGHLNPRSTV୕ୖ୪୼஡௫ఄ౞಄ದ೘ൡඅ櫬Āou୛୤ngruent;扢pCap;扭oubleVerticalBar;戦ƀlqxஃஊ஛ement;戉ualĀ;Tஒஓ扠ilde;쀀≂̸ists;戄reater΀;EFGLSTஶஷ஽௉௓௘௥扯qual;扱ullEqual;쀀≧̸reater;쀀≫̸ess;批lantEqual;쀀⩾̸ilde;扵umpń௲௽ownHump;쀀≎̸qual;쀀≏̸eĀfsఊధtTriangleƀ;BEచఛడ拪ar;쀀⧏̸qual;括s̀;EGLSTవశ఼ౄోౘ扮qual;扰reater;扸ess;쀀≪̸lantEqual;쀀⩽̸ilde;扴estedĀGL౨౹reaterGreater;쀀⪢̸essLess;쀀⪡̸recedesƀ;ESಒಓಛ技qual;쀀⪯̸lantEqual;拠ĀeiಫಹverseElement;戌ghtTriangleƀ;BEೋೌ೒拫ar;쀀⧐̸qual;拭ĀquೝഌuareSuĀbp೨೹setĀ;E೰ೳ쀀⊏̸qual;拢ersetĀ;Eഃആ쀀⊐̸qual;拣ƀbcpഓതൎsetĀ;Eഛഞ쀀⊂⃒qual;抈ceedsȀ;ESTലള഻െ抁qual;쀀⪰̸lantEqual;拡ilde;쀀≿̸ersetĀ;E൘൛쀀⊃⃒qual;抉ildeȀ;EFT൮൯൵ൿ扁qual;扄ullEqual;扇ilde;扉erticalBar;戤cr;쀀𝒩ilde耻Ñ䃑;䎝܀Eacdfgmoprstuvලෂ෉෕ෛ෠෧෼ขภยา฿ไlig;䅒cute耻Ó䃓Āiy෎ීrc耻Ô䃔;䐞blac;䅐r;쀀𝔒rave耻Ò䃒ƀaei෮ෲ෶cr;䅌ga;䎩cron;䎟pf;쀀𝕆enCurlyĀDQฎบoubleQuote;怜uote;怘;橔Āclวฬr;쀀𝒪ash耻Ø䃘iŬื฼de耻Õ䃕es;樷ml耻Ö䃖erĀBP๋๠Āar๐๓r;怾acĀek๚๜;揞et;掴arenthesis;揜Ҁacfhilors๿ງຊຏຒດຝະ໼rtialD;戂y;䐟r;쀀𝔓i;䎦;䎠usMinus;䂱Āipຢອncareplanåڝf;愙Ȁ;eio຺ູ໠໤檻cedesȀ;EST່້໏໚扺qual;檯lantEqual;扼ilde;找me;怳Ādp໩໮uct;戏ortionĀ;aȥ໹l;戝Āci༁༆r;쀀𝒫;䎨ȀUfos༑༖༛༟OT耻"䀢r;쀀𝔔pf;愚cr;쀀𝒬؀BEacefhiorsu༾གྷཇའཱིྦྷྪྭ႖ႩႴႾarr;椐G耻®䂮ƀcnrཎནབute;䅔g;柫rĀ;tཛྷཝ憠l;椖ƀaeyཧཬཱron;䅘dil;䅖;䐠Ā;vླྀཹ愜erseĀEUྂྙĀlq྇ྎement;戋uilibrium;懋pEquilibrium;楯r»ཹo;䎡ghtЀACDFTUVa࿁࿫࿳ဢဨၛႇϘĀnr࿆࿒gleBracket;柩rowƀ;BL࿜࿝࿡憒ar;懥eftArrow;懄eiling;按oǵ࿹\0စbleBracket;柧nǔည\0နeeVector;楝ectorĀ;Bဝသ懂ar;楕loor;挋Āerိ၃eƀ;AVဵံြ抢rrow;憦ector;楛iangleƀ;BEၐၑၕ抳ar;槐qual;抵pƀDTVၣၮၸownVector;楏eeVector;楜ectorĀ;Bႂႃ憾ar;楔ectorĀ;B႑႒懀ar;楓Āpuႛ႞f;愝ndImplies;楰ightarrow;懛ĀchႹႼr;愛;憱leDelayed;槴ڀHOacfhimoqstuფჱჷჽᄙᄞᅑᅖᅡᅧᆵᆻᆿĀCcჩხHcy;䐩y;䐨FTcy;䐬cute;䅚ʀ;aeiyᄈᄉᄎᄓᄗ檼ron;䅠dil;䅞rc;䅜;䐡r;쀀𝔖ortȀDLRUᄪᄴᄾᅉownArrow»ОeftArrow»࢚ightArrow»࿝pArrow;憑gma;䎣allCircle;战pf;쀀𝕊ɲᅭ\0\0ᅰt;戚areȀ;ISUᅻᅼᆉᆯ斡ntersection;抓uĀbpᆏᆞsetĀ;Eᆗᆘ抏qual;抑ersetĀ;Eᆨᆩ抐qual;抒nion;抔cr;쀀𝒮ar;拆ȀbcmpᇈᇛሉላĀ;sᇍᇎ拐etĀ;Eᇍᇕqual;抆ĀchᇠህeedsȀ;ESTᇭᇮᇴᇿ扻qual;檰lantEqual;扽ilde;承Tháྌ;我ƀ;esሒሓሣ拑rsetĀ;Eሜም抃qual;抇et»ሓրHRSacfhiorsሾቄ቉ቕ቞ቱቶኟዂወዑORN耻Þ䃞ADE;愢ĀHc቎ቒcy;䐋y;䐦Ābuቚቜ;䀉;䎤ƀaeyብቪቯron;䅤dil;䅢;䐢r;쀀𝔗Āeiቻ኉ǲኀ\0ኇefore;戴a;䎘Ācn኎ኘkSpace;쀀  Space;怉ldeȀ;EFTካኬኲኼ戼qual;扃ullEqual;扅ilde;扈pf;쀀𝕋ipleDot;惛Āctዖዛr;쀀𝒯rok;䅦ૡዷጎጚጦ\0ጬጱ\0\0\0\0\0ጸጽ፷ᎅ\0᏿ᐄᐊᐐĀcrዻጁute耻Ú䃚rĀ;oጇገ憟cir;楉rǣጓ\0጖y;䐎ve;䅬Āiyጞጣrc耻Û䃛;䐣blac;䅰r;쀀𝔘rave耻Ù䃙acr;䅪Ādiፁ፩erĀBPፈ፝Āarፍፐr;䁟acĀekፗፙ;揟et;掵arenthesis;揝onĀ;P፰፱拃lus;抎Āgp፻፿on;䅲f;쀀𝕌ЀADETadps᎕ᎮᎸᏄϨᏒᏗᏳrrowƀ;BDᅐᎠᎤar;椒ownArrow;懅ownArrow;憕quilibrium;楮eeĀ;AᏋᏌ报rrow;憥ownáϳerĀLRᏞᏨeftArrow;憖ightArrow;憗iĀ;lᏹᏺ䏒on;䎥ing;䅮cr;쀀𝒰ilde;䅨ml耻Ü䃜ҀDbcdefosvᐧᐬᐰᐳᐾᒅᒊᒐᒖash;披ar;櫫y;䐒ashĀ;lᐻᐼ抩;櫦Āerᑃᑅ;拁ƀbtyᑌᑐᑺar;怖Ā;iᑏᑕcalȀBLSTᑡᑥᑪᑴar;戣ine;䁼eparator;杘ilde;所ThinSpace;怊r;쀀𝔙pf;쀀𝕍cr;쀀𝒱dash;抪ʀcefosᒧᒬᒱᒶᒼirc;䅴dge;拀r;쀀𝔚pf;쀀𝕎cr;쀀𝒲Ȁfiosᓋᓐᓒᓘr;쀀𝔛;䎞pf;쀀𝕏cr;쀀𝒳ҀAIUacfosuᓱᓵᓹᓽᔄᔏᔔᔚᔠcy;䐯cy;䐇cy;䐮cute耻Ý䃝Āiyᔉᔍrc;䅶;䐫r;쀀𝔜pf;쀀𝕐cr;쀀𝒴ml;䅸ЀHacdefosᔵᔹᔿᕋᕏᕝᕠᕤcy;䐖cute;䅹Āayᕄᕉron;䅽;䐗ot;䅻ǲᕔ\0ᕛoWidtè૙a;䎖r;愨pf;愤cr;쀀𝒵௡ᖃᖊᖐ\0ᖰᖶᖿ\0\0\0\0ᗆᗛᗫᙟ᙭\0ᚕ᚛ᚲᚹ\0ᚾcute耻á䃡reve;䄃̀;Ediuyᖜᖝᖡᖣᖨᖭ戾;쀀∾̳;房rc耻â䃢te肻´̆;䐰lig耻æ䃦Ā;r²ᖺ;쀀𝔞rave耻à䃠ĀepᗊᗖĀfpᗏᗔsym;愵èᗓha;䎱ĀapᗟcĀclᗤᗧr;䄁g;樿ɤᗰ\0\0ᘊʀ;adsvᗺᗻᗿᘁᘇ戧nd;橕;橜lope;橘;橚΀;elmrszᘘᘙᘛᘞᘿᙏᙙ戠;榤e»ᘙsdĀ;aᘥᘦ戡ѡᘰᘲᘴᘶᘸᘺᘼᘾ;榨;榩;榪;榫;榬;榭;榮;榯tĀ;vᙅᙆ戟bĀ;dᙌᙍ抾;榝Āptᙔᙗh;戢»¹arr;捼Āgpᙣᙧon;䄅f;쀀𝕒΀;Eaeiop዁ᙻᙽᚂᚄᚇᚊ;橰cir;橯;扊d;手s;䀧roxĀ;e዁ᚒñᚃing耻å䃥ƀctyᚡᚦᚨr;쀀𝒶;䀪mpĀ;e዁ᚯñʈilde耻ã䃣ml耻ä䃤Āciᛂᛈoninôɲnt;樑ࠀNabcdefiklnoprsu᛭ᛱᜰ᜼ᝃᝈ᝸᝽០៦ᠹᡐᜍ᤽᥈ᥰot;櫭Ācrᛶ᜞kȀcepsᜀᜅᜍᜓong;扌psilon;䏶rime;怵imĀ;e᜚᜛戽q;拍Ŷᜢᜦee;抽edĀ;gᜬᜭ挅e»ᜭrkĀ;t፜᜷brk;掶Āoyᜁᝁ;䐱quo;怞ʀcmprtᝓ᝛ᝡᝤᝨausĀ;eĊĉptyv;榰séᜌnoõēƀahwᝯ᝱ᝳ;䎲;愶een;扬r;쀀𝔟g΀costuvwឍឝឳេ៕៛៞ƀaiuបពរðݠrc;旯p»፱ƀdptឤឨឭot;樀lus;樁imes;樂ɱឹ\0\0ើcup;樆ar;昅riangleĀdu៍្own;施p;斳plus;樄eåᑄåᒭarow;植ƀako៭ᠦᠵĀcn៲ᠣkƀlst៺֫᠂ozenge;槫riangleȀ;dlr᠒᠓᠘᠝斴own;斾eft;旂ight;斸k;搣Ʊᠫ\0ᠳƲᠯ\0ᠱ;斒;斑4;斓ck;斈ĀeoᠾᡍĀ;qᡃᡆ쀀=⃥uiv;쀀≡⃥t;挐Ȁptwxᡙᡞᡧᡬf;쀀𝕓Ā;tᏋᡣom»Ꮜtie;拈؀DHUVbdhmptuvᢅᢖᢪᢻᣗᣛᣬ᣿ᤅᤊᤐᤡȀLRlrᢎᢐᢒᢔ;敗;敔;敖;敓ʀ;DUduᢡᢢᢤᢦᢨ敐;敦;敩;敤;敧ȀLRlrᢳᢵᢷᢹ;敝;敚;敜;教΀;HLRhlrᣊᣋᣍᣏᣑᣓᣕ救;敬;散;敠;敫;敢;敟ox;槉ȀLRlrᣤᣦᣨᣪ;敕;敒;攐;攌ʀ;DUduڽ᣷᣹᣻᣽;敥;敨;攬;攴inus;抟lus;択imes;抠ȀLRlrᤙᤛᤝ᤟;敛;敘;攘;攔΀;HLRhlrᤰᤱᤳᤵᤷ᤻᤹攂;敪;敡;敞;攼;攤;攜Āevģ᥂bar耻¦䂦Ȁceioᥑᥖᥚᥠr;쀀𝒷mi;恏mĀ;e᜚᜜lƀ;bhᥨᥩᥫ䁜;槅sub;柈Ŭᥴ᥾lĀ;e᥹᥺怢t»᥺pƀ;Eeįᦅᦇ;檮Ā;qۜۛೡᦧ\0᧨ᨑᨕᨲ\0ᨷᩐ\0\0᪴\0\0᫁\0\0ᬡᬮ᭍᭒\0᯽\0ᰌƀcpr᦭ᦲ᧝ute;䄇̀;abcdsᦿᧀᧄ᧊᧕᧙戩nd;橄rcup;橉Āau᧏᧒p;橋p;橇ot;橀;쀀∩︀Āeo᧢᧥t;恁îړȀaeiu᧰᧻ᨁᨅǰ᧵\0᧸s;橍on;䄍dil耻ç䃧rc;䄉psĀ;sᨌᨍ橌m;橐ot;䄋ƀdmnᨛᨠᨦil肻¸ƭptyv;榲t脀¢;eᨭᨮ䂢räƲr;쀀𝔠ƀceiᨽᩀᩍy;䑇ckĀ;mᩇᩈ朓ark»ᩈ;䏇r΀;Ecefms᩟᩠ᩢᩫ᪤᪪᪮旋;槃ƀ;elᩩᩪᩭ䋆q;扗eɡᩴ\0\0᪈rrowĀlr᩼᪁eft;憺ight;憻ʀRSacd᪒᪔᪖᪚᪟»ཇ;擈st;抛irc;抚ash;抝nint;樐id;櫯cir;槂ubsĀ;u᪻᪼晣it»᪼ˬ᫇᫔᫺\0ᬊonĀ;eᫍᫎ䀺Ā;qÇÆɭ᫙\0\0᫢aĀ;t᫞᫟䀬;䁀ƀ;fl᫨᫩᫫戁îᅠeĀmx᫱᫶ent»᫩eóɍǧ᫾\0ᬇĀ;dኻᬂot;橭nôɆƀfryᬐᬔᬗ;쀀𝕔oäɔ脀©;sŕᬝr;愗Āaoᬥᬩrr;憵ss;朗Ācuᬲᬷr;쀀𝒸Ābpᬼ᭄Ā;eᭁᭂ櫏;櫑Ā;eᭉᭊ櫐;櫒dot;拯΀delprvw᭠᭬᭷ᮂᮬᯔ᯹arrĀlr᭨᭪;椸;椵ɰ᭲\0\0᭵r;拞c;拟arrĀ;p᭿ᮀ憶;椽̀;bcdosᮏᮐᮖᮡᮥᮨ截rcap;橈Āauᮛᮞp;橆p;橊ot;抍r;橅;쀀∪︀Ȁalrv᮵ᮿᯞᯣrrĀ;mᮼᮽ憷;椼yƀevwᯇᯔᯘqɰᯎ\0\0ᯒreã᭳uã᭵ee;拎edge;拏en耻¤䂤earrowĀlrᯮ᯳eft»ᮀight»ᮽeäᯝĀciᰁᰇoninôǷnt;戱lcty;挭ঀAHabcdefhijlorstuwz᰸᰻᰿ᱝᱩᱵᲊᲞᲬᲷ᳻᳿ᴍᵻᶑᶫᶻ᷆᷍rò΁ar;楥Ȁglrs᱈ᱍ᱒᱔ger;怠eth;愸òᄳhĀ;vᱚᱛ怐»ऊūᱡᱧarow;椏aã̕Āayᱮᱳron;䄏;䐴ƀ;ao̲ᱼᲄĀgrʿᲁr;懊tseq;橷ƀglmᲑᲔᲘ耻°䂰ta;䎴ptyv;榱ĀirᲣᲨsht;楿;쀀𝔡arĀlrᲳᲵ»ࣜ»သʀaegsv᳂͸᳖᳜᳠mƀ;oș᳊᳔ndĀ;ș᳑uit;晦amma;䏝in;拲ƀ;io᳧᳨᳸䃷de脀÷;o᳧ᳰntimes;拇nø᳷cy;䑒cɯᴆ\0\0ᴊrn;挞op;挍ʀlptuwᴘᴝᴢᵉᵕlar;䀤f;쀀𝕕ʀ;emps̋ᴭᴷᴽᵂqĀ;d͒ᴳot;扑inus;戸lus;戔quare;抡blebarwedgåúnƀadhᄮᵝᵧownarrowóᲃarpoonĀlrᵲᵶefôᲴighôᲶŢᵿᶅkaro÷གɯᶊ\0\0ᶎrn;挟op;挌ƀcotᶘᶣᶦĀryᶝᶡ;쀀𝒹;䑕l;槶rok;䄑Ādrᶰᶴot;拱iĀ;fᶺ᠖斿Āah᷀᷃ròЩaòྦangle;榦Āci᷒ᷕy;䑟grarr;柿ऀDacdefglmnopqrstuxḁḉḙḸոḼṉṡṾấắẽỡἪἷὄ὎὚ĀDoḆᴴoôᲉĀcsḎḔute耻é䃩ter;橮ȀaioyḢḧḱḶron;䄛rĀ;cḭḮ扖耻ê䃪lon;払;䑍ot;䄗ĀDrṁṅot;扒;쀀𝔢ƀ;rsṐṑṗ檚ave耻è䃨Ā;dṜṝ檖ot;檘Ȁ;ilsṪṫṲṴ檙nters;揧;愓Ā;dṹṺ檕ot;檗ƀapsẅẉẗcr;䄓tyƀ;svẒẓẕ戅et»ẓpĀ1;ẝẤĳạả;怄;怅怃ĀgsẪẬ;䅋p;怂ĀgpẴẸon;䄙f;쀀𝕖ƀalsỄỎỒrĀ;sỊị拕l;槣us;橱iƀ;lvỚớở䎵on»ớ;䏵ȀcsuvỪỳἋἣĀioữḱrc»Ḯɩỹ\0\0ỻíՈantĀglἂἆtr»ṝess»Ṻƀaeiἒ἖Ἒls;䀽st;扟vĀ;DȵἠD;橸parsl;槥ĀDaἯἳot;打rr;楱ƀcdiἾὁỸr;愯oô͒ĀahὉὋ;䎷耻ð䃰Āmrὓὗl耻ë䃫o;悬ƀcipὡὤὧl;䀡sôծĀeoὬὴctatioîՙnentialåչৡᾒ\0ᾞ\0ᾡᾧ\0\0ῆῌ\0ΐ\0ῦῪ \0 ⁚llingdotseñṄy;䑄male;晀ƀilrᾭᾳ῁lig;耀ﬃɩᾹ\0\0᾽g;耀ﬀig;耀ﬄ;쀀𝔣lig;耀ﬁlig;쀀fjƀaltῙ῜ῡt;晭ig;耀ﬂns;斱of;䆒ǰ΅\0ῳf;쀀𝕗ĀakֿῷĀ;vῼ´拔;櫙artint;樍Āao‌⁕Ācs‑⁒α‚‰‸⁅⁈\0⁐β•‥‧‪‬\0‮耻½䂽;慓耻¼䂼;慕;慙;慛Ƴ‴\0‶;慔;慖ʴ‾⁁\0\0⁃耻¾䂾;慗;慜5;慘ƶ⁌\0⁎;慚;慝8;慞l;恄wn;挢cr;쀀𝒻ࢀEabcdefgijlnorstv₂₉₟₥₰₴⃰⃵⃺⃿℃ℒℸ̗ℾ⅒↞Ā;lٍ₇;檌ƀcmpₐₕ₝ute;䇵maĀ;dₜ᳚䎳;檆reve;䄟Āiy₪₮rc;䄝;䐳ot;䄡Ȁ;lqsؾق₽⃉ƀ;qsؾٌ⃄lanô٥Ȁ;cdl٥⃒⃥⃕c;檩otĀ;o⃜⃝檀Ā;l⃢⃣檂;檄Ā;e⃪⃭쀀⋛︀s;檔r;쀀𝔤Ā;gٳ؛mel;愷cy;䑓Ȁ;Eajٚℌℎℐ;檒;檥;檤ȀEaesℛℝ℩ℴ;扩pĀ;p℣ℤ檊rox»ℤĀ;q℮ℯ檈Ā;q℮ℛim;拧pf;쀀𝕘Āci⅃ⅆr;愊mƀ;el٫ⅎ⅐;檎;檐茀>;cdlqr׮ⅠⅪⅮⅳⅹĀciⅥⅧ;檧r;橺ot;拗Par;榕uest;橼ʀadelsↄⅪ←ٖ↛ǰ↉\0↎proø₞r;楸qĀlqؿ↖lesó₈ií٫Āen↣↭rtneqq;쀀≩︀Å↪ԀAabcefkosy⇄⇇⇱⇵⇺∘∝∯≨≽ròΠȀilmr⇐⇔⇗⇛rsðᒄf»․ilôکĀdr⇠⇤cy;䑊ƀ;cwࣴ⇫⇯ir;楈;憭ar;意irc;䄥ƀalr∁∎∓rtsĀ;u∉∊晥it»∊lip;怦con;抹r;쀀𝔥sĀew∣∩arow;椥arow;椦ʀamopr∺∾≃≞≣rr;懿tht;戻kĀlr≉≓eftarrow;憩ightarrow;憪f;쀀𝕙bar;怕ƀclt≯≴≸r;쀀𝒽asè⇴rok;䄧Ābp⊂⊇ull;恃hen»ᱛૡ⊣\0⊪\0⊸⋅⋎\0⋕⋳\0\0⋸⌢⍧⍢⍿\0⎆⎪⎴cute耻í䃭ƀ;iyݱ⊰⊵rc耻î䃮;䐸Ācx⊼⊿y;䐵cl耻¡䂡ĀfrΟ⋉;쀀𝔦rave耻ì䃬Ȁ;inoܾ⋝⋩⋮Āin⋢⋦nt;樌t;戭fin;槜ta;愩lig;䄳ƀaop⋾⌚⌝ƀcgt⌅⌈⌗r;䄫ƀelpܟ⌏⌓inåގarôܠh;䄱f;抷ed;䆵ʀ;cfotӴ⌬⌱⌽⍁are;愅inĀ;t⌸⌹戞ie;槝doô⌙ʀ;celpݗ⍌⍐⍛⍡al;抺Āgr⍕⍙eróᕣã⍍arhk;樗rod;樼Ȁcgpt⍯⍲⍶⍻y;䑑on;䄯f;쀀𝕚a;䎹uest耻¿䂿Āci⎊⎏r;쀀𝒾nʀ;EdsvӴ⎛⎝⎡ӳ;拹ot;拵Ā;v⎦⎧拴;拳Ā;iݷ⎮lde;䄩ǫ⎸\0⎼cy;䑖l耻ï䃯̀cfmosu⏌⏗⏜⏡⏧⏵Āiy⏑⏕rc;䄵;䐹r;쀀𝔧ath;䈷pf;쀀𝕛ǣ⏬\0⏱r;쀀𝒿rcy;䑘kcy;䑔Ѐacfghjos␋␖␢␧␭␱␵␻ppaĀ;v␓␔䎺;䏰Āey␛␠dil;䄷;䐺r;쀀𝔨reen;䄸cy;䑅cy;䑜pf;쀀𝕜cr;쀀𝓀஀ABEHabcdefghjlmnoprstuv⑰⒁⒆⒍⒑┎┽╚▀♎♞♥♹♽⚚⚲⛘❝❨➋⟀⠁⠒ƀart⑷⑺⑼rò৆òΕail;椛arr;椎Ā;gঔ⒋;檋ar;楢ॣ⒥\0⒪\0⒱\0\0\0\0\0⒵Ⓔ\0ⓆⓈⓍ\0⓹ute;䄺mptyv;榴raîࡌbda;䎻gƀ;dlࢎⓁⓃ;榑åࢎ;檅uo耻«䂫rЀ;bfhlpst࢙ⓞⓦⓩ⓫⓮⓱⓵Ā;f࢝ⓣs;椟s;椝ë≒p;憫l;椹im;楳l;憢ƀ;ae⓿─┄檫il;椙Ā;s┉┊檭;쀀⪭︀ƀabr┕┙┝rr;椌rk;杲Āak┢┬cĀek┨┪;䁻;䁛Āes┱┳;榋lĀdu┹┻;榏;榍Ȁaeuy╆╋╖╘ron;䄾Ādi═╔il;䄼ìࢰâ┩;䐻Ȁcqrs╣╦╭╽a;椶uoĀ;rนᝆĀdu╲╷har;楧shar;楋h;憲ʀ;fgqs▋▌উ◳◿扤tʀahlrt▘▤▷◂◨rrowĀ;t࢙□aé⓶arpoonĀdu▯▴own»њp»०eftarrows;懇ightƀahs◍◖◞rrowĀ;sࣴࢧarpoonó྘quigarro÷⇰hreetimes;拋ƀ;qs▋ও◺lanôবʀ;cdgsব☊☍☝☨c;檨otĀ;o☔☕橿Ā;r☚☛檁;檃Ā;e☢☥쀀⋚︀s;檓ʀadegs☳☹☽♉♋pproøⓆot;拖qĀgq♃♅ôউgtò⒌ôছiíলƀilr♕࣡♚sht;楼;쀀𝔩Ā;Eজ♣;檑š♩♶rĀdu▲♮Ā;l॥♳;楪lk;斄cy;䑙ʀ;achtੈ⚈⚋⚑⚖rò◁orneòᴈard;楫ri;旺Āio⚟⚤dot;䅀ustĀ;a⚬⚭掰che»⚭ȀEaes⚻⚽⛉⛔;扨pĀ;p⛃⛄檉rox»⛄Ā;q⛎⛏檇Ā;q⛎⚻im;拦Ѐabnoptwz⛩⛴⛷✚✯❁❇❐Ānr⛮⛱g;柬r;懽rëࣁgƀlmr⛿✍✔eftĀar০✇ightá৲apsto;柼ightá৽parrowĀlr✥✩efô⓭ight;憬ƀafl✶✹✽r;榅;쀀𝕝us;樭imes;樴š❋❏st;戗áፎƀ;ef❗❘᠀旊nge»❘arĀ;l❤❥䀨t;榓ʀachmt❳❶❼➅➇ròࢨorneòᶌarĀ;d྘➃;業;怎ri;抿̀achiqt➘➝ੀ➢➮➻quo;怹r;쀀𝓁mƀ;egল➪➬;檍;檏Ābu┪➳oĀ;rฟ➹;怚rok;䅂萀<;cdhilqrࠫ⟒☹⟜⟠⟥⟪⟰Āci⟗⟙;檦r;橹reå◲mes;拉arr;楶uest;橻ĀPi⟵⟹ar;榖ƀ;ef⠀भ᠛旃rĀdu⠇⠍shar;楊har;楦Āen⠗⠡rtneqq;쀀≨︀Å⠞܀Dacdefhilnopsu⡀⡅⢂⢎⢓⢠⢥⢨⣚⣢⣤ઃ⣳⤂Dot;戺Ȁclpr⡎⡒⡣⡽r耻¯䂯Āet⡗⡙;時Ā;e⡞⡟朠se»⡟Ā;sျ⡨toȀ;dluျ⡳⡷⡻owîҌefôएðᏑker;斮Āoy⢇⢌mma;権;䐼ash;怔asuredangle»ᘦr;쀀𝔪o;愧ƀcdn⢯⢴⣉ro耻µ䂵Ȁ;acdᑤ⢽⣀⣄sôᚧir;櫰ot肻·Ƶusƀ;bd⣒ᤃ⣓戒Ā;uᴼ⣘;横ţ⣞⣡p;櫛ò−ðઁĀdp⣩⣮els;抧f;쀀𝕞Āct⣸⣽r;쀀𝓂pos»ᖝƀ;lm⤉⤊⤍䎼timap;抸ఀGLRVabcdefghijlmoprstuvw⥂⥓⥾⦉⦘⧚⧩⨕⨚⩘⩝⪃⪕⪤⪨⬄⬇⭄⭿⮮ⰴⱧⱼ⳩Āgt⥇⥋;쀀⋙̸Ā;v⥐௏쀀≫⃒ƀelt⥚⥲⥶ftĀar⥡⥧rrow;懍ightarrow;懎;쀀⋘̸Ā;v⥻ే쀀≪⃒ightarrow;懏ĀDd⦎⦓ash;抯ash;抮ʀbcnpt⦣⦧⦬⦱⧌la»˞ute;䅄g;쀀∠⃒ʀ;Eiop඄⦼⧀⧅⧈;쀀⩰̸d;쀀≋̸s;䅉roø඄urĀ;a⧓⧔普lĀ;s⧓ସǳ⧟\0⧣p肻 ଷmpĀ;e௹ఀʀaeouy⧴⧾⨃⨐⨓ǰ⧹\0⧻;橃on;䅈dil;䅆ngĀ;dൾ⨊ot;쀀⩭̸p;橂;䐽ash;怓΀;Aadqsxஒ⨩⨭⨻⩁⩅⩐rr;懗rĀhr⨳⨶k;椤Ā;oᏲᏰot;쀀≐̸uiöୣĀei⩊⩎ar;椨í஘istĀ;s஠டr;쀀𝔫ȀEest௅⩦⩹⩼ƀ;qs஼⩭௡ƀ;qs஼௅⩴lanô௢ií௪Ā;rஶ⪁»ஷƀAap⪊⪍⪑rò⥱rr;憮ar;櫲ƀ;svྍ⪜ྌĀ;d⪡⪢拼;拺cy;䑚΀AEadest⪷⪺⪾⫂⫅⫶⫹rò⥦;쀀≦̸rr;憚r;急Ȁ;fqs఻⫎⫣⫯tĀar⫔⫙rro÷⫁ightarro÷⪐ƀ;qs఻⪺⫪lanôౕĀ;sౕ⫴»శiíౝĀ;rవ⫾iĀ;eచథiäඐĀpt⬌⬑f;쀀𝕟膀¬;in⬙⬚⬶䂬nȀ;Edvஉ⬤⬨⬮;쀀⋹̸ot;쀀⋵̸ǡஉ⬳⬵;拷;拶iĀ;vಸ⬼ǡಸ⭁⭃;拾;拽ƀaor⭋⭣⭩rȀ;ast୻⭕⭚⭟lleì୻l;쀀⫽⃥;쀀∂̸lint;樔ƀ;ceಒ⭰⭳uåಥĀ;cಘ⭸Ā;eಒ⭽ñಘȀAait⮈⮋⮝⮧rò⦈rrƀ;cw⮔⮕⮙憛;쀀⤳̸;쀀↝̸ghtarrow»⮕riĀ;eೋೖ΀chimpqu⮽⯍⯙⬄୸⯤⯯Ȁ;cerല⯆ഷ⯉uå൅;쀀𝓃ortɭ⬅\0\0⯖ará⭖mĀ;e൮⯟Ā;q൴൳suĀbp⯫⯭å೸åഋƀbcp⯶ⰑⰙȀ;Ees⯿ⰀഢⰄ抄;쀀⫅̸etĀ;eഛⰋqĀ;qണⰀcĀ;eലⰗñസȀ;EesⰢⰣൟⰧ抅;쀀⫆̸etĀ;e൘ⰮqĀ;qൠⰣȀgilrⰽⰿⱅⱇìௗlde耻ñ䃱çృiangleĀlrⱒⱜeftĀ;eచⱚñదightĀ;eೋⱥñ೗Ā;mⱬⱭ䎽ƀ;esⱴⱵⱹ䀣ro;愖p;怇ҀDHadgilrsⲏⲔⲙⲞⲣⲰⲶⳓⳣash;抭arr;椄p;쀀≍⃒ash;抬ĀetⲨⲬ;쀀≥⃒;쀀>⃒nfin;槞ƀAetⲽⳁⳅrr;椂;쀀≤⃒Ā;rⳊⳍ쀀<⃒ie;쀀⊴⃒ĀAtⳘⳜrr;椃rie;쀀⊵⃒im;쀀∼⃒ƀAan⳰⳴ⴂrr;懖rĀhr⳺⳽k;椣Ā;oᏧᏥear;椧ቓ᪕\0\0\0\0\0\0\0\0\0\0\0\0\0ⴭ\0ⴸⵈⵠⵥ⵲ⶄᬇ\0\0ⶍⶫ\0ⷈⷎ\0ⷜ⸙⸫⸾⹃Ācsⴱ᪗ute耻ó䃳ĀiyⴼⵅrĀ;c᪞ⵂ耻ô䃴;䐾ʀabios᪠ⵒⵗǈⵚlac;䅑v;樸old;榼lig;䅓Ācr⵩⵭ir;榿;쀀𝔬ͯ⵹\0\0⵼\0ⶂn;䋛ave耻ò䃲;槁Ābmⶈ෴ar;榵Ȁacitⶕ⶘ⶥⶨrò᪀Āir⶝ⶠr;榾oss;榻nå๒;槀ƀaeiⶱⶵⶹcr;䅍ga;䏉ƀcdnⷀⷅǍron;䎿;榶pf;쀀𝕠ƀaelⷔ⷗ǒr;榷rp;榹΀;adiosvⷪⷫⷮ⸈⸍⸐⸖戨rò᪆Ȁ;efmⷷⷸ⸂⸅橝rĀ;oⷾⷿ愴f»ⷿ耻ª䂪耻º䂺gof;抶r;橖lope;橗;橛ƀclo⸟⸡⸧ò⸁ash耻ø䃸l;折iŬⸯ⸴de耻õ䃵esĀ;aǛ⸺s;樶ml耻ö䃶bar;挽ૡ⹞\0⹽\0⺀⺝\0⺢⺹\0\0⻋ຜ\0⼓\0\0⼫⾼\0⿈rȀ;astЃ⹧⹲຅脀¶;l⹭⹮䂶leìЃɩ⹸\0\0⹻m;櫳;櫽y;䐿rʀcimpt⺋⺏⺓ᡥ⺗nt;䀥od;䀮il;怰enk;怱r;쀀𝔭ƀimo⺨⺰⺴Ā;v⺭⺮䏆;䏕maô੶ne;明ƀ;tv⺿⻀⻈䏀chfork»´;䏖Āau⻏⻟nĀck⻕⻝kĀ;h⇴⻛;愎ö⇴sҀ;abcdemst⻳⻴ᤈ⻹⻽⼄⼆⼊⼎䀫cir;樣ir;樢Āouᵀ⼂;樥;橲n肻±ຝim;樦wo;樧ƀipu⼙⼠⼥ntint;樕f;쀀𝕡nd耻£䂣Ԁ;Eaceinosu່⼿⽁⽄⽇⾁⾉⾒⽾⾶;檳p;檷uå໙Ā;c໎⽌̀;acens່⽙⽟⽦⽨⽾pproø⽃urlyeñ໙ñ໎ƀaes⽯⽶⽺pprox;檹qq;檵im;拨iíໟmeĀ;s⾈ຮ怲ƀEas⽸⾐⽺ð⽵ƀdfp໬⾙⾯ƀals⾠⾥⾪lar;挮ine;挒urf;挓Ā;t໻⾴ï໻rel;抰Āci⿀⿅r;쀀𝓅;䏈ncsp;怈̀fiopsu⿚⋢⿟⿥⿫⿱r;쀀𝔮pf;쀀𝕢rime;恗cr;쀀𝓆ƀaeo⿸〉〓tĀei⿾々rnionóڰnt;樖stĀ;e【】䀿ñἙô༔઀ABHabcdefhilmnoprstux぀けさすムㄎㄫㅇㅢㅲㆎ㈆㈕㈤㈩㉘㉮㉲㊐㊰㊷ƀartぇおがròႳòϝail;検aròᱥar;楤΀cdenqrtとふへみわゔヌĀeuねぱ;쀀∽̱te;䅕iãᅮmptyv;榳gȀ;del࿑らるろ;榒;榥å࿑uo耻»䂻rր;abcfhlpstw࿜ガクシスゼゾダッデナp;極Ā;f࿠ゴs;椠;椳s;椞ë≝ð✮l;楅im;楴l;憣;憝Āaiパフil;椚oĀ;nホボ戶aló༞ƀabrョリヮrò៥rk;杳ĀakンヽcĀekヹ・;䁽;䁝Āes㄂㄄;榌lĀduㄊㄌ;榎;榐Ȁaeuyㄗㄜㄧㄩron;䅙Ādiㄡㄥil;䅗ì࿲âヺ;䑀Ȁclqsㄴㄷㄽㅄa;椷dhar;楩uoĀ;rȎȍh;憳ƀacgㅎㅟངlȀ;ipsླྀㅘㅛႜnåႻarôྩt;断ƀilrㅩဣㅮsht;楽;쀀𝔯ĀaoㅷㆆrĀduㅽㅿ»ѻĀ;l႑ㆄ;楬Ā;vㆋㆌ䏁;䏱ƀgns㆕ㇹㇼht̀ahlrstㆤㆰ㇂㇘㇤㇮rrowĀ;t࿜ㆭaéトarpoonĀduㆻㆿowîㅾp»႒eftĀah㇊㇐rrowó࿪arpoonóՑightarrows;應quigarro÷ニhreetimes;拌g;䋚ingdotseñἲƀahm㈍㈐㈓rò࿪aòՑ;怏oustĀ;a㈞㈟掱che»㈟mid;櫮Ȁabpt㈲㈽㉀㉒Ānr㈷㈺g;柭r;懾rëဃƀafl㉇㉊㉎r;榆;쀀𝕣us;樮imes;樵Āap㉝㉧rĀ;g㉣㉤䀩t;榔olint;樒arò㇣Ȁachq㉻㊀Ⴜ㊅quo;怺r;쀀𝓇Ābu・㊊oĀ;rȔȓƀhir㊗㊛㊠reåㇸmes;拊iȀ;efl㊪ၙᠡ㊫方tri;槎luhar;楨;愞ൡ㋕㋛㋟㌬㌸㍱\0㍺㎤\0\0㏬㏰\0㐨㑈㑚㒭㒱㓊㓱\0㘖\0\0㘳cute;䅛quï➺Ԁ;Eaceinpsyᇭ㋳㋵㋿㌂㌋㌏㌟㌦㌩;檴ǰ㋺\0㋼;檸on;䅡uåᇾĀ;dᇳ㌇il;䅟rc;䅝ƀEas㌖㌘㌛;檶p;檺im;择olint;樓iíሄ;䑁otƀ;be㌴ᵇ㌵担;橦΀Aacmstx㍆㍊㍗㍛㍞㍣㍭rr;懘rĀhr㍐㍒ë∨Ā;oਸ਼਴t耻§䂧i;䀻war;椩mĀin㍩ðnuóñt;朶rĀ;o㍶⁕쀀𝔰Ȁacoy㎂㎆㎑㎠rp;景Āhy㎋㎏cy;䑉;䑈rtɭ㎙\0\0㎜iäᑤaraì⹯耻­䂭Āgm㎨㎴maƀ;fv㎱㎲㎲䏃;䏂Ѐ;deglnprካ㏅㏉㏎㏖㏞㏡㏦ot;橪Ā;q኱ኰĀ;E㏓㏔檞;檠Ā;E㏛㏜檝;檟e;扆lus;樤arr;楲aròᄽȀaeit㏸㐈㐏㐗Āls㏽㐄lsetmé㍪hp;樳parsl;槤Ādlᑣ㐔e;挣Ā;e㐜㐝檪Ā;s㐢㐣檬;쀀⪬︀ƀflp㐮㐳㑂tcy;䑌Ā;b㐸㐹䀯Ā;a㐾㐿槄r;挿f;쀀𝕤aĀdr㑍ЂesĀ;u㑔㑕晠it»㑕ƀcsu㑠㑹㒟Āau㑥㑯pĀ;sᆈ㑫;쀀⊓︀pĀ;sᆴ㑵;쀀⊔︀uĀbp㑿㒏ƀ;esᆗᆜ㒆etĀ;eᆗ㒍ñᆝƀ;esᆨᆭ㒖etĀ;eᆨ㒝ñᆮƀ;afᅻ㒦ְrť㒫ֱ»ᅼaròᅈȀcemt㒹㒾㓂㓅r;쀀𝓈tmîñiì㐕aræᆾĀar㓎㓕rĀ;f㓔ឿ昆Āan㓚㓭ightĀep㓣㓪psiloîỠhé⺯s»⡒ʀbcmnp㓻㕞ሉ㖋㖎Ҁ;Edemnprs㔎㔏㔑㔕㔞㔣㔬㔱㔶抂;櫅ot;檽Ā;dᇚ㔚ot;櫃ult;櫁ĀEe㔨㔪;櫋;把lus;檿arr;楹ƀeiu㔽㕒㕕tƀ;en㔎㕅㕋qĀ;qᇚ㔏eqĀ;q㔫㔨m;櫇Ābp㕚㕜;櫕;櫓c̀;acensᇭ㕬㕲㕹㕻㌦pproø㋺urlyeñᇾñᇳƀaes㖂㖈㌛pproø㌚qñ㌗g;晪ڀ123;Edehlmnps㖩㖬㖯ሜ㖲㖴㗀㗉㗕㗚㗟㗨㗭耻¹䂹耻²䂲耻³䂳;櫆Āos㖹㖼t;檾ub;櫘Ā;dሢ㗅ot;櫄sĀou㗏㗒l;柉b;櫗arr;楻ult;櫂ĀEe㗤㗦;櫌;抋lus;櫀ƀeiu㗴㘉㘌tƀ;enሜ㗼㘂qĀ;qሢ㖲eqĀ;q㗧㗤m;櫈Ābp㘑㘓;櫔;櫖ƀAan㘜㘠㘭rr;懙rĀhr㘦㘨ë∮Ā;oਫ਩war;椪lig耻ß䃟௡㙑㙝㙠ዎ㙳㙹\0㙾㛂\0\0\0\0\0㛛㜃\0㜉㝬\0\0\0㞇ɲ㙖\0\0㙛get;挖;䏄rë๟ƀaey㙦㙫㙰ron;䅥dil;䅣;䑂lrec;挕r;쀀𝔱Ȁeiko㚆㚝㚵㚼ǲ㚋\0㚑eĀ4fኄኁaƀ;sv㚘㚙㚛䎸ym;䏑Ācn㚢㚲kĀas㚨㚮pproø዁im»ኬsðኞĀas㚺㚮ð዁rn耻þ䃾Ǭ̟㛆⋧es膀×;bd㛏㛐㛘䃗Ā;aᤏ㛕r;樱;樰ƀeps㛡㛣㜀á⩍Ȁ;bcf҆㛬㛰㛴ot;挶ir;櫱Ā;o㛹㛼쀀𝕥rk;櫚á㍢rime;怴ƀaip㜏㜒㝤dåቈ΀adempst㜡㝍㝀㝑㝗㝜㝟ngleʀ;dlqr㜰㜱㜶㝀㝂斵own»ᶻeftĀ;e⠀㜾ñम;扜ightĀ;e㊪㝋ñၚot;旬inus;樺lus;樹b;槍ime;樻ezium;揢ƀcht㝲㝽㞁Āry㝷㝻;쀀𝓉;䑆cy;䑛rok;䅧Āio㞋㞎xô᝷headĀlr㞗㞠eftarro÷ࡏightarrow»ཝऀAHabcdfghlmoprstuw㟐㟓㟗㟤㟰㟼㠎㠜㠣㠴㡑㡝㡫㢩㣌㣒㣪㣶ròϭar;楣Ācr㟜㟢ute耻ú䃺òᅐrǣ㟪\0㟭y;䑞ve;䅭Āiy㟵㟺rc耻û䃻;䑃ƀabh㠃㠆㠋ròᎭlac;䅱aòᏃĀir㠓㠘sht;楾;쀀𝔲rave耻ù䃹š㠧㠱rĀlr㠬㠮»ॗ»ႃlk;斀Āct㠹㡍ɯ㠿\0\0㡊rnĀ;e㡅㡆挜r»㡆op;挏ri;旸Āal㡖㡚cr;䅫肻¨͉Āgp㡢㡦on;䅳f;쀀𝕦̀adhlsuᅋ㡸㡽፲㢑㢠ownáᎳarpoonĀlr㢈㢌efô㠭ighô㠯iƀ;hl㢙㢚㢜䏅»ᏺon»㢚parrows;懈ƀcit㢰㣄㣈ɯ㢶\0\0㣁rnĀ;e㢼㢽挝r»㢽op;挎ng;䅯ri;旹cr;쀀𝓊ƀdir㣙㣝㣢ot;拰lde;䅩iĀ;f㜰㣨»᠓Āam㣯㣲rò㢨l耻ü䃼angle;榧ހABDacdeflnoprsz㤜㤟㤩㤭㦵㦸㦽㧟㧤㧨㧳㧹㧽㨁㨠ròϷarĀ;v㤦㤧櫨;櫩asèϡĀnr㤲㤷grt;榜΀eknprst㓣㥆㥋㥒㥝㥤㦖appá␕othinçẖƀhir㓫⻈㥙opô⾵Ā;hᎷ㥢ïㆍĀiu㥩㥭gmá㎳Ābp㥲㦄setneqĀ;q㥽㦀쀀⊊︀;쀀⫋︀setneqĀ;q㦏㦒쀀⊋︀;쀀⫌︀Āhr㦛㦟etá㚜iangleĀlr㦪㦯eft»थight»ၑy;䐲ash»ံƀelr㧄㧒㧗ƀ;beⷪ㧋㧏ar;抻q;扚lip;拮Ābt㧜ᑨaòᑩr;쀀𝔳tré㦮suĀbp㧯㧱»ജ»൙pf;쀀𝕧roð໻tré㦴Ācu㨆㨋r;쀀𝓋Ābp㨐㨘nĀEe㦀㨖»㥾nĀEe㦒㨞»㦐igzag;榚΀cefoprs㨶㨻㩖㩛㩔㩡㩪irc;䅵Ādi㩀㩑Ābg㩅㩉ar;機eĀ;qᗺ㩏;扙erp;愘r;쀀𝔴pf;쀀𝕨Ā;eᑹ㩦atèᑹcr;쀀𝓌ૣណ㪇\0㪋\0㪐㪛\0\0㪝㪨㪫㪯\0\0㫃㫎\0㫘ៜ៟tré៑r;쀀𝔵ĀAa㪔㪗ròσrò৶;䎾ĀAa㪡㪤ròθrò৫að✓is;拻ƀdptឤ㪵㪾Āfl㪺ឩ;쀀𝕩imåឲĀAa㫇㫊ròώròਁĀcq㫒ីr;쀀𝓍Āpt៖㫜ré។Ѐacefiosu㫰㫽㬈㬌㬑㬕㬛㬡cĀuy㫶㫻te耻ý䃽;䑏Āiy㬂㬆rc;䅷;䑋n耻¥䂥r;쀀𝔶cy;䑗pf;쀀𝕪cr;쀀𝓎Ācm㬦㬩y;䑎l耻ÿ䃿Ԁacdefhiosw㭂㭈㭔㭘㭤㭩㭭㭴㭺㮀cute;䅺Āay㭍㭒ron;䅾;䐷ot;䅼Āet㭝㭡træᕟa;䎶r;쀀𝔷cy;䐶grarr;懝pf;쀀𝕫cr;쀀𝓏Ājn㮅㮇;怍j;怌'.split("").map(function(c2) {
      return c2.charCodeAt(0);
    })
  );
  return decodeDataHtml;
}
var decodeDataXml = {};
var hasRequiredDecodeDataXml;
function requireDecodeDataXml() {
  if (hasRequiredDecodeDataXml) return decodeDataXml;
  hasRequiredDecodeDataXml = 1;
  Object.defineProperty(decodeDataXml, "__esModule", { value: true });
  decodeDataXml.default = new Uint16Array(
    // prettier-ignore
    "Ȁaglq	\x1Bɭ\0\0p;䀦os;䀧t;䀾t;䀼uot;䀢".split("").map(function(c2) {
      return c2.charCodeAt(0);
    })
  );
  return decodeDataXml;
}
var decode_codepoint = {};
var hasRequiredDecode_codepoint;
function requireDecode_codepoint() {
  if (hasRequiredDecode_codepoint) return decode_codepoint;
  hasRequiredDecode_codepoint = 1;
  (function(exports) {
    var _a;
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.replaceCodePoint = exports.fromCodePoint = void 0;
    var decodeMap = /* @__PURE__ */ new Map([
      [0, 65533],
      // C1 Unicode control character reference replacements
      [128, 8364],
      [130, 8218],
      [131, 402],
      [132, 8222],
      [133, 8230],
      [134, 8224],
      [135, 8225],
      [136, 710],
      [137, 8240],
      [138, 352],
      [139, 8249],
      [140, 338],
      [142, 381],
      [145, 8216],
      [146, 8217],
      [147, 8220],
      [148, 8221],
      [149, 8226],
      [150, 8211],
      [151, 8212],
      [152, 732],
      [153, 8482],
      [154, 353],
      [155, 8250],
      [156, 339],
      [158, 382],
      [159, 376]
    ]);
    exports.fromCodePoint = // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition, node/no-unsupported-features/es-builtins
    (_a = String.fromCodePoint) !== null && _a !== void 0 ? _a : function(codePoint) {
      var output = "";
      if (codePoint > 65535) {
        codePoint -= 65536;
        output += String.fromCharCode(codePoint >>> 10 & 1023 | 55296);
        codePoint = 56320 | codePoint & 1023;
      }
      output += String.fromCharCode(codePoint);
      return output;
    };
    function replaceCodePoint(codePoint) {
      var _a2;
      if (codePoint >= 55296 && codePoint <= 57343 || codePoint > 1114111) {
        return 65533;
      }
      return (_a2 = decodeMap.get(codePoint)) !== null && _a2 !== void 0 ? _a2 : codePoint;
    }
    exports.replaceCodePoint = replaceCodePoint;
    function decodeCodePoint(codePoint) {
      return (0, exports.fromCodePoint)(replaceCodePoint(codePoint));
    }
    exports.default = decodeCodePoint;
  })(decode_codepoint);
  return decode_codepoint;
}
var hasRequiredDecode;
function requireDecode() {
  if (hasRequiredDecode) return decode$1;
  hasRequiredDecode = 1;
  (function(exports) {
    var __createBinding = decode$1 && decode$1.__createBinding || (Object.create ? (function(o2, m2, k2, k22) {
      if (k22 === void 0) k22 = k2;
      var desc = Object.getOwnPropertyDescriptor(m2, k2);
      if (!desc || ("get" in desc ? !m2.__esModule : desc.writable || desc.configurable)) {
        desc = { enumerable: true, get: function() {
          return m2[k2];
        } };
      }
      Object.defineProperty(o2, k22, desc);
    }) : (function(o2, m2, k2, k22) {
      if (k22 === void 0) k22 = k2;
      o2[k22] = m2[k2];
    }));
    var __setModuleDefault = decode$1 && decode$1.__setModuleDefault || (Object.create ? (function(o2, v2) {
      Object.defineProperty(o2, "default", { enumerable: true, value: v2 });
    }) : function(o2, v2) {
      o2["default"] = v2;
    });
    var __importStar = decode$1 && decode$1.__importStar || function(mod) {
      if (mod && mod.__esModule) return mod;
      var result = {};
      if (mod != null) {
        for (var k2 in mod) if (k2 !== "default" && Object.prototype.hasOwnProperty.call(mod, k2)) __createBinding(result, mod, k2);
      }
      __setModuleDefault(result, mod);
      return result;
    };
    var __importDefault = decode$1 && decode$1.__importDefault || function(mod) {
      return mod && mod.__esModule ? mod : { "default": mod };
    };
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.decodeXML = exports.decodeHTMLStrict = exports.decodeHTMLAttribute = exports.decodeHTML = exports.determineBranch = exports.EntityDecoder = exports.DecodingMode = exports.BinTrieFlags = exports.fromCodePoint = exports.replaceCodePoint = exports.decodeCodePoint = exports.xmlDecodeTree = exports.htmlDecodeTree = void 0;
    var decode_data_html_js_1 = __importDefault(/* @__PURE__ */ requireDecodeDataHtml());
    exports.htmlDecodeTree = decode_data_html_js_1.default;
    var decode_data_xml_js_1 = __importDefault(/* @__PURE__ */ requireDecodeDataXml());
    exports.xmlDecodeTree = decode_data_xml_js_1.default;
    var decode_codepoint_js_1 = __importStar(/* @__PURE__ */ requireDecode_codepoint());
    exports.decodeCodePoint = decode_codepoint_js_1.default;
    var decode_codepoint_js_2 = /* @__PURE__ */ requireDecode_codepoint();
    Object.defineProperty(exports, "replaceCodePoint", { enumerable: true, get: function() {
      return decode_codepoint_js_2.replaceCodePoint;
    } });
    Object.defineProperty(exports, "fromCodePoint", { enumerable: true, get: function() {
      return decode_codepoint_js_2.fromCodePoint;
    } });
    var CharCodes;
    (function(CharCodes2) {
      CharCodes2[CharCodes2["NUM"] = 35] = "NUM";
      CharCodes2[CharCodes2["SEMI"] = 59] = "SEMI";
      CharCodes2[CharCodes2["EQUALS"] = 61] = "EQUALS";
      CharCodes2[CharCodes2["ZERO"] = 48] = "ZERO";
      CharCodes2[CharCodes2["NINE"] = 57] = "NINE";
      CharCodes2[CharCodes2["LOWER_A"] = 97] = "LOWER_A";
      CharCodes2[CharCodes2["LOWER_F"] = 102] = "LOWER_F";
      CharCodes2[CharCodes2["LOWER_X"] = 120] = "LOWER_X";
      CharCodes2[CharCodes2["LOWER_Z"] = 122] = "LOWER_Z";
      CharCodes2[CharCodes2["UPPER_A"] = 65] = "UPPER_A";
      CharCodes2[CharCodes2["UPPER_F"] = 70] = "UPPER_F";
      CharCodes2[CharCodes2["UPPER_Z"] = 90] = "UPPER_Z";
    })(CharCodes || (CharCodes = {}));
    var TO_LOWER_BIT = 32;
    var BinTrieFlags;
    (function(BinTrieFlags2) {
      BinTrieFlags2[BinTrieFlags2["VALUE_LENGTH"] = 49152] = "VALUE_LENGTH";
      BinTrieFlags2[BinTrieFlags2["BRANCH_LENGTH"] = 16256] = "BRANCH_LENGTH";
      BinTrieFlags2[BinTrieFlags2["JUMP_TABLE"] = 127] = "JUMP_TABLE";
    })(BinTrieFlags = exports.BinTrieFlags || (exports.BinTrieFlags = {}));
    function isNumber(code2) {
      return code2 >= CharCodes.ZERO && code2 <= CharCodes.NINE;
    }
    function isHexadecimalCharacter(code2) {
      return code2 >= CharCodes.UPPER_A && code2 <= CharCodes.UPPER_F || code2 >= CharCodes.LOWER_A && code2 <= CharCodes.LOWER_F;
    }
    function isAsciiAlphaNumeric(code2) {
      return code2 >= CharCodes.UPPER_A && code2 <= CharCodes.UPPER_Z || code2 >= CharCodes.LOWER_A && code2 <= CharCodes.LOWER_Z || isNumber(code2);
    }
    function isEntityInAttributeInvalidEnd(code2) {
      return code2 === CharCodes.EQUALS || isAsciiAlphaNumeric(code2);
    }
    var EntityDecoderState;
    (function(EntityDecoderState2) {
      EntityDecoderState2[EntityDecoderState2["EntityStart"] = 0] = "EntityStart";
      EntityDecoderState2[EntityDecoderState2["NumericStart"] = 1] = "NumericStart";
      EntityDecoderState2[EntityDecoderState2["NumericDecimal"] = 2] = "NumericDecimal";
      EntityDecoderState2[EntityDecoderState2["NumericHex"] = 3] = "NumericHex";
      EntityDecoderState2[EntityDecoderState2["NamedEntity"] = 4] = "NamedEntity";
    })(EntityDecoderState || (EntityDecoderState = {}));
    var DecodingMode;
    (function(DecodingMode2) {
      DecodingMode2[DecodingMode2["Legacy"] = 0] = "Legacy";
      DecodingMode2[DecodingMode2["Strict"] = 1] = "Strict";
      DecodingMode2[DecodingMode2["Attribute"] = 2] = "Attribute";
    })(DecodingMode = exports.DecodingMode || (exports.DecodingMode = {}));
    var EntityDecoder = (
      /** @class */
      (function() {
        function EntityDecoder2(decodeTree, emitCodePoint, errors2) {
          this.decodeTree = decodeTree;
          this.emitCodePoint = emitCodePoint;
          this.errors = errors2;
          this.state = EntityDecoderState.EntityStart;
          this.consumed = 1;
          this.result = 0;
          this.treeIndex = 0;
          this.excess = 1;
          this.decodeMode = DecodingMode.Strict;
        }
        EntityDecoder2.prototype.startEntity = function(decodeMode) {
          this.decodeMode = decodeMode;
          this.state = EntityDecoderState.EntityStart;
          this.result = 0;
          this.treeIndex = 0;
          this.excess = 1;
          this.consumed = 1;
        };
        EntityDecoder2.prototype.write = function(str, offset) {
          switch (this.state) {
            case EntityDecoderState.EntityStart: {
              if (str.charCodeAt(offset) === CharCodes.NUM) {
                this.state = EntityDecoderState.NumericStart;
                this.consumed += 1;
                return this.stateNumericStart(str, offset + 1);
              }
              this.state = EntityDecoderState.NamedEntity;
              return this.stateNamedEntity(str, offset);
            }
            case EntityDecoderState.NumericStart: {
              return this.stateNumericStart(str, offset);
            }
            case EntityDecoderState.NumericDecimal: {
              return this.stateNumericDecimal(str, offset);
            }
            case EntityDecoderState.NumericHex: {
              return this.stateNumericHex(str, offset);
            }
            case EntityDecoderState.NamedEntity: {
              return this.stateNamedEntity(str, offset);
            }
          }
        };
        EntityDecoder2.prototype.stateNumericStart = function(str, offset) {
          if (offset >= str.length) {
            return -1;
          }
          if ((str.charCodeAt(offset) | TO_LOWER_BIT) === CharCodes.LOWER_X) {
            this.state = EntityDecoderState.NumericHex;
            this.consumed += 1;
            return this.stateNumericHex(str, offset + 1);
          }
          this.state = EntityDecoderState.NumericDecimal;
          return this.stateNumericDecimal(str, offset);
        };
        EntityDecoder2.prototype.addToNumericResult = function(str, start, end, base2) {
          if (start !== end) {
            var digitCount = end - start;
            this.result = this.result * Math.pow(base2, digitCount) + parseInt(str.substr(start, digitCount), base2);
            this.consumed += digitCount;
          }
        };
        EntityDecoder2.prototype.stateNumericHex = function(str, offset) {
          var startIdx = offset;
          while (offset < str.length) {
            var char = str.charCodeAt(offset);
            if (isNumber(char) || isHexadecimalCharacter(char)) {
              offset += 1;
            } else {
              this.addToNumericResult(str, startIdx, offset, 16);
              return this.emitNumericEntity(char, 3);
            }
          }
          this.addToNumericResult(str, startIdx, offset, 16);
          return -1;
        };
        EntityDecoder2.prototype.stateNumericDecimal = function(str, offset) {
          var startIdx = offset;
          while (offset < str.length) {
            var char = str.charCodeAt(offset);
            if (isNumber(char)) {
              offset += 1;
            } else {
              this.addToNumericResult(str, startIdx, offset, 10);
              return this.emitNumericEntity(char, 2);
            }
          }
          this.addToNumericResult(str, startIdx, offset, 10);
          return -1;
        };
        EntityDecoder2.prototype.emitNumericEntity = function(lastCp, expectedLength) {
          var _a;
          if (this.consumed <= expectedLength) {
            (_a = this.errors) === null || _a === void 0 ? void 0 : _a.absenceOfDigitsInNumericCharacterReference(this.consumed);
            return 0;
          }
          if (lastCp === CharCodes.SEMI) {
            this.consumed += 1;
          } else if (this.decodeMode === DecodingMode.Strict) {
            return 0;
          }
          this.emitCodePoint((0, decode_codepoint_js_1.replaceCodePoint)(this.result), this.consumed);
          if (this.errors) {
            if (lastCp !== CharCodes.SEMI) {
              this.errors.missingSemicolonAfterCharacterReference();
            }
            this.errors.validateNumericCharacterReference(this.result);
          }
          return this.consumed;
        };
        EntityDecoder2.prototype.stateNamedEntity = function(str, offset) {
          var decodeTree = this.decodeTree;
          var current = decodeTree[this.treeIndex];
          var valueLength = (current & BinTrieFlags.VALUE_LENGTH) >> 14;
          for (; offset < str.length; offset++, this.excess++) {
            var char = str.charCodeAt(offset);
            this.treeIndex = determineBranch(decodeTree, current, this.treeIndex + Math.max(1, valueLength), char);
            if (this.treeIndex < 0) {
              return this.result === 0 || // If we are parsing an attribute
              this.decodeMode === DecodingMode.Attribute && // We shouldn't have consumed any characters after the entity,
              (valueLength === 0 || // And there should be no invalid characters.
              isEntityInAttributeInvalidEnd(char)) ? 0 : this.emitNotTerminatedNamedEntity();
            }
            current = decodeTree[this.treeIndex];
            valueLength = (current & BinTrieFlags.VALUE_LENGTH) >> 14;
            if (valueLength !== 0) {
              if (char === CharCodes.SEMI) {
                return this.emitNamedEntityData(this.treeIndex, valueLength, this.consumed + this.excess);
              }
              if (this.decodeMode !== DecodingMode.Strict) {
                this.result = this.treeIndex;
                this.consumed += this.excess;
                this.excess = 0;
              }
            }
          }
          return -1;
        };
        EntityDecoder2.prototype.emitNotTerminatedNamedEntity = function() {
          var _a;
          var _b = this, result = _b.result, decodeTree = _b.decodeTree;
          var valueLength = (decodeTree[result] & BinTrieFlags.VALUE_LENGTH) >> 14;
          this.emitNamedEntityData(result, valueLength, this.consumed);
          (_a = this.errors) === null || _a === void 0 ? void 0 : _a.missingSemicolonAfterCharacterReference();
          return this.consumed;
        };
        EntityDecoder2.prototype.emitNamedEntityData = function(result, valueLength, consumed) {
          var decodeTree = this.decodeTree;
          this.emitCodePoint(valueLength === 1 ? decodeTree[result] & ~BinTrieFlags.VALUE_LENGTH : decodeTree[result + 1], consumed);
          if (valueLength === 3) {
            this.emitCodePoint(decodeTree[result + 2], consumed);
          }
          return consumed;
        };
        EntityDecoder2.prototype.end = function() {
          var _a;
          switch (this.state) {
            case EntityDecoderState.NamedEntity: {
              return this.result !== 0 && (this.decodeMode !== DecodingMode.Attribute || this.result === this.treeIndex) ? this.emitNotTerminatedNamedEntity() : 0;
            }
            // Otherwise, emit a numeric entity if we have one.
            case EntityDecoderState.NumericDecimal: {
              return this.emitNumericEntity(0, 2);
            }
            case EntityDecoderState.NumericHex: {
              return this.emitNumericEntity(0, 3);
            }
            case EntityDecoderState.NumericStart: {
              (_a = this.errors) === null || _a === void 0 ? void 0 : _a.absenceOfDigitsInNumericCharacterReference(this.consumed);
              return 0;
            }
            case EntityDecoderState.EntityStart: {
              return 0;
            }
          }
        };
        return EntityDecoder2;
      })()
    );
    exports.EntityDecoder = EntityDecoder;
    function getDecoder(decodeTree) {
      var ret = "";
      var decoder = new EntityDecoder(decodeTree, function(str) {
        return ret += (0, decode_codepoint_js_1.fromCodePoint)(str);
      });
      return function decodeWithTrie(str, decodeMode) {
        var lastIndex = 0;
        var offset = 0;
        while ((offset = str.indexOf("&", offset)) >= 0) {
          ret += str.slice(lastIndex, offset);
          decoder.startEntity(decodeMode);
          var len = decoder.write(
            str,
            // Skip the "&"
            offset + 1
          );
          if (len < 0) {
            lastIndex = offset + decoder.end();
            break;
          }
          lastIndex = offset + len;
          offset = len === 0 ? lastIndex + 1 : lastIndex;
        }
        var result = ret + str.slice(lastIndex);
        ret = "";
        return result;
      };
    }
    function determineBranch(decodeTree, current, nodeIdx, char) {
      var branchCount = (current & BinTrieFlags.BRANCH_LENGTH) >> 7;
      var jumpOffset = current & BinTrieFlags.JUMP_TABLE;
      if (branchCount === 0) {
        return jumpOffset !== 0 && char === jumpOffset ? nodeIdx : -1;
      }
      if (jumpOffset) {
        var value = char - jumpOffset;
        return value < 0 || value >= branchCount ? -1 : decodeTree[nodeIdx + value] - 1;
      }
      var lo = nodeIdx;
      var hi = lo + branchCount - 1;
      while (lo <= hi) {
        var mid = lo + hi >>> 1;
        var midVal = decodeTree[mid];
        if (midVal < char) {
          lo = mid + 1;
        } else if (midVal > char) {
          hi = mid - 1;
        } else {
          return decodeTree[mid + branchCount];
        }
      }
      return -1;
    }
    exports.determineBranch = determineBranch;
    var htmlDecoder = getDecoder(decode_data_html_js_1.default);
    var xmlDecoder = getDecoder(decode_data_xml_js_1.default);
    function decodeHTML(str, mode) {
      if (mode === void 0) {
        mode = DecodingMode.Legacy;
      }
      return htmlDecoder(str, mode);
    }
    exports.decodeHTML = decodeHTML;
    function decodeHTMLAttribute(str) {
      return htmlDecoder(str, DecodingMode.Attribute);
    }
    exports.decodeHTMLAttribute = decodeHTMLAttribute;
    function decodeHTMLStrict(str) {
      return htmlDecoder(str, DecodingMode.Strict);
    }
    exports.decodeHTMLStrict = decodeHTMLStrict;
    function decodeXML(str) {
      return xmlDecoder(str, DecodingMode.Strict);
    }
    exports.decodeXML = decodeXML;
  })(decode$1);
  return decode$1;
}
var encode$1 = {};
var encodeHtml = {};
var hasRequiredEncodeHtml;
function requireEncodeHtml() {
  if (hasRequiredEncodeHtml) return encodeHtml;
  hasRequiredEncodeHtml = 1;
  Object.defineProperty(encodeHtml, "__esModule", { value: true });
  function restoreDiff(arr) {
    for (var i2 = 1; i2 < arr.length; i2++) {
      arr[i2][0] += arr[i2 - 1][0] + 1;
    }
    return arr;
  }
  encodeHtml.default = new Map(/* @__PURE__ */ restoreDiff([[9, "&Tab;"], [0, "&NewLine;"], [22, "&excl;"], [0, "&quot;"], [0, "&num;"], [0, "&dollar;"], [0, "&percnt;"], [0, "&amp;"], [0, "&apos;"], [0, "&lpar;"], [0, "&rpar;"], [0, "&ast;"], [0, "&plus;"], [0, "&comma;"], [1, "&period;"], [0, "&sol;"], [10, "&colon;"], [0, "&semi;"], [0, { v: "&lt;", n: 8402, o: "&nvlt;" }], [0, { v: "&equals;", n: 8421, o: "&bne;" }], [0, { v: "&gt;", n: 8402, o: "&nvgt;" }], [0, "&quest;"], [0, "&commat;"], [26, "&lbrack;"], [0, "&bsol;"], [0, "&rbrack;"], [0, "&Hat;"], [0, "&lowbar;"], [0, "&DiacriticalGrave;"], [5, { n: 106, o: "&fjlig;" }], [20, "&lbrace;"], [0, "&verbar;"], [0, "&rbrace;"], [34, "&nbsp;"], [0, "&iexcl;"], [0, "&cent;"], [0, "&pound;"], [0, "&curren;"], [0, "&yen;"], [0, "&brvbar;"], [0, "&sect;"], [0, "&die;"], [0, "&copy;"], [0, "&ordf;"], [0, "&laquo;"], [0, "&not;"], [0, "&shy;"], [0, "&circledR;"], [0, "&macr;"], [0, "&deg;"], [0, "&PlusMinus;"], [0, "&sup2;"], [0, "&sup3;"], [0, "&acute;"], [0, "&micro;"], [0, "&para;"], [0, "&centerdot;"], [0, "&cedil;"], [0, "&sup1;"], [0, "&ordm;"], [0, "&raquo;"], [0, "&frac14;"], [0, "&frac12;"], [0, "&frac34;"], [0, "&iquest;"], [0, "&Agrave;"], [0, "&Aacute;"], [0, "&Acirc;"], [0, "&Atilde;"], [0, "&Auml;"], [0, "&angst;"], [0, "&AElig;"], [0, "&Ccedil;"], [0, "&Egrave;"], [0, "&Eacute;"], [0, "&Ecirc;"], [0, "&Euml;"], [0, "&Igrave;"], [0, "&Iacute;"], [0, "&Icirc;"], [0, "&Iuml;"], [0, "&ETH;"], [0, "&Ntilde;"], [0, "&Ograve;"], [0, "&Oacute;"], [0, "&Ocirc;"], [0, "&Otilde;"], [0, "&Ouml;"], [0, "&times;"], [0, "&Oslash;"], [0, "&Ugrave;"], [0, "&Uacute;"], [0, "&Ucirc;"], [0, "&Uuml;"], [0, "&Yacute;"], [0, "&THORN;"], [0, "&szlig;"], [0, "&agrave;"], [0, "&aacute;"], [0, "&acirc;"], [0, "&atilde;"], [0, "&auml;"], [0, "&aring;"], [0, "&aelig;"], [0, "&ccedil;"], [0, "&egrave;"], [0, "&eacute;"], [0, "&ecirc;"], [0, "&euml;"], [0, "&igrave;"], [0, "&iacute;"], [0, "&icirc;"], [0, "&iuml;"], [0, "&eth;"], [0, "&ntilde;"], [0, "&ograve;"], [0, "&oacute;"], [0, "&ocirc;"], [0, "&otilde;"], [0, "&ouml;"], [0, "&div;"], [0, "&oslash;"], [0, "&ugrave;"], [0, "&uacute;"], [0, "&ucirc;"], [0, "&uuml;"], [0, "&yacute;"], [0, "&thorn;"], [0, "&yuml;"], [0, "&Amacr;"], [0, "&amacr;"], [0, "&Abreve;"], [0, "&abreve;"], [0, "&Aogon;"], [0, "&aogon;"], [0, "&Cacute;"], [0, "&cacute;"], [0, "&Ccirc;"], [0, "&ccirc;"], [0, "&Cdot;"], [0, "&cdot;"], [0, "&Ccaron;"], [0, "&ccaron;"], [0, "&Dcaron;"], [0, "&dcaron;"], [0, "&Dstrok;"], [0, "&dstrok;"], [0, "&Emacr;"], [0, "&emacr;"], [2, "&Edot;"], [0, "&edot;"], [0, "&Eogon;"], [0, "&eogon;"], [0, "&Ecaron;"], [0, "&ecaron;"], [0, "&Gcirc;"], [0, "&gcirc;"], [0, "&Gbreve;"], [0, "&gbreve;"], [0, "&Gdot;"], [0, "&gdot;"], [0, "&Gcedil;"], [1, "&Hcirc;"], [0, "&hcirc;"], [0, "&Hstrok;"], [0, "&hstrok;"], [0, "&Itilde;"], [0, "&itilde;"], [0, "&Imacr;"], [0, "&imacr;"], [2, "&Iogon;"], [0, "&iogon;"], [0, "&Idot;"], [0, "&imath;"], [0, "&IJlig;"], [0, "&ijlig;"], [0, "&Jcirc;"], [0, "&jcirc;"], [0, "&Kcedil;"], [0, "&kcedil;"], [0, "&kgreen;"], [0, "&Lacute;"], [0, "&lacute;"], [0, "&Lcedil;"], [0, "&lcedil;"], [0, "&Lcaron;"], [0, "&lcaron;"], [0, "&Lmidot;"], [0, "&lmidot;"], [0, "&Lstrok;"], [0, "&lstrok;"], [0, "&Nacute;"], [0, "&nacute;"], [0, "&Ncedil;"], [0, "&ncedil;"], [0, "&Ncaron;"], [0, "&ncaron;"], [0, "&napos;"], [0, "&ENG;"], [0, "&eng;"], [0, "&Omacr;"], [0, "&omacr;"], [2, "&Odblac;"], [0, "&odblac;"], [0, "&OElig;"], [0, "&oelig;"], [0, "&Racute;"], [0, "&racute;"], [0, "&Rcedil;"], [0, "&rcedil;"], [0, "&Rcaron;"], [0, "&rcaron;"], [0, "&Sacute;"], [0, "&sacute;"], [0, "&Scirc;"], [0, "&scirc;"], [0, "&Scedil;"], [0, "&scedil;"], [0, "&Scaron;"], [0, "&scaron;"], [0, "&Tcedil;"], [0, "&tcedil;"], [0, "&Tcaron;"], [0, "&tcaron;"], [0, "&Tstrok;"], [0, "&tstrok;"], [0, "&Utilde;"], [0, "&utilde;"], [0, "&Umacr;"], [0, "&umacr;"], [0, "&Ubreve;"], [0, "&ubreve;"], [0, "&Uring;"], [0, "&uring;"], [0, "&Udblac;"], [0, "&udblac;"], [0, "&Uogon;"], [0, "&uogon;"], [0, "&Wcirc;"], [0, "&wcirc;"], [0, "&Ycirc;"], [0, "&ycirc;"], [0, "&Yuml;"], [0, "&Zacute;"], [0, "&zacute;"], [0, "&Zdot;"], [0, "&zdot;"], [0, "&Zcaron;"], [0, "&zcaron;"], [19, "&fnof;"], [34, "&imped;"], [63, "&gacute;"], [65, "&jmath;"], [142, "&circ;"], [0, "&caron;"], [16, "&breve;"], [0, "&DiacriticalDot;"], [0, "&ring;"], [0, "&ogon;"], [0, "&DiacriticalTilde;"], [0, "&dblac;"], [51, "&DownBreve;"], [127, "&Alpha;"], [0, "&Beta;"], [0, "&Gamma;"], [0, "&Delta;"], [0, "&Epsilon;"], [0, "&Zeta;"], [0, "&Eta;"], [0, "&Theta;"], [0, "&Iota;"], [0, "&Kappa;"], [0, "&Lambda;"], [0, "&Mu;"], [0, "&Nu;"], [0, "&Xi;"], [0, "&Omicron;"], [0, "&Pi;"], [0, "&Rho;"], [1, "&Sigma;"], [0, "&Tau;"], [0, "&Upsilon;"], [0, "&Phi;"], [0, "&Chi;"], [0, "&Psi;"], [0, "&ohm;"], [7, "&alpha;"], [0, "&beta;"], [0, "&gamma;"], [0, "&delta;"], [0, "&epsi;"], [0, "&zeta;"], [0, "&eta;"], [0, "&theta;"], [0, "&iota;"], [0, "&kappa;"], [0, "&lambda;"], [0, "&mu;"], [0, "&nu;"], [0, "&xi;"], [0, "&omicron;"], [0, "&pi;"], [0, "&rho;"], [0, "&sigmaf;"], [0, "&sigma;"], [0, "&tau;"], [0, "&upsi;"], [0, "&phi;"], [0, "&chi;"], [0, "&psi;"], [0, "&omega;"], [7, "&thetasym;"], [0, "&Upsi;"], [2, "&phiv;"], [0, "&piv;"], [5, "&Gammad;"], [0, "&digamma;"], [18, "&kappav;"], [0, "&rhov;"], [3, "&epsiv;"], [0, "&backepsilon;"], [10, "&IOcy;"], [0, "&DJcy;"], [0, "&GJcy;"], [0, "&Jukcy;"], [0, "&DScy;"], [0, "&Iukcy;"], [0, "&YIcy;"], [0, "&Jsercy;"], [0, "&LJcy;"], [0, "&NJcy;"], [0, "&TSHcy;"], [0, "&KJcy;"], [1, "&Ubrcy;"], [0, "&DZcy;"], [0, "&Acy;"], [0, "&Bcy;"], [0, "&Vcy;"], [0, "&Gcy;"], [0, "&Dcy;"], [0, "&IEcy;"], [0, "&ZHcy;"], [0, "&Zcy;"], [0, "&Icy;"], [0, "&Jcy;"], [0, "&Kcy;"], [0, "&Lcy;"], [0, "&Mcy;"], [0, "&Ncy;"], [0, "&Ocy;"], [0, "&Pcy;"], [0, "&Rcy;"], [0, "&Scy;"], [0, "&Tcy;"], [0, "&Ucy;"], [0, "&Fcy;"], [0, "&KHcy;"], [0, "&TScy;"], [0, "&CHcy;"], [0, "&SHcy;"], [0, "&SHCHcy;"], [0, "&HARDcy;"], [0, "&Ycy;"], [0, "&SOFTcy;"], [0, "&Ecy;"], [0, "&YUcy;"], [0, "&YAcy;"], [0, "&acy;"], [0, "&bcy;"], [0, "&vcy;"], [0, "&gcy;"], [0, "&dcy;"], [0, "&iecy;"], [0, "&zhcy;"], [0, "&zcy;"], [0, "&icy;"], [0, "&jcy;"], [0, "&kcy;"], [0, "&lcy;"], [0, "&mcy;"], [0, "&ncy;"], [0, "&ocy;"], [0, "&pcy;"], [0, "&rcy;"], [0, "&scy;"], [0, "&tcy;"], [0, "&ucy;"], [0, "&fcy;"], [0, "&khcy;"], [0, "&tscy;"], [0, "&chcy;"], [0, "&shcy;"], [0, "&shchcy;"], [0, "&hardcy;"], [0, "&ycy;"], [0, "&softcy;"], [0, "&ecy;"], [0, "&yucy;"], [0, "&yacy;"], [1, "&iocy;"], [0, "&djcy;"], [0, "&gjcy;"], [0, "&jukcy;"], [0, "&dscy;"], [0, "&iukcy;"], [0, "&yicy;"], [0, "&jsercy;"], [0, "&ljcy;"], [0, "&njcy;"], [0, "&tshcy;"], [0, "&kjcy;"], [1, "&ubrcy;"], [0, "&dzcy;"], [7074, "&ensp;"], [0, "&emsp;"], [0, "&emsp13;"], [0, "&emsp14;"], [1, "&numsp;"], [0, "&puncsp;"], [0, "&ThinSpace;"], [0, "&hairsp;"], [0, "&NegativeMediumSpace;"], [0, "&zwnj;"], [0, "&zwj;"], [0, "&lrm;"], [0, "&rlm;"], [0, "&dash;"], [2, "&ndash;"], [0, "&mdash;"], [0, "&horbar;"], [0, "&Verbar;"], [1, "&lsquo;"], [0, "&CloseCurlyQuote;"], [0, "&lsquor;"], [1, "&ldquo;"], [0, "&CloseCurlyDoubleQuote;"], [0, "&bdquo;"], [1, "&dagger;"], [0, "&Dagger;"], [0, "&bull;"], [2, "&nldr;"], [0, "&hellip;"], [9, "&permil;"], [0, "&pertenk;"], [0, "&prime;"], [0, "&Prime;"], [0, "&tprime;"], [0, "&backprime;"], [3, "&lsaquo;"], [0, "&rsaquo;"], [3, "&oline;"], [2, "&caret;"], [1, "&hybull;"], [0, "&frasl;"], [10, "&bsemi;"], [7, "&qprime;"], [7, { v: "&MediumSpace;", n: 8202, o: "&ThickSpace;" }], [0, "&NoBreak;"], [0, "&af;"], [0, "&InvisibleTimes;"], [0, "&ic;"], [72, "&euro;"], [46, "&tdot;"], [0, "&DotDot;"], [37, "&complexes;"], [2, "&incare;"], [4, "&gscr;"], [0, "&hamilt;"], [0, "&Hfr;"], [0, "&Hopf;"], [0, "&planckh;"], [0, "&hbar;"], [0, "&imagline;"], [0, "&Ifr;"], [0, "&lagran;"], [0, "&ell;"], [1, "&naturals;"], [0, "&numero;"], [0, "&copysr;"], [0, "&weierp;"], [0, "&Popf;"], [0, "&Qopf;"], [0, "&realine;"], [0, "&real;"], [0, "&reals;"], [0, "&rx;"], [3, "&trade;"], [1, "&integers;"], [2, "&mho;"], [0, "&zeetrf;"], [0, "&iiota;"], [2, "&bernou;"], [0, "&Cayleys;"], [1, "&escr;"], [0, "&Escr;"], [0, "&Fouriertrf;"], [1, "&Mellintrf;"], [0, "&order;"], [0, "&alefsym;"], [0, "&beth;"], [0, "&gimel;"], [0, "&daleth;"], [12, "&CapitalDifferentialD;"], [0, "&dd;"], [0, "&ee;"], [0, "&ii;"], [10, "&frac13;"], [0, "&frac23;"], [0, "&frac15;"], [0, "&frac25;"], [0, "&frac35;"], [0, "&frac45;"], [0, "&frac16;"], [0, "&frac56;"], [0, "&frac18;"], [0, "&frac38;"], [0, "&frac58;"], [0, "&frac78;"], [49, "&larr;"], [0, "&ShortUpArrow;"], [0, "&rarr;"], [0, "&darr;"], [0, "&harr;"], [0, "&updownarrow;"], [0, "&nwarr;"], [0, "&nearr;"], [0, "&LowerRightArrow;"], [0, "&LowerLeftArrow;"], [0, "&nlarr;"], [0, "&nrarr;"], [1, { v: "&rarrw;", n: 824, o: "&nrarrw;" }], [0, "&Larr;"], [0, "&Uarr;"], [0, "&Rarr;"], [0, "&Darr;"], [0, "&larrtl;"], [0, "&rarrtl;"], [0, "&LeftTeeArrow;"], [0, "&mapstoup;"], [0, "&map;"], [0, "&DownTeeArrow;"], [1, "&hookleftarrow;"], [0, "&hookrightarrow;"], [0, "&larrlp;"], [0, "&looparrowright;"], [0, "&harrw;"], [0, "&nharr;"], [1, "&lsh;"], [0, "&rsh;"], [0, "&ldsh;"], [0, "&rdsh;"], [1, "&crarr;"], [0, "&cularr;"], [0, "&curarr;"], [2, "&circlearrowleft;"], [0, "&circlearrowright;"], [0, "&leftharpoonup;"], [0, "&DownLeftVector;"], [0, "&RightUpVector;"], [0, "&LeftUpVector;"], [0, "&rharu;"], [0, "&DownRightVector;"], [0, "&dharr;"], [0, "&dharl;"], [0, "&RightArrowLeftArrow;"], [0, "&udarr;"], [0, "&LeftArrowRightArrow;"], [0, "&leftleftarrows;"], [0, "&upuparrows;"], [0, "&rightrightarrows;"], [0, "&ddarr;"], [0, "&leftrightharpoons;"], [0, "&Equilibrium;"], [0, "&nlArr;"], [0, "&nhArr;"], [0, "&nrArr;"], [0, "&DoubleLeftArrow;"], [0, "&DoubleUpArrow;"], [0, "&DoubleRightArrow;"], [0, "&dArr;"], [0, "&DoubleLeftRightArrow;"], [0, "&DoubleUpDownArrow;"], [0, "&nwArr;"], [0, "&neArr;"], [0, "&seArr;"], [0, "&swArr;"], [0, "&lAarr;"], [0, "&rAarr;"], [1, "&zigrarr;"], [6, "&larrb;"], [0, "&rarrb;"], [15, "&DownArrowUpArrow;"], [7, "&loarr;"], [0, "&roarr;"], [0, "&hoarr;"], [0, "&forall;"], [0, "&comp;"], [0, { v: "&part;", n: 824, o: "&npart;" }], [0, "&exist;"], [0, "&nexist;"], [0, "&empty;"], [1, "&Del;"], [0, "&Element;"], [0, "&NotElement;"], [1, "&ni;"], [0, "&notni;"], [2, "&prod;"], [0, "&coprod;"], [0, "&sum;"], [0, "&minus;"], [0, "&MinusPlus;"], [0, "&dotplus;"], [1, "&Backslash;"], [0, "&lowast;"], [0, "&compfn;"], [1, "&radic;"], [2, "&prop;"], [0, "&infin;"], [0, "&angrt;"], [0, { v: "&ang;", n: 8402, o: "&nang;" }], [0, "&angmsd;"], [0, "&angsph;"], [0, "&mid;"], [0, "&nmid;"], [0, "&DoubleVerticalBar;"], [0, "&NotDoubleVerticalBar;"], [0, "&and;"], [0, "&or;"], [0, { v: "&cap;", n: 65024, o: "&caps;" }], [0, { v: "&cup;", n: 65024, o: "&cups;" }], [0, "&int;"], [0, "&Int;"], [0, "&iiint;"], [0, "&conint;"], [0, "&Conint;"], [0, "&Cconint;"], [0, "&cwint;"], [0, "&ClockwiseContourIntegral;"], [0, "&awconint;"], [0, "&there4;"], [0, "&becaus;"], [0, "&ratio;"], [0, "&Colon;"], [0, "&dotminus;"], [1, "&mDDot;"], [0, "&homtht;"], [0, { v: "&sim;", n: 8402, o: "&nvsim;" }], [0, { v: "&backsim;", n: 817, o: "&race;" }], [0, { v: "&ac;", n: 819, o: "&acE;" }], [0, "&acd;"], [0, "&VerticalTilde;"], [0, "&NotTilde;"], [0, { v: "&eqsim;", n: 824, o: "&nesim;" }], [0, "&sime;"], [0, "&NotTildeEqual;"], [0, "&cong;"], [0, "&simne;"], [0, "&ncong;"], [0, "&ap;"], [0, "&nap;"], [0, "&ape;"], [0, { v: "&apid;", n: 824, o: "&napid;" }], [0, "&backcong;"], [0, { v: "&asympeq;", n: 8402, o: "&nvap;" }], [0, { v: "&bump;", n: 824, o: "&nbump;" }], [0, { v: "&bumpe;", n: 824, o: "&nbumpe;" }], [0, { v: "&doteq;", n: 824, o: "&nedot;" }], [0, "&doteqdot;"], [0, "&efDot;"], [0, "&erDot;"], [0, "&Assign;"], [0, "&ecolon;"], [0, "&ecir;"], [0, "&circeq;"], [1, "&wedgeq;"], [0, "&veeeq;"], [1, "&triangleq;"], [2, "&equest;"], [0, "&ne;"], [0, { v: "&Congruent;", n: 8421, o: "&bnequiv;" }], [0, "&nequiv;"], [1, { v: "&le;", n: 8402, o: "&nvle;" }], [0, { v: "&ge;", n: 8402, o: "&nvge;" }], [0, { v: "&lE;", n: 824, o: "&nlE;" }], [0, { v: "&gE;", n: 824, o: "&ngE;" }], [0, { v: "&lnE;", n: 65024, o: "&lvertneqq;" }], [0, { v: "&gnE;", n: 65024, o: "&gvertneqq;" }], [0, { v: "&ll;", n: new Map(/* @__PURE__ */ restoreDiff([[824, "&nLtv;"], [7577, "&nLt;"]])) }], [0, { v: "&gg;", n: new Map(/* @__PURE__ */ restoreDiff([[824, "&nGtv;"], [7577, "&nGt;"]])) }], [0, "&between;"], [0, "&NotCupCap;"], [0, "&nless;"], [0, "&ngt;"], [0, "&nle;"], [0, "&nge;"], [0, "&lesssim;"], [0, "&GreaterTilde;"], [0, "&nlsim;"], [0, "&ngsim;"], [0, "&LessGreater;"], [0, "&gl;"], [0, "&NotLessGreater;"], [0, "&NotGreaterLess;"], [0, "&pr;"], [0, "&sc;"], [0, "&prcue;"], [0, "&sccue;"], [0, "&PrecedesTilde;"], [0, { v: "&scsim;", n: 824, o: "&NotSucceedsTilde;" }], [0, "&NotPrecedes;"], [0, "&NotSucceeds;"], [0, { v: "&sub;", n: 8402, o: "&NotSubset;" }], [0, { v: "&sup;", n: 8402, o: "&NotSuperset;" }], [0, "&nsub;"], [0, "&nsup;"], [0, "&sube;"], [0, "&supe;"], [0, "&NotSubsetEqual;"], [0, "&NotSupersetEqual;"], [0, { v: "&subne;", n: 65024, o: "&varsubsetneq;" }], [0, { v: "&supne;", n: 65024, o: "&varsupsetneq;" }], [1, "&cupdot;"], [0, "&UnionPlus;"], [0, { v: "&sqsub;", n: 824, o: "&NotSquareSubset;" }], [0, { v: "&sqsup;", n: 824, o: "&NotSquareSuperset;" }], [0, "&sqsube;"], [0, "&sqsupe;"], [0, { v: "&sqcap;", n: 65024, o: "&sqcaps;" }], [0, { v: "&sqcup;", n: 65024, o: "&sqcups;" }], [0, "&CirclePlus;"], [0, "&CircleMinus;"], [0, "&CircleTimes;"], [0, "&osol;"], [0, "&CircleDot;"], [0, "&circledcirc;"], [0, "&circledast;"], [1, "&circleddash;"], [0, "&boxplus;"], [0, "&boxminus;"], [0, "&boxtimes;"], [0, "&dotsquare;"], [0, "&RightTee;"], [0, "&dashv;"], [0, "&DownTee;"], [0, "&bot;"], [1, "&models;"], [0, "&DoubleRightTee;"], [0, "&Vdash;"], [0, "&Vvdash;"], [0, "&VDash;"], [0, "&nvdash;"], [0, "&nvDash;"], [0, "&nVdash;"], [0, "&nVDash;"], [0, "&prurel;"], [1, "&LeftTriangle;"], [0, "&RightTriangle;"], [0, { v: "&LeftTriangleEqual;", n: 8402, o: "&nvltrie;" }], [0, { v: "&RightTriangleEqual;", n: 8402, o: "&nvrtrie;" }], [0, "&origof;"], [0, "&imof;"], [0, "&multimap;"], [0, "&hercon;"], [0, "&intcal;"], [0, "&veebar;"], [1, "&barvee;"], [0, "&angrtvb;"], [0, "&lrtri;"], [0, "&bigwedge;"], [0, "&bigvee;"], [0, "&bigcap;"], [0, "&bigcup;"], [0, "&diam;"], [0, "&sdot;"], [0, "&sstarf;"], [0, "&divideontimes;"], [0, "&bowtie;"], [0, "&ltimes;"], [0, "&rtimes;"], [0, "&leftthreetimes;"], [0, "&rightthreetimes;"], [0, "&backsimeq;"], [0, "&curlyvee;"], [0, "&curlywedge;"], [0, "&Sub;"], [0, "&Sup;"], [0, "&Cap;"], [0, "&Cup;"], [0, "&fork;"], [0, "&epar;"], [0, "&lessdot;"], [0, "&gtdot;"], [0, { v: "&Ll;", n: 824, o: "&nLl;" }], [0, { v: "&Gg;", n: 824, o: "&nGg;" }], [0, { v: "&leg;", n: 65024, o: "&lesg;" }], [0, { v: "&gel;", n: 65024, o: "&gesl;" }], [2, "&cuepr;"], [0, "&cuesc;"], [0, "&NotPrecedesSlantEqual;"], [0, "&NotSucceedsSlantEqual;"], [0, "&NotSquareSubsetEqual;"], [0, "&NotSquareSupersetEqual;"], [2, "&lnsim;"], [0, "&gnsim;"], [0, "&precnsim;"], [0, "&scnsim;"], [0, "&nltri;"], [0, "&NotRightTriangle;"], [0, "&nltrie;"], [0, "&NotRightTriangleEqual;"], [0, "&vellip;"], [0, "&ctdot;"], [0, "&utdot;"], [0, "&dtdot;"], [0, "&disin;"], [0, "&isinsv;"], [0, "&isins;"], [0, { v: "&isindot;", n: 824, o: "&notindot;" }], [0, "&notinvc;"], [0, "&notinvb;"], [1, { v: "&isinE;", n: 824, o: "&notinE;" }], [0, "&nisd;"], [0, "&xnis;"], [0, "&nis;"], [0, "&notnivc;"], [0, "&notnivb;"], [6, "&barwed;"], [0, "&Barwed;"], [1, "&lceil;"], [0, "&rceil;"], [0, "&LeftFloor;"], [0, "&rfloor;"], [0, "&drcrop;"], [0, "&dlcrop;"], [0, "&urcrop;"], [0, "&ulcrop;"], [0, "&bnot;"], [1, "&profline;"], [0, "&profsurf;"], [1, "&telrec;"], [0, "&target;"], [5, "&ulcorn;"], [0, "&urcorn;"], [0, "&dlcorn;"], [0, "&drcorn;"], [2, "&frown;"], [0, "&smile;"], [9, "&cylcty;"], [0, "&profalar;"], [7, "&topbot;"], [6, "&ovbar;"], [1, "&solbar;"], [60, "&angzarr;"], [51, "&lmoustache;"], [0, "&rmoustache;"], [2, "&OverBracket;"], [0, "&bbrk;"], [0, "&bbrktbrk;"], [37, "&OverParenthesis;"], [0, "&UnderParenthesis;"], [0, "&OverBrace;"], [0, "&UnderBrace;"], [2, "&trpezium;"], [4, "&elinters;"], [59, "&blank;"], [164, "&circledS;"], [55, "&boxh;"], [1, "&boxv;"], [9, "&boxdr;"], [3, "&boxdl;"], [3, "&boxur;"], [3, "&boxul;"], [3, "&boxvr;"], [7, "&boxvl;"], [7, "&boxhd;"], [7, "&boxhu;"], [7, "&boxvh;"], [19, "&boxH;"], [0, "&boxV;"], [0, "&boxdR;"], [0, "&boxDr;"], [0, "&boxDR;"], [0, "&boxdL;"], [0, "&boxDl;"], [0, "&boxDL;"], [0, "&boxuR;"], [0, "&boxUr;"], [0, "&boxUR;"], [0, "&boxuL;"], [0, "&boxUl;"], [0, "&boxUL;"], [0, "&boxvR;"], [0, "&boxVr;"], [0, "&boxVR;"], [0, "&boxvL;"], [0, "&boxVl;"], [0, "&boxVL;"], [0, "&boxHd;"], [0, "&boxhD;"], [0, "&boxHD;"], [0, "&boxHu;"], [0, "&boxhU;"], [0, "&boxHU;"], [0, "&boxvH;"], [0, "&boxVh;"], [0, "&boxVH;"], [19, "&uhblk;"], [3, "&lhblk;"], [3, "&block;"], [8, "&blk14;"], [0, "&blk12;"], [0, "&blk34;"], [13, "&square;"], [8, "&blacksquare;"], [0, "&EmptyVerySmallSquare;"], [1, "&rect;"], [0, "&marker;"], [2, "&fltns;"], [1, "&bigtriangleup;"], [0, "&blacktriangle;"], [0, "&triangle;"], [2, "&blacktriangleright;"], [0, "&rtri;"], [3, "&bigtriangledown;"], [0, "&blacktriangledown;"], [0, "&dtri;"], [2, "&blacktriangleleft;"], [0, "&ltri;"], [6, "&loz;"], [0, "&cir;"], [32, "&tridot;"], [2, "&bigcirc;"], [8, "&ultri;"], [0, "&urtri;"], [0, "&lltri;"], [0, "&EmptySmallSquare;"], [0, "&FilledSmallSquare;"], [8, "&bigstar;"], [0, "&star;"], [7, "&phone;"], [49, "&female;"], [1, "&male;"], [29, "&spades;"], [2, "&clubs;"], [1, "&hearts;"], [0, "&diamondsuit;"], [3, "&sung;"], [2, "&flat;"], [0, "&natural;"], [0, "&sharp;"], [163, "&check;"], [3, "&cross;"], [8, "&malt;"], [21, "&sext;"], [33, "&VerticalSeparator;"], [25, "&lbbrk;"], [0, "&rbbrk;"], [84, "&bsolhsub;"], [0, "&suphsol;"], [28, "&LeftDoubleBracket;"], [0, "&RightDoubleBracket;"], [0, "&lang;"], [0, "&rang;"], [0, "&Lang;"], [0, "&Rang;"], [0, "&loang;"], [0, "&roang;"], [7, "&longleftarrow;"], [0, "&longrightarrow;"], [0, "&longleftrightarrow;"], [0, "&DoubleLongLeftArrow;"], [0, "&DoubleLongRightArrow;"], [0, "&DoubleLongLeftRightArrow;"], [1, "&longmapsto;"], [2, "&dzigrarr;"], [258, "&nvlArr;"], [0, "&nvrArr;"], [0, "&nvHarr;"], [0, "&Map;"], [6, "&lbarr;"], [0, "&bkarow;"], [0, "&lBarr;"], [0, "&dbkarow;"], [0, "&drbkarow;"], [0, "&DDotrahd;"], [0, "&UpArrowBar;"], [0, "&DownArrowBar;"], [2, "&Rarrtl;"], [2, "&latail;"], [0, "&ratail;"], [0, "&lAtail;"], [0, "&rAtail;"], [0, "&larrfs;"], [0, "&rarrfs;"], [0, "&larrbfs;"], [0, "&rarrbfs;"], [2, "&nwarhk;"], [0, "&nearhk;"], [0, "&hksearow;"], [0, "&hkswarow;"], [0, "&nwnear;"], [0, "&nesear;"], [0, "&seswar;"], [0, "&swnwar;"], [8, { v: "&rarrc;", n: 824, o: "&nrarrc;" }], [1, "&cudarrr;"], [0, "&ldca;"], [0, "&rdca;"], [0, "&cudarrl;"], [0, "&larrpl;"], [2, "&curarrm;"], [0, "&cularrp;"], [7, "&rarrpl;"], [2, "&harrcir;"], [0, "&Uarrocir;"], [0, "&lurdshar;"], [0, "&ldrushar;"], [2, "&LeftRightVector;"], [0, "&RightUpDownVector;"], [0, "&DownLeftRightVector;"], [0, "&LeftUpDownVector;"], [0, "&LeftVectorBar;"], [0, "&RightVectorBar;"], [0, "&RightUpVectorBar;"], [0, "&RightDownVectorBar;"], [0, "&DownLeftVectorBar;"], [0, "&DownRightVectorBar;"], [0, "&LeftUpVectorBar;"], [0, "&LeftDownVectorBar;"], [0, "&LeftTeeVector;"], [0, "&RightTeeVector;"], [0, "&RightUpTeeVector;"], [0, "&RightDownTeeVector;"], [0, "&DownLeftTeeVector;"], [0, "&DownRightTeeVector;"], [0, "&LeftUpTeeVector;"], [0, "&LeftDownTeeVector;"], [0, "&lHar;"], [0, "&uHar;"], [0, "&rHar;"], [0, "&dHar;"], [0, "&luruhar;"], [0, "&ldrdhar;"], [0, "&ruluhar;"], [0, "&rdldhar;"], [0, "&lharul;"], [0, "&llhard;"], [0, "&rharul;"], [0, "&lrhard;"], [0, "&udhar;"], [0, "&duhar;"], [0, "&RoundImplies;"], [0, "&erarr;"], [0, "&simrarr;"], [0, "&larrsim;"], [0, "&rarrsim;"], [0, "&rarrap;"], [0, "&ltlarr;"], [1, "&gtrarr;"], [0, "&subrarr;"], [1, "&suplarr;"], [0, "&lfisht;"], [0, "&rfisht;"], [0, "&ufisht;"], [0, "&dfisht;"], [5, "&lopar;"], [0, "&ropar;"], [4, "&lbrke;"], [0, "&rbrke;"], [0, "&lbrkslu;"], [0, "&rbrksld;"], [0, "&lbrksld;"], [0, "&rbrkslu;"], [0, "&langd;"], [0, "&rangd;"], [0, "&lparlt;"], [0, "&rpargt;"], [0, "&gtlPar;"], [0, "&ltrPar;"], [3, "&vzigzag;"], [1, "&vangrt;"], [0, "&angrtvbd;"], [6, "&ange;"], [0, "&range;"], [0, "&dwangle;"], [0, "&uwangle;"], [0, "&angmsdaa;"], [0, "&angmsdab;"], [0, "&angmsdac;"], [0, "&angmsdad;"], [0, "&angmsdae;"], [0, "&angmsdaf;"], [0, "&angmsdag;"], [0, "&angmsdah;"], [0, "&bemptyv;"], [0, "&demptyv;"], [0, "&cemptyv;"], [0, "&raemptyv;"], [0, "&laemptyv;"], [0, "&ohbar;"], [0, "&omid;"], [0, "&opar;"], [1, "&operp;"], [1, "&olcross;"], [0, "&odsold;"], [1, "&olcir;"], [0, "&ofcir;"], [0, "&olt;"], [0, "&ogt;"], [0, "&cirscir;"], [0, "&cirE;"], [0, "&solb;"], [0, "&bsolb;"], [3, "&boxbox;"], [3, "&trisb;"], [0, "&rtriltri;"], [0, { v: "&LeftTriangleBar;", n: 824, o: "&NotLeftTriangleBar;" }], [0, { v: "&RightTriangleBar;", n: 824, o: "&NotRightTriangleBar;" }], [11, "&iinfin;"], [0, "&infintie;"], [0, "&nvinfin;"], [4, "&eparsl;"], [0, "&smeparsl;"], [0, "&eqvparsl;"], [5, "&blacklozenge;"], [8, "&RuleDelayed;"], [1, "&dsol;"], [9, "&bigodot;"], [0, "&bigoplus;"], [0, "&bigotimes;"], [1, "&biguplus;"], [1, "&bigsqcup;"], [5, "&iiiint;"], [0, "&fpartint;"], [2, "&cirfnint;"], [0, "&awint;"], [0, "&rppolint;"], [0, "&scpolint;"], [0, "&npolint;"], [0, "&pointint;"], [0, "&quatint;"], [0, "&intlarhk;"], [10, "&pluscir;"], [0, "&plusacir;"], [0, "&simplus;"], [0, "&plusdu;"], [0, "&plussim;"], [0, "&plustwo;"], [1, "&mcomma;"], [0, "&minusdu;"], [2, "&loplus;"], [0, "&roplus;"], [0, "&Cross;"], [0, "&timesd;"], [0, "&timesbar;"], [1, "&smashp;"], [0, "&lotimes;"], [0, "&rotimes;"], [0, "&otimesas;"], [0, "&Otimes;"], [0, "&odiv;"], [0, "&triplus;"], [0, "&triminus;"], [0, "&tritime;"], [0, "&intprod;"], [2, "&amalg;"], [0, "&capdot;"], [1, "&ncup;"], [0, "&ncap;"], [0, "&capand;"], [0, "&cupor;"], [0, "&cupcap;"], [0, "&capcup;"], [0, "&cupbrcap;"], [0, "&capbrcup;"], [0, "&cupcup;"], [0, "&capcap;"], [0, "&ccups;"], [0, "&ccaps;"], [2, "&ccupssm;"], [2, "&And;"], [0, "&Or;"], [0, "&andand;"], [0, "&oror;"], [0, "&orslope;"], [0, "&andslope;"], [1, "&andv;"], [0, "&orv;"], [0, "&andd;"], [0, "&ord;"], [1, "&wedbar;"], [6, "&sdote;"], [3, "&simdot;"], [2, { v: "&congdot;", n: 824, o: "&ncongdot;" }], [0, "&easter;"], [0, "&apacir;"], [0, { v: "&apE;", n: 824, o: "&napE;" }], [0, "&eplus;"], [0, "&pluse;"], [0, "&Esim;"], [0, "&Colone;"], [0, "&Equal;"], [1, "&ddotseq;"], [0, "&equivDD;"], [0, "&ltcir;"], [0, "&gtcir;"], [0, "&ltquest;"], [0, "&gtquest;"], [0, { v: "&leqslant;", n: 824, o: "&nleqslant;" }], [0, { v: "&geqslant;", n: 824, o: "&ngeqslant;" }], [0, "&lesdot;"], [0, "&gesdot;"], [0, "&lesdoto;"], [0, "&gesdoto;"], [0, "&lesdotor;"], [0, "&gesdotol;"], [0, "&lap;"], [0, "&gap;"], [0, "&lne;"], [0, "&gne;"], [0, "&lnap;"], [0, "&gnap;"], [0, "&lEg;"], [0, "&gEl;"], [0, "&lsime;"], [0, "&gsime;"], [0, "&lsimg;"], [0, "&gsiml;"], [0, "&lgE;"], [0, "&glE;"], [0, "&lesges;"], [0, "&gesles;"], [0, "&els;"], [0, "&egs;"], [0, "&elsdot;"], [0, "&egsdot;"], [0, "&el;"], [0, "&eg;"], [2, "&siml;"], [0, "&simg;"], [0, "&simlE;"], [0, "&simgE;"], [0, { v: "&LessLess;", n: 824, o: "&NotNestedLessLess;" }], [0, { v: "&GreaterGreater;", n: 824, o: "&NotNestedGreaterGreater;" }], [1, "&glj;"], [0, "&gla;"], [0, "&ltcc;"], [0, "&gtcc;"], [0, "&lescc;"], [0, "&gescc;"], [0, "&smt;"], [0, "&lat;"], [0, { v: "&smte;", n: 65024, o: "&smtes;" }], [0, { v: "&late;", n: 65024, o: "&lates;" }], [0, "&bumpE;"], [0, { v: "&PrecedesEqual;", n: 824, o: "&NotPrecedesEqual;" }], [0, { v: "&sce;", n: 824, o: "&NotSucceedsEqual;" }], [2, "&prE;"], [0, "&scE;"], [0, "&precneqq;"], [0, "&scnE;"], [0, "&prap;"], [0, "&scap;"], [0, "&precnapprox;"], [0, "&scnap;"], [0, "&Pr;"], [0, "&Sc;"], [0, "&subdot;"], [0, "&supdot;"], [0, "&subplus;"], [0, "&supplus;"], [0, "&submult;"], [0, "&supmult;"], [0, "&subedot;"], [0, "&supedot;"], [0, { v: "&subE;", n: 824, o: "&nsubE;" }], [0, { v: "&supE;", n: 824, o: "&nsupE;" }], [0, "&subsim;"], [0, "&supsim;"], [2, { v: "&subnE;", n: 65024, o: "&varsubsetneqq;" }], [0, { v: "&supnE;", n: 65024, o: "&varsupsetneqq;" }], [2, "&csub;"], [0, "&csup;"], [0, "&csube;"], [0, "&csupe;"], [0, "&subsup;"], [0, "&supsub;"], [0, "&subsub;"], [0, "&supsup;"], [0, "&suphsub;"], [0, "&supdsub;"], [0, "&forkv;"], [0, "&topfork;"], [0, "&mlcp;"], [8, "&Dashv;"], [1, "&Vdashl;"], [0, "&Barv;"], [0, "&vBar;"], [0, "&vBarv;"], [1, "&Vbar;"], [0, "&Not;"], [0, "&bNot;"], [0, "&rnmid;"], [0, "&cirmid;"], [0, "&midcir;"], [0, "&topcir;"], [0, "&nhpar;"], [0, "&parsim;"], [9, { v: "&parsl;", n: 8421, o: "&nparsl;" }], [44343, { n: new Map(/* @__PURE__ */ restoreDiff([[56476, "&Ascr;"], [1, "&Cscr;"], [0, "&Dscr;"], [2, "&Gscr;"], [2, "&Jscr;"], [0, "&Kscr;"], [2, "&Nscr;"], [0, "&Oscr;"], [0, "&Pscr;"], [0, "&Qscr;"], [1, "&Sscr;"], [0, "&Tscr;"], [0, "&Uscr;"], [0, "&Vscr;"], [0, "&Wscr;"], [0, "&Xscr;"], [0, "&Yscr;"], [0, "&Zscr;"], [0, "&ascr;"], [0, "&bscr;"], [0, "&cscr;"], [0, "&dscr;"], [1, "&fscr;"], [1, "&hscr;"], [0, "&iscr;"], [0, "&jscr;"], [0, "&kscr;"], [0, "&lscr;"], [0, "&mscr;"], [0, "&nscr;"], [1, "&pscr;"], [0, "&qscr;"], [0, "&rscr;"], [0, "&sscr;"], [0, "&tscr;"], [0, "&uscr;"], [0, "&vscr;"], [0, "&wscr;"], [0, "&xscr;"], [0, "&yscr;"], [0, "&zscr;"], [52, "&Afr;"], [0, "&Bfr;"], [1, "&Dfr;"], [0, "&Efr;"], [0, "&Ffr;"], [0, "&Gfr;"], [2, "&Jfr;"], [0, "&Kfr;"], [0, "&Lfr;"], [0, "&Mfr;"], [0, "&Nfr;"], [0, "&Ofr;"], [0, "&Pfr;"], [0, "&Qfr;"], [1, "&Sfr;"], [0, "&Tfr;"], [0, "&Ufr;"], [0, "&Vfr;"], [0, "&Wfr;"], [0, "&Xfr;"], [0, "&Yfr;"], [1, "&afr;"], [0, "&bfr;"], [0, "&cfr;"], [0, "&dfr;"], [0, "&efr;"], [0, "&ffr;"], [0, "&gfr;"], [0, "&hfr;"], [0, "&ifr;"], [0, "&jfr;"], [0, "&kfr;"], [0, "&lfr;"], [0, "&mfr;"], [0, "&nfr;"], [0, "&ofr;"], [0, "&pfr;"], [0, "&qfr;"], [0, "&rfr;"], [0, "&sfr;"], [0, "&tfr;"], [0, "&ufr;"], [0, "&vfr;"], [0, "&wfr;"], [0, "&xfr;"], [0, "&yfr;"], [0, "&zfr;"], [0, "&Aopf;"], [0, "&Bopf;"], [1, "&Dopf;"], [0, "&Eopf;"], [0, "&Fopf;"], [0, "&Gopf;"], [1, "&Iopf;"], [0, "&Jopf;"], [0, "&Kopf;"], [0, "&Lopf;"], [0, "&Mopf;"], [1, "&Oopf;"], [3, "&Sopf;"], [0, "&Topf;"], [0, "&Uopf;"], [0, "&Vopf;"], [0, "&Wopf;"], [0, "&Xopf;"], [0, "&Yopf;"], [1, "&aopf;"], [0, "&bopf;"], [0, "&copf;"], [0, "&dopf;"], [0, "&eopf;"], [0, "&fopf;"], [0, "&gopf;"], [0, "&hopf;"], [0, "&iopf;"], [0, "&jopf;"], [0, "&kopf;"], [0, "&lopf;"], [0, "&mopf;"], [0, "&nopf;"], [0, "&oopf;"], [0, "&popf;"], [0, "&qopf;"], [0, "&ropf;"], [0, "&sopf;"], [0, "&topf;"], [0, "&uopf;"], [0, "&vopf;"], [0, "&wopf;"], [0, "&xopf;"], [0, "&yopf;"], [0, "&zopf;"]])) }], [8906, "&fflig;"], [0, "&filig;"], [0, "&fllig;"], [0, "&ffilig;"], [0, "&ffllig;"]]));
  return encodeHtml;
}
var _escape = {};
var hasRequired_escape;
function require_escape() {
  if (hasRequired_escape) return _escape;
  hasRequired_escape = 1;
  (function(exports) {
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.escapeText = exports.escapeAttribute = exports.escapeUTF8 = exports.escape = exports.encodeXML = exports.getCodePoint = exports.xmlReplacer = void 0;
    exports.xmlReplacer = /["&'<>$\x80-\uFFFF]/g;
    var xmlCodeMap = /* @__PURE__ */ new Map([
      [34, "&quot;"],
      [38, "&amp;"],
      [39, "&apos;"],
      [60, "&lt;"],
      [62, "&gt;"]
    ]);
    exports.getCodePoint = // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
    String.prototype.codePointAt != null ? function(str, index) {
      return str.codePointAt(index);
    } : (
      // http://mathiasbynens.be/notes/javascript-encoding#surrogate-formulae
      function(c2, index) {
        return (c2.charCodeAt(index) & 64512) === 55296 ? (c2.charCodeAt(index) - 55296) * 1024 + c2.charCodeAt(index + 1) - 56320 + 65536 : c2.charCodeAt(index);
      }
    );
    function encodeXML(str) {
      var ret = "";
      var lastIdx = 0;
      var match;
      while ((match = exports.xmlReplacer.exec(str)) !== null) {
        var i2 = match.index;
        var char = str.charCodeAt(i2);
        var next = xmlCodeMap.get(char);
        if (next !== void 0) {
          ret += str.substring(lastIdx, i2) + next;
          lastIdx = i2 + 1;
        } else {
          ret += "".concat(str.substring(lastIdx, i2), "&#x").concat((0, exports.getCodePoint)(str, i2).toString(16), ";");
          lastIdx = exports.xmlReplacer.lastIndex += Number((char & 64512) === 55296);
        }
      }
      return ret + str.substr(lastIdx);
    }
    exports.encodeXML = encodeXML;
    exports.escape = encodeXML;
    function getEscaper(regex, map2) {
      return function escape2(data) {
        var match;
        var lastIdx = 0;
        var result = "";
        while (match = regex.exec(data)) {
          if (lastIdx !== match.index) {
            result += data.substring(lastIdx, match.index);
          }
          result += map2.get(match[0].charCodeAt(0));
          lastIdx = match.index + 1;
        }
        return result + data.substring(lastIdx);
      };
    }
    exports.escapeUTF8 = getEscaper(/[&<>'"]/g, xmlCodeMap);
    exports.escapeAttribute = getEscaper(/["&\u00A0]/g, /* @__PURE__ */ new Map([
      [34, "&quot;"],
      [38, "&amp;"],
      [160, "&nbsp;"]
    ]));
    exports.escapeText = getEscaper(/[&<>\u00A0]/g, /* @__PURE__ */ new Map([
      [38, "&amp;"],
      [60, "&lt;"],
      [62, "&gt;"],
      [160, "&nbsp;"]
    ]));
  })(_escape);
  return _escape;
}
var hasRequiredEncode;
function requireEncode() {
  if (hasRequiredEncode) return encode$1;
  hasRequiredEncode = 1;
  var __importDefault = encode$1 && encode$1.__importDefault || function(mod) {
    return mod && mod.__esModule ? mod : { "default": mod };
  };
  Object.defineProperty(encode$1, "__esModule", { value: true });
  encode$1.encodeNonAsciiHTML = encode$1.encodeHTML = void 0;
  var encode_html_js_1 = __importDefault(/* @__PURE__ */ requireEncodeHtml());
  var escape_js_1 = /* @__PURE__ */ require_escape();
  var htmlReplacer = /[\t\n!-,./:-@[-`\f{-}$\x80-\uFFFF]/g;
  function encodeHTML(data) {
    return encodeHTMLTrieRe(htmlReplacer, data);
  }
  encode$1.encodeHTML = encodeHTML;
  function encodeNonAsciiHTML(data) {
    return encodeHTMLTrieRe(escape_js_1.xmlReplacer, data);
  }
  encode$1.encodeNonAsciiHTML = encodeNonAsciiHTML;
  function encodeHTMLTrieRe(regExp, str) {
    var ret = "";
    var lastIdx = 0;
    var match;
    while ((match = regExp.exec(str)) !== null) {
      var i2 = match.index;
      ret += str.substring(lastIdx, i2);
      var char = str.charCodeAt(i2);
      var next = encode_html_js_1.default.get(char);
      if (typeof next === "object") {
        if (i2 + 1 < str.length) {
          var nextChar = str.charCodeAt(i2 + 1);
          var value = typeof next.n === "number" ? next.n === nextChar ? next.o : void 0 : next.n.get(nextChar);
          if (value !== void 0) {
            ret += value;
            lastIdx = regExp.lastIndex += 1;
            continue;
          }
        }
        next = next.v;
      }
      if (next !== void 0) {
        ret += next;
        lastIdx = i2 + 1;
      } else {
        var cp = (0, escape_js_1.getCodePoint)(str, i2);
        ret += "&#x".concat(cp.toString(16), ";");
        lastIdx = regExp.lastIndex += Number(cp !== char);
      }
    }
    return ret + str.substr(lastIdx);
  }
  return encode$1;
}
var hasRequiredLib;
function requireLib() {
  if (hasRequiredLib) return lib$1;
  hasRequiredLib = 1;
  (function(exports) {
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.decodeXMLStrict = exports.decodeHTML5Strict = exports.decodeHTML4Strict = exports.decodeHTML5 = exports.decodeHTML4 = exports.decodeHTMLAttribute = exports.decodeHTMLStrict = exports.decodeHTML = exports.decodeXML = exports.DecodingMode = exports.EntityDecoder = exports.encodeHTML5 = exports.encodeHTML4 = exports.encodeNonAsciiHTML = exports.encodeHTML = exports.escapeText = exports.escapeAttribute = exports.escapeUTF8 = exports.escape = exports.encodeXML = exports.encode = exports.decodeStrict = exports.decode = exports.EncodingMode = exports.EntityLevel = void 0;
    var decode_js_1 = /* @__PURE__ */ requireDecode();
    var encode_js_1 = /* @__PURE__ */ requireEncode();
    var escape_js_1 = /* @__PURE__ */ require_escape();
    var EntityLevel;
    (function(EntityLevel2) {
      EntityLevel2[EntityLevel2["XML"] = 0] = "XML";
      EntityLevel2[EntityLevel2["HTML"] = 1] = "HTML";
    })(EntityLevel = exports.EntityLevel || (exports.EntityLevel = {}));
    var EncodingMode;
    (function(EncodingMode2) {
      EncodingMode2[EncodingMode2["UTF8"] = 0] = "UTF8";
      EncodingMode2[EncodingMode2["ASCII"] = 1] = "ASCII";
      EncodingMode2[EncodingMode2["Extensive"] = 2] = "Extensive";
      EncodingMode2[EncodingMode2["Attribute"] = 3] = "Attribute";
      EncodingMode2[EncodingMode2["Text"] = 4] = "Text";
    })(EncodingMode = exports.EncodingMode || (exports.EncodingMode = {}));
    function decode2(data, options) {
      if (options === void 0) {
        options = EntityLevel.XML;
      }
      var level = typeof options === "number" ? options : options.level;
      if (level === EntityLevel.HTML) {
        var mode = typeof options === "object" ? options.mode : void 0;
        return (0, decode_js_1.decodeHTML)(data, mode);
      }
      return (0, decode_js_1.decodeXML)(data);
    }
    exports.decode = decode2;
    function decodeStrict(data, options) {
      var _a;
      if (options === void 0) {
        options = EntityLevel.XML;
      }
      var opts = typeof options === "number" ? { level: options } : options;
      (_a = opts.mode) !== null && _a !== void 0 ? _a : opts.mode = decode_js_1.DecodingMode.Strict;
      return decode2(data, opts);
    }
    exports.decodeStrict = decodeStrict;
    function encode2(data, options) {
      if (options === void 0) {
        options = EntityLevel.XML;
      }
      var opts = typeof options === "number" ? { level: options } : options;
      if (opts.mode === EncodingMode.UTF8)
        return (0, escape_js_1.escapeUTF8)(data);
      if (opts.mode === EncodingMode.Attribute)
        return (0, escape_js_1.escapeAttribute)(data);
      if (opts.mode === EncodingMode.Text)
        return (0, escape_js_1.escapeText)(data);
      if (opts.level === EntityLevel.HTML) {
        if (opts.mode === EncodingMode.ASCII) {
          return (0, encode_js_1.encodeNonAsciiHTML)(data);
        }
        return (0, encode_js_1.encodeHTML)(data);
      }
      return (0, escape_js_1.encodeXML)(data);
    }
    exports.encode = encode2;
    var escape_js_2 = /* @__PURE__ */ require_escape();
    Object.defineProperty(exports, "encodeXML", { enumerable: true, get: function() {
      return escape_js_2.encodeXML;
    } });
    Object.defineProperty(exports, "escape", { enumerable: true, get: function() {
      return escape_js_2.escape;
    } });
    Object.defineProperty(exports, "escapeUTF8", { enumerable: true, get: function() {
      return escape_js_2.escapeUTF8;
    } });
    Object.defineProperty(exports, "escapeAttribute", { enumerable: true, get: function() {
      return escape_js_2.escapeAttribute;
    } });
    Object.defineProperty(exports, "escapeText", { enumerable: true, get: function() {
      return escape_js_2.escapeText;
    } });
    var encode_js_2 = /* @__PURE__ */ requireEncode();
    Object.defineProperty(exports, "encodeHTML", { enumerable: true, get: function() {
      return encode_js_2.encodeHTML;
    } });
    Object.defineProperty(exports, "encodeNonAsciiHTML", { enumerable: true, get: function() {
      return encode_js_2.encodeNonAsciiHTML;
    } });
    Object.defineProperty(exports, "encodeHTML4", { enumerable: true, get: function() {
      return encode_js_2.encodeHTML;
    } });
    Object.defineProperty(exports, "encodeHTML5", { enumerable: true, get: function() {
      return encode_js_2.encodeHTML;
    } });
    var decode_js_2 = /* @__PURE__ */ requireDecode();
    Object.defineProperty(exports, "EntityDecoder", { enumerable: true, get: function() {
      return decode_js_2.EntityDecoder;
    } });
    Object.defineProperty(exports, "DecodingMode", { enumerable: true, get: function() {
      return decode_js_2.DecodingMode;
    } });
    Object.defineProperty(exports, "decodeXML", { enumerable: true, get: function() {
      return decode_js_2.decodeXML;
    } });
    Object.defineProperty(exports, "decodeHTML", { enumerable: true, get: function() {
      return decode_js_2.decodeHTML;
    } });
    Object.defineProperty(exports, "decodeHTMLStrict", { enumerable: true, get: function() {
      return decode_js_2.decodeHTMLStrict;
    } });
    Object.defineProperty(exports, "decodeHTMLAttribute", { enumerable: true, get: function() {
      return decode_js_2.decodeHTMLAttribute;
    } });
    Object.defineProperty(exports, "decodeHTML4", { enumerable: true, get: function() {
      return decode_js_2.decodeHTML;
    } });
    Object.defineProperty(exports, "decodeHTML5", { enumerable: true, get: function() {
      return decode_js_2.decodeHTML;
    } });
    Object.defineProperty(exports, "decodeHTML4Strict", { enumerable: true, get: function() {
      return decode_js_2.decodeHTMLStrict;
    } });
    Object.defineProperty(exports, "decodeHTML5Strict", { enumerable: true, get: function() {
      return decode_js_2.decodeHTMLStrict;
    } });
    Object.defineProperty(exports, "decodeXMLStrict", { enumerable: true, get: function() {
      return decode_js_2.decodeXML;
    } });
  })(lib$1);
  return lib$1;
}
var libExports = /* @__PURE__ */ requireLib();
function _class(obj) {
  return Object.prototype.toString.call(obj);
}
function isString$1(obj) {
  return _class(obj) === "[object String]";
}
const _hasOwnProperty = Object.prototype.hasOwnProperty;
function has(object, key) {
  return _hasOwnProperty.call(object, key);
}
function assign(obj) {
  const sources = Array.prototype.slice.call(arguments, 1);
  sources.forEach(function(source) {
    if (!source) {
      return;
    }
    if (typeof source !== "object") {
      throw new TypeError(source + "must be object");
    }
    Object.keys(source).forEach(function(key) {
      obj[key] = source[key];
    });
  });
  return obj;
}
function arrayReplaceAt(src, pos, newElements) {
  return [].concat(src.slice(0, pos), newElements, src.slice(pos + 1));
}
function isValidEntityCode(c2) {
  if (c2 >= 55296 && c2 <= 57343) {
    return false;
  }
  if (c2 >= 64976 && c2 <= 65007) {
    return false;
  }
  if ((c2 & 65535) === 65535 || (c2 & 65535) === 65534) {
    return false;
  }
  if (c2 >= 0 && c2 <= 8) {
    return false;
  }
  if (c2 === 11) {
    return false;
  }
  if (c2 >= 14 && c2 <= 31) {
    return false;
  }
  if (c2 >= 127 && c2 <= 159) {
    return false;
  }
  if (c2 > 1114111) {
    return false;
  }
  return true;
}
function fromCodePoint(c2) {
  if (c2 > 65535) {
    c2 -= 65536;
    const surrogate1 = 55296 + (c2 >> 10);
    const surrogate2 = 56320 + (c2 & 1023);
    return String.fromCharCode(surrogate1, surrogate2);
  }
  return String.fromCharCode(c2);
}
const UNESCAPE_MD_RE = /\\([!"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~])/g;
const ENTITY_RE = /&([a-z#][a-z0-9]{1,31});/gi;
const UNESCAPE_ALL_RE = new RegExp(UNESCAPE_MD_RE.source + "|" + ENTITY_RE.source, "gi");
const DIGITAL_ENTITY_TEST_RE = /^#((?:x[a-f0-9]{1,8}|[0-9]{1,8}))$/i;
function replaceEntityPattern(match, name) {
  if (name.charCodeAt(0) === 35 && DIGITAL_ENTITY_TEST_RE.test(name)) {
    const code2 = name[1].toLowerCase() === "x" ? parseInt(name.slice(2), 16) : parseInt(name.slice(1), 10);
    if (isValidEntityCode(code2)) {
      return fromCodePoint(code2);
    }
    return match;
  }
  const decoded = libExports.decodeHTML(match);
  if (decoded !== match) {
    return decoded;
  }
  return match;
}
function unescapeMd(str) {
  if (str.indexOf("\\") < 0) {
    return str;
  }
  return str.replace(UNESCAPE_MD_RE, "$1");
}
function unescapeAll(str) {
  if (str.indexOf("\\") < 0 && str.indexOf("&") < 0) {
    return str;
  }
  return str.replace(UNESCAPE_ALL_RE, function(match, escaped, entity2) {
    if (escaped) {
      return escaped;
    }
    return replaceEntityPattern(match, entity2);
  });
}
const HTML_ESCAPE_TEST_RE = /[&<>"]/;
const HTML_ESCAPE_REPLACE_RE = /[&<>"]/g;
const HTML_REPLACEMENTS = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;"
};
function replaceUnsafeChar(ch) {
  return HTML_REPLACEMENTS[ch];
}
function escapeHtml(str) {
  if (HTML_ESCAPE_TEST_RE.test(str)) {
    return str.replace(HTML_ESCAPE_REPLACE_RE, replaceUnsafeChar);
  }
  return str;
}
const REGEXP_ESCAPE_RE = /[.?*+^$[\]\\(){}|-]/g;
function escapeRE(str) {
  return str.replace(REGEXP_ESCAPE_RE, "\\$&");
}
function isSpace(code2) {
  switch (code2) {
    case 9:
    case 32:
      return true;
  }
  return false;
}
function isWhiteSpace(code2) {
  if (code2 >= 8192 && code2 <= 8202) {
    return true;
  }
  switch (code2) {
    case 9:
    // \t
    case 10:
    // \n
    case 11:
    // \v
    case 12:
    // \f
    case 13:
    // \r
    case 32:
    case 160:
    case 5760:
    case 8239:
    case 8287:
    case 12288:
      return true;
  }
  return false;
}
function isPunctChar(ch) {
  return index_cjsExports$1.P.test(ch) || index_cjsExports$1.S.test(ch);
}
function isMdAsciiPunct(ch) {
  switch (ch) {
    case 33:
    case 34:
    case 35:
    case 36:
    case 37:
    case 38:
    case 39:
    case 40:
    case 41:
    case 42:
    case 43:
    case 44:
    case 45:
    case 46:
    case 47:
    case 58:
    case 59:
    case 60:
    case 61:
    case 62:
    case 63:
    case 64:
    case 91:
    case 92:
    case 93:
    case 94:
    case 95:
    case 96:
    case 123:
    case 124:
    case 125:
    case 126:
      return true;
    default:
      return false;
  }
}
function normalizeReference(str) {
  str = str.trim().replace(/\s+/g, " ");
  if ("ẞ".toLowerCase() === "Ṿ") {
    str = str.replace(/ẞ/g, "ß");
  }
  return str.toLowerCase().toUpperCase();
}
const lib = { mdurl, ucmicro };
var utils = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  arrayReplaceAt,
  assign,
  escapeHtml,
  escapeRE,
  fromCodePoint,
  has,
  isMdAsciiPunct,
  isPunctChar,
  isSpace,
  isString: isString$1,
  isValidEntityCode,
  isWhiteSpace,
  lib,
  normalizeReference,
  unescapeAll,
  unescapeMd
});
function parseLinkLabel(state, start, disableNested) {
  let level, found, marker, prevPos;
  const max = state.posMax;
  const oldPos = state.pos;
  state.pos = start + 1;
  level = 1;
  while (state.pos < max) {
    marker = state.src.charCodeAt(state.pos);
    if (marker === 93) {
      level--;
      if (level === 0) {
        found = true;
        break;
      }
    }
    prevPos = state.pos;
    state.md.inline.skipToken(state);
    if (marker === 91) {
      if (prevPos === state.pos - 1) {
        level++;
      } else if (disableNested) {
        state.pos = oldPos;
        return -1;
      }
    }
  }
  let labelEnd = -1;
  if (found) {
    labelEnd = state.pos;
  }
  state.pos = oldPos;
  return labelEnd;
}
function parseLinkDestination(str, start, max) {
  let code2;
  let pos = start;
  const result = {
    ok: false,
    pos: 0,
    str: ""
  };
  if (str.charCodeAt(pos) === 60) {
    pos++;
    while (pos < max) {
      code2 = str.charCodeAt(pos);
      if (code2 === 10) {
        return result;
      }
      if (code2 === 60) {
        return result;
      }
      if (code2 === 62) {
        result.pos = pos + 1;
        result.str = unescapeAll(str.slice(start + 1, pos));
        result.ok = true;
        return result;
      }
      if (code2 === 92 && pos + 1 < max) {
        pos += 2;
        continue;
      }
      pos++;
    }
    return result;
  }
  let level = 0;
  while (pos < max) {
    code2 = str.charCodeAt(pos);
    if (code2 === 32) {
      break;
    }
    if (code2 < 32 || code2 === 127) {
      break;
    }
    if (code2 === 92 && pos + 1 < max) {
      if (str.charCodeAt(pos + 1) === 32) {
        break;
      }
      pos += 2;
      continue;
    }
    if (code2 === 40) {
      level++;
      if (level > 32) {
        return result;
      }
    }
    if (code2 === 41) {
      if (level === 0) {
        break;
      }
      level--;
    }
    pos++;
  }
  if (start === pos) {
    return result;
  }
  if (level !== 0) {
    return result;
  }
  result.str = unescapeAll(str.slice(start, pos));
  result.pos = pos;
  result.ok = true;
  return result;
}
function parseLinkTitle(str, start, max, prev_state) {
  let code2;
  let pos = start;
  const state = {
    // if `true`, this is a valid link title
    ok: false,
    // if `true`, this link can be continued on the next line
    can_continue: false,
    // if `ok`, it's the position of the first character after the closing marker
    pos: 0,
    // if `ok`, it's the unescaped title
    str: "",
    // expected closing marker character code
    marker: 0
  };
  if (prev_state) {
    state.str = prev_state.str;
    state.marker = prev_state.marker;
  } else {
    if (pos >= max) {
      return state;
    }
    let marker = str.charCodeAt(pos);
    if (marker !== 34 && marker !== 39 && marker !== 40) {
      return state;
    }
    start++;
    pos++;
    if (marker === 40) {
      marker = 41;
    }
    state.marker = marker;
  }
  while (pos < max) {
    code2 = str.charCodeAt(pos);
    if (code2 === state.marker) {
      state.pos = pos + 1;
      state.str += unescapeAll(str.slice(start, pos));
      state.ok = true;
      return state;
    } else if (code2 === 40 && state.marker === 41) {
      return state;
    } else if (code2 === 92 && pos + 1 < max) {
      pos++;
    }
    pos++;
  }
  state.can_continue = true;
  state.str += unescapeAll(str.slice(start, pos));
  return state;
}
var helpers = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  parseLinkDestination,
  parseLinkLabel,
  parseLinkTitle
});
const default_rules = {};
default_rules.code_inline = function(tokens, idx, options, env, slf) {
  const token = tokens[idx];
  return "<code" + slf.renderAttrs(token) + ">" + escapeHtml(token.content) + "</code>";
};
default_rules.code_block = function(tokens, idx, options, env, slf) {
  const token = tokens[idx];
  return "<pre" + slf.renderAttrs(token) + "><code>" + escapeHtml(tokens[idx].content) + "</code></pre>\n";
};
default_rules.fence = function(tokens, idx, options, env, slf) {
  const token = tokens[idx];
  const info = token.info ? unescapeAll(token.info).trim() : "";
  let langName = "";
  let langAttrs = "";
  if (info) {
    const arr = info.split(/(\s+)/g);
    langName = arr[0];
    langAttrs = arr.slice(2).join("");
  }
  let highlighted;
  if (options.highlight) {
    highlighted = options.highlight(token.content, langName, langAttrs) || escapeHtml(token.content);
  } else {
    highlighted = escapeHtml(token.content);
  }
  if (highlighted.indexOf("<pre") === 0) {
    return highlighted + "\n";
  }
  if (info) {
    const i2 = token.attrIndex("class");
    const tmpAttrs = token.attrs ? token.attrs.slice() : [];
    if (i2 < 0) {
      tmpAttrs.push(["class", options.langPrefix + langName]);
    } else {
      tmpAttrs[i2] = tmpAttrs[i2].slice();
      tmpAttrs[i2][1] += " " + options.langPrefix + langName;
    }
    const tmpToken = {
      attrs: tmpAttrs
    };
    return `<pre><code${slf.renderAttrs(tmpToken)}>${highlighted}</code></pre>
`;
  }
  return `<pre><code${slf.renderAttrs(token)}>${highlighted}</code></pre>
`;
};
default_rules.image = function(tokens, idx, options, env, slf) {
  const token = tokens[idx];
  token.attrs[token.attrIndex("alt")][1] = slf.renderInlineAsText(token.children, options, env);
  return slf.renderToken(tokens, idx, options);
};
default_rules.hardbreak = function(tokens, idx, options) {
  return options.xhtmlOut ? "<br />\n" : "<br>\n";
};
default_rules.softbreak = function(tokens, idx, options) {
  return options.breaks ? options.xhtmlOut ? "<br />\n" : "<br>\n" : "\n";
};
default_rules.text = function(tokens, idx) {
  return escapeHtml(tokens[idx].content);
};
default_rules.html_block = function(tokens, idx) {
  return tokens[idx].content;
};
default_rules.html_inline = function(tokens, idx) {
  return tokens[idx].content;
};
function Renderer() {
  this.rules = assign({}, default_rules);
}
Renderer.prototype.renderAttrs = function renderAttrs(token) {
  let i2, l2, result;
  if (!token.attrs) {
    return "";
  }
  result = "";
  for (i2 = 0, l2 = token.attrs.length; i2 < l2; i2++) {
    result += " " + escapeHtml(token.attrs[i2][0]) + '="' + escapeHtml(token.attrs[i2][1]) + '"';
  }
  return result;
};
Renderer.prototype.renderToken = function renderToken(tokens, idx, options) {
  const token = tokens[idx];
  let result = "";
  if (token.hidden) {
    return "";
  }
  if (token.block && token.nesting !== -1 && idx && tokens[idx - 1].hidden) {
    result += "\n";
  }
  result += (token.nesting === -1 ? "</" : "<") + token.tag;
  result += this.renderAttrs(token);
  if (token.nesting === 0 && options.xhtmlOut) {
    result += " /";
  }
  let needLf = false;
  if (token.block) {
    needLf = true;
    if (token.nesting === 1) {
      if (idx + 1 < tokens.length) {
        const nextToken = tokens[idx + 1];
        if (nextToken.type === "inline" || nextToken.hidden) {
          needLf = false;
        } else if (nextToken.nesting === -1 && nextToken.tag === token.tag) {
          needLf = false;
        }
      }
    }
  }
  result += needLf ? ">\n" : ">";
  return result;
};
Renderer.prototype.renderInline = function(tokens, options, env) {
  let result = "";
  const rules = this.rules;
  for (let i2 = 0, len = tokens.length; i2 < len; i2++) {
    const type = tokens[i2].type;
    if (typeof rules[type] !== "undefined") {
      result += rules[type](tokens, i2, options, env, this);
    } else {
      result += this.renderToken(tokens, i2, options);
    }
  }
  return result;
};
Renderer.prototype.renderInlineAsText = function(tokens, options, env) {
  let result = "";
  for (let i2 = 0, len = tokens.length; i2 < len; i2++) {
    switch (tokens[i2].type) {
      case "text":
        result += tokens[i2].content;
        break;
      case "image":
        result += this.renderInlineAsText(tokens[i2].children, options, env);
        break;
      case "html_inline":
      case "html_block":
        result += tokens[i2].content;
        break;
      case "softbreak":
      case "hardbreak":
        result += "\n";
        break;
    }
  }
  return result;
};
Renderer.prototype.render = function(tokens, options, env) {
  let result = "";
  const rules = this.rules;
  for (let i2 = 0, len = tokens.length; i2 < len; i2++) {
    const type = tokens[i2].type;
    if (type === "inline") {
      result += this.renderInline(tokens[i2].children, options, env);
    } else if (typeof rules[type] !== "undefined") {
      result += rules[type](tokens, i2, options, env, this);
    } else {
      result += this.renderToken(tokens, i2, options, env);
    }
  }
  return result;
};
function Ruler() {
  this.__rules__ = [];
  this.__cache__ = null;
}
Ruler.prototype.__find__ = function(name) {
  for (let i2 = 0; i2 < this.__rules__.length; i2++) {
    if (this.__rules__[i2].name === name) {
      return i2;
    }
  }
  return -1;
};
Ruler.prototype.__compile__ = function() {
  const self2 = this;
  const chains = [""];
  self2.__rules__.forEach(function(rule) {
    if (!rule.enabled) {
      return;
    }
    rule.alt.forEach(function(altName) {
      if (chains.indexOf(altName) < 0) {
        chains.push(altName);
      }
    });
  });
  self2.__cache__ = {};
  chains.forEach(function(chain) {
    self2.__cache__[chain] = [];
    self2.__rules__.forEach(function(rule) {
      if (!rule.enabled) {
        return;
      }
      if (chain && rule.alt.indexOf(chain) < 0) {
        return;
      }
      self2.__cache__[chain].push(rule.fn);
    });
  });
};
Ruler.prototype.at = function(name, fn, options) {
  const index = this.__find__(name);
  const opt = options || {};
  if (index === -1) {
    throw new Error("Parser rule not found: " + name);
  }
  this.__rules__[index].fn = fn;
  this.__rules__[index].alt = opt.alt || [];
  this.__cache__ = null;
};
Ruler.prototype.before = function(beforeName, ruleName, fn, options) {
  const index = this.__find__(beforeName);
  const opt = options || {};
  if (index === -1) {
    throw new Error("Parser rule not found: " + beforeName);
  }
  this.__rules__.splice(index, 0, {
    name: ruleName,
    enabled: true,
    fn,
    alt: opt.alt || []
  });
  this.__cache__ = null;
};
Ruler.prototype.after = function(afterName, ruleName, fn, options) {
  const index = this.__find__(afterName);
  const opt = options || {};
  if (index === -1) {
    throw new Error("Parser rule not found: " + afterName);
  }
  this.__rules__.splice(index + 1, 0, {
    name: ruleName,
    enabled: true,
    fn,
    alt: opt.alt || []
  });
  this.__cache__ = null;
};
Ruler.prototype.push = function(ruleName, fn, options) {
  const opt = options || {};
  this.__rules__.push({
    name: ruleName,
    enabled: true,
    fn,
    alt: opt.alt || []
  });
  this.__cache__ = null;
};
Ruler.prototype.enable = function(list2, ignoreInvalid) {
  if (!Array.isArray(list2)) {
    list2 = [list2];
  }
  const result = [];
  list2.forEach(function(name) {
    const idx = this.__find__(name);
    if (idx < 0) {
      if (ignoreInvalid) {
        return;
      }
      throw new Error("Rules manager: invalid rule name " + name);
    }
    this.__rules__[idx].enabled = true;
    result.push(name);
  }, this);
  this.__cache__ = null;
  return result;
};
Ruler.prototype.enableOnly = function(list2, ignoreInvalid) {
  if (!Array.isArray(list2)) {
    list2 = [list2];
  }
  this.__rules__.forEach(function(rule) {
    rule.enabled = false;
  });
  this.enable(list2, ignoreInvalid);
};
Ruler.prototype.disable = function(list2, ignoreInvalid) {
  if (!Array.isArray(list2)) {
    list2 = [list2];
  }
  const result = [];
  list2.forEach(function(name) {
    const idx = this.__find__(name);
    if (idx < 0) {
      if (ignoreInvalid) {
        return;
      }
      throw new Error("Rules manager: invalid rule name " + name);
    }
    this.__rules__[idx].enabled = false;
    result.push(name);
  }, this);
  this.__cache__ = null;
  return result;
};
Ruler.prototype.getRules = function(chainName) {
  if (this.__cache__ === null) {
    this.__compile__();
  }
  return this.__cache__[chainName] || [];
};
function Token(type, tag, nesting) {
  this.type = type;
  this.tag = tag;
  this.attrs = null;
  this.map = null;
  this.nesting = nesting;
  this.level = 0;
  this.children = null;
  this.content = "";
  this.markup = "";
  this.info = "";
  this.meta = null;
  this.block = false;
  this.hidden = false;
}
Token.prototype.attrIndex = function attrIndex(name) {
  if (!this.attrs) {
    return -1;
  }
  const attrs = this.attrs;
  for (let i2 = 0, len = attrs.length; i2 < len; i2++) {
    if (attrs[i2][0] === name) {
      return i2;
    }
  }
  return -1;
};
Token.prototype.attrPush = function attrPush(attrData) {
  if (this.attrs) {
    this.attrs.push(attrData);
  } else {
    this.attrs = [attrData];
  }
};
Token.prototype.attrSet = function attrSet(name, value) {
  const idx = this.attrIndex(name);
  const attrData = [name, value];
  if (idx < 0) {
    this.attrPush(attrData);
  } else {
    this.attrs[idx] = attrData;
  }
};
Token.prototype.attrGet = function attrGet(name) {
  const idx = this.attrIndex(name);
  let value = null;
  if (idx >= 0) {
    value = this.attrs[idx][1];
  }
  return value;
};
Token.prototype.attrJoin = function attrJoin(name, value) {
  const idx = this.attrIndex(name);
  if (idx < 0) {
    this.attrPush([name, value]);
  } else {
    this.attrs[idx][1] = this.attrs[idx][1] + " " + value;
  }
};
function StateCore(src, md, env) {
  this.src = src;
  this.env = env;
  this.tokens = [];
  this.inlineMode = false;
  this.md = md;
}
StateCore.prototype.Token = Token;
const NEWLINES_RE = /\r\n?|\n/g;
const NULL_RE = /\0/g;
function normalize(state) {
  let str;
  str = state.src.replace(NEWLINES_RE, "\n");
  str = str.replace(NULL_RE, "�");
  state.src = str;
}
function block(state) {
  let token;
  if (state.inlineMode) {
    token = new state.Token("inline", "", 0);
    token.content = state.src;
    token.map = [0, 1];
    token.children = [];
    state.tokens.push(token);
  } else {
    state.md.block.parse(state.src, state.md, state.env, state.tokens);
  }
}
function inline(state) {
  const tokens = state.tokens;
  for (let i2 = 0, l2 = tokens.length; i2 < l2; i2++) {
    const tok = tokens[i2];
    if (tok.type === "inline") {
      state.md.inline.parse(tok.content, state.md, state.env, tok.children);
    }
  }
}
function isLinkOpen$1(str) {
  return /^<a[>\s]/i.test(str);
}
function isLinkClose$1(str) {
  return /^<\/a\s*>/i.test(str);
}
function linkify$1(state) {
  const blockTokens = state.tokens;
  if (!state.md.options.linkify) {
    return;
  }
  for (let j2 = 0, l2 = blockTokens.length; j2 < l2; j2++) {
    if (blockTokens[j2].type !== "inline" || !state.md.linkify.pretest(blockTokens[j2].content)) {
      continue;
    }
    let tokens = blockTokens[j2].children;
    let htmlLinkLevel = 0;
    for (let i2 = tokens.length - 1; i2 >= 0; i2--) {
      const currentToken = tokens[i2];
      if (currentToken.type === "link_close") {
        i2--;
        while (tokens[i2].level !== currentToken.level && tokens[i2].type !== "link_open") {
          i2--;
        }
        continue;
      }
      if (currentToken.type === "html_inline") {
        if (isLinkOpen$1(currentToken.content) && htmlLinkLevel > 0) {
          htmlLinkLevel--;
        }
        if (isLinkClose$1(currentToken.content)) {
          htmlLinkLevel++;
        }
      }
      if (htmlLinkLevel > 0) {
        continue;
      }
      if (currentToken.type === "text" && state.md.linkify.test(currentToken.content)) {
        const text2 = currentToken.content;
        let links = state.md.linkify.match(text2);
        const nodes = [];
        let level = currentToken.level;
        let lastPos = 0;
        if (links.length > 0 && links[0].index === 0 && i2 > 0 && tokens[i2 - 1].type === "text_special") {
          links = links.slice(1);
        }
        for (let ln = 0; ln < links.length; ln++) {
          const url = links[ln].url;
          const fullUrl = state.md.normalizeLink(url);
          if (!state.md.validateLink(fullUrl)) {
            continue;
          }
          let urlText = links[ln].text;
          if (!links[ln].schema) {
            urlText = state.md.normalizeLinkText("http://" + urlText).replace(/^http:\/\//, "");
          } else if (links[ln].schema === "mailto:" && !/^mailto:/i.test(urlText)) {
            urlText = state.md.normalizeLinkText("mailto:" + urlText).replace(/^mailto:/, "");
          } else {
            urlText = state.md.normalizeLinkText(urlText);
          }
          const pos = links[ln].index;
          if (pos > lastPos) {
            const token = new state.Token("text", "", 0);
            token.content = text2.slice(lastPos, pos);
            token.level = level;
            nodes.push(token);
          }
          const token_o = new state.Token("link_open", "a", 1);
          token_o.attrs = [["href", fullUrl]];
          token_o.level = level++;
          token_o.markup = "linkify";
          token_o.info = "auto";
          nodes.push(token_o);
          const token_t = new state.Token("text", "", 0);
          token_t.content = urlText;
          token_t.level = level;
          nodes.push(token_t);
          const token_c = new state.Token("link_close", "a", -1);
          token_c.level = --level;
          token_c.markup = "linkify";
          token_c.info = "auto";
          nodes.push(token_c);
          lastPos = links[ln].lastIndex;
        }
        if (lastPos < text2.length) {
          const token = new state.Token("text", "", 0);
          token.content = text2.slice(lastPos);
          token.level = level;
          nodes.push(token);
        }
        blockTokens[j2].children = tokens = arrayReplaceAt(tokens, i2, nodes);
      }
    }
  }
}
const RARE_RE = /\+-|\.\.|\?\?\?\?|!!!!|,,|--/;
const SCOPED_ABBR_TEST_RE = /\((c|tm|r)\)/i;
const SCOPED_ABBR_RE = /\((c|tm|r)\)/ig;
const SCOPED_ABBR = {
  c: "©",
  r: "®",
  tm: "™"
};
function replaceFn(match, name) {
  return SCOPED_ABBR[name.toLowerCase()];
}
function replace_scoped(inlineTokens) {
  let inside_autolink = 0;
  for (let i2 = inlineTokens.length - 1; i2 >= 0; i2--) {
    const token = inlineTokens[i2];
    if (token.type === "text" && !inside_autolink) {
      token.content = token.content.replace(SCOPED_ABBR_RE, replaceFn);
    }
    if (token.type === "link_open" && token.info === "auto") {
      inside_autolink--;
    }
    if (token.type === "link_close" && token.info === "auto") {
      inside_autolink++;
    }
  }
}
function replace_rare(inlineTokens) {
  let inside_autolink = 0;
  for (let i2 = inlineTokens.length - 1; i2 >= 0; i2--) {
    const token = inlineTokens[i2];
    if (token.type === "text" && !inside_autolink) {
      if (RARE_RE.test(token.content)) {
        token.content = token.content.replace(/\+-/g, "±").replace(/\.{2,}/g, "…").replace(/([?!])…/g, "$1..").replace(/([?!]){4,}/g, "$1$1$1").replace(/,{2,}/g, ",").replace(/(^|[^-])---(?=[^-]|$)/mg, "$1—").replace(/(^|\s)--(?=\s|$)/mg, "$1–").replace(/(^|[^-\s])--(?=[^-\s]|$)/mg, "$1–");
      }
    }
    if (token.type === "link_open" && token.info === "auto") {
      inside_autolink--;
    }
    if (token.type === "link_close" && token.info === "auto") {
      inside_autolink++;
    }
  }
}
function replace(state) {
  let blkIdx;
  if (!state.md.options.typographer) {
    return;
  }
  for (blkIdx = state.tokens.length - 1; blkIdx >= 0; blkIdx--) {
    if (state.tokens[blkIdx].type !== "inline") {
      continue;
    }
    if (SCOPED_ABBR_TEST_RE.test(state.tokens[blkIdx].content)) {
      replace_scoped(state.tokens[blkIdx].children);
    }
    if (RARE_RE.test(state.tokens[blkIdx].content)) {
      replace_rare(state.tokens[blkIdx].children);
    }
  }
}
const QUOTE_TEST_RE = /['"]/;
const QUOTE_RE = /['"]/g;
const APOSTROPHE = "’";
function replaceAt(str, index, ch) {
  return str.slice(0, index) + ch + str.slice(index + 1);
}
function process_inlines(tokens, state) {
  let j2;
  const stack = [];
  for (let i2 = 0; i2 < tokens.length; i2++) {
    const token = tokens[i2];
    const thisLevel = tokens[i2].level;
    for (j2 = stack.length - 1; j2 >= 0; j2--) {
      if (stack[j2].level <= thisLevel) {
        break;
      }
    }
    stack.length = j2 + 1;
    if (token.type !== "text") {
      continue;
    }
    let text2 = token.content;
    let pos = 0;
    let max = text2.length;
    OUTER:
      while (pos < max) {
        QUOTE_RE.lastIndex = pos;
        const t2 = QUOTE_RE.exec(text2);
        if (!t2) {
          break;
        }
        let canOpen = true;
        let canClose = true;
        pos = t2.index + 1;
        const isSingle = t2[0] === "'";
        let lastChar = 32;
        if (t2.index - 1 >= 0) {
          lastChar = text2.charCodeAt(t2.index - 1);
        } else {
          for (j2 = i2 - 1; j2 >= 0; j2--) {
            if (tokens[j2].type === "softbreak" || tokens[j2].type === "hardbreak") break;
            if (!tokens[j2].content) continue;
            lastChar = tokens[j2].content.charCodeAt(tokens[j2].content.length - 1);
            break;
          }
        }
        let nextChar = 32;
        if (pos < max) {
          nextChar = text2.charCodeAt(pos);
        } else {
          for (j2 = i2 + 1; j2 < tokens.length; j2++) {
            if (tokens[j2].type === "softbreak" || tokens[j2].type === "hardbreak") break;
            if (!tokens[j2].content) continue;
            nextChar = tokens[j2].content.charCodeAt(0);
            break;
          }
        }
        const isLastPunctChar = isMdAsciiPunct(lastChar) || isPunctChar(String.fromCharCode(lastChar));
        const isNextPunctChar = isMdAsciiPunct(nextChar) || isPunctChar(String.fromCharCode(nextChar));
        const isLastWhiteSpace = isWhiteSpace(lastChar);
        const isNextWhiteSpace = isWhiteSpace(nextChar);
        if (isNextWhiteSpace) {
          canOpen = false;
        } else if (isNextPunctChar) {
          if (!(isLastWhiteSpace || isLastPunctChar)) {
            canOpen = false;
          }
        }
        if (isLastWhiteSpace) {
          canClose = false;
        } else if (isLastPunctChar) {
          if (!(isNextWhiteSpace || isNextPunctChar)) {
            canClose = false;
          }
        }
        if (nextChar === 34 && t2[0] === '"') {
          if (lastChar >= 48 && lastChar <= 57) {
            canClose = canOpen = false;
          }
        }
        if (canOpen && canClose) {
          canOpen = isLastPunctChar;
          canClose = isNextPunctChar;
        }
        if (!canOpen && !canClose) {
          if (isSingle) {
            token.content = replaceAt(token.content, t2.index, APOSTROPHE);
          }
          continue;
        }
        if (canClose) {
          for (j2 = stack.length - 1; j2 >= 0; j2--) {
            let item = stack[j2];
            if (stack[j2].level < thisLevel) {
              break;
            }
            if (item.single === isSingle && stack[j2].level === thisLevel) {
              item = stack[j2];
              let openQuote;
              let closeQuote;
              if (isSingle) {
                openQuote = state.md.options.quotes[2];
                closeQuote = state.md.options.quotes[3];
              } else {
                openQuote = state.md.options.quotes[0];
                closeQuote = state.md.options.quotes[1];
              }
              token.content = replaceAt(token.content, t2.index, closeQuote);
              tokens[item.token].content = replaceAt(
                tokens[item.token].content,
                item.pos,
                openQuote
              );
              pos += closeQuote.length - 1;
              if (item.token === i2) {
                pos += openQuote.length - 1;
              }
              text2 = token.content;
              max = text2.length;
              stack.length = j2;
              continue OUTER;
            }
          }
        }
        if (canOpen) {
          stack.push({
            token: i2,
            pos: t2.index,
            single: isSingle,
            level: thisLevel
          });
        } else if (canClose && isSingle) {
          token.content = replaceAt(token.content, t2.index, APOSTROPHE);
        }
      }
  }
}
function smartquotes(state) {
  if (!state.md.options.typographer) {
    return;
  }
  for (let blkIdx = state.tokens.length - 1; blkIdx >= 0; blkIdx--) {
    if (state.tokens[blkIdx].type !== "inline" || !QUOTE_TEST_RE.test(state.tokens[blkIdx].content)) {
      continue;
    }
    process_inlines(state.tokens[blkIdx].children, state);
  }
}
function text_join(state) {
  let curr, last;
  const blockTokens = state.tokens;
  const l2 = blockTokens.length;
  for (let j2 = 0; j2 < l2; j2++) {
    if (blockTokens[j2].type !== "inline") continue;
    const tokens = blockTokens[j2].children;
    const max = tokens.length;
    for (curr = 0; curr < max; curr++) {
      if (tokens[curr].type === "text_special") {
        tokens[curr].type = "text";
      }
    }
    for (curr = last = 0; curr < max; curr++) {
      if (tokens[curr].type === "text" && curr + 1 < max && tokens[curr + 1].type === "text") {
        tokens[curr + 1].content = tokens[curr].content + tokens[curr + 1].content;
      } else {
        if (curr !== last) {
          tokens[last] = tokens[curr];
        }
        last++;
      }
    }
    if (curr !== last) {
      tokens.length = last;
    }
  }
}
const _rules$2 = [
  ["normalize", normalize],
  ["block", block],
  ["inline", inline],
  ["linkify", linkify$1],
  ["replacements", replace],
  ["smartquotes", smartquotes],
  // `text_join` finds `text_special` tokens (for escape sequences)
  // and joins them with the rest of the text
  ["text_join", text_join]
];
function Core() {
  this.ruler = new Ruler();
  for (let i2 = 0; i2 < _rules$2.length; i2++) {
    this.ruler.push(_rules$2[i2][0], _rules$2[i2][1]);
  }
}
Core.prototype.process = function(state) {
  const rules = this.ruler.getRules("");
  for (let i2 = 0, l2 = rules.length; i2 < l2; i2++) {
    rules[i2](state);
  }
};
Core.prototype.State = StateCore;
function StateBlock(src, md, env, tokens) {
  this.src = src;
  this.md = md;
  this.env = env;
  this.tokens = tokens;
  this.bMarks = [];
  this.eMarks = [];
  this.tShift = [];
  this.sCount = [];
  this.bsCount = [];
  this.blkIndent = 0;
  this.line = 0;
  this.lineMax = 0;
  this.tight = false;
  this.ddIndent = -1;
  this.listIndent = -1;
  this.parentType = "root";
  this.level = 0;
  const s2 = this.src;
  for (let start = 0, pos = 0, indent = 0, offset = 0, len = s2.length, indent_found = false; pos < len; pos++) {
    const ch = s2.charCodeAt(pos);
    if (!indent_found) {
      if (isSpace(ch)) {
        indent++;
        if (ch === 9) {
          offset += 4 - offset % 4;
        } else {
          offset++;
        }
        continue;
      } else {
        indent_found = true;
      }
    }
    if (ch === 10 || pos === len - 1) {
      if (ch !== 10) {
        pos++;
      }
      this.bMarks.push(start);
      this.eMarks.push(pos);
      this.tShift.push(indent);
      this.sCount.push(offset);
      this.bsCount.push(0);
      indent_found = false;
      indent = 0;
      offset = 0;
      start = pos + 1;
    }
  }
  this.bMarks.push(s2.length);
  this.eMarks.push(s2.length);
  this.tShift.push(0);
  this.sCount.push(0);
  this.bsCount.push(0);
  this.lineMax = this.bMarks.length - 1;
}
StateBlock.prototype.push = function(type, tag, nesting) {
  const token = new Token(type, tag, nesting);
  token.block = true;
  if (nesting < 0) this.level--;
  token.level = this.level;
  if (nesting > 0) this.level++;
  this.tokens.push(token);
  return token;
};
StateBlock.prototype.isEmpty = function isEmpty(line) {
  return this.bMarks[line] + this.tShift[line] >= this.eMarks[line];
};
StateBlock.prototype.skipEmptyLines = function skipEmptyLines(from) {
  for (let max = this.lineMax; from < max; from++) {
    if (this.bMarks[from] + this.tShift[from] < this.eMarks[from]) {
      break;
    }
  }
  return from;
};
StateBlock.prototype.skipSpaces = function skipSpaces(pos) {
  for (let max = this.src.length; pos < max; pos++) {
    const ch = this.src.charCodeAt(pos);
    if (!isSpace(ch)) {
      break;
    }
  }
  return pos;
};
StateBlock.prototype.skipSpacesBack = function skipSpacesBack(pos, min) {
  if (pos <= min) {
    return pos;
  }
  while (pos > min) {
    if (!isSpace(this.src.charCodeAt(--pos))) {
      return pos + 1;
    }
  }
  return pos;
};
StateBlock.prototype.skipChars = function skipChars(pos, code2) {
  for (let max = this.src.length; pos < max; pos++) {
    if (this.src.charCodeAt(pos) !== code2) {
      break;
    }
  }
  return pos;
};
StateBlock.prototype.skipCharsBack = function skipCharsBack(pos, code2, min) {
  if (pos <= min) {
    return pos;
  }
  while (pos > min) {
    if (code2 !== this.src.charCodeAt(--pos)) {
      return pos + 1;
    }
  }
  return pos;
};
StateBlock.prototype.getLines = function getLines(begin, end, indent, keepLastLF) {
  if (begin >= end) {
    return "";
  }
  const queue = new Array(end - begin);
  for (let i2 = 0, line = begin; line < end; line++, i2++) {
    let lineIndent = 0;
    const lineStart = this.bMarks[line];
    let first = lineStart;
    let last;
    if (line + 1 < end || keepLastLF) {
      last = this.eMarks[line] + 1;
    } else {
      last = this.eMarks[line];
    }
    while (first < last && lineIndent < indent) {
      const ch = this.src.charCodeAt(first);
      if (isSpace(ch)) {
        if (ch === 9) {
          lineIndent += 4 - (lineIndent + this.bsCount[line]) % 4;
        } else {
          lineIndent++;
        }
      } else if (first - lineStart < this.tShift[line]) {
        lineIndent++;
      } else {
        break;
      }
      first++;
    }
    if (lineIndent > indent) {
      queue[i2] = new Array(lineIndent - indent + 1).join(" ") + this.src.slice(first, last);
    } else {
      queue[i2] = this.src.slice(first, last);
    }
  }
  return queue.join("");
};
StateBlock.prototype.Token = Token;
const MAX_AUTOCOMPLETED_CELLS = 65536;
function getLine(state, line) {
  const pos = state.bMarks[line] + state.tShift[line];
  const max = state.eMarks[line];
  return state.src.slice(pos, max);
}
function escapedSplit(str) {
  const result = [];
  const max = str.length;
  let pos = 0;
  let ch = str.charCodeAt(pos);
  let isEscaped = false;
  let lastPos = 0;
  let current = "";
  while (pos < max) {
    if (ch === 124) {
      if (!isEscaped) {
        result.push(current + str.substring(lastPos, pos));
        current = "";
        lastPos = pos + 1;
      } else {
        current += str.substring(lastPos, pos - 1);
        lastPos = pos;
      }
    }
    isEscaped = ch === 92;
    pos++;
    ch = str.charCodeAt(pos);
  }
  result.push(current + str.substring(lastPos));
  return result;
}
function table(state, startLine, endLine, silent) {
  if (startLine + 2 > endLine) {
    return false;
  }
  let nextLine = startLine + 1;
  if (state.sCount[nextLine] < state.blkIndent) {
    return false;
  }
  if (state.sCount[nextLine] - state.blkIndent >= 4) {
    return false;
  }
  let pos = state.bMarks[nextLine] + state.tShift[nextLine];
  if (pos >= state.eMarks[nextLine]) {
    return false;
  }
  const firstCh = state.src.charCodeAt(pos++);
  if (firstCh !== 124 && firstCh !== 45 && firstCh !== 58) {
    return false;
  }
  if (pos >= state.eMarks[nextLine]) {
    return false;
  }
  const secondCh = state.src.charCodeAt(pos++);
  if (secondCh !== 124 && secondCh !== 45 && secondCh !== 58 && !isSpace(secondCh)) {
    return false;
  }
  if (firstCh === 45 && isSpace(secondCh)) {
    return false;
  }
  while (pos < state.eMarks[nextLine]) {
    const ch = state.src.charCodeAt(pos);
    if (ch !== 124 && ch !== 45 && ch !== 58 && !isSpace(ch)) {
      return false;
    }
    pos++;
  }
  let lineText = getLine(state, startLine + 1);
  let columns = lineText.split("|");
  const aligns = [];
  for (let i2 = 0; i2 < columns.length; i2++) {
    const t2 = columns[i2].trim();
    if (!t2) {
      if (i2 === 0 || i2 === columns.length - 1) {
        continue;
      } else {
        return false;
      }
    }
    if (!/^:?-+:?$/.test(t2)) {
      return false;
    }
    if (t2.charCodeAt(t2.length - 1) === 58) {
      aligns.push(t2.charCodeAt(0) === 58 ? "center" : "right");
    } else if (t2.charCodeAt(0) === 58) {
      aligns.push("left");
    } else {
      aligns.push("");
    }
  }
  lineText = getLine(state, startLine).trim();
  if (lineText.indexOf("|") === -1) {
    return false;
  }
  if (state.sCount[startLine] - state.blkIndent >= 4) {
    return false;
  }
  columns = escapedSplit(lineText);
  if (columns.length && columns[0] === "") columns.shift();
  if (columns.length && columns[columns.length - 1] === "") columns.pop();
  const columnCount = columns.length;
  if (columnCount === 0 || columnCount !== aligns.length) {
    return false;
  }
  if (silent) {
    return true;
  }
  const oldParentType = state.parentType;
  state.parentType = "table";
  const terminatorRules = state.md.block.ruler.getRules("blockquote");
  const token_to = state.push("table_open", "table", 1);
  const tableLines = [startLine, 0];
  token_to.map = tableLines;
  const token_tho = state.push("thead_open", "thead", 1);
  token_tho.map = [startLine, startLine + 1];
  const token_htro = state.push("tr_open", "tr", 1);
  token_htro.map = [startLine, startLine + 1];
  for (let i2 = 0; i2 < columns.length; i2++) {
    const token_ho = state.push("th_open", "th", 1);
    if (aligns[i2]) {
      token_ho.attrs = [["style", "text-align:" + aligns[i2]]];
    }
    const token_il = state.push("inline", "", 0);
    token_il.content = columns[i2].trim();
    token_il.children = [];
    state.push("th_close", "th", -1);
  }
  state.push("tr_close", "tr", -1);
  state.push("thead_close", "thead", -1);
  let tbodyLines;
  let autocompletedCells = 0;
  for (nextLine = startLine + 2; nextLine < endLine; nextLine++) {
    if (state.sCount[nextLine] < state.blkIndent) {
      break;
    }
    let terminate = false;
    for (let i2 = 0, l2 = terminatorRules.length; i2 < l2; i2++) {
      if (terminatorRules[i2](state, nextLine, endLine, true)) {
        terminate = true;
        break;
      }
    }
    if (terminate) {
      break;
    }
    lineText = getLine(state, nextLine).trim();
    if (!lineText) {
      break;
    }
    if (state.sCount[nextLine] - state.blkIndent >= 4) {
      break;
    }
    columns = escapedSplit(lineText);
    if (columns.length && columns[0] === "") columns.shift();
    if (columns.length && columns[columns.length - 1] === "") columns.pop();
    autocompletedCells += columnCount - columns.length;
    if (autocompletedCells > MAX_AUTOCOMPLETED_CELLS) {
      break;
    }
    if (nextLine === startLine + 2) {
      const token_tbo = state.push("tbody_open", "tbody", 1);
      token_tbo.map = tbodyLines = [startLine + 2, 0];
    }
    const token_tro = state.push("tr_open", "tr", 1);
    token_tro.map = [nextLine, nextLine + 1];
    for (let i2 = 0; i2 < columnCount; i2++) {
      const token_tdo = state.push("td_open", "td", 1);
      if (aligns[i2]) {
        token_tdo.attrs = [["style", "text-align:" + aligns[i2]]];
      }
      const token_il = state.push("inline", "", 0);
      token_il.content = columns[i2] ? columns[i2].trim() : "";
      token_il.children = [];
      state.push("td_close", "td", -1);
    }
    state.push("tr_close", "tr", -1);
  }
  if (tbodyLines) {
    state.push("tbody_close", "tbody", -1);
    tbodyLines[1] = nextLine;
  }
  state.push("table_close", "table", -1);
  tableLines[1] = nextLine;
  state.parentType = oldParentType;
  state.line = nextLine;
  return true;
}
function code(state, startLine, endLine) {
  if (state.sCount[startLine] - state.blkIndent < 4) {
    return false;
  }
  let nextLine = startLine + 1;
  let last = nextLine;
  while (nextLine < endLine) {
    if (state.isEmpty(nextLine)) {
      nextLine++;
      continue;
    }
    if (state.sCount[nextLine] - state.blkIndent >= 4) {
      nextLine++;
      last = nextLine;
      continue;
    }
    break;
  }
  state.line = last;
  const token = state.push("code_block", "code", 0);
  token.content = state.getLines(startLine, last, 4 + state.blkIndent, false) + "\n";
  token.map = [startLine, state.line];
  return true;
}
function fence(state, startLine, endLine, silent) {
  let pos = state.bMarks[startLine] + state.tShift[startLine];
  let max = state.eMarks[startLine];
  if (state.sCount[startLine] - state.blkIndent >= 4) {
    return false;
  }
  if (pos + 3 > max) {
    return false;
  }
  const marker = state.src.charCodeAt(pos);
  if (marker !== 126 && marker !== 96) {
    return false;
  }
  let mem = pos;
  pos = state.skipChars(pos, marker);
  let len = pos - mem;
  if (len < 3) {
    return false;
  }
  const markup = state.src.slice(mem, pos);
  const params = state.src.slice(pos, max);
  if (marker === 96) {
    if (params.indexOf(String.fromCharCode(marker)) >= 0) {
      return false;
    }
  }
  if (silent) {
    return true;
  }
  let nextLine = startLine;
  let haveEndMarker = false;
  for (; ; ) {
    nextLine++;
    if (nextLine >= endLine) {
      break;
    }
    pos = mem = state.bMarks[nextLine] + state.tShift[nextLine];
    max = state.eMarks[nextLine];
    if (pos < max && state.sCount[nextLine] < state.blkIndent) {
      break;
    }
    if (state.src.charCodeAt(pos) !== marker) {
      continue;
    }
    if (state.sCount[nextLine] - state.blkIndent >= 4) {
      continue;
    }
    pos = state.skipChars(pos, marker);
    if (pos - mem < len) {
      continue;
    }
    pos = state.skipSpaces(pos);
    if (pos < max) {
      continue;
    }
    haveEndMarker = true;
    break;
  }
  len = state.sCount[startLine];
  state.line = nextLine + (haveEndMarker ? 1 : 0);
  const token = state.push("fence", "code", 0);
  token.info = params;
  token.content = state.getLines(startLine + 1, nextLine, len, true);
  token.markup = markup;
  token.map = [startLine, state.line];
  return true;
}
function blockquote(state, startLine, endLine, silent) {
  let pos = state.bMarks[startLine] + state.tShift[startLine];
  let max = state.eMarks[startLine];
  const oldLineMax = state.lineMax;
  if (state.sCount[startLine] - state.blkIndent >= 4) {
    return false;
  }
  if (state.src.charCodeAt(pos) !== 62) {
    return false;
  }
  if (silent) {
    return true;
  }
  const oldBMarks = [];
  const oldBSCount = [];
  const oldSCount = [];
  const oldTShift = [];
  const terminatorRules = state.md.block.ruler.getRules("blockquote");
  const oldParentType = state.parentType;
  state.parentType = "blockquote";
  let lastLineEmpty = false;
  let nextLine;
  for (nextLine = startLine; nextLine < endLine; nextLine++) {
    const isOutdented = state.sCount[nextLine] < state.blkIndent;
    pos = state.bMarks[nextLine] + state.tShift[nextLine];
    max = state.eMarks[nextLine];
    if (pos >= max) {
      break;
    }
    if (state.src.charCodeAt(pos++) === 62 && !isOutdented) {
      let initial = state.sCount[nextLine] + 1;
      let spaceAfterMarker;
      let adjustTab;
      if (state.src.charCodeAt(pos) === 32) {
        pos++;
        initial++;
        adjustTab = false;
        spaceAfterMarker = true;
      } else if (state.src.charCodeAt(pos) === 9) {
        spaceAfterMarker = true;
        if ((state.bsCount[nextLine] + initial) % 4 === 3) {
          pos++;
          initial++;
          adjustTab = false;
        } else {
          adjustTab = true;
        }
      } else {
        spaceAfterMarker = false;
      }
      let offset = initial;
      oldBMarks.push(state.bMarks[nextLine]);
      state.bMarks[nextLine] = pos;
      while (pos < max) {
        const ch = state.src.charCodeAt(pos);
        if (isSpace(ch)) {
          if (ch === 9) {
            offset += 4 - (offset + state.bsCount[nextLine] + (adjustTab ? 1 : 0)) % 4;
          } else {
            offset++;
          }
        } else {
          break;
        }
        pos++;
      }
      lastLineEmpty = pos >= max;
      oldBSCount.push(state.bsCount[nextLine]);
      state.bsCount[nextLine] = state.sCount[nextLine] + 1 + (spaceAfterMarker ? 1 : 0);
      oldSCount.push(state.sCount[nextLine]);
      state.sCount[nextLine] = offset - initial;
      oldTShift.push(state.tShift[nextLine]);
      state.tShift[nextLine] = pos - state.bMarks[nextLine];
      continue;
    }
    if (lastLineEmpty) {
      break;
    }
    let terminate = false;
    for (let i2 = 0, l2 = terminatorRules.length; i2 < l2; i2++) {
      if (terminatorRules[i2](state, nextLine, endLine, true)) {
        terminate = true;
        break;
      }
    }
    if (terminate) {
      state.lineMax = nextLine;
      if (state.blkIndent !== 0) {
        oldBMarks.push(state.bMarks[nextLine]);
        oldBSCount.push(state.bsCount[nextLine]);
        oldTShift.push(state.tShift[nextLine]);
        oldSCount.push(state.sCount[nextLine]);
        state.sCount[nextLine] -= state.blkIndent;
      }
      break;
    }
    oldBMarks.push(state.bMarks[nextLine]);
    oldBSCount.push(state.bsCount[nextLine]);
    oldTShift.push(state.tShift[nextLine]);
    oldSCount.push(state.sCount[nextLine]);
    state.sCount[nextLine] = -1;
  }
  const oldIndent = state.blkIndent;
  state.blkIndent = 0;
  const token_o = state.push("blockquote_open", "blockquote", 1);
  token_o.markup = ">";
  const lines = [startLine, 0];
  token_o.map = lines;
  state.md.block.tokenize(state, startLine, nextLine);
  const token_c = state.push("blockquote_close", "blockquote", -1);
  token_c.markup = ">";
  state.lineMax = oldLineMax;
  state.parentType = oldParentType;
  lines[1] = state.line;
  for (let i2 = 0; i2 < oldTShift.length; i2++) {
    state.bMarks[i2 + startLine] = oldBMarks[i2];
    state.tShift[i2 + startLine] = oldTShift[i2];
    state.sCount[i2 + startLine] = oldSCount[i2];
    state.bsCount[i2 + startLine] = oldBSCount[i2];
  }
  state.blkIndent = oldIndent;
  return true;
}
function hr(state, startLine, endLine, silent) {
  const max = state.eMarks[startLine];
  if (state.sCount[startLine] - state.blkIndent >= 4) {
    return false;
  }
  let pos = state.bMarks[startLine] + state.tShift[startLine];
  const marker = state.src.charCodeAt(pos++);
  if (marker !== 42 && marker !== 45 && marker !== 95) {
    return false;
  }
  let cnt = 1;
  while (pos < max) {
    const ch = state.src.charCodeAt(pos++);
    if (ch !== marker && !isSpace(ch)) {
      return false;
    }
    if (ch === marker) {
      cnt++;
    }
  }
  if (cnt < 3) {
    return false;
  }
  if (silent) {
    return true;
  }
  state.line = startLine + 1;
  const token = state.push("hr", "hr", 0);
  token.map = [startLine, state.line];
  token.markup = Array(cnt + 1).join(String.fromCharCode(marker));
  return true;
}
function skipBulletListMarker(state, startLine) {
  const max = state.eMarks[startLine];
  let pos = state.bMarks[startLine] + state.tShift[startLine];
  const marker = state.src.charCodeAt(pos++);
  if (marker !== 42 && marker !== 45 && marker !== 43) {
    return -1;
  }
  if (pos < max) {
    const ch = state.src.charCodeAt(pos);
    if (!isSpace(ch)) {
      return -1;
    }
  }
  return pos;
}
function skipOrderedListMarker(state, startLine) {
  const start = state.bMarks[startLine] + state.tShift[startLine];
  const max = state.eMarks[startLine];
  let pos = start;
  if (pos + 1 >= max) {
    return -1;
  }
  let ch = state.src.charCodeAt(pos++);
  if (ch < 48 || ch > 57) {
    return -1;
  }
  for (; ; ) {
    if (pos >= max) {
      return -1;
    }
    ch = state.src.charCodeAt(pos++);
    if (ch >= 48 && ch <= 57) {
      if (pos - start >= 10) {
        return -1;
      }
      continue;
    }
    if (ch === 41 || ch === 46) {
      break;
    }
    return -1;
  }
  if (pos < max) {
    ch = state.src.charCodeAt(pos);
    if (!isSpace(ch)) {
      return -1;
    }
  }
  return pos;
}
function markTightParagraphs(state, idx) {
  const level = state.level + 2;
  for (let i2 = idx + 2, l2 = state.tokens.length - 2; i2 < l2; i2++) {
    if (state.tokens[i2].level === level && state.tokens[i2].type === "paragraph_open") {
      state.tokens[i2 + 2].hidden = true;
      state.tokens[i2].hidden = true;
      i2 += 2;
    }
  }
}
function list(state, startLine, endLine, silent) {
  let max, pos, start, token;
  let nextLine = startLine;
  let tight = true;
  if (state.sCount[nextLine] - state.blkIndent >= 4) {
    return false;
  }
  if (state.listIndent >= 0 && state.sCount[nextLine] - state.listIndent >= 4 && state.sCount[nextLine] < state.blkIndent) {
    return false;
  }
  let isTerminatingParagraph = false;
  if (silent && state.parentType === "paragraph") {
    if (state.sCount[nextLine] >= state.blkIndent) {
      isTerminatingParagraph = true;
    }
  }
  let isOrdered;
  let markerValue;
  let posAfterMarker;
  if ((posAfterMarker = skipOrderedListMarker(state, nextLine)) >= 0) {
    isOrdered = true;
    start = state.bMarks[nextLine] + state.tShift[nextLine];
    markerValue = Number(state.src.slice(start, posAfterMarker - 1));
    if (isTerminatingParagraph && markerValue !== 1) return false;
  } else if ((posAfterMarker = skipBulletListMarker(state, nextLine)) >= 0) {
    isOrdered = false;
  } else {
    return false;
  }
  if (isTerminatingParagraph) {
    if (state.skipSpaces(posAfterMarker) >= state.eMarks[nextLine]) return false;
  }
  if (silent) {
    return true;
  }
  const markerCharCode = state.src.charCodeAt(posAfterMarker - 1);
  const listTokIdx = state.tokens.length;
  if (isOrdered) {
    token = state.push("ordered_list_open", "ol", 1);
    if (markerValue !== 1) {
      token.attrs = [["start", markerValue]];
    }
  } else {
    token = state.push("bullet_list_open", "ul", 1);
  }
  const listLines = [nextLine, 0];
  token.map = listLines;
  token.markup = String.fromCharCode(markerCharCode);
  let prevEmptyEnd = false;
  const terminatorRules = state.md.block.ruler.getRules("list");
  const oldParentType = state.parentType;
  state.parentType = "list";
  while (nextLine < endLine) {
    pos = posAfterMarker;
    max = state.eMarks[nextLine];
    const initial = state.sCount[nextLine] + posAfterMarker - (state.bMarks[nextLine] + state.tShift[nextLine]);
    let offset = initial;
    while (pos < max) {
      const ch = state.src.charCodeAt(pos);
      if (ch === 9) {
        offset += 4 - (offset + state.bsCount[nextLine]) % 4;
      } else if (ch === 32) {
        offset++;
      } else {
        break;
      }
      pos++;
    }
    const contentStart = pos;
    let indentAfterMarker;
    if (contentStart >= max) {
      indentAfterMarker = 1;
    } else {
      indentAfterMarker = offset - initial;
    }
    if (indentAfterMarker > 4) {
      indentAfterMarker = 1;
    }
    const indent = initial + indentAfterMarker;
    token = state.push("list_item_open", "li", 1);
    token.markup = String.fromCharCode(markerCharCode);
    const itemLines = [nextLine, 0];
    token.map = itemLines;
    if (isOrdered) {
      token.info = state.src.slice(start, posAfterMarker - 1);
    }
    const oldTight = state.tight;
    const oldTShift = state.tShift[nextLine];
    const oldSCount = state.sCount[nextLine];
    const oldListIndent = state.listIndent;
    state.listIndent = state.blkIndent;
    state.blkIndent = indent;
    state.tight = true;
    state.tShift[nextLine] = contentStart - state.bMarks[nextLine];
    state.sCount[nextLine] = offset;
    if (contentStart >= max && state.isEmpty(nextLine + 1)) {
      state.line = Math.min(state.line + 2, endLine);
    } else {
      state.md.block.tokenize(state, nextLine, endLine, true);
    }
    if (!state.tight || prevEmptyEnd) {
      tight = false;
    }
    prevEmptyEnd = state.line - nextLine > 1 && state.isEmpty(state.line - 1);
    state.blkIndent = state.listIndent;
    state.listIndent = oldListIndent;
    state.tShift[nextLine] = oldTShift;
    state.sCount[nextLine] = oldSCount;
    state.tight = oldTight;
    token = state.push("list_item_close", "li", -1);
    token.markup = String.fromCharCode(markerCharCode);
    nextLine = state.line;
    itemLines[1] = nextLine;
    if (nextLine >= endLine) {
      break;
    }
    if (state.sCount[nextLine] < state.blkIndent) {
      break;
    }
    if (state.sCount[nextLine] - state.blkIndent >= 4) {
      break;
    }
    let terminate = false;
    for (let i2 = 0, l2 = terminatorRules.length; i2 < l2; i2++) {
      if (terminatorRules[i2](state, nextLine, endLine, true)) {
        terminate = true;
        break;
      }
    }
    if (terminate) {
      break;
    }
    if (isOrdered) {
      posAfterMarker = skipOrderedListMarker(state, nextLine);
      if (posAfterMarker < 0) {
        break;
      }
      start = state.bMarks[nextLine] + state.tShift[nextLine];
    } else {
      posAfterMarker = skipBulletListMarker(state, nextLine);
      if (posAfterMarker < 0) {
        break;
      }
    }
    if (markerCharCode !== state.src.charCodeAt(posAfterMarker - 1)) {
      break;
    }
  }
  if (isOrdered) {
    token = state.push("ordered_list_close", "ol", -1);
  } else {
    token = state.push("bullet_list_close", "ul", -1);
  }
  token.markup = String.fromCharCode(markerCharCode);
  listLines[1] = nextLine;
  state.line = nextLine;
  state.parentType = oldParentType;
  if (tight) {
    markTightParagraphs(state, listTokIdx);
  }
  return true;
}
function reference(state, startLine, _endLine, silent) {
  let pos = state.bMarks[startLine] + state.tShift[startLine];
  let max = state.eMarks[startLine];
  let nextLine = startLine + 1;
  if (state.sCount[startLine] - state.blkIndent >= 4) {
    return false;
  }
  if (state.src.charCodeAt(pos) !== 91) {
    return false;
  }
  function getNextLine(nextLine2) {
    const endLine = state.lineMax;
    if (nextLine2 >= endLine || state.isEmpty(nextLine2)) {
      return null;
    }
    let isContinuation = false;
    if (state.sCount[nextLine2] - state.blkIndent > 3) {
      isContinuation = true;
    }
    if (state.sCount[nextLine2] < 0) {
      isContinuation = true;
    }
    if (!isContinuation) {
      const terminatorRules = state.md.block.ruler.getRules("reference");
      const oldParentType = state.parentType;
      state.parentType = "reference";
      let terminate = false;
      for (let i2 = 0, l2 = terminatorRules.length; i2 < l2; i2++) {
        if (terminatorRules[i2](state, nextLine2, endLine, true)) {
          terminate = true;
          break;
        }
      }
      state.parentType = oldParentType;
      if (terminate) {
        return null;
      }
    }
    const pos2 = state.bMarks[nextLine2] + state.tShift[nextLine2];
    const max2 = state.eMarks[nextLine2];
    return state.src.slice(pos2, max2 + 1);
  }
  let str = state.src.slice(pos, max + 1);
  max = str.length;
  let labelEnd = -1;
  for (pos = 1; pos < max; pos++) {
    const ch = str.charCodeAt(pos);
    if (ch === 91) {
      return false;
    } else if (ch === 93) {
      labelEnd = pos;
      break;
    } else if (ch === 10) {
      const lineContent = getNextLine(nextLine);
      if (lineContent !== null) {
        str += lineContent;
        max = str.length;
        nextLine++;
      }
    } else if (ch === 92) {
      pos++;
      if (pos < max && str.charCodeAt(pos) === 10) {
        const lineContent = getNextLine(nextLine);
        if (lineContent !== null) {
          str += lineContent;
          max = str.length;
          nextLine++;
        }
      }
    }
  }
  if (labelEnd < 0 || str.charCodeAt(labelEnd + 1) !== 58) {
    return false;
  }
  for (pos = labelEnd + 2; pos < max; pos++) {
    const ch = str.charCodeAt(pos);
    if (ch === 10) {
      const lineContent = getNextLine(nextLine);
      if (lineContent !== null) {
        str += lineContent;
        max = str.length;
        nextLine++;
      }
    } else if (isSpace(ch)) ;
    else {
      break;
    }
  }
  const destRes = state.md.helpers.parseLinkDestination(str, pos, max);
  if (!destRes.ok) {
    return false;
  }
  const href = state.md.normalizeLink(destRes.str);
  if (!state.md.validateLink(href)) {
    return false;
  }
  pos = destRes.pos;
  const destEndPos = pos;
  const destEndLineNo = nextLine;
  const start = pos;
  for (; pos < max; pos++) {
    const ch = str.charCodeAt(pos);
    if (ch === 10) {
      const lineContent = getNextLine(nextLine);
      if (lineContent !== null) {
        str += lineContent;
        max = str.length;
        nextLine++;
      }
    } else if (isSpace(ch)) ;
    else {
      break;
    }
  }
  let titleRes = state.md.helpers.parseLinkTitle(str, pos, max);
  while (titleRes.can_continue) {
    const lineContent = getNextLine(nextLine);
    if (lineContent === null) break;
    str += lineContent;
    pos = max;
    max = str.length;
    nextLine++;
    titleRes = state.md.helpers.parseLinkTitle(str, pos, max, titleRes);
  }
  let title;
  if (pos < max && start !== pos && titleRes.ok) {
    title = titleRes.str;
    pos = titleRes.pos;
  } else {
    title = "";
    pos = destEndPos;
    nextLine = destEndLineNo;
  }
  while (pos < max) {
    const ch = str.charCodeAt(pos);
    if (!isSpace(ch)) {
      break;
    }
    pos++;
  }
  if (pos < max && str.charCodeAt(pos) !== 10) {
    if (title) {
      title = "";
      pos = destEndPos;
      nextLine = destEndLineNo;
      while (pos < max) {
        const ch = str.charCodeAt(pos);
        if (!isSpace(ch)) {
          break;
        }
        pos++;
      }
    }
  }
  if (pos < max && str.charCodeAt(pos) !== 10) {
    return false;
  }
  const label = normalizeReference(str.slice(1, labelEnd));
  if (!label) {
    return false;
  }
  if (silent) {
    return true;
  }
  if (typeof state.env.references === "undefined") {
    state.env.references = {};
  }
  if (typeof state.env.references[label] === "undefined") {
    state.env.references[label] = { title, href };
  }
  state.line = nextLine;
  return true;
}
var block_names = [
  "address",
  "article",
  "aside",
  "base",
  "basefont",
  "blockquote",
  "body",
  "caption",
  "center",
  "col",
  "colgroup",
  "dd",
  "details",
  "dialog",
  "dir",
  "div",
  "dl",
  "dt",
  "fieldset",
  "figcaption",
  "figure",
  "footer",
  "form",
  "frame",
  "frameset",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "head",
  "header",
  "hr",
  "html",
  "iframe",
  "legend",
  "li",
  "link",
  "main",
  "menu",
  "menuitem",
  "nav",
  "noframes",
  "ol",
  "optgroup",
  "option",
  "p",
  "param",
  "search",
  "section",
  "summary",
  "table",
  "tbody",
  "td",
  "tfoot",
  "th",
  "thead",
  "title",
  "tr",
  "track",
  "ul"
];
const attr_name = "[a-zA-Z_:][a-zA-Z0-9:._-]*";
const unquoted = "[^\"'=<>`\\x00-\\x20]+";
const single_quoted = "'[^']*'";
const double_quoted = '"[^"]*"';
const attr_value = "(?:" + unquoted + "|" + single_quoted + "|" + double_quoted + ")";
const attribute = "(?:\\s+" + attr_name + "(?:\\s*=\\s*" + attr_value + ")?)";
const open_tag = "<[A-Za-z][A-Za-z0-9\\-]*" + attribute + "*\\s*\\/?>";
const close_tag = "<\\/[A-Za-z][A-Za-z0-9\\-]*\\s*>";
const comment = "<!---?>|<!--(?:[^-]|-[^-]|--[^>])*-->";
const processing = "<[?][\\s\\S]*?[?]>";
const declaration = "<![A-Za-z][^>]*>";
const cdata = "<!\\[CDATA\\[[\\s\\S]*?\\]\\]>";
const HTML_TAG_RE = new RegExp("^(?:" + open_tag + "|" + close_tag + "|" + comment + "|" + processing + "|" + declaration + "|" + cdata + ")");
const HTML_OPEN_CLOSE_TAG_RE = new RegExp("^(?:" + open_tag + "|" + close_tag + ")");
const HTML_SEQUENCES = [
  [/^<(script|pre|style|textarea)(?=(\s|>|$))/i, /<\/(script|pre|style|textarea)>/i, true],
  [/^<!--/, /-->/, true],
  [/^<\?/, /\?>/, true],
  [/^<![A-Z]/, />/, true],
  [/^<!\[CDATA\[/, /\]\]>/, true],
  [new RegExp("^</?(" + block_names.join("|") + ")(?=(\\s|/?>|$))", "i"), /^$/, true],
  [new RegExp(HTML_OPEN_CLOSE_TAG_RE.source + "\\s*$"), /^$/, false]
];
function html_block(state, startLine, endLine, silent) {
  let pos = state.bMarks[startLine] + state.tShift[startLine];
  let max = state.eMarks[startLine];
  if (state.sCount[startLine] - state.blkIndent >= 4) {
    return false;
  }
  if (!state.md.options.html) {
    return false;
  }
  if (state.src.charCodeAt(pos) !== 60) {
    return false;
  }
  let lineText = state.src.slice(pos, max);
  let i2 = 0;
  for (; i2 < HTML_SEQUENCES.length; i2++) {
    if (HTML_SEQUENCES[i2][0].test(lineText)) {
      break;
    }
  }
  if (i2 === HTML_SEQUENCES.length) {
    return false;
  }
  if (silent) {
    return HTML_SEQUENCES[i2][2];
  }
  let nextLine = startLine + 1;
  if (!HTML_SEQUENCES[i2][1].test(lineText)) {
    for (; nextLine < endLine; nextLine++) {
      if (state.sCount[nextLine] < state.blkIndent) {
        break;
      }
      pos = state.bMarks[nextLine] + state.tShift[nextLine];
      max = state.eMarks[nextLine];
      lineText = state.src.slice(pos, max);
      if (HTML_SEQUENCES[i2][1].test(lineText)) {
        if (lineText.length !== 0) {
          nextLine++;
        }
        break;
      }
    }
  }
  state.line = nextLine;
  const token = state.push("html_block", "", 0);
  token.map = [startLine, nextLine];
  token.content = state.getLines(startLine, nextLine, state.blkIndent, true);
  return true;
}
function heading(state, startLine, endLine, silent) {
  let pos = state.bMarks[startLine] + state.tShift[startLine];
  let max = state.eMarks[startLine];
  if (state.sCount[startLine] - state.blkIndent >= 4) {
    return false;
  }
  let ch = state.src.charCodeAt(pos);
  if (ch !== 35 || pos >= max) {
    return false;
  }
  let level = 1;
  ch = state.src.charCodeAt(++pos);
  while (ch === 35 && pos < max && level <= 6) {
    level++;
    ch = state.src.charCodeAt(++pos);
  }
  if (level > 6 || pos < max && !isSpace(ch)) {
    return false;
  }
  if (silent) {
    return true;
  }
  max = state.skipSpacesBack(max, pos);
  const tmp = state.skipCharsBack(max, 35, pos);
  if (tmp > pos && isSpace(state.src.charCodeAt(tmp - 1))) {
    max = tmp;
  }
  state.line = startLine + 1;
  const token_o = state.push("heading_open", "h" + String(level), 1);
  token_o.markup = "########".slice(0, level);
  token_o.map = [startLine, state.line];
  const token_i = state.push("inline", "", 0);
  token_i.content = state.src.slice(pos, max).trim();
  token_i.map = [startLine, state.line];
  token_i.children = [];
  const token_c = state.push("heading_close", "h" + String(level), -1);
  token_c.markup = "########".slice(0, level);
  return true;
}
function lheading(state, startLine, endLine) {
  const terminatorRules = state.md.block.ruler.getRules("paragraph");
  if (state.sCount[startLine] - state.blkIndent >= 4) {
    return false;
  }
  const oldParentType = state.parentType;
  state.parentType = "paragraph";
  let level = 0;
  let marker;
  let nextLine = startLine + 1;
  for (; nextLine < endLine && !state.isEmpty(nextLine); nextLine++) {
    if (state.sCount[nextLine] - state.blkIndent > 3) {
      continue;
    }
    if (state.sCount[nextLine] >= state.blkIndent) {
      let pos = state.bMarks[nextLine] + state.tShift[nextLine];
      const max = state.eMarks[nextLine];
      if (pos < max) {
        marker = state.src.charCodeAt(pos);
        if (marker === 45 || marker === 61) {
          pos = state.skipChars(pos, marker);
          pos = state.skipSpaces(pos);
          if (pos >= max) {
            level = marker === 61 ? 1 : 2;
            break;
          }
        }
      }
    }
    if (state.sCount[nextLine] < 0) {
      continue;
    }
    let terminate = false;
    for (let i2 = 0, l2 = terminatorRules.length; i2 < l2; i2++) {
      if (terminatorRules[i2](state, nextLine, endLine, true)) {
        terminate = true;
        break;
      }
    }
    if (terminate) {
      break;
    }
  }
  if (!level) {
    return false;
  }
  const content = state.getLines(startLine, nextLine, state.blkIndent, false).trim();
  state.line = nextLine + 1;
  const token_o = state.push("heading_open", "h" + String(level), 1);
  token_o.markup = String.fromCharCode(marker);
  token_o.map = [startLine, state.line];
  const token_i = state.push("inline", "", 0);
  token_i.content = content;
  token_i.map = [startLine, state.line - 1];
  token_i.children = [];
  const token_c = state.push("heading_close", "h" + String(level), -1);
  token_c.markup = String.fromCharCode(marker);
  state.parentType = oldParentType;
  return true;
}
function paragraph(state, startLine, endLine) {
  const terminatorRules = state.md.block.ruler.getRules("paragraph");
  const oldParentType = state.parentType;
  let nextLine = startLine + 1;
  state.parentType = "paragraph";
  for (; nextLine < endLine && !state.isEmpty(nextLine); nextLine++) {
    if (state.sCount[nextLine] - state.blkIndent > 3) {
      continue;
    }
    if (state.sCount[nextLine] < 0) {
      continue;
    }
    let terminate = false;
    for (let i2 = 0, l2 = terminatorRules.length; i2 < l2; i2++) {
      if (terminatorRules[i2](state, nextLine, endLine, true)) {
        terminate = true;
        break;
      }
    }
    if (terminate) {
      break;
    }
  }
  const content = state.getLines(startLine, nextLine, state.blkIndent, false).trim();
  state.line = nextLine;
  const token_o = state.push("paragraph_open", "p", 1);
  token_o.map = [startLine, state.line];
  const token_i = state.push("inline", "", 0);
  token_i.content = content;
  token_i.map = [startLine, state.line];
  token_i.children = [];
  state.push("paragraph_close", "p", -1);
  state.parentType = oldParentType;
  return true;
}
const _rules$1 = [
  // First 2 params - rule name & source. Secondary array - list of rules,
  // which can be terminated by this one.
  ["table", table, ["paragraph", "reference"]],
  ["code", code],
  ["fence", fence, ["paragraph", "reference", "blockquote", "list"]],
  ["blockquote", blockquote, ["paragraph", "reference", "blockquote", "list"]],
  ["hr", hr, ["paragraph", "reference", "blockquote", "list"]],
  ["list", list, ["paragraph", "reference", "blockquote"]],
  ["reference", reference],
  ["html_block", html_block, ["paragraph", "reference", "blockquote"]],
  ["heading", heading, ["paragraph", "reference", "blockquote"]],
  ["lheading", lheading],
  ["paragraph", paragraph]
];
function ParserBlock() {
  this.ruler = new Ruler();
  for (let i2 = 0; i2 < _rules$1.length; i2++) {
    this.ruler.push(_rules$1[i2][0], _rules$1[i2][1], { alt: (_rules$1[i2][2] || []).slice() });
  }
}
ParserBlock.prototype.tokenize = function(state, startLine, endLine) {
  const rules = this.ruler.getRules("");
  const len = rules.length;
  const maxNesting = state.md.options.maxNesting;
  let line = startLine;
  let hasEmptyLines = false;
  while (line < endLine) {
    state.line = line = state.skipEmptyLines(line);
    if (line >= endLine) {
      break;
    }
    if (state.sCount[line] < state.blkIndent) {
      break;
    }
    if (state.level >= maxNesting) {
      state.line = endLine;
      break;
    }
    const prevLine = state.line;
    let ok = false;
    for (let i2 = 0; i2 < len; i2++) {
      ok = rules[i2](state, line, endLine, false);
      if (ok) {
        if (prevLine >= state.line) {
          throw new Error("block rule didn't increment state.line");
        }
        break;
      }
    }
    if (!ok) throw new Error("none of the block rules matched");
    state.tight = !hasEmptyLines;
    if (state.isEmpty(state.line - 1)) {
      hasEmptyLines = true;
    }
    line = state.line;
    if (line < endLine && state.isEmpty(line)) {
      hasEmptyLines = true;
      line++;
      state.line = line;
    }
  }
};
ParserBlock.prototype.parse = function(src, md, env, outTokens) {
  if (!src) {
    return;
  }
  const state = new this.State(src, md, env, outTokens);
  this.tokenize(state, state.line, state.lineMax);
};
ParserBlock.prototype.State = StateBlock;
function StateInline(src, md, env, outTokens) {
  this.src = src;
  this.env = env;
  this.md = md;
  this.tokens = outTokens;
  this.tokens_meta = Array(outTokens.length);
  this.pos = 0;
  this.posMax = this.src.length;
  this.level = 0;
  this.pending = "";
  this.pendingLevel = 0;
  this.cache = {};
  this.delimiters = [];
  this._prev_delimiters = [];
  this.backticks = {};
  this.backticksScanned = false;
  this.linkLevel = 0;
}
StateInline.prototype.pushPending = function() {
  const token = new Token("text", "", 0);
  token.content = this.pending;
  token.level = this.pendingLevel;
  this.tokens.push(token);
  this.pending = "";
  return token;
};
StateInline.prototype.push = function(type, tag, nesting) {
  if (this.pending) {
    this.pushPending();
  }
  const token = new Token(type, tag, nesting);
  let token_meta = null;
  if (nesting < 0) {
    this.level--;
    this.delimiters = this._prev_delimiters.pop();
  }
  token.level = this.level;
  if (nesting > 0) {
    this.level++;
    this._prev_delimiters.push(this.delimiters);
    this.delimiters = [];
    token_meta = { delimiters: this.delimiters };
  }
  this.pendingLevel = this.level;
  this.tokens.push(token);
  this.tokens_meta.push(token_meta);
  return token;
};
StateInline.prototype.scanDelims = function(start, canSplitWord) {
  const max = this.posMax;
  const marker = this.src.charCodeAt(start);
  const lastChar = start > 0 ? this.src.charCodeAt(start - 1) : 32;
  let pos = start;
  while (pos < max && this.src.charCodeAt(pos) === marker) {
    pos++;
  }
  const count = pos - start;
  const nextChar = pos < max ? this.src.charCodeAt(pos) : 32;
  const isLastPunctChar = isMdAsciiPunct(lastChar) || isPunctChar(String.fromCharCode(lastChar));
  const isNextPunctChar = isMdAsciiPunct(nextChar) || isPunctChar(String.fromCharCode(nextChar));
  const isLastWhiteSpace = isWhiteSpace(lastChar);
  const isNextWhiteSpace = isWhiteSpace(nextChar);
  const left_flanking = !isNextWhiteSpace && (!isNextPunctChar || isLastWhiteSpace || isLastPunctChar);
  const right_flanking = !isLastWhiteSpace && (!isLastPunctChar || isNextWhiteSpace || isNextPunctChar);
  const can_open = left_flanking && (canSplitWord || !right_flanking || isLastPunctChar);
  const can_close = right_flanking && (canSplitWord || !left_flanking || isNextPunctChar);
  return { can_open, can_close, length: count };
};
StateInline.prototype.Token = Token;
function isTerminatorChar(ch) {
  switch (ch) {
    case 10:
    case 33:
    case 35:
    case 36:
    case 37:
    case 38:
    case 42:
    case 43:
    case 45:
    case 58:
    case 60:
    case 61:
    case 62:
    case 64:
    case 91:
    case 92:
    case 93:
    case 94:
    case 95:
    case 96:
    case 123:
    case 125:
    case 126:
      return true;
    default:
      return false;
  }
}
function text(state, silent) {
  let pos = state.pos;
  while (pos < state.posMax && !isTerminatorChar(state.src.charCodeAt(pos))) {
    pos++;
  }
  if (pos === state.pos) {
    return false;
  }
  if (!silent) {
    state.pending += state.src.slice(state.pos, pos);
  }
  state.pos = pos;
  return true;
}
const SCHEME_RE = /(?:^|[^a-z0-9.+-])([a-z][a-z0-9.+-]*)$/i;
function linkify(state, silent) {
  if (!state.md.options.linkify) return false;
  if (state.linkLevel > 0) return false;
  const pos = state.pos;
  const max = state.posMax;
  if (pos + 3 > max) return false;
  if (state.src.charCodeAt(pos) !== 58) return false;
  if (state.src.charCodeAt(pos + 1) !== 47) return false;
  if (state.src.charCodeAt(pos + 2) !== 47) return false;
  const match = state.pending.match(SCHEME_RE);
  if (!match) return false;
  const proto = match[1];
  const link2 = state.md.linkify.matchAtStart(state.src.slice(pos - proto.length));
  if (!link2) return false;
  let url = link2.url;
  if (url.length <= proto.length) return false;
  url = url.replace(/\*+$/, "");
  const fullUrl = state.md.normalizeLink(url);
  if (!state.md.validateLink(fullUrl)) return false;
  if (!silent) {
    state.pending = state.pending.slice(0, -proto.length);
    const token_o = state.push("link_open", "a", 1);
    token_o.attrs = [["href", fullUrl]];
    token_o.markup = "linkify";
    token_o.info = "auto";
    const token_t = state.push("text", "", 0);
    token_t.content = state.md.normalizeLinkText(url);
    const token_c = state.push("link_close", "a", -1);
    token_c.markup = "linkify";
    token_c.info = "auto";
  }
  state.pos += url.length - proto.length;
  return true;
}
function newline(state, silent) {
  let pos = state.pos;
  if (state.src.charCodeAt(pos) !== 10) {
    return false;
  }
  const pmax = state.pending.length - 1;
  const max = state.posMax;
  if (!silent) {
    if (pmax >= 0 && state.pending.charCodeAt(pmax) === 32) {
      if (pmax >= 1 && state.pending.charCodeAt(pmax - 1) === 32) {
        let ws = pmax - 1;
        while (ws >= 1 && state.pending.charCodeAt(ws - 1) === 32) ws--;
        state.pending = state.pending.slice(0, ws);
        state.push("hardbreak", "br", 0);
      } else {
        state.pending = state.pending.slice(0, -1);
        state.push("softbreak", "br", 0);
      }
    } else {
      state.push("softbreak", "br", 0);
    }
  }
  pos++;
  while (pos < max && isSpace(state.src.charCodeAt(pos))) {
    pos++;
  }
  state.pos = pos;
  return true;
}
const ESCAPED = [];
for (let i2 = 0; i2 < 256; i2++) {
  ESCAPED.push(0);
}
"\\!\"#$%&'()*+,./:;<=>?@[]^_`{|}~-".split("").forEach(function(ch) {
  ESCAPED[ch.charCodeAt(0)] = 1;
});
function escape(state, silent) {
  let pos = state.pos;
  const max = state.posMax;
  if (state.src.charCodeAt(pos) !== 92) return false;
  pos++;
  if (pos >= max) return false;
  let ch1 = state.src.charCodeAt(pos);
  if (ch1 === 10) {
    if (!silent) {
      state.push("hardbreak", "br", 0);
    }
    pos++;
    while (pos < max) {
      ch1 = state.src.charCodeAt(pos);
      if (!isSpace(ch1)) break;
      pos++;
    }
    state.pos = pos;
    return true;
  }
  let escapedStr = state.src[pos];
  if (ch1 >= 55296 && ch1 <= 56319 && pos + 1 < max) {
    const ch2 = state.src.charCodeAt(pos + 1);
    if (ch2 >= 56320 && ch2 <= 57343) {
      escapedStr += state.src[pos + 1];
      pos++;
    }
  }
  const origStr = "\\" + escapedStr;
  if (!silent) {
    const token = state.push("text_special", "", 0);
    if (ch1 < 256 && ESCAPED[ch1] !== 0) {
      token.content = escapedStr;
    } else {
      token.content = origStr;
    }
    token.markup = origStr;
    token.info = "escape";
  }
  state.pos = pos + 1;
  return true;
}
function backtick(state, silent) {
  let pos = state.pos;
  const ch = state.src.charCodeAt(pos);
  if (ch !== 96) {
    return false;
  }
  const start = pos;
  pos++;
  const max = state.posMax;
  while (pos < max && state.src.charCodeAt(pos) === 96) {
    pos++;
  }
  const marker = state.src.slice(start, pos);
  const openerLength = marker.length;
  if (state.backticksScanned && (state.backticks[openerLength] || 0) <= start) {
    if (!silent) state.pending += marker;
    state.pos += openerLength;
    return true;
  }
  let matchEnd = pos;
  let matchStart;
  while ((matchStart = state.src.indexOf("`", matchEnd)) !== -1) {
    matchEnd = matchStart + 1;
    while (matchEnd < max && state.src.charCodeAt(matchEnd) === 96) {
      matchEnd++;
    }
    const closerLength = matchEnd - matchStart;
    if (closerLength === openerLength) {
      if (!silent) {
        const token = state.push("code_inline", "code", 0);
        token.markup = marker;
        token.content = state.src.slice(pos, matchStart).replace(/\n/g, " ").replace(/^ (.+) $/, "$1");
      }
      state.pos = matchEnd;
      return true;
    }
    state.backticks[closerLength] = matchStart;
  }
  state.backticksScanned = true;
  if (!silent) state.pending += marker;
  state.pos += openerLength;
  return true;
}
function strikethrough_tokenize(state, silent) {
  const start = state.pos;
  const marker = state.src.charCodeAt(start);
  if (silent) {
    return false;
  }
  if (marker !== 126) {
    return false;
  }
  const scanned = state.scanDelims(state.pos, true);
  let len = scanned.length;
  const ch = String.fromCharCode(marker);
  if (len < 2) {
    return false;
  }
  let token;
  if (len % 2) {
    token = state.push("text", "", 0);
    token.content = ch;
    len--;
  }
  for (let i2 = 0; i2 < len; i2 += 2) {
    token = state.push("text", "", 0);
    token.content = ch + ch;
    state.delimiters.push({
      marker,
      length: 0,
      // disable "rule of 3" length checks meant for emphasis
      token: state.tokens.length - 1,
      end: -1,
      open: scanned.can_open,
      close: scanned.can_close
    });
  }
  state.pos += scanned.length;
  return true;
}
function postProcess$1(state, delimiters) {
  let token;
  const loneMarkers = [];
  const max = delimiters.length;
  for (let i2 = 0; i2 < max; i2++) {
    const startDelim = delimiters[i2];
    if (startDelim.marker !== 126) {
      continue;
    }
    if (startDelim.end === -1) {
      continue;
    }
    const endDelim = delimiters[startDelim.end];
    token = state.tokens[startDelim.token];
    token.type = "s_open";
    token.tag = "s";
    token.nesting = 1;
    token.markup = "~~";
    token.content = "";
    token = state.tokens[endDelim.token];
    token.type = "s_close";
    token.tag = "s";
    token.nesting = -1;
    token.markup = "~~";
    token.content = "";
    if (state.tokens[endDelim.token - 1].type === "text" && state.tokens[endDelim.token - 1].content === "~") {
      loneMarkers.push(endDelim.token - 1);
    }
  }
  while (loneMarkers.length) {
    const i2 = loneMarkers.pop();
    let j2 = i2 + 1;
    while (j2 < state.tokens.length && state.tokens[j2].type === "s_close") {
      j2++;
    }
    j2--;
    if (i2 !== j2) {
      token = state.tokens[j2];
      state.tokens[j2] = state.tokens[i2];
      state.tokens[i2] = token;
    }
  }
}
function strikethrough_postProcess(state) {
  const tokens_meta = state.tokens_meta;
  const max = state.tokens_meta.length;
  postProcess$1(state, state.delimiters);
  for (let curr = 0; curr < max; curr++) {
    if (tokens_meta[curr] && tokens_meta[curr].delimiters) {
      postProcess$1(state, tokens_meta[curr].delimiters);
    }
  }
}
var r_strikethrough = {
  tokenize: strikethrough_tokenize,
  postProcess: strikethrough_postProcess
};
function emphasis_tokenize(state, silent) {
  const start = state.pos;
  const marker = state.src.charCodeAt(start);
  if (silent) {
    return false;
  }
  if (marker !== 95 && marker !== 42) {
    return false;
  }
  const scanned = state.scanDelims(state.pos, marker === 42);
  for (let i2 = 0; i2 < scanned.length; i2++) {
    const token = state.push("text", "", 0);
    token.content = String.fromCharCode(marker);
    state.delimiters.push({
      // Char code of the starting marker (number).
      //
      marker,
      // Total length of these series of delimiters.
      //
      length: scanned.length,
      // A position of the token this delimiter corresponds to.
      //
      token: state.tokens.length - 1,
      // If this delimiter is matched as a valid opener, `end` will be
      // equal to its position, otherwise it's `-1`.
      //
      end: -1,
      // Boolean flags that determine if this delimiter could open or close
      // an emphasis.
      //
      open: scanned.can_open,
      close: scanned.can_close
    });
  }
  state.pos += scanned.length;
  return true;
}
function postProcess(state, delimiters) {
  const max = delimiters.length;
  for (let i2 = max - 1; i2 >= 0; i2--) {
    const startDelim = delimiters[i2];
    if (startDelim.marker !== 95 && startDelim.marker !== 42) {
      continue;
    }
    if (startDelim.end === -1) {
      continue;
    }
    const endDelim = delimiters[startDelim.end];
    const isStrong = i2 > 0 && delimiters[i2 - 1].end === startDelim.end + 1 && // check that first two markers match and adjacent
    delimiters[i2 - 1].marker === startDelim.marker && delimiters[i2 - 1].token === startDelim.token - 1 && // check that last two markers are adjacent (we can safely assume they match)
    delimiters[startDelim.end + 1].token === endDelim.token + 1;
    const ch = String.fromCharCode(startDelim.marker);
    const token_o = state.tokens[startDelim.token];
    token_o.type = isStrong ? "strong_open" : "em_open";
    token_o.tag = isStrong ? "strong" : "em";
    token_o.nesting = 1;
    token_o.markup = isStrong ? ch + ch : ch;
    token_o.content = "";
    const token_c = state.tokens[endDelim.token];
    token_c.type = isStrong ? "strong_close" : "em_close";
    token_c.tag = isStrong ? "strong" : "em";
    token_c.nesting = -1;
    token_c.markup = isStrong ? ch + ch : ch;
    token_c.content = "";
    if (isStrong) {
      state.tokens[delimiters[i2 - 1].token].content = "";
      state.tokens[delimiters[startDelim.end + 1].token].content = "";
      i2--;
    }
  }
}
function emphasis_post_process(state) {
  const tokens_meta = state.tokens_meta;
  const max = state.tokens_meta.length;
  postProcess(state, state.delimiters);
  for (let curr = 0; curr < max; curr++) {
    if (tokens_meta[curr] && tokens_meta[curr].delimiters) {
      postProcess(state, tokens_meta[curr].delimiters);
    }
  }
}
var r_emphasis = {
  tokenize: emphasis_tokenize,
  postProcess: emphasis_post_process
};
function link(state, silent) {
  let code2, label, res, ref;
  let href = "";
  let title = "";
  let start = state.pos;
  let parseReference = true;
  if (state.src.charCodeAt(state.pos) !== 91) {
    return false;
  }
  const oldPos = state.pos;
  const max = state.posMax;
  const labelStart = state.pos + 1;
  const labelEnd = state.md.helpers.parseLinkLabel(state, state.pos, true);
  if (labelEnd < 0) {
    return false;
  }
  let pos = labelEnd + 1;
  if (pos < max && state.src.charCodeAt(pos) === 40) {
    parseReference = false;
    pos++;
    for (; pos < max; pos++) {
      code2 = state.src.charCodeAt(pos);
      if (!isSpace(code2) && code2 !== 10) {
        break;
      }
    }
    if (pos >= max) {
      return false;
    }
    start = pos;
    res = state.md.helpers.parseLinkDestination(state.src, pos, state.posMax);
    if (res.ok) {
      href = state.md.normalizeLink(res.str);
      if (state.md.validateLink(href)) {
        pos = res.pos;
      } else {
        href = "";
      }
      start = pos;
      for (; pos < max; pos++) {
        code2 = state.src.charCodeAt(pos);
        if (!isSpace(code2) && code2 !== 10) {
          break;
        }
      }
      res = state.md.helpers.parseLinkTitle(state.src, pos, state.posMax);
      if (pos < max && start !== pos && res.ok) {
        title = res.str;
        pos = res.pos;
        for (; pos < max; pos++) {
          code2 = state.src.charCodeAt(pos);
          if (!isSpace(code2) && code2 !== 10) {
            break;
          }
        }
      }
    }
    if (pos >= max || state.src.charCodeAt(pos) !== 41) {
      parseReference = true;
    }
    pos++;
  }
  if (parseReference) {
    if (typeof state.env.references === "undefined") {
      return false;
    }
    if (pos < max && state.src.charCodeAt(pos) === 91) {
      start = pos + 1;
      pos = state.md.helpers.parseLinkLabel(state, pos);
      if (pos >= 0) {
        label = state.src.slice(start, pos++);
      } else {
        pos = labelEnd + 1;
      }
    } else {
      pos = labelEnd + 1;
    }
    if (!label) {
      label = state.src.slice(labelStart, labelEnd);
    }
    ref = state.env.references[normalizeReference(label)];
    if (!ref) {
      state.pos = oldPos;
      return false;
    }
    href = ref.href;
    title = ref.title;
  }
  if (!silent) {
    state.pos = labelStart;
    state.posMax = labelEnd;
    const token_o = state.push("link_open", "a", 1);
    const attrs = [["href", href]];
    token_o.attrs = attrs;
    if (title) {
      attrs.push(["title", title]);
    }
    state.linkLevel++;
    state.md.inline.tokenize(state);
    state.linkLevel--;
    state.push("link_close", "a", -1);
  }
  state.pos = pos;
  state.posMax = max;
  return true;
}
function image(state, silent) {
  let code2, content, label, pos, ref, res, title, start;
  let href = "";
  const oldPos = state.pos;
  const max = state.posMax;
  if (state.src.charCodeAt(state.pos) !== 33) {
    return false;
  }
  if (state.src.charCodeAt(state.pos + 1) !== 91) {
    return false;
  }
  const labelStart = state.pos + 2;
  const labelEnd = state.md.helpers.parseLinkLabel(state, state.pos + 1, false);
  if (labelEnd < 0) {
    return false;
  }
  pos = labelEnd + 1;
  if (pos < max && state.src.charCodeAt(pos) === 40) {
    pos++;
    for (; pos < max; pos++) {
      code2 = state.src.charCodeAt(pos);
      if (!isSpace(code2) && code2 !== 10) {
        break;
      }
    }
    if (pos >= max) {
      return false;
    }
    start = pos;
    res = state.md.helpers.parseLinkDestination(state.src, pos, state.posMax);
    if (res.ok) {
      href = state.md.normalizeLink(res.str);
      if (state.md.validateLink(href)) {
        pos = res.pos;
      } else {
        href = "";
      }
    }
    start = pos;
    for (; pos < max; pos++) {
      code2 = state.src.charCodeAt(pos);
      if (!isSpace(code2) && code2 !== 10) {
        break;
      }
    }
    res = state.md.helpers.parseLinkTitle(state.src, pos, state.posMax);
    if (pos < max && start !== pos && res.ok) {
      title = res.str;
      pos = res.pos;
      for (; pos < max; pos++) {
        code2 = state.src.charCodeAt(pos);
        if (!isSpace(code2) && code2 !== 10) {
          break;
        }
      }
    } else {
      title = "";
    }
    if (pos >= max || state.src.charCodeAt(pos) !== 41) {
      state.pos = oldPos;
      return false;
    }
    pos++;
  } else {
    if (typeof state.env.references === "undefined") {
      return false;
    }
    if (pos < max && state.src.charCodeAt(pos) === 91) {
      start = pos + 1;
      pos = state.md.helpers.parseLinkLabel(state, pos);
      if (pos >= 0) {
        label = state.src.slice(start, pos++);
      } else {
        pos = labelEnd + 1;
      }
    } else {
      pos = labelEnd + 1;
    }
    if (!label) {
      label = state.src.slice(labelStart, labelEnd);
    }
    ref = state.env.references[normalizeReference(label)];
    if (!ref) {
      state.pos = oldPos;
      return false;
    }
    href = ref.href;
    title = ref.title;
  }
  if (!silent) {
    content = state.src.slice(labelStart, labelEnd);
    const tokens = [];
    state.md.inline.parse(
      content,
      state.md,
      state.env,
      tokens
    );
    const token = state.push("image", "img", 0);
    const attrs = [["src", href], ["alt", ""]];
    token.attrs = attrs;
    token.children = tokens;
    token.content = content;
    if (title) {
      attrs.push(["title", title]);
    }
  }
  state.pos = pos;
  state.posMax = max;
  return true;
}
const EMAIL_RE = /^([a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)$/;
const AUTOLINK_RE = /^([a-zA-Z][a-zA-Z0-9+.-]{1,31}):([^<>\x00-\x20]*)$/;
function autolink(state, silent) {
  let pos = state.pos;
  if (state.src.charCodeAt(pos) !== 60) {
    return false;
  }
  const start = state.pos;
  const max = state.posMax;
  for (; ; ) {
    if (++pos >= max) return false;
    const ch = state.src.charCodeAt(pos);
    if (ch === 60) return false;
    if (ch === 62) break;
  }
  const url = state.src.slice(start + 1, pos);
  if (AUTOLINK_RE.test(url)) {
    const fullUrl = state.md.normalizeLink(url);
    if (!state.md.validateLink(fullUrl)) {
      return false;
    }
    if (!silent) {
      const token_o = state.push("link_open", "a", 1);
      token_o.attrs = [["href", fullUrl]];
      token_o.markup = "autolink";
      token_o.info = "auto";
      const token_t = state.push("text", "", 0);
      token_t.content = state.md.normalizeLinkText(url);
      const token_c = state.push("link_close", "a", -1);
      token_c.markup = "autolink";
      token_c.info = "auto";
    }
    state.pos += url.length + 2;
    return true;
  }
  if (EMAIL_RE.test(url)) {
    const fullUrl = state.md.normalizeLink("mailto:" + url);
    if (!state.md.validateLink(fullUrl)) {
      return false;
    }
    if (!silent) {
      const token_o = state.push("link_open", "a", 1);
      token_o.attrs = [["href", fullUrl]];
      token_o.markup = "autolink";
      token_o.info = "auto";
      const token_t = state.push("text", "", 0);
      token_t.content = state.md.normalizeLinkText(url);
      const token_c = state.push("link_close", "a", -1);
      token_c.markup = "autolink";
      token_c.info = "auto";
    }
    state.pos += url.length + 2;
    return true;
  }
  return false;
}
function isLinkOpen(str) {
  return /^<a[>\s]/i.test(str);
}
function isLinkClose(str) {
  return /^<\/a\s*>/i.test(str);
}
function isLetter(ch) {
  const lc = ch | 32;
  return lc >= 97 && lc <= 122;
}
function html_inline(state, silent) {
  if (!state.md.options.html) {
    return false;
  }
  const max = state.posMax;
  const pos = state.pos;
  if (state.src.charCodeAt(pos) !== 60 || pos + 2 >= max) {
    return false;
  }
  const ch = state.src.charCodeAt(pos + 1);
  if (ch !== 33 && ch !== 63 && ch !== 47 && !isLetter(ch)) {
    return false;
  }
  const match = state.src.slice(pos).match(HTML_TAG_RE);
  if (!match) {
    return false;
  }
  if (!silent) {
    const token = state.push("html_inline", "", 0);
    token.content = match[0];
    if (isLinkOpen(token.content)) state.linkLevel++;
    if (isLinkClose(token.content)) state.linkLevel--;
  }
  state.pos += match[0].length;
  return true;
}
const DIGITAL_RE = /^&#((?:x[a-f0-9]{1,6}|[0-9]{1,7}));/i;
const NAMED_RE = /^&([a-z][a-z0-9]{1,31});/i;
function entity(state, silent) {
  const pos = state.pos;
  const max = state.posMax;
  if (state.src.charCodeAt(pos) !== 38) return false;
  if (pos + 1 >= max) return false;
  const ch = state.src.charCodeAt(pos + 1);
  if (ch === 35) {
    const match = state.src.slice(pos).match(DIGITAL_RE);
    if (match) {
      if (!silent) {
        const code2 = match[1][0].toLowerCase() === "x" ? parseInt(match[1].slice(1), 16) : parseInt(match[1], 10);
        const token = state.push("text_special", "", 0);
        token.content = isValidEntityCode(code2) ? fromCodePoint(code2) : fromCodePoint(65533);
        token.markup = match[0];
        token.info = "entity";
      }
      state.pos += match[0].length;
      return true;
    }
  } else {
    const match = state.src.slice(pos).match(NAMED_RE);
    if (match) {
      const decoded = libExports.decodeHTML(match[0]);
      if (decoded !== match[0]) {
        if (!silent) {
          const token = state.push("text_special", "", 0);
          token.content = decoded;
          token.markup = match[0];
          token.info = "entity";
        }
        state.pos += match[0].length;
        return true;
      }
    }
  }
  return false;
}
function processDelimiters(delimiters) {
  const openersBottom = {};
  const max = delimiters.length;
  if (!max) return;
  let headerIdx = 0;
  let lastTokenIdx = -2;
  const jumps = [];
  for (let closerIdx = 0; closerIdx < max; closerIdx++) {
    const closer = delimiters[closerIdx];
    jumps.push(0);
    if (delimiters[headerIdx].marker !== closer.marker || lastTokenIdx !== closer.token - 1) {
      headerIdx = closerIdx;
    }
    lastTokenIdx = closer.token;
    closer.length = closer.length || 0;
    if (!closer.close) continue;
    if (!openersBottom.hasOwnProperty(closer.marker)) {
      openersBottom[closer.marker] = [-1, -1, -1, -1, -1, -1];
    }
    const minOpenerIdx = openersBottom[closer.marker][(closer.open ? 3 : 0) + closer.length % 3];
    let openerIdx = headerIdx - jumps[headerIdx] - 1;
    let newMinOpenerIdx = openerIdx;
    for (; openerIdx > minOpenerIdx; openerIdx -= jumps[openerIdx] + 1) {
      const opener = delimiters[openerIdx];
      if (opener.marker !== closer.marker) continue;
      if (opener.open && opener.end < 0) {
        let isOddMatch = false;
        if (opener.close || closer.open) {
          if ((opener.length + closer.length) % 3 === 0) {
            if (opener.length % 3 !== 0 || closer.length % 3 !== 0) {
              isOddMatch = true;
            }
          }
        }
        if (!isOddMatch) {
          const lastJump = openerIdx > 0 && !delimiters[openerIdx - 1].open ? jumps[openerIdx - 1] + 1 : 0;
          jumps[closerIdx] = closerIdx - openerIdx + lastJump;
          jumps[openerIdx] = lastJump;
          closer.open = false;
          opener.end = closerIdx;
          opener.close = false;
          newMinOpenerIdx = -1;
          lastTokenIdx = -2;
          break;
        }
      }
    }
    if (newMinOpenerIdx !== -1) {
      openersBottom[closer.marker][(closer.open ? 3 : 0) + (closer.length || 0) % 3] = newMinOpenerIdx;
    }
  }
}
function link_pairs(state) {
  const tokens_meta = state.tokens_meta;
  const max = state.tokens_meta.length;
  processDelimiters(state.delimiters);
  for (let curr = 0; curr < max; curr++) {
    if (tokens_meta[curr] && tokens_meta[curr].delimiters) {
      processDelimiters(tokens_meta[curr].delimiters);
    }
  }
}
function fragments_join(state) {
  let curr, last;
  let level = 0;
  const tokens = state.tokens;
  const max = state.tokens.length;
  for (curr = last = 0; curr < max; curr++) {
    if (tokens[curr].nesting < 0) level--;
    tokens[curr].level = level;
    if (tokens[curr].nesting > 0) level++;
    if (tokens[curr].type === "text" && curr + 1 < max && tokens[curr + 1].type === "text") {
      tokens[curr + 1].content = tokens[curr].content + tokens[curr + 1].content;
    } else {
      if (curr !== last) {
        tokens[last] = tokens[curr];
      }
      last++;
    }
  }
  if (curr !== last) {
    tokens.length = last;
  }
}
const _rules = [
  ["text", text],
  ["linkify", linkify],
  ["newline", newline],
  ["escape", escape],
  ["backticks", backtick],
  ["strikethrough", r_strikethrough.tokenize],
  ["emphasis", r_emphasis.tokenize],
  ["link", link],
  ["image", image],
  ["autolink", autolink],
  ["html_inline", html_inline],
  ["entity", entity]
];
const _rules2 = [
  ["balance_pairs", link_pairs],
  ["strikethrough", r_strikethrough.postProcess],
  ["emphasis", r_emphasis.postProcess],
  // rules for pairs separate '**' into its own text tokens, which may be left unused,
  // rule below merges unused segments back with the rest of the text
  ["fragments_join", fragments_join]
];
function ParserInline() {
  this.ruler = new Ruler();
  for (let i2 = 0; i2 < _rules.length; i2++) {
    this.ruler.push(_rules[i2][0], _rules[i2][1]);
  }
  this.ruler2 = new Ruler();
  for (let i2 = 0; i2 < _rules2.length; i2++) {
    this.ruler2.push(_rules2[i2][0], _rules2[i2][1]);
  }
}
ParserInline.prototype.skipToken = function(state) {
  const pos = state.pos;
  const rules = this.ruler.getRules("");
  const len = rules.length;
  const maxNesting = state.md.options.maxNesting;
  const cache = state.cache;
  if (typeof cache[pos] !== "undefined") {
    state.pos = cache[pos];
    return;
  }
  let ok = false;
  if (state.level < maxNesting) {
    for (let i2 = 0; i2 < len; i2++) {
      state.level++;
      ok = rules[i2](state, true);
      state.level--;
      if (ok) {
        if (pos >= state.pos) {
          throw new Error("inline rule didn't increment state.pos");
        }
        break;
      }
    }
  } else {
    state.pos = state.posMax;
  }
  if (!ok) {
    state.pos++;
  }
  cache[pos] = state.pos;
};
ParserInline.prototype.tokenize = function(state) {
  const rules = this.ruler.getRules("");
  const len = rules.length;
  const end = state.posMax;
  const maxNesting = state.md.options.maxNesting;
  while (state.pos < end) {
    const prevPos = state.pos;
    let ok = false;
    if (state.level < maxNesting) {
      for (let i2 = 0; i2 < len; i2++) {
        ok = rules[i2](state, false);
        if (ok) {
          if (prevPos >= state.pos) {
            throw new Error("inline rule didn't increment state.pos");
          }
          break;
        }
      }
    }
    if (ok) {
      if (state.pos >= end) {
        break;
      }
      continue;
    }
    state.pending += state.src[state.pos++];
  }
  if (state.pending) {
    state.pushPending();
  }
};
ParserInline.prototype.parse = function(str, md, env, outTokens) {
  const state = new this.State(str, md, env, outTokens);
  this.tokenize(state);
  const rules = this.ruler2.getRules("");
  const len = rules.length;
  for (let i2 = 0; i2 < len; i2++) {
    rules[i2](state);
  }
};
ParserInline.prototype.State = StateInline;
var index_cjs;
var hasRequiredIndex_cjs;
function requireIndex_cjs() {
  if (hasRequiredIndex_cjs) return index_cjs;
  hasRequiredIndex_cjs = 1;
  var uc_micro = requireIndex_cjs$1();
  function reFactory(opts) {
    const re = {};
    opts = opts || {};
    re.src_Any = uc_micro.Any.source;
    re.src_Cc = uc_micro.Cc.source;
    re.src_Z = uc_micro.Z.source;
    re.src_P = uc_micro.P.source;
    re.src_ZPCc = [re.src_Z, re.src_P, re.src_Cc].join("|");
    re.src_ZCc = [re.src_Z, re.src_Cc].join("|");
    const text_separators = "[><｜]";
    re.src_pseudo_letter = "(?:(?!" + text_separators + "|" + re.src_ZPCc + ")" + re.src_Any + ")";
    re.src_ip4 = "(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)";
    re.src_auth = "(?:(?:(?!" + re.src_ZCc + "|[@/\\[\\]()]).)+@)?";
    re.src_port = "(?::(?:6(?:[0-4]\\d{3}|5(?:[0-4]\\d{2}|5(?:[0-2]\\d|3[0-5])))|[1-5]?\\d{1,4}))?";
    re.src_host_terminator = "(?=$|" + text_separators + "|" + re.src_ZPCc + ")(?!" + (opts["---"] ? "-(?!--)|" : "-|") + "_|:\\d|\\.-|\\.(?!$|" + re.src_ZPCc + "))";
    re.src_path = "(?:[/?#](?:(?!" + re.src_ZCc + "|" + text_separators + `|[()[\\]{}.,"'?!\\-;]).|\\[(?:(?!` + re.src_ZCc + "|\\]).)*\\]|\\((?:(?!" + re.src_ZCc + "|[)]).)*\\)|\\{(?:(?!" + re.src_ZCc + '|[}]).)*\\}|\\"(?:(?!' + re.src_ZCc + `|["]).)+\\"|\\'(?:(?!` + re.src_ZCc + "|[']).)+\\'|\\'(?=" + re.src_pseudo_letter + "|[-])|\\.{2,}[a-zA-Z0-9%/&]|\\.(?!" + re.src_ZCc + "|[.]|$)|" + (opts["---"] ? "\\-(?!--(?:[^-]|$))(?:-*)|" : "\\-+|") + // allow `,,,` in paths
    ",(?!" + re.src_ZCc + "|$)|;(?!" + re.src_ZCc + "|$)|\\!+(?!" + re.src_ZCc + "|[!]|$)|\\?(?!" + re.src_ZCc + "|[?]|$))+|\\/)?";
    re.src_email_name = '[\\-;:&=\\+\\$,\\.a-zA-Z0-9_][\\-;:&=\\+\\$,\\"\\.a-zA-Z0-9_]*';
    re.src_xn = "xn--[a-z0-9\\-]{1,59}";
    re.src_domain_root = // Allow letters & digits (http://test1)
    "(?:" + re.src_xn + "|" + re.src_pseudo_letter + "{1,63})";
    re.src_domain = "(?:" + re.src_xn + "|(?:" + re.src_pseudo_letter + ")|(?:" + re.src_pseudo_letter + "(?:-|" + re.src_pseudo_letter + "){0,61}" + re.src_pseudo_letter + "))";
    re.src_host = "(?:(?:(?:(?:" + re.src_domain + ")\\.)*" + re.src_domain + "))";
    re.tpl_host_fuzzy = "(?:" + re.src_ip4 + "|(?:(?:(?:" + re.src_domain + ")\\.)+(?:%TLDS%)))";
    re.tpl_host_no_ip_fuzzy = "(?:(?:(?:" + re.src_domain + ")\\.)+(?:%TLDS%))";
    re.src_host_strict = re.src_host + re.src_host_terminator;
    re.tpl_host_fuzzy_strict = re.tpl_host_fuzzy + re.src_host_terminator;
    re.src_host_port_strict = re.src_host + re.src_port + re.src_host_terminator;
    re.tpl_host_port_fuzzy_strict = re.tpl_host_fuzzy + re.src_port + re.src_host_terminator;
    re.tpl_host_port_no_ip_fuzzy_strict = re.tpl_host_no_ip_fuzzy + re.src_port + re.src_host_terminator;
    re.tpl_host_fuzzy_test = "localhost|www\\.|\\.\\d{1,3}\\.|(?:\\.(?:%TLDS%)(?:" + re.src_ZPCc + "|>|$))";
    re.tpl_email_fuzzy = "(^|" + text_separators + '|"|\\(|' + re.src_ZCc + ")(" + re.src_email_name + "@" + re.tpl_host_fuzzy_strict + ")";
    re.tpl_link_fuzzy = // Fuzzy link can't be prepended with .:/\- and non punctuation.
    // but can start with > (markdown blockquote)
    "(^|(?![.:/\\-_@])(?:[$+<=>^`|｜]|" + re.src_ZPCc + "))((?![$+<=>^`|｜])" + re.tpl_host_port_fuzzy_strict + re.src_path + ")";
    re.tpl_link_no_ip_fuzzy = // Fuzzy link can't be prepended with .:/\- and non punctuation.
    // but can start with > (markdown blockquote)
    "(^|(?![.:/\\-_@])(?:[$+<=>^`|｜]|" + re.src_ZPCc + "))((?![$+<=>^`|｜])" + re.tpl_host_port_no_ip_fuzzy_strict + re.src_path + ")";
    return re;
  }
  function assign2(obj) {
    const sources = Array.prototype.slice.call(arguments, 1);
    sources.forEach(function(source) {
      if (!source) {
        return;
      }
      Object.keys(source).forEach(function(key) {
        obj[key] = source[key];
      });
    });
    return obj;
  }
  function _class2(obj) {
    return Object.prototype.toString.call(obj);
  }
  function isString2(obj) {
    return _class2(obj) === "[object String]";
  }
  function isObject(obj) {
    return _class2(obj) === "[object Object]";
  }
  function isRegExp(obj) {
    return _class2(obj) === "[object RegExp]";
  }
  function isFunction(obj) {
    return _class2(obj) === "[object Function]";
  }
  function escapeRE2(str) {
    return str.replace(/[.?*+^$[\]\\(){}|-]/g, "\\$&");
  }
  const defaultOptions = {
    fuzzyLink: true,
    fuzzyEmail: true,
    fuzzyIP: false
  };
  function isOptionsObj(obj) {
    return Object.keys(obj || {}).reduce(function(acc, k2) {
      return acc || defaultOptions.hasOwnProperty(k2);
    }, false);
  }
  const defaultSchemas = {
    "http:": {
      validate: function(text2, pos, self2) {
        const tail = text2.slice(pos);
        if (!self2.re.http) {
          self2.re.http = new RegExp(
            "^\\/\\/" + self2.re.src_auth + self2.re.src_host_port_strict + self2.re.src_path,
            "i"
          );
        }
        if (self2.re.http.test(tail)) {
          return tail.match(self2.re.http)[0].length;
        }
        return 0;
      }
    },
    "https:": "http:",
    "ftp:": "http:",
    "//": {
      validate: function(text2, pos, self2) {
        const tail = text2.slice(pos);
        if (!self2.re.no_http) {
          self2.re.no_http = new RegExp(
            "^" + self2.re.src_auth + // Don't allow single-level domains, because of false positives like '//test'
            // with code comments
            "(?:localhost|(?:(?:" + self2.re.src_domain + ")\\.)+" + self2.re.src_domain_root + ")" + self2.re.src_port + self2.re.src_host_terminator + self2.re.src_path,
            "i"
          );
        }
        if (self2.re.no_http.test(tail)) {
          if (pos >= 3 && text2[pos - 3] === ":") {
            return 0;
          }
          if (pos >= 3 && text2[pos - 3] === "/") {
            return 0;
          }
          return tail.match(self2.re.no_http)[0].length;
        }
        return 0;
      }
    },
    "mailto:": {
      validate: function(text2, pos, self2) {
        const tail = text2.slice(pos);
        if (!self2.re.mailto) {
          self2.re.mailto = new RegExp(
            "^" + self2.re.src_email_name + "@" + self2.re.src_host_strict,
            "i"
          );
        }
        if (self2.re.mailto.test(tail)) {
          return tail.match(self2.re.mailto)[0].length;
        }
        return 0;
      }
    }
  };
  const tlds_2ch_src_re = "a[cdefgilmnoqrstuwxz]|b[abdefghijmnorstvwyz]|c[acdfghiklmnoruvwxyz]|d[ejkmoz]|e[cegrstu]|f[ijkmor]|g[abdefghilmnpqrstuwy]|h[kmnrtu]|i[delmnoqrst]|j[emop]|k[eghimnprwyz]|l[abcikrstuvy]|m[acdeghklmnopqrstuvwxyz]|n[acefgilopruz]|om|p[aefghklmnrstwy]|qa|r[eosuw]|s[abcdeghijklmnortuvxyz]|t[cdfghjklmnortvwz]|u[agksyz]|v[aceginu]|w[fs]|y[et]|z[amw]";
  const tlds_default = "biz|com|edu|gov|net|org|pro|web|xxx|aero|asia|coop|info|museum|name|shop|рф".split("|");
  function resetScanCache(self2) {
    self2.__index__ = -1;
    self2.__text_cache__ = "";
  }
  function createValidator(re) {
    return function(text2, pos) {
      const tail = text2.slice(pos);
      if (re.test(tail)) {
        return tail.match(re)[0].length;
      }
      return 0;
    };
  }
  function createNormalizer() {
    return function(match, self2) {
      self2.normalize(match);
    };
  }
  function compile(self2) {
    const re = self2.re = reFactory(self2.__opts__);
    const tlds = self2.__tlds__.slice();
    self2.onCompile();
    if (!self2.__tlds_replaced__) {
      tlds.push(tlds_2ch_src_re);
    }
    tlds.push(re.src_xn);
    re.src_tlds = tlds.join("|");
    function untpl(tpl) {
      return tpl.replace("%TLDS%", re.src_tlds);
    }
    re.email_fuzzy = RegExp(untpl(re.tpl_email_fuzzy), "i");
    re.link_fuzzy = RegExp(untpl(re.tpl_link_fuzzy), "i");
    re.link_no_ip_fuzzy = RegExp(untpl(re.tpl_link_no_ip_fuzzy), "i");
    re.host_fuzzy_test = RegExp(untpl(re.tpl_host_fuzzy_test), "i");
    const aliases = [];
    self2.__compiled__ = {};
    function schemaError(name, val) {
      throw new Error('(LinkifyIt) Invalid schema "' + name + '": ' + val);
    }
    Object.keys(self2.__schemas__).forEach(function(name) {
      const val = self2.__schemas__[name];
      if (val === null) {
        return;
      }
      const compiled = { validate: null, link: null };
      self2.__compiled__[name] = compiled;
      if (isObject(val)) {
        if (isRegExp(val.validate)) {
          compiled.validate = createValidator(val.validate);
        } else if (isFunction(val.validate)) {
          compiled.validate = val.validate;
        } else {
          schemaError(name, val);
        }
        if (isFunction(val.normalize)) {
          compiled.normalize = val.normalize;
        } else if (!val.normalize) {
          compiled.normalize = createNormalizer();
        } else {
          schemaError(name, val);
        }
        return;
      }
      if (isString2(val)) {
        aliases.push(name);
        return;
      }
      schemaError(name, val);
    });
    aliases.forEach(function(alias) {
      if (!self2.__compiled__[self2.__schemas__[alias]]) {
        return;
      }
      self2.__compiled__[alias].validate = self2.__compiled__[self2.__schemas__[alias]].validate;
      self2.__compiled__[alias].normalize = self2.__compiled__[self2.__schemas__[alias]].normalize;
    });
    self2.__compiled__[""] = { validate: null, normalize: createNormalizer() };
    const slist = Object.keys(self2.__compiled__).filter(function(name) {
      return name.length > 0 && self2.__compiled__[name];
    }).map(escapeRE2).join("|");
    self2.re.schema_test = RegExp("(^|(?!_)(?:[><｜]|" + re.src_ZPCc + "))(" + slist + ")", "i");
    self2.re.schema_search = RegExp("(^|(?!_)(?:[><｜]|" + re.src_ZPCc + "))(" + slist + ")", "ig");
    self2.re.schema_at_start = RegExp("^" + self2.re.schema_search.source, "i");
    self2.re.pretest = RegExp(
      "(" + self2.re.schema_test.source + ")|(" + self2.re.host_fuzzy_test.source + ")|@",
      "i"
    );
    resetScanCache(self2);
  }
  function Match(self2, shift) {
    const start = self2.__index__;
    const end = self2.__last_index__;
    const text2 = self2.__text_cache__.slice(start, end);
    this.schema = self2.__schema__.toLowerCase();
    this.index = start + shift;
    this.lastIndex = end + shift;
    this.raw = text2;
    this.text = text2;
    this.url = text2;
  }
  function createMatch(self2, shift) {
    const match = new Match(self2, shift);
    self2.__compiled__[match.schema].normalize(match, self2);
    return match;
  }
  function LinkifyIt2(schemas, options) {
    if (!(this instanceof LinkifyIt2)) {
      return new LinkifyIt2(schemas, options);
    }
    if (!options) {
      if (isOptionsObj(schemas)) {
        options = schemas;
        schemas = {};
      }
    }
    this.__opts__ = assign2({}, defaultOptions, options);
    this.__index__ = -1;
    this.__last_index__ = -1;
    this.__schema__ = "";
    this.__text_cache__ = "";
    this.__schemas__ = assign2({}, defaultSchemas, schemas);
    this.__compiled__ = {};
    this.__tlds__ = tlds_default;
    this.__tlds_replaced__ = false;
    this.re = {};
    compile(this);
  }
  LinkifyIt2.prototype.add = function add(schema, definition) {
    this.__schemas__[schema] = definition;
    compile(this);
    return this;
  };
  LinkifyIt2.prototype.set = function set(options) {
    this.__opts__ = assign2(this.__opts__, options);
    return this;
  };
  LinkifyIt2.prototype.test = function test(text2) {
    this.__text_cache__ = text2;
    this.__index__ = -1;
    if (!text2.length) {
      return false;
    }
    let m2, ml, me, len, shift, next, re, tld_pos, at_pos;
    if (this.re.schema_test.test(text2)) {
      re = this.re.schema_search;
      re.lastIndex = 0;
      while ((m2 = re.exec(text2)) !== null) {
        len = this.testSchemaAt(text2, m2[2], re.lastIndex);
        if (len) {
          this.__schema__ = m2[2];
          this.__index__ = m2.index + m2[1].length;
          this.__last_index__ = m2.index + m2[0].length + len;
          break;
        }
      }
    }
    if (this.__opts__.fuzzyLink && this.__compiled__["http:"]) {
      tld_pos = text2.search(this.re.host_fuzzy_test);
      if (tld_pos >= 0) {
        if (this.__index__ < 0 || tld_pos < this.__index__) {
          if ((ml = text2.match(this.__opts__.fuzzyIP ? this.re.link_fuzzy : this.re.link_no_ip_fuzzy)) !== null) {
            shift = ml.index + ml[1].length;
            if (this.__index__ < 0 || shift < this.__index__) {
              this.__schema__ = "";
              this.__index__ = shift;
              this.__last_index__ = ml.index + ml[0].length;
            }
          }
        }
      }
    }
    if (this.__opts__.fuzzyEmail && this.__compiled__["mailto:"]) {
      at_pos = text2.indexOf("@");
      if (at_pos >= 0) {
        if ((me = text2.match(this.re.email_fuzzy)) !== null) {
          shift = me.index + me[1].length;
          next = me.index + me[0].length;
          if (this.__index__ < 0 || shift < this.__index__ || shift === this.__index__ && next > this.__last_index__) {
            this.__schema__ = "mailto:";
            this.__index__ = shift;
            this.__last_index__ = next;
          }
        }
      }
    }
    return this.__index__ >= 0;
  };
  LinkifyIt2.prototype.pretest = function pretest(text2) {
    return this.re.pretest.test(text2);
  };
  LinkifyIt2.prototype.testSchemaAt = function testSchemaAt(text2, schema, pos) {
    if (!this.__compiled__[schema.toLowerCase()]) {
      return 0;
    }
    return this.__compiled__[schema.toLowerCase()].validate(text2, pos, this);
  };
  LinkifyIt2.prototype.match = function match(text2) {
    const result = [];
    let shift = 0;
    if (this.__index__ >= 0 && this.__text_cache__ === text2) {
      result.push(createMatch(this, shift));
      shift = this.__last_index__;
    }
    let tail = shift ? text2.slice(shift) : text2;
    while (this.test(tail)) {
      result.push(createMatch(this, shift));
      tail = tail.slice(this.__last_index__);
      shift += this.__last_index__;
    }
    if (result.length) {
      return result;
    }
    return null;
  };
  LinkifyIt2.prototype.matchAtStart = function matchAtStart(text2) {
    this.__text_cache__ = text2;
    this.__index__ = -1;
    if (!text2.length) return null;
    const m2 = this.re.schema_at_start.exec(text2);
    if (!m2) return null;
    const len = this.testSchemaAt(text2, m2[2], m2[0].length);
    if (!len) return null;
    this.__schema__ = m2[2];
    this.__index__ = m2.index + m2[1].length;
    this.__last_index__ = m2.index + m2[0].length + len;
    return createMatch(this, 0);
  };
  LinkifyIt2.prototype.tlds = function tlds(list2, keepOld) {
    list2 = Array.isArray(list2) ? list2 : [list2];
    if (!keepOld) {
      this.__tlds__ = list2.slice();
      this.__tlds_replaced__ = true;
      compile(this);
      return this;
    }
    this.__tlds__ = this.__tlds__.concat(list2).sort().filter(function(el, idx, arr) {
      return el !== arr[idx - 1];
    }).reverse();
    compile(this);
    return this;
  };
  LinkifyIt2.prototype.normalize = function normalize2(match) {
    if (!match.schema) {
      match.url = "http://" + match.url;
    }
    if (match.schema === "mailto:" && !/^mailto:/i.test(match.url)) {
      match.url = "mailto:" + match.url;
    }
  };
  LinkifyIt2.prototype.onCompile = function onCompile() {
  };
  index_cjs = LinkifyIt2;
  return index_cjs;
}
var index_cjsExports = requireIndex_cjs();
var LinkifyIt = /* @__PURE__ */ getDefaultExportFromCjs(index_cjsExports);
const maxInt = 2147483647;
const base = 36;
const tMin = 1;
const tMax = 26;
const skew = 38;
const damp = 700;
const initialBias = 72;
const initialN = 128;
const delimiter = "-";
const regexPunycode = /^xn--/;
const regexNonASCII = /[^\0-\x7F]/;
const regexSeparators = /[\x2E\u3002\uFF0E\uFF61]/g;
const errors = {
  "overflow": "Overflow: input needs wider integers to process",
  "not-basic": "Illegal input >= 0x80 (not a basic code point)",
  "invalid-input": "Invalid input"
};
const baseMinusTMin = base - tMin;
const floor = Math.floor;
const stringFromCharCode = String.fromCharCode;
function error(type) {
  throw new RangeError(errors[type]);
}
function map(array, callback) {
  const result = [];
  let length = array.length;
  while (length--) {
    result[length] = callback(array[length]);
  }
  return result;
}
function mapDomain(domain, callback) {
  const parts = domain.split("@");
  let result = "";
  if (parts.length > 1) {
    result = parts[0] + "@";
    domain = parts[1];
  }
  domain = domain.replace(regexSeparators, ".");
  const labels = domain.split(".");
  const encoded = map(labels, callback).join(".");
  return result + encoded;
}
function ucs2decode(string) {
  const output = [];
  let counter = 0;
  const length = string.length;
  while (counter < length) {
    const value = string.charCodeAt(counter++);
    if (value >= 55296 && value <= 56319 && counter < length) {
      const extra = string.charCodeAt(counter++);
      if ((extra & 64512) == 56320) {
        output.push(((value & 1023) << 10) + (extra & 1023) + 65536);
      } else {
        output.push(value);
        counter--;
      }
    } else {
      output.push(value);
    }
  }
  return output;
}
const ucs2encode = (codePoints) => String.fromCodePoint(...codePoints);
const basicToDigit = function(codePoint) {
  if (codePoint >= 48 && codePoint < 58) {
    return 26 + (codePoint - 48);
  }
  if (codePoint >= 65 && codePoint < 91) {
    return codePoint - 65;
  }
  if (codePoint >= 97 && codePoint < 123) {
    return codePoint - 97;
  }
  return base;
};
const digitToBasic = function(digit, flag) {
  return digit + 22 + 75 * (digit < 26) - ((flag != 0) << 5);
};
const adapt = function(delta, numPoints, firstTime) {
  let k2 = 0;
  delta = firstTime ? floor(delta / damp) : delta >> 1;
  delta += floor(delta / numPoints);
  for (; delta > baseMinusTMin * tMax >> 1; k2 += base) {
    delta = floor(delta / baseMinusTMin);
  }
  return floor(k2 + (baseMinusTMin + 1) * delta / (delta + skew));
};
const decode = function(input) {
  const output = [];
  const inputLength = input.length;
  let i2 = 0;
  let n2 = initialN;
  let bias = initialBias;
  let basic = input.lastIndexOf(delimiter);
  if (basic < 0) {
    basic = 0;
  }
  for (let j2 = 0; j2 < basic; ++j2) {
    if (input.charCodeAt(j2) >= 128) {
      error("not-basic");
    }
    output.push(input.charCodeAt(j2));
  }
  for (let index = basic > 0 ? basic + 1 : 0; index < inputLength; ) {
    const oldi = i2;
    for (let w2 = 1, k2 = base; ; k2 += base) {
      if (index >= inputLength) {
        error("invalid-input");
      }
      const digit = basicToDigit(input.charCodeAt(index++));
      if (digit >= base) {
        error("invalid-input");
      }
      if (digit > floor((maxInt - i2) / w2)) {
        error("overflow");
      }
      i2 += digit * w2;
      const t2 = k2 <= bias ? tMin : k2 >= bias + tMax ? tMax : k2 - bias;
      if (digit < t2) {
        break;
      }
      const baseMinusT = base - t2;
      if (w2 > floor(maxInt / baseMinusT)) {
        error("overflow");
      }
      w2 *= baseMinusT;
    }
    const out = output.length + 1;
    bias = adapt(i2 - oldi, out, oldi == 0);
    if (floor(i2 / out) > maxInt - n2) {
      error("overflow");
    }
    n2 += floor(i2 / out);
    i2 %= out;
    output.splice(i2++, 0, n2);
  }
  return String.fromCodePoint(...output);
};
const encode = function(input) {
  const output = [];
  input = ucs2decode(input);
  const inputLength = input.length;
  let n2 = initialN;
  let delta = 0;
  let bias = initialBias;
  for (const currentValue of input) {
    if (currentValue < 128) {
      output.push(stringFromCharCode(currentValue));
    }
  }
  const basicLength = output.length;
  let handledCPCount = basicLength;
  if (basicLength) {
    output.push(delimiter);
  }
  while (handledCPCount < inputLength) {
    let m2 = maxInt;
    for (const currentValue of input) {
      if (currentValue >= n2 && currentValue < m2) {
        m2 = currentValue;
      }
    }
    const handledCPCountPlusOne = handledCPCount + 1;
    if (m2 - n2 > floor((maxInt - delta) / handledCPCountPlusOne)) {
      error("overflow");
    }
    delta += (m2 - n2) * handledCPCountPlusOne;
    n2 = m2;
    for (const currentValue of input) {
      if (currentValue < n2 && ++delta > maxInt) {
        error("overflow");
      }
      if (currentValue === n2) {
        let q2 = delta;
        for (let k2 = base; ; k2 += base) {
          const t2 = k2 <= bias ? tMin : k2 >= bias + tMax ? tMax : k2 - bias;
          if (q2 < t2) {
            break;
          }
          const qMinusT = q2 - t2;
          const baseMinusT = base - t2;
          output.push(
            stringFromCharCode(digitToBasic(t2 + qMinusT % baseMinusT, 0))
          );
          q2 = floor(qMinusT / baseMinusT);
        }
        output.push(stringFromCharCode(digitToBasic(q2, 0)));
        bias = adapt(delta, handledCPCountPlusOne, handledCPCount === basicLength);
        delta = 0;
        ++handledCPCount;
      }
    }
    ++delta;
    ++n2;
  }
  return output.join("");
};
const toUnicode = function(input) {
  return mapDomain(input, function(string) {
    return regexPunycode.test(string) ? decode(string.slice(4).toLowerCase()) : string;
  });
};
const toASCII = function(input) {
  return mapDomain(input, function(string) {
    return regexNonASCII.test(string) ? "xn--" + encode(string) : string;
  });
};
const punycode = {
  /**
   * A string representing the current Punycode.js version number.
   * @memberOf punycode
   * @type String
   */
  "version": "2.3.1",
  /**
   * An object of methods to convert from JavaScript's internal character
   * representation (UCS-2) to Unicode code points, and back.
   * @see <https://mathiasbynens.be/notes/javascript-encoding>
   * @memberOf punycode
   * @type Object
   */
  "ucs2": {
    "decode": ucs2decode,
    "encode": ucs2encode
  },
  "decode": decode,
  "encode": encode,
  "toASCII": toASCII,
  "toUnicode": toUnicode
};
var cfg_default = {
  options: {
    // Enable HTML tags in source
    html: false,
    // Use '/' to close single tags (<br />)
    xhtmlOut: false,
    // Convert '\n' in paragraphs into <br>
    breaks: false,
    // CSS language prefix for fenced blocks
    langPrefix: "language-",
    // autoconvert URL-like texts to links
    linkify: false,
    // Enable some language-neutral replacements + quotes beautification
    typographer: false,
    // Double + single quotes replacement pairs, when typographer enabled,
    // and smartquotes on. Could be either a String or an Array.
    //
    // For example, you can use '«»„“' for Russian, '„“‚‘' for German,
    // and ['«\xA0', '\xA0»', '‹\xA0', '\xA0›'] for French (including nbsp).
    quotes: "“”‘’",
    /* “”‘’ */
    // Highlighter function. Should return escaped HTML,
    // or '' if the source string is not changed and should be escaped externaly.
    // If result starts with <pre... internal wrapper is skipped.
    //
    // function (/*str, lang*/) { return ''; }
    //
    highlight: null,
    // Internal protection, recursion limit
    maxNesting: 100
  },
  components: {
    core: {},
    block: {},
    inline: {}
  }
};
var cfg_zero = {
  options: {
    // Enable HTML tags in source
    html: false,
    // Use '/' to close single tags (<br />)
    xhtmlOut: false,
    // Convert '\n' in paragraphs into <br>
    breaks: false,
    // CSS language prefix for fenced blocks
    langPrefix: "language-",
    // autoconvert URL-like texts to links
    linkify: false,
    // Enable some language-neutral replacements + quotes beautification
    typographer: false,
    // Double + single quotes replacement pairs, when typographer enabled,
    // and smartquotes on. Could be either a String or an Array.
    //
    // For example, you can use '«»„“' for Russian, '„“‚‘' for German,
    // and ['«\xA0', '\xA0»', '‹\xA0', '\xA0›'] for French (including nbsp).
    quotes: "“”‘’",
    /* “”‘’ */
    // Highlighter function. Should return escaped HTML,
    // or '' if the source string is not changed and should be escaped externaly.
    // If result starts with <pre... internal wrapper is skipped.
    //
    // function (/*str, lang*/) { return ''; }
    //
    highlight: null,
    // Internal protection, recursion limit
    maxNesting: 20
  },
  components: {
    core: {
      rules: [
        "normalize",
        "block",
        "inline",
        "text_join"
      ]
    },
    block: {
      rules: [
        "paragraph"
      ]
    },
    inline: {
      rules: [
        "text"
      ],
      rules2: [
        "balance_pairs",
        "fragments_join"
      ]
    }
  }
};
var cfg_commonmark = {
  options: {
    // Enable HTML tags in source
    html: true,
    // Use '/' to close single tags (<br />)
    xhtmlOut: true,
    // Convert '\n' in paragraphs into <br>
    breaks: false,
    // CSS language prefix for fenced blocks
    langPrefix: "language-",
    // autoconvert URL-like texts to links
    linkify: false,
    // Enable some language-neutral replacements + quotes beautification
    typographer: false,
    // Double + single quotes replacement pairs, when typographer enabled,
    // and smartquotes on. Could be either a String or an Array.
    //
    // For example, you can use '«»„“' for Russian, '„“‚‘' for German,
    // and ['«\xA0', '\xA0»', '‹\xA0', '\xA0›'] for French (including nbsp).
    quotes: "“”‘’",
    /* “”‘’ */
    // Highlighter function. Should return escaped HTML,
    // or '' if the source string is not changed and should be escaped externaly.
    // If result starts with <pre... internal wrapper is skipped.
    //
    // function (/*str, lang*/) { return ''; }
    //
    highlight: null,
    // Internal protection, recursion limit
    maxNesting: 20
  },
  components: {
    core: {
      rules: [
        "normalize",
        "block",
        "inline",
        "text_join"
      ]
    },
    block: {
      rules: [
        "blockquote",
        "code",
        "fence",
        "heading",
        "hr",
        "html_block",
        "lheading",
        "list",
        "reference",
        "paragraph"
      ]
    },
    inline: {
      rules: [
        "autolink",
        "backticks",
        "emphasis",
        "entity",
        "escape",
        "html_inline",
        "image",
        "link",
        "newline",
        "text"
      ],
      rules2: [
        "balance_pairs",
        "emphasis",
        "fragments_join"
      ]
    }
  }
};
const config = {
  default: cfg_default,
  zero: cfg_zero,
  commonmark: cfg_commonmark
};
const BAD_PROTO_RE = /^(vbscript|javascript|file|data):/;
const GOOD_DATA_RE = /^data:image\/(gif|png|jpeg|webp);/;
function validateLink(url) {
  const str = url.trim().toLowerCase();
  return BAD_PROTO_RE.test(str) ? GOOD_DATA_RE.test(str) : true;
}
const RECODE_HOSTNAME_FOR = ["http:", "https:", "mailto:"];
function normalizeLink(url) {
  const parsed = index_cjsExports$2.parse(url, true);
  if (parsed.hostname) {
    if (!parsed.protocol || RECODE_HOSTNAME_FOR.indexOf(parsed.protocol) >= 0) {
      try {
        parsed.hostname = punycode.toASCII(parsed.hostname);
      } catch (er) {
      }
    }
  }
  return index_cjsExports$2.encode(index_cjsExports$2.format(parsed));
}
function normalizeLinkText(url) {
  const parsed = index_cjsExports$2.parse(url, true);
  if (parsed.hostname) {
    if (!parsed.protocol || RECODE_HOSTNAME_FOR.indexOf(parsed.protocol) >= 0) {
      try {
        parsed.hostname = punycode.toUnicode(parsed.hostname);
      } catch (er) {
      }
    }
  }
  return index_cjsExports$2.decode(index_cjsExports$2.format(parsed), index_cjsExports$2.decode.defaultChars + "%");
}
function MarkdownIt(presetName, options) {
  if (!(this instanceof MarkdownIt)) {
    return new MarkdownIt(presetName, options);
  }
  if (!options) {
    if (!isString$1(presetName)) {
      options = presetName || {};
      presetName = "default";
    }
  }
  this.inline = new ParserInline();
  this.block = new ParserBlock();
  this.core = new Core();
  this.renderer = new Renderer();
  this.linkify = new LinkifyIt();
  this.validateLink = validateLink;
  this.normalizeLink = normalizeLink;
  this.normalizeLinkText = normalizeLinkText;
  this.utils = utils;
  this.helpers = assign({}, helpers);
  this.options = {};
  this.configure(presetName);
  if (options) {
    this.set(options);
  }
}
MarkdownIt.prototype.set = function(options) {
  assign(this.options, options);
  return this;
};
MarkdownIt.prototype.configure = function(presets) {
  const self2 = this;
  if (isString$1(presets)) {
    const presetName = presets;
    presets = config[presetName];
    if (!presets) {
      throw new Error('Wrong `markdown-it` preset "' + presetName + '", check name');
    }
  }
  if (!presets) {
    throw new Error("Wrong `markdown-it` preset, can't be empty");
  }
  if (presets.options) {
    self2.set(presets.options);
  }
  if (presets.components) {
    Object.keys(presets.components).forEach(function(name) {
      if (presets.components[name].rules) {
        self2[name].ruler.enableOnly(presets.components[name].rules);
      }
      if (presets.components[name].rules2) {
        self2[name].ruler2.enableOnly(presets.components[name].rules2);
      }
    });
  }
  return this;
};
MarkdownIt.prototype.enable = function(list2, ignoreInvalid) {
  let result = [];
  if (!Array.isArray(list2)) {
    list2 = [list2];
  }
  ["core", "block", "inline"].forEach(function(chain) {
    result = result.concat(this[chain].ruler.enable(list2, true));
  }, this);
  result = result.concat(this.inline.ruler2.enable(list2, true));
  const missed = list2.filter(function(name) {
    return result.indexOf(name) < 0;
  });
  if (missed.length && !ignoreInvalid) {
    throw new Error("MarkdownIt. Failed to enable unknown rule(s): " + missed);
  }
  return this;
};
MarkdownIt.prototype.disable = function(list2, ignoreInvalid) {
  let result = [];
  if (!Array.isArray(list2)) {
    list2 = [list2];
  }
  ["core", "block", "inline"].forEach(function(chain) {
    result = result.concat(this[chain].ruler.disable(list2, true));
  }, this);
  result = result.concat(this.inline.ruler2.disable(list2, true));
  const missed = list2.filter(function(name) {
    return result.indexOf(name) < 0;
  });
  if (missed.length && !ignoreInvalid) {
    throw new Error("MarkdownIt. Failed to disable unknown rule(s): " + missed);
  }
  return this;
};
MarkdownIt.prototype.use = function(plugin) {
  const args = [this].concat(Array.prototype.slice.call(arguments, 1));
  plugin.apply(plugin, args);
  return this;
};
MarkdownIt.prototype.parse = function(src, env) {
  if (typeof src !== "string") {
    throw new Error("Input data should be a String");
  }
  const state = new this.core.State(src, this, env);
  this.core.process(state);
  return state.tokens;
};
MarkdownIt.prototype.render = function(src, env) {
  env = env || {};
  return this.renderer.render(this.parse(src, env), this.options, env);
};
MarkdownIt.prototype.parseInline = function(src, env) {
  const state = new this.core.State(src, this, env);
  state.inlineMode = true;
  this.core.process(state);
  return state.tokens;
};
MarkdownIt.prototype.renderInline = function(src, env) {
  env = env || {};
  return this.renderer.render(this.parseInline(src, env), this.options, env);
};
var prism$1 = { exports: {} };
var hasRequiredPrism;
function requirePrism() {
  if (hasRequiredPrism) return prism$1.exports;
  hasRequiredPrism = 1;
  (function(module) {
    var _self = typeof window !== "undefined" ? window : typeof WorkerGlobalScope !== "undefined" && self instanceof WorkerGlobalScope ? self : {};
    /**
     * Prism: Lightweight, robust, elegant syntax highlighting
     *
     * @license MIT <https://opensource.org/licenses/MIT>
     * @author Lea Verou <https://lea.verou.me>
     * @namespace
     * @public
     */
    var Prism2 = (function(_self2) {
      var lang = /(?:^|\s)lang(?:uage)?-([\w-]+)(?=\s|$)/i;
      var uniqueId = 0;
      var plainTextGrammar = {};
      var _2 = {
        /**
         * By default, Prism will attempt to highlight all code elements (by calling {@link Prism.highlightAll}) on the
         * current page after the page finished loading. This might be a problem if e.g. you wanted to asynchronously load
         * additional languages or plugins yourself.
         *
         * By setting this value to `true`, Prism will not automatically highlight all code elements on the page.
         *
         * You obviously have to change this value before the automatic highlighting started. To do this, you can add an
         * empty Prism object into the global scope before loading the Prism script like this:
         *
         * ```js
         * window.Prism = window.Prism || {};
         * Prism.manual = true;
         * // add a new <script> to load Prism's script
         * ```
         *
         * @default false
         * @type {boolean}
         * @memberof Prism
         * @public
         */
        manual: _self2.Prism && _self2.Prism.manual,
        /**
         * By default, if Prism is in a web worker, it assumes that it is in a worker it created itself, so it uses
         * `addEventListener` to communicate with its parent instance. However, if you're using Prism manually in your
         * own worker, you don't want it to do this.
         *
         * By setting this value to `true`, Prism will not add its own listeners to the worker.
         *
         * You obviously have to change this value before Prism executes. To do this, you can add an
         * empty Prism object into the global scope before loading the Prism script like this:
         *
         * ```js
         * window.Prism = window.Prism || {};
         * Prism.disableWorkerMessageHandler = true;
         * // Load Prism's script
         * ```
         *
         * @default false
         * @type {boolean}
         * @memberof Prism
         * @public
         */
        disableWorkerMessageHandler: _self2.Prism && _self2.Prism.disableWorkerMessageHandler,
        /**
         * A namespace for utility methods.
         *
         * All function in this namespace that are not explicitly marked as _public_ are for __internal use only__ and may
         * change or disappear at any time.
         *
         * @namespace
         * @memberof Prism
         */
        util: {
          encode: function encode2(tokens) {
            if (tokens instanceof Token2) {
              return new Token2(tokens.type, encode2(tokens.content), tokens.alias);
            } else if (Array.isArray(tokens)) {
              return tokens.map(encode2);
            } else {
              return tokens.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/\u00a0/g, " ");
            }
          },
          /**
           * Returns the name of the type of the given value.
           *
           * @param {any} o
           * @returns {string}
           * @example
           * type(null)      === 'Null'
           * type(undefined) === 'Undefined'
           * type(123)       === 'Number'
           * type('foo')     === 'String'
           * type(true)      === 'Boolean'
           * type([1, 2])    === 'Array'
           * type({})        === 'Object'
           * type(String)    === 'Function'
           * type(/abc+/)    === 'RegExp'
           */
          type: function(o2) {
            return Object.prototype.toString.call(o2).slice(8, -1);
          },
          /**
           * Returns a unique number for the given object. Later calls will still return the same number.
           *
           * @param {Object} obj
           * @returns {number}
           */
          objId: function(obj) {
            if (!obj["__id"]) {
              Object.defineProperty(obj, "__id", { value: ++uniqueId });
            }
            return obj["__id"];
          },
          /**
           * Creates a deep clone of the given object.
           *
           * The main intended use of this function is to clone language definitions.
           *
           * @param {T} o
           * @param {Record<number, any>} [visited]
           * @returns {T}
           * @template T
           */
          clone: function deepClone(o2, visited) {
            visited = visited || {};
            var clone;
            var id;
            switch (_2.util.type(o2)) {
              case "Object":
                id = _2.util.objId(o2);
                if (visited[id]) {
                  return visited[id];
                }
                clone = /** @type {Record<string, any>} */
                {};
                visited[id] = clone;
                for (var key in o2) {
                  if (o2.hasOwnProperty(key)) {
                    clone[key] = deepClone(o2[key], visited);
                  }
                }
                return (
                  /** @type {any} */
                  clone
                );
              case "Array":
                id = _2.util.objId(o2);
                if (visited[id]) {
                  return visited[id];
                }
                clone = [];
                visited[id] = clone;
                /** @type {Array} */
                /** @type {any} */
                o2.forEach(function(v2, i2) {
                  clone[i2] = deepClone(v2, visited);
                });
                return (
                  /** @type {any} */
                  clone
                );
              default:
                return o2;
            }
          },
          /**
           * Returns the Prism language of the given element set by a `language-xxxx` or `lang-xxxx` class.
           *
           * If no language is set for the element or the element is `null` or `undefined`, `none` will be returned.
           *
           * @param {Element} element
           * @returns {string}
           */
          getLanguage: function(element) {
            while (element) {
              var m2 = lang.exec(element.className);
              if (m2) {
                return m2[1].toLowerCase();
              }
              element = element.parentElement;
            }
            return "none";
          },
          /**
           * Sets the Prism `language-xxxx` class of the given element.
           *
           * @param {Element} element
           * @param {string} language
           * @returns {void}
           */
          setLanguage: function(element, language) {
            element.className = element.className.replace(RegExp(lang, "gi"), "");
            element.classList.add("language-" + language);
          },
          /**
           * Returns the script element that is currently executing.
           *
           * This does __not__ work for line script element.
           *
           * @returns {HTMLScriptElement | null}
           */
          currentScript: function() {
            if (typeof document === "undefined") {
              return null;
            }
            if (document.currentScript && document.currentScript.tagName === "SCRIPT" && 1 < 2) {
              return (
                /** @type {any} */
                document.currentScript
              );
            }
            try {
              throw new Error();
            } catch (err) {
              var src = (/at [^(\r\n]*\((.*):[^:]+:[^:]+\)$/i.exec(err.stack) || [])[1];
              if (src) {
                var scripts = document.getElementsByTagName("script");
                for (var i2 in scripts) {
                  if (scripts[i2].src == src) {
                    return scripts[i2];
                  }
                }
              }
              return null;
            }
          },
          /**
           * Returns whether a given class is active for `element`.
           *
           * The class can be activated if `element` or one of its ancestors has the given class and it can be deactivated
           * if `element` or one of its ancestors has the negated version of the given class. The _negated version_ of the
           * given class is just the given class with a `no-` prefix.
           *
           * Whether the class is active is determined by the closest ancestor of `element` (where `element` itself is
           * closest ancestor) that has the given class or the negated version of it. If neither `element` nor any of its
           * ancestors have the given class or the negated version of it, then the default activation will be returned.
           *
           * In the paradoxical situation where the closest ancestor contains __both__ the given class and the negated
           * version of it, the class is considered active.
           *
           * @param {Element} element
           * @param {string} className
           * @param {boolean} [defaultActivation=false]
           * @returns {boolean}
           */
          isActive: function(element, className, defaultActivation) {
            var no = "no-" + className;
            while (element) {
              var classList = element.classList;
              if (classList.contains(className)) {
                return true;
              }
              if (classList.contains(no)) {
                return false;
              }
              element = element.parentElement;
            }
            return !!defaultActivation;
          }
        },
        /**
         * This namespace contains all currently loaded languages and the some helper functions to create and modify languages.
         *
         * @namespace
         * @memberof Prism
         * @public
         */
        languages: {
          /**
           * The grammar for plain, unformatted text.
           */
          plain: plainTextGrammar,
          plaintext: plainTextGrammar,
          text: plainTextGrammar,
          txt: plainTextGrammar,
          /**
           * Creates a deep copy of the language with the given id and appends the given tokens.
           *
           * If a token in `redef` also appears in the copied language, then the existing token in the copied language
           * will be overwritten at its original position.
           *
           * ## Best practices
           *
           * Since the position of overwriting tokens (token in `redef` that overwrite tokens in the copied language)
           * doesn't matter, they can technically be in any order. However, this can be confusing to others that trying to
           * understand the language definition because, normally, the order of tokens matters in Prism grammars.
           *
           * Therefore, it is encouraged to order overwriting tokens according to the positions of the overwritten tokens.
           * Furthermore, all non-overwriting tokens should be placed after the overwriting ones.
           *
           * @param {string} id The id of the language to extend. This has to be a key in `Prism.languages`.
           * @param {Grammar} redef The new tokens to append.
           * @returns {Grammar} The new language created.
           * @public
           * @example
           * Prism.languages['css-with-colors'] = Prism.languages.extend('css', {
           *     // Prism.languages.css already has a 'comment' token, so this token will overwrite CSS' 'comment' token
           *     // at its original position
           *     'comment': { ... },
           *     // CSS doesn't have a 'color' token, so this token will be appended
           *     'color': /\b(?:red|green|blue)\b/
           * });
           */
          extend: function(id, redef) {
            var lang2 = _2.util.clone(_2.languages[id]);
            for (var key in redef) {
              lang2[key] = redef[key];
            }
            return lang2;
          },
          /**
           * Inserts tokens _before_ another token in a language definition or any other grammar.
           *
           * ## Usage
           *
           * This helper method makes it easy to modify existing languages. For example, the CSS language definition
           * not only defines CSS highlighting for CSS documents, but also needs to define highlighting for CSS embedded
           * in HTML through `<style>` elements. To do this, it needs to modify `Prism.languages.markup` and add the
           * appropriate tokens. However, `Prism.languages.markup` is a regular JavaScript object literal, so if you do
           * this:
           *
           * ```js
           * Prism.languages.markup.style = {
           *     // token
           * };
           * ```
           *
           * then the `style` token will be added (and processed) at the end. `insertBefore` allows you to insert tokens
           * before existing tokens. For the CSS example above, you would use it like this:
           *
           * ```js
           * Prism.languages.insertBefore('markup', 'cdata', {
           *     'style': {
           *         // token
           *     }
           * });
           * ```
           *
           * ## Special cases
           *
           * If the grammars of `inside` and `insert` have tokens with the same name, the tokens in `inside`'s grammar
           * will be ignored.
           *
           * This behavior can be used to insert tokens after `before`:
           *
           * ```js
           * Prism.languages.insertBefore('markup', 'comment', {
           *     'comment': Prism.languages.markup.comment,
           *     // tokens after 'comment'
           * });
           * ```
           *
           * ## Limitations
           *
           * The main problem `insertBefore` has to solve is iteration order. Since ES2015, the iteration order for object
           * properties is guaranteed to be the insertion order (except for integer keys) but some browsers behave
           * differently when keys are deleted and re-inserted. So `insertBefore` can't be implemented by temporarily
           * deleting properties which is necessary to insert at arbitrary positions.
           *
           * To solve this problem, `insertBefore` doesn't actually insert the given tokens into the target object.
           * Instead, it will create a new object and replace all references to the target object with the new one. This
           * can be done without temporarily deleting properties, so the iteration order is well-defined.
           *
           * However, only references that can be reached from `Prism.languages` or `insert` will be replaced. I.e. if
           * you hold the target object in a variable, then the value of the variable will not change.
           *
           * ```js
           * var oldMarkup = Prism.languages.markup;
           * var newMarkup = Prism.languages.insertBefore('markup', 'comment', { ... });
           *
           * assert(oldMarkup !== Prism.languages.markup);
           * assert(newMarkup === Prism.languages.markup);
           * ```
           *
           * @param {string} inside The property of `root` (e.g. a language id in `Prism.languages`) that contains the
           * object to be modified.
           * @param {string} before The key to insert before.
           * @param {Grammar} insert An object containing the key-value pairs to be inserted.
           * @param {Object<string, any>} [root] The object containing `inside`, i.e. the object that contains the
           * object to be modified.
           *
           * Defaults to `Prism.languages`.
           * @returns {Grammar} The new grammar object.
           * @public
           */
          insertBefore: function(inside, before, insert, root) {
            root = root || /** @type {any} */
            _2.languages;
            var grammar = root[inside];
            var ret = {};
            for (var token in grammar) {
              if (grammar.hasOwnProperty(token)) {
                if (token == before) {
                  for (var newToken in insert) {
                    if (insert.hasOwnProperty(newToken)) {
                      ret[newToken] = insert[newToken];
                    }
                  }
                }
                if (!insert.hasOwnProperty(token)) {
                  ret[token] = grammar[token];
                }
              }
            }
            var old = root[inside];
            root[inside] = ret;
            _2.languages.DFS(_2.languages, function(key, value) {
              if (value === old && key != inside) {
                this[key] = ret;
              }
            });
            return ret;
          },
          // Traverse a language definition with Depth First Search
          DFS: function DFS(o2, callback, type, visited) {
            visited = visited || {};
            var objId = _2.util.objId;
            for (var i2 in o2) {
              if (o2.hasOwnProperty(i2)) {
                callback.call(o2, i2, o2[i2], type || i2);
                var property = o2[i2];
                var propertyType = _2.util.type(property);
                if (propertyType === "Object" && !visited[objId(property)]) {
                  visited[objId(property)] = true;
                  DFS(property, callback, null, visited);
                } else if (propertyType === "Array" && !visited[objId(property)]) {
                  visited[objId(property)] = true;
                  DFS(property, callback, i2, visited);
                }
              }
            }
          }
        },
        plugins: {},
        /**
         * This is the most high-level function in Prism’s API.
         * It fetches all the elements that have a `.language-xxxx` class and then calls {@link Prism.highlightElement} on
         * each one of them.
         *
         * This is equivalent to `Prism.highlightAllUnder(document, async, callback)`.
         *
         * @param {boolean} [async=false] Same as in {@link Prism.highlightAllUnder}.
         * @param {HighlightCallback} [callback] Same as in {@link Prism.highlightAllUnder}.
         * @memberof Prism
         * @public
         */
        highlightAll: function(async, callback) {
          _2.highlightAllUnder(document, async, callback);
        },
        /**
         * Fetches all the descendants of `container` that have a `.language-xxxx` class and then calls
         * {@link Prism.highlightElement} on each one of them.
         *
         * The following hooks will be run:
         * 1. `before-highlightall`
         * 2. `before-all-elements-highlight`
         * 3. All hooks of {@link Prism.highlightElement} for each element.
         *
         * @param {ParentNode} container The root element, whose descendants that have a `.language-xxxx` class will be highlighted.
         * @param {boolean} [async=false] Whether each element is to be highlighted asynchronously using Web Workers.
         * @param {HighlightCallback} [callback] An optional callback to be invoked on each element after its highlighting is done.
         * @memberof Prism
         * @public
         */
        highlightAllUnder: function(container, async, callback) {
          var env = {
            callback,
            container,
            selector: 'code[class*="language-"], [class*="language-"] code, code[class*="lang-"], [class*="lang-"] code'
          };
          _2.hooks.run("before-highlightall", env);
          env.elements = Array.prototype.slice.apply(env.container.querySelectorAll(env.selector));
          _2.hooks.run("before-all-elements-highlight", env);
          for (var i2 = 0, element; element = env.elements[i2++]; ) {
            _2.highlightElement(element, async === true, env.callback);
          }
        },
        /**
         * Highlights the code inside a single element.
         *
         * The following hooks will be run:
         * 1. `before-sanity-check`
         * 2. `before-highlight`
         * 3. All hooks of {@link Prism.highlight}. These hooks will be run by an asynchronous worker if `async` is `true`.
         * 4. `before-insert`
         * 5. `after-highlight`
         * 6. `complete`
         *
         * Some the above hooks will be skipped if the element doesn't contain any text or there is no grammar loaded for
         * the element's language.
         *
         * @param {Element} element The element containing the code.
         * It must have a class of `language-xxxx` to be processed, where `xxxx` is a valid language identifier.
         * @param {boolean} [async=false] Whether the element is to be highlighted asynchronously using Web Workers
         * to improve performance and avoid blocking the UI when highlighting very large chunks of code. This option is
         * [disabled by default](https://prismjs.com/faq.html#why-is-asynchronous-highlighting-disabled-by-default).
         *
         * Note: All language definitions required to highlight the code must be included in the main `prism.js` file for
         * asynchronous highlighting to work. You can build your own bundle on the
         * [Download page](https://prismjs.com/download.html).
         * @param {HighlightCallback} [callback] An optional callback to be invoked after the highlighting is done.
         * Mostly useful when `async` is `true`, since in that case, the highlighting is done asynchronously.
         * @memberof Prism
         * @public
         */
        highlightElement: function(element, async, callback) {
          var language = _2.util.getLanguage(element);
          var grammar = _2.languages[language];
          _2.util.setLanguage(element, language);
          var parent = element.parentElement;
          if (parent && parent.nodeName.toLowerCase() === "pre") {
            _2.util.setLanguage(parent, language);
          }
          var code2 = element.textContent;
          var env = {
            element,
            language,
            grammar,
            code: code2
          };
          function insertHighlightedCode(highlightedCode) {
            env.highlightedCode = highlightedCode;
            _2.hooks.run("before-insert", env);
            env.element.innerHTML = env.highlightedCode;
            _2.hooks.run("after-highlight", env);
            _2.hooks.run("complete", env);
            callback && callback.call(env.element);
          }
          _2.hooks.run("before-sanity-check", env);
          parent = env.element.parentElement;
          if (parent && parent.nodeName.toLowerCase() === "pre" && !parent.hasAttribute("tabindex")) {
            parent.setAttribute("tabindex", "0");
          }
          if (!env.code) {
            _2.hooks.run("complete", env);
            callback && callback.call(env.element);
            return;
          }
          _2.hooks.run("before-highlight", env);
          if (!env.grammar) {
            insertHighlightedCode(_2.util.encode(env.code));
            return;
          }
          if (async && _self2.Worker) {
            var worker = new Worker(_2.filename);
            worker.onmessage = function(evt) {
              insertHighlightedCode(evt.data);
            };
            worker.postMessage(JSON.stringify({
              language: env.language,
              code: env.code,
              immediateClose: true
            }));
          } else {
            insertHighlightedCode(_2.highlight(env.code, env.grammar, env.language));
          }
        },
        /**
         * Low-level function, only use if you know what you’re doing. It accepts a string of text as input
         * and the language definitions to use, and returns a string with the HTML produced.
         *
         * The following hooks will be run:
         * 1. `before-tokenize`
         * 2. `after-tokenize`
         * 3. `wrap`: On each {@link Token}.
         *
         * @param {string} text A string with the code to be highlighted.
         * @param {Grammar} grammar An object containing the tokens to use.
         *
         * Usually a language definition like `Prism.languages.markup`.
         * @param {string} language The name of the language definition passed to `grammar`.
         * @returns {string} The highlighted HTML.
         * @memberof Prism
         * @public
         * @example
         * Prism.highlight('var foo = true;', Prism.languages.javascript, 'javascript');
         */
        highlight: function(text2, grammar, language) {
          var env = {
            code: text2,
            grammar,
            language
          };
          _2.hooks.run("before-tokenize", env);
          if (!env.grammar) {
            throw new Error('The language "' + env.language + '" has no grammar.');
          }
          env.tokens = _2.tokenize(env.code, env.grammar);
          _2.hooks.run("after-tokenize", env);
          return Token2.stringify(_2.util.encode(env.tokens), env.language);
        },
        /**
         * This is the heart of Prism, and the most low-level function you can use. It accepts a string of text as input
         * and the language definitions to use, and returns an array with the tokenized code.
         *
         * When the language definition includes nested tokens, the function is called recursively on each of these tokens.
         *
         * This method could be useful in other contexts as well, as a very crude parser.
         *
         * @param {string} text A string with the code to be highlighted.
         * @param {Grammar} grammar An object containing the tokens to use.
         *
         * Usually a language definition like `Prism.languages.markup`.
         * @returns {TokenStream} An array of strings and tokens, a token stream.
         * @memberof Prism
         * @public
         * @example
         * let code = `var foo = 0;`;
         * let tokens = Prism.tokenize(code, Prism.languages.javascript);
         * tokens.forEach(token => {
         *     if (token instanceof Prism.Token && token.type === 'number') {
         *         console.log(`Found numeric literal: ${token.content}`);
         *     }
         * });
         */
        tokenize: function(text2, grammar) {
          var rest = grammar.rest;
          if (rest) {
            for (var token in rest) {
              grammar[token] = rest[token];
            }
            delete grammar.rest;
          }
          var tokenList = new LinkedList();
          addAfter(tokenList, tokenList.head, text2);
          matchGrammar(text2, tokenList, grammar, tokenList.head, 0);
          return toArray(tokenList);
        },
        /**
         * @namespace
         * @memberof Prism
         * @public
         */
        hooks: {
          all: {},
          /**
           * Adds the given callback to the list of callbacks for the given hook.
           *
           * The callback will be invoked when the hook it is registered for is run.
           * Hooks are usually directly run by a highlight function but you can also run hooks yourself.
           *
           * One callback function can be registered to multiple hooks and the same hook multiple times.
           *
           * @param {string} name The name of the hook.
           * @param {HookCallback} callback The callback function which is given environment variables.
           * @public
           */
          add: function(name, callback) {
            var hooks = _2.hooks.all;
            hooks[name] = hooks[name] || [];
            hooks[name].push(callback);
          },
          /**
           * Runs a hook invoking all registered callbacks with the given environment variables.
           *
           * Callbacks will be invoked synchronously and in the order in which they were registered.
           *
           * @param {string} name The name of the hook.
           * @param {Object<string, any>} env The environment variables of the hook passed to all callbacks registered.
           * @public
           */
          run: function(name, env) {
            var callbacks = _2.hooks.all[name];
            if (!callbacks || !callbacks.length) {
              return;
            }
            for (var i2 = 0, callback; callback = callbacks[i2++]; ) {
              callback(env);
            }
          }
        },
        Token: Token2
      };
      _self2.Prism = _2;
      function Token2(type, content, alias, matchedStr) {
        this.type = type;
        this.content = content;
        this.alias = alias;
        this.length = (matchedStr || "").length | 0;
      }
      Token2.stringify = function stringify(o2, language) {
        if (typeof o2 == "string") {
          return o2;
        }
        if (Array.isArray(o2)) {
          var s2 = "";
          o2.forEach(function(e2) {
            s2 += stringify(e2, language);
          });
          return s2;
        }
        var env = {
          type: o2.type,
          content: stringify(o2.content, language),
          tag: "span",
          classes: ["token", o2.type],
          attributes: {},
          language
        };
        var aliases = o2.alias;
        if (aliases) {
          if (Array.isArray(aliases)) {
            Array.prototype.push.apply(env.classes, aliases);
          } else {
            env.classes.push(aliases);
          }
        }
        _2.hooks.run("wrap", env);
        var attributes = "";
        for (var name in env.attributes) {
          attributes += " " + name + '="' + (env.attributes[name] || "").replace(/"/g, "&quot;") + '"';
        }
        return "<" + env.tag + ' class="' + env.classes.join(" ") + '"' + attributes + ">" + env.content + "</" + env.tag + ">";
      };
      function matchPattern(pattern, pos, text2, lookbehind) {
        pattern.lastIndex = pos;
        var match = pattern.exec(text2);
        if (match && lookbehind && match[1]) {
          var lookbehindLength = match[1].length;
          match.index += lookbehindLength;
          match[0] = match[0].slice(lookbehindLength);
        }
        return match;
      }
      function matchGrammar(text2, tokenList, grammar, startNode, startPos, rematch) {
        for (var token in grammar) {
          if (!grammar.hasOwnProperty(token) || !grammar[token]) {
            continue;
          }
          var patterns = grammar[token];
          patterns = Array.isArray(patterns) ? patterns : [patterns];
          for (var j2 = 0; j2 < patterns.length; ++j2) {
            if (rematch && rematch.cause == token + "," + j2) {
              return;
            }
            var patternObj = patterns[j2];
            var inside = patternObj.inside;
            var lookbehind = !!patternObj.lookbehind;
            var greedy = !!patternObj.greedy;
            var alias = patternObj.alias;
            if (greedy && !patternObj.pattern.global) {
              var flags = patternObj.pattern.toString().match(/[imsuy]*$/)[0];
              patternObj.pattern = RegExp(patternObj.pattern.source, flags + "g");
            }
            var pattern = patternObj.pattern || patternObj;
            for (var currentNode = startNode.next, pos = startPos; currentNode !== tokenList.tail; pos += currentNode.value.length, currentNode = currentNode.next) {
              if (rematch && pos >= rematch.reach) {
                break;
              }
              var str = currentNode.value;
              if (tokenList.length > text2.length) {
                return;
              }
              if (str instanceof Token2) {
                continue;
              }
              var removeCount = 1;
              var match;
              if (greedy) {
                match = matchPattern(pattern, pos, text2, lookbehind);
                if (!match || match.index >= text2.length) {
                  break;
                }
                var from = match.index;
                var to = match.index + match[0].length;
                var p2 = pos;
                p2 += currentNode.value.length;
                while (from >= p2) {
                  currentNode = currentNode.next;
                  p2 += currentNode.value.length;
                }
                p2 -= currentNode.value.length;
                pos = p2;
                if (currentNode.value instanceof Token2) {
                  continue;
                }
                for (var k2 = currentNode; k2 !== tokenList.tail && (p2 < to || typeof k2.value === "string"); k2 = k2.next) {
                  removeCount++;
                  p2 += k2.value.length;
                }
                removeCount--;
                str = text2.slice(pos, p2);
                match.index -= pos;
              } else {
                match = matchPattern(pattern, 0, str, lookbehind);
                if (!match) {
                  continue;
                }
              }
              var from = match.index;
              var matchStr = match[0];
              var before = str.slice(0, from);
              var after = str.slice(from + matchStr.length);
              var reach = pos + str.length;
              if (rematch && reach > rematch.reach) {
                rematch.reach = reach;
              }
              var removeFrom = currentNode.prev;
              if (before) {
                removeFrom = addAfter(tokenList, removeFrom, before);
                pos += before.length;
              }
              removeRange(tokenList, removeFrom, removeCount);
              var wrapped = new Token2(token, inside ? _2.tokenize(matchStr, inside) : matchStr, alias, matchStr);
              currentNode = addAfter(tokenList, removeFrom, wrapped);
              if (after) {
                addAfter(tokenList, currentNode, after);
              }
              if (removeCount > 1) {
                var nestedRematch = {
                  cause: token + "," + j2,
                  reach
                };
                matchGrammar(text2, tokenList, grammar, currentNode.prev, pos, nestedRematch);
                if (rematch && nestedRematch.reach > rematch.reach) {
                  rematch.reach = nestedRematch.reach;
                }
              }
            }
          }
        }
      }
      function LinkedList() {
        var head = { value: null, prev: null, next: null };
        var tail = { value: null, prev: head, next: null };
        head.next = tail;
        this.head = head;
        this.tail = tail;
        this.length = 0;
      }
      function addAfter(list2, node, value) {
        var next = node.next;
        var newNode = { value, prev: node, next };
        node.next = newNode;
        next.prev = newNode;
        list2.length++;
        return newNode;
      }
      function removeRange(list2, node, count) {
        var next = node.next;
        for (var i2 = 0; i2 < count && next !== list2.tail; i2++) {
          next = next.next;
        }
        node.next = next;
        next.prev = node;
        list2.length -= i2;
      }
      function toArray(list2) {
        var array = [];
        var node = list2.head.next;
        while (node !== list2.tail) {
          array.push(node.value);
          node = node.next;
        }
        return array;
      }
      if (!_self2.document) {
        if (!_self2.addEventListener) {
          return _2;
        }
        if (!_2.disableWorkerMessageHandler) {
          _self2.addEventListener("message", function(evt) {
            var message = JSON.parse(evt.data);
            var lang2 = message.language;
            var code2 = message.code;
            var immediateClose = message.immediateClose;
            _self2.postMessage(_2.highlight(code2, _2.languages[lang2], lang2));
            if (immediateClose) {
              _self2.close();
            }
          }, false);
        }
        return _2;
      }
      var script = _2.util.currentScript();
      if (script) {
        _2.filename = script.src;
        if (script.hasAttribute("data-manual")) {
          _2.manual = true;
        }
      }
      function highlightAutomaticallyCallback() {
        if (!_2.manual) {
          _2.highlightAll();
        }
      }
      if (!_2.manual) {
        var readyState = document.readyState;
        if (readyState === "loading" || readyState === "interactive" && script && script.defer) {
          document.addEventListener("DOMContentLoaded", highlightAutomaticallyCallback);
        } else {
          if (window.requestAnimationFrame) {
            window.requestAnimationFrame(highlightAutomaticallyCallback);
          } else {
            window.setTimeout(highlightAutomaticallyCallback, 16);
          }
        }
      }
      return _2;
    })(_self);
    if (module.exports) {
      module.exports = Prism2;
    }
    if (typeof commonjsGlobal !== "undefined") {
      commonjsGlobal.Prism = Prism2;
    }
    Prism2.languages.markup = {
      "comment": {
        pattern: /<!--(?:(?!<!--)[\s\S])*?-->/,
        greedy: true
      },
      "prolog": {
        pattern: /<\?[\s\S]+?\?>/,
        greedy: true
      },
      "doctype": {
        // https://www.w3.org/TR/xml/#NT-doctypedecl
        pattern: /<!DOCTYPE(?:[^>"'[\]]|"[^"]*"|'[^']*')+(?:\[(?:[^<"'\]]|"[^"]*"|'[^']*'|<(?!!--)|<!--(?:[^-]|-(?!->))*-->)*\]\s*)?>/i,
        greedy: true,
        inside: {
          "internal-subset": {
            pattern: /(^[^\[]*\[)[\s\S]+(?=\]>$)/,
            lookbehind: true,
            greedy: true,
            inside: null
            // see below
          },
          "string": {
            pattern: /"[^"]*"|'[^']*'/,
            greedy: true
          },
          "punctuation": /^<!|>$|[[\]]/,
          "doctype-tag": /^DOCTYPE/i,
          "name": /[^\s<>'"]+/
        }
      },
      "cdata": {
        pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
        greedy: true
      },
      "tag": {
        pattern: /<\/?(?!\d)[^\s>\/=$<%]+(?:\s(?:\s*[^\s>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))|(?=[\s/>])))+)?\s*\/?>/,
        greedy: true,
        inside: {
          "tag": {
            pattern: /^<\/?[^\s>\/]+/,
            inside: {
              "punctuation": /^<\/?/,
              "namespace": /^[^\s>\/:]+:/
            }
          },
          "special-attr": [],
          "attr-value": {
            pattern: /=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+)/,
            inside: {
              "punctuation": [
                {
                  pattern: /^=/,
                  alias: "attr-equals"
                },
                {
                  pattern: /^(\s*)["']|["']$/,
                  lookbehind: true
                }
              ]
            }
          },
          "punctuation": /\/?>/,
          "attr-name": {
            pattern: /[^\s>\/]+/,
            inside: {
              "namespace": /^[^\s>\/:]+:/
            }
          }
        }
      },
      "entity": [
        {
          pattern: /&[\da-z]{1,8};/i,
          alias: "named-entity"
        },
        /&#x?[\da-f]{1,8};/i
      ]
    };
    Prism2.languages.markup["tag"].inside["attr-value"].inside["entity"] = Prism2.languages.markup["entity"];
    Prism2.languages.markup["doctype"].inside["internal-subset"].inside = Prism2.languages.markup;
    Prism2.hooks.add("wrap", function(env) {
      if (env.type === "entity") {
        env.attributes["title"] = env.content.replace(/&amp;/, "&");
      }
    });
    Object.defineProperty(Prism2.languages.markup.tag, "addInlined", {
      /**
       * Adds an inlined language to markup.
       *
       * An example of an inlined language is CSS with `<style>` tags.
       *
       * @param {string} tagName The name of the tag that contains the inlined language. This name will be treated as
       * case insensitive.
       * @param {string} lang The language key.
       * @example
       * addInlined('style', 'css');
       */
      value: function addInlined(tagName, lang) {
        var includedCdataInside = {};
        includedCdataInside["language-" + lang] = {
          pattern: /(^<!\[CDATA\[)[\s\S]+?(?=\]\]>$)/i,
          lookbehind: true,
          inside: Prism2.languages[lang]
        };
        includedCdataInside["cdata"] = /^<!\[CDATA\[|\]\]>$/i;
        var inside = {
          "included-cdata": {
            pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
            inside: includedCdataInside
          }
        };
        inside["language-" + lang] = {
          pattern: /[\s\S]+/,
          inside: Prism2.languages[lang]
        };
        var def = {};
        def[tagName] = {
          pattern: RegExp(/(<__[^>]*>)(?:<!\[CDATA\[(?:[^\]]|\](?!\]>))*\]\]>|(?!<!\[CDATA\[)[\s\S])*?(?=<\/__>)/.source.replace(/__/g, function() {
            return tagName;
          }), "i"),
          lookbehind: true,
          greedy: true,
          inside
        };
        Prism2.languages.insertBefore("markup", "cdata", def);
      }
    });
    Object.defineProperty(Prism2.languages.markup.tag, "addAttribute", {
      /**
       * Adds an pattern to highlight languages embedded in HTML attributes.
       *
       * An example of an inlined language is CSS with `style` attributes.
       *
       * @param {string} attrName The name of the tag that contains the inlined language. This name will be treated as
       * case insensitive.
       * @param {string} lang The language key.
       * @example
       * addAttribute('style', 'css');
       */
      value: function(attrName, lang) {
        Prism2.languages.markup.tag.inside["special-attr"].push({
          pattern: RegExp(
            /(^|["'\s])/.source + "(?:" + attrName + ")" + /\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))/.source,
            "i"
          ),
          lookbehind: true,
          inside: {
            "attr-name": /^[^\s=]+/,
            "attr-value": {
              pattern: /=[\s\S]+/,
              inside: {
                "value": {
                  pattern: /(^=\s*(["']|(?!["'])))\S[\s\S]*(?=\2$)/,
                  lookbehind: true,
                  alias: [lang, "language-" + lang],
                  inside: Prism2.languages[lang]
                },
                "punctuation": [
                  {
                    pattern: /^=/,
                    alias: "attr-equals"
                  },
                  /"|'/
                ]
              }
            }
          }
        });
      }
    });
    Prism2.languages.html = Prism2.languages.markup;
    Prism2.languages.mathml = Prism2.languages.markup;
    Prism2.languages.svg = Prism2.languages.markup;
    Prism2.languages.xml = Prism2.languages.extend("markup", {});
    Prism2.languages.ssml = Prism2.languages.xml;
    Prism2.languages.atom = Prism2.languages.xml;
    Prism2.languages.rss = Prism2.languages.xml;
    (function(Prism3) {
      var string = /(?:"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"|'(?:\\(?:\r\n|[\s\S])|[^'\\\r\n])*')/;
      Prism3.languages.css = {
        "comment": /\/\*[\s\S]*?\*\//,
        "atrule": {
          pattern: RegExp("@[\\w-](?:" + /[^;{\s"']|\s+(?!\s)/.source + "|" + string.source + ")*?" + /(?:;|(?=\s*\{))/.source),
          inside: {
            "rule": /^@[\w-]+/,
            "selector-function-argument": {
              pattern: /(\bselector\s*\(\s*(?![\s)]))(?:[^()\s]|\s+(?![\s)])|\((?:[^()]|\([^()]*\))*\))+(?=\s*\))/,
              lookbehind: true,
              alias: "selector"
            },
            "keyword": {
              pattern: /(^|[^\w-])(?:and|not|only|or)(?![\w-])/,
              lookbehind: true
            }
            // See rest below
          }
        },
        "url": {
          // https://drafts.csswg.org/css-values-3/#urls
          pattern: RegExp("\\burl\\((?:" + string.source + "|" + /(?:[^\\\r\n()"']|\\[\s\S])*/.source + ")\\)", "i"),
          greedy: true,
          inside: {
            "function": /^url/i,
            "punctuation": /^\(|\)$/,
            "string": {
              pattern: RegExp("^" + string.source + "$"),
              alias: "url"
            }
          }
        },
        "selector": {
          pattern: RegExp(`(^|[{}\\s])[^{}\\s](?:[^{};"'\\s]|\\s+(?![\\s{])|` + string.source + ")*(?=\\s*\\{)"),
          lookbehind: true
        },
        "string": {
          pattern: string,
          greedy: true
        },
        "property": {
          pattern: /(^|[^-\w\xA0-\uFFFF])(?!\s)[-_a-z\xA0-\uFFFF](?:(?!\s)[-\w\xA0-\uFFFF])*(?=\s*:)/i,
          lookbehind: true
        },
        "important": /!important\b/i,
        "function": {
          pattern: /(^|[^-a-z0-9])[-a-z0-9]+(?=\()/i,
          lookbehind: true
        },
        "punctuation": /[(){};:,]/
      };
      Prism3.languages.css["atrule"].inside.rest = Prism3.languages.css;
      var markup = Prism3.languages.markup;
      if (markup) {
        markup.tag.addInlined("style", "css");
        markup.tag.addAttribute("style", "css");
      }
    })(Prism2);
    Prism2.languages.clike = {
      "comment": [
        {
          pattern: /(^|[^\\])\/\*[\s\S]*?(?:\*\/|$)/,
          lookbehind: true,
          greedy: true
        },
        {
          pattern: /(^|[^\\:])\/\/.*/,
          lookbehind: true,
          greedy: true
        }
      ],
      "string": {
        pattern: /(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
        greedy: true
      },
      "class-name": {
        pattern: /(\b(?:class|extends|implements|instanceof|interface|new|trait)\s+|\bcatch\s+\()[\w.\\]+/i,
        lookbehind: true,
        inside: {
          "punctuation": /[.\\]/
        }
      },
      "keyword": /\b(?:break|catch|continue|do|else|finally|for|function|if|in|instanceof|new|null|return|throw|try|while)\b/,
      "boolean": /\b(?:false|true)\b/,
      "function": /\b\w+(?=\()/,
      "number": /\b0x[\da-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?/i,
      "operator": /[<>]=?|[!=]=?=?|--?|\+\+?|&&?|\|\|?|[?*/~^%]/,
      "punctuation": /[{}[\];(),.:]/
    };
    Prism2.languages.javascript = Prism2.languages.extend("clike", {
      "class-name": [
        Prism2.languages.clike["class-name"],
        {
          pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$A-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\.(?:constructor|prototype))/,
          lookbehind: true
        }
      ],
      "keyword": [
        {
          pattern: /((?:^|\})\s*)catch\b/,
          lookbehind: true
        },
        {
          pattern: /(^|[^.]|\.\.\.\s*)\b(?:as|assert(?=\s*\{)|async(?=\s*(?:function\b|\(|[$\w\xA0-\uFFFF]|$))|await|break|case|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally(?=\s*(?:\{|$))|for|from(?=\s*(?:['"]|$))|function|(?:get|set)(?=\s*(?:[#\[$\w\xA0-\uFFFF]|$))|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)\b/,
          lookbehind: true
        }
      ],
      // Allow for all non-ASCII characters (See http://stackoverflow.com/a/2008444)
      "function": /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*(?:\.\s*(?:apply|bind|call)\s*)?\()/,
      "number": {
        pattern: RegExp(
          /(^|[^\w$])/.source + "(?:" + // constant
          (/NaN|Infinity/.source + "|" + // binary integer
          /0[bB][01]+(?:_[01]+)*n?/.source + "|" + // octal integer
          /0[oO][0-7]+(?:_[0-7]+)*n?/.source + "|" + // hexadecimal integer
          /0[xX][\dA-Fa-f]+(?:_[\dA-Fa-f]+)*n?/.source + "|" + // decimal bigint
          /\d+(?:_\d+)*n/.source + "|" + // decimal number (integer or float) but no bigint
          /(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[Ee][+-]?\d+(?:_\d+)*)?/.source) + ")" + /(?![\w$])/.source
        ),
        lookbehind: true
      },
      "operator": /--|\+\+|\*\*=?|=>|&&=?|\|\|=?|[!=]==|<<=?|>>>?=?|[-+*/%&|^!=<>]=?|\.{3}|\?\?=?|\?\.?|[~:]/
    });
    Prism2.languages.javascript["class-name"][0].pattern = /(\b(?:class|extends|implements|instanceof|interface|new)\s+)[\w.\\]+/;
    Prism2.languages.insertBefore("javascript", "keyword", {
      "regex": {
        pattern: RegExp(
          // lookbehind
          // eslint-disable-next-line regexp/no-dupe-characters-character-class
          /((?:^|[^$\w\xA0-\uFFFF."'\])\s]|\b(?:return|yield))\s*)/.source + // Regex pattern:
          // There are 2 regex patterns here. The RegExp set notation proposal added support for nested character
          // classes if the `v` flag is present. Unfortunately, nested CCs are both context-free and incompatible
          // with the only syntax, so we have to define 2 different regex patterns.
          /\//.source + "(?:" + /(?:\[(?:[^\]\\\r\n]|\\.)*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}/.source + "|" + // `v` flag syntax. This supports 3 levels of nested character classes.
          /(?:\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.)*\])*\])*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}v[dgimyus]{0,7}/.source + ")" + // lookahead
          /(?=(?:\s|\/\*(?:[^*]|\*(?!\/))*\*\/)*(?:$|[\r\n,.;:})\]]|\/\/))/.source
        ),
        lookbehind: true,
        greedy: true,
        inside: {
          "regex-source": {
            pattern: /^(\/)[\s\S]+(?=\/[a-z]*$)/,
            lookbehind: true,
            alias: "language-regex",
            inside: Prism2.languages.regex
          },
          "regex-delimiter": /^\/|\/$/,
          "regex-flags": /^[a-z]+$/
        }
      },
      // This must be declared before keyword because we use "function" inside the look-forward
      "function-variable": {
        pattern: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*[=:]\s*(?:async\s*)?(?:\bfunction\b|(?:\((?:[^()]|\([^()]*\))*\)|(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)\s*=>))/,
        alias: "function"
      },
      "parameter": [
        {
          pattern: /(function(?:\s+(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)?\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\))/,
          lookbehind: true,
          inside: Prism2.languages.javascript
        },
        {
          pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*=>)/i,
          lookbehind: true,
          inside: Prism2.languages.javascript
        },
        {
          pattern: /(\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*=>)/,
          lookbehind: true,
          inside: Prism2.languages.javascript
        },
        {
          pattern: /((?:\b|\s|^)(?!(?:as|async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)(?![$\w\xA0-\uFFFF]))(?:(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*)\(\s*|\]\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*\{)/,
          lookbehind: true,
          inside: Prism2.languages.javascript
        }
      ],
      "constant": /\b[A-Z](?:[A-Z_]|\dx?)*\b/
    });
    Prism2.languages.insertBefore("javascript", "string", {
      "hashbang": {
        pattern: /^#!.*/,
        greedy: true,
        alias: "comment"
      },
      "template-string": {
        pattern: /`(?:\\[\s\S]|\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}|(?!\$\{)[^\\`])*`/,
        greedy: true,
        inside: {
          "template-punctuation": {
            pattern: /^`|`$/,
            alias: "string"
          },
          "interpolation": {
            pattern: /((?:^|[^\\])(?:\\{2})*)\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}/,
            lookbehind: true,
            inside: {
              "interpolation-punctuation": {
                pattern: /^\$\{|\}$/,
                alias: "punctuation"
              },
              rest: Prism2.languages.javascript
            }
          },
          "string": /[\s\S]+/
        }
      },
      "string-property": {
        pattern: /((?:^|[,{])[ \t]*)(["'])(?:\\(?:\r\n|[\s\S])|(?!\2)[^\\\r\n])*\2(?=\s*:)/m,
        lookbehind: true,
        greedy: true,
        alias: "property"
      }
    });
    Prism2.languages.insertBefore("javascript", "operator", {
      "literal-property": {
        pattern: /((?:^|[,{])[ \t]*)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*:)/m,
        lookbehind: true,
        alias: "property"
      }
    });
    if (Prism2.languages.markup) {
      Prism2.languages.markup.tag.addInlined("script", "javascript");
      Prism2.languages.markup.tag.addAttribute(
        /on(?:abort|blur|change|click|composition(?:end|start|update)|dblclick|error|focus(?:in|out)?|key(?:down|up)|load|mouse(?:down|enter|leave|move|out|over|up)|reset|resize|scroll|select|slotchange|submit|unload|wheel)/.source,
        "javascript"
      );
    }
    Prism2.languages.js = Prism2.languages.javascript;
    (function() {
      if (typeof Prism2 === "undefined" || typeof document === "undefined") {
        return;
      }
      if (!Element.prototype.matches) {
        Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
      }
      var LOADING_MESSAGE = "Loading…";
      var FAILURE_MESSAGE = function(status, message) {
        return "✖ Error " + status + " while fetching file: " + message;
      };
      var FAILURE_EMPTY_MESSAGE = "✖ Error: File does not exist or is empty";
      var EXTENSIONS = {
        "js": "javascript",
        "py": "python",
        "rb": "ruby",
        "ps1": "powershell",
        "psm1": "powershell",
        "sh": "bash",
        "bat": "batch",
        "h": "c",
        "tex": "latex"
      };
      var STATUS_ATTR = "data-src-status";
      var STATUS_LOADING = "loading";
      var STATUS_LOADED = "loaded";
      var STATUS_FAILED = "failed";
      var SELECTOR = "pre[data-src]:not([" + STATUS_ATTR + '="' + STATUS_LOADED + '"]):not([' + STATUS_ATTR + '="' + STATUS_LOADING + '"])';
      function loadFile(src, success, error2) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", src, true);
        xhr.onreadystatechange = function() {
          if (xhr.readyState == 4) {
            if (xhr.status < 400 && xhr.responseText) {
              success(xhr.responseText);
            } else {
              if (xhr.status >= 400) {
                error2(FAILURE_MESSAGE(xhr.status, xhr.statusText));
              } else {
                error2(FAILURE_EMPTY_MESSAGE);
              }
            }
          }
        };
        xhr.send(null);
      }
      function parseRange(range) {
        var m2 = /^\s*(\d+)\s*(?:(,)\s*(?:(\d+)\s*)?)?$/.exec(range || "");
        if (m2) {
          var start = Number(m2[1]);
          var comma = m2[2];
          var end = m2[3];
          if (!comma) {
            return [start, start];
          }
          if (!end) {
            return [start, void 0];
          }
          return [start, Number(end)];
        }
        return void 0;
      }
      Prism2.hooks.add("before-highlightall", function(env) {
        env.selector += ", " + SELECTOR;
      });
      Prism2.hooks.add("before-sanity-check", function(env) {
        var pre = (
          /** @type {HTMLPreElement} */
          env.element
        );
        if (pre.matches(SELECTOR)) {
          env.code = "";
          pre.setAttribute(STATUS_ATTR, STATUS_LOADING);
          var code2 = pre.appendChild(document.createElement("CODE"));
          code2.textContent = LOADING_MESSAGE;
          var src = pre.getAttribute("data-src");
          var language = env.language;
          if (language === "none") {
            var extension = (/\.(\w+)$/.exec(src) || [, "none"])[1];
            language = EXTENSIONS[extension] || extension;
          }
          Prism2.util.setLanguage(code2, language);
          Prism2.util.setLanguage(pre, language);
          var autoloader = Prism2.plugins.autoloader;
          if (autoloader) {
            autoloader.loadLanguages(language);
          }
          loadFile(
            src,
            function(text2) {
              pre.setAttribute(STATUS_ATTR, STATUS_LOADED);
              var range = parseRange(pre.getAttribute("data-range"));
              if (range) {
                var lines = text2.split(/\r\n?|\n/g);
                var start = range[0];
                var end = range[1] == null ? lines.length : range[1];
                if (start < 0) {
                  start += lines.length;
                }
                start = Math.max(0, Math.min(start - 1, lines.length));
                if (end < 0) {
                  end += lines.length;
                }
                end = Math.max(0, Math.min(end, lines.length));
                text2 = lines.slice(start, end).join("\n");
                if (!pre.hasAttribute("data-start")) {
                  pre.setAttribute("data-start", String(start + 1));
                }
              }
              code2.textContent = text2;
              Prism2.highlightElement(code2);
            },
            function(error2) {
              pre.setAttribute(STATUS_ATTR, STATUS_FAILED);
              code2.textContent = error2;
            }
          );
        }
      });
      Prism2.plugins.fileHighlight = {
        /**
         * Executes the File Highlight plugin for all matching `pre` elements under the given container.
         *
         * Note: Elements which are already loaded or currently loading will not be touched by this method.
         *
         * @param {ParentNode} [container=document]
         */
        highlight: function highlight(container) {
          var elements = (container || document).querySelectorAll(SELECTOR);
          for (var i2 = 0, element; element = elements[i2++]; ) {
            Prism2.highlightElement(element);
          }
        }
      };
      var logged = false;
      Prism2.fileHighlight = function() {
        if (!logged) {
          console.warn("Prism.fileHighlight is deprecated. Use `Prism.plugins.fileHighlight.highlight` instead.");
          logged = true;
        }
        Prism2.plugins.fileHighlight.highlight.apply(this, arguments);
      };
    })();
  })(prism$1);
  return prism$1.exports;
}
var prismExports = requirePrism();
var prism = /* @__PURE__ */ getDefaultExportFromCjs(prismExports);
var Prism = /* @__PURE__ */ _mergeNamespaces({
  __proto__: null,
  default: prism
}, [prismExports]);
var __classPrivateFieldSet$2 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$2$1 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfSyntax_LF_MANAGER, _LfSyntax_markdown, _LfSyntax_prism, _LfSyntax_loadedLanguages;
const LANGUAGE_LOADERS = {
  css: () => Promise.resolve().then(function() {
    return prism_css_highlight;
  }),
  javascript: () => Promise.resolve().then(function() {
    return prism_javascript_highlight;
  }),
  json: () => Promise.resolve().then(function() {
    return prism_json_highlight;
  }),
  jsx: () => Promise.resolve().then(function() {
    return prism_jsx_highlight;
  }),
  markdown: () => Promise.resolve().then(function() {
    return prism_markdown_highlight;
  }),
  markup: () => Promise.resolve().then(function() {
    return prism_markup_highlight;
  }),
  python: () => Promise.resolve().then(function() {
    return prism_python_highlight;
  }),
  regex: () => Promise.resolve().then(function() {
    return prism_regex_highlight;
  }),
  scss: () => Promise.resolve().then(function() {
    return prism_scss_highlight;
  }),
  tsx: () => Promise.resolve().then(function() {
    return prism_tsx_highlight;
  }),
  typescript: () => Promise.resolve().then(function() {
    return prism_typescript_highlight;
  })
};
const LANGUAGE_EXPORT_NAMES = {
  css: "LF_SYNTAX_CSS",
  javascript: "LF_SYNTAX_JAVASCRIPT",
  json: "LF_SYNTAX_JSON",
  jsx: "LF_SYNTAX_JSX",
  markdown: "LF_SYNTAX_MARKDOWN",
  markup: "LF_SYNTAX_MARKUP",
  python: "LF_SYNTAX_PYTHON",
  regex: "LF_SYNTAX_REGEX",
  scss: "LF_SYNTAX_SCSS",
  tsx: "LF_SYNTAX_TSX",
  typescript: "LF_SYNTAX_TYPESCRIPT"
};
const LANGUAGE_ALIASES = {
  js: "javascript",
  jsx: "jsx",
  ts: "typescript",
  tsx: "tsx",
  md: "markdown",
  html: "markup",
  htm: "markup"
};
class LfSyntax {
  constructor(lfFramework2) {
    _LfSyntax_LF_MANAGER.set(this, void 0);
    _LfSyntax_markdown.set(this, void 0);
    _LfSyntax_prism.set(this, void 0);
    _LfSyntax_loadedLanguages.set(this, /* @__PURE__ */ new Set());
    this.parseMarkdown = (content) => {
      return __classPrivateFieldGet$2$1(this, _LfSyntax_markdown, "f").parse(content, {});
    };
    this.highlightElement = (element) => {
      __classPrivateFieldGet$2$1(this, _LfSyntax_prism, "f").highlightElement(element);
    };
    this.highlightCode = (code2, language) => {
      const grammar = __classPrivateFieldGet$2$1(this, _LfSyntax_prism, "f").languages[language];
      if (!grammar) {
        const { debug } = __classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f");
        debug.logs.new(__classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f"), `[LfSyntax] Language "${language}" not loaded for syntax highlighting`, "warning");
        return code2;
      }
      return __classPrivateFieldGet$2$1(this, _LfSyntax_prism, "f").highlight(code2, grammar, language);
    };
    this.registerLanguage = (name, loader) => {
      if (!__classPrivateFieldGet$2$1(this, _LfSyntax_loadedLanguages, "f").has(name)) {
        loader(__classPrivateFieldGet$2$1(this, _LfSyntax_prism, "f"));
        if (__classPrivateFieldGet$2$1(this, _LfSyntax_prism, "f").languages[name]) {
          __classPrivateFieldGet$2$1(this, _LfSyntax_loadedLanguages, "f").add(name);
        } else {
          const { debug } = __classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f");
          debug.logs.new(__classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f"), `[LfSyntax] Failed to register Prism language "${name}" (loader did not define grammar)`, "warning");
        }
      }
    };
    this.isLanguageLoaded = (name) => {
      const normalized = (name ?? "").toLowerCase();
      if (__classPrivateFieldGet$2$1(this, _LfSyntax_loadedLanguages, "f").has(normalized)) {
        return true;
      }
      const canonical = LANGUAGE_ALIASES[normalized];
      if (canonical) {
        return __classPrivateFieldGet$2$1(this, _LfSyntax_loadedLanguages, "f").has(canonical);
      }
      return __classPrivateFieldGet$2$1(this, _LfSyntax_loadedLanguages, "f").has(normalized);
    };
    this.loadLanguage = async (name) => {
      if (typeof window === "undefined" || typeof document === "undefined") {
        return false;
      }
      const normalized = (name ?? "").toLowerCase();
      if (!normalized) {
        return false;
      }
      const canonical = LANGUAGE_ALIASES[normalized] ?? (normalized in LANGUAGE_LOADERS ? normalized : void 0);
      if (!canonical) {
        __classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f").debug.logs.new(__classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f"), `[LfSyntax] No loader defined for language "${normalized}".`, "warning");
        return false;
      }
      if (this.isLanguageLoaded(canonical)) {
        if (canonical !== normalized) {
          __classPrivateFieldGet$2$1(this, _LfSyntax_loadedLanguages, "f").add(normalized);
        }
        return true;
      }
      try {
        const module = await LANGUAGE_LOADERS[canonical]();
        const exportName = LANGUAGE_EXPORT_NAMES[canonical];
        const loader = module == null ? void 0 : module[exportName];
        if (typeof loader === "function") {
          this.registerLanguage(canonical, loader);
          if (canonical !== normalized) {
            __classPrivateFieldGet$2$1(this, _LfSyntax_loadedLanguages, "f").add(normalized);
          }
          return this.isLanguageLoaded(canonical);
        }
        __classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f").debug.logs.new(__classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f"), `[LfSyntax] Loader for language "${canonical}" did not expose "${exportName}".`, "warning");
      } catch (error2) {
        __classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f").debug.logs.new(__classPrivateFieldGet$2$1(this, _LfSyntax_LF_MANAGER, "f"), `[LfSyntax] Failed to load language "${canonical}": ${error2}`, "error");
      }
      return false;
    };
    __classPrivateFieldSet$2(this, _LfSyntax_LF_MANAGER, lfFramework2, "f");
    __classPrivateFieldSet$2(this, _LfSyntax_markdown, new MarkdownIt({
      html: false,
      // Don't allow raw HTML for security
      linkify: false,
      // Don't auto-convert URLs (explicit links only)
      typographer: false
      // Don't replace quotes/dashes
    }), "f");
    __classPrivateFieldSet$2(this, _LfSyntax_prism, Prism, "f");
  }
  /**
   * Get the underlying MarkdownIt instance for advanced configuration or plugin usage.
   *
   * @returns The MarkdownIt parser instance
   *
   * @example
   * ```typescript
   * const md = syntax.markdown;
   * md.use(somePlugin);
   * ```
   */
  get markdown() {
    return __classPrivateFieldGet$2$1(this, _LfSyntax_markdown, "f");
  }
  /**
   * Get the underlying Prism instance for advanced usage or plugin integration.
   *
   * @returns The Prism syntax highlighter instance
   *
   * @example
   * ```typescript
   * const prism = syntax.prism;
   * // Use Prism API directly
   * ```
   */
  get prism() {
    return __classPrivateFieldGet$2$1(this, _LfSyntax_prism, "f");
  }
}
_LfSyntax_LF_MANAGER = /* @__PURE__ */ new WeakMap(), _LfSyntax_markdown = /* @__PURE__ */ new WeakMap(), _LfSyntax_prism = /* @__PURE__ */ new WeakMap(), _LfSyntax_loadedLanguages = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldSet$1$1 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$1$1 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfTheme_COMPONENTS, _LfTheme_CURRENT, _LfTheme_DEFAULT, _LfTheme_LIST, _LfTheme_MANAGER, _LfTheme_MASTER_CUSTOM_STYLE, _LfTheme_STYLE_ELEMENT, _LfTheme_SPRITE_IDS, _LfTheme_SPRITE_INDEXING, _LfTheme_consistencyCheck, _LfTheme_prepFont, _LfTheme_prepGlobalStyles, _LfTheme_prepVariables, _LfTheme_updateComponents, _LfTheme_updateDocument, _LfTheme_updateStyleElement;
class LfTheme {
  constructor(lfFramework2) {
    _LfTheme_COMPONENTS.set(this, /* @__PURE__ */ new Set());
    _LfTheme_CURRENT.set(this, void 0);
    _LfTheme_DEFAULT.set(this, "dark");
    _LfTheme_LIST.set(this, void 0);
    _LfTheme_MANAGER.set(this, void 0);
    _LfTheme_MASTER_CUSTOM_STYLE.set(this, "MASTER");
    _LfTheme_STYLE_ELEMENT.set(this, void 0);
    _LfTheme_SPRITE_IDS.set(this, void 0);
    _LfTheme_SPRITE_INDEXING.set(this, void 0);
    _LfTheme_consistencyCheck.set(this, () => {
      var _a;
      const { logs } = __classPrivateFieldGet$1$1(this, _LfTheme_MANAGER, "f").debug;
      if (!((_a = __classPrivateFieldGet$1$1(this, _LfTheme_LIST, "f")) == null ? void 0 : _a[__classPrivateFieldGet$1$1(this, _LfTheme_CURRENT, "f")])) {
        logs.new(this, `Invalid theme! Falling back to (${__classPrivateFieldGet$1$1(this, _LfTheme_DEFAULT, "f")}).`);
        __classPrivateFieldSet$1$1(this, _LfTheme_CURRENT, __classPrivateFieldGet$1$1(this, _LfTheme_DEFAULT, "f"), "f");
      }
    });
    _LfTheme_prepFont.set(this, () => {
      const { get } = __classPrivateFieldGet$1$1(this, _LfTheme_MANAGER, "f").assets;
      let css = "";
      const { font } = this.get.current();
      if (font == null ? void 0 : font.length) {
        font.forEach((f2) => {
          const path = get(`./assets/fonts/${f2}-Regular`).path;
          css += `@font-face{font-family:${f2.split("-")[0].replace(new RegExp("(?<!^)(?=[A-Z])", "g"), " ")};`;
          css += `src:url('${path}.woff2')format('woff2');}`;
        });
      }
      return css;
    });
    _LfTheme_prepGlobalStyles.set(this, () => {
      let css = "";
      for (const [selector, rules] of Object.entries(GLOBAL_STYLES)) {
        if (selector.startsWith("@keyframes")) {
          css += `${selector} { `;
          if (Array.isArray(rules)) {
            for (const frame of rules) {
              for (const [frameKey, props] of Object.entries(frame)) {
                css += `${frameKey} { `;
                for (const [prop, value] of Object.entries(props)) {
                  css += `${prop}: ${value}; `;
                }
                css += `} `;
              }
            }
          }
          css += `} `;
        } else {
          css += `${selector} { `;
          for (const [prop, value] of Object.entries(rules)) {
            css += `${prop}: ${value}; `;
          }
          css += `} `;
        }
      }
      return css.trim();
    });
    _LfTheme_prepVariables.set(this, () => {
      const { assets, color } = __classPrivateFieldGet$1$1(this, _LfTheme_MANAGER, "f");
      let css = "";
      const { variables } = this.get.current();
      Object.entries(variables).forEach(([key, val]) => {
        switch (key) {
          case (key.startsWith(LF_THEME_COLORS_PREFIX) && key):
            const { rgbValues } = color.compute(val);
            css += `${key}: ${rgbValues};`;
            break;
          case (key.startsWith(LF_THEME_ICONS_PREFIX) && key):
            const path = assets.get(`./assets/svg/${val}.svg`).path;
            css += `${key}: url(${path}) no-repeat center;`;
            break;
          default:
            css += `${key}: ${val};`;
            break;
        }
      });
      return css;
    });
    _LfTheme_updateComponents.set(this, () => {
      __classPrivateFieldGet$1$1(this, _LfTheme_COMPONENTS, "f").forEach((comp) => {
        var _a;
        if ((_a = comp == null ? void 0 : comp.rootElement) == null ? void 0 : _a.isConnected) {
          comp.refresh();
        }
      });
    });
    _LfTheme_updateDocument.set(this, () => {
      const { isDark, name } = this.get.current();
      const dom = document.documentElement;
      dom.setAttribute(LF_THEME_ATTRIBUTE.theme, name);
      if (isDark) {
        dom.removeAttribute(LF_THEME_ATTRIBUTE.light);
        dom.setAttribute(LF_THEME_ATTRIBUTE.dark, "");
      } else {
        dom.removeAttribute(LF_THEME_ATTRIBUTE.dark);
        dom.setAttribute(LF_THEME_ATTRIBUTE.light, "");
      }
      document.dispatchEvent(new CustomEvent("lf-theme-change"));
    });
    _LfTheme_updateStyleElement.set(this, () => {
      let css = "";
      css += __classPrivateFieldGet$1$1(this, _LfTheme_prepFont, "f").call(this);
      css += __classPrivateFieldGet$1$1(this, _LfTheme_prepGlobalStyles, "f").call(this);
      css += `:root[lf-theme="${__classPrivateFieldGet$1$1(this, _LfTheme_CURRENT, "f")}"] {${__classPrivateFieldGet$1$1(this, _LfTheme_prepVariables, "f").call(this)}}`;
      __classPrivateFieldGet$1$1(this, _LfTheme_STYLE_ELEMENT, "f").innerText = css;
    });
    this.bemClass = (block2, element, modifiers) => {
      let baseClass = element ? `${block2}__${element}` : block2;
      if (modifiers) {
        const modifierClasses = Object.entries(modifiers).filter(([_2, isActive]) => isActive).map(([key]) => `${baseClass}--${key}`);
        baseClass += ` ${modifierClasses.join(" ")}`;
      }
      return baseClass.trim();
    };
    this.get = {
      current: () => {
        __classPrivateFieldGet$1$1(this, _LfTheme_consistencyCheck, "f").call(this);
        const { variables, isDark, customStyles, font } = __classPrivateFieldGet$1$1(this, _LfTheme_LIST, "f")[__classPrivateFieldGet$1$1(this, _LfTheme_CURRENT, "f")];
        return {
          variables,
          customStyles,
          font,
          isDark,
          name: __classPrivateFieldGet$1$1(this, _LfTheme_CURRENT, "f"),
          full: __classPrivateFieldGet$1$1(this, _LfTheme_LIST, "f")[__classPrivateFieldGet$1$1(this, _LfTheme_CURRENT, "f")]
        };
      },
      sprite: {
        path: () => {
          const { assets } = __classPrivateFieldGet$1$1(this, _LfTheme_MANAGER, "f");
          return assets.get("./assets/svg/sprite.svg").path;
        },
        ids: async () => {
          if (__classPrivateFieldGet$1$1(this, _LfTheme_SPRITE_IDS, "f"))
            return __classPrivateFieldGet$1$1(this, _LfTheme_SPRITE_IDS, "f");
          if (__classPrivateFieldGet$1$1(this, _LfTheme_SPRITE_INDEXING, "f"))
            return __classPrivateFieldGet$1$1(this, _LfTheme_SPRITE_INDEXING, "f");
          __classPrivateFieldSet$1$1(this, _LfTheme_SPRITE_INDEXING, (async () => {
            try {
              const { assets } = __classPrivateFieldGet$1$1(this, _LfTheme_MANAGER, "f");
              const sprite = assets.get("./assets/svg/sprite.svg");
              if (!(sprite == null ? void 0 : sprite.path) || typeof fetch === "undefined")
                return /* @__PURE__ */ new Set();
              const res = await fetch(sprite.path);
              if (!res.ok)
                return /* @__PURE__ */ new Set();
              const text2 = await res.text();
              const ids = /* @__PURE__ */ new Set();
              const re = /<symbol\s+id=\"([^\"]+)\"/g;
              let m2;
              while (m2 = re.exec(text2))
                ids.add(m2[1]);
              __classPrivateFieldSet$1$1(this, _LfTheme_SPRITE_IDS, ids, "f");
              return ids;
            } catch {
              return /* @__PURE__ */ new Set();
            } finally {
              __classPrivateFieldSet$1$1(this, _LfTheme_SPRITE_INDEXING, void 0, "f");
            }
          })(), "f");
          return __classPrivateFieldGet$1$1(this, _LfTheme_SPRITE_INDEXING, "f");
        },
        hasIcon: async (id) => {
          const ids = await this.get.sprite.ids();
          return ids.has(id);
        }
      },
      icon: (name) => LF_ICONS_REGISTRY[name],
      icons: () => LF_ICONS_REGISTRY,
      themes: () => {
        const asArray = [];
        const nodes = [];
        Object.keys(__classPrivateFieldGet$1$1(this, _LfTheme_LIST, "f")).forEach((id) => {
          const char0 = id.charAt(0).toUpperCase();
          asArray.push(id);
          nodes.push({
            id,
            value: `${char0}${id.substring(1)}`
          });
        });
        return {
          asArray,
          asDataset: {
            nodes: [
              {
                icon: this.get.icon("colorSwatch"),
                id: "root",
                value: "Random",
                children: nodes
              }
            ]
          }
        };
      }
    };
    this.set = (name, list2) => {
      if (typeof document === "undefined") {
        return;
      }
      if (!__classPrivateFieldGet$1$1(this, _LfTheme_STYLE_ELEMENT, "f")) {
        __classPrivateFieldSet$1$1(this, _LfTheme_STYLE_ELEMENT, document.documentElement.querySelector("head").appendChild(document.createElement("style")), "f");
      }
      if (name) {
        __classPrivateFieldSet$1$1(this, _LfTheme_CURRENT, name, "f");
      }
      if (list2) {
        __classPrivateFieldSet$1$1(this, _LfTheme_LIST, list2, "f");
      }
      __classPrivateFieldGet$1$1(this, _LfTheme_consistencyCheck, "f").call(this);
      __classPrivateFieldGet$1$1(this, _LfTheme_updateStyleElement, "f").call(this);
      __classPrivateFieldGet$1$1(this, _LfTheme_updateComponents, "f").call(this);
      __classPrivateFieldGet$1$1(this, _LfTheme_updateDocument, "f").call(this);
    };
    this.refresh = () => {
      const { logs } = __classPrivateFieldGet$1$1(this, _LfTheme_MANAGER, "f").debug;
      try {
        __classPrivateFieldGet$1$1(this, _LfTheme_updateStyleElement, "f").call(this);
        logs.new(this, "Theme " + __classPrivateFieldGet$1$1(this, _LfTheme_CURRENT, "f") + " refreshed.");
        document.dispatchEvent(new CustomEvent("lf-theme-refresh"));
      } catch (error2) {
        logs.new(this, "Theme not refreshed.", "warning");
      }
    };
    this.setLfStyle = (comp) => {
      const isMaliciousCSS = (css2) => {
        if (!css2)
          return true;
        if (/javascript:/i.test(css2))
          return true;
        if (/<script>/i.test(css2))
          return true;
        if (/url\(.*(javascript|data):/i.test(css2))
          return true;
        return false;
      };
      let css = "";
      const { customStyles } = this.get.current();
      const tag = comp.rootElement.tagName;
      if (customStyles == null ? void 0 : customStyles[__classPrivateFieldGet$1$1(this, _LfTheme_MASTER_CUSTOM_STYLE, "f")]) {
        css += customStyles[__classPrivateFieldGet$1$1(this, _LfTheme_MASTER_CUSTOM_STYLE, "f")];
      }
      if (customStyles == null ? void 0 : customStyles[tag]) {
        css += ` ${customStyles[tag]}`;
      }
      if (comp.lfStyle) {
        css += ` ${comp.lfStyle}`;
      }
      return !isMaliciousCSS(css) && css || "";
    };
    this.randomize = () => {
      const { logs } = __classPrivateFieldGet$1$1(this, _LfTheme_MANAGER, "f").debug;
      const themes = this.get.themes().asArray;
      if (themes.length > 0) {
        let index = null;
        while (index === null || themes[index] === __classPrivateFieldGet$1$1(this, _LfTheme_CURRENT, "f")) {
          index = Math.floor(Math.random() * Math.floor(themes.length));
        }
        this.set(themes[index]);
      } else {
        logs.new(this, "Couldn't randomize theme: no themes available!", "warning");
      }
    };
    this.register = (comp) => {
      __classPrivateFieldGet$1$1(this, _LfTheme_COMPONENTS, "f").add(comp);
    };
    this.unregister = (comp) => {
      var _a;
      (_a = __classPrivateFieldGet$1$1(this, _LfTheme_COMPONENTS, "f")) == null ? void 0 : _a.delete(comp);
    };
    __classPrivateFieldSet$1$1(this, _LfTheme_MANAGER, lfFramework2, "f");
    __classPrivateFieldSet$1$1(this, _LfTheme_LIST, THEME_LIST, "f");
    __classPrivateFieldSet$1$1(this, _LfTheme_CURRENT, __classPrivateFieldGet$1$1(this, _LfTheme_DEFAULT, "f"), "f");
  }
}
_LfTheme_COMPONENTS = /* @__PURE__ */ new WeakMap(), _LfTheme_CURRENT = /* @__PURE__ */ new WeakMap(), _LfTheme_DEFAULT = /* @__PURE__ */ new WeakMap(), _LfTheme_LIST = /* @__PURE__ */ new WeakMap(), _LfTheme_MANAGER = /* @__PURE__ */ new WeakMap(), _LfTheme_MASTER_CUSTOM_STYLE = /* @__PURE__ */ new WeakMap(), _LfTheme_STYLE_ELEMENT = /* @__PURE__ */ new WeakMap(), _LfTheme_SPRITE_IDS = /* @__PURE__ */ new WeakMap(), _LfTheme_SPRITE_INDEXING = /* @__PURE__ */ new WeakMap(), _LfTheme_consistencyCheck = /* @__PURE__ */ new WeakMap(), _LfTheme_prepFont = /* @__PURE__ */ new WeakMap(), _LfTheme_prepGlobalStyles = /* @__PURE__ */ new WeakMap(), _LfTheme_prepVariables = /* @__PURE__ */ new WeakMap(), _LfTheme_updateComponents = /* @__PURE__ */ new WeakMap(), _LfTheme_updateDocument = /* @__PURE__ */ new WeakMap(), _LfTheme_updateStyleElement = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldGet$9 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var __classPrivateFieldSet$9 = function(receiver, state, value, kind, f2) {
  if (kind === "m")
    throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2)
    throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver))
    throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var _LfFramework_LISTENERS_SETUP, _LfFramework_MODULES, _LfFramework_SHAPES, _LfFramework_data, _LfFramework_drag, _LfFramework_llm, _LfFramework_portal, _LfFramework_syntax, _LfFramework_setupListeners;
let ASSET_BASE_PATH = "";
const fallbackGetAssetPath = (path) => {
  return ASSET_BASE_PATH + path;
};
const fallbackSetAssetPath = (path) => {
  ASSET_BASE_PATH = path.endsWith("/") ? path : path + "/";
};
let getAssetPath = fallbackGetAssetPath;
let setAssetPath = fallbackSetAssetPath;
class LfFramework {
  constructor() {
    _LfFramework_LISTENERS_SETUP.set(this, false);
    _LfFramework_MODULES.set(this, /* @__PURE__ */ new Map([
      [
        "lf-framework",
        {
          name: "lf-framework",
          getAssetPath,
          setAssetPath
        }
      ]
    ]));
    _LfFramework_SHAPES.set(this, /* @__PURE__ */ new WeakMap());
    _LfFramework_data.set(this, void 0);
    _LfFramework_drag.set(this, void 0);
    _LfFramework_llm.set(this, void 0);
    _LfFramework_portal.set(this, void 0);
    _LfFramework_syntax.set(this, void 0);
    _LfFramework_setupListeners.set(this, () => {
      if (typeof document === "undefined") {
        return;
      }
      document.addEventListener("click", (e2) => {
        const { utilities, portal } = this;
        const { clickCallbacks } = utilities;
        const paths = e2.composedPath();
        clickCallbacks.forEach(({ cb, element }) => {
          if (!(element == null ? void 0 : element.isConnected)) {
            cb();
            return;
          }
          if (paths.includes(element)) {
            return;
          }
          const portalState = portal.getState(element);
          if (portalState) {
            const { parent } = portalState;
            if (!paths.includes(parent)) {
              cb();
            }
          } else {
            cb();
          }
        });
      });
    });
    this.addClickCallback = (cb, async) => {
      const { utilities } = this;
      const { clickCallbacks } = utilities;
      if (!__classPrivateFieldGet$9(this, _LfFramework_LISTENERS_SETUP, "f")) {
        __classPrivateFieldSet$9(this, _LfFramework_LISTENERS_SETUP, true, "f");
        __classPrivateFieldGet$9(this, _LfFramework_setupListeners, "f").call(this);
      }
      if (async) {
        requestAnimationFrame(async () => clickCallbacks.add(cb));
      } else {
        clickCallbacks.add(cb);
      }
    };
    this.assignRef = (refs, key) => (el) => {
      if (el)
        refs[key] = el;
    };
    this.getModules = () => __classPrivateFieldGet$9(this, _LfFramework_MODULES, "f");
    this.register = (module, options) => {
      if (__classPrivateFieldGet$9(this, _LfFramework_MODULES, "f").has(module)) {
        this.debug.logs.new(this, `Module ${module} is already registered.`, "error");
        return;
      }
      const safeGet = typeof options.getAssetPath === "function" ? options.getAssetPath : fallbackGetAssetPath;
      const safeSet = typeof options.setAssetPath === "function" ? options.setAssetPath : fallbackSetAssetPath;
      __classPrivateFieldGet$9(this, _LfFramework_MODULES, "f").set(module, {
        name: module,
        getAssetPath: safeGet,
        setAssetPath: safeSet
      });
      this.debug.logs.new(this, `Module ${module} registered.`);
    };
    this.removeClickCallback = (cb) => {
      this.utilities.clickCallbacks.delete(cb);
    };
    this.shapes = {
      get: () => __classPrivateFieldGet$9(this, _LfFramework_SHAPES, "f").get(this),
      set: (shapes) => {
        __classPrivateFieldGet$9(this, _LfFramework_SHAPES, "f").set(this, shapes);
      }
    };
    const ICON_STYLE_CACHE = /* @__PURE__ */ new Map();
    this.assets = {
      get: (value, module = "lf-framework") => {
        if (!__classPrivateFieldGet$9(this, _LfFramework_MODULES, "f").has(module)) {
          this.debug.logs.new(this, `Module ${module} is not registered.`, "error");
          return {
            path: "",
            style: { mask: "", webkitMask: "" }
          };
        }
        const normalizeRequest = (raw) => {
          if (raw.startsWith("./assets/")) {
            return `./${raw.slice(9)}`;
          }
          if (raw.startsWith("assets/")) {
            return `./${raw.slice(7)}`;
          }
          if (raw.startsWith("/assets/")) {
            return `./${raw.slice(8)}`;
          }
          return raw;
        };
        const request = normalizeRequest(value);
        if (ICON_STYLE_CACHE.has(request)) {
          return ICON_STYLE_CACHE.get(request);
        }
        const { getAssetPath: getAssetPath2 } = __classPrivateFieldGet$9(this, _LfFramework_MODULES, "f").get(module);
        const resolveGetAssetPath = typeof getAssetPath2 === "function" ? getAssetPath2 : fallbackGetAssetPath;
        const path = resolveGetAssetPath(request);
        const style = {
          mask: `url('${path}') no-repeat center`,
          webkitMask: `url('${path}') no-repeat center`
        };
        const cached = { path, style };
        ICON_STYLE_CACHE.set(request, cached);
        return cached;
      },
      set: (value, module) => {
        if (!module) {
          __classPrivateFieldGet$9(this, _LfFramework_MODULES, "f").forEach(({ setAssetPath: setAssetPath2 }) => {
            if (typeof setAssetPath2 === "function") {
              setAssetPath2(value);
            } else {
              fallbackSetAssetPath(value);
            }
          });
        } else if (__classPrivateFieldGet$9(this, _LfFramework_MODULES, "f").has(module)) {
          const { setAssetPath: setAssetPath2 } = __classPrivateFieldGet$9(this, _LfFramework_MODULES, "f").get(module);
          if (typeof setAssetPath2 === "function") {
            setAssetPath2(value);
          } else {
            fallbackSetAssetPath(value);
          }
        }
      }
    };
    this.color = new LfColor(this);
    this.debug = new LfDebug(this);
    this.effects = new LfEffects(this);
    this.theme = new LfTheme(this);
    this.utilities = {
      clickCallbacks: /* @__PURE__ */ new Set()
    };
  }
  //#region Lazy Getters for Heavy Modules
  /**
   * Data module - lazy initialized on first access.
   * Provides utilities for data manipulation and tree structures.
   */
  get data() {
    if (!__classPrivateFieldGet$9(this, _LfFramework_data, "f")) {
      __classPrivateFieldSet$9(this, _LfFramework_data, new LfData(this), "f");
    }
    return __classPrivateFieldGet$9(this, _LfFramework_data, "f");
  }
  /**
   * Drag module - lazy initialized on first access.
   * Provides drag-and-drop functionality.
   */
  get drag() {
    if (!__classPrivateFieldGet$9(this, _LfFramework_drag, "f")) {
      __classPrivateFieldSet$9(this, _LfFramework_drag, new LfDrag(this), "f");
    }
    return __classPrivateFieldGet$9(this, _LfFramework_drag, "f");
  }
  /**
   * LLM module - lazy initialized on first access.
   * Provides utilities for LLM streaming and interaction.
   */
  get llm() {
    if (!__classPrivateFieldGet$9(this, _LfFramework_llm, "f")) {
      __classPrivateFieldSet$9(this, _LfFramework_llm, new LfLLM(this), "f");
    }
    return __classPrivateFieldGet$9(this, _LfFramework_llm, "f");
  }
  /**
   * Portal module - lazy initialized on first access.
   * Manages DOM portals for rendering content outside component tree.
   */
  get portal() {
    if (!__classPrivateFieldGet$9(this, _LfFramework_portal, "f")) {
      __classPrivateFieldSet$9(this, _LfFramework_portal, new LfPortal(this), "f");
    }
    return __classPrivateFieldGet$9(this, _LfFramework_portal, "f");
  }
  /**
   * Syntax module - lazy initialized on first access.
   * Provides markdown parsing and code syntax highlighting.
   * Heavy module: loads Prism + Markdown-it only when needed.
   */
  get syntax() {
    if (!__classPrivateFieldGet$9(this, _LfFramework_syntax, "f")) {
      __classPrivateFieldSet$9(this, _LfFramework_syntax, new LfSyntax(this), "f");
    }
    return __classPrivateFieldGet$9(this, _LfFramework_syntax, "f");
  }
  sanitizeProps(props, compName) {
    var _a;
    const ALLOWED_ATTRS = new Set(LF_FRAMEWORK_ALLOWED_ATTRS);
    const ALLOWED_PREFIXES = new Set(LF_FRAMEWORK_ALLOWED_PREFIXES);
    const PROPS = getComponentProps();
    if (compName && PROPS[compName]) {
      for (const key of PROPS[compName]) {
        ALLOWED_ATTRS.add(key);
      }
    }
    const isAllowedAttribute = (attrName) => {
      if (ALLOWED_ATTRS.has(attrName))
        return true;
      if (ALLOWED_PREFIXES.has(attrName.split("-")[0]))
        return true;
      return false;
    };
    const isMaliciousValue = (value) => {
      if (typeof value !== "string")
        return false;
      if (/javascript:/i.test(value))
        return true;
      if (/<script>/i.test(value))
        return true;
      return false;
    };
    const sanitized = {};
    for (const key in props) {
      if (!Object.prototype.hasOwnProperty.call(props, key))
        continue;
      const value = props[key];
      if (key.toLowerCase().startsWith("on"))
        continue;
      if (!isAllowedAttribute(key))
        continue;
      if (isMaliciousValue(value))
        continue;
      sanitized[key] = value;
    }
    if (compName) {
      return sanitized;
    }
    if (typeof process !== "undefined" && ((_a = process == null ? void 0 : process.env) == null ? void 0 : _a.NODE_ENV) !== "production") {
      const droppedKeys = [];
      for (const key in props) {
        if (!Object.prototype.hasOwnProperty.call(props, key))
          continue;
        if (key in sanitized)
          continue;
        if (!key.startsWith("lf"))
          continue;
        droppedKeys.push(key);
      }
      if (droppedKeys.length) {
        console.warn(`[lf-framework] sanitizeProps called without component name. Dropped lf-prefixed attributes: ${droppedKeys.join(", ")}. Pass the target component name as the second argument to keep them.`);
      }
    }
    return sanitized;
  }
}
_LfFramework_LISTENERS_SETUP = /* @__PURE__ */ new WeakMap(), _LfFramework_MODULES = /* @__PURE__ */ new WeakMap(), _LfFramework_SHAPES = /* @__PURE__ */ new WeakMap(), _LfFramework_data = /* @__PURE__ */ new WeakMap(), _LfFramework_drag = /* @__PURE__ */ new WeakMap(), _LfFramework_llm = /* @__PURE__ */ new WeakMap(), _LfFramework_portal = /* @__PURE__ */ new WeakMap(), _LfFramework_syntax = /* @__PURE__ */ new WeakMap(), _LfFramework_setupListeners = /* @__PURE__ */ new WeakMap();
const LF_SYNTAX_CSS = (Prism2) => {
  var e2 = /(?:"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"|'(?:\\(?:\r\n|[\s\S])|[^'\\\r\n])*')/;
  Prism2.languages.css = {
    comment: /\/\*[\s\S]*?\*\//,
    atrule: {
      pattern: RegExp(`@[\\w-](?:[^;{\\s"']|\\s+(?!\\s)|` + e2.source + ")*?(?:;|(?=\\s*\\{))"),
      inside: {
        rule: /^@[\w-]+/,
        "selector-function-argument": {
          pattern: /(\bselector\s*\(\s*(?![\s)]))(?:[^()\s]|\s+(?![\s)])|\((?:[^()]|\([^()]*\))*\))+(?=\s*\))/,
          lookbehind: true,
          alias: "selector"
        },
        keyword: {
          pattern: /(^|[^\w-])(?:and|not|only|or)(?![\w-])/,
          lookbehind: true
        }
      }
    },
    url: {
      pattern: RegExp("\\burl\\((?:" + e2.source + `|(?:[^\\\\\r
()"']|\\\\[^])*)\\)`, "i"),
      greedy: true,
      inside: {
        function: /^url/i,
        punctuation: /^\(|\)$/,
        string: {
          pattern: RegExp("^" + e2.source + "$"),
          alias: "url"
        }
      }
    },
    selector: {
      pattern: RegExp(`(^|[{}\\s])[^{}\\s](?:[^{};"'\\s]|\\s+(?![\\s{])|` + e2.source + ")*(?=\\s*\\{)"),
      lookbehind: true
    },
    string: { pattern: e2, greedy: true },
    property: {
      pattern: /(^|[^-\w\xA0-\uFFFF])(?!\s)[-_a-z\xA0-\uFFFF](?:(?!\s)[-\w\xA0-\uFFFF])*(?=\s*:)/i,
      lookbehind: true
    },
    important: /!important\b/i,
    function: {
      pattern: /(^|[^-a-z0-9])[-a-z0-9]+(?=\()/i,
      lookbehind: true
    },
    punctuation: /[(){};:,]/
  }, Prism2.languages.css.atrule.inside.rest = Prism2.languages.css;
  var t2 = Prism2.languages.markup;
  t2 && (t2.tag.addInlined("style", "css"), t2.tag.addAttribute("style", "css"));
};
var prism_css_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_CSS
});
const LF_SYNTAX_JAVASCRIPT = (Prism2) => {
  Prism2.languages.javascript = Prism2.languages.extend("clike", {
    "class-name": [
      Prism2.languages.clike["class-name"],
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$A-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\.(?:constructor|prototype))/,
        lookbehind: true
      }
    ],
    keyword: [
      { pattern: /((?:^|\})\s*)catch\b/, lookbehind: true },
      {
        pattern: /(^|[^.]|\.\.\.\s*)\b(?:as|assert(?=\s*\{)|async(?=\s*(?:function\b|\(|[$\w\xA0-\uFFFF]|$))|await|break|case|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally(?=\s*(?:\{|$))|for|from(?=\s*(?:['"]|$))|function|(?:get|set)(?=\s*(?:[#\[$\w\xA0-\uFFFF]|$))|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)\b/,
        lookbehind: true
      }
    ],
    function: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*(?:\.\s*(?:apply|bind|call)\s*)?\()/,
    number: {
      pattern: RegExp("(^|[^\\w$])(?:NaN|Infinity|0[bB][01]+(?:_[01]+)*n?|0[oO][0-7]+(?:_[0-7]+)*n?|0[xX][\\dA-Fa-f]+(?:_[\\dA-Fa-f]+)*n?|\\d+(?:_\\d+)*n|(?:\\d+(?:_\\d+)*(?:\\.(?:\\d+(?:_\\d+)*)?)?|\\.\\d+(?:_\\d+)*)(?:[Ee][+-]?\\d+(?:_\\d+)*)?)(?![\\w$])"),
      lookbehind: true
    },
    operator: /--|\+\+|\*\*=?|=>|&&=?|\|\|=?|[!=]==|<<=?|>>>?=?|[-+*/%&|^!=<>]=?|\.{3}|\?\?=?|\?\.?|[~:]/
  }), Prism2.languages.javascript["class-name"][0].pattern = /(\b(?:class|extends|implements|instanceof|interface|new)\s+)[\w.\\]+/, Prism2.languages.insertBefore("javascript", "keyword", {
    regex: {
      pattern: RegExp(`((?:^|[^$\\w\\xA0-\\uFFFF."'\\])\\s]|\\b(?:return|yield))\\s*)/(?:(?:\\[(?:[^\\]\\\\\r
]|\\\\.)*\\]|\\\\.|[^/\\\\\\[\r
])+/[dgimyus]{0,7}|(?:\\[(?:[^[\\]\\\\\r
]|\\\\.|\\[(?:[^[\\]\\\\\r
]|\\\\.|\\[(?:[^[\\]\\\\\r
]|\\\\.)*\\])*\\])*\\]|\\\\.|[^/\\\\\\[\r
])+/[dgimyus]{0,7}v[dgimyus]{0,7})(?=(?:\\s|/\\*(?:[^*]|\\*(?!/))*\\*/)*(?:$|[\r
,.;:})\\]]|//))`),
      lookbehind: true,
      greedy: true,
      inside: {
        "regex-source": {
          pattern: /^(\/)[\s\S]+(?=\/[a-z]*$)/,
          lookbehind: true,
          alias: "language-regex",
          inside: Prism2.languages.regex
        },
        "regex-delimiter": /^\/|\/$/,
        "regex-flags": /^[a-z]+$/
      }
    },
    "function-variable": {
      pattern: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*[=:]\s*(?:async\s*)?(?:\bfunction\b|(?:\((?:[^()]|\([^()]*\))*\)|(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)\s*=>))/,
      alias: "function"
    },
    parameter: [
      {
        pattern: /(function(?:\s+(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)?\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\))/,
        lookbehind: true,
        inside: Prism2.languages.javascript
      },
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*=>)/i,
        lookbehind: true,
        inside: Prism2.languages.javascript
      },
      {
        pattern: /(\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*=>)/,
        lookbehind: true,
        inside: Prism2.languages.javascript
      },
      {
        pattern: /((?:\b|\s|^)(?!(?:as|async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)(?![$\w\xA0-\uFFFF]))(?:(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*)\(\s*|\]\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*\{)/,
        lookbehind: true,
        inside: Prism2.languages.javascript
      }
    ],
    constant: /\b[A-Z](?:[A-Z_]|\dx?)*\b/
  }), Prism2.languages.insertBefore("javascript", "string", {
    hashbang: { pattern: /^#!.*/, greedy: true, alias: "comment" },
    "template-string": {
      pattern: /`(?:\\[\s\S]|\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}|(?!\$\{)[^\\`])*`/,
      greedy: true,
      inside: {
        "template-punctuation": {
          pattern: /^`|`$/,
          alias: "string"
        },
        interpolation: {
          pattern: /((?:^|[^\\])(?:\\{2})*)\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}/,
          lookbehind: true,
          inside: {
            "interpolation-punctuation": {
              pattern: /^\$\{|\}$/,
              alias: "punctuation"
            },
            rest: Prism2.languages.javascript
          }
        },
        string: /[\s\S]+/
      }
    },
    "string-property": {
      pattern: /((?:^|[,{])[ \t]*)(["'])(?:\\(?:\r\n|[\s\S])|(?!\2)[^\\\r\n])*\2(?=\s*:)/m,
      lookbehind: true,
      greedy: true,
      alias: "property"
    }
  }), Prism2.languages.insertBefore("javascript", "operator", {
    "literal-property": {
      pattern: /((?:^|[,{])[ \t]*)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*:)/m,
      lookbehind: true,
      alias: "property"
    }
  }), Prism2.languages.markup && (Prism2.languages.markup.tag.addInlined("script", "javascript"), Prism2.languages.markup.tag.addAttribute("on(?:abort|blur|change|click|composition(?:end|start|update)|dblclick|error|focus(?:in|out)?|key(?:down|up)|load|mouse(?:down|enter|leave|move|out|over|up)|reset|resize|scroll|select|slotchange|submit|unload|wheel)", "javascript")), Prism2.languages.js = Prism2.languages.javascript;
};
var prism_javascript_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_JAVASCRIPT
});
const LF_SYNTAX_JSON = (Prism2) => {
  Prism2.languages.json = {
    property: {
      pattern: /(^|[^\\])"(?:\\.|[^\\"\r\n])*"(?=\s*:)/,
      lookbehind: true,
      greedy: true
    },
    string: {
      pattern: /(^|[^\\])"(?:\\.|[^\\"\r\n])*"(?!\s*:)/,
      lookbehind: true,
      greedy: true
    },
    comment: { pattern: /\/\/.*|\/\*[\s\S]*?(?:\*\/|$)/, greedy: true },
    number: /-?\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b/i,
    punctuation: /[{}[\],]/,
    operator: /:/,
    boolean: /\b(?:false|true)\b/,
    null: { pattern: /\bnull\b/, alias: "keyword" }
  }, Prism2.languages.webmanifest = Prism2.languages.json;
};
var prism_json_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_JSON
});
const LF_SYNTAX_JSX = (Prism2) => {
  var n2 = Prism2.util.clone(Prism2.languages.javascript), e2 = "(?:\\{<S>*\\.{3}(?:[^{}]|<BRACES>)*\\})";
  function a2(t2, n3) {
    return t2 = t2.replace(/<S>/g, function() {
      return "(?:\\s|//.*(?!.)|/\\*(?:[^*]|\\*(?!/))\\*/)";
    }).replace(/<BRACES>/g, function() {
      return "(?:\\{(?:\\{(?:\\{[^{}]*\\}|[^{}])*\\}|[^{}])*\\})";
    }).replace(/<SPREAD>/g, function() {
      return e2;
    }), RegExp(t2, n3);
  }
  e2 = a2(e2).source, Prism2.languages.jsx = Prism2.languages.extend("markup", n2), Prism2.languages.jsx.tag.pattern = a2(`</?(?:[\\w.:-]+(?:<S>+(?:[\\w.:$-]+(?:=(?:"(?:\\\\[^]|[^\\\\"])*"|'(?:\\\\[^]|[^\\\\'])*'|[^\\s{'"/>=]+|<BRACES>))?|<SPREAD>))*<S>*/?)?>`), Prism2.languages.jsx.tag.inside.tag.pattern = /^<\/?[^\s>\/]*/, Prism2.languages.jsx.tag.inside["attr-value"].pattern = /=(?!\{)(?:"(?:\\[\s\S]|[^\\"])*"|'(?:\\[\s\S]|[^\\'])*'|[^\s'">]+)/, Prism2.languages.jsx.tag.inside.tag.inside["class-name"] = /^[A-Z]\w*(?:\.[A-Z]\w*)*$/, Prism2.languages.jsx.tag.inside.comment = n2.comment, Prism2.languages.insertBefore("inside", "attr-name", {
    spread: {
      pattern: a2("<SPREAD>"),
      inside: Prism2.languages.jsx
    }
  }, Prism2.languages.jsx.tag), Prism2.languages.insertBefore("inside", "special-attr", {
    script: {
      pattern: a2("=<BRACES>"),
      alias: "language-javascript",
      inside: {
        "script-punctuation": {
          pattern: /^=(?=\{)/,
          alias: "punctuation"
        },
        rest: Prism2.languages.jsx
      }
    }
  }, Prism2.languages.jsx.tag);
  var s2 = function(t2) {
    return t2 ? "string" == typeof t2 ? t2 : "string" == typeof t2.content ? t2.content : t2.content.map(s2).join("") : "";
  }, g2 = function(n3) {
    for (var e3 = [], a3 = 0; a3 < n3.length; a3++) {
      var o2 = n3[a3], i2 = false;
      if ("string" != typeof o2 && ("tag" === o2.type && o2.content[0] && "tag" === o2.content[0].type ? "</" === o2.content[0].content[0].content ? e3.length > 0 && e3[e3.length - 1].tagName === s2(o2.content[0].content[1]) && e3.pop() : "/>" === o2.content[o2.content.length - 1].content || e3.push({
        tagName: s2(o2.content[0].content[1]),
        openedBraces: 0
      }) : e3.length > 0 && "punctuation" === o2.type && "{" === o2.content ? e3[e3.length - 1].openedBraces++ : e3.length > 0 && e3[e3.length - 1].openedBraces > 0 && "punctuation" === o2.type && "}" === o2.content ? e3[e3.length - 1].openedBraces-- : i2 = true), (i2 || "string" == typeof o2) && e3.length > 0 && 0 === e3[e3.length - 1].openedBraces) {
        var r2 = s2(o2);
        a3 < n3.length - 1 && ("string" == typeof n3[a3 + 1] || "plain-text" === n3[a3 + 1].type) && (r2 += s2(n3[a3 + 1]), n3.splice(a3 + 1, 1)), a3 > 0 && ("string" == typeof n3[a3 - 1] || "plain-text" === n3[a3 - 1].type) && (r2 = s2(n3[a3 - 1]) + r2, n3.splice(a3 - 1, 1), a3--), n3[a3] = new Prism2.Token("plain-text", r2, null, r2);
      }
      o2.content && "string" != typeof o2.content && g2(o2.content);
    }
  };
  Prism2.hooks.add("after-tokenize", function(t2) {
    "jsx" !== t2.language && "tsx" !== t2.language || g2(t2.tokens);
  });
};
var prism_jsx_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_JSX
});
const LF_SYNTAX_MARKDOWN = (Prism2) => {
  function e2(reg) {
    return reg = reg.replace(/<inner>/g, function() {
      return "(?:\\\\.|[^\\\\\n\r]|(?:\n|\r\n?)(?![\r\n]))";
    }), RegExp("((?:^|[^\\\\])(?:\\\\{2})*)(?:" + reg + ")");
  }
  const t2 = "(?:\\\\.|``(?:[^`\r\n]|`(?!`))+``|`[^`\r\n]+`|[^\\\\|\r\n`])+", a2 = "\\|?__(?:\\|__)+\\|?(?:(?:\n|\r\n?)|(?![^]))".replace(/__/g, function() {
    return t2;
  }), i2 = "\\|?[ 	]*:?-{3,}:?[ 	]*(?:\\|[ 	]*:?-{3,}:?[ 	]*)+\\|?(?:\n|\r\n?)";
  Prism2.languages.markdown = Prism2.languages.extend("markup", {}), Prism2.languages.insertBefore("markdown", "prolog", {
    "front-matter-block": {
      pattern: /(^(?:\s*[\r\n])?)---(?!.)[\s\S]*?[\r\n]---(?!.)/,
      lookbehind: true,
      greedy: true,
      inside: {
        punctuation: /^---|---$/,
        "front-matter": {
          pattern: /\S+(?:\s+\S+)*/,
          alias: ["yaml", "language-yaml"],
          inside: Prism2.languages.yaml
        }
      }
    },
    blockquote: {
      pattern: /^>(?:[\t ]*>)*/m,
      alias: "punctuation"
    },
    table: {
      pattern: RegExp("^" + a2 + i2 + "(?:" + a2 + ")*", "m"),
      inside: {
        "table-data-rows": {
          pattern: RegExp("^(" + a2 + i2 + ")(?:" + a2 + ")*$"),
          lookbehind: true,
          inside: {
            "table-data": {
              pattern: RegExp(t2),
              inside: Prism2.languages.markdown
            },
            punctuation: /\|/
          }
        },
        "table-line": {
          pattern: RegExp("^(" + a2 + ")" + i2 + "$"),
          lookbehind: true,
          inside: { punctuation: /\||:?-{3,}:?/ }
        },
        "table-header-row": {
          pattern: RegExp("^" + a2 + "$"),
          inside: {
            "table-header": {
              pattern: RegExp(t2),
              alias: "important",
              inside: Prism2.languages.markdown
            },
            punctuation: /\|/
          }
        }
      }
    },
    code: [
      {
        pattern: /((?:^|\n)[ \t]*\n|(?:^|\r\n?)[ \t]*\r\n?)(?: {4}|\t).+(?:(?:\n|\r\n?)(?: {4}|\t).+)*/,
        lookbehind: true,
        alias: "keyword"
      },
      {
        pattern: /^```[\s\S]*?^```$/m,
        greedy: true,
        inside: {
          "code-block": {
            pattern: /^(```.*(?:\n|\r\n?))[\s\S]+?(?=(?:\n|\r\n?)^```$)/m,
            lookbehind: true
          },
          "code-language": {
            pattern: /^(```).+/,
            lookbehind: true
          },
          punctuation: /```/
        }
      }
    ],
    title: [
      {
        pattern: /\S.*(?:\n|\r\n?)(?:==+|--+)(?=[ \t]*$)/m,
        alias: "important",
        inside: { punctuation: /==+$|--+$/ }
      },
      {
        pattern: /(^\s*)#.+/m,
        lookbehind: true,
        alias: "important",
        inside: { punctuation: /^#+|#+$/ }
      }
    ],
    hr: {
      pattern: /(^\s*)([*-])(?:[\t ]*\2){2,}(?=\s*$)/m,
      lookbehind: true,
      alias: "punctuation"
    },
    list: {
      pattern: /(^\s*)(?:[*+-]|\d+\.)(?=[\t ].)/m,
      lookbehind: true,
      alias: "punctuation"
    },
    "url-reference": {
      pattern: /!?\[[^\]]+\]:[\t ]+(?:\S+|<(?:\\.|[^>\\])+>)(?:[\t ]+(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\((?:\\.|[^)\\])*\)))?/,
      inside: {
        variable: { pattern: /^(!?\[)[^\]]+/, lookbehind: true },
        string: /(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\((?:\\.|[^)\\])*\))$/,
        punctuation: /^[\[\]!:]|[<>]/
      },
      alias: "url"
    },
    bold: {
      pattern: e2("\\b__(?:(?!_)<inner>|_(?:(?!_)<inner>)+_)+__\\b|\\*\\*(?:(?!\\*)<inner>|\\*(?:(?!\\*)<inner>)+\\*)+\\*\\*"),
      lookbehind: true,
      greedy: true,
      inside: {
        content: {
          pattern: /(^..)[\s\S]+(?=..$)/,
          lookbehind: true,
          inside: {}
        },
        punctuation: /\*\*|__/
      }
    },
    italic: {
      pattern: e2("\\b_(?:(?!_)<inner>|__(?:(?!_)<inner>)+__)+_\\b|\\*(?:(?!\\*)<inner>|\\*\\*(?:(?!\\*)<inner>)+\\*\\*)+\\*"),
      lookbehind: true,
      greedy: true,
      inside: {
        content: {
          pattern: /(^.)[\s\S]+(?=.$)/,
          lookbehind: true,
          inside: {}
        },
        punctuation: /[*_]/
      }
    },
    strike: {
      pattern: e2("(~~?)(?:(?!~)<inner>)+\\2"),
      lookbehind: true,
      greedy: true,
      inside: {
        content: {
          pattern: /(^~~?)[\s\S]+(?=\1$)/,
          lookbehind: true,
          inside: {}
        },
        punctuation: /~~?/
      }
    },
    "code-snippet": {
      pattern: /(^|[^\\`])(?:``[^`\r\n]+(?:`[^`\r\n]+)*``(?!`)|`[^`\r\n]+`(?!`))/,
      lookbehind: true,
      greedy: true,
      alias: ["code", "keyword"]
    },
    url: {
      pattern: e2('!?\\[(?:(?!\\])<inner>)+\\](?:\\([^\\s)]+(?:[	 ]+"(?:\\\\.|[^"\\\\])*")?\\)|[ 	]?\\[(?:(?!\\])<inner>)+\\])'),
      lookbehind: true,
      greedy: true,
      inside: {
        operator: /^!/,
        content: {
          pattern: /(^\[)[^\]]+(?=\])/,
          lookbehind: true,
          inside: {}
        },
        variable: {
          pattern: /(^\][ \t]?\[)[^\]]+(?=\]$)/,
          lookbehind: true
        },
        url: { pattern: /(^\]\()[^\s)]+/, lookbehind: true },
        string: {
          pattern: /(^[ \t]+)"(?:\\.|[^"\\])*"(?=\)$)/,
          lookbehind: true
        }
      }
    }
  }), ["url", "bold", "italic", "strike"].forEach(function(e3) {
    ["url", "bold", "italic", "strike", "code-snippet"].forEach(function(t3) {
      e3 !== t3 && (Prism2.languages.markdown[e3].inside.content.inside[t3] = Prism2.languages.markdown[t3]);
    });
  }), Prism2.hooks.add("after-tokenize", function(Prism3) {
    "markdown" !== Prism3.language && "md" !== Prism3.language || (function n2(e3) {
      if (e3 && "string" != typeof e3)
        for (var t3 = 0, a3 = e3.length; t3 < a3; t3++) {
          var i3 = e3[t3];
          if ("code" === i3.type) {
            var r3 = i3.content[1], o3 = i3.content[3];
            if (r3 && o3 && "code-language" === r3.type && "code-block" === o3.type && "string" == typeof r3.content) {
              var l3 = r3.content.replace(/\b#/g, "sharp").replace(/\b\+\+/g, "pp"), s2 = "language-" + (l3 = (/[a-z][\w-]*/i.exec(l3) || [""])[0].toLowerCase());
              o3.alias ? "string" == typeof o3.alias ? o3.alias = [o3.alias, s2] : o3.alias.push(s2) : o3.alias = [s2];
            }
          } else
            n2(i3.content);
        }
    })(Prism3.tokens);
  }), Prism2.hooks.add("wrap", function(e3) {
    if ("code-block" === e3.type) {
      for (var t3 = "", a3 = 0, i3 = e3.classes.length; a3 < i3; a3++) {
        var s2 = e3.classes[a3], d2 = /language-(.+)/.exec(s2);
        if (d2) {
          t3 = d2[1];
          break;
        }
      }
      var p2 = Prism2.languages[t3];
      if (p2)
        e3.content = Prism2.highlight(e3.content.replace(r2, "").replace(/&(\w{1,8}|#x?[\da-f]{1,8});/gi, function(Prism3, e4) {
          var t4;
          return "#" === (e4 = e4.toLowerCase())[0] ? (t4 = "x" === e4[1] ? parseInt(e4.slice(2), 16) : Number(e4.slice(1)), l2(t4)) : o2[e4] || Prism3;
        }), p2, t3);
      else if (t3 && "none" !== t3 && Prism2.plugins.autoloader) {
        var u2 = "md-" + (/* @__PURE__ */ new Date()).valueOf() + "-" + Math.floor(1e16 * Math.random());
        e3.attributes.id = u2, Prism2.plugins.autoloader.loadLanguages(t3, function() {
          var e4 = document.getElementById(u2);
          e4 && (e4.innerHTML = Prism2.highlight(e4.textContent, Prism2.languages[t3], t3));
        });
      }
    }
  });
  var r2 = RegExp(Prism2.languages.markup.tag.pattern.source, "gi"), o2 = { amp: "&", lt: "<", gt: ">", quot: '"' }, l2 = String.fromCodePoint || String.fromCharCode;
  Prism2.languages.md = Prism2.languages.markdown;
};
var prism_markdown_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_MARKDOWN
});
const LF_SYNTAX_MARKUP = (Prism2) => {
  Prism2.languages.markup = {
    comment: { pattern: /<!--(?:(?!<!--)[\s\S])*?-->/, greedy: true },
    prolog: { pattern: /<\?[\s\S]+?\?>/, greedy: true },
    doctype: {
      pattern: /<!DOCTYPE(?:[^>"'[\]]|"[^"]*"|'[^']*')+(?:\[(?:[^<"'\]]|"[^"]*"|'[^']*'|<(?!!--)|<!--(?:[^-]|-(?!->))*-->)*\]\s*)?>/i,
      greedy: true,
      inside: {
        "internal-subset": {
          pattern: /(^[^\[]*\[)[\s\S]+(?=\]>$)/,
          lookbehind: true,
          greedy: true,
          inside: null
        },
        string: { pattern: /"[^"]*"|'[^']*'/, greedy: true },
        punctuation: /^<!|>$|[[\]]/,
        "doctype-tag": /^DOCTYPE/i,
        name: /[^\s<>'"]+/
      }
    },
    cdata: { pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i, greedy: true },
    tag: {
      pattern: /<\/?(?!\d)[^\s>\/=$<%]+(?:\s(?:\s*[^\s>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))|(?=[\s/>])))+)?\s*\/?>/,
      greedy: true,
      inside: {
        tag: {
          pattern: /^<\/?[^\s>\/]+/,
          inside: {
            punctuation: /^<\/?/,
            namespace: /^[^\s>\/:]+:/
          }
        },
        "special-attr": [],
        "attr-value": {
          pattern: /=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+)/,
          inside: {
            punctuation: [
              { pattern: /^=/, alias: "attr-equals" },
              { pattern: /^(\s*)["']|["']$/, lookbehind: true }
            ]
          }
        },
        punctuation: /\/?>/,
        "attr-name": {
          pattern: /[^\s>\/]+/,
          inside: { namespace: /^[^\s>\/:]+:/ }
        }
      }
    },
    entity: [
      { pattern: /&[\da-z]{1,8};/i, alias: "named-entity" },
      /&#x?[\da-f]{1,8};/i
    ]
  }, Prism2.languages.markup.tag.inside["attr-value"].inside.entity = Prism2.languages.markup.entity, Prism2.languages.markup.doctype.inside["internal-subset"].inside = Prism2.languages.markup, Prism2.hooks.add("wrap", function(a2) {
    "entity" === a2.type && (a2.attributes.title = a2.content.replace(/&amp;/, "&"));
  }), Object.defineProperty(Prism2.languages.markup.tag, "addInlined", {
    value: function(a2, e2) {
      var s2 = {};
      s2["language-" + e2] = {
        pattern: /(^<!\[CDATA\[)[\s\S]+?(?=\]\]>$)/i,
        lookbehind: true,
        inside: Prism2.languages[e2]
      }, s2["cdata"] = /^<!\[CDATA\[|\]\]>$/i;
      var t2 = {
        "included-cdata": {
          pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
          inside: s2
        }
      };
      t2["language-" + e2] = {
        pattern: /[\s\S]+/,
        inside: Prism2.languages[e2]
      };
      var n2 = {};
      n2[a2] = {
        pattern: RegExp("(<__[^>]*>)(?:<!\\[CDATA\\[(?:[^\\]]|\\](?!\\]>))*\\]\\]>|(?!<!\\[CDATA\\[)[^])*?(?=</__>)".replace(/__/g, function() {
          return a2;
        }), "i"),
        lookbehind: true,
        greedy: true,
        inside: t2
      }, Prism2.languages.insertBefore("markup", "cdata", n2);
    }
  }), Object.defineProperty(Prism2.languages.markup.tag, "addAttribute", {
    value: function(a2, e2) {
      Prism2.languages.markup.tag.inside["special-attr"].push({
        pattern: RegExp(`(^|["'\\s])(?:` + a2 + `)\\s*=\\s*(?:"[^"]*"|'[^']*'|[^\\s'">=]+(?=[\\s>]))`, "i"),
        lookbehind: true,
        inside: {
          "attr-name": /^[^\s=]+/,
          "attr-value": {
            pattern: /=[\s\S]+/,
            inside: {
              value: {
                pattern: /(^=\s*(["']|(?!["'])))\S[\s\S]*(?=\2$)/,
                lookbehind: true,
                alias: [e2, "language-" + e2],
                inside: Prism2.languages[e2]
              },
              punctuation: [{ pattern: /^=/, alias: "attr-equals" }, /"|'/]
            }
          }
        }
      });
    }
  }), Prism2.languages.html = Prism2.languages.markup, Prism2.languages.mathml = Prism2.languages.markup, Prism2.languages.svg = Prism2.languages.markup, Prism2.languages.xml = Prism2.languages.extend("markup", {}), Prism2.languages.ssml = Prism2.languages.xml, Prism2.languages.atom = Prism2.languages.xml, Prism2.languages.rss = Prism2.languages.xml;
};
var prism_markup_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_MARKUP
});
const LF_SYNTAX_PYTHON = (Prism2) => {
  Prism2.languages.python = {
    comment: { pattern: /(^|[^\\])#.*/, lookbehind: true, greedy: true },
    "string-interpolation": {
      pattern: /(?:f|fr|rf)(?:("""|''')[\s\S]*?\1|("|')(?:\\.|(?!\2)[^\\\r\n])*\2)/i,
      greedy: true,
      inside: {
        interpolation: {
          pattern: /((?:^|[^{])(?:\{\{)*)\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}])+\})+\})+\}/,
          lookbehind: true,
          inside: {
            "format-spec": {
              pattern: /(:)[^:(){}]+(?=\}$)/,
              lookbehind: true
            },
            "conversion-option": {
              pattern: /![sra](?=[:}]$)/,
              alias: "punctuation"
            },
            rest: null
          }
        },
        string: /[\s\S]+/
      }
    },
    "triple-quoted-string": {
      pattern: /(?:[rub]|br|rb)?("""|''')[\s\S]*?\1/i,
      greedy: true,
      alias: "string"
    },
    string: {
      pattern: /(?:[rub]|br|rb)?("|')(?:\\.|(?!\1)[^\\\r\n])*\1/i,
      greedy: true
    },
    function: {
      pattern: /((?:^|\s)def[ \t]+)[a-zA-Z_]\w*(?=\s*\()/g,
      lookbehind: true
    },
    "class-name": { pattern: /(\bclass\s+)\w+/i, lookbehind: true },
    decorator: {
      pattern: /(^[\t ]*)@\w+(?:\.\w+)*/m,
      lookbehind: true,
      alias: ["annotation", "punctuation"],
      inside: { punctuation: /\./ }
    },
    keyword: /\b(?:_(?=\s*:)|and|as|assert|async|await|break|case|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|match|nonlocal|not|or|pass|print|raise|return|try|while|with|yield)\b/,
    builtin: /\b(?:__import__|abs|all|any|apply|ascii|basestring|bin|bool|buffer|bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|complex|delattr|dict|dir|divmod|enumerate|eval|execfile|file|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|intern|isinstance|issubclass|iter|len|list|locals|long|map|max|memoryview|min|next|object|oct|open|ord|pow|property|range|raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|vars|xrange|zip)\b/,
    boolean: /\b(?:False|None|True)\b/,
    number: /\b0(?:b(?:_?[01])+|o(?:_?[0-7])+|x(?:_?[a-f0-9])+)\b|(?:\b\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\B\.\d+(?:_\d+)*)(?:e[+-]?\d+(?:_\d+)*)?j?(?!\w)/i,
    operator: /[-+%=]=?|!=|:=|\*\*?=?|\/\/?=?|<[<=>]?|>[=>]?|[&|^~]/,
    punctuation: /[{}[\];(),.:]/
  }, Prism2.languages.python["string-interpolation"].inside.interpolation.inside.rest = Prism2.languages.python, Prism2.languages.py = Prism2.languages.python;
};
var prism_python_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_PYTHON
});
const LF_SYNTAX_REGEX = (Prism2) => {
  var e2 = { pattern: /\\[\\(){}[\]^$+*?|.]/, alias: "escape" }, n2 = /\\(?:x[\da-fA-F]{2}|u[\da-fA-F]{4}|u\{[\da-fA-F]+\}|0[0-7]{0,2}|[123][0-7]{2}|c[a-zA-Z]|.)/, t2 = "(?:[^\\\\-]|" + n2.source + ")", s2 = RegExp(t2 + "-" + t2), i2 = {
    pattern: /(<|')[^<>']+(?=[>']$)/,
    lookbehind: true,
    alias: "variable"
  };
  Prism2.languages.regex = {
    "char-class": {
      pattern: /((?:^|[^\\])(?:\\\\)*)\[(?:[^\\\]]|\\[\s\S])*\]/,
      lookbehind: true,
      inside: {
        "char-class-negation": {
          pattern: /(^\[)\^/,
          lookbehind: true,
          alias: "operator"
        },
        "char-class-punctuation": {
          pattern: /^\[|\]$/,
          alias: "punctuation"
        },
        range: {
          pattern: s2,
          inside: {
            escape: n2,
            "range-punctuation": {
              pattern: /-/,
              alias: "operator"
            }
          }
        },
        "special-escape": e2,
        "char-set": {
          pattern: /\\[wsd]|\\p\{[^{}]+\}/i,
          alias: "class-name"
        },
        escape: n2
      }
    },
    "special-escape": e2,
    "char-set": {
      pattern: /\.|\\[wsd]|\\p\{[^{}]+\}/i,
      alias: "class-name"
    },
    backreference: [
      { pattern: /\\(?![123][0-7]{2})[1-9]/, alias: "keyword" },
      {
        pattern: /\\k<[^<>']+>/,
        alias: "keyword",
        inside: { "group-name": i2 }
      }
    ],
    anchor: { pattern: /[$^]|\\[ABbGZz]/, alias: "function" },
    escape: n2,
    group: [
      {
        pattern: /\((?:\?(?:<[^<>']+>|'[^<>']+'|[>:]|<?[=!]|[idmnsuxU]+(?:-[idmnsuxU]+)?:?))?/,
        alias: "punctuation",
        inside: { "group-name": i2 }
      },
      { pattern: /\)/, alias: "punctuation" }
    ],
    quantifier: {
      pattern: /(?:[+*?]|\{\d+(?:,\d*)?\})[?+]?/,
      alias: "number"
    },
    alternation: { pattern: /\|/, alias: "keyword" }
  };
};
var prism_regex_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_REGEX
});
const LF_SYNTAX_SCSS = (Prism2) => {
  Prism2.languages.scss = Prism2.languages.extend("css", {
    comment: {
      pattern: /(^|[^\\])(?:\/\*[\s\S]*?\*\/|\/\/.*)/,
      lookbehind: true
    },
    atrule: {
      pattern: /@[\w-](?:\([^()]+\)|[^()\s]|\s+(?!\s))*?(?=\s+[{;])/,
      inside: { rule: /@[\w-]+/ }
    },
    url: /(?:[-a-z]+-)?url(?=\()/i,
    selector: {
      pattern: /(?=\S)[^@;{}()]?(?:[^@;{}()\s]|\s+(?!\s)|#\{\$[-\w]+\})+(?=\s*\{(?:\}|\s|[^}][^:{}]*[:{][^}]))/,
      inside: {
        parent: { pattern: /&/, alias: "important" },
        placeholder: /%[-\w]+/,
        variable: /\$[-\w]+|#\{\$[-\w]+\}/
      }
    },
    property: {
      pattern: /(?:[-\w]|\$[-\w]|#\{\$[-\w]+\})+(?=\s*:)/,
      inside: { variable: /\$[-\w]+|#\{\$[-\w]+\}/ }
    }
  }), Prism2.languages.insertBefore("scss", "atrule", {
    keyword: [
      /@(?:content|debug|each|else(?: if)?|extend|for|forward|function|if|import|include|mixin|return|use|warn|while)\b/i,
      { pattern: /( )(?:from|through)(?= )/, lookbehind: true }
    ]
  }), Prism2.languages.insertBefore("scss", "important", {
    variable: /\$[-\w]+|#\{\$[-\w]+\}/
  }), Prism2.languages.insertBefore("scss", "function", {
    "module-modifier": {
      pattern: /\b(?:as|hide|show|with)\b/i,
      alias: "keyword"
    },
    placeholder: { pattern: /%[-\w]+/, alias: "selector" },
    statement: {
      pattern: /\B!(?:default|optional)\b/i,
      alias: "keyword"
    },
    boolean: /\b(?:false|true)\b/,
    null: { pattern: /\bnull\b/, alias: "keyword" },
    operator: {
      pattern: /(\s)(?:[-+*\/%]|[=!]=|<=?|>=?|and|not|or)(?=\s)/,
      lookbehind: true
    }
  }), Prism2.languages.scss.atrule.inside.rest = Prism2.languages.scss;
};
var prism_scss_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_SCSS
});
const LF_SYNTAX_TSX = (Prism2) => {
  var _a, _b, _c, _d, _e, _f;
  const a2 = Prism2.util.clone(Prism2.languages.typescript);
  Prism2.languages.tsx = Prism2.languages.extend("jsx", a2), (_b = (_a = Prism2 == null ? void 0 : Prism2.languages) == null ? void 0 : _a.tsx) == null ? true : delete _b.parameter, (_d = (_c = Prism2 == null ? void 0 : Prism2.languages) == null ? void 0 : _c.tsx) == null ? true : delete _d["literal-property"];
  const t2 = (_f = (_e = Prism2.languages) == null ? void 0 : _e.tsx) == null ? void 0 : _f.tag;
  t2.pattern = RegExp("(^|[^\\w$]|(?=</))(?:" + t2.pattern.source + ")", t2.pattern.flags), t2.lookbehind = true;
};
var prism_tsx_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_TSX
});
const LF_SYNTAX_TYPESCRIPT = (Prism2) => {
  Prism2.languages.typescript = Prism2.languages.extend("javascript", {
    "class-name": {
      pattern: /(\b(?:class|extends|implements|instanceof|interface|new|type)\s+)(?!keyof\b)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?:\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>)?/,
      lookbehind: true,
      greedy: true,
      inside: null
    },
    builtin: /\b(?:Array|Function|Promise|any|boolean|console|never|number|string|symbol|unknown)\b/
  }), Prism2.languages.typescript.keyword.push(/\b(?:abstract|declare|is|keyof|readonly|require)\b/, /\b(?:asserts|infer|interface|module|namespace|type)\b(?=\s*(?:[{_$a-zA-Z\xA0-\uFFFF]|$))/, /\btype\b(?=\s*(?:[\{*]|$))/), delete Prism2.languages.typescript.parameter, delete Prism2.languages.typescript["literal-property"];
  var s2 = Prism2.languages.extend("typescript", {});
  delete s2["class-name"], Prism2.languages.typescript["class-name"].inside = s2, Prism2.languages.insertBefore("typescript", "function", {
    decorator: {
      pattern: /@[$\w\xA0-\uFFFF]+/,
      inside: {
        at: { pattern: /^@/, alias: "operator" },
        function: /^[\s\S]+/
      }
    },
    "generic-function": {
      pattern: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>(?=\s*\()/,
      greedy: true,
      inside: {
        function: /^#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*/,
        generic: {
          pattern: /<[\s\S]+/,
          alias: "class-name",
          inside: s2
        }
      }
    }
  }), Prism2.languages.ts = Prism2.languages.typescript;
};
var prism_typescript_highlight = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  LF_SYNTAX_TYPESCRIPT
});
const isClient = typeof window !== "undefined";
let lfFramework = null;
function getLfFramework() {
  if (!lfFramework) {
    initLfFramework();
    if (!lfFramework) {
      throw new Error("Failed to initialize LfFramework.");
    }
  }
  return lfFramework;
}
function initLfFramework() {
  const isInitialized = isClient && window[LF_FRAMEWORK_SYMBOL] || lfFramework;
  if (isInitialized) {
    return;
  }
  const framework = new LfFramework();
  lfFramework = framework;
  if (isClient) {
    finalize(framework);
  }
}
const finalize = (framework) => {
  window[LF_FRAMEWORK_SYMBOL] = framework;
  markFrameworkReady(framework);
  const ev = new CustomEvent(LF_FRAMEWORK_EVENT_NAME, {
    detail: { lfFramework: framework }
  });
  document.dispatchEvent(ev);
};
const __variableDynamicImportRuntimeHelper = (glob, path, segs) => {
  const v2 = glob[path];
  if (v2) {
    return typeof v2 === "function" ? v2() : Promise.resolve(v2);
  }
  return new Promise((_2, reject) => {
    (typeof queueMicrotask === "function" ? queueMicrotask : setTimeout)(
      reject.bind(
        null,
        new Error(
          "Unknown variable dynamic import: " + path + (path.split("/").length !== segs ? ". Note that variables only represent file names one level deep." : "")
        )
      )
    );
  });
};
var t = Object.defineProperty, e = (t2) => {
  if (t2.__stencil__getHostRef) return t2.__stencil__getHostRef();
}, n = (t2, e2) => {
  e2 && (t2.__stencil__getHostRef = () => e2, e2.t = t2);
}, o$1 = (t2, e2) => e2 in t2, l = (t2, e2) => (0, console.error)(t2, e2), i = /* @__PURE__ */ new Map(), r = /* @__PURE__ */ new Map(), s = "slot-fb{display:contents}slot-fb[hidden]{display:none}", c = "http://www.w3.org/1999/xlink", u = "undefined" != typeof window ? window : {}, a = { o: 0, l: "", jmp: (t2) => t2(), raf: (t2) => requestAnimationFrame(t2), ael: (t2, e2, n2, o2) => t2.addEventListener(e2, n2, o2), rel: (t2, e2, n2, o2) => t2.removeEventListener(e2, n2, o2), ce: (t2, e2) => new CustomEvent(t2, e2) }, f = (t2) => Promise.resolve(t2), d = (() => {
  try {
    return new CSSStyleSheet(), "function" == typeof new CSSStyleSheet().replaceSync;
  } catch (t2) {
  }
  return false;
})(), h = !!d && (() => !!u.document && Object.getOwnPropertyDescriptor(u.document.adoptedStyleSheets, "length").writable)(), p = false, v = [], m = [], y = (t2, e2) => (n2) => {
  t2.push(n2), p || (p = true, 4 & a.o ? $(b) : a.raf(b));
}, w = (t2) => {
  for (let e2 = 0; e2 < t2.length; e2++) try {
    t2[e2](performance.now());
  } catch (t3) {
    l(t3);
  }
  t2.length = 0;
}, b = () => {
  w(v), w(m), (p = v.length > 0) && a.raf(b);
}, $ = (t2) => f().then(t2), g = y(m), S = (t2) => "object" == (t2 = typeof t2) || "function" === t2;
function j(t2) {
  var e2, n2, o2;
  return null != (o2 = null == (n2 = null == (e2 = t2.head) ? void 0 : e2.querySelector('meta[name="csp-nonce"]')) ? void 0 : n2.getAttribute("content")) ? o2 : void 0;
}
((e2, n2) => {
  for (var o2 in n2) t(e2, o2, { get: n2[o2], enumerable: true });
})({}, { err: () => O, map: () => E, ok: () => k, unwrap: () => C, unwrapErr: () => M });
var k = (t2) => ({ isOk: true, isErr: false, value: t2 }), O = (t2) => ({ isOk: false, isErr: true, value: t2 });
function E(t2, e2) {
  if (t2.isOk) {
    const n2 = e2(t2.value);
    return n2 instanceof Promise ? n2.then(((t3) => k(t3))) : k(n2);
  }
  if (t2.isErr) return O(t2.value);
  throw "should never get here";
}
var x, C = (t2) => {
  if (t2.isOk) return t2.value;
  throw t2.value;
}, M = (t2) => {
  if (t2.isErr) return t2.value;
  throw t2.value;
};
function P() {
  const t2 = this.attachShadow({ mode: "open" });
  void 0 === x && (x = null), x && (h ? t2.adoptedStyleSheets.push(x) : t2.adoptedStyleSheets = [...t2.adoptedStyleSheets, x]);
}
var N = /* @__PURE__ */ new WeakMap(), R = (t2) => "sc-" + t2.i, D = (t2, e2, ...n2) => {
  let o2 = null, l2 = null, i2 = false, r2 = false;
  const s2 = [], c2 = (e3) => {
    for (let n3 = 0; n3 < e3.length; n3++) o2 = e3[n3], Array.isArray(o2) ? c2(o2) : null != o2 && "boolean" != typeof o2 && ((i2 = "function" != typeof t2 && !S(o2)) && (o2 += ""), i2 && r2 ? s2[s2.length - 1].u += o2 : s2.push(i2 ? U(null, o2) : o2), r2 = i2);
  };
  if (c2(n2), e2) {
    e2.key && (l2 = e2.key);
    {
      const t3 = e2.className || e2.class;
      t3 && (e2.class = "object" != typeof t3 ? t3 : Object.keys(t3).filter(((e3) => t3[e3])).join(" "));
    }
  }
  if ("function" == typeof t2) return t2(null === e2 ? {} : e2, s2, A);
  const u2 = U(t2, null);
  return u2.h = e2, s2.length > 0 && (u2.p = s2), u2.v = l2, u2;
}, U = (t2, e2) => ({ o: 0, m: t2, u: e2, $: null, p: null, h: null, v: null }), W$1 = {}, A = { forEach: (t2, e2) => t2.map(F).forEach(e2), map: (t2, e2) => t2.map(F).map(e2).map(H) }, F = (t2) => ({ vattrs: t2.h, vchildren: t2.p, vkey: t2.v, vname: t2.S, vtag: t2.m, vtext: t2.u }), H = (t2) => {
  if ("function" == typeof t2.vtag) {
    const e3 = { ...t2.vattrs };
    return t2.vkey && (e3.key = t2.vkey), t2.vname && (e3.name = t2.vname), D(t2.vtag, e3, ...t2.vchildren || []);
  }
  const e2 = U(t2.vtag, t2.vtext);
  return e2.h = t2.vattrs, e2.p = t2.vchildren, e2.v = t2.vkey, e2.S = t2.vname, e2;
}, L = (t2) => {
  const e2 = ((t3) => t3.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))(t2);
  return RegExp(`(^|[^@]|@(?!supports\\s+selector\\s*\\([^{]*?${e2}))(${e2}\\b)`, "g");
};
L("::slotted"), L(":host"), L(":host-context");
var T, q = (t2, e2) => null == t2 || S(t2) ? t2 : 4 & e2 ? "false" !== t2 && ("" === t2 || !!t2) : 2 & e2 ? "string" == typeof t2 ? parseFloat(t2) : "number" == typeof t2 ? t2 : NaN : 1 & e2 ? t2 + "" : t2, z = (t2) => {
  var n2;
  return null == (n2 = e(t2)) ? void 0 : n2.$hostElement$;
}, V = (t2, e2) => {
  const n2 = z(t2);
  return { emit: (t3) => G(n2, e2, { bubbles: true, composed: true, cancelable: false, detail: t3 }) };
}, G = (t2, e2, n2) => {
  const o2 = a.ce(e2, n2);
  return t2.dispatchEvent(o2), o2;
}, I = (t2, e2, n2, l2, i2, r2) => {
  if (n2 === l2) return;
  let s2 = o$1(t2, e2), f2 = e2.toLowerCase();
  if ("class" === e2) {
    const e3 = t2.classList, o2 = _(n2);
    let i3 = _(l2);
    e3.remove(...o2.filter(((t3) => t3 && !i3.includes(t3)))), e3.add(...i3.filter(((t3) => t3 && !o2.includes(t3))));
  } else if ("style" === e2) {
    for (const e3 in n2) l2 && null != l2[e3] || (e3.includes("-") ? t2.style.removeProperty(e3) : t2.style[e3] = "");
    for (const e3 in l2) n2 && l2[e3] === n2[e3] || (e3.includes("-") ? t2.style.setProperty(e3, l2[e3]) : t2.style[e3] = l2[e3]);
  } else if ("key" === e2) ;
  else if ("ref" === e2) l2 && l2(t2);
  else if (s2 || "o" !== e2[0] || "n" !== e2[1]) {
    const o2 = S(l2);
    if ((s2 || o2 && null !== l2) && !i2) try {
      if (t2.tagName.includes("-")) t2[e2] !== l2 && (t2[e2] = l2);
      else {
        const o3 = null == l2 ? "" : l2;
        "list" === e2 ? s2 = false : null != n2 && t2[e2] == o3 || ("function" == typeof t2.__lookupSetter__(e2) ? t2[e2] = o3 : t2.setAttribute(e2, o3));
      }
    } catch (t3) {
    }
    let u2 = false;
    f2 !== (f2 = f2.replace(/^xlink\:?/, "")) && (e2 = f2, u2 = true), null == l2 || false === l2 ? false === l2 && "" !== t2.getAttribute(e2) || (u2 ? t2.removeAttributeNS(c, e2) : t2.removeAttribute(e2)) : (!s2 || 4 & r2 || i2) && !o2 && 1 === t2.nodeType && (l2 = true === l2 ? "" : l2, u2 ? t2.setAttributeNS(c, e2, l2) : t2.setAttribute(e2, l2));
  } else if (e2 = "-" === e2[2] ? e2.slice(3) : o$1(u, f2) ? f2.slice(2) : f2[2] + e2.slice(3), n2 || l2) {
    const o2 = e2.endsWith(B);
    e2 = e2.replace(J, ""), n2 && a.rel(t2, e2, n2, o2), l2 && a.ael(t2, e2, l2, o2);
  }
}, Y = /\s/, _ = (t2) => ("object" == typeof t2 && t2 && "baseVal" in t2 && (t2 = t2.baseVal), t2 && "string" == typeof t2 ? t2.split(Y) : []), B = "Capture", J = RegExp(B + "$"), K = (t2, e2, n2) => {
  const o2 = 11 === e2.$.nodeType && e2.$.host ? e2.$.host : e2.$, l2 = t2 && t2.h || {}, i2 = e2.h || {};
  for (const t3 of Q(Object.keys(l2))) t3 in i2 || I(o2, t3, l2[t3], void 0, n2, e2.o);
  for (const t3 of Q(Object.keys(i2))) I(o2, t3, l2[t3], i2[t3], n2, e2.o);
};
function Q(t2) {
  return t2.includes("ref") ? [...t2.filter(((t3) => "ref" !== t3)), "ref"] : t2;
}
var X = false, Z = (t2, e2, n2) => {
  const o2 = e2.p[n2];
  let l2, i2, r2 = 0;
  if (null !== o2.u) l2 = o2.$ = u.document.createTextNode(o2.u);
  else {
    if (X || (X = "svg" === o2.m), !u.document) throw Error("You are trying to render a Stencil component in an environment that doesn't support the DOM. Make sure to populate the [`window`](https://developer.mozilla.org/en-US/docs/Web/API/Window/window) object before rendering a component.");
    if (l2 = o2.$ = u.document.createElementNS(X ? "http://www.w3.org/2000/svg" : "http://www.w3.org/1999/xhtml", o2.m), X && "foreignObject" === o2.m && (X = false), K(null, o2, X), o2.p) for (r2 = 0; r2 < o2.p.length; ++r2) i2 = Z(t2, o2, r2), i2 && l2.appendChild(i2);
    "svg" === o2.m ? X = false : "foreignObject" === l2.tagName && (X = true);
  }
  return l2["s-hn"] = T, l2;
}, tt = (t2, e2, n2, o2, l2, i2) => {
  let r2, s2 = t2;
  for (s2.shadowRoot && s2.tagName === T && (s2 = s2.shadowRoot); l2 <= i2; ++l2) o2[l2] && (r2 = Z(null, n2, l2), r2 && (o2[l2].$ = r2, it(s2, r2, e2)));
}, et = (t2, e2, n2) => {
  for (let o2 = e2; o2 <= n2; ++o2) {
    const e3 = t2[o2];
    if (e3) {
      const t3 = e3.$;
      lt(e3), t3 && t3.remove();
    }
  }
}, nt = (t2, e2, n2 = false) => t2.m === e2.m && (n2 ? (n2 && !t2.v && e2.v && (t2.v = e2.v), true) : t2.v === e2.v), ot = (t2, e2, n2 = false) => {
  const o2 = e2.$ = t2.$, l2 = t2.p, i2 = e2.p, r2 = e2.m, s2 = e2.u;
  null === s2 ? (K(t2, e2, X = "svg" === r2 || "foreignObject" !== r2 && X), null !== l2 && null !== i2 ? ((t3, e3, n3, o3, l3 = false) => {
    let i3, r3, s3 = 0, c2 = 0, u2 = 0, a2 = 0, f2 = e3.length - 1, d2 = e3[0], h2 = e3[f2], p2 = o3.length - 1, v2 = o3[0], m2 = o3[p2];
    for (; s3 <= f2 && c2 <= p2; ) if (null == d2) d2 = e3[++s3];
    else if (null == h2) h2 = e3[--f2];
    else if (null == v2) v2 = o3[++c2];
    else if (null == m2) m2 = o3[--p2];
    else if (nt(d2, v2, l3)) ot(d2, v2, l3), d2 = e3[++s3], v2 = o3[++c2];
    else if (nt(h2, m2, l3)) ot(h2, m2, l3), h2 = e3[--f2], m2 = o3[--p2];
    else if (nt(d2, m2, l3)) ot(d2, m2, l3), it(t3, d2.$, h2.$.nextSibling), d2 = e3[++s3], m2 = o3[--p2];
    else if (nt(h2, v2, l3)) ot(h2, v2, l3), it(t3, h2.$, d2.$), h2 = e3[--f2], v2 = o3[++c2];
    else {
      for (u2 = -1, a2 = s3; a2 <= f2; ++a2) if (e3[a2] && null !== e3[a2].v && e3[a2].v === v2.v) {
        u2 = a2;
        break;
      }
      u2 >= 0 ? (r3 = e3[u2], r3.m !== v2.m ? i3 = Z(e3 && e3[c2], n3, u2) : (ot(r3, v2, l3), e3[u2] = void 0, i3 = r3.$), v2 = o3[++c2]) : (i3 = Z(e3 && e3[c2], n3, c2), v2 = o3[++c2]), i3 && it(d2.$.parentNode, i3, d2.$);
    }
    s3 > f2 ? tt(t3, null == o3[p2 + 1] ? null : o3[p2 + 1].$, n3, o3, c2, p2) : c2 > p2 && et(e3, s3, f2);
  })(o2, l2, e2, i2, n2) : null !== i2 ? (null !== t2.u && (o2.textContent = ""), tt(o2, null, e2, i2, 0, i2.length - 1)) : !n2 && null !== l2 && et(l2, 0, l2.length - 1), X && "svg" === r2 && (X = false)) : t2.u !== s2 && (o2.data = s2);
}, lt = (t2) => {
  t2.h && t2.h.ref && t2.h.ref(null), t2.p && t2.p.map(lt);
}, it = (t2, e2, n2) => null == t2 ? void 0 : t2.insertBefore(e2, n2), rt = (t2, e2) => {
  if (e2 && !t2.j && e2["s-p"]) {
    const n2 = e2["s-p"].push(new Promise(((o2) => t2.j = () => {
      e2["s-p"].splice(n2 - 1, 1), o2();
    })));
  }
}, st = (t2, e2) => {
  if (t2.o |= 16, 4 & t2.o) return void (t2.o |= 512);
  rt(t2, t2.k);
  const n2 = () => ct(t2, e2);
  if (!e2) return g(n2);
  queueMicrotask((() => {
    n2();
  }));
}, ct = (t2, e2) => {
  const n2 = t2.$hostElement$, o2 = t2.t;
  if (!o2) throw Error(`Can't render component <${n2.tagName.toLowerCase()} /> with invalid Stencil runtime! Make sure this imported component is compiled with a \`externalRuntime: true\` flag. For more information, please refer to https://stenciljs.com/docs/custom-elements#externalruntime`);
  let l2;
  return e2 ? (t2.o |= 256, t2.O && (t2.O.map((([t3, e3]) => mt(o2, t3, e3, n2))), t2.O = void 0), l2 = mt(o2, "componentWillLoad", void 0, n2)) : l2 = mt(o2, "componentWillUpdate", void 0, n2), l2 = ut(l2, (() => mt(o2, "componentWillRender", void 0, n2))), ut(l2, (() => ft(t2, o2, e2)));
}, ut = (t2, e2) => at(t2) ? t2.then(e2).catch(((t3) => {
  console.error(t3), e2();
})) : e2(), at = (t2) => t2 instanceof Promise || t2 && t2.then && "function" == typeof t2.then, ft = async (t2, e2, n2) => {
  var o2;
  const l2 = t2.$hostElement$, i2 = l2["s-rc"];
  n2 && ((t3) => {
    const e3 = t3.C, n3 = t3.$hostElement$, o3 = e3.o, l3 = ((t4, e4) => {
      var n4;
      const o4 = R(e4), l4 = r.get(o4);
      if (!u.document) return o4;
      if (t4 = 11 === t4.nodeType ? t4 : u.document, l4) if ("string" == typeof l4) {
        let i3, r2 = N.get(t4 = t4.head || t4);
        if (r2 || N.set(t4, r2 = /* @__PURE__ */ new Set()), !r2.has(o4)) {
          {
            i3 = u.document.createElement("style"), i3.innerHTML = l4;
            const o5 = null != (n4 = a.M) ? n4 : j(u.document);
            if (null != o5 && i3.setAttribute("nonce", o5), !(1 & e4.o)) if ("HEAD" === t4.nodeName) {
              const e5 = t4.querySelectorAll("link[rel=preconnect]"), n5 = e5.length > 0 ? e5[e5.length - 1].nextSibling : t4.querySelector("style");
              t4.insertBefore(i3, (null == n5 ? void 0 : n5.parentNode) === t4 ? n5 : null);
            } else if ("host" in t4) if (d) {
              const e5 = new CSSStyleSheet();
              e5.replaceSync(l4), h ? t4.adoptedStyleSheets.unshift(e5) : t4.adoptedStyleSheets = [e5, ...t4.adoptedStyleSheets];
            } else {
              const e5 = t4.querySelector("style");
              e5 ? e5.innerHTML = l4 + e5.innerHTML : t4.prepend(i3);
            }
            else t4.append(i3);
            1 & e4.o && t4.insertBefore(i3, null);
          }
          4 & e4.o && (i3.innerHTML += s), r2 && r2.add(o4);
        }
      } else t4.adoptedStyleSheets.includes(l4) || (h ? t4.adoptedStyleSheets.push(l4) : t4.adoptedStyleSheets = [...t4.adoptedStyleSheets, l4]);
      return o4;
    })(n3.shadowRoot ? n3.shadowRoot : n3.getRootNode(), e3);
    10 & o3 && (n3["s-sc"] = l3, n3.classList.add(l3 + "-h"));
  })(t2);
  dt(t2, e2, l2, n2), i2 && (i2.map(((t3) => t3())), l2["s-rc"] = void 0);
  {
    const e3 = null != (o2 = l2["s-p"]) ? o2 : [], n3 = () => ht(t2);
    0 === e3.length ? n3() : (Promise.all(e3).then(n3), t2.o |= 4, e3.length = 0);
  }
}, dt = (t2, e2, n2, o2) => {
  try {
    e2 = e2.render(), t2.o &= -17, t2.o |= 2, ((t3, e3, n3 = false) => {
      const o3 = t3.$hostElement$, l2 = t3.C, i2 = t3.P || U(null, null), r2 = ((t4) => t4 && t4.m === W$1)(e3) ? e3 : D(null, null, e3);
      if (T = o3.tagName, l2.N && (r2.h = r2.h || {}, l2.N.map((([t4, e4]) => r2.h[e4] = o3[t4]))), n3 && r2.h) for (const t4 of Object.keys(r2.h)) o3.hasAttribute(t4) && !["key", "ref", "style", "class"].includes(t4) && (r2.h[t4] = o3[t4]);
      r2.m = null, r2.o |= 4, t3.P = r2, r2.$ = i2.$ = o3.shadowRoot || o3, ot(i2, r2, n3);
    })(t2, e2, o2);
  } catch (e3) {
    l(e3, t2.$hostElement$);
  }
  return null;
}, ht = (t2) => {
  const e2 = t2.$hostElement$, n2 = t2.t, o2 = t2.k;
  mt(n2, "componentDidRender", void 0, e2), 64 & t2.o ? mt(n2, "componentDidUpdate", void 0, e2) : (t2.o |= 64, yt(e2), mt(n2, "componentDidLoad", void 0, e2), t2.R(e2), o2 || vt()), t2.D(e2), t2.j && (t2.j(), t2.j = void 0), 512 & t2.o && $((() => st(t2, false))), t2.o &= -517;
}, pt = (t2) => {
  var n2;
  {
    const o2 = e(t2), l2 = null == (n2 = null == o2 ? void 0 : o2.$hostElement$) ? void 0 : n2.isConnected;
    return l2 && 2 == (18 & o2.o) && st(o2, false), l2;
  }
}, vt = () => {
  $((() => G(u, "appload", { detail: { namespace: "lf-core" } })));
}, mt = (t2, e2, n2, o2) => {
  if (t2 && t2[e2]) try {
    return t2[e2](n2);
  } catch (t3) {
    l(t3, o2);
  }
}, yt = (t2) => t2.setAttribute("lf-hydrated", ""), wt = (t2, n2, o2, i2) => {
  const r2 = e(t2);
  if (!r2) return;
  if (!r2) throw Error(`Couldn't find host element for "${i2.i}" as it is unknown to this Stencil runtime. This usually happens when integrating a 3rd party Stencil component with another Stencil component or application. Please reach out to the maintainers of the 3rd party Stencil component or report this on the Stencil Discord server (https://chat.stenciljs.com) or comment on this similar [GitHub issue](https://github.com/stenciljs/core/issues/5457).`);
  const s2 = r2.$hostElement$, c2 = r2.U.get(n2), u2 = r2.o, a2 = r2.t;
  if (o2 = q(o2, i2.W[n2][0]), (!(8 & u2) || void 0 === c2) && o2 !== c2 && (!Number.isNaN(c2) || !Number.isNaN(o2)) && (r2.U.set(n2, o2), a2)) {
    if (i2.A && 128 & u2) {
      const t3 = i2.A[n2];
      t3 && t3.map(((t4) => {
        try {
          a2[t4](o2, c2, n2);
        } catch (t5) {
          l(t5, s2);
        }
      }));
    }
    if (2 == (18 & u2)) {
      if (a2.componentShouldUpdate && false === a2.componentShouldUpdate(o2, c2, n2)) return;
      st(r2, false);
    }
  }
}, bt = (t2, n2, o2) => {
  var l2, i2;
  const r2 = t2.prototype;
  if (n2.W || n2.A || t2.watchers) {
    t2.watchers && !n2.A && (n2.A = t2.watchers);
    const s2 = Object.entries(null != (l2 = n2.W) ? l2 : {});
    if (s2.map((([t3, [l3]]) => {
      if (31 & l3 || 2 & o2 && 32 & l3) {
        const { get: i3, set: s3 } = Object.getOwnPropertyDescriptor(r2, t3) || {};
        i3 && (n2.W[t3][0] |= 2048), s3 && (n2.W[t3][0] |= 4096), (1 & o2 || !i3) && Object.defineProperty(r2, t3, { get() {
          {
            if (!(2048 & n2.W[t3][0])) return ((t4, n3) => e(this).U.get(n3))(0, t3);
            const o3 = e(this), l4 = o3 ? o3.t : r2;
            if (!l4) return;
            return l4[t3];
          }
        }, configurable: true, enumerable: true }), Object.defineProperty(r2, t3, { set(i4) {
          const r3 = e(this);
          if (r3) {
            if (s3) {
              const e2 = 32 & l3 ? this[t3] : r3.$hostElement$[t3];
              return void 0 === e2 && r3.U.get(t3) ? i4 = r3.U.get(t3) : !r3.U.get(t3) && e2 && r3.U.set(t3, e2), s3.call(this, q(i4, l3)), void wt(this, t3, i4 = 32 & l3 ? this[t3] : r3.$hostElement$[t3], n2);
            }
            {
              if (!(1 & o2 && 4096 & n2.W[t3][0])) return wt(this, t3, i4, n2), void (1 & o2 && !r3.t && r3.F.then((() => {
                4096 & n2.W[t3][0] && r3.t[t3] !== r3.U.get(t3) && (r3.t[t3] = i4);
              })));
              const e2 = () => {
                const e3 = r3.t[t3];
                !r3.U.get(t3) && e3 && r3.U.set(t3, e3), r3.t[t3] = q(i4, l3), wt(this, t3, r3.t[t3], n2);
              };
              r3.t ? e2() : r3.F.then((() => e2()));
            }
          }
        } });
      } else 1 & o2 && 64 & l3 && Object.defineProperty(r2, t3, { value(...n3) {
        var o3;
        const l4 = e(this);
        return null == (o3 = null == l4 ? void 0 : l4.H) ? void 0 : o3.then((() => {
          var e2;
          return null == (e2 = l4.t) ? void 0 : e2[t3](...n3);
        }));
      } });
    })), 1 & o2) {
      const o3 = /* @__PURE__ */ new Map();
      r2.attributeChangedCallback = function(t3, l3, i3) {
        a.jmp((() => {
          var s3;
          const c2 = o3.get(t3);
          if (this.hasOwnProperty(c2)) i3 = this[c2], delete this[c2];
          else {
            if (r2.hasOwnProperty(c2) && "number" == typeof this[c2] && this[c2] == i3) return;
            if (null == c2) {
              const o4 = e(this), r3 = null == o4 ? void 0 : o4.o;
              if (o4 && r3 && !(8 & r3) && 128 & r3 && i3 !== l3) {
                const e2 = o4.t, r4 = null == (s3 = n2.A) ? void 0 : s3[t3];
                null == r4 || r4.forEach(((n3) => {
                  null != e2[n3] && e2[n3].call(e2, i3, l3, t3);
                }));
              }
              return;
            }
          }
          const u2 = Object.getOwnPropertyDescriptor(r2, c2);
          (i3 = (null !== i3 || "boolean" != typeof this[c2]) && i3) === this[c2] || u2.get && !u2.set || (this[c2] = i3);
        }));
      }, t2.observedAttributes = Array.from(/* @__PURE__ */ new Set([...Object.keys(null != (i2 = n2.A) ? i2 : {}), ...s2.filter((([t3, e2]) => 31 & e2[0])).map((([t3, e2]) => {
        var l3;
        const i3 = e2[1] || t3;
        return o3.set(i3, t3), 512 & e2[0] && (null == (l3 = n2.N) || l3.push([t3, i3])), i3;
      }))]));
    }
  }
  return t2;
}, $t = (t2, e2) => {
  mt(t2, "connectedCallback", void 0, e2);
}, gt = (t2, e2) => {
  mt(t2, "disconnectedCallback", void 0, e2 || t2);
}, St = (t2, n2 = {}) => {
  var o2;
  if (!u.document) return void console.warn("Stencil: No document found. Skipping bootstrapping lazy components.");
  const c2 = [], f2 = n2.exclude || [], h2 = u.customElements, p2 = u.document.head, v2 = p2.querySelector("meta[charset]"), m2 = u.document.createElement("style"), y2 = [];
  let w2, b2 = true;
  Object.assign(a, n2), a.l = new URL(n2.resourcesUrl || "./", u.document.baseURI).href;
  let $2 = false;
  if (t2.map(((t3) => {
    t3[1].map(((n3) => {
      var o3;
      const s2 = { o: n3[0], i: n3[1], W: n3[2], L: n3[3] };
      4 & s2.o && ($2 = true), s2.W = n3[2], s2.L = n3[3], s2.N = [], s2.A = null != (o3 = n3[4]) ? o3 : {};
      const u2 = s2.i, p3 = class extends HTMLElement {
        constructor(t4) {
          if (super(t4), this.hasRegisteredEventListeners = false, ((t5, e2) => {
            const n4 = { o: 0, $hostElement$: t5, C: e2, U: /* @__PURE__ */ new Map() };
            n4.H = new Promise(((t6) => n4.D = t6)), n4.F = new Promise(((t6) => n4.R = t6)), t5["s-p"] = [], t5["s-rc"] = [];
            const o4 = n4;
            t5.__stencil__getHostRef = () => o4;
          })(t4 = this, s2), 1 & s2.o) if (t4.shadowRoot) {
            if ("open" !== t4.shadowRoot.mode) throw Error(`Unable to re-use existing shadow root for ${s2.i}! Mode is set to ${t4.shadowRoot.mode} but Stencil only supports open shadow roots.`);
          } else P.call(t4, s2);
        }
        connectedCallback() {
          const t4 = e(this);
          t4 && (this.hasRegisteredEventListeners || (this.hasRegisteredEventListeners = true, kt(this, t4, s2.L)), w2 && (clearTimeout(w2), w2 = null), b2 ? y2.push(this) : a.jmp((() => ((t5) => {
            if (!(1 & a.o)) {
              const n4 = e(t5);
              if (!n4) return;
              const o4 = n4.C;
              if (1 & n4.o) kt(t5, n4, o4.L), (null == n4 ? void 0 : n4.t) ? $t(n4.t, t5) : (null == n4 ? void 0 : n4.F) && n4.F.then((() => $t(n4.t, t5)));
              else {
                n4.o |= 1;
                {
                  let e2 = t5;
                  for (; e2 = e2.parentNode || e2.host; ) if (e2["s-p"]) {
                    rt(n4, n4.k = e2);
                    break;
                  }
                }
                o4.W && Object.entries(o4.W).map((([e2, [n5]]) => {
                  if (31 & n5 && t5.hasOwnProperty(e2)) {
                    const n6 = t5[e2];
                    delete t5[e2], t5[e2] = n6;
                  }
                })), (async (t6, e2, n5) => {
                  let o5;
                  if (!(32 & e2.o)) {
                    if (e2.o |= 32, n5.T) {
                      const r2 = ((t7, e3) => {
                        const n6 = t7.i.replace(/-/g, "_"), o6 = t7.T;
                        if (!o6) return;
                        const r3 = i.get(o6);
                        return r3 ? r3[n6] : __variableDynamicImportRuntimeHelper(/* @__PURE__ */ Object.assign({ "./p-0df37de3.entry.js": () => import("./p-0df37de3.entry-hSOvjrd5.js"), "./p-182c6c19.entry.js": () => import("./p-182c6c19.entry-CKrAnArC.js"), "./p-28dd0bff.entry.js": () => import("./p-28dd0bff.entry-BTYSJaWu.js"), "./p-36aa4a7f.entry.js": () => import("./p-36aa4a7f.entry-DsCcbEOE.js"), "./p-55c6a817.entry.js": () => import("./p-55c6a817.entry-Dof5rrDQ.js"), "./p-5d51f267.entry.js": () => import("./p-5d51f267.entry-DrC2LHm0.js"), "./p-62695161.entry.js": () => import("./p-62695161.entry-Ci6-Pxdw.js"), "./p-924ca284.entry.js": () => import("./p-924ca284.entry-mcKT-Yt0.js"), "./p-9738317a.entry.js": () => import("./p-9738317a.entry-Biwx3Vy6.js"), "./p-988ad9c7.entry.js": () => import("./p-988ad9c7.entry-BpooDYG2.js"), "./p-a6642965.entry.js": () => import("./p-a6642965.entry-SJUITRTL.js"), "./p-b1bf3d70.entry.js": () => import("./p-b1bf3d70.entry-CF8WvqYu.js"), "./p-e2900881.entry.js": () => import("./p-e2900881.entry-Da7qgTMA.js"), "./p-e4e76694.entry.js": () => import("./p-e4e76694.entry-CnZ5q5gF.js"), "./p-e6148250.entry.js": () => import("./p-e6148250.entry-Cxh6qDpa.js"), "./p-f19de954.entry.js": () => import("./p-f19de954.entry-CqkVoxEo.js") }), `./${o6}.entry.js`, 2).then(((t8) => (i.set(o6, t8), t8[n6])), ((t8) => {
                          l(t8, e3.$hostElement$);
                        }));
                        /*!__STENCIL_STATIC_IMPORT_SWITCH__*/
                      })(n5, e2);
                      if (r2 && "then" in r2) {
                        o5 = await r2;
                      } else o5 = r2;
                      if (!o5) throw Error(`Constructor for "${n5.i}#${e2.q}" was not found`);
                      o5.isProxied || (n5.A = o5.watchers, bt(o5, n5, 2), o5.isProxied = true);
                      e2.o |= 8;
                      try {
                        new o5(e2);
                      } catch (e3) {
                        l(e3, t6);
                      }
                      e2.o &= -9, e2.o |= 128, $t(e2.t, t6);
                    } else o5 = t6.constructor, customElements.whenDefined(t6.localName).then((() => e2.o |= 128));
                    if (o5 && o5.style) {
                      let t7;
                      "string" == typeof o5.style && (t7 = o5.style);
                      const e3 = R(n5);
                      if (!r.has(e3)) {
                        ((t8, e4, n6) => {
                          let o6 = r.get(t8);
                          d && n6 ? (o6 = o6 || new CSSStyleSheet(), "string" == typeof o6 ? o6 = e4 : o6.replaceSync(e4)) : o6 = e4, r.set(t8, o6);
                        })(e3, t7, !!(1 & n5.o));
                      }
                    }
                  }
                  const s3 = e2.k, c3 = () => st(e2, true);
                  s3 && s3["s-rc"] ? s3["s-rc"].push(c3) : c3();
                })(t5, n4, o4);
              }
            }
          })(this))));
        }
        disconnectedCallback() {
          a.jmp((() => (async (t4) => {
            if (!(1 & a.o)) {
              const n4 = e(t4);
              (null == n4 ? void 0 : n4.V) && (n4.V.map(((t5) => t5())), n4.V = void 0), (null == n4 ? void 0 : n4.t) ? gt(n4.t, t4) : (null == n4 ? void 0 : n4.F) && n4.F.then((() => gt(n4.t, t4)));
            }
            N.has(t4) && N.delete(t4), t4.shadowRoot && N.has(t4.shadowRoot) && N.delete(t4.shadowRoot);
          })(this))), a.raf((() => {
            var t4;
            const n4 = e(this);
            if (!n4) return;
            const o4 = y2.findIndex(((t5) => t5 === this));
            o4 > -1 && y2.splice(o4, 1), (null == (t4 = null == n4 ? void 0 : n4.P) ? void 0 : t4.$) instanceof Node && !n4.P.$.isConnected && delete n4.P.$;
          }));
        }
        componentOnReady() {
          var t4;
          return null == (t4 = e(this)) ? void 0 : t4.F;
        }
      };
      s2.T = t3[0], f2.includes(u2) || h2.get(u2) || (c2.push(u2), h2.define(u2, bt(p3, s2, 1)));
    }));
  })), c2.length > 0 && ($2 && (m2.textContent += s), m2.textContent += c2.sort() + "{visibility:hidden}[lf-hydrated]{visibility:inherit}", m2.innerHTML.length)) {
    m2.setAttribute("data-styles", "");
    const t3 = null != (o2 = a.M) ? o2 : j(u.document);
    null != t3 && m2.setAttribute("nonce", t3), p2.insertBefore(m2, v2 ? v2.nextSibling : p2.firstChild);
  }
  b2 = false, y2.length ? y2.map(((t3) => t3.connectedCallback())) : a.jmp((() => w2 = setTimeout(vt, 30)));
}, jt = (t2, e2) => e2, kt = (t2, e2, n2) => {
  n2 && u.document && n2.map((([n3, o2, l2]) => {
    const i2 = t2, r2 = Ot(e2, l2), s2 = Et(n3);
    a.ael(i2, o2, r2, s2), (e2.V = e2.V || []).push((() => a.rel(i2, o2, r2, s2)));
  }));
}, Ot = (t2, e2) => (n2) => {
  var o2;
  try {
    256 & t2.o ? null == (o2 = t2.t) || o2[e2](n2) : (t2.O = t2.O || []).push([e2, n2]);
  } catch (e3) {
    l(e3, t2.$hostElement$);
  }
}, Et = (t2) => ({ passive: !!(1 & t2), capture: !!(2 & t2) });
const o = () => {
};
(() => {
  const l2 = import.meta.url, f$1 = {};
  return "" !== l2 && (f$1.resourcesUrl = new URL(".", l2).href), f(f$1);
})().then((async (e2) => (await o(), St(JSON.parse('[["p-988ad9c7",[[257,"lf-imageviewer",{"lfDataset":[1040,"lf-dataset"],"lfLoadCallback":[1040,"lf-load-callback"],"lfNavigation":[1040,"lf-navigation"],"lfStyle":[1025,"lf-style"],"lfValue":[1040,"lf-value"],"debugInfo":[32],"currentShape":[32],"history":[32],"historyIndex":[32],"isNavigationTreeOpen":[32],"isSpinnerActive":[32],"addSnapshot":[64],"clearHistory":[64],"clearSelection":[64],"getComponents":[64],"getCurrentSnapshot":[64],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"reset":[64],"setSpinnerStatus":[64],"unmount":[64]}]]],["p-182c6c19",[[257,"lf-compare",{"lfDataset":[1040,"lf-dataset"],"lfShape":[1025,"lf-shape"],"lfStyle":[1025,"lf-style"],"lfView":[1025,"lf-view"],"debugInfo":[32],"isLeftPanelOpened":[32],"isRightPanelOpened":[32],"leftShape":[32],"rightShape":[32],"shapes":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfDataset":["updateShapes"],"lfShape":["updateShapes"]}]]],["p-e4e76694",[[257,"lf-accordion",{"lfDataset":[1040,"lf-dataset"],"lfRipple":[1028,"lf-ripple"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfStyle":[1025,"lf-style"],"debugInfo":[32],"expandedNodes":[32],"selectedNodes":[32],"getDebugInfo":[64],"getProps":[64],"getSelectedNodes":[64],"refresh":[64],"toggleNode":[64],"unmount":[64]}]]],["p-62695161",[[257,"lf-article",{"lfDataset":[1040,"lf-dataset"],"lfEmpty":[1025,"lf-empty"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-5d51f267",[[257,"lf-carousel",{"lfDataset":[1040,"lf-dataset"],"lfAutoPlay":[4,"lf-auto-play"],"lfInterval":[2,"lf-interval"],"lfLightbox":[1540,"lf-lightbox"],"lfNavigation":[1028,"lf-navigation"],"lfShape":[1537,"lf-shape"],"lfStyle":[1025,"lf-style"],"debugInfo":[32],"currentIndex":[32],"shapes":[32],"getDebugInfo":[64],"getProps":[64],"goToSlide":[64],"nextSlide":[64],"prevSlide":[64],"refresh":[64],"unmount":[64]},null,{"lfDataset":["updateShapes"],"lfShape":["updateShapes"]}]]],["p-28dd0bff",[[257,"lf-messenger",{"lfAutosave":[1028,"lf-autosave"],"lfDataset":[1040,"lf-dataset"],"lfStyle":[1025,"lf-style"],"lfValue":[16,"lf-value"],"debugInfo":[32],"chat":[32],"connectionStatus":[32],"covers":[32],"currentCharacter":[32],"formStatusMap":[32],"history":[32],"hoveredCustomizationOption":[32],"saveInProgress":[32],"ui":[32],"deleteOption":[64],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"reset":[64],"save":[64],"unmount":[64]}]]],["p-f19de954",[[257,"lf-drawer",{"lfDisplay":[1537,"lf-display"],"lfPosition":[1537,"lf-position"],"lfResponsive":[1026,"lf-responsive"],"lfStyle":[1025,"lf-style"],"lfValue":[1540,"lf-value"],"debugInfo":[32],"close":[64],"getDebugInfo":[64],"getProps":[64],"isOpened":[64],"open":[64],"refresh":[64],"toggle":[64],"unmount":[64]},[[0,"keydown","listenKeydown"]],{"lfDisplay":["onLfDisplayChange"],"lfResponsive":["onLfResponsiveChange"]}]]],["p-a6642965",[[257,"lf-header",{"lfStyle":[1025,"lf-style"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-e6148250",[[257,"lf-placeholder",{"lfIcon":[1,"lf-icon"],"lfProps":[16,"lf-props"],"lfStyle":[1025,"lf-style"],"lfThreshold":[2,"lf-threshold"],"lfTrigger":[1,"lf-trigger"],"lfValue":[1,"lf-value"],"debugInfo":[32],"isInViewport":[32],"getComponent":[64],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-36aa4a7f",[[257,"lf-slider",{"lfLabel":[1025,"lf-label"],"lfLeadingLabel":[1028,"lf-leading-label"],"lfMax":[2,"lf-max"],"lfMin":[2,"lf-min"],"lfStep":[2,"lf-step"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1026,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setValue":[64],"unmount":[64]}]]],["p-0df37de3",[[257,"lf-splash",{"lfLabel":[1025,"lf-label"],"lfStyle":[1025,"lf-style"],"debugInfo":[32],"state":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-924ca284",[[257,"lf-toast",{"lfCloseIcon":[1025,"lf-close-icon"],"lfCloseCallback":[16,"lf-close-callback"],"lfIcon":[1025,"lf-icon"],"lfTimer":[2,"lf-timer"],"lfMessage":[1025,"lf-message"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-9738317a",[[257,"lf-card",{"lfDataset":[1040,"lf-dataset"],"lfLayout":[1025,"lf-layout"],"lfSizeX":[1025,"lf-size-x"],"lfSizeY":[1025,"lf-size-y"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"debugInfo":[32],"shapes":[32],"getDebugInfo":[64],"getProps":[64],"getShapes":[64],"refresh":[64],"unmount":[64]},null,{"lfDataset":["updateShapes"]}],[257,"lf-badge",{"lfImageProps":[1040,"lf-image-props"],"lfLabel":[1025,"lf-label"],"lfPosition":[1537,"lf-position"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}],[257,"lf-canvas",{"lfBrush":[1025,"lf-brush"],"lfColor":[1025,"lf-color"],"lfCursor":[1025,"lf-cursor"],"lfImageProps":[1040,"lf-image-props"],"lfOpacity":[1026,"lf-opacity"],"lfPreview":[1028,"lf-preview"],"lfStrokeTolerance":[1026,"lf-stroke-tolerance"],"lfSize":[1026,"lf-size"],"lfStyle":[1025,"lf-style"],"boxing":[32],"debugInfo":[32],"isPainting":[32],"orientation":[32],"points":[32],"clearCanvas":[64],"getCanvas":[64],"getDebugInfo":[64],"getImage":[64],"getProps":[64],"refresh":[64],"resizeCanvas":[64],"setCanvasHeight":[64],"setCanvasWidth":[64],"unmount":[64]}],[257,"lf-photoframe",{"lfOverlay":[1040,"lf-overlay"],"lfPlaceholder":[16,"lf-placeholder"],"lfStyle":[1025,"lf-style"],"lfThreshold":[2,"lf-threshold"],"lfValue":[16,"lf-value"],"debugInfo":[32],"imageOrientation":[32],"isInViewport":[32],"isReady":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}],[257,"lf-chart",{"lfAxis":[1025,"lf-axis"],"lfColors":[1040,"lf-colors"],"lfDataset":[1040,"lf-dataset"],"lfLegend":[1025,"lf-legend"],"lfSeries":[1040,"lf-series"],"lfSizeX":[1025,"lf-size-x"],"lfSizeY":[1025,"lf-size-y"],"lfStyle":[1025,"lf-style"],"lfTypes":[1040,"lf-types"],"lfXAxis":[1040,"lf-x-axis"],"lfYAxis":[1040,"lf-y-axis"],"debugInfo":[32],"themeValues":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"resize":[64],"unmount":[64]}],[257,"lf-toggle",{"lfAriaLabel":[1025,"lf-aria-label"],"lfLabel":[1025,"lf-label"],"lfLeadingLabel":[1028,"lf-leading-label"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[4,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setValue":[64],"unmount":[64]}],[257,"lf-upload",{"lfLabel":[1025,"lf-label"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfValue":[16,"lf-value"],"debugInfo":[32],"selectedFiles":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"unmount":[64]}],[257,"lf-chat",{"lfContextWindow":[1026,"lf-context-window"],"lfEmpty":[1025,"lf-empty"],"lfEndpointUrl":[1025,"lf-endpoint-url"],"lfLayout":[1025,"lf-layout"],"lfMaxTokens":[1026,"lf-max-tokens"],"lfPollingInterval":[1026,"lf-polling-interval"],"lfSeed":[1026,"lf-seed"],"lfStyle":[1025,"lf-style"],"lfSystem":[1025,"lf-system"],"lfTemperature":[1026,"lf-temperature"],"lfTypewriterProps":[1028,"lf-typewriter-props"],"lfUiSize":[1537,"lf-ui-size"],"lfValue":[1040,"lf-value"],"currentAbortStreaming":[32],"currentPrompt":[32],"currentTokens":[32],"debugInfo":[32],"history":[32],"status":[32],"view":[32],"abortStreaming":[64],"getDebugInfo":[64],"getHistory":[64],"getLastMessage":[64],"getProps":[64],"refresh":[64],"scrollToBottom":[64],"setHistory":[64],"unmount":[64]},[[0,"keydown","listenKeydown"]],{"lfPollingInterval":["updatePollingInterval"],"lfSystem":["updateTokensCount"]}],[257,"lf-chip",{"lfAriaLabel":[1025,"lf-aria-label"],"lfDataset":[1040,"lf-dataset"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfStyling":[1025,"lf-styling"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[16,"lf-value"],"debugInfo":[32],"expandedNodes":[32],"hiddenNodes":[32],"selectedNodes":[32],"getDebugInfo":[64],"getProps":[64],"getSelectedNodes":[64],"refresh":[64],"setSelectedNodes":[64],"unmount":[64]}],[257,"lf-code",{"lfFadeIn":[1028,"lf-fade-in"],"lfFormat":[1028,"lf-format"],"lfLanguage":[1025,"lf-language"],"lfPreserveSpaces":[1028,"lf-preserve-spaces"],"lfShowCopy":[1028,"lf-show-copy"],"lfShowHeader":[1028,"lf-show-header"],"lfStickyHeader":[1028,"lf-sticky-header"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1025,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfLanguage":["loadLanguage"]}],[257,"lf-progressbar",{"lfAnimated":[1540,"lf-animated"],"lfCenteredLabel":[1540,"lf-centered-label"],"lfIcon":[1537,"lf-icon"],"lfIsRadial":[1540,"lf-is-radial"],"lfLabel":[1025,"lf-label"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1026,"lf-value"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}],[257,"lf-textfield",{"lfHelper":[1040,"lf-helper"],"lfHtmlAttributes":[1040,"lf-html-attributes"],"lfIcon":[1025,"lf-icon"],"lfLabel":[1025,"lf-label"],"lfStretchX":[1540,"lf-stretch-x"],"lfStretchY":[1540,"lf-stretch-y"],"lfStyle":[1025,"lf-style"],"lfStyling":[1025,"lf-styling"],"lfTrailingIcon":[1540,"lf-trailing-icon"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1,"lf-value"],"debugInfo":[32],"status":[32],"value":[32],"getDebugInfo":[64],"getElement":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setBlur":[64],"setFocus":[64],"setValue":[64],"unmount":[64]}],[257,"lf-typewriter",{"lfCursor":[1025,"lf-cursor"],"lfDeleteSpeed":[1026,"lf-delete-speed"],"lfLoop":[1028,"lf-loop"],"lfPause":[1026,"lf-pause"],"lfSpeed":[1026,"lf-speed"],"lfStyle":[1025,"lf-style"],"lfTag":[1025,"lf-tag"],"lfUiSize":[1537,"lf-ui-size"],"lfUpdatable":[1028,"lf-updatable"],"lfValue":[1025,"lf-value"],"debugInfo":[32],"displayedText":[32],"isDeleting":[32],"currentTextIndex":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfValue":["handleLfValueChange"]}],[257,"lf-image",{"lfHtmlAttributes":[1040,"lf-html-attributes"],"lfMode":[1537,"lf-mode"],"lfShowSpinner":[1028,"lf-show-spinner"],"lfSizeX":[1025,"lf-size-x"],"lfSizeY":[1025,"lf-size-y"],"lfStyle":[1025,"lf-style"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1025,"lf-value"],"debugInfo":[32],"error":[32],"isLoaded":[32],"resolvedSpriteName":[32],"getDebugInfo":[64],"getImage":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfValue":["resetState"]}],[257,"lf-button",{"lfAriaLabel":[1025,"lf-aria-label"],"lfDataset":[1040,"lf-dataset"],"lfIcon":[1025,"lf-icon"],"lfIconOff":[1025,"lf-icon-off"],"lfLabel":[1025,"lf-label"],"lfRipple":[1028,"lf-ripple"],"lfShowSpinner":[1540,"lf-show-spinner"],"lfStretchX":[1540,"lf-stretch-x"],"lfStretchY":[1540,"lf-stretch-y"],"lfStyle":[1025,"lf-style"],"lfStyling":[1025,"lf-styling"],"lfToggable":[1028,"lf-toggable"],"lfTrailingIcon":[1028,"lf-trailing-icon"],"lfType":[1025,"lf-type"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[4,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setMessage":[64],"setValue":[64],"unmount":[64]}],[257,"lf-list",{"lfDataset":[1040,"lf-dataset"],"lfEmpty":[1025,"lf-empty"],"lfEnableDeletions":[1028,"lf-enable-deletions"],"lfNavigation":[1028,"lf-navigation"],"lfRipple":[1028,"lf-ripple"],"lfSelectable":[1028,"lf-selectable"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[2,"lf-value"],"debugInfo":[32],"focused":[32],"selected":[32],"focusNext":[64],"focusPrevious":[64],"getDebugInfo":[64],"getProps":[64],"getSelected":[64],"refresh":[64],"selectNode":[64],"unmount":[64]},[[0,"keydown","listenKeydown"]]],[257,"lf-spinner",{"lfActive":[1540,"lf-active"],"lfBarVariant":[1540,"lf-bar-variant"],"lfDimensions":[1025,"lf-dimensions"],"lfFader":[1540,"lf-fader"],"lfFaderTimeout":[1026,"lf-fader-timeout"],"lfFullScreen":[1540,"lf-full-screen"],"lfLayout":[1026,"lf-layout"],"lfStyle":[1025,"lf-style"],"lfTimeout":[1026,"lf-timeout"],"bigWait":[32],"debugInfo":[32],"progress":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfActive":["onFaderChange"],"lfFader":["onFaderChange"],"lfFaderTimeout":["onFaderChange"],"lfBarVariant":["lfBarVariantChanged"],"lfTimeout":["lfTimeoutChanged"]}]]],["p-55c6a817",[[257,"lf-masonry",{"lfActions":[1028,"lf-actions"],"lfColumns":[1026,"lf-columns"],"lfDataset":[1040,"lf-dataset"],"lfSelectable":[1540,"lf-selectable"],"lfShape":[1025,"lf-shape"],"lfStyle":[1025,"lf-style"],"lfView":[1025,"lf-view"],"debugInfo":[32],"selectedShape":[32],"shapes":[32],"viewportWidth":[32],"getDebugInfo":[64],"getProps":[64],"getSelectedShape":[64],"redecorateShapes":[64],"refresh":[64],"setSelectedShape":[64],"unmount":[64]},null,{"lfColumns":["validateColumns"],"lfDataset":["updateShapes"],"lfShape":["updateShapes"]}]]],["p-e2900881",[[257,"lf-tabbar",{"lfAriaLabel":[1025,"lf-aria-label"],"lfDataset":[16,"lf-dataset"],"lfNavigation":[4,"lf-navigation"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[8,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setValue":[64],"unmount":[64]}]]],["p-b1bf3d70",[[257,"lf-tree",{"lfAccordionLayout":[1540,"lf-accordion-layout"],"lfDataset":[1040,"lf-dataset"],"lfEmpty":[1025,"lf-empty"],"lfExpandedNodeIds":[1040,"lf-expanded-node-ids"],"lfFilter":[1028,"lf-filter"],"lfGrid":[1540,"lf-grid"],"lfInitialExpansionDepth":[1026,"lf-initial-expansion-depth"],"lfSelectedNodeIds":[1040,"lf-selected-node-ids"],"lfRipple":[1028,"lf-ripple"],"lfSelectable":[1540,"lf-selectable"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"debugInfo":[32],"expandedNodes":[32],"hiddenNodes":[32],"selectedNode":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"getExpandedNodeIds":[64],"getSelectedNodeIds":[64],"setExpandedNodes":[64],"setSelectedNodes":[64],"selectByPredicate":[64],"unmount":[64]},null,{"lfDataset":["handleDatasetChange"],"lfExpandedNodeIds":["handleExpandedPropChange"],"lfSelectedNodeIds":["handleSelectedPropChange"],"lfInitialExpansionDepth":["handleInitialDepthChange"],"lfSelectable":["handleSelectableChange"],"lfFilter":["handleFilterToggle"]}]]]]'), e2))));
var APIEndpoints;
(function(APIEndpoints2) {
  APIEndpoints2["ClearAnalytics"] = "/lf-nodes/clear-analytics";
  APIEndpoints2["ClearMetadata"] = "/lf-nodes/clear-metadata";
  APIEndpoints2["ClearPreviewCache"] = "/lf-nodes/clear-preview-cache";
  APIEndpoints2["LFFree"] = "/lf-nodes/free";
  APIEndpoints2["LFRefreshNodeDefs"] = "/lf-nodes/refresh-node-defs";
  APIEndpoints2["GetAnalytics"] = "/lf-nodes/get-analytics";
  APIEndpoints2["GetImage"] = "/lf-nodes/get-image";
  APIEndpoints2["ExploreFilesystem"] = "/lf-nodes/explore-filesystem";
  APIEndpoints2["GetJson"] = "/lf-nodes/get-json";
  APIEndpoints2["GetMetadata"] = "/lf-nodes/get-metadata";
  APIEndpoints2["GetPreviewStats"] = "/lf-nodes/get-preview-stats";
  APIEndpoints2["GetBackupStats"] = "/lf-nodes/get-backup-stats";
  APIEndpoints2["NewBackup"] = "/lf-nodes/new-backup";
  APIEndpoints2["CleanOldBackups"] = "/lf-nodes/clean-old-backups";
  APIEndpoints2["ProcessImage"] = "/lf-nodes/process-image";
  APIEndpoints2["SaveMetadata"] = "/lf-nodes/save-metadata";
  APIEndpoints2["UpdateJson"] = "/lf-nodes/update-json";
  APIEndpoints2["UpdateMetadataCover"] = "/lf-nodes/update-metadata-cover";
  APIEndpoints2["GetGpuStats"] = "/lf-nodes/get-gpu-stats";
  APIEndpoints2["GetDiskStats"] = "/lf-nodes/get-disk-stats";
  APIEndpoints2["GetCpuStats"] = "/lf-nodes/get-cpu-stats";
  APIEndpoints2["GetRamStats"] = "/lf-nodes/get-ram-stats";
})(APIEndpoints || (APIEndpoints = {}));
var LogSeverity;
(function(LogSeverity2) {
  LogSeverity2["Info"] = "info";
  LogSeverity2["Success"] = "success";
  LogSeverity2["Warning"] = "warning";
  LogSeverity2["Error"] = "error";
})(LogSeverity || (LogSeverity = {}));
const ANALYTICS_API = {
  //#region clear
  clear: async (type) => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("type", type);
      const response = await api.fetchApi(APIEndpoints.ClearAnalytics, {
        body,
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message;
            payload.status = LogSeverity.Success;
            lfManager.getCachedDatasets().usage = {};
          }
          break;
        case 404:
          payload.message = `Analytics not found: ${type}. Skipping deletion.`;
          payload.status = LogSeverity.Info;
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the clear-analytics ${type} API (${code2}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region get
  get: async (directory, type) => {
    const lfManager = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    if (!directory || !type) {
      payload.message = `Missing directory (received ${directory}) or  (received ${type}).`;
      payload.status = LogSeverity.Error;
      lfManager.log(payload.message, { payload }, LogSeverity.Error);
      return payload;
    }
    try {
      const body = new FormData();
      body.append("directory", directory);
      body.append("type", type);
      const response = await api.fetchApi(APIEndpoints.GetAnalytics, {
        body,
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.message = "Analytics data fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
            lfManager.getCachedDatasets().usage = payload.data;
          }
          break;
        case 404:
          payload.status = LogSeverity.Info;
          lfManager.log(`${type} analytics file not found.`, { payload }, payload.status);
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the get-analytics ${type} API (${code2}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const BACKUP_API = {
  //#region new
  new: async (backupType = "automatic") => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("backup_type", backupType);
      const response = await api.fetchApi(APIEndpoints.NewBackup, { body, method: "POST" });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getStats
  getStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: {
        total_size_bytes: 0,
        file_count: 0,
        backups: []
      },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.GetBackupStats, { method: "GET" });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.message = "Backup statistics retrieved successfully.";
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region cleanOld
  cleanOld: async (maxBackups) => {
    const lfManager = getLfManager();
    const _maxBackups = maxBackups || lfManager.getBackupRetention();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    if (_maxBackups <= 0) {
      const message = "Backup retention is set to 0, skipping cleanup.";
      lfManager.log(payload.message, { payload }, payload.status);
      payload.message = message;
      payload.status = LogSeverity.Info;
      return payload;
    }
    try {
      const body = new FormData();
      body.append("max_backups", String(_maxBackups));
      const response = await api.fetchApi(APIEndpoints.CleanOldBackups, { body, method: "POST" });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const COMFY_API = {
  comfyUi: () => window.comfyAPI,
  event: (name, callback) => {
    api.addEventListener(name, callback);
  },
  executeCommand: (name) => {
    try {
      app.extensionManager.command.execute(name);
    } catch (error2) {
      getLfManager().log(`Command ${name} not executed!`, { error: error2 }, LogSeverity.Warning);
    }
  },
  getDragAndScale: () => {
    return app.canvas.ds;
  },
  getLinkById: (id) => {
    return app.graph.links[String(id).valueOf()];
  },
  getNodeById: (id) => {
    return app.graph.getNodeById(+(id || app.runningNodeId));
  },
  getResourceUrl: (subfolder, filename, type = "output") => {
    const params = [
      "filename=" + encodeURIComponent(filename),
      "type=" + type,
      "subfolder=" + subfolder,
      app.getRandParam().substring(1)
    ].join("&");
    return `/view?${params}`;
  },
  interrupt: () => {
    return api.interrupt();
  },
  queuePrompt: async () => {
    app.queuePrompt(0);
  },
  redraw: () => {
    app.graph.setDirtyCanvas(true, false);
  },
  redrawFull: () => {
    app.graph.setDirtyCanvas(true, true);
  },
  scheduleRedraw: /* @__PURE__ */ (() => {
    let scheduled = false;
    return (immediate = false) => {
      if (immediate) {
        scheduled = false;
        try {
          app.graph.setDirtyCanvas(true, true);
        } catch {
        }
        return;
      }
      if (scheduled) {
        return;
      }
      scheduled = true;
      requestAnimationFrame(() => {
        scheduled = false;
        try {
          app.graph.setDirtyCanvas(true, true);
        } catch {
        }
      });
    };
  })(),
  register: (extension) => {
    app.registerExtension(extension);
  },
  upload: async (body) => {
    return await api.fetchApi("/upload/image", {
      method: "POST",
      body
    });
  }
};
const GITHUB_API = {
  //#region getLatestRelease
  getLatestRelease: async () => {
    const lfManager = getLfManager();
    const REPO = "lf-nodes";
    const USER = "lucafoscili";
    const payload = {
      data: null,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await fetch(`https://api.github.com/repos/${USER}/${REPO}/releases/latest`);
      const code2 = response.status;
      switch (code2) {
        case 200:
          const releaseData = await response.json();
          payload.data = releaseData;
          payload.message = "Latest release successfully fetched from GitHub.";
          payload.status = LogSeverity.Success;
          break;
        case 404:
          payload.message = "No releases found for the repository!";
          payload.status = LogSeverity.Info;
          break;
        default:
          payload.message = "Unexpected response from the GitHub API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = `Error fetching release info: ${error2}`;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const IMAGE_API = {
  //#region get
  get: async (directory) => {
    const lfManager = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      if (directory) {
        body.append("directory", directory);
      }
      const response = await api.fetchApi(APIEndpoints.GetImage, {
        body,
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.message = "Images fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the get-image API (${code2}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region process
  process: async (url, type, settings) => {
    const lfManager = getLfManager();
    const payload = {
      data: "",
      mask: void 0,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("url", url);
      body.append("type", type);
      body.append("settings", JSON.stringify(settings));
      const response = await api.fetchApi(APIEndpoints.ProcessImage, {
        body,
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.mask = p2.mask;
            payload.message = "Image processed successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the process-image API (${code2}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region explore
  explore: async (directory, options = {}) => {
    const lfManager = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      if (directory) {
        body.append("directory", directory);
      }
      const { scope, nodePath } = options;
      if (scope) {
        body.append("scope", scope);
      }
      if (nodePath) {
        body.append("node", nodePath);
      }
      const response = await api.fetchApi(APIEndpoints.ExploreFilesystem, {
        body,
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data ?? {};
            payload.message = "Filesystem data fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the explore-filesystem API (${code2}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload, options }, payload.status);
    return payload;
  }
  //#endregion
};
const JSON_API = {
  //#region get
  get: async (filePath) => {
    const lfManager = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("file_path", filePath);
      const response = await api.fetchApi(APIEndpoints.GetJson, {
        body,
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.message = "JSON data fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          payload.message = `Unexpected response from the get-json API: ${await response.text()}`;
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2.toString();
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region update
  update: async (filePath, dataset) => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    const body = new FormData();
    body.append("file_path", filePath);
    body.append("dataset", JSON.stringify(dataset));
    try {
      const response = await api.fetchApi(APIEndpoints.UpdateJson, {
        body,
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const METADATA_API = {
  //#region clear
  clear: async () => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.ClearMetadata, {
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region get
  get: async (hash) => {
    const lfManager = getLfManager();
    const payload = {
      data: null,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await fetch(`https://civitai.com/api/v1/model-versions/by-hash/${hash}`);
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          payload.data = p2;
          payload.message = "Metadata succesfully fetched from CivitAI.";
          payload.status = LogSeverity.Success;
          break;
        case 404:
          payload.message = "Model not found on CivitAI!";
          payload.status = LogSeverity.Info;
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region save
  save: async (modelPath, dataset, forcedSave = false) => {
    const lfManager = getLfManager();
    const payload = {
      data: null,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("model_path", modelPath);
      body.append("metadata", JSON.stringify(dataset));
      body.append("forced_save", String(forcedSave).valueOf());
      const response = await api.fetchApi(APIEndpoints.SaveMetadata, {
        method: "POST",
        body
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region updateCover
  updateCover: async (modelPath, b64image) => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("model_path", modelPath);
      body.append("base64_image", b64image);
      const response = await api.fetchApi(APIEndpoints.UpdateMetadataCover, {
        method: "POST",
        body
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message;
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          payload.message = "Unexpected response from the API!";
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = error2;
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const MODELS_API = {
  free: async () => {
    const lfManager = getLfManager();
    try {
      const response = await api.fetchApi(APIEndpoints.LFFree, { method: "POST" });
      if (response.status === 200) {
        return true;
      }
      lfManager.log('"free" endpoint returned non-200', { status: response.status }, LogSeverity.Warning);
      return false;
    } catch (error2) {
      lfManager.log('"free" endpoint failed', { error: error2 }, LogSeverity.Warning);
      return false;
    }
  },
  refresh: async () => {
    const lfManager = getLfManager();
    try {
      const response = await api.fetchApi(APIEndpoints.LFRefreshNodeDefs, { method: "POST" });
      if (response.status === 200) {
        return true;
      }
      lfManager.log('"refresh-node-defs" endpoint returned non-200', { status: response.status }, LogSeverity.Warning);
      return false;
    } catch (error2) {
      lfManager.log('"refresh-node-defs" endpoint failed', { error: error2 }, LogSeverity.Warning);
      return false;
    }
  }
};
const beforeFree = async (options) => {
  const lfManager = getLfManager();
  lfManager.log("Unload triggered — clearing LF caches first…", { options }, LogSeverity.Info);
  try {
    const ok = await MODELS_API.free();
    if (ok) {
      lfManager.log("Caches cleared ✔️", {}, LogSeverity.Success);
    } else {
      lfManager.log("Cache clear call returned non-200", {}, LogSeverity.Warning);
    }
  } catch (error2) {
    lfManager.log("Error while clearing caches", { error: error2 }, LogSeverity.Warning);
  }
};
const beforeRefreshNodeDefs = async (trigger) => {
  const lfManager = getLfManager();
  lfManager.log("Refresh requested — clearing LF caches first…", { trigger }, LogSeverity.Info);
  try {
    const ok = await MODELS_API.refresh();
    if (ok) {
      lfManager.log("Refresh caches cleared ✔️", {}, LogSeverity.Success);
    } else {
      lfManager.log("Refresh cache clear call returned non-200", {}, LogSeverity.Warning);
    }
  } catch (error2) {
    lfManager.log("Error while clearing caches ahead of refresh", { error: error2 }, LogSeverity.Warning);
  }
};
const PREVIEW_API = {
  //#region clearCache
  clearCache: async () => {
    const lfManager = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.ClearPreviewCache, {
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message || "Preview cache cleared successfully.";
            payload.status = LogSeverity.Success;
          }
          break;
        case 403:
          payload.message = "Permission denied: Unable to delete preview cache.";
          payload.status = LogSeverity.Error;
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the clear-preview-cache API (${code2}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = String(error2);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getStats
  getStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: {
        total_size_bytes: 0,
        file_count: 0,
        path: ""
      },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.GetPreviewStats, {
        method: "POST"
      });
      const code2 = response.status;
      switch (code2) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.message = p2.message || "Preview stats retrieved successfully.";
            payload.status = LogSeverity.Success;
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the get-preview-stats API (${code2}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error2) {
      payload.message = String(error2);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const unexpectedMessage = (endpoint, code2, response, text2) => {
  const body = text2 || response.statusText || "No message provided.";
  return `Unexpected response from ${endpoint} (${code2}): ${body}`;
};
const normalizeMessage = (message, fallback = "Statistics retrieved successfully.") => {
  return message && message.trim().length > 0 ? message : fallback;
};
const SYSTEM_API = {
  //#region getGpuStats
  getGpuStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: [],
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.GetGpuStats, { method: "GET" });
      const code2 = response.status;
      switch (code2) {
        case 200: {
          const p2 = await response.json();
          payload.data = p2.data || [];
          payload.message = normalizeMessage(p2.message, "GPU statistics retrieved successfully.");
          payload.status = p2.status === "success" ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text2 = await response.text().catch(() => "");
          payload.message = unexpectedMessage("get-gpu-stats", code2, response, text2);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error2) {
      payload.message = String(error2);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getDiskStats
  getDiskStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: [],
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.GetDiskStats, { method: "GET" });
      const code2 = response.status;
      switch (code2) {
        case 200: {
          const p2 = await response.json();
          payload.data = p2.data || [];
          payload.message = normalizeMessage(p2.message, "Disk statistics retrieved successfully.");
          payload.status = p2.status === "success" ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text2 = await response.text().catch(() => "");
          payload.message = unexpectedMessage("get-disk-stats", code2, response, text2);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error2) {
      payload.message = String(error2);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getCpuStats
  getCpuStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: {
        average: 0,
        cores: [],
        count: 0,
        physical_count: 0
      },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.GetCpuStats, { method: "GET" });
      const code2 = response.status;
      switch (code2) {
        case 200: {
          const p2 = await response.json();
          payload.data = p2.data || payload.data;
          payload.message = normalizeMessage(p2.message, "CPU statistics retrieved successfully.");
          payload.status = p2.status === "success" ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text2 = await response.text().catch(() => "");
          payload.message = unexpectedMessage("get-cpu-stats", code2, response, text2);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error2) {
      payload.message = String(error2);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region getRamStats
  getRamStats: async () => {
    const lfManager = getLfManager();
    const payload = {
      data: {
        available: 0,
        percent: 0,
        swap_total: 0,
        swap_used: 0,
        total: 0,
        used: 0
      },
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.GetRamStats, { method: "GET" });
      const code2 = response.status;
      switch (code2) {
        case 200: {
          const p2 = await response.json();
          payload.data = p2.data || payload.data;
          payload.message = normalizeMessage(p2.message, "RAM statistics retrieved successfully.");
          payload.status = p2.status === "success" ? LogSeverity.Success : LogSeverity.Error;
          break;
        }
        default: {
          const text2 = await response.text().catch(() => "");
          payload.message = unexpectedMessage("get-ram-stats", code2, response, text2);
          payload.status = LogSeverity.Error;
          break;
        }
      }
    } catch (error2) {
      payload.message = String(error2);
      payload.status = LogSeverity.Error;
    }
    lfManager.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
var MessengerCSS;
(function(MessengerCSS2) {
  MessengerCSS2["Content"] = "lf-messenger";
  MessengerCSS2["Widget"] = "lf-messenger__widget";
  MessengerCSS2["Placeholder"] = "lf-messenger__placeholder";
  MessengerCSS2["PlaceholderHidden"] = "lf-messenger__placeholder--hidden";
})(MessengerCSS || (MessengerCSS = {}));
var ComfyWidgetName;
(function(ComfyWidgetName2) {
  ComfyWidgetName2["boolean"] = "BOOLEAN";
  ComfyWidgetName2["combo"] = "COMBO";
  ComfyWidgetName2["customtext"] = "CUSTOMTEXT";
  ComfyWidgetName2["float"] = "FLOAT";
  ComfyWidgetName2["integer"] = "INTEGER";
  ComfyWidgetName2["json"] = "JSON";
  ComfyWidgetName2["number"] = "NUMBER";
  ComfyWidgetName2["seed"] = "SEED";
  ComfyWidgetName2["string"] = "STRING";
  ComfyWidgetName2["text"] = "TEXT";
  ComfyWidgetName2["toggle"] = "TOGGLE";
})(ComfyWidgetName || (ComfyWidgetName = {}));
var CustomWidgetName;
(function(CustomWidgetName2) {
  CustomWidgetName2["card"] = "LF_CARD";
  CustomWidgetName2["cardsWithChip"] = "LF_CARDS_WITH_CHIP";
  CustomWidgetName2["carousel"] = "LF_CAROUSEL";
  CustomWidgetName2["chat"] = "LF_CHAT";
  CustomWidgetName2["chip"] = "LF_CHIP";
  CustomWidgetName2["code"] = "LF_CODE";
  CustomWidgetName2["compare"] = "LF_COMPARE";
  CustomWidgetName2["controlPanel"] = "LF_CONTROL_PANEL";
  CustomWidgetName2["countBarChart"] = "LF_COUNT_BAR_CHART";
  CustomWidgetName2["history"] = "LF_HISTORY";
  CustomWidgetName2["imageEditor"] = "LF_IMAGE_EDITOR";
  CustomWidgetName2["masonry"] = "LF_MASONRY";
  CustomWidgetName2["messenger"] = "LF_MESSENGER";
  CustomWidgetName2["progressbar"] = "LF_PROGRESSBAR";
  CustomWidgetName2["tabBarChart"] = "LF_TAB_BAR_CHART";
  CustomWidgetName2["textarea"] = "LF_TEXTAREA";
  CustomWidgetName2["tree"] = "LF_TREE";
  CustomWidgetName2["upload"] = "LF_UPLOAD";
})(CustomWidgetName || (CustomWidgetName = {}));
var NodeName;
(function(NodeName2) {
  NodeName2["backgroundRemover"] = "LF_BackgroundRemover";
  NodeName2["blend"] = "LF_Blend";
  NodeName2["blobToImage"] = "LF_BlobToImage";
  NodeName2["bloom"] = "LF_Bloom";
  NodeName2["blurImages"] = "LF_BlurImages";
  NodeName2["boolean"] = "LF_Boolean";
  NodeName2["brightness"] = "LF_Brightness";
  NodeName2["brush"] = "LF_Brush";
  NodeName2["captionImageWD14"] = "LF_CaptionImageWD14";
  NodeName2["characterImpersonator"] = "LF_CharacterImpersonator";
  NodeName2["checkpointSelector"] = "LF_CheckpointSelector";
  NodeName2["civitaiMetadataSetup"] = "LF_CivitAIMetadataSetup";
  NodeName2["clarity"] = "LF_Clarity";
  NodeName2["colorAnalysis"] = "LF_ColorAnalysis";
  NodeName2["compareImages"] = "LF_CompareImages";
  NodeName2["contrast"] = "LF_Contrast";
  NodeName2["controlPanel"] = "LF_ControlPanel";
  NodeName2["createMask"] = "LF_CreateMask";
  NodeName2["detectRegions"] = "LF_DetectRegions";
  NodeName2["desaturation"] = "LF_Desaturation";
  NodeName2["diffusionModelSelector"] = "LF_DiffusionModelSelector";
  NodeName2["displayBoolean"] = "LF_DisplayBoolean";
  NodeName2["displayFloat"] = "LF_DisplayFloat";
  NodeName2["displayInteger"] = "LF_DisplayInteger";
  NodeName2["displayJson"] = "LF_DisplayJSON";
  NodeName2["displayPrimitiveAsJson"] = "LF_DisplayPrimitiveAsJSON";
  NodeName2["displayString"] = "LF_DisplayString";
  NodeName2["markdownDocGenerator"] = "LF_MarkdownDocGenerator";
  NodeName2["filmGrain"] = "LF_FilmGrain";
  NodeName2["float"] = "LF_Float";
  NodeName2["embeddingSelector"] = "LF_EmbeddingSelector";
  NodeName2["emptyImage"] = "LF_EmptyImage";
  NodeName2["extractFaceEmbedding"] = "LF_ExtractFaceEmbedding";
  NodeName2["extractPromptFromLoraTag"] = "LF_ExtractPromptFromLoraTag";
  NodeName2["extractString"] = "LF_ExtractString";
  NodeName2["gaussianBlur"] = "LF_GaussianBlur";
  NodeName2["getValueFromJson"] = "LF_GetValueFromJSON";
  NodeName2["getRandomKeyFromJson"] = "LF_GetRandomKeyFromJSON";
  NodeName2["imageClassifier"] = "LF_ImageClassifier";
  NodeName2["imageListFromJSON"] = "LF_ImageListFromJSON";
  NodeName2["imageHistogram"] = "LF_ImageHistogram";
  NodeName2["imagesEditingBreakpoint"] = "LF_ImagesEditingBreakpoint";
  NodeName2["imagesSlideshow"] = "LF_ImagesSlideshow";
  NodeName2["imageToSvg"] = "LF_ImageToSVG";
  NodeName2["inpaint"] = "LF_Inpaint";
  NodeName2["inpaintAdvanced"] = "LF_InpaintAdvanced";
  NodeName2["integer"] = "LF_Integer";
  NodeName2["isLandscape"] = "LF_IsLandscape";
  NodeName2["jsonPromptCombinator"] = "LF_JSONPromptCombinator";
  NodeName2["keywordCounter"] = "LF_KeywordCounter";
  NodeName2["keywordToggleFromJson"] = "LF_KeywordToggleFromJSON";
  NodeName2["line"] = "LF_Line";
  NodeName2["llmChat"] = "LF_LLMChat";
  NodeName2["llmMessenger"] = "LF_LLMMessenger";
  NodeName2["loadAndEditImages"] = "LF_LoadAndEditImages";
  NodeName2["loadClipSegModel"] = "LF_LoadCLIPSegModel";
  NodeName2["loadWd14Model"] = "LF_LoadWD14Model";
  NodeName2["loadFileOnce"] = "LF_LoadFileOnce";
  NodeName2["loadImages"] = "LF_LoadImages";
  NodeName2["loadLoraTags"] = "LF_LoadLoraTags";
  NodeName2["loadMetadata"] = "LF_LoadMetadata";
  NodeName2["loraAndEmbeddingSelector"] = "LF_LoraAndEmbeddingSelector";
  NodeName2["loraSelector"] = "LF_LoraSelector";
  NodeName2["lutApplication"] = "LF_LUTApplication";
  NodeName2["lutGeneration"] = "LF_LUTGeneration";
  NodeName2["mathOperation"] = "LF_MathOperation";
  NodeName2["multipleImageResizeForWeb"] = "LF_MultipleImageResizeForWeb";
  NodeName2["notify"] = "LF_Notify";
  NodeName2["parsePromptWithLoraTags"] = "LF_ParsePromptWithLoraTags";
  NodeName2["randomBoolean"] = "LF_RandomBoolean";
  NodeName2["regexReplace"] = "LF_RegexReplace";
  NodeName2["regionExtractor"] = "LF_RegionExtractor";
  NodeName2["regionMask"] = "LF_RegionMask";
  NodeName2["resizeImageByEdge"] = "LF_ResizeImageByEdge";
  NodeName2["resizeImageToDimension"] = "LF_ResizeImageToDimension";
  NodeName2["resizeImageToSquare"] = "LF_ResizeImageToSquare";
  NodeName2["resolutionSwitcher"] = "LF_ResolutionSwitcher";
  NodeName2["samplerSelector"] = "LF_SamplerSelector";
  NodeName2["saturation"] = "LF_Saturation";
  NodeName2["saveImageForCivitai"] = "LF_SaveImageForCivitAI";
  NodeName2["saveJson"] = "LF_SaveJSON";
  NodeName2["saveMarkdown"] = "LF_SaveMarkdown";
  NodeName2["saveText"] = "LF_SaveText";
  NodeName2["schedulerSelector"] = "LF_SchedulerSelector";
  NodeName2["sepia"] = "LF_Sepia";
  NodeName2["sequentialSeedsGenerator"] = "LF_SequentialSeedsGenerator";
  NodeName2["setValueInJson"] = "LF_SetValueInJSON";
  NodeName2["shuffleJsonKeys"] = "LF_ShuffleJSONKeys";
  NodeName2["something2Number"] = "LF_Something2Number";
  NodeName2["something2String"] = "LF_Something2String";
  NodeName2["sortJsonKeys"] = "LF_SortJSONKeys";
  NodeName2["sortTags"] = "LF_SortTags";
  NodeName2["splitTone"] = "LF_SplitTone";
  NodeName2["string"] = "LF_String";
  NodeName2["stringReplace"] = "LF_StringReplace";
  NodeName2["stringTemplate"] = "LF_StringTemplate";
  NodeName2["stringToJson"] = "LF_StringToJSON";
  NodeName2["switchFloat"] = "LF_SwitchFloat";
  NodeName2["switchImage"] = "LF_SwitchImage";
  NodeName2["switchInteger"] = "LF_SwitchInteger";
  NodeName2["switchJson"] = "LF_SwitchJSON";
  NodeName2["switchString"] = "LF_SwitchString";
  NodeName2["tiledSuperRes"] = "LF_TiledSuperRes";
  NodeName2["tiltShift"] = "LF_TiltShift";
  NodeName2["updateUsageStatistics"] = "LF_UpdateUsageStatistics";
  NodeName2["upscaleModelSelector"] = "LF_UpscaleModelSelector";
  NodeName2["urandomSeedGenerator"] = "LF_UrandomSeedGenerator";
  NodeName2["usageStatistics"] = "LF_UsageStatistics";
  NodeName2["vaeDecode"] = "LF_VAEDecode";
  NodeName2["vaeSelector"] = "LF_VAESelector";
  NodeName2["onnxSelector"] = "LF_ONNXSelector";
  NodeName2["viewImages"] = "LF_ViewImages";
  NodeName2["viewSVGs"] = "LF_ViewSVGs";
  NodeName2["vibrance"] = "LF_Vibrance";
  NodeName2["vignette"] = "LF_Vignette";
  NodeName2["wallOfText"] = "LF_WallOfText";
  NodeName2["writeJson"] = "LF_WriteJSON";
})(NodeName || (NodeName = {}));
var TagName;
(function(TagName2) {
  TagName2["Div"] = "div";
  TagName2["LfAccordion"] = "lf-accordion";
  TagName2["LfArticle"] = "lf-article";
  TagName2["LfButton"] = "lf-button";
  TagName2["LfCard"] = "lf-card";
  TagName2["LfCarousel"] = "lf-carousel";
  TagName2["LfChat"] = "lf-chat";
  TagName2["LfChart"] = "lf-chart";
  TagName2["LfChip"] = "lf-chip";
  TagName2["LfCode"] = "lf-code";
  TagName2["LfCompare"] = "lf-compare";
  TagName2["LfImageviewer"] = "lf-imageviewer";
  TagName2["LfList"] = "lf-list";
  TagName2["LfMasonry"] = "lf-masonry";
  TagName2["LfMessenger"] = "lf-messenger";
  TagName2["LfProgressbar"] = "lf-progressbar";
  TagName2["LfSlider"] = "lf-slider";
  TagName2["LfSpinner"] = "lf-spinner";
  TagName2["LfTabbar"] = "lf-tabbar";
  TagName2["LfTextfield"] = "lf-textfield";
  TagName2["LfToggle"] = "lf-toggle";
  TagName2["LfTree"] = "lf-tree";
  TagName2["LfUpload"] = "lf-upload";
  TagName2["Textarea"] = "textarea";
})(TagName || (TagName = {}));
const NODE_WIDGET_MAP = {
  LF_BackgroundRemover: [CustomWidgetName.compare],
  LF_Blend: [CustomWidgetName.compare],
  LF_BlobToImage: [CustomWidgetName.code],
  LF_Bloom: [CustomWidgetName.compare],
  LF_BlurImages: [CustomWidgetName.masonry],
  LF_Boolean: [CustomWidgetName.history],
  LF_Brightness: [CustomWidgetName.compare],
  LF_Brush: [CustomWidgetName.compare],
  LF_CaptionImageWD14: [CustomWidgetName.countBarChart],
  LF_CharacterImpersonator: [CustomWidgetName.code],
  LF_CheckpointSelector: [CustomWidgetName.card],
  LF_CivitAIMetadataSetup: [CustomWidgetName.code],
  LF_Clarity: [CustomWidgetName.compare],
  LF_ColorAnalysis: [CustomWidgetName.tabBarChart],
  LF_CompareImages: [CustomWidgetName.compare],
  LF_Contrast: [CustomWidgetName.compare],
  LF_ControlPanel: [CustomWidgetName.controlPanel],
  LF_CreateMask: [CustomWidgetName.compare],
  LF_DetectRegions: [CustomWidgetName.compare],
  LF_Desaturation: [CustomWidgetName.compare],
  LF_DiffusionModelSelector: [CustomWidgetName.card],
  LF_DisplayBoolean: [CustomWidgetName.code],
  LF_DisplayFloat: [CustomWidgetName.code],
  LF_DisplayInteger: [CustomWidgetName.code],
  LF_DisplayJSON: [CustomWidgetName.code],
  LF_DisplayPrimitiveAsJSON: [CustomWidgetName.code],
  LF_DisplayString: [CustomWidgetName.code],
  LF_EmbeddingSelector: [CustomWidgetName.card],
  LF_EmptyImage: [CustomWidgetName.masonry],
  LF_ExtractFaceEmbedding: [CustomWidgetName.code],
  LF_ExtractPromptFromLoraTag: [CustomWidgetName.code],
  LF_ExtractString: [CustomWidgetName.code],
  LF_FilmGrain: [CustomWidgetName.compare],
  LF_Float: [CustomWidgetName.history],
  LF_GaussianBlur: [CustomWidgetName.compare],
  LF_GetRandomKeyFromJSON: [CustomWidgetName.code],
  LF_GetValueFromJSON: [CustomWidgetName.code],
  LF_ImageClassifier: [CustomWidgetName.code],
  LF_ImageHistogram: [CustomWidgetName.tabBarChart],
  LF_ImageListFromJSON: [CustomWidgetName.masonry],
  LF_ImagesEditingBreakpoint: [CustomWidgetName.imageEditor],
  LF_ImagesSlideshow: [CustomWidgetName.carousel],
  LF_ImageToSVG: [CustomWidgetName.compare],
  LF_Inpaint: [CustomWidgetName.compare],
  LF_InpaintAdvanced: [CustomWidgetName.compare],
  LF_Integer: [CustomWidgetName.history],
  LF_IsLandscape: [CustomWidgetName.tree],
  LF_JSONPromptCombinator: [CustomWidgetName.code],
  LF_KeywordCounter: [CustomWidgetName.countBarChart],
  LF_KeywordToggleFromJSON: [CustomWidgetName.chip],
  LF_Line: [CustomWidgetName.compare],
  LF_LLMChat: [CustomWidgetName.chat],
  LF_LLMMessenger: [CustomWidgetName.messenger],
  LF_LoadAndEditImages: [CustomWidgetName.imageEditor],
  LF_LoadFileOnce: [CustomWidgetName.history],
  LF_LoadCLIPSegModel: [CustomWidgetName.code],
  LF_LoadWD14Model: [CustomWidgetName.code],
  LF_LoadImages: [CustomWidgetName.masonry],
  LF_LoadLoraTags: [CustomWidgetName.cardsWithChip],
  LF_LoadMetadata: [CustomWidgetName.code, CustomWidgetName.upload],
  LF_LoraAndEmbeddingSelector: [CustomWidgetName.card],
  LF_LoraSelector: [CustomWidgetName.card],
  LF_LUTApplication: [CustomWidgetName.compare],
  LF_LUTGeneration: [CustomWidgetName.tabBarChart],
  LF_MarkdownDocGenerator: [CustomWidgetName.code],
  LF_MathOperation: [CustomWidgetName.code],
  LF_MultipleImageResizeForWeb: [CustomWidgetName.tree],
  LF_Notify: [],
  LF_ParsePromptWithLoraTags: [CustomWidgetName.code],
  LF_RandomBoolean: [CustomWidgetName.progressbar],
  LF_RegexReplace: [CustomWidgetName.code],
  LF_RegionExtractor: [CustomWidgetName.code],
  LF_RegionMask: [CustomWidgetName.compare],
  LF_ResizeImageByEdge: [CustomWidgetName.tree],
  LF_ResizeImageToDimension: [CustomWidgetName.tree],
  LF_ResizeImageToSquare: [CustomWidgetName.tree],
  LF_ResolutionSwitcher: [CustomWidgetName.progressbar],
  LF_SamplerSelector: [CustomWidgetName.history],
  LF_Saturation: [CustomWidgetName.compare],
  LF_SaveImageForCivitAI: [CustomWidgetName.masonry],
  LF_SaveJSON: [CustomWidgetName.tree],
  LF_SaveMarkdown: [CustomWidgetName.tree],
  LF_SaveText: [CustomWidgetName.tree],
  LF_SchedulerSelector: [CustomWidgetName.history],
  LF_Sepia: [CustomWidgetName.compare],
  LF_SequentialSeedsGenerator: [CustomWidgetName.history],
  LF_SetValueInJSON: [CustomWidgetName.code],
  LF_ShuffleJSONKeys: [CustomWidgetName.code],
  LF_Something2Number: [CustomWidgetName.code],
  LF_Something2String: [CustomWidgetName.code],
  LF_SortJSONKeys: [CustomWidgetName.code],
  LF_SortTags: [CustomWidgetName.code],
  LF_SplitTone: [CustomWidgetName.compare],
  LF_String: [CustomWidgetName.history],
  LF_StringReplace: [CustomWidgetName.code],
  LF_StringTemplate: [CustomWidgetName.code],
  LF_StringToJSON: [CustomWidgetName.code],
  LF_SwitchFloat: [CustomWidgetName.progressbar],
  LF_SwitchImage: [CustomWidgetName.progressbar],
  LF_SwitchInteger: [CustomWidgetName.progressbar],
  LF_SwitchJSON: [CustomWidgetName.progressbar],
  LF_SwitchString: [CustomWidgetName.progressbar],
  LF_TiledSuperRes: [CustomWidgetName.compare],
  LF_TiltShift: [CustomWidgetName.compare],
  LF_UpdateUsageStatistics: [CustomWidgetName.code],
  LF_UpscaleModelSelector: [CustomWidgetName.history],
  LF_UsageStatistics: [CustomWidgetName.tabBarChart],
  LF_UrandomSeedGenerator: [CustomWidgetName.tree],
  LF_VAEDecode: [CustomWidgetName.code],
  LF_VAESelector: [CustomWidgetName.history],
  LF_ONNXSelector: [CustomWidgetName.history],
  LF_Vibrance: [CustomWidgetName.compare],
  LF_ViewImages: [CustomWidgetName.masonry],
  LF_ViewSVGs: [CustomWidgetName.masonry],
  LF_Vignette: [CustomWidgetName.compare],
  LF_WallOfText: [CustomWidgetName.code],
  LF_WriteJSON: [CustomWidgetName.textarea]
};
const onAfterGraphConfigured = async (ctor, cb) => {
  const proto = ctor.prototype;
  const original = proto.onAfterGraphConfigured;
  proto.onAfterGraphConfigured = function() {
    var _a, _b;
    const r2 = original == null ? void 0 : original.apply(this, arguments);
    try {
      cb(this);
    } catch (err) {
      (_b = (_a = getLfManager()) == null ? void 0 : _a.log) == null ? void 0 : _b.call(_a, "onAfterGraphConfigured hook error", { err }, LogSeverity.Warning);
    }
    return r2;
  };
};
const onConnectionsChange = async (nodeType) => {
  const onConnectionsChange2 = nodeType.prototype.onConnectionsChange;
  nodeType.prototype.onConnectionsChange = function() {
    const r2 = onConnectionsChange2 == null ? void 0 : onConnectionsChange2.apply(this, arguments);
    const node = this;
    switch (node.comfyClass) {
      case NodeName.keywordToggleFromJson:
        chipCb(node);
        break;
      case NodeName.llmMessenger:
        messengerCb(node);
        break;
    }
    return r2;
  };
};
const onDrawBackground = async (nodeType) => {
  const onDrawBackground2 = nodeType.prototype.onDrawBackground;
  nodeType.prototype.onDrawBackground = function() {
    const r2 = onDrawBackground2 == null ? void 0 : onDrawBackground2.apply(this, arguments);
    const node = this;
    refreshChart(node);
    return r2;
  };
};
const onNodeCreated = async (nodeType) => {
  const onNodeCreated2 = nodeType.prototype.onNodeCreated;
  nodeType.prototype.onNodeCreated = function() {
    var _a;
    const r2 = onNodeCreated2 ? onNodeCreated2.apply(this, arguments) : void 0;
    const node = this;
    for (let index = 0; index < ((_a = node.widgets) == null ? void 0 : _a.length); index++) {
      const w2 = node.widgets[index];
      switch (w2.type.toUpperCase()) {
        case CustomWidgetName.imageEditor:
          const ds = getApiRoutes().comfy.getDragAndScale();
          if (ds) {
            const onredraw = ds.onredraw;
            ds.onredraw = function() {
              const r3 = onredraw ? onredraw.apply(this, arguments) : void 0;
              const state = w2.options.getState();
              setCanvasSizeCb(state.elements.imageviewer);
              return r3;
            };
          }
          break;
        case ComfyWidgetName.customtext:
        case ComfyWidgetName.string:
        case ComfyWidgetName.text:
          w2.serializeValue = () => {
            const comfy = getApiRoutes().comfy.comfyUi();
            return comfy.utils.applyTextReplacements(comfy.app.app, w2.value);
          };
          break;
      }
    }
    return r2;
  };
};
const chipCb = (node) => {
  var _a, _b, _c, _d, _e;
  const lfManager = getLfManager();
  const routes = getApiRoutes().comfy;
  const textarea = getInput(node, ComfyWidgetName.json);
  const linkInput = routes.getLinkById((_a = textarea == null ? void 0 : textarea.link) == null ? void 0 : _a.toString());
  const nodeInput = routes.getNodeById((_b = linkInput == null ? void 0 : linkInput.origin_id) == null ? void 0 : _b.toString());
  if (!textarea || !linkInput || !nodeInput) {
    return;
  }
  const chipW = getCustomWidget(node, CustomWidgetName.chip);
  const datasetW = (_c = nodeInput == null ? void 0 : nodeInput.widgets) == null ? void 0 : _c[linkInput.origin_slot];
  if (!((_d = chipW.options) == null ? void 0 : _d.getState) || !((_e = datasetW.options) == null ? void 0 : _e.getValue)) {
    lfManager.log("Missing options", { chipW, datasetW }, LogSeverity.Warning);
    return;
  }
  const dataset = datasetW.options.getValue();
  const chip = chipW.options.getState().chip;
  try {
    const newData = unescapeJson(dataset).parsedJson;
    if (isValidJSON(newData) && isValidJSON(chip.lfDataset)) {
      if (!areJSONEqual(newData, chip.lfDataset)) {
        chip.lfDataset = newData;
        lfManager.log("Updated chip data", { dataset }, LogSeverity.Info);
      }
    } else {
      if (isValidJSON(newData)) {
        chip.lfDataset = newData;
        lfManager.log("Set chip data", { dataset }, LogSeverity.Info);
      } else {
        lfManager.log("Invalid JSON data", { dataset, error: "Invalid JSON" }, LogSeverity.Warning);
      }
    }
  } catch (error2) {
    lfManager.log("Error processing chip data", { dataset, error: error2 }, LogSeverity.Error);
  }
};
const messengerCb = (node) => {
  var _a, _b, _c, _d, _e, _f, _g;
  const textarea = getInput(node, ComfyWidgetName.json);
  const linkInput = getApiRoutes().comfy.getLinkById((_a = textarea == null ? void 0 : textarea.link) == null ? void 0 : _a.toString());
  const nodeInput = getApiRoutes().comfy.getNodeById((_b = linkInput == null ? void 0 : linkInput.origin_id) == null ? void 0 : _b.toString());
  if (!textarea || !linkInput || !nodeInput) {
    return;
  }
  const messengerW = getCustomWidget(node, CustomWidgetName.messenger);
  const datasetW = (_c = nodeInput == null ? void 0 : nodeInput.widgets) == null ? void 0 : _c[linkInput.origin_slot];
  if (!((_d = datasetW == null ? void 0 : datasetW.options) == null ? void 0 : _d.getValue)) {
    return;
  }
  const dataset = datasetW.options.getValue();
  const messenger = ((_e = messengerW == null ? void 0 : messengerW.options) == null ? void 0 : _e.getState()).elements.messenger;
  try {
    const newData = unescapeJson(dataset).parsedJson;
    if (isValidJSON(newData) && isValidJSON(messenger.lfDataset)) {
      if (!areJSONEqual(newData, messenger.lfDataset)) {
        messenger.lfDataset = newData;
        messenger.reset();
        getLfManager().log("Updated messenger data", { dataset }, LogSeverity.Info);
      }
    } else {
      if (isValidJSON(newData)) {
        messenger.lfDataset = newData;
        messenger.reset();
        getLfManager().log("Set messenger data", { dataset }, LogSeverity.Info);
      } else {
        getLfManager().log("Invalid JSON data", { dataset, error: "Invalid JSON" }, LogSeverity.Warning);
      }
    }
    const placeholder = messenger.nextSibling || messenger.previousSibling;
    if ((_g = (_f = messenger.lfDataset) == null ? void 0 : _f.nodes) == null ? void 0 : _g[0]) {
      placeholder.classList.add(MessengerCSS.PlaceholderHidden);
    } else {
      placeholder.classList.remove(MessengerCSS.PlaceholderHidden);
    }
  } catch (error2) {
    getLfManager().log("Error processing messenger data", { dataset, error: error2 }, LogSeverity.Error);
  }
};
const setCanvasSizeCb = (imageviewer) => {
  requestAnimationFrame(async () => {
    try {
      const { canvas } = (await imageviewer.getComponents()).details;
      canvas == null ? void 0 : canvas.resizeCanvas();
    } catch (error2) {
    }
  });
};
const getLogStyle = () => {
  return {
    fontFamily: "var(--lf-font-family-monospace)",
    margin: "0",
    maxWidth: "100%",
    overflow: "hidden",
    padding: "4px 8px",
    textOverflow: "ellipsis"
  };
};
function installLFBeforeFreeHooks(api2, opts = {}) {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {
  });
  if (!isFreeHookAPI(api2)) {
    logger('"api" object not available; cannot install free hooks yet', {}, LogSeverity.Warning);
    return { freeMemoryHook: false, fetchFallbackHook: false };
  }
  const wrap = opts.freeWrapper ?? ((fn) => async function(options) {
    await beforeFree(options);
    return fn.apply(this ?? api2, [options]);
  });
  const installFreeMemory = () => {
    try {
      if (api2[LFFreeFlags.PatchedFree] === true)
        return true;
      const current = api2.freeMemory;
      if (typeof current === "function") {
        api2[LFFreeFlags.OriginalFreeRef] = current;
        api2.freeMemory = wrap(current);
        api2[LFFreeFlags.PatchedFree] = true;
        return true;
      }
      const desc = Object.getOwnPropertyDescriptor(api2, "freeMemory");
      if (!desc || desc.configurable) {
        let original;
        Object.defineProperty(api2, "freeMemory", {
          configurable: true,
          enumerable: true,
          get() {
            return original;
          },
          set(fn) {
            if (api2[LFFreeFlags.PatchedFree] === true) {
              original = fn;
              return;
            }
            if (typeof fn === "function") {
              api2[LFFreeFlags.OriginalFreeRef] = fn;
              original = wrap(fn);
              api2[LFFreeFlags.PatchedFree] = true;
            } else {
              original = fn;
            }
          }
        });
      }
      return false;
    } catch (e2) {
      logger("Failed to patch freeMemory; proceeding without LF cache clear hook", { e: e2 }, LogSeverity.Warning);
      return false;
    }
  };
  let freePatched = installFreeMemory();
  if (!freePatched) {
    let count = 0;
    const iv = setInterval(() => {
      count += 1;
      if (installFreeMemory() || api2[LFFreeFlags.PatchedFree] === true || count > attempts) {
        clearInterval(iv);
      }
    }, intervalMs);
  }
  const installFetchFallback = () => {
    try {
      if (api2[LFFreeFlags.PatchedFetch] === true) {
        return true;
      }
      const originalFetchApi = api2.fetchApi;
      if (typeof originalFetchApi !== "function") {
        return false;
      }
      api2[LFFreeFlags.PatchedFetch] = true;
      api2.fetchApi = async function(path, init) {
        try {
          const url = typeof path === "string" ? path : String(path ?? "");
          const isFree = url.endsWith("/free") || url.endsWith("/api/free");
          const isOur = url.includes("/lf-nodes/free");
          const method = ((init == null ? void 0 : init.method) ?? "GET").toUpperCase();
          if (isFree && !isOur && method === "POST" && api2[LFFreeFlags.InBeforeFree] !== true) {
            api2[LFFreeFlags.InBeforeFree] = true;
            try {
              await beforeFree(init);
            } finally {
              api2[LFFreeFlags.InBeforeFree] = false;
            }
          }
        } catch {
        }
        return originalFetchApi.apply(this ?? api2, [path, init]);
      };
      return true;
    } catch (e2) {
      logger("Failed to patch api.fetchApi; proceeding without LF cache clear fallback", { e: e2 }, LogSeverity.Warning);
      return false;
    }
  };
  const fetchPatched = installFetchFallback();
  return { freeMemoryHook: freePatched, fetchFallbackHook: fetchPatched };
}
const applySelectionColumn = (dataset, selection) => {
  var _a, _b, _c;
  const lfData = (_c = (_b = (_a = getLfManager()) == null ? void 0 : _a.getManagers()) == null ? void 0 : _b.lfFramework) == null ? void 0 : _c.data;
  const existingColumns = Array.isArray(dataset == null ? void 0 : dataset.columns) ? dataset.columns : [];
  const [existingSelectionColumn] = lfData ? lfData.column.find(existingColumns, { id: "selected" }) : [];
  const updatedSelectionColumn = {
    ...existingSelectionColumn ?? { id: "selected" },
    title: selection
  };
  const nextColumns = existingSelectionColumn ? existingColumns.map((col) => col.id === "selected" ? updatedSelectionColumn : col) : [...existingColumns, updatedSelectionColumn];
  return {
    ...dataset,
    columns: nextColumns,
    selection
  };
};
const buildSelectionPayload = ({ dataset, index, nodes, selectedShape, fallbackContextId }) => {
  var _a, _b;
  const resolvedContextId = dataset.context_id ?? ((_a = dataset.selection) == null ? void 0 : _a.context_id) ?? fallbackContextId;
  const selection = {
    index,
    context_id: resolvedContextId
  };
  const derivedName = deriveSelectionName(selectedShape);
  if (derivedName) {
    selection.name = derivedName;
  }
  const selectedNode = Array.isArray(nodes) && index >= 0 && index < nodes.length && nodes[index] ? nodes[index] : void 0;
  if (selectedNode && typeof selectedNode === "object") {
    const nodeId = asString(selectedNode.id);
    if (nodeId) {
      selection.node_id = nodeId;
    }
    const imageCell = (_b = selectedNode.cells) == null ? void 0 : _b.lfImage;
    const imageValue = asString(imageCell == null ? void 0 : imageCell.value) ?? asString(imageCell == null ? void 0 : imageCell.lfValue);
    if (imageValue) {
      selection.url = imageValue;
    }
  }
  return { selection, contextId: resolvedContextId };
};
const deriveDirectoryValue = (directory) => {
  if (!directory) {
    return void 0;
  }
  if (isString(directory.raw)) {
    return directory.raw;
  }
  if (isString(directory.relative)) {
    return directory.relative;
  }
  if (isString(directory.resolved)) {
    return directory.resolved;
  }
  return void 0;
};
const deriveSelectionName = (selectedShape) => {
  if (!selectedShape) {
    return void 0;
  }
  const shape = selectedShape.shape;
  const htmlProps = (shape == null ? void 0 : shape.htmlProps) ?? {};
  const htmlTitle = asString(htmlProps["title"]);
  const htmlId = asString(htmlProps["id"]);
  const shapeValue = asString(shape == null ? void 0 : shape.value);
  const lfValue = asString(shape == null ? void 0 : shape.lfValue);
  return htmlTitle ?? htmlId ?? shapeValue ?? lfValue ?? void 0;
};
const ensureDatasetContext = (dataset, state) => {
  if (!dataset) {
    return state == null ? void 0 : state.contextId;
  }
  const setStateContext = (contextId) => {
    if (contextId && state) {
      state.contextId = contextId;
    }
  };
  if (dataset.context_id) {
    setStateContext(dataset.context_id);
  } else if (state == null ? void 0 : state.contextId) {
    dataset.context_id = state.contextId;
  }
  const selection = dataset.selection;
  const resolvedContext = (selection == null ? void 0 : selection.context_id) ?? dataset.context_id ?? (state == null ? void 0 : state.contextId);
  if (selection && resolvedContext) {
    selection.context_id = selection.context_id ?? resolvedContext;
    if (!dataset.context_id) {
      dataset.context_id = resolvedContext;
    }
    setStateContext(resolvedContext);
    return resolvedContext;
  }
  if (dataset.context_id) {
    setStateContext(dataset.context_id);
    return dataset.context_id;
  }
  if (state == null ? void 0 : state.contextId) {
    dataset.context_id = state.contextId;
    return state.contextId;
  }
  return void 0;
};
const getNavigationDirectory = (dataset) => {
  var _a;
  return (_a = dataset == null ? void 0 : dataset.navigation) == null ? void 0 : _a.directory;
};
const hasContextChanged = (previousContextId, nextContextId) => {
  return previousContextId !== nextContextId;
};
const hasSelectionChanged = (previousSelection, nextSelection) => {
  return JSON.stringify(previousSelection ?? null) !== JSON.stringify(nextSelection ?? null);
};
const mergeNavigationDirectory = (dataset, directory) => {
  var _a;
  const current = ((_a = dataset.navigation) == null ? void 0 : _a.directory) ?? {};
  const next = {
    ...current,
    ...directory
  };
  dataset.navigation = dataset.navigation ?? {};
  dataset.navigation.directory = next;
  return next;
};
const resolveSelectionIndex = (selectedShape, nodes) => {
  var _a;
  if (typeof (selectedShape == null ? void 0 : selectedShape.index) === "number") {
    return selectedShape.index;
  }
  if (!Array.isArray(nodes)) {
    return void 0;
  }
  const shape = selectedShape == null ? void 0 : selectedShape.shape;
  const shapeId = asString((_a = shape == null ? void 0 : shape.htmlProps) == null ? void 0 : _a["id"]);
  const shapeValue = asString(shape == null ? void 0 : shape.value) ?? asString(shape == null ? void 0 : shape.lfValue);
  const resolvedIndex = nodes.findIndex((node) => {
    var _a2, _b;
    if (!node || typeof node !== "object") {
      return false;
    }
    const imageCell = (_a2 = node.cells) == null ? void 0 : _a2.lfImage;
    if (!imageCell) {
      return false;
    }
    const cellId = asString((_b = imageCell.htmlProps) == null ? void 0 : _b["id"]);
    const cellValue = asString(imageCell.value) ?? asString(imageCell.lfValue);
    if (shapeId && cellId === shapeId) {
      return true;
    }
    if (shapeValue && cellValue === shapeValue) {
      return true;
    }
    return false;
  });
  return resolvedIndex >= 0 ? resolvedIndex : void 0;
};
const MANUAL_APPLY_PROCESSING_LABEL = "Applying…";
const hasManualApplyPendingChanges = (state) => {
  const manual = state.manualApply;
  if (!manual) {
    return false;
  }
  return manual.latestChangeId > manual.latestAppliedChangeId;
};
const updateManualApplyButton = (state) => {
  const manual = state.manualApply;
  if (!manual) {
    return;
  }
  manual.dirty = hasManualApplyPendingChanges(state);
  if (manual.isProcessing) {
    manual.button.lfUiState = "disabled";
    manual.button.lfLabel = MANUAL_APPLY_PROCESSING_LABEL;
    return;
  }
  manual.button.lfLabel = manual.defaultLabel;
  if (manual.dirty) {
    manual.button.lfUiState = "success";
  } else {
    manual.button.lfUiState = "disabled";
  }
};
const initManualApplyState = (state, button) => {
  state.manualApply = {
    button,
    defaultLabel: button.lfLabel ?? "Apply",
    dirty: false,
    isProcessing: false,
    changeCounter: 0,
    latestChangeId: 0,
    latestAppliedChangeId: 0,
    activeRequestChangeId: 0
  };
  updateManualApplyButton(state);
};
const registerManualApplyChange = (state) => {
  var _a;
  if (!((_a = state.filter) == null ? void 0 : _a.requiresManualApply) || !state.manualApply) {
    return;
  }
  const manual = state.manualApply;
  manual.latestChangeId = ++manual.changeCounter;
  if (!manual.isProcessing) {
    updateManualApplyButton(state);
  }
};
const beginManualApplyRequest = (state) => {
  if (!state.manualApply) {
    return;
  }
  const manual = state.manualApply;
  manual.isProcessing = true;
  manual.activeRequestChangeId = manual.latestChangeId;
  updateManualApplyButton(state);
};
const resolveManualApplyRequest = (state, wasSuccessful) => {
  if (!state.manualApply) {
    return;
  }
  const manual = state.manualApply;
  if (wasSuccessful) {
    manual.latestAppliedChangeId = Math.max(manual.latestAppliedChangeId, manual.activeRequestChangeId);
  }
  manual.activeRequestChangeId = 0;
  manual.isProcessing = false;
  updateManualApplyButton(state);
};
const apiCall$2 = async (state, addSnapshot) => {
  var _a, _b;
  const { elements, filter, filterType } = state;
  const { imageviewer } = elements;
  const lfManager = getLfManager();
  const snapshot = await imageviewer.getCurrentSnapshot();
  if (!snapshot) {
    lfManager.log("No snapshot available for processing!", {}, LogSeverity.Warning);
    return false;
  }
  const snapshotValue = snapshot.value;
  const baseSettings = filter.settings;
  const payload = {
    ...baseSettings
  };
  const contextDataset = imageviewer.lfDataset;
  const contextId = ensureDatasetContext(contextDataset, state);
  if (!contextId && filterType === "inpaint") {
    lfManager.log("Missing editing context. Run the workflow to register an editing session before using inpaint.", { dataset: contextDataset }, LogSeverity.Warning);
    if ((_a = state.manualApply) == null ? void 0 : _a.isProcessing) {
      resolveManualApplyRequest(state, false);
    }
    return false;
  }
  payload.context_id = contextId;
  requestAnimationFrame(() => imageviewer.setSpinnerStatus(true));
  let isSuccess = false;
  try {
    const response = await getApiRoutes().image.process(snapshotValue, filterType, payload);
    if (response.mask) {
      lfManager.log("Saved inpaint mask preview to temp", { mask: response.mask }, LogSeverity.Info);
    }
    if (response.cutout) {
      lfManager.log("Saved cutout preview to temp", { cutout: response.cutout }, LogSeverity.Info);
    }
    if (response.stats) {
      lfManager.log("Filter statistics", { stats: response.stats }, LogSeverity.Info);
    }
    if (addSnapshot) {
      await imageviewer.addSnapshot(response.data);
    } else {
      const { canvas } = (await imageviewer.getComponents()).details;
      const image2 = await canvas.getImage();
      requestAnimationFrame(() => image2.lfValue = response.data);
    }
    isSuccess = true;
  } catch (error2) {
    lfManager.log("Error processing image!", { error: error2 }, LogSeverity.Error);
  }
  requestAnimationFrame(() => imageviewer.setSpinnerStatus(false));
  if ((_b = state.manualApply) == null ? void 0 : _b.isProcessing) {
    resolveManualApplyRequest(state, isSuccess);
  }
  return isSuccess;
};
var ImageEditorCSS;
(function(ImageEditorCSS2) {
  ImageEditorCSS2["Content"] = "lf-imageeditor";
  ImageEditorCSS2["Widget"] = "lf-imageeditor__widget";
  ImageEditorCSS2["Actions"] = "lf-imageeditor__actions";
  ImageEditorCSS2["Grid"] = "lf-imageeditor__grid";
  ImageEditorCSS2["GridHasActions"] = "lf-imageeditor__grid--has-actions";
  ImageEditorCSS2["GridIsInactive"] = "lf-imageeditor__grid--is-inactive";
  ImageEditorCSS2["Settings"] = "lf-imageeditor__settings";
  ImageEditorCSS2["SettingsControls"] = "lf-imageeditor__settings__controls";
  ImageEditorCSS2["SettingsButtons"] = "lf-imageeditor__settings__buttons";
})(ImageEditorCSS || (ImageEditorCSS = {}));
var ImageEditorStatus;
(function(ImageEditorStatus2) {
  ImageEditorStatus2["Completed"] = "completed";
  ImageEditorStatus2["Pending"] = "pending";
})(ImageEditorStatus || (ImageEditorStatus = {}));
var ImageEditorColumnId;
(function(ImageEditorColumnId2) {
  ImageEditorColumnId2["Path"] = "path";
  ImageEditorColumnId2["Status"] = "status";
})(ImageEditorColumnId || (ImageEditorColumnId = {}));
var ImageEditorIcons;
(function(ImageEditorIcons2) {
  ImageEditorIcons2["Interrupt"] = "x";
  ImageEditorIcons2["Reset"] = "refresh";
  ImageEditorIcons2["Resume"] = "check";
})(ImageEditorIcons || (ImageEditorIcons = {}));
var ImageEditorControls;
(function(ImageEditorControls2) {
  ImageEditorControls2["Canvas"] = "canvas";
  ImageEditorControls2["Slider"] = "slider";
  ImageEditorControls2["Textfield"] = "textfield";
  ImageEditorControls2["Toggle"] = "toggle";
})(ImageEditorControls || (ImageEditorControls = {}));
var ImageEditorCanvasIds;
(function(ImageEditorCanvasIds2) {
  ImageEditorCanvasIds2["B64Canvas"] = "b64_canvas";
  ImageEditorCanvasIds2["Points"] = "points";
})(ImageEditorCanvasIds || (ImageEditorCanvasIds = {}));
var ImageEditorSliderIds;
(function(ImageEditorSliderIds2) {
  ImageEditorSliderIds2["Amount"] = "amount";
  ImageEditorSliderIds2["Balance"] = "balance";
  ImageEditorSliderIds2["BlueChannel"] = "b_channel";
  ImageEditorSliderIds2["BlurKernelSize"] = "blur_kernel_size";
  ImageEditorSliderIds2["BlurSigma"] = "blur_sigma";
  ImageEditorSliderIds2["ClarityAmount"] = "clarity_amount";
  ImageEditorSliderIds2["DenoisePercentage"] = "denoise_percentage";
  ImageEditorSliderIds2["Cfg"] = "cfg";
  ImageEditorSliderIds2["Dilate"] = "dilate";
  ImageEditorSliderIds2["FocusPosition"] = "focus_position";
  ImageEditorSliderIds2["FocusSize"] = "focus_size";
  ImageEditorSliderIds2["Gamma"] = "gamma";
  ImageEditorSliderIds2["GreenChannel"] = "g_channel";
  ImageEditorSliderIds2["Intensity"] = "intensity";
  ImageEditorSliderIds2["Midpoint"] = "midpoint";
  ImageEditorSliderIds2["Opacity"] = "opacity";
  ImageEditorSliderIds2["RoiAlign"] = "roi_align";
  ImageEditorSliderIds2["RoiMinSize"] = "roi_min_size";
  ImageEditorSliderIds2["RoiPadding"] = "roi_padding";
  ImageEditorSliderIds2["Radius"] = "radius";
  ImageEditorSliderIds2["RedChannel"] = "r_channel";
  ImageEditorSliderIds2["SharpenAmount"] = "sharpen_amount";
  ImageEditorSliderIds2["Size"] = "size";
  ImageEditorSliderIds2["Sigma"] = "sigma";
  ImageEditorSliderIds2["Softness"] = "softness";
  ImageEditorSliderIds2["Steps"] = "steps";
  ImageEditorSliderIds2["Strength"] = "strength";
  ImageEditorSliderIds2["Threshold"] = "threshold";
  ImageEditorSliderIds2["UpsampleTarget"] = "upsample_target";
  ImageEditorSliderIds2["Feather"] = "feather";
})(ImageEditorSliderIds || (ImageEditorSliderIds = {}));
var ImageEditorTextfieldIds;
(function(ImageEditorTextfieldIds2) {
  ImageEditorTextfieldIds2["Color"] = "color";
  ImageEditorTextfieldIds2["Highlights"] = "highlights";
  ImageEditorTextfieldIds2["NegativePrompt"] = "negative_prompt";
  ImageEditorTextfieldIds2["PositivePrompt"] = "positive_prompt";
  ImageEditorTextfieldIds2["Seed"] = "seed";
  ImageEditorTextfieldIds2["Shadows"] = "shadows";
  ImageEditorTextfieldIds2["Tint"] = "tint";
})(ImageEditorTextfieldIds || (ImageEditorTextfieldIds = {}));
var ImageEditorToggleIds;
(function(ImageEditorToggleIds2) {
  ImageEditorToggleIds2["ClipSoft"] = "clip_soft";
  ImageEditorToggleIds2["Localized"] = "localized";
  ImageEditorToggleIds2["ProtectSkin"] = "protect_skin";
  ImageEditorToggleIds2["Shape"] = "shape";
  ImageEditorToggleIds2["Smooth"] = "smoooth";
  ImageEditorToggleIds2["SoftBlend"] = "soft_blend";
  ImageEditorToggleIds2["TransparentBackground"] = "transparent_background";
  ImageEditorToggleIds2["Vertical"] = "vertical";
  ImageEditorToggleIds2["UseConditioning"] = "use_conditioning";
  ImageEditorToggleIds2["RoiAuto"] = "roi_auto";
  ImageEditorToggleIds2["RoiAlignAuto"] = "roi_align_auto";
})(ImageEditorToggleIds || (ImageEditorToggleIds = {}));
var ImageEditorBackgroundRemoverIds;
(function(ImageEditorBackgroundRemoverIds2) {
  ImageEditorBackgroundRemoverIds2["Color"] = "color";
  ImageEditorBackgroundRemoverIds2["TransparentBackground"] = "transparent_background";
})(ImageEditorBackgroundRemoverIds || (ImageEditorBackgroundRemoverIds = {}));
var ImageEditorBlendIds;
(function(ImageEditorBlendIds2) {
  ImageEditorBlendIds2["Opacity"] = "opacity";
})(ImageEditorBlendIds || (ImageEditorBlendIds = {}));
var ImageEditorBloomIds;
(function(ImageEditorBloomIds2) {
  ImageEditorBloomIds2["Threshold"] = "threshold";
  ImageEditorBloomIds2["Radius"] = "radius";
  ImageEditorBloomIds2["Intensity"] = "intensity";
  ImageEditorBloomIds2["Tint"] = "tint";
})(ImageEditorBloomIds || (ImageEditorBloomIds = {}));
var ImageEditorBrightnessIds;
(function(ImageEditorBrightnessIds2) {
  ImageEditorBrightnessIds2["Strength"] = "strength";
  ImageEditorBrightnessIds2["Gamma"] = "gamma";
  ImageEditorBrightnessIds2["Midpoint"] = "midpoint";
  ImageEditorBrightnessIds2["Localized"] = "localized";
})(ImageEditorBrightnessIds || (ImageEditorBrightnessIds = {}));
var ImageEditorBrushIds;
(function(ImageEditorBrushIds2) {
  ImageEditorBrushIds2["B64Canvas"] = "b64_canvas";
  ImageEditorBrushIds2["Color"] = "color";
  ImageEditorBrushIds2["Opacity"] = "opacity";
  ImageEditorBrushIds2["Size"] = "size";
})(ImageEditorBrushIds || (ImageEditorBrushIds = {}));
var ImageEditorClarityIds;
(function(ImageEditorClarityIds2) {
  ImageEditorClarityIds2["Amount"] = "clarity_amount";
})(ImageEditorClarityIds || (ImageEditorClarityIds = {}));
var ImageEditorContrastIds;
(function(ImageEditorContrastIds2) {
  ImageEditorContrastIds2["Strength"] = "strength";
  ImageEditorContrastIds2["Localized"] = "contrast";
  ImageEditorContrastIds2["Midpoint"] = "midpoint";
})(ImageEditorContrastIds || (ImageEditorContrastIds = {}));
var ImageEditorDesaturateIds;
(function(ImageEditorDesaturateIds2) {
  ImageEditorDesaturateIds2["RedChannel"] = "r_channel";
  ImageEditorDesaturateIds2["GreenChannel"] = "g_channel";
  ImageEditorDesaturateIds2["BlueChannel"] = "b_channel";
  ImageEditorDesaturateIds2["Strength"] = "strength";
})(ImageEditorDesaturateIds || (ImageEditorDesaturateIds = {}));
var ImageEditorFilmGrainIds;
(function(ImageEditorFilmGrainIds2) {
  ImageEditorFilmGrainIds2["Intensity"] = "intensity";
  ImageEditorFilmGrainIds2["Size"] = "size";
  ImageEditorFilmGrainIds2["Tint"] = "tint";
  ImageEditorFilmGrainIds2["SoftBlend"] = "soft_blend";
})(ImageEditorFilmGrainIds || (ImageEditorFilmGrainIds = {}));
var ImageEditorGaussianBlurIds;
(function(ImageEditorGaussianBlurIds2) {
  ImageEditorGaussianBlurIds2["BlurKernelSize"] = "blur_kernel_size";
  ImageEditorGaussianBlurIds2["BlurSigma"] = "blur_sigma";
})(ImageEditorGaussianBlurIds || (ImageEditorGaussianBlurIds = {}));
var ImageEditorLineIds;
(function(ImageEditorLineIds2) {
  ImageEditorLineIds2["Color"] = "color";
  ImageEditorLineIds2["Opacity"] = "opacity";
  ImageEditorLineIds2["Points"] = "points";
  ImageEditorLineIds2["Size"] = "size";
  ImageEditorLineIds2["Smooth"] = "smooth";
})(ImageEditorLineIds || (ImageEditorLineIds = {}));
var ImageEditorSaturationIds;
(function(ImageEditorSaturationIds2) {
  ImageEditorSaturationIds2["Intensity"] = "intensity";
})(ImageEditorSaturationIds || (ImageEditorSaturationIds = {}));
var ImageEditorSepiaIds;
(function(ImageEditorSepiaIds2) {
  ImageEditorSepiaIds2["Intensity"] = "intensity";
})(ImageEditorSepiaIds || (ImageEditorSepiaIds = {}));
var ImageEditorSplitToneIds;
(function(ImageEditorSplitToneIds2) {
  ImageEditorSplitToneIds2["Balance"] = "balance";
  ImageEditorSplitToneIds2["Highlights"] = "highlights";
  ImageEditorSplitToneIds2["Intensity"] = "intensity";
  ImageEditorSplitToneIds2["Shadows"] = "shadows";
  ImageEditorSplitToneIds2["Softness"] = "softness";
})(ImageEditorSplitToneIds || (ImageEditorSplitToneIds = {}));
var ImageEditorTiltShiftIds;
(function(ImageEditorTiltShiftIds2) {
  ImageEditorTiltShiftIds2["FocusPosition"] = "focus_position";
  ImageEditorTiltShiftIds2["FocusSize"] = "focus_size";
  ImageEditorTiltShiftIds2["Radius"] = "radius";
  ImageEditorTiltShiftIds2["Smooth"] = "smooth";
  ImageEditorTiltShiftIds2["Vertical"] = "vertical";
})(ImageEditorTiltShiftIds || (ImageEditorTiltShiftIds = {}));
var ImageEditorUnsharpMaskIds;
(function(ImageEditorUnsharpMaskIds2) {
  ImageEditorUnsharpMaskIds2["Amount"] = "amount";
  ImageEditorUnsharpMaskIds2["Radius"] = "radius";
  ImageEditorUnsharpMaskIds2["Sigma"] = "sigma";
  ImageEditorUnsharpMaskIds2["Threshold"] = "threshold";
})(ImageEditorUnsharpMaskIds || (ImageEditorUnsharpMaskIds = {}));
var ImageEditorVibranceIds;
(function(ImageEditorVibranceIds2) {
  ImageEditorVibranceIds2["Intensity"] = "intensity";
  ImageEditorVibranceIds2["ClipSoft"] = "clip_soft";
  ImageEditorVibranceIds2["ProtectSkin"] = "protect_skin";
})(ImageEditorVibranceIds || (ImageEditorVibranceIds = {}));
var ImageEditorVignetteIds;
(function(ImageEditorVignetteIds2) {
  ImageEditorVignetteIds2["Color"] = "color";
  ImageEditorVignetteIds2["Intensity"] = "intensity";
  ImageEditorVignetteIds2["Radius"] = "radius";
  ImageEditorVignetteIds2["Shape"] = "shape";
})(ImageEditorVignetteIds || (ImageEditorVignetteIds = {}));
var ImageEditorInpaintIds;
(function(ImageEditorInpaintIds2) {
  ImageEditorInpaintIds2["B64Canvas"] = "b64_canvas";
  ImageEditorInpaintIds2["Cfg"] = "cfg";
  ImageEditorInpaintIds2["DenoisePercentage"] = "denoise_percentage";
  ImageEditorInpaintIds2["NegativePrompt"] = "negative_prompt";
  ImageEditorInpaintIds2["PositivePrompt"] = "positive_prompt";
  ImageEditorInpaintIds2["Seed"] = "seed";
  ImageEditorInpaintIds2["Steps"] = "steps";
  ImageEditorInpaintIds2["UseConditioning"] = "use_conditioning";
  ImageEditorInpaintIds2["RoiAuto"] = "roi_auto";
  ImageEditorInpaintIds2["RoiPadding"] = "roi_padding";
  ImageEditorInpaintIds2["RoiAlign"] = "roi_align";
  ImageEditorInpaintIds2["RoiAlignAuto"] = "roi_align_auto";
  ImageEditorInpaintIds2["RoiMinSize"] = "roi_min_size";
  ImageEditorInpaintIds2["Dilate"] = "dilate";
  ImageEditorInpaintIds2["Feather"] = "feather";
  ImageEditorInpaintIds2["UpsampleTarget"] = "upsample_target";
})(ImageEditorInpaintIds || (ImageEditorInpaintIds = {}));
const BACKGROUND_SETTINGS = {
  backgroundRemover: {
    controlIds: ImageEditorBackgroundRemoverIds,
    settings: {
      color: "#000000",
      transparent_background: true
    },
    configs: {
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Background color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#000000",
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: "Used to fill the removed background when transparency is disabled.",
          type: "color"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Transparent background",
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.TransparentBackground,
          off: "false",
          on: "true",
          title: "Keep an alpha channel instead of filling the background with the selected color."
        }
      ]
    }
  }
};
const BASIC_ADJUSTMENT_SETTINGS = {
  //#region Brightness
  brightness: {
    controlIds: ImageEditorBrightnessIds,
    settings: {
      strength: 0,
      gamma: 0,
      localized: false,
      midpoint: 0.5
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Brightness Strength",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: "1",
          min: "-1",
          step: "0.05",
          title: "Adjust the brightness of the image. Negative values darken, positive values brighten."
        },
        {
          ariaLabel: "Gamma",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Gamma,
          max: "3",
          min: "0.1",
          step: "0.1",
          title: "Adjust the gamma correction. Values < 1 brighten shadows, > 1 darken highlights."
        },
        {
          ariaLabel: "Midpoint",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Midpoint,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Defines the tonal midpoint for brightness scaling."
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Localized Brightness",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Localized,
          off: "false",
          on: "true",
          title: "Enhance brightness locally in darker regions."
        }
      ]
    }
  },
  //#endregion
  //#region Clarity
  clarity: {
    controlIds: ImageEditorClarityIds,
    settings: {
      clarity_amount: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Clarity Amount",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.ClarityAmount,
          isMandatory: true,
          max: "1",
          min: "-1",
          step: "0.05",
          title: "Lightroom-style clarity. Negative values soften details, positive values boost local contrast."
        }
      ]
    }
  },
  //#endregion
  //#region Contrast
  contrast: {
    controlIds: ImageEditorContrastIds,
    settings: {
      strength: 0,
      localized: false,
      midpoint: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Contrast Strength",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: "1",
          min: "-1",
          step: "0.05",
          title: "Controls the intensity of the contrast adjustment. 1.0 is no change, below 1 reduces contrast, above 1 increases contrast."
        },
        {
          ariaLabel: "Midpoint",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Midpoint,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Defines the tonal midpoint for contrast scaling."
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Localized Contrast",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Localized,
          off: "false",
          on: "true",
          title: "Apply contrast enhancement locally to edges and textures."
        }
      ]
    }
  },
  //#endregion
  //#region Desaturate
  desaturate: {
    controlIds: ImageEditorDesaturateIds,
    settings: {
      r_channel: 1,
      g_channel: 1,
      b_channel: 1,
      strength: 0
    },
    configs: {
      slider: [
        {
          ariaLabel: "Desaturation strength",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the intensity of the desaturation. 0 is no effect, 1 is fully desaturated."
        },
        {
          ariaLabel: "Red channel level",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.RedChannel,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the intensity of the red channel desaturation relative to the total strength of the filter."
        },
        {
          ariaLabel: "Green channel level",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.GreenChannel,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the intensity of the green channel desaturation relative to the total strength of the filter."
        },
        {
          ariaLabel: "Blue channel level",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.BlueChannel,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the intensity of the blue channel desaturation relative to the total strength of the filter."
        }
      ]
    }
  },
  //#endregion
  //#region Saturation
  saturation: {
    controlIds: ImageEditorSaturationIds,
    settings: {
      intensity: 1
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Saturation Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "5",
          min: "0",
          step: "0.1",
          title: "Controls the intensity of the saturation adjustment. 1.0 is no change, below 1 reduces saturation, above 1 increases saturation."
        }
      ]
    }
  },
  //#endregion
  //#region Unsharp Mask
  unsharpMask: {
    controlIds: ImageEditorUnsharpMaskIds,
    settings: {
      amount: 0.5,
      radius: 5,
      sigma: 1,
      threshold: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Sharpen Amount",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Amount,
          isMandatory: true,
          max: "5",
          min: "0",
          step: "0.05",
          title: "Overall strength applied to the high-frequency detail mask."
        },
        {
          ariaLabel: "Radius",
          controlType: ImageEditorControls.Slider,
          defaultValue: 5,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: "31",
          min: "1",
          step: "2",
          title: "Gaussian blur kernel size (odd numbers give the best results)."
        },
        {
          ariaLabel: "Sigma",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Sigma,
          isMandatory: true,
          max: "5",
          min: "0.1",
          step: "0.1",
          title: "Gaussian blur sigma controlling feather softness around edges."
        },
        {
          ariaLabel: "Threshold",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Threshold,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Skip sharpening for pixels below this normalized contrast level."
        }
      ]
    }
    //#endregion
  }
};
const CREATIVE_EFFECT_SETTINGS = {
  //#region Blend
  blend: {
    controlIds: ImageEditorBlendIds,
    settings: {
      color: "#FF0000",
      opacity: 0.5
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Opacity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Adjust the opacity of the blended layer."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FF0000",
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: "Sets the solid color that will be blended onto the image.",
          type: "color"
        }
      ]
    }
  },
  //#endregion
  //#region Bloom
  bloom: {
    controlIds: ImageEditorBloomIds,
    settings: {
      intensity: 0.6,
      radius: 15,
      threshold: 0.8,
      tint: "#FFFFFF"
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Bloom Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.6,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "2",
          min: "0",
          step: "0.05",
          title: "How strong the bloom reads after compositing. 1.0 = add the blurred highlights at full strength."
        },
        {
          ariaLabel: "Bloom Radius",
          controlType: ImageEditorControls.Slider,
          defaultValue: 15,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: "127",
          min: "3",
          step: "2",
          title: "Blur radius in pixels (odd numbers only). Bigger radius → softer, more cinematic glow."
        },
        {
          ariaLabel: "Threshold",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.8,
          id: ImageEditorSliderIds.Threshold,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Bright-pass cutoff. 0 = everything glows, 1 = nothing glows. For dim scenes start around 0.15-0.35."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Tint Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FFFFFF",
          id: ImageEditorTextfieldIds.Color,
          title: "Hex color for the glow (e.g., FFCCAA). Pure white FFFFFF keeps original hue.",
          type: "color"
        }
      ]
    }
  },
  //#endregion
  //#region Film Grain
  filmGrain: {
    controlIds: ImageEditorFilmGrainIds,
    settings: { intensity: 0, size: 1, soft_blend: false, tint: "#FFFFFF" },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Sets the strength of the filter."
        },
        {
          ariaLabel: "Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: "5",
          min: "0.5",
          step: "0.1",
          title: "Sets the size of the noise's granularity."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Tint",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FFFFFF",
          id: ImageEditorTextfieldIds.Tint,
          isMandatory: true,
          title: "Hexadecimal color (default is FFFFFF for no tint).",
          type: "color"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Soft blend",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.SoftBlend,
          title: "If True, uses a soft blending mode for the grain.",
          off: "false",
          on: "true"
        }
      ]
    }
  },
  //#endregion
  //#region Gaussian Blur
  gaussianBlur: {
    controlIds: ImageEditorGaussianBlurIds,
    settings: {
      blur_kernel_size: 1,
      blur_sigma: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Blur Sigma",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.BlurSigma,
          max: "10",
          min: "0.1",
          step: "0.1",
          title: "Standard deviation for the Gaussian kernel. Controls blur intensity."
        },
        {
          ariaLabel: "Blur Kernel Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 7,
          id: ImageEditorSliderIds.BlurKernelSize,
          max: "51",
          min: "1",
          step: "2",
          title: "Controls the size of the Gaussian blur kernel. Higher values mean more smoothing."
        }
      ]
    }
  },
  //#endregion
  //#region Sepia
  sepia: {
    controlIds: ImageEditorSepiaIds,
    settings: {
      intensity: 0
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Sepia Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Controls the intensity of the sepia effect."
        }
      ]
    }
  },
  //#endregion
  //#region Split Tone
  splitTone: {
    controlIds: ImageEditorSplitToneIds,
    settings: {
      balance: 0.5,
      highlights: "#FFAA55",
      intensity: 0.6,
      shadows: "#0066FF",
      softness: 0.25
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.6,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "2",
          min: "0",
          step: "0.05",
          title: "Strength of the tint applied."
        },
        {
          ariaLabel: "Balance",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Balance,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Luminance pivot. 0 = lift even deep blacks; 1 = tint only the brightest pixels."
        },
        {
          ariaLabel: "Softness",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.25,
          id: ImageEditorSliderIds.Softness,
          isMandatory: true,
          max: "0.5",
          min: "0.01",
          step: "0.01",
          title: "Width of the transition band around the balance value."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Highlights",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FFAA55",
          id: ImageEditorTextfieldIds.Highlights,
          title: "Hex colour applied to highlights (e.g. FFAA55).",
          type: "color"
        },
        {
          ariaLabel: "Shadows",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#0066FF",
          id: ImageEditorTextfieldIds.Shadows,
          title: "Hex colour applied to shadows (e.g. 0066FF).",
          type: "color"
        }
      ]
    }
  },
  //#endregion
  //#region Tilt Shift
  tiltShift: {
    controlIds: ImageEditorTiltShiftIds,
    settings: {
      focus_position: 0.5,
      focus_size: 0.25,
      radius: 25,
      smooth: false,
      vertical: false
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Focus Position",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.FocusPosition,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.01",
          title: "Vertical center of the sharp band (0 = top, 1 = bottom)."
        },
        {
          ariaLabel: "Focus Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.25,
          id: ImageEditorSliderIds.FocusSize,
          isMandatory: true,
          max: "0.9",
          min: "0.05",
          step: "0.01",
          title: "Height of the sharp zone as a fraction of the image."
        },
        {
          ariaLabel: "Blur Radius",
          controlType: ImageEditorControls.Slider,
          defaultValue: 25,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: "151",
          min: "3",
          step: "2",
          title: "Gaussian radius for out-of-focus areas. Higher values mean more blur and less detail."
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Smooth Fall-off Curve",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Smooth,
          off: "linear",
          on: "smooth",
          title: "Fall-off curve of blur vs distance. Linear means a constant fall-off, smooth means a gradual transition."
        },
        {
          ariaLabel: "Vertical Orientation",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Vertical,
          off: "horizontal",
          on: "vertical",
          title: "Direction of the focus band. Horizontal means the focus band is horizontal, vertical means it is vertical."
        }
      ]
    }
  },
  //#endregion
  //#region Vibrance
  vibrance: {
    controlIds: ImageEditorVibranceIds,
    settings: {
      intensity: 0,
      protect_skin: true,
      clip_soft: true
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Vibrance Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "2",
          min: "-1",
          step: "0.05",
          title: "Controls the intensity of the vibrance adjustment. Negative values reduce vibrance, positive values increase it."
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Protect Skin Tones",
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.ProtectSkin,
          off: "false",
          on: "true",
          title: "If true, skin tones are less affected by the vibrance adjustment."
        },
        {
          ariaLabel: "Clip Softly",
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.ClipSoft,
          off: "false",
          on: "true",
          title: "If true, saturation is rolled off near maximum to avoid clipping."
        }
      ]
    }
  },
  //#endregion
  //#region Vignette
  vignette: {
    controlIds: ImageEditorVignetteIds,
    settings: {
      intensity: 0,
      radius: 0,
      shape: false,
      color: "000000"
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Vignette Intensity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the darkness of the vignette effect. Higher values mean darker edges."
        },
        {
          ariaLabel: "Vignette Radius",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: "1",
          min: "0",
          step: "0.05",
          title: "Controls the size of the vignette effect. Lower values mean a smaller vignette."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#000000",
          id: ImageEditorTextfieldIds.Color,
          title: "Sets the color of the vignette.",
          type: "color"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Circular",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Shape,
          off: "elliptical",
          on: "circular",
          title: "Selects the shape of the vignette effect, defaults to elliptical."
        }
      ]
    }
  }
  //#endregion
};
const DIFFUSION_SETTINGS = {
  //#region Inpaint
  inpaint: {
    controlIds: ImageEditorInpaintIds,
    hasCanvasAction: true,
    requiresManualApply: true,
    settings: {
      b64_canvas: "",
      cfg: 7,
      denoise_percentage: 40,
      steps: 16,
      positive_prompt: "",
      negative_prompt: "",
      upsample_target: 1024,
      use_conditioning: true
    },
    configs: {
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Positive prompt",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "",
          id: ImageEditorTextfieldIds.PositivePrompt,
          isMandatory: false,
          title: "Prompt applied to masked pixels.",
          type: "text"
        },
        {
          ariaLabel: "Negative prompt",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "",
          id: ImageEditorTextfieldIds.NegativePrompt,
          isMandatory: false,
          title: "Negative prompt applied to masked pixels.",
          type: "text"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Use conditioning prompts",
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.UseConditioning,
          isMandatory: false,
          off: "false",
          on: "true",
          title: "If enabled, prepend the connected conditioning inputs to the prompts before sampling."
        }
      ],
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Denoise percentage",
          controlType: ImageEditorControls.Slider,
          defaultValue: 40,
          id: ImageEditorSliderIds.DenoisePercentage,
          isMandatory: true,
          max: "100",
          min: "0",
          step: "1",
          title: "Noise applied during inpaint. 0 keeps original pixels, 100 fully regenerates."
        },
        {
          ariaLabel: "CFG scale",
          controlType: ImageEditorControls.Slider,
          defaultValue: 7,
          id: ImageEditorSliderIds.Cfg,
          isMandatory: true,
          max: "30",
          min: "1",
          step: "0.5",
          title: "Classifier-free guidance applied during the inpaint pass."
        },
        {
          ariaLabel: "Steps",
          controlType: ImageEditorControls.Slider,
          defaultValue: 16,
          id: ImageEditorSliderIds.Steps,
          isMandatory: true,
          max: "30",
          min: "1",
          step: "1",
          title: "Diffusion steps used for the inpaint sampler."
        },
        {
          ariaLabel: "Upsample target (px)",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1024,
          id: ImageEditorSliderIds.UpsampleTarget,
          isMandatory: false,
          max: "2048",
          min: "0",
          step: "16",
          title: "Detailer path: upscale ROI longer side to this size before inpaint (0 disables)."
        }
      ]
    }
  }
  //#endregion
};
const INPAINT_ADV = {
  //#region Inpaint (adv.)
  controlIds: ImageEditorInpaintIds,
  hasCanvasAction: true,
  requiresManualApply: true,
  settings: {
    ...DIFFUSION_SETTINGS.inpaint.settings,
    roi_auto: true,
    roi_padding: 32,
    roi_align: 8,
    roi_align_auto: false,
    roi_min_size: 64,
    dilate: 0,
    feather: 0,
    seed: 42
  },
  configs: {
    [ImageEditorControls.Textfield]: [
      {
        ariaLabel: "Positive prompt",
        controlType: ImageEditorControls.Textfield,
        defaultValue: "",
        id: ImageEditorTextfieldIds.PositivePrompt,
        isMandatory: false,
        title: "Prompt applied to masked pixels.",
        type: "text"
      },
      {
        ariaLabel: "Negative prompt",
        controlType: ImageEditorControls.Textfield,
        defaultValue: "",
        id: ImageEditorTextfieldIds.NegativePrompt,
        isMandatory: false,
        title: "Negative prompt applied to masked pixels.",
        type: "text"
      },
      {
        ariaLabel: "Seed",
        controlType: ImageEditorControls.Textfield,
        defaultValue: "",
        id: ImageEditorTextfieldIds.Seed,
        isMandatory: false,
        title: "Optional seed override. Leave blank for a random seed.",
        type: "number"
      }
    ],
    [ImageEditorControls.Slider]: [
      {
        ariaLabel: "Denoise percentage",
        controlType: ImageEditorControls.Slider,
        defaultValue: 40,
        id: ImageEditorSliderIds.DenoisePercentage,
        isMandatory: true,
        max: "100",
        min: "0",
        step: "1",
        title: "Noise applied during inpaint. 0 keeps original pixels, 100 fully regenerates."
      },
      {
        ariaLabel: "CFG scale",
        controlType: ImageEditorControls.Slider,
        defaultValue: 7,
        id: ImageEditorSliderIds.Cfg,
        isMandatory: true,
        max: "30",
        min: "1",
        step: "0.5",
        title: "Classifier-free guidance applied during the inpaint pass."
      },
      {
        ariaLabel: "Steps",
        controlType: ImageEditorControls.Slider,
        defaultValue: 16,
        id: ImageEditorSliderIds.Steps,
        isMandatory: true,
        max: "30",
        min: "1",
        step: "1",
        title: "Diffusion steps used for the inpaint sampler."
      },
      {
        ariaLabel: "Upsample target (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 0,
        id: ImageEditorSliderIds.UpsampleTarget,
        isMandatory: false,
        max: "2048",
        min: "0",
        step: "16",
        title: "Detailer path: upscale ROI longer side to this size before inpaint (0 disables)."
      },
      {
        ariaLabel: "ROI padding (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 32,
        id: ImageEditorSliderIds.RoiPadding,
        isMandatory: false,
        max: "256",
        min: "0",
        step: "1",
        title: "Pixels of padding around the mask bounding box when cropping the ROI."
      },
      {
        ariaLabel: "ROI align multiple",
        controlType: ImageEditorControls.Slider,
        defaultValue: 8,
        id: ImageEditorSliderIds.RoiAlign,
        isMandatory: false,
        max: "64",
        min: "1",
        step: "1",
        title: "Align ROI size/position to this multiple. Keeps latent-friendly dims. Disable auto-align to use."
      },
      {
        ariaLabel: "ROI minimum size (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 64,
        id: ImageEditorSliderIds.RoiMinSize,
        isMandatory: false,
        max: "1024",
        min: "1",
        step: "1",
        title: "Enforce a minimum width/height for the cropped ROI."
      },
      {
        ariaLabel: "Dilate mask (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 0,
        id: ImageEditorSliderIds.Dilate,
        isMandatory: false,
        max: "64",
        min: "0",
        step: "1",
        title: "Expand mask edges before inpaint to avoid seams."
      },
      {
        ariaLabel: "Feather mask (px)",
        controlType: ImageEditorControls.Slider,
        defaultValue: 0,
        id: ImageEditorSliderIds.Feather,
        isMandatory: false,
        max: "64",
        min: "0",
        step: "1",
        title: "Soften mask edges to blend the inpainted region."
      }
    ],
    [ImageEditorControls.Toggle]: [
      {
        ariaLabel: "Use conditioning prompts",
        controlType: ImageEditorControls.Toggle,
        defaultValue: false,
        id: ImageEditorToggleIds.UseConditioning,
        isMandatory: false,
        off: "false",
        on: "true",
        title: "If enabled, prepend the connected conditioning inputs to the prompts before sampling."
      },
      {
        ariaLabel: "Auto ROI crop",
        controlType: ImageEditorControls.Toggle,
        defaultValue: true,
        id: ImageEditorToggleIds.RoiAuto,
        isMandatory: false,
        off: "false",
        on: "true",
        title: "Automatically crop to mask bounding box to speed up inpainting."
      },
      {
        ariaLabel: "Auto-align ROI",
        controlType: ImageEditorControls.Toggle,
        defaultValue: false,
        id: ImageEditorToggleIds.RoiAlignAuto,
        isMandatory: false,
        off: "false",
        on: "true",
        title: "Infer alignment multiple from VAE/model. Disable to set a manual multiple (see slider)."
      }
    ]
  }
  //#endregion
};
const DRAWING_SETTINGS = {
  //#region Brush
  brush: {
    controlIds: ImageEditorBrushIds,
    hasCanvasAction: true,
    settings: { b64_canvas: "", color: "#FF0000", opacity: 1, size: 50 },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 50,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: "500",
          min: "1",
          step: "1",
          title: "Sets the size of the brush."
        },
        {
          ariaLabel: "Opacity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: "1",
          min: "0.05",
          step: "0.05",
          title: "Sets the opacity of the brush."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FF0000",
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: "Sets the color of the brush stroke.",
          type: "color"
        }
      ]
    }
  },
  //#endregion
  //#region Line
  line: {
    controlIds: ImageEditorLineIds,
    hasCanvasAction: true,
    settings: { color: "#FF0000", opacity: 1, points: [], size: 10, smooth: false },
    configs: {
      [ImageEditorControls.Canvas]: [],
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 10,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: "500",
          min: "1",
          step: "1",
          title: "Sets the size of the brush."
        },
        {
          ariaLabel: "Opacity",
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: "1",
          min: "0.05",
          step: "0.05",
          title: "Sets the opacity of the brush."
        }
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: "Color",
          controlType: ImageEditorControls.Textfield,
          defaultValue: "#FF0000",
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: "Sets the color of the brush stroke.",
          type: "color"
        }
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: "Smooth",
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Smooth,
          title: "Draws a smooth line.",
          off: "false",
          on: "true"
        }
      ]
    }
  }
  //#endregion
};
const SETTINGS = {
  ...BASIC_ADJUSTMENT_SETTINGS,
  ...BACKGROUND_SETTINGS,
  ...CREATIVE_EFFECT_SETTINGS,
  ...DRAWING_SETTINGS,
  ...DIFFUSION_SETTINGS
};
const TREE_DATA = {
  nodes: [
    //#region Settings
    {
      description: "Tool configuration.",
      id: "settings",
      icon: "brush",
      value: "Settings",
      children: [
        {
          description: "Brush configuration.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.brush)
            }
          },
          id: "brush",
          value: "Brush"
        }
      ]
    },
    //#endregion
    //#region Diffusion Tools
    {
      description: "Diffusion-based retouching tools.",
      id: "diffusion_tools",
      value: "Diffusion Tools",
      icon: "wand",
      children: [
        {
          description: "Inpaint masked areas using the connected diffusion model.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.inpaint)
            }
          },
          id: "inpaint",
          value: "Inpaint"
        },
        {
          description: "Inpaint with advanced ROI controls.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(INPAINT_ADV)
            }
          },
          id: "inpaint_adv",
          value: "Inpaint (adv.)"
        }
      ]
    },
    //#endregion
    //#region Cutouts
    {
      description: "Background removal and matting tools.",
      id: "cutouts",
      value: "Cutouts",
      icon: "replace",
      children: [
        {
          description: "Remove the background using rembg with optional solid fill.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.backgroundRemover)
            }
          },
          id: "background_remover",
          value: "Background remover"
        }
      ]
    },
    //#endregion
    //#region Basic Adjustments
    {
      description: "Basic adjustments such as sharpening and color tuning.",
      id: "basic_adjustments",
      value: "Basic Adjustments",
      icon: "settings",
      children: [
        {
          description: "Adjusts the brightness.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.brightness)
            }
          },
          id: "brightness",
          value: "Brightness"
        },
        {
          description: "Simulates the Lightroom clarity effect.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.clarity)
            }
          },
          id: "clarity",
          value: "Clarity"
        },
        {
          description: "Sharpens edges using a classic unsharp mask pipeline.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.unsharpMask)
            }
          },
          id: "unsharp_mask",
          value: "Unsharp Mask"
        },
        {
          description: "Adjusts the contrast.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.contrast)
            }
          },
          id: "contrast",
          value: "Contrast"
        },
        {
          description: "Reduces the saturation.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.desaturate)
            }
          },
          id: "desaturate",
          value: "Desaturate"
        },
        {
          description: "Adjusts the saturation.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.saturation)
            }
          },
          id: "saturation",
          value: "Saturation"
        }
      ]
    },
    //#endregion
    //#region Creative Effects
    {
      description: "Artistic filters, such as vignette effect and gaussian blur.",
      id: "creative_effects",
      icon: "palette",
      value: "Creative Effects",
      children: [
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.blend)
            }
          },
          description: "Blends a color layer onto the image.",
          id: "blend",
          value: "Blend"
        },
        {
          description: "Applies a bloom effect.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.bloom)
            }
          },
          id: "bloom",
          value: "Bloom"
        },
        {
          description: "Applies a film grain effect.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.filmGrain)
            }
          },
          id: "film_grain",
          value: "Film grain"
        },
        {
          description: "Blurs the image.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.gaussianBlur)
            }
          },
          id: "gaussian_blur",
          value: "Gaussian blur"
        },
        {
          description: "Draws a line.",
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.line)
            }
          },
          id: "line",
          value: "Line"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.sepia)
            }
          },
          description: "Applies a sepia effect to the image.",
          id: "sepia",
          value: "Sepia"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.splitTone)
            }
          },
          description: "Applies a split tone effect to the image.",
          id: "split_tone",
          value: "Split tone"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.tiltShift)
            }
          },
          description: "Applies a tilt-shift effect to the image.",
          id: "tilt_shift",
          value: "Tilt-shift"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.vibrance)
            }
          },
          description: "Applies a vibrance effect to the image.",
          id: "vibrance",
          value: "Vibrance"
        },
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.vignette)
            }
          },
          description: "Applies a vignetting effect to the image.",
          id: "vignette",
          value: "Vignette"
        }
      ]
    }
    //#endregion
  ]
};
var LfEventName;
(function(LfEventName2) {
  LfEventName2["LfAccordion"] = "lf-accordion-event";
  LfEventName2["LfArticle"] = "lf-article-event";
  LfEventName2["LfButton"] = "lf-button-event";
  LfEventName2["LfCanvas"] = "lf-canvas-event";
  LfEventName2["LfCard"] = "lf-card-event";
  LfEventName2["LfCarousel"] = "lf-carousel-event";
  LfEventName2["LfChat"] = "lf-chat-event";
  LfEventName2["LfChart"] = "lf-chart-event";
  LfEventName2["LfChip"] = "lf-chip-event";
  LfEventName2["LfCode"] = "lf-code-event";
  LfEventName2["LfCompare"] = "lf-compare-event";
  LfEventName2["LfImageviewer"] = "lf-imageviewer-event";
  LfEventName2["LfList"] = "lf-list-event";
  LfEventName2["LfManager"] = "lf-manager-ready";
  LfEventName2["LfMasonry"] = "lf-masonry-event";
  LfEventName2["LfMessenger"] = "lf-messenger-event";
  LfEventName2["LfProgressbar"] = "lf-progressbar-event";
  LfEventName2["LfSlider"] = "lf-slider-event";
  LfEventName2["LfSpinner"] = "lf-spinner-event";
  LfEventName2["LfTabbar"] = "lf-tabbar-event";
  LfEventName2["LfTextfield"] = "lf-textfield-event";
  LfEventName2["LfToggle"] = "lf-toggle-event";
  LfEventName2["LfTree"] = "lf-tree-event";
  LfEventName2["LfUpload"] = "lf-upload-event";
  LfEventName2["Textarea"] = "textarea-event";
})(LfEventName || (LfEventName = {}));
function getPathColumn(dataset) {
  var _a;
  return ((_a = dataset == null ? void 0 : dataset.columns) == null ? void 0 : _a.find((c2) => c2.id === ImageEditorColumnId.Path)) || null;
}
function getStatusColumn(dataset) {
  var _a;
  return ((_a = dataset == null ? void 0 : dataset.columns) == null ? void 0 : _a.find((c2) => c2.id === ImageEditorColumnId.Status)) || null;
}
function parseLabel(data) {
  return data.isMandatory ? `${data.ariaLabel}*` : data.ariaLabel;
}
const refreshValues = async (state, addSnapshot = false) => {
  const { elements, filter } = state;
  const { controls } = elements;
  const lfManager = getLfManager();
  state.settingsStore = state.settingsStore ?? {};
  const storeForFilter = state.settingsStore[state.filterType] = state.settingsStore[state.filterType] ?? {};
  for (const key in controls) {
    if (Object.prototype.hasOwnProperty.call(controls, key)) {
      const id = key;
      const control = controls[id];
      switch (control.tagName) {
        case "LF-SLIDER": {
          const slider = control;
          const sliderValue = await slider.getValue();
          const value = addSnapshot ? sliderValue.real : sliderValue.display;
          filter.settings[id] = value;
          storeForFilter[id] = value;
          break;
        }
        case "LF-TEXTFIELD": {
          const textfield = control;
          const textfieldValue = await textfield.getValue();
          filter.settings[id] = textfieldValue;
          storeForFilter[id] = textfieldValue;
          break;
        }
        case "LF-TOGGLE": {
          const toggle = control;
          const toggleValue = await toggle.getValue();
          const value = toggleValue === "on" ? toggle.dataset.on : toggle.dataset.off;
          filter.settings[id] = value;
          storeForFilter[id] = value;
          break;
        }
        default:
          lfManager.log(`Unhandled control type: ${control.tagName}`, { control }, LogSeverity.Warning);
          continue;
      }
    }
  }
};
const updateCb = async (state, addSnapshot = false, force = false) => {
  await refreshValues(state, addSnapshot);
  const { elements, filter } = state;
  const { imageviewer } = elements;
  if (!filter) {
    return false;
  }
  const { settings } = filter;
  const validValues = isValidObject(settings);
  const isCanvasAction = settings.points || settings.b64_canvas;
  const hasCanvasAction = filter.hasCanvasAction;
  if (validValues && hasCanvasAction) {
    const canvas = (await imageviewer.getComponents()).details.canvas;
    const brushDefaults = {
      ...SETTINGS.brush.settings,
      ...state.lastBrushSettings
    };
    const candidateSettings = settings ?? {};
    const brushSettings = {
      color: candidateSettings.color ?? brushDefaults.color,
      opacity: candidateSettings.opacity ?? brushDefaults.opacity,
      size: candidateSettings.size ?? brushDefaults.size
    };
    canvas.lfColor = brushSettings.color;
    canvas.lfOpacity = brushSettings.opacity;
    canvas.lfSize = brushSettings.size;
    state.lastBrushSettings = {
      ...state.lastBrushSettings,
      color: brushSettings.color,
      opacity: brushSettings.opacity,
      size: brushSettings.size
    };
  }
  const shouldUpdate = validValues && (!hasCanvasAction || isCanvasAction);
  const requiresManualApply = !!(filter == null ? void 0 : filter.requiresManualApply);
  let success = false;
  if (shouldUpdate && (force || !requiresManualApply)) {
    success = await apiCall$2(state, addSnapshot);
  }
  return success;
};
const createPrepSettings = (deps) => {
  const { onSlider, onTextfield, onToggle } = deps;
  return (state, node) => {
    var _a;
    state.elements.controls = {};
    state.filter = unescapeJson(node.cells.lfCode.value).parsedJson;
    const idRaw = node.id || "brush";
    const alias = idRaw === "inpaint_detail" || idRaw === "inpaint_adv" ? "inpaint" : idRaw;
    state.filterType = alias;
    state.manualApply = void 0;
    const dataset = state.elements.imageviewer.lfDataset;
    const defaults = (_a = dataset == null ? void 0 : dataset.defaults) == null ? void 0 : _a[state.filterType];
    if (defaults) {
      applyFilterDefaults(state, defaults);
    }
    state.settingsStore = state.settingsStore ?? {};
    const stored = state.settingsStore[state.filterType] ?? {};
    const mutableSettings = state.filter.settings;
    Object.keys(stored).forEach((id) => {
      const storedValue = stored[id];
      if (typeof storedValue === "undefined") {
        return;
      }
      mutableSettings[id] = storedValue;
    });
    const { elements, filter } = state;
    const { settings } = elements;
    if (!(filter == null ? void 0 : filter.configs)) {
      return;
    }
    settings.innerHTML = "";
    const controlsContainer = document.createElement(TagName.Div);
    controlsContainer.classList.add(ImageEditorCSS.SettingsControls);
    settings.appendChild(controlsContainer);
    const controlGroups = Object.keys(filter.configs);
    controlGroups.forEach((controlType) => {
      const configs = filter.configs[controlType];
      if (!configs) {
        return;
      }
      configs.forEach((config2) => {
        switch (controlType) {
          case ImageEditorControls.Slider: {
            const sliderConfig = config2;
            const slider = document.createElement(TagName.LfSlider);
            slider.lfLabel = parseLabel(sliderConfig);
            slider.lfLeadingLabel = true;
            slider.lfMax = Number(sliderConfig.max);
            slider.lfMin = Number(sliderConfig.min);
            slider.lfStep = Number(sliderConfig.step);
            slider.lfStyle = ".form-field { width: 100%; }";
            slider.lfValue = Number(sliderConfig.defaultValue);
            slider.title = sliderConfig.title;
            slider.dataset.id = sliderConfig.id;
            slider.addEventListener(LfEventName.LfSlider, (event) => onSlider(state, event));
            const storedValue = stored[sliderConfig.id];
            if (typeof storedValue !== "undefined") {
              slider.lfValue = Number(storedValue);
            }
            controlsContainer.appendChild(slider);
            state.elements.controls[sliderConfig.id] = slider;
            break;
          }
          case ImageEditorControls.Textfield: {
            const textfieldConfig = config2;
            const textfield = document.createElement(TagName.LfTextfield);
            textfield.lfLabel = parseLabel(textfieldConfig);
            textfield.lfHtmlAttributes = { type: textfieldConfig.type };
            textfield.lfValue = String(textfieldConfig.defaultValue).valueOf();
            textfield.title = textfieldConfig.title;
            textfield.dataset.id = textfieldConfig.id;
            textfield.addEventListener(LfEventName.LfTextfield, (event) => onTextfield(state, event));
            const storedValue = stored[textfieldConfig.id];
            if (typeof storedValue !== "undefined") {
              textfield.lfValue = String(storedValue);
            }
            controlsContainer.appendChild(textfield);
            state.elements.controls[textfieldConfig.id] = textfield;
            break;
          }
          case ImageEditorControls.Toggle: {
            const toggleConfig = config2;
            const toggle = document.createElement(TagName.LfToggle);
            toggle.dataset.off = toggleConfig.off;
            toggle.dataset.on = toggleConfig.on;
            toggle.lfLabel = parseLabel(toggleConfig);
            toggle.lfValue = toggleConfig.defaultValue ?? false;
            toggle.title = toggleConfig.title;
            toggle.dataset.id = toggleConfig.id;
            toggle.addEventListener(LfEventName.LfToggle, (event) => onToggle(state, event));
            const storedValue = stored[toggleConfig.id];
            if (typeof storedValue !== "undefined") {
              const boolValue = storedValue === true || typeof storedValue === "string" && storedValue.toLowerCase() === "true";
              toggle.lfValue = boolValue;
            }
            controlsContainer.appendChild(toggle);
            state.elements.controls[toggleConfig.id] = toggle;
            break;
          }
          default:
            throw new Error(`Unknown control type: ${controlType}`);
        }
      });
    });
    const buttonsWrapper = document.createElement(TagName.Div);
    buttonsWrapper.classList.add(ImageEditorCSS.SettingsButtons);
    settings.appendChild(buttonsWrapper);
    const resetButton = document.createElement(TagName.LfButton);
    resetButton.lfIcon = ImageEditorIcons.Reset;
    resetButton.lfLabel = "Reset";
    resetButton.lfStretchX = true;
    resetButton.addEventListener("click", () => {
      void (async () => {
        await resetSettings(settings);
        registerManualApplyChange(state);
      })();
    });
    buttonsWrapper.appendChild(resetButton);
    if (state.filterType === "brush") {
      const brushSettings = state.filter.settings ?? {};
      state.lastBrushSettings = {
        ...state.lastBrushSettings,
        ...JSON.parse(JSON.stringify(brushSettings))
      };
    }
    if (filter == null ? void 0 : filter.hasCanvasAction) {
      requestAnimationFrame(async () => {
        const canvas = (await state.elements.imageviewer.getComponents()).details.canvas;
        const brushSource = {
          ...SETTINGS.brush.settings,
          ...state.lastBrushSettings,
          ...state.filter.settings ?? {}
        };
        if (brushSource.color) {
          canvas.lfColor = brushSource.color;
        }
        if (typeof brushSource.opacity === "number") {
          canvas.lfOpacity = brushSource.opacity;
        }
        if (typeof brushSource.size === "number") {
          canvas.lfSize = brushSource.size;
        }
      });
    }
    if (filter == null ? void 0 : filter.requiresManualApply) {
      const applyButton = document.createElement(TagName.LfButton);
      applyButton.lfIcon = ImageEditorIcons.Resume;
      applyButton.lfLabel = "Apply";
      applyButton.lfStretchX = true;
      initManualApplyState(state, applyButton);
      applyButton.addEventListener("click", () => {
        if (!state.manualApply || state.manualApply.isProcessing) {
          return;
        }
        const hasPending = hasManualApplyPendingChanges(state);
        if (!hasPending) {
          return;
        }
        beginManualApplyRequest(state);
        void updateCb(state, true, true);
      });
      buttonsWrapper.appendChild(applyButton);
    }
  };
};
async function resetSettings(settings) {
  const controls = Array.from(settings.querySelectorAll("[data-id]"));
  for (const control of controls) {
    switch (control.tagName) {
      case "LF-SLIDER": {
        const slider = control;
        await slider.setValue(slider.lfValue);
        await slider.refresh();
        break;
      }
      case "LF-TEXTFIELD": {
        const textfield = control;
        await textfield.setValue(textfield.lfValue);
        break;
      }
      case "LF-TOGGLE": {
        const toggle = control;
        toggle.setValue(toggle.lfValue ? "on" : "off");
        break;
      }
    }
  }
}
const setBrush = async (canvas, lastBrushSettings) => {
  if (canvas) {
    const { color, opacity, size } = lastBrushSettings;
    canvas.lfColor = color;
    canvas.lfOpacity = opacity;
    canvas.lfSize = size;
  }
};
const applyFilterDefaults = (state, defaults) => {
  const { filter } = state;
  if (!filter) {
    return;
  }
  const mutableSettings = filter.settings;
  Object.keys(filter.configs).forEach((controlType) => {
    const configs = filter.configs[controlType];
    configs == null ? void 0 : configs.forEach((config2) => {
      const defaultValue = defaults[config2.id];
      if (typeof defaultValue === "undefined") {
        return;
      }
      switch (controlType) {
        case ImageEditorControls.Slider: {
          const sliderConfig = config2;
          const numericValue = typeof defaultValue === "number" ? defaultValue : Number(defaultValue);
          sliderConfig.defaultValue = numericValue;
          mutableSettings[sliderConfig.id] = numericValue;
          break;
        }
        case ImageEditorControls.Textfield: {
          const textfieldConfig = config2;
          const stringValue = defaultValue === null || typeof defaultValue === "undefined" ? "" : String(defaultValue);
          textfieldConfig.defaultValue = stringValue;
          mutableSettings[textfieldConfig.id] = stringValue;
          break;
        }
        case ImageEditorControls.Toggle: {
          const toggleConfig = config2;
          const boolValue = defaultValue === true || typeof defaultValue === "string" && defaultValue.toLowerCase() === "true";
          toggleConfig.defaultValue = boolValue;
          mutableSettings[toggleConfig.id] = boolValue ? toggleConfig.on : toggleConfig.off;
          break;
        }
      }
    });
  });
};
const createEventHandlers = ({ handleInterruptForState: handleInterruptForState2, prepSettings: prepSettings2 }) => {
  const syncSelectionWithDataset = async (state, masonryEvent) => {
    const { elements } = state;
    const dataset = elements.imageviewer.lfDataset || {};
    const effectiveContextId = ensureDatasetContext(dataset, state);
    const previousSelection = dataset.selection;
    const previousContextId = dataset.context_id ?? effectiveContextId;
    const { comp, selectedShape: rawSelectedShape } = masonryEvent.detail;
    const masonryComp = comp;
    let selectedShape = rawSelectedShape;
    if ((!selectedShape || typeof selectedShape.index !== "number") && (masonryComp == null ? void 0 : masonryComp.getSelectedShape)) {
      try {
        selectedShape = await masonryComp.getSelectedShape();
      } catch (error2) {
        getLfManager().log("Failed to resolve masonry selection.", { error: error2 }, LogSeverity.Warning);
      }
    }
    const nodes = Array.isArray(dataset == null ? void 0 : dataset.nodes) ? dataset.nodes : [];
    const selectionIndex = resolveSelectionIndex(selectedShape, nodes);
    if (typeof selectionIndex !== "number") {
      getLfManager().log("Unable to resolve selected masonry index.", { selectedShape }, LogSeverity.Warning);
      return;
    }
    const { selection, contextId } = buildSelectionPayload({
      dataset,
      index: selectionIndex,
      nodes,
      selectedShape,
      fallbackContextId: previousContextId ?? state.contextId
    });
    const resolvedContextId = selection.context_id ?? contextId ?? previousContextId ?? state.contextId;
    if (resolvedContextId) {
      state.contextId = resolvedContextId;
      if (!selection.context_id) {
        selection.context_id = resolvedContextId;
      }
    }
    const nextDataset = applySelectionColumn({
      ...dataset,
      context_id: dataset.context_id ?? resolvedContextId
    }, selection);
    if (resolvedContextId && nextDataset.selection) {
      nextDataset.selection.context_id = resolvedContextId;
    }
    elements.imageviewer.lfDataset = nextDataset;
    if (!resolvedContextId) {
      return;
    }
    if (!hasSelectionChanged(previousSelection, nextDataset.selection) && !hasContextChanged(previousContextId, nextDataset.context_id)) {
      return;
    }
    getApiRoutes().json.update(resolvedContextId, nextDataset).catch((error2) => getLfManager().log("Failed to persist image selection.", { error: error2, contextId: resolvedContextId }, LogSeverity.Warning));
  };
  const handlers = {
    //#region Button
    button: async (state, e2) => {
      var _a;
      const { comp, eventType } = e2.detail;
      if (eventType === "click") {
        const isPatched = ((_a = api) == null ? void 0 : _a[LFInterruptFlags.PatchedInterrupt]) === true;
        switch (comp.lfIcon) {
          case ImageEditorIcons.Interrupt:
            getApiRoutes().comfy.interrupt();
            if (!isPatched) {
              await handleInterruptForState2(state);
            }
            break;
          case ImageEditorIcons.Resume:
            await handleInterruptForState2(state);
            break;
        }
      }
    },
    //#endregion
    //#region Canvas
    canvas: async (state, e2) => {
      const { comp, eventType, points } = e2.detail;
      const { filter, filterType } = state;
      switch (eventType) {
        case "stroke":
          const originalFilter = filter;
          const originalFilterType = filterType;
          const canvas = await comp.getCanvas();
          const b64Canvas = canvasToBase64(canvas);
          if (filterType !== "brush" && !(filter == null ? void 0 : filter.hasCanvasAction)) {
            state.filterType = "brush";
          }
          const brushDefaults = {
            ...SETTINGS.brush.settings,
            ...state.lastBrushSettings
          };
          const temporaryFilter = {
            ...JSON.parse(JSON.stringify(SETTINGS.brush)),
            settings: {
              ...brushDefaults,
              b64_canvas: b64Canvas,
              color: comp.lfColor ?? brushDefaults.color,
              opacity: comp.lfOpacity ?? brushDefaults.opacity,
              points,
              size: comp.lfSize ?? brushDefaults.size
            }
          };
          state.filter = temporaryFilter;
          try {
            await updateCb(state, true, true);
          } finally {
            if (originalFilter == null ? void 0 : originalFilter.hasCanvasAction) {
              const existingSettings = originalFilter.settings ?? {};
              originalFilter.settings = {
                ...existingSettings,
                b64_canvas: b64Canvas
              };
            }
            state.filter = originalFilter;
            state.filterType = originalFilterType;
            await comp.clearCanvas();
          }
          break;
      }
    },
    //#endregion
    //#region Imageviewer
    imageviewer: async (state, e2) => {
      var _a;
      const { comp, eventType, originalEvent } = e2.detail;
      const { node } = state;
      switch (eventType) {
        case "lf-event": {
          const ogEv = originalEvent;
          if (isTree(ogEv.detail.comp)) {
            const treeEvent = ogEv;
            const { id, node: treeNode, eventType: eventType2 } = treeEvent.detail;
            switch (id) {
              case "details-tree":
                if (((_a = treeNode == null ? void 0 : treeNode.cells) == null ? void 0 : _a.lfCode) && eventType2 === "click") {
                  prepSettings2(state, treeNode);
                }
                break;
              case "navigation-tree":
                if (!state.navigationManager || !treeNode || eventType2 !== "click") {
                  break;
                }
                await state.navigationManager.handleTreeClick(treeNode);
                const needsLazyLoad = !treeNode.children || treeNode.children.length === 0;
                if (needsLazyLoad) {
                  await state.navigationManager.expandNode(treeNode);
                }
                break;
            }
          }
          switch (ogEv.detail.eventType) {
            case "lf-event":
              const masonryEvent = ogEv;
              const isMasonryEvent = isMasonry(ogEv.detail.comp);
              if (isMasonryEvent) {
                const { selectedShape } = masonryEvent.detail;
                switch (masonryEvent.detail.eventType) {
                  case "lf-event":
                    const subOgEv = masonryEvent.detail.originalEvent;
                    const isImageEvent = isImage(subOgEv.detail.comp);
                    if (isImageEvent) {
                      switch (subOgEv.detail.eventType) {
                        case "click":
                          if (!selectedShape) {
                            getLfManager().log("Masonry selection cleared.", { selectedShape }, LogSeverity.Info);
                            return;
                          }
                          await syncSelectionWithDataset(state, masonryEvent);
                          break;
                      }
                    }
                }
                break;
              }
              break;
            case "ready":
              const c2 = ogEv.detail.comp;
              const isCanvas = c2.rootElement.tagName.toLowerCase() === "lf-canvas";
              if (isCanvas) {
                setBrush(c2, SETTINGS.brush.settings);
              }
              break;
            case "stroke": {
              const canvasEv = ogEv;
              await handlers.canvas(state, canvasEv);
              break;
            }
          }
          break;
        }
        case "ready": {
          const { navigation } = await comp.getComponents();
          switch (node.comfyClass) {
            case NodeName.imagesEditingBreakpoint:
              navigation.load.lfLabel = "";
              navigation.load.lfUiState = "disabled";
              navigation.textfield.lfLabel = "Previews are visible in your ComfyUI/temp folder";
              navigation.textfield.lfUiState = "disabled";
              break;
            default:
              navigation.textfield.lfLabel = "Directory (relative to ComfyUI/input)";
              break;
          }
          break;
        }
      }
    },
    //#endregion
    //#region Slider
    slider: async (state, e2) => {
      const { eventType } = e2.detail;
      const { update } = state;
      const { preview, snapshot } = update;
      switch (eventType) {
        case "change":
          registerManualApplyChange(state);
          snapshot();
          break;
        case "input":
          registerManualApplyChange(state);
          const debouncedSlider = debounce(preview, 300);
          debouncedSlider();
          break;
      }
    },
    //#endregion
    //#region Textfield
    textfield: async (state, e2) => {
      const { eventType } = e2.detail;
      const { update } = state;
      const { preview, snapshot } = update;
      switch (eventType) {
        case "change":
          registerManualApplyChange(state);
          snapshot();
          break;
        case "input":
          registerManualApplyChange(state);
          const debouncedTextfield = debounce(preview, 300);
          debouncedTextfield();
          break;
      }
    },
    //#endregion
    //#region Toggle
    toggle: async (state, e2) => {
      const { eventType } = e2.detail;
      const { update } = state;
      const { snapshot } = update;
      switch (eventType) {
        case "change":
          registerManualApplyChange(state);
          snapshot();
          break;
      }
    }
    //#endregion
  };
  return handlers;
};
function setGridStatus(status, grid, actionButtons) {
  const { interrupt, resume } = actionButtons;
  switch (status) {
    case ImageEditorStatus.Completed:
      requestAnimationFrame(() => {
        if (interrupt) {
          interrupt.lfUiState = "disabled";
        }
        if (resume) {
          resume.lfUiState = "disabled";
        }
      });
      grid == null ? void 0 : grid.classList.add(ImageEditorCSS.GridIsInactive);
      break;
    case ImageEditorStatus.Pending:
      requestAnimationFrame(() => {
        if (interrupt) {
          interrupt.lfUiState = "danger";
        }
        if (resume) {
          resume.lfUiState = "success";
        }
      });
      grid == null ? void 0 : grid.classList.remove(ImageEditorCSS.GridIsInactive);
      break;
  }
}
const handleInterruptForState = async (state) => {
  var _a, _b;
  const lfManager = getLfManager();
  const { actionButtons, grid, imageviewer } = state.elements;
  const dataset = imageviewer.lfDataset;
  const statusColumn = getStatusColumn(dataset);
  const pathColumn = getPathColumn(dataset);
  const parsedPath = pathColumn ? unescapeJson(pathColumn).parsedJson : void 0;
  const path = typeof (parsedPath == null ? void 0 : parsedPath.title) === "string" ? parsedPath.title : null;
  if ((statusColumn == null ? void 0 : statusColumn.title) === ImageEditorStatus.Pending) {
    statusColumn.title = ImageEditorStatus.Completed;
    if (dataset && path) {
      try {
        await getApiRoutes().json.update(path, dataset);
      } catch (error2) {
        lfManager.log("Failed to update JSON after workflow interrupt.", { error: error2, path }, LogSeverity.Warning);
      }
    }
    if ((actionButtons == null ? void 0 : actionButtons.interrupt) && (actionButtons == null ? void 0 : actionButtons.resume)) {
      setGridStatus(ImageEditorStatus.Completed, grid, actionButtons);
    } else {
      grid == null ? void 0 : grid.classList.add(ImageEditorCSS.GridIsInactive);
    }
    try {
      const components = await imageviewer.getComponents();
      const navigation = components == null ? void 0 : components.navigation;
      await imageviewer.reset();
      await ((_b = (_a = navigation == null ? void 0 : navigation.masonry) == null ? void 0 : _a.setSelectedShape) == null ? void 0 : _b.call(_a, null));
    } catch (error2) {
      lfManager.log("Failed to reset image viewer after workflow interrupt.", { error: error2 }, LogSeverity.Warning);
    }
  }
  await resetSettings(imageviewer);
};
const handlerRefs = {
  slider: async () => {
    throw new Error("Image editor slider handler not initialized.");
  },
  textfield: async () => {
    throw new Error("Image editor textfield handler not initialized.");
  },
  toggle: async () => {
    throw new Error("Image editor toggle handler not initialized.");
  }
};
const prepSettings = createPrepSettings({
  onSlider: (state, event) => handlerRefs.slider(state, event),
  onTextfield: (state, event) => handlerRefs.textfield(state, event),
  onToggle: (state, event) => handlerRefs.toggle(state, event)
});
const EV_HANDLERS$a = createEventHandlers({
  handleInterruptForState,
  prepSettings
});
handlerRefs.slider = EV_HANDLERS$a.slider;
handlerRefs.textfield = EV_HANDLERS$a.textfield;
handlerRefs.toggle = EV_HANDLERS$a.toggle;
const syncNavigationDirectoryControl = async (state, directoryValue) => {
  const { imageviewer } = state.elements;
  const { navigation } = await imageviewer.getComponents();
  const { textfield } = navigation;
  const current = await textfield.getValue();
  const target = normalizeDirectoryRequest(directoryValue);
  if ((current ?? "") === target) {
    return;
  }
  try {
    state.isSyncingDirectory = true;
    await textfield.setValue(target);
  } catch (error2) {
    getLfManager().log("Failed to synchronize directory input.", { error: error2 }, LogSeverity.Warning);
  } finally {
    state.isSyncingDirectory = false;
  }
};
const extractMetadata = (node) => {
  const lfData = getLfData();
  const metadata = lfData.node.extractCellMetadata(node, "lfCode", {
    validate: (val) => {
      if (typeof val === "string") {
        try {
          val = JSON.parse(val);
        } catch {
          return false;
        }
      }
      if (typeof val !== "object" || val === null) {
        return false;
      }
      return "id" in val || "name" in val || "paths" in val;
    },
    transform: (val) => {
      let parsed = val;
      if (typeof val === "string") {
        try {
          parsed = JSON.parse(val);
        } catch {
          parsed = val;
        }
      }
      return {
        id: parsed.id ?? String(node.id ?? ""),
        name: parsed.name ?? String(node.value ?? ""),
        hasChildren: Boolean(parsed.hasChildren),
        paths: parsed.paths ?? {},
        isRoot: parsed.isRoot
      };
    }
  });
  return metadata ?? null;
};
const createNavigationTreeManager = (imageviewer, editorState) => {
  const _getDirectoryPath = (metadata) => {
    return metadata.paths.resolved ?? metadata.paths.raw ?? metadata.paths.relative ?? metadata.name ?? "";
  };
  const loadRoots = async () => {
    var _a;
    try {
      const response = await IMAGE_API.explore("", { scope: "roots" });
      if (response.status === LogSeverity.Success && ((_a = response.data) == null ? void 0 : _a.tree)) {
        imageviewer.lfNavigation = {
          isTreeOpen: false,
          treeProps: {
            lfAccordionLayout: true,
            lfDataset: response.data.tree ?? { columns: [], nodes: [] },
            lfFilter: true,
            lfGrid: true,
            lfSelectable: true
          }
        };
      }
    } catch (error2) {
      getLfManager().log("Failed to load navigation roots.", { error: error2 }, LogSeverity.Warning);
    }
  };
  const expandNode = async (node) => {
    var _a, _b, _c;
    const metadata = extractMetadata(node);
    if (!(metadata == null ? void 0 : metadata.hasChildren)) {
      return;
    }
    const nodeId = metadata.id;
    const path = normalizeDirectoryRequest(_getDirectoryPath(metadata));
    if (!path) {
      return;
    }
    try {
      const response = await IMAGE_API.explore(path, { scope: "tree", nodePath: path });
      if (response.status === LogSeverity.Success && ((_a = response.data) == null ? void 0 : _a.tree)) {
        const { navigation } = await imageviewer.getComponents();
        const branch = response.data.tree;
        if (!Array.isArray(branch.nodes)) {
          return;
        }
        const currentDataset = (_c = (_b = imageviewer.lfNavigation) == null ? void 0 : _b.treeProps) == null ? void 0 : _c.lfDataset;
        if (!currentDataset) {
          return;
        }
        const lfData = getLfData();
        if (!lfData) {
          return;
        }
        const parentNode = lfData.node.find(currentDataset, (n2) => n2.id === nodeId);
        if (!parentNode) {
          return;
        }
        parentNode.children = branch.nodes;
        const parentId = parentNode.id;
        navigation.tree.lfExpandedNodeIds = Array.isArray(navigation.tree.lfExpandedNodeIds) && !navigation.tree.lfExpandedNodeIds.includes(parentId) ? [...navigation.tree.lfExpandedNodeIds, parentId] : [parentId];
      }
    } catch (error2) {
      getLfManager().log("Failed to expand node.", { error: error2, nodeId, path }, LogSeverity.Warning);
    }
  };
  const handleTreeClick = async (node) => {
    var _a;
    const metadata = extractMetadata(node);
    if (!metadata) {
      return;
    }
    const targetPath = normalizeDirectoryRequest(_getDirectoryPath(metadata));
    const currentPath = normalizeDirectoryRequest(editorState.directoryValue ?? deriveDirectoryValue(editorState.directory) ?? "");
    if (targetPath === currentPath && !metadata.isRoot) {
      return;
    }
    await ((_a = editorState.refreshDirectory) == null ? void 0 : _a.call(editorState, targetPath));
  };
  return {
    loadRoots,
    expandNode,
    handleTreeClick
  };
};
const IMAGE_EDITOR_INSTANCES = /* @__PURE__ */ new Set();
const STATE$h = /* @__PURE__ */ new WeakMap();
const imageEditorFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$h.get(wrapper),
      getValue: () => {
        const { imageviewer } = STATE$h.get(wrapper).elements;
        return imageviewer.lfDataset || {};
      },
      setValue: (value) => {
        const state = STATE$h.get(wrapper);
        const { actionButtons, grid, imageviewer } = state.elements;
        const callback = (_2, u2) => {
          var _a, _b;
          const parsedValue = u2.parsedJson;
          const isPending = ((_a = getStatusColumn(parsedValue)) == null ? void 0 : _a.title) === ImageEditorStatus.Pending;
          if (isPending) {
            setGridStatus(ImageEditorStatus.Pending, grid, actionButtons);
          }
          const dataset = parsedValue || {};
          ensureDatasetContext(dataset, state);
          const navigationDirectory = getNavigationDirectory(dataset);
          if (navigationDirectory) {
            state.directory = { ...navigationDirectory };
          }
          const derivedDirectoryValue = deriveDirectoryValue(navigationDirectory);
          if (derivedDirectoryValue !== void 0) {
            state.directoryValue = derivedDirectoryValue;
          }
          imageviewer.lfDataset = dataset;
          imageviewer.getComponents().then(({ details }) => {
            const { canvas } = details;
            if (canvas) {
              setBrush(canvas, STATE$h.get(wrapper).lastBrushSettings);
            }
          }).catch((error2) => getLfManager().log("Failed to prepare image editor canvas.", { error: error2 }, LogSeverity.Warning));
          void syncNavigationDirectoryControl(state, state.directoryValue);
          const shouldAutoLoad = !state.hasAutoDirectoryLoad && (!Array.isArray(dataset == null ? void 0 : dataset.nodes) || dataset.nodes.length === 0);
          if (shouldAutoLoad) {
            state.hasAutoDirectoryLoad = true;
            (_b = state.refreshDirectory) == null ? void 0 : _b.call(state, normalizeDirectoryRequest(state.directoryValue));
          }
        };
        normalizeValue(value, callback, CustomWidgetName.imageEditor);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const settings = document.createElement(TagName.Div);
    const imageviewer = document.createElement(TagName.LfImageviewer);
    const navigationTreeEnabled = node.comfyClass === NodeName.loadAndEditImages;
    let navigationManager = null;
    const refresh = async (directory) => {
      const state2 = STATE$h.get(wrapper);
      const normalizedDirectory = normalizeDirectoryRequest(directory);
      if (!state2) {
        return;
      }
      state2.hasAutoDirectoryLoad = true;
      state2.lastRequestedDirectory = normalizedDirectory;
      try {
        const response = navigationTreeEnabled ? await IMAGE_API.explore(normalizedDirectory, { scope: "dataset" }) : await IMAGE_API.get(normalizedDirectory);
        if (response.status !== LogSeverity.Success) {
          getLfManager().log("Images not found.", { response }, LogSeverity.Info);
          return;
        }
        const rawData = response.data;
        const dataset = (navigationTreeEnabled ? rawData == null ? void 0 : rawData.dataset : rawData) ?? { nodes: [] };
        const mergedDirectory = mergeNavigationDirectory(dataset, { raw: normalizedDirectory });
        state2.directory = { ...mergedDirectory };
        const derivedDirectoryValue = deriveDirectoryValue(mergedDirectory);
        state2.directoryValue = derivedDirectoryValue ?? normalizedDirectory;
        state2.lastRequestedDirectory = state2.directoryValue;
        ensureDatasetContext(dataset, state2);
        imageviewer.lfDataset = dataset;
        await syncNavigationDirectoryControl(state2, state2.directoryValue);
      } catch (error2) {
        getLfManager().log("Failed to refresh image directory.", { error: error2, directory: normalizedDirectory }, LogSeverity.Warning);
      }
    };
    settings.classList.add(ImageEditorCSS.Settings);
    settings.slot = "settings";
    imageviewer.classList.add(ImageEditorCSS.Widget);
    imageviewer.lfLoadCallback = async (_2, value) => {
      const state2 = STATE$h.get(wrapper);
      if (!state2 || state2.isSyncingDirectory) {
        return;
      }
      const directoryValue = normalizeDirectoryRequest(value);
      if (state2.lastRequestedDirectory === directoryValue && state2.directoryValue === directoryValue) {
        getLfManager().log("lfLoadCallback: directory unchanged, skipping", {}, LogSeverity.Info);
        return;
      }
      await refresh(directoryValue);
    };
    imageviewer.lfValue = TREE_DATA;
    imageviewer.addEventListener(LfEventName.LfImageviewer, (e2) => EV_HANDLERS$a.imageviewer(STATE$h.get(wrapper), e2));
    imageviewer.appendChild(settings);
    const actionButtons = {};
    const state = {
      contextId: void 0,
      elements: { actionButtons, controls: {}, grid, imageviewer, settings },
      directory: void 0,
      directoryValue: void 0,
      filter: null,
      filterType: null,
      hasAutoDirectoryLoad: false,
      isSyncingDirectory: false,
      lastBrushSettings: JSON.parse(JSON.stringify(SETTINGS.brush.settings)),
      lastRequestedDirectory: void 0,
      node,
      refreshDirectory: refresh,
      update: {
        preview: () => updateCb(STATE$h.get(wrapper)).then(() => {
        }),
        snapshot: () => updateCb(STATE$h.get(wrapper), true).then(() => {
        })
      },
      wrapper
    };
    switch (node.comfyClass) {
      case NodeName.imagesEditingBreakpoint:
        const actions = document.createElement(TagName.Div);
        const interrupt = document.createElement(TagName.LfButton);
        const resume = document.createElement(TagName.LfButton);
        interrupt.lfIcon = ImageEditorIcons.Interrupt;
        interrupt.lfLabel = "Interrupt workflow";
        interrupt.lfStretchX = true;
        interrupt.lfUiState = "danger";
        interrupt.title = "Click to interrupt the workflow.";
        interrupt.addEventListener(LfEventName.LfButton, (e2) => EV_HANDLERS$a.button(STATE$h.get(wrapper), e2));
        resume.lfIcon = ImageEditorIcons.Resume;
        resume.lfLabel = "Resume workflow";
        resume.lfStretchX = true;
        resume.lfStyling = "flat";
        resume.lfUiState = "success";
        resume.title = "Click to resume the workflow. Remember to save your snapshots after editing the images!";
        resume.addEventListener(LfEventName.LfButton, (e2) => EV_HANDLERS$a.button(STATE$h.get(wrapper), e2));
        actions.classList.add(ImageEditorCSS.Actions);
        actions.appendChild(interrupt);
        actions.appendChild(resume);
        grid.classList.add(ImageEditorCSS.GridIsInactive);
        grid.classList.add(ImageEditorCSS.GridHasActions);
        grid.appendChild(actions);
        actionButtons.interrupt = interrupt;
        actionButtons.resume = resume;
        setGridStatus(ImageEditorStatus.Completed, grid, actionButtons);
    }
    grid.classList.add(ImageEditorCSS.Grid);
    grid.appendChild(imageviewer);
    content.classList.add(ImageEditorCSS.Content);
    content.appendChild(grid);
    wrapper.appendChild(content);
    const options = imageEditorFactory.options(wrapper);
    STATE$h.set(wrapper, state);
    IMAGE_EDITOR_INSTANCES.add(state);
    if (navigationTreeEnabled) {
      navigationManager = createNavigationTreeManager(imageviewer, state);
      state.navigationManager = navigationManager;
    }
    void Promise.resolve().then(async () => {
      var _a, _b;
      const currentState = STATE$h.get(wrapper);
      if (!currentState) {
        return;
      }
      if (navigationTreeEnabled && navigationManager) {
        await navigationManager.loadRoots();
      }
      if (currentState.hasAutoDirectoryLoad) {
        return;
      }
      const currentDataset = (_a = currentState.elements.imageviewer) == null ? void 0 : _a.lfDataset;
      const hasNodes = Array.isArray(currentDataset == null ? void 0 : currentDataset.nodes) && currentDataset.nodes.length > 0;
      const hasDirectoryValue = Boolean(currentState.directoryValue);
      if (hasNodes || hasDirectoryValue) {
        return;
      }
      (_b = currentState.refreshDirectory) == null ? void 0 : _b.call(currentState, "");
    });
    return { widget: createDOMWidget(CustomWidgetName.imageEditor, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$h
  //#endregion
};
function installLFInterruptHook(apiObj, opts = {}) {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {
  });
  if (!isInterruptHookAPI(apiObj)) {
    logger('"api" object not available; cannot install interrupt hook yet', {}, LogSeverity.Warning);
    return { interruptHook: false };
  }
  const scopedApi = apiObj;
  const wrap = opts.interruptWrapper;
  const makePatched = (fn) => {
    const factory = wrap ?? ((original) => async function patched2(...args) {
      if (scopedApi[LFInterruptFlags.InBeforeInterrupt] === true) {
        return original.apply(this ?? scopedApi, args);
      }
      scopedApi[LFInterruptFlags.InBeforeInterrupt] = true;
      try {
        const result = await original.apply(this ?? scopedApi, args);
        for (const state of IMAGE_EDITOR_INSTANCES) {
          try {
            await handleInterruptForState(state);
          } catch (error2) {
            logger("LF interrupt hook failed while applying image editor cleanup.", { error: error2 }, LogSeverity.Warning);
          }
        }
        return result;
      } finally {
        scopedApi[LFInterruptFlags.InBeforeInterrupt] = false;
      }
    });
    return factory(fn);
  };
  const installInterrupt = () => {
    try {
      if (scopedApi[LFInterruptFlags.PatchedInterrupt] === true) {
        return true;
      }
      const current = scopedApi.interrupt;
      if (typeof current === "function") {
        scopedApi[LFInterruptFlags.OriginalInterruptRef] = current;
        scopedApi.interrupt = makePatched(current);
        scopedApi[LFInterruptFlags.PatchedInterrupt] = true;
        return true;
      }
      const descriptor = Object.getOwnPropertyDescriptor(scopedApi, "interrupt");
      if (!descriptor || descriptor.configurable) {
        let original;
        Object.defineProperty(scopedApi, "interrupt", {
          configurable: true,
          enumerable: true,
          get() {
            return scopedApi[LFInterruptFlags.PatchedInterrupt] ? original : scopedApi[LFInterruptFlags.OriginalInterruptRef] ?? original;
          },
          set(fn) {
            if (typeof fn !== "function") {
              original = fn;
              return;
            }
            scopedApi[LFInterruptFlags.OriginalInterruptRef] = fn;
            original = makePatched(fn);
            scopedApi[LFInterruptFlags.PatchedInterrupt] = true;
          }
        });
      }
      return false;
    } catch (error2) {
      logger("Failed to patch api.interrupt; proceeding without LF interrupt hook", { error: error2 }, LogSeverity.Warning);
      return false;
    }
  };
  let patched = installInterrupt();
  if (!patched) {
    let count = 0;
    const timer2 = setInterval(() => {
      count += 1;
      patched = installInterrupt();
      if (patched || count > attempts) {
        clearInterval(timer2);
      }
    }, intervalMs);
  }
  return { interruptHook: patched };
}
function installLFRefreshNodeHook(appObj, opts = {}) {
  const attempts = opts.attempts ?? 20;
  const intervalMs = opts.intervalMs ?? 250;
  const logger = opts.logger ?? (() => {
  });
  if (!isRefreshHookApp(appObj)) {
    logger('"app" object not available; cannot install refresh hook yet', {}, LogSeverity.Warning);
    return { refreshHook: false };
  }
  const scopedApp = appObj;
  const wrap = opts.refreshWrapper;
  const makePatched = (fn) => {
    const factory = wrap ?? ((original) => async function patched2(...args) {
      if (scopedApp[LFRefreshFlags.InBeforeRefresh] === true) {
        return original.apply(this ?? scopedApp, args);
      }
      scopedApp[LFRefreshFlags.InBeforeRefresh] = true;
      try {
        await beforeRefreshNodeDefs(args == null ? void 0 : args[0]);
      } catch (error2) {
        logger("LF refresh hook failed before calling original function", { error: error2 }, LogSeverity.Warning);
      } finally {
        scopedApp[LFRefreshFlags.InBeforeRefresh] = false;
      }
      return original.apply(this ?? scopedApp, args);
    });
    return factory(fn);
  };
  const installRefresh = () => {
    try {
      if (scopedApp[LFRefreshFlags.PatchedRefresh] === true) {
        return true;
      }
      const current = scopedApp.refreshComboInNodes;
      if (typeof current === "function") {
        scopedApp[LFRefreshFlags.OriginalRefreshRef] = current;
        scopedApp.refreshComboInNodes = makePatched(current);
        scopedApp[LFRefreshFlags.PatchedRefresh] = true;
        return true;
      }
      const descriptor = Object.getOwnPropertyDescriptor(scopedApp, "refreshComboInNodes");
      if (!descriptor || descriptor.configurable) {
        let original;
        Object.defineProperty(scopedApp, "refreshComboInNodes", {
          configurable: true,
          enumerable: true,
          get() {
            return scopedApp[LFRefreshFlags.PatchedRefresh] ? original : scopedApp[LFRefreshFlags.OriginalRefreshRef] ?? original;
          },
          set(fn) {
            if (typeof fn !== "function") {
              original = fn;
              return;
            }
            scopedApp[LFRefreshFlags.OriginalRefreshRef] = fn;
            original = makePatched(fn);
            scopedApp[LFRefreshFlags.PatchedRefresh] = true;
          }
        });
      }
      return false;
    } catch (error2) {
      logger("Failed to patch refreshComboInNodes; proceeding without LF refresh hook", { error: error2 }, LogSeverity.Warning);
      return false;
    }
  };
  let patched = installRefresh();
  if (!patched) {
    let count = 0;
    const timer2 = setInterval(() => {
      count += 1;
      patched = installRefresh();
      if (patched || count > attempts) {
        clearInterval(timer2);
      }
    }, intervalMs);
  }
  return { refreshHook: patched };
}
const CATEGORY = "✨ LF Nodes";
const DESCRIPTION = "Virtual reroute node that propagates upstream type and optional label.";
const DISPLAY_NAME = "Reroute";
const EXTENSION_NAME = `lf.virtual.${DISPLAY_NAME}`;
const NODE_PATH = "✨ LF Nodes/Reroute";
const SERIALIZED_KEYS = ["label", "showIcon", "showType", "mode", "horizontal"];
function deriveInnerColor(base2) {
  const hex = base2.trim();
  const expand = (h2) => h2.length === 4 ? `#${h2[1]}${h2[1]}${h2[2]}${h2[2]}${h2[3]}${h2[3]}` : h2;
  if (!/^#([0-9a-fA-F]{3}){1,2}$/.test(hex)) {
    return "#ececec";
  }
  const full = expand(hex).substring(1);
  const r2 = parseInt(full.substring(0, 2), 16);
  const g2 = parseInt(full.substring(2, 4), 16);
  const b2 = parseInt(full.substring(4, 6), 16);
  const lighten = (c2) => Math.min(255, Math.round(c2 + (255 - c2) * 0.55));
  const rL = lighten(r2);
  const gL = lighten(g2);
  const bL = lighten(b2);
  return `#${rL.toString(16).padStart(2, "0")}${gL.toString(16).padStart(2, "0")}${bL.toString(16).padStart(2, "0")}`;
}
const lfReroute = {
  name: EXTENSION_NAME,
  registerCustomNodes(appInstance) {
    var _a, _b;
    class LFReroute extends LGraphNode {
      constructor() {
        var _a2, _b2, _c, _d, _e, _f;
        super();
        this.isVirtualNode = true;
        this.properties = {
          horizontal: false,
          label: "",
          mode: "label+type",
          showType: true,
          showIcon: true
        };
        this.title = this.properties.label || "Label";
        (_a2 = this.addProperty) == null ? void 0 : _a2.call(this, "label", this.properties.label, "string");
        (_b2 = this.addProperty) == null ? void 0 : _b2.call(this, "mode", this.properties.mode, "string");
        (_c = this.addProperty) == null ? void 0 : _c.call(this, "showType", this.properties.showType, "boolean");
        (_d = this.addProperty) == null ? void 0 : _d.call(this, "showIcon", this.properties.showIcon, "boolean");
        (_e = this.addProperty) == null ? void 0 : _e.call(this, "horizontal", this.properties.horizontal, "boolean");
        this.addInput("", "*");
        this.addOutput(this.makeOutputName("*"), "*");
        this.__labelWidget = (_f = this.addWidget) == null ? void 0 : _f.call(this, "text", "Label", this.properties.label, (v2) => {
          this.properties.label = v2;
          this.refreshLabel();
        }, { multiline: false });
        if (this.__labelWidget) {
          this.__labelWidget.serializeValue = () => this.properties.label;
        }
        this.onConnectionsChange = () => {
          var _a3, _b3;
          try {
            reroutePropagationLogic.call(this, appInstance);
          } catch (error2) {
            (_b3 = (_a3 = getLfManager()) == null ? void 0 : _a3.log) == null ? void 0 : _b3.call(_a3, "[LFReroute] onConnectionsChange error", { error: error2 }, LogSeverity.Warning);
          }
        };
      }
      snapToGrid(size) {
        const proto = LGraphNode.prototype;
        if (proto == null ? void 0 : proto.snapToGrid) {
          return proto.snapToGrid.call(this, size);
        }
        const grid = size || LiteGraph.CANVAS_GRID_SIZE || 10;
        if (this.pos) {
          this.pos[0] = grid * Math.round(this.pos[0] / grid);
          this.pos[1] = grid * Math.round(this.pos[1] / grid);
        }
      }
      getExtraMenuOptions(_ignored, options) {
        options.unshift({
          content: "Cycle Label/Type Mode",
          callback: () => {
            const order = ["label+type", "label", "type"];
            const i2 = order.indexOf(this.properties.mode);
            this.properties.mode = order[(i2 + 1) % order.length];
            this.refreshLabel();
          }
        }, {
          content: (this.properties.showType ? "Hide" : "Show") + " Type Part",
          callback: () => {
            this.properties.showType = !this.properties.showType;
            this.refreshLabel();
          }
        }, {
          content: (this.properties.showIcon ? "Hide" : "Show") + " Icon",
          callback: () => {
            this.properties.showIcon = !this.properties.showIcon;
            COMFY_API.scheduleRedraw();
          }
        }, {
          content: "Edit Label",
          callback: () => {
            const v2 = prompt("Set label", this.properties.label || "");
            if (v2 !== null) {
              this.properties.label = v2;
              this.refreshLabel();
            }
          }
        }, {
          content: "Set " + (this.properties.horizontal ? "Horizontal" : "Vertical"),
          callback: () => {
            this.properties.horizontal = !this.properties.horizontal;
            this.applyOrientation();
          }
        });
      }
      makeOutputName(displayType, labelOverride) {
        const label = (labelOverride !== void 0 ? labelOverride : this.properties.label || "").trim();
        const typePart = this.properties.showType ? displayType : "";
        switch (this.properties.mode) {
          case "label":
            return label || (this.properties.showType ? displayType : "");
          case "type":
            return typePart;
          case "label+type":
          default:
            if (label && typePart)
              return `${label}:${typePart}`;
            return label || typePart;
        }
      }
      refreshLabel() {
        var _a2;
        if (!((_a2 = this.outputs) == null ? void 0 : _a2.length))
          return;
        const effectiveLabel = (this.properties.label || "").trim() || this.__autoLabel || "";
        const displayType = this.__outputType || this.outputs[0].type || "*";
        this.outputs[0].name = this.makeOutputName(displayType, effectiveLabel);
        this.title = effectiveLabel || "Label";
        this.size = this.computeSize();
        this.applyOrientation();
        COMFY_API.scheduleRedraw();
        const w2 = this.__labelWidget;
        if (w2 && "value" in w2 && w2.value !== this.properties.label) {
          w2.value = this.properties.label;
        }
      }
      onSerialize(raw) {
        const o2 = raw;
        if (o2 == null ? void 0 : o2.properties) {
          const target = o2.properties;
          for (const key of SERIALIZED_KEYS) {
            target[key] = this.properties[key];
          }
        }
        if (Array.isArray(o2 == null ? void 0 : o2.widgets_values) && this.__labelWidget && this.widgets) {
          const idx = this.widgets.indexOf(this.__labelWidget);
          if (idx >= 0) {
            o2.widgets_values[idx] = this.properties.label;
          }
        }
      }
      onConfigure(raw) {
        const o2 = raw;
        const props = (o2 == null ? void 0 : o2.properties) || {};
        for (const key of SERIALIZED_KEYS) {
          const incoming = props[key];
          if (incoming === void 0)
            continue;
          if (key === "mode") {
            if (typeof incoming === "string" && ["label", "type", "label+type"].includes(incoming)) {
              this.properties.mode = incoming;
            }
            continue;
          }
          if (key === "label") {
            if (typeof incoming === "string") {
              this.properties.label = incoming;
            } else if (Array.isArray(o2 == null ? void 0 : o2.widgets_values) && this.__labelWidget && this.widgets) {
              const idx = this.widgets.indexOf(this.__labelWidget);
              const wv = o2.widgets_values[idx];
              if (idx >= 0 && typeof wv === "string") {
                this.properties.label = wv;
              }
            }
            continue;
          }
          if (key === "horizontal" || key === "showIcon" || key === "showType") {
            if (typeof incoming === "boolean") {
              this.properties[key] = incoming;
            }
            continue;
          }
        }
        if (this.__labelWidget && this.widgets) {
          const idx = this.widgets.indexOf(this.__labelWidget);
          if (idx >= 0 && "value" in this.__labelWidget) {
            this.__labelWidget.value = this.properties.label;
          }
        }
        this.refreshLabel();
      }
      applyOrientation() {
        var _a2, _b2, _c, _d;
        if (this.properties.horizontal) {
          if ((_a2 = this.inputs) == null ? void 0 : _a2[0]) {
            this.inputs[0].pos = [this.size[0] / 2, 0];
          }
          if ((_b2 = this.outputs) == null ? void 0 : _b2[0]) {
            this.outputs[0].pos = [this.size[0] / 2, this.size[1]];
          }
        } else {
          if ((_c = this.inputs) == null ? void 0 : _c[0]) {
            delete this.inputs[0].pos;
          }
          if ((_d = this.outputs) == null ? void 0 : _d[0]) {
            delete this.outputs[0].pos;
          }
        }
        COMFY_API.scheduleRedraw();
      }
      computeSize() {
        var _a2, _b2, _c;
        const base2 = this.title || "";
        const slotName = ((_b2 = (_a2 = this.outputs) == null ? void 0 : _a2[0]) == null ? void 0 : _b2.name) || "";
        const longest = base2.length > slotName.length ? base2 : slotName;
        const textSize = LiteGraph.NODE_TEXT_SIZE || 14;
        const w2 = Math.max(120, textSize * longest.length * 0.6 + 50);
        const collapsed = (_c = this.flags) == null ? void 0 : _c.collapsed;
        const h2 = collapsed ? 28 : 50;
        return [w2, h2];
      }
      onDrawForeground(ctx) {
        var _a2, _b2, _c, _d;
        try {
          if (!this.properties.showIcon || !ctx) {
            return;
          }
          const headerH = LiteGraph && LiteGraph.NODE_TITLE_HEIGHT || 24;
          const radius = 6;
          const cx = 10 + radius;
          const cy = -headerH / 2;
          ctx.save();
          const displayType = this.__outputType || ((_b2 = (_a2 = this.outputs) == null ? void 0 : _a2[0]) == null ? void 0 : _b2.type);
          let baseColor;
          if (displayType && (LGraphCanvas == null ? void 0 : LGraphCanvas.link_type_colors)) {
            const c2 = LGraphCanvas.link_type_colors[displayType];
            if (typeof c2 === "string") {
              baseColor = c2;
            }
          }
          const outer = baseColor || "#3a3a3a";
          const inner = deriveInnerColor(baseColor || "#3a3a3a");
          ctx.fillStyle = outer;
          ctx.beginPath();
          ctx.arc(cx, cy, radius, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = inner;
          ctx.beginPath();
          ctx.arc(cx, cy, radius * 0.4, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        } catch (err) {
          (_d = (_c = getLfManager()) == null ? void 0 : _c.log) == null ? void 0 : _d.call(_c, "[LFReroute] onDrawForeground error", { err }, LogSeverity.Info);
        }
      }
    }
    function reroutePropagationLogic(appInstance2) {
      var _a2, _b2, _c, _d, _e, _f, _g, _h, _i, _j, _k, _l, _m, _n, _o, _p;
      const isLabeled = (n2) => {
        var _a3;
        return ((_a3 = n2 == null ? void 0 : n2.constructor) == null ? void 0 : _a3.type) === NODE_PATH;
      };
      let inputType = null;
      let upstream = this;
      let originNode = null;
      while (((_b2 = (_a2 = upstream == null ? void 0 : upstream.inputs) == null ? void 0 : _a2[0]) == null ? void 0 : _b2.link) != null) {
        const linkId = upstream.inputs[0].link;
        const link2 = appInstance2.graph.links[linkId];
        if (!link2)
          break;
        const origin = appInstance2.graph.getNodeById(link2.origin_id);
        if (!origin)
          break;
        if (isLabeled(origin)) {
          if (origin === this) {
            (_c = upstream.disconnectInput) == null ? void 0 : _c.call(upstream, link2.target_slot);
            break;
          }
          upstream = origin;
          continue;
        }
        inputType = ((_e = (_d = origin.outputs) == null ? void 0 : _d[link2.origin_slot]) == null ? void 0 : _e.type) || null;
        originNode = origin;
        break;
      }
      let downstreamType = null;
      const firstLinks = ((_g = (_f = this.outputs) == null ? void 0 : _f[0]) == null ? void 0 : _g.links) || [];
      for (const l2 of firstLinks) {
        const link2 = appInstance2.graph.links[l2];
        if (!link2) {
          continue;
        }
        const target = appInstance2.graph.getNodeById(link2.target_id);
        if (!target || isLabeled(target)) {
          continue;
        }
        downstreamType = ((_i = (_h = target.inputs) == null ? void 0 : _h[link2.target_slot]) == null ? void 0 : _i.type) || null;
        if (downstreamType) {
          break;
        }
      }
      const finalType = inputType || downstreamType || "*";
      if (!(this.properties.label || "").trim()) {
        if (originNode) {
          const candidateTitle = (originNode.title || "").trim();
          const candidateSlotName = (() => {
            var _a3, _b3, _c2, _d2;
            if (!originNode.outputs)
              return "";
            const slotIdx = (() => {
              var _a4, _b4;
              if (((_b4 = (_a4 = upstream == null ? void 0 : upstream.inputs) == null ? void 0 : _a4[0]) == null ? void 0 : _b4.link) != null) {
                const linkId = upstream.inputs[0].link;
                const link2 = appInstance2.graph.links[linkId];
                if (link2)
                  return link2.origin_slot ?? 0;
              }
              return 0;
            })();
            return (((_b3 = (_a3 = originNode.outputs) == null ? void 0 : _a3[slotIdx]) == null ? void 0 : _b3.label) || ((_d2 = (_c2 = originNode.outputs) == null ? void 0 : _c2[slotIdx]) == null ? void 0 : _d2.name) || "").trim();
          })();
          const effectiveSlotName = candidateSlotName && candidateSlotName !== "*" ? candidateSlotName : "";
          const chosen = effectiveSlotName || candidateTitle;
          if (chosen) {
            this.__autoLabel = chosen;
          }
        } else {
          this.__autoLabel = void 0;
        }
      } else {
        this.__autoLabel = void 0;
      }
      this.__outputType = finalType;
      if ((_j = this.inputs) == null ? void 0 : _j[0]) {
        this.inputs[0].type = finalType;
      }
      if ((_k = this.outputs) == null ? void 0 : _k[0]) {
        this.outputs[0].type = finalType;
        this.outputs[0].name = this.makeOutputName(finalType);
      }
      this.size = this.computeSize();
      this.applyOrientation();
      this.refreshLabel();
      const color = (_l = LGraphCanvas.link_type_colors) == null ? void 0 : _l[finalType];
      if (color) {
        if ((_n = (_m = this.outputs) == null ? void 0 : _m[0]) == null ? void 0 : _n.links) {
          for (const l2 of this.outputs[0].links) {
            const link2 = appInstance2.graph.links[l2];
            if (link2) {
              link2.color = color;
            }
          }
        }
        const inLinkId = (_p = (_o = this.inputs) == null ? void 0 : _o[0]) == null ? void 0 : _p.link;
        if (inLinkId != null) {
          const inLink = appInstance2.graph.links[inLinkId];
          if (inLink) {
            inLink.color = color;
          }
        }
      }
      COMFY_API.scheduleRedraw();
    }
    LiteGraph.registerNodeType(NODE_PATH, Object.assign(LFReroute, {
      title_mode: LiteGraph.NORMAL_TITLE,
      title: "Reroute",
      collapsable: true,
      category: "LF Nodes",
      description: "Label + type aware reroute (frontend virtual)"
    }));
    onAfterGraphConfigured(LFReroute, (node) => {
      requestAnimationFrame(() => {
        var _a2, _b2, _c;
        try {
          (_a2 = node.onConnectionsChange) == null ? void 0 : _a2.call(node);
        } catch (err) {
          (_c = (_b2 = getLfManager()) == null ? void 0 : _b2.log) == null ? void 0 : _c.call(_b2, "[LFReroute] onAfterGraphConfigured", { err }, LogSeverity.Warning);
        }
      });
    });
    (_b = (_a = getLfManager()) == null ? void 0 : _a.log) == null ? void 0 : _b.call(_a, `Virtual node registered (UI compliant): ${NODE_PATH}`, {}, LogSeverity.Success);
  },
  beforeRegisterVueAppNodeDefs(defs) {
    const def = defs.find((d2) => d2.name === NODE_PATH);
    if (def) {
      def.display_name = DISPLAY_NAME;
      def.category = CATEGORY;
      def.description = DESCRIPTION;
      if (def.python_module === "custom_nodes.frontend_only") {
        def.python_module = "lf_nodes.virtual";
      }
    }
  }
};
var __classPrivateFieldGet$3 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LFNodes_REGISTRY;
class LFNodes {
  constructor() {
    _LFNodes_REGISTRY.set(this, /* @__PURE__ */ new Map());
    this.add = (extension) => {
      var _a, _b;
      const lfManager = getLfManager();
      if (!(extension == null ? void 0 : extension.name)) {
        (_a = lfManager == null ? void 0 : lfManager.log) == null ? void 0 : _a.call(lfManager, `Attempted to add virtual node with invalid name`, { extension }, LogSeverity.Warning);
        return;
      }
      if (__classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").has(extension.name)) {
        (_b = lfManager == null ? void 0 : lfManager.log) == null ? void 0 : _b.call(lfManager, `Duplicate virtual node ignored: '${extension.name}'`, {}, LogSeverity.Warning);
        return;
      }
      __classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").set(extension.name, { extension, registered: false });
    };
    this.addMany = (extensions) => {
      extensions.forEach((e2) => this.add(e2));
    };
    this.list = () => Array.from(__classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").values());
    this.registerAll = () => {
      const lfManager = getLfManager();
      __classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").forEach((entry, key) => {
        var _a, _b;
        if (entry.registered) {
          return;
        }
        try {
          COMFY_API.register(entry.extension);
          entry.registered = true;
          (_a = lfManager == null ? void 0 : lfManager.log) == null ? void 0 : _a.call(lfManager, `Registered virtual node '${key}'`, {}, LogSeverity.Success);
        } catch (error2) {
          entry.error = error2;
          (_b = lfManager == null ? void 0 : lfManager.log) == null ? void 0 : _b.call(lfManager, `Failed to register virtual node '${key}'`, { error: error2 }, LogSeverity.Error);
        }
      });
    };
    this.add(lfReroute);
  }
}
_LFNodes_REGISTRY = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldGet$2 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var __classPrivateFieldSet$1 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var _LFTooltip_instances, _LFTooltip_CB, _LFTooltip_CSS_CLASSES, _LFTooltip_LAYOUT, _LFTooltip_TOOLTIP_ELEMENT, _LFTooltip_initialize, _LFTooltip_uploadLayout, _LFTooltip_buttonEventHandler;
class LFTooltip {
  constructor() {
    _LFTooltip_instances.add(this);
    _LFTooltip_CB.set(this, {});
    _LFTooltip_CSS_CLASSES.set(this, {
      wrapper: "lf-tooltip",
      content: `lf-tooltip__content`
    });
    _LFTooltip_LAYOUT.set(this, void 0);
    _LFTooltip_TOOLTIP_ELEMENT.set(this, void 0);
    _LFTooltip_buttonEventHandler.set(this, async (upload, e2) => {
      const { eventType } = e2.detail;
      switch (eventType) {
        case "click":
          const lfManager = getLfManager();
          switch (__classPrivateFieldGet$2(this, _LFTooltip_LAYOUT, "f")) {
            case "upload":
              const files = await upload.getValue();
              const reader = new FileReader();
              reader.onload = (e3) => {
                var _a;
                const result = (_a = e3.target) == null ? void 0 : _a.result;
                let base64String = "";
                if (typeof result === "string") {
                  base64String = result.replace(/^data:.*,/, "");
                } else if (result instanceof ArrayBuffer) {
                  const arrayBufferView = new Uint8Array(result);
                  base64String = btoa(String.fromCharCode.apply(null, arrayBufferView));
                }
                if (__classPrivateFieldGet$2(this, _LFTooltip_CB, "f")) {
                  lfManager.log("Invoking upload callback.", { base64String }, LogSeverity.Info);
                  __classPrivateFieldGet$2(this, _LFTooltip_CB, "f")[__classPrivateFieldGet$2(this, _LFTooltip_LAYOUT, "f")](base64String);
                }
              };
              reader.readAsDataURL(files[0]);
              break;
          }
      }
    });
  }
  //#endregion
  //#region Create
  create(anchor, layout, cb) {
    const lfFramework2 = getLfManager().getManagers().lfFramework;
    if (__classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f")) {
      __classPrivateFieldGet$2(this, _LFTooltip_instances, "m", _LFTooltip_initialize).call(this);
    }
    const parent = document.body;
    __classPrivateFieldSet$1(this, _LFTooltip_CB, cb ? { [layout]: cb } : {}, "f");
    __classPrivateFieldSet$1(this, _LFTooltip_LAYOUT, layout ?? "upload", "f");
    __classPrivateFieldSet$1(this, _LFTooltip_TOOLTIP_ELEMENT, document.createElement("div"), "f");
    __classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f").classList.add(__classPrivateFieldGet$2(this, _LFTooltip_CSS_CLASSES, "f").wrapper);
    let layoutElement;
    switch (__classPrivateFieldGet$2(this, _LFTooltip_LAYOUT, "f")) {
      case "upload":
        layoutElement = __classPrivateFieldGet$2(this, _LFTooltip_instances, "m", _LFTooltip_uploadLayout).call(this);
        __classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f").appendChild(layoutElement);
        break;
    }
    lfFramework2.portal.open(layoutElement, __classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f"), anchor, 0, "auto");
    lfFramework2.addClickCallback({ cb: () => this.destroy(), element: layoutElement });
    requestAnimationFrame(() => parent.appendChild(__classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f")));
  }
  //#endregion
  //#region Destroy
  destroy() {
    __classPrivateFieldGet$2(this, _LFTooltip_instances, "m", _LFTooltip_initialize).call(this);
  }
}
_LFTooltip_CB = /* @__PURE__ */ new WeakMap(), _LFTooltip_CSS_CLASSES = /* @__PURE__ */ new WeakMap(), _LFTooltip_LAYOUT = /* @__PURE__ */ new WeakMap(), _LFTooltip_TOOLTIP_ELEMENT = /* @__PURE__ */ new WeakMap(), _LFTooltip_buttonEventHandler = /* @__PURE__ */ new WeakMap(), _LFTooltip_instances = /* @__PURE__ */ new WeakSet(), _LFTooltip_initialize = function _LFTooltip_initialize2() {
  var _a;
  (_a = __classPrivateFieldGet$2(this, _LFTooltip_TOOLTIP_ELEMENT, "f")) == null ? void 0 : _a.remove();
  __classPrivateFieldSet$1(this, _LFTooltip_TOOLTIP_ELEMENT, null, "f");
  __classPrivateFieldSet$1(this, _LFTooltip_CB, {}, "f");
  __classPrivateFieldSet$1(this, _LFTooltip_LAYOUT, null, "f");
}, _LFTooltip_uploadLayout = function _LFTooltip_uploadLayout2() {
  const content = document.createElement(TagName.Div);
  const upload = document.createElement(TagName.LfUpload);
  const button = document.createElement(TagName.LfButton);
  content.classList.add(__classPrivateFieldGet$2(this, _LFTooltip_CSS_CLASSES, "f").content);
  button.lfIcon = "upload";
  button.lfLabel = "Update cover";
  button.lfStretchX = true;
  content.dataset.lf = "portal";
  content.appendChild(upload);
  content.appendChild(button);
  button.addEventListener(LfEventName.LfButton, __classPrivateFieldGet$2(this, _LFTooltip_buttonEventHandler, "f").bind(__classPrivateFieldGet$2(this, _LFTooltip_buttonEventHandler, "f"), upload));
  return content;
};
const DOWNLOAD_PLACEHOLDERS = {
  lfDataset: {
    nodes: [
      {
        cells: {
          lfImage: { shape: "image", value: "download" },
          lfText: { shape: "text", value: "Fetching metadata from CivitAI..." }
        },
        id: "0"
      }
    ]
  }
};
const CARD_PROPS_TO_SERIALIZE = ["lfDataset"];
const EV_HANDLERS$9 = {
  //#region Button handler
  button: (state, e2) => {
    const { comp, eventType } = e2.detail;
    const { grid, node } = state;
    switch (eventType) {
      case "click":
        const cards = Array.from(grid.querySelectorAll(TagName.LfCard));
        if (cards == null ? void 0 : cards.length) {
          const models = [];
          const widget = getCustomWidget(node, CustomWidgetName.card);
          cards.forEach((card) => {
            var _a, _b, _c, _d;
            const hashCell = (_d = (_c = (_b = (_a = card.lfDataset) == null ? void 0 : _a.nodes) == null ? void 0 : _b[0]) == null ? void 0 : _c.cells) == null ? void 0 : _d.lfCode;
            if (hashCell) {
              const { hash, path } = JSON.parse(JSON.stringify(hashCell.value));
              const dataset = card.lfDataset;
              comp.lfShowSpinner = true;
              models.push({ apiFlag: true, dataset, hash, path });
            }
          });
          if (models.length) {
            const value = {
              props: []
            };
            cardPlaceholders(widget, cards.length);
            apiCall$1(models, true).then((r2) => {
              for (let index = 0; index < r2.length; index++) {
                const cardProps = r2[index];
                if (cardProps.lfDataset) {
                  value.props.push(cardProps);
                } else {
                  value.props.push({
                    ...cardProps,
                    lfDataset: models[index].dataset
                  });
                }
              }
              widget.options.setValue(JSON.stringify(value));
              requestAnimationFrame(() => comp.lfShowSpinner = false);
            });
          }
        }
        break;
    }
  },
  //#endregion
  //#region Card handler
  card: (e2) => {
    var _a, _b;
    const { comp, eventType, originalEvent } = e2.detail;
    const node = (_b = (_a = comp.lfDataset) == null ? void 0 : _a.nodes) == null ? void 0 : _b[0];
    switch (eventType) {
      case "click":
        if (node == null ? void 0 : node.value) {
          window.open(String(node.value).valueOf(), "_blank");
        }
        break;
      case "contextmenu":
        const ogEv = originalEvent;
        const lfManager = getLfManager();
        ogEv.preventDefault();
        ogEv.stopPropagation();
        const tip = lfManager.getManagers().tooltip;
        const cb = async (b64image) => {
          var _a2, _b2, _c, _d;
          const node2 = (_b2 = (_a2 = comp.lfDataset) == null ? void 0 : _a2.nodes) == null ? void 0 : _b2[0];
          if (node2) {
            const code2 = (_c = node2 == null ? void 0 : node2.cells) == null ? void 0 : _c.lfCode;
            if (code2) {
              try {
                const path = JSON.parse(JSON.stringify(code2.value)).path;
                lfManager.log(`Updating cover for model with path: ${path}`, { b64image }, LogSeverity.Info);
                getApiRoutes().metadata.updateCover(path, b64image);
                const image2 = (_d = node2 == null ? void 0 : node2.cells) == null ? void 0 : _d.lfImage;
                if (image2) {
                  image2.value = `data:image/png;charset=utf-8;base64,${b64image}`;
                  comp.refresh();
                  tip.destroy();
                }
              } catch (error2) {
                lfManager.log("Failed to fetch the model's path from .info file", { b64image }, LogSeverity.Error);
              }
            }
          }
        };
        tip.create({ x: ogEv.x, y: ogEv.y }, "upload", cb);
        break;
    }
  }
  //#endregion
};
const cardPlaceholders = (widget, count) => {
  const dummyValue = {
    props: []
  };
  for (let index = 0; index < count; index++) {
    dummyValue.props.push(DOWNLOAD_PLACEHOLDERS);
  }
  widget.options.setValue(JSON.stringify(dummyValue));
};
const apiCall$1 = async (models, forcedSave = false) => {
  const promises = models.map(async ({ dataset, hash, path, apiFlag }) => {
    if (apiFlag) {
      const payload = await getApiRoutes().metadata.get(hash);
      return onResponse(dataset, path, forcedSave, payload);
    } else {
      return onResponse(dataset, path, forcedSave, null);
    }
  });
  return Promise.all(promises);
};
const onResponse = async (dataset, path, forcedSave, payload) => {
  var _a, _b, _c;
  const r2 = payload == null ? void 0 : payload.data;
  const id = r2 == null ? void 0 : r2.id;
  const props = {
    lfStyle: ".sub-2.description { white-space: pre-wrap; }"
  };
  switch (typeof id) {
    case "number":
      const code2 = (_c = (_b = (_a = dataset == null ? void 0 : dataset.nodes) == null ? void 0 : _a[0]) == null ? void 0 : _b.cells) == null ? void 0 : _c.lfCode;
      const civitaiDataset = prepareValidDataset(r2, code2);
      props.lfDataset = civitaiDataset;
      getApiRoutes().metadata.save(path, civitaiDataset, forcedSave);
      break;
    case "string":
      const node = dataset.nodes[0];
      node.description = "";
      node.value = "";
      node.cells.lfButton = {
        lfIcon: "warning",
        lfLabel: "Not found on CivitAI!",
        lfStyling: "flat",
        lfUiState: "disabled",
        shape: "button",
        value: ""
      };
      node.cells.text3 = {
        value: "Whoops! It seems like something's off. Falling back to local data."
      };
      props.lfDataset = dataset;
      break;
  }
  return props;
};
const prepCards = (container, propsArray) => {
  var _a;
  let count = 0;
  const cards = container.querySelectorAll("lf-card");
  cards.forEach((c2) => c2.remove());
  for (let index = 0; propsArray && index < propsArray.length; index++) {
    const card = container.appendChild(createCard());
    count += 1;
    const props = propsArray[index];
    if (props.lfDataset) {
      for (const key in props) {
        if (Object.prototype.hasOwnProperty.call(props, key)) {
          const prop = props[key];
          if (key === "lfDataset") {
            try {
              if (typeof prop === "string") {
                card.lfDataset = unescapeJson(prop).parsedJson;
              } else {
                card.lfDataset = prop;
              }
              const node = (_a = card.lfDataset.nodes) == null ? void 0 : _a[0];
              if (node) {
                card.dataset.link = node.description;
                if (node.value) {
                  card.title = String(node.value).valueOf();
                }
              }
            } catch (error2) {
              getLfManager().log("Error when setting lfData prop on card!", { error: error2 }, LogSeverity.Error);
            }
          } else {
            card[key] = prop;
          }
        }
      }
    }
  }
  return count;
};
const getCardProps = (container) => {
  const propsArray = [];
  const cards = container.querySelectorAll("lf-card");
  for (let index = 0; index < cards.length; index++) {
    const card = cards[index];
    const props = CARD_PROPS_TO_SERIALIZE.reduce((acc, p2) => {
      if (card[p2]) {
        acc[p2] = card[p2];
      }
      return acc;
    }, {});
    propsArray.push(props);
  }
  return propsArray;
};
const createCard = () => {
  const card = document.createElement(TagName.LfCard);
  card.addEventListener(LfEventName.LfCard, EV_HANDLERS$9.card);
  return card;
};
const prepareValidDataset = (r2, code2) => {
  var _a, _b, _c, _d, _e;
  const dataset = {
    nodes: [
      {
        cells: { lfCode: code2 ?? null, lfImage: null, text1: null, text2: null, text3: null },
        id: r2.id.toString(),
        description: "Click to open the model's page on CivitAI",
        value: `https://civitai.com/models/${r2.modelId}`
      }
    ]
  };
  const cells = dataset.nodes[0].cells;
  cells.lfImage = {
    shape: "image",
    value: r2.images[0].url
  };
  cells.text1 = { value: r2.model.name };
  cells.text2 = { value: r2.name };
  cells.text3 = {
    value: `- Info:
Type: ${((_a = r2.model) == null ? void 0 : _a.type) ? r2.model.type : "N/A"}
Status: ${r2.status ? r2.status : "N/A"}
Base model: ${r2.baseModel ? r2.baseModel : "N/A"}
Description: ${r2.description ? r2.description : "N/A"}

- Trained words:
${((_b = r2.trainedWords) == null ? void 0 : _b.length) ? r2.trainedWords.join(", ") : "N/A"}

- Stats:
Updated at: ${r2.updatedAt ? r2.updatedAt : "N/A"}
Downloads: ${((_c = r2.stats) == null ? void 0 : _c.downloadCount) ? r2.stats.downloadCount : "N/A"}
Rating: ${((_d = r2.stats) == null ? void 0 : _d.rating) ? r2.stats.rating : "N/A"}
Thumbs up: ${((_e = r2.stats) == null ? void 0 : _e.thumbsUpCount) ? r2.stats.thumbsUpCount : "N/A"}

(data pulled from CivitAI at: ${(/* @__PURE__ */ new Date()).toLocaleDateString()})
`
  };
  return dataset;
};
var CardCSS;
(function(CardCSS2) {
  CardCSS2["Content"] = "lf-card";
  CardCSS2["ContentHasButton"] = "lf-card--has-button";
  CardCSS2["Grid"] = "lf-card__grid";
})(CardCSS || (CardCSS = {}));
const STATE$g = /* @__PURE__ */ new WeakMap();
const cardFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$g.get(wrapper),
      getValue() {
        const { grid } = STATE$g.get(wrapper);
        return {
          props: getCardProps(grid) || []
        };
      },
      setValue(value) {
        const { grid } = STATE$g.get(wrapper);
        const callback = (_2, u2) => {
          const { props } = u2.parsedJson;
          const len = (props == null ? void 0 : props.length) > 1 ? 2 : 1;
          grid.style.setProperty("--card-grid", `repeat(1, 1fr) / repeat(${len}, 1fr)`);
          prepCards(grid, props);
        };
        normalizeValue(value, callback, CustomWidgetName.card);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    grid.classList.add(CardCSS.Grid);
    content.classList.add(CardCSS.Content);
    content.appendChild(grid);
    switch (node.comfyClass) {
      case NodeName.checkpointSelector:
      case NodeName.diffusionModelSelector:
      case NodeName.embeddingSelector:
      case NodeName.loraAndEmbeddingSelector:
      case NodeName.loraSelector:
        content.classList.add(CardCSS.ContentHasButton);
        const button = document.createElement(TagName.LfButton);
        button.lfIcon = "download";
        button.lfLabel = "Refresh";
        button.lfStretchX = true;
        button.title = "Attempts to manually ownload fresh metadata from CivitAI";
        button.addEventListener(LfEventName.LfButton, (e2) => EV_HANDLERS$9.button(STATE$g.get(wrapper), e2));
        content.appendChild(button);
        break;
    }
    wrapper.appendChild(content);
    const options = cardFactory.options(wrapper);
    STATE$g.set(wrapper, { grid, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.card, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$g
  //#endregion
};
var CardsWithChipCSS;
(function(CardsWithChipCSS2) {
  CardsWithChipCSS2["Content"] = "lf-cardswithchip";
  CardsWithChipCSS2["Cards"] = "lf-cardswithchip__cards";
  CardsWithChipCSS2["Chip"] = "lf-cardswithchip__chip";
  CardsWithChipCSS2["Grid"] = "lf-cardswithchip__grid";
})(CardsWithChipCSS || (CardsWithChipCSS = {}));
const STATE$f = /* @__PURE__ */ new WeakMap();
const cardsWithChipFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$f.get(wrapper),
      getValue() {
        const { chip, grid } = STATE$f.get(wrapper);
        return {
          chip: (chip == null ? void 0 : chip.lfDataset) || {},
          props: getCardProps(grid) || []
        };
      },
      setValue(value) {
        const { chip, grid } = STATE$f.get(wrapper);
        const callback = (v2, u2) => {
          const dataset = u2.parsedJson;
          const cardsCount = prepCards(grid, dataset.props);
          if (!cardsCount || !v2) {
            return;
          }
          const columns = cardsCount > 1 ? 2 : 1;
          grid.style.setProperty("--card-grid", String(columns).valueOf());
          if (chip) {
            chip.lfDataset = dataset.chip;
          }
        };
        normalizeValue(value, callback, CustomWidgetName.cardsWithChip);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const outerGrid = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const chip = document.createElement(TagName.LfChip);
    content.classList.add(CardsWithChipCSS.Content);
    outerGrid.classList.add(CardsWithChipCSS.Grid);
    grid.classList.add(CardsWithChipCSS.Cards);
    chip.classList.add(CardsWithChipCSS.Chip);
    outerGrid.appendChild(chip);
    outerGrid.appendChild(grid);
    content.appendChild(outerGrid);
    wrapper.appendChild(content);
    const options = cardsWithChipFactory.options(wrapper);
    STATE$f.set(wrapper, { chip, grid, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.cardsWithChip, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$f
  //#endregion
};
var CarouselCSS;
(function(CarouselCSS2) {
  CarouselCSS2["Content"] = "lf-carousel";
  CarouselCSS2["Widget"] = "lf-carousel__widget";
})(CarouselCSS || (CarouselCSS = {}));
const STATE$e = /* @__PURE__ */ new WeakMap();
const carouselFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE$e.get(wrapper),
      getValue() {
        const { carousel } = STATE$e.get(wrapper);
        return (carousel == null ? void 0 : carousel.lfDataset) || {};
      },
      setValue(value) {
        const { carousel } = STATE$e.get(wrapper);
        const callback = (_2, u2) => {
          const dataset = u2.parsedJson;
          carousel.lfDataset = dataset || {};
        };
        normalizeValue(value, callback, CustomWidgetName.carousel);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const carousel = document.createElement(TagName.LfCarousel);
    carousel.lfAutoPlay = true;
    content.classList.add(CarouselCSS.Content);
    carousel.classList.add(CarouselCSS.Widget);
    content.appendChild(carousel);
    wrapper.appendChild(content);
    const options = carouselFactory.options(wrapper);
    STATE$e.set(wrapper, { carousel, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.carousel, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$e
  //#endregion
};
const EV_HANDLERS$8 = {
  //#region Chat handler
  chat: (state, e2) => {
    const { eventType, history, status } = e2.detail;
    switch (eventType) {
      case "polling":
        const severity = status === "ready" ? LogSeverity.Info : status === "offline" ? LogSeverity.Error : LogSeverity.Warning;
        getLfManager().log("Chat widget, polling status: " + status, { chat: e2.detail }, severity);
        break;
      case "update":
        state.history = history;
        break;
    }
  }
  //#endregion
};
var ChatCSS;
(function(ChatCSS2) {
  ChatCSS2["Content"] = "lf-chat";
  ChatCSS2["Widget"] = "lf-chat__widget";
})(ChatCSS || (ChatCSS = {}));
const STATE$d = /* @__PURE__ */ new WeakMap();
const chatFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$d.get(wrapper),
      getValue() {
        const { history } = STATE$d.get(wrapper);
        return history || "";
      },
      setValue(value) {
        const state = STATE$d.get(wrapper);
        const callback = (v2) => {
          state.history = v2 || "";
          if (v2 && state.chat.lfValue) {
            state.chat.lfValue = JSON.parse(v2);
          }
          state.chat.setHistory(v2);
        };
        normalizeValue(value, callback, CustomWidgetName.chat);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const chat = document.createElement(TagName.LfChat);
    content.classList.add(ChatCSS.Content);
    chat.classList.add(ChatCSS.Widget);
    chat.addEventListener(LfEventName.LfChat, (e2) => EV_HANDLERS$8.chat(STATE$d.get(wrapper), e2));
    content.appendChild(chat);
    wrapper.appendChild(content);
    const options = chatFactory.options(wrapper);
    STATE$d.set(wrapper, { chat, history: "", node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.chat, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$d
  //#endregion
};
const EV_HANDLERS$7 = {
  //#region Chip handler
  chip: async (state, e2) => {
    const { comp, eventType } = e2.detail;
    switch (eventType) {
      case "click":
        const selectedValues = [];
        (await comp.getSelectedNodes()).forEach((node) => {
          selectedValues.push(String(node.value).valueOf());
        });
        state.selected = selectedValues.join(", ");
        break;
    }
  }
};
var ChipCSS;
(function(ChipCSS2) {
  ChipCSS2["Content"] = "lf-chip";
  ChipCSS2["Widget"] = "lf-chip__widget";
})(ChipCSS || (ChipCSS = {}));
const STATE$c = /* @__PURE__ */ new WeakMap();
const chipFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE$c.get(wrapper),
      getValue() {
        const { selected } = STATE$c.get(wrapper);
        return selected || "";
      },
      setValue(value) {
        const state = STATE$c.get(wrapper);
        const callback = (v2) => {
          const value2 = v2 ? v2.split(", ") : [];
          state.selected = v2;
          state.chip.setSelectedNodes(value2);
        };
        normalizeValue(value, callback, CustomWidgetName.chip);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const chip = document.createElement(TagName.LfChip);
    content.classList.add(ChipCSS.Content);
    chip.classList.add(ChipCSS.Widget);
    chip.addEventListener(LfEventName.LfChip, (e2) => EV_HANDLERS$7.chip(STATE$c.get(wrapper), e2));
    switch (node.comfyClass) {
      case NodeName.keywordToggleFromJson:
        chip.lfStyling = "filter";
        break;
    }
    content.appendChild(chip);
    wrapper.appendChild(content);
    const options = chipFactory.options(wrapper);
    STATE$c.set(wrapper, { chip, node, selected: "", wrapper });
    return { widget: createDOMWidget(CustomWidgetName.chip, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$c
  //#endregion
};
var CodeCSS;
(function(CodeCSS2) {
  CodeCSS2["Content"] = "lf-code";
  CodeCSS2["Widget"] = "lf-code__widget";
})(CodeCSS || (CodeCSS = {}));
const STATE$b = /* @__PURE__ */ new WeakMap();
const codeFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$b.get(wrapper),
      getValue() {
        const { code: code2 } = STATE$b.get(wrapper);
        switch (code2.lfLanguage) {
          case "json":
            return code2.lfValue || "{}";
          default:
            return code2.lfValue || "";
        }
      },
      setValue(value) {
        const { code: code2 } = STATE$b.get(wrapper);
        const callback = (v2, u2) => {
          switch (code2.lfLanguage) {
            case "json":
              code2.lfValue = u2.unescapedStr || "{}";
              break;
            default:
              code2.lfValue = typeof v2 === "string" ? v2 : "";
              break;
          }
        };
        normalizeValue(value, callback, CustomWidgetName.code);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const code2 = document.createElement(TagName.LfCode);
    content.classList.add(CodeCSS.Content);
    code2.classList.add(CodeCSS.Widget);
    switch (node.comfyClass) {
      case NodeName.displayJson:
      case NodeName.displayPrimitiveAsJson:
      case NodeName.shuffleJsonKeys:
      case NodeName.sortJsonKeys:
      case NodeName.stringToJson:
        code2.lfLanguage = "json";
        code2.lfValue = "{}";
        break;
      default:
        code2.lfLanguage = "markdown";
        code2.lfValue = "";
        break;
    }
    content.appendChild(code2);
    wrapper.appendChild(content);
    const options = codeFactory.options(wrapper);
    STATE$b.set(wrapper, { code: code2, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.code, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$b
  //#endregion
};
var CompareCSS;
(function(CompareCSS2) {
  CompareCSS2["Content"] = "lf-compare";
  CompareCSS2["Widget"] = "lf-compare__widget";
})(CompareCSS || (CompareCSS = {}));
const STATE$a = /* @__PURE__ */ new WeakMap();
const compareFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$a.get(wrapper),
      getValue() {
        const { compare } = STATE$a.get(wrapper);
        return compare.lfDataset || {};
      },
      setValue(value) {
        const { compare } = STATE$a.get(wrapper);
        const callback = (_2, u2) => {
          compare.lfDataset = u2.parsedJson || {};
        };
        normalizeValue(value, callback, CustomWidgetName.compare);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const compare = document.createElement(TagName.LfCompare);
    content.classList.add(CompareCSS.Content);
    compare.classList.add(CompareCSS.Widget);
    switch (node.comfyClass) {
      default:
        compare.lfShape = "image";
        break;
    }
    content.appendChild(compare);
    wrapper.appendChild(content);
    const options = compareFactory.options(wrapper);
    STATE$a.set(wrapper, { compare, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.compare, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$a
  //#endregion
};
var ControlPanelCSS;
(function(ControlPanelCSS2) {
  ControlPanelCSS2["Content"] = "lf-controlpanel";
  ControlPanelCSS2["Grid"] = "lf-controlpanel__grid";
  ControlPanelCSS2["Spinner"] = "lf-controlpanel__spinner";
})(ControlPanelCSS || (ControlPanelCSS = {}));
var ControlPanelIcons;
(function(ControlPanelIcons2) {
  ControlPanelIcons2["Analytics"] = "chart-histogram";
  ControlPanelIcons2["Backup"] = "download";
  ControlPanelIcons2["Debug"] = "bug";
  ControlPanelIcons2["ExternalPreviews"] = "photo-search";
  ControlPanelIcons2["GitHub"] = "brand-github";
  ControlPanelIcons2["Metadata"] = "info-hexagon";
  ControlPanelIcons2["SystemDashboard"] = "percentage-60";
  ControlPanelIcons2["Theme"] = "color-swatch";
})(ControlPanelIcons || (ControlPanelIcons = {}));
var ControlPanelIds;
(function(ControlPanelIds2) {
  ControlPanelIds2["Analytics"] = "analytics";
  ControlPanelIds2["Backup"] = "backup";
  ControlPanelIds2["Debug"] = "debug";
  ControlPanelIds2["ExternalPreviews"] = "external-previews";
  ControlPanelIds2["GitHub"] = "github";
  ControlPanelIds2["Metadata"] = "metadata";
  ControlPanelIds2["SystemDashboard"] = "system-dashboard";
  ControlPanelIds2["Theme"] = "theme";
})(ControlPanelIds || (ControlPanelIds = {}));
var ControlPanelLabels;
(function(ControlPanelLabels2) {
  ControlPanelLabels2["AutoBackup"] = "Automatic Backup";
  ControlPanelLabels2["Backup"] = "Backup now";
  ControlPanelLabels2["BackupRetention"] = "Maximum backups to keep";
  ControlPanelLabels2["ClearLogs"] = "Clear logs";
  ControlPanelLabels2["ClearPreviews"] = "Clear preview cache";
  ControlPanelLabels2["Debug"] = "Debug";
  ControlPanelLabels2["DeleteUsage"] = "Delete usage analytics info";
  ControlPanelLabels2["DeleteMetadata"] = "Delete models info";
  ControlPanelLabels2["Done"] = "Done!";
  ControlPanelLabels2["OpenIssue"] = "Open an issue";
  ControlPanelLabels2["RefreshBackupStats"] = "Refresh backup stats";
  ControlPanelLabels2["RefreshPreviewStats"] = "Refresh preview stats";
  ControlPanelLabels2["SystemAutoRefresh"] = "Auto refresh (seconds)";
  ControlPanelLabels2["RefreshSystemStats"] = "Refresh system stats";
  ControlPanelLabels2["Theme"] = "Random theme";
})(ControlPanelLabels || (ControlPanelLabels = {}));
var ControlPanelSection;
(function(ControlPanelSection2) {
  ControlPanelSection2["Content"] = "content";
  ControlPanelSection2["ContentSeparator"] = "content_spearator";
  ControlPanelSection2["Paragraph"] = "paragraph";
  ControlPanelSection2["Root"] = "root";
  ControlPanelSection2["Section"] = "section";
})(ControlPanelSection || (ControlPanelSection = {}));
const BUTTON_STYLE = ":host { margin: auto; padding: 1em 0; width: max-content; }";
const STYLES = {
  customization: () => ({
    margin: "0"
  }),
  debugGrid: () => ({
    display: "grid",
    gridTemplateRows: "repeat(5, max-content) 1fr",
    height: "100%",
    margin: "0"
  }),
  debugLogs: () => ({
    display: "grid",
    gridGap: "0.75em",
    gridTemplateRows: "320px 480px"
  }),
  logsArea: () => ({
    backgroundColor: "rgba(var(--lf-color-on-bg), 0.075)",
    borderRadius: "0.5em",
    display: "block",
    height: "100%",
    marginBottom: "1em",
    overflow: "auto"
  }),
  separator: () => ({
    border: "1px solid rgb(var(--lf-color-border))",
    display: "block",
    margin: "0.75em auto 1.25em",
    opacity: "0.25",
    width: "50%"
  })
};
const buildAnalyticsSection = () => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-clear": clearIcon } = theme.get.current().variables;
  return {
    icon: ControlPanelIcons.Analytics,
    id: ControlPanelSection.Section,
    value: "Analytics",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Usage",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Usage analytics can be enabled by saving datasets through the UpdateUsageStatistics node and displayed with the UsageStatistics node."
          },
          {
            id: ControlPanelSection.Content,
            tagName: "br",
            value: ""
          },
          {
            id: ControlPanelSection.Content,
            value: "Once datasets are created (input folder of ComfyUI), the count for each resource used will increase everytime that particular resource is updated."
          },
          {
            id: ControlPanelSection.Content,
            tagName: "br",
            value: ""
          },
          {
            id: ControlPanelSection.Content,
            value: "This button will clear all usage analytics data from your input folder."
          },
          {
            id: ControlPanelSection.Content,
            tagName: "br",
            value: ""
          },
          {
            id: ControlPanelSection.Content,
            value: "This action is IRREVERSIBLE so use it with caution."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: clearIcon,
                lfLabel: ControlPanelLabels.DeleteUsage,
                lfStyle: BUTTON_STYLE,
                lfStyling: "outlined",
                lfUiState: "danger",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildBackupSection = (stats) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-download": downloadIcon, "--lf-icon-refresh": refreshIcon } = theme.get.current().variables;
  const { progress } = theme.get.icons();
  const totalBytes = (stats == null ? void 0 : stats.totalSizeBytes) ?? 0;
  const fileCount = (stats == null ? void 0 : stats.fileCount) ?? 0;
  const maxBytes = 1024 * 1024 * 1024;
  const percentage = Math.min(totalBytes / maxBytes * 100, 100);
  return {
    icon: ControlPanelIcons.Backup,
    id: ControlPanelSection.Section,
    value: "Backup",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Toggle on/off",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Toggle this toggle to automatically back up the folder <path/to/your/comfyui/user/LF_Nodes> once a day (the first time you open this workflow)."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfToggle: {
                lfLabel: ControlPanelLabels.AutoBackup,
                lfLeadingLabel: true,
                lfStyle: ":host { text-align: center; padding: 1em 0; }",
                shape: "toggle",
                value: !!getLfManager().isBackupEnabled()
              }
            }
          }
        ]
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Backup statistics",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Backup files are stored in the user/LF_Nodes folder. Monitor your backup folder size to ensure you have enough disk space."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "",
            children: [
              {
                id: "backup-info",
                value: `Current backup: ${formatBytes(totalBytes)} (${fileCount} files)`,
                cssStyle: { display: "block", marginBottom: "0.75em" }
              },
              {
                id: "backup-progress",
                value: "",
                cells: {
                  lfProgressbar: {
                    lfIcon: progress,
                    lfLabel: `${formatBytes(totalBytes)} (${percentage.toFixed(1)}%)`,
                    shape: "progressbar",
                    value: percentage
                  }
                }
              }
            ]
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: refreshIcon,
                lfLabel: ControlPanelLabels.RefreshBackupStats,
                lfStyle: BUTTON_STYLE,
                lfStyling: "flat",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Rolling backup retention",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Set the maximum number of backups to keep. When this limit is exceeded, the oldest backups will be automatically deleted. Set to 0 to disable this feature."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfTextfield: {
                lfHtmlAttributes: { type: "number" },
                lfLabel: ControlPanelLabels.BackupRetention,
                lfStyle: ":host { text-align: center; padding: 1em 0; }",
                lfValue: getLfManager().getBackupRetention().toString() || "14",
                shape: "textfield",
                value: ""
              }
            }
          }
        ]
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Backup files",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "This button will create a manual backup of the content in <path/to/your/comfyui/user/LF_Nodes>."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: downloadIcon,
                lfLabel: ControlPanelLabels.Backup,
                lfStyle: BUTTON_STYLE,
                lfStyling: "raised",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildDebugSection = (logsData) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-clear": clearIcon } = theme.get.current().variables;
  return {
    icon: ControlPanelIcons.Debug,
    id: ControlPanelSection.Section,
    cssStyle: STYLES.debugGrid(),
    value: "Debug",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Toggle on/off",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Activating the debug will enable the display of verbose logging."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfToggle: {
                lfLabel: ControlPanelLabels.Debug,
                lfLeadingLabel: true,
                lfStyle: ":host { text-align: center; padding: 1em 0; }",
                shape: "toggle",
                value: !!getLfManager().isDebug()
              }
            }
          }
        ]
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Logs",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Every time the node manager receives a message it will be printed below."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "In the browser console there should be more informations."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "Further below another card will display additional LF Widgets information."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                shape: "button",
                lfIcon: clearIcon,
                lfLabel: ControlPanelLabels.ClearLogs,
                lfStretchX: true,
                lfStyle: BUTTON_STYLE,
                lfUiState: "danger",
                value: ""
              }
            }
          }
        ]
      },
      {
        id: ControlPanelSection.Paragraph,
        cssStyle: STYLES.debugLogs(),
        value: "",
        children: [
          {
            id: "content-wrapper",
            cssStyle: STYLES.logsArea(),
            value: "",
            children: logsData
          },
          {
            id: "content-wrapper",
            value: "",
            cells: {
              lfCard: {
                lfDataset: {
                  nodes: [
                    {
                      cells: {
                        lfCode: { shape: "code", value: "" },
                        lfButton: { shape: "button", value: "" },
                        lfButton_2: { shape: "button", value: "" },
                        lfToggle: {
                          shape: "toggle",
                          value: !!getLfManager().getManagers().lfFramework.debug.isEnabled()
                        }
                      },
                      id: "debug"
                    }
                  ]
                },
                lfLayout: "debug",
                shape: "card",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildExternalPreviewsSection = (stats) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-delete": deleteIcon, "--lf-icon-refresh": refreshIcon } = theme.get.current().variables;
  const { progress } = theme.get.icons();
  const totalBytes = (stats == null ? void 0 : stats.totalSizeBytes) ?? 0;
  const fileCount = (stats == null ? void 0 : stats.fileCount) ?? 0;
  const maxBytes = 1024 * 1024 * 1024;
  const percentage = Math.min(totalBytes / maxBytes * 100, 100);
  return {
    icon: ControlPanelIcons.ExternalPreviews,
    id: ControlPanelSection.Section,
    value: "External Previews",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Cache statistics",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "External image previews are cached in the _lf_external_previews folder under ComfyUI/input to speed up loading."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "",
            children: [
              {
                id: "cache-info",
                value: `Current cache: ${formatBytes(totalBytes)} (${fileCount} files)`,
                cssStyle: { display: "block", marginBottom: "0.75em" }
              },
              {
                id: "cache-progress",
                value: "",
                cells: {
                  lfProgressbar: {
                    lfIcon: progress,
                    lfLabel: `${formatBytes(totalBytes)} (${percentage.toFixed(1)}%)`,
                    shape: "progressbar",
                    value: percentage
                  }
                }
              }
            ]
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: refreshIcon,
                lfLabel: ControlPanelLabels.RefreshPreviewStats,
                lfStyle: BUTTON_STYLE,
                lfStyling: "flat",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Clear cache",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "This button will permanently delete the entire preview cache folder and all its contents."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "This action is IRREVERSIBLE so use it with caution."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: deleteIcon,
                lfLabel: ControlPanelLabels.ClearPreviews,
                lfStyle: BUTTON_STYLE,
                lfStyling: "outlined",
                lfUiState: "danger",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildGitHubSection = () => {
  var _a, _b;
  const lfManager = getLfManager();
  const releaseData = lfManager.getLatestRelease();
  const { theme } = lfManager.getManagers().lfFramework;
  const { brandGithub } = theme.get.icons();
  return {
    icon: ControlPanelIcons.GitHub,
    id: ControlPanelSection.Section,
    value: "",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: `Version: ${(releaseData == null ? void 0 : releaseData.tag_name) || "N/A"}`,
        children: [
          {
            cells: {
              lfCode: {
                lfLanguage: "markdown",
                shape: "code",
                value: (releaseData == null ? void 0 : releaseData.body) || "No changelog available"
              }
            },
            id: "release-description"
          },
          {
            id: "release-author",
            children: [
              {
                id: "author-avatar",
                value: "",
                cssStyle: {
                  backgroundImage: `url(${((_a = releaseData == null ? void 0 : releaseData.author) == null ? void 0 : _a.avatar_url) || ""})`,
                  backgroundSize: "cover",
                  borderRadius: "50%",
                  display: "inline-block",
                  height: "2em",
                  marginRight: "0.5em",
                  verticalAlign: "middle",
                  width: "2em"
                }
              },
              {
                id: "author-name",
                value: `Author: ${((_b = releaseData == null ? void 0 : releaseData.author) == null ? void 0 : _b.login) || "Unknown"}`,
                cssStyle: {
                  fontSize: "0.9em",
                  color: "rgb(var(--lf-color-secondary))",
                  verticalAlign: "middle"
                }
              }
            ],
            cssStyle: {
              alignItems: "center",
              display: "flex",
              justifyContent: "center",
              marginBottom: ".25em"
            }
          },
          {
            cssStyle: {
              color: "rgb(var(--lf-color-secondary))",
              display: "block",
              fontSize: "0.9em",
              fontStyle: "italic",
              marginBottom: "2em",
              textAlign: "center",
              width: "100%"
            },
            id: "release-date",
            value: `Published on: ${(releaseData == null ? void 0 : releaseData.published_at) ? new Date(releaseData.published_at).toLocaleDateString() : "Unknown"}`
          },
          {
            cssStyle: STYLES.separator(),
            id: ControlPanelSection.ContentSeparator,
            value: ""
          },
          {
            id: ControlPanelSection.Paragraph,
            value: "Bug report",
            children: [
              {
                id: ControlPanelSection.Content,
                value: "If you find bugs or odd behaviors feel free to open an issue on GitHub, just follow the link below!"
              },
              { id: ControlPanelSection.Content, tagName: "br", value: "" },
              {
                id: ControlPanelSection.Content,
                value: "Be sure to include as much information as you can, without sufficient data it's difficult to troubleshoot problems."
              },
              {
                id: ControlPanelSection.Content,
                value: "",
                cells: {
                  lfButton: {
                    lfIcon: brandGithub,
                    lfLabel: ControlPanelLabels.OpenIssue,
                    lfStyle: BUTTON_STYLE,
                    lfStyling: "raised",
                    shape: "button",
                    value: ""
                  }
                }
              }
            ]
          }
        ]
      }
    ]
  };
};
const buildMetadataSection = () => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-delete": deleteIcon } = theme.get.current().variables;
  return {
    icon: ControlPanelIcons.Metadata,
    id: ControlPanelSection.Section,
    value: "Metadata",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Purge metadata files",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Metadata pulled from CivitAI are stored in .info files saved in the same folders of the models to avoid unnecessary fetches from the API."
          },
          { id: ControlPanelSection.Content, tagName: "div", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "By pressing this button it's possible to delete every .info file created by fetching the metadata."
          },
          { id: ControlPanelSection.Content, tagName: "br", value: "" },
          {
            id: ControlPanelSection.Content,
            value: "This action is IRREVERSIBLE so use it with caution."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfIcon: deleteIcon,
                lfLabel: ControlPanelLabels.DeleteMetadata,
                lfStyle: BUTTON_STYLE,
                lfStyling: "outlined",
                lfUiState: "danger",
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const buildSystemDashboardSection = (stats) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { "--lf-icon-refresh": refreshIcon } = theme.get.current().variables;
  const { progress } = theme.get.icons();
  const refreshTimeout = getLfManager().getSystemTimeout() || 0;
  const gpus = (stats == null ? void 0 : stats.gpus) ?? [];
  const disks = (stats == null ? void 0 : stats.disks) ?? [];
  const cpu = stats == null ? void 0 : stats.cpu;
  const ram = stats == null ? void 0 : stats.ram;
  const errors2 = (stats == null ? void 0 : stats.errors) ?? [];
  const timestamp = (stats == null ? void 0 : stats.timestamp) ? new Date(stats.timestamp) : null;
  const lastUpdated = timestamp ? timestamp.toLocaleString() : "Waiting for data";
  const gpuNodes = gpus.length ? gpus.map((gpu) => {
    const vramPercent = gpu.vram_total ? clampPercent(gpu.vram_used / gpu.vram_total * 100) : 0;
    const utilPercent = clampPercent(gpu.utilization);
    return {
      id: `gpu-${gpu.index}`,
      value: "",
      cssStyle: { marginBottom: "1em" },
      children: [
        {
          id: `gpu-${gpu.index}-title`,
          value: `${gpu.name} (GPU ${gpu.index})`,
          tagName: "strong"
        },
        buildProgressNode(progress, `gpu-${gpu.index}-vram`, `VRAM ${formatBytes(gpu.vram_used)} / ${formatBytes(gpu.vram_total)} (${percentLabel(vramPercent)})`, vramPercent),
        buildProgressNode(progress, `gpu-${gpu.index}-util`, `Utilization ${percentLabel(utilPercent)}`, utilPercent)
      ]
    };
  }) : [
    {
      id: "gpu-none",
      value: "No GPUs detected.",
      cssStyle: { opacity: "0.7" }
    }
  ];
  const cpuNodes = cpu ? [
    buildProgressNode(progress, "cpu-average", `Average usage ${percentLabel(cpu.average)}`, clampPercent(cpu.average)),
    {
      id: "cpu-meta",
      value: `Logical cores: ${cpu.count} • Physical cores: ${cpu.physical_count}`,
      cssStyle: { fontSize: "0.9em", opacity: "0.8" }
    },
    {
      id: "cpu-cores",
      value: "",
      cssStyle: {
        display: "grid",
        gap: "0.75em",
        gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))"
      },
      children: cpu.cores.map((core) => buildProgressNode(progress, `cpu-core-${core.index}`, `Core ${core.index} ${percentLabel(core.usage)}`, clampPercent(core.usage)))
    }
  ] : [
    {
      id: "cpu-none",
      value: "CPU statistics unavailable.",
      cssStyle: { opacity: "0.7" }
    }
  ];
  const ramNodes = ram ? [
    buildProgressNode(progress, "ram-usage", `RAM ${formatBytes(ram.used)} / ${formatBytes(ram.total)} (${percentLabel(ram.percent)})`, clampPercent(ram.percent)),
    {
      id: "ram-available",
      value: `Available: ${formatBytes(ram.available)}`,
      cssStyle: { fontSize: "0.9em", opacity: "0.8" }
    },
    ...ram.swap_total ? [
      buildProgressNode(progress, "swap-usage", `Swap ${formatBytes(ram.swap_used)} / ${formatBytes(ram.swap_total)} (${percentLabel(ram.swap_used / ram.swap_total * 100)})`, clampPercent(ram.swap_used / ram.swap_total * 100))
    ] : []
  ] : [
    {
      id: "ram-none",
      value: "RAM statistics unavailable.",
      cssStyle: { opacity: "0.7" }
    }
  ];
  const diskNodes = disks.length ? disks.map((disk, index) => {
    const used = toNumber(disk.used);
    const total = toNumber(disk.total);
    const percent = total ? clampPercent(used / total * 100) : clampPercent(disk.percent);
    const descriptor = [disk.device || disk.mountpoint, disk.label].filter(Boolean).join(" ");
    return {
      id: `disk-${index}`,
      value: "",
      cssStyle: { marginBottom: "1em" },
      children: [
        {
          id: `disk-${index}-title`,
          value: descriptor || disk.mountpoint,
          tagName: "strong"
        },
        {
          id: `disk-${index}-mount`,
          value: `Mount: ${disk.mountpoint}`,
          cssStyle: { fontSize: "0.9em", opacity: "0.8", marginBottom: "0.25em" }
        },
        buildProgressNode(progress, `disk-${index}-usage`, `${formatBytes(disk.used)} / ${formatBytes(disk.total)} (${percentLabel(percent)})`, percent)
      ]
    };
  }) : [
    {
      id: "disk-none",
      value: "No disks detected.",
      cssStyle: { opacity: "0.7" }
    }
  ];
  const overviewChildren = [
    {
      id: ControlPanelSection.Content,
      value: "Monitor real-time hardware usage for GPUs, CPU, memory, and storage."
    },
    {
      id: ControlPanelSection.Content,
      value: `Last updated: ${lastUpdated}`,
      cssStyle: { fontSize: "0.85em", opacity: "0.75" }
    },
    {
      id: ControlPanelSection.Content,
      value: refreshTimeout > 0 ? `Auto refresh every ${refreshTimeout}s` : "Auto refresh disabled.",
      cssStyle: { fontSize: "0.85em", opacity: "0.75", marginTop: "0.3em" }
    },
    {
      id: ControlPanelSection.Content,
      value: "",
      cells: {
        lfTextfield: {
          lfHelper: { showWhenFocused: false, value: "Set to 0 to disable auto refresh" },
          lfHtmlAttributes: { type: "number", min: "0", step: "any" },
          lfLabel: ControlPanelLabels.SystemAutoRefresh,
          lfStyle: ":host { display: block; margin: 0.75em auto; max-width: 240px; }",
          lfValue: refreshTimeout > 0 ? refreshTimeout.toString() : "",
          shape: "textfield",
          value: ""
        }
      }
    }
  ];
  if (errors2.length) {
    overviewChildren.push({
      id: "system-errors",
      value: "",
      children: errors2.map((message, index) => ({
        id: `system-error-${index}`,
        value: message,
        cssStyle: {
          color: "rgb(var(--lf-color-danger))",
          fontSize: "0.85em"
        }
      }))
    });
  }
  overviewChildren.push({
    id: ControlPanelSection.Content,
    value: "",
    cells: {
      lfButton: {
        lfIcon: refreshIcon,
        lfLabel: ControlPanelLabels.RefreshSystemStats,
        lfStyle: BUTTON_STYLE,
        lfStyling: "flat",
        shape: "button",
        value: ""
      }
    }
  });
  return {
    icon: ControlPanelIcons.SystemDashboard,
    id: ControlPanelSection.Section,
    value: "System monitor",
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Overview",
        children: overviewChildren
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "GPU usage",
        children: gpuNodes
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "CPU usage",
        children: cpuNodes
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Memory",
        children: ramNodes
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: ""
      },
      {
        id: ControlPanelSection.Paragraph,
        value: "Disk usage",
        children: diskNodes
      }
    ]
  };
};
const getUsageState = (percent) => {
  const value = clampPercent(percent);
  if (value >= 90)
    return "danger";
  if (value >= 70)
    return "warning";
  if (value === 0)
    return "primary";
  return "success";
};
const buildProgressNode = (icon, id, label, percent) => ({
  id,
  value: "",
  cells: {
    lfProgressbar: {
      lfIcon: icon,
      lfLabel: label,
      lfUiState: getUsageState(percent),
      shape: "progressbar",
      value: clampPercent(percent)
    }
  }
});
const buildThemeSection = () => {
  return {
    icon: ControlPanelIcons.Theme,
    id: ControlPanelSection.Section,
    value: "Customization",
    cssStyle: STYLES.customization(),
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: "Theme selector",
        children: [
          {
            id: ControlPanelSection.Content,
            value: "Through the button below it's possible to set a random theme for the LF Widgets components, or select one from the dropdown menu."
          },
          {
            id: ControlPanelSection.Content,
            value: "",
            cells: {
              lfButton: {
                lfDataset: getLfThemes(),
                lfLabel: ControlPanelLabels.Theme,
                lfStyle: BUTTON_STYLE,
                shape: "button",
                value: ""
              }
            }
          }
        ]
      }
    ]
  };
};
const SECTIONS = {
  [ControlPanelIds.Analytics]: buildAnalyticsSection,
  [ControlPanelIds.Backup]: buildBackupSection,
  [ControlPanelIds.Debug]: buildDebugSection,
  [ControlPanelIds.ExternalPreviews]: buildExternalPreviewsSection,
  [ControlPanelIds.GitHub]: buildGitHubSection,
  [ControlPanelIds.Metadata]: buildMetadataSection,
  [ControlPanelIds.SystemDashboard]: buildSystemDashboardSection,
  [ControlPanelIds.Theme]: buildThemeSection
};
const setArticleDataset = (article, node) => {
  article.lfDataset = {
    nodes: [{ children: [node], id: ControlPanelSection.Root }]
  };
};
let SYSTEM_REFRESH_TIMER = null;
let SYSTEM_ARTICLE = null;
let SYSTEM_LAST_STATS;
const clearSystemAutoRefresh = () => {
  if (SYSTEM_REFRESH_TIMER) {
    clearTimeout(SYSTEM_REFRESH_TIMER);
    SYSTEM_REFRESH_TIMER = null;
  }
};
const getSystemAutoRefreshSeconds = () => {
  var _a, _b;
  try {
    const stored = ((_b = (_a = getLfManager()) == null ? void 0 : _a.getSystemTimeout) == null ? void 0 : _b.call(_a)) ?? 0;
    return typeof stored === "number" && stored > 0 ? Math.floor(stored) : 0;
  } catch {
    return 0;
  }
};
const hasConnectedArticle = () => {
  return SYSTEM_ARTICLE && SYSTEM_ARTICLE.isConnected && document.body.contains(SYSTEM_ARTICLE);
};
const scheduleSystemAutoRefresh = () => {
  clearSystemAutoRefresh();
  const seconds = getSystemAutoRefreshSeconds();
  if (seconds <= 0 || !hasConnectedArticle()) {
    return;
  }
  const delay = Math.max(seconds * 1e3, 1e3);
  SYSTEM_REFRESH_TIMER = setTimeout(() => {
    if (!hasConnectedArticle()) {
      clearSystemAutoRefresh();
      return;
    }
    refreshSystemDashboard(SYSTEM_ARTICLE, { reschedule: false }).finally(() => {
      scheduleSystemAutoRefresh();
    });
  }, delay);
};
const setSystemAutoRefreshSeconds = (seconds, article) => {
  const sanitized = typeof seconds === "number" && Number.isFinite(seconds) && seconds > 0 ? Math.floor(seconds) : 0;
  getLfManager().setSystemTimeout(sanitized);
  if (article) {
    SYSTEM_ARTICLE = article;
  }
  if (sanitized > 0) {
    scheduleSystemAutoRefresh();
  } else {
    clearSystemAutoRefresh();
  }
  const targetArticle = article ?? SYSTEM_ARTICLE;
  if (targetArticle) {
    applySystemStats(targetArticle, SYSTEM_LAST_STATS);
  }
  return sanitized;
};
const applySystemStats = (article, stats) => {
  const nextStats = stats ? { ...stats } : SYSTEM_LAST_STATS ? { ...SYSTEM_LAST_STATS } : void 0;
  SYSTEM_LAST_STATS = nextStats;
  setArticleDataset(article, SECTIONS[ControlPanelIds.SystemDashboard](nextStats));
  requestAnimationFrame(() => {
    const textfield = article.querySelector(`lf-textfield[lf-label="${ControlPanelLabels.SystemAutoRefresh}"]`);
    if (textfield) {
      const timeout = getSystemAutoRefreshSeconds();
      const value = timeout > 0 ? timeout.toString() : "";
      if (textfield.lfValue !== value) {
        textfield.lfValue = value;
      }
    }
  });
};
const gatherSystemStats = async () => {
  const routes = getApiRoutes().system;
  const [gpu, cpu, ram, disks] = await Promise.all([
    routes.getGpuStats(),
    routes.getCpuStats(),
    routes.getRamStats(),
    routes.getDiskStats()
  ]);
  const stats = { timestamp: Date.now() };
  const errors2 = [];
  if (gpu.status === LogSeverity.Success) {
    stats.gpus = gpu.data || [];
  } else {
    errors2.push(`GPU: ${gpu.message || "Statistics unavailable."}`);
  }
  if (cpu.status === LogSeverity.Success) {
    stats.cpu = cpu.data;
  } else {
    errors2.push(`CPU: ${cpu.message || "Statistics unavailable."}`);
  }
  if (ram.status === LogSeverity.Success) {
    stats.ram = ram.data;
  } else {
    errors2.push(`RAM: ${ram.message || "Statistics unavailable."}`);
  }
  if (disks.status === LogSeverity.Success) {
    stats.disks = disks.data || [];
  } else {
    errors2.push(`Disks: ${disks.message || "Statistics unavailable."}`);
  }
  if (errors2.length) {
    stats.errors = errors2;
  }
  return stats;
};
const refreshSystemDashboard = async (article, options = {}) => {
  var _a;
  const { reschedule = true } = options;
  const payload = {
    message: "",
    status: LogSeverity.Info
  };
  SYSTEM_ARTICLE = article;
  try {
    const stats = await gatherSystemStats();
    applySystemStats(article, stats);
    if ((_a = stats.errors) == null ? void 0 : _a.length) {
      payload.message = `System statistics updated with warnings: ${stats.errors.join(" | ")}`;
      payload.status = LogSeverity.Warning;
    } else {
      payload.message = "System statistics updated.";
      payload.status = LogSeverity.Success;
    }
  } catch (error2) {
    payload.message = String(error2);
    payload.status = LogSeverity.Error;
  }
  if (reschedule) {
    scheduleSystemAutoRefresh();
  }
  return payload;
};
const getSystemLastStats = () => SYSTEM_LAST_STATS;
let BUTTON_TIMEOUT;
const INTRO_SECTION = ControlPanelIds.GitHub;
const withButtonSpinner = (comp, promise, label) => {
  const onResponse2 = () => {
    comp.lfIcon = "check";
    comp.lfLabel = ControlPanelLabels.Done;
    comp.lfShowSpinner = false;
    comp.lfUiState = "disabled";
  };
  const restore = () => {
    comp.lfLabel = label;
    comp.lfIcon = "x";
    comp.lfUiState = "primary";
    BUTTON_TIMEOUT = null;
  };
  requestAnimationFrame(() => comp.lfShowSpinner = true);
  promise.then(() => {
    requestAnimationFrame(onResponse2);
    if (BUTTON_TIMEOUT) {
      clearTimeout(BUTTON_TIMEOUT);
    }
    BUTTON_TIMEOUT = setTimeout(() => requestAnimationFrame(restore), 1e3);
  });
};
const updateArticleSection = (article, id, data) => {
  const buildNode = SECTIONS[id];
  if (!buildNode)
    return;
  setArticleDataset(article, buildNode(data));
};
const handleButtonClick = (comp, slot) => {
  switch (comp.lfLabel) {
    case ControlPanelLabels.Backup:
      withButtonSpinner(comp, getApiRoutes().backup.new("manual"), ControlPanelLabels.Backup);
      getApiRoutes().backup.cleanOld();
      break;
    case ControlPanelLabels.ClearLogs: {
      const { article, dataset } = getLfManager().getDebugDataset();
      if ((dataset == null ? void 0 : dataset.length) > 0) {
        dataset.splice(0, dataset.length);
        article.refresh();
      }
      break;
    }
    case ControlPanelLabels.ClearPreviews:
      withButtonSpinner(comp, getApiRoutes().preview.clearCache(), ControlPanelLabels.ClearPreviews);
      break;
    case ControlPanelLabels.DeleteMetadata:
      withButtonSpinner(comp, getApiRoutes().metadata.clear(), ControlPanelLabels.DeleteMetadata);
      break;
    case ControlPanelLabels.DeleteUsage:
      withButtonSpinner(comp, getApiRoutes().analytics.clear("usage"), ControlPanelLabels.DeleteUsage);
      break;
    case ControlPanelLabels.OpenIssue:
      window.open("https://github.com/lucafoscili/comfyui-lf/issues/new", "_blank");
      break;
    case ControlPanelLabels.RefreshPreviewStats:
      getApiRoutes().preview.getStats().then((response) => {
        if (response.status === "success") {
          updateArticleSection(slot, ControlPanelIds.ExternalPreviews, {
            totalSizeBytes: response.data.total_size_bytes,
            fileCount: response.data.file_count
          });
        }
      });
      break;
    case ControlPanelLabels.RefreshBackupStats:
      getApiRoutes().backup.getStats().then((response) => {
        if (response.status === "success") {
          updateArticleSection(slot, ControlPanelIds.Backup, {
            totalSizeBytes: response.data.total_size_bytes,
            fileCount: response.data.file_count
          });
        }
      });
      break;
    case ControlPanelLabels.RefreshSystemStats:
      withButtonSpinner(comp, refreshSystemDashboard(slot), ControlPanelLabels.RefreshSystemStats);
      break;
    case ControlPanelLabels.Theme:
      getLfManager().getManagers().lfFramework.theme.randomize();
      break;
  }
};
const EV_HANDLERS$6 = {
  article: (e2) => {
    const { comp, eventType, originalEvent } = e2.detail;
    if (eventType === "lf-event") {
      handleLfEvent(originalEvent, comp.rootElement);
    }
  },
  button: (e2, slot) => {
    const { comp, eventType, originalEvent } = e2.detail;
    switch (eventType) {
      case "click":
        handleButtonClick(comp, slot);
        break;
      case "lf-event": {
        const ogEv = originalEvent;
        EV_HANDLERS$6.list(ogEv);
        break;
      }
    }
  },
  list: (e2) => {
    const { comp, eventType, node } = e2.detail;
    const { lfFramework: lfFramework2 } = getLfManager().getManagers();
    const element = comp.rootElement;
    const value = node.id;
    switch (eventType) {
      case "click":
        lfFramework2.theme.set(value);
        break;
      case "ready":
        element.title = "Change the LF Nodes suite theme";
        lfFramework2.theme.set(value);
        break;
    }
  },
  textfield: (e2) => {
    const { comp, eventType, value } = e2.detail;
    const element = comp.rootElement;
    const article = element.closest("lf-article");
    switch (eventType) {
      case "change":
        if (comp.lfLabel === ControlPanelLabels.SystemAutoRefresh) {
          const trimmed = (value || "").trim();
          const parsed = trimmed ? Number(trimmed) : 0;
          const normalized = setSystemAutoRefreshSeconds(parsed, article);
          comp.lfValue = normalized > 0 ? normalized.toString() : "";
        } else if (comp.lfLabel === ControlPanelLabels.BackupRetention) {
          const retentionValue = parseInt(value, 10);
          if (!isNaN(retentionValue) && retentionValue >= 0) {
            getLfManager().setBackupRetention(retentionValue);
          }
        }
        break;
      case "ready":
        if (comp.lfLabel === ControlPanelLabels.SystemAutoRefresh) {
          element.title = "Auto refresh interval in seconds (0 or empty disables auto refresh)";
          const currentTimeout = getSystemAutoRefreshSeconds();
          comp.lfValue = currentTimeout > 0 ? currentTimeout.toString() : comp.lfValue || "";
        } else if (comp.lfLabel === ControlPanelLabels.BackupRetention) {
          element.title = "Maximum number of backups to keep (0 = unlimited)";
        }
        break;
    }
  },
  toggle: (e2) => {
    const { comp, eventType, value } = e2.detail;
    const element = comp.rootElement;
    switch (eventType) {
      case "change":
        getLfManager().toggleDebug(value === "on" ? true : false);
        break;
      case "ready":
        element.title = "Activate verbose console logging";
        break;
    }
  }
};
const handleLfEvent = (e2, slot) => {
  const { comp } = e2.detail;
  if (isButton(comp)) {
    const ogEv = e2;
    EV_HANDLERS$6.button(ogEv, slot);
  }
  if (isTextfield(comp)) {
    const ogEv = e2;
    EV_HANDLERS$6.textfield(ogEv);
  }
  if (isToggle(comp)) {
    const ogEv = e2;
    EV_HANDLERS$6.toggle(ogEv);
  }
};
const INTRO_SECTION_ID = INTRO_SECTION;
const prepArticle = (key, node) => {
  const article = document.createElement(TagName.LfArticle);
  setArticleDataset(article, node);
  article.slot = key;
  article.addEventListener(LfEventName.LfArticle, EV_HANDLERS$6.article);
  return article;
};
const buildSection = (id) => {
  switch (id) {
    //#region Analytics
    case ControlPanelIds.Analytics: {
      const node = SECTIONS[ControlPanelIds.Analytics]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion
    //#region Backup
    case ControlPanelIds.Backup: {
      const node = SECTIONS[ControlPanelIds.Backup]();
      const article = prepArticle(id, node);
      getApiRoutes().backup.getStats().then((response) => {
        if (response.status === "success") {
          const updatedNode = SECTIONS[ControlPanelIds.Backup]({
            totalSizeBytes: response.data.total_size_bytes,
            fileCount: response.data.file_count
          });
          setArticleDataset(article, updatedNode);
        }
      });
      return { article, node };
    }
    //#endregion
    //#region Debug
    case ControlPanelIds.Debug: {
      const logsData = [];
      const node = SECTIONS[ControlPanelIds.Debug](logsData);
      const article = prepArticle(id, node);
      getLfManager().setDebugDataset(article, logsData);
      return { article, node };
    }
    //#endregion
    //#region ExternalPreviews
    case ControlPanelIds.ExternalPreviews: {
      const node = SECTIONS[ControlPanelIds.ExternalPreviews]();
      const article = prepArticle(id, node);
      getApiRoutes().preview.getStats().then((response) => {
        if (response.status === "success") {
          const updatedNode = SECTIONS[ControlPanelIds.ExternalPreviews]({
            totalSizeBytes: response.data.total_size_bytes,
            fileCount: response.data.file_count
          });
          setArticleDataset(article, updatedNode);
        }
      });
      return { article, node };
    }
    //#endregion
    //#region Metadata
    case ControlPanelIds.Metadata: {
      const node = SECTIONS[ControlPanelIds.Metadata]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion
    //#region System Dashboard
    case ControlPanelIds.SystemDashboard: {
      const initialStats = getSystemLastStats();
      const node = SECTIONS[ControlPanelIds.SystemDashboard](initialStats);
      const article = prepArticle(id, node);
      applySystemStats(article, initialStats);
      refreshSystemDashboard(article);
      return { article, node };
    }
    //#endregion
    //#region Theme
    case ControlPanelIds.Theme: {
      const node = SECTIONS[ControlPanelIds.Theme]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion
    default:
      return null;
  }
};
const createContent = () => {
  const grid = document.createElement(TagName.Div);
  const accordion = document.createElement(TagName.LfAccordion);
  const nodes = [];
  accordion.lfDataset = { nodes };
  for (const id in SECTIONS) {
    if (id !== INTRO_SECTION_ID && Object.prototype.hasOwnProperty.call(SECTIONS, id)) {
      const section = buildSection(id);
      if (!section) {
        continue;
      }
      const { article, node } = section;
      const { icon, value } = node;
      nodes.push({
        cells: {
          lfSlot: {
            shape: "slot",
            value: id
          }
        },
        icon,
        id,
        value
      });
      accordion.appendChild(article);
    }
  }
  const intro = prepArticle(INTRO_SECTION_ID, SECTIONS[INTRO_SECTION_ID]());
  grid.classList.add(ControlPanelCSS.Grid);
  grid.appendChild(intro);
  grid.appendChild(accordion);
  return grid;
};
const STATE$9 = /* @__PURE__ */ new WeakMap();
const controlPanelFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$9.get(wrapper),
      getValue() {
        return {
          backup: getLfManager().isBackupEnabled() || false,
          backupRetention: getLfManager().getBackupRetention() || 14,
          debug: getLfManager().isDebug() || false,
          systemTimeout: getLfManager().getSystemTimeout() || 0,
          themes: getLfManager().getManagers().lfFramework.theme.get.current().name || ""
        };
      },
      setValue(value) {
        const callback = (_2, u2) => {
          const { backup, backupRetention, debug, systemTimeout, themes } = u2.parsedJson;
          if (backup === true || backup === false) {
            getLfManager().toggleBackup(backup);
          }
          if (typeof backupRetention === "number") {
            getLfManager().setBackupRetention(backupRetention);
          }
          if (debug === true || debug === false) {
            getLfManager().toggleDebug(debug);
          }
          if (typeof systemTimeout === "number") {
            setSystemAutoRefreshSeconds(systemTimeout);
          }
          if (themes) {
            getLfManager().getManagers().lfFramework.theme.set(themes);
          }
          return value;
        };
        normalizeValue(value, callback, CustomWidgetName.controlPanel);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const contentCb = (domWidget, isReady) => {
      const readyCb = (domWidget2) => {
        setTimeout(() => {
          getApiRoutes().backup.new();
          contentCb(domWidget2, true);
          getApiRoutes().backup.cleanOld();
        }, 750);
      };
      const createSpinner = () => {
        const spinner = document.createElement(TagName.LfSpinner);
        spinner.classList.add(ControlPanelCSS.Spinner);
        spinner.lfActive = true;
        spinner.lfLayout = 11;
        return spinner;
      };
      const content = document.createElement(TagName.Div);
      if (isReady) {
        content.appendChild(createContent());
        domWidget.replaceChild(content, domWidget.firstChild);
      } else {
        const spinner = createSpinner();
        spinner.addEventListener(LfEventName.LfSpinner, readyCb.bind(null, domWidget));
        content.appendChild(spinner);
        domWidget.appendChild(content);
      }
      content.classList.add(ControlPanelCSS.Content);
    };
    const wrapper = document.createElement(TagName.Div);
    contentCb(wrapper, false);
    const options = controlPanelFactory.options(wrapper);
    STATE$9.set(wrapper, { node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.controlPanel, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$9
  //#endregion
};
var CountBarChartCSS;
(function(CountBarChartCSS2) {
  CountBarChartCSS2["Content"] = "lf-countbarchart";
  CountBarChartCSS2["Widget"] = "lf-countbarchart__widget";
})(CountBarChartCSS || (CountBarChartCSS = {}));
const STATE$8 = /* @__PURE__ */ new WeakMap();
const countBarChartFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE$8.get(wrapper),
      getValue() {
        const { datasets } = STATE$8.get(wrapper);
        return {
          chart: (datasets == null ? void 0 : datasets.chart) || {},
          chip: (datasets == null ? void 0 : datasets.chip) || {}
        };
      },
      setValue(value) {
        const { card, datasets } = STATE$8.get(wrapper);
        const callback = (_2, u2) => {
          const json = u2.parsedJson;
          datasets.chart = json.chart || {};
          datasets.chip = json.chip || {};
          card.lfDataset = {
            nodes: [
              {
                id: "countBarChart",
                cells: {
                  lfButton: { shape: "button", value: "" },
                  lfChart: {
                    lfAxis: ["Axis_0"],
                    lfDataset: datasets.chart,
                    lfSeries: ["Series_0"],
                    shape: "chart",
                    value: ""
                  },
                  lfChip: { lfDataset: datasets.chip, shape: "chip", value: "" }
                }
              }
            ]
          };
        };
        normalizeValue(value, callback, CustomWidgetName.countBarChart);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const card = document.createElement(TagName.LfCard);
    const chart = {};
    const chip = {};
    card.classList.add(CountBarChartCSS.Widget);
    card.lfLayout = "keywords";
    content.classList.add(CountBarChartCSS.Content);
    content.appendChild(card);
    wrapper.appendChild(content);
    const options = countBarChartFactory.options(wrapper);
    STATE$8.set(wrapper, { card, datasets: { chart, chip }, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.countBarChart, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$8
  //#endregion
};
const EV_HANDLERS$5 = {
  //#region List handler
  list: (state, e2) => {
    const { eventType, node } = e2.detail;
    const comfyNode = state.node;
    const strValue = node ? String(node.value).valueOf() : "";
    if (eventType === "click" && strValue) {
      const boolW = getWidget(comfyNode, ComfyWidgetName.boolean);
      const comboW = getWidget(comfyNode, ComfyWidgetName.combo);
      const customtextW = getWidget(comfyNode, ComfyWidgetName.customtext);
      const floatW = getWidget(comfyNode, ComfyWidgetName.float);
      const intW = getWidget(comfyNode, ComfyWidgetName.integer);
      const numberW = getWidget(comfyNode, ComfyWidgetName.number);
      const seedW = getWidget(comfyNode, ComfyWidgetName.seed);
      const stringW = getWidget(comfyNode, ComfyWidgetName.string);
      const textW = getWidget(comfyNode, ComfyWidgetName.text);
      const toggleW = getWidget(comfyNode, ComfyWidgetName.toggle);
      switch (comfyNode.comfyClass) {
        case NodeName.boolean:
          if (boolW) {
            boolW.value = String(node.value).toLowerCase() === "true" ? true : false;
          } else if (toggleW) {
            toggleW.value = String(node.value).toLowerCase() === "true" ? true : false;
          }
          break;
        case NodeName.float:
          if (numberW) {
            numberW.value = Number(node.value).valueOf();
          } else if (intW) {
            floatW.value = Number(node.value).valueOf();
          }
          break;
        case NodeName.integer:
        case NodeName.sequentialSeedsGenerator:
          if (numberW) {
            numberW.value = Number(node.value).valueOf();
          } else if (intW) {
            intW.value = Number(node.value).valueOf();
          } else if (seedW) {
            seedW.value = Number(node.value).valueOf();
          }
          break;
        case NodeName.samplerSelector:
        case NodeName.schedulerSelector:
        case NodeName.upscaleModelSelector:
        case NodeName.vaeSelector:
          comboW.value = node.value;
          break;
        case NodeName.string:
          if (stringW) {
            stringW.options.setValue(node.value);
          } else if (customtextW) {
            customtextW.options.setValue(node.value);
          } else if (textW) {
            textW.value = node.value;
          }
          break;
      }
    }
  }
  //#endregion
};
var HistoryCSS;
(function(HistoryCSS2) {
  HistoryCSS2["Content"] = "lf-history";
  HistoryCSS2["Widget"] = "lf-history__widget";
})(HistoryCSS || (HistoryCSS = {}));
const STATE$7 = /* @__PURE__ */ new WeakMap();
const historyFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$7.get(wrapper),
      getValue() {
        const { list: list2 } = STATE$7.get(wrapper);
        return (list2 == null ? void 0 : list2.lfDataset) || {};
      },
      setValue(value) {
        const { list: list2 } = STATE$7.get(wrapper);
        const callback = (_2, u2) => {
          list2.lfDataset = u2.parsedJson || {};
        };
        normalizeValue(value, callback, CustomWidgetName.history);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const list2 = document.createElement(TagName.LfList);
    list2.classList.add(HistoryCSS.Widget);
    list2.lfEmpty = "History is empty!";
    list2.lfEnableDeletions = true;
    switch (node.comfyClass) {
      case NodeName.loadFileOnce:
        break;
      default:
        list2.lfSelectable = true;
        break;
    }
    list2.addEventListener(LfEventName.LfList, (e2) => EV_HANDLERS$5.list(STATE$7.get(wrapper), e2));
    content.classList.add(HistoryCSS.Content);
    content.appendChild(list2);
    wrapper.appendChild(content);
    const options = historyFactory.options(wrapper);
    STATE$7.set(wrapper, { list: list2, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.history, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$7
  //#endregion
};
const EV_HANDLERS$4 = {
  //#region Masonry handler
  masonry: (state, e2) => {
    var _a, _b;
    const { comp, eventType, originalEvent, selectedShape } = e2.detail;
    if (!comp.lfSelectable) {
      return;
    }
    switch (eventType) {
      case "lf-event":
        const { eventType: eventType2 } = originalEvent.detail;
        switch (eventType2) {
          case "click":
            const v2 = ((_a = selectedShape.shape) == null ? void 0 : _a.value) || ((_b = selectedShape.shape) == null ? void 0 : _b.lfValue);
            state.selected.index = selectedShape.index;
            state.selected.name = v2 ? String(v2).valueOf() : "";
            break;
        }
        break;
    }
  }
  //#endregion
};
var MasonryCSS;
(function(MasonryCSS2) {
  MasonryCSS2["Content"] = "lf-masonry";
  MasonryCSS2["Slot"] = "lf-masonry__slot";
  MasonryCSS2["Widget"] = "lf-masonry__widget";
})(MasonryCSS || (MasonryCSS = {}));
const STATE$6 = /* @__PURE__ */ new WeakMap();
const masonryFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$6.get(wrapper),
      getValue() {
        const { masonry, selected } = STATE$6.get(wrapper);
        const { index, name } = selected;
        return {
          columns: (masonry == null ? void 0 : masonry.lfColumns) || 3,
          dataset: (masonry == null ? void 0 : masonry.lfDataset) || {},
          index: isValidNumber(index) ? index : NaN,
          name: name || "",
          view: (masonry == null ? void 0 : masonry.lfView) || "main"
        };
      },
      setValue(value) {
        const callback = (_2, u2) => {
          const { masonry, selected } = STATE$6.get(wrapper);
          const { columns, dataset, index, name, view, slot_map } = u2.parsedJson;
          if (columns) {
            masonry.lfColumns = columns;
          }
          if (dataset) {
            masonry.lfDataset = dataset || {};
          }
          if (view) {
            masonry.lfView = view;
          }
          if (isValidNumber(index)) {
            selected.index = index;
            selected.name = name || "";
            masonry.setSelectedShape(index);
          }
          if (slot_map && typeof slot_map === "object" && Object.keys(slot_map).length > 0) {
            while (masonry.firstChild) {
              masonry.removeChild(masonry.firstChild);
            }
            for (const key in slot_map) {
              if (!Object.hasOwn(slot_map, key))
                continue;
              const element = slot_map[key];
              const div = document.createElement("div");
              div.innerHTML = element;
              div.setAttribute("slot", key);
              div.classList.add(MasonryCSS.Slot);
              masonry.appendChild(div);
            }
            masonry.lfShape = "slot";
          }
        };
        normalizeValue(value, callback, CustomWidgetName.masonry);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const masonry = document.createElement(TagName.LfMasonry);
    masonry.classList.add(MasonryCSS.Widget);
    masonry.addEventListener(LfEventName.LfMasonry, (e2) => EV_HANDLERS$4.masonry(STATE$6.get(wrapper), e2));
    masonry.lfActions = true;
    masonry.lfColumns = 3;
    switch (node.comfyClass) {
      case NodeName.loadImages:
        masonry.lfSelectable = true;
        break;
    }
    content.classList.add(MasonryCSS.Content);
    content.appendChild(masonry);
    wrapper.appendChild(content);
    const options = masonryFactory.options(wrapper);
    STATE$6.set(wrapper, { masonry, node, selected: { index: NaN, name: "" }, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.masonry, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$6
  //#endregion
};
const PLACEHOLDER_MESSAGE = `The setup of this node must be done client-side. Use either <strong>LF_WriteJSON</strong> or <strong>LF_DisplayJSON</strong>
to connect as input a valid JSON dataset. Check the repository's workflows to see a 
<a target="_blank" href="https://github.com/lucafoscili/lucafoscili/blob/7cd0e072cb790ff2e921d6db0b16027d1dea0545/lf-nodes/workflows/Flux%20%2B%20LLM%20Character%20manager.json">working example here.</a>.`;
const EV_HANDLERS$3 = {
  //#region Messenger handler
  messenger: (state, e2) => {
    const { eventType, config: config2 } = e2.detail;
    switch (eventType) {
      case "save":
        if (config2 && typeof config2 === "object") {
          state.config = config2;
        }
        break;
    }
  }
  //#endregion
};
const STATE$5 = /* @__PURE__ */ new WeakMap();
const messengerFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$5.get(wrapper),
      getValue() {
        const { config: config2, elements } = STATE$5.get(wrapper);
        const { messenger } = elements;
        return {
          dataset: messenger.lfDataset || {},
          config: config2
        };
      },
      setValue(value) {
        const state = STATE$5.get(wrapper);
        const { elements } = state;
        const { messenger, placeholder } = elements;
        const callback = (_2, u2) => {
          const { config: config2, dataset } = u2.parsedJson;
          messenger.lfDataset = dataset;
          if (isValidObject(config2)) {
            messenger.lfValue = config2;
            state.config = config2;
          }
          placeholder.classList.add(MessengerCSS.PlaceholderHidden);
        };
        const onException = () => {
          placeholder.classList.remove(MessengerCSS.PlaceholderHidden);
        };
        normalizeValue(value, callback, CustomWidgetName.messenger, onException);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const placeholder = document.createElement(TagName.Div);
    const messenger = document.createElement(TagName.LfMessenger);
    content.classList.add(MessengerCSS.Content);
    messenger.classList.add(MessengerCSS.Widget);
    placeholder.classList.add(MessengerCSS.Placeholder);
    placeholder.innerHTML = PLACEHOLDER_MESSAGE;
    messenger.addEventListener(LfEventName.LfMessenger, (e2) => EV_HANDLERS$3.messenger(STATE$5.get(wrapper), e2));
    content.appendChild(placeholder);
    content.appendChild(messenger);
    wrapper.appendChild(content);
    const options = messengerFactory.options(wrapper);
    STATE$5.set(wrapper, { config: null, elements: { messenger, placeholder }, node, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.messenger, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$5
  //#endregion
};
var ProgressbarCSS;
(function(ProgressbarCSS2) {
  ProgressbarCSS2["Content"] = "lf-progressbar";
})(ProgressbarCSS || (ProgressbarCSS = {}));
var ProgressbarLabels;
(function(ProgressbarLabels2) {
  ProgressbarLabels2["ArrowRight"] = "→";
  ProgressbarLabels2["ArrowUp"] = "↑";
  ProgressbarLabels2["Fallback"] = "N/A";
  ProgressbarLabels2["False"] = "false";
  ProgressbarLabels2["True"] = "true";
})(ProgressbarLabels || (ProgressbarLabels = {}));
const STATE$4 = /* @__PURE__ */ new WeakMap();
const progressbarFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$4.get(wrapper),
      getValue() {
        const { progressbar } = STATE$4.get(wrapper);
        return {
          bool: progressbar.lfLabel === "true" ? true : false,
          roll: progressbar.lfValue || 0
        };
      },
      setValue(value) {
        const { node, progressbar } = STATE$4.get(wrapper);
        const callback = (_2, u2) => {
          const { bool, roll } = u2.parsedJson;
          const isFalse = !!(bool === false);
          const isTrue = !!(bool === true);
          switch (node.comfyClass) {
            case NodeName.resolutionSwitcher:
              if (isTrue) {
                progressbar.lfLabel = ProgressbarLabels.ArrowRight;
                progressbar.lfUiState = "primary";
              } else if (isFalse) {
                progressbar.lfLabel = ProgressbarLabels.ArrowUp;
                progressbar.lfUiState = "secondary";
              } else {
                progressbar.lfLabel = ProgressbarLabels.Fallback;
                progressbar.lfUiState = "disabled";
              }
              break;
            default:
              if (isTrue) {
                progressbar.lfLabel = ProgressbarLabels.True;
                progressbar.lfUiState = "success";
              } else if (isFalse) {
                progressbar.lfLabel = ProgressbarLabels.False;
                progressbar.lfUiState = "danger";
              } else {
                progressbar.lfLabel = ProgressbarLabels.Fallback;
                progressbar.lfUiState = "disabled";
              }
              break;
          }
          progressbar.title = roll ? "Actual roll: " + roll.toString() : "";
          progressbar.lfValue = roll || 100;
        };
        normalizeValue(value, callback, CustomWidgetName.progressbar);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const progressbar = document.createElement(TagName.LfProgressbar);
    progressbar.lfIsRadial = true;
    progressbar.lfLabel = ProgressbarLabels.Fallback;
    content.classList.add(ProgressbarCSS.Content);
    content.appendChild(progressbar);
    wrapper.appendChild(content);
    const options = progressbarFactory.options(wrapper);
    STATE$4.set(wrapper, { node, progressbar, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.progressbar, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$4
  //#endregion
};
const EV_HANDLERS$2 = {
  //#region Tabbar handler
  tabbar: (state, e2) => {
    const { eventType, node } = e2.detail;
    const { elements } = state;
    const { chart } = elements;
    switch (eventType) {
      case "click":
        switch (state.node.comfyClass) {
          case NodeName.usageStatistics:
            chart.lfDataset = getLfManager().getCachedDatasets().usage[node.id];
            break;
          default:
            chart.lfDataset = node.cells.lfChart.lfDataset;
            break;
        }
        break;
    }
  },
  //#endregion
  //#region Textfield handler
  textfield: (state, e2) => {
    const { eventType, value } = e2.detail;
    switch (eventType) {
      case "change":
        state.directory = value;
        apiCall(state);
        break;
    }
  }
  //#endregion
};
const apiCall = async (state) => {
  const { directory, elements, selected, type } = state;
  const { chart, tabbar, textfield } = elements;
  getApiRoutes().analytics.get(directory, type).then((r2) => {
    if (r2.status === "success") {
      if ((r2 == null ? void 0 : r2.data) && Object.entries(r2.data).length > 0) {
        const firstKey = selected || Object.keys(r2.data)[0];
        chart.lfDataset = r2.data[firstKey];
        tabbar.lfDataset = prepareTabbarDataset(r2.data);
        requestAnimationFrame(async () => {
          if (directory !== await textfield.getValue()) {
            textfield.setValue(directory);
          }
          tabbar.setValue(0);
        });
      } else {
        getLfManager().log("Analytics not found.", { r: r2 }, LogSeverity.Info);
      }
    }
  });
};
const prepareTabbarDataset = (data) => {
  var _a;
  const dataset = { nodes: [] };
  for (const filename in data) {
    if (Object.prototype.hasOwnProperty.call(data, filename)) {
      const node = {
        cells: { lfChart: { lfDataset: data[filename], shape: "chart", value: "" } },
        id: filename,
        value: ((_a = filename.split("_")) == null ? void 0 : _a[0]) || filename
      };
      dataset.nodes.push(node);
    }
  }
  return dataset;
};
var TabBarChartCSS;
(function(TabBarChartCSS2) {
  TabBarChartCSS2["Content"] = "lf-tabbarchart";
  TabBarChartCSS2["Directory"] = "lf-tabbarchart__directory";
  TabBarChartCSS2["DirectoryHidden"] = "lf-tabbarchart__directory--hidden";
  TabBarChartCSS2["Grid"] = "lf-tabbarchart__grid";
  TabBarChartCSS2["GridNoDirectory"] = "lf-tabbarchart__grid--no-directory";
  TabBarChartCSS2["Spinner"] = "lf-tabbarchart__spinner";
  TabBarChartCSS2["Tabbar"] = "lf-tabbarchart__tabbar";
})(TabBarChartCSS || (TabBarChartCSS = {}));
var TabBarChartColors;
(function(TabBarChartColors2) {
  TabBarChartColors2["Blue"] = "blue";
  TabBarChartColors2["Green"] = "green";
  TabBarChartColors2["Red"] = "red";
})(TabBarChartColors || (TabBarChartColors = {}));
var TabBarChartIds;
(function(TabBarChartIds2) {
  TabBarChartIds2["Blue"] = "blue";
  TabBarChartIds2["Counter"] = "counter";
  TabBarChartIds2["Green"] = "green";
  TabBarChartIds2["Intensity"] = "intensity";
  TabBarChartIds2["Name"] = "name";
  TabBarChartIds2["Red"] = "red";
})(TabBarChartIds || (TabBarChartIds = {}));
const STATE$3 = /* @__PURE__ */ new WeakMap();
const tabBarChartFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$3.get(wrapper),
      getValue: () => {
        const { directory, node } = STATE$3.get(wrapper);
        switch (node.comfyClass) {
          case NodeName.usageStatistics:
            return { directory: directory || "" };
          default:
            return {};
        }
      },
      setValue: (value) => {
        const state = STATE$3.get(wrapper);
        const { chart, tabbar } = state.elements;
        const callback = (_2, u2) => {
          const parsedValue = u2.parsedJson;
          switch (state.node.comfyClass) {
            case NodeName.usageStatistics:
              state.directory = parsedValue.directory;
              apiCall(state);
              break;
            default:
              for (const key in parsedValue) {
                const dataset = parsedValue[key];
                chart.lfDataset = dataset || {};
                tabbar.lfDataset = prepareTabbarDataset(parsedValue) || {};
                requestAnimationFrame(async () => tabbar.setValue(0));
              }
              break;
          }
        };
        normalizeValue(value, callback, CustomWidgetName.tabBarChart);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const grid = document.createElement(TagName.Div);
    const textfield = document.createElement(TagName.LfTextfield);
    const chart = document.createElement(TagName.LfChart);
    const tabbar = document.createElement(TagName.LfTabbar);
    let type;
    switch (node.comfyClass) {
      case NodeName.colorAnalysis:
        chart.lfAxis = [TabBarChartIds.Intensity];
        chart.lfColors = [TabBarChartColors.Red, TabBarChartColors.Green, TabBarChartColors.Blue];
        chart.lfSeries = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfTypes = ["scatter"];
        grid.classList.add(TabBarChartCSS.GridNoDirectory);
        textfield.classList.add(TabBarChartCSS.DirectoryHidden);
        break;
      case NodeName.imageHistogram:
      case NodeName.lutGeneration:
        chart.lfAxis = [TabBarChartIds.Intensity];
        chart.lfColors = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfSeries = [TabBarChartIds.Red, TabBarChartIds.Green, TabBarChartIds.Blue];
        chart.lfTypes = ["area"];
        grid.classList.add(TabBarChartCSS.GridNoDirectory);
        textfield.classList.add(TabBarChartCSS.DirectoryHidden);
        break;
      case NodeName.usageStatistics:
        type = "usage";
        chart.lfAxis = [TabBarChartIds.Name];
        chart.lfSeries = [TabBarChartIds.Counter, TabBarChartIds.Counter];
        chart.lfTypes = ["area"];
        break;
    }
    tabbar.classList.add(TabBarChartCSS.Tabbar);
    tabbar.lfValue = null;
    tabbar.addEventListener(LfEventName.LfTabbar, (e2) => EV_HANDLERS$2.tabbar(STATE$3.get(wrapper), e2));
    textfield.classList.add(TabBarChartCSS.Directory);
    textfield.lfIcon = "folder";
    textfield.lfLabel = "Directory";
    textfield.lfStyling = "flat";
    textfield.addEventListener(LfEventName.LfTextfield, (e2) => EV_HANDLERS$2.textfield(STATE$3.get(wrapper), e2));
    grid.classList.add(TabBarChartCSS.Grid);
    grid.appendChild(textfield);
    grid.appendChild(tabbar);
    grid.appendChild(chart);
    content.classList.add(TabBarChartCSS.Content);
    content.appendChild(grid);
    wrapper.appendChild(content);
    const options = tabBarChartFactory.options(wrapper);
    STATE$3.set(wrapper, {
      directory: "",
      elements: { chart, tabbar, textfield },
      node,
      selected: "",
      type,
      wrapper
    });
    return { widget: createDOMWidget(CustomWidgetName.tabBarChart, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$3
  //#endregion
};
var TextareaCSS;
(function(TextareaCSS2) {
  TextareaCSS2["Content"] = "lf-textarea";
  TextareaCSS2["Widget"] = "lf-textarea__widget";
  TextareaCSS2["WidgetError"] = "lf-textarea__widget--error";
})(TextareaCSS || (TextareaCSS = {}));
let VALIDATION_TIMEOUT;
const EV_HANDLERS$1 = {
  //#region Input handler
  input: (e2) => {
    const textarea = e2.currentTarget;
    const startValidationTimer = () => {
      const validateAndFormatJSON = async () => {
        try {
          const jsonObject = JSON.parse(textarea.value);
          const formattedJson = JSON.stringify(jsonObject, null, 2);
          if (formattedJson !== "{}") {
            textarea.title = "";
            textarea.value = formattedJson;
            textarea.classList.remove(TextareaCSS.WidgetError);
          }
        } catch (error2) {
          getLfManager().log("Error parsing JSON", { error: error2 }, LogSeverity.Warning);
          textarea.classList.add(TextareaCSS.WidgetError);
          textarea.title = error2;
        }
      };
      VALIDATION_TIMEOUT = setTimeout(validateAndFormatJSON, 2500);
    };
    clearTimeout(VALIDATION_TIMEOUT);
    startValidationTimer();
  }
  //#endregion
};
const STATE$2 = /* @__PURE__ */ new WeakMap();
const textareaFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: false,
      getState: () => STATE$2.get(wrapper),
      getValue() {
        const { textarea } = STATE$2.get(wrapper);
        try {
          return (textarea == null ? void 0 : textarea.value) || "{}";
        } catch (error2) {
          return error2;
        }
      },
      setValue(value) {
        const { textarea } = STATE$2.get(wrapper);
        const callback = (_2, u2) => {
          const parsedJson = u2.parsedJson;
          textarea.value = JSON.stringify(parsedJson, null, 2) || "{}";
        };
        normalizeValue(value, callback, CustomWidgetName.textarea);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const textarea = document.createElement(TagName.Textarea);
    content.classList.add(TextareaCSS.Content);
    content.appendChild(textarea);
    textarea.classList.add(TextareaCSS.Widget);
    textarea.addEventListener("input", EV_HANDLERS$1.input);
    wrapper.appendChild(content);
    const options = textareaFactory.options(wrapper);
    STATE$2.set(wrapper, { node, textarea, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.textarea, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$2
  //#endregion
};
var TreeCSS;
(function(TreeCSS2) {
  TreeCSS2["Content"] = "lf-tree";
  TreeCSS2["Widget"] = "lf-tree__widget";
})(TreeCSS || (TreeCSS = {}));
const STATE$1 = /* @__PURE__ */ new WeakMap();
const treeFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE$1.get(wrapper),
      getValue() {
        const { tree } = STATE$1.get(wrapper);
        return tree.lfDataset || {};
      },
      setValue(value) {
        const { tree } = STATE$1.get(wrapper);
        const callback = (_2, u2) => {
          tree.lfDataset = u2.parsedJson || {};
        };
        normalizeValue(value, callback, CustomWidgetName.tree);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const tree = document.createElement(TagName.LfTree);
    switch (node.comfyClass) {
      case NodeName.isLandscape:
        tree.lfAccordionLayout = false;
        tree.lfSelectable = false;
        break;
      default:
        tree.lfAccordionLayout = true;
        tree.lfSelectable = false;
        break;
    }
    tree.classList.add(TreeCSS.Widget);
    content.classList.add(TreeCSS.Content);
    content.appendChild(tree);
    wrapper.appendChild(content);
    const options = treeFactory.options(wrapper);
    STATE$1.set(wrapper, { node, tree, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.tree, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE$1
  //#endregion
};
const EV_HANDLERS = {
  //#region Upload handler
  upload: async (state, e2) => {
    var _a;
    const { eventType, selectedFiles } = e2.detail;
    const { upload } = state;
    switch (eventType) {
      case "delete":
        state.files = Array.from(selectedFiles, (file) => file.name).join(";") || "";
        return;
      case "upload":
        const fileNames = /* @__PURE__ */ new Set();
        for (let index = 0; index < selectedFiles.length; index++) {
          const file = selectedFiles[index];
          try {
            const body = new FormData();
            const i2 = file.webkitRelativePath.lastIndexOf("/");
            const subfolder = file.webkitRelativePath.slice(0, i2 + 1);
            const new_file = new File([file], file.name, {
              type: file.type,
              lastModified: file.lastModified
            });
            body.append("image", new_file);
            if (i2 > 0) {
              body.append("subfolder", subfolder);
            }
            const resp = await getApiRoutes().comfy.upload(body);
            if (resp.status === 200 || resp.status === 201) {
              getLfManager().log("POST result", { json: resp.json }, LogSeverity.Success);
              fileNames.add(file.name);
              upload.dataset.files = upload.dataset.files + ";" + file.name;
            } else {
              getLfManager().log("POST failed", { statusText: resp.statusText }, LogSeverity.Error);
            }
          } catch (error2) {
            alert(`Upload failed: ${error2}`);
          }
        }
        state.files = ((_a = Array.from(fileNames)) == null ? void 0 : _a.join(";")) || "";
        break;
    }
  }
  //#endregion
};
var UploadCSS;
(function(UploadCSS2) {
  UploadCSS2["Content"] = "lf-upload";
  UploadCSS2["Widget"] = "lf-upload__widget";
})(UploadCSS || (UploadCSS = {}));
const STATE = /* @__PURE__ */ new WeakMap();
const uploadFactory = {
  //#region Options
  options: (wrapper) => {
    return {
      hideOnZoom: true,
      getState: () => STATE.get(wrapper),
      getValue() {
        const { files } = STATE.get(wrapper);
        return files || "";
      },
      setValue(value) {
        const state = STATE.get(wrapper);
        const callback = (v2) => {
          state.files = v2;
        };
        normalizeValue(value, callback, CustomWidgetName.upload);
      }
    };
  },
  //#endregion
  //#region Render
  render: (node) => {
    const wrapper = document.createElement(TagName.Div);
    const content = document.createElement(TagName.Div);
    const upload = document.createElement(TagName.LfUpload);
    upload.classList.add(UploadCSS.Widget);
    upload.addEventListener(LfEventName.LfUpload, (e2) => EV_HANDLERS.upload(STATE.get(wrapper), e2));
    content.classList.add(UploadCSS.Content);
    content.appendChild(upload);
    wrapper.appendChild(content);
    const options = uploadFactory.options(wrapper);
    STATE.set(wrapper, { files: "", node, upload, wrapper });
    return { widget: createDOMWidget(CustomWidgetName.upload, wrapper, node, options) };
  },
  //#endregion
  //#region State
  state: STATE
  //#endregion
};
var __classPrivateFieldGet$1 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LFWidgets_FACTORIES, _LFWidgets_notifications;
class LFWidgets {
  constructor() {
    _LFWidgets_FACTORIES.set(this, {
      [CustomWidgetName.card]: cardFactory,
      [CustomWidgetName.carousel]: carouselFactory,
      [CustomWidgetName.cardsWithChip]: cardsWithChipFactory,
      [CustomWidgetName.chat]: chatFactory,
      [CustomWidgetName.chip]: chipFactory,
      [CustomWidgetName.code]: codeFactory,
      [CustomWidgetName.compare]: compareFactory,
      [CustomWidgetName.controlPanel]: controlPanelFactory,
      [CustomWidgetName.countBarChart]: countBarChartFactory,
      [CustomWidgetName.history]: historyFactory,
      [CustomWidgetName.imageEditor]: imageEditorFactory,
      [CustomWidgetName.masonry]: masonryFactory,
      [CustomWidgetName.messenger]: messengerFactory,
      [CustomWidgetName.progressbar]: progressbarFactory,
      [CustomWidgetName.tabBarChart]: tabBarChartFactory,
      [CustomWidgetName.textarea]: textareaFactory,
      [CustomWidgetName.tree]: treeFactory,
      [CustomWidgetName.upload]: uploadFactory
    });
    this.render = (name) => __classPrivateFieldGet$1(this, _LFWidgets_FACTORIES, "f")[name].render;
    this.decorators = {
      card: (payload, widget) => {
        const { apiFlags, datasets, hashes, paths, chip } = payload;
        cardPlaceholders(widget, 1);
        const value = {
          props: [],
          chip
        };
        const models = [];
        for (let index = 0; index < (datasets == null ? void 0 : datasets.length); index++) {
          const apiFlag = apiFlags[index];
          const dataset = datasets[index];
          const hash = hashes[index];
          const path = paths[index];
          models.push({ dataset, hash, path, apiFlag });
        }
        apiCall$1(models).then((r2) => {
          for (let index = 0; index < r2.length; index++) {
            const cardProps = r2[index];
            if (cardProps.lfDataset) {
              value.props.push(cardProps);
            } else {
              value.props.push({
                ...cardProps,
                lfDataset: models[index].dataset
              });
            }
          }
          widget.options.setValue(JSON.stringify(value));
          getApiRoutes().comfy.redraw();
        });
      }
    };
    this.onEvent = (name, event, widgets) => {
      const lfManager = getLfManager();
      const payload = event.detail;
      const id = resolveNodeId(payload);
      if (!id) {
        lfManager.log(`Event '${name}' missing node identifier; present keys: ${Object.keys(payload).join(", ")}`, { payload, name }, LogSeverity.Warning);
        return;
      }
      const node = lfManager.getApiRoutes().comfy.getNodeById(id);
      if (node) {
        lfManager.log(`${node.comfyClass} (#${node.id}): event '${name}' fired`, { payload, node }, LogSeverity.Info);
        switch (name) {
          case NodeName.notify:
            if ("action" in payload) {
              __classPrivateFieldGet$1(this, _LFWidgets_notifications, "f").show(payload);
            }
            break;
        }
        for (let index = 0; index < widgets.length; index++) {
          const widgetName = widgets[index];
          const widget = getCustomWidget(node, widgetName);
          switch (widgetName) {
            case CustomWidgetName.imageEditor:
              switch (name) {
                case NodeName.imagesEditingBreakpoint:
                  if (widget && "value" in payload) {
                    const { value } = payload;
                    lfManager.log(`Initiating JSON data fetch for editing breakpoint from path: ${value}`, { widget, value });
                    getApiRoutes().json.get(value).then((r2) => {
                      if (r2.status === LogSeverity.Success) {
                        lfManager.log("JSON data fetched successfully for image editing breakpoint.", { data: r2.data }, LogSeverity.Success);
                        widget.options.setValue(JSON.stringify(r2.data));
                      } else {
                        lfManager.log(`Failed to fetch JSON data: ${r2.message}`, { response: r2 }, LogSeverity.Error);
                      }
                    }).catch((error2) => {
                      lfManager.log(`Error during JSON fetch for editing breakpoint: ${error2.toString()}`, { error: error2 }, LogSeverity.Error);
                    });
                  } else {
                    lfManager.log(`Image editor widget handling failed: missing 'widget' or 'value' in payload.`, { widget, payload }, LogSeverity.Warning);
                  }
                  break;
                default:
                  if (widget && "dataset" in payload) {
                    const { dataset } = payload;
                    widget.options.setValue(JSON.stringify(dataset));
                  }
                  break;
              }
              break;
            case CustomWidgetName.card:
            case CustomWidgetName.cardsWithChip:
              if (widget && "apiFlags" in payload) {
                this.decorators.card(payload, widget);
              }
              break;
            case CustomWidgetName.code:
            case CustomWidgetName.upload:
              if (widget && "value" in payload) {
                const { value } = payload;
                widget.options.setValue(value);
              }
              break;
            case CustomWidgetName.masonry:
            case CustomWidgetName.progressbar:
              if (widget) {
                widget.options.setValue(JSON.stringify(payload));
              }
              break;
            case CustomWidgetName.countBarChart:
            case CustomWidgetName.tabBarChart:
              if (widget && "datasets" in payload) {
                const { datasets } = payload;
                widget.options.setValue(JSON.stringify(datasets));
              }
              break;
            default:
              if (widget && "dataset" in payload) {
                const { dataset } = payload;
                widget.options.setValue(JSON.stringify(dataset));
              }
              break;
          }
        }
        lfManager.getApiRoutes().comfy.redraw();
      } else {
        lfManager.log(`Event '${name}' was fired but its related node (#${id}) wasn't found in the graph! Skipping handling the event.`, { payload, name }, LogSeverity.Warning);
      }
    };
    _LFWidgets_notifications.set(this, {
      decorate: (payload) => {
        const { action, image: image2, message, silent, tag, title } = payload;
        const icon = action === "focus tab" ? "photo-search" : action === "interrupt" ? "x" : action === "interrupt and queue" ? "refresh" : action === "queue prompt" ? "stack-push" : "";
        const options = {
          body: message,
          icon: icon ? window.location.href + `extensions/lf-nodes/assets/svg/${icon}.svg` : void 0,
          requireInteraction: action === "none" ? false : true,
          silent,
          tag
        };
        if ("image" in Notification.prototype && image2) {
          options.image = image2;
        }
        if (Notification.permission === "granted") {
          const notification = new Notification(title, options);
          notification.addEventListener("click", () => {
            const lfManager = getLfManager();
            const routes = getApiRoutes().comfy;
            switch (action) {
              case "focus tab":
                window.focus();
                break;
              case "interrupt":
                routes.interrupt();
                break;
              case "interrupt and queue":
                routes.interrupt();
                routes.queuePrompt();
                lfManager.log("New prompt queued from notification after interrupting.", {}, LogSeverity.Success);
                break;
              case "queue prompt":
                routes.queuePrompt();
                lfManager.log("New prompt queued from notification.", {}, LogSeverity.Success);
                break;
            }
          });
        }
      },
      show: (payload) => {
        const lfManager = getLfManager();
        if (Notification.permission !== "granted") {
          Notification.requestPermission().then((permission) => {
            if (permission === "granted") {
              __classPrivateFieldGet$1(this, _LFWidgets_notifications, "f").decorate(payload);
            } else {
              lfManager.log("Notification permission denied.", {}, LogSeverity.Warning);
            }
          });
        } else {
          __classPrivateFieldGet$1(this, _LFWidgets_notifications, "f").decorate(payload);
        }
      }
    });
  }
}
_LFWidgets_FACTORIES = /* @__PURE__ */ new WeakMap(), _LFWidgets_notifications = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldGet = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var __classPrivateFieldSet = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var _LFManager_APIS, _LFManager_AUTOMATIC_BACKUP, _LFManager_BACKUP_RETENTION, _LFManager_CACHED_DATASETS, _LFManager_DEBUG, _LFManager_DEBUG_ARTICLE, _LFManager_DEBUG_DATASET, _LFManager_INITIALIZED, _LFManager_LATEST_RELEASE, _LFManager_MANAGERS, _LFManager_SYSTEM_TIMEOUT;
class LFManager {
  constructor() {
    _LFManager_APIS.set(this, {
      analytics: ANALYTICS_API,
      backup: BACKUP_API,
      comfy: COMFY_API,
      models: MODELS_API,
      github: GITHUB_API,
      image: IMAGE_API,
      json: JSON_API,
      metadata: METADATA_API,
      preview: PREVIEW_API,
      system: SYSTEM_API
    });
    _LFManager_AUTOMATIC_BACKUP.set(this, true);
    _LFManager_BACKUP_RETENTION.set(this, 14);
    _LFManager_CACHED_DATASETS.set(this, {
      usage: null
    });
    _LFManager_DEBUG.set(this, false);
    _LFManager_DEBUG_ARTICLE.set(this, void 0);
    _LFManager_DEBUG_DATASET.set(this, void 0);
    _LFManager_INITIALIZED.set(this, false);
    _LFManager_LATEST_RELEASE.set(this, void 0);
    _LFManager_MANAGERS.set(this, {});
    _LFManager_SYSTEM_TIMEOUT.set(this, 0);
    const assetsUrl = window.location.href + "extensions/lf-nodes/assets";
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework = getLfFramework();
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework.assets.set(assetsUrl);
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework.theme.set("dark");
    this.log("LfFramework ready!", { lfFramework: __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework }, LogSeverity.Success);
    const link2 = document.createElement("link");
    link2.dataset.filename = "_index";
    link2.rel = "stylesheet";
    link2.type = "text/css";
    link2.href = `extensions/lf-nodes/css/_index.css`;
    document.head.appendChild(link2);
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").tooltip = new LFTooltip();
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").widgets = new LFWidgets();
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").nodes = new LFNodes();
  }
  //#region Initialize
  initialize() {
    installLFBeforeFreeHooks(api, {
      logger: (m2, a2, s2) => this.log(m2, a2, s2)
    });
    installLFRefreshNodeHook(app, {
      logger: (m2, a2, s2) => this.log(m2, a2, s2)
    });
    installLFInterruptHook(api, {
      logger: (m2, a2, s2) => this.log(m2, a2, s2)
    });
    __classPrivateFieldGet(this, _LFManager_APIS, "f").github.getLatestRelease().then((r2) => __classPrivateFieldSet(this, _LFManager_LATEST_RELEASE, (r2 == null ? void 0 : r2.data) || null, "f"));
    if (__classPrivateFieldGet(this, _LFManager_INITIALIZED, "f")) {
      this.log("Attempt to initialize LFManager when already ready!", { LFManager: this }, LogSeverity.Warning);
      return;
    }
    for (const key in NodeName) {
      if (Object.prototype.hasOwnProperty.call(NodeName, key)) {
        const name = NodeName[key];
        const eventName = this.getEventName(name);
        const widgets = NODE_WIDGET_MAP[name];
        const customWidgets = {};
        const callbacks = [];
        if (widgets.includes(CustomWidgetName.countBarChart) || widgets.includes(CustomWidgetName.tabBarChart)) {
          callbacks.push(onDrawBackground);
        }
        if (widgets.includes(CustomWidgetName.chip) || widgets.includes(CustomWidgetName.messenger)) {
          callbacks.push(onConnectionsChange);
        }
        callbacks.push(onNodeCreated);
        const extension = {
          name: "LFExt_" + name,
          async beforeRegisterNodeDef(node) {
            if (node.comfyClass === name) {
              callbacks.forEach((c2) => c2(node));
            }
          },
          getCustomWidgets: () => widgets.reduce((acc, widget) => {
            return {
              ...acc,
              [widget]: __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").widgets.render(widget)
            };
          }, customWidgets)
        };
        __classPrivateFieldGet(this, _LFManager_APIS, "f").comfy.register(extension);
        __classPrivateFieldGet(this, _LFManager_APIS, "f").comfy.event(eventName, (e2) => {
          __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").widgets.onEvent(name, e2, widgets);
        });
      }
    }
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").nodes.registerAll();
    __classPrivateFieldSet(this, _LFManager_INITIALIZED, true, "f");
  }
  //#endregion
  //#region Getters
  getApiRoutes() {
    return __classPrivateFieldGet(this, _LFManager_APIS, "f");
  }
  getCachedDatasets() {
    return __classPrivateFieldGet(this, _LFManager_CACHED_DATASETS, "f");
  }
  getDebugDataset() {
    return { article: __classPrivateFieldGet(this, _LFManager_DEBUG_ARTICLE, "f"), dataset: __classPrivateFieldGet(this, _LFManager_DEBUG_DATASET, "f") };
  }
  getEventName(node) {
    return node.toLowerCase().replace("_", "-");
  }
  getLatestRelease() {
    return __classPrivateFieldGet(this, _LFManager_LATEST_RELEASE, "f");
  }
  getManagers() {
    return __classPrivateFieldGet(this, _LFManager_MANAGERS, "f");
  }
  getPrefixedNode(nodeName) {
    return `✨ LF Nodes/${nodeName}`;
  }
  getBackupRetention() {
    return __classPrivateFieldGet(this, _LFManager_BACKUP_RETENTION, "f");
  }
  getSystemTimeout() {
    return __classPrivateFieldGet(this, _LFManager_SYSTEM_TIMEOUT, "f");
  }
  isBackupEnabled() {
    return __classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f");
  }
  isDebug() {
    return __classPrivateFieldGet(this, _LFManager_DEBUG, "f");
  }
  //#endregion
  //#region Log
  log(message, args, severity = LogSeverity.Info) {
    var _a;
    if (!__classPrivateFieldGet(this, _LFManager_DEBUG, "f")) {
      return;
    }
    let colorCode = "";
    switch (severity) {
      case "success":
        colorCode = "\x1B[32m";
        break;
      case "warning":
        colorCode = "\x1B[33m";
        break;
      case "error":
        colorCode = "\x1B[31m";
        break;
      default:
        colorCode = "\x1B[0m";
        break;
    }
    const italicCode = "\x1B[3m";
    const boldCode = "\x1B[1m";
    const resetColorCode = "\x1B[0m";
    const dot = "• LF Nodes •";
    if (__classPrivateFieldGet(this, _LFManager_DEBUG_DATASET, "f") && ((_a = __classPrivateFieldGet(this, _LFManager_DEBUG_ARTICLE, "f")) == null ? void 0 : _a.isConnected) && severity !== LogSeverity.Info) {
      const id = String(performance.now()).valueOf();
      const icon = severity === LogSeverity.Error ? "🔴 " : severity === LogSeverity.Success ? "🟢 " : severity === LogSeverity.Warning ? "🟠 " : "🔵 ";
      __classPrivateFieldGet(this, _LFManager_DEBUG_DATASET, "f").unshift({
        cssStyle: getLogStyle(),
        id,
        tagName: "pre",
        value: icon + message
      });
      __classPrivateFieldGet(this, _LFManager_DEBUG_ARTICLE, "f").refresh();
    }
    console.log(`${colorCode}${boldCode}${dot}${resetColorCode}${italicCode} ${message} ${resetColorCode}`, args);
  }
  //#endregion
  //#region Setters
  setBackupRetention(value) {
    if (typeof value === "number" && value >= 0) {
      __classPrivateFieldSet(this, _LFManager_BACKUP_RETENTION, Math.floor(value), "f");
      this.log(`Backup retention set to: ${__classPrivateFieldGet(this, _LFManager_BACKUP_RETENTION, "f")}`, { value }, LogSeverity.Info);
    }
    return __classPrivateFieldGet(this, _LFManager_BACKUP_RETENTION, "f");
  }
  setDebugDataset(article, dataset) {
    __classPrivateFieldSet(this, _LFManager_DEBUG_ARTICLE, article, "f");
    __classPrivateFieldSet(this, _LFManager_DEBUG_DATASET, dataset, "f");
    this.log("Debug dataset set!", { article, dataset }, LogSeverity.Info);
  }
  setSystemTimeout(value = 0) {
    if (typeof value === "number" && value >= 0) {
      __classPrivateFieldSet(this, _LFManager_SYSTEM_TIMEOUT, Math.floor(value), "f");
      this.log(`System timeout set to: ${value}`, { value }, LogSeverity.Info);
    }
  }
  toggleBackup(value) {
    if (value === false || value === true) {
      __classPrivateFieldSet(this, _LFManager_AUTOMATIC_BACKUP, value, "f");
    } else {
      __classPrivateFieldSet(this, _LFManager_AUTOMATIC_BACKUP, !__classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f"), "f");
    }
    this.log(`Automatic backup active: '${__classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f")}'`, { value }, LogSeverity.Warning);
    return __classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f");
  }
  toggleDebug(value) {
    if (value === false || value === true) {
      __classPrivateFieldSet(this, _LFManager_DEBUG, value, "f");
    } else {
      __classPrivateFieldSet(this, _LFManager_DEBUG, !__classPrivateFieldGet(this, _LFManager_DEBUG, "f"), "f");
    }
    this.log(`Debug active: '${__classPrivateFieldGet(this, _LFManager_DEBUG, "f")}'`, { value }, LogSeverity.Warning);
    return __classPrivateFieldGet(this, _LFManager_DEBUG, "f");
  }
}
_LFManager_APIS = /* @__PURE__ */ new WeakMap(), _LFManager_AUTOMATIC_BACKUP = /* @__PURE__ */ new WeakMap(), _LFManager_BACKUP_RETENTION = /* @__PURE__ */ new WeakMap(), _LFManager_CACHED_DATASETS = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG_ARTICLE = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG_DATASET = /* @__PURE__ */ new WeakMap(), _LFManager_INITIALIZED = /* @__PURE__ */ new WeakMap(), _LFManager_LATEST_RELEASE = /* @__PURE__ */ new WeakMap(), _LFManager_MANAGERS = /* @__PURE__ */ new WeakMap(), _LFManager_SYSTEM_TIMEOUT = /* @__PURE__ */ new WeakMap();
var LFFreeFlags;
(function(LFFreeFlags2) {
  LFFreeFlags2["PatchedFree"] = "_lf_patched_freeMemory";
  LFFreeFlags2["OriginalFreeRef"] = "_lf_original_freeMemory";
  LFFreeFlags2["PatchedFetch"] = "_lf_patched_fetchApi_free";
  LFFreeFlags2["InBeforeFree"] = "_lf_in_beforeFree";
})(LFFreeFlags || (LFFreeFlags = {}));
var LFInterruptFlags;
(function(LFInterruptFlags2) {
  LFInterruptFlags2["PatchedInterrupt"] = "_lf_patched_interrupt";
  LFInterruptFlags2["OriginalInterruptRef"] = "_lf_original_interrupt";
  LFInterruptFlags2["InBeforeInterrupt"] = "_lf_in_beforeInterrupt";
})(LFInterruptFlags || (LFInterruptFlags = {}));
var LFRefreshFlags;
(function(LFRefreshFlags2) {
  LFRefreshFlags2["PatchedRefresh"] = "_lf_patched_refreshComboInNodes";
  LFRefreshFlags2["OriginalRefreshRef"] = "_lf_original_refreshComboInNodes";
  LFRefreshFlags2["InBeforeRefresh"] = "_lf_in_beforeRefreshComboInNodes";
})(LFRefreshFlags || (LFRefreshFlags = {}));
const LF_MANAGER_SYMBOL_ID = "__LfManager__";
const LF_MANAGER_SYMBOL = Symbol.for(LF_MANAGER_SYMBOL_ID);
const DEFAULT_WIDGET_NAME = "ui_widget";
let timer;
const isButton = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-button";
};
const isImage = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-image";
};
const isMasonry = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-masonry";
};
const isTextfield = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-textfield";
};
const isTree = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-tree";
};
const isToggle = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-toggle";
};
const areJSONEqual = (a2, b2) => {
  return JSON.stringify(a2) === JSON.stringify(b2);
};
const isJSONLikeString = (value) => {
  if (typeof value !== "string")
    return false;
  const trimmed = value.trim();
  if (!(trimmed.startsWith("{") && trimmed.endsWith("}") || trimmed.startsWith("[") && trimmed.endsWith("]"))) {
    return false;
  }
  if (trimmed.startsWith("{")) {
    if (trimmed === "{}")
      return true;
    if (/".*"\s*:\s*.+/.test(trimmed))
      return true;
    return false;
  }
  if (trimmed.indexOf('"') !== -1)
    return true;
  const simpleArrayScalar = /^\[\s*(?:-?\d+(\.\d+)?|true|false|null)(\s*,\s*(?:-?\d+(\.\d+)?|true|false|null))*\s*\]$/i;
  if (trimmed.startsWith("[") && simpleArrayScalar.test(trimmed))
    return true;
  return false;
};
const isValidJSON = (value) => {
  try {
    JSON.stringify(value);
    return true;
  } catch (error2) {
    return false;
  }
};
const unescapeJson = (input) => {
  let validJson = false;
  let parsedJson = void 0;
  let unescapedStr = input;
  const recursiveUnescape = (inputStr) => {
    let newStr = inputStr.replace(/\\(.)/g, "$1");
    while (newStr !== inputStr) {
      inputStr = newStr;
      newStr = inputStr.replace(/\\(.)/g, "$1");
    }
    return newStr;
  };
  const deepParse = (data) => {
    if (isJSONLikeString(data)) {
      try {
        const innerJson = JSON.parse(data);
        if (typeof innerJson === "object" && innerJson !== null) {
          return deepParse(innerJson);
        }
      } catch (e2) {
        return data;
      }
    } else if (typeof data === "object" && data !== null) {
      Object.keys(data).forEach((key) => {
        data[key] = deepParse(data[key]);
      });
    }
    return data;
  };
  try {
    parsedJson = isJSONLikeString(input) ? JSON.parse(input) : input;
    validJson = true;
    parsedJson = deepParse(parsedJson);
    unescapedStr = JSON.stringify(parsedJson, null, 2);
  } catch (error2) {
    if (typeof input === "object" && input !== null) {
      try {
        unescapedStr = JSON.stringify(input, null, 2);
        validJson = true;
        parsedJson = input;
      } catch (stringifyError) {
        unescapedStr = recursiveUnescape(input.toString());
      }
    } else {
      unescapedStr = recursiveUnescape(input.toString());
    }
  }
  return { validJson, parsedJson, unescapedStr };
};
const getApiRoutes = () => {
  return getLfManager().getApiRoutes();
};
const getLfData = () => {
  var _a;
  return (_a = getLfManager().getManagers().lfFramework) == null ? void 0 : _a.data;
};
const getLfManager = () => {
  return window[LF_MANAGER_SYMBOL];
};
const getLfThemes = () => {
  return getLfManager().getManagers().lfFramework.theme.get.themes().asDataset;
};
const initLfManager = () => {
  if (!window[LF_MANAGER_SYMBOL]) {
    window[LF_MANAGER_SYMBOL] = new LFManager();
  }
};
function isFreeHookAPI(obj) {
  if (!obj || typeof obj !== "object")
    return false;
  const o2 = obj;
  return typeof o2["freeMemory"] === "function" || typeof o2["fetchApi"] === "function" || LFFreeFlags.PatchedFree in o2 || LFFreeFlags.PatchedFetch in o2;
}
function isRefreshHookApp(obj) {
  if (!obj || typeof obj !== "object")
    return false;
  const o2 = obj;
  return typeof o2["refreshComboInNodes"] === "function" || "refreshComboInNodes" in o2 || LFRefreshFlags.PatchedRefresh in o2;
}
function isInterruptHookAPI(obj) {
  if (!obj || typeof obj !== "object")
    return false;
  const o2 = obj;
  return typeof o2["interrupt"] === "function" || "interrupt" in o2 || LFInterruptFlags.PatchedInterrupt in o2;
}
const getInput = (node, type) => {
  var _a;
  return (_a = node == null ? void 0 : node.inputs) == null ? void 0 : _a.find((w2) => w2.type.toLowerCase() === type.toLowerCase());
};
const resolveNodeId = (p2) => {
  if (!p2) {
    return null;
  }
  return p2.node ?? p2.id ?? p2.node_id ?? null;
};
const clampPercent = (value) => {
  if (typeof value !== "number" || Number.isNaN(value) || !Number.isFinite(value)) {
    return 0;
  }
  return Math.min(100, Math.max(0, value));
};
const isValidNumber = (n2) => {
  return !isNaN(n2) && typeof n2 === "number";
};
const toNumber = (value) => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  return 0;
};
const asString = (value) => typeof value === "string" ? value : void 0;
const formatBytes = (bytes) => {
  if (!bytes) {
    return "0 B";
  }
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / Math.pow(1024, index);
  return `${value.toFixed(2)} ${units[index]}`;
};
const isString = (value) => typeof value === "string";
const normalizeDirectoryRequest = (value) => typeof value === "string" ? value : "";
const percentLabel = (value) => `${clampPercent(value).toFixed(1)}%`;
const canvasToBase64 = (canvas) => {
  return canvas.toDataURL("image/png");
};
const createDOMWidget = (type, element, node, options) => {
  getLfManager().log(`Creating '${type}'`, { element });
  try {
    const { nodeData } = Object.getPrototypeOf(node).constructor;
    let name = DEFAULT_WIDGET_NAME;
    for (const key in nodeData.input) {
      if (Object.prototype.hasOwnProperty.call(nodeData.input, key)) {
        const input = nodeData.input[key];
        for (const key2 in input) {
          if (Object.prototype.hasOwnProperty.call(input, key2)) {
            const element2 = Array.from(input[key2]);
            if (element2[0] === type) {
              name = key2;
              break;
            }
          }
        }
        if (name) {
          break;
        }
      }
    }
    return node.addDOMWidget(name, type, element, options);
  } catch (error2) {
    getLfManager().log(`Couldn't find a widget of type ${type}`, { error: error2, node }, LogSeverity.Warning);
    return node.addDOMWidget(DEFAULT_WIDGET_NAME, type, element, options);
  }
};
const debounce = (func, delay) => {
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => func(...args), delay);
  };
};
const findWidget = (node, type) => {
  var _a;
  return (_a = node == null ? void 0 : node.widgets) == null ? void 0 : _a.find((w2) => w2.type === type);
};
const getCustomWidget = (node, type) => {
  var _a;
  return (_a = node == null ? void 0 : node.widgets) == null ? void 0 : _a.find((w2) => w2.type.toLowerCase() === type.toLowerCase());
};
const getWidget = (node, type) => {
  var _a;
  return (_a = node == null ? void 0 : node.widgets) == null ? void 0 : _a.find((w2) => w2.type.toLowerCase() === type.toLowerCase());
};
const isValidObject = (obj) => {
  return obj && typeof obj === "object" && Object.keys(obj).length > 0;
};
const normalizeValue = (value, callback, widget, onException) => {
  try {
    callback(value, unescapeJson(value));
  } catch (error2) {
    if (onException) {
      onException();
    }
    getLfManager().log(`Normalization error!`, { error: error2, widget }, LogSeverity.Error);
  }
};
const refreshChart = (node) => {
  var _a, _b;
  try {
    const domWidget = ((_a = findWidget(node, CustomWidgetName.countBarChart)) == null ? void 0 : _a.element) || ((_b = findWidget(node, CustomWidgetName.tabBarChart)) == null ? void 0 : _b.element);
    if (domWidget) {
      const chart = domWidget.querySelector("lf-chart");
      if (chart) {
        const canvas = chart.shadowRoot.querySelector("canvas");
        const isSmaller = (canvas == null ? void 0 : canvas.clientWidth) < chart.clientWidth || (canvas == null ? void 0 : canvas.clientHeight) < chart.clientHeight;
        const isBigger = (canvas == null ? void 0 : canvas.clientWidth) > chart.clientWidth || (canvas == null ? void 0 : canvas.clientHeight) > chart.clientHeight;
        if (isSmaller || isBigger) {
          chart.refresh();
        }
      }
    }
  } catch (error2) {
    getLfManager().log("Whoops! It seems there is no chart. :V", { error: error2 }, LogSeverity.Error);
  }
};
{
  console.log("LF modules loaded!");
}
getLfFramework();
{
  console.log("LF Framework initialized!");
}
const hasComfyApp = typeof window !== "undefined" && typeof window.LGraph !== "undefined";
if (hasComfyApp) {
  initLfManager();
  const lfManager = getLfManager();
  lfManager.initialize();
  {
    console.log("LF Manager initialized!", lfManager);
  }
} else {
  {
    console.log("Skipping dashboard bootstrap (no Comfy app detected)");
  }
}
export {
  LF_TOAST_BLOCKS as $,
  AVATAR_COVER as A,
  LF_SLIDER_BLOCKS as B,
  CY_ATTRIBUTES as C,
  D,
  LF_SLIDER_PARTS as E,
  LF_SLIDER_CSS_VARIABLES as F,
  LF_SLIDER_PROPS as G,
  LF_MASONRY_DEFAULT_COLUMNS as H,
  IMAGE_TYPE_IDS as I,
  LF_MASONRY_BLOCKS as J,
  LF_MASONRY_PARTS as K,
  LF_SPLASH_BLOCKS as L,
  LF_MASONRY_CSS_VARS as M,
  LF_MASONRY_PROPS as N,
  OPTION_TYPE_IDS as O,
  LF_MASONRY_IDS as P,
  LF_CAROUSEL_BLOCKS as Q,
  LF_CAROUSEL_PARTS as R,
  STYLE_COVER as S,
  TIMEFRAME_COVER as T,
  LF_CAROUSEL_PROPS as U,
  V,
  W$1 as W,
  LF_CAROUSEL_IDS as X,
  LF_ARTICLE_BLOCKS as Y,
  LF_ARTICLE_PARTS as Z,
  LF_ARTICLE_PROPS as _,
  LF_SPLASH_PARTS as a,
  LF_THEME_ICONS as a$,
  LF_TOAST_PARTS as a0,
  LF_TOAST_CSS_VARIABLES as a1,
  LF_TOAST_PROPS as a2,
  LF_BADGE_BLOCKS as a3,
  LF_BADGE_PARTS as a4,
  LF_BADGE_PROPS as a5,
  LF_BUTTON_BLOCKS as a6,
  LF_BUTTON_PARTS as a7,
  LF_BUTTON_PROPS as a8,
  LF_CANVAS_BLOCKS as a9,
  LF_LIST_BLOCKS as aA,
  LF_LIST_PARTS as aB,
  LF_LIST_PROPS as aC,
  LF_PHOTOFRAME_BLOCKS as aD,
  LF_PHOTOFRAME_PARTS as aE,
  LF_PHOTOFRAME_PROPS as aF,
  LF_PROGRESSBAR_BLOCKS as aG,
  LF_PROGRESSBAR_PARTS as aH,
  LF_PROGRESSBAR_CSS_VARIABLES as aI,
  LF_PROGRESSBAR_PROPS as aJ,
  LF_SPINNER_PROPS as aK,
  LF_TEXTFIELD_BLOCKS as aL,
  LF_TEXTFIELD_PARTS as aM,
  LF_TEXTFIELD_PROPS as aN,
  LF_TOGGLE_BLOCKS as aO,
  LF_TOGGLE_PARTS as aP,
  LF_TOGGLE_PROPS as aQ,
  LF_TYPEWRITER_BLOCKS as aR,
  LF_TYPEWRITER_PARTS as aS,
  LF_TYPEWRITER_PROPS as aT,
  LF_UPLOAD_BLOCKS as aU,
  LF_UPLOAD_PARTS as aV,
  LF_UPLOAD_PROPS as aW,
  LF_BADGE_CSS_VARS as aX,
  LF_CHIP_CSS_VARS as aY,
  LF_CARD_IDS as aZ,
  LF_CHAT_IDS as a_,
  LF_CANVAS_PARTS as aa,
  LF_CANVAS_PROPS as ab,
  LF_CARD_BLOCKS as ac,
  LF_CARD_PARTS as ad,
  LF_CARD_CSS_VARS as ae,
  LF_CARD_DEFAULTS as af,
  LF_CARD_PROPS as ag,
  LF_CHART_BLOCKS as ah,
  LF_CHART_PARTS as ai,
  LF_CHART_CSS_VARS as aj,
  LF_THEME_COLORS_DATA_PREFIX as ak,
  LF_CHART_PROPS as al,
  LF_CHAT_BLOCKS as am,
  LF_CHAT_PARTS as an,
  LF_CHAT_PROPS as ao,
  LF_CHIP_BLOCKS as ap,
  LF_CHIP_PARTS as aq,
  LF_CHIP_PROPS as ar,
  LF_CODE_BLOCKS as as,
  LF_CODE_PARTS as at,
  LF_CODE_PROPS as au,
  LF_IMAGE_BLOCKS as av,
  LF_IMAGE_PARTS as aw,
  LF_IMAGE_CSS_VARS as ax,
  LF_IMAGE_PROPS as ay,
  CSS_VAR_PREFIX as az,
  LF_STYLE_ID as b,
  LF_IMAGEVIEWER_BLOCKS as b0,
  LF_IMAGEVIEWER_PARTS as b1,
  LF_IMAGEVIEWER_PROPS as b2,
  IDS as b3,
  LF_HEADER_BLOCKS as b4,
  LF_HEADER_PARTS as b5,
  LF_HEADER_PROPS as b6,
  LF_HEADER_SLOT as b7,
  LF_TREE_BLOCKS as b8,
  LF_TREE_PARTS as b9,
  LF_TREE_PROPS as ba,
  LF_TREE_CSS_VARIABLES as bb,
  LF_TABBAR_BLOCKS as bc,
  LF_TABBAR_PARTS as bd,
  LF_TABBAR_PROPS as be,
  LF_ACCORDION_BLOCKS as bf,
  LF_ACCORDION_PARTS as bg,
  LF_ACCORDION_PROPS as bh,
  LF_PLACEHOLDER_BLOCKS as bi,
  LF_PLACEHOLDER_PARTS as bj,
  LF_PLACEHOLDER_PROPS as bk,
  LF_DRAWER_BLOCKS as bl,
  LF_DRAWER_PARTS as bm,
  LF_DRAWER_PROPS as bn,
  LF_DRAWER_SLOT as bo,
  LF_EFFECTS_FOCUSABLES as bp,
  onFrameworkReady as bq,
  LF_WRAPPER_ID as c,
  LF_SPLASH_PROPS as d,
  LF_COMPARE_BLOCKS as e,
  LF_ATTRIBUTES as f,
  LF_COMPARE_PARTS as g,
  LF_COMPARE_CSS_VARS as h,
  LF_COMPARE_DEFAULTS as i,
  LF_COMPARE_PROPS as j,
  jt as k,
  LF_COMPARE_IDS as l,
  LF_MESSENGER_CLEAN_UI as m,
  n,
  LF_MESSENGER_BLOCKS as o,
  pt as p,
  LF_MESSENGER_PARTS as q,
  LF_MESSENGER_PROPS as r,
  LF_MESSENGER_IDS as s,
  LF_MESSENGER_FILTER as t,
  LF_MESSENGER_NAV as u,
  LF_MESSENGER_MENU as v,
  OUTFIT_COVER as w,
  LOCATION_COVER as x,
  CHILD_ROOT_MAP as y,
  z
};
