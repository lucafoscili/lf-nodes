"""Offline contracts for the opt-in ACE-Step remix vertical slice."""

from __future__ import annotations

import json
import sys
import types

import pytest

sys.path.insert(0, str(__file__.split("custom_nodes")[0] + "custom_nodes/lf-nodes"))

# Keep this contract test independent of Comfy's GPU sampler import graph.
samplers = types.ModuleType("comfy.samplers")
samplers.KSampler = types.SimpleNamespace(SAMPLERS=[], SCHEDULERS=[])
sys.modules.setdefault("comfy.samplers", samplers)

# The registry only needs json_safe; importing the normal helper package pulls
# in Comfy's server and model stack.
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.nodes.io import ace_step_remix as remix
from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows.ace_step_remix import WORKFLOW
from modules.workflow_runner.workflows import _WORKFLOW_MODULES


class _Response:
    def __init__(self, payload=None, content=b"", headers=None):
        self._payload = payload
        self._content = content
        self.headers = headers or {}

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload

    def iter_content(self, chunk_size=0):
        yield self._content


class _HTTP:
    def __init__(self):
        self.posts = []
        self.queries = 0

    def post(self, url, **kwargs):
        self.posts.append((url, kwargs))
        if url.endswith("/release_task"):
            return _Response({"data": {"task_id": "job-1"}})
        self.queries += 1
        if self.queries == 1:
            return _Response({"data": [{"status": 0}]})
        return _Response({"data": [{"status": 1, "result": json.dumps([{"file": "/v1/audio?path=rendered.mp3"}])}]})

    def get(self, url, **kwargs):
        return _Response(content=b"fake-audio", headers={"Content-Length": "10"})


@pytest.fixture
def managed_roots(tmp_path, monkeypatch):
    roots = {name: tmp_path / name for name in ("input", "temp", "output")}
    for root in roots.values():
        root.mkdir()
    monkeypatch.setattr(remix.folder_paths, "get_input_directory", lambda: str(roots["input"]))
    monkeypatch.setattr(remix.folder_paths, "get_temp_directory", lambda: str(roots["temp"]))
    monkeypatch.setattr(remix.folder_paths, "get_output_directory", lambda: str(roots["output"]))
    source = roots["input"] / "reference.m4a"
    source.write_bytes(b"source")
    return roots, source


def _defaults(source):
    return dict(
        source_audio=str(source), mode="cover", style_prompt="warm synthwave",
        lyrics="", instrumental=True, audio_cover_strength=0.8,
        cover_noise_strength=0.15, repaint_start=0.0, repaint_end=-1.0,
        seed=42, inference_steps=8, guidance_scale=6.5, infer_method="ode",
        shift=1.0, output_format="mp3",
    )


def test_cover_submission_is_multipart_and_returns_audio_ui_and_receipt(managed_roots, monkeypatch):
    roots, source = managed_roots
    http = _HTTP()
    monkeypatch.setenv("LF_ACESTEP_ENABLED", "1")
    monkeypatch.setenv("LF_ACESTEP_API_TOKEN", "secret")
    monkeypatch.setenv("LF_ACESTEP_API_URL", "http://127.0.0.1:8001")
    monkeypatch.setattr(remix, "_HTTP", http)
    monkeypatch.setattr(remix, "_SLEEP", lambda _: None)

    result = remix.LF_ACEStepRemix().on_exec(**_defaults(source))

    release_url, request = http.posts[0]
    assert release_url.endswith("/release_task")
    assert request["headers"] == {"Authorization": "Bearer secret"}
    assert request["data"]["task_type"] == "cover"
    assert request["data"]["use_random_seed"] == "false"
    assert request["data"]["batch_size"] == "1"
    assert request["data"]["infer_method"] == "ode"
    assert request["data"]["shift"] == "1.0"
    assert "src_audio" not in request["data"]
    assert "duration" not in request["data"]
    assert request["files"]["src_audio"][0] == "reference.m4a"
    output_reference, receipt = result["result"]
    assert output_reference.endswith(" [output]")
    assert result["ui"]["audio"][0]["type"] == "output"
    assert receipt["schema"] == "lf.ace-step-remix.v1"
    assert receipt["source_reference"] == "reference.m4a [input]"
    assert (roots["output"] / "lf-workflow-runner" / "ace-step").is_dir()


def test_repaint_controls_are_sent_and_source_path_escape_is_rejected(managed_roots, monkeypatch, tmp_path):
    roots, source = managed_roots
    http = _HTTP()
    monkeypatch.setenv("LF_ACESTEP_ENABLED", "1")
    monkeypatch.setattr(remix, "_HTTP", http)
    monkeypatch.setattr(remix, "_SLEEP", lambda _: None)
    controls = _defaults(source)
    controls.update(mode="repaint", repaint_start=3.0, repaint_end=12.0, cover_noise_strength=0.4)
    remix.LF_ACEStepRemix().on_exec(**controls)
    assert http.posts[0][1]["data"]["task_type"] == "repaint"
    assert http.posts[0][1]["data"]["repainting_start"] == "3.0"
    assert http.posts[0][1]["data"]["repainting_end"] == "12.0"

    outside = tmp_path / "outside.wav"
    outside.write_bytes(b"no")
    controls["source_audio"] = str(outside)
    with pytest.raises(ValueError, match="inside ComfyUI"):
        remix.LF_ACEStepRemix().on_exec(**controls)


def test_disabled_by_default_and_workflow_is_packaged(monkeypatch):
    monkeypatch.delenv("LF_ACESTEP_ENABLED", raising=False)
    with pytest.raises(RuntimeError, match="disabled"):
        remix.LF_ACEStepRemix().on_exec(**_defaults("missing.wav"))
    assert "ace_step_remix" in _WORKFLOW_MODULES
    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.inputs[:2]] == [
        ("reference", "youtube_url", "textfield"),
        ("remix", "mode", "select"),
    ]
    assert WORKFLOW.inputs[1].props == {
        "lfDataset": {
            "nodes": [
                {"id": "cover", "value": "Cover", "workflowValue": "cover"},
                {"id": "repaint", "value": "Repaint", "workflowValue": "repaint"},
            ],
        },
        "lfTextfieldProps": {"lfLabel": "Mode"},
        "lfValue": "cover",
    }
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, {
        "youtube_url": "https://youtu.be/ETPjddfrk_w",
        "mode": "repaint",
        "repaint_start": 1,
        "repaint_end": 8,
    })
    assert prompt["reference"]["inputs"] == {
        "youtube_url": "https://www.youtube.com/watch?v=ETPjddfrk_w",
        "media_kind": "audio_m4a",
    }
    assert prompt["remix"]["inputs"]["mode"] == "repaint"
    assert prompt["remix"]["inputs"]["source_audio"] == ["reference", 0]
    assert prompt["remix"]["inputs"]["infer_method"] == "ode"
    assert prompt["remix"]["inputs"]["shift"] == 3.0

    assert [(cell.node_id, cell.id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("remix", "audio", "masonry"),
        ("output_reference", "output_reference", "code"),
        ("receipt", "receipt", "code"),
    ]
    assert prompt["output_reference"]["inputs"] == {
        "ui_widget": "",
        "string": ["remix", 0],
    }
    assert prompt["receipt"]["inputs"] == {
        "ui_widget": "",
        "json_input": ["remix", 1],
    }


@pytest.mark.parametrize(
    "youtube_url",
    [
        "",
        "https://youtu.be/ETPjddfrk_w?t=30",
        "https://www.youtube.com/shorts/ETPjddfrk_w",
        42,
    ],
)
def test_packaged_workflow_rejects_invalid_youtube_sources(youtube_url):
    with pytest.raises(InputValidationError) as exc:
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), {"youtube_url": youtube_url})

    assert exc.value.input_name == "youtube_url"


def test_timeout_is_configurable_and_bounded(monkeypatch):
    monkeypatch.delenv("LF_ACESTEP_TIMEOUT_SECONDS", raising=False)
    assert remix._poll_timeout_seconds() == 3600

    monkeypatch.setenv("LF_ACESTEP_TIMEOUT_SECONDS", "7200")
    assert remix._poll_timeout_seconds() == 7200

    for value in ("0", "86401", "not-a-number"):
        monkeypatch.setenv("LF_ACESTEP_TIMEOUT_SECONDS", value)
        with pytest.raises(ValueError, match="LF_ACESTEP_TIMEOUT_SECONDS"):
            remix._poll_timeout_seconds()


def test_random_seed_mode_is_explicit(managed_roots, monkeypatch):
    _, source = managed_roots
    http = _HTTP()
    monkeypatch.setenv("LF_ACESTEP_ENABLED", "1")
    monkeypatch.setattr(remix, "_HTTP", http)
    monkeypatch.setattr(remix, "_SLEEP", lambda _: None)
    controls = _defaults(source)
    controls["seed"] = -1

    remix.LF_ACEStepRemix().on_exec(**controls)

    assert http.posts[0][1]["data"]["use_random_seed"] == "true"
