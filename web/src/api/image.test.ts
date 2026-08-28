import { beforeEach, describe, expect, it, vi } from 'vitest';

import { IMAGE_API } from './image';

const mocks = vi.hoisted(() => ({
  callerClientId: undefined as string | undefined,
  fetchApi: vi.fn(),
  log: vi.fn(),
}));

vi.mock('../utils/common', () => ({
  getComfyAPI: () => ({ fetchApi: mocks.fetchApi }),
  getComfyClientId: () => mocks.callerClientId,
  getLfManager: () => ({ log: mocks.log }),
}));

beforeEach(() => {
  mocks.callerClientId = undefined;
  mocks.fetchApi.mockReset();
});

describe('image editor processing authority', () => {
  it('sends the current caller separately from processing settings', async () => {
    mocks.callerClientId = 'client-process';
    mocks.fetchApi.mockResolvedValueOnce({
      json: async () => ({ data: '/view?filename=result.png', status: 'success' }),
      status: 200,
    } as Response);
    const settings = {
      context_id: 'C:/ComfyUI/temp/session.json',
      strength: 0.5,
    } as never;

    await IMAGE_API.process('/view?filename=source.png', 'brightness', settings);

    const [, options] = mocks.fetchApi.mock.calls[0];
    const body = options.body as FormData;
    expect(body.get('caller_client_id')).toBe('client-process');
    expect(body.get('context_id')).toBe('C:/ComfyUI/temp/session.json');
    expect(JSON.parse(String(body.get('settings')))).toEqual(settings);
  });

  it('keeps stateless filters context-free while still identifying the caller', async () => {
    mocks.callerClientId = 'client-stateless';
    mocks.fetchApi.mockResolvedValueOnce({
      json: async () => ({ data: '/view?filename=result.png', status: 'success' }),
      status: 200,
    } as Response);

    await IMAGE_API.process('/view?filename=source.png', 'brightness', {} as never);

    const [, options] = mocks.fetchApi.mock.calls[0];
    const body = options.body as FormData;
    expect(body.get('caller_client_id')).toBe('client-stateless');
    expect(body.has('context_id')).toBe(false);
  });
});
