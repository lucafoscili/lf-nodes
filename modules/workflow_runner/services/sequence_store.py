"""Private durable state for declaration-driven Workflow Runner sequences.

Sequence state is deliberately separate from the public run-history contract.
The public surface receives one synthetic parent job from ``job_store`` while
this module keeps only the small amount of orchestration authority required to
resume the linear assembly after a Runner restart.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time

from contextlib import asynccontextmanager
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, AsyncIterator, Mapping

from . import job_store


SEQUENCE_STATE_SCHEMA = "lf.workflow-sequence-state.v1"
ACTIVE_SEQUENCE_STATUSES = frozenset({"pending", "running"})
TERMINAL_SEQUENCE_STATUSES = frozenset(
    {"succeeded", "failed", "cancelled", "timeout"}
)

_MAX_STATE_JSON_BYTES = 1024 * 1024
_memory_records: dict[str, dict[str, Any]] = {}
_memory_lock = asyncio.Lock()
_sqlite_schema_lock = asyncio.Lock()
_sqlite_schema_ready_for: int | None = None
LOG = logging.getLogger(__name__)

_SELECT_COLUMNS = (
    "parent_run_id, sequence_id, owner_id, status, created_at, updated_at, "
    "seq, state_json"
)


@dataclass(frozen=True, slots=True)
class SequenceStateRecord:
    parent_run_id: str
    sequence_id: str
    owner_id: str | None
    status: str
    created_at: float
    updated_at: float
    seq: int
    state: dict[str, Any]


def _encode_state(state: Mapping[str, Any]) -> str:
    try:
        encoded = json.dumps(
            state,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("sequence state must be JSON serializable") from exc
    if len(encoded.encode("utf-8")) > _MAX_STATE_JSON_BYTES:
        raise ValueError("sequence state exceeds the 1 MiB persistence budget")
    return encoded


def _record_from_mapping(record: Mapping[str, Any]) -> SequenceStateRecord:
    return SequenceStateRecord(
        parent_run_id=str(record["parent_run_id"]),
        sequence_id=str(record["sequence_id"]),
        owner_id=(
            str(record["owner_id"])
            if isinstance(record.get("owner_id"), str)
            else None
        ),
        status=str(record["status"]),
        created_at=float(record["created_at"]),
        updated_at=float(record["updated_at"]),
        seq=int(record.get("seq", 0)),
        state=deepcopy(dict(record["state"])),
    )


async def _sqlite_adapter():
    """Return the configured SQLite adapter and its shared connection scopes."""

    adapter = await job_store._get_adapter()  # type: ignore[attr-defined]
    operation = getattr(adapter, "_connection_operation", None) if adapter else None
    transaction = getattr(adapter, "_transaction", None) if adapter else None
    if operation is None or transaction is None:
        raise RuntimeError(
            "sequence persistence requires the configured SQLite job-store adapter"
        )
    return adapter


@asynccontextmanager
async def _sqlite_operation() -> AsyncIterator[Any]:
    adapter = await _sqlite_adapter()
    async with adapter._connection_operation() as conn:
        yield conn


@asynccontextmanager
async def _sqlite_transaction() -> AsyncIterator[Any]:
    adapter = await _sqlite_adapter()
    async with adapter._transaction() as conn:
        yield conn


def _record_from_sqlite_row(row: Any) -> SequenceStateRecord:
    try:
        state = json.loads(row[7])
    except (TypeError, ValueError) as exc:
        raise RuntimeError("stored sequence state is malformed") from exc
    if not isinstance(state, dict):
        raise RuntimeError("stored sequence state is malformed")
    return SequenceStateRecord(
        parent_run_id=row[0],
        sequence_id=row[1],
        owner_id=row[2],
        status=row[3],
        created_at=row[4],
        updated_at=row[5],
        seq=row[6] or 0,
        state=state,
    )


async def _ensure_sqlite_schema():
    global _sqlite_schema_ready_for

    async with _sqlite_operation() as conn:
        connection_identity = id(conn)
        if _sqlite_schema_ready_for == connection_identity:
            return
    async with _sqlite_schema_lock:
        async with _sqlite_transaction() as conn:
            connection_identity = id(conn)
            if _sqlite_schema_ready_for == connection_identity:
                return
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_sequences (
                    parent_run_id TEXT PRIMARY KEY,
                    sequence_id TEXT NOT NULL,
                    owner_id TEXT,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    seq INTEGER NOT NULL DEFAULT 0,
                    state_json TEXT NOT NULL
                )
                """
            )
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_workflow_sequences_status
                ON workflow_sequences(status, updated_at DESC)
                """
            )
        # Publish readiness only after the shared transaction committed.
        _sqlite_schema_ready_for = connection_identity


async def create_state(
    parent_run_id: str,
    sequence_id: str,
    *,
    owner_id: str | None,
    state: Mapping[str, Any],
) -> SequenceStateRecord:
    """Create one immutable sequence authority, accepting only exact replay."""

    encoded = _encode_state(state)
    now = time.time()
    status = str(state.get("status") or "pending")

    if job_store._USE_PERSISTENCE:  # type: ignore[attr-defined]
        await _ensure_sqlite_schema()
        async with _sqlite_transaction() as conn:
            await conn.execute(
                """
                INSERT INTO workflow_sequences (
                    parent_run_id, sequence_id, owner_id, status,
                    created_at, updated_at, seq, state_json
                ) VALUES (?, ?, ?, ?, ?, ?, 0, ?)
                ON CONFLICT(parent_run_id) DO NOTHING
                """,
                (
                    parent_run_id,
                    sequence_id,
                    owner_id,
                    status,
                    now,
                    now,
                    encoded,
                ),
            )
            cursor = await conn.execute(
                f"SELECT {_SELECT_COLUMNS} FROM workflow_sequences "
                "WHERE parent_run_id = ?",
                (parent_run_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                raise RuntimeError("sequence state was not persisted")
            existing = _record_from_sqlite_row(row)
            if (
                existing.sequence_id != sequence_id
                or existing.owner_id != owner_id
                or existing.status != status
                or _encode_state(existing.state) != encoded
            ):
                raise ValueError("parent run id is already bound to another sequence")
            return existing

    async with _memory_lock:
        existing = _memory_records.get(parent_run_id)
        if existing is not None:
            if (
                existing["sequence_id"] != sequence_id
                or existing["owner_id"] != owner_id
                or _encode_state(existing["state"]) != encoded
            ):
                raise ValueError("parent run id is already bound to another sequence")
            return _record_from_mapping(existing)
        record = {
            "parent_run_id": parent_run_id,
            "sequence_id": sequence_id,
            "owner_id": owner_id,
            "status": status,
            "created_at": now,
            "updated_at": now,
            "seq": 0,
            "state": deepcopy(dict(state)),
        }
        _memory_records[parent_run_id] = record
        return _record_from_mapping(record)


async def get_state(parent_run_id: str) -> SequenceStateRecord | None:
    if job_store._USE_PERSISTENCE:  # type: ignore[attr-defined]
        await _ensure_sqlite_schema()
        async with _sqlite_operation() as conn:
            cursor = await conn.execute(
                f"SELECT {_SELECT_COLUMNS} FROM workflow_sequences "
                "WHERE parent_run_id = ?",
                (parent_run_id,),
            )
            row = await cursor.fetchone()
        if row is None:
            return None
        return _record_from_sqlite_row(row)

    async with _memory_lock:
        record = _memory_records.get(parent_run_id)
        return _record_from_mapping(record) if record is not None else None


async def save_state(
    parent_run_id: str,
    state: Mapping[str, Any],
) -> SequenceStateRecord:
    """Replace one private snapshot and advance its sequence number."""

    encoded = _encode_state(state)
    status = str(state.get("status") or "")
    if status not in ACTIVE_SEQUENCE_STATUSES | TERMINAL_SEQUENCE_STATUSES:
        raise ValueError("sequence state has an invalid status")
    now = time.time()

    if job_store._USE_PERSISTENCE:  # type: ignore[attr-defined]
        await _ensure_sqlite_schema()
        async with _sqlite_transaction() as conn:
            cursor = await conn.execute(
                "SELECT seq FROM workflow_sequences WHERE parent_run_id = ?",
                (parent_run_id,),
            )
            previous = await cursor.fetchone()
            if previous is None:
                raise KeyError(parent_run_id)
            expected_seq = int(previous[0] or 0) + 1
            cursor = await conn.execute(
                """
                UPDATE workflow_sequences
                SET status = ?, updated_at = ?, seq = seq + 1, state_json = ?
                WHERE parent_run_id = ? AND seq = ?
                RETURNING parent_run_id, sequence_id, owner_id, status,
                          created_at, updated_at, seq, state_json
                """,
                (status, now, encoded, parent_run_id, expected_seq - 1),
            )
            row = await cursor.fetchone()
            if row is None:
                raise KeyError(parent_run_id)
            updated = _record_from_sqlite_row(row)
            if (
                updated.status != status
                or updated.seq != expected_seq
                or _encode_state(updated.state) != encoded
            ):
                raise RuntimeError(
                    "sequence state write did not preserve the requested snapshot"
                )
            return updated

    async with _memory_lock:
        record = _memory_records.get(parent_run_id)
        if record is None:
            raise KeyError(parent_run_id)
        record["state"] = deepcopy(dict(state))
        record["status"] = status
        record["updated_at"] = now
        record["seq"] = int(record.get("seq", 0)) + 1
        return _record_from_mapping(record)


async def list_states(*, active_only: bool = False) -> list[SequenceStateRecord]:
    if job_store._USE_PERSISTENCE:  # type: ignore[attr-defined]
        await _ensure_sqlite_schema()
        async with _sqlite_operation() as conn:
            if active_only:
                cursor = await conn.execute(
                    f"SELECT {_SELECT_COLUMNS} FROM workflow_sequences "
                    "WHERE status IN ('pending', 'running') "
                    "ORDER BY created_at ASC, parent_run_id ASC"
                )
            else:
                cursor = await conn.execute(
                    f"SELECT {_SELECT_COLUMNS} FROM workflow_sequences "
                    "ORDER BY created_at ASC, parent_run_id ASC"
                )
            rows = await cursor.fetchall()
        records: list[SequenceStateRecord] = []
        for row in rows:
            parent_run_id = str(row[0])
            try:
                record = _record_from_sqlite_row(row)
            except Exception:
                LOG.exception(
                    "Ignoring malformed workflow sequence state %s",
                    parent_run_id,
                )
                continue
            records.append(record)
        return records

    async with _memory_lock:
        records = [
            _record_from_mapping(record)
            for record in _memory_records.values()
            if not active_only or record["status"] in ACTIVE_SEQUENCE_STATUSES
        ]
    return sorted(records, key=lambda item: (item.created_at, item.parent_run_id))


async def delete_state(parent_run_id: str) -> bool:
    """Delete private orchestration state after its public parent is removed."""

    if job_store._USE_PERSISTENCE:  # type: ignore[attr-defined]
        await _ensure_sqlite_schema()
        async with _sqlite_transaction() as conn:
            cursor = await conn.execute(
                "DELETE FROM workflow_sequences WHERE parent_run_id = ?",
                (parent_run_id,),
            )
        return cursor.rowcount == 1

    async with _memory_lock:
        return _memory_records.pop(parent_run_id, None) is not None


async def reset_for_tests() -> None:
    """Clear process-local records; SQLite tests own and delete their DB."""

    global _sqlite_schema_ready_for
    async with _memory_lock:
        _memory_records.clear()
    _sqlite_schema_ready_for = None


__all__ = [
    "ACTIVE_SEQUENCE_STATUSES",
    "SEQUENCE_STATE_SCHEMA",
    "TERMINAL_SEQUENCE_STATUSES",
    "SequenceStateRecord",
    "create_state",
    "delete_state",
    "get_state",
    "list_states",
    "reset_for_tests",
    "save_state",
]
