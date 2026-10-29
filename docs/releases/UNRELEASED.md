# Next release

Draft notes for the release after [LF Nodes 4.0.0](4.0.0.md).

## New nodes

- **Text Region Masks** (`LF_TextRegionMasks`) labels precomputed detector masks
  using an ordered region table. Higher priorities win overlaps, with earlier
  rows winning ties. It returns disjoint masks as a batch and list, plus JSON
  metadata for areas, overlap losses and retained empty regions. Input masks
  are region-major; outputs are image-major.
- **Region Color Stats** (`LF_RegionColorStats`) compares two registered,
  same-size images by region in CIE Lab: means, medians, standard deviations,
  B-minus-A differences and CIEDE2000 over their same-coordinate mask
  intersection. JSON includes banding and row-profile heuristics; the latter
  reports the largest L* step between adjacent five-row windows and skips the
  first and last ten image rows. Both need visual interpretation. An
  outlined side-by-side preview persists in history.
- **Region Feature Similarity** (`LF_RegionFeatureSimilarity`) compares vision
  features by region using cosine similarity of coverage-weighted patch means.
  Pooled-only outputs instead require one encoded crop per region. Both sides
  must use matching model and crop settings; the model filename is recorded as
  supplied by the workflow.
- **Vision Patch Encode** (`LF_VisionPatchEncode`) accepts a core-loaded
  `CLIP_VISION` model, images and `center` or `none` crop, returning core
  `CLIP_VISION_OUTPUT`. It supports DINOv3's absent penultimate hidden state,
  which makes core `CLIPVisionEncode` raise in ComfyUI revision `651ca296a`.
  SigLIP2 models are rejected; use core's encoder for those.

All four have result widgets backed by durable history: labelled mask overlays,
per-region colour comparisons and numbers, searchable per-region
feature-similarity records, and encoded-image patch grids with tensor shapes.
Empty regions and unavailable measurements remain visible. The canonical E2E
workflow now includes synthetic CPU coverage and separate SAM3.1 and DINOv3
cases.

The nodes do not download weights; Core owns model loading and detector
inference. See [region comparison wiring and measurement limits](../REGION_COMPARISON.md).

## Saved workflows

Model card cover thumbnails now survive workflow save and reload instead of
staying blank until the node executes again.

## Behavior changes that shipped without notes

These changes reached users in 3.0.0 and are recorded here because neither the
3.0.0 nor the 4.0.0 notes named them. No socket was added, removed, renamed or
reordered.

- **Five nodes take lists.** `LF_Blend`, `LF_ImageToSVG`, `LF_Inpaint`,
  `LF_InpaintAdvanced` and `LF_LUTApplication` set `INPUT_IS_LIST = True`. Image
  batches and lists now pair item by item (Blend also broadcasts a single image
  or overlay), but a list of per-item controls (for example several opacities
  or LUT strengths) collapses to its first value. Workflows that fed such a list
  get the first value for every item; run the node once per setting instead.
- **CivitAI Metadata Setup combos.** On ComfyUI with the V3 schema,
  `LF_CivitAIMetadataSetup` declares its six optional model and sampler inputs
  as `COMBO` with `"None"` as the first option, so `vae` and `hires_upscaler`
  now default to `"None"`; older hosts default to the first installed file.
  Saved values still validate. Its `hires_upscaler` output carries the concrete
  upscale model list instead of `COMBO`.
- **Upscale Model Selector retag.** `LF_UpscaleModelSelector`'s `combo` output
  carries the concrete upscale model list instead of `COMBO`, matching the other
  selectors. Links into Core combo inputs are expected to keep working; this was
  not checked against every receiver.

## Save DDS and Pillow

LF Nodes requires Pillow 12.2.0 or newer instead of exactly 12.2.0. Save DDS
records the running Pillow version in each receipt instead of refusing other
versions.

Save DDS writes each file through a temporary file in its destination folder
and replaces the final path atomically with `os.replace`, removing the hard-link
filesystem requirement. If a later batch write fails, earlier files remain on
disk. The receipt retains the SHA-256 of the encoded bytes; staged and final
file readbacks and batch rollback have been removed.

## Workflow Runner

- **Direct submission.** Runner now posts prepared workflows directly to
  ComfyUI. The admission-provider entry-point loader and lease handling have
  been removed. Run supervision, terminal-history draining and cancellation
  remain; an ambiguous queue response is still recorded as an unknown outcome.
- **`WorkflowSubmissionPolicy` removed.** The class, the `WorkflowNode`
  `submission_policy` field, `WorkflowRegistry.get_submission_policy` and
  `get_workflow_submission_policy` are gone; the Runner never acted on them.
  Workflow definitions in external workflow roots that pass
  `submission_policy=` now raise `TypeError`; drop the argument.
- **Krea 2 VAE choice.** Generate, Style Reference, Style Blend and Identity
  Edit gain a VAE control. The official Qwen Image VAE is the first choice and
  the default; the other files in ComfyUI's `vae` folder follow, read once when
  the catalogue loads.
- **Krea 2 checkpoint choices.** The official Krea 2 Turbo INT8 ConvRot
  checkpoint is now the default. Other `.safetensors` checkpoints in
  `diffusion_models/KR2` are discovered when the catalogue loads; restart
  ComfyUI to refresh the list after installing one. ReID recipes continue to
  use the official Qwen Image VAE.
- **H3 prompt integration removals.** The unused planner, writer, compiler and
  audit helpers have been removed from `workflow_runner.prompts`, including
  the `minimax_h3_pipeline` and `minimax_h3_audit` modules. External workflow
  roots that imported them must update their imports. `compose_base_prompt`
  and `compose_full_reference_prompt` remain available.
