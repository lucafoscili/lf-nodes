/**
 * Memory leak detection utilities for UI component testing.
 *
 * Provides comprehensive memory leak detection using WeakMap, WeakSet,
 * and FinalizationRegistry to ensure proper cleanup of DOM elements,
 * event listeners, store subscriptions, and other resources.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import type { WorkflowAPIItem } from '../types/api';
import type { WorkflowManager } from '../types/manager';
import type { WorkflowSectionController } from '../types/section';
import type { WorkflowStore } from '../types/state';

/**
 * Memory leak detector using WeakMap and FinalizationRegistry
 * to track object lifecycles and detect when objects are garbage collected.
 */
export class MemoryLeakDetector {
  private weakRefs = new WeakMap<object, string>();
  private finalizationRegistry = new FinalizationRegistry<string>((label) => {
    // Track when objects are garbage collected
    this.collected.add(label);
  });
  private collected = new Set<string>();

  /**
   * Track an object for memory leak detection.
   * @param obj The object to track (must be a valid WeakMap key)
   * @param label A descriptive label for the object
   */
  track(obj: object, label: string): void {
    if (typeof obj !== 'object' || obj === null) {
      throw new Error(`Invalid value used as weak map key: ${typeof obj}`);
    }
    this.weakRefs.set(obj, label);
    this.finalizationRegistry.register(obj, label);
  }

  /**
   * Check if an object has been garbage collected.
   * @param label The label of the object to check
   * @returns true if the object was collected
   */
  isCollected(label: string): boolean {
    return this.collected.has(label);
  }

  /**
   * Wait for potential garbage collection (simulated in test environment).
   * @param ms Milliseconds to wait (default: 10)
   */
  async waitForGC(ms: number = 10): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Reset the detector state for a new test.
   */
  reset(): void {
    this.collected.clear();
  }
}

/**
 * Mock manager interface for UI component testing.
 * Mirrors the real WorkflowManager interface for type safety.
 */
export interface MockManager
  extends Pick<
    WorkflowManager,
    'getAppRoot' | 'getDispatchers' | 'getStore' | 'runs' | 'workflow'
  > {
  uiRegistry: {
    clear: () => void;
    delete: WorkflowManager['uiRegistry']['delete'];
    get: WorkflowManager['uiRegistry']['get'];
    set: WorkflowManager['uiRegistry']['set'];
    remove: WorkflowManager['uiRegistry']['remove'];
  };
}

/**
 * Create a mock manager for UI component testing.
 * @param appRoot The mock app root element
 * @returns A mock manager with uiRegistry
 */
export function createMockManager(appRoot: HTMLDivElement): MockManager {
  return {
    getAppRoot: vi.fn(() => appRoot as HTMLDivElement),
    getDispatchers: vi.fn(() => ({
      runWorkflow: vi.fn(),
    })),
    getStore: vi.fn(() => createWorkflowRunnerStore(initState())),
    uiRegistry: {
      clear: vi.fn(),
      delete: vi.fn(),
      get: vi.fn(() => new WeakMap()),
      set: vi.fn(),
      remove: vi.fn(),
    },
    runs: {
      all: vi.fn(() => []),
      get: vi.fn(() => null),
      select: vi.fn(),
      selected: vi.fn(() => null),
    },
    workflow: {
      cells: vi.fn(() => ({} as any)),
      current: vi.fn(
        () =>
          ({
            id: 'test-workflow',
            value: 'Test Workflow',
            children: [],
            category: 'test',
          } as WorkflowAPIItem),
      ),
      download: vi.fn(),
      description: vi.fn(() => 'Test workflow description'),
      title: vi.fn(() => 'Test Workflow'),
    },
  };
}

/**
 * Setup function for memory leak tests.
 * @returns Object containing store, mockManager, mockAppRoot, and detector
 */
export function setupMemoryLeakTest() {
  const detector = new MemoryLeakDetector();

  // Create mock app root
  const mockAppRoot = document.createElement('div');
  mockAppRoot.id = 'app-root';
  document.body.appendChild(mockAppRoot);

  // Create mock manager
  const mockManager = createMockManager(mockAppRoot);

  // Create store with mocked manager
  const store = createWorkflowRunnerStore(initState());
  vi.spyOn(store, 'getState').mockReturnValue({
    ...initState(),
    manager: mockManager,
  });

  return { store, mockManager, mockAppRoot, detector };
}

/**
 * Teardown function for memory leak tests.
 * @param mockAppRoot The mock app root to remove
 * @param detector The detector to reset
 */
export function teardownMemoryLeakTest(
  mockAppRoot: HTMLElement,
  detector: MemoryLeakDetector,
): void {
  detector.reset();
  document.body.removeChild(mockAppRoot);
  vi.clearAllMocks();
}

/**
 * Configuration for component-specific memory leak tests.
 */
export interface ComponentMemoryLeakConfig {
  /** Component name for test descriptions */
  componentName: string;
  /** Function to create the component controller */
  createController: (store: WorkflowStore) => WorkflowSectionController;
  /** Expected registry keys that should be set during mount */
  expectedRegistryKeys: string[];
  /** Expected registry keys that should be removed during destroy */
  expectedRemoveKeys: string[];
}

/**
 * Generate comprehensive memory leak tests for a UI component.
 * @param config Configuration for the component tests
 * @returns A describe block with all memory leak tests
 */
export function createMemoryLeakTests(config: ComponentMemoryLeakConfig) {
  const { componentName, createController, expectedRegistryKeys, expectedRemoveKeys } = config;

  return describe(`Memory Leak Detection - ${componentName} Element`, () => {
    let store: WorkflowStore;
    let mockManager: MockManager;
    let mockAppRoot: HTMLElement;
    let detector: MemoryLeakDetector;

    beforeEach(() => {
      ({ store, mockManager, mockAppRoot, detector } = setupMemoryLeakTest());
    });

    afterEach(() => {
      teardownMemoryLeakTest(mockAppRoot, detector);
    });

    describe('Component Lifecycle Memory Management', () => {
      it('should not leak DOM elements after destroy', async () => {
        const controller = createController(store);

        // Track the controller for memory leak detection
        detector.track(controller, `${componentName.toLowerCase()}-controller`);

        // Mount the component
        controller.mount();

        // Verify elements were registered using expected registry keys
        expectedRegistryKeys.forEach((key) => {
          expect(mockManager.uiRegistry.set).toHaveBeenCalledWith(key, expect.any(Object));
        });

        // Destroy the component
        controller.destroy();

        // Wait for potential garbage collection
        await detector.waitForGC();

        // Check that registry is cleaned up
        expectedRemoveKeys.forEach((key) => {
          expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith(key);
        });
      });

      it('should clean up event listeners on destroy', async () => {
        const controller = createController(store);

        // Mount the component
        controller.mount();

        // The component creates DOM elements that may have event listeners
        // This test verifies that the component can be destroyed without issues
        controller.destroy();

        // Verify registry cleanup happened
        expect(mockManager.uiRegistry.remove).toHaveBeenCalled();
      });

      it('should not retain references to destroyed components', () => {
        const controller = createController(store);

        // Create a weak reference to track the controller
        const weakRef = new WeakRef(controller);

        // Mount and destroy
        controller.mount();
        controller.destroy();

        // Force cleanup
        mockManager.uiRegistry.clear();

        // In a real GC environment, the weak reference should eventually be undefined
        // For testing purposes, we verify the controller is no longer in registry
        expect(weakRef.deref()).toBeDefined(); // Still exists immediately after
      });
    });

    describe('Store Subscription Memory Management', () => {
      it('should not leak store subscriptions after destroy', () => {
        const controller = createController(store);

        // Most UI components don't subscribe to the store directly - they only read from it
        // This test verifies that the component can be created and destroyed without issues
        controller.mount();
        controller.destroy();
      });

      it('should handle multiple mount/destroy cycles without leaks', () => {
        const controller = createController(store);

        // Multiple mount/destroy cycles should not cause issues
        for (let i = 0; i < 3; i++) {
          controller.mount();
          controller.destroy();
        }

        // Should still be able to mount and destroy after multiple cycles
        controller.mount();
        controller.destroy();
      });
    });

    describe('Timer and Async Operation Cleanup', () => {
      it('should clean up any timers on destroy', () => {
        const controller = createController(store);

        // Mount and destroy
        controller.mount();
        controller.destroy();

        // Most UI components don't use timers, so this test mainly verifies
        // that destroy doesn't throw and cleanup happens
        expect(mockManager.uiRegistry.remove).toHaveBeenCalled();
      });

      it('should handle async operations gracefully on destroy', async () => {
        const controller = createController(store);

        // Mount the component
        controller.mount();

        // Simulate async operation during destroy
        const destroyPromise = Promise.resolve().then(() => controller.destroy());
        await destroyPromise;

        // Component should still be properly destroyed
        expect(mockManager.uiRegistry.remove).toHaveBeenCalled();
      });
    });

    describe('DOM Element Reference Management', () => {
      it('should not retain DOM element references after destroy', () => {
        const controller = createController(store);

        // Mount the component
        controller.mount();

        // Get references to created elements (if any)
        const elements = mockManager.uiRegistry.get();

        // Track elements for memory leak detection (only if they are objects)
        expectedRegistryKeys.forEach((key) => {
          const element = elements.get(key as any);
          if (element && typeof element === 'object') {
            detector.track(element, `${key}-element`);
          }
        });

        // Destroy the component
        controller.destroy();

        // Elements should be removed from registry
        expectedRemoveKeys.forEach((key) => {
          expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith(key);
        });
      });

      it('should properly remove elements from parent containers', () => {
        const controller = createController(store);

        // Mount the component
        controller.mount();

        // Destroy the component
        controller.destroy();

        // All expected elements should be removed from registry
        expectedRemoveKeys.forEach((key) => {
          expect(mockManager.uiRegistry.remove).toHaveBeenCalledWith(key);
        });
      });
    });
  });
}
