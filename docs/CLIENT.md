# WorkflowRunnerClient

> **Single Source of Truth for Run State Ingestion**

## Overview

`WorkflowRunnerClient` is the **only** ingestion path for workflow run state in the Workflow Runner application. It owns all network concerns related to run state (SSE, polling, cold-load, cache, backoff, reconciliation) and provides a clean, reactive interface to the application layer.

## Architecture

```plaintext
┌─────────────────────────────────────────┐
│      WorkflowRunnerClient (client.ts)   │  ← Single ingestion point
│  ┌────────────────────────────────────┐ │
│  │ • localStorage cache               │ │
│  │ • Cold load (REST)                 │ │
│  │ • SSE connection                   │ │
│  │ • Polling fallback                 │ │
│  │ • Gap detection + reconciliation   │ │
│  │ • Seq monotonicity guards          │ │
│  │ • Workflow name resolution         │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    ↓
            onUpdate(runs)
                    ↓
┌─────────────────────────────────────────┐
│         LfWorkflowRunnerManager         │  ← Orchestration
│  ┌────────────────────────────────────┐ │
│  │ mapRunRecordToUi()                 │ │  ← DRY mapper
│  │ upsertRun()                        │ │  ← Store actions
│  │ ensureActiveRun()                  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          WorkflowStore + State          │  ← Application state
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│              UI Components              │  ← Presentation
└─────────────────────────────────────────┘
```

## Responsibilities

### WorkflowRunnerClient owns

- **Network layer**: EventSource (SSE), fetch (REST), polling timers
- **Resilience**: Reconnection with exponential backoff, polling fallback when SSE fails
- **State reconciliation**: Gap detection, sequence monotonicity, de-duplicated reconciliation
- **Caching**: localStorage persistence for hydration on page refresh
- **Workflow metadata**: Batch fetching and caching of workflow names

### WorkflowRunnerClient does NOT own

- **Application state**: Store mutations happen in manager via `onUpdate` callback
- **Business logic**: Run lifecycle handlers, notifications, input validation
- **UI concerns**: Rendering, selection, routing

## Public API

### Constructor

```typescript
const client = new WorkflowRunnerClient(store: WorkflowStore);
```

**Parameters:**

- `store` (required): The workflow store instance. The client needs direct access to the store for updating workflow names and queue status.

### Methods

#### `setUpdateHandler(handler: UpdateHandler): void`

Sets the callback invoked when run state changes. The client provides a default `onUpdate` handler that integrates with the store, but this can be overridden for custom behavior.

```typescript
type UpdateHandler = (runs: Map<string, RunRecord>) => void;

// Default behavior (built-in)
client.onUpdate = (runs) => {
  // Auto-extracts workflow names from store
  // Converts records to UI format
  // Calls upsertRun and ensureActiveRun
};

// Custom override (optional)
client.setUpdateHandler((runs) => {
  for (const [runId, rec] of runs) {
    const uiEntry = mapRunRecordToUi(rec, workflowNames);
    upsertRun(store, uiEntry);
  }
  ensureActiveRun(store);
});
```

**Contract:**

- Called immediately after any run state mutation
- Receives a **snapshot** of all known runs (Map is fresh copy)
- Handler should be **idempotent** (may be called with same state)
- Handler should be **fast** (no async I/O, minimal compute)

#### `setQueueHandler(handler: (pending: number, running: number) => void): void`

Sets the callback invoked when queue status updates arrive via SSE. The client provides a default handler that updates store state.

```typescript
// Default behavior (built-in)
client.queueHandler = (pending, running) => {
  const state = this.#STORE.getState();
  state.mutate.queuedJobs(pending + running);
};

// Custom override (optional)
client.setQueueHandler((pending, running) => {
  console.log(`Queue: ${pending} pending, ${running} running`);
  updateQueueIndicator(pending + running);
});
```

#### `setWorkflowNames(names: Map<string, string>): void`

Preloads workflow names to avoid individual fetch-per-run.

```typescript
// After workflows load
const names = new Map([
  ['wf-1', 'Image Generation'],
  ['wf-2', 'Text Processing'],
]);
client.setWorkflowNames(names);
```

**When to call:**

- After fetching workflow definitions from `/workflows`
- Before calling `start()` (optional but recommended)
- Anytime workflow metadata changes

#### `start(): Promise<void>`

Starts the client. Call **exactly once** per application lifecycle.

```typescript
await client.start();
```

**What happens:**

1. Loads cached runs from localStorage (synchronous)
2. Fetches authoritative runs via REST (cold load)
3. Opens SSE connection to `/workflow-runner/events`
4. Starts polling fallback if SSE fails

**Idempotent**: Subsequent calls are no-ops.

#### `stop(): void`

Stops all network activity and timers. Call on cleanup/unmount.

```typescript
client.stop();
```

**What happens:**

- Closes SSE connection
- Clears polling timers
- Aborts in-flight requests

## Data Flow

### Startup (Cold Load)

```plaintext
User opens app
     ↓
manager.constructor()
     ↓
client = new WorkflowRunnerClient(store)
     ↓
[Client has default onUpdate handler built-in]
     ↓
[workflows load]
     ↓
client.setWorkflowNames(...) [optional]
     ↓
client.start()
     ├─→ loadCacheIds() ─────────→ seedPlaceholders() → onUpdate (optimistic)
     ├─→ coldLoadRuns() ─────────→ processSnapshotArray() → onUpdate (authoritative)
     │   └─→ reconcileRun() for local IDs not in server response
     ├─→ reconcileRun() for cached IDs not hydrated by coldLoad
     └─→ openSse() ──────────────→ (listen for events)
```

### Runtime (SSE Events)

```plaintext
Server emits SSE event
     ↓
client receives event (type: 'run', 'queue', or generic)
     ↓
     ├─→ 'run' event or generic message
     │   ↓
     │   applyEvent(rec)
     │   ├─→ validate (run_id, status, seq present?)
     │   ├─→ gap detection (seq > last+1?)
     │   │       ├─→ YES: reconcileRun(run_id) [async, de-duped]
     │   │       └─→ NO: continue
     │   ├─→ upsertRun(rec)
     │   │       ├─→ seq <= last? → REJECT (no update)
     │   │       └─→ seq > last? → ACCEPT
     │   │               ├─→ lastSeq[run_id] = rec.seq
     │   │               ├─→ runs[run_id] = rec
     │   │               ├─→ fetchWorkflowNames([rec.workflow_id]) if missing
     │   │               └─→ emitUpdate()
     │   └─→ onUpdate(runs) → store
     │
     └─→ 'queue' event
         ↓
         handleQueuePayload(payload)
         ├─→ extract pending & running counts
         └─→ queueHandler(pending, running) → update store
```

### Reconnection

```plaintext
SSE error
     ↓
es.onerror
     ├─→ close existing EventSource
     ├─→ startPollingFallback() [every 3s, status=pending,running]
     └─→ setTimeout(openSse, backoffWithJitter())
         ↓
         [exponential backoff with jitter: 1s → 2s → 4s → ... → 30s]
         ↓
     openSse() [retry]
         ↓
         [if SSE succeeds]
         ↓
         es.onopen
         ├─→ reset backoffMs to 1000
         └─→ stop polling fallback (clearInterval + abort)
```

## Server-Side Execution State Management

The server monitors ComfyUI's execution queue and updates run status accurately:

```plaintext
Workflow submitted
     ↓
Job created: PENDING (seq=0)
     ↓
Queued in ComfyUI
     ↓
_monitor_execution_state() starts polling
     ↓
┌────────────────────────────────────────────┐
│ Check ComfyUI queue state (every 350ms)   │
├────────────────────────────────────────────┤
│ Prompt in currently_running?              │ ─── YES ──→ Status: RUNNING (seq++)
│   (Only 1 item max in currently_running)  │            SSE event published
│                                            │            Exit monitoring
│                NO                          │
│                ↓                           │
│ Prompt in history?                        │ ─── YES ──→ Already completed
│   (Fast execution - completed before      │            (skip RUNNING)
│    monitoring could detect it)            │            Exit monitoring
│                                            │
│                NO                          │
│                ↓                           │
│ Prompt still in queue?                    │ ─── YES ──→ Keep polling
│   (Waiting for execution)                 │            Status stays PENDING
│                                            │
│                NO                          │
│                ↓                           │
│ Prompt lost (not in queue/running/hist)   │ ─── YES ──→ Log warning
│                                            │            Exit monitoring
└────────────────────────────────────────────┘
                    ↓
        _wait_for_completion()
                    ↓
        Status: SUCCEEDED/FAILED (seq++)
                    ↓
            SSE event published
```

**Key Properties:**

- **Single-execution constraint**: Only 1 run shows as RUNNING (ComfyUI processes 1 job at a time)
- **Fast-execution handling**: Workflows that complete before monitoring detects them skip RUNNING state
- **No stuck PENDING**: All runs either transition to RUNNING or complete directly
- **Accurate queue representation**: PENDING means queued, RUNNING means executing

**State Transitions:**

```plaintext
Normal workflow:     PENDING → RUNNING → SUCCEEDED/FAILED
Fast workflow:       PENDING → SUCCEEDED/FAILED (skip RUNNING)
Queued workflow:     PENDING (stays until execution starts)
```

## Constraints & Invariants

### ✅ DO

- **Instantiate once** at the manager/root level with store instance
- **Call `start()` exactly once** per application lifecycle
- **Call `stop()` on cleanup** (unmount, destroy)
- **Keep `onUpdate` handler fast** (< 5ms) if overriding default
- **Keep `queueHandler` fast** if overriding default
- **Use default handlers** unless custom behavior is needed (they integrate with store)
- **Trust the client** for network concerns (don't open EventSource elsewhere)

### ❌ DON'T

- **Don't instantiate without a store** (store is required parameter)
- **Don't open EventSource elsewhere** (breaks single-source-of-truth)
- **Don't fetch runs directly** (use client's cold load)
- **Don't poll manually** (client handles fallback)
- **Don't mutate `runs` Map** (it's a snapshot; mutations won't propagate)
- **Don't make handlers async** (fire-and-forget side effects only)
- **Don't call `start()` multiple times** (idempotent but wasteful)

## Sequence Monotonicity

The client enforces **sequence monotonicity** to prevent event reordering and stale updates:

```typescript
// Events arrive with seq numbers
{ run_id: 'run-1', status: 'pending', seq: 1 }
{ run_id: 'run-1', status: 'running', seq: 2 }
{ run_id: 'run-1', status: 'succeeded', seq: 3 }

// If seq <= lastSeq, reject
{ run_id: 'run-1', status: 'failed', seq: 2 } // REJECTED (2 <= 3)

// Reconciliation returns older seq? Also rejected
reconcile('run-1') → { seq: 2 } // REJECTED (2 <= 3)
```

**Why?**

- SSE events may arrive out-of-order (network, proxies)
- Reconciliation may return stale state (server lag)
- We want **newest wins**, never regress to older state

## Gap Detection

The client detects **event gaps** and triggers reconciliation:

```typescript
// Last seen: seq=5
applyEvent({ run_id: 'run-1', seq: 10 })
           ↓
           Gap detected: 5 → 10 (missing 6, 7, 8, 9)
           ↓
           reconcileRun('run-1') [fetch authoritative state]
```

**Why?**

- SSE may drop events (connection hiccup, server restart)
- Gaps indicate missed updates
- Reconciliation fetches authoritative state to fill gaps

## Reconciliation De-duplication

The client de-duplicates concurrent reconciliation calls:

```typescript
// Multiple triggers
applyEvent({ seq: 10 }) // gap → reconcileRun('run-1')
applyEvent({ seq: 15 }) // gap → reconcileRun('run-1')
applyEvent({ seq: 20 }) // gap → reconcileRun('run-1')

// Only one fetch happens (in-flight map)
inflightReconciles.set('run-1', promise)
```

**Why?**

- Avoid redundant fetches
- Reduce server load
- Faster reconciliation

**Additional Reconciliation Triggers:**

- **404 responses**: When reconciliation returns 404, the run is removed from state (via `removeRun`)
- **Missing workflow_id**: Runs without workflow_id trigger reconciliation to fetch complete details
- **Stale local state**: During cold load, local runs not in server response are reconciled
- **Disappeared running runs**: After snapshot/reconnect, locally-running runs not in snapshot are reconciled

## Workflow Name Resolution

The client automatically fetches missing workflow names:

```typescript
upsertRun({ run_id: 'run-1', workflow_id: 'wf-1' })
     ↓
     workflowNames.has('wf-1')? NO
     ↓
     fetchWorkflowNames(['wf-1'])
     ↓
     GET /api/lf-nodes/workflows?ids=wf-1
     ↓
     workflowNames.set('wf-1', 'Image Generation')
     ↓
     emitUpdate() [UI re-renders with name]
```

**Optimization:** Preload all workflow names via `setWorkflowNames()` to avoid per-run fetches.

## Cache Persistence

The client saves run IDs to `localStorage` for fast hydration on refresh:

```typescript
// After every update
emitUpdate()
     ↓
     saveCache()
     ↓
     localStorage.setItem('lf-runs-cache', JSON.stringify({
       version: 1,
       cached_at: Date.now(),
       run_ids: ids.slice(-300) // cap to recent 300 IDs
     }))
```

**Cache Strategy:**

- **V1 Schema**: Stores only run IDs (not full records) for schema stability
- **Optimistic placeholders**: On startup, seeds placeholder entries for cached IDs
- **Hydration**: Full run data fetched via REST cold load
- **Expiry**: Cache older than 60 minutes is ignored
- **Limits**: Keeps **300 most recent** run IDs
- **Graceful degradation**: Handles quota exceeded silently (cache disabled)

## Error Handling

The client handles errors gracefully:

- **SSE errors**: Trigger reconnection with exponential backoff + polling fallback
- **Fetch errors**: Logged but don't crash (silent failure)
- **JSON parse errors**: Logged but don't crash (invalid events ignored)
- **localStorage quota exceeded**: Silent failure (cache disabled)
- **Invalid events**: Logged + ignored (missing required fields)

## Extension Points

### Custom Base URL

```typescript
const client = new WorkflowRunnerClient('/custom/api/path');
```

### Custom Update Logic

```typescript
client.setUpdateHandler((runs) => {
  // Transform runs before storing
  for (const [id, rec] of runs) {
    if (rec.status === 'succeeded') {
      // Custom logic for successful runs
      notifyUser(`Run ${id} completed!`);
    }
  }
  // Standard store update
  syncToStore(runs);
});
```

### Debugging

```typescript
// Enable console logging
const client = new WorkflowRunnerClient();
client.setUpdateHandler((runs) => {
  console.log('[CLIENT UPDATE]', runs.size, 'runs');
  // ...
});
```

## Migration from Legacy

**Before (legacy `realtime.ts`):**

```typescript
const realtime = createRealtimeController({ runLifecycle, store });
realtime.startRealtimeUpdates();
```

**After (`WorkflowRunnerClient`):**

```typescript
// Client integrates directly with store
const client = new WorkflowRunnerClient(store);

// Default handlers are built-in, but can be customized
client.setUpdateHandler((runs) => {
  // Custom update logic if needed
  for (const rec of runs.values()) {
    upsertRun(store, mapRunRecordToUi(rec));
  }
});

client.setQueueHandler((pending, running) => {
  // Custom queue status logic if needed
  updateQueueDisplay(pending + running);
});

await client.start();
```

**Benefits:**

- ✅ Hydration on refresh (localStorage cache with 60min expiry)
- ✅ Resilience (reconnection with jittered backoff + polling fallback)
- ✅ Correctness (deduplication, gap detection, seq monotonicity)
- ✅ Workflow name resolution (batch fetching, multiple response shapes)
- ✅ Single source of truth (no duplicate ingestion paths)
- ✅ Queue status tracking (via 'queue' SSE events)
- ✅ Run removal on 404 (cleans up deleted runs)

## Testing

See `tests/client.test.ts` and `tests/manager-integration.test.ts` for comprehensive test coverage:

- ✅ Hydration from localStorage
- ✅ Sequence monotonicity
- ✅ Reconciliation de-duplication
- ✅ Gap detection
- ✅ Workflow name resolution
- ✅ Manager integration (bootstrap, no-legacy, cleanup)

## Troubleshooting

### Runs not appearing after refresh

**Cause:** Cold load not completing, cache expired, or cache corrupted

**Fix:**

```typescript
// Check localStorage cache
const cache = localStorage.getItem('lf-runs-cache');
const parsed = JSON.parse(cache);
console.log('Cache version:', parsed.version); // should be 1
console.log('Cache age:', Date.now() - parsed.cached_at); // should be < 3600000ms
console.log('Cached IDs:', parsed.run_ids); // should be array of run_ids

// Check network
// Look for GET /api/lf-nodes/workflow-runner/runs?status=...
// Look for GET /api/lf-nodes/run/{run_id}/status (reconciliation)
```

### "Unnamed Workflow" showing in UI

**Cause:** Workflow names not preloaded

**Fix:**

```typescript
// After fetching workflows
const names = extractWorkflowNames(workflows);
client.setWorkflowNames(names);
```

### SSE not connecting

**Cause:** Browser/proxy blocking SSE, or endpoint missing

**Fix:**

- Client automatically falls back to polling (check network tab for polling requests)
- Verify `/api/lf-nodes/workflow-runner/events` endpoint exists

### Duplicate events / stale state

**Cause:** Multiple clients instantiated, or legacy code still running

**Fix:**

- Ensure **one client instance** per application
- Remove all legacy `subscribeRunEvents` / `createRealtimeController` calls
- Check for deprecation warnings in console

### Queue status not updating

**Cause:** 'queue' SSE events not being received or handler not set

**Fix:**

```typescript
// Check if queue handler is set (default should exist)
console.log('Queue handler:', typeof client.queueHandler); // should be 'function'

// Monitor SSE events in browser DevTools
// Look for event type: 'queue' with payload: { pending, running }

// Check store state
const state = store.getState();
console.log('Queued jobs:', state.queuedJobs); // should reflect queue count
```

---

## Summary

`WorkflowRunnerClient` is the **only** way to ingest run state. It owns all network concerns and provides a clean, reactive interface via built-in handlers that integrate directly with the store.

**Key Points:**

- **Constructor requires store**: `new WorkflowRunnerClient(store)`
- **Built-in handlers**: Default `onUpdate` and `queueHandler` work out-of-the-box
- **Optional customization**: Override handlers only if needed
- **Cache v1 schema**: Stores run IDs only (300 max, 60min expiry)
- **Queue tracking**: Handles 'queue' SSE events automatically
- **404 cleanup**: Removes deleted runs from state
- **Jittered backoff**: Reconnection uses randomized delays to reduce thundering herd

Keep it simple: instantiate once with store, start once, stop on cleanup. The client handles everything else.
