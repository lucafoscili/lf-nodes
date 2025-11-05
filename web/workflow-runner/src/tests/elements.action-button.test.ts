import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { createActionButtonSection } from '../elements/layout.action-button';
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

describe('Action Button Element', () => {
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
        get: vi.fn(() => ({})),
        set: vi.fn(),
        remove: vi.fn(),
        delete: vi.fn(),
      },
    };
    store.getState().mutate.manager(mockManager);
  });

  afterEach(() => {
    document.body.removeChild(mockAppRoot);
    vi.clearAllMocks();
  });

  describe('createActionButtonSection', () => {
    it('returns a WorkflowSectionController with required methods', () => {
      const section = createActionButtonSection(store);

      expect(section).toHaveProperty('mount');
      expect(section).toHaveProperty('render');
      expect(section).toHaveProperty('destroy');
      expect(typeof section.mount).toBe('function');
      expect(typeof section.render).toBe('function');
      expect(typeof section.destroy).toBe('function');
    });

    it('mounts the action button to the app root', () => {
      const section = createActionButtonSection(store);

      section.mount();

      // Should create and append a button element
      const button = mockAppRoot.querySelector('lf-button') as any;
      expect(button).toBeTruthy();
      expect(button?.className).toContain('action-button-section');
      // Check properties set on the element (attributes are handled by the web component)
      expect(button?.lfIcon).toBe('send');
      expect(button?.lfStyling).toBe('floating');
      expect(button?.title).toBe('Run current workflow');
    });

    it('does not mount if already mounted', () => {
      const section = createActionButtonSection(store);

      // Mock that element already exists
      mockManager.uiRegistry.get.mockReturnValue({
        'action-button-section': document.createElement('lf-button'),
      });

      section.mount();

      // Should not append anything new
      const buttons = mockAppRoot.querySelectorAll('lf-button');
      expect(buttons.length).toBe(0);
    });

    it('registers the button in uiRegistry', () => {
      const section = createActionButtonSection(store);

      section.mount();

      expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(
        'action-button-section',
        expect.any(HTMLElement),
      );
    });

    it('destroys the action button and cleans up registry', () => {
      const section = createActionButtonSection(store);
      section.mount();

      const button = mockAppRoot.querySelector('lf-button');
      expect(button).toBeTruthy();

      section.destroy();

      expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith('action-button-section');
    });

    it('render updates existing button', () => {
      const section = createActionButtonSection(store);
      section.mount();

      // Mock existing element in registry
      const existingButton = document.createElement('lf-button');
      mockManager.uiRegistry.get.mockReturnValue({
        'action-button-section': existingButton,
      });

      section.render();

      // Should not create new elements, just update existing
      expect(mockManager.uiRegistry.set).toHaveBeenCalledTimes(1); // Only from mount
    });

    it('render does nothing if no elements in registry', () => {
      const section = createActionButtonSection(store);

      mockManager.uiRegistry.get.mockReturnValue(null);

      // Should not throw when no elements exist
      section.render();
    });
  });
});
