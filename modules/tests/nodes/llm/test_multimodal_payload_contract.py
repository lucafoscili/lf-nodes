from __future__ import annotations

import importlib
import json

import pytest
import torch


multimodal_module = importlib.import_module(
    "modules.utils.helpers.api.build_multimodal_content"
)
classifier_module = importlib.import_module("modules.nodes.llm.image_classifier")
impersonator_module = importlib.import_module(
    "modules.nodes.llm.character_impersonator"
)


class _Response:
    status_code = 200

    def json(self) -> dict:
        return {"choices": [{"message": {"content": "ok"}}]}


def _capture_request(monkeypatch: pytest.MonkeyPatch, node_module) -> list[dict]:
    calls: list[dict] = []

    def post(url, *, headers, data):
        calls.append({"url": url, "headers": headers, "data": json.loads(data)})
        return _Response()

    monkeypatch.setattr(node_module.requests, "post", post)
    monkeypatch.setattr(node_module, "safe_send_sync", lambda *_args, **_kwargs: None)
    return calls


def _assert_standard_first_image_payload(
    request: dict,
    *,
    expected_prompt: str,
) -> None:
    content = request["messages"][1]["content"]
    assert content == [
        {
            "type": "image_url",
            "image_url": {"url": "data:image/png;base64,first-frame"},
        },
        {"type": "text", "text": expected_prompt},
    ]
    assert "charset" not in content[0]["image_url"]["url"]


def test_multimodal_helper_uses_standard_png_data_url_and_first_list_image(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = torch.zeros((1, 2, 3, 3), dtype=torch.float32)
    second = torch.ones((1, 2, 3, 3), dtype=torch.float32)
    encoded: list[torch.Tensor] = []

    def encode(tensor: torch.Tensor) -> str:
        encoded.append(tensor)
        return "first-frame"

    monkeypatch.setattr(multimodal_module, "tensor_to_base64", encode)

    content = multimodal_module.build_openai_multimodal_content(
        [first, second],
        "Describe it.",
    )

    assert encoded == [first]
    assert content == [
        {
            "type": "image_url",
            "image_url": {"url": "data:image/png;base64,first-frame"},
        },
        {"type": "text", "text": "Describe it."},
    ]


def test_image_classifier_payload_keeps_first_image_from_nested_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batch = torch.stack(
        (
            torch.zeros((2, 3, 3), dtype=torch.float32),
            torch.ones((2, 3, 3), dtype=torch.float32),
        )
    )
    encoded: list[torch.Tensor] = []

    def encode(tensor: torch.Tensor) -> str:
        encoded.append(tensor)
        return "first-frame"

    monkeypatch.setattr(multimodal_module, "tensor_to_base64", encode)
    monkeypatch.setattr(classifier_module, "resolve_api_url", lambda url: url)
    calls = _capture_request(monkeypatch, classifier_module)

    result = classifier_module.LF_ImageClassifier().on_exec(
        image=[batch],
        temperature=[0.2],
        max_tokens=[64],
        prompt=["Classify this."],
        seed=[7],
        url=["http://localhost.test/v1/chat/completions"],
        character_bio=[""],
        node_id=["classifier-node"],
    )

    assert len(encoded) == 1
    assert tuple(encoded[0].shape) == (1, 2, 3, 3)
    assert torch.count_nonzero(encoded[0]) == 0
    assert len(calls) == 1
    _assert_standard_first_image_payload(
        calls[0]["data"],
        expected_prompt="Classify this.",
    )
    assert result[0] == calls[0]["data"]
    assert result[2] == "ok"


def test_character_impersonator_payload_keeps_first_image_from_nested_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    batch = torch.stack(
        (
            torch.zeros((2, 3, 3), dtype=torch.float32),
            torch.ones((2, 3, 3), dtype=torch.float32),
        )
    )
    encoded: list[torch.Tensor] = []

    def encode(tensor: torch.Tensor) -> str:
        encoded.append(tensor)
        return "first-frame"

    monkeypatch.setattr(multimodal_module, "tensor_to_base64", encode)
    calls = _capture_request(monkeypatch, impersonator_module)

    result = impersonator_module.LF_CharacterImpersonator().on_exec(
        image=[batch],
        temperature=[0.2],
        max_tokens=[64],
        prompt=["Answer in character."],
        seed=[7],
        character_bio=["A fictional character."],
        url=["http://localhost.test/v1/chat/completions"],
        node_id=["impersonator-node"],
    )

    assert len(encoded) == 1
    assert tuple(encoded[0].shape) == (1, 2, 3, 3)
    assert torch.count_nonzero(encoded[0]) == 0
    assert len(calls) == 1
    _assert_standard_first_image_payload(
        calls[0]["data"],
        expected_prompt="Answer in character.",
    )
    assert result[0] == calls[0]["data"]
    assert result[2] == "ok"
