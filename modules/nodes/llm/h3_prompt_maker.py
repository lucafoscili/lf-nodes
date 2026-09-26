"""Atomic MiniMax H3 prompt authoring with a local multimodal LLM."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any, TypeVar
from urllib.parse import urlsplit

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.api import (
    request_local_chat_completion,
    resolve_loaded_lm_studio_llm,
)
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image
from ...utils.helpers.llm.h3_prompt import (
    H3_PROMPT_MODES,
    build_authoring_system,
)


_T = TypeVar("_T")
# Reasoning and final prose share the provider's output budget.
_MAX_TOKENS = 32768
_TIMEOUT_SECONDS = 600
_MAX_INTENT_CHARACTERS = 24_000
_LM_STUDIO_NATIVE_CHAT_PATH = "/api/v1/chat"
_MODES = ["auto", *H3_PROMPT_MODES]
_REASONING_PROFILES = ["vision", "off", "auto", "on"]
_FIXED_REFERENCE_COUNTS = {
    "t2va": 0,
    "i2va": 1,
    "fl2va": 2,
    "l2va": 1,
}
_PROGRESS_MESSAGES = {
    "model": "Resolving the loaded local model...",
    "writer": "Writing the scene from your idea and references...",
    "review": "Reviewing the prompt against your idea and references...",
}


def _scalar(value: Any, name: str) -> Any:
    """Normalize one list-wrapped control without hiding cardinality errors."""

    if isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise ValueError(f"{name} must contain exactly one value")
        return value[0]
    return value


def _uses_lm_studio_native_chat(url: str) -> bool:
    return urlsplit(url).path.rstrip("/").endswith(
        _LM_STUDIO_NATIVE_CHAT_PATH
    )


def _run_stage(stage: str, operation: Callable[[], _T]) -> _T:
    try:
        return operation()
    except (TypeError, ValueError) as error:
        raise ValueError(f"{stage} stage failed: {error}") from error


def _publish_progress(node_id: Any, stage: str) -> None:
    safe_send_sync(
        "h3promptmaker",
        {
            "status": "running",
            "stage": stage,
            "value": _PROGRESS_MESSAGES[stage],
        },
        node_id,
    )


def _validated_inputs(kwargs: dict[str, Any]) -> tuple[
    str,
    str,
    float,
    str,
    str,
    float,
    str,
    list[Any],
    bool,
]:
    intent = _scalar(kwargs.get("intent", ""), "intent")
    mode = _scalar(kwargs.get("mode", "auto"), "mode")
    duration_seconds = _scalar(
        kwargs.get("duration_seconds", 6.0),
        "duration_seconds",
    )
    url = _scalar(kwargs.get("url", ""), "url")
    model = _scalar(kwargs.get("model", ""), "model")
    temperature = _scalar(
        kwargs.get("temperature", 0.2),
        "temperature",
    )
    reasoning = _scalar(kwargs.get("reasoning", "vision"), "reasoning")
    review = _scalar(kwargs.get("review", True), "review")
    images = normalize_input_image(kwargs.get("image"))
    for index in range(2, 10):
        images.extend(normalize_input_image(kwargs.get(f"image_{index}")))

    if not isinstance(review, bool):
        raise TypeError("review must be a boolean")

    if not isinstance(intent, str):
        raise TypeError("intent must be a string")
    intent = intent.strip()
    if not intent:
        raise ValueError("intent must not be blank")
    if len(intent) > _MAX_INTENT_CHARACTERS:
        raise ValueError(
            f"intent cannot exceed {_MAX_INTENT_CHARACTERS} characters"
        )

    if not isinstance(mode, str):
        raise TypeError("mode must be a string")
    mode = mode.strip().lower()
    if mode not in _MODES:
        raise ValueError("mode must be one of: " + ", ".join(_MODES))
    if mode == "auto":
        mode = "ref2va" if images else "t2va"

    if isinstance(duration_seconds, bool) or not isinstance(
        duration_seconds,
        (int, float),
    ):
        raise TypeError("duration_seconds must be a finite number")
    duration_seconds = float(duration_seconds)
    if (
        not math.isfinite(duration_seconds)
        or duration_seconds <= 0
        or duration_seconds >= 6000
    ):
        raise ValueError(
            "duration_seconds must be greater than 0 and less than 6000"
        )

    if not isinstance(url, str):
        raise TypeError("url must be a string")
    url = url.strip()
    if not url:
        raise ValueError("url must not be blank")
    if not isinstance(model, str):
        raise TypeError("model must be a string")
    model = model.strip()

    if isinstance(temperature, bool):
        raise TypeError("temperature must be a finite number between 0 and 1")
    try:
        temperature = float(temperature)
    except (TypeError, ValueError, OverflowError) as error:
        raise TypeError(
            "temperature must be a finite number between 0 and 1"
        ) from error
    if not math.isfinite(temperature) or not 0 <= temperature <= 1:
        raise ValueError("temperature must be a finite number between 0 and 1")

    if not isinstance(reasoning, str):
        raise TypeError("reasoning must be a string")
    reasoning = reasoning.strip().lower()
    if reasoning not in _REASONING_PROFILES:
        raise ValueError(
            "reasoning must be one of: " + ", ".join(_REASONING_PROFILES)
        )

    reference_image_count = len(images)
    if mode == "ref2va":
        if not 1 <= reference_image_count <= 9:
            raise ValueError(
                "ref2va requires between 1 and 9 reference images"
            )
    else:
        expected = _FIXED_REFERENCE_COUNTS[mode]
        if reference_image_count != expected:
            raise ValueError(
                f"{mode} requires exactly {expected} reference image"
                + ("" if expected == 1 else "s")
            )

    return (
        intent,
        mode,
        duration_seconds,
        url,
        model,
        temperature,
        reasoning,
        images,
        review,
    )


def _reasoning_modes(profile: str) -> tuple[str, str]:
    if profile == "vision":
        return "on", "off"
    return profile, profile


# region LF_H3PromptMaker
class LF_H3PromptMaker:
    """Turn a short idea and ordered references into a reviewed H3 prompt."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "intent": (
                    Input.STRING,
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": (
                            "A short idea is enough, e.g. walking from behind in a "
                            "medieval town. Add reference roles or constraints only "
                            "when you want to override the automatic choices."
                        ),
                    },
                ),
                "mode": (
                    _MODES,
                    {
                        "default": "auto",
                        "advanced": True,
                        "tooltip": (
                            "Auto uses text generation without images and reusable "
                            "references with images. Choose i2va/fl2va/l2va only "
                            "for fixed first/last frames."
                        ),
                    },
                ),
                "duration_seconds": (
                    Input.FLOAT,
                    {
                        "default": 6.0,
                        "min": 0.001,
                        "max": 5_999.999,
                        "step": 0.001,
                        "tooltip": "Exact target video duration in seconds.",
                    },
                ),
                "url": (
                    Input.STRING,
                    {
                        "default": "http://127.0.0.1:1234/api/v1/chat",
                        "advanced": True,
                        "tooltip": (
                            "LM Studio native /api/v1/chat endpoint. This route "
                            "supports blank-model discovery, vision, and the "
                            "pipeline reasoning profiles."
                        ),
                    },
                ),
            },
            "optional": {
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": (
                            "Picture 1 (or an ordered image list). Connect more "
                            "references below; different sizes are preserved."
                        ),
                    },
                ),
                "model": (
                    Input.STRING,
                    {
                        "default": "",
                        "advanced": True,
                        "tooltip": (
                            "Optional model identifier. A blank native LM Studio "
                            "request uses its sole loaded LLM instance."
                        ),
                    },
                ),
                "temperature": (
                    Input.FLOAT,
                    {
                        "default": 0.2,
                        "advanced": True,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.1,
                        "tooltip": "Response randomness shared by every stage.",
                    },
                ),
                "reasoning": (
                    _REASONING_PROFILES,
                    {
                        "default": "vision",
                        "advanced": True,
                        "tooltip": (
                            "Vision reasons while inspecting or reviewing pixels; other "
                            "profiles apply to every stage."
                        ),
                    },
                ),
                "ui_widget": (Input.LF_CODE, {"default": ""}),
                "review": (
                    Input.BOOLEAN,
                    {
                        "default": True,
                        "tooltip": (
                            "Review the completed prompt against your idea and "
                            "images. Off returns the writer's prose directly."
                        ),
                    },
                ),
                **{
                    f"image_{index}": (
                        Input.IMAGE,
                        {"tooltip": "Next ordered Picture reference; no shared size required."},
                    )
                    for index in range(2, 10)
                },
                "instructions": (
                    Input.STRING,
                    {
                        "default": "",
                        "multiline": True,
                        "advanced": True,
                        "tooltip": "Optional authoring direction alongside the H3 writing guidance.",
                    },
                ),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.STRING, Input.JSON, Input.JSON)
    RETURN_NAMES = ("prompt", "validation_report", "visual_inventory")
    OUTPUT_IS_LIST = (False, False, False)
    OUTPUT_TOOLTIPS = (
        "Prompt prose returned by the writer or optional reviewer, without schema compilation.",
        "Authoring status on the legacy report socket; no format validation is performed.",
        "Ordered reference receipt; images are read directly without an intermediate facts ledger.",
    )

    @classmethod
    def IS_CHANGED(cls, **kwargs: Any):
        """Do not cache results whose model identity is discovered at runtime."""

        model = kwargs.get("model", "")
        if isinstance(model, (list, tuple)):
            if len(model) == 1:
                model = model[0]
            elif not model:
                model = ""
            else:
                return float("NaN")
        if model is None or (isinstance(model, str) and not model.strip()):
            return float("NaN")
        return None

    def on_exec(self, **kwargs: Any):
        node_id = kwargs.get("node_id")
        (
            intent, mode, duration_seconds, url, model, temperature,
            reasoning, images, review,
        ) = _run_stage("Input validation", lambda: _validated_inputs(kwargs))
        instructions = _scalar(kwargs.get("instructions", ""), "instructions")
        if not isinstance(instructions, str):
            raise TypeError("instructions must be a string")
        reference_image_count = len(images)
        vision_reasoning, text_reasoning = _reasoning_modes(reasoning)
        stage_reasoning = vision_reasoning if images else text_reasoning

        if not model and _uses_lm_studio_native_chat(url):
            _publish_progress(node_id, "model")
            model = _run_stage(
                "Model resolution",
                lambda: resolve_loaded_lm_studio_llm(url, _TIMEOUT_SECONDS),
            )

        calls: list[str] = []

        def request(stage: str, prompt: str, *, reviewing: bool = False) -> str:
            _publish_progress(node_id, stage)
            system = build_authoring_system(
                mode, duration_seconds, reference_image_count,
                review=reviewing, instructions=instructions,
            )
            text, _response = _run_stage(
                stage.capitalize(),
                lambda: request_local_chat_completion(
                    prompt=prompt, url=url, system_message=system, images=images,
                    model=model, temperature=temperature,
                    max_tokens=_MAX_TOKENS,
                    reasoning=stage_reasoning,
                    timeout=_TIMEOUT_SECONDS,
                ),
            )
            calls.append(stage)
            return text

        prompt = request("writer", intent)
        if review:
            prompt = request(
                "review",
                f"Original idea:\n{intent}\n\nDraft prompt:\n{prompt}\n\n"
                "Review this draft against the original idea, attached images, and "
                "authoring guidance. Return only the complete prompt prose.",
                reviewing=True,
            )

        # Preserve saved output connections, without claiming prose was validated.
        validation_report = {
            "valid": None,
            "validation": "not_performed",
            "mode": mode,
            "referenceImageCount": reference_image_count,
            "review": {
                "enabled": review,
                "status": "completed" if review else "skipped",
            },
            "authoring": {"method": "prose", "stages": calls},
        }
        # Keep the published socket and pictures/facts containers. An empty ledger
        # is explicit: no claims were extracted by a separate inventory model.
        visual_inventory = {
            "pictures": [
                {"picture": index, "facts": []}
                for index in range(1, reference_image_count + 1)
            ],
            "method": "direct_vision",
            "inventoryPerformed": False,
        }
        final_payload = {
            "status": "complete", "stage": "complete", "value": prompt,
            "validation_report": validation_report,
            "visual_inventory": visual_inventory,
        }
        safe_send_sync("h3promptmaker", final_payload, node_id)
        return {
            "ui": {"lf_output": [final_payload]},
            "result": (prompt, validation_report, visual_inventory),
        }


# endregion


# region Mappings
NODE_CLASS_MAPPINGS = {"LF_H3PromptMaker": LF_H3PromptMaker}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_H3PromptMaker": "MiniMax H3 prompt maker",
}
# endregion
