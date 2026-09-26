"""Raw prompt rendering keeps prose and ordered independent references intact."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import types

import pytest

constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.constants", constants_module)
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError, default_input_values
from modules.workflow_runner.workflows import minimax_h3_prompt_video as renderer


WORKFLOW = renderer.WORKFLOW
PROSE = "  A character walks away.\nAn unfinished <Picture tag is still passed verbatim.\n"


def _inputs(mode="auto", count=0):
    return {
        "prompt": PROSE, "mode": mode,
        "duration": renderer.DEFAULT_DURATION, "seed": "73", "aspect_ratio": "9:16",
        **{f"picture_{n}": [Path(f"C:/uploads/reference-{n}.png")] for n in range(1, count + 1)},
    }


def _assert_links_resolve(graph):
    for node in graph.values():
        for value in node["inputs"].values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[1], int):
                assert value[0] in graph


def test_public_contract_and_portable_defaults():
    assert WORKFLOW.id == "minimax_h3_prompt_video"
    cells = {cell.id: cell for cell in WORKFLOW.inputs}
    assert set(cells) == {"prompt", "mode", "duration", "aspect_ratio", "seed", *renderer._PICTURE_IDS}
    assert [cell.id for cell in WORKFLOW.outputs] == ["video", "prompt"]
    assert all(not cells[field].required for field in renderer._PICTURE_IDS)
    assert cells["duration"].props["lfValue"] == str(124 / 24)
    assert [option["workflowValue"] for option in cells["duration"].props["lfDataset"]["nodes"]] == [
        str(frames / 24) for frames in (124, 192, 243, 362)
    ]
    graph = WORKFLOW.load_prompt()
    WORKFLOW.configure_download(graph, default_input_values(WORKFLOW))
    assert graph["h3"]["class_type"] == "MiniMaxH3ImageToVideo"
    assert graph["h3"]["inputs"]["length"] == 124
    assert graph["display_prompt"]["class_type"] == "LF_DisplayString"
    _assert_links_resolve(graph)


@pytest.mark.parametrize("mode,count", [
    ("auto", 0), ("auto", 1), ("auto", 9), ("t2va", 0),
    ("i2va", 1), ("fl2va", 2), ("l2va", 1), ("ref2va", 1), ("ref2va", 9),
])
@pytest.mark.parametrize("download", [False, True])
def test_modes_preserve_prose_order_and_quality_recipe(monkeypatch, mode, count, download):
    inputs = _inputs(mode, count)
    resolved = []
    def resolve(values, field):
        assert not download
        assert values[field] == inputs[field]
        resolved.append(field)
        return f"staged/{field}.png"
    monkeypatch.setattr(renderer, "resolve_load_image_reference", resolve)
    graph = WORKFLOW.load_prompt()
    configure = WORKFLOW.configure_download if download else WORKFLOW.configure_prompt
    configure(graph, inputs)
    actual_mode = ("ref2va" if count else "t2va") if mode == "auto" else mode
    h3_inputs = graph["h3"]["inputs"]
    assert h3_inputs["prompt"] == PROSE
    assert graph["display_prompt"]["inputs"]["string"] == PROSE
    assert (h3_inputs["width"], h3_inputs["height"], h3_inputs["length"]) == (768, 1344, 124)
    assert graph["noise"]["inputs"]["noise_seed"] == 73
    assert graph["scheduler"]["inputs"]["steps"] == 20
    assert graph["sampler_select"]["inputs"]["sampler_name"] == "res_multistep"
    assert graph["attention_backend"]["inputs"]["attention"] == "comfy kitchen attention"
    assert all(graph[node]["inputs"]["device"] == "default" for node in (
        "model_device", "clip_device", "video_vae_device", "audio_vae_device",
    ))
    assert graph["create_video"]["inputs"]["fps"] == 24.0
    assert graph["save"]["inputs"]["filename_prefix"].endswith(f"kitchen_quality/seed-73-refs{count}-f124")
    expected_images = [f"picture_{n}.png" if download else f"staged/picture_{n}.png" for n in range(1, count + 1)]
    if actual_mode == "ref2va":
        assert graph["h3"]["class_type"] == "MiniMaxH3ReferenceToVideo"
        assert "ref2va" in graph["unet"]["inputs"]["unet_name"]
        assert h3_inputs["ref_image_size"] == "max"
        assert not any(node.startswith("prompt_") for node in graph)
        assert [h3_inputs[f"ref_images.ref_image_{n}"] for n in range(count)] == [
            [f"source_{n}", 0] for n in range(1, count + 1)
        ]
        assert [graph[f"source_{n}"]["inputs"]["image"] for n in range(1, count + 1)] == expected_images
        assert f"source_{count + 1}" not in graph
        assert f"ref_images.ref_image_{count}" not in h3_inputs
    else:
        assert graph["h3"]["class_type"] == "MiniMaxH3ImageToVideo"
        assert "fl2va" in graph["unet"]["inputs"]["unet_name"]
        for source, socket, exists, index in (
            ("source_first", "first_frame", actual_mode in {"i2va", "fl2va"}, 0),
            ("source_last", "last_frame", actual_mode in {"l2va", "fl2va"}, -1),
        ):
            assert (source in graph) == exists
            assert (socket in h3_inputs) == exists
            if exists:
                assert h3_inputs[socket] == [source, 0]
                assert graph[source]["inputs"]["image"] == expected_images[index]
    assert resolved == ([] if download else [f"picture_{n}" for n in range(1, count + 1)])
    _assert_links_resolve(graph)


@pytest.mark.parametrize("frames", [124, 192, 243, 362])
@pytest.mark.parametrize("numeric", [False, True])
def test_seconds_select_exact_allowed_frames(frames, numeric):
    seconds = frames / 24
    graph = WORKFLOW.load_prompt()
    WORKFLOW.configure_download(graph, {**_inputs(), "duration": seconds if numeric else str(seconds)})
    assert graph["h3"]["inputs"]["length"] == frames


@pytest.mark.parametrize("updates", [
    {"prompt": " "}, {"prompt": 123}, {"mode": "invalid"},
    {"duration": "5.17"}, {"duration": "124"}, {"duration": "nan"},
    {"duration": True}, {"duration": 0}, {"duration": []},
    {"seed": -1}, {"aspect_ratio": "invalid"}, {"execution_profile": "turbo_preview"},
    {"mode": "ref2va"}, {"mode": "i2va"}, {"mode": "fl2va", "picture_1": "one.png"},
    {"mode": "t2va", "picture_1": "one.png"}, {"picture_2": "gap.png"},
])
@pytest.mark.parametrize("download", [False, True])
def test_invalid_inputs_fail_before_uploads_or_graph_mutation(monkeypatch, updates, download):
    monkeypatch.setattr(renderer, "resolve_load_image_reference", lambda *args: pytest.fail("No uploads on invalid input"))
    graph = WORKFLOW.load_prompt()
    original = deepcopy(graph)
    with pytest.raises((InputValidationError, ValueError)):
        (WORKFLOW.configure_download if download else WORKFLOW.configure_prompt)(graph, {**_inputs(), **updates})
    assert graph == original


def test_reconfiguration_switches_graph_families_without_stale_nodes():
    graph = WORKFLOW.load_prompt()
    for mode, count in (("ref2va", 9), ("l2va", 1), ("t2va", 0), ("ref2va", 2)):
        WORKFLOW.configure_download(graph, _inputs(mode, count))
        _assert_links_resolve(graph)
        assert ("source_1" in graph) == (mode == "ref2va")
        assert ("source_last" in graph) == (mode == "l2va")
