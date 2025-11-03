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
          manager.runs.select(id, 'run');
          const selected = manager.runs.get(id);
          const selectedOutputs = JSON.parse(JSON.stringify(selected.outputs)) || null;
          store.getState().mutate.results(selectedOutputs);
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
//#endregion
