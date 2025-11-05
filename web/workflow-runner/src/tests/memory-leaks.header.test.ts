import { vi } from 'vitest';

// Mock getLfFramework to satisfy imports in the service module
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((...args: string[]) => args.join('-')),
      get: {
        icon: vi.fn((iconName: string) => {
          const iconMap: Record<string, string> = {
            menu2: 'menu-2',
            alertTriangle: 'alert-triangle',
            check: 'check',
            hourglassLow: 'hourglass-low',
          };
          return iconMap[iconName] || 'test-icon';
        }),
        icons: vi.fn(() => ({
          alertTriangle: 'alert-triangle',
          check: 'check',
          hourglassLow: 'hourglass-low',
        })),
      },
    },
    sanitizeProps: vi.fn((props: any) => props),
  })),
}));

import { createHeaderSection } from '../elements/layout.header';
import { createMemoryLeakTests, type ComponentMemoryLeakConfig } from './memory-leak-utils';

// Configuration for header component memory leak tests
const headerConfig: ComponentMemoryLeakConfig = {
  componentName: 'Header',
  createController: createHeaderSection,
  expectedRegistryKeys: [
    'header-section',
    'header-section-app-message',
    'header-section-drawer-toggle',
  ],
  expectedRemoveKeys: [
    'header-section',
    'header-section-app-message',
    'header-section-container',
    'header-section-drawer-toggle',
    'header-section-server-indicator',
    'header-section-server-indicator-counter',
    'header-section-server-indicator-light',
  ],
};

// Generate comprehensive memory leak tests for the header component
createMemoryLeakTests(headerConfig);
