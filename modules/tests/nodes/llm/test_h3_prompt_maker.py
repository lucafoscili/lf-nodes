"""Focused public contracts for the atomic MiniMax H3 prompt maker."""

from __future__ import annotations

import importlib
import json
import math
from collections.abc import Iterable

import pytest
import torch

from modules.utils.constants import FUNCTION, Input


h3_module = importlib.import_module("modules.nodes.llm.h3_prompt_maker")
_OMITTED = object()
_AUDIT_PASS = json.dumps({"verdict": "pass", "findings": []})


_BASE_PLAN = json.dumps(
    {
        "shots": [
            {
                "start_seconds": 0,
                "description": (
                    "A camera glides across the room as rain taps the window."
                ),
                "dialogue": [],
            }
        ],
        "overall_soundscape": "Rain taps the glass.",
        "non_diegetic_music": "N/A",
    }
)


def _inventory_response(count: int) -> str:
    return json.dumps(
        {
            "pictures": [
                {
                    "picture": ordinal,
                    "facts": [f"Picture {ordinal} contains a distinct form."],
                }
                for ordinal in range(1, count + 1)
            ]
        }
    )


def _scope_response(count: int) -> str:
    return json.dumps(
        {
            "pictures": [
                {
                    "picture": ordinal,
                    "decisions": [{"id": 1, "transfer": "allow"}],
                }
                for ordinal in range(1, count + 1)
            ]
        }
    )


def _responses_for(count: int) -> list[str]:
    if count == 0:
        return [_BASE_PLAN, _AUDIT_PASS]
    return [
        _inventory_response(count),
        _scope_response(count),
        _BASE_PLAN,
        _AUDIT_PASS,
    ]


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
    return h3_module.LF_H3PromptMaker().on_exec(**kwargs)


def _without_tooltips(schema: dict) -> dict:
    return {
        group: {
            name: (
                config[0],
                {
                    key: value
                    for key, value in config[1].items()
                    if key != "tooltip"
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
                ["t2va", "i2va", "fl2va", "l2va", "ref2va"],
                {"default": "t2va"},
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
    ]
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
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


def test_t2va_uses_two_text_calls_and_returns_real_compiler_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls, events = _install_transport(monkeypatch, _responses_for(0))

    result = _execute(node_id=["wrapped-node"])

    assert len(calls) == 2
    assert [call["images"] for call in calls] == [[], []]
    assert [call["reasoning"] for call in calls] == ["off", "off"]
    assert [call["max_tokens"] for call in calls] == [8192, 32768]
    assert [call["timeout"] for call in calls] == [300, 600]
    prompt, report, inventory = result["result"]
    assert prompt.startswith("integrated_multimodal_description:\n[Shot 1]")
    assert report["valid"] is True
    assert report["mode"] == "t2va"
    assert report["referenceImageCount"] == 0
    assert report["review"] == {
        "enabled": True, "status": "passed", "repaired_stage": None,
        "attempts": [{"verdict": "pass", "findings": []}],
    }
    assert inventory == {"pictures": []}

    assert [event[1]["stage"] for event in events] == [
        "planner",
        "review",
        "compiler",
        "complete",
    ]
    assert all(event[0] == "h3promptmaker" for event in events)
    final_payload = events[-1][1]
    assert result["ui"] == {"lf_output": [final_payload]}
    assert result["ui"]["lf_output"][0] is final_payload
    assert final_payload == {
        "status": "complete",
        "stage": "complete",
        "value": prompt,
        "validation_report": report,
        "visual_inventory": inventory,
    }
    assert "private_stage_response" not in json.dumps(result)
    assert "private_stage_response" not in json.dumps(events)


def test_image_mode_inventory_and_auditor_receive_ordered_images(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = torch.arange(18, dtype=torch.float32).reshape(1, 2, 3, 3)
    second = torch.arange(80, dtype=torch.float32).reshape(1, 4, 5, 4)
    calls, _events = _install_transport(monkeypatch, _responses_for(2))

    result = _execute(mode="fl2va", image=[first, [second]])

    assert len(calls) == 4
    received = calls[0]["images"]
    assert [call["max_tokens"] for call in calls] == [8192, 8192, 8192, 32768]
    assert [call["timeout"] for call in calls] == [300, 300, 300, 600]
    assert [tuple(image.shape) for image in received] == [
        (1, 2, 3, 3),
        (1, 4, 5, 4),
    ]
    assert torch.equal(received[0], first)
    assert torch.equal(received[1], second)
    assert calls[0]["prompt"] == (
        "Inspect all 2 attached Pictures and return only the requested atomic "
        "pixel observations."
    )
    assert "Create one coherent" not in calls[0]["prompt"]
    assert [call["images"] for call in calls[1:3]] == [[], []]
    assert all(torch.equal(actual, expected) for actual, expected in zip(
        calls[3]["images"], (first, second), strict=True
    ))
    assert [call["reasoning"] for call in calls] == [
        "on",
        "off",
        "off",
        "on",
    ]
    audit_context = json.loads(calls[3]["prompt"])
    assert [item["stage"] for item in audit_context["stages"]] == [
        "inventory", "scope", "planner"
    ]
    assert audit_context["stages"][0]["response_text"] == _inventory_response(2)
    assert audit_context["stages"][2]["system_message"] == calls[2]["system_message"]
    assert result["result"][1]["mode"] == "fl2va"
    assert result["result"][2] == {
        "pictures": [
            {
                "picture": 1,
                "facts": [
                    {
                        "fact": "Picture 1 contains a distinct form.",
                        "transfer": "allow",
                    }
                ],
            },
            {
                "picture": 2,
                "facts": [
                    {
                        "fact": "Picture 2 contains a distinct form.",
                        "transfer": "allow",
                    }
                ],
            },
        ]
    }


@pytest.mark.parametrize(
    ("profile", "expected"),
    (
        ("vision", ["on", "off", "off", "on"]),
        ("off", ["off", "off", "off", "off"]),
        ("auto", ["auto", "auto", "auto", "auto"]),
        ("on", ["on", "on", "on", "on"]),
    ),
)
def test_reasoning_profile_routes_per_stage(
    monkeypatch: pytest.MonkeyPatch,
    profile: str,
    expected: list[str],
) -> None:
    calls, _events = _install_transport(monkeypatch, _responses_for(1))

    _execute(
        mode="i2va",
        image=torch.zeros((1, 2, 2, 3)),
        reasoning=profile,
    )

    assert [call["reasoning"] for call in calls] == expected


def test_blank_native_model_is_resolved_once_and_reused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls, _events = _install_transport(monkeypatch, _responses_for(0))
    lookups: list[tuple] = []

    def resolve(*args):
        lookups.append(args)
        return "sole-loaded-model"

    monkeypatch.setattr(h3_module, "resolve_loaded_lm_studio_llm", resolve)

    _execute(model="")

    assert lookups == [("http://localhost.test/api/v1/chat", 300)]
    assert [call["model"] for call in calls] == [
        "sole-loaded-model",
        "sole-loaded-model",
    ]


def test_explicit_model_skips_discovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls, _events = _install_transport(monkeypatch, _responses_for(0))
    monkeypatch.setattr(
        h3_module,
        "resolve_loaded_lm_studio_llm",
        lambda *_args: pytest.fail("An explicit model must skip discovery."),
    )

    _execute(model=" explicit-model ")

    assert [call["model"] for call in calls] == [
        "explicit-model",
        "explicit-model",
    ]


@pytest.mark.parametrize(
    ("failure_index", "stage"),
    (
        (0, "Inventory"),
        (1, "Scope"),
        (2, "Planner"),
        (3, "Review"),
    ),
)
def test_provider_failures_have_stable_stage_prefixes(
    monkeypatch: pytest.MonkeyPatch,
    failure_index: int,
    stage: str,
) -> None:
    responses = _responses_for(1)
    calls = 0

    def request(**_kwargs):
        nonlocal calls
        index = calls
        calls += 1
        if index == failure_index:
            raise ValueError("provider unavailable")
        return responses[index], {"private": True}

    monkeypatch.setattr(h3_module, "request_local_chat_completion", request)
    monkeypatch.setattr(h3_module, "safe_send_sync", lambda *_args: None)

    with pytest.raises(ValueError) as raised:
        _execute(mode="i2va", image=torch.zeros((1, 2, 2, 3)))

    assert str(raised.value) == (
        f"{stage} stage failed: provider unavailable"
    )


def test_invalid_stage_json_and_compiler_errors_keep_own_stage_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _calls, _events = _install_transport(
        monkeypatch,
        ["not-json", _scope_response(1), _BASE_PLAN, _BASE_PLAN],
    )

    with pytest.raises(ValueError, match=r"^Inventory stage failed:"):
        _execute(mode="i2va", image=torch.zeros((1, 2, 2, 3)))

    _calls, _events = _install_transport(monkeypatch, _responses_for(0))
    monkeypatch.setattr(
        h3_module,
        "compile_h3_prompt_response",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            ValueError("semantic plan rejected")
        ),
    )

    with pytest.raises(ValueError) as raised:
        _execute(review=False)

    assert str(raised.value) == (
        "Compiler stage failed: semantic plan rejected"
    )


def test_model_resolution_failure_has_stable_prefix_and_skips_inference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        h3_module,
        "resolve_loaded_lm_studio_llm",
        lambda *_args: (_ for _ in ()).throw(ValueError("none loaded")),
    )
    monkeypatch.setattr(
        h3_module,
        "request_local_chat_completion",
        lambda **_kwargs: pytest.fail("Failed discovery must skip inference."),
    )
    monkeypatch.setattr(h3_module, "safe_send_sync", lambda *_args: None)

    with pytest.raises(ValueError) as raised:
        _execute(model="")

    assert str(raised.value) == "Model resolution stage failed: none loaded"


def _audit_failure(stage: str = "planner", *, verdict: str = "fail") -> str:
    return json.dumps({
        "verdict": verdict,
        "findings": [{
            "stage": stage,
            "path": "shots[0].description" if stage == "planner" else "pictures[0].facts[0]",
            "rule": "Preserve the original source ownership and requested action.",
            "evidence": "The candidate attributes the equipment to the wrong entity.",
            "correction": "Keep the equipment attached to its source entity.",
        }],
    })


@pytest.mark.parametrize("review", [False, [False]])
def test_review_opt_out_has_one_planner_call_and_keeps_format_validation(
    monkeypatch: pytest.MonkeyPatch, review,
) -> None:
    calls, events = _install_transport(monkeypatch, [_BASE_PLAN])

    result = _execute(review=review)

    assert len(calls) == 1
    assert result["result"][1]["review"] == {
        "enabled": False, "status": "skipped", "repaired_stage": None, "attempts": [],
    }
    assert [event[1]["stage"] for event in events] == ["planner", "compiler", "complete"]

    calls, _events = _install_transport(monkeypatch, ["not-json"])
    with pytest.raises(ValueError, match="^Compiler stage failed:"):
        _execute(review=review)
    assert len(calls) == 1


def test_image_review_opt_out_skips_audit_and_all_repair_requests(monkeypatch) -> None:
    calls, _events = _install_transport(monkeypatch, _responses_for(1)[:3])

    result = _execute(mode="i2va", image=torch.zeros((1, 2, 3, 3)), review=False)

    assert len(calls) == 3
    assert result["result"][1]["review"]["status"] == "skipped"


@pytest.mark.parametrize("review", ["false", "true", 0, 1, None, {}, []])
def test_review_requires_a_real_boolean_before_transport(monkeypatch, review) -> None:
    calls, _events = _install_transport(monkeypatch, [])

    with pytest.raises(ValueError, match="^Input validation stage failed: review"):
        _execute(review=review)
    assert not calls


def test_failed_planner_audit_repairs_once_then_rechecks_the_new_plan(monkeypatch) -> None:
    repaired = _BASE_PLAN.replace("glides", "moves")
    calls, events = _install_transport(
        monkeypatch, [_BASE_PLAN, _audit_failure(), repaired, _AUDIT_PASS]
    )

    result = _execute()

    assert len(calls) == 4
    repair_context = json.loads(calls[2]["prompt"])
    assert [call["max_tokens"] for call in calls] == [8192, 32768, 8192, 32768]
    assert [call["timeout"] for call in calls] == [300, 600, 300, 600]
    assert repair_context["previous_response_text"] == _BASE_PLAN
    assert repair_context["audit_findings"] == json.loads(_audit_failure())["findings"]
    assert "BOUNDED STAGE REPAIR" in calls[2]["system_message"]
    recheck = json.loads(calls[3]["prompt"])
    assert recheck["stages"][0]["response_text"] == repaired
    assert "moves" in result["result"][0]
    review = result["result"][1]["review"]
    assert review["repaired_stage"] == "planner"
    assert [item["verdict"] for item in review["attempts"]] == ["fail", "pass"]
    assert result["ui"]["lf_output"][0]["validation_report"]["review"] == review
    assert [event[1]["stage"] for event in events].count("repair") == 1


def test_compiler_failure_cannot_be_overridden_by_an_auditor_pass(monkeypatch) -> None:
    calls, _events = _install_transport(
        monkeypatch, ["not-json", _AUDIT_PASS, _BASE_PLAN, _AUDIT_PASS]
    )

    result = _execute()

    assert len(calls) == 4
    context = json.loads(calls[1]["prompt"])
    assert context["candidate_validation_error"]
    attempts = result["result"][1]["review"]["attempts"]
    assert attempts[0]["verdict"] == "fail"
    assert attempts[0]["findings"][-1]["evidence"] == context["candidate_validation_error"]
    assert attempts[-1]["verdict"] == "pass"


@pytest.mark.parametrize("verdict", ["fail", "uncertain"])
def test_unresolved_audit_stops_after_one_repair_with_findings_in_error(
    monkeypatch, verdict,
) -> None:
    failure = _audit_failure(verdict=verdict)
    calls, events = _install_transport(monkeypatch, [_BASE_PLAN, failure, _BASE_PLAN, failure])

    with pytest.raises(ValueError, match="^Review stage failed after one repair:") as error:
        _execute()

    assert len(calls) == 4
    assert "wrong entity" in str(error.value)
    assert f'"verdict": "{verdict}"' in str(error.value)
    assert not any(event[1].get("status") == "complete" for event in events)


@pytest.mark.parametrize("response", ["not-json", _BASE_PLAN, _audit_failure("inventory")])
def test_invalid_audit_does_not_trigger_repair_or_unreviewed_success(monkeypatch, response) -> None:
    calls, _events = _install_transport(monkeypatch, [_BASE_PLAN, response])

    with pytest.raises(ValueError, match="^Review stage failed:"):
        _execute()
    assert len(calls) == 2


@pytest.mark.parametrize("failed_stage", ["inventory", "scope"])
def test_upstream_review_repair_rebuilds_only_affected_downstream_stages(
    monkeypatch, failed_stage,
) -> None:
    responses = _responses_for(1)[:3] + [_audit_failure(failed_stage)]
    if failed_stage == "inventory":
        responses.append(_inventory_response(1))
    responses += [_scope_response(1), _BASE_PLAN, _AUDIT_PASS]
    calls, events = _install_transport(monkeypatch, responses)
    original = torch.zeros((1, 2, 3, 3))

    result = _execute(mode="i2va", image=original)

    expected_stages = ["inventory", "scope", "planner", "review", "repair"]
    if failed_stage == "inventory":
        expected_stages.append("inventory")
    expected_stages += ["scope", "planner", "review", "compiler", "complete"]
    assert [event[1]["stage"] for event in events] == expected_stages
    assert result["result"][1]["review"]["repaired_stage"] == failed_stage
    assert len(calls) == (8 if failed_stage == "inventory" else 7)
    for audit_index in (3, len(calls) - 1):
        assert torch.equal(calls[audit_index]["images"][0], original)
    assert json.loads(calls[4]["prompt"])["audit_findings"][0]["stage"] == failed_stage


def test_inventory_repair_refreshes_fact_ids_and_all_audit_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repaired_facts = ["The human wears armor.", "The panther has black fur."]
    repaired_observations = {
        "pictures": [{"picture": 1, "facts": repaired_facts}]
    }
    repaired_scope = {
        "pictures": [{
            "picture": 1,
            "decisions": [
                {"id": 1, "transfer": "allow"},
                {"id": 2, "transfer": "allow"},
            ],
        }]
    }
    # Deliberately reverse dependency order: the first finding is not the
    # earliest stage, and the repaired observation count differs from the old one.
    failure = {
        "verdict": "fail",
        "findings": [
            json.loads(_audit_failure(stage))["findings"][0]
            for stage in ("planner", "scope", "inventory")
        ],
    }
    repaired_plan = _BASE_PLAN.replace("glides", "moves")
    repaired_responses = [
        json.dumps(repaired_observations),
        json.dumps(repaired_scope),
        repaired_plan,
    ]
    calls, events = _install_transport(
        monkeypatch,
        _responses_for(1)[:3]
        + [json.dumps(failure)]
        + repaired_responses
        + [_AUDIT_PASS],
    )
    original = torch.arange(18, dtype=torch.float32).reshape(1, 2, 3, 3)

    result = _execute(mode="i2va", image=original)

    assert len(calls) == 8
    assert [event[1]["stage"] for event in events] == [
        "inventory", "scope", "planner", "review", "repair",
        "inventory", "scope", "planner", "review", "compiler", "complete",
    ]
    review = result["result"][1]["review"]
    assert review["repaired_stage"] == "inventory"
    assert [attempt["verdict"] for attempt in review["attempts"]] == ["fail", "pass"]
    assert json.loads(calls[4]["prompt"])["previous_response_text"] == _inventory_response(1)

    scope_context = json.loads(calls[5]["prompt"])
    assert scope_context["visual_observations"] == {
        "pictures": [{
            "picture": 1,
            "facts": [
                {"id": 1, "fact": repaired_facts[0]},
                {"id": 2, "fact": repaired_facts[1]},
            ],
        }]
    }
    planner_context = json.loads(calls[6]["prompt"])
    assert planner_context["visual_inventory"] == {
        "pictures": [{"picture": 1, "allowed_facts": repaired_facts}]
    }

    recheck = json.loads(calls[7]["prompt"])
    assert recheck["visual_observations"] == repaired_observations
    expected_inventory = {
        "pictures": [{
            "picture": 1,
            "facts": [{"fact": fact, "transfer": "allow"} for fact in repaired_facts],
        }]
    }
    assert recheck["visual_inventory"] == expected_inventory
    assert recheck["candidate_validation_error"] is None
    assert recheck["stages"] == [
        {
            "stage": stage,
            "system_message": calls[index]["system_message"],
            "prompt": calls[index]["prompt"],
            "response_text": response,
        }
        for stage, index, response in zip(
            ("inventory", "scope", "planner"), (4, 5, 6), repaired_responses, strict=True
        )
    ]
    assert result["result"][2] == expected_inventory
    assert "moves" in result["result"][0]
    for index in (0, 3, 4, 7):
        assert len(calls[index]["images"]) == 1
        assert torch.equal(calls[index]["images"][0], original)
    assert all(calls[index]["images"] == [] for index in (1, 2, 5, 6))


def test_auditor_sees_forbidden_facts_not_only_planner_projection(monkeypatch) -> None:
    observations = json.dumps({"pictures": [{"picture": 1, "facts": [
        "The animal has blue eyes.", "The person carries a quiver."
    ]}]})
    scope = json.dumps({"pictures": [{"picture": 1, "decisions": [
        {"id": 1, "transfer": "allow"}, {"id": 2, "transfer": "forbid"}
    ]}]})
    # Ref2VA is necessary here: concrete keyframe modes deliberately allow all facts.
    plan = json.dumps({
        "style_lead": "Naturalistic photography.", "summary": "An animal waits.",
        "subjects": [{
            "definition": "The blue-eyed animal", "source_pictures": [1],
            "uses": [{"shot": 1, "application": "waits in view"}],
            "retention": {"marker": "fully_preserved", "rationale": "Its blue eyes remain visible."}
        }], "picture_anchors": [],
        "shots": [{"start_seconds": 0, "description": "The animal waits quietly.", "dialogue": []}],
        "overall_soundscape": "Quiet breathing.", "non_diegetic_music": "N/A",
    })
    calls, _events = _install_transport(monkeypatch, [observations, scope, plan, _AUDIT_PASS])

    _execute(mode="ref2va", image=torch.zeros((1, 2, 3, 3)))

    planner = json.loads(calls[2]["prompt"])
    audit = json.loads(calls[3]["prompt"])
    assert "quiver" not in json.dumps(planner["visual_inventory"])
    assert audit["visual_inventory"]["pictures"][0]["facts"][1] == {
        "fact": "The person carries a quiver.", "transfer": "forbid"
    }
