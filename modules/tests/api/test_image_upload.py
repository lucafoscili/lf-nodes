from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest


class _Routes:
    def get(self, *_args, **_kwargs):
        return lambda function: function

    def post(self, *_args, **_kwargs):
        return lambda function: function


class _Part:
    def __init__(
        self,
        name: str,
        *,
        filename: str | None = None,
        data: bytes = b"",
        text: str = "",
    ):
        self.name = name
        self.filename = filename
        self._data = data
        self._text = text
        self._read = False

    async def text(self) -> str:
        return self._text

    async def read_chunk(self) -> bytes:
        if self._read:
            return b""
        self._read = True
        return self._data


class _Reader:
    def __init__(self, parts: list[_Part]):
        self._parts = iter(parts)

    async def next(self):
        return next(self._parts, None)


class _Request:
    def __init__(self, parts: list[_Part]):
        self._reader = _Reader(parts)

    async def multipart(self):
        return self._reader


@pytest.fixture
def image_api(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    roots = {
        storage_type: tmp_path / storage_type
        for storage_type in ("input", "output", "temp")
    }
    for root in roots.values():
        root.mkdir()

    folder_paths = types.ModuleType("folder_paths")
    folder_paths.get_input_directory = lambda: str(roots["input"])
    folder_paths.get_output_directory = lambda: str(roots["output"])
    folder_paths.get_temp_directory = lambda: str(roots["temp"])
    folder_paths.get_directory_by_type = lambda storage_type: str(roots[storage_type])

    server = types.ModuleType("server")
    server.PromptServer = SimpleNamespace(
        instance=SimpleNamespace(routes=_Routes()),
    )

    constants = types.ModuleType("modules.utils.constants")
    constants.API_ROUTE_PREFIX = "/api/lf-nodes"
    constants.IMAGE_FILE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
    processors = types.ModuleType("modules.utils.filters.processors")
    processors.UnknownFilterError = ValueError
    processors.process_filter = lambda *args, **kwargs: None
    api_helpers = types.ModuleType("modules.utils.helpers.api")
    api_helpers.get_resource_url = lambda *args, **kwargs: ""
    api_helpers.resolve_url = lambda *args, **kwargs: ("", "", "")
    comfy_helpers = types.ModuleType("modules.utils.helpers.comfy")
    comfy_helpers.ensure_external_preview = lambda *args, **kwargs: ("", "")
    comfy_helpers.get_comfy_dir = lambda *args, **kwargs: ""
    comfy_helpers.resolve_filepath = lambda *args, **kwargs: ("", "", "")
    comfy_helpers.resolve_input_directory_path = lambda *args, **kwargs: (None, None, False)
    conversion_helpers = types.ModuleType("modules.utils.helpers.conversion")
    conversion_helpers.pil_to_tensor = lambda *args, **kwargs: None
    conversion_helpers.tensor_to_pil = lambda *args, **kwargs: None
    logic_helpers = types.ModuleType("modules.utils.helpers.logic")
    logic_helpers.sanitize_filename = lambda value: value or None
    ui_helpers = types.ModuleType("modules.utils.helpers.ui")
    ui_helpers.create_masonry_node = lambda *args, **kwargs: {}
    torch = types.ModuleType("torch")
    torch.Tensor = object

    previous_image_api = sys.modules.pop("modules.api.image", None)
    for name, module in {
        "folder_paths": folder_paths,
        "server": server,
        "torch": torch,
        "modules.utils.constants": constants,
        "modules.utils.filters.processors": processors,
        "modules.utils.helpers.api": api_helpers,
        "modules.utils.helpers.comfy": comfy_helpers,
        "modules.utils.helpers.conversion": conversion_helpers,
        "modules.utils.helpers.logic": logic_helpers,
        "modules.utils.helpers.ui": ui_helpers,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    try:
        module = importlib.import_module("modules.api.image")
        yield module, roots
    finally:
        sys.modules.pop("modules.api.image", None)
        if previous_image_api is not None:
            sys.modules["modules.api.image"] = previous_image_api


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_explicit_input_upload_is_durable_portable_and_collision_safe(image_api) -> None:
    module, roots = image_api

    first = await module.lf_nodes_upload(
        _Request(
            [
                _Part("directory", text="input"),
                _Part("file", filename="portrait.png", data=b"first"),
            ]
        )
    )
    second = await module.lf_nodes_upload(
        _Request(
            [
                _Part("directory", text="input"),
                _Part("file", filename="portrait.png", data=b"second"),
            ]
        )
    )

    assert first.status == 200
    assert second.status == 200
    first_payload = json.loads(first.text)
    second_payload = json.loads(second.text)
    assert first_payload["payload"]["paths"] == ["portrait.png [input]"]
    assert second_payload["payload"]["paths"] == ["portrait_1.png [input]"]
    assert str(roots["input"]) not in first.text
    assert str(roots["input"]) not in second.text
    assert (roots["input"] / "portrait.png").read_bytes() == b"first"
    assert (roots["input"] / "portrait_1.png").read_bytes() == b"second"
    assert list(roots["temp"].iterdir()) == []
