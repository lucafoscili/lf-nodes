import { LfArticleNode, LfDataNode } from '@lf-widgets/foundations';
import { SECTIONS } from '../../fixtures/controlPanel';
import { LfEventName } from '../../types/events/events';
import { ControlPanelCSS, ControlPanelIds } from '../../types/widgets/controlPanel';
import { TagName } from '../../types/widgets/widgets';
import { getApiRoutes, getLfManager } from '../../utils/common';
import { EV_HANDLERS, INTRO_SECTION_ID } from './events';
import { applySystemStats, getSystemLastStats, refreshSystemDashboard } from './systemDashboard';
import { setArticleDataset } from './utils';

//#region prepArticle
export const prepArticle = (key: string, node: LfArticleNode) => {
  const article = document.createElement(TagName.LfArticle);
  setArticleDataset(article, node);
  article.slot = key;
  article.addEventListener(LfEventName.LfArticle, EV_HANDLERS.article);

  return article;
};
//#endregion

const buildSection = (
  id: ControlPanelIds,
): { article: HTMLLfArticleElement; node: LfArticleNode } | null => {
  switch (id) {
    //#region Analytics
    case ControlPanelIds.Analytics: {
      const node = SECTIONS[ControlPanelIds.Analytics]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion

    //#region Backup
    case ControlPanelIds.Backup: {
      const node = SECTIONS[ControlPanelIds.Backup]();
      const article = prepArticle(id, node);
      getApiRoutes()
        .backup.getStats()
        .then((response) => {
          if (response.status === 'success') {
            const updatedNode = SECTIONS[ControlPanelIds.Backup]({
              totalSizeBytes: response.data.total_size_bytes,
              fileCount: response.data.file_count,
            });
            setArticleDataset(article, updatedNode);
          }
        });
      return { article, node };
    }
    //#endregion

    //#region Debug
    case ControlPanelIds.Debug: {
      const logsData: LfArticleNode[] = [];
      const node = SECTIONS[ControlPanelIds.Debug](logsData);
      const article = prepArticle(id, node);
      getLfManager().setDebugDataset(article, logsData);
      return { article, node };
    }
    //#endregion

    //#region ExternalPreviews
    case ControlPanelIds.ExternalPreviews: {
      const node = SECTIONS[ControlPanelIds.ExternalPreviews]();
      const article = prepArticle(id, node);
      getApiRoutes()
        .preview.getStats()
        .then((response) => {
          if (response.status === 'success') {
            const updatedNode = SECTIONS[ControlPanelIds.ExternalPreviews]({
              totalSizeBytes: response.data.total_size_bytes,
              fileCount: response.data.file_count,
            });
            setArticleDataset(article, updatedNode);
          }
        });
      return { article, node };
    }
    //#endregion

    //#region Metadata
    case ControlPanelIds.Metadata: {
      const node = SECTIONS[ControlPanelIds.Metadata]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion

    //#region System Dashboard
    case ControlPanelIds.SystemDashboard: {
      const initialStats = getSystemLastStats();
      const node = SECTIONS[ControlPanelIds.SystemDashboard](initialStats);
      const article = prepArticle(id, node);
      applySystemStats(article, initialStats);
      refreshSystemDashboard(article);
      return { article, node };
    }
    //#endregion

    //#region Theme
    case ControlPanelIds.Theme: {
      const node = SECTIONS[ControlPanelIds.Theme]();
      const article = prepArticle(id, node);
      return { article, node };
    }
    //#endregion

    default:
      return null;
  }
};

export const createContent = () => {
  const grid = document.createElement(TagName.Div);
  const accordion = document.createElement(TagName.LfAccordion);
  const nodes: LfDataNode[] = [];

  accordion.lfDataset = { nodes };

  for (const id in SECTIONS) {
    if (id !== INTRO_SECTION_ID && Object.prototype.hasOwnProperty.call(SECTIONS, id)) {
      const section = buildSection(id as ControlPanelIds);
      if (!section) {
        continue;
      }

      const { article, node } = section;
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

  const intro = prepArticle(INTRO_SECTION_ID, SECTIONS[INTRO_SECTION_ID]());

  grid.classList.add(ControlPanelCSS.Grid);
  grid.appendChild(intro);
  grid.appendChild(accordion);

  return grid;
};
//#endregion
