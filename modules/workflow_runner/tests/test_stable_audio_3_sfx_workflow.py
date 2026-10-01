"""Declaration-only sound-effects contracts; no models, audio server, or GPU."""

import copy

import pytest

from modules.workflow_runner.services.readiness import (
    WorkflowReadinessScanner,
    evaluate_workflow_readiness,
)
from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows.stable_audio_3_sfx import WORKFLOW


def test_small_generic_block_is_registered_and_every_knob_has_help():
    assert WORKFLOW.id in _WORKFLOW_MODULES
    assert WORKFLOW.value == "Sound Effects"
    assert WORKFLOW.category == "Stable Audio 3"
    assert [(cell.id, cell.required) for cell in WORKFLOW.inputs] == [
        ("prompt", True), ("duration", False), ("seed", False),
    ]
    assert all(cell.props["lfHelper"]["value"] for cell in WORKFLOW.inputs)
    assert WORKFLOW.card is not None
    assert WORKFLOW.card.hero is not None
    assert WORKFLOW.card.hero.asset == "audio/hearth.webp"


def test_medium_recipe_stays_native_and_locked():
    graph = WORKFLOW.load_prompt()
    assert graph["checkpoint"]["inputs"] == {
        "ckpt_name": "stable_audio_3_medium.safetensors",
    }
    assert graph["text_encoder"]["inputs"] == {
        "clip_name": "t5gemma_b_b_ul2.safetensors",
        "type": "stable_audio", "device": "default",
    }
    assert graph["sample"]["inputs"] == {
        "model": ["checkpoint", 0], "positive": ["positive", 0],
        "negative": ["negative", 0], "latent_image": ["latent", 0],
        "seed": 42, "steps": 8, "cfg": 1.0, "sampler_name": "lcm",
        "scheduler": "simple", "denoise": 1.0,
    }
    assert graph["decode"]["inputs"] == {
        "samples": ["sample", 0], "vae": ["checkpoint", 2],
    }
    assert graph["save_audio"]["class_type"] == "LF_SaveAudio"
    assert graph["save_audio"]["inputs"]["audio"] == ["decode", 0]
    assert graph["display_receipt"]["inputs"]["json_input"] == ["save_audio", 1]
    assert not any(node["class_type"].startswith("LLM") for node in graph.values())
    assert len(graph) == 9


def test_download_defaults_match_form_and_packaged_graph():
    graph = WORKFLOW.load_prompt()
    expected = copy.deepcopy(graph)
    defaults = {cell.id: cell.props["lfValue"] for cell in WORKFLOW.inputs}
    WORKFLOW.configure_prompt(graph, defaults)
    assert graph == expected
    WORKFLOW.configure_download(graph, {})
    assert graph == expected


def test_controls_wire_prompt_seconds_seed_and_output_prefix_only():
    graph = WORKFLOW.load_prompt()
    sampler = graph["sample"]["inputs"].copy()
    WORKFLOW.configure_prompt(graph, {
        "prompt": "  One axe hitting dry wood, then silence.  ",
        "duration": "3.5", "seed": "84", "steps": 100, "cfg": 7,
    })
    assert graph["positive"]["inputs"]["text"] == (
        "TrackType: SFX, One axe hitting dry wood, then silence."
    )
    assert graph["negative"]["inputs"]["text"] == ""
    assert graph["latent"]["inputs"] == {"seconds": 3.5, "batch_size": 1}
    assert graph["sample"]["inputs"] == {**sampler, "seed": 84}
    assert graph["save_audio"]["inputs"]["filename_prefix"].endswith("sfx-seed-84")


def test_existing_sfx_tag_is_not_duplicated():
    graph = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(graph, {"prompt": "TrackType: SFX, A short knock."})
    assert graph["positive"]["inputs"]["text"] == "TrackType: SFX, A short knock."


@pytest.mark.parametrize("value", [None, "", "  ", [], 7, True])
def test_prompt_is_required(value):
    with pytest.raises(InputValidationError):
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), {"prompt": value})


@pytest.mark.parametrize("value", [0, -1, 380.1, "nan", "inf", True, [], "no"])
def test_invalid_duration_is_rejected_before_mutating_graph(value):
    graph = WORKFLOW.load_prompt()
    before = copy.deepcopy(graph)
    with pytest.raises(ValueError):
        WORKFLOW.configure_prompt(graph, {"prompt": "Fire.", "duration": value})
    assert graph == before


@pytest.mark.parametrize("value", [1, 380])
def test_medium_duration_boundaries(value):
    graph = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(graph, {"prompt": "Fire.", "duration": value})
    assert graph["latent"]["inputs"]["seconds"] == value


@pytest.mark.parametrize("value", [-1, 1.5, True, 1 << 53, "nan"])
def test_invalid_seed_is_rejected(value):
    with pytest.raises(ValueError):
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), {"prompt": "Fire.", "seed": value})


def test_missing_models_are_setup_required_and_both_components_admit_the_block():
    graph = WORKFLOW.load_prompt()
    models = {}
    scanner = WorkflowReadinessScanner(
        node_mapping_loader=lambda: {node["class_type"]: object() for node in graph.values()},
        model_filename_loader=lambda category: models.get(category, ()),
    )
    missing = evaluate_workflow_readiness(WORKFLOW, scanner=scanner)
    assert missing["status"] == "setup_required"
    assert len(missing["issues"]) == 2
    models.update({
        "checkpoints": ["stable_audio_3_medium.safetensors"],
        "text_encoders": ["t5gemma_b_b_ul2.safetensors"],
    })
    # A scanner intentionally caches one scan; the next readiness request is fresh.
    fresh = WorkflowReadinessScanner(
        node_mapping_loader=lambda: {node["class_type"]: object() for node in graph.values()},
        model_filename_loader=lambda category: models.get(category, ()),
    )
    assert evaluate_workflow_readiness(WORKFLOW, scanner=fresh)["status"] == "ready"
