import { LfArticleElement } from '@lf-widgets/foundations';
import { SECTIONS } from '../../fixtures/controlPanel';
import { BaseAPIPayload } from '../../types/api/api';
import { LogSeverity } from '../../types/manager/manager';
import {
  ControlPanelIds,
  ControlPanelLabels,
  ControlPanelSystemStats,
} from '../../types/widgets/controlPanel';
import { getApiRoutes, getLfManager } from '../../utils/common';
import { setArticleDataset } from './utils';

let SYSTEM_REFRESH_TIMER: NodeJS.Timeout | null = null;
let SYSTEM_ARTICLE: LfArticleElement | null = null;
let SYSTEM_LAST_STATS: ControlPanelSystemStats | undefined;

//#region clearSystemAutoRefresh
const clearSystemAutoRefresh = () => {
  if (SYSTEM_REFRESH_TIMER) {
    clearTimeout(SYSTEM_REFRESH_TIMER);
    SYSTEM_REFRESH_TIMER = null;
  }
};
//#endregion

//#region buildProgressNode
export const getSystemAutoRefreshSeconds = (): number => {
  try {
    const stored = getLfManager()?.getSystemTimeout?.() ?? 0;
    return typeof stored === 'number' && stored > 0 ? Math.floor(stored) : 0;
  } catch {
    return 0;
  }
};
//#endregion

//#region hasConnectedArticle
const hasConnectedArticle = () => {
  return SYSTEM_ARTICLE && SYSTEM_ARTICLE.isConnected && document.body.contains(SYSTEM_ARTICLE);
};
//#endregion

//#region scheduleSystemAutoRefresh
const scheduleSystemAutoRefresh = () => {
  clearSystemAutoRefresh();
  const seconds = getSystemAutoRefreshSeconds();

  if (seconds <= 0 || !hasConnectedArticle()) {
    return;
  }

  const delay = Math.max(seconds * 1000, 1000);
  SYSTEM_REFRESH_TIMER = setTimeout(() => {
    if (!hasConnectedArticle()) {
      clearSystemAutoRefresh();
      return;
    }

    refreshSystemDashboard(SYSTEM_ARTICLE, { reschedule: false }).finally(() => {
      scheduleSystemAutoRefresh();
    });
  }, delay);
};
//#endregion

//#region setSystemAutoRefreshSeconds
export const setSystemAutoRefreshSeconds = (seconds: number, article?: LfArticleElement | null) => {
  const sanitized =
    typeof seconds === 'number' && Number.isFinite(seconds) && seconds > 0
      ? Math.floor(seconds)
      : 0;

  getLfManager().setSystemTimeout(sanitized);

  if (article) {
    SYSTEM_ARTICLE = article;
  }

  if (sanitized > 0) {
    scheduleSystemAutoRefresh();
  } else {
    clearSystemAutoRefresh();
  }

  const targetArticle = article ?? SYSTEM_ARTICLE;
  if (targetArticle) {
    applySystemStats(targetArticle, SYSTEM_LAST_STATS);
  }

  return sanitized;
};
//#endregion

//#region applySystemStats
export const applySystemStats = (article: LfArticleElement, stats?: ControlPanelSystemStats) => {
  const nextStats = stats ? { ...stats } : SYSTEM_LAST_STATS ? { ...SYSTEM_LAST_STATS } : undefined;

  SYSTEM_LAST_STATS = nextStats;

  setArticleDataset(article, SECTIONS[ControlPanelIds.SystemDashboard](nextStats));

  requestAnimationFrame(() => {
    const textfield = article.querySelector(
      `lf-textfield[lf-label="${ControlPanelLabels.SystemAutoRefresh}"]`,
    ) as HTMLLfTextfieldElement | null;
    if (textfield) {
      const timeout = getSystemAutoRefreshSeconds();
      const value = timeout > 0 ? timeout.toString() : '';
      if (textfield.lfValue !== value) {
        textfield.lfValue = value;
      }
    }
  });
};
//#endregion

//#region gatherSystemStats
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
//#endregion

//#region refreshSystemDashboard
export const refreshSystemDashboard = async (
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
//#endregion

export const getSystemLastStats = () => SYSTEM_LAST_STATS;
