import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { workflowDispatcher } from '../dispatchers/workflow';
import { MAIN_CLASSES } from '../elements/layout.main';
import { createInputsSection, INPUTS_CLASSES } from '../elements/main.inputs';
import { runWorkflow, WorkflowApiError } from '../services/workflow-service';
import type { WorkflowCellInput } from '../types/api';
import type { WorkflowCellStatus, WorkflowUICells } from '../types/section';
import type { WorkflowStore } from '../types/state';
import {
  getWorkflowSessionDraft,
  replaceWorkflowSessionDraft,
} from '../utils/session-drafts';

vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: () => ({
    theme: {
      bemClass: (block: string, element?: string) =>
        element ? `${block}__${element}` : block,
      get: { icon: () => 'test-icon' },
    },
    sanitizeProps: (props: unknown) => props,
  }),
}));
vi.mock('../handlers/button', () => ({ buttonHandler: vi.fn() }));
vi.mock('../utils/artifact-handoff', () => ({ consumeArtifactHandoff: () => null }));
vi.mock('../utils/debug', () => ({ debugLog: vi.fn() }));
vi.mock('../app/store-actions', () => ({
  addNotification: vi.fn(),
  clearResults: vi.fn(),
  ensureActiveRun: vi.fn(),
  setStatus: vi.fn(),
  upsertRun: vi.fn(),
}));
vi.mock('../services/workflow-service', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../services/workflow-service')>()),
  runWorkflow: vi.fn(async () => 'caption-run'),
}));

const createFixture = () => {
  const main = document.createElement('main');
  document.body.appendChild(main);
  const registry: Record<string, HTMLElement | WorkflowUICells> = {
    [MAIN_CLASSES._]: main,
  };
  const inputs: Record<string, WorkflowCellInput> = {
    endpoint: {
      id: 'endpoint',
      nodeId: '4',
      shape: 'textfield',
      props: { lfValue: '/api/lf-nodes/proxy/kobold' },
    },
    max_tokens: {
      id: 'max_tokens',
      nodeId: '4',
      shape: 'textfield',
      required: false,
      advanced: true,
      props: { lfValue: '2048' },
    },
  };
  const state = {
    current: { id: 'caption-image', message: null, status: 'idle' },
    inputStatuses: {} as Record<string, WorkflowCellStatus>,
    manager: {
      workflow: {
        current: () => ({ id: 'caption-image' }),
        cells: () => inputs,
        description: () => 'Describe an image.',
        title: () => 'Caption image',
      },
      uiRegistry: {
        get: () => registry,
        set: (key: string, value: HTMLElement | WorkflowUICells) => {
          registry[key] = value;
        },
        remove: (key: string) => {
          const element = registry[key];
          if (element instanceof HTMLElement) element.remove();
          delete registry[key];
        },
      },
    },
    mutate: {
      inputStatus: (id: string, status: WorkflowCellStatus) => {
        state.inputStatuses[id] = status;
      },
    },
  };
  const store = { getState: () => state } as unknown as WorkflowStore;
  const controller = createInputsSection(store);
  const mount = () => {
    controller.mount();
    const cells = registry[INPUTS_CLASSES.cells] as HTMLLfTextfieldElement[];
    // Exercise real component construction, registry, drafts, and dispatch;
    // only the custom elements' asynchronous value API is a host double.
    for (const cell of cells) cell.getValue = async () => String(cell.lfValue ?? '');
    return {
      budget: cells.find((cell) => cell.id === 'max_tokens')!,
      details: main.querySelector<HTMLDetailsElement>('details')!,
    };
  };
  return { controller, mount, state, store };
};

describe('Advanced input integration', () => {
  beforeEach(() => vi.clearAllMocks());
  afterEach(() => document.body.replaceChildren());

  it('restores, captures, and submits a collapsed advanced field through the ordinary registry', async () => {
    const { controller, mount, store } = createFixture();
    replaceWorkflowSessionDraft(store, 'caption-image', { max_tokens: '4096' });
    const { budget, details } = mount();
    // Finish mount hydration before simulating the next user interaction.
    await new Promise<void>((resolve) => setTimeout(resolve, 0));
    expect(budget.lfValue).toBe('4096');
    expect(details.open).toBe(false);

    budget.lfValue = '3072';
    budget.dispatchEvent(
      new CustomEvent('lf-textfield-event', { detail: { eventType: 'input' } }),
    );
    await vi.waitFor(() => {
      expect(getWorkflowSessionDraft(store, 'caption-image')?.max_tokens).toBe('3072');
    });
    await workflowDispatcher(store);

    expect(runWorkflow).toHaveBeenCalledWith({
      workflowId: 'caption-image',
      inputs: { endpoint: '/api/lf-nodes/proxy/kobold', max_tokens: '3072' },
      submissionId: expect.stringMatching(/^lf-web:/),
    });
    expect(details.open).toBe(false);
    controller.destroy();
  });

  it('reveals the advanced field when its submission receives a validation error', async () => {
    const { controller, mount, state, store } = createFixture();
    const { budget, details } = mount();
    budget.lfValue = '19';
    vi.mocked(runWorkflow).mockRejectedValueOnce(
      new WorkflowApiError('Invalid response budget.', {
        status: 400,
        payload: { error: { input: 'max_tokens' } },
      }),
    );

    await workflowDispatcher(store);
    controller.render();

    expect(state.inputStatuses.max_tokens).toBe('error');
    expect(details.open).toBe(true);
    expect(budget.parentElement?.dataset.status).toBe('error');
    controller.destroy();
  });
});
