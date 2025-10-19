import {
  LfButtonInterface,
  LfCodeInterface,
  LfComponentName,
  LfComponentPropsFor,
  LfComponentRootElement,
  LfDataCell,
  LfMasonryInterface,
  LfTextfieldInterface,
  LfToggleInterface,
  LfUploadInterface,
} from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowAPIResult } from '../types/api';
import { normalize_description } from '../utils/common';

//#region Helpers
const _chooseComponentForResult = <T extends LfComponentName>(
  key: string,
  props: Partial<LfComponentPropsFor<T>> & { _description?: string | string[] },
) => {
  const el = document.createElement('div');

  const { _description } = props;
  if (_description) {
    const desc = document.createElement('div');
    desc.innerHTML = normalize_description(_description);
    el.appendChild(desc);
  }

  switch (key) {
    case 'masonry':
      const masonry = createComponent.masonry(props);
      el.appendChild(masonry);
      break;
    default:
    case 'code':
      const code = createComponent.code(props);
      el.appendChild(code);
      break;
  }

  return el;
};
const _setProps = <T extends LfComponentName>(
  comp: T,
  element: LfComponentRootElement<T>,
  props: Partial<LfComponentPropsFor<T>> & { _slotmap?: Record<string, string> },
) => {
  if (!props) {
    return;
  }

  const { sanitizeProps } = getLfFramework();

  const hasSlots = props._slotmap && Object.keys(props._slotmap).length > 0;
  if (hasSlots) {
    _setSlots(comp, element, props);
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
  props: Partial<LfComponentPropsFor<T>> & { _slotmap?: Record<string, string> },
) => {
  for (const slotName in props._slotmap) {
    const slotHtml = props._slotmap[slotName];
    const wrapper = document.createElement('div');
    wrapper.innerHTML = slotHtml;
    wrapper.setAttribute('slot', slotName);
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
  masonry: (props: Partial<LfMasonryInterface>) => {
    const comp = document.createElement('lf-masonry');

    _setProps('LfMasonry', comp, props);
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
export const createInputCell = (cell: LfDataCell) => {
  const { sanitizeProps } = getLfFramework();

  switch (cell.shape) {
    case 'toggle': {
      return createComponent.toggle(sanitizeProps(cell as LfDataCell<'toggle'>, 'LfToggle'));
    }
    case 'upload': {
      return createComponent.upload(sanitizeProps(cell as LfDataCell<'upload'>, 'LfUpload'));
    }
    default:
    case 'textfield': {
      return createComponent.textfield(
        sanitizeProps(cell as LfDataCell<'textfield'>, 'LfTextfield'),
      );
    }
  }
};
//#endregion

//#region Outputs
export const createOutputField = (key: string, result: WorkflowAPIResult) => {
  const isArrayOfComps =
    Array.isArray(result) && result.every((item) => typeof item === 'object') && result.length > 1;
  if (isArrayOfComps) {
    const wrapper = document.createElement('div');
    wrapper.classList.add(`${key}-output-wrapper`);

    for (const item of result) {
      wrapper.appendChild(_chooseComponentForResult(key, item));
    }

    return wrapper;
  }

  const r = Array.isArray(result) ? result[0] : result;

  return _chooseComponentForResult(key, r);
};
//#endregion
