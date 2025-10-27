import {
  LfButtonInterface,
  LfCodeInterface,
  LfComponentName,
  LfComponentPropsFor,
  LfComponentRootElement,
  LfMasonryInterface,
  LfTextfieldInterface,
  LfToggleInterface,
  LfUploadInterface,
} from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowCellInput, WorkflowCellOutput } from '../types/api';

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
//#endregion

//#region Components
export const createComponent = {
  button: (props: Partial<LfButtonInterface>) => {
    const comp = document.createElement('lf-button');

    _setProps('LfButton', comp, props);
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
export const createOutputComponent = (descriptor: WorkflowCellOutput) => {
  const { syntax } = getLfFramework();
  const { dataset, json, metadata, props, shape, slot_map, svg } = descriptor;
  const el = document.createElement('div');

  switch (shape) {
    case 'code': {
      const p = (props || {}) as Partial<LfCodeInterface>;
      p.lfValue =
        svg ||
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
