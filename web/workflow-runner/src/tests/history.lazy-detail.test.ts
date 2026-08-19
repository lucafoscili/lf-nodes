import './setup';
import { describe, expect, it } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';
import { getFirstOutputMediaUrl } from '../elements/main.outputs';
import { RunRecord } from '../types/client';
import { getClientInternalsWithMethods, makeFetchMock } from './_utils';


const previewOutputs = {
  save: {
    images: [
      {
        filename: 'maeva.png',
        subfolder: 'velora/history',
        type: 'output',
        url: '/view?filename=maeva.png&subfolder=velora%2Fhistory&type=output',
      },
    ],
  },
};


describe('history summary/detail boundary', () => {
  it('renders a history preview from the summary artifact URL', () => {
    expect(getFirstOutputMediaUrl(previewOutputs)).toBe(
      '/view?filename=maeva.png&subfolder=velora%2Fhistory&type=output',
    );
  });

  it('fetches one full result only when one run detail is requested', async () => {
    const store = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(store);
    const summary: RunRecord = {
      run_id: 'run-maeva',
      workflow_id: 'portrait',
      status: 'succeeded',
      seq: 3,
      outputs: previewOutputs,
    };
    getClientInternalsWithMethods(client).processSnapshotArray([summary]);

    let detailFetches = 0;
    makeFetchMock(async (url: string) => {
      if (url.endsWith('/run/run-maeva/status')) {
        detailFetches += 1;
        return {
          ok: true,
          status: 200,
          json: async () => ({
            ...summary,
            result: {
              http_status: 200,
              body: {
                payload: {
                  history: {
                    outputs: {
                      save: {
                        images: [
                          {
                            filename: 'maeva.png',
                            subfolder: 'velora/history',
                            type: 'output',
                          },
                        ],
                      },
                      metadata: { lf_output: [{ metadata: 'detail-only-base64' }] },
                    },
                  },
                },
              },
            },
          }),
        };
      }
      return { ok: false, status: 404 };
    });

    const first = client.loadRunDetail('run-maeva');
    const second = client.loadRunDetail('run-maeva');
    await Promise.all([first, second]);
    await client.loadRunDetail('run-maeva');

    expect(detailFetches).toBe(1);
    expect(client.getRuns().get('run-maeva')?.result?.http_status).toBe(200);
    expect(store.getState().runs[0].resultPayload?.http_status).toBe(200);
  });

  it('retains only the currently open heavyweight detail payload', async () => {
    const store = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(store);
    const summaries: RunRecord[] = ['run-a', 'run-b'].map((run_id) => ({
      run_id,
      workflow_id: 'portrait',
      status: 'succeeded',
      seq: 3,
      outputs: previewOutputs,
    }));
    getClientInternalsWithMethods(client).processSnapshotArray(summaries);

    makeFetchMock(async (url: string) => {
      const runId = url.includes('run-a') ? 'run-a' : 'run-b';
      return {
        ok: true,
        status: 200,
        json: async () => ({
          ...summaries.find((run) => run.run_id === runId),
          result: {
            http_status: 200,
            body: { payload: { history: { outputs: {}, marker: `${runId}-detail` } } },
          },
        }),
      };
    });

    await client.loadRunDetail('run-a');
    await client.loadRunDetail('run-b');

    expect(client.getRuns().get('run-a')?.result).toBeNull();
    expect(client.getRuns().get('run-b')?.result?.http_status).toBe(200);
    expect(store.getState().runs.find((run) => run.runId === 'run-a')?.resultPayload).toBeNull();
  });

  it('uses the summary endpoint for reconciliation', async () => {
    const store = createWorkflowRunnerStore(initState());
    const client = new WorkflowRunnerClient(store);
    const urls: string[] = [];
    makeFetchMock(async (url: string) => {
      urls.push(url);
      return {
        ok: true,
        status: 200,
        json: async () => ({
          run_id: 'run-summary',
          workflow_id: 'portrait',
          status: 'running',
          seq: 2,
          outputs: {},
        }),
      };
    });

    getClientInternalsWithMethods(client).reconcileRun('run-summary');
    const pending = getClientInternalsWithMethods(client).inflightReconciles.get('run-summary');
    if (pending) {
      await pending;
    }

    expect(urls.filter((url) => url.includes('/run/run-summary/status'))).toEqual([
      '/api/lf-nodes/run/run-summary/status?detail=0',
    ]);
  });
});
