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
    "minimax_h3_anchored_sprite_loop": "Anchored Sprite Loop",
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
    "minimax_h3_anchored_sprite_loop",
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
    "minimax_h3_anchored_sprite_loop": (
        "first_frame_image",
        "last_frame_image",
    ),
    "minimax_h3_reference_restage": ("reference_image",),
    "minimax_h3_character_swap": ("scene_image", "character_image"),
    "minimax_h3_outfit_transfer": ("character_image", "outfit_image"),
    "minimax_h3_sprite_motion": ("source_image",),
    "minimax_h3_scene_sheet": ("scene_sheet",),
}
OPTIONAL_UPLOADS = {
    "minimax_h3_anchored_sprite_loop": (
        "guide_image_1",
        "guide_image_2",
        "guide_image_3",
    ),
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
    "minimax_h3_anchored_sprite_loop": (
        "LF_Nodes/MiniMaxH3/AnchoredSpriteLoop/kitchen_quality/seed-73-f124"
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
FORBIDDEN_DOMAIN_WORDS = (
    "velora",
    "garage",
    "stellaris",
    "azeroth",
    "sentinel",
)
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
    for cell in workflow.inputs:
        if cell.shape == "upload" and cell.required:
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
    assert re.search(r"\bden\b", public_text) is None


def test_task_families_use_separate_local_checkpoints_and_profiles() -> None:
    workflows = _workflows()

    for workflow_id in BASE_IDS:
        workflow = workflows[workflow_id]
        prompt = workflow.load_prompt()
        expected_graph = (
            "minimax_h3_anchored_loop.json"
            if workflow_id == "minimax_h3_anchored_sprite_loop"
            else "minimax_h3_base.json"
        )
        assert workflow.workflow_path.name == expected_graph
        assert prompt["unet"]["inputs"]["unet_name"] == (
            "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
        )
        assert prompt["h3"]["class_type"] == "MiniMaxH3ImageToVideo"
        if workflow_id == "minimax_h3_anchored_sprite_loop":
            assert prompt["guide_1"]["class_type"] == "MiniMaxH3AddGuide"
            assert prompt["guide_2"]["class_type"] == "MiniMaxH3AddGuide"
            assert prompt["guide_3"]["class_type"] == "MiniMaxH3AddGuide"
            assert prompt["sprite_sampler"]["class_type"] == (
                "LF_PeriodicImageBatchSampler"
            )
            assert prompt["remove_background"]["class_type"] == "VNCCS_RMBG2"
            assert prompt["verify_rmbg_alpha"]["class_type"] == "ImageToMask"
            assert prompt["rmbg_transparency_mask"]["class_type"] == "InvertMask"
            assert prompt["validated_cutout"]["class_type"] == (
                "JoinImageWithAlpha"
            )
            assert prompt["sprite_normalize"]["class_type"] == (
                "LF_NormalizeSpriteBatch"
            )
            assert not any(
                node["class_type"] == "ImageScale" for node in prompt.values()
            )
            assert prompt["sprite_grid"]["class_type"] == "LF_ImageGrid"
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


def test_public_cards_do_not_require_policy_attestations() -> None:
    forbidden = (
        "access_basis",
        "applicable territory",
        "separate written authorization",
        "grants no licence",
    )
    for workflow in _workflows().values():
        public = json.dumps(
            {
                "description": workflow.description,
                "inputs": [cell.to_dict() for cell in workflow.inputs],
            },
            ensure_ascii=False,
        ).lower()
        assert all(phrase not in public for phrase in forbidden)


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
            cell
            for cell in _workflows()[workflow_id].inputs
            if cell.shape == "upload" and cell.required
        ]
        assert tuple(cell.id for cell in uploads) == expected_uploads
        assert all(cell.required for cell in uploads)

    for workflow_id, expected_uploads in OPTIONAL_UPLOADS.items():
        uploads = [
            cell
            for cell in _workflows()[workflow_id].inputs
            if cell.shape == "upload" and not cell.required
        ]
        assert tuple(cell.id for cell in uploads) == expected_uploads


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


def test_anchored_sprite_loop_declares_three_optional_image_guides() -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    cells = _cells(workflow)

    assert [
        cell.id for cell in workflow.inputs if cell.shape == "upload"
    ] == [
        "first_frame_image",
        "last_frame_image",
        "guide_image_1",
        "guide_image_2",
        "guide_image_3",
    ]
    assert cells["first_frame_image"].required is True
    assert cells["last_frame_image"].required is True
    for ordinal, default_frame in ((1, "41"), (2, "82"), (3, "103")):
        assert cells[f"guide_image_{ordinal}"].required is False
        frame = cells[f"guide_frame_{ordinal}"]
        assert frame.required is False
        assert frame.props["lfValue"] == default_frame
        assert frame.props["lfHtmlAttributes"]["min"] == 1
        assert frame.props["lfHtmlAttributes"]["max"] == 360


def test_anchored_sprite_loop_exposes_bounded_sprite_controls_and_outputs() -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    cells = _cells(workflow)

    assert cells["sprite_size"].node_id == "sprite_normalize"
    assert cells["sprite_size"].props["lfValue"] == "256"
    assert cells["sprite_size"].props["lfHtmlAttributes"] == {
        "autocomplete": "off",
        "name": "sprite_size",
        "type": "number",
        "min": 32,
        "max": 1024,
        "step": 1,
    }
    assert cells["sprite_alpha_height"].node_id == "sprite_normalize"
    assert cells["sprite_alpha_height"].props["lfValue"] == "224"
    assert cells["sprite_reference_frame"].node_id == "sprite_normalize"
    assert cells["sprite_reference_frame"].props["lfValue"] == "0"
    assert cells["sprite_reference_frame"].props["lfHtmlAttributes"]["max"] == 23
    assert cells["sprite_bottom_padding"].node_id == "sprite_normalize"
    assert cells["sprite_bottom_padding"].props["lfValue"] == "16"
    assert cells["intended_fps"].node_id == "sprite_sampler"
    assert cells["intended_fps"].props["lfValue"] == "12"
    assert cells["intended_fps"].props["lfHtmlAttributes"]["min"] == 1
    assert cells["intended_fps"].props["lfHtmlAttributes"]["max"] == 60
    assert [
        (cell.id, cell.node_id, cell.shape) for cell in workflow.outputs
    ] == [
        ("video", "save", "masonry"),
        ("frames", "save_frames", "masonry"),
        ("atlas", "save_atlas", "masonry"),
        ("receipt", "display_sampling_receipt", "code"),
        (
            "normalization_receipt",
            "display_normalization_receipt",
            "code",
        ),
    ]
    assert tuple(workflow.outputs)[-1].props == {"lfLanguage": "json"}


def test_anchored_sprite_loop_builds_the_exact_sprite_output_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    prompt, _calls = _configure(
        workflow,
        monkeypatch,
        sprite_size="512",
        sprite_alpha_height="448",
        sprite_reference_frame="7",
        sprite_bottom_padding="32",
        intended_fps="24",
    )

    assert prompt["sprite_sampler"]["inputs"] == {
        "image": ["decode_video", 0],
        "target_count": 24,
        "loop_endpoint_policy": "exclude_final_endpoint",
        "source_fps": 24.0,
        "intended_fps": 24.0,
    }
    assert prompt["remove_background"]["inputs"] == {
        "image": ["sprite_sampler", 0],
        "model": "RMBG-2.0",
        "sensitivity": 1.0,
        "process_res": 1024,
        "mask_blur": 0,
        "mask_offset": 0,
        "invert_output": False,
        "refine_foreground": False,
        "background": "Alpha",
    }
    assert prompt["verify_rmbg_alpha"]["inputs"] == {
        "image": ["remove_background", 0],
        "channel": "alpha",
    }
    assert prompt["rmbg_transparency_mask"]["inputs"] == {
        "mask": ["verify_rmbg_alpha", 0],
    }
    assert prompt["validated_cutout"]["inputs"] == {
        "image": ["remove_background", 0],
        "alpha": ["rmbg_transparency_mask", 0],
    }
    assert prompt["sprite_normalize"]["inputs"] == {
        "image": ["validated_cutout", 0],
        "canvas_width": 512,
        "canvas_height": 512,
        "target_reference_alpha_height": 448,
        "reference_frame_index": 7,
        "bottom_padding": 32,
    }
    assert prompt["save_frames"]["inputs"] == {
        "images": ["sprite_normalize", 0],
        "filename_prefix": (
            "LF_Nodes/MiniMaxH3/AnchoredSpriteLoop/kitchen_quality/"
            "seed-42-f124/frames-512px-content-448px-bottom-32px-ref-7-24fps"
        ),
    }
    grid_inputs = prompt["sprite_grid"]["inputs"]
    assert grid_inputs["image"] == ["sprite_normalize", 0]
    assert grid_inputs["cell_width"] == 512
    assert grid_inputs["cell_height"] == 512
    assert grid_inputs["gap_px"] == 0
    assert grid_inputs["background"] == "transparent"
    assert grid_inputs["show_headers"] is False
    assert grid_inputs["title"] == ""
    assert len(grid_inputs["dataset"]["columns"]) == 6
    assert len(grid_inputs["dataset"]["nodes"]) == 4
    assert all(
        column["title"] == "" for column in grid_inputs["dataset"]["columns"]
    )
    assert all(node["value"] == "" for node in grid_inputs["dataset"]["nodes"])
    assert prompt["save_atlas"]["inputs"] == {
        "images": ["sprite_grid", 0],
        "filename_prefix": (
            "LF_Nodes/MiniMaxH3/AnchoredSpriteLoop/kitchen_quality/"
            "seed-42-f124/atlas-6x4-512px-content-448px-bottom-32px-ref-7-24fps"
        ),
    }
    assert prompt["display_sampling_receipt"]["inputs"]["json_input"] == [
        "sprite_sampler",
        1,
    ]
    assert prompt["display_normalization_receipt"]["inputs"]["json_input"] == [
        "sprite_normalize",
        1,
    ]
    assert prompt["create_video"]["inputs"]["images"] == ["decode_video", 0]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sprite_size", 31),
        ("sprite_size", 1025),
        ("sprite_size", True),
        ("sprite_size", "nan"),
        ("sprite_alpha_height", 0),
        ("sprite_alpha_height", 1025),
        ("sprite_alpha_height", True),
        ("sprite_alpha_height", "nan"),
        ("sprite_reference_frame", -1),
        ("sprite_reference_frame", 24),
        ("sprite_reference_frame", True),
        ("sprite_bottom_padding", -1),
        ("sprite_bottom_padding", 1024),
        ("sprite_bottom_padding", True),
        ("intended_fps", 0),
        ("intended_fps", 61),
        ("intended_fps", True),
        ("intended_fps", "nan"),
    ],
)
def test_anchored_sprite_controls_fail_before_upload_staging_or_graph_mutation(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: Any,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    inputs = {**_default_inputs(workflow), field: value}
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid sprite controls must not stage uploads"),
    )
    prompt = workflow.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises((InputValidationError, ValueError)):
        workflow.configure_prompt(prompt, inputs)

    assert prompt == original


def test_anchored_sprite_geometry_must_fit_before_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    inputs = {
        **_default_inputs(workflow),
        "sprite_size": 256,
        "sprite_alpha_height": 241,
        "sprite_bottom_padding": 16,
    }
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid sprite geometry must not stage uploads"),
    )
    prompt = workflow.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises(ValueError, match="content height plus bottom padding"):
        workflow.configure_prompt(prompt, inputs)

    assert prompt == original


def test_anchored_sprite_loop_declares_exact_local_rmbg2_package() -> None:
    workflows = _workflows()
    workflow = workflows["minimax_h3_anchored_sprite_loop"]

    assert len(workflow.required_model_assets) == 1
    asset = workflow.required_model_assets[0]
    assert asset.label == "VNCCS RMBG-2.0 model"
    assert asset.relative_paths == (
        "RMBG/RMBG-2.0/config.json",
        "RMBG/RMBG-2.0/model.safetensors",
        "RMBG/RMBG-2.0/birefnet.py",
        "RMBG/RMBG-2.0/BiRefNet_config.py",
    )
    assert all(
        not other.required_model_assets
        for workflow_id, other in workflows.items()
        if workflow_id != workflow.id
    )
    assert "Runner does not start the wrapper's fallback download" in (
        workflow.description
    )
    assert "one reference-derived scale and horizontal pivot" in (
        workflow.description
    )
    assert "not semantic body height" in workflow.description
    assert "does not stabilize the inferred matte itself" in workflow.description


def test_anchored_sprite_loop_keeps_explicit_endpoints_without_optional_guides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    prompt, calls = _configure(workflow, monkeypatch)

    assert calls == ["first_frame_image", "last_frame_image"]
    assert prompt["h3"]["inputs"]["first_frame"] == ["source_first", 0]
    assert prompt["h3"]["inputs"]["last_frame"] == ["source_last", 0]
    assert prompt["guider"]["inputs"]["conditioning"] == ["h3", 0]
    for ordinal in (1, 2, 3):
        assert f"source_guide_{ordinal}" not in prompt
        assert f"guide_{ordinal}" not in prompt


def test_anchored_sprite_loop_download_removes_optional_guide_branches() -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    defaults = {
        cell.id: cell.props["lfValue"]
        for cell in workflow.inputs
        if "lfValue" in cell.props
    }
    prompt = workflow.load_prompt()

    assert workflow.configure_download is not None
    workflow.configure_download(prompt, defaults)

    assert prompt["h3"]["inputs"]["first_frame"] == ["source_first", 0]
    assert prompt["h3"]["inputs"]["last_frame"] == ["source_last", 0]
    assert prompt["guider"]["inputs"]["conditioning"] == ["h3", 0]
    assert prompt["sprite_sampler"]["inputs"]["target_count"] == 24
    assert prompt["save"]["inputs"]["filename_prefix"].endswith(
        "/seed-42-f124"
    )
    for ordinal in (1, 2, 3):
        assert f"source_guide_{ordinal}" not in prompt
        assert f"guide_{ordinal}" not in prompt


def test_anchored_sprite_loop_keeps_legacy_two_guide_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    prompt, calls = _configure(
        workflow,
        monkeypatch,
        guide_image_1=[Path("C:/uploads/guide_image_1.png")],
        guide_frame_1="35",
        guide_image_2=[Path("C:/uploads/guide_image_2.png")],
        guide_frame_2="70",
    )

    assert calls == [
        "first_frame_image",
        "last_frame_image",
        "guide_image_1",
        "guide_image_2",
    ]
    assert "source_guide_3" not in prompt
    assert "guide_3" not in prompt
    assert prompt["guide_1"]["inputs"]["positive"] == ["h3", 0]
    assert prompt["guide_2"]["inputs"]["positive"] == ["guide_1", 0]
    assert prompt["guider"]["inputs"]["conditioning"] == ["guide_2", 0]


def test_anchored_sprite_loop_chains_guides_in_frame_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    prompt, calls = _configure(
        workflow,
        monkeypatch,
        guide_image_1=[Path("C:/uploads/guide_image_1.png")],
        guide_frame_1="90",
        guide_image_2=[Path("C:/uploads/guide_image_2.png")],
        guide_frame_2="30",
        guide_image_3=[Path("C:/uploads/guide_image_3.png")],
        guide_frame_3="60",
    )

    assert calls == [
        "first_frame_image",
        "last_frame_image",
        "guide_image_1",
        "guide_image_2",
        "guide_image_3",
    ]
    assert prompt["guide_2"] == {
        "inputs": {
            "positive": ["h3", 0],
            "vae": ["video_vae_device", 0],
            "latent": ["h3", 1],
            "image": ["source_guide_2", 0],
            "frame_idx": 30,
        },
        "class_type": "MiniMaxH3AddGuide",
        "_meta": {"title": "Anchor optional intermediate guide 2"},
    }
    assert prompt["guide_3"]["inputs"]["positive"] == ["guide_2", 0]
    assert prompt["guide_3"]["inputs"]["frame_idx"] == 60
    assert prompt["guide_1"]["inputs"]["positive"] == ["guide_3", 0]
    assert prompt["guide_1"]["inputs"]["frame_idx"] == 90
    assert prompt["guider"]["inputs"]["conditioning"] == ["guide_1", 0]


@pytest.mark.parametrize("ordinal", [1, 2, 3])
def test_anchored_sprite_loop_accepts_any_optional_guide_slot(
    monkeypatch: pytest.MonkeyPatch,
    ordinal: int,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    image_field = f"guide_image_{ordinal}"
    prompt, calls = _configure(
        workflow,
        monkeypatch,
        **{
            image_field: [Path(f"C:/uploads/{image_field}.png")],
            f"guide_frame_{ordinal}": "61",
        },
    )

    assert calls == ["first_frame_image", "last_frame_image", image_field]
    for other in {1, 2, 3} - {ordinal}:
        assert f"guide_{other}" not in prompt
        assert f"source_guide_{other}" not in prompt
    assert prompt[f"guide_{ordinal}"]["inputs"]["positive"] == ["h3", 0]
    assert prompt[f"guide_{ordinal}"]["inputs"]["frame_idx"] == 61
    assert prompt["guider"]["inputs"]["conditioning"] == [
        f"guide_{ordinal}",
        0,
    ]


@pytest.mark.parametrize("ordinal", [1, 2, 3])
@pytest.mark.parametrize("bad_frame", [0, 123, -1, 124, True, "nan"])
def test_anchored_guide_indices_must_be_interior_before_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
    ordinal: int,
    bad_frame: Any,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    inputs = {
        **_default_inputs(workflow),
        f"guide_image_{ordinal}": [
            Path(f"C:/uploads/guide_image_{ordinal}.png")
        ],
        f"guide_frame_{ordinal}": bad_frame,
    }
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("invalid guide indices must not stage uploads"),
    )
    prompt = workflow.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises((InputValidationError, ValueError)):
        workflow.configure_prompt(prompt, inputs)

    assert prompt == original


@pytest.mark.parametrize("first, second", [(1, 2), (1, 3), (2, 3)])
def test_anchored_guide_indices_must_be_distinct_before_upload_staging(
    monkeypatch: pytest.MonkeyPatch,
    first: int,
    second: int,
) -> None:
    workflow = _workflows()["minimax_h3_anchored_sprite_loop"]
    inputs = {
        **_default_inputs(workflow),
        f"guide_image_{first}": [Path(f"C:/uploads/guide_image_{first}.png")],
        f"guide_frame_{first}": "62",
        f"guide_image_{second}": [Path(f"C:/uploads/guide_image_{second}.png")],
        f"guide_frame_{second}": "62",
    }
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: pytest.fail("duplicate guide indices must not stage uploads"),
    )
    prompt = workflow.load_prompt()
    original = copy.deepcopy(prompt)

    with pytest.raises(ValueError, match="must be distinct"):
        workflow.configure_prompt(prompt, inputs)

    assert prompt == original


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
        outputs = tuple(workflow.outputs)
        if workflow_id == "minimax_h3_anchored_sprite_loop":
            assert [
                (output.id, output.node_id, output.shape) for output in outputs
            ] == [
                ("video", "save", "masonry"),
                ("frames", "save_frames", "masonry"),
                ("atlas", "save_atlas", "masonry"),
                ("receipt", "display_sampling_receipt", "code"),
                (
                    "normalization_receipt",
                    "display_normalization_receipt",
                    "code",
                ),
            ]
        else:
            assert len(outputs) == 1
            assert (outputs[0].id, outputs[0].node_id, outputs[0].shape) == (
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
        if workflow_id == "minimax_h3_anchored_sprite_loop":
            assert first["save_frames"]["inputs"] == {
                "images": ["sprite_normalize", 0],
                "filename_prefix": (
                    EXPECTED_PREFIXES[workflow_id]
                    + "/frames-256px-content-224px-bottom-16px-ref-0-12fps"
                ),
            }
            assert first["save_atlas"]["inputs"] == {
                "images": ["sprite_grid", 0],
                "filename_prefix": (
                    EXPECTED_PREFIXES[workflow_id]
                    + "/atlas-6x4-256px-content-224px-bottom-16px-ref-0-12fps"
                ),
            }


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
