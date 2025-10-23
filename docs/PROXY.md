Proxy README
=============

This document describes the simple multi-service proxy used by the workflow-runner.

Secrets
-------

Prefer one secret per file and set the corresponding *_FILE environment variable. Example:

GEMINI_API_KEY_FILE=/run/secrets/gemini
LF_PROXY_SECRET_FILE=/run/secrets/lf_proxy_secret

The proxy supports the following environment variables (each also supports a corresponding *_FILE var):

- GEMINI_API_KEY (or GEMINI_API_KEY_FILE)
- OPENAI_API_KEY (or OPENAI_API_KEY_FILE)
- LF_PROXY_SECRET (or LF_PROXY_SECRET_FILE)

Local development
-----------------

For local convenience you can place a `.env` file in this folder and set `DEV_ENV=1` before starting the server. The server will load `.env` only when `DEV_ENV` is set to avoid accidental production usage.

Example `.env` (do NOT commit this file):

```plaintext
# Example .env for local development (DO NOT commit secrets)
# This example shows two options: set the key directly (quick/dev) OR point
# to a secret file using the *_FILE convention (recommended).
# Set DEV_ENV=1 to enable loading this file at startup
DEV_ENV=1

# Option A: Direct keys (development convenience - do NOT commit real keys)
GEMINI_API_KEY=ya29.example_key
LF_PROXY_SECRET=replace_with_secret
OPENAI_API_KEY=sk.example_openai_key

# Option B: Preferred for local/CI/container use: point to per-secret files
# Create files under C:\my_secret_secrets (one file per secret) and point env vars to them.
GEMINI_API_KEY_FILE=C:\my_secret_secrets\gemini.txt
LF_PROXY_SECRET_FILE=C:\my_secret_secrets\lf_proxy_secret.txt
OPENAI_API_KEY_FILE=C:\my_secret_secrets\openai.txt
```

Testing
-------

Use the PowerShell `Invoke-RestMethod` examples in the main README to call `http://localhost:8080/api/proxy/gemini` with header `X-LF-Proxy-Secret`.

Security
--------

Use per-secret files and set file-level permissions so only the service account can read them.

For production, prefer managed secret providers and mount secrets as readonly files.
