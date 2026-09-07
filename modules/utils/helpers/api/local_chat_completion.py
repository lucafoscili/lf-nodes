"""Headless transport for local OpenAI-compatible and LM Studio chat APIs."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any
from urllib.parse import urlsplit

import requests

from ...constants import HEADERS
from .build_multimodal_content import build_openai_multimodal_content
from .handle_response import require_response_text
from .lm_studio_models import resolve_loaded_lm_studio_llm
from .parse_openai_response import parse_openai_response
from .resolve_url import local_proxy_request_options, resolve_api_url


_MAX_UPSTREAM_ERROR_CHARS = 500
_LM_STUDIO_NATIVE_CHAT_PATH = "/api/v1/chat"
_REASONING_OPTIONS = ("auto", "off", "on")


def _upstream_error_detail(response: Any) -> str | None:
    """Return one bounded, human-readable error supplied by the endpoint."""

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
    if len(detail) > _MAX_UPSTREAM_ERROR_CHARS:
        return f"{detail[: _MAX_UPSTREAM_ERROR_CHARS - 3]}..."
    return detail


def _bounded_temperature(value: Any) -> float:
    message = "temperature must be a finite number between 0 and 2."
    if isinstance(value, bool):
        raise ValueError(message)
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(message) from error
    if not math.isfinite(parsed) or parsed < 0 or parsed > 2:
        raise ValueError(message)
    return parsed


def _positive_integer(value: Any, name: str) -> int:
    message = f"{name} must be a positive integer."
    if isinstance(value, bool):
        raise ValueError(message)
    if isinstance(value, int):
        if value < 1:
            raise ValueError(message)
        return value
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(message) from error
    if not math.isfinite(numeric) or not numeric.is_integer():
        raise ValueError(message)
    parsed = int(numeric)
    if parsed < 1:
        raise ValueError(message)
    return parsed


def _reasoning_mode(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("reasoning must be a string.")
    normalized = value.strip().lower()
    if normalized not in _REASONING_OPTIONS:
        expected = ", ".join(_REASONING_OPTIONS)
        raise ValueError(f"reasoning must be one of: {expected}.")
    return normalized


def _uses_lm_studio_native_chat(url: str) -> bool:
    """Return whether an endpoint names LM Studio's native chat route."""

    return urlsplit(url).path.rstrip("/").endswith(
        _LM_STUDIO_NATIVE_CHAT_PATH
    )


def _lm_studio_native_input(content: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Translate shared multimodal content into LM Studio native input items."""

    text_items: list[dict[str, Any]] = []
    image_items: list[dict[str, Any]] = []
    for item in content:
        if item.get("type") == "image_url":
            image_url = item.get("image_url")
            if isinstance(image_url, dict) and isinstance(
                image_url.get("url"),
                str,
            ):
                image_items.append(
                    {"type": "image", "data_url": image_url["url"]}
                )
        elif item.get("type") == "text" and isinstance(item.get("text"), str):
            text_items.append({"type": "text", "content": item["text"]})
    return [*text_items, *image_items]


def _parse_lm_studio_native_response(data: dict[str, Any]) -> str:
    """Extract only final message records, never private reasoning records."""

    output = data.get("output")
    if not isinstance(output, list):
        return ""
    messages = [
        item["content"]
        for item in output
        if isinstance(item, dict)
        and item.get("type") == "message"
        and isinstance(item.get("content"), str)
        and item["content"].strip()
    ]
    return messages[-1] if messages else ""


def request_local_chat_completion(
    prompt: str,
    url: str,
    system_message: str = "",
    images: Sequence[Any] = (),
    model: str = "",
    temperature: float = 0.2,
    max_tokens: int = 4096,
    reasoning: str = "auto",
    timeout: int = 120,
) -> tuple[str, dict[str, Any]]:
    """Execute one headless local chat request and return text plus raw JSON.

    ``images`` must already be an ordered sequence of normalized image tensors.
    The helper has no Comfy node, event, or durable-history side effects.
    """

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must not be empty.")
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must not be empty.")
    if not isinstance(system_message, str):
        raise TypeError("system_message must be a string.")
    if not isinstance(model, str):
        raise TypeError("model must be a string.")

    normalized_temperature = _bounded_temperature(temperature)
    normalized_max_tokens = _positive_integer(max_tokens, "max_tokens")
    normalized_reasoning = _reasoning_mode(reasoning)
    normalized_timeout = _positive_integer(timeout, "timeout")
    normalized_model = model.strip()
    normalized_url = url.strip()

    content = build_openai_multimodal_content(
        list(images),
        prompt,
        include_all_images=True,
    )
    uses_native_chat = _uses_lm_studio_native_chat(normalized_url)
    if uses_native_chat:
        if normalized_temperature > 1:
            raise ValueError(
                "temperature must be between 0 and 1 when using LM Studio "
                "/api/v1/chat."
            )
        if not normalized_model:
            normalized_model = resolve_loaded_lm_studio_llm(
                normalized_url,
                normalized_timeout,
            )
        request = {
            "model": normalized_model,
            "input": _lm_studio_native_input(content),
            "temperature": normalized_temperature,
            "max_output_tokens": normalized_max_tokens,
            "store": False,
        }
        if system_message.strip():
            request["system_prompt"] = system_message
        if normalized_reasoning != "auto":
            request["reasoning"] = normalized_reasoning
    else:
        if normalized_reasoning != "auto":
            raise ValueError(
                "reasoning off/on requires an LM Studio native "
                "/api/v1/chat endpoint."
            )
        messages = []
        if system_message.strip():
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": content})
        request = {
            "messages": messages,
            "temperature": normalized_temperature,
            "max_tokens": normalized_max_tokens,
        }
        if normalized_model:
            request["model"] = normalized_model

    resolved_url = resolve_api_url(normalized_url)
    request_options = local_proxy_request_options(normalized_url, HEADERS)
    try:
        response = requests.post(
            resolved_url,
            json=request,
            timeout=normalized_timeout,
            **request_options,
        )
    except requests.RequestException as error:
        raise ValueError(
            "Local chat-completions request failed. Check the endpoint and "
            "whether the local model server is running."
        ) from error

    status_code = getattr(response, "status_code", None)
    if status_code != 200:
        upstream_detail = _upstream_error_detail(response)
        provider_message = (
            f" Provider said: {upstream_detail}" if upstream_detail else ""
        )
        raise ValueError(
            "Local chat-completions request failed with HTTP status "
            f"{status_code}.{provider_message}"
        )

    try:
        response_data = response.json()
    except ValueError as error:
        raise ValueError(
            "Local chat-completions response was not valid JSON."
        ) from error
    if not isinstance(response_data, dict):
        raise ValueError(
            "Local chat-completions response must be a JSON object."
        )

    parsed_text = (
        _parse_lm_studio_native_response(response_data)
        if uses_native_chat
        else parse_openai_response(response_data)
    )
    text = require_response_text(response_data, parsed_text)
    return text, response_data
