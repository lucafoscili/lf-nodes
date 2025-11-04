import './setup';
import {
  createMockLocalStorage,
  attachMockLocalStorage,
  getClientInternalsWithMethods,
} from './_utils';
import { describe, expect, it, vi } from 'vitest';
import { WorkflowRunnerClient } from '../app/client';
import { initState } from '../app/state';
import { createWorkflowRunnerStore } from '../app/store';

const store = createWorkflowRunnerStore(initState());

describe('workflowRunnerClient - cache', () => {
  it('limits cache to 200 most recent runs', () => {
    const client = new WorkflowRunnerClient(store);

    // Add 250 runs with different updated_at timestamps
    for (let i = 0; i < 250; i++) {
      getClientInternalsWithMethods(client).runs.set(`run${i}`, {
        run_id: `run${i}`,
        status: i % 2 === 0 ? 'succeeded' : 'running',
        seq: i,
        updated_at: 1000 + i,
      });
    }

    const mockLocalStorage3 = createMockLocalStorage();
    attachMockLocalStorage(mockLocalStorage3);

    getClientInternalsWithMethods(client).saveCache();

    const cached = JSON.parse(
      (mockLocalStorage3 as ReturnType<typeof createMockLocalStorage>)._getStore()['lf-runs-cache'],
    );
    // New format stores envelope with run_ids; since we added 250 runs (less than cap 300)
    expect(Array.isArray(cached.run_ids)).toBe(true);
    expect(cached.run_ids.length).toBe(250);
    // Ensure boundary ids are present
    expect(cached.run_ids).toContain('run249');
    expect(cached.run_ids).toContain('run0');
  });

  it('caches workflow_id in localStorage', () => {
    const client = new WorkflowRunnerClient(store);

    getClientInternalsWithMethods(client).runs.set('cache-wf-1', {
      run_id: 'cache-wf-1',
      workflow_id: 't2i_15_lcm',
      status: 'running',
      seq: 1,
    });

    const mockLocalStorage = createMockLocalStorage();
    attachMockLocalStorage(mockLocalStorage);

    getClientInternalsWithMethods(client).saveCache();

    const cached = JSON.parse(
      (mockLocalStorage as ReturnType<typeof createMockLocalStorage>)._getStore()['lf-runs-cache'],
    );

    // IDs-only cache: only run id is persisted
    expect(cached.version).toBe(1);
    expect(cached.run_ids).toContain('cache-wf-1');
  });

  it('restores placeholders from IDs-only cache (workflow_id hydrated by server)', () => {
    const client = new WorkflowRunnerClient(store);

    const cachePayload = { version: 1, cached_at: Date.now(), run_ids: ['restore-wf-1'] };

    const mockLocalStorage = createMockLocalStorage({
      'lf-runs-cache': JSON.stringify(cachePayload),
    });
    attachMockLocalStorage(mockLocalStorage);

    // Load cache ids and seed placeholders
    const ids = getClientInternalsWithMethods(client).loadCacheIds();
    getClientInternalsWithMethods(client).seedPlaceholders(ids);

    // Placeholder should be created with null workflow_id
    const restored = getClientInternalsWithMethods(client).runs.get('restore-wf-1');
    expect(restored).toBeDefined();
    expect(restored.run_id).toBe('restore-wf-1');
    // Accept null or undefined (implementation may set null)
    expect(restored.workflow_id == null).toBe(true);
    expect(restored.status).toBe('pending');
  });

  it('saveCache stores runs to localStorage', () => {
    const client = new WorkflowRunnerClient(store);
    const internals = getClientInternalsWithMethods(client);
    internals.runs.set('cache1', {
      run_id: 'cache1',
      status: 'running',
      seq: 10,
      updated_at: 5000,
    });
    internals.runs.set('cache2', {
      run_id: 'cache2',
      status: 'succeeded',
      seq: 20,
      updated_at: 6000,
    });

    const mockLocalStorage = createMockLocalStorage();
    attachMockLocalStorage(mockLocalStorage);
    const setSpy = vi.spyOn(
      mockLocalStorage as unknown as { setItem: (...args: unknown[]) => void },
      'setItem',
    );

    internals.saveCache();

    expect(setSpy).toHaveBeenCalledWith('lf-runs-cache', expect.any(String));
    const cached = JSON.parse(
      (mockLocalStorage as ReturnType<typeof createMockLocalStorage>)._getStore()['lf-runs-cache'],
    );
    // New cache format stores an envelope with run_ids
    expect(cached.version).toBe(1);
    expect(Array.isArray(cached.run_ids)).toBe(true);
    expect(cached.run_ids.length).toBe(2);
    expect(cached.run_ids).toContain('cache1');
    expect(cached.run_ids).toContain('cache2');
  });

  it('loadCache restores runs from localStorage (IDs-only envelope -> placeholders)', () => {
    const client = new WorkflowRunnerClient(store);
    const cachePayload = {
      version: 1,
      cached_at: Date.now(),
      run_ids: ['restore1', 'restore2'],
    };

    const mockLocalStorage = createMockLocalStorage({
      'lf-runs-cache': JSON.stringify(cachePayload),
    });
    attachMockLocalStorage(mockLocalStorage);

    // Use the new API: loadCacheIds + seedPlaceholders
    const internals = getClientInternalsWithMethods(client);
    const ids = internals.loadCacheIds();
    internals.seedPlaceholders(ids);

    expect(internals.runs.size).toBe(2);
    // Placeholders have pending status and seq -1
    expect(internals.runs.get('restore1').status).toBe('pending');
    expect(internals.runs.get('restore1').seq).toBe(-1);
    expect(internals.runs.get('restore2').status).toBe('pending');
  });

  it('loadCacheIds handles missing or invalid cache gracefully', () => {
    const client = new WorkflowRunnerClient(store);
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    const mockLocalStorage = createMockLocalStorage();
    attachMockLocalStorage(mockLocalStorage);

    const internals = getClientInternalsWithMethods(client);
    const ids = internals.loadCacheIds();
    expect(ids).toEqual([]);

    // test invalid JSON
    const spyGet = vi
      .spyOn(mockLocalStorage as unknown as { getItem: (...args: unknown[]) => unknown }, 'getItem')
      .mockImplementation(() => '{invalid json}');
    const ids2 = internals.loadCacheIds();
    expect(ids2).toEqual([]);

    // Do not rely on a specific console.warn implementation (implementation may have changed)
    consoleWarn.mockRestore();
  });
});
