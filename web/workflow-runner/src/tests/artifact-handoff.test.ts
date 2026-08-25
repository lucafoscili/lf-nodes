import { describe, expect, it, vi } from 'vitest';
import { WorkflowAPIDataset } from '../types/api';
import { WorkflowStore } from '../types/state';
import {
  consumeArtifactHandoff,
  listCompatibleArtifactTargets,
  queueArtifactHandoff,
  WorkflowOutputArtifact,
} from '../utils/artifact-handoff';

const artifact = (overrides: Partial<WorkflowOutputArtifact> = {}): WorkflowOutputArtifact => ({
  schema: 'lf.workflow-artifact.v1',
  reference: {
    schema: 'lf.workflow-artifact-ref.v1',
    sourceRunId: 'source-run',
    artifactId: 'a'.repeat(64),
    filename: 'candidate.png',
  },
  filename: 'candidate.png',
  nodeId: '42',
  mediaType: 'image/png',
  available: true,
  ...overrides,
});

const workflows: WorkflowAPIDataset = {
  nodes: [
    {
      id: 'compare',
      value: 'Compare images',
      description: '',
      category: 'Image',
      children: [
        {
          id: 'compare:inputs',
          value: 'Inputs',
          cells: {
            image_a: {
              id: 'image_a',
              nodeId: '1',
              value: 'Image A',
              shape: 'upload',
              props: { lfHtmlAttributes: { accept: 'image/*' } },
            },
            audio: {
              id: 'audio',
              nodeId: '2',
              value: 'Audio',
              shape: 'upload',
              props: { lfHtmlAttributes: { accept: 'audio/*' } },
            },
          },
        },
      ],
    },
    {
      id: 'generic',
      value: 'Generic intake',
      description: '',
      category: 'Utility',
      children: [
        {
          id: 'generic:inputs',
          value: 'Inputs',
          cells: {
            file: { id: 'file', nodeId: '3', value: 'File', shape: 'upload' },
          },
        },
      ],
    },
    {
      id: 'missing-model',
      value: 'Unavailable intake',
      description: '',
      category: 'Utility',
      readiness: {
        status: 'setup_required',
        issues: [{ code: 'model_missing', message: 'Install the required model.' }],
      },
      children: [
        {
          id: 'missing-model:inputs',
          value: 'Inputs',
          cells: {
            file: { id: 'file', nodeId: '4', value: 'File', shape: 'upload' },
          },
        },
      ],
    },
  ],
};

describe('artifact handoff', () => {
  it('offers only compatible upload inputs in deterministic order', () => {
    expect(listCompatibleArtifactTargets(workflows, artifact())).toEqual([
      {
        workflowId: 'compare',
        workflowName: 'Compare images',
        inputId: 'image_a',
        inputName: 'Image A',
      },
      {
        workflowId: 'generic',
        workflowName: 'Generic intake',
        inputId: 'file',
        inputName: 'File',
      },
    ]);
    expect(
      listCompatibleArtifactTargets(workflows, artifact()).some(
        (target) => target.workflowId === 'missing-model',
      ),
    ).toBe(false);
    expect(listCompatibleArtifactTargets(workflows, artifact({ available: false }))).toEqual([]);
  });

  it('queues one opaque prefill and consumes it only in the selected workflow', () => {
    const state: any = {
      current: { id: 'source-workflow' },
      mutate: {
        workflow: vi.fn((id: string) => {
          state.current.id = id;
        }),
        selectRun: vi.fn(),
        results: vi.fn(),
        view: vi.fn(),
      },
    };
    const store = { getState: () => state } as WorkflowStore;
    const target = listCompatibleArtifactTargets(workflows, artifact())[0];

    queueArtifactHandoff(store, artifact(), target);

    expect(state.mutate.workflow).toHaveBeenCalledWith('compare');
    expect(consumeArtifactHandoff(store, 'other')).toBeNull();
    expect(consumeArtifactHandoff(store, 'compare')).toEqual({
      image_a: {
        schema: 'lf.workflow-upload-prefill.v1',
        reference: artifact().reference,
        names: ['candidate.png'],
        available: true,
      },
    });
    expect(consumeArtifactHandoff(store, 'compare')).toBeNull();
  });
});
