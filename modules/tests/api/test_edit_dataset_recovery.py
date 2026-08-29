from __future__ import annotations

import asyncio
import importlib
import io
import json
import os
import stat
import sys
import threading
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
from PIL import Image


_TOKEN_A = "a" * 32
_TOKEN_B = "b" * 32


class _Routes:
    def post(self, *_args, **_kwargs):
        return lambda function: function


class _Request:
    def __init__(self, form: dict[str, str]) -> None:
        self._form = form

    async def post(self) -> dict[str, str]:
        return self._form


@pytest.fixture
def json_api(monkeypatch: pytest.MonkeyPatch):
    server = types.ModuleType("server")
    server.PromptServer = SimpleNamespace(instance=SimpleNamespace(routes=_Routes()))
    monkeypatch.setitem(sys.modules, "server", server)

    previous = sys.modules.pop("modules.api.json", None)
    try:
        yield importlib.import_module("modules.api.json")
    finally:
        sys.modules.pop("modules.api.json", None)
        if previous is not None:
            sys.modules["modules.api.json"] = previous


def _write_dataset(
    directory: Path,
    *,
    name: str,
    status: str,
    marker: str,
    mtime: float,
    lf_node_id: str = "463",
    context_id: str | None = None,
    prefix: str = "edit_breakpoint",
    owner_client_id: str | None = "client-a",
) -> Path:
    path = directory / name
    payload = {
        "lf_node_id": lf_node_id,
        "prefix": prefix,
        "context_id": context_id or str(path.resolve()),
        "columns": [
            {"id": "path", "title": context_id or str(path.resolve())},
            {"id": "status", "title": status},
        ],
        "marker": marker,
    }
    payload["owner_client_id"] = owner_client_id
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    os.utime(path, (mtime, mtime))
    return path


def _same_path_with_dot_segment(path: str) -> str:
    """Return a textually distinct path to the same target on Windows and POSIX."""
    return os.path.join(os.path.dirname(path), ".", os.path.basename(path))


def test_recovery_skips_newer_completed_breakpoint_dataset(json_api, tmp_path: Path) -> None:
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="recoverable",
        mtime=10,
    )
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="completed",
        marker="must-not-recover",
        mtime=20,
    )

    recovered = json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a")

    assert recovered is not None
    assert recovered["marker"] == "recoverable"


def test_get_json_authorizes_edit_datasets_but_keeps_generic_json_compatible(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="owned",
        mtime=10,
        owner_client_id="client-a",
    )
    generic = tmp_path / "generic.json"
    generic.write_text(json.dumps({"generic": True}), encoding="utf-8")
    headless = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="pending",
        marker="headless",
        mtime=20,
        owner_client_id=None,
    )
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))

    wrong = asyncio.run(
        json_api.get_json_data(
            _Request(
                {
                    "file_path": str(target),
                    "caller_client_id": "client-b",
                }
            )
        )
    )
    same = asyncio.run(
        json_api.get_json_data(
            _Request(
                {
                    "file_path": str(target),
                    "caller_client_id": "client-a",
                }
            )
        )
    )
    generic_response = asyncio.run(
        json_api.get_json_data(_Request({"file_path": str(generic)}))
    )
    headless_response = asyncio.run(
        json_api.get_json_data(_Request({"file_path": str(headless)}))
    )

    assert wrong.status == 403
    assert json.loads(same.body)["data"]["marker"] == "owned"
    assert json.loads(generic_response.body)["data"] == {"generic": True}
    assert json.loads(headless_response.body)["data"]["marker"] == "headless"


@pytest.mark.skipif(
    os.name != "nt",
    reason="Trailing dot/space aliases are a Windows filesystem behavior.",
)
@pytest.mark.parametrize("alias_suffix", [".", " "])
def test_get_json_cannot_bypass_editor_owner_with_windows_path_alias(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    alias_suffix: str,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="owned",
        mtime=10,
        owner_client_id="client-a",
    )
    alias = f"{target}{alias_suffix}"
    assert os.path.exists(alias), "Windows should resolve this alias to the target file."
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))

    response = asyncio.run(
        json_api.get_json_data(
            _Request(
                {
                    "file_path": alias,
                    "caller_client_id": "client-b",
                }
            )
        )
    )

    assert response.status == 403


def test_breakpoint_recovery_is_bound_to_the_exact_comfy_client(
    json_api,
    tmp_path: Path,
) -> None:
    client_a = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="client-a-session",
        mtime=10,
        owner_client_id="client-a",
    )
    client_b = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="pending",
        marker="client-b-session",
        mtime=20,
        owner_client_id="client-b",
    )

    recovered_a = json_api._latest_pending_edit_dataset(
        str(tmp_path), "463", "client-a"
    )
    recovered_b = json_api._latest_pending_edit_dataset(
        str(tmp_path), "463", "client-b"
    )
    exact_mismatch = json_api._recover_bound_edit_dataset(
        str(tmp_path), "463", str(client_a), "client-b"
    )
    exact_match = json_api._recover_bound_edit_dataset(
        str(tmp_path), "463", str(client_b), "client-b"
    )

    assert recovered_a is not None and recovered_a["marker"] == "client-a-session"
    assert recovered_b is not None and recovered_b["marker"] == "client-b-session"
    assert exact_mismatch is None
    assert exact_match is not None and exact_match["marker"] == "client-b-session"


def test_breakpoint_recovery_fails_closed_without_a_client_id(
    json_api,
    tmp_path: Path,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="owned",
        mtime=10,
        owner_client_id="client-a",
    )

    assert json_api._latest_pending_edit_dataset(str(tmp_path), "463", "") is None
    assert (
        json_api._recover_bound_edit_dataset(str(tmp_path), "463", str(target), "")
        is None
    )


def test_recovery_returns_none_when_only_completed_or_malformed_candidates_exist(
    json_api,
    tmp_path: Path,
) -> None:
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="completed",
        marker="done",
        mtime=10,
    )
    malformed = tmp_path / f"463_{_TOKEN_B}_edit_dataset.json"
    malformed.write_text("{", encoding="utf-8")
    os.utime(malformed, (20, 20))

    assert json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a") is None


def test_recovery_is_scoped_to_the_exact_node_id(json_api, tmp_path: Path) -> None:
    _write_dataset(
        tmp_path,
        name=f"464_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="foreign",
        mtime=10,
    )

    assert json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a") is None


def test_recovery_rejects_dataset_with_mismatched_internal_binding(
    json_api,
    tmp_path: Path,
) -> None:
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="wrong-node",
        mtime=20,
        lf_node_id="464",
    )
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="pending",
        marker="wrong-context",
        mtime=10,
        context_id=str(tmp_path / "another_edit_dataset.json"),
    )

    assert json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a") is None


def test_recovery_rejects_non_uuid_filename_and_mismatched_path_column(
    json_api,
    tmp_path: Path,
) -> None:
    _write_dataset(
        tmp_path,
        name="463_not-a-session_edit_dataset.json",
        status="pending",
        marker="invalid-name",
        mtime=20,
    )
    bound = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="wrong-path-column",
        mtime=10,
    )
    payload = json.loads(bound.read_text(encoding="utf-8"))
    payload["columns"][0]["title"] = str(tmp_path / "another_edit_dataset.json")
    bound.write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / f"463_{_TOKEN_B}_edit_dataset.json").mkdir()

    assert json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a") is None


def test_recovery_retries_transient_replace_read_denial(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="recoverable",
        mtime=10,
    )
    real_open = open
    attempts = 0

    def open_after_transient_denial(path, *args, **kwargs):
        nonlocal attempts
        if os.path.normcase(os.path.abspath(path)) == os.path.normcase(str(target)):
            attempts += 1
            if attempts == 1:
                raise PermissionError("replace in progress")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", open_after_transient_denial)
    monkeypatch.setattr(json_api.time, "sleep", lambda _interval: None)

    recovered = json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a")

    assert attempts == 2
    assert recovered is not None
    assert recovered["marker"] == "recoverable"


def test_node_wide_recovery_never_returns_loader_from_another_workflow(
    json_api,
    tmp_path: Path,
) -> None:
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="pending-loader",
        mtime=10,
        prefix="load_and_edit",
    )
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="completed",
        marker="completed-loader",
        mtime=20,
        prefix="load_and_edit",
    )

    recovered = json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a")

    assert recovered is None


def test_exact_context_recovery_supports_legacy_loader_prefix_and_rejects_bad_binding(
    json_api,
    tmp_path: Path,
) -> None:
    valid = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="completed",
        marker="valid-legacy-loader",
        mtime=10,
        prefix="load_and_edit",
        owner_client_id=None,
    )
    valid_payload = json.loads(valid.read_text(encoding="utf-8"))
    valid_payload["filename_prefix"] = valid_payload.pop("prefix")
    valid.write_text(json.dumps(valid_payload), encoding="utf-8")
    os.utime(valid, (10, 10))
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="completed",
        marker="invalid-newer-loader",
        mtime=20,
        prefix="load_and_edit",
        context_id=str(tmp_path / "wrong.json"),
    )

    recovered = json_api._recover_bound_edit_dataset(
        str(tmp_path),
        "463",
        str(valid),
        "",
    )
    rejected = json_api._recover_bound_edit_dataset(
        str(tmp_path),
        "463",
        str(tmp_path / f"463_{_TOKEN_B}_edit_dataset.json"),
        "",
    )

    assert recovered is not None
    assert recovered["marker"] == "valid-legacy-loader"
    assert rejected is None


def test_recovery_keeps_pending_breakpoint_authoritative_over_loader_fallback(
    json_api,
    tmp_path: Path,
) -> None:
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="active-breakpoint",
        mtime=10,
    )
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="completed",
        marker="loader-fallback",
        mtime=20,
        prefix="load_and_edit",
    )

    recovered = json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a")

    assert recovered is not None
    assert recovered["marker"] == "active-breakpoint"


def test_recovery_route_requires_exact_context_for_same_node_loader_snapshots(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="first-loader",
        mtime=10,
        prefix="load_and_edit",
    )
    second = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="completed",
        marker="second-loader",
        mtime=20,
        prefix="load_and_edit",
    )
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))

    first_response = asyncio.run(
        json_api.recover_edit_dataset(
            _Request(
                {
                    "node_id": "463",
                    "context_id": str(first),
                    "caller_client_id": "client-a",
                }
            )
        )
    )
    second_response = asyncio.run(
        json_api.recover_edit_dataset(
            _Request(
                {
                    "node_id": "463",
                    "context_id": str(second),
                    "caller_client_id": "client-a",
                }
            )
        )
    )
    unbound_response = asyncio.run(
        json_api.recover_edit_dataset(_Request({"node_id": "463"}))
    )
    first_body = json.loads(first_response.body.decode("utf-8"))
    second_body = json.loads(second_response.body.decode("utf-8"))
    unbound_body = json.loads(unbound_response.body.decode("utf-8"))

    assert first_response.status == 200
    assert second_response.status == 200
    assert unbound_response.status == 200
    assert first_body["data"]["marker"] == "first-loader"
    assert second_body["data"]["marker"] == "second-loader"
    assert unbound_body["data"] is None


def test_recovery_route_uses_caller_client_id_for_exact_and_node_scan(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="owned",
        mtime=10,
        owner_client_id="client-a",
    )
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))

    exact_wrong = asyncio.run(
        json_api.recover_edit_dataset(
            _Request(
                {
                    "node_id": "463",
                    "context_id": str(target),
                    "caller_client_id": "client-b",
                }
            )
        )
    )
    scan_wrong = asyncio.run(
        json_api.recover_edit_dataset(
            _Request({"node_id": "463", "caller_client_id": "client-b"})
        )
    )
    exact_same = asyncio.run(
        json_api.recover_edit_dataset(
            _Request(
                {
                    "node_id": "463",
                    "context_id": str(target),
                    "caller_client_id": "client-a",
                }
            )
        )
    )
    scan_same = asyncio.run(
        json_api.recover_edit_dataset(
            _Request({"node_id": "463", "caller_client_id": "client-a"})
        )
    )

    assert json.loads(exact_wrong.body)["data"] is None
    assert json.loads(scan_wrong.body)["data"] is None
    assert json.loads(exact_same.body)["data"]["marker"] == "owned"
    assert json.loads(scan_same.body)["data"]["marker"] == "owned"


def test_exact_context_failure_does_not_fall_back_to_same_node_scan(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="pending-breakpoint",
        mtime=10,
    )
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))

    response = asyncio.run(
        json_api.recover_edit_dataset(
            _Request(
                {
                    "node_id": "463",
                    "context_id": str(
                        tmp_path / f"463_{_TOKEN_B}_edit_dataset.json"
                    ),
                }
            )
        )
    )
    body = json.loads(response.body.decode("utf-8"))

    assert response.status == 200
    assert body["data"] is None


def test_atomic_json_write_preserves_mode_and_leaves_no_staging_file(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "463_session_edit_dataset.json"
    target.write_text('{"generation": 0}', encoding="utf-8")
    target.chmod(0o640)
    original_mode = stat.S_IMODE(target.stat().st_mode)
    fsync_calls: list[int] = []
    real_fsync = json_api.os.fsync

    def record_fsync(descriptor: int) -> None:
        fsync_calls.append(descriptor)
        real_fsync(descriptor)

    monkeypatch.setattr(json_api.os, "fsync", record_fsync)

    json_api._atomic_write_json(
        str(target),
        {"generation": 1, "label": "café"},
    )

    assert json.loads(target.read_text(encoding="utf-8")) == {
        "generation": 1,
        "label": "café",
    }
    assert len(fsync_calls) == 1
    assert stat.S_IMODE(target.stat().st_mode) == original_mode
    assert list(tmp_path.glob(f".{target.name}.*.tmp")) == []


def test_atomic_json_write_keeps_original_and_cleans_stage_on_replace_failure(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "463_session_edit_dataset.json"
    target.write_text('{"generation": 0}', encoding="utf-8")

    replace_attempts = 0

    def fail_replace(_source: str, _destination: str) -> None:
        nonlocal replace_attempts
        replace_attempts += 1
        raise PermissionError("replace failed")

    monkeypatch.setattr(json_api.os, "replace", fail_replace)
    monkeypatch.setattr(json_api.time, "sleep", lambda _interval: None)

    with pytest.raises(PermissionError, match="replace failed"):
        json_api._atomic_write_json(str(target), {"generation": 1})

    assert replace_attempts == json_api._REPLACE_ATTEMPTS
    assert json.loads(target.read_text(encoding="utf-8")) == {"generation": 0}
    assert list(tmp_path.glob(f".{target.name}.*.tmp")) == []


def test_atomic_json_write_never_exposes_partial_json_to_concurrent_reader(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "463_session_edit_dataset.json"
    target.write_text(json.dumps({"generation": 0}), encoding="utf-8")
    monkeypatch.setattr(json_api.os, "fsync", lambda _descriptor: None)

    stop = threading.Event()
    observed_errors: list[BaseException] = []
    observed_generations: set[int] = set()

    def read_repeatedly() -> None:
        while not stop.is_set():
            try:
                payload = json.loads(target.read_text(encoding="utf-8"))
                observed_generations.add(payload["generation"])
                stop.wait(0.0005)
            except PermissionError:
                # Windows may transiently deny a new open while replacing the
                # directory entry; this is not a partial JSON observation.
                continue
            except BaseException as error:  # captured for assertion in the main thread
                observed_errors.append(error)
                stop.set()

    reader = threading.Thread(target=read_repeatedly, daemon=True)
    reader.start()
    try:
        for generation in range(1, 26):
            json_api._atomic_write_json(
                str(target),
                {"generation": generation, "payload": "x" * 32768},
            )
    finally:
        stop.set()
        reader.join(timeout=5)

    assert not reader.is_alive()
    assert observed_errors == []
    assert observed_generations
    assert json.loads(target.read_text(encoding="utf-8"))["generation"] == 25


def test_update_route_accepts_only_exact_bound_temp_dataset(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="before",
        mtime=10,
    )
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["marker"] = "after"
    payload["columns"][1]["title"] = "completed"
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _folder_type: str(tmp_path))

    response = asyncio.run(
        json_api.update_json_data(
            _Request(
                {
                    "file_path": str(target),
                    "dataset": json.dumps(payload),
                    "caller_client_id": "client-a",
                }
            )
        )
    )

    assert response.status == 200
    assert json.loads(target.read_text(encoding="utf-8"))["marker"] == "after"


def test_update_route_rejects_completed_to_pending_regression(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="completed",
        marker="completed",
        mtime=10,
        prefix="load_and_edit",
    )
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["columns"][1]["title"] = "pending"
    payload["marker"] = "regressed"
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _folder_type: str(tmp_path))

    response = asyncio.run(
        json_api.update_json_data(
            _Request(
                {
                    "file_path": str(target),
                    "dataset": json.dumps(payload),
                    "caller_client_id": "client-a",
                }
            )
        )
    )

    persisted = json.loads(target.read_text(encoding="utf-8"))
    assert response.status == 409
    assert persisted["marker"] == "completed"
    assert persisted["columns"][1]["title"] == "completed"


def test_update_route_rejects_context_mismatch_and_path_escape(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_root = tmp_path / "sessions"
    session_root.mkdir()
    target = _write_dataset(
        session_root,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="original",
        mtime=10,
    )
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _folder_type: str(session_root))

    mismatched = json.loads(target.read_text(encoding="utf-8"))
    mismatched["context_id"] = str(session_root / "different.json")
    mismatch_response = asyncio.run(
        json_api.update_json_data(
            _Request(
                {
                    "file_path": str(target),
                    "dataset": json.dumps(mismatched),
                    "caller_client_id": "client-a",
                }
            )
        )
    )

    outside = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_B}_edit_dataset.json",
        status="pending",
        marker="outside",
        mtime=20,
    )
    outside_payload = json.loads(outside.read_text(encoding="utf-8"))
    escape_response = asyncio.run(
        json_api.update_json_data(
            _Request(
                {
                    "file_path": str(outside),
                    "dataset": json.dumps(outside_payload),
                    "caller_client_id": "client-a",
                }
            )
        )
    )

    assert mismatch_response.status == 400
    assert escape_response.status == 404
    assert json.loads(target.read_text(encoding="utf-8"))["marker"] == "original"
    assert json.loads(outside.read_text(encoding="utf-8"))["marker"] == "outside"


def test_update_route_authorizes_against_persisted_owner_before_payload(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="original",
        mtime=10,
        owner_client_id="client-a",
    )
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["owner_client_id"] = "client-b"
    payload["marker"] = "forged"
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))

    response = asyncio.run(
        json_api.update_json_data(
            _Request(
                {
                    "file_path": str(target),
                    "dataset": json.dumps(payload),
                    "caller_client_id": "client-b",
                }
            )
        )
    )

    assert response.status == 403
    persisted = json.loads(target.read_text(encoding="utf-8"))
    assert persisted["owner_client_id"] == "client-a"
    assert persisted["marker"] == "original"


@pytest.mark.parametrize(
    ("mutation", "expected_status"),
    [
        (lambda data: data.update(prefix="foreign"), 409),
        (lambda data: data.update(owner_client_id="client-b"), 409),
        (
            lambda data: next(
                column for column in data["columns"] if column["id"] == "path"
            ).update(title=_same_path_with_dot_segment(data["context_id"])),
            409,
        ),
        (
            lambda data: data["columns"].append(
                {"id": "path", "title": data["context_id"]}
            ),
            400,
        ),
        (
            lambda data: data["columns"].append(
                {"id": "status", "title": "pending"}
            ),
            400,
        ),
        (
            lambda data: next(
                column for column in data["columns"] if column["id"] == "status"
            ).update(title="unknown"),
            400,
        ),
    ],
)
def test_update_route_freezes_authority_and_requires_exact_status_path_columns(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation,
    expected_status: int,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="original",
        mtime=10,
        owner_client_id="client-a",
    )
    payload = json.loads(target.read_text(encoding="utf-8"))
    mutation(payload)
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))

    response = asyncio.run(
        json_api.update_json_data(
            _Request(
                {
                    "file_path": str(target),
                    "dataset": json.dumps(payload),
                    "caller_client_id": "client-a",
                }
            )
        )
    )

    assert response.status == expected_status
    assert json.loads(target.read_text(encoding="utf-8"))["marker"] == "original"


def test_ownerless_breakpoint_recovery_requires_exact_context_and_never_scans(
    json_api,
    tmp_path: Path,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="headless",
        mtime=10,
        owner_client_id=None,
    )

    assert json_api._latest_pending_edit_dataset(str(tmp_path), "463", "client-a") is None
    recovered = json_api._recover_bound_edit_dataset(
        str(tmp_path),
        "463",
        str(target),
        "",
    )
    assert recovered is not None
    assert recovered["marker"] == "headless"


def test_update_route_allows_ownerless_headless_exact_context(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="before",
        mtime=10,
        owner_client_id=None,
    )
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["marker"] = "after"
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))

    response = asyncio.run(
        json_api.update_json_data(
            _Request(
                {
                    "file_path": str(target),
                    "dataset": json.dumps(payload),
                }
            )
        )
    )

    assert response.status == 200
    assert json.loads(target.read_text(encoding="utf-8"))["marker"] == "after"


def test_load_and_edit_rebinds_serialized_dataset_and_retires_only_same_node_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    context_module = importlib.import_module(
        "modules.utils.helpers.editing.context"
    )
    load_module = importlib.import_module("modules.nodes.io.load_and_edit_images")
    monkeypatch.setattr(session_module, "get_comfy_dir", lambda _kind: str(tmp_path))
    sent_events: list[tuple] = []
    monkeypatch.setattr(
        load_module,
        "safe_send_sync",
        lambda *args, **_kwargs: sent_events.append(args),
    )
    monkeypatch.setattr(
        load_module,
        "get_current_client_id",
        lambda: "server-owner",
    )

    old_context = _write_dataset(
        tmp_path,
        name=f"73_{_TOKEN_A}_edit_dataset.json",
        status="completed",
        marker="old",
        mtime=10,
        lf_node_id="73",
        prefix="load_and_edit",
        owner_client_id="server-owner",
    )
    foreign_context = _write_dataset(
        tmp_path,
        name=f"74_{_TOKEN_B}_edit_dataset.json",
        status="completed",
        marker="foreign",
        mtime=20,
        lf_node_id="74",
        prefix="load_and_edit",
    )
    serialized = json.loads(old_context.read_text(encoding="utf-8"))
    serialized["prefix"] = "edit_breakpoint"
    serialized["owner_client_id"] = "ui-spoof"
    serialized["selection"] = {
        "context_id": str(old_context.resolve()),
        "index": 0,
        "name": "remembered",
    }
    original_serialized = json.loads(json.dumps(serialized))
    context_module.register_editing_context(str(old_context.resolve()), marker="old")
    context_module.register_editing_context(
        str(foreign_context.resolve()),
        marker="foreign",
    )

    node = load_module.LF_LoadAndEditImages()
    response = node.on_exec(
        node_id="73",
        ui_widget=serialized,
        config={"selection": {"index": 0, "name": "remembered"}},
    )
    rebound = response[9]
    rebound_context = Path(rebound["context_id"])
    persisted = json.loads(rebound_context.read_text(encoding="utf-8"))

    assert serialized == original_serialized
    assert rebound_context.parent == tmp_path
    assert rebound_context.name.startswith("73_")
    assert rebound_context.name.endswith("_edit_dataset.json")
    assert rebound_context != old_context
    assert rebound["lf_node_id"] == "73"
    assert rebound["prefix"] == "load_and_edit"
    assert rebound["selection"]["context_id"] == str(rebound_context)
    assert all(
        column["title"] == str(rebound_context)
        for column in rebound["columns"]
        if isinstance(column, dict) and column.get("id") == "path"
    )
    assert persisted["lf_node_id"] == "73"
    assert persisted["context_id"] == str(rebound_context)
    assert persisted["selection"]["context_id"] == str(rebound_context)
    assert persisted["owner_client_id"] == "server-owner"
    assert not old_context.exists()
    assert context_module.get_editing_context(str(old_context.resolve())) is None
    assert foreign_context.exists()
    assert context_module.get_editing_context(str(foreign_context.resolve())) == {
        "marker": "foreign"
    }
    assert context_module.get_editing_context(str(rebound_context)) is not None
    assert sent_events == [
        (
            "loadandeditimages",
            {"value": str(rebound_context)},
            "73",
        )
    ]

    session = session_module.EditingSession(
        node_id="73",
        owner_client_id="server-owner",
    )
    assert session.retire_owned_context(str(foreign_context.resolve())) is False
    session.retire_owned_context(str(rebound_context))
    context_module.clear_editing_context(str(foreign_context.resolve()))


def test_retirement_revokes_context_when_session_file_cannot_be_removed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    context_module = importlib.import_module(
        "modules.utils.helpers.editing.context"
    )
    monkeypatch.setattr(session_module, "get_comfy_dir", lambda _kind: str(tmp_path))
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="active",
        mtime=10,
    )
    context_module.register_editing_context(str(target.resolve()), marker="active")

    def fail_remove(_path: str) -> None:
        raise PermissionError("busy")

    monkeypatch.setattr(session_module.os, "remove", fail_remove)
    session = session_module.EditingSession(
        node_id="463",
        owner_client_id="client-a",
    )

    assert session.retire_owned_context(str(target.resolve())) is False
    assert target.exists()
    assert context_module.get_editing_context(str(target.resolve())) is None


def test_retirement_never_deletes_another_client_owned_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    context_module = importlib.import_module(
        "modules.utils.helpers.editing.context"
    )
    monkeypatch.setattr(session_module, "get_comfy_dir", lambda _kind: str(tmp_path))
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="client-a",
        mtime=10,
        owner_client_id="client-a",
    )
    context_module.register_editing_context(
        str(target.resolve()),
        owner_client_id="client-a",
    )

    session = session_module.EditingSession(
        node_id="463",
        owner_client_id="client-b",
    )

    assert session.retire_owned_context(str(target.resolve())) is False
    assert target.exists()
    assert context_module.get_editing_context(str(target.resolve())) == {
        "owner_client_id": "client-a"
    }
    context_module.clear_editing_context(str(target.resolve()))


def test_register_context_does_not_publish_context_when_dataset_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    context_module = importlib.import_module(
        "modules.utils.helpers.editing.context"
    )
    monkeypatch.setattr(session_module, "get_comfy_dir", lambda _kind: str(tmp_path))
    target = tmp_path / f"463_{_TOKEN_A}_edit_dataset.json"
    session = session_module.EditingSession(node_id="463")

    def fail_write(_dataset: dict) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(session, "_write_dataset", fail_write)

    with pytest.raises(OSError, match="disk full"):
        session.register_context({"context_id": str(target)}, marker="new")

    assert context_module.get_editing_context(str(target)) is None


def test_update_then_cleanup_is_serialized_without_leaving_an_orphan(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    context_module = importlib.import_module(
        "modules.utils.helpers.editing.context"
    )
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))
    monkeypatch.setattr(session_module, "get_comfy_dir", lambda _kind: str(tmp_path))
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="before",
        mtime=10,
    )
    context_module.register_editing_context(str(target.resolve()), marker="active")
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["marker"] = "updated"
    payload["columns"][1]["title"] = "completed"

    update_entered = threading.Event()
    allow_update = threading.Event()
    cleanup_attempted = threading.Event()
    cleanup_finished = threading.Event()
    real_atomic_write = json_api._atomic_write_json
    response_box: list[object] = []
    cleanup_box: list[bool] = []

    def blocking_atomic_write(file_path: str, data: object) -> None:
        update_entered.set()
        assert allow_update.wait(timeout=5)
        real_atomic_write(file_path, data)

    def update_worker() -> None:
        response_box.append(
            asyncio.run(
                json_api.update_json_data(
                    _Request(
                        {
                            "file_path": str(target),
                            "dataset": json.dumps(payload),
                            "caller_client_id": "client-a",
                        }
                    )
                )
            )
        )

    def cleanup_worker() -> None:
        cleanup_attempted.set()
        cleanup_box.append(
            session_module.EditingSession(
                node_id="463",
                owner_client_id="client-a",
            ).retire_owned_context(
                str(target.resolve())
            )
        )
        cleanup_finished.set()

    monkeypatch.setattr(json_api, "_atomic_write_json", blocking_atomic_write)
    update_thread = threading.Thread(target=update_worker)
    cleanup_thread = threading.Thread(target=cleanup_worker)
    update_thread.start()
    assert update_entered.wait(timeout=5)
    cleanup_thread.start()
    assert cleanup_attempted.wait(timeout=5)
    assert not cleanup_finished.wait(timeout=0.05)
    allow_update.set()
    update_thread.join(timeout=5)
    cleanup_thread.join(timeout=5)

    assert not update_thread.is_alive()
    assert not cleanup_thread.is_alive()
    assert response_box[0].status == 200
    assert cleanup_box == [True]
    assert not target.exists()
    assert context_module.get_editing_context(str(target.resolve())) is None


def test_cleanup_then_update_is_serialized_without_recreating_session_file(
    json_api,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    context_module = importlib.import_module(
        "modules.utils.helpers.editing.context"
    )
    monkeypatch.setattr(json_api, "get_comfy_dir", lambda _kind: str(tmp_path))
    monkeypatch.setattr(session_module, "get_comfy_dir", lambda _kind: str(tmp_path))
    target = _write_dataset(
        tmp_path,
        name=f"463_{_TOKEN_A}_edit_dataset.json",
        status="pending",
        marker="before",
        mtime=10,
    )
    context_module.register_editing_context(str(target.resolve()), marker="active")
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["marker"] = "late-update"

    cleanup_entered = threading.Event()
    allow_cleanup = threading.Event()
    update_attempted = threading.Event()
    update_finished = threading.Event()
    real_remove = os.remove
    response_box: list[object] = []
    cleanup_box: list[bool] = []

    def blocking_remove(path: str) -> None:
        cleanup_entered.set()
        assert allow_cleanup.wait(timeout=5)
        real_remove(path)

    def cleanup_worker() -> None:
        cleanup_box.append(
            session_module.EditingSession(
                node_id="463",
                owner_client_id="client-a",
            ).retire_owned_context(
                str(target.resolve())
            )
        )

    def update_worker() -> None:
        update_attempted.set()
        response_box.append(
            asyncio.run(
                json_api.update_json_data(
                    _Request(
                        {
                            "file_path": str(target),
                            "dataset": json.dumps(payload),
                            "caller_client_id": "client-a",
                        }
                    )
                )
            )
        )
        update_finished.set()

    monkeypatch.setattr(session_module.os, "remove", blocking_remove)
    cleanup_thread = threading.Thread(target=cleanup_worker)
    update_thread = threading.Thread(target=update_worker)
    cleanup_thread.start()
    assert cleanup_entered.wait(timeout=5)
    update_thread.start()
    assert update_attempted.wait(timeout=5)
    assert not update_finished.wait(timeout=0.05)
    allow_cleanup.set()
    cleanup_thread.join(timeout=5)
    update_thread.join(timeout=5)

    assert not cleanup_thread.is_alive()
    assert not update_thread.is_alive()
    assert cleanup_box == [True]
    assert response_box[0].status == 404
    assert not target.exists()
    assert context_module.get_editing_context(str(target.resolve())) is None


def test_wait_for_completion_retries_transient_replace_read_denial(
    json_api,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    session = session_module.EditingSession(node_id="463")
    completed = json.dumps(
        {"columns": [{"id": "status", "title": "completed"}]}
    )
    attempts = iter((PermissionError("replace in progress"), io.StringIO(completed)))

    def open_after_transient_denial(*_args, **_kwargs):
        outcome = next(attempts)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    monkeypatch.setattr("builtins.open", open_after_transient_denial)
    monkeypatch.setattr(session_module.time, "sleep", lambda _interval: None)

    result = session.wait_for_completion(
        {"context_id": "session.json", "columns": []},
        poll_interval=0,
    )

    assert result["columns"][0]["title"] == "completed"


def test_wait_for_completion_fails_after_bounded_malformed_reads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    session = session_module.EditingSession(node_id="463")
    attempts = 0

    def open_malformed(*_args, **_kwargs):
        nonlocal attempts
        attempts += 1
        return io.StringIO("{")

    monkeypatch.setattr("builtins.open", open_malformed)
    monkeypatch.setattr(session_module.time, "sleep", lambda _interval: None)

    with pytest.raises(json.JSONDecodeError):
        session.wait_for_completion(
            {"context_id": "session.json", "columns": []},
            poll_interval=0,
        )

    assert attempts == session_module._TRANSIENT_READ_ATTEMPTS


def _editor_image_node(url: str, index: int = 0) -> dict:
    return {
        "id": f"image-{index}",
        "value": f"image-{index}.png",
        "cells": {
            "lfImage": {
                "lfValue": url,
                "value": url,
            }
        },
    }


def test_collect_results_preserves_rgba_and_never_drops_broken_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    monkeypatch.setattr(session_module, "get_comfy_dir", lambda _kind: str(tmp_path))
    rgba_path = tmp_path / "rgba.png"
    Image.new("RGBA", (3, 2), (10, 20, 30, 64)).save(rgba_path)
    rgba_url = "/view?filename=rgba.png&type=temp"
    session = session_module.EditingSession(node_id="463")

    result = session.collect_results({"nodes": [_editor_image_node(rgba_url)]})

    assert len(result.image_list) == 1
    assert result.image_list[0].shape == (1, 2, 3, 4)
    assert torch.allclose(
        result.image_list[0][..., 3],
        torch.full((1, 2, 3), 64 / 255.0),
    )

    broken_dataset = {
        "nodes": [
            _editor_image_node(rgba_url, 0),
            _editor_image_node("/view?filename=missing.png&type=temp", 1),
        ]
    }
    with pytest.raises(
        ValueError,
        match=r"entry 1 could not be loaded",
    ):
        session.collect_results(broken_dataset)

    with pytest.raises(ValueError, match=r"entry 0 is missing an image URL"):
        session.collect_results({"nodes": [_editor_image_node("")]})


@pytest.mark.parametrize("column_id", ["path", "status"])
def test_session_binding_rejects_duplicate_authority_columns(
    column_id: str,
) -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    session = session_module.EditingSession(node_id="463")
    title = "pending" if column_id == "status" else "one"
    dataset = {
        "nodes": [],
        "columns": [
            {"id": column_id, "title": title},
            {"id": column_id, "title": title},
        ],
    }

    with pytest.raises(ValueError, match=f"exactly one {column_id} column"):
        session.bind_dataset_context(dataset, default_status="pending")


def test_wait_for_completion_fails_when_session_dataset_disappears() -> None:
    session_module = importlib.import_module(
        "modules.utils.helpers.editing.sessions.session"
    )
    session = session_module.EditingSession(node_id="463")

    with pytest.raises(
        RuntimeError,
        match="disappeared before completion",
    ):
        session.wait_for_completion(
            {"context_id": "definitely-missing-editor-session.json"},
            poll_interval=0,
        )


def test_breakpoint_derives_owner_from_execution_and_ignores_widget_spoof(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    breakpoint_module = importlib.import_module(
        "modules.nodes.image.images_editing_breakpoint"
    )
    captured: dict[str, object] = {}
    sent: list[tuple] = []

    class _Session:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)
            self.images = []

        def build_dataset(self, images, **_kwargs) -> dict:
            self.images = list(images)
            return {
                "context_id": "exact-context",
                "columns": [{"id": "status", "title": "pending"}],
                "nodes": [],
            }

        def register_context(self, dataset, **_kwargs) -> None:
            captured["dataset"] = dataset

        def wait_for_completion(self, dataset) -> dict:
            dataset["columns"][0]["title"] = "completed"
            return dataset

        def collect_results(self, dataset):
            return SimpleNamespace(
                batch_list=[self.images[0]],
                image_list=self.images,
            )

        def cleanup(self, _dataset) -> None:
            pass

    monkeypatch.setattr(breakpoint_module, "EditingSession", _Session)
    monkeypatch.setattr(
        breakpoint_module,
        "get_current_client_id",
        lambda: "server-owner",
    )
    monkeypatch.setattr(
        breakpoint_module,
        "safe_send_sync",
        lambda *args: sent.append(args),
    )

    image = torch.zeros((1, 2, 2, 4), dtype=torch.float32)
    result = breakpoint_module.LF_ImagesEditingBreakpoint().on_exec(
        image=image,
        node_id="463",
        ui_widget={"owner_client_id": "ui-spoof", "recovery_client_id": "legacy"},
    )

    assert captured["owner_client_id"] == "server-owner"
    assert "owner_client_id" not in captured["dataset"]
    assert sent == [
        (
            "imageseditingbreakpoint",
            {"value": "exact-context"},
            "463",
        )
    ]
    assert result[0].shape == (1, 2, 2, 4)
