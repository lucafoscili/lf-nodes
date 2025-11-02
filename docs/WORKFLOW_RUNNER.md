# Workflow Runner Miniapp Architecture

## Overview

The Workflow Runner is a miniapp within LF Nodes that provides a web-based interface for executing ComfyUI workflows. It allows users to select, configure, and run workflows through a modern web UI, with real-time progress tracking and result visualization.

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
│   ├── job_store.py         # In-memory job storage
│   ├── job_store_sqlite.py  # SQLite-based persistent job storage
│   ├── proxy_service.py     # API proxy logic
│   └── registry.py          # Workflow registry
├── utils/                   # Shared utilities
│   ├── __init__.py
│   ├── errors.py            # Custom exception types
│   ├── helpers.py           # Common helper functions
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
- `JOB_TTL_SECONDS`: How long to keep completed jobs in storage. Default: `300`
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

**Notes:**

- The runner is shipped inside the `lf-nodes` package but is opt-in by default. If `WORKFLOW_RUNNER_ENABLED` is not set or is false, route registration is skipped and the runner will not expose its APIs or UI.
- Configuration is read from the repository-level `.env` (project root).
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
