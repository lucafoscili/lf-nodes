# Workflow Runner showcase

Working snapshot: **2026-08-31**. This covers all 41 shipped workflows (39 blocks
and two orchestras), not a claim that the catalogue is finished or that every
workflow has passed visual acceptance. Active work can advance beyond this
snapshot; update the affected row after inspecting the result. The manifest
currently contains **28 curated covers**; seven samples need further quality
work, five workflows are blocked on setup/access, and the sound-effects example
awaits listening acceptance. None of those 13 receives a substitute or fabricated
cover.

The checked-in [cover manifest](../web/deploy/assets/workflow-runner/heroes/samples.json)
records curated assets, actual source outputs, run identities, and display
transforms. It is the source for distributable cover provenance. Case names below
refer to local receipts in `output/hero-cards/`; those disposable records and their
original outputs are not packaged assets or public download links. A case in
`cases.json` or `h3-cases.json` is a proposed input, not evidence that it ran.

## Reading the status

- **Validated**: terminal execution and the expected result nodes are present in
  the available run evidence. This does not establish visual quality.
- **Curated**: the actual example was selected for a cover in the manifest. This
  is sample-level acceptance, not a guarantee for other prompts or inputs.
- **Pending**: execution or review is unfinished, or no terminal showcase receipt
  is available. **Blocked** names the missing prerequisite or authority.
- **Rejected**: the result is not suitable showcase evidence, even if its run
  reported success. A replacement needs its own execution and review.

## Coverage

| Shipped workflow ID | Execution evidence | Sample decision / remaining work |
| --- | --- | --- |
| `krea2_generate` | Validated; manifest source runs and `explorer-source-a1`, `icon-source-a1` | Curated generated-image example. |
| `krea2_style_reference` | Validated; `style-reference-a1` | Curated reference/output example; style guidance is not identity preservation. |
| `krea2_style_blend` | Validated; `style-blend-a1` | Curated two-reference/output example; not a measured blend ratio. |
| `krea2_identity_edit` | Validated; manifest source run and turnaround cleanup child | Curated before/after example. |
| `krea2_character_restage` | Validated; manifest source run | Curated before/after example. |
| `krea2_outfit_change` | Validated; `outfit-a1` | Curated before/after example. |
| `krea2_pose_change` | Validated; `pose-a1` | Curated before/after example. |
| `krea2_feature_edit` | Validated; `feature-a1`, replacement `feature-a2` | Rejected by visual review, including the replacement; no curated cover. |
| `krea2_character_restyle` | Validated; `restyle-a1` | Curated before/after example. |
| `identity_cleanup_restage` | Validated complete orchestra; manifest records both stages | Curated original-input/final-output example from that orchestra. |
| `character_turnaround_orchestra` | Validated complete orchestra; `turnaround-orchestra-a1` | Curated with limits: generated views, minor matte halos, non-calibrated geometry. |
| `minimax_h3_generate_video` | Validated; `h3-generate-video-a1` | Curated actual market-video frame; sampled visual review only, not exact step-count or audio acceptance. |
| `minimax_h3_animate_image` | Validated; `h3-animate-image-a1` | Curated actual input, wave, and return frames; sampled visual review only, audio unreviewed. |
| `minimax_h3_first_last_frame` | Validated; `h3-first-last-frame-a1` | Curated sampled neutral-to-wave transition; not exact morphing, pixel-perfect endpoints, or audio acceptance. |
| `minimax_h3_anchored_sprite_loop` | Validated; `h3-anchored-sprite-loop-a1`, including atlas/frame outputs | Curated actual normalized loop evidence; all 24 sprites reviewed. Matte fringe remains; no pixel-perfect seam or audio claim. |
| `minimax_h3_directed_view` | Validated three actual children of `turnaround-orchestra-a1` | Curated with limits; selected views and sampled temporal sheets reviewed. |
| `minimax_h3_character_turnaround` | Validated; `h3-character-turnaround-a1`, including atlas/frame outputs | Curated this block's own four saved cutouts, not orchestra substitutes; matte/detail/scale and generated-view limits remain. |
| `minimax_h3_reference_restage` | Validated; `h3-reference-restage-a1` | Curated actual reference/output example; broad outfit/color continuity, with a real style change and unproven facial likeness. |
| `minimax_h3_character_swap` | Validated; `h3-character-swap-a1` | Rejected for this showcase: recognizable foreground replacement, but large unrequested camera pullback, cropped opening and distant extra people. |
| `minimax_h3_outfit_transfer` | Validated; `h3-outfit-transfer-a1` | Rejected for this showcase: blue coat and recognizable identity retained, but a close-up opening followed by a full-body pullback violates the fixed-framing request despite a full-body reference. |
| `minimax_h3_sprite_motion` | Validated; `h3-sprite-motion-a1` | Curated this run's own input/wave/return frames; an opaque motion clip, not a finished transparent atlas or seamless loop. |
| `minimax_h3_scene_sheet` | Validated; `h3-scene-sheet-a1` | Rejected: the prop reference's white backdrop/floor becomes a conspicuous hard-edged plane inside the generated scene. |
| `assemble_cardinal_turnaround` | Validated actual assembly child of `turnaround-orchestra-a1` | Curated composition of four actual saved cutout PNGs, not the exact saved sheet image; minor halos and scale/detail differences remain. |
| `compare_images` | Validated; `compare-a1` | Curated composition of the workflow's two emitted preview images. |
| `image_detail_4k` | Validated; `detail-4k-a1` | Curated matched detail crops; not evidence that every inferred detail is faithful. |
| `image_sheet` | Validated; `sheet-a1`, `sheet-a2` | Curated actual labelled sheet. |
| `image_to_dds` | Validated; `dds-a1` | Curated preview decoded from the saved DDS, not substituted source pixels. |
| `image_to_svg` | Validated post-fix run `svg-a5`; earlier `svg-a1`–`svg-a4` rejected | Curated actual source beside a rendering of the saved three-color SVG, preserving orange flame/dark logs; not the quantized PNG preview. |
| `load_metadata` | Validated; `metadata-a1` | Curated source image and selected fields from the actual metadata output; omissions disclosed. |
| `remove_bg` | Validated; `remove-background-a1`, `remove-background-explorer-a1` | Curated before/after example with visible transparency. |
| `sort_json_keys` | Validated; `sort-json-a1`, `sort-json-a2` | Curated exact input/output text; preserve values and output key order. |
| `trellis2_image_to_textured_mesh` | Validated; `trellis-single-a1` | Curated actual input beside front/rear three-quarter renders of the saved GLB; not a topology or rig-readiness guarantee. |
| `triposplat_image_to_splat` | Validated; `triposplat-a1` | Rejected for rear-view quality; file creation is not geometric acceptance. No cover promoted. |
| `caption_image_vision` | `caption-a1` returned a proxy-authorization error; `caption-a2` completed against local Qwen3.5 4B but returned empty text. Controlled provider probes reproduced 500 reasoning tokens with no answer; 2048 allowed completed captions on the 4B and shared 27B Qwen sessions | Budget/empty-answer fix implemented and CPU/provider checked. Original Runner sample remains rejected; rerun the actual workflow before promoting a cover. |
| `simple_chat` | History normalization and proxy-auth/status contracts checked on CPU; live UI configuration inspected | Blocked: the local proxy requires a secret header that the stock chat does not send; Runner cookies do not replace it. The status endpoint now reports this instead of false readiness. No live assistant reply/export or cover is claimed; browser authentication remains a setup decision. |
| `svg_generation_gemini` | Blocked on hosted-API authority/configuration | Wiring checks are not an API execution or accepted SVG. |
| `ace_step_remix` | Blocked on approved source, external-action authority, and backend configuration | A real remix needs listening review; a waveform alone cannot establish audio quality. |
| `stable_audio_3_sfx` | Live: one hearth and four axe candidates generated; float WAV decode, LF node preview restore, and Runner history/reload playback pass | Listening acceptance is pending. Hearth has a quiet tail, not a proven seamless loop; no accepted showcase cover yet. |
| `youtube_reference_intake` | Blocked on approved source and external-action authority/configuration | No downloaded-media sample is claimed. |
| `t2i_15_lcm` | Blocked: declared Dreamshaper8 checkpoint is missing | Do not silently substitute another checkpoint and call it this showcase. |
| `t2i_illustrious_xl` | Validated execution; `illustrious-a1` | Rejected for prompt non-adherence; unexpected ice cream and requested appearance/outfit drift. No cover promoted. |

## What the examples do and do not prove

Covers contain actual output pixels or explicitly described representations of
actual non-raster results. Allowed presentation changes include contain-fit,
labels, a transparency backdrop, disclosed shared transparent-margin or matched
detail crops, decoding a saved format, and typesetting exact output text. They
must not retouch away defects,
invent missing views, replace a failed result, or present source pixels as a
decoded output. Strip embedded prompts and private execution metadata from the
distributed raster; keep its source relationship in the manifest.

For the accepted turnaround example, all 124 frames in each of three camera-turn
clips were CPU-decoded. Visual review inspected 13 sampled frames per clip, each
lossless selected PNG, and the assembled contact sheet. It did **not** include
continuous playback, every unsampled frame, audio listening, or calibrated 3D
measurement. The local `turnaround-stage-review.json` records the observations
and the `keep_with_limits` decision. Generated rear details, minor matte halos,
and roughly -1.9% to +2.3% alpha-height variation remain; these views are not proof
of identical geometry, rig readiness, or reconstruction quality.

The Assembly and turnaround-orchestra covers compose the four separately saved
RGBA cutouts, with a shared transparent-margin crop and shared display scale.
They do not reproduce the saved contact-sheet image verbatim. The mesh covers
use mechanical renders of the actual GLBs with their saved materials; the
manifest records the renderer, camera, lighting, and display crops.

For Animate Image, all 124 frames were decoded, with 17 temporal samples and five
native stills visually inspected alongside the prepared source. The accepted
cover uses actual wave and return frames. Mild face/garment-detail changes remain;
continuous playback, unsampled-frame quality, audio, and a seamless loop are not
verified. Other completed H3 runs still need their own final review decisions.

Generate Video, Reference Restage, and the standalone Character Turnaround also
have sample-level acceptance recorded in the manifest. Their temporal sheets
were reviewed, not continuous playback or audio. The restage's more realistic
style is retained; the standalone turntable uses its own actual cutouts and does
not inherit the orchestra's evidence. Remaining H3 samples stay pending until
their own review is complete.

An orchestra sample must retain the complete parent/child relationship. Reusing
its real Directed View or Assembly children is valid; inventing separate
standalone runs is not. In this turnaround review, live Core history for those
children was unavailable, so provenance uses retained Runner child records and
metadata in their actual saved PNGs, without inventing Core prompt IDs.

Finally, a green status, manifest, hash, or unit test cannot judge appearance,
motion, text correctness, or sound. The original SVG false-green run is excluded
despite its success status. Keep pending rows pending until their own outputs
have been exercised and reviewed; keep unsuitable samples rejected even when
the workflow technically ran.

## Focused follow-up — 2026-08-31

The rejected H3 Swap, Outfit Transfer, and Scene Sheet videos contain their
actual prompt graphs. Those confirm REF2VA, Kitchen attention, 20 steps,
`res_multistep` / `simple`, Max reference detail, 124 frames, and the intended
reference order. The failures are not explained by a hidden Turbo profile or
reversed input wiring. The source character/market PNGs are 1152×1728 (2:3),
not the 9:16 described in the disposable case plan; Max preprocessing preserves
reference aspect rather than center-cropping. This discrepancy does not prove
the cause of the camera pullback.

Next controlled H3 experiments, not yet execution evidence:

- **Outfit Transfer:** retain its seed, settings, and references; append only an
  explicit head-to-boots, constant-subject-size, locked-camera instruction from
  the opening through final frame. Identity, coat, and setting already work.
- **Scene Sheet:** retain the sheet; clarify that its environment panel alone
  supplies floors/walls, while the prop panel supplies the stall but not its
  pale studio floor. The unwanted plane is present in the actual reference.
- **Character Swap:** the market reference contains a background person, so
  scene preservation competes with the single-person request. Test a cleaned
  scene reference separately from any camera-prompt change.

The empty-caption cause was reproduced with two sequential raw provider probes
using the same image, classifier system/user text, temperature, and seed. A
separate local Qwen3.5 4B alias used an 8192-token context, one parallel session,
and no saved-setting changes:

| Response budget | Provider outcome | Observed time |
| --- | --- | --- |
| 500 | `finish_reason=length`; all 500 completion tokens were reasoning, visible content empty | 8.234 s |
| 2048 | `finish_reason=stop`; 1354 completion tokens, including 947 reasoning tokens; completed campfire-icon description | 19.937 s |

Evidence: disposable `caption-budget-500.json` and `caption-budget-2048.json`
beside the other local case receipts. This isolates the hidden output budget as
the cause of the reproduced empty answer. The shared response helper accepts an
empty `message.content` without checking `finish_reason`, explaining the earlier
false-green Runner result. These direct probes are **not** a new Runner pass or
accepted hero example. The completed description recognizes the orange flame
and dark crossed logs; its detailed interpretation is not a ground-truth label.

Follow-up implementation: the Runner template now defaults to 2048, with an
optional response-budget override under Advanced settings. The public node's
published default and sockets remain unchanged. The classifier opts into a
shared answer-text guard and fails instead of emitting successful empty text;
other callers of the permissive response parser retain their existing behavior.

One authorized direct request to an already-loaded local 27B Q6 Qwen session
then returned HTTP 200 and `finish_reason=stop` in 64.421 s:
1430 completion tokens, including 662 reasoning tokens, and a 3345-character
answer accepted by the production response guard. Image, prompt, temperature,
and seed stayed unchanged. Receipt: `caption-budget-2048-shared-q6.json` beside
the prior probes. The receipt was saved successfully; the disposable script's
console print subsequently hit a Windows Unicode-encoding error. No duplicate
request was submitted. Visual review confirms the broad campfire description,
but exact color codes and small shape claims are not verified ground truth.

**Defer:** live Runner/Titanic acceptance and hero promotion. Comfy was never
started alongside the user-owned Qwen session, and the model's configuration
and lifecycle were left untouched. The conflicting character-classifier system
message versus general-caption request merits a separate prompt test; it was
deliberately held constant here. No provider guard was relaxed.

Caption follow-up checkpoint: 65 caption/registry tests, 38 focused frontend
tests, and the CPU publication gate passed (484 pytest cases, two skipped;
12 quality unittest cases; 140 public mappings checked). TypeScript, Sass, Vite,
and Runner builds passed; the deployed JS/CSS contains the Advanced disclosure
and validation-error expansion. These are not live browser or full-graph tests.

Connection follow-up: source inspection found that the classifier also omitted
the shared secret on its default relative proxy request. It now authenticates
that server-side transport only, without putting credentials in saved inputs,
outputs, or absolute/custom endpoint requests; authenticated redirects are
disabled. Simple Chat's status poll now applies the same secret requirement as
its POSTs. This fixes misleading readiness, not browser authentication: the
reviewed local configuration exposed no browser-authenticated proxy injection
path.
No access-policy, CORS, model, or service-lifecycle change was made. The normal
reviewed launcher has no CPU-only variant; a temporary CPU-only test instance
and the browser authentication path were considered, but not started or enabled.
The connection fixes passed 107 focused classifier, multimodal, proxy, status,
and chat tests. Independent review caught and closed a URL-normalization escape
before credential lookup; canonical relative paths alone receive the header.

After Garage released its serialized provider window, one additional direct
request tested a cleaner user prompt: a concise Markdown paragraph describing
visible subject, composition, style, and colors, with character details only
when present and no invented biography/context or precise color codes. The
classifier system message, source image, seed, temperature, resident model, and
2048-token budget were unchanged. The request finished normally in 16.953 s,
using 319 completion tokens (188 reasoning) and returning a 645-character
paragraph accepted by the response guard. Receipt:
`caption-prompt-clean-shared-q6.json`. This is a useful concise-caption candidate,
not a general accuracy or speed benchmark; the wording also requests less
detail than the old prompt. The shipped prompt was not changed, and this remains
direct-provider evidence rather than a Runner result or accepted hero.

## Checkpoint scope

The expanded catalogue and final safety pass completed the frontend build, all
578 frontend tests, and 1,090 Runner tests (five skipped). The CPU publication
gate passed 595 behavioral tests (three skipped), 140 public mappings, and the
23 Titanic unit/sanitizer contracts. Real-browser checks loaded every curated
image at phone and desktop widths, exercised keyboard/image navigation, and
verified the missing-image fallback. The node-authoring contracts guided the SVG
palette fix: its public sockets and list/batch behavior remain unchanged.

Titanic passed real frontend hydration and the existing `fs.read-unpinned`
branch, including the public ImageToSVG path and its preview/display outputs.
The run explicitly accepted warm-cache coverage and reported
`targeted-branch-coverage`, **not** a full-workflow E2E pass. The canonical fixture
was unchanged. Local evidence is in
`output/titanic-e2e/2026-08-30T23-04-00-201Z/summary.json`.

## Deferred-work checkpoint (2026-09-03)

**Keep:** cold-cache Titanic hydration, CPU smoke, targeted `cpu.headless`, and
targeted `gpu.vae-roundtrip` all passed against the live Comfy instance. The
final post-restart hydration loaded 355 nodes and 468 links, compiled 294 prompt
nodes, mounted 270 custom widgets, classified all 120 active outputs, reported
zero widget/page/coverage failures, recognized the absolute Windows `main.py`
argv with `--cache-none`, and left the canonical fixture unchanged. Its evidence
is `output/titanic-e2e/2026-09-03T05-42-04-248Z/summary.json`. The smoke, CPU,
and GPU evidence is retained beside it under `output/titanic-e2e/`.

The Stable Audio card also completed a new real-browser run from its live form:
run/prompt ID `784a198d-d602-40a1-9e58-6cfe953cab31`, seed 46, eight sampling
steps, and no cached nodes. Runner restored the exact succeeded run after a page
reload and exposed both the playable WAV and `lf.audio_file.receipt.v1`. The
receipt reports a 2.972154-second, 44.1 kHz, two-channel `pcm_f32le` file with
131,072 samples per channel and 1,048,668 bytes. Numeric inspection found finite
samples, a -3.16 dBFS peak, and about 2.09 seconds below -60 dB after the last
active window. Two short energy clusters may be the requested crack and thud or
an unintended second hit; listening, not waveform inference, decides that.

Three live defects found along the way are now covered by focused regressions:
the package loader uses canonical imports so dataclass workflows no longer fail
before registration; Titanic accepts relative, Windows, and POSIX paths ending
in `main.py` while rejecting unrelated/malformed arrays; and changing Runner's
selected workflow rerenders the floating action button. A clean restart loaded
all 58 catalogue entries, including all 10 Krea cards, without the earlier Krea
import error. The final shared worktree passed 1,091 Runner tests (five skipped),
479 Runner frontend tests, 24 Titanic unit tests, frontend TypeScript checking,
and `git diff --check`. The two Python warnings are the known deprecated
`workflow_runner.controllers` import path.

**Drop from the shipping catalogue:** the orphaned
`trellis2/multiview-to-mesh.webp` belongs to the intentionally removed
multiview wrapper. It is not included in `samples.json`; its exact bytes and
SHA-256 were preserved outside the repository in the pre-H3 checkpoint before
the undeclared deploy-path copy was removed.

**Defer:** perceptual selection among the five audio candidates; the full
Titanic gate, because LM Studio has no loaded model instance; and
canon/promotion. The seven mode-2 provider branches remain explicit policy
skips and were not called.
