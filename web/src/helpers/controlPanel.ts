import {
  LfArticleEventPayload,
  LfArticleNode,
  LfButtonEvent,
  LfButtonEventPayload,
  LfDataNode,
  LfListEventPayload,
  LfToggleEvent,
  LfToggleEventPayload,
} from '@lf-widgets/foundations';
import { SECTIONS } from '../fixtures/controlPanel';
import { BaseAPIPayload } from '../types/api/api';
import { LfEventName } from '../types/events/events';
import {
  ControlPanelCSS,
  ControlPanelFixture,
  ControlPanelIds,
  ControlPanelLabels,
  ControlPanelSection,
} from '../types/widgets/controlPanel';
import { TagName } from '../types/widgets/widgets';
import { getApiRoutes, getLfManager, isButton, isToggle } from '../utils/common';

const INTRO_SECTION = ControlPanelIds.GitHub;

let TIMEOUT: NodeJS.Timeout;

export const EV_HANDLERS = {
  //#region Article handler
  article: (e: CustomEvent<LfArticleEventPayload>) => {
    const { eventType, originalEvent } = (e as CustomEvent<LfArticleEventPayload>).detail;

    switch (eventType) {
      case 'lf-event':
        handleLfEvent(originalEvent);
        break;
    }
  },
  //#endregion

  //#region Button handler
  button: (e: CustomEvent<LfButtonEventPayload>) => {
    const { comp, eventType, originalEvent } = e.detail;

    const element = comp.rootElement;

    const createSpinner = () => {
      const spinner = document.createElement('lf-spinner');
      spinner.lfActive = true;
      spinner.lfDimensions = '0.6em';
      spinner.lfLayout = 2;
      spinner.slot = 'spinner';
      return spinner;
    };

    const invokeAPI = (promise: Promise<BaseAPIPayload>, label: ControlPanelLabels) => {
      const onResponse = () => {
        comp.lfIcon = 'check';
        comp.lfLabel = ControlPanelLabels.Done;
        comp.lfShowSpinner = false;
        comp.lfUiState = 'disabled';
      };
      const restore = (label: ControlPanelLabels) => {
        comp.lfLabel = label;
        comp.lfIcon = 'delete';
        comp.lfUiState = 'primary';
        TIMEOUT = null;
      };
      requestAnimationFrame(() => (comp.lfShowSpinner = true));
      promise.then(() => {
        requestAnimationFrame(onResponse);

        if (TIMEOUT) {
          clearTimeout(TIMEOUT);
        }

        TIMEOUT = setTimeout(() => requestAnimationFrame(() => restore(label)), 1000);
      });
    };

    switch (eventType as LfButtonEvent) {
      case 'click':
        switch (comp.lfLabel) {
          case ControlPanelLabels.Backup:
            invokeAPI(getApiRoutes().backup.new('manual'), ControlPanelLabels.Backup);
            break;
          case ControlPanelLabels.ClearLogs:
            const { article, dataset } = getLfManager().getDebugDataset();
            if (dataset?.length > 0) {
              dataset.splice(0, dataset.length);
              article.refresh();
            }
            break;
          case ControlPanelLabels.DeleteMetadata:
            invokeAPI(getApiRoutes().metadata.clear(), ControlPanelLabels.DeleteMetadata);
            break;
          case ControlPanelLabels.DeleteUsage:
            invokeAPI(getApiRoutes().analytics.clear('usage'), ControlPanelLabels.DeleteUsage);
            break;
          case ControlPanelLabels.OpenIssue:
            window.open('https://github.com/lucafoscili/comfyui-lf/issues/new', '_blank');
            break;
          case ControlPanelLabels.Theme:
            getLfManager().getManagers().lfFramework.theme.randomize();
            break;
          default:
            break;
        }
        break;

      case 'lf-event':
        const ogEv = originalEvent as CustomEvent<LfListEventPayload>;
        EV_HANDLERS.list(ogEv);
        break;

      case 'ready':
        switch (comp.lfLabel) {
          case ControlPanelLabels.Backup:
            element.appendChild(createSpinner());
            break;
          case ControlPanelLabels.DeleteMetadata:
          case ControlPanelLabels.DeleteUsage:
            element.classList.add('lf-danger');
            element.appendChild(createSpinner());
            break;
        }
    }
  },
  //#endregion

  //#region List handler
  list: (e: CustomEvent<LfListEventPayload>) => {
    const { comp, eventType, node } = e.detail;

    const { lfFramework } = getLfManager().getManagers();
    const element = comp.rootElement;
    const value = node.id;

    switch (eventType) {
      case 'click':
        lfFramework.theme.set(value);
        break;
      case 'ready':
        element.title = 'Change the LF Nodes suite theme';
        lfFramework.theme.set(value);
        break;
    }
  },
  //#endregion

  //#region Toggle handler
  toggle: (e: CustomEvent<LfToggleEventPayload>) => {
    const { comp, eventType, value } = e.detail;

    const element = comp.rootElement;

    switch (eventType as LfToggleEvent) {
      case 'change':
        getLfManager().toggleDebug(value === 'on' ? true : false);
        break;
      case 'ready':
        element.title = 'Activate verbose console logging';
    }
  },
  //#endregion
};

//#region createContent
export const createContent = () => {
  const grid = document.createElement(TagName.Div);
  const accordion = document.createElement(TagName.LfAccordion);

  const nodes: LfDataNode[] = [];

  accordion.lfDataset = { nodes };

  for (const id in SECTIONS) {
    if (id !== INTRO_SECTION && Object.prototype.hasOwnProperty.call(SECTIONS, id)) {
      const section = SECTIONS[id as keyof ControlPanelFixture];
      let article: HTMLLfArticleElement;
      let node: LfDataNode;

      switch (id) {
        case ControlPanelIds.Debug:
          const logsData: LfArticleNode[] = [];
          node = section(logsData);
          article = prepArticle(id, node);
          getLfManager().setDebugDataset(article, logsData);
          break;

        default:
          node = section(undefined);
          article = prepArticle(id, node);
          break;
      }

      const { icon, value } = node;
      nodes.push({
        cells: {
          lfSlot: {
            shape: 'slot',
            value: id,
          },
        },
        icon,
        id,
        value,
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
//#endregion

//#region prepArticle
export const prepArticle = (key: string, node: LfArticleNode) => {
  const article = document.createElement(TagName.LfArticle);
  article.lfDataset = { nodes: [{ children: [node], id: ControlPanelSection.Root }] };
  article.slot = key;
  article.addEventListener(LfEventName.LfArticle, EV_HANDLERS.article);

  return article;
};
//#endregion

//#region handleLfEvent
export const handleLfEvent = (e: Event) => {
  const { comp } = (
    e as CustomEvent<LfButtonEventPayload | LfListEventPayload | LfToggleEventPayload>
  ).detail;

  if (isButton(comp)) {
    const ogEv = e as CustomEvent<LfButtonEventPayload>;
    EV_HANDLERS.button(ogEv);
  }

  if (isToggle(comp)) {
    const ogEv = e as CustomEvent<LfToggleEventPayload>;
    EV_HANDLERS.toggle(ogEv);
  }
};
//#endregion
