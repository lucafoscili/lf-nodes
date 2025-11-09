import logging
import json
import asyncio
from aiohttp import web
from typing import Optional

LOG = logging.getLogger(__name__)

from ..utils.serialize import serialize_job

# region Parse body
async def parse_json_body(request, expected_type=dict, allow_empty=False):
    """Parse JSON body from an aiohttp request and validate its type.

    Returns a tuple (body, error_response).
    - On success: (body, None)
    - On failure: (None, web.Response) where the response contains the error
      payload and an appropriate status code.

    This mirrors the existing controller behaviour where invalid JSON results
    in {"detail": "invalid_json"} (400) and a wrong payload shape results
    in {"detail": "invalid_payload"} (400).
    """
    try:
        body = await request.json()
    except Exception:
        LOG.debug("parse_json_body: failed to parse JSON", exc_info=True)
        return None, web.json_response({"detail": "invalid_json"}, status=400)

    # Explicit None handling: allow_empty controls whether None is acceptable
    if body is None:
        if allow_empty:
            return None, None
        return None, web.json_response({"detail": "invalid_payload"}, status=400)

    if expected_type is not None and not isinstance(body, expected_type):
        return None, web.json_response({"detail": "invalid_payload"}, status=400)

    return body, None
# endregion

# region Get owner
async def get_owner_from_request(request) -> str | None:
    """Extract the subject (email or provider sub) from the request and derive
    an opaque owner id (SHA256 hex digest).

    Extraction tries, in order:
    - request._cache['google_oauth_email'] or request._cache['email'] when
      _cache is a dict
    - request.get('google_oauth_email')
    - request.google_oauth_email attribute
    """
    try:
        subj = None
        try:
            cache = getattr(request, "_cache", None)
            if isinstance(cache, dict):
                subj = cache.get("google_oauth_email") or cache.get("email")
        except Exception:
            subj = None

        if subj is None:
            try:
                subj = request.get("google_oauth_email", None)
            except Exception:
                subj = None
            if subj is None:
                subj = getattr(request, "google_oauth_email", None)

        if subj is not None and not isinstance(subj, str):
            try:
                subj = str(subj)
            except Exception:
                subj = None

        if not subj:
            return None

        import hashlib

        owner = hashlib.sha256(subj.encode("utf-8")).hexdigest()
        return owner
    except Exception:
        LOG.debug("get_owner_from_request: failed to derive owner", exc_info=True)
        return None
# endregion

# region Session cookie
def create_and_set_session_cookie(resp, request, email, create_session_fn=None):
    """Create a server session and set the LF_SESSION cookie on the response.

    Parameters:
    - resp: object providing set_cookie(name, value, ...) and del_cookie(name, ...)
    - request: aiohttp Request-like object used to determine 'secure'
    - email: str email to create session for
    - create_session_fn: optional callable(email) -> (session_id, expires_at).
                         If None, the function will import the local
                         workflow_runner auth_service and call
                         create_server_session(email).

    Returns: (session_id, expires_at) on success, (None, None) on failure.
    """
    try:
        if create_session_fn is None:
            # import lazily to avoid import-time side-effects in tests
            from ..services.auth_service import create_server_session, _SESSION_TTL

            create_session_fn = create_server_session
            session_ttl = _SESSION_TTL
        else:
            # If a custom create_session_fn is provided, we can't know _SESSION_TTL
            # so allow callers/tests to ignore TTL checks; use None as placeholder.
            session_ttl = None

        session_id, expires_at = create_session_fn(email)
    except Exception:
        LOG.exception("Failed to create session in store")
        return None, None

    try:
        secure_flag = getattr(request, "secure", None)
        if secure_flag is None:
            secure_flag = (getattr(request, "scheme", "") == "https")

        # Use max_age when available (session_ttl may be None during tests)
        if session_ttl is not None:
            resp.set_cookie(
                "LF_SESSION",
                session_id,
                max_age=session_ttl,
                httponly=True,
                path="/api/lf-nodes/",
                samesite="Lax",
                secure=bool(secure_flag),
            )
        else:
            resp.set_cookie(
                "LF_SESSION",
                session_id,
                httponly=True,
                path="/api/lf-nodes/",
                samesite="Lax",
                secure=bool(secure_flag),
            )

    # Set LF_SESSION cookie for the created session.
    except Exception:
        LOG.exception("Failed to set session cookie")
        return session_id, expires_at

    return session_id, expires_at
# endregion

# region SSE
async def write_sse_event(resp, event: dict) -> bool:
    """Write an event to an aiohttp StreamResponse in SSE format.

    Returns True if the event was sent (or a non-fatal error occurred),
    False if the client disconnected (ConnectionResetError or CancelledError).
    """
    try:
        event_type = "queue" if event.get("type") == "queue_status" else "run"
        event_id = event.get("id") or (f"{event.get('run_id')}:{event.get('seq', 0)}")
        data = json.dumps(event)
        payload = f"id: {event_id}\nevent: {event_type}\ndata: {data}\n\n".encode("utf-8")
        await resp.write(payload)
        # drain can raise CancelledError when connection is closed
        try:
            await resp.drain()
        except asyncio.CancelledError:
            return False
        return True
    except (ConnectionResetError, asyncio.CancelledError):
        # client disconnected while writing
        return False
    except Exception:
        LOG.exception("Failed to write SSE event")
        return True

def parse_last_event_id(header: Optional[str]) -> Optional[tuple[str, int]]:
    """Parse Last-Event-ID header into (run_id, seq) or return None.

    Accepts values like "run-123:45" or just "run-123" (seq defaults to 0).
    Returns None for malformed inputs or non-string headers.
    """
    try:
        if not header or not isinstance(header, str):
            return None
        header = header.strip()
        if not header:
            return None
        parts = header.split(":", 1)
        if len(parts) == 1:
            return (parts[0], 0)
        run_id = parts[0]
        seq_raw = parts[1]
        try:
            seq = int(seq_raw)
        except Exception:
            return None
        return (run_id, seq)
    except Exception:
        LOG.debug("parse_last_event_id: failed to parse header", exc_info=True)
        return None
# endregion