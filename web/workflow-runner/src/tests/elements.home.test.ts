import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { createHomeSection } from '../elements/main.home';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { getLfFramework } from '@lf-widgets/framework';
import { MAIN_CLASSES } from '../elements/layout.main';
import { setView } from '../app/store-actions';

// Mock the LF framework
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((...args: string[]) => args.join('-')),
    },
  })),
}));

vi.mock('../app/store-actions', () => ({
  setView: vi.fn(),
}));

describe('Home Element', () => {
  let store: ReturnType<typeof createWorkflowRunnerStore>;
  let mockAppRoot: HTMLElement;
  let mockManager: any;
  let mockMainElement: HTMLElement;

  beforeEach(() => {
    // Setup DOM
    mockAppRoot = document.createElement('div');
    mockAppRoot.id = 'app';
    document.body.appendChild(mockAppRoot);

    // Create mock main element
    mockMainElement = document.createElement('main');
    mockMainElement.className = 'main-section';
    mockAppRoot.appendChild(mockMainElement);

    // Setup store with mock manager
    store = createWorkflowRunnerStore(initState());
    mockManager = {
      getAppRoot: vi.fn(() => mockAppRoot),
      uiRegistry: {
        get: vi.fn(() => ({
          [MAIN_CLASSES._]: mockMainElement,
        })),
        set: vi.fn(),
        remove: vi.fn(),
      },
    };

    // Mock store.getState to return our mock manager
    vi.spyOn(store, 'getState').mockReturnValue({
      ...initState(),
      manager: mockManager,
    });
  });

  afterEach(() => {
    document.body.removeChild(mockAppRoot);
    vi.clearAllMocks();
  });

  describe('createHomeSection', () => {
    it('returns a WorkflowSectionController with required methods', () => {
      const section = createHomeSection(store);

      expect(section).toHaveProperty('destroy');
      expect(section).toHaveProperty('mount');
      expect(section).toHaveProperty('render');
      expect(typeof section.destroy).toBe('function');
      expect(typeof section.mount).toBe('function');
      expect(typeof section.render).toBe('function');
    });
  });

  describe('mount', () => {
    it('mounts the home section to the main element', () => {
      const section = createHomeSection(store);

      section.mount();

      // Should create and prepend a section element to main
      const homeSection = mockMainElement.querySelector('section');
      expect(homeSection).toBeTruthy();
      expect(homeSection?.className).toBe('home-section');

      // Should be the first child (prepended)
      expect(mockMainElement.firstChild).toBe(homeSection);
    });

    it('does not mount if already mounted', () => {
      const section = createHomeSection(store);

      // Mock that element already exists
      mockManager.uiRegistry.get.mockReturnValue({
        [MAIN_CLASSES._]: mockMainElement,
        'home-section': document.createElement('section'),
      });

      section.mount();

      // Should not prepend anything new
      const sections = mockMainElement.querySelectorAll('section');
      expect(sections.length).toBe(0);
    });

    it('registers all home elements in uiRegistry', () => {
      const section = createHomeSection(store);

      section.mount();

      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith('home-section', expect.any(Element));
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'home-section-description',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'home-section-title-h1',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'home-section-block-masonry',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'home-section-block-rail',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'home-section-catalogue',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'home-section-orchestra-masonry',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'home-section-orchestra-rail',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'home-section-title',
        expect.any(Element),
      );
    });

    it('creates title with correct content', () => {
      const section = createHomeSection(store);

      section.mount();

      const h1 = mockMainElement.querySelector('h1');
      expect(h1).toBeTruthy();
      expect(h1?.className).toContain('home-section-title-h1');
      expect(h1?.textContent).toBe('Workflow Runner');
    });

    it('creates description with correct content', () => {
      const section = createHomeSection(store);

      section.mount();

      const description = mockMainElement.querySelector('p');
      expect(description).toBeTruthy();
      expect(description?.className).toContain('home-section-description');
      expect(description?.textContent).toBe(
        'Choose a focused block or a ready-made orchestra.',
      );
    });

    it('creates distinct orchestra and block rails with canonical attributes', () => {
      const section = createHomeSection(store);

      section.mount();

      const rails = mockMainElement.querySelectorAll('.home-section-rail');
      const masonries = mockMainElement.querySelectorAll('lf-masonry') as NodeListOf<any>;
      expect(rails).toHaveLength(2);
      expect(rails[0].getAttribute('data-workflow-kind')).toBe('orchestra');
      expect(rails[1].getAttribute('data-workflow-kind')).toBe('block');
      expect(masonries).toHaveLength(2);
      expect(masonries[0].className).toContain('home-section-masonry');
      expect(masonries[0].className).toContain('home-section-orchestra-masonry');
      expect(masonries[1].className).toContain('home-section-block-masonry');
      expect(masonries[0].lfShape).toBe('card');
      expect(masonries[1].lfStyle).toBeDefined();
    });

    it('routes clicks from either modified home masonry class', () => {
      const selectWorkflow = vi.fn();
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        mutate: {
          ...initState().mutate,
          workflow: selectWorkflow,
        },
      });
      createHomeSection(store).mount();

      const card = document.createElement('lf-card') as any;
      card.lfDataset = { nodes: [{ id: 'identity_cleanup_restage' }] };
      const masonry = mockMainElement.querySelector(
        '.home-section-orchestra-masonry',
      ) as HTMLElement;
      masonry.dispatchEvent(
        new CustomEvent('lf-masonry-event', {
          detail: {
            comp: { rootElement: masonry },
            originalEvent: {
              detail: {
                comp: { lfDataset: card.lfDataset, rootElement: card },
                eventType: 'click',
              },
            },
          },
        }),
      );

      expect(selectWorkflow).toHaveBeenCalledWith('identity_cleanup_restage');
      expect(vi.mocked(setView)).toHaveBeenCalledWith(store, 'workflow');
    });
  });

  describe('destroy', () => {
    it('removes all home elements from uiRegistry', () => {
      const section = createHomeSection(store);

      section.destroy();

      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-block-masonry');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-block-rail');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-catalogue');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-description');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-title-h1');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith(
        'home-section-orchestra-masonry',
      );
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-orchestra-rail');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-title');
    });
  });

  describe('render', () => {
    beforeEach(() => {
      // Setup mounted elements for render tests
      const homeSection = document.createElement('section');
      const catalogue = document.createElement('div');
      const orchestraMasonry = document.createElement('lf-masonry');
      const orchestraRail = document.createElement('section');
      const orchestraCount = document.createElement('span');
      orchestraCount.dataset.railCount = 'orchestra';
      orchestraRail.appendChild(orchestraCount);
      const blockMasonry = document.createElement('lf-masonry');
      const blockRail = document.createElement('section');
      const blockCount = document.createElement('span');
      blockCount.dataset.railCount = 'block';
      blockRail.appendChild(blockCount);
      const h1 = document.createElement('h1');
      const description = document.createElement('p');
      const title = document.createElement('div');

      mockManager.uiRegistry.get.mockReturnValue({
        [MAIN_CLASSES._]: mockMainElement,
        'home-section-block-masonry': blockMasonry,
        'home-section-block-rail': blockRail,
        'home-section': homeSection,
        'home-section-catalogue': catalogue,
        'home-section-orchestra-masonry': orchestraMasonry,
        'home-section-orchestra-rail': orchestraRail,
        'home-section-title-h1': h1,
        'home-section-description': description,
        'home-section-title': title,
      });
    });

    it('updates masonry dataset with workflow data', () => {
      const section = createHomeSection(store);

      // Mock workflows in store
      const mockWorkflows = {
        nodes: [
          {
            id: 'wf1',
            value: 'Test Workflow',
            category: 'Test Category',
            description: 'A test workflow',
            children: [undefined, undefined] as [undefined, undefined],
          },
        ],
      };

      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        workflows: mockWorkflows,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const masonry = elements['home-section-block-masonry'];

      expect(masonry.lfDataset).toBeDefined();
      expect(masonry.lfDataset.nodes).toHaveLength(1);
      expect(masonry.lfDataset.nodes[0].id).toBe('root');
      expect(masonry.lfDataset.nodes[0].value).toBe('Blocks');
      expect(elements['home-section-block-rail'].hidden).toBe(false);
      expect(elements['home-section-orchestra-rail'].hidden).toBe(true);
    });

    it('creates dataset with workflow cells', () => {
      const section = createHomeSection(store);

      const mockWorkflows = {
        nodes: [
          {
            id: 'wf1',
            value: 'My Workflow',
            category: 'Image Processing',
            description: 'Processes images',
            children: [undefined, undefined] as [undefined, undefined],
          },
        ],
      };

      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        workflows: mockWorkflows,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const masonry = elements['home-section-block-masonry'];
      const rootNode = masonry.lfDataset.nodes[0];

      expect(rootNode.cells['wf1']).toBeDefined();
      expect(rootNode.cells['wf1'].lfDataset.nodes[0].cells['1'].value).toBe('My Workflow');
      expect(rootNode.cells['wf1'].lfDataset.nodes[0].cells['2'].value).toBe('Image Processing');
      expect(rootNode.cells['wf1'].lfDataset.nodes[0].cells['3'].value).toBe('Processes images');
      expect(rootNode.cells['wf1'].shape).toBe('card');
    });

    it('partitions sequences into the orchestra rail and shows their declared stage trail', () => {
      const section = createHomeSection(store);
      const identity = {
        id: 'krea2_identity_edit',
        value: 'Identity Edit',
        category: 'Krea 2',
        description: 'Edit one identity.',
        children: [undefined, undefined] as [undefined, undefined],
      };
      const restage = {
        id: 'krea2_character_restage',
        value: 'Character Restage',
        category: 'Krea 2',
        description: 'Restage one character.',
        children: [undefined, undefined] as [undefined, undefined],
      };
      const sequence = {
        id: 'identity-monument',
        value: 'Identity Cleanup and Restage',
        category: 'Orchestration',
        description: 'Cleans one identity, then restages the kept result.',
        children: [undefined, undefined] as [undefined, undefined],
        kind: 'orchestra' as const,
        downloadable: false,
        stages: [
          { id: 'identity', workflowId: 'krea2_identity_edit' },
          { id: 'restage', workflowId: 'krea2_character_restage' },
        ],
      };

      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        workflows: { nodes: [identity, restage, sequence] },
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const orchestraRoot = elements['home-section-orchestra-masonry'].lfDataset.nodes[0];
      const blockRoot = elements['home-section-block-masonry'].lfDataset.nodes[0];
      const card = orchestraRoot.cells[sequence.id];
      expect(card.shape).toBe('card');
      expect(card.htmlProps.dataset.workflowKind).toBe('orchestra');
      expect(card.lfUiState).toBe('secondary');
      expect(card.lfStyle).toContain('border-inline-start');
      expect(card.lfDataset.nodes[0].cells['1'].value).toBe(sequence.value);
      expect(card.lfDataset.nodes[0].cells['2'].value).toBe('ORCHESTRA · 2 BLOCKS');
      expect(card.lfDataset.nodes[0].cells['3'].value).toBe(
        `Identity Edit → Character Restage\n${sequence.description}`,
      );
      expect(Object.keys(orchestraRoot.cells)).toEqual([sequence.id]);
      expect(Object.keys(blockRoot.cells)).toEqual([identity.id, restage.id]);
      expect(elements['home-section-orchestra-rail'].hidden).toBe(false);
      expect(elements['home-section-block-rail'].hidden).toBe(false);
      expect(
        elements['home-section-orchestra-rail'].querySelector('[data-rail-count="orchestra"]')
          .textContent,
      ).toBe('1');
      expect(
        elements['home-section-block-rail'].querySelector('[data-rail-count="block"]')
          .textContent,
      ).toBe('2');
    });

    it('names the roles of repeated blocks in an orchestra trail', () => {
      const section = createHomeSection(store);
      const directedView = {
        id: 'minimax_h3_directed_view',
        value: 'Directed View',
        category: 'MiniMax H3',
        description: 'Generate one directed character view.',
        children: [undefined, undefined] as [undefined, undefined],
      };
      const assembler = {
        id: 'assemble_cardinal_turnaround',
        value: 'Assemble Cardinal Turnaround',
        category: 'Image Processing',
        description: 'Assemble four views.',
        children: [undefined, undefined] as [undefined, undefined],
      };
      const orchestra = {
        id: 'character-turnaround',
        value: 'Character Turnaround',
        category: 'Orchestration',
        description: 'Build the stable cardinal sheet.',
        children: [undefined, undefined] as [undefined, undefined],
        kind: 'orchestra' as const,
        stages: [
          { id: 'subject_right', workflowId: directedView.id },
          { id: 'back', workflowId: directedView.id },
          { id: 'subject_left', workflowId: directedView.id },
          { id: 'sheet', workflowId: assembler.id },
        ],
      };

      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        workflows: { nodes: [directedView, assembler, orchestra] },
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const orchestraRoot = elements['home-section-orchestra-masonry'].lfDataset.nodes[0];
      expect(orchestraRoot.cells[orchestra.id].lfDataset.nodes[0].cells['3'].value).toBe(
        `Subject Right · Directed View → Back · Directed View → Subject Left · Directed View → Assemble Cardinal Turnaround\n${orchestra.description}`,
      );
    });

    it('normalizes legacy kinds while avoiding a bogus zero-block label', () => {
      const section = createHomeSection(store);
      const legacy = {
        id: 'legacy',
        value: 'Legacy Workflow',
        category: 'Custom',
        description: 'Still a block.',
        kind: 'workflow' as const,
        children: [undefined, undefined] as [undefined, undefined],
      };
      const malformedSequence = {
        id: 'empty-sequence',
        value: 'Empty Orchestra',
        category: 'Orchestration',
        description: 'Malformed test declaration.',
        kind: 'sequence' as const,
        children: [undefined, undefined] as [undefined, undefined],
      };
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        workflows: { nodes: [legacy, malformedSequence] },
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const blockRoot = elements['home-section-block-masonry'].lfDataset.nodes[0];
      const orchestraRoot = elements['home-section-orchestra-masonry'].lfDataset.nodes[0];
      expect(blockRoot.cells.legacy).toBeDefined();
      expect(blockRoot.cells.legacy.htmlProps.dataset.workflowKind).toBe('block');
      expect(orchestraRoot.cells['empty-sequence'].htmlProps.dataset.workflowKind).toBe(
        'orchestra',
      );
      expect(orchestraRoot.cells['empty-sequence'].lfDataset.nodes[0].cells['2'].value).toBe(
        'ORCHESTRA',
      );
    });

    it('handles empty workflows gracefully', () => {
      const section = createHomeSection(store);

      const mockWorkflows = {
        nodes: [],
      };

      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        workflows: mockWorkflows,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      for (const key of ['home-section-block-masonry', 'home-section-orchestra-masonry']) {
        const masonry = elements[key];
        expect(masonry.lfDataset).toBeDefined();
        expect(masonry.lfDataset.nodes).toHaveLength(1);
        expect(masonry.lfDataset.nodes[0].cells).toEqual({});
      }
      expect(elements['home-section-block-rail'].hidden).toBe(true);
      expect(elements['home-section-orchestra-rail'].hidden).toBe(true);
    });

    it('handles undefined workflows gracefully', () => {
      const section = createHomeSection(store);

      const mockWorkflows = {
        nodes: undefined,
      };

      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        workflows: mockWorkflows,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      for (const key of ['home-section-block-masonry', 'home-section-orchestra-masonry']) {
        const masonry = elements[key];
        expect(masonry.lfDataset).toBeDefined();
        expect(masonry.lfDataset.nodes).toHaveLength(1);
        expect(masonry.lfDataset.nodes[0].cells).toEqual({});
      }
    });

    it('does nothing if elements are not registered', () => {
      const section = createHomeSection(store);

      // Mock missing elements
      mockManager.uiRegistry.get.mockReturnValue(null);

      // Should not throw
      section.render();
    });
  });
});
