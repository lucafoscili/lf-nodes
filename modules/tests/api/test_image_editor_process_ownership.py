from __future__ import annotations

import asyncio
import importlib
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
from PIL import Image


class _Routes:
    def post(self, *_args, **_kwargs):
        return lambda function: function


class _Request:
    def __init__(self, form: dict[str, str]) -> None:
        self._form = form

    async def post(self) -> dict[str, str]:
        return self._form


@pytest.fixture
def image_api(monkeypatch: pytest.MonkeyPatch):
    server = types.ModuleType("server")
    server.PromptServer = SimpleNamespace(instance=SimpleNamespace(routes=_Routes()))
    monkeypatch.setitem(sys.modules, "server", server)

    previous = sys.modules.pop("modules.api.image", None)
    try:
        yield importlib.import_module("modules.api.image")
    finally:
        sys.modules.pop("modules.api.image", None)
        if previous is not None:
            sys.modules["modules.api.image"] = previous


def _process_form(
    context_id: str,
    *,
    caller_client_id: str | None,
) -> dict[str, str]:
    form = {
        "url": "/view?filename=source.png&type=temp",
        "type": "brightness",
        "context_id": context_id,
        "settings": json.dumps(
            {
                "context_id": context_id,
                "filename": "processed.png",
                "resource_type": "temp",
            }
        ),
    }
    if caller_client_id is not None:
        form["caller_client_id"] = caller_client_id
    return form


def _configure_success_path(
    image_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    owner_client_id: str | None,
) -> tuple[str, list[tuple[str, tuple[int, ...]]]]:
    context_id = str(tmp_path / "463_context_edit_dataset.json")
    source = tmp_path / "source.png"
    Image.new("RGBA", (3, 2), (10, 20, 30, 64)).save(source)
    calls: list[tuple[str, tuple[int, ...]]] = []

    monkeypatch.setattr(
        image_api,
        "get_editing_context",
        lambda candidate: (
            {"owner_client_id": owner_client_id}
            if candidate == context_id
            else None
        ),
    )
    monkeypatch.setattr(image_api, "get_comfy_dir", lambda _kind: str(tmp_path))
    monkeypatch.setattr(
        image_api,
        "resolve_url",
        lambda _url: ("source.png", "temp", ""),
    )

    def process_filter(filter_type, image, _settings):
        calls.append((filter_type, tuple(image.shape)))
        return image, {}

    monkeypatch.setattr(image_api, "process_filter", process_filter)
    return context_id, calls


def test_process_image_rejects_wrong_owner_before_filter_and_accepts_same_owner(
    image_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_id, calls = _configure_success_path(
        image_api,
        tmp_path,
        monkeypatch,
        owner_client_id="client-a",
    )

    wrong = asyncio.run(
        image_api.process_image(
            _Request(_process_form(context_id, caller_client_id="client-b"))
        )
    )
    assert wrong.status == 403
    assert calls == []

    same = asyncio.run(
        image_api.process_image(
            _Request(_process_form(context_id, caller_client_id="client-a"))
        )
    )
    assert same.status == 200
    assert calls == [("brightness", (1, 2, 3, 4))]
    assert (tmp_path / "processed.png").is_file()


def test_process_image_ownerless_headless_context_requires_exact_registration(
    image_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context_id, calls = _configure_success_path(
        image_api,
        tmp_path,
        monkeypatch,
        owner_client_id=None,
    )

    response = asyncio.run(
        image_api.process_image(
            _Request(_process_form(context_id, caller_client_id=None))
        )
    )
    missing = asyncio.run(
        image_api.process_image(
            _Request(_process_form("missing-context", caller_client_id=None))
        )
    )

    assert response.status == 200
    assert missing.status == 404
    assert calls == [("brightness", (1, 2, 3, 4))]


def test_process_image_rejects_form_and_settings_context_mismatch(
    image_api,
) -> None:
    form = _process_form("settings-context", caller_client_id="client-a")
    form["context_id"] = "form-context"

    response = asyncio.run(image_api.process_image(_Request(form)))

    assert response.status == 400
    assert "mismatch" in response.text.lower()


def test_process_image_keeps_stateless_filters_context_free_but_not_inpaint(
    image_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (2, 2), (10, 20, 30)).save(source)
    calls: list[str] = []
    monkeypatch.setattr(image_api, "get_comfy_dir", lambda _kind: str(tmp_path))
    monkeypatch.setattr(
        image_api,
        "resolve_url",
        lambda _url: ("source.png", "temp", ""),
    )
    monkeypatch.setattr(
        image_api,
        "process_filter",
        lambda filter_type, image, _settings: (calls.append(filter_type) or image, {}),
    )

    stateless = asyncio.run(
        image_api.process_image(
            _Request(
                {
                    "url": "/view?filename=source.png&type=temp",
                    "type": "brightness",
                    "settings": json.dumps(
                        {
                            "filename": "stateless.png",
                            "resource_type": "temp",
                        }
                    ),
                }
            )
        )
    )
    inpaint = asyncio.run(
        image_api.process_image(
            _Request(
                {
                    "url": "/view?filename=source.png&type=temp",
                    "type": "inpaint",
                    "settings": "{}",
                }
            )
        )
    )

    assert stateless.status == 200
    assert inpaint.status == 400
    assert calls == ["brightness"]


def test_image_loader_preserves_rgba_alpha(image_api, tmp_path: Path) -> None:
    source = tmp_path / "alpha.png"
    Image.new("RGBA", (2, 1), (0, 0, 0, 127)).save(source)

    tensor = image_api._load_image_tensor(str(source))

    assert tensor.shape == (1, 1, 2, 4)
    assert torch.allclose(
        tensor[..., 3],
        torch.full((1, 1, 2), 127 / 255.0),
    )
