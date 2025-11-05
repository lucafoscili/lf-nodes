import { describe } from 'vitest';
import { createResultsSection } from '../../../src/elements/main.results';
import { createMemoryLeakTests } from '../memory-leak-utils';
import { setupMemoryLeakTest, teardownMemoryLeakTest } from '../memory-leak-utils';

const resultsConfig = {
  componentName: 'Results',
  createComponent: createResultsSection,
  registryKeys: [
    'results-section',
    'results-section__actions',
    'results-section__back',
    'results-section__description',
    'results-section__title-h3',
    'results-section__history',
    'results-section__results',
    'results-section__title',
  ],
  mockDependencies: {
    lfFramework: true,
    lfButton: true,
    workflow: true,
    workflowRuns: true,
  },
};

describe('Results Memory Leak Tests', () => {
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

  createMemoryLeakTests(resultsConfig);
});
