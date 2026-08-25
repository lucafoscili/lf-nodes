"""Offline contract tests for the public Krea 2 Runner workflows."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
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
from modules.workflow_runner.services import workflow_service
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows import krea2 as workflow_module


EXPECTED_IDS = {
    "krea2_generate",
    "krea2_style_reference",
    "krea2_style_blend",
    "krea2_identity_edit",
    "krea2_character_restage",
    "krea2_outfit_change",
    "krea2_pose_change",
    "krea2_feature_edit",
    "krea2_character_restyle",
}
EXPECTED_CATALOGUE_NAMES = {
    "krea2_generate": "Generate Image",
    "krea2_style_reference": "Style Reference",
    "krea2_style_blend": "Blend Two Styles",
    "krea2_identity_edit": "Identity Edit",
    "krea2_character_restage": "Character Restage",
    "krea2_outfit_change": "Outfit Change",
    "krea2_pose_change": "Pose Change",
    "krea2_feature_edit": "Feature Edit",
    "krea2_character_restyle": "Character Restyle",
}
REID_IDS = {
    "krea2_character_restage",
    "krea2_outfit_change",
    "krea2_pose_change",
    "krea2_feature_edit",
    "krea2_character_restyle",
}
SAMPLING_CONTROL_IDS = EXPECTED_IDS - REID_IDS
FORBIDDEN_NODE_TYPES = {"Krea2ImageNode", "Krea2StyleReferenceNode"}
FORBIDDEN_VOCABULARY = ("velora", "stellaris", "azeroth", "sentinel", "sprite")


def _workflows() -> dict[str, Any]:
    return {workflow.id: workflow for workflow in workflow_module.WORKFLOWS}


def _default_inputs(workflow: Any) -> dict[str, Any]:
    return {
        cell.id: cell.props["lfValue"]
        for cell in workflow.inputs
        if "lfValue" in cell.props
    }


def _nodes_by_class(prompt: dict[str, Any], class_type: str) -> list[tuple[str, dict[str, Any]]]:
    return [
        (node_id, node)
        for node_id, node in prompt.items()
        if isinstance(node, dict) and node.get("class_type") == class_type
    ]


def _node_by_class(prompt: dict[str, Any], class_type: str) -> tuple[str, dict[str, Any]]:
    matches = _nodes_by_class(prompt, class_type)
    assert len(matches) == 1, f"expected one {class_type}, found {len(matches)}"
    return matches[0]


def _references(value: Any, target: str) -> bool:
    if isinstance(value, (list, tuple)):
        return bool(value and value[0] == target) or any(
            _references(item, target) for item in value
        )
    if isinstance(value, dict):
        return any(_references(item, target) for item in value.values())
    return False


def _common_inputs() -> dict[str, Any]:
    return {
        "prompt": "A graphic portrait with deliberate ink lines and moonlit colors",
        "model_name": workflow_module._LOCAL_MODELS[1],
        "aspect_ratio": "4:3 (Standard)",
        "seed": 1234,
        "steps": 9,
        "cfg": 1.2,
        "sampler_name": "heun",
        "scheduler": "karras",
    }


def test_public_family_uses_concise_context_aware_names() -> None:
    workflows = _workflows()

    assert set(workflows) == EXPECTED_IDS
    assert "krea2" in _WORKFLOW_MODULES
    assert {
        workflow_id: workflow.value for workflow_id, workflow in workflows.items()
    } == EXPECTED_CATALOGUE_NAMES

    for workflow in workflows.values():
        assert workflow.category == "Krea 2"
        assert not workflow.value.startswith(workflow.category)
        assert workflow.inputs
        assert workflow.outputs
        public_declaration = json.dumps(
            {
                "value": workflow.value,
                "description": workflow.description,
                "category": workflow.category,
                "inputs": [cell.to_dict() for cell in workflow.inputs],
                "outputs": [cell.to_dict() for cell in workflow.outputs],
            }
        ).lower()
        assert "local" not in public_declaration
        for cell in (*workflow.inputs, *workflow.outputs):
            assert cell.id
            assert cell.node_id
            assert cell.description, f"{workflow.id}:{cell.id} needs a description"


def test_public_graphs_use_no_hosted_partner_api_nodes() -> None:
    for workflow in _workflows().values():
        prompt = workflow.load_prompt()
        class_types = {
            node.get("class_type")
            for node in prompt.values()
            if isinstance(node, dict)
        }
        assert class_types.isdisjoint(FORBIDDEN_NODE_TYPES)
        assert "SaveImage" in class_types


def test_generate_graph_is_a_complete_local_text_to_image_chain() -> None:
    prompt = _workflows()["krea2_generate"].load_prompt()
    expected = {
        "UNETLoader",
        "CLIPLoader",
        "VAELoader",
        "CLIPTextEncode",
        "ConditioningZeroOut",
        "EmptySD3LatentImage",
        "ResolutionSelector",
        "KSampler",
        "VAEDecode",
        "SaveImage",
    }
    assert expected.issubset(
        {
            node["class_type"]
            for node in prompt.values()
            if isinstance(node, dict)
        }
    )
    assert not _nodes_by_class(prompt, "Krea2OstrisEditModelPatch")


@pytest.mark.parametrize(
    ("workflow_id", "expected_loaders"),
    [("krea2_style_reference", 1), ("krea2_style_blend", 2)],
)
def test_style_graphs_use_the_pinned_ostris_reference_stack(
    workflow_id: str,
    expected_loaders: int,
) -> None:
    workflow = _workflows()[workflow_id]
    prompt = workflow.load_prompt()
    assert workflow.configure_download is not None
    workflow.configure_download(prompt, _default_inputs(workflow))
    _node_by_class(prompt, "TextEncodeKrea2OstrisEdit")
    patch_id, patch = _node_by_class(prompt, "Krea2OstrisEditModelPatch")
    lora_id, lora = _node_by_class(prompt, "LoraLoaderModelOnly")
    _sampler_id, sampler = _node_by_class(prompt, "KSampler")

    assert len(_nodes_by_class(prompt, "LoadImage")) == expected_loaders
    assert lora["inputs"]["lora_name"] == workflow_module._STYLE_LORA
    assert prompt["unet"]["inputs"]["unet_name"] == workflow_module._OFFICIAL_KREA2_MODEL
    assert prompt["vae"]["inputs"]["vae_name"] == workflow_module._OFFICIAL_VAE
    assert patch["inputs"] == {"model": [lora_id, 0], "kv_cache": False}
    assert sampler["inputs"]["model"] == [patch_id, 0]


@pytest.mark.parametrize("workflow_id", sorted(REID_IDS))
def test_reid_recipes_match_the_published_engine_contract(workflow_id: str) -> None:
    workflow = _workflows()[workflow_id]
    prompt = workflow.load_prompt()
    assert workflow.configure_download is not None
    workflow.configure_download(prompt, _default_inputs(workflow))
    patch_id, patch = _node_by_class(prompt, "Krea2OstrisEditModelPatch")
    lora_id, lora = _node_by_class(prompt, "LoraLoaderModelOnly")
    _latent_id, latent = _node_by_class(prompt, "EmptyLatentImage")
    _scale_id, scale = _node_by_class(prompt, "ImageScaleToTotalPixels")
    _sampler_id, sampler = _node_by_class(prompt, "KSampler")
    encoders = _nodes_by_class(prompt, "TextEncodeKrea2OstrisEdit")
    reference_methods = _nodes_by_class(
        prompt, "FluxKontextMultiReferenceLatentMethod"
    )

    assert prompt["unet"]["inputs"]["unet_name"] == workflow_module._REID_MODEL
    assert prompt["vae"]["inputs"]["vae_name"] == workflow_module._REID_VAE
    assert lora["inputs"] == {
        "lora_name": workflow_module._REID_LORA,
        "strength_model": 1.0,
        "model": ["unet", 0],
    }
    assert patch["inputs"] == {"model": [lora_id, 0], "kv_cache": True}
    assert sampler["inputs"]["model"] == [patch_id, 0]
    assert {
        key: sampler["inputs"][key]
        for key in ("steps", "cfg", "sampler_name", "scheduler", "denoise")
    } == {
        "steps": 8,
        "cfg": 1.0,
        "sampler_name": "euler",
        "scheduler": "simple",
        "denoise": 1.0,
    }
    assert latent["inputs"] == {
        "width": ["resolution", 0],
        "height": ["resolution", 1],
        "batch_size": 1,
    }
    _resolution_id, resolution = _node_by_class(prompt, "ResolutionSelector")
    assert resolution["inputs"] == {
        "aspect_ratio": "2:3 (Portrait Photo)",
        "megapixels": 1.9,
        "multiple": 16,
    }
    assert scale["inputs"] == {
        "image": ["reference", 0],
        "upscale_method": "area",
        "megapixels": 0.140625,
        "resolution_steps": 16,
    }
    assert len(encoders) == 2
    assert {encoder["inputs"]["prompt"] for _node_id, encoder in encoders} == {
        "",
        prompt["positive_encode"]["inputs"]["prompt"],
    }
    assert all(
        encoder["inputs"]["image1"] == ["reference_scale", 0]
        for _node_id, encoder in encoders
    )
    assert len(reference_methods) == 2
    assert all(
        node["inputs"]["reference_latents_method"] == "index_timestep_zero"
        for _node_id, node in reference_methods
    )
    assert not _nodes_by_class(prompt, "ConditioningZeroOut")


def test_local_scalar_controls_map_to_the_prompt() -> None:
    for workflow_id in EXPECTED_IDS - REID_IDS:
        workflow = _workflows()[workflow_id]
        prompt = workflow.load_prompt()
        inputs = _common_inputs()
        if workflow_id == "krea2_style_reference":
            inputs["cfg"] = 1.0
            inputs["style_image"] = [Path("C:/uploads/style.png")]
        elif workflow_id == "krea2_style_blend":
            inputs.update(
                {
                    "cfg": 1.0,
                    "style_a_image": [Path("C:/uploads/a.png")],
                    "style_b_image": [Path("C:/uploads/b.png")],
                }
            )
        elif workflow_id == "krea2_identity_edit":
            inputs["identity_image"] = [Path("C:/uploads/identity.png")]

        original_resolver = workflow_module.resolve_load_image_reference
        workflow_module.resolve_load_image_reference = (
            lambda _inputs, name: f"lf_workflow_runner/{name}.png [input]"
        )
        try:
            workflow.configure_prompt(prompt, inputs)
        finally:
            workflow_module.resolve_load_image_reference = original_resolver

        assert prompt["unet"]["inputs"]["unet_name"] == inputs["model_name"]
        assert prompt["latent"]["inputs"] == {
            "width": ["resolution", 0],
            "height": ["resolution", 1],
            "batch_size": 1,
        }
        _resolution_id, resolution = _node_by_class(prompt, "ResolutionSelector")
        assert resolution["inputs"]["aspect_ratio"] == inputs["aspect_ratio"]
        assert resolution["inputs"]["multiple"] == 16
        assert {
            key: prompt["sampler"]["inputs"][key]
            for key in ("seed", "steps", "cfg", "sampler_name", "scheduler")
        } == {
            "seed": 1234,
            "steps": 9,
            "cfg": (
                1.0
                if workflow_id in {"krea2_style_reference", "krea2_style_blend"}
                else 1.2
            ),
            "sampler_name": "heun",
            "scheduler": "karras",
        }
        prompt_key = "text" if workflow_id == "krea2_generate" else "prompt"
        assert prompt["positive"]["inputs"][prompt_key] == inputs["prompt"]


def test_character_restage_maps_only_the_creative_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["krea2_character_restage"]
    reference = [Path("C:/uploads/character.png")]
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda inputs, name: (
            "lf_workflow_runner/character.png [input]"
            if inputs[name] == reference
            else pytest.fail("unexpected reference")
        ),
    )
    prompt = workflow.load_prompt()
    workflow.configure_prompt(
        prompt,
        {
            "reference_image": reference,
            "prompt": "The same character sitting at a pub table, holding a cocktail",
            "aspect_ratio": "3:4 (Portrait Standard)",
            "seed": 240831,
        },
    )

    assert prompt["reference"]["inputs"]["image"].endswith(
        "character.png [input]"
    )
    assert prompt["unet"]["inputs"]["unet_name"] == workflow_module._REID_MODEL
    assert prompt["positive_encode"]["inputs"]["prompt"].endswith(
        "holding a cocktail"
    )
    assert prompt["latent"]["inputs"] == {
        "width": ["resolution", 0],
        "height": ["resolution", 1],
        "batch_size": 1,
    }
    _resolution_id, resolution = _node_by_class(prompt, "ResolutionSelector")
    assert resolution["inputs"]["aspect_ratio"] == "3:4 (Portrait Standard)"
    assert prompt["sampler"]["inputs"]["seed"] == 240831
    assert prompt["sampler"]["inputs"]["steps"] == 8
    assert prompt["patch"]["inputs"]["kv_cache"] is True
    assert prompt["save"]["inputs"]["filename_prefix"].endswith(
        "CharacterRestage/seed-240831"
    )


def test_reid_recipe_cards_have_distinct_prompts_and_focused_controls() -> None:
    workflows = _workflows()
    defaults: set[str] = set()
    for workflow_id in REID_IDS:
        workflow = workflows[workflow_id]
        assert workflow.workflow_path.name == "krea2_character_restage.json"
        cell_ids = [cell.id for cell in workflow.inputs]
        assert cell_ids == [
            "reference_image",
            "prompt",
            "model_name",
            "aspect_ratio",
            "seed",
        ]
        prompt_cell = next(cell for cell in workflow.inputs if cell.id == "prompt")
        default = prompt_cell.props["lfValue"]
        assert isinstance(default, str) and "same character" in default.lower()
        assert default not in defaults
        defaults.add(default)


def test_safe_krea_cards_expose_curated_sampling_controls() -> None:
    workflows = _workflows()
    expected_sampler_values = [
        "euler",
        "euler_ancestral",
        "heun",
        "dpmpp_2m",
        "dpmpp_2m_sde",
    ]
    expected_scheduler_values = [
        "beta",
        "simple",
        "normal",
        "karras",
        "sgm_uniform",
    ]

    for workflow_id in SAMPLING_CONTROL_IDS:
        cells = {cell.id: cell for cell in workflows[workflow_id].inputs}
        sampler = cells["sampler_name"]
        scheduler = cells["scheduler"]
        assert sampler.shape == scheduler.shape == "select"
        assert sampler.props["lfValue"] == "euler"
        assert scheduler.props["lfValue"] == "beta"
        assert [
            option["workflowValue"]
            for option in sampler.props["lfDataset"]["nodes"]
        ] == expected_sampler_values
        assert [
            option["workflowValue"]
            for option in scheduler.props["lfDataset"]["nodes"]
        ] == expected_scheduler_values
        assert sampler.description and scheduler.description

        prompt = workflows[workflow_id].load_prompt()
        assert prompt["sampler"]["inputs"]["sampler_name"] == "euler"
        assert prompt["sampler"]["inputs"]["scheduler"] == "beta"

    for workflow_id in REID_IDS:
        cell_ids = {cell.id for cell in workflows[workflow_id].inputs}
        assert "sampler_name" not in cell_ids
        assert "scheduler" not in cell_ids


def test_krea_cards_surface_curated_aspect_ratios_instead_of_raw_canvas_dimensions() -> None:
    workflows = _workflows()
    square_ids = {
        "krea2_generate",
        "krea2_style_reference",
        "krea2_style_blend",
    }
    portrait_ids = EXPECTED_IDS - square_ids

    for workflow_id in square_ids:
        cells = {cell.id: cell for cell in workflows[workflow_id].inputs}
        assert cells["aspect_ratio"].props["lfValue"] == "1:1 (Square)"

    for workflow_id in portrait_ids:
        cells = {cell.id: cell for cell in workflows[workflow_id].inputs}
        assert cells["aspect_ratio"].props["lfValue"] == "2:3 (Portrait Photo)"

    for workflow in workflows.values():
        cell_ids = {cell.id for cell in workflow.inputs}
        assert "aspect_ratio" in cell_ids
        assert "width" not in cell_ids
        assert "height" not in cell_ids
        aspect = next(cell for cell in workflow.inputs if cell.id == "aspect_ratio")
        assert aspect.shape == "select"
        assert [
            node["workflowValue"] for node in aspect.props["lfDataset"]["nodes"]
        ] == list(workflow_module._ASPECT_RATIO_TARGETS)


def test_reid_cards_surface_validated_and_experimental_base_profiles() -> None:
    for workflow_id in REID_IDS:
        cells = {cell.id: cell for cell in _workflows()[workflow_id].inputs}
        model = cells["model_name"]
        assert model.props["lfValue"] == workflow_module._REID_MODEL
        options = model.props["lfDataset"]["nodes"]
        assert [option["workflowValue"] for option in options] == list(
            workflow_module._REID_MODELS
        )
        assert "validated" in options[0]["value"].lower()
        assert all("experimental" in option["value"].lower() for option in options[1:])


def test_style_and_identity_cards_default_to_the_documented_adapter_profile() -> None:
    for workflow_id in (
        "krea2_style_reference",
        "krea2_style_blend",
        "krea2_identity_edit",
    ):
        cells = {cell.id: cell for cell in _workflows()[workflow_id].inputs}
        model = cells["model_name"]
        assert model.props["lfValue"] == workflow_module._ADAPTER_DEFAULT_MODEL
        assert model.props["lfTextfieldProps"]["lfHelper"]["value"]
        options = model.props["lfDataset"]["nodes"]
        assert options[0]["workflowValue"] == workflow_module._OFFICIAL_KREA2_MODEL
        assert "default" in options[0]["value"].lower()
        assert all("experimental" in option["value"].lower() for option in options[1:])


def test_generation_cards_surface_all_local_checkpoint_profiles() -> None:
    for workflow_id in ("krea2_generate", "krea2_style_reference", "krea2_style_blend"):
        cells = {cell.id: cell for cell in _workflows()[workflow_id].inputs}
        model = cells["model_name"]
        expected_models = (
            workflow_module._LOCAL_MODELS
            if workflow_id == "krea2_generate"
            else workflow_module._ADAPTER_MODELS
        )
        assert [
            option["workflowValue"] for option in model.props["lfDataset"]["nodes"]
        ] == list(expected_models)
        assert model.props["lfValue"] == (
            workflow_module._ADAPTER_DEFAULT_MODEL
            if workflow_id != "krea2_generate"
            else workflow_module._LOCAL_DEFAULT_MODEL
        )
        assert any(
            "lustify" in option["value"].lower()
            for option in model.props["lfDataset"]["nodes"]
        )


def test_style_cards_pin_cfg_one_instead_of_exposing_an_invalid_cfg_sweep() -> None:
    for workflow_id in ("krea2_style_reference", "krea2_style_blend"):
        workflow = _workflows()[workflow_id]
        cell_ids = {cell.id for cell in workflow.inputs}
        assert "cfg" not in cell_ids
        prompt = workflow.load_prompt()
        assert prompt["sampler"]["inputs"]["cfg"] == 1.0
        with pytest.raises(ValueError, match="cfg must be between 1.0 and 1.0"):
            workflow.configure_download(prompt, {**_default_inputs(workflow), "cfg": 1.2})


def test_reid_alternate_base_is_explicitly_mapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["krea2_character_restage"]
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: "lf_workflow_runner/character.png [input]",
    )
    prompt = workflow.load_prompt()

    workflow.configure_prompt(
        prompt,
        {
            "reference_image": [Path("C:/uploads/character.png")],
            "prompt": "The same character in a controlled portrait test",
            "model_name": workflow_module._REID_MODELS[1],
        },
    )

    assert prompt["unet"]["inputs"]["unet_name"] == workflow_module._REID_MODELS[1]


@pytest.mark.parametrize(
    ("workflow_id", "output_folder"),
    [
        ("krea2_outfit_change", "OutfitChange"),
        ("krea2_pose_change", "PoseChange"),
        ("krea2_feature_edit", "FeatureEdit"),
        ("krea2_character_restyle", "CharacterRestyle"),
    ],
)
def test_reid_recipe_writes_to_its_own_output_folder(
    monkeypatch: pytest.MonkeyPatch,
    workflow_id: str,
    output_folder: str,
) -> None:
    workflow = _workflows()[workflow_id]
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args: "lf_workflow_runner/character.png [input]",
    )
    prompt_cell = next(cell for cell in workflow.inputs if cell.id == "prompt")
    prompt = workflow.load_prompt()
    workflow.configure_prompt(
        prompt,
        {
            "reference_image": [Path("C:/uploads/character.png")],
            "prompt": prompt_cell.props["lfValue"],
            "seed": 73,
        },
    )
    assert prompt["save"]["inputs"]["filename_prefix"].endswith(
        f"{output_folder}/seed-73"
    )


def test_style_reference_resolves_upload_and_strength(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["krea2_style_reference"]
    path = [Path("C:/uploads/style.png")]
    calls: list[str] = []

    def resolve(inputs: dict[str, Any], name: str) -> str:
        calls.append(name)
        assert inputs[name] == path
        return "lf_workflow_runner/style.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    prompt = workflow.load_prompt()
    workflow.configure_prompt(
        prompt,
        {
            **_common_inputs(),
            "cfg": 1.0,
            "style_image": path,
            "style_strength": 0.7,
        },
    )

    assert calls == ["style_image"]
    assert prompt["style"]["inputs"]["image"] == "lf_workflow_runner/style.png [input]"
    assert prompt["lora"]["inputs"]["strength_model"] == pytest.approx(0.7)
    assert prompt["positive"]["inputs"]["image1"] == ["style", 0]


def test_style_blend_resolves_two_ordered_uploads_with_one_honest_strength(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["krea2_style_blend"]
    paths = {
        "style_a_image": [Path("C:/uploads/a.png")],
        "style_b_image": [Path("C:/uploads/b.png")],
    }
    calls: list[str] = []

    def resolve(_inputs: dict[str, Any], name: str) -> str:
        calls.append(name)
        return f"lf_workflow_runner/{name}.png [input]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    prompt = workflow.load_prompt()
    workflow.configure_prompt(
        prompt,
        {
            **_common_inputs(),
            "cfg": 1.0,
            **paths,
            "style_strength": 1.25,
        },
    )

    assert calls == ["style_a_image", "style_b_image"]
    assert prompt["style_a"]["inputs"]["image"].endswith("style_a_image.png [input]")
    assert prompt["style_b"]["inputs"]["image"].endswith("style_b_image.png [input]")
    assert prompt["lora"]["inputs"]["strength_model"] == pytest.approx(1.25)
    assert prompt["positive"]["inputs"]["image1"] == ["style_a", 0]
    assert prompt["positive"]["inputs"]["image2"] == ["style_b", 0]


def test_identity_edit_handles_identity_plus_scene_and_identity_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflows()["krea2_identity_edit"]
    paths = {
        "identity_image": [Path("C:/uploads/identity.png")],
        "scene_image": [Path("C:/uploads/scene.png")],
    }
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda _inputs, name: f"lf_workflow_runner/{name}.png [input]",
    )

    prompt = workflow.load_prompt()
    workflow.configure_prompt(prompt, {**_common_inputs(), **paths})
    assert prompt["identity"]["inputs"]["image"].endswith("identity_image.png [input]")
    assert prompt["scene"]["inputs"]["image"].endswith("scene_image.png [input]")
    _node_by_class(prompt, "Krea2EditModelPatch")

    prompt_without_scene = workflow.load_prompt()
    workflow.configure_prompt(
        prompt_without_scene,
        {**_common_inputs(), "identity_image": paths["identity_image"]},
    )
    assert "scene" not in prompt_without_scene
    assert "scene_latent" not in prompt_without_scene
    assert not _references(prompt_without_scene, "scene")


@pytest.mark.parametrize(
    ("workflow_id", "inputs", "input_name"),
    [
        ("krea2_generate", {"prompt": "x", "model_name": "not-a-model"}, "model_name"),
        ("krea2_style_reference", _common_inputs(), "style_image"),
        (
            "krea2_style_blend",
            {**_common_inputs(), "style_a_image": [Path("C:/uploads/a.png")]},
            "style_b_image",
        ),
        ("krea2_identity_edit", {"prompt": "x"}, "identity_image"),
        ("krea2_character_restage", {"prompt": "x"}, "reference_image"),
        ("krea2_outfit_change", {"prompt": "x"}, "reference_image"),
        ("krea2_pose_change", {"prompt": "x"}, "reference_image"),
        ("krea2_feature_edit", {"prompt": "x"}, "reference_image"),
        ("krea2_character_restyle", {"prompt": "x"}, "reference_image"),
        (
            "krea2_character_restage",
            {
                "prompt": "x",
                "reference_image": [Path("C:/uploads/character.png")],
                "model_name": "not-a-model",
            },
            "model_name",
        ),
        (
            "krea2_style_reference",
            {
                **_common_inputs(),
                "style_image": [Path("C:/uploads/style.png")],
                "cfg": 1.0,
                "sampler_name": "not-a-sampler",
            },
            "sampler_name",
        ),
        (
            "krea2_identity_edit",
            {
                **_common_inputs(),
                "identity_image": [Path("C:/uploads/identity.png")],
                "scheduler": "not-a-scheduler",
            },
            "scheduler",
        ),
    ],
)
def test_invalid_inputs_fail_before_staging_upload(
    monkeypatch: pytest.MonkeyPatch,
    workflow_id: str,
    inputs: dict[str, Any],
    input_name: str,
) -> None:
    workflow = _workflows()[workflow_id]
    monkeypatch.setattr(
        workflow_module,
        "resolve_load_image_reference",
        lambda *_args, **_kwargs: pytest.fail("invalid request must not stage uploads"),
    )
    with pytest.raises(InputValidationError) as error:
        workflow.configure_prompt(workflow.load_prompt(), inputs)
    assert error.value.input_name == input_name


def test_invalid_aspect_ratio_fails_closed() -> None:
    workflow = _workflows()["krea2_generate"]
    with pytest.raises(InputValidationError) as error:
        workflow.configure_prompt(
            workflow.load_prompt(),
            {**_common_inputs(), "aspect_ratio": "10:7 (Invented)"},
        )
    assert error.value.input_name == "aspect_ratio"


def test_all_aspect_ratio_profiles_are_maximal_safe_core_canvases() -> None:
    for aspect_ratio in workflow_module._ASPECT_RATIO_TARGETS:
        megapixels, width, height = workflow_module._resolution_for(aspect_ratio)
        assert width % 16 == height % 16 == 0
        assert 256 <= width <= 2048
        assert 256 <= height <= 2048
        assert width * height <= 2_000_000
        assert megapixels > 0
        (width_ratio, height_ratio), _ = workflow_module._ASPECT_RATIO_TARGETS[aspect_ratio]
        scale = math.sqrt(megapixels * 1024 * 1024 / (width_ratio * height_ratio))
        assert width == round(width_ratio * scale / 16) * 16
        assert height == round(height_ratio * scale / 16) * 16


@pytest.mark.parametrize(
    ("workflow_id", "output_folder"),
    [
        ("krea2_generate", "Generate"),
        ("krea2_style_reference", "StyleReference"),
        ("krea2_style_blend", "StyleBlend"),
        ("krea2_identity_edit", "IdentityEdit"),
        ("krea2_character_restage", "CharacterRestage"),
        ("krea2_outfit_change", "OutfitChange"),
        ("krea2_pose_change", "PoseChange"),
        ("krea2_feature_edit", "FeatureEdit"),
        ("krea2_character_restyle", "CharacterRestyle"),
    ],
)
def test_downloaded_krea_template_matches_the_visible_card_defaults(
    monkeypatch: pytest.MonkeyPatch,
    workflow_id: str,
    output_folder: str,
) -> None:
    workflow = _workflows()[workflow_id]
    monkeypatch.setattr(workflow_service, "_get_workflow", lambda _id: workflow)

    prompt = workflow_service.get_workflow_content(workflow_id)
    assert prompt is not None
    cells = {cell.id: cell for cell in workflow.inputs}
    assert prompt["latent"]["inputs"] == {
        "width": ["resolution", 0],
        "height": ["resolution", 1],
        "batch_size": 1,
    }
    _resolution_id, resolution = _node_by_class(prompt, "ResolutionSelector")
    expected_aspect = (
        "1:1 (Square)"
        if workflow_id in {"krea2_generate", "krea2_style_reference", "krea2_style_blend"}
        else "2:3 (Portrait Photo)"
    )
    assert resolution["inputs"] == {
        "aspect_ratio": expected_aspect,
        "megapixels": workflow_module._ASPECT_RATIO_TARGETS[expected_aspect][1],
        "multiple": 16,
    }
    assert prompt["save"]["inputs"]["filename_prefix"].endswith(
        f"{output_folder}/seed-42"
    )
    assert all(
        isinstance(node.get("_meta", {}).get("title"), str)
        and node["_meta"]["title"]
        for node in prompt.values()
    )

    if workflow_id == "krea2_identity_edit":
        assert "scene" not in prompt
        assert "scene_latent" not in prompt
        assert not _references(prompt, "scene")
        assert prompt["patch"]["inputs"]["source_image"] == ["identity", 0]

    expected_prompt = cells["prompt"].props["lfValue"]
    if workflow_id == "krea2_generate":
        actual_prompt = prompt["positive"]["inputs"]["text"]
    elif workflow_id in REID_IDS:
        actual_prompt = prompt["positive_encode"]["inputs"]["prompt"]
    else:
        actual_prompt = prompt["positive"]["inputs"]["prompt"]
    assert actual_prompt == expected_prompt

    if workflow_id in SAMPLING_CONTROL_IDS:
        assert prompt["sampler"]["inputs"]["sampler_name"] == "euler"
        assert prompt["sampler"]["inputs"]["scheduler"] == "beta"
    else:
        assert prompt["sampler"]["inputs"]["sampler_name"] == "euler"
        assert prompt["sampler"]["inputs"]["scheduler"] == "simple"


def test_krea_model_and_adapter_paths_follow_the_host_separator() -> None:
    assert workflow_module._OFFICIAL_KREA2_MODEL == os.path.join(
        "KR2", "krea2_turbo_int8_convrot.safetensors"
    )
    assert workflow_module._STYLE_LORA == os.path.join(
        "KR2", "krea2_style_reference.safetensors"
    )
    assert workflow_module._IDENTITY_LORA == os.path.join(
        "KR2", "krea2_identity_edit_v1_2.safetensors"
    )
    assert workflow_module._REID_LORA == os.path.join(
        "KR2", "krea2_reid_rank32.safetensors"
    )
    assert workflow_module._LUSTIFY_MODEL == os.path.join(
        "KR2", "lustifyNSFWCheckpoint_v10Krea2.safetensors"
    )

    for workflow in _workflows().values():
        if workflow.configure_download is None:
            continue
        defaults = _default_inputs(workflow)
        prompt = workflow.load_prompt()
        workflow.configure_download(prompt, defaults)
        assert prompt["unet"]["inputs"]["unet_name"] in (
            workflow_module._LOCAL_MODELS
        )
        if "lora" in prompt:
            assert os.path.dirname(prompt["lora"]["inputs"]["lora_name"]) == "KR2"


def test_public_workflows_are_consumer_agnostic() -> None:
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

    for forbidden in FORBIDDEN_VOCABULARY:
        assert forbidden not in public_text
