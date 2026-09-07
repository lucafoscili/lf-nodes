"""Atomic MiniMax H3 prompt authoring with a local multimodal LLM."""

from __future__ import annotations

import json
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
from ...workflow_runner.prompts.minimax_h3 import (
    H3_PROMPT_MODES,
    compile_h3_prompt_response,
)
from ...workflow_runner.prompts.minimax_h3_pipeline import (
    build_h3_planner_context,
    build_h3_prompt_planner_system,
    build_h3_scope_classifier_system,
    build_h3_scope_context,
    build_h3_visual_inventory_system,
)
from ...workflow_runner.prompts.minimax_h3_audit import (
    build_h3_audit_context,
    build_h3_audit_system,
    build_h3_repair_system,
    parse_h3_audit_response,
)


_T = TypeVar("_T")
_MAX_TOKENS = 8192
_TIMEOUT_SECONDS = 300
# Cross-checking all stages can use more reasoning than the writers themselves.
_REVIEW_MAX_TOKENS = 32768
_REVIEW_TIMEOUT_SECONDS = 600
_MAX_INTENT_CHARACTERS = 24_000
_LM_STUDIO_NATIVE_CHAT_PATH = "/api/v1/chat"
_MODES = list(H3_PROMPT_MODES)
_REASONING_PROFILES = ["vision", "off", "auto", "on"]
_FIXED_REFERENCE_COUNTS = {
    "t2va": 0,
    "i2va": 1,
    "fl2va": 2,
    "l2va": 1,
}
_PROGRESS_MESSAGES = {
    "model": "Resolving the loaded local model...",
    "inventory": "Inspecting the ordered Picture references...",
    "scope": "Classifying exact reference-transfer scope...",
    "planner": "Planning the MiniMax H3 sequence...",
    "review": "Auditing the stages against the original request and references...",
    "repair": "Repairing the earliest failing stage and rebuilding its dependents...",
    "compiler": "Compiling and validating the MiniMax H3 prompt...",
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
    mode = _scalar(kwargs.get("mode", "t2va"), "mode")
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
    if mode not in H3_PROMPT_MODES:
        raise ValueError("mode must be one of: " + ", ".join(H3_PROMPT_MODES))

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
    """Create one compiler-validated MiniMax H3 prompt as one operation."""

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
                            "Describe the desired video, reference roles, exact "
                            "continuity, motion, camera, dialogue, and sound."
                        ),
                    },
                ),
                "mode": (
                    _MODES,
                    {
                        "default": "t2va",
                        "tooltip": "MiniMax H3 input and prompt format.",
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
                            "Ordered Picture references. Count must match the "
                            "selected H3 mode."
                        ),
                    },
                ),
                "model": (
                    Input.STRING,
                    {
                        "default": "",
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
                            "Independently review the original request, images, "
                            "and every stage. Repair once and recheck if needed. "
                            "Off skips LLM review/repair, not format validation."
                        ),
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
        "Copy-ready MiniMax H3 prompt in the selected official format.",
        "H3 format validation plus the independent review findings or skipped status.",
        "Validated per-Picture allow, forbid, and uncertain evidence ledger.",
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
            intent,
            mode,
            duration_seconds,
            url,
            model,
            temperature,
            reasoning,
            images,
            review,
        ) = _run_stage(
            "Input validation",
            lambda: _validated_inputs(kwargs),
        )
        reference_image_count = len(images)
        vision_reasoning, text_reasoning = _reasoning_modes(reasoning)

        if not model and _uses_lm_studio_native_chat(url):
            _publish_progress(node_id, "model")
            model = _run_stage(
                "Model resolution",
                lambda: resolve_loaded_lm_studio_llm(
                    url,
                    _TIMEOUT_SECONDS,
                ),
            )

        def request(
            stage: str,
            prompt: str,
            system_message: str,
            stage_images: list[Any],
            stage_reasoning: str,
        ) -> str:
            _publish_progress(node_id, stage)
            text, _response_json = _run_stage(
                stage.capitalize(),
                lambda: request_local_chat_completion(
                    prompt=prompt,
                    url=url,
                    system_message=system_message,
                    images=stage_images,
                    model=model,
                    temperature=temperature,
                    max_tokens=(
                        _REVIEW_MAX_TOKENS if stage == "review" else _MAX_TOKENS
                    ),
                    reasoning=stage_reasoning,
                    timeout=(
                        _REVIEW_TIMEOUT_SECONDS
                        if stage == "review"
                        else _TIMEOUT_SECONDS
                    ),
                ),
            )
            return text

        stages: dict[str, dict[str, str]] = {}
        visual_observations: dict[str, Any] = {"pictures": []}
        visual_inventory: dict[str, Any] = {"pictures": []}
        scope_context = ""
        scope_text = json.dumps({"pictures": []})
        candidate_plan = ""

        def generate(
            stage: str,
            stage_prompt: str,
            system: str,
            stage_images: list[Any],
            stage_reasoning: str,
            findings: list[dict[str, str]],
        ) -> str:
            feedback = [item for item in findings if item["stage"] == stage]
            if feedback:
                previous = stages[stage]["response_text"]
                context = (
                    {"request": stage_prompt}
                    if stage == "inventory"
                    else json.loads(stage_prompt)
                )
                context.update(
                    previous_response_text=previous,
                    audit_findings=feedback,
                )
                stage_prompt = json.dumps(context, ensure_ascii=False)
                system = build_h3_repair_system(system, stage)
            text = request(stage, stage_prompt, system, stage_images, stage_reasoning)
            stages[stage] = {
                "stage": stage,
                "system_message": system,
                "prompt": stage_prompt,
                "response_text": text,
            }
            return text

        def generate_from(start: str, findings: list[dict[str, str]]) -> None:
            nonlocal visual_observations, visual_inventory
            nonlocal scope_context, scope_text, candidate_plan
            if start == "inventory":
                inventory_text = generate(
                    "inventory",
                    f"Inspect all {reference_image_count} attached Pictures and return "
                    "only the requested atomic pixel observations.",
                    build_h3_visual_inventory_system(mode, duration_seconds, reference_image_count),
                    images,
                    vision_reasoning,
                    findings,
                )
                scope_context, visual_observations = _run_stage(
                    "Inventory",
                    lambda: build_h3_scope_context(
                        inventory_text, intent, mode, duration_seconds, reference_image_count
                    ),
                )
            if images and start in {"inventory", "scope"}:
                scope_text = generate(
                    "scope",
                    scope_context,
                    build_h3_scope_classifier_system(mode, duration_seconds, reference_image_count),
                    [],
                    text_reasoning,
                    findings,
                )
            planner_context, visual_inventory = _run_stage(
                "Scope" if images else "Planner",
                lambda: build_h3_planner_context(
                    scope_text, visual_observations, intent, mode,
                    duration_seconds, reference_image_count,
                ),
            )
            candidate_plan = generate(
                "planner",
                planner_context,
                build_h3_prompt_planner_system(mode, duration_seconds, reference_image_count),
                [],
                text_reasoning,
                findings,
            )

        generate_from("inventory" if images else "planner", [])
        audit_reports: list[dict[str, Any]] = []
        repaired_stage: str | None = None

        def compile_candidate() -> tuple[str, dict[str, Any]]:
            return compile_h3_prompt_response(
                candidate_plan, mode, duration_seconds, reference_image_count
            )

        if review:
            # At most one repair cycle. Syntax checks remain authoritative even
            # when the independent model misses a compiler-reported defect.
            for attempt in range(2):
                compiled = None
                compiler_error = None
                try:
                    compiled = compile_candidate()
                except (TypeError, ValueError) as error:
                    compiler_error = str(error)
                audit_context = _run_stage(
                    "Review",
                    lambda: build_h3_audit_context(
                        intent=intent,
                        mode=mode,
                        duration_seconds=duration_seconds,
                        visual_observations=visual_observations,
                        visual_inventory=visual_inventory,
                        stages=list(stages.values()),
                        candidate_validation_error=compiler_error,
                    ),
                )
                audit_text = request(
                    "review",
                    audit_context,
                    build_h3_audit_system(mode, duration_seconds, reference_image_count),
                    images,
                    vision_reasoning if images else text_reasoning,
                )
                audit = _run_stage(
                    "Review",
                    lambda: parse_h3_audit_response(audit_text, list(stages)),
                )
                if compiler_error is not None:
                    audit["verdict"] = "fail"
                    audit["findings"].append({
                        "stage": "planner",
                        "path": "$",
                        "rule": "The semantic plan must pass deterministic H3 format validation.",
                        "evidence": compiler_error,
                        "correction": "Correct this compiler error in the semantic plan.",
                    })
                audit_reports.append(audit)
                if audit["verdict"] == "pass":
                    assert compiled is not None
                    prompt, validation_report = compiled
                    break
                if attempt == 1:
                    # Include the evidence in the exception so failed Comfy
                    # history retains findings even without a successful UI result.
                    raise ValueError(
                        "Review stage failed after one repair: "
                        + json.dumps(audit, ensure_ascii=False)
                    )
                order = {"inventory": 0, "scope": 1, "planner": 2}
                repaired_stage = min(
                    (finding["stage"] for finding in audit["findings"]),
                    key=order.__getitem__,
                )
                _publish_progress(node_id, "repair")
                generate_from(repaired_stage, audit["findings"])
        else:
            prompt, validation_report = _run_stage("Compiler", compile_candidate)

        _publish_progress(node_id, "compiler")
        validation_report["review"] = {
            "enabled": review,
            "status": "passed" if review else "skipped",
            "repaired_stage": repaired_stage,
            "attempts": audit_reports,
        }
        final_payload = {
            "status": "complete",
            "stage": "complete",
            "value": prompt,
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
