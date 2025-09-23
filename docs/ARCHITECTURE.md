# LF Nodes Architecture

This document explains how the lf-nodes suite is structured and how its parts interact across Python (ComfyUI custom nodes) and the companion UI (lf-widgets).

## TL;DR

- Nodes process images one-at-a-time even when inputs are batched. Normalizers convert inputs to a consistent shape.
- Shared helpers live under `modules/utils/helpers/*` and implement normalization, device logic, editing context, and misc utilities.
- Web UI integrates via prompt server events and a small dataset protocol to drive interactive flows like inpainting.
- Conditioning handling preserves ComfyUI's CONDITIONING structure (list of `[tensor, dict]` pairs) via `normalize_conditioning`.

---

## Repository layout (Python side)

```text
custom_nodes/lf-nodes/
  modules/
    nodes/                  # Node implementations grouped by domain
      image/                # Image transformations & interactive tools
      filters/              # Pure image filters
      regions/              # Region detection/masking
      selector/             # Selector nodes (models, sampler, scheduler, etc.)
      seeds/                # Seed generators
      logic/                # Logic/composition nodes
      ...
    utils/
      constants.py          # Shared constants (enums, ranges, names)
      filters/              # Reusable filter kernels/ops
      helpers/
        api/                # API helpers (URLs, resources)
        comfy/              # Comfy-specific helpers
        conversion/         # PIL <-> Tensor, b64, etc.
        detection/          # Detection-related helpers
        editing/            # Editing context registry (inpainting flows, etc.)
        logic/              # Normalizers and generic helpers
          normalize_conditioning.py  # CONDITIONING structure normalizer
        metadata/           # Metadata helpers
        prompt/             # Prompt helpers
        torch/              # Torch-specific helpers
        ui/                 # UI helpers
```

## Key design principles

1. Single-image processing loop
   - Even if inputs arrive as batches, nodes typically split into individual images and process them sequentially.
   - This keeps node implementations simple and deterministic, especially when chaining interactive steps.

2. Normalization first, always
   - Inputs are normalized using helpers in `modules/utils/helpers/logic`:
     - `normalize_input_image` converts 3D/4D tensors or lists into `[1, H, W, C]` tensors list.
     - `normalize_output_image` reconsolidates outputs into batches grouped by resolution.
     - `normalize_list_to_value` extracts the first value from list-ish inputs when appropriate (NOT for CONDITIONING).
     - `normalize_conditioning` preserves CONDITIONING as a list of `[tensor, dict]` pairs.

3. Keep core untouched
   - lf-nodes should operate without modifying ComfyUI core.
   - Any robustness (e.g., normalizing CONDITIONING) is handled inside lf-nodes helpers.

4. UI-powered workflows
   - Interactive flows (e.g., inpainting) use an editing context (see below) and prompt-server events.

## Output normalization and return shapes

- Standard pattern: return both a batch and a list for image outputs to give downstream nodes flexibility.
- Typical signature for a simple image transform:
  - `RETURN_TYPES = ("IMAGE", "IMAGE")`
  - `RETURN_NAMES = ("image", "image_list")`
  - `OUTPUT_IS_LIST = (False, True)`
  - Return `(batch_list[0], image_list)` after `batch_list, image_list = normalize_output_image(tensors)`.
- Mixed outputs (e.g., file names and counts) can be appended:
  - `RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "INT")`
  - `OUTPUT_IS_LIST = (False, True, True, False)`

## Data flow: inpainting as an example

1. `LF_ImagesEditingBreakpoint` captures the current image(s) and registers an editing context:
   - Stores `model`, `clip`, `vae`, `sampler`, `scheduler`, `cfg`, `seed`, prompts, and optional CONDITIONING.
   - Emits a prompt-server event for the UI to open the inpaint editor and writes a dataset JSON in `temp`.

2. The web UI edits mask/regions and writes completion status and assets into the dataset file.

3. The filter entrypoint (`modules/utils/filters/inpaint.py`):
   - Reads the context via `get_editing_context`.
   - Normalizes/validates inputs (image, mask, prompts, params).
   - If `use_conditioning` is true, preprends stored CONDITIONING via `ConditioningCombine`.
   - Invokes `InpaintModelConditioning.encode` to inject `concat_latent_image` and `concat_mask`.
   - Samples without preview (or via a sampler node) and blends the decoded result with the original image using the mask.

4. Results are returned to the UI and/or pipeline.

## Conditioning handling

- ComfyUI CONDITIONING is a list of pairs: `[embedding_tensor, metadata_dict]`.
- lf-nodes preserve this structure with `normalize_conditioning(cond)`:
  - If already a list-of-pairs → return as-is.
  - If a single pair `[tensor, dict]` → wrap into `[ [tensor, dict] ]`.
  - Otherwise → return `None`.
- Do NOT use `normalize_list_to_value` on CONDITIONING; it is for scalar-like values.

## Editing context

- The editing context is an in-memory registry keyed by a dataset path (`temp/<id>_edit_dataset.json`).
- Implemented in `helpers/editing/context.py` with:
  - `register_editing_context(identifier, **context)`
  - `get_editing_context(identifier)`
  - `clear_editing_context(identifier)`
- Used to pass model components, params, prompts, and optional CONDITIONING between nodes and UI flows.

## UI integration (lf-widgets)

- The UI triggers via `PromptServer.instance.send_sync(<event>, payload)`.
- The editor writes its status (pending → completed) and assets to the dataset JSON.
- Nodes read the dataset for mask and image references.

### Registering a node + widget in the UI

- Add a new entry in the UI's `NODE_WIDGET_MAP` and the related enum to bind an existing LF Widget to a node.
- Widgets are async: they update whenever the backend sends a `send_sync` event, even while the node is still executing.

Example (live logging from the backend):

```python
from server import PromptServer

PromptServer.instance.send_sync(
  f"{EVENT_PREFIX}loadclipsegmodel",
  {"node": node_id, "value": "## Load CLIPSeg Model\n\n- ⏳ Downloading..."},
)
```

See `LF_LoadCLIPSegModel` for a concrete pattern of streaming progress messages.

## Conventions & best practices

- Always normalize inputs at the start of `on_exec`.
- Maintain `[1, H, W, C]` tensors when working per-image.
- Group outputs by resolution with `normalize_output_image` and return both batch and list when appropriate.
- For CONDITIONING, always use `normalize_conditioning`.
- Keep device/dtype conversions local and explicit.
- Avoid assumptions about batch sizes—stick to the single-image processing loop.

## Testing & build

- Python nodes: a comprehensive CICD workflow exercises effectively every node in the suite to catch hiccups. No formal unit test harness is required at this time.
- Web (lf-widgets): `yarn install`, `yarn build`, `yarn test` (see root tasks).
- Prefer small, reproducible harnesses for new helpers/utilities.

## Dataset typing & versioning

- Editing datasets sent to the frontend are well-typed in the LF Widgets (Stencil) repo; that typing acts as the source of truth. We don’t maintain a separate JSON schema here.
- Protocol versioning is informal. The LF Widgets structure is stable and unlikely to change; if it does, we update both ends in lockstep.

## Debugging and inspection

- A frontend-only Control Panel provides debugging tools. Use it to observe events, state, and live updates while nodes run.

## Extension points

- New image filters: place under `modules/nodes/filters` and reuse `normalize_input_image`/`normalize_output_image`.
- New interactive flows: use the editing context and prompt-server event contract.
- Integrations: add lightweight helpers under `modules/utils/helpers`.

## Future ideas

- Shared debug logging utilities toggled via env/setting.
- Schema validation for dataset JSON to catch mismatches early.
- Golden workflows for regression testing complex interactions (inpainting, region-aware edits).
