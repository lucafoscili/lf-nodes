"""Offline contract tests for the URL-only YouTube reference intake runner."""

from __future__ import annotations

import json
import sys
import types

import pytest

# Registry needs only ``json_safe`` for this declarative graph contract.  Do
# not import ComfyUI, yt-dlp, or any downloader implementation here.
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows.youtube_reference_intake import WORKFLOW


def test_declaration_exposes_only_url_and_media_profile() -> None:
    assert WORKFLOW.id == "youtube_reference_intake"
    assert WORKFLOW.category == "Media Intake"
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.inputs] == [
        ("reference", "youtube_url", "textfield"),
        ("reference", "media_profile", "select"),
    ]
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("input_reference", "input_reference", "code"),
        ("video_id", "video_id", "code"),
        ("manifest", "receipt", "code"),
    ]
    assert WORKFLOW.inputs[1].props == {
        "lfDataset": {
            "nodes": [
                {"id": "audio_m4a", "value": "Audio (M4A)", "workflowValue": "audio_m4a"},
                {"id": "audio_flac", "value": "Audio (FLAC)", "workflowValue": "audio_flac"},
                {"id": "video_mp4", "value": "Video (MP4)", "workflowValue": "video_mp4"},
            ],
        },
        "lfTextfieldProps": {"lfLabel": "Media profile"},
        "lfValue": "audio_m4a",
    }
    assert WORKFLOW.outputs[2].props["lfLanguage"] == "json"


def test_generic_workflow_is_part_of_the_packaged_inventory() -> None:
    assert "youtube_reference_intake" in _WORKFLOW_MODULES


def test_configure_maps_valid_url_and_profile_to_the_downloader_node() -> None:
    prompt = WORKFLOW.load_prompt()

    WORKFLOW.configure_prompt(
        prompt,
        {
            "youtube_url": "  https://youtu.be/ETPjddfrk_w?si=reference  ",
            "media_profile": "video_mp4",
        },
    )

    assert prompt["reference"]["inputs"] == {
        "youtube_url": "https://www.youtube.com/watch?v=ETPjddfrk_w",
        "media_kind": "video_mp4",
    }
    assert prompt["input_reference"]["inputs"]["string"] == ["reference", 0]
    assert prompt["video_id"]["inputs"]["string"] == ["reference", 1]
    assert prompt["manifest"]["inputs"]["json_input"] == ["reference", 2]


@pytest.mark.parametrize(
    "youtube_url",
    [
        "http://youtu.be/ETPjddfrk_w",
        "https://youtu.be/ETPjddfrk_w?t=30",
        "https://m.youtube.com/watch?v=ETPjddfrk_w&list=playlist",
        "https://www.youtube.com/watch?v=ETPjddfrk_w&si=",
        "https://www.youtube.com/shorts/ETPjddfrk_w",
    ],
)
def test_configure_rejects_urls_the_downloader_node_would_reject(youtube_url) -> None:
    with pytest.raises(InputValidationError) as exc:
        WORKFLOW.configure_prompt(
            WORKFLOW.load_prompt(),
            {"youtube_url": youtube_url, "media_profile": "audio_m4a"},
        )

    assert exc.value.input_name == "youtube_url"


@pytest.mark.parametrize(
    ("inputs", "input_name"),
    [
        ({}, "youtube_url"),
        ({"youtube_url": ""}, "youtube_url"),
        ({"youtube_url": "   ", "media_profile": "audio_m4a"}, "youtube_url"),
        ({"youtube_url": 42, "media_profile": "audio_m4a"}, "youtube_url"),
        ({"youtube_url": "https://youtu.be/ETPjddfrk_w"}, "media_profile"),
        ({"youtube_url": "https://youtu.be/ETPjddfrk_w", "media_profile": ""}, "media_profile"),
        ({"youtube_url": "https://youtu.be/ETPjddfrk_w", "media_profile": "mp3"}, "media_profile"),
        ({"youtube_url": "https://youtu.be/ETPjddfrk_w", "media_profile": True}, "media_profile"),
    ],
)
def test_configure_rejects_missing_or_invalid_runner_inputs(inputs, input_name) -> None:
    with pytest.raises(InputValidationError) as exc:
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), inputs)

    assert exc.value.input_name == input_name


def test_graph_is_only_the_reference_node_and_standard_json_display() -> None:
    graph = json.loads(WORKFLOW.workflow_path.read_text(encoding="utf-8"))

    assert graph == {
        "reference": {
            "inputs": {"youtube_url": "", "media_kind": "audio_m4a"},
            "class_type": "LF_YouTubeReference",
            "_meta": {"title": "YouTube reference (cached input)"},
        },
        "input_reference": {
            "inputs": {
                "ui_widget": "",
                "string": ["reference", 0],
            },
            "class_type": "LF_DisplayString",
            "_meta": {"title": "Portable Comfy input reference"},
        },
        "video_id": {
            "inputs": {
                "ui_widget": "",
                "string": ["reference", 1],
            },
            "class_type": "LF_DisplayString",
            "_meta": {"title": "Canonical YouTube video ID"},
        },
        "manifest": {
            "inputs": {
                "ui_widget": "",
                "json_input": ["reference", 2],
            },
            "class_type": "LF_DisplayJSON",
            "_meta": {"title": "Portable reference receipt"},
        },
    }
