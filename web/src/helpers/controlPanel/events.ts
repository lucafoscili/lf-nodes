import {
  LfArticleElement,
  LfArticleEventPayload,
  LfButtonEvent,
  LfButtonEventPayload,
  LfButtonInterface,
  LfListEventPayload,
  LfTextfieldEvent,
  LfTextfieldEventPayload,
  LfToggleEvent,
  LfToggleEventPayload,
} from '@lf-widgets/foundations';
import { SECTIONS } from '../../fixtures/controlPanel';
import { BaseAPIPayload } from '../../types/api/api';
import { ControlPanelIds, ControlPanelLabels } from '../../types/widgets/controlPanel';
import { getApiRoutes, getLfManager, isButton, isTextfield, isToggle } from '../../utils/common';
import {
  getSystemAutoRefreshSeconds,
  refreshSystemDashboard,
  setSystemAutoRefreshSeconds,
} from './systemDashboard';
import { setArticleDataset } from './utils';

let BUTTON_TIMEOUT: NodeJS.Timeout;
const INTRO_SECTION = ControlPanelIds.GitHub;

//#region withButtonSpinner
const withButtonSpinner = (
  comp: LfButtonInterface,
  promise: Promise<BaseAPIPayload>,
  label: ControlPanelLabels,
) => {
  const onResponse = () => {
    comp.lfIcon = 'check';
    comp.lfLabel = ControlPanelLabels.Done;
    comp.lfShowSpinner = false;
    comp.lfUiState = 'disabled';
  };
  const restore = () => {
    comp.lfLabel = label;
    comp.lfIcon = 'x';
    comp.lfUiState = 'primary';
    BUTTON_TIMEOUT = null;
  };

  requestAnimationFrame(() => (comp.lfShowSpinner = true));
  promise.then(() => {
    requestAnimationFrame(onResponse);

    if (BUTTON_TIMEOUT) {
      clearTimeout(BUTTON_TIMEOUT);
    }

    BUTTON_TIMEOUT = setTimeout(() => requestAnimationFrame(restore), 1000);
  });
};
//#endregion

//#region updateArticleSection
const updateArticleSection = (article: LfArticleElement, id: ControlPanelIds, data?: unknown) => {
  const buildNode = SECTIONS[id];
  if (!buildNode) return;
  setArticleDataset(article, buildNode(data as never));
};
//#endregion

//#region handleButtonClick
const handleButtonClick = (comp: LfButtonInterface, slot: LfArticleElement) => {
  switch (comp.lfLabel) {
    case ControlPanelLabels.Backup:
      withButtonSpinner(comp, getApiRoutes().backup.new('manual'), ControlPanelLabels.Backup);
      getApiRoutes().backup.cleanOld();
      break;
    case ControlPanelLabels.ClearLogs: {
      const { article, dataset } = getLfManager().getDebugDataset();
      if (dataset?.length > 0) {
        dataset.splice(0, dataset.length);
        article.refresh();
      }
      break;
    }
    case ControlPanelLabels.ClearPreviews:
      withButtonSpinner(
        comp,
        getApiRoutes().preview.clearCache(),
        ControlPanelLabels.ClearPreviews,
      );
      break;
    case ControlPanelLabels.DeleteMetadata:
      withButtonSpinner(comp, getApiRoutes().metadata.clear(), ControlPanelLabels.DeleteMetadata);
      break;
    case ControlPanelLabels.DeleteUsage:
      withButtonSpinner(
        comp,
        getApiRoutes().analytics.clear('usage'),
        ControlPanelLabels.DeleteUsage,
      );
      break;
    case ControlPanelLabels.OpenIssue:
      window.open('https://github.com/lucafoscili/comfyui-lf/issues/new', '_blank');
      break;
    case ControlPanelLabels.RefreshPreviewStats:
      getApiRoutes()
        .preview.getStats()
        .then((response) => {
          if (response.status === 'success') {
            updateArticleSection(slot, ControlPanelIds.ExternalPreviews, {
              totalSizeBytes: response.data.total_size_bytes,
              fileCount: response.data.file_count,
            });
          }
        });
      break;
    case ControlPanelLabels.RefreshBackupStats:
      getApiRoutes()
        .backup.getStats()
        .then((response) => {
          if (response.status === 'success') {
            updateArticleSection(slot, ControlPanelIds.Backup, {
              totalSizeBytes: response.data.total_size_bytes,
              fileCount: response.data.file_count,
            });
          }
        });
      break;
    case ControlPanelLabels.RefreshSystemStats:
      withButtonSpinner(comp, refreshSystemDashboard(slot), ControlPanelLabels.RefreshSystemStats);
      break;
    case ControlPanelLabels.Theme:
      getLfManager().getManagers().lfFramework.theme.randomize();
      break;
    default:
      break;
  }
};
//#endregion

//#region setArticleDataset
export const EV_HANDLERS = {
  article: (e: CustomEvent<LfArticleEventPayload>) => {
    const { comp, eventType, originalEvent } = (e as CustomEvent<LfArticleEventPayload>).detail;

    if (eventType === 'lf-event') {
      handleLfEvent(originalEvent, comp.rootElement);
    }
  },
  button: (e: CustomEvent<LfButtonEventPayload>, slot: LfArticleElement) => {
    const { comp, eventType, originalEvent } = e.detail;

    switch (eventType as LfButtonEvent) {
      case 'click':
        handleButtonClick(comp, slot);
        break;
      case 'lf-event': {
        const ogEv = originalEvent as CustomEvent<LfListEventPayload>;
        EV_HANDLERS.list(ogEv);
        break;
      }
    }
  },
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
  textfield: (e: CustomEvent<LfTextfieldEventPayload>) => {
    const { comp, eventType, value } = e.detail;
    const element = comp.rootElement;
    const article = element.closest('lf-article') as LfArticleElement;

    switch (eventType as LfTextfieldEvent) {
      case 'change':
        if (comp.lfLabel === ControlPanelLabels.SystemAutoRefresh) {
          const trimmed = (value || '').trim();
          const parsed = trimmed ? Number(trimmed) : 0;
          const normalized = setSystemAutoRefreshSeconds(parsed, article);
          comp.lfValue = normalized > 0 ? normalized.toString() : '';
        } else if (comp.lfLabel === ControlPanelLabels.BackupRetention) {
          const retentionValue = parseInt(value, 10);
          if (!isNaN(retentionValue) && retentionValue >= 0) {
            getLfManager().setBackupRetention(retentionValue);
          }
        }
        break;
      case 'ready':
        if (comp.lfLabel === ControlPanelLabels.SystemAutoRefresh) {
          element.title = 'Auto refresh interval in seconds (0 or empty disables auto refresh)';
          const currentTimeout = getSystemAutoRefreshSeconds();
          comp.lfValue = currentTimeout > 0 ? currentTimeout.toString() : comp.lfValue || '';
        } else if (comp.lfLabel === ControlPanelLabels.BackupRetention) {
          element.title = 'Maximum number of backups to keep (0 = unlimited)';
        }
        break;
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
        break;
    }
  },
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

export const INTRO_SECTION_ID = INTRO_SECTION;
