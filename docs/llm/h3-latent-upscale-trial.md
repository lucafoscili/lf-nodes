# H3 learned latent upscale — paired trial, 2026-09-26

**Keep as an opt-in output; do not replace the accepted default.** The
learned upscale plus short refinement adds visible detail, especially to the
face, hair and corset, while retaining the scene and action in five matched
frames. It also redraws small features. Following Luca's acceptance, the
[four-step HD option](h3-hd-output.md) is now wired into the rendering blocks and
H3-backed orchestras. The results below record the preceding experiments.

## Exact case

Reused the accepted renderer `40263f99-fbed-4706-9e18-11f16a15fb67` without another
LLM call: same final prompt, original Picture 1, seed 42, 124 frames at 24 fps,
ref2va and Kitchen/res_multistep 20-step first pass. The original executed graph
was recovered from its MP4 metadata and checked against durable Runner inputs;
the current reference image hash matches the original execution fingerprint.

The first pass is 768×1024 (0.786 MP). The learned 3D BF16 upscaler produces
1248×1664 (2.077 MP), preserving the exact 3:4 aspect ratio. This is a ~2 MP
portrait test, not a claim of 2560×1440 output. The second pass uses the same
model/sampler, a simple schedule, **4 steps / 0.25 denoise**. Those are local
experimental settings, not a validated upstream Kitchen preset. No Turbo LoRA,
temporal splitting, spatial tiles, or pixel decode/re-encode upscaling is used.
Target conditioning is rebuilt from the original prompt and reference at the
same dimensions as the upscaler target. Both video savers share original audio.

Source builder and structural tests: `scripts/experiments/h3_latent_upscale.py`
and `test_h3_latent_upscale.py`. Environment versions and recovery pointers:
[ecosystem update](h3-ecosystem-update.md).

## Execution and output

Comfy prompt `22c3fcf7-b7d8-4f40-8746-4424e8e27bc8` completed successfully with no
cached nodes in **391.46 seconds**. Logged first-pass sampling: 164 seconds;
second-pass sampling: 124 seconds. Total also includes cold model setup,
conditioning, learned upscaling, two video decodes and saves. Sampled GPU usage
was roughly 23,400–23,600 MiB on the 24-GiB RTX 4090; these readings are not a peak
memory measurement. The 4060 Ti was not used. No out-of-memory error occurred.

Outputs, under `ComfyUI/output/LF_Nodes/MiniMaxH3/LatentUpscaleExperiment/20260926/`:

- `seed42-4step025-baseline_00001_.mp4`: 768×1024, 1,110,350 bytes.
- `seed42-4step025-latent-upscale_00001_.mp4`: 1248×1664, 2,370,631 bytes.

Both have 124 decoded H.264 frames, 24 fps and a 5.167-second container duration.
All 163 AAC packet payload hashes, timestamps, durations and sizes match exactly:
stereo 32-kHz audio was preserved, not regenerated. This is byte-level evidence,
not a listening judgment. The upscaled video also loaded in the browser player
and reached its end without a reported playback error.

## Visual judgment and limits

Matched frames at 0, 1.25, 2.542, 3.833 and 5.125 seconds were inspected, including
equal-display-size crops. Subject detail improves visibly: hair strands, makeup
edges, corset seams and texture are more defined. Framing and action remain
matched in the samples; no obvious new structural defect was found there.
At phone-sized full-frame display the improvement is modest. Background stone
and pavement remain soft.

This is generative refinement, not a lossless enlargement: the eye becomes more
vivid red and jewelry/face details are redrawn. Full-motion smoothness and human
audio listening are not independently certified by the frame/packet checks.
The updated base render remains very close to the previously accepted video in
the five sampled frames, but the old/new render is not bit-identical.

No direct native-2-MP 20-step render was measured, so this test does **not** prove
a speed advantage over direct high-resolution generation. Other orientations,
longer clips, first/last-frame modes, other seeds and denoise schedules remain
untested. The next useful step is Luca's playback judgment, then an opt-in
output-quality choice using the existing two-block orchestra if accepted.

Ignored local evidence in `output/h3-upscale-20260926/`: accepted inputs/graph,
experiment graph, submission/history, before/after environment receipts,
`paired-comparison.json`, `paired-contact-sheet.png`, `paired-detail-crops.png`,
individual sampled frames and runtime logs. Do not overwrite accepted source
media or treat the recovery backups as disposable scratch files.

## Follow-up: four/eight steps and export quality

**Keep four steps for this candidate; defer eight-step promotion.** The extra
refinement did not produce a convincing visual improvement in this clip.
Lower-compression CRF 18 is a useful optional export, not a fix for generated
softness. No production renderer or phone orchestra default was changed.

Prompt `ddddb81c-91db-479a-bc4e-b723902c5a5e` completed successfully in **346.51
seconds**. The comparison shares the exact first-pass denoised AV latent,
reference, prompt, seed, target conditioning and original audio. Both branches
use the same learned upscale and 0.25 denoise; only the second-pass schedule
changes from four to eight steps. The base and four-step branch were cached.
The four-step CRF 23 export has all 124 compressed video packets and their timing
identical to the previous upscale, despite differing container metadata.

Eight-step sampling took about **250 seconds**, versus **124 seconds** logged
for the previous four-step sampling. These are sampling-stage measurements,
not cold end-to-end comparisons: the new total includes cached inputs, exports
of the four-step result, learned upscaling, eight-step sampling, decode and saves.
The simple schedules start at the same noise level; eight steps add intermediate
sampling points, not a higher initial denoise strength.

Each decoded result was exported directly at H.264 CRF 23 and CRF 18, without
recompressing an existing MP4. Encoder headers confirm the requested CRF values.
Files under `ComfyUI/output/LF_Nodes/MiniMaxH3/RefinementComparison/20260926/`:

| File | Bytes |
| --- | ---: |
| `seed42-4step-crf23_00001_.mp4` | 2,372,085 |
| `seed42-4step-crf18_00001_.mp4` | 4,797,916 |
| `seed42-8step-crf23_00001_.mp4` | 2,295,220 |
| `seed42-8step-crf18_00001_.mp4` | 4,567,876 |

All four contain 124 decoded frames at 1248×1664 and 24 fps, with a 5.167-second
container duration. All 163 AAC packets, payloads and timing match across all
four files. Both CRF 18 versions loaded in the browser player and reached the
end with no reported playback error. A Windows connection-reset callback was
logged after successful execution; neither render history nor player reported
failure. No service restart or ecosystem update was attempted in this follow-up.

Two independent still-frame reviews compared the same five timestamps and
equal-area, equal-display-size crops. Eight steps slightly redraw the face,
eyeliner, earring and corset trim; some areas appear smoother rather than more
detailed. The scene, silhouette and action match in these samples. Pavement
remains soft, and no clear overall quality gain or new major structural defect
was found. CRF 18 preserves slightly cleaner fine hair/corset/stone textures at
both step counts, but is nearly indistinguishable at phone-sized full-frame
display while roughly doubling file size.

This supports four steps as the better time/quality tradeoff **for this clip**,
not a universal H3 ceiling. Continuous-motion quality and human listening remain
for Luca's judgment; reaching the end of playback is only a compatibility check.
More seeds, other schedules and direct native-resolution generation remain
untested. Preserve both candidates for comparison rather than relabeling eight
steps as a higher-quality preset.

Replay: `h3_latent_upscale.py --compare-refinement`. Five CPU structural tests
passed, and live prompt validation accepted all four saver branches. Ignored
local evidence lives in `output/h3-refinement-20260926/`: source/comparison API
graphs, submission, full history, `comparison-summary.json`, frame samples and
`refinement-crf18` / `compression-4step` / `compression-8step` comparison sheets.
