import json
import sqlite3
from types import SimpleNamespace

import pytest

from modules.workflow_runner.services import job_store, job_store_sqlite
from modules.workflow_runner.services.job_store import Job, JobStatus
from modules.workflow_runner.services.input_snapshot import (
    INPUT_SNAPSHOT_MAX_BYTES,
    sanitize_input_snapshot,
)
from modules.workflow_runner.services.job_service import get_job_status
from modules.workflow_runner.utils.serialize import serialize_job, serialize_run_summary


pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    # The adapter is intentionally asyncio-native (aiosqlite); its existing
    # contract does not promise Trio support.
    return "asyncio"


def test_snapshot_omits_binary_and_bounds_large_values() -> None:
    snapshot = sanitize_input_snapshot(
        {
            "style_prompt": "x" * 10_000,
            "source_audio": "data:audio/flac;base64," + ("A" * 1_000_000),
            "binary_preview": b"raw-audio" * 1000,
            "controls": {"shift": 3.0, "enabled": True},
        }
    )

    encoded = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")).encode()
    assert len(encoded) <= INPUT_SNAPSHOT_MAX_BYTES
    assert snapshot["source_audio"].startswith("[omitted:")
    assert snapshot["binary_preview"].startswith("[omitted:")
    assert len(snapshot["style_prompt"]) <= 4096
    assert "AAAA" not in encoded.decode()
    assert snapshot["controls"] == {"shift": 3.0, "enabled": True}


def test_snapshot_redacts_credential_shaped_keys_at_every_depth() -> None:
    snapshot = sanitize_input_snapshot(
        {
            "apiKey": "top-secret",
            "connection": {
                "access_token": "also-secret",
                "password": "still-secret",
                "max_tokens": 2048,
            },
            "style_prompt": "night",
        }
    )

    encoded = json.dumps(snapshot)
    assert "top-secret" not in encoded
    assert "also-secret" not in encoded
    assert "still-secret" not in encoded
    assert snapshot["connection"]["max_tokens"] == 2048
    assert snapshot["style_prompt"] == "night"


async def test_legacy_persistence_adapter_without_inputs_kwarg_still_creates_job(monkeypatch) -> None:
    class LegacyAdapter:
        def __init__(self) -> None:
            self.calls = []

        async def create_job(self, run_id, workflow_id, owner_id=None):
            self.calls.append((run_id, workflow_id, owner_id))
            return SimpleNamespace(
                run_id=run_id,
                workflow_id=workflow_id,
                owner_id=owner_id,
                created_at=1.0,
                status="pending",
                result=None,
                error=None,
                seq=0,
                updated_at=1.0,
            )

    adapter = LegacyAdapter()
    monkeypatch.setattr(job_store, "_USE_PERSISTENCE", True)
    monkeypatch.setattr(job_store, "_adapter", adapter)

    created = await job_store.create_job(
        "legacy-adapter-run",
        "ace_step_remix",
        owner_id="owner",
        inputs={"style_prompt": "night"},
    )

    assert adapter.calls == [("legacy-adapter-run", "ace_step_remix", "owner")]
    assert created.id == "legacy-adapter-run"
    assert created.inputs == {}


async def test_in_memory_snapshot_round_trip_is_detached() -> None:
    original = {"style_prompt": "night", "controls": {"shift": 3.0}}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(job_store, "_USE_PERSISTENCE", False)
        job_store._jobs.clear()
        created = await job_store.create_job("snapshot-memory", "ace_step_remix", inputs=original)
        original["controls"]["shift"] = 99
        loaded = await job_store.get_job("snapshot-memory")

    assert created.inputs == {"style_prompt": "night", "controls": {"shift": 3.0}}
    assert loaded is not None
    assert loaded.inputs == created.inputs


async def test_sqlite_snapshot_round_trip_and_status_update(tmp_path) -> None:
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "history.db"))
    try:
        await job_store_sqlite.create_job(
            "snapshot-sqlite",
            "ace_step_remix",
            inputs={"style_prompt": "night", "shift": 3.0},
        )
        await job_store_sqlite.set_job_status("snapshot-sqlite", "succeeded", result={"ok": True})
        loaded = await job_store_sqlite.get_job("snapshot-sqlite")
        listed = await job_store_sqlite.list_jobs()
    finally:
        await job_store_sqlite.close()

    assert loaded is not None
    assert loaded.inputs == {"style_prompt": "night", "shift": 3.0}
    assert listed["snapshot-sqlite"].inputs == loaded.inputs


async def test_sqlite_old_schema_migrates_without_losing_rows(tmp_path) -> None:
    db_path = tmp_path / "old-history.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE runs (
            run_id TEXT PRIMARY KEY, workflow_id TEXT, status TEXT,
            created_at REAL, updated_at REAL, result TEXT, error TEXT,
            seq INTEGER NOT NULL DEFAULT 0, owner_id TEXT
        )"""
    )
    conn.execute(
        "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("legacy-run", "old-workflow", "succeeded", 1.0, 2.0, None, None, 1, None),
    )
    conn.commit()
    conn.close()

    await job_store_sqlite.close()
    job_store_sqlite.configure(str(db_path))
    try:
        loaded = await job_store_sqlite.get_job("legacy-run")
        columns = await job_store_sqlite._conn.execute("PRAGMA table_info(runs)")
        names = {row[1] for row in await columns.fetchall()}
    finally:
        await job_store_sqlite.close()

    assert loaded is not None
    assert loaded.workflow_id == "old-workflow"
    assert loaded.inputs == {}
    assert "inputs" in names


async def test_detail_status_exposes_inputs_but_summary_and_events_do_not() -> None:
    job = Job(
        id="detail-run",
        workflow_id="ace_step_remix",
        status=JobStatus.SUCCEEDED,
        inputs={"style_prompt": "night"},
    )
    original_get_job = job_store.get_job
    job_store.get_job = lambda _run_id: _async_value(job)
    try:
        detail = await get_job_status("detail-run")
    finally:
        job_store.get_job = original_get_job

    full_event = serialize_job(job, include_result_for_terminal=True)
    summary = serialize_run_summary(job)
    assert detail["inputs"] == {"style_prompt": "night"}
    assert "inputs" not in full_event
    assert "inputs" not in summary


async def _async_value(value):
    return value
