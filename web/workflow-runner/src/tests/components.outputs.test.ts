import { describe, expect, it, vi } from 'vitest';
import { createOutputComponent } from '../elements/components';
import { WorkflowCellOutput } from '../types/api';

vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: vi.fn(() => ({
    sanitizeProps: vi.fn((props: unknown) => props),
  })),
}));

describe('createOutputComponent standard Comfy artifacts', () => {
  it('renders a native before-and-after comparison from the Display JSON envelope', () => {
    const dataset = {
      nodes: [
        {
          cells: {
            lfImage: { shape: 'image', lfValue: '/view?filename=before.png&type=temp' },
            lfImage_after: { shape: 'image', lfValue: '/view?filename=after.png&type=temp' },
          },
          id: 'image_1',
          value: 'Comparison 1',
        },
      ],
    };
    const component = createOutputComponent({
      id: 'comparison',
      nodeId: 'display_comparison',
      shape: 'compare',
      json: dataset,
      props: { lfShape: 'image', lfView: 'main' },
    } as unknown as WorkflowCellOutput);

    const compare = component.querySelector('lf-compare') as HTMLElement & {
      lfDataset?: unknown;
      lfShape?: string;
      lfView?: string;
    };
    expect(compare).toBeTruthy();
    expect(compare.className).toBe('workflow-output-compare');
    expect(compare.lfDataset).toBe(dataset);
    expect(compare.lfShape).toBe('image');
    expect(compare.lfView).toBe('main');
    expect(component.querySelector('lf-masonry')).toBeNull();
  });

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
    expect(image?.parentElement?.querySelector('a')?.hasAttribute('download')).toBe(false);
  });

  it.each([
    '//example.invalid/steal.png',
    '/untrusted/artifact.png',
    '/view?filename=other.png&subfolder=input&type=input',
  ])(
    'derives the artifact URL from its descriptor instead of trusting: %s',
    (url) => {
      const component = createOutputComponent({
        id: 'image',
        nodeId: 'save',
        shape: 'masonry',
        images: [{ filename: 'safe.png', subfolder: 'renders', type: 'output', url }],
      } as WorkflowCellOutput);

      expect(component.querySelector('img')?.getAttribute('src')).toBe(
        '/view?filename=safe.png&subfolder=renders&type=output',
      );
    },
  );

  it('renders DDS file_names as safe downloads without creating a broken image preview', () => {
    const component = createOutputComponent({
      id: 'dds',
      nodeId: 'save',
      shape: 'masonry',
      file_names: ['LF_Nodes/converted.dds'],
    } as WorkflowCellOutput);

    expect(component.querySelector('img')).toBeNull();
    expect(component.textContent).toContain('Preview is not available in the browser.');
    const link = component.querySelector('a');
    expect(link?.textContent).toBe('Download converted.dds');
    expect(link?.download).toBe('converted.dds');
    expect(link?.getAttribute('href')).toBe(
      '/view?filename=converted.dds&subfolder=LF_Nodes&type=output',
    );
  });

  it.each(['glb', 'gltf', 'ply', 'splat', 'spz', 'ksplat'])(
    'renders standard 3d %s artifacts as safe downloads without a broken preview',
    (extension) => {
      const component = createOutputComponent({
        id: 'model',
        nodeId: 'save',
        shape: 'masonry',
        '3d': [
          {
            filename: `asset.${extension}`,
            subfolder: 'workflow-runner/3d',
            type: 'output',
          },
        ],
      } as WorkflowCellOutput);

      expect(component.querySelector('img')).toBeNull();
      expect(component.querySelector('audio')).toBeNull();
      expect(component.querySelector('video')).toBeNull();
      expect(component.textContent).toContain('Preview is not available in the browser.');
      const link = component.querySelector('a');
      expect(link?.textContent).toBe(`Download asset.${extension}`);
      expect(link?.download).toBe(`asset.${extension}`);
      expect(link?.getAttribute('href')).toBe(
        `/view?filename=asset.${extension}&subfolder=workflow-runner%2F3d&type=output`,
      );
    },
  );

  it('does not turn unsafe file_names into links', () => {
    const component = createOutputComponent({
      id: 'files',
      nodeId: 'save',
      shape: 'masonry',
      file_names: ['../secret.dds', '/absolute.dds', 'nested\\escape.dds', 'safe.dds'],
    } as WorkflowCellOutput);

    const link = component.querySelector('a');
    expect(link?.textContent).toBe('Download safe.dds');
    expect(link?.getAttribute('href')).toBe('/view?filename=safe.dds&subfolder=&type=output');
    expect(component.querySelectorAll('a')).toHaveLength(1);
  });

  it('encodes URI-significant characters in a registered output-relative filename', () => {
    const component = createOutputComponent({
      id: 'model',
      nodeId: 'register',
      shape: 'code',
      file_names: ['LF_Nodes/100% #1?.glb'],
    } as WorkflowCellOutput);

    const link = component.querySelector('a');
    expect(link?.textContent).toBe('Download 100% #1?.glb');
    expect(link?.getAttribute('href')).toBe(
      '/view?filename=100%25+%231%3F.glb&subfolder=LF_Nodes&type=output',
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
