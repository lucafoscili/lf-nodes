"""Offline contracts for the focused, generic MiniMax H3 Runner cards."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import sys
import types
from typing import Any

import pytest


# Declarative workflow tests do not need Comfy's torch/xformers startup.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.constants", constants_module)
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import minimax_h3 as workflow_module


EXPECTED_NAMES = {
    "minimax_h3_generate_video": "Generate Video",
    "minimax_h3_animate_image": "Animate Image",
    "minimax_h3_first_last_frame": "First & Last Frame",
    "minimax_h3_reference_restage": "Reference Restage",
    "minimax_h3_character_swap": "Character Swap",
    "minimax_h3_outfit_transfer": "Outfit Transfer",
    "minimax_h3_sprite_motion": "Sprite Motion",
    "minimax_h3_scene_sheet": "Scene Sheet · Experimental",
}
BASE_IDS = {
    "minimax_h3_generate_video",
    "minimax_h3_animate_image",
    "minimax_h3_first_last_frame",
    "minimax_h3_sprite_motion",
}
REFERENCE_IDS = set(EXPECTED_NAMES) - BASE_IDS
EXPECTED_UPLOADS = {
    "minimax_h3_generate_video": (),
    "minimax_h3_animate_image": ("source_image",),
    "minimax_h3_first_last_frame": (
        "first_frame_image",
        "last_frame_image",
    ),
    "minimax_h3_reference_restage": ("reference_image",),
    "minimax_h3_character_swap": ("scene_image", "character_image"),
    "minimax_h3_outfit_transfer": ("character_image", "outfit_image"),
    "minimax_h3_sprite_motion": ("source_image",),
    "minimax_h3_scene_sheet": ("scene_sheet",),
}
EXPECTED_CANVASES = {
    "16:9": (1344, 768),
    "4:3": (1024, 768),
    "1:1": (768, 768),
    "3:4": (768, 1024),
    "9:16": (768, 1344),
    # Core's native ultrawide is the explicit long-edge exception. It remains
    # 32-aligned and exactly within the 1344x768 native pixel budget.
    "21:9": (1536, 672),
}
EXPECTED_DURATIONS = (124, 192, 243, 362)
EXPECTED_PREFIXES = {
    "minimax_h3_generate_video": (
        "LF_Nodes/MiniMaxH3/GenerateVideo/kitchen_quality/seed-73-f124"
    ),
    "minimax_h3_animate_image": (
        "LF_Nodes/MiniMaxH3/AnimateImage/kitchen_quality/seed-73-f124"
    ),
    "minimax_h3_first_last_frame": (
        "LF_Nodes/MiniMaxH3/FirstLastFrame/kitchen_quality/seed-73-f124"
    ),
    "minimax_h3_reference_restage": (
        "LF_Nodes/MiniMaxH3/ReferenceRestage/kitchen_quality/seed-73-refs1-f124"
    ),
    "minimax_h3_character_swap": (
        "LF_Nodes/MiniMaxH3/CharacterSwap/kitchen_quality/seed-73-refs2-f124"
    ),
    "minimax_h3_outfit_transfer": (
        "LF_Nodes/MiniMaxH3/OutfitTransfer/kitchen_quality/seed-73-refs2-f124"
    ),
    "minimax_h3_sprite_motion": (
        "LF_Nodes/MiniMaxH3/SpriteMotion/kitchen_quality/seed-73-f124"
    ),
    "minimax_h3_scene_sheet": (
        "LF_Nodes/MiniMaxH3/SceneSheetExperimental/kitchen_quality/seed-73-refs1-f124"
    ),
}
FORBIDDEN_DOMAIN_WORDS = ("velora", "stellaris", "azeroth", "sentinel")
FORBIDDEN_HOSTED_NODE_TYPES = {
    "MinimaxVideoGeneration",
    "MiniMaxVideoGeneration",
    "MinimaxImageToVideo",
    "MinimaxTextToVideo",
    "MiniMaxImageToVideo",
    "MiniMaxTextToVideo",
}
REFERENCE_SECTION_NODES = (
    "prompt_subject_definitions",
    "prompt_summary",
    "prompt_retention_analysis",
    "prompt_detailed_description",
    "prompt_overall_soundscape",
    "prompt_non_diegetic_music",
)


def _workflows() -> dict[str, Any]:
    return {workflow.id: workflow for workflow in workflow_module.WORKFLOWS}


def _cells(workflow: Any) -> dict[str, Any]:
    return {cell.id: cell for cell in workflow.inputs}


def _default_inputs(workflow: Any) -> dict[str, Any]:
    inputs = {
        cell.id: cell.props["lfValue"]
        for cell in workflow.inputs
        if "lfValue" in cell.props
    }
    inputs["access_basis"] = "applicable_territory"
    for cell in workflow.inputs:
        if cell.shape == "upload":
            inputs[cell.id] = [Path(f"C:/uploads/{cell.id}.png")]
    return inputs


def _configure(
    workflow: Any,
    monkeypatch: pytest.MonkeyPatch,
    **overrides: Any,
) -> tuple[dict[str, Any], list[str]]:
    calls: list[str] = []

    def resolve(inputs: dict[str, Any], name: str) -> str:
        calls.append(name)
        assert inputs[name] == [Path(f"C:/uploads/{name}.png")]
        return f"lf_workflow_runner/{name}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    inputs = {**_default_inputs(workflow), **overrides}
    prompt = workflow.load_prompt()
    workflow.configure_prompt(prompt, inputs)
    return prompt, calls


def _reference_prompt(prompt: dict[str, Any]) -> str:
    assert prompt["h3"]["inputs"]["prompt"] == ["prompt_join", 0]
    sections = [prompt[node_id]["inputs"]["value"] for node_id in REFERENCE_SECTION_NODES]
    assert all(isinstance(section, str) and section for section in sections)
    return "\n\n".join(sections)


def _option_values(cell: Any) -> list[str]:
    return [node["workflowValue"] for node in cell.props["lfDataset"]["nodes"]]


def test_catalogue_is_generic_concise_and_category_aware() -> None:
    workflows = _workflows()

    assert set(workflows) == set(EXPECTED_NAMES)
    assert {workflow_id: workflow.value for workflow_id, workflow in workflows.items()} == (
        EXPECTED_NAMES
    )
    for workflow in workflows.values():
        assert workflow.category == "MiniMax H3"
        assert not workflow.value.startswith(workflow.category)
        assert workflow.inputs and workflow.outputs
        for cell in (*workflow.inputs, *workflow.outputs):
            assert cell.id
            assert cell.node_id
            assert cell.description


def test_public_cards_have_no_velora_or_other_project_domain_vocabulary() -> None:
    public_text = ""
    for workflow in _workflows().values():
        public_text += json.dumps(
            {
                "id": workflow.id,
                "value": workflow.value,
                "description": workflow.description,
                "category": workflow.category,
                "inputs": [cell.to_dict() for cell in workflow.inputs],
                "outputs": [cell.to_dict() for cell in workflow.outputs],
            },
            ensure_ascii=False,
        ).lower()
        public_text += workflow.workflow_path.read_text(encoding="utf-8").lower()

    for forbidden in FORBIDDEN_DOMAIN_WORDS:
        assert forbidden not in public_text


def test_task_families_use_separate_local_checkpoints_and_profiles() -> None:
    workflows = _workflows()

    for workflow_id in BASE_IDS:
        workflow = workflows[workflow_id]
        prompt = workflow.load_prompt()
        assert workflow.workflow_path.name == "minimax_h3_base.json"
        assert prompt["unet"]["inputs"]["unet_name"] == (
            "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
        )
        assert prompt["h3"]["class_type"] == "MiniMaxH3ImageToVideo"
        assert "execution_profile" not in _cells(workflow)

    for workflow_id in REFERENCE_IDS:
        workflow = workflows[workflow_id]
        prompt = workflow.load_prompt()
        assert workflow.workflow_path.name == "minimax_h3_reference.json"
        assert prompt["unet"]["inputs"]["unet_name"] == (
            "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
        )
        assert prompt["h3"]["class_type"] == "MiniMaxH3ReferenceToVideo"
        assert "execution_profile" not in _cells(workflow)


def test_all_cards_use_the_validated_kitchen_attention_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for workflow in _workflows().values():
        prompt, _calls = _configure(workflow, monkeypatch)
        assert prompt["attention_backend"] == {
            "inputs": {
                "model": ["model_device", 0],
                "attention": "comfy kitchen attention",
            },
            "class_type": "ModelAttentionBackend",
            "_meta": {"title": "Use Comfy Kitchen attention"},
        }
        assert prompt["guider"]["inputs"]["model"] == [
            "attention_backend",
            0,
        ]
        assert prompt["scheduler"]["inputs"]["model"] == [
            "attention_backend",
            0,
        ]
        for node_id in (
            "model_device",
            "clip_device",
            "video_vae_device",
            "audio_vae_device",
        ):
            assert prompt[node_id]["inputs"]["device"] == "default"


def test_graphs_have_no_hosted_partner_api_nodes() -> None:
    for workflow in _workflows().values():
        prompt = workflow.load_prompt()
        class_types = {
            node.get("class_type")
            for node in prompt.values()
            if isinstance(node, dict)
        }
        assert class_types.isdisjoint(FORBIDDEN_HOSTED_NODE_TYPES)
        assert all(
            "hosted" not in str(class_type).lower()
            and "partner" not in str(class_type).lower()
            and "api" not in str(class_type).lower()
            for class_type in class_types
        )
        assert "SaveVideo" in class_types


def test_access_basis_is_required_select_with_no_default() -> None:
    for workflow in _workflows().values():
        access = _cells(workflow)["access_basis"]
        assert access.shape == "select"
        assert access.required is True
        assert "lfValue" not in access.props
        assert _option_values(access) == [
            "applicable_territory",
            "separate_written_authorization",
        ]


def test_public_access_copy_names_territories_and_denies_implied_authority() -> None:
    region_patterns = (
        r"\beuropean union\b|\beu\b",
        r"\bunited kingdom\b|\buk\b",
        r"\bunited states\b|\bus\b|\busa\b",
        r"\brepublic of korea\b|\bsouth korea\b",
    )
    for workflow in _workflows().values():
        public = json.dumps(
            {
                "description": workflow.description,
                "inputs": [cell.to_dict() for cell in workflow.inputs],
            },
            ensure_ascii=False,
        ).lower()
        assert all(re.search(pattern, public) for pattern in region_patterns)
        assert re.search(
            r"does not grant.{0,40}(?:licen[cs]e|authori[sz]ation)", public
        )
        assert "open source" not in public


@pytest.mark.parametrize("bad_value", [None, "", "other", True])
def test_access_basis_fails_closed_before_graph_mutation_or_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
    bad_value: Any,
) -> None:
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("access rejection must not stage an upload"),
    )
    for workflow in _workflows().values():
        inputs = _default_inputs(workflow)
        if bad_value is None:
            inputs.pop("access_basis")
        else:
            inputs["access_basis"] = bad_value
        prompt = workflow.load_prompt()
        original = copy.deepcopy(prompt)

        with pytest.raises(InputValidationError) as error:
            workflow.configure_prompt(prompt, inputs)

        assert error.value.input_name == "access_basis"
        assert prompt == original


@pytest.mark.parametrize(
    "access_basis",
    ["applicable_territory", "separate_written_authorization"],
)
def test_both_access_bases_are_accepted_but_never_written_to_the_graph(
    monkeypatch: pytest.MonkeyPatch,
    access_basis: str,
) -> None:
    for workflow in _workflows().values():
        prompt, _calls = _configure(
            workflow,
            monkeypatch,
            access_basis=access_basis,
        )
        serialized = json.dumps(prompt)
        assert access_basis not in serialized
        assert "access_basis" not in serialized
        assert "access" not in prompt


def test_curated_aspect_ratios_map_to_safe_native_canvases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflows = _workflows()
    expected_values = list(EXPECTED_CANVASES)
    for workflow in workflows.values():
        aspect = _cells(workflow)["aspect_ratio"]
        assert _option_values(aspect) == expected_values
        assert "width" not in _cells(workflow)
        assert "height" not in _cells(workflow)

    workflow = workflows["minimax_h3_generate_video"]
    for aspect_ratio, expected_size in EXPECTED_CANVASES.items():
        prompt, _calls = _configure(
            workflow,
            monkeypatch,
            aspect_ratio=aspect_ratio,
        )
        actual = (
            prompt["h3"]["inputs"]["width"],
            prompt["h3"]["inputs"]["height"],
        )
        assert actual == expected_size
        width, height = actual
        assert width % 32 == height % 32 == 0
        assert width * height <= 1344 * 768
        if aspect_ratio == "21:9":
            assert actual == (1536, 672)
        else:
            assert max(actual) <= 1344


def test_duration_choices_are_exact_17k_plus_5_frames_at_24_fps() -> None:
    expected = [str(frames) for frames in EXPECTED_DURATIONS]
    for workflow in _workflows().values():
        duration = _cells(workflow)["duration_frames"]
        assert _option_values(duration) == expected
        assert duration.props["lfValue"] == "124"
    assert all((frames - 5) % 17 == 0 for frames in EXPECTED_DURATIONS)


@pytest.mark.parametrize("frames", EXPECTED_DURATIONS)
def test_duration_maps_exactly_to_h3_and_fixed_mux_rate(
    monkeypatch: pytest.MonkeyPatch,
    frames: int,
) -> None:
    workflow = _workflows()["minimax_h3_generate_video"]
    prompt, _calls = _configure(
        workflow,
        monkeypatch,
        duration_frames=str(frames),
    )
    assert prompt["h3"]["inputs"]["length"] == frames
    assert prompt["create_video"]["inputs"]["fps"] == 24.0


@pytest.mark.parametrize("bad_duration", ["175", "191", True, "nan", "inf"])
def test_non_preset_durations_fail_before_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
    bad_duration: Any,
) -> None:
    workflow = _workflows()["minimax_h3_animate_image"]
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid duration must not stage an upload"),
    )
    with pytest.raises(InputValidationError) as error:
        workflow.configure_prompt(
            workflow.load_prompt(),
            {**_default_inputs(workflow), "duration_frames": bad_duration},
        )
    assert error.value.input_name == "duration_frames"


def test_required_uploads_are_declared_in_semantic_reference_order() -> None:
    for workflow_id, expected_uploads in EXPECTED_UPLOADS.items():
        uploads = [
            cell for cell in _workflows()[workflow_id].inputs if cell.shape == "upload"
        ]
        assert tuple(cell.id for cell in uploads) == expected_uploads
        assert all(cell.required for cell in uploads)


@pytest.mark.parametrize(
    ("workflow_id", "missing_input"),
    [
        (workflow_id, input_id)
        for workflow_id, input_ids in EXPECTED_UPLOADS.items()
        for input_id in input_ids
    ],
)
def test_each_required_upload_fails_before_any_upload_is_staged(
    monkeypatch: pytest.MonkeyPatch,
    workflow_id: str,
    missing_input: str,
) -> None:
    workflow = _workflows()[workflow_id]
    inputs = _default_inputs(workflow)
    inputs.pop(missing_input)
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("incomplete request must not stage uploads"),
    )

    with pytest.raises(InputValidationError) as error:
        workflow.configure_prompt(workflow.load_prompt(), inputs)

    assert error.value.input_name == missing_input


def test_uploads_resolve_in_order_and_wire_to_their_exact_graph_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflows = _workflows()
    for workflow_id, expected_uploads in EXPECTED_UPLOADS.items():
        prompt, calls = _configure(workflows[workflow_id], monkeypatch)
        assert calls == list(expected_uploads)

        if workflow_id in BASE_IDS:
            expected_first = expected_uploads[:1]
            expected_last = expected_uploads[1:]
            if expected_first:
                assert prompt["source_first"]["inputs"]["image"].endswith(
                    f"{expected_first[0]}.png [input]"
                )
                assert prompt["h3"]["inputs"]["first_frame"] == ["source_first", 0]
            else:
                assert "source_first" not in prompt
                assert "first_frame" not in prompt["h3"]["inputs"]
            if expected_last:
                assert prompt["source_last"]["inputs"]["image"].endswith(
                    f"{expected_last[0]}.png [input]"
                )
                assert prompt["h3"]["inputs"]["last_frame"] == ["source_last", 0]
            else:
                assert "source_last" not in prompt
                assert "last_frame" not in prompt["h3"]["inputs"]
            continue

        for ordinal, input_id in enumerate(expected_uploads, start=1):
            source_id = f"source_{ordinal}"
            socket = f"ref_images.ref_image_{ordinal - 1}"
            assert prompt[source_id]["inputs"]["image"].endswith(
                f"{input_id}.png [input]"
            )
            assert prompt["h3"]["inputs"][socket] == [source_id, 0]
        next_ordinal = len(expected_uploads) + 1
        assert f"source_{next_ordinal}" not in prompt
        assert (
            f"ref_images.ref_image_{next_ordinal - 1}"
            not in prompt["h3"]["inputs"]
        )


def test_animate_and_first_last_cards_expose_distinct_frame_support(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    animate, _calls = _configure(
        _workflows()["minimax_h3_animate_image"], monkeypatch
    )
    assert animate["h3"]["inputs"]["first_frame"] == ["source_first", 0]
    assert "last_frame" not in animate["h3"]["inputs"]

    first_last, _calls = _configure(
        _workflows()["minimax_h3_first_last_frame"],
        monkeypatch,
        duration_frames="192",
    )
    assert first_last["h3"]["inputs"]["first_frame"] == ["source_first", 0]
    assert first_last["h3"]["inputs"]["last_frame"] == ["source_last", 0]
    compiled = first_last["h3"]["inputs"]["prompt"]
    assert "Picture 1 (from Shot 1) aligns with the 0.00-second mark" in compiled
    assert "Picture 2 (from Shot 1) aligns with the 8.00-second mark" in compiled


def test_reference_cards_use_max_reference_detail_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for workflow_id in REFERENCE_IDS:
        workflow = _workflows()[workflow_id]
        prompt, _calls = _configure(workflow, monkeypatch)

        assert prompt["h3"]["inputs"]["ref_image_size"] == "max"
        assert "Max detail" in workflow.description
        assert "several times slower than Match" in workflow.description


def test_base_cards_use_the_official_structured_prompt_sections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    section_headers = (
        "integrated_multimodal_description:\n",
        "overall_soundscape:\n",
        "non_diegetic_music:\n",
    )
    for workflow_id in BASE_IDS:
        prompt, _calls = _configure(_workflows()[workflow_id], monkeypatch)
        compiled = prompt["h3"]["inputs"]["prompt"]
        assert isinstance(compiled, str)
        assert all(compiled.count(header) == 1 for header in section_headers)


def test_reference_presets_use_exact_picture_tags_and_canonical_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_tags = {
        "minimax_h3_reference_restage": {"<Picture 1>"},
        "minimax_h3_character_swap": {"<Picture 1>", "<Picture 2>"},
        "minimax_h3_outfit_transfer": {"<Picture 1>", "<Picture 2>"},
        "minimax_h3_scene_sheet": {"<Picture 1>"},
    }
    role_fragments = {
        "minimax_h3_reference_restage": (
            "<Subject 1> is the subject shown in <Picture 1>",
        ),
        "minimax_h3_character_swap": (
            "<Picture 1> supplies the target pose, framing, clothing, lighting, and environment",
            "identity-defining appearance from <Picture 2>",
        ),
        "minimax_h3_outfit_transfer": (
            "<Subject 1> is the subject shown in <Picture 1>",
            "<Picture 2> is an outfit reference",
        ),
        "minimax_h3_scene_sheet": (
            "<Picture 1> is one composite design and scene sheet",
        ),
    }
    picture_like = re.compile(r"<[^>]*picture[^>]*>", re.IGNORECASE)
    canonical = re.compile(r"<Picture [1-9]>")

    for workflow_id in REFERENCE_IDS:
        prompt, _calls = _configure(_workflows()[workflow_id], monkeypatch)
        compiled = _reference_prompt(prompt)
        tokens = picture_like.findall(compiled)
        assert tokens
        assert all(canonical.fullmatch(token) for token in tokens)
        assert set(tokens) == expected_tags[workflow_id]
        assert all(fragment in compiled for fragment in role_fragments[workflow_id])


def test_reference_cards_render_each_official_section_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    headers = (
        "subject_definitions:\n",
        "summary:\n",
        "retention_analysis:\n",
        "detailed_description:\n",
        "overall_soundscape:\n",
        "non_diegetic_music:\n",
    )
    for workflow_id in REFERENCE_IDS:
        prompt, _calls = _configure(_workflows()[workflow_id], monkeypatch)
        compiled = _reference_prompt(prompt)
        assert all(compiled.count(header) == 1 for header in headers)
        assert prompt["prompt_raw"]["inputs"]["value"] == ""


def test_reference_profiles_reject_base_only_accelerators_before_staging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["minimax_h3_character_swap"]
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid profile must not stage uploads"),
    )
    for profile in ("native_quality", "kitchen_turbo_8step", "turbo_preview"):
        with pytest.raises(InputValidationError) as error:
            workflow.configure_prompt(
                workflow.load_prompt(),
                {**_default_inputs(workflow), "execution_profile": profile},
            )
        assert error.value.input_name == "execution_profile"


def test_outputs_and_filename_prefixes_are_exact_and_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for workflow_id, workflow in _workflows().items():
        assert len(tuple(workflow.outputs)) == 1
        output = tuple(workflow.outputs)[0]
        assert (output.id, output.node_id, output.shape) == (
            "video",
            "save",
            "masonry",
        )

        first, _calls = _configure(workflow, monkeypatch, seed="73")
        second, _calls = _configure(workflow, monkeypatch, seed="73")
        assert first == second
        assert first["save"]["class_type"] == "SaveVideo"
        assert first["save"]["inputs"]["video"] == ["create_video", 0]
        assert first["save"]["inputs"]["filename_prefix"] == (
            EXPECTED_PREFIXES[workflow_id]
        )
        assert first["create_video"]["inputs"]["images"] == ["decode_video", 0]
        assert first["create_video"]["inputs"]["audio"] == ["decode_audio", 0]
        assert first["create_video"]["inputs"]["fps"] == 24.0


def test_serialized_and_native_help_contract_does_not_render_twice() -> None:
    for workflow in _workflows().values():
        for cell in workflow.inputs:
            serialized = cell.to_dict()
            assert serialized["title"] == cell.description
            if cell.shape == "select":
                native_help = cell.props["lfTextfieldProps"]["lfHelper"]["value"]
                assert "lfHelper" not in cell.props
            elif cell.shape == "textfield":
                native_help = cell.props["lfHelper"]["value"]
                assert "lfHelper" not in cell.props.get("lfTextfieldProps", {})
            else:
                # Upload has no native helper surface, so its serialized title is
                # intentionally the one visible guidance line in Workflow Runner.
                assert cell.shape == "upload"
                continue
            # Workflow Runner recognizes identical native help and suppresses the
            # serialized fallback instead of rendering the same prose twice.
            assert native_help == cell.description
