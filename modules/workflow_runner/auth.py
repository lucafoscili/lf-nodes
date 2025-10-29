import logging
import os
import time as _time
import uuid
from pathlib import Path
from typing import Optional

from aiohttp import web

from .google_oauth import verify_id_token_with_google, load_allowed_users_from_file

# Google OAuth opt-in configuration (read at import)
_ENABLE_GOOGLE_OAUTH = os.environ.get("ENABLE_GOOGLE_OAUTH", "").lower() in ("1", "true", "yes")
_ALLOWED_USERS_FILE = os.environ.get("ALLOWED_USERS_FILE", "")
_ALLOWED_USERS_ENV = os.environ.get("ALLOWED_USERS", "")
# strip surrounding quotes if present and split on commas
_GOOGLE_CLIENT_IDS = [s.strip().strip('"\'"') for s in os.environ.get("GOOGLE_CLIENT_IDS", "").split(",") if s.strip()]

# Simple in-memory token cache: id_token -> (email, expires_at)
_TOKEN_CACHE: dict[str, tuple[str, float]] = {}
_TOKEN_CACHE_TTL = int(os.environ.get("GOOGLE_IDTOKEN_CACHE_SECONDS", "300"))

# Require explicit allowlist? If true and no allowed users are configured, logins will be denied.
_REQUIRE_ALLOWED_USERS = os.environ.get("REQUIRE_ALLOWED_USERS", "1").lower() in ("1", "true", "yes")

# Server-side sessions: session_id -> (email, expires_at)
_SESSION_STORE: dict[str, tuple[str, float]] = {}
_SESSION_TTL = int(os.environ.get("SESSION_TTL_SECONDS", str(_TOKEN_CACHE_TTL)))
# Enable verbose debug for the workflow-runner verify handler
_WF_DEBUG = os.environ.get("WORKFLOW_RUNNER_DEBUG", "0").lower() in ("1", "true", "yes")


def _load_allowed_users() -> set:
    users = set()
    if _ALLOWED_USERS_FILE:
        users.update(load_allowed_users_from_file(_ALLOWED_USERS_FILE))
    if _ALLOWED_USERS_ENV:
        users.update(u.strip().lower() for u in _ALLOWED_USERS_ENV.split(",") if u.strip())
    return users


_ALLOWED_USERS = _load_allowed_users()


async def _verify_token_and_email(id_token: str) -> tuple[bool, Optional[str]]:
    """Verify token (possibly cached) and ensure email is allowed.

    Returns (True, email) on success, (False, None) otherwise.
    """
    if not id_token:
        return False, None

    # check cache
    now = _time.time()
    cached = _TOKEN_CACHE.get(id_token)
    if cached and cached[1] > now:
        return True, cached[0]

    claims = await verify_id_token_with_google(id_token, expected_audiences=_GOOGLE_CLIENT_IDS or None)
    if not claims:
        return False, None

    email = (claims.get("email") or "").lower()
    return True, email


def _extract_token_from_request(request: web.Request) -> Optional[str]:
    # Authorization header
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()
    # fallback: cookie LF_SESSION (server-side session id)
    cookie = request.cookies.get("LF_SESSION")
    if cookie:
        return cookie
    return None


def _cleanup_expired_sessions() -> None:
    now = _time.time()
    to_delete = [s for s, v in _SESSION_STORE.items() if v[1] <= now]
    for s in to_delete:
        _SESSION_STORE.pop(s, None)


async def _verify_session(session_id: str) -> tuple[bool, Optional[str]]:
    if not session_id:
        return False, None
    _cleanup_expired_sessions()
    now = _time.time()
    val = _SESSION_STORE.get(session_id)
    if not val:
        return False, None
    email, exp = val
    if exp <= now:
        try:
            _SESSION_STORE.pop(session_id, None)
        except Exception:
            pass
        return False, None
    return True, email


async def _require_auth(request: web.Request) -> Optional[web.Response]:
    if not _ENABLE_GOOGLE_OAUTH:
        return None
    token = _extract_token_from_request(request)
    if not token:
        logging.info("Auth missing for request %s %s", request.method, request.path)
        return web.json_response({"detail": "missing_bearer_token"}, status=401)
    # First, accept server-side sessions (LF_SESSION cookie)
    ok, email = await _verify_session(token)
    if not ok:
        # Fallback: treat token as an id_token and verify with Google
        ok, email = await _verify_token_and_email(token)
    if not ok:
        logging.info("Auth failed for request %s %s (invalid token or forbidden)", request.method, request.path)
        return web.json_response({"detail": "invalid_token_or_forbidden"}, status=401)
    # attach email to request for downstream use
    try:
        request['google_oauth_email'] = email
    except Exception:
        setattr(request, 'google_oauth_email', email)
    logging.info("Auth accepted for %s as %s on %s %s", email, request.remote, request.method, request.path)
    return None


def create_server_session(email: str) -> tuple[str, float]:
    """Create a new server-side session and return (session_id, expires_at)."""
    session_id = uuid.uuid4().hex
    expires_at = _time.time() + _SESSION_TTL
    _SESSION_STORE[session_id] = (email, expires_at)
    return session_id, expires_at
