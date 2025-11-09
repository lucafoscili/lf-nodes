import { describe } from 'vitest';
import { createInputsSection } from '../../../src/elements/main.inputs';
import { createMemoryLeakTests } from '../memory-leak-utils';
import { setupMemoryLeakTest, teardownMemoryLeakTest } from '../memory-leak-utils';

const inputsConfig = {
  componentName: 'Inputs',
  createComponent: createInputsSection,
  registryKeys: [
    'inputs-section',
    'inputs-section__cells',
    'inputs-section__description',
    'inputs-section__title-h3',
    'inputs-section__title-open-button',
    'inputs-section__options',
    'inputs-section__title',
  ],
  mockDependencies: {
    lfFramework: true,
    lfButton: true,
    workflow: true,
  },
};

describe('Inputs Memory Leak Tests', () => {
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

  createMemoryLeakTests(inputsConfig);
});
