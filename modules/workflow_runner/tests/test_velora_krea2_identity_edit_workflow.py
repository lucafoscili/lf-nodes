"""Offline contract tests for the one- or two-reference Krea 2 proof."""

from __future__ import annotations

import hashlib
import json
import pkgutil
import sys
import types

import pytest

# Keep graph contracts independent of ComfyUI, Torch, and the rest of LF.
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)
# Importing ``modules.workflow_runner`` normally loads the host's Comfy/Torch
# runtime just to expose CONFIG. The graph contract under test needs neither.
config_module = types.ModuleType("modules.workflow_runner.config")
config_module.CONFIG = object()
sys.modules.setdefault("modules.workflow_runner.config", config_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import custom as custom_workflows
from modules.workflow_runner.workflows.custom import velora_krea2_identity_edit as subject


def _inputs() -> dict[str, object]:
    return {
        "scene_image": r"C:\\fixtures\\scene.png",
        "identity_image": r"C:\\fixtures\\identity.png",
        "prompt": "Restore the woman from reference image 2 while preserving the scene.",
        "model_name": "KR2\\darkBeast30BF16INT8_darkBeastKREA2FP8.safetensors",
        "width": "1024",
        "height": "1536",
        "seed": "77",
        "steps": "10",
        "cfg": "1",
        "ref_boost": "4",
        "grounding_px": "1024",
    }


def _appearance_wire() -> dict[str, object]:
    return {
        "schema": "velora.krea2-appearance-buckets.v1",
        "planReceipt": "sha256:" + "a" * 64,
        "selectionMode": "weighted_sha256_v1",
        "samplerSeed": 1_458_331_362_111_639,
        "buckets": [
            {"seed": 11, "json": {"silver-white moon glow": 1}},
            {"seed": 12, "json": {"violet skin": 1, "blue-violet skin": 3}},
        ],
    }


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_registry_discovers_the_custom_workflow() -> None:
    names = {name for _, name, _ in pkgutil.iter_modules(custom_workflows.__path__)}
    assert "velora_krea2_identity_edit" in names
    assert subject.WORKFLOW.id == "velora_krea2_identity_edit"
    assert [cell.id for cell in subject.WORKFLOW.inputs[:3]] == [
        "scene_image",
        "identity_image",
        "prompt",
    ]
    assert len(list(subject.WORKFLOW.outputs)) == 1
    assert subject.WORKFLOW.outputs[0].id == "image"
    assert subject.input_scene.required is False
    assert subject.WORKFLOW.cells_as_dict("inputs")["scene_image"]["required"] is False


def test_configure_keeps_scene_first_and_identity_second(monkeypatch) -> None:
    calls: list[str] = []

    def resolve(inputs, name):
        calls.append(name)
        return f"{name}.png [input]"

    monkeypatch.setattr(subject, "resolve_load_image_reference", resolve)
    prompt = subject.WORKFLOW.load_prompt()
    subject.WORKFLOW.configure_prompt(prompt, _inputs())

    assert calls == ["scene_image", "identity_image"]
    assert prompt["scene"]["inputs"]["image"] == "scene_image.png [input]"
    assert prompt["identity"]["inputs"]["image"] == "identity_image.png [input]"
    assert prompt["positive"]["inputs"]["image"] == ["scene", 0]
    assert prompt["positive"]["inputs"]["image_b"] == ["identity", 0]
    assert prompt["patch"]["inputs"]["source_latent"] == ["scene_latent", 0]
    assert prompt["patch"]["inputs"]["source_latent_b"] == ["identity_latent", 0]


def test_configure_without_appearance_wire_is_the_pre_extension_graph(monkeypatch) -> None:
    """The optional compiler cannot perturb historical Krea submissions."""

    monkeypatch.setattr(
        subject,
        "resolve_load_image_reference",
        lambda _inputs, name: f"{name}.png [input]",
    )
    prompt = subject.WORKFLOW.load_prompt()
    subject.WORKFLOW.configure_prompt(prompt, _inputs())

    # Captured immediately before adding optional appearance support. The
    # canonical serializer is part of this regression contract, not Comfy UI.
    assert _canonical_hash(prompt) == (
        "5e3cfefbcf73f4bb0b7feec51bd46ae904821f63740bd71d32d703489b76b520"
    )
    assert not any(node_id.startswith("appearance_") for node_id in prompt)


def test_identity_only_configure_without_appearance_wire_is_the_pre_extension_graph(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        subject,
        "resolve_load_image_reference",
        lambda _inputs, name: f"{name}.png [input]",
    )
    inputs = _inputs()
    inputs.update(
        {
            "scene_image": "",
            "prompt": "Create a moon priestess.",
            "model_name": "KR2\\moodyKrea2Mix_v60.safetensors",
            "seed": 42,
            "ref_boost": 2,
        }
    )
    prompt = subject.WORKFLOW.load_prompt()
    subject.WORKFLOW.configure_prompt(prompt, inputs)

    assert _canonical_hash(prompt) == (
        "5b8b3f6fb47aec386ad24cdbf969fe51c190c45c64c0cdb50a5214ab7296af64"
    )
    assert not any(node_id.startswith("appearance_") for node_id in prompt)


def test_configure_compiles_weighted_appearance_buckets_into_existing_lf_nodes(monkeypatch) -> None:
    monkeypatch.setattr(
        subject,
        "resolve_load_image_reference",
        lambda _inputs, name: f"{name}.png [input]",
    )
    inputs = _inputs()
    inputs["appearance_buckets"] = json.dumps(_appearance_wire())
    prompt = subject.WORKFLOW.load_prompt()
    subject.WORKFLOW.configure_prompt(prompt, inputs)

    assert prompt["sampler"]["inputs"]["seed"] == 1_458_331_362_111_639
    assert prompt["save"]["inputs"]["filename_prefix"].endswith(
        "seed-1458331362111639"
    )
    assert prompt["positive"]["inputs"]["prompt"] == ["appearance_wall", 0]
    assert prompt["appearance_json_01"] == {
        "class_type": "LF_WriteJSON",
        "inputs": {"ui_widget": '{"silver-white moon glow":1}'},
        "_meta": {"title": "Velora appearance bucket 01"},
    }
    assert prompt["appearance_pick_01"]["inputs"] == {
        "seed": 11,
        "json_input": ["appearance_json_01", 0],
        "selection_mode": "weighted_sha256_v1",
    }
    assert prompt["appearance_wall"]["inputs"] == {
        "separator": ", ",
        "text_1": _inputs()["prompt"],
        "text_2": ["appearance_pick_01", 0],
        "text_3": ["appearance_pick_02", 0],
        "shuffle_inputs": False,
        "ui_widget": '{"planReceipt":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","selectionMode":"weighted_sha256_v1"}',
    }


@pytest.mark.parametrize(
    "mutate",
    [
        lambda wire: wire.update({"schema": "velora.not-this.v1"}),
        lambda wire: wire.update({"planReceipt": "sha256:BAD"}),
        lambda wire: wire.update({"selectionMode": "uniform_legacy"}),
        lambda wire: wire.update({"samplerSeed": 2**53}),
        lambda wire: wire.update({"unexpected": True}),
        lambda wire: wire.update({"buckets": []}),
        lambda wire: wire["buckets"][0].update({"seed": True}),
        lambda wire: wire["buckets"][0].update({"json": {"violet skin": 0}}),
        lambda wire: wire["buckets"][0].update({"json": {"violet skin": 1.0}}),
        lambda wire: wire["buckets"][0].update({"json": {"violet, skin": 1}}),
        lambda wire: wire["buckets"][0].update({"json": {" violet skin": 1}}),
    ],
)
def test_appearance_runtime_wire_fails_closed(monkeypatch, mutate) -> None:
    monkeypatch.setattr(
        subject,
        "resolve_load_image_reference",
        lambda _inputs, name: f"{name}.png [input]",
    )
    wire = _appearance_wire()
    mutate(wire)
    inputs = _inputs()
    inputs["appearance_buckets"] = wire

    with pytest.raises((InputValidationError, ValueError)):
        subject.WORKFLOW.configure_prompt(subject.WORKFLOW.load_prompt(), inputs)


@pytest.mark.parametrize("scene_value", [None, "", [], ()])
def test_configure_uses_identity_as_the_only_reference_when_scene_is_omitted(
    monkeypatch, scene_value
) -> None:
    calls: list[str] = []

    def resolve(inputs, name):
        calls.append(name)
        return f"{name}.png [input]"

    monkeypatch.setattr(subject, "resolve_load_image_reference", resolve)
    inputs = _inputs()
    inputs["scene_image"] = scene_value
    prompt = subject.WORKFLOW.load_prompt()
    subject.WORKFLOW.configure_prompt(prompt, inputs)

    assert calls == ["identity_image"]
    assert "scene" not in prompt
    assert "scene_latent" not in prompt
    assert prompt["identity"]["inputs"]["image"] == "identity_image.png [input]"
    assert prompt["patch"]["inputs"]["source_latent"] == ["identity_latent", 0]
    assert prompt["patch"]["inputs"]["source_image"] == ["identity", 0]
    assert "source_latent_b" not in prompt["patch"]["inputs"]
    assert "source_image_b" not in prompt["patch"]["inputs"]
    assert prompt["positive"]["inputs"]["image"] == ["identity", 0]
    assert prompt["negative"]["inputs"]["image"] == ["identity", 0]
    assert "image_b" not in prompt["positive"]["inputs"]
    assert "image_b" not in prompt["negative"]["inputs"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("identity_image", ""),
        ("prompt", "   "),
        ("steps", 7),
        ("width", 1025),
        ("model_name", "KR2/not-local.safetensors"),
    ],
)
def test_invalid_required_inputs_and_limits_fail_before_queueing(monkeypatch, field, value) -> None:
    monkeypatch.setattr(subject, "resolve_load_image_reference", lambda _inputs, name: f"{name}.png [input]")
    inputs = _inputs()
    inputs[field] = value

    with pytest.raises((InputValidationError, ValueError)):
        subject.WORKFLOW.configure_prompt(subject.WORKFLOW.load_prompt(), inputs)


def test_graph_has_fixed_assets_and_pre_sampling_target_latent_wiring() -> None:
    graph = json.loads(subject.WORKFLOW.workflow_path.read_text(encoding="utf-8"))

    assert graph["clip"]["inputs"] == {
        "clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2"
    }
    assert graph["vae"]["inputs"]["vae_name"] == "krea2RealVae_v10.safetensors"
    assert graph["lora"]["inputs"]["lora_name"] == "KR2\\krea2_identity_edit_v1_2.safetensors"
    assert graph["patch"]["class_type"] == "Krea2EditModelPatch"
    assert graph["positive"]["class_type"] == "Krea2EditGroundedEncode"
    assert graph["negative"]["inputs"]["prompt"] == ""
    assert graph["patch"]["inputs"]["target_latent"] == ["latent", 0]
    assert graph["sampler"]["inputs"]["latent_image"] == ["latent", 0]
    assert graph["save"]["class_type"] == "SaveImage"
    assert graph["save"]["inputs"]["images"] == ["decode", 0]


def test_submission_policy_uses_a_reviewed_4090_budget() -> None:
    policy = subject.WORKFLOW.submission_policy
    assert policy is not None
    assert policy.provider_id == "velora_guarded_v1"
    assert policy.expected_vram_mb == 20_000
    assert policy.max_duration_seconds == 600
    assert policy.required is True
