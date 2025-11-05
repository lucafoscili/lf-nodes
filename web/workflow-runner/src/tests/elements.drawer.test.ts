import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { createDrawerSection } from '../elements/layout.drawer';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { getLfFramework } from '@lf-widgets/framework';

// Mock the LF framework
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((...args: string[]) => args.join('-')),
      get: {
        icon: vi.fn((iconName: string) => {
          const iconMap: Record<string, string> = {
            imageInPicture: 'image-in-picture',
            bug: 'bug',
            brandGithub: 'brand-github',
          };
          return iconMap[iconName] || 'test-icon';
        }),
        icons: vi.fn(() => ({
          article: 'article',
          listTree: 'list-tree',
          alertTriangle: 'alert-triangle',
          codeCircle2: 'code-circle-2',
          photo: 'photo',
          json: 'json',
          robot: 'robot',
          wand: 'wand',
          imageInPicture: 'image-in-picture',
          bug: 'bug',
          brandGithub: 'brand-github',
        })),
      },
    },
  })),
}));

describe('Drawer Element', () => {
  let store: ReturnType<typeof createWorkflowRunnerStore>;
  let mockAppRoot: HTMLElement;
  let mockManager: any;

  beforeEach(() => {
    // Setup DOM
    mockAppRoot = document.createElement('div');
    mockAppRoot.id = 'app';
    document.body.appendChild(mockAppRoot);

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

  describe('createDrawerSection', () => {
    it('returns a WorkflowSectionController with required methods', () => {
      const section = createDrawerSection(store);

      expect(section).toHaveProperty('destroy');
      expect(section).toHaveProperty('mount');
      expect(section).toHaveProperty('render');
      expect(typeof section.destroy).toBe('function');
      expect(typeof section.mount).toBe('function');
      expect(typeof section.render).toBe('function');
    });
  });

  describe('mount', () => {
    it('mounts the drawer to the app root', () => {
      const section = createDrawerSection(store);

      section.mount();

      // Should create and append a drawer element
      const drawer = mockAppRoot.querySelector('lf-drawer');
      expect(drawer).toBeTruthy();
      expect(drawer?.className).toBe('drawer-section');
      expect((drawer as any)?.lfDisplay).toBe('slide');

      // Should create container, tree, and footer
      const container = drawer?.querySelector('[slot="content"]');
      expect(container).toBeTruthy();
      expect(container?.className).toContain('drawer-section-container');

      const tree = container?.querySelector('.drawer-section-tree');
      expect(tree).toBeTruthy();

      const footer = container?.querySelector('.drawer-section-footer');
      expect(footer).toBeTruthy();
    });

    it('does not mount if already mounted', () => {
      const section = createDrawerSection(store);

      // Mock that element already exists
      mockManager.uiRegistry.get.mockReturnValue({
        'drawer-section': document.createElement('lf-drawer'),
      });

      section.mount();

      // Should not append anything new
      const drawers = mockAppRoot.querySelectorAll('lf-drawer');
      expect(drawers.length).toBe(0);
    });

    it('registers all drawer elements in uiRegistry', () => {
      const section = createDrawerSection(store);

      section.mount();

      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'drawer-section',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'drawer-section-button-comfyui',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'drawer-section-button-debug',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'drawer-section-footer',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'drawer-section-button-github',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'drawer-section-container',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'drawer-section-tree',
        expect.any(Element),
      );
    });

    it('creates footer buttons with correct properties', () => {
      const section = createDrawerSection(store);

      section.mount();

      const footer = mockAppRoot.querySelector('.drawer-section-footer');
      expect(footer).toBeTruthy();

      const githubButton = footer?.querySelector('.drawer-section-button-github') as any;
      expect(githubButton).toBeTruthy();
      expect(githubButton.lfIcon).toBe('brand-github');
      expect(githubButton.lfAriaLabel).toBe('Open GitHub repository');
      expect(githubButton.title).toBe('Open GitHub repository');

      const comfyUiButton = footer?.querySelector('.drawer-section-button-comfyui') as any;
      expect(comfyUiButton).toBeTruthy();
      expect(comfyUiButton.lfIcon).toBe('image-in-picture');
      expect(comfyUiButton.lfAriaLabel).toBe('Open ComfyUI');
      expect(comfyUiButton.title).toBe('Open ComfyUI');

      const debugButton = footer?.querySelector('.drawer-section-button-debug') as any;
      expect(debugButton).toBeTruthy();
      expect(debugButton.lfIcon).toBe('bug');
      expect(debugButton.lfAriaLabel).toBe('Toggle developer console');
      expect(debugButton.title).toBe('Toggle developer console');
    });
  });

  describe('destroy', () => {
    it('removes all drawer elements from uiRegistry', () => {
      const section = createDrawerSection(store);

      section.destroy();

      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('drawer-section');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('drawer-section-button-comfyui');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('drawer-section-button-debug');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('drawer-section-footer');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('drawer-section-button-github');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('drawer-section-container');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('drawer-section-tree');
    });
  });

  describe('render', () => {
    beforeEach(() => {
      // Setup mounted elements for render tests
      const drawer = document.createElement('lf-drawer');
      const container = document.createElement('div');
      const tree = document.createElement('lf-tree');
      const footer = document.createElement('div');
      const debugButton = document.createElement('lf-button');
      const githubButton = document.createElement('lf-button');
      const comfyUiButton = document.createElement('lf-button');

      mockManager.uiRegistry.get.mockReturnValue({
        'drawer-section': drawer,
        'drawer-section-container': container,
        'drawer-section-tree': tree,
        'drawer-section-footer': footer,
        'drawer-section-button-debug': debugButton,
        'drawer-section-button-github': githubButton,
        'drawer-section-button-comfyui': comfyUiButton,
      });
    });

    it('updates debug button for non-debug mode', () => {
      const section = createDrawerSection(store);

      // Mock non-debug state
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        isDebug: false,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const debugButton = elements['drawer-section-button-debug'];

      expect(debugButton.lfUiState).toBe('primary');
      expect(debugButton.title).toBe('Show developer console');
    });

    it('updates debug button for debug mode', () => {
      const section = createDrawerSection(store);

      // Mock debug state
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        isDebug: true,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const debugButton = elements['drawer-section-button-debug'];

      expect(debugButton.lfUiState).toBe('warning');
      expect(debugButton.title).toBe('Hide developer console');
    });

    it('updates tree dataset with workflow data', () => {
      const section = createDrawerSection(store);

      const mockWorkflows = {
        nodes: [
          {
            id: 'wf1',
            value: 'Workflow 1',
            category: 'Image Processing',
            children: [undefined, undefined] as [undefined, undefined],
          },
          {
            id: 'wf2',
            value: 'Workflow 2',
            category: 'LLM',
            children: [undefined, undefined] as [undefined, undefined],
          },
        ],
      };

      // Mock state with workflows
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        workflows: mockWorkflows,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const tree = elements['drawer-section-tree'];

      expect(tree.lfDataset).toBeDefined();
      expect(tree.lfDataset.nodes).toHaveLength(2); // Home and Workflows
      expect(tree.lfDataset.nodes[0].id).toBe('home');
      expect(tree.lfDataset.nodes[1].id).toBe('workflows');
    });

    it('categorizes workflows correctly', () => {
      const section = createDrawerSection(store);

      const mockWorkflows = {
        nodes: [
          {
            id: 'wf1',
            value: 'Image Workflow',
            category: 'Image Processing',
            children: [undefined, undefined] as [undefined, undefined],
          },
          {
            id: 'wf2',
            value: 'Text Workflow',
            category: 'LLM',
            children: [undefined, undefined] as [undefined, undefined],
          },
          {
            id: 'wf3',
            value: 'JSON Workflow',
            category: 'JSON',
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
      const tree = elements['drawer-section-tree'];
      const workflowsNode = tree.lfDataset.nodes[1]; // Workflows node

      expect(workflowsNode.children).toHaveLength(3); // Three categories
      const categories = workflowsNode.children.map((cat: any) => cat.value);
      expect(categories).toContain('Image Processing');
      expect(categories).toContain('LLM');
      expect(categories).toContain('JSON');
    });

    it('does nothing if elements are not registered', () => {
      const section = createDrawerSection(store);

      // Mock missing elements
      mockManager.uiRegistry.get.mockReturnValue(null);

      // Should not throw
      section.render();
    });
  });
});
