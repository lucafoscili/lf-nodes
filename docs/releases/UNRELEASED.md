# Next release

Draft notes for the release after [LF Nodes 4.0.0](4.0.0.md).

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

## Pillow

LF Nodes requires Pillow 12.2.0 or newer instead of exactly 12.2.0. Save DDS
records the running Pillow version in each receipt instead of refusing other
versions.

## Workflow Runner

- **`WorkflowSubmissionPolicy` removed.** The class, the `WorkflowNode`
  `submission_policy` field, `WorkflowRegistry.get_submission_policy` and
  `get_workflow_submission_policy` are gone; the Runner never acted on them.
  Workflow definitions in external workflow roots that pass
  `submission_policy=` now raise `TypeError`; drop the argument.
- **Krea 2 VAE choice.** Generate, Style Reference, Style Blend and Identity
  Edit gain a VAE control. The official Qwen Image VAE is the first choice and
  the default; the other files in ComfyUI's `vae` folder follow, read once when
  the catalogue loads.
