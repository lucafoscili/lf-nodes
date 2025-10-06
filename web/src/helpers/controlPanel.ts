import {
  LfArticleElement,
  LfArticleEventPayload,
  LfArticleNode,
  LfButtonEvent,
  LfButtonEventPayload,
  LfDataNode,
  LfListEventPayload,
  LfTextfieldEvent,
  LfTextfieldEventPayload,
  LfToggleEvent,
  LfToggleEventPayload,
} from '@lf-widgets/foundations';
import { SECTIONS } from '../fixtures/controlPanel';
import { BaseAPIPayload } from '../types/api/api';
import { LfEventName } from '../types/events/events';
import {
  ControlPanelCSS,
  ControlPanelIds,
  ControlPanelLabels,
  ControlPanelSection,
} from '../types/widgets/controlPanel';
import { TagName } from '../types/widgets/widgets';
import { getApiRoutes, getLfManager, isButton, isTextfield, isToggle } from '../utils/common';

const INTRO_SECTION = ControlPanelIds.GitHub;

let TIMEOUT: NodeJS.Timeout;

export const EV_HANDLERS = {
  //#region Article handler
  article: (e: CustomEvent<LfArticleEventPayload>) => {
    const { comp, eventType, originalEvent } = (e as CustomEvent<LfArticleEventPayload>).detail;

    switch (eventType) {
      case 'lf-event':
        handleLfEvent(originalEvent, comp.rootElement);
        break;
    }
  },
  //#endregion

  //#region Button handler
  button: (e: CustomEvent<LfButtonEventPayload>, slot: LfArticleElement) => {
    const { comp, eventType, originalEvent } = e.detail;

    const element = comp.rootElement;

    const invokeAPI = (promise: Promise<BaseAPIPayload>, label: ControlPanelLabels) => {
      const onResponse = () => {
        comp.lfIcon = 'check';
        comp.lfLabel = ControlPanelLabels.Done;
        comp.lfShowSpinner = false;
        comp.lfUiState = 'disabled';
      };
      const restore = (label: ControlPanelLabels) => {
        comp.lfLabel = label;
        comp.lfIcon = 'x';
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
            getApiRoutes().backup.cleanOld();
            break;
          case ControlPanelLabels.ClearLogs:
            const { article, dataset } = getLfManager().getDebugDataset();
            if (dataset?.length > 0) {
              dataset.splice(0, dataset.length);
              article.refresh();
            }
            break;
          case ControlPanelLabels.ClearPreviews:
            invokeAPI(getApiRoutes().preview.clearCache(), ControlPanelLabels.ClearPreviews);
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
          case ControlPanelLabels.RefreshPreviewStats:
            getApiRoutes()
              .preview.getStats()
              .then((response) => {
                if (response.status === 'success') {
                  const updatedNode = SECTIONS[ControlPanelIds.ExternalPreviews]({
                    totalSizeBytes: response.data.total_size_bytes,
                    fileCount: response.data.file_count,
                  });
                  slot.lfDataset = {
                    nodes: [{ children: [updatedNode], id: ControlPanelSection.Root }],
                  };
                }
              });
            break;
          case ControlPanelLabels.RefreshBackupStats:
            getApiRoutes()
              .backup.getStats()
              .then((response) => {
                if (response.status === 'success') {
                  const updatedNode = SECTIONS[ControlPanelIds.Backup]({
                    totalSizeBytes: response.data.total_size_bytes,
                    fileCount: response.data.file_count,
                  });
                  slot.lfDataset = {
                    nodes: [{ children: [updatedNode], id: ControlPanelSection.Root }],
                  };
                }
              });
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
  textfield: (e: CustomEvent<LfTextfieldEventPayload>) => {
    const { comp, eventType, value } = e.detail;

    const element = comp.rootElement;

    switch (eventType as LfTextfieldEvent) {
      case 'change':
        const retentionValue = parseInt(value, 10);
        if (!isNaN(retentionValue) && retentionValue >= 0) {
          getLfManager().setBackupRetention(retentionValue);
        }
        break;
      case 'ready':
        element.title = 'Maximum number of backups to keep (0 = unlimited)';
    }
  },
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
      let article: HTMLLfArticleElement;
      let node: LfDataNode;

      switch (id) {
        case ControlPanelIds.Debug:
          const logsData: LfArticleNode[] = [];
          node = SECTIONS[ControlPanelIds.Debug](logsData);
          article = prepArticle(id, node);
          getLfManager().setDebugDataset(article, logsData);
          break;

        case ControlPanelIds.ExternalPreviews:
          node = SECTIONS[ControlPanelIds.ExternalPreviews]();
          article = prepArticle(id, node);
          getApiRoutes()
            .preview.getStats()
            .then((response) => {
              if (response.status === 'success') {
                const updatedNode = SECTIONS[ControlPanelIds.ExternalPreviews]({
                  totalSizeBytes: response.data.total_size_bytes,
                  fileCount: response.data.file_count,
                });
                article.lfDataset = {
                  nodes: [{ children: [updatedNode], id: ControlPanelSection.Root }],
                };
              }
            });
          break;

        case ControlPanelIds.Analytics:
          node = SECTIONS[ControlPanelIds.Analytics]();
          article = prepArticle(id, node);
          break;

        case ControlPanelIds.Backup:
          node = SECTIONS[ControlPanelIds.Backup]();
          article = prepArticle(id, node);
          getApiRoutes()
            .backup.getStats()
            .then((response) => {
              if (response.status === 'success') {
                const updatedNode = SECTIONS[ControlPanelIds.Backup]({
                  totalSizeBytes: response.data.total_size_bytes,
                  fileCount: response.data.file_count,
                });
                article.lfDataset = {
                  nodes: [{ children: [updatedNode], id: ControlPanelSection.Root }],
                };
              }
            });
          break;

        case ControlPanelIds.Metadata:
          node = SECTIONS[ControlPanelIds.Metadata]();
          article = prepArticle(id, node);
          break;

        case ControlPanelIds.Theme:
          node = SECTIONS[ControlPanelIds.Theme]();
          article = prepArticle(id, node);
          break;

        default:
          continue;
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
export const handleLfEvent = (e: Event, slot: LfArticleElement) => {
  const { comp } = (
    e as CustomEvent<
      LfButtonEventPayload | LfListEventPayload | LfTextfieldEventPayload | LfToggleEventPayload
    >
  ).detail;

  if (isButton(comp)) {
    const ogEv = e as CustomEvent<LfButtonEventPayload>;
    EV_HANDLERS.button(ogEv, slot);
  }

  if (isTextfield(comp)) {
    const ogEv = e as CustomEvent<LfTextfieldEventPayload>;
    EV_HANDLERS.textfield(ogEv);
  }

  if (isToggle(comp)) {
    const ogEv = e as CustomEvent<LfToggleEventPayload>;
    EV_HANDLERS.toggle(ogEv);
  }
};
//#endregion
