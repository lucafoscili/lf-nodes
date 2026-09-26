# Release readiness — 2026-09-26

**Candidate preparation; no release published.** Optional four-step H3 HD is
wired, Standard remains the default, and publication contracts cover the new
capabilities. The next version has intentionally not been selected or stamped.
The current `3.0.0` version already has a release tag: publishing this checkout
under that identity is not a valid next-release operation.

## Scope

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

**New unresolved runtime blocker:** the sprite orchestra's background-removal
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

## Measured gates

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

## Live evidence boundaries

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

1. The updated catalogue is now loaded after the reviewed JOC handover; the
   phone-sized proxy form exposes Output quality with Standard selected. Retain
   the remaining live Standard/HD execution and optional-node/checkpoint
   availability checks required by the advertised release scope. Catalogue
   browser acceptance alone does not certify those generation paths.
2. Complete whichever remaining model/provider/editor live cases are required
   for the release's advertised scope; record unavailable prerequisites as such.
3. Have Luca select the next version and accept the candidate. Update runtime,
   Python and package metadata together, adjust the version-specific contract,
   and promote the draft into the selected version's release notes.
4. Inspect the final publication diff and run its metadata checks. Pushing the
   relevant release change to `main` can trigger registry publication; keep that
   as an explicit, separately authorized action. No push, tag or publication was
   performed during this preparation.

## Final focused-execution update

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
