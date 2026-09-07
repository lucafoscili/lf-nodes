"""Resolve the sole loaded LM Studio LLM for native chat callers."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests

from ...constants import HEADERS
from .resolve_url import local_proxy_request_options, resolve_api_url


_NATIVE_CHAT_PATH = "/api/v1/chat"
_NATIVE_MODELS_PATH = "/api/v1/models"
_MAX_ERROR_CHARS = 500


def lm_studio_models_url(chat_url: str) -> str:
    """Return the native model-list endpoint paired with a chat endpoint."""

    parsed = urlsplit(chat_url)
    chat_path = parsed.path.rstrip("/")
    if not chat_path.endswith(_NATIVE_CHAT_PATH):
        raise ValueError(
            "Automatic model discovery requires an LM Studio /api/v1/chat endpoint."
        )
    models_path = (
        f"{chat_path[: -len(_NATIVE_CHAT_PATH)]}{_NATIVE_MODELS_PATH}"
    )
    return urlunsplit(
        (parsed.scheme, parsed.netloc, models_path, parsed.query, parsed.fragment)
    )


def select_loaded_lm_studio_llm_id(data: Any) -> str:
    """Select exactly one loaded LLM instance from a native model-list response."""

    malformed = (
        "LM Studio model lookup returned malformed JSON; expected the documented "
        "/api/v1/models response with models and loaded_instances."
    )
    if not isinstance(data, dict) or not isinstance(data.get("models"), list):
        raise ValueError(malformed)

    loaded_ids: list[str] = []
    for model in data["models"]:
        if not isinstance(model, dict):
            raise ValueError(malformed)
        model_type = model.get("type")
        loaded_instances = model.get("loaded_instances")
        if model_type not in ("llm", "embedding") or not isinstance(
            loaded_instances,
            list,
        ):
            raise ValueError(malformed)
        if model_type != "llm":
            continue
        for instance in loaded_instances:
            if not isinstance(instance, dict):
                raise ValueError(malformed)
            instance_id = instance.get("id")
            if not isinstance(instance_id, str) or not instance_id.strip():
                raise ValueError(malformed)
            loaded_ids.append(instance_id.strip())

    if not loaded_ids:
        raise ValueError(
            "Blank model could not be resolved because LM Studio reports no loaded "
            "LLM instances. Load exactly one LLM or specify model."
        )
    if len(loaded_ids) != 1:
        raise ValueError(
            "Blank model is ambiguous because LM Studio reports multiple loaded "
            f"LLM instances ({len(loaded_ids)}). Specify model."
        )
    return loaded_ids[0]


def _response_error_detail(response: Any) -> str | None:
    try:
        payload = response.json()
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    error = payload.get("error")
    if isinstance(error, dict):
        candidate = error.get("message")
    elif isinstance(error, str):
        candidate = error
    else:
        candidate = payload.get("detail") or payload.get("message")
    if not isinstance(candidate, str):
        return None
    detail = " ".join(candidate.split())
    if not detail:
        return None
    if len(detail) > _MAX_ERROR_CHARS:
        return f"{detail[: _MAX_ERROR_CHARS - 3]}..."
    return detail


def resolve_loaded_lm_studio_llm(chat_url: str, timeout: int) -> str:
    """Query LM Studio and return its sole loaded LLM instance identifier."""

    models_url = lm_studio_models_url(chat_url)
    try:
        response = requests.get(
            resolve_api_url(models_url),
            timeout=timeout,
            **local_proxy_request_options(models_url, HEADERS),
        )
    except requests.RequestException as error:
        raise ValueError(
            "LM Studio model lookup failed. Check the endpoint and whether the "
            "local model server is running."
        ) from error

    status_code = getattr(response, "status_code", None)
    if status_code != 200:
        upstream_detail = _response_error_detail(response)
        provider_message = (
            f" Provider said: {upstream_detail}" if upstream_detail else ""
        )
        raise ValueError(
            "LM Studio model lookup failed with HTTP status "
            f"{status_code}.{provider_message}"
        )

    try:
        response_data = response.json()
    except ValueError as error:
        raise ValueError(
            "LM Studio model lookup response was not valid JSON."
        ) from error
    return select_loaded_lm_studio_llm_id(response_data)
