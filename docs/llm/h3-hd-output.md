# Optional H3 HD output

Choose **Output quality → HD · learned 4-step** on any H3 rendering block, or
on **Idea to Video**, **Sprite Loop from One Still**, or **3D-Ready Character
Turnaround**. **Standard · native** remains the default and keeps the previous
graph, output geometry, dependencies and audio path.

HD generates the usual native-resolution video, applies the learned 3D latent
upscaler, then refines with four RES multistep steps, a simple schedule and
0.25 denoise. These are the locally accepted settings from the
[paired comparison](h3-latent-upscale-trial.md), not an upstream universal preset.
The original prompt, references, seed, frame count and audio are retained.
First/last-frame and intermediate-guide conditioning is rebuilt at the target
resolution. Still/frame/sprite consumers read the refined decode; their declared
final sprite or sheet dimensions do not change.

HD is a generative finishing pass: it can redraw fine face, jewelry, texture or
costume details. It needs more GPU memory and time, and is not an identity or
motion repair guarantee. Use **Baseline · Kitchen 20** when a block also exposes
Fast/Turbo. HD with Turbo is rejected before upload staging; the workflow does
not silently switch recipes. Original MP4 encoder quality is unchanged.

## Optional prerequisites

Install `benjiyaya/ComfyUI-MinimaxH3-Latent-Upres`, which provides
`MMH3LatentUpscaleWithModelParams` and `MMH3UltimateUpscale`, and place
`minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors` under
`ComfyUI/models/latent_upscale_models/`.

Restart Comfy after installing the extension or updating these Python workflow
definitions. The catalogue omits the HD choice if its nodes or checkpoint are
missing. Standard stays available without them. Submission checks the same
optional requirements; no model download or service restart happens in a run.

## Output canvases

HD means approximately two megapixels, not a promise of a specific 2K standard.
All dimensions are aligned to 32; wide/tall canvases can differ slightly in
aspect ratio because of that alignment.

| Aspect choice | Standard | HD |
| --- | --- | --- |
| 16:9 | 1344×768 | 1920×1088 |
| 4:3 | 1024×768 | 1664×1248 |
| 1:1 | 768×768 | 1440×1440 |
| 3:4 | 768×1024 | 1248×1664 |
| 9:16 | 768×1344 | 1088×1920 |
| 21:9 | 1536×672 | 2208×960 |

HD video filenames gain `-hd4`; outputs still occupy their existing Runner
output slots. No public LF node sockets were added or changed. References and
frame ordering are not resized into a shared image batch.

## Ownership and evidence

- Shared finishing pass: `modules/workflow_runner/workflows/minimax_h3_hd.py`.
- Eleven H3 render cards: `minimax_h3.py`; raw-prose renderer:
  `minimax_h3_prompt_video.py`; three assemblies: `orchestration.py`.
- Contracts: `test_minimax_h3_hd.py`, `test_minimax_h3_prompt_video.py`, and
  `test_h3_video_orchestra.py`. They cover Standard preservation, HD dependencies,
  all reference modes, guide chaining, canvas choices, audio/prose preservation,
  early invalid-input failure and assembly forwarding.
- Integrated REF2VA smoke on 2026-09-26:
  `d1d07961-1580-427a-b376-36a034128c38`, successful in 18.81 seconds. Comfy reused
  the already-tested four-step sample/decodes and executed the saver. Output:
  `LF_Nodes/MiniMaxH3/HDReleaseSmoke/20260926/seed42-hd4_00001_.mp4`, 1248×1664,
  124 frames, 24 fps, 5.167 seconds. This is cached integration/export evidence,
  not a fresh GPU timing measurement or a restarted catalogue UI test.
- Fresh FL2VA first/last-anchor run on 2026-09-26:
  `2b65fef8-acd2-4f45-a1e7-1f1f2dfa1a14`, successful in 359.43 seconds.
  Both base sampling and the four-step refinement executed; model loaders and
  static parameters were partly cached. Output:
  `LF_Nodes/MiniMaxH3/HDReleaseSmoke/20260926/first-last-seed43-hd4_00001_.mp4`,
  1248×1664, 124 decoded frames, 24 fps, 5.167 seconds, stereo AAC audio.
  Five sampled frames retain the composition while the cape moves; the browser
  player reached the end without a playback error. This checks an identical
  opening/ending anchor, not arbitrary transitions between different images.
  Local evidence: `output/h3-hd-release-20260926/`.

The actual uncached four-step render and comparison are recorded separately in
the paired trial. Full creative acceptance across all aspect ratios, long clips,
different endpoint anchors, intermediate guides and sprite/turnaround branches
remains outside these two short-clip checks. Continuous-motion judgment and
human audio listening remain for Luca; frame inspection and playback completion
alone do not certify those qualities.
