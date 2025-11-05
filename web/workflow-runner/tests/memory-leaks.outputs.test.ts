import { describe } from 'vitest';
import { createOutputsSection } from '../../../src/elements/main.outputs';
import { createMemoryLeakTests } from '../memory-leak-utils';
import { setupMemoryLeakTest, teardownMemoryLeakTest } from '../memory-leak-utils';

const outputsConfig = {
  componentName: 'Outputs',
  createComponent: createOutputsSection,
  registryKeys: [
    'outputs-section',
    'outputs-section__controls',
    'outputs-section__title-h4',
    'outputs-section__masonry',
    'outputs-section__title',
    'outputs-section__toggle',
  ],
  mockDependencies: {
    lfFramework: true,
    lfButton: true,
    lfMasonry: true,
    workflow: true,
    workflowRuns: true,
  },
};

describe('Outputs Memory Leak Tests', () => {
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

  createMemoryLeakTests(outputsConfig);
});
