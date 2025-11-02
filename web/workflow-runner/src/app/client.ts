import { API_ROOT } from '../config';
import { EventPayload, RunRecord, UpdateHandler } from '../types/client';

export class WorkflowRunnerClient {
  private es: EventSource | null = null;
  private lastSeq: Map<string, number> = new Map();
  private runs: Map<string, RunRecord> = new Map();
  private workflowNames: Map<string, string> = new Map();
  private onUpdate: UpdateHandler | null = null;
  // optional queue status handler: (pending, running) => void
  private queueHandler: ((pending: number, running: number) => void) | null = null;
  private pollingInterval = 3000; // ms
  private pollingTimer: any = null;
  private pollAbortController: AbortController | null = null;
  private backoffMs = 1000;
  private maxBackoffMs = 30000;
  private connected = false;
  // Guard to prevent concurrent start() invocations from creating multiple
  // EventSource instances in racey test environments or during reconnects.
  private connecting = false;
  private processingSnapshot = false;
  private cacheKey = 'lf-runs-cache';
  private inflightReconciles = new Map<string, Promise<void>>();

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
      if (!resp || !resp.ok) {
        console.warn('reconcileRun: fetch failed', resp?.status);
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
      console.warn('reconcileRun error', e);
      throw e;
    }
  }

  private applyEvent(ev: RunRecord) {
    // Validate mandatory fields
    if (!ev || !ev.run_id || typeof ev.status === 'undefined' || ev.status === null) {
      console.warn('applyEvent: invalid run record (missing run_id or status)', ev);
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
        console.warn('fetchWorkflowNames: failed to normalize response', e, data);
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
          console.warn('fetchWorkflowNames: skipping malformed item', it, e);
        }
      }
      // After populating names, emit an update so UI can re-render with names
      this.emitUpdate();
    } catch (e) {
      console.warn('fetchWorkflowNames error', e);
    }
  }

  // Save active runs to localStorage for fast restore on page reload
  private saveCache() {
    try {
      // Check if localStorage is available
      if (typeof localStorage === 'undefined') return;

      // Only cache runs that are potentially still active or recently completed
      const toCache: any[] = [];
      for (const [_id, rec] of this.runs.entries()) {
        // Cache all non-cancelled runs for now; limit total entries to 200 most recent
        if (rec.status !== 'cancelled') {
          toCache.push({
            run_id: rec.run_id,
            workflow_id: rec.workflow_id,
            status: rec.status,
            seq: rec.seq,
            updated_at: rec.updated_at,
            created_at: rec.created_at,
            owner_id: rec.owner_id,
            // omit result/error to keep cache small
          });
        }
      }
      // Sort by updated_at descending and keep only most recent 200
      toCache.sort((a, b) => (b.updated_at || 0) - (a.updated_at || 0));
      const limited = toCache.slice(0, 200);
      localStorage.setItem(this.cacheKey, JSON.stringify(limited));
    } catch (e) {
      // localStorage quota exceeded or disabled; fail silently
      console.warn('saveCache error', e);
    }
  }

  // Load cached runs from localStorage for optimistic rendering
  private loadCache() {
    try {
      // Check if localStorage is available
      if (typeof localStorage === 'undefined') return;

      const raw = localStorage.getItem(this.cacheKey);
      if (!raw) return;
      const arr: RunRecord[] = JSON.parse(raw);
      // Merge cached runs using processSnapshotArray (respects seq monotonicity)
      this.processSnapshotArray(arr);
    } catch (e) {
      console.warn('loadCache error', e);
    }
  }

  // Cold-load runs from server before SSE connection (restores state after refresh)
  private async coldLoadRuns(): Promise<void> {
    try {
      const resp = await fetch(
        `${API_ROOT}/workflow-runner/runs?status=pending,running,succeeded,failed,cancelled,timeout&owner=me&limit=200`,
        { credentials: 'include' },
      );
      if (!resp || !resp.ok) {
        console.warn('coldLoadRuns: fetch failed', resp?.status);
        return;
      }
      const data = await resp.json();
      const arr: RunRecord[] = (data.runs || []) as RunRecord[];
      // merge via shared snapshot handler
      this.processSnapshotArray(arr);
    } catch (e) {
      console.warn('coldLoadRuns error', e);
    }
  }

  // Start SSE connection and install handlers
  async start() {
    if (this.es) return;
    // If a start is already in progress, avoid attempting to create another
    // EventSource. This prevents duplicate connections in test mocks and
    // during jittery reconnect flows.
    if (this.connecting) return;
    this.connecting = true;

    // First, load cached runs from localStorage for optimistic rendering
    this.loadCache();

    // Then, cold-load persisted runs from server to restore authoritative state
    await this.coldLoadRuns();

    const lastEventId = this.buildLastEventId();
    const url = `${API_ROOT}/workflow-runner/events`;
    const headers: any = {};
    // Browser EventSource doesn't support custom headers; use Last-Event-ID via constructor if available
    const opts: any = {} as any;
    if (lastEventId) {
      // EventSource accepts lastEventId via the URL hash workaround or via the header in some polyfills.
      // We'll append it as a query param to be robust: server will read Last-Event-ID header but not query.
      // Instead, use native Last-Event-ID: rely on browser to send it from previous events when reconnecting.
    }

    // Some test environments mock EventSource as a plain factory (vi.fn(() => mock))
    // which is not constructable with `new`. Try to create with `new` first,
    // and fall back to calling the function directly when that fails so unit
    // tests that provide a factory-style mock still work.
    try {
      // Typical browser environment
      // eslint-disable-next-line new-cap
      this.es = new (EventSource as any)(url);
    } catch (err) {
      // Fallback for test mocks that return an instance when invoked
      // as a function (not as a constructor).
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      this.es = (EventSource as any)(url);
    }

    // Ensure a generic message handler exists for servers that emit 'message'
    // events (non-named events). Some EventSource mocks rely on `onmessage`
    // being present so we assign a safe handler here.
    try {
      if (this.es && typeof (this.es as any) === 'object') {
        (this.es as any).onmessage = (e: MessageEvent) => {
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
            // ignore non-json or heartbeat messages
          }
          if (this.processingSnapshot) this.processingSnapshot = false;
        };
      }
    } catch (e) {
      // ignore if assignment isn't possible on mocked EventSource
    }

    this.processingSnapshot = true;

    this.es.onopen = () => {
      this.connected = true;
      this.backoffMs = 1000;
      // stop polling fallback when SSE stable
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer);
        this.pollingTimer = null;
        // abort any in-flight polling fetch
        if (this.pollAbortController) {
          try {
            this.pollAbortController.abort();
          } catch {}
          this.pollAbortController = null;
        }
      }
    };

    this.es.onerror = () => {
      this.connected = false;
      // exponential backoff for reconnect attempts
      if (this.es) {
        try {
          this.es.close();
        } catch {}
        this.es = null;
      }
      this.startPollingFallback();
      // schedule reconnect with jittered backoff (coldLoadRuns will be called in start())
      const delay = this.backoffWithJitter();
      setTimeout(() => this.start(), delay);
      this.backoffMs = Math.min(this.backoffMs * 2, this.maxBackoffMs);
    };

    this.es.addEventListener('run', (e: MessageEvent) => {
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
        console.warn('invalid run event', err);
      }
    });

    this.es.addEventListener('queue', (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data) as any;
        this.handleQueuePayload(payload);
      } catch (err) {
        console.warn('invalid queue event', err);
      }
    });
    // Start completed: allow future start() calls to proceed only if the
    // current ES has been closed (prevents duplicate opens).
    this.connecting = false;
  }

  // Exposed for testing: handle a parsed queue payload from SSE. This will
  // call the registered queueHandler for queue_status snapshots, or fall
  // back to applying a run-like payload when appropriate.
  handleQueuePayload(payload: any) {
    if (!payload) return;
    try {
      if (payload && (payload.type === 'queue_status' || typeof payload.pending === 'number')) {
        const pending = Number(payload.pending || 0) || 0;
        const running = Number(payload.running || 0) || 0;
        if (this.queueHandler) this.queueHandler(pending, running);
        return;
      }

      // fallback: if payload looks like a run event, apply it
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
      console.warn('handleQueuePayload error', e);
    }

    // Generic message handler for snapshot items if server sends them as events
    try {
      if (this.es && typeof (this.es as any) === 'object') {
        (this.es as any).onmessage = (e: MessageEvent) => {
          // If processing snapshot, treat initial messages as part of snapshot until a short grace elapses
          try {
            const payload = JSON.parse(e.data) as EventPayload;
            // if snapshot contains multiple events in quick succession, we'll process them normally
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
          // After a brief grace, mark snapshot processing complete
          if (this.processingSnapshot) {
            this.processingSnapshot = false;
          }
        };
      }
    } catch (e) {
      // Defensive: if underlying EventSource mock doesn't support onmessage assignment,
      // ignore and continue — tests may simulate messages directly on the mock.
    }
  }

  stop() {
    if (this.es) {
      try {
        this.es.close();
      } catch {}
      this.es = null;
    }
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = null;
    }
    // abort any in-flight polling request
    if (this.pollAbortController) {
      try {
        this.pollAbortController.abort();
      } catch {}
      this.pollAbortController = null;
    }
  }

  private buildLastEventId() {
    // pick highest lastSeq and return as '<run_id>:<seq>' — EventSource will send Last-Event-ID automatically
    let maxRun: string | null = null;
    let maxSeq = -1;
    for (const [run, seq] of this.lastSeq.entries()) {
      if (seq > maxSeq) {
        maxSeq = seq;
        maxRun = run;
      }
    }
    if (!maxRun) return null;
    return `${maxRun}:${maxSeq}`;
  }

  private startPollingFallback() {
    if (this.pollingTimer) return;
    // poll active runs every pollingInterval ms until SSE stabilizes
    this.pollingTimer = setInterval(() => this.pollActiveRuns(), this.pollingInterval);
    // run immediately once
    this.pollActiveRuns();
  }

  private async pollActiveRuns() {
    try {
      // abort previous in-flight poll if any
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
      if (!resp.ok) return;
      const data = await resp.json();
      const arr: RunRecord[] = (data.runs || []) as RunRecord[];
      // merge snapshot via shared handler (always performs reconciliation)
      this.processSnapshotArray(arr);
      // clear controller on success
      if (this.pollAbortController === ac) this.pollAbortController = null;
    } catch (e) {
      // AbortError is expected when controller aborts; log others
      if (
        (e && (e.name === 'AbortError' || e.code === 'ABORT_ERR')) ||
        (e instanceof DOMException && e.name === 'AbortError')
      ) {
        // expected abort
      } else {
        console.warn('pollActiveRuns error', e);
      }
    }
  }

  // return a backoff delay in ms with jitter applied (randomized between 50% and 100% of backoffMs)
  private backoffWithJitter() {
    const base = this.backoffMs;
    const jitterFactor = 0.5 + Math.random() * 0.5; // 0.5 .. 1.0
    return Math.floor(base * jitterFactor);
  }
}
