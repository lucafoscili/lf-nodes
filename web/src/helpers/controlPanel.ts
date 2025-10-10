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
  ControlPanelSystemStats,
} from '../types/widgets/controlPanel';
import { TagName } from '../types/widgets/widgets';
import { getApiRoutes, getLfManager, isButton, isTextfield, isToggle } from '../utils/common';
import { LogSeverity } from '../types/manager/manager';

const INTRO_SECTION = ControlPanelIds.GitHub;

let TIMEOUT: NodeJS.Timeout;
let SYSTEM_REFRESH_TIMER: NodeJS.Timeout | null = null;
let SYSTEM_REFRESH_SECONDS = 0;
let SYSTEM_ARTICLE: LfArticleElement | null = null;
let SYSTEM_LAST_STATS: ControlPanelSystemStats | undefined;

const clearSystemAutoRefresh = () => {
  if (SYSTEM_REFRESH_TIMER) {
    clearTimeout(SYSTEM_REFRESH_TIMER);
    SYSTEM_REFRESH_TIMER = null;
  }
};

const scheduleSystemAutoRefresh = () => {
  clearSystemAutoRefresh();

  if (
    SYSTEM_REFRESH_SECONDS <= 0 ||
    !SYSTEM_ARTICLE ||
    !SYSTEM_ARTICLE.isConnected ||
    !document.body.contains(SYSTEM_ARTICLE)
  ) {
    return;
  }

  const delay = Math.max(SYSTEM_REFRESH_SECONDS * 1000, 1000);
  SYSTEM_REFRESH_TIMER = setTimeout(() => {
    if (!SYSTEM_ARTICLE || !SYSTEM_ARTICLE.isConnected) {
      clearSystemAutoRefresh();
      return;
    }

    refreshSystemDashboard(SYSTEM_ARTICLE, { reschedule: false }).finally(() => {
      scheduleSystemAutoRefresh();
    });
  }, delay);
};

const applySystemStats = (article: LfArticleElement, stats?: ControlPanelSystemStats) => {
  const nextStats = stats
    ? { ...stats }
    : SYSTEM_LAST_STATS
    ? { ...SYSTEM_LAST_STATS }
    : undefined;

  if (nextStats) {
    nextStats.autoRefreshSeconds = SYSTEM_REFRESH_SECONDS;
    SYSTEM_LAST_STATS = nextStats;
  }

  article.lfDataset = {
    nodes: [{ children: [SECTIONS[ControlPanelIds.SystemDashboard](nextStats)], id: ControlPanelSection.Root }],
  };
};

const gatherSystemStats = async (): Promise<ControlPanelSystemStats> => {
  const routes = getApiRoutes().system;
  const [gpu, cpu, ram, disks] = await Promise.all([
    routes.getGpuStats(),
    routes.getCpuStats(),
    routes.getRamStats(),
    routes.getDiskStats(),
  ]);

  const stats: ControlPanelSystemStats = { timestamp: Date.now() };
  const errors: string[] = [];

  if (gpu.status === LogSeverity.Success) {
    stats.gpus = gpu.data || [];
  } else {
    errors.push(`GPU: ${gpu.message || 'Statistics unavailable.'}`);
  }

  if (cpu.status === LogSeverity.Success) {
    stats.cpu = cpu.data;
  } else {
    errors.push(`CPU: ${cpu.message || 'Statistics unavailable.'}`);
  }

  if (ram.status === LogSeverity.Success) {
    stats.ram = ram.data;
  } else {
    errors.push(`RAM: ${ram.message || 'Statistics unavailable.'}`);
  }

  if (disks.status === LogSeverity.Success) {
    stats.disks = disks.data || [];
  } else {
    errors.push(`Disks: ${disks.message || 'Statistics unavailable.'}`);
  }

  if (errors.length) {
    stats.errors = errors;
  }

  return stats;
};

const refreshSystemDashboard = async (
  article: LfArticleElement,
  options: { reschedule?: boolean } = {},
): Promise<BaseAPIPayload> => {
  const { reschedule = true } = options;
  const payload: BaseAPIPayload = {
    message: '',
    status: LogSeverity.Info,
  };

  SYSTEM_ARTICLE = article;

  try {
    const stats = await gatherSystemStats();
    stats.autoRefreshSeconds = SYSTEM_REFRESH_SECONDS;
    applySystemStats(article, stats);

    if (stats.errors?.length) {
      payload.message = `System statistics updated with warnings: ${stats.errors.join(' | ')}`;
      payload.status = LogSeverity.Warning;
    } else {
      payload.message = 'System statistics updated.';
      payload.status = LogSeverity.Success;
    }
  } catch (error) {
    payload.message = String(error);
    payload.status = LogSeverity.Error;
  }

  if (reschedule) {
    scheduleSystemAutoRefresh();
  }

  return payload;
};

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
          case ControlPanelLabels.RefreshSystemStats:
            invokeAPI(refreshSystemDashboard(slot), ControlPanelLabels.RefreshSystemStats);
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
    const article = element.closest('lf-article') as LfArticleElement;
    if (article) {
      SYSTEM_ARTICLE = article;
    }

    switch (eventType as LfTextfieldEvent) {
      case 'change':
        switch (comp.lfLabel as ControlPanelLabels) {
          case ControlPanelLabels.BackupRetention: {
            const retentionValue = parseInt(value, 10);
            if (!isNaN(retentionValue) && retentionValue >= 0) {
              getLfManager().setBackupRetention(retentionValue);
            }
            break;
          }
          case ControlPanelLabels.SystemAutoRefresh: {
            const trimmed = (value || '').trim();
            const seconds = Number(trimmed);
            if (!trimmed || Number.isNaN(seconds) || seconds <= 0) {
              SYSTEM_REFRESH_SECONDS = 0;
              comp.lfValue = '';
              clearSystemAutoRefresh();
            } else {
              SYSTEM_REFRESH_SECONDS = Number(seconds.toFixed(2));
              comp.lfValue = SYSTEM_REFRESH_SECONDS.toString();
              scheduleSystemAutoRefresh();
            }

            if (article && SYSTEM_LAST_STATS) {
              applySystemStats(article, { ...SYSTEM_LAST_STATS, autoRefreshSeconds: SYSTEM_REFRESH_SECONDS });
            }
            break;
          }
        }
        break;
      case 'ready':
        switch (comp.lfLabel as ControlPanelLabels) {
          case ControlPanelLabels.BackupRetention:
            element.title = 'Maximum number of backups to keep (0 = unlimited)';
            break;
          case ControlPanelLabels.SystemAutoRefresh:
            element.title = 'Auto refresh interval in seconds (0 or empty disables auto refresh)';
            comp.lfValue =
              SYSTEM_REFRESH_SECONDS > 0 ? SYSTEM_REFRESH_SECONDS.toString() : comp.lfValue || '';
            break;
        }
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

        case ControlPanelIds.SystemDashboard:
          node = SECTIONS[ControlPanelIds.SystemDashboard]();
          article = prepArticle(id, node);
          refreshSystemDashboard(article);
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
