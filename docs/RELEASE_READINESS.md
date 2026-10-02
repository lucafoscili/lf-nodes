# Release readiness — 2026-10-02

**4.0.0 accepted; publication authorized on 2026-10-02.** Optional four-step H3 HD is
wired, Standard remains the default, and publication contracts cover the new
capabilities. Luca approved the HD motion/audio sign-off and explicitly authorized
publication to the Comfy registry and GitHub. Runtime, Python and package metadata
use `4.0.0`. The [versioned notes](releases/4.0.0.md) explain the breaking TRELLIS.2
Runner migration. The existing `3.0.0` release identity must not be reused.

This publication commit records acceptance, not a completed external upload.
The publication workflow must finish successfully before reporting the release
as live. Earlier dated pending-sign-off statements below are historical and are
superseded by this acceptance; their test and coverage limits still apply.

The first publication run (`36964880923`) stopped before upload because the clean
CPU environment lacked PyAV, imported by the audio encoder and its tests. PyAV
is now explicit in both installation manifests and pinned to the locally tested
17.0.1 in the CI lock; Core already requires 17.0 or newer. The same dependency
review found the real SVG palette tests would skip without `vtracer`/`svgwrite`;
their locally tested versions are now pinned in CI too. The upload, tag and
GitHub release steps did not execute in that failed attempt.

The next clean run (`36965284717`) passed the main and H3 CPU cohorts, then
exposed a missing `pytest-asyncio` plugin in the isolated orchestra tests. The
CI lock now uses the same pytest 9.1.1 / pytest-asyncio 1.4.0 pair as the accepted
local rehearsal, plus its direct AnyIO and SQLite test dependencies. The remaining
isolated groups were reviewed together for missing imports. This is CI setup,
not a change to installed-node behavior; this attempt also stopped before
publication.

## 4.0.0 candidate checks — 2026-10-02

**Keep — prepared locally, not published.** Commit `1eec2d6` stamps the three
version fields, retains the historical 3.0.0 socket migration and promotes the
draft into explicit 4.0.0 notes. Commit `8ff11b8` fixes a Windows release-tool
encoding defect found while inspecting the generated body: Git output is now
decoded as UTF-8, preserving Unicode notes and commit subjects.

- Full CPU publication command passed on the stamped candidate: **1,924 pytest
  passes**, four existing Windows symlink-permission skips, twelve gate unit
  tests, compilation and all 154 public node mappings. After the encoding-only
  fix, the focused metadata/generator/publication-workflow batch passed all
  **15 tests**, including the new Unicode regression. Unchanged groups were
  not rerun for that tooling-only fix.
- `corepack yarn check:release` passed: **608 frontend tests in 71 files**,
  32 Titanic unit contracts, three example-sanitizer tests, all 17 shipped
  examples unchanged, and the complete TypeScript/CSS/production build.
  The initial invocation stalled before collecting tests and was stopped;
  an identical retry completed without configuration or dependency changes.
  The cause is unproven; that interrupted invocation is not a pass.
- Rebuilt `web/deploy` has no tracked or untracked publication drift. Its
  253 tracked compiled files remain unchanged.
- The tracked archive of `8ff11b8` contains **1,341 files**, including all 253
  compiled frontend files. Archived runtime/Python/package versions are
  consistently `4.0.0`; release-note file links resolve inside the archive.
  No dotenv, local output, dependency environment or Git runtime paths were
  included. This is a source-package check, not a fresh GPU installation.
- The real release-note command generated the expected `v3.0.0` to candidate
  range and the TRELLIS migration text; Unicode was inspected after the fix.
  A read-only remote check found no `v4.0.0` tag at preparation time.

Evidence and the replayable package check are in
`output/release-4.0.0-20261002/`; generated archives, logs and the GitHub-body
preview remain local and ignored. The subsequent readiness-record commit
changes documentation only. Existing live node/browser/media evidence below
is reused; no services, models or workflow executions changed in this pass.

At candidate handoff, HD acceptance and publication approval were pending.
Both were supplied by Luca on 2026-10-02, as recorded above. The version-changing
push to `main` publishes through the existing registry/tag/GitHub pipeline.
No runtime or dependency change is part of this final publication pass.

## Direct RMBG-2.0 — 2026-10-02

**Keep — existing public node extended, shipped consumers migrated.**
`LF_BackgroundRemover` now offers RMBG-2.0 without VNCCS. The default `u2net`,
six old model choices, required inputs and all seven output indices are
unchanged. One locally loaded model serves the complete image list and is
released afterward; source alpha is intersected with inferred coverage.
See [setup and implementation](BACKGROUND_REMOVER.md).

The four-file local model package is reused without download or modification.
Its native class plus strict safetensors loading works on the installed
Transformers 5.10.1, where automatic pretrained loading failed with
`Config.model_type`. No dependency downgrade or model-code patch was made.
The external VNCCS installation and all custom project graphs are untouched.
Its repair is now a legacy/custom-consumer concern, **not a prerequisite for
current shipped LF sprite/turnaround cards**. This supersedes that requirement
in the dated rehearsal and consolidation records below.

Fresh evidence, with the workstation and services authorized by Luca:

- CPU publication gate: **1,894 pytest passes**, four existing Windows
  symlink-permission skips, twelve gate unit tests, compilation and all 154
  public mappings passed. Then the two migrated sprite/cardinal suites were
  added to that gate: **29 additional passes**, plus a passing rerun of its
  twelve unit tests. The current manifest therefore covers 1,923 passing
  pytest cases; unchanged groups were not rerun for a manifest-only edit.
  Twelve existing Pillow deprecation warnings remain non-blocking.
- Native browser: `u2net` still selected by default, RMBG-2.0 appended to the
  actual dropdown, all seven sockets retained. Canonical Titanic **hydration
  passed** (390 nodes / 515 links, unchanged fixture). This is not a full
  Titanic execution claim.
- Fresh same-frame A/B: Core prompt
  `6a0450df-60ad-4961-b202-ce9f17e3fba3`, no cached nodes. Three 1920×1088 RGB
  frames through LF and repaired VNCCS: identical RGB, maximum alpha delta
  **1/255**, foreground IoU above **0.99998** on every frame. Checkerboard
  comparison and native-pixel detail were visually inspected; no visible
  edge regression on this specimen. This is bounded equivalence evidence,
  not a promise of perfect matting for every subject.
- Runner `sprite_loop_cut` passed as
  `b9ef35a1-8147-4654-882a-a9a9ebea67f0`, about 27 seconds observed. Only saved
  video decoding was cached; loop selection, direct LF matting, registration
  and saving executed. It produced 24 RGBA 256×256 frames and a transparent
  1536×1024 atlas (`atlas-6x4_00004_.png`). The atlas was visually inspected;
  hands/boots fit, backgrounds are transparent and grounding is consistent.
  H3 generation was not repeated for this downstream-only change.
- Fresh mixed-size execution `e7d6da0f-4f51-4568-987d-e8c80a806836` retained
  640×368, 512×288, 640×368 order; the primary batch contains exactly the two
  matching-size items. All nine distinct durable preview URLs remained readable.
- Independent code review found no must-fix. CPU tests cover cleanup after
  inference/consumer failure and an escaped predictor not retaining weights.
  Exact peak GPU allocation was not measured; CPU-only inference and arbitrary
  third-party model packages were not live-certified.

Evidence: `output/rmbg2-20261002/`,
`output/playwright/rmbg2-20261002/`, and
`output/titanic-e2e/rmbg2-20261002-hydration/`.
No version, tag, push, upstream PR or release was published.

The final cache-cleanup restart exposed a stale service-owner Kitchen pin
(0.2.35 versus Core's required/installed 0.2.36). The first J.O.C. attempt
stopped at the dependency check without replacing the running service.
Velora owner commit `25c900a5` aligns that one pin and its regression test;
66 operation tests passed with one existing reparse-permission skip, followed
by the real GPU-hidden dependency probe. Identity, storage and idle guards
are unchanged. The subsequent named J.O.C. restart succeeded at
2026-10-01 23:30:37 UTC (October 2 locally), leaving Comfy and Runner ready/idle.
Afterward the public schema was unchanged, all nine saved preview URLs returned
HTTP 200, and Runner restored the sprite run's persisted succeeded status.
Unrelated Velora working changes were preserved.

## Fresh-package rehearsal — 2026-10-01

**Keep — clean source/frontend installation passed; not a blank-machine GPU
installation or a registry publication.** The manual-install instructions now
name the dependency step using ComfyUI's own Python. No public node contract,
runtime default, installed model or running service changed in this rehearsal.

- A clean archive of `db0dcb0` contained 1,334 files and all 253 compiled
  frontend files, with no private runtime/dependency/credential-file paths.
  Extraction checks parsed 646 Python sources and resolved all six relative
  JavaScript imports. Eight focused contracts passed, including an actual
  headless Visual Novel import through the inert Comfy host boundary.
- Fresh `corepack yarn install --immutable` and `corepack yarn build` passed
  using Node 22.13.0 / Yarn 4.6.0. All 253 shipped frontend files matched the
  rebuilt files after line-ending normalization; seven extra JS source maps
  are ignored build intermediates. Python checks reused the installed 3.11.9
  environment; no fresh Python dependency installation or full live node
  registration was performed.
- The inspected `Comfy-Org/publish-node-action@v1` checks out the repository
  again before publishing, while comfy-cli 1.22.0 packages tracked files.
  A narrow check now requires the compiled frontend to be committed after the
  build and before publication. Its exact shell body passed for the clean
  build and independently failed for modified tracked JS and new untracked JS;
  ignored source maps do not fail it. No registry publish command was invoked.
- The unaffected LF frontend needs no artifact repair. The external VNCCS
  decoder bug reproduced against an untouched upstream archive; its corrected
  snapshot passed all three CPU regressions. The shipped opt-in patch was
  applied and reversed in isolation, matching the repaired and original bytes
  exactly. ZIP/nested-checkout targeting and the existing Windows Git checkout
  were checked without modifying the live VNCCS installation.
- Final candidate `95c6b61` contains the installation guidance, patch and
  publication check. Its archive has 1,336 files, including all 253 frontend
  files and the exact patch bytes, with no private runtime directories. Thirteen
  release-workflow, version and release-note contracts passed independently.
  Prior live behavior evidence is reused because runtime code is unchanged.

Evidence: `output/fresh-install-20261001/` contains the package rehearsal
summary, candidate archive and upstream/repaired decoder snapshots. The
disposable extracted/build tree remains at
`C:/Users/Luca/AppData/Local/Temp/lf-release-rehearsal-6852a9c2621042e6a93b526e2ae0c1aa/`.
At that rehearsal, the [VNCCS note](compatibility/vnccs-rmbg.md) was the
setup/recovery entry point; it now covers older/custom consumers only.
Upstream distribution is still pending; the temporary patch is
not silently installed. No version, tag, push, PR or release was published.

## Updated host compatibility — 2026-10-01

The [Comfy ecosystem update](COMFY_ECOSYSTEM_UPDATE.md) is complete: Core
`651ca296` (0.38.0), frontend 1.53.10, Manager, ControlNet Aux and Ultimate SD
Upscale were updated with local changes preserved. Post-update Titanic
hydration/six-node targeted execution, a fresh full HD sprite orchestra, and
bounded Ultimate/Aux inference passed. All 154 LF schemas are unchanged.
The update record names recovery refs, exact evidence and upstream caveats;
it does not expand the release's acceptance scope or resolve VNCCS distribution.

## Consolidation checkpoint — 2026-10-01

**Keep — this consolidation's live checks passed; candidate acceptance and
publication remain separate decisions.**
There are now **154 public LF node types**, sixteen additions since v3.0.0.
The canonical Titanic contains **390 nodes / 515 links**, including the six
new image-region/layer and GLB nodes. Its new CPU cases use three checked-in
synthetic inputs, not private Studio assets or workstation paths. The release
draft now includes the Studio-supporting public contracts and editor fixes;
consumer-owned Studio workflows are not claimed as shipped Runner cards.

The publication gate now includes region/layer composition, GLB texture/joint
editing, image identity, editor input entries, RGBA processing, the exact
synthetic specimen, and catalogue presentation/accepted covers. Two obsolete
tests expecting missing Prompt Maker and Sound Effects covers were corrected
to their accepted assets. Windows Vitest defaults to serial worker startup
after concurrent startup stalled before collecting tests; non-Windows
settings are unchanged.

Fresh offline verification:

- `python -I scripts/quality/run_ci_contracts.py`: **PASS**, 1,876 pytest
  tests and twelve gate unit tests; four Windows symlink-permission skips.
  Compilation and static contracts passed for all 154 mappings. Twelve Pillow
  deprecation warnings remain non-blocking.
- Frontend: **PASS**, 608 tests across 71 files, three example contracts,
  all seventeen tracked examples sanitized without changes, and the complete
  TypeScript/CSS/production build. The initial two-worker startup stall is not
  counted as a pass; serial execution passed, and a default-settings focused
  rerun passed after the Windows configuration change.
- Titanic: **PASS**, 32 offline contracts and exact regeneration check for
  390 nodes, 515 links and three pinned assets, rerun after the live gate fix.
  The broader unchanged CPU/frontend evidence above was reused.

The sprite failure was traced to an eagerly referenced, undefined decoder in
the **external** VNCCS package. Local owner commit
`b843cc0caf1671e917f4567605b21269a03fc9cc` removes that unsupported mapping
entry without changing weights, preprocessing or the selected decoder. Three
CPU regression tests pass, followed by successful live cut and orchestra runs.
LF Nodes does not automatically repair the external installation: at this
checkpoint, fresh installs still needed that owner fix or an equivalent upstream
fix (superseded for current shipped cards by direct RMBG-2.0 above). The candidate
ships an [explicit patch with preview and rollback](compatibility/vnccs-rmbg.md), so
applying the repair does not require access to this workstation's local commit.
See the [repair record](WORKFLOW_RUNNER_SHOWCASE.md#sprite-decoder-repair--2026-10-01).

Fresh live verification, after Luca authorized the shared runtime:

- **Hydration passed:** 390 nodes, 515 links, 294 LF custom widgets, all 134
  active outputs classified. Canonical bytes remained unchanged by each run.
- **Region/layer targeted execution passed:**
  `5ddb6d61-1431-4407-8c19-d68518980663`; all four new LF nodes actually ran.
  Live/durable previews, ordered unequal-size layers and cut-mask composition
  passed. Enlarged output inspection confirmed selected regions changed while
  unselected regions remained intact.
- **GLB targeted execution passed:** `a38db356-77a0-417c-930d-c9120eff6639`;
  texture replacement, joint scaling and stock preview actually ran with no
  cached nodes. The visible 384×341 renderer loaded the exact terminal-history
  GLB. Geometry, replacement color and animation controls were inspected.
- **Complete sprite orchestra passed:** fresh H3 restage followed by real
  background removal/cutting, 24 transparent frames and atlas export in 272
  seconds. The separate saved-video cut passed first. See the repair record
  for child IDs, timings and sampled-frame visual judgment. No new catalogue
  cover or human motion-quality acceptance is implied.

The first GLB attempt completed backend work but failed its browser assertion:
the viewer was offscreen and production Vue omits the debug pointers used by
the check. The gate now centers the node and observes its exact renderer and
loaded artifact. The 280-pixel node allocation also visibly clipped controls;
the canonical viewer is now 500×600. This is the sole specimen change since
the region/layer pass; inputs, links and execution behavior are unchanged.
Final fixture SHA-256:
`1e2fa82b557465119aa2ac406ae461dac1502956e87451627ef6f867fcb29ca7`.

The achieved Titanic level is **hydration plus targeted branch execution**,
not exhaustive Titanic execution. Provider/model-heavy/editor branches not
selected here retain their earlier limits. Stock 3D previews remain temporary
Core assets; the new gate does not claim restart-durable GLB storage.

JOC started the stopped stack. The first attempt started the proxy but lost
its status observation; a fresh read established proxy-ready/Comfy-absent
before a successful managed retry. No manual launch or bypass was used.
The final queue was idle and Comfy/proxy were left available. The live shipped
catalogue has 48 entries and exposes the accepted hearth cover. No new credentials,
model downloads or dependency upgrades were needed for these checks.

Evidence: `output/titanic-e2e/consolidation-20261001-a1/` preserves the first
attempt and region/layer pass; `consolidation-20261001-glb-final/` preserves
the corrected GLB pass. Sprite receipts live in
`output/live-consolidation-20261001/`; inspected screenshots are in
`output/playwright/{sprite,native3d}-20261001/`. Commands and cache
prerequisites are in the [Titanic guide](../scripts/quality/TITANIC_E2E.md#synthetic-glb-region-and-layer-cases).
The September evidence below remains historical.

Catalogue acceptance remains 35 curated covers out of 48 shipped workflows;
the other thirteen have no accepted sample. No new cover is promoted by this
consolidation. No version, tag, push or publication has been made.

## Previous checkpoint — 2026-09-26

### Later catalogue probes — 2026-09-26

Fresh showcase runs added evidence after the gates below: reviewed H3
Idea to Video (reasoning off), local Illustrious XL, Iso Ground Tiles, and the
local prompt-to-tiles orchestra succeeded. Six genuine previews were added;
the [showcase log](WORKFLOW_RUNNER_SHOWCASE.md#catalogue-qol-and-fresh-samples--2026-09-26)
records exact runs and remaining cover gaps. Catalogue UI checks passed 593
frontend tests; this is not a rerun of the complete publication gate.

The subsequent reviewed JOC handover restarted the stopped Comfy stack and
loaded the new catalogue. Desktop and phone-sized HTTPS-proxy browser checks
passed for covers, collection separation, shortcuts, and card navigation;
Output quality is visible with Standard selected. No new generations were
queued during this post-restart check; remaining execution limits below stand.

**Runtime blocker recorded at this checkpoint:** the sprite orchestra's background-removal
stage failed to load its model (`name 'HierarAttDecBlk' is not defined`). H3
restaging succeeded, but no final atlas was produced. Resolve this dependency
failure and replay the complete sprite orchestra before claiming that path is
release-ready. Separately, Qwen returned no final writer answer with reasoning
`vision`; a simpler prompt with reasoning `off` and review on succeeded. This
remains a reliability limitation, not a fixed default behavior.

### Prepared candidate scope

- 148 public LF node types; ten additions since v3.0.0. The count and its
  publication contract now agree.
- Canonical Titanic: 372 nodes / 490 links, including all 148 public LF types.
  A publication test compares the specimen's types with current node mappings
  so new nodes cannot silently lose coverage.
- H3 HD: eleven rendering cards, the exact-prose renderer, and all three
  H3-backed orchestras. The shared helper preserves native defaults and the
  original audio path; optional requirements affect only the HD choice.
- [Draft release notes](releases/UNRELEASED.md), [HD guide](llm/h3-hd-output.md),
  and [Titanic gate instructions](../scripts/quality/TITANIC_E2E.md) describe
  user-facing changes and reproducible checks.

## Measured gates — 2026-09-26

| Gate | Result |
| --- | --- |
| Immutable dependency installation | PASS |
| CPU publication contracts | PASS — 1,614 passed; four Windows symlink-permission skips |
| Frontend publication gate | PASS — 590 UI tests, 29 Titanic contracts, three example contracts, sanitized examples, TypeScript/CSS/production build |
| Real Comfy Titanic hydration | PASS — 372 nodes, 490 links, 284 custom widgets, all active outputs classified |
| Focused live executions | PASS — every one of the ten new public node types executed; see exact scope below |
| Integrated reference HD export | PASS — cached sample/decode, real saver execution |
| Fresh first/last-anchor HD render | PASS — base and four-step HD sampling, decode, MP4/audio and browser playback |

CPU gate: `python scripts/quality/run_ci_contracts.py`. This now includes the
media tools, LMS authentication/lifecycle, prose authoring, H3 HD, orchestras,
sequence execution and optional-model readiness. The CPU host boundary forbids
accidental real Core execution imports and fails closed on an unmocked
`validate_prompt` call.

The four skipped checks require Windows symlink creation permission: one audio
directory-escape check, one model packaged-directory check and two output-file
registration checks. They are skips, not passes. Twelve Pillow `getdata`
deprecation warnings are non-blocking.

Frontend gate: `corepack yarn check:release`. Initial hydration also recorded
pre-existing third-party asset 404s and legacy browser-to-LMS CORS warnings;
no page exceptions or LF widget/coverage failures were reported. These warnings
are not a claim that every external frontend extension is healthy.
After the fixture corrections, its 29 focused contracts were rerun successfully;
the unchanged frontend build/UI-test evidence was reused.

## Live evidence boundaries — 2026-09-26

The canonical fixture includes CPU tile/loop checks, a separate durable WAV
saver, and a local model lifecycle case. The latter loads an explicit downloaded
vision model, exercises local chat and both H3 review settings with two
unequal-size references, joins their completion, and unloads the exact instance
emitted by the loader. It does not unload unrelated models.

The first media smoke caught a fixture serialization error: the isometric
node's UI value occupied its numeric scale field. Core accepted only the other
target; the gate detected the partial validation failure, cancelled that exact
owned prompt and verified an empty queue. That aborted attempt is preserved,
not counted as a pass. Explicit seed controls correct the isometric and text-join
widget ordering. The next attempt caught a second fixture issue: a single-frame
list was connected where loop selection needs a temporal batch of at least three
frames. The specimen now uses the existing deterministic six-frame batch.
Neither failure was hidden or counted as a pass; final reruns are tracked below.

Reading the first successful model output exposed a contradictory fixture brief:
it asked for a medieval town while supplying a line and a plain blue rectangle.
The review-disabled result invented a person; the reviewer instead replaced the
requested town with stripe motion. The final fixture asks for the line animation
actually supported by its images. Both final prose outputs follow that brief,
include a compact Picture 1 subject anchor, and retain the expected H3 sections.
This is a simple semantic spot-check, not proof of arbitrary reference grounding
or official-schema compliance. Review remains a second model opinion, not a
validator.

HD evidence and visual limitations are in the [HD guide](llm/h3-hd-output.md).
The new first/last-anchor run took 359.43 seconds for a 124-frame, 1248×1664
clip. Both sampling passes ran; some static/model-loader nodes were cached.
The reference export reused the previously accepted sample and is not a speed
benchmark. Continuous-motion acceptance and human audio listening remain for
Luca; sampled frames and successful playback alone cannot certify them.

This is **not an exhaustive Titanic execution pass**. Provider-disabled
branches remain explicitly skipped. Legacy model-heavy, workstation-input and
interactive-editor branches are not requalified merely by fixture presence,
hydration or CPU contract tests. Targeted passes report targeted scope.

Ignored local evidence:

- `output/release-readiness-20260926/`: CPU gate, skip reasons, frontend build
  and complete frontend publication gate logs.
- `output/titanic-e2e/release-20260926-*/`: per-run JSON/JUnit evidence, exact
  prompt identity, target execution and canonical fixture immutability.
- `output/h3-hd-release-20260926/`: generated graphs, histories, media metadata
  and inspected frame samples for reference and anchored HD runs.

## Before publication

1. Keep native RMBG-2.0's trusted local model package and licensing explicit in
   the install story. Older/custom VNCCS graphs remain separate; the bundled
   opt-in patch is not an upstream release or an automatic repair. Retain the
   recorded HD acceptance and limits of model/provider/editor checks required
   by the advertised scope. The October consolidation above
   is complete for its named branches, not an exhaustive release of every
   installed third-party dependency or Titanic branch.
2. Complete whichever remaining model/provider/editor live cases are required
   for the release's advertised scope; record unavailable prerequisites as such.
3. The 4.0.0 candidate is selected and stamped across runtime, Python and package
   metadata, with the version-specific contract and migration notes updated.
   Luca accepted the candidate and optional HD motion/audio judgment, then
   separately authorized publication on 2026-10-02.
4. Inspect the final publication diff and run its metadata checks. Pushing the
   relevant release change to `main` can trigger registry publication; keep that
   as an explicit, separately authorized action. This authorization is now
   supplied; verify registry upload, tag identity and GitHub release completion.

## Final focused-execution update — 2026-09-26

All final targeted runs passed, with no foreign queue work observed. The final
fixture hash is
`5a3ed5677af61c62f01e9cc36b6ae15a7c9fec3991100426542151b6cb0658f4`.
Its last change only aligned the two authoring briefs; earlier media/audio/JSON
evidence remains applicable to those unchanged branches.

| Case | Actual-work evidence |
| --- | --- |
| Existing CPU widget slice | `a68475fc-e8ce-4c5b-846a-a2782d7aec14`: periodic sampler, sprite normalization and new settled-frame selector executed |
| New media slice | `d57517c5-a0cc-464c-950f-50052b0eb3c4`: seamless tile, isometric tiles and loop selection executed; receipts, live previews and durable history passed |
| JSON key by index | `ac5a7e58-ddc1-463d-a3ee-eaf704c1e169`: key selection and displayed result executed |
| WAV saver | `4ce75dd4-76e4-410b-8235-4a2e21d0fafe`: audio creation and saver executed; independent decode confirmed mono PCM float32, 8 kHz, 2,000 samples / 0.25 seconds |
| LMS + local vision + H3 | `3ca4aa11-eb34-4c55-ad25-aefd08f67424`: load, local chat, review-on authoring, review-off authoring, join and exact unload all executed; 27.95 seconds |

The final LMS run used the downloaded 4B Qwen model, two 512×320 / 448×150
references, and reasoning off. Both authoring receipts reported prose mode and
two references; review-on completed and review-off skipped. The model inventory
was empty before and after; no unrelated instance was unloaded. Comfy's queue
was empty at handoff.

These runs used the existing warm-cache service. Exact events prove the listed
targets performed work; supporting image/model/static nodes sometimes reused
cache. They are not cold-start benchmarks and do not report a full-workflow pass.
The WAV is an intentionally silent fixture; successful decode is not an audio
quality listening test. Sampled tile/atlas previews were visually inspected.

Final local evidence directories are `release-20260926-smoke-final`,
`release-20260926-audio-json` and `release-20260926-lms-final` under
`output/titanic-e2e/`. Earlier failed/aborted attempts are preserved alongside
them. No services were restarted, no models downloaded, and no release version,
tag or remote publication was changed by these checks.
