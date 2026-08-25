import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: () => ({
    syntax: {
      json: {
        parse: async (response: Response) => response.json(),
      },
    },
  }),
}));

import { uploadWorkflowFiles } from '../services/workflow-service';

describe('workflow-service durable uploads', () => {
  const realFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = realFetch;
    vi.restoreAllMocks();
  });

  it('selects Comfy input storage before sending every file part', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          message: 'Upload successful.',
          payload: { paths: ['portrait.png [input]', 'pose.png [input]'] },
          status: 'success',
        }),
        { headers: { 'Content-Type': 'application/json' }, status: 200 },
      ),
    );
    const files = [
      new File(['portrait'], 'portrait.png', { type: 'image/png' }),
      new File(['pose'], 'pose.png', { type: 'image/png' }),
    ];

    const result = await uploadWorkflowFiles(files);

    expect(result.payload.paths).toEqual(['portrait.png [input]', 'pose.png [input]']);
    const [, request] = vi.mocked(globalThis.fetch).mock.calls[0];
    expect(request?.method).toBe('POST');
    expect(request?.body).toBeInstanceOf(FormData);
    const parts: Array<[string, FormDataEntryValue]> = [];
    (request?.body as FormData).forEach((value, name) => parts.push([name, value]));
    expect(parts.map(([name]) => name)).toEqual(['directory', 'file', 'file']);
    expect(parts[0]).toEqual(['directory', 'input']);
    expect((parts[1][1] as File).name).toBe('portrait.png');
    expect((parts[2][1] as File).name).toBe('pose.png');
  });
});
