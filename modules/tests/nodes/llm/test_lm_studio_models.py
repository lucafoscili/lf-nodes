from __future__ import annotations

import importlib
import math

import pytest
import requests

from modules.utils.constants import Input


nodes = importlib.import_module("modules.nodes.llm.lm_studio_models")
api = importlib.import_module("modules.utils.helpers.api.lm_studio_lifecycle")
URL = "http://localhost.test:1234/api/v1/chat"
MODELS = "http://localhost.test:1234/api/v1/models"


class Response:
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def json(self):
        if isinstance(self.data, Exception):
            raise self.data
        return self.data


def inventory(*instance_ids):
    return {"models": [
        {"key": "my/model", "type": "llm", "loaded_instances": [
            {"id": value, "config": {}} for value in instance_ids
        ]},
        {"key": "other/model", "type": "llm", "loaded_instances": [
            {"id": "other-instance", "config": {}}
        ]},
    ]}


@pytest.fixture
def transport(monkeypatch):
    calls = []
    replies = []
    monkeypatch.setattr(api, "read_secret", lambda _name: None)

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        reply = replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(api.requests, "get", lambda url, **kw: request("GET", url, **kw))
    monkeypatch.setattr(api.requests, "post", lambda url, **kw: request("POST", url, **kw))
    return calls, replies


def test_public_schema_native_widgets_scalar_outputs_and_cache():
    assert nodes.NODE_CLASS_MAPPINGS == {
        "LF_LMSLoadModel": nodes.LF_LMSLoadModel,
        "LF_LMSUnloadModel": nodes.LF_LMSUnloadModel,
    }
    assert nodes.NODE_DISPLAY_NAME_MAPPINGS == {
        "LF_LMSLoadModel": "LMS Load Model",
        "LF_LMSUnloadModel": "LMS Unload Model",
    }
    for node, required, output in (
        (nodes.LF_LMSLoadModel, ["model", "url"], "instance_id"),
        (nodes.LF_LMSUnloadModel, ["prompt", "instance_id", "url"], "prompt"),
    ):
        schema = node.INPUT_TYPES()
        assert list(schema["required"]) == required
        assert list(schema["optional"]) == ["timeout"]
        assert "hidden" not in schema
        assert schema["required"]["url"][1]["default"] == "http://127.0.0.1:1234/api/v1/chat"
        assert schema["optional"]["timeout"] == (Input.INTEGER, {"default": 120, "min": 1})
        assert node.INPUT_IS_LIST is True
        assert node.RETURN_TYPES == (Input.STRING,)
        assert node.RETURN_NAMES == (output,)
        assert node.OUTPUT_IS_LIST == (False,)
        assert len(node.OUTPUT_TOOLTIPS) == 1
        assert not getattr(node, "OUTPUT_NODE", False)
        assert math.isnan(node.IS_CHANGED())
        assert node.IS_CHANGED() != node.IS_CHANGED()
    assert nodes.LF_LMSUnloadModel.INPUT_TYPES()["required"]["prompt"][1]["forceInput"]


def test_load_requests_exact_downloaded_key_and_returns_instance(transport):
    calls, replies = transport
    replies.extend([
        Response(inventory()),
        Response({"type": "llm", "status": "loaded", "instance_id": "my-instance-2"}),
    ])
    assert nodes.LF_LMSLoadModel().on_exec(["my/model"], [URL], [90]) == ("my-instance-2",)
    assert calls == [
        ("GET", MODELS, {"timeout": 90, "headers": {"Content-Type": "application/json"}, "allow_redirects": False}),
        ("POST", MODELS + "/load", {"timeout": 90, "headers": {"Content-Type": "application/json"}, "allow_redirects": False, "json": {"model": "my/model"}}),
    ]


def test_load_reuses_only_exact_models_sole_instance(transport):
    calls, replies = transport
    replies.append(Response(inventory("my-instance")))
    assert nodes.LF_LMSLoadModel().on_exec("my/model", URL) == ("my-instance",)
    assert len(calls) == 1


@pytest.mark.parametrize("model,data,match", [
    ("missing", inventory(), "downloaded"),
    ("my/model", inventory("a", "b"), "multiple loaded instances"),
    ("my/model", {"models": [{"key": "my/model", "type": "embedding", "loaded_instances": []}]}, "downloaded"),
])
def test_load_refuses_missing_ambiguous_or_embedding_models(transport, model, data, match):
    calls, replies = transport
    replies.append(Response(data))
    with pytest.raises(ValueError, match=match):
        api.load_lm_studio_model(model, URL)
    assert len(calls) == 1


def test_unload_passes_prompt_only_after_exact_instance_confirmation(transport):
    calls, replies = transport
    replies.extend([Response(inventory("my-instance")), Response({"instance_id": "my-instance"})])
    prompt = "  Exact generated prompt.\n"
    assert nodes.LF_LMSUnloadModel().on_exec([prompt], ["my-instance"], [URL]) == (prompt,)
    assert len(calls) == 2
    assert calls[1][1] == MODELS + "/unload"
    assert calls[1][2]["json"] == {"instance_id": "my-instance"}


def test_unload_already_absent_instance_is_idempotent(transport):
    calls, replies = transport
    replies.append(Response(inventory()))
    assert nodes.LF_LMSUnloadModel().on_exec("prompt", "my-instance", URL) == ("prompt",)
    assert len(calls) == 1


@pytest.mark.parametrize("response,match", [
    (Response({"error": {"message": "busy"}}, 409), "HTTP status 409.*busy"),
    (Response({"instance_id": "other-instance"}), "did not confirm"),
    (Response(ValueError("bad JSON")), "not valid JSON"),
    (Response([]), "JSON object"),
    (requests.Timeout(), "may have completed"),
])
def test_unload_errors_block_prompt_output(transport, response, match):
    calls, replies = transport
    replies.extend([Response(inventory("my-instance")), response])
    with pytest.raises(ValueError, match=match):
        nodes.LF_LMSUnloadModel().on_exec("prompt", "my-instance", URL)
    assert len(calls) == 2


@pytest.mark.parametrize("data", [{}, {"instance_id": "x"}, {"type": "embedding", "status": "loaded", "instance_id": "x"}])
def test_load_requires_documented_success_confirmation(transport, data):
    _, replies = transport
    replies.extend([Response(inventory()), Response(data)])
    with pytest.raises(ValueError, match="confirm a loaded LLM"):
        api.load_lm_studio_model("my/model", URL)


@pytest.mark.parametrize("data", [
    {}, {"models": {}}, {"models": [None]},
    {"models": [{"key": "a", "type": "llm", "loaded_instances": [{}]}]},
])
def test_bad_inventory_never_permits_lifecycle_mutation(transport, data):
    calls, replies = transport
    replies.append(Response(data))
    with pytest.raises(ValueError, match="inventory"):
        api.unload_lm_studio_model("my-instance", URL)
    assert len(calls) == 1


@pytest.mark.parametrize("name,value", [("prompt", ["one", "two"]), ("instance_id", []), ("url", [URL, URL]), ("timeout", [1, 2]), ("prompt", 42)])
def test_unload_validates_all_scalar_inputs_before_http(transport, name, value):
    calls, _ = transport
    kwargs = {"prompt": ["one"], "instance_id": ["my-instance"], "url": [URL], "timeout": [120]}
    kwargs[name] = value
    with pytest.raises(ValueError):
        nodes.LF_LMSUnloadModel().on_exec(**kwargs)
    assert calls == []


@pytest.mark.parametrize("timeout", [0, -1, True, 1.5, "120"])
def test_invalid_timeout_fails_before_http(transport, timeout):
    calls, _ = transport
    with pytest.raises(ValueError, match="positive integer"):
        api.load_lm_studio_model("my/model", URL, timeout)
    assert calls == []


def test_auth_is_transport_only_and_errors_redact_token(transport, monkeypatch):
    calls, replies = transport
    monkeypatch.setattr(api, "read_secret", lambda name: "private-token" if name == "LM_API_TOKEN" else None)
    replies.append(Response({"error": "private-token denied"}, 401))
    with pytest.raises(ValueError, match="LM_API_TOKEN") as error:
        api.load_lm_studio_model("my/model", URL)
    assert "private-token" not in str(error.value)
    assert "[redacted]" in str(error.value)
    assert calls[0][2]["headers"]["Authorization"] == "Bearer private-token"
    assert calls[0][2]["allow_redirects"] is False


def test_repeated_queued_runs_recheck_residency_and_reload_after_unload(transport):
    calls, replies = transport
    for _ in range(2):
        replies.extend([
            Response(inventory()),
            Response({"type": "llm", "status": "loaded", "instance_id": "mine"}),
            Response(inventory("mine")),
            Response({"instance_id": "mine"}),
        ])
    loader = nodes.LF_LMSLoadModel()
    unloader = nodes.LF_LMSUnloadModel()
    for _ in range(2):
        instance_id, = loader.on_exec("my/model", URL)
        assert unloader.on_exec("done", instance_id, URL) == ("done",)
    assert [url for method, url, _ in calls if method == "POST"] == [
        MODELS + "/load", MODELS + "/unload", MODELS + "/load", MODELS + "/unload",
    ]
