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

# region Extract data
def extract_base64_data_from_result(result: dict) -> Optional[tuple[str, str]]:
    """
    Extract base64 encoded image/SVG data from workflow result.

    Args:
        result: The job result dict containing workflow execution data

    Returns:
        Tuple of (mime_type, base64_data) or None if no suitable data found
        - mime_type: "image/png", "image/jpeg", or "image/svg+xml"
        - base64_data: The base64 encoded data string (without data URL prefix)
    """
    import base64
    import folder_paths
    import os
    from PIL import Image
    import io

    try:
        if not result or not isinstance(result, dict):
            return None

        # The result structure is: {"http_status": int, "body": dict}
        body = result.get("body", {})
        if not isinstance(body, dict):
            return None

        # Look for history outputs in the response body
        history = body.get("payload", {}).get("history", {})
        outputs = history.get("outputs", {})

        svg_data = None  # Initialize for direct SVG content

        if not outputs and not svg_data:
            # Fallback for LF workflows: look for recently created files in output directory
            # This handles cases where ComfyUI history doesn't contain outputs for custom nodes
            try:
                output_dir = folder_paths.get_directory_by_type("output")
                if output_dir and os.path.exists(output_dir):
                    # Look for PNG, JPG, or SVG files (most common for LF workflows)
                    image_files = []
                    for ext in ['.png', '.jpg', '.jpeg', '.svg']:
                        image_files.extend([f for f in os.listdir(output_dir) if f.lower().endswith(ext)])
                    
                    if image_files:
                        # Sort by modification time, take the most recent
                        image_files.sort(key=lambda f: os.path.getmtime(os.path.join(output_dir, f)), reverse=True)
                        image_filename = image_files[0]
                        img_type = "output"
                        subfolder = ""
                        
                        # Determine MIME type from file extension
                        if image_filename.lower().endswith('.svg'):
                            mime_type = "image/svg+xml"
                        elif image_filename.lower().endswith('.jpg') or image_filename.lower().endswith('.jpeg'):
                            mime_type = "image/jpeg"
                        else:  # PNG and default
                            mime_type = "image/png"
                    else:
                        return None
                else:
                    return None
            except Exception as fallback_exc:
                LOG.warning(f"Fallback file search failed: {fallback_exc}")
                return None
        else:
            preferred_output = body.get("payload", {}).get("preferred_output")
            target_output = None

            if preferred_output and preferred_output in outputs:
                target_output = outputs[preferred_output]
            else:
                # Find any output with images (either standard ComfyUI format or LF format)
                for output_name, output_data in outputs.items():
                    if isinstance(output_data, dict):
                        # Check for standard ComfyUI images
                        if output_data.get("images") or output_data.get("lf_images"):
                            target_output = output_data
                            break
                        # Check for LF custom format
                        if output_data.get("lf_output"):
                            lf_output = output_data.get("lf_output")
                            if isinstance(lf_output, list) and lf_output and isinstance(lf_output[0], dict):
                                # Check for file_names (existing), slot_map (direct SVG), or svg field
                                first_lf = lf_output[0]
                                if (first_lf.get("file_names") or 
                                    first_lf.get("slot_map") or 
                                    first_lf.get("svg")):
                                    target_output = output_data
                                    break

            if not target_output:
                return None

            # Extract images/SVGs from the output
            image_filename = None
            mime_type = "image/png"  # default
            svg_data = None  # For direct SVG content

            # Try standard ComfyUI format first
            images = target_output.get("images") or target_output.get("lf_images", [])
            if images and isinstance(images, list) and images:
                first_image = images[0]
                if isinstance(first_image, dict):
                    filename = first_image.get("filename")
                    subfolder = first_image.get("subfolder", "")
                    img_type = first_image.get("type", "output")
                    image_filename = filename
                    img_type = img_type
                    subfolder = subfolder
                    
                    # Determine MIME type from filename
                    if filename and filename.lower().endswith('.svg'):
                        mime_type = "image/svg+xml"
                    elif filename and (filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')):
                        mime_type = "image/jpeg"
                    else:
                        mime_type = "image/png"

            # Check for LF SVG data in lf_output (direct content, no file needed)
            if not image_filename:
                lf_output = target_output.get("lf_output")
                if isinstance(lf_output, list) and lf_output:
                    first_lf = lf_output[0]
                    if isinstance(first_lf, dict):
                        # Try slot_map first (processed SVG blocks)
                        slot_map = first_lf.get("slot_map")
                        if isinstance(slot_map, dict):
                            # Find first SVG in slot_map
                            for filename, content in slot_map.items():
                                if isinstance(filename, str) and filename.lower().endswith('.svg'):
                                    if isinstance(content, str):
                                        svg_data = content
                                        mime_type = "image/svg+xml"
                                        break
                        
                        # If no SVG in slot_map, try the plain svg field
                        if not svg_data:
                            svg_content = first_lf.get("svg")
                            if isinstance(svg_content, str):
                                svg_data = svg_content
                                mime_type = "image/svg+xml"

            # Try LF custom format (file-based)
            if not image_filename and not svg_data:
                lf_output = target_output.get("lf_output")
                if isinstance(lf_output, list) and lf_output:
                    first_lf = lf_output[0]
                    if isinstance(first_lf, dict):
                        file_names = first_lf.get("file_names")
                        if isinstance(file_names, list) and file_names:
                            image_filename = file_names[0]
                            img_type = "output"
                            subfolder = ""
                            
                            # Determine MIME type from filename
                            if image_filename.lower().endswith('.svg'):
                                mime_type = "image/svg+xml"
                            elif image_filename.lower().endswith('.jpg') or image_filename.lower().endswith('.jpeg'):
                                mime_type = "image/jpeg"
                            else:
                                mime_type = "image/png"

            if not image_filename and not svg_data:
                return None

        # If we have direct SVG data, skip file operations
        if svg_data:
            pass  # Will be handled in the encoding section below
        else:
            # Build the full path
            output_dir = folder_paths.get_directory_by_type(img_type)
            if not output_dir:
                return None

            if subfolder:
                full_path = os.path.join(output_dir, subfolder, image_filename)
            else:
                full_path = os.path.join(output_dir, image_filename)

            # Check if file exists
            if not os.path.exists(full_path):
                LOG.warning(f"Image file not found: {full_path}")
                return None

        # Read and encode the file or direct SVG data
        try:
            if svg_data:
                # Direct SVG content from lf_output - need to unescape JSON and encode
                try:
                    # First unescape any JSON escaping (like \u003C for <)
                    unescaped_svg = svg_data.encode().decode('unicode_escape')
                except Exception:
                    # If unescaping fails, use as-is
                    unescaped_svg = svg_data
                
                # Encode to UTF-8 bytes then base64
                base64_data = base64.b64encode(unescaped_svg.encode('utf-8')).decode('utf-8')
            elif mime_type == "image/svg+xml":
                # For SVG files, read as text and encode
                with open(full_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                base64_data = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            else:
                # For image files, use PIL to process and convert to PNG
                with Image.open(full_path) as img:
                    # Convert to RGB if necessary (for JPEG, etc.)
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')

                    # Save to bytes buffer as PNG
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)

                    # Encode to base64
                    image_data = buffer.getvalue()
                    base64_data = base64.b64encode(image_data).decode('utf-8')

            return (mime_type, base64_data)

        except Exception as img_exc:
            LOG.exception(f"Failed to process {'SVG data' if svg_data else f'file {full_path}'}")
            return None

    except Exception as exc:
        LOG.exception("Failed to extract base64 data from result")
        return None
# endregion