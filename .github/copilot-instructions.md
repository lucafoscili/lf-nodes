# LF Nodes – Copilot Guide

## Big picture

- Python node logic lives under `modules/nodes/<domain>` and follows the architecture documented in `docs/ARCHITECTURE.md`; nodes wrap ComfyUI primitives while keeping batch handling deterministic via single-image loops.
- Frontend assets in `web/src` hydrate LF Widgets (Stencil-based web components) and bundle through Vite into `web/deploy`, which ComfyUI serves from `extensions/lf-nodes`.

## Python node patterns

- Each node file imports `CATEGORY` from its package `__init__.py` and uses `FUNCTION = "on_exec"`; use `docs/NODE_TEMPLATE.md` as the canonical skeleton.
- Normalize every input via helpers like `normalize_input_image`, `normalize_list_to_value`, and friends in `modules/utils/helpers/logic/` before processing, and return both batch + list using `normalize_output_image` (see `modules/nodes/image/blur_images.py`).
- Emit UI feedback with `PromptServer.instance.send_sync(f"{EVENT_PREFIX}...", payload)`; `modules/utils/constants.py` defines `EVENT_PREFIX`, `CATEGORY_PREFIX`, `Input` enums, and shared naming helpers.

## Shared helpers & data flow

- Editing workflows persist context through `modules/utils/helpers/editing/context.py` and dataset JSON files in `temp/`; inpainting filters read them back via `modules/utils/filters/inpaint.py`.
- Reuse conversions in `modules/utils/helpers/conversion.py` (PIL ↔ torch, base64) and filesystem helpers in `modules/utils/helpers/comfy.py` / `api.py` for temp output + public URLs.
- Image REST APIs (`modules/api/image.py`) expose `POST /lf-nodes/...` routes registered on `PromptServer.instance.routes`; `modules/utils/filters/processors.py` is the central registry for filter handlers invoked by those endpoints.

## Frontend integration

- `web/src/index.ts` boots the LF framework, creates a singleton `LFManager`, then calls `lfManager.initialize()` to patch ComfyUI hooks via `web/src/managers/manager.ts`.
- Back-end events must match the lowercase, hyphenated names produced by `LFManager.getEventName`; the `NODE_WIDGET_MAP` in `web/src/helpers/manager.ts` binds each node (e.g., `LF_BlurImages`) to the custom widget(s) rendered in the UI.
- Add or tweak widgets under `web/src/widgets/`; they wrap `@lf-widgets/*` components so stay within the APIs exposed by those packages.

## Build & tooling

- This repo uses Yarn 4 (PnP). Run `yarn install` once, then `yarn build` (alias for `clean → build:scss → build:ts → build:lfw → build:vite`) whenever frontend changes should refresh `web/deploy`.
- `build:lfw` copies the latest web components from `lf-widgets`; re-run it if you bump any `@lf-widgets/*` dependency.
- Python dependencies mirror `pyproject.toml` / `requirements.txt`; install them into the ComfyUI environment (`pip install -r requirements.txt`) before launching ComfyUI.

## Adding or updating nodes

- Start from the template, set `OUTPUT_IS_LIST`/`RETURN_TYPES` to expose both aggregated and per-item outputs, and register the class in `NODE_CLASS_MAPPINGS` at the bottom of the file.
- Persist artifacts with `resolve_filepath` + `get_resource_url` so the frontend can fetch previews, and clear editing contexts once finished to avoid stale state.
- If the node needs bespoke UI, map it in `NODE_WIDGET_MAP` and ensure the widget knows how to consume the dataset emitted via `send_sync` (inspect existing patterns like the masonry dataset built in `LF_BlurImages`).

## Key references

- `docs/ARCHITECTURE.md` for the end-to-end overview; `docs/NODE_TEMPLATE.md` for implementation conventions; `docs/IMAGE_EDITOR.md` for the image editor widget.
- `modules/utils/helpers/logic/normalize_conditioning.py` guards CONDITIONING payloads; never treat them like scalars.
- `web/src/utils/common.ts` centralizes ComfyUI hook flags and widget utilities; reuse its helpers (`createDOMWidget`, `refreshChart`, JSON tooling) instead of reinventing them.
