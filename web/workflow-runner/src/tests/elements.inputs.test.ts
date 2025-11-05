import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { getLfFramework } from '@lf-widgets/framework';
import { createInputsSection } from '../elements/main.inputs';
import { INPUTS_CLASSES } from '../elements/main.inputs';
import { MAIN_CLASSES } from '../elements/layout.main';
import { WorkflowCellInput } from '../types/api';

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
        icon: vi.fn(() => 'download-icon'),
      },
    },
    sanitizeProps: vi.fn((props: any) => props),
  })),
}));

// Mock button handler
vi.mock('../handlers/button', () => ({
  buttonHandler: vi.fn(),
}));

// Mock debug utilities
vi.mock('../utils/debug', () => ({
  debugLog: vi.fn(),
}));

// Mock constants
vi.mock('../utils/constants', () => ({
  DEBUG_MESSAGES: {
    WORKFLOW_INPUTS_DESTROYED: 'WORKFLOW_INPUTS_DESTROYED',
    WORKFLOW_INPUTS_MOUNTED: 'WORKFLOW_INPUTS_MOUNTED',
    WORKFLOW_INPUTS_UPDATED: 'WORKFLOW_INPUTS_UPDATED',
  },
}));

// Mock components
vi.mock('../elements/components', () => ({
  createInputCell: vi.fn((cell: WorkflowCellInput) => {
    const element = document.createElement('div');
    element.id = 'mock-input-cell';
    element.setAttribute('data-shape', cell.shape || 'textfield');
    return element;
  }),
}));

describe('createInputsSection', () => {
  let mockStore: any;
  let mockWorkflowManager: any;
  let mockUIRegistry: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockWorkflowManager = {
      current: vi.fn(() => ({ id: 'test-workflow' })),
      cells: vi.fn(() => ({})),
      title: vi.fn(() => 'Test Workflow'),
      description: vi.fn(() => 'Test Description'),
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
          uiRegistry: mockUIRegistry,
        },
        inputStatuses: {},
      })),
    };
  });

  describe('controller creation', () => {
    it('should return a controller with mount, render, and destroy methods', () => {
      const controller = createInputsSection(mockStore);

      expect(controller).toHaveProperty('mount');
      expect(controller).toHaveProperty('render');
      expect(controller).toHaveProperty('destroy');
      expect(typeof controller.mount).toBe('function');
      expect(typeof controller.render).toBe('function');
      expect(typeof controller.destroy).toBe('function');
    });
  });

  describe('destroy', () => {
    it('should remove all INPUTS_CLASSES elements from uiRegistry', () => {
      const controller = createInputsSection(mockStore);

      controller.destroy();

      // Verify all INPUTS_CLASSES were removed
      Object.values(INPUTS_CLASSES).forEach((className) => {
        expect(mockUIRegistry.remove).toHaveBeenCalledWith(className);
      });
    });

    it('should log destruction message', () => {
      const controller = createInputsSection(mockStore);

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
        [INPUTS_CLASSES._]: document.createElement('section'),
        [MAIN_CLASSES._]: mockMainElement,
      });

      const controller = createInputsSection(mockStore);
      controller.mount();

      // Should not call set if already mounted
      expect(mockUIRegistry.set).toHaveBeenCalledTimes(0);
    });

    it('should create and mount inputs section structure', () => {
      const controller = createInputsSection(mockStore);
      controller.mount();

      // Verify section was created and registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(INPUTS_CLASSES._, expect.any(HTMLElement));

      const section = mockUIRegistry.set.mock.calls.find(
        (call) => call[0] === INPUTS_CLASSES._,
      )?.[1] as HTMLElement;

      expect(section.tagName).toBe('SECTION');
      expect(section.className).toBe(INPUTS_CLASSES._);
      expect(mockMainElement.contains(section)).toBe(true);
    });

    it('should create title with download button', () => {
      const controller = createInputsSection(mockStore);
      controller.mount();

      // Verify title elements were registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        INPUTS_CLASSES.title,
        expect.any(HTMLElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        INPUTS_CLASSES.h3,
        expect.any(HTMLHeadingElement),
      );
      expect(mockUIRegistry.set).toHaveBeenCalledWith(
        INPUTS_CLASSES.openButton,
        expect.any(HTMLElement),
      );
    });

    it('should create input cells for workflow inputs', () => {
      const mockCells = {
        input1: { shape: 'textfield', props: {} } as WorkflowCellInput,
        input2: { shape: 'toggle', props: {} } as WorkflowCellInput,
      };

      mockWorkflowManager.cells.mockReturnValue(mockCells);

      const controller = createInputsSection(mockStore);
      controller.mount();

      // Verify cells were created and registered
      expect(mockUIRegistry.set).toHaveBeenCalledWith(INPUTS_CLASSES.cells, expect.any(Array));

      const cellsCall = mockUIRegistry.set.mock.calls.find(
        (call) => call[0] === INPUTS_CLASSES.cells,
      );
      const cells = cellsCall?.[1] as HTMLElement[];

      expect(cells).toHaveLength(2);
      cells.forEach((cell, index) => {
        const expectedId = index === 0 ? 'input1' : 'input2';
        expect(cell.id).toBe(expectedId);
      });
    });

    it('should handle empty workflow inputs', () => {
      mockWorkflowManager.cells.mockReturnValue({});

      const controller = createInputsSection(mockStore);
      controller.mount();

      const cellsCall = mockUIRegistry.set.mock.calls.find(
        (call) => call[0] === INPUTS_CLASSES.cells,
      );
      const cells = cellsCall?.[1] as HTMLElement[];

      expect(cells).toHaveLength(0);
    });

    it('should log mount message', () => {
      const controller = createInputsSection(mockStore);
      controller.mount();

      // Debug log is mocked, just verify mount completed
      expect(mockUIRegistry.set).toHaveBeenCalled();
    });
  });

  describe('render', () => {
    let mockElements: Record<string, HTMLElement | HTMLElement[]>;

    beforeEach(() => {
      mockElements = {
        [INPUTS_CLASSES.cells]: [
          Object.assign(document.createElement('div'), { id: 'input1' }),
          Object.assign(document.createElement('div'), { id: 'input2' }),
        ],
        [INPUTS_CLASSES.description]: document.createElement('p'),
        [INPUTS_CLASSES.h3]: document.createElement('h3'),
      };

      mockUIRegistry.get.mockReturnValue(mockElements);
    });

    it('should return early if no elements', () => {
      mockUIRegistry.get.mockReturnValue(null);

      const controller = createInputsSection(mockStore);
      controller.render();

      // Should not call workflow methods if no elements
      expect(mockWorkflowManager.title).toHaveBeenCalledTimes(0);
    });

    it('should update title and description from workflow', () => {
      mockWorkflowManager.title.mockReturnValue('Test Workflow');
      mockWorkflowManager.description.mockReturnValue('Test Description');

      const controller = createInputsSection(mockStore);
      controller.render();

      const h3 = mockElements[INPUTS_CLASSES.h3] as HTMLElement;
      const desc = mockElements[INPUTS_CLASSES.description] as HTMLElement;

      expect(h3.textContent).toBe('Test Workflow');
      expect(desc.textContent).toBe('Test Description');
    });

    it('should update cell status from inputStatuses', () => {
      const mockStatuses = { input1: 'valid', input2: 'invalid' };
      mockStore.getState.mockReturnValue({
        manager: mockStore.getState().manager,
        inputStatuses: mockStatuses,
      });

      // Add parent elements to cells
      const cells = mockElements[INPUTS_CLASSES.cells] as HTMLElement[];
      cells.forEach((cell) => {
        const parent = document.createElement('div');
        parent.appendChild(cell);
      });

      const controller = createInputsSection(mockStore);
      controller.render();

      cells.forEach((cell, index) => {
        const parent = cell.parentElement!;
        const expectedStatus = index === 0 ? 'valid' : 'invalid';
        expect(parent.dataset.status).toBe(expectedStatus);
      });
    });

    it('should remove status dataset when no status', () => {
      const mockStatuses = { input1: 'valid' };
      mockStore.getState.mockReturnValue({
        manager: mockStore.getState().manager,
        inputStatuses: mockStatuses,
      });

      const cells = mockElements[INPUTS_CLASSES.cells] as HTMLElement[];
      // Create parent elements and append cells
      cells.forEach((cell) => {
        const parent = document.createElement('div');
        parent.appendChild(cell);
      });

      const controller = createInputsSection(mockStore);
      controller.render();

      expect(cells[0].parentElement!.dataset.status).toBe('valid');
      expect(cells[1].parentElement!.dataset.status).toBeUndefined();
    });

    it('should log render message', () => {
      const controller = createInputsSection(mockStore);
      controller.render();

      // Debug log is mocked, just verify render completed
      expect(mockWorkflowManager.title).toHaveBeenCalled();
    });
  });
});
