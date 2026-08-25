import { describe, expect, it } from 'vitest';
import { WorkflowCellsOutputContainer, WorkflowNodeResults } from '../types/api';
import { RunRecord } from '../types/client';
import { deepMerge, recordToUI } from '../utils/common';

describe('deepMerge output payloads', () => {
  it('hydrates a comparison dataset from the LF history envelope', () => {
    const dataset = {
      nodes: [{ id: 'image_1', value: 'Comparison 1' }],
    };
    const definitions = {
      comparison: {
        id: 'comparison',
        nodeId: 'display_comparison',
        shape: 'compare',
      },
    } as unknown as WorkflowCellsOutputContainer;
    const outputs = {
      display_comparison: {
        lf_output: [{ json: dataset }],
      },
    } as unknown as WorkflowNodeResults;

    expect(deepMerge(definitions, outputs)[0]).toMatchObject({
      id: 'comparison',
      nodeId: 'display_comparison',
      shape: 'compare',
      json: dataset,
    });
  });

  it('preserves standard Comfy artifacts when lf_output is absent', () => {
    const definitions = {
      video: {
        id: 'video',
        nodeId: 'save',
        shape: 'masonry',
      },
    } as unknown as WorkflowCellsOutputContainer;
    const outputs = {
      save: {
        images: [
          {
            filename: 'seed-42.mp4',
            subfolder: 'workflow-runner/minimax_h3_i2v',
            type: 'output',
          },
        ],
      },
    } as unknown as WorkflowNodeResults;

    expect(deepMerge(definitions, outputs)[0].images).toEqual(outputs.save.images);
  });
});

describe('recordToUI output detail', () => {
  const summaryOutputs = {
    remix: {
      audio: [{ filename: 'mix.flac', type: 'output' }],
    },
  } as WorkflowNodeResults;

  it('prefers complete detail outputs over the bounded summary preview', () => {
    const detailOutputs = {
      ...summaryOutputs,
      output_reference: {
        lf_output: [{ string: 'audio/mix.flac [output]' }],
      },
    } as unknown as WorkflowNodeResults;
    const run = {
      run_id: 'run-remix',
      workflow_id: 'youtube_ace_step_remix',
      status: 'succeeded',
      seq: 3,
      outputs: summaryOutputs,
      result: {
        http_status: 200,
        body: { payload: { history: { outputs: detailOutputs } } },
      },
    } as RunRecord;

    expect(recordToUI(run).outputs).toEqual(detailOutputs);
  });

  it('falls back to the summary preview after detail is released', () => {
    const run = {
      run_id: 'run-remix',
      workflow_id: 'youtube_ace_step_remix',
      status: 'succeeded',
      seq: 3,
      outputs: summaryOutputs,
      result: null,
    } as RunRecord;

    expect(recordToUI(run).outputs).toEqual(summaryOutputs);
  });

  it('does not erase locally submitted inputs when a summary omits them', () => {
    const run = {
      run_id: 'run-remix',
      workflow_id: 'youtube_ace_step_remix',
      status: 'running',
      seq: 2,
    } as RunRecord;

    expect(recordToUI(run).inputs).toBeUndefined();
  });

  it('normalizes legacy milliseconds and current seconds to one browser unit', () => {
    const legacy = recordToUI({
      run_id: 'legacy',
      status: 'failed',
      created_at: 1_763_168_015_000,
      updated_at: 1_763_168_073_000,
    } as RunRecord);
    const current = recordToUI({
      run_id: 'current',
      status: 'succeeded',
      created_at: 1_786_848_000,
      updated_at: 1_786_848_001,
    } as RunRecord);

    expect(legacy.createdAt).toBe(1_763_168_015_000);
    expect(current.createdAt).toBe(1_786_848_000_000);
    expect(current.createdAt).toBeGreaterThan(legacy.createdAt);
  });

  it('keeps invalid or missing creation times at the end of history', () => {
    const mapped = recordToUI({
      run_id: 'invalid-time',
      status: 'failed',
      created_at: Number.NaN,
      updated_at: Number.POSITIVE_INFINITY,
    } as RunRecord);

    expect(mapped.createdAt).toBe(0);
    expect(mapped.updatedAt).toBe(0);

    const negative = recordToUI({
      run_id: 'negative-time',
      status: 'failed',
      created_at: -1,
      updated_at: -1,
    } as RunRecord);
    expect(negative.createdAt).toBe(0);
    expect(negative.updatedAt).toBe(0);
  });
});
