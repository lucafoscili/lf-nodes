"""Focused public contracts for the atomic MiniMax H3 prompt maker."""

from __future__ import annotations

import importlib
import math
from collections.abc import Iterable

import pytest
import torch

from modules.utils.constants import FUNCTION, Input


h3_module = importlib.import_module("modules.nodes.llm.h3_prompt_maker")
_OMITTED = object()
_BASE_TEXT = """integrated_multimodal_description:
[Shot 1] A camera glides across the room as rain taps the window.

overall_soundscape:
Rain taps the glass.

non_diegetic_music:
N/A"""


def _install_transport(
    monkeypatch: pytest.MonkeyPatch,
    responses: Iterable[str],
) -> tuple[list[dict], list[tuple]]:
    response_iterator = iter(responses)
    calls: list[dict] = []
    events: list[tuple] = []

    def request(**kwargs):
        calls.append(kwargs)
        return next(response_iterator), {
            "private_stage_response": f"response-{len(calls)}"
        }

    monkeypatch.setattr(h3_module, "request_local_chat_completion", request)
    monkeypatch.setattr(
        h3_module,
        "safe_send_sync",
        lambda *args: events.append(args),
    )
    return calls, events


def _execute(
    *,
    mode: str = "t2va",
    image=None,
    model: str = "test-model",
    reasoning: str = "vision",
    node_id="node-7",
    review=_OMITTED,
    **overrides,
):
    kwargs = dict(
        intent="Create one coherent cinematic movement with physical sound.",
        mode=mode,
        duration_seconds=6.0,
        url="http://localhost.test/api/v1/chat",
        image=image,
        model=model,
        temperature=0.2,
        reasoning=reasoning,
        node_id=node_id,
    )
    if review is not _OMITTED:
        kwargs["review"] = review
    kwargs.update(overrides)
    return h3_module.LF_H3PromptMaker().on_exec(**kwargs)


def _without_tooltips(schema: dict) -> dict:
    return {
        group: {
            name: (
                config[0],
                {
                    key: value
                    for key, value in config[1].items()
                    if key not in {"tooltip", "advanced"}
                },
            )
            for name, config in inputs.items()
        }
        for group, inputs in schema.items()
        if group != "hidden"
    }


def test_public_schema_mapping_and_output_contract() -> None:
    node = h3_module.LF_H3PromptMaker
    schema = node.INPUT_TYPES()

    assert _without_tooltips(schema) == {
        "required": {
            "intent": (Input.STRING, {"default": "", "multiline": True}),
            "mode": (
                ["auto", "t2va", "i2va", "fl2va", "l2va", "ref2va"],
                {"default": "auto"},
            ),
            "duration_seconds": (
                Input.FLOAT,
                {
                    "default": 6.0,
                    "min": 0.001,
                    "max": 5_999.999,
                    "step": 0.001,
                },
            ),
            "url": (
                Input.STRING,
                {"default": "http://127.0.0.1:1234/api/v1/chat"},
            ),
        },
        "optional": {
            "image": (Input.IMAGE, {}),
            "model": (Input.STRING, {"default": ""}),
            "temperature": (
                Input.FLOAT,
                {
                    "default": 0.2,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                },
            ),
            "reasoning": (
                ["vision", "off", "auto", "on"],
                {"default": "vision"},
            ),
            "ui_widget": (Input.LF_CODE, {"default": ""}),
            "review": (Input.BOOLEAN, {"default": True}),
            **{f"image_{index}": (Input.IMAGE, {}) for index in range(2, 10)},
            "instructions": (Input.STRING, {"default": "", "multiline": True}),
        },
    }
    assert list(schema["required"]) == [
        "intent",
        "mode",
        "duration_seconds",
        "url",
    ]
    assert list(schema["optional"]) == [
        "image",
        "model",
        "temperature",
        "reasoning",
        "ui_widget",
        "review",
        *[f"image_{index}" for index in range(2, 10)],
        "instructions",
    ]
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    for name in ("mode", "url"):
        assert schema["required"][name][1]["advanced"] is True
    for name in ("model", "temperature", "reasoning", "instructions"):
        assert schema["optional"][name][1]["advanced"] is True
    assert node.CATEGORY == h3_module.CATEGORY
    assert node.FUNCTION == FUNCTION
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_TYPES == (Input.STRING, Input.JSON, Input.JSON)
    assert node.RETURN_NAMES == (
        "prompt",
        "validation_report",
        "visual_inventory",
    )
    assert node.OUTPUT_IS_LIST == (False, False, False)
    assert len(node.OUTPUT_TOOLTIPS) == 3
    assert h3_module.NODE_CLASS_MAPPINGS == {"LF_H3PromptMaker": node}
    assert h3_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "LF_H3PromptMaker": "MiniMax H3 prompt maker"
    }


def test_cache_identity_refreshes_discovered_models_only() -> None:
    node = h3_module.LF_H3PromptMaker

    assert math.isnan(node.IS_CHANGED())
    assert math.isnan(node.IS_CHANGED(model="  "))
    assert math.isnan(node.IS_CHANGED(model=[""]))
    assert node.IS_CHANGED(model="explicit-model") is None
    assert node.IS_CHANGED(model=["explicit-model"]) is None


@pytest.mark.parametrize(
    "name",
    (
        "intent",
        "mode",
        "duration_seconds",
        "url",
        "model",
        "temperature",
        "reasoning",
        "review",
    ),
)
def test_scalar_controls_reject_multiple_values_before_transport(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> None:
    kwargs = {
        "intent": ["Intent"],
        "mode": ["t2va"],
        "duration_seconds": [6.0],
        "url": ["http://localhost.test/api/v1/chat"],
        "model": ["test-model"],
        "temperature": [0.2],
        "reasoning": ["vision"],
        "review": [True],
    }
    kwargs[name] = [kwargs[name][0], kwargs[name][0]]
    monkeypatch.setattr(
        h3_module,
        "request_local_chat_completion",
        lambda **_kwargs: pytest.fail("Invalid controls must not reach transport."),
    )

    with pytest.raises(ValueError) as raised:
        h3_module.LF_H3PromptMaker().on_exec(**kwargs)

    assert str(raised.value) == (
        f"Input validation stage failed: {name} must contain exactly one value"
    )


@pytest.mark.parametrize(
    ("mode", "count", "message"),
    (
        ("t2va", 1, "t2va requires exactly 0 reference images"),
        ("i2va", 0, "i2va requires exactly 1 reference image"),
        ("i2va", 2, "i2va requires exactly 1 reference image"),
        ("fl2va", 1, "fl2va requires exactly 2 reference images"),
        ("l2va", 0, "l2va requires exactly 1 reference image"),
        ("ref2va", 0, "ref2va requires between 1 and 9 reference images"),
        ("ref2va", 10, "ref2va requires between 1 and 9 reference images"),
    ),
)
def test_mode_image_cardinality_fails_before_model_or_transport(
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    count: int,
    message: str,
) -> None:
    images = [torch.zeros((1, 2, 3, 3)) for _ in range(count)]
    monkeypatch.setattr(
        h3_module,
        "resolve_loaded_lm_studio_llm",
        lambda *_args: pytest.fail("Invalid cardinality must skip lookup."),
    )
    monkeypatch.setattr(
        h3_module,
        "request_local_chat_completion",
        lambda **_kwargs: pytest.fail("Invalid cardinality must skip transport."),
    )

    with pytest.raises(ValueError) as raised:
        _execute(mode=mode, image=images, model="")

    assert str(raised.value) == f"Input validation stage failed: {message}"


_REFERENCE_TEXT = """subject_definitions:
<Subject 1> is the character from <Picture 1>.

summary:
[reference generation] <Subject 1> walks away through a medieval town.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - character identity is retained.

detailed_description:
Naturalistic fantasy with soft morning light.
[Shot 1] Seen from behind, <Subject 1> walks along a cobbled lane between timber houses.
The camera tracks at walking speed. Footsteps tap the uneven stones.

overall_soundscape:
Footsteps, wind and distant market activity.

non_diegetic_music:
N/A"""


def test_short_intent_and_one_image_go_directly_to_writer_and_reviewer(monkeypatch):
    calls, events = _install_transport(monkeypatch, [_REFERENCE_TEXT, _REFERENCE_TEXT])
    image = torch.zeros((1, 2, 3, 3))
    intent = "Walking from behind in a medieval town"
    result = _execute(mode="auto", image=image, intent=intent)
    assert len(calls) == 2
    assert f"Original idea:\n{intent}\n\n" in calls[0]["prompt"]
    assert all("Resolved mode: ref2va." in call["prompt"] for call in calls)
    assert all("Output sections, in order: subject_definitions, summary," in call["prompt"] for call in calls)
    assert all(torch.equal(call["images"][0], image) for call in calls)
    assert f"Original idea:\n{intent}\n\nDraft prompt:\n" in calls[1]["prompt"]
    assert _REFERENCE_TEXT in calls[1]["prompt"]
    assert "format_error" not in calls[1]["prompt"]
    prompt, report, receipt = result["result"]
    assert "<Subject 1> is the character from <Picture 1>." in prompt
    assert "<Subject 2>" not in prompt
    assert "allowed_facts" not in prompt
    assert report["mode"] == "ref2va"
    assert report["valid"] is None
    assert report["validation"] == "not_performed"
    assert report["authoring"]["stages"] == ["writer", "review"]
    assert report["review"]["status"] == "completed"
    assert receipt == {
        "pictures": [{"picture": 1, "facts": []}],
        "method": "direct_vision", "inventoryPerformed": False,
    }
    assert events[-1] == ("h3promptmaker", result["ui"]["lf_output"][0], "node-7")


def test_auto_without_images_uses_base_sections(monkeypatch):
    calls, _ = _install_transport(monkeypatch, [_BASE_TEXT, _BASE_TEXT])
    result = _execute(mode="auto")
    assert result["result"][1]["mode"] == "t2va"
    assert len(calls) == 2
    assert all(call["images"] == [] for call in calls)


def test_independent_sockets_and_legacy_lists_preserve_every_image_in_order(monkeypatch):
    a = torch.zeros((1, 2, 3, 3))
    b = torch.ones((2, 4, 5, 4))
    c = torch.full((1, 2, 3, 3), 0.5)
    text = _REFERENCE_TEXT.replace("from <Picture 1>.", "from <Picture 1>, <Picture 2>, <Picture 3>, and <Picture 4>.")
    calls, _ = _install_transport(monkeypatch, [text, text])
    result = _execute(mode="auto", image=[a], image_2=[b], image_4=[[c]])
    for call in calls:
        assert [tuple(item.shape) for item in call["images"]] == [
            (1, 2, 3, 3), (1, 4, 5, 4), (1, 4, 5, 4), (1, 2, 3, 3),
        ]
        assert torch.equal(call["images"][0], a)
        assert torch.equal(call["images"][-1], c)
    assert result["result"][1]["referenceImageCount"] == 4


@pytest.mark.parametrize("mode,count", [("i2va", 1), ("fl2va", 2), ("l2va", 1)])
def test_saved_explicit_frame_modes_keep_meaning(monkeypatch, mode, count):
    calls, _ = _install_transport(monkeypatch, [_BASE_TEXT])
    result = _execute(mode=mode, image=[torch.zeros((1, 2, 3, 3))] * count, review=False)
    assert result["result"][1]["mode"] == mode
    assert len(calls) == 1
    assert len(calls[0]["images"]) == count
    assert result["result"][0] == _BASE_TEXT  # No application-added alignment preamble.
    assert "image-alignment sentence" in calls[0]["system_message"]


@pytest.mark.parametrize("text", [
    "A character walks away through a medieval town. Footsteps tap the cobbles.",
    _REFERENCE_TEXT.replace("[Shot 1] Seen", "[Shot 1] At 00:01.000, Seen"),
    "  ```text\nAn unfenced answer was requested, but do not postprocess it.\n```  ",
])
def test_review_off_returns_exact_prose_without_format_gates_or_repairs(monkeypatch, text):
    calls, events = _install_transport(monkeypatch, [text])
    result = _execute(mode="auto", image=torch.zeros((1, 2, 3, 3)), review=False)
    assert len(calls) == 1
    assert result["result"][0] == text
    assert result["ui"]["lf_output"][0]["value"] == text
    assert result["result"][1]["authoring"] == {"method": "prose", "stages": ["writer"]}
    assert result["result"][1]["review"]["status"] == "skipped"
    assert result["result"][1]["valid"] is None
    assert [event[1]["stage"] for event in events] == ["writer", "complete"]


def test_reviewer_receives_plain_draft_and_returns_exact_replacement(monkeypatch):
    draft = "The character walks through town."
    reviewed = "  From behind, follow the character through the medieval town.\n"
    calls, _ = _install_transport(monkeypatch, [draft, reviewed])
    result = _execute()
    assert len(calls) == 2
    assert f"Draft prompt:\n{draft}" in calls[1]["prompt"]
    assert result["result"][0] == reviewed
    assert result["result"][1]["valid"] is None
    assert result["result"][1]["validation"] == "not_performed"


def test_reviewer_format_deviations_do_not_trigger_a_third_call(monkeypatch):
    reviewed = _REFERENCE_TEXT.replace("non_diegetic_music:", "Music:")
    calls, _ = _install_transport(monkeypatch, [_REFERENCE_TEXT, reviewed])
    result = _execute(mode="auto", image=torch.zeros((1, 2, 3, 3)))
    assert len(calls) == 2
    assert result["result"][0] == reviewed


def test_unreviewed_valid_prompt_needs_only_one_call(monkeypatch):
    calls, _ = _install_transport(monkeypatch, [_BASE_TEXT])
    result = _execute(review=False)
    assert len(calls) == 1
    assert result["result"][1]["review"]["status"] == "skipped"


@pytest.mark.parametrize("review", [None, 0, 1, "false"])
def test_review_requires_a_boolean(monkeypatch, review):
    calls, _ = _install_transport(monkeypatch, [])
    with pytest.raises(ValueError, match="review must be a boolean"):
        _execute(review=review)
    assert not calls


@pytest.mark.parametrize("reasoning,expected", [("vision", "on"), ("off", "off"), ("auto", "auto"), ("on", "on")])
def test_image_writer_and_review_use_requested_reasoning(monkeypatch, reasoning, expected):
    calls, _ = _install_transport(monkeypatch, [_REFERENCE_TEXT, _REFERENCE_TEXT])
    _execute(mode="auto", image=torch.zeros((1, 2, 3, 3)), reasoning=reasoning)
    assert [call["reasoning"] for call in calls] == [expected, expected]


def test_blank_native_model_resolves_once_and_reuses_exact_instance(monkeypatch):
    resolved = []
    monkeypatch.setattr(h3_module, "resolve_loaded_lm_studio_llm", lambda *args: resolved.append(args) or "loaded-instance")
    calls, _ = _install_transport(monkeypatch, [_BASE_TEXT, _BASE_TEXT])
    _execute(model="")
    assert len(resolved) == 1
    assert [call["model"] for call in calls] == ["loaded-instance", "loaded-instance"]


def test_provider_error_is_actionable_and_not_retried_as_format_error(monkeypatch):
    def fail(**kwargs):
        raise ValueError("Model is not loaded")
    monkeypatch.setattr(h3_module, "request_local_chat_completion", fail)
    with pytest.raises(ValueError, match="Writer stage failed: Model is not loaded"):
        _execute()


def test_review_transport_error_is_reported_without_retry_or_silent_fallback(monkeypatch):
    calls = []
    def request(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return _BASE_TEXT, {}
        raise ValueError("Model disconnected")
    monkeypatch.setattr(h3_module, "request_local_chat_completion", request)
    with pytest.raises(ValueError, match="Review stage failed: Model disconnected"):
        _execute()
    assert len(calls) == 2


def test_headless_output_and_list_wrapped_controls(monkeypatch):
    _install_transport(monkeypatch, [_BASE_TEXT])
    result = _execute(
        intent=["Rain on a window"], mode=["auto"], duration_seconds=[6.0],
        url=["http://localhost.test/api/v1/chat"], model=["model"],
        temperature=[0.2], reasoning=["off"], review=[False], node_id=None,
        instructions=["Use a restrained documentary style."],
    )
    assert result["ui"]["lf_output"][0]["status"] == "complete"
    assert result["result"][1]["valid"] is None
