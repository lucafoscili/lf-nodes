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
const LF_AUTOCOMPLETE_BLOCKS = {
  autocomplete: {
    _: "autocomplete",
    textfield: "textfield"
  },
  dropdown: {
    _: "dropdown",
    list: "list",
    spinner: "spinner"
  }
};
const LF_AUTOCOMPLETE_PARTS = {
  autocomplete: "autocomplete",
  dropdown: "dropdown",
  list: "list",
  spinner: "spinner",
  textfield: "textfield"
};
const LF_AUTOCOMPLETE_PROPS = [
  "lfAllowFreeInput",
  "lfCache",
  "lfCacheTTL",
  "lfDataset",
  "lfDebounceMs",
  "lfListProps",
  "lfMaxCacheSize",
  "lfMinChars",
  "lfNavigation",
  "lfSpinnerProps",
  "lfStyle",
  "lfTextfieldProps",
  "lfUiSize",
  "lfUiState",
  "lfValue"
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
    attachImage: "attach-image",
    attachFile: "attach-file",
    attachments: "attachments",
    clear: "clear",
    configuration: "configuration",
    editButtons: "edit-buttons",
    editContainer: "edit-container",
    editTextarea: "edit-textarea",
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
    exportHistory: "export-history",
    header: "header",
    importHistory: "import-history",
    textarea: "textarea",
    textfield: "textfield"
  },
  toolbar: {
    _: "toolbar",
    button: "button",
    buttons: "buttons",
    toolExecution: "tool-execution"
  }
};
const LF_CHAT_IDS = {
  chat: {
    attachFile: "chat-attach-file",
    attachImage: "chat-attach-image",
    attachments: "chat-attachments",
    editCancel: "chat-edit-cancel",
    editConfirm: "chat-edit-confirm",
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
    exportHistory: "option-export-history",
    frequencyPenalty: "option-frequency-penalty",
    importHistory: "option-import-history",
    maxTokens: "option-maxtokens",
    polling: "option-polling",
    presencePenalty: "option-presence-penalty",
    seed: "option-seed",
    system: "option-system",
    temperature: "option-temperature",
    topP: "option-top-p"
  },
  toolbar: {
    copyContent: "toolbar-copy-content",
    deleteMessage: "toolbar-delete-message",
    editMessage: "toolbar-edit-message",
    regenerate: "toolbar-regenerate"
  }
};
const LF_CHAT_PARTS = {
  attachFile: "attach-file",
  attachImage: "attach-image",
  attachments: "attachments",
  back: "back",
  chat: "chat",
  clear: "clear",
  configuration: "configuration",
  contextWindow: "context-window",
  copyContent: "copy-content",
  deleteMessage: "delete-message",
  divider: "divider",
  editButtons: "edit-buttons",
  editCancel: "edit-cancel",
  editConfirm: "edit-confirm",
  editContainer: "edit-container",
  editTextarea: "edit-textarea",
  endpointUrl: "endpoint-url",
  exportHistory: "export-history",
  frequencyPenalty: "frequency-penalty",
  importHistory: "import-history",
  maxTokens: "max-tokens",
  polling: "polling",
  presencePenalty: "presence-penalty",
  prompt: "prompt",
  regenerate: "regenerate",
  seed: "seed",
  send: "send",
  settings: "settings",
  stt: "stt",
  system: "system",
  temperature: "temperature",
  toolbar: "toolbar",
  topP: "top-p"
};
const LF_CHAT_PROPS = [
  "lfAttachmentUploadTimeout",
  "lfContextWindow",
  "lfEmpty",
  "lfEndpointUrl",
  "lfFrequencyPenalty",
  "lfLayout",
  "lfMaxTokens",
  "lfPollingInterval",
  "lfPresencePenalty",
  "lfSeed",
  "lfStyle",
  "lfSystem",
  "lfTemperature",
  "lfTopP",
  "lfUiSize",
  "lfValue",
  "lfUploadCallback"
];
const LF_CHECKBOX_BLOCKS = {
  formField: {
    _: "form-field",
    label: "label"
  },
  checkbox: {
    _: "checkbox",
    label: "label",
    nativeControl: "native-control",
    background: "background",
    checkmark: "checkmark",
    mixedmark: "mixedmark",
    surface: "surface"
  }
};
const LF_CHECKBOX_PARTS = {
  label: "label",
  nativeControl: "native-control",
  checkbox: "checkbox",
  background: "background",
  checkmark: "checkmark",
  mixedmark: "mixedmark"
};
const LF_CHECKBOX_PROPS = [
  "lfAriaLabel",
  "lfLabel",
  "lfLeadingLabel",
  "lfRipple",
  "lfStyle",
  "lfUiSize",
  "lfUiState",
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
    spinner: "spinner",
    spinnerContainer: "spinner-container",
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
  "lfFlat",
  "lfRipple",
  "lfShowSpinner",
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
  deleteIcon: { _: "delete", icon: "icon" },
  emptyData: { _: "empty-data", text: "text" },
  list: { _: "list", filter: "filter", item: "item" },
  node: {
    _: "node",
    icon: "icon",
    subtitle: "subtitle",
    text: "text",
    title: "title"
  }
};
const LF_LIST_PARTS = {
  deleteIcon: "delete-icon",
  emptyData: "empty-data",
  filter: "filter",
  icon: "icon",
  list: "list",
  node: "node",
  subtitle: "subtitle",
  title: "title"
};
const LF_LIST_PROPS = [
  "lfDataset",
  "lfEmpty",
  "lfEnableDeletions",
  "lfFilter",
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
  "lfCollapseColumns",
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
const LF_RADIO_BLOCKS = {
  _: "radio",
  control: {
    _: "control",
    circle: "circle",
    dot: "dot",
    input: "input",
    ripple: "ripple"
  },
  item: {
    _: "item",
    label: "label"
  }
};
const LF_RADIO_PARTS = {
  circle: "circle",
  control: "control",
  dot: "dot",
  input: "input",
  item: "item",
  label: "label",
  radio: "radio",
  ripple: "ripple"
};
const LF_RADIO_PROPS = [
  "lfAriaLabel",
  "lfDataset",
  "lfLeadingLabel",
  "lfOrientation",
  "lfRipple",
  "lfStyle",
  "lfUiSize",
  "lfUiState",
  "lfValue"
];
const LF_SELECT_BLOCKS = {
  select: {
    _: "select",
    list: "list",
    textfield: "textfield"
  }
};
const LF_SELECT_PARTS = {
  list: "list",
  select: "select",
  textfield: "textfield"
};
const LF_SELECT_PROPS = [
  "lfDataset",
  "lfListProps",
  "lfNavigation",
  "lfStyle",
  "lfTextfieldProps",
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
    iconAction: "icon-action",
    input: "input",
    label: "label",
    resizer: "resizer",
    rippleSurface: "ripple-surface"
  }
};
const LF_TEXTFIELD_PARTS = {
  counter: "counter",
  icon: "icon",
  iconAction: "icon-action",
  input: "input",
  label: "label",
  textfield: "textfield"
};
const LF_TEXTFIELD_PROPS = [
  "lfFormatJSON",
  "lfHelper",
  "lfHtmlAttributes",
  "lfIcon",
  "lfLabel",
  "lfStretchY",
  "lfStyle",
  "lfStyling",
  "lfTrailingIcon",
  "lfTrailingIconAction",
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
  "lfHtmlAttributes",
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
  showcaseGridWrapper: "showcase-grid-wrapper",
  spinner: "spinner"
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
    LfAutocomplete: LF_AUTOCOMPLETE_PROPS,
    LfBadge: LF_BADGE_PROPS,
    LfButton: LF_BUTTON_PROPS,
    LfCanvas: LF_CANVAS_PROPS,
    LfCard: LF_CARD_PROPS,
    LfCarousel: LF_CAROUSEL_PROPS,
    LfChart: LF_CHART_PROPS,
    LfChat: LF_CHAT_PROPS,
    LfCheckbox: LF_CHECKBOX_PROPS,
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
    LfRadio: LF_RADIO_PROPS,
    LfSelect: LF_SELECT_PROPS,
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
  },
  weatherLayout: {
    _: "weather-layout",
    header: "header",
    location: "location",
    mainSection: "main-section",
    temperature: "temperature",
    icon: "icon",
    detailsGrid: "details-grid",
    detailItem: "detail-item",
    detailLabel: "detail-label",
    detailValue: "detail-value"
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
    },
    weather: {
      image: () => [
        {
          lfSizeX: "100%",
          lfSizeY: "100%",
          shape: "image",
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
  uploadLayout: "upload-layout",
  weatherLayout: "weather-layout"
};
const LF_CARD_PROPS = [
  "lfDataset",
  "lfLayout",
  "lfSizeX",
  "lfSizeY",
  "lfStyle",
  "lfUiSize",
  "lfUiState"
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
  "accept",
  "accept-charset",
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
const getGlobalScope = () => {
  if (typeof globalThis === "undefined") {
    return void 0;
  }
  return globalThis;
};
const getStencilHelper = (key) => {
  const globalScope = getGlobalScope();
  const candidates = [
    globalScope == null ? void 0 : globalScope.StencilCore,
    globalScope == null ? void 0 : globalScope.app,
    globalScope == null ? void 0 : globalScope.App,
    globalScope == null ? void 0 : globalScope.lfWidgets,
    globalScope
  ];
  for (const candidate of candidates) {
    const helper = candidate == null ? void 0 : candidate[key];
    if (typeof helper === "function") {
      return helper.bind(candidate);
    }
  }
  if (typeof window === "undefined") {
    try {
      const stencil = require("@stencil/core");
      const helper = stencil == null ? void 0 : stencil[key];
      if (typeof helper === "function") {
        return helper;
      }
    } catch {
    }
  }
  return void 0;
};
const getAssetPathProxy = (path) => {
  const helper = getStencilHelper("getAssetPath");
  if (helper) {
    try {
      const result = helper(path);
      if (typeof result === "string" && result.length > 0) {
        return result;
      }
    } catch {
    }
  }
  return path;
};
const setAssetPathProxy = (path) => {
  const helper = getStencilHelper("setAssetPath");
  if (helper) {
    try {
      helper(path);
    } catch {
    }
  }
};
const registerStencilAssetProxies = (module) => {
  onFrameworkReady.then((framework) => {
    framework.register(module, {
      getAssetPath: getAssetPathProxy,
      setAssetPath: setAssetPathProxy
    });
  }).catch(() => {
  });
};
const GLOBAL_STYLES = {
  "::-webkit-scrollbar": {
    "width": "9px"
  },
  "::-webkit-scrollbar-thumb": {
    "transition": "all 400ms cubic-bezier(0.8, -0.5, 0.2, 1.4)",
    "background-color": "rgb(var(--lf-color-primary))"
  },
  "::-webkit-scrollbar-track": {
    "background-color": "rgb(var(--lf-color-bg))"
  },
  ".lf-effects [data-lf=backdrop]": {
    "transition": "all 200ms cubic-bezier(0.4, 0, 0.6, 1)",
    "background": "rgba(0, 0, 0, 0.375)",
    "height": "100vh",
    "left": "0",
    "opacity": "0",
    "position": "fixed",
    "top": "0",
    "width": "100vw",
    "z-index": "var(--lf-ui-zindex-backdrop, 899)"
  },
  "@keyframes lf-fade-in": [
    {
      "from": {
        "visibility": "hidden",
        "opacity": "0"
      }
    },
    {
      "to": {
        "visibility": "visible",
        "opacity": "1"
      }
    }
  ],
  ".lf-effects [data-lf=lightbox]": {
    "transition": "all 200ms cubic-bezier(0.4, 0, 0.6, 1)",
    "height": "90dvh",
    "left": "5dvw",
    "position": "fixed",
    "top": "5dvh",
    "width": "90dvw",
    "z-index": "var(--lf-ui-zindex-lightbox, 900)"
  },
  ".lf-effects [data-lf=lightbox-content]": {
    "width": "100%",
    "height": "100%",
    "border": "1px solid rgba(var(--lf-color-border), 0.375)",
    "border-radius": "var(--lf-ui-border-radius)",
    "box-sizing": "border-box",
    "outline": "none",
    "z-index": "calc(var(--lf-ui-zindex-lightbox, 900) + 1)"
  },
  "@keyframes lf-pop": [
    {
      "from": {
        "opacity": "0",
        "transform": "translate(-50%, -50%) scale(0.8)"
      }
    },
    {
      "to": {
        "opacity": "1",
        "transform": "translate(-50%, -50%) scale(1)"
      }
    }
  ],
  ".lf-portal [data-lf=portal]": {
    "display": "block",
    "height": "max-content",
    "max-height": "45dvh",
    "max-width": "45dvw",
    "overflow": "auto",
    "position": "fixed",
    "width": "auto",
    "z-index": "var(--lf-ui-zindex-portal)"
  },
  "@media (max-width: 600px)": {
    ".lf-portal [data-lf=portal]": {
      "max-height": "80dvh",
      "max-width": "90dvw"
    }
  }
};
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
  "--lf-icon-attachment": `file`,
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
  "--lf-icon-image": `photo`,
  "--lf-icon-info": `hexagon-info`,
  "--lf-icon-loading": `hourglass-low`,
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
  ai: "ai",
  alertTriangle: "alert-triangle",
  arrowAutofitContent: "arrow-autofit-content",
  arrowBack: "arrow-back",
  article: "article",
  bellRinging: "bell-ringing",
  brandFacebook: "brand-facebook",
  brandGithub: "brand-github",
  brandGithubCopilot: "brand-github-copilot",
  brandInstagram: "brand-instagram",
  brandLinkedin: "brand-linkedin",
  brandNpm: "brand-npm",
  brandReddit: "brand-reddit",
  brandX: "brand-x",
  brush: "brush",
  bug: "bug",
  calendarClock: "calendar-clock",
  camera: "camera",
  cameraAi: "camera-ai",
  caretDown: "caret-down",
  caretLeft: "caret-left",
  caretRight: "caret-right",
  caretUp: "caret-up",
  chartColumn: "chart-column",
  chartHistogram: "chart-histogram",
  check: "check",
  checkbox: "checkbox",
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
  exclamationCircle: "exclamation-circle",
  file: "file",
  filterSearch: "filter-search",
  folder: "folder",
  folderOpen: "folder-open",
  forms: "forms",
  help: "help",
  hexagonAlert: "hexagon-alert",
  hexagonInfo: "hexagon-info",
  hexagonMinus: "hexagon-minus",
  hexagonMinus2: "hexagon-minus-2",
  hexagonPhoto: "hexagon-photo",
  hexagonPlus: "hexagon-plus",
  hexagonPlus2: "hexagon-plus-2",
  highlight: "highlight",
  history: "history",
  home: "home",
  hourglass: "hourglass",
  hourglassLow: "hourglass-low",
  id: "id",
  ikosaedr: "ikosaedr",
  imageInPicture: "image-in-picture",
  innerShadowBottom: "inner-shadow-bottom",
  inputSearch: "input-search",
  json: "json",
  key: "key",
  layoutBoardSplit: "layout-board-split",
  layoutList: "layout-list",
  layoutNavbar: "layout-navbar",
  layoutNavbarInactive: "layout-navbar-inactive",
  layoutSidebar: "layout-sidebar",
  lfSignature: "lf-signature",
  lfWebsite: "lf-website",
  link: "link",
  linkPlus: "link-plus",
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
  playerRecord: "player-record",
  playerStop: "player-stop",
  playstationCircle: "playstation-circle",
  playstationSquare: "playstation-square",
  playstationTriangle: "playstation-triangle",
  playstationX: "playstation-x",
  progress: "progress",
  refresh: "refresh",
  replace: "replace",
  robot: "robot",
  schema: "schema",
  select: "select",
  search: "search",
  send: "send",
  settings: "settings",
  share2: "share-2",
  shirt: "shirt",
  slideshow: "slideshow",
  squareToggle: "square-toggle",
  squareX: "square-x",
  stackPop: "stack-pop",
  stackPush: "stack-push",
  stopWatch: "stopwatch",
  sunset2: "sunset-2",
  temperature: "temperature",
  template: "template",
  terminal2: "terminal-2",
  timeDuration30: "time-duration-30",
  toggleRight: "toggle-right",
  upload: "upload",
  viewportTall: "viewport-tall",
  viewportWide: "viewport-wide",
  wand: "wand",
  writing: "writing",
  x: "x",
  zip: "zip"
};
export {
  LF_TREE_PROPS as $,
  AVATAR_COVER as A,
  LF_TABBAR_BLOCKS as B,
  CY_ATTRIBUTES as C,
  LF_TABBAR_PARTS as D,
  LF_TABBAR_PROPS as E,
  LF_LIST_BLOCKS as F,
  LF_LIST_PARTS as G,
  LF_LIST_PROPS as H,
  IDS as I,
  LF_SPINNER_PROPS as J,
  LF_TEXTFIELD_BLOCKS as K,
  LF_IMAGEVIEWER_BLOCKS as L,
  LF_TEXTFIELD_PARTS as M,
  LF_TEXTFIELD_PROPS as N,
  OPTION_TYPE_IDS as O,
  LF_DRAWER_BLOCKS as P,
  LF_DRAWER_PARTS as Q,
  LF_DRAWER_PROPS as R,
  STYLE_COVER as S,
  TIMEFRAME_COVER as T,
  LF_DRAWER_SLOT as U,
  LF_EFFECTS_FOCUSABLES as V,
  LF_PLACEHOLDER_BLOCKS as W,
  LF_PLACEHOLDER_PARTS as X,
  LF_PLACEHOLDER_PROPS as Y,
  LF_TREE_BLOCKS as Z,
  LF_TREE_PARTS as _,
  LF_ATTRIBUTES as a,
  LF_CHAT_BLOCKS as a$,
  LF_TREE_CSS_VARIABLES as a0,
  LF_AUTOCOMPLETE_BLOCKS as a1,
  LF_AUTOCOMPLETE_PARTS as a2,
  LF_AUTOCOMPLETE_PROPS as a3,
  LF_THEME_ICONS as a4,
  LF_SLIDER_BLOCKS as a5,
  LF_SLIDER_PARTS as a6,
  LF_SLIDER_CSS_VARIABLES as a7,
  LF_SLIDER_PROPS as a8,
  LF_COMPARE_BLOCKS as a9,
  LF_MASONRY_BLOCKS as aA,
  LF_MASONRY_PARTS as aB,
  LF_MASONRY_CSS_VARS as aC,
  LF_MASONRY_PROPS as aD,
  LF_MASONRY_IDS as aE,
  LF_SELECT_BLOCKS as aF,
  LF_SELECT_PARTS as aG,
  LF_SELECT_PROPS as aH,
  LF_BADGE_BLOCKS as aI,
  LF_BADGE_PARTS as aJ,
  LF_BADGE_PROPS as aK,
  LF_BUTTON_BLOCKS as aL,
  LF_BUTTON_PARTS as aM,
  LF_BUTTON_PROPS as aN,
  LF_CANVAS_BLOCKS as aO,
  LF_CANVAS_PARTS as aP,
  LF_CANVAS_PROPS as aQ,
  LF_CARD_BLOCKS as aR,
  LF_CARD_PARTS as aS,
  LF_CARD_CSS_VARS as aT,
  LF_CARD_DEFAULTS as aU,
  LF_CARD_PROPS as aV,
  LF_CHART_BLOCKS as aW,
  LF_CHART_PARTS as aX,
  LF_CHART_CSS_VARS as aY,
  LF_THEME_COLORS_DATA_PREFIX as aZ,
  LF_CHART_PROPS as a_,
  LF_COMPARE_PARTS as aa,
  LF_COMPARE_CSS_VARS as ab,
  LF_COMPARE_DEFAULTS as ac,
  LF_COMPARE_PROPS as ad,
  LF_COMPARE_IDS as ae,
  LF_SPLASH_BLOCKS as af,
  LF_SPLASH_PARTS as ag,
  LF_SPLASH_PROPS as ah,
  LF_CAROUSEL_BLOCKS as ai,
  LF_CAROUSEL_PARTS as aj,
  LF_CAROUSEL_PROPS as ak,
  LF_CAROUSEL_IDS as al,
  LF_ACCORDION_BLOCKS as am,
  LF_ACCORDION_PARTS as an,
  LF_ACCORDION_PROPS as ao,
  LF_TOAST_BLOCKS as ap,
  LF_TOAST_PARTS as aq,
  LF_TOAST_CSS_VARIABLES as ar,
  LF_TOAST_PROPS as as,
  LF_ARTICLE_BLOCKS as at,
  LF_ARTICLE_PARTS as au,
  LF_ARTICLE_PROPS as av,
  LF_RADIO_BLOCKS as aw,
  LF_RADIO_PARTS as ax,
  LF_RADIO_PROPS as ay,
  LF_MASONRY_DEFAULT_COLUMNS as az,
  LF_IMAGEVIEWER_PARTS as b,
  LF_CHAT_PARTS as b0,
  LF_CHAT_PROPS as b1,
  LF_CHIP_BLOCKS as b2,
  LF_CHIP_PARTS as b3,
  LF_CHIP_PROPS as b4,
  LF_CODE_BLOCKS as b5,
  LF_CODE_PARTS as b6,
  LF_CODE_PROPS as b7,
  LF_IMAGE_BLOCKS as b8,
  LF_IMAGE_PARTS as b9,
  getComponentProps as bA,
  markFrameworkReady as bB,
  LF_COLOR_CODES as bC,
  LF_EFFECTS_VARS as bD,
  GLOBAL_STYLES as bE,
  LF_THEME_ICONS_PREFIX as bF,
  LF_THEME_COLORS_PREFIX as bG,
  LF_THEME_ATTRIBUTE as bH,
  LF_ICONS_REGISTRY as bI,
  LF_FRAMEWORK_EVENT_NAME as bJ,
  THEME_LIST as bK,
  LF_IMAGE_CSS_VARS as ba,
  LF_IMAGE_PROPS as bb,
  CSS_VAR_PREFIX as bc,
  LF_PHOTOFRAME_BLOCKS as bd,
  LF_PHOTOFRAME_PARTS as be,
  LF_PHOTOFRAME_PROPS as bf,
  LF_PROGRESSBAR_BLOCKS as bg,
  LF_PROGRESSBAR_PARTS as bh,
  LF_PROGRESSBAR_CSS_VARIABLES as bi,
  LF_PROGRESSBAR_PROPS as bj,
  LF_TOGGLE_BLOCKS as bk,
  LF_TOGGLE_PARTS as bl,
  LF_TOGGLE_PROPS as bm,
  LF_TYPEWRITER_BLOCKS as bn,
  LF_TYPEWRITER_PARTS as bo,
  LF_TYPEWRITER_PROPS as bp,
  LF_UPLOAD_BLOCKS as bq,
  LF_UPLOAD_PARTS as br,
  LF_UPLOAD_PROPS as bs,
  LF_BADGE_CSS_VARS as bt,
  LF_CHIP_CSS_VARS as bu,
  LF_CARD_IDS as bv,
  LF_CHAT_IDS as bw,
  LF_FRAMEWORK_SYMBOL as bx,
  LF_FRAMEWORK_ALLOWED_ATTRS as by,
  LF_FRAMEWORK_ALLOWED_PREFIXES as bz,
  LF_STYLE_ID as c,
  LF_WRAPPER_ID as d,
  LF_IMAGEVIEWER_PROPS as e,
  IMAGE_TYPE_IDS as f,
  LF_MESSENGER_CLEAN_UI as g,
  LF_MESSENGER_BLOCKS as h,
  LF_MESSENGER_PARTS as i,
  LF_MESSENGER_PROPS as j,
  LF_MESSENGER_IDS as k,
  LF_MESSENGER_FILTER as l,
  LF_MESSENGER_NAV as m,
  LF_MESSENGER_MENU as n,
  onFrameworkReady as o,
  OUTFIT_COVER as p,
  LOCATION_COVER as q,
  registerStencilAssetProxies as r,
  CHILD_ROOT_MAP as s,
  LF_CHECKBOX_BLOCKS as t,
  LF_CHECKBOX_PARTS as u,
  LF_CHECKBOX_PROPS as v,
  LF_HEADER_BLOCKS as w,
  LF_HEADER_PARTS as x,
  LF_HEADER_PROPS as y,
  LF_HEADER_SLOT as z
};
//# sourceMappingURL=lf-widgets-foundations-8UtpQZAe.js.map
