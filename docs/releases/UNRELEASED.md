# Next release — draft

Not published. Version selection and the final publication commit are deferred
to Luca. See [release readiness](../RELEASE_READINESS.md) for measured gates and
remaining prerequisites; this draft does not declare a full E2E pass.

## Highlights since v3.0.0

- **Simple idea to H3 video:** atomic prose-only Prompt Maker, optional review,
  vision and up to nine ordered references with independent dimensions. The
  phone-friendly Idea to Video orchestra hands the exact prose to the renderer.
- **Optional learned HD output:** native H3 generation followed by the accepted
  four-step latent refinement. Available across H3 rendering blocks and their
  three orchestras; Standard remains the default. Requires the optional external
  upscaler extension and checkpoint. See [HD setup](../llm/h3-hd-output.md).
- **Local model ergonomics:** local chat completions and exact-instance LM Studio
  load/unload nodes, including authenticated native discovery and model lifecycle.
  The writer can release its model before the video stage to free memory.
- **Reversible image editing:** named image-region extraction/composition and
  source-safe RGBA layer loading/composition. One editor session can combine
  base-image regions, fabric layers and optional cut masks; original alpha is
  locked by default. Labels and selection identity survive reordering and
  reload. See [image regions](../IMAGE_REGIONS.md) and
  [image layers](../IMAGE_LAYERS.md).
- **Animated GLB tools:** replace a selected material's texture without flattening
  its mesh, UVs, materials or animation, and scale selected joint subtrees around
  explicit anchors. Source files remain unchanged; stock Comfy 3D previews and
  savers consume the results. See [texture replacement](../GLB_TEXTURE.md) and
  [joint scaling](../GLB_SCALE.md). Character-specific Studio recipes remain
  consumer-owned, not new shipped Runner catalogue entries.
- **Sprite, tile and media tools:** settled-frame selection, loop-segment
  selection, seamless textures, isometric diamond tiles, audio saving/preview,
  and JSON key lookup by index.
- **Native RMBG-2.0:** the existing Background Remover gains a local RMBG-2.0
  choice, invocation-scoped model loading and source-alpha preservation.
  Shipped sprite/turnaround cards no longer depend on VNCCS. The default
  `u2net` choice, ordered mixed-size lists and all seven sockets are preserved.
- **Runner assemblies and history:** reusable multi-block orchestras, named
  artifact/text handoffs and durable child-run outputs, alongside proxy/auth
  hardening and phone-oriented controls.
- **Clearer catalogue:** separate LF Nodes and custom collections, quick section
  links, concise card descriptions, and seven new previews from real workflow runs,
  including a full stereo waveform of the user-accepted hearth sound effect.
  Unrelated queue/run updates now preserve mounted cards instead of restarting
  the custom collections' fade-in animations.
- **Compatibility fixes:** RGB editor effects and inpainting retain source alpha
  on RGBA images; file selection follows the selected file rather than a stale
  position; proxy URLs with hashes/query strings resolve frontend assets correctly.
  TRELLIS remesh/decimation inputs use native DynamicCombo wire formatting.
- **Release coverage:** the suite now exposes 154 public LF node types. The
  publication gate checks their canonical Titanic inventory separately from
  hydration and execution. Live gate outcomes and intentionally unexecuted cases
  are recorded in readiness notes, not inferred from unit-test totals.

## Compatibility and setup

Sixteen public nodes have been added since v3.0.0. This batch changes no existing
public output socket order. Existing H3 workflows keep Standard output unless HD
is explicitly selected. HD does not combine with Turbo; select Kitchen 20.

RMBG-2.0 now runs through LF's public Background Remover. Shipped sprite and
turnaround cards need its trusted four-file local model package, not VNCCS.
See [setup, licensing and output contracts](../BACKGROUND_REMOVER.md).
Older/downloaded/custom graphs containing `VNCCS_RMBG2` are not rewritten;
the [explicit temporary repair](../compatibility/vnccs-rmbg.md) remains available
for affected external versions. Nothing patches or uninstalls VNCCS automatically.

For users of the unreleased compiler-era Prompt Maker: `validation_report` now
reports authoring/review status, **not schema validation** (`valid: null`,
`validation: not_performed`). `visual_inventory` keeps its socket for compatibility
but does not claim extracted facts. See [Prompt Maker](../llm/h3-prompt-maker.md)
before relying on those older receipts. Review is not a correctness guarantee.

Restart Comfy to load updated Python nodes/workflow definitions. Existing
downloaded models are reused; no new model is downloaded automatically. LMS
lifecycle operations require workflow ownership of the selected instance;
failed/cancelled authoring may leave it loaded. See [LMS lifecycle](../llm/lms-models.md).

Region/layer compositors require exact ordered editor outputs and the original
source data; they do not guess pairing or overwrite source assets. Cut masks can
reduce or restore original coverage, not paint outside it. GLB transforms accept
self-contained GLB 2 inputs; texture replacement handles one image/material per
invocation, and joint scaling requires an explicit target recipe. These limits
are intentional and documented in the feature guides above.
