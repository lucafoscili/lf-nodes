"""Exact-instance LM Studio lifecycle operations for connected workflows."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests

from ...constants import HEADERS
from .lm_studio_models import lm_studio_models_url, _response_error_detail
from .read_secret import read_secret
from .resolve_url import local_proxy_request_options, resolve_api_url


def lifecycle_scalar(value: Any, name: str) -> Any:
    """Unwrap Comfy's scalar envelope; never discard a multi-item input."""
    while isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise ValueError(f"{name} requires exactly one value per lifecycle node.")
        value = value[0]
    return value


def _identifier(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value.strip()


def _endpoint(url: str, action: str = "") -> str:
    models_url = lm_studio_models_url(_identifier(url, "url"))
    parsed = urlsplit(models_url)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path + action,
                       parsed.query, parsed.fragment))


def _request(url: str, timeout: int, payload: dict | None = None) -> dict:
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout < 1:
        raise ValueError("timeout must be a positive integer.")
    options = local_proxy_request_options(url, HEADERS)
    token = read_secret("LM_API_TOKEN")
    if token:
        options["headers"]["Authorization"] = f"Bearer {token}"
    options["allow_redirects"] = False
    try:
        if payload is None:
            response = requests.get(resolve_api_url(url), timeout=timeout, **options)
        else:
            response = requests.post(
                resolve_api_url(url), json=payload, timeout=timeout, **options
            )
    except requests.RequestException as error:
        raise ValueError(
            "LM Studio model lifecycle request failed. Check the endpoint and "
            "server; a timed-out operation may have completed."
        ) from error
    status = getattr(response, "status_code", None)
    if status != 200:
        detail = _response_error_detail(response)
        if detail and token:
            detail = detail.replace(token, "[redacted]")
        hint = (
            " Check LM_API_TOKEN (or LM_API_TOKEN_FILE) on the Comfy server."
            if status in (401, 403) else ""
        )
        raise ValueError(
            f"LM Studio model lifecycle request failed with HTTP status {status}."
            f"{hint}" + (f" Provider said: {detail}" if detail else "")
        )
    try:
        data = response.json()
    except (TypeError, ValueError) as error:
        raise ValueError("LM Studio model lifecycle response was not valid JSON.") from error
    if not isinstance(data, dict):
        raise ValueError("LM Studio model lifecycle response must be a JSON object.")
    return data


def _inventory(url: str, timeout: int) -> list[dict]:
    data = _request(_endpoint(url), timeout)
    models = data.get("models")
    malformed = "LM Studio model inventory must contain model keys and loaded instance IDs."
    if not isinstance(models, list):
        raise ValueError(malformed)
    for model in models:
        if (
            not isinstance(model, dict)
            or model.get("type") not in ("llm", "embedding")
            or not isinstance(model.get("key"), str)
            or not model["key"].strip()
            or not isinstance(model.get("loaded_instances"), list)
        ):
            raise ValueError(malformed)
        for instance in model["loaded_instances"]:
            if (
                not isinstance(instance, dict)
                or not isinstance(instance.get("id"), str)
                or not instance["id"].strip()
            ):
                raise ValueError(malformed)
    return models


def load_lm_studio_model(model: str, url: str, timeout: int = 120) -> str:
    """Reuse a sole loaded instance of this exact model key, otherwise load it."""
    key = _identifier(model, "model")
    matches = [item for item in _inventory(url, timeout) if item["key"] == key]
    if len(matches) != 1 or matches[0]["type"] != "llm":
        raise ValueError(
            "model must match exactly one downloaded LM Studio LLM key. "
            "No model was loaded or downloaded."
        )
    instances = matches[0]["loaded_instances"]
    if len(instances) > 1:
        raise ValueError(
            "The requested model has multiple loaded instances. Keep one instance "
            "before using LMS Load Model; no instance was selected or unloaded."
        )
    if instances:
        return instances[0]["id"]
    data = _request(_endpoint(url, "/load"), timeout, {"model": key})
    instance_id = data.get("instance_id")
    if (
        data.get("type") != "llm" or data.get("status") != "loaded"
        or not isinstance(instance_id, str) or not instance_id.strip()
    ):
        raise ValueError(
            "LM Studio load response must confirm a loaded LLM and its instance_id."
        )
    return instance_id


def unload_lm_studio_model(instance_id: str, url: str, timeout: int = 120) -> None:
    """Unload only the exact instance, or succeed if it is already absent."""
    exact_id = _identifier(instance_id, "instance_id")
    present = any(
        instance["id"] == exact_id
        for model in _inventory(url, timeout)
        for instance in model["loaded_instances"]
    )
    if not present:
        return
    data = _request(_endpoint(url, "/unload"), timeout, {"instance_id": exact_id})
    if data.get("instance_id") != exact_id:
        raise ValueError("LM Studio unload response did not confirm the requested instance_id.")
