import assert from 'node:assert/strict';
import test from 'node:test';

import { normalizeRoute } from '../routing';
import { initState } from '../state';
import { WorkflowRoute, WorkflowState } from '../../types/state';

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
  }) as any;

test('normalizes run routes to include valid workflow and clearResults=false', () => {
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

  assert.equal(result.route.view, 'run');
  assert.equal(result.route.runId, 'run-1');
  assert.equal(result.route.workflowId, 'wf-1');
  assert.equal(result.clearResults, false);
});

test('downgrades run view to workflow when run is missing', () => {
  const state = createState({
    current: { ...initState().current, id: 'wf-1', status: 'idle', message: '' },
    workflows: { nodes: [createWorkflowNode('wf-1')] } as any,
  });

  const result = normalizeRoute({ view: 'run', runId: 'missing' }, state);

  assert.equal(result.route.view, 'workflow');
  assert.equal(result.route.runId, undefined);
  assert.equal(result.route.workflowId, 'wf-1');
  assert.equal(result.clearResults, undefined);
});

test('home view strips workflow/run identifiers', () => {
  const state = createState({
    workflows: { nodes: [createWorkflowNode('wf-1')] } as any,
  });

  const result = normalizeRoute({ view: 'home', runId: 'run-1', workflowId: 'wf-1' }, state);

  assert.equal(result.route.view, 'home');
  assert.equal(result.route.workflowId, undefined);
  assert.equal(result.route.runId, undefined);
});
