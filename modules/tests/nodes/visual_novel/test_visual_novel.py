"""Contract tests for LF Nodes' target-neutral visual-novel primitives."""

from __future__ import annotations

import json

import pytest

from modules.nodes.visual_novel.compile import LF_VNCompile
from modules.nodes.visual_novel.contracts import Input
from modules.nodes.visual_novel.core import (
    BUNDLE_SCHEMA,
    GRAPH_SCHEMA,
    PREVIEW_SCHEMA,
    STATE_SCHEMA,
    VALIDATION_SCHEMA,
    VNContractError,
    append_declaration,
    build_scene_declaration,
    build_switch_declaration,
    canonical_json,
    compile_graph,
    evaluate_predicate,
    evaluate_switch,
    make_state,
    normalize_bundle,
    preview_bundle,
    strict_json_loads,
)
from modules.nodes.visual_novel.scene_spec import LF_SceneSpec
from modules.nodes.visual_novel.state import LF_VNState
from modules.nodes.visual_novel.switch import LF_VNSwitch


def _scene(
    scene_id: str,
    *,
    entry_predicate: dict | None = None,
    choices: list[dict] | None = None,
    node_id: str = "1",
) -> dict:
    return build_scene_declaration(
        scene_id=scene_id,
        title=scene_id,
        participants=["actor.guide"],
        entry_predicate=entry_predicate or {},
        beats=[
            {
                "id": f"{scene_id}.beat.1",
                "speaker": "actor.guide",
                "text": f"Beat for {scene_id}",
            }
        ],
        choices=choices or [],
        art_requests=[],
        source_node_id=node_id,
    )


def _story_graph(*, dangling: bool = False) -> dict:
    target = "scene.missing" if dangling else "scene.follow-up"
    graph = append_declaration(
        None,
        _scene(
            "scene.opening",
            choices=[
                {
                    "id": "choice.answer",
                    "label": "Answer the signal",
                    "availabilityPredicate": {
                        "gte": {"path": "/trust", "value": 40}
                    },
                    "effects": [
                        {
                            "id": "effect.signal-answered",
                            "type": "lf.marker.set",
                            "payload": {"id": "signal.answered"},
                        }
                    ],
                    "nextSceneId": target,
                }
            ],
        ),
    )
    return append_declaration(
        graph,
        _scene(
            "scene.follow-up",
            entry_predicate={"has-marker": "signal.answered"},
            node_id="2",
        ),
    )


def _state(trust: int = 52) -> dict:
    return make_state(
        profile_id="example.signal",
        fixture_id=f"fixture.trust-{trust}",
        values={"trust": trust, "markers": []},
    )


def _scene_body(*, choices: list[dict] | None = None) -> str:
    """Return the serialized authoring body used by Scene Spec."""

    return json.dumps(
        {
            "participants": ["actor.guide"],
            "entryPredicate": {},
            "beats": [
                {
                    "id": "scene.opening.beat.1",
                    "speaker": "actor.guide",
                    "text": "Hello.",
                }
            ],
            "choices": choices or [],
            "artRequests": [],
        }
    )


class TestStrictJSONBoundary:
    @pytest.mark.parametrize(
        "raw",
        [
            '{"choice":1,"choice":2}',
            '{"value":NaN}',
            '{"value":Infinity}',
            '{"value":-Infinity}',
            '{"value":',
        ],
    )
    def test_rejects_ambiguous_or_non_json_input(self, raw):
        with pytest.raises(VNContractError):
            strict_json_loads(raw, label="payload")

    def test_preserves_finite_json_types(self):
        parsed = strict_json_loads(
            '{"n":2,"ok":true,"items":["a",null]}',
            label="payload",
            expected_type=dict,
        )
        assert parsed == {"n": 2, "ok": True, "items": ["a", None]}


class TestStateAndPredicates:
    def test_node_input_contracts_use_typed_ids_refs_and_real_textarea_bodies(self):
        state_inputs = LF_VNState.INPUT_TYPES()
        assert state_inputs["required"]["fixture_id"][0] == Input.LF_ID
        assert state_inputs["required"]["state_body"][0] == Input.LF_TEXTAREA
        assert state_inputs["optional"]["profile_ref"][0] == Input.LF_REF

        scene_inputs = LF_SceneSpec.INPUT_TYPES()
        assert scene_inputs["required"]["scene_id"][0] == Input.LF_ID
        assert scene_inputs["required"]["title"][0] == Input.STRING
        assert scene_inputs["required"]["scene_body"][0] == Input.LF_TEXTAREA

        switch_inputs = LF_VNSwitch.INPUT_TYPES()
        assert switch_inputs["required"]["switch_id"][0] == Input.LF_ID
        assert switch_inputs["required"]["switch_body"][0] == Input.LF_TEXTAREA

        compile_inputs = LF_VNCompile.INPUT_TYPES()["required"]
        assert compile_inputs["workflow_id"][0] == Input.LF_ID
        assert compile_inputs["entry_scene_id"][0] == Input.LF_REF
        assert compile_inputs["selected_choice_id"][0] == Input.LF_REF

    def test_state_node_emits_a_neutral_versioned_envelope(self):
        state, generic_json, serialized = LF_VNState().on_exec(
            fixture_id="fixture.curious",
            profile_ref="example.profile",
            state_body='{"trust":52,"markers":[]}',
            node_id="9",
        )

        assert state == generic_json
        assert state == {
            "schema": STATE_SCHEMA,
            "profileId": "example.profile",
            "fixtureId": "fixture.curious",
            "values": {"trust": 52, "markers": []},
            "appliedEffectIds": [],
        }
        assert json.loads(serialized) == state
        assert "standing" not in serialized
        assert "leader" not in serialized

    def test_state_missing_fixture_id_fails_closed_with_structured_error(self):
        with pytest.raises(VNContractError) as error:
            LF_VNState().on_exec(state_body='{"markers":[]}', node_id="9")

        payload = error.value.payload
        assert payload["status"] == "blocked"
        assert payload["errors"][0]["code"] == "missing_semantic_id"
        assert payload["errors"][0]["path"] == "/fixtureId"

    @pytest.mark.parametrize("bad_id", [None, 7, " fixture.curious "])
    def test_state_does_not_coerce_semantic_ids(self, bad_id):
        with pytest.raises(VNContractError) as error:
            LF_VNState().on_exec(
                fixture_id=bad_id,
                state_body='{"markers":[]}',
                node_id="9",
            )

        assert error.value.payload["errors"][0]["code"] in {
            "missing_semantic_id",
            "invalid_semantic_id",
        }

    @pytest.mark.parametrize("bad_ref", [None, 7, " example.profile "])
    def test_optional_profile_ref_only_accepts_exact_empty_string_as_absent(self, bad_ref):
        with pytest.raises(VNContractError) as error:
            LF_VNState().on_exec(
                fixture_id="fixture.curious",
                profile_ref=bad_ref,
                state_body='{"markers":[]}',
                node_id="9",
            )

        assert error.value.payload["errors"][0]["path"] == "/profileId"

    def test_optional_profile_ref_is_not_required_or_fabricated(self):
        state, _, _ = LF_VNState().on_exec(
            fixture_id="fixture.curious",
            state_body='{"markers":[]}',
            node_id="9",
        )

        assert "profileId" not in state

    def test_json_pointer_predicates_are_nested_and_rfc6901_aware(self):
        values = {
            "relationship": {"trust": 52},
            "facts": {"signal/seen": True},
            "markers": ["intro.seen"],
        }
        predicate = {
            "all": [
                {"gte": {"path": "/relationship/trust", "value": 40}},
                {"eq": {"path": "/facts/signal~1seen", "value": True}},
                {"has-marker": "intro.seen"},
            ]
        }

        matched, trace = evaluate_predicate(predicate, values)
        assert matched is True
        assert trace["operator"] == "all"
        assert all(item["matched"] for item in trace["items"])

    def test_missing_path_fails_closed_with_a_trace(self):
        matched, trace = evaluate_predicate(
            {"eq": {"path": "/missing", "value": True}},
            {},
        )
        assert matched is False
        assert trace["reason"] == "path_not_found"

    def test_json_integer_range_does_not_depend_on_float_limits(self):
        huge_integer = 10**1000
        matched, trace = evaluate_predicate(
            {"gte": {"path": "/score", "value": huge_integer}},
            {"score": huge_integer},
        )
        assert matched is True
        assert trace["actual"] == huge_integer


class TestDeclarationsAndCompilation:
    def test_scene_node_appends_without_confusing_execution_and_story_topology(self):
        graph, scene, scene_ref = LF_SceneSpec().on_exec(
            scene_id="scene.opening",
            title="Opening",
            scene_body=_scene_body(),
            node_id="17",
        )

        assert graph["schema"] == GRAPH_SCHEMA
        assert graph["declarations"] == [scene]
        assert scene["source"] == {"nodeId": "17"}
        assert scene_ref == "scene.opening"
        assert LF_SceneSpec.RETURN_TYPES[2] == Input.LF_REF

    def test_scene_body_is_real_serialized_input_and_title_does_not_change_identity(self):
        body = _scene_body()
        _, first, first_ref = LF_SceneSpec().on_exec(
            scene_id="scene.opening",
            title="Opening",
            scene_body=body,
            node_id="17",
        )
        _, renamed, renamed_ref = LF_SceneSpec().on_exec(
            scene_id="scene.opening",
            title="The Signal",
            scene_body=body,
            node_id="17",
        )

        assert first["id"] == renamed["id"] == "scene.opening"
        assert first_ref == renamed_ref == "scene.opening"
        assert first["title"] == "Opening"
        assert renamed["title"] == "The Signal"
        assert renamed["beats"][0]["id"] == "scene.opening.beat.1"

    def test_scene_missing_id_fails_closed_with_structured_error(self):
        with pytest.raises(VNContractError) as error:
            LF_SceneSpec().on_exec(
                title="Opening",
                scene_body=_scene_body(),
                node_id="17",
            )

        payload = error.value.payload
        assert payload["status"] == "blocked"
        assert payload["errors"][0]["code"] == "missing_semantic_id"
        assert payload["errors"][0]["path"] == "/scene/id"

    @pytest.mark.parametrize("bad_id", [None, 7, " scene.opening "])
    def test_scene_does_not_coerce_semantic_ids(self, bad_id):
        with pytest.raises(VNContractError) as error:
            LF_SceneSpec().on_exec(
                scene_id=bad_id,
                title="Opening",
                scene_body=_scene_body(),
                node_id="17",
            )

        assert error.value.payload["errors"][0]["code"] in {
            "missing_semantic_id",
            "invalid_semantic_id",
        }

    def test_scene_body_missing_required_field_fails(self):
        with pytest.raises(VNContractError) as error:
            LF_SceneSpec().on_exec(
                scene_id="scene.opening",
                title="Opening",
                scene_body=json.dumps({"participants": [], "beats": [], "choices": [], "artRequests": []}),
                node_id="17",
            )

        payload = error.value.payload
        assert payload["errors"][0]["code"] == "missing_field"
        assert payload["errors"][0]["path"] == "/sceneBody"

    def test_switch_retains_all_cases_while_preview_selects_one(self):
        graph = _story_graph()
        state = _state(52)
        cases = [
            {
                "id": "route.trusted",
                "when": {"gte": {"path": "/trust", "value": 40}},
                "targetSceneId": "scene.opening",
            },
            {
                "id": "route.guarded",
                "when": {"lte": {"path": "/trust", "value": 39}},
                "targetSceneId": "scene.follow-up",
            },
        ]
        fallback = {"id": "route.fallback", "targetSceneId": "scene.opening"}

        switch_body = json.dumps({"cases": cases, "fallback": fallback})
        out_graph, selected, target, report = LF_VNSwitch().on_exec(
            graph=graph,
            state=state,
            switch_id="route.by-trust",
            switch_body=switch_body,
            node_id="18",
        )

        declaration = out_graph["declarations"][-1]
        assert declaration["cases"] == cases
        assert selected["id"] == "route.trusted"
        assert target == "scene.opening"
        assert report["selectedCaseId"] == "route.trusted"
        assert [item["id"] for item in report["cases"]] == [
            "route.trusted",
            "route.guarded",
        ]
        assert LF_VNSwitch.RETURN_TYPES[2] == Input.LF_REF

    @pytest.mark.parametrize(
        "switch_body",
        [
            "{}",
            json.dumps({"cases": []}),
            json.dumps({"fallback": None}),
        ],
    )
    def test_switch_body_requires_cases_and_explicit_fallback(self, switch_body):
        with pytest.raises(VNContractError) as error:
            LF_VNSwitch().on_exec(
                state=_state(),
                switch_id="route.by-trust",
                switch_body=switch_body,
                node_id="18",
            )

        payload = error.value.payload
        assert payload["status"] == "blocked"
        assert payload["errors"][0]["code"] in {"missing_field", "invalid_switch"}

    def test_switch_missing_id_fails_closed_with_structured_error(self):
        with pytest.raises(VNContractError) as error:
            LF_VNSwitch().on_exec(
                state=_state(),
                switch_body=json.dumps(
                    {
                        "cases": [
                            {
                                "id": "route.case",
                                "when": {},
                                "targetSceneId": "scene.opening",
                            }
                        ],
                        "fallback": None,
                    }
                ),
                node_id="18",
            )

        payload = error.value.payload
        assert payload["errors"][0]["code"] == "missing_semantic_id"
        assert payload["errors"][0]["path"] == "/switch/id"

    @pytest.mark.parametrize("bad_id", [None, 7, " route.by-trust "])
    def test_switch_does_not_coerce_semantic_ids(self, bad_id):
        with pytest.raises(VNContractError) as error:
            LF_VNSwitch().on_exec(
                state=_state(),
                switch_id=bad_id,
                switch_body=json.dumps(
                    {
                        "cases": [
                            {
                                "id": "route.case",
                                "when": {},
                                "targetSceneId": "scene.opening",
                            }
                        ],
                        "fallback": None,
                    }
                ),
                node_id="18",
            )

        assert error.value.payload["errors"][0]["code"] in {
            "missing_semantic_id",
            "invalid_semantic_id",
        }

    def test_duplicate_and_dangling_ids_are_machine_readable(self):
        graph = _story_graph(dangling=True)
        graph = append_declaration(graph, _scene("scene.follow-up", node_id="3"))

        bundle, report = compile_graph(
            graph=graph,
            workflow_id="example.signal",
            entry_scene_id="scene.opening",
        )

        assert bundle == {}
        assert report["schema"] == VALIDATION_SCHEMA
        assert report["status"] == "blocked"
        codes = {item["code"] for item in report["errors"]}
        assert "duplicate_semantic_id" in codes
        assert "dangling_transition" in codes
        assert all("path" in item for item in report["errors"])

    def test_invalid_source_id_does_not_hide_valid_graph_diagnostics(self):
        bundle, report = compile_graph(
            graph=_story_graph(),
            workflow_id="contains spaces",
            entry_scene_id="scene.opening",
        )

        assert bundle == {}
        assert report["status"] == "blocked"
        assert report["counts"]["scenes"] == 2
        assert report["source"]["workflowId"] is None
        assert report["source"]["graphReceipt"].startswith("sha256:")
        assert {item["code"] for item in report["errors"]} == {
            "invalid_semantic_id"
        }

    @pytest.mark.parametrize(
        ("workflow_id", "entry_scene_id", "expected_path"),
        [
            ("", "scene.opening", "/source/workflowId"),
            ("example.signal", "", "/entrySceneId"),
        ],
    )
    def test_compile_missing_author_id_fails_closed(self, workflow_id, entry_scene_id, expected_path):
        _, report = compile_graph(
            graph=_story_graph(),
            workflow_id=workflow_id,
            entry_scene_id=entry_scene_id,
        )

        assert report["status"] == "blocked"
        errors = report["errors"]
        assert any(
            item["code"] == "missing_semantic_id" and item["path"] == expected_path
            for item in errors
        )

    @pytest.mark.parametrize("bad_id", [None, 7, " example.signal "])
    def test_compile_does_not_coerce_workflow_id(self, bad_id):
        _, report = compile_graph(
            graph=_story_graph(),
            workflow_id=bad_id,
            entry_scene_id="scene.opening",
        )

        assert report["status"] == "blocked"
        assert any(
            item["path"] == "/source/workflowId"
            and item["code"] in {"missing_semantic_id", "invalid_semantic_id"}
            for item in report["errors"]
        )

    @pytest.mark.parametrize("bad_id", [None, 7, " scene.opening "])
    def test_compile_does_not_coerce_entry_scene_id(self, bad_id):
        _, report = compile_graph(
            graph=_story_graph(),
            workflow_id="example.signal",
            entry_scene_id=bad_id,
        )

        assert report["status"] == "blocked"
        assert any(
            item["path"] == "/entrySceneId"
            and item["code"] in {"missing_semantic_id", "invalid_semantic_id"}
            for item in report["errors"]
        )

    def test_non_json_graph_returns_a_report_without_hashing_failure(self):
        bundle, report = compile_graph(
            graph={"schema": GRAPH_SCHEMA, "declarations": {object()}},
            workflow_id="example.invalid",
            entry_scene_id="scene.opening",
        )

        assert bundle == {}
        assert report["status"] == "blocked"
        assert report["source"]["graphReceipt"] is None
        assert "non_json_value" in {item["code"] for item in report["errors"]}

    def test_canonical_bundle_is_byte_identical(self):
        graph = _story_graph()
        one, one_report = compile_graph(
            graph=graph,
            workflow_id="example.signal",
            entry_scene_id="scene.opening",
        )
        two, two_report = compile_graph(
            graph=graph,
            workflow_id="example.signal",
            entry_scene_id="scene.opening",
        )

        assert one_report["status"] == two_report["status"] == "complete"
        assert one["schema"] == BUNDLE_SCHEMA
        assert canonical_json(one).encode("utf-8") == canonical_json(two).encode("utf-8")
        assert "absolute" not in canonical_json(one)

    def test_compiled_children_inherit_comfy_node_provenance(self):
        bundle, report = compile_graph(
            graph=_story_graph(),
            workflow_id="example.signal",
            entry_scene_id="scene.opening",
        )

        assert report["status"] == "complete"
        opening = bundle["scenes"][0]
        assert opening["source"] == {"nodeId": "1"}
        assert opening["beats"][0]["source"] == opening["source"]
        assert opening["choices"][0]["source"] == opening["source"]
        assert opening["choices"][0]["effects"][0]["source"] == opening["source"]

    @pytest.mark.parametrize(
        "malformed",
        [
            {"schema": BUNDLE_SCHEMA},
            {
                "schema": BUNDLE_SCHEMA,
                "source": {
                    "workflowId": "example.invalid",
                    "graphReceipt": "sha256:" + "0" * 64,
                    "semanticVersion": 1,
                },
                "entrySceneId": "scene.opening",
                "scenes": [{"kind": "scene", "id": "scene.opening"}],
                "switches": [],
            },
            {
                "schema": BUNDLE_SCHEMA,
                "source": {
                    "workflowId": "example.invalid",
                    "graphReceipt": "sha256:" + "0" * 64,
                    "semanticVersion": 1.0,
                },
                "entrySceneId": "scene.opening",
                "scenes": [],
                "switches": [],
            },
        ],
    )
    def test_bundle_boundary_never_leaks_raw_key_errors(self, malformed):
        with pytest.raises(VNContractError):
            normalize_bundle(malformed)
        with pytest.raises(VNContractError):
            preview_bundle(bundle=malformed, state=_state())


class TestFixtureReplay:
    @pytest.mark.parametrize("bad_id", [None, 7, " choice.answer "])
    def test_preview_does_not_coerce_optional_selected_choice_id(self, bad_id):
        bundle, report = compile_graph(
            graph=_story_graph(),
            workflow_id="example.signal",
            entry_scene_id="scene.opening",
        )
        assert report["status"] == "complete"

        with pytest.raises(VNContractError) as error:
            preview_bundle(
                bundle=bundle,
                state=_state(52),
                selected_choice_id=bad_id,
            )

        assert error.value.payload["errors"][0]["path"] == "/selectedChoiceId"

    def test_marker_effect_is_idempotent_and_enables_follow_up(self):
        bundle, report = compile_graph(
            graph=_story_graph(),
            workflow_id="example.signal",
            entry_scene_id="scene.opening",
        )
        assert report["status"] == "complete"

        preview, derived = preview_bundle(
            bundle=bundle,
            state=_state(52),
            selected_choice_id="choice.answer",
        )

        assert preview["schema"] == PREVIEW_SCHEMA
        assert preview["before"]["availableChoiceIds"] == ["choice.answer"]
        assert preview["selectedChoice"]["appliedEffectIds"] == [
            "effect.signal-answered"
        ]
        assert preview["after"]["activeSceneId"] == "scene.follow-up"
        assert preview["after"]["activeSceneEligible"] is True
        assert derived["values"]["markers"] == ["signal.answered"]

        repeated, repeated_state = preview_bundle(
            bundle=bundle,
            state=derived,
            selected_choice_id="choice.answer",
        )
        assert repeated["selectedChoice"]["appliedEffectIds"] == []
        assert repeated["selectedChoice"]["skippedEffectIds"] == [
            "effect.signal-answered"
        ]
        assert repeated_state == derived

    def test_low_fixture_keeps_authored_choice_but_marks_it_unavailable(self):
        bundle, report = compile_graph(
            graph=_story_graph(),
            workflow_id="example.signal",
            entry_scene_id="scene.opening",
        )
        assert report["status"] == "complete"

        preview, _ = preview_bundle(bundle=bundle, state=_state(12))
        opening = next(
            item for item in preview["before"]["scenes"] if item["id"] == "scene.opening"
        )
        assert opening["choices"][0]["id"] == "choice.answer"
        assert opening["choices"][0]["available"] is False
        assert bundle["scenes"][0]["choices"][0]["id"] == "choice.answer"

    def test_compile_node_emits_bundle_preview_report_and_canonical_text(self):
        result = LF_VNCompile().on_exec(
            graph=_story_graph(),
            state=_state(52),
            workflow_id="example.signal",
            entry_scene_id="scene.opening",
            selected_choice_id="choice.answer",
            node_id="99",
        )

        bundle, preview, report, derived, serialized = result["result"]
        assert bundle["schema"] == BUNDLE_SCHEMA
        assert preview["schema"] == PREVIEW_SCHEMA
        assert report["schema"] == VALIDATION_SCHEMA
        assert derived["schema"] == STATE_SCHEMA
        assert serialized == canonical_json(bundle)
        assert result["ui"]["lf_output"][0]["bundle"] == bundle


class TestOpaqueConsumerBoundary:
    def test_unknown_effect_type_is_retained_and_deferred_not_reinterpreted(self):
        graph = append_declaration(
            None,
            _scene(
                "scene.opening",
                choices=[
                    {
                        "id": "choice.delegate",
                        "label": "Delegate",
                        "effects": [
                            {
                                "id": "effect.consumer-owned",
                                "type": "example.capability.invoke",
                                "payload": {"capabilityId": "example.open-channel"},
                            }
                        ],
                    }
                ],
            ),
        )
        bundle, report = compile_graph(
            graph=graph,
            workflow_id="example.opaque",
            entry_scene_id="scene.opening",
        )
        assert report["status"] == "complete"
        assert "deferred_effect_capability" in {
            item["code"] for item in report["warnings"]
        }

        preview, derived = preview_bundle(
            bundle=bundle,
            state=_state(52),
            selected_choice_id="choice.delegate",
        )

        assert preview["selectedChoice"]["appliedEffectIds"] == []
        assert preview["selectedChoice"]["deferredEffects"][0]["type"] == (
            "example.capability.invoke"
        )
        assert derived["appliedEffectIds"] == []

    def test_unknown_lf_effect_names_fail_closed(self):
        with pytest.raises(VNContractError) as error:
            _scene(
                "scene.opening",
                choices=[
                    {
                        "id": "choice.typo",
                        "label": "Continue",
                        "effects": [
                            {
                                "id": "effect.typo",
                                "type": "lf.marker.typo",
                                "payload": {"id": "story.ready"},
                            }
                        ],
                    }
                ],
            )
        assert "unsupported_core_effect_type" in str(error.value)


def test_switch_core_evaluation_matches_node_contract():
    declaration = build_switch_declaration(
        switch_id="route.test",
        cases=[
            {
                "id": "route.test.high",
                "when": {"gte": {"path": "/trust", "value": 40}},
                "targetSceneId": "scene.opening",
            }
        ],
        fallback={"id": "route.test.low", "targetSceneId": "scene.follow-up"},
        source_node_id="7",
    )
    selected, report = evaluate_switch(declaration, _state(12))
    assert selected["id"] == "route.test.low"
    assert report["usedFallback"] is True
