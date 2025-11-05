import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { createHeaderSection } from '../elements/layout.header';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { getLfFramework } from '@lf-widgets/framework';

// Mock the LF framework
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((...args: string[]) => args.join('-')),
      get: {
        icon: vi.fn(() => 'menu2'),
        icons: vi.fn(() => ({
          alertTriangle: 'alert-triangle',
          check: 'check',
          hourglassLow: 'hourglass-low',
        })),
      },
    },
  })),
}));

// Mock the components module
vi.mock('../elements/components', () => ({
  createComponent: {
    button: vi.fn((props: any) => {
      const button = document.createElement('lf-button');
      Object.assign(button, props);
      return button;
    }),
  },
}));

describe('Header Element', () => {
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

  describe('createHeaderSection', () => {
    it('returns a WorkflowSectionController with required methods', () => {
      const section = createHeaderSection(store);

      expect(section).toHaveProperty('destroy');
      expect(section).toHaveProperty('mount');
      expect(section).toHaveProperty('render');
      expect(typeof section.destroy).toBe('function');
      expect(typeof section.mount).toBe('function');
      expect(typeof section.render).toBe('function');
    });
  });

  describe('mount', () => {
    it('mounts the header to the app root', () => {
      const section = createHeaderSection(store);

      section.mount();

      // Should create and append a header element
      const header = mockAppRoot.querySelector('lf-header');
      expect(header).toBeTruthy();
      expect(header?.className).toContain('header-section');

      // Should create container, app message, drawer toggle, and server indicator
      const container = header?.querySelector('[slot="content"]');
      expect(container).toBeTruthy();
      expect(container?.className).toContain('header-section-container');

      const appMessage = container?.querySelector('.header-section-app-message');
      expect(appMessage).toBeTruthy();

      const drawerToggle = container?.querySelector('.header-section-drawer-toggle');
      expect(drawerToggle).toBeTruthy();

      const serverIndicator = container?.querySelector('.header-section-server-indicator');
      expect(serverIndicator).toBeTruthy();
    });

    it('does not mount if already mounted', () => {
      const section = createHeaderSection(store);

      // Mock that element already exists
      mockManager.uiRegistry.get.mockReturnValue({
        'header-section': document.createElement('lf-header'),
      });

      section.mount();

      // Should not append anything new
      const headers = mockAppRoot.querySelectorAll('lf-header');
      expect(headers.length).toBe(0);
    });

    it('registers all header elements in uiRegistry', () => {
      const section = createHeaderSection(store);

      section.mount();

      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'header-section',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'header-section-app-message',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'header-section-container',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'header-section-drawer-toggle',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'header-section-server-indicator',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'header-section-server-indicator-counter',
        expect.any(Element),
      );
      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'header-section-server-indicator-light',
        expect.any(Element),
      );
    });
  });

  describe('destroy', () => {
    it('removes all header elements from uiRegistry', () => {
      const section = createHeaderSection(store);

      section.destroy();

      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('header-section');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('header-section-app-message');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('header-section-container');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('header-section-drawer-toggle');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('header-section-server-indicator');
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith(
        'header-section-server-indicator-counter',
      );
      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith(
        'header-section-server-indicator-light',
      );
    });

    it('clears app message timers', () => {
      const section = createHeaderSection(store);

      // Mock app message with timer
      const mockAppMessage = document.createElement('div');
      const mockTimer = setTimeout(() => {}, 1000);
      (mockAppMessage as any).__lf_hide_timer__ = mockTimer;

      mockManager.uiRegistry.get.mockReturnValue({
        'header-section-app-message': mockAppMessage,
      });

      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');

      section.destroy();

      expect(clearTimeoutSpy).toHaveBeenCalledWith(mockTimer);
      expect((mockAppMessage as any).__lf_hide_timer__).toBeUndefined();
    });
  });

  describe('render', () => {
    beforeEach(() => {
      // Setup mounted elements for render tests
      const header = document.createElement('lf-header');
      const appMessage = document.createElement('div');
      const container = document.createElement('div');
      const drawerToggle = document.createElement('lf-button');
      const serverIndicator = document.createElement('div');
      const counter = document.createElement('span');
      const light = document.createElement('lf-button');

      mockManager.uiRegistry.get.mockReturnValue({
        'header-section': header,
        'header-section-app-message': appMessage,
        'header-section-container': container,
        'header-section-drawer-toggle': drawerToggle,
        'header-section-server-indicator': serverIndicator,
        'header-section-server-indicator-counter': counter,
        'header-section-server-indicator-light': light,
      });
    });

    it('updates app message when idle with message', () => {
      const section = createHeaderSection(store);

      // Mock idle state with message
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        current: {
          id: null,
          status: 'idle',
          message: 'Workflow completed successfully',
        },
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const appMessage = elements['header-section-app-message'];

      expect(appMessage.innerText).toBe('Workflow completed successfully');
      expect(appMessage.dataset.status).toBe('idle');
      expect(appMessage.dataset.visible).toBe('true');
    });

    it('updates server indicator for disconnected state', () => {
      const section = createHeaderSection(store);

      // Mock disconnected state
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        queuedJobs: -1,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const counter = elements['header-section-server-indicator-counter'];
      const light = elements['header-section-server-indicator-light'];

      expect(counter.innerText).toBe('');
      expect(light.lfIcon).toBe('alert-triangle');
      expect(light.lfUiState).toBe('danger');
      expect(light.title).toBe('Server disconnected');
    });

    it('updates server indicator for idle state', () => {
      const section = createHeaderSection(store);

      // Mock idle state
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        queuedJobs: 0,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const counter = elements['header-section-server-indicator-counter'];
      const light = elements['header-section-server-indicator-light'];

      expect(counter.innerText).toBe('');
      expect(light.lfIcon).toBe('check');
      expect(light.lfUiState).toBe('success');
      expect(light.title).toBe('Server idle');
    });

    it('updates server indicator for queued jobs', () => {
      const section = createHeaderSection(store);

      // Mock queued jobs state
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        queuedJobs: 3,
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const counter = elements['header-section-server-indicator-counter'];
      const light = elements['header-section-server-indicator-light'];

      expect(counter.innerText).toBe('3');
      expect(light.lfIcon).toBe('hourglass-low');
      expect(light.lfUiState).toBe('warning');
      expect(light.title).toBe('Jobs in queue: 3');
    });

    it('updates app message for running state with run ID', () => {
      const section = createHeaderSection(store);

      // Mock running state with run ID
      vi.spyOn(store, 'getState').mockReturnValue({
        ...initState(),
        manager: mockManager,
        current: {
          id: null,
          status: 'running',
          message: 'Processing workflow',
        },
        currentRunId: 'abc123-def456-ghi789',
      });

      section.render();

      const elements = mockManager.uiRegistry.get();
      const appMessage = elements['header-section-app-message'];

      expect(appMessage.innerText).toBe('Processing abc123');
      expect(appMessage.dataset.status).toBe('running');
      expect(appMessage.dataset.visible).toBe('true');
    });

    it('does nothing if elements are not registered', () => {
      const section = createHeaderSection(store);

      // Mock missing elements
      mockManager.uiRegistry.get.mockReturnValue(null);

      // Should not throw
      section.render();
    });
  });
});
