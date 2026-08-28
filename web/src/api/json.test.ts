import { beforeEach, describe, expect, it, vi } from 'vitest';

import { JSON_API, serializeJSONUpdate } from './json';

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

const successfulUpdate = () =>
  ({
    json: async () => ({ message: 'updated', status: 'success' }),
    status: 200,
  } as Response);

beforeEach(() => {
  mocks.callerClientId = undefined;
  mocks.fetchApi.mockReset();
});

describe('serialized JSON updates', () => {
  it('keeps same-context writes in invocation order', async () => {
    let releaseFirst!: () => void;
    let markFirstStarted!: () => void;
    const firstGate = new Promise<void>((resolve) => {
      releaseFirst = resolve;
    });
    const firstStarted = new Promise<void>((resolve) => {
      markFirstStarted = resolve;
    });
    const order: string[] = [];

    const first = serializeJSONUpdate('session-a', async () => {
      order.push('first:start');
      markFirstStarted();
      await firstGate;
      order.push('first:end');
      return 1;
    });
    const second = serializeJSONUpdate('session-a', async () => {
      order.push('second:start');
      order.push('second:end');
      return 2;
    });

    await firstStarted;
    expect(order).toEqual(['first:start']);
    releaseFirst();
    await expect(Promise.all([first, second])).resolves.toEqual([1, 2]);
    expect(order).toEqual([
      'first:start',
      'first:end',
      'second:start',
      'second:end',
    ]);
  });

  it('does not serialize independent contexts behind each other', async () => {
    let releaseFirst!: () => void;
    let markFirstStarted!: () => void;
    let markSecondStarted!: () => void;
    const firstGate = new Promise<void>((resolve) => {
      releaseFirst = resolve;
    });
    const firstStarted = new Promise<void>((resolve) => {
      markFirstStarted = resolve;
    });
    const secondStarted = new Promise<void>((resolve) => {
      markSecondStarted = resolve;
    });
    const order: string[] = [];

    const first = serializeJSONUpdate('session-b', async () => {
      order.push('b:start');
      markFirstStarted();
      await firstGate;
      return 'b';
    });
    const second = serializeJSONUpdate('session-c', async () => {
      order.push('c:start');
      markSecondStarted();
      return 'c';
    });

    await Promise.all([firstStarted, secondStarted]);
    expect(order).toEqual(['b:start', 'c:start']);
    releaseFirst();
    await expect(Promise.all([first, second])).resolves.toEqual(['b', 'c']);
  });

  it('submits same-context dataset snapshots in invocation order', async () => {
    let releaseFirst!: () => void;
    let markFirstStarted!: () => void;
    const firstGate = new Promise<void>((resolve) => {
      releaseFirst = resolve;
    });
    const firstStarted = new Promise<void>((resolve) => {
      markFirstStarted = resolve;
    });
    const submitted: string[] = [];

    mocks.fetchApi.mockImplementation(async (_endpoint, options: RequestInit) => {
      const body = options.body as FormData;
      submitted.push(String(body.get('dataset')));
      if (submitted.length === 1) {
        markFirstStarted();
        await firstGate;
      }
      return successfulUpdate();
    });

    const dataset = { columns: [{ id: 'status', title: 'pending' }], nodes: [] };
    const first = JSON_API.update('context/session.json', dataset);
    dataset.columns[0].title = 'completed';
    const second = JSON_API.update('context/session.json', dataset);

    await firstStarted;
    expect(submitted.map((value) => JSON.parse(value))).toEqual([
      { columns: [{ id: 'status', title: 'pending' }], nodes: [] },
    ]);

    releaseFirst();
    await Promise.all([first, second]);
    expect(submitted.map((value) => JSON.parse(value))).toEqual([
      { columns: [{ id: 'status', title: 'pending' }], nodes: [] },
      { columns: [{ id: 'status', title: 'completed' }], nodes: [] },
    ]);
  });

  it('binds updates to the current caller without changing the serialized dataset', async () => {
    mocks.callerClientId = 'client-update';
    mocks.fetchApi.mockResolvedValueOnce(successfulUpdate());
    const dataset = {
      columns: [],
      nodes: [],
      owner_client_id: 'immutable-owner',
    };

    await JSON_API.update('context/session.json', dataset);

    const [, options] = mocks.fetchApi.mock.calls[0];
    const body = options.body as FormData;
    expect(body.get('caller_client_id')).toBe('client-update');
    expect(JSON.parse(String(body.get('dataset')))).toEqual(dataset);
  });
});

describe('JSON reads', () => {
  it('binds editor dataset reads to the current caller without changing the path', async () => {
    mocks.callerClientId = 'client-read';
    mocks.fetchApi.mockResolvedValueOnce({
      json: async () => ({ data: { nodes: [] }, status: 'success' }),
      status: 200,
    } as Response);

    await JSON_API.get('C:/ComfyUI/temp/session_edit_dataset.json');

    const [, options] = mocks.fetchApi.mock.calls[0];
    const body = options.body as FormData;
    expect(body.get('file_path')).toBe('C:/ComfyUI/temp/session_edit_dataset.json');
    expect(body.get('caller_client_id')).toBe('client-read');
  });
});

describe('editing dataset recovery', () => {
  it('forwards an exact serialized context capability when supplied', async () => {
    mocks.callerClientId = 'client-loader';
    mocks.fetchApi.mockResolvedValueOnce({
      json: async () => ({ data: null, status: 'success' }),
      status: 200,
    } as Response);

    await JSON_API.recoverEditDataset('73', 'C:/ComfyUI/temp/loader-context.json');

    const [, options] = mocks.fetchApi.mock.calls[0];
    const body = options.body as FormData;
    expect(body.get('node_id')).toBe('73');
    expect(body.get('context_id')).toBe('C:/ComfyUI/temp/loader-context.json');
    expect(body.get('caller_client_id')).toBe('client-loader');
  });

  it('forwards the current caller for node-scoped breakpoint recovery', async () => {
    mocks.fetchApi.mockResolvedValueOnce({
      json: async () => ({ data: null, status: 'success' }),
      status: 200,
    } as Response);

    await JSON_API.recoverEditDataset('441', undefined, 'client-a');

    const [, options] = mocks.fetchApi.mock.calls[0];
    const body = options.body as FormData;
    expect(body.get('node_id')).toBe('441');
    expect(body.has('context_id')).toBe(false);
    expect(body.get('caller_client_id')).toBe('client-a');
  });

  it('forwards exact breakpoint context and client together', async () => {
    mocks.fetchApi.mockResolvedValueOnce({
      json: async () => ({ data: null, status: 'success' }),
      status: 200,
    } as Response);

    await JSON_API.recoverEditDataset('441', 'C:/temp/breakpoint.json', 'client-b');

    const [, options] = mocks.fetchApi.mock.calls[0];
    const body = options.body as FormData;
    expect(body.get('context_id')).toBe('C:/temp/breakpoint.json');
    expect(body.get('caller_client_id')).toBe('client-b');
  });
});
