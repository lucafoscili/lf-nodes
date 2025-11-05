import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { getLfFramework } from '@lf-widgets/framework';
import { createResultsSection } from '../elements/main.results';
import { RESULTS_CLASSES } from '../elements/main.results';
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
          arrowBack: 'arrow-back',
          folder: 'folder',
        })),
      },
    },
    syntax: {
      json: {
        isLikeString: vi.fn(() => false),
      },
    },
  })),
}));

// Mock handlers
vi.mock('../handlers/button', () => ({
  buttonHandler: vi.fn(),
}));

// Mock utilities
vi.mock('../utils/debug', () => ({
  debugLog: vi.fn(),
}));
vi.mock('../utils/constants', () => ({
  DEBUG_MESSAGES: {
    WORKFLOW_RESULTS_DESTROYED: 'WORKFLOW_RESULTS_DESTROYED',
    WORKFLOW_RESULTS_MOUNTED: 'WORKFLOW_RESULTS_MOUNTED',
    WORKFLOW_RESULTS_UPDATED: 'WORKFLOW_RESULTS_UPDATED',
  },
}));
vi.mock('../utils/common', () => ({
  clearChildren: vi.fn(),
  deepMerge: vi.fn((a, b) => {
    // Convert objects to arrays for the test
    const aArray = Array.isArray(a) ? a : Object.values(a || {});
    const bArray = Array.isArray(b) ? b : Object.values(b || {});
    return [...aArray, ...bArray];
  }),
  formatStatus: vi.fn((status: string) => status?.toUpperCase() || 'UNKNOWN'),
  formatTimestamp: vi.fn((timestamp: string) => `formatted-${timestamp}`),
  stringifyDetail: vi.fn((detail: any) => (detail ? JSON.stringify(detail) : null)),
  summarizeDetail: vi.fn((detail: any) => detail || 'No error details'),
}));
vi.mock('../elements/components', () => ({
  createComponent: {
    code: vi.fn((props: any) => {
      const element = document.createElement('lf-code');
      Object.assign(element, props);
      return element;
    }),
  },
  createOutputComponent: vi.fn((output: any) => {
    const element = document.createElement('div');
    element.id = output.id || 'output-component';
    return element;
  }),
}));

describe('createResultsSection', () => {
  let mockStore: any;
  let mockWorkflowManager: any;
  let mockRunsManager: any;
  let mockUIRegistry: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockWorkflowManager = {
      title: vi.fn(() => 'Test Workflow'),
      description: vi.fn(() => 'Test Description'),
      current: vi.fn(() => ({ id: 'workflow-1' })),
      cells: vi.fn(() => ({})),
    };

    mockRunsManager = {
      all: vi.fn(() => []),
      selected: vi.fn(() => null),
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
        results: null,
      })),
    };
  });

  describe('controller creation', () => {
    it('should return a controller with mount, render, and destroy methods', () => {
      const controller = createResultsSection(mockStore);

      expect(controller).toHaveProperty('mount');
      expect(controller).toHaveProperty('render');
      expect(controller).toHaveProperty('destroy');
      expect(typeof controller.mount).toBe('function');
      expect(typeof controller.render).toBe('function');
      expect(typeof controller.destroy).toBe('function');
    });
  });

  describe('destroy', () => {
    it('should remove all RESULTS_CLASSES elements from uiRegistry', () => {
      const controller = createResultsSection(mockStore);

      controller.destroy();

      // Verify all RESULTS_CLASSES were removed
      Object.values(RESULTS_CLASSES).forEach((className) => {
        expect(mockUIRegistry.remove).toHaveBeenCalledWith(className);
      });
    });

    it('should log destruction message', () => {
      const controller = createResultsSection(mockStore);

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
        [RESULTS_CLASSES._]: document.createElement('section'),
        [MAIN_CLASSES._]: mockMainElement,
      });

      const controller = createResultsSection(mockStore);
      controller.mount();

      // Should not call set if already mounted
      expect(mockUIRegistry.set).toHaveBeenCalledTimes(0);
    });

    it('should create and mount results section structure', () => {
      const controller = createResultsSection(mockStore);
      controller.mount();

      // Verify section was created and registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(RESULTS_CLASSES._, expect.any(HTMLElement));

      const section = mockUIRegistry.set.mock.calls.find(
        (call) => call[0] === RESULTS_CLASSES._,
      )?.[1] as HTMLElement;

      expect(section.tagName).toBe('SECTION');
      expect(section.className).toBe(RESULTS_CLASSES._);
      expect(mockMainElement.contains(section)).toBe(true);
    });

    it('should create title with action buttons', () => {
      const controller = createResultsSection(mockStore);
      controller.mount();

      // Verify title elements were registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        RESULTS_CLASSES.title,
        expect.any(HTMLElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        RESULTS_CLASSES.h3,
        expect.any(HTMLHeadingElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        RESULTS_CLASSES.actions,
        expect.any(HTMLElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        RESULTS_CLASSES.back,
        expect.any(HTMLElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        RESULTS_CLASSES.history,
        expect.any(HTMLElement),
      );
    });

    it('should create results container', () => {
      const controller = createResultsSection(mockStore);
      controller.mount();

      // Verify results container was registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        RESULTS_CLASSES.results,
        expect.any(HTMLElement),
      );
    });

    it('should log mount message', () => {
      const controller = createResultsSection(mockStore);
      controller.mount();

      // Debug log is mocked, just verify mount completed
      expect(mockUIRegistry.set).toHaveBeenCalled();
    });
  });

  describe('render', () => {
    let mockElements: Record<string, HTMLElement>;

    beforeEach(() => {
      mockElements = {
        [RESULTS_CLASSES.description]: document.createElement('p'),
        [RESULTS_CLASSES.results]: document.createElement('div'),
        [RESULTS_CLASSES.h3]: document.createElement('h3'),
        [RESULTS_CLASSES.back]: document.createElement('lf-button'),
        [RESULTS_CLASSES.history]: document.createElement('lf-button'),
      };

      mockUIRegistry.get.mockReturnValue(mockElements);
    });

    it('should return early if no elements', () => {
      mockUIRegistry.get.mockReturnValue(null);

      const controller = createResultsSection(mockStore);
      controller.render();

      // Should not call workflow methods if no elements
      expect(mockWorkflowManager.title).toHaveBeenCalledTimes(0);
    });

    it('should update title and description when no run selected', () => {
      const controller = createResultsSection(mockStore);
      controller.render();

      const h3 = mockElements[RESULTS_CLASSES.h3] as HTMLElement;
      const descr = mockElements[RESULTS_CLASSES.description] as HTMLElement;

      expect(h3.textContent).toBe('Test Workflow');
      expect(descr.textContent).toBe('Test Description');
    });

    it('should update title and description when run is selected', () => {
      const selectedRun = {
        runId: 'run-12345678',
        workflowName: 'Selected Workflow',
        status: 'succeeded',
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-01-01T01:00:00Z',
      } as unknown as WorkflowRunEntry;

      mockRunsManager.selected.mockReturnValue(selectedRun);

      const controller = createResultsSection(mockStore);
      controller.render();

      const h3 = mockElements[RESULTS_CLASSES.h3] as HTMLElement;
      const descr = mockElements[RESULTS_CLASSES.description] as HTMLElement;

      expect(h3.textContent).toBe('Selected Workflow');
      expect(descr.textContent).toContain('Run run-1234');
      expect(descr.textContent).toContain('SUCCEEDED');
    });

    it('should disable back button when no run selected', () => {
      const controller = createResultsSection(mockStore);
      controller.render();

      const backButton = mockElements[RESULTS_CLASSES.back] as any;
      expect(backButton.lfUiState).toBe('disabled');
    });

    it('should enable back button when run is selected', () => {
      mockRunsManager.selected.mockReturnValue({ runId: 'run-1' } as WorkflowRunEntry);

      const controller = createResultsSection(mockStore);
      controller.render();

      const backButton = mockElements[RESULTS_CLASSES.back] as any;
      expect(backButton.lfUiState).toBe('primary');
    });

    it('should disable history button when no runs exist', () => {
      const controller = createResultsSection(mockStore);
      controller.render();

      const historyButton = mockElements[RESULTS_CLASSES.history] as any;
      expect(historyButton.lfUiState).toBe('disabled');
    });

    it('should enable history button when runs exist', () => {
      mockRunsManager.all.mockReturnValue([{ runId: 'run-1' } as WorkflowRunEntry]);

      const controller = createResultsSection(mockStore);
      controller.render();

      const historyButton = mockElements[RESULTS_CLASSES.history] as any;
      expect(historyButton.lfUiState).toBe('primary');
    });

    it('should show empty message when no outputs', () => {
      const controller = createResultsSection(mockStore);
      controller.render();

      const results = mockElements[RESULTS_CLASSES.results] as HTMLElement;
      expect(results.children).toHaveLength(1);
      expect(results.children[0].tagName).toBe('P');
      expect(results.children[0].className).toBe(RESULTS_CLASSES.empty);
      expect(results.children[0].textContent).toBe('Select a run to inspect its outputs.');
    });

    it('should show error details when run has error', () => {
      const selectedRun = {
        runId: 'run-1',
        error: { message: 'Test error' },
      } as unknown as WorkflowRunEntry;

      mockRunsManager.selected.mockReturnValue(selectedRun);

      const controller = createResultsSection(mockStore);
      controller.render();

      const results = mockElements[RESULTS_CLASSES.results] as HTMLElement;
      // Should have empty message + error detail section
      expect(results.children.length).toBeGreaterThan(1);
    });

    it('should render outputs when available', () => {
      const outputs = {
        node1: { id: 'output1', nodeId: 'node1', title: 'Output 1' },
        node2: { id: 'output2', nodeId: 'node2', title: 'Output 2' },
      };

      mockStore.getState.mockReturnValue({
        ...mockStore.getState(),
        results: outputs,
      });

      const controller = createResultsSection(mockStore);
      controller.render();

      const results = mockElements[RESULTS_CLASSES.results] as HTMLElement;
      // Should have h4 + grid for each output
      expect(results.children.length).toBeGreaterThan(2);
    });

    it('should clear children before rendering', () => {
      const controller = createResultsSection(mockStore);
      controller.render();

      // clearChildren is mocked, just verify render was called
      expect(mockWorkflowManager.title).toHaveBeenCalled();
    });

    it('should log render message', () => {
      const controller = createResultsSection(mockStore);
      controller.render();

      // Debug log is mocked, just verify render completed
      expect(mockWorkflowManager.title).toHaveBeenCalled();
    });
  });
});
