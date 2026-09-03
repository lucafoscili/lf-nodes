import {
  LfButtonInterface,
  LfChatInterface,
  LfCodeInterface,
  LfCompareInterface,
  LfComponentName,
  LfComponentPropsFor,
  LfComponentRootElement,
  LfMasonryInterface,
  LfIconType,
  LfSelectEventPayload,
  LfTextfieldInterface,
  LfThemeUIState,
  LfToggleInterface,
  LfUploadInterface,
} from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { CHAT_ENDPOINT } from '../config';
import {
  ComfyFileArtifact,
  WorkflowCellInput,
  WorkflowCellOutput,
  WorkflowProfileTier,
  WorkflowSelectNode,
  WorkflowSelectProps,
} from '../types/api';
import { artifactViewUrl } from '../utils/artifacts';

//#region Helpers
const _setProps = <T extends LfComponentName>(
  comp: T,
  element: LfComponentRootElement<T>,
  props: Partial<LfComponentPropsFor<T>>,
  slotMap: Record<string, string> = {},
) => {
  if (!props) {
    return;
  }

  const { sanitizeProps } = getLfFramework();

  const hasSlots = Object.keys(slotMap).length > 0;
  if (hasSlots) {
    _setSlots(comp, element, slotMap);
  }

  const el = element as Partial<LfComponentPropsFor<T>>;
  const safeProps = sanitizeProps(props, comp);
  for (const key in safeProps) {
    if (Object.hasOwn(safeProps, key)) {
      const prop = safeProps[key];
      el[key] = prop;
    }
  }
};
const _setSlots = <T extends LfComponentName>(
  _comp: T,
  element: HTMLElement,
  slotMap: Record<string, string>,
) => {
  for (const slotName in slotMap) {
    const slotHtml = slotMap[slotName];
    const wrapper = document.createElement('div');
    wrapper.innerHTML = slotHtml;
    wrapper.setAttribute('slot', slotName);
    wrapper.style.fill = 'rgba(var(--lf-color-secondary, 1))';
    wrapper.style.stroke = 'rgba(var(--lf-color-primary, 1))';
    element.appendChild(wrapper);

    if (slotName.toLowerCase().endsWith('.svg')) {
      const dlButton = createComponent.button({
        lfAriaLabel: 'Download SVG',
        lfIcon: 'download',
        lfLabel: 'Download SVG',
        lfStretchX: true,
        lfUiState: 'success',
      });
      dlButton.onclick = () => {
        const blob = new Blob([slotHtml], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = slotName.toLowerCase().endsWith('.svg') ? slotName : `${slotName}.svg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      };
      dlButton.style.position = 'absolute';
      dlButton.style.bottom = '0';
      wrapper.style.display = 'grid';
      wrapper.style.gridTemplateRows = '1fr auto';
      wrapper.style.margin = '0 auto';
      wrapper.style.maxWidth = '360px';
      wrapper.style.position = 'relative';
      wrapper.appendChild(dlButton);
    }
  }
};

const PROFILE_TIER_PRESENTATION: Record<
  WorkflowProfileTier,
  { icon: LfIconType; state: LfThemeUIState }
> = {
  fast: { icon: 'stopwatch', state: 'info' },
  baseline: { icon: 'contrast-2', state: 'primary' },
  quality: { icon: 'wand', state: 'secondary' },
};

const _profileTier = (node: WorkflowSelectNode | undefined): WorkflowProfileTier | null => {
  const tier = node?.profileTier;
  return tier && Object.prototype.hasOwnProperty.call(PROFILE_TIER_PRESENTATION, tier)
    ? tier
    : null;
};

const _profileSelectProps = (props: WorkflowSelectProps): WorkflowSelectProps => {
  const nodes = props.lfDataset?.nodes;
  if (!nodes?.some((node) => _profileTier(node))) {
    return props;
  }

  return {
    ...props,
    lfDataset: {
      ...props.lfDataset,
      nodes: nodes.map((node) => {
        const tier = _profileTier(node);
        return tier
          ? { ...node, icon: PROFILE_TIER_PRESENTATION[tier].icon }
          : node;
      }),
    },
  } satisfies WorkflowSelectProps;
};

const _bindProfileSelect = (
  comp: HTMLLfSelectElement,
  props: WorkflowSelectProps,
) => {
  const nodes = props.lfDataset?.nodes;
  if (!nodes?.some((node) => _profileTier(node))) {
    return;
  }

  const baseTextfieldProps = { ...(props.lfTextfieldProps || {}) };
  const mayDecorateState = props.lfUiState === undefined;
  const baseState: LfThemeUIState = props.lfUiState ?? 'primary';
  let appliedTierState: LfThemeUIState | undefined = mayDecorateState
    ? baseState
    : undefined;
  const apply = (node: WorkflowSelectNode | undefined) => {
    const tier = _profileTier(node);
    const currentState = comp.lfUiState;
    const ownsState =
      mayDecorateState &&
      (currentState === appliedTierState || currentState === undefined);
    if (!tier) {
      if (ownsState) {
        comp.lfUiState = baseState;
        appliedTierState = baseState;
      }
      comp.lfTextfieldProps = baseTextfieldProps;
      return;
    }
    const presentation = PROFILE_TIER_PRESENTATION[tier];
    if (ownsState) {
      comp.lfUiState = presentation.state;
      appliedTierState = presentation.state;
    }
    comp.lfTextfieldProps = {
      ...baseTextfieldProps,
      lfIcon: presentation.icon,
    };
  };

  const initialNode =
    typeof props.lfValue === 'number'
      ? nodes[props.lfValue]
      : nodes.find((node) => node.id === String(props.lfValue ?? ''));
  apply(initialNode);
  comp.addEventListener('lf-select-event', (event) => {
    const detail = (event as CustomEvent<LfSelectEventPayload>).detail;
    if (detail?.eventType === 'change') {
      apply(detail.node);
    }
  });
};
//#endregion

//#region Components
export const createComponent = {
  button: (props: Partial<LfButtonInterface>) => {
    const comp = document.createElement('lf-button');

    _setProps('LfButton', comp as any, props); // FIXME: TypeScript issue with next release
    return comp;
  },
  chat: (props: Partial<LfChatInterface>) => {
    const comp = document.createElement('lf-chat');

    if (CHAT_ENDPOINT) {
      comp.lfEndpointUrl = CHAT_ENDPOINT;
    }
    _setProps('LfChat', comp, props);
    return comp;
  },
  code: (props: Partial<LfCodeInterface>) => {
    const comp = document.createElement('lf-code');

    _setProps('LfCode', comp, props);
    return comp;
  },
  masonry: (props: Partial<LfMasonryInterface>, slot_map?: Record<string, string>) => {
    const comp = document.createElement('lf-masonry');

    _setProps('LfMasonry', comp, props, slot_map);
    return comp;
  },
  compare: (props: Partial<LfCompareInterface>) => {
    const comp = document.createElement('lf-compare');

    comp.className = 'workflow-output-compare';
    _setProps('LfCompare', comp, props);
    return comp;
  },
  select: (props: WorkflowSelectProps) => {
    const comp = document.createElement('lf-select');
    const profileProps = _profileSelectProps(props);

    _setProps('LfSelect', comp, profileProps);
    _bindProfileSelect(comp, profileProps);
    return comp;
  },
  textfield: (props: Partial<LfTextfieldInterface>) => {
    const comp = document.createElement('lf-textfield');

    _setProps('LfTextfield', comp, props);
    return comp;
  },
  toggle: (props: Partial<LfToggleInterface>) => {
    const comp = document.createElement('lf-toggle');

    _setProps('LfToggle', comp, props);
    return comp;
  },
  upload: (props: Partial<LfUploadInterface>) => {
    const comp = document.createElement('lf-upload');

    _setProps('LfUpload', comp, props);
    return comp;
  },
};
//#endregion

//#region Inputs
export const createInputCell = (cell: WorkflowCellInput) => {
  const { sanitizeProps } = getLfFramework();
  const { props, shape } = cell;

  switch (shape) {
    case 'chat': {
      const p = (props || {}) as Partial<LfChatInterface>;
      return createComponent.chat(sanitizeProps(p, 'LfChat'));
    }
    case 'choice':
    case 'select': {
      const p = (props || {}) as WorkflowSelectProps;
      return createComponent.select(sanitizeProps(p, 'LfSelect') as WorkflowSelectProps);
    }
    case 'toggle': {
      const p = (props || {}) as Partial<LfToggleInterface>;
      return createComponent.toggle(sanitizeProps(p, 'LfToggle'));
    }
    case 'upload': {
      const p = (props || {}) as Partial<LfUploadInterface>;
      return createComponent.upload(sanitizeProps(p, 'LfUpload'));
    }
    default:
    case 'textfield': {
      const p = (props || {}) as Partial<LfTextfieldInterface>;
      return createComponent.textfield(sanitizeProps(p, 'LfTextfield'));
    }
  }
};
//#endregion

//#region Outputs
const _outputRelativeArtifact = (value: unknown): ComfyFileArtifact | null => {
  if (typeof value !== 'string' || !value || value.includes('\\')) {
    return null;
  }

  const parts = value.split('/');
  if (
    parts.some((part) => !part || part === '.' || part === '..') ||
    !parts.every((part) => /^[^\\/:\x00-\x1F\x7F]+$/.test(part))
  ) {
    return null;
  }

  const filename = parts.pop();
  if (!filename) {
    return null;
  }

  return {
    filename,
    subfolder: parts.join('/'),
    type: 'output',
  };
};

const _fileNameArtifacts = (fileNames: string[] | undefined) =>
  Array.isArray(fileNames)
    ? fileNames
        .map(_outputRelativeArtifact)
        .filter((artifact): artifact is ComfyFileArtifact => artifact !== null)
    : [];

const _isBrowserImage = (artifact: ComfyFileArtifact, mediaType: string) =>
  /^(?:image\/(?:png|jpe?g|gif|webp|avif|apng|svg\+xml))$/.test(mediaType) ||
  /\.(?:png|jpe?g|gif|webp|avif|apng|svg)$/i.test(artifact.filename);

const _mediaOutput = (artifacts: ComfyFileArtifact[] | undefined) => {
  if (!Array.isArray(artifacts) || artifacts.length === 0) {
    return null;
  }

  const media = document.createElement('div');
  media.className = 'workflow-output-media';

  for (const artifact of artifacts) {
    if (!artifact?.filename) {
      continue;
    }

    const item = document.createElement('figure');
    item.className = 'workflow-output-media__item';

    const src = artifactViewUrl(artifact);
    const mediaType = artifact.media_type?.toLowerCase() || '';
    const isAudio = mediaType.startsWith('audio/') || /\.(?:wav|mp3|m4a|flac|ogg|opus)$/i.test(artifact.filename);
    const isVideo = mediaType.startsWith('video/') || /\.(?:mp4|webm)$/i.test(artifact.filename);
    const isBrowserImage = _isBrowserImage(artifact, mediaType);
    if (isAudio) {
      const audio = document.createElement('audio');
      audio.className = 'workflow-output-media__preview';
      audio.controls = true;
      audio.preload = 'metadata';
      audio.src = src;
      item.appendChild(audio);
    } else if (isVideo) {
      const video = document.createElement('video');
      video.className = 'workflow-output-media__preview';
      video.controls = true;
      video.playsInline = true;
      video.preload = 'metadata';
      video.src = src;
      item.appendChild(video);
    } else if (isBrowserImage) {
      const image = document.createElement('img');
      image.alt = artifact.filename;
      image.className = 'workflow-output-media__preview';
      image.loading = 'lazy';
      image.src = src;
      item.appendChild(image);
    } else {
      const note = document.createElement('span');
      note.className = 'workflow-output-media__note';
      note.textContent = 'Preview is not available in the browser.';
      item.appendChild(note);
    }

    const link = document.createElement('a');
    link.className = 'workflow-output-media__link';
    link.href = src;
    if (!isAudio && !isVideo && !isBrowserImage) {
      link.download = artifact.filename;
    }
    link.rel = 'noopener';
    link.target = '_blank';
    link.textContent =
      !isAudio && !isVideo && !isBrowserImage
        ? `Download ${artifact.filename}`
        : artifact.filename;
    item.appendChild(link);

    media.appendChild(item);
  }

  return media.childElementCount > 0 ? media : null;
};

export const createOutputComponent = (descriptor: WorkflowCellOutput) => {
  const { syntax } = getLfFramework();
  const modelArtifacts = descriptor['3d'];
  const {
    civitai_metadata,
    dataset,
    audio,
    file_names,
    audios,
    images,
    json,
    metadata,
    props,
    shape,
    slot_map,
    string,
    svg,
  } = descriptor;
  const el = document.createElement('div');
  const standardArtifacts = [
    ...(images || []),
    ...(audio || []),
    ...(audios || []),
    ...(modelArtifacts || []),
  ];
  const media = _mediaOutput(
    standardArtifacts.length > 0 ? standardArtifacts : _fileNameArtifacts(file_names),
  );
  if (media) {
    el.appendChild(media);
    const hasLegacyPayload =
      shape === 'masonry'
        ? dataset !== undefined && dataset !== null
        : Boolean(
            string ||
              svg ||
              civitai_metadata ||
              file_names?.length ||
              json ||
              metadata ||
              dataset,
          );
    if (!hasLegacyPayload) {
      return el;
    }
  }

  switch (shape) {
    case 'compare': {
      const p = (props || {}) as Partial<LfCompareInterface>;
      p.lfDataset = (dataset || json || { nodes: [] }) as LfCompareInterface['lfDataset'];
      p.lfShape ||= 'image';
      const compare = createComponent.compare(p);
      el.appendChild(compare);
      break;
    }
    case 'code': {
      const p = (props || {}) as Partial<LfCodeInterface>;
      p.lfValue =
        string ||
        svg ||
        civitai_metadata ||
        file_names?.join('\n') ||
        syntax.json.unescape(json || metadata || dataset || { message: 'No output available.' })
          .unescapedString;
      const code = createComponent.code(p);
      el.appendChild(code);
      break;
    }
    case 'masonry': {
      const p = (props || {}) as Partial<LfMasonryInterface>;
      p.lfDataset = dataset;
      const masonry = createComponent.masonry(p, slot_map);
      el.appendChild(masonry);
      break;
    }
    default: {
      const fallback = document.createElement('pre');
      fallback.textContent = 'No output available.';
      el.appendChild(fallback);
      break;
    }
  }

  return el;
};
//#endregion
