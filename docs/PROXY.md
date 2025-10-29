Proxy README
============

This document describes the multi‑service proxy used by the workflow runner to securely call external AI APIs (e.g., OpenAI, Gemini) without exposing keys to the browser.

Endpoints
---------

- POST /api/lf-nodes/proxy/{service}
  - service: openai, gemini, or kobold (see Services below)
  - Auth: if LF_PROXY_SECRET is set, the request must include header X-LF-Proxy-Secret: <secret>
  - Body: JSON payload in the shape expected by the upstream provider. The proxy injects keys and forwards it.
  - Response: Upstream JSON with an additional lf_http_status field or a normalized error payload.

Services
--------

- openai
  - Upstream: https://api.openai.com/v1/chat/completions
  - Env: OPENAI_API_KEY (or OPENAI_API_KEY_FILE)
  - Default model: gpt-4o (override by including model in the request body)
- gemini
  - Upstream: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
  - Env: GEMINI_API_KEY (or GEMINI_API_KEY_FILE)
  - Default model: gemini-2.0-flash (override with model in the request body)

- kobold (LAN/self-hosted KoboldCPP)
  - Upstream: base+path (no API key expected)
  - Env: KOBOLDCPP_BASE (e.g. http://192.168.1.50:5001)
  - Default path: /api/v1/generate (override by sending {"path":"/api/v1/generate/stream"} in the body)
  - Allowed paths: /api/v1/generate, /api/v1/generate/stream (requests to other paths are rejected)

Rate limiting
-------------

Basic per‑IP rate limiting is enabled by default:

- Global defaults (can be overridden per service):
  - PROXY_RATE_LIMIT_REQUESTS (default: 60)
  - PROXY_RATE_LIMIT_WINDOW_SECONDS (default: 60)
- Returns 429 + Retry-After when the limit is exceeded.

Secrets
-------

Use one secret per file and set the corresponding *_FILE environment variable when possible. Supported envs:

- OPENAI_API_KEY or OPENAI_API_KEY_FILE
- GEMINI_API_KEY or GEMINI_API_KEY_FILE
- LF_PROXY_SECRET or LF_PROXY_SECRET_FILE (shared secret required by the proxy endpoint)
- KOBOLDCPP_BASE or KOBOLDCPP_BASE_FILE (base URL for LAN/self-hosted KoboldCPP)

Local development
-----------------

For local convenience you can place a .env file and set DEV_ENV=1 before starting the server. The server will load .env only when DEV_ENV is set to avoid accidental production usage.

Example .env (do NOT commit this file):

`plaintext
# Enable local .env loading
DEV_ENV=1

# Option A: Direct keys (development convenience)
OPENAI_API_KEY=sk.example_openai_key
GEMINI_API_KEY=ya29.example_key
LF_PROXY_SECRET=replace_with_secret

# Option B: Preferred: point to per‑secret files
OPENAI_API_KEY_FILE=C:\my_secret_secrets\openai.txt
GEMINI_API_KEY_FILE=C:\my_secret_secrets\gemini.txt
LF_PROXY_SECRET_FILE=C:\my_secret_secrets\lf_proxy_secret.txt
KOBOLDCPP_BASE_FILE=C:\my_secret_secrets\kobold_base.txt
`

Client usage
------------

Example request to the OpenAI chat endpoint through the proxy (PowerShell):

`powershell
 = @{ 
  model = 'gpt-4o'
  messages = @(@{ role = 'user'; content = 'Hello!' })
} | ConvertTo-Json -Depth 6

Invoke-RestMethod \
  -Method Post \
  -Uri http://localhost:8188/api/lf-nodes/proxy/openai \
  -Headers @{ 'Content-Type'='application/json'; 'X-LF-Proxy-Secret'='replace_with_secret' } \
  -Body 
`

Example request to a LAN KoboldCPP via the proxy (PowerShell):

`powershell
$body = @{ 
  # Optional: choose the upstream route; defaults to /api/v1/generate
  path   = '/api/v1/generate' 
  prompt = 'Write a haiku about autumn.'
} | ConvertTo-Json -Depth 6

Invoke-RestMethod \
  -Method Post \
  -Uri http://localhost:8188/api/lf-nodes/proxy/kobold \
  -Headers @{ 'Content-Type'='application/json' } \
  -Body $body
`

Environment required for KoboldCPP:

`plaintext
KOBOLDCPP_BASE=http://192.168.1.50:5001
`

Front‑end integration (runner)
-------------------------------

Prefer routing chat through the proxy so API keys remain server‑side. A minimal config shape could be:

`jsonc
// runner.config.json
{
  "chat": {
    "useProxy": true,
    // One of: "openai", "gemini", "kobold"
    "provider": "kobold"
    // Optional: custom path under the API root (defaults to /proxy/{provider})
    // "path": "/proxy/kobold"
  }
}
`

Then POST the native provider body to /api/lf-nodes/proxy/{provider} (optionally include model to override the default). The proxy will append the correct auth headers and return the upstream payload.

Security
--------

- Keep keys out of client config; use the proxy and env secrets.
- Mount secrets as read‑only files and scope permissions to the service account.
- Use the shared secret header in production to prevent open relay.

Notes
-----

- If LF_PROXY_SECRET is set, browser components that cannot set custom headers may not be able to call the proxy directly. For local/dev, leave LF_PROXY_SECRET unset, or place the proxy behind an authenticated origin that injects the header server‑side.
