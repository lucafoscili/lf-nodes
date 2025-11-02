# Frontend Proxy (frontend_proxy.py)

This document describes the lightweight frontend proxy used to expose a very small, opt-in public surface for ComfyUI's workflow-runner. The proxy is intentionally narrow (deny-by-default) and kept inside the `custom_nodes` area so the Comfy core doesn't need modification.

## Purpose

- Expose only allowed HTTP prefixes from a public/tunneled endpoint (for example a VS Code devtunnel) and forward those requests to the local Comfy backend (usually 127.0.0.1:8188).
- Reduce attack surface by denying everything not explicitly allowed.
- Preserve important headers (Host, X-Forwarded-For, X-Forwarded-Proto) so Comfy origin checks continue to work.

## Location

`custom_nodes/lf-nodes/modules/workflow_runner/scripts/frontend_proxy.py`

## How it works (summary)

- Listens on a configurable frontend port (default in code: PROXY_FRONTEND_PORT). Typically you run the proxy locally and then expose that port with your chosen tunnel (devtunnels, Cloudflare Tunnel, ngrok, etc.).
- Accepts incoming HTTP requests and only allows requests whose path starts with an allowed prefix (configured in `PROXY_ALLOWED_PREFIXES`).
- Forwards the request to the configured backend URL (`COMFY_BACKEND_URL`), copying headers and preserving Host and X-Forwarded-* headers.
- Returns the upstream response body, status code and relevant headers (e.g., Set-Cookie) to the client.
- Optional debug mode (`WORKFLOW_RUNNER_DEBUG`) returns upstream traceback text in 502 responses to help troubleshooting locally (do NOT enable in public production).

## Configuration (env vars / config values)

Key values read by the proxy / routes module (see the code for defaults):

- `PROXY_FRONTEND_PORT` — port the proxy listens on (e.g., 9188).
- `COMFY_BACKEND_URL` — full URL of the local Comfy backend, e.g. `http://127.0.0.1:8188`.
- `PROXY_ALLOWED_PREFIXES` — list/tuple of path prefixes that are permitted (deny-by-default). Examples added for workflow-runner: `/api/lf-nodes/workflow-runner`, `/queue`, `/api/lf-nodes/workflows`, `/api/lf-nodes/run`, `/view`, `/favicon.ico`.
- `WORKFLOW_RUNNER_DEBUG` — boolean flag, when enabled returns more upstream details for debugging.

The exact variable names and defaults live in `frontend_proxy.py` and `routes.py` — check those files when changing behavior.

## Running (PowerShell)

From the repository root (recommended), run the proxy in the `custom_nodes/lf-nodes` working directory so relative imports work:

```powershell
cd C:\Users\luca.foscili_smeup\Documents\GitHub\ComfyUI\custom_nodes\lf-nodes
# Run with the repo's Python environment
& "C:\Users\luca.foscili_smeup\Documents\GitHub\ComfyUI\.venv\Scripts\python.exe" .\modules\workflow_runner\scripts\frontend_proxy.py
```

If you set environment variables before running in PowerShell, use `setx` (persist) or `$env:VAR = 'value'` for the session:

```powershell
$env:COMFY_BACKEND_URL = 'http://127.0.0.1:8188'
$env:PROXY_FRONTEND_PORT = '9188'
$env:WORKFLOW_RUNNER_DEBUG = '1'
& "C:\Users\luca.foscili_smeup\Documents\GitHub\ComfyUI\.venv\Scripts\python.exe" .\modules\workflow_runner\frontend_proxy.py
```

Note: when using VS Code devtunnels (or other tunnels) make sure the tunnel terminates TLS and forwards plain HTTP to the proxy (or that the proxy handles TLS). If you see `502` and a log entry showing "UNKNOWN / HTTP/1.0" with TLS ClientHello bytes, the tunnel is doing passthrough — switch the tunnel port to HTTP termination.

## Debugging checklist

- If you see 403 from Comfy: verify the proxy forwards the original `Host` header and `X-Forwarded-Proto` header. Comfy verifies origin/host and will return 403 otherwise.
- If the UI shows a persistent login splash: ensure these endpoints are allowed by the proxy and returning 200: `/queue`, `/api/lf-nodes/workflows`, `/api/lf-nodes/run`. Also ensure the login flow sets `LF_SESSION` cookie (HttpOnly) and that the client includes cookies in requests (UI uses fetch with `credentials:'include'`).
- Use the debug-only endpoint (if enabled) to create a session for testing: `/api/lf-nodes/workflow-runner/debug-login` (guarded by the `WORKFLOW_RUNNER_DEBUG` flag in the code). Do NOT enable this flag in a public environment.

## Streaming behaviour (dev proxy)

- The dev reverse proxy now supports streaming responses (SSE / chunked) and will forward upstream chunks directly to the client when appropriate. This avoids buffering streaming responses which previously prevented the UI from receiving incremental deltas.
- Streaming is detected heuristically by the proxy when the upstream response has `Content-Type: text/event-stream` or `Transfer-Encoding: chunked`.
- By default streaming is gated to the internal proxy endpoint to avoid exposing raw streamed content for arbitrary proxied paths. The env var `PROXY_STREAMING_ONLY_PROXY` (default `1`) controls this behaviour:
  - `PROXY_STREAMING_ONLY_PROXY=1` (default): only allow streaming when the incoming path starts with `/api/lf-nodes/proxy`.
  - `PROXY_STREAMING_ONLY_PROXY=0`: allow streaming for any allowed proxied path.

When streaming is blocked by the gate the proxy falls back to the previous buffered behaviour and returns the full response only after the upstream completes.

## Security considerations & recommendations

- The proxy narrows the public surface but does not make the backend fully safe for production by itself.
- For production or longer-term sharing consider:
  - Replacing Google `tokeninfo` usage with JWKS-signed id_token verification and caching the JWKS.
  - Adding rate-limiting to the `/verify` token endpoint (per-IP and per-session sliding window).
  - Storing sessions in a persistent backend (Redis) and adding a background session prune job.
  - Using signed, short-lived download URLs if you need to expose `/view` outputs publicly.
  - Turning off `WORKFLOW_RUNNER_DEBUG` and any debug endpoints before making the service publicly accessible.

## Google OAuth (optional) — env vars and setup notes

If you enabled the Google-based gating in the workflow-runner routes, the proxy + routes expect a small set of environment variables controlling OAuth behavior. These are optional — the whole auth flow is opt-in and lives inside the custom node.

Primary env vars used by the workflow-runner OAuth flow:

- `ENABLE_GOOGLE_OAUTH` — set to `1` to enable Google login gating for the workflow-runner endpoints. If disabled, the verify/login flow will be bypassed (depending on other flags in `routes.py`).
- `GOOGLE_CLIENT_IDS` — one or more OAuth 2.0 Client IDs (from Google Cloud) that the frontend's Google Identity SDK may use. Format: a single client id or a comma-separated list. Example:

  GOOGLE_CLIENT_IDS=490526385899-vl8rhf986upcupda1gcvh882o615g7qh.apps.googleusercontent.com

- `ALLOWED_USERS_FILE` — full path to a newline-separated text file that lists allowed user emails (one per line). If provided and `REQUIRE_ALLOWED_USERS` is enabled, only the listed email addresses will be permitted access. Example in your `.env`:

  ALLOWED_USERS_FILE=C:\secrets\allowed_users.txt

  The file should contain entries like:

  ```text
  alice@example.com
  bob@example.com
  ```

Additional flags you may see in the codebase (not required but relevant):

- `REQUIRE_ALLOWED_USERS` — if set, the service enforces that verified users appear in the `ALLOWED_USERS_FILE` (deny by default otherwise).
- `WORKFLOW_RUNNER_DEBUG` — debug-only endpoint(s) may be enabled if this is set; do NOT enable in public environments.

Important setup steps & gotchas:

- Authorized JavaScript origins: when you create (or edit) a Google OAuth Client ID in Google Cloud Console, you must add the public origin your users will visit (for example the devtunnel URL like `https://12345-0.tunnels.remote.dev`) to the list of Authorized JavaScript origins. If the origin is not registered, the Identity SDK will report "Given origin is not allowed for the given client ID" and login will fail.
- Absolute redirect/login URIs: the frontend expects absolute URIs for the Google Identity SDK configuration. If you see errors about "Relative login_uri" in the browser console, register the full origin and use the absolute URL the user navigates to.
- Token verification mode: the current helper uses Google's `tokeninfo` endpoint for simplicity (suitable for testing). For production you should verify id_tokens locally using Google's JWKS (`/oauth2/v3/certs`) and validate signatures, aud/iss/exp and nonce. JWKS verification is faster and does not rely on an extra network call per token.
- Cookie and SameSite behavior: `LF_SESSION` cookie is set as HttpOnly and SameSite=Lax by default in the routes. If your tunnel or browser enforces cross-site restrictions, ensure the browser allows the cookie to be set from the public origin and that the UI uses `fetch(..., { credentials: 'include' })` on requests that need the session cookie.

## Troubleshooting common errors

- 502 Bad Gateway from tunnel: check tunnel protocol (HTTP vs TLS passthrough). Switch tunnel to HTTP termination.
- 403 from Comfy: ensure `Host` and `X-Forwarded-Proto` forwarded by proxy match the public origin registered in Google OAuth and what Comfy expects.
- Login stuck: check browser cookie policy (SameSite, Secure), make sure the redirect is absolute and that the UI fetches use credentials.
