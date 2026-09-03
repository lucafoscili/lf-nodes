"""SQLite isolation contracts shared by job and sequence persistence."""

from __future__ import annotations

import asyncio
import threading

from dataclasses import replace

import pytest
import pytest_asyncio

from modules.workflow_runner.services import (
    job_store,
    job_store_sqlite,
    sequence_store,
)


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def persistent_store(tmp_path, monkeypatch: pytest.MonkeyPatch):
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "sequence-isolation.sqlite3"))
    monkeypatch.setattr(job_store, "_USE_PERSISTENCE", True)
    monkeypatch.setattr(job_store, "_adapter", job_store_sqlite)
    await sequence_store.reset_for_tests()
    try:
        yield
    finally:
        await job_store_sqlite.close()
        job_store_sqlite.configure(None)
        await sequence_store.reset_for_tests()


async def test_sequence_rollback_cannot_undo_or_commit_an_interleaved_job_write(
    persistent_store,
) -> None:
    """A failing sequence transaction owns the connection until rollback."""

    parent_run_id = "lf-sequence:rollback-isolation"
    initial_state = {"status": "pending", "marker": "original"}
    await sequence_store.create_state(
        parent_run_id,
        "rollback_isolation",
        owner_id="owner-a",
        state=initial_state,
    )
    await job_store_sqlite.create_job("ordinary-run", "ordinary-workflow")

    entered_trigger = threading.Event()
    release_trigger = threading.Event()

    def block_then_fail() -> int:
        entered_trigger.set()
        if not release_trigger.wait(timeout=5):
            raise RuntimeError("test trigger timed out")
        raise RuntimeError("injected sequence write failure")

    async with job_store_sqlite._transaction() as conn:
        await conn.create_function("lf_test_block_then_fail", 0, block_then_fail)
        await conn.execute(
            """
            CREATE TRIGGER fail_sequence_update
            BEFORE UPDATE ON workflow_sequences
            BEGIN
                SELECT lf_test_block_then_fail();
            END
            """
        )

    sequence_write = asyncio.create_task(
        sequence_store.save_state(
            parent_run_id,
            {"status": "running", "marker": "must-roll-back"},
        )
    )
    entered = await asyncio.wait_for(
        asyncio.to_thread(entered_trigger.wait, 5),
        timeout=6,
    )
    assert entered

    job_write = asyncio.create_task(
        job_store_sqlite.set_job_status("ordinary-run", "running")
    )
    await asyncio.sleep(0)
    assert not job_write.done(), "job write must wait for sequence rollback"

    release_trigger.set()
    with pytest.raises(Exception, match="user-defined function raised exception"):
        await sequence_write
    updated_job = await job_write

    assert updated_job is not None
    assert updated_job.status == "running"
    assert updated_job.seq == 1
    persisted_sequence = await sequence_store.get_state(parent_run_id)
    assert persisted_sequence is not None
    assert persisted_sequence.status == "pending"
    assert persisted_sequence.seq == 0
    assert persisted_sequence.state == initial_state


@pytest.mark.parametrize("mismatch", ["state", "seq"])
async def test_sequence_save_rejects_inexact_returned_snapshot(
    persistent_store,
    monkeypatch: pytest.MonkeyPatch,
    mismatch: str,
) -> None:
    parent_run_id = f"lf-sequence:readback-{mismatch}"
    initial_state = {"status": "pending", "marker": "original"}
    await sequence_store.create_state(
        parent_run_id,
        "readback_validation",
        owner_id="owner-a",
        state=initial_state,
    )

    original_decoder = sequence_store._record_from_sqlite_row

    def decode_inexact_row(row):
        record = original_decoder(row)
        if record.parent_run_id != parent_run_id or record.seq != 1:
            return record
        if mismatch == "state":
            return replace(
                record,
                state={"status": "running", "marker": "foreign"},
            )
        return replace(record, seq=record.seq + 1)

    monkeypatch.setattr(
        sequence_store,
        "_record_from_sqlite_row",
        decode_inexact_row,
    )
    with pytest.raises(
        RuntimeError,
        match="did not preserve the requested snapshot",
    ):
        await sequence_store.save_state(
            parent_run_id,
            {"status": "running", "marker": "requested"},
        )

    monkeypatch.setattr(
        sequence_store,
        "_record_from_sqlite_row",
        original_decoder,
    )
    persisted = await sequence_store.get_state(parent_run_id)
    assert persisted is not None
    assert persisted.status == "pending"
    assert persisted.seq == 0
    assert persisted.state == initial_state
