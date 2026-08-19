import { describe, expect, it, vi } from 'vitest';
import { createOutputComponent } from '../elements/components';
import { WorkflowCellOutput } from '../types/api';

vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    sanitizeProps: vi.fn((props: unknown) => props),
  })),
}));

describe('createOutputComponent standard Comfy artifacts', () => {
  it('renders MP4 artifacts as phone-friendly native video', () => {
    const component = createOutputComponent({
      id: 'video',
      nodeId: 'save',
      shape: 'masonry',
      images: [
        {
          filename: 'seed-42-f124_00001_.mp4',
          subfolder: 'workflow-runner/minimax_h3_i2v',
          type: 'output',
        },
      ],
    } as WorkflowCellOutput);

    const video = component.querySelector('video');
    expect(video instanceof HTMLVideoElement).toBe(true);
    expect(video?.controls).toBe(true);
    expect(video?.playsInline).toBe(true);
    expect(video?.preload).toBe('metadata');
    expect(video?.getAttribute('src')).toBe(
      '/view?filename=seed-42-f124_00001_.mp4&subfolder=workflow-runner%2Fminimax_h3_i2v&type=output',
    );
  });

  it('renders ordinary image artifacts through the same view endpoint', () => {
    const component = createOutputComponent({
      id: 'image',
      nodeId: 'save',
      shape: 'masonry',
      images: [{ filename: 'portrait.png', subfolder: '', type: 'temp' }],
    } as WorkflowCellOutput);

    const image = component.querySelector('img');
    expect(image?.alt).toBe('portrait.png');
    expect(image?.getAttribute('src')).toBe(
      '/view?filename=portrait.png&subfolder=&type=temp',
    );
  });

  it.each(['wav', 'mp3', 'm4a', 'flac', 'ogg', 'opus'])('renders %s artifacts as native audio', (extension) => {
    const component = createOutputComponent({
      id: 'audio',
      nodeId: 'save',
      shape: 'masonry',
      audios: [{ filename: `mix.${extension}`, subfolder: '', type: 'output' }],
    } as WorkflowCellOutput);

    const audio = component.querySelector('audio');
    expect(audio instanceof HTMLAudioElement).toBe(true);
    expect(audio?.controls).toBe(true);
    expect(audio?.preload).toBe('metadata');
    expect(audio?.getAttribute('src')).toBe(
      `/view?filename=mix.${extension}&subfolder=&type=output`,
    );
    expect(component.querySelector('img')).toBeNull();
  });

  it('renders raw Comfy singular audio output and does not fall back to an image', () => {
    const component = createOutputComponent({
      id: 'audio',
      nodeId: 'save',
      shape: 'masonry',
      audio: [{ filename: 'raw-output.m4a', subfolder: 'audio', type: 'output' }],
    } as WorkflowCellOutput);

    const audio = component.querySelector('audio');
    expect(audio instanceof HTMLAudioElement).toBe(true);
    expect(audio?.controls).toBe(true);
    expect(audio?.getAttribute('src')).toBe(
      '/view?filename=raw-output.m4a&subfolder=audio&type=output',
    );
    expect(component.querySelector('img')).toBeNull();
  });

  it('preserves legacy structured output when standard media is also present', () => {
    const dataset = { nodes: [{ id: 'metadata', value: 'seed-42' }] };
    const component = createOutputComponent({
      id: 'mixed',
      nodeId: 'save',
      shape: 'masonry',
      images: [{ filename: 'portrait.png', subfolder: '', type: 'output' }],
      dataset,
    } as WorkflowCellOutput);

    expect(component.querySelector('img')?.getAttribute('src')).toContain('portrait.png');
    const masonry = component.querySelector('lf-masonry') as HTMLElement & {
      lfDataset?: unknown;
    };
    expect(masonry).toBeTruthy();
    expect(masonry.lfDataset).toBe(dataset);
  });
});
