import { LfButtonEventPayload, LfPortalAnchor } from '@lf-widgets/foundations';
import { LfEventName } from '../types/events/events';
import {
  LogSeverity,
  TooltipCallbacks,
  TooltipLayouts,
  TooltipUploadCallback,
} from '../types/manager/manager';
import { TagName } from '../types/widgets/widgets';
import { getLfManager } from '../utils/common';

export class LFTooltip {
  #CB: {
    upload?: TooltipUploadCallback;
  } = {};
  #CSS_CLASSES = {
    wrapper: 'lf-tooltip',
    content: `lf-tooltip__content`,
  };
  #LAYOUT: TooltipLayouts; // more in the future?
  #TOOLTIP_ELEMENT: HTMLDivElement;

  //#region Initialize
  #initialize() {
    this.#TOOLTIP_ELEMENT?.remove();
    this.#TOOLTIP_ELEMENT = null;
    this.#CB = {};
    this.#LAYOUT = null;
  }
  //#endregion

  //#region Upload layout
  #uploadLayout() {
    const content = document.createElement(TagName.Div);
    const upload = document.createElement(TagName.LfUpload);
    const button = document.createElement(TagName.LfButton);

    content.classList.add(this.#CSS_CLASSES.content);

    upload.lfHtmlAttributes = { accept: 'image/*', multiple: 'false' };

    button.lfIcon = 'upload';
    button.lfLabel = 'Update cover';
    button.lfStretchX = true;

    content.dataset.lf = 'portal';
    content.appendChild(upload);
    content.appendChild(button);

    button.addEventListener(
      LfEventName.LfButton,
      this.#buttonEventHandler.bind(this.#buttonEventHandler, upload),
    );

    return content;
  }
  //#endregion

  //#region Button event handler
  #buttonEventHandler = async (
    upload: HTMLLfUploadElement,
    e: CustomEvent<LfButtonEventPayload>,
  ) => {
    const { eventType } = e.detail;

    switch (eventType) {
      case 'click':
        const lfManager = getLfManager();
        switch (this.#LAYOUT) {
          case 'upload':
            const files = await upload.getValue();

            const reader = new FileReader();
            reader.onload = (e) => {
              const result = e.target?.result;
              let base64String = '';

              if (typeof result === 'string') {
                base64String = result.replace(/^data:.*,/, '');
              } else if (result instanceof ArrayBuffer) {
                const arrayBufferView = new Uint8Array(result);
                base64String = btoa(String.fromCharCode.apply(null, arrayBufferView));
              }

              if (this.#CB) {
                lfManager.log('Invoking upload callback.', { base64String }, LogSeverity.Info);
                this.#CB[this.#LAYOUT](base64String);
              }
            };
            reader.readAsDataURL(files[0]);
            break;
        }
    }
  };
  //#endregion

  //#region Create
  create<T extends TooltipLayouts>(anchor: LfPortalAnchor, layout: T, cb?: TooltipCallbacks) {
    const lfFramework = getLfManager().getManagers().lfFramework;
    if (this.#TOOLTIP_ELEMENT) {
      this.#initialize();
    }

    const parent = document.body;

    this.#CB = cb ? { [layout]: cb } : {};
    this.#LAYOUT = layout ?? 'upload';
    this.#TOOLTIP_ELEMENT = document.createElement('div');
    this.#TOOLTIP_ELEMENT.classList.add(this.#CSS_CLASSES.wrapper);

    let layoutElement: HTMLDivElement;

    switch (this.#LAYOUT) {
      case 'upload':
        layoutElement = this.#uploadLayout();
        this.#TOOLTIP_ELEMENT.appendChild(layoutElement);
        break;
    }

    lfFramework.portal.open(layoutElement, this.#TOOLTIP_ELEMENT, anchor, 0, 'auto');
    lfFramework.addClickCallback({ cb: () => this.destroy(), element: layoutElement });

    requestAnimationFrame(() => parent.appendChild(this.#TOOLTIP_ELEMENT));
  }
  //#endregion

  //#region Destroy
  destroy() {
    this.#initialize();
  }
  //#endregion
}
