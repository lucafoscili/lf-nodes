import asyncio
import json
import sqlite3
from types import SimpleNamespace

import pytest

from modules.workflow_runner.services import job_store, job_store_sqlite, lifecycle
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
    assert {
        "inputs",
        "submission_id",
        "request_fingerprint",
        "comfy_url",
    } <= names


async def test_sqlite_legacy_migration_blocks_concurrent_startup_reads(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "concurrent-old-history.db"
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

    migration_reached = asyncio.Event()
    continue_migration = asyncio.Event()
    real_connect = job_store_sqlite.aiosqlite.connect

    class PausedMigrationConnection:
        def __init__(self, inner) -> None:
            self._inner = inner

        def __getattr__(self, name):
            return getattr(self._inner, name)

        async def execute(self, sql, parameters=None):
            normalized = " ".join(sql.split())
            if "ALTER TABLE runs ADD COLUMN submission_id" in normalized:
                migration_reached.set()
                await continue_migration.wait()
            if parameters is None:
                return await self._inner.execute(sql)
            return await self._inner.execute(sql, parameters)

    async def connect_with_paused_migration(*args, **kwargs):
        inner = await real_connect(*args, **kwargs)
        return PausedMigrationConnection(inner)

    await job_store_sqlite.close()
    job_store_sqlite.configure(str(db_path))
    monkeypatch.setattr(job_store_sqlite, "_conn_lock", asyncio.Lock())
    monkeypatch.setattr(
        job_store_sqlite.aiosqlite,
        "connect",
        connect_with_paused_migration,
    )
    initial_read = asyncio.create_task(job_store_sqlite.list_jobs())
    concurrent_read = None
    try:
        await asyncio.wait_for(migration_reached.wait(), timeout=2)
        concurrent_read = asyncio.create_task(job_store_sqlite.list_jobs())
        await asyncio.sleep(0)
        await asyncio.sleep(0)

        assert not concurrent_read.done(), (
            "the sqlite connection became visible before its legacy schema migration "
            "completed"
        )

        continue_migration.set()
        initial_listed = await initial_read
        listed = await concurrent_read
    finally:
        continue_migration.set()
        pending = [initial_read]
        if concurrent_read is not None:
            pending.append(concurrent_read)
        await asyncio.gather(*pending, return_exceptions=True)
        await job_store_sqlite.close()

    assert initial_listed["legacy-run"].workflow_id == "old-workflow"
    assert listed["legacy-run"].workflow_id == "old-workflow"
    assert listed["legacy-run"].submission_id is None


async def test_sqlite_submission_identity_round_trip_and_public_projection(tmp_path) -> None:
    fingerprint = "a" * 64
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "submission-history.db"))
    try:
        created = await job_store_sqlite.create_job(
            "prompt-durable",
            "remove_bg",
            owner_id="owner-a",
            submission_id="durable-submission",
            request_fingerprint=fingerprint,
            comfy_url="http://comfy:8188",
        )
        loaded = await job_store_sqlite.get_job_by_submission_id(
            "durable-submission"
        )
        listed = await job_store_sqlite.list_jobs()
    finally:
        await job_store_sqlite.close()

    assert loaded == created
    assert listed["prompt-durable"].submission_id == "durable-submission"
    serialized = serialize_run_summary(loaded)
    assert serialized["submission_id"] == "durable-submission"
    assert "request_fingerprint" not in serialized
    assert "comfy_url" not in serialized


async def test_sqlite_stable_prompt_collision_never_crosses_owner_boundary(tmp_path) -> None:
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "owner-collision.db"))
    try:
        original = await job_store_sqlite.create_job(
            "provider-duplicate-prompt",
            "workflow-a",
            owner_id="owner-a",
            submission_id="submission-a",
            request_fingerprint="a" * 64,
            comfy_url="http://comfy-a:8188",
        )

        with pytest.raises(ValueError, match="another submission identity"):
            await job_store_sqlite.create_job(
                "provider-duplicate-prompt",
                "workflow-b",
                owner_id="owner-b",
                submission_id="submission-b",
                request_fingerprint="b" * 64,
                comfy_url="http://comfy-b:8188",
            )

        retained = await job_store_sqlite.get_job("provider-duplicate-prompt")
        foreign = await job_store_sqlite.get_job_by_submission_id("submission-b")
    finally:
        await job_store_sqlite.close()

    assert retained == original
    assert retained is not None
    assert retained.owner_id == "owner-a"
    assert retained.submission_id == "submission-a"
    assert foreign is None


async def test_sqlite_cas_can_clear_only_the_scanned_synthetic_error(tmp_path) -> None:
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "cas-clear-error.db"))
    try:
        await job_store_sqlite.create_job(
            "pending-cancel-correction",
            "remove_bg",
            owner_id="owner-a",
        )
        failed = await job_store_sqlite.set_job_status(
            "pending-cancel-correction",
            "failed",
            error="execution_state_lost",
        )
        corrected = await job_store_sqlite.set_job_status_if_unchanged(
            "pending-cancel-correction",
            "cancelled",
            owner_id=failed.owner_id,
            expected_status=failed.status,
            seq=failed.seq,
            updated_at=failed.updated_at,
            clear_error=True,
        )
        loaded = await job_store_sqlite.get_job("pending-cancel-correction")
    finally:
        await job_store_sqlite.close()

    assert corrected is not None
    assert corrected.status == "cancelled"
    assert corrected.error is None
    assert loaded == corrected


async def test_memory_stable_prompt_collision_never_crosses_owner_boundary() -> None:
    original = await job_store.create_job(
        "provider-duplicate-prompt-memory",
        "workflow-a",
        owner_id="owner-a",
        submission_id="submission-a",
        request_fingerprint="a" * 64,
        comfy_url="http://comfy-a:8188",
    )

    with pytest.raises(ValueError, match="another submission identity"):
        await job_store.create_job(
            "provider-duplicate-prompt-memory",
            "workflow-b",
            owner_id="owner-b",
            submission_id="submission-b",
            request_fingerprint="b" * 64,
            comfy_url="http://comfy-b:8188",
        )

    retained = await job_store.get_job("provider-duplicate-prompt-memory")
    assert retained is original
    assert retained.owner_id == "owner-a"
    assert retained.submission_id == "submission-a"


async def test_lifecycle_recovers_retry_and_cancel_target_after_restart(
    tmp_path,
    monkeypatch,
) -> None:
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "restart-safe-submission",
        "inputs": {"image": "same-input"},
    }
    await lifecycle.reset_for_tests()
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "restart-history.db"))
    monkeypatch.setattr(job_store, "_USE_PERSISTENCE", True)
    monkeypatch.setattr(job_store, "_adapter", job_store_sqlite)
    try:
        _, created = await lifecycle.reserve_submission(
            payload,
            "remove_bg",
            owner_id="owner-a",
        )
        await lifecycle.bind_prompt(
            "restart-safe-submission",
            "prompt-after-restart",
            "http://comfy:8188",
        )
        identity = await lifecycle.get_submission_persistence_fields(
            "restart-safe-submission"
        )
        assert identity is not None
        await job_store.create_job(
            "prompt-after-restart",
            "remove_bg",
            owner_id="owner-a",
            **identity,
        )
        await job_store.set_job_status(
            "prompt-after-restart",
            JobStatus.RUNNING,
        )

        # Simulate a Runner process restart while retaining the SQLite row.
        await lifecycle.reset_for_tests()
        recovered = await lifecycle.get_submission(
            "restart-safe-submission",
            include_events=False,
        )
        target = await lifecycle.get_cancel_target("restart-safe-submission")
        replay, replay_created = await lifecycle.reserve_submission(
            payload,
            "remove_bg",
            owner_id="owner-a",
        )
    finally:
        await lifecycle.reset_for_tests()
        await job_store_sqlite.close()

    assert created is True
    assert recovered is not None
    assert recovered["run_id"] == "prompt-after-restart"
    assert recovered["status"] == "running"
    assert recovered["owner_id"] == "owner-a"
    assert target == {
        "submission_id": "restart-safe-submission",
        "run_id": "prompt-after-restart",
        "comfy_url": "http://comfy:8188",
        "status": "running",
        "cancel_requested": False,
    }
    assert replay_created is False
    assert replay["run_id"] == "prompt-after-restart"


async def test_explicit_retry_fails_closed_without_durable_lookup(monkeypatch) -> None:
    class LegacyAdapter:
        pass

    await lifecycle.reset_for_tests()
    monkeypatch.setattr(job_store, "_USE_PERSISTENCE", True)
    monkeypatch.setattr(job_store, "_adapter", LegacyAdapter())
    try:
        with pytest.raises(RuntimeError, match="cannot verify stable submission"):
            await lifecycle.reserve_submission(
                {
                    "workflowId": "remove_bg",
                    "submissionId": "unverifiable-submission",
                    "inputs": {},
                },
                "remove_bg",
            )
    finally:
        await lifecycle.reset_for_tests()


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
