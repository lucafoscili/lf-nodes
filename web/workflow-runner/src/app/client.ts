import { API_ROOT } from '../config';
import {
  EventPayload,
  QueuePayload,
  RunRecord,
  WorkflowApiResponse,
  WorkflowNameItem,
} from '../types/client';
import { WorkflowStore } from '../types/state';
import type { ClientInternals, ClientInternalsMethods } from '../types/test-utils';
import { recordToUI } from '../utils/common';
import { debugLog } from '../utils/debug';
import { ensureActiveRun, upsertRun } from './store-actions';

export class WorkflowRunnerClient {
  // Core
  #ES: EventSource | null = null;
  #STORE: WorkflowStore;
  #WORKFLOW_NAMES: Record<string, string> = {};

  // Configuration constants
  #CACHE_KEY = 'lf-runs-cache';
  #CACHE_EXPIRY_MS = 60 * 60 * 1000; // 1 hour
  #INITIAL_BACKOFF_MS = 1000;
  #MAX_BACKOFF_MS = 30000;
  #POLLING_INTERVAL_MS = 3000;
  #RUNS_QUERY_LIMIT = 200;

  // Event constants
  #EVENT_RUN = 'run';
  #EVENT_QUEUE = 'queue';

  // Core data structures
  #LAST_SEQ: Map<string, number> = new Map();
  #RUNS: Map<string, RunRecord> = new Map();
  #WORKFLOW_CACHE: Map<string, string> = new Map();

  // Runtime state
  #STATE = {
    connecting: false,
    processingSnapshot: false,
  };

  // Polling configuration and state
  #POLLING = {
    timer: null,
    abortController: null as AbortController | null,
  };

  // Backoff state
  #BACKOFF_MS = 1000;

  // Async operation deduplication
  #INFLIGHT_RECONCILES = new Map<string, Promise<void>>();
  #INFLIGHT_DETAILS = new Map<string, Promise<void>>();
  #LOADED_DETAILS = new Set<string>();
  #OPEN_DETAIL_RUN_ID: string | null = null;

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

  // Preload workflow names to avoid fetching them individually
  setWorkflowNames(names: Map<string, string>) {
    for (const [id, name] of names) {
      this.#WORKFLOW_CACHE.set(id, name);
    }
    // Emit update to refresh UI with names
    this.emitUpdate();
  }

  private emitUpdate() {
    if (this.onUpdate) this.onUpdate(new Map(this.#RUNS));
    // Save to cache after each update for persistence across reloads
    this.saveCache();
  }

  // Reconcile server record for a run via REST (de-duplicated)
  private reconcileRun(run_id: string) {
    // De-dupe inflight reconciles
    if (this.#INFLIGHT_RECONCILES.has(run_id)) {
      return;
    }

    const promise = this._fetchRun(run_id, false)
      .catch(() => {
        // ignore transient errors
      })
      .finally(() => {
        this.#INFLIGHT_RECONCILES.delete(run_id);
      });

    this.#INFLIGHT_RECONCILES.set(run_id, promise);
  }

  private async _fetchRun(run_id: string, includeDetail: boolean): Promise<void> {
    try {
      const detailQuery = includeDetail ? '' : '?detail=0';
      const resp = await fetch(`${API_ROOT}/run/${encodeURIComponent(run_id)}/status${detailQuery}`, {
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
      // A slow detail response must not resurrect a payload after the user
      // has already left that card or opened another one.
      if (includeDetail && this.#OPEN_DETAIL_RUN_ID !== run_id) {
        return;
      }
      const rec: RunRecord = {
        run_id: data.run_id,
        workflow_id: data.workflow_id,
        status: data.status,
        seq: data.seq || 0,
        owner_id: data.owner_id,
        created_at: data.created_at,
        updated_at: data.updated_at,
        outputs: data.outputs,
        result: data.result,
        error: data.error,
      };
      this.upsertRun(rec);
      if (includeDetail) {
        this.#LOADED_DETAILS.add(run_id);
      }
    } catch (e) {
      debugLog('reconcileRun error', 'warning', e);
      throw e;
    }
  }

  /** Fetch a terminal result only when its output detail is actually opened. */
  async loadRunDetail(run_id: string): Promise<void> {
    if (!run_id) {
      return;
    }

    if (this.#OPEN_DETAIL_RUN_ID && this.#OPEN_DETAIL_RUN_ID !== run_id) {
      this.releaseRunDetail(this.#OPEN_DETAIL_RUN_ID);
    }
    this.#OPEN_DETAIL_RUN_ID = run_id;

    if (this.#LOADED_DETAILS.has(run_id)) {
      return;
    }

    const pending = this.#INFLIGHT_DETAILS.get(run_id);
    if (pending) {
      return pending;
    }

    const promise = this._fetchRun(run_id, true).finally(() => {
      this.#INFLIGHT_DETAILS.delete(run_id);
    });
    this.#INFLIGHT_DETAILS.set(run_id, promise);
    return promise;
  }

  /** Release the heavyweight payload while retaining the run's summary preview. */
  releaseRunDetail(run_id?: string): void {
    const target = run_id || this.#OPEN_DETAIL_RUN_ID;
    if (!target) {
      return;
    }

    const existing = this.#RUNS.get(target);
    const hadResult = existing?.result !== undefined && existing.result !== null;
    if (existing && hadResult) {
      this.#RUNS.set(target, { ...existing, result: null });
    }
    this.#LOADED_DETAILS.delete(target);
    if (this.#OPEN_DETAIL_RUN_ID === target) {
      this.#OPEN_DETAIL_RUN_ID = null;
    }
    if (hadResult) {
      this.emitUpdate();
    }
  }

  private applyEvent(ev: RunRecord) {
    // Validate mandatory fields
    if (!ev || !ev.run_id || typeof ev.status === 'undefined' || ev.status === null) {
      debugLog('applyEvent: invalid run record (missing run_id or status)', 'warning', ev);
      return;
    }

    const last = this.#LAST_SEQ.get(ev.run_id) ?? -1;
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
    const last = this.#LAST_SEQ.get(rec.run_id) ?? -1;
    if (rec.seq < last) return; // older - don't regress seq

    const existing = this.#RUNS.get(rec.run_id);
    if (rec.seq === last && existing) {
      const supplements = {
        ...(rec.workflow_id !== undefined ? { workflow_id: rec.workflow_id } : {}),
        ...(rec.owner_id !== undefined ? { owner_id: rec.owner_id } : {}),
        ...(rec.created_at !== undefined ? { created_at: rec.created_at } : {}),
        ...(rec.updated_at !== undefined ? { updated_at: rec.updated_at } : {}),
        ...(rec.outputs !== undefined ? { outputs: rec.outputs } : {}),
        ...(rec.result !== undefined ? { result: rec.result } : {}),
        ...(rec.error !== undefined ? { error: rec.error } : {}),
      };
      const hasNewSupplement = Object.entries(supplements).some(
        ([key, value]) => existing[key as keyof RunRecord] !== value,
      );
      if (!hasNewSupplement) {
        return;
      }

      const merged: RunRecord = {
        ...existing,
        ...supplements,
      };
      this.#RUNS.set(rec.run_id, merged);
      this.emitUpdate();
      return;
    }

    const refreshOpenTerminalDetail =
      !!existing &&
      rec.seq > last &&
      this.#OPEN_DETAIL_RUN_ID === rec.run_id &&
      ['succeeded', 'failed', 'cancelled'].includes(rec.status);
    if (existing && rec.seq > last) {
      this.#LOADED_DETAILS.delete(rec.run_id);
    }

    // Accept record
    this.#LAST_SEQ.set(rec.run_id, rec.seq);
    this.#RUNS.set(rec.run_id, rec);

    // Fetch workflow name if workflow_id is present but name is unknown
    if (rec.workflow_id && !this.#WORKFLOW_CACHE.has(rec.workflow_id)) {
      this.fetchWorkflowNames([rec.workflow_id]);
    }

    this.emitUpdate();
    if (refreshOpenTerminalDetail) {
      void this.loadRunDetail(rec.run_id);
    }
  }

  // Remove a run completely from state and cache (used when server returns 404)
  private removeRun(runId: string) {
    this.#RUNS.delete(runId);
    this.#LAST_SEQ.delete(runId);
    this.#LOADED_DETAILS.delete(runId);
    if (this.#OPEN_DETAIL_RUN_ID === runId) {
      this.#OPEN_DETAIL_RUN_ID = null;
    }
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
      const last = this.#LAST_SEQ.get(s.run_id) ?? -1;
      if (s.seq <= last) continue;
      this.#LAST_SEQ.set(s.run_id, s.seq);
      this.#RUNS.set(s.run_id, s);
      if (s.workflow_id && !this.#WORKFLOW_CACHE.has(s.workflow_id)) {
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
        for (const [id, rec] of this.#RUNS.entries()) {
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
    const needs = ids.filter((id) => !!id && !this.#WORKFLOW_CACHE.has(id));
    if (needs.length === 0) return;
    try {
      const resp = await fetch(`${API_ROOT}/workflows?ids=${encodeURIComponent(needs.join(','))}`, {
        credentials: 'include',
      });
      if (!resp || !resp.ok) return;
      const data: WorkflowApiResponse = await resp.json();
      // Normalize multiple possible shapes returned by the server:
      // - Array of {workflow_id, name}
      // - { workflows: [ { ... } ] }
      // - { workflows: { nodes: [ { id, value, ... } ] } }
      // - { workflows: { <id>: "name", ... } }
      let items: WorkflowNameItem[] = [];
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
            items = data.workflows.nodes.map((n: WorkflowNameItem) => ({
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
          if (id && name) this.#WORKFLOW_CACHE.set(id, name);
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

      const ids = Array.from(this.#RUNS.keys());
      const payload = {
        version: 1,
        cached_at: Date.now(),
        run_ids: ids.slice(-300), // cap to recent 300 runs
      };
      localStorage.setItem(this.#CACHE_KEY, JSON.stringify(payload));
    } catch (e) {
      debugLog('LocalStorage write skipped', 'warning', e);
    }
  }

  // Load cached run IDs (optimistic placeholders until hydrated)
  private loadCacheIds(): string[] {
    try {
      if (typeof localStorage === 'undefined') return [];

      const raw = localStorage.getItem(this.#CACHE_KEY);
      if (!raw) return [];

      const parsed = JSON.parse(raw);
      if (parsed.version !== 1) return [];

      // Optional expiry: ignore cache older than 60 minutes
      const cacheAge = Date.now() - (parsed.cached_at ?? 0);
      if (cacheAge > this.#CACHE_EXPIRY_MS) return [];

      return Array.isArray(parsed.run_ids) ? parsed.run_ids : [];
    } catch (e) {
      debugLog('loadCacheIds error', 'warning', e);
      return [];
    }
  }

  // Seed placeholder entries for optimistic UI (hydrated later)
  private seedPlaceholders(ids: string[]) {
    for (const id of ids) {
      if (!this.#RUNS.has(id)) {
        this.#RUNS.set(id, {
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
        `${API_ROOT}/workflow-runner/runs?status=pending,running,succeeded,failed,cancelled,timeout&owner=me&summary=1&limit=${
          this.#RUNS_QUERY_LIMIT
        }`,
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

      for (const localId of Array.from(this.#RUNS.keys())) {
        if (!serverIds.has(localId)) {
          this.#RUNS.delete(localId);
          this.#LAST_SEQ.delete(localId);
          this.#LOADED_DETAILS.delete(localId);
        }
      }
      this.emitUpdate();
    } catch (e) {
      debugLog('coldLoadRuns error', 'warning', e);
    }
  }

  //#region SSE Connection
  async start() {
    if (this.#ES || this.#STATE.connecting) {
      return;
    }

    this.#STATE.connecting = true;

    // 1) Load cached IDs and show placeholders
    const cachedIds = this.loadCacheIds();
    if (cachedIds.length > 0) {
      this.seedPlaceholders(cachedIds);
    }

    // 2) Cold-load authoritative runs
    await this.coldLoadRuns();

    // 3) Open SSE. The bounded server list is authoritative for history;
    // cached ids outside it are deliberately not hydrated one-by-one.
    this.openSse();
  }

  private openSse() {
    const url = `${API_ROOT}/workflow-runner/events?summary=1`;

    try {
      this.#ES = new EventSource(url);
    } catch (err) {
      this.#ES = (EventSource as any)(url); // Workaround for test environments where EventSource constructor differs
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
              outputs: payload.outputs,
              result: payload.result,
              error: payload.error,
            });
          } catch (err) {
            debugLog('invalid generic event message', 'informational', err);
          }

          if (this.#STATE.processingSnapshot) {
            this.#STATE.processingSnapshot = false;
          }
        };
      }
    } catch (e) {
      debugLog('EventSource onmessage assignment failed', 'informational', e);
    }

    this.#STATE.processingSnapshot = true;

    this.#ES.onopen = () => {
      this.#BACKOFF_MS = this.#INITIAL_BACKOFF_MS;

      if (this.#POLLING.timer) {
        clearInterval(this.#POLLING.timer);
        this.#POLLING.timer = null;

        if (this.#POLLING.abortController) {
          try {
            this.#POLLING.abortController.abort();
          } catch {
            // ignore
          }
          this.#POLLING.abortController = null;
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
      // Note: backoff is increased in backoffWithJitter()
    };

    this.#ES.addEventListener(this.#EVENT_RUN, (e: MessageEvent) => {
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
          outputs: payload.outputs,
          result: payload.result,
          error: payload.error,
        });
      } catch (err) {
        debugLog('Invalid run event', 'warning', err);
      }
    });

    this.#ES.addEventListener(this.#EVENT_QUEUE, (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data) as any;
        this.handleQueuePayload(payload);
      } catch (err) {
        debugLog('Invalid queue event', 'warning', err);
      }
    });

    this.#STATE.connecting = false;
  }

  handleQueuePayload(payload: QueuePayload) {
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
          outputs: payload.outputs,
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
              outputs: payload.outputs,
              result: payload.result,
              error: payload.error,
            });
          } catch (err) {
            // non-json messages (heartbeats) ignored
          }

          if (this.#STATE.processingSnapshot) {
            this.#STATE.processingSnapshot = false;
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

    if (this.#POLLING.timer) {
      clearInterval(this.#POLLING.timer);
      this.#POLLING.timer = null;
    }

    if (this.#POLLING.abortController) {
      try {
        this.#POLLING.abortController.abort();
      } catch {}
      this.#POLLING.abortController = null;
    }

    this.#INFLIGHT_RECONCILES.clear();
    this.#INFLIGHT_DETAILS.clear();
    this.#LOADED_DETAILS.clear();
    this.#OPEN_DETAIL_RUN_ID = null;
  }

  getRuns(): Map<string, RunRecord> {
    return this.#RUNS;
  }

  getLastSeq(): Map<string, number> {
    return this.#LAST_SEQ;
  }

  /**
   * Test API: returns a minimal test-only facade exposing internal maps
   * and operations used by unit tests. Prefer public behavior where
   * possible; this API exists solely to avoid fragile `as any` casts in
   * tests and is intentionally small.
   */
  getTestApi(): ClientInternals & ClientInternalsMethods {
    const self: any = this;
    self.applyEvent = this.applyEvent.bind(this);
    self.upsertRun = this.upsertRun.bind(this);
    self.reconcileRun = this.reconcileRun.bind(this);
    self.loadRunDetail = this.loadRunDetail.bind(this);
    self.releaseRunDetail = this.releaseRunDetail.bind(this);
    self.pollActiveRuns = this.pollActiveRuns.bind(this);
    self.coldLoadRuns = this.coldLoadRuns.bind(this);
    self.processSnapshotArray = this.processSnapshotArray.bind(this);
    self.saveCache = this.saveCache.bind(this);
    self.loadCacheIds = this.loadCacheIds.bind(this);
    self.seedPlaceholders = this.seedPlaceholders.bind(this);
    self.start = this.start.bind(this);
    self.stop = this.stop.bind(this);
    self.fetchWorkflowNames = this.fetchWorkflowNames.bind(this);
    self.setWorkflowNames = this.setWorkflowNames.bind(this);

    self.lastSeq = this.#LAST_SEQ;
    self.runs = this.#RUNS;
    self.inflightReconciles = this.#INFLIGHT_RECONCILES;
    self.inflightDetails = this.#INFLIGHT_DETAILS;
    self.processingSnapshot = this.#STATE.processingSnapshot;
    self.cacheKey = this.#CACHE_KEY;
    self.workflowNames = this.#WORKFLOW_CACHE;
    self.store = this.#STORE;

    return this as unknown as ClientInternals & ClientInternalsMethods;
  }

  private startPollingFallback() {
    if (this.#POLLING.timer) {
      return;
    }

    this.#POLLING.timer = setInterval(() => this.pollActiveRuns(), this.#POLLING_INTERVAL_MS);
    this.pollActiveRuns();
  }

  private async pollActiveRuns() {
    try {
      if (this.#POLLING.abortController) {
        try {
          this.#POLLING.abortController.abort();
        } catch {}
        this.#POLLING.abortController = null;
      }

      const ac = new AbortController();
      this.#POLLING.abortController = ac;

      const resp = await fetch(
        `${API_ROOT}/workflow-runner/runs?status=pending,running&owner=me&summary=1&limit=${
          this.#RUNS_QUERY_LIMIT
        }`,
        { signal: ac.signal, credentials: 'include' },
      );
      if (!resp.ok) {
        return;
      }

      const data = await resp.json();
      const arr: RunRecord[] = (data.runs || []) as RunRecord[];
      this.processSnapshotArray(arr);
      if (this.#POLLING.abortController === ac) {
        this.#POLLING.abortController = null;
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
    const base = this.#BACKOFF_MS;
    const jitterFactor = 0.5 + Math.random() * 0.5; // 0.5 .. 1.0

    return Math.floor(base * jitterFactor);
  }
}
