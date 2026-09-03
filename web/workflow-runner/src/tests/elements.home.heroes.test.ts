import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createHomeSection, HOME_CARD_OPEN_ID, HOME_CLASSES } from '../elements/main.home';
import { MAIN_CLASSES } from '../elements/layout.main';
import { initState } from '../app/state';
import { setView } from '../app/store-actions';
import { WorkflowAPIItem } from '../types/api';
import { WorkflowStore } from '../types/state';

vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: () => ({ theme: { bemClass: (...args: string[]) => args.join('-') } }),
}));
vi.mock('../app/store-actions', () => ({ setView: vi.fn() }));

const workflow = (id: string, overrides: Partial<WorkflowAPIItem> = {}): WorkflowAPIItem => ({
  id,
  value: `Workflow ${id}`,
  kind: 'block',
  category: 'Image tools',
  description: 'Legacy full description.',
  children: [],
  card: {
    summary: 'A concise useful summary.',
    hero: { asset: `${id}.webp`, alt: `Actual output from ${id}.` },
  },
  ...overrides,
});

describe('home catalogue heroes', () => {
  let main: HTMLElement;
  let registry: Record<string, any>;
  let state: any;
  let store: WorkflowStore;
  let section: ReturnType<typeof createHomeSection>;

  beforeEach(() => {
    main = document.createElement('main');
    document.body.append(main);
    registry = { [MAIN_CLASSES._]: main };
    state = {
      ...initState(),
      manager: {
        uiRegistry: {
          get: () => registry,
          set: (name: string, element: Element) => { registry[name] = element; },
          remove: (name: string) => { delete registry[name]; },
        },
      },
      mutate: { ...initState().mutate, workflow: vi.fn() },
      workflows: { nodes: [] },
    };
    store = { getState: () => state } as WorkflowStore;
    section = createHomeSection(store);
    section.mount();
  });

  afterEach(() => {
    main.remove();
    vi.clearAllMocks();
  });

  const cardCell = (masonry: any, id: string) => masonry.lfDataset.nodes[0].cells[id];
  const project = (nodes: WorkflowAPIItem[], kind = 'block') => {
    state.workflows = { nodes };
    section.render();
    return registry[kind === 'block' ? HOME_CLASSES.blockMasonry : HOME_CLASSES.orchestraMasonry];
  };
  const cardComponent = (masonry: any, id: string) => ({
    rootElement: document.createElement('lf-card'),
    lfDataset: cardCell(masonry, id).lfDataset,
  });
  const forwardCardEvent = (masonry: any, card: any, eventType: string, originalEvent?: any) => {
    masonry.rootElement = masonry;
    masonry.dispatchEvent(new CustomEvent('lf-masonry-event', {
      detail: {
        comp: masonry,
        eventType: 'lf-event',
        originalEvent: new CustomEvent('lf-card-event', {
          detail: { comp: card, eventType, originalEvent },
        }),
      },
    }));
  };
  const imageEvent = (url: string, eventType = 'error') => new CustomEvent('lf-image-event', {
    detail: {
      comp: { rootElement: document.createElement('lf-image'), lfValue: url },
      eventType,
      originalEvent: new Event(eventType),
    },
  });

  it.each([
    ['block', 'portrait', 'Actual portrait output.'],
    ['orchestra', 'cleanup-before-after', 'Before: cluttered portrait. After: clean restaged portrait.'],
  ])('projects a %s hero as one image with accessible copy', (kind, id, alt) => {
    const node = workflow(id, {
      kind: kind as 'block' | 'orchestra',
      stages: kind === 'orchestra' ? [{ id: 'cleanup', workflowId: 'clean' }] : undefined,
      card: { summary: 'One-line result summary.', hero: { asset: `${id}.webp`, alt } },
    });
    const masonry = project([node], kind);
    const cell = cardCell(masonry, id);
    const inner = cell.lfDataset.nodes[0].cells;

    expect(inner['1'].value).toBe(node.value);
    expect(inner['2'].value).toBe(kind === 'block' ? 'Image tools' : 'ORCHESTRA · 1 BLOCK');
    expect(inner['3'].value).toBe('One-line result summary.');
    expect(Object.values(inner).filter((value: any) => value.shape === 'image')).toHaveLength(1);
    expect(inner.hero).toMatchObject({ shape: 'image', lfHtmlAttributes: { alt } });
    expect(inner.hero.value).toContain(`/workflow-runner/heroes/${id}.webp`);
    expect(inner.open).toMatchObject({
      shape: 'button', lfLabel: 'Open', lfAriaLabel: `Open ${node.value}`,
      htmlProps: { id: HOME_CARD_OPEN_ID },
    });
    expect(cell.lfSizeY).toBe('auto');
    expect(cell.lfStyle).toContain('aspect-ratio: 16 / 9');
    expect(cell.lfStyle).toContain('--lf-image-object-fit: contain');
    expect(cell.lfStyle).toContain(':host .material-layout .text-content__description { white-space: nowrap');
    expect(cell.lfStyle).toContain(':host .material-layout__actions-section { position: static');
    expect(cell.lfStyle.includes('height: 100%')).toBe(false);
    if (kind === 'orchestra') {
      expect(cell.lfUiState).toBe('secondary');
      expect(cell.lfStyle).toContain('border-inline-start: 4px double');
    }
    const rail = registry[kind === 'block' ? HOME_CLASSES.blockRail : HOME_CLASSES.orchestraRail];
    expect(rail.querySelector('[data-rail-count]').textContent).toBe('1');
    expect(state.workflows.nodes[0]).toEqual(node);
  });

  it('keeps legacy descriptions and gives every card a native Open action', () => {
    const masonry = project([
      workflow('legacy', { card: undefined }),
      workflow('summary', { card: { summary: 'A text-only summary.' } }),
      workflow('unsafe', { card: { summary: 'A safe summary.', hero: { asset: '../secret.png', alt: 'Output' } } }),
    ]);
    const legacy = cardCell(masonry, 'legacy');
    expect(legacy.lfDataset.nodes[0].cells).toEqual({
      '1': { value: 'Workflow legacy' }, '2': { value: 'Image tools' },
      '3': { value: 'Legacy full description.' },
      open: {
        shape: 'button',
        value: '',
        htmlProps: { id: HOME_CARD_OPEN_ID },
        lfLabel: 'Open',
        lfAriaLabel: 'Open Workflow legacy',
        lfStyling: 'flat',
        lfUiSize: 'small',
        lfUiState: 'primary',
      },
    });
    expect(legacy.lfStyle).toBeUndefined();
    for (const id of ['summary', 'unsafe']) {
      const cells = cardCell(masonry, id).lfDataset.nodes[0].cells;
      expect(cells.hero).toBeUndefined();
      expect(cells.open.lfLabel).toBe('Open');
      expect(cells['3'].value).toContain('summary.');
    }
  });

  it('recovers a broken image through LF image → card → masonry events and stays recovered', () => {
    const nodes = [workflow('broken'), workflow('healthy')];
    const masonry = project(nodes);
    const card = cardComponent(masonry, 'broken');
    const heroUrl = card.lfDataset.nodes[0].cells.hero.value;
    const healthy = cardCell(masonry, 'healthy');

    forwardCardEvent(masonry, card, 'lf-event', imageEvent(heroUrl));

    expect(card.lfDataset.nodes[0].cells.hero).toBeUndefined();
    expect(cardCell(masonry, 'broken').lfDataset.nodes[0].cells.hero).toBeUndefined();
    expect(cardCell(masonry, 'broken').lfDataset.nodes[0].cells['3'].value).toBe(nodes[0].card.summary);
    expect(cardCell(masonry, 'healthy')).toBe(healthy);
    expect(state.mutate.workflow).toHaveBeenCalledTimes(0);
    expect(state.workflows.nodes[0].card.hero).toEqual(nodes[0].card.hero);

    section.render();
    expect(cardCell(masonry, 'broken').lfDataset.nodes[0].cells.hero).toBeUndefined();
    expect(cardCell(masonry, 'healthy').lfDataset.nodes[0].cells.hero).toBeDefined();
    forwardCardEvent(masonry, card, 'click');
    expect(state.mutate.workflow).toHaveBeenCalledExactlyOnceWith('broken');
  });

  it('ignores image load events and stale or unrelated image errors', () => {
    const masonry = project([workflow('portrait')]);
    const card = cardComponent(masonry, 'portrait');
    const before = masonry.lfDataset;
    const url = card.lfDataset.nodes[0].cells.hero.value;
    forwardCardEvent(masonry, card, 'lf-event', imageEvent(url, 'load'));
    forwardCardEvent(masonry, card, 'lf-event', imageEvent(`${url}-stale`));
    forwardCardEvent(masonry, card, 'lf-event', new Event('error'));
    expect(masonry.lfDataset).toBe(before);
    expect(state.mutate.workflow).toHaveBeenCalledTimes(0);
  });

  it('opens once through the native LF button path and consumes the duplicate card click', () => {
    const masonry = project([workflow('legacy', { card: undefined })]);
    const card = cardComponent(masonry, 'legacy');
    const button = document.createElement('lf-button');
    button.id = HOME_CARD_OPEN_ID;
    const nativeClick = new MouseEvent('click', { bubbles: true, composed: true });
    const stop = vi.spyOn(nativeClick, 'stopPropagation');
    forwardCardEvent(masonry, card, 'lf-event', new CustomEvent('lf-button-event', {
      detail: { comp: { rootElement: button }, eventType: 'click', originalEvent: nativeClick },
    }));
    expect(stop).toHaveBeenCalledOnce();
    expect(state.mutate.workflow).toHaveBeenCalledExactlyOnceWith('legacy');
    expect(setView).toHaveBeenCalledExactlyOnceWith(store, 'workflow');
  });

  it('leaves hero clicks to the existing card click path', () => {
    const masonry = project([workflow('portrait')]);
    const card = cardComponent(masonry, 'portrait');
    forwardCardEvent(masonry, card, 'lf-event', imageEvent(card.lfDataset.nodes[0].cells.hero.value, 'click'));
    expect(state.mutate.workflow).toHaveBeenCalledTimes(0);
    forwardCardEvent(masonry, card, 'click');
    expect(state.mutate.workflow).toHaveBeenCalledExactlyOnceWith('portrait');
  });
});
