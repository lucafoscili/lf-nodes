import { describe, expect, it } from 'vitest';
import { WorkflowCellsOutputContainer, WorkflowNodeResults } from '../types/api';
import { deepMerge } from '../utils/common';

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
    } as WorkflowNodeResults;

    expect(deepMerge(definitions, outputs)[0].images).toEqual(outputs.save.images);
  });
});
