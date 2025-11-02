import { API_ROOT } from '../config';
import { EventPayload, RunRecord, UpdateHandler } from '../types/client';
import { WorkflowStore } from '../types/state';
import { recordToUI } from '../utils/common';
import { debugLog } from '../utils/debug';
import { ensureActiveRun, upsertRun } from './store-actions';

export class WorkflowRunnerClient {
  #ES: EventSource | null = null;
  #STORE: WorkflowStore;
  #WORKFLOW_NAMES: Record<string, string> = {};

  private lastSeq: Map<string, number> = new Map();
  private runs: Map<string, RunRecord> = new Map();
  private workflowNames: Map<string, string> = new Map();
  private pollingInterval = 3000; // FIXME: make configurable
  private pollingTimer: any = null;
  private pollAbortController: AbortController | null = null;
  private backoffMs = 1000;
  private maxBackoffMs = 30000;
  private connecting = false;
  private processingSnapshot = false;
  private cacheKey = 'lf-runs-cache';
  private inflightReconciles = new Map<string, Promise<void>>();

  constructor(store: WorkflowStore) {
    this.#STORE = store;
  }

  onUpdate = (runs: Map<string, RunRecord>) => {
    if (Object.keys(this.#WORKFLOW_NAMES).length === 0) {
      const workflows = this.#STORE.getState().workflows?.nodes || [];
      for (let i = 0; i < workflows.length; i++) {
        const w = workflows[i];
        this.#WORKFLOW_NAMES[w.id] = String(w.value);
      }
    }

    for (const rec of runs.values()) {
      const uiEntry = recordToUI(rec, this.#WORKFLOW_NAMES);
      upsertRun(this.#STORE, uiEntry);
    }

    ensureActiveRun(this.#STORE);
  };

  queueHandler = (pending: number, running: number) => {
    try {
      const state = this.#STORE.getState();
      const nr = pending + running;
      state.mutate.queuedJobs(nr);
    } catch (e) {
      debugLog('queueHandler error', 'informational', e);
    }
  };

  setUpdateHandler(h: UpdateHandler) {
    this.onUpdate = h;
  }

  setQueueHandler(h: (pending: number, running: number) => void) {
    this.queueHandler = h;
  }

  // Preload workflow names to avoid fetching them individually
  setWorkflowNames(names: Map<string, string>) {
    for (const [id, name] of names) {
      this.workflowNames.set(id, name);
    }
    // Emit update to refresh UI with names
    this.emitUpdate();
  }

  private emitUpdate() {
    if (this.onUpdate) this.onUpdate(new Map(this.runs));
    // Save to cache after each update for persistence across reloads
    this.saveCache();
  }

  // Reconcile server record for a run via REST (de-duplicated)
  private reconcileRun(run_id: string) {
    // De-dupe inflight reconciles
    if (this.inflightReconciles.has(run_id)) {
      return;
    }

    const promise = this._reconcileRunOnce(run_id)
      .catch(() => {
        // ignore transient errors
      })
      .finally(() => {
        this.inflightReconciles.delete(run_id);
      });

    this.inflightReconciles.set(run_id, promise);
  }

  private async _reconcileRunOnce(run_id: string): Promise<void> {
    try {
      const resp = await fetch(`${API_ROOT}/run/${encodeURIComponent(run_id)}/status`, {
        credentials: 'include',
      });

      if (resp.status === 404) {
        this.removeRun(run_id);
        return;
      }

      if (!resp || !resp.ok) {
        debugLog('reconcileRun: fetch failed', 'informational', resp?.status);
        return;
      }
      const data = await resp.json();
      const rec: RunRecord = {
        run_id: data.run_id,
        workflow_id: data.workflow_id,
        status: data.status,
        seq: data.seq || 0,
        owner_id: data.owner_id,
        created_at: data.created_at,
        updated_at: data.updated_at,
        result: data.result,
        error: data.error,
      };
      this.upsertRun(rec);
    } catch (e) {
      debugLog('reconcileRun error', 'warning', e);
      throw e;
    }
  }

  private applyEvent(ev: RunRecord) {
    // Validate mandatory fields
    if (!ev || !ev.run_id || typeof ev.status === 'undefined' || ev.status === null) {
      debugLog('applyEvent: invalid run record (missing run_id or status)', 'warning', ev);
      return;
    }

    const last = this.lastSeq.get(ev.run_id) ?? -1;
    // gap detection: if ev.seq > last+1 then reconcile first
    if (last >= 0 && ev.seq > last + 1) {
      // async reconcile; don't block applying this event but request authoritative state
      this.reconcileRun(ev.run_id);
    }

    // Upsert with seq monotonicity guard
    this.upsertRun(ev);
  }

  // Upsert with seq monotonicity guard and workflow name fetch
  private upsertRun(rec: RunRecord) {
    const last = this.lastSeq.get(rec.run_id) ?? -1;
    if (rec.seq <= last) return; // duplicate or older - don't regress seq

    // Accept record
    this.lastSeq.set(rec.run_id, rec.seq);
    this.runs.set(rec.run_id, rec);

    // Fetch workflow name if workflow_id is present but name is unknown
    if (rec.workflow_id && !this.workflowNames.has(rec.workflow_id)) {
      this.fetchWorkflowNames([rec.workflow_id]);
    }

    this.emitUpdate();
  }

  // Remove a run completely from state and cache (used when server returns 404)
  private removeRun(runId: string) {
    this.runs.delete(runId);
    this.lastSeq.delete(runId);
    this.emitUpdate(); // triggers push to UI and saveCache
  }

  private processSnapshotArray(arr: RunRecord[]) {
    // Replace/merge snapshot state. For each run, if snapshot.seq > lastSeq, accept it.
    const activeSet = new Set<string>();
    const missingWorkflowIds = new Set<string>();
    const runsMissingWorkflowId: string[] = [];
    for (const s of arr) {
      // validate snapshot entry
      if (!s || !s.run_id || typeof s.status === 'undefined' || s.status === null) {
        console.warn('processSnapshotArray: ignoring invalid snapshot entry', s);
        continue;
      }
      activeSet.add(s.run_id);
      const last = this.lastSeq.get(s.run_id) ?? -1;
      if (s.seq <= last) continue;
      this.lastSeq.set(s.run_id, s.seq);
      this.runs.set(s.run_id, s);
      if (s.workflow_id && !this.workflowNames.has(s.workflow_id)) {
        missingWorkflowIds.add(s.workflow_id);
      }
      if (!s.workflow_id) {
        // request authoritative run details later to populate workflow_id
        runsMissingWorkflowId.push(s.run_id);
      }
    }
    this.emitUpdate();

    // Reconciliation pass: any locally-known run that is marked 'running' but
    // not present in the snapshot likely finished while the client was
    // disconnected — fetch authoritative state once per snapshot/reconnect.
    (async () => {
      try {
        const toReconcile: string[] = [];
        for (const [id, rec] of this.runs.entries()) {
          if (rec.status === 'running' && !activeSet.has(id)) {
            toReconcile.push(id);
          }
        }
        for (const id of toReconcile) {
          // fire-and-forget; reconcileRun will update state when it completes
          this.reconcileRun(id);
        }
      } catch (e) {
        // keep reconciliation best-effort and silent on error
      }
      // fetch missing workflow names in batch (fire-and-forget)
      if (missingWorkflowIds.size > 0) {
        try {
          this.fetchWorkflowNames(Array.from(missingWorkflowIds));
        } catch (e) {
          // ignore fetch failures
        }
      }

      // For runs that arrived without workflow_id, reconcile authoritative state
      for (const runId of runsMissingWorkflowId) {
        try {
          this.reconcileRun(runId);
        } catch (e) {
          // ignore
        }
      }
    })();
  }

  // Fetch human-friendly workflow names for given ids and cache them
  private async fetchWorkflowNames(ids: string[]) {
    // filter out ids we already have
    const needs = ids.filter((id) => !!id && !this.workflowNames.has(id));
    if (needs.length === 0) return;
    try {
      const resp = await fetch(`${API_ROOT}/workflows?ids=${encodeURIComponent(needs.join(','))}`, {
        credentials: 'include',
      });
      if (!resp || !resp.ok) return;
      const data = await resp.json();
      // Normalize multiple possible shapes returned by the server:
      // - Array of {workflow_id, name}
      // - { workflows: [ { ... } ] }
      // - { workflows: { nodes: [ { id, value, ... } ] } }
      // - { workflows: { <id>: "name", ... } }
      let items: any[] = [];
      try {
        if (Array.isArray(data)) {
          items = data;
        } else if (data) {
          if (Array.isArray(data.workflows)) {
            items = data.workflows;
          } else if (data.items && Array.isArray(data.items)) {
            items = data.items;
          } else if (data.workflows && Array.isArray(data.workflows.nodes)) {
            // transform registry shape { workflows: { nodes: [...] } }
            items = data.workflows.nodes.map((n: any) => ({
              workflow_id: n.id ?? n.key ?? n.value,
              name: n.value ?? n.title ?? n.name,
            }));
          } else if (data.workflows && typeof data.workflows === 'object') {
            // transform mapping { workflows: { id: name, ... } } or objects
            for (const k of Object.keys(data.workflows)) {
              const v = data.workflows[k];
              if (typeof v === 'string') {
                items.push({ workflow_id: k, name: v });
              } else if (v && typeof v === 'object') {
                items.push({
                  workflow_id: v.id ?? k,
                  name: v.name ?? v.value ?? v.title ?? JSON.stringify(v),
                });
              }
            }
          }
        }
      } catch (e) {
        // Normalization failed — fall back to empty items to avoid breaking the UI
        debugLog('fetchWorkflowNames: failed to normalize response', 'warning', e);
        items = [];
      }

      if (!items || typeof items[Symbol.iterator] !== 'function') {
        // Ensure items is iterable
        items = [];
      }

      for (const it of items) {
        try {
          const id = it.workflow_id ?? it.id ?? it.workflowId ?? it.key;
          const name = it.name ?? it.title ?? it.workflow_name ?? it.value ?? null;
          if (id && name) this.workflowNames.set(id, name);
        } catch (e) {
          // be robust against malformed entries
          debugLog('fetchWorkflowNames: skipping malformed item', 'warning', e);
        }
      }
      // After populating names, emit an update so UI can re-render with names
      this.emitUpdate();
    } catch (e) {
      debugLog('fetchWorkflowNames error', 'warning', e);
    }
  }

  // Save active runs to localStorage (IDs-only for schema stability)
  private saveCache() {
    try {
      if (typeof localStorage === 'undefined') return;

      const ids = Array.from(this.runs.keys());
      const payload = {
        version: 1,
        cached_at: Date.now(),
        run_ids: ids.slice(-300), // cap to recent 300 runs
      };
      localStorage.setItem(this.cacheKey, JSON.stringify(payload));
    } catch (e) {
      debugLog('LocalStorage write skipped', 'warning', e);
    }
  }

  // Load cached run IDs (optimistic placeholders until hydrated)
  private loadCacheIds(): string[] {
    try {
      if (typeof localStorage === 'undefined') return [];

      const raw = localStorage.getItem(this.cacheKey);
      if (!raw) return [];

      const parsed = JSON.parse(raw);
      if (parsed.version !== 1) return [];

      // Optional expiry: ignore cache older than 60 minutes
      const cacheAge = Date.now() - (parsed.cached_at ?? 0);
      if (cacheAge > 60 * 60 * 1000) return [];

      return Array.isArray(parsed.run_ids) ? parsed.run_ids : [];
    } catch (e) {
      debugLog('loadCacheIds error', 'warning', e);
      return [];
    }
  }

  // Seed placeholder entries for optimistic UI (hydrated later)
  private seedPlaceholders(ids: string[]) {
    for (const id of ids) {
      if (!this.runs.has(id)) {
        this.runs.set(id, {
          run_id: id,
          status: 'pending', // placeholder status; harmless until hydrated
          seq: -1,
          created_at: 0,
          updated_at: 0,
          owner_id: null,
          workflow_id: null,
          // no result/error
        });
      }
    }
    this.emitUpdate();
  }

  // Cold-load runs from server before SSE connection (restores state after refresh)
  private async coldLoadRuns(): Promise<void> {
    try {
      const resp = await fetch(
        `${API_ROOT}/workflow-runner/runs?status=pending,running,succeeded,failed,cancelled,timeout&owner=me&limit=200`, // FIXME: make configurable, use constants
        { credentials: 'include' },
      );
      if (!resp || !resp.ok) {
        debugLog('coldLoadRuns: fetch failed', 'informational', resp?.status);
        return;
      }
      const data = await resp.json();
      const arr: RunRecord[] = (data.runs || []) as RunRecord[];
      const serverIds = new Set(arr.map((r) => r.run_id));

      this.processSnapshotArray(arr);

      for (const localId of Array.from(this.runs.keys())) {
        if (!serverIds.has(localId)) {
          this.reconcileRun(localId);
        }
      }
    } catch (e) {
      debugLog('coldLoadRuns error', 'warning', e);
    }
  }

  //#region SSE Connection
  async start() {
    if (this.#ES || this.connecting) {
      return;
    }

    this.connecting = true;

    // 1) Load cached IDs and show placeholders
    const cachedIds = this.loadCacheIds();
    if (cachedIds.length > 0) {
      this.seedPlaceholders(cachedIds);
    }

    // 2) Cold-load authoritative runs
    await this.coldLoadRuns();

    // 3) Hydrate IDs that server didn't list
    const serverIds = new Set(
      Array.from(this.runs.keys()).filter((id) => {
        const run = this.runs.get(id);
        return run && run.seq >= 0; // anything we've actually hydrated
      }),
    );
    for (const id of cachedIds) {
      if (!serverIds.has(id)) {
        this.reconcileRun(id); // 404 => removeRun
      }
    }

    // 4) Open SSE
    this.openSse();
  }

  private openSse() {
    const url = `${API_ROOT}/workflow-runner/events`;

    try {
      this.#ES = new EventSource(url);
    } catch (err) {
      this.#ES = (EventSource as any)(url); // FIXME: workaround for some test environments
    }

    try {
      if (this.#ES && typeof this.#ES === 'object') {
        this.#ES.onmessage = (e: MessageEvent) => {
          try {
            const payload = JSON.parse(e.data) as EventPayload;
            this.applyEvent({
              run_id: payload.run_id,
              workflow_id: payload.workflow_id,
              status: payload.status,
              seq: payload.seq ?? 0,
              owner_id: payload.owner_id,
              created_at: payload.created_at,
              updated_at: payload.updated_at,
              result: payload.result,
              error: payload.error,
            });
          } catch (err) {
            debugLog('invalid generic event message', 'informational', err);
          }

          if (this.processingSnapshot) {
            this.processingSnapshot = false;
          }
        };
      }
    } catch (e) {
      debugLog('EventSource onmessage assignment failed', 'informational', e);
    }

    this.processingSnapshot = true;

    this.#ES.onopen = () => {
      this.backoffMs = 1000; // FIXME: make configurable

      if (this.pollingTimer) {
        clearInterval(this.pollingTimer);
        this.pollingTimer = null;

        if (this.pollAbortController) {
          try {
            this.pollAbortController.abort();
          } catch {
            // ignore
          }
          this.pollAbortController = null;
        }
      }
    };

    this.#ES.onerror = () => {
      if (this.#ES) {
        try {
          this.#ES.close();
        } catch {
          debugLog('EventSource close failed', 'informational');
        }
        this.#ES = null;
      }
      this.startPollingFallback();

      const delay = this.backoffWithJitter();
      setTimeout(() => this.start(), delay);
      this.backoffMs = Math.min(this.backoffMs * 2, this.maxBackoffMs);
    };

    this.#ES.addEventListener('run', (e: MessageEvent) => {
      // FIXME: declare name as constant
      try {
        const payload = JSON.parse(e.data) as EventPayload;
        // payload contains seq and run_id
        this.applyEvent({
          run_id: payload.run_id,
          workflow_id: payload.workflow_id,
          status: payload.status,
          seq: payload.seq ?? 0,
          owner_id: payload.owner_id,
          created_at: payload.created_at,
          updated_at: payload.updated_at,
          result: payload.result,
          error: payload.error,
        });
      } catch (err) {
        debugLog('Invalid run event', 'warning', err);
      }
    });

    this.#ES.addEventListener('queue', (e: MessageEvent) => {
      // FIXME: declare name as constant
      try {
        const payload = JSON.parse(e.data) as any;
        this.handleQueuePayload(payload);
      } catch (err) {
        debugLog('Invalid queue event', 'warning', err);
      }
    });

    this.connecting = false;
  }

  handleQueuePayload(payload: any) {
    // FIXME: proper typing
    if (!payload) {
      return;
    }

    try {
      if (payload && (payload.type === 'queue_status' || typeof payload.pending === 'number')) {
        const pending = Number(payload.pending || 0) || 0;
        const running = Number(payload.running || 0) || 0;
        if (this.queueHandler) {
          this.queueHandler(pending, running);
        }
        return;
      }

      if (payload && (payload.run_id || payload.status || payload.seq !== undefined)) {
        this.applyEvent({
          run_id: payload.run_id,
          workflow_id: payload.workflow_id,
          status: payload.status,
          seq: payload.seq ?? 0,
          owner_id: payload.owner_id,
          created_at: payload.created_at,
          updated_at: payload.updated_at,
          result: payload.result,
          error: payload.error,
        });
      }
    } catch (e) {
      debugLog('handleQueuePayload error', 'warning', e);
    }

    try {
      if (this.#ES && typeof this.#ES === 'object') {
        this.#ES.onmessage = (e: MessageEvent) => {
          try {
            const payload = JSON.parse(e.data) as EventPayload;

            this.applyEvent({
              run_id: payload.run_id,
              workflow_id: payload.workflow_id,
              status: payload.status,
              seq: payload.seq ?? 0,
              owner_id: payload.owner_id,
              created_at: payload.created_at,
              updated_at: payload.updated_at,
              result: payload.result,
              error: payload.error,
            });
          } catch (err) {
            // non-json messages (heartbeats) ignored
          }

          if (this.processingSnapshot) {
            this.processingSnapshot = false;
          }
        };
      }
    } catch (e) {
      debugLog('EventSource onmessage reassignment failed', 'informational', e);
    }
  }

  stop() {
    if (this.#ES) {
      try {
        this.#ES.close();
      } catch {}
      this.#ES = null;
    }

    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = null;
    }

    if (this.pollAbortController) {
      try {
        this.pollAbortController.abort();
      } catch {}
      this.pollAbortController = null;
    }
  }

  private startPollingFallback() {
    if (this.pollingTimer) {
      return;
    }

    this.pollingTimer = setInterval(() => this.pollActiveRuns(), this.pollingInterval);
    this.pollActiveRuns();
  }

  private async pollActiveRuns() {
    try {
      if (this.pollAbortController) {
        try {
          this.pollAbortController.abort();
        } catch {}
        this.pollAbortController = null;
      }

      const ac = new AbortController();
      this.pollAbortController = ac;

      const resp = await fetch(
        `${API_ROOT}/workflow-runner/runs?status=pending,running&owner=me&limit=200`,
        { signal: ac.signal, credentials: 'include' },
      );
      if (!resp.ok) {
        return;
      }

      const data = await resp.json();
      const arr: RunRecord[] = (data.runs || []) as RunRecord[];
      this.processSnapshotArray(arr);
      if (this.pollAbortController === ac) {
        this.pollAbortController = null;
      }
    } catch (e) {
      if (
        (e && (e.name === 'AbortError' || e.code === 'ABORT_ERR')) ||
        (e instanceof DOMException && e.name === 'AbortError')
      ) {
        // expected abort
      } else {
        debugLog('pollActiveRuns error', 'warning', e);
      }
    }
  }

  private backoffWithJitter() {
    const base = this.backoffMs;
    const jitterFactor = 0.5 + Math.random() * 0.5; // 0.5 .. 1.0

    return Math.floor(base * jitterFactor);
  }
}
