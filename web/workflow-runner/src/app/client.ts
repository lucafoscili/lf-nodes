// TypeScript client for Workflow Runner SSE + polling fallback

export type RunRecord = {
  run_id: string;
  status: string;
  seq: number;
  owner_id?: string | null;
  created_at?: number | null;
  updated_at?: number | null;
  result?: any;
  error?: string | null;
};

export type UpdateHandler = (runs: Map<string, RunRecord>) => void;

type EventPayload = RunRecord & { type?: string };

export class WorkflowRunnerClient {
  private baseUrl: string;
  private es: EventSource | null = null;
  private lastSeq: Map<string, number> = new Map();
  private runs: Map<string, RunRecord> = new Map();
  private onUpdate: UpdateHandler | null = null;
  private pollingInterval = 3000; // ms
  private pollingTimer: any = null;
  private pollAbortController: AbortController | null = null;
  private backoffMs = 1000;
  private maxBackoffMs = 30000;
  private connected = false;
  private processingSnapshot = false;

  constructor(baseUrl = '/api/lf-nodes') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  setUpdateHandler(h: UpdateHandler) {
    this.onUpdate = h;
  }

  private emitUpdate() {
    if (this.onUpdate) this.onUpdate(new Map(this.runs));
  }

  // Reconcile server record for a run via REST
  private async reconcileRun(run_id: string) {
    try {
      const resp = await fetch(`${this.baseUrl}/run/${encodeURIComponent(run_id)}/status`);
      if (!resp.ok) return;
      const data = await resp.json();
      const rec: RunRecord = {
        run_id: data.run_id,
        status: data.status,
        seq: data.seq || 0,
        owner_id: data.owner_id,
        created_at: data.created_at,
        updated_at: data.updated_at,
        result: data.result,
        error: data.error,
      };
      this.applyEvent(rec);
    } catch (e) {
      // ignore transient errors
      console.warn('reconcileRun error', e);
    }
  }

  private applyEvent(ev: RunRecord) {
    const last = this.lastSeq.get(ev.run_id) ?? -1;
    if (ev.seq <= last) return; // duplicate or older
    // gap detection: if ev.seq > last+1 then reconcile first
    if (last >= 0 && ev.seq > last + 1) {
      // async reconcile; don't block applying this event but request authoritative state
      this.reconcileRun(ev.run_id);
    }
    // accept event
    this.lastSeq.set(ev.run_id, ev.seq);
    this.runs.set(ev.run_id, ev);
    this.emitUpdate();
  }

  private processSnapshotArray(arr: RunRecord[]) {
    // Replace/merge snapshot state. For each run, if snapshot.seq > lastSeq, accept it.
    const activeSet = new Set<string>();
    for (const s of arr) {
      activeSet.add(s.run_id);
      const last = this.lastSeq.get(s.run_id) ?? -1;
      if (s.seq <= last) continue;
      this.lastSeq.set(s.run_id, s.seq);
      this.runs.set(s.run_id, s);
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
    })();
  }

  // Start SSE connection and install handlers
  start() {
    if (this.es) return;
    const lastEventId = this.buildLastEventId();
    const url = `${this.baseUrl}/workflow-runner/events`;
    const headers: any = {};
    // Browser EventSource doesn't support custom headers; use Last-Event-ID via constructor if available
    const opts: any = {} as any;
    if (lastEventId) {
      // EventSource accepts lastEventId via the URL hash workaround or via the header in some polyfills.
      // We'll append it as a query param to be robust: server will read Last-Event-ID header but not query.
      // Instead, use native Last-Event-ID: rely on browser to send it from previous events when reconnecting.
    }

    this.es = new EventSource(url);

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
      // schedule reconnect with jittered backoff
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
      // queue events may be ignored or used; treat similarly to run
      try {
        const payload = JSON.parse(e.data) as EventPayload;
        this.applyEvent({
          run_id: payload.run_id,
          status: payload.status,
          seq: payload.seq ?? 0,
          owner_id: payload.owner_id,
          created_at: payload.created_at,
          updated_at: payload.updated_at,
          result: payload.result,
          error: payload.error,
        });
      } catch (err) {
        console.warn('invalid queue event', err);
      }
    });

    // Generic message handler for snapshot items if server sends them as events
    this.es.onmessage = (e: MessageEvent) => {
      // If processing snapshot, treat initial messages as part of snapshot until a short grace elapses
      try {
        const payload = JSON.parse(e.data) as EventPayload;
        // if snapshot contains multiple events in quick succession, we'll process them normally
        this.applyEvent({
          run_id: payload.run_id,
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
        `${this.baseUrl}/workflow-runner/runs?status=pending,running&owner=me&limit=200`,
        { signal: ac.signal },
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
