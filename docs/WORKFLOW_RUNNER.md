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
├── api_constants.py         # Lightweight API constants (no heavy imports)
├── config.py                # Centralized configuration management
├── routes.py                # Route registration and controller imports
├── google_oauth.py          # REMOVED - was compatibility shim
├── adapters/                # External system interfaces
│   └── storage_adapter.py   # Abstract storage interface
├── controllers/             # HTTP request handlers
│   ├── __init__.py          # Lazy forwarding layer
│   ├── api_controllers.py   # Core API endpoints
│   ├── api_routes.py        # Route decorators
│   ├── page_controller.py   # Page serving
│   ├── assets_controller.py # Static asset serving
│   └── proxy_controller.py  # API proxying
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
│   ├── proxy_service.py     # API proxy logic
│   └── registry.py          # Workflow registry
├── utils/                   # Shared utilities
│   ├── __init__.py
│   ├── errors.py            # Custom exception types
│   └── helpers.py           # Common helper functions
├── scripts/                 # Utility scripts
│   └── frontend_proxy.py    # Reverse proxy for development
├── tests/                   # Unit tests
│   ├── test_routes.py
│   ├── test_run_service.py
│   └── test_workflow_conversion.py
└── workflows/               # Workflow definitions
    ├── __init__.py
    ├── image_to_svg.py
    ├── load_metadata.py
    ├── remove_bg.py
    ├── simple_chat.py
    ├── sort_json_keys.py
    ├── svg_generation_gemini.py
    └── utils.py
```

## Key Components

### Controllers Layer

Thin HTTP adapters that:

- Validate and deserialize input
- Call service layer functions
- Handle HTTP-specific concerns (status codes, content types)
- Avoid business logic

**Example:**

```python
async def start_workflow_controller(request: web.Request) -> web.Response:
    # Validate input
    payload = await request.json()

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
- **executor.py**: Core workflow execution logic

### Models Layer

Data structures using dataclasses:

- **schemas.py**: Request/response validation schemas
- Lightweight, no external dependencies
- Type-safe data transfer objects

### Adapters Layer

Abstractions for external systems:

- **storage_adapter.py**: Pluggable storage interface
- Allows swapping storage backends (filesystem, database, etc.)

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

- Routes register themselves via decorators in controller modules
- `routes.py` imports controllers to trigger registration
- No manual route registration required

### 4. In-Memory Job Storage

- Simple dict-based storage for job status
- Suitable for single-instance deployments
- Can be extended with persistent storage adapters

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

- `ENABLE_GOOGLE_OAUTH`: Enable OAuth authentication
- `GOOGLE_CLIENT_IDS`: Allowed OAuth client IDs
- `WORKFLOW_RUNNER_DEBUG`: Enable debug logging
- `ALLOWED_USERS_FILE`: Path to allowed users file
- `SESSION_TTL_SECONDS`: Session timeout

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

- Job storage could be moved to persistent storage
- Session storage could use Redis/external store
- Horizontal scaling would require shared storage

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
