import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BACKUP_API } from './backup';

const mocks = vi.hoisted(() => ({
  fetchApi: vi.fn(),
  log: vi.fn(),
}));

vi.mock('../utils/common', () => ({
  getComfyAPI: () => ({ fetchApi: mocks.fetchApi }),
  getLfManager: () => ({ getBackupRetention: () => 5, log: mocks.log }),
}));

beforeEach(() => {
  mocks.fetchApi.mockReset();
  mocks.fetchApi.mockResolvedValue({
    json: async () => ({ message: 'done', status: 'success' }),
    status: 200,
  } as Response);
});

describe('backup calls outlast the frontend abort', () => {
  it('lifts the fetch timeout for a new backup and for the cleanup', async () => {
    await BACKUP_API.new('manual');
    await BACKUP_API.cleanOld(3);

    const timeouts = mocks.fetchApi.mock.calls.map(([, options]) => options.timeoutMs);
    expect(timeouts).toEqual([null, null]);
  });
});
