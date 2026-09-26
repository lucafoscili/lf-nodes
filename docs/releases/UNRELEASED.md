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
- **Sprite, tile and media tools:** settled-frame selection, loop-segment
  selection, seamless textures, isometric diamond tiles, audio saving/preview,
  and JSON key lookup by index.
- **Runner assemblies and history:** reusable multi-block orchestras, named
  artifact/text handoffs and durable child-run outputs, alongside proxy/auth
  hardening and phone-oriented controls.
- **Clearer catalogue:** separate LF Nodes and custom collections, quick section
  links, concise card descriptions, and six new previews from real workflow runs.
  Unrelated queue/run updates now preserve mounted cards instead of restarting
  the custom collections' fade-in animations.
- **Release coverage:** all 148 current public LF node types have a canonical
  Titanic specimen; new-node omissions are checked automatically. CPU publication
  contracts include the new tools and H3/HD/orchestration paths. Live gate outcomes
  and intentionally unexecuted cases are recorded separately in readiness notes.

## Compatibility and setup

Ten public nodes have been added since v3.0.0. This batch changes no existing
public output socket order. Existing H3 workflows keep Standard output unless HD
is explicitly selected. HD does not combine with Turbo; select Kitchen 20.

For users of the unreleased compiler-era Prompt Maker: `validation_report` now
reports authoring/review status, **not schema validation** (`valid: null`,
`validation: not_performed`). `visual_inventory` keeps its socket for compatibility
but does not claim extracted facts. See [Prompt Maker](../llm/h3-prompt-maker.md)
before relying on those older receipts. Review is not a correctness guarantee.

Restart Comfy to load updated Python nodes/workflow definitions. Existing
downloaded models are reused; no new model is downloaded automatically. LMS
lifecycle operations require workflow ownership of the selected instance;
failed/cancelled authoring may leave it loaded. See [LMS lifecycle](../llm/lms-models.md).
