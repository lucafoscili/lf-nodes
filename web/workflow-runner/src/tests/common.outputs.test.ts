import { describe, expect, it } from 'vitest';
import { WorkflowCellsOutputContainer, WorkflowNodeResults } from '../types/api';
import { RunRecord } from '../types/client';
import { deepMerge, recordToUI } from '../utils/common';

describe('deepMerge output payloads', () => {
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
});
