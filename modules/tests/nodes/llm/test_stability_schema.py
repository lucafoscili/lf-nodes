from __future__ import annotations

import asyncio
import json
import sys
import types
from types import SimpleNamespace

import torch

from modules.tests.common_mocks import scoped_common_mocks


with scoped_common_mocks(torch_enabled=True):
    base64_module = types.ModuleType(
        "modules.utils.helpers.conversion.base64_to_tensor"
    )
    base64_module.base64_to_tensor = lambda value: value
    sys.modules[base64_module.__name__] = base64_module
    from modules.nodes.llm import stability_api as stability_module  # noqa: E402
    from modules.nodes.llm.stability_api import LF_StabilityAPI  # noqa: E402

from modules.utils.constants import Input  # noqa: E402
from modules.utils.helpers.logic.normalize_output_image import (  # noqa: E402
    normalize_output_image,
)


def test_stability_api_exposes_the_code_logger_widget() -> None:
    schema = LF_StabilityAPI.INPUT_TYPES()

    assert schema["optional"]["ui_widget"] == (
        Input.LF_CODE,
        {"default": ""},
    )
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert LF_StabilityAPI.RETURN_TYPES == (Input.IMAGE, Input.IMAGE)
    assert LF_StabilityAPI.RETURN_NAMES == ("images", "image_list")
    assert LF_StabilityAPI.OUTPUT_IS_LIST == (False, True)


class _FakeResponse:
    status = 200

    def __init__(self, data: dict) -> None:
        self.data = data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args) -> None:
        return None

    async def text(self) -> str:
        return json.dumps(self.data)

    async def json(self) -> dict:
        return self.data


class _FakeSession:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.request: dict | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args) -> None:
        return None

    def post(self, url: str, **kwargs) -> _FakeResponse:
        self.request = {"url": url, **kwargs}
        return _FakeResponse(self.data)


def test_stability_success_returns_primary_batch_and_lossless_public_list(
    monkeypatch,
) -> None:
    first = torch.zeros((1, 2, 3, 3), dtype=torch.float32)
    second = torch.ones((1, 2, 3, 3), dtype=torch.float32)
    decoded = {"first-image": first, "second-image": second}
    session = _FakeSession(
        {
            "artifacts": [
                {"base64": "first-image"},
                {"base64": "second-image"},
            ]
        }
    )
    logs: list[str] = []
    monkeypatch.setenv("STABILITY_PROXY_URL", "https://stability.invalid/proxy")
    monkeypatch.setattr(
        stability_module,
        "create_ui_logger",
        lambda *_args: SimpleNamespace(log=logs.append),
    )
    monkeypatch.setattr(stability_module, "read_secret", lambda _name: None)
    monkeypatch.setattr(
        stability_module,
        "base64_to_tensor",
        lambda value: decoded[value],
    )
    monkeypatch.setattr(
        stability_module,
        "normalize_output_image",
        normalize_output_image,
    )

    result = asyncio.run(
        LF_StabilityAPI().on_exec(
            prompt="two ordered images",
            samples=2,
            _test_session=session,
            node_id="stability-node",
        )
    )

    assert isinstance(result, tuple)
    assert len(result) == len(LF_StabilityAPI.RETURN_TYPES) == 2
    batch, image_list = result
    assert batch.shape == (2, 2, 3, 3)
    assert torch.equal(batch[0:1], first)
    assert torch.equal(batch[1:2], second)
    assert isinstance(image_list, list)
    assert [tuple(image.shape) for image in image_list] == [
        (1, 2, 3, 3),
        (1, 2, 3, 3),
    ]
    assert torch.equal(image_list[0], first)
    assert torch.equal(image_list[1], second)
    assert LF_StabilityAPI.OUTPUT_IS_LIST == (False, True)
    assert session.request is not None
    assert session.request["url"] == "https://stability.invalid/proxy"
    assert session.request["json"]["samples"] == 2
    assert logs[-1] == "Successfully generated 2 image(s)."
