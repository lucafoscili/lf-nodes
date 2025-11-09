import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { createHomeSection } from '../elements/main.home';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { getLfFramework } from '@lf-widgets/framework';
import { MAIN_CLASSES } from '../elements/layout.main';

// Mock the LF framework
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((...args: string[]) => args.join('-')),
    },
  })),
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
        'home-section-masonry',
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
      expect(description?.textContent).toBe('Below a list of the available workflows.');
    });

    it('creates masonry element with correct properties', () => {
      const section = createHomeSection(store);

      section.mount();

      const masonry = mockMainElement.querySelector('lf-masonry') as any;
      expect(masonry).toBeTruthy();
      expect(masonry?.className).toContain('home-section-masonry');
      expect(masonry?.lfShape).toBe('card');
      expect(masonry?.lfStyle).toBeDefined();
    });
  });

  describe('destroy', () => {
    it('removes all home elements from uiRegistry', () => {
      const section = createHomeSection(store);

      section.destroy();

      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-description');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-title-h1');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-masonry');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('home-section-title');
    });
  });

  describe('render', () => {
    beforeEach(() => {
      // Setup mounted elements for render tests
      const homeSection = document.createElement('section');
      const masonry = document.createElement('lf-masonry');
      const h1 = document.createElement('h1');
      const description = document.createElement('p');
      const title = document.createElement('div');

      mockManager.uiRegistry.get.mockReturnValue({
        [MAIN_CLASSES._]: mockMainElement,
        'home-section': homeSection,
        'home-section-masonry': masonry,
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
      const masonry = elements['home-section-masonry'];

      expect(masonry.lfDataset).toBeDefined();
      expect(masonry.lfDataset.nodes).toHaveLength(1);
      expect(masonry.lfDataset.nodes[0].id).toBe('root');
      expect(masonry.lfDataset.nodes[0].value).toBe('Workflows');
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
      const masonry = elements['home-section-masonry'];
      const rootNode = masonry.lfDataset.nodes[0];

      expect(rootNode.cells['wf1']).toBeDefined();
      expect(rootNode.cells['wf1'].lfDataset.nodes[0].cells['1'].value).toBe('My Workflow');
      expect(rootNode.cells['wf1'].lfDataset.nodes[0].cells['2'].value).toBe('Image Processing');
      expect(rootNode.cells['wf1'].lfDataset.nodes[0].cells['3'].value).toBe('Processes images');
      expect(rootNode.cells['wf1'].shape).toBe('card');
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
      const masonry = elements['home-section-masonry'];

      expect(masonry.lfDataset).toBeDefined();
      expect(masonry.lfDataset.nodes).toHaveLength(1);
      expect(masonry.lfDataset.nodes[0].cells).toEqual({});
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
      const masonry = elements['home-section-masonry'];

      expect(masonry.lfDataset).toBeDefined();
      expect(masonry.lfDataset.nodes).toHaveLength(1);
      expect(masonry.lfDataset.nodes[0].cells).toEqual({});
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
