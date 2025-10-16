import {
  LfButtonInterface,
  LfCodeInterface,
  LfComponentName,
  LfComponentPropsFor,
  LfComponentRootElement,
} from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';

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
};
