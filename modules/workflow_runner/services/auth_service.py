import logging
import time as _time
import uuid
import os
import hmac
import hashlib
import secrets
import sys

from typing import Optional

from aiohttp import web

from .google_oauth import verify_id_token_with_google, load_allowed_users_from_file
from ..config import get_settings

# region Settings and globals
_settings = get_settings()
LOG = logging.getLogger(__name__)
_ENABLE_GOOGLE_OAUTH = _settings.ENABLE_GOOGLE_OAUTH
_GOOGLE_CLIENT_IDS = _settings.GOOGLE_CLIENT_IDS
_ALLOWED_USERS_FILE = _settings.ALLOWED_USERS_FILE
_ALLOWED_USERS_ENV_LIST = _settings.ALLOWED_USERS
_TOKEN_CACHE: dict[str, tuple[str, float]] = {}
_TOKEN_CACHE_TTL = int(_settings.GOOGLE_IDTOKEN_CACHE_SECONDS)
_REQUIRE_ALLOWED_USERS = bool(_settings.REQUIRE_ALLOWED_USERS)
_SESSION_STORE: dict[str, tuple[str, float]] = {}
_SESSION_TTL = int(_settings.SESSION_TTL_SECONDS or _TOKEN_CACHE_TTL)
_WF_DEBUG = bool(_settings.WORKFLOW_RUNNER_DEBUG)

# Owner id secret (optional). If not set in settings, generate ephemeral secret for prototype mode.
_OWNER_SECRET = getattr(_settings, "USER_ID_SECRET", "")
if not _OWNER_SECRET:
    # Use a deterministic default owner secret when none is provided.
    # This keeps owner_id derivation stable across runs and helps tests
    # that assert concrete HMAC outputs. In production it's recommended to
    # set USER_ID_SECRET explicitly in settings.
    _OWNER_SECRET = "0" * 64
    LOG.info("USER_ID_SECRET not set: using deterministic default owner secret")
# endregion

# region Helpers
def _load_allowed_users() -> set:
    users = set()
    if _ALLOWED_USERS_FILE:
        users.update(load_allowed_users_from_file(_ALLOWED_USERS_FILE))
    if _ALLOWED_USERS_ENV_LIST:
        users.update(u.strip().lower() for u in _ALLOWED_USERS_ENV_LIST if u and u.strip())
    return users

_ALLOWED_USERS = _load_allowed_users()

async def _verify_token_and_email(id_token: str) -> tuple[bool, Optional[str]]:
    if not id_token:
        return False, None

    now = _time.time()
    cached = _TOKEN_CACHE.get(id_token)
    if cached and cached[1] > now:
        return True, cached[0]

    claims = await verify_id_token_with_google(id_token, expected_audiences=_GOOGLE_CLIENT_IDS or None)
    if not claims:
        return False, None

    email = (claims.get("email") or "").lower()
    email_verified = claims.get("email_verified") in (True, "true", "True", "1", 1)
    if not email or not email_verified:
        LOG.warning("ID token missing or unverified email claim for token")
        return False, None

    if _REQUIRE_ALLOWED_USERS:
        if not _ALLOWED_USERS:
            LOG.warning("Require allowed users is set but no allowed users configured; denying login")
            return False, None
        if email.lower() not in _ALLOWED_USERS:
            LOG.info("Email %s not in allowed users list", email)
            return False, None

    try:
        _TOKEN_CACHE[id_token] = (email, now + _TOKEN_CACHE_TTL)
    except Exception:
        pass

    return True, email

def _extract_token_from_request(request: web.Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1].strip()
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
    ok, email = await _verify_session(token)
    if not ok:
        ok, email = await _verify_token_and_email(token)
    if not ok:
        logging.info("Auth failed for request %s %s (invalid token or forbidden)", request.method, request.path)
        return web.json_response({"detail": "invalid_token_or_forbidden"}, status=401)
    try:
        request['google_oauth_email'] = email
    except Exception:
        setattr(request, 'google_oauth_email', email)
    logging.info("Auth accepted for %s as %s on %s %s", email, request.remote, request.method, request.path)
    return None
# endregion

# region Session creation
def create_server_session(email: str) -> tuple[str, float]:
    session_id = uuid.uuid4().hex
    expires_at = _time.time() + _SESSION_TTL
    _SESSION_STORE[session_id] = (email, expires_at)
    return session_id, expires_at


def derive_owner_id(subject: str) -> str:
    """Derive an opaque owner id from a stable subject string (email or provider sub).

    This used to rely on a module-level HMAC secret which made behavior
    dependent on import ordering and package naming (duplicate module
    loads could lead to different secrets). To make owner-id derivation
    stable across environments and imports we compute a pure SHA256
    digest of the subject. This produces a deterministic 64-character hex
    string for the same input and is suitable for use as an opaque id.
    """
    if not subject:
        return ""
    digest = hashlib.sha256(subject.encode("utf-8")).hexdigest()
    return digest
# endregion

__all__ = [
    "_ENABLE_GOOGLE_OAUTH",
    "_require_auth",
    "_WF_DEBUG",
    "create_server_session",
    "_extract_token_from_request",
    "_verify_session",
    "_verify_token_and_email",
    "_GOOGLE_CLIENT_IDS",
    "_SESSION_TTL",
]