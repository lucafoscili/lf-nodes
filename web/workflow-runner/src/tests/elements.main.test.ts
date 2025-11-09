import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { createMainSection } from '../elements/layout.main';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { getLfFramework } from '@lf-widgets/framework';

// Mock the LF framework
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((...args: string[]) => args.join('-')),
    },
  })),
}));

// Mock the section modules
vi.mock('../elements/main.home', () => ({
  createHomeSection: vi.fn(() => ({
    destroy: vi.fn(),
    mount: vi.fn(),
    render: vi.fn(),
  })),
}));

vi.mock('../elements/main.inputs', () => ({
  createInputsSection: vi.fn(() => ({
    destroy: vi.fn(),
    mount: vi.fn(),
    render: vi.fn(),
  })),
}));

vi.mock('../elements/main.outputs', () => ({
  createOutputsSection: vi.fn(() => ({
    destroy: vi.fn(),
    mount: vi.fn(),
    render: vi.fn(),
  })),
}));

vi.mock('../elements/main.results', () => ({
  createResultsSection: vi.fn(() => ({
    destroy: vi.fn(),
    mount: vi.fn(),
    render: vi.fn(),
  })),
}));

// Mock the sections resolver
vi.mock('../app/sections', () => ({
  resolveMainSections: vi.fn(() => ['home']),
}));

describe('Main Element', () => {
  let store: ReturnType<typeof createWorkflowRunnerStore>;
  let mockAppRoot: HTMLElement;
  let mockManager: any;
  let mockHomeController: any;
  let mockInputsController: any;
  let mockOutputsController: any;
  let mockResultsController: any;

  beforeEach(async () => {
    // Setup DOM
    mockAppRoot = document.createElement('div');
    mockAppRoot.id = 'app';
    document.body.appendChild(mockAppRoot);

    // Setup mock controllers
    mockHomeController = {
      destroy: vi.fn(),
      mount: vi.fn(),
      render: vi.fn(),
    };
    mockInputsController = {
      destroy: vi.fn(),
      mount: vi.fn(),
      render: vi.fn(),
    };
    mockOutputsController = {
      destroy: vi.fn(),
      mount: vi.fn(),
      render: vi.fn(),
    };
    mockResultsController = {
      destroy: vi.fn(),
      mount: vi.fn(),
      render: vi.fn(),
    };

    // Update mocks
    const homeMock = vi.mocked(await import('../elements/main.home'));
    const inputsMock = vi.mocked(await import('../elements/main.inputs'));
    const outputsMock = vi.mocked(await import('../elements/main.outputs'));
    const resultsMock = vi.mocked(await import('../elements/main.results'));

    homeMock.createHomeSection.mockReturnValue(mockHomeController);
    inputsMock.createInputsSection.mockReturnValue(mockInputsController);
    outputsMock.createOutputsSection.mockReturnValue(mockOutputsController);
    resultsMock.createResultsSection.mockReturnValue(mockResultsController);

    // Setup store with mock manager
    store = createWorkflowRunnerStore(initState());
    mockManager = {
      getAppRoot: vi.fn(() => mockAppRoot),
      uiRegistry: {
        get: vi.fn(() => null),
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

  describe('createMainSection', () => {
    it('returns a WorkflowSectionController with required methods', async () => {
      const section = createMainSection(store);

      expect(section).toHaveProperty('destroy');
      expect(section).toHaveProperty('mount');
      expect(section).toHaveProperty('render');
      expect(typeof section.destroy).toBe('function');
      expect(typeof section.mount).toBe('function');
      expect(typeof section.render).toBe('function');
    });

    it('creates section controllers for all main sections', async () => {
      const homeMock = vi.mocked(await import('../elements/main.home'));
      const inputsMock = vi.mocked(await import('../elements/main.inputs'));
      const outputsMock = vi.mocked(await import('../elements/main.outputs'));
      const resultsMock = vi.mocked(await import('../elements/main.results'));

      createMainSection(store);

      expect(homeMock.createHomeSection).toHaveBeenCalledWith(store);
      expect(inputsMock.createInputsSection).toHaveBeenCalledWith(store);
      expect(outputsMock.createOutputsSection).toHaveBeenCalledWith(store);
      expect(resultsMock.createResultsSection).toHaveBeenCalledWith(store);
    });
  });

  describe('mount', () => {
    it('mounts the main element to the app root', async () => {
      const section = createMainSection(store);

      section.mount();

      // Should create and append a main element
      const main = mockAppRoot.querySelector('main');
      expect(main).toBeTruthy();
      expect(main?.className).toBe('main-section');
    });

    it('does not mount if already mounted', () => {
      const section = createMainSection(store);

      // Mock that element already exists
      mockManager.uiRegistry.get.mockReturnValue({
        'main-section': document.createElement('main'),
      });

      section.mount();

      // Should not append anything new
      const mains = mockAppRoot.querySelectorAll('main');
      expect(mains.length).toBe(0);
    });

    it('registers the main element in uiRegistry', () => {
      const section = createMainSection(store);

      section.mount();

      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith('main-section', expect.any(Element));
    });
  });

  describe('destroy', () => {
    it('removes main element from uiRegistry', () => {
      const section = createMainSection(store);

      section.destroy();

      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('main-section');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('main-section-home');
    });

    it('destroys all section controllers', () => {
      const section = createMainSection(store);

      section.destroy();

      expect(mockHomeController.destroy).toHaveBeenCalled();
      expect(mockInputsController.destroy).toHaveBeenCalled();
      expect(mockOutputsController.destroy).toHaveBeenCalled();
      expect(mockResultsController.destroy).toHaveBeenCalled();
    });
  });

  describe('render', () => {
    beforeEach(() => {
      // Setup mounted main element
      const mainElement = document.createElement('main');
      mockManager.uiRegistry.get.mockReturnValue({
        'main-section': mainElement,
      });
    });

    it('sets view dataset on main element', () => {
      const section = createMainSection(store);

      // Mock state with specific view
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        view: 'workflow',
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const mainElement = elements['main-section'];

      expect(mainElement.dataset.view).toBe('workflow');
    });

    it('mounts and renders sections for the first time', async () => {
      const section = createMainSection(store);

      // Mock resolved sections
      const sectionsMock = vi.mocked(await import('../app/sections'));
      sectionsMock.resolveMainSections.mockReturnValue(['home', 'inputs']);

      section.render();

      expect(mockHomeController.mount).toHaveBeenCalled();
      expect(mockInputsController.mount).toHaveBeenCalled();
      expect(mockHomeController.render).toHaveBeenCalled();
      expect(mockInputsController.render).toHaveBeenCalled();
    });

    it('destroys sections that are no longer in scope', async () => {
      const section = createMainSection(store);

      // First render with home and inputs
      const sectionsMock = vi.mocked(await import('../app/sections'));
      sectionsMock.resolveMainSections.mockReturnValue(['home', 'inputs']);
      section.render();

      // Second render with only home
      sectionsMock.resolveMainSections.mockReturnValue(['home']);
      section.render();

      expect(mockInputsController.destroy).toHaveBeenCalled();
      expect(mockHomeController.destroy).toHaveBeenCalledTimes(0);
    });

    it('re-mounts sections when workflow changes', async () => {
      const section = createMainSection(store);

      // First render
      const sectionsMock = vi.mocked(await import('../app/sections'));
      sectionsMock.resolveMainSections.mockReturnValue(['home']);
      section.render();

      // Change workflow ID
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        current: { id: 'new-workflow', message: '', status: 'idle' },
      });

      // Second render with same sections
      section.render();

      // Should destroy and re-mount due to workflow change
      expect(mockHomeController.destroy).toHaveBeenCalled();
      expect(mockHomeController.mount).toHaveBeenCalledTimes(2);
    });

    it('accepts custom scope parameter', () => {
      const section = createMainSection(store);

      section.render(['inputs', 'outputs']);

      expect(mockInputsController.mount).toHaveBeenCalled();
      expect(mockOutputsController.mount).toHaveBeenCalled();
      expect(mockHomeController.mount).toHaveBeenCalledTimes(0);
      expect(mockResultsController.mount).toHaveBeenCalledTimes(0);
    });

    it('does nothing if elements are not registered', () => {
      const section = createMainSection(store);

      // Mock missing elements
      mockManager.uiRegistry.get.mockReturnValue(null);

      // Should not throw
      section.render();
    });

    it('tracks last scope and workflow ID', async () => {
      const section = createMainSection(store);

      const sectionsMock = vi.mocked(await import('../app/sections'));
      sectionsMock.resolveMainSections.mockReturnValue(['results']);

      section.render();

      // Should have tracked the scope
      expect(mockResultsController.mount).toHaveBeenCalled();

      // Change workflow and render again
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        current: { id: 'different-workflow', message: '', status: 'idle' },
      });

      sectionsMock.resolveMainSections.mockReturnValue(['results']);
      section.render();

      // Should destroy and re-mount due to workflow change
      expect(mockResultsController.destroy).toHaveBeenCalled();
      expect(mockResultsController.mount).toHaveBeenCalledTimes(2);
    });
  });
});
