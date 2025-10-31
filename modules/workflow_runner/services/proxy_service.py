import json
import logging
import os
from time import time
from urllib.parse import urlsplit
from typing import Any, Dict, Optional, Tuple

from aiohttp import web

LOG = logging.getLogger(__name__)

# region Proxy Service Config
SERVICES: Dict[str, Dict[str, Any]] = {
    "kobold": {
        "base_env": "KOBOLDCPP_BASE",
        "default_path": "/api/v1/generate",
        "allowed_paths": [
            "/api/v1/generate",
            "/api/v1/generate/stream",
            "/v1/chat/completions",
            "/v1/chat/completions/stream",
        ],
        "map_openai_to_generate": False,
    "forward_raw_sse": True,
        "timeout": 60,
    },
    "gemini": {
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "api_key_env": "GEMINI_API_KEY",
        "api_key_header": "X-goog-api-key",
        "default_model": "gemini-2.0-flash",
        "timeout": 60,
    },
    "openai": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "api_key_env": "OPENAI_API_KEY",
        "api_key_header": "Authorization",
        "default_model": "gpt-4o",
        "timeout": 60,
    },
}

def _read_secret(env_name: str, file_env_name: Optional[str] = None) -> Optional[str]:
    val = os.environ.get(env_name)
    if val:
        return val

    if file_env_name:
        path = None
        try:
            from ..config import get_settings

            _settings_local = get_settings()
            if hasattr(_settings_local, file_env_name):
                path = getattr(_settings_local, file_env_name) or None
        except Exception:
            path = None

        if not path:
            path = os.environ.get(file_env_name)

        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    return fh.read().strip()
            except Exception:
                LOG.exception("Failed reading secret file %s", path)

    return None

PROXY_SECRET = _read_secret("LF_PROXY_SECRET", "LF_PROXY_SECRET_FILE") or _read_secret("GEMINI_PROXY_SECRET", "GEMINI_PROXY_SECRET_FILE")
PROXY_SECRET_HEADER = "X-LF-Proxy-Secret"
_RATE_LIMIT_STORE: dict[tuple[str, str], dict] = {}

from ..config import get_settings

_settings = get_settings()

DEFAULT_RATE_LIMIT = {
    "requests": int(_settings.PROXY_RATE_LIMIT_REQUESTS or 60),
    "window_seconds": int(_settings.PROXY_RATE_LIMIT_WINDOW_SECONDS or 60),
}
# endregion

# region Helpers
def _get_client_id(request: web.Request) -> str:
    try:
        if getattr(request, "remote", None):
            return str(request.remote)
        transport = request.transport
        if transport is not None:
            peer = transport.get_extra_info("peername")
            if peer and isinstance(peer, (list, tuple)) and len(peer) >= 1:
                return str(peer[0])
    except Exception:
        pass
    return "unknown"

def _check_rate_limit(client_id: str, service: str, cfg: dict) -> Tuple[bool, int]:
    svc_limit = cfg.get("rate_limit") if cfg else None
    if svc_limit is None:
        limit = DEFAULT_RATE_LIMIT
    else:
        try:
            limit = {
                "requests": int(svc_limit.get("requests", DEFAULT_RATE_LIMIT["requests"])),
                "window_seconds": int(svc_limit.get("window_seconds", DEFAULT_RATE_LIMIT["window_seconds"])),
            }
        except Exception:
            limit = DEFAULT_RATE_LIMIT

    if limit.get("requests", 0) <= 0:
        return True, 0

    key = (client_id, service)
    now = time()
    entry = _RATE_LIMIT_STORE.get(key)
    if not entry or (now - entry.get("start", 0)) >= limit["window_seconds"]:
        _RATE_LIMIT_STORE[key] = {"count": 1, "start": now}
        return True, 0

    if entry["count"] < limit["requests"]:
        entry["count"] += 1
        return True, 0

    retry_after = int(limit["window_seconds"] - (now - entry.get("start", 0)))
    return False, retry_after

def _build_body_for_openai(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a forward_body that preserves the OpenAI chat shape (messages, model, stream, etc.).

    We keep all keys except an explicit proxy `path` key so the upstream chat endpoint
    receives the original OpenAI-style payload.
    """
    return {k: v for k, v in body.items() if k != "path"}

def _build_body_for_legacy(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a legacy 'generate' style body from an OpenAI chat `messages` list.

    Mirrors previous inlined behavior: flattens messages into a single `prompt` string,
    maps common parameters (max_tokens->max_length, temperature, top_p, etc.), and
    sets sensible defaults for stop sequences.
    """
    messages = body.get("messages", [])

    def _extract_content(msg: Any) -> str:
        try:
            c = msg.get("content")
            if isinstance(c, list):
                return " ".join(str(p.get("text", "")) for p in c if isinstance(p, dict))
            return str(c)
        except Exception:
            return ""

    system_parts: list[str] = []
    dialogue_lines: list[str] = []
    for m in messages:
        role = (m.get("role") if isinstance(m, dict) else "").strip() or "user"
        content = _extract_content(m).strip()
        if not content:
            continue
        if role == "system":
            system_parts.append(content)
        elif role == "assistant":
            dialogue_lines.append(f"Assistant: {content}")
        else:
            dialogue_lines.append(f"User: {content}")

    prompt_lines: list[str] = []
    if system_parts:
        prompt_lines.append(f"System: {' '.join(system_parts)}")
        prompt_lines.append("")
    prompt_lines.extend(dialogue_lines)
    prompt_lines.append("Assistant:")
    prompt = "\n".join(prompt_lines).strip()

    forward_body: Dict[str, Any] = {"prompt": prompt}

    if isinstance(body.get("max_tokens"), int):
        forward_body["max_length"] = body.get("max_tokens")
    if isinstance(body.get("temperature"), (int, float)):
        forward_body["temperature"] = float(body.get("temperature"))
    if body.get("seed") is not None:
        forward_body["seed"] = body.get("seed")
    if isinstance(body.get("top_p"), (int, float)):
        forward_body["top_p"] = float(body.get("top_p"))
    if isinstance(body.get("top_k"), int):
        forward_body["top_k"] = int(body.get("top_k"))
    if isinstance(body.get("min_p"), (int, float)):
        forward_body["min_p"] = float(body.get("min_p"))
    if isinstance(body.get("stream"), bool):
        forward_body["stream"] = body.get("stream")
    if isinstance(body.get("repetition_penalty"), (int, float)):
        forward_body["repetition_penalty"] = float(body.get("repetition_penalty"))

    stop = body.get("stop")
    if stop is not None:
        forward_body["stop_sequence"] = stop
    else:
        forward_body["stop_sequence"] = ["\nUser:", "\nSystem:"]

    for extra_key in (
        "mirostat",
        "mirostat_eta",
        "mirostat_tau",
        "typical_p",
        "tfs",
        "sampler",
        "sampler_order",
        "use_default_prompt_template",
    ):
        if extra_key in body:
            forward_body[extra_key] = body[extra_key]

    return forward_body

def _build_upstream_and_headers(cfg: Dict[str, Any], body: Dict[str, Any], proxypath: Optional[str]) -> Tuple[str, Dict[str, str], int, Dict[str, Any]]:
    headers: Dict[str, str] = {}
    timeout = int(cfg.get("timeout", 60))

    if "endpoint" in cfg:
        if proxypath:
            parts = urlsplit(cfg["endpoint"])
            base = f"{parts.scheme}://{parts.netloc}"
            upstream = base.rstrip("/") + "/" + proxypath.lstrip("/")
        else:
            model = body.get("model") or cfg.get("default_model")
            upstream = cfg["endpoint"].format(model=model)

        api_env = cfg.get("api_key_env")
        if api_env:
            key = _read_secret(api_env, f"{api_env}_FILE")
            if key:
                header_name = cfg.get("api_key_header")
                if header_name == "Authorization":
                    headers[header_name] = f"Bearer {key}"
                else:
                    headers[header_name] = key
        forward_body = body
    else:
        base_env = cfg.get("base_env")
        base_url = _read_secret(base_env, f"{base_env}_FILE") if base_env else None
        if not base_url:
            raise web.HTTPInternalServerError(text=json.dumps({"detail": "proxy_not_configured", "error": f"Missing base URL: set {base_env}"}))

        path = proxypath or body.get("path") or cfg.get("default_path", "/")
        if not isinstance(path, str):
            raise web.HTTPBadRequest(text=json.dumps({"detail": "invalid_path"}))
        if not path.startswith('/'):
            path = "/" + path

        allowed = cfg.get("allowed_paths")
        mapped_for_openai_chat = False
        stream = body.get("stream")
        map_openai = bool(cfg.get("map_openai_to_generate", True))
        # initialize decision flag early (clear and explicit for SoC/DRY)
        use_legacy = False
        if path.lstrip("/").startswith("v1/chat/completions"):
            mapped_for_openai_chat = True
            use_legacy = isinstance(body.get("prompt"), str) or (map_openai and isinstance(body.get("messages"), list))
            if use_legacy:
                if bool(stream):
                    path = "/api/v1/generate/stream"
                else:
                    path = "/api/v1/generate"
            else:
                path = "/v1/chat/completions"

        if isinstance(allowed, list) and path not in allowed:
            raise web.HTTPBadRequest(text=json.dumps({"detail": "path_not_allowed", "path": path}))

        upstream = base_url.rstrip("/") + path

        if mapped_for_openai_chat:
            if use_legacy:
                forward_body = _build_body_for_legacy(body)
            else:
                forward_body = _build_body_for_openai(body)

    return upstream, headers, timeout, forward_body
# endregion

__all__ = [
    "SERVICES",
    "_read_secret",
    "PROXY_SECRET",
    "PROXY_SECRET_HEADER",
    "_get_client_id",
    "_check_rate_limit",
    "_build_upstream_and_headers",
]
