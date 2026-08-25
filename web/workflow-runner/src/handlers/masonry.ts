import { LfCardEventPayload, LfMasonryEventPayload } from '@lf-widgets/foundations/dist';
import { setView } from '../app/store-actions';
import { HOME_CLASSES } from '../elements/main.home';
import { OUTPUTS_CLASSES } from '../elements/main.outputs';
import { WorkflowStore } from '../types/state';

//#region Masonry handlers
export const masonryHandler = (e: CustomEvent<LfMasonryEventPayload>, store: WorkflowStore) => {
  const { comp, originalEvent } = e.detail;
  const ogEvent = originalEvent as CustomEvent<LfCardEventPayload>;

  const { manager, mutate } = store.getState();

  // Outputs
  if (comp.rootElement.className === OUTPUTS_CLASSES.masonry) {
    switch (ogEvent?.detail?.eventType) {
      case 'click':
        const card = ogEvent.detail.comp;
        const node = card.lfDataset?.nodes?.[0];
        const isValidCard = node?.id && card.rootElement.tagName.toLowerCase() === 'lf-card';
        if (isValidCard) {
          const { id } = node;
          if (manager.runs.get(id) && manager.runs.selected()?.runId !== id) {
            manager.runs.select(id, 'run');
          }
        }

        break;
      default:
        return;
    }
  }

  // Home
  if (comp.rootElement.className === HOME_CLASSES.masonry) {
    switch (ogEvent?.detail?.eventType) {
      case 'click':
        const card = ogEvent.detail.comp;
        const node = card.lfDataset?.nodes?.[0];
        const isValidCard = node?.id && card.rootElement.tagName.toLowerCase() === 'lf-card';
        if (isValidCard) {
          const { id } = node;
          mutate.workflow(id);
          setView(store, 'workflow');
        }

        break;
      default:
        return;
    }
  }
};

/**
 * Native-click fallback for result cards.
 *
 * LFW normally forwards a card click through `lf-masonry-event`. Some browser /
 * custom-element upgrade paths do not forward that event even though the
 * composed native click still reaches the masonry host. Keep the result detail
 * reachable without replacing the normal LFW path, and de-duplicate when both
 * paths fire.
 */
export const masonryClickFallback = (e: MouseEvent, store: WorkflowStore) => {
  const card = e
    .composedPath()
    .find(
      (entry): entry is HTMLLfCardElement =>
        entry instanceof Element && entry.tagName.toLowerCase() === 'lf-card',
    );
  const node = card?.lfDataset?.nodes?.[0];
  const runId = typeof node?.id === 'string' ? node.id : '';
  if (!runId) {
    return;
  }

  const { manager } = store.getState();
  if (manager.runs.get(runId) && manager.runs.selected()?.runId !== runId) {
    manager.runs.select(runId, 'run');
  }
};
//#endregion
