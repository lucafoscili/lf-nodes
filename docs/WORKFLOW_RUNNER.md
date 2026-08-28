# Workflow Runner Miniapp Architecture

## Overview

The Workflow Runner is a miniapp within LF Nodes that provides a web-based interface for executing ComfyUI workflows. It allows users to select, configure, and run workflows through a modern web UI, with real-time progress tracking and result visualization.

### MiniMax H3 workflows

The shipped `MiniMax H3` category contains nine focused local-weight cards:
Generate Video, Animate Image, First & Last Frame, Anchored Sprite Loop,
Reference Restage, Character Swap, Outfit Transfer, Sprite Motion, and the
experimental Scene Sheet workflow. They use current ComfyUI Core H3 nodes,
fixed 24 fps output, the `kitchen_quality` 20-step
`res_multistep`/`simple` profile, curated native canvases, and exact 5–15 second
frame presets with a trained minimum of 124 frames. FL2VA and REF2VA cards
remain bound to their respective model families; the transfer cards use
reference-guided prompts rather than masking or pixel replacement.

Anchored Sprite Loop keeps required FL2VA opening and ending frames and can
chain up to three optional images through Core's `MiniMaxH3AddGuide` node. Each
guide uses a caller-selected, zero-based interior frame index; configured guide
indices must be in range and distinct. All controls are validated before the
shared content-addressed upload staging path is entered. In addition to the
original 24 fps MP4, the card periodically selects exactly 24 ordered frames
from the decoded batch while excluding the final endpoint. Reusing the opening
image as the ending reference makes excluding that conditioned endpoint
appropriate for a visually closed cycle; H3 generation does not guarantee that
the decoded first and last frames are pixel-identical. With different endpoints,
the ending keyframe remains in the MP4 but not the sprite export. The card then
uses the installed `VNCCS_RMBG2` node in Alpha mode and passes the RGBA batch
through `LF_NormalizeSpriteBatch`. The normalizer measures one selected
reference frame, derives one uniform scale and one horizontal pivot, and applies
both to the entire batch. It varies only the vertical translation needed to
place every frame's lowest alpha pixel on the requested baseline. The default is
a 256 px square canvas, 224 px nominal reference-content height, reference frame
0, and 16 px bottom padding. Content that cannot fit the chosen canvas fails
instead of being silently cropped. The card saves every normalized RGBA frame
and a transparent, zero-gap, no-header 6x4 `LF_ImageGrid` atlas.

The sampling receipt records the exact indices and source/intended playback
rates. A separate normalization receipt records the shared transform,
post-filter alpha bounds, per-frame vertical translations, and clipping policy.
A Core alpha round-trip verifies that background removal produced RGBA before
any frame or atlas is saved; an RGB fallback fails the run instead of publishing
opaque sprites.

RMBG-2.0's four-file local package is an explicit Runner model prerequisite;
the card remains **Setup required** when it cannot be verified and never falls
through to the wrapper's automatic download. Alpha is inferred independently
per frame, and the first vertical slice does not stabilize that matte.
Normalization uses every alpha pixel above 1/255 as geometry: equipment,
effects, and shadows count, so the requested height is an alpha-content height
rather than a semantic body height. Fainter alpha is preserved but does not
steer the transform. Bicubic antialiasing can introduce a small measured edge
halo, which is why the requested height is nominal and the receipt reports the
rasterized bounds. Matte quality and depicted content can still vary and should
be checked in the saved frame sequence before the atlas is treated as
production-ready.

LF Nodes does not bundle or download MiniMax H3 weights. Catalogue readiness
checks the declared local files and node types before a card can run.

The generic `Compose Image Sheet` card arranges four uploads into a labeled 2×2
PNG using `LF_ImageList` and `LF_ImageGrid`. The list seam preserves every
source tensor at its original dimensions so the grid alone owns aspect-preserving
contain-fit and letterboxing. Its populated LfDataDataset and deterministic
layout receipt are also retained in Runner history. The Scene Sheet H3 card can
consume that composite as one experimental dense reference.

### TripoSplat workflows

The shipped `TripoSplat` category contains one focused card,
`Image to Gaussian Splat`. It reconstructs a clearly visible, isolated subject
from one uploaded image. The form exposes automatic background removal,
foreground-edge cleanup, Gaussian density, export format, and seed. Density is
bounded to 262k (Full), 131k (Balanced), 64k (Light), or 32k (Draft) Gaussians;
increasing that count above the native 262k result would not add model detail.
Edge cleanup can be Gentle (one-pixel erosion), Off, or Strong (two-pixel
erosion). Export can be compact base-color SPZ, full-spherical-harmonics PLY,
or uncompressed base-color KSPLAT.

The reconstruction recipe remains fixed at 1024px preprocessing and a 20-step
local sample. Each successful run saves three complementary artifacts: a still
PNG preview, a 1024px three-second MP4 orbit at 25 fps, and the selected splat
file. Runner uses the PNG for the visual result card, exposes the orbit as a
video/download in run detail, and exposes SPZ, PLY, or KSPLAT as a direct
download. Interactive splat viewing remains outside this first Runner slice.

LF Nodes does not distribute the required weights. The default graph expects a
TripoSplat diffusion model and decoder, a DINOv3 vision encoder, a Flux2 image
VAE, and the Core BiRefNet background-removal model. In the shipped recipe those
literal files are `triposplat_fp16.safetensors`,
`triposplat_vae_decoder_fp16.safetensors`, `dino_v3_vit_h.safetensors`,
`flux2-vae.safetensors`, and `birefnet.safetensors`. The corresponding current
ComfyUI Core node types must also be loaded. Catalogue readiness reports a
missing known file or node as `setup_required`; it never downloads a model.

A Gaussian splat is a viewable radiance representation, not polygonal geometry.
The card produces no watertightness, manifold-topology, rigging, or game-ready
optimization pass. Hidden surfaces are inferred, and input isolation and
silhouette quality materially affect the reconstruction.

### TRELLIS.2 workflows

The shipped `TRELLIS.2` category contains two local textured-mesh cards.
`Image to Textured Mesh` accepts one source image. `Multi-view to Textured Mesh`
requires a front view and optionally accepts matching rear, left, and right
views. Extra views constrain hidden surfaces only when they show the same subject
state, scale, lighting, and framing. Both cards expose a seed and two bounded
quality profiles:

- **Balanced 1024 cascade** (default): 12 structure, shape, and texture steps,
  a 200k-face target, and embedded 4K textures. This is the established 24 GB
  starting profile.
- **Draft 512**: the same 12-step schedule with a 100k-face target and embedded
  2K textures for lighter iteration.

Each run exports a PBR-textured GLB, saves a deterministic 512px front render,
and registers the GLB's relative output path with `LF_RegisterOutputFile`.
Runner therefore gets a durable visual history card plus a direct mesh download
without exposing an absolute host path. Textures are embedded in the GLB;
transparency may still need to be enabled in the destination material. The
current Runner intentionally does not embed a WebGL mesh viewer.

These cards require the local TRELLIS.2 wrapper, its matching native CUDA
extensions, the official `microsoft/TRELLIS.2-4B` model, DINOv3 weights, the
Core BiRefNet model, and the LF output-registration node. The third-party
wrapper can otherwise fetch several gigabytes of model data during execution.
LF Nodes does not initiate those downloads: these shipped cards explicitly
declare their local multi-file model assets and remain **Setup required** until
every declared file is present. Readiness also checks that the workflow's node
types are registered and that known Core loader files are present. It cannot
prove that a compiled CUDA extension matches the active Python, PyTorch, and
CUDA ABI.

The preview renderer uses `nvdiffrast`, whose compiled extension must match the
active Python, PyTorch, CUDA, and GPU environment.

TRELLIS.2 output is a presentation-oriented textured mesh. Multi-view input can
improve unseen geometry; the cards add no watertightness, manifold-topology,
production-UV, skeleton, or game-ready optimization pass.

### Catalogue readiness

Each workflow catalogue entry includes a `readiness` object with a `status`
(`ready`, `warning`, or `setup_required`) and a bounded list of machine-readable
`issues` (`{code, message}`). The check is intentionally lightweight: it reads
the card's default prompt, compares its node types with ComfyUI's loaded
`NODE_CLASS_MAPPINGS`, and verifies literal file choices only for known Core
model-loader inputs. A shipped workflow may additionally declare bounded file
requirements below ComfyUI's model root; related files can be grouped into one
asset so an incomplete package produces one useful setup issue. The check does
not load models, download files, contact a remote service, hash large assets,
or try to predict whether every optional model choice is installed.

`setup_required` means a concrete, immutable dependency is absent (the workflow
file, a node type, or a known loader file that the form cannot replace).
A missing default on a loader directly exposed by the form is a `warning`, so
the user can choose an installed alternative. General node/import and known
loader-category scanner uncertainty is also only a warning; it is never treated
as proof that a workflow cannot run. A workflow's explicitly declared local
model prerequisites are different: if Runner cannot verify those bounded paths,
it fails closed as `setup_required` rather than allowing execution to fall
through to a third-party auto-download path. Runner disables Run only for
`setup_required` and shows the first actionable reason in the workflow form;
warning cards remain runnable.

### Run control and output handoff

Each Run click owns a stable client-generated submission ID. The floating Run
button locks while admission is ambiguous, then becomes an elapsed Stop control
for that exact pending or running job. Cancellation is owner-bound and targets
only the corresponding Comfy prompt; terminal races retain their real outcome.

Durable replay and Stop authority begin once the accepted Comfy prompt is bound
to its SQLite job row. One narrow host-crash window remains: if the Runner
process dies after Core accepts the prompt but before that row commits, a retry
after restart cannot recover the original stable ID and may submit the work
again. Closing that window requires a pre-queue durable reservation plus a
preassigned Core prompt UUID across every admission provider; the current
provider ABI deliberately does not claim that guarantee.

A succeeded Runner-owned run may expose bounded `lf.workflow-artifact.v1`
descriptors in its detail response. **Use in…** offers available artifacts only
to compatible upload inputs on workflows that are not `setup_required`. The
browser passes an opaque `lf.workflow-artifact-ref.v1` identity; the server
recomputes the source manifest, rechecks ownership, media compatibility, root
containment, symlinks, and file existence at queue time. Absolute host paths are
never returned. This handoff prefills the destination but never auto-runs it.

New files selected in Runner are stored explicitly in ComfyUI's input directory,
using collision-safe filenames, rather than its disposable temp directory. The
upload response contains only a portable Comfy input reference; the server keeps
the resolved host path private in the run snapshot and later remixes reuse it
through the same owner-bound opaque upload reference. Legacy temp uploads that
have already disappeared remain unavailable and require reselection.

### In-session workflow drafts

Runner keeps one unfinished form draft per workflow while the current browser
page remains open. Moving between Home, History, and workflow cards restores
text, chat, selections, toggles, retained opaque upload references, and any
still-live selected `File` objects. Drafts are intentionally memory-only: they
are not presets, do not use local storage, and disappear on page reload. **Reset**
clears only the current workflow's draft and remounts its declaration defaults.
An explicit **Remix** replaces the ordinary draft with the selected run's inputs;
neither draft navigation nor Reset starts, cancels, or mutates a submission.

## Architecture Principles

### Separation of Concerns (SoC)

The codebase is strictly organized by responsibility:

- **Controllers**: HTTP request/response handling
- **Services**: Business logic and external integrations
- **Models**: Data structures and schemas
- **Adapters**: External system interfaces
- **Utils**: Shared helper functions

### Don't Repeat Yourself (DRY)

- Shared utilities are centralized in `modules/utils/`
- Common patterns are extracted into reusable components
- Configuration is centralized in `config.py`

### Lazy Loading

To avoid importing heavy dependencies (Torch, CUDA, etc.) at package import time:

- Controllers use lazy imports for heavy service dependencies
- The `controllers/__init__.py` provides lazy forwarding
- Route registration uses `importlib` to defer controller imports

## Package Structure

```text
modules/workflow_runner/
├── __init__.py              # Package exports with lazy loading
├── config.py                # Centralized configuration management
├── adapters/                # External system interfaces
│   └── storage_adapter.py   # Abstract storage interface
├── controllers/             # HTTP request handlers
│   ├── __init__.py          # Lazy forwarding layer
│   ├── api_controllers.py   # Core API endpoints
│   ├── api_routes.py        # Route registration decorators
│   ├── routes.py            # Compatibility shim for imports
│   ├── page_controller.py   # Page serving
│   ├── assets_controller.py # Static asset serving
│   ├── proxy_controller.py  # API proxying
│   └── _helpers.py          # Shared controller utilities
├── models/                  # Data structures
│   ├── __init__.py
│   └── schemas.py           # Request/response schemas
├── services/                # Business logic
│   ├── __init__.py
│   ├── auth_service.py      # Authentication & authorization
│   ├── run_service.py       # Workflow execution orchestration
│   ├── job_service.py       # Job status tracking
│   ├── workflow_service.py  # Workflow metadata management
│   ├── executor.py          # Core execution logic
│   ├── background.py        # Background task management
│   ├── google_oauth.py      # OAuth token verification
│   ├── history_cleanup.py   # Conservative missing-artifact history pruning
│   ├── readiness.py         # Non-executing catalogue readiness checks
│   ├── remix_inputs.py      # Owner-bound upload and output-artifact reuse
│   ├── job_store.py         # In-memory job storage
│   ├── job_store_sqlite.py  # SQLite-based persistent job storage
│   ├── proxy_service.py     # API proxy logic
│   └── registry.py          # Workflow registry
├── utils/                   # Shared utilities
│   ├── __init__.py
│   ├── errors.py            # Custom exception types
│   ├── helpers.py           # Common helper functions
│   ├── media.py             # Shared artifact media-type mapping
│   └── serialize.py         # Job serialization utilities
├── scripts/                 # Utility scripts
│   └── frontend_proxy.py    # Reverse proxy for development
├── tests/                   # Unit tests
│   ├── test_routes.py
│   ├── test_run_service.py
│   └── test_workflow_conversion.py
└── workflows/               # Workflow definitions
    ├── __init__.py
    ├── caption_image_vision.py/.json  # Image captioning with vision LLM
    ├── image_to_svg.py/.json          # Convert images to SVG
    ├── load_metadata.py/.json         # Extract image metadata
    ├── remove_bg.py/.json             # Background removal
    ├── simple_chat.py/.json           # Simple LLM chat interface
    ├── sort_json_keys.py/.json        # Sort JSON keys alphabetically
    ├── svg_generation_gemini.py/.json # Generate SVG with Gemini
    ├── t2i_15_lcm.py/.json            # Text-to-image with LCM
    └── utils.py                       # Shared workflow utilities
```

## Key Components

### Controllers Layer

Thin HTTP adapters that:

- Validate and deserialize input
- Call service layer functions
- Handle HTTP-specific concerns (status codes, content types)
- Avoid business logic
- Use shared utilities from `_helpers.py` for common operations (JSON parsing, job serialization)

**Example:**

```python
async def start_workflow_controller(request: web.Request) -> web.Response:
    # Validate input with helpers
    payload, error_response = await parse_json_body(request)
    if error_response:
        return error_response

    # Call service
    result = await run_workflow(payload)

    # Return HTTP response
    return web.json_response(result, status=202)
```

### Services Layer

Contains all business logic:

- **auth_service.py**: OAuth authentication, session management
- **run_service.py**: Workflow execution orchestration
- **job_service.py**: Job status tracking and persistence
- **workflow_service.py**: Workflow metadata and file operations
- **executor.py**: Core workflow execution logic, including queue state monitoring
  - Monitors workflow execution state transitions (PENDING → RUNNING → completed)
  - Handles three scenarios: normal execution, fast completion, and queued waiting
  - Uses indefinite polling until job starts or completes (no fixed iteration limit)

### Models Layer

Data structures using dataclasses:

- **schemas.py**: Request/response validation schemas
- Lightweight, no external dependencies
- Type-safe data transfer objects

### Adapters Layer

Abstractions for external systems:

- **storage_adapter.py**: Pluggable storage interface
- Allows swapping storage backends (filesystem, database, etc.)

### Job Storage Layer

Dual implementation for different deployment scenarios:

- **job_store.py** (In-Memory):
  - Fast, simple dict-based storage
  - Suitable for development and single-session use
  - No persistence across restarts
  
- **job_store_sqlite.py** (Persistent):
  - Async SQLite operations via `aiosqlite`
  - Persistent job history across restarts
  - Built-in SSE event streaming with resume support
  - Configurable database path via environment variable
  - Thread-safe with async lock coordination

The active storage backend is determined by configuration in `job_service.py`.

### History Cleanup

The History view exposes **Remove missing** for pruning stale Runner records.
It removes terminal failures and successful runs only when every safely
recorded local artifact is definitively absent. Active runs, successful
fileless outputs, malformed or ambiguous legacy records, and runs with any
remaining artifact are preserved. Cleanup removes Runner history and its remix
input snapshot; it never deletes ComfyUI history or files.

The UI previews the candidate count before confirmation through
`POST /api/lf-nodes/workflow-runner/runs/prune-missing-artifacts` with
`{"dry_run": true}`. Confirmed cleanup repeats the scan with `dry_run: false`
and hard-deletes each unchanged record using owner, status, sequence, and
update-time matching. At the destructive boundary, Runner also verifies a
well-formed ComfyUI queue snapshot and preserves every pending or running
prompt. If the queue cannot be verified, cleanup fails safe and removes
nothing.

## Data Flow

### Workflow Execution Flow

1. **HTTP Request** → `controllers/api_routes.py`
2. **Input Validation** → `controllers/api_controllers.py`
3. **Job Creation** → `services/job_store.py`
4. **Workflow Execution** → `services/run_service.py` → `services/executor.py`
5. **Progress Updates** → WebSocket via `utils/helpers.py`
6. **Result Storage** → `services/job_store.py`
7. **HTTP Response** → Client

### Authentication Flow

1. **OAuth Callback** → `controllers/api_controllers.py`
2. **Token Verification** → `services/auth_service.py` → `services/google_oauth.py`
3. **Session Creation** → `services/auth_service.py`
4. **Request Authorization** → Middleware checks session

## Key Design Decisions

### 1. No External File Touches

- Cannot modify ComfyUI core files
- Uses autoregistration via module imports
- Leverages ComfyUI's existing routing system

### 2. Heavy Dependency Isolation

- ComfyUI automatically imports all custom node modules
- Lazy loading prevents Torch/CUDA initialization at import time
- Controllers import services on first use

### 3. Autoregistration for Routes

- Routes register themselves via decorators in `api_routes.py`
- `controllers/routes.py` is a compatibility shim for test imports
- No manual route registration required

### 4. Persistent Job Storage

- **In-Memory** (`job_store.py`): Simple dict-based storage for job status
- **SQLite** (`job_store_sqlite.py`): Persistent storage with async operations
- Configurable storage backend via `job_service.py`
- SQLite adapter includes SSE event streaming and job history persistence

### 5. WebSocket Progress Updates

- Real-time progress via ComfyUI's WebSocket system
- Structured progress events with run_id and message
- Extensible for additional progress metadata

## Testing Strategy

### Python Backend

- Unit tests for core services
- Integration tests for API endpoints
- Mock external dependencies (ComfyUI server, OAuth)

### TypeScript Frontend

- Unit tests for state management
- Component interaction tests
- API integration tests

### Test Organization

```text
tests/
├── test_routes.py       # Route registration tests
├── test_run_service.py  # Workflow execution tests
└── test_workflow_conversion.py  # Workflow processing tests
```

## Configuration Management

### Environment Variables

**Core Settings:**

- `WORKFLOW_RUNNER_ENABLED`: When set to a truthy value (e.g., `1` or `true`), the Workflow Runner will register its HTTP routes and static frontend at startup. Default: `false`
- `WORKFLOW_RUNNER_EXTRA_WORKFLOW_ROOTS`: Optional comma- or semicolon-separated list of absolute directories containing project-owned `.py` workflow definitions and their `.json` graphs. Default: empty
- `WORKFLOW_RUNNER_EXTRA_WORKFLOW_GROUPS`: Optional ordered display labels matching `WORKFLOW_RUNNER_EXTRA_WORKFLOW_ROOTS`. These trusted labels keep each project's workflows together under the drawer's Custom branch without exposing filesystem paths. Missing labels fall back to `Custom`. Default: empty
- `WORKFLOW_RUNNER_DEBUG`: Enable debug logging. Default: `false`
- `DEV_ENV`: Enable development environment features. Default: `false`

**Authentication & Authorization:**

- `ENABLE_GOOGLE_OAUTH`: Enable OAuth authentication. Default: `false`
- `GOOGLE_CLIENT_IDS`: Comma-separated list of allowed OAuth client IDs
- `GOOGLE_IDTOKEN_CACHE_SECONDS`: OAuth token cache duration. Default: `3600`
- `ALLOWED_USERS_FILE`: Path to file containing allowed user emails (one per line)
- `ALLOWED_USERS`: Comma-separated list of allowed user emails
- `REQUIRE_ALLOWED_USERS`: Require users to be in allowlist. Default: `true`
- `SESSION_TTL_SECONDS`: Session timeout in seconds. Default: same as `GOOGLE_IDTOKEN_CACHE_SECONDS`
- `SESSION_PRUNE_INTERVAL_SECONDS`: How often to clean up expired sessions. Default: `60`
- `USER_ID_SECRET`: Secret for deterministic owner ID generation (uses default if not set)

**Job Storage:**

- `WORKFLOW_RUNNER_USE_PERSISTENCE`: Use SQLite for persistent storage instead of in-memory. Default: `false`
- `WORKFLOW_RUNNER_DB_PATH`: Path to SQLite database file (uses default location if not set)
- `JOB_TTL_SECONDS`: Optional automatic terminal-history retention after the
  last terminal update. Default: `0` (disabled), so Runner history remains
  durable until the explicit **Remove missing** action is used. A positive
  value enables operator-managed retention; it never makes active work
  terminal and removes an expired row only after a validated ComfyUI queue
  snapshot proves its prompt is neither pending nor running.
- `JOB_PRUNE_INTERVAL_SECONDS`: How often to clean up old jobs. Default: `60`

**Proxy Settings:**

- `COMFY_BACKEND_URL`: ComfyUI backend URL for proxying
- `PROXY_FRONTEND_PORT`: Port for development frontend proxy. Default: `0`
- `LF_PROXY_SERVICE_FILE`: Path to proxy service configuration file
- `KOBOLDCPP_BASE_FILE`: Path to KoboldCpp base URL file
- `GEMINI_API_KEY_FILE`: Path to Gemini API key file
- `OPENAI_API_KEY_FILE`: Path to OpenAI API key file
- `PROXY_ALLOWED_PREFIXES`: Comma-separated list of allowed proxy URL prefixes
- `PROXY_RATE_LIMIT_REQUESTS`: Max requests per time window. Default: `60`
- `PROXY_RATE_LIMIT_WINDOW_SECONDS`: Rate limit time window in seconds. Default: `60`

**Optional Media Integrations:**

- `LF_YOUTUBE_INGEST_ENABLED`: Enable verified, cache-aware YouTube reference intake. Default: `false`
- `LF_ACESTEP_API_URL`: Base URL of an ACE-Step API server. Default: `http://127.0.0.1:8001`
- `LF_ACESTEP_API_TOKEN`: Optional bearer token for the ACE-Step API. Default: empty
- `LF_ACESTEP_TIMEOUT_SECONDS`: Maximum wait for one ACE-Step job, from `1` to `86400` seconds. Default: `3600`

**Notes:**

- The runner is shipped inside the `lf-nodes` package but is opt-in by default. If `WORKFLOW_RUNNER_ENABLED` is not set or is false, route registration is skipped and the runner will not expose its APIs or UI.
- Configuration is read from the repository-level `.env` (project root).
- Extra workflow roots are trusted Python source directories. Their modules are discovered at first registry access, so configure them before startup and restart ComfyUI after changing the setting or files.
- External modules share the `modules.workflow_runner.workflows.custom` import namespace. Use unique filenames: the bundled custom directory and then the configured roots are searched in order, and the first module with a given filename wins with a warning for later duplicates. Duplicate workflow IDs retain the existing last-registration-wins behavior and emit a warning.
- If you enable the runner, please also configure authentication/allowed-users to avoid exposing the endpoints unintentionally.
- For persistence, set `WORKFLOW_RUNNER_USE_PERSISTENCE=true` to enable SQLite storage for job history.

### Settings Class

Centralized configuration in `config.py`:

- Environment variable parsing
- Type conversion and validation
- Default value handling

## Error Handling

### Custom Exceptions

- `WorkflowPreparationError`: Workflow validation failures
- Structured error responses with status codes
- Client-friendly error messages

### Logging Strategy

- Structured logging with context
- Debug logging for troubleshooting
- Error logging with stack traces

## Security Considerations

### Authentication

- Google OAuth 2.0 integration
- Session-based authentication
- Configurable user allowlists

### Authorization

- Route-level authentication checks
- Session validation on protected endpoints
- Graceful handling of unauthenticated requests

### Input Validation

- JSON schema validation for requests
- Type checking for parameters
- Sanitization of user inputs

## Performance Optimizations

### Lazy

- Defer heavy imports until needed
- Reduce startup time
- Avoid unnecessary dependency initialization

### Background Execution

- Asynchronous workflow execution
- Non-blocking HTTP responses
- Progress tracking via WebSocket

### Caching

- OAuth token caching
- Session storage
- Workflow metadata caching

## Future Considerations

### Scalability

- ✅ Job storage now supports SQLite for persistence (`job_store_sqlite.py`)
- Session storage could use Redis/external store
- Horizontal scaling would require distributed lock coordination for SQLite or migration to PostgreSQL/MySQL

### Extensibility

- Plugin architecture for additional workflow types
- Custom authentication providers
- Additional storage adapters

### Monitoring

- Structured logging for observability
- Metrics collection for performance monitoring
- Health check endpoints

## Development Workflow

### Building

```bash
yarn build  # TypeScript compilation and bundling
```

### Testing

```bash
yarn test   # Run TypeScript tests
```

### Development Server

```bash
python main.py  # Start ComfyUI with LF Nodes
```

### Debugging

- Use `WORKFLOW_RUNNER_DEBUG=1` for verbose logging
- Frontend proxy script for development
- WebSocket debugging for real-time features
