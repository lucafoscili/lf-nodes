# LF Image Editor Architecture

This guide explains how the interactive image editor (the inpainting workflow surfaced by `LF_ImagesEditingBreakpoint`) is wired end-to-end. It maps the moving pieces across Python helpers, custom nodes, HTTP APIs, on-disk datasets, and the frontend widgets so that future contributors can navigate the system confidently.

---

## TL;DR

- **`LF_ImagesEditingBreakpoint`** snapshots the current batch, registers an editing context, and notifies the UI via the prompt server.
- The UI writes its state into a **dataset JSON** in `ComfyUI/temp`, then sends filter requests back to the backend.
- **`/lf-nodes/process-image`** loads the requested asset, dispatches it through `process_filter`, and saves results with deterministic names provided by the UI.
- Inpainting is implemented by **`apply_inpaint_filter`**, which reuses the stored context (model, clip, vae, prompts, conditioning) to run denoising and mask blending.
- Mask previews and filtered outputs are stored with helper utilities (`resolve_filepath`, `get_resource_url`) so the UI can refresh non-linear history snapshots.

---

## Component map

| Layer | File(s) | Responsibility |
| --- | --- | --- |
| Custom node | `modules/nodes/image/images_editing_breakpoint.py` | Starts an editing session, writes dataset JSON, emits prompt-server events, returns edited images to the graph. |
| Context registry | `modules/utils/helpers/editing/context.py` | In-memory store for per-session state (model, sampler, prompts, conditioning). |
| HTTP API | `modules/api/image.py` | `get-image` lists existing assets, `process-image` runs filters + persists outputs/masks. |
| Filter dispatcher | `modules/utils/filters/processors.py` | Maps `type` strings to concrete filter implementations (`apply_inpaint_filter`, etc.). |
| Inpaint core | `modules/utils/filters/inpaint.py` | Crops & upsamples masked regions, runs sampling without preview, blends decoded pixels, saves mask previews. |
| File helpers | `modules/utils/helpers/comfy/resolve_filepath.py`, `modules/utils/helpers/api/get_resource_url.py` | Resolve sanitized output paths under `temp`/`output`/`input` and emit `view` URLs with cache-busting nonces. |
| UI integration | `lf-widgets` bundle (outside this repo) | React-based widget listens for prompt-server events, edits masks, POSTs to the API, and updates dataset JSON. |

---

## Request flow

1. **Node executes (`on_exec`)**
   1. Captures inputs (`image`, optional `model/clip/vae`, sampler params, prompts).
   2. Normalizes images via `normalize_input_image` and saves each to `temp/edit_breakpoint_{counter}.png` using `resolve_filepath`.
   3. Writes a dataset JSON (`temp/<node_id>_edit_dataset.json`) with:
      - `columns`: `path` (dataset file path) and `status` (`pending` → `completed`).
      - `nodes`: masonry tiles with `/view?filename=…` URLs for the UI.
      - `defaults`: prefilled inpaint parameters (cfg, seed, prompts).
      - `context_id`: absolute dataset path – used as the editing context key.
   4. Registers context data via `register_editing_context(context_id, …)`.
   5. Emits a prompt-server event (`lf-imageseditingbreakpoint`) so the frontend opens the editor.
   6. Blocks until the dataset’s `status` column flips to `completed` (the UI mutation).
   7. Reads final `nodes` entries, resolves image paths with `get_comfy_dir(type)` + `subfolder`, converts to tensors, and returns them to the ComfyUI graph.

2. **UI lifecycle (high-level)**
   1. Widget loads the dataset file and renders the image gallery.
   2. When the user paints a mask + submits, the widget sends a multipart form to `/lf-nodes/process-image` containing:
      - `url`: The `view` URL of the base image.
      - `type`: Filter name (`"inpaint"`, …) – matches keys in `FILTER_PROCESSORS`.
      - `settings`: JSON string with filter-specific payload (mask, prompts, cfg, etc.).
      - Optional `filename`, `filename_prefix`, `subfolder`, `resource_type` to control output placement.
   3. The widget updates the dataset JSON with a new node entry and eventually sets the `status` column to `completed` to unblock the backend node.

3. **`process-image` endpoint**
   1. Parses the request payload, resolving the source image path via `resolve_url`.
   2. Loads the tensor from disk (`load_image_tensor`) and passes it to `process_filter(filter_type, tensor, settings)`.
   3. Saves the processed tensor to disk:
      - Honors optional overrides in `settings`:
        - `resource_type` / `output_type`: target Comfy directory (`temp`, `output`, `input`, …).
        - `subfolder`: appended directory (sanitized to prevent directory traversal).
        - `filename_prefix`: Base prefix when auto-generating names via `resolve_filepath`.
        - `filename`: Exact filename (extension optional – defaults to `.png`).
      - Detects desired image format from the extension (`.png`, `.jpg`, `.webp`, …) and saves accordingly.
   4. Returns a JSON payload with:

      ```json
      {
        "status": "success",
        "data": "/view?filename=…",
        "type": "temp",
        "subfolder": "…",
        "filename": "…",
        …extra filter payload…
      }
      ```

   5. The frontend appends the new `/view` URL to the dataset history, giving each edit its own immutable snapshot.

4. **`get-image` endpoint**
   - Enumerates files under `ComfyUI/input[/<directory>]`, emits masonry nodes with `/view` URLs so the UI can offer quick picks.

---

## Inpainting internals (`apply_inpaint_filter`)

| Stage | Key calls | Notes |
| --- | --- | --- |
| Context lookup | `get_editing_context(context_id)` | Validates that the editing session exists and fetches model/clip/vae references. |
| Mask decoding | `base64_to_tensor`, thresholding | Converts the brush canvas to a binary mask, resizes to match the base image, ensures non-empty strokes. |
| ROI prep | `_prepare_inpaint_region` | Automatically crops around the mask with configurable padding, alignment to VAE stride, optional dilation/feathering, and optional upsampling of the working area. |
| Sampling | `perform_inpaint` | Runs CLIP encoding, optional conditioning combine, `InpaintModelConditioning.encode`, and sampling (`sample_without_preview` by default). |
| Blending | `_finalize_inpaint_output` | Pastes processed region back into the full image, clamps to `[0, 1]`, moves to CPU for downstream conversion. |
| Mask preview | `resolve_filepath(prefix="inpaint_mask")`, `tensor_to_pil` | Saves a visual mask preview alongside the edited image (mirrors the same folder/filename overrides used by the main API). |

Additional behaviors:

- **Prompts & conditioning**: The editing context stores prompts and optional conditioning tensors. When `settings["use_conditioning"]` is truthy, the stored conditioning is merged via `ConditioningCombine` prior to sampling.
- **Sampler/scheduler/cfg/seed overrides**: Each inpaint call can override defaults; absent values fall back to the context (or sensible defaults like `dpmpp_2m` / `karras`).
- **Upsampling ROI**: If `settings["upsample"]` / `"upsample_target"` is set, the masked crop is upsampled prior to sampling and downsampled back, improving small-detail edits.
- **Device placement**: All sampling work runs on the VAE/model device; outputs are returned on CPU for safe serialization.

---

## Dataset contract

Minimal dataset structure emitted by `LF_ImagesEditingBreakpoint`:

```json
{
   "columns": [
      { "id": "path", "title": "C:\\…\\temp\\608_edit_dataset.json" },
      { "id": "status", "title": "pending" }
   ],
   "nodes": [
      {
         "cells": {
            "lfImage": {
               "htmlProps": {"id": "edit_breakpoint_38.PNG", "title": "edit_breakpoint_38.PNG"},
               "shape": "image",
               "lfValue": "/view?filename=edit_breakpoint_38.PNG&type=temp&subfolder=&nonce=…",
               "value": "/view?filename=edit_breakpoint_38.PNG&type=temp&subfolder=&nonce=…"
            }
         },
         "id": "1",
         "value": "1"
      }
   ],
   "context_id": "C:\\…\\temp\\608_edit_dataset.json",
   "node_id": "608",
   "defaults": {
      "inpaint": { "cfg": 7 }
   }
}
```

The frontend augments this structure by:

- Pushing additional `nodes` entries as edits are created.
- Setting the `status` column title to `"completed"` once the history is finalized.
- Optionally adding per-node metadata (e.g., brush settings, timestamps) for UI purposes.

Backend consumers should rely on `context_id` to reopen the editing context and on `nodes[*].cells.lfImage.lfValue` for deterministic asset loading.

---

## Key settings recognized by `/process-image`

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `resource_type` / `output_type` | string | `"temp"` | Chooses the ComfyUI directory: `temp`, `output`, `input`, or any folder registered via `get_comfy_dir`. |
| `subfolder` | string | `""` | Creates or reuses a subdirectory under the chosen resource type. Sanitized to prevent `..` escapes. |
| `filename` | string | auto | If provided, saves the result with this exact name (extension optional – `.png` implied). |
| `filename_prefix` | string | filter type | Prefix used by `resolve_filepath` when auto-generating numbered files. Supports slashes to embed within subfolders. |
| `settings` (filter-specific) | stringified JSON | `{}` | Passed directly to the chosen filter (`apply_inpaint_filter`, etc.). |

Filters can also append custom payload back to the response. For example, `apply_inpaint_filter` adds a `mask` URL and ROI metadata.

---

## Extending the image editor

1. **Add a new filter**
   - Implement `apply_<name>_filter(image: torch.Tensor, settings: dict)` under `modules/utils/filters`.
   - Register it in `FILTER_PROCESSORS` within `modules/utils/filters/processors.py`.
   - Ensure the filter returns a `(torch.Tensor, dict)` tuple (image tensor + extra payload).
   - Decide whether it needs editing context data; if so, mirror the inpaint pattern by storing prerequisites in `register_editing_context`.

2. **Expose UI controls**
   - Extend the dataset defaults (`defaults[name]`) to prefill widget inputs.
   - Update the lf-widgets counterpart (Stencil components) to render the new controls and post the appropriate `type` + `settings` payload.

3. **Custom outputs**
   - Use the `filename` / `subfolder` overrides when the UI needs deterministic file names (e.g., branching history).
   - Return additional keys in the payload so the front end can display metadata (preview masks, ROI info, sampler settings, etc.).

4. **Testing**
   - Trigger the node locally, inspect the dataset JSON, ensure snapshots land in the expected folder.
   - Validate `/process-image` manually with `curl` or a REST client using the same payload the widget emits.

---

## Troubleshooting

- **History entries overwrite each other** → Confirm the UI is sending unique `filename` values per edit or let `resolve_filepath` auto-increment; ensure the backend honors these (fixed in September 2025 to avoid collisions).
- **Mask errors** → An empty mask raises `ValueError("Inpaint mask strokes are empty.")`; the UI should prevent submitting blank masks.
- **Context missing** → If `get_editing_context` returns `None`, check that `context_id` matches the dataset path and that `register_editing_context` ran (the backend clears contexts in a `finally` block after the dataset flips to completed).
- **Permissions/path issues** → `subfolder` is sanitized via `os.path.normpath`; paths starting with `..` are rejected with a 400 response.
- **Format mismatches** → Output format is inferred from the filename; ensure extensions align with what Pillow can save (`PNG`, `JPEG`, `WEBP`, `BMP`, `GIF`).

---

## Reference cheat sheet

- Start session: `LF_ImagesEditingBreakpoint.on_exec`
- Finish session: dataset `status` → `"completed"`
- API base: `/lf-nodes`
  - `POST /get-image` → list available inputs.
  - `POST /process-image` → run filter + persist output.
- Filter registry: `modules/utils/filters/processors.py`
- Editing context helpers: `modules/utils/helpers/editing/context.py`
- Path helpers: `modules/utils/helpers/comfy/resolve_filepath.py`, `modules/utils/helpers/api/get_resource_url.py`
- Inpaint implementation: `modules/utils/filters/inpaint.py`

With these pieces connected, the image editor delivers a non-linear history of edits, cleanly round-tripping between ComfyUI’s backend and the LF frontend. Feel free to extend the workflow or add new filters by following the conventions outlined above.
