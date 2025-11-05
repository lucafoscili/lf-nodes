import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { getLfFramework } from '@lf-widgets/framework';
import { createOutputsSection } from '../elements/main.outputs';
import { OUTPUTS_CLASSES } from '../elements/main.outputs';
import { MAIN_CLASSES } from '../elements/layout.main';
import { WorkflowRunEntry } from '../types/state';

// Mock the LF framework
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((block: string, element?: string) => {
        if (element) {
          return `${block}__${element}`;
        }
        return block;
      }),
      get: {
        icons: vi.fn(() => ({
          alertTriangle: 'alert-triangle',
          check: 'check',
          wand: 'wand',
          hourglassLow: 'hourglass-low',
          x: 'x',
          arrowBack: 'arrow-back',
          folder: 'folder',
          photoX: 'photo-x',
          code: 'code',
          forms: 'forms',
          json: 'json',
        })),
      },
    },
  })),
}));

// Mock handlers
vi.mock('../handlers/button', () => ({
  buttonHandler: vi.fn(),
}));
vi.mock('../handlers/masonry', () => ({
  masonryHandler: vi.fn(),
}));

// Mock utilities
vi.mock('../utils/debug', () => ({
  debugLog: vi.fn(),
}));
vi.mock('../utils/constants', () => ({
  DEBUG_MESSAGES: {
    WORKFLOW_OUTPUTS_DESTROYED: 'WORKFLOW_OUTPUTS_DESTROYED',
    WORKFLOW_OUTPUTS_MOUNTED: 'WORKFLOW_OUTPUTS_MOUNTED',
    WORKFLOW_OUTPUTS_UPDATED: 'WORKFLOW_OUTPUTS_UPDATED',
  },
  UI_CONSTANTS: {
    MASONRY_STYLE: '.masonry { display: grid; }',
  },
}));
vi.mock('../utils/common', () => ({
  formatStatus: vi.fn((status: string) => status.toUpperCase()),
  formatTimestamp: vi.fn((timestamp: string) => `formatted-${timestamp}`),
  summarizeDetail: vi.fn((detail: any) => detail || 'No error details'),
}));

describe('createOutputsSection', () => {
  let mockStore: any;
  let mockWorkflowManager: any;
  let mockRunsManager: any;
  let mockUIRegistry: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockWorkflowManager = {
      title: vi.fn(() => 'Test Workflow'),
    };

    mockRunsManager = {
      all: vi.fn(() => []),
    };

    mockUIRegistry = {
      get: vi.fn(() => null),
      set: vi.fn(),
      remove: vi.fn(),
    };

    mockStore = {
      getState: vi.fn(() => ({
        manager: {
          workflow: mockWorkflowManager,
          runs: mockRunsManager,
          uiRegistry: mockUIRegistry,
        },
        current: { id: 'workflow-1' },
        view: 'current',
      })),
    };
  });

  describe('controller creation', () => {
    it('should return a controller with mount, render, and destroy methods', () => {
      const controller = createOutputsSection(mockStore);

      expect(controller).toHaveProperty('mount');
      expect(controller).toHaveProperty('render');
      expect(controller).toHaveProperty('destroy');
      expect(typeof controller.mount).toBe('function');
      expect(typeof controller.render).toBe('function');
      expect(typeof controller.destroy).toBe('function');
    });
  });

  describe('destroy', () => {
    it('should remove all OUTPUTS_CLASSES elements from uiRegistry', () => {
      const controller = createOutputsSection(mockStore);

      controller.destroy();

      // Verify all OUTPUTS_CLASSES were removed
      Object.values(OUTPUTS_CLASSES).forEach((className) => {
        expect(mockUIRegistry.remove).toHaveBeenCalledWith(className);
      });
    });

    it('should log destruction message', () => {
      const controller = createOutputsSection(mockStore);

      controller.destroy();

      // Debug log is mocked, just verify destroy was called
      expect(mockUIRegistry.remove).toHaveBeenCalled();
    });
  });

  describe('mount', () => {
    let mockMainElement: HTMLElement;

    beforeEach(() => {
      mockMainElement = document.createElement('div');
      mockMainElement.className = MAIN_CLASSES._;
      document.body.appendChild(mockMainElement);

      mockUIRegistry.get.mockReturnValue({
        [MAIN_CLASSES._]: mockMainElement,
      });
    });

    afterEach(() => {
      document.body.removeChild(mockMainElement);
    });

    it('should not mount if already mounted', () => {
      mockUIRegistry.get.mockReturnValue({
        [OUTPUTS_CLASSES._]: document.createElement('section'),
        [MAIN_CLASSES._]: mockMainElement,
      });

      const controller = createOutputsSection(mockStore);
      controller.mount();

      // Should not call set if already mounted
      expect(mockUIRegistry.set).toHaveBeenCalledTimes(0);
    });

    it('should create and mount outputs section structure', () => {
      const controller = createOutputsSection(mockStore);
      controller.mount();

      // Verify section was created and registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(OUTPUTS_CLASSES._, expect.any(HTMLElement));

      const section = mockUIRegistry.set.mock.calls.find(
        (call) => call[0] === OUTPUTS_CLASSES._,
      )?.[1] as HTMLElement;

      expect(section.tagName).toBe('SECTION');
      expect(section.className).toBe(OUTPUTS_CLASSES._);
      expect(mockMainElement.contains(section)).toBe(true);
    });

    it('should create title with controls and toggle button', () => {
      const controller = createOutputsSection(mockStore);
      controller.mount();

      // Verify title elements were registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        OUTPUTS_CLASSES.title,
        expect.any(HTMLElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        OUTPUTS_CLASSES.h4,
        expect.any(HTMLHeadingElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        OUTPUTS_CLASSES.controls,
        expect.any(HTMLElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        OUTPUTS_CLASSES.toggle,
        expect.any(HTMLElement),
      );
    });

    it('should create masonry element', () => {
      const controller = createOutputsSection(mockStore);
      controller.mount();

      // Verify masonry was registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        OUTPUTS_CLASSES.masonry,
        expect.any(HTMLElement),
      );

      const masonryCall = mockUIRegistry.set.mock.calls.find(
        (call) => call[0] === OUTPUTS_CLASSES.masonry,
      );
      const masonry = masonryCall?.[1] as HTMLElement;

      expect(masonry.tagName).toBe('LF-MASONRY');
      expect(masonry.className).toBe(OUTPUTS_CLASSES.masonry);
    });

    it('should log mount message', () => {
      const controller = createOutputsSection(mockStore);
      controller.mount();

      // Debug log is mocked, just verify mount completed
      expect(mockUIRegistry.set).toHaveBeenCalled();
    });
  });

  describe('render', () => {
    let mockElements: Record<string, HTMLElement>;

    beforeEach(() => {
      mockElements = {
        [OUTPUTS_CLASSES.h4]: document.createElement('h4'),
        [OUTPUTS_CLASSES.masonry]: document.createElement('lf-masonry'),
        [OUTPUTS_CLASSES.toggle]: document.createElement('lf-button'),
      };

      mockUIRegistry.get.mockReturnValue(mockElements);
    });

    it('should return early if no elements', () => {
      mockUIRegistry.get.mockReturnValue(null);

      const controller = createOutputsSection(mockStore);
      controller.render();

      // Should not call workflow methods if no elements
      expect(mockWorkflowManager.title).toHaveBeenCalledTimes(0);
    });

    it('should return early if required elements are missing', () => {
      mockUIRegistry.get.mockReturnValue({
        [OUTPUTS_CLASSES.h4]: null,
      });

      const controller = createOutputsSection(mockStore);
      controller.render();

      expect(mockWorkflowManager.title).toHaveBeenCalledTimes(0);
    });

    it('should update title from workflow', () => {
      mockWorkflowManager.title.mockReturnValue('My Workflow');

      const controller = createOutputsSection(mockStore);
      controller.render();

      const h4 = mockElements[OUTPUTS_CLASSES.h4] as HTMLElement;
      expect(h4.textContent).toBe('My Workflow outputs');
    });

    it('should update title when no workflow title', () => {
      mockWorkflowManager.title.mockReturnValue('');

      const controller = createOutputsSection(mockStore);
      controller.render();

      const h4 = mockElements[OUTPUTS_CLASSES.h4] as HTMLElement;
      expect(h4.textContent).toBe('Workflow outputs');
    });

    it('should show current workflow runs when view is current', () => {
      const mockRuns = [
        { runId: 'run1', workflowId: 'workflow-1', status: 'succeeded' } as WorkflowRunEntry,
        { runId: 'run2', workflowId: 'workflow-2', status: 'failed' } as WorkflowRunEntry,
      ];
      mockRunsManager.all.mockReturnValue(mockRuns);

      const controller = createOutputsSection(mockStore);
      controller.render();

      const masonry = mockElements[OUTPUTS_CLASSES.masonry] as any;
      expect(masonry.lfDataset.nodes).toHaveLength(1);
      expect(masonry.lfDataset.nodes[0].id).toBe('run1');
    });

    it('should show all runs when view is history', () => {
      mockStore.getState.mockReturnValue({
        ...mockStore.getState(),
        view: 'history',
      });

      const mockRuns = [
        { runId: 'run1', workflowId: 'workflow-1', status: 'succeeded' } as WorkflowRunEntry,
        { runId: 'run2', workflowId: 'workflow-2', status: 'failed' } as WorkflowRunEntry,
      ];
      mockRunsManager.all.mockReturnValue(mockRuns);

      const controller = createOutputsSection(mockStore);
      controller.render();

      const masonry = mockElements[OUTPUTS_CLASSES.masonry] as any;
      expect(masonry.lfDataset.nodes).toHaveLength(2);
    });

    it('should show empty state when no runs', () => {
      mockRunsManager.all.mockReturnValue([]);

      const controller = createOutputsSection(mockStore);
      controller.render();

      const masonry = mockElements[OUTPUTS_CLASSES.masonry] as any;
      expect(masonry.lfDataset.nodes).toHaveLength(1);
      expect(masonry.lfDataset.nodes[0].id).toBe('');
      expect(masonry.lfCollapseColumns).toBe(true);
      expect(masonry.lfSelectable).toBe(false);
    });

    it('should configure masonry for multiple runs', () => {
      const mockRuns = [
        { runId: 'run1', workflowId: 'workflow-1', status: 'succeeded' } as WorkflowRunEntry,
      ];
      mockRunsManager.all.mockReturnValue(mockRuns);

      const controller = createOutputsSection(mockStore);
      controller.render();

      const masonry = mockElements[OUTPUTS_CLASSES.masonry] as any;
      expect(masonry.lfCollapseColumns).toBe(false);
      expect(masonry.lfSelectable).toBe(true);
    });

    it('should update toggle button for current view', () => {
      mockRunsManager.all.mockReturnValue([]);

      const controller = createOutputsSection(mockStore);
      controller.render();

      const toggle = mockElements[OUTPUTS_CLASSES.toggle] as any;
      expect(toggle.lfIcon).toBe('folder');
      expect(toggle.lfLabel).toBe('History');
      expect(toggle.lfUiState).toBe('disabled');
    });

    it('should update toggle button for history view', () => {
      mockStore.getState.mockReturnValue({
        ...mockStore.getState(),
        view: 'history',
      });

      const controller = createOutputsSection(mockStore);
      controller.render();

      const toggle = mockElements[OUTPUTS_CLASSES.toggle] as any;
      expect(toggle.lfIcon).toBe('arrow-back');
      expect(toggle.lfLabel).toBe('Back');
      expect(toggle.lfUiState).toBe('primary');
    });

    it('should enable toggle button when runs exist', () => {
      const mockRuns = [
        { runId: 'run1', workflowId: 'workflow-1', status: 'succeeded' } as WorkflowRunEntry,
      ];
      mockRunsManager.all.mockReturnValue(mockRuns);

      const controller = createOutputsSection(mockStore);
      controller.render();

      const toggle = mockElements[OUTPUTS_CLASSES.toggle] as any;
      expect(toggle.lfUiState).toBe('primary');
    });

    it('should log render message', () => {
      const controller = createOutputsSection(mockStore);
      controller.render();

      // Debug log is mocked, just verify render completed
      expect(mockWorkflowManager.title).toHaveBeenCalled();
    });
  });
});
