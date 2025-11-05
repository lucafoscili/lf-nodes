import { vi } from 'vitest';

// Mock getLfFramework to satisfy imports in the service module
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((...args: string[]) => args.join('-')),
      get: {
        icon: vi.fn(() => 'test-icon'),
        icons: vi.fn(() => ({
          article: 'article',
          listTree: 'list-tree',
        })),
      },
    },
  })),
}));

import { createMainSection } from '../elements/layout.main';
import { createMemoryLeakTests, type ComponentMemoryLeakConfig } from './memory-leak-utils';

// Configuration for main component memory leak tests
const mainConfig: ComponentMemoryLeakConfig = {
  componentName: 'Main',
  createController: createMainSection,
  expectedRegistryKeys: ['main-section'],
  expectedRemoveKeys: ['main-section', 'main-section-home'],
};

// Generate comprehensive memory leak tests for the main component
createMemoryLeakTests(mainConfig);
