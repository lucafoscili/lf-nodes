import {
  LfButtonInterface,
  LfCodeInterface,
  LfComponentName,
  LfComponentPropsFor,
  LfComponentRootElement,
  LfTextfieldInterface,
  LfToggleInterface,
  LfUploadInterface,
} from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';

//#region Helpers
const _setProps = <T extends LfComponentName>(
  comp: T,
  element: LfComponentRootElement<T>,
  props: Partial<LfComponentPropsFor<T>>,
) => {
  const { sanitizeProps } = getLfFramework();

  const el = element as Partial<LfComponentPropsFor<T>>;

  const safeProps = sanitizeProps(props, comp);
  for (const key in safeProps) {
    if (Object.hasOwn(safeProps, key)) {
      const prop = safeProps[key];
      el[key] = prop;
    }
  }
};
//#endregion

//#region Public API
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
