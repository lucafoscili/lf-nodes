import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { MAIN_CLASSES } from '../elements/layout.main';
import { createHomeSection, HOME_CLASSES } from '../elements/main.home';
import { WorkflowAPIItem } from '../types/api';
import { WorkflowManager } from '../types/manager';

vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: () => ({ theme: { bemClass: (...args: string[]) => args.join('-') } }),
}));

const workflow = (id: string, origin: 'shipped' | 'custom'): WorkflowAPIItem => ({
  id,
  value: `Workflow ${id}`,
  kind: 'block',
  origin,
  collection: 'Local tools',
  category: 'Image tools',
  description: 'Original description.',
  children: [],
});

describe('home catalogue render stability', () => {
  let main: HTMLElement;
  let registry: Record<string, HTMLElement>;
  let store: ReturnType<typeof createWorkflowRunnerStore>;
  let section: ReturnType<typeof createHomeSection>;
  let unsubscribe: () => void;

  beforeEach(() => {
    main = document.createElement('main');
    document.body.append(main);
    registry = { [MAIN_CLASSES._]: main };
    store = createWorkflowRunnerStore({
      ...initState(),
      manager: {
        uiRegistry: {
          get: () => registry,
          set: (name: string, element: HTMLElement) => { registry[name] = element; },
          remove: (name: string) => {
            registry[name]?.remove();
            delete registry[name];
          },
        },
      } as unknown as WorkflowManager,
      workflows: { nodes: [workflow('shipped', 'shipped'), workflow('custom', 'custom')] },
    });
    section = createHomeSection(store);
    section.mount();
    section.render();
    unsubscribe = store.subscribe(() => section.render());
  });

  afterEach(() => {
    unsubscribe();
    section.destroy();
    main.remove();
  });

  const masonries = () => Array.from(main.querySelectorAll('lf-masonry'));
  const customMasonry = () => registry[HOME_CLASSES.customCatalogue]
    .querySelector<HTMLLfMasonryElement>('[data-workflow-kind="block"] lf-masonry');

  it('preserves custom DOM and all masonry datasets across unrelated queue mutations', () => {
    const catalogue = registry[HOME_CLASSES.customCatalogue];
    const group = catalogue.firstElementChild;
    const before = masonries();
    const datasets = before.map((masonry) => masonry.lfDataset);
    const replaceChildren = vi.spyOn(catalogue, 'replaceChildren');
    let workflows = store.getState().workflows;

    for (const count of [1, 2, 1, 0, 1, 0]) {
      store.getState().mutate.queuedJobs(count);

      expect(store.getState().workflows === workflows).toBe(false);
      workflows = store.getState().workflows;
      expect(catalogue.firstElementChild).toBe(group);
      const after = masonries();
      expect(after).toHaveLength(before.length);
      after.forEach((masonry, index) => {
        expect(masonry).toBe(before[index]);
        expect(masonry.lfDataset).toBe(datasets[index]);
      });
    }
    expect(replaceChildren).toHaveBeenCalledTimes(0);
  });

  it('updates same-count metadata edits and ownership navigation', () => {
    const before = customMasonry();
    const nodes = store.getState().workflows.nodes.map((node) => ({
      ...node,
      value: `Updated ${node.id}`,
      collection: 'Renamed collection',
      description: 'Updated description.',
    }));
    store.getState().mutate.workflows({ nodes });

    const custom = customMasonry();
    expect(custom === before).toBe(false);
    const customCell = custom.lfDataset.nodes[0].cells.custom;
    if (customCell.shape !== 'card') {
      throw new Error('Expected custom workflow card');
    }
    expect(customCell.lfDataset.nodes[0].cells).toMatchObject({
      '1': { value: 'Updated custom' },
      '3': { value: 'Updated description.' },
    });
    expect(registry[HOME_CLASSES.customCatalogue].querySelector('h3').textContent)
      .toBe('Renamed collection');
    const shipped = registry[HOME_CLASSES.blockMasonry] as HTMLLfMasonryElement;
    const shippedCell = shipped.lfDataset.nodes[0].cells.shipped;
    if (shippedCell.shape !== 'card') {
      throw new Error('Expected shipped workflow card');
    }
    expect(shippedCell.lfDataset.nodes[0].cells['1'].value)
      .toBe('Updated shipped');

    store.getState().mutate.workflows({ nodes: [] });
    expect(registry[HOME_CLASSES.customCatalogue].childElementCount).toBe(0);
    expect(registry[HOME_CLASSES.custom].hidden).toBe(true);
    expect(registry[HOME_CLASSES.shipped].hidden).toBe(true);
    expect(registry[HOME_CLASSES.jumpNavigation].hidden).toBe(true);
  });

  it('renders unchanged workflows after destroy and remount', () => {
    const before = customMasonry();
    section.destroy();
    section.render();
    section.mount();
    section.render();

    const custom = customMasonry();
    expect(custom === before).toBe(false);
    expect(custom.lfDataset.nodes[0].cells.custom).toBeDefined();
    const shipped = registry[HOME_CLASSES.blockMasonry] as HTMLLfMasonryElement;
    expect(shipped.lfDataset.nodes[0].cells.shipped).toBeDefined();
    expect(registry[HOME_CLASSES.jumpCustom].hidden).toBe(false);
    expect(registry[HOME_CLASSES.jumpShipped].hidden).toBe(false);
  });
});
