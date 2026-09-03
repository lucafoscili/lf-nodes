"""Offline input/wiring contracts; no Comfy execution or output files are created."""

import itertools
import json

import pytest

from modules.workflow_runner.workflows import image_to_svg as workflow_module
from modules.workflow_runner.workflows.image_to_svg import WORKFLOW


def _graph():
    return json.loads(WORKFLOW.workflow_path.read_text(encoding="utf-8"))


@pytest.fixture
def resolve_source(monkeypatch):
    calls = []

    def resolve(inputs, name):
        calls.append((inputs[name], name))
        return "LF_Nodes/Source/source.png [output]"

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    return calls


def test_every_public_control_and_link_targets_an_existing_node() -> None:
    graph = _graph()
    assert [(cell.id, cell.node_id) for cell in WORKFLOW.inputs] == [
        ("source_path", "16"),
        ("icon_name", "47"),
        ("number_of_colors", "40"),
        ("keep_transparency", "72"),
        ("strip_attributes", "80"),
        ("desaturate", "51"),
    ]
    for cell in [*WORKFLOW.inputs, *WORKFLOW.outputs]:
        assert cell.node_id in graph
    for node in graph.values():
        for value in node["inputs"].values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[1], int):
                assert value[0] in graph


def test_explicit_public_defaults_match_omitted_optional_controls(resolve_source) -> None:
    defaults = {
        cell.id: cell.props["lfValue"]
        for cell in WORKFLOW.inputs
        if "lfValue" in cell.props
    }
    explicit = _graph()
    omitted = _graph()
    WORKFLOW.configure_prompt(explicit, {"source_path": "uploaded", **defaults})
    WORKFLOW.configure_prompt(omitted, {"source_path": "uploaded"})

    assert explicit == omitted
    assert omitted["16"]["inputs"]["image"] == "LF_Nodes/Source/source.png [output]"
    assert omitted["47"]["inputs"]["string"] == "icon"
    assert omitted["40"]["inputs"]["integer"] == 2
    assert omitted["51"]["inputs"]["boolean"] is False
    assert omitted["72"]["inputs"]["boolean"] is True
    assert omitted["80"]["inputs"]["boolean"] is True
    assert resolve_source == [("uploaded", "source_path")] * 2


@pytest.mark.parametrize("reference", (
    "source.png [input]",
    "LF_Nodes/Catalogue/source.png [output]",
    "preview.png [temp]",
    "C:/external/source.png",
))
def test_core_loader_receives_the_canonical_reference_not_the_raw_upload(
    monkeypatch, reference,
) -> None:
    resolved = "lf-workflow-runner/staged-images/sha256-example.png [input]"
    calls = []

    def resolve(inputs, name):
        calls.append((inputs[name], name))
        return resolved

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    graph = _graph()
    WORKFLOW.configure_prompt(graph, {"source_path": reference})

    assert calls == [(reference, "source_path")]
    assert graph["16"]["inputs"]["image"] == resolved


@pytest.mark.parametrize(
    ("transparency", "strip", "desaturate"),
    itertools.product((False, True), repeat=3),
)
def test_controls_are_independent_and_preserve_the_mask_link(
    resolve_source, transparency, strip, desaturate,
) -> None:
    graph = _graph()
    WORKFLOW.configure_prompt(graph, {
        "source_path": "uploaded",
        "icon_name": "exports/compass",
        "number_of_colors": "8",
        "keep_transparency": transparency,
        "strip_attributes": strip,
        "desaturate": desaturate,
    })

    assert graph["47"]["inputs"]["string"] == "exports/compass"
    assert graph["40"]["inputs"]["integer"] == 8
    assert graph["51"]["inputs"]["boolean"] is desaturate
    assert graph["72"]["inputs"]["boolean"] is transparency
    assert graph["71"]["inputs"]["boolean"] == ["72", 0]
    assert graph["80"]["inputs"]["boolean"] is strip


def test_strip_switch_reaches_both_original_and_stripped_svg() -> None:
    graph = _graph()
    assert graph["80"]["class_type"] == "LF_SwitchString"
    assert graph["20"]["inputs"]["svg"] == ["80", 0]
    assert graph["80"]["inputs"]["on_false"] == ["42", 0]
    assert graph["80"]["inputs"]["on_true"] == ["44", 0]
    assert graph["42"]["inputs"]["text_2"] == ["30", 0]
    assert graph["43"]["inputs"]["input_text"] == ["42", 0]
    assert graph["43"]["inputs"]["target"] == 'height="100%"'
    assert graph["44"]["inputs"]["input_text"] == ["43", 0]
    assert graph["44"]["inputs"]["target"] == 'width="100%"'
    assert graph["43"]["inputs"]["replacement"] == graph["44"]["inputs"]["replacement"] == ""


def test_non_square_geometry_and_mask_polarity_are_preserved() -> None:
    graph = _graph()
    resize = graph["22"]["inputs"]
    assert resize["image"] == ["16", 0]
    assert resize["longest_edge"] is True
    assert resize["new_size"] == 512
    assert graph["52"]["inputs"]["image"] == ["22", 0]
    assert graph["30"]["inputs"]["image"] == ["52", 0]
    # Empty override uses the resized source's width/height, not a square viewBox.
    assert graph["30"]["inputs"]["viewbox"] == ""
    # Core MASK uses 1=transparent. SVG tracing uses 1=opaque, so only that branch inverts.
    assert graph["71"]["inputs"]["on_true"] == ["16", 1]
    assert graph["71"]["inputs"]["on_false"] == ["70", 0]
    assert graph["70"]["inputs"]["value"] == 0
    assert graph["77"]["inputs"]["mask"] == ["71", 0]
    assert graph["30"]["inputs"]["mask"] == ["77", 0]
    assert graph["56"]["class_type"] == "JoinImageWithAlpha"
    assert graph["56"]["inputs"] == {"image": ["30", 2], "alpha": ["71", 0]}
    assert graph["61"]["inputs"]["image"] == ["56", 0]


def test_saver_uses_existing_counter_without_changing_location_or_timestamp(resolve_source) -> None:
    graph = _graph()
    assert graph["20"]["inputs"]["add_counter"] is True
    graph["20"]["inputs"].update({
        "filename_prefix": "custom-icons/compass",
        "add_timestamp": True,
        "add_counter": False,
    })
    WORKFLOW.configure_prompt(graph, {"source_path": "uploaded"})
    assert graph["20"]["inputs"]["filename_prefix"] == "custom-icons/compass"
    assert graph["20"]["inputs"]["add_timestamp"] is True
    assert graph["20"]["inputs"]["add_counter"] is True
