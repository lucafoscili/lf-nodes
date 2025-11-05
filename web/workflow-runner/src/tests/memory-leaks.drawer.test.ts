import { vi } from 'vitest';

// Mock getLfFramework to satisfy imports in the service module
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    theme: {
      bemClass: vi.fn((...args: string[]) => args.join('-')),
      get: {
        icon: vi.fn((iconName: string) => {
          const iconMap: Record<string, string> = {
            imageInPicture: 'image-in-picture',
            bug: 'bug',
            brandGithub: 'brand-github',
          };
          return iconMap[iconName] || 'test-icon';
        }),
        icons: vi.fn(() => ({
          article: 'article',
          listTree: 'list-tree',
          alertTriangle: 'alert-triangle',
          codeCircle2: 'code-circle-2',
          photo: 'photo',
          json: 'json',
          robot: 'robot',
          wand: 'wand',
          imageInPicture: 'image-in-picture',
          bug: 'bug',
          brandGithub: 'brand-github',
        })),
      },
    },
    syntax: { json: { parse: async () => null } },
  })),
}));

import { createDrawerSection } from '../elements/layout.drawer';
import { createMemoryLeakTests, type ComponentMemoryLeakConfig } from './memory-leak-utils';

// Configuration for drawer component memory leak tests
const drawerConfig: ComponentMemoryLeakConfig = {
  componentName: 'Drawer',
  createController: createDrawerSection,
  expectedRegistryKeys: ['drawer-section', 'drawer-section-tree', 'drawer-section-button-debug'],
  expectedRemoveKeys: [
    'drawer-section',
    'drawer-section-button-comfyui',
    'drawer-section-button-debug',
    'drawer-section-button-github',
    'drawer-section-container',
    'drawer-section-footer',
    'drawer-section-tree',
  ],
};

// Generate comprehensive memory leak tests for the drawer component
createMemoryLeakTests(drawerConfig);
