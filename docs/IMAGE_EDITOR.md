# LF Image Editor Architecture

This document walks through the moving parts behind the interactive image editor that is exposed by the `LF_ImagesEditingBreakpoint` node. It maps the Python helpers, HTTP endpoints, on-disk datasets, and frontend widgets so contributors can reason about the end-to-end workflow with confidence.

---

## TL;DR

- **`LF_ImagesEditingBreakpoint`** snapshots the incoming batch, caches all diffusion context (model, clip, vae, prompts, conditioning, sampler options), writes a dataset JSON to `ComfyUI/temp`, and notifies the UI through the prompt server.
- **The UI** reads and mutates that dataset file, renders masonry previews, and posts filter requests back to the backend. Manual-apply filters (including inpaint) hold changes until the user confirms.
- **`POST /lf-nodes/process-image`** resolves the selected asset, routes the request through `process_filter`, saves outputs/masks with deterministic names from the UI, and returns payload metadata to update the history view.
- **`apply_inpaint_filter`** adapts the masked ROI to SDXL-friendly presets (multiples of 64px, aspect ratio <= 3:1), blends prompt vs. stored conditioning via the `conditioning_mix` slider, runs denoising without preview, re-injects original background pixels to avoid seams, and optionally applies a light unsharp mask.

---

## Component map

| Layer | File(s) | Responsibility |
| --- | --- | --- |
| Custom node | `modules/nodes/image/images_editing_breakpoint.py` | Starts an editing session, materialises the dataset JSON, fires prompt-server events, and returns edited tensors to the graph. |
| Context registry | `modules/utils/helpers/editing/context.py` | In-memory store for per-session state (model, sampler, prompts, conditioning tensors). |
| Dataset helpers | `modules/utils/helpers/editing/dataset.py` | Normalises dataset files, applies selection updates, and keeps loader nodes in sync with the UI. |
| HTTP API | `modules/api/image.py` | `get-image` lists assets; `process-image` validates requests, dispatches filters, and persists results. |
| Filter dispatcher | `modules/utils/filters/processors.py` | Maps `type` values to concrete filter functions such as `apply_inpaint_filter`. |
| Inpaint core | `modules/utils/filters/inpaint.py` | Prepares ROI/masks, performs sampling, saves mask/region previews, and returns the blended image. |
| File helpers | `modules/utils/helpers/comfy/resolve_filepath.py`, `modules/utils/helpers/api/get_resource_url.py` | Resolve safe output paths inside `temp`/`output`/`input` and build cache-busted URLs for the UI. |
| Frontend widgets | `web/src/widgets/imageEditor.ts` + fixtures/helpers | React/StenciI widget that renders the editor, manages manual-apply state, and coordinates API calls. |

---

## Request flow

### 1. Node execution

1. `LF_ImagesEditingBreakpoint.on_exec` receives the batch, optional model components, prompts, conditioning, and UI widget state.
2. Each image is normalised and saved to `temp/edit_breakpoint_<counter>.png` via `resolve_filepath`.
3. A dataset JSON is written to `temp/<node_id>_<uuid>_edit_dataset.json` containing:
   - `columns`: path + status markers (`pending` -> `completed`).
   - `nodes`: masonry entries pointing to `/view?filename=...`.
   - `defaults`: inpaint UI defaults seeded from node inputs.
   - `context_id`: absolute dataset path, used as the lookup key.
4. `register_editing_context` stores every reusable input (model, clip, vae, sampler, scheduler, cfg, seed, prompts, conditioning).
5. A prompt-server event (`lf-imageseditingbreakpoint`) opens the editor UI.
6. Execution blocks until the UI writes `status = completed` to the dataset.
7. The node collects edited outputs from disk, converts them back to tensors, and returns them alongside original inputs for downstream comparison.

### 2. UI lifecycle

1. The widget loads the dataset JSON, renders a masonry grid, and pre-fills settings with `defaults`.
2. Canvas interactions capture mask strokes into base64 payloads.
3. When the user requests an inpaint, the widget submits a multipart form to `/lf-nodes/process-image` containing the base image URL, filter `type`, and `settings`.
4. For manual-apply filters the widget defers the API call until the user presses **Apply** to avoid accidental requests.
5. Responses update the dataset (`nodes`, history snapshots, status) so the node can resume once the user is satisfied.

### 3. `/process-image`

1. Resolves the URL back to a real file with `resolve_url`.
2. Loads the tensor, builds a settings dict, and looks up the editing context with `context_id`.
3. Dispatches to the registered filter function (e.g., `apply_inpaint_filter`).
4. Saves outputs/masks via `resolve_filepath`, builds response metadata, and returns JSON so the UI can refresh history.

---

## Inpaint pipeline overview

| Stage | Key calls | Notes |
| --- | --- | --- |
| Context lookup | `get_editing_context` | Validates the session and retrieves stored model components + prompts + conditioning. |
| Mask decoding | `base64_to_tensor`, thresholding | Converts the brush strokes into a binary mask, resized to the base image resolution. |
| ROI prep | `_prepare_inpaint_region` | Auto-crops around the mask (padding + alignment), optionally upscales to an SDXL preset, dilates/feathers edges, and caches the original ROI to prevent seam artefacts. |
| Sampling | `perform_inpaint` | Encodes prompts, mixes conditioning via `ConditioningAverage`, encodes latents through `InpaintModelConditioning`, and samples without preview. |
| Downscale + blending | `_finalize_inpaint_output` | Downscales with bicubic + antialias, optionally applies unsharp mask, restores original pixels outside the mask, pastes results, clamps to `[0, 1]`, and moves to CPU. |
| Previews | `_save_tensor_preview` | Optional debug saves for mask, region pre/post downscale, and stitched output. |

Additional behaviour:

- **Prompts & conditioning**: When `use_conditioning` is enabled, the UI exposes a `conditioning_mix` slider (`-1` -> stored conditioning only, `0` -> balanced, `1` -> prompt only). The backend logs the resolved mix factor for visibility.
- **Adaptive presets**: `_select_upsample_plan` chooses the largest whitelist preset (multiples of 64) that fits the ROI area and respects the <= 3:1 aspect cap. If the ROI already exceeds the chosen size, no upscale occurs. Console logs print the preset that was selected.
- **Seamless background**: Original ROI pixels are re-blended after sampling so unmasked areas remain untouched, eliminating hard patch edges.
- **Manual apply**: Inpaint defaults to manual-apply mode so multiple slider tweaks can be staged before triggering a backend call.

---

## Dataset contract

Minimal dataset structure produced by the breakpoint node:

```json
{
  "columns": [
    { "id": "path", "title": "C:/ComfyUI/temp/6123_edit_dataset.json" },
    { "id": "status", "title": "pending" }
  ],
  "nodes": [
    {
      "id": "1",
      "cells": {
        "lfImage": {
          "shape": "image",
          "htmlProps": { "id": "edit_breakpoint_1.png", "title": "edit_breakpoint_1.png" },
          "lfValue": "/view?filename=edit_breakpoint_1.png&type=temp&subfolder=&nonce=...",
          "value": "/view?filename=edit_breakpoint_1.png&type=temp&subfolder=&nonce=..."
        }
      }
    }
  ],
  "defaults": {
    "inpaint": {
      "cfg": 7,
      "seed": 42,
      "positive_prompt": "",
      "negative_prompt": ""
    }
  },
  "context_id": "C:/ComfyUI/temp/6123_edit_dataset.json"
}
```

The UI mutates `columns[1].title` to `completed` when the workflow should resume, and appends new nodes for each history snapshot.

---

## Key settings recognised by `/process-image`

| Setting | Type | Default | Purpose |
| --- | --- | --- | --- |
| `resource_type` / `output_type` | string | `"temp"` | Which ComfyUI directory (`temp`, `output`, `input`, ...) should receive outputs. |
| `subfolder` | string | `""` | Optional subdirectory under the selected resource; sanitised to avoid `..` escapes. |
| `filename` | string | auto | Exact file name (extension optional) if deterministic naming is required. |
| `filename_prefix` | string | filter type | Prefix passed to `resolve_filepath` when auto-generating numbered files. |
| `settings` | stringified JSON | `{}` | Filter-specific payload forwarded to the dispatcher. |

Inpaint-specific settings:

- `conditioning_mix` (float, default `0`): blend factor between stored conditioning (`-1`) and the live prompt (`1`).
- `upsample_target` (int, default `1024`, commonly set to `2048`): desired longer edge for the ROI. The backend snaps to a preset that fits under `target^2`.
- `apply_unsharp_mask` (bool, default `true`): toggles the conservative sharpening pass applied after downscaling the generated patch.

The filter response can include extra metadata (mask URL, ROI coordinates, upsample info, debug previews) that the UI surfaces in the history view or console.

---

## Extending the image editor

1. **Add a filter**
   - Implement `apply_<filter>_filter(image: torch.Tensor, settings: dict)` under `modules/utils/filters`.
   - Register it in `FILTER_PROCESSORS` within `modules/utils/filters/processors.py`.
   - Return `(result_tensor, payload_dict)` so the UI can display metadata.
   - Persist any required context ahead of time using `register_editing_context`.
2. **Expose controls**
   - Add defaults in `web/src/fixtures/imageEditor/settings`.
   - Update the type definitions in `web/src/types/widgets/imageEditor.ts`.
   - Wire events to the API in `web/src/helpers/imageEditor`.
3. **Custom outputs**
   - Use `filename`, `filename_prefix`, and `subfolder` when deterministic history structures are needed.
   - Emit additional payload fields for previews, stats, or ROI metadata.
4. **Testing**
   - Exercise the node locally, inspect the dataset JSON, and ensure outputs land in the expected folders.
   - Use `curl`/Postman against `/lf-nodes/process-image` with a captured payload to smoke-test the API.

---

## Troubleshooting

- **History entries overwrite each other**: Ensure the UI provides unique `filename` values or allow `resolve_filepath` to auto-increment.
- **Empty masks**: Submitting without strokes raises `ValueError("Inpaint mask strokes are empty.")`; the UI prevents the call but the backend guards it.
- **Missing context**: If `get_editing_context` returns `None`, confirm the dataset `context_id` still points to the active JSON and that the node has not cleaned up the session.
- **Path issues**: `subfolder` is normalised; any attempt to escape (`..`) results in a HTTP 400.
- **Unexpected seams**: Adaptive ROI blending now reuses original pixels, but extremely sharp masks may still need a small feather radius (1-2 px).

---

## Reference cheat sheet

- Start session: `LF_ImagesEditingBreakpoint.on_exec`
- Finish session: dataset `columns[id="status"].title = "completed"`
- API base: `/lf-nodes`
  - `POST /get-image` - list available inputs
  - `POST /process-image` - run filter + persist output
- Filter registry: `modules/utils/filters/processors.py`
- Editing context helpers: `modules/utils/helpers/editing/context.py`
- Path helpers: `modules/utils/helpers/comfy/resolve_filepath.py`, `modules/utils/helpers/api/get_resource_url.py`
- Inpaint implementation: `modules/utils/filters/inpaint.py`

With these pieces connected, the image editor delivers a non-linear editing history that round-trips cleanly between the ComfyUI backend and the LF frontend. Follow the conventions above to extend the tooling or add new filters safely.
