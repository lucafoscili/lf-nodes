import { describe } from 'vitest';
import { createActionButtonSection } from '../../../src/elements/layout.action-button';
import { createMemoryLeakTests } from '../memory-leak-utils';
import { setupMemoryLeakTest, teardownMemoryLeakTest } from '../memory-leak-utils';

const actionButtonConfig = {
  componentName: 'ActionButton',
  createComponent: createActionButtonSection,
  registryKeys: ['action-button-section'],
  mockDependencies: {
    lfFramework: true,
    lfButton: true,
  },
};

describe('ActionButton Memory Leak Tests', () => {
  let cleanup: (() => void) | null = null;

  beforeEach(() => {
    cleanup = setupMemoryLeakTest();
  });

  afterEach(() => {
    if (cleanup) {
      cleanup();
    }
    teardownMemoryLeakTest();
  });

  createMemoryLeakTests(actionButtonConfig);
});
