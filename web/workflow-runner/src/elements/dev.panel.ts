import type { LfDataDataset } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowSectionController } from '../types/section';
import { WorkflowState } from '../types/state';

//#region Constants
const ROOT_CLASS = 'dev-panel';
const CARD_CLASS = `${ROOT_CLASS}__card`;
type LfCardElement = HTMLElementTagNameMap['lf-card'];
//#endregion

//#region Factory
export const createDevPanel = (): WorkflowSectionController => {
  const framework = getLfFramework();
  const debugCardDataset: LfDataDataset = {
    nodes: [
      {
        id: 'workflow-runner-debug',
        cells: {
          lfToggle: {
            shape: 'toggle',
            lfValue: framework.debug.isEnabled(),
            value: framework.debug.isEnabled(),
          },
          lfCode: {
            shape: 'code',
            value: '',
          },
          lfButton: {
            shape: 'button',
            value: '',
          },
          lfButton_2: {
            shape: 'button',
            value: '',
          },
        },
      },
    ],
  };

  let container: HTMLDivElement | null = null;
  let card: LfCardElement | null = null;
  let mountedState: WorkflowState | null = null;

  const mount = (state: WorkflowState) => {
    if (container) {
      return;
    }

    mountedState = state;

    container = document.createElement('div');
    container.className = ROOT_CLASS;
    container.dataset.open = 'false';
    container.setAttribute('aria-hidden', 'true');

    card = document.createElement('lf-card');
    card.className = CARD_CLASS;
    card.lfLayout = 'debug';
    card.lfDataset = debugCardDataset;

    container.appendChild(card);
    (state.ui.layout._root?.ownerDocument?.body ?? document.body).appendChild(container);

    if (state.dev.panel.open) {
      container.dataset.open = 'true';
      container.setAttribute('aria-hidden', 'false');
    }

    state.mutate.ui((ui) => {
      ui.layout.dev._root = container;
      ui.layout.dev.card = card;
    });
  };

  const render = (state: WorkflowState) => {
    if (!container) {
      return;
    }

    const isOpen = state.dev.panel.open;
    container.dataset.open = String(isOpen);
    container.setAttribute('aria-hidden', String(!isOpen));
  };

  const destroy = () => {
    if (container?.isConnected) {
      container.remove();
    }

    if (mountedState) {
      mountedState.mutate.ui((ui) => {
        ui.layout.dev._root = null;
        ui.layout.dev.card = null;
      });
    }

    container = null;
    card = null;
    mountedState = null;
  };

  return {
    mount,
    render,
    destroy,
  };
};
//#endregion
