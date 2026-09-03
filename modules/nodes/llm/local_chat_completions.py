import math
from typing import Any
from urllib.parse import urlsplit

import requests

from . import CATEGORY
from ...utils.constants import FUNCTION, HEADERS, Input
from ...utils.helpers.api import (
    build_openai_multimodal_content,
    local_proxy_request_options,
    parse_openai_response,
    require_response_text,
    resolve_api_url,
)
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value


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


def _scalar(value: Any) -> Any:
    if isinstance(value, list) and not value:
        return None
    return normalize_list_to_value(value)


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
    """Translate the shared vision payload into LM Studio native input items."""

    text_items: list[dict[str, Any]] = []
    image_items: list[dict[str, Any]] = []
    for item in content:
        if item.get("type") == "image_url":
            image_url = item.get("image_url")
            if isinstance(image_url, dict) and isinstance(image_url.get("url"), str):
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


# region LF_LocalChatCompletions
class LF_LocalChatCompletions:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    Input.STRING,
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "User prompt sent to the local chat-completions endpoint.",
                    },
                ),
                "url": (
                    Input.STRING,
                    {
                        "default": "http://127.0.0.1:1234/v1/chat/completions",
                        "tooltip": (
                            "Local OpenAI-compatible /v1/chat/completions or "
                            "LM Studio native /api/v1/chat endpoint."
                        ),
                    },
                ),
            },
            "optional": {
                "system_message": (
                    Input.STRING,
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Optional system instruction sent before the user prompt.",
                    },
                ),
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": "Optional ordered reference images for a vision-capable model.",
                    },
                ),
                "model": (
                    Input.STRING,
                    {
                        "default": "",
                        "tooltip": (
                            "Optional for OpenAI-compatible endpoints; required "
                            "for LM Studio native chat."
                        ),
                    },
                ),
                "temperature": (
                    Input.FLOAT,
                    {
                        "default": 0.2,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.1,
                        "tooltip": "Controls response randomness.",
                    },
                ),
                "max_tokens": (
                    Input.INTEGER,
                    {
                        "default": 4096,
                        "min": 1,
                        "tooltip": "Response token budget, including any model reasoning.",
                    },
                ),
                "timeout": (
                    Input.INTEGER,
                    {
                        "default": 120,
                        "min": 1,
                        "tooltip": "Request timeout in seconds.",
                    },
                ),
                "ui_widget": (Input.LF_CODE, {"default": ""}),
                "reasoning": (
                    list(_REASONING_OPTIONS),
                    {
                        "default": "auto",
                        "tooltip": (
                            "LM Studio native reasoning control. auto uses the "
                            "model default; off/on require /api/v1/chat."
                        ),
                    },
                ),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, False)
    OUTPUT_TOOLTIPS = (
        "Exact answer text returned by the local model.",
        "Complete JSON response returned by the endpoint.",
    )
    RETURN_NAMES = ("text", "response_json")
    RETURN_TYPES = (Input.STRING, Input.JSON)

    def on_exec(self, **kwargs: dict):
        prompt = _scalar(kwargs.get("prompt", ""))
        url = _scalar(kwargs.get("url", ""))
        system_message = _scalar(kwargs.get("system_message", ""))
        model = _scalar(kwargs.get("model", ""))
        temperature = _scalar(kwargs.get("temperature", 0.2))
        max_tokens = _scalar(kwargs.get("max_tokens", 4096))
        reasoning = _scalar(kwargs.get("reasoning", "auto"))
        timeout = _scalar(kwargs.get("timeout", 120))
        images = normalize_input_image(kwargs.get("image"))

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must not be empty.")
        if not isinstance(url, str) or not url.strip():
            raise ValueError("URL must not be empty.")
        if not isinstance(system_message, str):
            raise TypeError("system_message must be a string.")
        if not isinstance(model, str):
            raise TypeError("model must be a string.")

        temperature = _bounded_temperature(temperature)
        max_tokens = _positive_integer(max_tokens, "max_tokens")
        reasoning = _reasoning_mode(reasoning)
        timeout = _positive_integer(timeout, "timeout")

        content = build_openai_multimodal_content(
            images,
            prompt,
            include_all_images=True,
        )
        normalized_model = model.strip()
        normalized_url = url.strip()
        uses_native_chat = _uses_lm_studio_native_chat(normalized_url)
        if uses_native_chat:
            if not normalized_model:
                raise ValueError(
                    "model must name a loaded LM Studio model when using "
                    "/api/v1/chat."
                )
            if temperature > 1:
                raise ValueError(
                    "temperature must be between 0 and 1 when using LM Studio "
                    "/api/v1/chat."
                )
            request = {
                "model": normalized_model,
                "input": _lm_studio_native_input(content),
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "store": False,
            }
            if system_message.strip():
                request["system_prompt"] = system_message
            if reasoning != "auto":
                request["reasoning"] = reasoning
        else:
            if reasoning != "auto":
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
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if normalized_model:
                request["model"] = normalized_model

        resolved_url = resolve_api_url(normalized_url)
        request_options = local_proxy_request_options(normalized_url, HEADERS)
        try:
            response = requests.post(
                resolved_url,
                json=request,
                timeout=timeout,
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
                f" Provider said: {upstream_detail}"
                if upstream_detail
                else ""
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
        final_payload = {"value": text}
        safe_send_sync(
            "localchatcompletions",
            final_payload,
            kwargs.get("node_id"),
        )

        return {
            "ui": {"lf_output": [final_payload]},
            "result": (text, response_data),
        }
# endregion


# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LocalChatCompletions": LF_LocalChatCompletions,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LocalChatCompletions": "Local chat completions",
}
# endregion
