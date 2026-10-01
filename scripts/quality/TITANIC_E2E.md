# Titanic E2E gate

`titanic_e2e.mts` turns the checked-in canonical ComfyUI workflow at
`scripts/quality/fixtures/E2E.json` into an honest,
programmatic release gate. It loads the real LiteGraph document in Comfy's
frontend and uses `app.graphToPrompt()` as the only executable prompt
authority. The older offline workflow converter is intentionally not used: it
cannot faithfully resolve Titanic's reroutes, virtual links, disabled nodes,
and asynchronously serialized widgets.

The command never starts or stops ComfyUI or LM Studio, saves the workflow,
clears a queue, downloads a model, or issues a global interrupt.

The maintainer's workflow under ComfyUI's user directory is a working
projection. Refresh the repository authority deliberately with:

```powershell
corepack yarn sanitize:titanic
```

The deterministic sanitizer preserves nodes, links, groups, and other graph
metadata while removing private filenames/paths, transient editor state,
history, preview URLs, credentials, and adult-content references. Its tests
also prove idempotence. Review and commit both the fixture and its expected
SHA-256 in `titanic_cases.json`.

## Hydration gate

With ComfyUI already running and idle:

```powershell
corepack yarn test:titanic
```

This checks workflow identity, the seven disabled-policy branches, real
frontend hydration, LF custom-widget DOM mounting, authoritative prompt
serialization, exhaustive classification of every active output node, and
inventory coverage for every currently published LF node type.
The canonical `E2E.json` bytes are checked again before exit.

## Bounded CPU experience check

```powershell
corepack yarn test:titanic -- --execute-smoke
```

This additionally queues the three established CPU widget specimens plus the
new deterministic media slice: `LF_SeamlessTile`, `LF_IsoDiamondTiles`, and
`LF_SelectLoopSegment`. It requires exact terminal history, their versioned
receipts, generated preview URLs, live widget updates, durable `ui.lf_output`,
and an unchanged workflow file. It never calls a provider or changes model
residency.

### Synthetic GLB, region and layer cases

The six Studio-supporting public nodes have two dedicated CPU cases. With
Comfy already running, idle and coordinated with other users:

```powershell
corepack yarn test:titanic -- --full --case cpu.glb-texture-scale
corepack yarn test:titanic -- --full --case cpu.image-regions-layers
```

Use `--cache-none` at Comfy startup for repeatable actual-work checks. A first
uncached run on a warm-cache service may explicitly add `--accept-warm-cache`,
but these cases still require execution events from all six new LF nodes and
reject their cached execution. Repeating the same warm-cache run is therefore
not an execution pass. The gate does not restart Comfy or clear its cache.

The GLB case replaces the texture of a tiny animated, skinned synthetic quad,
scales its joint chain, and previews the result through stock
`Preview3DAdvanced`. The gate fetches the history GLB, checks its header and
declared length, and checks
native viewport hydration; it does not mistake that widget for LF's image
dataset. Geometry and animation quality still require visual inspection.
The region/layer case edits named regions, composes unequal-sized RGBA layers,
and exercises combined base regions and layer cut masks without model calls.

Inputs are the three pinned assets in `fixtures/titanic-cpu/`, not workstation
or user media. The harness binds their local repository paths only in the
submitted prompt, leaving the serialized workflow untouched. This assumes
Comfy and the harness can access the same repository filesystem.

```powershell
python -I scripts/quality/update_titanic_cpu_coverage.py --check
```

The generator verifies the synthetic assets, appended graph and manifest.
Without `--check`, it regenerates those repository-owned fixtures; it never
reads or edits the maintainer's external working projection. If refreshing
Titanic from that older projection, reapply the synthetic append and review
the resulting graph before committing.

## Full active-workflow gate

```powershell
corepack yarn test:titanic -- --full `
  --allow-gpu `
  --allow-models `
  --allow-writes `
  --allow-unpinned-inputs `
  --allow-local-llm `
  --local-model-id <exact-model-key> `
  --local-instance-id <exact-loaded-instance-id> `
  --allow-interaction
```

Full execution is serial and fail-closed. It requires an idle queue and, by
default, a Comfy process launched with `--cache-none`; use
`--accept-warm-cache` only when cached coverage is intentionally acceptable.
Every active output belongs to exactly one reviewed case in
`titanic_cases.json`. The seven mode-2 provider/input branches remain explicit
policy `SKIPPED` entries and never masquerade as passes.

The fixed repository manifest pins the canonical workflow SHA-256, not only its node/link
counts, so a topology or widget change cannot inherit previously reviewed
resource grants. Custom manifests are intentionally unsupported: every
resource class is an exact reviewed value and unknown classes fail before any
service or queue interaction. Evidence records the manifest path, hash, size,
schema, and repository authority. A warm-cache exhaustive pass reports
`full-workflow-coverage`; only actual target execution may report
`full-workflow-execution`.

`--full --case <id>` is a **targeted branch execution**, not a full-workflow
pass. Its evidence records `requestedMode: "full"`, `mode: "targeted"`, the
selected case IDs, every granted authority flag, and the achieved gate. Only a
successful run that selected and passed every coverage case with execution
proven by `--cache-none` or exact target execution events may report
`achievedGate: "full-workflow-execution"` and `fullWorkflowPass: true`.

The image-editor case is a real model-backed transaction rather than a resume
smoke test. Playwright selects an input, opens Inpaint, applies deterministic
sampling controls, draws a physical canvas stroke, verifies the multipart
request and returned mask pixels, saves the edited snapshot, and only then
resumes the workflow. Its execution recorder is installed before submission.
For the exact owned prompt it requires nodes `463 → 441 → 442 → 449 → 450 →
455 → 418` to appear in Core's actual-work events and forbids every one from
the exact cache list. The downstream nodes must run after the interaction's
resume timestamp. Node 441's comparison history must carry the committed edit
at the rail ingress. Node 418's executed-event artifact URLs must separately
match its exact terminal-history URLs after the deliberately
appearance-changing filter chain. The gate also requires exact editing-session
JSON cleanup. The browser's live Comfy client ID is sent separately as
`caller_client_id` on recovery, processing, and completion requests; it is
never copied into or substituted for the dataset's immutable
`owner_client_id`. The evidence includes a wrong-owner exact-context recovery
probe, verifies that it returns no dataset, and proves that the pending,
recovered, and completed owners are unchanged.

Queue preflight, polling, and before/after history snapshots detect foreign
work; they are not an atomic lease. External coordination remains required.
On editor failure the harness waits only five seconds for an in-flight process
request, never releases a session while that request remains active, requests
only exact-prompt cancellation, preserves the exact context evidence, and
reports `ABORTED` when filesystem and recovery cleanup cannot be proven.

The local LLM/VLM nodes currently omit `model` from their OpenAI-compatible
requests. Consequently, the gate uses LM Studio's native `/api/v1/models`
catalogue and requires exactly one entry across all `loaded_instances`; its
parent model key must equal `--local-model-id`, its instance ID can be pinned
with `--local-instance-id`, and it must advertise vision support. The
OpenAI-compatible `/v1/models` endpoint is deliberately not used because LM
Studio can list every downloaded model there while JIT loading is enabled. The
gate does not unload a foreign model or choose one implicitly.

The separate `llm.local-lifecycle` case exercises `LF_LMSLoadModel`,
`LF_LocalChatCompletions`, both reviewed and review-disabled
`LF_H3PromptMaker` paths with two unequal-size image references, and
`LF_LMSUnloadModel`. The checked-in workflow keeps model and endpoint fields
portable; immediately before the owned frontend submission, the gate binds
`--local-model-id` and `--lm-studio-url` only to the manifest-declared nodes.
An unloaded downloaded model may be loaded by the case. Reusing an already
loaded model additionally requires `--local-instance-id`, making the exact
instance subject to unload explicit. The graph passes that loader-emitted ID
to the unload node, and the gate verifies after success that this model has no
resident instance. No global unload is issued.

## Outcomes and evidence

- `PASS`: submitted work reached terminal success and every declared history,
  artifact, interaction, and widget assertion passed.
- `FAIL`: prerequisites passed, but execution or an assertion failed.
- `BLOCKED`: required service, authority, fixture, model, or queue ownership is
  absent. Exit code `2` keeps this distinct from a green test.
- `SKIPPED`: the workflow itself intentionally disables that policy branch.
- `ABORTED`: owned work could not be terminalized safely.

Each run writes ignored evidence under `output/titanic-e2e/`: a
`lf.titanic-e2e.v1` `summary.json` and `junit.xml`. Each executed case hashes
the prompt captured at the frontend's actual `api.queuePrompt` boundary, then
requires that digest to match the prompt tuple in Core's exact
`/history/<promptId>` entry. The harness injects a fresh UUID through Core's
supported client-supplied `prompt_id` field, so even an identical concurrent
foreign prompt cannot be mistaken for owned work during uncertain-response
recovery. The prompt itself is never persisted, avoiding
accidental disclosure of workflow content or credentials. The earlier
`graphToPrompt()` hash is labeled hydration-only and is not execution proof.
