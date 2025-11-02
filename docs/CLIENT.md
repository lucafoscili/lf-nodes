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
const client = new WorkflowRunnerClient(baseUrl?: string);
```

**Parameters:**

- `baseUrl` (optional): API base URL. Defaults to `/api/lf-nodes`. Trailing slash is stripped.

### Methods

#### `setUpdateHandler(handler: UpdateHandler): void`

Sets the callback invoked when run state changes. This is the **single integration point** with the application.

```typescript
type UpdateHandler = (runs: Map<string, RunRecord>) => void;

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
client = new WorkflowRunnerClient()
     ↓
client.setUpdateHandler(...)
     ↓
[workflows load]
     ↓
client.setWorkflowNames(...)
     ↓
client.start()
     ├─→ loadCache() ────────────→ onUpdate (optimistic)
     ├─→ coldLoadRuns() ─────────→ onUpdate (authoritative)
     └─→ SSE.connect() ──────────→ (listen for events)
```

### Runtime (SSE Events)

```plaintext
Server emits SSE event
     ↓
client receives 'run' event
     ↓
applyEvent(rec)
     ├─→ validate (run_id, status, seq present?)
     ├─→ gap detection (seq > last+1?)
     │       ├─→ YES: reconcileRun(run_id) [async, de-duped]
     │       └─→ NO: continue
     ├─→ upsertRun(rec)
     │       ├─→ seq <= last? → REJECT (no update)
     │       └─→ seq > last? → ACCEPT
     │               ├─→ lastSeq[run_id] = rec.seq
     │               ├─→ runs[run_id] = rec
     │               ├─→ fetchWorkflowNames([rec.workflow_id]) if missing
     │               └─→ emitUpdate()
     └─→ onUpdate(runs) → manager → store
```

### Reconnection

```plaintext
SSE error
     ↓
es.onerror
     ├─→ startPollingFallback() [every 3s]
     └─→ setTimeout(start, backoffMs)
         ↓
         [exponential backoff: 1s → 2s → 4s → ... → 30s]
         ↓
     client.start() [retry]
         ↓
         [if SSE succeeds]
         ↓
         es.onopen
         ↓
         stopPollingFallback()
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

- **Instantiate once** at the manager/root level
- **Call `start()` exactly once** per application lifecycle
- **Call `stop()` on cleanup** (unmount, destroy)
- **Keep `onUpdate` handler fast** (< 5ms)
- **Map run records in one place** (DRY: `mapRunRecordToUi()`)
- **Trust the client** for network concerns (don't open EventSource elsewhere)

### ❌ DON'T

- **Don't open EventSource elsewhere** (breaks single-source-of-truth)
- **Don't fetch runs directly** (use client's cold load)
- **Don't poll manually** (client handles fallback)
- **Don't mutate `runs` Map** (it's a snapshot; mutations won't propagate)
- **Don't make `onUpdate` async** (fire-and-forget side effects only)
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

The client saves runs to `localStorage` for fast hydration on refresh:

```typescript
// After every update
emitUpdate()
     ↓
     saveCache()
     ↓
     localStorage.setItem('lf-runs-cache', JSON.stringify(runs))
```

**Limits:**

- Keeps **200 most recent** runs (sorted by `updated_at` desc)
- Omits `result` and `error` fields (reduce size)
- Handles quota exceeded gracefully (silent failure)

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
const client = new WorkflowRunnerClient();
client.setUpdateHandler((runs) => {
  for (const rec of runs.values()) {
    upsertRun(store, mapRunRecordToUi(rec));
  }
});
await client.start();
```

**Benefits:**

- ✅ Hydration on refresh (localStorage cache)
- ✅ Resilience (reconnection + polling fallback)
- ✅ Correctness (deduplication, gap detection, seq monotonicity)
- ✅ Workflow name resolution
- ✅ Single source of truth (no duplicate ingestion paths)

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

**Cause:** Cold load not completing or cache corrupted

**Fix:**

```typescript
// Check localStorage
localStorage.getItem('lf-runs-cache') // should be valid JSON

// Check network
// Look for GET /api/lf-nodes/workflow-runner/runs?status=...
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

---

## Summary

`WorkflowRunnerClient` is the **only** way to ingest run state. It owns all network concerns and provides a clean, reactive interface via `onUpdate`. Keep it simple: instantiate once, bind once, start once, stop on cleanup.
