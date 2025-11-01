import { describe, it, expect } from 'vitest';
import { normalizeRoute } from '../app/routing';
import { initState } from '../app/state';
import { WorkflowRoute, WorkflowState } from '../types/state';

const createState = (overrides: Partial<WorkflowState> = {}): WorkflowState => {
  const base = initState();
  return Object.assign(base, overrides);
};

const createWorkflowNode = (id: string) =>
  ({
    id,
    category: 'test',
    title: `Workflow ${id}`,
    children: [],
  } as any);

describe('routing.normalize', () => {
  it('normalizes run routes to include valid workflow and clearResults=false', () => {
    const state = createState({
      workflows: { nodes: [createWorkflowNode('wf-1')] } as any,
      runs: [
        {
          runId: 'run-1',
          createdAt: 0,
          updatedAt: 1,
          status: 'running',
          workflowId: 'wf-1',
          workflowName: 'Test workflow',
          inputs: {},
          outputs: null,
          error: null,
          httpStatus: null,
          resultPayload: null,
        },
      ],
    });

    const input: WorkflowRoute = { view: 'run', runId: 'run-1', workflowId: 'missing' };
    const result = normalizeRoute(input, state);

    expect(result.route.view).toBe('run');
    expect(result.route.runId).toBe('run-1');
    expect(result.route.workflowId).toBe('wf-1');
    expect(result.clearResults).toBe(false);
  });

  it('downgrades run view to workflow when run is missing', () => {
    const state = createState({
      current: { ...initState().current, id: 'wf-1', status: 'idle', message: '' },
      workflows: { nodes: [createWorkflowNode('wf-1')] } as any,
    });

    const result = normalizeRoute({ view: 'run', runId: 'missing' }, state);

    expect(result.route.view).toBe('workflow');
    expect(result.route.runId).toBeUndefined();
    expect(result.route.workflowId).toBe('wf-1');
    expect(result.clearResults).toBeUndefined();
  });

  it('home view strips workflow/run identifiers', () => {
    const state = createState({
      workflows: { nodes: [createWorkflowNode('wf-1')] } as any,
    });

    const result = normalizeRoute({ view: 'home', runId: 'run-1', workflowId: 'wf-1' }, state);

    expect(result.route.view).toBe('home');
    expect(result.route.workflowId).toBeUndefined();
    expect(result.route.runId).toBeUndefined();
  });
});
