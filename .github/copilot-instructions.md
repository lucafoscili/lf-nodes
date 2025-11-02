# LF Nodes – Copilot Guide

## Big picture

- **Python nodes** live under `modules/nodes/<domain>` and follow single-image processing loops (even with batched inputs) to keep logic deterministic. Nodes wrap ComfyUI primitives while preserving CONDITIONING structure as `[tensor, dict]` pairs.
- **Workflow Runner** is a miniapp under `modules/workflow_runner/` providing web-based workflow execution with strict separation of concerns (controllers → services → models/adapters).
- **Frontend assets** in `web/src` hydrate LF Widgets (Stencil-based web components) and bundle through Vite into `web/deploy`, served by ComfyUI from `extensions/lf-nodes`.

## Python node patterns

- Each node file imports `CATEGORY` from its package `__init__.py` and uses `FUNCTION = "on_exec"`; use `docs/NODE_TEMPLATE.md` as the canonical skeleton.
- **Always normalize inputs first**: Use helpers like `normalize_input_image`, `normalize_list_to_value`, and `normalize_conditioning` from `modules/utils/helpers/logic/` before processing. Never treat CONDITIONING like scalars.
- **Return both batch and list**: Use `normalize_output_image` to return `(batch[0], image_list)` with `RETURN_TYPES = ("IMAGE", "IMAGE")` and `OUTPUT_IS_LIST = (False, True)`.
- **Emit UI feedback**: Use `PromptServer.instance.send_sync(f"{EVENT_PREFIX}...", payload)` for real-time updates; `modules/utils/constants.py` defines `EVENT_PREFIX`, `CATEGORY_PREFIX`, and shared enums.

## Workflow Runner architecture

- **Strict SoC**: Controllers handle HTTP (validation/response), services contain business logic, models define schemas, adapters abstract external systems. No business logic in controllers.
- **Lazy loading**: Heavy dependencies (Torch/CUDA) are imported only when needed to avoid initialization at package import time. Controllers use `importlib` for deferred service imports.
- **Autoregistration**: Routes register themselves via decorators; `routes.py` imports controllers to trigger registration. No manual route mapping needed.
- **Key components**: `run_service.py` orchestrates execution, `executor.py` handles core logic, `job_store.py` manages in-memory job status, `auth_service.py` handles OAuth sessions.
- **Data flow**: HTTP request → controller validation → job creation → service orchestration → WebSocket progress → result storage → HTTP response.

## Shared helpers & data flow

- **Editing context**: Interactive workflows (inpainting) persist state via `modules/utils/helpers/editing/context.py` and dataset JSON files in `temp/`. Use `register_editing_context()` and `get_editing_context()` for cross-node communication.
- **Normalization patterns**: `normalize_input_image` converts batches to `[1, H, W, C]` tensors, `normalize_output_image` groups by resolution, `normalize_conditioning` preserves CONDITIONING as list-of-pairs.
- **Conversions**: Reuse `modules/utils/helpers/conversion.py` for PIL ↔ torch, base64 encoding; filesystem helpers in `comfy.py`/`api.py` for temp outputs and public URLs.
- **Filter processors**: `modules/utils/filters/processors.py` is the central registry for image processing handlers invoked by REST API endpoints.

## Frontend integration

- `web/src/index.ts` boots the LF framework, creates `LFManager` singleton, then calls `lfManager.initialize()` to patch ComfyUI hooks via `web/src/managers/manager.ts`.
- **Event naming**: Backend events must match lowercase, hyphenated names from `LFManager.getEventName`; `NODE_WIDGET_MAP` in `web/src/helpers/manager.ts` binds nodes to custom widgets.
- **Widget development**: Add/tweak under `web/src/widgets/`; they wrap `@lf-widgets/*` components so stay within exposed APIs. Use `createDOMWidget`, `refreshChart` from `web/src/utils/common.ts`.

## API routes & REST patterns

- Routes register on `PromptServer.instance.routes` with `POST /lf-nodes/...` prefix; `modules/api/image.py` exposes image processing endpoints.
- Filter handlers in `processors.py` are invoked by API endpoints; use `resolve_filepath` + `get_resource_url` to persist artifacts for frontend consumption.
- Dataset protocol drives interactive flows: nodes write JSON to `temp/`, UI reads for mask/image references, updates status back to nodes.

## Build & tooling

- **Yarn 4 (PnP)**: Run `yarn install` once, then `yarn build` (cleans → SCSS → TypeScript → widgets → Vite → submit) for frontend changes.
- **Widget updates**: `build:lfw` copies latest `@lf-widgets/*` components; re-run after dependency bumps.
- **Python deps**: Mirror `pyproject.toml`/`requirements.txt`; install into ComfyUI environment before launch.
- **Workflow Runner dev**: Use `WORKFLOW_RUNNER_DEBUG=1` for logging, `frontend_proxy.py` for development, WebSocket debugging for real-time features.

## Testing & performance

- **Python nodes**: Comprehensive CI/CD exercises all nodes; no formal unit tests needed but prefer small reproducible harnesses for utilities.
- **Workflow Runner**: Unit tests for services, integration for APIs, mocks for ComfyUI/OAuth. Background execution prevents blocking; lazy loading reduces startup time.
- **Frontend**: Unit/component tests via `yarn test`; integration tests for API calls.

## Adding/updating nodes

- Start from `docs/NODE_TEMPLATE.md`, set `OUTPUT_IS_LIST`/`RETURN_TYPES` for batch+list outputs, register in `NODE_CLASS_MAPPINGS`.
- For interactive nodes: Map in `NODE_WIDGET_MAP`, emit datasets via `send_sync`, clear editing contexts to avoid stale state.
- Persist artifacts with `resolve_filepath` + `get_resource_url` for previews; use `TempFileCache` for cleanup.

## Key references

- `docs/ARCHITECTURE.md`: End-to-end overview, normalization patterns, editing context, UI integration
- `docs/WORKFLOW_RUNNER.md`: Miniapp architecture, SoC principles, lazy loading, data flows
- `docs/NODE_TEMPLATE.md`: Implementation skeleton and conventions
- `modules/utils/helpers/logic/normalize_conditioning.py`: CONDITIONING structure guard
- `web/src/utils/common.ts`: ComfyUI hook flags, widget utilities (`createDOMWidget`, `refreshChart`)
