/**
 * Test utilities and helpers for workflow-runner tests.
 *
 * Preferred test API:
 * - Use `client.getTestApi()` for accessing internal state/methods in tests.
 * - Use public getters like `client.getRuns()`, `client.getLastSeq()` for observable state.
 * - Use `getClientInternalsWithMethods(client)` as fallback if `getTestApi()` is unavailable.
 * - Avoid direct casts like `(client as any)`; prefer typed accessors.
 * - For seeded fixtures, minimal casts like `as RunRecord` are acceptable if the object has required fields.
 */
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import type { WorkflowState, WorkflowStore } from '../types/state';
import type {
  ClientInternals,
  ClientInternalsMethods,
  ResponseLike,
  SeedRunInput,
  SSEHandler,
  SSEPayload,
} from '../types/test-utils';

export class TestEventSource {
  static instances: TestEventSource[] = [];
  public listeners: Record<string, SSEHandler | null> = {};
  public onmessage: SSEHandler | null = null;
  public onopen: ((e?: unknown) => void) | null = null;
  public onerror: ((e?: unknown) => void) | null = null;

  constructor(public url: string) {
    TestEventSource.instances.push(this);
  }

  addEventListener(type: string, cb: SSEHandler) {
    this.listeners[type] = cb;
  }

  removeEventListener(type: string) {
    delete this.listeners[type];
  }

  close(): void {
    // no-op; tests call emit helpers instead
  }

  sendMessage(data: unknown): void {
    const evt: SSEPayload = { data: JSON.stringify(data) };
    const handler = this.listeners['message'] || this.onmessage;
    if (handler) handler(evt);
  }

  sendRun(type: string, data: unknown): void {
    const evt: SSEPayload = { data: JSON.stringify(data) };
    const handler = this.listeners[type] || this.onmessage;
    if (handler) handler(evt);
  }

  static reset(): void {
    TestEventSource.instances = [];
  }
}

export function setGlobalEventSourceMock(): void {
  const G = globalThis as unknown as Record<string, unknown>;
  G.TestEventSource = TestEventSource;
  G.EventSource = TestEventSource as unknown;
}

export function restoreGlobalEventSourceMock(): void {
  const G = globalThis as unknown as Record<string, unknown>;
  try {
    delete G.EventSource;
  } catch {
    /* ignore */
  }
  try {
    delete G.TestEventSource;
  } catch {
    /* ignore */
  }
  TestEventSource.reset();
}

export function createMockLocalStorage(initial: Record<string, string> = {}): Storage & {
  _getStore: () => Record<string, string>;
} {
  let store: Record<string, string> = { ...initial };
  const mock: Storage & { _getStore: () => Record<string, string> } = {
    length: 0,
    clear(): void {
      store = {};
    },
    getItem(key: string): string | null {
      return key in store ? store[key] : null;
    },
    key(_index: number): string | null {
      return null;
    },
    removeItem(key: string): void {
      delete store[key];
    },
    setItem(key: string, value: string): void {
      store[key] = String(value);
    },
    _getStore(): Record<string, string> {
      return store;
    },
  };
  return mock;
}

export function attachMockLocalStorage(
  mock: Storage & { _getStore?: () => Record<string, string> },
): void {
  const G = globalThis as unknown as Record<string, unknown> & { localStorage?: Storage };
  G.localStorage = mock;
}

export type FetchMock = ReturnType<typeof makeFetchMock>;
export function makeFetchMock(
  handler: (url: string, opts?: RequestInit) => ResponseLike | Promise<ResponseLike>,
): (url: string, opts?: RequestInit) => ResponseLike | Promise<ResponseLike> {
  const f = ((url: string, opts?: RequestInit) => handler(url, opts)) as (
    url: string,
    opts?: RequestInit,
  ) => ResponseLike | Promise<ResponseLike>;
  const G = globalThis as unknown as Record<string, unknown> & { fetch?: unknown };
  G.fetch = f;
  return f;
}

export function createTestStoreAndClient(): { store: WorkflowStore; client: WorkflowRunnerClient } {
  const store = createWorkflowRunnerStore(initState());
  const client = new WorkflowRunnerClient(store);
  return { store, client };
}

export function seedStoreRuns(store: WorkflowStore, runs: SeedRunInput[]): void {
  for (const r of runs) {
    if (store.setState) {
      store.setState((s: WorkflowState) => ({
        ...s,
        runs: [
          {
            runId: r.runId || r.run_id || '',
            workflowId: r.workflowId || r.workflow_id || null,
            workflowName: r.workflowName || '',
            status: r.status,
            createdAt: r.createdAt || r.created_at || Date.now(),
            updatedAt: r.updatedAt || r.updated_at || Date.now(),
            inputs: {},
            outputs: null,
            error: null,
            httpStatus: null,
          },
          ...(s.runs || []),
        ],
      }));
    }
  }
}

export const wait = (ms = 0) => new Promise<void>((r) => setTimeout(r, ms));

export function getClientInternals(client: WorkflowRunnerClient): ClientInternals {
  return client as unknown as ClientInternals;
}

export function getClientInternalsWithMethods(
  client: WorkflowRunnerClient,
): ClientInternals & ClientInternalsMethods {
  // Prefer explicit test API on the client when available to avoid
  // casting to unknown/any in tests. Fall back to the legacy cast for
  // older client versions.
  const anyClient = client as any;
  if (typeof anyClient.getTestApi === 'function') {
    return anyClient.getTestApi() as ClientInternals & ClientInternalsMethods;
  }

  return client as unknown as ClientInternals & ClientInternalsMethods;
}

export function createMinimalDocumentMock(): Document {
  const mockHead = {
    appendChild(element: Node) {
      return element;
    },
  } as unknown as HTMLHeadElement;

  const mockAppRoot = {
    firstChild: null as Node | null,
    removeChild(_child: Node) {
      const emptyNode = {} as unknown as Node;
      return emptyNode;
    },
    appendChild(_e: Node) {
      const emptyNode = {} as unknown as Node;
      return emptyNode;
    },
    prepend(_e: Node) {
      const emptyNode = {} as unknown as Node;
      return emptyNode;
    },
  };

  const mockDocumentElement = {
    querySelector(selector: string) {
      if (selector === 'head') return mockHead;
      return null;
    },
    setAttribute() {
      /* noop */
    },
    removeAttribute() {
      /* noop */
    },
  } as unknown as Document['documentElement'];

  const mockDocument = {
    body: { innerHTML: '' },
    documentElement: mockDocumentElement,
    querySelector(selector: string) {
      if (selector === '#app') return mockAppRoot as unknown as Element;
      if (selector === 'head') return mockHead as unknown as Element;
      return null;
    },
    createElement(tagName: string) {
      return {
        tagName,
        style: {},
        className: '',
        title: '',
        dataset: {},
        innerText: '',
        addEventListener() {
          /* noop */
        },
        removeEventListener() {
          /* noop */
        },
        appendChild() {
          /* noop */
        },
        prepend() {
          /* noop */
        },
        insertBefore() {
          /* noop */
        },
        classList: { add() {}, remove() {} },
      } as unknown as HTMLElement;
    },
    dispatchEvent() {
      /* noop */
    },
  } as unknown as Document;

  return mockDocument;
}

export function attachMockDocument(mock: Document): void {
  Object.defineProperty(globalThis, 'document', { value: mock, writable: true });
}
