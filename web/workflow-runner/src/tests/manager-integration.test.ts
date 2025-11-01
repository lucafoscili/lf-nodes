import { describe, it, expect, vi, beforeEach } from 'vitest';
import { LfWorkflowRunnerManager } from '../app/manager';

// Mock window for Node environment
const mockWindow = {
  location: {
    href: 'http://localhost/',
    search: '',
    hash: '',
    pathname: '/',
    origin: 'http://localhost',
    protocol: 'http:',
    host: 'localhost',
    hostname: 'localhost',
    port: '',
  },
  history: {
    replaceState: vi.fn(),
    pushState: vi.fn(),
  },
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
} as unknown as Window & typeof globalThis;

Object.defineProperty(global, 'window', {
  value: mockWindow,
  writable: true,
});

// Mock DOM for Node environment
const mockHead = {
  appendChild: vi.fn((element) => element),
};

const mockAppRoot = {
  firstChild: null as Node | null,
  removeChild: vi.fn((child: Node) => child),
  appendChild: vi.fn((element) => element),
};

const mockDocumentElement = {
  querySelector: vi.fn((selector: string) => {
    if (selector === 'head') return mockHead;
    return null;
  }),
  setAttribute: vi.fn(),
  removeAttribute: vi.fn(),
};

const mockDocument = {
  body: {
    innerHTML: '',
  },
  documentElement: mockDocumentElement,
  querySelector: vi.fn((selector: string) => {
    if (selector === '#app') return mockAppRoot;
    return null;
  }),
  createElement: vi.fn((tagName: string) => ({
    tagName,
    style: {},
    className: '',
    title: '',
    lfIcon: '',
    lfStyling: '',
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    appendChild: vi.fn(),
  })),
  dispatchEvent: vi.fn(),
} as unknown as Document;

Object.defineProperty(global, 'document', {
  value: mockDocument,
  writable: true,
});

// Mock CustomEvent for Node environment
Object.defineProperty(global, 'CustomEvent', {
  value: class CustomEvent {
    constructor(public type: string, public detail?: any) {}
  },
  writable: true,
});

// Mock localStorage for Node environment
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(global, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

// Mock requestAnimationFrame for Node environment
global.requestAnimationFrame = vi.fn((callback) => {
  setTimeout(callback, 0);
  return 0;
}) as unknown as typeof requestAnimationFrame;

describe('LfWorkflowRunnerManager - Client Integration', () => {
  beforeEach(() => {
    // Clear mocks
    mockLocalStorage.clear();
    mockDocument.body.innerHTML = '<div id="app"></div>';

    // Mock EventSource as proper class
    global.EventSource = class MockEventSource {
      addEventListener = vi.fn();
      close = vi.fn();
      onerror = null;
      onmessage = null;
      onopen = null;
      constructor(public url: string) {}
    } as unknown as typeof EventSource;

    // Mock fetch
    global.fetch = vi.fn().mockImplementation((url) => {
      // Mock workflows endpoint
      if (url.includes('/workflows')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              workflows: {
                nodes: [
                  { id: 'wf-1', name: 'Test Workflow 1' },
                  { id: 'wf-2', name: 'Test Workflow 2' },
                ],
              },
            }),
        });
      }

      // Mock runs endpoint (cold load)
      if (url.includes('/workflow-runner/runs')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              runs: [
                {
                  run_id: 'run-1',
                  workflow_id: 'wf-1',
                  status: 'succeeded',
                  seq: 5,
                  created_at: Date.now() - 10000,
                  updated_at: Date.now() - 5000,
                },
              ],
            }),
        });
      }

      return Promise.resolve({
        ok: false,
        status: 404,
        json: () => Promise.resolve({}),
      });
    });

    // Mock EventSource
    global.EventSource = vi.fn(() => ({
      addEventListener: vi.fn(),
      close: vi.fn(),
      onerror: null,
      onmessage: null,
      onopen: null,
    })) as any;
  });

  it('should bootstrap client exactly once', async () => {
    const manager = new LfWorkflowRunnerManager();

    // Wait for async initialization
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Client should be instantiated
    expect((manager as any)['#CLIENT']).toBeDefined();

    // EventSource should be called once (SSE connection)
    expect(global.EventSource).toHaveBeenCalledTimes(1);
  });

  it('should not use legacy realtime path', () => {
    const consoleWarnSpy = vi.spyOn(console, 'warn');

    const manager = new LfWorkflowRunnerManager();

    // Should not see deprecation warnings (means legacy path not used)
    const deprecationWarnings = consoleWarnSpy.mock.calls.filter(
      (call) => call[0].includes('DEPRECATED') || call[0].includes('deprecated'),
    );

    expect(deprecationWarnings.length).toBe(0);

    consoleWarnSpy.mockRestore();
  });

  it('should hydrate store with cold-loaded runs', async () => {
    const manager = new LfWorkflowRunnerManager();

    // Wait for workflows to load and client to start
    await new Promise((resolve) => setTimeout(resolve, 500));

    const store = (manager as any)['#STORE'];
    const state = store.getState();

    // Store should have runs from cold load
    expect(state.runs.length).toBeGreaterThan(0);

    const run = state.runs.find((r: any) => r.runId === 'run-1');
    expect(run).toBeDefined();
    expect(run?.workflowId).toBe('wf-1');
    expect(run?.status).toBe('succeeded');
  });

  it('should preload workflow names into client', async () => {
    const manager = new LfWorkflowRunnerManager();

    // Wait for workflows to load
    await new Promise((resolve) => setTimeout(resolve, 500));

    const client = (manager as any)['#CLIENT'];
    const workflowNames = (manager as any)['#WORKFLOW_NAMES'];

    // Workflow names should be populated
    expect(workflowNames.size).toBeGreaterThan(0);
    expect(workflowNames.get('wf-1')).toBe('Test Workflow 1');
    expect(workflowNames.get('wf-2')).toBe('Test Workflow 2');
  });

  it('should map RunRecord to UI state correctly', async () => {
    const manager = new LfWorkflowRunnerManager();

    await new Promise((resolve) => setTimeout(resolve, 500));

    const store = (manager as any)['#STORE'];
    const state = store.getState();

    const run = state.runs.find((r: any) => r.runId === 'run-1');

    // Should have all required UI fields
    expect(run?.runId).toBe('run-1');
    expect(run?.workflowId).toBe('wf-1');
    expect(run?.workflowName).toBeTruthy(); // Should resolve name
    expect(run?.status).toBe('succeeded');
    expect(run?.createdAt).toBeDefined();
    expect(run?.updatedAt).toBeDefined();
  });

  it('should clean up client on destroy', () => {
    const manager = new LfWorkflowRunnerManager();
    const client = (manager as any)['#CLIENT'];
    const stopSpy = vi.spyOn(client, 'stop');

    // Trigger cleanup via uiRegistry.delete()
    manager.uiRegistry.delete();

    expect(stopSpy).toHaveBeenCalledTimes(1);
  });
});
