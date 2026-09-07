"""Focused contracts for the decomposed MiniMax H3 prompt pipeline."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Callable

import pytest

from modules.workflow_runner.prompts.minimax_h3 import compile_h3_prompt_response
from modules.workflow_runner.prompts.minimax_h3_pipeline import (
    build_h3_planner_context,
    build_h3_prompt_planner_system,
    build_h3_prompt_reviewer_system,
    build_h3_review_context,
    build_h3_scope_classifier_system,
    build_h3_scope_context,
    build_h3_visual_inventory_system,
)


def _picture(picture: int) -> dict[str, Any]:
    facts = [
        {"fact": f"observable feature {picture}", "transfer": "allow"},
        {"fact": "cool blue light", "transfer": "forbid"},
    ]
    if picture == 4:
        facts.extend(
            [
                {"fact": "purple banner", "transfer": "forbid"},
                {"fact": "partially hidden insignia", "transfer": "uncertain"},
            ]
        )
    return {"picture": picture, "facts": facts}


def _inventory(count: int = 4) -> dict[str, Any]:
    return {"pictures": [_picture(ordinal) for ordinal in range(1, count + 1)]}


def _observations(count: int = 4) -> dict[str, Any]:
    return {
        "pictures": [
            {
                "picture": picture["picture"],
                "facts": [fact["fact"] for fact in picture["facts"]],
            }
            for picture in _inventory(count)["pictures"]
        ]
    }


def _scope(count: int = 4) -> dict[str, Any]:
    return {
        "pictures": [
            {
                "picture": picture["picture"],
                "decisions": [
                    {"id": index, "transfer": fact["transfer"]}
                    for index, fact in enumerate(picture["facts"], start=1)
                ],
            }
            for picture in _inventory(count)["pictures"]
        ]
    }


def _allowed_inventory(count: int = 4) -> dict[str, Any]:
    return {
        "pictures": [
            {
                "picture": ordinal,
                "allowed_facts": [f"observable feature {ordinal}"],
            }
            for ordinal in range(1, count + 1)
        ]
    }


def _valid_reference_plan(count: int = 4) -> dict[str, Any]:
    return {
        "style_lead": "Naturalistic fantasy portraiture in cool cathedral light.",
        "summary": "Keep the sentinel recognizable throughout the motion.",
        "subjects": [
            {
                "definition": "The sentinel described by the allowed references",
                "source_pictures": list(range(1, count + 1)),
                "uses": [
                    {
                        "shot": 1,
                        "application": "stands alert in the quiet chamber",
                    }
                ],
                "retention": {
                    "marker": "fully_preserved",
                    "rationale": "The permitted identity traits remain stable.",
                },
            }
        ],
        "picture_anchors": [],
        "shots": [
            {
                "start_seconds": 0,
                "description": (
                    "A slow camera push follows the sentinel as cold window light "
                    "crosses the chamber and cloth rustles with the movement."
                ),
                "dialogue": [],
            }
        ],
        "overall_soundscape": "Quiet room tone and softly moving cloth.",
        "non_diegetic_music": "N/A",
    }


def _scope_context(
    response_text: str,
    *,
    mode: str = "ref2va",
    references: int = 4,
) -> tuple[str, dict[str, Any]]:
    return build_h3_scope_context(
        response_text,
        "Preserve the sentinel’s face; never copy the purple banner. 🫡",
        mode,
        15,
        references,
    )


def _planner_context(
    response_text: str,
    *,
    observations: dict[str, Any] | None = None,
    mode: str = "ref2va",
    references: int = 4,
) -> tuple[str, dict[str, Any]]:
    return build_h3_planner_context(
        response_text,
        _observations(references) if observations is None else observations,
        "Preserve the sentinel’s face; never copy the purple banner. 🫡",
        mode,
        15,
        references,
    )


def test_stage_systems_separate_observation_scope_planning_and_review() -> None:
    inventory = build_h3_visual_inventory_system("ref2va", 15, 4)
    scope = build_h3_scope_classifier_system("ref2va", 15, 4)
    planner = build_h3_prompt_planner_system("ref2va", 15, 4)
    reviewer = build_h3_prompt_reviewer_system("ref2va", 15, 4)

    assert "Mode: ref2va" in inventory
    assert "15.00" in inventory
    assert '"pictures"' in inventory
    assert "facts" in inventory
    assert "transfer policy" in inventory
    assert "start_seconds" not in inventory

    assert "15.00" in scope
    assert all(
        field in scope for field in ("picture", "decisions", "id", "transfer")
    )
    assert all(value in scope for value in ("allow", "forbid", "uncertain"))
    assert "no images" in scope.casefold()

    assert "15.00" in planner
    assert "visual_inventory" in planner
    assert "allowed_facts" in planner
    assert "start_seconds" in planner

    reviewer_lower = reviewer.casefold()
    assert "candidate" in reviewer_lower
    assert "candidate_validation_error" in reviewer
    assert "repair that reported defect first" in reviewer_lower
    assert "analogous occurrence" in reviewer_lower
    assert "allowed_facts" in reviewer_lower
    assert "dialogue" in reviewer_lower
    assert "350" in reviewer and "500" in reviewer


def test_stage_systems_do_not_seed_copyable_semantic_exemplars() -> None:
    systems = (
        build_h3_visual_inventory_system("ref2va", 15, 4),
        build_h3_scope_classifier_system("ref2va", 15, 4),
        build_h3_prompt_planner_system("ref2va", 15, 4),
        build_h3_prompt_reviewer_system("ref2va", 15, 4),
    )
    copied_fingerprints = (
        "wide opening composition establishes",
        "the principal visible subject",
        "remains the central visual subject",
        "anchors the final framing",
        "defining visible features remain stable",
        "whispers softly",
    )
    for system in systems:
        lowered = system.casefold()
        assert all(fingerprint not in lowered for fingerprint in copied_fingerprints)


@pytest.mark.parametrize(
    "builder",
    (build_h3_prompt_planner_system, build_h3_prompt_reviewer_system),
)
def test_ref2va_stages_distinguish_reusable_subjects_from_explicit_anchors(
    builder: Callable[[str, float, int], str],
) -> None:
    contract = builder("ref2va", 6, 4)

    assert "subjects represent reusable visible content, not source files" in contract
    assert "do not substitute a picture_anchors entry" in contract
    assert "An environment reference alone is not a composition anchor" in contract
    assert "creative_intent explicitly assigns" in contract
    assert "represent both roles" in contract
    assert "subjects may be empty only" in contract
    assert "no reusable content is independently tracked" in contract
    assert "return subjects: []" in contract
    assert "Only reference-derived content belongs in subjects" in contract
    assert "never invent source provenance" in contract
    assert "One image may supply multiple distinct subjects" in contract
    assert "which source supplies each part" in contract
    assert "Keep every trait attached to its owning entity" in contract


@pytest.mark.parametrize(
    "builder",
    (build_h3_prompt_planner_system, build_h3_prompt_reviewer_system),
)
@pytest.mark.parametrize(
    ("mode", "references"),
    (("t2va", 0), ("i2va", 1), ("fl2va", 2), ("l2va", 1)),
)
def test_base_stages_do_not_require_ref2va_subject_planning(
    builder: Callable[[str, float, int], str],
    mode: str,
    references: int,
) -> None:
    contract = builder(mode, 6, references)

    assert "Reference-role rules:" not in contract
    assert "The output has exactly these top-level keys: shots," in contract


def test_planner_separates_reference_evidence_from_requested_new_content() -> None:
    contract = build_h3_prompt_planner_system("ref2va", 6, 1)

    assert "sole authority for reference-derived visual claims" in contract
    assert "creative_intent is authoritative for requested new content" in contract
    assert "A reference-derived detail absent from allowed_facts is unavailable" in contract
    assert "the sole authority for visual claims" not in contract
    assert "A visual detail absent from allowed_facts is unavailable" not in contract


def test_prompts_cover_observed_qwen_ceiling_failures() -> None:
    scope = build_h3_scope_classifier_system("ref2va", 15, 4).casefold()
    planner = build_h3_prompt_planner_system("ref2va", 15, 4).casefold()
    reviewer = build_h3_prompt_reviewer_system("ref2va", 15, 4).casefold()

    assert "closed-world" in scope
    assert "composition_reference" in scope
    assert "banner" in scope and "symbol" in scope
    for contract in (planner, reviewer):
        assert "one subject" in contract
        assert "screen entity" in contract
        assert "source_pictures" in contract
        assert "splitting" in contract
        assert "face" in contract and "body" in contract
        assert "hand" in contract
        assert "equipment" in contract
        assert "prop" in contract
        assert "visible reaction" in contract
        assert "acknowledgment" in contract
        assert "causal action" in contract
        assert "physical sound" in contract
        assert "screen-direction" in contract or "screen direction" in contract
        assert "dialogue" in contract
        assert "diegetic sound" in contract
        assert "music" in contract
        assert "350" in contract and "500" in contract
        assert "400" in contract and "450" in contract
        assert "visual treatment only" in contract
        assert "exactly one or two sentences" in contract
        assert "never an array of integers" in contract
        assert "empty uses arrays are forbidden" in contract
        assert "must cover every shot" in contract
        assert "never create placeholder dialogue objects" in contract
        assert "a requested single shot has exactly one entry" in contract
    assert "every explicit must" in planner
    assert "every explicit user negative" in planner
    assert "assertions do not count" in planner
    assert "every explicit user negative" in reviewer
    assert "never assertions" in reviewer
    assert "unsupported visual claims" in reviewer


def test_observation_prompt_requires_dense_atomic_pixel_facts() -> None:
    prompt = build_h3_visual_inventory_system("ref2va", 15, 4).casefold()

    assert "atomic" in prompt
    assert "eight to sixteen" in prompt
    assert "pose" in prompt
    assert "spatial relation" in prompt
    assert "banner" in prompt and "symbol" in prompt
    assert "do not omit" in prompt
    assert "without deciding" in prompt


def test_scope_prompt_requires_one_closed_world_decision_per_fact_id() -> None:
    prompt = build_h3_scope_classifier_system("ref2va", 15, 4).casefold()

    assert "repeat every supplied fact id once" in prompt
    assert "add none and omit none" in prompt
    assert "only as closed-world scope" in prompt
    assert "every fact outside" in prompt
    assert "composition_reference" in prompt


@pytest.mark.parametrize(
    ("mode", "references", "required_text"),
    (
        ("t2va", 0, "empty pictures array"),
        ("i2va", 1, "concrete first frame"),
        ("fl2va", 2, "picture 1 is the concrete first frame"),
        ("l2va", 1, "concrete last frame"),
        ("ref2va", 1, "only from creative_intent"),
    ),
)
def test_scope_prompt_carries_the_fixed_mode_role_rule(
    mode: str,
    references: int,
    required_text: str,
) -> None:
    prompt = build_h3_scope_classifier_system(mode, 15, references).casefold()

    assert required_text in prompt


@pytest.mark.parametrize(
    "wrapper",
    (
        lambda value: value,
        lambda value: f"```json\n{value}\n```",
        lambda value: f"```\n{value}\n```",
    ),
)
def test_scope_context_accepts_one_bare_or_fenced_observation_document(
    wrapper: Callable[[str], str],
) -> None:
    expected = _observations()
    context_text, observations = _scope_context(
        wrapper(json.dumps(expected, ensure_ascii=False))
    )
    context = json.loads(context_text)

    assert observations == expected
    assert list(context) == [
        "mode",
        "duration_seconds",
        "creative_intent",
        "visual_observations",
    ]
    assert context["visual_observations"]["pictures"][0]["facts"] == [
        {"id": 1, "fact": "observable feature 1"},
        {"id": 2, "fact": "cool blue light"},
    ]
    assert "sentinel’s" in context_text and "🫡" in context_text


@pytest.mark.parametrize(
    "wrapper",
    (
        lambda value: value,
        lambda value: f"```json\n{value}\n```",
        lambda value: f"```\n{value}\n```",
    ),
)
def test_planner_context_accepts_scope_and_returns_full_ledger(
    wrapper: Callable[[str], str],
) -> None:
    context_text, inventory = _planner_context(
        wrapper(json.dumps(_scope(), ensure_ascii=False))
    )
    context = json.loads(context_text)

    assert inventory == _inventory()
    assert list(context) == [
        "mode",
        "duration_seconds",
        "creative_intent",
        "visual_inventory",
    ]
    assert context["visual_inventory"] == _allowed_inventory()


def test_text_only_pipeline_uses_canonical_empty_documents() -> None:
    scope_text, observations = _scope_context(
        '{"pictures": []}',
        mode="t2va",
        references=0,
    )
    planner_text, inventory = _planner_context(
        '{"pictures": []}',
        observations=observations,
        mode="t2va",
        references=0,
    )

    assert observations == {"pictures": []}
    assert inventory == {"pictures": []}
    assert json.loads(scope_text)["visual_observations"] == {"pictures": []}
    assert json.loads(planner_text)["visual_inventory"] == {"pictures": []}


def test_review_context_is_sanitized_and_preserves_candidate_bytes() -> None:
    candidate = "  ```json\n{\"shots\": [], \"note\": \"l’eroina 🫡\"}\n```  "
    context_text = build_h3_review_context(
        candidate,
        _inventory(),
        "Keep the exact quoted line: “Go.”",
        "ref2va",
        15,
    )
    context = json.loads(context_text)

    assert list(context) == [
        "mode",
        "duration_seconds",
        "creative_intent",
        "visual_inventory",
        "candidate_plan_text",
        "candidate_validation_error",
    ]
    assert context["visual_inventory"] == _allowed_inventory()
    assert context["candidate_plan_text"] == candidate
    with pytest.raises((TypeError, ValueError)) as compiler_error:
        compile_h3_prompt_response(candidate, "ref2va", 15, 4)
    assert context["candidate_validation_error"] == str(compiler_error.value)
    assert "l’eroina" in context_text and "🫡" in context_text
    assert "partially hidden insignia" not in context_text


def test_review_context_reports_null_for_a_compiler_valid_candidate() -> None:
    candidate = json.dumps(_valid_reference_plan(), ensure_ascii=False)

    context = json.loads(
        build_h3_review_context(
            candidate,
            _inventory(),
            "Keep the sentinel recognizable. 🫡",
            "ref2va",
            15,
        )
    )

    assert context["candidate_plan_text"] == candidate
    assert context["candidate_validation_error"] is None


def test_review_context_reports_the_exact_compiler_validation_error() -> None:
    invalid_plan = _valid_reference_plan()
    invalid_plan["subjects"][0]["uses"] = []
    candidate = json.dumps(invalid_plan)

    with pytest.raises(ValueError) as compiler_error:
        compile_h3_prompt_response(candidate, "ref2va", 15, 4)
    context = json.loads(
        build_h3_review_context(
            candidate,
            _inventory(),
            "Keep the sentinel recognizable.",
            "ref2va",
            15,
        )
    )

    assert str(compiler_error.value) == "Semantic plan subjects[0].uses must not be empty"
    assert context["candidate_validation_error"] == str(compiler_error.value)


@pytest.mark.parametrize(
    ("response", "message"),
    (
        ("", "empty|JSON"),
        ("[]", "object"),
        ('{"pictures": [], "extra": true}', "unexpected|extra"),
        ("{}", "missing|pictures"),
        ('{"pictures": {}}', "array|list"),
        ('before\n```json\n{"pictures": []}\n```', "bare|only one|JSON"),
        ('{"pictures": [], "pictures": []}', "repeat|duplicate"),
    ),
)
def test_stage_documents_are_one_unambiguous_exact_json_object(
    response: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _scope_context(response, mode="t2va", references=0)


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        (lambda value: value["pictures"][0].pop("facts"), "missing|facts"),
        (
            lambda value: value["pictures"][0].update({"extra": True}),
            "unexpected|extra",
        ),
        (
            lambda value: value["pictures"][0].update({"picture": "1"}),
            "integer",
        ),
        (
            lambda value: value["pictures"][0].update({"picture": True}),
            "integer",
        ),
        (
            lambda value: value["pictures"][0].update({"facts": "armor"}),
            "facts.*array|facts.*list",
        ),
        (
            lambda value: value["pictures"][0].update({"facts": []}),
            "facts.*empty",
        ),
        (
            lambda value: value["pictures"][0].update({"facts": [" "]}),
            "facts.*blank|facts.*empty",
        ),
        (
            lambda value: value["pictures"][0].update({"facts": [7]}),
            "facts.*string",
        ),
        (
            lambda value: value["pictures"][0].update(
                {"facts": ["blue armor", " Blue Armor "]}
            ),
            "facts.*repeat",
        ),
    ),
)
def test_observation_picture_schema_is_exact(
    mutation: Callable[[dict[str, Any]], object],
    message: str,
) -> None:
    values = _observations()
    mutation(values)
    with pytest.raises(ValueError, match=message):
        _scope_context(json.dumps(values))


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        (lambda value: value["pictures"][0].pop("decisions"), "missing|decisions"),
        (
            lambda value: value["pictures"][0].update({"roles": []}),
            "unexpected|roles",
        ),
        (
            lambda value: value["pictures"][0].update({"decisions": {}}),
            "decisions.*array",
        ),
        (
            lambda value: value["pictures"][0]["decisions"].pop(),
            "classify exactly",
        ),
        (
            lambda value: value["pictures"][0]["decisions"][0].update({"id": True}),
            "id.*integer",
        ),
        (
            lambda value: value["pictures"][0]["decisions"][0].update({"id": 2}),
            "id.*must be 1",
        ),
        (
            lambda value: value["pictures"][0]["decisions"][0].update(
                {"transfer": "allowed"}
            ),
            "transfer.*exactly",
        ),
        (
            lambda value: value["pictures"][0]["decisions"][0].pop("transfer"),
            "missing|transfer",
        ),
        (
            lambda value: value["pictures"][0]["decisions"][0].update(
                {"extra": True}
            ),
            "unexpected|extra",
        ),
    ),
)
def test_scope_decision_schema_is_complete_and_id_bound(
    mutation: Callable[[dict[str, Any]], object],
    message: str,
) -> None:
    values = _scope()
    mutation(values)
    with pytest.raises(ValueError, match=message):
        _planner_context(json.dumps(values))


@pytest.mark.parametrize(
    ("pictures", "references", "message"),
    (
        (
            [_observations(2)["pictures"][1], _observations(2)["pictures"][0]],
            2,
            "must be 1",
        ),
        ([_observations(1)["pictures"][0]], 2, "exactly 2"),
        (_observations(3)["pictures"], 2, "exactly 2"),
    ),
)
def test_observation_ordinals_are_complete_and_in_attachment_order(
    pictures: list[dict[str, Any]],
    references: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _scope_context(json.dumps({"pictures": pictures}), references=references)


@pytest.mark.parametrize(
    ("pictures", "message"),
    (
        (
            [
                _scope(4)["pictures"][1],
                _scope(4)["pictures"][0],
                _scope(4)["pictures"][2],
                _scope(4)["pictures"][3],
            ],
            "must be 1",
        ),
        ([_scope(1)["pictures"][0]], "exactly 4"),
        (_scope(4)["pictures"] + [_scope(1)["pictures"][0]], "exactly 4"),
    ),
)
def test_scope_picture_ordinals_and_count_match_observations(
    pictures: list[dict[str, Any]],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _planner_context(json.dumps({"pictures": pictures}))


def test_planner_projection_hides_forbidden_and_uncertain_facts() -> None:
    context_text, inventory = _planner_context(json.dumps(_scope()))
    planner_inventory = json.loads(context_text)["visual_inventory"]
    planner_inventory_text = json.dumps(planner_inventory)

    assert inventory == _inventory()
    assert planner_inventory == _allowed_inventory()
    assert "cool blue light" not in planner_inventory_text
    assert "purple banner" not in planner_inventory_text
    assert "partially hidden insignia" not in planner_inventory_text
    assert "forbid" not in planner_inventory_text
    assert "uncertain" not in planner_inventory_text


def test_picture_with_no_allowed_facts_is_rejected() -> None:
    scope = _scope(1)
    for decision in scope["pictures"][0]["decisions"]:
        decision["transfer"] = "forbid"

    with pytest.raises(ValueError, match="allow at least one|lawful H3"):
        _planner_context(
            json.dumps(scope),
            observations=_observations(1),
            references=1,
        )


@pytest.mark.parametrize("mode", ("i2va", "fl2va", "l2va"))
@pytest.mark.parametrize("transfer", ("forbid", "uncertain"))
def test_fixed_frame_modes_require_every_boundary_fact_to_be_allowed(
    mode: str,
    transfer: str,
) -> None:
    references = 2 if mode == "fl2va" else 1
    scope = _scope(references)
    for picture in scope["pictures"]:
        for decision in picture["decisions"]:
            decision["transfer"] = "allow"
    scope["pictures"][-1]["decisions"][-1]["transfer"] = transfer

    with pytest.raises(ValueError, match="must be allow.*boundary-frame fact"):
        _planner_context(
            json.dumps(scope),
            observations=_observations(references),
            mode=mode,
            references=references,
        )


@pytest.mark.parametrize("mode", ("i2va", "fl2va", "l2va"))
def test_fixed_frame_modes_accept_a_complete_all_allowed_boundary_ledger(
    mode: str,
) -> None:
    references = 2 if mode == "fl2va" else 1
    scope = _scope(references)
    for picture in scope["pictures"]:
        for decision in picture["decisions"]:
            decision["transfer"] = "allow"

    _, inventory = _planner_context(
        json.dumps(scope),
        observations=_observations(references),
        mode=mode,
        references=references,
    )

    assert all(
        fact["transfer"] == "allow"
        for picture in inventory["pictures"]
        for fact in picture["facts"]
    )


def test_observation_whitespace_is_canonicalized_before_id_binding() -> None:
    observations = _observations(1)
    observations["pictures"][0]["facts"][0] = "  observable   feature 1  "
    scope_text, canonical = _scope_context(
        json.dumps(observations),
        references=1,
    )

    assert canonical["pictures"][0]["facts"][0] == "observable feature 1"
    assert json.loads(scope_text)["visual_observations"]["pictures"][0][
        "facts"
    ][0] == {"id": 1, "fact": "observable feature 1"}


def test_inventory_and_context_size_limits_fail_closed() -> None:
    oversized = _observations(1)
    oversized["pictures"][0]["facts"][0] = "x" * 1_000_000
    with pytest.raises(ValueError, match="maximum|exceed|large"):
        _scope_context(json.dumps(oversized), references=1)

    with pytest.raises(ValueError, match="maximum|exceed|large"):
        build_h3_scope_context(
            json.dumps(_observations()),
            "x" * 1_000_000,
            "ref2va",
            15,
            4,
        )
    with pytest.raises(ValueError, match="maximum|exceed|large"):
        build_h3_review_context(
            "x" * 1_000_000,
            _inventory(),
            "A concise intent.",
            "ref2va",
            15,
        )


def test_observation_fact_lists_are_bounded() -> None:
    values = _observations(1)
    values["pictures"][0]["facts"] = [f"feature {index}" for index in range(25)]
    with pytest.raises(ValueError, match="facts.*24|facts.*more than"):
        _scope_context(json.dumps(values), references=1)


@pytest.mark.parametrize(
    ("mode", "duration", "references", "error_type", "message"),
    (
        ("unknown", 15, 4, ValueError, "mode"),
        ("ref2va", 0, 4, ValueError, "duration"),
        ("ref2va", float("nan"), 4, ValueError, "duration"),
        ("ref2va", 15, 0, ValueError, "between 1 and 9|reference"),
        ("t2va", 15, 1, ValueError, "exactly 0|reference"),
        ("ref2va", True, 4, TypeError, "duration"),
        ("ref2va", 15, True, TypeError, "reference"),
    ),
)
def test_pipeline_request_contract_is_strict(
    mode: str,
    duration: object,
    references: object,
    error_type: type[Exception],
    message: str,
) -> None:
    for builder in (
        build_h3_visual_inventory_system,
        build_h3_scope_classifier_system,
        build_h3_prompt_planner_system,
        build_h3_prompt_reviewer_system,
    ):
        with pytest.raises(error_type, match=message):
            builder(mode, duration, references)  # type: ignore[arg-type]

    with pytest.raises(error_type, match=message):
        build_h3_scope_context(
            json.dumps(_observations()),
            "A valid intent.",
            mode,
            duration,  # type: ignore[arg-type]
            references,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("field", "value", "error_type", "message"),
    (
        ("candidate", None, TypeError, "candidate"),
        ("candidate", "  ", ValueError, "candidate"),
        ("inventory", [], TypeError, "inventory|object"),
        ("intent", None, TypeError, "intent"),
        ("intent", " ", ValueError, "intent"),
    ),
)
def test_review_context_rejects_invalid_values(
    field: str,
    value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    kwargs: dict[str, Any] = {
        "candidate_plan": '{"shots": []}',
        "visual_inventory": deepcopy(_inventory()),
        "creative_intent": "A valid intent.",
        "mode": "ref2va",
        "duration_seconds": 15,
    }
    kwargs[
        {
            "candidate": "candidate_plan",
            "inventory": "visual_inventory",
            "intent": "creative_intent",
        }[field]
    ] = value
    with pytest.raises(error_type, match=message):
        build_h3_review_context(**kwargs)


def test_review_context_revalidates_full_ledger() -> None:
    inventory = _inventory()
    inventory["pictures"][3]["facts"].append(
        {"fact": " Purple Banner ", "transfer": "allow"}
    )
    with pytest.raises(ValueError, match="facts.*repeat"):
        build_h3_review_context(
            '{"candidate": true}',
            inventory,
            "A valid intent.",
            "ref2va",
            15,
        )
