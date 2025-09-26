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
    code: "code",
    container: "container",
    content: "content",
    empty: "empty",
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
  "lfFilter",
  "lfInitialExpansionDepth",
  "lfRipple",
  "lfSelectable",
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
  hexagonMinus: "hexagon-minus",
  hexagonMinus2: "hexagon-minus-2",
  hexagonPlus: "hexagon-plus",
  hexagonPlus2: "hexagon-plus-2",
  hourglassLow: "hourglass-low",
  id: "id",
  ikosaedr: "ikosaedr",
  imageInPicture: "image-in-picture",
  infoHexagon: "info-hexagon",
  innerShadowBottom: "inner-shadow-bottom",
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
  offId: "off-id",
  offMicrophone: "off-microphone",
  offMoon: "off-moon",
  offNotification: "off-notification",
  offPalette: "off-palette",
  offReplace: "off-replace",
  offSearch: "off-search",
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
var __defProp = Object.defineProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var win = typeof window !== "undefined" ? window : {};
var plt = {
  $resourcesUrl$: ""
};
var getAssetPath = (path) => {
  const assetUrl = new URL(path, plt.$resourcesUrl$);
  return assetUrl.origin !== win.location.origin ? assetUrl.href : assetUrl.pathname;
};
var setAssetPath = (path) => plt.$resourcesUrl$ = path;
var escapeRegExpSpecialCharacters = (text) => {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
};
var result_exports = {};
__export(result_exports, {
  err: () => err,
  map: () => map,
  ok: () => ok,
  unwrap: () => unwrap,
  unwrapErr: () => unwrapErr
});
var ok = (value) => ({
  isOk: true,
  isErr: false,
  value
});
var err = (value) => ({
  isOk: false,
  isErr: true,
  value
});
function map(result, fn) {
  if (result.isOk) {
    const val = fn(result.value);
    if (val instanceof Promise) {
      return val.then((newVal) => ok(newVal));
    } else {
      return ok(val);
    }
  }
  if (result.isErr) {
    const value = result.value;
    return err(value);
  }
  throw "should never get here";
}
var unwrap = (result) => {
  if (result.isOk) {
    return result.value;
  } else {
    throw result.value;
  }
};
var unwrapErr = (result) => {
  if (result.isErr) {
    return result.value;
  } else {
    throw result.value;
  }
};
var createSupportsRuleRe = (selector) => {
  const safeSelector2 = escapeRegExpSpecialCharacters(selector);
  return new RegExp(
    // First capture group: match any context before the selector that's not inside @supports selector()
    // Using negative lookahead to avoid matching inside @supports selector(...) condition
    `(^|[^@]|@(?!supports\\s+selector\\s*\\([^{]*?${safeSelector2}))(${safeSelector2}\\b)`,
    "g"
  );
};
createSupportsRuleRe("::slotted");
createSupportsRuleRe(":host");
createSupportsRuleRe(":host-context");
var __classPrivateFieldSet$7 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$7 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfColor_LF_MANAGER, _LfColor_handleEdgeCases;
class LfColor {
  constructor(lfFramework2) {
    _LfColor_LF_MANAGER.set(this, void 0);
    _LfColor_handleEdgeCases.set(this, (color) => {
      const { logs } = __classPrivateFieldGet$7(this, _LfColor_LF_MANAGER, "f").debug;
      const { variables } = __classPrivateFieldGet$7(this, _LfColor_LF_MANAGER, "f").theme.get.current();
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
      const { logs } = __classPrivateFieldGet$7(this, _LfColor_LF_MANAGER, "f").debug;
      color = __classPrivateFieldGet$7(this, _LfColor_handleEdgeCases, "f").call(this, color);
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
        const { logs } = __classPrivateFieldGet$7(this, _LfColor_LF_MANAGER, "f").debug;
        const code = color.toLowerCase();
        if (LF_COLOR_CODES[code]) {
          return LF_COLOR_CODES[code];
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
    __classPrivateFieldSet$7(this, _LfColor_LF_MANAGER, lfFramework2, "f");
  }
}
_LfColor_LF_MANAGER = /* @__PURE__ */ new WeakMap(), _LfColor_handleEdgeCases = /* @__PURE__ */ new WeakMap();
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
const nodeGetDrilldownInfo = (nodes) => {
  let maxChildren = 0;
  let maxDepth = 0;
  const getDepth = function(n2) {
    const depth = 0;
    if (n2.children) {
      n2.children.forEach(function(d2) {
        getDepth(d2);
      });
    }
    return depth;
  };
  const recursive = (arr) => {
    maxDepth++;
    for (let index = 0; index < arr.length; index++) {
      const node = arr[index];
      getDepth(node);
      if (Array.isArray(node.children) && maxChildren < node.children.length) {
        maxChildren = node.children.length;
        recursive(node.children);
      }
    }
  };
  recursive(nodes);
  return {
    maxChildren,
    maxDepth
  };
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
const nodeSetProperties = (nodes, properties, recursively, exclude) => {
  const updated = [];
  if (!exclude) {
    exclude = [];
  }
  if (recursively) {
    nodes = nodeToStream(nodes);
  }
  for (let index = 0; index < nodes.length; index++) {
    const node = nodes[index];
    for (const key in properties) {
      if (!exclude.includes(node)) {
        node[key] = properties[key];
        updated.push(node);
      }
    }
  }
  return updated;
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
    slot: [],
    text: [],
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
    } catch (error) {
      console.error("Failed to stringify object:", error);
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
      getDrilldownInfo: (nodes) => nodeGetDrilldownInfo(nodes),
      getParent: (nodes, child) => nodeGetParent(nodes, child),
      pop: (nodes, node2remove) => nodePop(nodes, node2remove),
      removeNodeByCell: (dataset, cell) => findNodeByCell(dataset, cell),
      setProperties: (nodes, properties, recursively, exclude) => nodeSetProperties(nodes, properties, recursively, exclude),
      toStream: (nodes) => nodeToStream(nodes),
      traverseVisible: (nodes, predicates) => nodeTraverseVisible(nodes, predicates)
    };
  }
}
var __classPrivateFieldSet$6 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$6 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
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
      Array.from(__classPrivateFieldGet$6(this, _LfDebug_COMPONENTS, "f").codes).forEach((comp) => {
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
      Array.from(__classPrivateFieldGet$6(this, _LfDebug_COMPONENTS, "f").toggles).forEach((comp) => {
        comp.setValue(__classPrivateFieldGet$6(this, _LfDebug_IS_ENABLED, "f") ? "on" : "off");
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
        __classPrivateFieldSet$6(this, _LfDebug_LOGS, [], "f");
        __classPrivateFieldGet$6(this, _LfDebug_codeDispatcher, "f").call(this);
      },
      //#endregion
      //#region Logs from comp
      fromComponent(comp) {
        return comp.rootElement !== void 0;
      },
      //#endregion
      //#region New log
      new: async (comp, message, category = "informational") => {
        if (__classPrivateFieldGet$6(this, _LfDebug_IS_PROD, "f") && category === "informational") {
          return;
        }
        if (__classPrivateFieldGet$6(this, _LfDebug_COMPONENTS, "f").codes.has(comp)) {
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
        if (__classPrivateFieldGet$6(this, _LfDebug_LOGS, "f").length > __classPrivateFieldGet$6(this, _LfDebug_LOG_LIMIT, "f")) {
          if (__classPrivateFieldGet$6(this, _LfDebug_IS_ENABLED, "f")) {
            console.warn(log.date.toLocaleDateString() + " lf-debug => Too many logs (> " + __classPrivateFieldGet$6(this, _LfDebug_LOG_LIMIT, "f") + ")! Dumping (increase debug.logLimit to store more logs)... .");
          }
          this.logs.dump();
        }
        __classPrivateFieldGet$6(this, _LfDebug_LOGS, "f").push(log);
        switch (category) {
          case "error":
            console.error(`${log.date.toLocaleDateString()} ${log.id} ${log.message}`, log.class);
            break;
          case "warning":
            console.warn(`${log.date.toLocaleDateString()} ${log.id} ${log.message}`, log.class);
            break;
        }
        if (this.isEnabled()) {
          __classPrivateFieldGet$6(this, _LfDebug_codeDispatcher, "f").call(this, log);
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
        for (let index = 0; index < __classPrivateFieldGet$6(this, _LfDebug_LOGS, "f").length; index++) {
          const log = __classPrivateFieldGet$6(this, _LfDebug_LOGS, "f")[index];
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
        if (__classPrivateFieldGet$6(this, _LfDebug_LOGS, "f").length > 0) {
          console.groupCollapsed("%c  %cAll logs (" + __classPrivateFieldGet$6(this, _LfDebug_LOGS, "f").length + ")", "background-color: blue; margin-right: 10px; border-radius: 50%", "background-color: transparent");
          console.table(__classPrivateFieldGet$6(this, _LfDebug_LOGS, "f"));
          console.groupEnd();
        }
      }
      //#endregion
    };
    this.isEnabled = () => {
      return __classPrivateFieldGet$6(this, _LfDebug_IS_ENABLED, "f");
    };
    this.register = (comp) => {
      if (comp.rootElement.tagName.toLowerCase() === "lf-code") {
        __classPrivateFieldGet$6(this, _LfDebug_COMPONENTS, "f").codes.add(comp);
      } else {
        __classPrivateFieldGet$6(this, _LfDebug_COMPONENTS, "f").toggles.add(comp);
      }
    };
    this.toggle = (value, dispatch = true) => {
      if (value === false || value === true) {
        __classPrivateFieldSet$6(this, _LfDebug_IS_ENABLED, value, "f");
      } else {
        __classPrivateFieldSet$6(this, _LfDebug_IS_ENABLED, !__classPrivateFieldGet$6(this, _LfDebug_IS_ENABLED, "f"), "f");
      }
      if (dispatch) {
        __classPrivateFieldGet$6(this, _LfDebug_toggleDispatcher, "f").call(this);
      }
      return __classPrivateFieldGet$6(this, _LfDebug_IS_ENABLED, "f");
    };
    this.unregister = (comp) => {
      if (comp.rootElement.tagName.toLowerCase() === "lf-code") {
        __classPrivateFieldGet$6(this, _LfDebug_COMPONENTS, "f").codes.delete(comp);
      } else {
        __classPrivateFieldGet$6(this, _LfDebug_COMPONENTS, "f").toggles.delete(comp);
      }
    };
    __classPrivateFieldSet$6(this, _LfDebug_IS_PROD, typeof process !== "undefined" && ((_a = process.env) == null ? void 0 : _a.NODE_ENV) === "production", "f");
  }
}
_LfDebug_COMPONENTS = /* @__PURE__ */ new WeakMap(), _LfDebug_IS_ENABLED = /* @__PURE__ */ new WeakMap(), _LfDebug_IS_PROD = /* @__PURE__ */ new WeakMap(), _LfDebug_LOG_LIMIT = /* @__PURE__ */ new WeakMap(), _LfDebug_LOGS = /* @__PURE__ */ new WeakMap(), _LfDebug_codeDispatcher = /* @__PURE__ */ new WeakMap(), _LfDebug_toggleDispatcher = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldSet$5 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$5 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
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
      const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
      if (!session) {
        __classPrivateFieldGet$5(this, _LfDrag_MANAGER, "f").debug.logs.new(this, "Attempted to interact with an unregistered element.", "warning");
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
      const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
      if (!session) {
        __classPrivateFieldGet$5(this, _LfDrag_MANAGER, "f").debug.logs.new(this, "Attempted to interact with an unregistered element.", "warning");
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
      const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
      if (!session) {
        __classPrivateFieldGet$5(this, _LfDrag_MANAGER, "f").debug.logs.new(this, "Attempted to interact with an unregistered element.", "warning");
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
        if (!__classPrivateFieldGet$5(this, _LfDrag_REDUCED_MOTION, "f")) {
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
      const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
      if (!session) {
        __classPrivateFieldGet$5(this, _LfDrag_MANAGER, "f").debug.logs.new(this, "Attempted to interact with an unregistered element.", "warning");
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
        __classPrivateFieldGet$5(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2) => {
          const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
          if (!session) {
            console.warn("Attempted to interact with an unregistered element.");
            return;
          }
          onPointerDown(e2, session);
          if (!callbacks.onMove && !callbacks.onEnd) {
            __classPrivateFieldGet$5(this, _LfDrag_defaultPointerMoveAndUp, "f").call(this, element, session);
          }
        });
      },
      /**
       * Registers a skeleton for drag-to-drop.
       */
      dragToDrop: (element, callbacks) => {
        __classPrivateFieldGet$5(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2) => {
          __classPrivateFieldGet$5(this, _LfDrag_dragToDropHandler, "f").call(this, element, e2);
        });
      },
      /**
       * Registers a skeleton for drag-to-resize.
       */
      dragToResize: (element, callbacks) => {
        __classPrivateFieldGet$5(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2) => {
          __classPrivateFieldGet$5(this, _LfDrag_dragToResizeHandler, "f").call(this, element, e2);
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
        __classPrivateFieldGet$5(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2, distX, distY) => {
          __classPrivateFieldGet$5(this, _LfDrag_dragToScrollHandler, "f").call(this, element, e2, direction, distX, distY);
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
        __classPrivateFieldGet$5(this, _LfDrag_instances, "m", _LfDrag_initializeSession).call(this, element, callbacks, (e2) => {
          __classPrivateFieldGet$5(this, _LfDrag_swipeHandler, "f").call(this, element, e2, direction);
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
        const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
        if (!session)
          return;
        session.cleanupCb();
        __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").delete(element);
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
        const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").delete(element);
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
        const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").delete(element);
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
        const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").delete(element);
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
        const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").delete(element);
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
        const session = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
        session == null ? void 0 : session.cleanupCb();
        __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").delete(element);
      }
    };
    __classPrivateFieldSet$5(this, _LfDrag_MANAGER, lfFramework2, "f");
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
    return __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element);
  }
}
_LfDrag_IS_DRAGGING = /* @__PURE__ */ new WeakMap(), _LfDrag_DRAG_THRESHOLD = /* @__PURE__ */ new WeakMap(), _LfDrag_MANAGER = /* @__PURE__ */ new WeakMap(), _LfDrag_POINTER_ID = /* @__PURE__ */ new WeakMap(), _LfDrag_REDUCED_MOTION = /* @__PURE__ */ new WeakMap(), _LfDrag_SESSIONS = /* @__PURE__ */ new WeakMap(), _LfDrag_defaultPointerMoveAndUp = /* @__PURE__ */ new WeakMap(), _LfDrag_dragToDropHandler = /* @__PURE__ */ new WeakMap(), _LfDrag_dragToResizeHandler = /* @__PURE__ */ new WeakMap(), _LfDrag_dragToScrollHandler = /* @__PURE__ */ new WeakMap(), _LfDrag_swipeHandler = /* @__PURE__ */ new WeakMap(), _LfDrag_instances = /* @__PURE__ */ new WeakSet(), _LfDrag_initializeSession = function _LfDrag_initializeSession2(element, callbacks = {}, dragLogicHandler) {
  var _a;
  (_a = __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").get(element)) == null ? void 0 : _a.cleanupCb();
  __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").delete(element);
  const removeThresholdListeners = __classPrivateFieldGet$5(this, _LfDrag_instances, "m", _LfDrag_setupThresholdAwarePointerDown).call(this, element, __classPrivateFieldGet$5(this, _LfDrag_DRAG_THRESHOLD, "f"), (moveEvent, distX, distY) => {
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
  __classPrivateFieldGet$5(this, _LfDrag_SESSIONS, "f").set(element, session);
}, _LfDrag_setupThresholdAwarePointerDown = function _LfDrag_setupThresholdAwarePointerDown2(element, threshold, startDragHandler) {
  let pointerDownX = 0;
  let pointerDownY = 0;
  __classPrivateFieldSet$5(this, _LfDrag_IS_DRAGGING, false, "f");
  __classPrivateFieldSet$5(this, _LfDrag_POINTER_ID, null, "f");
  const onPointerDown = (e2) => {
    pointerDownX = e2.clientX;
    pointerDownY = e2.clientY;
    __classPrivateFieldSet$5(this, _LfDrag_IS_DRAGGING, false, "f");
    __classPrivateFieldSet$5(this, _LfDrag_POINTER_ID, e2.pointerId, "f");
  };
  const onPointerMove = (moveEvent) => {
    if (__classPrivateFieldGet$5(this, _LfDrag_POINTER_ID, "f") === null) {
      return;
    }
    const distX = moveEvent.clientX - pointerDownX;
    const distY = moveEvent.clientY - pointerDownY;
    const distance = Math.sqrt(distX ** 2 + distY ** 2);
    if (!__classPrivateFieldGet$5(this, _LfDrag_IS_DRAGGING, "f") && distance > threshold) {
      __classPrivateFieldSet$5(this, _LfDrag_IS_DRAGGING, true, "f");
      moveEvent.preventDefault();
      element.setPointerCapture(moveEvent.pointerId);
      startDragHandler(moveEvent, distX, distY);
    }
  };
  const onPointerUp = (_upEvent) => {
    __classPrivateFieldSet$5(this, _LfDrag_POINTER_ID, null, "f");
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
var __classPrivateFieldSet$4 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$4 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
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
      if (!__classPrivateFieldGet$4(this, _LfEffects_EFFECTS, "f")) {
        __classPrivateFieldSet$4(this, _LfEffects_EFFECTS, document.createElement("div"), "f");
        __classPrivateFieldGet$4(this, _LfEffects_EFFECTS, "f").classList.add("lf-effects");
        __classPrivateFieldGet$4(this, _LfEffects_EFFECTS, "f").dataset.cy = CY_ATTRIBUTES.effects;
        document.body.appendChild(__classPrivateFieldGet$4(this, _LfEffects_EFFECTS, "f"));
      }
      __classPrivateFieldGet$4(this, _LfEffects_EFFECTS, "f").appendChild(element);
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
      intensity: (key, value) => __classPrivateFieldGet$4(this, _LfEffects_INTENSITY, "f")[key] = value,
      timeout: (key, value) => __classPrivateFieldGet$4(this, _LfEffects_TIMEOUT, "f")[key] = value
    };
    this.backdrop = {
      hide: () => {
        if (!__classPrivateFieldGet$4(this, _LfEffects_BACKDROP, "f")) {
          return;
        }
        const backdrop = __classPrivateFieldGet$4(this, _LfEffects_BACKDROP, "f");
        backdrop.style.opacity = "0";
        backdrop.addEventListener("transitionend", () => {
          backdrop.remove();
          __classPrivateFieldSet$4(this, _LfEffects_BACKDROP, null, "f");
        });
      },
      isVisible: () => !!__classPrivateFieldGet$4(this, _LfEffects_BACKDROP, "f"),
      show: (onClose) => {
        const { logs } = __classPrivateFieldGet$4(this, _LfEffects_MANAGER, "f").debug;
        if (__classPrivateFieldGet$4(this, _LfEffects_BACKDROP, "f")) {
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
        __classPrivateFieldGet$4(this, _LfEffects_appendToWrapper, "f").call(this, backdrop);
        requestAnimationFrame(() => {
          backdrop.style.opacity = "1";
        });
        __classPrivateFieldSet$4(this, _LfEffects_BACKDROP, backdrop, "f");
      }
    };
    this.lightbox = {
      show: async (element, closeCb) => {
        const { debug } = __classPrivateFieldGet$4(this, _LfEffects_MANAGER, "f");
        if (__classPrivateFieldGet$4(this, _LfEffects_LIGHTBOX, "f")) {
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
        __classPrivateFieldGet$4(this, _LfEffects_appendToWrapper, "f").call(this, portal);
        __classPrivateFieldSet$4(this, _LfEffects_LIGHTBOX, portal, "f");
        this.backdrop.show(() => this.lightbox.hide());
        requestAnimationFrame(async () => {
          clone.focus();
        });
      },
      hide: () => {
        if (!__classPrivateFieldGet$4(this, _LfEffects_LIGHTBOX, "f")) {
          return;
        }
        __classPrivateFieldGet$4(this, _LfEffects_LIGHTBOX, "f").remove();
        __classPrivateFieldSet$4(this, _LfEffects_LIGHTBOX, null, "f");
        this.backdrop.hide();
      },
      isVisible: () => !!__classPrivateFieldGet$4(this, _LfEffects_LIGHTBOX, "f")
    };
    this.ripple = (e2, element, autoSurfaceRadius = true) => {
      if (!element) {
        return;
      }
      const ripple = document.createElement("span");
      const { left, height: h2, top, width: w2 } = element.getBoundingClientRect();
      const { backgroundColor, borderRadius, color } = __classPrivateFieldGet$4(this, _LfEffects_getParentStyle, "f").call(this, element);
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
      }), __classPrivateFieldGet$4(this, _LfEffects_TIMEOUT, "f").ripple);
    };
    this.isRegistered = (element) => __classPrivateFieldGet$4(this, _LfEffects_COMPONENTS, "f").has(element);
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
        __classPrivateFieldGet$4(this, _LfEffects_COMPONENTS, "f").add(element);
      }
    };
    this.unregister = {
      tilt: (element) => {
        element.removeEventListener("pointermove", () => {
        });
        element.removeEventListener("pointerleave", () => {
        });
        __classPrivateFieldGet$4(this, _LfEffects_COMPONENTS, "f").delete(element);
      }
    };
    __classPrivateFieldSet$4(this, _LfEffects_MANAGER, lfFramework2, "f");
  }
}
_LfEffects_BACKDROP = /* @__PURE__ */ new WeakMap(), _LfEffects_COMPONENTS = /* @__PURE__ */ new WeakMap(), _LfEffects_EFFECTS = /* @__PURE__ */ new WeakMap(), _LfEffects_INTENSITY = /* @__PURE__ */ new WeakMap(), _LfEffects_LIGHTBOX = /* @__PURE__ */ new WeakMap(), _LfEffects_MANAGER = /* @__PURE__ */ new WeakMap(), _LfEffects_TIMEOUT = /* @__PURE__ */ new WeakMap(), _LfEffects_appendToWrapper = /* @__PURE__ */ new WeakMap(), _LfEffects_getParentStyle = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldSet$3 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$3$1 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var _LfLLM_IS_ABORT_ERROR, _LfLLM_LF_MANAGER;
class LfLLM {
  constructor(lfFramework2) {
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
        const base = prune({
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
        const str = JSON.stringify(base);
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
      } catch (error) {
        console.error("Error calling LLM:", error);
        throw error;
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
        if (__classPrivateFieldGet$3$1(this, _LfLLM_IS_ABORT_ERROR, "f").call(this, e2)) {
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
        const text = ((_d = (_c = (_b = full.choices) == null ? void 0 : _b[0]) == null ? void 0 : _c.message) == null ? void 0 : _d.content) || "";
        yield { contentDelta: text, done: true, raw: full };
        return;
      }
      const decoder = new TextDecoder();
      let buffered = "";
      while (true) {
        let result;
        try {
          result = await reader.read();
        } catch (e2) {
          if (__classPrivateFieldGet$3$1(this, _LfLLM_IS_ABORT_ERROR, "f").call(this, e2)) {
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
          if (trimmed === "data: [DONE]") {
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
      const { debug } = __classPrivateFieldGet$3$1(this, _LfLLM_LF_MANAGER, "f");
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
      } catch (err2) {
        debug.logs.new(this, "Error: " + err2, "error");
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
          if (__classPrivateFieldGet$3$1(this, _LfLLM_IS_ABORT_ERROR, "f").call(this, e2)) {
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
    __classPrivateFieldSet$3(this, _LfLLM_LF_MANAGER, lfFramework2, "f");
  }
}
_LfLLM_IS_ABORT_ERROR = /* @__PURE__ */ new WeakMap(), _LfLLM_LF_MANAGER = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldSet$2 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$2$1 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
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
      if (!__classPrivateFieldGet$2$1(this, _LfPortal_PORTAL, "f")) {
        __classPrivateFieldSet$2(this, _LfPortal_PORTAL, document.createElement("div"), "f");
        __classPrivateFieldGet$2$1(this, _LfPortal_PORTAL, "f").classList.add("lf-portal");
        __classPrivateFieldGet$2$1(this, _LfPortal_PORTAL, "f").dataset.cy = CY_ATTRIBUTES.portal;
        document.body.appendChild(__classPrivateFieldGet$2$1(this, _LfPortal_PORTAL, "f"));
      }
      __classPrivateFieldGet$2$1(this, _LfPortal_PORTAL, "f").appendChild(element);
    });
    _LfPortal_clean.set(this, (element) => {
      if (!this.isInPortal(element)) {
        return;
      }
      const { dismissCb, parent } = __classPrivateFieldGet$2$1(this, _LfPortal_STATE, "f").get(element);
      __classPrivateFieldGet$2$1(this, _LfPortal_MANAGER, "f").removeClickCallback(dismissCb);
      if (parent) {
        parent.appendChild(element);
      }
      __classPrivateFieldGet$2$1(this, _LfPortal_STATE, "f").delete(element);
    });
    _LfPortal_schedulePositionUpdate.set(this, (element) => {
      __classPrivateFieldGet$2$1(this, _LfPortal_RAF, "f").queue.add(element);
      if (!__classPrivateFieldGet$2$1(this, _LfPortal_RAF, "f").frameId) {
        __classPrivateFieldGet$2$1(this, _LfPortal_RAF, "f").frameId = requestAnimationFrame(() => {
          __classPrivateFieldGet$2$1(this, _LfPortal_RAF, "f").frameId = 0;
          __classPrivateFieldGet$2$1(this, _LfPortal_RAF, "f").queue.forEach((el) => __classPrivateFieldGet$2$1(this, _LfPortal_executeRun, "f").call(this, el));
          __classPrivateFieldGet$2$1(this, _LfPortal_RAF, "f").queue.clear();
        });
      }
    });
    _LfPortal_executeRun.set(this, (element) => {
      if (!this.isInPortal(element) || !element.isConnected) {
        __classPrivateFieldGet$2$1(this, _LfPortal_clean, "f").call(this, element);
        return;
      }
      __classPrivateFieldGet$2$1(this, _LfPortal_resetStyle, "f").call(this, element);
      const state = __classPrivateFieldGet$2$1(this, _LfPortal_STATE, "f").get(element);
      if (!state) {
        __classPrivateFieldGet$2$1(this, _LfPortal_MANAGER, "f").debug.logs.new(this, `State for element not found.`, "warning");
        return;
      }
      const { anchor, margin, placement } = state;
      const { offsetHeight, offsetWidth, style } = element;
      style.display = "block";
      if (!__classPrivateFieldGet$2$1(this, _LfPortal_isAnchorHTMLElement, "f").call(this, anchor)) {
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
      requestAnimationFrame(() => __classPrivateFieldGet$2$1(this, _LfPortal_schedulePositionUpdate, "f").call(this, element));
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
      __classPrivateFieldGet$2$1(this, _LfPortal_clean, "f").call(this, element);
      __classPrivateFieldGet$2$1(this, _LfPortal_resetStyle, "f").call(this, element);
    };
    this.getState = (element) => {
      return __classPrivateFieldGet$2$1(this, _LfPortal_STATE, "f").get(element);
    };
    this.isInPortal = (element) => {
      return __classPrivateFieldGet$2$1(this, _LfPortal_STATE, "f").has(element);
    };
    this.open = (element, parent, anchor = parent, margin = 0, placement = "auto") => {
      let state = __classPrivateFieldGet$2$1(this, _LfPortal_STATE, "f").get(element);
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
        __classPrivateFieldGet$2$1(this, _LfPortal_STATE, "f").set(element, {
          anchor,
          dismissCb,
          margin,
          parent,
          placement
        });
        __classPrivateFieldGet$2$1(this, _LfPortal_MANAGER, "f").addClickCallback(dismissCb, true);
        __classPrivateFieldGet$2$1(this, _LfPortal_appendToWrapper, "f").call(this, element);
      }
      __classPrivateFieldGet$2$1(this, _LfPortal_schedulePositionUpdate, "f").call(this, element);
    };
    __classPrivateFieldSet$2(this, _LfPortal_MANAGER, lfFramework2, "f");
  }
}
_LfPortal_RAF = /* @__PURE__ */ new WeakMap(), _LfPortal_MANAGER = /* @__PURE__ */ new WeakMap(), _LfPortal_PORTAL = /* @__PURE__ */ new WeakMap(), _LfPortal_STATE = /* @__PURE__ */ new WeakMap(), _LfPortal_appendToWrapper = /* @__PURE__ */ new WeakMap(), _LfPortal_clean = /* @__PURE__ */ new WeakMap(), _LfPortal_schedulePositionUpdate = /* @__PURE__ */ new WeakMap(), _LfPortal_executeRun = /* @__PURE__ */ new WeakMap(), _LfPortal_isAnchorHTMLElement = /* @__PURE__ */ new WeakMap(), _LfPortal_resetStyle = /* @__PURE__ */ new WeakMap();
var __classPrivateFieldSet$1$1 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var __classPrivateFieldGet$1$1 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
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
    this.bemClass = (block, element, modifiers) => {
      let baseClass = element ? `${block}__${element}` : block;
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
              const text = await res.text();
              const ids = /* @__PURE__ */ new Set();
              const re = /<symbol\s+id=\"([^\"]+)\"/g;
              let m2;
              while (m2 = re.exec(text))
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
    this.set = (name, list) => {
      if (typeof document === "undefined") {
        return;
      }
      if (!__classPrivateFieldGet$1$1(this, _LfTheme_STYLE_ELEMENT, "f")) {
        __classPrivateFieldSet$1$1(this, _LfTheme_STYLE_ELEMENT, document.documentElement.querySelector("head").appendChild(document.createElement("style")), "f");
      }
      if (name) {
        __classPrivateFieldSet$1$1(this, _LfTheme_CURRENT, name, "f");
      }
      if (list) {
        __classPrivateFieldSet$1$1(this, _LfTheme_LIST, list, "f");
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
      } catch (error) {
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
var __classPrivateFieldGet$8 = function(receiver, state, kind, f2) {
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a getter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return kind === "m" ? f2 : kind === "a" ? f2.call(receiver) : f2 ? f2.value : state.get(receiver);
};
var __classPrivateFieldSet$8 = function(receiver, state, value, kind, f2) {
  if (kind === "m") throw new TypeError("Private method is not writable");
  if (kind === "a" && !f2) throw new TypeError("Private accessor was defined without a setter");
  if (typeof state === "function" ? receiver !== state || !f2 : !state.has(receiver)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return kind === "a" ? f2.call(receiver, value) : f2 ? f2.value = value : state.set(receiver, value), value;
};
var _LfFramework_LISTENERS_SETUP, _LfFramework_MODULES, _LfFramework_SHAPES, _LfFramework_setupListeners;
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
      if (!__classPrivateFieldGet$8(this, _LfFramework_LISTENERS_SETUP, "f")) {
        __classPrivateFieldSet$8(this, _LfFramework_LISTENERS_SETUP, true, "f");
        __classPrivateFieldGet$8(this, _LfFramework_setupListeners, "f").call(this);
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
    this.getModules = () => __classPrivateFieldGet$8(this, _LfFramework_MODULES, "f");
    this.register = (module, options) => {
      if (__classPrivateFieldGet$8(this, _LfFramework_MODULES, "f").has(module)) {
        this.debug.logs.new(this, `Module ${module} is already registered.`, "error");
        return;
      }
      __classPrivateFieldGet$8(this, _LfFramework_MODULES, "f").set(module, { name: module, ...options });
      this.debug.logs.new(this, `Module ${module} registered.`);
    };
    this.removeClickCallback = (cb) => {
      this.utilities.clickCallbacks.delete(cb);
    };
    this.shapes = {
      get: () => __classPrivateFieldGet$8(this, _LfFramework_SHAPES, "f").get(this),
      set: (shapes) => {
        __classPrivateFieldGet$8(this, _LfFramework_SHAPES, "f").set(this, shapes);
      }
    };
    const ICON_STYLE_CACHE = /* @__PURE__ */ new Map();
    this.assets = {
      get: (value, module = "lf-framework") => {
        if (!__classPrivateFieldGet$8(this, _LfFramework_MODULES, "f").has(module)) {
          this.debug.logs.new(this, `Module ${module} is not registered.`, "error");
          return {
            path: "",
            style: { mask: "", webkitMask: "" }
          };
        }
        const { getAssetPath: getAssetPath2 } = __classPrivateFieldGet$8(this, _LfFramework_MODULES, "f").get(module);
        if (ICON_STYLE_CACHE.has(value)) {
          return ICON_STYLE_CACHE.get(value);
        }
        const path = getAssetPath2(value);
        const style = {
          mask: `url('${path}') no-repeat center`,
          webkitMask: `url('${path}') no-repeat center`
        };
        const cached = { path, style };
        ICON_STYLE_CACHE.set(value, cached);
        return cached;
      },
      set: (value, module) => {
        if (!module) {
          __classPrivateFieldGet$8(this, _LfFramework_MODULES, "f").forEach(({ setAssetPath: setAssetPath2 }) => setAssetPath2(value));
        } else if (__classPrivateFieldGet$8(this, _LfFramework_MODULES, "f").has(module)) {
          const { setAssetPath: setAssetPath2 } = __classPrivateFieldGet$8(this, _LfFramework_MODULES, "f").get(module);
          setAssetPath2(value);
        }
      }
    };
    this.color = new LfColor(this);
    this.data = new LfData(this);
    this.debug = new LfDebug(this);
    this.drag = new LfDrag(this);
    this.effects = new LfEffects(this);
    this.llm = new LfLLM(this);
    this.portal = new LfPortal(this);
    this.theme = new LfTheme(this);
    this.utilities = {
      clickCallbacks: /* @__PURE__ */ new Set()
    };
  }
  sanitizeProps(props, compName) {
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
    } else {
      return sanitized;
    }
  }
}
_LfFramework_LISTENERS_SETUP = /* @__PURE__ */ new WeakMap(), _LfFramework_MODULES = /* @__PURE__ */ new WeakMap(), _LfFramework_SHAPES = /* @__PURE__ */ new WeakMap(), _LfFramework_setupListeners = /* @__PURE__ */ new WeakMap();
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
  t2.__stencil__getHostRef = () => e2, e2.t = t2;
}, o$1 = (t2, e2) => e2 in t2, l = (t2, e2) => (0, console.error)(t2, e2), r = /* @__PURE__ */ new Map(), i = /* @__PURE__ */ new Map(), s = "slot-fb{display:contents}slot-fb[hidden]{display:none}", c = "http://www.w3.org/1999/xlink", u = "undefined" != typeof window ? window : {}, a = { o: 0, l: "", jmp: (t2) => t2(), raf: (t2) => requestAnimationFrame(t2), ael: (t2, e2, n2, o2) => t2.addEventListener(e2, n2, o2), rel: (t2, e2, n2, o2) => t2.removeEventListener(e2, n2, o2), ce: (t2, e2) => new CustomEvent(t2, e2) }, f = (t2) => Promise.resolve(t2), d = (() => {
  try {
    return new CSSStyleSheet(), "function" == typeof new CSSStyleSheet().replaceSync;
  } catch (t2) {
  }
  return false;
})(), h = !!d && (() => !!u.document && Object.getOwnPropertyDescriptor(u.document.adoptedStyleSheets, "length").writable)(), p = false, v = [], m = [], y = (t2, e2) => (n2) => {
  t2.push(n2), p || (p = true, 4 & a.o ? g(b) : a.raf(b));
}, w = (t2) => {
  for (let e2 = 0; e2 < t2.length; e2++) try {
    t2[e2](performance.now());
  } catch (t3) {
    l(t3);
  }
  t2.length = 0;
}, b = () => {
  w(v), w(m), (p = v.length > 0) && a.raf(b);
}, g = (t2) => f().then(t2), $ = y(m), S = (t2) => {
  const e2 = new URL(t2, a.l);
  return e2.origin !== u.location.origin ? e2.href : e2.pathname;
}, j = (t2) => a.l = t2, O = (t2) => "object" == (t2 = typeof t2) || "function" === t2;
function k(t2) {
  var e2, n2, o2;
  return null != (o2 = null == (n2 = null == (e2 = t2.head) ? void 0 : e2.querySelector('meta[name="csp-nonce"]')) ? void 0 : n2.getAttribute("content")) ? o2 : void 0;
}
((e2, n2) => {
  for (var o2 in n2) t(e2, o2, { get: n2[o2], enumerable: true });
})({}, { err: () => x, map: () => C, ok: () => E, unwrap: () => P, unwrapErr: () => N });
var E = (t2) => ({ isOk: true, isErr: false, value: t2 }), x = (t2) => ({ isOk: false, isErr: true, value: t2 });
function C(t2, e2) {
  if (t2.isOk) {
    const n2 = e2(t2.value);
    return n2 instanceof Promise ? n2.then(((t3) => E(t3))) : E(n2);
  }
  if (t2.isErr) return x(t2.value);
  throw "should never get here";
}
var M, P = (t2) => {
  if (t2.isOk) return t2.value;
  throw t2.value;
}, N = (t2) => {
  if (t2.isErr) return t2.value;
  throw t2.value;
};
function R() {
  const t2 = this.attachShadow({ mode: "open" });
  void 0 === M && (M = null), M && (h ? t2.adoptedStyleSheets.push(M) : t2.adoptedStyleSheets = [...t2.adoptedStyleSheets, M]);
}
var U = /* @__PURE__ */ new WeakMap(), D = (t2) => "sc-" + t2.i, W$1 = (t2, e2, ...n2) => {
  let o2 = null, l2 = null, r2 = false, i2 = false;
  const s2 = [], c2 = (e3) => {
    for (let n3 = 0; n3 < e3.length; n3++) o2 = e3[n3], Array.isArray(o2) ? c2(o2) : null != o2 && "boolean" != typeof o2 && ((r2 = "function" != typeof t2 && !O(o2)) && (o2 += ""), r2 && i2 ? s2[s2.length - 1].u += o2 : s2.push(r2 ? A(null, o2) : o2), i2 = r2);
  };
  if (c2(n2), e2) {
    e2.key && (l2 = e2.key);
    {
      const t3 = e2.className || e2.class;
      t3 && (e2.class = "object" != typeof t3 ? t3 : Object.keys(t3).filter(((e3) => t3[e3])).join(" "));
    }
  }
  if ("function" == typeof t2) return t2(null === e2 ? {} : e2, s2, F);
  const u2 = A(t2, null);
  return u2.h = e2, s2.length > 0 && (u2.p = s2), u2.v = l2, u2;
}, A = (t2, e2) => ({ o: 0, m: t2, u: e2, $: null, p: null, h: null, v: null }), L = {}, F = { forEach: (t2, e2) => t2.map(H).forEach(e2), map: (t2, e2) => t2.map(H).map(e2).map(T) }, H = (t2) => ({ vattrs: t2.h, vchildren: t2.p, vkey: t2.v, vname: t2.S, vtag: t2.m, vtext: t2.u }), T = (t2) => {
  if ("function" == typeof t2.vtag) {
    const e3 = { ...t2.vattrs };
    return t2.vkey && (e3.key = t2.vkey), t2.vname && (e3.name = t2.vname), W$1(t2.vtag, e3, ...t2.vchildren || []);
  }
  const e2 = A(t2.vtag, t2.vtext);
  return e2.h = t2.vattrs, e2.p = t2.vchildren, e2.v = t2.vkey, e2.S = t2.vname, e2;
}, q = (t2) => {
  const e2 = ((t3) => t3.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))(t2);
  return RegExp(`(^|[^@]|@(?!supports\\s+selector\\s*\\([^{]*?${e2}))(${e2}\\b)`, "g");
};
q("::slotted"), q(":host"), q(":host-context");
var z, V = (t2, e2) => {
  if ("string" == typeof t2 && (16 & e2 || 8 & e2) && (t2.startsWith("{") && t2.endsWith("}") || t2.startsWith("[") && t2.endsWith("]"))) try {
    return JSON.parse(t2);
  } catch (t3) {
  }
  return null == t2 || O(t2) ? t2 : 4 & e2 ? "false" !== t2 && ("" === t2 || !!t2) : 2 & e2 ? "string" == typeof t2 ? parseFloat(t2) : "number" == typeof t2 ? t2 : NaN : 1 & e2 ? t2 + "" : t2;
}, G = (t2) => {
  var n2;
  return null == (n2 = e(t2)) ? void 0 : n2.$hostElement$;
}, I = (t2, e2) => {
  const n2 = G(t2);
  return { emit: (t3) => J(n2, e2, { bubbles: true, composed: true, cancelable: false, detail: t3 }) };
}, J = (t2, e2, n2) => {
  const o2 = a.ce(e2, n2);
  return t2.dispatchEvent(o2), o2;
}, Y = (t2, e2, n2, l2, r2, i2) => {
  if (n2 === l2) return;
  let s2 = o$1(t2, e2), f2 = e2.toLowerCase();
  if ("class" === e2) {
    const e3 = t2.classList, o2 = B(n2);
    let r3 = B(l2);
    e3.remove(...o2.filter(((t3) => t3 && !r3.includes(t3)))), e3.add(...r3.filter(((t3) => t3 && !o2.includes(t3))));
  } else if ("style" === e2) {
    for (const e3 in n2) l2 && null != l2[e3] || (e3.includes("-") ? t2.style.removeProperty(e3) : t2.style[e3] = "");
    for (const e3 in l2) n2 && l2[e3] === n2[e3] || (e3.includes("-") ? t2.style.setProperty(e3, l2[e3]) : t2.style[e3] = l2[e3]);
  } else if ("key" === e2) ;
  else if ("ref" === e2) l2 && l2(t2);
  else if (s2 || "o" !== e2[0] || "n" !== e2[1]) {
    const o2 = O(l2);
    if ((s2 || o2 && null !== l2) && !r2) try {
      if (t2.tagName.includes("-")) t2[e2] !== l2 && (t2[e2] = l2);
      else {
        const o3 = null == l2 ? "" : l2;
        "list" === e2 ? s2 = false : null != n2 && t2[e2] == o3 || ("function" == typeof t2.__lookupSetter__(e2) ? t2[e2] = o3 : t2.setAttribute(e2, o3));
      }
    } catch (t3) {
    }
    let u2 = false;
    f2 !== (f2 = f2.replace(/^xlink\:?/, "")) && (e2 = f2, u2 = true), null == l2 || false === l2 ? false === l2 && "" !== t2.getAttribute(e2) || (u2 ? t2.removeAttributeNS(c, e2) : t2.removeAttribute(e2)) : (!s2 || 4 & i2 || r2) && !o2 && 1 === t2.nodeType && (l2 = true === l2 ? "" : l2, u2 ? t2.setAttributeNS(c, e2, l2) : t2.setAttribute(e2, l2));
  } else if (e2 = "-" === e2[2] ? e2.slice(3) : o$1(u, f2) ? f2.slice(2) : f2[2] + e2.slice(3), n2 || l2) {
    const o2 = e2.endsWith(K);
    e2 = e2.replace(Q, ""), n2 && a.rel(t2, e2, n2, o2), l2 && a.ael(t2, e2, l2, o2);
  }
}, _ = /\s/, B = (t2) => ("object" == typeof t2 && t2 && "baseVal" in t2 && (t2 = t2.baseVal), t2 && "string" == typeof t2 ? t2.split(_) : []), K = "Capture", Q = RegExp(K + "$"), X = (t2, e2, n2) => {
  const o2 = 11 === e2.$.nodeType && e2.$.host ? e2.$.host : e2.$, l2 = t2 && t2.h || {}, r2 = e2.h || {};
  for (const t3 of Z(Object.keys(l2))) t3 in r2 || Y(o2, t3, l2[t3], void 0, n2, e2.o);
  for (const t3 of Z(Object.keys(r2))) Y(o2, t3, l2[t3], r2[t3], n2, e2.o);
};
function Z(t2) {
  return t2.includes("ref") ? [...t2.filter(((t3) => "ref" !== t3)), "ref"] : t2;
}
var tt = false, et = (t2, e2, n2) => {
  const o2 = e2.p[n2];
  let l2, r2, i2 = 0;
  if (null !== o2.u) l2 = o2.$ = u.document.createTextNode(o2.u);
  else {
    if (tt || (tt = "svg" === o2.m), !u.document) throw Error("You are trying to render a Stencil component in an environment that doesn't support the DOM. Make sure to populate the [`window`](https://developer.mozilla.org/en-US/docs/Web/API/Window/window) object before rendering a component.");
    if (l2 = o2.$ = u.document.createElementNS(tt ? "http://www.w3.org/2000/svg" : "http://www.w3.org/1999/xhtml", o2.m), tt && "foreignObject" === o2.m && (tt = false), X(null, o2, tt), o2.p) for (i2 = 0; i2 < o2.p.length; ++i2) r2 = et(t2, o2, i2), r2 && l2.appendChild(r2);
    "svg" === o2.m ? tt = false : "foreignObject" === l2.tagName && (tt = true);
  }
  return l2["s-hn"] = z, l2;
}, nt = (t2, e2, n2, o2, l2, r2) => {
  let i2, s2 = t2;
  for (s2.shadowRoot && s2.tagName === z && (s2 = s2.shadowRoot); l2 <= r2; ++l2) o2[l2] && (i2 = et(null, n2, l2), i2 && (o2[l2].$ = i2, st(s2, i2, e2)));
}, ot = (t2, e2, n2) => {
  for (let o2 = e2; o2 <= n2; ++o2) {
    const e3 = t2[o2];
    if (e3) {
      const t3 = e3.$;
      it(e3), t3 && t3.remove();
    }
  }
}, lt = (t2, e2, n2 = false) => t2.m === e2.m && (n2 ? (n2 && !t2.v && e2.v && (t2.v = e2.v), true) : t2.v === e2.v), rt = (t2, e2, n2 = false) => {
  const o2 = e2.$ = t2.$, l2 = t2.p, r2 = e2.p, i2 = e2.m, s2 = e2.u;
  null === s2 ? (X(t2, e2, tt = "svg" === i2 || "foreignObject" !== i2 && tt), null !== l2 && null !== r2 ? ((t3, e3, n3, o3, l3 = false) => {
    let r3, i3, s3 = 0, c2 = 0, u2 = 0, a2 = 0, f2 = e3.length - 1, d2 = e3[0], h2 = e3[f2], p2 = o3.length - 1, v2 = o3[0], m2 = o3[p2];
    for (; s3 <= f2 && c2 <= p2; ) if (null == d2) d2 = e3[++s3];
    else if (null == h2) h2 = e3[--f2];
    else if (null == v2) v2 = o3[++c2];
    else if (null == m2) m2 = o3[--p2];
    else if (lt(d2, v2, l3)) rt(d2, v2, l3), d2 = e3[++s3], v2 = o3[++c2];
    else if (lt(h2, m2, l3)) rt(h2, m2, l3), h2 = e3[--f2], m2 = o3[--p2];
    else if (lt(d2, m2, l3)) rt(d2, m2, l3), st(t3, d2.$, h2.$.nextSibling), d2 = e3[++s3], m2 = o3[--p2];
    else if (lt(h2, v2, l3)) rt(h2, v2, l3), st(t3, h2.$, d2.$), h2 = e3[--f2], v2 = o3[++c2];
    else {
      for (u2 = -1, a2 = s3; a2 <= f2; ++a2) if (e3[a2] && null !== e3[a2].v && e3[a2].v === v2.v) {
        u2 = a2;
        break;
      }
      u2 >= 0 ? (i3 = e3[u2], i3.m !== v2.m ? r3 = et(e3 && e3[c2], n3, u2) : (rt(i3, v2, l3), e3[u2] = void 0, r3 = i3.$), v2 = o3[++c2]) : (r3 = et(e3 && e3[c2], n3, c2), v2 = o3[++c2]), r3 && st(d2.$.parentNode, r3, d2.$);
    }
    s3 > f2 ? nt(t3, null == o3[p2 + 1] ? null : o3[p2 + 1].$, n3, o3, c2, p2) : c2 > p2 && ot(e3, s3, f2);
  })(o2, l2, e2, r2, n2) : null !== r2 ? (null !== t2.u && (o2.textContent = ""), nt(o2, null, e2, r2, 0, r2.length - 1)) : !n2 && null !== l2 && ot(l2, 0, l2.length - 1), tt && "svg" === i2 && (tt = false)) : t2.u !== s2 && (o2.data = s2);
}, it = (t2) => {
  t2.h && t2.h.ref && t2.h.ref(null), t2.p && t2.p.map(it);
}, st = (t2, e2, n2) => null == t2 ? void 0 : t2.insertBefore(e2, n2), ct = (t2, e2) => {
  if (e2 && !t2.j && e2["s-p"]) {
    const n2 = e2["s-p"].push(new Promise(((o2) => t2.j = () => {
      e2["s-p"].splice(n2 - 1, 1), o2();
    })));
  }
}, ut = (t2, e2) => {
  if (t2.o |= 16, 4 & t2.o) return void (t2.o |= 512);
  ct(t2, t2.O);
  const n2 = () => at(t2, e2);
  if (!e2) return $(n2);
  queueMicrotask((() => {
    n2();
  }));
}, at = (t2, e2) => {
  const n2 = t2.$hostElement$, o2 = t2.t;
  if (!o2) throw Error(`Can't render component <${n2.tagName.toLowerCase()} /> with invalid Stencil runtime! Make sure this imported component is compiled with a \`externalRuntime: true\` flag. For more information, please refer to https://stenciljs.com/docs/custom-elements#externalruntime`);
  let l2;
  return e2 ? (t2.o |= 256, t2.k && (t2.k.map((([t3, e3]) => wt(o2, t3, e3, n2))), t2.k = void 0), l2 = wt(o2, "componentWillLoad", void 0, n2)) : l2 = wt(o2, "componentWillUpdate", void 0, n2), l2 = ft(l2, (() => wt(o2, "componentWillRender", void 0, n2))), ft(l2, (() => ht(t2, o2, e2)));
}, ft = (t2, e2) => dt(t2) ? t2.then(e2).catch(((t3) => {
  console.error(t3), e2();
})) : e2(), dt = (t2) => t2 instanceof Promise || t2 && t2.then && "function" == typeof t2.then, ht = async (t2, e2, n2) => {
  var o2;
  const l2 = t2.$hostElement$, r2 = l2["s-rc"];
  n2 && ((t3) => {
    const e3 = t3.C, n3 = t3.$hostElement$, o3 = e3.o, l3 = ((t4, e4) => {
      var n4;
      const o4 = D(e4), l4 = i.get(o4);
      if (!u.document) return o4;
      if (t4 = 11 === t4.nodeType ? t4 : u.document, l4) if ("string" == typeof l4) {
        let r3, i2 = U.get(t4 = t4.head || t4);
        if (i2 || U.set(t4, i2 = /* @__PURE__ */ new Set()), !i2.has(o4)) {
          {
            r3 = u.document.createElement("style"), r3.innerHTML = l4;
            const o5 = null != (n4 = a.M) ? n4 : k(u.document);
            if (null != o5 && r3.setAttribute("nonce", o5), !(1 & e4.o)) if ("HEAD" === t4.nodeName) {
              const e5 = t4.querySelectorAll("link[rel=preconnect]"), n5 = e5.length > 0 ? e5[e5.length - 1].nextSibling : t4.querySelector("style");
              t4.insertBefore(r3, (null == n5 ? void 0 : n5.parentNode) === t4 ? n5 : null);
            } else if ("host" in t4) if (d) {
              const e5 = new CSSStyleSheet();
              e5.replaceSync(l4), h ? t4.adoptedStyleSheets.unshift(e5) : t4.adoptedStyleSheets = [e5, ...t4.adoptedStyleSheets];
            } else {
              const e5 = t4.querySelector("style");
              e5 ? e5.innerHTML = l4 + e5.innerHTML : t4.prepend(r3);
            }
            else t4.append(r3);
            1 & e4.o && t4.insertBefore(r3, null);
          }
          4 & e4.o && (r3.innerHTML += s), i2 && i2.add(o4);
        }
      } else t4.adoptedStyleSheets.includes(l4) || (h ? t4.adoptedStyleSheets.push(l4) : t4.adoptedStyleSheets = [...t4.adoptedStyleSheets, l4]);
      return o4;
    })(n3.shadowRoot ? n3.shadowRoot : n3.getRootNode(), e3);
    10 & o3 && (n3["s-sc"] = l3, n3.classList.add(l3 + "-h"));
  })(t2);
  pt(t2, e2, l2, n2), r2 && (r2.map(((t3) => t3())), l2["s-rc"] = void 0);
  {
    const e3 = null != (o2 = l2["s-p"]) ? o2 : [], n3 = () => vt(t2);
    0 === e3.length ? n3() : (Promise.all(e3).then(n3), t2.o |= 4, e3.length = 0);
  }
}, pt = (t2, e2, n2, o2) => {
  try {
    e2 = e2.render(), t2.o &= -17, t2.o |= 2, ((t3, e3, n3 = false) => {
      const o3 = t3.$hostElement$, l2 = t3.C, r2 = t3.P || A(null, null), i2 = ((t4) => t4 && t4.m === L)(e3) ? e3 : W$1(null, null, e3);
      if (z = o3.tagName, l2.N && (i2.h = i2.h || {}, l2.N.map((([t4, e4]) => i2.h[e4] = o3[t4]))), n3 && i2.h) for (const t4 of Object.keys(i2.h)) o3.hasAttribute(t4) && !["key", "ref", "style", "class"].includes(t4) && (i2.h[t4] = o3[t4]);
      i2.m = null, i2.o |= 4, t3.P = i2, i2.$ = r2.$ = o3.shadowRoot || o3, rt(r2, i2, n3);
    })(t2, e2, o2);
  } catch (e3) {
    l(e3, t2.$hostElement$);
  }
  return null;
}, vt = (t2) => {
  const e2 = t2.$hostElement$, n2 = t2.t, o2 = t2.O;
  wt(n2, "componentDidRender", void 0, e2), 64 & t2.o ? wt(n2, "componentDidUpdate", void 0, e2) : (t2.o |= 64, bt(e2), wt(n2, "componentDidLoad", void 0, e2), t2.R(e2), o2 || yt()), t2.U(e2), t2.j && (t2.j(), t2.j = void 0), 512 & t2.o && g((() => ut(t2, false))), t2.o &= -517;
}, mt = (t2) => {
  var n2;
  {
    const o2 = e(t2), l2 = null == (n2 = null == o2 ? void 0 : o2.$hostElement$) ? void 0 : n2.isConnected;
    return l2 && 2 == (18 & o2.o) && ut(o2, false), l2;
  }
}, yt = () => {
  g((() => J(u, "appload", { detail: { namespace: "lf-core" } })));
}, wt = (t2, e2, n2, o2) => {
  if (t2 && t2[e2]) try {
    return t2[e2](n2);
  } catch (t3) {
    l(t3, o2);
  }
}, bt = (t2) => t2.setAttribute("lf-hydrated", ""), gt = (t2, n2, o2, r2) => {
  const i2 = e(t2);
  if (!i2) return;
  if (!i2) throw Error(`Couldn't find host element for "${r2.i}" as it is unknown to this Stencil runtime. This usually happens when integrating a 3rd party Stencil component with another Stencil component or application. Please reach out to the maintainers of the 3rd party Stencil component or report this on the Stencil Discord server (https://chat.stenciljs.com) or comment on this similar [GitHub issue](https://github.com/stenciljs/core/issues/5457).`);
  const s2 = i2.$hostElement$, c2 = i2.D.get(n2), u2 = i2.o, a2 = i2.t;
  if (o2 = V(o2, r2.W[n2][0]), (!(8 & u2) || void 0 === c2) && o2 !== c2 && (!Number.isNaN(c2) || !Number.isNaN(o2)) && (i2.D.set(n2, o2), a2)) {
    if (r2.A && 128 & u2) {
      const t3 = r2.A[n2];
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
      ut(i2, false);
    }
  }
}, $t = (t2, n2, o2) => {
  var l2, r2;
  const i2 = t2.prototype;
  if (n2.W || n2.A || t2.watchers) {
    t2.watchers && !n2.A && (n2.A = t2.watchers);
    const s2 = Object.entries(null != (l2 = n2.W) ? l2 : {});
    if (s2.map((([t3, [l3]]) => {
      if (31 & l3 || 2 & o2 && 32 & l3) {
        const { get: r3, set: s3 } = Object.getOwnPropertyDescriptor(i2, t3) || {};
        r3 && (n2.W[t3][0] |= 2048), s3 && (n2.W[t3][0] |= 4096), (1 & o2 || !r3) && Object.defineProperty(i2, t3, { get() {
          {
            if (!(2048 & n2.W[t3][0])) return ((t4, n3) => e(this).D.get(n3))(0, t3);
            const o3 = e(this), l4 = o3 ? o3.t : i2;
            if (!l4) return;
            return l4[t3];
          }
        }, configurable: true, enumerable: true }), Object.defineProperty(i2, t3, { set(r4) {
          const i3 = e(this);
          if (i3) {
            if (s3) {
              const e2 = 32 & l3 ? this[t3] : i3.$hostElement$[t3];
              return void 0 === e2 && i3.D.get(t3) ? r4 = i3.D.get(t3) : !i3.D.get(t3) && e2 && i3.D.set(t3, e2), s3.call(this, V(r4, l3)), void gt(this, t3, r4 = 32 & l3 ? this[t3] : i3.$hostElement$[t3], n2);
            }
            {
              if (!(1 & o2 && 4096 & n2.W[t3][0])) return gt(this, t3, r4, n2), void (1 & o2 && !i3.t && i3.L.then((() => {
                4096 & n2.W[t3][0] && i3.t[t3] !== i3.D.get(t3) && (i3.t[t3] = r4);
              })));
              const e2 = () => {
                const e3 = i3.t[t3];
                !i3.D.get(t3) && e3 && i3.D.set(t3, e3), i3.t[t3] = V(r4, l3), gt(this, t3, i3.t[t3], n2);
              };
              i3.t ? e2() : i3.L.then((() => e2()));
            }
          }
        } });
      } else 1 & o2 && 64 & l3 && Object.defineProperty(i2, t3, { value(...n3) {
        var o3;
        const l4 = e(this);
        return null == (o3 = null == l4 ? void 0 : l4.F) ? void 0 : o3.then((() => {
          var e2;
          return null == (e2 = l4.t) ? void 0 : e2[t3](...n3);
        }));
      } });
    })), 1 & o2) {
      const o3 = /* @__PURE__ */ new Map();
      i2.attributeChangedCallback = function(t3, l3, r3) {
        a.jmp((() => {
          var s3;
          const c2 = o3.get(t3);
          if (this.hasOwnProperty(c2)) r3 = this[c2], delete this[c2];
          else {
            if (i2.hasOwnProperty(c2) && "number" == typeof this[c2] && this[c2] == r3) return;
            if (null == c2) {
              const o4 = e(this), i3 = null == o4 ? void 0 : o4.o;
              if (o4 && i3 && !(8 & i3) && 128 & i3 && r3 !== l3) {
                const e2 = o4.t, i4 = null == (s3 = n2.A) ? void 0 : s3[t3];
                null == i4 || i4.forEach(((n3) => {
                  null != e2[n3] && e2[n3].call(e2, r3, l3, t3);
                }));
              }
              return;
            }
          }
          const u2 = Object.getOwnPropertyDescriptor(i2, c2);
          (r3 = (null !== r3 || "boolean" != typeof this[c2]) && r3) === this[c2] || u2.get && !u2.set || (this[c2] = r3);
        }));
      }, t2.observedAttributes = Array.from(/* @__PURE__ */ new Set([...Object.keys(null != (r2 = n2.A) ? r2 : {}), ...s2.filter((([t3, e2]) => 31 & e2[0])).map((([t3, e2]) => {
        var l3;
        const r3 = e2[1] || t3;
        return o3.set(r3, t3), 512 & e2[0] && (null == (l3 = n2.N) || l3.push([t3, r3])), r3;
      }))]));
    }
  }
  return t2;
}, St = (t2, e2) => {
  wt(t2, "connectedCallback", void 0, e2);
}, jt = (t2, e2) => {
  wt(t2, "disconnectedCallback", void 0, e2 || t2);
}, Ot = (t2, n2 = {}) => {
  var o2;
  if (!u.document) return void console.warn("Stencil: No document found. Skipping bootstrapping lazy components.");
  const c2 = [], f2 = n2.exclude || [], h2 = u.customElements, p2 = u.document.head, v2 = p2.querySelector("meta[charset]"), m2 = u.document.createElement("style"), y2 = [];
  let w2, b2 = true;
  Object.assign(a, n2), a.l = new URL(n2.resourcesUrl || "./", u.document.baseURI).href;
  let g2 = false;
  if (t2.map(((t3) => {
    t3[1].map(((n3) => {
      var o3;
      const s2 = { o: n3[0], i: n3[1], W: n3[2], H: n3[3] };
      4 & s2.o && (g2 = true), s2.W = n3[2], s2.H = n3[3], s2.N = [], s2.A = null != (o3 = n3[4]) ? o3 : {};
      const u2 = s2.i, p3 = class extends HTMLElement {
        constructor(t4) {
          if (super(t4), this.hasRegisteredEventListeners = false, ((t5, e2) => {
            const n4 = { o: 0, $hostElement$: t5, C: e2, D: /* @__PURE__ */ new Map() };
            n4.F = new Promise(((t6) => n4.U = t6)), n4.L = new Promise(((t6) => n4.R = t6)), t5["s-p"] = [], t5["s-rc"] = [];
            const o4 = n4;
            t5.__stencil__getHostRef = () => o4;
          })(t4 = this, s2), 1 & s2.o) if (t4.shadowRoot) {
            if ("open" !== t4.shadowRoot.mode) throw Error(`Unable to re-use existing shadow root for ${s2.i}! Mode is set to ${t4.shadowRoot.mode} but Stencil only supports open shadow roots.`);
          } else R.call(t4, s2);
        }
        connectedCallback() {
          const t4 = e(this);
          t4 && (this.hasRegisteredEventListeners || (this.hasRegisteredEventListeners = true, Et(this, t4, s2.H)), w2 && (clearTimeout(w2), w2 = null), b2 ? y2.push(this) : a.jmp((() => ((t5) => {
            if (!(1 & a.o)) {
              const n4 = e(t5);
              if (!n4) return;
              const o4 = n4.C;
              if (1 & n4.o) Et(t5, n4, o4.H), (null == n4 ? void 0 : n4.t) ? St(n4.t, t5) : (null == n4 ? void 0 : n4.L) && n4.L.then((() => St(n4.t, t5)));
              else {
                n4.o |= 1;
                {
                  let e2 = t5;
                  for (; e2 = e2.parentNode || e2.host; ) if (e2["s-p"]) {
                    ct(n4, n4.O = e2);
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
                      const i2 = ((t7, e3) => {
                        const n6 = t7.i.replace(/-/g, "_"), o6 = t7.T;
                        if (!o6) return;
                        const i3 = r.get(o6);
                        return i3 ? i3[n6] : __variableDynamicImportRuntimeHelper(/* @__PURE__ */ Object.assign({ "./p-4ba08932.entry.js": () => import("./p-4ba08932.entry-xfvvy2N4.js"), "./p-60af2d7f.entry.js": () => import("./p-60af2d7f.entry-D9eOv8_y.js"), "./p-746a8577.entry.js": () => import("./p-746a8577.entry-BDGGzDKn.js"), "./p-7652d72d.entry.js": () => import("./p-7652d72d.entry-C0q2AFNm.js"), "./p-79cc15c2.entry.js": () => import("./p-79cc15c2.entry-C82cNBlZ.js"), "./p-846257eb.entry.js": () => import("./p-846257eb.entry-BpR5P0Ne.js"), "./p-84927cea.entry.js": () => import("./p-84927cea.entry-C7VkQxzE.js"), "./p-928c4970.entry.js": () => import("./p-928c4970.entry-CSCHynsT.js"), "./p-a147e6c9.entry.js": () => import("./p-a147e6c9.entry-CP6438MK.js"), "./p-a14c6d82.entry.js": () => import("./p-a14c6d82.entry-BYM_xg-V.js"), "./p-a7fc1135.entry.js": () => import("./p-a7fc1135.entry-Dpx1yUON.js"), "./p-bd214b33.entry.js": () => import("./p-bd214b33.entry-DclXjbaR.js"), "./p-bf8a47d4.entry.js": () => import("./p-bf8a47d4.entry-C4Ru_dxj.js"), "./p-ccea11a0.entry.js": () => import("./p-ccea11a0.entry-43a1p2EU.js"), "./p-dbe042fd.entry.js": () => import("./p-dbe042fd.entry-BkX1PUbc.js"), "./p-e2689624.entry.js": () => import("./p-e2689624.entry-B2Tq6McS.js") }), `./${o6}.entry.js`, 2).then(((t8) => (r.set(o6, t8), t8[n6])), ((t8) => {
                          l(t8, e3.$hostElement$);
                        }));
                        /*!__STENCIL_STATIC_IMPORT_SWITCH__*/
                      })(n5, e2);
                      if (i2 && "then" in i2) {
                        o5 = await i2;
                      } else o5 = i2;
                      if (!o5) throw Error(`Constructor for "${n5.i}#${e2.q}" was not found`);
                      o5.isProxied || (n5.A = o5.watchers, $t(o5, n5, 2), o5.isProxied = true);
                      e2.o |= 8;
                      try {
                        new o5(e2);
                      } catch (e3) {
                        l(e3, t6);
                      }
                      e2.o &= -9, e2.o |= 128, St(e2.t, t6);
                    } else o5 = t6.constructor, customElements.whenDefined(t6.localName).then((() => e2.o |= 128));
                    if (o5 && o5.style) {
                      let t7;
                      "string" == typeof o5.style && (t7 = o5.style);
                      const e3 = D(n5);
                      if (!i.has(e3)) {
                        ((t8, e4, n6) => {
                          let o6 = i.get(t8);
                          d && n6 ? (o6 = o6 || new CSSStyleSheet(), "string" == typeof o6 ? o6 = e4 : o6.replaceSync(e4)) : o6 = e4, i.set(t8, o6);
                        })(e3, t7, !!(1 & n5.o));
                      }
                    }
                  }
                  const s3 = e2.O, c3 = () => ut(e2, true);
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
              (null == n4 ? void 0 : n4.V) && (n4.V.map(((t5) => t5())), n4.V = void 0), (null == n4 ? void 0 : n4.t) ? jt(n4.t, t4) : (null == n4 ? void 0 : n4.L) && n4.L.then((() => jt(n4.t, t4)));
            }
            U.has(t4) && U.delete(t4), t4.shadowRoot && U.has(t4.shadowRoot) && U.delete(t4.shadowRoot);
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
          return null == (t4 = e(this)) ? void 0 : t4.L;
        }
      };
      s2.T = t3[0], f2.includes(u2) || h2.get(u2) || (c2.push(u2), h2.define(u2, $t(p3, s2, 1)));
    }));
  })), c2.length > 0 && (g2 && (m2.textContent += s), m2.textContent += c2.sort() + "{visibility:hidden}[lf-hydrated]{visibility:inherit}", m2.innerHTML.length)) {
    m2.setAttribute("data-styles", "");
    const t3 = null != (o2 = a.M) ? o2 : k(u.document);
    null != t3 && m2.setAttribute("nonce", t3), p2.insertBefore(m2, v2 ? v2.nextSibling : p2.firstChild);
  }
  b2 = false, y2.length ? y2.map(((t3) => t3.connectedCallback())) : a.jmp((() => w2 = setTimeout(yt, 30)));
}, kt = (t2, e2) => e2, Et = (t2, e2, n2) => {
  n2 && u.document && n2.map((([n3, o2, l2]) => {
    const r2 = t2, i2 = xt(e2, l2), s2 = Ct(n3);
    a.ael(r2, o2, i2, s2), (e2.V = e2.V || []).push((() => a.rel(r2, o2, i2, s2)));
  }));
}, xt = (t2, e2) => (n2) => {
  var o2;
  try {
    256 & t2.o ? null == (o2 = t2.t) || o2[e2](n2) : (t2.k = t2.k || []).push([e2, n2]);
  } catch (e3) {
    l(e3, t2.$hostElement$);
  }
}, Ct = (t2) => ({ passive: !!(1 & t2), capture: !!(2 & t2) });
const o = () => {
};
(() => {
  const l2 = import.meta.url, f$1 = {};
  return "" !== l2 && (f$1.resourcesUrl = new URL(".", l2).href), f(f$1);
})().then((async (e2) => (await o(), Ot(JSON.parse('[["p-746a8577",[[257,"lf-imageviewer",{"lfDataset":[1040,"lf-dataset"],"lfLoadCallback":[1040,"lf-load-callback"],"lfStyle":[1025,"lf-style"],"lfValue":[1040,"lf-value"],"debugInfo":[32],"currentShape":[32],"history":[32],"historyIndex":[32],"isSpinnerActive":[32],"addSnapshot":[64],"clearHistory":[64],"clearSelection":[64],"getComponents":[64],"getCurrentSnapshot":[64],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"reset":[64],"setSpinnerStatus":[64],"unmount":[64]}]]],["p-7652d72d",[[257,"lf-compare",{"lfDataset":[1040,"lf-dataset"],"lfShape":[1025,"lf-shape"],"lfStyle":[1025,"lf-style"],"lfView":[1025,"lf-view"],"debugInfo":[32],"isLeftPanelOpened":[32],"isRightPanelOpened":[32],"leftShape":[32],"rightShape":[32],"shapes":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfDataset":["updateShapes"],"lfShape":["updateShapes"]}]]],["p-4ba08932",[[257,"lf-accordion",{"lfDataset":[1040,"lf-dataset"],"lfRipple":[1028,"lf-ripple"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfStyle":[1025,"lf-style"],"debugInfo":[32],"expandedNodes":[32],"selectedNodes":[32],"getDebugInfo":[64],"getProps":[64],"getSelectedNodes":[64],"refresh":[64],"toggleNode":[64],"unmount":[64]}]]],["p-60af2d7f",[[257,"lf-article",{"lfDataset":[1040,"lf-dataset"],"lfEmpty":[1025,"lf-empty"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-84927cea",[[257,"lf-carousel",{"lfDataset":[1040,"lf-dataset"],"lfAutoPlay":[4,"lf-auto-play"],"lfInterval":[2,"lf-interval"],"lfLightbox":[1540,"lf-lightbox"],"lfNavigation":[1028,"lf-navigation"],"lfShape":[1537,"lf-shape"],"lfStyle":[1025,"lf-style"],"debugInfo":[32],"currentIndex":[32],"shapes":[32],"getDebugInfo":[64],"getProps":[64],"goToSlide":[64],"nextSlide":[64],"prevSlide":[64],"refresh":[64],"unmount":[64]},null,{"lfDataset":["updateShapes"],"lfShape":["updateShapes"]}]]],["p-bd214b33",[[257,"lf-messenger",{"lfAutosave":[1028,"lf-autosave"],"lfDataset":[1040,"lf-dataset"],"lfStyle":[1025,"lf-style"],"lfValue":[16,"lf-value"],"debugInfo":[32],"chat":[32],"connectionStatus":[32],"covers":[32],"currentCharacter":[32],"formStatusMap":[32],"history":[32],"hoveredCustomizationOption":[32],"saveInProgress":[32],"ui":[32],"deleteOption":[64],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"reset":[64],"save":[64],"unmount":[64]}]]],["p-846257eb",[[257,"lf-drawer",{"lfDisplay":[1537,"lf-display"],"lfPosition":[1537,"lf-position"],"lfResponsive":[1026,"lf-responsive"],"lfStyle":[1025,"lf-style"],"lfValue":[1540,"lf-value"],"debugInfo":[32],"close":[64],"getDebugInfo":[64],"getProps":[64],"isOpened":[64],"open":[64],"refresh":[64],"toggle":[64],"unmount":[64]},[[0,"keydown","listenKeydown"]],{"lfDisplay":["onLfDisplayChange"],"lfResponsive":["onLfResponsiveChange"]}]]],["p-e2689624",[[257,"lf-header",{"lfStyle":[1025,"lf-style"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-a7fc1135",[[257,"lf-placeholder",{"lfIcon":[1,"lf-icon"],"lfProps":[16,"lf-props"],"lfStyle":[1025,"lf-style"],"lfThreshold":[2,"lf-threshold"],"lfTrigger":[1,"lf-trigger"],"lfValue":[1,"lf-value"],"debugInfo":[32],"isInViewport":[32],"getComponent":[64],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-bf8a47d4",[[257,"lf-slider",{"lfLabel":[1025,"lf-label"],"lfLeadingLabel":[1028,"lf-leading-label"],"lfMax":[2,"lf-max"],"lfMin":[2,"lf-min"],"lfStep":[2,"lf-step"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1026,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setValue":[64],"unmount":[64]}]]],["p-a147e6c9",[[257,"lf-splash",{"lfLabel":[1025,"lf-label"],"lfStyle":[1025,"lf-style"],"debugInfo":[32],"state":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-ccea11a0",[[257,"lf-toast",{"lfCloseIcon":[1025,"lf-close-icon"],"lfCloseCallback":[16,"lf-close-callback"],"lfIcon":[1025,"lf-icon"],"lfTimer":[2,"lf-timer"],"lfMessage":[1025,"lf-message"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}]]],["p-dbe042fd",[[257,"lf-card",{"lfDataset":[1040,"lf-dataset"],"lfLayout":[1025,"lf-layout"],"lfSizeX":[1025,"lf-size-x"],"lfSizeY":[1025,"lf-size-y"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"debugInfo":[32],"shapes":[32],"getDebugInfo":[64],"getProps":[64],"getShapes":[64],"refresh":[64],"unmount":[64]},null,{"lfDataset":["updateShapes"]}],[257,"lf-badge",{"lfImageProps":[1040,"lf-image-props"],"lfLabel":[1025,"lf-label"],"lfPosition":[1537,"lf-position"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}],[257,"lf-canvas",{"lfBrush":[1025,"lf-brush"],"lfColor":[1025,"lf-color"],"lfCursor":[1025,"lf-cursor"],"lfImageProps":[1040,"lf-image-props"],"lfOpacity":[1026,"lf-opacity"],"lfPreview":[1028,"lf-preview"],"lfStrokeTolerance":[1026,"lf-stroke-tolerance"],"lfSize":[1026,"lf-size"],"lfStyle":[1025,"lf-style"],"debugInfo":[32],"isPainting":[32],"points":[32],"clearCanvas":[64],"getCanvas":[64],"getDebugInfo":[64],"getImage":[64],"getProps":[64],"refresh":[64],"resizeCanvas":[64],"setCanvasHeight":[64],"setCanvasWidth":[64],"unmount":[64]}],[257,"lf-photoframe",{"lfOverlay":[1040,"lf-overlay"],"lfPlaceholder":[16,"lf-placeholder"],"lfStyle":[1025,"lf-style"],"lfThreshold":[2,"lf-threshold"],"lfValue":[16,"lf-value"],"debugInfo":[32],"imageOrientation":[32],"isInViewport":[32],"isReady":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}],[257,"lf-chart",{"lfAxis":[1025,"lf-axis"],"lfColors":[1040,"lf-colors"],"lfDataset":[1040,"lf-dataset"],"lfLegend":[1025,"lf-legend"],"lfSeries":[1040,"lf-series"],"lfSizeX":[1025,"lf-size-x"],"lfSizeY":[1025,"lf-size-y"],"lfStyle":[1025,"lf-style"],"lfTypes":[1040,"lf-types"],"lfXAxis":[1040,"lf-x-axis"],"lfYAxis":[1040,"lf-y-axis"],"debugInfo":[32],"themeValues":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"resize":[64],"unmount":[64]}],[257,"lf-toggle",{"lfAriaLabel":[1025,"lf-aria-label"],"lfLabel":[1025,"lf-label"],"lfLeadingLabel":[1028,"lf-leading-label"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[4,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setValue":[64],"unmount":[64]}],[257,"lf-upload",{"lfLabel":[1025,"lf-label"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfValue":[16,"lf-value"],"debugInfo":[32],"selectedFiles":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"unmount":[64]}],[257,"lf-chat",{"lfContextWindow":[1026,"lf-context-window"],"lfEmpty":[1025,"lf-empty"],"lfEndpointUrl":[1025,"lf-endpoint-url"],"lfLayout":[1025,"lf-layout"],"lfMaxTokens":[1026,"lf-max-tokens"],"lfPollingInterval":[1026,"lf-polling-interval"],"lfSeed":[1026,"lf-seed"],"lfStyle":[1025,"lf-style"],"lfSystem":[1025,"lf-system"],"lfTemperature":[1026,"lf-temperature"],"lfTypewriterProps":[1040,"lf-typewriter-props"],"lfUiSize":[1537,"lf-ui-size"],"lfValue":[1040,"lf-value"],"debugInfo":[32],"history":[32],"currentPrompt":[32],"currentTokens":[32],"status":[32],"view":[32],"getDebugInfo":[64],"getHistory":[64],"getLastMessage":[64],"getProps":[64],"refresh":[64],"setHistory":[64],"unmount":[64]},[[0,"keydown","listenKeydown"]],{"lfPollingInterval":["updatePollingInterval"],"lfSystem":["updateTokensCount"]}],[257,"lf-chip",{"lfAriaLabel":[1025,"lf-aria-label"],"lfDataset":[1040,"lf-dataset"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfStyling":[1025,"lf-styling"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[16,"lf-value"],"debugInfo":[32],"expandedNodes":[32],"hiddenNodes":[32],"selectedNodes":[32],"getDebugInfo":[64],"getProps":[64],"getSelectedNodes":[64],"refresh":[64],"setSelectedNodes":[64],"unmount":[64]}],[257,"lf-code",{"lfFormat":[1028,"lf-format"],"lfLanguage":[1025,"lf-language"],"lfPreserveSpaces":[1028,"lf-preserve-spaces"],"lfShowCopy":[1028,"lf-show-copy"],"lfShowHeader":[1028,"lf-show-header"],"lfStickyHeader":[1028,"lf-sticky-header"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1025,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfLanguage":["loadLanguage"]}],[257,"lf-progressbar",{"lfAnimated":[1540,"lf-animated"],"lfCenteredLabel":[1540,"lf-centered-label"],"lfIcon":[1537,"lf-icon"],"lfIsRadial":[1540,"lf-is-radial"],"lfLabel":[1025,"lf-label"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1026,"lf-value"],"debugInfo":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]}],[257,"lf-textfield",{"lfHelper":[1040,"lf-helper"],"lfHtmlAttributes":[1040,"lf-html-attributes"],"lfIcon":[1025,"lf-icon"],"lfLabel":[1025,"lf-label"],"lfStretchX":[1540,"lf-stretch-x"],"lfStretchY":[1540,"lf-stretch-y"],"lfStyle":[1025,"lf-style"],"lfStyling":[1025,"lf-styling"],"lfTrailingIcon":[1540,"lf-trailing-icon"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1,"lf-value"],"debugInfo":[32],"status":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setBlur":[64],"setFocus":[64],"setValue":[64],"unmount":[64]}],[257,"lf-typewriter",{"lfCursor":[1025,"lf-cursor"],"lfDeleteSpeed":[1026,"lf-delete-speed"],"lfLoop":[1028,"lf-loop"],"lfPause":[1026,"lf-pause"],"lfSpeed":[1026,"lf-speed"],"lfStyle":[1025,"lf-style"],"lfTag":[1025,"lf-tag"],"lfUiSize":[1537,"lf-ui-size"],"lfUpdatable":[1028,"lf-updatable"],"lfValue":[1025,"lf-value"],"debugInfo":[32],"displayedText":[32],"isDeleting":[32],"currentTextIndex":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfValue":["handleLfValueChange"]}],[257,"lf-image",{"lfHtmlAttributes":[1040,"lf-html-attributes"],"lfMode":[1537,"lf-mode"],"lfShowSpinner":[1028,"lf-show-spinner"],"lfSizeX":[1025,"lf-size-x"],"lfSizeY":[1025,"lf-size-y"],"lfStyle":[1025,"lf-style"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[1025,"lf-value"],"debugInfo":[32],"error":[32],"isLoaded":[32],"resolvedSpriteName":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfValue":["resetState"]}],[257,"lf-button",{"lfAriaLabel":[1025,"lf-aria-label"],"lfDataset":[1040,"lf-dataset"],"lfIcon":[1025,"lf-icon"],"lfIconOff":[1025,"lf-icon-off"],"lfLabel":[1025,"lf-label"],"lfRipple":[1028,"lf-ripple"],"lfShowSpinner":[1540,"lf-show-spinner"],"lfStretchX":[1540,"lf-stretch-x"],"lfStretchY":[1540,"lf-stretch-y"],"lfStyle":[1025,"lf-style"],"lfStyling":[1025,"lf-styling"],"lfToggable":[1028,"lf-toggable"],"lfTrailingIcon":[1028,"lf-trailing-icon"],"lfType":[1025,"lf-type"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[4,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setMessage":[64],"setValue":[64],"unmount":[64]}],[257,"lf-list",{"lfDataset":[1040,"lf-dataset"],"lfEmpty":[1025,"lf-empty"],"lfEnableDeletions":[1028,"lf-enable-deletions"],"lfNavigation":[1028,"lf-navigation"],"lfRipple":[1028,"lf-ripple"],"lfSelectable":[1028,"lf-selectable"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[2,"lf-value"],"debugInfo":[32],"focused":[32],"selected":[32],"focusNext":[64],"focusPrevious":[64],"getDebugInfo":[64],"getProps":[64],"getSelected":[64],"refresh":[64],"selectNode":[64],"unmount":[64]},[[0,"keydown","listenKeydown"]]],[257,"lf-spinner",{"lfActive":[1540,"lf-active"],"lfBarVariant":[1540,"lf-bar-variant"],"lfDimensions":[1025,"lf-dimensions"],"lfFader":[1540,"lf-fader"],"lfFaderTimeout":[1026,"lf-fader-timeout"],"lfFullScreen":[1540,"lf-full-screen"],"lfLayout":[1026,"lf-layout"],"lfStyle":[1025,"lf-style"],"lfTimeout":[1026,"lf-timeout"],"bigWait":[32],"debugInfo":[32],"progress":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfActive":["onFaderChange"],"lfFader":["onFaderChange"],"lfFaderTimeout":["onFaderChange"],"lfBarVariant":["lfBarVariantChanged"],"lfTimeout":["lfTimeoutChanged"]}]]],["p-79cc15c2",[[257,"lf-masonry",{"lfActions":[1028,"lf-actions"],"lfColumns":[1026,"lf-columns"],"lfDataset":[1040,"lf-dataset"],"lfSelectable":[1540,"lf-selectable"],"lfShape":[1025,"lf-shape"],"lfStyle":[1025,"lf-style"],"lfView":[1025,"lf-view"],"debugInfo":[32],"selectedShape":[32],"shapes":[32],"viewportWidth":[32],"getDebugInfo":[64],"getProps":[64],"getSelectedShape":[64],"redecorateShapes":[64],"refresh":[64],"setSelectedShape":[64],"unmount":[64]},null,{"lfColumns":["validateColumns"],"lfDataset":["updateShapes"],"lfShape":["updateShapes"]}]]],["p-928c4970",[[257,"lf-tabbar",{"lfAriaLabel":[1025,"lf-aria-label"],"lfDataset":[16,"lf-dataset"],"lfNavigation":[4,"lf-navigation"],"lfRipple":[1028,"lf-ripple"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"lfUiState":[1025,"lf-ui-state"],"lfValue":[8,"lf-value"],"debugInfo":[32],"value":[32],"getDebugInfo":[64],"getProps":[64],"getValue":[64],"refresh":[64],"setValue":[64],"unmount":[64]}]]],["p-a14c6d82",[[257,"lf-tree",{"lfAccordionLayout":[1540,"lf-accordion-layout"],"lfDataset":[1040,"lf-dataset"],"lfEmpty":[1025,"lf-empty"],"lfFilter":[1028,"lf-filter"],"lfGrid":[1540,"lf-grid"],"lfInitialExpansionDepth":[1026,"lf-initial-expansion-depth"],"lfRipple":[1028,"lf-ripple"],"lfSelectable":[1540,"lf-selectable"],"lfStyle":[1025,"lf-style"],"lfUiSize":[1537,"lf-ui-size"],"debugInfo":[32],"expandedNodes":[32],"hiddenNodes":[32],"selectedNode":[32],"getDebugInfo":[64],"getProps":[64],"refresh":[64],"unmount":[64]},null,{"lfDataset":["handleDatasetChange"],"lfInitialExpansionDepth":["handleInitialDepthChange"]}]]]]'), e2))));
var APIEndpoints;
(function(APIEndpoints2) {
  APIEndpoints2["ClearAnalytics"] = "/lf-nodes/clear-analytics";
  APIEndpoints2["ClearMetadata"] = "/lf-nodes/clear-metadata";
  APIEndpoints2["LFFree"] = "/lf-nodes/free";
  APIEndpoints2["LFRefreshNodeDefs"] = "/lf-nodes/refresh-node-defs";
  APIEndpoints2["GetAnalytics"] = "/lf-nodes/get-analytics";
  APIEndpoints2["GetImage"] = "/lf-nodes/get-image";
  APIEndpoints2["GetJson"] = "/lf-nodes/get-json";
  APIEndpoints2["GetMetadata"] = "/lf-nodes/get-metadata";
  APIEndpoints2["NewBackup"] = "/lf-nodes/new-backup";
  APIEndpoints2["ProcessImage"] = "/lf-nodes/process-image";
  APIEndpoints2["SaveMetadata"] = "/lf-nodes/save-metadata";
  APIEndpoints2["UpdateJson"] = "/lf-nodes/update-json";
  APIEndpoints2["UpdateMetadataCover"] = "/lf-nodes/update-metadata-cover";
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
    const lfManager2 = getLfManager();
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
      const code = response.status;
      switch (code) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.message = p2.message;
            payload.status = LogSeverity.Success;
            lfManager2.getCachedDatasets().usage = {};
          }
          break;
        case 404:
          payload.message = `Analytics not found: ${type}. Skipping deletion.`;
          payload.status = LogSeverity.Info;
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the clear-analytics ${type} API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region get
  get: async (directory, type) => {
    const lfManager2 = getLfManager();
    const payload = {
      data: {},
      message: "",
      status: LogSeverity.Info
    };
    if (!directory || !type) {
      payload.message = `Missing directory (received ${directory}) or  (received ${type}).`;
      payload.status = LogSeverity.Error;
      lfManager2.log(payload.message, { payload }, LogSeverity.Error);
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
      const code = response.status;
      switch (code) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.message = "Analytics data fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager2.log(payload.message, { payload }, payload.status);
            lfManager2.getCachedDatasets().usage = payload.data;
          }
          break;
        case 404:
          payload.status = LogSeverity.Info;
          lfManager2.log(`${type} analytics file not found.`, { payload }, payload.status);
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the get-analytics ${type} API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const BACKUP_API = {
  //#region new
  new: async (backupType = "automatic") => {
    const lfManager2 = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const body = new FormData();
      body.append("backup_type", backupType);
      const response = await api.fetchApi(APIEndpoints.NewBackup, { body, method: "POST" });
      const code = response.status;
      switch (code) {
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
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
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
    } catch (error) {
      getLfManager().log(`Command ${name} not executed!`, { error }, LogSeverity.Warning);
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
    const lfManager2 = getLfManager();
    const REPO = "lf-nodes";
    const USER = "lucafoscili";
    const payload = {
      data: null,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await fetch(`https://api.github.com/repos/${USER}/${REPO}/releases/latest`);
      const code = response.status;
      switch (code) {
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
    } catch (error) {
      payload.message = `Error fetching release info: ${error}`;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const IMAGE_API = {
  //#region get
  get: async (directory) => {
    const lfManager2 = getLfManager();
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
      const code = response.status;
      switch (code) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.message = "Images fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager2.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the get-image API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region process
  process: async (url, type, settings) => {
    const lfManager2 = getLfManager();
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
      const code = response.status;
      switch (code) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.mask = p2.mask;
            payload.message = "Image processed successfully.";
            payload.status = LogSeverity.Success;
            lfManager2.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          {
            const errorText = await response.text().catch(() => "");
            payload.message = `Unexpected response from the process-image API (${code}): ${errorText || response.statusText}`;
          }
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const JSON_API = {
  //#region get
  get: async (filePath) => {
    const lfManager2 = getLfManager();
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
      const code = response.status;
      switch (code) {
        case 200:
          const p2 = await response.json();
          if (p2.status === "success") {
            payload.data = p2.data;
            payload.message = "JSON data fetched successfully.";
            payload.status = LogSeverity.Success;
            lfManager2.log(payload.message, { payload }, payload.status);
          }
          break;
        default:
          payload.message = `Unexpected response from the get-json API: ${await response.text()}`;
          payload.status = LogSeverity.Error;
          break;
      }
    } catch (error) {
      payload.message = error.toString();
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region update
  update: async (filePath, dataset) => {
    const lfManager2 = getLfManager();
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
      const code = response.status;
      switch (code) {
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
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const METADATA_API = {
  //#region clear
  clear: async () => {
    const lfManager2 = getLfManager();
    const payload = {
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await api.fetchApi(APIEndpoints.ClearMetadata, {
        method: "POST"
      });
      const code = response.status;
      switch (code) {
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
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region get
  get: async (hash) => {
    const lfManager2 = getLfManager();
    const payload = {
      data: null,
      message: "",
      status: LogSeverity.Info
    };
    try {
      const response = await fetch(`https://civitai.com/api/v1/model-versions/by-hash/${hash}`);
      const code = response.status;
      switch (code) {
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
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region save
  save: async (modelPath, dataset, forcedSave = false) => {
    const lfManager2 = getLfManager();
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
      const code = response.status;
      switch (code) {
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
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  },
  //#endregion
  //#region updateCover
  updateCover: async (modelPath, b64image) => {
    const lfManager2 = getLfManager();
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
      const code = response.status;
      switch (code) {
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
    } catch (error) {
      payload.message = error;
      payload.status = LogSeverity.Error;
    }
    lfManager2.log(payload.message, { payload }, payload.status);
    return payload;
  }
  //#endregion
};
const MODELS_API = {
  free: async () => {
    const lfManager2 = getLfManager();
    try {
      const response = await api.fetchApi(APIEndpoints.LFFree, { method: "POST" });
      if (response.status === 200) {
        return true;
      }
      lfManager2.log('"free" endpoint returned non-200', { status: response.status }, LogSeverity.Warning);
      return false;
    } catch (error) {
      lfManager2.log('"free" endpoint failed', { error }, LogSeverity.Warning);
      return false;
    }
  },
  refresh: async () => {
    const lfManager2 = getLfManager();
    try {
      const response = await api.fetchApi(APIEndpoints.LFRefreshNodeDefs, { method: "POST" });
      if (response.status === 200) {
        return true;
      }
      lfManager2.log('"refresh-node-defs" endpoint returned non-200', { status: response.status }, LogSeverity.Warning);
      return false;
    } catch (error) {
      lfManager2.log('"refresh-node-defs" endpoint failed', { error }, LogSeverity.Warning);
      return false;
    }
  }
};
const beforeFree = async (options) => {
  const lfManager2 = getLfManager();
  lfManager2.log("Unload triggered — clearing LF caches first…", { options }, LogSeverity.Info);
  try {
    const ok2 = await MODELS_API.free();
    if (ok2) {
      lfManager2.log("Caches cleared ✔️", {}, LogSeverity.Success);
    } else {
      lfManager2.log("Cache clear call returned non-200", {}, LogSeverity.Warning);
    }
  } catch (error) {
    lfManager2.log("Error while clearing caches", { error }, LogSeverity.Warning);
  }
};
const beforeRefreshNodeDefs = async (trigger) => {
  const lfManager2 = getLfManager();
  lfManager2.log("Refresh requested — clearing LF caches first…", { trigger }, LogSeverity.Info);
  try {
    const ok2 = await MODELS_API.refresh();
    if (ok2) {
      lfManager2.log("Refresh caches cleared ✔️", {}, LogSeverity.Success);
    } else {
      lfManager2.log("Refresh cache clear call returned non-200", {}, LogSeverity.Warning);
    }
  } catch (error) {
    lfManager2.log("Error while clearing caches ahead of refresh", { error }, LogSeverity.Warning);
  }
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
  NodeName2["tiltShift"] = "LF_TiltShift";
  NodeName2["updateUsageStatistics"] = "LF_UpdateUsageStatistics";
  NodeName2["upscaleModelSelector"] = "LF_UpscaleModelSelector";
  NodeName2["urandomSeedGenerator"] = "LF_UrandomSeedGenerator";
  NodeName2["usageStatistics"] = "LF_UsageStatistics";
  NodeName2["vaeDecode"] = "LF_VAEDecode";
  NodeName2["vaeSelector"] = "LF_VAESelector";
  NodeName2["onnxSelector"] = "LF_ONNXSelector";
  NodeName2["viewImages"] = "LF_ViewImages";
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
    } catch (err2) {
      (_b = (_a = getLfManager()) == null ? void 0 : _a.log) == null ? void 0 : _b.call(_a, "onAfterGraphConfigured hook error", { err: err2 }, LogSeverity.Warning);
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
  const lfManager2 = getLfManager();
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
    lfManager2.log("Missing options", { chipW, datasetW }, LogSeverity.Warning);
    return;
  }
  const dataset = datasetW.options.getValue();
  const chip = chipW.options.getState().chip;
  try {
    const newData = unescapeJson(dataset).parsedJson;
    if (isValidJSON(newData) && isValidJSON(chip.lfDataset)) {
      if (!areJSONEqual(newData, chip.lfDataset)) {
        chip.lfDataset = newData;
        lfManager2.log("Updated chip data", { dataset }, LogSeverity.Info);
      }
    } else {
      if (isValidJSON(newData)) {
        chip.lfDataset = newData;
        lfManager2.log("Set chip data", { dataset }, LogSeverity.Info);
      } else {
        lfManager2.log("Invalid JSON data", { dataset, error: "Invalid JSON" }, LogSeverity.Warning);
      }
    }
  } catch (error) {
    lfManager2.log("Error processing chip data", { dataset, error }, LogSeverity.Error);
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
  } catch (error) {
    getLfManager().log("Error processing messenger data", { dataset, error }, LogSeverity.Error);
  }
};
const setCanvasSizeCb = async (imageviewer) => {
  requestAnimationFrame(async () => {
    try {
      const { canvas } = (await imageviewer.getComponents()).details;
      canvas.resizeCanvas();
    } catch (error) {
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
  ImageEditorToggleIds2["Vertical"] = "vertical";
  ImageEditorToggleIds2["UseConditioning"] = "use_conditioning";
  ImageEditorToggleIds2["RoiAuto"] = "roi_auto";
  ImageEditorToggleIds2["RoiAlignAuto"] = "roi_align_auto";
})(ImageEditorToggleIds || (ImageEditorToggleIds = {}));
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
  ImageEditorClarityIds2["BlurKernelSize"] = "blur_kernel_size";
  ImageEditorClarityIds2["Strength"] = "strength";
  ImageEditorClarityIds2["SharpenAmount"] = "sharpen_amount";
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
const SETTINGS = {
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
  //#region Brush
  brush: {
    controlIds: ImageEditorBrushIds,
    hasCanvasAction: true,
    settings: { b64_canvas: "", color: "#FF0000", opacity: 1, size: 10 },
    configs: {
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
      ]
    }
  },
  //#endregion
  //#region Clarity
  clarity: {
    controlIds: ImageEditorClarityIds,
    settings: {
      strength: 0,
      sharpen_amount: 0,
      blur_kernel_size: 1
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: "Clarity Strength",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: "5",
          min: "0",
          step: "0.1",
          title: "Controls the amount of contrast enhancement in midtones."
        },
        {
          ariaLabel: "Sharpen Amount",
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.SharpenAmount,
          max: "5",
          min: "0",
          step: "0.1",
          title: "Controls how much sharpening is applied to the image."
        },
        {
          ariaLabel: "Blur Kernel Size",
          controlType: ImageEditorControls.Slider,
          defaultValue: 7,
          id: ImageEditorSliderIds.BlurKernelSize,
          max: "15",
          min: "1",
          step: "2",
          title: "Controls the size of the Gaussian blur kernel. Higher values mean more smoothing."
        }
      ]
    }
  },
  //#endregion
  //#region Unsharp mask
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
          title: "Controls the total intensity of the desaturation. 0 is no effect, 1 is fully desaturated."
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
  //#region Film grain
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
  //#region Gaussian blur
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
      use_conditioning: false
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
          defaultValue: false,
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
          defaultValue: 0,
          id: ImageEditorSliderIds.UpsampleTarget,
          isMandatory: false,
          max: "2048",
          min: "0",
          step: "16",
          title: "Detailer path: upscale ROI longer side to this size before inpaint (0 disables)."
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
  //#region Split tone
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
  //#region Tilt-shift
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
const INPAINT_ADV = {
  controlIds: ImageEditorInpaintIds,
  hasCanvasAction: true,
  requiresManualApply: true,
  settings: {
    ...SETTINGS.inpaint.settings,
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
};
const TREE_DATA = {
  nodes: [
    {
      description: "Tool configuration.",
      id: "settings",
      icon: "brush",
      value: "Settings",
      children: [
        //#region Brush
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
        //#endregion
      ]
    },
    {
      description: "Diffusion-based retouching tools.",
      id: "diffusion_tools",
      value: "Diffusion Tools",
      icon: "wand",
      children: [
        //#region Inpaint
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
        //#endregion
      ]
    },
    {
      description: "Basic adjustments such as sharpening and color tuning.",
      id: "basic_adjustments",
      value: "Basic Adjustments",
      icon: "settings",
      children: [
        //#region Brightness
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
        //#endregion
        //#region Clarity
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
        //#endregion
        //#region Unsharp mask
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
        //#endregion
        //#region Contrast
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
        //#endregion
        //#region Desaturate
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
        //#endregion
        //#region Saturation
        {
          cells: {
            lfCode: {
              shape: "code",
              value: JSON.stringify(SETTINGS.saturation)
            }
          },
          description: "Adjusts the saturation.",
          id: "saturation",
          value: "Saturation"
        }
        //#endregion
      ]
    },
    {
      description: "Artistic filters, such as vignette effect and gaussian blur.",
      id: "creative_effects",
      icon: "palette",
      value: "Creative Effects",
      children: [
        //#region Blend
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
        //#endregion
        //#region Bloom
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
        //#endregion
        //#region Film grain
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
        //#endregion
        //#region Gaussian blur
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
        //#endregion
        //#region Line
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
        //#endregion
        //#region Sepia
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
        //#endregion
        //#region Split tone
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
        //#endregion
        //#region Tilt-shift
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
        //#endregion
        //#region Vibrance
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
        //#endregion
        //#region Vignette
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
        //#endregion
      ]
    }
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
const handleInterruptForState = async (state) => {
  var _a, _b;
  const lfManager2 = getLfManager();
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
      } catch (error) {
        lfManager2.log("Failed to update JSON after workflow interrupt.", { error, path }, LogSeverity.Warning);
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
    } catch (error) {
      lfManager2.log("Failed to reset image viewer after workflow interrupt.", { error }, LogSeverity.Warning);
    }
  }
  await resetSettings(imageviewer);
};
const EV_HANDLERS$a = {
  //#region Button handler
  button: async (state, e2) => {
    var _a;
    const { comp, eventType } = e2.detail;
    if (eventType === "click") {
      const isPatched = ((_a = api) == null ? void 0 : _a[LFInterruptFlags.PatchedInterrupt]) === true;
      switch (comp.lfIcon) {
        case ImageEditorIcons.Interrupt:
          getApiRoutes().comfy.interrupt();
          if (!isPatched) {
            await handleInterruptForState(state);
          }
          break;
        case ImageEditorIcons.Resume:
          await handleInterruptForState(state);
          break;
      }
    }
  },
  //#endregion
  //#region Canvas handler
  canvas: async (state, e2) => {
    const { comp, eventType, points } = e2.detail;
    const { filter, filterType } = state;
    switch (eventType) {
      case "stroke":
        const originalFilter = filter;
        const originalFilterType = filterType;
        const canvas = await comp.getCanvas();
        const b64_canvas = canvasToBase64(canvas);
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
            b64_canvas,
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
              b64_canvas
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
  //#region Imageviewer handler
  imageviewer: async (state, e2) => {
    var _a;
    const { comp, eventType, originalEvent } = e2.detail;
    const { node } = state;
    switch (eventType) {
      case "lf-event":
        const ogEv = originalEvent;
        switch (ogEv.detail.eventType) {
          case "click":
            if (isTree(ogEv.detail.comp)) {
              const { node: node2 } = ogEv.detail;
              if ((_a = node2.cells) == null ? void 0 : _a.lfCode) {
                prepSettings(state, node2);
              }
            }
            break;
          case "stroke":
            const canvasEv = ogEv;
            EV_HANDLERS$a.canvas(state, canvasEv);
            break;
        }
        break;
      case "ready":
        const { details, navigation } = await comp.getComponents();
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
  },
  //#endregion
  //#region Slider handler
  slider: async (state, e2) => {
    const { eventType } = e2.detail;
    const { update } = state;
    const { preview, snapshot } = update;
    switch (eventType) {
      case "change":
        snapshot();
        break;
      case "input":
        const debouncedCallback = debounce(preview, 300);
        debouncedCallback();
        break;
    }
  },
  //#endregion
  //#region Textfield handler
  textfield: async (state, e2) => {
    const { eventType } = e2.detail;
    const { update } = state;
    const { preview, snapshot } = update;
    switch (eventType) {
      case "change":
        snapshot();
        break;
      case "input":
        const debouncedCallback = debounce(preview, 300);
        debouncedCallback();
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
        snapshot();
        break;
    }
  }
  //#endregion
};
const apiCall$2 = async (state, addSnapshot) => {
  const { elements, filter, filterType } = state;
  const { imageviewer } = elements;
  const lfManager2 = getLfManager();
  const snapshotValue = (await imageviewer.getCurrentSnapshot()).value;
  const baseSettings = filter.settings;
  const payload = {
    ...baseSettings
  };
  const contextDataset = imageviewer.lfDataset;
  const contextId = contextDataset == null ? void 0 : contextDataset.context_id;
  if (contextId) {
    payload.context_id = contextId;
  }
  requestAnimationFrame(() => imageviewer.setSpinnerStatus(true));
  try {
    const response = await getApiRoutes().image.process(snapshotValue, filterType, payload);
    if (response.mask) {
      lfManager2.log("Saved inpaint mask preview to temp", { mask: response.mask }, LogSeverity.Info);
    }
    if (addSnapshot) {
      await imageviewer.addSnapshot(response.data);
    } else {
      const { canvas } = (await imageviewer.getComponents()).details;
      const image = await canvas.getImage();
      requestAnimationFrame(() => image.lfValue = response.data);
    }
  } catch (error) {
    lfManager2.log("Error processing image!", { error }, LogSeverity.Error);
  }
  requestAnimationFrame(() => imageviewer.setSpinnerStatus(false));
};
const refreshValues = async (state, addSnapshot = false) => {
  const { elements, filter } = state;
  const { controls } = elements;
  const lfManager2 = getLfManager();
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
          lfManager2.log(`Unhandled control type: ${control.tagName}`, { control }, LogSeverity.Warning);
          continue;
      }
    }
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
    configs == null ? void 0 : configs.forEach((config) => {
      const defaultValue = defaults[config.id];
      if (typeof defaultValue === "undefined") {
        return;
      }
      switch (controlType) {
        case ImageEditorControls.Slider: {
          const numericValue = typeof defaultValue === "number" ? defaultValue : Number(defaultValue);
          config.defaultValue = numericValue;
          mutableSettings[config.id] = numericValue;
          break;
        }
        case ImageEditorControls.Textfield: {
          const stringValue = defaultValue === null || typeof defaultValue === "undefined" ? "" : String(defaultValue);
          config.defaultValue = stringValue;
          mutableSettings[config.id] = stringValue;
          break;
        }
        case ImageEditorControls.Toggle: {
          const toggleConfig = config;
          const boolValue = defaultValue === true || typeof defaultValue === "string" && defaultValue.toLowerCase() === "true";
          toggleConfig.defaultValue = boolValue;
          mutableSettings[config.id] = boolValue ? toggleConfig.on : toggleConfig.off;
          break;
        }
      }
    });
  });
};
const prepSettings = (state, node) => {
  var _a;
  state.elements.controls = {};
  state.filter = unescapeJson(node.cells.lfCode.value).parsedJson;
  const idRaw = node.id || "brush";
  const alias = idRaw === "inpaint_detail" || idRaw === "inpaint_adv" ? "inpaint" : idRaw;
  state.filterType = alias;
  const dataset = state.elements.imageviewer.lfDataset;
  const defaults = (_a = dataset == null ? void 0 : dataset.defaults) == null ? void 0 : _a[state.filterType];
  if (defaults) {
    applyFilterDefaults(state, defaults);
  }
  state.settingsStore = state.settingsStore ?? {};
  const stored = state.settingsStore[state.filterType] ?? {};
  const mutableSettings = state.filter.settings;
  Object.keys(stored).forEach((id) => {
    const v2 = stored[id];
    if (typeof v2 === "undefined")
      return;
    mutableSettings[id] = v2;
  });
  const { elements, filter } = state;
  const { settings } = elements;
  settings.innerHTML = "";
  const controlsContainer = document.createElement(TagName.Div);
  controlsContainer.classList.add(ImageEditorCSS.SettingsControls);
  settings.appendChild(controlsContainer);
  const controlNames = Object.keys(filter.configs);
  controlNames.forEach((controlName) => {
    const controls = filter.configs[controlName];
    if (controls) {
      controls.forEach((control) => {
        switch (controlName) {
          case ImageEditorControls.Slider:
            const slider = createSlider(state, control);
            const storedValueSlider = stored[control.id];
            if (typeof storedValueSlider !== "undefined") {
              slider.lfValue = Number(storedValueSlider);
            }
            controlsContainer.appendChild(slider);
            state.elements.controls[control.id] = slider;
            break;
          case ImageEditorControls.Textfield:
            const textfield = createTextfield(state, control);
            const storedValueText = stored[control.id];
            if (typeof storedValueText !== "undefined") {
              textfield.lfValue = String(storedValueText);
            }
            controlsContainer.appendChild(textfield);
            state.elements.controls[control.id] = textfield;
            break;
          case ImageEditorControls.Toggle:
            const toggle = createToggle(state, control);
            const storedValueToggle = stored[control.id];
            if (typeof storedValueToggle !== "undefined") {
              const bool = storedValueToggle === true || typeof storedValueToggle === "string" && storedValueToggle.toLowerCase() === "true";
              toggle.lfValue = bool;
            }
            controlsContainer.appendChild(toggle);
            state.elements.controls[control.id] = toggle;
            break;
          default:
            throw new Error(`Unknown control type: ${controlName}`);
        }
      });
    }
  });
  const buttonsWrapper = document.createElement(TagName.Div);
  buttonsWrapper.classList.add(ImageEditorCSS.SettingsButtons);
  settings.appendChild(buttonsWrapper);
  const resetButton = document.createElement(TagName.LfButton);
  resetButton.lfIcon = ImageEditorIcons.Reset;
  resetButton.lfLabel = "Reset";
  resetButton.lfStretchX = true;
  resetButton.addEventListener("click", () => resetSettings(settings));
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
    applyButton.addEventListener("click", () => {
      void updateCb(state, true, true);
    });
    buttonsWrapper.appendChild(applyButton);
  }
};
const createSlider = (state, data) => {
  const comp = document.createElement(TagName.LfSlider);
  comp.lfLabel = parseLabel(data);
  comp.lfLeadingLabel = true;
  comp.lfMax = Number(data.max);
  comp.lfMin = Number(data.min);
  comp.lfStep = Number(data.step);
  comp.lfStyle = ".form-field { width: 100%; }";
  comp.lfValue = Number(data.defaultValue);
  comp.title = data.title;
  comp.addEventListener(LfEventName.LfSlider, (e2) => EV_HANDLERS$a.slider(state, e2));
  return comp;
};
const createTextfield = (state, data) => {
  const comp = document.createElement(TagName.LfTextfield);
  comp.lfLabel = parseLabel(data);
  comp.lfHtmlAttributes = { type: data.type };
  comp.lfValue = String(data.defaultValue).valueOf();
  comp.title = data.title;
  comp.addEventListener(LfEventName.LfTextfield, (e2) => EV_HANDLERS$a.textfield(state, e2));
  return comp;
};
const createToggle = (state, data) => {
  const comp = document.createElement(TagName.LfToggle);
  comp.dataset.off = data.off;
  comp.dataset.on = data.on;
  comp.lfLabel = parseLabel(data);
  comp.lfValue = data.defaultValue ?? false;
  comp.title = data.title;
  comp.addEventListener(LfEventName.LfToggle, (e2) => EV_HANDLERS$a.toggle(state, e2));
  return comp;
};
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
async function resetSettings(settings) {
  const controls = Array.from(settings.querySelectorAll("[data-id]"));
  for (const control of controls) {
    switch (control.tagName) {
      case "LF-SLIDER":
        const slider = control;
        await slider.setValue(slider.lfValue);
        await slider.refresh();
        break;
      case "LF-TEXTFIELD":
        const textfield = control;
        await textfield.setValue(textfield.lfValue);
        break;
      case "LF-TOGGLE":
        const toggle = control;
        toggle.setValue(toggle.lfValue ? "on" : "off");
        break;
    }
  }
}
function setGridStatus(status, grid, actionButtons) {
  const { interrupt, resume } = actionButtons;
  switch (status) {
    case ImageEditorStatus.Completed:
      requestAnimationFrame(() => {
        if (interrupt)
          interrupt.lfUiState = "disabled";
        if (resume)
          resume.lfUiState = "disabled";
      });
      grid == null ? void 0 : grid.classList.add(ImageEditorCSS.GridIsInactive);
      break;
    case ImageEditorStatus.Pending:
      requestAnimationFrame(() => {
        if (interrupt)
          interrupt.lfUiState = "danger";
        if (resume)
          resume.lfUiState = "success";
      });
      grid == null ? void 0 : grid.classList.remove(ImageEditorCSS.GridIsInactive);
      break;
  }
}
const updateCb = async (state, addSnapshot = false, force = false) => {
  await refreshValues(state, addSnapshot);
  const { elements, filter } = state;
  const { imageviewer } = elements;
  const { settings } = filter;
  const validValues = isValidObject(settings);
  const isCanvasAction = settings.points || settings.b64_canvas;
  const isStroke = !filter || filter.hasCanvasAction;
  if (validValues && isStroke) {
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
  const shouldUpdate = !!(validValues && (!isStroke || isStroke && isCanvasAction));
  const requiresManualApply = !!(filter == null ? void 0 : filter.requiresManualApply);
  if (shouldUpdate && (force || !requiresManualApply)) {
    apiCall$2(state, addSnapshot);
  }
};
const STATE$h = /* @__PURE__ */ new WeakMap();
const IMAGE_EDITOR_INSTANCES = /* @__PURE__ */ new Set();
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
        const { actionButtons, grid, imageviewer } = STATE$h.get(wrapper).elements;
        const callback = (_2, u2) => {
          var _a;
          const parsedValue = u2.parsedJson;
          const isPending = ((_a = getStatusColumn(parsedValue)) == null ? void 0 : _a.title) === ImageEditorStatus.Pending;
          if (isPending) {
            setGridStatus(ImageEditorStatus.Pending, grid, actionButtons);
          }
          imageviewer.lfDataset = parsedValue || {};
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
    const refresh = async (directory) => {
      getLfManager().getApiRoutes().image.get(directory).then((r2) => {
        if (r2.status === "success") {
          if ((r2 == null ? void 0 : r2.data) && Object.entries(r2.data).length > 0) {
            imageviewer.lfDataset = r2.data;
          } else {
            getLfManager().log("Images not found.", { r: r2 }, LogSeverity.Info);
          }
        }
      });
    };
    settings.classList.add(ImageEditorCSS.Settings);
    settings.slot = "settings";
    imageviewer.classList.add(ImageEditorCSS.Widget);
    imageviewer.lfLoadCallback = async (_2, value) => await refresh(value);
    imageviewer.lfValue = TREE_DATA;
    imageviewer.addEventListener(LfEventName.LfImageviewer, (e2) => EV_HANDLERS$a.imageviewer(STATE$h.get(wrapper), e2));
    imageviewer.appendChild(settings);
    const actionButtons = {};
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
    const state = {
      elements: { actionButtons, controls: {}, grid, imageviewer, settings },
      filter: null,
      filterType: null,
      lastBrushSettings: JSON.parse(JSON.stringify(SETTINGS.brush.settings)),
      node,
      update: {
        preview: () => updateCb(STATE$h.get(wrapper)),
        snapshot: () => updateCb(STATE$h.get(wrapper), true)
      },
      wrapper
    };
    STATE$h.set(wrapper, state);
    IMAGE_EDITOR_INSTANCES.add(state);
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
          } catch (error) {
            logger("LF interrupt hook failed while applying image editor cleanup.", { error }, LogSeverity.Warning);
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
    } catch (error) {
      logger("Failed to patch api.interrupt; proceeding without LF interrupt hook", { error }, LogSeverity.Warning);
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
      } catch (error) {
        logger("LF refresh hook failed before calling original function", { error }, LogSeverity.Warning);
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
    } catch (error) {
      logger("Failed to patch refreshComboInNodes; proceeding without LF refresh hook", { error }, LogSeverity.Warning);
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
function deriveInnerColor(base) {
  const hex = base.trim();
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
          } catch (error) {
            (_b3 = (_a3 = getLfManager()) == null ? void 0 : _a3.log) == null ? void 0 : _b3.call(_a3, "[LFReroute] onConnectionsChange error", { error }, LogSeverity.Warning);
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
        const base = this.title || "";
        const slotName = ((_b2 = (_a2 = this.outputs) == null ? void 0 : _a2[0]) == null ? void 0 : _b2.name) || "";
        const longest = base.length > slotName.length ? base : slotName;
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
        } catch (err2) {
          (_d = (_c = getLfManager()) == null ? void 0 : _c.log) == null ? void 0 : _d.call(_c, "[LFReroute] onDrawForeground error", { err: err2 }, LogSeverity.Info);
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
        const link = appInstance2.graph.links[linkId];
        if (!link)
          break;
        const origin = appInstance2.graph.getNodeById(link.origin_id);
        if (!origin)
          break;
        if (isLabeled(origin)) {
          if (origin === this) {
            (_c = upstream.disconnectInput) == null ? void 0 : _c.call(upstream, link.target_slot);
            break;
          }
          upstream = origin;
          continue;
        }
        inputType = ((_e = (_d = origin.outputs) == null ? void 0 : _d[link.origin_slot]) == null ? void 0 : _e.type) || null;
        originNode = origin;
        break;
      }
      let downstreamType = null;
      const firstLinks = ((_g = (_f = this.outputs) == null ? void 0 : _f[0]) == null ? void 0 : _g.links) || [];
      for (const l2 of firstLinks) {
        const link = appInstance2.graph.links[l2];
        if (!link) {
          continue;
        }
        const target = appInstance2.graph.getNodeById(link.target_id);
        if (!target || isLabeled(target)) {
          continue;
        }
        downstreamType = ((_i = (_h = target.inputs) == null ? void 0 : _h[link.target_slot]) == null ? void 0 : _i.type) || null;
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
                const link = appInstance2.graph.links[linkId];
                if (link)
                  return link.origin_slot ?? 0;
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
            const link = appInstance2.graph.links[l2];
            if (link) {
              link.color = color;
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
        } catch (err2) {
          (_c = (_b2 = getLfManager()) == null ? void 0 : _b2.log) == null ? void 0 : _c.call(_b2, "[LFReroute] onAfterGraphConfigured", { err: err2 }, LogSeverity.Warning);
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
      const lfManager2 = getLfManager();
      if (!(extension == null ? void 0 : extension.name)) {
        (_a = lfManager2 == null ? void 0 : lfManager2.log) == null ? void 0 : _a.call(lfManager2, `Attempted to add virtual node with invalid name`, { extension }, LogSeverity.Warning);
        return;
      }
      if (__classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").has(extension.name)) {
        (_b = lfManager2 == null ? void 0 : lfManager2.log) == null ? void 0 : _b.call(lfManager2, `Duplicate virtual node ignored: '${extension.name}'`, {}, LogSeverity.Warning);
        return;
      }
      __classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").set(extension.name, { extension, registered: false });
    };
    this.addMany = (extensions) => {
      extensions.forEach((e2) => this.add(e2));
    };
    this.list = () => Array.from(__classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").values());
    this.registerAll = () => {
      const lfManager2 = getLfManager();
      __classPrivateFieldGet$3(this, _LFNodes_REGISTRY, "f").forEach((entry, key) => {
        var _a, _b;
        if (entry.registered) {
          return;
        }
        try {
          COMFY_API.register(entry.extension);
          entry.registered = true;
          (_a = lfManager2 == null ? void 0 : lfManager2.log) == null ? void 0 : _a.call(lfManager2, `Registered virtual node '${key}'`, {}, LogSeverity.Success);
        } catch (error) {
          entry.error = error;
          (_b = lfManager2 == null ? void 0 : lfManager2.log) == null ? void 0 : _b.call(lfManager2, `Failed to register virtual node '${key}'`, { error }, LogSeverity.Error);
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
          const lfManager2 = getLfManager();
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
                  lfManager2.log("Invoking upload callback.", { base64String }, LogSeverity.Info);
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
        const lfManager2 = getLfManager();
        ogEv.preventDefault();
        ogEv.stopPropagation();
        const tip = lfManager2.getManagers().tooltip;
        const cb = async (b64image) => {
          var _a2, _b2, _c, _d;
          const node2 = (_b2 = (_a2 = comp.lfDataset) == null ? void 0 : _a2.nodes) == null ? void 0 : _b2[0];
          if (node2) {
            const code = (_c = node2 == null ? void 0 : node2.cells) == null ? void 0 : _c.lfCode;
            if (code) {
              try {
                const path = JSON.parse(JSON.stringify(code.value)).path;
                lfManager2.log(`Updating cover for model with path: ${path}`, { b64image }, LogSeverity.Info);
                getApiRoutes().metadata.updateCover(path, b64image);
                const image = (_d = node2 == null ? void 0 : node2.cells) == null ? void 0 : _d.lfImage;
                if (image) {
                  image.value = `data:image/png;charset=utf-8;base64,${b64image}`;
                  comp.refresh();
                  tip.destroy();
                }
              } catch (error) {
                lfManager2.log("Failed to fetch the model's path from .info file", { b64image }, LogSeverity.Error);
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
      const code = (_c = (_b = (_a = dataset == null ? void 0 : dataset.nodes) == null ? void 0 : _a[0]) == null ? void 0 : _b.cells) == null ? void 0 : _c.lfCode;
      const civitaiDataset = prepareValidDataset(r2, code);
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
            } catch (error) {
              getLfManager().log("Error when setting lfData prop on card!", { error }, LogSeverity.Error);
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
const prepareValidDataset = (r2, code) => {
  var _a, _b, _c, _d, _e;
  const dataset = {
    nodes: [
      {
        cells: { lfCode: code ?? null, lfImage: null, text1: null, text2: null, text3: null },
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
        const { code } = STATE$b.get(wrapper);
        switch (code.lfLanguage) {
          case "json":
            return code.lfValue || "{}";
          default:
            return code.lfValue || "";
        }
      },
      setValue(value) {
        const { code } = STATE$b.get(wrapper);
        const callback = (v2, u2) => {
          switch (code.lfLanguage) {
            case "json":
              code.lfValue = u2.unescapedStr || "{}";
              break;
            default:
              code.lfValue = typeof v2 === "string" ? v2 : "";
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
    const code = document.createElement(TagName.LfCode);
    content.classList.add(CodeCSS.Content);
    code.classList.add(CodeCSS.Widget);
    switch (node.comfyClass) {
      case NodeName.displayJson:
      case NodeName.displayPrimitiveAsJson:
      case NodeName.shuffleJsonKeys:
      case NodeName.sortJsonKeys:
      case NodeName.stringToJson:
        code.lfLanguage = "json";
        code.lfValue = "{}";
        break;
      default:
        code.lfLanguage = "markdown";
        code.lfValue = "";
        break;
    }
    content.appendChild(code);
    wrapper.appendChild(content);
    const options = codeFactory.options(wrapper);
    STATE$b.set(wrapper, { code, node, wrapper });
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
  ControlPanelIcons2["GitHub"] = "brand-github";
  ControlPanelIcons2["Metadata"] = "info-hexagon";
  ControlPanelIcons2["Theme"] = "color-swatch";
})(ControlPanelIcons || (ControlPanelIcons = {}));
var ControlPanelIds;
(function(ControlPanelIds2) {
  ControlPanelIds2["Analytics"] = "analytics";
  ControlPanelIds2["Backup"] = "backup";
  ControlPanelIds2["Debug"] = "debug";
  ControlPanelIds2["GitHub"] = "github";
  ControlPanelIds2["Metadata"] = "metadata";
  ControlPanelIds2["Theme"] = "theme";
})(ControlPanelIds || (ControlPanelIds = {}));
var ControlPanelLabels;
(function(ControlPanelLabels2) {
  ControlPanelLabels2["AutoBackup"] = "Automatic Backup";
  ControlPanelLabels2["Backup"] = "Backup now";
  ControlPanelLabels2["ClearLogs"] = "Clear logs";
  ControlPanelLabels2["Debug"] = "Debug";
  ControlPanelLabels2["DeleteUsage"] = "Delete usage analytics info";
  ControlPanelLabels2["DeleteMetadata"] = "Delete models info";
  ControlPanelLabels2["Done"] = "Done!";
  ControlPanelLabels2["OpenIssue"] = "Open an issue";
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
  customization: () => {
    return {
      margin: "0"
    };
  },
  debugGrid: () => {
    return {
      display: "grid",
      gridTemplateRows: "repeat(5, max-content) 1fr",
      height: "100%",
      margin: "0"
    };
  },
  debugLogs: () => {
    return {
      display: "grid",
      gridGap: "0.75em",
      gridTemplateRows: "320px 480px"
    };
  },
  logsArea: () => {
    return {
      backgroundColor: "rgba(var(--lf-color-on-bg), 0.075)",
      borderRadius: "0.5em",
      display: "block",
      height: "100%",
      marginBottom: "1em",
      overflow: "auto"
    };
  },
  separator: () => {
    return {
      border: "1px solid rgb(var(--lf-color-border))",
      display: "block",
      margin: "0.75em auto 1.25em",
      opacity: "0.25",
      width: "50%"
    };
  }
};
const SECTIONS = {
  //#region Analytics
  [ControlPanelIds.Analytics]: () => {
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
  },
  //#endregion
  //#region Backup
  [ControlPanelIds.Backup]: () => {
    const { theme } = getLfManager().getManagers().lfFramework;
    const { "--lf-icon-download": downloadIcon } = theme.get.current().variables;
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
            {
              id: ControlPanelSection.Content,
              tagName: "br",
              value: ""
            },
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
          value: "Backup files",
          children: [
            {
              id: ControlPanelSection.Content,
              value: "This button will create a manual backup of the content in <path/to/your/comfyui/user/LF_Nodes>"
            },
            {
              id: ControlPanelSection.Content,
              value: "Be sure to include as much information as you can, without sufficient data it's difficult to troubleshoot problems."
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
  },
  //#endregion
  //#region Debug
  [ControlPanelIds.Debug]: (logsData) => {
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
            {
              id: ControlPanelSection.Content,
              tagName: "br",
              value: ""
            },
            {
              id: ControlPanelSection.Content,
              value: "In the browser console there should be more informations."
            },
            {
              id: ControlPanelSection.Content,
              tagName: "br",
              value: ""
            },
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
              cells: {
                lfCard: {
                  lfDataset: {
                    nodes: [
                      {
                        cells: {
                          lfCode: { shape: "code", value: "" },
                          lfButton: {
                            shape: "button",
                            value: ""
                          },
                          lfButton_2: {
                            shape: "button",
                            value: ""
                          },
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
              },
              id: "content-wrapper"
            }
          ]
        }
      ]
    };
  },
  //#endregion
  //#region GitHub
  [ControlPanelIds.GitHub]: () => {
    var _a, _b;
    const lfManager2 = getLfManager();
    const releaseData = lfManager2.getLatestRelease();
    const { theme } = lfManager2.getManagers().lfFramework;
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
                marginBottom: "1em"
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
                {
                  id: ControlPanelSection.Content,
                  tagName: "br",
                  value: ""
                },
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
  },
  //#endregion
  //#region Metadata
  [ControlPanelIds.Metadata]: () => {
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
            {
              id: ControlPanelSection.Content,
              value: "By pressing this button it's possible to delete every .info file created by fetching the metadata."
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
  },
  //#endregion
  //#region Theme
  [ControlPanelIds.Theme]: () => {
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
  }
  //#endregion
};
const INTRO_SECTION = ControlPanelIds.GitHub;
let TIMEOUT;
const EV_HANDLERS$6 = {
  //#region Article handler
  article: (e2) => {
    const { eventType, originalEvent } = e2.detail;
    switch (eventType) {
      case "lf-event":
        handleLfEvent(originalEvent);
        break;
    }
  },
  //#endregion
  //#region Button handler
  button: (e2) => {
    const { comp, eventType, originalEvent } = e2.detail;
    const element = comp.rootElement;
    const createSpinner = () => {
      const spinner = document.createElement("lf-spinner");
      spinner.lfActive = true;
      spinner.lfDimensions = "0.6em";
      spinner.lfLayout = 2;
      spinner.slot = "spinner";
      return spinner;
    };
    const invokeAPI = (promise, label) => {
      const onResponse2 = () => {
        comp.lfIcon = "check";
        comp.lfLabel = ControlPanelLabels.Done;
        comp.lfShowSpinner = false;
        comp.lfUiState = "disabled";
      };
      const restore = (label2) => {
        comp.lfLabel = label2;
        comp.lfIcon = "delete";
        comp.lfUiState = "primary";
        TIMEOUT = null;
      };
      requestAnimationFrame(() => comp.lfShowSpinner = true);
      promise.then(() => {
        requestAnimationFrame(onResponse2);
        if (TIMEOUT) {
          clearTimeout(TIMEOUT);
        }
        TIMEOUT = setTimeout(() => requestAnimationFrame(() => restore(label)), 1e3);
      });
    };
    switch (eventType) {
      case "click":
        switch (comp.lfLabel) {
          case ControlPanelLabels.Backup:
            invokeAPI(getApiRoutes().backup.new("manual"), ControlPanelLabels.Backup);
            break;
          case ControlPanelLabels.ClearLogs:
            const { article, dataset } = getLfManager().getDebugDataset();
            if ((dataset == null ? void 0 : dataset.length) > 0) {
              dataset.splice(0, dataset.length);
              article.refresh();
            }
            break;
          case ControlPanelLabels.DeleteMetadata:
            invokeAPI(getApiRoutes().metadata.clear(), ControlPanelLabels.DeleteMetadata);
            break;
          case ControlPanelLabels.DeleteUsage:
            invokeAPI(getApiRoutes().analytics.clear("usage"), ControlPanelLabels.DeleteUsage);
            break;
          case ControlPanelLabels.OpenIssue:
            window.open("https://github.com/lucafoscili/comfyui-lf/issues/new", "_blank");
            break;
          case ControlPanelLabels.Theme:
            getLfManager().getManagers().lfFramework.theme.randomize();
            break;
        }
        break;
      case "lf-event":
        const ogEv = originalEvent;
        EV_HANDLERS$6.list(ogEv);
        break;
      case "ready":
        switch (comp.lfLabel) {
          case ControlPanelLabels.Backup:
            element.appendChild(createSpinner());
            break;
          case ControlPanelLabels.DeleteMetadata:
          case ControlPanelLabels.DeleteUsage:
            element.classList.add("lf-danger");
            element.appendChild(createSpinner());
            break;
        }
    }
  },
  //#endregion
  //#region List handler
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
  //#endregion
  //#region Toggle handler
  toggle: (e2) => {
    const { comp, eventType, value } = e2.detail;
    const element = comp.rootElement;
    switch (eventType) {
      case "change":
        getLfManager().toggleDebug(value === "on" ? true : false);
        break;
      case "ready":
        element.title = "Activate verbose console logging";
    }
  }
  //#endregion
};
const createContent = () => {
  const grid = document.createElement(TagName.Div);
  const accordion = document.createElement(TagName.LfAccordion);
  const nodes = [];
  accordion.lfDataset = { nodes };
  for (const id in SECTIONS) {
    if (id !== INTRO_SECTION && Object.prototype.hasOwnProperty.call(SECTIONS, id)) {
      const section = SECTIONS[id];
      let article;
      let node;
      switch (id) {
        case ControlPanelIds.Debug:
          const logsData = [];
          node = section(logsData);
          article = prepArticle(id, node);
          getLfManager().setDebugDataset(article, logsData);
          break;
        default:
          node = section(void 0);
          article = prepArticle(id, node);
          break;
      }
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
  const intro = prepArticle(INTRO_SECTION, SECTIONS[INTRO_SECTION]());
  grid.classList.add(ControlPanelCSS.Grid);
  grid.appendChild(intro);
  grid.appendChild(accordion);
  return grid;
};
const prepArticle = (key, node) => {
  const article = document.createElement(TagName.LfArticle);
  article.lfDataset = { nodes: [{ children: [node], id: ControlPanelSection.Root }] };
  article.slot = key;
  article.addEventListener(LfEventName.LfArticle, EV_HANDLERS$6.article);
  return article;
};
const handleLfEvent = (e2) => {
  const { comp } = e2.detail;
  if (isButton(comp)) {
    const ogEv = e2;
    EV_HANDLERS$6.button(ogEv);
  }
  if (isToggle(comp)) {
    const ogEv = e2;
    EV_HANDLERS$6.toggle(ogEv);
  }
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
          debug: getLfManager().isDebug() || false,
          themes: getLfManager().getManagers().lfFramework.theme.get.current().name || ""
        };
      },
      setValue(value) {
        const callback = (_2, u2) => {
          const { backup, debug, themes } = u2.parsedJson;
          if (backup === true || backup === false) {
            getLfManager().toggleBackup(backup);
          }
          if (debug === true || debug === false) {
            getLfManager().toggleDebug(debug);
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
        const { list } = STATE$7.get(wrapper);
        return (list == null ? void 0 : list.lfDataset) || {};
      },
      setValue(value) {
        const { list } = STATE$7.get(wrapper);
        const callback = (_2, u2) => {
          list.lfDataset = u2.parsedJson || {};
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
    const list = document.createElement(TagName.LfList);
    list.classList.add(HistoryCSS.Widget);
    list.lfEmpty = "History is empty!";
    list.lfEnableDeletions = true;
    switch (node.comfyClass) {
      case NodeName.loadFileOnce:
        break;
      default:
        list.lfSelectable = true;
        break;
    }
    list.addEventListener(LfEventName.LfList, (e2) => EV_HANDLERS$5.list(STATE$7.get(wrapper), e2));
    content.classList.add(HistoryCSS.Content);
    content.appendChild(list);
    wrapper.appendChild(content);
    const options = historyFactory.options(wrapper);
    STATE$7.set(wrapper, { list, node, wrapper });
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
          const { columns, dataset, index, name, view } = u2.parsedJson;
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
    const { eventType, config } = e2.detail;
    switch (eventType) {
      case "save":
        if (config && typeof config === "object") {
          state.config = config;
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
        const { config, elements } = STATE$5.get(wrapper);
        const { messenger } = elements;
        return {
          dataset: messenger.lfDataset || {},
          config
        };
      },
      setValue(value) {
        const state = STATE$5.get(wrapper);
        const { elements } = state;
        const { messenger, placeholder } = elements;
        const callback = (_2, u2) => {
          const { config, dataset } = u2.parsedJson;
          messenger.lfDataset = dataset;
          if (isValidObject(config)) {
            messenger.lfValue = config;
            state.config = config;
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
        } catch (error) {
          getLfManager().log("Error parsing JSON", { error }, LogSeverity.Warning);
          textarea.classList.add(TextareaCSS.WidgetError);
          textarea.title = error;
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
        } catch (error) {
          return error;
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
          } catch (error) {
            alert(`Upload failed: ${error}`);
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
      const lfManager2 = getLfManager();
      const payload = event.detail;
      const id = resolveNodeId(payload);
      if (!id) {
        lfManager2.log(`Event '${name}' missing node identifier; present keys: ${Object.keys(payload).join(", ")}`, { payload, name }, LogSeverity.Warning);
        return;
      }
      const node = lfManager2.getApiRoutes().comfy.getNodeById(id);
      if (node) {
        lfManager2.log(`${node.comfyClass} (#${node.id}): event '${name}' fired`, { payload, node }, LogSeverity.Info);
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
                    lfManager2.log(`Initiating JSON data fetch for editing breakpoint from path: ${value}`, { widget, value });
                    getApiRoutes().json.get(value).then((r2) => {
                      if (r2.status === LogSeverity.Success) {
                        lfManager2.log("JSON data fetched successfully for image editing breakpoint.", { data: r2.data }, LogSeverity.Success);
                        widget.options.setValue(JSON.stringify(r2.data));
                      } else {
                        lfManager2.log(`Failed to fetch JSON data: ${r2.message}`, { response: r2 }, LogSeverity.Error);
                      }
                    }).catch((error) => {
                      lfManager2.log(`Error during JSON fetch for editing breakpoint: ${error.toString()}`, { error }, LogSeverity.Error);
                    });
                  } else {
                    lfManager2.log(`Image editor widget handling failed: missing 'widget' or 'value' in payload.`, { widget, payload }, LogSeverity.Warning);
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
        lfManager2.getApiRoutes().comfy.redraw();
      } else {
        lfManager2.log(`Event '${name}' was fired but its related node (#${id}) wasn't found in the graph! Skipping handling the event.`, { payload, name }, LogSeverity.Warning);
      }
    };
    _LFWidgets_notifications.set(this, {
      decorate: (payload) => {
        const { action, image, message, silent, tag, title } = payload;
        const icon = action === "focus tab" ? "photo-search" : action === "interrupt" ? "x" : action === "interrupt and queue" ? "refresh" : action === "queue prompt" ? "stack-push" : "";
        const options = {
          body: message,
          icon: icon ? window.location.href + `extensions/lf-nodes/assets/svg/${icon}.svg` : void 0,
          requireInteraction: action === "none" ? false : true,
          silent,
          tag
        };
        if ("image" in Notification.prototype && image) {
          options.image = image;
        }
        if (Notification.permission === "granted") {
          const notification = new Notification(title, options);
          notification.addEventListener("click", () => {
            const lfManager2 = getLfManager();
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
                lfManager2.log("New prompt queued from notification after interrupting.", {}, LogSeverity.Success);
                break;
              case "queue prompt":
                routes.queuePrompt();
                lfManager2.log("New prompt queued from notification.", {}, LogSeverity.Success);
                break;
            }
          });
        }
      },
      show: (payload) => {
        const lfManager2 = getLfManager();
        if (Notification.permission !== "granted") {
          Notification.requestPermission().then((permission) => {
            if (permission === "granted") {
              __classPrivateFieldGet$1(this, _LFWidgets_notifications, "f").decorate(payload);
            } else {
              lfManager2.log("Notification permission denied.", {}, LogSeverity.Warning);
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
var _LFManager_APIS, _LFManager_AUTOMATIC_BACKUP, _LFManager_CACHED_DATASETS, _LFManager_DEBUG, _LFManager_DEBUG_ARTICLE, _LFManager_DEBUG_DATASET, _LFManager_INITIALIZED, _LFManager_LATEST_RELEASE, _LFManager_MANAGERS;
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
      metadata: METADATA_API
    });
    _LFManager_AUTOMATIC_BACKUP.set(this, true);
    _LFManager_CACHED_DATASETS.set(this, {
      usage: null
    });
    _LFManager_DEBUG.set(this, false);
    _LFManager_DEBUG_ARTICLE.set(this, void 0);
    _LFManager_DEBUG_DATASET.set(this, void 0);
    _LFManager_INITIALIZED.set(this, false);
    _LFManager_LATEST_RELEASE.set(this, void 0);
    _LFManager_MANAGERS.set(this, {});
    const assetsUrl = window.location.href + "extensions/lf-nodes/assets";
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework = getLfFramework();
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework.assets.set(assetsUrl);
    __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework.theme.set("dark");
    this.log("LfFramework ready!", { lfFramework: __classPrivateFieldGet(this, _LFManager_MANAGERS, "f").lfFramework }, LogSeverity.Success);
    const link = document.createElement("link");
    link.dataset.filename = "_index";
    link.rel = "stylesheet";
    link.type = "text/css";
    link.href = `extensions/lf-nodes/css/_index.css`;
    document.head.appendChild(link);
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
  setDebugDataset(article, dataset) {
    __classPrivateFieldSet(this, _LFManager_DEBUG_ARTICLE, article, "f");
    __classPrivateFieldSet(this, _LFManager_DEBUG_DATASET, dataset, "f");
  }
  toggleBackup(value) {
    if (value === false || value === true) {
      __classPrivateFieldSet(this, _LFManager_AUTOMATIC_BACKUP, value, "f");
    } else {
      __classPrivateFieldSet(this, _LFManager_AUTOMATIC_BACKUP, !__classPrivateFieldGet(this, _LFManager_AUTOMATIC_BACKUP, "f"), "f");
    }
    this.log(`Automatic backup active: '${__classPrivateFieldGet(this, _LFManager_DEBUG, "f")}'`, { value }, LogSeverity.Warning);
    return __classPrivateFieldGet(this, _LFManager_DEBUG, "f");
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
_LFManager_APIS = /* @__PURE__ */ new WeakMap(), _LFManager_AUTOMATIC_BACKUP = /* @__PURE__ */ new WeakMap(), _LFManager_CACHED_DATASETS = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG_ARTICLE = /* @__PURE__ */ new WeakMap(), _LFManager_DEBUG_DATASET = /* @__PURE__ */ new WeakMap(), _LFManager_INITIALIZED = /* @__PURE__ */ new WeakMap(), _LFManager_LATEST_RELEASE = /* @__PURE__ */ new WeakMap(), _LFManager_MANAGERS = /* @__PURE__ */ new WeakMap();
var LFFreeFlags;
(function(LFFreeFlags2) {
  LFFreeFlags2["PatchedFree"] = "_lf_patched_freeMemory";
  LFFreeFlags2["OriginalFreeRef"] = "_lf_original_freeMemory";
  LFFreeFlags2["PatchedFetch"] = "_lf_patched_fetchApi_free";
  LFFreeFlags2["InBeforeFree"] = "_lf_in_beforeFree";
})(LFFreeFlags || (LFFreeFlags = {}));
var LFRefreshFlags;
(function(LFRefreshFlags2) {
  LFRefreshFlags2["PatchedRefresh"] = "_lf_patched_refreshComboInNodes";
  LFRefreshFlags2["OriginalRefreshRef"] = "_lf_original_refreshComboInNodes";
  LFRefreshFlags2["InBeforeRefresh"] = "_lf_in_beforeRefreshComboInNodes";
})(LFRefreshFlags || (LFRefreshFlags = {}));
var LFInterruptFlags;
(function(LFInterruptFlags2) {
  LFInterruptFlags2["PatchedInterrupt"] = "_lf_patched_interrupt";
  LFInterruptFlags2["OriginalInterruptRef"] = "_lf_original_interrupt";
  LFInterruptFlags2["InBeforeInterrupt"] = "_lf_in_beforeInterrupt";
})(LFInterruptFlags || (LFInterruptFlags = {}));
const LF_MANAGER_SYMBOL_ID = "__LfManager__";
const LF_MANAGER_SYMBOL = Symbol.for(LF_MANAGER_SYMBOL_ID);
const DEFAULT_WIDGET_NAME = "ui_widget";
let timer;
const isButton = (comp) => {
  return comp.rootElement.tagName.toLowerCase() === "lf-button";
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
const isValidJSON = (value) => {
  try {
    JSON.stringify(value);
    return true;
  } catch (error) {
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
    if (typeof data === "string") {
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
    parsedJson = JSON.parse(input);
    validJson = true;
    parsedJson = deepParse(parsedJson);
    unescapedStr = JSON.stringify(parsedJson, null, 2);
  } catch (error) {
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
const isValidNumber = (n2) => {
  return !isNaN(n2) && typeof n2 === "number";
};
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
  } catch (error) {
    getLfManager().log(`Couldn't find a widget of type ${type}`, { error, node }, LogSeverity.Warning);
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
  } catch (error) {
    if (onException) {
      onException();
    }
    getLfManager().log(`Normalization error!`, { error, widget }, LogSeverity.Error);
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
  } catch (error) {
    getLfManager().log("Whoops! It seems there is no chart. :V", { error }, LogSeverity.Error);
  }
};
{
  console.log("LF modules loaded!");
}
getLfFramework();
{
  console.log("LF Framework initialized!");
}
initLfManager();
const lfManager = getLfManager();
lfManager.initialize();
{
  console.log("LF Manager initialized!", lfManager);
}
export {
  LF_PLACEHOLDER_PARTS as $,
  LF_MASONRY_PROPS as A,
  LF_MASONRY_IDS as B,
  CY_ATTRIBUTES as C,
  LF_DRAWER_BLOCKS as D,
  LF_DRAWER_PARTS as E,
  LF_DRAWER_PROPS as F,
  G,
  LF_DRAWER_SLOT as H,
  I,
  LF_EFFECTS_FOCUSABLES as J,
  LF_CAROUSEL_BLOCKS as K,
  LF_ACCORDION_BLOCKS as L,
  LF_CAROUSEL_PARTS as M,
  LF_CAROUSEL_PROPS as N,
  LF_CAROUSEL_IDS as O,
  LF_TABBAR_BLOCKS as P,
  LF_TABBAR_PARTS as Q,
  LF_TABBAR_PROPS as R,
  LF_SPLASH_BLOCKS as S,
  LF_SPLASH_PARTS as T,
  LF_SPLASH_PROPS as U,
  LF_TREE_BLOCKS as V,
  W$1 as W,
  LF_TREE_PARTS as X,
  LF_TREE_PROPS as Y,
  LF_TREE_CSS_VARIABLES as Z,
  LF_PLACEHOLDER_BLOCKS as _,
  LF_ATTRIBUTES as a,
  LF_PHOTOFRAME_PROPS as a$,
  LF_PLACEHOLDER_PROPS as a0,
  IMAGE_TYPE_IDS as a1,
  LF_MESSENGER_CLEAN_UI as a2,
  LF_MESSENGER_BLOCKS as a3,
  LF_MESSENGER_PARTS as a4,
  OPTION_TYPE_IDS as a5,
  LF_MESSENGER_PROPS as a6,
  LF_MESSENGER_IDS as a7,
  LF_MESSENGER_FILTER as a8,
  LF_MESSENGER_NAV as a9,
  LF_CARD_CSS_VARS as aA,
  LF_CARD_DEFAULTS as aB,
  LF_CARD_PROPS as aC,
  LF_CHART_BLOCKS as aD,
  LF_CHART_PARTS as aE,
  LF_CHART_CSS_VARS as aF,
  LF_THEME_COLORS_DATA_PREFIX as aG,
  LF_CHART_PROPS as aH,
  LF_CHAT_BLOCKS as aI,
  LF_CHAT_PARTS as aJ,
  LF_CHAT_PROPS as aK,
  LF_CHIP_BLOCKS as aL,
  LF_CHIP_PARTS as aM,
  LF_CHIP_PROPS as aN,
  LF_CODE_BLOCKS as aO,
  LF_CODE_PARTS as aP,
  LF_CODE_PROPS as aQ,
  LF_IMAGE_BLOCKS as aR,
  LF_IMAGE_PARTS as aS,
  LF_IMAGE_CSS_VARS as aT,
  LF_IMAGE_PROPS as aU,
  CSS_VAR_PREFIX as aV,
  LF_LIST_BLOCKS as aW,
  LF_LIST_PARTS as aX,
  LF_LIST_PROPS as aY,
  LF_PHOTOFRAME_BLOCKS as aZ,
  LF_PHOTOFRAME_PARTS as a_,
  LF_MESSENGER_MENU as aa,
  TIMEFRAME_COVER as ab,
  STYLE_COVER as ac,
  OUTFIT_COVER as ad,
  LOCATION_COVER as ae,
  AVATAR_COVER as af,
  CHILD_ROOT_MAP as ag,
  LF_SLIDER_BLOCKS as ah,
  LF_SLIDER_PARTS as ai,
  LF_SLIDER_CSS_VARIABLES as aj,
  LF_SLIDER_PROPS as ak,
  LF_TOAST_BLOCKS as al,
  LF_TOAST_PARTS as am,
  LF_TOAST_CSS_VARIABLES as an,
  LF_TOAST_PROPS as ao,
  LF_BADGE_BLOCKS as ap,
  LF_BADGE_PARTS as aq,
  LF_BADGE_PROPS as ar,
  LF_BUTTON_BLOCKS as as,
  LF_BUTTON_PARTS as at,
  LF_BUTTON_PROPS as au,
  LF_CANVAS_BLOCKS as av,
  LF_CANVAS_PARTS as aw,
  LF_CANVAS_PROPS as ax,
  LF_CARD_BLOCKS as ay,
  LF_CARD_PARTS as az,
  LF_ACCORDION_PARTS as b,
  LF_PROGRESSBAR_BLOCKS as b0,
  LF_PROGRESSBAR_PARTS as b1,
  LF_PROGRESSBAR_CSS_VARIABLES as b2,
  LF_PROGRESSBAR_PROPS as b3,
  LF_SPINNER_PROPS as b4,
  LF_TEXTFIELD_BLOCKS as b5,
  LF_TEXTFIELD_PARTS as b6,
  LF_TEXTFIELD_PROPS as b7,
  LF_TOGGLE_BLOCKS as b8,
  LF_TOGGLE_PARTS as b9,
  LF_TOGGLE_PROPS as ba,
  LF_TYPEWRITER_BLOCKS as bb,
  LF_TYPEWRITER_PARTS as bc,
  LF_TYPEWRITER_PROPS as bd,
  LF_UPLOAD_BLOCKS as be,
  LF_UPLOAD_PARTS as bf,
  LF_UPLOAD_PROPS as bg,
  LF_BADGE_CSS_VARS as bh,
  LF_CHIP_CSS_VARS as bi,
  LF_CARD_IDS as bj,
  LF_CHAT_IDS as bk,
  LF_THEME_ICONS as bl,
  LF_HEADER_BLOCKS as bm,
  LF_HEADER_PARTS as bn,
  LF_HEADER_PROPS as bo,
  LF_HEADER_SLOT as bp,
  onFrameworkReady as bq,
  j as br,
  S as bs,
  LF_STYLE_ID as c,
  LF_WRAPPER_ID as d,
  LF_ACCORDION_PROPS as e,
  L as f,
  LF_ARTICLE_BLOCKS as g,
  LF_ARTICLE_PARTS as h,
  LF_ARTICLE_PROPS as i,
  LF_IMAGEVIEWER_BLOCKS as j,
  kt as k,
  LF_IMAGEVIEWER_PARTS as l,
  mt as m,
  n,
  LF_IMAGEVIEWER_PROPS as o,
  IDS as p,
  LF_COMPARE_BLOCKS as q,
  LF_COMPARE_PARTS as r,
  LF_COMPARE_CSS_VARS as s,
  LF_COMPARE_DEFAULTS as t,
  LF_COMPARE_PROPS as u,
  LF_COMPARE_IDS as v,
  LF_MASONRY_DEFAULT_COLUMNS as w,
  LF_MASONRY_BLOCKS as x,
  LF_MASONRY_PARTS as y,
  LF_MASONRY_CSS_VARS as z
};
